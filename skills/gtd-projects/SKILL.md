---
name: projects
description: "Use when the user asks about projects: 'show projects', 'create a project', 'what are my projects', 'project status', 'project actions', 'complete a project', 'put project on hold', or wants to manage multi-step outcomes in their GTD system."
---

# GTD Projects

Manage GTD projects — multi-step outcomes that require more than one action to complete.

## Invocation Triggers

**Explicit:** "show my projects," "create a project," "what are my projects?," "project status," "project actions."

**During processing:** When an inbox item is clearly multi-step, suggest creating a project rather than a single next action.

## When to Create a Project vs. a Next Action

A **project** is any outcome requiring more than one action step. Use this decision guide:

- "Email John about the meeting" → **next action** (single step)
- "Plan the team offsite" → **project** (multiple steps: venue, agenda, invites, etc.)
- "Fix the login bug" → could be either — ask if it involves investigation + fix + test

When in doubt, start with a next action. It can always become a project later.

## Project Operations

### List Projects

```
GET https://gtd-api.fly.dev/projects
Header: X-API-Key: [from TOOLS.md]
```

Returns all projects with stats (action count, completion percentage). Filter by status:
- Active projects (default)
- `?status=on_hold` — projects on hold
- `?status=completed` — completed projects
- `?include_completed=true` — include completed in results

### Create a Project

```
POST https://gtd-api.fly.dev/projects
Header: X-API-Key: [from TOOLS.md]
Body: {
  "title": "Plan team offsite",
  "outcome": "Offsite booked with agenda finalized and team notified",
  "area_id": null,
  "due_date": "2026-04-15"
}
```

**Fields:**
- `title` (required) — concise project name
- `outcome` — what "done" looks like (GTD best practice: always define the outcome)
- `area_id` — link to an area of responsibility (optional)
- `due_date` — deadline in ISO format (optional)

After creating, immediately add at least one next action:

```
POST https://gtd-api.fly.dev/projects/{id}/actions
Header: X-API-Key: [from TOOLS.md]
Body: {
  "title": "Research venue options for offsite",
  "energy_level": "high",
  "time_estimate_minutes": 30
}
```

### Get Project Detail

```
GET https://gtd-api.fly.dev/projects/{id}
Header: X-API-Key: [from TOOLS.md]
```

Returns project with stats: total actions, completed actions, completion percentage.

### Update a Project

```
PATCH https://gtd-api.fly.dev/projects/{id}
Header: X-API-Key: [from TOOLS.md]
Body: { "title": "...", "outcome": "...", "due_date": "..." }
```

### Delete a Project

```
DELETE https://gtd-api.fly.dev/projects/{id}
Header: X-API-Key: [from TOOLS.md]
```

Only when the user explicitly wants to remove it. Prefer completing or putting on hold.

## Project Lifecycle

### Complete a Project

```
POST https://gtd-api.fly.dev/projects/{id}/complete
Header: X-API-Key: [from TOOLS.md]
```

Use when all actions are done and the outcome is achieved. Sets `completed_at` timestamp.

### Put on Hold

```
POST https://gtd-api.fly.dev/projects/{id}/hold
Header: X-API-Key: [from TOOLS.md]
```

For projects that are paused but not abandoned. Will appear in weekly review as needing attention.

### Reactivate

```
POST https://gtd-api.fly.dev/projects/{id}/activate
Header: X-API-Key: [from TOOLS.md]
```

Resume a project that was on hold. Remind the user to add a next action if none exists.

## Actions Within Projects

### List Project Actions

```
GET https://gtd-api.fly.dev/projects/{id}/actions
Header: X-API-Key: [from TOOLS.md]
```

Shows all actions (next actions) belonging to this project.

### Create Action in Project

```
POST https://gtd-api.fly.dev/projects/{id}/actions
Header: X-API-Key: [from TOOLS.md]
Body: {
  "title": "...",
  "energy_level": "low|medium|high",
  "time_estimate_minutes": 15,
  "due_date": "2026-03-10",
  "tag_ids": [1, 2]
}
```

Creates a next action directly linked to the project. All fields except `title` are optional.

## Stale Project Detection

```
GET https://gtd-api.fly.dev/review/stale-projects
Header: X-API-Key: [from TOOLS.md]
```

Returns active projects with zero next actions. During weekly review, each stale project needs:
- A new next action added, OR
- To be put on hold, OR
- To be completed or deleted

## API Reference

Endpoint and credentials in `/workspace/TOOLS.md`. Full API spec at https://gtd-api.fly.dev/openapi.json.

**Project CRUD:**
```
GET    /projects              — list all projects
POST   /projects              — create project
GET    /projects/{id}         — get project detail
PATCH  /projects/{id}         — update project
DELETE /projects/{id}         — delete project
```

**Project lifecycle:**
```
POST /projects/{id}/complete  — mark project complete
POST /projects/{id}/hold      — put project on hold
POST /projects/{id}/activate  — reactivate from hold
```

**Project actions:**
```
GET  /projects/{id}/actions   — list actions in project
POST /projects/{id}/actions   — create action in project
```

**Review:**
```
GET /review/stale-projects    — projects without next actions
```
