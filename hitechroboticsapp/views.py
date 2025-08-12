from __future__ import annotations
from typing import Any
import requests
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.http import HttpResponse, StreamingHttpResponse
from django.utils.timezone import now
from django.views.decorators.http import require_GET
from django.views.decorators.clickjacking import xframe_options_exempt
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics, status, permissions, viewsets
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.throttling import AnonRateThrottle
from django.conf import settings

from .models import *
from .filters import ProductFilter
from .serializers import *


# Create your views here.


class ProductPagination(PageNumberPagination):
    page_size = 12


class ProductListAPIView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = ProductPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter


class OrderCreateAPIView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


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
    serializer_class = ProductDetailSerializer
    lookup_field = 'slug'


class ContactMessageCreateAPIView(generics.CreateAPIView):
    serializer_class = ContactMessageSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]  # Optional: configure rate in settings

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class AboutCompanyAPIView(APIView):
    def get(self, request):
        about = AboutCompany.objects.first()
        if not about:
            return Response({"error": "No about data found"}, status=404)

        serializer = AboutCompanySerializer(about, context={'request': request})

        depth_hero = {
            "title": about.depth_hero_title,
            "backgroundImage": (
                request.build_absolute_uri(about.depth_hero_image.url)
                if about.depth_hero_image else None
            )
        }

        return Response({
            "depthHero": depth_hero,  # ✅ Appears first
            "aboutUs": serializer.data  # ✅ Appears second
        })


class ContactInfoMainPageAPIView(RetrieveAPIView):
    queryset = ContactInfo.objects.all()
    serializer_class = ContactInfoSerializer

    def get_object(self):
        # Always return the first instance (single entry for main page)
        return ContactInfo.objects.first()


class CategoryProductsAPIView(APIView):

    def get(self, request, slug):
        try:
            category = Category.objects.get(slug=slug)
        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

        products = Product.objects.filter(product_category=category)
        serializer = ProductCardSerializer(products, many=True, context={'request': request})

        response_data = {
            "deviceLandingData": {
                slug: {
                    "label": category.name,
                    "cards": serializer.data
                }
            }
        }

        return Response(response_data, status=status.HTTP_200_OK)


class RobotGLBModelAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        model_instance = RobotModel3D.objects.last()
        if model_instance and model_instance.glb_file:
            model_url = request.build_absolute_uri(model_instance.glb_file.url)
            return Response({"modelUrl": model_url}, status=status.HTTP_200_OK)
        return Response({"detail": "No model uploaded."}, status=status.HTTP_404_NOT_FOUND)


class RoboticsHeroView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        hero = RoboticsHero.objects.first()
        if hero:
            serializer = RoboticsHeroSerializer(hero, context={'request': request})
            return Response(serializer.data)
        return Response({"detail": "Not found"}, status=404)


class PhoneNumberView(APIView):
    permission_classes = [AllowAny]

    def get(self, reqeust):
        queryset = PhoneNumber.objects.all()
        serializer = PhoneNumberSerializer(queryset, many=True)
        return Response(serializer.data)


class SplineModelUrlView(APIView):
    """
    Returns all spline model URLs from the database as JSON.
    (No pk; always a list.)
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        queryset = SplineModelUrl.objects.all()
        serializer = SplineModelUrlSerializer(queryset, many=True)
        return Response(serializer.data)


@xframe_options_exempt
@require_GET
def spline_proxy(request):
    """
    Proxies the Spline URL so you can hide the direct Spline link
    and avoid exposing it on the frontend.

    Logic:
      - If there is at least one SplineModelUrl in DB -> use the first().spline_url
      - Otherwise fall back to your hardcoded default URL.
    """
    DEFAULT_SPLINE_URL = "https://my.spline.design/nexbotrobotcharacterconcept-U710QbcCaueudeie1QgVOCuU/"

    # Prefer DB value if present
    obj = SplineModelUrl.objects.first()
    spline_url = obj.spline_url if obj and obj.spline_url else DEFAULT_SPLINE_URL

    try:
        # Pass along a minimal set of headers; stream to reduce memory usage
        upstream = requests.get(
            spline_url,
            timeout=15,
            stream=True,
            headers={
                "User-Agent": request.META.get("HTTP_USER_AGENT", "Mozilla/5.0"),
                "Accept": request.META.get("HTTP_ACCEPT", "*/*"),
            },
        )
    except requests.RequestException as e:
        return HttpResponse(
            f"Upstream request failed: {e}",
            status=502,
            content_type="text/plain; charset=utf-8",
        )

    # If upstream error, return its payload/status to the client
    content_type = upstream.headers.get("Content-Type", "text/html; charset=utf-8")

    if upstream.status_code != 200:
        content = upstream.content if not upstream.raw.closed else b""
        return HttpResponse(content, status=upstream.status_code, content_type=content_type)

    # Stream success responses
    def stream_generator():
        for chunk in upstream.iter_content(chunk_size=64 * 1024):
            if chunk:
                yield chunk

    resp = StreamingHttpResponse(stream_generator(), content_type=content_type)
    # Forward a few useful headers if present
    for hdr in ("Cache-Control", "ETag", "Last-Modified"):
        if hdr in upstream.headers:
            resp[hdr] = upstream.headers[hdr]
    return resp
