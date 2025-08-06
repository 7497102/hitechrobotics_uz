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
    features = serializers.SerializerMethodField()
    featuredServices = serializers.SerializerMethodField()
    counts = serializers.SerializerMethodField()
    services = serializers.SerializerMethodField()

    class Meta:
        model = AboutCompany
        fields = [
            'title',
            'subtitle',
            'main_paragraph',
            'imageSrc',
            'section_title',
            'section_subtitle',
            'features',
            'conclusion',
            'featuredServices',
            'counts',
            'services',
        ]

    def get_imageSrc(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            return request.build_absolute_uri(obj.image.url)
        return None

    def get_features(self, obj):
        # Replace this with your real FeatureSerializer
        features = obj.features_list.all()
        serializer = FeatureSerializer(features, many=True)

        return {
            "features": serializer.data,
        }

    def get_featuredServices(self, obj):
        services = obj.featured_services.all()
        return {"services": FeaturedServiceSerializer(services, many=True).data}

    def get_counts(self, obj):
        stats = obj.count_stats.all()
        return {"stats": CountStatSerializer(stats, many=True).data}

    def get_services(self, obj):
        services = obj.services_list.all()
        return {
            "title": "Services",
            "subtitle": "We provide our clients with a full range of services for the implementation, configuration, and effective use of robotics.",
            "services": ServiceSerializer(services, many=True).data
        }


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
        fields = ('title_en', 'title_ru', 'title_uz', 'desc_en', 'desc_ru', 'desc_uz')


class ProductDetailSerializer(serializers.ModelSerializer):
    featureCards = serializers.SerializerMethodField()
    navigationShowcase = serializers.SerializerMethodField()
    techSpecs = serializers.SerializerMethodField()
    integrationAccordion = serializers.SerializerMethodField()
    specs = serializers.SerializerMethodField()
    features = ProductFeatureSerializer(read_only=True)
    highlights = HighlightSerializer(source='highlight', read_only=True)
    product_category_name = serializers.SerializerMethodField()
    unitreeHero = serializers.SerializerMethodField()
    infoModel = serializers.SerializerMethodField()

    def get_product_category_name(self, obj):
        lang = self.context['request'].META.get('HTTP_ACCEPT_LANGUAGE', 'en')[:2]
        return getattr(obj.product_category, f'name_{lang}', obj.product_category.name)

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
            'highlights',
            'product_name',  # локализуется автоматически через modeltranslation
            'product_description',  # то же самое
            'product_image',
            'product_category_name',  # мультиязычный вывод категории

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
            'features',
            'featureCards',
            'integrationAccordion'
        ]

    def get_integrationAccordion(self, obj):
        items = obj.additionals.all()  # related_name on ForeignKey in AdditionalDevice
        serializer = AdditionalDeviceSerializer(items, many=True, context=self.context)
        return {
            "title": "Purchase additionally:",
            "items": serializer.data
        }

    def get_navigationShowcase(self, obj):
        showcases = obj.navigation_showcase.all()
        return NavigationShowcaseSerializer(showcases, many=True, context=self.context).data

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

    def get_techSpecs(self, obj):
        blocks = []

        # 1. Processor block
        if obj.processor:
            blocks.append({
                "title": "Processors",
                "tags": [obj.processor]
            })

        # 2. Cameras & sensors
        camera_tags = []
        if obj.cameras_sensors:
            camera_tags.append(obj.cameras_sensors)
        if obj.camera_specs:
            camera_tags.append(obj.camera_specs)
        if camera_tags:
            blocks.append({
                "title": "Cameras and sensors",
                "tags": camera_tags
            })

        # 3. Connectivity
        connectivity = []
        if obj.wifi:
            connectivity.append("WiFi 6")
        if obj.bluetooth_version:
            connectivity.append(f"Bluetooth {obj.bluetooth_version}")
        if connectivity:
            blocks.append({
                "title": "Additional devices",
                "tags": connectivity
            })

        # 4. Battery
        battery_tags = []
        if obj.battery_life_hours:
            battery_tags.append(f"{obj.battery_life_hours} hours")
        if obj.battery_capacity:
            battery_tags.append(obj.battery_capacity)
        if obj.battery_model:
            battery_tags.append(obj.battery_model)
        if battery_tags:
            blocks.append({
                "title": "Battery",
                "tags": battery_tags
            })

        return {"blocks": blocks}

    def get_language(self):
        request = self.context.get('request')
        return request.LANGUAGE_CODE if request else 'en'

    def get_image(self, obj):
        request = self.context.get('request')  # 👈 get request context

        image_url = None
        if obj.product_image and hasattr(obj.product_image, 'url'):
            image_url = obj.product_image.url
        elif obj.product_image and hasattr(obj.product_image, 'url'):
            image_url = obj.product_image.url
        else:
            image_url = '/media/defaults/default-card.jpg'

        if request:
            return request.build_absolute_uri(image_url)  # 👈 full URL
        return image_url

    def get_unitreeHero(self, obj):
        lang = self.get_language()

        texts = {
            "en": {
                "subtitle": "Bionic robot in basic configuration",
                "priceText": "Available for rent",
                "ctaText": "Make an order",
            },
            "ru": {
                "subtitle": "Бионический робот в базовой комплектации",
                "priceText": "Доступен для аренды",
                "ctaText": "Сделать заказ",
            },
            "uz": {
                "subtitle": "Asosiy konfiguratsiyadagi bionik robot",
                "priceText": "Ijaraga olish mumkin",
                "ctaText": "Buyurtma berish",
            }
        }

        t = texts.get(lang, texts["en"])

        return {
            "title": getattr(obj, f'product_name_{lang}', ''),
            "subtitle": t["subtitle"],
            "priceText": t["priceText"],
            "ctaText": t["ctaText"],
            "imageSrc": self.get_image(obj),  # ✅ call with self + obj
            "imageAlt": getattr(obj, f'product_name_{lang}', ''),
            "showParticles": True
        }

        # fallback to English

    def get_infoModel(self, obj):
        lang = self.get_language()

        static_texts = {
            "en": {
                "price": "Available for sale"
            },
            "ru": {
                "price": "Доступен для продажи"
            },
            "uz": {
                "price": "Sotuvga mavjud"
            }
        }

        t = static_texts.get(lang, static_texts["en"])

        return {
            "chip": obj.battery_model,
            "display": obj.processor,
            "battery": obj.battery_capacity,
            "material": obj.bluetooth_version,
            "price": t["price"],
        }

    def get_featureCards(self, obj):
        lang = self.context.get('lang', 'en')

        cards = obj.feature_cards.all()
        return {
            "title": f"Advantages of {obj.product_name_en}",
            "features": FeatureCardSerializer(cards, many=True).data
        }


