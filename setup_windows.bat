@echo off
title EduBot - Windows Setup
color 0C
echo.
echo  ==========================================
echo   EduBot - Windows Setup Script
echo  ==========================================
echo.

:: Python tekshirish
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [XATO] Python topilmadi!
    echo  https://python.org/downloads dan yuklab ornatib,
    echo  "Add Python to PATH" ni belgilang!
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set PY_VER=%%i
echo  [OK] %PY_VER% topildi

:: Virtual env
if not exist "venv" (
    echo  [1/6] Virtual environment yaratilmoqda...
    python -m venv venv
    echo  [OK] venv yaratildi
) else (
    echo  [OK] venv allaqachon mavjud
)

:: Activate
call venv\Scripts\activate.bat
echo  [OK] venv faollashtirildi

:: pip
echo  [2/6] pip yangilanmoqda...
python -m pip install --upgrade pip -q
echo  [OK] pip yangilandi

:: Kutubxonalar
echo  [3/6] Kutubxonalar ornatilmoqda (3-5 daqiqa, kuting)...
pip install -r requirements.txt -q
if %errorlevel% neq 0 (
    echo.
    echo  [XATO] Kutubxonalar ornatilmadi!
    echo  Internet aloqasini tekshiring va qayta urinib koring
    pause
    exit /b 1
)
echo  [OK] Kutubxonalar ornatildi

:: .env fayl
if not exist ".env" (
    copy ".env.example" ".env" >nul
    echo  [!] .env fayl yaratildi
    echo  [!] MUHIM: .env faylini oching va TELEGRAM_BOT_TOKEN ni kiriting!
) else (
    echo  [OK] .env mavjud
)

:: Environment
set DJANGO_SETTINGS_MODULE=config.settings.local
set USE_SQLITE=true
set USE_MEMORY_CACHE=true
set CELERY_EAGER=true

:: Migration
echo  [4/6] Database (SQLite) migration...
python manage.py migrate
if %errorlevel% neq 0 (
    echo  [XATO] Migration muvaffaqiyatsiz!
    pause
    exit /b 1
)
echo  [OK] Database tayyor

:: Initial data
echo  [5/6] Dastlabki malumotlar kiritilmoqda...
python scripts\create_initial_data.py
echo  [OK] Malumotlar kiritildi

:: Admin
echo  [6/6] Admin foydalanuvchi yaratilmoqda...
python manage.py shell -c "from apps.users.models import User; u,_=User.objects.get_or_create(telegram_id=100000000); u.first_name='Admin'; u.is_staff=True; u.is_superuser=True; u.set_password('admin123'); u.save(); print('[OK] Admin: telegram_id=100000000 | parol=admin123')"

echo.
echo  ==========================================
echo   Setup muvaffaqiyatli tugadi!
echo  ==========================================
echo.
echo  Keyingi qadamlar:
echo.
echo  1. .env faylini NOTEPAD da oching:
echo     notepad .env
echo     TELEGRAM_BOT_TOKEN=BOTFATHER_DAN_TOKENNI_BU_YERGA_YOZING
echo.
echo  2. start_django.bat ni 2x bosib oching (Django server)
echo.
echo  3. start_bot.bat ni 2x bosib oching (Telegram bot)
echo.
echo  Manzillar:
echo     Admin: http://localhost:8000/admin/
echo     Docs:  http://localhost:8000/api/docs/
echo.
pause
