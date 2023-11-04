from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework import viewsets, mixins, status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from django.urls import reverse
from .permissions import IsOwnerOrAdmin
from .serializers import *
from .utils.utils import delivery_is_valid
from apps.online_payment.utils.utils import initiate_payment
from rest_framework.response import Response
from django.db import transaction
from django.shortcuts import redirect


class FillOrder(APIView):
    """For created order completely we need to add delivery and payment method"""
    permission_classes = (IsOwnerOrAdmin,)

    def get(self, request, pk):
        order = get_object_or_404(Order, id=pk)
        serializer = FillOrderSerializer(order, many=False, context={'request': 'request'})
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateCompleteOrder(APIView):
    """Here we get data and adding one to the order and creating payment if needed"""
    permission_classes = (IsOwnerOrAdmin,)

    def post(self, request, *args, **kwargs):
        order_id = self.request.data.get('id')
        order = get_object_or_404(Order, id=order_id)

        if order.order_status in ['Cancelled', 'Finished', ]:
            return Response({'error': 'order finished or cancelled'})

        delivery_data = self.request.data.get('delivery')
        payment_method = self.request.data.get('payment_method')
        if payment_method not in ['Online payment', 'Cash on delivery']:
            return Response({'message': 'Payment method is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
        if not delivery_data:
            return Response({'message': 'Delivery not found'}, status=status.HTTP_400_BAD_REQUEST)

        delivery = get_object_or_404(Delivery, id=delivery_data['id'])

        order.delivery, order.payment_method = delivery, payment_method
        order.order_status = 'Pending'
        order.save()
        if payment_method == 'Online payment':
            return initiate_payment(self.request, order)

        url = reverse('history-detail', kwargs={'pk': order_id})
        return redirect(url)


class PositionPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


class ShowPositions(viewsets.ReadOnlyModelViewSet):
    """Using 'post' method to add a position to the user's cart.
    Using 'get' method to return all product positions or one position.
    """
    queryset = Position.objects.filter(is_published=True, deleted=False, in_stock=True)
    serializer_class = PositionSerializer
    pagination_class = PositionPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['price', 'title', 'brand', 'categories']
    search_fields = ['title', 'description', 'brand']
    ordering_fields = ['title', 'price']

    def post(self, request, *args, **kwargs):
        user = request.user
        try:
            cart, _ = Cart.objects.get_or_create(user=user)
        except TypeError:
            return Response({"message": "Користувача не знайдено."}, status=status.HTTP_404_NOT_FOUND)
        position = get_object_or_404(Position, id=kwargs['pk'])
        cart_item, created = CartItem.objects.get_or_create(cart=cart, position=position)
        if created:
            cart_item.quantity = 1
        else:
            cart_item.quantity += 1
        cart_item.save()
        return Response({"message": "Позицію успішно додана для корзини."}, status=status.HTTP_200_OK)


class ShowCategories(mixins.ListModelMixin, viewsets.GenericViewSet):  # all categories
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer


class CategoryList(viewsets.ReadOnlyModelViewSet):
    """List all category`s products"""
    serializer_class = CategoryListSerializer
    lookup_field = "slug"
    pagination_class = PositionPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['price', 'title', 'brand']
    search_fields = ['title', 'description', 'brand']
    ordering_fields = ['title', 'price']

    def get_queryset(self, *args, **kwargs):
        slug = self.kwargs.get('slug')
        queryset = Position.objects.filter(categories__slug=slug, is_published=True, deleted=False, in_stock=True)
        return queryset


class ShowCart(APIView):
    """Cart management methods :
    get - get user cart.
    post - create order based on user cart, without delivery and payment method.
    put - update quantity of the product in the cart.
    delete - delete product from the cart by to get request with 'delete' method and cart data.
    Deleted will be those objects that were not in the request."""
    permission_classes = (IsOwnerOrAdmin, IsAuthenticated)

    def get_queryset(self):
        user = self.request.user
        cart, _ = Cart.objects.get_or_create(user=user)
        return cart.cart_item.all()

    def get(self, request):
        user = self.request.user
        cart, _ = Cart.objects.get_or_create(user=user)
        return Response(CartSerializer(cart, many=False, context={'request': request}).data)

    def post(self, request):
        user = self.request.user
        cart_items = self.get_queryset()
        if cart_items.first() is None or not cart_items.exists():
            return Response({'message': 'Cart is empty'}, status=status.HTTP_204_NO_CONTENT)

        with (transaction.atomic()):
            order = Order.objects.create(user=user, order_status='New')
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    position=cart_item.position,
                    quantity=cart_item.quantity,
                    saved_title=cart_item.position.title,
                    saved_price=cart_item.position.price,
                )

        cart_items.delete()
        return redirect('fill-order', pk=order.id)

    def put(self, request, *args, **kwargs):
        cart_items = self.get_queryset()
        if cart_items.first() is None or not cart_items.exists():
            return Response(status=status.HTTP_204_NO_CONTENT)

        with transaction.atomic():
            try:
                data = self.request.data.get('cart_item')
            except KeyError:
                return Response({'message': 'No data'}, status=status.HTTP_204_NO_CONTENT)
            for item in data:
                cart_item = cart_items.get(id=item['id'])
                cart_item.quantity = item['quantity']
                cart_item.save()
                if item['quantity'] == 0:
                    cart_item.delete()
        serializer = CartSerializer(cart_items.first().cart, many=False, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None, *args, **kwargs):  # good to use 'delete selected' at frontend
        data = self.request.data.get('cart_item', [])

        if not data:
            return Response(status=status.HTTP_204_NO_CONTENT)

        cart_items = self.get_queryset()
        ids_to_save = [item['id'] for item in data]

        items_to_delete = cart_items.exclude(id__in=ids_to_save)
        items_to_delete.delete()

        if cart_items.exists():
            serializer = CartSerializer(cart_items.first().cart, many=False, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)


class DeliveryView(viewsets.ModelViewSet):
    """
    Create a new delivery address for the user, or list all the user's delivery addresses.
    """
    serializer_class = DeliverySerializer
    permission_classes = (IsOwnerOrAdmin,)

    def get_queryset(self):
        user = CustomUser.objects.get(id=self.request.user.id)
        return user.delivery

    def create(self, request, *args, **kwargs):
        user = CustomUser.objects.get(id=request.user.id)
        data = request.data
        if not delivery_is_valid(request.data):
            return Response({'error': 'Invalid delivery data'}, status=status.HTTP_400_BAD_REQUEST)
        delivery = Delivery.objects.create(
            user=user,
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            phone=data.get('phone'),
            city=data.get('city'),
            address=data.get('address'),
            index=data.get('index', None)
        )

        serializer = DeliverySerializer(delivery, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ShowOrders(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                 viewsets.GenericViewSet):
    """Show user`s orders history"""
    serializer_class = OrdersSerializer
    permission_classes = (IsOwnerOrAdmin,)

    def get_queryset(self):
        user = CustomUser.objects.get(id=self.request.user.id)
        queryset = user.get_order_history()

        order_number = self.kwargs.get('pk')
        if order_number:
            queryset = queryset.filter(id=order_number)
        return queryset


