#!/usr/bin/env python3
"""Download a pfSense configuration backup (pfSense 2.3.3 and higher).

Port of the original .NET tool. Based on
https://doc.pfsense.org/index.php/Remote_Config_Backup
"""

import os
import re
import sys
import datetime

import requests
import urllib3

# pfSense ships with self-signed certificates by default, so we disable
# verification (matching the original tool's ServerCertificateValidationCallback).
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CSRF_RE = re.compile(
    r"name=['\"]__csrf_magic['\"]\s+value=['\"]([^'\"]+)['\"]", re.IGNORECASE
)

# Characters not allowed in file names on common file systems.
UNSAFE_FILENAME_CHARS = '\\/"*:?<>|'


class UsernamePasswordInvalidError(Exception):
    """Raised when pfSense reports incorrect credentials."""


def to_safe_filename(name):
    return "".join(c for c in name if c not in UNSAFE_FILENAME_CHARS)


def extract_csrf_token(html):
    match = CSRF_RE.search(html)
    if not match:
        raise ValueError("Could not find __csrf_magic token in pfSense response")
    return match.group(1)


class PfSense:
    def __init__(self, url, username, password):
        self.url = url.rstrip("/")
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.verify = False
        self.backup_url = f"{self.url}/diag_backup.php"

    def download_backup(self):
        try:
            csrf = self._stage1_get_token()
            csrf = self._stage2_login(csrf)
            self._stage3_download(csrf)
            print(f"{datetime.datetime.now()} [SUCCESS] Downloaded a backup copy!")
            return True
        except Exception as ex:  # noqa: BLE001 - mirror original broad catch
            print(f"{datetime.datetime.now()} [FATAL] Could not download config: {ex}")
            return False

    def _stage1_get_token(self):
        response = self.session.get(self.backup_url)
        response.raise_for_status()
        return extract_csrf_token(response.text)

    def _stage2_login(self, csrf):
        data = {
            "login": "Login",
            "usernamefld": self.username,
            "passwordfld": self.password,
            "__csrf_magic": csrf,
        }
        response = self.session.post(self.backup_url, data=data)
        response.raise_for_status()

        # pfSense does not return a 403, so check the body for the error string.
        if "Username or Password incorrect" in response.text:
            raise UsernamePasswordInvalidError("Username or Password incorrect")

        return extract_csrf_token(response.text)

    def _stage3_download(self, csrf):
        data = {
            "download": "download",
            "donotbackuprrd": "yes",
            "__csrf_magic": csrf,
        }
        response = self.session.post(self.backup_url, data=data)
        response.raise_for_status()

        file_name = to_safe_filename(f"pfSenseBackup-{datetime.datetime.now()}.xml")
        os.makedirs("backups", exist_ok=True)
        with open(os.path.join("backups", file_name), "w", encoding="utf-8") as fh:
            fh.write(response.text)


def main(argv):
    if len(argv) != 3:
        print(
            "Please run this application with three arguments: the URL of your "
            "pfSense machine, your username and password "
            "E.g. https://mypfsense:8443 admin password"
        )
        return 1

    url, username, password = argv
    pfsense = PfSense(url, username, password)
    return 0 if pfsense.download_backup() else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
