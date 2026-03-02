---
name: organize
description: "Use when the user asks about areas of responsibility, tags, or system organization: 'show my areas', 'create an area', 'what tags do I have?', 'create a tag', 'organize my system', 'what contexts are available?', '@home tasks', '@phone tasks'."
---

# GTD Organize — Areas & Tags

Manage the organizational backbone of the GTD system: areas of responsibility and context tags.

## Invocation Triggers

**Areas:** "show my areas," "create an area," "what are my areas of responsibility?," "area projects," "area actions."

**Tags:** "what tags do I have?," "create a tag," "show me @home items," "what contexts are available?"

**General:** "organize my system," "set up my GTD structure."

## Areas of Responsibility

Areas are the broad categories of your life and work (e.g., "Health," "Finance," "Work — Engineering"). Projects and actions are organized under areas.

### List All Areas

```
GET https://gtd-api.fly.dev/areas
Header: X-API-Key: [from TOOLS.md]
```

Returns areas with stats: action count, project count.

### Get Area Detail

```
GET https://gtd-api.fly.dev/areas/{id}
Header: X-API-Key: [from TOOLS.md]
```

### Create an Area

```
POST https://gtd-api.fly.dev/areas
Header: X-API-Key: [from TOOLS.md]
Body: {
  "name": "Health & Fitness",
  "description": "Exercise, nutrition, medical appointments"
}
```

### Update an Area

```
PATCH https://gtd-api.fly.dev/areas/{id}
Header: X-API-Key: [from TOOLS.md]
Body: { "name": "...", "description": "..." }
```

### Delete an Area

```
DELETE https://gtd-api.fly.dev/areas/{id}
Header: X-API-Key: [from TOOLS.md]
```

Confirm before deleting. Items linked to this area will be unlinked, not deleted.

### List Actions in an Area

```
GET https://gtd-api.fly.dev/areas/{id}/actions
Header: X-API-Key: [from TOOLS.md]
```

Shows all next actions belonging to this area.

### List Projects in an Area

```
GET https://gtd-api.fly.dev/areas/{id}/projects
Header: X-API-Key: [from TOOLS.md]
```

Shows all projects belonging to this area.

## Tags

Tags provide cross-cutting labels, most commonly used as GTD **context tags** that describe where or how an action can be done.

### List All Tags

```
GET https://gtd-api.fly.dev/tags
Header: X-API-Key: [from TOOLS.md]
```

Returns tags with item counts.

### Get Tag Detail

```
GET https://gtd-api.fly.dev/tags/{id}
Header: X-API-Key: [from TOOLS.md]
```

### Create a Tag

```
POST https://gtd-api.fly.dev/tags
Header: X-API-Key: [from TOOLS.md]
Body: {
  "name": "@phone",
  "color": "#4CAF50"
}
```

### Update a Tag

```
PATCH https://gtd-api.fly.dev/tags/{id}
Header: X-API-Key: [from TOOLS.md]
Body: { "name": "...", "color": "..." }
```

### Delete a Tag

```
DELETE https://gtd-api.fly.dev/tags/{id}
Header: X-API-Key: [from TOOLS.md]
```

### List Items with a Tag

```
GET https://gtd-api.fly.dev/tags/{id}/items
Header: X-API-Key: [from TOOLS.md]
```

Returns all items (across lists) that carry this tag. Useful for context-based work: "show me everything tagged @phone."

## Context Tags Convention

GTD uses context tags to filter actions by where/how they can be done. Recommended set:

| Tag | Use for |
|-----|---------|
| `@home` | Tasks that require being at home |
| `@phone` | Calls to make (can be done anywhere with a phone) |
| `@computer` | Tasks requiring a computer/laptop |
| `@errands` | Things to do while out (grocery, post office, etc.) |
| `@waiting_for` | Delegated items waiting on someone else |
| `@agenda` | Topics to discuss at next meeting with someone |

These are conventions, not requirements. The user can create any tags they want. When capturing items, suggest relevant context tags if the context is obvious (e.g., "call John" → suggest @phone tag).

## API Reference

Endpoint and credentials in `/workspace/TOOLS.md`. Full API spec at https://gtd-api.fly.dev/openapi.json.

**Areas:**
```
GET    /areas                — list all areas (with stats)
GET    /areas/{id}           — area detail
POST   /areas                — create area
PATCH  /areas/{id}           — update area
DELETE /areas/{id}           — delete area
GET    /areas/{id}/actions   — list actions in area
GET    /areas/{id}/projects  — list projects in area
```

**Tags:**
```
GET    /tags                 — list all tags (with item counts)
GET    /tags/{id}            — tag detail
POST   /tags                 — create tag
PATCH  /tags/{id}            — update tag
DELETE /tags/{id}            — delete tag
GET    /tags/{id}/items      — list items with tag
```
