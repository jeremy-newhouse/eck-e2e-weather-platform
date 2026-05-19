---
status: accepted
type: prd
date: 2026-05-19
---

# Product Requirements Document — Weather Platform

**Version:** 1.0 | **Date:** 2026-05-19 | **Status:** Accepted

---

## 1. Overview

Weather Platform delivers a real-time weather dashboard with AI chatbot capabilities. Built as a monorepo with a Next.js 16 frontend and FastAPI backend, it ingests live weather data from OpenWeatherMap, stores time-series metrics in TimescaleDB, and exposes an LLM chatbot powered by the Anthropic Claude API.

---

## 2. Architecture Overview

| Layer          | Technology                                                 |
| -------------- | ---------------------------------------------------------- |
| Frontend       | Next.js 16 App Router, TypeScript, Tailwind CSS, Recharts  |
| Backend        | FastAPI (Python), SQLAlchemy async, Alembic, uv            |
| Primary DB     | PostgreSQL 16 (users, sessions, chat history)              |
| Metrics DB     | TimescaleDB (time-series weather metrics)                  |
| Cache/Queue    | Redis (response cache + arq task queue)                    |
| External APIs  | OpenWeatherMap, Anthropic Claude API                       |
| Infrastructure | Docker Compose (local), AWS ECS Fargate + ALB (production) |

---

## 3. Features

### 3.1 Weather Dashboard (P1)

- Display current conditions: temperature, humidity, wind speed/direction, precipitation, UV index
- Location search by city name or coordinates
- Recharts time-series visualizations for historical metrics (24h, 7d, 30d)
- Auto-refresh every 60 seconds via TanStack Query polling

### 3.2 Weather Data Ingestion (P1)

- Scheduled background ingestion via arq every 5–10 minutes
- Store raw + aggregated metrics in TimescaleDB hypertables
- Redis cache layer: 5-minute TTL on weather API responses
- Rate limit enforcement: max 60 OpenWeatherMap calls/min via Redis counter

### 3.3 AI Chatbot (P1)

- Natural language weather queries powered by Claude API
- Streaming responses via Server-Sent Events (SSE)
- Chat history persisted in PostgreSQL per user session
- Context injection: current weather data included in every LLM prompt

### 3.4 User Authentication (P2)

- JWT-based auth (RS256, 15-minute access tokens)
- Refresh tokens in httpOnly cookies (7-day, rotating)
- User registration and login
- Session management tied to chat history

### 3.5 API Layer (P1)

- RESTful FastAPI endpoints with OpenAPI/Swagger docs
- Pydantic v2 request/response validation
- Structured error responses
- Health check endpoint for ALB target group

---

## 4. Non-Functional Requirements

| Category      | Requirement                                                                 |
| ------------- | --------------------------------------------------------------------------- |
| Performance   | p95 API response < 200ms (cached); chat first token < 1s                    |
| Scalability   | Horizontal scaling via ECS Fargate tasks                                    |
| Observability | Structured logging (structlog), OpenTelemetry traces                        |
| Security      | JWT auth, AWS Secrets Manager, CORS allowlist, no wildcard origins          |
| Reliability   | arq dead-letter queue for failed ingestion tasks                            |
| Developer DX  | Full local dev via Docker Compose; hot reload for both frontend and backend |

---

## 5. Tech Decisions (ADR References)

| Decision                 | ADR                                                               |
| ------------------------ | ----------------------------------------------------------------- |
| Tech stack selection     | [ADR 001](../adrs/001-tech-stack-selection.md)                    |
| Modular monolith backend | [ADR 002](../adrs/002-backend-architecture-modular-monolith.md)   |
| JWT authentication       | [ADR 003](../adrs/003-authentication-jwt.md)                      |
| Next.js App Router       | [ADR 004](../adrs/004-frontend-architecture-nextjs-app-router.md) |
| TanStack Query + Zustand | [ADR 005](../adrs/005-state-management-tanstack-query-zustand.md) |
| Security model           | [ADR 006](../adrs/006-security-model-jwt-secrets-manager.md)      |

---

## 6. Quality Gates

| Gate  | Backend               | Frontend            |
| ----- | --------------------- | ------------------- |
| Tests | `uv run pytest`       | `npm test`          |
| Lint  | `uv run ruff check .` | `npm run lint`      |
| Types | `uv run mypy .`       | `npm run typecheck` |

All gates must pass before merge to `dev`. Branch strategy: `feat/WX-XXX-description` → PR → `dev` → `main`.
