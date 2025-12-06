"""
Views for the store app handling frontpage, shop, cart, and other pages.
"""
# pylint: disable=no-member

import json
import uuid
import stripe

from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db import models
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.text import slugify
from django.views.decorators.http import require_POST

from .cart import Cart
from .forms import OrderForm, VendorRegistrationForm, ReviewForm
from .models import (
    Product, Vendor, Category, Contact, Order, OrderItem, Profile, Wishlist
)

stripe.api_key = settings.STRIPE_API_KEY_HIDDEN


def frontpage(request):
    """
    Render the frontpage with featured vendors and products.
    """
    products = Product.objects.select_related('category', 'vendor').all()[0:8]
    vendors = Vendor.objects.all()[0:4]
    categories = Category.objects.all()

    context = {
        'products': products,
        'vendors': vendors,
        'categories': categories,
    }
    return render(request, 'index.html', context)

def shop(request):
    """
    Render the shop page with products, advanced search, filtering, sorting, and pagination.
    """
    products = Product.objects.select_related('category', 'vendor').all()
    categories = Category.objects.all()
    vendors = Vendor.objects.all()

    # Get filter parameters
    query = request.GET.get('q', '')
    category_slug = request.GET.get('category', '')
    vendor_slug = request.GET.get('vendor', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    sort = request.GET.get('sort', 'relevance')
    page = request.GET.get('page', 1)

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

    # Sorting
    if sort == 'name':
        products = products.order_by('name')
    elif sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created_at')
    elif sort == 'rating':
        products = products.order_by('-created_at')
    else:  # relevance
        products = products.order_by('-created_at')

    # Pagination
    paginator = Paginator(products, 12)  # 12 products per page
    products = paginator.get_page(page)

    context = {
        'products': products,
        'categories': categories,
        'vendors': vendors,
        'query': query,
        'category_slug': category_slug,
        'vendor_slug': vendor_slug,
        'min_price': min_price,
        'max_price': max_price,
        'sort': sort
    }
    return render(request, 'shop.html', context)

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
            user.first_name = form.cleaned_data['name']
            user.save()

            # Create Vendor
            vendor = form.save(commit=False)
            vendor.created_by = user

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

def product_detail(request, slug):
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

@login_required
def checkout(request):
    """Render the checkout page and handle order creation."""
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            total_price = cart.get_total_cost()

            order = form.save(commit=False)
            order.user = request.user
            order.paid_amount = total_price
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

@login_required
def success(request):
    """Render the success page."""
    cart = Cart(request)
    cart.clear()

    order_id = request.GET.get('order_id')
    order = None
    if order_id:
        order = Order.objects.filter(id=order_id, user=request.user).first()
        if order:
            order.paid = True
            order.status = 'confirmed'
            order.save()

    return render(request, 'success.html', {'order': order})

@login_required
def order_detail(request, order_id):
    """Render the details of a specific order."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_detail.html', {'order': order})

@require_POST
def start_order(request):
    """API endpoint to start a Stripe checkout session."""
    cart = Cart(request)
    data = json.loads(request.body)

    # Calculate total using cart method
    total_price = cart.get_total_cost()

    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        first_name=data.get('first_name', ''),
        last_name=data.get('last_name', ''),
        email=data.get('email', ''),
        address=data.get('address', ''),
        zipcode=data.get('zipcode', ''),
        place=data.get('place', ''),
        phone=data.get('phone', ''),
        paid_amount=total_price,
        paid=False,
        payment_method='card',
        status='pending'
    )

    items = []

    for item in cart:
        product = item['product']
        quantity = int(item['quantity'])
        price = product.price * quantity

        # Create OrderItem
        OrderItem.objects.create(
            order=order, product=product, price=price,
            quantity=quantity, vendor=product.vendor
        )

        items.append({
            'price_data': {
                'currency': 'inr',
                'product_data': {
                    'name': product.name,
                },
                'unit_amount': int(product.price * 100),
            },
            'quantity': quantity
        })

    # Create Stripe Session
    success_url = request.build_absolute_uri('/cart/success/') + f'?order_id={order.id}'
    cancel_url = request.build_absolute_uri('/cart/')

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=items,
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                'order_id': order.id
            }
        )
        return JsonResponse({'session': session})
    except stripe.error.StripeError as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def contact(request):
    """Render the contact page."""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

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
