---
name: donor-ask
description: "Use when the user asks about a donor or contact: 'tell me about [person]', 'look up [name]', 'who is [name]?', 'donor info', 'contact search', 'what do we know about [name]?', 'giving history for [name]', or wants to query the donor management system."
---

# Donor Ask — Query Contacts & Giving

Read-only skill for looking up donors, contacts, and their history in the donor management system.

## Invocation Triggers

**Explicit:** "tell me about [person]," "look up [name]," "who is [name]?," "donor info."

**Giving-focused:** "how much has [name] given?," "giving history for [name]," "[name]'s pledges."

**Activity-focused:** "when did we last talk to [name]?," "interaction history for [name]."

## Lookup Workflow

### Step 1: Search for the Contact

```
GET https://donor-management.fly.dev/api/v1/contacts?search=<query>
Header: X-API-Key: [from TOOLS.md]
```

Searches across first_name, last_name, org_name, and file_as fields. Returns matching contacts with basic info.

If multiple matches, present them and ask which one:
> Found 3 contacts matching "Smith":
> 1. John Smith (ID 42) — Portland, OR
> 2. Jane Smith (ID 43) — Portland, OR
> 3. Robert Smith (ID 87) — Seattle, WA

### Step 2: Get Contact Detail

```
GET https://donor-management.fly.dev/api/v1/contacts/{id}
Header: X-API-Key: [from TOOLS.md]
```

Returns full contact record: name, addresses, phone numbers, email addresses, organization, and metadata.

### Step 3: Get Contact Summary

```
GET https://donor-management.fly.dev/api/v1/contacts/{id}/summary
Header: X-API-Key: [from TOOLS.md]
```

Computed giving stats and activity overview:
- Lifetime giving total
- Year-to-date giving
- Last 12-month giving
- Last gift date and amount
- Active pledge amounts
- Last contact dates (call, visit, letter)

### Step 4: Enrich with Detail (as needed)

Depending on what the user asked, pull additional data:

**Giving history:**
```
GET https://donor-management.fly.dev/api/v1/gifts?contact_id={id}
Header: X-API-Key: [from TOOLS.md]
```

**Interaction history:**
```
GET https://donor-management.fly.dev/api/v1/history?contact_id={id}
Header: X-API-Key: [from TOOLS.md]
```

**Active pledges:**
```
GET https://donor-management.fly.dev/api/v1/pledges?contact_id={id}&active_only=true
Header: X-API-Key: [from TOOLS.md]
```

**Pending tasks:**
```
GET https://donor-management.fly.dev/api/v1/tasks?contact_id={id}&status=pending
Header: X-API-Key: [from TOOLS.md]
```

## Presenting a "Tell Me About" Response

When the user asks "tell me about [name]," synthesize multiple API calls into a natural narrative:

```
John Smith — Portland, OR
────────────────────────────
Giving:     $12,500 lifetime · $2,000 YTD · Last gift: $500 on Jan 15
Pledges:    $200/month (active since 2024)
Activity:   Last call Dec 10 · Last visit Sep 5
Tasks:      1 pending (thank-you call for year-end gift)
```

Keep it concise. Offer to drill deeper: "Want to see the full giving history or interaction log?"

## Important Notes

- Agent API keys do not return `confidential_notes` — this is by design for privacy. Do not mention or ask about confidential notes.
- Search is case-insensitive and supports partial matching.
- The `/summary` endpoint is the most efficient way to get an overview — it computes stats server-side rather than requiring you to aggregate gifts manually.

## API Reference

Endpoint and credentials in `/workspace/TOOLS.md`.
Auth: `X-API-Key` header (agent_read or agent_readwrite key).
Base URL: `https://donor-management.fly.dev`

**Contact lookup:**
```
GET /api/v1/contacts              — search/list contacts (?search=query)
GET /api/v1/contacts/{id}         — full contact detail
GET /api/v1/contacts/{id}/summary — computed giving stats & activity overview
```

**Related data:**
```
GET /api/v1/gifts?contact_id={id}                  — giving history
GET /api/v1/history?contact_id={id}                 — interaction history
GET /api/v1/pledges?contact_id={id}&active_only=true — active pledges
GET /api/v1/tasks?contact_id={id}&status=pending     — pending tasks
```
