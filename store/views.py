"""
Views for the store app handling frontpage, shop, cart, and other pages.
"""
# pylint: disable=no-member,too-many-lines

import csv
import json
import uuid

import bleach
import stripe

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db import models
from django.db.models import Q, Sum, Count
from django.db.models.functions import TruncDate
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.utils.text import slugify
from django.views.decorators.http import require_POST

from .cart import Cart
from .forms import (
    OrderForm, VendorRegistrationForm, ReviewForm, UserUpdateForm, ProfileUpdateForm
)
from .models import (
    Product, Vendor, Category, Contact, Order, OrderItem, Profile, Wishlist,
    Coupon, FlashSale, BulkOrder, InventoryLog, Deal, ProductComparison,
    AdvancedSearch, AnalyticsEvent, VendorAnalytics, Notification,
    Subscription, BuyerInquiry, RFQQuote, VendorVerification, RFQ,
    AuditLog, SiteSettings, TradeEvent, Crop
)
from .utils import sanitize_csv_field

stripe.api_key = settings.STRIPE_API_KEY_HIDDEN

# Constants
ERROR_INVALID_REQUEST = 'Invalid request'

def frontpage(request):
    """
    Render the frontpage with featured vendors, products, flash sales, and more.
    Enhanced homepage with dynamic content for better user engagement.
    """
    now = timezone.now()

    # Featured products (top rated or most popular)
    products = Product.objects.select_related('category', 'vendor').filter(
        is_active=True
    ).order_by('-created_at')[:8]

    # Trending products (based on order count in last 30 days)
    trending_products = Product.objects.select_related('category', 'vendor').filter(
        is_active=True,
        items__order__created_at__gte=now - timezone.timedelta(days=30)
    ).annotate(
        order_count=models.Count('items')
    ).order_by('-order_count').distinct()[:6]

    # New arrivals (products added in last 14 days)
    new_arrivals = Product.objects.select_related('category', 'vendor').filter(
        is_active=True,
        created_at__gte=now - timezone.timedelta(days=14)
    ).order_by('-created_at')[:6]

    # Active flash sales
    active_flash_sales = FlashSale.objects.filter(
        is_active=True,
        start_time__lte=now,
        end_time__gte=now
    ).prefetch_related(
        'products', 'products__category', 'products__vendor'
    ).order_by('end_time')[:4]

    # Active deals
    active_deals = Deal.objects.filter(
        is_active=True,
        start_date__lte=now,
        end_date__gte=now
    ).order_by('-discount_value')[:3]

    # On sale products (where MRP > price)
    on_sale_products = Product.objects.select_related('category', 'vendor').filter(
        is_active=True,
        mrp__gt=models.F('price')
    ).order_by('-created_at')[:6]

    # Vendors
    vendors = Vendor.objects.all()[:6]
    categories = Category.objects.all()

    # Premium products (high trending score)
    premium_products = Product.objects.select_related('category', 'vendor').filter(
        is_active=True,
        trending_score__gte=80
    ).order_by('-trending_score')[:8]

    # Crops - fetch top crops
    crops = Crop.objects.all().order_by('order')[:12]

    # Statistics for the homepage
    stats = {
        'total_products': Product.objects.filter(is_active=True).count(),
        'total_vendors': Vendor.objects.count(),
        'total_categories': Category.objects.count(),
        'total_orders': Order.objects.filter(paid=True).count(),
        'total_crops': Crop.objects.count(),
    }

    # Superfoods products
    superfood_products = Product.objects.select_related('category', 'vendor').filter(
        is_active=True,
        category__name__iexact='Superfoods'
    ).order_by('-trending_score')[:8]

    # Machinery products
    machinery_products = Product.objects.select_related('category', 'vendor').filter(
        is_active=True,
        category__name__iexact='Machinery'
    ).order_by('-price')[:4]

    context = {
        'products': products,
        'trending_products': trending_products if trending_products.exists() else products[:6],
        'premium_products': premium_products,
        'superfood_products': superfood_products,
        'machinery_products': machinery_products,
        'new_arrivals': new_arrivals if new_arrivals.exists() else products[:6],

        'on_sale_products': on_sale_products,
        'active_flash_sales': active_flash_sales,
        'active_deals': active_deals,
        'vendors': vendors,
        'categories': categories,
        'crops': crops,
        'stats': stats,
    }
    return render(request, 'index.html', context)


def _apply_price_filter(products, min_price, max_price):
    """Apply price range filter to queryset."""
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass
    return products


def _apply_rating_filter(products, rating_filter):
    """Apply rating filter to queryset."""
    if not rating_filter:
        return products
    try:
        min_rating = int(rating_filter)
        if 1 <= min_rating <= 5:
            products = products.annotate(
                avg_rating=models.Avg('reviews__rating')
            ).filter(avg_rating__gte=min_rating)
    except ValueError:
        pass
    return products


def _apply_shop_filters(products, params):
    """Apply search and filter parameters to product queryset."""
    query = params.get('query', '')
    category_slug = params.get('category_slug', '')
    vendor_slug = params.get('vendor_slug', '')
    in_stock_only = params.get('in_stock_only', '')
    on_sale_only = params.get('on_sale_only', '')

    # Search filtering
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(brand__icontains=query) |
            Q(technical_name__icontains=query) |
            Q(target_crops__icontains=query)
        )

    # Category filtering
    if category_slug:
        products = products.filter(category__slug=category_slug)

    # Vendor filtering
    if vendor_slug:
        products = products.filter(vendor__slug=vendor_slug)

    # Price range filtering
    products = _apply_price_filter(
        products, params.get('min_price', ''), params.get('max_price', '')
    )

    # Rating filtering
    products = _apply_rating_filter(products, params.get('rating_filter', ''))

    # Stock filtering
    if in_stock_only:
        products = products.filter(stock_quantity__gt=0)

    # On sale filtering
    if on_sale_only:
        products = products.filter(mrp__gt=models.F('price'))

    return products


def _apply_shop_sorting(products, sort):
    """Apply sorting to product queryset."""
    sort_options = {
        'name': 'name',
        'price_low': 'price',
        'price_high': '-price',
        'newest': '-created_at',
        'rating': '-avg_rating',
        'popularity': '-order_count',
    }

    sort_key = sort_options.get(sort, '-created_at')

    if sort == 'rating':
        return products.annotate(
            avg_rating=models.Avg('reviews__rating')
        ).order_by(sort_key, '-created_at')

    if sort == 'popularity':
        return products.annotate(
            order_count=models.Count('items')
        ).order_by(sort_key, '-created_at')

    return products.order_by(sort_key)


def shop(request):
    """
    Render the shop page with products, advanced search, filtering, sorting, and pagination.
    """
    products = Product.objects.select_related('category', 'vendor').filter(is_active=True)

    # Get categories with product counts
    categories = Category.objects.annotate(
        product_count=models.Count('products', filter=models.Q(products__is_active=True))
    ).filter(product_count__gt=0)

    vendors = Vendor.objects.all()

    # Get filter parameters
    params = {
        'query': request.GET.get('q', ''),
        'category_slug': request.GET.get('category', ''),
        'vendor_slug': request.GET.get('vendor', ''),
        'min_price': request.GET.get('min_price', ''),
        'max_price': request.GET.get('max_price', ''),
        'rating_filter': request.GET.get('rating', ''),
        'in_stock_only': request.GET.get('in_stock', ''),
        'on_sale_only': request.GET.get('on_sale', ''),
    }
    sort = request.GET.get('sort', 'relevance')
    page = request.GET.get('page', 1)

    # Apply filters and sorting
    products = _apply_shop_filters(products, params)
    products = _apply_shop_sorting(products, sort)

    # Get active flash sales
    now = timezone.now()
    active_flash_sales = FlashSale.objects.filter(
        is_active=True,
        start_time__lte=now,
        end_time__gte=now
    ).order_by('-discount_percentage')[:3]

    # Pagination
    paginator = Paginator(products, 12)  # 12 products per page
    products = paginator.get_page(page)

    context = {
        'products': products,
        'categories': categories,
        'vendors': vendors,
        'query': params['query'],
        'category_slug': params['category_slug'],
        'vendor_slug': params['vendor_slug'],
        'min_price': params['min_price'],
        'max_price': params['max_price'],
        'sort': sort,
        'rating_filter': params['rating_filter'],
        'in_stock_only': params['in_stock_only'],
        'on_sale_only': params['on_sale_only'],
        'flash_sales': active_flash_sales,
    }
    return render(request, 'shop.html', context)



def quick_view(request, product_id):
    """
    Render a partial view for product quick view modal.
    """
    product = get_object_or_404(Product.objects.select_related('category', 'vendor'), id=product_id)
    
    context = {
        'product': product,
    }
    return render(request, 'partials/quick_view_modal.html', context)


def vendor_register(request):
    """Render the vendor registration page and handle signup."""
    if request.method == 'POST':
        form = VendorRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            # Check if email exists
            email = form.cleaned_data['email']
            if User.objects.filter(email=email).exists():
                return render(request, 'vendor_register.html', {
                    'form': form,
                    'error': 'Email already registered'
                })

            # Simple unique username generation
            username = f"vendor_{uuid.uuid4().hex[:8]}"
            password = form.cleaned_data['password']

            user = User.objects.create_user(username=username, email=email, password=password)
            user.first_name = bleach.clean(form.cleaned_data['name'])
            user.save()

            # Create Vendor
            vendor = form.save(commit=False)
            vendor.created_by = user

            # Sanitize user input
            vendor.name = bleach.clean(vendor.name)
            vendor.city = bleach.clean(vendor.city)

            # Slug generation
            vendor.slug = slugify(vendor.name) + "-" + str(uuid.uuid4().hex[:4])

            vendor.save()

            login(request, user)

            return redirect('frontpage')
    else:
        form = VendorRegistrationForm()

    return render(request, 'vendor_register.html', {'form': form})

def vendor_detail(request, slug):
    """Render the vendor detail page."""
    vendor = get_object_or_404(Vendor, slug=slug)
    products = vendor.products.select_related('category').all()

    context = {
        'vendor': vendor,
        'products': products
    }
    return render(request, 'vendor_detail.html', context)

def product_detail(request, slug, category_slug=None):
    """Render the product detail page with reviews."""
    product = get_object_or_404(
        Product.objects.select_related('category', 'vendor'), slug=slug
    )
    related_products = Product.objects.select_related('category', 'vendor').filter(
        category=product.category
    ).exclude(id=product.id)[0:4]

    # Get reviews
    reviews = product.reviews.all().order_by('-created_at')
    review_count = reviews.count()
    avg_rating = reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0

    # Rating distribution
    rating_counts = {}
    for i in range(1, 6):
        rating_counts[i] = reviews.filter(rating=i).count()

    # Check if user has already reviewed this product
    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()

    # Handle review submission
    review_form = None
    if request.user.is_authenticated and not user_review:
        if request.method == 'POST' and 'review_submit' in request.POST:
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.product = product
                review.user = request.user
                # Sanitize user input
                review.title = bleach.clean(review.title)
                review.comment = bleach.clean(review.comment)
                # Check if user has purchased this product
                review.is_verified_purchase = OrderItem.objects.filter(
                    order__user=request.user,
                    product=product
                ).exists()
                review.save()
                return redirect('product_detail', slug=slug)
        else:
            review_form = ReviewForm()

    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'review_count': review_count,
        'avg_rating': avg_rating,
        'rating_counts': rating_counts,
        'user_review': user_review,
        'review_form': review_form
    }
    return render(request, 'product_detail.html', context)

def vendor_list(request):
    """Render the vendor list page."""
    vendors = Vendor.objects.all()
    return render(request, 'vendor_list.html', {'vendors': vendors})

@require_POST
def cart_add(request, product_id):
    """Add a product to the cart."""
    cart = Cart(request)
    cart.add(product_id)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': len(cart),
            'cart_total_cost': cart.get_total_cost()
        })

    return redirect('cart_detail')

@require_POST
def cart_remove(request, product_id):
    """Remove a product from the cart."""
    cart = Cart(request)
    cart.remove(product_id)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': len(cart),
            'cart_total_cost': cart.get_total_cost()
        })

    return redirect('cart_detail')

@require_POST
def cart_update(request, product_id, action):
    """Update quantity of a product in the cart."""
    cart = Cart(request)
    if action == 'increment':
        cart.add(product_id, 1, True)
    else:
        cart.add(product_id, -1, True)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': len(cart),
            'cart_total_cost': cart.get_total_cost()
        })

    return redirect('cart_detail')

def cart_detail(request):
    """Render the cart page."""
    cart = Cart(request)
    return render(request, 'cart.html', {'cart': cart})


def checkout(request):
    """Render the checkout page and handle order creation."""
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            total_price = cart.get_total_cost()

            order = form.save(commit=False)

            if request.user.is_authenticated:
                order.user = request.user
            else:
                order.user = None

            order.paid_amount = total_price

            # Sanitize user input
            order.first_name = bleach.clean(order.first_name)
            order.last_name = bleach.clean(order.last_name)
            order.email = bleach.clean(order.email)
            order.address = bleach.clean(order.address)
            order.zipcode = bleach.clean(order.zipcode)
            order.place = bleach.clean(order.place)
            order.phone = bleach.clean(order.phone)

            order.save()

            for item in cart:
                product = item['product']
                quantity = int(item['quantity'])
                price = product.price * quantity
                OrderItem.objects.create(
                    order=order, product=product, price=price,
                    quantity=quantity, vendor=product.vendor
                )

            cart.clear()

            return redirect('success')
    else:
        form = OrderForm()

    return render(request, 'checkout.html', {
        'cart': cart,
        'form': form,
        'pub_key': settings.STRIPE_API_KEY_PUBLISHABLE
    })


def success(request):
    """Render the success page."""
    cart = Cart(request)
    cart.clear()

    return render(request, 'success.html')


@login_required
def order_detail(request, order_id):
    """Render the details of a specific order."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_detail.html', {'order': order})



def contact(request):
    """Render the contact page."""
    if request.method == 'POST':
        name = bleach.clean(request.POST.get('name'))
        email = bleach.clean(request.POST.get('email'))
        message = bleach.clean(request.POST.get('message'))

        Contact.objects.create(name=name, email=email, message=message)
        return redirect('frontpage')

    return render(request, 'contact.html')


def about(request):
    """Render the about page."""
    return render(request, 'about.html')

def signup(request):
    """Render the signup page and handle registration."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('frontpage')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    """Render the login page and handle authentication."""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('frontpage')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    """Handle user logout."""
    logout(request)
    return redirect('frontpage')

@login_required
def dashboard(request):
    """Render the user dashboard."""
    orders = Order.objects.filter(user=request.user).prefetch_related(
        'items__product'
    ).order_by('-created_at')
    # Use existing Profile or create one if missing
    if not hasattr(request.user, 'profile'):
        Profile.objects.create(user=request.user, shop_name=f"{request.user.username}'s Shop")

    pending_orders_count = orders.exclude(status='delivered').exclude(status='cancelled').count()

    return render(request, 'dashboard.html', {
        'orders': orders,
        'pending_orders_count': pending_orders_count
    })

@login_required
@require_POST
def wishlist_add(request, product_id):
    """Add a product to the user's wishlist."""
    product = get_object_or_404(Product, id=product_id)
    _, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'created': created,
            'message': 'Added to wishlist' if created else 'Already in wishlist'
        })

    return redirect('product_detail', slug=product.slug)

@login_required
@require_POST
def wishlist_remove(request, product_id):
    """Remove a product from the user's wishlist."""
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.filter(user=request.user, product=product).delete()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Removed from wishlist'
        })

    return redirect('wishlist_view')

@login_required
def wishlist_view(request):
    """Display the user's wishlist."""
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'wishlist.html', {
        'wishlist_items': wishlist_items
    })


def search_api(request):
    """
    API endpoint for live search suggestions.
    Returns JSON with matching products.
    """
    query = request.GET.get('q', '').strip()
    results = []

    if len(query) >= 2:
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(brand__icontains=query) |
            Q(category__name__icontains=query)
        ).select_related('category')[:10]

        for product in products:
            results.append({
                'id': product.id,
                'name': product.name,
                'slug': product.slug,
                'price': float(product.price),
                'category': product.category.name,
                'image': product.image.url if product.image else None,
                'in_stock': product.is_in_stock
            })

    return JsonResponse({'results': results})


@require_POST
def apply_coupon(request):
    """
    API endpoint to validate and apply a coupon code.
    """
    try:
        data = json.loads(request.body)
        code = data.get('code', '').strip().upper()
        cart_total = data.get('cart_total', 0)

        if not code:
            return JsonResponse({'success': False, 'error': 'Please enter a coupon code'})

        try:
            coupon = Coupon.objects.get(code__iexact=code)
        except Coupon.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Invalid coupon code'})

        # Validate coupon
        now = timezone.now()
        if not coupon.is_active:
            return JsonResponse({'success': False, 'error': 'This coupon is no longer active'})

        if coupon.used_count >= coupon.max_uses:
            return JsonResponse({
                'success': False,
                'error': 'This coupon has reached its usage limit'
            })

        if now < coupon.valid_from:
            return JsonResponse({'success': False, 'error': 'This coupon is not yet valid'})

        if now > coupon.valid_until:
            return JsonResponse({'success': False, 'error': 'This coupon has expired'})

        if float(cart_total) < float(coupon.min_order_value):
            return JsonResponse({
                'success': False,
                'error': f'Minimum order value of ₹{coupon.min_order_value} required'
            })

        # Calculate discount
        if coupon.discount_type == 'percent':
            discount = float(cart_total) * (float(coupon.discount_value) / 100)
        else:
            discount = float(coupon.discount_value)

        # Don't allow discount more than cart total
        discount = min(discount, float(cart_total))

        return JsonResponse({
            'success': True,
            'code': coupon.code,
            'discount_type': coupon.discount_type,
            'discount_value': float(coupon.discount_value),
            'discount_amount': round(discount, 2),
            'message': f'Coupon applied! You save ₹{round(discount, 2)}'
        })

    except json.JSONDecodeError:
        return JsonResponse(
            {'success': False, 'error': ERROR_INVALID_REQUEST}, status=400
        )


def product_compare(request):
    """
    Compare multiple products side by side.
    """
    product_ids = request.GET.getlist('products')
    products = Product.objects.filter(id__in=product_ids).select_related('vendor', 'category')

    return render(request, 'product_compare.html', {
        'products': products
    })


def get_recommendations(_request, product_id):
    """
    Simple recommendation engine based on:
    1. Same category
    2. Same vendor
    3. Similar price range
    """
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'recommendations': []})

    # Get products in same category
    category_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]

    # Get products from same vendor
    vendor_products = Product.objects.filter(
        vendor=product.vendor,
        is_active=True
    ).exclude(id=product.id).exclude(id__in=category_products)[:2]

    # Get products in similar price range (±20%)
    price_min = float(product.price) * 0.8
    price_max = float(product.price) * 1.2
    price_products = Product.objects.filter(
        price__gte=price_min,
        price__lte=price_max,
        is_active=True
    ).exclude(id=product.id).exclude(
        id__in=category_products
    ).exclude(id__in=vendor_products)[:2]

    # Combine recommendations
    all_recommendations = list(category_products) + list(vendor_products) + list(price_products)

    recommendations = [{
        'id': p.id,
        'name': p.name,
        'slug': p.slug,
        'price': float(p.price),
        'image': p.image.url if p.image else None,
        'category': p.category.name,
        'vendor': p.vendor.name
    } for p in all_recommendations[:8]]

    return JsonResponse({'recommendations': recommendations})


def update_order_status(request, order_id):
    """
    Update order status (for admin/vendor use).
    """
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

    try:
        order = Order.objects.get(id=order_id)
        data = json.loads(request.body)
        new_status = data.get('status')

        valid_statuses = ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']
        if new_status not in valid_statuses:
            return JsonResponse({'success': False, 'error': 'Invalid status'})

        order.status = new_status
        order.save()

        return JsonResponse({
            'success': True,
            'message': f'Order #{order.id} status updated to {new_status}'
        })

    except Order.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Order not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse(
            {'success': False, 'error': ERROR_INVALID_REQUEST}, status=400
        )


@login_required
def vendor_dashboard(request):
    """
    Dashboard for vendors to manage their products and orders.
    """
    try:
        vendor = request.user.vendor
    except Vendor.DoesNotExist:
        return redirect('frontpage')

    # Get vendor's products
    products = Product.objects.filter(vendor=vendor).order_by('-created_at')
    products_count = products.count()

    # Product stock analytics
    active_products_count = products.filter(is_active=True, stock_quantity__gt=0).count()
    low_stock_count = products.filter(
        stock_quantity__gt=0,
        stock_quantity__lte=models.F('low_stock_threshold')
    ).count()
    out_of_stock_count = products.filter(stock_quantity=0).count()

    # Get order items for this vendor's products
    order_items = OrderItem.objects.filter(
        product__vendor=vendor
    ).select_related('order', 'product').order_by('-order__created_at')[:20]

    # Calculate total revenue
    total_revenue = order_items.filter(
        order__paid=True
    ).aggregate(total=Sum('price'))['total'] or 0

    # Get pending orders count
    pending_orders = order_items.filter(
        order__status='pending'
    ).values('order').distinct().count()

    total_orders = order_items.values('order').distinct().count()

    # Get bulk orders
    bulk_orders = BulkOrder.objects.filter(vendor=vendor).order_by('-created_at')[:10]

    # Get inventory logs
    inventory_logs = InventoryLog.objects.filter(
        product__vendor=vendor
    ).order_by('-created_at')[:20]

    # Get buyer inquiries for this vendor
    inquiries = BuyerInquiry.objects.filter(
        vendor=vendor
    ).select_related('buyer', 'product').order_by('-created_at')[:20]

    # Count new inquiries
    new_inquiries_count = BuyerInquiry.objects.filter(
        vendor=vendor, status='new'
    ).count()

    # Get RFQ quotes submitted by this vendor
    vendor_quotes = RFQQuote.objects.filter(
        vendor=vendor
    ).select_related('rfq', 'rfq__buyer').order_by('-created_at')[:20]

    # Top products by orders
    top_products = Product.objects.filter(vendor=vendor).annotate(
        order_count=models.Count('items')
    ).order_by('-order_count')[:5]

    context = {
        'vendor': vendor,
        'products': products,
        'products_count': products_count,
        'order_items': order_items,
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'bulk_orders': bulk_orders,
        'inventory_logs': inventory_logs,
        # New context for enhanced dashboard
        'inquiries': inquiries,
        'new_inquiries_count': new_inquiries_count,
        'vendor_quotes': vendor_quotes,
        'top_products': top_products,
        'active_products_count': active_products_count,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
    }
    return render(request, 'vendor_dashboard.html', context)



def flash_sales(request):
    """
    Display active flash sales.
    """
    now = timezone.now()
    active_sales = FlashSale.objects.filter(
        is_active=True,
        start_time__lte=now,
        end_time__gte=now
    ).prefetch_related('products')

    upcoming_sales = FlashSale.objects.filter(
        is_active=True,
        start_time__gt=now
    ).prefetch_related('products')[:5]

    context = {
        'active_sales': active_sales,
        'upcoming_sales': upcoming_sales,
    }
    return render(request, 'flash_sales.html', context)


@login_required
@require_POST
def create_bulk_order(request):
    """
    Create a bulk order request.
    """
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = data.get('quantity')
        requested_price = data.get('requested_price')
        notes = bleach.clean(data.get('notes', ''))

        product = Product.objects.get(id=product_id)

        new_bulk_order = BulkOrder.objects.create(
            user=request.user,
            product=product,
            vendor=product.vendor,
            quantity=quantity,
            requested_price=requested_price,
            notes=notes
        )

        return JsonResponse({
            'success': True,
            'message': 'Bulk order request submitted successfully!',
            'order_id': new_bulk_order.id
        })

    except Product.DoesNotExist:
        return JsonResponse(
            {'success': False, 'error': 'Product not found'},
            status=404
        )
    except json.JSONDecodeError:
        return JsonResponse(
            {'success': False, 'error': ERROR_INVALID_REQUEST},
            status=400
        )


# ============================================================================
# ADMIN PANEL VIEWS
# ============================================================================


def staff_required(view_func):
    """Decorator to require staff access."""
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapped


@staff_required
def admin_dashboard(request):
    """
    Comprehensive admin dashboard with stats and analytics.
    """
    now = timezone.now()
    thirty_days_ago = now - timezone.timedelta(days=30)

    # Calculate stats
    total_revenue = Order.objects.filter(
        paid=True,
        created_at__gte=thirty_days_ago
    ).aggregate(total=Sum('paid_amount'))['total'] or 0

    stats = {
        'total_revenue': f"₹{total_revenue:,.0f}",
        'total_orders': Order.objects.count(),
        'total_products': Product.objects.count(),
        'total_vendors': Vendor.objects.count(),
        'total_users': User.objects.count(),
        'pending_orders': Order.objects.filter(status='pending').count(),
        'low_stock_products': Product.objects.filter(
            stock_quantity__lte=models.F('low_stock_threshold')
        ).count(),
        'pending_verifications': VendorVerification.objects.filter(
            status='pending'
        ).count(),
        'new_inquiries': BuyerInquiry.objects.filter(status='new').count(),
        'open_rfqs': RFQ.objects.filter(status='open').count(),
    }

    # Recent orders
    recent_orders = Order.objects.select_related('user').order_by(
        '-created_at'
    )[:10]

    # Top products by order count
    top_products = Product.objects.annotate(
        sales_count=models.Count('items')
    ).order_by('-sales_count')[:5]

    # Recent activity from audit log
    recent_activity = AuditLog.objects.select_related('user').order_by(
        '-created_at'
    )[:10]

    context = {
        'stats': stats,
        'recent_orders': recent_orders,
        'top_products': top_products,
        'recent_activity': recent_activity,
    }
    return render(request, 'admin_dashboard.html', context)


@staff_required
def admin_rfq_list(request):
    """
    List and manage RFQs.
    """
    status_filter = request.GET.get('status', '')
    rfqs = RFQ.objects.select_related('buyer', 'category').prefetch_related(
        'quotes'
    ).order_by('-created_at')

    if status_filter:
        rfqs = rfqs.filter(status=status_filter)

    paginator = Paginator(rfqs, 20)
    page = request.GET.get('page', 1)
    rfqs = paginator.get_page(page)

    context = {
        'rfqs': rfqs,
        'status_filter': status_filter,
    }
    return render(request, 'admin/rfq_list.html', context)


@staff_required
def admin_inquiry_list(request):
    """
    List and manage buyer inquiries.
    """
    status_filter = request.GET.get('status', '')
    inquiries = BuyerInquiry.objects.select_related(
        'buyer', 'vendor', 'product'
    ).order_by('-created_at')

    if status_filter:
        inquiries = inquiries.filter(status=status_filter)

    paginator = Paginator(inquiries, 20)
    page = request.GET.get('page', 1)
    inquiries = paginator.get_page(page)

    context = {
        'inquiries': inquiries,
        'status_filter': status_filter,
    }
    return render(request, 'admin/inquiry_list.html', context)


@staff_required
def admin_vendor_verification(request):
    """
    Manage vendor verifications.
    """
    status_filter = request.GET.get('status', 'pending')
    verifications = VendorVerification.objects.select_related(
        'vendor', 'verified_by'
    ).order_by('-created_at')

    if status_filter:
        verifications = verifications.filter(status=status_filter)

    context = {
        'verifications': verifications,
        'status_filter': status_filter,
    }
    return render(request, 'admin/vendor_verification.html', context)


@staff_required
@require_POST
def admin_verify_vendor(request, verification_id):
    """
    Approve or reject vendor verification.
    """
    verification = get_object_or_404(VendorVerification, id=verification_id)
    action = request.POST.get('action')
    notes = request.POST.get('notes', '')

    if action == 'approve':
        verification.status = 'approved'
        verification.verified_by = request.user
        verification.verified_at = timezone.now()
        message = 'Vendor verification approved successfully.'
    elif action == 'reject':
        verification.status = 'rejected'
        message = 'Vendor verification rejected.'
    elif action == 'more_info':
        verification.status = 'more_info'
        message = 'Requested more information from vendor.'
    else:
        return JsonResponse({'success': False, 'error': 'Invalid action'})

    verification.verification_notes = notes
    verification.save()

    # Create audit log
    AuditLog.objects.create(
        user=request.user,
        action='verify' if action == 'approve' else 'reject',
        model_name='VendorVerification',
        object_id=verification.id,
        object_repr=str(verification),
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
    )

    return JsonResponse({'success': True, 'message': message})


@staff_required
def admin_notifications(request):
    """
    Manage system notifications.
    """
    admin_notifications_list = Notification.objects.select_related('user').order_by(
        '-created_at'
    )[:100]

    context = {
        'notifications': admin_notifications_list,
    }
    return render(request, 'admin/notifications.html', context)


@staff_required
@require_POST
def admin_send_notification(request):
    """
    Send notifications to users.
    """
    try:
        data = json.loads(request.body)
        user_ids = data.get('user_ids', [])
        notification_type = data.get('type', 'system')
        title = bleach.clean(data.get('title'))
        message_text = bleach.clean(data.get('message'))

        if not title or not message_text:
            return JsonResponse({
                'success': False,
                'error': 'Title and message are required'
            })

        # Create notifications for specified users or all users
        if user_ids:
            users = User.objects.filter(id__in=user_ids)
        else:
            users = User.objects.all()

        notifications_created = 0
        for user in users:
            Notification.objects.create(
                user=user,
                notification_type=notification_type,
                title=title,
                message=message_text,
            )
            notifications_created += 1

        return JsonResponse({
            'success': True,
            'message': f'{notifications_created} notifications sent.'
        })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'})


def _export_orders(writer):
    """Export orders data to CSV."""
    writer.writerow([
        'Order ID', 'Customer', 'Email', 'Phone', 'Total',
        'Status', 'Payment Method', 'Created At'
    ])
    orders = Order.objects.all().order_by('-created_at')
    for order in orders:
        writer.writerow([
            order.id,
            sanitize_csv_field(f"{order.first_name} {order.last_name}"),
            sanitize_csv_field(order.email),
            sanitize_csv_field(order.phone),
            order.paid_amount or 0,
            order.status,
            order.payment_method,
            order.created_at.strftime('%Y-%m-%d %H:%M'),
        ])


def _export_products(writer):
    """Export products data to CSV."""
    writer.writerow([
        'ID', 'Name', 'Category', 'Vendor', 'Price', 'MRP',
        'Stock', 'Status'
    ])
    products = Product.objects.select_related('category', 'vendor').all()
    for product in products:
        writer.writerow([
            product.id,
            sanitize_csv_field(product.name),
            sanitize_csv_field(product.category.name),
            sanitize_csv_field(product.vendor.name),
            product.price,
            product.mrp or '',
            product.stock_quantity,
            'Active' if product.is_active else 'Inactive',
        ])


def _export_vendors(writer):
    """Export vendors data to CSV."""
    writer.writerow(['ID', 'Name', 'City', 'Products Count'])
    vendors = Vendor.objects.annotate(
        products_count=models.Count('products')
    ).all()
    for vendor in vendors:
        writer.writerow([
            vendor.id,
            sanitize_csv_field(vendor.name),
            sanitize_csv_field(vendor.city),
            vendor.products_count,
        ])


def _export_users(writer):
    """Export users data to CSV."""
    writer.writerow([
        'ID', 'Username', 'Email', 'First Name', 'Last Name',
        'Date Joined', 'Is Active'
    ])
    users = User.objects.all().order_by('-date_joined')
    for user in users:
        writer.writerow([
            user.id,
            sanitize_csv_field(user.username),
            sanitize_csv_field(user.email),
            sanitize_csv_field(user.first_name),
            sanitize_csv_field(user.last_name),
            user.date_joined.strftime('%Y-%m-%d'),
            'Yes' if user.is_active else 'No',
        ])


# Export handlers mapping
EXPORT_HANDLERS = {
    'orders': _export_orders,
    'products': _export_products,
    'vendors': _export_vendors,
    'users': _export_users,
}


@staff_required
def admin_export_data(request):
    """Export data as CSV."""
    export_type = request.GET.get('type', 'orders')
    date_str = timezone.now().strftime("%Y%m%d")

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = (
        f'attachment; filename="{export_type}_{date_str}.csv"'
    )

    writer = csv.writer(response)

    # Use handler if available
    handler = EXPORT_HANDLERS.get(export_type)
    if handler:
        handler(writer)

    # Log export action
    AuditLog.objects.create(
        user=request.user,
        action='export',
        model_name=export_type.capitalize(),
        object_repr=f"Exported {export_type} data",
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
    )

    return response


@staff_required
def admin_site_settings(request):
    """
    Manage site settings.
    """
    settings_obj = SiteSettings.get_settings()

    if request.method == 'POST':
        # Update settings from form
        settings_obj.site_name = bleach.clean(request.POST.get('site_name', settings_obj.site_name))
        settings_obj.site_tagline = bleach.clean(request.POST.get('site_tagline', ''))
        settings_obj.contact_email = bleach.clean(request.POST.get('contact_email', ''))
        settings_obj.contact_phone = bleach.clean(request.POST.get('contact_phone', ''))
        settings_obj.address = bleach.clean(request.POST.get('address', ''))
        settings_obj.maintenance_mode = request.POST.get('maintenance_mode') == 'on'
        settings_obj.maintenance_message = bleach.clean(request.POST.get('maintenance_message', ''))
        settings_obj.enable_rfq = request.POST.get('enable_rfq') == 'on'
        settings_obj.enable_messaging = request.POST.get('enable_messaging') == 'on'
        settings_obj.enable_reviews = request.POST.get('enable_reviews') == 'on'
        settings_obj.save()

        return redirect('admin_site_settings')

    context = {
        'settings': settings_obj,
    }
    return render(request, 'admin/site_settings.html', context)


@staff_required
def admin_trade_events(request):
    """
    Manage trade events.
    """
    events = TradeEvent.objects.annotate(
        registrations_count=models.Count('registrations')
    ).order_by('start_date')

    context = {
        'events': events,
    }
    return render(request, 'admin/trade_events.html', context)


@staff_required
def admin_analytics(request):
    """
    Advanced analytics dashboard.
    """
    now = timezone.now()
    thirty_days_ago = now - timezone.timedelta(days=30)
    # Unused variable removed: seven_days_ago = now - timezone.timedelta(days=7)

    # Daily sales for last 30 days
    daily_sales = Order.objects.filter(
        paid=True,
        created_at__gte=thirty_days_ago
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        total=Sum('paid_amount'),
        count=models.Count('id')
    ).order_by('date')

    # Category-wise sales
    category_sales = OrderItem.objects.filter(
        order__paid=True,
        order__created_at__gte=thirty_days_ago
    ).values(
        'product__category__name'
    ).annotate(
        total=Sum(models.F('price') * models.F('quantity'))
    ).order_by('-total')[:5]

    # Vendor-wise sales
    vendor_sales = OrderItem.objects.filter(
        order__paid=True,
        order__created_at__gte=thirty_days_ago
    ).values(
        'vendor__name'
    ).annotate(
        total=Sum(models.F('price') * models.F('quantity'))
    ).order_by('-total')[:5]

    # Convert to JSON-serializable format
    daily_sales_json = json.dumps([
        {
            'date': item['date'].strftime('%Y-%m-%d') if item['date'] else '',
            'total': float(item['total']) if item['total'] else 0,
            'count': item['count'] or 0
        }
        for item in daily_sales
    ])

    category_sales_json = json.dumps([
        {
            'product__category__name': item['product__category__name'] or 'Unknown',
            'total': float(item['total']) if item['total'] else 0
        }
        for item in category_sales
    ])

    vendor_sales_json = json.dumps([
        {
            'vendor__name': item['vendor__name'] or 'Unknown',
            'total': float(item['total']) if item['total'] else 0
        }
        for item in vendor_sales
    ])

    context = {
        'daily_sales': list(daily_sales),  # For table rendering
        'daily_sales_json': daily_sales_json,  # For json_script tag
        'category_sales_json': category_sales_json,
        'vendor_sales_json': vendor_sales_json,
    }
    return render(request, 'admin/analytics.html', context)


# ============================================================================
# ENHANCED FEATURES VIEWS
# ============================================================================

def deals(request):
    """
    Display active deals and promotions.
    """
    now = timezone.now()
    active_deals = Deal.objects.filter(
        is_active=True,
        start_date__lte=now,
        end_date__gte=now
    ).prefetch_related('products', 'categories', 'vendors')

    # Group deals by type for better display
    percentage_deals = active_deals.filter(deal_type='percentage')
    fixed_deals = active_deals.filter(deal_type='fixed')
    seasonal_deals = active_deals.filter(deal_type='seasonal')

    context = {
        'active_deals': active_deals,
        'percentage_deals': percentage_deals,
        'fixed_deals': fixed_deals,
        'seasonal_deals': seasonal_deals,
    }
    return render(request, 'deals.html', context)


@login_required
def product_comparison(request):
    """
    Product comparison page with side-by-side comparison.
    """
    product_ids = request.GET.getlist('products')
    products = Product.objects.filter(id__in=product_ids).select_related('vendor', 'category')[:4]

    # Create or get comparison session
    session_id = request.session.session_key or 'default'
    comparison, created = ProductComparison.objects.get_or_create(
        user=request.user,
        session_id=session_id,
        defaults={'products': products}
    )

    if not created:
        comparison.products.set(products)
        comparison.save()

    # Track analytics
    AnalyticsEvent.objects.create(
        user=request.user,
        session_id=session_id,
        event_type='comparison',
        data={'product_ids': product_ids, 'product_count': len(products)}
    )

    context = {
        'products': products,
        'comparison': comparison,
    }
    return render(request, 'product_comparison.html', context)


@login_required
def notifications(request):
    """
    User notifications page.
    """
    notifications_list = Notification.objects.filter(user=request.user).order_by('-created_at')[:50]

    # Mark notifications as read if requested
    if request.method == 'POST' and 'mark_read' in request.POST:
        notification_id = request.POST.get('notification_id')
        if notification_id:
            notification = get_object_or_404(Notification, id=notification_id, user=request.user)
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save()
        else:
            # Mark all as read
            notifications_list.filter(is_read=False).update(
                is_read=True,
                read_at=timezone.now()
            )
        return redirect('notifications')

    # Separate unread and read notifications
    unread_notifications = notifications_list.filter(is_read=False)
    read_notifications = notifications_list.filter(is_read=True)

    context = {
        'unread_notifications': unread_notifications,
        'read_notifications': read_notifications,
        'total_count': notifications_list.count(),
        'unread_count': unread_notifications.count(),
    }
    return render(request, 'notifications.html', context)


@login_required
def advanced_search(request):
    """
    Advanced search page with filters and saved searches.
    """
    # Get saved searches for user
    saved_searches = AdvancedSearch.objects.filter(user=request.user)

    # Get search parameters
    query = request.GET.get('q', '')
    category_ids = request.GET.getlist('categories')
    vendor_ids = request.GET.getlist('vendors')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    brands = request.GET.getlist('brands')
    in_stock = request.GET.get('in_stock')
    sort_by = request.GET.get('sort', 'relevance')

    products = Product.objects.select_related('category', 'vendor').filter(is_active=True)

    # Apply filters
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(brand__icontains=query) |
            Q(technical_name__icontains=query) |
            Q(target_crops__icontains=query)
        )

    if category_ids:
        products = products.filter(category_id__in=category_ids)

    if vendor_ids:
        products = products.filter(vendor_id__in=vendor_ids)

    if min_price:
        products = products.filter(price__gte=min_price)

    if max_price:
        products = products.filter(price__lte=max_price)

    if brands:
        products = products.filter(brand__in=brands)

    if in_stock == '1':
        products = products.filter(stock_quantity__gt=0)

    # Sorting
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    elif sort_by == 'name':
        products = products.order_by('name')
    else:
        products = products.order_by('-created_at')

    # Pagination
    paginator = Paginator(products, 20)
    page = request.GET.get('page', 1)
    products = paginator.get_page(page)

    # Get filter options
    categories = Category.objects.all()
    vendors = Vendor.objects.all()
    available_brands = Product.objects.values_list('brand', flat=True).distinct().exclude(brand='')

    # Track search analytics
    if query:
        AnalyticsEvent.objects.create(
            user=request.user,
            session_id=request.session.session_key or 'default',
            event_type='search',
            data={
                'query': query,
                'filters': {
                    'categories': category_ids,
                    'vendors': vendor_ids,
                    'price_range': [min_price, max_price],
                    'brands': brands,
                    'in_stock': in_stock
                },
                'results_count': paginator.count
            }
        )

    context = {
        'products': products,
        'saved_searches': saved_searches,
        'categories': categories,
        'vendors': vendors,
        'brands': available_brands,
        'query': query,
        'selected_categories': category_ids,
        'selected_vendors': vendor_ids,
        'selected_brands': brands,
        'min_price': min_price,
        'max_price': max_price,
        'in_stock': in_stock,
        'sort_by': sort_by,
    }
    return render(request, 'advanced_search.html', context)


@login_required
@require_POST
def save_search(request):
    """
    Save advanced search filters.
    """
    name = bleach.clean(request.POST.get('search_name'))
    filters = {
        'q': request.POST.get('q', ''),
        'categories': request.POST.getlist('categories'),
        'vendors': request.POST.getlist('vendors'),
        'min_price': request.POST.get('min_price'),
        'max_price': request.POST.get('max_price'),
        'brands': request.POST.getlist('brands'),
        'in_stock': request.POST.get('in_stock'),
        'sort': request.POST.get('sort', 'relevance'),
    }

    AdvancedSearch.objects.create(
        user=request.user,
        name=name,
        filters=filters
    )

    return JsonResponse({'success': True, 'message': 'Search saved successfully'})


@login_required
def enhanced_vendor_dashboard(request):
    """
    Enhanced vendor dashboard with analytics and advanced features.
    """
    try:
        vendor = request.user.vendor
    except Vendor.DoesNotExist:
        return redirect('frontpage')

    # Get or create analytics
    analytics, created = VendorAnalytics.objects.get_or_create(vendor=vendor)

    # Update analytics data
    if created or (timezone.now() - analytics.last_updated).days >= 1:
        # Calculate analytics
        order_items = OrderItem.objects.filter(
            product__vendor=vendor,
            order__paid=True
        )

        analytics.total_sales = order_items.count()
        analytics.total_revenue = order_items.aggregate(
            total=Sum('price')
        )['total'] or 0

        if analytics.total_sales > 0:
            analytics.avg_order_value = analytics.total_revenue / analytics.total_sales

        # Top products
        top_products_data = order_items.values('product__name').annotate(
            sales_count=Count('product'),
            revenue=Sum('price')
        ).order_by('-revenue')[:5]

        analytics.top_products = list(top_products_data)

        # Sales trend (last 30 days)
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        sales_trend = order_items.filter(
            order__created_at__gte=thirty_days_ago
        ).annotate(
            date=TruncDate('order__created_at')
        ).values('date').annotate(
            sales=Count('id'),
            revenue=Sum('price')
        ).order_by('date')

        analytics.sales_trend = list(sales_trend)
        analytics.save()

    # Get recent data
    products = Product.objects.filter(vendor=vendor).order_by('-created_at')
    recent_orders = OrderItem.objects.filter(
        product__vendor=vendor
    ).select_related('order', 'product').order_by('-order__created_at')[:20]

    bulk_orders = BulkOrder.objects.filter(vendor=vendor).order_by('-created_at')[:10]

    # Calculate additional metrics
    total_revenue = analytics.total_revenue
    total_orders = recent_orders.values('order').distinct().count()
    pending_orders = (
        recent_orders.filter(order__status='pending')
        .values('order').distinct().count()
    )

    context = {
        'vendor': vendor,
        'analytics': analytics,
        'products': products,
        'recent_orders': recent_orders,
        'bulk_orders': bulk_orders,
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
    }
    return render(request, 'enhanced_vendor_dashboard.html', context)


@login_required
@require_POST
def track_analytics(request):
    """
    API endpoint to track user analytics events.
    """
    try:
        data = json.loads(request.body)
        event_type = data.get('event_type')
        product_id = data.get('product_id')
        additional_data = data.get('data', {})

        event = AnalyticsEvent.objects.create(
            user=request.user,
            session_id=request.session.session_key or 'default',
            event_type=event_type,
            product_id=product_id,
            data=additional_data,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
        )

        return JsonResponse({'success': True, 'event_id': event.id})

    except (ValueError, KeyError) as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_POST
def subscribe_alert(request):
    """
    Subscribe to price/stock/deal alerts.
    """
    try:
        data = json.loads(request.body)
        subscription_type = data.get('type')
        product_id = data.get('product_id')
        vendor_id = data.get('vendor_id')
        category_id = data.get('category_id')
        frequency = data.get('frequency', 'weekly')

        subscription, created = Subscription.objects.get_or_create(
            user=request.user,
            subscription_type=subscription_type,
            product_id=product_id,
            vendor_id=vendor_id,
            category_id=category_id,
            defaults={'frequency': frequency}
        )

        if not created:
            subscription.is_active = True
            subscription.frequency = frequency
            subscription.save()

        return JsonResponse({
            'success': True,
            'message': 'Subscription activated successfully',
            'created': created
        })

    except (ValueError, KeyError) as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_POST
def apply_deal(request):
    """
    Apply a deal to cart or checkout.
    """
    try:
        data = json.loads(request.body)
        deal_id = data.get('deal_id')
        cart_total = data.get('cart_total', 0)

        deal = get_object_or_404(Deal, id=deal_id)

        if not deal.is_valid:
            return JsonResponse({'success': False, 'error': 'Deal is not valid'})

        discount = deal.calculate_discount(float(cart_total))

        # Increment usage count
        deal.used_count += 1
        deal.save()

        return JsonResponse({
            'success': True,
            'discount': discount,
            'deal_name': deal.name,
            'message': f'Deal "{deal.name}" applied successfully!'
        })

    except (ValueError, KeyError) as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def bulk_order(request):
    """
    Render the bulk order request page.
    """
    template_name = 'bulk_order.html'
    categories = Category.objects.all()
    vendors = Vendor.objects.filter(is_active=True)[:20]

    if request.method == 'POST':
        # Handle bulk order form submission
        product_name = bleach.clean(request.POST.get('product_name'))
        quantity = request.POST.get('quantity')
        category_id = request.POST.get('category')
        description = bleach.clean(request.POST.get('description'))
        company_name = bleach.clean(request.POST.get('company_name'))
        contact_name = bleach.clean(request.POST.get('contact_name'))
        email = bleach.clean(request.POST.get('email'))
        phone = bleach.clean(request.POST.get('phone'))

        # Create RFQ (Request for Quote)
        try:
            RFQ.objects.create(
                product_name=product_name,
                quantity=int(quantity) if quantity else 1,
                category_id=category_id if category_id else None,
                requirements=description,
                company_name=company_name,
                contact_name=contact_name,
                email=email,
                phone=phone,
                user=request.user if request.user.is_authenticated else None
            )
            return render(request, template_name, {
                'categories': categories,
                'vendors': vendors,
                'success': True,
                'message': 'Your bulk order request has been submitted successfully!'
            })
        except (ValueError, KeyError):
            return render(request, template_name, {
                'categories': categories,
                'vendors': vendors,
                'error': 'There was an error submitting your request. Please try again.'
            })

    return render(request, template_name, {
        'categories': categories,
        'vendors': vendors
    })

# ============================================================================
# ERROR HANDLERS
# ============================================================================


def error_404(request, _exception):
    """Custom 404 error page."""
    return render(request, '404.html', status=404)


def error_500(request):
    """Custom 500 error page."""
    return render(request, '500.html', status=500)


# ============================================================================
# USER SETTINGS VIEWS
# ============================================================================

@login_required
def profile_settings(request):
    """
    Update user profile and business details.
    """
    user_form = UserUpdateForm(instance=request.user)
    profile, _created = Profile.objects.get_or_create(user=request.user)
    profile_form = ProfileUpdateForm(instance=profile)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile_settings')

    return render(request, 'profile_settings.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


@login_required
def credit_billing(request):
    """
    View credit details and billing history.
    """
    profile, _created = Profile.objects.get_or_create(user=request.user)

    # Placeholder for transactions/invoices not yet linked to credit
    transactions = []

    credit_percentage = 0
    if profile.credit_limit and profile.credit_limit > 0:
        credit_percentage = int((profile.credit_used / profile.credit_limit) * 100)

    return render(request, 'credit_billing.html', {
        'profile': profile,
        'transactions': transactions,
        'credit_percentage': credit_percentage
    })


@login_required
def invoices(request):
    """
    List user orders with invoice download options.
    """
    orders = Order.objects.filter(user=request.user, paid=True).order_by('-created_at')

    return render(request, 'invoices.html', {
        'orders': orders
    })


def offline_page(request):
    """
    Render the offline fallback page for PWA.
    This page is shown when the user is offline and the requested page is not cached.
    """
    return render(request, 'offline.html')


@login_required
def pwa_analytics_dashboard(request):
    """
    Render the PWA analytics dashboard for admin users.
    Shows installation metrics, trends, and configuration status.
    """
    if not request.user.is_staff:
        return redirect('frontpage')

    return render(request, 'admin/pwa_analytics.html')
