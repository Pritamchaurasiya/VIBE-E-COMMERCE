"""Enhance categories with premium images."""
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()


def enhance_categories():
    """Re-enhance categories with premium images."""
    # pylint: disable=import-outside-toplevel
    from store.models import Category, Product

    print("Re-Enhancing Categories with Premium Images...")

    # Map slug/names to our new images
    category_map = {
        'seeds': 'categories/seeds.png',
        'fertilizer': 'categories/fertilizers.png',
        'growth': 'categories/fertilizers.png',
        'machinery': 'categories/machinery.png',
        'tools': 'categories/tools.png',
        'implement': 'categories/tools.png',
        'pesticide': 'categories/pesticides.png',
        'insecticid': 'categories/pesticides.png',
        'fungicid': 'categories/pesticides.png',
        'herbicid': 'categories/pesticides.png',
        'weed': 'categories/pesticides.png',
        'organic': 'categories/fertilizers.png',
        'irrigation': 'categories/machinery.png'
    }

    categories = Category.objects.all()  # pylint: disable=no-member
    for cat in categories:
        slug_check = cat.slug.lower()
        name_check = cat.name.lower()

        target_image = None

        # Check matching
        for key, image_path in category_map.items():
            if key in slug_check or key in name_check:
                target_image = image_path
                break

        if target_image:
            cat.image = target_image
            cat.save()
            print(f"Updated Category [{cat.name}] -> {target_image}")

            # Update products
            products = Product.objects.filter(  # pylint: disable=no-member
                category=cat
            )
            for prod in products:
                prod.image = target_image
                prod.save()
            print(f"  -> Updated {products.count()} products in {cat.name}")
        else:
            print(f"Still no match for [{cat.name}]")


if __name__ == '__main__':
    try:
        enhance_categories()
        print("\nWebsite Enhancement Complete!")
    except (ValueError, OSError) as e:
        print(f"Error: {e}")
