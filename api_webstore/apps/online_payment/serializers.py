from rest_framework import serializers
from .models import OnlinePayment


class OnlinePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnlinePayment
        fields = "__all__"




