# kometa_mediux_sync

Small utility to scan Kometa YAML files for MediUX set URLs and propose adding missing
`url_poster` entries. The script is non-destructive by default (dry-run) and writes a
summary JSON file describing proposed changes. Use `--apply` to write changes.

Usage (from repository root):

```
python3 scripts/kometa_mediux_sync.py --root . --output /tmp/changes.json
```

Default behavior is dry-run. To actually apply the proposed updates:

```
python3 scripts/kometa_mediux_sync.py --root . --apply --output /tmp/changes.json
```

Configuration and notes:
- Provide a MediUX API key through the `--api-key` flag or the `MEDIUX_API_KEY` environment variable.
- The script will search for `mediux.pro/sets/<id>` anywhere in the YAML file (including comments) to find the set id.
- By default files with names starting with `config` are excluded to avoid altering system config files. Use `--no-exclude-config` to override.
- The summary JSON contains entries like:

Additional debugging helpers:
- `--probe-set <id>` will test candidate MediUX endpoints for a single set id and write a small JSON probe output to `--output` (useful to reproduce 404s).
- `--log-file <path>` will write structured logs to a file (timestamped entries).
 - `--file <name|path-suffix>` will limit the scan to files matching a filename or path suffix (useful for testing a single YAML).
 - `--probe-asset <url>` will GET an arbitrary asset URL and write the response (status/body truncated) to `--output`.

```json
[
  {
    "file": "libraries/series/metadata/.../something.yml",
    "set_ids": ["24172"],
    "changes": [
      {"path": ["408436"], "add": {"url_poster": "https://api.mediux.pro/assets/..."}}
    ]
  }
]
```

Next steps (future work):
- Improve mapping between specific assets and season/episode nodes (SxxExx parsing).
- Add unit tests and an integration test using a mocked MediUX API response.
- Add Dockerfile and APScheduler integration for running periodically.
