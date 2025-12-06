"""
Admin configuration for the store app.
"""
from django.contrib import admin
from .models import Category, Vendor, Product, Order, OrderItem, Contact

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'created_by']
    search_fields = ['name', 'city']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'vendor', 'category', 'created_at']
    list_filter = ['vendor', 'category']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email', 'created_at', 'paid', 'paid_amount']
    list_filter = ['paid', 'created_at']
    search_fields = ['first_name', 'address', 'email']
    inlines = [OrderItemInline]

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'created_at']
    search_fields = ['name', 'email']
