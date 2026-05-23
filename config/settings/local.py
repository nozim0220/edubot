"""
Local / Windows development settings.
PostgreSQL va Redis siz ham ishlaydi.
"""
from .base import *
import os

DEBUG = True
ALLOWED_HOSTS = ['*']

# ── SQLite (PostgreSQL o'rnatmasdan) ─────────────────
USE_SQLITE = os.environ.get('USE_SQLITE', 'true').lower() == 'true'
if USE_SQLITE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ── Memory Cache (Redis o'rnatmasdan) ─────────────────
USE_MEMORY_CACHE = os.environ.get('USE_MEMORY_CACHE', 'true').lower() == 'true'
if USE_MEMORY_CACHE:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'edubot-local',
        }
    }
    SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# ── Redis URL (optional) ──────────────────────────────
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/1')

# ── Celery ────────────────────────────────────────────
# CELERY_EAGER=true bo'lsa Celery task'lar Redis siz ishlaydi
if os.environ.get('CELERY_EAGER', 'true').lower() == 'true':
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True

# ── Email ─────────────────────────────────────────────
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ── Security (dev uchun o'chirilgan) ─────────────────
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# ── Throttle (dev uchun yuqori limit) ─────────────────
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'anon': '10000/hour',
    'user': '100000/hour',
}

# AI keys — .env dan yoki PowerShell env dan o'qiladi
import os
GROQ_API_KEY   = os.environ.get('GROQ_API_KEY',   '')
GROQ_MODEL     = os.environ.get('GROQ_MODEL',     'llama-3.3-70b-versatile')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
AI_DAILY_FREE_LIMIT    = 100
AI_DAILY_PREMIUM_LIMIT = 500
