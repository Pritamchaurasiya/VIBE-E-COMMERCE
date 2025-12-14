"""
Custom filters for the store app.
"""
import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    """
    FilterSet for the Product model.
    """
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr='lte')
    in_stock = django_filters.BooleanFilter(method='filter_in_stock')
    q = django_filters.CharFilter(method='search_filter', label='Search')
    sort = django_filters.OrderingFilter(
        fields=(
            ('name', 'name'),
            ('price', 'price'),
            ('-created_at', 'newest'),
            # Note: 'relevance' and 'rating' are handled in the view for now
        )
    )

    class Meta:
        model = Product
        fields = ['category__slug', 'vendor__slug']

    def filter_in_stock(self, queryset, name, value):
        """
        Filter for products that are in stock.
        """
        if value:
            return queryset.filter(stock_quantity__gt=0)
        return queryset

    def search_filter(self, queryset, name, value):
        """
        Custom search filter for products.
        """
        from django.db.models import Q
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(brand__icontains=value) |
            Q(technical_name__icontains=value) |
            Q(target_crops__icontains=value)
        )
