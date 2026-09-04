---
name: calendar-update-event
description: Update an existing calendar event (requires approval)
allowed-tools: Bash
---

# Update Calendar Event

Update an existing calendar event. This is a **write operation** that modifies your calendar.

**This skill requires your approval before executing the update.**

## Prerequisites

Requires `CALENDAR_AGENT_URL` environment variable to be set.

## Read this before you update anything

**An update blocks while a human approves it.** Every mutation goes through
api-proxy, which holds the request open while a human operator says yes or no.
calendar-agent waits `PROXY_CONFIRM_TIMEOUT` seconds for that answer (default
330s = a 300s operator window plus a 30s margin). **An update that sits there for
four minutes is working normally, not hung.** Do not kill it and do not retry it —
a retry enqueues a *second* approval request for the same operation. Give curl
`--max-time 420` so it outlives the server's own budget instead of dying first
with an ambiguous transport error.

**There are three outcomes, not two:** success, failure, and **unknown**. An update
whose answer never arrived may still be applied minutes later when the operator
approves it. Never report unknown as failure, and never issue a second write to
"put it back".

## The outcome contract

`PATCH` and `PUT /calendars/{calendar_id}/events/{event_id}` return an
`EventDetailResponse`:

```json
{"success": true, "event": {"id": "abc123", "status": "confirmed", "...": "..."}, "error": null}
```

**Note the asymmetry with deletion:** `EventDetailResponse` has no `outcome` field
— only `DELETE` (and `/bulk-actions`) carry the tri-state `outcome` enum. So for
updates **the HTTP status is the authoritative signal**, read together with the
body's `success`:

| Status | Outcome | What to do next |
|--------|---------|-----------------|
| `200` + `success: true` | **succeeded** | Report the change, echoing the fields from `.event` |
| `403` | **failed** — the operator rejected it, or policy blocked it | Do not retry; tell the user it was rejected |
| `404` | **failed** — no such event or calendar | Check the ids |
| `422` | **failed** — malformed request. Body is a FastAPI validation error, not the envelope | Fix the payload |
| `500` | **failed** — unexpected server fault | Report it |
| `502` | **failed** — upstream proxy or LLM failure | Report it |
| `504` | **UNKNOWN** — no answer before calendar-agent's timeout | Verify by re-reading the event; the change may still land |
| curl exit != 0 | **UNKNOWN** — transport timeout or connection failure | Same: verify by re-reading |

If a future calendar-agent adds `outcome` to this envelope, prefer it over the
status table: it is the field the server computes, and the table is the
client-side re-derivation of it. When it appears, `unknown` and `not_attempted`
must never be reported as failure.

A body without a boolean `success` key is not calendar-agent's answer at all
(most likely a wrong `CALENDAR_AGENT_URL`). Treat it as unknown.

## Sequencing invariant (binding)

> **Never issue a follow-on or compensating mutation until the prior mutation has
> been observed complete by a read.**

If an update came back `504` or timed out, do **not** re-send it, revert it, or
delete and recreate the event. Re-read the event and compare the fields you
intended to change. If the read is inconclusive, wait and re-read; do not act.
Compensating for an outcome that was never established is what produced the
2026-08-07 duplicate-event incident.

## Workflow

Brian's calendar id is `robergb@dm.org` — **name it explicitly, do not use
`primary`.** `primary` is not an id: it resolves to whichever account the proxy
happens to be authenticated as, so it can silently address a different calendar
than the one intended, and it is not the documented id for this deployment. Path
segments must be URL-encoded, so `robergb@dm.org` becomes `robergb%40dm.org`
inside a URL.

### Step 1: Find the event

```bash
curl -s --max-time 35 "$CALENDAR_AGENT_URL/calendars/robergb%40dm.org/events?time_min=START_ISO&time_max=END_ISO" \
    | jq '.events[] | {id, summary, start, end}'
```

Or search by keyword. `calendar_id` is **required** on `POST /search`, and the
search terms go inside `filters`:

```bash
curl -s --max-time 35 -X POST "$CALENDAR_AGENT_URL/search" \
    -H "Content-Type: application/json" \
    -d '{
        "calendar_id": "robergb@dm.org",
        "filters": {"query": "SEARCH_TERM", "max_results": 10}
    }' \
    | jq '.events[] | {id, summary, start, end}'
```

Extract the `id` field from the event you want to update.

### Step 2: Update the event, capturing status and body

Use `PATCH` to change only the fields that need to change:

```bash
resp=$(curl -sS --max-time 420 -w '\n%{http_code}' \
    -X PATCH "$CALENDAR_AGENT_URL/calendars/robergb%40dm.org/events/EVENT_ID" \
    -H "Content-Type: application/json" \
    -d '{
        "summary": "NEW_TITLE",
        "start": {"dateTime": "NEW_START_ISO", "timeZone": "America/New_York"},
        "end": {"dateTime": "NEW_END_ISO", "timeZone": "America/New_York"}
    }')
rc=$?
code="${resp##*$'\n'}"
body="${resp%$'\n'*}"
if [ "$rc" -ne 0 ]; then
    echo "UNKNOWN: no response (curl exit $rc). The update may still be applied."
else
    echo "HTTP $code"
    printf '%s' "$body" | jq '{success, summary: .event.summary, start: .event.start, end: .event.end, error}'
fi
```

Then branch on `code` per the table above. Only `HTTP 200` with `success: true`
means the change took effect.

### Step 3: Verify after an unknown outcome

```bash
curl -s --max-time 35 "$CALENDAR_AGENT_URL/calendars/robergb%40dm.org/events/EVENT_ID" \
    | jq '{success, summary: .event.summary, start: .event.start, end: .event.end, status: .event.status}'
```

Compare against what you intended. Report what you actually observed — "the change
is present", "the event is unchanged", or "could not read the event" — not what you
assume happened. An unchanged event after a `504` is still **unknown**, not failed:
the operator may approve it later.

## Updatable fields

| Field | Description |
|-------|-------------|
| `summary` | Event title |
| `start` | Start time object with dateTime and timeZone |
| `end` | End time object with dateTime and timeZone |
| `description` | Event description/notes |
| `location` | Event location |
| `attendees` | Array of attendee objects |

Only include fields you want to change. Omitted fields remain unchanged under
`PATCH`. `PUT` is a full replacement — prefer `PATCH` unless you mean to replace.

## Examples

**Change meeting time:**
```bash
curl -sS --max-time 420 -w '\n%{http_code}' \
    -X PATCH "$CALENDAR_AGENT_URL/calendars/robergb%40dm.org/events/abc123" \
    -H "Content-Type: application/json" \
    -d '{
        "start": {"dateTime": "2026-01-31T15:00:00", "timeZone": "America/New_York"},
        "end": {"dateTime": "2026-01-31T16:00:00", "timeZone": "America/New_York"}
    }'
```

**Update title and add location:**
```bash
curl -sS --max-time 420 -w '\n%{http_code}' \
    -X PATCH "$CALENDAR_AGENT_URL/calendars/robergb%40dm.org/events/abc123" \
    -H "Content-Type: application/json" \
    -d '{
        "summary": "Updated Meeting Title",
        "location": "Conference Room B"
    }'
```

**Add attendees:**
```bash
curl -sS --max-time 420 -w '\n%{http_code}' \
    -X PATCH "$CALENDAR_AGENT_URL/calendars/robergb%40dm.org/events/abc123" \
    -H "Content-Type: application/json" \
    -d '{
        "attendees": [
            {"email": "alice@example.com"},
            {"email": "bob@example.com"}
        ]
    }'
```

In each example the trailing line of output is the HTTP status; read it, do not
discard it. A discarded status is how a non-200 gets read as success.

## Security notes

- Claude Code's approval prompt is a gate on issuing the request; the operator
  approval at the proxy is a second, independent gate on it taking effect.
- Always confirm the event details with the user before updating: show the current
  event and the proposed change.
- Never retry a mutation that timed out. Verify, then decide.
