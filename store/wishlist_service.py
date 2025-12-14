"""
Wishlist Service for VIBE E-Commerce
Handles wishlist operations including add, remove, and price drop monitoring.
"""
import logging
from typing import Dict, List, Optional

from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


class WishlistService:
    """
    Service for managing user wishlists.
    """

    def __init__(self, user: User):
        self.user = user

    def _get_model(self, model_name: str):
        """Lazy import to avoid circular imports."""
        # pylint: disable=import-outside-toplevel
        from store.models import Wishlist, Product
        models_map = {
            'Wishlist': Wishlist,
            'Product': Product,
        }
        return models_map.get(model_name)

    def add_to_wishlist(self, product_id: int) -> Dict:
        """
        Add a product to the user's wishlist.

        Args:
            product_id: Product ID to add

        Returns:
            Dictionary with status and message
        """
        # pylint: disable=invalid-name
        wishlist_model = self._get_model('Wishlist')
        product_model = self._get_model('Product')

        try:
            # pylint: disable=no-member
            product = product_model.objects.get(id=product_id, is_active=True)

            # Check if already in wishlist
            # pylint: disable=no-member
            existing = wishlist_model.objects.filter(
                user=self.user,
                product=product
            ).first()

            if existing:
                return {
                    'success': False,
                    'message': 'Product already in wishlist',
                    'wishlist_id': existing.id,
                }

            # Add to wishlist with current price for price drop tracking
            # pylint: disable=no-member
            wishlist_item = wishlist_model.objects.create(
                user=self.user,
                product=product,
                price_when_added=product.price,
            )

            logger.info(
                "Product %s added to wishlist for user %s",
                product_id, self.user.id
            )

            return {
                'success': True,
                'message': 'Added to wishlist',
                'wishlist_id': wishlist_item.id,
            }

        except product_model.DoesNotExist:
            return {
                'success': False,
                'message': 'Product not found',
            }

    def remove_from_wishlist(self, product_id: int) -> Dict:
        """
        Remove a product from the user's wishlist.

        Args:
            product_id: Product ID to remove

        Returns:
            Dictionary with status and message
        """
        # pylint: disable=invalid-name
        wishlist_model = self._get_model('Wishlist')

        # pylint: disable=no-member
        deleted, _ = wishlist_model.objects.filter(
            user=self.user,
            product_id=product_id
        ).delete()

        if deleted:
            logger.info(
                "Product %s removed from wishlist for user %s",
                product_id, self.user.id
            )
            return {
                'success': True,
                'message': 'Removed from wishlist',
            }

        return {
            'success': False,
            'message': 'Product not in wishlist',
        }

    def get_wishlist(self, include_details: bool = True) -> List[Dict]:
        """
        Get the user's wishlist.

        Args:
            include_details: Whether to include product details

        Returns:
            List of wishlist items
        """
        # pylint: disable=invalid-name
        wishlist_model = self._get_model('Wishlist')

        # pylint: disable=no-member
        items = wishlist_model.objects.filter(user=self.user).select_related(
            'product', 'product__category', 'product__vendor'
        ).order_by('-created_at')

        result = []
        for item in items:
            product = item.product
            price_drop = self._calculate_price_drop(item)

            item_data = {
                'id': item.id,
                'product_id': product.id,
                'added_at': item.created_at.isoformat(),
            }

            if include_details:
                item_data.update({
                    'name': product.name,
                    'slug': product.slug,
                    'price': str(product.price),
                    'original_price': str(product.original_price) if hasattr(product, 'original_price') and product.original_price else str(product.price),
                    'image': product.image.url if product.image else None,
                    'category': product.category.name if product.category else None,
                    'in_stock': product.stock > 0 if hasattr(product, 'stock') else True,
                    'price_when_added': str(item.price_when_added) if hasattr(item, 'price_when_added') and item.price_when_added else str(product.price),
                    'price_drop': price_drop,
                })

            result.append(item_data)

        return result

    def _calculate_price_drop(self, wishlist_item) -> Optional[Dict]:
        """Calculate price drop information."""
        if not hasattr(wishlist_item, 'price_when_added') or not wishlist_item.price_when_added:
            return None

        product = wishlist_item.product
        original_price = wishlist_item.price_when_added
        current_price = product.price

        if current_price < original_price:
            drop_amount = original_price - current_price
            drop_percentage = (drop_amount / original_price) * 100

            return {
                'original_price': str(original_price),
                'current_price': str(current_price),
                'drop_amount': str(drop_amount),
                'drop_percentage': round(float(drop_percentage), 1),
            }

        return None

    def is_in_wishlist(self, product_id: int) -> bool:
        """Check if a product is in the user's wishlist."""
        # pylint: disable=invalid-name
        wishlist_model = self._get_model('Wishlist')

        # pylint: disable=no-member
        return wishlist_model.objects.filter(
            user=self.user,
            product_id=product_id
        ).exists()

    def get_wishlist_count(self) -> int:
        """Get the number of items in the wishlist."""
        # pylint: disable=invalid-name
        wishlist_model = self._get_model('Wishlist')

        # pylint: disable=no-member
        return wishlist_model.objects.filter(user=self.user).count()

    def get_price_drops(self) -> List[Dict]:
        """Get wishlist items with price drops."""
        wishlist = self.get_wishlist(include_details=True)
        return [
            item for item in wishlist
            if item.get('price_drop') is not None
        ]

    def move_to_cart(self, product_id: int, quantity: int = 1) -> Dict:
        """
        Move a wishlist item to cart.

        Args:
            product_id: Product ID
            quantity: Quantity to add to cart

        Returns:
            Dictionary with status
        """
        # pylint: disable=import-outside-toplevel
        from store.cart_service import CartService

        # Remove from wishlist
        self.remove_from_wishlist(product_id)

        # Add to cart
        cart_service = CartService(self.user)
        result = cart_service.add_item(product_id, quantity)

        return result

    def clear_wishlist(self) -> Dict:
        """Clear all items from the wishlist."""
        # pylint: disable=invalid-name
        wishlist_model = self._get_model('Wishlist')

        # pylint: disable=no-member
        deleted, _ = wishlist_model.objects.filter(user=self.user).delete()

        return {
            'success': True,
            'message': f'Cleared {deleted} items from wishlist',
            'deleted_count': deleted,
        }
