from django.urls import path
import apps.online_payment.views as online_payment_views


app_name = 'online_payment'


urlpatterns = [
    path('payment-status/', online_payment_views.PaymentStatusView.as_view(), name='online-payment-status'),

]