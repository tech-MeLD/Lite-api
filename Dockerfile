FROM python:3.11.14-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    APP_ENV=production \
    DEBUG=false \
    LOG_LEVEL=INFO \
    REDIS_URL=redis://redis:6379/0 \
    SQLITE_URL=sqlite+aiosqlite:///./data/weather.db \
    GITHUB_CACHE_TTL_SECONDS=300 \
    WEATHER_CACHE_TTL_SECONDS=1800 \
    REQUEST_TIMEOUT_SECONDS=10

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY app ./app
RUN mkdir -p /app/data

RUN python -m pip install --upgrade pip \
    && python -m pip install .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
