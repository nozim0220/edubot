"""Development settings."""
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

# Use console email backend in development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable SSL redirect in development
SECURE_SSL_REDIRECT = False

REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'anon': '1000/hour',
    'user': '10000/hour',
}
