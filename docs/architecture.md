# Architecture

## Summary

- One script, `pfsense_backup.py`, no package structure.
- HTTP client: `requests.Session` with cookie handling; TLS verification off,
  `urllib3` `InsecureRequestWarning` suppressed.
- Output: one XML file per run in `./backups/` relative to the current working
  directory (`/app/backups` in the Docker image, `WORKDIR /app`).

## Code map (`pfsense_backup.py`)

| Identifier | Responsibility |
| --- | --- |
| `CSRF_RE` | Regex for the `__csrf_magic` hidden field |
| `UNSAFE_FILENAME_CHARS`, `to_safe_filename()` | Strip characters not allowed in file names |
| `extract_csrf_token()` | Return the CSRF token or raise `ValueError` |
| `UsernamePasswordInvalidError` | Raised when the login page reports wrong credentials |
| `PfSense` | Session, `backup_url = <url>/diag_backup.php`, `download_backup()` and the three stages |
| `main(argv)` | Validates exactly three arguments, returns exit code |

## Flow

1. `main()` requires `<url> <username> <password>`; otherwise prints usage and
   returns `1`.
2. `_stage1_get_token()`: `GET diag_backup.php`, extract `__csrf_magic`.
3. `_stage2_login()`: `POST` `login=Login`, `usernamefld`, `passwordfld`,
   `__csrf_magic`. pfSense answers 200 on failure, so the body is checked for
   `Username or Password incorrect`. Returns the new CSRF token.
4. `_stage3_download()`: `POST` `download=download`, `donotbackuprrd=yes`,
   `__csrf_magic`. Writes `response.text` to
   `backups/pfSenseBackup-<datetime.now()>.xml` (unsafe characters such as `:`
   removed).
5. `download_backup()` catches every exception, prints
   `<timestamp> [FATAL] Could not download config: <error>` and returns
   `False`; success prints `<timestamp> [SUCCESS] Downloaded a backup copy!`.
6. Exit code: `0` on success, `1` on failure or wrong arguments.

## Invariants

- Credentials are only sent in the login `POST` body; they are never printed.
- RRD data is excluded from the backup (`donotbackuprrd=yes`).
- One run writes one file; existing backups are never touched.

## Known limitations

- The password is a command-line argument and is visible in the process list
  and shell history.
- No request timeouts are set on `requests` calls.
- The output directory is fixed to `backups/` in the working directory.
