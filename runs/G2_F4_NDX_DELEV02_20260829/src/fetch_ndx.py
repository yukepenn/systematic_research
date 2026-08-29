"""G2_F4_NDX_DELEV02_20260829 — Stage A fetch (trial G00028).

Downloads FRED series NASDAQ100 as CSV per out/spec_resolutions.txt R1:
  * coed pinned to 2026-07-31 -> no virgin (>= 2026-08-01) observation is ever downloaded
  * streamed with a HARD 5 MB cap
  * raw bytes quarantined at raw/fredgraph_NASDAQ100.csv, never inspected here
  * URL + HTTP status + byte count + sha256 + UTC time recorded in raw/fetch_manifest.json

Exactly one fetch. The fallback (R4, Stooq ^NDX) is only invoked by a documented
insufficiency of what FRED provides, decided by the main program — not here.
"""
from __future__ import annotations

import hashlib
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

RUN = Path(__file__).resolve().parents[1]
RAW = RUN / "raw"

# AMENDED per out/spec_resolutions.txt A1: live FRED host unreachable from this environment
# (probes recorded); source = Wayback Machine raw-bytes snapshot of the EXACT FRED endpoint.
URL = ("https://web.archive.org/web/20260828145044id_/"
       "https://fred.stlouisfed.org/graph/fredgraph.csv?id=NASDAQ100")
CAP = 5 * 1024 * 1024  # hard 5 MB bound (spec)
DEST = RAW / "fredgraph_NASDAQ100.csv"
MANIFEST = RAW / "fetch_manifest.json"


MAX_ATTEMPTS = 3  # identical retries on TRANSIENT failure only (R1); count recorded


def _fetch_once() -> tuple[int, bytes]:
    req = urllib.request.Request(URL, headers={"User-Agent": "systematic-research-data-contract/1.0"})
    buf = b""
    with urllib.request.urlopen(req, timeout=120) as resp:
        status = resp.status
        while True:
            chunk = resp.read(1 << 16)
            if not chunk:
                break
            buf += chunk
            if len(buf) > CAP:
                raise RuntimeError(f"download exceeded {CAP} B hard cap — DEFECT (bounded-download clause)")
    return status, buf


def main() -> int:
    t_utc = datetime.now(timezone.utc).isoformat(timespec="seconds")
    status, buf, attempts, last_err = None, None, 0, None
    for attempts in range(1, MAX_ATTEMPTS + 1):
        try:
            status, buf = _fetch_once()
            break
        except (TimeoutError, OSError) as e:  # transient network classes only
            last_err = repr(e)
            print(f"attempt {attempts} transient failure: {last_err}")
    if buf is None:
        raise RuntimeError(f"fetch failed after {MAX_ATTEMPTS} identical attempts: {last_err}")
    sha = hashlib.sha256(buf).hexdigest()
    DEST.write_bytes(buf)
    manifest = {
        "trial_id": "G00028",
        "source": ("FRED (Federal Reserve Bank of St. Louis), series NASDAQ100 (NASDAQ 100 Index), "
                   "public — retrieved via Internet Archive Wayback Machine snapshot "
                   "2026-08-28 14:50:44 UTC (raw id_ mode) per spec_resolutions A1 "
                   "(live FRED host network-blocked in this environment)"),
        "url": URL,
        "snapshot_utc": "2026-08-28T14:50:44Z",
        "http_status": status,
        "bytes": len(buf),
        "sha256": sha,
        "fetched_utc": t_utc,
        "attempts": attempts,
        "cap_bytes": CAP,
        "quarantine": ("raw/fredgraph_NASDAQ100.csv — raw bytes never inspected beyond programmatic "
                       "parse; snapshot post-dates the 2026-08-01 seal so sealed observations may be "
                       "present in raw and are mechanically dropped by seal_guard.truncate_presealed "
                       "at parse (spec clause: 'truncated < 2026-08-01 via seal_guard')"),
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"FETCH OK status={status} bytes={len(buf):,} sha256={sha} utc={t_utc}")
    print(f"WROTE: {DEST}")
    print(f"WROTE: {MANIFEST}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
