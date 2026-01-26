"""
Serializers for the store app REST API.
"""
# pylint: disable=no-member

from rest_framework import serializers
from django.db.models import Avg
from .models import (
    Product, Category, Vendor, Order, OrderItem, Profile, Wishlist,
    Coupon, Review, FlashSale, BulkOrder, Notification, Deal,
    InventoryLog, VendorAnalytics
)
# Analytics model imports
from .models import (
    UserSession, UserInteraction, UserBehaviorPattern, UserPreference,
    UserFeedback, UserSegment, UserSegmentMembership, UserAnalyticsReport,
    UserPredictiveModel, UserPredictiveResult, UserActivityLog, UserDataEncryption,
    UserAnalyticsDashboard, UserAnalyticsIntegration, UserAnalyticsAPIKey,
    UserAnalyticsWebhook, UserAnalyticsExport, UserAnalyticsAuditLog
)

class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""
    class Meta:
        """Meta class for CategorySerializer."""
        model = Category
        fields = ['id', 'name', 'slug']


class VendorSerializer(serializers.ModelSerializer):
    """Serializer for Vendor model."""
    class Meta:
        """Meta class for VendorSerializer."""
        model = Vendor
        fields = ['id', 'name', 'slug', 'logo', 'city']


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model."""
    category = CategorySerializer(read_only=True)
    vendor = VendorSerializer(read_only=True)
    images = serializers.SerializerMethodField()
    is_in_wishlist = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        """Meta class for ProductSerializer."""
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'short_description', 'price', 'mrp',
            'image', 'brand', 'technical_name', 'target_crops', 'usage_instructions',
            'safety_guidelines', 'stock_quantity', 'is_active', 'category', 'vendor',
            'images', 'is_in_wishlist', 'average_rating', 'review_count', 'discount_percentage',
            'bulk_price', 'bulk_min_quantity', 'is_instant_pack', 'trending_score'
        ]

    def get_images(self, obj):
        """Get product images."""
        return [{'image': img.image.url, 'alt_text': img.alt_text} for img in obj.images.all()]

    def get_is_in_wishlist(self, obj):
        """Check if product is in user's wishlist."""
        # Optimization: Use pre-fetched wishlist IDs from context if available
        wishlist_ids = self.context.get('wishlist_product_ids')
        if wishlist_ids is not None:
            return obj.id in wishlist_ids

        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Wishlist.objects.filter(user=request.user, product=obj).exists()
        return False

    def get_average_rating(self, obj):
        """Get average rating for product."""
        # Optimization: Use annotated value if available
        if hasattr(obj, 'annotated_avg_rating'):
            return obj.annotated_avg_rating or 0

        reviews = obj.reviews.all()
        if reviews:
            result = reviews.aggregate(avg_rating=Avg('rating'))
            return result['avg_rating'] or 0
        return 0

    def get_review_count(self, obj):
        """Get review count for product."""
        # Optimization: Use annotated value if available
        if hasattr(obj, 'annotated_review_count'):
            return obj.annotated_review_count

        return obj.reviews.count()


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for Review model."""
    user = serializers.StringRelatedField(read_only=True)
    is_verified_purchase = serializers.BooleanField(read_only=True)

    class Meta:
        """Meta class for ReviewSerializer."""
        model = Review
        fields = [
            'id', 'user', 'rating', 'title', 'comment', 'created_at',
            'is_verified_purchase', 'helpful_votes'
        ]
        read_only_fields = ['user', 'created_at', 'is_verified_purchase']


class WishlistSerializer(serializers.ModelSerializer):
    """Serializer for Wishlist model."""
    product = ProductSerializer(read_only=True)

    class Meta:
        """Meta class for WishlistSerializer."""
        model = Wishlist
        fields = ['id', 'product', 'added_at']


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for OrderItem model."""
    product = ProductSerializer(read_only=True)

    class Meta:
        """Meta class for OrderItemSerializer."""
        model = OrderItem
        fields = ['id', 'product', 'price', 'quantity', 'vendor']


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order model."""
    items = OrderItemSerializer(many=True, read_only=True)
    total_amount = serializers.SerializerMethodField()

    class Meta:
        """Meta class for OrderSerializer."""
        model = Order
        fields = [
            'id', 'first_name', 'last_name', 'email', 'address', 'zipcode',
            'place', 'phone', 'created_at', 'paid', 'paid_amount', 'payment_method',
            'status', 'items', 'total_amount'
        ]
        read_only_fields = ['id', 'created_at', 'paid', 'paid_amount']

    def get_total_amount(self, obj):
        """Calculate total order amount."""
        return sum(item.price * item.quantity for item in obj.items.all())


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for Profile model."""
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        """Meta class for ProfileSerializer."""
        model = Profile
        fields = [
            'user', 'shop_name', 'gst_number', 'address', 'city',
            'state', 'pincode', 'credit_limit', 'credit_used', 'is_kyc_verified'
        ]


class CouponSerializer(serializers.ModelSerializer):
    """Serializer for Coupon model."""

    class Meta:
        """Meta class for CouponSerializer."""

        model = Coupon
        fields = [
            'id', 'code', 'discount_type', 'discount_value', 'min_order_value',
            'max_uses', 'used_count', 'valid_from', 'valid_until', 'is_active', 'is_valid'
        ]


class FlashSaleSerializer(serializers.ModelSerializer):
    """Serializer for FlashSale model."""
    products = ProductSerializer(many=True, read_only=True)
    is_live = serializers.BooleanField(read_only=True)
    time_remaining = serializers.SerializerMethodField()

    class Meta:
        """Meta class for FlashSaleSerializer."""
        model = FlashSale
        fields = [
            'id', 'name', 'slug', 'description', 'discount_percentage',
            'start_time', 'end_time', 'is_active', 'banner_image',
            'products', 'is_live', 'time_remaining'
        ]

    def get_time_remaining(self, obj):
        """Get time remaining in seconds."""
        remaining = obj.time_remaining
        if remaining:
            return int(remaining.total_seconds())
        return None


class BulkOrderSerializer(serializers.ModelSerializer):
    """Serializer for BulkOrder model."""
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )
    vendor = VendorSerializer(read_only=True)
    total_value = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )

    class Meta:
        """Meta class for BulkOrderSerializer."""
        model = BulkOrder
        fields = [
            'id', 'product', 'product_id', 'vendor', 'quantity',
            'requested_price', 'approved_price', 'status', 'notes',
            'vendor_notes', 'created_at', 'updated_at', 'total_value'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'status',
            'approved_price', 'vendor_notes'
        ]


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model."""
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        """Meta class for NotificationSerializer."""
        model = Notification
        fields = [
            'id', 'notification_type', 'title', 'message', 'is_read',
            'priority', 'link', 'created_at', 'expires_at', 'is_expired'
        ]
        read_only_fields = ['id', 'created_at', 'notification_type', 'title', 'message']


class DealSerializer(serializers.ModelSerializer):
    """Serializer for Deal model."""
    products = ProductSerializer(many=True, read_only=True)
    is_valid = serializers.BooleanField(read_only=True)

    class Meta:
        """Meta class for DealSerializer."""
        model = Deal
        fields = [
            'id', 'name', 'slug', 'description', 'deal_type', 'discount_value',
            'min_purchase', 'max_discount', 'products', 'start_date', 'end_date',
            'is_active', 'banner_image', 'terms_conditions', 'is_valid'
        ]


class InventoryLogSerializer(serializers.ModelSerializer):
    """Serializer for InventoryLog model."""
    product = ProductSerializer(read_only=True)

    class Meta:
        """Meta class for InventoryLogSerializer."""
        model = InventoryLog
        fields = [
            'id', 'product', 'action', 'quantity', 'previous_stock',
            'new_stock', 'reference', 'notes', 'created_at'
        ]


class VendorAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for VendorAnalytics model."""
    vendor = VendorSerializer(read_only=True)

    class Meta:
        """Meta class for VendorAnalyticsSerializer."""
        model = VendorAnalytics
        fields = [
            'id', 'vendor', 'total_products', 'total_orders', 'total_revenue',
            'average_rating', 'total_reviews', 'total_views', 'total_inquiries',
            'conversion_rate', 'date', 'created_at'
        ]

class UserSessionSerializer(serializers.ModelSerializer):
    """Serializer for UserSession model."""
    user = serializers.StringRelatedField(read_only=True)
    interactions = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        """Meta class for UserSessionSerializer."""
        model = UserSession
        fields = [
            'id', 'user', 'session_id', 'ip_address', 'user_agent',
            'device_type', 'operating_system', 'browser', 'is_mobile',
            'is_tablet', 'is_desktop', 'screen_resolution', 'language',
            'referrer', 'landing_page', 'started_at', 'ended_at',
            'is_active', 'duration_seconds', 'page_views', 'last_activity'
        ]
        read_only_fields = ['id', 'user', 'started_at', 'last_activity']

class UserInteractionSerializer(serializers.ModelSerializer):
    """Serializer for UserInteraction model."""
    user = serializers.StringRelatedField(read_only=True)
    session = UserSessionSerializer(read_only=True)

    class Meta:
        """Meta class for UserInteractionSerializer."""
        model = UserInteraction
        fields = [
            'id', 'user', 'session', 'interaction_type', 'page_url',
            'page_title', 'element_id', 'element_class', 'element_text',
            'timestamp', 'duration_seconds', 'scroll_percentage',
            'mouse_x', 'mouse_y', 'metadata', 'is_conversion', 'conversion_value'
        ]
        read_only_fields = ['id', 'user', 'timestamp']

class UserBehaviorPatternSerializer(serializers.ModelSerializer):
    """Serializer for UserBehaviorPattern model."""
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        """Meta class for UserBehaviorPatternSerializer."""
        model = UserBehaviorPattern
        fields = [
            'id', 'user', 'pattern_type', 'pattern_data', 'confidence_score',
            'frequency', 'last_observed', 'first_observed', 'is_active'
        ]
        read_only_fields = ['id', 'user', 'last_observed', 'first_observed']

class UserPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for UserPreference model."""
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        """Meta class for UserPreferenceSerializer."""
        model = UserPreference
        fields = [
            'id', 'user', 'preference_type', 'preference_key', 'preference_value',
            'data_type', 'source', 'confidence_score', 'last_updated', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'last_updated', 'created_at']

class UserFeedbackSerializer(serializers.ModelSerializer):
    """Serializer for UserFeedback model."""
    user = serializers.StringRelatedField(read_only=True)
    session = UserSessionSerializer(read_only=True)

    class Meta:
        """Meta class for UserFeedbackSerializer."""
        model = UserFeedback
        fields = [
            'id', 'user', 'session', 'feedback_type', 'rating', 'title',
            'content', 'sentiment_score', 'sentiment_analysis', 'is_positive',
            'is_negative', 'is_neutral', 'tags', 'metadata', 'created_at',
            'updated_at', 'is_processed', 'response_status'
        ]
        read_only_fields = [
            'id', 'user', 'sentiment_score', 'sentiment_analysis',
            'is_positive', 'is_negative', 'is_neutral', 'created_at',
            'updated_at', 'is_processed'
        ]

class UserSegmentSerializer(serializers.ModelSerializer):
    """Serializer for UserSegment model."""
    members = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        """Meta class for UserSegmentSerializer."""
        model = UserSegment
        fields = [
            'id', 'name', 'description', 'criteria', 'user_count',
            'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['id', 'user_count', 'created_at', 'updated_at']

class UserSegmentMembershipSerializer(serializers.ModelSerializer):
    """Serializer for UserSegmentMembership model."""
    user = serializers.StringRelatedField(read_only=True)
    segment = UserSegmentSerializer(read_only=True)

    class Meta:
        """Meta class for UserSegmentMembershipSerializer."""
        model = UserSegmentMembership
        fields = [
            'id', 'user', 'segment', 'joined_at', 'last_updated', 'membership_score'
        ]
        read_only_fields = ['id', 'joined_at', 'last_updated']

class UserAnalyticsReportSerializer(serializers.ModelSerializer):
    """Serializer for UserAnalyticsReport model."""
    generated_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        """Meta class for UserAnalyticsReportSerializer."""
        model = UserAnalyticsReport
        fields = [
            'id', 'title', 'report_type', 'description', 'criteria',
            'data', 'file', 'format', 'generated_by', 'generated_at',
            'start_date', 'end_date', 'is_scheduled', 'schedule_frequency',
            'next_run'
        ]
        read_only_fields = [
            'id', 'generated_by', 'generated_at'
        ]

class UserPredictiveModelSerializer(serializers.ModelSerializer):
    """Serializer for UserPredictiveModel model."""
    results = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        """Meta class for UserPredictiveModelSerializer."""
        model = UserPredictiveModel
        fields = [
            'id', 'name', 'model_type', 'description', 'model_data',
            'training_data', 'evaluation_metrics', 'created_at',
            'updated_at', 'is_active', 'version'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class UserPredictiveResultSerializer(serializers.ModelSerializer):
    """Serializer for UserPredictiveResult model."""
    user = serializers.StringRelatedField(read_only=True)
    model = UserPredictiveModelSerializer(read_only=True)

    class Meta:
        """Meta class for UserPredictiveResultSerializer."""
        model = UserPredictiveResult
        fields = [
            'id', 'user', 'model', 'prediction_score', 'prediction_class',
            'confidence', 'prediction_data', 'created_at', 'expires_at'
        ]
        read_only_fields = ['id', 'created_at']

class UserActivityLogSerializer(serializers.ModelSerializer):
    """Serializer for UserActivityLog model."""
    user = serializers.StringRelatedField(read_only=True)
    session = UserSessionSerializer(read_only=True)

    class Meta:
        """Meta class for UserActivityLogSerializer."""
        model = UserActivityLog
        fields = [
            'id', 'user', 'session', 'activity_type', 'activity_data',
            'ip_address', 'user_agent', 'timestamp', 'is_sensitive'
        ]
        read_only_fields = ['id', 'timestamp']

class UserDataEncryptionSerializer(serializers.ModelSerializer):
    """Serializer for UserDataEncryption model."""
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        """Meta class for UserDataEncryptionSerializer."""
        model = UserDataEncryption
        fields = [
            'id', 'user', 'data_type', 'encryption_method',
            'encryption_key', 'is_encrypted', 'encrypted_at',
            'last_decrypted'
        ]
        read_only_fields = ['id', 'encrypted_at', 'last_decrypted']

class UserAnalyticsDashboardSerializer(serializers.ModelSerializer):
    """Serializer for UserAnalyticsDashboard model."""
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        """Meta class for UserAnalyticsDashboardSerializer."""
        model = UserAnalyticsDashboard
        fields = [
            'id', 'user', 'dashboard_name', 'configuration',
            'is_default', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class UserAnalyticsIntegrationSerializer(serializers.ModelSerializer):
    """Serializer for UserAnalyticsIntegration model."""

    class Meta:
        """Meta class for UserAnalyticsIntegrationSerializer."""
        model = UserAnalyticsIntegration
        fields = [
            'id', 'integration_type', 'configuration', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class UserAnalyticsAPIKeySerializer(serializers.ModelSerializer):
    """Serializer for UserAnalyticsAPIKey model."""

    class Meta:
        """Meta class for UserAnalyticsAPIKeySerializer."""
        model = UserAnalyticsAPIKey
        fields = [
            'id', 'name', 'api_key', 'secret_key', 'permissions',
            'is_active', 'created_at', 'expires_at', 'last_used',
            'usage_count'
        ]
        read_only_fields = [
            'id', 'created_at', 'last_used', 'usage_count'
        ]

class UserAnalyticsWebhookSerializer(serializers.ModelSerializer):
    """Serializer for UserAnalyticsWebhook model."""

    class Meta:
        """Meta class for UserAnalyticsWebhookSerializer."""
        model = UserAnalyticsWebhook
        fields = [
            'id', 'name', 'url', 'events', 'secret', 'is_active',
            'created_at', 'updated_at', 'last_triggered', 'failure_count'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'last_triggered', 'failure_count'
        ]

class UserAnalyticsExportSerializer(serializers.ModelSerializer):
    """Serializer for UserAnalyticsExport model."""
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        """Meta class for UserAnalyticsExportSerializer."""
        model = UserAnalyticsExport
        fields = [
            'id', 'user', 'export_type', 'criteria', 'file', 'format',
            'record_count', 'status', 'created_at', 'completed_at', 'expires_at'
        ]
        read_only_fields = [
            'id', 'user', 'created_at', 'completed_at', 'record_count'
        ]

class UserAnalyticsAuditLogSerializer(serializers.ModelSerializer):
    """Serializer for UserAnalyticsAuditLog model."""
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        """Meta class for UserAnalyticsAuditLogSerializer."""
        model = UserAnalyticsAuditLog
        fields = [
            'id', 'user', 'audit_type', 'description', 'metadata',
            'ip_address', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']

READ_ONLY_ERROR_MSG = "This serializer is read-only."

# ============================================
# ANALYTICS AGGREGATION SERIALIZERS
# ============================================

class UserAnalyticsSummarySerializer(serializers.Serializer):
    """Serializer for user analytics summary."""
    total_sessions = serializers.IntegerField()
    total_interactions = serializers.IntegerField()
    total_page_views = serializers.IntegerField()
    average_session_duration = serializers.DecimalField(max_digits=10, decimal_places=2)
    conversion_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    top_interactions = serializers.ListField()
    behavior_patterns = serializers.ListField()
    preferred_categories = serializers.ListField()
    purchase_history = serializers.ListField()
    engagement_score = serializers.DecimalField(max_digits=5, decimal_places=2)
    loyalty_score = serializers.DecimalField(max_digits=5, decimal_places=2)
    predicted_churn_risk = serializers.DecimalField(max_digits=5, decimal_places=2)
    lifetime_value = serializers.DecimalField(max_digits=10, decimal_places=2)

    def create(self, validated_data):
        raise NotImplementedError(READ_ONLY_ERROR_MSG)

    def update(self, instance, validated_data):
        raise NotImplementedError(READ_ONLY_ERROR_MSG)

class RealTimeAnalyticsSerializer(serializers.Serializer):
    """Serializer for real-time analytics data."""
    active_users = serializers.IntegerField()
    current_sessions = serializers.IntegerField()
    page_views_last_hour = serializers.IntegerField()
    conversions_last_hour = serializers.IntegerField()
    top_pages = serializers.ListField()
    active_devices = serializers.DictField()
    traffic_sources = serializers.DictField()
    recent_events = serializers.ListField()

    def create(self, validated_data):
        raise NotImplementedError(READ_ONLY_ERROR_MSG)

    def update(self, instance, validated_data):
        raise NotImplementedError(READ_ONLY_ERROR_MSG)

class AnalyticsDashboardSerializer(serializers.Serializer):
    """Serializer for analytics dashboard data."""
    summary = UserAnalyticsSummarySerializer()
    real_time = RealTimeAnalyticsSerializer()
    charts = serializers.DictField()
    recent_activities = serializers.ListField()
    alerts = serializers.ListField()
    recommendations = serializers.ListField()

    def create(self, validated_data):
        raise NotImplementedError(READ_ONLY_ERROR_MSG)

    def update(self, instance, validated_data):
        raise NotImplementedError(READ_ONLY_ERROR_MSG)

class WishlistPriceAlertSerializer(serializers.ModelSerializer):
    """Serializer for updating wishlist price alerts."""
    target_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, allow_null=True
    )
    notify_on_sale = serializers.BooleanField(required=False)
    notify_on_restock = serializers.BooleanField(required=False)

    class Meta:
        """Meta class for WishlistPriceAlertSerializer."""
        model = Wishlist
        fields = ['target_price', 'notify_on_sale', 'notify_on_restock']

    def validate_target_price(self, value):
        """
        Validate that the target price is a positive number.
        """
        if value is not None and value <= 0:
            raise serializers.ValidationError("Target price must be a positive number.")
        return value
