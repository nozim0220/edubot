#!/bin/bash
# ============================================
# EduBot — Dockersiz local ishga tushirish
# ============================================
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_ok()   { echo -e "${GREEN}✅ $1${NC}"; }
log_err()  { echo -e "${RED}❌ $1${NC}"; exit 1; }
log_warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════╗"
echo "║   EduBot — Local Setup & Run Script      ║"
echo "╚══════════════════════════════════════════╝"
echo -e "${NC}"

# ─── 1. PYTHON TEKSHIRISH ───────────────────
log_info "Python tekshirilmoqda..."
python3 --version >/dev/null 2>&1 || log_err "Python 3 topilmadi! https://python.org dan yuklab oling"
PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
log_ok "Python $PY_VER topildi"

# ─── 2. POSTGRESQL TEKSHIRISH ───────────────
log_info "PostgreSQL tekshirilmoqda..."
if ! command -v psql >/dev/null 2>&1; then
    log_warn "PostgreSQL topilmadi. O'rnatish:"
    echo "  Ubuntu/Debian: sudo apt install postgresql postgresql-contrib"
    echo "  macOS:         brew install postgresql@16"
    echo "  Windows:       https://www.postgresql.org/download/windows/"
    read -p "PostgreSQL o'rnatilgandan so'ng ENTER bosing..."
fi
log_ok "PostgreSQL topildi"

# ─── 3. REDIS TEKSHIRISH ────────────────────
log_info "Redis tekshirilmoqda..."
if ! command -v redis-cli >/dev/null 2>&1; then
    log_warn "Redis topilmadi. O'rnatish:"
    echo "  Ubuntu/Debian: sudo apt install redis-server"
    echo "  macOS:         brew install redis"
    echo "  Windows:       https://github.com/microsoftarchive/redis/releases"
    read -p "Redis o'rnatilgandan so'ng ENTER bosing..."
fi
log_ok "Redis topildi"

# ─── 4. VIRTUAL ENV ─────────────────────────
log_info "Virtual environment yaratilmoqda..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    log_ok "venv yaratildi"
else
    log_ok "venv mavjud"
fi

source venv/bin/activate
log_ok "venv faollashtirildi"

# ─── 5. DEPENDENCIES ────────────────────────
log_info "Kutubxonalar o'rnatilmoqda (1-2 daqiqa)..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
log_ok "Barcha kutubxonalar o'rnatildi"

# ─── 6. .ENV FAYL ───────────────────────────
if [ ! -f ".env" ]; then
    cp .env.example .env
    log_warn ".env fayl yaratildi — quyidagi qiymatlarni to'ldiring!"
fi

# ─── 7. DATABASE YARATISH ───────────────────
log_info "PostgreSQL bazasi yaratilmoqda..."
source .env 2>/dev/null || true
DB_NAME="${DB_NAME:-edubot}"
DB_USER="${DB_USER:-edubot_user}"
DB_PASSWORD="${DB_PASSWORD:-edubot_pass}"

# Create user and database
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" 2>/dev/null || true
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;" 2>/dev/null || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;" 2>/dev/null || true
log_ok "Database: $DB_NAME"

# ─── 8. REDIS START ─────────────────────────
log_info "Redis ishga tushirilmoqda..."
sudo systemctl start redis-server 2>/dev/null || \
redis-server --daemonize yes 2>/dev/null || \
brew services start redis 2>/dev/null || true
sleep 1
redis-cli ping >/dev/null 2>&1 && log_ok "Redis ishlamoqda" || log_warn "Redis ishlamayapti, qo'lda ishga tushiring"

# ─── 9. ENV SOZLAMALAR ──────────────────────
export DJANGO_SETTINGS_MODULE=config.settings.development

# ─── 10. MIGRATIONS ─────────────────────────
log_info "Migration ishlatilmoqda..."
python manage.py makemigrations users education universities payments notifications ai_assistant 2>/dev/null || true
python manage.py migrate
log_ok "Migration bajarildi"

# ─── 11. INITIAL DATA ───────────────────────
log_info "Dastlabki ma'lumotlar kiritilmoqda..."
python scripts/create_initial_data.py
log_ok "Ma'lumotlar kiritildi"

# ─── 12. STATIC FILES ───────────────────────
log_info "Static fayllar yig'ilmoqda..."
python manage.py collectstatic --noinput -v 0
log_ok "Static fayllar tayyor"

# ─── 13. SUPERUSER ──────────────────────────
echo ""
echo -e "${YELLOW}Admin foydalanuvchi yaratish (ixtiyoriy):${NC}"
read -p "Admin yaratishni xohlaysizmi? (y/N): " CREATE_ADMIN
if [[ "$CREATE_ADMIN" == "y" || "$CREATE_ADMIN" == "Y" ]]; then
    python manage.py shell -c "
from apps.users.models import User
if not User.objects.filter(telegram_id=100000000).exists():
    u = User.objects.create(telegram_id=100000000, first_name='Admin', is_staff=True, is_superuser=True)
    u.set_password('admin123')
    u.save()
    print('Admin yaratildi: telegram_id=100000000, parol=admin123')
else:
    print('Admin allaqachon mavjud')
"
fi

# ─── 14. ISHGA TUSHIRISH ────────────────────
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║        ✅ SETUP TUGADI!                  ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Endi quyidagi 3 terminal oching:${NC}"
echo ""
echo -e "${YELLOW}Terminal 1 — Django server:${NC}"
echo "  source venv/bin/activate"
echo "  DJANGO_SETTINGS_MODULE=config.settings.development python manage.py runserver 0.0.0.0:8000"
echo ""
echo -e "${YELLOW}Terminal 2 — Celery worker:${NC}"
echo "  source venv/bin/activate"
echo "  DJANGO_SETTINGS_MODULE=config.settings.development celery -A config.celery worker --loglevel=info"
echo ""
echo -e "${YELLOW}Terminal 3 — Telegram Bot:${NC}"
echo "  source venv/bin/activate"
echo "  DJANGO_SETTINGS_MODULE=config.settings.development python bot/main.py"
echo ""
echo -e "${BLUE}Manzillar:${NC}"
echo "  🌐 API:    http://localhost:8000/api/v1/"
echo "  📚 Docs:   http://localhost:8000/api/docs/"
echo "  ⚙️  Admin:  http://localhost:8000/admin/"
echo ""
echo -e "${RED}MUHIM: .env faylida TELEGRAM_BOT_TOKEN va boshqa kalitlarni to'ldiring!${NC}"
