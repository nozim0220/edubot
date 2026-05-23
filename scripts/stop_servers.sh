#!/bin/bash
echo "🛑 EduBot serverlar to'xtatilmoqda..."
if [ -f ".pids" ]; then
    for pid in $(cat .pids); do
        kill $pid 2>/dev/null && echo "  Stopped PID: $pid" || true
    done
    rm .pids
fi
# Also kill by name
pkill -f "manage.py runserver" 2>/dev/null || true
pkill -f "celery" 2>/dev/null || true
pkill -f "bot/main.py" 2>/dev/null || true
echo "✅ Barcha serverlar to'xtatildi"
