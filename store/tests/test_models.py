"""
Model tests for VIBE E-Commerce.

Comprehensive tests for all store models including validation and business logic.

Note: Snyk may report "Use of Hardcoded Credentials" warnings for test fixture
usernames (e.g., 'profileuser'). These are expected false positives - test
usernames are not security-sensitive. Actual passwords use environment variables
via TEST_USER_PASSWORD constant from test_config.py.
"""
# pylint: disable=no-member
from decimal import Decimal
from datetime import timedelta
from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.utils import timezone
from store.models import (
    Vendor, Category, Product, ProductImage, Order, OrderItem,
    Review, Wishlist, Profile, Coupon, FlashSale, BulkOrder,
    Notification, Deal
)
from store.tests.test_config import TEST_USER_PASSWORD, TEST_PROFILE_USERNAME


class VendorModelTest(TestCase):
    """Test cases for Vendor model."""

    def test_vendor_creation(self):
        """Test creating a vendor."""
        vendor = Vendor.objects.create(
            name='Test Vendor',
            slug='test-vendor',
            city='Mumbai'
        )
        self.assertEqual(str(vendor), 'Test Vendor')
        self.assertEqual(vendor.slug, 'test-vendor')
        self.assertEqual(vendor.city, 'Mumbai')

    def test_vendor_with_user(self):
        """Test vendor associated with a user."""
        user = User.objects.create_user(
            username='vendoruser',
            password=TEST_USER_PASSWORD  # noqa: S106
        )
        vendor = Vendor.objects.create(
            name='User Vendor',
            slug='user-vendor',
            city='Delhi',
            created_by=user
        )
        self.assertEqual(vendor.created_by, user)


class CategoryModelTest(TestCase):
    """Test cases for Category model."""

    def test_category_creation(self):
        """Test creating a category."""
        category = Category.objects.create(
            name='Electronics',
            slug='electronics'
        )
        self.assertEqual(str(category), 'Electronics')
        self.assertEqual(category.slug, 'electronics')

    def test_category_slug_uniqueness(self):
        """Test category slug must be unique."""
        Category.objects.create(name='Category 1', slug='unique-slug')
        with self.assertRaises(IntegrityError):
            Category.objects.create(name='Category 2', slug='unique-slug')


class ProductModelTest(TestCase):
    """Test cases for Product model."""

    def setUp(self):
        """Set up test fixtures."""
        self.vendor = Vendor.objects.create(
            name='Test Vendor',
            slug='test-vendor',
            city='Test City'
        )
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )

    def test_product_creation(self):
        """Test creating a product."""
        product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            price=Decimal('99.99'),
            category=self.category,
            vendor=self.vendor
        )
        self.assertEqual(str(product), 'Test Product')
        self.assertEqual(product.price, Decimal('99.99'))

    def test_product_discount_percentage(self):
        """Test product discount percentage calculation."""
        product = Product.objects.create(
            name='Discounted Product',
            slug='discounted-product',
            price=Decimal('80.00'),
            mrp=Decimal('100.00'),
            category=self.category,
            vendor=self.vendor
        )
        # Discount should be 20%
        self.assertEqual(product.discount_percentage, 20)

    def test_product_no_discount_without_mrp(self):
        """Test product with no MRP has no discount."""
        product = Product.objects.create(
            name='No MRP Product',
            slug='no-mrp-product',
            price=Decimal('50.00'),
            category=self.category,
            vendor=self.vendor
        )
        self.assertEqual(product.discount_percentage, 0)

    def test_product_in_stock(self):
        """Test product stock status."""
        in_stock = Product.objects.create(
            name='In Stock Product',
            slug='in-stock-product',
            price=Decimal('25.00'),
            stock_quantity=10,
            category=self.category,
            vendor=self.vendor
        )
        out_of_stock = Product.objects.create(
            name='Out Of Stock Product',
            slug='out-of-stock-product',
            price=Decimal('25.00'),
            stock_quantity=0,
            category=self.category,
            vendor=self.vendor
        )
        self.assertTrue(in_stock.is_in_stock)
        self.assertFalse(out_of_stock.is_in_stock)

    def test_product_low_stock(self):
        """Test product low stock detection."""
        low_stock = Product.objects.create(
            name='Low Stock Product',
            slug='low-stock-product',
            price=Decimal('25.00'),
            stock_quantity=3,
            low_stock_threshold=5,
            category=self.category,
            vendor=self.vendor
        )
        normal_stock = Product.objects.create(
            name='Normal Stock Product',
            slug='normal-stock-product',
            price=Decimal('25.00'),
            stock_quantity=10,
            low_stock_threshold=5,
            category=self.category,
            vendor=self.vendor
        )
        self.assertTrue(low_stock.is_low_stock)
        self.assertFalse(normal_stock.is_low_stock)


class ProductImageModelTest(TestCase):
    """Test cases for ProductImage model."""

    def setUp(self):
        """Set up test fixtures."""
        self.vendor = Vendor.objects.create(
            name='Test Vendor',
            slug='test-vendor',
            city='Test City'
        )
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            price=Decimal('99.99'),
            category=self.category,
            vendor=self.vendor
        )

    def test_product_image_ordering(self):
        """Test product images are ordered correctly."""
        ProductImage.objects.create(
            product=self.product,
            order=2,
            is_primary=False
        )
        img2 = ProductImage.objects.create(
            product=self.product,
            order=1,
            is_primary=True
        )
        images = list(self.product.images.all())
        # primary images come first, then by order
        self.assertEqual(images[0], img2)


class OrderModelTest(TestCase):
    """Test cases for Order model."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = User.objects.create_user(
            username='testuser',
            password=TEST_USER_PASSWORD  # noqa: S106
        )
        self.vendor = Vendor.objects.create(
            name='Test Vendor',
            slug='test-vendor',
            city='Test City'
        )
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            price=Decimal('50.00'),
            category=self.category,
            vendor=self.vendor
        )

    def test_order_creation(self):
        """Test creating an order."""
        order = Order.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            address='123 Main St',
            zipcode='12345',
            place='Test City',
            phone='1234567890'
        )
        self.assertEqual(order.status, 'pending')
        self.assertFalse(order.paid)

    def test_order_with_items(self):
        """Test order with order items."""
        order = Order.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            address='123 Main St',
            zipcode='12345',
            place='Test City',
            phone='1234567890'
        )
        item = OrderItem.objects.create(
            order=order,
            product=self.product,
            vendor=self.vendor,
            price=Decimal('50.00'),
            quantity=2
        )
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(str(item), f'{item.id}')


class ReviewModelTest(TestCase):
    """Test cases for Review model."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = User.objects.create_user(
            username='reviewer',
            password=TEST_USER_PASSWORD  # noqa: S106
        )
        self.vendor = Vendor.objects.create(
            name='Test Vendor',
            slug='test-vendor',
            city='Test City'
        )
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            price=Decimal('50.00'),
            category=self.category,
            vendor=self.vendor
        )

    def test_review_creation(self):
        """Test creating a review."""
        review = Review.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            title='Great product!',
            comment='Really loved this product.'
        )
        self.assertEqual(review.rating, 5)
        self.assertFalse(review.is_verified_purchase)

    def test_review_unique_per_user_product(self):
        """Test user can only review a product once."""
        Review.objects.create(
            product=self.product,
            user=self.user,
            rating=4,
            title='First review',
            comment='Initial review'
        )
        with self.assertRaises(IntegrityError):
            Review.objects.create(
                product=self.product,
                user=self.user,
                rating=3,
                title='Second review',
                comment='Another review'
            )


class WishlistModelTest(TestCase):
    """Test cases for Wishlist model."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = User.objects.create_user(
            username='wishlistuser',
            password=TEST_USER_PASSWORD  # noqa: S106
        )
        self.vendor = Vendor.objects.create(
            name='Test Vendor',
            slug='test-vendor',
            city='Test City'
        )
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        self.product = Product.objects.create(
            name='Wishlist Product',
            slug='wishlist-product',
            price=Decimal('75.00'),
            category=self.category,
            vendor=self.vendor
        )

    def test_wishlist_creation(self):
        """Test adding product to wishlist."""
        Wishlist.objects.create(
            user=self.user,
            product=self.product
        )
        self.assertIn(self.product, [w.product for w in self.user.wishlist.all()])

    def test_wishlist_unique_constraint(self):
        """Test unique constraint for user-product in wishlist."""
        Wishlist.objects.create(user=self.user, product=self.product)
        with self.assertRaises(IntegrityError):
            Wishlist.objects.create(user=self.user, product=self.product)


class CouponModelTest(TestCase):
    """Test cases for Coupon model."""

    def test_coupon_creation(self):
        """Test creating a coupon."""
        coupon = Coupon.objects.create(
            code='SAVE20',
            discount_type='percent',
            discount_value=Decimal('20.00'),
            valid_from=timezone.now(),
            valid_until=timezone.now() + timedelta(days=30),
            is_active=True
        )
        self.assertEqual(str(coupon), 'SAVE20')

    def test_coupon_is_valid(self):
        """Test coupon validity check."""
        valid_coupon = Coupon.objects.create(
            code='VALID',
            discount_type='fixed',
            discount_value=Decimal('10.00'),
            valid_from=timezone.now() - timedelta(days=1),
            valid_until=timezone.now() + timedelta(days=30),
            is_active=True
        )
        expired_coupon = Coupon.objects.create(
            code='EXPIRED',
            discount_type='fixed',
            discount_value=Decimal('10.00'),
            valid_from=timezone.now() - timedelta(days=60),
            valid_until=timezone.now() - timedelta(days=30),
            is_active=True
        )
        self.assertTrue(valid_coupon.is_valid)
        self.assertFalse(expired_coupon.is_valid)

    def test_coupon_inactive_is_invalid(self):
        """Test inactive coupon is invalid."""
        inactive_coupon = Coupon.objects.create(
            code='INACTIVE',
            discount_type='percent',
            discount_value=Decimal('15.00'),
            valid_from=timezone.now() - timedelta(days=1),
            valid_until=timezone.now() + timedelta(days=30),
            is_active=False
        )
        self.assertFalse(inactive_coupon.is_valid)


class FlashSaleModelTest(TestCase):
    """Test cases for FlashSale model."""

    def setUp(self):
        """Set up test fixtures."""
        self.vendor = Vendor.objects.create(
            name='Test Vendor',
            slug='test-vendor',
            city='Test City'
        )
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        self.product = Product.objects.create(
            name='Flash Sale Product',
            slug='flash-sale-product',
            price=Decimal('100.00'),
            category=self.category,
            vendor=self.vendor
        )

    def test_flash_sale_is_live(self):
        """Test flash sale is_live property."""
        live_sale = FlashSale.objects.create(
            name='Live Sale',
            slug='live-sale',
            discount_percentage=25,
            start_time=timezone.now() - timedelta(hours=1),
            end_time=timezone.now() + timedelta(hours=1),
            is_active=True
        )
        future_sale = FlashSale.objects.create(
            name='Future Sale',
            slug='future-sale',
            discount_percentage=30,
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=2),
            is_active=True
        )
        self.assertTrue(live_sale.is_live)
        self.assertFalse(future_sale.is_live)

    def test_flash_sale_time_remaining(self):
        """Test flash sale time remaining calculation."""
        sale = FlashSale.objects.create(
            name='Timed Sale',
            slug='timed-sale',
            discount_percentage=20,
            start_time=timezone.now() - timedelta(hours=1),
            end_time=timezone.now() + timedelta(hours=2),
            is_active=True
        )
        remaining = sale.time_remaining
        self.assertIsNotNone(remaining)


class ProfileModelTest(TestCase):
    """Test cases for Profile model."""

    def test_profile_creation(self):
        """Test creating a user profile."""
        user = User.objects.create_user(
            username=TEST_PROFILE_USERNAME,
            password=TEST_USER_PASSWORD  # noqa: S106
        )
        # Profile is automatically created by signal, so we get it
        profile, created = Profile.objects.get_or_create(
            user=user,
            defaults={
                'shop_name': 'Test Shop',
                'city': 'Mumbai',
                'credit_limit': Decimal('10000.00')
            }
        )
        # If profile was already created by signal, update it
        if not created:
            profile.shop_name = 'Test Shop'
            profile.city = 'Mumbai'
            profile.credit_limit = Decimal('10000.00')
            profile.save()

        # Check profile was created/retrieved successfully
        self.assertEqual(profile.user.username, 'profileuser')
        self.assertFalse(profile.is_kyc_verified)


class NotificationModelTest(TestCase):
    """Test cases for Notification model."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = User.objects.create_user(
            username='notifyuser',
            password=TEST_USER_PASSWORD  # noqa: S106
        )

    def test_notification_creation(self):
        """Test creating a notification."""
        notification = Notification.objects.create(
            user=self.user,
            notification_type='order',
            title='Order Update',
            message='Your order has been shipped!'
        )
        self.assertFalse(notification.is_read)
        self.assertEqual(notification.priority, 'normal')

    def test_notification_expiry(self):
        """Test notification expiry check."""
        expired = Notification.objects.create(
            user=self.user,
            notification_type='promo',
            title='Expired Promo',
            message='This promo has expired',
            expires_at=timezone.now() - timedelta(days=1)
        )
        valid = Notification.objects.create(
            user=self.user,
            notification_type='promo',
            title='Valid Promo',
            message='This promo is valid',
            expires_at=timezone.now() + timedelta(days=1)
        )
        self.assertTrue(expired.is_expired)
        self.assertFalse(valid.is_expired)


class DealModelTest(TestCase):
    """Test cases for Deal model."""

    def setUp(self):
        """Set up test fixtures."""
        self.vendor = Vendor.objects.create(
            name='Test Vendor',
            slug='test-vendor',
            city='Test City'
        )
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        self.product = Product.objects.create(
            name='Deal Product',
            slug='deal-product',
            price=Decimal('100.00'),
            category=self.category,
            vendor=self.vendor
        )

    def test_deal_is_valid(self):
        """Test deal validity check."""
        valid_deal = Deal.objects.create(
            name='Valid Deal',
            slug='valid-deal',
            deal_type='percentage',
            discount_value=Decimal('10.00'),
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=30),
            is_active=True
        )
        expired_deal = Deal.objects.create(
            name='Expired Deal',
            slug='expired-deal',
            deal_type='fixed',
            discount_value=Decimal('5.00'),
            start_date=timezone.now() - timedelta(days=60),
            end_date=timezone.now() - timedelta(days=30),
            is_active=True
        )
        self.assertTrue(valid_deal.is_valid)
        self.assertFalse(expired_deal.is_valid)

    def test_deal_percentage_discount(self):
        """Test percentage discount calculation."""
        deal = Deal.objects.create(
            name='Percentage Deal',
            slug='percentage-deal',
            deal_type='percentage',
            discount_value=Decimal('20.00'),
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=30),
            is_active=True
        )
        # 20% of 100 = 20
        discount = deal.calculate_discount(Decimal('100.00'))
        self.assertEqual(discount, Decimal('20.00'))

    def test_deal_fixed_discount(self):
        """Test fixed discount calculation."""
        deal = Deal.objects.create(
            name='Fixed Deal',
            slug='fixed-deal',
            deal_type='fixed',
            discount_value=Decimal('15.00'),
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=30),
            is_active=True
        )
        discount = deal.calculate_discount(Decimal('100.00'))
        self.assertEqual(discount, Decimal('15.00'))


class BulkOrderModelTest(TestCase):
    """Test cases for BulkOrder model."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = User.objects.create_user(
            username='bulkuser',
            password=TEST_USER_PASSWORD  # noqa: S106
        )
        self.vendor = Vendor.objects.create(
            name='Test Vendor',
            slug='test-vendor',
            city='Test City'
        )
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        self.product = Product.objects.create(
            name='Bulk Product',
            slug='bulk-product',
            price=Decimal('50.00'),
            category=self.category,
            vendor=self.vendor
        )

    def test_bulk_order_creation(self):
        """Test creating a bulk order."""
        bulk_order = BulkOrder.objects.create(
            user=self.user,
            product=self.product,
            vendor=self.vendor,
            quantity=100,
            requested_price=Decimal('45.00')
        )
        self.assertEqual(bulk_order.status, 'pending')
        self.assertEqual(bulk_order.quantity, 100)

    def test_bulk_order_total_value(self):
        """Test bulk order total value calculation."""
        bulk_order = BulkOrder.objects.create(
            user=self.user,
            product=self.product,
            vendor=self.vendor,
            quantity=50,
            requested_price=Decimal('40.00'),
            approved_price=Decimal('42.00')
        )
        # Total = 50 * 42 = 2100 (total_value is a property)
        self.assertEqual(bulk_order.total_value, Decimal('2100.00'))
