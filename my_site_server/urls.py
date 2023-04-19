from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from base_app.views import *


router = routers.DefaultRouter()
router.register(r'positions', ShowPositions, basename='positions')
router.register(r'rud', RUD, basename='rud')
router.register(r'client', ClientViewSet, basename='client')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/session/', include('rest_framework.urls')),
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),
]
