"""
URL configuration for the store app.
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import api_views
from . import recommendations_api
from . import notifications_api
from . import wishlist_api
from . import search_api
from . import social_share_api
from . import review_api
from . import flash_sale_api
from . import coupon_api
from . import wishlist_price_alert_api

urlpatterns = [
    path('', views.frontpage, name='frontpage'),
    path('home/', views.frontpage, name='home'),  # Alias for frontpage
    path('shop/', views.shop, name='shop'),
    path('vendors/', views.vendor_list, name='vendor_list'),
    path('vendors/register/', views.vendor_register, name='vendor_register'),
    path('vendors/<slug:slug>/', views.vendor_detail, name='vendor_detail'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path(
        'product/<slug:category_slug>/<slug:slug>/',
        views.product_detail,
        name='product_detail'
    ),
    path('product/<int:product_id>/quick-view/', views.quick_view, name='quick_view'),


    # Cart
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('cart/update/<int:product_id>/<str:action>/', views.cart_update, name='cart_update'),
    path('cart/success/', views.success, name='success'),

    # Checkout
    path('checkout/', views.checkout, name='checkout'),
    path('api/start_order/', api_views.StartOrderView.as_view(), name='start_order'),
    path('api/apply_coupon/', views.apply_coupon, name='apply_coupon'),

    # Search API
    path('api/search/', views.search_api, name='search_api'),

    # Other
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('profile-settings/', views.profile_settings, name='profile_settings'),
    path('credit-billing/', views.credit_billing, name='credit_billing'),
    path('invoices/', views.invoices, name='invoices'),

    # Wishlist
    path('wishlist/', views.wishlist_view, name='wishlist_view'),
    path('wishlist/add/<int:product_id>/', views.wishlist_add, name='wishlist_add'),
    path('wishlist/remove/<int:product_id>/', views.wishlist_remove, name='wishlist_remove'),

    # Password Reset (using Django built-in views)
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='password_reset.html',
             email_template_name='emails/password_reset_email.html',
             subject_template_name='emails/password_reset_subject.txt',
             success_url='/password-reset/done/'
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='password_reset_confirm.html',
             success_url='/password-reset-complete/'
         ),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='password_reset_complete.html'
         ),
         name='password_reset_complete'),

    # Admin Dashboard
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Product Comparison
    path('compare/', views.product_compare, name='product_compare'),

    # Recommendations API
    path(
        'api/recommendations/<int:product_id>/',
        views.get_recommendations,
        name='get_recommendations'
    ),

    # Order Status Update API
    path(
        'api/orders/<int:order_id>/status/',
        views.update_order_status,
        name='update_order_status'
    ),

    # Vendor Dashboard
    path('vendor/dashboard/', views.vendor_dashboard, name='vendor_dashboard'),

    # Flash Sales
    path('flash-sales/', views.flash_sales, name='flash_sales'),

    # Bulk Order API
    path('api/bulk-order/', views.create_bulk_order, name='create_bulk_order'),

    # ====== ADMIN PANEL URLS ======
    # RFQ Management
    path('admin-panel/rfqs/', views.admin_rfq_list, name='admin_rfq_list'),

    # Inquiry Management
    path('admin-panel/inquiries/', views.admin_inquiry_list, name='admin_inquiry_list'),

    # Vendor Verification
    path(
        'admin-panel/vendor-verification/',
        views.admin_vendor_verification,
        name='admin_vendor_verification'
    ),
    path(
        'admin-panel/verify-vendor/<int:verification_id>/',
        views.admin_verify_vendor,
        name='admin_verify_vendor'
    ),

    # Notifications
    path(
        'admin-panel/notifications/',
        views.admin_notifications,
        name='admin_notifications'
    ),
    path(
        'api/admin/send-notification/',
        views.admin_send_notification,
        name='admin_send_notification'
    ),

    # Data Export
    path('admin-panel/export/', views.admin_export_data, name='admin_export_data'),

    # Site Settings
    path(
        'admin-panel/settings/',
        views.admin_site_settings,
        name='admin_site_settings'
    ),

    # Trade Events
    path(
        'admin-panel/events/',
        views.admin_trade_events,
        name='admin_trade_events'
    ),

    # Analytics
    path('admin-panel/analytics/', views.admin_analytics, name='admin_analytics'),

    # Bulk Order Page
    path('bulk-order/', views.bulk_order, name='bulk_order'),

    # ====== REST API URLS ======
    # Categories API
    path('api/v1/categories/', api_views.CategoryListView.as_view(), name='api_categories'),

    # Products API
    path('api/v1/products/', api_views.ProductListView.as_view(), name='api_products'),
    path(
        'api/v1/products/<slug:slug>/',
        api_views.ProductDetailView.as_view(),
        name='api_product_detail'
    ),

    # Vendors API
    path('api/v1/vendors/', api_views.VendorListView.as_view(), name='api_vendors'),
    path(
        'api/v1/vendors/<slug:slug>/',
        api_views.VendorDetailView.as_view(),
        name='api_vendor_detail'
    ),

    # Search API
    path('api/v1/search/', api_views.SearchSuggestionsView.as_view(), name='api_search'),

    # Cart API
    path('api/v1/cart/', api_views.CartView.as_view(), name='api_cart'),

    # Wishlist API
    path('api/v1/wishlist/', api_views.WishlistView.as_view(), name='api_wishlist'),
    path(
        'api/v1/wishlist/<int:product_id>/',
        api_views.WishlistView.as_view(),
        name='api_wishlist_delete'
    ),

    # Reviews API
    path(
        'api/v1/products/<slug:product_slug>/reviews/',
        api_views.ReviewListView.as_view(),
        name='api_reviews'
    ),

    # Orders API
    path('api/v1/orders/', api_views.OrderListView.as_view(), name='api_orders'),
    path('api/v1/orders/<int:pk>/', api_views.OrderDetailView.as_view(), name='api_order_detail'),

    # Coupon API
    path('api/v1/apply-coupon/', api_views.ApplyCouponView.as_view(), name='api_apply_coupon'),

    # Recommendations API
    path(
        'api/v1/recommendations/<int:product_id>/',
        api_views.RecommendationsView.as_view(),
        name='api_recommendations'
    ),

    # Authentication API
    path('api/v1/auth/login/', api_views.LoginView.as_view(), name='api_login'),
    path('api/v1/auth/logout/', api_views.LogoutView.as_view(), name='api_logout'),
    path('api/v1/auth/register/', api_views.RegisterView.as_view(), name='api_register'),

    # User Profile API
    path('api/v1/profile/', api_views.UserProfileView.as_view(), name='api_profile'),

    # ====== NEW ENHANCED API ENDPOINTS ======
    # Flash Sales API
    path('api/v1/flash-sales/', api_views.FlashSaleListView.as_view(), name='api_flash_sales'),
    path(
        'api/v1/flash-sales/<slug:slug>/',
        api_views.FlashSaleDetailView.as_view(),
        name='api_flash_sale_detail'
    ),

    # Bulk Orders API
    path('api/v1/bulk-orders/', api_views.BulkOrderView.as_view(), name='api_bulk_orders'),

    # Notifications API
    path(
        'api/v1/notifications/',
        api_views.NotificationListView.as_view(),
        name='api_notifications'
    ),

    # Deals API
    path('api/v1/deals/', api_views.DealListView.as_view(), name='api_deals'),
    path(
        'api/v1/deals/<slug:slug>/',
        api_views.DealDetailView.as_view(),
        name='api_deal_detail'
    ),

    # Inventory API (for vendors)
    path('api/v1/inventory/', api_views.InventoryView.as_view(), name='api_inventory'),

    # ====== ADVANCED POWER API ENDPOINTS ======
    # Vendor Analytics API
    path(
        'api/v1/vendor/analytics/',
        api_views.VendorAnalyticsAPIView.as_view(),
        name='api_vendor_analytics'
    ),

    # Trending Products API
    path(
        'api/v1/trending/',
        api_views.TrendingProductsView.as_view(),
        name='api_trending'
    ),

    # Recently Viewed Products API
    path(
        'api/v1/recently-viewed/',
        api_views.RecentlyViewedView.as_view(),
        name='api_recently_viewed'
    ),

    # Advanced Search API
    path(
        'api/v1/advanced-search/',
        api_views.AdvancedSearchView.as_view(),
        name='api_advanced_search'
    ),

    # Dashboard Stats API (Admin)
    path(
        'api/v1/admin/dashboard-stats/',
        api_views.DashboardStatsView.as_view(),
        name='api_dashboard_stats'
    ),

    # Bulk Inventory Update API (Vendors)
    path(
        'api/v1/inventory/bulk-update/',
        api_views.BulkInventoryUpdateView.as_view(),
        name='api_bulk_inventory_update'
    ),

    # ====== ADDITIONAL POWERFUL API ENDPOINTS ======
    # Product Comparison API
    path(
        'api/v1/compare/',
        api_views.ProductCompareView.as_view(),
        name='api_compare'
    ),

    # Export Data API (Admin)
    path(
        'api/v1/export/',
        api_views.ExportDataView.as_view(),
        name='api_export'
    ),

    # Invoice API
    path(
        'api/v1/orders/<int:order_id>/invoice/',
        api_views.InvoiceView.as_view(),
        name='api_invoice'
    ),

    # Activity Log API
    path(
        'api/v1/activity/',
        api_views.ActivityLogView.as_view(),
        name='api_activity'
    ),

    # Payment Webhook APIs
    path(
        'api/v1/webhooks/<str:provider>/',
        api_views.WebhookView.as_view(),
        name='api_webhook'
    ),

    # Health Check API
    path(
        'api/v1/health/',
        api_views.HealthCheckView.as_view(),
        name='api_health'
    ),

    # Contact Form API
    path(
        'api/v1/contact/',
        api_views.ContactFormView.as_view(),
        name='api_contact'
    ),

    # Newsletter Subscription API
    path(
        'api/v1/subscribe/',
        api_views.SubscriptionView.as_view(),
        name='api_subscribe'
    ),

    # ====== RECOMMENDATION API ENDPOINTS ======
    # Similar Products API
    path(
        'api/v1/products/<int:product_id>/similar/',
        api_views.SimilarProductsView.as_view(),
        name='api_similar_products'
    ),

    # Frequently Bought Together API
    path(
        'api/v1/products/<int:product_id>/frequently-bought-together/',
        api_views.FrequentlyBoughtTogetherView.as_view(),
        name='api_frequently_bought_together'
    ),

    # Personalized Recommendations API
    path(
        'api/v1/personalized/',
        api_views.PersonalizedRecommendationsView.as_view(),
        name='api_personalized'
    ),

    # Enhanced Trending Products API
    path(
        'api/v1/enhanced-trending/',
        api_views.EnhancedTrendingProductsView.as_view(),
        name='api_enhanced_trending'
    ),

    # Seasonal Recommendations API
    path(
        'api/v1/seasonal/',
        api_views.SeasonalRecommendationsView.as_view(),
        name='api_seasonal'
    ),

    # Cart Recommendations API
    path(
        'api/v1/cart/recommendations/',
        api_views.CartRecommendationsView.as_view(),
        name='api_cart_recommendations'
    ),

    # ====== AGRIM-STYLE API ENDPOINTS ======
    # Crops API
    path('api/v1/crops/', api_views.CropListView.as_view(), name='api_crops'),
    path(
        'api/v1/crops/<slug:crop_slug>/products/',
        api_views.ProductsByCropView.as_view(),
        name='api_products_by_crop'
    ),

    # Diseases API
    path('api/v1/diseases/', api_views.DiseaseListView.as_view(), name='api_diseases'),
    path(
        'api/v1/diseases/<slug:disease_slug>/products/',
        api_views.ProductsByDiseaseView.as_view(),
        name='api_products_by_disease'
    ),

    # Location-based API
    path(
        'api/v1/location/detect/',
        api_views.LocationDetectView.as_view(),
        name='api_location_detect'
    ),
    path(
        'api/v1/location/popular/<str:city>/',
        api_views.PopularInCityView.as_view(),
        name='api_popular_in_city'
    ),

    # Deal of the Day API
    path('api/v1/deal-of-day/', api_views.DealOfDayView.as_view(), name='api_deal_of_day'),

    # Price Alerts API
    path('api/v1/price-alerts/', api_views.PriceAlertView.as_view(), name='api_price_alerts'),

    # User Coins/Rewards API
    path('api/v1/coins/', api_views.UserCoinView.as_view(), name='api_coins'),

    # High Margin Products API
    path('api/v1/high-margin/', api_views.HighMarginProductsView.as_view(), name='api_high_margin'),

    # Newly Launched Products API
    path(
        'api/v1/newly-launched/',
        api_views.NewlyLaunchedView.as_view(),
        name='api_newly_launched'
    ),

    # ====== POSTGRESQL ANALYTICS API ENDPOINTS ======
    # PostgreSQL Analytics API (Admin only)
    path(
        'api/v1/db/analytics/',
        api_views.PostgreSQLAnalyticsView.as_view(),
        name='api_postgresql_analytics'
    ),

    # Database Dashboard API (Admin only)
    path(
        'api/v1/db/dashboard/',
        api_views.DatabaseDashboardView.as_view(),
        name='api_database_dashboard'
    ),

    # ====== PWA ENDPOINTS ======
    # Offline Page
    path('offline/', views.offline_page, name='offline'),

    # PWA Analytics API
    path(
        'api/pwa-analytics/',
        api_views.PWAAnalyticsView.as_view(),
        name='api_pwa_analytics'
    ),

    # PWA Install Status API
    path(
        'api/pwa-status/',
        api_views.PWAStatusView.as_view(),
        name='api_pwa_status'
    ),

    # PWA Analytics Dashboard (Admin)
    path(
        'admin-panel/pwa-analytics/',
        views.pwa_analytics_dashboard,
        name='pwa_analytics_dashboard'
    ),

    # User Analytics API
    path(
        'api/analytics/sessions/',
        api_views.UserSessionListView.as_view(),
        name='api_user_sessions'
    ),
    path(
        'api/analytics/sessions/<str:session_id>/',
        api_views.UserSessionDetailView.as_view(),
        name='api_user_session_detail'
    ),
    path(
        'api/analytics/interactions/',
        api_views.UserInteractionCreateView.as_view(),
        name='api_user_interaction_create'
    ),
    path(
        'api/analytics/behavior-patterns/',
        api_views.UserBehaviorPatternListView.as_view(),
        name='api_user_behavior_patterns'
    ),
    path(
        'api/analytics/preferences/',
        api_views.UserPreferenceListView.as_view(),
        name='api_user_preferences'
    ),
    path(
        'api/analytics/feedback/',
        api_views.UserFeedbackCreateView.as_view(),
        name='api_user_feedback'
    ),
    path(
        'api/analytics/segmentation/',
        api_views.UserSegmentationView.as_view(),
        name='api_user_segmentation'
    ),
    path(
        'api/analytics/summary/',
        api_views.UserAnalyticsSummaryView.as_view(),
        name='api_user_analytics_summary'
    ),
    path(
        'api/analytics/realtime/',
        api_views.RealTimeAnalyticsView.as_view(),
        name='api_realtime_analytics'
    ),
    path(
        'api/analytics/dashboard/',
        api_views.AnalyticsDashboardView.as_view(),
        name='api_analytics_dashboard'
    ),

    # ====== TRACKING SYSTEM API ENDPOINTS ======
    # Tracking Dashboard API (Admin only)
    path(
        'api/v1/tracking/dashboard/',
        api_views.TrackingDashboardAPIView.as_view(),
        name='api_tracking_dashboard'
    ),

    # Tracking Analytics API (Admin only)
    path(
        'api/v1/tracking/analytics/<str:metric_type>/',
        api_views.TrackingAnalyticsAPIView.as_view(),
        name='api_tracking_analytics'
    ),

    # Tracking Alerts API (Admin only)
    path(
        'api/v1/tracking/alerts/',
        api_views.TrackingAlertsAPIView.as_view(),
        name='api_tracking_alerts'
    ),

    # Tracking Real-time Stats API (Admin only)
    path(
        'api/v1/tracking/realtime/',
        api_views.tracking_realtime_stats,
        name='api_tracking_realtime'
    ),

    # ====== RECOMMENDATION API ENDPOINTS ======
    path(
        'api/v1/recommendations/similar/<int:product_id>/',
        recommendations_api.similar_products,
        name='api_similar_products'
    ),
    path(
        'api/v1/recommendations/bought-together/<int:product_id>/',
        recommendations_api.frequently_bought_together,
        name='api_bought_together'
    ),
    path(
        'api/v1/recommendations/personalized/',
        recommendations_api.personalized_recommendations,
        name='api_personalized_recommendations'
    ),
    path(
        'api/v1/recommendations/trending/',
        recommendations_api.trending_products,
        name='api_trending_products'
    ),
    path(
        'api/v1/recommendations/price-drops/',
        recommendations_api.price_drop_alerts,
        name='api_price_drop_alerts'
    ),
    path(
        'api/v1/recommendations/restock/',
        recommendations_api.restock_suggestions,
        name='api_restock_suggestions'
    ),
    path(
        'api/v1/recommendations/dashboard/',
        recommendations_api.recommendation_dashboard,
        name='api_recommendation_dashboard'
    ),

    # ====== SEARCH SUGGESTION API ENDPOINTS ======
    path(
        'api/v1/search/suggestions/',
        recommendations_api.search_suggestions,
        name='api_search_suggestions'
    ),
    path(
        'api/v1/search/popular/',
        recommendations_api.popular_searches,
        name='api_popular_searches'
    ),

    # ====== NOTIFICATION API ENDPOINTS ======
    path(
        'api/v1/notifications/',
        notifications_api.get_notifications,
        name='api_notifications'
    ),
    path(
        'api/v1/notifications/unread-count/',
        notifications_api.get_unread_count,
        name='api_notifications_unread_count'
    ),
    path(
        'api/v1/notifications/mark-read/',
        notifications_api.mark_as_read,
        name='api_notifications_mark_read'
    ),
    path(
        'api/v1/notifications/mark-all-read/',
        notifications_api.mark_all_read,
        name='api_notifications_mark_all_read'
    ),
    path(
        'api/v1/notifications/<int:notification_id>/delete/',
        notifications_api.delete_notification,
        name='api_notifications_delete'
    ),
    path(
        'api/v1/notifications/settings/',
        notifications_api.notification_settings,
        name='api_notifications_settings'
    ),
    path(
        'api/v1/notifications/settings/update/',
        notifications_api.update_notification_settings,
        name='api_notifications_settings_update'
    ),

    # ====== WISHLIST API ENDPOINTS ======
    path(
        'api/v2/wishlist/',
        wishlist_api.wishlist_list,
        name='api_v2_wishlist_list'
    ),
    path(
        'api/v2/wishlist/add/<int:product_id>/',
        wishlist_api.wishlist_add,
        name='api_v2_wishlist_add'
    ),
    path(
        'api/v2/wishlist/remove/<int:product_id>/',
        wishlist_api.wishlist_remove,
        name='api_v2_wishlist_remove'
    ),
    path(
        'api/v2/wishlist/check/<int:product_id>/',
        wishlist_api.wishlist_check,
        name='api_v2_wishlist_check'
    ),
    path(
        'api/v2/wishlist/price-drops/',
        wishlist_api.wishlist_price_drops,
        name='api_v2_wishlist_price_drops'
    ),
    path(
        'api/v2/wishlist/move-to-cart/<int:product_id>/',
        wishlist_api.wishlist_move_to_cart,
        name='api_v2_wishlist_move_to_cart'
    ),
    path(
        'api/v2/wishlist/clear/',
        wishlist_api.wishlist_clear,
        name='api_v2_wishlist_clear'
    ),
    path(
        'api/v2/wishlist/count/',
        wishlist_api.wishlist_count,
        name='api_v2_wishlist_count'
    ),

    # ====== SEARCH API ENDPOINTS ======
    path(
        'api/v2/search/',
        search_api.search_products,
        name='api_v2_search'
    ),
    path(
        'api/v2/search/autocomplete/',
        search_api.search_autocomplete,
        name='api_v2_search_autocomplete'
    ),
    path(
        'api/v2/search/filters/',
        search_api.search_filters,
        name='api_v2_search_filters'
    ),
    path(
        'api/v2/search/popular/',
        search_api.search_popular,
        name='api_v2_search_popular'
    ),
    path(
        'api/v2/search/recent/',
        search_api.search_recent,
        name='api_v2_search_recent'
    ),
    path(
        'api/v2/search/clear-recent/',
        search_api.search_clear_recent,
        name='api_v2_search_clear_recent'
    ),

    # ====== SOCIAL SHARE API ENDPOINTS ======
    path(
        'api/v1/social/product/<int:product_id>/',
        social_share_api.get_product_share_urls,
        name='api_social_product_share'
    ),
    path(
        'api/v1/social/track/<int:product_id>/',
        social_share_api.track_share,
        name='api_social_track_share'
    ),
    path(
        'api/v1/social/stats/<int:product_id>/',
        social_share_api.get_share_stats,
        name='api_social_share_stats'
    ),
    path(
        'api/v1/social/custom/',
        social_share_api.get_custom_share_url,
        name='api_social_custom_share'
    ),

    # ====== REVIEW API ENDPOINTS ======
    path(
        'api/v1/reviews/<int:review_id>/vote/',
        review_api.vote_review,
        name='api_review_vote'
    ),
    path(
        'api/v1/reviews/<int:review_id>/respond/',
        review_api.vendor_respond,
        name='api_review_respond'
    ),
    path(
        'api/v1/reviews/<int:review_id>/',
        review_api.get_review_details,
        name='api_review_details'
    ),
    path(
        'api/v1/products/<int:product_id>/reviews/',
        review_api.get_product_reviews,
        name='api_product_reviews'
    ),

    # ====== FLASH SALE API ENDPOINTS (Phase 2) ======
    path(
        'api/v1/flash-sales/active/',
        flash_sale_api.get_active_flash_sales,
        name='api_active_flash_sales'
    ),
    path(
        'api/v1/flash-sales/<int:sale_id>/detail/',
        flash_sale_api.get_flash_sale_detail,
        name='api_flash_sale_detail_v2'
    ),
    path(
        'api/v1/flash-sales/<int:sale_id>/countdown/',
        flash_sale_api.get_flash_sale_countdown,
        name='api_flash_sale_countdown'
    ),
    path(
        'api/v1/flash-sales/<int:sale_id>/subscribe/',
        flash_sale_api.subscribe_flash_sale,
        name='api_flash_sale_subscribe'
    ),
    path(
        'api/v1/flash-sales/<int:sale_id>/unsubscribe/',
        flash_sale_api.unsubscribe_flash_sale,
        name='api_flash_sale_unsubscribe'
    ),

    # ====== COUPON API ENDPOINTS (Phase 2) ======
    path(
        'api/v1/coupons/validate/',
        coupon_api.validate_coupon,
        name='api_coupon_validate'
    ),
    path(
        'api/v1/coupons/best/',
        coupon_api.get_best_coupon,
        name='api_coupon_best'
    ),
    path(
        'api/v1/coupons/available/',
        coupon_api.list_available_coupons,
        name='api_coupon_available'
    ),
    path(
        'api/v1/coupons/apply/',
        coupon_api.apply_coupon_to_order,
        name='api_coupon_apply'
    ),

    # ====== WISHLIST PRICE ALERT API ENDPOINTS (Phase 2) ======
    path(
        'api/v1/wishlist/<int:product_id>/price-alert/',
        wishlist_price_alert_api.set_price_alert,
        name='api_wishlist_price_alert_set'
    ),
    path(
        'api/v1/wishlist/<int:product_id>/price-alert/remove/',
        wishlist_price_alert_api.remove_price_alert,
        name='api_wishlist_price_alert_remove'
    ),
    path(
        'api/v1/wishlist/price-alerts/',
        wishlist_price_alert_api.get_price_alerts,
        name='api_wishlist_price_alerts'
    ),
    path(
        'api/v1/wishlist/price-alerts/check/',
        wishlist_price_alert_api.check_price_alerts,
        name='api_wishlist_price_alerts_check'
    ),
]



