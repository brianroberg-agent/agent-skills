---
name: someday-maybe
description: "Use when the user mentions 'someday list', 'someday/maybe', 'maybe I should...', 'park this for later', 'not now but eventually', 'activate that idea', or wants to browse, manage, or activate items on their someday/maybe list."
---

# GTD Someday/Maybe

Manage the someday/maybe list — ideas and intentions that aren't active commitments yet.

## Invocation Triggers

**Explicit:** "show someday list," "someday/maybe," "what's on my maybe list?," "activate that idea."

**Implicit capture:** "maybe I should...," "someday I'd like to...," "not now but eventually...," "park this for later."

**During review:** Weekly review Step 6 scans this list for items whose time has come.

## Operations

### List Someday/Maybe Items

```
GET https://gtd-api.fly.dev/someday-maybe
Header: X-API-Key: [from TOOLS.md]
```

**Available query parameters:**
- `?area_id=N` — filter by area of responsibility
- `?project_id=N` — filter by project
- `?tag_id=N` — filter by tag
- `?include_completed=true` — show completed items too

### Get Single Item

```
GET https://gtd-api.fly.dev/someday-maybe/{id}
Header: X-API-Key: [from TOOLS.md]
```

### Create Directly

```
POST https://gtd-api.fly.dev/someday-maybe
Header: X-API-Key: [from TOOLS.md]
Body: {
  "title": "Learn to play guitar",
  "notes": "Look into online courses or local teachers",
  "area_id": null,
  "project_id": null,
  "tag_ids": []
}
```

Items can also arrive here via inbox processing (`POST /inbox/{id}/process` with `destination: "someday_maybe"`) or deferring a next action (`POST /next-actions/{id}/defer`).

### Update

```
PATCH https://gtd-api.fly.dev/someday-maybe/{id}
Header: X-API-Key: [from TOOLS.md]
Body: { "title": "...", "notes": "...", "area_id": null, "tag_ids": [] }
```

All fields are optional — only include what's changing.

### Delete

```
DELETE https://gtd-api.fly.dev/someday-maybe/{id}
Header: X-API-Key: [from TOOLS.md]
```

Use when the user is no longer interested. Confirm before deleting: "Remove [title] from someday/maybe?"

### Activate to Next Actions

```
POST https://gtd-api.fly.dev/someday-maybe/{id}/activate
Header: X-API-Key: [from TOOLS.md]
```

Moves the item to the next actions list. Use when:
- The user says "let's do that," "time to act on this," "activate that"
- During weekly review, an item's time has come
- Circumstances have changed making it actionable

After activating, consider whether the item needs refinement (energy level, time estimate, tags, due date) — those can be set via `PATCH /next-actions/{id}`.

### Complete Without Activating

```
POST https://gtd-api.fly.dev/someday-maybe/{id}/complete
Header: X-API-Key: [from TOOLS.md]
```

For items that got done outside the system or are no longer relevant but worth keeping as completed rather than deleted.

## Review Guidance

During the weekly review, scan someday/maybe for:
- **Items whose time has come** → activate
- **Items that are no longer interesting** → delete
- **Items that need updating** → edit notes with new context
- **Items that have been sitting for months unchanged** → consider if they're actually "never" items and remove them

Don't rush this step — the someday/maybe list is where good ideas incubate.

## API Reference

Endpoint and credentials in `/workspace/TOOLS.md`. Full API spec at https://gtd-api.fly.dev/openapi.json.

**CRUD:**
```
GET    /someday-maybe              — list items (with filters)
GET    /someday-maybe/{id}         — single item detail
POST   /someday-maybe              — create item directly
PATCH  /someday-maybe/{id}         — update item
DELETE /someday-maybe/{id}         — delete item
```

**Lifecycle:**
```
POST /someday-maybe/{id}/activate  — move to next actions
POST /someday-maybe/{id}/complete  — mark complete
```
