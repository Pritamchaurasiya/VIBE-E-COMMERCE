"""
PostgreSQL Database Enhancements for VIBE E-Commerce.
Fixed version with correct model fields.

Note: This script uses the standard `random` module for generating test data.
This is intentional as security-grade randomness is not required for sample data.
"""
import os
# trunk-ignore-all(bandit/B311): Intentional use for non-security test data seeding
import random  # nosec B311
from datetime import timedelta

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# pylint: disable=wrong-import-position
from django.contrib.auth.models import User  # noqa: E402
from django.utils import timezone  # noqa: E402
from django.db import connection  # noqa: E402
from store.models import (  # noqa: E402
    Product, Vendor, Category, Order, OrderItem,
    InventoryLog, PremiumListing, Subscription,
    ProductComparison, LocationPopularity, Deal,
    ProductImage, Profile,
)
# pylint: enable=wrong-import-position


def create_inventory_logs():
    """Create inventory log entries for products."""
    print("Creating Inventory Logs...")
    products = list(Product.objects.all()[:50])  # pylint: disable=no-member
    count = 0

    actions = ['restock', 'sale', 'adjustment', 'return', 'purchase']

    for prod in products:
        num_logs = random.randint(3, 10)

        for _ in range(num_logs):
            action = random.choice(actions)
            quantity = random.randint(1, 50)

            if action in ['sale']:
                quantity = -quantity

            InventoryLog.objects.create(  # pylint: disable=no-member
                product=prod,
                action=action,
                quantity=quantity,
                previous_stock=prod.stock_quantity,
                new_stock=prod.stock_quantity + quantity,
                reference=f"REF-{random.randint(10000, 99999)}",
                notes=f"{action.title()} operation"
            )
            count += 1

    print(f"  Created {count} inventory logs")


def create_premium_listings():
    """Create premium/featured listings for products."""
    print("\nCreating Premium Listings...")
    products = list(Product.objects.all()[:30])  # pylint: disable=no-member
    vendors = list(Vendor.objects.all())  # pylint: disable=no-member
    count = 0

    positions = ['home_featured', 'category_top', 'search_sponsored', 'sidebar']

    for prod in random.sample(products, 20):
        start_date = timezone.now() - timedelta(days=random.randint(0, 10))
        end_date = start_date + timedelta(days=random.randint(7, 30))

        PremiumListing.objects.create(  # pylint: disable=no-member
            product=prod,
            vendor=prod.vendor or random.choice(vendors),
            position=random.choice(positions),
            start_date=start_date,
            end_date=end_date,
            amount_paid=random.randint(500, 5000),
            is_active=True,
            impressions=random.randint(100, 10000),
            clicks=random.randint(10, 1000)
        )
        count += 1

    print(f"  Created {count} premium listings")


def create_subscriptions():
    """Create user subscriptions."""
    print("\nCreating User Subscriptions...")
    users = list(User.objects.exclude(is_superuser=True)[:30])
    products = list(Product.objects.all()[:20])  # pylint: disable=no-member
    vendors = list(Vendor.objects.all())  # pylint: disable=no-member
    categories = list(Category.objects.all())  # pylint: disable=no-member
    count = 0

    sub_types = ['price_alert', 'stock_alert', 'new_product', 'newsletter']
    frequencies = ['instant', 'daily', 'weekly']

    for user in users:
        num_subs = random.randint(1, 3)

        for _ in range(num_subs):
            sub_type = random.choice(sub_types)

            Subscription.objects.create(  # pylint: disable=no-member
                user=user,
                subscription_type=sub_type,
                product=random.choice(products) if sub_type == 'price_alert' else None,
                vendor=(random.choice(vendors)
                        if sub_type == 'new_product' and vendors else None),
                category=(random.choice(categories)
                          if sub_type == 'new_product' and categories else None),
                is_active=True,
                frequency=random.choice(frequencies)
            )
            count += 1

    print(f"  Created {count} subscriptions")


def create_product_comparisons():
    """Create product comparison records."""
    print("\nCreating Product Comparisons...")
    users = list(User.objects.exclude(is_superuser=True)[:30])
    products = list(Product.objects.all()[:50])  # pylint: disable=no-member
    count = 0

    for user in users:
        if ProductComparison.objects.filter(user=user).exists():  # pylint: disable=no-member
            continue

        num_products = random.randint(2, 4)
        compare_products = random.sample(products, num_products)

        comparison = ProductComparison.objects.create(  # pylint: disable=no-member
            user=user,
            session_id=f"session_{random.randint(10000, 99999)}"
        )
        comparison.products.set(compare_products)
        count += 1

    print(f"  Created {count} product comparisons")


def create_location_popularity():
    """Create location-based popularity data."""
    print("\nCreating Location Popularity...")
    products = list(Product.objects.all()[:40])  # pylint: disable=no-member

    cities = [
        ('Mumbai', 'Mumbai', 'Maharashtra'),
        ('Delhi', 'Central Delhi', 'Delhi'),
        ('Bangalore', 'Bangalore Urban', 'Karnataka'),
        ('Chennai', 'Chennai', 'Tamil Nadu'),
        ('Hyderabad', 'Hyderabad', 'Telangana'),
        ('Kolkata', 'Kolkata', 'West Bengal'),
        ('Pune', 'Pune', 'Maharashtra'),
        ('Ahmedabad', 'Ahmedabad', 'Gujarat'),
    ]

    count = 0
    for city, district, state in cities:
        city_products = random.sample(products, min(15, len(products)))

        for prod in city_products:
            exists = LocationPopularity.objects.filter(  # pylint: disable=no-member
                product=prod, city=city
            ).exists()
            if exists:
                continue

            LocationPopularity.objects.create(  # pylint: disable=no-member
                product=prod,
                city=city,
                district=district,
                state=state,
                view_count=random.randint(500, 10000),
                cart_add_count=random.randint(50, 500),
                purchase_count=random.randint(10, 200),
                popularity_score=random.randint(50, 100)
            )
            count += 1

    print(f"  Created {count} location popularity records")


def create_deals():
    """Create deals/offers."""
    print("\nCreating Deals...")
    products = list(Product.objects.all()[:30])  # pylint: disable=no-member
    categories = list(Category.objects.all())  # pylint: disable=no-member
    vendors = list(Vendor.objects.all())  # pylint: disable=no-member
    count = 0

    deals_data = [
        ("Monsoon Mega Sale", 25, 'percentage'),
        ("Festive Bonanza", 30, 'percentage'),
        ("Weekly Steals", 500, 'fixed'),
        ("Clearance Sale", 40, 'percentage'),
        ("New Customer Offer", 200, 'fixed'),
        ("Bulk Buy Discount", 35, 'percentage'),
    ]

    for name, discount, deal_type in deals_data:
        slug = name.lower().replace(' ', '-')
        if Deal.objects.filter(slug=slug).exists():  # pylint: disable=no-member
            continue

        start = timezone.now() - timedelta(days=random.randint(0, 5))

        deal = Deal.objects.create(  # pylint: disable=no-member
            name=name,
            slug=slug,
            description=f"Get amazing discounts with {name}!",
            deal_type=deal_type,
            discount_value=discount,
            min_purchase=random.randint(500, 2000),
            max_discount=random.randint(1000, 5000) if deal_type == 'percentage' else None,
            start_date=start,
            end_date=start + timedelta(days=random.randint(7, 30)),
            is_active=True,
            usage_limit=random.randint(100, 1000),
            priority=random.randint(1, 10)
        )

        deal.products.set(random.sample(products, min(10, len(products))))
        if categories:
            deal.categories.set(random.sample(categories, min(3, len(categories))))
        if vendors:
            deal.vendors.set(random.sample(vendors, min(3, len(vendors))))

        count += 1

    print(f"  Created {count} deals")


def create_product_images():
    """Create product image records."""
    print("\nCreating Product Images...")
    products = list(Product.objects.all())  # pylint: disable=no-member
    count = 0

    for prod in products:
        if ProductImage.objects.filter(product=prod).exists():  # pylint: disable=no-member
            continue

        num_images = random.randint(1, 4)
        for i in range(num_images):
            ProductImage.objects.create(  # pylint: disable=no-member
                product=prod,
                alt_text=f"{prod.name} - Image {i+1}",
                is_primary=i == 0,
                order=i
            )
            count += 1

    print(f"  Created {count} product images")


def _populate_profile_fields(profile, user, cities, states, roles):
    """Helper to populate empty profile fields."""
    if not profile.city:
        profile.city = random.choice(cities)
    if not profile.state:
        profile.state = random.choice(states)
    if not profile.address:
        profile.address = f"{random.randint(1, 500)}, Main Road, {profile.city}"
    if not profile.pincode:
        profile.pincode = str(random.randint(110001, 999999))
    if not profile.role:
        profile.role = random.choice(roles)
    if not profile.shop_name:
        profile.shop_name = f"{user.first_name or 'User'}'s Shop"
    profile.credit_limit = random.randint(10000, 100000)
    profile.is_kyc_verified = random.choice([True, True, False])


def update_user_profiles():
    """Ensure all users have complete profiles."""
    print("\nUpdating User Profiles...")
    users = User.objects.exclude(is_superuser=True)

    cities = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Hyderabad', 'Kolkata', 'Pune']
    states = ['Maharashtra', 'Delhi', 'Karnataka', 'Tamil Nadu', 'Telangana', 'West Bengal']
    roles = ['buyer', 'farmer', 'retailer', 'wholesaler']

    count = 0
    for user in users:
        try:
            profile = user.profile
        except Profile.DoesNotExist:  # pylint: disable=no-member
            profile = Profile.objects.create(user=user)  # pylint: disable=no-member

        _populate_profile_fields(profile, user, cities, states, roles)
        profile.save()
        count += 1

    print(f"  Updated {count} user profiles")


def create_historical_orders():
    """Create more historical orders for analytics."""
    print("\nCreating Historical Orders...")
    users = list(User.objects.exclude(is_superuser=True)[:30])
    products = list(Product.objects.all()[:40])  # pylint: disable=no-member

    order_count = 0
    statuses = ['delivered', 'delivered', 'delivered', 'shipped', 'cancelled']
    payment_methods = ['COD', 'UPI', 'Card', 'NetBanking']

    for month_offset in range(1, 4):
        num_orders = random.randint(20, 40)

        for _ in range(num_orders):
            user = random.choice(users)
            num_items = random.randint(1, 4)
            order_products = random.sample(products, min(num_items, len(products)))
            total = sum(float(p.price) for p in order_products)

            days_ago = month_offset * 30 + random.randint(0, 29)
            order_date = timezone.now() - timedelta(days=days_ago)
            status = random.choice(statuses)

            order = Order.objects.create(  # pylint: disable=no-member
                user=user,
                first_name=user.first_name or "Customer",
                last_name=user.last_name or "User",
                email=user.email,
                phone=f"+91{random.randint(7000000000, 9999999999)}",
                address=f"{random.randint(1, 500)}, Street, City",
                place=random.choice(['Mumbai', 'Delhi', 'Bangalore']),
                zipcode=str(random.randint(110001, 999999)),
                paid_amount=total,
                status=status,
                payment_method=random.choice(payment_methods),
                paid=status == 'delivered',
            )
            order.created_at = order_date
            order.save()

            for prod in order_products:
                OrderItem.objects.create(  # pylint: disable=no-member
                    order=order,
                    product=prod,
                    vendor=prod.vendor,
                    price=prod.price,
                    quantity=random.randint(1, 3)
                )

            order_count += 1

    print(f"  Created {order_count} historical orders")


def add_postgresql_optimizations():
    """Add PostgreSQL-specific optimizations."""
    print("\nAdding PostgreSQL Optimizations...")

    with connection.cursor() as cursor:
        views = [
            """
            CREATE OR REPLACE VIEW daily_sales_summary AS
            SELECT
                DATE(created_at) as sale_date,
                COUNT(*) as total_orders,
                SUM(paid_amount) as total_revenue,
                AVG(paid_amount) as avg_order_value
            FROM store_order
            WHERE paid = true
            GROUP BY DATE(created_at)
            ORDER BY sale_date DESC;
            """,
            """
            CREATE OR REPLACE VIEW top_products AS
            SELECT
                p.id,
                p.name,
                p.price,
                COUNT(oi.id) as times_ordered,
                SUM(oi.quantity) as total_quantity_sold
            FROM store_product p
            LEFT JOIN store_orderitem oi ON p.id = oi.product_id
            GROUP BY p.id, p.name, p.price
            ORDER BY times_ordered DESC;
            """,
            """
            CREATE OR REPLACE VIEW vendor_performance AS
            SELECT
                v.id,
                v.name,
                COUNT(DISTINCT p.id) as product_count,
                COALESCE(AVG(r.rating), 0) as avg_rating
            FROM store_vendor v
            LEFT JOIN store_product p ON v.id = p.vendor_id
            LEFT JOIN store_review r ON p.id = r.product_id
            GROUP BY v.id, v.name;
            """,
        ]

        for view_sql in views:
            try:
                cursor.execute(view_sql)
                print("  ✓ Created view")
            except Exception as e:  # pylint: disable=broad-except
                print(f"  ! View: {str(e)[:40]}")

        try:
            cursor.execute("ANALYZE;")
            print("  ✓ Analyzed all tables")
        except Exception as e:  # pylint: disable=broad-except
            # ANALYZE may fail on SQLite; that's expected and safe to ignore
            print(f"  ! ANALYZE skipped (expected on SQLite): {str(e)[:30]}")

    print("  PostgreSQL optimizations applied")


def main():
    """Main function to enhance PostgreSQL database."""
    print("=" * 60)
    print("VIBE E-Commerce - PostgreSQL Database Enhancement")
    print("=" * 60)

    create_inventory_logs()
    create_premium_listings()
    create_subscriptions()
    create_product_comparisons()
    create_location_popularity()
    create_deals()
    create_product_images()
    update_user_profiles()
    create_historical_orders()
    add_postgresql_optimizations()

    print("\n" + "=" * 60)
    print("PostgreSQL Enhancement Complete!")
    print("=" * 60)

    print("\nENHANCEMENT SUMMARY:")
    print(f"  - Inventory Logs: {InventoryLog.objects.count()}")  # pylint: disable=no-member
    print(f"  - Premium Listings: {PremiumListing.objects.count()}")  # pylint: disable=no-member
    print(f"  - Subscriptions: {Subscription.objects.count()}")  # pylint: disable=no-member
    print(f"  - Product Comparisons: {ProductComparison.objects.count()}")  # pylint: disable=no-member
    print(f"  - Location Popularity: {LocationPopularity.objects.count()}")  # pylint: disable=no-member
    print(f"  - Deals: {Deal.objects.count()}")  # pylint: disable=no-member
    print(f"  - Product Images: {ProductImage.objects.count()}")  # pylint: disable=no-member
    print(f"  - Total Orders: {Order.objects.count()}")  # pylint: disable=no-member


if __name__ == '__main__':
    main()
