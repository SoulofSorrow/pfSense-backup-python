---
date: 2026-11-26
type: fix
scope: ci
files: [.gitea/workflows/ci.yml, docs/development.md, docs/changes/2026-11-26-registry-login-packages-token.md, docs/README.md]
breaking: false
---
# Log in to the container registry with PACKAGES_TOKEN

## Context

- The registry login in `.gitea/workflows/ci.yml` used `secrets.REGISTRY_PASSWORD`, falling
  back to `secrets.GITHUB_TOKEN`. `REGISTRY_PASSWORD` is not defined, and the
  automatic job token is rejected by the Gitea registry.
- Result on `main`: `Error response from daemon: Get "https://gitea.groot.rocks/v2/": unauthorized`
  in the step "Log in to Gitea Container Registry".
- The registry token is stored once as the user-level Actions secret
  `PACKAGES_TOKEN`, which the other Docker workflows of this account already
  use.

## Change

- `.gitea/workflows/ci.yml`, `docker/login-action` step:
  - `username`: `secrets.GITEA_USERNAME || github.actor`
  - `password`: `secrets.PACKAGES_TOKEN`

## Decisions

- Use the shared `PACKAGES_TOKEN` instead of a per-repository secret: one place
  to rotate the token.
- Rejected: keeping `secrets.GITHUB_TOKEN` as fallback; Gitea rejects it for
  the registry login, so the fallback only hides a missing secret.

## Usage / Verification

- Push to `main`; the build job must pass "Log in to Gitea Container Registry".
- Pull requests still skip the login (`if: github.event_name != 'pull_request'`).

## Follow-ups

- The copy under `.github/workflows/` still uses the GitHub secrets; it is not
  run by Gitea.
