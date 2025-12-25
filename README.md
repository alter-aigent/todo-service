# todo-service

FastAPI microservice for managing user tasks.

## Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

export DATABASE_URL='postgresql+asyncpg://postgres:postgres@localhost:5432/todo'
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

## Auth (stub)

Provide one of headers:
- `X-User-Id: <uuid>`
- `X-User-Email: user@example.com`

User is auto-created on first request.

## Endpoints

- `GET /health`
- `POST /tasks`
- `GET /tasks` (filters: `status`, `due_before`, `due_after`, `priority`, pagination: `limit`, `offset`, sort: `sort`)
- `GET /tasks/{task_id}`
- `PATCH /tasks/{task_id}`
- `PATCH /tasks/{task_id}/status`
- `DELETE /tasks/{task_id}`

## Migrations

```bash
alembic upgrade head
```
