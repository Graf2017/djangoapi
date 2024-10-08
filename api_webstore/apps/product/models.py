import os
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from .utils.utils import image_upload_path, categories_image_upload_path
from api_webstore_core import settings


class Position(models.Model):
    """A product`s position"""
    title = models.CharField(max_length=150,
                             verbose_name='Title')
    slug = models.SlugField(max_length=100,
                            unique=True,
                            db_index=True,
                            verbose_name='URL')
    brand = models.CharField(max_length=40,
                             verbose_name='Brand',
                             null=True,
                             blank=True)
    description = models.CharField(max_length=500,
                                   verbose_name='Describe')
    price = models.DecimalField(decimal_places=2,
                                max_digits=10,
                                verbose_name='Price')
    date_create = models.DateTimeField(auto_now_add=True,
                                       verbose_name='Date create')
    date_update = models.DateTimeField(auto_now=True,
                                       verbose_name='Date update')
    is_published = models.BooleanField(default=True,
                                       verbose_name='Is published')
    in_stock = models.BooleanField(default=True,
                                   verbose_name='In stock')
    categories = models.ForeignKey('Categories',
                                   on_delete=models.PROTECT,
                                   verbose_name='Category',
                                   related_name='Category')
    deleted = models.BooleanField(default=False,
                                  verbose_name='Deleted')

    def __str__(self):
        return f'{self.id}: {self.title}'

    def get_title(self):
        return self.title

    class Meta:
        verbose_name = 'Position'
        verbose_name_plural = 'Positions'
        ordering = ["id"]


class Image(models.Model):  # images for a position
    position = models.ForeignKey('Position',
                                 on_delete=models.CASCADE,
                                 verbose_name='Position',
                                 related_name='images')
    image = models.ImageField(upload_to=image_upload_path,
                              verbose_name='Image',
                              blank=True)


class Categories(models.Model):  # category of the position
    name = models.CharField(max_length=50,
                            verbose_name='Categories name')
    slug = models.SlugField(max_length=100,
                            db_index=True,
                            unique=True,
                            verbose_name='Slugs URL')
    image = models.ImageField(upload_to=categories_image_upload_path,
                              verbose_name='Image',
                              blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ["name"]


class CustomUserManager(BaseUserManager):
    """Additional functional for custom user"""
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

    def get_by_natural_key(self, email):
        return self.get(email=email)


class CustomUser(AbstractUser):
    """Email use as the main one for the user account"""
    username = None
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f'{self.email}, id - {self.id}'

    def get_order_history(self):
        return self.orders.all()

    def get_cart(self):
        return self.cart.all()


class Delivery(models.Model):
    user = models.ForeignKey('CustomUser',
                             on_delete=models.CASCADE,
                             verbose_name='Delivery',
                             related_name='delivery')
    first_name = models.CharField(max_length=50,
                                  verbose_name='First name')
    last_name = models.CharField(max_length=50,
                                 verbose_name='Last name')
    phone = models.CharField(max_length=15,
                             verbose_name='Phone number')
    city = models.CharField(max_length=50,
                            verbose_name='City')
    address = models.CharField(max_length=100,
                               verbose_name='Address')
    index = models.CharField(max_length=10,
                             verbose_name='Index',
                             blank=True, null=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name} - {self.phone}, {self.address}, {self.city}, {self.index}'


class Order(models.Model):
    user = models.ForeignKey('CustomUser',
                             on_delete=models.CASCADE,
                             verbose_name='Order',
                             related_name='orders',
                             editable=False)
    delivery = models.ForeignKey('Delivery',
                                 on_delete=models.CASCADE,
                                 verbose_name='Delivery',
                                 related_name='delivery',
                                 null=True
                                 )
    date_create = models.DateTimeField(auto_now_add=True,
                                       verbose_name='Date create')
    date_update = models.DateTimeField(auto_now=True,
                                       verbose_name='Last update')
    order_status = models.CharField(max_length=20,
                                    choices=(
                                        ('New', 'New'),
                                        ('Pending', 'Pending'),
                                        ('Confirmed', 'Confirmed'),
                                        ('Shipped', 'Shipped'),
                                        ('Delivered', 'Delivered'),
                                        ('Finished', 'Finished'),
                                        ('Canceled', 'Canceled'),
                                    ), default='Pending')
    payment_method = models.CharField(max_length=20,
                                      choices=(
                                          ('Cash on delivery', 'Cash on delivery'),
                                          ('Online payment', 'Online payment')),
                                      null=True)

    @property
    def saved_total_price(self):
        return sum(item.saved_total_price for item in self.order_item.all())

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = self.generate_unique_order_number()
        super().save(*args, **kwargs)

    def generate_unique_order_number(self):
        last_order = Order.objects.order_by('-id').first()
        if last_order:
            return last_order.id + 1
        else:
            return settings.FIRST_ORDER_NUMBER

    def __str__(self):
        return f'Order № - {self.id} |' \
               f' - User: {self.user.email} id-{self.user.id}' \
               f' | - Order status: {self.order_status}'


class OrderItem(models.Model):  # save the data of a Position in the time of ordering
    order = models.ForeignKey('Order',
                              on_delete=models.CASCADE,
                              related_name='order_item')
    position = models.ForeignKey('Position',
                                 on_delete=models.DO_NOTHING,
                                 related_name='+')
    quantity = models.PositiveSmallIntegerField()
    saved_title = models.CharField(max_length=150, blank=True)
    saved_price = models.DecimalField(decimal_places=2, max_digits=10, blank=True)
    saved_total_price = models.DecimalField(decimal_places=2, max_digits=10, blank=True)

    def save(self, *args, **kwargs):  # creating the rest of the data when the object is creating
        self.saved_title = self.position.title
        self.saved_price = self.position.price
        self.saved_total_price = self.position.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.position.id}. Saved title: {self.saved_title}. Price: {self.saved_price} x {self.quantity}шт. ' \
               f'Saved total price - {self.saved_total_price}'


class Cart(models.Model):
    user = models.ForeignKey('CustomUser',
                             on_delete=models.CASCADE,
                             verbose_name='Carts',
                             related_name='cart',
                             editable=False)

    def __str__(self):
        return f'{self.user.email} id-{self.user.id}'

    @property
    def total_price(self):
        return sum(item.total_price for item in self.cart_item.all())


class CartItem(models.Model):
    position = models.ForeignKey('Position',
                                 on_delete=models.DO_NOTHING,
                                 related_name='+')
    quantity = models.PositiveSmallIntegerField(default=0)
    cart = models.ForeignKey('Cart',
                             on_delete=models.CASCADE,
                             related_name='cart_item')

    def __str__(self):
        return f'{self.position.id}: {self.position.title}- {self.quantity}'

    @property
    def total_price(self):
        total_price = self.position.price * self.quantity
        return total_price




