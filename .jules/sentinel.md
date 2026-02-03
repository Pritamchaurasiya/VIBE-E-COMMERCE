## 2024-05-22 - Razorpay Webhook Signature Bypass
**Vulnerability:** Razorpay webhooks were processed without verification if RAZORPAY_WEBHOOK_SECRET was not configured.
**Learning:** Default behavior was 'fail open' (skip verification) instead of 'fail secure' (deny request).
**Prevention:** Always ensure security checks default to 'deny' if configuration is missing.
