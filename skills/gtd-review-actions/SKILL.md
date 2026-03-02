---
name: review-actions
description: "Use when the user asks 'what should I do?', 'show my next actions', 'what can I do in 15 minutes?', 'low energy tasks', 'what's due this week?', 'tasks at home', 'phone calls to make', or wants to browse and filter their next action list."
---

# Review Next Actions

Query, filter, and manage next actions — the core "what should I do now?" workflow.

## Invocation Triggers

**Explicit:** "what should I do?," "show my next actions," "what can I work on?," "what's on my list?"

**Filtered:** "what can I do in 15 minutes?," "low energy tasks," "tasks at home," "phone calls to make," "what's due this week?"

**Context-aware:** When the user describes their current situation ("I have 20 minutes before my next meeting and I'm tired"), map that to filters automatically.

## Natural Language → Filter Mapping

| User says | Filters to apply |
|-----------|-----------------|
| "what can I do in 15 minutes?" | `?max_time=15` |
| "low energy tasks" | `?energy_level=low` |
| "tasks at home" | `?tag_id=` (find @home tag ID first) |
| "phone calls to make" | `?tag_id=` (find @phone tag ID first) |
| "what's due this week?" | `?due_before=` (next Sunday's date) `&has_deadline=true` |
| "quick wins" | `?max_time=15&energy_level=low` |
| "what should I focus on?" | `?energy_level=high` (show high-energy items) |
| "tasks for [project]" | `?project_id=` (look up project ID first) |
| "work tasks" / "[area] tasks" | `?area_id=` (look up area ID first) |

When context tags are needed, first fetch tags to get the right ID:
```
GET https://gtd-api.fly.dev/tags
Header: X-API-Key: [from TOOLS.md]
```

## Querying Next Actions

### List with Filters

```
GET https://gtd-api.fly.dev/next-actions
Header: X-API-Key: [from TOOLS.md]
```

**Available query parameters:**
- `?tag_id=N` — filter by context tag (@home, @phone, etc.)
- `?project_id=N` — filter by project
- `?area_id=N` — filter by area of responsibility
- `?energy_level=low|medium|high` — filter by energy required
- `?max_time=15` — filter by time estimate (minutes)
- `?due_before=2026-03-05` — deadline filter (ISO date)
- `?has_deadline=true` — only items with deadlines
- `?include_completed=true` — show completed items too

Combine multiple filters: `?energy_level=low&max_time=15&tag_id=3`

### Get Single Action

```
GET https://gtd-api.fly.dev/next-actions/{id}
Header: X-API-Key: [from TOOLS.md]
```

Returns full detail including notes, tags, project, area, energy level, time estimate, and deadline.

## Managing Actions

### Update an Action

```
PATCH https://gtd-api.fly.dev/next-actions/{id}
Header: X-API-Key: [from TOOLS.md]
Body: {
  "title": "...",
  "notes": "...",
  "energy_level": "low|medium|high",
  "time_estimate_minutes": 30,
  "due_date": "2026-03-10",
  "tag_ids": [1, 2],
  "area_id": 1,
  "project_id": 1
}
```

All fields are optional — only include what's changing.

### Complete an Action

```
POST https://gtd-api.fly.dev/next-actions/{id}/complete
Header: X-API-Key: [from TOOLS.md]
```

### Defer to Someday/Maybe

```
POST https://gtd-api.fly.dev/next-actions/{id}/defer
Header: X-API-Key: [from TOOLS.md]
```

Moves the action to the someday/maybe list. Use when the user says "not now," "maybe later," or "park that for now."

### Delete an Action

```
DELETE https://gtd-api.fly.dev/next-actions/{id}
Header: X-API-Key: [from TOOLS.md]
```

Only when explicitly requested. Prefer completing or deferring.

## Presentation

When showing a list of actions, format clearly:

```
Next Actions (filtered: low energy, ≤15 min)
─────────────────────────────────────────────
1. Reply to Sarah's email          ⏱ 10m  ⚡ low   📅 Mar 5
2. Review expense report           ⏱ 15m  ⚡ low
3. Update calendar for next week   ⏱ 10m  ⚡ low   @computer
```

Include energy level, time estimate, deadline (if set), and context tag (if set). Omit fields that aren't populated.

## API Reference

Endpoint and credentials in `/workspace/TOOLS.md`. Full API spec at https://gtd-api.fly.dev/openapi.json.

**Query:**
```
GET /next-actions              — list with filters
GET /next-actions/{id}         — single action detail
```

**Manage:**
```
PATCH  /next-actions/{id}          — update action
POST   /next-actions/{id}/complete — complete action
POST   /next-actions/{id}/defer    — defer to someday/maybe
DELETE /next-actions/{id}          — delete action
```

**Supporting:**
```
GET /tags                      — list tags (for context filtering)
GET /projects                  — list projects (for project filtering)
GET /areas                     — list areas (for area filtering)
```
