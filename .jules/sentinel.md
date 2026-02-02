## 2026-02-02 - Missing Secret Validation in Webhooks
**Vulnerability:** Found a payment webhook handler that bypassed signature verification when the secret key was not configured (empty or None).
**Learning:** Checking `if secret:` is insufficient if the code following it assumes verification happened. The absence of a secret should be a hard failure mode for security-critical endpoints.
**Prevention:** Enforce critical configuration variables at startup or raise 500 errors if missing during runtime. Always fail securely (default deny).
