import requests

from rest_framework.views import APIView
from rest_framework import status
from django.utils import timezone
from rest_framework.response import Response
from api_webstore_core import settings
from apps.online_payment.models import Order
from .utils.utils import signature_verification, generate_response_signature, handle_successful_transaction, \
    handle_failed_transaction


class PaymentStatusView(APIView):
    """Processing information about order payment status from WayForPay"""

    def post(self, request, *args, **kwargs):

        merchant_signature_from_server = request.data.get('merchantSignature')
        if not signature_verification(merchant_signature_from_server, request):
            return Response({'error': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)

        reason_code = request.data.get('reasonCode')
        if reason_code == 1100:
            order_number = request.data.get('orderReference')
            print(str(request.data.get('transactionStatus')) + 'PaymentStaTUsview')  # testing, need to delete
            try:
                order = Order.objects.get(id=order_number)
            except Order.DoesNotExist:
                return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

            transaction_status = request.data.get('transactionStatus')
            if transaction_status == 'Approved':
                handle_successful_transaction(order)
            elif transaction_status in ['Refunded/Voided', 'Expired']:
                handle_failed_transaction(order)

            current_time = int(timezone.now().timestamp())
            response_signature = generate_response_signature(
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

            requests.post(settings.PAYMENT_URL, json=response_data)

        pass
