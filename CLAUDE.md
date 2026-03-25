# CLAUDE.md

A multi-service weather platform with Next.js 16 frontend (App Router, Tailwind, Recharts), FastAPI backend (SQLAlchemy, Alembic), PostgreSQL for persistence, TimescaleDB for time-series weather metrics, OpenWeatherMap API integration, Claude API LLM chatbot, Docker Compose for local dev, and AWS ECS Fargate deployment

## What This Repo Is

<!-- Describe the repository's purpose and what it contains -->

| Repo | Contains | Purpose |
| --- | --- | --- |
| `Weather Platform` | {REPO_CONTENTS} | {REPO_PURPOSE} |

## Governance

Principles, constraints, and invariants are governed by `.claude/project-constitution.md` (rarely changes). This file (`CLAUDE.md`) contains operational instructions and procedures (changes with features). Pre-computed values live in `.claude/project-constants.md` (changes with config). To amend the constitution, see its S8 Amendment Process.

## Directory Structure

```
Weather Platform/
├── .claude/                    # AI agent infrastructure
│   ├── agents/                 # Agent definitions
│   ├── skills/                 # Skill definitions
│   ├── hooks/                  # Hook scripts
│   ├── primitives/             # Primitive operations
│   ├── output-modes/           # Mode definitions
│   ├── heuristics/             # Learning pipeline
│   ├── context/                # Standards + project context
│   ├── scripts/                # Utility scripts
│   ├── settings.json           # Hook config
│   ├── settings.local.json     # Project permissions
│   ├── project-constitution.md # Governing principles (top authority)
│   └── project-constants.md    # Pre-computed values for skills/agents
├── docs/                       # Documentation
│   ├── guides/                 # Contributing guides + workflow docs
│   ├── project/                # Project docs (BRD, PRD, backlog)
│   ├── adrs/                   # Architecture Decision Records
│   └── INDEX.md                # Documentation index
└── CLAUDE.md                   # This file
```

## Development Workflow

Two-session model separating planning from implementation:

| Session | Command | Purpose |
| --- | --- | --- |
| **A** (Planning) | `/WX:design-feature <desc>` | Research, design, document, create tasks. STOPS after. |
| **B** (Implementation) | `/WX:dev-feature WX-XXX` | Execute all tasks under an epic |
| **B** (Single issue) | `/WX:dev-task WX-XXX` | Execute a single task with TDD |

Full workflow docs: `docs/guides/development-workflow.md`

## Agent Selection

| Prefix | Agent | Repo |
| --- | --- | --- |
| DB- | database-specialist | Weather Platform |
| BE- | backend-developer | Weather Platform |
| FE- | frontend-developer | Weather Platform |
| UI- | frontend-designer | Weather Platform |
| BOT- | bot-developer | Weather Platform |
| DOC- | technical-writer | Weather Platform |
| INFRA- | devops-engineer | Weather Platform |
| SEC- | security-specialist | Weather Platform |
| QA- | integration-qa | varies |

## Source of Truth

| Topic | File |
| --- | --- |
| Constitution | `.claude/project-constitution.md` |
| Project constants | `.claude/project-constants.md` |
| Naming conventions | `.claude/context/standards/naming-conventions.md` |
| Workflow docs | `docs/guides/` |

## Tech Stack

<!-- Populated by /start-project -->
- **Frontend**: {FRONTEND_STACK}
- **Backend**: {BACKEND_STACK}
- **Database**: {DATABASE_STACK}

## Quality Gates

See `.claude/project-constants.md` for gate commands.

| Gate | Command |
| --- | --- |
| Tests | `npm test / uv run pytest` |
| Lint | `npm run lint / uv run ruff check .` |
| Types | `npm run typecheck / uv run mypy .` |

## Contributing Guide

@docs/guides/CONTRIBUTING.md

## Learned Guidance

@.claude/heuristics/active-guidance.md

---

**Version**: 0.7.1 | **Updated**: 2026-03-25
