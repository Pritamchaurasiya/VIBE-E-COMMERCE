## 2025-02-20 - Fix dependency conflict and optimized analytics
**Learning:** `django-celery-beat` has a strict dependency on `Django<6.0`, but `requirements.txt` specified `Django>=6.0`, causing installation failures. Also `django-csp` 4.0+ requires dictionary-based configuration, but `settings.py` used the legacy tuple format, causing `SystemCheckError`.
**Action:** Always check `requirements.txt` for conflicting version constraints before installation. When upgrading packages like `django-csp`, verify configuration compatibility.
