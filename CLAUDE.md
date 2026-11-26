@AGENTS.md

## Claude Code specifics

- Project skills live in `.claude/skills/`. Invoke the matching skill before
  starting a task it covers.
- `.claude/settings.json` allows lint and compile checks and denies reading
  `.env` and `backups/`.
- Run `ruff check . --select E,F,W,S,B` before reporting a task as done.
