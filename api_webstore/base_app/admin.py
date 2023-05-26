from django.contrib import admin
from .models import *


class PositionAdmin(admin.ModelAdmin):
    list_display = ('title', 'brand', 'slug', 'price', 'is_published', 'in_stock', 'categories')
    prepopulated_fields = {'slug': ('title',)}

    def get_prepopulated_fields(self, request, obj=None):  # auto-completion of slugs when editing
        if obj:
            return {}
        return self.prepopulated_fields


admin.site.register(Position, PositionAdmin)
admin.site.register(Categories)
admin.site.register(Client)
