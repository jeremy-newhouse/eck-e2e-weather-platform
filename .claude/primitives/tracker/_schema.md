---
name: tracker:schema
description: Interface contract for tracker domain operations
version: "0.4.3"
type: schema
---

# Tracker Schema

Defines the common interface for tracker operations across all backends. Skills read this to understand parameters and expected output without needing to inspect individual backend primitives.

## issue-create

| Parameter   | Type     | Required | Description                   |
| ----------- | -------- | -------- | ----------------------------- |
| title       | string   | Yes      | Issue title/summary           |
| description | string   | No       | Issue body (markdown)         |
| labels      | string[] | No       | Labels to apply               |
| assignee    | string   | No       | Assignee identifier           |
| parent      | string   | No       | Parent issue/epic ID          |
| type        | string   | No       | Issue type (Story, Task, Bug) |

**Returns:** `id` (string), `url` (string)

**Backend parameter mapping:**

- JIRA: `title` -> `summary`, `assignee` -> `assignee_id`, `parent` -> `parent_key`
- GitHub: `title` -> `title`, `description` -> `body`
- Linear: `title` -> `title`, `description` -> `description`
- Local: `title` -> `title`, `description` -> `description`

## issue-read

| Parameter | Type   | Required | Description      |
| --------- | ------ | -------- | ---------------- |
| id        | string | Yes      | Issue identifier |

**Returns:** `id`, `title`, `description`, `status`, `assignee`, `labels`, `url`

## issue-update

| Parameter   | Type     | Required | Description         |
| ----------- | -------- | -------- | ------------------- |
| id          | string   | Yes      | Issue identifier    |
| title       | string   | No       | Updated title       |
| description | string   | No       | Updated description |
| labels      | string[] | No       | Updated labels      |
| assignee    | string   | No       | Updated assignee    |

**Returns:** `id`, `url`

## issue-search

| Parameter | Type   | Required | Description                   |
| --------- | ------ | -------- | ----------------------------- |
| query     | string | Yes      | Search query or JQL           |
| max       | number | No       | Maximum results (default: 20) |

**Returns:** Array of `{ id, title, status, assignee, url }`

## issue-transition

| Parameter     | Type   | Required | Description        |
| ------------- | ------ | -------- | ------------------ |
| id            | string | Yes      | Issue identifier   |
| target_status | string | Yes      | Target status name |

**Returns:** `id`, `previous_status`, `new_status`

## comment-add

| Parameter | Type   | Required | Description             |
| --------- | ------ | -------- | ----------------------- |
| id        | string | Yes      | Issue identifier        |
| body      | string | Yes      | Comment body (markdown) |

**Returns:** `comment_id`, `issue_id`

## Used By

- deploy-tracker
- dev-task
- dev-pr
- dev-task
- dev-feature
- design-feature
