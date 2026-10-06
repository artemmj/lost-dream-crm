# lost-dream-crm

<img width="4026" height="3626" alt="output" src="https://github.com/user-attachments/assets/1e207786-b1e3-4cb1-a2bf-769f5865b4f5" />

> **⚠️ ACTIVE DEVELOPMENT WARNING — Проект находится в стадии активной разработки.**

lost-dream-crm — микросервисная CRM-система. Архитектура построена на слабосвязанных доменах с изолированным хранением персональных данных.
Проект реализует стек FastAPI, Kafka и Vue.js с применением паттернов событийно-ориентированного взаимодействия.

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

> **Примечание:** в локальной инфраструктуре PostgreSQL опубликован на портах 5432 и 5433. Порты не являются публичными в production-среде и должны быть закрыты вне Docker Compose.

## 🚀 Быстрый старт

```bash
# Клонирование и настройка
git clone https://github.com/your-org/lostdream-crm.git
cp services/service-crm/.env.example services/service-crm/.env
cp services/service-auth/.env.example services/service-auth/.env
cp services/service-customers/.env.example services/service-customers/.env

# Запуск всей инфраструктуры и сервисов
make up

# Открыть Kafka UI для мониторинга событий
open http://localhost:8080

# Открыть Frontend
open http://localhost:3000
```

### Демонстрационный поток событий

В `service-customers` предусмотрен live-демо поток для проверки Kafka, Schema Registry, consumer и SSE:

```text
POST /api/v1/customers/demo/customer-created
    ↓
Kafka topic: customer.events.v1
    ↓
Schema Registry: Avro-схема + Confluent Wire Format
    ↓
CustomerEventsConsumer
    ↓
EventStream
    ↓
GET /api/v1/customers/events (SSE)
    ↓
Vue Dashboard
```

Ручные события отправляются через Kafka producer с `source=manual`. Дополнительно доступен backend-процесс генерации случайных `customer.created.v1` и `customer.updated.v1` раз в секунду:

```text
POST /api/v1/customers/demo/auto-stream/start
POST /api/v1/customers/demo/auto-stream/stop
GET  /api/v1/customers/demo/auto-stream
```

Автоматический генератор по умолчанию остановлен и запускается по необходимости. События `source=auto` отображаются отдельной лентой на dashboard.

Каждое demo-событие отправляется только один раз: через Kafka producer, а не напрямую в EventStream. Так обеспечивается единый источник событий для интерфейса и предотвращается дублирование.

## 📋 Статус реализации (Roadmap)

### ✅ Реализовано (MVP)

- [x] **service-auth** — единственный источник аутентификации (JWT + Redis сессии), регистрация, логин, интроспекция токенов, RBAC (User ↔ Role ↔ Permission)
- [x] **service-crm** — пользователи, роли, пермишены; защита эндпоинтов через `service-auth` (`AuthProxy` → `/auth/introspect`)
- [x] **service-customers** — CRUD для PII-данных клиентов, изолированная БД `db-customers`
- [x] **Frontend (Vue 3 + Pinia + Vite)** — страница логина, профиль пользователя, админка пользователей/ролей/пермишенов
- [x] **Nginx API Gateway** — роутинг `/api/v1/auth/*`, `/api/v1/crm/*`, `/api/v1/customers/*` + Vite HMR прокси
- [x] **Docker Compose** — весь стек одной командой (`make up`), healthchecks БД, volumes для персистентности
- [x] **Alembic миграции** — автогенерация, seed тестовых пользователей (`admin@crm.local` / `admin`)
- [x] **Kafka + Schema Registry (Avro)** — событийная шина для межсервисного взаимодействия
- [x] **Transactional Outbox Pattern** — гарантированная доставка событий без 2PC
- [x] **Демонстрационный Kafka-поток** — синтетические события `customer.created.v1` и `customer.updated.v1` проходят через Kafka, Schema Registry, consumer и попадают в live SSE-поток фронтенда

### 🚧 В работе (ближайшие итерации)

- [ ] **AES-256 шифрование PII at-rest** — шифрование чувствительных полей в `service-customers`
- [ ] **Rate Limiting + Circuit Breaker** — защита от перегрузок и каскадных сбоев
- [ ] **WebSocket Gateway** — real-time обновления метрик/статусов на фронтенде
- [ ] **Prometheus + Grafana** — метрики, алерты, дашборды
- [ ] **Testcontainers** — интеграционные тесты в CI
- [ ] **API Gateway JWT терминация** — nginx `auth_request` → `service-auth`, передача `X-User-*` заголовков downstream
- [ ] **service-commercial** — коммерческий домен (заказы, счета, воронки)

### 📦 Техдолг (планируемый рефакторинг)

- [ ] Вынос общего кода в `shared` пакет (`dao/base.py`, `db_dependency`, `models/mixins.py`, `handlers/auth.py`)
- [ ] Защита `service-customers` на уровне API Gateway
- [ ] Production сборка фронтенда (multi-stage Dockerfile)
- [ ] CORS и логирование через settings
