---
date: 2026-11-26
type: config
scope: ci
files: [.gitea/workflows/ci.yml, docs/README.md, docs/changes/2026-11-26-standard-image-build-and-tags.md, docs/development.md]
breaking: true
---
# Standard image build job and tag policy

## Context

- The image build jobs differed per repository (three generations of the
  same job). Most pushed a branch tag (`main`) and moved `latest` with every
  push to the default branch, so `latest` could point at an unreleased commit.
- Gitea does not expand the `vars` context in a workflow-level `env` block.
  Jobs that read `vars.REGISTRY_GITEA` there got an empty value.
- Required policy: `latest` and the version only from a release; every other
  build only as the git commit.

## Change

- `.gitea/workflows/ci.yml`: the image job is replaced by the standard
  job (same job id, `needs`, triggers, platforms, context and OCI labels).
  Steps: checkout, wait for dind, QEMU `qemu-v9.2.2`, Buildx, resolve image
  reference, registry login, metadata, build and push, build summary.
- Workflow-level `REGISTRY`, `IMAGE_NAME` or `RAW_REGISTRY` removed where only
  the image job used them.
- Docs describing image tags and the registry variable updated (see `files`).

Tag policy (`docker/metadata-action`, `flavor: latest=false`):

| Event | Image tags |
| --- | --- |
| Push to a branch (e.g. `main`), manual run | `sha-<short>` only |
| Release tag `v1.2.3` | `1.2.3`, `latest`, `sha-<short>` |
| Prerelease tag `v1.2.3-rc1` | `1.2.3-rc1`, `sha-<short>` |
| Pull request | built, not pushed |

## Decisions

- No branch tags and no floating `X` / `X.Y` tags: every tag except `latest`
  names exactly one build.
- Registry host read inside the step (`vars.REGISTRY_GITEA`, default
  `gitea.groot.rocks`); push only when `PACKAGES_TOKEN` is set.
- Rejected: keeping the `main` tag as a "latest unreleased" pointer; the
  commit tag `sha-<short>` covers that without a moving tag.

## Usage / Verification

- Push to `main`: the build summary lists only `sha-<short>`.
- Push tag `vX.Y.Z`: the summary lists `X.Y.Z`, `latest`, `sha-<short>`.

## Follow-ups

- Deployments that pull `:main` or rely on `latest` moving with every push
  must switch to a release tag, `latest` (releases only) or `sha-<short>`.
