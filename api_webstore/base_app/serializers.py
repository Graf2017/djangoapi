from rest_framework import serializers

from .models import *


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


class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True)
    delivery = DeliverySerializer(many=True, allow_null=True, read_only=True)

    class Meta:
        model = Cart
        fields = "id", "user", "total_price", "cart_items", "delivery"


class OrderItemSerializer(serializers.ModelSerializer):
    position = PositionSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = "__all__"


class OrdersSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True, source='order_item')
    delivery = DeliverySerializer(read_only=True)

    class Meta:
        model = Order
        fields = "id", "user", "order_items", "saved_total_price", "status", "date_create", "delivery"

