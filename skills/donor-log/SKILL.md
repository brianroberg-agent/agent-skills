---
name: donor-log
description: "Use when the user wants to log an interaction with a donor: 'I just called [name]', 'log a visit with [name]', 'record that I sent a letter to [name]', 'note that interaction', 'log a thank-you call', or when they describe a completed donor interaction that should be recorded."
---

# Donor Log — Record Interactions

Log calls, visits, letters, and other interactions with donors and contacts.

## Invocation Triggers

**Explicit:** "log a call with [name]," "record a visit with [name]," "I sent a letter to [name]," "note that interaction."

**Implicit:** When the user describes having completed an interaction — "I just called John about his pledge," "Had coffee with the Smiths today" — offer to log it.

## Logging Workflow

### Step 1: Identify the Contact

Search for the contact to get their ID:

```
GET https://donor-management.fly.dev/api/v1/contacts?search=<name>
Header: X-API-Key: [from TOOLS.md]
```

If multiple matches, ask which one. If no match, ask for clarification.

### Step 2: Determine Interaction Type

Look up available types:

```
GET https://donor-management.fly.dev/api/v1/history/types
Header: X-API-Key: [from TOOLS.md]
```

Common types: Call, Letter, Email, Visit, Newsletter, Thank. Each type has flags like `affects_last_call`, `affects_last_letter`, `affects_last_visit` that automatically update the contact's "last contacted" dates.

Map the user's description to the right type:
- "called" / "phoned" → Call
- "visited" / "met with" / "had coffee with" → Visit
- "sent a letter" / "mailed" → Letter
- "emailed" → Email
- "thanked" / "thank-you call" → Thank (or Call with `is_thank: true`)

### Step 3: Determine Result

Look up available results:

```
GET https://donor-management.fly.dev/api/v1/history/results
Header: X-API-Key: [from TOOLS.md]
```

Common results: Done, Attempted, Received, Left Message. Default to "Done" unless the user indicates otherwise ("tried to call but no answer" → Attempted or Left Message).

### Step 4: Clarify Details

Before creating, confirm:
- **Who:** Contact name(s)
- **What:** Interaction type
- **When:** Date (default to today)
- **Notes:** Brief description of what was discussed

Skip clarification when the user has already provided all details: "I just called John Smith about his pledge renewal — he's renewing at $200/month."

### Step 5: Create the History Entry

```
POST https://donor-management.fly.dev/api/v1/history
Header: X-API-Key: [from TOOLS.md]
Body: {
  "history_date": "2026-03-02T10:00:00",
  "history_type_id": 1,
  "history_result_id": 1,
  "description": "Called about pledge renewal",
  "notes": "John is renewing at $200/month, appreciates the ministry updates",
  "is_thank": false,
  "is_challenge": false,
  "contact_ids": [42]
}
```

**Fields:**
- `history_date` (required) — when the interaction happened (ISO datetime)
- `history_type_id` (required) — from `/history/types`
- `history_result_id` (required) — from `/history/results`
- `description` — short summary line
- `notes` — longer details about the conversation
- `is_thank` — set `true` if this was a thank-you interaction
- `is_challenge` — set `true` if a gift challenge/ask was made
- `contact_ids` (required) — array of contact IDs involved

### Multi-Contact Interactions

One interaction can be linked to multiple contacts. If the user says "visited John and Jane Smith," include both contact IDs:

```json
{
  "contact_ids": [42, 43]
}
```

Search for each contact separately to get their IDs.

### After Logging

Confirm simply:
> Logged: Call with John Smith on Mar 2 — pledge renewal discussion

## Important Notes

- Agent API keys cannot write `confidential_notes` — the field is silently dropped. Do not include it in the request body.
- The `is_thank` flag is important for tracking stewardship activity. Set it when the interaction is primarily a thank-you.
- History types with `affects_last_call: true` (etc.) automatically update the contact's last-contacted dates — no separate update needed.

## API Reference

Endpoint and credentials in `/workspace/TOOLS.md`.
Auth: `X-API-Key` header (agent_readwrite key required for writes).
Base URL: `https://donor-management.fly.dev`

**Lookup:**
```
GET /api/v1/contacts?search=<name>  — find contact by name
GET /api/v1/history/types           — list interaction types
GET /api/v1/history/results         — list interaction results
```

**Create:**
```
POST /api/v1/history                — create history entry
```

**Read (for reference):**
```
GET /api/v1/history                 — list history entries (?contact_id=N)
GET /api/v1/history/{id}            — get single history entry
```

**Update/Delete:**
```
PUT    /api/v1/history/{id}         — update history entry
DELETE /api/v1/history/{id}         — delete history entry
```
