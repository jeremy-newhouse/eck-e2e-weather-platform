# Project Constants

Pre-computed task tracker and project values. Referenced by skills and agents.

**Last Updated:** 2026-03-24

---

## Project Identity

| Constant            | Value                                                                                                           | Description                                        |
| ------------------- | --------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| PROJECT_NAME        | Weather Platform                                                                                                | Project display name                               |
| PROJECT_KEY         | WX                                                                                                              | Project identifier                                 |
| PROJECT_DESCRIPTION | Multi-service weather platform with Next.js frontend, FastAPI backend, PostgreSQL, TimescaleDB, and LLM chatbot | Project description                                |
| CONFLUENCE_ENABLED  | false                                                                                                           | Enable Confluence publishing (boolean: true/false) |

---

## Task Tracker Constants

| Constant             | Value                                                       | Description                                                                  |
| -------------------- | ----------------------------------------------------------- | ---------------------------------------------------------------------------- |
| TRACKER_TYPE         | GitHub                                                      | JIRA \| GitHub \| Linear \| none                                             |
| TRACKER_URL          | https://github.com/jeremy-newhouse/eck-e2e-weather-platform | Task tracker instance URL                                                    |
| BOARD_ID             |                                                             | Agile board ID                                                               |
| BOARD_NAME           |                                                             | Board display name                                                           |
| ASSIGNEE_ID          |                                                             | Default assignee ID                                                          |
| ASSIGNEE_NAME        | E2E Tester                                                  | Default assignee name                                                        |
| TRACKER_SYNC_ENABLED | false                                                       | Set by preflight, not user-configurable. true when tracker preflight passes. |

---

## Repository Paths

| Repository       | Description  | Absolute Path                 |
| ---------------- | ------------ | ----------------------------- |
| Weather Platform | Primary repo | /home/tester/weather-platform |

---

## Branch Configuration

| Branch           | Purpose                 |
| ---------------- | ----------------------- |
| main             | Production (protected)  |
| dev              | Integration (protected) |
| feat/WX-XXX-name | Feature development     |

---

## Quality Gate Configuration

| Gate  | Backend Command | Frontend Command  |
| ----- | --------------- | ----------------- |
| Tests | pytest          | npm test          |
| Lint  | ruff check .    | npm run lint      |
| Types | mypy src/       | npm run typecheck |

---

## Project Configuration

| Constant     | Value    | Description                                          |
| ------------ | -------- | ---------------------------------------------------- |
| PROJECT_TYPE | 4        | Project type level (1-5)                             |
| DEV_RIGOR    | standard | Auto-derived from project type (do not set directly) |

---

## Learning Configuration

| Constant          | Value    | Description                                             |
| ----------------- | -------- | ------------------------------------------------------- |
| LEARNING_AUTONOMY | observer | Learning autonomy level (observer\|advisor\|autonomous) |

---

## Standards Repository

| Constant              | Value                                                    | Description                   |
| --------------------- | -------------------------------------------------------- | ----------------------------- |
| STANDARDS_REPO_URL    | https://github.com/evolvconsulting/evolv-coder-standards | GitHub repo URL for standards |
| STANDARDS_REPO_BRANCH | main                                                     | Branch to pull from           |

---

## Loop & Retry Configuration

| Constant                  | Value    | Description                                     |
| ------------------------- | -------- | ----------------------------------------------- |
| MAX_GATE_RETRIES          | 3        | Max re-runs for review gates                    |
| MAX_APPROVAL_ROUNDS       | 10       | Max approval iterations                         |
| MAX_AGENT_LOOP_ITERATIONS | 5        | Default for agent:loop primitive                |
| MAX_AGENT_LOOP_HARD_CAP   | 10       | Absolute ceiling for agent:loop                 |
| MAX_SPRINT_TASK_RETRIES   | 2        | Max retries per task in dev-sprint              |
| LOOP_EXHAUSTION_ACTION    | escalate | What happens at max: escalate (to user) or fail |

---

## Code Review Configuration

| Constant           | Value         | Description                                       |
| ------------------ | ------------- | ------------------------------------------------- |
| CODE_REVIEW_PLUGIN | not-installed | PR code review plugin: installed \| not-installed |

---

## Plugin & Backend Overrides

| Constant                 | Value | Description                            |
| ------------------------ | ----- | -------------------------------------- |
| TRACKER_BACKEND_OVERRIDE |       | Custom tracker backend (empty=default) |
| DOC_BACKEND_OVERRIDE     |       | Custom docs backend (empty=default)    |
