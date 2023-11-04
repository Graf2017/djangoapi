from django.apps import AppConfig


app_name = 'product'


class ProductConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.product'
    verbose_name = 'Product app'
