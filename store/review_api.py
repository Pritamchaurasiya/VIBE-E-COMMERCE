"""
Review API Views for VIBE E-Commerce.

REST API endpoints for review voting, vendor responses, and moderation.
"""
import json
from django.db import models  # For annotations
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from store.models import Review, Product


@login_required
@require_http_methods(["POST"])
def vote_review(request, review_id):
    """
    Vote a review as helpful.

    POST /api/reviews/{review_id}/vote/
    Body: {"action": "add|remove"}
    """
    review = get_object_or_404(Review, id=review_id, is_moderated=True)

    try:
        data = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        data = {}

    action = data.get('action', 'add')

    # Can't vote on your own review
    if review.user == request.user:
        return JsonResponse({
            'success': False,
            'error': 'You cannot vote on your own review',
        }, status=400)

    if action == 'add':
        review.helpful_votes.add(request.user)
        message = 'Vote added'
    elif action == 'remove':
        review.helpful_votes.remove(request.user)
        message = 'Vote removed'
    else:
        return JsonResponse({
            'success': False,
            'error': 'Invalid action. Use "add" or "remove"',
        }, status=400)

    return JsonResponse({
        'success': True,
        'message': message,
        'helpful_count': review.helpful_count,
        'user_voted': review.helpful_votes.filter(id=request.user.id).exists(),
    })


@login_required
@require_http_methods(["POST"])
def vendor_respond(request, review_id):
    """
    Vendor responds to a review.

    POST /api/reviews/{review_id}/respond/
    Body: {"response": "Thank you for your feedback..."}
    """
    review = get_object_or_404(Review, id=review_id)

    # Check if user is the vendor of the product
    product = review.product
    if not hasattr(product, 'vendor') or not product.vendor:
        return JsonResponse({
            'success': False,
            'error': 'Product has no vendor',
        }, status=400)

    # Check vendor ownership
    vendor = product.vendor
    is_vendor_owner = (
        hasattr(vendor, 'created_by') and vendor.created_by == request.user
    ) or request.user.is_staff

    if not is_vendor_owner:
        return JsonResponse({
            'success': False,
            'error': 'Only the product vendor can respond to reviews',
        }, status=403)

    try:
        data = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON',
        }, status=400)

    response_text = data.get('response', '').strip()

    if not response_text:
        return JsonResponse({
            'success': False,
            'error': 'Response text is required',
        }, status=400)

    if len(response_text) > 2000:
        return JsonResponse({
            'success': False,
            'error': 'Response too long (max 2000 characters)',
        }, status=400)

    review.vendor_response = response_text
    review.vendor_response_at = timezone.now()
    review.save(update_fields=['vendor_response', 'vendor_response_at'])

    return JsonResponse({
        'success': True,
        'message': 'Response added successfully',
        'vendor_response': review.vendor_response,
        'vendor_response_at': review.vendor_response_at.isoformat(),
    })


@require_http_methods(["GET"])
def get_review_details(request, review_id):
    """
    Get detailed information about a review.

    GET /api/reviews/{review_id}/
    """
    review = get_object_or_404(Review, id=review_id, is_moderated=True)

    # Check if current user voted
    user_voted = False
    if request.user.is_authenticated:
        user_voted = review.helpful_votes.filter(id=request.user.id).exists()

    return JsonResponse({
        'success': True,
        'review': {
            'id': review.id,
            'product_id': review.product_id,
            'product_name': review.product.name,
            'user': review.user.username,
            'rating': review.rating,
            'title': review.title,
            'comment': review.comment,
            'created_at': review.created_at.isoformat(),
            'is_verified_purchase': review.is_verified_purchase,
            'helpful_count': review.helpful_count,
            'user_voted': user_voted,
            'vendor_response': review.vendor_response,
            'vendor_response_at': (
                review.vendor_response_at.isoformat()
                if review.vendor_response_at else None
            ),
        },
    })


@require_http_methods(["GET"])
def get_product_reviews(request, product_id):
    """
    Get all reviews for a product with pagination.

    GET /api/products/{product_id}/reviews/?page=1&sort=recent
    """
    product = get_object_or_404(Product, id=product_id, is_active=True)

    # Get query parameters
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))
    sort = request.GET.get('sort', 'recent')
    rating_filter = request.GET.get('rating')

    # Base queryset
    reviews = Review.objects.filter(  # pylint: disable=no-member
        product=product,
        is_moderated=True
    ).select_related('user')

    # Apply rating filter
    if rating_filter:
        try:
            reviews = reviews.filter(rating=int(rating_filter))
        except ValueError:
            pass

    # Apply sorting
    if sort == 'recent':
        reviews = reviews.order_by('-created_at')
    elif sort == 'oldest':
        reviews = reviews.order_by('created_at')
    elif sort == 'highest':
        reviews = reviews.order_by('-rating', '-created_at')
    elif sort == 'lowest':
        reviews = reviews.order_by('rating', '-created_at')
    elif sort == 'helpful':
        reviews = reviews.annotate(
            vote_count=models.Count('helpful_votes')
        ).order_by('-vote_count', '-created_at')
    else:
        reviews = reviews.order_by('-created_at')

    # Pagination
    total_count = reviews.count()
    start = (page - 1) * per_page
    end = start + per_page
    reviews = reviews[start:end]

    # Format response
    review_list = []
    for review in reviews:
        user_voted = False
        if request.user.is_authenticated:
            user_voted = review.helpful_votes.filter(id=request.user.id).exists()

        review_list.append({
            'id': review.id,
            'user': review.user.username,
            'rating': review.rating,
            'title': review.title,
            'comment': review.comment,
            'created_at': review.created_at.isoformat(),
            'is_verified_purchase': review.is_verified_purchase,
            'helpful_count': review.helpful_count,
            'user_voted': user_voted,
            'vendor_response': review.vendor_response,
            'vendor_response_at': (
                review.vendor_response_at.isoformat()
                if review.vendor_response_at else None
            ),
        })

    # Rating distribution
    all_reviews = Review.objects.filter(  # pylint: disable=no-member
        product=product, is_moderated=True
    )
    rating_distribution = {}
    for i in range(1, 6):
        rating_distribution[str(i)] = all_reviews.filter(rating=i).count()

    avg_rating = all_reviews.aggregate(
        avg=models.Avg('rating')
    )['avg'] or 0

    return JsonResponse({
        'success': True,
        'product_id': product_id,
        'total_count': total_count,
        'page': page,
        'per_page': per_page,
        'total_pages': (total_count + per_page - 1) // per_page,
        'average_rating': round(avg_rating, 1),
        'rating_distribution': rating_distribution,
        'reviews': review_list,
    })
