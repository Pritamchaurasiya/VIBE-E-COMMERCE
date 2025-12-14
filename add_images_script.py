#!/usr/bin/env python3
"""
Script to add images to the agricultural website database.

Run this script after placing your images in the appropriate media folders.
Usage: python add_images_script.py [--dry-run]
"""

import os
import sys


def setup_django():
    """Configure Django settings."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    # pylint: disable=import-outside-toplevel
    import django
    django.setup()


def add_crop_images():
    """Add crop variety images to the database."""
    # pylint: disable=import-outside-toplevel
    from store.models import Crop
    print("Adding crop images...")

    crop_images = [
        ('cabbage_premium.jpg', 'Premium Cabbage', 'High-quality cabbage variety'),
        ('broccoli_green.jpg', 'Green Broccoli', 'Fresh green broccoli heads'),
        ('cauliflower_white.jpg', 'White Cauliflower', 'Clean white cauliflower'),
        ('carrot_orange.jpg', 'Orange Carrot', 'Sweet orange carrots'),
        ('spinach_green.jpg', 'Green Spinach', 'Fresh green spinach leaves'),
        ('lettuce_crisp.jpg', 'Crisp Lettuce', 'Fresh crispy lettuce'),
        ('onion_red.jpg', 'Red Onion', 'Red variety onions'),
        ('garlic_white.jpg', 'White Garlic', 'Premium white garlic bulbs'),
        ('potato_russet.jpg', 'Russet Potato', 'High-starch russet potatoes'),
        ('sweet_potato.jpg', 'Sweet Potato', 'Orange-fleshed sweet potatoes'),
    ]

    added_count = 0
    for i, (filename, name, description) in enumerate(crop_images, 1):
        try:
            image_path = f'media/crops/{filename}'
            if os.path.exists(image_path):
                _, created = Crop.objects.get_or_create(  # pylint: disable=no-member
                    name=name,
                    defaults={
                        'slug': name.lower().replace(' ', '-'),
                        'description': description,
                        'image': f'crops/{filename}',
                        'season': 'all',
                        'order': i
                    }
                )
                if created:
                    print(f"  Added crop: {name}")
                    added_count += 1
                else:
                    print(f"  Crop already exists: {name}")
            else:
                print(f"  Image not found: {image_path}")
        except (ValueError, OSError) as e:
            print(f"  Error adding {name}: {e}")

    return added_count


def add_disease_images():
    """Add disease identification images."""
    # pylint: disable=import-outside-toplevel
    from store.models import Disease
    print("\nAdding disease images...")

    disease_images = [
        ('mosaic_virus.jpg', 'Mosaic Virus', 'Viral disease causing leaf mottling'),
        ('bacterial_blight.jpg', 'Bacterial Blight', 'Bacterial infection'),
        ('fungal_rust.jpg', 'Fungal Rust', 'Orange-brown fungal spots'),
        ('downy_mildew.jpg', 'Downy Mildew', 'White fungal growth on leaves'),
        ('powdery_mildew.jpg', 'Powdery Mildew', 'White powdery fungal coating'),
        ('root_rot.jpg', 'Root Rot', 'Darkened, decaying roots'),
        ('leaf_spot.jpg', 'Leaf Spot', 'Circular brown spots on leaves'),
        ('stem_canker.jpg', 'Stem Canker', 'Elongated lesions on stems'),
        ('wilt_disease.jpg', 'Wilt Disease', 'Sudden wilting of plant foliage'),
        ('anthracnose.jpg', 'Anthracnose', 'Dark, sunken lesions on fruits'),
    ]

    added_count = 0
    for i, (filename, name, description) in enumerate(disease_images, 1):
        try:
            image_path = f'media/diseases/{filename}'
            if os.path.exists(image_path):
                _, created = Disease.objects.get_or_create(  # pylint: disable=no-member
                    name=name,
                    defaults={
                        'slug': name.lower().replace(' ', '-'),
                        'description': description,
                        'image': f'diseases/{filename}',
                        'symptoms': f'Symptoms of {name.lower()}',
                        'is_common': i <= 5,
                        'order': i
                    }
                )
                if created:
                    print(f"  Added disease: {name}")
                    added_count += 1
                else:
                    print(f"  Disease already exists: {name}")
            else:
                print(f"  Image not found: {image_path}")
        except (ValueError, OSError) as e:
            print(f"  Error adding {name}: {e}")

    return added_count


def add_product_gallery_images():
    """Add gallery images to existing products."""
    # pylint: disable=import-outside-toplevel
    from store.models import Product, ProductImage
    print("\nAdding product gallery images...")

    products = Product.objects.all()[:10]  # pylint: disable=no-member

    gallery_images = [
        'product_view_1.jpg',
        'product_view_2.jpg',
        'product_view_3.jpg',
        'packaging_detail.jpg',
        'usage_demo.jpg',
        'before_after.jpg',
        'application_method.jpg',
        'storage_tips.jpg',
        'comparison_chart.jpg',
        'application_guide.jpg'
    ]

    added_count = 0
    for i, product in enumerate(products):
        try:
            gallery_filename = gallery_images[i % len(gallery_images)]
            image_path = f'media/products/gallery/{gallery_filename}'

            if os.path.exists(image_path):
                existing = ProductImage.objects.filter(  # pylint: disable=no-member
                    product=product
                ).count()
                if existing < 3:
                    ProductImage.objects.create(  # pylint: disable=no-member
                        product=product,
                        image=f'products/gallery/{gallery_filename}',
                        alt_text=f'{product.name} - View {existing + 1}',
                        order=existing
                    )
                    print(f"  Added gallery image to: {product.name}")
                    added_count += 1
                else:
                    print(f"  Max gallery images for: {product.name}")
            else:
                print(f"  Gallery image not found: {image_path}")
        except (ValueError, OSError) as e:
            print(f"  Error for {product.name}: {e}")

    return added_count


def main():
    """Main function to add all images."""
    print("Agricultural Website - Image Upload Helper")
    print("=" * 50)

    print("\nBefore running this script:")
    print("1. Place images in the appropriate media folders:")
    print("   - Crop images: media/crops/")
    print("   - Disease images: media/diseases/")
    print("   - Product gallery: media/products/gallery/")
    print("\n2. Ensure Django is set up and database is accessible")

    if len(sys.argv) > 1 and sys.argv[1] == '--dry-run':
        print("\nDRY RUN MODE - No changes will be made")
        return

    # Setup Django
    setup_django()

    # pylint: disable=import-outside-toplevel
    from store.models import Crop, Disease, ProductImage

    try:
        crops_added = add_crop_images()
        diseases_added = add_disease_images()
        gallery_added = add_product_gallery_images()

        print("\n" + "=" * 50)
        print("Image upload process completed!")
        print("\nSummary:")
        # pylint: disable=no-member
        print(f"  Crops added: {crops_added} (Total: {Crop.objects.count()})")
        print(f"  Diseases added: {diseases_added} "
              f"(Total: {Disease.objects.count()})")
        print(f"  Gallery images added: {gallery_added} "
              f"(Total: {ProductImage.objects.count()})")

    except (ValueError, OSError) as e:
        print(f"\nError during image upload: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
