"""
URL configuration for the store app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.frontpage, name='frontpage'),
    path('shop/', views.shop, name='shop'),
    path('vendors/', views.vendor_list, name='vendor_list'),
    path('vendors/register/', views.vendor_register, name='vendor_register'),
    path('vendors/<slug:slug>/', views.vendor_detail, name='vendor_detail'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    # Cart
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('cart/update/<int:product_id>/<str:action>/', views.cart_update, name='cart_update'),
    path('cart/success/', views.success, name='success'),

    # Checkout
    path('checkout/', views.checkout, name='checkout'),
    path('api/start_order/', views.start_order, name='start_order'),

    # Other
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),

    # Wishlist
    path('wishlist/', views.wishlist_view, name='wishlist_view'),
    path('wishlist/add/<int:product_id>/', views.wishlist_add, name='wishlist_add'),
    path('wishlist/remove/<int:product_id>/', views.wishlist_remove, name='wishlist_remove'),
]
