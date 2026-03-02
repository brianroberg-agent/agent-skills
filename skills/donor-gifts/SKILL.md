---
name: donor-gifts
description: "Use when the user asks about giving data: 'who gave recently?', 'giving report', 'how much has [name] given?', 'record a gift', 'gift history', 'donations this year', or wants to query or record gifts in the donor management system."
---

# Donor Gifts — Giving Data & Manual Entry

Query giving history and record manual gifts (e.g., IRA distributions, stock transfers) that don't come through the automated DonorHub sync.

## Invocation Triggers

**Queries:** "who gave recently?," "giving report," "how much has [name] given?," "gift history," "donations this year."

**Recording:** "record a gift," "log a donation," "enter an IRA distribution," "[name] gave $500."

## Querying Gifts

### List Gifts

```
GET https://donor-management.fly.dev/api/v1/gifts
Header: X-API-Key: [from TOOLS.md]
```

Returns all gifts. Filter by contact:

```
GET https://donor-management.fly.dev/api/v1/gifts?contact_id={id}
Header: X-API-Key: [from TOOLS.md]
```

### Gift Detail

```
GET https://donor-management.fly.dev/api/v1/gifts/{id}
Header: X-API-Key: [from TOOLS.md]
```

Returns full gift record including splits (campaign/promise allocation).

### Contact Giving Summary

The most efficient way to get giving stats — computed server-side:

```
GET https://donor-management.fly.dev/api/v1/contacts/{id}/summary
Header: X-API-Key: [from TOOLS.md]
```

Returns:
- Lifetime giving total
- Year-to-date giving
- Last 12-month giving
- Last gift date and amount
- Average gift amount
- Active pledge totals

## Recording Manual Gifts

For gifts that don't come through DonorHub sync (IRA distributions, stock transfers, in-kind gifts, checks received directly):

### Step 1: Find the Contact

```
GET https://donor-management.fly.dev/api/v1/contacts?search=<name>
Header: X-API-Key: [from TOOLS.md]
```

### Step 2: Create the Gift

```
POST https://donor-management.fly.dev/api/v1/gifts
Header: X-API-Key: [from TOOLS.md]
Body: {
  "contact_id": 42,
  "gift_date": "2026-03-01",
  "amount": 500.00,
  "memo": "IRA distribution",
  "payment_method": "check"
}
```

**Fields:**
- `contact_id` (required) — donor's contact ID
- `gift_date` (required) — date the gift was received (ISO date)
- `amount` (required) — gift amount as a decimal
- `memo` — description/purpose of the gift
- `payment_method` — how the gift was made (check, cash, stock, wire, etc.)

**Important:** Do NOT set `external_gift_code` for manual gifts — leave it null. This field is used by the DonorHub sync to track imported gifts. Setting it on a manual gift could cause sync conflicts.

### Step 3: Confirm

> Recorded: $500.00 gift from John Smith on Mar 1 (IRA distribution)

## Updating Gifts

```
PUT https://donor-management.fly.dev/api/v1/gifts/{id}
Header: X-API-Key: [from TOOLS.md]
Body: { "memo": "...", "payment_method": "..." }
```

Only `memo` and `payment_method` are updatable on existing gifts. Amount and date changes require deleting and re-creating.

## Deleting Gifts

```
DELETE https://donor-management.fly.dev/api/v1/gifts/{id}
Header: X-API-Key: [from TOOLS.md]
```

Only for manual gifts entered in error. Never delete synced gifts (those with `external_gift_code` set) — the sync will re-import them.

## Presentation

Format currency amounts consistently:
- `$1,250.00` (always two decimal places)
- Use comma separators for thousands

When showing giving history, format as a table:

```
Giving History — John Smith
─────────────────────────────────
Date        Amount      Memo
Mar 1       $500.00     IRA distribution
Jan 15      $200.00     Monthly pledge
Dec 20      $1,000.00   Year-end gift
─────────────────────────────────
YTD: $700.00 · Lifetime: $12,500.00
```

## API Reference

Endpoint and credentials in `/workspace/TOOLS.md`.
Auth: `X-API-Key` header (agent_readwrite key required for writes).
Base URL: `https://donor-management.fly.dev`

**Query:**
```
GET /api/v1/gifts                   — list gifts (?contact_id=N)
GET /api/v1/gifts/{id}              — gift detail (with splits)
GET /api/v1/contacts/{id}/summary   — computed giving stats
```

**Write:**
```
POST   /api/v1/gifts                — create manual gift
PUT    /api/v1/gifts/{id}           — update gift (memo, payment_method only)
DELETE /api/v1/gifts/{id}           — delete gift
```
