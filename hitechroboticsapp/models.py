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
    product_image = models.ImageField(upload_to='product_image/', null=True, blank=True)
    landing_image = models.ImageField(
        upload_to='product_card_images/',
        null=True,
        blank=True,
        help_text="Image used in category landing cards"
    )

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

    # Availability
    is_available_for_rent = models.BooleanField(default=True)
    is_available_for_sale = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    # Slug
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.product_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.product_name

    def get_image_url(self):
        if self.product_image and hasattr(self.product_image, 'url'):
            return self.product_image.url
        else:
            return '/media/product_images/default.jpg'

    def get_lading_image_url(self):
        if self.landing_image and hasattr(self.landing_image, 'url'):
            return self.landing_image.url
        else:
            return '/media/product_images/default.jpg'


class ProductFeature(models.Model):
    product = models.OneToOneField(Product, related_name='features', on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    subtitle = models.TextField()

    img1 = models.ImageField(upload_to='product_images/')
    img2 = models.ImageField(upload_to='product_images/')
    img3 = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return f"Features of {self.product}"


class FeatureParagraph(models.Model):
    feature = models.ForeignKey(ProductFeature, related_name='paragraphs', on_delete=models.CASCADE)

    before = models.TextField()
    highlight = models.TextField()
    after = models.TextField()


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


class Highlight(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="highlight")
    title = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Highlight for {self.product.product_name}"


class HighlightItem(models.Model):
    highlight = models.ForeignKey(Highlight, on_delete=models.CASCADE, related_name='slides')
    image = models.ImageField(upload_to='highlights/')
    imageDuration = models.PositiveSmallIntegerField(default=3)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']

    @property
    def type(self):
        return "image"

    def __str__(self):
        return f"Slider {self.order} for {self.highlight.product.product_name}"


class AboutCompany(models.Model):
    depth_hero_title = models.CharField(max_length=255, default="Kelajak hozir")
    depth_hero_image = models.ImageField(upload_to='aboutcompany/', null=True, blank=True)
    title = models.CharField(max_length=255)
    subtitle = models.TextField()
    main_paragraph = models.TextField()
    image = models.ImageField(upload_to='aboutcompany/')
    section_title = models.CharField(max_length=255)
    section_subtitle = models.TextField()
    conclusion = models.TextField()

    def __str__(self):
        return self.title


class AboutFeature(models.Model):
    about = models.ForeignKey(AboutCompany, related_name='features', on_delete=models.CASCADE)
    text = models.TextField()

    def __str__(self):
        return f"Feature for {self.about.title}"


class ShowroomLocation(models.Model):
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    lat = models.FloatField()
    lon = models.FloatField()
    map_src = models.URLField()

    def __str__(self):
        return f"{self.city} - {self.address}"


class ContactInfo(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.TextField()
    map_src = models.URLField()
    locations = models.ManyToManyField(ShowroomLocation, related_name='contacts')

    def __str__(self):
        return self.title


class AdditionalDevice(models.Model):
    product = models.ForeignKey(Product, related_name='additionals', on_delete=models.CASCADE)

    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='additional_devices/')
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.title} (for {self.product.product_name})"


class FeaturedService(models.Model):
    about = models.ForeignKey('AboutCompany', related_name='featured_services', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    desc = models.TextField()


class CountStat(models.Model):
    about = models.ForeignKey('AboutCompany', related_name='count_stats', on_delete=models.CASCADE)
    value = models.CharField(max_length=20)  # e.g., "120+"
    title = models.CharField(max_length=100)
    desc = models.TextField()


class Feature(models.Model):
    about = models.ForeignKey('AboutCompany', related_name='features_list', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    desc = models.TextField()


class Service(models.Model):
    about = models.ForeignKey('AboutCompany', related_name='services_list', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    desc = models.TextField()


# models.py
class NavigationShowcase(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='navigation_showcase')
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='navigation_showcase/')

    def __str__(self):
        return f"{self.title} ({self.product})"


class ProductFeatureCard(models.Model):
    product = models.ForeignKey('Product', related_name='feature_cards',
                                on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    desc = models.TextField()

    class Meta:
        verbose_name = "Product Feature Card"
        verbose_name_plural = "Product Feature Cards"


class RobotModel3D(models.Model):
    glb_file = models.FileField(upload_to='models/')


class RoboticsHero(models.Model):
    image = models.ImageField(upload_to='robotImg/')
    image_alt = models.CharField(max_length=255)

    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255)
    cta_text = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class SplineModelUrl(models.Model):
    spline_url = models.CharField(max_length=500)


class PhoneNumber(models.Model):
    phone_number = models.CharField(max_length=300)
