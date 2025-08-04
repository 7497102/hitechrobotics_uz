from modeltranslation.translator import register, TranslationOptions, translator
from .models import *


@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ('product_name', 'product_description', 'delivery_contents')


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


@register(Highlight)
class HighlightTranslationOptions(TranslationOptions):
    fields = ('title',)


# @register(AboutCompany)
class AboutCompanyTranslationOptions(TranslationOptions):
    fields = ('title', 'description',)


@register(ProductFeature)
class ProductFeatureTranslationOptions(TranslationOptions):
    fields = ('title', 'subtitle',)


@register(FeatureParagraph)
class FeatureParagraphTranslationOptions(TranslationOptions):
    fields = ('before', 'highlight', 'after',)


translator.register(AboutCompany, AboutCompanyTranslationOptions)


@register(ContactInfo)
class ContactInfoTranslationOptions(TranslationOptions):
    fields = ('title', 'subtitle',)
