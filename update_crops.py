"""Update crop images with premium assets."""
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()


def update_crops():
    """Update crops with premium images."""
    # pylint: disable=import-outside-toplevel
    from store.models import Crop

    print("Updating Crop Images with Premium Assets...")

    # Map crop names to our premium images
    crop_map = {
        'wheat': 'products/wheat_grains.png',
        'rice': 'products/basmati_rice.png',
        'paddy': 'products/basmati_rice.png',
        'cotton': 'products/cotton_bales.png',
        'tomato': 'products/tomatoes.png',
        'potato': 'products/potatoes.png',
        'onion': 'products/onions.png',
        'mango': 'products/mangoes.png',
        'chilli': 'products/tomatoes.png',
        'sugarcane': 'products/smart_farm.png',
        'corn': 'products/seeds_macro.png',
        'maize': 'products/seeds_macro.png',
    }

    crops = Crop.objects.all()  # pylint: disable=no-member
    count = 0

    for crop in crops:
        name_lower = crop.name.lower()
        target = None

        for key, img in crop_map.items():
            if key in name_lower:
                target = img
                break

        if target:
            crop.image = target
            crop.save()
            count += 1
            print(f"Updated Crop [{crop.name}] -> {target}")

    print(f"\nUpdated {count} crops with premium images!")


if __name__ == '__main__':
    update_crops()
