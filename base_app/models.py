from django.contrib.auth.models import User
from django.db import models


class Position(models.Model): # a product position
    title = models.CharField(max_length=150, verbose_name='Title')
    slug = models.SlugField(max_length=100, unique=True, db_index=True, verbose_name='URL')
    description = models.CharField(max_length=500, verbose_name='Describe')
    photo = models.ImageField(upload_to="photos/%Y/%m/", verbose_name='Photo', null=True)
    price = models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Price')
    date_create = models.DateTimeField(auto_now_add=True, verbose_name='Date create')
    date_update = models.DateTimeField(auto_now=True, verbose_name='Date update')
    is_published = models.BooleanField(default=True, verbose_name='Is published')
    in_stock = models.BooleanField(default=True, verbose_name='In stock')
    categories = models.ForeignKey('Categories', on_delete=models.PROTECT,
                                   verbose_name='Category of the position', related_name='pos')

    def __str__(self):
        return f'{self.id}: {self.title}'

    def get_title(self):
        return self.title

    class Meta:
        verbose_name = 'Position'
        verbose_name_plural = 'Positions'


class Categories(models.Model): # category of the position
    name = models.CharField(max_length=50, verbose_name='Categories name')
    slug = models.SlugField(max_length=100, db_index=True, unique=True, verbose_name='Slugs URL')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'


class Client(models.Model): # a client
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    basket = models.ManyToManyField('Position', default=None, blank=True)

    def __str__(self):
        return f'{self.user.username}, id-{self.user.id}'




