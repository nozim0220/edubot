#!/bin/bash
set -e

echo "🔧 Setting up EduBot development environment..."

# Check Python version
python_version=$(python3 --version 2>&1 | grep -o "3\.[0-9]*")
echo "✅ Python: $(python3 --version)"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt -q

# Copy .env if not exists
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "📋 Created .env from .env.example — please fill in your values!"
fi

# Create log directory
mkdir -p logs media staticfiles

echo ""
echo "✅ Setup complete! Next steps:"
echo "  1. Edit .env with your API keys"
echo "  2. Start PostgreSQL and Redis"
echo "  3. Run: python manage.py migrate"
echo "  4. Run: python scripts/create_initial_data.py"
echo "  5. Run: python manage.py createsuperuser"
echo "  6. Run: python manage.py runserver"
echo "  7. In another terminal: python bot/main.py"
