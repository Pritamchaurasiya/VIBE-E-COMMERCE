from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from store.models import OTPVerification
import random
import logging

logger = logging.getLogger(__name__)

def generate_otp(length=6):
    """Generate a random OTP of given length."""
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

def send_otp(phone, otp, purpose='login'):
    """Send OTP to the given phone number."""
    # In a real application, you would use an SMS gateway here.
    # For now, we will log it and also send via email if available for dev.

    logger.info(f"OTP for {phone} ({purpose}): {otp}")

    # If phone is actually an email (for testing purposes often interchangeable in early stage)
    if '@' in phone:
        send_mail(
            f'Your OTP for {purpose}',
            f'Your OTP is {otp}. It is valid for 10 minutes.',
            settings.DEFAULT_FROM_EMAIL,
            [phone],
            fail_silently=True,
        )

def verify_otp(phone, otp, purpose='login'):
    """Verify the provided OTP."""
    try:
        otp_record = OTPVerification.objects.filter(
            phone=phone,
            purpose=purpose,
            is_verified=False
        ).latest('created_at')

        if otp_record.is_expired:
            return False, "OTP expired"

        if otp_record.attempts >= 5:
            return False, "Too many failed attempts"

        if otp_record.otp == otp:
            otp_record.is_verified = True
            otp_record.save()
            return True, "Verified"
        else:
            otp_record.attempts += 1
            otp_record.save()
            return False, "Invalid OTP"

    except OTPVerification.DoesNotExist:
        return False, "No OTP found"
