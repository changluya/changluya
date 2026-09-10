# changluya GitHub Profile README - Setup

This repository is intended to be your GitHub profile repository.

## 1. Create the profile repository

Create a **public** GitHub repository named exactly:

```text
changluya
```

GitHub will automatically render its root `README.md` on your profile page.

## 2. Push these files

```bash
git init
git add .
git commit -m "feat: initialize GitHub profile"
git branch -M main
git remote add origin git@github.com:changluya/changluya.git
git push -u origin main
```

## 3. Enable GitHub Actions write access

The workflow uses `GITHUB_TOKEN` and `permissions: contents: write` to refresh the README automatically.

If your account/repository policy blocks workflow writes, open:

```text
Repository Settings -> Actions -> General -> Workflow permissions
```

and allow **Read and write permissions**.

## 4. What updates automatically

Every 6 hours the workflow refreshes:

- GitHub followers
- Total stars received by your non-fork public repositories
- Total forks of your non-fork public repositories
- Featured-project star/fork numbers
- Latest GitHub Release for each featured repository

No personal access token is required for normal use.

## 5. Customize featured projects

Edit `profile_config.json`.

The initial featured projects are:

- OpenReach
- open-office-skill
- Studio-Vue
- Java-Demos

The forked `druid` repository is intentionally not highlighted because the profile is designed to emphasize your own engineering work.

## 6. Local test

```bash
python3 build_readme.py
```

Unauthenticated GitHub API requests are rate-limited, so GitHub Actions is the recommended execution environment.

## Design idea

The structure borrows the useful parts of Tw93's profile approach — concise identity, project proof, stats and automatic updates — but is intentionally rewritten around your goal: **show technical capability first, projects second**.
