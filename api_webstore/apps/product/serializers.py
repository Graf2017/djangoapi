from rest_framework import serializers

from .models import *
from ..online_payment.serializers import OnlinePaymentSerializer


def get_image_url(self, obj):
    request = self.context.get('request')
    return [request.build_absolute_uri(image.image.url) for image in obj.images.all()]


class PositionSerializer(serializers.ModelSerializer):
    # categories_id = serializers.CharField(source='categories.name', read_only=True)  # name of the category
    images = serializers.SerializerMethodField(method_name='get_images')

    class Meta:
        model = Position
        fields = "id", "title", "brand", "description", "images", "price", "categories_id"

    def get_images(self, obj):
        return get_image_url(self, obj)


class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = "__all__"


class CategoryListSerializer(serializers.ModelSerializer):  # list of all category's products
    images = serializers.SerializerMethodField(method_name='get_images')

    class Meta:
        model = Position
        fields = "id", "title", "brand", "description", "images", "price", "categories_id"

    def get_images(self, obj):
        return get_image_url(self, obj)


# user = serializers.HiddenField(default=serializers.CurrentUserDefault())
# email = serializers.CharField(source='user.email')

class CartItemSerializer(serializers.ModelSerializer):
    position = PositionSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = "__all__"


class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = "__all__"


class OrderItemSerializer(serializers.ModelSerializer):
    position = PositionSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = "__all__"


class FillOrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    delivery = DeliverySerializer(read_only=True)
    # payment_method = serializers.CharField(source='payment_method', read_only=True, allow_null=True)  # need to change over choice

    class Meta:
        model = Order
        fields = ("id", "user", "order_items", "saved_total_price",
                  "payment_method", "delivery", "order_status")


class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = "id", "user", "total_price", "cart_items"


class OrdersSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True, source='order_item')
    delivery = DeliverySerializer(read_only=True)
    # online_payment = serializers.SerializerMethodField(method_name='get_online_payment')
    online_payment = OnlinePaymentSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ("id", "user", "order_items", "saved_total_price", "order_status", "date_create", "payment_method",
                  "online_payment", "delivery")

    # def get_online_payment(self, obj):
    #     return obj.online_payment.invoice_url if obj.online_payment else None

    # def get_online_payment(self, obj):
    #     if obj.order_status in ['Cancelled', 'Finished', 'New'] or obj.payment_method != 'Online payment':
    #         return OnlinePaymentSerializer(obj.online_payment).data
    #     return self.get_online_payment_status(obj)
    #
    # def get_online_payment_status(self, obj):
    #     if not obj.online_payment:
    #         obj.online_payment = OnlinePayment.objects.create(invoice_url=None, payment_status='Pending')
    #         return OnlinePaymentSerializer(obj.online_payment).data
    #     if obj.online_payment.payment_status in ['Cancelled', 'Refunded', 'Finished']:
    #         return "Finished"
    #     if obj.online_payment.is_invoice_valid():
    #         return obj.online_payment.invoice_url
    #     if obj.online_payment.payment_status == 'Paid':
    #         return 'Paid'
    #     else:
    #         self.cancel_order(obj)
    #         return None
    #
    # def cancel_order(self, obj):
    #     obj.online_payment.payment_status = 'Cancelled'
    #     obj.order_status = 'Cancelled'
    #     obj.online_payment.invoice_url = None
    #     obj.online_payment.save()
    #     obj.save()
