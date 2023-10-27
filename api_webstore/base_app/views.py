import hmac

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework import generics, viewsets, mixins, status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated

from django.urls import reverse
from api_webstore import settings
from .models import *
from .permissions import IsOwner, IsAdminOrReadOnly, IsOwnerOrAdmin, IsAdmin
from .serializers import *
from rest_framework.response import Response
from django.db import transaction
from django.shortcuts import redirect
import requests
import hashlib

secret_key = settings.PAYMENT_SECRET_KEY
wayforpay_url = 'https://api.wayforpay.com/api'


def remove_invoice(order):
    def get_signature(order):
        signature = f'{settings.MERCHANT_ID};{order.id}'.encode('utf-8')
        return hmac.new(secret_key.encode('utf-8'), signature, hashlib.md5).hexdigest()

    data_to_server = {
        'transactionType': 'REMOVE_INVOICE',
        'apiVersion': '1',
        'merchantAccount': settings.MERCHANT_ID,
        'orderReference': str(order.id),
        'merchantSignature': get_signature(order),
    }
    response = requests.post(wayforpay_url, json=data_to_server)
    data_from_server = response.json()
    return data_from_server.get('reasonCode')


def delivery_is_valid(delivery):
    required_fields = ['first_name', 'last_name', 'phone', 'city', 'address']
    return all(delivery.get(field) for field in required_fields)


class FillOrder(APIView):
    """Необхідний функціонал для додавання делівері і тип оплати"""
    permission_classes = (IsOwnerOrAdmin,)

    def get(self, request, pk):
        order = get_object_or_404(Order, id=pk)
        serializer = FillOrderSerializer(order, many=False, context={'request': 'request'})
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateCompleteOrder(APIView):
    permission_classes = (IsOwnerOrAdmin,)
    """Сюда відправляються дані від фронтенда з додатковими даними по доставці та типу оплати.
    Тут ми додаємо до замовлення додаткові дані та запускаємо оплату якщо її тип онлайн"""

    def post(self, request, *args, **kwargs):
        user = CustomUser.objects.get(id=self.request.user.id)
        order_id = self.request.data.get('id')
        order = get_object_or_404(Order, id=order_id)

        if order.order_status in ['Cancelled', 'Finished', ]:
            return redirect(reverse('history-detail', kwargs={'pk': order_id}))

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


class CategoryList(viewsets.ReadOnlyModelViewSet):  # list of all products of the category
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
    """методи керуванням корзини:
    get - отримання корзини юзера.
    post - створення замовлення на основі корзини юзера, без доставки та способа оплати.
    put - оновленнне кількості товару в кожному елементі козини.
    delete - видалення товарної одиниці з корзини юзера при отрманні запиту з методом 'delete'
    та даними корзини. Будуть видалені обєкти які були відсутні в цьому запиті"""
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

    def delete(self, request, pk=None, *args, **kwargs):  # можна використовувати "видалити вибрані" на фронті
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
                 viewsets.GenericViewSet):  # show the user's orders history
    serializer_class = OrdersSerializer
    permission_classes = (IsOwnerOrAdmin,)

    def get_queryset(self):
        user = CustomUser.objects.get(id=self.request.user.id)
        queryset = user.get_order_history()

        order_number = self.kwargs.get('pk')
        if order_number:
            queryset = queryset.filter(id=order_number)
        return queryset


def initiate_payment(request, order):
    """Функціонал для формування запитів на сервер оплати WayForPay
    та обробка відповідей. Процес оплати проводить сервер WayForPay"""

    payment_data = {'transactionType': "CREATE_INVOICE",
                    'merchantAccount': settings.MERCHANT_ID,
                    'merchantDomainName': 'www.' + request.META['HTTP_HOST'],
                    'merchantAuthType': "SimpleSignature",
                    'apiVersion': "1",
                    # 'merchantTransactionSecureType': "AUTO",
                    'orderReference': str(order.id),
                    'orderDate': int(order.date_create.timestamp()),
                    'amount': str(order.saved_total_price),
                    'currency': "UAH",
                    'productName': ["Замовлення " + str(order.id)],
                    'productPrice': [str(order.saved_total_price)],
                    'productCount': ["1"],
                    'language': "UA",
                    'serviceUrl': 'www.' + request.META['HTTP_HOST'] + '/payment-status/',
                    'orderTimeOut': settings.INVOICE_LIFETIME}
    print(payment_data['serviceUrl'])  # 444444444444444444444444444444444444444444444444444444444
    # create signature data for server of WayForPay
    data_to_sign_for_request = [
        payment_data['merchantAccount'],
        payment_data['merchantDomainName'],
        payment_data['orderReference'],
        str(payment_data['orderDate']),
        payment_data['amount'],
        payment_data['currency'],
        payment_data['productName'][0],
        payment_data['productCount'][0],
        payment_data['productPrice'][0]
    ]

    data_to_sign_for_request = ";".join(data_to_sign_for_request).encode('utf-8')
    payment_data["merchantSignature"] = hmac.new(secret_key.encode('utf-8'), data_to_sign_for_request,
                                                 hashlib.md5).hexdigest()

    response = requests.post(wayforpay_url, json=payment_data)

    # response processing from payment server
    print(response.json().get('reasonCode'))
    print(response.status_code)
    if response.status_code == 200:
        wayforpay_response = response.json()
        invoice_url = wayforpay_response.get('invoiceUrl', None)
        print(str(invoice_url))
        if wayforpay_response.get('reasonCode') == 1100:
            if not hasattr(order, 'online_payment'):
                OnlinePayment.objects.create(order=order,
                                             payment_status='Pending',
                                             invoice_url=invoice_url,
                                             )
            print('invoiceUrl  -  ' + invoice_url)
            if not order.online_payment.is_invoice_valid():
                order.online_payment.invoice_url = None
                order.order_status = 'Cancelled'
                order.online_payment.payment_status = 'Cancelled'
                order.online_payment.save()
                order.save()
                remove_invoice(order)
                return Response({'error': 'invoice is expire'})

            url = reverse('history-detail', kwargs={'pk': order.id})
            return redirect(url)

        elif not hasattr(order, 'online_payment'):
            remove_invoice(order)  # this func must be deleted on deploy
            return Response({'error': 'Order`s reference is invalid'}, status=status.HTTP_404_NOT_FOUND)

        elif wayforpay_response.get('reasonCode') == 1112 and order.online_payment.is_invoice_valid():
            return redirect(order.online_payment.invoice_url)

        else:
            print('sserrsdrsidroiesndoiansodena')
            return Response({'error': wayforpay_response.get('reasonCode')},
                            status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'Error from Wayforpayyy server'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentStatusView(APIView):
    """Функціонал для обробки інформації про статус оплати замовлення
    за допомогою запиту з сервера WayForPay"""

    def handle_successful_transaction(self, order):
        with transaction.atomic():
            order.order_status = 'Confirmed'
            order.online_payment.payment_status = 'Paid'
            order.online_payment.save()
            order.save()

    def handle_failed_transaction(self, order):
        with transaction.atomic():
            order.order_status = 'Cancelled'
            order.online_payment.payment_status = 'Cancelled'
            order.online_payment.save()
            order.save()

    def generate_response_signature(self, order_reference, status, time):
        data_to_sign = f'{order_reference};{status};{time}'.encode('utf-8')
        return hmac.new(secret_key.encode('utf-8'), data_to_sign, hashlib.md5).hexdigest()

    def signature_verification(self, merchant_signature_from_server, request):
        # створення контрольного підпису замовлення для перевірки запиту від сервера
        signature_data = [
            request.data.get('merchantAccount'),
            request.data.get('orderReference'),
            request.data.get('amount'),
            request.data.get('currency'),
            request.data.get('authCode'),
            request.data.get('cardPan'),
            request.data.get('transactionStatus'),
            request.data.get('reasonCode')
        ]

        signature = ";".join(signature_data).encode('utf-8')
        signature = hmac.new(secret_key.encode('utf-8'), signature, hashlib.md5).hexdigest()

        return hmac.new(secret_key.encode('utf-8'), signature,
                        hashlib.md5).hexdigest() == merchant_signature_from_server

    def post(self, request, *args, **kwargs):

        merchant_signature_from_server = request.data.get('merchantSignature')
        if not self.signature_verification(merchant_signature_from_server, request):
            return Response({'error': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)

        reason_code = request.data.get('reasonCode')
        if reason_code == 1100:
            order_number = request.data.get('orderReference')
            print(request.data.get('transactionStatus'))  # srssssssssssssssssssss
            try:
                order = Order.objects.get(id=order_number)
            except Order.DoesNotExist:
                return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

            transaction_status = request.data.get('transactionStatus')
            if transaction_status == 'Approved':
                self.handle_successful_transaction(order)
            elif transaction_status in ['Refunded/Voided', 'Expired']:
                self.handle_failed_transaction(order)

            current_time = int(timezone.now().timestamp())
            response_signature = self.generate_response_signature(
                request.data.get('orderReference'),
                'accept',
                current_time
            )

            response_data = {
                'orderReference': request.data.get('orderReference'),
                'status': 'accept',
                'time': current_time,
                'signature': response_signature,
            }

            requests.post(wayforpay_url, json=response_data)

        pass
