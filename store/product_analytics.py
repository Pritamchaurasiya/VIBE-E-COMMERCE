"""
Product Analytics Service for VIBE E-Commerce
Provides insights on product performance, sales trends, and inventory management.
"""
import logging
from datetime import timedelta
from decimal import Decimal
from typing import Dict, List, Optional

from django.db.models import Sum, Count, Avg, F
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.core.cache import cache

logger = logging.getLogger(__name__)


class ProductAnalyticsService:
    """
    Service for product analytics and insights.
    """

    CACHE_TIMEOUT = 1800  # 30 minutes

    def __init__(self):
        pass

    def _get_model(self, model_name: str):
        """Lazy import to avoid circular imports."""
        # pylint: disable=import-outside-toplevel
        from store.models import Product, Order, OrderItem, Review, Category
        models_map = {
            'Product': Product,
            'Order': Order,
            'OrderItem': OrderItem,
            'Review': Review,
            'Category': Category,
        }
        return models_map.get(model_name)

    def get_best_sellers(
        self,
        days: int = 30,
        limit: int = 10,
        category_id: Optional[int] = None
    ) -> List[Dict]:
        """
        Get best-selling products.

        Args:
            days: Number of days to look back
            limit: Maximum number of products
            category_id: Filter by category

        Returns:
            List of best-selling products
        """
        cache_key = f'best_sellers_{days}_{limit}_{category_id}'
        cached = cache.get(cache_key)
        if cached:
            return cached

        # pylint: disable=invalid-name
        order_item_model = self._get_model('OrderItem')
        product_model = self._get_model('Product')

        start_date = timezone.now() - timedelta(days=days)

        # pylint: disable=no-member
        queryset = order_item_model.objects.filter(
            order__created_at__gte=start_date,
            order__status__in=['delivered', 'shipped', 'confirmed']
        )

        if category_id:
            queryset = queryset.filter(product__category_id=category_id)

        top_products = queryset.values('product_id').annotate(
            total_sold=Sum('quantity'),
            total_revenue=Sum(F('quantity') * F('price'))
        ).order_by('-total_sold')[:limit]

        product_ids = [item['product_id'] for item in top_products]
        # pylint: disable=no-member
        products = {
            p.id: p for p in product_model.objects.filter(id__in=product_ids)
        }

        result = []
        for item in top_products:
            product = products.get(item['product_id'])
            if product:
                result.append({
                    'id': product.id,
                    'name': product.name,
                    'slug': product.slug,
                    'image': product.image.url if product.image else None,
                    'price': str(product.price),
                    'total_sold': item['total_sold'],
                    'total_revenue': str(item['total_revenue']),
                    'category': product.category.name if product.category else None,
                })

        cache.set(cache_key, result, self.CACHE_TIMEOUT)
        return result

    def get_sales_by_category(self, days: int = 30) -> List[Dict]:
        """
        Get sales breakdown by category.

        Args:
            days: Number of days to look back

        Returns:
            List of category sales data
        """
        cache_key = f'sales_by_category_{days}'
        cached = cache.get(cache_key)
        if cached:
            return cached

        # pylint: disable=invalid-name
        order_item_model = self._get_model('OrderItem')

        start_date = timezone.now() - timedelta(days=days)

        # pylint: disable=no-member
        category_sales = order_item_model.objects.filter(
            order__created_at__gte=start_date,
            order__status__in=['delivered', 'shipped', 'confirmed']
        ).values(
            'product__category__id',
            'product__category__name'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum(F('quantity') * F('price')),
            order_count=Count('order', distinct=True)
        ).order_by('-total_revenue')

        result = [
            {
                'category_id': item['product__category__id'],
                'category_name': item['product__category__name'] or 'Uncategorized',
                'total_quantity': item['total_quantity'],
                'total_revenue': str(item['total_revenue'] or 0),
                'order_count': item['order_count'],
            }
            for item in category_sales
        ]

        cache.set(cache_key, result, self.CACHE_TIMEOUT)
        return result

    def get_product_performance(self, product_id: int) -> Dict:
        """
        Get detailed performance metrics for a product.

        Args:
            product_id: The product ID

        Returns:
            Product performance metrics
        """
        # pylint: disable=invalid-name
        product_model = self._get_model('Product')
        order_item_model = self._get_model('OrderItem')
        review_model = self._get_model('Review')

        try:
            # pylint: disable=no-member
            product = product_model.objects.get(id=product_id)
        except product_model.DoesNotExist:
            return {}

        # Sales data for different periods
        now = timezone.now()
        periods = {
            'today': now - timedelta(days=1),
            'week': now - timedelta(days=7),
            'month': now - timedelta(days=30),
            'year': now - timedelta(days=365),
        }

        sales_data = {}
        for period_name, start_date in periods.items():
            # pylint: disable=no-member
            data = order_item_model.objects.filter(
                product_id=product_id,
                order__created_at__gte=start_date,
                order__status__in=['delivered', 'shipped', 'confirmed']
            ).aggregate(
                total_sold=Sum('quantity'),
                total_revenue=Sum(F('quantity') * F('price'))
            )
            sales_data[period_name] = {
                'quantity': data['total_sold'] or 0,
                'revenue': str(data['total_revenue'] or 0),
            }

        # Review metrics
        # pylint: disable=no-member
        reviews = review_model.objects.filter(product_id=product_id)
        review_count = reviews.count()
        avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0

        rating_distribution = {}
        for rating in range(1, 6):
            rating_distribution[rating] = reviews.filter(rating=rating).count()

        return {
            'product': {
                'id': product.id,
                'name': product.name,
                'price': str(product.price),
                'stock': getattr(product, 'stock', 0),
            },
            'sales': sales_data,
            'reviews': {
                'count': review_count,
                'average_rating': round(avg_rating, 1),
                'distribution': rating_distribution,
            },
        }

    def get_low_stock_products(self, threshold: int = 10) -> List[Dict]:
        """
        Get products with low stock.

        Args:
            threshold: Stock threshold

        Returns:
            List of low stock products
        """
        # pylint: disable=invalid-name
        product_model = self._get_model('Product')

        # pylint: disable=no-member
        low_stock = product_model.objects.filter(
            is_active=True,
            stock__lte=threshold,
            stock__gt=0
        ).order_by('stock')[:50]

        return [
            {
                'id': p.id,
                'name': p.name,
                'slug': p.slug,
                'stock': p.stock,
                'price': str(p.price),
                'category': p.category.name if p.category else None,
            }
            for p in low_stock
        ]

    def get_out_of_stock_products(self) -> List[Dict]:
        """Get products that are out of stock."""
        # pylint: disable=invalid-name
        product_model = self._get_model('Product')

        # pylint: disable=no-member
        out_of_stock = product_model.objects.filter(
            is_active=True,
            stock=0
        ).order_by('-created_at')[:50]

        return [
            {
                'id': p.id,
                'name': p.name,
                'slug': p.slug,
                'category': p.category.name if p.category else None,
                'vendor': p.vendor.name if p.vendor else None,
            }
            for p in out_of_stock
        ]

    def get_revenue_trends(self, days: int = 30) -> List[Dict]:
        """
        Get daily revenue trends.

        Args:
            days: Number of days to look back

        Returns:
            List of daily revenue data
        """
        cache_key = f'revenue_trends_{days}'
        cached = cache.get(cache_key)
        if cached:
            return cached

        # pylint: disable=invalid-name
        order_model = self._get_model('Order')

        start_date = timezone.now() - timedelta(days=days)

        # pylint: disable=no-member
        daily_revenue = order_model.objects.filter(
            created_at__gte=start_date,
            status__in=['delivered', 'shipped', 'confirmed']
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            revenue=Sum('paid_amount'),
            orders=Count('id')
        ).order_by('date')

        result = [
            {
                'date': str(item['date']),
                'revenue': str(item['revenue'] or 0),
                'orders': item['orders'],
            }
            for item in daily_revenue
        ]

        cache.set(cache_key, result, self.CACHE_TIMEOUT)
        return result


class InventoryService:
    """
    Service for inventory management.
    """

    def __init__(self):
        pass

    def _get_model(self, model_name: str):
        """Lazy import to avoid circular imports."""
        # pylint: disable=import-outside-toplevel
        from store.models import Product, InventoryLog
        models_map = {
            'Product': Product,
            'InventoryLog': InventoryLog,
        }
        return models_map.get(model_name)

    def update_stock(
        self,
        product_id: int,
        quantity_change: int,
        reason: str = '',
        user=None
    ) -> bool:
        """
        Update product stock.

        Args:
            product_id: Product ID
            quantity_change: Positive to add, negative to subtract
            reason: Reason for stock change
            user: User making the change

        Returns:
            True if successful
        """
        # pylint: disable=invalid-name
        product_model = self._get_model('Product')
        inventory_log_model = self._get_model('InventoryLog')

        try:
            # pylint: disable=no-member
            product = product_model.objects.select_for_update().get(id=product_id)

            old_stock = product.stock
            new_stock = max(0, old_stock + quantity_change)
            product.stock = new_stock
            product.save(update_fields=['stock'])

            # Log the change
            if inventory_log_model:
                # pylint: disable=no-member
                inventory_log_model.objects.create(
                    product=product,
                    previous_quantity=old_stock,
                    new_quantity=new_stock,
                    change_type='add' if quantity_change > 0 else 'remove',
                    reason=reason,
                    changed_by=user,
                )

            logger.info(
                "Stock updated for product %s: %d -> %d",
                product_id, old_stock, new_stock
            )
            return True

        except product_model.DoesNotExist:
            logger.error("Product %s not found for stock update", product_id)
            return False

    def get_inventory_value(self, category_id: Optional[int] = None) -> Decimal:
        """
        Calculate total inventory value.

        Args:
            category_id: Filter by category

        Returns:
            Total inventory value
        """
        # pylint: disable=invalid-name
        product_model = self._get_model('Product')

        # pylint: disable=no-member
        queryset = product_model.objects.filter(is_active=True, stock__gt=0)

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        total = queryset.aggregate(
            value=Sum(F('stock') * F('price'))
        )['value']

        return total or Decimal('0.00')
