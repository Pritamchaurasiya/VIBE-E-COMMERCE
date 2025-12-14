"""Bulk populate product images with high-quality images."""
import os
import secrets

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()


def populate_product_images():
    """Populate products with appropriate images based on keywords."""
    # pylint: disable=import-outside-toplevel
    from store.models import Product
    print("Bulk Populating Product Images...")

    # Define our High Quality Image Pool
    image_pool = {
        'wheat': 'products/wheat_grains.png',
        'rice': 'products/basmati_rice.png',
        'tomato': 'products/tomatoes.png',
        'vegetable': 'products/tomatoes.png',
        'chilli': 'products/green_chilli.jpg',
        'bell_pepper': 'products/red_capsicum.jpg',
        'onion': 'products/onions.png',
        'potato': 'products/potatoes.png',
        'mango': 'products/mangoes.png',
        'fruit': 'products/apple.jpg',
        'apple': 'products/fresh_apple.jpg',
        'banana': 'products/banana_bunch.jpg',
        'grape': 'products/grapes_vineyard.jpg',
        'orange': 'products/orange_grove.jpg',
        'citrus': 'products/orange_grove.jpg',
        'corn': 'products/corn_field.jpg',
        'maize': 'products/corn_field.jpg',
        'sunflower': 'products/sunflower_crop.jpg',
        'soy': 'products/soybean_plant.jpg',
        'sugar': 'products/sugarcane_farm.jpg',
        'cane': 'products/sugarcane_farm.jpg',
        'barley': 'products/barley_grain.jpg',
        'millet': 'products/barley_grain.jpg',
        'mushroom': 'products/mushroom_farm.jpg',
        'honey': 'products/honey_bee_hive.jpg',
        'bee': 'products/honey_bee_hive.jpg',
        'dairy': 'products/dairy_cow.jpg',
        'cow': 'products/dairy_cow.jpg',
        'milk': 'products/dairy_cow.jpg',
        'poultry': 'products/poultry_chicken.jpg',
        'chicken': 'products/poultry_chicken.jpg',
        'goat': 'products/goat_farm.jpg',
        'animal': 'products/goat_farm.jpg',
        'cotton': 'products/cotton_bales.png',
        'fiber': 'products/cotton_bales.png',
        'fertilizer': 'products/liquid_fertilizer.png',
        'urea': 'products/fertilizer_organic.png',
        'growth': 'products/fertilizer_organic.png',
        'organic': 'products/fertilizer_organic.png',
        'humic': 'products/fertilizer_organic.png',
        'bio': 'products/fertilizer_organic.png',
        'tonic': 'products/liquid_fertilizer.png',
        'nutrient': 'products/liquid_fertilizer.png',
        'pesticide': 'products/pesticide_bottle.png',
        'insecticide': 'products/lab_research.png',
        'fungicide': 'products/lab_research.png',
        'herbicide': 'products/pesticide_bottle.png',
        'weed': 'products/pesticide_bottle.png',
        'killer': 'products/pesticide_bottle.png',
        'control': 'products/pesticide_bottle.png',
        'chemical': 'products/lab_research.png',
        'sucking': 'products/lab_research.png',
        'sprayer': 'products/sprayer.png',
        'pump': 'products/sprayer.png',
        'irrigation': 'products/drip_pipe.png',
        'pipe': 'products/drip_pipe.png',
        'drip': 'products/drip_pipe.png',
        'seed': 'products/seeds_packet.png',
        'hybrid': 'products/seeds_packet.png',
        'machinery': 'products/tractor_autonomous.png',
        'cultivator': 'products/cultivator.png',
        'tractor': 'products/tractor_autonomous.png',
        'tool': 'products/tools_set.png',
        'equipment': 'products/tools_set.png',
        'plough': 'products/cultivator.png',
        'drill': 'products/cultivator.png',
        'smart': 'products/smart_farm.png',
        'tech': 'products/smart_farm.png',
        'iot': 'products/smart_farm.png',
        'drone': 'products/agriculture_drone.jpg',
        'uav': 'products/agriculture_drone.jpg',
        'greenhouse': 'products/greenhouse_interior.jpg',
        'polyhouse': 'products/greenhouse_interior.jpg',
        'truck': 'products/farm_truck_pickup.jpg',
        'energy': 'products/wind_turbine_farm.jpg',
        'solar': 'products/wind_turbine_farm.jpg',
        'coconut': 'products/coconut_tree.jpg',
        'coco': 'products/coconut_tree.jpg',
        'tea': 'products/tea_plantation.jpg',
        'coffee': 'products/coffee_beans.jpg',
        'rubber': 'products/rubber_tapping.jpg',
        'latex': 'products/rubber_tapping.jpg',
        'turmeric': 'products/turmeric_powder.jpg',
        'haldi': 'products/turmeric_powder.jpg',
        'black_pepper': 'products/black_pepper.jpg',
        'pomegranate': 'products/pomegranate_fruit.jpg',
        'anar': 'products/pomegranate_fruit.jpg',
        'guava': 'products/guava_fruit.jpg',
        'papaya': 'products/papaya_tree.jpg',
        'ginger': 'products/ginger_root.jpg',
        'cauliflower': 'products/cauliflower_harvest.jpg',
        'cabbage': 'products/cabbage_field.jpg',
        'brinjal': 'products/eggplant_brinjal.jpg',
        'eggplant': 'products/eggplant_brinjal.jpg',
        'okra': 'products/okra_ladyfinger.jpg',
        'bhindi': 'products/okra_ladyfinger.jpg',
        'gourd': 'products/bottle_gourd.jpg',
        'bottle': 'products/bottle_gourd.jpg',
        'bitter': 'products/bitter_gourd.jpg',
        'karela': 'products/bitter_gourd.jpg',
        'pea': 'products/green_peas.jpg',
        'carrot': 'products/carrot_harvest.jpg',
        'melon': 'products/watermelon_field.jpg',
        'pineapple': 'products/pineapple_farm.jpg',
        'berry': 'products/strawberry_plant.jpg',
        'lemon': 'products/lemon_tree.jpg',
        'lime': 'products/lemon_tree.jpg',
        'flower': 'products/marigold_flower_field.jpg',
        'marigold': 'products/marigold_flower_field.jpg',
        'rose': 'products/rose_farming.jpg',
        'compost': 'products/organic_compost.jpg',
        'vermi': 'products/vermicompost_bed.jpg',
        'neem': 'products/neem_leaves.jpg',
        'aloe': 'products/aloe_vera_farm.jpg',
        'bamboo': 'products/bamboo_farm.jpg',
        'hydro': 'products/hydroponic_setup.jpg',
    }

    # Fallback images list
    fallback_images = [
        'products/liquid_fertilizer.png',
        'products/seeds_packet.png',
        'products/pesticide_bottle.png',
        'products/tools_set.png',
        'products/corn_field.jpg',
        'products/sunflower_crop.jpg',
        'products/dairy_cow.jpg',
        'products/tea_plantation.jpg',
        'products/coconut_tree.jpg',
        'products/organic_compost.jpg'
    ]

    products = Product.objects.all()  # pylint: disable=no-member
    print(f"Found {products.count()} products")
    stats = {'updated': 0, 'skipped': 0, 'errors': 0}

    for product in products:
        try:
            name_lower = product.name.lower()
            desc_lower = product.description.lower()
            target_image = None

            # Try to find a specific match
            for keyword, img_path in image_pool.items():
                if keyword in name_lower or keyword in desc_lower:
                    target_image = img_path
                    break

            # If no specific match, try category match
            if not target_image:
                cat_name = product.category.name.lower()
                if 'seed' in cat_name:
                    target_image = 'products/seeds_packet.png'
                elif 'fertilizer' in cat_name:
                    target_image = 'products/liquid_fertilizer.png'
                elif 'pesticide' in cat_name:
                    target_image = 'products/pesticide_bottle.png'
                elif 'machi' in cat_name:
                    target_image = 'products/cultivator.png'
                elif 'tool' in cat_name:
                    target_image = 'products/sprayer.png'

            # If still no match, pick a random high quality one
            if not target_image:
                target_image = secrets.choice(fallback_images)

            # Apply the image
            if target_image:
                if product.image != target_image:
                    product.image = target_image
                    product.save()
                    stats['updated'] += 1
                    print(f"Updated: {product.name} -> {target_image}")
                else:
                    stats['skipped'] += 1
                    print(f"Skipped: {product.name} (already has {target_image})")
            else:
                stats['skipped'] += 1
                print(f"Skipped: {product.name} (no suitable image)")

        except (ValueError, AttributeError) as e:
            stats['errors'] += 1
            print(f"Error processing {product.name}: {e}")

    print(f"\nSuccessfully updated {stats['updated']} products, "
          f"skipped {stats['skipped']}, encountered {stats['errors']} errors.")


if __name__ == '__main__':
    try:
        populate_product_images()
    except (ValueError, OSError) as e:
        print(f"Error: {e}")
