# changluya Profile README

This is a compact GitHub profile inspired by Tw93's approach: **short positioning + project proof + automatic updates**, with a small amount of visual styling.

## Structure

- `README.md` — the profile page itself
- `assets/header.svg` — lightweight local header artwork
- `profile_config.json` — featured repository configuration
- `build_readme.py` — updates stats, project stars, releases and recent public activity
- `.github/workflows/update-profile.yml` — runs every 6 hours and on demand

## Push the update

If this repository is already cloned locally, replace the corresponding files and run:

```bash
git add .
git commit -m "refactor: simplify GitHub profile"
git push
```

## GitHub Actions permissions

The workflow needs write permission to update `README.md`:

```text
Repository Settings -> Actions -> General -> Workflow permissions
```

Select **Read and write permissions**.

## Featured projects

The default profile keeps only three projects to reduce noise:

- OpenReach — current AI Agent infrastructure direction
- open-office-skill — Agent Skill / document capability
- Studio-Vue — Java backend / full-stack engineering proof

Edit `profile_config.json` whenever you want to change the featured set.
