from django.urls import path, include
from rest_framework import routers
import apps.product.views as base_views


router = routers.DefaultRouter()
router.register(r'positions', base_views.ShowPositions, basename='positions')
router.register(r'categories', base_views.ShowCategories, basename='show_categories')
router.register(r'orders', base_views.ShowOrders, basename='history')
router.register(r'delivery', base_views.DeliveryView, basename='delivery')

urlpatterns = [
         path('categories/<slug:slug>/', base_views.CategoryList.as_view({'get': 'list'})),
         path('', include(router.urls)),
         path('cart/', base_views.ShowCart.as_view()),
         path('create-order/', base_views.CreateCompleteOrder.as_view(), name='create-order'),
         path('fill-order/<int:pk>/', base_views.FillOrder.as_view(), name='fill-order'),

]