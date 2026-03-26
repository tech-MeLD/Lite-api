# Standard FastAPI Backend

A lightweight but production-aware FastAPI template for a public REST API.

## What Was Added

- Request logging with `X-Request-ID`
- Standardized API error codes and error response shape
- Simple `X-API-Key` protection for public endpoints
- Redis cache for GitHub repository data
- SQLite + SQLModel persistence for weather data
- `pre-commit`, `ruff`, `mypy`, `pytest`
- GitHub Actions CI

## Project Notes

This project intentionally stays small:

- no Alembic
- no RBAC or JWT
- no message queue
- no split into many micro-layers

It is enough for a team to start cleanly, while leaving room to grow.

## API Overview

Public endpoint:

- `GET /api/v1/health`
- `GET /api/v1/health/dependencies`

Protected endpoints:

- `GET /api/v1/external/github/repo-stats?owner=fastapi&repo=fastapi`
- `GET /api/v1/external/weather?latitude=39.9042&longitude=116.4074`
- `GET /api/v1/external/weather/history?limit=20`

Protected endpoints require:

```http
X-API-Key: your-api-key
```

Every response also includes:

```http
X-Request-ID: <uuid>
```

## Error Response Format

```json
{
  "code": "INVALID_API_KEY",
  "message": "Invalid or missing API key",
  "details": null,
  "request_id": "4b9bb7e0-6d44-4d3b-9f34-1f6e0f2d7f58"
}
```

Current error codes:

- `INVALID_API_KEY`
- `VALIDATION_ERROR`
- `UPSTREAM_SERVICE_ERROR`
- `HTTP_ERROR`
- `INTERNAL_SERVER_ERROR`

## Runtime Decisions

### Python Version

Use `Python 3.11.14` as the team baseline.

The version is aligned in:

- `pyproject.toml`
- `.python-version`
- `Dockerfile`
- GitHub Actions

Python should not be managed only as a package dependency. The correct approach is to pin it in tooling, packaging, and container runtime together.

### GitHub Data

GitHub data is not stored in a database. It is cached in Redis with a TTL to reduce upstream requests and lower the chance of abuse.

### Weather Data

Weather data is fetched from the external API and stored in SQLite through SQLModel. Recent records are reused as a simple local cache, and history can be queried through the history endpoint.

## Local Development

```bash
python -m venv .venv
python -m pip install --upgrade pip
python -m pip install -e .[dev]
```

Then prepare `.env` from `.env.example` and run:

```bash
uvicorn app.main:app --reload
```

## Makefile

If your team uses `make`, these commands are now standardized:

```bash
make dev
make run
make check
make docker-up
```

Common targets:

- `make dev`: install app and dev dependencies
- `make run`: start FastAPI in reload mode
- `make lint`: run Ruff
- `make typecheck`: run mypy
- `make test`: run pytest
- `make check`: run lint, typecheck, and tests

On Windows, run them from Git Bash, WSL, or any environment with `make` installed.

## Docker

```bash
docker compose up --build
```

This starts:

- the FastAPI app
- Redis for GitHub cache
- a mounted SQLite data directory for weather records

## Health Checks

- `GET /api/v1/health`: lightweight liveness check
- `GET /api/v1/health/dependencies`: Redis and SQLite dependency check

The dependency health endpoint returns `200` when all dependencies are healthy, and `503` when any dependency is degraded.

## Quality Tools

```bash
pre-commit install
pre-commit run --all-files
ruff check .
mypy app
pytest
```

## CI

GitHub Actions runs:

- `ruff check .`
- `mypy app`
- `pytest`
