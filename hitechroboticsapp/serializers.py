from rest_framework import serializers
from .models import Product, ProductImage, Category, Order, ContactMessage
import re


class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url

    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text']


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    product_category = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )

    # Add multilingual fields manually
    # product_name_en = serializers.CharField(read_only=True)
    # product_name_ru = serializers.CharField(read_only=True)
    # product_name_uz = serializers.CharField(read_only=True)
    #
    # product_description_en = serializers.CharField(read_only=True)
    # product_description_ru = serializers.CharField(read_only=True)
    # product_description_uz = serializers.CharField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',

            # multilingual fields
            'product_name',
            'product_description',

            'product_category',
            'product_quantity',
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
            'delivery_contents',
            'is_available_for_rent',
            'is_available_for_sale',
            'created_at',
            'images',
            'slug',
        ]


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
