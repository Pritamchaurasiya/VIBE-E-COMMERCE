## 2025-02-20 - Environment & Dependency Hell
**Learning:** The codebase has critical configuration drifts:
1. `requirements.txt` requests `Django>=6.0` which causes conflict hell. Downgraded to `Django>=5.0,<6.0`.
2. `store/tracking_service.py` imports non-existent `tracking_models` module; models are actually in `store/models.py`.
3. Default permissions are strict (`IsAuthenticated`), breaking public API tests.
4. `NO_REDIS` env var support in `settings.py` was incomplete, causing tests to fail in environments without Redis.

**Action:** Always check `requirements.txt` vs installed packages. Be wary of `CaptureQueriesContext` returning 0 queries; ensure `DEBUG=True` is active during such tests via `@override_settings`.
