---
date: 2026-11-26
type: fix
scope: ci
files: [.gitea/workflows/ci.yml, docs/README.md, docs/changes/2026-11-26-pin-qemu-and-build-timeout.md, docs/development.md]
breaking: false
---
# Pin the QEMU emulator and bound the image build time

## Context

- `docker/setup-qemu-action@v3` installs `tonistiigi/binfmt:latest`, which
  ships QEMU 10 (`qemu/v10.2.3` in the job log).
- In `discord-music-bot` run 633 the arm64 stage crashed under emulation:
  `RUN npm ci --omit=dev` -> `qemu: uncaught target signal 4 (Illegal instruction) - core dumped`.
  The step did not fail; the job hung and blocked the runner, so other runs
  stayed queued.

## Change

- `.gitea/workflows/ci.yml`, step `docker/setup-qemu-action@v3`:
  `with.image: tonistiigi/binfmt:qemu-v9.2.2`.
- Job `build-and-push`: `timeout-minutes: 45` added.
- `docs/development.md`: note on emulation and timeout.

## Decisions

- Pin QEMU 9.2.2 instead of dropping arm64: keeps multi-arch images.
- Timeout as a safety net: a hanging emulated build fails after the limit
  instead of holding the runner.
- Rejected: native arm64 runner; not available.

## Usage / Verification

- Next run of job `build-and-push`: the "Set up QEMU" log shows `qemu/v9.2.2`, the
  arm64 stage finishes.

## Follow-ups

- Check whether a later `tonistiigi/binfmt` release fixes the crash, then
  drop the pin.
