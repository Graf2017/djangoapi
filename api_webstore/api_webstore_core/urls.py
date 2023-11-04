from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from drf_yasg import openapi
from drf_yasg.views import get_schema_view as get_schema_views

schema_view = get_schema_views(  # add openapi documentation
    openapi.Info(
        title="eCommerce",
        default_version="1.0.0",
        description="API Documentation",
    ),
    public=True,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/',
         include([
             path('auth/session/', include('rest_framework.urls')),  # /api/v1/auth/session/login/
             path('auth/', include('djoser.urls')),
             path('auth/', include('djoser.urls.authtoken')),  # /api/v1/auth/token/login/
             path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name="swagger-schema"),
             path('online-payment/', include('apps.online_payment.urls')),
             path('', include('apps.product.urls')),
         ])),

]

