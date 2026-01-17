## 2025-05-23 - Missing Webhook Secret Validation
**Vulnerability:** The Razorpay webhook endpoint allowed bypassing signature verification when `RAZORPAY_WEBHOOK_SECRET` was not configured in settings.
**Learning:** Default configuration values (empty strings) can lead to "fail open" security checks if not explicitly handled.
**Prevention:** Always enforce "fail closed" logic. Check for the existence of secrets/keys before proceeding with sensitive operations.
