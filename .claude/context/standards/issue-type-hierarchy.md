# Issue Type Hierarchy

Authoritative specification for issue types, their relationships, and tracker-platform mappings in the evolv-coder-kit ecosystem.

**Version:** 0.4.0

---

## Issue Types

| Type        | Purpose                                          | When to Create            |
| ----------- | ------------------------------------------------ | ------------------------- |
| **Epic**    | Large initiative spanning multiple features      | Roadmap planning          |
| **Feature** | Atomic deliverable tracked through SDD lifecycle | `/eck:create-feature`     |
| **Task**    | Implementation work item within a feature        | `/eck:develop` (TASKS.md) |
| **Bug**     | Defect found during validate or production       | `/eck:validate` or ad-hoc |

---

## Relationships

```
Epic
 └── Feature (1+)
      ├── docs folder: FEAT-<issue>-<slug>/
      ├── lifecycle.json entry (exactly 1)
      ├── tracker issue (optional, 0 or 1)
      └── Task (1+, generated during develop phase)
```

- **Epic** contains 1 or more Features
- **Feature** contains 1 or more Tasks (generated during the develop phase via TASKS.md)
- **Feature** has exactly 1 docs folder (`FEAT-<issue>-<slug>/`)
- **Feature** has exactly 1 `lifecycle.json` entry (keyed by slug)
- **Feature** optionally links to 1 tracker issue
- **Task** belongs to exactly 1 Feature

---

## Tracker Platform Mapping

### JIRA

| Type    | JIRA Mapping         | Notes                                    |
| ------- | -------------------- | ---------------------------------------- |
| Epic    | Epic issue type      | Uses `epic_link` for feature association |
| Feature | Story with epic_link | Or standalone Epic for large features    |
| Task    | Sub-task             | Parented to the Feature Story            |
| Bug     | Bug issue type       | Linked to Feature via `epic_link`        |

### GitHub Issues

| Type    | GitHub Mapping             | Notes                                  |
| ------- | -------------------------- | -------------------------------------- |
| Epic    | Milestone or label `epic`  | Milestones preferred for timeline view |
| Feature | Issue with label `feature` | Created by `/eck:create-feature`       |
| Task    | Issue with label `task`    | Or tracked only in TASKS.md            |
| Bug     | Issue with label `bug`     | Standard GitHub convention             |

### Linear

| Type    | Linear Mapping | Notes                              |
| ------- | -------------- | ---------------------------------- |
| Epic    | Project        | Linear Projects group related work |
| Feature | Issue          | Standard Linear issue              |
| Task    | Sub-issue      | Nested under Feature issue         |
| Bug     | Issue (Bug)    | Uses Linear's Bug label/type       |

### Local (no external tracker)

| Type    | Local Mapping                      | Notes                          |
| ------- | ---------------------------------- | ------------------------------ |
| Epic    | `docs/issues/{PK}-{NNN}.md` (epic) | `type: epic` in frontmatter    |
| Feature | `docs/issues/{PK}-{NNN}.md` (feat) | `type: feature` in frontmatter |
| Task    | TASKS.md entries                   | No separate issue file needed  |
| Bug     | `docs/issues/{PK}-{NNN}.md` (bug)  | `type: bug` in frontmatter     |

---

## Feature Docs Folder Naming

Feature documentation folders follow the `FEAT-<issue>-<slug>/` convention:

- **With issue number:** `FEAT-<issue_number>-<slug>/` (e.g., `FEAT-340-discovery-system/`)
- **Without issue:** `FEAT-<slug>/` (e.g., `FEAT-internal-refactor/`)

The `<slug>` is the kebab-case feature name, matching the lifecycle.json key minus any numeric prefix.

> **Legacy:** Directories named `feat-NN-*` predate v0.7.0 and follow the old sequential numbering convention. These are renamed to `FEAT-<issue>-<slug>/` as part of the v0.7.0 migration.

---

## Cross-Reference Requirements

Every feature should maintain these cross-references:

| Source             | Field / Location        | Links To             |
| ------------------ | ----------------------- | -------------------- |
| `lifecycle.json`   | `issue_number`          | Tracker issue number |
| `lifecycle.json`   | Feature slug key        | Docs folder name     |
| `docs/INDEX.md`    | Feature row link        | Docs folder path     |
| Docs folder README | Issue link in header    | Tracker issue URL    |
| Tracker issue      | Description or comments | Docs folder path     |
