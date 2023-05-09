from django.contrib import admin
from .models import *


class PositionAdmin(admin.ModelAdmin):
    list_display = ('title', 'brand', 'slug', 'price', 'is_published', 'in_stock', 'categories')
    prepopulated_fields = {'slug': ('title',)}


admin.site.register(Position, PositionAdmin)
admin.site.register(Categories)
admin.site.register(Client)
