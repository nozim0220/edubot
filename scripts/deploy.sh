#!/bin/bash
set -e

echo "🚀 EduBot deployment started..."

# Check .env
if [ ! -f .env ]; then
    echo "❌ .env file not found! Copy .env.example to .env and fill in values."
    exit 1
fi

mkdir -p logs media staticfiles nginx/certs

# Build
echo "📦 Building Docker images..."
docker compose build --no-cache

# Start DB and Redis first
echo "🗄️ Starting database and Redis..."
docker compose up -d db redis
sleep 10

# Run migrations
echo "🔄 Running migrations..."
docker compose run --rm web python manage.py migrate --noinput

# Collect static
echo "📁 Collecting static files..."
docker compose run --rm web python manage.py collectstatic --noinput

# Create superuser (optional)
echo "👤 Creating superuser (skip with Ctrl+C)..."
docker compose run --rm web python manage.py createsuperuser --noinput \
    --telegram_id=100000000 || true

# Load initial data
echo "📊 Loading initial data..."
docker compose run --rm web python manage.py loaddata fixtures/initial_data.json || true

# Start all services
echo "▶️ Starting all services..."
docker compose up -d

echo "✅ Deployment complete!"
echo "🌐 API: https://yourdomain.com/api/v1/"
echo "📚 Docs: https://yourdomain.com/api/docs/"
echo "⚙️ Admin: https://yourdomain.com/admin/"
