# AGENTS.md

Instructions for AI coding agents working in this repository. Tool-agnostic;
`CLAUDE.md` imports this file.

## Project

pfSense backup, Python port of a .NET tool: logs in to the pfSense web UI
(`diag_backup.php`, pfSense 2.3.3 and higher) and saves the configuration XML
under `backups/`. Single script `pfsense_backup.py`, Python 3.12 (Docker base
image), dependency `requests`. Runs directly or as a Docker container.

## Read first

1. `docs/README.md` (index).
2. The topic doc for the area you touch:

| Area | Doc |
| --- | --- |
| Script structure, login and download flow, invariants | `docs/architecture.md` |
| Lint, Docker image, CI workflows, image tags | `docs/development.md` |
| Gitea runner DNS problems in CI (German) | `docs/gitea-runner-dns.md` |

## Commands

```bash
pip install -r requirements.txt
python pfsense_backup.py <url> <username> <password>   # writes backups/*.xml
ruff check . --select E,F,W,S,B                       # lint, same as CI
python -m compileall pfsense_backup.py                # compile check, same as CI
docker build -t pfsense-backup-py .
```

There is no test suite.

## Definition of done

- `ruff check . --select E,F,W,S,B` and `python -m compileall pfsense_backup.py`
  pass.
- Affected topic doc in `docs/` updated.
- New file `docs/changes/YYYY-MM-DD-<slug>.md` (template in
  `.claude/skills/document-change/SKILL.md`), listed in `docs/README.md`.
- CLI or Docker usage changed: `README.md` updated.

## Hard rules

- `ruff` is the only linter. CI selects `E,F,W,S,B` (includes Bandit security
  rules `S`).
- Never commit files from `backups/`: they contain the full pfSense
  configuration including credentials and keys. `backups/` is in `.gitignore`.
- Never commit real pfSense URLs, usernames or passwords; use placeholders.
- Do not log or print the password.
- TLS verification is intentionally off (`self.session.verify = False`)
  because pfSense uses self-signed certificates by default. Do not change it
  without the user's request.
- The three positional arguments `<url> <username> <password>` and the output
  directory `backups/` (`/app/backups` in the container) are the public
  interface; README and cron examples depend on them.
- Do not push tags or images unless the user asks.
- No emojis in code, logs or docs.

## Language

| Artifact | Language |
| --- | --- |
| Code, comments, docstrings, log output | English |
| `README.md`, `docs/gitea-runner-dns.md`, CI comments | German (existing) |
| New `docs/` files, commit messages | English |

Commits: Conventional Commits, imperative, no tool attribution trailers.

## Project skills

Located in `.claude/skills/<name>/SKILL.md`.

| Skill | Use for |
| --- | --- |
| `document-change` | Writing the `docs/changes/` record |
| `release-image` | Tagging `vX.Y.Z` to publish a versioned image (user-invoked only) |
