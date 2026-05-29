# Gitea Runner: DNS im Job-Container reparieren

## Symptom

Im CI-Job (z. B. `pip install`) schlägt der Netzwerkzugriff fehl — je nach
Konfiguration mit einer von zwei Meldungen:

```
[Errno -3] Temporary failure in name resolution      # kein/falscher Nameserver
;; connection timed out; no servers could be reached  # Nameserver gesetzt, aber nicht erreichbar
```

Der **Repo-Checkout funktioniert** (geht gegen das interne `gitea.groot.rocks`),
nur die **externe Auflösung** (pypi.org o. ä.) scheitert.

## Setup-Kontext

Dieser Runner (`~/docker/gitea-runner` auf `jupiter`) ist DinD-basiert:

- Der Runner startet Job-Container über den **DinD-Daemon** (`docker_host: tcp://dind:2376`),
  nicht über den Host-Docker.
- Job-Container hängen am Default-Bridge des DinD-Daemons und erben dessen
  `resolv.conf` → `nameserver 127.0.0.11` (Dockers eingebettetes DNS). Diese
  Adresse existiert **nur in der Namespace des dind-Containers**, im Job-Container
  läuft jede Query ins Leere → "no servers could be reached".

## Diagnose (Reihenfolge)

```bash
# 1. Kann der Job-Container überhaupt ins Internet (IP-Ebene)?
docker compose exec dind docker run --rm alpine ping -c2 1.1.1.1

# 2. Funktioniert DNS gegen einen externen Resolver?
docker compose exec dind docker run --rm alpine nslookup pypi.org 1.1.1.1

# 3. Welche Resolver nutzt der Host wirklich?
cat /etc/resolv.conf
```

**Wichtiger Befund in diesem Netz:** `ping 1.1.1.1` klappt (ICMP/TCP frei), aber
DNS gegen `1.1.1.1` (UDP 53) läuft in den Timeout. Die vorgelagerte Firewall
(pfSense) **blockt ausgehendes DNS zu externen Resolvern** und erlaubt nur die
DNS-Server des Hosters. `1.1.1.1`/`9.9.9.9` sind hier also die *falsche* Wahl.

## Lösung: user-defined network + eingebettetes DNS

Job-Container an ein **user-defined network** hängen, damit Dockers eingebettetes
DNS (`127.0.0.11`) aktiv ist. Das löst Service-Namen (z. B. den `dind`-Service)
lokal auf **und** leitet externe Anfragen an die Resolver weiter, die der
dind-/Host-Resolver kennt (die erlaubten Hoster-DNS `46.38.225.230` /
`46.38.252.230`).

In `docker-compose.yml` im `runner-configurator`-Heredoc:

```yaml
        container:
          network: ""        # statt: bridge
```

`""` lässt den `act_runner` pro Job ein Netzwerk anlegen (user-defined → embedded
DNS). `Dockerfile.dind` bleibt im Original **ohne** `--dns`.

Anwenden:

```bash
cd ~/docker/gitea-runner
docker compose build dind
docker compose up -d --build --force-recreate
```

> `gitea.groot.rocks` (intern) bleibt über `--add-host=gitea.groot.rocks:$$GITEA_IP`
> in `options` aufgelöst. IPv6-Resolver entfallen wegen `enable_ipv6: false`.

## Gegenprobe

```bash
# user-defined Netz nachstellen — muss eine IP liefern:
docker compose exec dind sh -c \
  'docker network create t >/dev/null 2>&1; \
   docker run --rm --network t alpine nslookup pypi.org; \
   docker network rm t >/dev/null 2>&1'
```

Danach CI neu auslösen — `lint` (PyPI) und `docker` (Service `dind`) werden grün.

## Sonderfall: Docker-Build im Workflow (dind-Service)

Der `docker`-Job nutzt einen `docker:dind`-Service und baut darin das Image. Zwei
zusätzliche Stolpersteine:

1. **Race:** Gitea wartet nicht zuverlässig auf den Service-Healthcheck. Vor dem
   Build aktiv pollen:
   ```yaml
   - name: Wait for Docker daemon
     run: |
       for i in $(seq 1 30); do docker info >/dev/null 2>&1 && break; sleep 2; done
       docker info
   ```
2. **DNS in den `RUN`-Steps:** Der dind-Daemon kann Base-Images ziehen (eigene
   Netns), aber die buildkit-`RUN`-Sandbox erreicht weder `127.0.0.11` noch
   (über die zusätzliche NAT-Schicht) `46.38.x`. Lösung: mit der Netns des
   dind-Containers bauen, dort funktioniert das embedded DNS:
   ```yaml
   - run: docker build --network=host -t pfsense-backup:ci .
   ```
   (`--dns` am Service-Container half hier NICHT — `options` wird an
   Service-Container nicht zuverlässig durchgereicht.)

## Was NICHT hilft

- `--dns 1.1.1.1` / `9.9.9.9`: extern blockt die Firewall UDP 53.
- `dockerd --dns <hoster>` oder `--dns` in `options`: umgeht das eingebettete DNS
  und zerschießt die Service-Namensauflösung →
  `lookup dind ... no such host` im docker-Job.
- `network: bridge` (Default-Bridge): kein eingebettetes DNS → genau dieses Problem.
- Image-Wechsel: behebt nur fehlende Tools (`node`/`python`), nicht DNS.
