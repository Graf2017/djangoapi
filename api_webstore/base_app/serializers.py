from rest_framework import serializers

from .models import *


class PositionSerializer(serializers.ModelSerializer):
    # categories = serializers.CharField(source='categories.name', read_only=True)  # name of the category
    categories_id = serializers.PrimaryKeyRelatedField(queryset=Categories.objects.all(), source='categories')

    class Meta:
        model = Position
        fields = "title", "brand", "id", "images", "price", "description", "categories_id"


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
        return [image.image.url for image in obj.images.all()]

# user = serializers.HiddenField(default=serializers.CurrentUserDefault())
# email = serializers.CharField(source='user.email') #витягуємо мило з базового класу юзера


class ClientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Client
        fields = "id", "user", "basket"


class OrdersSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = "id", "client", "order_list", "status", "date_create"
