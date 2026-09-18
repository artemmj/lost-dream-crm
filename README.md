# lost-dream-crm

> **⚠️ ACTIVE DEVELOPMENT WARNING — Проект находится в стадии активной разработки.**

lost-dream-crm — микросервисная CRM-система. Архитектура построена на слабосвязанных доменах с изолированным хранением персональных данных.
Проект реализует стек FastAPI, Kafka и Vue/Refine с применением паттернов событийно-ориентированного взаимодействия.

## 🏗 Архитектура

- **Privacy by Design:** Сервис `customers-service` полностью изолирован. PII-данные шифруются at-rest и никогда не передаются по REST/gRPC напрямую. Обмен только через зашифрованные события Kafka.
- **Eventual Consistency:** Использование Transactional Outbox Pattern гарантирует атомарность бизнес-операций и доставки событий (без 2PC).
- **Real-Time First:** Фронтенд получает обновления метрик и статусов через WebSocket Gateway, подписанный на поток событий (не polling).
- **Infrastructure as Code:** Весь стек поднимается одной командой.

## 🛠 Технологический стек

| Слой | Технологии |
| :--- | :--- |
| **Backend Core** | Python 3.13, FastAPI, SQLAlchemy 2.0 (Async), Pydantic V2 |
| **Message Broker** | Apache Kafka, Schema Registry (Avro), Outbox Pattern — **В работе** |
| **Frontend** | Vue 3, Refine Framework, Recharts, Pinia — **Refine в работе** |
| **Data & Cache** | PostgreSQL 18, Redis 7 |
| **DevOps / Infra** | Docker Compose, Nginx, Testcontainers, Prometheus + Grafana — **В работе** |
| **Security** | JWT/OAuth2, AES-256 Encryption, Rate Limiting, Circuit Breaker — **В работе** |

## 🚀 Быстрый старт

```bash
# Клонирование и настройка
git clone https://github.com/your-org/lostdream-crm.git
cp services/service-crm/.env.example services/service-crm/.env
cp services/service-auth/.env.example services/service-auth/.env
cp services/service-customers/.env.example services/service-customers/.env

# Запуск всей инфраструктуры и сервисов
make up

# Открыть Kafka UI для мониторинга событий (когда Kafka будет добавлен)
# open http://localhost:8080

# Открыть Frontend
open http://localhost:3000
```

## 📋 Статус реализации (Roadmap)

### ✅ Реализовано (MVP)

- [x] **service-auth** — единственный источник аутентификации (JWT + Redis сессии), регистрация, логин, интроспекция токенов, RBAC (User ↔ Role ↔ Permission)
- [x] **service-crm** — пользователи, роли, пермишены; защита эндпоинтов через `service-auth` (`AuthProxy` → `/auth/introspect`)
- [x] **service-customers** — CRUD для PII-данных клиентов, изолированная БД `db-customers`
- [x] **Frontend (Vue 3 + Pinia + Vite)** — страница логина, профиль пользователя, админка пользователей/ролей/пермишенов
- [x] **Nginx API Gateway** — роутинг `/api/v1/auth/*`, `/api/v1/crm/*`, `/api/v1/customers/*` + Vite HMR прокси
- [x] **Docker Compose** — весь стек одной командой (`make up`), healthchecks БД, volumes для персистентности
- [x] **Alembic миграции** — автогенерация, seed тестовых пользователей (`admin@crm.local` / `admin`)

### 🚧 В работе (ближайшие итерации)

- [ ] **Kafka + Schema Registry (Avro)** — событийная шина для межсервисного взаимодействия
- [ ] **Transactional Outbox Pattern** — гарантированная доставка событий без 2PC
- [ ] **AES-256 шифрование PII at-rest** — шифрование чувствительных полей в `service-customers`
- [ ] **Rate Limiting + Circuit Breaker** — защита от перегрузок и каскадных сбоев
- [ ] **WebSocket Gateway** — real-time обновления метрик/статусов на фронтенде
- [ ] **Refine Framework** — миграция фронтенда с ручного Vue на Refine (CRUD-админка out of the box)
- [ ] **Prometheus + Grafana** — метрики, алерты, дашборды
- [ ] **Testcontainers** — интеграционные тесты в CI
- [ ] **API Gateway JWT терминация** — nginx `auth_request` → `service-auth`, передача `X-User-*` заголовков downstream
- [ ] **service-commercial** — коммерческий домен (заказы, счета, воронки)

### 📦 Техдолг (планируемый рефакторинг)

- [ ] Вынос общего кода в `shared` пакет (`dao/base.py`, `db_dependency`, `models/mixins.py`, `handlers/auth.py`)
- [ ] Устранение дублирования префикса `/auth/auth` в роутинге (см. раздел ниже)
- [ ] Защита `service-customers` на уровне API Gateway
- [ ] Production сборка фронтенда (multi-stage Dockerfile)
- [ ] CORS и логирование через settings, убрать `print()`
