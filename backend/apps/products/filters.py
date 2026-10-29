import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    category = django_filters.NumberFilter(field_name='category__id')
    purity = django_filters.NumberFilter(field_name='purity__id')
    min_weight = django_filters.NumberFilter(field_name='gross_weight', lookup_expr='gte')
    max_weight = django_filters.NumberFilter(field_name='gross_weight', lookup_expr='lte')

    class Meta:
        model = Product
        fields = ['category', 'purity', 'is_active', 'branch']
