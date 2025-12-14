"""
Script to add 10 additional products with images to the website.
Does NOT delete existing data.
"""
import os
import random
from io import BytesIO

import django
from PIL import Image, ImageDraw

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# noqa: E402 - Django must be set up before importing models
from django.core.files.base import ContentFile  # noqa: E402
from django.utils.text import slugify  # noqa: E402
from store.models import Category, Vendor, Product, ProductCropMapping, Crop, Disease  # noqa: E402

def create_placeholder_image(text, color, size=(600, 400)):
    """Generate a placeholder image with text."""
    img = Image.new('RGB', size, color=color)
    draw = ImageDraw.Draw(img)
    # Simple centering
    draw.text((size[0]//3, size[1]//2), text, fill=(255, 255, 255))
    
    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    return ContentFile(buffer.getvalue())

def add_products():
    print("Adding 10 new products with images...")
    
    vendors = list(Vendor.objects.all())
    categories = list(Category.objects.all())
    
    if not vendors or not categories:
        print("No vendors or categories found. Please run populate_db.py first or ensure basic data exists.")
        return

    crops = list(Crop.objects.all())
    _diseases = list(Disease.objects.all())  # Reserved for future disease mappings

    new_products_data = [
        ("Premium Organic Compost", "Fertilizers", 500, 800),
        ("High Yield Hybrid Tomato Seeds", "Seeds", 1200, 1800),
        ("Solar Insect Trap", "Farm Implements", 2500, 3500),
        ("Neem Oil Pesticide", "Insecticides", 300, 450),
        ("Drip Irrigation Kit", "Farm Implements", 8000, 12000),
        ("Coco Peat Block 5kg", "Fertilizers", 250, 400),
        ("Power Weeder 5HP", "Farm Implements", 25000, 35000),
        ("Bio-Fungicide Trichoderma", "Fungicides", 150, 250),
        ("Sticky Traps (Yellow/Blue)", "Insecticides", 400, 600),
        ("Vegetable Seed Kit (10 Varieties)", "Seeds", 999, 1499),
    ]

    count = 0
    for name, cat_name, price, mrp in new_products_data:
        # Find or create category (fuzzy match or exact)
        category = next((c for c in categories if c.name == cat_name), None)
        if not category:
            category = random.choice(categories)  # nosec B311 - not for security
        
        vendor = random.choice(vendors)  # nosec B311 - not for security
        slug = slugify(f"{name} {random.randint(1000,9999)}")  # nosec B311
        
        # Check if identical slug already exists (though we added random int)
        if Product.objects.filter(slug=slug).exists():
            print(f"Skipping existing product slug: {slug}")
            continue

        prod = Product.objects.create(
            name=name,
            slug=slug,
            category=category,
            vendor=vendor,
            price=price,
            mrp=mrp,
            brand=vendor.name,
            description=f"Advanced {name} for better yield. Brand: {vendor.name}.",
            stock_quantity=random.randint(10, 100),  # nosec B311
            is_active=True,
            trending_score=random.randint(50, 100)  # nosec B311
        )

        # Create Image
        # nosec B311 - random colors for placeholder, not security-sensitive
        color = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
        img_content = create_placeholder_image(name, color)
        prod.image.save(f"{slug}.jpg", img_content, save=False)
        prod.save()
        count += 1
        print(f"Created product: {name}")

        # Add Crop mappings
        if crops:
             # Use sample to ensure UNIQUE crops are selected for this product
             k = random.randint(1, min(2, len(crops)))  # nosec B311
             selected_crops = random.sample(crops, k)  # nosec B311
             for crop in selected_crops:
                ProductCropMapping.objects.get_or_create(
                    product=prod, 
                    crop=crop, 
                    defaults={'effectiveness_rating': random.randint(8, 10)}  # nosec B311
                )

    print(f"Successfully added {count} new products.")

if __name__ == "__main__":
    add_products()
