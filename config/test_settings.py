from .settings import *

DATABASE_ENGINE = 'sqlite'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Disable Redis for tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
AXES_CACHE = 'default'

# Disable throttling for tests
REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = []

# Disable security tracking middleware for tests as it might require Redis
MIDDLEWARE = [m for m in MIDDLEWARE if 'store.tracking_middleware.SecurityTrackingMiddleware' not in m]

# Use simple password hasher for speed
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]
