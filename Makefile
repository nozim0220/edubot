.PHONY: help build up down logs migrate shell test lint createsuperuser webhook

help:
	@echo "EduBot — Available commands:"
	@echo "  make build          — Build Docker images"
	@echo "  make up             — Start all services"
	@echo "  make down           — Stop all services"
	@echo "  make logs           — Tail all logs"
	@echo "  make migrate        — Run database migrations"
	@echo "  make shell          — Django shell"
	@echo "  make test           — Run all tests"
	@echo "  make lint           — Run syntax check"
	@echo "  make createsuperuser — Create admin user"
	@echo "  make webhook        — Set Telegram webhook"
	@echo "  make initdata       — Load initial data"

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

logs-web:
	docker compose logs -f web

logs-bot:
	docker compose logs -f bot

logs-celery:
	docker compose logs -f celery

migrate:
	docker compose run --rm web python manage.py migrate

makemigrations:
	docker compose run --rm web python manage.py makemigrations

shell:
	docker compose run --rm web python manage.py shell

test:
	docker compose run --rm web pytest tests/ -v --tb=short

lint:
	find . -name "*.py" | grep -v __pycache__ | xargs python3 -m py_compile && echo "All OK"

createsuperuser:
	docker compose run --rm web python manage.py createsuperuser

webhook:
	docker compose run --rm web python manage.py set_webhook

delete-webhook:
	docker compose run --rm web python manage.py set_webhook --delete

initdata:
	docker compose run --rm web python scripts/create_initial_data.py

daily-challenge:
	docker compose run --rm web python manage.py create_daily_challenge

backup:
	docker compose exec db pg_dump -U $${DB_USER:-edubot_user} $${DB_NAME:-edubot} > backup_$$(date +%Y%m%d_%H%M%S).sql

collectstatic:
	docker compose run --rm web python manage.py collectstatic --noinput

restart:
	docker compose restart

restart-bot:
	docker compose restart bot

restart-web:
	docker compose restart web

dev-run:
	DJANGO_SETTINGS_MODULE=config.settings.development python manage.py runserver

dev-bot:
	DJANGO_SETTINGS_MODULE=config.settings.development python bot/main.py

dev-celery:
	DJANGO_SETTINGS_MODULE=config.settings.development celery -A config.celery worker --loglevel=info
