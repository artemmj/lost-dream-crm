FROM python:3.13-alpine

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
RUN pip install uvicorn

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml uv.lock alembic.ini start.sh ./
COPY src/ ./src/

RUN uv sync --frozen

RUN chmod +x ./start.sh
EXPOSE 8000

# RUN useradd -m -u 1000 celery_user && chown -R celery_user:celery_user /app
# USER celery_user

CMD ["./start.sh"]
