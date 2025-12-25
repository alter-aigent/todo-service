# Microservice template (FastAPI + Postgres + SQLAlchemy + Alembic)

Шаблон микросервиса: **FastAPI** (API), **SQLAlchemy async** (ORM), **Postgres** (DB), **Alembic** (миграции), Docker/Docker Compose.

## Быстрый старт (Docker)

1) Поднять сервис вместе с базой:

```bash
make docker-up
```

2) Проверить health-check:

```bash
curl -s http://localhost:8000/health
```

## Быстрый старт (локально, venv)

1) Создать окружение и установить зависимости:

```bash
make install
```

2) Создать `.env` (файл с переменными окружения):

В репозитории лежит пример `example.env` — скопируйте его в `.env` и при необходимости поправьте значения.

3) Запустить сервис:

```bash
make run
```

## Конфигурация

Основные переменные окружения:

- **`DATABASE_URL`**: строка подключения SQLAlchemy (async), пример: `postgresql+asyncpg://postgres:postgres@db:5432/postgres`
- **`APP_NAME`**: имя приложения
- **`API_PREFIX`**: префикс для роутов (по умолчанию пустой)

Настройки читаются в `app/core/config.py`.

## Health-check

Эндпоинт:

- `GET /health` — возвращает `{"status":"ok"}` и делает `SELECT 1` в БД.

## Миграции (Alembic)

Alembic настроен на автогенерацию миграций из `Base.metadata` (модели лежат в `app/models/`).

### Локально (venv)

Перед командами убедитесь что:
- зависимости установлены (`make install`)
- задан `DATABASE_URL` (через `.env` или экспорт переменной)

Создать миграцию (autogenerate):

```bash
make mig-create MSG="create users table"
```

Накатить миграции:

```bash
make mig-up
```

Посмотреть текущую ревизию:

```bash
make mig-current
```

### В Docker

Накатить миграции внутри контейнера приложения:

```bash
docker compose exec app alembic upgrade head
```

Создать миграцию (autogenerate) внутри контейнера:

```bash
docker compose exec app alembic revision --autogenerate -m "message"
```

## Структура

- `app/main.py` — точка входа FastAPI
- `app/api/health.py` — health-check endpoint
- `app/db/session.py` — async engine/session
- `app/models/` — модели
- `alembic/` + `alembic.ini` — миграции
- `docker-compose.yml` — app + postgres + healthchecks
- `docker-compose.server.yml` — деплой на сервер (только app, база уже на сервере)

## CI/CD (GitHub Actions)

В репозитории есть:

- `.github/workflows/ci.yml` — тесты
- `.github/workflows/deploy.yml` — деплой на сервер по SSH (сборка на сервере)

### Настройка для деплоя

1) В GitHub repo → **Settings → Secrets and variables → Actions** добавь:

**Secrets**
- `DEPLOY_SSH_KEY` — приватный SSH ключ для доступа на сервер (например содержимое `~/.ssh/aws_ed25519`)

**Variables**
- `DEPLOY_HOST` — IP/домен сервера (например `63.179.106.169`)
- `DEPLOY_USER` — пользователь (например `ubuntu`)
- `DEPLOY_PORT` — порт SSH (обычно `22`)

Опционально (если хочешь другой каталог на сервере):
- `DEPLOY_DIR` — путь на сервере, куда клонировать репозиторий (по умолчанию `/home/<DEPLOY_USER>/<repo-name>`)

Порт сервиса **захардкожен в пайплайне**: см. `.github/workflows/deploy.yml` (переменная `SERVICE_PORT` внутри script).

2) На сервере должны быть установлены `docker` и `docker compose` (v2).  
В workflow запуск идёт через `sudo`, как ты просил.

3) Деплой запускается при **merge PR в `main`** (или вручную через **Actions → Deploy (server)**).


