#!/usr/bin/env python3
"""Refresh dynamic sections in the GitHub profile README.

No third-party dependencies are required. The script uses GitHub's REST API
and the repository-provided GITHUB_TOKEN when executed from GitHub Actions.
"""

from __future__ import annotations

import json
import os
import pathlib
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime

ROOT = pathlib.Path(__file__).resolve().parent
README = ROOT / "README.md"
CONFIG = ROOT / "profile_config.json"
API = "https://api.github.com"
TOKEN = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN") or ""


def api_get(path: str):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "changluya-profile-readme",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    request = urllib.request.Request(f"{API}{path}", headers=headers)
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def replace_chunk(content: str, marker: str, chunk: str) -> str:
    pattern = re.compile(
        rf"<!-- {re.escape(marker)} starts -->.*?<!-- {re.escape(marker)} ends -->",
        re.DOTALL,
    )
    replacement = f"<!-- {marker} starts -->\n{chunk.rstrip()}\n<!-- {marker} ends -->"
    if not pattern.search(content):
        raise RuntimeError(f"README marker not found: {marker}")
    return pattern.sub(replacement, content)


def load_config():
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def fetch_owned_repositories(username: str):
    repos = []
    page = 1
    while True:
        batch = api_get(
            f"/users/{username}/repos?type=owner&sort=updated&per_page=100&page={page}"
        )
        if not batch:
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return repos


def render_stats(user: dict, repositories: list[dict]) -> str:
    original = [repo for repo in repositories if not repo.get("fork")]
    stars = sum(repo.get("stargazers_count", 0) for repo in original)
    forks = sum(repo.get("forks_count", 0) for repo in original)
    followers = user.get("followers", 0)
    return f"{followers:,} followers · {stars:,} stars · {forks:,} forks across public projects"


def repo_index(repositories: list[dict]) -> dict[str, dict]:
    return {repo["name"].lower(): repo for repo in repositories}


def escape_html(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def render_project(project: dict, repo: dict | None, username: str) -> str:
    name = project["name"]
    url = (repo or {}).get("html_url") or f"https://github.com/{username}/{name}"
    summary = project.get("summary") or (repo or {}).get("description") or "Open-source project."
    tags = " · ".join(f"<code>{escape_html(tag)}</code>" for tag in project.get("tags", []))

    metrics = []
    if repo:
        metrics.append(f"⭐ {repo.get('stargazers_count', 0)}")
        if repo.get("forks_count", 0):
            metrics.append(f"Forks {repo['forks_count']}")
    metric_text = " · ".join(metrics)
    details = " · ".join(part for part in [tags, metric_text] if part)

    return (
        f'<td width="50%" valign="top">\n'
        f'<h3><a href="{escape_html(url)}">{escape_html(name)}</a></h3>\n'
        f'<p>{escape_html(summary)}</p>\n'
        f'<p>{details}</p>\n'
        f'</td>'
    )


def render_featured_projects(config: dict, repositories: list[dict]) -> str:
    index = repo_index(repositories)
    cards = [
        render_project(project, index.get(project["name"].lower()), config["github_username"])
        for project in config["featured_repositories"]
    ]
    rows = []
    for i in range(0, len(cards), 2):
        pair = cards[i : i + 2]
        if len(pair) == 1:
            pair.append('<td width="50%"></td>')
        rows.append("<tr>\n" + "\n".join(pair) + "\n</tr>")
    return "<table>\n" + "\n".join(rows) + "\n</table>"


def fetch_latest_release(username: str, repo_name: str):
    try:
        return api_get(f"/repos/{username}/{repo_name}/releases/latest")
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise


def render_releases(config: dict) -> str:
    username = config["github_username"]
    releases = []
    for project in config["featured_repositories"]:
        release = fetch_latest_release(username, project["name"])
        if not release or release.get("prerelease") or release.get("draft"):
            continue
        published = release.get("published_at") or release.get("created_at") or ""
        releases.append(
            {
                "repo": project["name"],
                "title": release.get("name") or release.get("tag_name") or "Release",
                "tag": release.get("tag_name") or "",
                "url": release.get("html_url") or f"https://github.com/{username}/{project['name']}/releases",
                "published": published,
            }
        )

    releases.sort(key=lambda item: item["published"], reverse=True)
    releases = releases[: int(config.get("release_limit", 6))]
    if not releases:
        return "No public releases found yet. Once a featured repository publishes a GitHub Release, this section will update automatically."

    lines = []
    for item in releases:
        date = item["published"][:10] if item["published"] else ""
        label = item["title"]
        if item["tag"] and item["tag"].lower() not in label.lower():
            label = f"{item['tag']} — {label}"
        suffix = f" — {date}" if date else ""
        lines.append(f"- **{item['repo']}** · [{label}]({item['url']}){suffix}")
    return "\n".join(lines)


def main() -> int:
    config = load_config()
    username = config["github_username"]
    content = README.read_text(encoding="utf-8")

    try:
        user = api_get(f"/users/{username}")
        repositories = fetch_owned_repositories(username)
        content = replace_chunk(content, "profile_stats", render_stats(user, repositories))
        content = replace_chunk(content, "featured_projects", render_featured_projects(config, repositories))
        content = replace_chunk(content, "latest_releases", render_releases(config))
    except Exception as exc:
        print(f"Profile refresh failed: {exc}", file=sys.stderr)
        return 1

    README.write_text(content, encoding="utf-8")
    print(f"README refreshed at {datetime.now().isoformat(timespec='seconds')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
