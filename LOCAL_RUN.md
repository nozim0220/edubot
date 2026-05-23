# 🚀 EduBot — Dockersiz Ishga Tushirish

## ⚡ Eng tezkor yo'l (SQLite + Xotirada cache)

```bash
# 1. Papkaga kiring
cd edubot

# 2. Virtual environment
python3 -m venv venv
source venv/bin/activate        # Linux/macOS
# yoki: venv\Scripts\activate   # Windows

# 3. Kutubxonalar
pip install -r requirements.txt

# 4. .env fayl
cp .env.example .env
```

`.env` faylini oching va **faqat bu 2 ta qatorni** to'ldiring:
```env
SECRET_KEY=istalgan-uzun-maxfiy-kalit-123456789
TELEGRAM_BOT_TOKEN=sizning_bot_tokeningiz_bu_yerda
```

```bash
# 5. SQLite + Memory cache bilan ishga tushirish
export DJANGO_SETTINGS_MODULE=config.settings.local
export USE_SQLITE=true
export USE_MEMORY_CACHE=true
export CELERY_EAGER=true

# 6. Migration
python manage.py migrate

# 7. Dastlabki ma'lumotlar
python scripts/create_initial_data.py

# 8. Admin yaratish
python manage.py shell -c "
from apps.users.models import User
u, _ = User.objects.get_or_create(telegram_id=100000000)
u.first_name='Admin'; u.is_staff=True; u.is_superuser=True
u.set_password('admin123'); u.save()
print('Admin: telegram_id=100000000  parol=admin123')
"

# 9. Server ishga tushirish
python manage.py runserver
```

Yangi terminalda bot:
```bash
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=config.settings.local
export USE_SQLITE=true
export USE_MEMORY_CACHE=true
python bot/main.py
```

---

## 🔧 To'liq yo'l (PostgreSQL + Redis bilan)

### PostgreSQL o'rnatish

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**macOS (Homebrew):**
```bash
brew install postgresql@16
brew services start postgresql@16
```

**Windows:**
- https://www.postgresql.org/download/windows/ dan yuklab o'rnating

### PostgreSQL baza yaratish

```bash
sudo -u postgres psql
```
Psql ichida:
```sql
CREATE USER edubot_user WITH PASSWORD 'kuchli_parol_123';
CREATE DATABASE edubot OWNER edubot_user;
GRANT ALL PRIVILEGES ON DATABASE edubot TO edubot_user;
\q
```

### Redis o'rnatish

**Ubuntu/Debian:**
```bash
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
# Tekshirish:
redis-cli ping   # PONG chiqishi kerak
```

**macOS:**
```bash
brew install redis
brew services start redis
```

**Windows:**
- https://github.com/microsoftarchive/redis/releases

---

### .env to'ldirish (to'liq)

```env
SECRET_KEY=django-insecure-CHANGE-THIS-TO-RANDOM-50-CHARS
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=edubot
DB_USER=edubot_user
DB_PASSWORD=kuchli_parol_123
DB_HOST=localhost
DB_PORT=5432

REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1

TELEGRAM_BOT_TOKEN=1234567890:AAFake-tokenni-bu-yerga-yozing
REQUIRED_CHANNELS=@kanalingiz   # bo'sh qoldirsa ham bo'ladi

OPENAI_API_KEY=sk-your-openai-key    # bo'sh qoldirsa AI ishlamaydi
OPENAI_MODEL=gpt-4o

STRIPE_SECRET_KEY=sk_test_...        # bo'sh qoldirsa to'lov test
CLICK_SERVICE_ID=12345
PAYME_MERCHANT_ID=your_id
```

---

### 4 ta terminal oching

**Terminal 1 — Django:**
```bash
cd edubot
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=config.settings.development
python manage.py runserver 0.0.0.0:8000
```

**Terminal 2 — Celery Worker:**
```bash
cd edubot
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=config.settings.development
celery -A config.celery worker --loglevel=info
```

**Terminal 3 — Celery Beat (eslatmalar):**
```bash
cd edubot
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=config.settings.development
celery -A config.celery beat --loglevel=info
```

**Terminal 4 — Bot:**
```bash
cd edubot
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=config.settings.development
python bot/main.py
```

---

## 🌐 Manzillar

| Xizmat | URL |
|--------|-----|
| Admin panel | http://localhost:8000/admin/ |
| Swagger API docs | http://localhost:8000/api/docs/ |
| ReDoc | http://localhost:8000/api/redoc/ |
| API | http://localhost:8000/api/v1/ |

---

## 🤖 Bot Token olish

1. Telegramda **@BotFather** ga yozing
2. `/newbot` buyrug'ini yuboring
3. Bot nomini kiriting: `EduBot`
4. Username kiriting: `MyEduBot` (oxiri `bot` bilan tugashi kerak)
5. Token oling: `1234567890:AAFake...`
6. `.env` ga qo'ying: `TELEGRAM_BOT_TOKEN=1234567890:AAFake...`

---

## ❓ Ko'p uchraydigan xatolar

**"ModuleNotFoundError: No module named 'django'"**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**"django.db.utils.OperationalError: could not connect to server"**
```bash
sudo systemctl start postgresql
# yoki SQLite ishlating: export USE_SQLITE=true
```

**"redis.exceptions.ConnectionError"**
```bash
sudo systemctl start redis-server
# yoki memory cache: export USE_MEMORY_CACHE=true
```

**"psycopg2 not installed"**
```bash
pip install psycopg2-binary
```

**Bot ishlamayapti:**
- `.env` da `TELEGRAM_BOT_TOKEN` to'g'ri ekanligini tekshiring
- Bot tokenini @BotFather dan yangi oling

---

## 🪟 Windows uchun

PowerShell:
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
$env:DJANGO_SETTINGS_MODULE="config.settings.local"
$env:USE_SQLITE="true"
$env:USE_MEMORY_CACHE="true"
python manage.py migrate
python manage.py runserver
```

---

## 🧪 Testlarni ishlatish

```bash
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=config.settings.local
export USE_SQLITE=true
export USE_MEMORY_CACHE=true
pytest tests/ -v
```
