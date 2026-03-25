# Changelog

All notable changes to Weather Platform are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [v0.1.0] — 2026-03-25

### Features

- Add backend project scaffold with FastAPI, SQLAlchemy, and Alembic (WX-6)
- Add database models and Alembic migrations for PostgreSQL and TimescaleDB (WX-5)
- Add weather service and router with OpenWeatherMap integration (WX-7; AC-1, AC-2, AC-3, AC-4)
- Add metrics service and router for time-series weather data (WX-8; AC-5)
- Add chat service and router with Claude API LLM integration (WX-9; AC-7, AC-8)
- Add full health endpoints with database connectivity checks (WX-10; AC-9, AC-10)
- Add frontend project scaffold and home page with Next.js 16 and Tailwind (WX-11)
- Add dashboard page with Recharts weather and metrics visualizations (WX-12; AC-6)
- Add chat page with ChatContainer component for LLM conversation (WX-13; AC-7, AC-8 frontend)
- Add Docker Compose setup with service health checks and test compose configuration (WX-14)
- Add ECS Fargate deployment configuration with Application Load Balancer routing (WX-15; AC-13)
- Add frontend test suite achieving ≥70% coverage (WX-17; AC-6, AC-14, AC-15)

### Maintenance

- Seed project constants for CI and agent configuration
- Seed Feature Requirements Document (FRD) for FEAT-001
- Update lifecycle, feature flags, and FRD for FEAT-001 deployment
- Simplify test_chat_integration imports (refactor)
