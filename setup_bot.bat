@echo off
title EduBot Setup
color 0A
echo.
echo  =====================================
echo   EduBot — Dastlabki Sozlash
echo  =====================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo  [XATO] Python topilmadi!
    pause & exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do echo  [OK] %%i

echo.
echo  [1/5] Virtual muhit...
if exist "venv" rmdir /s /q venv
python -m venv venv
call venv\Scripts\activate.bat
echo  [OK] venv yaratildi

echo  [2/5] pip yangilanmoqda...
python -m pip install --upgrade pip -q

echo  [3/5] Kutubxonalar o'rnatilmoqda (5-10 daqiqa)...
pip install -r requirements.txt -q --no-warn-script-location
if errorlevel 1 (
    echo.
    echo  [!] Ba'zi kutubxonalar o'rnatilmadi, asosiylar tekshirilmoqda...
)

:: Asosiy kutubxonalar alohida tekshirish
python -c "import django" >nul 2>&1
if errorlevel 1 (
    echo  [XATO] Django o'rnatilmadi! Internetni tekshiring.
    pause & exit /b 1
)
python -c "import aiogram" >nul 2>&1
if errorlevel 1 (
    echo  [XATO] Aiogram o'rnatilmadi!
    pause & exit /b 1
)
echo  [OK] Asosiy kutubxonalar tayyor

echo  [4/5] Database...
set USE_SQLITE=true
set USE_MEMORY_CACHE=true
set CELERY_EAGER=true
set DJANGO_SETTINGS_MODULE=config.settings.local
python manage.py migrate
if errorlevel 1 ( echo [XATO] Migration! & pause & exit /b 1 )
echo  [OK] Database tayyor

echo  [5/5] Ma'lumotlar...
python scripts\fix_all.py

echo.
echo  =====================================
echo   SETUP TUGADI!
echo  =====================================
echo.
echo   .env faylida to'ldiring:
echo     TELEGRAM_BOT_TOKEN=tokeningiz
echo     GROQ_API_KEY=gsk_...
echo.
echo   Botni ishga tushirish: start_bot.bat
echo.
pause
