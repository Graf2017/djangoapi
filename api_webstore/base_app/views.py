from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework import generics, viewsets, mixins, status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .models import *
from .permissions import IsOwner, IsAdminOrReadOnly, IsOwnerOrAdmin, IsAdmin
from .serializers import *
from rest_framework.response import Response
from django.db import transaction


class ApiPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


class ShowPositions(viewsets.ReadOnlyModelViewSet):  # return all product positions or one position
    """Using 'post' method to add a position to the user's cart.
    Using 'get' method to return all product positions or one position.
    """
    queryset = Position.objects.filter(is_published=True, deleted=False, in_stock=True)
    serializer_class = PositionSerializer
    pagination_class = ApiPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['price', 'title', 'brand', 'categories']
    search_fields = ['title', 'description', 'brand']
    ordering_fields = ['title', 'price']

    def post(self, request, *args, **kwargs):  # add position to the user's cart
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


class CategoryList(viewsets.ReadOnlyModelViewSet):  # list of all products of a category
    serializer_class = CategoryListSerializer
    lookup_field = "slug"
    pagination_class = ApiPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['price', 'title', 'brand']
    search_fields = ['title', 'description', 'brand']
    ordering_fields = ['title', 'price']

    def get_queryset(self, *args, **kwargs):
        slug = self.kwargs.get('slug')
        queryset = Position.objects.filter(categories__slug=slug, is_published=True, deleted=False, in_stock=True)
        return queryset


class ShowCart(APIView):
    """методи керуванням корзини: get - отримання корзини юзера.
    post - створення замовлення на основі корзини юзера.
    put - оновленнне кількості товару в кожному елементі козини.
    delete - видалення товарної одиниці з корзини юзера при отрманні запиту з методом 'delete'
    та даними корзини. Будуть видалені обєкти які були відсутні в цьому запиті"""
    permission_classes = (IsOwnerOrAdmin, IsAuthenticated)

    def get_queryset(self):
        user = self.request.user
        cart, _ = Cart.objects.get_or_create(user=user)
        return cart.cart_items.all()

    def get(self, request):
        user = self.request.user
        cart, _ = Cart.objects.get_or_create(user=user)
        return Response(CartSerializer(cart, many=False, context={'request': request}).data)

    def post(self, request):
        user = self.request.user
        delivery_data = request.data.get('delivery')
        delivery, created = user.delivery.get_or_create(
            first_name=delivery_data.get('first_name'),
            last_name=delivery_data.get('last_name'),
            phone=delivery_data.get('phone'),
            index=delivery_data.get('index'),
            city=delivery_data.get('city'),
            address=delivery_data.get('address')
        )
        cart_items = self.get_queryset()
        if cart_items.first() is None or not cart_items.exists():
            return Response(status=status.HTTP_204_NO_CONTENT)

        with transaction.atomic():
            order = Order.objects.create(user=user, delivery=delivery)
            # order.delivery = delivery
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    position=cart_item.position,
                    quantity=cart_item.quantity,
                    saved_title=cart_item.position.title,
                    saved_price=cart_item.position.price
                )

            cart_items.delete()

        serializer = OrdersSerializer(order, many=False, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        cart_items = self.get_queryset()
        if cart_items.first() is None or not cart_items.exists():
            return Response(status=status.HTTP_204_NO_CONTENT)

        with transaction.atomic():
            try:
                data = self.request.data.get('cart_items')
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

    def delete(self, request, pk=None, *args, **kwargs): # можна використовувати "видалити вибрані" на фронті
        data = self.request.data.get('cart_items', [])

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


class CreateDelivery(mixins.CreateModelMixin, viewsets.GenericViewSet):  # create delivery address
    serializer_class = DeliverySerializer
    permission_classes = (IsOwnerOrAdmin,)

    def get_queryset(self):
        user = self.request.user
        return user.delivery

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)


class ShowOrders(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):  # show the user's order history
    serializer_class = OrdersSerializer
    permission_classes = (IsOwnerOrAdmin,)

    def get_queryset(self):
        user = self.request.user
        queryset = user.get_order_history()

        order_id = self.kwargs.get('pk')
        if order_id:
            queryset = queryset.filter(id=order_id)

        return queryset


class ShowDelivery(viewsets.ModelViewSet):
    serializer_class = DeliverySerializer
    permission_classes = (IsOwnerOrAdmin,)

    def get_queryset(self):
        user = self.request.user
        return user.delivery
