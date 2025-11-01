```markdown
# central_mapping

This folder holds central mapping files used by the Kometa MediUX Resolver (`kometa-resolver` / `kometa_mediux_resolver.py`) to decide where to insert generated `url_poster` (and similar) entries.

Design
- `write_path_map.yml` — maps MediUX set ids, TVDB ids, and filenames to a dot-separated insertion path inside the YAML (e.g. `metadata.372264.seasons`).

Precedence
1. Per-file marker comment in the YAML: `# kometa:write_path=metadata.372264.seasons`
2. `scripts/kometa_mediux_resolver/central_mapping/write_path_map.yml` entries (set -> tvdb -> filename)
3. Heuristics implemented in the script

Notes
- The mapping folder is intentionally kept in the repo by default so the script can use these mappings as a fallback during automated runs. If you prefer this to be local-only (learning/dev mode), add `scripts/kometa_mediux_resolver/central_mapping/` to `.gitignore` and `.dockerignore`.
- `percyjacks(collection).yml` was intentionally omitted from the mapping; collections that span multiple shows can be handled per-file or via per-file markers.

```
