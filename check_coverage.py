"""Check image coverage for products."""
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()


def check_images():
    """Check which products have images assigned."""
    # pylint: disable=import-outside-toplevel
    from store.models import Product

    products = Product.objects.all()  # pylint: disable=no-member
    missing_count = 0
    print(f"Total Products: {products.count()}")

    categorized = {}

    for p in products:
        if not p.image:
            print(f"MISSING IMAGE: {p.name}")
            missing_count += 1
        else:
            img_name = p.image.name
            if 'gallery' in img_name:
                continue

            if img_name not in categorized:
                categorized[img_name] = []
            if len(categorized[img_name]) < 3:
                categorized[img_name].append(p.name)

    print("\n--- Image Distribution ---")
    for img, names in categorized.items():
        print(f"{img}: {len(names)} examples: {names}")

    print(f"\nMissing images: {missing_count}")


if __name__ == '__main__':
    check_images()
