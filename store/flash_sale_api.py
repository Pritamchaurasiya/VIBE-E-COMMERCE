"""
Flash Sale API Views for VIBE E-Commerce.

REST API endpoints for flash sales with countdown timers and notifications.
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from store.models import FlashSale


@require_http_methods(["GET"])
def get_active_flash_sales(_request):
    """
    Get all currently active flash sales with countdown.

    GET /api/v1/flash-sales/active/
    """
    now = timezone.now()

    # Get flash sales that are currently active or starting soon
    sales = FlashSale.objects.filter(  # pylint: disable=no-member
        is_active=True,
        end_time__gt=now
    ).prefetch_related('products').order_by('start_time')

    sales_data = []
    for sale in sales:
        # Calculate time remaining
        if now < sale.start_time:
            status = 'upcoming'
            time_remaining = (sale.start_time - now).total_seconds()
        elif now <= sale.end_time:
            status = 'active'
            time_remaining = (sale.end_time - now).total_seconds()
        else:
            status = 'ended'
            time_remaining = 0

        # Get products with sale prices
        products = []
        for product in sale.products.filter(is_active=True)[:10]:
            sale_price = float(product.price) * (1 - sale.discount_percentage / 100)
            products.append({
                'id': product.id,
                'name': product.name,
                'slug': product.slug,
                'original_price': str(product.price),
                'sale_price': f"{sale_price:.2f}",
                'discount': sale.discount_percentage,
                'image': product.image.url if product.image else None,
            })

        sales_data.append({
            'id': sale.id,
            'name': sale.name,
            'slug': sale.slug,
            'description': sale.description,
            'discount_percentage': sale.discount_percentage,
            'start_time': sale.start_time.isoformat(),
            'end_time': sale.end_time.isoformat(),
            'status': status,
            'time_remaining_seconds': int(time_remaining),
            'banner_image': sale.banner_image.url if sale.banner_image else None,
            'product_count': sale.products.count(),
            'products': products,
        })

    return JsonResponse({
        'success': True,
        'count': len(sales_data),
        'sales': sales_data,
    })


@require_http_methods(["GET"])
def get_flash_sale_detail(_request, sale_id):
    """
    Get detailed information about a flash sale with all products.

    GET /api/v1/flash-sales/<id>/detail/
    """
    sale = get_object_or_404(FlashSale, id=sale_id, is_active=True)
    now = timezone.now()

    # Calculate time remaining
    if now < sale.start_time:
        status = 'upcoming'
        time_remaining = (sale.start_time - now).total_seconds()
    elif now <= sale.end_time:
        status = 'active'
        time_remaining = (sale.end_time - now).total_seconds()
    else:
        status = 'ended'
        time_remaining = 0

    # Get all products with sale prices
    products = []
    for product in sale.products.filter(is_active=True):
        sale_price = float(product.price) * (1 - sale.discount_percentage / 100)
        products.append({
            'id': product.id,
            'name': product.name,
            'slug': product.slug,
            'original_price': str(product.price),
            'sale_price': f"{sale_price:.2f}",
            'discount': sale.discount_percentage,
            'image': product.image.url if product.image else None,
            'stock': product.stock_quantity,
            'in_stock': product.is_in_stock,
        })

    return JsonResponse({
        'success': True,
        'sale': {
            'id': sale.id,
            'name': sale.name,
            'slug': sale.slug,
            'description': sale.description,
            'discount_percentage': sale.discount_percentage,
            'start_time': sale.start_time.isoformat(),
            'end_time': sale.end_time.isoformat(),
            'status': status,
            'time_remaining_seconds': int(time_remaining),
            'banner_image': sale.banner_image.url if sale.banner_image else None,
        },
        'products': products,
    })


@login_required
@require_http_methods(["POST"])
def subscribe_flash_sale(request, sale_id):
    """
    Subscribe to flash sale notifications.

    POST /api/v1/flash-sales/<id>/subscribe/
    """
    sale = get_object_or_404(FlashSale, id=sale_id, is_active=True)

    # Store subscription in session or notification preferences
    subscriptions = request.session.get('flash_sale_subscriptions', [])

    if sale_id not in subscriptions:
        subscriptions.append(sale_id)
        request.session['flash_sale_subscriptions'] = subscriptions

        # Create notification for when sale starts
        try:
            # pylint: disable=import-outside-toplevel
            from store.models import Notification
            Notification.objects.get_or_create(  # pylint: disable=no-member
                user=request.user,
                notification_type='flash_sale',
                title=f'Flash Sale Reminder: {sale.name}',
                defaults={
                    'message': f'The "{sale.name}" flash sale starts at {sale.start_time.strftime("%B %d, %I:%M %p")}!',
                    'link': f'/flash-sales/{sale.slug}/',
                }
            )
        except Exception:  # pylint: disable=broad-except
            pass

        message = 'Subscribed to sale notifications'
    else:
        message = 'Already subscribed'

    return JsonResponse({
        'success': True,
        'message': message,
        'sale_id': sale_id,
    })


@login_required
@require_http_methods(["DELETE"])
def unsubscribe_flash_sale(request, sale_id):
    """
    Unsubscribe from flash sale notifications.

    DELETE /api/v1/flash-sales/<id>/unsubscribe/
    """
    subscriptions = request.session.get('flash_sale_subscriptions', [])

    if sale_id in subscriptions:
        subscriptions.remove(sale_id)
        request.session['flash_sale_subscriptions'] = subscriptions
        message = 'Unsubscribed from sale notifications'
    else:
        message = 'Not subscribed'

    return JsonResponse({
        'success': True,
        'message': message,
    })


@require_http_methods(["GET"])
def get_flash_sale_countdown(_request, sale_id):
    """
    Get countdown timer data for a flash sale (lightweight endpoint).

    GET /api/v1/flash-sales/<id>/countdown/
    """
    sale = get_object_or_404(FlashSale, id=sale_id)
    now = timezone.now()

    if now < sale.start_time:
        status = 'upcoming'
        target_time = sale.start_time
    elif now <= sale.end_time:
        status = 'active'
        target_time = sale.end_time
    else:
        status = 'ended'
        target_time = sale.end_time

    time_remaining = max(0, (target_time - now).total_seconds())

    # Calculate days, hours, minutes, seconds
    days = int(time_remaining // 86400)
    hours = int((time_remaining % 86400) // 3600)
    minutes = int((time_remaining % 3600) // 60)
    seconds = int(time_remaining % 60)

    return JsonResponse({
        'success': True,
        'sale_id': sale_id,
        'status': status,
        'time_remaining': {
            'total_seconds': int(time_remaining),
            'days': days,
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds,
            'formatted': f"{days}d {hours:02d}:{minutes:02d}:{seconds:02d}",
        },
    })
