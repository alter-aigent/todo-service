SHELL := /bin/sh

.PHONY: venv install run docker-up docker-down mig-create mig-up mig-current

venv:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -U pip

install: venv
	. .venv/bin/activate && pip install -r requirements.txt -r requirements-dev.txt

run:
	. .venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down

# Migrations (local venv)
# Usage: make mig-create MSG="create users table"
mig-create:
	. .venv/bin/activate && alembic revision --autogenerate -m "$$MSG"

mig-up:
	. .venv/bin/activate && alembic upgrade head

mig-current:
	. .venv/bin/activate && alembic current


