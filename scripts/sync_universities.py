"""
University ma'lumotlarini rasmiy manbalardan yangilash.

Ishlatish:
  python scripts/sync_universities.py          -- hammasi
  python scripts/sync_universities.py --uz      -- faqat O'zbekiston
  python scripts/sync_universities.py --world   -- xorijiy universitetlar
  python scripts/sync_universities.py --status  -- hozirgi holat
"""
import os, sys, django, argparse, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.universities.models import University, Faculty
from apps.universities.scrapers import (
    get_all_verified_data,
    fetch_uz_from_hemis,
    fetch_world_unis_by_country,
)
from datetime import date as d

# ── Ariza muddatlari (2026-2027) ─────────────────────
DEADLINES = {
    'UZ': d(2026, 7, 20),
    'US': d(2027, 1, 1),
    'GB': d(2026, 10, 15),
    'DE': d(2026, 7, 15),
    'KR': d(2026, 9, 30),
    'TR': d(2026, 2, 28),
    'CN': d(2026, 3, 31),
    'JP': d(2026, 11, 30),
    'MY': d(2026, 3, 31),
    'RU': d(2026, 4, 1),
    'CA': d(2027, 1, 15),
    'FR': d(2027, 1, 15),
}


def sync_verified(verbose=True):
    """Tekshirilgan ma'lumotlarni yangilash."""
    data   = get_all_verified_data()
    added  = 0
    updated= 0

    for uni_name, info in data.items():
        deadline = info.pop('application_deadline_fall', None)
        faculties = info.pop('faculties', [])
        if deadline and isinstance(deadline, str):
            try:
                from datetime import date
                y, m, day = map(int, deadline.split('-'))
                deadline = date(y, m, day)
            except Exception:
                deadline = DEADLINES.get(info.get('country', 'UZ'))

        defaults = {k: v for k, v in info.items()
                    if v is not None and v != '' and k != 'faculties'}
        if deadline:
            defaults['application_deadline_fall'] = deadline

        try:
            u, created = University.objects.update_or_create(
                name=uni_name, defaults=defaults
            )
            if created:
                added += 1
                if verbose: print(f"  ✅ YANGI: {info.get('short_name','?')} — {uni_name[:45]}")
            else:
                updated += 1
                if verbose: print(f"  ♻️  YANGILANDI: {info.get('short_name','?')} — {uni_name[:45]}")

            # Fakultetlar
            for f_data in faculties:
                name, degree, years, fee, lang = f_data
                Faculty.objects.get_or_create(
                    university=u, name=name,
                    defaults={
                        'degree':          degree,
                        'duration_years':  years,
                        'tuition_fee_usd': fee,
                        'language':        lang,
                        'is_active':       True,
                    }
                )
        except Exception as e:
            print(f"  ❌ Xato ({uni_name[:30]}): {e}")

    return added, updated


def sync_uz_from_api(verbose=True):
    """HEMIS yoki Hipolabs dan O'zbekiston universitetlarini olish."""
    if verbose: print("\n📡 HEMIS / Hipolabs dan ma'lumot olinmoqda...")
    unis = fetch_uz_from_hemis()
    added = 0
    for item in unis:
        name = item.get('name', '').strip()
        if not name or len(name) < 6:
            continue
        # Allaqachon bazada bor bo'lsa o'tkazib yuborish
        if University.objects.filter(name__icontains=name[:25]).exists():
            continue
        try:
            University.objects.create(
                name=name,
                country='UZ',
                city=item.get('city', 'Toshkent'),
                website=item.get('website', ''),
                is_active=True,
                description_uz=f"{name} — O'zbekiston oliy ta'lim muassasasi.",
                application_deadline_fall=DEADLINES['UZ'],
            )
            added += 1
            if verbose: print(f"  ✅ {name[:50]}")
        except Exception as e:
            pass
    if verbose: print(f"  📊 {added} ta yangi O'zbekiston universiteti qo'shildi")
    return added


def sync_world_unis(verbose=True):
    """Xorijiy universitetlarni Hipolabs dan olish (is_active=False)."""
    countries = [
        ('United States', 'US'), ('United Kingdom', 'GB'),
        ('Germany', 'DE'), ('Japan', 'JP'),
        ('South Korea', 'KR'), ('China', 'CN'),
        ('Turkey', 'TR'), ('Malaysia', 'MY'),
        ('France', 'FR'), ('Canada', 'CA'),
        ('Russia', 'RU'), ('Australia', 'AU'),
    ]
    total = 0
    for country_name, code in countries:
        if verbose: print(f"  📡 {country_name}...")
        unis = fetch_world_unis_by_country(country_name, code)
        added = 0
        for item in unis:
            name = item.get('name', '').strip()
            if not name or len(name) < 5: continue
            if University.objects.filter(name__icontains=name[:25]).exists(): continue
            try:
                University.objects.create(
                    name=name, country=code,
                    website=item.get('website', ''),
                    is_active=False,  # Admin tekshirguncha o'chiq
                    application_deadline_fall=DEADLINES.get(code),
                )
                added += 1
            except Exception: pass
        if verbose: print(f"     {added} ta yangi ({code})")
        total += added
        time.sleep(0.5)  # API ni haddan ziyod so'rovlarga to'smaslik uchun
    return total


def show_status():
    """Hozirgi holat."""
    total   = University.objects.count()
    active  = University.objects.filter(is_active=True).count()
    with_fac= University.objects.filter(faculties__isnull=False).distinct().count()
    by_country = {}
    for code in ['UZ','US','GB','DE','KR','JP','CN','TR','MY','RU','CA','FR']:
        n = University.objects.filter(country=code, is_active=True).count()
        if n: by_country[code] = n
    flags = {'UZ':'🇺🇿','US':'🇺🇸','GB':'🇬🇧','DE':'🇩🇪','KR':'🇰🇷','JP':'🇯🇵',
             'CN':'🇨🇳','TR':'🇹🇷','MY':'🇲🇾','RU':'🇷🇺','CA':'🇨🇦','FR':'🇫🇷'}
    print(f"\n📊 DATABASE HOLATI")
    print(f"  Jami universitetlar: {total}")
    print(f"  Faol (botda ko'rinadi): {active}")
    print(f"  Tasdiqlash kutilmoqda: {total - active}")
    print(f"  Fakultetli: {with_fac}\n")
    print("  Mamlakat bo'yicha (faol):")
    for code, n in sorted(by_country.items(), key=lambda x: -x[1]):
        flag = flags.get(code, '🌍')
        print(f"    {flag} {code}: {n} ta")


def main():
    parser = argparse.ArgumentParser(description="University sync")
    parser.add_argument('--uz',     action='store_true', help="Faqat O'zbekiston")
    parser.add_argument('--world',  action='store_true', help="Xorijiy universitetlar (Hipolabs)")
    parser.add_argument('--status', action='store_true', help="Hozirgi holat")
    parser.add_argument('--all',    action='store_true', help="Hammasi")
    args = parser.parse_args()

    print("=" * 55)
    print("  🏫 University Sync — ABT Yordamchi Bot")
    print("=" * 55)

    if args.status:
        show_status()
        return

    # Har doim tekshirilgan ma'lumotlarni yangilash
    print("\n📚 Tekshirilgan ma'lumotlar (rasmiy)...")
    added, updated = sync_verified(verbose=True)
    print(f"\n  ✅ {added} ta yangi, {updated} ta yangilandi")

    if args.uz or args.all or (not any([args.world])):
        sync_uz_from_api()

    if args.world or args.all:
        print("\n🌍 Xorijiy universitetlar (Hipolabs)...")
        n = sync_world_unis()
        print(f"\n  ✅ {n} ta yangi xorijiy universitet (admin tasdiq kerak)")

    print()
    show_status()
    print("\n✅ SYNC TUGADI!")
    print("  Botni qayta ishga tushirmasangiz ham yangilanadi.")
    print("  Yangi universitetlarni faollashtirish:")
    print("  python manage.py admin yoki scripts/make_admin.py orqali")


if __name__ == '__main__':
    main()
