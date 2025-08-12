from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

urlpatterns = [
    path('mobile-hero/', RoboticsHeroView.as_view(), name='mobile-hero'),
    path("spline-models/", SplineModelUrlView.as_view(), name="spline-model-list"),
    path("spline-proxy/", spline_proxy, name="spline-proxy"),
    path('phone-number/', PhoneNumberView.as_view(), name='phone-number'),
    path('models/', RobotGLBModelAPIView.as_view(), name='robot_file'),
    path('products/', ProductListAPIView.as_view(), name='product-list'),
    path('submit-order/', OrderCreateAPIView.as_view(), name='submit-order'),
    path('products/search/', ProductSearchAPIView.as_view(), name='product-search'),
    path('categories/', CategoryListAPIView.as_view(), name='category-list'),
    path('products/<slug:slug>/', ProductDetailAPIView.as_view(), name='product-detail'),
    path('contact/', ContactMessageCreateAPIView.as_view(), name='contact-message'),
    path('about-us/', AboutCompanyAPIView.as_view(), name='about-us'),
    path('contact-info/', ContactInfoMainPageAPIView.as_view(), name='contact-main'),
    path('products/categories/<slug:slug>/', CategoryProductsAPIView.as_view(), name='category-products'),
]
