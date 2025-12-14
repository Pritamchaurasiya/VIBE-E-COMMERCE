"""
Script to populate the database with realistic Agri B2B data (AGRIM style).
Generates ~100 products, crops, diseases, and deals.

Note: Pylint warnings about 'Class X has no objects member' are false positives.
Django models have the 'objects' manager added dynamically at runtime.
"""
import os
import random
from io import BytesIO

import django
from PIL import Image, ImageDraw

# Setup Django environment - must happen before importing Django models
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# pylint: disable=wrong-import-position
# These imports must come after django.setup() to work correctly
from django.core.files.base import ContentFile  # noqa: E402
from django.utils import timezone  # noqa: E402
from django.utils.text import slugify  # noqa: E402
from store.models import (  # noqa: E402
    Category, Vendor, Product, Crop, Disease,
    ProductCropMapping, ProductDiseaseMapping,
    DealOfTheDay, ProductPackingOption, BulkPricing,
)
# pylint: enable=wrong-import-position

# Constants
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
CAT_FARM_IMPLEMENTS = 'Farm Implements'
CAT_FUNGICIDES = 'Fungicides'
CAT_INSECTICIDES = 'Insecticides'

# Ensure media directories exist
for subdir in ['products', 'crops', 'diseases', 'vendors', 'flash_sales']:
    path = os.path.join(MEDIA_ROOT, subdir)
    os.makedirs(path, exist_ok=True)


def create_placeholder_image(text, color, size=(400, 400)):
    """Generate a placeholder image with text."""
    img = Image.new('RGB', size, color=color)
    draw = ImageDraw.Draw(img)
    # Just center text slightly roughly
    draw.text((size[0]//4, size[1]//2), text, fill=(255, 255, 255))

    # Save to buffer
    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    return ContentFile(buffer.getvalue())


def clean_old_data():
    """Clear existing relevant data for a clean slate."""
    print("Cleaning old data...")
    # pylint: disable=no-member
    ProductCropMapping.objects.all().delete()
    ProductDiseaseMapping.objects.all().delete()
    ProductPackingOption.objects.all().delete()
    BulkPricing.objects.all().delete()
    DealOfTheDay.objects.all().delete()
    Crop.objects.all().delete()
    Disease.objects.all().delete()
    Product.objects.all().delete()
    Category.objects.all().delete()
    Vendor.objects.all().delete()
    # pylint: enable=no-member


def create_crops():
    """Create crop entries and return the list of created crops."""
    print("Creating Crops...")
    crops_data = [
        ('Wheat', 'wheat', 'Gehu', 'ðŸŒ¾', 'rabi'),
        ('Rice', 'rice', 'Dhan', 'ðŸš', 'kharif'),
        ('Cotton', 'cotton', 'Kapas', 'ðŸŒ¿', 'kharif'),
        ('Tomato', 'tomato', 'Tamatar', 'ðŸ…', 'all'),
        ('Potato', 'potato', 'Aloo', 'ðŸ¥”', 'rabi'),
        ('Onion', 'onion', 'Pyaz', 'ðŸ§…', 'rabi'),
        ('Chilli', 'chilli', 'Mirch', 'ðŸŒ¶ï¸', 'all'),
        ('Maize', 'maize', 'Makka', 'ðŸŒ½', 'kharif'),
        ('Sugarcane', 'sugarcane', 'Ganna', 'ðŸŽ‹', 'all'),
        ('Mustard', 'mustard', 'Sarson', 'ðŸŒ¼', 'rabi'),
    ]

    db_crops = []
    for i, (name, slug, hindi, icon, season) in enumerate(crops_data):
        crop_obj = Crop.objects.create(  # pylint: disable=no-member
            name=name, slug=slug, hindi_name=hindi, icon=icon, season=season,
            is_popular=True, order=i
        )
        # Generate image
        img_content = create_placeholder_image(name, (34, 139, 34))
        crop_obj.image.save(f"{slug}.jpg", img_content, save=False)
        crop_obj.save()
        db_crops.append(crop_obj)

    return db_crops


def create_diseases():
    """Create disease entries and return the list of created diseases."""
    print("Creating Diseases...")
    diseases_data = [
        ('Leaf Miner', 'leaf-miner', 'Leaf Miner', 'ðŸ›', 'Small tunnels in leaves'),
        ('Powdery Mildew', 'powdery-mildew', 'Safed Fafundi', 'âšª',
         'White powder on leaves'),
        ('Root Rot', 'root-rot', 'Jad Galan', 'ðŸŸ¤', 'Roots turn black/brown'),
        ('Aphids', 'aphids', 'Maho', 'ðŸœ', 'Small sucking pests'),
        ('Blight', 'blight', 'Jhulsa', 'ðŸ‚', 'Brown spots on leaves'),
        ('Whitefly', 'whitefly', 'Safed Makkhi', 'ðŸª°', 'White flies under leaves'),
        ('Bollworm', 'bollworm', 'Illi', 'ðŸ›', 'Bores into cotton bolls'),
        ('Rust', 'rust', 'Gerui', 'ðŸ”´', 'Rusty pustules on leaves'),
    ]

    db_diseases = []
    for i, (name, slug, hindi, icon, symp) in enumerate(diseases_data):
        disease_obj = Disease.objects.create(  # pylint: disable=no-member
            name=name, slug=slug, hindi_name=hindi, icon=icon,
            symptoms=symp, is_common=True, order=i
        )
        img_content = create_placeholder_image(name, (139, 69, 19))
        disease_obj.image.save(f"{slug}.jpg", img_content, save=False)
        disease_obj.save()
        db_diseases.append(disease_obj)

    return db_diseases


def create_categories():
    """Create category entries and return the dictionary of created categories."""
    print("Creating Categories...")
    cats = {
        'Seeds': 'seeds',
        CAT_FUNGICIDES: 'fungicides',
        CAT_INSECTICIDES: 'insecticides',
        'Herbicides': 'herbicides',
        'Plant Growth Promoters': 'pgp',
        'Fertilizers': 'fertilizers',
        CAT_FARM_IMPLEMENTS: 'implements'
    }
    db_cats = {}
    for name, slug in cats.items():
        cat_obj = Category.objects.create(name=name, slug=slug)  # pylint: disable=no-member
        db_cats[name] = cat_obj

    return db_cats


def create_vendors():
    """Create vendor entries and return the list of created vendors."""
    print("Creating Vendors...")
    vendors = [
        'Syngenta', 'Bayer', 'UPL', 'Dhanuka', 'Godrej Agrovet',
        'Corteva', 'PI Industries', 'FMC', 'Crystal', 'Sumitomo'
    ]
    db_vendors = []
    for v_name in vendors:
        slug = slugify(v_name)
        ven = Vendor.objects.create(  # pylint: disable=no-member
            name=v_name, slug=slug, city='Mumbai',
            is_active=True, is_verified=True, rating=4.5
        )
        db_vendors.append(ven)

    return db_vendors


def create_single_product(tmpl_name, cat_name, min_p, max_p, db_vendors,
                          db_cats, db_crops, db_diseases):
    """Create a single product with all its related data. Returns True if created."""
    vendor = random.choice(db_vendors)
    price = random.randint(min_p, max_p)
    mrp = int(price * random.uniform(1.1, 1.4))

    # Unique naming
    variant_id = random.randint(100, 9999)
    name = f"{vendor.name} {tmpl_name} {variant_id}"
    slug = slugify(name)

    if Product.objects.filter(slug=slug).exists():  # pylint: disable=no-member
        return False

    prod = Product.objects.create(  # pylint: disable=no-member
        name=name,
        slug=slug,
        category=db_cats[cat_name],
        vendor=vendor,
        price=price,
        mrp=mrp,
        brand=vendor.name,
        description=(
            f"High quality {tmpl_name} from {vendor.name}. "
            "Best results for farmers."
        ),
        stock_quantity=random.randint(50, 500),
        is_active=True,
        trending_score=random.randint(0, 100)
    )

    # Image
    color = (
        random.randint(0, 100),
        random.randint(100, 200),
        random.randint(0, 100)
    )
    img_content = create_placeholder_image(
        f"{vendor.name}\n{tmpl_name}", color
    )
    prod.image.save(f"{slug}.jpg", img_content, save=False)
    prod.save()

    # Add packings
    ProductPackingOption.objects.create(  # pylint: disable=no-member
        product=prod, size="500g", price=price, mrp=mrp, is_default=True
    )
    ProductPackingOption.objects.create(  # pylint: disable=no-member
        product=prod, size="1kg", price=price*1.9, mrp=mrp*1.9
    )

    # Add Bulk pricing
    BulkPricing.objects.create(  # pylint: disable=no-member
        product=prod, min_quantity=10, price_per_unit=int(price*0.9)
    )

    # Link Crops
    k = random.randint(1, 3)
    selected_crops = random.sample(db_crops, k)
    for crop in selected_crops:
        ProductCropMapping.objects.create(  # pylint: disable=no-member
            product=prod, crop=crop, effectiveness_rating=random.randint(7, 10)
        )

    # Link Diseases (if chemical)
    if cat_name in [CAT_FUNGICIDES, CAT_INSECTICIDES]:
        k = random.randint(1, 2)
        selected_diseases = random.sample(db_diseases, k)
        for disease in selected_diseases:
            ProductDiseaseMapping.objects.create(  # pylint: disable=no-member
                product=prod, disease=disease,
                effectiveness_rating=random.randint(7, 10)
            )

    return True


def create_products(db_vendors, db_cats, db_crops, db_diseases):
    """Create product entries using templates."""
    print("Creating 100+ Products...")

    product_templates = [
        # Seeds
        ('Tomato Seeds', 'Seeds', 400, 1500),
        ('Chilli Seeds', 'Seeds', 300, 1200),
        ('Cotton Seeds', 'Seeds', 800, 2000),
        ('Wheat Seeds', 'Seeds', 40, 100),
        ('Paddy Seeds', 'Seeds', 50, 120),
        # Chemicals
        ('Systemic Fungicide', CAT_FUNGICIDES, 300, 2000),
        ('Contact Fungicide', CAT_FUNGICIDES, 200, 1000),
        ('Broad Spectrum Insecticide', CAT_INSECTICIDES, 400, 2500),
        ('Sucking Pest Control', CAT_INSECTICIDES, 300, 1500),
        ('Weed Killer', 'Herbicides', 500, 3000),
        # Nutrition
        ('Liquid Bio-Fertilizer', 'Fertilizers', 300, 900),
        ('Humic Acid', 'Plant Growth Promoters', 400, 1200),
        ('Micro-nutrient Mix', 'Fertilizers', 200, 800),
        # Tools
        ('Knapsack Sprayer', CAT_FARM_IMPLEMENTS, 1500, 4000),
        ('Battery Sprayer', CAT_FARM_IMPLEMENTS, 2500, 6000),
    ]

    count = 0
    for _ in range(7):  # Loop to create multiples
        for tmpl_name, cat_name, min_p, max_p in product_templates:
            if create_single_product(tmpl_name, cat_name, min_p, max_p,
                                     db_vendors, db_cats, db_crops, db_diseases):
                count += 1

    print(f"Created {count} products.")


def create_deal_of_day():
    """Create deal of the day with random products."""
    print("Creating Deal of the Day...")
    today = timezone.now().date()
    deal, _ = DealOfTheDay.objects.get_or_create(  # pylint: disable=no-member
        date=today,
        defaults={'title': "Mega Monsoon Sale", 'discount_percentage': 25}
    )
    # Add random 10 products
    all_prods = list(Product.objects.all())  # pylint: disable=no-member
    if len(all_prods) > 10:
        for prod in random.sample(all_prods, 10):
            deal.products.add(prod)
    deal.save()


def populate():
    """Populate database with sample Agri B2B data."""
    print("Beginning database population...")

    # Clear existing data
    clean_old_data()

    # Create base entities
    db_crops = create_crops()
    db_diseases = create_diseases()
    db_cats = create_categories()
    db_vendors = create_vendors()

    # Create products with all related data
    create_products(db_vendors, db_cats, db_crops, db_diseases)

    # Create deal of the day
    create_deal_of_day()

    print("Population Complete! Media files created in /media/")


if __name__ == '__main__':
    populate()
