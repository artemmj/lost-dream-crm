# lost-dream-crm

> **⚠️ ACTIVE DEVELOPMENT WARNING**
> Проект находится в стадии активной архитектурной разработки и прототипирования.

lost-dream-crm — микросервисная CRM-система для развлекательных центров. Архитектура построена на слабосвязанных доменах с изолированным хранением персональных данных.
Проект реализует стек FastAPI, Kafka и Vue/Refine с применением паттернов событийно-ориентированного взаимодействия.

## 🏗 Архитектура

- **Privacy by Design:** Сервис `customers-vault` полностью изолирован. PII-данные шифруются at-rest и никогда не передаются по REST/gRPC напрямую. Обмен только через зашифрованные события Kafka.
- **Eventual Consistency:** Использование Transactional Outbox Pattern гарантирует атомарность бизнес-операций и доставки событий. Никаких распределенных транзакций 2PC.
- **Real-Time First:** Фронтенд получает обновления метрик и статусов через WebSocket Gateway, подписанный на поток событий, а не через polling.
- **Infrastructure as Code:** Весь стек поднимается одной командой. Конфигурация Kafka, ACLs и схемы хранятся в репозитории.

## 🛠 Технологический стек

| Слой | Технологии |
| :--- | :--- |
| **Backend Core** | Python 3.12+, FastAPI, SQLAlchemy 2.0 (Async), Pydantic V2 |
| **Message Broker** | Apache Kafka, Schema Registry (Avro), Outbox Pattern |
| **Frontend** | Vue 3, Refine Framework, Recharts, Pinia |
| **Data & Cache** | PostgreSQL 16, Redis 7 |
| **DevOps / Infra** | Docker Compose, Nginx, Testcontainers, Prometheus + Grafana |
| **Security** | JWT/OAuth2, AES-256 Encryption, Rate Limiting, Circuit Breaker |

## 🚀 Быстрый старт

```bash
# Клонирование и настройка
git clone https://github.com/your-org/lostdream-crm.git
cp .env.example .env

# Запуск всей инфраструктуры и сервисов
make up

# Открыть Kafka UI для мониторинга событий
open http://localhost:8080

# Открыть Frontend
open http://localhost:3000
```
