---
status: accepted
type: adr
date: 2026-05-19
---

# ADR 001: Tech Stack Selection

## Status

Accepted

## Context

Weather Platform requires a backend that handles real-time weather data ingestion, time-series storage, LLM chatbot orchestration, and REST API serving. We need high async throughput for external API calls (OpenWeatherMap, Claude API), strong typing for data contracts, efficient time-series queries, and a deployment model suitable for a pilot/beta with a small team.

Key constraints: the team has Python expertise, the project must reach production quickly, and operational cost must stay low during pilot phase.

## Decision

**FastAPI over Django/Express/Spring:** FastAPI provides native async/await, automatic OpenAPI docs, Pydantic v2 validation, and minimal boilerplate. Django's ORM is synchronous-first and its batteries (admin, templates) are unnecessary. Express lacks built-in validation and type safety. Spring's JVM overhead and verbosity are excessive for a pilot.

**PostgreSQL 16 + TimescaleDB dual-database:** PostgreSQL handles relational data (users, sessions, chat history) with mature tooling. TimescaleDB extends PostgreSQL for time-series weather metrics with automatic partitioning, continuous aggregates, and retention policies -- avoiding a separate TSDB like InfluxDB while keeping the same driver and query language.

**uv over poetry/pip:** uv resolves and installs dependencies 10-100x faster than pip/poetry, supports lockfiles, and integrates virtual environment management. This accelerates CI and local development significantly.

**Docker Compose + ECS Fargate:** Compose provides reproducible local environments matching production topology. Fargate eliminates EC2 instance management, auto-scales on demand, and integrates natively with ALB, Secrets Manager, and CloudWatch -- appropriate for a pilot that may scale without re-architecture.

## Consequences

- Team must learn FastAPI idioms and async patterns (mitigated by strong documentation ecosystem).
- Two logical databases share the PostgreSQL engine, simplifying operations but requiring careful connection pool management.
- uv is newer tooling with smaller community; fallback to pip is trivial if needed.
- Fargate cost-per-task is higher than EC2 at scale, but acceptable for pilot volume and eliminates ops burden.
