## 2025-02-19 - Django Test Environment & Redis
**Learning:** `config/settings.py` configured Redis unconditionally if the package was installed, causing tests to fail in environments without Redis. Also, `DEFAULT_PERMISSION_CLASSES = [IsAuthenticated]` caused regression in public API endpoints that didn't explicitly set `permission_classes = [AllowAny]`.
**Action:** Use a dedicated `test_settings.py` that mocks cache/session to LocMem/DB and ensures public views explicitly declare permissions.
