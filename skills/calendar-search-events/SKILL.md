---
name: calendar-search-events
description: Search calendar events with structured filters
allowed-tools: Bash
---

# Search Events

Search for calendar events using structured filters. This is a **read-only**
operation for finding specific events.

## Prerequisites

Requires `CALENDAR_AGENT_URL` environment variable to be set.

## Usage

When this skill is invoked, run:

```bash
resp=$(curl -sS --max-time 35 -X POST "$CALENDAR_AGENT_URL/search" -w '\n%{http_code}' \
    -H "Content-Type: application/json" \
    -d '{
        "calendar_id": "robergb@dm.org",
        "filters": {
            "query": "SEARCH_TERM",
            "time_min": "START_ISO",
            "time_max": "END_ISO",
            "max_results": 10,
            "order_by": "startTime"
        }
    }')
rc=$?
code="${resp##*$'\n'}"
body="${resp%$'\n'*}"
if [ "$rc" -ne 0 ] || [ "$code" != "200" ]; then
    echo "READ FAILED (curl exit $rc, HTTP ${code:-none}) - the answer is missing, not empty"
    printf '%s' "$body" | jq -r '.error // .' 2>/dev/null
else
    printf '%s' "$body" | jq .
fi
```

## Request Fields

`calendar_id` is a required top-level field; every search term goes inside
`filters`. Terms sent at the top level are silently ignored, which returns an
unfiltered result set that looks like a successful search.

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `calendar_id` | Yes | - | Calendar to search. Name it explicitly (`robergb@dm.org`); `primary` resolves to whatever account the proxy is authenticated as |
| `filters.query` | No | - | Search term (matches title, description, location) |
| `filters.time_min` | No | - | Start of search range (ISO 8601) |
| `filters.time_max` | No | - | End of search range (ISO 8601) |
| `filters.max_results` | No | `100` | Maximum number of results |
| `filters.order_by` | No | - | Sort order (`startTime` or `updated`) |
| `filters.show_deleted` | No | `false` | Include cancelled events |

## Response Format

```json
{
  "success": true,
  "events": [
    {
      "id": "abc123",
      "summary": "Team Meeting",
      "start": {
        "dateTime": "2026-01-30T14:00:00-05:00"
      },
      "end": {
        "dateTime": "2026-01-30T15:00:00-05:00"
      },
      "location": "Conference Room A",
      "attendees": [
        {"email": "alice@example.com", "responseStatus": "accepted"}
      ]
    }
  ],
  "next_page_token": null,
  "error": null
}
```

The envelope is `EventsListResponse` = `{success, events, next_page_token, error}`.
**There is no `total_count`** — count the array yourself (`jq '.events | length'`).
An empty `events` array with `"success": false` is a *failed read*, not an empty
calendar; see *Non-200 responses* below.

## Examples

**Search for meetings with a person:**
```bash
curl -s -X POST "$CALENDAR_AGENT_URL/search" \
    -H "Content-Type: application/json" \
    -d '{
        "calendar_id": "robergb@dm.org",
        "filters": {"query": "Alice"}
    }' \
    | jq .
```

**Search for project meetings this month:**
```bash
curl -s -X POST "$CALENDAR_AGENT_URL/search" \
    -H "Content-Type: application/json" \
    -d '{
        "calendar_id": "robergb@dm.org",
        "filters": {
            "query": "Project Alpha",
            "time_min": "2026-01-01T00:00:00-05:00",
            "time_max": "2026-01-31T23:59:59-05:00"
        }
    }' \
    | jq .
```

**Find recent standup meetings:**
```bash
curl -s -X POST "$CALENDAR_AGENT_URL/search" \
    -H "Content-Type: application/json" \
    -d '{
        "calendar_id": "robergb@dm.org",
        "filters": {"query": "standup", "max_results": 5, "order_by": "startTime"}
    }' \
    | jq .
```

**Search by location:**
```bash
curl -s -X POST "$CALENDAR_AGENT_URL/search" \
    -H "Content-Type: application/json" \
    -d '{
        "calendar_id": "robergb@dm.org",
        "filters": {"query": "Conference Room B"}
    }' \
    | jq .
```

## Use Cases

- "Find all meetings with John"
- "Search for 1-on-1 meetings"
- "Show me all project review meetings"
- "Find events at the downtown office"

## Tips

- The query searches across event title, description, and location
- Use time range filters to narrow results to a specific period
- Combine with `/summarize-event` to get details about found events
- Use `/ask-calendar` for more complex natural language queries

## Non-200 responses

calendar-agent's HTTP status now agrees with the body instead of always being
`200`: `403` blocked by policy or rejected by the operator, `404` no such calendar
or event, `422` malformed request, `500` unexpected fault, `502` upstream proxy or
LLM failure, `504` no answer in time. For a read, a non-200 means *the answer is
missing*, not that the calendar is empty. Never present a failed read as "nothing
scheduled".

**Do not bolt `-w '\n%{http_code}'` onto a piped `curl ... | jq ...` command.** `jq`
then reads the trailing status line as a second JSON document and dies on it —
`jq: error (at <stdin>:1): Cannot index number with string "events"`, exit status 5,
with whatever it managed to print from the real body left tangled up with the error.
Verified live 2026-09-04 against the deployed agent. Capture the response into a
variable, split off the status, and pipe only the body to `jq`:

```bash
resp=$(curl -sS --max-time 35 -w '\n%{http_code}' "$CALENDAR_AGENT_URL/health")
rc=$?
code="${resp##*$'\n'}"
body="${resp%$'\n'*}"
if [ "$rc" -ne 0 ] || [ "$code" != "200" ]; then
    echo "READ FAILED (curl exit $rc, HTTP ${code:-none}) - the answer is missing, not empty"
    printf '%s' "$body" | jq -r '.error // .' 2>/dev/null
else
    printf '%s' "$body" | jq .
fi
```

The commands under *Usage* above are already in this form — copy one and change the
URL, the payload and the final `jq` filter. Any remaining `curl -s ... | jq ...`
snippet in this file illustrates request shape only; do not run it as the real read.
