"""
Social Share Service for VIBE E-Commerce.

Provides utilities for social media sharing of products and pages.
Includes Open Graph meta tag generation and share URL builders.
"""
import urllib.parse
from typing import Dict

from dataclasses import dataclass

from django.conf import settings


@dataclass
class ShareData:
    """Data structure for shareable content."""
    url: str
    title: str
    description: str = ""
    image_url: str = ""
    hashtags: str = ""


class SocialShareService:
    """
    Service for generating social media share URLs.

    Supports: Facebook, Twitter/X, WhatsApp, LinkedIn, Pinterest, Email
    """

    BASE_URLS = {
        'facebook': 'https://www.facebook.com/sharer/sharer.php',
        'twitter': 'https://twitter.com/intent/tweet',
        'whatsapp': 'https://api.whatsapp.com/send',
        'linkedin': 'https://www.linkedin.com/sharing/share-offsite/',
        'pinterest': 'https://pinterest.com/pin/create/button/',
        'email': 'mailto:',
    }

    def __init__(self, share_data: ShareData):
        """Initialize with share data."""
        self.data = share_data

    def get_facebook_url(self) -> str:
        """Generate Facebook share URL."""
        params = {
            'u': self.data.url,
            'quote': self.data.title,
        }
        return f"{self.BASE_URLS['facebook']}?{urllib.parse.urlencode(params)}"

    def get_twitter_url(self) -> str:
        """Generate Twitter/X share URL."""
        text = self.data.title
        if self.data.description:
            text = f"{text} - {self.data.description[:100]}"

        params = {
            'url': self.data.url,
            'text': text,
        }
        if self.data.hashtags:
            params['hashtags'] = self.data.hashtags

        return f"{self.BASE_URLS['twitter']}?{urllib.parse.urlencode(params)}"

    def get_whatsapp_url(self) -> str:
        """Generate WhatsApp share URL."""
        text = f"{self.data.title}\n{self.data.url}"
        params = {'text': text}
        return f"{self.BASE_URLS['whatsapp']}?{urllib.parse.urlencode(params)}"

    def get_linkedin_url(self) -> str:
        """Generate LinkedIn share URL."""
        params = {'url': self.data.url}
        return f"{self.BASE_URLS['linkedin']}?{urllib.parse.urlencode(params)}"

    def get_pinterest_url(self) -> str:
        """Generate Pinterest share URL."""
        params = {
            'url': self.data.url,
            'description': self.data.title,
        }
        if self.data.image_url:
            params['media'] = self.data.image_url
        return f"{self.BASE_URLS['pinterest']}?{urllib.parse.urlencode(params)}"

    def get_email_url(self) -> str:
        """Generate Email share URL."""
        subject = urllib.parse.quote(self.data.title)
        body = urllib.parse.quote(f"{self.data.description}\n\n{self.data.url}")
        return f"{self.BASE_URLS['email']}?subject={subject}&body={body}"

    def get_copy_url(self) -> str:
        """Get URL for copy-to-clipboard."""
        return self.data.url

    def get_all_share_urls(self) -> Dict[str, str]:
        """Get all share URLs as dictionary."""
        return {
            'facebook': self.get_facebook_url(),
            'twitter': self.get_twitter_url(),
            'whatsapp': self.get_whatsapp_url(),
            'linkedin': self.get_linkedin_url(),
            'pinterest': self.get_pinterest_url(),
            'email': self.get_email_url(),
            'copy': self.get_copy_url(),
        }


def get_product_share_data(product, request=None) -> ShareData:
    """
    Create ShareData for a product.

    Args:
        product: Product instance
        request: HTTP request for building absolute URL

    Returns:
        ShareData instance
    """
    # Build absolute URL
    if request:
        base_url = request.build_absolute_uri('/')[:-1]
    else:
        base_url = getattr(settings, 'SITE_URL', 'https://example.com')

    product_url = f"{base_url}/products/{product.slug}/"

    # Get product image
    image_url = ""
    if hasattr(product, 'image') and product.image:
        image_url = f"{base_url}{product.image.url}"
    elif hasattr(product, 'images') and product.images.exists():
        first_image = product.images.first()
        if first_image and first_image.image:
            image_url = f"{base_url}{first_image.image.url}"

    # Create share data
    description = ""
    if hasattr(product, 'description') and product.description:
        description = product.description[:200]

    return ShareData(
        url=product_url,
        title=f"{product.name} - ₹{product.price}",
        description=description,
        image_url=image_url,
        hashtags="shopping,ecommerce",
    )


def get_og_meta_tags(share_data: ShareData) -> Dict[str, str]:
    """
    Generate Open Graph meta tags for SEO and social sharing.

    Args:
        share_data: ShareData instance

    Returns:
        Dictionary of meta tag names to values
    """
    return {
        'og:type': 'product',
        'og:url': share_data.url,
        'og:title': share_data.title,
        'og:description': share_data.description,
        'og:image': share_data.image_url,
        'twitter:card': 'summary_large_image',
        'twitter:title': share_data.title,
        'twitter:description': share_data.description,
        'twitter:image': share_data.image_url,
    }
