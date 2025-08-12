from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from modeltranslation.admin import TranslationAdmin, InlineModelAdmin
from .models import *


# --- Inline Images ---


class FeatureParagraphInline(admin.StackedInline):
    model = FeatureParagraph
    extra = 1
    exclude = ('before', 'highlight', 'after')


@admin.register(ProductFeature)
class ProductFeatureAdmin(admin.ModelAdmin):
    inlines = [FeatureParagraphInline]
    exclude = ('title', 'subtitle')


class NavigationShowcaseInline(admin.TabularInline):
    model = NavigationShowcase
    extra = 1
    exclude = ('title', 'description')


class ProductFeatureCardInline(admin.TabularInline):
    model = ProductFeatureCard
    extra = 1  # Number of empty forms shown
    exclude = ('title', 'desc')


# --- Product Admin ---
class ProductAdmin(TranslationAdmin):
    list_display = (
        'pk',
        'product_name',
        'product_category',
        'product_quantity',
        'created_at',
        'is_available_for_rent',
        'is_available_for_sale'
    )
    list_display_links = ('product_name',)
    list_editable = ('is_available_for_rent',
                     'is_available_for_sale')
    list_filter = ('product_category',
                   'created_at')
    inlines = [NavigationShowcaseInline, ProductFeatureCardInline]


# --- Category Admin ---
class CategoryAdmin(TranslationAdmin):
    list_display = ('id', 'name')


# --- Order Admin ---
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'product', 'order_type', 'created_at')
    list_display_links = ('full_name',)
    list_filter = ('order_type', 'created_at')
    # readonly_fields = ('product', 'full_name', 'company_name', 'email', 'phone', 'order_type', 'message', 'created_at')


class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'created_at')
    list_display_links = ('id',)
    list_filter = ('created_at',)


class HighlightItemInline(admin.TabularInline):
    model = HighlightItem
    extra = 3


class HighlightAdmin(admin.ModelAdmin):
    inlines = [HighlightItemInline]
    list_display = ['product', 'title']
    exclude = ('title',)


class AboutCompanyAdmin(admin.ModelAdmin):
    list_display = ('title',)
    list_display_links = ('title',)
    exclude = ('title', 'description',)


class ShowroomLocationInline(admin.TabularInline):
    model = ContactInfo.locations.through
    extra = 1


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    inlines = [ShowroomLocationInline]
    list_display = ('title',)
    exclude = ('title', 'subtitle')


@admin.register(ShowroomLocation)
class ShowroomLocationAdmin(admin.ModelAdmin):
    list_display = ('city', 'address', 'lat', 'lon')


@admin.register(AdditionalDevice)
class AdditionalDeviceAdmin(admin.ModelAdmin):
    list_display = ('title', 'product', 'order')
    list_display_links = ('title',)
    exclude = ('title', 'description')


class AboutFeatureInline(admin.TabularInline):
    model = AboutFeature
    extra = 1
    exclude = ('text',)


class FeaturedServiceInline(admin.TabularInline):
    model = FeaturedService
    extra = 1
    exclude = ('title',)


class CountStatInline(admin.TabularInline):
    model = CountStat
    extra = 1
    exclude = ('title',)


class FeatureInline(admin.TabularInline):
    model = Feature
    extra = 1
    exclude = ('title',)


class ServiceInline(admin.TabularInline):
    model = Service
    extra = 1
    exclude = ('title',)


@admin.register(RobotModel3D)
class RobotModel3DAdmin(admin.ModelAdmin):
    list_display = ('glb_file',)


@admin.register(AboutCompany)
class AboutCompanyAdmin(admin.ModelAdmin):
    inlines = [
        AboutFeatureInline,
        FeaturedServiceInline,
        CountStatInline,
        FeatureInline,
        ServiceInline
    ]
    exclude = ('title', 'subtitle', 'main_paragraph', 'section_title', 'section_subtitle',
               'conclusion', 'depth_hero_title')
    list_display = ('pk', 'title')
    # Do NOT exclude translated fields
    # django-modeltranslation handles title_en, title_ru, etc.


# ---------------- ImportExport Support for Bulk Upload ---------------- #

@admin.register(FeaturedService)
class FeaturedServiceAdmin(ImportExportModelAdmin):
    list_display = ('title_en', 'desc_en')


@admin.register(CountStat)
class CountStatAdmin(ImportExportModelAdmin):
    list_display = ('title_en', 'value')
    exclude = ('title', 'desc')


@admin.register(PhoneNumber)
class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = ('pk', 'phone_number')


@admin.register(Feature)
class FeatureAdmin(ImportExportModelAdmin):
    list_display = ('title_en',)


@admin.register(Service)
class ServiceAdmin(ImportExportModelAdmin):
    list_display = ('title_en',)


@admin.register(RoboticsHero)
class RoboricsHeroAdmin(admin.ModelAdmin):
    list_display = ('title_en',)
    exclude = ('title', 'subtitle', 'cta_text')


@admin.register(SplineModelUrl)
class SplineModelUrlAdmin(admin.ModelAdmin):
    list_display = ('pk',)
    list_display_links = ('pk',)


# --- Register Everything ---
admin.site.register(Product, ProductAdmin)
admin.site.register(Highlight, HighlightAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(ContactMessage, ContactMessageAdmin)
