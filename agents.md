# AGENTS.md — инструкции для AI-агентов

> Гайд по работе с репозиторием **lost-dream-crm** для AI-ассистентов и новых разработчиков.
> Проект **в активной разработке** — часть возможностей из README ещё не реализована (см. раздел «Текущее состояние и планы»).

---

## 1. Обзор проекта

lost-dream-crm — микросервисная CRM-система. Целевая архитектура (по README): Privacy by Design (изолированное хранение PII), event-driven на Kafka, Transactional Outbox. Фактически сейчас реализован монолитный набор из трёх синхронных FastAPI-сервисов + Vue-фронтенд за Nginx-шлюзом.

| Слой | Фактический стек |
| :--- | :--- |
| Backend | Python 3.13, FastAPI, SQLAlchemy 2.0 (async), Pydantic v2, Alembic, Redis, PyJWT, bcrypt/passlib |
| Пакетный менеджер | **uv** (`uv.lock`, `uv sync --frozen`, `uv run`) |
| Frontend | Vue 3, Vite 5, Pinia, vue-router 4, axios |
|| БД / кэш | PostgreSQL 16 (две изолированные БД), Redis 7 ||
| Инфраструктура | Docker Compose, Nginx (reverse proxy) |

**Язык кода и комментариев — русский.** Комментарии, docstring и сообщения об ошибках пишутся на русском; идентификаторы — на английском.

---

## 2. Архитектура и сервисы

```
Браузер → :80 nginx ─┬─ /api/v1/auth/*       → service-auth:8000   (логин/регистрация/сессии/introspect/me)
                     ├─ /api/v1/crm/          → service-crm:8000    (пользователи, роли, пермишены)
                     ├─ /api/v1/customers/  → service-customers:8000
                     └─ / (прочее)          → frontend:3000 (Vite dev + HMR)

service-crm ──(GET /auth/introspect, Authorization)──► service-auth
service-auth ──► db-crm + redis (сессии)
```

**Аутентификация — единый источник `service-auth`.** Он один выпускает JWT, хранит сессии в Redis и проверяет пермишены. Остальные сервисы **не декодируют токен сами** — они спрашивают у auth через `GET /introspect` (см. раздел 6).

| Сервис | Каталог | Порт (host) | root_path | БД / Redis | Назначение |
| :--- | :--- | :--- | :--- | :--- | :--- |
|| service-auth | `services/service-auth` | 8003 | — | db-crm + redis | **Единственный источник аутентификации**: register/login/logout, сессии (Redis), валидация токена и пермишенов (`/introspect`) ||
| service-crm | `services/service-crm` | 8001 | `/api/v1/crm` | db-crm | Пользователи, роли, пермишены;**владелец схемы** `db-crm` (единственная папка миграций) |
| service-customers | `services/service-customers` | 8002 | — | db-customers | PII-данные клиентов, изолированная БД |
| service-commercial | `services/service-commercial` | — | — | — | **Пустой каталог**, планируется |
| frontend | `frontend` | 3000 | — | — | SPA (Vite dev-сервер, proxy `/api` → nginx) |
| nginx | `infra/nginx` | 80, 443 | — | — | API Gateway (reverse proxy; JWT-терминация пока в сервисах) |
| redis | — | 6379 (только внутри сети) | — | — | Сессии/access-токены (dev-пароль `redispass`, volume `redis_data`) |
| db-crm / db-customers | — | 5432 / 5433 (порты НЕ публикуются на хост, только внутри compose-сети) | — | — | PostgreSQL 18 |

---

## 3. Структура репозитория

```
lost-dream-crm/
├── agents.md               # этот файл
├── docker-compose.yml      # весь стек одной командой
├── Makefile                # make up / down / logs / build (см. оговорки ниже)
├── infra/nginx/nginx.conf  # конфиг шлюза (роутинг /api/v1/*)
├── frontend/               # Vue 3 SPA
│   ├── Dockerfile          # multi-stage, target=development
│   ├── vite.config.js      # alias '@' → src/, proxy /api → nginx:80
│   └── src/
│       ├── api/            # axios-клиенты по доменам (client.js — фабрика + интерсепторы)
│       ├── stores/         # Pinia (auth.js)
│       ├── router/         # vue-router, meta.requiresAuth
│       ├── components/     # страницы/виджеты (SFC)
│       └── composables/    # useApi.js
└── services/
    ├── service-crm/        # эталонный сервис — придерживаться его структуры
    ├── service-customers/
    ├── service-auth/
    └── service-commercial/ # пусто, зарезервировано
```

Структура каждого backend-сервиса (эталон — `service-crm`):

```
services/service-X/
├── Dockerfile              # python:3.13-alpine + uv
├── pyproject.toml          # зависимости + [dependency-groups] dev
├── uv.lock
├── alembic.ini
├── start.sh                # миграции с retry → uvicorn
├── .dockerignore           # исключает .env и мусор из контекста сборки
├── .env.example            # шаблон; .env обязателен локально для make up (env_file)!
└── src/
    ├── main.py             # FastAPI app, CORS, include_router
    ├── settings.py         # pydantic-settings, env-алиасы
    ├── routes/             # эндпоинты: только HTTP-слой
    ├── schemas/            # Pydantic request/response модели
    ├── services/           # бизнес-логика + доменные ошибки + DTO
    ├── dao/                # доступ к данным (BaseDAO + конкретные DAO)
    ├── models/             # SQLAlchemy 2.0 (Mapped/mapped_column) + mixins
    ├── handlers/           # технические обработчики (AuthHandler: JWT encode/decode)
    ├── dependencies/       # DI-фабрики, auth/permissions/db/redis
    └── migrations/         # Alembic (versions/)
```

---

## 4. Команды

### Запуск всего стека

```bash
# 1. Создать .env для каждого сервиса (ОБЯЗАТЕЛЬНО — compose подключает его
#    через env_file; в сами образы .env больше НЕ копируется):
cp services/service-crm/.env.example services/service-crm/.env
cp services/service-auth/.env.example services/service-auth/.env
cp services/service-customers/.env.example services/service-customers/.env

# 2. Поднять всё (compose дождётся healthcheck'ов БД и Redis):
make up            # = docker compose up -d --build

make logs          # логи всех сервисов
make down          # остановить
make downup        # пересоздать контейнеры с пересборкой
make test          # pytest во всех backend-сервисах
make lint          # ruff во всех backend-сервисах
docker compose down -v   # снести вместе с томами БД и Redis (ОПАСНО)
```

### Backend (внутри контейнера или локально через uv)

```bash
cd services/service-crm
uv sync                          # установка зависимостей из uv.lock
uv run uvicorn src.main:app --reload --port 8000   # локальный запуск
uv run alembic upgrade head      # применить миграции
uv run alembic revision --autogenerate -m "описание"   # создать миграцию
uv run pytest -v                 # тесты (pytest, pytest-asyncio, httpx, aiosqlite)
uv run ruff check .              # линтер
```

### Frontend

```bash
cd frontend
npm install
npm run dev        # :3000, HMR, proxy /api → nginx
npm run build
```

### Проверка работоспособности

- Gateway health: `curl http://localhost/health`
- AUTH docs (Swagger): `http://localhost/api/v1/auth/docs`
- CRM docs (Swagger): `http://localhost/api/v1/crm/docs`
- Логин (seed-пользователи `admin@crm.local` / `john.doe@example.com`, пароль `admin`):
  `curl -X POST http://localhost/api/v1/auth/login -H 'Content-Type: application/json' -d '{"email":"admin@crm.local","password":"admin"}'`

---

## 5. Конвенции backend

### Слои и направление зависимостей

Строго: `routes → services → dao → models`. Слой знает только про слой под ним.

- **routes/** — только HTTP: парсинг запроса, вызов сервиса, маппинг доменных ошибок в `HTTPException` (404/409/403/401). Бизнес-логики быть не должно.
- **services/** — бизнес-логика. Принимает/возвращает DTO и dict, бросает **доменные исключения** (`UserNotFoundError`, `UserAlreadyExistsError`), определённые здесь же. Никакого FastAPI внутри.
- **dao/** — наследники `BaseDAO` (Generic, см. `dao/base.py`). **Наружу отдают dict**, а не ORM-объекты (`_model_to_dict` внутри сессии). Чтение — через `db.read_only_scope()`, запись — через `db.session_scope()` (авто-commit/rollback).
- **models/** — SQLAlchemy 2.0 (`Mapped`, `mapped_column`), миксины `IDMixin`, `CreatedAtUpdatedAtMixin` из `models/mixins.py`. Связи M2M через вторичные таблицы (`user_roles`, `role_permissions`).
- **schemas/** — Pydantic v2 (`model_config = {"from_attributes": True}` для ответов из dict/ORM). Схемы ответов не включают чувствительные поля: `password_hash` исключён из `UserResponse` и `CustomerResponse` — не возвращайте его обратно.
- **dependencies/** — DI-фабрики вида `get_user_service(auth_handler: AuthHandler = Depends(AuthHandler)) -> UserService`. Сессии БД — через класс `DBDependency` (`session_scope`/`read_only_scope`), а не сырые генераторы. `db_dependency` и `redis_dependency` — **модульные синглтоны**: движок SQLAlchemy и пулы Redis создаются один раз на процесс, а не на каждый запрос. В фабриках используйте синглтоны напрямую, не `Depends(DBDependency)`.
- **handlers/** — инфраструктурные обработчики (JWT encode/decode в `AuthHandler`).

### Конфигурация

- Только через `pydantic-settings` (`src/settings.py`): поля с `alias="POSTGRES_..."` и т.п., `SettingsConfigDict(env_file="../.env", extra="ignore")`.
- Нельзя хардкодить секреты и хосты. Новые переменные добавлять в `settings.py` **и** в `.env.example`.

### Миграции

- Alembic, каталог `src/migrations/versions/`. Перед коммитом миграции — проверить, что `start.sh` поднимет её на чистой БД (миграции выполняются автоматически при старте контейнера, с retry до 30 попыток).

### Точка входа

- Приложение создаётся в `src/main.py` как `app = FastAPI(root_path=...)`; роутеры подключаются через `app.include_router(...)`. `root_path` должен соответствовать префиксу проксирования в nginx.

---

## 6. Аутентификация и RBAC

- Логин выдаёт JWT (`pyjwt`) c `user_id` + `session_id`; `session_id` хранится в **Redis** — access-токен валиден, только пока сессия жива.
- Токен передаётся в заголовке `Authorization` (фронт кладёт его целиком, без префикса Bearer — см. `frontend/src/api/client.js`).
- Проверка токена выполняется в **service-auth**: `GET /auth/introspect` → декодирует JWT (`handlers/auth.py::AuthHandler`), сверяет сессию в Redis, загружает пользователя с ролями, возвращает `UserMeResponse`.
- **service-crm не валидирует токен локально** — он проксирует проверку через `AuthProxy` → `http://service-auth:8000/auth/introspect`.
- RBAC: `User M2M Role M2M Permission` (модели в `models/user.py`). Защита эндпоинта:

```python
from src.dependencies.permissions import RequirePermission, Perm

@router.get("/{user_id}")
async def get_user(
    user_id: int,
    current_user: UserMeResponse = Depends(RequirePermission("get_user")),
    # короткая запись: current_user: UserMeResponse = Perm("get_user"),
):
    ...
```

- `is_superuser` проходит любую проверку; неактивный пользователь получает 403.
- `PATCH/DELETE /users/{id}` требуют пермишены `update_user`/`delete_user`; административные поля (`is_active`, `is_banned`, `is_superuser`, `is_verified`) может менять **только суперпользователь** — иначе 403 (защита от эскалации привилегий).
- Коды пермишенов — строки вида `get_user`, `list_users`, `update_user`, `delete_user`, `manage_roles`. Коды управления ролями/пермишенами сидят в БД (миграция `add_roles_and_permissions`), коды управления пользователями — в миграции `add_user_management_permissions` (выданы роли `admin`). Новые коды добавлять осознанно — через миграцию с `ON CONFLICT DO NOTHING`.

---

## 7. Конвенции frontend

- **api/** — фабрика `createApiClient(servicePath)` в `client.js`: интерсептор запроса добавляет JWT из `localStorage('token')`, интерсептор ответа при 401 чистит токен. Клиенты: `crmApiClient` (`/api/v1/crm`), `customersApiClient` (`/api/v1/customers`). Новый домен = новый модуль в `src/api/` на базе фабрики.
- **stores/** — Pinia (setup-стиль, `defineStore` с функцией). Auth-сторе: `login/register/fetchUser/logout/init`; токен дублируется в `localStorage`.
- **router/** — маршруты с `meta: { requiresAuth: true }`; фактическую проверку делает `App.vue` через `isAuthenticated` (показ `AuthPage`).
- Alias `@` → `src/` (настроен в `vite.config.js`); в существующем коде встречаются и относительные импорты — допустимо, но в новом коде предпочитайте `@/`.
- Стиль: 4 пробела, одинарные кавычки, без точек с запятой (как в существующих файлах).

---

## 8. Рецепты

### Добавить эндпоинт в backend-сервис

1. `models/` — модель/поля (при изменении схемы — миграция, п.2).
2. `uv run alembic revision --autogenerate -m "..."`, проверить файл, `alembic upgrade head`.
3. `dao/` — при необходимости методы в DAO (или переиспользуйте `BaseDAO`).
4. `services/` — DTO + бизнес-логика + доменные исключения.
5. `schemas/` — Request/Response Pydantic-модели.
6. `routes/` — эндпоинт; ошибки → `HTTPException` с корректным статусом.
7. DI-фабрика сервиса в `dependencies/` (если новая).
8. Защита: `Depends(get_current_user)` или `Perm("code")`.
9. Проверить руками через Swagger (`/api/v1/<service>/docs`).

### Добавить страницу на фронтенде

1. Компонент в `src/components/`.
2. Маршрут в `src/router/index.js` c `meta: { requiresAuth: true }`.
3. API-модуль в `src/api/` (через `createApiClient`), если нужен новый домен.
4. Состояние — в Pinia-сторе, не в компоненте, если оно переиспользуется.

---

## 9. Текущее состояние и планы

### ✅ Аутентификация через service-auth (работает)

**Аутентификация реализована в `service-auth`** и используется как фронтендом, так и сервисом-crm.

**Как это работает через nginx:**

1. **Фронтенд → nginx → service-auth**:
   - `POST /api/v1/auth/login` → nginx `proxy_pass http://auth_backend/;` → service-auth:8000/login ✅

2. **service-crm → service-auth (напрямую, без nginx)**:
   - `GET /introspect?permission=list_users` → service-auth:8000/introspect ✅
   - Реализовано через `AuthProxy` в `src/handlers/auth_proxy.py`

**Ближайший план: вынести аутентификацию за API Gateway:**

1. Развить `infra/nginx` в полноценный **API Gateway**: терминация и валидация JWT (introspection / `auth_request` → `service-auth`), единый префикс `/api/v1/*`.
2. `service-auth` становится **единственным** источником регистрации/логина/сессий (Redis).
3. `service-crm` и `service-commercial` **перестают содержать auth-эндпоинты** — принимают только проверенные заголовки пользователя от gateway (`X-User-ID` и т.п.) или валидируют JWT локально по общему секрету/JWKS.
4. Фронтенд переключается с `/api/v1/crm/auth/*` на `/api/v1/auth/*`.

### Асpirational-фичи README, которых НЕТ в коде

Не ссылайтесь на них как на существующие: Kafka + Schema Registry + Outbox, WebSocket Gateway, Prometheus/Grafana, Testcontainers, AES-шифрование PII, Rate Limiting, Circuit Breaker. Также `service-commercial` — пустой каталог.

### Известные огрехи инфраструктуры

- Локальный `.env` обязателен для `make up` (compose подключает его через `env_file`), но **в образы он больше не копируется**: Dockerfile не содержит `COPY .env`, а `.dockerignore` исключает его — секреты не запекаются в слои образа.
- Redis работает с паролем (`REDIS_PASSWORD=redispass`, dev-дефолт задан в `docker-compose.yml`) и volume `redis_data` — сессии переживают пересоздание контейнера. При смене пароля меняйте синхронно: compose + `.env` сервисов crm и auth (`settings.py` подставляет его в `redis_url`).
- Порты БД не публикуются на хост (только `expose` внутри compose-сети); `.env.example` используют хосты `db-crm`/`db-customers`. Для ручного доступа: `docker compose exec db-crm psql -U postgres -d db-crm`.
- Сервисы и БД связаны через `depends_on` с `condition: service_healthy`; у backend-сервисов есть healthcheck по `/health`.
- `service-auth` использует общую БД `db-crm` — при изменении моделей пользователей синхронизируйте миграции обоих сервисов.
- Фронт кладёт в `Authorization` «сырой» токен без `Bearer ` — при добавлении стандартных middleware/OAuth2-схем это нужно учитывать.
- `POSTGRES_ECHO` в dev может быть `True` — шумный SQL-лог в консоли сервиса, это норма.

### Осознанно отложенные проблемы (техдолг)

- **service-customers не защищён**: CRUD эндпоинты клиентов не требуют токена. План — закрыть на уровне API Gateway вместе с миграцией auth (см. выше).
- **Тестов нет**: pytest/pytest-asyncio/aiosqlite в dev-зависимостях, но каталогов `tests/` в сервисах ещё нет (`make test` вернёт ошибку «no tests ran»).
- **Копипаста общего кода** между сервисами (`dao/base.py`, `db_dependency`, `models/mixins.py`, `handlers/auth.py`) — кандидат в общий shared-пакет.
- **Межсервисного взаимодействия нет**: ни REST-клиентов, ни событийной шины (Kafka — только в планах).
- `service-auth`: `logout` принимает `session_id`-заглушку, `register_confirm` без логики; фронтендом не используется (см. выше про gateway).
- Seed тестовых пользователей выполняется миграцией (`seed_test_users`), отладочные роуты `routes/testing.py` живут в прод-коде.
- CORS-ориджины захардкожены в `main.py` сервисов; в `db_dependency` используется `print()` вместо logging.
- Frontend в compose — Vite dev-сервер (`target=development`), production-сборки пока нет.

---

## 10. Быстрая шпаргалка для агента

- Backend-изменения → всегда по слоям, эталон — `service-crm`; не нарушать направление зависимостей.
- Тесты/линтер, если контейнер запущен: `docker compose run --rm service-crm uv run pytest -v` / `uv run ruff check .`.
- Любые новые env-переменные → `settings.py` + `.env.example` (и запустить `make downup`/пересборку).
- Комментарии/докстринги — на русском; код, идентификаторы — на английском.
- Не коммитить `.env` (проверьте `.gitignore`), не коммитить миграции без их проверки на чистой БД.
- Сомневаетесь в auth-фичах → перечитайте раздел 9: auth дублируется, идёт миграция на API Gateway.