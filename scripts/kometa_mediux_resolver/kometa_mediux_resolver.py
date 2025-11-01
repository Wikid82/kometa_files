#!/usr/bin/env python3
"""
Kometa MediUX Resolver

kometa_mediux_sync.py

Kometa MediUX Resolver scans Kometa YAML files for MediUX set URLs, discovers
candidate assets (title_card, poster, backdrop) from MediUX, probes them for
accessibility, and proposes adding missing `url_poster` (and related) entries.

The tool is non-destructive by default (dry-run) and emits a summary JSON file
describing proposed changes. Use --apply to write changes; the script creates a
timestamped backup before modifying any file.

Recommended CLI slug: `kometa-resolver` (the script filename remains
`kometa_mediux_sync.py`). See README for examples and configuration.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import requests
import yaml


# Note: environment file loading has been intentionally removed.
# Configuration is loaded solely from the config file in the resolver's
# `config/` folder. CLI flags override config file values.

SET_URL_RE = re.compile(r"mediux\.pro/sets/(\d+)")


def find_set_ids_in_text(text: str) -> List[str]:
    return list({m.group(1) for m in SET_URL_RE.finditer(text)})


def fetch_set_assets(api_base: str, set_id: str, api_key: Optional[str] = None, timeout=10) -> List[Dict[str, Any]]:
    """Try a couple of plausible MediUX API endpoints and normalize a list of assets.

    Returns a list of dicts with at least 'id' (uuid) and optionally 'type' and 'name'.
    """
    headers = {}
    if api_key:
        headers['Authorization'] = f"Bearer {api_key}"

    candidates = [
        f"{api_base.rstrip('/')}/sets/{set_id}",
        f"{api_base.rstrip('/')}/sets/{set_id}/assets",
        f"{api_base.rstrip('/')}/api/sets/{set_id}",
        f"{api_base.rstrip('/')}/api/sets/{set_id}/assets",
        f"{api_base.rstrip('/')}/assets?set_id={set_id}",
        f"{api_base.rstrip('/')}/assets?set={set_id}",
        f"{api_base.rstrip('/')}/api/assets?set_id={set_id}",
    ]

    for url in candidates:
        try:
            r = requests.get(url, headers=headers, timeout=timeout)
        except Exception as e:
            logging.debug("Failed to fetch %s: %s", url, e)
            continue

        if r.status_code != 200:
            # log some body for debugging (truncated)
            body = r.text[:1000].replace('\n', ' ')
            logging.debug("Non-200 from %s: %s -- body: %s", url, r.status_code, body)
            continue

        try:
            data = r.json()
        except Exception:
            # helpful debug output for non-JSON responses
            body = r.text[:1000].replace('\n', ' ')
            logging.debug("Response from %s is not JSON (body truncated): %s", url, body)
            continue

        # possible shapes: {'assets': [...]}, {'data': {'assets': [...]}} or list directly
        assets = None
        if isinstance(data, dict):
            if 'assets' in data and isinstance(data['assets'], list):
                assets = data['assets']
            elif 'data' in data:
                if isinstance(data['data'], dict) and 'assets' in data['data']:
                    assets = data['data']['assets']
                elif isinstance(data['data'], list):
                    assets = data['data']
        elif isinstance(data, list):
            assets = data

        if not assets:
            logging.debug("No assets found at %s (keys: %s)", url, list(data.keys()) if isinstance(data, dict) else type(data))
            continue

        normalized = []
        for a in assets:
            if not isinstance(a, dict):
                continue
            # infer uuid/id
            aid = a.get('id') or a.get('uuid') or a.get('asset_id')
            name = a.get('name') or a.get('filename') or a.get('title')
            atype = a.get('type') or a.get('asset_type')
            # If the asset object itself is lightweight and only has nested meta, try to find uuid inside
            if not aid:
                for v in a.values():
                    if isinstance(v, str) and re.match(r"[0-9a-fA-F-]{20,}", v):
                        aid = v
                        break

            normalized.append({'id': aid, 'name': name, 'type': atype, 'raw': a})

        return normalized

    return []


def fetch_set_assets_with_scrape(api_base: str, set_id: str, api_key: Optional[str] = None, use_scrape: bool = False, mediux_opts: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Wrap fetch_set_assets and optionally fallback to scraping the MediUX set page to extract asset ids."""
    assets = fetch_set_assets(api_base, set_id, api_key, timeout=10)
    if assets:
        return assets

    if not use_scrape:
        return []

    # lazy import of our scraper helper (it's optional). Try a few import strategies
    try:
        from .mediux_scraper import MediuxScraper, extract_asset_ids_from_yaml
    except Exception:
        try:
            from scripts.mediux_scraper import MediuxScraper, extract_asset_ids_from_yaml
        except Exception:
            # final attempt: import directly from the scripts/mediux_scraper.py file path
            try:
                import importlib.util
                mod_path = Path(__file__).resolve().parent / 'mediux_scraper.py'
                spec = importlib.util.spec_from_file_location('mediux_scraper', str(mod_path))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                MediuxScraper = getattr(mod, 'MediuxScraper')
                extract_asset_ids_from_yaml = getattr(mod, 'extract_asset_ids_from_yaml')
            except Exception:
                logging.warning('MediUX scraper not available (selenium not installed or import failed). Cannot scrape set %s', set_id)
                return []

    set_url = f"https://mediux.pro/sets/{set_id}"
    username = None
    password = None
    nickname = None
    headless = True
    profile_path = None
    chromedriver_path = None

    if mediux_opts:
        username = mediux_opts.get('username')
        password = mediux_opts.get('password')
        nickname = mediux_opts.get('nickname')
        headless = mediux_opts.get('headless', True)
        profile_path = mediux_opts.get('profile_path')
        chromedriver_path = mediux_opts.get('chromedriver_path')

    scraper = MediuxScraper()
    try:
        yaml_text = scraper.scrape_set_yaml(
            set_url,
            username=username,
            password=password,
            nickname=nickname,
            headless=headless,
            profile_path=profile_path,
            chromedriver_path=chromedriver_path,
        )
    except Exception as e:
        logging.warning('Scraper failed for set %s: %s', set_id, e)
        return []

    if not yaml_text:
        logging.info('Scraper returned no YAML for set %s', set_id)
        return []

    extracted = extract_asset_ids_from_yaml(yaml_text)
    if not extracted:
        return []

    # extracted may be a list of uuid strings or a list of dicts {id, fileType}
    normalized = []
    for item in extracted:
        if isinstance(item, dict):
            normalized.append({'id': item.get('id'), 'name': None, 'type': item.get('fileType'), 'raw': item})
        else:
            normalized.append({'id': item, 'name': None, 'type': None, 'raw': {}})
    return normalized


def probe_url(url: str, api_key: Optional[str] = None, timeout: int = 10) -> Dict[str, Any]:
    """GET the URL and return status and truncated body for debugging."""
    headers = {}
    if api_key:
        headers['Authorization'] = f"Bearer {api_key}"
    try:
        r = requests.get(url, headers=headers, timeout=timeout)
    except Exception as e:
        logging.debug("Probe failed for %s: %s", url, e)
        return {'url': url, 'status': None, 'error': str(e)}

    body = None
    try:
        body = r.text[:2000]
    except Exception:
        body = '<unable to read body>'

    return {'url': url, 'status': r.status_code, 'body': body}


def pick_best_asset(assets: List[Dict[str, Any]]) -> List[str]:
    """Return asset ids ordered by preferred fileType.

    Preference order (per user):
      1) title_card
      2) poster
      3) backdrop

    The function returns a list of candidate asset ids (strings) in preference order
    followed by any remaining assets. It does NOT probe the asset URLs — probing is
    performed by the caller so we only select assets that are actually reachable.
    """
    if not assets:
        return []

    priority = ['title_card', 'title-card', 'titlecard', 'poster', 'backdrop']

    def key_fn(a: Dict[str, Any]) -> int:
        # lower score for higher priority so sorting ascending gives preferred first
        t = (a.get('type') or '') or ''
        n = (a.get('name') or '') or ''
        tn = (t + ' ' + n).lower()
        for idx, token in enumerate(priority):
            if token in tn:
                return idx
        # put unknown types after priority list
        return len(priority)

    # stable sort by key_fn and return ids in that order
    sorted_assets = sorted([a for a in assets if a.get('id')], key=key_fn)
    ids = [a.get('id') for a in sorted_assets if a.get('id')]

    # fallback: if no ids collected above, look for uuid-like strings in raw data
    if not ids:
        for a in assets:
            raw = a.get('raw')
            if isinstance(raw, dict):
                for v in raw.values():
                    if isinstance(v, str) and re.match(r"[0-9a-fA-F-]{20,}", v):
                        ids.append(v)
    return ids


def construct_asset_url(api_base: str, asset_id: str) -> str:
    return f"{api_base.rstrip('/')}/assets/{asset_id}"


def gather_yaml_metadata_paths(obj: Any, prefix: Tuple = ()) -> List[Tuple[Tuple, Any]]:
    """Recursively collect nodes (path, node) where node is a mapping that may contain 'url_poster'.

    Path is a tuple of keys to reach the mapping from root.
    """
    results = []

    if isinstance(obj, dict):
        results.append((prefix, obj))
        for k, v in obj.items():
            if isinstance(v, dict):
                results.extend(gather_yaml_metadata_paths(v, prefix + (k,)))
            elif isinstance(v, list):
                # skip lists for now
                continue
    return results


def propose_changes_for_file(file_path: Path, api_base: str, api_key: Optional[str], use_scrape: bool = False, mediux_opts: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    text = file_path.read_text(encoding='utf-8')
    if 'metadata:' not in text:
        return None

    set_ids = find_set_ids_in_text(text)
    if not set_ids:
        logging.debug("No MediUX set URL found in %s", file_path)
        return None

    try:
        yaml_obj = yaml.safe_load(text)
    except Exception as e:
        logging.warning("Failed to parse YAML %s: %s", file_path, e)
        return None

    if not isinstance(yaml_obj, dict) or 'metadata' not in yaml_obj:
        logging.debug("File %s has no metadata key after parse", file_path)
        return None

    metadata = yaml_obj['metadata']
    if not isinstance(metadata, dict):
        return None

    changes = []

    # For each set id, fetch assets once and reuse
    assets_cache: Dict[str, List[Dict[str, Any]]] = {}
    for sid in set_ids:
        assets_cache[sid] = fetch_set_assets_with_scrape(api_base, sid, api_key, use_scrape=use_scrape, mediux_opts=mediux_opts)

    # For each metadata entry (usually keyed by numeric id), traverse nested dicts
    for top_key, top_val in metadata.items():
        if not isinstance(top_val, dict):
            continue

        # gather all nested mapping nodes under this metadata entry
        nodes = gather_yaml_metadata_paths(top_val, prefix=(str(top_key),))
        for path, node in nodes:
            # only consider mappings that don't already have url_poster
            if 'url_poster' in node and node.get('url_poster'):
                continue

            # pick an available asset using preference order (title_card, poster, backdrop)
            chosen_asset = None
            chosen_probe = None
            for sid, assets in assets_cache.items():
                # pick_best_asset now returns ordered list of candidate ids
                candidates = pick_best_asset(assets)
                for aid in candidates:
                    if not aid:
                        continue
                    candidate_url = construct_asset_url(api_base, aid)
                    probe = probe_url(candidate_url, api_key)
                    # accept only assets that are accessible (HTTP 200)
                    if probe.get('status') == 200:
                        chosen_asset = candidate_url
                        chosen_probe = probe
                        break
                if chosen_asset:
                    break

            if chosen_asset:
                change = {
                    'path': list(path),
                    'add': {'url_poster': chosen_asset},
                    'probe': chosen_probe,
                }
                changes.append(change)

    if changes:
        return {'file': str(file_path), 'set_ids': set_ids, 'changes': changes}
    return None


def scan_root(root: Path, api_base: str, api_key: Optional[str], exclude_config: bool = True, file_filter: Optional[str] = None, use_scrape: bool = False, mediux_opts: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Scan YAML files under root. If file_filter is provided, only files matching
    the filter (by exact name or suffix) are considered.
    """
    results = []

    def match_file(p: Path) -> bool:
        if exclude_config and p.name.lower().startswith('config'):
            return False
        if not file_filter:
            return True
        # if user provided a path-like filter, check suffix; else check filename contains
        if os.path.sep in file_filter or '/' in file_filter:
            return str(p).endswith(file_filter)
        # match by exact name or substring
        return p.name == file_filter or file_filter in p.name

    for p in list(root.rglob('*.yml')) + list(root.rglob('*.yaml')):
        if not match_file(p):
            continue
        try:
            r = propose_changes_for_file(p, api_base, api_key, use_scrape=use_scrape, mediux_opts=mediux_opts)
        except Exception as e:
            logging.exception('Error processing %s: %s', p, e)
            continue
        if r:
            results.append(r)

    return results


def apply_changes(changes: List[Dict[str, Any]], apply: bool = False, require_probe_ok: bool = True, create_backup: bool = True) -> None:
    """Apply changes to files. If apply is False, only write the summary (already done by caller).

    Implementation note: this is conservative and creates a timestamped backup before writing.
    """
    import time

    # attempt to load JSON schema for validation (optional)
    schema = None
    try:
        import json as _json
        schema_path = Path(__file__).resolve().parent / 'kometa_metadata_schema.json'
        if schema_path.exists():
            schema = _json.loads(schema_path.read_text(encoding='utf-8'))
    except Exception:
        schema = None

    # helper to stringify mapping keys for JSON Schema validation
    def _stringify(obj):
        if isinstance(obj, dict):
            return {str(k): _stringify(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_stringify(x) for x in obj]
        return obj

    for entry in changes:
        file_path = Path(entry['file'])
        if not file_path.exists():
            logging.warning('File no longer exists: %s', file_path)
            continue
        text = file_path.read_text(encoding='utf-8')
        # Prefer ruamel.yaml for round-trip preservation of comments/formatting.
        use_ruamel = False
        ruamel_loader = None
        try:
            from ruamel.yaml import YAML as _YAML
            ruamel_loader = _YAML()
            # preserve existing formatting as much as possible
            ruamel_loader.preserve_quotes = True
            ruamel_loader.width = 4096
            use_ruamel = True
        except Exception:
            use_ruamel = False

        try:
            if use_ruamel and ruamel_loader:
                yaml_obj = ruamel_loader.load(text) or {}
            else:
                yaml_obj = yaml.safe_load(text) or {}
        except Exception as e:
            logging.warning('Failed to parse YAML before apply for %s: %s', file_path, e)
            continue

        metadata = yaml_obj.get('metadata')
        if not isinstance(metadata, dict):
            logging.warning('No metadata to apply to in %s', file_path)
            continue

        changed = False
        for c in entry['changes']:
            path = c['path']
            add = c.get('add', {})
            probe = c.get('probe')
            if require_probe_ok and probe:
                status = probe.get('status')
                if status != 200:
                    logging.warning('Skipping change for %s path %s because probe status is %s', file_path, path, status)
                    continue
            # navigate to the mapping: path[0] should be metadata top-key (e.g. tvdb id)
            node = metadata
            try:
                if not path:
                    raise RuntimeError('Empty path')
                # Ensure we step into the top-level metadata key first
                topk = path[0]
                # if the top-level key exists, use it; otherwise create mapping under metadata
                if topk in node and isinstance(node[topk], dict):
                    node = node[topk]
                else:
                    # create the top-level mapping under metadata
                    node = node.setdefault(topk, {})

                for k in path[1:]:
                    # descend, creating intermediate mappings as needed
                    if not isinstance(node, dict):
                        raise RuntimeError('Path leads to non-mapping')
                    node = node.setdefault(k, {})
            except Exception as e:
                logging.warning('Failed to navigate path %s in %s: %s', path, file_path, e)
                continue

            for kk, vv in add.items():
                if kk not in node or not node.get(kk):
                    node[kk] = vv
                    changed = True

        if changed and apply:
            # if schema loaded, validate the resulting YAML before writing
            if schema is not None:
                try:
                    try:
                        from jsonschema import validate as _validate
                    except Exception:
                        # jsonschema not available despite requirements; fall back
                        _validate = None

                    if _validate:
                        inst = _stringify(yaml_obj)
                        _validate(instance=inst, schema=schema)
                except Exception as ve:
                    logging.warning('Validation failed for %s: %s. Skipping write.', file_path, ve)
                    # continue to next file without writing
                    continue

            # write new YAML. If create_backup is True, preserve the original as a timestamped .bak.<ts>
            ts = int(time.time())
            if create_backup:
                bak = file_path.with_suffix(file_path.suffix + f'.bak.{ts}')
                try:
                    file_path.rename(bak)
                except Exception as e:
                    logging.exception('Failed to create backup %s for %s: %s', bak, file_path, e)
                    # fall through to attempt write without backup
                    bak = None

                try:
                    if use_ruamel and ruamel_loader:
                        with file_path.open('w', encoding='utf-8') as fh:
                            ruamel_loader.dump(yaml_obj, fh)
                    else:
                        file_path.write_text(yaml.safe_dump(yaml_obj, sort_keys=False, allow_unicode=True), encoding='utf-8')
                    logging.info('Applied changes to %s (backup %s)', file_path, bak)
                except Exception as e:
                    logging.exception('Failed to write updated YAML to %s: %s', file_path, e)
                    # attempt to restore backup
                    try:
                        if file_path.exists():
                            file_path.unlink()
                        if bak and bak.exists():
                            bak.rename(file_path)
                            logging.info('Restored backup %s to %s after failed write', bak, file_path)
                    except Exception:
                        logging.exception('Failed to restore backup %s after failed write', bak)
            else:
                # no backup requested: write to a temporary file then atomically replace
                tmp = file_path.with_suffix(file_path.suffix + f'.tmp.{ts}')
                try:
                    if use_ruamel and ruamel_loader:
                        with tmp.open('w', encoding='utf-8') as fh:
                            ruamel_loader.dump(yaml_obj, fh)
                    else:
                        tmp.write_text(yaml.safe_dump(yaml_obj, sort_keys=False, allow_unicode=True), encoding='utf-8')
                    # atomic replace
                    os.replace(str(tmp), str(file_path))
                    logging.info('Applied changes to %s (no backup)', file_path)
                except Exception as e:
                    logging.exception('Failed to write updated YAML to %s: %s', file_path, e)
                    try:
                        if tmp.exists():
                            tmp.unlink()
                    except Exception:
                        pass
        elif changed:
            logging.info('Would apply changes to %s (dry-run)', file_path)


def main(argv=None):
    # Keep the script filename stable but recommend a concise CLI program name.
    parser = argparse.ArgumentParser(prog='kometa-resolver')
    parser.add_argument('--root', '-r', default='.', help='Root path to scan (default: repository root)')
    parser.add_argument('--api-base', default='https://api.mediux.pro', help='MediUX API base URL')
    parser.add_argument('--api-key', default=None, help='MediUX API key (overrides config file)')
    parser.add_argument('--apply', action='store_true', help='Actually write changes (default: dry-run)')
    parser.add_argument('--output', default='.kometa_mediux_changes.json', help='Summary output (JSON)')
    parser.add_argument('--verbose', '-v', action='count', default=0, help='Increase verbosity')
    parser.add_argument('--no-exclude-config', dest='exclude_config', action='store_false', help='Do not exclude files named config*')
    parser.add_argument('--log-file', default=None, help='Optional log file to write logs to')
    parser.add_argument('--log-max-bytes', dest='log_max_bytes', type=int, default=1048576, help='Max bytes per log file before rotation (default: 1048576)')
    parser.add_argument('--log-backups', dest='log_backups', type=int, default=5, help='Number of rotated log files to keep (default: 5)')
    parser.add_argument('--probe-set', default=None, help='If provided, probe MediUX endpoints for this set id and exit')
    parser.add_argument('--file', dest='file_filter', default=None, help='If provided, only scan files matching this name or path suffix')
    parser.add_argument('--probe-asset', dest='probe_asset', default=None, help='If provided, probe this asset URL and exit')
    parser.add_argument('--require-probe-ok', dest='require_probe_ok', action='store_true', help='Only apply additions if asset probe returns HTTP 200')
    parser.add_argument('--use-scrape', dest='use_scrape', action='store_true', help='When API listing fails, use Selenium scraper fallback to fetch MediUX YAML')
    parser.add_argument('--mediux-username', dest='mediux_username', default=None, help='Mediux username (overrides config file)')
    parser.add_argument('--mediux-password', dest='mediux_password', default=None, help='Mediux password (overrides config file)')
    parser.add_argument('--mediux-nickname', dest='mediux_nickname', default=None, help='Mediux nickname (overrides config file)')
    parser.add_argument('--profile-path', dest='profile_path', default=None, help='Chrome profile path to reuse')
    parser.add_argument('--chromedriver-path', dest='chromedriver_path', default=None, help='Path to chromedriver executable')
    parser.add_argument('--no-headless', dest='headless', action='store_false', help='Run browser with UI (not headless)')
    parser.add_argument('--apply-backup', dest='apply_backup', action='store_true', help='When applying, keep a timestamped backup of the original file (overrides config)')

    args = parser.parse_args(argv)

    # Load configuration file (YAML). Precedence for values is:
    # CLI args > config file > defaults.
    cfg = {}
    try:
        cfg_path = str(Path(__file__).resolve().parent / 'config' / 'config.yml')
        cfgp = Path(cfg_path)
        if cfgp.exists():
            try:
                cfg = yaml.safe_load(cfgp.read_text(encoding='utf-8')) or {}
            except Exception:
                logging.warning('Failed to parse config file %s; ignoring', cfgp)
                cfg = {}
    except Exception:
        cfg = {}

    # Helper: parse boolean-like values from env/config
    def _bool_from(val, default=False):
        if val is None:
            return default
        if isinstance(val, bool):
            return val
        s = str(val).strip().lower()
        return s in ('1', 'true', 'yes', 'on')

    # Resolve logging enabled (default: true). Read from config only.
    logging_enabled = _bool_from(cfg.get('logging', True))

    # Resolve root path: CLI > config > default '.'
    root_override = args.root or cfg.get('root') or '.'
    args.root = root_override

    # Resolve apply/backup defaults (CLI > config)
    cfg_apply = cfg.get('apply', True)
    args.apply = args.apply or cfg_apply

    cfg_backup = cfg.get('backup', False)
    # CLI flag --apply-backup overrides config
    args.apply_backup = args.apply_backup or cfg_backup

    # Resolve logging file and rotation settings (CLI flags already may be present)
    args.log_file = args.log_file or cfg.get('log_file')
    args.log_max_bytes = getattr(args, 'log_max_bytes', None) or int(cfg.get('log_max_bytes', 1048576))
    args.log_backups = getattr(args, 'log_backups', None) or int(cfg.get('log_backups', 5))

    # Ensure logs dir exists if a relative path is configured
    try:
        if args.log_file:
            # resolve to an absolute path under the resolver folder when a relative path is used
            logp = Path(args.log_file)
            if not logp.is_absolute():
                logp = Path(__file__).resolve().parent / args.log_file
            logdir = logp.parent
            logdir.mkdir(parents=True, exist_ok=True)
            # replace args.log_file with the absolute path so handlers open the right location
            args.log_file = str(logp)
    except Exception:
        pass

    level = logging.WARNING
    # Verbosity from CLI (-v) takes precedence. If omitted, use config.log_level.
    if args.verbose >= 2:
        level = logging.DEBUG
    elif args.verbose == 1:
        level = logging.INFO
    else:
        # read config default log_level (e.g. INFO, DEBUG). Fallback to WARNING.
        try:
            cfg_level = str(cfg.get('log_level', 'WARNING')).upper()
            level = getattr(logging, cfg_level, logging.WARNING)
        except Exception:
            level = logging.WARNING

    # configure logging: use a rotating file handler when --log-file provided
    if args.log_file:
        try:
            from logging.handlers import RotatingFileHandler
        except Exception:
            RotatingFileHandler = None

        fmt = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')

        if RotatingFileHandler:
            try:
                rfh = RotatingFileHandler(
                    args.log_file,
                    maxBytes=args.log_max_bytes,
                    backupCount=args.log_backups,
                )
                rfh.setLevel(level)
                rfh.setFormatter(fmt)

                # console handler for immediate stdout/stderr
                ch = logging.StreamHandler()
                ch.setLevel(level)
                ch.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))

                root = logging.getLogger()
                root.setLevel(level)
                # clear any existing handlers (avoid duplicate logs on repeated runs)
                for h in list(root.handlers):
                    root.removeHandler(h)
                root.addHandler(rfh)
                root.addHandler(ch)
            except Exception:
                # fallback to basicConfig if handler creation fails
                logging.basicConfig(level=level, format='%(asctime)s %(levelname)s: %(message)s', filename=args.log_file)
        else:
            logging.basicConfig(level=level, format='%(asctime)s %(levelname)s: %(message)s', filename=args.log_file)
    else:
        logging.basicConfig(level=level, format='%(levelname)s: %(message)s')

    api_key = args.api_key or cfg.get('api_key')

    # mediux scraping options (CLI > config)
    mediux_username = args.mediux_username or cfg.get('mediux_username')
    mediux_password = args.mediux_password or cfg.get('mediux_password')
    mediux_nickname = args.mediux_nickname or cfg.get('mediux_nickname')
    profile_path = args.profile_path or cfg.get('profile_path')
    chromedriver_path = args.chromedriver_path or cfg.get('chromedriver_path')
    headless = getattr(args, 'headless', True)

    mediux_opts = {
        'username': mediux_username,
        'password': mediux_password,
        'nickname': mediux_nickname,
        'profile_path': profile_path,
        'chromedriver_path': chromedriver_path,
        'headless': headless,
    }

    root = Path(args.root).resolve()
    if not root.exists():
        logging.error('Root does not exist: %s', root)
        return 2

    # If probe-asset is provided, probe it and exit (avoid scanning repo)
    if args.probe_asset:
        logging.info('Probing MediUX asset URL %s', args.probe_asset)
        probe = probe_url(args.probe_asset, api_key)
        out = Path(args.output)
        out.write_text(json.dumps({'probe_asset': args.probe_asset, 'probe': probe}, indent=2), encoding='utf-8')
        logging.info('Wrote probe output to %s', out)
        return 0

    # If probe-set is provided, just test candidate endpoints and print debug info
    if args.probe_set:
        logging.info('Probing MediUX endpoints for set id %s', args.probe_set)
        if args.use_scrape:
            assets = fetch_set_assets_with_scrape(args.api_base, args.probe_set, api_key, use_scrape=True, mediux_opts=mediux_opts)
        else:
            assets = fetch_set_assets(args.api_base, args.probe_set, api_key)
        # write probe result to output and exit
        out = Path(args.output)
        out.write_text(json.dumps({'probe_set': args.probe_set, 'assets': assets}, indent=2), encoding='utf-8')
        logging.info('Wrote probe output to %s', out)
        return 0

    # Determine whether logging is enabled (default: True). We loaded `logging_enabled`
    # from config/env earlier; if it's False, suppress non-critical logging.
    try:
        logging_enabled
    except NameError:
        logging_enabled = True

    if not logging_enabled:
        # disable logging by raising the level very high and removing handlers
        root_logger = logging.getLogger()
        for h in list(root_logger.handlers):
            root_logger.removeHandler(h)
        logging.getLogger().addHandler(logging.NullHandler())
        logging.getLogger().setLevel(logging.CRITICAL)

    logging.info('Scanning %s (dry-run=%s)', root, not args.apply)
    results = scan_root(
        root,
        args.api_base,
        api_key,
        exclude_config=args.exclude_config,
        file_filter=args.file_filter,
        use_scrape=args.use_scrape,
        mediux_opts=mediux_opts,
    )

    # write summary
    out = Path(args.output)
    out.write_text(json.dumps(results, indent=2), encoding='utf-8')
    logging.info('Wrote summary to %s', out)

    if args.apply:
        # args.apply_backup determines whether to keep a timestamped .bak file.
        apply_changes(results, apply=True, require_probe_ok=args.require_probe_ok, create_backup=bool(getattr(args, 'apply_backup', False)))
    else:
        logging.info('Dry-run complete. Use --apply to write changes.')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
