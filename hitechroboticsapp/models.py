from django.db import models
from django.urls import reverse
from django.utils.text import slugify


# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    # General Info
    product_name = models.CharField(max_length=100, help_text="Name of the product")
    product_description = models.TextField(help_text="Description of the product")
    product_category = models.ForeignKey(Category, on_delete=models.CASCADE, help_text="Category of the product")
    product_quantity = models.IntegerField()

    # Specs
    product_speed = models.IntegerField(help_text="Speed in km/h or m/s")
    product_weight_lifting = models.CharField(max_length=30, help_text="How much weight robot can lift")
    weight_kg = models.FloatField(help_text="Robot's own weight (e.g. 15)")
    dimensions_cm = models.CharField(max_length=50, help_text="Format: Length x Width x Height")
    protection_level = models.CharField(max_length=10, blank=True, null=True, help_text="IP level protection")

    # Features
    voice_recognition = models.BooleanField(default=False)
    front_light = models.BooleanField(default=False)
    carrying_strap = models.BooleanField(default=False)

    # Hardware
    processor = models.CharField(max_length=255, blank=True, null=True)
    cameras_sensors = models.CharField(max_length=255, blank=True, null=True)
    camera_specs = models.CharField(max_length=255, blank=True, null=True)

    # Connectivity
    wifi = models.BooleanField(default=False)
    bluetooth_version = models.CharField(max_length=10, blank=True, null=True)

    # Battery
    battery_life_hours = models.FloatField(blank=True, null=True)
    battery_model = models.CharField(max_length=100, blank=True, null=True)
    battery_capacity = models.CharField(max_length=100, blank=True, null=True)
    battery_protection = models.BooleanField(default=False)

    # Logistics
    delivery_contents = models.TextField(help_text="Comma-separated list of delivery items")

    # Availability
    is_available_for_rent = models.BooleanField(default=True)
    is_available_for_sale = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    #Slug
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.product_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.product_name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    alt_text = models.CharField(max_length=100, blank=True, help_text="Image description for SEO")

    def __str__(self):
        return f"Image for {self.product.product_name}"

    def get_image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        else:
            return '/media/product_images/default.jpg'


class Order(models.Model):
    ORDER_TYPE_CHOICES = [
        ('buy', 'Buy'),
        ('rent', 'Rent'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=300, null=True, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    order_type = models.CharField(max_length=15, choices=ORDER_TYPE_CHOICES)
    message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.order_type} {self.product.product_name}"


class ContactMessage(models.Model):
    full_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name
