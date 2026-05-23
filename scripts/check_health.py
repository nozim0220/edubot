"""Health check script - verifies all services are running."""
import os
import sys
import socket

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')


def check_postgres():
    import django
    django.setup()
    from django.db import connection
    try:
        connection.ensure_connection()
        count = connection.cursor().execute("SELECT COUNT(*) FROM users").fetchone()
        print("✅ PostgreSQL: Connected")
        return True
    except Exception as e:
        print(f"❌ PostgreSQL: {e}")
        return False


def check_redis():
    import django
    django.setup()
    from django.core.cache import cache
    try:
        cache.set('health_check', 'ok', 10)
        val = cache.get('health_check')
        if val == 'ok':
            print("✅ Redis: Connected")
            return True
        print("❌ Redis: Cache get/set failed")
        return False
    except Exception as e:
        print(f"❌ Redis: {e}")
        return False


def check_telegram_token():
    import django
    django.setup()
    from django.conf import settings
    token = settings.TELEGRAM_BOT_TOKEN
    if token and ':' in token:
        print(f"✅ Telegram token: Set ({token[:10]}...)")
        return True
    print("❌ Telegram token: Not set or invalid")
    return False


def check_openai_key():
    import django
    django.setup()
    from django.conf import settings
    key = settings.OPENAI_API_KEY
    if key and key.startswith('sk-'):
        print(f"✅ OpenAI key: Set ({key[:10]}...)")
        return True
    print("⚠️  OpenAI key: Not set (AI features will not work)")
    return False


if __name__ == '__main__':
    print("🔍 EduBot Health Check\n" + "="*40)
    results = []
    results.append(check_postgres())
    results.append(check_redis())
    results.append(check_telegram_token())
    results.append(check_openai_key())

    print("\n" + "="*40)
    if all(results[:3]):  # Postgres, Redis, Telegram are critical
        print("✅ All critical services OK!")
        sys.exit(0)
    else:
        print("❌ Some critical services failed!")
        sys.exit(1)
