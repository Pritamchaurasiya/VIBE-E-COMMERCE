"""
Email Service for VIBE E-Commerce
Handles all email communications including order confirmations,
password resets, notifications, and marketing emails.
"""
import logging
from typing import Dict, List, Optional
from enum import Enum

from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


class EmailType(Enum):
    """Types of emails."""
    ORDER_CONFIRMATION = 'order_confirmation'
    ORDER_SHIPPED = 'order_shipped'
    ORDER_DELIVERED = 'order_delivered'
    ORDER_CANCELLED = 'order_cancelled'
    PASSWORD_RESET = 'password_reset'
    WELCOME = 'welcome'
    VENDOR_WELCOME = 'vendor_welcome'
    PRICE_DROP = 'price_drop'
    FLASH_SALE = 'flash_sale'
    NEWSLETTER = 'newsletter'
    REVIEW_REQUEST = 'review_request'
    ACCOUNT_VERIFICATION = 'account_verification'


class EmailService:
    """
    Service for sending emails.
    """

    DEFAULT_FROM_EMAIL = getattr(
        settings, 'DEFAULT_FROM_EMAIL', 'noreply@vibecommerce.com'
    )

    EMAIL_TEMPLATES = {
        EmailType.ORDER_CONFIRMATION: 'emails/order_confirmation.html',
        EmailType.ORDER_SHIPPED: 'emails/order_shipped.html',
        EmailType.ORDER_DELIVERED: 'emails/order_delivered.html',
        EmailType.ORDER_CANCELLED: 'emails/order_cancelled.html',
        EmailType.PASSWORD_RESET: 'emails/password_reset.html',
        EmailType.WELCOME: 'emails/welcome.html',
        EmailType.VENDOR_WELCOME: 'emails/vendor_welcome.html',
        EmailType.PRICE_DROP: 'emails/price_drop.html',
        EmailType.FLASH_SALE: 'emails/flash_sale.html',
        EmailType.NEWSLETTER: 'emails/newsletter.html',
        EmailType.REVIEW_REQUEST: 'emails/review_request.html',
        EmailType.ACCOUNT_VERIFICATION: 'emails/account_verification.html',
    }

    def __init__(self):
        self.from_email = self.DEFAULT_FROM_EMAIL

    def send_email(
        self,
        to_email: str,
        subject: str,
        template_name: str,
        context: Optional[Dict] = None,
        from_email: Optional[str] = None,
    ) -> bool:
        """
        Send an email using a template.

        Args:
            to_email: Recipient email address
            subject: Email subject
            template_name: Path to the email template
            context: Context data for the template
            from_email: Sender email (optional)

        Returns:
            True if email was sent successfully
        """
        try:
            ctx = context or {}
            ctx['site_name'] = 'VIBE E-Commerce'
            ctx['site_url'] = getattr(settings, 'SITE_URL', 'http://localhost:8000')

            # Try to render HTML template
            try:
                html_content = render_to_string(template_name, ctx)
                text_content = strip_tags(html_content)
            except Exception:
                # If template doesn't exist, use plain text
                html_content = None
                text_content = ctx.get('message', '')

            if html_content:
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=from_email or self.from_email,
                    to=[to_email],
                )
                email.attach_alternative(html_content, 'text/html')
                email.send()
            else:
                send_mail(
                    subject=subject,
                    message=text_content,
                    from_email=from_email or self.from_email,
                    recipient_list=[to_email],
                )

            logger.info("Email sent to %s: %s", to_email, subject)
            return True

        except Exception as e:
            logger.error("Failed to send email to %s: %s", to_email, e)
            return False

    def send_bulk_email(
        self,
        recipients: List[str],
        subject: str,
        template_name: str,
        context: Optional[Dict] = None,
    ) -> int:
        """
        Send bulk emails.

        Args:
            recipients: List of email addresses
            subject: Email subject
            template_name: Path to email template
            context: Context data for template

        Returns:
            Number of successfully sent emails
        """
        success_count = 0
        for email in recipients:
            if self.send_email(email, subject, template_name, context):
                success_count += 1
        return success_count


class OrderEmailHelper:
    """
    Helper class for sending order-related emails.
    """

    def __init__(self):
        self.service = EmailService()

    def send_order_confirmation(self, order) -> bool:
        """Send order confirmation email."""
        context = {
            'order': order,
            'order_number': order.order_number,
            'items': order.items.all() if hasattr(order, 'items') else [],
            'total': order.paid_amount,
            'shipping_address': self._format_address(order),
        }

        return self.service.send_email(
            to_email=order.user.email,
            subject=f'Order Confirmation - #{order.order_number}',
            template_name=EmailService.EMAIL_TEMPLATES[EmailType.ORDER_CONFIRMATION],
            context=context,
        )

    def send_order_shipped(self, order, tracking_number: str = '') -> bool:
        """Send order shipped notification."""
        context = {
            'order': order,
            'order_number': order.order_number,
            'tracking_number': tracking_number,
        }

        return self.service.send_email(
            to_email=order.user.email,
            subject=f'Your Order #{order.order_number} Has Shipped!',
            template_name=EmailService.EMAIL_TEMPLATES[EmailType.ORDER_SHIPPED],
            context=context,
        )

    def send_order_delivered(self, order) -> bool:
        """Send order delivered notification."""
        context = {
            'order': order,
            'order_number': order.order_number,
        }

        return self.service.send_email(
            to_email=order.user.email,
            subject=f'Your Order #{order.order_number} Has Been Delivered!',
            template_name=EmailService.EMAIL_TEMPLATES[EmailType.ORDER_DELIVERED],
            context=context,
        )

    def send_order_cancelled(self, order, reason: str = '') -> bool:
        """Send order cancellation notification."""
        context = {
            'order': order,
            'order_number': order.order_number,
            'reason': reason,
        }

        return self.service.send_email(
            to_email=order.user.email,
            subject=f'Order #{order.order_number} Has Been Cancelled',
            template_name=EmailService.EMAIL_TEMPLATES[EmailType.ORDER_CANCELLED],
            context=context,
        )

    def _format_address(self, order) -> str:
        """Format shipping address as string."""
        parts = [
            getattr(order, 'shipping_name', ''),
            getattr(order, 'shipping_address', ''),
            getattr(order, 'shipping_city', ''),
            getattr(order, 'shipping_state', ''),
            getattr(order, 'shipping_pincode', ''),
        ]
        return ', '.join(p for p in parts if p)


class UserEmailHelper:
    """
    Helper class for sending user-related emails.
    """

    def __init__(self):
        self.service = EmailService()

    def send_welcome_email(self, user: User) -> bool:
        """Send welcome email to new user."""
        context = {
            'user': user,
            'username': user.username,
            'first_name': user.first_name or user.username,
        }

        return self.service.send_email(
            to_email=user.email,
            subject='Welcome to VIBE E-Commerce!',
            template_name=EmailService.EMAIL_TEMPLATES[EmailType.WELCOME],
            context=context,
        )

    def send_password_reset(self, user: User, reset_link: str) -> bool:
        """Send password reset email."""
        context = {
            'user': user,
            'reset_link': reset_link,
            'username': user.username,
        }

        return self.service.send_email(
            to_email=user.email,
            subject='Password Reset Request',
            template_name=EmailService.EMAIL_TEMPLATES[EmailType.PASSWORD_RESET],
            context=context,
        )

    def send_verification_email(self, user: User, verification_link: str) -> bool:
        """Send account verification email."""
        context = {
            'user': user,
            'verification_link': verification_link,
            'username': user.username,
        }

        return self.service.send_email(
            to_email=user.email,
            subject='Verify Your Email Address',
            template_name=EmailService.EMAIL_TEMPLATES[EmailType.ACCOUNT_VERIFICATION],
            context=context,
        )

    def send_review_request(self, user: User, order) -> bool:
        """Send review request email after delivery."""
        context = {
            'user': user,
            'order': order,
            'order_number': order.order_number,
        }

        return self.service.send_email(
            to_email=user.email,
            subject='How was your order? Leave a review!',
            template_name=EmailService.EMAIL_TEMPLATES[EmailType.REVIEW_REQUEST],
            context=context,
        )


class PromotionalEmailHelper:
    """
    Helper class for sending promotional emails.
    """

    def __init__(self):
        self.service = EmailService()

    def send_price_drop_alert(self, user: User, product, old_price, new_price) -> bool:
        """Send price drop alert for wishlist item."""
        savings = old_price - new_price
        context = {
            'user': user,
            'product': product,
            'old_price': old_price,
            'new_price': new_price,
            'savings': savings,
        }

        return self.service.send_email(
            to_email=user.email,
            subject=f'Price Drop Alert: {product.name}',
            template_name=EmailService.EMAIL_TEMPLATES[EmailType.PRICE_DROP],
            context=context,
        )

    def send_flash_sale_notification(self, user: User, flash_sale) -> bool:
        """Send flash sale notification."""
        context = {
            'user': user,
            'flash_sale': flash_sale,
            'discount': flash_sale.discount_percentage,
        }

        return self.service.send_email(
            to_email=user.email,
            subject=f'Flash Sale: Up to {flash_sale.discount_percentage}% Off!',
            template_name=EmailService.EMAIL_TEMPLATES[EmailType.FLASH_SALE],
            context=context,
        )

    def send_newsletter(
        self,
        recipients: List[str],
        subject: str,
        content: str
    ) -> int:
        """Send newsletter to multiple recipients."""
        context = {'content': content}

        return self.service.send_bulk_email(
            recipients=recipients,
            subject=subject,
            template_name=EmailService.EMAIL_TEMPLATES[EmailType.NEWSLETTER],
            context=context,
        )
