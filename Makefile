.PHONY: up down downup build logs test lint db-reset help

COMPOSE = docker compose

# Имена сервисов должны совпадать с docker-compose.yml
BACKEND_SERVICES = service-crm service-auth service-customers

up: ## Запустить всю инфраструктуру и сервисы
	$(COMPOSE) up -d --build

down: ## Остановить все контейнеры
	$(COMPOSE) down

downup: ## Пересоздать контейнеры с пересборкой образов
	$(COMPOSE) down
	$(COMPOSE) up -d --build

build: ## Пересобрать образы без запуска
	$(COMPOSE) build

logs: ## Просмотр логов всех сервисов (Ctrl+C для выхода)
	$(COMPOSE) logs -f --tail=100

test: ## Запуск тестов всех backend-сервисов (uv run pytest)
	$(COMPOSE) run --rm service-crm uv run pytest -v
	$(COMPOSE) run --rm service-auth uv run pytest -v
	$(COMPOSE) run --rm service-customers uv run pytest -v

lint: ## Проверка кода линтером (uv run ruff check)
	$(COMPOSE) run --rm service-crm uv run ruff check .
	$(COMPOSE) run --rm service-auth uv run ruff check .
	$(COMPOSE) run --rm service-customers uv run ruff check .

db-reset: ## Сброс БД (ОПАСНО: удаляет все данные, включая тома)
	$(COMPOSE) down -v
	$(COMPOSE) up -d db-crm db-customers redis

help: ## Показать справку
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'