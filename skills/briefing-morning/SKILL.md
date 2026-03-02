---
name: briefing-morning
description: Get a comprehensive morning briefing combining calendar and email summaries
allowed-tools: Bash
---

# Morning Briefing

Get a comprehensive morning briefing combining calendar and email summaries.
This demonstrates multi-agent orchestration where Claude Code synthesizes
information from multiple specialist agents.

## Prerequisites

Requires environment variables:
- `EMAIL_AGENT_URL` - Email agent server
- `CALENDAR_AGENT_URL` - Calendar agent server

GTD and Donor Management credentials in `/workspace/TOOLS.md`.

## Usage

When this skill is invoked, run both queries and present the combined results:

### Step 1: Get Calendar Briefing

```bash
curl -s -X POST "$CALENDAR_AGENT_URL/prepare-briefing" \
    -H "Content-Type: application/json" \
    -d '{
        "briefing_type": "daily",
        "calendar_id": "primary"
    }' \
    | jq -r 'if .success then .briefing else "Calendar error: " + .error end'
```

### Step 2: Get Unread Emails

```bash
curl -s -X POST "$EMAIL_AGENT_URL/search" \
    -H "Content-Type: application/json" \
    -d '{"query": "is:unread", "folder": "INBOX", "limit": 10}' \
    | jq .
```

Review the returned message stubs (subject, sender, snippet). For any that look urgent or important, get a summary:

```bash
curl -s -X POST "$EMAIL_AGENT_URL/summarize" \
    -H "Content-Type: application/json" \
    -d '{"message_id": "MESSAGE_ID_HERE"}' \
    | jq -r '.answer'
```

### Step 3: GTD Status Check

```bash
# Inbox count
curl -s "https://gtd-api.fly.dev/review/inbox-count" \
    -H "X-API-Key: $GTD_API_KEY" | jq .

# Overdue items
curl -s "https://gtd-api.fly.dev/review/overdue" \
    -H "X-API-Key: $GTD_API_KEY" | jq .

# Tickler items surfacing today
curl -s "https://gtd-api.fly.dev/tickler/today" \
    -H "X-API-Key: $GTD_API_KEY" | jq .

# Deadlines today
curl -s "https://gtd-api.fly.dev/review/upcoming-deadlines?days=1" \
    -H "X-API-Key: $GTD_API_KEY" | jq .
```

### Step 4: Donor Task Check

```bash
# Pending donor tasks (via GTD API)
curl -s "https://gtd-api.fly.dev/donor-tasks?status=next_action" \
    -H "X-API-Key: $GTD_API_KEY" | jq .
```

### Step 5: Synthesize

After getting all responses, synthesize them into a coherent briefing that:
- Highlights priorities for the day
- Notes any conflicts between meetings and email deadlines
- Suggests time blocks for email responses
- Reports GTD inbox count and any overdue items
- Surfaces today's tickler items and deadlines
- Lists pending donor follow-ups (thank-you calls, etc.)
- Provides a priority ranking across all four domains (calendar, email, GTD, donor)

## Follow-up Suggestions

After presenting the briefing, the user might ask:
- "Based on that briefing, what should I prioritize today?"
- "Are there any conflicts between my meetings and email deadlines?"
- "Summarize my day in one paragraph"
- "Process my inbox" (→ use `gtd-process-inbox` skill)
- "Show me those donor tasks" (→ use `gtd-donor-tasks` skill)
- "What's overdue?" (→ use `gtd-review-actions` skill)
