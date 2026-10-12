from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
]

# Development Database Configuration (PostgreSQL + PostGIS with SQLite dev fallback)
USE_SQLITE = env.bool('USE_SQLITE', default=False)

# Target database path: backend/db.sqlite3; transitional fallback: repo root db.sqlite3
SQLITE_PATH = BASE_DIR / 'db.sqlite3'
if not SQLITE_PATH.exists() and (REPO_DIR / 'db.sqlite3').exists():
    SQLITE_PATH = REPO_DIR / 'db.sqlite3'

if USE_SQLITE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': SQLITE_PATH,
        }
    }
else:
    try:
        DATABASES = {
            'default': env.db('DATABASE_URL', default=f"{DEFAULT_DB_ENGINE}://{env('DB_USER', default='postgres')}:{env('DB_PASSWORD', default='postgres')}@{env('DB_HOST', default='localhost')}:{env('DB_PORT', default='5432')}/{env('DB_NAME', default='sanjog_db')}")
        }
    except Exception:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': SQLITE_PATH,
            }
        }

# Development Email Backend (Console Output)
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')

# Development Logging Setup
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
