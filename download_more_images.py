import os
import random
import time
import urllib.request

def download_images():
    print("ðŸŒ Downloading 20 New Agriculture Images from Public Sources...")

    # Target directory
    save_dir = 'media/products'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # List of 20 new distinct keywords to fetch
    keywords = [
        'corn_field', 'sunflower_crop', 'soybean_plant', 'sugarcane_farm', 'barley_grain',
        'fresh_apple', 'banana_bunch', 'grapes_vineyard', 'orange_grove', 'dairy_cow',
        'poultry_chicken', 'goat_farm', 'honey_bee_hive', 'mushroom_farm', 'green_chilli',
        'red_capsicum', 'greenhouse_interior', 'agriculture_drone', 'farm_truck_pickup', 'wind_turbine_farm'
    ]

    downloaded_count = 0

    for key in keywords:
        search_term = key.replace('_', ',') # e.g. "corn,field"
        url = f"https://loremflickr.com/800/600/{search_term}"
        filename = f"{key}.jpg"
        filepath = os.path.join(save_dir, filename)

        try:
            print(f"   â¬‡ï¸ Downloading: {key}...", end='\r')
            # Add random parameter to bypass cache
            req_url = f"{url}?random={random.randint(1, 1000)}"

            # Download
            urllib.request.urlretrieve(req_url, filepath)

            # Verify file size (sometimes these services return tiny error images)
            if os.path.getsize(filepath) > 1000:
                print(f"   âœ… Saved: {filename}                  ")
                downloaded_count += 1
            else:
                print(f"   âš ï¸ Failed (Too small): {filename}      ")

            # Be nice to the server
            time.sleep(1)

        except Exception as e:
            print(f"   âŒ Error downloading {key}: {e}")

    print(f"\nâœ¨ Downloaded {downloaded_count} new images!")

if __name__ == '__main__':
    download_images()
