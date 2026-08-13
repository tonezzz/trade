---
title: Trade Stack Containerization with Shared Postgres
description: How the Trade API and automation containers are deployed using the existing Postgres container and the key configuration changes involved.
tags: [trade, docker, postgres, containerization, automation]
created: 2026-08-13
updated: 2026-08-13
category: operations
related: [config/infrastructure.yml, config/ssot.health.yml, docker-compose.yml, Dockerfile]
search_keywords: [trade, docker compose, postgres, trade-api, trade-automation, chaba, web_default]
---

# Trade Stack Containerization with Shared Postgres

**Abstract**: The Trade stack now runs as two Docker Compose containers (`trade-api` and `trade-automation`) that share the existing `postgres` container on the `web_default` network. The legacy FastAPI entry point was renamed from `src/api.py` to `src/legacy_api.py` to avoid clashing with the `src/api/` package.

## Overview

The Trade system is split into three concerns:

- **UI** — still served by Caddy from `/srv/public/apps/trade`.
- **API** — `trade-api` container (`uvicorn src.legacy_api:app`).
- **Automation** — `trade-automation` container (`python scripts/auto_update.py --scheduled`).

Both backend containers share a single PostgreSQL database (`dollar_prices`) on the same `postgres` instance used by the chaba web stack.

## Purpose

- Use the existing Postgres instead of SQLite for production-like concurrency and reliability.
- Run API and automation as separate containers so one crashing does not take down the other.
- Keep the UI, API, and automation isolated while still deploying with one `docker compose up` command.

## Key Files

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Defines `trade-api`, `trade-automation`, networking on `web_default`, and Postgres env vars. |
| `Dockerfile` | Builds the shared image; `CMD` is `uvicorn src.legacy_api:app`. |
| `.env` | Holds `DB_PASSWORD`, `ALPHA_VANTAGE_API_KEY`, `FRED_API_KEY`, etc. (gitignored). |
| `.env.example` | Template showing `DB_HOST=postgres` and `DB_USER=chaba`. |
| `requirements.txt` | Python deps, including `requests` for Alpha Vantage. |
| `src/legacy_api.py` | Legacy FastAPI app with `/api/health` and UI chart endpoints. |
| `config/infrastructure.yml` | SSOT documenting the Docker Compose and database configuration. |
| `config/ssot.health.yml` | Health check definitions for the containerized services. |

## Implementation/Architecture

- `trade-api` builds from the local `Dockerfile` and is tagged `trade-trade-api`.
- `trade-automation` reuses the same image (`image: trade-trade-api`) with a different `command`.
- Both connect to `postgres:5432` with `DB_NAME=dollar_prices` and `DB_USER=chaba`.
- The database and tables are created once with `Base.metadata.create_all()`.

### Configuration

```yaml
# docker-compose.yml
services:
  trade-api:
    env_file: [.env]
    environment:
      - DB_TYPE=postgresql
      - DB_HOST=postgres
      - DB_PORT=5432
      - DB_NAME=dollar_prices
      - DB_USER=chaba
  trade-automation:
    image: trade-trade-api
    command: ["python", "scripts/auto_update.py", "--scheduled"]
    healthcheck:
      disable: true

networks:
  web_default:
    external: true
```

### Integration Points

- Caddy at `:8080` proxies `/apps/trade/api/*` to `host.docker.internal:9000`.
- Caddy serves `/apps/trade/*` static UI files.
- The `postgres` container is on `web_default`; Trade containers join the same network.

### Data Flow

1. `trade-automation` schedules daily/weekly/monthly jobs.
2. Jobs download data via Alpha Vantage, FRED, MetalPrices, etc.
3. Data is written to `dollar_prices` Postgres database.
4. `trade-api` reads the same database and serves REST/WebSocket endpoints.

## Operational Procedures

### Setup/Installation

```bash
cd /home/tony/CascadeProjects/trade
# Create database and tables (run once)
docker exec postgres psql -U chaba -c "CREATE DATABASE dollar_prices;"
docker compose run --rm trade-api python -c "from src.database import db; db.init_db()"
# Start the stack
docker compose up -d --build
```

### Usage

```bash
docker compose ps
curl -s http://tony-omen.local:9000/api/health
docker compose logs -f trade-api
docker compose logs -f trade-automation
```

### Maintenance

- Rebuild and restart: `docker compose up -d --build`
- Restart a single service: `docker compose restart trade-api`
- Pull fresh data: `docker exec trade-automation python scripts/auto_update.py --run-once`

## Troubleshooting

### Issue: `Attribute "app" not found in module "src.api"`
- **Symptoms**: `trade-api` container exits immediately with that error.
- **Causes**: `src/api/__init__.py` package shadows the legacy `src/api.py` module.
- **Solutions**: Rename `src/api.py` to `src/legacy_api.py` and update `Dockerfile` `CMD` to `uvicorn src.legacy_api:app`.

### Issue: `ModuleNotFoundError: No module named 'requests'`
- **Symptoms**: `trade-automation` fails to start.
- **Causes**: `requests` was missing from `requirements.txt`.
- **Solutions**: Add `requests>=2.31.0` to `requirements.txt` and rebuild.

### Issue: `trade-automation` marked unhealthy
- **Symptoms**: Container flaps or shows `unhealthy`.
- **Causes**: The Dockerfile healthcheck checks `/api/health`, but the automation container has no API.
- **Solutions**: Add `healthcheck: { disable: true }` in `docker-compose.yml` for `trade-automation`.

## Related Documentation

- **Infrastructure SSOT**: `config/infrastructure.yml` — Docker and database configuration.
- **Health SSOT**: `config/ssot.health.yml` — Health check endpoints and recovery notes.
- **Docker Compose**: `docker-compose.yml` — Runtime service definitions.

## Change History

| Date | Change | Author |
|------|--------|--------|
| 2026-08-13 | Initial containerization to Postgres with separate API and automation containers | Devin |
