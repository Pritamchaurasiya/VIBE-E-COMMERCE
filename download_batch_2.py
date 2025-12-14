import os
import random
import time
import urllib.request

def download_more_images():
    print("ðŸŒ Downloading 10 Additional Images (Batch 2)...")

    save_dir = 'media/products'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # Batch 2 Keywords (Focus on Cash Crops & Spices common in India)
    keywords = {
        'coconut_tree': 'coconut',
        'tea_plantation': 'tea',
        'coffee_beans': 'coffee',
        'rubber_tapping': 'rubber',
        'turmeric_powder': 'turmeric',
        'black_pepper': 'spices',
        'pomegranate_fruit': 'pomegranate',
        'guava_fruit': 'guava',
        'papaya_tree': 'papaya',
        'ginger_root': 'ginger'
    }

    downloaded_count = 0

    for filename_key, search_term in keywords.items():
        url = f"https://loremflickr.com/800/600/{search_term.replace('_', ',')}"
        filename = f"{filename_key}.jpg"
        filepath = os.path.join(save_dir, filename)

        try:
            print(f"   â¬‡ï¸ Downloading: {search_term}...", end='\r')
            req_url = f"{url}?random={random.randint(1000, 2000)}"
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
    download_more_images()
