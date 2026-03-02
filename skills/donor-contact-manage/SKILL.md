---
name: donor-contact-manage
description: "Use when the user wants to create, update, or delete a contact in the donor system, or manage groups: 'add a new contact', 'update [name]'s address', 'create a group', 'add [name] to the [group] group', 'remove contact', 'manage groups'."
---

# Donor Contact Manage — Contact CRUD & Groups

Create, update, and delete contacts in the donor management system, and manage contact groups.

## Invocation Triggers

**Contacts:** "add a new contact," "create a contact for [name]," "update [name]'s address," "change [name]'s phone number," "delete [name]'s record."

**Groups:** "create a group," "show groups," "add [name] to [group]," "remove [name] from [group]."

## Contact Operations

### Create a Contact

```
POST https://donor-management.fly.dev/api/v1/contacts
Header: X-API-Key: [from TOOLS.md]
Body: {
  "first_name": "John",
  "last_name": "Smith",
  "org_name": "",
  "file_as": "Smith, John",
  "addresses": [
    {
      "address_type": "home",
      "street": "123 Main St",
      "city": "Portland",
      "state": "OR",
      "zip": "97201",
      "is_primary": true
    }
  ],
  "phones": [
    {
      "phone_type": "mobile",
      "number": "503-555-1234",
      "is_primary": true
    }
  ],
  "emails": [
    {
      "email_type": "personal",
      "address": "john@example.com",
      "is_primary": true
    }
  ]
}
```

**Fields:**
- `first_name`, `last_name` — at least one is required
- `org_name` — organization name (for org contacts, can be used instead of first/last)
- `file_as` — how the contact is sorted/displayed (auto-generated if omitted)
- `addresses` — array of addresses with `address_type` (home, work, other), `is_primary` flag
- `phones` — array of phone numbers with `phone_type` (home, work, mobile, other), `is_primary` flag
- `emails` — array of email addresses with `email_type` (personal, work, other), `is_primary` flag

Addresses, phones, and emails are optional — a contact can be created with just a name.

### Update a Contact

```
PUT https://donor-management.fly.dev/api/v1/contacts/{id}
Header: X-API-Key: [from TOOLS.md]
Body: { "first_name": "...", "addresses": [...], ... }
```

Send the full contact object with updates. Nested arrays (addresses, phones, emails) are replaced entirely — include all existing items plus changes.

To find the contact ID first:
```
GET https://donor-management.fly.dev/api/v1/contacts?search=<name>
Header: X-API-Key: [from TOOLS.md]
```

### Delete a Contact

```
DELETE https://donor-management.fly.dev/api/v1/contacts/{id}
Header: X-API-Key: [from TOOLS.md]
```

**Confirm before deleting.** This removes the contact and disassociates (but does not delete) their gifts, history, and tasks. This action cannot be undone.

## Group Operations

Groups are collections of contacts used for bulk operations (mailings, reports, etc.).

### List Groups

```
GET https://donor-management.fly.dev/api/v1/groups
Header: X-API-Key: [from TOOLS.md]
```

### Get Group with Members

```
GET https://donor-management.fly.dev/api/v1/groups/{id}
Header: X-API-Key: [from TOOLS.md]
```

Returns the group and its member contacts.

### Create a Group

```
POST https://donor-management.fly.dev/api/v1/groups
Header: X-API-Key: [from TOOLS.md]
Body: {
  "name": "Board Members",
  "description": "Current board of directors"
}
```

### Update a Group

```
PUT https://donor-management.fly.dev/api/v1/groups/{id}
Header: X-API-Key: [from TOOLS.md]
Body: { "name": "...", "description": "..." }
```

### Delete a Group

```
DELETE https://donor-management.fly.dev/api/v1/groups/{id}
Header: X-API-Key: [from TOOLS.md]
```

Deleting a group does not delete its member contacts.

### Add Contacts to a Group

```
POST https://donor-management.fly.dev/api/v1/groups/{id}/contacts
Header: X-API-Key: [from TOOLS.md]
Body: {
  "contact_ids": [42, 43, 87]
}
```

### Remove Contacts from a Group

```
DELETE https://donor-management.fly.dev/api/v1/groups/{id}/contacts
Header: X-API-Key: [from TOOLS.md]
Body: {
  "contact_ids": [42]
}
```

## Important Notes

- Agent API keys cannot read or write `confidential_notes` on contacts — this is by design.
- When updating a contact, the nested arrays (addresses, phones, emails) are replaced entirely. Always read the current contact first (`GET /api/v1/contacts/{id}`) and merge changes before sending the update.
- The `file_as` field controls sort order. Convention: "LastName, FirstName" for individuals, org name for organizations.

## API Reference

Endpoint and credentials in `/workspace/TOOLS.md`.
Auth: `X-API-Key` header (agent_readwrite key required for writes).
Base URL: `https://donor-management.fly.dev`

**Contacts:**
```
GET    /api/v1/contacts              — search/list contacts (?search=query)
GET    /api/v1/contacts/{id}         — contact detail
POST   /api/v1/contacts              — create contact
PUT    /api/v1/contacts/{id}         — update contact
DELETE /api/v1/contacts/{id}         — delete contact
```

**Groups:**
```
GET    /api/v1/groups                — list groups
GET    /api/v1/groups/{id}           — group with members
POST   /api/v1/groups                — create group
PUT    /api/v1/groups/{id}           — update group
DELETE /api/v1/groups/{id}           — delete group
POST   /api/v1/groups/{id}/contacts  — add contacts to group
DELETE /api/v1/groups/{id}/contacts  — remove contacts from group
```
