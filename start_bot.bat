@echo off
title EduBot (Telegram)
color 0B
echo.
echo  [1] venv faollashtirilmoqda...
call venv\Scripts\activate.bat

echo  [2] Muhit sozlanmoqda...
set USE_SQLITE=true
set USE_MEMORY_CACHE=true
set CELERY_EAGER=true
set DJANGO_SETTINGS_MODULE=config.settings.local

echo  [3] Bot ishga tushmoqda...
echo.
echo  ================================
echo   ABT Yordamchi Bot — ONLINE
echo  ================================
echo.
python bot\main.py
pause
