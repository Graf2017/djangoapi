from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from base_app.views import *

router = routers.DefaultRouter()
router.register(r'positions', ShowPositions, basename='positions')
router.register(r'moderate', ModeratePositions, basename='moderate_positions')
router.register(r'basket', ShowBasket, basename='basket')
router.register(r'categories', ShowCategories, basename='show_categories')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/categories/<slug:slug>/', CategoryList.as_view({'get': 'list'})),
    path('api/', include(router.urls)),
    path('api/auth/session/', include('rest_framework.urls')),  # /api/auth/session/login/
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),        # /api/auth/token/login/

]
