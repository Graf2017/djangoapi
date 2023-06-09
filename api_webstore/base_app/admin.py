from django.contrib import admin
from .models import *
from django import forms

class ImageInline(admin.TabularInline):
    model = Image
    extra = 0


class PositionInline(admin.TabularInline):
    model = Order.order_list.through
    extra = 0


class PositionAdmin(admin.ModelAdmin):
    list_display = ('title', 'brand', 'slug', 'price', 'is_published', 'in_stock', 'categories')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ImageInline, ]

    def get_prepopulated_fields(self, request, obj=None):  # auto-completion of slugs when editing
        if obj:
            return {}
        return self.prepopulated_fields


class OrderAdminForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__'

    def __init__(self, *args, **kwargs):  # need to show only the order's positions
        super().__init__(*args, **kwargs)
        if self.instance:
            order = self.instance
            self.fields['order_list'].queryset = order.order_list.all()


class OrderAdmin(admin.ModelAdmin):
    form = OrderAdminForm
    list_display = ['id', 'status', 'date_update', 'date_create']
    list_display_links = ['id']
    search_fields = ['date_create', 'status', 'date_update']
    inlines = [PositionInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.filter(status__in=['Confirmed', 'Shipped', 'Delivered'])
        return queryset


admin.site.register(Position, PositionAdmin)
admin.site.register(Categories)
admin.site.register(Client)
admin.site.register(Image)
admin.site.register(Order, OrderAdmin)
