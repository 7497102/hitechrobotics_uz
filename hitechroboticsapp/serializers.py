from __future__ import annotations
from urllib.parse import urlparse
from typing import Any, Dict
from modeltranslation.utils import get_language
from rest_framework import serializers
from modeltranslation.utils import get_translation_fields
from .specs_translations import SPECS_TRANSLATIONS
from .models import *
import re
from functools import cached_property



class HighlightItemSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()

    class Meta:
        model = HighlightItem
        fields = ['id', 'type', 'image', 'imageDuration']

    def get_type(self, obj):
        return "image"


class HighlightSerializer(serializers.ModelSerializer):
    slides = HighlightItemSerializer(many=True, read_only=True)

    class Meta:
        model = Highlight
        fields = ['title', 'slides']


class FeatureParagraphSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeatureParagraph
        fields = ['before', 'highlight', 'after']


class ProductFeatureSerializer(serializers.ModelSerializer):
    paragraphs = FeatureParagraphSerializer(many=True, read_only=True)
    img1 = serializers.SerializerMethodField()
    img2 = serializers.SerializerMethodField()
    img3 = serializers.SerializerMethodField()

    def get_img1(self, obj):
        request = self.context.get('request')
        if obj.img1:
            return request.build_absolute_uri(obj.img1.url) if request else obj.img1.url
        return None

    def get_img2(self, obj):
        request = self.context.get('request')
        if obj.img2:
            return request.build_absolute_uri(obj.img2.url) if request else obj.img2.url
        return None

    def get_img3(self, obj):
        request = self.context.get('request')
        if obj.img3:
            return request.build_absolute_uri(obj.img3.url) if request else obj.img3.url
        return None

    class Meta:
        model = ProductFeature
        fields = ['title',
                  'subtitle',
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
    product_category_slug = serializers.SlugField(source='product_category.slug', read_only=True)

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
            'product_category_slug',
            'specs',
            'product_speed',
            'product_weight_lifting',
            'weight_kg',
            'dimensions_cm',
            'protection_level',
            'voice_recognition',
            'front_light',
            'carrying_strap',
            'processor',
            'cameras_sensors',
            'camera_specs',
            'wifi',
            'bluetooth_version',
            'battery_life_hours',
            'battery_model',
            'battery_capacity',
            'battery_protection',
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


EMAIL_REGEX = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
PHONE_REGEX = re.compile(r"^\+?\d{7,15}$")  # e.g. +998991234567


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

        # initial_data is safe here for cross-field validation
        order_type = self.initial_data.get("order_type")
        if order_type == "buy" and not value.is_available_for_sale:
            raise serializers.ValidationError("This product is not available for sale.")
        if order_type == "rent" and not value.is_available_for_rent:
            raise serializers.ValidationError("This product is not available for rent.")
        return value

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Optional: shape response for frontend
        return {
            "id": instance.id,
            "status": "ok",
            "message": "Your request has been received. We’ll contact you soon.",
            "order": {
                "fullName": instance.full_name,
                "email": instance.email,
                "phone": instance.phone,
                "orderType": instance.order_type,
                "product": {
                    "id": instance.product_id,
                    "name": instance.product.product_name,
                    "slug": instance.product.slug,
                },
                "message": instance.message,
                "createdAt": instance.created_at.isoformat(),
            }
        }


class CategoryProductPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'product_name']


class CategorySerializer(serializers.ModelSerializer):
    products = CategoryProductPreviewSerializer(many=True, read_only=True, source='product_set')
    name_en = serializers.CharField(read_only=True)
    name_ru = serializers.CharField(read_only=True)
    name_uz = serializers.CharField(read_only=True)
    slug = serializers.SlugField(read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'products', 'slug', 'name_en', 'name_ru', 'name_uz']


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ("id", "full_name", "email", "phone_number", "message", "created_at")
        read_only_fields = ("id", "created_at")

    def validate_full_name(self, value: str) -> str:
        v = value.strip()
        if len(v) < 3:
            raise serializers.ValidationError("Full name must be at least 3 characters long.")
        if len(v) > 50:
            raise serializers.ValidationError("Full name cannot exceed 50 characters.")
        return v

    def validate_phone_number(self, value: str) -> str:
        v = value.strip()
        if not PHONE_REGEX.match(v):
            raise serializers.ValidationError("Enter a valid phone number (e.g., +998991234567).")
        return v

    def validate_message(self, value: str) -> str:
        v = value.strip()
        if len(v) < 5:
            raise serializers.ValidationError("Message must be at least 5 characters long.")
        if len(v) > 5000:
            raise serializers.ValidationError("Message must be 5000 characters or fewer.")
        return v

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Shape response for frontend
        return {
            "status": "ok",
            "message": "Your message has been received. We’ll contact you soon.",
            "data": {
                "id": data["id"],
                "fullName": data["full_name"],
                "email": data["email"],
                "phoneNumber": data["phone_number"],
                "message": data["message"],
                "createdAt": data["created_at"],
            }
        }


class AboutFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutFeature
        fields = ['text']


class FeaturedServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeaturedService
        fields = ['title', 'desc']


class CountStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = CountStat
        fields = ['value', 'title', 'desc']


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ['title', 'desc']


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['title', 'desc']


class AboutCompanySerializer(serializers.ModelSerializer):
    imageSrc = serializers.SerializerMethodField()
    featureList = serializers.SerializerMethodField()
    featuredServices = serializers.SerializerMethodField()
    counts = serializers.SerializerMethodField()
    services = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()

    title = serializers.SerializerMethodField()
    subtitle = serializers.SerializerMethodField()
    mainParagraph = serializers.SerializerMethodField()
    sectionTitle = serializers.SerializerMethodField()
    sectionSubtitle = serializers.SerializerMethodField()
    conclusion = serializers.SerializerMethodField()

    class Meta:
        model = AboutCompany
        fields = [
            'title',
            'subtitle',
            'mainParagraph',
            'imageSrc',
            'sectionTitle',
            'sectionSubtitle',
            'features',
            'conclusion',
            'featureList',
            'featuredServices',
            'counts',
            'services',
        ]

    def get_language(self):
        """Get language from request path or header (e.g. /en/, /uz/, /ru/)"""
        request = self.context.get('request')
        if request is None:
            return 'en'
        path = request.path
        if path.startswith('/uz/'):
            return 'uz'
        elif path.startswith('/ru/'):
            return 'ru'
        return 'en'

    def get_translated_field(self, obj, field_base):
        """Helper to return the translated value based on selected language"""
        lang = self.get_language()
        field_name = f"{field_base}_{lang}"
        return getattr(obj, field_name, '')

    def get_title(self, obj):
        return self.get_translated_field(obj, "title")

    def get_subtitle(self, obj):
        return self.get_translated_field(obj, "subtitle")

    def get_features(self, obj):
        return list(obj.features.values_list('text', flat=True))

    def get_mainParagraph(self, obj):
        return self.get_translated_field(obj, "main_paragraph")

    def get_sectionTitle(self, obj):
        return self.get_translated_field(obj, "section_title")

    def get_sectionSubtitle(self, obj):
        return self.get_translated_field(obj, "section_subtitle")

    def get_conclusion(self, obj):
        return self.get_translated_field(obj, "conclusion")

    def get_imageSrc(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url') and request:
            return request.build_absolute_uri(obj.image.url)
        return None

    def get_featureList(self, obj):
        features = obj.features_list.all()
        serializer = FeatureSerializer(features, many=True, context=self.context)
        return {
            "features": serializer.data,
        }

    def get_featuredServices(self, obj):
        services = obj.featured_services.all()
        return {"services": FeaturedServiceSerializer(services, many=True, context=self.context).data}

    def get_counts(self, obj):
        stats = obj.count_stats.all()
        return {"stats": CountStatSerializer(stats, many=True, context=self.context).data}

    def get_services(self, obj):
        services = obj.services_list.all()
        lang = self.get_language()
        # Optional: Translate title/subtitle in services block too
        titles = {
            'en': ("Services",
                   "We provide our clients with a full range of services for the implementation, configuration, and effective use of robotics."),
            'ru': ("Услуги",
                   "Мы предоставляем полный спектр услуг по внедрению, настройке и эффективному использованию робототехники."),
            'uz': ("Xizmatlar",
                   "Biz mijozlarga robototexnikadan samarali foydalanish, sozlash va joriy etish uchun to‘liq xizmatlar ko‘lamini taqdim etamiz.")
        }
        title, subtitle = titles.get(lang, titles['en'])
        return {
            "title": title,
            "subtitle": subtitle,
            "services": ServiceSerializer(services, many=True, context=self.context).data
        }


class ShowroomLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowroomLocation
        fields = ('city', 'address', 'lat', 'lon', 'map_src')


class ContactInfoSerializer(serializers.ModelSerializer):
    locations = ShowroomLocationSerializer(many=True, read_only=True)

    map_src = serializers.URLField(read_only=True)

    class Meta:
        model = ContactInfo
        fields = [
            'title',
            'subtitle',
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


class ProductCardSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='product_name')
    description = serializers.SerializerMethodField()
    slug = serializers.SlugField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('title', 'slug', 'description', 'image')

    def get_description(self, obj):
        desc = obj.product_description or ''
        return desc[:50] + '...' if len(desc) > 50 else desc

    def get_image(self, obj):
        request = self.context.get('request')  # 👈 get request context

        image_url = None
        if obj.landing_image and hasattr(obj.landing_image, 'url'):
            image_url = obj.landing_image.url
        elif obj.product_image and hasattr(obj.product_image, 'url'):
            image_url = obj.product_image.url
        else:
            image_url = '/media/defaults/default-card.jpg'

        if request:
            return request.build_absolute_uri(image_url)  # 👈 full URL
        return image_url


class AdditionalDeviceSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = AdditionalDevice
        fields = ['title', 'description', 'image']

    def get_image(self, obj):
        request = self.context.get('request')
        image_url = obj.image.url if obj.image else '/media/defaults/default-additional.jpg'
        return request.build_absolute_uri(image_url) if request else image_url


class IntegrationAccordionSerializer(serializers.Serializer):
    title = serializers.CharField()
    items = AdditionalDeviceSerializer(many=True)


class NavigationShowcaseSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = NavigationShowcase
        fields = ['title', 'description', 'image']

    def get_language(self):
        request = self.context.get('request')
        return request.LANGUAGE_CODE if request else 'en'

    def get_title(self, obj):
        return getattr(obj, f"title_{self.get_language()}", obj.title)

    def get_description(self, obj):
        return getattr(obj, f"description_{self.get_language()}", obj.description)

    def get_image(self, obj):
        request = self.context.get('request')  # 👈 get request context

        image_url = None
        if obj.image and hasattr(obj.image, 'url'):
            image_url = obj.image.url
        elif obj.product_image and hasattr(obj.image, 'url'):
            image_url = obj.image.url
        else:
            image_url = '/media/defaults/default-card.jpg'

        if request:
            return request.build_absolute_uri(image_url)  # 👈 full URL
        return image_url


# serializers.py
class FeatureCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductFeatureCard
        fields = ('title', 'desc')


class ProductDetailSerializer(serializers.ModelSerializer):
    features = ProductFeatureSerializer(read_only=True)
    highlights = HighlightSerializer(source='highlight', read_only=True)

    specifications = serializers.SerializerMethodField()
    featureCards = serializers.SerializerMethodField()
    navigationShowcase = serializers.SerializerMethodField()
    techSpecs = serializers.SerializerMethodField()
    integrationAccordion = serializers.SerializerMethodField()
    specs = serializers.SerializerMethodField()
    product_category_name = serializers.SerializerMethodField()
    unitreeHero = serializers.SerializerMethodField()
    infoModel = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'unitreeHero',
            'infoModel',
            'specs',
            'navigationShowcase',
            'product_name',
            'product_description',
            'slug',
            'id',
            'product_image',
            'product_category_name',
            'techSpecs',
            'product_speed',
            'product_weight_lifting',
            'weight_kg',
            'dimensions_cm',
            'protection_level',
            'voice_recognition',
            'front_light',
            'carrying_strap',
            'processor',
            'cameras_sensors',
            'camera_specs',
            'wifi',
            'bluetooth_version',
            'battery_life_hours',
            'battery_model',
            'battery_capacity',
            'battery_protection',
            'created_at',
            'featureCards',
            'integrationAccordion',
            'features',
            'highlights',
            'specifications'
        ]

    @cached_property
    def lang(self):
        request = self.context.get('request')
        return request.LANGUAGE_CODE if request else 'en'

    def translate(self, key):
        return SPECS_TRANSLATIONS.get(key, {}).get(self.lang, key)

    def bool_to_text(self, value):
        return {
            'en': 'Yes' if value else 'No',
            'ru': 'Да' if value else 'Нет',
            'uz': 'Ha' if value else 'Yo‘q'
        }.get(self.lang, 'Yes' if value else 'No')

    def get_product_category_name(self, obj):
        return getattr(obj.product_category, f'name_{self.lang}', obj.product_category.name)

    def get_specifications(self, obj):
        return [
            {
                "category": self.translate("physical"),
                "items": [
                    {"label": self.translate("dimensions"), "value": obj.dimensions_cm},
                    {"label": self.translate("protection"), "value": obj.protection_level},
                    {"label": self.translate("weight"), "value": f"{obj.weight_kg} кг"},
                ],
            },
            {
                "category": self.translate("mobility"),
                "items": [
                    {"label": self.translate("speed"), "value": f"{obj.product_speed} км/ч"},
                    {"label": self.translate("lifting"), "value": obj.product_weight_lifting},
                ],
            },
            {
                "category": self.translate("electric"),
                "items": [
                    {"label": self.translate("battery_capacity"), "value": obj.battery_capacity or "—"},
                    {"label": self.translate("battery_life"), "value": f"{obj.battery_life_hours} ч"},
                ],
            },
            {
                "category": self.translate("connectivity"),
                "items": [
                    {"label": self.translate("wifi"), "value": self.bool_to_text(obj.wifi)},
                    {"label": self.translate("bluetooth"), "value": obj.bluetooth_version or "—"},
                ],
            },
            {
                "category": self.translate("hardware"),
                "items": [
                    {"label": self.translate("processor"), "value": obj.processor or "—"},
                    {"label": self.translate("sensors"), "value": obj.cameras_sensors or "—"},
                    {"label": self.translate("camera_specs"), "value": obj.camera_specs or "—"},
                ],
            },
            {
                "category": self.translate("functions"),
                "items": [
                    {"label": self.translate("voice"), "value": self.bool_to_text(obj.voice_recognition)},
                    {"label": self.translate("light"), "value": self.bool_to_text(obj.front_light)},
                    {"label": self.translate("strap"), "value": self.bool_to_text(obj.carrying_strap)},
                ],
            },
        ]

    def get_featureCards(self, obj):
        cards = obj.feature_cards.all()
        return {
            "title": f"Advantages of {getattr(obj, f'product_name_{self.lang}', obj.product_name)}",
            "features": FeatureCardSerializer(cards, many=True).data
        }

    def get_navigationShowcase(self, obj):
        return NavigationShowcaseSerializer(obj.navigation_showcase.all(), many=True, context=self.context).data

    def get_integrationAccordion(self, obj):
        items = obj.additionals.all()
        return {
            "title": {
                "en": "Purchase additionally:",
                "ru": "Купить дополнительно:",
                "uz": "Qo‘shimcha xarid qilish:"
            }.get(self.lang, "Purchase additionally:"),
            "items": AdditionalDeviceSerializer(items, many=True, context=self.context).data
        }

    def get_specs(self, obj):
        labels = {
            "speed": {"en": "Maximum speed", "ru": "Максимальная скорость", "uz": "Maksimal tezlik"},
            "capacity": {"en": "Carrying capacity", "ru": "Грузоподъёмность", "uz": "Yuk ko‘tarish qobiliyati"},
            "wireless": {"en": "Wireless module", "ru": "Беспроводной модуль", "uz": "Simsiz aloqa moduli"},
            "autonomy": {"en": "Autonomous work", "ru": "Автономная работа", "uz": "Avtonom ish vaqti"},
        }
        result = []
        if obj.product_speed:
            result.append({"label": labels["speed"][self.lang], "value": f"{obj.product_speed} km/h"})
        if obj.product_weight_lifting:
            result.append({"label": labels["capacity"][self.lang], "value": obj.product_weight_lifting})
        wireless = []
        if obj.wifi:
            wireless.append("WiFi 6")
        if obj.bluetooth_version:
            wireless.append(f"Bluetooth {obj.bluetooth_version}")
        if wireless:
            result.append({"label": labels["wireless"][self.lang], "value": " and ".join(wireless)})
        if obj.battery_life_hours:
            result.append({"label": labels["autonomy"][self.lang], "value": f"{obj.battery_life_hours} hours"})
        return result

    def get_techSpecs(self, obj):
        blocks = []
        if obj.processor:
            blocks.append({"title": "Processors", "tags": [obj.processor]})
        camera_tags = list(filter(None, [obj.cameras_sensors, obj.camera_specs]))
        if camera_tags:
            blocks.append({"title": "Cameras and sensors", "tags": camera_tags})
        connectivity = []
        if obj.wifi:
            connectivity.append("WiFi 6")
        if obj.bluetooth_version:
            connectivity.append(f"Bluetooth {obj.bluetooth_version}")
        if connectivity:
            blocks.append({"title": "Additional devices", "tags": connectivity})
        battery = list(filter(None, [
            f"{obj.battery_life_hours} hours" if obj.battery_life_hours else None,
            obj.battery_capacity,
            obj.battery_model
        ]))
        if battery:
            blocks.append({"title": "Battery", "tags": battery})
        return {"blocks": blocks}

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.product_image and hasattr(obj.product_image, 'url'):
            url = obj.product_image.url
        else:
            url = '/media/defaults/default-card.jpg'
        return request.build_absolute_uri(url) if request else url

    def get_unitreeHero(self, obj):
        texts = {
            "en": {"subtitle": "Bionic robot in basic configuration", "priceText": "Available for rent",
                   "ctaText": "Make an order"},
            "ru": {"subtitle": "Бионический робот в базовой комплектации", "priceText": "Доступен для аренды",
                   "ctaText": "Сделать заказ"},
            "uz": {"subtitle": "Asosiy konfiguratsiyadagi bionik robot", "priceText": "Ijaraga olish mumkin",
                   "ctaText": "Buyurtma berish"},
        }[self.lang]
        return {
            "title": getattr(obj, f'product_name_{self.lang}', obj.product_name),
            "subtitle": texts["subtitle"],
            "priceText": texts["priceText"],
            "ctaText": texts["ctaText"],
            "imageSrc": self.get_image(obj),
            "imageAlt": getattr(obj, f'product_name_{self.lang}', obj.product_name),
            "showParticles": True
        }

    def get_infoModel(self, obj):
        texts = {
            "en": "Available for sale",
            "ru": "Доступен для продажи",
            "uz": "Sotuvga mavjud"
        }
        return {
            "chip": obj.battery_model,
            "display": obj.processor,
            "battery": obj.battery_capacity,
            "material": obj.bluetooth_version,
            "price": texts[self.lang]
        }


class RoboticsHeroSerializer(serializers.ModelSerializer):
    imageSrc = serializers.SerializerMethodField()
    imageAlt = serializers.CharField(source='image_alt')
    title = serializers.SerializerMethodField()
    subtitle = serializers.SerializerMethodField()
    ctaText = serializers.SerializerMethodField()

    class Meta:
        model = RoboticsHero
        fields = ['imageSrc', 'imageAlt', 'title', 'subtitle', 'ctaText']

    def get_imageSrc(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.image.url) if obj.image else None

    def get_title(self, obj):
        return getattr(obj, f"title_{get_language()}") or obj.title

    def get_subtitle(self, obj):
        return getattr(obj, f"subtitle_{get_language()}") or obj.subtitle

    def get_ctaText(self, obj):
        return getattr(obj, f"cta_text_{get_language()}") or obj.cta_text


class SplineModelUrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = SplineModelUrl
        fields = ("pk", "spline_url")
