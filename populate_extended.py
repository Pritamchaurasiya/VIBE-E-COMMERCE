"""
Extended data population script for VIBE E-Commerce.

This module adds sample data for testing and development purposes:
- Users with profiles
- Orders with order items
- Product reviews
- Wishlists
- Discount coupons
- Flash sales
- Notifications
- Contact inquiries
- Newsletter subscriptions

Security Note:
    This script is for DEVELOPMENT/TESTING purposes only.
    It creates sample data with test credentials that should never be used in production.
    Uses standard random module (not cryptographically secure) which is intentional
    for deterministic, reproducible test data generation.

Usage:
    python populate_extended.py

Author: VIBE E-Commerce Team
"""
import logging
import os
import sys
from dataclasses import dataclass, field
from datetime import timedelta
from typing import List, Tuple

# nosemgrep: python.lang.security.insecure-random-use
# trunk-ignore-all(bandit/B311): Intentional use for non-security test data seeding
import random  # nosec B311 # noqa: S311

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# pylint: disable=wrong-import-position
from django.contrib.auth.models import User  # noqa: E402
from django.db import IntegrityError, transaction  # noqa: E402
from django.utils import timezone  # noqa: E402
from store.models import (  # noqa: E402
    Product, Order, OrderItem, Review, Wishlist, Coupon,
    FlashSale, Contact, Notification, NewsletterSubscription
)
# pylint: enable=wrong-import-position

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Development-only test password - NOT for production use
# nosec B105 - This is intentional for test data seeding
TEST_USER_PASSWORD = os.environ.get('TEST_USER_PASSWORD', 'User@123!')  # noqa: S105


@dataclass
class PopulationStats:
    """Statistics for data population."""
    users_created: int = 0
    orders_created: int = 0
    reviews_created: int = 0
    wishlists_created: int = 0
    coupons_created: int = 0
    flash_sales_created: int = 0
    notifications_created: int = 0
    contacts_created: int = 0
    newsletters_created: int = 0
    errors: List[str] = field(default_factory=list)


# Sample data constants
FIRST_NAMES: Tuple[str, ...] = (
    'Rahul', 'Priya', 'Amit', 'Neha', 'Vikram', 'Anjali', 'Suresh', 'Kavita',
    'Rajesh', 'Sunita', 'Deepak', 'Meera', 'Arun', 'Pooja', 'Sanjay', 'Rekha',
    'Manish', 'Divya', 'Ashok', 'Anita', 'Vikas', 'Shweta', 'Ravi', 'Geeta',
    'Manoj', 'Sapna', 'Nitin', 'Jyoti', 'Rakesh', 'Seema'
)

LAST_NAMES: Tuple[str, ...] = (
    'Sharma', 'Verma', 'Patel', 'Singh', 'Kumar', 'Gupta', 'Joshi', 'Yadav',
    'Mishra', 'Reddy', 'Nair', 'Iyer', 'Menon', 'Pillai', 'Rao', 'Desai',
    'Shah', 'Mehta', 'Thakur', 'Chauhan', 'Dubey', 'Pandey', 'Tiwari', 'Saxena'
)

CITIES: Tuple[str, ...] = (
    'Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Hyderabad', 'Kolkata',
    'Pune', 'Ahmedabad', 'Jaipur', 'Lucknow', 'Nagpur', 'Indore',
    'Bhopal', 'Chandigarh', 'Patna', 'Varanasi', 'Surat', 'Vadodara'
)

STATES: Tuple[str, ...] = (
    'Maharashtra', 'Delhi', 'Karnataka', 'Tamil Nadu', 'Telangana', 'West Bengal',
    'Gujarat', 'Rajasthan', 'Uttar Pradesh', 'Madhya Pradesh', 'Punjab', 'Bihar'
)

REVIEW_TEXTS: Tuple[str, ...] = (
    "Excellent quality product! Highly recommended for farmers.",
    "Good value for money. Worked as expected on my crops.",
    "Fast delivery and genuine product. Will buy again.",
    "Best pesticide I've used. My crop yield increased significantly.",
    "Authentic product from trusted brand. Very satisfied.",
    "Great for controlling pests. Easy to apply.",
    "Effective against diseases. Saved my tomato crop.",
    "Affordable and effective. Must-have for every farmer.",
    "Quality is top-notch. Results visible within days.",
    "Trusted brand, reliable results. Using it for years.",
    "Very effective fungicide. Controlled powdery mildew completely.",
    "Good packaging, product was intact. Works great.",
    "Exactly as described. My wheat crop looks healthy now.",
    "Recommended by my agriculture officer. Works perfectly.",
    "Premium quality seeds. Germination rate was 95%+.",
)

ORDER_STATUSES: Tuple[str, ...] = (
    'pending', 'processing', 'shipped', 'delivered', 'cancelled'
)

PAYMENT_METHODS: Tuple[str, ...] = ('COD', 'UPI', 'Card', 'NetBanking')


def generate_phone_number() -> str:
    """Generate a random Indian phone number."""
    return f"+91{random.randint(7000000000, 9999999999)}"  # noqa: S311


def generate_pincode() -> str:
    """Generate a random Indian pincode."""
    return str(random.randint(110001, 999999))  # noqa: S311


def generate_address(city: str) -> str:
    """Generate a random address."""
    return f"{random.randint(1, 500)}, Main Road, {city}"  # noqa: S311


def create_users(stats: PopulationStats, count: int = 25) -> List[User]:
    """
    Create sample users with profiles.

    Args:
        stats: PopulationStats object to track creation
        count: Number of users to create

    Returns:
        List of created User objects
    """
    logger.info("Creating %d sample users...", count)
    users: List[User] = []

    for _ in range(count):
        first = random.choice(FIRST_NAMES)  # noqa: S311
        last = random.choice(LAST_NAMES)  # noqa: S311
        username = f"{first.lower()}{last.lower()}{random.randint(100, 999)}"  # noqa: S311
        email = f"{username}@example.com"

        # Check if user exists
        if User.objects.filter(username=username).exists():
            continue

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=TEST_USER_PASSWORD,
                    first_name=first,
                    last_name=last
                )

                # Update profile if it exists
                if hasattr(user, 'profile'):
                    profile = user.profile
                    profile.phone = generate_phone_number()
                    profile.city = random.choice(CITIES)  # noqa: S311
                    profile.state = random.choice(STATES)  # noqa: S311
                    profile.address = generate_address(profile.city)
                    profile.pincode = generate_pincode()
                    profile.save()

                users.append(user)
                stats.users_created += 1
                logger.debug("Created user: %s %s (%s)", first, last, username)

        except IntegrityError as e:
            logger.warning("Could not create user %s: %s", username, e)
            stats.errors.append(f"User {username}: {str(e)[:50]}")
        except AttributeError:
            # Profile might not be auto-created if signal is missing
            logger.warning("Profile not created for %s", username)
            users.append(user)
            stats.users_created += 1

    logger.info("Created %d users", stats.users_created)
    return users


def create_orders(users: List[User], stats: PopulationStats) -> None:
    """
    Create sample orders for users.

    Args:
        users: List of User objects to create orders for
        stats: PopulationStats object to track creation
    """
    logger.info("Creating sample orders...")

    products = list(Product.objects.filter(is_active=True))  # pylint: disable=no-member

    if not products:
        logger.warning("No products found. Skipping orders.")
        return

    user_subset = users[:min(20, len(users))]

    for user in user_subset:
        num_orders = random.randint(1, 5)  # noqa: S311

        for _ in range(num_orders):
            try:
                with transaction.atomic():
                    # Random date in last 60 days
                    days_ago = random.randint(0, 60)  # noqa: S311
                    order_date = timezone.now() - timedelta(days=days_ago)

                    # Random products for order
                    num_items = random.randint(1, 4)  # noqa: S311
                    order_products = random.sample(
                        products, min(num_items, len(products))
                    )  # noqa: S311

                    # Calculate total
                    total = sum(p.price for p in order_products)
                    status = random.choice(ORDER_STATUSES)  # noqa: S311
                    city = random.choice(CITIES)  # noqa: S311

                    order = Order.objects.create(  # pylint: disable=no-member
                        user=user,
                        first_name=user.first_name,
                        last_name=user.last_name,
                        email=user.email,
                        phone=generate_phone_number(),
                        address=generate_address(city),
                        place=city,
                        zipcode=generate_pincode(),
                        paid_amount=total,
                        status=status,
                        payment_method=random.choice(PAYMENT_METHODS),  # noqa: S311
                        paid=status in ('shipped', 'delivered'),
                    )
                    order.created_at = order_date
                    order.save(update_fields=['created_at'])

                    # Create order items
                    for prod in order_products:
                        qty = random.randint(1, 3)  # noqa: S311
                        OrderItem.objects.create(  # pylint: disable=no-member
                            order=order,
                            product=prod,
                            vendor=prod.vendor,
                            price=prod.price,
                            quantity=qty
                        )

                    stats.orders_created += 1

            except IntegrityError as e:
                logger.warning("Could not create order for %s: %s", user.username, e)
                stats.errors.append(f"Order for {user.username}: {str(e)[:50]}")

    logger.info("Created %d orders with items", stats.orders_created)


def create_reviews(users: List[User], stats: PopulationStats) -> None:
    """
    Create sample product reviews.

    Args:
        users: List of User objects to create reviews for
        stats: PopulationStats object to track creation
    """
    logger.info("Creating product reviews...")

    products = list(Product.objects.filter(is_active=True))  # pylint: disable=no-member

    if not products:
        logger.warning("No products found. Skipping reviews.")
        return

    user_subset = users[:min(15, len(users))]

    for user in user_subset:
        num_reviews = random.randint(2, 6)  # noqa: S311
        reviewed_products = random.sample(
            products, min(num_reviews, len(products))
        )  # noqa: S311

        for prod in reviewed_products:
            # Check if review exists
            if Review.objects.filter(product=prod, user=user).exists():  # pylint: disable=no-member
                continue

            try:
                rating = random.choices([5, 4, 3], weights=[50, 35, 15])[0]  # noqa: S311

                title = {5: 'Excellent Product', 4: 'Good Product', 3: 'Average Product'}[rating]

                Review.objects.create(  # pylint: disable=no-member
                    product=prod,
                    user=user,
                    rating=rating,
                    title=title,
                    comment=random.choice(REVIEW_TEXTS),  # noqa: S311
                    is_verified_purchase=random.choice([True, True, False])  # noqa: S311
                )
                stats.reviews_created += 1

            except IntegrityError as e:
                logger.warning("Could not create review: %s", e)
                stats.errors.append(f"Review: {str(e)[:50]}")

    logger.info("Created %d reviews", stats.reviews_created)


def create_wishlists(users: List[User], stats: PopulationStats) -> None:
    """
    Create sample wishlists for users.

    Args:
        users: List of User objects to create wishlists for
        stats: PopulationStats object to track creation
    """
    logger.info("Creating wishlists...")

    products = list(Product.objects.filter(is_active=True))  # pylint: disable=no-member

    if not products:
        logger.warning("No products found. Skipping wishlists.")
        return

    user_subset = users[:min(12, len(users))]

    for user in user_subset:
        num_items = random.randint(3, 8)  # noqa: S311
        wishlist_products = random.sample(
            products, min(num_items, len(products))
        )  # noqa: S311

        for prod in wishlist_products:
            if not Wishlist.objects.filter(user=user, product=prod).exists():  # pylint: disable=no-member
                try:
                    Wishlist.objects.create(user=user, product=prod)  # pylint: disable=no-member
                    stats.wishlists_created += 1
                except IntegrityError:
                    pass  # Already exists

    logger.info("Created %d wishlist items", stats.wishlists_created)


def create_coupons(stats: PopulationStats) -> None:
    """
    Create sample discount coupons.

    Args:
        stats: PopulationStats object to track creation
    """
    logger.info("Creating coupons...")

    coupons_data = [
        ('WELCOME10', 10, 'percentage', 1000),
        ('FLAT200', 200, 'fixed', 2000),
        ('MEGA25', 25, 'percentage', 3000),
        ('AGRI15', 15, 'percentage', 1500),
        ('MONSOON20', 20, 'percentage', 2500),
        ('KISAN50', 50, 'fixed', 500),
        ('FESTIVAL30', 30, 'percentage', 5000),
        ('FIRSTORDER', 15, 'percentage', 1000),
        ('BULK100', 100, 'fixed', 10000),
        ('SEED10', 10, 'percentage', 800),
    ]

    for code, discount_val, disc_type, min_val in coupons_data:
        if not Coupon.objects.filter(code=code).exists():  # pylint: disable=no-member
            try:
                Coupon.objects.create(  # pylint: disable=no-member
                    code=code,
                    discount_value=discount_val,
                    discount_type=disc_type,
                    min_order_value=min_val,
                    max_uses=100,
                    is_active=True,
                    valid_from=timezone.now() - timedelta(days=30),
                    valid_until=timezone.now() + timedelta(days=90),
                )
                stats.coupons_created += 1
            except IntegrityError as e:
                logger.warning("Could not create coupon %s: %s", code, e)

    logger.info("Created %d coupons", stats.coupons_created)


def create_flash_sales(stats: PopulationStats) -> None:
    """
    Create sample flash sales.

    Args:
        stats: PopulationStats object to track creation
    """
    logger.info("Creating flash sales...")

    products = list(Product.objects.filter(is_active=True)[:30])  # pylint: disable=no-member

    if not products:
        logger.warning("No products found. Skipping flash sales.")
        return

    flash_sales_data = [
        ('mega-monsoon-sale', 'Mega Monsoon Sale', 30, 0, 24),
        ('weekend-special', 'Weekend Special Offers', 25, 24, 72),
        ('clearance-sale', 'Year End Clearance', 40, 72, 168),
        ('festival-bonanza', 'Festival Bonanza', 35, 168, 336),
    ]

    for slug, title, discount, start_hours, end_hours in flash_sales_data:
        if not FlashSale.objects.filter(slug=slug).exists():  # pylint: disable=no-member
            try:
                flash = FlashSale.objects.create(  # pylint: disable=no-member
                    name=title,
                    slug=slug,
                    description=f"Get up to {discount}% off on selected products!",
                    discount_percentage=discount,
                    start_time=timezone.now() + timedelta(hours=start_hours),
                    end_time=timezone.now() + timedelta(hours=end_hours),
                    is_active=True
                )
                # Add random products
                flash.products.add(*random.sample(products, min(10, len(products))))  # noqa: S311
                stats.flash_sales_created += 1
            except IntegrityError as e:
                logger.warning("Could not create flash sale %s: %s", slug, e)

    logger.info("Created %d flash sales", stats.flash_sales_created)


def create_notifications(users: List[User], stats: PopulationStats) -> None:
    """
    Create sample notifications for users.

    Args:
        users: List of User objects to create notifications for
        stats: PopulationStats object to track creation
    """
    logger.info("Creating notifications...")

    notification_templates = [
        ("🎉 Welcome!", "Welcome to VIBE E-Commerce! Start shopping now.", "info"),
        ("📦 Order Shipped", "Your order has been shipped and is on the way.", "success"),
        ("⚡ Flash Sale Live!", "Don't miss out on our mega flash sale - up to 40% off!", "warning"),
        ("💰 Coupon Alert", "Use code WELCOME10 for 10% off on your first order.", "info"),
        ("🌟 New Arrival", "Check out our latest collection of premium seeds.", "info"),
        ("🚀 Limited Offer", "Hurry! Stock is running low on your wishlist items.", "warning"),
    ]

    user_subset = users[:min(15, len(users))]

    for user in user_subset:
        num_notifs = random.randint(2, 5)  # noqa: S311
        for _ in range(num_notifs):
            title, msg, ntype = random.choice(notification_templates)  # noqa: S311
            try:
                Notification.objects.create(  # pylint: disable=no-member
                    user=user,
                    title=title,
                    message=msg,
                    notification_type=ntype,
                    is_read=random.choice([True, False, False])  # noqa: S311
                )
                stats.notifications_created += 1
            except IntegrityError:
                pass

    logger.info("Created %d notifications", stats.notifications_created)


def create_contacts(stats: PopulationStats, count: int = 15) -> None:
    """
    Create sample contact inquiries.

    Args:
        stats: PopulationStats object to track creation
        count: Number of contacts to create
    """
    logger.info("Creating contact inquiries...")

    topics = [
        "Product inquiry about pesticides",
        "Bulk order request",
        "Delivery issue",
        "Payment problem",
        "Return request",
        "Partnership opportunity",
        "Feedback on recent purchase",
        "Technical assistance needed",
    ]

    for _ in range(count):
        first = random.choice(FIRST_NAMES)  # noqa: S311
        last = random.choice(LAST_NAMES)  # noqa: S311
        topic = random.choice(topics)  # noqa: S311

        try:
            Contact.objects.create(  # pylint: disable=no-member
                name=f"{first} {last}",
                email=f"{first.lower()}.{last.lower()}@example.com",
                message=(
                    f"Subject: {topic}\n\n"
                    f"I would like to inquire about {topic.lower()}. "
                    "Please get back to me at your earliest convenience. "
                    "Thank you for your assistance."
                )
            )
            stats.contacts_created += 1
        except IntegrityError:
            pass

    logger.info("Created %d contact inquiries", stats.contacts_created)


def create_newsletter_subscriptions(stats: PopulationStats, count: int = 30) -> None:
    """
    Create sample newsletter subscriptions.

    Args:
        stats: PopulationStats object to track creation
        count: Number of subscriptions to create
    """
    logger.info("Creating newsletter subscriptions...")

    for _ in range(count):
        first = random.choice(FIRST_NAMES)  # noqa: S311
        last = random.choice(LAST_NAMES)  # noqa: S311
        email = f"{first.lower()}.{last.lower()}{random.randint(1, 99)}@example.com"  # noqa: S311

        if not NewsletterSubscription.objects.filter(email=email).exists():  # pylint: disable=no-member
            try:
                NewsletterSubscription.objects.create(  # pylint: disable=no-member
                    email=email,
                    is_active=True
                )
                stats.newsletters_created += 1
            except IntegrityError:
                pass

    logger.info("Created %d newsletter subscriptions", stats.newsletters_created)


def update_product_stats() -> int:
    """
    Update product statistics like view counts and ratings.

    Returns:
        Number of products updated
    """
    logger.info("Updating product statistics...")

    products = Product.objects.filter(is_active=True)  # pylint: disable=no-member
    count = 0

    for prod in products:
        try:
            prod.view_count = random.randint(50, 5000)  # noqa: S311
            prod.trending_score = random.randint(0, 100)  # noqa: S311
            prod.save(update_fields=['view_count', 'trending_score'])
            count += 1
        except IntegrityError as e:
            logger.warning("Could not update product %s: %s", prod.id, e)

    logger.info("Updated stats for %d products", count)
    return count


def print_summary(stats: PopulationStats) -> None:
    """Print population summary."""
    print("\n" + "=" * 60)
    print("Extended Data Population Complete!")
    print("=" * 60)

    print("\nCREATED:")
    print(f"  - Users: {stats.users_created}")
    print(f"  - Orders: {stats.orders_created}")
    print(f"  - Reviews: {stats.reviews_created}")
    print(f"  - Wishlists: {stats.wishlists_created}")
    print(f"  - Coupons: {stats.coupons_created}")
    print(f"  - Flash Sales: {stats.flash_sales_created}")
    print(f"  - Notifications: {stats.notifications_created}")
    print(f"  - Contacts: {stats.contacts_created}")
    print(f"  - Newsletter Subs: {stats.newsletters_created}")

    if stats.errors:
        print(f"\nERRORS ({len(stats.errors)}):")
        for error in stats.errors[:10]:  # Show first 10 errors
            print(f"  - {error}")
        if len(stats.errors) > 10:
            print(f"  ... and {len(stats.errors) - 10} more")

    print("\nFINAL DATABASE TOTALS:")
    print(f"  - Users: {User.objects.count()}")
    print(f"  - Products: {Product.objects.count()}")  # pylint: disable=no-member
    print(f"  - Orders: {Order.objects.count()}")  # pylint: disable=no-member
    print(f"  - Reviews: {Review.objects.count()}")  # pylint: disable=no-member
    print(f"  - Wishlists: {Wishlist.objects.count()}")  # pylint: disable=no-member
    print(f"  - Coupons: {Coupon.objects.count()}")  # pylint: disable=no-member
    print(f"  - Flash Sales: {FlashSale.objects.count()}")  # pylint: disable=no-member
    print(f"  - Notifications: {Notification.objects.count()}")  # pylint: disable=no-member
    print(f"  - Contacts: {Contact.objects.count()}")  # pylint: disable=no-member
    print(f"  - Newsletter Subs: {NewsletterSubscription.objects.count()}")  # pylint: disable=no-member


def main() -> int:
    """
    Main function to populate extended data.

    Returns:
        Exit code (0 for success, 1 for errors)
    """
    print("=" * 60)
    print("VIBE E-Commerce - Extended Data Population")
    print("=" * 60)

    stats = PopulationStats()

    # Create users first
    users = create_users(stats)

    # If no new users created, get existing ones
    if not users:
        users = list(User.objects.exclude(is_superuser=True)[:25])
        logger.info("Using %d existing users", len(users))

    if not users:
        logger.error("No users available. Cannot populate data.")
        return 1

    # Create related data
    create_orders(users, stats)
    create_reviews(users, stats)
    create_wishlists(users, stats)
    create_coupons(stats)
    create_flash_sales(stats)
    create_notifications(users, stats)
    create_contacts(stats)
    create_newsletter_subscriptions(stats)
    update_product_stats()

    # Print summary
    print_summary(stats)

    return 1 if stats.errors else 0


if __name__ == '__main__':
    sys.exit(main())
