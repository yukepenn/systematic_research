"""GENESIS_FREEDATA_CBOE_20260828 — bounded download step (spec download_protocol).

Downloads the free Cboe volatility complex + CFTC COT into raw/ QUARANTINE.
Raw files may contain post-seal (>= 2026-08-01) rows: this script NEVER parses,
prints, or inspects file CONTENT — it records only url, sha256, bytes, HTTP status,
Last-Modified header, retrieval timestamp (UTC). Certification/truncation happens
in certify.py via research_sdk.seal_guard.

Caps (spec): total 100 MB, per-file 30 MB — enforced, abort on breach.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests

RUN = Path(r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\runs\GENESIS_FREEDATA_CBOE_20260828")
RAW = RUN / "raw"
TOTAL_CAP = 100 * 1024 * 1024
FILE_CAP = 30 * 1024 * 1024
UA = {"User-Agent": "Mozilla/5.0 (research; bounded academic download; contact: none)"}
SLEEP = 0.15

session = requests.Session()
session.headers.update(UA)

manifest: list[dict] = []
total_bytes = 0


class CapError(RuntimeError):
    pass


def head_ok(url: str) -> bool:
    try:
        r = session.head(url, timeout=30, allow_redirects=True)
        return r.status_code == 200
    except requests.RequestException:
        return False


def fetch(url: str, dest_rel: str, note: str, required: bool) -> bool:
    """Download url -> raw/dest_rel. Returns True on success. Never prints content."""
    global total_bytes
    dest = RAW / dest_rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    status, content, lm, ctype, err = None, None, None, None, None
    for attempt in (1, 2, 3):
        try:
            r = session.get(url, timeout=90)
            status = r.status_code
            lm = r.headers.get("Last-Modified")
            ctype = r.headers.get("Content-Type")
            if status == 200:
                content = r.content
                break
            if status in (403, 404):
                break  # definitive absence — no retry
        except requests.RequestException as e:
            err = type(e).__name__
        time.sleep(1.0 * attempt)
    rec = {
        "url": url,
        "dest": f"raw/{dest_rel}",
        "http_status": status,
        "error": err,
        "retrieved_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "last_modified_header": lm,
        "content_type": ctype,
        "note": note,
        "required": required,
    }
    if content is not None:
        if len(content) > FILE_CAP:
            raise CapError(f"per-file cap breach: {len(content)} B from {url}")
        if total_bytes + len(content) > TOTAL_CAP:
            raise CapError(f"total cap breach at {url}")
        dest.write_bytes(content)
        total_bytes += len(content)
        rec["bytes"] = len(content)
        rec["sha256"] = hashlib.sha256(content).hexdigest()
        manifest.append(rec)
        return True
    rec["bytes"] = 0
    rec["sha256"] = None
    rec["result"] = "UNREACHABLE"
    manifest.append(rec)
    return False


# ---------------------------------------------------------------- expiry math
def third_friday(y: int, m: int) -> date:
    d = date(y, m, 1)
    fridays = [date(y, m, dd) for dd in range(1, 29) if date(y, m, dd).weekday() == 4]
    return fridays[2]


def vx_monthly_expiry_candidate(y: int, m: int) -> date:
    """Wednesday 30 days before third Friday of the FOLLOWING month (holiday shifts
    handled downstream by offset probing)."""
    ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
    return third_friday(ny, nm) - timedelta(days=30)


MONTH_CODE = {1: "F", 2: "G", 3: "H", 4: "J", 5: "K", 6: "M", 7: "N", 8: "Q", 9: "U", 10: "V", 11: "X", 12: "Z"}


def main() -> int:
    ok_core = True
    print("== [1/4] Cboe index daily-history CSVs ==", flush=True)
    idx_base = "https://cdn.cboe.com/api/global/us_indices/daily_prices/"
    for sym in ["VIX", "VIX3M", "VIX9D", "VXN", "VVIX", "SKEW", "OVX", "GVZ"]:
        got = fetch(f"{idx_base}{sym}_History.csv", f"indices/{sym}_History.csv", f"{sym} daily index history", required=sym in ("VIX", "VXN"))
        print(f"  {sym}: {'OK' if got else 'UNREACHABLE'}", flush=True)
        if not got and sym in ("VIX", "VXN"):
            ok_core = False
        time.sleep(SLEEP)

    print("== [2/4] CFE volume + open interest ==", flush=True)
    got = fetch(
        "https://cdn.cboe.com/data/us/futures/market_statistics/historical_data/cfevoloi.csv",
        "cfe/cfevoloi.csv", "CFE daily volume and open interest by product, 2004->current", required=True)
    print(f"  cfevoloi.csv: {'OK' if got else 'UNREACHABLE'}", flush=True)
    if not got:
        ok_core = False

    print("== [3/4] VX per-contract daily settlement files ==", flush=True)
    modern_base = "https://cdn.cboe.com/data/us/futures/market_statistics/historical_data/VX/"
    n_modern = 0
    modern_absent: list[str] = []
    for y in range(2013, 2028):
        for m in range(1, 13):
            cand = vx_monthly_expiry_candidate(y, m)
            hit = None
            for off in (0, -1, -2, 1, 2):
                d = cand + timedelta(days=off)
                url = f"{modern_base}VX_{d.isoformat()}.csv"
                if head_ok(url):
                    hit = (d, url, off)
                    break
                time.sleep(0.05)
            if hit is None:
                modern_absent.append(f"{y}-{m:02d}")
                continue
            d, url, off = hit
            got = fetch(url, f"vx_modern/VX_{d.isoformat()}.csv",
                        f"VX monthly contract exp {y}-{m:02d}; expiry-date file; probe offset {off} from 30-day rule", required=False)
            if got:
                n_modern += 1
            time.sleep(SLEEP)
        print(f"  modern year {y} done (cum files {n_modern})", flush=True)
    print(f"  modern: {n_modern} files; absent months: {modern_absent}", flush=True)
    if n_modern < 100:
        ok_core = False

    arch_base = "https://cdn.cboe.com/resources/futures/archive/volume-and-price/"
    n_arch = 0
    arch_absent: list[str] = []
    for y in range(2004, 2013):
        for m in range(1, 13):
            code = f"CFE_{MONTH_CODE[m]}{y % 100:02d}_VX.csv"
            url = f"{arch_base}{code}"
            if head_ok(url):
                got = fetch(url, f"vx_archive/{code}", f"VX archive contract {MONTH_CODE[m]}{y % 100:02d} (pre-2013 era)", required=False)
                if got:
                    n_arch += 1
            else:
                arch_absent.append(f"{y}-{m:02d}")
            time.sleep(SLEEP)
        print(f"  archive year {y} done (cum files {n_arch})", flush=True)
    print(f"  archive: {n_arch} files; absent months (never listed or delisted): {len(arch_absent)}", flush=True)

    print("== [4/4] CFTC COT — TFF futures-only ==", flush=True)
    n_cot = 0
    got = fetch("https://www.cftc.gov/files/dea/history/fin_fut_txt_2006_2016.zip",
                "cot/fin_fut_txt_2006_2016.zip", "TFF futures-only combined 2006-2016 (used for 2006-2009 rows)", required=True)
    print(f"  fin_fut_txt_2006_2016.zip: {'OK' if got else 'UNREACHABLE'}", flush=True)
    if got:
        n_cot += 1
    else:
        ok_core = False
    time.sleep(SLEEP)
    for y in range(2010, 2027):
        got = fetch(f"https://www.cftc.gov/files/dea/history/fut_fin_txt_{y}.zip",
                    f"cot/fut_fin_txt_{y}.zip", f"TFF futures-only annual {y}", required=(y <= 2026))
        if got:
            n_cot += 1
        else:
            ok_core = False
        time.sleep(SLEEP)
    print(f"  COT zips: {n_cot}/18", flush=True)

    (RUN / "raw" / "_MANIFEST.json").write_text(json.dumps(
        {"generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
         "total_bytes": total_bytes, "total_cap": TOTAL_CAP, "file_cap": FILE_CAP,
         "n_files_downloaded": sum(1 for r in manifest if r.get("sha256")),
         "n_unreachable": sum(1 for r in manifest if r.get("result") == "UNREACHABLE"),
         "modern_vx_absent_months": modern_absent,
         "archive_vx_absent_months": arch_absent,
         "files": manifest}, indent=1), encoding="utf-8")
    print(f"TOTAL BYTES: {total_bytes} ({total_bytes / 1e6:.1f} MB) — cap {TOTAL_CAP}", flush=True)
    print(f"CORE-DOWNLOAD-OK: {ok_core}", flush=True)
    return 0 if ok_core else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except CapError as e:
        (RUN / "raw" / "_MANIFEST.json").write_text(json.dumps({"ABORTED_CAP": str(e), "files": manifest}, indent=1), encoding="utf-8")
        print(f"ABORTED — CAP BREACH: {e}", flush=True)
        sys.exit(2)
