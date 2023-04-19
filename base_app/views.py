from django.forms import model_to_dict
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets
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


class ShowPositions(viewsets.ReadOnlyModelViewSet): #returns all product positions or a position
    serializer_class = PositionSerializer
    pagination_class = ApiPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['price']
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'price']

    def get_queryset(self):  # need to name basename in router
        pk = self.kwargs.get('pk')
        if not pk:
            return Position.objects.all()
        return Position.objects.filter(pk=pk)


class RUD(viewsets.ModelViewSet):  # get, put, patch, delete
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    permission_classes = (IsAdmin,)


class ClientViewSet(viewsets.ModelViewSet):
    serializer_class = ClientSerializer
    permission_classes = (IsOwnerOrAdmin,)

    def get_queryset(self): #get pk from url like 'client/2/'
        pk = self.kwargs.get('pk')
       # need a list of objects, not an one
        return Client.objects.filter(pk=pk)
