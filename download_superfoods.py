import os
import random
import time
import urllib.request
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def download_superfood_images():
    print("Downloading 10 Superfood Product Images...")

    save_dir = 'media/products/superfoods'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # Format: (search_term, product_name, category_name, price, mrp)
    products = [
        ('chia_seeds', 'Organic Chia Seeds', 'Superfoods', 450.00, 600.00),
        ('quinoa_grain', 'White Quinoa Grain', 'Superfoods', 380.00, 500.00),
        ('flax_seeds', 'Roasted Flax Seeds', 'Superfoods', 120.00, 180.00),
        ('spirulina_powder', 'Organic Spirulina Powder', 'Superfoods', 850.00, 1200.00),
        ('moringa_powder', 'Moringa Leaf Powder', 'Superfoods', 350.00, 450.00),
        ('goji_berries', 'Dried Goji Berries', 'Superfoods', 1500.00, 1800.00),
        ('matcha_tea', 'Ceremonial Matcha Tea', 'Superfoods', 2200.00, 3000.00),
        ('acai_berry', 'Acai Berry Powder', 'Superfoods', 3000.00, 3800.00),
        ('hemp_seeds', 'Raw Hemp Seeds', 'Superfoods', 900.00, 1100.00),
        ('cacao_nibs', 'Raw Cacao Nibs', 'Superfoods', 700.00, 950.00),
    ]

    from store.models import Product, Category, Vendor
    
    vendor, _ = Vendor.objects.get_or_create(
        name="Nature's Basket",
        defaults={
            'slug': 'natures-basket',
            'city': 'Bangalore',
            'is_verified': True,
            'description': 'Your source for organic and natural superfoods.',
            'rating': 4.7
        }
    )

    category, _ = Category.objects.get_or_create(
        name='Superfoods', 
        defaults={'slug': 'superfoods'}
    )

    downloaded_count = 0

    for search_term, name, _cat_name, price, mrp in products:
        filename = f"{search_term}.jpg"
        filepath = os.path.join(save_dir, filename)
        url = f"https://loremflickr.com/800/800/{search_term.replace('_', ',')}"

        try:
            if not os.path.exists(filepath) or os.path.getsize(filepath) < 1000:
                print(f"   Downloading: {name}...", end='\r')
                req_url = f"{url}?random={random.randint(10000, 99999)}"  # nosec B311
                urllib.request.urlretrieve(req_url, filepath)  # nosec B310 - trusted domain
                time.sleep(1.2)
            
            if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
                print(f"   Image ready: {filename}                  ")
                
                product, created = Product.objects.get_or_create(
                    name=name,
                    defaults={
                        'slug': name.lower().replace(' ', '-').replace("'", ""),
                        'category': category,
                        'vendor': vendor,
                        'price': price,
                        'mrp': mrp,
                        'description': f"High quality {name}. Rich in nutrients and 100% organic.",
                        'stock_quantity': 100,
                        'image': f'products/superfoods/{filename}',
                        'trending_score': 75,
                        'is_instant_pack': True,
                    }
                )
                if not created:
                    product.image = f'products/superfoods/{filename}'
                    product.save()

                downloaded_count += 1
            else:
                 print(f"   Failed to get valid image for: {name}")

        except Exception as e:
            print(f"   Error processing {name}: {e}")

    print(f"\nProcessed {downloaded_count} superfood products!")

if __name__ == '__main__':
    download_superfood_images()
