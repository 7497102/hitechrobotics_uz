from modeltranslation.utils import get_language
from rest_framework import serializers
from modeltranslation.utils import get_translation_fields
from .models import *
import re


class HighlightItemSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()

    class Meta:
        model = HighlightItem
        fields = ['id', 'type', 'image', 'imageDuration']

    def get_type(self, obj):
        return "image"


class HighlightSerializer(serializers.ModelSerializer):
    slides = HighlightItemSerializer(many=True, read_only=True)

    title_en = serializers.CharField(read_only=True)
    title_ru = serializers.CharField(read_only=True)
    title_uz = serializers.CharField(read_only=True)

    class Meta:
        model = Highlight
        fields = ['title_en',
                  'title_ru',
                  'title_uz',
                  'slides']


class FeatureParagraphSerializer(serializers.ModelSerializer):
    before_en = serializers.CharField(read_only=True)
    before_ru = serializers.CharField(read_only=True)
    before_uz = serializers.CharField(read_only=True)

    highlight_en = serializers.CharField(read_only=True)
    highlight_ru = serializers.CharField(read_only=True)
    highlight_uz = serializers.CharField(read_only=True)

    after_en = serializers.CharField(read_only=True)
    after_ru = serializers.CharField(read_only=True)
    after_uz = serializers.CharField(read_only=True)

    class Meta:
        model = FeatureParagraph
        fields = ['before_en', 'before_ru', 'before_uz',
                  'highlight_en', 'highlight_ru', 'highlight_uz',
                  'after_en', 'after_ru', 'after_uz', ]


class ProductFeatureSerializer(serializers.ModelSerializer):
    paragraphs = FeatureParagraphSerializer(many=True, read_only=True)
    img1 = serializers.SerializerMethodField()
    img2 = serializers.SerializerMethodField()
    img3 = serializers.SerializerMethodField()

    def get_img1(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.img1.url) if obj.img1 and request else obj.img1.url

    def get_img2(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.img2.url) if obj.img2 and request else obj.img2.url

    def get_img3(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.img3.url) if obj.img3 and request else obj.img3.url

    title_en = serializers.CharField(read_only=True)
    title_ru = serializers.CharField(read_only=True)
    title_uz = serializers.CharField(read_only=True)

    subtitle_en = serializers.CharField(read_only=True)
    subtitle_ru = serializers.CharField(read_only=True)
    subtitle_uz = serializers.CharField(read_only=True)

    class Meta:
        model = ProductFeature
        fields = ['title_en',
                  'title_ru',
                  'title_uz',
                  'subtitle_en',
                  'subtitle_ru',
                  'subtitle_uz',
                  'img1',
                  'img2',
                  'img3',
                  'paragraphs']


# Adjust if needed

class ProductSerializer(serializers.ModelSerializer):
    specs = serializers.SerializerMethodField()
    features = ProductFeatureSerializer(read_only=True)
    highlights = HighlightSerializer(source='highlight', read_only=True)
    product_category_name = serializers.SerializerMethodField()

    def get_product_category_name(self, obj):
        lang = self.context['request'].META.get('HTTP_ACCEPT_LANGUAGE', 'en')[:2]
        return getattr(obj.product_category, f'name_{lang}', obj.product_category.name)

    class Meta:
        model = Product
        fields = [
            'id',
            'highlights',
            'product_name',  # локализуется автоматически через modeltranslation
            'product_description',  # то же самое
            'product_image',
            'product_category_name',  # мультиязычный вывод категории
            'specs',
            'created_at',
            'features',
            'slug',
        ]

    def get_specs(self, obj):
        lang = self.context['request'].META.get('HTTP_ACCEPT_LANGUAGE', 'en')[:2]
        lang = lang if lang in ['en', 'ru', 'uz'] else 'en'

        labels = {
            "en": {
                "speed": "Maximum speed",
                "capacity": "Carrying capacity",
                "wireless": "Wireless module",
                "autonomy": "Autonomous work"
            },
            "ru": {
                "speed": "Максимальная скорость",
                "capacity": "Грузоподъёмность",
                "wireless": "Беспроводной модуль",
                "autonomy": "Автономная работа"
            },
            "uz": {
                "speed": "Maksimal tezlik",
                "capacity": "Yuk ko‘tarish qobiliyati",
                "wireless": "Simsiz aloqa moduli",
                "autonomy": "Avtonom ish vaqti"
            }
        }

        specs = []

        if obj.product_speed:
            specs.append({
                "label": labels[lang]["speed"],
                "value": f"{obj.product_speed} km/h"
            })

        if obj.product_weight_lifting:
            specs.append({
                "label": labels[lang]["capacity"],
                "value": obj.product_weight_lifting
            })

        connectivity = []
        if obj.wifi:
            connectivity.append("WiFi 6")
        if obj.bluetooth_version:
            connectivity.append(f"Bluetooth {obj.bluetooth_version}")
        if connectivity:
            specs.append({
                "label": labels[lang]["wireless"],
                "value": " and ".join(connectivity)
            })

        if obj.battery_life_hours:
            specs.append({
                "label": labels[lang]["autonomy"],
                "value": f"{obj.battery_life_hours} hours"
            })

        return specs


EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
PHONE_REGEX = re.compile(r'^\+?\d{9,15}$')


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

    def validate_full_name(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError("Full name must be at least 3 characters long.")
        return value

    def validate_email(self, value):
        if not EMAIL_REGEX.match(value):
            raise serializers.ValidationError("Enter a valid email address.")
        return value

    def validate_phone(self, value):
        value = value.strip()
        if not PHONE_REGEX.match(value):
            raise serializers.ValidationError("Enter a valid phone number (e.g., +998991234567).")
        return value

    def validate_order_type(self, value):
        if value not in ['buy', 'rent']:
            raise serializers.ValidationError("Order type must be 'buy' or 'rent'.")
        return value

    def validate_product(self, value):
        if value is None:
            raise serializers.ValidationError("Product must be selected.")

        order_type = self.initial_data.get("order_type")
        if order_type == "buy" and not value.is_available_for_sale:
            raise serializers.ValidationError("This product is not available for sale.")
        if order_type == "rent" and not value.is_available_for_rent:
            raise serializers.ValidationError("This product is not available for rent.")

        return value


class CategoryProductPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'product_name']


class CategorySerializer(serializers.ModelSerializer):
    products = CategoryProductPreviewSerializer(many=True, read_only=True, source='product_set')

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'products']


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = '__all__'

    def validate_full_name(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Name must be at least 3 characters.")
        return value

    def validate_message(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Message must be at least 10 characters.")
        return value


class AboutCompanySerializer(serializers.ModelSerializer):
    title_en = serializers.CharField(read_only=True)
    title_ru = serializers.CharField(read_only=True)
    title_uz = serializers.CharField(read_only=True)
    description_en = serializers.CharField(read_only=True)
    description_ru = serializers.CharField(read_only=True)
    description_uz = serializers.CharField(read_only=True)

    class Meta:
        model = AboutCompany
        fields = ['title_en',
                  'title_ru',
                  'title_uz',
                  'description_en',
                  'description_ru',
                  'description_uz',
                  'image']


class ShowroomLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowroomLocation
        fields = ('city', 'address', 'lat', 'lon', 'map_src')


class ContactInfoSerializer(serializers.ModelSerializer):
    locations = ShowroomLocationSerializer(many=True, read_only=True)

    title_en = serializers.CharField(read_only=True)
    title_uz = serializers.CharField(read_only=True)
    title_ru = serializers.CharField(read_only=True)

    subtitle_en = serializers.CharField(read_only=True)
    subtitle_uz = serializers.CharField(read_only=True)
    subtitle_ru = serializers.CharField(read_only=True)

    map_src = serializers.URLField(read_only=True)

    class Meta:
        model = ContactInfo
        fields = [
            'title_en', 'title_uz', 'title_ru',
            'subtitle_en', 'subtitle_uz', 'subtitle_ru',
            'map_src',
            'locations'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        lang = get_language()

        title = data.get(f"title_{lang}", "")
        subtitle = data.get(f"subtitle_{lang}", "")
        map_src = data.get("map_src")
        locations = data.get("locations")

        return {
            "contact": {
                "title": title,
                "subtitle": subtitle,
                "mapSrc": map_src,
                "locations": locations
            }
        }
