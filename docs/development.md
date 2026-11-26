# Development

## Setup

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt     # requests>=2.25
pip install ruff
```

## Checks (same as CI job `lint`)

```bash
ruff check . --select E,F,W,S,B
python -m compileall pfsense_backup.py
```

- No `pyproject.toml` or ruff config file; rules are selected on the command
  line only.
- No test suite exists.

## Docker image

- `Dockerfile`: `python:3.12-slim`, `WORKDIR /app`, installs
  `requirements.txt`, copies only `pfsense_backup.py`,
  `ENTRYPOINT ["python", "pfsense_backup.py"]`.
- Backups are written to `/app/backups`; mount a host folder there:

```bash
docker build -t pfsense-backup-py .
docker run --rm -v /my/backup/folder:/app/backups pfsense-backup-py <url> <username> <password>
```

- No `.dockerignore` exists; the image only copies two files explicitly.
- No compose file exists.

## CI

Job order: the check jobs (`lint`) run first. The image job `build-and-push` has `needs: [lint]` and starts only when all of them pass; on pull requests it builds without pushing.

Two equivalent workflows with jobs `lint` and `build-and-push`:

| File | Registry | Notes |
| --- | --- | --- |
| `.gitea/workflows/ci.yml` | `vars.REGISTRY_GITEA`, default `gitea.groot.rocks` | Runs in `catthehacker/ubuntu:act-latest`; build via `docker:27-dind` service with buildx `network=host` (see `docs/gitea-runner-dns.md`); credentials `secrets.GITEA_USERNAME` (default `github.actor`) / `secrets.PACKAGES_TOKEN` |
| `.github/workflows/ci.yml` | `ghcr.io` | `GITHUB_TOKEN`, GHA build cache |

Triggers: push to `main`, tags `v*.*.*`, pull requests to `main`, manual.
Images are built for `linux/amd64` and `linux/arm64` and pushed except on
pull requests.

Image tags (`docker/metadata-action`): branch name, `pr-<n>`, semver
`<version>` and `<major>.<minor>` on tags, short SHA, `latest` on the default
branch.

## Versioning

No version string in the code. Versions exist only as git tags `vX.Y.Z`,
which produce semver image tags. No `CHANGELOG.md` and no release script.
