---
name: calendar-delete-event
description: Delete a calendar event (requires approval)
allowed-tools: Bash
---

# Delete Calendar Event

Delete a calendar event. This is a **destructive write operation** that removes an event.

**This skill requires your explicit approval before executing the deletion.**

## Prerequisites

Requires `CALENDAR_AGENT_URL` environment variable to be set.

## Read this before you delete anything

Three things about deletion are counter-intuitive and each one has caused a real
incident. Read them before writing a command.

**1. A deletion blocks while a human approves it.** Every mutation goes through
api-proxy, which holds the request open while a human operator says yes or no.
calendar-agent waits `PROXY_CONFIRM_TIMEOUT` seconds for that answer (default
330s = a 300s operator window plus a 30s margin), then re-reads the event to
verify — another read budget of up to 30s. **A delete that sits there for four
minutes is working normally, not hung.** Do not kill it, do not retry it (a retry
enqueues a *second* approval request for the same operation), and do not report
it as failed. Give curl `--max-time 420` so it outlives the server's own budget.

🚨 **You must also pass `timeout: 450000` on the Bash tool call that runs it.** The
Bash tool's own timeout defaults to **120000 ms** (max 600000) — *shorter than the
operator's approval window*. At the default the tool kills the call at two minutes,
curl never prints its `%{http_code}`, and you are left in exactly the ambiguous
"did it happen?" state this contract exists to remove, while the operator's approval
lands at minute three and the deletion goes through anyway. `--max-time 420` without
`timeout: 450000` buys nothing.

**2. There are three outcomes, not two.** Success, failure, and **unknown**. An
unknown deletion may still be applied minutes later when the operator gets to it.
Reporting unknown as "failed" is exactly what produced the 2026-08-07 duplicate-event
incident: a delete was reported failed, a replacement event was created, and then
the original deletion landed after all.

**3. Never compensate before you have verified.** See *Sequencing invariant* below.

## The outcome contract

`DELETE /calendars/{calendar_id}/events/{event_id}` returns an `ActionResponse`:

```json
{"success": true, "outcome": "succeeded", "message": "Event deleted successfully", "error": null}
```

**`outcome` is the authoritative field — read it first.** It is a required field on
`ActionResponse` and takes one of four values:

| `outcome` | Meaning | What to do next |
|-----------|---------|-----------------|
| `succeeded` | calendar-agent re-read the event and it is gone | Report the deletion done |
| `failed` | Definitively did not happen; nothing is outstanding | Report the failure and the `error` text |
| `unknown` | **Outcome not established.** May still be applied when the operator approves it | Do NOT report failure. Do NOT compensate. Verify (below), and re-verify later |
| `not_attempted` | Bulk only: never sent because an earlier operation came back `unknown` | Treat as not done and not attempted; re-run after the earlier one resolves |

`unknown` and `not_attempted` must **never** be collapsed into a failure count or
described to the user as a failure.

**HTTP status is the fallback**, for a calendar-agent old enough not to send
`outcome`, and for responses that are not an envelope at all:

| Status | Meaning |
|--------|---------|
| `200` | Deleted, and confirmed gone by calendar-agent's own re-read |
| `403` | Operator rejected it, or policy blocked it. **Do not retry** — tell the user |
| `404` | No such event or calendar; nothing was deleted (check the id before assuming success) |
| `422` | Malformed request. Body is a FastAPI validation error, not the `{success, outcome}` envelope |
| `500` | Unexpected server fault |
| `502` | Upstream proxy or LLM failure |
| `504` | **Outcome unknown** — no answer in time, or the verifying re-read failed |
| curl exit != 0 | **Outcome unknown** — transport timeout or connection failure |

**Read `outcome` first, then the status table; the body's shape is only a
fallback.** A `422` is a **definite failure**, not an unknown, even though its
FastAPI body (`{"detail": [...]}`) carries no `success`/`outcome` key: the request
was rejected by validation before it reached the calendar, nothing is outstanding,
and the fix is to correct the payload and send it again. Reporting it as "the
deletion may still be applied" both misleads the user and blocks, under the
sequencing invariant below, the retry that would actually fix it.

Only for a status *not* in the table above does the body's shape matter: a response
with no boolean `success` key is then not calendar-agent's answer at all (most
likely a wrong `CALENDAR_AGENT_URL` hitting a bare FastAPI 404, whose status code
tells you nothing about the event). Treat that as unknown.

### If you use `POST /bulk-actions`

No skill in this repo wraps `/bulk-actions`, but if you call it directly: each
entry in `results` carries its own `outcome`, and the envelope carries
`success_count`, `error_count`, **`unknown_count`** and **`not_attempted_count`**.
Report the last two separately — collapsing them into the failure tally is the
same mistake as calling a `504` a failure. Once one operation comes back
`unknown`, calendar-agent stops sending the rest (each would hold the connection
for another full timeout and enqueue another approval) and marks them
`not_attempted`; the batch's status code is the most urgent of its operations,
with `504` outranking every definite failure.

## Sequencing invariant (binding)

> **Never issue a follow-on or compensating mutation until the prior mutation has
> been observed complete by a read.**

Concretely: no replacement event, no re-create, no second delete, no "fix it up"
update while any earlier mutation is `unknown`. Read the event back first. If the
read is inconclusive, the answer is still "wait and re-read", never "act anyway".
This is the control that would have prevented the 2026-08-07 overlapping events.

## Workflow

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

Brian's calendar id is `robergb@dm.org` — **name it explicitly, do not use
`primary`.** `primary` is not an id: it resolves to whichever account the proxy
happens to be authenticated as, so it can silently address a different calendar
than the one intended, and it is not the documented id for this deployment. Path
segments must be URL-encoded, so `robergb@dm.org` becomes `robergb%40dm.org`
inside a URL.

Both of these finding commands discard the HTTP status. If one prints nothing, that
is **not** evidence the event is absent — a failed read looks identical to an empty
result (`EventsListResponse` is `{"success": false, "events": [], "error": ...}`).
Before concluding an event does not exist, re-run the read in the status-capturing
form used in Step 4.

### Step 2: Confirm the event details with the user

```bash
curl -s --max-time 35 "$CALENDAR_AGENT_URL/calendars/robergb%40dm.org/events/EVENT_ID" \
    | jq .
```

Present summary, time, location and attendees, and ask before deleting.

### Step 3: Delete, capturing status and body

In Brian's assistant workspace, prefer the whitelisted wrapper script
`scripts/calendar-delete-event.sh <event_id> [calendar_id]`: a bare
`curl -X DELETE` is refused there by the permission classifier as
`[Modify Shared Resources]`, and the wrapper carries the allow rule. Invoke it as a
**standalone** Bash command — wrapping it in a compound command (`echo …; script …`)
stops the allow rule matching and the whole line gets classified. The wrapper
implements the same contract described here; rewriting this skill fully around it
is tracked separately as agent-skills issue #3.

Where no wrapper exists, the raw call is:

```bash
resp=$(curl -sS --max-time 420 -w '\n%{http_code}' \
    -X DELETE "$CALENDAR_AGENT_URL/calendars/robergb%40dm.org/events/EVENT_ID")
rc=$?
code="${resp##*$'\n'}"
body="${resp%$'\n'*}"
if [ "$rc" -ne 0 ]; then
    echo "UNKNOWN: no response (curl exit $rc). The deletion may still be applied."
else
    echo "HTTP $code"
    printf '%s' "$body" | jq '{success, outcome, message, error}'
fi
```

Then branch on `outcome` (preferred) or `code` (fallback), per the tables above.

### Step 4: Verify before you report or act

Whenever the outcome is anything other than `succeeded`, re-read the event. The
re-read, not the delete's own answer, is the evidence:

```bash
vresp=$(curl -sS --max-time 35 -w '\n%{http_code}' \
    "$CALENDAR_AGENT_URL/calendars/robergb%40dm.org/events/EVENT_ID")
vrc=$?
vcode="${vresp##*$'\n'}"
vbody="${vresp%$'\n'*}"
if [ "$vrc" -ne 0 ]; then
    echo "INCONCLUSIVE: could not re-read the event (curl exit $vrc)"
else
    echo "HTTP $vcode"
    printf '%s' "$vbody" | jq '{success, status: .event.status, error}'
fi
```

- HTTP `404`, or HTTP `200` with `.event.status == "cancelled"` → **gone**.
  Google keeps a deleted event readable as `cancelled` for a while before it 404s,
  so both count as gone. (calendar-agent's `error_status_code()` emits only 403,
  404, 500, 502 and 504 — a `410` from this server would itself be the anomaly, so
  do not treat one as evidence of anything.)
- HTTP `200` with any other `.event.status` → **still present**. That is a failure
  only if nothing is outstanding; if the delete came back `unknown`, it is still
  unknown.
- Anything else → **inconclusive**. Report unknown; do not act.

## Response format

```json
{
  "success": false,
  "outcome": "unknown",
  "message": "Deletion outcome unknown: no response before timeout and the event is still present; it may yet be applied when the operator approves it. Re-verify before acting",
  "error": "Outcome unknown: No response from proxy after 330s..."
}
```

There is no `event_id` field in this envelope — an older version of this skill
claimed one. The fields are `success`, `outcome`, `message`, `error`.

## Safety notes

- **Always confirm** with the user before deleting; show attendees.
- Deletion is permanent — there is no undo.
- If the event has attendees, cancellation notices may be sent.
- Claude Code's approval prompt is a gate on issuing the request; the operator
  approval at the proxy is a second, independent gate on the request taking effect.
- Never retry a mutation that timed out. Verify, then decide.

## Cancellation vs deletion

- This endpoint deletes the event entirely.
- For recurring events, consider whether to delete one instance or the whole series.
