"""
Models for the store app.

Contains Vendor, Category, Product, Order, Contact, and enhanced shop models.
"""
# pylint: disable=no-member

import logging

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

logger = logging.getLogger(__name__)

# Constants
SITE_SETTINGS_NAME = 'Site Settings'

class Vendor(models.Model):
    """
    Vendor model representing a seller or manufacturer.
    """
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    logo = models.ImageField(upload_to='vendors/', blank=True, null=True)
    city = models.CharField(max_length=100)
    created_by = models.OneToOneField(
        User, related_name='vendor', on_delete=models.CASCADE, null=True, blank=True
    )
    is_active = models.BooleanField(default=True, help_text="Vendor is active and visible")
    is_verified = models.BooleanField(default=False, help_text="Vendor has been verified")
    description = models.TextField(blank=True, help_text="About the vendor")
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_products = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        """Meta definition for Vendor."""
        ordering = ['name']
        indexes = [
            models.Index(fields=['is_active', 'is_verified'], name='idx_vendor_active_verified'),
            models.Index(fields=['rating'], name='idx_vendor_rating'),
            models.Index(fields=['city'], name='idx_vendor_city'),
        ]

    def __str__(self):
        return str(self.name)


class Category(models.Model):
    """
    Category model for organizing products.
    """
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    class Meta:
        """Meta definition for Category."""
        verbose_name_plural = 'Categories'
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug'], name='idx_category_slug'),
        ]

    def __str__(self):
        return str(self.name)

class Product(models.Model):
    """
    Product model representing items for sale.
    """
    objects = models.Manager()
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, default='')
    short_description = models.CharField(max_length=255, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Wholesale Price")
    mrp = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="MRP"
    )
    image = models.ImageField(upload_to='products/', blank=True, null=True)

    # New Agri-specific fields
    brand = models.CharField(
        max_length=100, blank=True, help_text="e.g. UPL, Godrej Agrovet"
    )
    technical_name = models.CharField(
        max_length=255, blank=True, help_text="Chemical composition"
    )
    target_crops = models.CharField(
        max_length=255, blank=True, help_text="e.g. Wheat, Rice, Tomato"
    )
    usage_instructions = models.TextField(blank=True, help_text="Dosage and application guidelines")
    safety_guidelines = models.TextField(blank=True, help_text="Safety precautions")

    # Inventory Management
    stock_quantity = models.PositiveIntegerField(default=100, help_text="Available stock")
    low_stock_threshold = models.PositiveIntegerField(
        default=10, help_text="Alert when stock below this"
    )
    is_active = models.BooleanField(default=True, help_text="Product visibility")

    # SEO fields
    meta_title = models.CharField(max_length=70, blank=True, help_text="SEO title")
    meta_description = models.CharField(max_length=160, blank=True, help_text="SEO description")

    # AGRIM Features
    trending_score = models.IntegerField(default=0, help_text="Score for trending ranking")
    is_instant_pack = models.BooleanField(default=False, help_text="Ready for instant shipping")

    # Bulk Pricing
    bulk_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Discounted price for bulk orders"
    )
    bulk_min_quantity = models.PositiveIntegerField(
        default=0,
        help_text="Minimum quantity for bulk price"
    )


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta definition for Product."""
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'is_active'], name='idx_product_cat_active'),
            models.Index(fields=['vendor', 'is_active'], name='idx_product_vendor_active'),
            models.Index(fields=['price'], name='idx_product_price'),
            models.Index(fields=['created_at'], name='idx_product_created'),
            models.Index(fields=['is_active', 'stock_quantity'], name='idx_product_active_stock'),
            models.Index(fields=['slug'], name='idx_product_slug'),
        ]

    def __str__(self):
        return str(self.name)

    @property
    def is_in_stock(self):
        """Check if product is in stock."""
        return self.stock_quantity > 0

    @property
    def is_low_stock(self):
        """Check if product is running low on stock."""
        return self.stock_quantity <= self.low_stock_threshold

    @property
    def discount_percentage(self):
        """Calculate discount percentage if MRP is set."""
        if self.mrp and self.mrp > self.price:
            return int(((self.mrp - self.price) / self.mrp) * 100)
        return 0


class ProductImage(models.Model):
    """
    Model for storing multiple images per product.
    """
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        """Meta definition for ProductImage."""
        ordering = ['order', '-is_primary']

    def __str__(self):
        return f"Image for {self.product.name}"


class Coupon(models.Model):
    """
    Model for discount coupons.
    """
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=10, choices=[
        ('percent', 'Percentage'),
        ('fixed', 'Fixed Amount')
    ], default='percent')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_uses = models.PositiveIntegerField(default=100)
    used_count = models.PositiveIntegerField(default=0)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        """Meta options for Coupon model."""
        indexes = [
            models.Index(
                fields=['is_active', 'valid_from', 'valid_until'],
                name='idx_coupon_active_validity'
            ),
        ]

    def __str__(self):
        return str(self.code)

    @property
    def is_valid(self):
        """Check if coupon is currently valid."""
        now = timezone.now()
        return (
            self.is_active and
            self.used_count < self.max_uses and
            self.valid_from <= now <= self.valid_until
        )

class Wishlist(models.Model):
    """
    Model for storing user wishlists with price alert features.
    """
    user = models.ForeignKey(User, related_name='wishlist', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='wishlisted_by', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Price alert features
    price_when_added = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Product price when added to wishlist"
    )
    target_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Notify when price drops to this value"
    )
    notify_on_sale = models.BooleanField(
        default=False,
        help_text="Notify when product goes on sale"
    )
    notify_on_restock = models.BooleanField(
        default=False,
        help_text="Notify when product is back in stock"
    )
    last_notified_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time user was notified about this item"
    )

    class Meta:
        """Meta definition for Wishlist."""
        unique_together = ('user', 'product')
        ordering = ['-added_at']
        indexes = [
            models.Index(fields=['user', 'added_at'], name='idx_wishlist_user_date'),
            models.Index(fields=['notify_on_sale'], name='idx_wishlist_notify_sale'),
        ]

    def __str__(self):
        return f"{self.user.username}'s wishlist - {self.product.name}"

    @property
    def has_price_drop(self):
        """Check if product price has dropped since added."""
        if self.price_when_added and self.product:
            return self.product.price < self.price_when_added
        return False

    @property
    def price_drop_amount(self):
        """Get amount of price drop."""
        if self.has_price_drop:
            return self.price_when_added - self.product.price
        return 0

    @property
    def price_drop_percentage(self):
        """Get percentage of price drop."""
        if self.has_price_drop and self.price_when_added > 0:
            return ((self.price_when_added - self.product.price) / self.price_when_added) * 100
        return 0

    @property
    def target_price_reached(self):
        """Check if target price has been reached."""
        if self.target_price and self.product:
            return self.product.price <= self.target_price
        return False

class Profile(models.Model):
    """
    Extended user profile for Retailers (KYC, GST, Credit).
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    shop_name = models.CharField(max_length=255, blank=True)
    gst_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)

    ROLE_CHOICES = [
        ('retailer', 'Retailer'),
        ('distributor', 'Distributor'),
        ('farmer', 'Farmer'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='retailer')

    # Business details
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    credit_used = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    is_kyc_verified = models.BooleanField(default=False)

    class Meta:
        """Meta options for Profile model."""
        indexes = [
            models.Index(fields=['city', 'state'], name='idx_profile_location'),
            models.Index(fields=['is_kyc_verified'], name='idx_profile_kyc'),
        ]

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Order(models.Model):
    """
    Order model to track customer purchases.
    """
    user = models.ForeignKey(
        User, related_name='orders', on_delete=models.SET_NULL, blank=True, null=True
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    address = models.CharField(max_length=255)
    zipcode = models.CharField(max_length=20)
    place = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    payment_intent = models.CharField(max_length=255, blank=True, default='')
    payment_method = models.CharField(max_length=20, default='cod')

    # New status field for tracking
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled')
    ], default='pending')

    class Meta:
        """Meta options for Order model."""
        indexes = [
            models.Index(fields=['user', 'status'], name='idx_order_user_status'),
            models.Index(fields=['created_at'], name='idx_order_created'),
            models.Index(fields=['status', 'paid'], name='idx_order_status_paid'),
            models.Index(fields=['email'], name='idx_order_email'),
        ]

    def __str__(self):
        return str(self.first_name)

class OrderItem(models.Model):
    """
    Individual items within an order.
    """
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='items', on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, related_name='items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=1)
    vendor_paid = models.BooleanField(default=False)

    class Meta:
        """Meta options for OrderItem."""
        indexes = [
            models.Index(
                fields=['order', 'product'],
                name='idx_orderitem_order_product'
            ),
            models.Index(
                fields=['vendor', 'vendor_paid'],
                name='idx_orderitem_vendor_paid'
            ),
        ]

    def __str__(self):
        return str(self.id)

class Review(models.Model):
    """
    Model for storing product reviews and ratings.
    """
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified_purchase = models.BooleanField(default=False)
    helpful_votes = models.ManyToManyField(User, related_name='helpful_reviews', blank=True)

    # Enhanced review features
    vendor_response = models.TextField(
        blank=True,
        help_text="Vendor's response to this review"
    )
    vendor_response_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the vendor responded"
    )
    is_moderated = models.BooleanField(
        default=True,
        help_text="Whether the review has been approved by moderation"
    )

    class Meta:
        """Meta definition for Review."""
        unique_together = ('product', 'user')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', 'rating'], name='idx_review_product_rating'),
            models.Index(fields=['user'], name='idx_review_user'),
            models.Index(fields=['is_verified_purchase'], name='idx_review_verified'),
        ]

    def __str__(self):
        return f"{self.user.username}'s review of {self.product.name}"

    @property
    def helpful_count(self):
        """Return the number of helpful votes."""
        return self.helpful_votes.count()

class Contact(models.Model):
    """
    Model for storing contact form submissions.
    """
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.name)


class FlashSale(models.Model):
    """
    Model for flash sales and limited-time deals.
    """
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    products = models.ManyToManyField(Product, related_name='flash_sales')
    discount_percentage = models.PositiveIntegerField(
        help_text="Discount percentage for all products in this sale"
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    banner_image = models.ImageField(
        upload_to='flash_sales/',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta definition for FlashSale."""
        ordering = ['-start_time']
        indexes = [
            models.Index(
                fields=['is_active', 'start_time', 'end_time'],
                name='idx_flashsale_active_time'
            ),
            models.Index(fields=['slug'], name='idx_flashsale_slug'),
        ]

    def __str__(self):
        return str(self.name)

    @property
    def time_remaining(self):
        """Return time remaining for the sale."""
        now = timezone.now()
        if now > self.end_time:
            return None
        elif now < self.start_time:
            return self.start_time - now
        else:
            return self.end_time - now

    @property
    def is_live(self):
        """Check if the flash sale is currently active and running."""
        now = timezone.now()
        return (
            self.is_active and
            self.start_time <= now <= self.end_time
        )


class BulkOrder(models.Model):
    """
    Model for bulk/wholesale order requests.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(
        User,
        related_name='bulk_orders',
        on_delete=models.CASCADE
    )
    vendor = models.ForeignKey(
        Vendor,
        related_name='bulk_orders',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    product = models.ForeignKey(
        Product,
        related_name='bulk_orders',
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField()
    requested_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Customer's proposed price per unit"
    )
    approved_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Vendor's approved price per unit"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    notes = models.TextField(blank=True)
    vendor_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta definition for BulkOrder."""
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status'], name='idx_bulkorder_user_status'),
            models.Index(fields=['vendor', 'status'], name='idx_bulkorder_vendor_status'),
        ]

    def __str__(self):
        return f"Bulk Order #{self.id} - {self.product.name}"

    @property
    def total_value(self):
        """Calculate total order value."""
        price = self.approved_price or self.requested_price or self.product.price
        return price * self.quantity


class InventoryLog(models.Model):
    """
    Model for tracking inventory changes.
    """
    ACTION_CHOICES = [
        ('add', 'Stock Added'),
        ('remove', 'Stock Removed'),
        ('sale', 'Sold'),
        ('return', 'Returned'),
        ('adjustment', 'Manual Adjustment'),
        ('damaged', 'Damaged/Lost'),
    ]

    product = models.ForeignKey(
        Product,
        related_name='inventory_logs',
        on_delete=models.CASCADE
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    quantity = models.IntegerField(help_text="Positive for add, negative for remove")
    previous_stock = models.PositiveIntegerField()
    new_stock = models.PositiveIntegerField()
    reference = models.CharField(
        max_length=255,
        blank=True,
        help_text="Order ID or other reference"
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options for InventoryLog."""
        indexes = [
            models.Index(fields=['product', 'created_at'], name='idx_invlog_product_date'),
            models.Index(fields=['action'], name='idx_invlog_action'),
        ]

    def __str__(self):
        return f"{self.action}: {self.quantity} units of {self.product.name}"


class VendorVerification(models.Model):
    """
    Model for vendor verification and KYC documents.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('more_info', 'More Info Required'),
    ]

    vendor = models.OneToOneField(
        Vendor,
        related_name='verification',
        on_delete=models.CASCADE
    )
    business_registration = models.FileField(
        upload_to='vendor_docs/registration/',
        blank=True,
        null=True
    )
    gst_certificate = models.FileField(
        upload_to='vendor_docs/gst/',
        blank=True,
        null=True
    )
    pan_card = models.FileField(
        upload_to='vendor_docs/pan/',
        blank=True,
        null=True
    )
    address_proof = models.FileField(
        upload_to='vendor_docs/address/',
        blank=True,
        null=True
    )
    gst_number = models.CharField(max_length=15, blank=True)
    pan_number = models.CharField(max_length=10, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    verification_notes = models.TextField(blank=True)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_vendors'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    is_premium_vendor = models.BooleanField(default=False)
    trust_score = models.PositiveIntegerField(
        default=0,
        help_text="Score from 0-100 based on activity"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Verification for {self.vendor.name}"


class BuyerInquiry(models.Model):
    """
    Model for buyer inquiries/leads (IndiaMART-like feature).
    """
    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('quoted', 'Quote Sent'),
        ('negotiating', 'Negotiating'),
        ('won', 'Won'),
        ('lost', 'Lost'),
    ]

    buyer = models.ForeignKey(
        User,
        related_name='inquiries',
        on_delete=models.CASCADE
    )
    vendor = models.ForeignKey(
        Vendor,
        related_name='inquiries',
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        related_name='inquiries',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    subject = models.CharField(max_length=255)
    message = models.TextField()
    quantity_required = models.PositiveIntegerField(blank=True, null=True)
    budget_range = models.CharField(max_length=100, blank=True)
    delivery_location = models.CharField(max_length=255, blank=True)
    expected_delivery_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new'
    )
    is_urgent = models.BooleanField(default=False)
    contact_phone = models.CharField(max_length=20, blank=True)
    contact_email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta class for BuyerInquiry."""
        verbose_name_plural = 'Buyer Inquiries'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['buyer', 'status'], name='idx_inquiry_buyer_status'),
            models.Index(fields=['vendor', 'status'], name='idx_inquiry_vendor_status'),
            models.Index(fields=['is_urgent', 'created_at'], name='idx_inquiry_urgent_date'),
        ]

    def __str__(self):
        return f"Inquiry from {self.buyer.username} - {self.subject}"


class RFQ(models.Model):
    """
    Request for Quote model (IndiaMART-like feature).
    """
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('quoted', 'Quotes Received'),
        ('closed', 'Closed'),
        ('awarded', 'Awarded'),
        ('cancelled', 'Cancelled'),
    ]

    buyer = models.ForeignKey(
        User,
        related_name='rfqs',
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    quantity = models.PositiveIntegerField()
    unit = models.CharField(
        max_length=50,
        default='pieces',
        help_text="e.g., kg, liters, pieces"
    )
    budget_min = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True
    )
    budget_max = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True
    )
    delivery_location = models.CharField(max_length=255)
    delivery_deadline = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='open'
    )
    is_public = models.BooleanField(
        default=True,
        help_text="Visible to all vendors"
    )
    attachment = models.FileField(
        upload_to='rfq_attachments/',
        blank=True,
        null=True
    )
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options for RFQ."""
        verbose_name = 'RFQ'
        verbose_name_plural = 'RFQs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['buyer', 'status'], name='idx_rfq_buyer_status'),
            models.Index(fields=['status', 'is_public'], name='idx_rfq_status_public'),
            models.Index(fields=['category'], name='idx_rfq_category'),
        ]

    def __str__(self):
        return f"RFQ #{self.id} - {self.title}"


class RFQQuote(models.Model):
    """
    Quote submitted by vendors in response to an RFQ.
    """
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    rfq = models.ForeignKey(
        RFQ,
        related_name='quotes',
        on_delete=models.CASCADE
    )
    vendor = models.ForeignKey(
        Vendor,
        related_name='rfq_quotes',
        on_delete=models.CASCADE
    )
    price_per_unit = models.DecimalField(max_digits=12, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    delivery_time = models.CharField(max_length=100)
    validity_days = models.PositiveIntegerField(default=7)
    terms_and_conditions = models.TextField(blank=True)
    attachment = models.FileField(
        upload_to='quote_attachments/',
        blank=True,
        null=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='submitted'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta options for RFQQuote."""
        unique_together = ('rfq', 'vendor')
        ordering = ['price_per_unit']

    def __str__(self):
        return f"Quote by {self.vendor.name} for RFQ #{self.rfq.id}"


class PremiumListing(models.Model):
    """
    Model for premium/featured product listings.
    """
    POSITION_CHOICES = [
        ('homepage', 'Homepage Banner'),
        ('category_top', 'Category Top'),
        ('search_top', 'Search Results Top'),
        ('sidebar', 'Sidebar'),
    ]

    product = models.ForeignKey(
        Product,
        related_name='premium_listings',
        on_delete=models.CASCADE
    )
    vendor = models.ForeignKey(
        Vendor,
        related_name='premium_listings',
        on_delete=models.CASCADE
    )
    position = models.CharField(max_length=20, choices=POSITION_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    impressions = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta options for PremiumListing."""
        ordering = ['-created_at']
        indexes = [
            models.Index(
                fields=['position', 'is_active', 'start_date', 'end_date'],
                name='idx_premium_position_active'
            ),
        ]

    def __str__(self):
        return f"Premium: {self.product.name} - {self.position}"

    @property
    def ctr(self):
        """Calculate Click-Through Rate."""
        if self.impressions > 0:
            return round((self.clicks / self.impressions) * 100, 2)
        return 0


class Message(models.Model):
    """
    Model for messaging between buyers and sellers.
    """
    sender = models.ForeignKey(
        User,
        related_name='sent_messages',
        on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        User,
        related_name='received_messages',
        on_delete=models.CASCADE
    )
    inquiry = models.ForeignKey(
        BuyerInquiry,
        related_name='messages',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    subject = models.CharField(max_length=255, blank=True)
    content = models.TextField()
    attachment = models.FileField(
        upload_to='message_attachments/',
        blank=True,
        null=True
    )
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta options for Message."""
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sender', 'created_at'], name='idx_message_sender_date'),
            models.Index(fields=['receiver', 'is_read'], name='idx_message_receiver_read'),
        ]

    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username}"


class Deal(models.Model):
    """
    Model for special deals and promotions.
    """
    DEAL_TYPES = [
        ('percentage', 'Percentage Discount'),
        ('fixed', 'Fixed Amount Discount'),
        ('buy_get', 'Buy X Get Y'),
        ('bundle', 'Bundle Deal'),
        ('seasonal', 'Seasonal Promotion'),
    ]

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    deal_type = models.CharField(max_length=20, choices=DEAL_TYPES, default='percentage')
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Discount amount or percentage"
    )
    min_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    products = models.ManyToManyField(Product, related_name='deals', blank=True)
    categories = models.ManyToManyField(Category, related_name='deals', blank=True)
    vendors = models.ManyToManyField(Vendor, related_name='deals', blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    banner_image = models.ImageField(upload_to='deals/', blank=True, null=True)
    terms_conditions = models.TextField(blank=True)
    usage_limit = models.PositiveIntegerField(default=0, help_text="0 = unlimited")
    used_count = models.PositiveIntegerField(default=0)
    priority = models.PositiveIntegerField(default=0, help_text="Higher priority deals show first")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta options for Deal."""
        ordering = ['-priority', '-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_deal_type_display()})"

    @property
    def is_valid(self):
        """Check if deal is currently valid."""
        now = timezone.now()
        return (
            self.is_active and
            self.start_date <= now <= self.end_date and
            (self.usage_limit == 0 or self.used_count < self.usage_limit)
        )

    def calculate_discount(self, price, quantity=1):
        """Calculate discount amount for given price and quantity."""
        if not self.is_valid:
            return 0

        total_price = price * quantity

        if self.deal_type == 'percentage':
            discount = total_price * (self.discount_value / 100)
        elif self.deal_type == 'fixed':
            discount = self.discount_value * quantity
        else:
            # For other deal types, return percentage discount as fallback
            discount = total_price * (self.discount_value / 100)

        # Apply max discount limit if set
        if self.max_discount and discount > self.max_discount:
            discount = self.max_discount

        return discount


class ProductComparison(models.Model):
    """
    Model for storing product comparison sessions.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comparisons')
    session_id = models.CharField(max_length=100, help_text="Unique session identifier")
    products = models.ManyToManyField(Product, related_name='comparisons')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options for ProductComparison."""
        unique_together = ('user', 'session_id')

    def __str__(self):
        return f"Comparison by {self.user.username} - {self.products.count()} products"


class AdvancedSearch(models.Model):
    """
    Model for storing advanced search filters and preferences.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='search_filters')
    name = models.CharField(max_length=100, help_text="Saved search name")
    filters = models.JSONField(help_text="Search filter parameters")
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'name')

    def __str__(self):
        return f"{self.user.username}'s search: {self.name}"


class AnalyticsEvent(models.Model):
    """
    Model for tracking user analytics events.
    """
    EVENT_TYPES = [
        ('page_view', 'Page View'),
        ('product_view', 'Product View'),
        ('add_to_cart', 'Add to Cart'),
        ('purchase', 'Purchase'),
        ('search', 'Search'),
        ('comparison', 'Product Comparison'),
        ('wishlist', 'Wishlist Action'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=100)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True)
    data = models.JSONField(blank=True, null=True, help_text="Additional event data")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta options for AnalyticsEvent."""
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event_type', 'created_at']),
            models.Index(fields=['user', 'event_type']),
        ]

    def __str__(self):
        return f"{self.event_type} by {self.user.username if self.user else 'Anonymous'}"


class VendorAnalytics(models.Model):
    """
    Model for vendor-specific analytics data, stored daily.
    """
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='daily_analytics')
    date = models.DateField(db_index=True)
    total_products = models.PositiveIntegerField(default=0)
    active_products = models.PositiveIntegerField(default=0)
    out_of_stock_products = models.PositiveIntegerField(default=0)
    low_stock_products = models.PositiveIntegerField(default=0)
    total_orders = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    monthly_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    weekly_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.PositiveIntegerField(default=0)
    pending_bulk_orders = models.PositiveIntegerField(default=0)
    top_selling_products = models.JSONField(blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options for VendorAnalytics."""
        unique_together = ('vendor', 'date')
        ordering = ['-date', 'vendor']
        verbose_name = 'Vendor Analytics'
        verbose_name_plural = 'Vendor Analytics'

    def __str__(self):
        return f"Analytics for {self.vendor.name} on {self.date}"


class Notification(models.Model):
    """
    Enhanced notification model with more types and delivery options.
    """
    TYPE_CHOICES = [
        ('order', 'Order Update'),
        ('inquiry', 'New Inquiry'),
        ('message', 'New Message'),
        ('rfq', 'RFQ Update'),
        ('promotion', 'Promotion'),
        ('deal', 'New Deal'),
        ('system', 'System Notification'),
        ('stock', 'Low Stock Alert'),
        ('bulk_order', 'Bulk Order Update'),
        ('review', 'New Review'),
        ('comparison', 'Product Comparison'),
    ]

    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    link = models.URLField(blank=True)
    image = models.ImageField(upload_to='notifications/', blank=True, null=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    is_email_sent = models.BooleanField(default=False)
    is_sms_sent = models.BooleanField(default=False)
    is_push_sent = models.BooleanField(default=False)
    priority = models.CharField(max_length=10, choices=[
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ], default='normal')
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta options for Notification."""
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', 'created_at']),
            models.Index(fields=['notification_type', 'created_at']),
        ]

    def __str__(self):
        return f"{self.notification_type}: {self.title}"

    @property
    def is_expired(self):
        """Check if notification has expired."""
        return self.expires_at and timezone.now() > self.expires_at


class ProductVariant(models.Model):
    """
    Model for product variants (size, packaging, etc.)
    """
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, help_text="e.g., 1kg, 5kg, 25kg")
    sku = models.CharField(max_length=50, unique=True)
    price_modifier = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                       help_text="Additional price for this variant")
    stock_quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        """Meta options for ProductVariant."""
        ordering = ['sort_order', 'name']
        unique_together = ('product', 'name')

    def __str__(self):
        return f"{self.product.name} - {self.name}"

    @property
    def final_price(self):
        """Calculate final price including modifier."""
        return self.product.price + self.price_modifier


class CartItem(models.Model):
    """
    Enhanced cart item model with variant support.
    """
    cart_id = models.CharField(max_length=100)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta options for CartItem."""
        unique_together = ('cart_id', 'product', 'variant')

    def __str__(self):
        variant_info = f" ({self.variant.name})" if self.variant else ""
        return f"{self.product.name}{variant_info} x {self.quantity}"

    @property
    def total_price(self):
        """Calculate total price for this cart item."""
        base_price = self.variant.final_price if self.variant else self.product.price
        return base_price * self.quantity


class Subscription(models.Model):
    """
    Model for user subscriptions (newsletter, price alerts, etc.).
    """
    SUBSCRIPTION_TYPES = [
        ('newsletter', 'Newsletter'),
        ('price_alert', 'Price Alert'),
        ('stock_alert', 'Stock Alert'),
        ('deal_alert', 'Deal Alert'),
        ('vendor_update', 'Vendor Updates'),
    ]

    user = models.ForeignKey(User, related_name='subscriptions', on_delete=models.CASCADE)
    subscription_type = models.CharField(max_length=20, choices=SUBSCRIPTION_TYPES)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    frequency = models.CharField(max_length=20, choices=[
        ('immediate', 'Immediate'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ], default='weekly')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta options for Subscription."""
        unique_together = ('user', 'subscription_type', 'product', 'vendor', 'category')

    def __str__(self):
        return f"{self.user.username} - {self.get_subscription_type_display()}"


class AuditLog(models.Model):
    """
    Model for tracking all admin actions (audit trail).
    """
    ACTION_CHOICES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('login', 'Logged In'),
        ('logout', 'Logged Out'),
        ('export', 'Data Exported'),
        ('import', 'Data Imported'),
        ('verify', 'Verified'),
        ('reject', 'Rejected'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    object_repr = models.CharField(max_length=255)
    changes = models.JSONField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta options for AuditLog."""
        ordering = ['-created_at']
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'

    def __str__(self):
        return f"{self.user} {self.action} {self.model_name}"


class SiteSettings(models.Model):
    """
    Model for site-wide settings (singleton pattern).
    """
    site_name = models.CharField(max_length=255, default='Agri B2B')
    site_tagline = models.CharField(max_length=255, blank=True)
    site_logo = models.ImageField(upload_to='settings/', blank=True, null=True)
    favicon = models.ImageField(upload_to='settings/', blank=True, null=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    # Social Links
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)

    # SEO Settings
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    google_analytics_id = models.CharField(max_length=50, blank=True)

    # Feature Toggles
    enable_rfq = models.BooleanField(default=True)
    enable_premium_listings = models.BooleanField(default=True)
    enable_messaging = models.BooleanField(default=True)
    enable_reviews = models.BooleanField(default=True)
    maintenance_mode = models.BooleanField(default=False)
    maintenance_message = models.TextField(blank=True)

    # Commission Settings
    default_commission_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=5.00,
        help_text="Default commission percentage"
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = SITE_SETTINGS_NAME
        verbose_name_plural = SITE_SETTINGS_NAME

    def __str__(self):
        return str(self.site_name) if self.site_name else SITE_SETTINGS_NAME

    def save(self, *args, **kwargs):
        """Ensure only one instance exists."""
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        """Get or create site settings."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class TradeEvent(models.Model):
    """
    Model for trade shows/events (IndiaMART-like feature).
    """
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    banner_image = models.ImageField(
        upload_to='events/',
        blank=True,
        null=True
    )
    venue = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    registration_deadline = models.DateField(null=True, blank=True)
    entry_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    max_exhibitors = models.PositiveIntegerField(default=100)
    organizer = models.CharField(max_length=255, blank=True)
    website_url = models.URLField(blank=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_date']

    def __str__(self):
        return str(self.name) if self.name else f'Trade Event #{self.pk}'


class EventRegistration(models.Model):
    """
    Model for event registrations.
    """
    event = models.ForeignKey(
        TradeEvent,
        related_name='registrations',
        on_delete=models.CASCADE
    )
    vendor = models.ForeignKey(
        Vendor,
        related_name='event_registrations',
        on_delete=models.CASCADE
    )
    booth_number = models.CharField(max_length=20, blank=True)
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('paid', 'Paid'),
            ('refunded', 'Refunded'),
        ],
        default='pending'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta class for EventRegistration."""
        unique_together = ('event', 'vendor')

    def __str__(self):
        return f"{self.vendor.name} - {self.event.name}"


class NewsletterSubscription(models.Model):
    """
    Model for newsletter subscriptions.
    Separate from user Subscription model for email-only signups.
    """
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    source = models.CharField(
        max_length=50,
        default='website',
        help_text='Where user subscribed from'
    )

    class Meta:
        """Meta definition for NewsletterSubscription."""
        ordering = ['-subscribed_at']
        verbose_name = 'Newsletter Subscription'
        verbose_name_plural = 'Newsletter Subscriptions'

    def __str__(self):
        return str(self.email) if self.email else f'Subscription #{self.pk}'


# ============================================
# AGRIM-STYLE MODELS FOR AGRI B2B PLATFORM
# ============================================

class Crop(models.Model):
    """
    Model for crops that products can target.
    Used for 'Shop by Crop' feature.
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    hindi_name = models.CharField(max_length=100, blank=True, help_text="Name in Hindi")
    image = models.ImageField(upload_to='crops/', blank=True, null=True)
    icon = models.CharField(max_length=10, blank=True, help_text="Emoji icon for the crop")
    description = models.TextField(blank=True)
    season = models.CharField(
        max_length=20,
        choices=[
            ('kharif', 'Kharif (Monsoon)'),
            ('rabi', 'Rabi (Winter)'),
            ('zaid', 'Zaid (Summer)'),
            ('all', 'All Seasons'),
        ],
        default='all'
    )
    is_popular = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['is_popular', 'order'], name='idx_crop_popular_order'),
            models.Index(fields=['season'], name='idx_crop_season'),
        ]

    def __str__(self):
        return str(self.name) if self.name else f'Crop #{self.pk}'


class Disease(models.Model):
    """
    Model for plant diseases and pests.
    Used for 'Shop by Disease' feature.
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    hindi_name = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='diseases/', blank=True, null=True)
    icon = models.CharField(max_length=10, blank=True, help_text="Emoji icon")
    description = models.TextField(blank=True)
    symptoms = models.TextField(blank=True, help_text="Visible symptoms of the disease")
    affected_crops = models.ManyToManyField(Crop, related_name='diseases', blank=True)
    prevention_tips = models.TextField(blank=True)
    is_common = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['is_common', 'order'], name='idx_disease_common_order'),
        ]

    def __str__(self):
        return str(self.name) if self.name else f'Disease #{self.pk}'


class ProductCropMapping(models.Model):
    """
    Many-to-many relationship between products and crops.
    """
    product = models.ForeignKey(Product, related_name='crop_mappings', on_delete=models.CASCADE)
    crop = models.ForeignKey(Crop, related_name='product_mappings', on_delete=models.CASCADE)
    effectiveness_rating = models.PositiveIntegerField(
        default=5,
        help_text="Rating 1-10 for how effective this product is for this crop"
    )
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('product', 'crop')

    def __str__(self):
        return f"{self.product.name} → {self.crop.name}"


class ProductDiseaseMapping(models.Model):
    """
    Many-to-many relationship between products and diseases.
    """
    product = models.ForeignKey(Product, related_name='disease_mappings', on_delete=models.CASCADE)
    disease = models.ForeignKey(Disease, related_name='product_mappings', on_delete=models.CASCADE)
    effectiveness_rating = models.PositiveIntegerField(
        default=5,
        help_text="Rating 1-10 for how effective this product is against this disease"
    )
    dosage_info = models.TextField(blank=True, help_text="Specific dosage for this disease")

    class Meta:
        unique_together = ('product', 'disease')

    def __str__(self):
        return f"{self.product.name} treats {self.disease.name}"


class ProductPackingOption(models.Model):
    """
    Multiple packing sizes for a product (e.g., 500ml, 1L, 5L).
    """
    product = models.ForeignKey(Product, related_name='packing_options', on_delete=models.CASCADE)
    size = models.CharField(max_length=50, help_text="e.g., 500ml, 1kg, 5L")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    mrp = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.PositiveIntegerField(default=100)
    sku = models.CharField(max_length=50, blank=True)
    is_default = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'price']
        indexes = [
            models.Index(fields=['product', 'is_default'], name='idx_packing_product_default'),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.size}"

    @property
    def discount_percentage(self):
        if self.mrp and self.mrp > self.price:
            return int(((self.mrp - self.price) / self.mrp) * 100)
        return 0


class BulkPricing(models.Model):
    """
    Bulk/volume-based pricing tiers for products.
    """
    product = models.ForeignKey(Product, related_name='bulk_pricing_tiers', on_delete=models.CASCADE)
    min_quantity = models.PositiveIntegerField(help_text="Minimum quantity for this price tier")
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    class Meta:
        """Meta options for BulkPricing."""
        ordering = ['min_quantity']
        unique_together = ('product', 'min_quantity')

    def __str__(self):
        return f"{self.product.name}: {self.min_quantity}+ units @ ₹{self.price_per_unit}"


class LocationPopularity(models.Model):
    """
    Track product popularity by location for 'Popular in [City]' feature.
    """
    product = models.ForeignKey(Product, related_name='location_popularity', on_delete=models.CASCADE)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    view_count = models.PositiveIntegerField(default=0)
    cart_add_count = models.PositiveIntegerField(default=0)
    purchase_count = models.PositiveIntegerField(default=0)
    popularity_score = models.FloatField(default=0.0, help_text="Calculated score for ranking")
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'city')
        ordering = ['-popularity_score']
        indexes = [
            models.Index(fields=['city', 'popularity_score'], name='idx_locpop_city_score'),
            models.Index(fields=['state', 'popularity_score'], name='idx_locpop_state_score'),
        ]

    def __str__(self):
        return f"{self.product.name} in {self.city}"

    def calculate_score(self):
        """Calculate popularity score based on interactions."""
        self.popularity_score = (
            self.view_count * 1 +
            self.cart_add_count * 5 +
            self.purchase_count * 10
        )
        return self.popularity_score


class PriceAlert(models.Model):
    """
    Price drop alerts for users.
    """
    user = models.ForeignKey(User, related_name='price_alerts', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='price_alerts', on_delete=models.CASCADE)
    target_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_price_at_creation = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    is_triggered = models.BooleanField(default=False)
    triggered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta options for PriceAlert."""
        unique_together = ('user', 'product')
        ordering = ['-created_at']
        indexes = [
            models.Index(
                fields=['product', 'is_active', 'target_price'],
                name='idx_pricealert_product'
            ),
            models.Index(
                fields=['user', 'is_active'],
                name='idx_pricealert_user'
            ),
        ]

    def __str__(self):
        return f"Alert: {self.user.username} wants {self.product.name} at ₹{self.target_price}"


class UserCoin(models.Model):
    """
    Coin/reward system for users (AGRIM-style).
    """
    user = models.OneToOneField(User, related_name='coins', on_delete=models.CASCADE)
    balance = models.PositiveIntegerField(default=0)
    lifetime_earned = models.PositiveIntegerField(default=0)
    lifetime_spent = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}: {self.balance} coins"

    def add_coins(self, amount, reason=''):
        """Add coins to user balance."""
        self.balance += amount
        self.lifetime_earned += amount
        self.save()
        CoinTransaction.objects.create(
            user_coin=self,
            amount=amount,
            transaction_type='credit',
            reason=reason
        )

    def spend_coins(self, amount, reason=''):
        """Spend coins from user balance."""
        if amount > self.balance:
            raise ValueError("Insufficient coin balance")
        self.balance -= amount
        self.lifetime_spent += amount
        self.save()
        CoinTransaction.objects.create(
            user_coin=self,
            amount=amount,
            transaction_type='debit',
            reason=reason
        )


class CoinTransaction(models.Model):
    """
    Track coin transactions.
    """
    user_coin = models.ForeignKey(UserCoin, related_name='transactions', on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    transaction_type = models.CharField(
        max_length=10,
        choices=[('credit', 'Credit'), ('debit', 'Debit')]
    )
    reason = models.CharField(max_length=255, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_type}: {self.amount} coins"


class OTPVerification(models.Model):
    """
    OTP-based login/verification system.
    """
    phone = models.CharField(max_length=15)
    otp = models.CharField(max_length=6)
    purpose = models.CharField(
        max_length=20,
        choices=[
            ('login', 'Login'),
            ('register', 'Registration'),
            ('reset', 'Password Reset'),
            ('verify', 'Phone Verification'),
        ],
        default='login'
    )
    is_verified = models.BooleanField(default=False)
    attempts = models.PositiveIntegerField(default=0)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['phone', 'purpose', 'is_verified'], name='idx_otp_phone_purpose'),
        ]

    def __str__(self):
        return f"OTP for {self.phone}"

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        return not self.is_expired and not self.is_verified and self.attempts < 5


class DealOfTheDay(models.Model):
    """
    Featured deal of the day products.
    """
    products = models.ManyToManyField(Product, related_name='deal_of_day')
    date = models.DateField(unique=True)
    title = models.CharField(max_length=255, default="Deal of the Day")
    discount_percentage = models.PositiveIntegerField(default=20)
    start_time = models.TimeField(default='00:00:00')
    end_time = models.TimeField(default='23:59:59')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name_plural = "Deals of the Day"

    def __str__(self):
        return f"Deal for {self.date}"

    @property
    def is_live(self):
        now = timezone.now()
        today = now.date()
        current_time = now.time()
        return (
            self.is_active and
            self.date == today and
            self.start_time <= current_time <= self.end_time
        )


class UserSession(models.Model):
    """
    Model for tracking user sessions and interactions.
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=100, unique=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    device_type = models.CharField(max_length=50, blank=True)
    operating_system = models.CharField(max_length=50, blank=True)
    browser = models.CharField(max_length=50, blank=True)
    is_mobile = models.BooleanField(default=False)
    is_tablet = models.BooleanField(default=False)
    is_desktop = models.BooleanField(default=False)
    screen_resolution = models.CharField(max_length=50, blank=True)
    language = models.CharField(max_length=20, blank=True)
    referrer = models.URLField(blank=True)
    landing_page = models.URLField(blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    duration_seconds = models.PositiveIntegerField(default=0)
    page_views = models.PositiveIntegerField(default=0)
    last_activity = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options for UserSession."""
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', 'started_at'], name='idx_session_user_date'),
            models.Index(fields=['is_active'], name='idx_session_active'),
            models.Index(fields=['session_id'], name='idx_session_id'),
        ]

    def __str__(self):
        return f"Session {self.session_id} - {self.user.username if self.user else 'Anonymous'}"

    def end_session(self):
        """End the session and calculate duration."""
        if self.is_active:
            self.is_active = False
            self.ended_at = timezone.now()
            self.duration_seconds = int((self.ended_at - self.started_at).total_seconds())
            self.save()

class UserInteraction(models.Model):
    """
    Model for tracking detailed user interactions and behaviors.
    """
    INTERACTION_TYPES = [
        ('page_view', 'Page View'),
        ('product_view', 'Product View'),
        ('add_to_cart', 'Add to Cart'),
        ('remove_from_cart', 'Remove from Cart'),
        ('checkout_start', 'Checkout Started'),
        ('purchase', 'Purchase Completed'),
        ('search', 'Search'),
        ('filter', 'Filter Applied'),
        ('sort', 'Sort Applied'),
        ('wishlist_add', 'Wishlist Add'),
        ('wishlist_remove', 'Wishlist Remove'),
        ('review_submit', 'Review Submitted'),
        ('click', 'Click'),
        ('hover', 'Hover'),
        ('scroll', 'Scroll'),
        ('form_submit', 'Form Submit'),
        ('video_play', 'Video Play'),
        ('video_pause', 'Video Pause'),
        ('video_complete', 'Video Complete'),
        ('error', 'Error Encountered'),
        ('custom', 'Custom Event'),
    ]

    session = models.ForeignKey(UserSession, related_name='interactions', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    interaction_type = models.CharField(max_length=30, choices=INTERACTION_TYPES)
    page_url = models.URLField(blank=True)
    page_title = models.CharField(max_length=255, blank=True)
    element_id = models.CharField(max_length=100, blank=True)
    element_class = models.CharField(max_length=100, blank=True)
    element_text = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    scroll_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    mouse_x = models.PositiveIntegerField(null=True, blank=True)
    mouse_y = models.PositiveIntegerField(null=True, blank=True)
    metadata = models.JSONField(blank=True, null=True)
    is_conversion = models.BooleanField(default=False)
    conversion_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        """Meta options for UserInteraction."""
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['session', 'timestamp'], name='idx_interaction_session_time'),
            models.Index(fields=['user', 'interaction_type'], name='idx_interaction_user_type'),
            models.Index(fields=['interaction_type', 'timestamp'], name='idx_interaction_type_time'),
        ]

    def __str__(self):
        return f"{self.interaction_type} - {self.session.session_id}"

class UserBehaviorPattern(models.Model):
    """
    Model for analyzing and storing user behavior patterns.
    """
    user = models.ForeignKey(User, related_name='behavior_patterns', on_delete=models.CASCADE)
    pattern_type = models.CharField(max_length=50)
    pattern_data = models.JSONField()
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    frequency = models.PositiveIntegerField(default=1)
    last_observed = models.DateTimeField(auto_now=True)
    first_observed = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        """Meta options for UserBehaviorPattern."""
        ordering = ['-confidence_score', '-last_observed']
        indexes = [
            models.Index(fields=['user', 'pattern_type'], name='idx_behavior_user_type'),
            models.Index(fields=['pattern_type', 'confidence_score'], name='idx_behavior_type_score'),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.pattern_type} ({self.confidence_score}%)"

class UserPreference(models.Model):
    """
    Model for storing user preferences and personalization data.
    """
    user = models.ForeignKey(User, related_name='preferences', on_delete=models.CASCADE)
    preference_type = models.CharField(max_length=50)
    preference_key = models.CharField(max_length=100)
    preference_value = models.TextField()
    data_type = models.CharField(max_length=20, choices=[
        ('string', 'String'),
        ('number', 'Number'),
        ('boolean', 'Boolean'),
        ('json', 'JSON'),
        ('array', 'Array'),
    ], default='string')
    source = models.CharField(max_length=50, choices=[
        ('explicit', 'Explicit User Input'),
        ('implicit', 'Inferred from Behavior'),
        ('default', 'System Default'),
    ], default='implicit')
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta options for UserPreference."""
        unique_together = ('user', 'preference_type', 'preference_key')
        indexes = [
            models.Index(fields=['user', 'preference_type'], name='idx_preference_user_type'),
            models.Index(fields=['preference_type', 'preference_key'], name='idx_preference_type_key'),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.preference_type}:{self.preference_key}"

class UserFeedback(models.Model):
    """
    Model for collecting and analyzing user feedback.
    """
    FEEDBACK_TYPES = [
        ('rating', 'Rating'),
        ('review', 'Review'),
        ('survey', 'Survey Response'),
        ('contact', 'Contact Form'),
        ('bug_report', 'Bug Report'),
        ('feature_request', 'Feature Request'),
        ('general', 'General Feedback'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session = models.ForeignKey(UserSession, on_delete=models.SET_NULL, null=True, blank=True)
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES)
    rating = models.PositiveSmallIntegerField(null=True, blank=True)
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    sentiment_score = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    sentiment_analysis = models.JSONField(blank=True, null=True)
    is_positive = models.BooleanField(null=True, blank=True)
    is_negative = models.BooleanField(null=True, blank=True)
    is_neutral = models.BooleanField(null=True, blank=True)
    tags = models.JSONField(blank=True, null=True)
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_processed = models.BooleanField(default=False)
    response_status = models.CharField(max_length=20, choices=[
        ('new', 'New'),
        ('read', 'Read'),
        ('responded', 'Responded'),
        ('resolved', 'Resolved'),
        ('archived', 'Archived'),
    ], default='new')

    class Meta:
        """Meta options for UserFeedback."""
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at'], name='idx_feedback_user_date'),
            models.Index(fields=['feedback_type', 'created_at'], name='idx_feedback_type_date'),
            models.Index(fields=['sentiment_score'], name='idx_feedback_sentiment'),
        ]

    def __str__(self):
        return f"Feedback #{self.id} - {self.feedback_type}"

    def analyze_sentiment(self):
        """Analyze sentiment of feedback content."""
        # This will be implemented in the sentiment analysis service
        return None

class UserSegment(models.Model):
    """
    Model for user segmentation and targeting.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    criteria = models.JSONField(help_text="Segmentation criteria in JSON format")
    user_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        """Meta options for UserSegment."""
        ordering = ['name']
        indexes = [
            models.Index(fields=['is_active'], name='idx_segment_active'),
            models.Index(fields=['user_count'], name='idx_segment_count'),
        ]

    def __str__(self):
        return str(self.name)

class UserSegmentMembership(models.Model):
    """
    Model for tracking which users belong to which segments.
    """
    user = models.ForeignKey(User, related_name='segment_memberships', on_delete=models.CASCADE)
    segment = models.ForeignKey(UserSegment, related_name='members', on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    membership_score = models.DecimalField(max_digits=5, decimal_places=2, default=1.00)

    class Meta:
        """Meta options for UserSegmentMembership."""
        unique_together = ('user', 'segment')
        indexes = [
            models.Index(fields=['user', 'segment'], name='idx_membership_user_segment'),
            models.Index(fields=['segment', 'membership_score'], name='idx_membership_segment_score'),
        ]

    def __str__(self):
        return f"{self.user.username} in {self.segment.name}"

class UserAnalyticsReport(models.Model):
    """
    Model for storing generated analytics reports.
    """
    REPORT_TYPES = [
        ('user_behavior', 'User Behavior Report'),
        ('conversion_funnel', 'Conversion Funnel Report'),
        ('retention', 'Retention Report'),
        ('engagement', 'Engagement Report'),
        ('demographics', 'Demographics Report'),
        ('custom', 'Custom Report'),
    ]

    FORMAT_CHOICES = [
        ('json', 'JSON'),
        ('csv', 'CSV'),
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('html', 'HTML'),
    ]

    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
    description = models.TextField(blank=True)
    criteria = models.JSONField(help_text="Report generation criteria")
    data = models.JSONField(blank=True, null=True)
    file = models.FileField(upload_to='analytics_reports/', blank=True, null=True)
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='json')
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_scheduled = models.BooleanField(default=False)
    schedule_frequency = models.CharField(max_length=20, choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ], blank=True)
    next_run = models.DateTimeField(null=True, blank=True)

    class Meta:
        """Meta options for UserAnalyticsReport."""
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['report_type', 'generated_at'], name='idx_report_type_date'),
            models.Index(fields=['generated_by', 'generated_at'], name='idx_report_user_date'),
        ]

    def __str__(self):
        return f"{self.title} ({self.report_type})"

class UserPredictiveModel(models.Model):
    """
    Model for storing predictive analytics models and results.
    """
    MODEL_TYPES = [
        ('churn', 'Churn Prediction'),
        ('purchase', 'Purchase Prediction'),
        ('lifetime_value', 'Customer Lifetime Value'),
        ('recommendation', 'Recommendation'),
        ('engagement', 'Engagement Prediction'),
        ('conversion', 'Conversion Prediction'),
    ]

    name = models.CharField(max_length=100)
    model_type = models.CharField(max_length=30, choices=MODEL_TYPES)
    description = models.TextField(blank=True)
    model_data = models.JSONField(blank=True, null=True)
    training_data = models.JSONField(blank=True, null=True)
    evaluation_metrics = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    version = models.CharField(max_length=20, default='1.0')

    class Meta:
        """Meta options for UserPredictiveModel."""
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['model_type', 'is_active'], name='idx_predictive_type_active'),
            models.Index(fields=['created_at'], name='idx_predictive_created'),
        ]

    def __str__(self):
        return f"{self.name} ({self.model_type})"

class UserPredictiveResult(models.Model):
    """
    Model for storing individual predictive analytics results.
    """
    user = models.ForeignKey(User, related_name='predictive_results', on_delete=models.CASCADE)
    model = models.ForeignKey(UserPredictiveModel, related_name='results', on_delete=models.CASCADE)
    prediction_score = models.DecimalField(max_digits=10, decimal_places=6)
    prediction_class = models.CharField(max_length=50, blank=True)
    confidence = models.DecimalField(max_digits=5, decimal_places=2)
    prediction_data = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        """Meta options for UserPredictiveResult."""
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'model'], name='idx_prediction_user_model'),
            models.Index(fields=['model', 'created_at'], name='idx_prediction_model_date'),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.model.name} ({self.prediction_score})"

class UserActivityLog(models.Model):
    """
    Model for comprehensive user activity logging.
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session = models.ForeignKey(UserSession, on_delete=models.SET_NULL, null=True, blank=True)
    activity_type = models.CharField(max_length=50)
    activity_data = models.JSONField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_sensitive = models.BooleanField(default=False)

    class Meta:
        """Meta options for UserActivityLog."""
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp'], name='idx_activity_user_time'),
            models.Index(fields=['activity_type', 'timestamp'], name='idx_activity_type_time'),
        ]

    def __str__(self):
        return f"{self.activity_type} - {self.user.username if self.user else 'Anonymous'}"

class UserDataEncryption(models.Model):
    """
    Model for tracking data encryption and security.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    data_type = models.CharField(max_length=50)
    encryption_method = models.CharField(max_length=50)
    encryption_key = models.CharField(max_length=100, blank=True)
    is_encrypted = models.BooleanField(default=True)
    encrypted_at = models.DateTimeField(auto_now_add=True)
    last_decrypted = models.DateTimeField(null=True, blank=True)

    class Meta:
        """Meta options for UserDataEncryption."""
        unique_together = ('user', 'data_type')
        indexes = [
            models.Index(fields=['user', 'data_type'], name='idx_encryption_user_type'),
            models.Index(fields=['is_encrypted'], name='idx_encryption_status'),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.data_type} encryption"

class UserAnalyticsDashboard(models.Model):
    """
    Model for storing user analytics dashboard configurations.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dashboard_name = models.CharField(max_length=100)
    configuration = models.JSONField()
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options for UserAnalyticsDashboard."""
        unique_together = ('user', 'dashboard_name')
        indexes = [
            models.Index(fields=['user', 'is_default'], name='idx_dashboard_user_default'),
            models.Index(fields=['dashboard_name'], name='idx_dashboard_name'),
        ]

    def __str__(self):
        return f"{self.user.username}'s {self.dashboard_name} Dashboard"

class UserAnalyticsIntegration(models.Model):
    """
    Model for tracking integrations with external analytics tools.
    """
    INTEGRATION_TYPES = [
        ('google_analytics', 'Google Analytics'),
        ('google_tag_manager', 'Google Tag Manager'),
        ('facebook_pixel', 'Facebook Pixel'),
        ('hotjar', 'Hotjar'),
        ('mixpanel', 'Mixpanel'),
        ('amplitude', 'Amplitude'),
        ('custom', 'Custom Integration'),
    ]

    integration_type = models.CharField(max_length=30, choices=INTEGRATION_TYPES)
    configuration = models.JSONField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options for UserAnalyticsIntegration."""
        ordering = ['integration_type']
        indexes = [
            models.Index(fields=['integration_type', 'is_active'], name='idx_integration_type_active'),
        ]

    def __str__(self):
        return f"{self.integration_type} Integration"

class UserAnalyticsAPIKey(models.Model):
    """
    Model for managing API keys for analytics access.
    """
    name = models.CharField(max_length=100)
    api_key = models.CharField(max_length=100, unique=True)
    secret_key = models.CharField(max_length=100, blank=True)
    permissions = models.JSONField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    last_used = models.DateTimeField(null=True, blank=True)
    usage_count = models.PositiveIntegerField(default=0)

    class Meta:
        """Meta options for UserAnalyticsAPIKey."""
        indexes = [
            models.Index(fields=['is_active'], name='idx_apikey_active'),
            models.Index(fields=['created_at'], name='idx_apikey_created'),
        ]

    def __str__(self):
        return f"{self.name} API Key"

    def set_secret_key(self, raw_key):
        """
        Hashes and sets the secret key.
        """
        from django.contrib.auth.hashers import make_password
        self.secret_key = make_password(raw_key)

    def verify_secret_key(self, raw_key):
        """
        Verifies the provided secret key against the stored hash.
        Handles backward compatibility for plaintext keys.
        """
        from django.contrib.auth.hashers import check_password, make_password

        # Try verifying as hash
        if check_password(raw_key, self.secret_key):
            return True

        # Fallback: Check if stored as plaintext (Legacy)
        if self.secret_key == raw_key:
            # Auto-migrate to hash
            self.secret_key = make_password(raw_key)
            self.save(update_fields=['secret_key'])
            return True

        return False

class UserAnalyticsWebhook(models.Model):
    """
    Model for managing analytics webhooks.
    """
    name = models.CharField(max_length=100)
    url = models.URLField()
    events = models.JSONField(help_text="List of events to trigger webhook")
    secret = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_triggered = models.DateTimeField(null=True, blank=True)
    failure_count = models.PositiveIntegerField(default=0)

    class Meta:
        """Meta options for UserAnalyticsWebhook."""
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['is_active', 'name'], name='idx_webhook_active_name'),
            models.Index(fields=['created_at'], name='idx_webhook_created'),
        ]

    def __str__(self):
        return f"{self.name} Webhook"

class UserAnalyticsExport(models.Model):
    """
    Model for tracking data exports.
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    export_type = models.CharField(max_length=50)
    criteria = models.JSONField()
    file = models.FileField(upload_to='analytics_exports/')
    format = models.CharField(max_length=10)
    record_count = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        """Meta options for UserAnalyticsExport."""
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at'], name='idx_export_user_date'),
            models.Index(fields=['status', 'created_at'], name='idx_export_status_date'),
        ]

    def __str__(self):
        return f"Export #{self.id} - {self.export_type}"

class UserAnalyticsAuditLog(models.Model):
    """
    Model for auditing analytics system activities.
    """
    AUDIT_TYPES = [
        ('data_access', 'Data Access'),
        ('report_generation', 'Report Generation'),
        ('configuration_change', 'Configuration Change'),
        ('data_export', 'Data Export'),
        ('api_access', 'API Access'),
        ('integration_change', 'Integration Change'),
        ('security_event', 'Security Event'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    audit_type = models.CharField(max_length=30, choices=AUDIT_TYPES)
    description = models.TextField()
    metadata = models.JSONField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta options for UserAnalyticsAuditLog."""
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['audit_type', 'timestamp'], name='idx_audit_type_time'),
            models.Index(fields=['user', 'timestamp'], name='idx_audit_user_time'),
        ]

    def __str__(self):
        return f"{self.audit_type} - {self.user.username if self.user else 'System'}"


# ============================================
# ADMIN-CONTROLLED TRACKING SYSTEM MODELS
# ============================================

class TrackingConfiguration(models.Model):
    """
    Model for configuring which tracking features are enabled.
    This allows admins to granularly control what gets tracked.
    """
    TRACKING_CATEGORIES = [
        ('file_operations', 'File Operations Tracking'),
        ('user_actions', 'User Action Monitoring'),
        ('system_access', 'System Access Patterns'),
        ('data_modifications', 'Data Modification Tracking'),
        ('login_sessions', 'Login/Session Monitoring'),
        ('performance_metrics', 'Performance Metrics'),
        ('security_events', 'Security Events'),
        ('api_calls', 'API Call Tracking'),
        ('database_queries', 'Database Query Tracking'),
        ('error_tracking', 'Error Tracking'),
    ]

    category = models.CharField(max_length=30, choices=TRACKING_CATEGORIES, unique=True)
    is_enabled = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    config_data = models.JSONField(default=dict, blank=True)
    retention_days = models.PositiveIntegerField(default=90)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tracking Configuration'
        verbose_name_plural = 'Tracking Configurations'

    def __str__(self):
        return f"{self.get_category_display()}: {'Enabled' if self.is_enabled else 'Disabled'}"


class TrackingAlert(models.Model):
    """
    Model for storing system and security alerts.
    """
    ALERT_TYPES = [
        ('security', 'Security Alert'),
        ('performance', 'Performance Alert'),
        ('system', 'System Alert'),
        ('compliance', 'Compliance Alert'),
    ]

    SEVERITY_LEVELS = [
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('high', 'High Priority'),
        ('critical', 'Critical'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
        ('ignored', 'Ignored'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='info')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    # Metadata
    source = models.CharField(max_length=100, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    # Resolution tracking
    acknowledged_by = models.ForeignKey(
        User, related_name='acknowledged_alerts',
        on_delete=models.SET_NULL, null=True, blank=True
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        User, related_name='resolved_alerts',
        on_delete=models.SET_NULL, null=True, blank=True
    )
    resolved_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tracking Alert'
        verbose_name_plural = 'Tracking Alerts'
        indexes = [
            models.Index(fields=['status', 'severity']),
            models.Index(fields=['alert_type', 'created_at']),
        ]

    def __str__(self):
        return f"[{self.get_severity_display()}] {self.title}"


class AdminTrackingAudit(models.Model):
    """
    Audit log for sensitive admin actions.
    """
    action = models.CharField(max_length=50)
    admin_user = models.ForeignKey(
        User, related_name='admin_audit_logs',
        on_delete=models.SET_NULL, null=True, blank=True
    )
    target_type = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100, null=True, blank=True)
    object_repr = models.CharField(max_length=255, blank=True)

    changes = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    is_successful = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)

    action_timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Admin Audit Log'
        verbose_name_plural = 'Admin Audit Logs'
        indexes = [
            models.Index(fields=['action', 'action_timestamp']),
            models.Index(fields=['admin_user', 'action_timestamp']),
            models.Index(fields=['target_type']),
        ]

    def __str__(self):
        return f"{self.admin_user} - {self.action} ({self.action_timestamp})"


class SystemFileTracker(models.Model):
    """
    Model for tracking file operations across the system.
    """
    FILE_OPERATIONS = [
        ('create', 'File Created'),
        ('read', 'File Read'),
        ('update', 'File Updated'),
        ('delete', 'File Deleted'),
        ('upload', 'File Uploaded'),
        ('download', 'File Downloaded'),
        ('move', 'File Moved'),
        ('copy', 'File Copied'),
    ]

    operation = models.CharField(max_length=10, choices=FILE_OPERATIONS)
    file_path = models.CharField(max_length=500)
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField(null=True, blank=True)
    file_type = models.CharField(max_length=50, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    request_path = models.CharField(max_length=255, blank=True)
    operation_timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)
    is_sensitive = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'File Operation'
        verbose_name_plural = 'File Operations'
        indexes = [
            models.Index(fields=['operation', 'operation_timestamp']),
            models.Index(fields=['user', 'operation_timestamp']),
            models.Index(fields=['file_path']),
            models.Index(fields=['ip_address', 'operation_timestamp']),
        ]

    def __str__(self):
        return f"{self.operation} - {self.file_name}"


class PerformanceMetric(models.Model):
    """
    Model for tracking system performance metrics.
    """
    metric_type = models.CharField(max_length=50)
    metric_value = models.FloatField()
    metric_unit = models.CharField(max_length=20, default='count')
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = 'Performance Metric'
        verbose_name_plural = 'Performance Metrics'
        indexes = [
            models.Index(fields=['metric_type', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.metric_type}: {self.metric_value} {self.metric_unit}"


class UserActionTracker(models.Model):
    """
    Model for tracking detailed user actions and behaviors.
    """
    ACTION_TYPES = [
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('page_view', 'Page View'),
        ('button_click', 'Button Click'),
        ('form_submit', 'Form Submit'),
        ('search', 'Search Query'),
        ('filter_apply', 'Filter Applied'),
        ('sort_apply', 'Sort Applied'),
        ('download', 'Download'),
        ('upload', 'Upload'),
        ('purchase', 'Purchase'),
        ('cart_add', 'Add to Cart'),
        ('cart_remove', 'Remove from Cart'),
        ('wishlist_add', 'Add to Wishlist'),
        ('wishlist_remove', 'Remove from Wishlist'),
        ('review_submit', 'Review Submitted'),
        ('profile_update', 'Profile Updated'),
        ('password_change', 'Password Changed'),
        ('email_change', 'Email Changed'),
        ('custom_action', 'Custom Action'),
    ]

    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=100, default='')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    page_url = models.URLField(blank=True, default='')
    page_title = models.CharField(max_length=255, blank=True)
    element_id = models.CharField(max_length=100, blank=True)
    element_class = models.CharField(max_length=100, blank=True)
    action_timestamp = models.DateTimeField(auto_now_add=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    scroll_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    mouse_x = models.PositiveIntegerField(null=True, blank=True)
    mouse_y = models.PositiveIntegerField(null=True, blank=True)
    exit_intent_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="AI-estimated intent to leave the website based on mouse movements")
    heat_map_data = models.JSONField(default=dict, blank=True)
    performance_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="AI-estimated page performance score based on user actions")
    heat_map_timestamp = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'User Action'
        verbose_name_plural = 'User Actions'
        indexes = [
            models.Index(fields=['action_type', 'action_timestamp']),
            models.Index(fields=['user', 'action_timestamp']),
            models.Index(fields=['session_id', 'action_timestamp']),
            models.Index(fields=['page_url', 'action_timestamp']),
        ]

    def __str__(self):
        return f"{self.action_type} - {self.user.username if self.user else 'Anonymous'} ({self.action_timestamp})"


class RecentlyViewed(models.Model):
    """
    Track recently viewed products for each user.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recently_viewed'
    )
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='viewed_by'
    )
    viewed_at = models.DateTimeField(auto_now=True)
    view_count = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'Recently Viewed'
        verbose_name_plural = 'Recently Viewed'
        unique_together = ['user', 'product']
        ordering = ['-viewed_at']
        indexes = [
            models.Index(fields=['user', '-viewed_at']),
        ]

    def __str__(self):
        return f"{self.user.username} viewed {self.product.name}"
