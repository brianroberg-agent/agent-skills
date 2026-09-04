---
name: calendar-daily-briefing
description: Get a summary of your calendar for today
allowed-tools: Bash
---

# Daily Briefing

Get a summary of your calendar for today. This is a convenience skill that
provides a quick overview of your schedule (calendar only, no email).

## Prerequisites

Requires `CALENDAR_AGENT_URL` environment variable to be set.

## Usage

When this skill is invoked, run:

```bash
curl -s -X POST "$CALENDAR_AGENT_URL/prepare-briefing" \
    -H "Content-Type: application/json" \
    -d '{
        "briefing_type": "daily",
        "calendar_id": "robergb@dm.org"
    }' \
    | jq -r 'if .success then .briefing else "Error: " + .error end'
```

## Response Format

The briefing includes:
- Summary of today's events
- Key meetings and their times
- Back-to-back meeting warnings
- Free time blocks
- Preparation reminders

## Difference from Other Briefings

- `/daily-briefing` - Calendar only, today
- `/weekly-briefing` - Calendar only, this week
- `/morning-briefing` - Calendar + Email combined

## Non-200 responses

calendar-agent's HTTP status now agrees with the body instead of always being
`200`: `403` blocked by policy or rejected by the operator, `404` no such calendar
or event, `422` malformed request, `500` unexpected fault, `502` upstream proxy or
LLM failure, `504` no answer in time. Capture the status (`curl -sS -w '\n%{http_code}'`)
and check it before reading the body — for a read, a non-200 means *the answer is
missing*, not that the calendar is empty. Never present a failed read as "nothing
scheduled".
