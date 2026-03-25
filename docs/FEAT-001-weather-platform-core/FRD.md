---
feature: FEAT-001
revision: 2
date: 2026-03-25
status: Draft
---

# Feature Requirements Document: Weather Platform Core

**Feature ID:** FEAT-001
**Status:** Draft
**Solution Type:** full-stack

---

## Problem Statement

Users need a production-grade, full-stack weather platform that delivers real-time weather data, historical trend visualizations, and an AI-powered conversational interface — deployable locally via Docker Compose and to AWS ECS Fargate for E2E testing and demonstration.

---

## Goals

1. Expose a FastAPI weather endpoint that proxies OpenWeatherMap (via geocoding + One Call API 3.0), caches results for 5 minutes server-side, and stores temperature/humidity/wind_speed metrics to TimescaleDB on each lookup.
2. Serve a Next.js 16 dashboard displaying time-series charts (temperature, humidity, wind speed) with range selection (1h/6h/24h/7d) via TimescaleDB `time_bucket` aggregation.
3. Provide an LLM chatbot at `/chat` backed by the Claude API with live weather context injection and PostgreSQL-persisted conversation history (`chat_sessions` + `chat_messages`).
4. Pass all quality gates: `pytest` (≥80% coverage, unit + integration with live TimescaleDB) and `npm test` (≥70% coverage, Jest + React Testing Library).
5. Run fully in Docker Compose locally (4 services: frontend, backend, PostgreSQL, TimescaleDB); deploy stateless services (frontend, backend) to ECS Fargate with ALB; TimescaleDB runs as a containerized service for MVP.

---

## Non-Goals

- Multi-region deployment
- User authentication (public access for E2E)
- Custom domain / SSL certificate (ALB default URL is sufficient)
- Auto-scaling policies (single task per service)
- Weather alerts or push notifications
- Mobile app or PWA
- Redis or external cache layer (in-memory TTL only for MVP)
- Background ingest queue or worker (synchronous ingest at query time)
- RDS Aurora + TimescaleDB extension migration (deferred to post-MVP)
- Cost optimization beyond basic Fargate pricing

---

## Architecture Overview

```
┌──────────────────┐     ┌──────────────────┐
│  Next.js Frontend │────▶│  FastAPI Backend  │
│  (Port 3000)      │     │  (Port 8000)      │
└──────────────────┘     └────────┬─────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼              ▼
             ┌───────────┐ ┌───────────┐ ┌─────────────┐
             │ PostgreSQL │ │TimescaleDB│ │OpenWeatherMap│
             │ (Port 5432)│ │(Port 5433)│ │   API        │
             └───────────┘ └───────────┘ └─────────────┘
                                              ▲
                                              │
                                        ┌─────────┐
                                        │Claude API│
                                        └─────────┘
```

> **Note:** TimescaleDB runs as a containerized service for MVP. This is a stateful container on ECS Fargate (known ops risk). Post-MVP path: migrate to RDS Aurora PostgreSQL + TimescaleDB extension or Timescale Cloud.

---

## Acceptance Criteria

| ID    | Criterion                                                                                                                                                                          | Verification     | Status  |
| ----- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- | ------- |
| AC-1  | Returns JSON {city, temperature, description, humidity, wind_speed, timestamp} from GET /api/weather/{city} after resolving the city to coordinates via OWM geocoding API          | Integration test | Pending |
| AC-2  | Caches weather responses server-side for 5 minutes in an in-memory TTL cache; repeated requests within the TTL return cached data without contacting OWM                           | Integration test | Pending |
| AC-3  | Returns HTTP 404 with a JSON error body when GET /api/weather/{city} is called with an unresolvable city name                                                                      | Integration test | Pending |
| AC-4  | Stores temperature, humidity, and wind_speed in the weather_metrics TimescaleDB hypertable on each successful weather lookup (fields: city, metric_name, value, recorded_at)       | Integration test | Pending |
| AC-5  | Returns time-bucket aggregated metric averages from GET /api/metrics/{city}?range={range} for ranges 1h, 6h, 24h, 7d                                                               | Integration test | Pending |
| AC-6  | Displays Recharts line charts for temperature, humidity, and wind speed at /dashboard with a working range selector (1h / 6h / 24h / 7d)                                           | E2E test         | Pending |
| AC-7  | Sends user message with current weather context JSON injected into the Claude API system prompt and returns a conversational response                                              | Integration test | Pending |
| AC-8  | Persists all chat messages (role, content, created_at) to PostgreSQL chat_sessions and chat_messages tables                                                                        | Integration test | Pending |
| AC-9  | Returns GET /health as {"status":"ok","services":{"postgres":"ok","timescale":"ok"}} with HTTP 200 when all services are reachable                                                 | Unit test        | Pending |
| AC-10 | Returns GET /ready with HTTP 200 when all database connections are established; HTTP 503 otherwise                                                                                 | Unit test        | Pending |
| AC-11 | Creates chat_sessions, chat_messages, cities tables and weather_metrics hypertable via Alembic migrations with indexes on cities(name) and weather_metrics(city, recorded_at DESC) | Unit test        | Pending |
| AC-12 | Starts all 4 Docker Compose services with frontend at :3000, backend at :8000, both databases healthy, and CORS configured to allow requests from localhost:3000                   | Manual test      | Pending |
| AC-13 | Deploys frontend and backend as ECS Fargate services accessible via ALB with passing health checks and secrets sourced from AWS Secrets Manager                                    | Deployment test  | Pending |
| AC-14 | Renders weather search page at / via Next.js server component with city search input, current weather card, and navigation links to /dashboard and /chat                           | E2E test         | Pending |
| AC-15 | Passes uv run pytest with ≥80% backend coverage (unit + integration with live TimescaleDB via TEST_DATABASE_URL) and npm test with ≥70% frontend coverage                          | Unit test        | Pending |

---

## AC Changelog

| Revision | AC-ID       | Change   | Reason                                                                                 |
| -------- | ----------- | -------- | -------------------------------------------------------------------------------------- |
| 2        | AC-1        | Modified | Refined from AC-01: verb-first, OWM geocoding flow made explicit                       |
| 2        | AC-2        | Added    | Split from AC-01: caching behavior separated into its own atomic criterion             |
| 2        | AC-3        | Added    | New error-state criterion: 404 on unresolvable city name (absent from v1)              |
| 2        | AC-4        | Modified | Refined from AC-02: hypertable explicit, field list confirmed                          |
| 2        | AC-5        | Modified | Refined from AC-03 (backend half): time_bucket aggregation made explicit               |
| 2        | AC-6        | Modified | Split from AC-03 (frontend half): Recharts chart rendering separated                   |
| 2        | AC-7        | Modified | Refined from AC-04 (Claude call half): context injection made explicit                 |
| 2        | AC-8        | Modified | Split from AC-04 (persistence half): chat schema (sessions + messages) separated       |
| 2        | AC-9        | Modified | Refined from AC-05 (health half): exact response body specified                        |
| 2        | AC-10       | Modified | Split from AC-05 (ready half): 503 on DB unavailability made explicit                  |
| 2        | AC-11       | Modified | Refined from AC-06: if_not_exists, index specs, and Alembic idiom clarified            |
| 2        | AC-12       | Modified | Refined from AC-07: CORS requirement absorbed from Architecture notes                  |
| 2        | AC-13       | Modified | Refined from AC-08: stateful TimescaleDB container risk acknowledged                   |
| 2        | AC-14       | Modified | Refined from AC-09: server component requirement explicit                              |
| 2        | AC-15       | Modified | Refined from AC-10: uv run pytest, TEST_DATABASE_URL, and live DB requirement explicit |
| 1        | AC-01–AC-10 | Added    | Initial draft: 10 narrative GWT criteria                                               |

---

## Tech Stack

| Component        | Technology              | Version |
| ---------------- | ----------------------- | ------- |
| Frontend         | Next.js (App Router)    | 16.x    |
| UI Framework     | Tailwind CSS            | 3.x     |
| Charts           | Recharts                | 2.x     |
| Backend          | FastAPI                 | 0.110+  |
| ORM              | SQLAlchemy + Alembic    | 2.x     |
| Database         | PostgreSQL              | 16      |
| Time-series      | TimescaleDB             | 2.x     |
| LLM              | Claude API (Anthropic)  | Latest  |
| Weather API      | OpenWeatherMap          | 3.0     |
| Containerization | Docker + Docker Compose | Latest  |
| Deployment       | AWS ECS Fargate + ALB   | —       |
| Secrets          | AWS Secrets Manager     | —       |
| CI/CD            | GitHub Actions          | —       |

---

## Revision History

| Rev | Date       | Author      | Summary                                                                                                                                             |
| --- | ---------- | ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2   | 2026-03-25 | AI-assisted | Quick-pass revision: scope locked (goals/non-goals), ACs converted to canonical table, +5 split/new ACs, all 15 refined for atomicity and precision |
| 1   | 2026-03-25 | AI-assisted | Initial spec: 10 narrative GWT ACs covering weather API, metrics, chatbot, deployment, testing                                                      |
