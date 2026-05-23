# ============================================
#  EduBot — Windows PowerShell Setup Script
#  Ishlatish: powershell -ExecutionPolicy Bypass -File scripts\windows_setup.ps1
# ============================================

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "╔══════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   EduBot — Windows Setup Script          ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ─── 1. Python tekshirish ───────────────────
Write-Host "[1/7] Python tekshirilmoqda..." -ForegroundColor Yellow
try {
    $pyVersion = python --version 2>&1
    Write-Host "  ✅ $pyVersion" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Python topilmadi!" -ForegroundColor Red
    Write-Host "  https://python.org/downloads dan yuklab o'rnating" -ForegroundColor Red
    Write-Host "  O'rnatishda 'Add Python to PATH' ni belgilang!" -ForegroundColor Red
    pause
    exit 1
}

# ─── 2. Virtual Environment ─────────────────
Write-Host "[2/7] Virtual environment yaratilmoqda..." -ForegroundColor Yellow
if (-Not (Test-Path "venv")) {
    python -m venv venv
    Write-Host "  ✅ venv yaratildi" -ForegroundColor Green
} else {
    Write-Host "  ✅ venv allaqachon mavjud" -ForegroundColor Green
}

# Activate
.\venv\Scripts\Activate.ps1
Write-Host "  ✅ venv faollashtirildi" -ForegroundColor Green

# ─── 3. pip yangilash ───────────────────────
Write-Host "[3/7] pip yangilanmoqda..." -ForegroundColor Yellow
python -m pip install --upgrade pip -q
Write-Host "  ✅ pip yangilandi" -ForegroundColor Green

# ─── 4. Kutubxonalar ────────────────────────
Write-Host "[4/7] Kutubxonalar o'rnatilmoqda (3-5 daqiqa)..." -ForegroundColor Yellow
pip install -r requirements.txt -q
Write-Host "  ✅ Barcha kutubxonalar o'rnatildi" -ForegroundColor Green

# ─── 5. .env fayl ───────────────────────────
Write-Host "[5/7] .env fayl tekshirilmoqda..." -ForegroundColor Yellow
if (-Not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "  ⚠️  .env fayl yaratildi — to'ldiring!" -ForegroundColor Yellow
} else {
    Write-Host "  ✅ .env mavjud" -ForegroundColor Green
}

# ─── 6. Migrate ─────────────────────────────
Write-Host "[6/7] Database migration..." -ForegroundColor Yellow
$env:DJANGO_SETTINGS_MODULE = "config.settings.local"
$env:USE_SQLITE = "true"
$env:USE_MEMORY_CACHE = "true"

python manage.py migrate
Write-Host "  ✅ Migration bajarildi" -ForegroundColor Green

# ─── 7. Initial data ────────────────────────
Write-Host "[7/7] Dastlabki ma'lumotlar kiritilmoqda..." -ForegroundColor Yellow
python scripts/create_initial_data.py
Write-Host "  ✅ Ma'lumotlar kiritildi" -ForegroundColor Green

# ─── Admin yaratish ─────────────────────────
Write-Host ""
Write-Host "Admin foydalanuvchi yaratilmoqda..." -ForegroundColor Yellow
python manage.py shell -c @"
from apps.users.models import User
u, created = User.objects.get_or_create(telegram_id=100000000)
u.first_name='Admin'; u.is_staff=True; u.is_superuser=True
u.set_password('admin123'); u.save()
print('Admin tayyor: telegram_id=100000000 | parol=admin123')
"@

# ─── Tugash ─────────────────────────────────
Write-Host ""
Write-Host "╔══════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║   ✅  SETUP MUVAFFAQIYATLI TUGADI!       ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "Keyingi qadam — start_bot.bat ni ishga tushiring!" -ForegroundColor Cyan
Write-Host ""
pause
