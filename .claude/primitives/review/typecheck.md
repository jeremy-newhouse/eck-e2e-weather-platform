---
name: core/review:typecheck
description: Run type checker
version: "0.4.0"
---

# Typecheck

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| target | string | Yes | Target codebase: `backend` or `frontend` |

## Implementation

Backend:

```bash
cd /home/tester/weather-platform/backend
uv run mypy .
```

Frontend:

```bash
cd /home/tester/weather-platform/frontend
npm run typecheck
```

## Output

| Field | Type | Description |
|-------|------|-------------|
| errors | array | Type errors with file, line, and message |
| error_count | number | Total number of type errors |
| verdict | string | `PASS` (zero errors) or `FAIL` |

## Errors

| Code | Cause | Recovery |
|------|-------|----------|
| INVALID_TARGET | `target` is not `backend` or `frontend` | Halt and report invalid parameter |
| TOOL_NOT_FOUND | `mypy` or `npm run typecheck` not available | Skip with warning |
| PATH_NOT_FOUND | `/home/tester/weather-platform/backend` or `/home/tester/weather-platform/frontend` does not exist | Halt and report missing path |

## Used By

- `dev-task`
- `validate-code`
- `validate-quality`
