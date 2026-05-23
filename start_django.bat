@echo off
title EduBot - Django Server
color 0A
echo.
echo  ==========================================
echo   EduBot - Django Server
echo  ==========================================
echo.

if not exist "venv\Scripts\activate.bat" (
    echo  [XATO] venv topilmadi! Avval setup_windows.bat ni ishga tushiring
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

set DJANGO_SETTINGS_MODULE=config.settings.local
set USE_SQLITE=true
set USE_MEMORY_CACHE=true
set CELERY_EAGER=true

echo  [OK] Django server http://localhost:8000 da ishga tushmoqda...
echo  [OK] Admin:  http://localhost:8000/admin/
echo  [OK] Docs:   http://localhost:8000/api/docs/
echo.
echo  Toxtatish: Ctrl+C
echo.

python manage.py runserver 0.0.0.0:8000
pause
