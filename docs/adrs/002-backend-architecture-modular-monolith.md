---
status: accepted
type: adr
date: 2026-05-19
---

# ADR 002: Backend Architecture — Modular Monolith

## Status

Accepted

## Context

The Weather Platform has four distinct functional domains: weather data ingestion, LLM chatbot, user management, and metrics/analytics. We considered microservices (one service per domain) versus a modular monolith (single deployable with internal module boundaries).

At pilot/beta scale the team is small (1-3 developers), request volume is low (< 1000 RPM), and iteration speed is critical. Cross-domain operations (e.g., chatbot referencing recent weather data) are frequent.

## Decision

Adopt a modular monolith: a single FastAPI application with explicit internal module boundaries enforced by directory structure and import conventions.

**Module boundaries:**

| Module    | Responsibility                                        |
| --------- | ----------------------------------------------------- |
| `weather` | OpenWeatherMap ingestion, caching, forecast queries   |
| `chatbot` | Claude API orchestration, conversation management     |
| `users`   | Registration, authentication, profile management      |
| `metrics` | TimescaleDB writes, aggregation, dashboarding queries |

**Enforcement rules:**

- Each module owns its own router, schemas, service layer, and repository.
- Cross-module communication happens only through explicit service interfaces, never direct repository access.
- Shared kernel (auth context, common models, configuration) lives in a `core` package.

**Extraction triggers -- migrate to microservices when:**

- A single module requires independent scaling (e.g., weather ingestion exceeds 10x other traffic).
- A module needs a different deployment cadence (e.g., chatbot model upgrades weekly while others are stable).
- Team grows beyond 5 engineers and module ownership boundaries cause merge contention.

## Consequences

- Single deployment simplifies CI/CD, observability, and local development.
- Cross-module calls are in-process function calls (microsecond latency, no serialization overhead).
- Risk of coupling if import boundaries are not enforced; mitigated by linting rules and code review.
- Extraction to microservices later requires refactoring service interfaces to network calls, but the boundary design minimizes this cost.
