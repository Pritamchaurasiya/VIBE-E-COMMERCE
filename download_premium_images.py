import os
import random
import time
import urllib.request
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def download_premium_images():
    print("Downloading 10 Premium Product Images...")

    save_dir = 'media/products/premium'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # List of premium products with specific search terms
    # Format: (search_term, product_name, category_name, price, mrp)
    premium_products = [
        ('saffron_crocus', 'Kashmiri Saffron (Kesar)', 'Seeds', 5000.00, 6500.00),
        ('vanilla_pods', 'Organic Vanilla Beans', 'Seeds', 2500.00, 3200.00),
        ('dragon_fruit', 'Exotic Dragon Fruit Saplings', 'Seeds', 150.00, 250.00),
        ('macadamia_nuts', 'Macadamia Nut Plants', 'Seeds', 450.00, 600.00),
        ('hass_avocado', 'Grafted Hass Avocado Plant', 'Seeds', 350.00, 500.00),
        ('black_truffle', 'Black Truffle Inoculated Tree', 'Seeds', 8000.00, 10000.00),
        ('ginseng_roots', 'Medicinal Ginseng Roots', 'Seeds', 1200.00, 1800.00),
        ('wasabi_root', 'Real Wasabi Rhizome', 'Seeds', 3000.00, 4000.00),
        ('blueberries', 'Highbush Blueberry Plant', 'Seeds', 400.00, 550.00),
        ('royal_quinoa', 'Royal Quinoa Seeds', 'Seeds', 800.00, 950.00),
    ]

    from store.models import Product, Category, Vendor
    
    # Ensure a premium vendor exists
    vendor, _ = Vendor.objects.get_or_create(
        name="Premium Agro Imports",
        defaults={
            'slug': 'premium-agro-imports',
            'city': 'Mumbai',
            'is_verified': True,
            'description': 'Importers of exotic and high-value agricultural products.',
            'rating': 4.9
        }
    )

    downloaded_count = 0

    for search_term, name, cat_name, price, mrp in premium_products:
        
        # 1. Download Image
        filename = f"{search_term}.jpg"
        filepath = os.path.join(save_dir, filename)
        url = f"https://loremflickr.com/800/800/{search_term.replace('_', ',')}"

        try:
            if not os.path.exists(filepath) or os.path.getsize(filepath) < 1000:
                print(f"   Downloading: {name}...", end='\r')
                req_url = f"{url}?random={random.randint(10000, 99999)}"
                urllib.request.urlretrieve(req_url, filepath)
                time.sleep(1.5) # Be gentle
            
            if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
                print(f"   Image ready: {filename}                  ")
                
                # 2. Update/Create Product
                category, _ = Category.objects.get_or_create(
                    name=cat_name, 
                    defaults={'slug': cat_name.lower()}
                )

                product, created = Product.objects.get_or_create(
                    name=name,
                    defaults={
                        'slug': name.lower().replace(' ', '-').replace('(', '').replace(')', ''),
                        'category': category,
                        'vendor': vendor,
                        'price': price,
                        'mrp': mrp,
                        'description': f"Premium quality {name}. Imported and certified for best yield.",
                        'stock_quantity': 50,
                        'image': f'products/premium/{filename}',
                        'trending_score': 100, # Boost visibility
                        'is_instant_pack': True,
                    }
                )

                if not created:
                    # Update existing product to ensure it has the image and trending score
                    product.image = f'products/premium/{filename}'
                    product.trending_score = 100
                    product.save()
                    print(f"      Updated product: {name}")
                else:
                    print(f"      Created product: {name}")
                
                downloaded_count += 1
            else:
                 print(f"   Failed to get valid image for: {name}")

        except Exception as e:
            print(f"   Error processing {name}: {e}")

    print(f"\nProcessed {downloaded_count} premium products!")

if __name__ == '__main__':
    download_premium_images()
