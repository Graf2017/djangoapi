from django.contrib.auth.models import User
from django.db import models, transaction


class Position(models.Model):  # a product's position
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
    #    photos = models.ManyToManyField('Photo', verbose_name='Photos', blank=True)
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
                                   verbose_name='Category ',
                                   related_name='Category')

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
    image = models.ImageField(upload_to="photos/%Y/%m/",
                              verbose_name='Image',
                              blank=True)


class Categories(models.Model):  # category of the position
    name = models.CharField(max_length=50,
                            verbose_name='Categories name')
    slug = models.SlugField(max_length=100,
                            db_index=True,
                            unique=True,
                            verbose_name='Slugs URL')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ["name"]


class Client(models.Model):  # a client
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                related_name='client')
    basket = models.ManyToManyField('Position',
                                    default=None,
                                    blank=True)

    def __str__(self):
        return f'{self.user.username}, id-{self.user.id}'

    def confirm_order(self):
        with transaction.atomic():  # need to
            order = Order.objects.create(client=self)
            order.order_list.set(self.basket.all())
            self.basket.clear()
            order.status = 'Confirmed'
            order.save()

    def get_order_history(self):
        return self.orders.all()


class Order(models.Model):  # ordered position from basket
    client = models.ForeignKey('Client',
                               on_delete=models.PROTECT,
                               verbose_name='Order',
                               related_name='orders',
                               editable=False)
    order_list = models.ManyToManyField('Position',
                                        verbose_name='Order List',
                                        blank=True)
    status = models.CharField(max_length=20,
                              choices=(
                                  ('Pending', 'Pending'),
                                  ('Confirmed', 'Confirmed'),
                                  ('Shipped', 'Shipped'),
                                  ('Delivered', 'Delivered'),
                                  ('Finished', 'Finished'),
                              ), default='Pending')
    date_create = models.DateTimeField(auto_now_add=True,
                                       verbose_name='Date create')
    date_update = models.DateTimeField(auto_now=True,
                                       verbose_name='Last update')

    def __str__(self):
        return f'Order №- {self.id} |' \
               f' - Client: {self.client.user.username} id-{self.client.user.id}' \
               f' | - Status: {self.status}'
