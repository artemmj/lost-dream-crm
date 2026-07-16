#!/bin/sh
set -e

echo "(AUTH-APP) Running database migrations..."
# ✅ Retry loop: ждем базу до 60 секунд
MAX_RETRIES=30
RETRY_COUNT=0
until uv run alembic upgrade head; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo "(AUTH-APP) ❌ Migrations failed after $MAX_RETRIES attempts!" >&2
        exit 1
    fi
    echo "(AUTH-APP) ⏳ Migration attempt $RETRY_COUNT failed. Retrying in 1s..."
    sleep 1
done

echo "(AUTH-APP) 🚀 Starting FastAPI..."
exec uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 1
