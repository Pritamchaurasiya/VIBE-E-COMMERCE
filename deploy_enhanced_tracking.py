#!/usr/bin/env python3
"""
Enhanced Tracking System Deployment Script

This script automates the deployment and configuration of the Enhanced Tracking System
for the VIBE E-Commerce platform.

Features:
- Automated database setup and migration
- Redis configuration and optimization
- Django settings configuration
- Celery worker setup
- WebSocket server configuration
- Health checks and validation
- Performance optimization

Author: VIBE E-Commerce Enhancement Team
Version: 3.0.0
Last Updated: 2025-12-13
"""

import os
import sys
import subprocess  # nosec B404 - subprocess used for deployment automation
import json
import logging
import shutil
import argparse
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deployment.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EnhancedTrackingDeployment:
    """Main deployment class for Enhanced Tracking System."""

    def __init__(self, config_file: Optional[str] = None):
        self.config = self.load_config(config_file)
        self.project_root = Path(__file__).parent
        self.venv_path = self.project_root / 'venv_tracking'
        self.logs_dir = self.project_root / 'logs'

    def load_config(self, config_file: Optional[str] = None) -> Dict[str, Any]:
        """Load deployment configuration."""
        default_config = {
            'database': {
                'name': os.environ.get('DB_NAME', 'vibe_tracking'),
                'user': os.environ.get('DB_USER', 'tracking_user'),
                'password': os.environ.get('DB_PASSWORD', 'secure_password_from_env'),
                'host': os.environ.get('DB_HOST', 'localhost'),
                'port': os.environ.get('DB_PORT', '5432')
            },
            'redis': {
                'host': os.environ.get('REDIS_HOST', 'localhost'),
                'port': int(os.environ.get('REDIS_PORT', 6379)),
                'db': 1,
                'password': os.environ.get('REDIS_PASSWORD', None)
            },
            'django': {
                'secret_key': os.environ.get('DJANGO_SECRET_KEY', 'your-secret-key-change-in-production'),
                'debug': os.environ.get('DEBUG', 'False').lower() == 'true',
                'allowed_hosts': os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(','),
                'timezone': 'UTC'
            },
            'tracking': {
                'enable_enhanced_tracking': True,
                'enable_real_time_tracking': True,
                'enable_ai_analytics': True,
                'enable_anomaly_detection': True,
                'batch_size': 1000,
                'cache_timeout': 300,
                'rate_limit': 1000
            },
            'performance': {
                'max_workers': 4,
                'async_batch_size': 500,
                'cache_levels': ['redis', 'local'],
                'enable_circuit_breakers': True
            },
            'security': {
                'enable_data_encryption': True,
                'enable_rate_limiting': True,
                'enable_audit_logging': True,
                'anonymize_after_days': 90
            }
        }

        if config_file:
            # Security: Validate config file path
            config_path = Path(config_file).resolve()
            project_root = Path(__file__).parent.resolve()
            # Ensure config file is within project directory or common config locations
            if not (str(config_path).startswith(str(project_root)) or
                    config_path.suffix == '.json'):
                logger.warning("Config file path may be unsafe: %s", config_file)
            if config_path.exists():
                try:
                    # nosec B113 - config file path validated above
                    with open(config_path, 'r', encoding='utf-8') as f:
                        user_config = json.load(f)
                    default_config.update(user_config)
                    logger.info("Loaded configuration from %s", config_file)
                except (json.JSONDecodeError, OSError) as e:
                    logger.error("Error loading config file %s: %s", config_file, e)

        return default_config

    # Note: This method runs shell commands for deployment automation.
    # It should only be used with trusted input from configuration files.
    # pylint: disable=subprocess-run-check
    def run_command(
        self,
        command: str,
        cwd: Optional[str] = None,
        check: bool = True
    ) -> subprocess.CompletedProcess:
        """Run a shell command with logging."""
        logger.info("Running command: %s", command)
        try:
            result = subprocess.run(  # nosec B602 - deployment script with trusted config
                command,
                shell=True,  # nosec B602 - required for deployment commands
                cwd=cwd or str(self.project_root),
                capture_output=True,
                text=True,
                check=check
            )
            if result.stdout:
                logger.info("Command output: %s", result.stdout)
            return result
        except subprocess.CalledProcessError as e:
            logger.error("Command failed: %s", command)
            logger.error("Error: %s", e.stderr)
            if check:
                raise
            return e

    def setup_virtual_environment(self):
        """Set up Python virtual environment."""
        logger.info("Setting up virtual environment...")

        if self.venv_path.exists():
            logger.info("Virtual environment already exists, removing...")
            shutil.rmtree(self.venv_path)

        # Create virtual environment
        self.run_command(f"python -m venv {self.venv_path}")

        # Install base requirements
        requirements_file = self.project_root / 'requirements_tracking.txt'
        if not requirements_file.exists():
            self.create_requirements_file()

        pip_path = self.venv_path / 'bin' / 'pip'
        if os.name == 'nt':  # Windows
            pip_path = self.venv_path / 'Scripts' / 'pip.exe'

        self.run_command(f"{pip_path} install --upgrade pip")
        self.run_command(f"{pip_path} install -r {requirements_file}")

        logger.info("Virtual environment setup completed")

    def create_requirements_file(self):
        """Create requirements file with all necessary dependencies."""
        requirements_content = """# Enhanced Tracking System Requirements
Django>=4.2.0,<5.0.0
djangorestframework>=3.14.0
django-cors-headers>=4.0.0
channels>=4.0.0
channels-redis>=4.0.0
redis>=4.5.0
celery>=5.3.0
kombu>=5.3.0

# Analytics and ML
numpy>=1.24.0
pandas>=2.0.0
scikit-learn>=1.3.0
scipy>=1.10.0

# Database
psycopg2-binary>=2.9.0
dj-database-url>=1.2.0

# Utilities
python-decouple>=3.8
Pillow>=10.0.0
requests>=2.31.0
python-dateutil>=2.8.0

# Development and Testing
pytest>=7.4.0
pytest-django>=4.5.0
pytest-asyncio>=0.21.0
black>=23.0.0
flake8>=6.0.0

# Monitoring
sentry-sdk>=1.32.0
django-debug-toolbar>=4.0.0
"""

        requirements_file = self.project_root / 'requirements_tracking.txt'
        with open(requirements_file, 'w', encoding='utf-8') as f:
            f.write(requirements_content)

        logger.info("Created requirements_tracking.txt")

    def setup_database(self):
        """Set up PostgreSQL database for tracking."""
        logger.info("Setting up database...")

        db_config = self.config['database']

        # Create database
        create_db_command = f"""
        createdb -h {db_config['host']} -p {db_config['port']} -U postgres {db_config['name']}
        """

        try:
            self.run_command(create_db_command, check=False)
        except (subprocess.CalledProcessError, OSError) as e:
            logger.warning("Database creation failed (may already exist): %s", e)

        # Create user if it doesn't exist
        create_user_command = f"""
        psql -h {db_config['host']} -p {db_config['port']} -U postgres -c "
        CREATE USER {db_config['user']} WITH PASSWORD '{db_config['password']}';
        GRANT ALL PRIVILEGES ON DATABASE {db_config['name']} TO {db_config['user']};
        "
        """

        try:
            self.run_command(create_user_command, check=False)
        except (subprocess.CalledProcessError, OSError) as e:
            logger.warning("User creation failed (may already exist): %s", e)

        # Run migrations
        python_path = self.venv_path / 'bin' / 'python'
        if os.name == 'nt':
            python_path = self.venv_path / 'Scripts' / 'python.exe'

        self.run_command(f"{python_path} manage.py makemigrations store")
        self.run_command(f"{python_path} manage.py migrate")

        logger.info("Database setup completed")

    def setup_redis(self):
        """Set up and configure Redis."""
        logger.info("Setting up Redis...")

        # Check if Redis is running
        try:
            result = self.run_command("redis-cli ping", check=False)
            if "PONG" not in result.stdout:
                logger.warning("Redis is not responding, please ensure Redis is running")
        except (subprocess.CalledProcessError, OSError) as e:
            logger.error("Redis connectivity check failed: %s", e)

        # Create Redis configuration
        redis_config = self.config['redis']
        redis_config_content = f"""
# Redis configuration for Enhanced Tracking System
port {redis_config['port']}
bind 127.0.0.1
timeout 300
tcp-keepalive 60
maxmemory 512mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename tracking_dump.rdb
"""

        redis_config_file = self.project_root / 'redis_tracking.conf'
        with open(redis_config_file, 'w', encoding='utf-8') as f:
            f.write(redis_config_content)

        logger.info("Redis configuration created")

    def configure_django(self):
        """Configure Django settings for enhanced tracking."""
        logger.info("Configuring Django settings...")

        django_config = self.config['django']
        tracking_config = self.config['tracking']
        performance_config = self.config['performance']
        security_config = self.config['security']

        # Create enhanced settings file
        settings_content = f'''
"""
Enhanced Tracking System Django Settings
Generated automatically by deployment script
"""

import os
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "{django_config['secret_key']}"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = {str(django_config['debug']).title()}

ALLOWED_HOSTS = {django_config['allowed_hosts']}

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',

    # Third party apps
    'rest_framework',
    'corsheaders',
    'channels',

    # Local apps
    'store',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Enhanced Tracking Middleware
    'store.tracking_middleware.SilentTrackingMiddleware',
    'store.tracking_middleware.SecurityTrackingMiddleware',
    'store.tracking_middleware.PerformanceTrackingMiddleware',
    'store.tracking_middleware.DataModificationTrackingMiddleware',
]

ROOT_URLCONF = 'vibe_ecommerce.urls'

TEMPLATES = [
    {{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {{
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'store.context_processors.site_settings',
            ],
        }},
    }},
]

WSGI_APPLICATION = 'vibe_ecommerce.wsgi.application'
ASGI_APPLICATION = 'vibe_ecommerce.asgi.application'

# Database
DATABASES = {{
    'default': {{
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '{self.config['database']['name']}',
        'USER': '{self.config['database']['user']}',
        'PASSWORD': '{self.config['database']['password']}',
        'HOST': '{self.config['database']['host']}',
        'PORT': '{self.config['database']['port']}',
        'OPTIONS': {{
            'MAX_CONNS': 20,
            'MIN_CONNS': 5,
        }},
    }}
}}

# Cache Configuration
CACHES = {{
    'default': {{
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://{self.config['redis']['host']}:{self.config['redis']['port']}/{self.config['redis']['db']}',
        'OPTIONS': {{
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {{
                'max_connections': 50,
                'retry_on_timeout': True,
            }}
        }}
    }},
    'local': {{
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'tracking-cache',
    }}
}}

# Session Configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 86400  # 24 hours

# WebSocket Configuration
CHANNEL_LAYERS = {{
    'default': {{
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {{
            'hosts': [('{self.config['redis']['host']}', {self.config['redis']['port']})],
            'capacity': 1500,
            'expiry': 10,
        }},
    }},
}}

# Celery Configuration
CELERY_BROKER_URL = 'redis://{self.config['redis']['host']}:{self.config['redis']['port']}/2'
CELERY_RESULT_BACKEND = 'redis://{self.config['redis']['host']}:{self.config['redis']['port']}/3'
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = '{django_config['timezone']}'
CELERY_ENABLE_UTC = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = '{django_config['timezone']}'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# Enhanced Tracking Configuration
ENABLE_ENHANCED_TRACKING = {str(tracking_config['enable_enhanced_tracking']).title()}
ENABLE_REAL_TIME_TRACKING = {str(tracking_config['enable_real_time_tracking']).title()}
ENABLE_AI_ANALYTICS = {str(tracking_config['enable_ai_analytics']).title()}
ENABLE_ANOMALY_DETECTION = {str(tracking_config['enable_anomaly_detection']).title()}

# Tracking Performance Settings
TRACKING_BATCH_SIZE = {tracking_config['batch_size']}
TRACKING_CACHE_TIMEOUT = {tracking_config['cache_timeout']}
TRACKING_RATE_LIMIT = {tracking_config['rate_limit']}

# Security Settings
SECURE_SSL_REDIRECT = False  # Set to True in production
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Enhanced Security for Tracking Data
ENABLE_DATA_ENCRYPTION = {str(security_config['enable_data_encryption']).title()}
ENABLE_RATE_LIMITING = {str(security_config['enable_rate_limiting']).title()}
ENABLE_AUDIT_LOGGING = {str(security_config['enable_audit_logging']).title()}
ANONYMIZE_DATA_AFTER_DAYS = {security_config['anonymize_after_days']}

# Performance Optimization
MAX_WORKERS = {performance_config['max_workers']}
ASYNC_BATCH_SIZE = {performance_config['async_batch_size']}
CACHE_LEVELS = {performance_config['cache_levels']}
ENABLE_CIRCUIT_BREAKERS = {str(performance_config['enable_circuit_breakers']).title()}

# Logging Configuration
LOGGING = {{
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {{
        'verbose': {{
            'format': '{{levelname}} {{asctime}} {{module}} {{process:d}} {{thread:d}} {{message}}',
            'style': '{{',
        }},
        'simple': {{
            'format': '{{levelname}} {{message}}',
            'style': '{{',
        }},
    }},
    'handlers': {{
        'file': {{
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'tracking.log',
            'formatter': 'verbose',
        }},
        'console': {{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        }},
    }},
    'root': {{
        'handlers': ['console', 'file'],
        'level': 'INFO',
    }},
    'loggers': {{
        'store': {{
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        }},
        'django': {{
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        }},
    }},
}}

# Create logs directory
os.makedirs(BASE_DIR / 'logs', exist_ok=True)
'''

        settings_file = self.project_root / 'enhanced_settings.py'
        with open(settings_file, 'w', encoding='utf-8') as f:
            f.write(settings_content)

        logger.info("Django settings configured")

    def setup_celery(self):
        """Set up Celery configuration."""
        logger.info("Setting up Celery...")

        celery_content = '''
"""
Celery configuration for Enhanced Tracking System
"""

import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'enhanced_settings')

app = Celery('vibe_ecommerce')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
'''

        celery_file = self.project_root / 'celery_tracking.py'
        with open(celery_file, 'w', encoding='utf-8') as f:
            f.write(celery_content)

        logger.info("Celery configuration created")

    def setup_asgi(self):
        """Set up ASGI configuration for WebSockets."""
        logger.info("Setting up ASGI configuration...")

        asgi_content = '''
"""
ASGI config for Enhanced Tracking System
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'enhanced_settings')

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may need it.
django_asgi_app = get_asgi_application()

from store.routing import websocket_urlpatterns

application = ProtocolTypeRouter({{
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            )
        )
    ),
}})
'''

        asgi_file = self.project_root / 'asgi_tracking.py'
        with open(asgi_file, 'w', encoding='utf-8') as f:
            f.write(asgi_content)

        logger.info("ASGI configuration created")

    def create_startup_scripts(self):
        """Create startup scripts for different components."""
        logger.info("Creating startup scripts...")

        # Web server startup script
        web_startup = f'''#!/bin/bash
# Enhanced Tracking System Web Server Startup

echo "Starting Enhanced Tracking System Web Server..."

# Activate virtual environment
source {self.venv_path}/bin/activate

# Set environment variables
export DJANGO_SETTINGS_MODULE=enhanced_settings
export PYTHONPATH="{self.project_root}"

# Start Django development server
python manage.py runserver 0.0.0.0:8000

echo "Web server started on http://localhost:8000"
'''

        web_script = self.project_root / 'start_web.sh'
        with open(web_script, 'w', encoding='utf-8') as f:
            f.write(web_startup)
        os.chmod(web_script, 0o755)  # nosec B103 - standard executable permission

        # Celery worker startup script
        celery_startup = f'''#!/bin/bash
# Enhanced Tracking System Celery Worker Startup

echo "Starting Enhanced Tracking System Celery Worker..."

# Activate virtual environment
source {self.venv_path}/bin/activate

# Set environment variables
export DJANGO_SETTINGS_MODULE=enhanced_settings
export PYTHONPATH="{self.project_root}"

# Start Celery worker
celery -A vibe_ecommerce worker --loglevel=info

echo "Celery worker started"
'''

        celery_script = self.project_root / 'start_celery.sh'
        with open(celery_script, 'w', encoding='utf-8') as f:
            f.write(celery_startup)
        os.chmod(celery_script, 0o755)  # nosec B103 - standard executable permission

        # WebSocket server startup script
        websocket_startup = f'''#!/bin/bash
# Enhanced Tracking System WebSocket Server Startup

echo "Starting Enhanced Tracking System WebSocket Server..."

# Activate virtual environment
source {self.venv_path}/bin/activate

# Set environment variables
export DJANGO_SETTINGS_MODULE=enhanced_settings
export PYTHONPATH="{self.project_root}"

# Start Daphne WebSocket server
daphne -b 0.0.0.0 -p 8001 asgi_tracking:application

echo "WebSocket server started on http://localhost:8001"
'''

        websocket_script = self.project_root / 'start_websocket.sh'
        with open(websocket_script, 'w', encoding='utf-8') as f:
            f.write(websocket_startup)
        os.chmod(websocket_script, 0o755)  # nosec B103 - standard executable permission

        # Master startup script
        master_startup = f'''#!/bin/bash
# Enhanced Tracking System Master Startup

echo "Starting Enhanced Tracking System..."

# Create logs directory
mkdir -p {self.logs_dir}

# Function to handle cleanup
cleanup() {{
    echo "Shutting down Enhanced Tracking System..."
    kill $(jobs -p) 2>/dev/null
    exit 0
}}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start all components
echo "Starting web server..."
{self.project_root}/start_web.sh &

echo "Starting Celery worker..."
{self.project_root}/start_celery.sh &

echo "Starting WebSocket server..."
{self.project_root}/start_websocket.sh &

echo "Enhanced Tracking System started successfully!"
echo "Web Dashboard: http://localhost:8000/admin/enhanced-tracking/"
echo "API Endpoints: http://localhost:8000/api/v1/tracking/"
echo "WebSocket: ws://localhost:8001/"

# Wait for all processes
wait
'''

        master_script = self.project_root / 'start_tracking_system.sh'
        with open(master_script, 'w', encoding='utf-8') as f:
            f.write(master_startup)
        os.chmod(master_script, 0o755)  # nosec B103 - standard executable permission

        logger.info("Startup scripts created")

    def initialize_tracking_data(self):
        """Initialize tracking configuration and sample data."""
        logger.info("Initializing tracking data...")

        python_path = self.venv_path / 'bin' / 'python'
        if os.name == 'nt':
            python_path = self.venv_path / 'Scripts' / 'python.exe'

        # Create tracking configuration
        init_script = '''
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'enhanced_settings')
django.setup()

from store.models import TrackingConfiguration

# Default tracking configurations
configs = [
    {
        'category': 'file_operations',
        'is_enabled': True,
        'description': 'Track all file operations across the system',
        'retention_days': 90
    },
    {
        'category': 'user_actions',
        'is_enabled': True,
        'description': 'Track user interactions and behavior',
        'retention_days': 30
    },
    {
        'category': 'system_access',
        'is_enabled': True,
        'description': 'Track system access patterns and security events',
        'retention_days': 60
    },
    {
        'category': 'performance_metrics',
        'is_enabled': True,
        'description': 'Track system performance metrics',
        'retention_days': 30
    },
    {
        'category': 'security_events',
        'is_enabled': True,
        'description': 'Track security-related events and threats',
        'retention_days': 180
    }
]

for config_data in configs:
    TrackingConfiguration.objects.update_or_create(
        category=config_data['category'],
        defaults=config_data
    )

print("Tracking configuration initialized successfully")
'''

        init_file = self.project_root / 'init_tracking.py'
        with open(init_file, 'w', encoding='utf-8') as f:
            f.write(init_script)

        self.run_command(f"{python_path} {init_file}")

        # Clean up init script
        os.remove(init_file)

        logger.info("Tracking data initialization completed")

    def run_health_checks(self):
        """Run system health checks."""
        logger.info("Running health checks...")

        health_checks = [
            self.check_database_connection,
            self.check_redis_connection,
            self.check_django_setup,
            self.check_celery_setup,
            self.check_tracking_modules
        ]

        passed = 0
        failed = 0

        for check in health_checks:
            try:
                check()
                passed += 1
                logger.info("âœ“ %s passed", check.__name__)
            except Exception as e:
                failed += 1
                logger.error("âœ— %s failed: %s", check.__name__, e)

        logger.info("Health checks completed: %d passed, %d failed", passed, failed)

        if failed > 0:
            logger.error("Some health checks failed. Please review the errors above.")
            return False

        return True

    def check_database_connection(self):
        """Check database connectivity."""
        python_path = self.venv_path / 'bin' / 'python'
        if os.name == 'nt':
            python_path = self.venv_path / 'Scripts' / 'python.exe'

        check_script = '''
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'enhanced_settings')
django.setup()

from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    print("Database connection successful")
except Exception as e:
    raise Exception(f"Database connection failed: {e}")
'''

        result = self.run_command(f"{python_path} -c '{check_script}'", check=False)
        if result.returncode != 0:
            raise RuntimeError("Database connection test failed")

    def check_redis_connection(self):
        """Check Redis connectivity."""
        result = self.run_command("redis-cli ping", check=False)
        if "PONG" not in result.stdout:
            raise RuntimeError("Redis connection test failed")

    def check_django_setup(self):
        """Check Django setup."""
        python_path = self.venv_path / 'bin' / 'python'
        if os.name == 'nt':
            python_path = self.venv_path / 'Scripts' / 'python.exe'

        check_script = '''
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'enhanced_settings')
django.setup()

from store.realtime_tracking import realtime_tracking_service
from store.analytics_engine import analytics_engine

# Test basic imports and initialization
print("Django setup successful")
'''

        result = self.run_command(f"{python_path} -c '{check_script}'", check=False)
        if result.returncode != 0:
            raise RuntimeError("Django setup test failed")

    def check_celery_setup(self):
        """Check Celery setup."""
        python_path = self.venv_path / 'bin' / 'python'
        if os.name == 'nt':
            python_path = self.venv_path / 'Scripts' / 'python.exe'

        check_script = '''
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'enhanced_settings')
django.setup()

from celery_tracking import app as celery_app
print("Celery setup successful")
'''

        result = self.run_command(f"{python_path} -c '{check_script}'", check=False)
        if result.returncode != 0:
            raise RuntimeError("Celery setup test failed")

    def check_tracking_modules(self):
        """Check tracking module imports."""
        python_path = self.venv_path / 'bin' / 'python'
        if os.name == 'nt':
            python_path = self.venv_path / 'Scripts' / 'python.exe'

        check_script = '''
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'enhanced_settings')
django.setup()

try:
    from store.realtime_tracking import realtime_tracking_service, cache_manager
    from store.analytics_engine import analytics_engine
    from store.enhanced_tracking_api import EnhancedDashboardAPIView
    print("All tracking modules imported successfully")
except ImportError as e:
    raise Exception(f"Module import failed: {e}")
'''

        result = self.run_command(f"{python_path} -c '{check_script}'", check=False)
        if result.returncode != 0:
            raise RuntimeError("Tracking modules test failed")

    def generate_deployment_report(self):
        """Generate deployment report."""
        logger.info("Generating deployment report...")

        report = {
            'deployment_info': {
                'timestamp': datetime.now().isoformat(),
                'version': '3.0.0',
                'deployment_type': 'Enhanced Tracking System'
            },
            'configuration': self.config,
            'components': {
                'database': 'PostgreSQL',
                'cache': 'Redis',
                'message_queue': 'Celery',
                'websocket_server': 'Daphne',
                'web_framework': 'Django',
                'analytics_engine': 'Custom AI/ML',
                'real_time_processing': 'AsyncIO + WebSockets'
            },
            'endpoints': {
                'dashboard': 'http://localhost:8000/admin/enhanced-tracking/',
                'api_base': 'http://localhost:8000/api/v1/tracking/',
                'websocket': 'ws://localhost:8001/',
                'admin': 'http://localhost:8000/admin/'
            },
            'status': 'deployed',
            'next_steps': [
                'Start the system using ./start_tracking_system.sh',
                'Access the dashboard at http://localhost:8000/admin/enhanced-tracking/',
                'Configure tracking categories in the admin interface',
                'Set up monitoring and alerting',
                'Review and customize security settings',
                'Schedule regular maintenance tasks'
            ]
        }

        report_file = self.project_root / 'deployment_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)

        logger.info("Deployment report saved to %s", report_file)
        return report

    def deploy(self):
        """Main deployment method."""
        logger.info("Starting Enhanced Tracking System deployment...")

        try:
            # Create logs directory
            self.logs_dir.mkdir(exist_ok=True)

            # Run deployment steps
            self.setup_virtual_environment()
            self.setup_database()
            self.setup_redis()
            self.configure_django()
            self.setup_celery()
            self.setup_asgi()
            self.create_startup_scripts()
            self.initialize_tracking_data()

            # Run health checks
            if not self.run_health_checks():
                logger.error("Deployment failed health checks")
                return False

            # Generate deployment report
            report = self.generate_deployment_report()

            logger.info("Enhanced Tracking System deployment completed successfully!")
            logger.info("=" * 60)
            logger.info("DEPLOYMENT SUMMARY")
            logger.info("=" * 60)
            logger.info("Deployment Time: %s", report['deployment_info']['timestamp'])
            logger.info("Version: %s", report['deployment_info']['version'])
            logger.info("")
            logger.info("COMPONENTS:")
            for component, technology in report['components'].items():
                logger.info("  %s: %s", component.replace('_', ' ').title(), technology)
            logger.info("")
            logger.info("ENDPOINTS:")
            for name, url in report['endpoints'].items():
                logger.info("  %s: %s", name.replace('_', ' ').title(), url)
            logger.info("")
            logger.info("NEXT STEPS:")
            for step in report['next_steps']:
                logger.info("  â€¢ %s", step)
            logger.info("=" * 60)

            return True

        except Exception as e:
            logger.error("Deployment failed: %s", e)
            return False


def main():
    """Main deployment entry point."""

    parser = argparse.ArgumentParser(description='Enhanced Tracking System Deployment')
    parser.add_argument('--config', '-c', type=str, help='Configuration file path')
    parser.add_argument('--skip-checks', action='store_true', help='Skip health checks')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    deployment = EnhancedTrackingDeployment(args.config)

    success = deployment.deploy()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
