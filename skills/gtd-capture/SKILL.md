---
name: capture
description: "Use when the user asks to 'add to inbox', 'capture this', 'remind me to', 'record a task', 'I need to', or when potential action items or commitments surface in conversation."
---

# Capture to GTD Inbox

Capture tasks and action items to the GTD inbox with appropriate clarification.

## Invocation Triggers

**Explicit capture:** Triggered by phrases like "add to inbox," "capture this," "remind me to," "record a task," "I need to..."

**Proactive capture:** When something surfaces in conversation that sounds like an action item or commitment, ask: "Should I capture that?" Never silently add items.

## Capture Process

### Clarify Before Capturing

Prod for clarity before adding to inbox. Items should enter already reasonably actionable. Useful clarifying questions:

- "What's the concrete first step?"
- "Are you doing this, or is someone else responsible?"
- "Is there a timeline or deadline?"
- "What does 'done' look like?"

Exercise judgment—skip clarification when the item is already clear ("email John about the meeting"). Only prod when something is genuinely vague ("figure out the budget situation").

### Handle Vague Intentions

When phrases like "I should probably..." or "I've been meaning to..." appear, push gently: "What would be the first concrete step toward that?" If no concrete step emerges, suggest Someday/Maybe or acknowledge it's not ready to capture yet.

## Item Format

**Title:** Concise, action-oriented.
- Good: "Email John re: Q3 budget"
- Bad: "Budget stuff"

**Notes:** Any context from clarification—timeline, who's involved, why it matters. Keep brief.

## Voice Capture: Always Store the Raw Transcription

On any voice capture, put the raw transcribed utterance in `notes` — unconditionally,
even when the title is already a clean summary, never "only when it seems useful". On
2026-08-23/24, a bike ride with wind noise defeating silence detection (plus a dropped
transport and listen windows cut to 40s) produced inbox items with a garbled or
truncated title and an *empty* notes field — one was the single word "Text", another
"I know about Case USCCom which was that we need to receive" (cuts off mid-clause). By
the 2026-09-04 weekly review neither meant anything, and both had to be deleted as
unrecoverable. A garbled raw transcription sitting in notes still gives more to work
with a week later than a garbled title alone with nothing behind it.

## "Record a Note About X" Is Never a Task

When Brian asks to record a note, capture the note's CONTENT in the same turn and store
it as the note body. Never create an inbox item whose title is "record a note about …"
— that defers the information to a later capture that, in practice, doesn't happen: two
2026-08-23/24 items ("Record a note about understory podcast metaphor"; "Record a note
about Mike Skaist's comment in the understory podcast") were captured as tasks with no
notes field at all, and by 2026-09-04 the actual content — what the metaphor was, what
Skaist said — was gone, not just the to-do to write it down. Brian's own words on 9/4:
"those came from an attempt to record the note itself along with the task, but clearly
it didn't work." If he genuinely can't dictate the content right then (e.g. mid-ride),
that has to be his explicit, stated choice — never a silent default to a task with an
empty notes field.

## What NOT to Capture

- Reference material ("remember that the API key is X")
- Things being done right now in this session
- Vague worries that aren't actionable yet

## After Capture

Confirm simply:
> Captured: [title]

No lengthy confirmation. No "anything else?" Just acknowledge and move on.

## API Reference

Endpoint and credentials in `/workspace/TOOLS.md`. Full API spec at https://gtd-api.fly.dev/openapi.json.

**Capture to inbox:**
```
POST https://gtd-api.fly.dev/inbox
Header: X-API-Key: [from TOOLS.md]
Body: { "title": "...", "notes": "...", "area_id": int|null, "project_id": int|null, "tag_ids": [int] }
```

The `area_id`, `project_id`, and `tag_ids` fields are optional. When the area is obvious from context, set it at capture time to save a step during processing. If the item has an obvious context (e.g., "call John" → @phone tag), set the tag at capture time.

**List available tags:**
```
GET https://gtd-api.fly.dev/tags
Header: X-API-Key: [from TOOLS.md]
```

Common context tags: `@home`, `@phone`, `@computer`, `@errands`, `@waiting_for`.

**Areas of responsibility:**
```
GET  /areas                — list all areas
POST /areas                — create area: { "name": "...", "description": "..." }
GET  /areas/{id}/actions   — list actions in an area
GET  /areas/{id}/projects  — list projects in an area
```

**Projects:**
```
GET  /projects             — list all projects
POST /projects             — create: { "title": "...", "outcome": "...", "area_id": int|null }
GET  /projects/{id}/actions — list actions in a project
POST /projects/{id}/actions — create action directly in a project
```

**Other key endpoints:**
- `GET /inbox` — list inbox items (`?include_completed=true` to show completed)
- `POST /inbox/{id}/complete` — mark inbox item complete
- `DELETE /inbox/{id}` — permanently delete inbox item
- `POST /inbox/{id}/process` — move to next_action, someday_maybe, tickler, or delete
- `GET /next-actions` — list next actions (`?include_completed=true` to show completed)
- `POST /next-actions/{id}/complete` — mark action complete
- `DELETE /next-actions/{id}` — permanently delete next action
- `POST /someday-maybe/{id}/complete` — mark someday/maybe item complete
- `POST /tickler/{id}/complete` — mark tickler item complete
