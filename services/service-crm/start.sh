#!/bin/sh
set -e

echo "(CRM-APP) Running database migrations..."
# ✅ Retry loop: ждем базу до 60 секунд
MAX_RETRIES=30
RETRY_COUNT=0
until uv run alembic upgrade head; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo "(CRM-APP) ❌ Migrations failed after $MAX_RETRIES attempts!" >&2
        exit 1
    fi
    echo "(CRM-APP) ⏳ Migration attempt $RETRY_COUNT failed. Retrying in 1s..."
    sleep 1
done

echo "(CRM-APP) ✅ Migrations completed successfully!"

# ===== Создание тестовых пользователей =====

echo "(CRM-APP) 🌱 Creating test users..."

# Используем Python скрипт для создания тестовых данных
uv run python -m src.scripts.seed_users || {
    echo "(CRM-APP) ⚠️  Warning: Seed script failed, but continuing..."
}

echo "(CRM-APP) ✅ Test users created (or already existed)"

# ===== Запуск приложения =====

echo "(CRM-APP) 🚀 Starting FastAPI..."
exec uv run uvicorn src.main:app --host 0.0.0.0 --port 8000