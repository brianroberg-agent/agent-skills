---
name: agent-status
description: Check the health of all agent servers
allowed-tools: Bash
---

# Agent Status

Check the health of all agent servers. Useful for debugging connectivity issues.

## Usage

When this skill is invoked, check the health endpoints of both agent servers:

### Check Email Agent

```bash
if [ -n "$EMAIL_AGENT_URL" ]; then
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$EMAIL_AGENT_URL/health" 2>/dev/null)
    if [ "$STATUS" = "200" ]; then
        echo "Email Agent ($EMAIL_AGENT_URL): OK"
    else
        echo "Email Agent ($EMAIL_AGENT_URL): UNREACHABLE (HTTP $STATUS)"
    fi
else
    echo "Email Agent: NOT CONFIGURED (EMAIL_AGENT_URL not set)"
fi
```

### Check Calendar Agent

```bash
if [ -n "$CALENDAR_AGENT_URL" ]; then
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$CALENDAR_AGENT_URL/health" 2>/dev/null)
    if [ "$STATUS" = "200" ]; then
        echo "Calendar Agent ($CALENDAR_AGENT_URL): OK"
    else
        echo "Calendar Agent ($CALENDAR_AGENT_URL): UNREACHABLE (HTTP $STATUS)"
    fi
else
    echo "Calendar Agent: NOT CONFIGURED (CALENDAR_AGENT_URL not set)"
fi
```

### Check GTD API

```bash
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://gtd-api.fly.dev/health" 2>/dev/null)
if [ "$STATUS" = "200" ]; then
    echo "GTD API (https://gtd-api.fly.dev): OK"
else
    echo "GTD API (https://gtd-api.fly.dev): UNREACHABLE (HTTP $STATUS)"
fi
```

### Check Donor Management DB

```bash
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://donor-management.fly.dev/health" 2>/dev/null)
if [ "$STATUS" = "200" ]; then
    echo "Donor DB (https://donor-management.fly.dev): OK"
else
    echo "Donor DB (https://donor-management.fly.dev): UNREACHABLE (HTTP $STATUS)"
fi
```

## Expected Output

When all services are running:
```
Email Agent (http://100.x.x.x:8081): OK
Calendar Agent (http://localhost:8082): OK
GTD API (https://gtd-api.fly.dev): OK
Donor DB (https://donor-management.fly.dev): OK
```

When a service is down:
```
Email Agent (http://100.x.x.x:8081): UNREACHABLE (HTTP 000)
Calendar Agent (http://localhost:8082): OK
GTD API (https://gtd-api.fly.dev): OK
Donor DB (https://donor-management.fly.dev): UNREACHABLE (HTTP 503)
```
