#!/usr/bin/env python3
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
CONFIG = ROOT / "profile_config.json"

cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
groups = cfg["featured_repository_groups"]

categories = [group["title"] for group in groups]
category_text = ", ".join(categories[:-1]) + f", and {categories[-1]}"
summary = (
    "I founded the [AgentForge organization](https://github.com/agentforge-tech); "
    f"my open-source work spans {category_text}. "
    "Under AgentForge I maintain "
    "[**AgentForge**](https://github.com/agentforge-tech/AgentForge), "
    "a Java-first AI Agent framework, together with two open-sourced Skills, "
    "[**OpenReach**](https://github.com/agentforge-tech/OpenReach) and "
    "[**open-office-skill**](https://github.com/agentforge-tech/open-office-skill). "
    "I also build [**BlogLoom**](https://github.com/changluya/BlogLoom), "
    "my own blog content management and publishing system.\n\n"
    "I also contribute to [DTStack/SqlParserX](https://github.com/DTStack/SqlParserX), "
    "a Java SQL parser built on Druid, working on multi-dialect parsing, "
    "table and column lineage, and SQL rewriting."
)
block = "<!-- PROJECTS_START -->\n" + summary + "\n<!-- PROJECTS_END -->"

text = README.read_text(encoding="utf-8")
text = re.sub(
    r"<!-- PROJECTS_START -->.*?<!-- PROJECTS_END -->",
    block,
    text,
    flags=re.S,
)
README.write_text(text, encoding="utf-8")
print("README updated.")
