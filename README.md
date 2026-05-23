# 🎓 EduBot — Telegram Education Platform

Production-ready Telegram education platform for students and university applicants.

## 🚀 Tech Stack
- **Python 3.12** + **Django 5.0** + **DRF**
- **PostgreSQL 16** — Main database
- **Redis 7** — Cache & Celery broker
- **Celery** — Async tasks & scheduling
- **aiogram 3.x** — Telegram Bot
- **OpenAI GPT-4o** — AI Assistant
- **Docker + Nginx** — Deployment

## 📁 Project Structure
```
edubot/
├── config/                  # Django settings, URLs, Celery
│   ├── settings/
│   │   ├── base.py         # Base settings
│   │   ├── production.py   # Production settings
│   │   └── development.py  # Dev settings
│   ├── urls.py
│   ├── celery.py
│   └── celery_beat_schedule.py
├── apps/
│   ├── users/              # User model, auth, admin
│   ├── education/          # Subjects, tests, quizzes, XP
│   ├── universities/       # University DB, search, save
│   ├── payments/           # Click, Payme, Stripe
│   ├── notifications/      # Celery tasks, reminders
│   └── ai_assistant/       # OpenAI integration
├── bot/
│   ├── handlers/           # Aiogram handlers
│   ├── middlewares/        # Auth, subscription, throttle, i18n
│   ├── keyboards/          # Inline keyboards
│   ├── utils/              # i18n texts
│   ├── main.py             # Bot entry point
│   └── webhook.py          # Django webhook view
├── nginx/                  # Nginx config
├── scripts/                # Deploy & init scripts
├── tests/                  # Pytest tests
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## ⚡ Quick Start

### 1. Clone & Configure
```bash
git clone https://github.com/yourrepo/edubot.git
cd edubot
cp .env.example .env
# Edit .env with your values
nano .env
```

### 2. Deploy with Docker
```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

### 3. Manual Setup (Development)
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

export DJANGO_SETTINGS_MODULE=config.settings.development

# Create .env file
cp .env.example .env

python manage.py migrate
python scripts/create_initial_data.py
python manage.py createsuperuser
python manage.py runserver
```

### 4. Run Bot (Dev/Polling mode)
```bash
# In .env: leave WEBHOOK_URL empty for polling
python bot/main.py
```

## 🔑 Required Environment Variables

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DB_PASSWORD` | PostgreSQL password |
| `TELEGRAM_BOT_TOKEN` | From @BotFather |
| `REQUIRED_CHANNELS` | e.g. `@channel1,@channel2` |
| `OPENAI_API_KEY` | OpenAI API key |
| `WEBHOOK_URL` | `https://yourdomain.com/webhook/telegram/` |
| `STRIPE_SECRET_KEY` | Stripe secret key |
| `CLICK_SERVICE_ID` | Click.uz service ID |
| `PAYME_MERCHANT_ID` | Payme merchant ID |

## 🌟 Features

### 🤖 Telegram Bot
- `/start` — Main menu
- Channel subscription gate (blocks access until subscribed)
- 3 languages: O'zbek, Русский, English
- Inline keyboards everywhere, back buttons

### 📚 Education
- 9 subjects: Math, English, Physics, Chemistry, Biology, History, IT, IELTS, SAT
- Quiz, Mock Exam, Random, Daily Challenge modes
- XP system + Levels (20 levels) + Streak
- Leaderboard (top 10 + my rank)
- Certificates

### 🤖 AI Assistant
- Homework help, Math solver, Grammar check
- Essay writing, Career advice, Study plan
- 10 requests/day (free) | 200/day (premium)
- Saved chat history

### 🏫 Universities
- 190+ countries support
- Search by name, country, budget, IELTS
- AI-powered recommendations
- Save favorites
- Compare universities

### 💎 Premium
- Monthly ($9.99) & Yearly ($79.99)
- Payment: Click.uz, Payme, Stripe
- Unlimited AI, Mock Exams, Advanced Analytics

### 🔔 Reminders
- Study reminders (custom time)
- Exam deadline alerts
- Premium expiry warnings

## 🔐 Security
- JWT Authentication (access + refresh tokens)
- Telegram webhook secret validation
- Rate limiting (DRF throttling)
- Django security headers
- SQL injection protection (ORM)
- Environment variables for secrets

## 📊 Admin Panel
- `https://yourdomain.com/admin/`
- User management (ban/unban, premium)
- Test & Question management
- University database
- Broadcast messages
- Payment tracking
- Celery beat schedules

## 📖 API Documentation
- Swagger: `https://yourdomain.com/api/docs/`
- ReDoc: `https://yourdomain.com/api/redoc/`

## 🧪 Running Tests
```bash
pytest tests/ -v
pytest tests/unit/ -v --tb=short
```

## 📦 Docker Commands
```bash
# View logs
docker compose logs -f web
docker compose logs -f bot
docker compose logs -f celery

# Shell access
docker compose exec web python manage.py shell

# Database backup
docker compose exec db pg_dump -U edubot_user edubot > backup.sql

# Restart specific service
docker compose restart bot

# Scale workers
docker compose up -d --scale celery=3
```

## 🔄 Celery Tasks
- `send_study_reminders_task` — Every 5 minutes
- `check_exam_deadlines_task` — Daily at 9:00 AM
- `check_premium_expiry_task` — Daily at 10:00 AM
- `send_broadcast_task` — On demand
- `send_telegram_message_task` — Async Telegram messages

## 🗄️ Database Models
| Model | Description |
|---|---|
| `User` | Telegram user + profile |
| `UserSession` | FSM state storage |
| `BannedUser` | Banned users |
| `Broadcast` | Mass messages |
| `Subject` | Academic subjects |
| `Question` | Test questions |
| `Test` | Test collections |
| `TestSession` | Active test sessions |
| `UserProgress` | Per-subject progress |
| `Certificate` | Achievement certs |
| `University` | University database |
| `Faculty` | University faculties |
| `SavedUniversity` | User saved unis |
| `AIChat` | AI conversations |
| `AIMessage` | Chat messages |
| `AIUsageLog` | Daily usage limits |
| `Payment` | Payment transactions |
| `PremiumPlan` | Subscription plans |
| `UserSubscription` | Active subscriptions |
| `Notification` | System notifications |
| `ExamDeadline` | User exam deadlines |

## 🚀 Production Checklist
- [ ] Set strong `SECRET_KEY`
- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Get SSL certificate (Let's Encrypt)
- [ ] Update nginx `yourdomain.com`
- [ ] Configure Telegram webhook
- [ ] Add `REQUIRED_CHANNELS`
- [ ] Set up Sentry (`SENTRY_DSN`)
- [ ] Configure Click/Payme credentials
- [ ] Test payments in sandbox mode
- [ ] Load initial data: `python scripts/create_initial_data.py`
- [ ] Create admin superuser

## 👨‍💻 Author
Built with ❤️ for Uzbek students
