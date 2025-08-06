from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('products/', ProductListAPIView.as_view(), name='product-list'),
    path('submit-order/', SubmitOrderAPIView.as_view(), name='submit-order'),
    path('products/search/', ProductSearchAPIView.as_view(), name='product-search'),
    path('categories/', CategoryListAPIView.as_view(), name='category-list'),
    path('products/<slug:slug>/', ProductDetailAPIView.as_view(), name='product-detail'),
    path('contact/', ContactMessageAPIView.as_view(), name='contact-message'),
    path('about-us/', AboutCompanyAPIView.as_view(), name='about-us'),
    path('contact-info/', ContactInfoMainPageAPIView.as_view(), name='contact-main'),
    path('products/categories/<slug:slug>/', CategoryProductsAPIView.as_view(), name='category-products'),
    path('models/', RobotGLBModelAPIView.as_view(), name='robot-glb'),
    ]

