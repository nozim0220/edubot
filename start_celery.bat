@echo off
title EduBot - Celery Worker
color 0E
echo.
echo  ╔══════════════════════════════════╗
echo  ║   EduBot - Celery Worker         ║
echo  ╚══════════════════════════════════╝
echo.

call venv\Scripts\activate.bat

set DJANGO_SETTINGS_MODULE=config.settings.local
set USE_SQLITE=true

echo  [OK] Celery worker ishga tushmoqda...
echo  [OK] Eslatmalar va broadcast ishlaydi
echo.
echo  Toxtatish uchun: Ctrl+C
echo.

celery -A config.celery worker --loglevel=info --pool=solo
pause
