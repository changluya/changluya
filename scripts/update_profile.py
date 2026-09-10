#!/usr/bin/env python3
from pathlib import Path
import json
import os
import re
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
CONFIG = ROOT / "profile_config.json"

cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
user = cfg["github_user"]
repos = cfg["featured_repositories"]

token = os.getenv("GITHUB_TOKEN", "")
headers = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "changluya-profile-updater",
}
if token:
    headers["Authorization"] = f"Bearer {token}"

def get_json(url):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))

descriptions = {
    "OpenReach": ("Web access infrastructure for AI Agents", "`Java` `Spring Boot`"),
    "open-office-skill": ("Office document processing Skill for Agents", "`Python` `Agent Skill`"),
    "Studio-Vue": ("Spring Boot + Vue RBAC management system", "`Java` `Vue`"),
}

rows = [
    "| Project | What it does | Stack |",
    "| --- | --- | --- |",
]

for repo_name in repos:
    data = get_json(f"https://api.github.com/repos/{user}/{repo_name}")
    stars = data.get("stargazers_count", 0)
    desc, stack = descriptions[repo_name]
    rows.append(
        f"| [**{repo_name}**](https://github.com/{user}/{repo_name}) ⭐ {stars} | {desc} | {stack} |"
    )

block = "<!-- PROJECTS_START -->\n" + "\n".join(rows) + "\n<!-- PROJECTS_END -->"

text = README.read_text(encoding="utf-8")
text = re.sub(
    r"<!-- PROJECTS_START -->.*?<!-- PROJECTS_END -->",
    block,
    text,
    flags=re.S,
)
README.write_text(text, encoding="utf-8")
print("README updated.")
