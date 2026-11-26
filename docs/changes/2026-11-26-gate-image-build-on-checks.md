---
date: 2026-11-26
type: config
scope: ci
files: [.gitea/workflows/ci.yml, docs/README.md, docs/changes/2026-11-26-gate-image-build-on-checks.md]
breaking: false
---
# Build the image only after the checks pass

## Context

- Job `build-and-push` in `.gitea/workflows/ci.yml` had no `needs`, so it ran in parallel with the check jobs and could push an image although they failed.
- Target layout, as in `discord-music-bot`: checks first, image build only
  when every check job passed.

## Change

- `.gitea/workflows/ci.yml`: job `build-and-push` got `needs: [lint]`.
- `docs/development.md`: job order note; references to `docker.yml` updated in the docs listed under `files`.

## Decisions

- One workflow with `needs:` instead of two workflows: Gitea Actions has no
  reliable cross-workflow dependency, `needs:` works inside one workflow.
- The check jobs now also run for tag pushes, so a release image is only
  built from a commit that passes lint and tests.
- Pull requests still build the image (validation) but never push.

## Usage / Verification

- Open a pull request: the run shows the check jobs, then `build-and-push`.
- Break a check on purpose: `build-and-push` is skipped.

## Follow-ups

none
