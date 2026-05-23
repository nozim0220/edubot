"""
Base Django settings for EduBot platform.
"""
import os
from pathlib import Path
from datetime import timedelta
import environ

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load environment variables
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('SECRET_KEY')
DEBUG = env.bool('DEBUG', default=False)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
    'django_celery_beat',
    'django_celery_results',
]

LOCAL_APPS = [
    'apps.users',
    'apps.education',
    'apps.universities',
    'apps.payments',
    'apps.notifications',
    'apps.ai_assistant',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME', default='edubot'),
        'USER': env('DB_USER', default='edubot_user'),
        'PASSWORD': env('DB_PASSWORD', default=''),
        'HOST': env('DB_HOST', default='localhost'),
        'PORT': env('DB_PORT', default='5432'),
        'OPTIONS': {
            'connect_timeout': 10,
        },
        'CONN_MAX_AGE': 60,
    }
}

# Redis (optional - local.py da override qilinadi)
REDIS_URL = env('REDIS_URL', default='redis://localhost:6379/0')
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://localhost:6379/1')

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env('REDIS_URL', default='redis://localhost:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'RETRY_ON_TIMEOUT': True,
            'MAX_CONNECTIONS': 1000,
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
        }
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Celery
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://localhost:6379/1')
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'django-cache'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Tashkent'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.User'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    },
    'EXCEPTION_HANDLER': 'apps.users.exceptions.custom_exception_handler',
}

# JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=env.int('JWT_ACCESS_TOKEN_LIFETIME_MINUTES', default=60)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=env.int('JWT_REFRESH_TOKEN_LIFETIME_DAYS', default=30)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': env('SECRET_KEY'),
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# CORS
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[
    'http://localhost:3000',
    'http://localhost:8000',
])
CORS_ALLOW_CREDENTIALS = True

# DRF Spectacular
SPECTACULAR_SETTINGS = {
    'TITLE': 'EduBot API',
    'DESCRIPTION': 'Telegram Education Platform API',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'TAGS': [
        {'name': 'auth', 'description': 'Authentication endpoints'},
        {'name': 'users', 'description': 'User profile endpoints'},
        {'name': 'education', 'description': 'Education and quiz endpoints'},
        {'name': 'universities', 'description': 'University database endpoints'},
        {'name': 'payments', 'description': 'Payment endpoints'},
        {'name': 'ai', 'description': 'AI assistant endpoints'},
    ],
}

# Telegram Bot
TELEGRAM_BOT_TOKEN = env('TELEGRAM_BOT_TOKEN', default='')
TELEGRAM_WEBHOOK_SECRET = env('TELEGRAM_WEBHOOK_SECRET', default='')
WEBHOOK_URL = env('WEBHOOK_URL', default='')
REQUIRED_CHANNELS = env.list('REQUIRED_CHANNELS', default=[])

# Groq (bepul AI)
GROQ_API_KEY = env('GROQ_API_KEY', default='')
GROQ_MODEL = env('GROQ_MODEL', default='llama-3.3-70b-versatile')

# OpenAI (pullik)
OPENAI_API_KEY = env('OPENAI_API_KEY', default='')
OPENAI_MODEL = env('OPENAI_MODEL', default='gpt-4o')
AI_MAX_TOKENS = 2000
AI_DAILY_FREE_LIMIT = 50
AI_DAILY_PREMIUM_LIMIT = 500

# Payments
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY', default='')
STRIPE_WEBHOOK_SECRET = env('STRIPE_WEBHOOK_SECRET', default='')
CLICK_SERVICE_ID = env('CLICK_SERVICE_ID', default='')
CLICK_MERCHANT_ID = env('CLICK_MERCHANT_ID', default='')
CLICK_SECRET_KEY = env('CLICK_SECRET_KEY', default='')
PAYME_MERCHANT_ID = env('PAYME_MERCHANT_ID', default='')
PAYME_SECRET_KEY = env('PAYME_SECRET_KEY', default='')

PREMIUM_MONTHLY_PRICE = env.int('PREMIUM_MONTHLY_PRICE', default=999)
PREMIUM_YEARLY_PRICE = env.int('PREMIUM_YEARLY_PRICE', default=7999)

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='EduBot <noreply@edubot.uz>')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'bot_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'bot.log',
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'bot': {
            'handlers': ['console', 'bot_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'celery': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# XP System
XP_PER_CORRECT_ANSWER = 10
XP_PER_TEST_COMPLETION = 50
XP_PER_DAILY_CHALLENGE = 100
XP_LEVEL_MULTIPLIER = 100

LEVEL_THRESHOLDS = {
    1: 0, 2: 100, 3: 300, 4: 600, 5: 1000,
    6: 1500, 7: 2100, 8: 2800, 9: 3600, 10: 4500,
    11: 5500, 12: 6600, 13: 7800, 14: 9100, 15: 10500,
    16: 12000, 17: 13600, 18: 15300, 19: 17100, 20: 19000,
}


# Override REST_FRAMEWORK exception handler and pagination
REST_FRAMEWORK['EXCEPTION_HANDLER'] = 'config.exceptions.custom_exception_handler'
REST_FRAMEWORK['DEFAULT_PAGINATION_CLASS'] = 'config.pagination.StandardResultsSetPagination'

# Celery Beat Schedule
from celery.schedules import crontab
CELERY_BEAT_SCHEDULE = {
    'send-study-reminders': {
        'task': 'apps.notifications.tasks.send_study_reminders_task',
        'schedule': crontab(minute='*/5'),
    },
    'check-exam-deadlines': {
        'task': 'apps.notifications.tasks.check_exam_deadlines_task',
        'schedule': crontab(hour=9, minute=0),
    },
    'check-premium-expiry': {
        'task': 'apps.notifications.tasks.check_premium_expiry_task',
        'schedule': crontab(hour=10, minute=0),
    },
}
