#!/usr/bin/env python3
"""Read-only Sentry API helper for querying issues and events.

Provides deterministic API access to Sentry's issue and event endpoints.
Handles pagination, transient error retries, and automatic PII redaction.

Usage:
    python3 sentry_api.py list-issues --org ORG --project PROJ [--time-range 24h] [--limit 20]
    python3 sentry_api.py issue-detail ISSUE_ID
    python3 sentry_api.py issue-events ISSUE_ID [--limit 20]
    python3 sentry_api.py event-detail EVENT_ID --org ORG --project PROJ [--include-entries]

Environment variables:
    SENTRY_AUTH_TOKEN  (required) Bearer token with read-only scopes
    SENTRY_ORG         (optional) Default organization slug
    SENTRY_PROJECT     (optional) Default project slug
    SENTRY_BASE_URL    (optional) Base URL, defaults to https://sentry.io
"""

import argparse
import json
import os
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

DEFAULT_BASE_URL = "https://sentry.io"
DEFAULT_ORG = "your-org"
DEFAULT_PROJECT = "your-project"
MAX_LIMIT = 50
MAX_RETRIES = 1
RETRY_DELAY_SECONDS = 1

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")

PII_FIELD_NAMES = frozenset({"email", "ip", "ip_address", "user_ip", "remote_addr"})


def redact_string(value: str) -> str:
    """Replace email addresses and IP addresses with redaction markers."""
    value = EMAIL_RE.sub("[REDACTED_EMAIL]", value)
    value = IP_RE.sub("[REDACTED_IP]", value)
    return value


def redact_data(value: object) -> object:
    """Recursively redact PII from API response data."""
    if isinstance(value, str):
        return redact_string(value)
    if isinstance(value, list):
        return [redact_data(item) for item in value]
    if isinstance(value, dict):
        redacted = {}
        for key, item in value.items():
            if key.lower() in PII_FIELD_NAMES:
                redacted[key] = "[REDACTED]"
            else:
                redacted[key] = redact_data(item)
        return redacted
    return value


def parse_next_cursor(link_header: str | None) -> str | None:
    """Extract the next page cursor from Sentry's Link header."""
    if not link_header:
        return None
    for part in link_header.split(","):
        if 'rel="next"' in part and 'results="true"' in part:
            match = re.search(r'cursor="([^"]+)"', part)
            if match:
                return match.group(1)
    return None


def request_json(url: str, token: str, retries: int = MAX_RETRIES) -> tuple[object, object]:
    """Execute authenticated GET request with retry on transient errors."""
    req = Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/json")

    attempt = 0
    while True:
        try:
            with urlopen(req) as resp:
                body = resp.read().decode("utf-8")
                data = json.loads(body) if body else None
                return data, resp.headers
        except HTTPError as err:
            err_body = err.read().decode("utf-8", "ignore")
            if attempt < retries and (err.code >= 500 or err.code == 429):
                attempt += 1
                time.sleep(RETRY_DELAY_SECONDS)
                continue
            raise RuntimeError(
                f"HTTP {err.code} for {url}: {err_body or 'request failed'}"
            ) from err
        except URLError as err:
            if attempt < retries:
                attempt += 1
                time.sleep(RETRY_DELAY_SECONDS)
                continue
            raise RuntimeError(f"Network error for {url}: {err.reason}") from err


def build_url(base_url: str, path: str, params: dict | None = None) -> str:
    """Construct full API URL with optional query parameters."""
    base = base_url.rstrip("/")
    url = f"{base}{path}"
    if params:
        url = f"{url}?{urlencode(params, doseq=True)}"
    return url


def paged_get(base_url: str, path: str, params: dict, token: str, limit: int) -> list:
    """Fetch paginated results up to the specified limit."""
    results: list = []
    cursor = None
    while len(results) < limit:
        page_params = dict(params)
        page_params["per_page"] = min(MAX_LIMIT, limit - len(results))
        if cursor:
            page_params["cursor"] = cursor
        url = build_url(base_url, path, page_params)
        data, headers = request_json(url, token)
        if not data:
            break
        results.extend(data)
        cursor = parse_next_cursor(headers.get("Link"))
        if not cursor:
            break
    return results[:limit]


def require_org_project(org: str, project: str) -> None:
    """Validate that real org and project slugs were provided."""
    if org == DEFAULT_ORG or project == DEFAULT_PROJECT:
        raise RuntimeError(
            "Missing org/project. "
            "Set SENTRY_ORG and SENTRY_PROJECT env vars or pass --org/--project."
        )


def handle_list_issues(args: argparse.Namespace, token: str, base_url: str) -> object:
    """List issues for a project filtered by environment and time range."""
    require_org_project(args.org, args.project)
    limit = min(args.limit, MAX_LIMIT)
    params: dict[str, str] = {
        "statsPeriod": args.time_range,
        "environment": args.environment,
    }
    if args.query:
        params["query"] = args.query
    path = f"/api/0/projects/{args.org}/{args.project}/issues/"
    return paged_get(base_url, path, params, token, limit)


def handle_issue_detail(args: argparse.Namespace, token: str, base_url: str) -> object:
    """Retrieve detailed information for a single issue by ID."""
    path = f"/api/0/issues/{args.issue_id}/"
    url = build_url(base_url, path)
    data, _ = request_json(url, token)
    return data


def handle_issue_events(args: argparse.Namespace, token: str, base_url: str) -> object:
    """List events for a specific issue."""
    limit = min(args.limit, MAX_LIMIT)
    path = f"/api/0/issues/{args.issue_id}/events/"
    return paged_get(base_url, path, {}, token, limit)


def handle_event_detail(args: argparse.Namespace, token: str, base_url: str) -> object:
    """Retrieve detailed information for a single event."""
    require_org_project(args.org, args.project)
    path = f"/api/0/projects/{args.org}/{args.project}/events/{args.event_id}/"
    url = build_url(base_url, path)
    data, _ = request_json(url, token)
    if data and not args.include_entries:
        data = dict(data)
        data.pop("entries", None)
    return data


def build_parser() -> argparse.ArgumentParser:
    """Build CLI argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        description="Read-only Sentry API helper for issues and events"
    )
    parser.add_argument(
        "--base-url",
        default=os.environ.get("SENTRY_BASE_URL", DEFAULT_BASE_URL),
        help="Sentry base URL (default: https://sentry.io)",
    )
    parser.add_argument(
        "--org",
        default=os.environ.get("SENTRY_ORG", DEFAULT_ORG),
        help="Sentry org slug",
    )
    parser.add_argument(
        "--project",
        default=os.environ.get("SENTRY_PROJECT", DEFAULT_PROJECT),
        help="Sentry project slug",
    )
    parser.add_argument(
        "--no-redact",
        action="store_true",
        help="Disable automatic PII redaction in output",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    list_issues = subparsers.add_parser("list-issues", help="List project issues")
    list_issues.add_argument(
        "--time-range", default="24h", help="Stats period (e.g., 1h, 24h, 7d, 30d)"
    )
    list_issues.add_argument("--environment", default="prod", help="Target environment")
    list_issues.add_argument("--query", default="", help="Sentry search query")
    list_issues.add_argument("--limit", type=int, default=20, help="Max results (capped at 50)")

    issue_detail = subparsers.add_parser("issue-detail", help="Get issue details")
    issue_detail.add_argument("issue_id", help="Numeric issue ID")

    issue_events = subparsers.add_parser("issue-events", help="List issue events")
    issue_events.add_argument("issue_id", help="Numeric issue ID")
    issue_events.add_argument("--limit", type=int, default=20, help="Max results (capped at 50)")

    event_detail = subparsers.add_parser("event-detail", help="Get event details")
    event_detail.add_argument("event_id", help="Event ID string")
    event_detail.add_argument(
        "--include-entries",
        action="store_true",
        help="Include event entries (may contain stack traces)",
    )

    return parser


COMMAND_HANDLERS = {
    "list-issues": handle_list_issues,
    "issue-detail": handle_issue_detail,
    "issue-events": handle_issue_events,
    "event-detail": handle_event_detail,
}


def main() -> None:
    """Entry point: parse args, authenticate, dispatch command, print JSON."""
    parser = build_parser()
    args = parser.parse_args()

    token = os.environ.get("SENTRY_AUTH_TOKEN")
    if not token:
        raise RuntimeError(
            "Missing SENTRY_AUTH_TOKEN env var. "
            "Create one at https://sentry.io/settings/account/api/auth-tokens/ "
            "with scopes: project:read, event:read, org:read"
        )

    handler = COMMAND_HANDLERS.get(args.command)
    if not handler:
        raise RuntimeError(f"Unknown command: {args.command}")

    data = handler(args, token, args.base_url)

    if not args.no_redact:
        data = redact_data(data)

    print(json.dumps(data, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
