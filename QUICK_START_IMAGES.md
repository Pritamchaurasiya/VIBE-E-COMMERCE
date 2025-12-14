# Quick Start - Adding Images

## Prerequisites

Make sure you have Django set up and running.

```bash
python manage.py runserver
```

## Adding Crop Images

1. Place images in `media/crops/` folder
2. Run the script:

```bash
python add_images_script.py
```

## Adding Disease Images

1. Place images in `media/diseases/` folder
2. Run the same script above

## Adding Product Gallery Images

1. Place images in `media/products/gallery/` folder
2. Run the script

## Bulk Population

To bulk populate all product images:

```bash
python bulk_image_populate.py
```

## Checking Coverage

To check image coverage:

```bash
python check_coverage.py
```
