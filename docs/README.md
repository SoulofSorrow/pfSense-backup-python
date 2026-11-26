# Documentation Index

Primary reader: AI coding agents. Human readers start with `README.md`.

Read this index first, then the topic docs that match the area you change.
Agent rules and workflow live in `AGENTS.md` in the repository root.

## Topic docs (current state)

| File | Purpose |
| --- | --- |
| `docs/architecture.md` | Script structure, three-stage login and download flow, output, invariants |
| `docs/development.md` | Setup, ruff, Docker image, CI workflows, image tags |
| `docs/gitea-runner-dns.md` | German: fixing DNS in Gitea runner job containers (DinD, buildkit `network=host`) |

## Change records

One file per change set in `docs/changes/`, named `YYYY-MM-DD-<short-slug>.md`.
Never rewrite an existing change file; add a new one.

| File | Purpose |
| --- | --- |
| `docs/changes/2026-11-25-ai-ready-docs.md` | Adds `docs/README.md`, topic docs, `AGENTS.md`, `CLAUDE.md` and project skills |
| `docs/changes/2026-11-26-registry-login-packages-token.md` | Registry login uses the shared `PACKAGES_TOKEN` |
| `docs/changes/2026-11-26-gate-image-build-on-checks.md` | Image build runs only after all check jobs pass |
| `docs/changes/2026-11-26-pin-qemu-and-build-timeout.md` | QEMU pinned to 9.2.2, build job timeout |
| `docs/changes/2026-11-26-standard-image-build-and-tags.md` | Standard image build job; `latest` and version only from releases, otherwise `sha-<short>` |

## Maintenance rules

- Add, rename or remove a doc: update this index in the same change.
- Change behaviour: update the affected topic doc in the same change.
- Every change set: add a file in `docs/changes/`.
