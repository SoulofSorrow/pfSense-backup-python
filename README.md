# pfSense backup — Python port

Python-Portierung des .NET-Tools. Lädt eine pfSense-Konfigurationssicherung
herunter (pfSense 2.3.3 und höher) und speichert sie unter `backups/`.

Basiert auf <https://doc.pfsense.org/index.php/Remote_Config_Backup>.

## Direkt mit Python ausführen

```bash
pip install -r requirements.txt
python pfsense_backup.py https://192.168.0.1:8443 admin password
```

Die Sicherung landet im Unterordner `backups/` des aktuellen Verzeichnisses.

## Mit Docker

```bash
docker build -t pfsense-backup-py .
docker run --rm -v /my/backup/folder:/app/backups pfsense-backup-py https://192.168.0.1:8443 admin password
```

Lege den Befehl in einen Cronjob/Task Scheduler, um regelmäßig zu sichern.

## Mehrere pfSense-Maschinen sichern

```bash
#!/bin/bash
BackupTarget() {
    docker run --rm -v "$1":/app/backups pfsense-backup-py "$2" "$3" "$4" >> /opt/pfSense/output.log
}

BackupTarget "/opt/pfSense/backups/pfSense-master"  "https://10.10.10.2:444" "admin" "password"
BackupTarget "/opt/pfSense/backups/pfSense-slave"   "https://10.10.10.3:444" "admin" "password"
BackupTarget "/opt/pfSense/backups/pfSense-another" "https://10.10.10.4:444" "admin" "password"
```

## Hinweis zu TLS

pfSense nutzt standardmäßig selbstsignierte Zertifikate. Die Zertifikatsprüfung
wird daher (wie im Original) deaktiviert.
