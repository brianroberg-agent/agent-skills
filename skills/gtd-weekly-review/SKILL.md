---
name: weekly-review
description: "Use when the user asks for a 'weekly review', 'review my system', 'Friday review', 'GTD review', 'full review', or wants to do a comprehensive check of their entire GTD system. This orchestrates the full GTD weekly review ceremony."
---

# GTD Weekly Review

Orchestrate the full GTD weekly review — a systematic sweep of every list to get the system current and trusted.

## Invocation Triggers

**Explicit:** "weekly review," "review my system," "Friday review," "let's do a full review," "GTD review."

**Proactive:** If it's Friday or Monday and the user is working through tasks, gently suggest: "Want to do a weekly review while we're at it?"

## Review Workflow

Work through each step in order. Summarize findings at each step before moving to the next. The user can skip any step.

### Step 1: Clear the Inbox

```
GET https://gtd-api.fly.dev/review/inbox-count
Header: X-API-Key: [from TOOLS.md]
```

If count > 0, prompt to process inbox first:
> You have [N] items in your inbox. Want to process them before continuing the review?

If the user wants to process, use the `gtd-process-inbox` skill. If they want to skip, note the count and continue.

### Step 2: Review Overdue Items

```
GET https://gtd-api.fly.dev/review/overdue
Header: X-API-Key: [from TOOLS.md]
```

For each overdue item, present it and ask:
- **Reschedule** — update the due date
- **Complete** — mark done now
- **Delete** — remove if no longer relevant

### Step 3: Review Upcoming Deadlines

```
GET https://gtd-api.fly.dev/review/upcoming-deadlines?days=7
Header: X-API-Key: [from TOOLS.md]
```

Show items with deadlines in the next 7 days. Ask:
- Is the deadline still realistic?
- Do you need to break this into smaller steps?
- Any blockers to address this week?

### Step 4: Review Waiting-For Items

```
GET https://gtd-api.fly.dev/review/waiting-for
Header: X-API-Key: [from TOOLS.md]
```

For each waiting-for item, ask:
- Has this been received? → Complete it
- Need to follow up? → Note the follow-up action
- No longer needed? → Delete it

### Step 5: Review Stale Projects

```
GET https://gtd-api.fly.dev/review/stale-projects
Header: X-API-Key: [from TOOLS.md]
```

Stale projects have no next actions. For each:
- **Add a next action** — what's the very next step?
- **Put on hold** — `POST /projects/{id}/hold`
- **Complete** — if actually done: `POST /projects/{id}/complete`
- **Delete** — if abandoned: `DELETE /projects/{id}`

### Step 6: Review Someday/Maybe

```
GET https://gtd-api.fly.dev/someday-maybe
Header: X-API-Key: [from TOOLS.md]
```

Scan the list for items whose time has come:
- **Activate** — move to next actions: `POST /someday-maybe/{id}/activate`
- **Keep** — still not the right time
- **Delete** — no longer interested

### Step 7: Check Today's Tickler

```
GET https://gtd-api.fly.dev/tickler/today
Header: X-API-Key: [from TOOLS.md]
```

Items surfacing today need attention:
- **Surface** — move to next actions: `POST /tickler/{id}/surface`
- **Snooze** — update the tickler date: `PATCH /tickler/{id}` with new `tickler_date`
- **Complete** — already handled: `POST /tickler/{id}/complete`

### Step 8: Check Donor Tasks

```
GET https://gtd-api.fly.dev/donor-tasks?status=next_action
Header: X-API-Key: [from TOOLS.md]
```

Surface any pending donor tasks (thank-you calls, follow-ups):
- **Complete** — `PATCH /donor-tasks/{id}/status` with `{"status": "completed"}`
- **Defer** — note it for later
- **View contact** — look up the donor for context

## Review Summary

After completing all steps, present a summary:

```
Weekly Review Complete
─────────────────────
Inbox:           [N] items (processed / skipped)
Overdue:         [N] resolved
Upcoming (7d):   [N] deadlines reviewed
Waiting-for:     [N] items checked
Stale projects:  [N] addressed
Someday/maybe:   [N] activated, [N] removed
Tickler:         [N] surfaced
Donor tasks:     [N] pending
```

## API Reference

Endpoint and credentials in `/workspace/TOOLS.md`. Full API spec at https://gtd-api.fly.dev/openapi.json.

**Review endpoints:**
```
GET /review/inbox-count         — inbox item count
GET /review/overdue             — past-due items
GET /review/upcoming-deadlines  — items with approaching deadlines (?days=N)
GET /review/waiting-for         — delegated/waiting items
GET /review/stale-projects      — projects without next actions
```

**List endpoints:**
```
GET /someday-maybe              — all someday/maybe items
GET /tickler/today              — tickler items surfacing today
GET /donor-tasks                — donor tasks in GTD (?status=next_action)
```

**Action endpoints:**
```
POST  /someday-maybe/{id}/activate    — move to next actions
POST  /tickler/{id}/surface           — surface to next actions
POST  /projects/{id}/hold             — put project on hold
POST  /projects/{id}/complete         — complete project
PATCH /donor-tasks/{id}/status        — update donor task status
PATCH /next-actions/{id}              — update a next action (reschedule, etc.)
POST  /next-actions/{id}/complete     — complete a next action
```
