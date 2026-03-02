# Skills Coverage Expansion — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Expand `agent-skills` to cover the full capabilities of the GTD API (`todo-api`) and Donor Management DB (`sr-assistant`), add cross-system orchestration skills, update stale existing skills, and introduce a skills testing framework to prevent future coverage drift.

**Architecture:** Skills are markdown files (`skills/<name>/SKILL.md`) with YAML frontmatter (name, description, allowed-tools) and structured documentation including API references, example `curl` commands, and behavioral guidance. Each skill is a self-contained prompt that teaches Claude Code how to perform a specific workflow. The testing framework will be a Python script that validates skill files against the live OpenAPI specs of both APIs.

**Tech Stack:** Markdown (skills), Python + pytest (test framework), `curl` via Bash (skill execution), FastAPI OpenAPI specs (validation source)

---

## Overview

### Phases

| Phase | Description | Tasks |
|-------|-------------|-------|
| **Phase 1** | Skills testing framework | Tasks 1–3 |
| **Phase 2** | GTD skills expansion | Tasks 4–9 |
| **Phase 3** | Donor Management skills (new domain) | Tasks 10–14 |
| **Phase 4** | Cross-system & orchestration skills | Tasks 15–17 |
| **Phase 5** | Existing skill updates | Tasks 18–21 |
| **Phase 6** | Documentation & plugin manifest | Tasks 22–23 |

### API Base URLs and Auth

**GTD API:**
- Base: `https://gtd-api.fly.dev` (prod) / `http://localhost:8000` (dev)
- Auth: `X-API-Key` header
- OpenAPI spec: `https://gtd-api.fly.dev/openapi.json`
- Credentials: stored in `/workspace/TOOLS.md`

**Donor Management API:**
- Base: `https://donor-management.fly.dev` (prod) / `http://localhost:8001` (dev)
- Auth: `X-API-Key` header (agent-level keys: `agent_read` or `agent_readwrite`)
- Note: Agent keys strip `confidential_notes` from responses and silently drop them on writes — this is by design
- Credentials: will need to be added to `/workspace/TOOLS.md`

---

## Phase 1: Skills Testing Framework

### Task 1: Design and implement the skills linter

**Files:**
- Create: `tests/test_skills.py`
- Create: `tests/conftest.py`
- Create: `pyproject.toml` (minimal, for pytest + httpx)

This task creates a Python test suite that validates skill files structurally without requiring live API access.

**Step 1: Create `pyproject.toml`**

```toml
[project]
name = "agent-skills-tests"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "pytest>=8.0",
    "pyyaml>=6.0",
]

[project.optional-dependencies]
api = [
    "httpx>=0.27",
]
```

**Step 2: Create `tests/conftest.py`**

Shared fixtures:
- `skills_dir` → path to `skills/` directory
- `all_skill_paths` → list of all `SKILL.md` file paths
- `skill_frontmatter(path)` → parsed YAML frontmatter for a skill
- `readme_content` → contents of `README.md`

**Step 3: Create `tests/test_skills.py`**

Structural tests (no network required):

```python
# 1. Every directory under skills/ has a SKILL.md file
def test_every_skill_dir_has_skill_md(skills_dir):
    ...

# 2. Every SKILL.md has valid YAML frontmatter with required fields
@pytest.mark.parametrize("skill_path", ALL_SKILLS)
def test_frontmatter_has_required_fields(skill_path):
    """Must have: name, description. Optional: allowed-tools."""
    ...

# 3. Every SKILL.md has at least one curl command or API reference
@pytest.mark.parametrize("skill_path", ALL_SKILLS)
def test_skill_has_api_reference(skill_path):
    """Skills that interact with APIs must document their endpoints."""
    ...

# 4. No skill references a hardcoded API key
@pytest.mark.parametrize("skill_path", ALL_SKILLS)
def test_no_hardcoded_credentials(skill_path):
    ...

# 5. Every skill directory listed in skills/ is documented in README.md
@pytest.mark.parametrize("skill_path", ALL_SKILLS)
def test_skill_documented_in_readme(skill_path, readme_content):
    ...

# 6. Skill names are consistent (dir name matches frontmatter name, or is a known alias)
@pytest.mark.parametrize("skill_path", ALL_SKILLS)
def test_skill_name_consistency(skill_path):
    ...
```

**Step 4: Run tests and verify they pass against the existing 21 skills**

Run: `cd /workspaces/agent-skills && uv run pytest tests/ -v`
Expected: All tests pass (fix any existing skills that fail structural checks)

**Step 5: Commit**

```bash
git add pyproject.toml tests/
git commit -m "feat: add skills linter test suite (structural validation)"
```

---

### Task 2: Add API coverage tests

**Files:**
- Create: `tests/test_api_coverage.py`
- Create: `tests/api_specs.py` (endpoint registry)

These tests validate that every API endpoint in the GTD and Donor Management APIs is referenced by at least one skill. This is the key "documentation test" that prevents future coverage gaps.

**Step 1: Create `tests/api_specs.py`**

A registry of all endpoints from both APIs, grouped by domain:

```python
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
```

**Step 2: Create `tests/test_api_coverage.py`**

```python
import re
from pathlib import Path
from tests.api_specs import GTD_ENDPOINTS, DONOR_ENDPOINTS, EXCLUDED_ENDPOINTS

def _all_skill_contents(skills_dir: Path) -> str:
    """Concatenate all SKILL.md files into one searchable string."""
    ...

def _endpoint_referenced(endpoint: str, content: str) -> bool:
    """Check if an endpoint pattern appears in the skill content.

    Matches patterns like:
    - "GET /inbox" or "POST /inbox/{id}/process"
    - curl command URLs containing the path
    - Plain path references like "/inbox" or "/next-actions"
    """
    ...

@pytest.mark.parametrize("endpoint",
    [e for e in {**GTD_ENDPOINTS, **DONOR_ENDPOINTS} if e not in EXCLUDED_ENDPOINTS])
def test_endpoint_has_skill_coverage(endpoint, skills_dir):
    """Every API endpoint must be referenced in at least one skill."""
    content = _all_skill_contents(skills_dir)
    assert _endpoint_referenced(endpoint, content), (
        f"Endpoint {endpoint} is not referenced in any skill. "
        f"Description: {({**GTD_ENDPOINTS, **DONOR_ENDPOINTS})[endpoint]['description']}"
    )
```

**Step 3: Run tests — they SHOULD fail for all uncovered endpoints**

Run: `cd /workspaces/agent-skills && uv run pytest tests/test_api_coverage.py -v`
Expected: Many failures — this is the "gap detector". Each failure = a missing skill reference.

**Step 4: Commit**

```bash
git add tests/
git commit -m "feat: add API coverage tests (gap detector for skill coverage)"
```

---

### Task 3: Add OpenAPI spec sync test (optional, network-dependent)

**Files:**
- Create: `tests/test_openapi_sync.py`

This test fetches live OpenAPI specs and checks that our endpoint registry (`api_specs.py`) is up to date. Marked with `@pytest.mark.network` so it only runs explicitly.

**Step 1: Create `tests/test_openapi_sync.py`**

```python
import pytest
httpx = pytest.importorskip("httpx")

GTD_OPENAPI_URL = "https://gtd-api.fly.dev/openapi.json"
DONOR_OPENAPI_URL = "https://donor-management.fly.dev/openapi.json"

@pytest.mark.network
def test_gtd_spec_in_sync():
    """Verify our GTD endpoint registry matches the live OpenAPI spec."""
    ...

@pytest.mark.network
def test_donor_spec_in_sync():
    """Verify our Donor endpoint registry matches the live OpenAPI spec."""
    ...
```

Run: `uv run pytest tests/test_openapi_sync.py -m network -v`

**Step 2: Commit**

```bash
git add tests/test_openapi_sync.py
git commit -m "feat: add OpenAPI sync tests (network-dependent)"
```

---

## Phase 2: GTD Skills Expansion

### Task 4: Create `gtd-weekly-review` skill

**Files:**
- Create: `skills/gtd-weekly-review/SKILL.md`

This is the highest-value missing skill. It orchestrates the full GTD weekly review ceremony.

**Skill content covers:**
- Invocation triggers: "weekly review", "review my system", "Friday review"
- Review workflow steps:
  1. Check inbox count (`GET /review/inbox-count`) → if non-zero, prompt to process first
  2. Review overdue items (`GET /review/overdue`) → decide: reschedule, complete, or delete
  3. Review upcoming deadlines (`GET /review/upcoming-deadlines?days=7`)
  4. Review waiting-for items (`GET /review/waiting-for`) → follow up or update
  5. Review stale projects (`GET /review/stale-projects`) → add next action, hold, or complete
  6. Review someday/maybe (`GET /someday-maybe`) → activate any that are now timely
  7. Check today's tickler (`GET /tickler/today`) → surface or snooze
  8. Check donor tasks (`GET /donor-tasks?status=next_action`) → surface any due
- Summary format at end of review
- All API references with curl commands

**Step 1: Write the skill file**

(Full SKILL.md content — see skill format from existing skills for structure)

**Step 2: Run structural tests**

Run: `uv run pytest tests/test_skills.py -v -k "gtd-weekly-review"`

**Step 3: Commit**

```bash
git add skills/gtd-weekly-review/
git commit -m "feat: add gtd-weekly-review skill (orchestrates full GTD review)"
```

---

### Task 5: Create `gtd-projects` skill

**Files:**
- Create: `skills/gtd-projects/SKILL.md`

**Skill covers:**
- Invocation triggers: "show projects", "create a project", "what are my projects", "project status"
- CRUD operations:
  - `GET /projects` — list all projects (with stats: action count, completion %)
  - `POST /projects` — create: `{ "title", "outcome", "area_id", "due_date" }`
  - `GET /projects/{id}` — detail with stats
  - `PATCH /projects/{id}` — update
  - `DELETE /projects/{id}` — delete
- Lifecycle operations:
  - `POST /projects/{id}/complete` — mark done
  - `POST /projects/{id}/hold` — put on hold
  - `POST /projects/{id}/activate` — reactivate from hold
- Action management within projects:
  - `GET /projects/{id}/actions` — list actions for a project
  - `POST /projects/{id}/actions` — create an action directly in a project
- Decision guide: when to create a project vs. a next action
- Stale project detection: `GET /review/stale-projects`

**Step 1: Write the skill file**
**Step 2: Run structural tests**
**Step 3: Commit**

```bash
git add skills/gtd-projects/
git commit -m "feat: add gtd-projects skill (project lifecycle management)"
```

---

### Task 6: Create `gtd-review-actions` skill

**Files:**
- Create: `skills/gtd-review-actions/SKILL.md`

**Skill covers:**
- Invocation triggers: "what should I do?", "show my next actions", "what can I do in 15 minutes?", "low energy tasks", "what's due this week?"
- Query with filters:
  - `GET /next-actions` with query params:
    - `?tag_id=` — filter by context (@home, @phone, etc.)
    - `?project_id=` — filter by project
    - `?area_id=` — filter by area
    - `?energy_level=low|medium|high` — filter by energy
    - `?max_time=15` — filter by time estimate (minutes)
    - `?due_before=2026-03-05` — deadline filter
    - `?has_deadline=true` — only items with deadlines
    - `?include_completed=true` — show completed items too
- Item detail: `GET /next-actions/{id}`
- Update: `PATCH /next-actions/{id}` (change energy, time estimate, tags, due date, etc.)
- Defer: `POST /next-actions/{id}/defer` — move to someday/maybe
- Complete: `POST /next-actions/{id}/complete`
- Natural language examples mapping to filter combinations

**Step 1: Write the skill file**
**Step 2: Run structural tests**
**Step 3: Commit**

```bash
git add skills/gtd-review-actions/
git commit -m "feat: add gtd-review-actions skill (filtered next action queries)"
```

---

### Task 7: Create `gtd-someday-maybe` skill

**Files:**
- Create: `skills/gtd-someday-maybe/SKILL.md`

**Skill covers:**
- Invocation triggers: "show someday list", "someday/maybe", "maybe I should...", "park this for later", "activate that idea"
- Operations:
  - `GET /someday-maybe` — list all (with filters: area_id, project_id, tag_id)
  - `GET /someday-maybe/{id}` — detail
  - `POST /someday-maybe` — create directly (not via inbox processing)
  - `PATCH /someday-maybe/{id}` — update
  - `DELETE /someday-maybe/{id}` — delete
  - `POST /someday-maybe/{id}/activate` — move to next actions
  - `POST /someday-maybe/{id}/complete` — mark complete without activating
- Review guidance: during weekly review, scan for items whose time has come

**Step 1: Write the skill file**
**Step 2: Run structural tests**
**Step 3: Commit**

```bash
git add skills/gtd-someday-maybe/
git commit -m "feat: add gtd-someday-maybe skill"
```

---

### Task 8: Create `gtd-tickler` skill

**Files:**
- Create: `skills/gtd-tickler/SKILL.md`

**Skill covers:**
- Invocation triggers: "remind me on [date]", "tickler", "what's coming up?", "deferred items"
- Operations:
  - `GET /tickler` — list all
  - `GET /tickler/today` — items surfacing today
  - `GET /tickler/{id}` — detail
  - `POST /tickler` — create with `tickler_date`
  - `PATCH /tickler/{id}` — update (change date, etc.)
  - `DELETE /tickler/{id}` — delete
  - `POST /tickler/{id}/surface` — manually surface to next actions now
  - `POST /tickler/{id}/complete` — complete without surfacing
- Behavior: explain that tickler items automatically surface on their `tickler_date`

**Step 1: Write the skill file**
**Step 2: Run structural tests**
**Step 3: Commit**

```bash
git add skills/gtd-tickler/
git commit -m "feat: add gtd-tickler skill"
```

---

### Task 9: Create `gtd-organize` skill (areas + tags)

**Files:**
- Create: `skills/gtd-organize/SKILL.md`

Combines areas and tags into one "organize your system" skill rather than two tiny skills.

**Skill covers:**
- Invocation triggers: "show my areas", "create an area", "what tags do I have?", "create a tag", "organize"
- Areas:
  - `GET /areas` — list all (with stats: action count, project count)
  - `GET /areas/{id}` — detail
  - `POST /areas` — create: `{ "name", "description" }`
  - `PATCH /areas/{id}` — update
  - `DELETE /areas/{id}` — delete
  - `GET /areas/{id}/actions` — all actions in an area
  - `GET /areas/{id}/projects` — all projects in an area
- Tags:
  - `GET /tags` — list all (with item counts)
  - `GET /tags/{id}` — detail
  - `POST /tags` — create: `{ "name", "color" }`
  - `PATCH /tags/{id}` — update
  - `DELETE /tags/{id}` — delete
  - `GET /tags/{id}/items` — all items with a tag
- Context tags convention: `@home`, `@phone`, `@computer`, `@errands`, `@waiting_for`

**Step 1: Write the skill file**
**Step 2: Run structural tests**
**Step 3: Commit**

```bash
git add skills/gtd-organize/
git commit -m "feat: add gtd-organize skill (areas + tags management)"
```

---

## Phase 3: Donor Management Skills

### Task 10: Create `donor-ask` skill

**Files:**
- Create: `skills/donor-ask/SKILL.md`

Read-only skill for querying the donor management system. The most natural conversational skill.

**Skill covers:**
- Invocation triggers: "tell me about [person]", "look up [name]", "who is [name]?", "donor info", "contact search"
- Search: `GET /api/v1/contacts?search=<query>` — searches first_name, last_name, org_name, file_as
- Detail: `GET /api/v1/contacts/{id}` — full contact with addresses, phones, emails
- Summary: `GET /api/v1/contacts/{id}/summary` — computed giving stats, activity dates, pledge amounts
- Giving history: `GET /api/v1/gifts?contact_id={id}` — list all gifts for a contact
- Interaction history: `GET /api/v1/history?contact_id={id}` — past calls, visits, letters
- Active pledges: `GET /api/v1/pledges?contact_id={id}&active_only=true`
- Pending tasks: `GET /api/v1/tasks?contact_id={id}&status=pending`
- Presentation format: how to synthesize a natural "tell me about John" response from multiple API calls
- Important: agent keys do NOT see `confidential_notes` — this is by design, do not mention or ask about them

**Auth note in skill:**
```
Endpoint and credentials in `/workspace/TOOLS.md`.
Auth: X-API-Key header (agent_read or agent_readwrite key).
Base URL: https://donor-management.fly.dev
```

**Step 1: Write the skill file**
**Step 2: Run structural tests**
**Step 3: Commit**

```bash
git add skills/donor-ask/
git commit -m "feat: add donor-ask skill (read-only donor/contact queries)"
```

---

### Task 11: Create `donor-log` skill

**Files:**
- Create: `skills/donor-log/SKILL.md`

Write skill to log interactions with donors. This is high-value because it captures relationship activity from within conversation.

**Skill covers:**
- Invocation triggers: "I just called [name]", "log a visit with [name]", "record that I sent a letter to [name]", "note that interaction"
- Prerequisite: look up contact first (`GET /api/v1/contacts?search=`) to get contact ID
- Look up types: `GET /api/v1/history/types` — returns: Call, Letter, Email, Visit, Newsletter, Thank, etc. (each has `affects_last_call`, `affects_last_letter`, `affects_last_visit` flags)
- Look up results: `GET /api/v1/history/results` — returns: Done, Attempted, Received, Left Message, etc.
- Create: `POST /api/v1/history`
  ```json
  {
    "history_date": "2026-03-02T10:00:00",
    "history_type_id": 1,
    "history_result_id": 1,
    "description": "Called about pledge renewal",
    "notes": "Discussed family updates...",
    "is_thank": false,
    "is_challenge": false,
    "contact_ids": [42]
  }
  ```
- Multi-contact: can link one interaction to multiple contacts (e.g., "visited John and Jane Smith")
- Important: agent keys cannot write `confidential_notes` — the field is silently dropped. Do not include it.
- Clarification prompts: determine type, result, and contacts before creating
- After logging: show confirmation with contact name, type, date

**Step 1: Write the skill file**
**Step 2: Run structural tests**
**Step 3: Commit**

```bash
git add skills/donor-log/
git commit -m "feat: add donor-log skill (log interactions with donors)"
```

---

### Task 12: Create `donor-gifts` skill

**Files:**
- Create: `skills/donor-gifts/SKILL.md`

Read-oriented skill for querying giving data. Can also record manual gifts (e.g., IRA distributions).

**Skill covers:**
- Invocation triggers: "who gave recently?", "giving report", "how much has [name] given?", "record a gift"
- List gifts: `GET /api/v1/gifts` — all gifts, or `?contact_id={id}` for a specific donor
- Gift detail: `GET /api/v1/gifts/{id}` — includes splits (campaign/promise allocation)
- Contact giving summary: `GET /api/v1/contacts/{id}/summary` — computed stats (lifetime, YTD, 12-month, etc.)
- Create manual gift: `POST /api/v1/gifts` — for gifts that don't come through DonorHub (e.g., IRA distributions)
  ```json
  {
    "contact_id": 42,
    "gift_date": "2026-03-01",
    "amount": 500.00,
    "memo": "IRA distribution",
    "payment_method": "check"
  }
  ```
  Note: `external_gift_code` should be null for manual gifts — this prevents sync from touching them.
- Update: `PUT /api/v1/gifts/{id}` — only memo and payment_method are updatable
- Presentation: format currency amounts, summarize giving patterns

**Step 1: Write the skill file**
**Step 2: Run structural tests**
**Step 3: Commit**

```bash
git add skills/donor-gifts/
git commit -m "feat: add donor-gifts skill (giving queries and manual gift entry)"
```

---

### Task 13: Create `donor-tasks` skill

**Files:**
- Create: `skills/donor-tasks/SKILL.md`

Manage donor-related tasks (thank-you calls, follow-ups, etc.) and the cross-system donor task integration.

**Skill covers:**
- Invocation triggers: "show my donor tasks", "thank-you tasks", "what donor follow-ups do I have?"
- Donor DB tasks (direct):
  - `GET /api/v1/tasks?status=pending` — pending tasks from donor DB
  - `GET /api/v1/tasks/{id}` — task detail
  - `POST /api/v1/tasks/{id}/complete` — complete a task
  - `GET /api/v1/tasks/types` — list task types (Thank, Call, Letter, etc.)
- GTD donor tasks (cross-system, via todo-api):
  - `GET https://gtd-api.fly.dev/donor-tasks` — donor tasks visible in GTD system
  - `PATCH https://gtd-api.fly.dev/donor-tasks/{id}/status` — push completion back to donor DB
- Decision guide: explain that donor tasks auto-generate (via `auto_tasks.py` rules):
  - First gift → thank-you task
  - Returning donor (18+ months gap) → thank-you task
  - Large gift (>1.5x average) → thank-you task
- Create task manually: `POST /api/v1/tasks`
  ```json
  {
    "task_type_id": 1,
    "description": "Call to thank for first gift of $100",
    "task_date": "2026-03-02",
    "status": "pending",
    "is_thank": true,
    "contact_ids": [42]
  }
  ```

**Step 1: Write the skill file**
**Step 2: Run structural tests**
**Step 3: Commit**

```bash
git add skills/donor-tasks/
git commit -m "feat: add donor-tasks skill (donor task management + GTD integration)"
```

---

### Task 14: Create `donor-sync` skill

**Files:**
- Create: `skills/donor-sync/SKILL.md`

Trigger and monitor DonorHub sync operations.

**Skill covers:**
- Invocation triggers: "sync donations", "run sync", "sync status", "any pending sync items?"
- Trigger sync: `POST /api/v1/sync/trigger` — runs donation import from DonorHub
- Check status: `GET /api/v1/sync/status` — connection state + last 10 sync log entries
- Pending items: `GET /api/v1/sync/pending` — items needing manual review (e.g., address conflicts)
- Resolve pending: `POST /api/v1/sync/pending/{id}/resolve` — mark a pending item as resolved
- Export mailing list: `POST /api/v1/export/mailing-list` — streams CSV of newsletter recipients
- Pledge management (also fits here since it's about ongoing support relationships):
  - `GET /api/v1/pledges` — list all pledges, or `?contact_id={id}`
  - `GET /api/v1/pledges/{id}` — detail with frequency info
  - `POST /api/v1/pledges` — create pledge
  - `PUT /api/v1/pledges/{id}` — update
  - `POST /api/v1/pledges/{id}/deactivate` — mark inactive
  - `GET /api/v1/pledges/frequencies` — monthly, quarterly, semi-annual, annual

**Step 1: Write the skill file**
**Step 2: Run structural tests**
**Step 3: Commit**

```bash
git add skills/donor-sync/
git commit -m "feat: add donor-sync skill (DonorHub sync + pledge management)"
```

---

## Phase 4: Cross-System & Orchestration Skills

### Task 15: Create `donor-contact-manage` skill

**Files:**
- Create: `skills/donor-contact-manage/SKILL.md`

Write skill for creating and updating contacts, and managing groups. Separated from `donor-ask` (read) to keep the approval gate clear.

**Skill covers:**
- Create contact: `POST /api/v1/contacts` with nested addresses, phones, emails
- Update contact: `PUT /api/v1/contacts/{id}`
- Delete contact: `DELETE /api/v1/contacts/{id}`
- Groups:
  - `GET /api/v1/groups` — list groups
  - `GET /api/v1/groups/{id}` — group with members
  - `POST /api/v1/groups` — create group
  - `PUT /api/v1/groups/{id}` — update
  - `DELETE /api/v1/groups/{id}` — delete
  - `POST /api/v1/groups/{id}/contacts` — add contacts to group
  - `DELETE /api/v1/groups/{id}/contacts` — remove contacts from group

**Step 1: Write the skill file**
**Step 2: Run structural tests**
**Step 3: Commit**

```bash
git add skills/donor-contact-manage/
git commit -m "feat: add donor-contact-manage skill (contact CRUD + groups)"
```

---

### Task 16: Create `gtd-donor-tasks` skill

**Files:**
- Create: `skills/gtd-donor-tasks/SKILL.md`

Dedicated skill for the cross-system donor task workflow from the GTD perspective.

**Skill covers:**
- Invocation triggers: "show donor tasks in GTD", "complete that donor task"
- List: `GET /donor-tasks` (on GTD API) — donor tasks mapped to GTD domain
- Detail: `GET /donor-tasks/{id}`
- Complete: `PATCH /donor-tasks/{id}/status` with `{"status": "completed"}` — pushes back to donor DB
- Delete: `PATCH /donor-tasks/{id}/status` with `{"status": "deleted"}` — maps to "cancelled" in donor DB
- Consistency check: `GET /donor-tasks/consistency` — compare cache vs. live data
- Explain the flow: donor DB auto-generates tasks → GTD API reads them → agent can complete → status pushed back

**Step 1: Write the skill file**
**Step 2: Run structural tests**
**Step 3: Commit**

```bash
git add skills/gtd-donor-tasks/
git commit -m "feat: add gtd-donor-tasks skill (cross-system donor task management)"
```

---

### Task 17: Update `briefing-morning` for full system coverage

**Files:**
- Modify: `skills/briefing-morning/SKILL.md`

Extend the morning briefing to include GTD and donor data.

**Changes:**
- Add Step 1.5: GTD Status Check
  - `GET /review/inbox-count` — inbox items waiting
  - `GET /review/overdue` — past-due items
  - `GET /tickler/today` — items surfacing today
  - `GET /review/upcoming-deadlines?days=1` — deadlines today
- Add Step 1.75: Donor Task Check
  - `GET /donor-tasks?status=next_action` (on GTD API) — pending donor tasks
  - Or `GET /api/v1/tasks?status=pending` (on donor DB) — pending donor tasks
- Update Step 3 (Synthesize) to include:
  - GTD inbox count and overdue items
  - Today's tickler items
  - Pending donor follow-ups
  - Priority synthesis across all four domains (email, calendar, GTD, donor)

**Step 1: Edit the skill file**
**Step 2: Run structural tests**
**Step 3: Commit**

```bash
git add skills/briefing-morning/
git commit -m "feat: extend morning briefing with GTD + donor data"
```

---

## Phase 5: Existing Skill Updates

### Task 18: Update `agent-status` to check all services

**Files:**
- Modify: `skills/agent-status/SKILL.md`

**Changes:**
Add health checks for:
- GTD API: `curl -s -o /dev/null -w "%{http_code}" "https://gtd-api.fly.dev/health"`
- Donor DB: `curl -s -o /dev/null -w "%{http_code}" "https://donor-management.fly.dev/health"`

Read base URLs from `/workspace/TOOLS.md` where possible.

**Step 1: Edit the skill file**
**Step 2: Run structural tests**
**Step 3: Commit**

```bash
git add skills/agent-status/
git commit -m "feat: add GTD API and Donor DB health checks to agent-status"
```

---

### Task 19: Update `gtd-capture` with tag support

**Files:**
- Modify: `skills/gtd-capture/SKILL.md`

**Changes:**
- Add `tag_ids` to the capture API reference (the API already accepts it, but the skill doesn't mention it)
- Add guidance: "If the item has an obvious context (e.g., 'call John' → @phone tag), set the tag at capture time"
- Add `GET /tags` reference for listing available tags

**Step 1: Edit the skill file**
**Step 2: Run structural tests**
**Step 3: Commit**

```bash
git add skills/gtd-capture/
git commit -m "feat: add tag support to gtd-capture skill"
```

---

### Task 20: Update `gtd-process-inbox` — verify area_id workaround

**Files:**
- Modify: `skills/gtd-process-inbox/SKILL.md` (if needed)

**Action:**
1. Check the todo-api source code to see if the `area_id` bug has been fixed
2. If fixed: remove the workaround documentation
3. If still present: keep the workaround, add a note about which API version this applies to

**Step 1: Check the code**

Read: `/workspaces/todo-api/app/routers/inbox.py` — look at the `/process` endpoint implementation

**Step 2: Update skill if needed**
**Step 3: Commit (if changes made)**

---

### Task 21: Update `gtd-complete` with donor task completion

**Files:**
- Modify: `skills/gtd-complete/SKILL.md`

**Changes:**
- Add donor tasks as a completable list: `PATCH /donor-tasks/{id}/status` with `{"status": "completed"}`
- Add guidance: "If the user says 'done' about a donor task (thank-you call, etc.), use the donor task endpoint"
- Note the different HTTP method (PATCH vs POST) and body format

**Step 1: Edit the skill file**
**Step 2: Run structural tests**
**Step 3: Commit**

```bash
git add skills/gtd-complete/
git commit -m "feat: add donor task completion to gtd-complete skill"
```

---

## Phase 6: Documentation & Plugin Manifest

### Task 22: Update README.md

**Files:**
- Modify: `README.md`

**Changes:**
- Add "Donor Management Skills" section to the features table
- Add GTD skills that were added (weekly-review, projects, review-actions, someday-maybe, tickler, organize, donor-tasks)
- Update project structure tree
- Add donor management API to prerequisites and configuration
- Add `DONOR_DB_URL` and `DONOR_DB_API_KEY` to configuration table (or note that creds are in TOOLS.md)
- Update skill count in description
- Add Testing section explaining `uv run pytest tests/ -v`

**Step 1: Edit README.md**
**Step 2: Run structural tests (including README coverage check)**

Run: `uv run pytest tests/test_skills.py -v -k "readme"`

**Step 3: Commit**

```bash
git add README.md
git commit -m "docs: update README with new skills and testing instructions"
```

---

### Task 23: Update plugin manifest

**Files:**
- Modify: `.claude-plugin/plugin.json`

**Changes:**
- Bump version to `0.3.0` (new feature release)
- Update description to mention donor management

**Step 1: Edit plugin.json**
**Step 2: Commit**

```bash
git add .claude-plugin/plugin.json
git commit -m "chore: bump plugin version to 0.3.0"
```

---

## Summary

### Skills Inventory After Completion

| Domain | Before | After | Net New |
|--------|--------|-------|---------|
| Email | 6 | 6 | 0 |
| Calendar | 10 | 10 | 0 |
| GTD | 3 | 9 | +6 |
| Donor Management | 0 | 6 | +6 |
| Cross-System | 2 | 2 | 0 (updated) |
| **Total** | **21** | **33** | **+12** |

### New Skills

1. `gtd-weekly-review` — Full GTD weekly review ceremony
2. `gtd-projects` — Project lifecycle management
3. `gtd-review-actions` — Filtered next action queries
4. `gtd-someday-maybe` — Someday/maybe management
5. `gtd-tickler` — Tickler/deferred items
6. `gtd-organize` — Areas of responsibility + tags
7. `donor-ask` — Read-only donor/contact queries
8. `donor-log` — Log interactions with donors
9. `donor-gifts` — Giving data queries + manual gift entry
10. `donor-tasks` — Donor task management
11. `donor-sync` — DonorHub sync + pledge management
12. `donor-contact-manage` — Contact CRUD + group management
13. `gtd-donor-tasks` — Cross-system donor tasks from GTD perspective

### Updated Skills

1. `briefing-morning` — Now includes GTD + donor data
2. `agent-status` — Now checks GTD API + Donor DB health
3. `gtd-capture` — Tag support added
4. `gtd-process-inbox` — Area_id workaround verified/updated
5. `gtd-complete` — Donor task completion added

### Testing Framework

- `tests/test_skills.py` — Structural validation (frontmatter, API refs, credentials, README coverage)
- `tests/test_api_coverage.py` — Endpoint gap detection (every API endpoint must be in at least one skill)
- `tests/test_openapi_sync.py` — Live OpenAPI spec sync verification (network-dependent)
- Run: `uv run pytest tests/ -v` (structural) or `uv run pytest tests/ -v -m network` (full)
