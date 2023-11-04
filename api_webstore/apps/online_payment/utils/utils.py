from api_webstore_core import settings
from ..models import OnlinePayment
import hmac
import hashlib
import requests
from rest_framework import status
from rest_framework.response import Response
from django.urls import reverse
from django.shortcuts import redirect
from django.db import transaction


def get_signature(order):
    order_reference = str(order.id)
    signature = f'{settings.MERCHANT_ID};{order_reference}'.encode('utf-8')
    return hmac.new(settings.PAYMENT_SECRET_KEY.encode('utf-8'), signature, hashlib.md5).hexdigest()


def cancel_order(order):
    order.order_status = 'Cancelled'
    order.online_payment.payment_status = 'Cancelled'
    order.online_payment.save()
    order.save()


def remove_invoice(order):
    data_to_server = {
        'transactionType': 'REMOVE_INVOICE',
        'apiVersion': '1',
        'merchantAccount': settings.MERCHANT_ID,
        'orderReference': str(order.id),
        'merchantSignature': get_signature(order),
    }
    response = requests.post(settings.PAYMENT_URL, json=data_to_server)
    response_data = response.json()
    print('remove status', response_data.get('reasonCode'))


def initiate_payment(request, order):
    """Generate requests to the payment server and response processing. Invoice creating"""
    http_host = request.META.get('HTTP_HOST', '')
    if not http_host:
        return Response({'error': 'Invalid host'}, status=status.HTTP_400_BAD_REQUEST)
    payment_data = {'transactionType': "CREATE_INVOICE",
                    'merchantAccount': settings.MERCHANT_ID,
                    'merchantDomainName': f'www.{http_host}',
                    'merchantAuthType': "SimpleSignature",
                    'apiVersion': "1",
                    # 'merchantTransactionSecureType': "AUTO",
                    'orderReference': str(order.id),
                    'orderDate': int(order.date_create.timestamp()),
                    'amount': str(order.saved_total_price),
                    'currency': "UAH",
                    'productName': ["Order " + str(order.id)],
                    'productPrice': [str(order.saved_total_price)],
                    'productCount': ["1"],
                    'language': "UA",
                    'serviceUrl': f'www.{http_host}{reverse("online_payment:online-payment-status")}',
                    'orderTimeOut': settings.INVOICE_LIFETIME}

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
    payment_data["merchantSignature"] = hmac.new(settings.PAYMENT_SECRET_KEY.encode('utf-8'), data_to_sign_for_request,
                                                 hashlib.md5).hexdigest()

    # response processing from payment server
    response = requests.post(settings.PAYMENT_URL, json=payment_data)

    print('reason code', response.json().get('reasonCode'))
    if response.status_code == 200:
        wayforpay_response = response.json()
        invoice_url = wayforpay_response.get('invoiceUrl', None)
        print('invoiceUrl  -  ', invoice_url)

        if not hasattr(order, 'online_payment'):
            OnlinePayment.objects.create(order=order, invoice_url=invoice_url, payment_status='Pending')

        if wayforpay_response.get('reasonCode') == 1100:

            url = reverse('history-detail', kwargs={'pk': order.id})
            return redirect(url)

        elif not order.online_payment.is_invoice_valid() or not order.online_payment.invoice_url:
            cancel_order(order)
            remove_invoice(order)
            return Response({'error': 'invoice is expire or invalid. Order cancelled'})

        elif wayforpay_response.get('reasonCode') == 1112:
            url = reverse('history-detail', kwargs={'pk': order.id})
            return redirect(url)

        else:
            return Response({'error': wayforpay_response.get('reasonCode')},
                            status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'Error from Wayforpayyy server'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def handle_successful_transaction(order):
    with transaction.atomic():
        order.order_status = 'Confirmed'
        order.online_payment.payment_status = 'Paid'
        order.online_payment.save()
        order.save()


def handle_failed_transaction(order):
    with transaction.atomic():
        order.order_status = 'Cancelled'
        order.online_payment.payment_status = 'Cancelled'
        order.online_payment.save()
        order.save()


def generate_response_signature(order_reference, request_status, time):
    data_to_sign = f'{order_reference};{request_status};{time}'.encode('utf-8')
    return hmac.new(settings.PAYMENT_SECRET_KEY.encode('utf-8'), data_to_sign, hashlib.md5).hexdigest()


def signature_verification(merchant_signature_from_server, request):
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
    signature = hmac.new(settings.PAYMENT_SECRET_KEY.encode('utf-8'), signature, hashlib.md5).hexdigest()

    return hmac.new(settings.PAYMENT_SECRET_KEY.encode('utf-8'), signature,
                    hashlib.md5).hexdigest() == merchant_signature_from_server
