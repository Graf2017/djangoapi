from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *
from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm


class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'phone', 'city', 'address', 'index')
    list_filter = ('user', 'city', 'index')
    fields = ('user', 'first_name', 'last_name', 'phone', 'city', 'address', 'index')


class CustomUserCreateForm(UserCreationForm):
    id = forms.CharField(disabled=True, required=False)  # Додаємо поле 'id' як лише для відображення (readonly field)

    class Meta:
        model = CustomUser
        fields = "__all__"  # Додаємо поле 'id' у форму


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = "__all__"


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreateForm
    form = CustomUserChangeForm
    model = CustomUser
    ordering = ('email',)
    list_display = ('id', 'email',)
    list_display_links = ('id', 'email',)
    search_fields = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )


class ImageInline(admin.TabularInline):
    model = Image
    extra = 0


class PositionInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class PositionAdmin(admin.ModelAdmin):
    list_display = ('title', 'brand', 'slug', 'price', 'is_published', 'in_stock', 'categories')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ImageInline, ]

    def get_prepopulated_fields(self, request, obj=None):  # auto-completion of slugs when editing
        if obj:
            return {}
        return self.prepopulated_fields


# class OrderAdminForm(forms.ModelForm):
#     class Meta:
#         model = Order
#         fields = '__all__'

# def __init__(self, *args, **kwargs):  # need to show only the order's positions
#     super().__init__(*args, **kwargs)
#     if self.instance:
#         order = self.instance
#         self.fields['order_item'].queryset = order.order_item.all()


class OrderItemInline(admin.StackedInline):
    model = OrderItem
    extra = 0
    fields = 'position', 'quantity', 'saved_title', 'saved_price', 'saved_total_price'

    def get_readonly_fields(self, request, obj=None):
        if obj and isinstance(obj, OrderItem):
            return 'saved_title', 'saved_price', 'saved_total_price'
        return 'saved_title', 'saved_price', 'saved_total_price'


# class OrderItemAdmin(admin.ModelAdmin):
#     list_display = ('id', 'order', 'product', 'quantity', 'price')
#     list_display_links = ('id', 'order', 'product')
#     search_fields = ('order', 'product')
#
#     def get_prepopulated_fields(self, request, obj=None):
#         if obj:
#             return {}
#         return self.prepopulated_fields
#
#     def get_readonly_fields(self, request, obj=None):
#         if obj and isinstance(obj, OrderItem):
#             return 'product'
#         return 'product'


class OrderAdmin(admin.ModelAdmin):
    # form = OrderAdminForm
    fields = ['order_status', 'user', 'date_update', 'date_create', 'saved_total_price', 'payment_method', 'delivery']
    list_display = ['id', 'order_status', 'date_update', 'payment_method', 'date_create']
    list_display_links = ['id', 'order_status']
    search_fields = ['date_create', 'order_status', 'date_update', 'date_create']
    inlines = [OrderItemInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # queryset = queryset.filter(status__in=['Confirmed', 'Shipped', 'Delivered'])
        return queryset

    def get_inline_instances(self, request, obj=None):
        if obj and isinstance(obj, Order):
            self.inlines = [OrderItemInline]
        else:
            self.inlines = []
        return super().get_inline_instances(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if obj and isinstance(obj, Order):
            return (
                'date_create', 'user', 'date_update', 'delivery', 'payment_method',
                'saved_total_price')  # Make date_create and total_price fields read-only for existing orders
        return ('date_create',)


class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'position', 'quantity', 'total_price')
    list_display_links = ('cart', 'position')
    search_fields = ('cart', 'position')
    fields = ('cart', 'position', 'quantity')

    def get_readonly_fields(self, request, obj=None):
        if obj and isinstance(obj, CartItem):
            return 'cart'
        return 'cart', 'position', 'quantity'


admin.site.register(Position, PositionAdmin)
admin.site.register(Categories)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Image)
admin.site.register(Order, OrderAdmin)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(Delivery, DeliveryAdmin)
