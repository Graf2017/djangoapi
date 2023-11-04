from django.db import models
from apps.product.models import Order
from api_webstore_core import settings
from django.utils import timezone


class OnlinePayment(models.Model):
    """Online payment object for the order, if order has 'Online payment' value in payment_method field.
     Included invoice and valid time the one"""
    order = models.OneToOneField(Order,
                                 on_delete=models.CASCADE,
                                 related_name='online_payment',
                                 editable=False)
    invoice_url = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20,
                                      choices=(
                                          ('Pending', 'Pending'),
                                          ('Paid', 'Paid'),
                                          ('Canceled', 'Canceled'),
                                          ('Refunded', 'Refunded'),
                                          ('Finished', 'Finished')
                                      ), default='Pending')

    def is_invoice_valid(self):
        return self.created_at + timezone.timedelta(minutes=settings.INVOICE_LIFETIME) >= timezone.now()
