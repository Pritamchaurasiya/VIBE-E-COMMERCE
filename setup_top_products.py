# pylint: disable=no-member

import os
import shutil
import django

from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from store.models import Product, Category, Vendor

# Source directory for generated images
SOURCE_DIR = r"C:/Users/asus/.gemini/antigravity/brain/edf6da0a-6976-4e3b-93dd-c26ed99e41b7"

# Map of original filename suffix (or part of it) to product details
# We will look for files starting with the key
PRODUCTS_DATA = [
    {
        "file_prefix": "premium_organic_fertilizer",
        "name": "Terra Vita Premium Organic Fertilizer",
        "category": "Fertilizers",
        "price": 1299.00,
        "description": "100% Limited Edition Premium Organic Fertilizer. Rich in microbials, slow release technology for sustained growth.",
        "sku": "FERT-ORG-001"
    },
    {
        "file_prefix": "smart_soil_sensor",
        "name": "AgriTech Smart Soil Sensor",
        "category": "Technology",
        "price": 2499.00,
        "description": "Real-time soil moisture and health monitoring. Solar powered with wireless connectivity.",
        "sku": "TECH-SENS-001"
    },
    {
        "file_prefix": "high_yield_hybrid_seeds",
        "name": "Sun-Gro High Yield Tomato Seeds",
        "category": "Seeds",
        "price": 299.00,
        "description": "Premium hybrid tomato seeds guaranteed for high yield and disease resistance.",
        "sku": "SEED-TOM-001"
    },
    {
        "file_prefix": "automated_irrigation_valve",
        "name": "Agri-Flow Automated Irrigation Valve",
        "category": "Irrigation",
        "price": 3500.00,
        "description": "Industrial grade automated valve for precise water control. Compatible with smart systems.",
        "sku": "IRR-VALVE-001"
    },
    {
        "file_prefix": "organic_pest_repellent",
        "name": "Eco-Guard Organic Pest Repellent",
        "category": "Pest Control",
        "price": 599.00,
        "description": "Safe, plant-based pest repellent. USDA Organic certified, safe for pets and beneficial insects.",
        "sku": "PEST-ORG-001"
    },
    {
        "file_prefix": "hydroponic_nutrient_mix",
        "name": "Hydro-Gro Nutrient Mix (A+B)",
        "category": "Hydroponics",
        "price": 899.00,
        "description": "Complete 2-part nutrient system for hydroponic setups. Maximizes growth and yield.",
        "sku": "HYD-NUT-001"
    },
    {
        "file_prefix": "precision_pruning_shears",
        "name": "Pro-Cut Precision Pruning Shears",
        "category": "Tools",
        "price": 750.00,
        "description": "Ergonomic, high-carbon steel pruning shears for clean, precise cuts.",
        "sku": "TOOL-SHEAR-001"
    },
    {
        "file_prefix": "grow_light_led_panel",
        "name": "Lumen-Agra LED Grow Light",
        "category": "Grow Lights",
        "price": 4500.00,
        "description": "Full spectrum LED panel for indoor farming. Energy efficient and high PAR output.",
        "sku": "YIELD-LED-001"
    },
    {
        "file_prefix": "portable_soil_ph_meter",
        "name": "AgriTech Pro Soil pH Meter",
        "category": "Technology",
        "price": 1800.00,
        "description": "Instant digital pH readings. rugged design for field use.",
        "sku": "TECH-PH-001"
    },
    {
        "file_prefix": "greenhouse_temperature_controller",
        "name": "GrowMaster Temp Controller",
        "category": "Technology",
        "price": 3200.00,
        "description": "Precise temperature control for greenhouses. Heating and cooling modes.",
        "sku": "TECH-TEMP-001"
    }
]

def setup_products():
    print("Starting Top Products Setup...")

    # Ensure Vendor Exists
    vendor, _ = Vendor.objects.get_or_create(
        slug="vibe-agri-premium",
        defaults={'name': "Vibe Agri Premium", 'email': "premium@vibe.com"}
    )
    
    # Destination directory
    dest_dir = os.path.join(settings.MEDIA_ROOT, 'products', 'top_best')
    os.makedirs(dest_dir, exist_ok=True)
    
    # Find files in source dir
    if not os.path.exists(SOURCE_DIR):
        print(f"Source directory not found: {SOURCE_DIR}")
        return

    files = os.listdir(SOURCE_DIR)
    
    for product_data in PRODUCTS_DATA:
        prefix = product_data['file_prefix']
        
        # Find matching file
        matching_file = next((f for f in files if f.startswith(prefix) and f.endswith('.png')), None)
        
        if not matching_file:
            print(f"No image found for {prefix}")
            continue
            
        full_source_path = os.path.join(SOURCE_DIR, matching_file)
        new_filename = f"{prefix}.png"
        full_dest_path = os.path.join(dest_dir, new_filename)
        
        # Copy image
        shutil.copy2(full_source_path, full_dest_path)
        print(f"Copied image: {new_filename}")
        
        # Ensure Category Exists
        category, _ = Category.objects.get_or_create(
            slug=product_data['category'].lower().replace(' ', '-'),
            defaults={'name': product_data['category']}
        )
        
        # Create/Update Product
        slug = product_data['name'].lower().replace(' ', '-').replace('(', '').replace(')', '').replace('+', 'plus')
        product, created = Product.objects.update_or_create(
            slug=slug,
            defaults={
                'name': product_data['name'],
                'vendor': vendor,
                'category': category,
                'price': product_data['price'],
                'description': product_data['description'],
                'stock_quantity': 100,
                'is_active': True,
                # 'is_featured': True, # FieldError might happen if is_featured doesn't exist, checking list above...
                'image': f"products/top_best/{new_filename}" 
            }
        )
        
        if created:
            print(f"Created product: {product.name}")
        else:
            print(f"Updated product: {product.name}")

if __name__ == '__main__':
    setup_products()
