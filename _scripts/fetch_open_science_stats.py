#!/usr/bin/env python3
"""
Fetch open-science stats from GitHub and OSF and write to _data/open_science_stats.yml.
Run before `bundle exec jekyll build`. Set GITHUB_TOKEN env var to raise rate limits.
"""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "..", "_data", "open_science_stats.yml")
GITHUB_USER = "gonzalezgarcia"
OSF_USER = "ufuaa"


def _get(url, headers=None, label=""):
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except Exception as exc:
        print(f"  [warn] {label or url}: {exc}", file=sys.stderr)
        return None


def _paginate(base_url, headers, label=""):
    """Collect all pages from a GitHub list endpoint."""
    results = []
    url = f"{base_url}?per_page=100&page=1"
    page = 1
    while url:
        data = _get(url, headers, label=f"{label} p{page}")
        if not data:
            break
        results.extend(data)
        # Stop if fewer than 100 returned (last page)
        if len(data) < 100:
            break
        page += 1
        url = f"{base_url}?per_page=100&page={page}"
    return results


# ---------------------------------------------------------------------------
# GitHub
# ---------------------------------------------------------------------------

def fetch_github():
    token = os.environ.get("GITHUB_TOKEN", "")
    headers = {"User-Agent": "open-science-stats-fetcher"}
    if token:
        headers["Authorization"] = f"token {token}"

    print("Fetching GitHub user info…")
    user = _get(f"https://api.github.com/users/{GITHUB_USER}", headers, "user")
    if not user:
        return None

    print("Fetching GitHub repos…")
    repos = _paginate(f"https://api.github.com/users/{GITHUB_USER}/repos", headers, "repos")

    # Filter out forks; own_repos drives all stats
    own_repos = [r for r in repos if not r.get("fork", False)]
    total_stars = sum(r.get("stargazers_count", 0) for r in own_repos)
    total_forks_received = sum(r.get("forks_count", 0) for r in own_repos)

    # Top 6 non-fork repos by stars (repos with no description and no stars filtered by the page)
    top_repos = sorted(own_repos, key=lambda r: r.get("stargazers_count", 0), reverse=True)[:6]

    top_repos_data = [
        {
            "name": r["name"],
            "url": r["html_url"],
            "description": (r.get("description") or "").strip(),
            "stars": r.get("stargazers_count", 0),
            "forks": r.get("forks_count", 0),
            "language": r.get("language") or "",
            "updated_at": (r.get("updated_at") or "")[:10],
        }
        for r in top_repos
    ]

    # Top 3 languages by repo count
    lang_counts = {}
    for r in own_repos:
        lang = r.get("language")
        if lang:
            lang_counts[lang] = lang_counts.get(lang, 0) + 1
    top_languages = [
        {"language": lang, "count": count}
        for lang, count in sorted(lang_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    ]

    # Commit count via search API (requires preview header, optional token for higher limits)
    commit_count = None
    if token:
        search_headers = {**headers, "Accept": "application/vnd.github.cloak-preview+json"}
        result = _get(
            f"https://api.github.com/search/commits?q=author:{GITHUB_USER}&per_page=1",
            search_headers,
            "commit search",
        )
        if result and "total_count" in result:
            commit_count = result["total_count"]

    # Pinned repos via GraphQL (requires token; falls back to top_repos on the page)
    pinned_repos_data = []
    if token:
        print("Fetching GitHub pinned repos…")
        gql_query = (
            '{ user(login: "%s") { pinnedItems(first: 6, types: [REPOSITORY]) {'
            ' nodes { ... on Repository { name owner { login } url description'
            ' stargazerCount forkCount primaryLanguage { name } updatedAt } } } } }'
            % GITHUB_USER
        )
        gql_body = json.dumps({"query": gql_query}).encode()
        gql_req = urllib.request.Request(
            "https://api.github.com/graphql",
            data=gql_body,
            headers={**headers, "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(gql_req, timeout=15) as resp:
                gql_result = json.loads(resp.read().decode())
            if gql_result.get("errors"):
                print(f"  [warn] GraphQL errors: {gql_result['errors']}", file=sys.stderr)
            nodes = (
                (gql_result.get("data") or {})
                .get("user", {})
                .get("pinnedItems", {})
                .get("nodes", [])
            ) or []
            pinned_repos_data = [
                {
                    "name": r["name"],
                    "owner": (r.get("owner") or {}).get("login", ""),
                    "url": r["url"],
                    "description": (r.get("description") or "").strip(),
                    "stars": r.get("stargazerCount", 0),
                    "forks": r.get("forkCount", 0),
                    "language": (r.get("primaryLanguage") or {}).get("name") or "",
                    "updated_at": (r.get("updatedAt") or "")[:10],
                }
                for r in nodes
            ]
        except Exception as exc:
            print(f"  [warn] GraphQL pinned repos: {exc}", file=sys.stderr)

    return {
        "repos": user.get("public_repos", len(own_repos)),
        "stars": total_stars,
        "forks_received": total_forks_received,
        "followers": user.get("followers", 0),
        "commit_count": commit_count,
        "profile_url": f"https://github.com/{GITHUB_USER}",
        "pinned_repos": pinned_repos_data,
        "top_repos": top_repos_data,
        "top_languages": top_languages,
    }


# ---------------------------------------------------------------------------
# OSF
# ---------------------------------------------------------------------------

def fetch_osf():
    headers = {"User-Agent": "open-science-stats-fetcher"}

    print("Fetching OSF projects…")
    proj_page = _get(
        f"https://api.osf.io/v2/users/{OSF_USER}/nodes/?page[size]=10",
        headers,
        "osf projects list",
    )
    projects_data = []
    project_count = 0
    if proj_page:
        # meta.total is authoritative; fall back to len(data) if absent/zero
        project_count = (proj_page.get("meta") or {}).get("total", 0)
        for item in (proj_page.get("data") or []):
            attrs = item.get("attributes", {})
            # Skip components (non-root nodes) to surface only top-level projects
            if attrs.get("parent"):
                continue
            projects_data.append(
                {
                    "title": attrs.get("title", ""),
                    "url": f"https://osf.io/{item['id']}/",
                    "doi": (attrs.get("doi") or "").strip(),
                    "description": (attrs.get("description") or "")[:200].strip(),
                    "date_created": (attrs.get("date_created") or "")[:10],
                }
            )
        if project_count == 0 and projects_data:
            project_count = len(projects_data)

    print("Fetching OSF registrations…")
    reg_page = _get(
        f"https://api.osf.io/v2/users/{OSF_USER}/registrations/?page[size]=10",
        headers,
        "osf registrations",
    )
    reg_count = 0
    registrations_data = []
    if reg_page:
        reg_count = (reg_page.get("meta") or {}).get("total", 0)
        for item in (reg_page.get("data") or []):
            attrs = item.get("attributes", {})
            registrations_data.append(
                {
                    "title": attrs.get("title", ""),
                    "url": f"https://osf.io/{item['id']}/",
                    "doi": (attrs.get("doi") or "").strip(),
                    "description": (attrs.get("description") or "")[:200].strip(),
                    "date_created": (attrs.get("date_created") or "")[:10],
                    "category": attrs.get("category", ""),
                }
            )
        if reg_count == 0 and registrations_data:
            reg_count = len(registrations_data)

    return {
        "projects": project_count,
        "preregistrations": reg_count,
        "profile_url": f"https://osf.io/{OSF_USER}/",
        "top_projects": projects_data,
        "registrations": registrations_data,
    }


# ---------------------------------------------------------------------------
# YAML writer (stdlib only – avoids pyyaml dependency)
# ---------------------------------------------------------------------------

def _yaml_str(s):
    s = str(s)
    if any(c in s for c in (':', '#', '{', '}', '[', ']', ',', '&', '*', '?', '|', '-', '<', '>', '=', '!', '%', '@', '`', '"', "'", '\n')):
        escaped = s.replace('"', '\\"')
        return f'"{escaped}"'
    return s or '""'


def _to_yaml(obj, indent=0):
    pad = "  " * indent
    if isinstance(obj, dict):
        lines = []
        for k, v in obj.items():
            if isinstance(v, (dict, list)):
                lines.append(f"{pad}{k}:")
                lines.append(_to_yaml(v, indent + 1))
            elif v is None:
                lines.append(f"{pad}{k}:")
            else:
                lines.append(f"{pad}{k}: {_yaml_str(v)}")
        return "\n".join(lines)
    elif isinstance(obj, list):
        if not obj:
            return f"{pad}[]"
        lines = []
        for item in obj:
            if isinstance(item, dict):
                first = True
                for k, v in item.items():
                    prefix = f"{pad}- " if first else f"{pad}  "
                    first = False
                    if isinstance(v, (dict, list)):
                        lines.append(f"{prefix}{k}:")
                        lines.append(_to_yaml(v, indent + 2))
                    elif v is None:
                        lines.append(f"{prefix}{k}:")
                    else:
                        lines.append(f"{prefix}{k}: {_yaml_str(v)}")
            else:
                lines.append(f"{pad}- {_yaml_str(item)}")
        return "\n".join(lines)
    else:
        return f"{pad}{_yaml_str(obj)}"


def write_yaml(path, data):
    header = "# Auto-generated by _scripts/fetch_open_science_stats.py — do not edit by hand.\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(header)
        f.write(_to_yaml(data))
        f.write("\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=== fetch_open_science_stats.py ===")

    github_data = fetch_github()
    osf_data = fetch_osf()

    if github_data is None:
        print("GitHub fetch failed entirely; keeping existing stats.", file=sys.stderr)
        github_data = {"repos": 0, "stars": 0, "forks_received": 0, "followers": 0,
                       "commit_count": None, "profile_url": f"https://github.com/{GITHUB_USER}",
                       "top_repos": []}

    if osf_data is None:
        osf_data = {"projects": 0, "preregistrations": 0,
                    "profile_url": f"https://osf.io/{OSF_USER}/",
                    "top_projects": [], "registrations": []}

    output = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "github": github_data,
        "osf": osf_data,
    }

    write_yaml(OUTPUT_FILE, output)
    print(f"Written to {OUTPUT_FILE}")
    print(f"  GitHub: {github_data['repos']} repos, {github_data['stars']} stars")
    print(f"  OSF:    {osf_data['projects']} projects, {osf_data['preregistrations']} preregistrations")


if __name__ == "__main__":
    main()
