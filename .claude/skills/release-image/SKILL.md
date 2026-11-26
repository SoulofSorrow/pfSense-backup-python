---
name: release-image
description: Publish a versioned pfSense backup Docker image by pushing a vX.Y.Z git tag, which triggers the CI build-and-push job. Only when the user explicitly asks for a release or a versioned image.
disable-model-invocation: true
---

# Release a versioned image

Background: `docs/development.md`, sections "CI" and "Versioning". Pushing the
tag publishes images to the registry.

## Preconditions

1. On `main`, up to date: `git switch main && git pull --ff-only`.
2. Clean working tree: `git status --short` prints nothing.
3. Checks pass: `ruff check . --select E,F,W,S,B` and
   `python -m compileall pfsense_backup.py`.
4. Existing tags: `git tag --list 'v*' --sort=-v:refname | head`. Confirm the
   new version `vX.Y.Z` with the user; it must not exist yet.

## Run

```bash
git tag -a vX.Y.Z -m "vX.Y.Z"
git push origin vX.Y.Z
```

## After

- CI pushes `<registry>/<owner>/<repo>:X.Y.Z` and `:X.Y`.
- Report the tag and the CI run status. On failure report the failing step.
  Do not delete or move tags without the user's explicit request.
