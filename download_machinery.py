
import os
import random
import shutil
import urllib.request
from decimal import Decimal
import django
from django.core.files import File
from django.utils.text import slugify

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# noqa: E402 - Import must happen after Django setup
from store.models import Product, Category, Vendor, User  # noqa: E402

# Configuration
CATEGORY_NAME = 'Machinery'
VENDOR_NAME = 'AgriTech Solutions'
IMAGE_DIR = 'media/products/machinery'

# Ensure directory exists
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

# Product Data (Machinery)
products_data = [
    {
        "name": "Heavy Duty Tractor 50HP",
        "price": 650000.00,
        "mrp": 700000.00,
        "description": "Powerful 50HP tractor suitable for all major farming tasks. Features power steering and high fuel efficiency.",
        "search_term": "tractor"
    },
    {
        "name": "Combine Harvester Pro",
        "price": 1800000.00,
        "mrp": 2000000.00,
        "description": "Advanced combine harvester for wheat, rice, and corn. Maximizes grain recovery and minimizes loss.",
        "search_term": "harvester"
    },
    {
        "name": "Rotavator 6 Feet",
        "price": 95000.00,
        "mrp": 105000.00,
        "description": "Heavy-duty rotavator for perfect soil pulverization. Compatible with 40-50HP tractors.",
        "search_term": "tiller"
    },
    {
        "name": "Seed Drill Machine",
        "price": 45000.00,
        "mrp": 50000.00,
        "description": "Precision seed drill for wheat, pulses, and oilseeds. Ensures uniform seed distribution.",
        "search_term": "planting machinery"
    },
    {
        "name": "Agricultural Drone Sprayer",
        "price": 350000.00,
        "mrp": 400000.00,
        "description": "10L capacity drone for efficient pesticide spraying. Covers 1 acre in 15 minutes.",
        "search_term": "agricultural drone"
    },
    {
        "name": "Power Tiller 12HP",
        "price": 145000.00,
        "mrp": 160000.00,
        "description": "Versatile power tiller for small farms. Attachments available for ploughing and weeding.",
        "search_term": "tractor"
    },
    {
        "name": "Irrigation Water Pump 5HP",
        "price": 28000.00,
        "mrp": 32000.00,
        "description": "High-pressure diesel water pump for irrigation. Durable and fuel-efficient.",
        "search_term": "pump"
    },
    {
        "name": "Chaff Cutter Machine",
        "price": 18500.00,
        "mrp": 22000.00,
        "description": "Electric chaff cutter for preparing animal feed. Safety features included.",
        "search_term": "machine"
    },
    {
        "name": "Solar Insect Trap",
        "price": 4500.00,
        "mrp": 5500.00,
        "description": "Eco-friendly solar trap to control pests in the field. Automatic operation.",
        "search_term": "light trap"
    },
    {
        "name": "Brush Cutter 4 Stroke",
        "price": 12000.00,
        "mrp": 15000.00,
        "description": "Portable brush cutter for clearing weeds and grass. Lightweight and easy to use.",
        "search_term": "brush cutter"
    }
]

def download_image(url, filepath):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            with open(filepath, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def main():
    # 1. Get or Create User
    user, created = User.objects.get_or_create(username='agritech_admin', defaults={'email': 'admin@agritech.com'})
    if created:
        # Use environment variable for password, avoid hardcoding credentials
        admin_password = os.environ.get('AGRITECH_ADMIN_PASSWORD', None)
        if not admin_password:
            # Generate a secure random password if not provided
            import secrets as sec
            admin_password = sec.token_urlsafe(16)
            print("Generated secure password for agritech_admin. Set AGRITECH_ADMIN_PASSWORD env var to customize.")
        user.set_password(admin_password)
        user.save()
        print(f"Created user: {user.username}")

    # 2. Get or Create Verify Vendor
    vendor, created = Vendor.objects.get_or_create(
        name=VENDOR_NAME,
        defaults={
            'slug': slugify(VENDOR_NAME),
            'city': 'Pune',
            'created_by': user,
            'is_active': True,
            'is_verified': True,
            'rating': 4.9
        }
    )
    if created:
        print(f"Created vendor: {vendor.name}")

    # 3. Get or Create Category
    category, created = Category.objects.get_or_create(
        name=CATEGORY_NAME,
        defaults={'slug': slugify(CATEGORY_NAME)}
    )
    if created:
        print(f"Created category: {category.name}")

    # 4. Create Products
    for prod_data in products_data:
        print(f"Processing: {prod_data['name']}")
        
        # Check if product exists
        if Product.objects.filter(name=prod_data['name']).exists():
            print(" - Skipped (Already exists)")
            continue

        # Download Image
        image_filename = f"{slugify(prod_data['name'])}.jpg"
        image_path = os.path.join(IMAGE_DIR, image_filename)
        
        # Use loremflickr or unsplash source
        image_url = f"https://loremflickr.com/800/600/{prod_data['search_term'].replace(' ', ',')}/all"
        
        if download_image(image_url, image_path):
            # Create Product Entry
            product = Product(
                category=category,
                vendor=vendor,
                name=prod_data['name'],
                slug=slugify(prod_data['name']),
                description=prod_data['description'],
                price=Decimal(str(prod_data['price'])),
                mrp=Decimal(str(prod_data['mrp'])) if prod_data['mrp'] else None,
                stock_quantity=random.randint(5, 50), # Fewer in stock for machinery
                is_active=True,
                trending_score=random.randint(70, 95),
                meta_title=f"{prod_data['name']} - Buy Online",
                meta_description=f"Buy {prod_data['name']} at best price from {VENDOR_NAME}."
            )
            
            # Save image
            with open(image_path, 'rb') as img_file:
                product.image.save(image_filename, File(img_file), save=True)
            
            print(" - Created successfully")
        else:
            print(" - Failed to download image")

    print("\nMachinery products added successfully!")

if __name__ == '__main__':
    main()
