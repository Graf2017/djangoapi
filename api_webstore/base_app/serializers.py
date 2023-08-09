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
        fields = "title", "brand", "id", "images", "price", "description", "categories_id"

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
        fields = "title", "brand", "id", "images", "price", "description", "categories_id"

    def get_images(self, obj):
        return get_image_url(self, obj)


# user = serializers.HiddenField(default=serializers.CurrentUserDefault())
# email = serializers.CharField(source='user.email')

class CartItemSerializer(serializers.ModelSerializer):
    position = PositionSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = "__all__"
        

class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = "__all__"


# class CreateOrderSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Order
#         fields = "__all__"


class OrdersSerializer(serializers.ModelSerializer):
    order_items = serializers.SerializerMethodField(method_name='get_order_items')

    class Meta:
        model = Order
        fields = "id", "user", "order_items", "saved_total_price", "status", "date_create"

    def get_order_items(self, obj):
        return [order_item.position.title for order_item in obj.order_item.all()]
