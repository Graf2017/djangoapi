from rest_framework import serializers

from .models import *


class PositionSerializer(serializers.ModelSerializer):
    # categories = serializers.CharField(source='categories.name', read_only=True)  # name of the category
    categories_id = serializers.PrimaryKeyRelatedField(queryset=Categories.objects.all(), source='categories')

    class Meta:
        model = Position
        fields = "title", "brand", "id", "photo", "price", "description", "categories_id"

    def update(self, instance, validated_data):
        photo = validated_data.pop('photo', None)
        instance = super().update(instance, validated_data)
        if photo is not None:
            instance.photo = photo
            instance.save()
        return instance


class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = "__all__"


class CategoryListSerializer(serializers.ModelSerializer):  # list of all category's products
    class Meta:
        model = Position
        fields = "title", "brand", "id", "photo", "price", "description", "categories_id"


# user = serializers.HiddenField(default=serializers.CurrentUserDefault())
# email = serializers.CharField(source='user.email') #витягуємо мило з базового класу юзера

class ClientSerializer(serializers.ModelSerializer):
    basket = serializers.SerializerMethodField(method_name='get_position')  # get title from Position, not id

    class Meta:
        model = Client
        fields = "user", "basket"

    def get_position(self, obj):  # all positions of basket of the client
        all_basket = Client.objects.get(id=obj.id).basket.all()
        return all_basket.values()
