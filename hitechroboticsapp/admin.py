from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import *


# --- Inline Images ---
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 5


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
    inlines = [ProductImageInline]


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


# --- Register Everything ---
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(ContactMessage, ContactMessageAdmin)

