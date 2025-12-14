import os
import random
import time
import urllib.request

def download_batch_3():
    print("ðŸŒ Downloading 20 Additional Images (Batch 3 - Veg/Flower/Organic)...")

    save_dir = 'media/products'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    keywords = {
        'cauliflower_harvest': 'cauliflower',
        'cabbage_field': 'cabbage',
        'eggplant_brinjal': 'eggplant',
        'okra_ladyfinger': 'okra_plant',
        'bottle_gourd': 'calabash',
        'bitter_gourd': 'bitter_melon',
        'green_peas': 'peas_pod',
        'carrot_harvest': 'carrot',
        'watermelon_field': 'watermelon',
        'pineapple_farm': 'pineapple',
        'strawberry_plant': 'strawberry',
        'lemon_tree': 'lemon',
        'marigold_flower_field': 'marigold_flower',
        'rose_farming': 'rose_garden',
        'organic_compost': 'compost_soil',
        'vermicompost_bed': 'worm_compost',
        'neem_leaves': 'neem_tree',
        'aloe_vera_farm': 'aloe_vera',
        'bamboo_farm': 'bamboo',
        'hydroponic_setup': 'hydroponic_lettuce'
    }

    downloaded_count = 0

    for filename_key, search_term in keywords.items():
        url = f"https://loremflickr.com/800/600/{search_term.replace('_', ',')}"
        filename = f"{filename_key}.jpg"
        filepath = os.path.join(save_dir, filename)

        try:
            print(f"   â¬‡ï¸ Downloading: {search_term}...", end='\r')
            req_url = f"{url}?random={random.randint(2000, 3000)}"
            urllib.request.urlretrieve(req_url, filepath)

            if os.path.getsize(filepath) > 1000:
                print(f"   âœ… Saved: {filename}                  ")
                downloaded_count += 1
            else:
                print(f"   âš ï¸ Failed (Too small): {filename}      ")

            time.sleep(1)

        except Exception as e:
            print(f"   âŒ Error downloading {filename_key}: {e}")

    print(f"\nâœ¨ Downloaded {downloaded_count} new images!")

if __name__ == '__main__':
    download_batch_3()
