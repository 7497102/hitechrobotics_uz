from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import translation

from .models import Product, Category


class ProductAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(
            slug='humanoid-robots',
            description_en="English description",
            description_ru="Описание на русском",
            description_uz="Tavsif o'zbek tilida",
        )
        self.category.name_en = "Humanoid Robots"
        self.category.name_ru = "Гуманоидные роботы"
        self.category.name_uz = "Gumanoid robotlar"
        self.category.save()

        self.product = Product.objects.create(
            slug='unitree-g1-basic',
            product_category=self.category,
            product_quantity=10,
            product_speed=12,
            product_weight_lifting="10 kg",
            weight_kg=25.0,
            dimensions_cm="100x40x25",
            protection_level="IP67",
            voice_recognition=True,
            front_light=True,
            carrying_strap=True,
            processor="ARM",
            cameras_sensors="Lidar, IR",
            camera_specs="1080p",
            wifi=True,
            bluetooth_version="5.0",
            battery_life_hours=8,
            battery_model="Model-X",
            battery_capacity="8000mAh",
            battery_protection=True,
            delivery_contents="Robot, Charger, Manual",
            is_available_for_sale=True,
            is_available_for_rent=True,
        )
        self.product.product_name_en = "Unitree G1 Basic"
        self.product.product_name_ru = "Юнитри G1 Базовый"
        self.product.product_name_uz = "Unitree G1 Asosiy"
        self.product.product_description_en = "English description"
        self.product.product_description_ru = "Описание на русском"
        self.product.product_description_uz = "O'zbekcha tavsif"
        self.product.save()

    def test_product_created(self):
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(Category.objects.count(), 1)

    def test_product_list_default_language(self):
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertIn("Unitree G1 Basic", str(response.data))

    def test_product_list_russian(self):
        with translation.override('ru'):
            url = reverse('product-list') + '?category=humanoid-robots'
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn("Юнитри G1 Базовый", str(response.data))

    def test_product_list_uzbek(self):
        with translation.override('uz'):
            url = reverse('product-list') + '?category=humanoid-robots'
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn("Unitree G1 Asosiy", str(response.data))
