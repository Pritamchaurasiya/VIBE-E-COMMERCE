"""
Social Share API Views for VIBE E-Commerce.

REST API endpoints for social sharing functionality.
"""
import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from store.models import Product, AnalyticsEvent
from store.social_share import (
    SocialShareService,
    ShareData,
    get_product_share_data,
    get_og_meta_tags,
)


@require_http_methods(["GET"])
def get_product_share_urls(request, product_id):
    """
    Get share URLs for a product.

    Returns URLs for Facebook, Twitter, WhatsApp, LinkedIn, Pinterest, Email.
    """
    product = get_object_or_404(Product, id=product_id, is_active=True)

    share_data = get_product_share_data(product, request)
    service = SocialShareService(share_data)

    # Track share view event
    if request.user.is_authenticated:
        AnalyticsEvent.objects.create(  # pylint: disable=no-member
            user=request.user,
            session_id=request.session.session_key or 'anonymous',
            event_type='product_view',
            data={
                'action': 'share_intent',
                'product_id': product_id,
            }
        )

    return JsonResponse({
        'success': True,
        'product': {
            'id': product.id,
            'name': product.name,
            'price': str(product.price),
        },
        'share_urls': service.get_all_share_urls(),
        'og_meta': get_og_meta_tags(share_data),
    })


@csrf_exempt
@require_http_methods(["POST"])
def track_share(request, product_id):
    """
    Track when a user shares a product.

    Body: {"platform": "facebook|twitter|whatsapp|..."}
    """
    product = get_object_or_404(Product, id=product_id, is_active=True)

    try:
        data = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        data = {}

    platform = data.get('platform', 'unknown')

    # Track share event
    AnalyticsEvent.objects.create(  # pylint: disable=no-member
        user=request.user if request.user.is_authenticated else None,
        session_id=request.session.session_key or 'anonymous',
        event_type='product_view',
        data={
            'action': 'shared',
            'product_id': product_id,
            'platform': platform,
        },
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
    )

    return JsonResponse({
        'success': True,
        'message': f'Share tracked for {product.name} on {platform}',
    })


@require_http_methods(["GET"])
def get_share_stats(request, product_id):
    """
    Get share statistics for a product (admin only).
    """
    if not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'error': 'Admin access required',
        }, status=403)

    # product = get_object_or_404(Product, id=product_id)  # Unused variable removed


    # Get share events
    share_events = AnalyticsEvent.objects.filter(  # pylint: disable=no-member
        event_type='product_view',
        data__action='shared',
        data__product_id=product_id,
    )

    # Count by platform
    platform_counts = {}
    for event in share_events:
        platform = event.data.get('platform', 'unknown')
        platform_counts[platform] = platform_counts.get(platform, 0) + 1

    return JsonResponse({
        'success': True,
        'product_id': product_id,
        'total_shares': share_events.count(),
        'by_platform': platform_counts,
    })


@require_http_methods(["GET"])
def get_custom_share_url(request):
    """
    Generate share URLs for custom content.

    Query params: url, title, description, image_url, hashtags
    """
    url = request.GET.get('url', '')
    title = request.GET.get('title', '')

    if not url or not title:
        return JsonResponse({
            'success': False,
            'error': 'url and title are required',
        }, status=400)

    share_data = ShareData(
        url=url,
        title=title,
        description=request.GET.get('description', ''),
        image_url=request.GET.get('image_url', ''),
        hashtags=request.GET.get('hashtags', ''),
    )

    service = SocialShareService(share_data)

    return JsonResponse({
        'success': True,
        'share_urls': service.get_all_share_urls(),
    })
