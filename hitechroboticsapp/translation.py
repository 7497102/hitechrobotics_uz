from modeltranslation.translator import register, TranslationOptions, translator
from .models import *


@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ('product_name', 'product_description',)


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


@register(Highlight)
class HighlightTranslationOptions(TranslationOptions):
    fields = ('title',)


# @register(AboutCompany)
class AboutCompanyTranslationOptions(TranslationOptions):
    fields = ('title', 'subtitle',
              'main_paragraph', 'section_title',
              'section_subtitle', 'conclusion', 'depth_hero_title')


@register(AboutFeature)
class AboutFeatureTranslationOptions(TranslationOptions):
    fields = ('text',)


@register(FeaturedService)
class FeaturedServiceTranslationOptions(TranslationOptions):
    fields = ('title', 'desc')


@register(CountStat)
class CountStatTranslationOptions(TranslationOptions):
    fields = ('title', 'desc')


@register(Feature)
class FeatureTranslationOptions(TranslationOptions):
    fields = ('title', 'desc')


@register(Service)
class ServiceTranslationOptions(TranslationOptions):
    fields = ('title', 'desc')


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


@register(AdditionalDevice)
class AdditionalDeviceTranslationOptions(TranslationOptions):
    fields = ('title', 'description')


@register(NavigationShowcase)
class NavigationShowcaseTranslationOptions(TranslationOptions):
    fields = ('title', 'description',)


@register(ProductFeatureCard)
class FeatureCardTranslationOptions(TranslationOptions):
    fields = ('title', 'desc')


@register(RoboticsHero)
class RoboticsHeroTranslationOptions(TranslationOptions):
    fields = ('title', 'subtitle', 'cta_text')