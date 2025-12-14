"""
Enhanced Admin configuration for the store app.

This module provides advanced admin features including:
- Custom admin views
- Export functionality
- Bulk actions
- Advanced filtering
"""
# pylint: disable=no-member
import csv

from django.contrib import admin
from django.db.models import Avg
from django.http import HttpResponse
from django.utils import timezone
from django.utils.html import format_html

from .models import (
    Category, Vendor, Product, ProductImage, Order, OrderItem,
    Contact, Review, Wishlist, Profile, Coupon, FlashSale, BulkOrder,
    InventoryLog, VendorVerification, BuyerInquiry, RFQ, RFQQuote,
    PremiumListing, Message, Notification, AuditLog, SiteSettings,
    TradeEvent, EventRegistration, Deal
)

# Constants for admin display
DATE_RANGE_FORMAT = '{} → {}'


# Export Mixins
class ExportCsvMixin:
    """Mixin to add CSV export capability to ModelAdmin."""

    def export_as_csv(self, _request, queryset):
        """Export selected items to CSV file."""
        meta = self.model._meta  # pylint: disable=protected-access
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta.verbose_name_plural}.csv'
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = []
            for field in field_names:
                value = getattr(obj, field)
                if callable(value):
                    value = value()
                row.append(str(value) if value else '')
            writer.writerow(row)

        return response

    export_as_csv.short_description = "Export selected to CSV"


class ProductImageInline(admin.TabularInline):
    """Inline admin for product images."""
    model = ProductImage
    extra = 3
    fields = ['image', 'alt_text', 'is_primary', 'order']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Enhanced Category Admin."""
    list_display = ['name', 'slug', 'product_count']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    ordering = ['name']

    def product_count(self, obj):
        """Return the number of products in this category."""
        return obj.products.count()
    product_count.short_description = 'Products'


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin, ExportCsvMixin):
    """Enhanced Vendor Admin with export and stats."""
    list_display = ['name', 'city', 'created_by', 'product_count', 'average_rating']
    search_fields = ['name', 'city']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['city']
    actions = ['export_as_csv']

    def product_count(self, obj):
        """Return the count of active products for this vendor."""
        count = obj.products.filter(is_active=True).count()
        return format_html('<span style="font-weight: bold;">{}</span>', count)
    product_count.short_description = 'Products'

    def average_rating(self, obj):
        """Calculate and display the vendor's average product rating."""
        avg = Review.objects.filter(product__vendor=obj).aggregate(
            avg_rating=Avg('rating')
        )['avg_rating']
        if avg:
            return format_html('⭐ {:.1f}', avg)
        return '-'
    average_rating.short_description = 'Rating'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin, ExportCsvMixin):
    """Enhanced Product Admin with advanced features."""
    list_display = [
        'name', 'price_display', 'stock_status', 'is_active',
        'vendor', 'category', 'created_at'
    ]
    list_filter = ['vendor', 'category', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'brand', 'technical_name']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']
    inlines = [ProductImageInline]
    actions = ['export_as_csv', 'mark_active', 'mark_inactive']
    date_hierarchy = 'created_at'
    list_per_page = 25
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'slug', 'category', 'vendor', 'short_description', 'description')
        }),
        ('Pricing', {
            'fields': ('price', 'mrp')
        }),
        ('Inventory', {
            'fields': ('stock_quantity', 'low_stock_threshold', 'is_active')
        }),
        ('Images', {
            'fields': ('image',)
        }),
        ('Agricultural Details', {
            'fields': (
                'brand', 'technical_name', 'target_crops',
                'usage_instructions', 'safety_guidelines'
            ),
            'classes': ('collapse',)
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
    )

    def price_display(self, obj):
        """Display product price with discount badge if applicable."""
        if obj.mrp and obj.mrp > obj.price:
            discount = int((1 - obj.price / obj.mrp) * 100)
            return format_html(
                '<span style="color: #22c55e; font-weight: bold;">₹{}</span> '
                '<span style="text-decoration: line-through; color: #9ca3af;">₹{}</span> '
                '<span style="background-color: #ef4444; color: white; padding: 1px 6px; '
                'border-radius: 4px; font-size: 10px;">-{}%</span>',
                obj.price, obj.mrp, discount
            )
        return format_html('<span style="font-weight: bold;">₹{}</span>', obj.price)
    price_display.short_description = 'Price'
    price_display.admin_order_field = 'price'

    def stock_status(self, obj):
        """Display stock status with color-coded badge."""
        if obj.stock_quantity <= 0:
            return format_html(
                '<span style="background-color: #ef4444; color: white; '
                'padding: 2px 8px; border-radius: 12px;">Out of Stock</span>'
            )
        if obj.stock_quantity <= obj.low_stock_threshold:
            return format_html(
                '<span style="background-color: #f59e0b; color: white; '
                'padding: 2px 8px; border-radius: 12px;">Low: {}</span>',
                obj.stock_quantity
            )
        return format_html(
            '<span style="background-color: #22c55e; color: white; '
            'padding: 2px 8px; border-radius: 12px;">{}</span>',
            obj.stock_quantity
        )
    stock_status.short_description = 'Stock'
    stock_status.admin_order_field = 'stock_quantity'

    @admin.action(description='Mark selected products as active')
    def mark_active(self, _request, queryset):
        """Set selected products as active."""
        queryset.update(is_active=True)

    @admin.action(description='Mark selected products as inactive')
    def mark_inactive(self, _request, queryset):
        """Set selected products as inactive."""
        queryset.update(is_active=False)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Product Image Admin."""
    list_display = ['product', 'is_primary', 'order']
    list_filter = ['is_primary']
    search_fields = ['product__name', 'alt_text']


class OrderItemInline(admin.TabularInline):
    """Inline admin for order items."""
    model = OrderItem
    raw_id_fields = ['product']
    readonly_fields = ['price', 'quantity', 'vendor']
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin, ExportCsvMixin):
    """Enhanced Order Admin with detailed views."""
    list_display = [
        'order_id', 'customer_info', 'order_total', 'status_badge',
        'payment_badge', 'items_count', 'created_at'
    ]
    list_filter = ['status', 'paid', 'payment_method', 'created_at']
    search_fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'address']
    inlines = [OrderItemInline]
    readonly_fields = ['created_at', 'paid_amount']
    actions = ['export_as_csv', 'mark_as_paid', 'mark_as_shipped', 'mark_as_delivered']
    date_hierarchy = 'created_at'
    list_per_page = 25
    fieldsets = (
        ('Customer Info', {
            'fields': ('user', 'first_name', 'last_name', 'email', 'phone')
        }),
        ('Shipping', {
            'fields': ('address', 'place', 'zipcode')
        }),
        ('Payment', {
            'fields': ('paid', 'paid_amount', 'payment_method', 'payment_intent')
        }),
        ('Status', {
            'fields': ('status', 'created_at')
        }),
    )

    def order_id(self, obj):
        """Display formatted order ID."""
        return format_html('<strong>#{}</strong>', obj.id)
    order_id.short_description = 'Order ID'
    order_id.admin_order_field = 'id'

    def customer_info(self, obj):
        """Display customer name and email."""
        return format_html(
            '<strong>{} {}</strong><br/>'
            '<span style="color: #6b7280; font-size: 11px;">{}</span>',
            obj.first_name, obj.last_name, obj.email
        )
    customer_info.short_description = 'Customer'

    def order_total(self, obj):
        """Display formatted order total amount."""
        return format_html(
            '<span style="font-weight: bold; color: #22c55e;">₹{:,.2f}</span>',
            obj.paid_amount or 0
        )
    order_total.short_description = 'Total'
    order_total.admin_order_field = 'paid_amount'

    def status_badge(self, obj):
        """Display color-coded status badge."""
        colors = {
            'pending': '#f59e0b',
            'confirmed': '#3b82f6',
            'shipped': '#8b5cf6',
            'delivered': '#22c55e',
            'cancelled': '#ef4444',
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 2px 8px; border-radius: 12px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def payment_badge(self, obj):
        """Display payment status badge."""
        if obj.paid:
            return format_html(
                '<span style="background-color: #22c55e; color: white; '
                'padding: 2px 8px; border-radius: 12px; font-size: 11px;">✓ Paid</span>'
            )
        return format_html(
            '<span style="background-color: #ef4444; color: white; '
            'padding: 2px 8px; border-radius: 12px; font-size: 11px;">Unpaid</span>'
        )
    payment_badge.short_description = 'Payment'

    def items_count(self, obj):
        """Return the number of items in the order."""
        return obj.items.count()
    items_count.short_description = 'Items'

    @admin.action(description='Mark selected orders as paid')
    def mark_as_paid(self, _request, queryset):
        """Mark selected orders as paid."""
        queryset.update(paid=True)

    @admin.action(description='Mark selected orders as shipped')
    def mark_as_shipped(self, _request, queryset):
        """Mark selected orders as shipped."""
        queryset.update(status='shipped')

    @admin.action(description='Mark selected orders as delivered')
    def mark_as_delivered(self, _request, queryset):
        """Mark selected orders as delivered."""
        queryset.update(status='delivered')


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """Contact Admin."""
    list_display = ['name', 'email', 'created_at']
    search_fields = ['name', 'email', 'message']
    readonly_fields = ['name', 'email', 'message', 'created_at']
    list_filter = ['created_at']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Enhanced Review Admin."""
    list_display = [
        'product', 'user', 'rating_stars', 'title',
        'is_verified_purchase', 'created_at'
    ]
    list_filter = ['rating', 'is_verified_purchase', 'created_at']
    search_fields = ['product__name', 'user__username', 'title', 'comment']
    readonly_fields = ['product', 'user', 'created_at', 'updated_at']

    def rating_stars(self, obj):
        """Display star rating with Unicode characters."""
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="color: #f59e0b;">{}</span>', stars)
    rating_stars.short_description = 'Rating'


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    """Wishlist Admin."""
    list_display = ['user', 'product', 'added_at']
    list_filter = ['added_at']
    search_fields = ['user__username', 'product__name']


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin, ExportCsvMixin):
    """Enhanced Profile Admin."""
    list_display = [
        'user', 'shop_name', 'city', 'kyc_status',
        'credit_status', 'total_orders'
    ]
    list_filter = ['is_kyc_verified', 'city', 'state']
    search_fields = ['user__username', 'shop_name', 'gst_number']
    actions = ['export_as_csv', 'verify_kyc']

    def kyc_status(self, obj):
        """Display KYC verification status badge."""
        if obj.is_kyc_verified:
            return format_html(
                '<span style="background-color: #22c55e; color: white; '
                'padding: 2px 8px; border-radius: 12px;">✓ Verified</span>'
            )
        return format_html(
            '<span style="background-color: #f59e0b; color: white; '
            'padding: 2px 8px; border-radius: 12px;">Pending</span>'
        )
    kyc_status.short_description = 'KYC Status'

    def credit_status(self, obj):
        """Display credit usage status."""
        if obj.credit_limit > 0:
            used_percent = (obj.credit_used / obj.credit_limit) * 100 if obj.credit_limit else 0
            return format_html(
                '₹{:,.0f} / ₹{:,.0f} ({:.0f}%)',
                obj.credit_used, obj.credit_limit, used_percent
            )
        return 'No credit limit'
    credit_status.short_description = 'Credit'

    def total_orders(self, obj):
        """Return total orders for this user."""
        return Order.objects.filter(user=obj.user).count()
    total_orders.short_description = 'Orders'

    @admin.action(description='Verify KYC for selected profiles')
    def verify_kyc(self, _request, queryset):
        """Verify KYC for selected user profiles."""
        queryset.update(is_kyc_verified=True)


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    """Enhanced Coupon Admin."""
    list_display = [
        'code', 'discount_display', 'usage_display',
        'is_active', 'valid_period'
    ]
    list_filter = ['is_active', 'discount_type', 'valid_from', 'valid_until']
    search_fields = ['code']
    list_editable = ['is_active']
    actions = ['activate_coupons', 'deactivate_coupons']

    def discount_display(self, obj):
        """Display formatted discount value."""
        if obj.discount_type == 'percent':
            return f'{obj.discount_value}%'
        return f'₹{obj.discount_value}'
    discount_display.short_description = 'Discount'

    def usage_display(self, obj):
        """Display coupon usage count."""
        return format_html('{} / {}', obj.used_count, obj.max_uses)
    usage_display.short_description = 'Used/Max'

    def valid_period(self, obj):
        """Display coupon validity period."""
        return format_html(
            DATE_RANGE_FORMAT,
            obj.valid_from.strftime('%Y-%m-%d'),
            obj.valid_until.strftime('%Y-%m-%d')
        )
    valid_period.short_description = 'Valid Period'

    @admin.action(description='Activate selected coupons')
    def activate_coupons(self, _request, queryset):
        """Activate selected coupons."""
        queryset.update(is_active=True)

    @admin.action(description='Deactivate selected coupons')
    def deactivate_coupons(self, _request, queryset):
        """Deactivate selected coupons."""
        queryset.update(is_active=False)


@admin.register(FlashSale)
class FlashSaleAdmin(admin.ModelAdmin):
    """Enhanced Flash Sale Admin."""
    list_display = [
        'name', 'discount_percentage', 'time_display',
        'is_active', 'live_status', 'products_count'
    ]
    list_filter = ['is_active', 'start_time', 'end_time']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['products']
    list_editable = ['is_active']

    def time_display(self, obj):
        """Display flash sale duration period."""
        return format_html(
            DATE_RANGE_FORMAT,
            obj.start_time.strftime('%Y-%m-%d %H:%M'),
            obj.end_time.strftime('%Y-%m-%d %H:%M')
        )
    time_display.short_description = 'Duration'

    def live_status(self, obj):
        """Display flash sale live/upcoming/ended status."""
        if obj.is_live:
            return format_html(
                '<span style="background-color: #22c55e; color: white; '
                'padding: 2px 8px; border-radius: 12px;">🔴 LIVE</span>'
            )
        now = timezone.now()
        if now < obj.start_time:
            return format_html(
                '<span style="background-color: #3b82f6; color: white; '
                'padding: 2px 8px; border-radius: 12px;">⏰ Upcoming</span>'
            )
        return format_html(
            '<span style="background-color: #6b7280; color: white; '
            'padding: 2px 8px; border-radius: 12px;">Ended</span>'
        )
    live_status.short_description = 'Status'

    def products_count(self, obj):
        """Return count of products in flash sale."""
        return obj.products.count()
    products_count.short_description = 'Products'


@admin.register(BulkOrder)
class BulkOrderAdmin(admin.ModelAdmin, ExportCsvMixin):
    """Enhanced Bulk Order Admin."""
    list_display = [
        'id', 'user', 'product', 'quantity', 'price_info',
        'status', 'created_at'
    ]
    list_filter = ['status', 'created_at', 'vendor']
    search_fields = ['user__username', 'product__name', 'notes']
    list_editable = ['status']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['export_as_csv', 'approve_orders', 'reject_orders']

    def price_info(self, obj):
        """Display pricing information with approval status."""
        if obj.approved_price:
            return format_html(
                'Req: ₹{} → Approved: <strong style="color: #22c55e;">₹{}</strong>',
                obj.requested_price, obj.approved_price
            )
        return format_html('Req: ₹{}', obj.requested_price)
    price_info.short_description = 'Pricing'

    @admin.action(description='Approve selected bulk orders')
    def approve_orders(self, _request, queryset):
        """Approve selected bulk orders with requested price."""
        for order in queryset:
            order.status = 'approved'
            if not order.approved_price:
                order.approved_price = order.requested_price
            order.save()

    @admin.action(description='Reject selected bulk orders')
    def reject_orders(self, _request, queryset):
        """Reject selected bulk orders."""
        queryset.update(status='rejected')


@admin.register(InventoryLog)
class InventoryLogAdmin(admin.ModelAdmin, ExportCsvMixin):
    """Inventory Log Admin."""
    list_display = [
        'product', 'action', 'quantity', 'previous_stock',
        'new_stock', 'created_at'
    ]
    list_filter = ['action', 'created_at']
    search_fields = ['product__name', 'reference', 'notes']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    actions = ['export_as_csv']


@admin.register(VendorVerification)
class VendorVerificationAdmin(admin.ModelAdmin):
    """Enhanced Vendor Verification Admin."""
    list_display = [
        'vendor', 'status', 'is_premium_vendor', 'trust_score',
        'verified_by', 'verified_at', 'created_at'
    ]
    list_filter = ['status', 'is_premium_vendor', 'verified_at']
    search_fields = ['vendor__name', 'gst_number', 'pan_number']
    list_editable = ['status', 'is_premium_vendor', 'trust_score']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['approve_verification', 'reject_verification']

    @admin.action(description='Approve selected verifications')
    def approve_verification(self, request, queryset):
        """Approve vendor verification with current user and timestamp."""
        queryset.update(status='approved', verified_by=request.user, verified_at=timezone.now())

    @admin.action(description='Reject selected verifications')
    def reject_verification(self, _request, queryset):
        """Reject selected vendor verifications."""
        queryset.update(status='rejected')


@admin.register(BuyerInquiry)
class BuyerInquiryAdmin(admin.ModelAdmin):
    """Buyer Inquiry Admin."""
    list_display = [
        'id', 'buyer', 'vendor', 'subject', 'status',
        'is_urgent', 'quantity_required', 'created_at'
    ]
    list_filter = ['status', 'is_urgent', 'created_at', 'vendor']
    search_fields = ['buyer__username', 'vendor__name', 'subject', 'message']
    list_editable = ['status']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'


class RFQQuoteInline(admin.TabularInline):
    """RFQ Quote Inline."""
    model = RFQQuote
    extra = 0
    readonly_fields = ['vendor', 'price_per_unit', 'total_price', 'status', 'created_at']


@admin.register(RFQ)
class RFQAdmin(admin.ModelAdmin, ExportCsvMixin):
    """Enhanced RFQ Admin."""
    list_display = [
        'id', 'title', 'buyer', 'category', 'quantity',
        'status', 'is_public', 'quotes_count', 'created_at'
    ]
    list_filter = ['status', 'is_public', 'category', 'created_at']
    search_fields = ['title', 'description', 'buyer__username']
    list_editable = ['status']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [RFQQuoteInline]
    date_hierarchy = 'created_at'
    actions = ['export_as_csv']

    def quotes_count(self, obj):
        """Return the number of quotes for this RFQ."""
        return obj.quotes.count()
    quotes_count.short_description = 'Quotes'


@admin.register(RFQQuote)
class RFQQuoteAdmin(admin.ModelAdmin):
    """RFQ Quote Admin."""
    list_display = [
        'id', 'rfq', 'vendor', 'price_per_unit', 'total_price',
        'delivery_time', 'status', 'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['rfq__title', 'vendor__name']
    list_editable = ['status']
    readonly_fields = ['created_at']


@admin.register(PremiumListing)
class PremiumListingAdmin(admin.ModelAdmin):
    """Premium Listing Admin."""
    list_display = [
        'product', 'vendor', 'position', 'start_date', 'end_date',
        'is_active', 'amount_paid', 'impressions', 'clicks', 'ctr_display'
    ]
    list_filter = ['position', 'is_active', 'start_date', 'end_date']
    search_fields = ['product__name', 'vendor__name']
    list_editable = ['is_active']
    readonly_fields = ['impressions', 'clicks', 'created_at']

    def ctr_display(self, obj):
        """Display click-through rate percentage."""
        return f'{obj.ctr}%'
    ctr_display.short_description = 'CTR'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Message Admin."""
    list_display = [
        'id', 'sender', 'receiver', 'subject', 'is_read',
        'read_at', 'created_at'
    ]
    list_filter = ['is_read', 'created_at']
    search_fields = ['sender__username', 'receiver__username', 'subject', 'content']
    readonly_fields = ['created_at', 'read_at']
    date_hierarchy = 'created_at'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Enhanced Notification Admin."""
    list_display = [
        'id', 'user', 'notification_type', 'title',
        'is_read', 'is_email_sent', 'is_sms_sent', 'created_at'
    ]
    list_filter = ['notification_type', 'is_read', 'is_email_sent', 'is_sms_sent', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    list_editable = ['is_read']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    actions = ['mark_as_read', 'send_email_notifications']

    @admin.action(description='Mark selected notifications as read')
    def mark_as_read(self, _request, queryset):
        """Mark selected notifications as read with timestamp."""
        queryset.update(is_read=True, read_at=timezone.now())

    @admin.action(description='Send email for selected notifications')
    def send_email_notifications(self, request, queryset):
        """Queue emails for selected notifications."""
        queryset.update(is_email_sent=True)
        self.message_user(request, f"{queryset.count()} emails queued for sending.")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Audit Log Admin (read-only)."""
    list_display = [
        'id', 'user', 'action', 'model_name', 'object_repr',
        'ip_address', 'created_at'
    ]
    list_filter = ['action', 'model_name', 'created_at']
    search_fields = ['user__username', 'model_name', 'object_repr', 'ip_address']
    readonly_fields = [
        'user', 'action', 'model_name', 'object_id', 'object_repr',
        'changes', 'ip_address', 'user_agent', 'created_at'
    ]
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """Site Settings Admin (singleton)."""
    list_display = ['site_name', 'contact_email', 'maintenance_mode', 'updated_at']
    fieldsets = (
        ('General', {
            'fields': ('site_name', 'site_tagline', 'site_logo', 'favicon')
        }),
        ('Contact', {
            'fields': ('contact_email', 'contact_phone', 'address')
        }),
        ('Social Media', {
            'fields': (
                'facebook_url', 'twitter_url', 'instagram_url',
                'linkedin_url', 'youtube_url'
            ),
            'classes': ('collapse',)
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'google_analytics_id'),
            'classes': ('collapse',)
        }),
        ('Features', {
            'fields': (
                'enable_rfq', 'enable_premium_listings',
                'enable_messaging', 'enable_reviews'
            )
        }),
        ('Maintenance', {
            'fields': ('maintenance_mode', 'maintenance_message')
        }),
        ('Commission', {
            'fields': ('default_commission_rate',)
        }),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


class EventRegistrationInline(admin.TabularInline):
    """Event Registration Inline."""
    model = EventRegistration
    extra = 0
    readonly_fields = ['vendor', 'booth_number', 'payment_status', 'created_at']


@admin.register(TradeEvent)
class TradeEventAdmin(admin.ModelAdmin):
    """Trade Event Admin."""
    list_display = [
        'name', 'city', 'start_date', 'end_date', 'is_featured',
        'is_active', 'registrations_count', 'entry_fee'
    ]
    list_filter = ['is_featured', 'is_active', 'city', 'start_date']
    search_fields = ['name', 'description', 'venue', 'city', 'organizer']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_featured', 'is_active']
    inlines = [EventRegistrationInline]
    date_hierarchy = 'start_date'

    def registrations_count(self, obj):
        """Return the number of registrations for this event."""
        return obj.registrations.count()
    registrations_count.short_description = 'Registrations'


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    """Event Registration Admin."""
    list_display = [
        'id', 'event', 'vendor', 'booth_number',
        'payment_status', 'created_at'
    ]
    list_filter = ['payment_status', 'event', 'created_at']
    search_fields = ['event__name', 'vendor__name', 'booth_number']
    list_editable = ['payment_status', 'booth_number']
    readonly_fields = ['created_at']


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    """Deal Admin."""
    list_display = [
        'name', 'deal_type', 'discount_value', 'date_range',
        'is_active', 'products_count'
    ]
    list_filter = ['is_active', 'deal_type', 'start_date', 'end_date']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['products', 'categories', 'vendors']
    list_editable = ['is_active']

    def date_range(self, obj):
        """Display the deal validity date range."""
        return format_html(DATE_RANGE_FORMAT, obj.start_date.date(), obj.end_date.date())
    date_range.short_description = 'Duration'

    def products_count(self, obj):
        """Return the number of products in this deal."""
        return obj.products.count()
    products_count.short_description = 'Products'
