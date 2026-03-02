---
name: tickler
description: "Use when the user says 'remind me on [date]', 'tickler', 'what's coming up?', 'deferred items', 'snooze this until', 'surface that later', or wants to manage time-deferred items in their GTD system."
---

# GTD Tickler

Manage the tickler file — items deferred to a specific future date. When the date arrives, they automatically surface for attention.

## Invocation Triggers

**Explicit:** "tickler," "what's coming up?," "deferred items," "show my tickler."

**Date-based:** "remind me on March 15th," "snooze this until Friday," "defer to next week," "surface that on the 1st."

**During review:** Weekly review Step 7 checks today's tickler items.

## How the Tickler Works

Each tickler item has a `tickler_date`. When that date arrives, the item is ready to be surfaced to next actions. Items don't move automatically — they wait to be reviewed and surfaced (or snoozed).

Think of it as a "43 folders" system: items parked until a specific date, then they demand attention.

## Operations

### List All Tickler Items

```
GET https://gtd-api.fly.dev/tickler
Header: X-API-Key: [from TOOLS.md]
```

Returns all tickler items sorted by `tickler_date`.

### Get Today's Items

```
GET https://gtd-api.fly.dev/tickler/today
Header: X-API-Key: [from TOOLS.md]
```

Items whose `tickler_date` is today or earlier (past-due tickler items also appear here). These need attention now.

### Get Single Item

```
GET https://gtd-api.fly.dev/tickler/{id}
Header: X-API-Key: [from TOOLS.md]
```

### Create a Tickler Item

```
POST https://gtd-api.fly.dev/tickler
Header: X-API-Key: [from TOOLS.md]
Body: {
  "title": "Follow up with vendor about proposal",
  "notes": "They said they'd have numbers by mid-March",
  "tickler_date": "2026-03-15",
  "area_id": null,
  "project_id": null,
  "tag_ids": []
}
```

**Fields:**
- `title` (required) — what to do when the date arrives
- `tickler_date` (required) — when to surface this item (ISO date format)
- `notes` — context for future-you
- `area_id`, `project_id`, `tag_ids` — optional organization

Items can also arrive here via inbox processing (`POST /inbox/{id}/process` with `destination: "tickler"` and `tickler_date`).

### Update a Tickler Item

```
PATCH https://gtd-api.fly.dev/tickler/{id}
Header: X-API-Key: [from TOOLS.md]
Body: { "title": "...", "tickler_date": "2026-03-20", "notes": "..." }
```

Common use: snoozing an item by changing its `tickler_date` to a later date.

### Delete a Tickler Item

```
DELETE https://gtd-api.fly.dev/tickler/{id}
Header: X-API-Key: [from TOOLS.md]
```

### Surface to Next Actions

```
POST https://gtd-api.fly.dev/tickler/{id}/surface
Header: X-API-Key: [from TOOLS.md]
```

Moves the item to the next actions list. Use when:
- Today's tickler review shows items ready for action
- The user says "surface that now," "move that to next actions"

After surfacing, consider setting energy level, time estimate, and tags on the new next action via `PATCH /next-actions/{id}`.

### Complete Without Surfacing

```
POST https://gtd-api.fly.dev/tickler/{id}/complete
Header: X-API-Key: [from TOOLS.md]
```

For items that are already handled or no longer needed. Preserves the record with a `completed_at` timestamp.

## Common Patterns

**"Remind me on [date]"** → Create a tickler item with the specified date.

**"Snooze this until [date]"** → Update the tickler_date: `PATCH /tickler/{id}` with new date.

**"What's due today?"** → `GET /tickler/today` to see what's surfacing.

**"What's coming up this week?"** → `GET /tickler` and filter results by date in the next 7 days.

## API Reference

Endpoint and credentials in `/workspace/TOOLS.md`. Full API spec at https://gtd-api.fly.dev/openapi.json.

**CRUD:**
```
GET    /tickler              — list all tickler items
GET    /tickler/today        — items surfacing today (or past-due)
GET    /tickler/{id}         — single item detail
POST   /tickler              — create tickler item
PATCH  /tickler/{id}         — update item (snooze, edit, etc.)
DELETE /tickler/{id}         — delete item
```

**Lifecycle:**
```
POST /tickler/{id}/surface   — move to next actions
POST /tickler/{id}/complete  — mark complete without surfacing
```
