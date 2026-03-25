# Contributing to Weather Platform

> A multi-service weather platform with Next.js 16 frontend (App Router, Tailwind, Recharts), FastAPI backend (SQLAlchemy, Alembic), PostgreSQL for persistence, TimescaleDB for time-series weather metrics, OpenWeatherMap API integration, Claude API LLM chatbot, Docker Compose for local dev, and AWS ECS Fargate deployment

---

## Prerequisites

Install project dependencies with `npm install` (frontend) and `uv sync` (backend).

---

## The Contribution Loop

1. **Claim** an issue in [WX on GitHub](https://github.com/jeremy-newhouse/eck-e2e-weather-platform)
2. **Branch** from `dev`:
   ```bash
   git checkout dev && git pull
   git checkout -b feat/WX-XXX-short-description
   ```
3. **Implement** your changes (run quality gates before pushing)
4. **Open PR** against `dev`

---

## Branch Conventions

| Prefix    | Purpose            | Example                                   |
| --------- | ------------------ | ----------------------------------------- |
| `feat/`   | New features       | `feat/WX-42-user-auth`         |
| `fix/`    | Bug fixes          | `fix/WX-51-login-redirect`     |
| `hotfix/` | Production patches | `hotfix/WX-99-session-timeout` |

All branches include the tracker issue ID for traceability.

---

## Commit Format

```
feat(WX-XXX): short description of change

Longer explanation if needed. Focus on *why*, not *what*.

Refs: WX-XXX
```

| Type       | When                                 |
| ---------- | ------------------------------------ |
| `feat`     | New feature or capability            |
| `fix`      | Bug fix                              |
| `refactor` | Code restructure, no behavior change |
| `docs`     | Documentation only                   |
| `test`     | Test additions or fixes              |
| `chore`    | Build, CI, or tooling changes        |

---

## Quality Gates

Run these before opening a PR:

| Gate  | Backend                  | Frontend                 |
| ----- | ------------------------ | ------------------------ |
| Tests | `uv run pytest`      | `npm test`      |
| Lint  | `uv run ruff check .`      | `npm run lint`      |
| Types | `uv run mypy .` | `npm run typecheck` |

All gates must pass before merge.

---

## Pull Requests

- Target branch: `dev`
- Title matches commit format: `feat(WX-XXX): description`
- Link the tracker issue in the PR body
- Link the feature spec (if applicable)
- Request review from at least one team member

---

## Using ECK Skills

If this project uses [evolv-coder-kit](https://github.com/evolvconsulting/evolv-coder-kit), these slash commands streamline the workflow:

| Command                               | Purpose                                    |
| ------------------------------------- | ------------------------------------------ |
| `/{PK}:design-feature <desc>`         | Design a feature (research, design, tasks) |
| `/{PK}:dev-feature WX-XXX` | Implement all tasks under an epic          |
| `/{PK}:dev-task WX-XXX`    | Implement a single task (TDD)              |
| `/{PK}:validate-quality`              | Run all quality gates                      |

> Full workflow details: [development-workflow.md](development-workflow.md)

---

## Further Reading

| Document                                           | Purpose                                                 |
| -------------------------------------------------- | ------------------------------------------------------- |
| [development-workflow.md](development-workflow.md) | Two-session model, agent dispatch, full workflow spec   |
| [project-constitution.md](project-constitution.md) | Architecture principles, security, testing requirements |
| [CLAUDE.md](CLAUDE.md)                             | AI agent configuration, slash commands, hooks           |
| [docs/INDEX.md](docs/INDEX.md)                     | Documentation index (if available)                      |
