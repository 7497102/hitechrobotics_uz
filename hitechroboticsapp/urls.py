from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

urlpatterns = [
    path('mobile-hero/', RoboticsHeroView.as_view(), name='mobile-hero'),
    path("spline-models/", SplineModelUrlView.as_view(), name="spline-model-list"),
    path("spline-proxy/", spline_proxy, name="spline-proxy"),
    path('models/', RobotGLBModelAPIView.as_view(), name='robot_file'),
    path('products/', ProductListAPIView.as_view(), name='product-list'),
    path('order-page/', OrderCreateAPIView.as_view(), name='order-page'),
    path('products/search/', ProductSearchAPIView.as_view(), name='product-search'),
    path('categories/', CategoryListAPIView.as_view(), name='category-list'),
    path('products/<slug:slug>/', ProductDetailAPIView.as_view(), name='product-detail'),
    path('contact/', ContactMessageCreateAPIView.as_view(), name='contact-message'),
    path('about-us/', AboutCompanyAPIView.as_view(), name='about-us'),
    path('contact-info/', ContactInfoMainPageAPIView.as_view(), name='contact-main'),
    path('products/categories/<slug:slug>/', CategoryProductsAPIView.as_view(), name='category-products'),
]
