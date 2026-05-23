"""Foydalanuvchini admin qilish."""
import os, sys, django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.users.models import User

# Barcha userlarni ko'rsat
print("=== Barcha foydalanuvchilar ===")
for u in User.objects.all():
    print(f"  ID: {u.telegram_id} | {u.full_name} | admin={u.is_admin} | staff={u.is_staff}")

print()
tg_id = input("Admin qilmoqchi bo'lgan Telegram ID ni kiriting: ").strip()
try:
    user = User.objects.get(telegram_id=int(tg_id))
    user.is_admin = True
    user.is_staff = True
    user.save(update_fields=['is_admin', 'is_staff'])
    print(f"✅ {user.full_name} admin qilindi!")
except User.DoesNotExist:
    print(f"❌ Telegram ID {tg_id} topilmadi!")
except Exception as e:
    print(f"❌ Xato: {e}")
