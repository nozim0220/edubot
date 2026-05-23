#!/bin/bash
# ============================================
# EduBot — Barcha serverlarni ishga tushirish
# ============================================

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Virtual env
if [ -d "venv" ]; then
    source venv/bin/activate
fi

export DJANGO_SETTINGS_MODULE=config.settings.development

mkdir -p logs

echo -e "${BLUE}EduBot serverlar ishga tushmoqda...${NC}"
echo ""

# Django
echo -e "${GREEN}[1/3] Django server ishga tushmoqda...${NC}"
python manage.py runserver 0.0.0.0:8000 > logs/django.log 2>&1 &
DJANGO_PID=$!
echo "  PID: $DJANGO_PID"
sleep 2

# Celery
echo -e "${GREEN}[2/3] Celery worker ishga tushmoqda...${NC}"
celery -A config.celery worker --loglevel=info > logs/celery.log 2>&1 &
CELERY_PID=$!
echo "  PID: $CELERY_PID"
sleep 2

# Celery Beat
echo -e "${GREEN}[2b] Celery Beat ishga tushmoqda...${NC}"
celery -A config.celery beat --loglevel=info > logs/celery_beat.log 2>&1 &
BEAT_PID=$!
echo "  PID: $BEAT_PID"
sleep 1

# Bot
echo -e "${GREEN}[3/3] Telegram Bot ishga tushmoqda...${NC}"
python bot/main.py > logs/bot.log 2>&1 &
BOT_PID=$!
echo "  PID: $BOT_PID"

# PID file
echo "$DJANGO_PID $CELERY_PID $BEAT_PID $BOT_PID" > .pids

echo ""
echo -e "${GREEN}✅ Barcha serverlar ishga tushdi!${NC}"
echo ""
echo "  🌐 API:   http://localhost:8000/api/v1/"
echo "  📚 Docs:  http://localhost:8000/api/docs/"
echo "  ⚙️  Admin: http://localhost:8000/admin/"
echo ""
echo "  📋 Loglar: logs/ papkasida"
echo ""
echo -e "${YELLOW}Toxtatish uchun: ./scripts/stop_servers.sh${NC}"
echo -e "${YELLOW}Loglarni ko'rish: tail -f logs/bot.log${NC}"

# Wait
wait
