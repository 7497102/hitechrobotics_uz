from django.contrib import admin
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


# --- Register Everything ---
admin.site.register(Product, ProductAdmin)
admin.site.register(Highlight, HighlightAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(ContactMessage, ContactMessageAdmin)
admin.site.register(AboutCompany, AboutCompanyAdmin)
