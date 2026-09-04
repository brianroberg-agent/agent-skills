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
curl -s -X POST "$CALENDAR_AGENT_URL/search" \
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
    }' \
    | jq .
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
  "total_count": 1
}
```

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
LLM failure, `504` no answer in time. Capture the status (`curl -sS -w '\n%{http_code}'`)
and check it before reading the body — for a read, a non-200 means *the answer is
missing*, not that the calendar is empty. Never present a failed read as "nothing
scheduled".
