from modeltranslation.translator import register, TranslationOptions
from .models import Product, Category


@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ('product_name', 'product_description', 'delivery_contents')


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'description')
