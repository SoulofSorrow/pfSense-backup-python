---
date: 2026-11-25
type: docs
scope: docs, agent tooling
files: [AGENTS.md, CLAUDE.md, .claude/settings.json, .claude/skills/document-change/SKILL.md, .claude/skills/release-image/SKILL.md, docs/README.md, docs/architecture.md, docs/development.md, docs/changes/2026-11-25-ai-ready-docs.md, README.md]
breaking: false
---
# Agent-ready documentation and project skills

## Context

- The repository had one German runbook (`docs/gitea-runner-dns.md`) but no
  docs index and no instructions for AI coding agents.
- Goal: an agent can find the flow, rules and checks without reading the
  whole repository.

## Change

- `docs/README.md`: index of docs (including the existing
  `docs/gitea-runner-dns.md`) and change records, maintenance rules.
- `docs/architecture.md`: code map of `pfsense_backup.py`, three-stage flow,
  output file, exit codes, invariants, known limitations.
- `docs/development.md`: setup, ruff, Docker image, both CI workflows, image
  tags, versioning.
- `AGENTS.md`: tool-agnostic agent instructions (commands, definition of done,
  hard rules, language table, skill list).
- `CLAUDE.md`: imports `AGENTS.md` via `@AGENTS.md`, Claude Code notes.
- `.claude/settings.json`: allows `ruff check`, `ruff format --check`,
  `python -m compileall pfsense_backup.py`, `docker build`; asks before
  `git push`, `git tag`, `docker push`; denies reading `.env` and
  `backups/**`.
- `.claude/skills/`:
  - `document-change`: change record template.
  - `release-image`: tag `vX.Y.Z` to publish images,
    `disable-model-invocation: true`.
- `README.md`: German section "Dokumentation" pointing to `docs/` and
  `AGENTS.md` (the README is written in German).
- `docs/gitea-runner-dns.md`: unchanged.

## Decisions

- `AGENTS.md` as the canonical file, `CLAUDE.md` only imports it.
- `backups/**` denied for reading: backup XML contains the full firewall
  configuration with credentials.
- README section in German to match the existing file language.
- No `.dockerignore` change: the file does not exist and the `Dockerfile`
  copies files explicitly.

## Usage / Verification

```bash
python3 -m json.tool .claude/settings.json
ruff check . --select E,F,W,S,B
ls docs docs/changes .claude/skills
```

## Follow-ups

- Missing standard files: `.editorconfig`, `Makefile` (build/test/tag
  targets), `CHANGELOG.md`, `CONTRIBUTING.md`, `.pre-commit-config.yaml`,
  `README.de.md`, `LICENSE`, `.dockerignore`.
- `README.md` is in German; an English `README.md` plus `README.de.md` is
  expected by the documentation rules.
- No tests and no `pyproject.toml` / ruff configuration.
- Password is passed as a command-line argument (visible in process list and
  shell history); no request timeouts.
