"""
API views for the store app providing RESTful endpoints.
"""
# pylint: disable=no-member,too-many-lines

# Standard library imports
import csv
import hashlib
import hmac
import json
import logging
import re
from datetime import timedelta

# Third-party imports
import stripe
import bleach


# Django imports
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import connection, models
from django.db.models import Q, Sum, Count, Min, Max
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

# DRF imports
from rest_framework import generics, status, permissions
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from django.views import View

# Local imports
from .cart import Cart
from .permissions import IsVendorUser
from .models import (
    Product, Category, Vendor, Order, OrderItem, Wishlist, Review, Coupon, Profile,
    FlashSale, BulkOrder, Notification, Deal, InventoryLog, Contact, Subscription,
    Crop, Disease, ProductCropMapping, ProductDiseaseMapping,
    LocationPopularity, DealOfTheDay, PriceAlert, UserCoin, CoinTransaction,
    AnalyticsEvent, UserSession, UserInteraction, UserBehaviorPattern, UserPreference,
    UserActivityLog, UserSegmentMembership, UserFeedback, UserSegment
)
from .serializers import (
    ProductSerializer, CategorySerializer, VendorSerializer, OrderSerializer,
    WishlistSerializer, ReviewSerializer, FlashSaleSerializer, BulkOrderSerializer,
    NotificationSerializer, DealSerializer,
    UserSessionSerializer, UserInteractionSerializer, UserBehaviorPatternSerializer,
    UserPreferenceSerializer, UserFeedbackSerializer, UserAnalyticsSummarySerializer,
    RealTimeAnalyticsSerializer, AnalyticsDashboardSerializer
)
from .services.recommendations import (
    RecommendationService, get_seasonal_recommendations, get_recommendations_for_cart
)

logger = logging.getLogger(__name__)

# Constants for error messages - used throughout the module
ERROR_NOT_VENDOR = 'Not a vendor account'
ERROR_PRODUCT_NOT_FOUND = 'Product not found'
ERROR_INVALID_EMAIL = 'Invalid email format'
CSV_CONTENT_TYPE = 'text/csv'


class CategoryListView(generics.ListAPIView):
    """API view for listing categories."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

    @method_decorator(cache_page(settings.CACHE_TTL_MEDIUM))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class ProductListView(generics.ListAPIView):
    """API view for listing products with filtering and search."""
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Product.objects.select_related('category', 'vendor').filter(is_active=True)

        queryset = self._filter_by_search(queryset)
        queryset = self._filter_by_category_and_vendor(queryset)
        queryset = self._filter_by_price(queryset)
        queryset = self._filter_by_attributes(queryset)
        queryset = self._filter_by_brand_crop_disease(queryset)

        return self._apply_sorting(queryset)

    def _filter_by_search(self, queryset):
        query = self.request.query_params.get('q', '')
        if query:
            return queryset.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(brand__icontains=query) |
                Q(technical_name__icontains=query) |
                Q(target_crops__icontains=query)
            )
        return queryset

    def _filter_by_category_and_vendor(self, queryset):
        category_slug = self.request.query_params.get('category', '')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        vendor_slug = self.request.query_params.get('vendor', '')
        if vendor_slug:
            queryset = queryset.filter(vendor__slug=vendor_slug)
        return queryset

    def _filter_by_price(self, queryset):
        min_price = self.request.query_params.get('min_price', '')
        max_price = self.request.query_params.get('max_price', '')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        return queryset

    def _filter_by_attributes(self, queryset):
        in_stock = self.request.query_params.get('in_stock', '')
        if in_stock == '1':
            queryset = queryset.filter(stock_quantity__gt=0)

        has_discount = self.request.query_params.get('has_discount', '')
        if has_discount == 'true' or has_discount == '1':
            queryset = queryset.filter(discount_percentage__gt=0)
        return queryset

    def _filter_by_brand_crop_disease(self, queryset):
        brands = self.request.query_params.get('brands', '')
        brands = brands or self.request.query_params.get('brand', '')
        if brands:
            brands_list = [b.strip() for b in brands.split(',') if b.strip()]
            if brands_list:
                brand_query = Q()
                for b in brands_list:
                    brand_query |= Q(brand__icontains=b)
                queryset = queryset.filter(brand_query)

        crop = self.request.query_params.get('crop', '')
        if crop:
            queryset = queryset.filter(target_crops__icontains=crop)

        disease = self.request.query_params.get('disease', '')
        if disease:
            queryset = queryset.filter(target_diseases__icontains=disease)
        return queryset

    def _apply_sorting(self, queryset):
        sort = self.request.query_params.get('sort', 'relevance')
        if sort == 'name':
            return queryset.order_by('name')
        elif sort == 'price_low':
            return queryset.order_by('price')
        elif sort == 'price_high':
            return queryset.order_by('-price')
        elif sort == 'newest':
            return queryset.order_by('-created_at')
        elif sort == 'rating':
            return queryset.order_by('-created_at')
        return queryset.order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        limit = request.query_params.get('limit')
        if limit:
            # Return limited results without pagination
            try:
                limit = int(limit)
                queryset = queryset[:limit]
            except ValueError:
                logger.warning("Invalid limit parameter: %s", limit)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            # Use pagination
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)


class ProductDetailView(generics.RetrieveAPIView):
    """API view for product details."""
    queryset = Product.objects.select_related('category', 'vendor').filter(is_active=True)
    serializer_class = ProductSerializer
    lookup_field = 'slug'
    permission_classes = [permissions.AllowAny]

    @method_decorator(cache_page(settings.CACHE_TTL_MEDIUM))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class VendorListView(generics.ListAPIView):
    """API view for listing vendors."""
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    permission_classes = [permissions.AllowAny]


class VendorDetailView(generics.RetrieveAPIView):
    """API view for vendor details."""
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    lookup_field = 'slug'
    permission_classes = [permissions.AllowAny]


class SearchSuggestionsView(APIView):
    """API view for search suggestions."""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        """Get search suggestions based on query."""
        query = request.query_params.get('q', '').strip()
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

        return Response({'results': results})


class WishlistView(APIView):
    """API view for managing wishlist."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get user's wishlist items."""
        wishlist_items = Wishlist.objects.filter(user=request.user).select_related(
            'product__category', 'product__vendor'
        )
        serializer = WishlistSerializer(wishlist_items, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Add product to wishlist."""
        product_id = request.data.get('product_id')
        product = get_object_or_404(Product, id=product_id)

        _, created = Wishlist.objects.get_or_create(
            user=request.user,
            product=product
        )

        if created:
            return Response(
                {'message': 'Added to wishlist', 'created': True},
                status=status.HTTP_201_CREATED
            )
        return Response({'message': 'Already in wishlist', 'created': False})

    def delete(self, request, product_id):
        """Remove product from wishlist."""
        product = get_object_or_404(Product, id=product_id)
        Wishlist.objects.filter(user=request.user, product=product).delete()
        return Response({'message': 'Removed from wishlist'})


class CartView(APIView):
    """API view for managing shopping cart."""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        """Get cart contents."""
        cart = Cart(request)
        items = []
        for item in cart:
            items.append({
                'id': item['product'].id,
                'name': item['product'].name,
                'price': float(item['product'].price),
                'quantity': item['quantity'],
                'total_price': float(item['total_price']),
                'image': item['product'].image.url if item['product'].image else None
            })

        return Response({
            'items': items,
            'total_cost': float(cart.get_total_cost()),
            'item_count': len(cart)
        })

    def post(self, request):
        """Add/update/remove cart items."""
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        action = request.data.get('action', 'add')  # add, remove, update

        cart = Cart(request)

        if action == 'add':
            cart.add(product_id, quantity)
        elif action == 'remove':
            cart.remove(product_id)
        elif action == 'update':
            cart.add(product_id, quantity, update_quantity=True)

        return Response({
            'success': True,
            'item_count': len(cart),
            'total_cost': float(cart.get_total_cost())
        })

    def delete(self, request):
        """Clear the cart."""
        cart = Cart(request)
        cart.clear()
        return Response({'message': 'Cart cleared'})


class ReviewListView(generics.ListCreateAPIView):
    """API view for product reviews."""
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        product_slug = self.kwargs.get('product_slug')
        product = get_object_or_404(Product, slug=product_slug)
        return Review.objects.filter(product=product).select_related(
            'product', 'user'
        ).order_by('-created_at')

    def perform_create(self, serializer):
        product_slug = self.kwargs.get('product_slug')
        product = get_object_or_404(Product, slug=product_slug)

        # Check if user already reviewed this product
        if Review.objects.filter(product=product, user=self.request.user).exists():
            raise ValidationError("You have already reviewed this product")

        # Check if user purchased the product
        is_verified = OrderItem.objects.filter(
            order__user=self.request.user,
            product=product
        ).exists()

        serializer.save(
            product=product,
            user=self.request.user,
            is_verified_purchase=is_verified
        )


class OrderListView(generics.ListAPIView):
    """API view for user orders."""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Get user's orders."""
        return Order.objects.filter(
            user=self.request.user
        ).prefetch_related(
            'items__product__vendor', 'items__product__category'
        ).order_by('-created_at')


class OrderDetailView(generics.RetrieveAPIView):
    """API view for order details."""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related(
            'items__product__vendor', 'items__product__category'
        )


class ApplyCouponView(APIView):
    """API view for applying coupons."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Apply a coupon code."""
        code = request.data.get('code', '').strip().upper()
        cart_total = request.data.get('cart_total', 0)

        if not code:
            return Response({'success': False, 'error': 'Please enter a coupon code'})

        try:
            coupon = Coupon.objects.get(code__iexact=code)
        except Coupon.DoesNotExist:
            return Response({'success': False, 'error': 'Invalid coupon code'})

        # Validate coupon
        now = timezone.now()
        if not coupon.is_active:
            return Response({'success': False, 'error': 'This coupon is no longer active'})

        if coupon.used_count >= coupon.max_uses:
            return Response({'success': False, 'error': 'This coupon has reached its usage limit'})

        if now < coupon.valid_from:
            return Response({'success': False, 'error': 'This coupon is not yet valid'})

        if now > coupon.valid_until:
            return Response({'success': False, 'error': 'This coupon has expired'})

        if float(cart_total) < float(coupon.min_order_value):
            return Response({
                'success': False,
                'error': f'Minimum order value of â‚¹{coupon.min_order_value} required'
            })

        # Calculate discount
        if coupon.discount_type == 'percent':
            discount = float(cart_total) * (float(coupon.discount_value) / 100)
        else:
            discount = float(coupon.discount_value)

        discount = min(discount, float(cart_total))

        return Response({
            'success': True,
            'code': coupon.code,
            'discount_type': coupon.discount_type,
            'discount_value': float(coupon.discount_value),
            'discount_amount': round(discount, 2),
            'message': f'Coupon applied! You save â‚¹{round(discount, 2)}'
        })


class RecommendationsView(APIView):
    """API view for product recommendations."""
    permission_classes = [permissions.AllowAny]

    def get(self, _request, product_id):
        """Get product recommendations."""
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'recommendations': []})

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

        # Get products in similar price range (Â±20%)
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

        return Response({'recommendations': recommendations})


class LoginView(APIView):
    """API view for user login with rate limiting."""
    permission_classes = [permissions.AllowAny]

    # Apply stricter rate limiting to prevent brute force attacks
    throttle_classes = [AnonRateThrottle]
    throttle_scope = 'login'

    def post(self, request):
        """Authenticate and login user."""
        username = bleach.clean(request.data.get('username', ''))
        password = request.data.get('password', '')

        if not username or not password:
            return Response({
                'success': False,
                'error': 'Username and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            token, _ = Token.objects.get_or_create(user=user)
            logger.info("User %s logged in successfully", username)

            # Ensure profile and coins exist
            Profile.objects.get_or_create(user=user)
            UserCoin.objects.get_or_create(user=user)

            return Response({
                'success': True,
                'token': token.key,
                'user': self._get_user_data(user)
            })
        logger.warning("Failed login attempt for username: %s", username)
        return Response({
            'success': False,
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)

    def _get_user_data(self, user):
        """Helper to format user data with profile info."""
        profile = getattr(user, 'profile', None)
        coins = getattr(user, 'coins', None)
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'business_name': profile.shop_name if profile else '',
            'role': profile.role if profile else 'retailer',
            'coin_balance': coins.balance if coins else 0
        }


class LogoutView(APIView):
    """API view for user logout."""

    def post(self, request):
        """Logout user."""
        logout(request)
        return Response({'success': True})


class RegisterView(APIView):
    """API view for user registration with validation."""
    permission_classes = [permissions.AllowAny]

    # Rate limit registration to prevent abuse
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        """Register a new user with input validation."""
        # Sanitize inputs
        username = bleach.clean(request.data.get('username', ''))
        email = bleach.clean(request.data.get('email', ''))
        password = request.data.get('password', '')
        first_name = bleach.clean(request.data.get('first_name', ''))
        last_name = bleach.clean(request.data.get('last_name', ''))
        shop_name = bleach.clean(request.data.get('shop_name', ''))
        role = request.data.get('role', 'retailer')

        # Validate required fields
        if not username or not email or not password:
            return Response({
                'success': False,
                'error': 'Username, email, and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate email format
        if '@' not in email or '.' not in email:
            return Response({
                'success': False,
                'error': ERROR_INVALID_EMAIL
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate password length (Django validators will be applied too)
        if len(password) < 8:
            return Response({
                'success': False,
                'error': 'Password must be at least 8 characters'
            }, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'success': False, 'error': 'Username already exists'})

        if User.objects.filter(email=email).exists():
            return Response({'success': False, 'error': 'Email already registered'})

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        # Create Profile and UserCoin
        Profile.objects.create(user=user, shop_name=shop_name, role=role)
        UserCoin.objects.create(user=user)

        logger.info("New user registered: %s", username)
        login(request, user)
        token, _ = Token.objects.get_or_create(user=user)

        # Get formatted user data
        profile = user.profile
        coins = user.coins
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'date_joined': user.date_joined,
            'business_name': profile.shop_name,
            'role': profile.role,
            'coin_balance': coins.balance
        }

        return Response({
            'success': True,
            'token': token.key,
            'user': user_data
        }, status=status.HTTP_201_CREATED)


class UserProfileView(APIView):
    """API view for user profile."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get user profile."""
        user = request.user
        profile = getattr(user, 'profile', None)
        coins = getattr(user, 'coins', None)

        profile_data = None
        if profile:
            profile_data = {
                'shop_name': profile.shop_name or '',
                'gst_number': profile.gst_number or '',
                'address': profile.address or '',
                'city': profile.city or '',
                'state': profile.state or '',
                'pincode': profile.pincode or '',
                'is_kyc_verified': profile.is_kyc_verified,
                'role': profile.role,
            }

        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'date_joined': user.date_joined,
                'business_name': profile.shop_name if profile else '',
                'role': profile.role if profile else 'retailer',
                'coin_balance': coins.balance if coins else 0
            },
            'profile': profile_data
        })

    def put(self, request):
        """Update user profile."""
        user = request.user
        profile_data = request.data.get('profile', {})

        # Update user fields
        user.first_name = request.data.get('first_name', user.first_name)
        user.last_name = request.data.get('last_name', user.last_name)
        user.email = request.data.get('email', user.email)
        user.save()

        # Update or create profile
        profile, _ = Profile.objects.get_or_create(user=user)
        for field in ['shop_name', 'gst_number', 'address', 'city', 'state', 'pincode']:
            if field in profile_data:
                setattr(profile, field, profile_data[field])
        profile.save()

        return Response({'success': True})


# ============================================================================
# NEW API VIEWS FOR ENHANCED FUNCTIONALITY
# ============================================================================


class FlashSaleListView(generics.ListAPIView):
    """API view for listing active flash sales."""
    serializer_class = FlashSaleSerializer

    def get_queryset(self):
        """Get currently active flash sales."""
        now = timezone.now()
        return FlashSale.objects.filter(
            is_active=True,
            start_time__lte=now,
            end_time__gte=now
        ).prefetch_related('products__vendor', 'products__category')


class FlashSaleDetailView(generics.RetrieveAPIView):
    """API view for flash sale details."""
    queryset = FlashSale.objects.prefetch_related('products__vendor', 'products__category')
    serializer_class = FlashSaleSerializer
    lookup_field = 'slug'


class BulkOrderView(APIView):
    """API view for managing bulk orders."""
    permission_classes = [permissions.IsAuthenticated]

    @method_decorator(cache_page(120))  # Cache for 2 minutes
    def get(self, request):
        """Get user's bulk order requests."""
        bulk_orders = BulkOrder.objects.filter(
            user=request.user
        ).select_related('product__category', 'vendor').order_by('-created_at')
        serializer = BulkOrderSerializer(bulk_orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Create a new bulk order request."""
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')
        requested_price = request.data.get('requested_price')
        notes = request.data.get('notes', '')

        if not product_id or not quantity:
            return Response(
                {'error': 'Product ID and quantity are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': ERROR_PRODUCT_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND
            )

        bulk_order = BulkOrder.objects.create(
            user=request.user,
            product=product,
            vendor=product.vendor,
            quantity=quantity,
            requested_price=requested_price,
            notes=notes
        )

        serializer = BulkOrderSerializer(bulk_order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class NotificationListView(APIView):
    """API view for user notifications."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get user's notifications."""
        notifications = Notification.objects.filter(
            user=request.user
        ).order_by('-created_at')[:50]

        unread_count = notifications.filter(is_read=False).count()

        serializer = NotificationSerializer(notifications, many=True)
        return Response({
            'notifications': serializer.data,
            'unread_count': unread_count
        })

    def post(self, request):
        """Mark notifications as read."""
        notification_ids = request.data.get('notification_ids', [])
        mark_all = request.data.get('mark_all', False)

        if mark_all:
            Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        elif notification_ids:
            Notification.objects.filter(
                user=request.user,
                id__in=notification_ids
            ).update(is_read=True)

        return Response({'success': True})


class DealListView(generics.ListAPIView):
    """API view for listing active deals."""
    serializer_class = DealSerializer

    @method_decorator(cache_page(settings.CACHE_TTL_MEDIUM))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        """Get currently active deals."""
        now = timezone.now()
        return Deal.objects.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).prefetch_related(
            'products__vendor', 'products__category', 'categories', 'vendors'
        ).order_by('-priority')


class DealDetailView(generics.RetrieveAPIView):
    """API view for deal details."""
    queryset = Deal.objects.prefetch_related(
        'products__vendor', 'products__category', 'categories', 'vendors'
    )
    serializer_class = DealSerializer
    lookup_field = 'slug'


class InventoryView(APIView):
    """API view for vendor inventory management."""

    permission_classes = [permissions.IsAuthenticated, IsVendorUser]

    def get(self, request):
        """Get inventory status for vendor's products."""
        user = request.user

        # Check if user is a vendor
        if not hasattr(user, 'vendor'):
            return Response(
                {'error': ERROR_NOT_VENDOR},
                status=status.HTTP_403_FORBIDDEN
            )

        vendor = user.vendor
        products = Product.objects.filter(vendor=vendor).order_by('stock_quantity')

        # Get low stock products
        low_stock = products.filter(stock_quantity__lte=models.F('low_stock_threshold'))

        inventory_data = [{
            'id': p.id,
            'name': p.name,
            'slug': p.slug,
            'stock_quantity': p.stock_quantity,
            'low_stock_threshold': p.low_stock_threshold,
            'is_low_stock': p.is_low_stock,
            'is_in_stock': p.is_in_stock
        } for p in products]

        return Response({
            'total_products': products.count(),
            'low_stock_count': low_stock.count(),
            'out_of_stock_count': products.filter(stock_quantity=0).count(),
            'inventory': inventory_data
        })

    def put(self, request):
        """Update product stock quantity."""
        user = request.user
        product_id = request.data.get('product_id')
        new_quantity = request.data.get('quantity')
        notes = request.data.get('notes', '')

        if not hasattr(user, 'vendor'):
            return Response(
                {'error': ERROR_NOT_VENDOR},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            product = Product.objects.get(id=product_id, vendor=user.vendor)
        except Product.DoesNotExist:
            return Response(
                {'error': ERROR_PRODUCT_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND
            )

        previous_stock = product.stock_quantity
        product.stock_quantity = new_quantity
        product.save()

        # Log inventory change
        InventoryLog.objects.create(
            product=product,
            action='adjustment',
            quantity=new_quantity - previous_stock,
            previous_stock=previous_stock,
            new_stock=new_quantity,
            notes=notes,
            created_by=user
        )

        return Response({
            'success': True,
            'previous_stock': previous_stock,
            'new_stock': new_quantity
        })


# ============================================================================
# ADVANCED API VIEWS FOR POWERFUL BACKEND
# ============================================================================


class VendorAnalyticsAPIView(APIView):
    """API view for vendor analytics and dashboard data."""
    permission_classes = [permissions.IsAuthenticated, IsVendorUser]

    def get(self, request):
        """Get comprehensive vendor analytics."""
        user = request.user

        if not hasattr(user, 'vendor'):
            return Response(
                {'error': ERROR_NOT_VENDOR},
                status=status.HTTP_403_FORBIDDEN
            )

        vendor = user.vendor
        now = timezone.now()
        thirty_days_ago = now - timezone.timedelta(days=30)
        seven_days_ago = now - timezone.timedelta(days=7)

        # Get vendor products with optimized query
        products = Product.objects.filter(vendor=vendor).select_related('category')

        # Get orders for this vendor's products
        order_items = OrderItem.objects.filter(
            vendor=vendor,
            order__paid=True
        ).select_related('order', 'product__category')

        # Calculate metrics
        total_revenue = sum(
            float(item.price) * item.quantity for item in order_items
        )
        monthly_revenue = sum(
            float(item.price) * item.quantity
            for item in order_items
            if item.order.created_at >= thirty_days_ago
        )
        weekly_revenue = sum(
            float(item.price) * item.quantity
            for item in order_items
            if item.order.created_at >= seven_days_ago
        )

        # Get reviews
        reviews = Review.objects.filter(product__vendor=vendor).select_related('product')
        avg_rating = reviews.aggregate(avg=models.Avg('rating'))['avg'] or 0

        # Get bulk orders
        bulk_orders = BulkOrder.objects.filter(vendor=vendor).select_related('product', 'user')
        pending_bulk = bulk_orders.filter(status='pending').count()

        # Top selling products
        top_products = OrderItem.objects.filter(
            vendor=vendor,
            order__paid=True
        ).values('product__name', 'product__slug').annotate(
            total_sold=Sum('quantity')
        ).order_by('-total_sold')[:5]

        return Response({
            'overview': {
                'total_products': products.count(),
                'active_products': products.filter(is_active=True).count(),
                'out_of_stock': products.filter(stock_quantity=0).count(),
                'low_stock': products.filter(
                    stock_quantity__lte=models.F('low_stock_threshold')
                ).count(),
            },
            'revenue': {
                'total': round(total_revenue, 2),
                'monthly': round(monthly_revenue, 2),
                'weekly': round(weekly_revenue, 2),
            },
            'orders': {
                'total': order_items.values('order').distinct().count(),
                'pending_bulk_orders': pending_bulk,
            },
            'reviews': {
                'total': reviews.count(),
                'average_rating': round(avg_rating, 1),
            },
            'top_products': list(top_products),
        })


class TrendingProductsView(APIView):
    """API view for trending products based on recent orders and views."""

    def get(self, request):
        """Get trending products."""
        days = int(request.query_params.get('days', 7))
        limit = int(request.query_params.get('limit', 10))

        since = timezone.now() - timezone.timedelta(days=days)

        # Get products ordered most frequently recently
        trending = OrderItem.objects.filter(
            order__created_at__gte=since,
            order__paid=True
        ).values('product').annotate(
            order_count=Count('id')
        ).order_by('-order_count')[:limit]

        product_ids = [item['product'] for item in trending]
        products = Product.objects.filter(
            id__in=product_ids,
            is_active=True
        ).select_related('category', 'vendor')

        # Maintain order by trending score
        product_map = {p.id: p for p in products}
        ordered_products = [
            product_map[pid] for pid in product_ids if pid in product_map
        ]

        serializer = ProductSerializer(ordered_products, many=True, context={'request': request})
        return Response({
            'trending_products': serializer.data,
            'period_days': days
        })


class RecentlyViewedView(APIView):
    """API view for tracking and retrieving recently viewed products."""

    def get(self, request):
        """Get recently viewed products from session."""
        recently_viewed = request.session.get('recently_viewed', [])
        limit = int(request.query_params.get('limit', 10))

        if recently_viewed:
            products = Product.objects.filter(
                id__in=recently_viewed[:limit],
                is_active=True
            ).select_related('category', 'vendor')

            # Maintain order
            product_map = {p.id: p for p in products}
            ordered_products = [
                product_map[pid] for pid in recently_viewed[:limit]
                if pid in product_map
            ]

            serializer = ProductSerializer(
                ordered_products, many=True, context={'request': request}
            )
            return Response({'products': serializer.data})

        return Response({'products': []})

    def post(self, request):
        """Add product to recently viewed."""
        product_id = request.data.get('product_id')

        if not product_id:
            return Response(
                {'error': 'Product ID required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response(
                {'error': ERROR_PRODUCT_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND
            )

        recently_viewed = request.session.get('recently_viewed', [])

        # Remove if already exists (to move to front)
        if product_id in recently_viewed:
            recently_viewed.remove(product_id)

        # Add to front
        recently_viewed.insert(0, product_id)

        # Keep only last 20
        request.session['recently_viewed'] = recently_viewed[:20]

        return Response({'success': True})


class AdvancedSearchView(APIView):
    """API view for advanced product search with faceted filters."""

    def get(self, request):
        """Advanced search with aggregations."""
        query = request.query_params.get('q', '').strip()
        category = request.query_params.get('category', '')
        vendor = request.query_params.get('vendor', '')
        min_price = request.query_params.get('min_price', '')
        max_price = request.query_params.get('max_price', '')
        in_stock = request.query_params.get('in_stock', '')
        rating = request.query_params.get('min_rating', '')
        sort = request.query_params.get('sort', 'relevance')
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 20))

        # Base queryset with optimization
        queryset = Product.objects.filter(is_active=True).select_related(
            'category', 'vendor'
        ).prefetch_related('reviews', 'images')

        # Apply filters
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(brand__icontains=query) |
                Q(technical_name__icontains=query) |
                Q(category__name__icontains=query) |
                Q(vendor__name__icontains=query)
            )

        if category:
            queryset = queryset.filter(category__slug=category)

        if vendor:
            queryset = queryset.filter(vendor__slug=vendor)

        if min_price:
            queryset = queryset.filter(price__gte=float(min_price))

        if max_price:
            queryset = queryset.filter(price__lte=float(max_price))

        if in_stock == '1':
            queryset = queryset.filter(stock_quantity__gt=0)

        if rating:
            queryset = queryset.annotate(
                avg_rating=models.Avg('reviews__rating')
            ).filter(avg_rating__gte=float(rating))

        # Get facets before sorting/pagination
        facets = {
            'categories': list(
                queryset.values('category__slug', 'category__name').annotate(
                    count=Count('id')
                ).order_by('-count')[:20]
            ),
            'vendors': list(
                queryset.values('vendor__slug', 'vendor__name').annotate(
                    count=Count('id')
                ).order_by('-count')[:20]
            ),
            'price_range': queryset.aggregate(
                min_price=Min('price'),
                max_price=Max('price')
            ),
            'total_count': queryset.count()
        }

        # Apply sorting
        if sort == 'price_low':
            queryset = queryset.order_by('price')
        elif sort == 'price_high':
            queryset = queryset.order_by('-price')
        elif sort == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort == 'name':
            queryset = queryset.order_by('name')
        elif sort == 'rating':
            queryset = queryset.annotate(
                avg_rating=models.Avg('reviews__rating')
            ).order_by('-avg_rating')
        else:
            queryset = queryset.order_by('-created_at')

        # Pagination
        start = (page - 1) * per_page
        end = start + per_page
        products = queryset[start:end]

        serializer = ProductSerializer(products, many=True, context={'request': request})

        return Response({
            'products': serializer.data,
            'facets': facets,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': facets['total_count'],
                'pages': (facets['total_count'] + per_page - 1) // per_page
            }
        })


class DashboardStatsView(APIView):
    """API view for admin dashboard statistics."""
    permission_classes = [permissions.IsAdminUser]

    def get(self, _request):
        """Get comprehensive dashboard statistics."""
        now = timezone.now()
        today = now.date()
        thirty_days_ago = now - timezone.timedelta(days=30)
        seven_days_ago = now - timezone.timedelta(days=7)

        # Orders statistics
        all_orders = Order.objects.all()
        paid_orders = all_orders.filter(paid=True)

        # Revenue calculations
        total_revenue = paid_orders.aggregate(
            total=Sum('paid_amount')
        )['total'] or 0

        monthly_revenue = paid_orders.filter(
            created_at__gte=thirty_days_ago
        ).aggregate(total=Sum('paid_amount'))['total'] or 0

        weekly_revenue = paid_orders.filter(
            created_at__gte=seven_days_ago
        ).aggregate(total=Sum('paid_amount'))['total'] or 0

        today_revenue = paid_orders.filter(
            created_at__date=today
        ).aggregate(total=Sum('paid_amount'))['total'] or 0

        # Order counts
        orders_stats = {
            'total': all_orders.count(),
            'paid': paid_orders.count(),
            'pending': all_orders.filter(status='pending').count(),
            'processing': all_orders.filter(status='processing').count(),
            'shipped': all_orders.filter(status='shipped').count(),
            'delivered': all_orders.filter(status='delivered').count(),
            'cancelled': all_orders.filter(status='cancelled').count(),
            'today': all_orders.filter(created_at__date=today).count(),
        }

        # Products statistics
        products_stats = {
            'total': Product.objects.count(),
            'active': Product.objects.filter(is_active=True).count(),
            'out_of_stock': Product.objects.filter(stock_quantity=0).count(),
            'low_stock': Product.objects.filter(
                stock_quantity__lte=models.F('low_stock_threshold'),
                stock_quantity__gt=0
            ).count(),
        }

        # Users statistics (User already imported at top)
        users_stats = {
            'total': User.objects.count(),
            'new_today': User.objects.filter(date_joined__date=today).count(),
            'new_this_week': User.objects.filter(date_joined__gte=seven_days_ago).count(),
            'new_this_month': User.objects.filter(date_joined__gte=thirty_days_ago).count(),
        }

        # Vendors statistics
        vendors_stats = {
            'total': Vendor.objects.count(),
            'with_products': Vendor.objects.annotate(
                product_count=Count('product')
            ).filter(product_count__gt=0).count(),
        }

        # Recent orders
        recent_orders = Order.objects.order_by('-created_at')[:10].values(
            'id', 'first_name', 'last_name', 'paid_amount', 'status', 'created_at'
        )

        # Top selling products
        top_products = OrderItem.objects.filter(
            order__paid=True
        ).values('product__name', 'product__slug').annotate(
            total_sold=Sum('quantity'),
            revenue=Sum(models.F('price') * models.F('quantity'))
        ).order_by('-total_sold')[:10]

        return Response({
            'revenue': {
                'total': float(total_revenue),
                'monthly': float(monthly_revenue),
                'weekly': float(weekly_revenue),
                'today': float(today_revenue),
            },
            'orders': orders_stats,
            'products': products_stats,
            'users': users_stats,
            'vendors': vendors_stats,
            'recent_orders': list(recent_orders),
            'top_products': list(top_products),
            'timestamp': now.isoformat(),
        })


class BulkInventoryUpdateView(APIView):
    """API view for bulk inventory updates."""
    permission_classes = [permissions.IsAuthenticated, IsVendorUser]

    def post(self, request):
        """Update inventory for multiple products at once."""
        user = request.user
        updates = request.data.get('updates', [])

        if not hasattr(user, 'vendor'):
            return Response(
                {'error': ERROR_NOT_VENDOR},
                status=status.HTTP_403_FORBIDDEN
            )

        if not updates:
            return Response(
                {'error': 'No updates provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        vendor = user.vendor
        results = []
        errors = []

        for update in updates:
            product_id = update.get('product_id')
            new_quantity = update.get('quantity')
            notes = update.get('notes', '')

            try:
                product = Product.objects.get(id=product_id, vendor=vendor)
                previous_stock = product.stock_quantity
                product.stock_quantity = new_quantity
                product.save()

                # Log inventory change
                InventoryLog.objects.create(
                    product=product,
                    action='bulk_adjustment',
                    quantity=new_quantity - previous_stock,
                    previous_stock=previous_stock,
                    new_stock=new_quantity,
                    notes=notes,
                    created_by=user
                )

                results.append({
                    'product_id': product_id,
                    'success': True,
                    'previous_stock': previous_stock,
                    'new_stock': new_quantity
                })
            except Product.DoesNotExist:
                errors.append({
                    'product_id': product_id,
                    'error': 'Product not found or not owned by vendor'
                })
            except (ValueError, TypeError) as e:
                errors.append({
                    'product_id': product_id,
                    'error': str(e)
                })

        return Response({
            'success': len(errors) == 0,
            'updated': results,
            'errors': errors
        })


# ============================================================================
# ADDITIONAL POWERFUL API VIEWS
# ============================================================================


class ProductCompareView(APIView):
    """API view for comparing multiple products side by side."""

    def get(self, request):
        """Compare products by IDs."""
        product_ids = request.query_params.get('ids', '').split(',')
        product_ids = [int(pid.strip()) for pid in product_ids if pid.strip().isdigit()]

        if not product_ids:
            return Response(
                {'error': 'No product IDs provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(product_ids) > 5:
            return Response(
                {'error': 'Maximum 5 products can be compared'},
                status=status.HTTP_400_BAD_REQUEST
            )

        products = Product.objects.filter(
            id__in=product_ids,
            is_active=True
        ).select_related('category', 'vendor').prefetch_related('reviews', 'images')

        comparison_data = []
        for product in products:
            avg_rating = product.reviews.aggregate(avg=models.Avg('rating'))['avg'] or 0
            comparison_data.append({
                'id': product.id,
                'name': product.name,
                'slug': product.slug,
                'image': product.image.url if product.image else None,
                'price': float(product.price),
                'mrp': float(product.mrp) if product.mrp else None,
                'discount_percentage': product.discount_percentage,
                'category': product.category.name,
                'vendor': product.vendor.name,
                'brand': product.brand,
                'description': product.description,
                'short_description': product.short_description,
                'technical_name': product.technical_name,
                'target_crops': product.target_crops,
                'in_stock': product.is_in_stock,
                'stock_quantity': product.stock_quantity,
                'average_rating': round(avg_rating, 1),
                'review_count': product.reviews.count(),
                'specifications': {
                    'brand': product.brand,
                    'technical_name': product.technical_name,
                    'target_crops': product.target_crops,
                    'usage_instructions': product.usage_instructions,
                    'safety_guidelines': product.safety_guidelines,
                }
            })

        return Response({
            'products': comparison_data,
            'count': len(comparison_data)
        })


class ExportDataView(APIView):
    """API view for exporting data in various formats."""
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        """Export data as CSV."""
        export_type = request.query_params.get('type', 'orders')
        date_from = request.query_params.get('from', '')
        date_to = request.query_params.get('to', '')

        if export_type == 'orders':
            return self._export_orders(date_from, date_to)
        elif export_type == 'products':
            return self._export_products()
        elif export_type == 'users':
            return self._export_users(date_from, date_to)
        elif export_type == 'vendors':
            return self._export_vendors()
        else:
            return Response({'error': 'Invalid export type'}, status=status.HTTP_400_BAD_REQUEST)

    def _export_orders(self, date_from, date_to):
        """Export orders to CSV."""
        orders = Order.objects.select_related('user').prefetch_related(
            'items__product', 'items__vendor'
        )

        if date_from:
            orders = orders.filter(created_at__date__gte=date_from)
        if date_to:
            orders = orders.filter(created_at__date__lte=date_to)

        response = HttpResponse(content_type=CSV_CONTENT_TYPE)
        response['Content-Disposition'] = 'attachment; filename="orders_export.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Order ID', 'Customer Name', 'Email', 'Phone', 'Address',
            'Total Amount', 'Payment Status', 'Order Status', 'Created At'
        ])

        for order in orders:
            writer.writerow([
                order.id,
                f"{order.first_name} {order.last_name}",
                order.email,
                order.phone,
                order.address,
                order.paid_amount or 0,
                'Paid' if order.paid else 'Unpaid',
                order.status,
                order.created_at.strftime('%Y-%m-%d %H:%M')
            ])

        return response

    def _export_products(self):
        """Export products to CSV."""
        products = Product.objects.all().select_related('category', 'vendor')

        response = HttpResponse(content_type=CSV_CONTENT_TYPE)
        response['Content-Disposition'] = 'attachment; filename="products_export.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Name', 'Category', 'Vendor', 'Price', 'MRP', 'Stock',
            'Brand', 'Active', 'Created At'
        ])

        for product in products:
            writer.writerow([
                product.id,
                product.name,
                product.category.name,
                product.vendor.name,
                product.price,
                product.mrp or '',
                product.stock_quantity,
                product.brand,
                'Yes' if product.is_active else 'No',
                product.created_at.strftime('%Y-%m-%d')
            ])

        return response

    def _export_users(self, date_from, date_to):
        """Export users to CSV."""
        users = User.objects.all()

        if date_from:
            users = users.filter(date_joined__date__gte=date_from)
        if date_to:
            users = users.filter(date_joined__date__lte=date_to)

        response = HttpResponse(content_type=CSV_CONTENT_TYPE)
        response['Content-Disposition'] = 'attachment; filename="users_export.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Username', 'Email', 'First Name', 'Last Name',
            'Date Joined', 'Active'
        ])

        for user in users:
            writer.writerow([
                user.id,
                user.username,
                user.email,
                user.first_name,
                user.last_name,
                user.date_joined.strftime('%Y-%m-%d'),
                'Yes' if user.is_active else 'No'
            ])

        return response

    def _export_vendors(self):
        """Export vendors to CSV."""
        vendors = Vendor.objects.all()

        response = HttpResponse(content_type=CSV_CONTENT_TYPE)
        response['Content-Disposition'] = 'attachment; filename="vendors_export.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Name', 'City', 'Products Count'])

        for vendor in vendors:
            writer.writerow([
                vendor.id,
                vendor.name,
                vendor.city,
                vendor.products.count()
            ])

        return response


class InvoiceView(APIView):
    """API view for generating order invoices."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, order_id):
        """Get invoice data for an order."""
        try:
            order = Order.objects.select_related('user').prefetch_related(
                'items__product', 'items__vendor'
            ).get(id=order_id)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check permission
        if order.user != request.user and not request.user.is_staff:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        # Calculate totals
        items_data = []
        subtotal = 0
        for item in order.items.all():
            item_total = float(item.price) * item.quantity
            subtotal += item_total
            items_data.append({
                'product_name': item.product.name,
                'product_sku': item.product.slug,
                'vendor': item.vendor.name,
                'quantity': item.quantity,
                'unit_price': float(item.price),
                'total': item_total
            })

        # Calculate tax (18% GST)
        tax_rate = 0.18
        tax = subtotal * tax_rate
        total = subtotal + tax

        invoice_data = {
            'invoice_number': f'INV-{order.id:06d}',
            'order_id': order.id,
            'order_date': order.created_at.isoformat(),
            'customer': {
                'name': f"{order.first_name} {order.last_name}",
                'email': order.email,
                'phone': order.phone,
                'address': order.address,
                'city': order.place,
                'pincode': order.zipcode
            },
            'items': items_data,
            'subtotal': round(subtotal, 2),
            'tax_rate': tax_rate * 100,
            'tax_amount': round(tax, 2),
            'total': round(total, 2),
            'payment_status': 'Paid' if order.paid else 'Pending',
            'payment_method': order.payment_method,
            'generated_at': timezone.now().isoformat()
        }

        return Response(invoice_data)


class ActivityLogView(APIView):
    """API view for user activity tracking."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get user's activity log."""
        user = request.user
        limit = int(request.query_params.get('limit', 20))

        activities = []

        # Recent orders
        recent_orders = Order.objects.filter(user=user).order_by('-created_at')[:5]
        for order in recent_orders:
            activities.append({
                'type': 'order',
                'action': 'placed_order',
                'description': f'Placed order #{order.id}',
                'amount': float(order.paid_amount) if order.paid_amount else 0,
                'timestamp': order.created_at.isoformat(),
                'link': f'/orders/{order.id}/'
            })

        # Recent reviews
        recent_reviews = Review.objects.filter(user=user).order_by('-created_at')[:5]
        for review in recent_reviews:
            activities.append({
                'type': 'review',
                'action': 'wrote_review',
                'description': f'Reviewed {review.product.name}',
                'rating': review.rating,
                'timestamp': review.created_at.isoformat(),
                'link': f'/product/{review.product.slug}/'
            })

        # Recent wishlist additions
        recent_wishlist = Wishlist.objects.filter(user=user).order_by('-added_at')[:5]
        for item in recent_wishlist:
            activities.append({
                'type': 'wishlist',
                'action': 'added_to_wishlist',
                'description': f'Added {item.product.name} to wishlist',
                'timestamp': item.added_at.isoformat(),
                'link': f'/product/{item.product.slug}/'
            })

        # Sort by timestamp
        activities.sort(key=lambda x: x['timestamp'], reverse=True)

        return Response({
            'activities': activities[:limit],
            'count': len(activities)
        })

    def post(self, request):
        """Log a user activity."""
        activity_type = request.data.get('type')
        action = request.data.get('action')
        data = request.data.get('data', {})

        # Store in session for now (can be extended to database)
        activity_log = request.session.get('activity_log', [])
        activity_log.insert(0, {
            'type': activity_type,
            'action': action,
            'data': data,
            'timestamp': timezone.now().isoformat()
        })
        request.session['activity_log'] = activity_log[:50]  # Keep last 50

        return Response({'success': True})


class WebhookView(APIView):
    """API view for handling payment webhooks."""
    permission_classes = []  # No auth needed for webhooks

    def post(self, request, provider):
        """Handle webhook from payment provider."""
        if provider == 'stripe':
            return self._handle_stripe_webhook(request)
        elif provider == 'razorpay':
            return self._handle_razorpay_webhook(request)
        else:
            return Response({'error': 'Unknown provider'}, status=status.HTTP_400_BAD_REQUEST)

    def _handle_stripe_webhook(self, request):
        """Handle Stripe webhook events."""
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_ENDPOINT_SECRET
            )
        except ValueError:
            return Response({'error': 'Invalid payload'}, status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError:
            return Response({'error': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)

        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            self._fulfill_order(session)
        elif event['type'] == 'payment_intent.succeeded':
            intent = event['data']['object']
            logger.info("Payment succeeded for intent: %s", intent['id'])

        return Response({'received': True})

    def _handle_razorpay_webhook(self, request):
        """Handle Razorpay webhook events."""
        # Verify webhook signature
        razorpay_signature = request.META.get('HTTP_X_RAZORPAY_SIGNATURE', '')
        webhook_secret = getattr(settings, 'RAZORPAY_WEBHOOK_SECRET', '')

        if webhook_secret:
            expected_signature = hmac.new(
                webhook_secret.encode(),
                request.body,
                hashlib.sha256
            ).hexdigest()

            if not hmac.compare_digest(razorpay_signature, expected_signature):
                return Response({'error': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)

        # Process the webhook
        payload = json.loads(request.body)
        event_type = payload.get('event')

        if event_type == 'payment.captured':
            payment = payload.get('payload', {}).get('payment', {}).get('entity', {})
            order_id = payment.get('notes', {}).get('order_id')
            if order_id:
                self._mark_order_paid(order_id, payment.get('id'))

        return Response({'received': True})

    def _fulfill_order(self, session):
        """Fulfill order after successful payment."""
        payment_intent = session.get('payment_intent')
        try:
            order = Order.objects.get(payment_intent=payment_intent)
            order.paid = True
            order.status = 'confirmed'
            order.save()
            logger.info("Order #%d fulfilled", order.id)
        except Order.DoesNotExist:
            logger.error("Order not found for payment intent: %s", payment_intent)

    def _mark_order_paid(self, order_id, payment_id):
        """Mark order as paid."""
        try:
            order = Order.objects.get(id=order_id)
            order.paid = True
            order.payment_intent = payment_id
            order.status = 'confirmed'
            order.save()
            logger.info("Order #%d marked as paid", order.id)
        except Order.DoesNotExist:
            logger.error("Order %s not found", order_id)


class HealthCheckView(APIView):
    """API view for system health check."""

    permission_classes = []

    def get(self, _request):
        """Check system health."""
        health = {
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'components': {}
        }

        # Database check
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            health['components']['database'] = {'status': 'healthy'}
        except Exception as e:  # pylint: disable=broad-exception-caught
            # Deliberately catching all exceptions to report health status
            health['components']['database'] = {'status': 'unhealthy', 'error': str(e)}
            health['status'] = 'degraded'

        # Check counts
        health['components']['stats'] = {
            'products': Product.objects.count(),
            'orders': Order.objects.count(),
            'vendors': Vendor.objects.count()
        }

        return Response(health)


class PostgreSQLAnalyticsView(View):
    """API view for PostgreSQL-specific analytics and metrics."""

    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        """Get comprehensive PostgreSQL analytics."""
        analytics = {
            'timestamp': timezone.now().isoformat(),
            'database_info': self._get_database_info(),
            'performance_metrics': self._get_performance_metrics(),
            'table_stats': self._get_table_stats(),
            'analytics': self._get_business_analytics(),
        }

        # Optional: Include detailed metrics
        if request.query_params.get('detailed', '') == 'true':
            analytics['index_usage'] = self._get_index_usage()
            analytics['slow_queries'] = self._get_slow_queries()

        return Response(analytics)

    def _get_database_info(self):
        """Get PostgreSQL database information."""
        info = {'engine': 'unknown', 'version': 'unknown'}
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()[0]
                info['version'] = version.split(',')[0] if version else 'unknown'

                cursor.execute("SELECT current_database();")
                info['database'] = cursor.fetchone()[0]

                cursor.execute("SELECT pg_size_pretty(pg_database_size(current_database()));")
                info['size'] = cursor.fetchone()[0]

                info['engine'] = 'PostgreSQL'
        except Exception:  # pylint: disable=broad-exception-caught
            info['engine'] = settings.DATABASES['default']['ENGINE']
        return info

    def _get_performance_metrics(self):
        """Get database performance metrics."""
        metrics = {}
        try:
            with connection.cursor() as cursor:
                # Active connections
                cursor.execute("""
                    SELECT COUNT(*) FROM pg_stat_activity
                    WHERE datname = current_database();
                """)
                metrics['active_connections'] = cursor.fetchone()[0]

                # Cache hit ratio
                cursor.execute("""
                    SELECT
                        ROUND(100.0 * SUM(heap_blks_hit) /
                        NULLIF(SUM(heap_blks_hit) + SUM(heap_blks_read), 0), 2) as ratio
                    FROM pg_statio_user_tables;
                """)
                result = cursor.fetchone()[0]
                metrics['cache_hit_ratio'] = float(result) if result else 0

                # Transaction stats
                cursor.execute("""
                    SELECT xact_commit, xact_rollback
                    FROM pg_stat_database
                    WHERE datname = current_database();
                """)
                row = cursor.fetchone()
                if row:
                    metrics['transactions_committed'] = row[0]
                    metrics['transactions_rolled_back'] = row[1]

        except Exception:  # pylint: disable=broad-exception-caught
            metrics['error'] = 'Unable to fetch PostgreSQL metrics'
        return metrics

    def _get_table_stats(self):
        """Get table statistics."""
        stats = []
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        relname as table_name,
                        n_live_tup as row_count,
                        pg_size_pretty(pg_total_relation_size(relid)) as total_size,
                        n_tup_ins as inserts,
                        n_tup_upd as updates,
                        n_tup_del as deletes
                    FROM pg_stat_user_tables
                    WHERE schemaname = 'public'
                    ORDER BY n_live_tup DESC
                    LIMIT 15;
                """)
                columns = ['table', 'rows', 'size', 'inserts', 'updates', 'deletes']
                for row in cursor.fetchall():
                    stats.append(dict(zip(columns, row, strict=False)))
        except Exception:  # pylint: disable=broad-exception-caught
            stats = [{'error': 'Unable to fetch table stats'}]
        return stats

    def _get_business_analytics(self):
        """Get business analytics from database."""
        analytics = {}
        try:
            with connection.cursor() as cursor:
                # Today's metrics
                cursor.execute("""
                    SELECT
                        COUNT(*) as orders_today,
                        COALESCE(SUM(paid_amount), 0) as revenue_today
                    FROM store_order
                    WHERE DATE(created_at) = CURRENT_DATE AND paid = true;
                """)
                row = cursor.fetchone()
                analytics['today'] = {
                    'orders': row[0],
                    'revenue': float(row[1])
                }

                # This week metrics
                cursor.execute("""
                    SELECT
                        COUNT(*) as orders,
                        COALESCE(SUM(paid_amount), 0) as revenue
                    FROM store_order
                    WHERE created_at >= CURRENT_DATE - INTERVAL '7 days' AND paid = true;
                """)
                row = cursor.fetchone()
                analytics['week'] = {
                    'orders': row[0],
                    'revenue': float(row[1])
                }

                # This month metrics
                cursor.execute("""
                    SELECT
                        COUNT(*) as orders,
                        COALESCE(SUM(paid_amount), 0) as revenue,
                        COUNT(DISTINCT user_id) as unique_customers
                    FROM store_order
                    WHERE DATE_TRUNC('month', created_at) = DATE_TRUNC('month', CURRENT_DATE)
                    AND paid = true;
                """)
                row = cursor.fetchone()
                analytics['month'] = {
                    'orders': row[0],
                    'revenue': float(row[1]),
                    'unique_customers': row[2]
                }

                # Top products (last 30 days)
                cursor.execute("""
                    SELECT p.name, SUM(oi.quantity) as sold
                    FROM store_orderitem oi
                    JOIN store_product p ON oi.product_id = p.id
                    JOIN store_order o ON oi.order_id = o.id
                    WHERE o.created_at >= CURRENT_DATE - INTERVAL '30 days'
                    GROUP BY p.id, p.name
                    ORDER BY sold DESC
                    LIMIT 5;
                """)
                analytics['top_products'] = [
                    {'name': row[0], 'sold': row[1]}
                    for row in cursor.fetchall()
                ]

                # Low stock products
                cursor.execute("""
                    SELECT name, stock_quantity
                    FROM store_product
                    WHERE is_active = true AND stock_quantity <= 5
                    ORDER BY stock_quantity ASC
                    LIMIT 10;
                """)
                analytics['low_stock'] = [
                    {'name': row[0], 'stock': row[1]}
                    for row in cursor.fetchall()
                ]

        except Exception:  # pylint: disable=broad-exception-caught
            analytics['error'] = 'Unable to fetch business analytics'
        return analytics

    def _get_index_usage(self):
        """Get index usage statistics."""
        usage = []
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        indexrelname as index_name,
                        idx_scan as scans,
                        idx_tup_read as tuples_read,
                        idx_tup_fetch as tuples_fetched,
                        pg_size_pretty(pg_relation_size(indexrelid)) as size
                    FROM pg_stat_user_indexes
                    ORDER BY idx_scan DESC
                    LIMIT 20;
                """)
                columns = ['index', 'scans', 'tuples_read', 'tuples_fetched', 'size']
                for row in cursor.fetchall():
                    usage.append(dict(zip(columns, row, strict=False)))
        except Exception as e:
            logger.error("Error getting index usage: %s", e)
            return []

    def _get_slow_queries(self):
        """Get slow query statistics (if pg_stat_statements available)."""
        queries = []
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT query, calls, mean_time, total_time
                    FROM pg_stat_statements
                    ORDER BY mean_time DESC
                    LIMIT 10;
                """)
                for row in cursor.fetchall():
                    queries.append({
                        'query': row[0][:100],
                        'calls': row[1],
                        'mean_time_ms': round(row[2], 2),
                        'total_time_ms': round(row[3], 2)
                    })
        except Exception:  # pylint: disable=broad-exception-caught
            # pg_stat_statements extension might not be enabled
            queries = [{'note': 'pg_stat_statements not available'}]
        return queries


class DatabaseDashboardView(APIView):
    """API view for real-time database dashboard."""

    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        """Get real-time dashboard data from PostgreSQL views."""
        dashboard = {
            'timestamp': timezone.now().isoformat(),
            'realtime': {},
            'trends': {},
        }

        try:
            with connection.cursor() as cursor:
                # Try to get data from materialized views
                try:
                    cursor.execute("SELECT * FROM v_dashboard_stats;")
                    row = cursor.fetchone()
                    if row:
                        dashboard['realtime'] = {
                            'orders_today': row[0],
                            'revenue_today': float(row[1]) if row[1] else 0,
                            'active_products': row[2],
                            'low_stock_count': row[3]
                        }
                except Exception:  # pylint: disable=broad-exception-caught
                    # View might not exist, calculate directly
                    cursor.execute("""
                        SELECT
                            (SELECT COUNT(*) FROM store_order WHERE DATE(created_at) = CURRENT_DATE),
                            (SELECT COALESCE(SUM(paid_amount), 0) FROM store_order
                             WHERE DATE(created_at) = CURRENT_DATE AND paid = true),
                            (SELECT COUNT(*) FROM store_product WHERE is_active = true),
                            (SELECT COUNT(*) FROM store_product
                             WHERE stock_quantity <= 10 AND is_active = true);
                    """)
                    row = cursor.fetchone()
                    dashboard['realtime'] = {
                        'orders_today': row[0],
                        'revenue_today': float(row[1]) if row[1] else 0,
                        'active_products': row[2],
                        'low_stock_count': row[3]
                    }

                # Get hourly sales trend
                cursor.execute("""
                    SELECT
                        EXTRACT(HOUR FROM created_at) as hour,
                        COUNT(*) as orders,
                        COALESCE(SUM(paid_amount), 0) as revenue
                    FROM store_order
                    WHERE DATE(created_at) = CURRENT_DATE AND paid = true
                    GROUP BY EXTRACT(HOUR FROM created_at)
                    ORDER BY hour;
                """)
                dashboard['trends']['hourly_sales'] = [
                    {'hour': int(row[0]), 'orders': row[1], 'revenue': float(row[2])}
                    for row in cursor.fetchall()
                ]

                # Get daily sales trend (last 7 days)
                cursor.execute("""
                    SELECT
                        DATE(created_at) as date,
                        COUNT(*) as orders,
                        COALESCE(SUM(paid_amount), 0) as revenue
                    FROM store_order
                    WHERE created_at >= CURRENT_DATE - INTERVAL '7 days' AND paid = true
                    GROUP BY DATE(created_at)
                    ORDER BY date;
                """)
                dashboard['trends']['daily_sales'] = [
                    {'date': row[0].isoformat(), 'orders': row[1], 'revenue': float(row[2])}
                    for row in cursor.fetchall()
                ]

                # Order status breakdown
                cursor.execute("""
                    SELECT status, COUNT(*)
                    FROM store_order
                    GROUP BY status;
                """)
                dashboard['order_status'] = {
                    row[0]: row[1] for row in cursor.fetchall()
                }

        except Exception as e:  # pylint: disable=broad-exception-caught
            dashboard['error'] = str(e)

        return Response(dashboard)


class ContactFormView(APIView):
    """API view for contact form submissions."""

    def post(self, request):
        """Submit a contact form."""
        name = request.data.get('name', '').strip()
        email = request.data.get('email', '').strip()
        message = request.data.get('message', '').strip()

        if not all([name, email, message]):
            return Response(
                {'error': 'Name, email, and message are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return Response(
                {'error': ERROR_INVALID_EMAIL},
                status=status.HTTP_400_BAD_REQUEST
            )

        contact = Contact.objects.create(
            name=name,
            email=email,
            message=message
        )

        return Response({
            'success': True,
            'message': 'Thank you for your message. We will get back to you soon.',
            'reference': f'CONTACT-{contact.id}'
        }, status=status.HTTP_201_CREATED)


class SubscriptionView(APIView):
    """API view for newsletter subscriptions."""

    def post(self, request):
        """Subscribe to newsletter."""
        email = request.data.get('email', '').strip()

        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate email
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return Response({'error': ERROR_INVALID_EMAIL}, status=status.HTTP_400_BAD_REQUEST)

        # Store subscription (can be extended to a Subscription model)
        try:
            _, created = Subscription.objects.get_or_create(email=email)
            if created:
                return Response({
                    'success': True,
                    'message': 'Successfully subscribed to newsletter'
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': True,
                    'message': 'Email already subscribed'
                })
        except (ImportError, LookupError) as exc:  # pylint: disable=broad-exception-caught
            # Subscription model might not exist or migration not applied
            logger.warning("Newsletter subscription model issue: %s", exc)
            return Response({
                'success': True,
                'message': 'Subscription recorded'
            }, status=status.HTTP_201_CREATED)


# ==================== ENHANCED RECOMMENDATION ENDPOINTS ====================


class PersonalizedRecommendationsView(APIView):
    """API view for getting personalized product recommendations."""

    def get(self, request):
        """Get personalized recommendations for the current user."""
        service = RecommendationService(user=request.user)
        recommendations = service.get_personalized_recommendations(limit=12)

        serializer = ProductSerializer(recommendations, many=True)
        return Response({
            'recommendations': serializer.data,
            'type': 'personalized' if request.user.is_authenticated else 'trending'
        })


class SimilarProductsView(APIView):
    """API view for getting similar products."""

    def get(self, request, product_id):
        """Get products similar to the specified product."""
        product = get_object_or_404(Product, id=product_id)
        service = RecommendationService(user=request.user)
        similar = service.get_similar_products(product, limit=6)

        serializer = ProductSerializer(similar, many=True)
        return Response({
            'similar_products': serializer.data,
            'product_id': product_id
        })


class FrequentlyBoughtTogetherView(APIView):
    """API view for getting frequently bought together products."""

    def get(self, _request, product_id):
        """Get products frequently purchased with the specified product."""
        product = get_object_or_404(Product, id=product_id)
        service = RecommendationService()
        together = service.get_frequently_bought_together(product, limit=4)

        serializer = ProductSerializer(together, many=True)
        return Response({
            'frequently_bought_together': serializer.data,
            'product_id': product_id
        })


class EnhancedTrendingProductsView(APIView):
    """API view for getting trending products with caching."""

    @method_decorator(cache_page(settings.CACHE_TTL_SHORT))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        """Get trending products based on recent activity."""
        days = int(request.query_params.get('days', 7))
        limit = int(request.query_params.get('limit', 12))

        service = RecommendationService()
        trending = service.get_trending_products(limit=limit, days=days)

        serializer = ProductSerializer(trending, many=True)
        return Response({
            'trending_products': serializer.data,
            'period_days': days
        })


class SeasonalRecommendationsView(APIView):
    """API view for getting seasonal/agricultural recommendations."""

    @method_decorator(cache_page(settings.CACHE_TTL_MEDIUM))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, _request):
        """Get seasonal recommendations based on agricultural calendar."""
        products = get_seasonal_recommendations(limit=8)

        serializer = ProductSerializer(products, many=True)
        return Response({
            'seasonal_products': serializer.data
        })


class CartRecommendationsView(APIView):
    """API view for getting cart-based recommendations."""

    def get(self, request):
        """Get recommendations based on cart contents."""
        cart = Cart(request)
        recommendations = get_recommendations_for_cart(cart, limit=4)

        serializer = ProductSerializer(recommendations, many=True)
        return Response({
            'cart_recommendations': serializer.data,
            'cart_count': len(cart)
        })


class StartOrderView(APIView):
    """
    API endpoint to start a checkout session (Stripe or COD).
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *_args, **_kwargs):
        """Start a checkout session for card payment or COD."""
        cart = Cart(request)
        data = request.data

        # Calculate total using cart method
        total_price = cart.get_total_cost()
        payment_method = data.get('payment_method', 'card')

        # Create Order
        user = request.user if request.user.is_authenticated else None

        order = Order.objects.create(
            user=user,
            first_name=bleach.clean(data.get('first_name', '')),
            last_name=bleach.clean(data.get('last_name', '')),
            email=bleach.clean(data.get('email', '')),
            address=bleach.clean(data.get('address', '')),
            zipcode=bleach.clean(data.get('zipcode', '')),
            place=bleach.clean(data.get('place', '')),
            phone=bleach.clean(data.get('phone', '')),
            paid_amount=total_price,
            paid=False,
            payment_method=payment_method,
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

            if payment_method == 'card':
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

        # Handle COD
        if payment_method == 'cod':
            cart.clear()
            return Response({
                'success': True,
                'order_id': order.id,
                'message': 'Order placed successfully!'
            })

        # Create Stripe Session for Card payments
        success_url = request.build_absolute_uri('/cart/success/')
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
            order.payment_intent = session.id
            order.save()
            return Response({'session': session})
        except stripe.error.StripeError as e:
            order.delete() # Delete the order if session creation fails
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================
# AGRIM-STYLE API ENDPOINTS
# ============================================

class CropListView(APIView):
    """API view for listing all crops."""
    permission_classes = [permissions.AllowAny]

    def get(self, _request):
        """Get list of popular crops."""
        crops = Crop.objects.filter(is_popular=True).order_by('order', 'name')[:20]
        return Response({
            'crops': [
                {
                    'id': crop.id,
                    'name': crop.name,
                    'slug': crop.slug,
                    'hindi_name': crop.hindi_name,
                    'icon': crop.icon,
                    'image': crop.image.url if crop.image else None,
                    'season': crop.season
                }
                for crop in crops
            ]
        })


class DiseaseListView(APIView):
    """API view for listing plant diseases."""
    permission_classes = [permissions.AllowAny]

    def get(self, _request):
        """Get list of common plant diseases."""
        diseases = Disease.objects.filter(is_common=True).order_by('order', 'name')[:20]
        return Response({
            'diseases': [
                {
                    'id': disease.id,
                    'name': disease.name,
                    'slug': disease.slug,
                    'hindi_name': disease.hindi_name,
                    'icon': disease.icon,
                    'image': disease.image.url if disease.image else None,
                    'symptoms': disease.symptoms
                }
                for disease in diseases
            ]
        })


class ProductsByCropView(APIView):
    """API view for products by crop."""
    permission_classes = [permissions.AllowAny]

    def get(self, _request, crop_slug):
        """Get products related to a specific crop."""
        try:
            crop = Crop.objects.get(slug=crop_slug)
            mappings = ProductCropMapping.objects.filter(
                crop=crop
            ).select_related('product').order_by('-effectiveness_rating')[:20]

            products = [m.product for m in mappings]
            serializer = ProductSerializer(products, many=True)
            return Response({
                'crop': {
                    'id': crop.id,
                    'name': crop.name,
                    'icon': crop.icon
                },
                'products': serializer.data
            })
        except Crop.DoesNotExist:
            return Response({'error': 'Crop not found'}, status=status.HTTP_404_NOT_FOUND)


class ProductsByDiseaseView(APIView):
    """API view for products by disease."""
    permission_classes = [permissions.AllowAny]

    def get(self, _request, disease_slug):
        """Get products related to a specific disease."""
        try:
            disease = Disease.objects.get(slug=disease_slug)
            mappings = ProductDiseaseMapping.objects.filter(
                disease=disease
            ).select_related('product').order_by('-effectiveness_rating')[:20]

            products = [m.product for m in mappings]
            serializer = ProductSerializer(products, many=True)
            return Response({
                'disease': {
                    'id': disease.id,
                    'name': disease.name,
                    'icon': disease.icon,
                    'symptoms': disease.symptoms
                },
                'products': serializer.data
            })
        except Disease.DoesNotExist:
            return Response({'error': 'Disease not found'}, status=status.HTTP_404_NOT_FOUND)


class PopularInCityView(APIView):
    """API view for products popular in a city."""
    permission_classes = [permissions.AllowAny]

    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    def get(self, _request, city):
        """Get products popular in a specific city."""
        popular = LocationPopularity.objects.filter(
            city__iexact=city
        ).select_related('product').order_by('-popularity_score')[:12]

        products = [p.product for p in popular if p.product.is_active]
        serializer = ProductSerializer(products, many=True)
        return Response({
            'city': city,
            'products': serializer.data
        })


class DealOfDayView(APIView):
    """API view for deal of the day products."""
    permission_classes = [permissions.AllowAny]

    def get(self, _request):
        """Get today's deal and associated products."""
        today = timezone.now().date()

        try:
            deal = DealOfTheDay.objects.get(date=today, is_active=True)
            products = deal.products.filter(is_active=True)[:10]
            serializer = ProductSerializer(products, many=True)

            # Calculate time remaining
            now = timezone.now()
            end_datetime = timezone.make_aware(
                timezone.datetime.combine(today, deal.end_time)
            )
            time_remaining = (end_datetime - now).total_seconds()

            return Response({
                'deal': {
                    'title': deal.title,
                    'discount_percentage': deal.discount_percentage,
                    'time_remaining_seconds': max(0, int(time_remaining)),
                    'is_live': deal.is_live
                },
                'products': serializer.data
            })
        except DealOfTheDay.DoesNotExist:
            # Return trending products as fallback
            products = Product.objects.filter(is_active=True).order_by('-created_at')[:10]
            serializer = ProductSerializer(products, many=True)
            return Response({
                'deal': None,
                'products': serializer.data
            })


class PriceAlertView(APIView):
    """API view for price alerts."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get user's active price alerts."""
        alerts = PriceAlert.objects.filter(
            user=request.user,
            is_active=True
        ).select_related('product')

        return Response({
            'alerts': [
                {
                    'id': alert.id,
                    'product': ProductSerializer(alert.product).data,
                    'target_price': float(alert.target_price),
                    'current_price': float(alert.product.price),
                    'is_triggered': alert.is_triggered,
                    'created_at': alert.created_at.isoformat()
                }
                for alert in alerts
            ]
        })

    def post(self, request):
        """Create or update a price alert for a product."""
        product_id = request.data.get('product_id')
        target_price = request.data.get('target_price')

        if not product_id or not target_price:
            return Response(
                {'error': 'product_id and target_price are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            product = Product.objects.get(id=product_id)
            alert, created = PriceAlert.objects.update_or_create(
                user=request.user,
                product=product,
                defaults={
                    'target_price': target_price,
                    'current_price_at_creation': product.price,
                    'is_active': True
                }
            )
            return Response({
                'success': True,
                'created': created,
                'alert_id': alert.id
            })
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)


class UserCoinView(APIView):
    """API view for user coins/rewards."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get user's coin balance and recent transactions."""
        coin, _ = UserCoin.objects.get_or_create(user=request.user)

        # Get recent transactions
        transactions = CoinTransaction.objects.filter(
            user_coin=coin
        ).order_by('-created_at')[:10]

        return Response({
            'balance': coin.balance,
            'lifetime_earned': coin.lifetime_earned,
            'lifetime_spent': coin.lifetime_spent,
            'recent_transactions': [
                {
                    'amount': t.amount,
                    'type': t.transaction_type,
                    'reason': t.reason,
                    'date': t.created_at.isoformat()
                }
                for t in transactions
            ]
        })


class LocationDetectView(APIView):
    """API view for detecting user location."""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        """Detect user's location based on IP address."""
        # Get IP-based location (simplified - in production use a geo-IP service)
        # For now, return a default location
        ip = request.META.get(
            'HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', '')
        )

        # Default to a major agricultural city
        return Response({
            'city': 'Varanasi',
            'district': 'Varanasi',
            'state': 'Uttar Pradesh',
            'pincode': '221001',
            'detected_from': 'ip' if ip else 'default'
        })


class HighMarginProductsView(APIView):
    """API view for high margin products (for retailers)."""
    permission_classes = [permissions.AllowAny]

    def get(self, _request):
        """Get products with high profit margins for retailers."""
        # Products with high margin (MRP vs price difference)
        # Using annotate with F expressions instead of deprecated .extra()
        products = Product.objects.filter(
            is_active=True,
            mrp__isnull=False,
            mrp__gt=0  # Avoid division by zero
        ).annotate(
            margin=models.ExpressionWrapper(
                (models.F('mrp') - models.F('price')) * 100 / models.F('mrp'),
                output_field=models.DecimalField()
            )
        ).order_by('-margin')[:12]

        serializer = ProductSerializer(products, many=True)
        return Response({
            'products': serializer.data
        })


class NewlyLaunchedView(APIView):
    """API view for newly launched products."""
    permission_classes = [permissions.AllowAny]

    @method_decorator(cache_page(60 * 30))  # Cache for 30 minutes
    def get(self, _request):
        """Get products launched within the last 30 days."""
        thirty_days_ago = timezone.now() - timedelta(days=30)

        products = Product.objects.filter(
            is_active=True,
            created_at__gte=thirty_days_ago
        ).order_by('-created_at')[:12]

        serializer = ProductSerializer(products, many=True)
        return Response({
            'products': serializer.data
        })


# ============================================
# PWA ANALYTICS ENDPOINTS
# ============================================

class PWAAnalyticsView(APIView):
    """API view for PWA analytics tracking."""
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        """
        Track PWA analytics events.
        Events include: pwa_init, prompt_shown, install_clicked, pwa_installed,
                       prompt_dismissed, prompt_snoozed, sw_registered, etc.
        """
        try:
            event = request.data.get('event', '')
            data = request.data.get('data', {})

            if not event:
                return Response(
                    {'error': 'Event name is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Valid PWA events
            valid_events = [
                'pwa_init', 'prompt_shown', 'install_clicked', 'pwa_installed',
                'prompt_dismissed', 'prompt_snoozed', 'prompt_closed',
                'sw_registered', 'sw_registration_failed', 'update_available',
                'install_prompt_available', 'install_prompt_result',
                'install_prompt_error', 'page_visit'
            ]

            if event not in valid_events:
                return Response(
                    {'error': f'Invalid event: {event}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Log analytics event
            try:
                AnalyticsEvent.objects.create(
                    event_type=f'pwa_{event}',
                    user=request.user if request.user.is_authenticated else None,
                    data=json.dumps({
                        'event': event,
                        'pwa_data': data,
                        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                        'ip_address': self._get_client_ip(request),
                        'referrer': request.META.get('HTTP_REFERER', '')
                    }),
                    created_at=timezone.now()
                )
            except (LookupError, ImportError):
                # AnalyticsEvent model might not exist
                logger.info("PWA Analytics: %s - %s", event, json.dumps(data))

            return Response({
                'success': True,
                'event': event,
                'timestamp': timezone.now().isoformat()
            })

        except json.JSONDecodeError:
            return Response(
                {'error': 'Invalid JSON data'},
                status=status.HTTP_400_BAD_REQUEST
            )

    def _get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip


class PWAStatusView(APIView):
    """API view for PWA status and statistics."""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        """
        Get PWA installation status and statistics.
        Returns aggregated analytics for admin users, basic status for others.
        """
        response_data = {
            'pwa_enabled': True,
            'service_worker_url': '/static/sw.js',
            'manifest_url': '/static/manifest.json',
            'features': {
                'offline_support': True,
                'push_notifications': True,
                'background_sync': True,
                'install_prompt': True
            }
        }

        # Add detailed analytics for admin users
        if request.user.is_authenticated and request.user.is_staff:
            try:
                # Get PWA analytics for the last 30 days
                thirty_days_ago = timezone.now() - timedelta(days=30)

                stats = {
                    'total_installs': 0,
                    'prompts_shown': 0,
                    'install_rate': 0,
                    'snooze_rate': 0,
                    'dismiss_rate': 0,
                    'daily_stats': []
                }

                try:
                    # Fetch analytics data
                    events = AnalyticsEvent.objects.filter(
                        event_type__startswith='pwa_',
                        created_at__gte=thirty_days_ago
                    )

                    stats['total_installs'] = events.filter(
                        event_type='pwa_pwa_installed'
                    ).count()
                    stats['prompts_shown'] = events.filter(
                        event_type='pwa_prompt_shown'
                    ).count()

                    if stats['prompts_shown'] > 0:
                        stats['install_rate'] = round(
                            (stats['total_installs'] / stats['prompts_shown']) * 100, 2
                        )

                    snoozed = events.filter(event_type='pwa_prompt_snoozed').count()
                    dismissed = events.filter(event_type='pwa_prompt_dismissed').count()

                    if stats['prompts_shown'] > 0:
                        stats['snooze_rate'] = round(
                            (snoozed / stats['prompts_shown']) * 100, 2
                        )
                        stats['dismiss_rate'] = round(
                            (dismissed / stats['prompts_shown']) * 100, 2
                        )

                    # Daily breakdown
                    from django.db.models.functions import TruncDate
                    daily = events.filter(
                        event_type='pwa_pwa_installed'
                    ).annotate(
                        date=TruncDate('created_at')
                    ).values('date').annotate(
                        count=Count('id')
                    ).order_by('-date')[:7]

                    stats['daily_stats'] = [
                        {'date': str(d['date']), 'installs': d['count']}
                        for d in daily
                    ]

                except (LookupError, ImportError):
                    stats['note'] = 'Analytics model not available'

                response_data['admin_stats'] = stats

            except Exception as exc:  # pylint: disable=broad-exception-caught
                logger.warning("Error fetching PWA stats: %s", exc)
                response_data['admin_stats'] = {'error': 'Unable to fetch statistics'}

        return Response(response_data)


# ============================================
# USER ANALYTICS API VIEWS
# ============================================

class UserSessionListView(generics.ListAPIView):
    """API view for listing user sessions."""
    serializer_class = UserSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return sessions for the current user."""
        return UserSession.objects.filter(user=self.request.user).order_by('-started_at')[:50]


class UserSessionDetailView(generics.RetrieveAPIView):
    """API view for retrieving a user session."""
    serializer_class = UserSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'session_id'

    def get_queryset(self):
        """Return sessions for the current user."""
        return UserSession.objects.filter(user=self.request.user)


class UserInteractionCreateView(generics.CreateAPIView):
    """API view for creating user interactions (tracking)."""
    serializer_class = UserInteractionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """Associate interaction with current user."""
        # Get or create session
        session_id = self.request.data.get('session_id')
        session = None
        if session_id:
            session = UserSession.objects.filter(
                user=self.request.user,
                session_id=session_id,
                is_active=True
            ).first()

        serializer.save(user=self.request.user, session=session)


class UserBehaviorPatternListView(generics.ListAPIView):
    """API view for listing user behavior patterns."""
    serializer_class = UserBehaviorPatternSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return patterns for the current user."""
        return UserBehaviorPattern.objects.filter(
            user=self.request.user,
            is_active=True
        ).order_by('-confidence_score')[:20]


class UserPreferenceListView(generics.ListCreateAPIView):
    """API view for listing and creating user preferences."""
    serializer_class = UserPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return preferences for the current user."""
        return UserPreference.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Associate preference with current user."""
        serializer.save(user=self.request.user)


class UserFeedbackCreateView(generics.CreateAPIView):
    """API view for creating user feedback."""
    serializer_class = UserFeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """Associate feedback with current user."""
        serializer.save(user=self.request.user)


class UserAnalyticsSummaryView(APIView):
    """API view for user analytics summary."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get analytics summary for the current user."""
        user = request.user
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)

        # Get session stats
        sessions = UserSession.objects.filter(
            user=user,
            started_at__gte=thirty_days_ago
        )

        # Get interaction stats
        interactions = UserInteraction.objects.filter(
            user=user,
            timestamp__gte=thirty_days_ago
        )

        # Calculate metrics
        total_sessions = sessions.count()
        total_interactions = interactions.count()
        total_page_views = interactions.filter(
            interaction_type='page_view'
        ).count()

        # Average session duration
        avg_duration = 0
        if total_sessions > 0:
            durations = [
                (s.ended_at - s.started_at).total_seconds()
                for s in sessions if s.ended_at
            ]
            if durations:
                avg_duration = sum(durations) / len(durations)

        # Conversion rate
        conversions = interactions.filter(is_conversion=True).count()
        conversion_rate = (conversions / total_interactions * 100) if total_interactions > 0 else 0

        # Get top interactions
        top_interactions = list(interactions.values('interaction_type').annotate(
            count=Count('id')
        ).order_by('-count')[:5])

        # Get behavior patterns
        patterns = list(UserBehaviorPattern.objects.filter(
            user=user,
            is_active=True
        ).values('pattern_type', 'confidence_score')[:5])

        # Get preferred categories from orders
        preferred_categories = list(
            OrderItem.objects.filter(
                order__user=user,
                order__paid=True
            ).values('product__category__name').annotate(
                count=Count('id')
            ).order_by('-count')[:5]
        )

        # Calculate engagement and loyalty scores
        engagement_score = min(100, (total_interactions / 10) * 10) if total_interactions else 0
        orders_count = Order.objects.filter(user=user, paid=True).count()
        loyalty_score = min(100, orders_count * 10)

        # Predicted churn risk (simple heuristic)
        days_since_last_session = 30
        if sessions.exists():
            last_session = sessions.first()
            days_since_last_session = (now - last_session.started_at).days
        churn_risk = min(100, days_since_last_session * 3.33)

        # Lifetime value
        lifetime_value = Order.objects.filter(
            user=user,
            paid=True
        ).aggregate(total=Sum('paid_amount'))['total'] or 0

        summary_data = {
            'total_sessions': total_sessions,
            'total_interactions': total_interactions,
            'total_page_views': total_page_views,
            'average_session_duration': round(avg_duration, 2),
            'conversion_rate': round(conversion_rate, 2),
            'top_interactions': top_interactions,
            'behavior_patterns': patterns,
            'preferred_categories': preferred_categories,
            'purchase_history': [],
            'engagement_score': round(engagement_score, 2),
            'loyalty_score': round(loyalty_score, 2),
            'predicted_churn_risk': round(churn_risk, 2),
            'lifetime_value': float(lifetime_value)
        }

        serializer = UserAnalyticsSummarySerializer(summary_data)
        return Response(serializer.data)


class RealTimeAnalyticsView(APIView):
    """API view for real-time analytics (admin only)."""
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        """Get real-time analytics data."""
        now = timezone.now()
        one_hour_ago = now - timedelta(hours=1)

        # Active users (sessions in last 15 minutes)
        active_sessions = UserSession.objects.filter(
            is_active=True,
            last_activity__gte=now - timedelta(minutes=15)
        )

        # Page views last hour
        recent_interactions = UserInteraction.objects.filter(
            timestamp__gte=one_hour_ago
        )

        # Top pages
        top_pages = list(recent_interactions.filter(
            interaction_type='page_view'
        ).values('page_url').annotate(
            count=Count('id')
        ).order_by('-count')[:10])

        # Device breakdown
        devices = dict(active_sessions.values('device_type').annotate(
            count=Count('id')
        ).values_list('device_type', 'count'))

        # Traffic sources
        sources = dict(active_sessions.values('referrer').annotate(
            count=Count('id')
        ).values_list('referrer', 'count')[:5])

        data = {
            'active_users': active_sessions.values('user').distinct().count(),
            'current_sessions': active_sessions.count(),
            'page_views_last_hour': recent_interactions.filter(
                interaction_type='page_view'
            ).count(),
            'conversions_last_hour': recent_interactions.filter(
                is_conversion=True
            ).count(),
            'top_pages': top_pages,
            'active_devices': devices,
            'traffic_sources': sources,
            'recent_events': []
        }

        serializer = RealTimeAnalyticsSerializer(data)
        return Response(serializer.data)


class AnalyticsDashboardView(APIView):
    """API view for analytics dashboard (admin only)."""
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        """Get complete analytics dashboard data."""
        # Get summary for overall platform
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)

        # Platform-wide stats
        total_users = User.objects.filter(is_active=True).count()
        total_orders = Order.objects.filter(paid=True).count()
        total_revenue = Order.objects.filter(
            paid=True
        ).aggregate(total=Sum('paid_amount'))['total'] or 0

        # Recent activity
        recent_orders = Order.objects.filter(
            created_at__gte=thirty_days_ago
        ).count()

        # Charts data
        daily_revenue = list(Order.objects.filter(
            paid=True,
            created_at__gte=thirty_days_ago
        ).extra(
            select={'date': 'DATE(created_at)'}
        ).values('date').annotate(
            revenue=Sum('paid_amount')
        ).order_by('date')[:30])

        dashboard_data = {
            'summary': {
                'total_sessions': UserSession.objects.count(),
                'total_interactions': UserInteraction.objects.count(),
                'total_page_views': UserInteraction.objects.filter(
                    interaction_type='page_view'
                ).count(),
                'average_session_duration': 0,
                'conversion_rate': 0,
                'top_interactions': [],
                'behavior_patterns': [],
                'preferred_categories': [],
                'purchase_history': [],
                'engagement_score': 0,
                'loyalty_score': 0,
                'predicted_churn_risk': 0,
                'lifetime_value': float(total_revenue)
            },
            'real_time': {
                'active_users': UserSession.objects.filter(
                    is_active=True
                ).values('user').distinct().count(),
                'current_sessions': UserSession.objects.filter(is_active=True).count(),
                'page_views_last_hour': 0,
                'conversions_last_hour': 0,
                'top_pages': [],
                'active_devices': {},
                'traffic_sources': {},
                'recent_events': []
            },
            'charts': {
                'daily_revenue': daily_revenue,
                'total_users': total_users,
                'total_orders': total_orders,
                'recent_orders': recent_orders
            },
            'recent_activities': [],
            'alerts': [],
            'recommendations': []
        }

        serializer = AnalyticsDashboardSerializer(dashboard_data)
        return Response(serializer.data)


class SystemMonitoringView(APIView):
    """API view for comprehensive system monitoring."""
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        """Get comprehensive system monitoring data."""
        try:
            import psutil
            # from django.conf import settings  # Unused import removed


            monitoring_data = {
                'timestamp': timezone.now().isoformat(),
                'system': {
                    'cpu_percent': psutil.cpu_percent(interval=1),
                    'memory_percent': psutil.virtual_memory().percent,
                    'disk_usage': psutil.disk_usage('/').percent,
                    'boot_time': psutil.boot_time()
                },
                'database': self._get_database_metrics(),
                'cache': self._get_cache_metrics(),
                'django': self._get_django_metrics(),
                'performance': self._get_performance_metrics(),
                'errors': self._get_error_metrics()
            }

            return Response(monitoring_data)
        except ImportError:
            return Response({
                'error': 'psutil not installed. Install with: pip install psutil'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error("Error in system monitoring: %s", e)
            return Response({
                'error': 'Failed to get system monitoring data'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _get_database_metrics(self):
        """Get database performance metrics."""
        try:
            with connection.cursor() as cursor:
                # Active connections
                cursor.execute("""
                    SELECT COUNT(*) FROM pg_stat_activity
                    WHERE datname = current_database()
                """)
                active_connections = cursor.fetchone()[0]

                # Database size
                cursor.execute("""
                    SELECT pg_size_pretty(pg_database_size(current_database()))
                """)
                db_size = cursor.fetchone()[0]

                return {
                    'active_connections': active_connections,
                    'database_size': db_size,
                    'status': 'healthy'
                }
        except Exception as e:
            logger.error("Database metrics error: %s", e)
            return {
                'status': 'error',
                'error': str(e)
            }

    def _get_cache_metrics(self):
        """Get cache performance metrics."""
        try:
            from django.core.cache import cache

            # Try to get cache statistics
            cache_stats = {}
            try:
                if hasattr(cache._cache, 'get_stats'):
                    stats = cache._cache.get_stats()
                    cache_stats['available'] = True
                    cache_stats['backends'] = len(stats)
                else:
                    cache_stats['available'] = False
                    cache_stats['message'] = 'Cache stats not available for this backend'
            except Exception as e:
                cache_stats['error'] = str(e)

            return cache_stats
        except Exception as e:
            logger.error("Cache metrics error: %s", e)
            return {'error': str(e)}

    def _get_django_metrics(self):
        """Get Django application metrics."""
        try:
            return {
                'debug': settings.DEBUG,
                'installed_apps': len(settings.INSTALLED_APPS),
                'middlewares': len(settings.MIDDLEWARE),
                'time_zone': settings.TIME_ZONE,
                'language_code': settings.LANGUAGE_CODE
            }
        except Exception as e:
            logger.error("Django metrics error: %s", e)
            return {'error': str(e)}

    def _get_performance_metrics(self):
        """Get application performance metrics."""
        try:
            # Calculate average response time from recent interactions
            recent_interactions = UserInteraction.objects.filter(
                timestamp__gte=timezone.now() - timedelta(minutes=5),
                interaction_type='page_view'
            )

            avg_response_time = 0
            if recent_interactions.exists():
                response_times = [
                    interaction.duration_seconds or 0
                    for interaction in recent_interactions
                    if interaction.duration_seconds
                ]
                avg_response_time = sum(response_times) / len(response_times) if response_times else 0

            return {
                'average_response_time': round(avg_response_time, 2),
                'requests_per_minute': recent_interactions.count(),
                'active_sessions': UserSession.objects.filter(is_active=True).count()
            }
        except Exception as e:
            logger.error("Performance metrics error: %s", e)
            return {'error': str(e)}

    def _get_error_metrics(self):
        """Get error tracking metrics."""
        try:
            # Count recent errors
            recent_errors = UserActivityLog.objects.filter(
                timestamp__gte=timezone.now() - timedelta(hours=1),
                activity_type='error'
            ).count()

            # Get error types distribution
            error_types = UserActivityLog.objects.filter(
                timestamp__gte=timezone.now() - timedelta(hours=1),
                activity_type='error'
            ).values('activity_data').annotate(
                count=Count('id')
            ).order_by('-count')[:5]

            return {
                'errors_last_hour': recent_errors,
                'top_error_types': list(error_types),
                'error_rate': 'low' if recent_errors < 10 else 'medium' if recent_errors < 50 else 'high'
            }
        except Exception as e:
            logger.error("Error metrics error: %s", e)
            return {'error': str(e)}


class ErrorTrackingView(APIView):
    """API view for error tracking and reporting."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Report an error or exception."""
        try:
            error_data = {
                'error_type': request.data.get('error_type', 'javascript_error'),
                'message': request.data.get('message', ''),
                'stack_trace': request.data.get('stack_trace', ''),
                'url': request.data.get('url', ''),
                'line_number': request.data.get('line_number'),
                'column_number': request.data.get('column_number'),
                'user_agent': request.data.get('user_agent', ''),
                'timestamp': timezone.now(),
                'user': request.user if request.user.is_authenticated else None,
                'session': request.session.session_key
            }

            # Store error in activity log
            UserActivityLog.objects.create(
                user=request.user if request.user.is_authenticated else None,
                activity_type='error',
                activity_data=error_data,
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                is_sensitive=True
            )

            # Log to application logger
            logger.error(
                "Client error reported: %s - %s",
                error_data['error_type'],
                error_data['message'],
                extra={'user_id': request.user.id if request.user.is_authenticated else None}
            )

            return Response({
                'success': True,
                'message': 'Error reported successfully'
            })

        except Exception as e:
            logger.error("Error reporting failed: %s", e)
            return Response({
                'success': False,
                'error': 'Failed to report error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        """Get recent errors (admin only)."""
        if not request.user.is_staff:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        try:
            errors = UserActivityLog.objects.filter(
                activity_type='error'
            ).order_by('-timestamp')[:50]

            error_list = []
            for error in errors:
                error_list.append({
                    'id': error.id,
                    'timestamp': error.timestamp.isoformat(),
                    'error_type': error.activity_data.get('error_type', 'unknown'),
                    'message': error.activity_data.get('message', ''),
                    'url': error.activity_data.get('url', ''),
                    'user': error.user.username if error.user else 'Anonymous',
                    'ip_address': error.ip_address
                })

            return Response({
                'errors': error_list,
                'total': len(error_list)
            })

        except Exception as e:
            logger.error("Error retrieving errors: %s", e)
            return Response({
                'error': 'Failed to retrieve errors'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip


class UserSegmentationView(APIView):
    """API view for user profiling and segmentation."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get user segmentation data."""
        try:
            # Get current user's segments
            user_segments = UserSegmentMembership.objects.filter(
                user=request.user
            ).select_related('segment')

            segments = []
            for membership in user_segments:
                segments.append({
                    'segment_id': membership.segment.id,
                    'segment_name': membership.segment.name,
                    'description': membership.segment.description,
                    'membership_score': float(membership.membership_score),
                    'joined_at': membership.joined_at.isoformat()
                })

            # Get user's behavior patterns
            behavior_patterns = UserBehaviorPattern.objects.filter(
                user=request.user,
                is_active=True
            )

            patterns = []
            for pattern in behavior_patterns:
                patterns.append({
                    'pattern_type': pattern.pattern_type,
                    'confidence_score': float(pattern.confidence_score),
                    'frequency': pattern.frequency,
                    'last_observed': pattern.last_observed.isoformat(),
                    'pattern_data': pattern.pattern_data
                })

            # Get user preferences
            preferences = UserPreference.objects.filter(
                user=request.user
            )

            user_preferences = []
            for pref in preferences:
                user_preferences.append({
                    'preference_type': pref.preference_type,
                    'preference_key': pref.preference_key,
                    'preference_value': pref.preference_value,
                    'data_type': pref.data_type,
                    'confidence_score': float(pref.confidence_score),
                    'source': pref.source
                })

            return Response({
                'user_segments': segments,
                'behavior_patterns': patterns,
                'preferences': user_preferences,
                'segment_count': len(segments),
                'pattern_count': len(patterns),
                'preference_count': len(user_preferences)
            })

        except Exception as e:
            logger.error("Error getting user segmentation data: %s", e)
            return Response({
                'error': 'Failed to get segmentation data'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        """Update user preferences or behavior."""
        try:
            action = request.data.get('action', '')

            if action == 'update_preference':
                return self._update_preference(request)
            elif action == 'add_feedback':
                return self._add_feedback(request)
            elif action == 'track_behavior':
                return self._track_behavior(request)
            else:
                return Response({
                    'error': 'Invalid action'
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error("Error in user segmentation: %s", e)
            return Response({
                'error': 'Failed to process request'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _update_preference(self, request):
        """Update a user preference."""
        preference_type = request.data.get('preference_type')
        preference_key = request.data.get('preference_key')
        preference_value = request.data.get('preference_value')
        data_type = request.data.get('data_type', 'string')

        if not all([preference_type, preference_key, preference_value]):
            return Response({
                'error': 'Missing required fields'
            }, status=status.HTTP_400_BAD_REQUEST)

        UserPreference.objects.update_or_create(
            user=request.user,
            preference_type=preference_type,
            preference_key=preference_key,
            defaults={
                'preference_value': str(preference_value),
                'data_type': data_type,
                'source': 'explicit',
                'confidence_score': 100.0
            }
        )

        return Response({
            'success': True,
            'message': 'Preference updated successfully'
        })

    def _add_feedback(self, request):
        """Add user feedback."""
        feedback_type = request.data.get('feedback_type', 'general')
        content = request.data.get('content', '')
        rating = request.data.get('rating')

        if not content:
            return Response({
                'error': 'Feedback content is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        UserFeedback.objects.create(
            user=request.user,
            feedback_type=feedback_type,
            content=content,
            rating=rating
        )

        return Response({
            'success': True,
            'message': 'Feedback submitted successfully'
        })

    def _track_behavior(self, request):
        """Track user behavior for segmentation."""
        behavior_type = request.data.get('behavior_type')
        behavior_data = request.data.get('behavior_data', {})

        if not behavior_type:
            return Response({
                'error': 'Behavior type is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create interaction record
        UserInteraction.objects.create(
            user=request.user,
            interaction_type=behavior_type,
            metadata=behavior_data,
            timestamp=timezone.now()
        )

        return Response({
            'success': True,
            'message': 'Behavior tracked successfully'
        })


class SegmentManagementView(APIView):
    """API view for managing user segments (admin only)."""
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        """Get all user segments."""
        try:
            segments = UserSegment.objects.filter(is_active=True)

            segment_list = []
            for segment in segments:
                segment_list.append({
                    'id': segment.id,
                    'name': segment.name,
                    'description': segment.description,
                    'criteria': segment.criteria,
                    'user_count': segment.user_count,
                    'created_at': segment.created_at.isoformat(),
                    'updated_at': segment.updated_at.isoformat()
                })

            return Response({
                'segments': segment_list,
                'total': len(segment_list)
            })

        except Exception as e:
            logger.error("Error getting segments: %s", e)
            return Response({
                'error': 'Failed to get segments'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        """Create a new user segment."""
        try:
            name = request.data.get('name')
            description = request.data.get('description', '')
            criteria = request.data.get('criteria', {})

            if not name:
                return Response({
                    'error': 'Segment name is required'
                }, status=status.HTTP_400_BAD_REQUEST
            )

            segment = UserSegment.objects.create(
                name=name,
                description=description,
                criteria=criteria
            )

            return Response({
                'success': True,
                'segment_id': segment.id,
                'message': 'Segment created successfully'
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error("Error creating segment: %s", e)
            return Response({
                'error': 'Failed to create segment'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# TRACKING SYSTEM API VIEWS
# Import tracking API views to expose them for URL routing
# ============================================================================
from .tracking_api import (  # noqa: E402 pylint: disable=wrong-import-position
    TrackingDashboardAPIView,
    TrackingAnalyticsAPIView,
    TrackingAlertsAPIView,
    tracking_realtime_stats,
)

__all__ = [
    'TrackingDashboardAPIView',
    'TrackingAnalyticsAPIView',
    'TrackingAlertsAPIView',
    'tracking_realtime_stats',
]

