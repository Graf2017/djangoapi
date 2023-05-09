from django.forms import model_to_dict
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets, mixins
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
from .permissions import IsOwner, IsAdminOrReadOnly, IsOwnerOrAdmin, IsAdmin
from .serializers import *


class ApiPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


class ShowPositions(viewsets.ReadOnlyModelViewSet):  # return all product positions or one position
    queryset = Position.objects.filter(is_published=True)
    serializer_class = PositionSerializer
    pagination_class = ApiPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['price', 'title', 'brand', 'categories']
    search_fields = ['title', 'description', 'brand']
    ordering_fields = ['title', 'price']
# can i change this view it is filtering positions for categories? yes, i can!


class ShowCategories(mixins.ListModelMixin,
                     viewsets.GenericViewSet):  # all categories

    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer


class CategoryList(viewsets.ReadOnlyModelViewSet):  # list of all category's products
    serializer_class = CategoryListSerializer
    lookup_field = "slug"
    pagination_class = ApiPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['price', 'title', 'brand']
    search_fields = ['title', 'description', 'brand']
    ordering_fields = ['title', 'price']

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        queryset = Position.objects.filter(categories__slug=slug)
        return queryset


class ModeratePositions(viewsets.ModelViewSet):  # read, update, delete for Moderators
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    permission_classes = (IsAdmin,)


class ShowBasket(mixins.RetrieveModelMixin, viewsets.GenericViewSet):  # show the positions in the user's basket
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = (IsOwnerOrAdmin,)



