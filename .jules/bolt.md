## 2024-05-23 - Dependency Version Conflicts
**Learning:** `requirements.txt` specifies `Django>=6.0` which conflicts with `django-celery-beat` (requires <6.0). Also `django-csp` installed as 4.0 requires new dictionary-based settings format, breaking legacy tuple config.
**Action:** Use `pip install "Django<6.0"` for testing environment and update `config/settings.py` to support `django-csp` 4.0 structure. Be wary of contradictory version requirements.
