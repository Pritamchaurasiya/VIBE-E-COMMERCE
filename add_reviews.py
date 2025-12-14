"""
Script to add sample reviews and complete remaining data.
"""
import os
import random

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# pylint: disable=wrong-import-position,no-member
from django.contrib.auth.models import User  # noqa: E402
from django.utils import timezone  # noqa: E402
from store.models import (  # noqa: E402
    Product, Review, FlashSale, Deal, Order, OrderItem, Vendor
)
# pylint: enable=wrong-import-position


def create_users():
    """Create sample users for reviews."""
    print("Creating sample users...")
    users = []
    usernames = [
        'ramesh_farmer', 'suresh_agro', 'kisan_kumar', 'priya_organic',
        'vijay_crops', 'meena_harvest', 'rajesh_fields', 'sunita_seeds',
        'mohan_farm', 'lakshmi_agri'
    ]
    for username in usernames:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username}@example.com',
                'first_name': username.split('_', maxsplit=1)[0].title(),
                'last_name': 'Farmer'
            }
        )
        if created:
            user.set_password('TestPass123!')
            user.save()
        users.append(user)
    print(f"Created/Found {len(users)} users")
    return users


def create_reviews(users):
    """Create sample reviews for products."""
    print("Creating sample reviews...")
    products = list(Product.objects.all()[:50])  # Review top 50 products

    review_titles = [
        "Excellent product!",
        "Very effective",
        "Good quality",
        "Best in market",
        "Worth the price",
        "Highly recommended",
        "Good results",
        "Satisfied customer",
        "Will buy again",
        "Quality product"
    ]

    review_comments = [
        "Used this on my wheat crop and got amazing results. Yield increased by 20%.",
        "Very effective against pests. My cotton crop is healthier now.",
        "Good value for money. Delivery was fast and packaging was excellent.",
        "Best product I have used in years. Highly recommend to all farmers.",
        "Works as described. My tomato plants are growing beautifully.",
        "Genuine product from trusted vendor. Quality is top-notch.",
        "Easy to use and very effective. Results visible within a week.",
        "My go-to brand now. Never disappoints. Great for all crops.",
        "Affordable and effective. Perfect for small farmers like me.",
        "Premium quality at reasonable price. Customer service is also good."
    ]

    count = 0
    for product in products:
        # 2-5 reviews per product
        num_reviews = random.randint(2, 5)
        selected_users = random.sample(users, min(num_reviews, len(users)))

        for user in selected_users:
            # Check if review already exists
            if Review.objects.filter(product=product, user=user).exists():
                continue

            Review.objects.create(
                product=product,
                user=user,
                rating=random.randint(3, 5),  # 3-5 stars
                title=random.choice(review_titles),
                comment=random.choice(review_comments),
                is_verified_purchase=random.choice([True, True, False]),  # 66% verified
            )
            count += 1

    print(f"Created {count} reviews")


def create_flash_sales():
    """Create active flash sales."""
    print("Creating flash sales...")
    now = timezone.now()

    # Clear old flash sales
    FlashSale.objects.filter(end_time__lt=now).delete()

    flash_sale_data = [
        {
            'name': 'Monsoon Mega Sale',
            'slug': 'monsoon-mega-sale',
            'discount_percentage': 30,
            'hours': 48
        },
        {
            'name': 'Kisan Diwas Special',
            'slug': 'kisan-diwas-special',
            'discount_percentage': 25,
            'hours': 72
        },
        {
            'name': 'Flash Friday Deal',
            'slug': 'flash-friday-deal',
            'discount_percentage': 20,
            'hours': 24
        }
    ]

    products = list(Product.objects.all())

    for data in flash_sale_data:
        sale, created = FlashSale.objects.get_or_create(
            slug=data['slug'],
            defaults={
                'name': data['name'],
                'discount_percentage': data['discount_percentage'],
                'start_time': now,
                'end_time': now + timezone.timedelta(hours=data['hours']),
                'is_active': True
            }
        )
        if created:
            # Add 8-12 random products
            sale_products = random.sample(products, min(10, len(products)))
            sale.products.set(sale_products)
            sale.save()
            print(f"Created flash sale: {data['name']}")


def create_deals():
    """Create active deals."""
    print("Creating deals...")
    now = timezone.now()

    deals_data = [
        {
            'name': 'Buy 2 Get 1 Free',
            'slug': 'buy-2-get-1',
            'deal_type': 'percent',
            'discount_value': 33,
            'days': 7
        },
        {
            'name': 'Flat Rs.500 Off',
            'slug': 'flat-500-off',
            'deal_type': 'fixed',
            'discount_value': 500,
            'days': 5
        },
        {
            'name': 'Bulk Order Discount',
            'slug': 'bulk-order-discount',
            'deal_type': 'percent',
            'discount_value': 15,
            'days': 14
        }
    ]

    products = list(Product.objects.all())

    for data in deals_data:
        deal, created = Deal.objects.get_or_create(
            slug=data['slug'],
            defaults={
                'name': data['name'],
                'deal_type': data['deal_type'],
                'discount_value': data['discount_value'],
                'start_date': now,
                'end_date': now + timezone.timedelta(days=data['days']),
                'is_active': True
            }
        )
        if created:
            deal_products = random.sample(products, min(8, len(products)))
            deal.products.set(deal_products)
            deal.save()
            print(f"Created deal: {data['name']}")


def create_sample_orders(users):
    """Create sample orders for testing."""
    print("Creating sample orders...")
    products = list(Product.objects.all()[:20])
    vendors = list(Vendor.objects.all())

    count = 0
    for user in users[:5]:  # First 5 users get orders
        for _ in range(random.randint(1, 3)):  # 1-3 orders each
            order = Order.objects.create(
                user=user,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                address=f"{random.randint(1, 500)} Main Road",
                zipcode=f"{random.randint(100000, 999999)}",
                place=random.choice(['Delhi', 'Mumbai', 'Pune', 'Jaipur', 'Chennai']),
                phone=f"+91{random.randint(7000000000, 9999999999)}",
                paid=random.choice([True, True, False]),  # 66% paid
                status=random.choice(['pending', 'confirmed', 'shipped', 'delivered']),
                paid_amount=0
            )

            # Add 1-4 items
            total = 0
            order_products = random.sample(products, random.randint(1, 4))
            for prod in order_products:
                qty = random.randint(1, 5)
                price = float(prod.price) * qty
                total += price
                OrderItem.objects.create(
                    order=order,
                    product=prod,
                    vendor=prod.vendor or random.choice(vendors),
                    quantity=qty,
                    price=price
                )

            order.paid_amount = total
            order.save()
            count += 1

    print(f"Created {count} sample orders")


def main():
    """Main function to run all data creation."""
    print("=" * 60)
    print("VIBE E-Commerce - Additional Data Population")
    print("=" * 60)

    users = create_users()
    create_reviews(users)
    create_flash_sales()
    create_deals()
    create_sample_orders(users)

    # Print final counts
    print("\n" + "=" * 60)
    print("Final Database Statistics:")
    print(f"  Products: {Product.objects.count()}")
    print(f"  Reviews: {Review.objects.count()}")
    print(f"  Flash Sales: {FlashSale.objects.filter(is_active=True).count()}")
    print(f"  Deals: {Deal.objects.filter(is_active=True).count()}")
    print(f"  Orders: {Order.objects.count()}")
    print(f"  Users: {User.objects.count()}")
    print("=" * 60)


if __name__ == '__main__':
    main()
