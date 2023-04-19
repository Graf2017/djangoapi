from rest_framework import serializers

from .models import *


class PositionSerializer(serializers.ModelSerializer):
    categories = serializers.CharField(source='categories.name') # відображаємо не айді категорії,а її назву
    class Meta:
        model = Position
        fields = "__all__"


class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = "__all__"

# user = serializers.HiddenField(default=serializers.CurrentUserDefault())
# email = serializers.CharField(source='user.email') #витягуємо мило з базового класу юзера

class ClientSerializer(serializers.ModelSerializer):
    # need to get title from Position, not id
    basket = serializers.SerializerMethodField(method_name='get_position')
    class Meta:
        model = Client
        fields = "user", "basket"

    def get_position(self, obj):
        list = Client.objects.get(id=obj.id).basket.all() # all positions of basket of the client
        positions = Position.objects.get(id=2).client_set.all() #all client who to basket the position
        frompos = Position.objects.filter(client__id=obj.id) # or Position.objects.filter(client=Client.objects.filter(id=obj.id)
        clientpoint = Client.objects.filter(basket__id=1)
        print(Position.objects.all().values_list('title', flat=True))
        return list.values()


#qs = Album.objects.prefetch_related('tracks')