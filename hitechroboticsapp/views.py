from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q

from .models import *
from .filters import ProductFilter
from .serializers import (ProductSerializer, OrderSerializer, CategorySerializer, ContactMessageSerializer,
                          AboutCompanySerializer, ContactInfoSerializer)


# Create your views here.


class ProductPagination(PageNumberPagination):
    page_size = 12


class ProductListAPIView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = ProductPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter


class SubmitOrderAPIView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class ProductSearchAPIView(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.all()
        query = self.request.query_params.get('q')

        if query:
            queryset = queryset.filter(
                Q(product_name__icontains=query) |
                Q(product_category__name__icontains=query)
            )
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({
                "message": "No robots found matching your search.",
                "results": []
            }, status=200)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class CategoryListAPIView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductDetailAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'slug'


class ContactMessageAPIView(generics.CreateAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer


class AboutCompanyAPIView(generics.ListAPIView):
    queryset = AboutCompany.objects.all()
    serializer_class = AboutCompanySerializer


class ContactInfoMainPageAPIView(RetrieveAPIView):
    queryset = ContactInfo.objects.all()
    serializer_class = ContactInfoSerializer

    def get_object(self):
        # Always return the first instance (single entry for main page)
        return ContactInfo.objects.first()