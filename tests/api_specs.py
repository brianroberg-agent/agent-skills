"""Registry of all API endpoints from GTD and Donor Management APIs.

Used by test_api_coverage.py to verify every endpoint is referenced
in at least one skill file.
"""

GTD_ENDPOINTS = {
    # Inbox
    "GET /inbox": {"description": "List inbox items", "domain": "gtd"},
    "POST /inbox": {"description": "Create inbox item", "domain": "gtd"},
    "PATCH /inbox/{id}": {"description": "Update inbox item", "domain": "gtd"},
    "DELETE /inbox/{id}": {"description": "Delete inbox item", "domain": "gtd"},
    "POST /inbox/{id}/process": {"description": "Process inbox item", "domain": "gtd"},
    "POST /inbox/{id}/complete": {"description": "Complete inbox item", "domain": "gtd"},
    # Next Actions
    "GET /next-actions": {"description": "List next actions", "domain": "gtd"},
    "POST /next-actions": {"description": "Create next action", "domain": "gtd"},
    "PATCH /next-actions/{id}": {"description": "Update next action", "domain": "gtd"},
    "DELETE /next-actions/{id}": {"description": "Delete next action", "domain": "gtd"},
    "POST /next-actions/{id}/complete": {"description": "Complete next action", "domain": "gtd"},
    "POST /next-actions/{id}/defer": {"description": "Defer to someday/maybe", "domain": "gtd"},
    "GET /next-actions/{id}": {"description": "Get single next action", "domain": "gtd"},
    # Someday/Maybe
    "GET /someday-maybe": {"description": "List someday/maybe items", "domain": "gtd"},
    "POST /someday-maybe": {"description": "Create someday/maybe item", "domain": "gtd"},
    "PATCH /someday-maybe/{id}": {"description": "Update someday/maybe item", "domain": "gtd"},
    "DELETE /someday-maybe/{id}": {"description": "Delete someday/maybe item", "domain": "gtd"},
    "POST /someday-maybe/{id}/complete": {"description": "Complete someday/maybe item", "domain": "gtd"},
    "POST /someday-maybe/{id}/activate": {"description": "Activate to next actions", "domain": "gtd"},
    "GET /someday-maybe/{id}": {"description": "Get single someday/maybe item", "domain": "gtd"},
    # Tickler
    "GET /tickler": {"description": "List tickler items", "domain": "gtd"},
    "POST /tickler": {"description": "Create tickler item", "domain": "gtd"},
    "PATCH /tickler/{id}": {"description": "Update tickler item", "domain": "gtd"},
    "DELETE /tickler/{id}": {"description": "Delete tickler item", "domain": "gtd"},
    "POST /tickler/{id}/complete": {"description": "Complete tickler item", "domain": "gtd"},
    "POST /tickler/{id}/surface": {"description": "Surface tickler to next actions", "domain": "gtd"},
    "GET /tickler/{id}": {"description": "Get single tickler item", "domain": "gtd"},
    "GET /tickler/today": {"description": "Get items surfacing today", "domain": "gtd"},
    # Projects
    "GET /projects": {"description": "List projects", "domain": "gtd"},
    "POST /projects": {"description": "Create project", "domain": "gtd"},
    "GET /projects/{id}": {"description": "Get single project", "domain": "gtd"},
    "PATCH /projects/{id}": {"description": "Update project", "domain": "gtd"},
    "DELETE /projects/{id}": {"description": "Delete project", "domain": "gtd"},
    "POST /projects/{id}/complete": {"description": "Complete project", "domain": "gtd"},
    "POST /projects/{id}/hold": {"description": "Put project on hold", "domain": "gtd"},
    "POST /projects/{id}/activate": {"description": "Reactivate project", "domain": "gtd"},
    "GET /projects/{id}/actions": {"description": "List project actions", "domain": "gtd"},
    "POST /projects/{id}/actions": {"description": "Create action in project", "domain": "gtd"},
    # Areas
    "GET /areas": {"description": "List areas", "domain": "gtd"},
    "POST /areas": {"description": "Create area", "domain": "gtd"},
    "GET /areas/{id}": {"description": "Get single area", "domain": "gtd"},
    "PATCH /areas/{id}": {"description": "Update area", "domain": "gtd"},
    "DELETE /areas/{id}": {"description": "Delete area", "domain": "gtd"},
    "GET /areas/{id}/actions": {"description": "List area actions", "domain": "gtd"},
    "GET /areas/{id}/projects": {"description": "List area projects", "domain": "gtd"},
    # Tags
    "GET /tags": {"description": "List tags", "domain": "gtd"},
    "POST /tags": {"description": "Create tag", "domain": "gtd"},
    "GET /tags/{id}": {"description": "Get single tag", "domain": "gtd"},
    "PATCH /tags/{id}": {"description": "Update tag", "domain": "gtd"},
    "DELETE /tags/{id}": {"description": "Delete tag", "domain": "gtd"},
    "GET /tags/{id}/items": {"description": "List items with tag", "domain": "gtd"},
    # Review
    "GET /review/inbox-count": {"description": "Get inbox count", "domain": "gtd"},
    "GET /review/stale-projects": {"description": "Projects without next actions", "domain": "gtd"},
    "GET /review/upcoming-deadlines": {"description": "Items with approaching deadlines", "domain": "gtd"},
    "GET /review/waiting-for": {"description": "Delegated/waiting items", "domain": "gtd"},
    "GET /review/overdue": {"description": "Past-due items", "domain": "gtd"},
    # Donor Tasks
    "GET /donor-tasks": {"description": "List donor tasks", "domain": "gtd"},
    "GET /donor-tasks/{id}": {"description": "Get single donor task", "domain": "gtd"},
    "PATCH /donor-tasks/{id}/status": {"description": "Update donor task status", "domain": "gtd"},
}

DONOR_ENDPOINTS = {
    # Contacts
    "GET /api/v1/contacts": {"description": "List/search contacts", "domain": "donor"},
    "GET /api/v1/contacts/{id}": {"description": "Get contact detail", "domain": "donor"},
    "GET /api/v1/contacts/{id}/summary": {"description": "Get contact summary (giving, activity, pledges)", "domain": "donor"},
    "POST /api/v1/contacts": {"description": "Create contact", "domain": "donor"},
    "PUT /api/v1/contacts/{id}": {"description": "Update contact", "domain": "donor"},
    "DELETE /api/v1/contacts/{id}": {"description": "Delete contact", "domain": "donor"},
    # Gifts
    "GET /api/v1/gifts": {"description": "List gifts", "domain": "donor"},
    "GET /api/v1/gifts/{id}": {"description": "Get gift detail", "domain": "donor"},
    "POST /api/v1/gifts": {"description": "Create gift", "domain": "donor"},
    "PUT /api/v1/gifts/{id}": {"description": "Update gift", "domain": "donor"},
    "DELETE /api/v1/gifts/{id}": {"description": "Delete gift", "domain": "donor"},
    # History
    "GET /api/v1/history": {"description": "List interaction history", "domain": "donor"},
    "GET /api/v1/history/{id}": {"description": "Get history entry", "domain": "donor"},
    "POST /api/v1/history": {"description": "Create history entry", "domain": "donor"},
    "PUT /api/v1/history/{id}": {"description": "Update history entry", "domain": "donor"},
    "DELETE /api/v1/history/{id}": {"description": "Delete history entry", "domain": "donor"},
    "GET /api/v1/history/types": {"description": "List history types", "domain": "donor"},
    "GET /api/v1/history/results": {"description": "List history results", "domain": "donor"},
    # Tasks
    "GET /api/v1/tasks": {"description": "List donor tasks", "domain": "donor"},
    "GET /api/v1/tasks/{id}": {"description": "Get donor task", "domain": "donor"},
    "POST /api/v1/tasks": {"description": "Create donor task", "domain": "donor"},
    "PUT /api/v1/tasks/{id}": {"description": "Update donor task", "domain": "donor"},
    "DELETE /api/v1/tasks/{id}": {"description": "Delete donor task", "domain": "donor"},
    "GET /api/v1/tasks/types": {"description": "List task types", "domain": "donor"},
    "POST /api/v1/tasks/{id}/complete": {"description": "Complete donor task", "domain": "donor"},
    # Pledges
    "GET /api/v1/pledges": {"description": "List pledges", "domain": "donor"},
    "GET /api/v1/pledges/{id}": {"description": "Get pledge detail", "domain": "donor"},
    "POST /api/v1/pledges": {"description": "Create pledge", "domain": "donor"},
    "PUT /api/v1/pledges/{id}": {"description": "Update pledge", "domain": "donor"},
    "DELETE /api/v1/pledges/{id}": {"description": "Delete pledge", "domain": "donor"},
    "GET /api/v1/pledges/frequencies": {"description": "List pledge frequencies", "domain": "donor"},
    "POST /api/v1/pledges/{id}/deactivate": {"description": "Deactivate pledge", "domain": "donor"},
    # Groups
    "GET /api/v1/groups": {"description": "List groups", "domain": "donor"},
    "GET /api/v1/groups/{id}": {"description": "Get group with members", "domain": "donor"},
    "POST /api/v1/groups": {"description": "Create group", "domain": "donor"},
    "PUT /api/v1/groups/{id}": {"description": "Update group", "domain": "donor"},
    "DELETE /api/v1/groups/{id}": {"description": "Delete group", "domain": "donor"},
    "POST /api/v1/groups/{id}/contacts": {"description": "Add contacts to group", "domain": "donor"},
    "DELETE /api/v1/groups/{id}/contacts": {"description": "Remove contacts from group", "domain": "donor"},
    # Sync
    "POST /api/v1/sync/trigger": {"description": "Trigger DonorHub sync", "domain": "donor"},
    "GET /api/v1/sync/status": {"description": "Get sync status", "domain": "donor"},
    "GET /api/v1/sync/pending": {"description": "List pending sync items", "domain": "donor"},
    "POST /api/v1/sync/pending/{id}/resolve": {"description": "Resolve pending sync item", "domain": "donor"},
    # Export
    "POST /api/v1/export/mailing-list": {"description": "Export mailing list CSV", "domain": "donor"},
}

# Endpoints intentionally NOT covered by skills (admin/infra only)
EXCLUDED_ENDPOINTS = {
    # Auth endpoints — managed via CLI scripts, not agent skills
    "POST /auth/keys",
    "GET /auth/keys/current",
    "DELETE /auth/keys/current",
    # Health checks — covered by agent-status skill but not as API references
    "GET /health",
    # Dashboard — HTML SPA, not an API for agent use
    "GET /dashboard",
    # SSE stream — not meaningful as a skill endpoint
    "GET /events",
    # OAuth flow — browser-based, not suitable for CLI skill
    "GET /api/v1/sync/oauth/authorize",
    "GET /api/v1/sync/oauth/callback",
}
