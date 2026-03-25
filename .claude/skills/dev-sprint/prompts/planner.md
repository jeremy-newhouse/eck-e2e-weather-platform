---
version: "0.4.0"
disable-model-invocation: false
---

# Planning Prompt Template

This prompt is used internally by dev-sprint during Stage 2 when analyzing dependencies and creating the execution plan.

## Dependency Analysis Prompt

When building the task dependency graph:

```
## Task Dependency Analysis

For each task in the sprint:
1. Parse tracker "is blocked by" links
2. Build adjacency list representation
3. Detect circular dependencies (fail if found)
4. Perform topological sort for execution order
5. Identify tasks that can run in parallel

### Topological Sort Algorithm
- Use Kahn's algorithm or DFS-based approach
- Ensure all dependencies satisfied before scheduling task
- Group independent tasks for potential parallel execution

### Output Format
- Ordered list of tasks respecting all dependencies
- Clear indication of which tasks have dependencies
- Identification of parallel execution opportunities
```

## Execution Plan Output Template

```markdown
## Sprint Execution Plan

**Sprint:** {epic-key} - {epic-name}
**Tasks:** {total} total ({completed} completed, {remaining} remaining)
**Feature Spec:** SPEC-FEAT-{number}

### Execution Order

| Order | Task ID              | Description | Dependencies         | Status   |
| ----- | -------------------- | ----------- | -------------------- | -------- |
| 1     | WX-121    | {summary}   | -                    | {status} |
| 2     | WX-122    | {summary}   | WX-121    | {status} |
| 3     | WX-123    | {summary}   | WX-122    | {status} |
| 4     | WX-124    | {summary}   | WX-122    | {status} |

### Recommended Agent Assignments

| Task              | Developer           | Simplifier      | Reviewer               |
| ----------------- | ------------------- | --------------- | ---------------------- |
| WX-121 | {agent-from-prefix} | code-simplifier | {reviewer-from-prefix} |
| WX-122 | {agent-from-prefix} | code-simplifier | {reviewer-from-prefix} |

**Note:** The orchestrator (dev-sprint) dispatches developer agents directly based on task prefix, then runs: code-simplifier → quality gates → reviewer → QA.

### Parallel Execution Opportunities

The following tasks have no dependencies and could theoretically run in parallel:

- None (sequential execution required)

OR

- WX-123 and WX-124 (both depend only on WX-122)

**Note:** Current development executes tasks sequentially. Parallel execution may be added in future versions.
```
