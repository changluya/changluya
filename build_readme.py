#!/usr/bin/env python3
"""Refresh the compact dynamic sections of changluya's GitHub profile README."""

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


def load_config() -> dict:
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def fetch_owned_repositories(username: str) -> list[dict]:
    repos: list[dict] = []
    page = 1
    while True:
        batch = api_get(f"/users/{username}/repos?type=owner&sort=updated&per_page=100&page={page}")
        if not batch:
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return repos


def repo_index(repositories: list[dict]) -> dict[str, dict]:
    return {repo["name"].lower(): repo for repo in repositories}


def render_stats(user: dict, repositories: list[dict]) -> str:
    original = [repo for repo in repositories if not repo.get("fork")]
    stars = sum(repo.get("stargazers_count", 0) for repo in original)
    forks = sum(repo.get("forks_count", 0) for repo in original)
    followers = user.get("followers", 0)
    return f"**{followers:,} followers** · **{stars:,} stars** · **{forks:,} forks** across public projects"


def render_featured_projects(config: dict, repositories: list[dict]) -> str:
    username = config["github_username"]
    index = repo_index(repositories)
    lines: list[str] = []
    for project in config["featured_repositories"]:
        name = project["name"]
        repo = index.get(name.lower())
        url = (repo or {}).get("html_url") or f"https://github.com/{username}/{name}"
        summary = project.get("summary") or (repo or {}).get("description") or "Open-source project"
        tags = " ".join(f"`{tag}`" for tag in project.get("tags", []))
        stars = (repo or {}).get("stargazers_count", 0)
        lines.append(f"- **[{name}]({url})** — {summary} · {tags} · ⭐ {stars:,}")
    return "\n".join(lines)


def fetch_latest_release(username: str, repo_name: str):
    try:
        return api_get(f"/repos/{username}/{repo_name}/releases/latest")
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise


def render_releases(config: dict) -> str:
    username = config["github_username"]
    releases: list[dict] = []
    for project in config["featured_repositories"]:
        release = fetch_latest_release(username, project["name"])
        if not release or release.get("draft") or release.get("prerelease"):
            continue
        published = release.get("published_at") or release.get("created_at") or ""
        releases.append(
            {
                "repo": project["name"],
                "label": release.get("name") or release.get("tag_name") or "Release",
                "url": release.get("html_url") or f"https://github.com/{username}/{project['name']}/releases",
                "published": published,
            }
        )

    releases.sort(key=lambda item: item["published"], reverse=True)
    releases = releases[: int(config.get("release_limit", 4))]
    if not releases:
        return "No public releases yet."

    return "\n".join(
        f"- [{item['repo']} · {item['label']}]({item['url']}) · {item['published'][:10]}"
        for item in releases
    )


def event_description(event: dict, username: str) -> str | None:
    event_type = event.get("type", "")
    repo_name = (event.get("repo") or {}).get("name", "")
    if not repo_name:
        return None
    short_repo = repo_name.split("/", 1)[-1]
    repo_url = f"https://github.com/{repo_name}"
    payload = event.get("payload") or {}

    if event_type == "PushEvent":
        commits = payload.get("commits") or []
        if commits:
            message = (commits[-1].get("message") or "").splitlines()[0].strip()
            if len(message) > 42:
                message = message[:39].rstrip() + "..."
            if message:
                return f"Pushed **{message}** to [{short_repo}]({repo_url})"
        return f"Pushed code to [{short_repo}]({repo_url})"

    if event_type == "ReleaseEvent":
        release = payload.get("release") or {}
        label = release.get("name") or release.get("tag_name") or "a release"
        url = release.get("html_url") or repo_url
        return f"Released [{label}]({url}) in **{short_repo}**"

    if event_type == "PullRequestEvent":
        action = payload.get("action", "updated")
        pr = payload.get("pull_request") or {}
        title = pr.get("title") or "pull request"
        url = pr.get("html_url") or repo_url
        return f"{action.capitalize()} PR [{title}]({url}) in **{short_repo}**"

    if event_type == "CreateEvent":
        ref_type = payload.get("ref_type", "item")
        ref = payload.get("ref")
        if ref:
            return f"Created {ref_type} **{ref}** in [{short_repo}]({repo_url})"
        if ref_type == "repository":
            return f"Created repository [{short_repo}]({repo_url})"

    if event_type == "IssuesEvent":
        action = payload.get("action", "updated")
        issue = payload.get("issue") or {}
        title = issue.get("title") or "issue"
        url = issue.get("html_url") or repo_url
        return f"{action.capitalize()} issue [{title}]({url}) in **{short_repo}**"

    return None


def render_activity(config: dict) -> str:
    username = config["github_username"]
    events = api_get(f"/users/{username}/events/public?per_page=100")
    limit = int(config.get("activity_limit", 5))
    lines: list[str] = []
    seen: set[str] = set()

    for event in events:
        description = event_description(event, username)
        if not description or description in seen:
            continue
        seen.add(description)
        created = (event.get("created_at") or "")[:10]
        suffix = f" · {created}" if created else ""
        lines.append(f"- {description}{suffix}")
        if len(lines) >= limit:
            break

    return "\n".join(lines) if lines else "No recent public activity."


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
        content = replace_chunk(content, "recent_activity", render_activity(config))
    except Exception as exc:
        print(f"Profile refresh failed: {exc}", file=sys.stderr)
        return 1

    README.write_text(content, encoding="utf-8")
    print(f"README refreshed at {datetime.now().isoformat(timespec='seconds')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
