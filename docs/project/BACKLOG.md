# Feature Backlog — Weather Platform

**Last Updated:** 2026-05-19 | **Project:** WX

Feature backlog populated by `/start-project` and managed via `/eck:select-feature`.

| #   | Feature                    | Description                                                         | Size | Priority | Issue                                                                        | Status  |
| --- | -------------------------- | ------------------------------------------------------------------- | ---- | -------- | ---------------------------------------------------------------------------- | ------- |
| 1   | Project Scaffold           | Monorepo structure, Docker Compose, env config, CI skeleton         | M    | P1       | [#45](https://github.com/jeremy-newhouse/eck-e2e-weather-platform/issues/45) | backlog |
| 2   | Weather Data Ingestion     | OpenWeatherMap integration, arq scheduler, TimescaleDB, Redis cache | M    | P1       | [#46](https://github.com/jeremy-newhouse/eck-e2e-weather-platform/issues/46) | backlog |
| 3   | Weather Dashboard UI       | Next.js dashboard with Recharts charts, city search, 60s polling    | L    | P1       | [#47](https://github.com/jeremy-newhouse/eck-e2e-weather-platform/issues/47) | backlog |
| 4   | LLM Chatbot                | Claude API integration, SSE streaming, PostgreSQL chat history      | M    | P1       | [#48](https://github.com/jeremy-newhouse/eck-e2e-weather-platform/issues/48) | backlog |
| 5   | User Authentication        | JWT auth, refresh tokens, registration, login, session management   | M    | P2       | [#49](https://github.com/jeremy-newhouse/eck-e2e-weather-platform/issues/49) | backlog |
| 6   | API Health & Observability | Health check endpoint, structlog, OpenTelemetry traces              | S    | P2       | [#50](https://github.com/jeremy-newhouse/eck-e2e-weather-platform/issues/50) | backlog |
| 7   | AWS ECS Fargate Deployment | ECS task definitions, ALB config, Secrets Manager, deploy pipeline  | M    | P3       | [#51](https://github.com/jeremy-newhouse/eck-e2e-weather-platform/issues/51) | backlog |

## Suggested Order

1. **Project Scaffold** — unblocks everything else
2. **Weather Data Ingestion** — core data pipeline
3. **Weather Dashboard UI** — primary user-facing surface
4. **LLM Chatbot** — differentiating feature
5. **User Authentication** — gates chat history per user
6. **API Health & Observability** — production readiness gate
7. **AWS ECS Fargate Deployment** — final production deployment

> Use `/eck:create-feature` to add new features to the backlog.
