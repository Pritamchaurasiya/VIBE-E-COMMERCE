"""
Models for the store app containing Vendor, Category, Product, Order, and Contact definitions.
"""
from django.db import models
from django.contrib.auth.models import User

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

    def __str__(self):
        return str(self.name)

class Category(models.Model):
    """
    Category model for organizing products.
    """
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    class Meta:
        """Meta definition for Category."""
        verbose_name_plural = 'Categories'

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

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.name)

class Wishlist(models.Model):
    """
    Model for storing user wishlists.
    """
    user = models.ForeignKey(User, related_name='wishlist', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='wishlisted_by', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta definition for Wishlist."""
        unique_together = ('user', 'product')
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.user.username}'s wishlist - {self.product.name}"

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

    # Business details
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    credit_used = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    is_kyc_verified = models.BooleanField(default=False)

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

    class Meta:
        """Meta definition for Review."""
        unique_together = ('product', 'user')
        ordering = ['-created_at']

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
