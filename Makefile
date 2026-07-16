.PHONY: up down build logs test lint kafka-ui

# Переменные для удобства
COMPOSE = docker compose
SERVICES = auth crm customers accounting external-api ws-gateway frontend nginx

up: ## Запустить всю инфраструктуру и сервисы
	$(COMPOSE) up -d --build

down: ## Остановить все контейнеры
	$(COMPOSE) down

downup: ## Пересобрать образы с перезапуском
	$(COMPOSE) down

build: ## Пересобрать образы без запуска
	$(COMPOSE) build

logs: ## Просмотр логов всех сервисов (Ctrl+C для выхода)
	$(COMPOSE) logs -f --tail=100

test: ## Запуск интеграционных тестов с Testcontainers
	$(COMPOSE) run --rm auth pytest -v
	$(COMPOSE) run --rm crm pytest -v
	$(COMPOSE) run --rm customers pytest -v

lint: ## Проверка кода (ruff + mypy)
	$(COMPOSE) run --rm auth ruff check .
	$(COMPOSE) run --rm crm mypy app/

kafka-ui: ## Открыть Kafka UI в браузере
	open http://localhost:8080 || xdg-open http://localhost:8080

db-reset: ## Сброс БД (ОПАСНО: удаляет все данные)
	$(COMPOSE) down -v
	$(COMPOSE) up -d postgres
	sleep 3
	$(COMPOSE) exec postgres psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname LIKE '%_db';"

help: ## Показать справку
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'
