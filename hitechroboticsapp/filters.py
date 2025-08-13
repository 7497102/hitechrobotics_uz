import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(method='filter_by_category_slug')

    def filter_by_category_slug(self, queryset, name, value):
        return queryset.filter(product_category__slug=value)

    is_available_for_sale = django_filters.BooleanFilter()
    is_available_for_rent = django_filters.BooleanFilter()

    class Meta:
        model = Product
        fields = ['category', 'is_available_for_sale', 'is_available_for_rent']
