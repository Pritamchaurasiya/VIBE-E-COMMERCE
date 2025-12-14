"""
Advanced Features Data Population for VIBE E-Commerce.

Adds: Vendor Analytics, Price Alerts, User Coins, RFQs, Trade Events, etc.
Fixed version with correct model fields.

Note: This script uses the standard `random` module for generating test data.
This is intentional as security-grade randomness is not required for sample data
seeding. For security-sensitive operations, use `secrets` module instead.
"""
# pylint: disable=no-member
import os
# nosemgrep: python.lang.security.insecure-random-use
# trunk-ignore-all(bandit/B311): Intentional use for non-security test data seeding
import random  # nosec B311 # noqa: S311
from datetime import timedelta

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# pylint: disable=wrong-import-position
from django.contrib.auth.models import User  # noqa: E402
from django.utils import timezone  # noqa: E402
from store.models import (  # noqa: E402
    Product, Vendor, Category, VendorAnalytics, PriceAlert, UserCoin,
    CoinTransaction, RFQ, RFQQuote, BuyerInquiry, TradeEvent,
    EventRegistration, AuditLog, AnalyticsEvent, ProductVariant,
)
# pylint: enable=wrong-import-position


def create_vendor_analytics():
    """Create analytics data for vendors."""
    print("Creating Vendor Analytics...")
    vendors = Vendor.objects.all()
    count = 0
    today = timezone.now().date()

    for vendor in vendors:
        analytics, _ = VendorAnalytics.objects.get_or_create(
            vendor=vendor, date=today
        )

        analytics.total_products = random.randint(5, 50)
        analytics.active_products = analytics.total_products - random.randint(0, 5)
        analytics.out_of_stock_products = random.randint(0, 3)
        analytics.low_stock_products = random.randint(0, 5)
        analytics.total_orders = random.randint(100, 5000)
        analytics.total_revenue = random.randint(100000, 5000000)
        analytics.monthly_revenue = random.randint(50000, 500000)
        analytics.weekly_revenue = random.randint(10000, 100000)
        analytics.average_rating = round(random.uniform(3.5, 5.0), 2)
        analytics.total_reviews = random.randint(50, 500)
        analytics.pending_bulk_orders = random.randint(0, 10)
        analytics.save()
        count += 1

    print(f"  Updated analytics for {count} vendors")


def create_price_alerts():
    """Create price alerts for users."""
    print("\nCreating Price Alerts...")
    users = list(User.objects.exclude(is_superuser=True)[:30])
    products = list(Product.objects.all()[:50])
    count = 0

    for user in users:
        num_alerts = random.randint(1, 4)
        alert_products = random.sample(products, min(num_alerts, len(products)))

        for prod in alert_products:
            if PriceAlert.objects.filter(user=user, product=prod).exists():
                continue

            target_price = float(prod.price) * random.uniform(0.7, 0.9)
            PriceAlert.objects.create(
                user=user,
                product=prod,
                target_price=round(target_price, 2),
                current_price_at_creation=float(prod.price),
                is_active=random.choice([True, True, False]),
                is_triggered=False
            )
            count += 1

    print(f"  Created {count} price alerts")


def create_user_coins():
    """Create user coins/rewards."""
    print("\nCreating User Coins...")
    users = list(User.objects.exclude(is_superuser=True)[:50])
    count = 0

    for user in users:
        coin_account, _ = UserCoin.objects.get_or_create(user=user)

        coin_account.balance = random.randint(50, 2000)
        coin_account.lifetime_earned = coin_account.balance + random.randint(100, 1000)
        coin_account.lifetime_spent = coin_account.lifetime_earned - coin_account.balance
        coin_account.save()
        count += 1

        _create_coin_transactions(coin_account)

    print(f"  Created coin accounts for {count} users")


def _create_coin_transactions(coin_account):
    """Helper to create coin transactions for a user."""
    for _ in range(random.randint(2, 6)):
        trans_type = random.choice(['credit', 'debit', 'credit', 'credit'])
        reason = 'Order Reward' if trans_type == 'credit' else 'Discount Applied'
        CoinTransaction.objects.create(
            user_coin=coin_account,
            transaction_type=trans_type,
            amount=random.randint(10, 200),
            reason=f"{reason} #{random.randint(1000, 9999)}"
        )


RFQ_TITLES = [
    "Need Premium Quality Pesticide",
    "Looking for Organic Fertilizer Bulk Order",
    "High-Yield Seeds for Kharif Season",
    "Agriculture Equipment Quote Request",
    "Bulk Bio-fertilizers Required",
]

RFQ_STATUSES = ['open', 'quoted', 'closed', 'expired']
CITIES = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai']


def create_rfqs():
    """Create Request for Quotations."""
    print("\nCreating RFQs...")
    users = list(User.objects.exclude(is_superuser=True)[:20])
    vendors = list(Vendor.objects.all())
    categories = list(Category.objects.all())

    rfq_count = 0
    quote_count = 0

    for user in users:
        for _ in range(random.randint(1, 3)):
            rfq = _create_single_rfq(user, categories)
            rfq_count += 1

            # Add quotes for quoted/closed RFQs
            if rfq.status in ['quoted', 'closed']:
                quote_count += _add_rfq_quotes(rfq, vendors)

    print(f"  Created {rfq_count} RFQs with {quote_count} quotes")


def _create_single_rfq(user, categories):
    """Create a single RFQ."""
    quantity = random.randint(50, 500)
    category = random.choice(categories) if categories else None

    return RFQ.objects.create(
        buyer=user,
        title=random.choice(RFQ_TITLES),
        description=f"Looking for bulk order. Need {quantity} units within 2 weeks.",
        category=category,
        quantity=quantity,
        unit='kg',
        budget_min=random.randint(10000, 50000),
        budget_max=random.randint(50001, 200000),
        delivery_location=random.choice(CITIES),
        delivery_deadline=timezone.now() + timedelta(days=random.randint(7, 30)),
        status=random.choice(RFQ_STATUSES),
        is_public=True,
        expires_at=timezone.now() + timedelta(days=random.randint(30, 60))
    )


def _add_rfq_quotes(rfq, vendors):
    """Add quotes to an RFQ."""
    count = 0
    num_quotes = random.randint(1, 3)
    quoting_vendors = random.sample(vendors, min(num_quotes, len(vendors)))

    for idx, vendor in enumerate(quoting_vendors):
        unit_price = random.randint(100, 500)
        status = 'accepted' if rfq.status == 'closed' and idx == 0 else 'pending'

        RFQQuote.objects.create(
            rfq=rfq,
            vendor=vendor,
            price_per_unit=unit_price,
            total_price=rfq.quantity * unit_price,
            delivery_time=random.randint(3, 14),
            validity_days=random.randint(7, 30),
            status=status
        )
        count += 1

    return count


INQUIRY_STATUSES = ['pending', 'responded', 'closed']


def create_buyer_inquiries():
    """Create buyer inquiries."""
    print("\nCreating Buyer Inquiries...")
    users = list(User.objects.exclude(is_superuser=True)[:25])
    products = list(Product.objects.all()[:40])
    count = 0

    for user in users:
        num_inquiries = random.randint(1, 3)
        inquiry_products = random.sample(products, min(num_inquiries, len(products)))

        for prod in inquiry_products:
            _create_single_inquiry(user, prod)
            count += 1

    print(f"  Created {count} buyer inquiries")


def _create_single_inquiry(user, prod):
    """Create a single buyer inquiry."""
    budget_min = random.randint(10000, 50000)
    budget_max = random.randint(50000, 100000)

    BuyerInquiry.objects.create(
        buyer=user,
        vendor=prod.vendor,
        product=prod,
        subject=f"Inquiry about {prod.name}",
        message=f"I am interested in {prod.name}. Can you provide bulk pricing?",
        quantity_required=random.randint(10, 200),
        budget_range=f"Rs.{budget_min} - Rs.{budget_max}",
        delivery_location=random.choice(['Mumbai', 'Delhi', 'Bangalore']),
        status=random.choice(INQUIRY_STATUSES),
        is_urgent=random.choice([True, False, False]),
        contact_phone=f"+91{random.randint(7000000000, 9999999999)}",
        contact_email=user.email
    )


EVENTS_DATA = [
    ("Kisan Mela 2025", "Annual agriculture exhibition", "Mumbai"),
    ("Agri Tech Summit", "Technology summit for farming", "Bangalore"),
    ("Seed Festival", "Premium quality seeds exhibition", "Delhi"),
    ("Organic Farming Expo", "Organic farming techniques", "Pune"),
    ("Farm Equipment Show", "Farm machinery showcase", "Chennai"),
]


def create_trade_events():
    """Create trade events and registrations."""
    print("\nCreating Trade Events...")
    vendors = list(Vendor.objects.all())
    event_count = 0
    reg_count = 0

    for i, (name, desc, city) in enumerate(EVENTS_DATA):
        slug = name.lower().replace(' ', '-')

        if TradeEvent.objects.filter(slug=slug).exists():
            continue

        event = _create_single_event(name, slug, desc, city, i)
        event_count += 1

        # Add registrations
        reg_count += _add_event_registrations(event, vendors)

    print(f"  Created {event_count} trade events with {reg_count} registrations")


def _create_single_event(name, slug, desc, city, index):
    """Create a single trade event."""
    start_date = timezone.now() + timedelta(days=random.randint(10, 90))

    return TradeEvent.objects.create(
        name=name,
        slug=slug,
        description=desc,
        venue=f"{city} Convention Center",
        city=city,
        start_date=start_date,
        end_date=start_date + timedelta(days=random.randint(1, 3)),
        registration_deadline=start_date - timedelta(days=5),
        entry_fee=random.choice([0, 100, 200, 500]),
        max_exhibitors=random.randint(100, 500),
        is_active=True,
        is_featured=index < 2
    )


def _add_event_registrations(event, vendors):
    """Add registrations to an event."""
    count = 0
    num_registrations = random.randint(5, 15)
    reg_vendors = random.sample(vendors, min(num_registrations, len(vendors)))

    for vendor in reg_vendors:
        if EventRegistration.objects.filter(event=event, vendor=vendor).exists():
            continue

        EventRegistration.objects.create(
            event=event,
            vendor=vendor,
            booth_number=f"B{random.randint(1, 100)}",
            payment_status=random.choice(['pending', 'paid', 'paid'])
        )
        count += 1

    return count


AUDIT_ACTIONS = [
    'login', 'logout', 'product_view', 'cart_add', 'order_placed', 'profile_update'
]


def create_audit_logs():
    """Create audit log entries."""
    print("\nCreating Audit Logs...")
    users = list(User.objects.all()[:20])
    count = 0

    for user in users:
        for _ in range(random.randint(5, 15)):
            action = random.choice(AUDIT_ACTIONS)
            model = 'User' if action in ['login', 'logout', 'profile_update'] else 'Product'

            AuditLog.objects.create(
                user=user,
                action=action,
                model_name=model,
                object_id=str(random.randint(1, 100)),
                object_repr=f"Object #{random.randint(1, 100)}",
                ip_address=f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
                user_agent="Mozilla/5.0 Chrome/120.0"
            )
            count += 1

    print(f"  Created {count} audit logs")


ANALYTICS_EVENT_TYPES = [
    'page_view', 'product_view', 'add_to_cart', 'purchase', 'search'
]


def create_analytics_events():
    """Create analytics event data."""
    print("\nCreating Analytics Events...")
    users = list(User.objects.exclude(is_superuser=True)[:30])
    products = list(Product.objects.all()[:50])
    categories = list(Category.objects.all())
    vendors = list(Vendor.objects.all())
    count = 0

    for user in users:
        count += _create_user_analytics_events(
            user, products, categories, vendors
        )

    print(f"  Created {count} analytics events")


def _create_user_analytics_events(user, products, categories, vendors):
    """Create analytics events for a single user."""
    count = 0
    for _ in range(random.randint(10, 30)):
        event_type = random.choice(ANALYTICS_EVENT_TYPES)
        product = _get_product_for_event(event_type, products)

        AnalyticsEvent.objects.create(
            user=user,
            session_id=f"session_{random.randint(10000, 99999)}",
            event_type=event_type,
            product=product,
            category=random.choice(categories) if categories else None,
            vendor=random.choice(vendors) if vendors else None,
            ip_address=f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
            user_agent="Mozilla/5.0 Chrome/120.0"
        )
        count += 1
    return count


def _get_product_for_event(event_type, products):
    """Get a product for product-related events."""
    if event_type in ['product_view', 'add_to_cart', 'purchase'] and products:
        return random.choice(products)
    return None


VARIANT_OPTIONS = [
    ('250g Pack', 250, -50),
    ('500g Pack', 500, 0),
    ('1kg Pack', 1000, 100),
    ('5kg Pack', 5000, 400),
]


def create_product_variants():
    """Create product variants."""
    print("\nCreating Product Variants...")
    products = list(Product.objects.all()[:30])
    count = 0

    for prod in products:
        if ProductVariant.objects.filter(product=prod).exists():
            continue

        num_variants = random.randint(2, 4)
        selected = random.sample(VARIANT_OPTIONS, num_variants)

        for i, (name, weight, price_mod) in enumerate(selected):
            ProductVariant.objects.create(
                product=prod,
                name=f"{prod.name} - {name}",
                sku=f"SKU-{prod.id}-{weight}",
                price_modifier=price_mod,
                stock_quantity=random.randint(10, 200),
                is_active=True,
                sort_order=i
            )
            count += 1

    print(f"  Created {count} product variants")


def main():
    """Main function to populate advanced features data."""
    print("=" * 60)
    print("VIBE E-Commerce - Advanced Features Data Population")
    print("=" * 60)

    create_vendor_analytics()
    create_price_alerts()
    create_user_coins()
    create_rfqs()
    create_buyer_inquiries()
    create_trade_events()
    create_audit_logs()
    create_analytics_events()
    create_product_variants()

    print("\n" + "=" * 60)
    print("Advanced Features Data Population Complete!")
    print("=" * 60)

    # Summary
    print("\nADVANCED FEATURES SUMMARY:")
    print(f"  - Vendor Analytics: {VendorAnalytics.objects.count()}")
    print(f"  - Price Alerts: {PriceAlert.objects.count()}")
    print(f"  - User Coin Accounts: {UserCoin.objects.count()}")
    print(f"  - Coin Transactions: {CoinTransaction.objects.count()}")
    print(f"  - RFQs: {RFQ.objects.count()}")
    print(f"  - RFQ Quotes: {RFQQuote.objects.count()}")
    print(f"  - Buyer Inquiries: {BuyerInquiry.objects.count()}")
    print(f"  - Trade Events: {TradeEvent.objects.count()}")
    print(f"  - Event Registrations: {EventRegistration.objects.count()}")
    print(f"  - Audit Logs: {AuditLog.objects.count()}")
    print(f"  - Analytics Events: {AnalyticsEvent.objects.count()}")
    print(f"  - Product Variants: {ProductVariant.objects.count()}")


if __name__ == '__main__':
    main()
