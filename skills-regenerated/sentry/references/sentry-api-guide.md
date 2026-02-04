# Sentry API Quick Reference

## Authentication

All requests require a Bearer token in the `Authorization` header. Tokens are created at `https://sentry.io/settings/account/api/auth-tokens/`.

Required read-only scopes:
- `project:read` — list projects and their issues
- `event:read` — retrieve events and event details
- `org:read` — list organizations and teams

## Endpoints

### List Issues

```
GET /api/0/projects/{org_slug}/{project_slug}/issues/
```

Query parameters:
- `query` — Sentry search syntax (e.g., `is:unresolved`, `assigned:me`, `PROJ-123`)
- `statsPeriod` — time window: `1h`, `24h`, `7d`, `14d`, `30d`, `90d`
- `environment` — filter by environment name
- `per_page` — results per page (max 100)
- `cursor` — pagination cursor from Link header

Response fields per issue:
- `id` — numeric issue ID (use for detail/events calls)
- `shortId` — human-readable ID like `PROJ-123`
- `title` — error message summary
- `status` — `unresolved`, `resolved`, `ignored`, `muted`
- `firstSeen` — ISO 8601 timestamp
- `lastSeen` — ISO 8601 timestamp
- `count` — total event count
- `userCount` — unique users affected
- `assignedTo` — assigned team member or null
- `metadata.type` — error type classification
- `metadata.value` — error value/message

### Issue Detail

```
GET /api/0/issues/{issue_id}/
```

Returns the full issue object including tags, activity log, and stats.

### Issue Events

```
GET /api/0/issues/{issue_id}/events/
```

Query parameters:
- `per_page` — results per page
- `cursor` — pagination cursor

Response fields per event:
- `eventID` — unique event identifier
- `dateCreated` — ISO 8601 timestamp
- `context` — runtime context data
- `tags` — key-value tag pairs
- `entries` — stack trace and other detailed data (large)

### Event Detail

```
GET /api/0/projects/{org_slug}/{project_slug}/events/{event_id}/
```

Returns the full event object. The `entries` field contains stack traces and request data and can be very large.

## Pagination

Sentry uses cursor-based pagination via the `Link` response header:

```
Link: <url>; rel="previous"; results="false"; cursor="...",
      <url>; rel="next"; results="true"; cursor="..."
```

Continue fetching while `rel="next"` has `results="true"`. Extract the cursor value and pass it as a query parameter.

## Rate Limits

Sentry enforces per-token rate limits. Response headers indicate current usage:
- `X-Sentry-Rate-Limit-Limit` — requests allowed per window
- `X-Sentry-Rate-Limit-Remaining` — requests remaining
- `X-Sentry-Rate-Limit-Reset` — window reset timestamp

On HTTP 429, wait and retry. The bundled script retries once after a 1-second delay.

## Search Query Syntax

Common search qualifiers for the `query` parameter:
- `is:unresolved` — only unresolved issues
- `is:resolved` — only resolved issues
- `assigned:username` — assigned to a specific user
- `assigned:me` — assigned to the token owner
- `!has:assignee` — unassigned issues
- `first-release:1.0.0` — first seen in a specific release
- `release:1.0.0` — associated with a release
- `platform:python` — filter by platform
- `PROJ-123` — search by short ID

## Self-Hosted Sentry

For self-hosted instances, set `SENTRY_BASE_URL` to your instance URL (e.g., `https://sentry.mycompany.com`). All endpoints remain the same.

## Common Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| 401 | Invalid or expired token | Regenerate token |
| 403 | Insufficient scopes | Add required scopes to token |
| 404 | Resource not found | Verify org/project/issue ID |
| 429 | Rate limited | Wait and retry |
| 500+ | Server error | Retry after delay |
