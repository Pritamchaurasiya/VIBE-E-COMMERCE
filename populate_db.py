"""
Script to populate the database with realistic Agri B2B data.
"""
# pylint: disable=no-member, wrong-import-position
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils.text import slugify
from store.models import Category, Vendor, Product, Order, OrderItem

CAT_SEEDS = 'Seeds'
CAT_AGROCHEMICALS = 'Agrochemicals'
CAT_NUTRIENTS = 'Nutrients'
CAT_AGRI_TOOLS = 'Agri Tools'
CAT_ANIMAL_NUTRITION = 'Animal Nutrition'

def populate():
    """
    Populate database with Categories, Vendors, and Products tailored for Indian Agri-Retailers.
    """
    # Clear existing data
    print("Clearing existing data...")
    OrderItem.objects.all().delete()
    Order.objects.all().delete()
    Product.objects.all().delete()
    Category.objects.all().delete()
    Vendor.objects.all().delete()

    # 1. Categories
    print("Creating Categories...")

    category_list = {
        CAT_SEEDS: 'field-crops-vegetables',
        CAT_AGROCHEMICALS: 'pesticides-herbicides-fungicides',
        CAT_NUTRIENTS: 'bio-fertilizers-crop-nutrition',
        CAT_AGRI_TOOLS: 'sprayers-cutters-tools',
        CAT_ANIMAL_NUTRITION: 'cattle-feed-fish-feed'
    }

    categories = {}
    for name, slug in category_list.items():
        cat, _ = Category.objects.get_or_create(name=name, slug=slug)
        categories[name] = cat

    # 2. Vendors (Top Indian Brands)
    print("Creating Vendors...")
    vendors_data = [
        ('UPL Ltd', 'upl', 'Mumbai'),
        ('Godrej Agrovet', 'godrej-agrovet', 'Mumbai'),
        ('Corteva Agriscience', 'corteva', 'Hyderabad'),
        ('Syngenta India', 'syngenta', 'Pune'),
        ('Bayer CropScience', 'bayer', 'Thane'),
        ('Dhanuka Agritech', 'dhanuka', 'Gurgaon'),
        ('Tata Rallis', 'tata-rallis', 'Mumbai')
    ]

    vendors = {}
    for name, slug, city in vendors_data:
        ven, _ = Vendor.objects.get_or_create(name=name, slug=slug, city=city, created_by=None)
        vendors[slug] = ven

    # 3. Products Catalog
    print("Creating Products...")

    products_data = [
        # Seeds
        {
            'cat': CAT_SEEDS, 'ven': 'syngenta', 'name': 'Syngenta 6242 Tomato Seeds',
            'price': 850.00, 'mrp': 1100.00,
            'brand': 'Syngenta', 'tech': 'Hybrid Tomato F1', 'crops': 'Tomato',
            'usage': 'Seed rate: 40-50g per acre. Transplanting 25 days after sowing.',
            'safety': 'Store in cool, dry place. Treated with Thiram.',
            'desc': 'High-yielding hybrid tomato variety, good heat set, disease resistant.'
        },
        {
            'cat': CAT_SEEDS, 'ven': 'bayer', 'name': 'Proagro 5222 Mustard Seeds',
            'price': 420.00, 'mrp': 550.00,
            'brand': 'Proagro (Bayer)', 'tech': 'Mustard Hybrid', 'crops': 'Mustard (Sarson)',
            'usage': 'Sowing time: Oct-Nov. Seed rate: 1.5 kg/acre.',
            'safety': 'Use gloves while handling treated seeds.',
            'desc': 'Bold siliqua, high oil content, and tolerant to white rust.'
        },
        {
            'cat': CAT_SEEDS, 'ven': 'corteva', 'name': 'Pioneer 30B11 Wheat Seeds',
            'price': 1200.00, 'mrp': 1450.00,
            'brand': 'Pioneer', 'tech': 'High Yielding Wheat Variety', 'crops': 'Wheat',
            'usage': 'Irrigated timing. Depth of sowing 5-6 cm.',
            'safety': 'Fungicide treated.',
            'desc': 'Excellent grain quality, resistant to rusts.'
        },

        # Agrochemicals
        {
            'cat': CAT_AGROCHEMICALS, 'ven': 'upl', 'name': 'Saaf Fungicide',
            'price': 480.00, 'mrp': 600.00,
            'brand': 'UPL', 'tech': 'Carbendazim 12% + Mancozeb 63% WP',
            'crops': 'Paddy, Groundnut, Potato',
            'usage': 'Foliar Spray: 2g per liter of water.',
            'safety': 'Wear mask and gloves during spraying. Keep away from water bodies.',
            'desc': ('Systemic and contact fungicide, effective against '
                     'leaf spot, blast, and rust.')
        },
        {
            'cat': CAT_AGROCHEMICALS, 'ven': 'syngenta', 'name': 'Amistar Top',
            'price': 1850.00, 'mrp': 2200.00,
            'brand': 'Syngenta', 'tech': 'Azoxystrobin 18.2% + Difenoconazole 11.4% SC',
            'crops': 'Wheat, Rice, Corn',
            'usage': '200ml per acre. Apply at booting/heading stage.',
            'safety': 'Toxic to fish and aquatic invertebrates.',
            'desc': 'Broad spectrum fungicide controlling yellow rust and sheath blight.'
        },
        {
            'cat': CAT_AGROCHEMICALS, 'ven': 'bayer', 'name': 'Confidor Insecticide',
            'price': 350.00, 'mrp': 450.00,
            'brand': 'Bayer', 'tech': 'Imidacloprid 17.8% SL', 'crops': 'Cotton, Chilli, Tomato',
            'usage': '0.5ml per liter of water for sucking pests.',
            'safety': 'Highly toxic to bees. Do not spray during flowering.',
            'desc': 'Systemic insecticide for control of aphids, jassids, and whiteflies.'
        },
        {
            'cat': CAT_AGROCHEMICALS, 'ven': 'dhanuka', 'name': 'Targa Super Herbicide',
            'price': 780.00, 'mrp': 950.00,
            'brand': 'Dhanuka', 'tech': 'Quizalofop Ethyl 5% EC',
            'crops': 'Soybean, Cotton, Groundnut',
            'usage': '400ml per acre. Apply when weeds are at 2-3 leaf stage.',
            'safety': 'Avoid drift to adjacent cereal crops.',
            'desc': 'Selective post-emergence herbicide for narrow-leaf weeds.'
        },

        # Nutrients
        {
            'cat': CAT_NUTRIENTS, 'ven': 'godrej-agrovet', 'name': 'Double Yield Stimulant',
            'price': 950.00, 'mrp': 1200.00,
            'brand': 'Godrej', 'tech': 'Homobrassinolide 0.04%', 'crops': 'All Veg and Fruit Crops',
            'usage': 'Spray 2-3 times during flowering and fruit setting.',
            'safety': 'Keep out of reach of children.',
            'desc': 'Increases yield, improves quality and quantity of produce.'
        },
        {
            'cat': CAT_NUTRIENTS, 'ven': 'upl', 'name': 'Macarena Bio-Stimulant',
            'price': 1100.00, 'mrp': 1350.00,
            'brand': 'UPL', 'tech': 'Seaweed Extract based', 'crops': 'Vegetables, Fruits',
            'usage': 'Foliar application: 2ml/liter.',
            'safety': 'Organic product, safe to handle.',
            'desc': 'Promotes root growth and stress tolerance.'
        },

        # Agri Tools
        {
            'cat': CAT_AGRI_TOOLS, 'ven': 'tata-rallis', 'name': 'Battery Sprayer 16L',
            'price': 2800.00, 'mrp': 3500.00,
            'brand': 'Rallis', 'tech': '12V 8AH Battery, Double Motor', 'crops': 'All',
            'usage': 'Charge battery fully before first use (8 hours).',
            'safety': 'Wear protective gear while spraying chemicals.',
            'desc': 'High pressure battery operated sprayer for ease of use.'
        },
        {
            'cat': CAT_AGRI_TOOLS, 'ven': 'godrej-agrovet', 'name': 'Brush Cutter 4-Stroke',
            'price': 12500.00, 'mrp': 16000.00,
            'brand': 'Stihl / Godrej', 'tech': '35cc Engine, Backpack Type', 'crops': 'Field crops',
            'usage': 'Use fresh petrol. Check oil level before start.',
            'safety': 'Wear eye protection and sturdy boots.',
            'desc': 'Heavy duty brush cutter for weed management and harvesting.'
        },

        # Animal Nutrition
        {
            'cat': CAT_ANIMAL_NUTRITION, 'ven': 'godrej-agrovet', 'name': 'Bovizyme Cattle Feed',
            'price': 1200.00, 'mrp': 1400.00,
            'brand': 'Godrej', 'tech': 'Probiotics + Minerals', 'crops': 'Cattle',
            'usage': 'Mix 50g daily in feed.',
            'safety': 'Store in dry place.',
            'desc': 'Improves milk yield and fat content in dairy cattle.'
        }
    ]

    for p in products_data:
        cat = categories[p['cat']]
        ven = vendors[p['ven']]

        slug = slugify(f"{p['brand']}-{p['name']}")

        if not Product.objects.filter(slug=slug).exists():
            Product.objects.create(
                category=cat,
                vendor=ven,
                name=p['name'],
                slug=slug,
                description=p['desc'],
                short_description=p['desc'],
                price=p['price'],
                mrp=p['mrp'],
                brand=p['brand'],
                technical_name=p['tech'],
                target_crops=p['crops'],
                usage_instructions=p['usage'],
                safety_guidelines=p['safety']
            )
            print(f"Added: {p['name']}")

    print("Database populated successfully with Agri B2B data!")

if __name__ == '__main__':
    populate()
