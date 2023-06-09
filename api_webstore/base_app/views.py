from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets, mixins
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
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


class ShowCategories(mixins.ListModelMixin, viewsets.GenericViewSet):  # all categories
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
        queryset = Position.objects.filter(categories__slug=slug, is_published=True)
        return queryset


class ShowBasket(mixins.ListModelMixin, viewsets.GenericViewSet):  # show positions in the user's basket
    serializer_class = ClientSerializer
    permission_classes = (IsOwnerOrAdmin,)

    def get_queryset(self):
        user = self.request.user
        client = Client.objects.filter(user=user)
        return client


class ShowOrders(mixins.ListModelMixin, viewsets.GenericViewSet):  # show the user's order history
    serializer_class = OrdersSerializer
    permission_classes = (IsOwnerOrAdmin,)

    def get_queryset(self):
        user = self.request.user
        client = Client.objects.get(user=user)
        queryset = client.get_order_history()
        return queryset
