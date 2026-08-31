"""data_census.py - the AUTHORITATIVE capability model for the local NinjaTrader 8 store.

WHY THIS MODULE EXISTS
----------------------
Five separate "we do not have X" conclusions in this repository were later shown false. All five
traced to TWO lines of code, not to five mistakes:

  research/data/build_registry.py:211
      mm = RM[(RM["kind"] == "minute") & (RM["series"] == "Last") & (RM["distinct_usable"] > 100)]
      -- silently dropped every Bid and Ask series, and every instrument with a short history.

  runs/DATA_CAPABILITY_AUDIT_20260827/src/enumerate_nt8_store.py:34
      ROOT_OF = re.compile(r"^([A-Z0-9]{1,4})\s+(\d{2})-(\d{2})$")
      -- CANNOT MATCH "^TICK", "^TRIN", "^VIX", "^ADD", "MSFT", "USDJPY", or a bare root like "NQ".
         It was the only minute-level input to the registry, so anything it could not name did not
         exist as far as this repository was concerned.

The governing design rule, and the reason this file is written the way it is:

    AN ENUMERATOR MUST NEVER FILTER. It reports what is on disk, classifies it explicitly, and
    marks what it does not understand as UNKNOWN. Selection is the CALLER's job, performed on the
    full table, in the open. A regex whose allowed character class quietly defines the research
    frontier is the defect this module exists to make impossible.

STRUCTURAL FACTS, MEASURED NOT ASSUMED (2026-08-31, 51,935 .ncd files)
---------------------------------------------------------------------
NCD files are a 31-byte header followed by records. Verified by reading bytes:

    minute/^TICK/20130105.Last.ncd   size 32     header + 1 trailing byte, ZERO bars
    minute/^TICK/20201017.Last.ncd   size 36     header + 5, a handful of bars
    minute/^TICK/20200228.Last.ncd   size 3943   a full session

Day-bar files are a clean header(28) + 48-byte records: the sorted distinct sizes in db/day/*/*.Last
.ncd differ by exactly 48, and the minimum observed is 76 = 28 + 48 = one single day bar.

Whole-store size distribution:  <=32 B: 1,148   33-200 B: 961   201-1000 B: 561   >1000 B: 49,265

THEREFORE the old "<= 32 bytes means empty" rule was RIGHT ABOUT ITS SIGNATURE and WRONG ABOUT ITS
SEMANTICS. 32 bytes is genuinely a zero-record minute file. But 36 bytes is not "data" in any useful
sense either - it is a session with a couple of prints. Collapsing that to a boolean is what produced
the "N sessions exist" claims that later turned out to be file-presence counts.

This module therefore refuses to emit a boolean. It emits THREE levels and makes the caller choose:

    EMPTY    zero records - the file exists only because something requested the symbol
    SPARSE   has records but below `sparse_max_bytes` - present, not a usable session
    PAYLOAD  above that threshold

`sparse_max_bytes` is a REPORTED PARAMETER with a default, never a hidden constant. Every artifact
this module writes records the value that produced it.

WHAT IT DOES NOT DO
-------------------
It does not decode prices. It reads file names, file sizes and mtimes only. It never opens an .ncd
for content. It is therefore safe to run while NinjaTrader holds the store open, and it cannot
consume a data seal: knowing that a file exists is not reading the market data inside it.

Usage:
    python -m research_sdk.data_census --selftest
    python -m research_sdk.data_census --out research/data/NT8_CAPABILITY_CENSUS.csv
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone

# --------------------------------------------------------------------------------------------
# Store location
# --------------------------------------------------------------------------------------------

DEFAULT_DB = os.path.join(os.path.expanduser("~"), "Documents", "NinjaTrader 8", "db")

# Every bar-storage kind NT8 uses. `replay` is included because it exists and has been miscounted
# before; it is enumerated and classified, never silently skipped.
KINDS = ("day", "minute", "tick", "replay")

# --------------------------------------------------------------------------------------------
# File-name grammar
#
# Three observed forms, ALL of which are matched. The historical bug was a scanner that knew only
# the first form and therefore reported ZERO daily files.
#     20260608.Last.ncd        date-chunked      (minute, day-in-some-stores)
#     202606080100.Last.ncd    date+hour-chunked (tick)
#     2026.Last.ncd            YEAR-chunked      (day)
# --------------------------------------------------------------------------------------------

_FILE = re.compile(
    r"^(?:(?P<date>\d{8})(?P<hour>\d{4})?|(?P<year>\d{4}))\.(?P<series>Last|Bid|Ask)\.ncd$",
    re.IGNORECASE,
)

# --------------------------------------------------------------------------------------------
# Instrument-name grammar
#
# NOTE THE ORDER AND THE FALLBACK. Nothing is ever dropped. An instrument name this module cannot
# parse is emitted with semantic_class="UNKNOWN" and root=the raw name, so it shows up in the
# artifact and can be argued about, rather than vanishing.
# --------------------------------------------------------------------------------------------

_FUT_CONTRACT = re.compile(r"^(?P<root>[A-Za-z0-9]{1,6})\s+(?P<mm>\d{2})-(?P<yy>\d{2})$")
_FUT_PLACEHOLDER = re.compile(r"^(?P<root>[A-Za-z0-9]{1,6})\s+##-##$")
_CASH_INDEX = re.compile(r"^\^(?P<root>[A-Za-z0-9._]+)$")
_FX_PAIR = re.compile(r"^(?P<root>[A-Z]{6})$")
_BARE = re.compile(r"^(?P<root>[A-Za-z0-9._]{1,6})$")

# Roots we know to be futures, used only to disambiguate a BARE name (e.g. "NQ" is a futures root,
# "MSFT" is an equity). Being absent from this set is not a judgement - it produces
# EQUITY_OR_UNKNOWN, which is an honest label, not an exclusion.
_KNOWN_FUTURES_ROOTS = {
    "NQ", "MNQ", "ES", "MES", "RTY", "M2K", "YM", "MYM", "CL", "MCL", "GC", "MGC", "SI", "SIL",
    "ZB", "ZN", "ZF", "ZT", "UB", "10YR", "2YR", "5YR", "30YR", "6A", "6B", "6C", "6E", "6J",
    "6M", "6N", "6S", "HG", "NG", "PL", "PA", "ZC", "ZS", "ZW", "ZL", "ZM", "HE", "LE", "VX",
    "VXM", "BTC", "MBT", "ETH", "MET",
}

MICRO_OF = {
    "NQ": "MNQ", "ES": "MES", "RTY": "M2K", "YM": "MYM", "CL": "MCL", "GC": "MGC",
    "SI": "SIL", "BTC": "MBT", "ETH": "MET", "VX": "VXM",
}
_MICROS = set(MICRO_OF.values())


def classify_instrument(name: str) -> tuple[str, str, str | None]:
    """-> (semantic_class, root, contract). NEVER raises, NEVER returns None for the class."""
    m = _FUT_CONTRACT.match(name)
    if m:
        root = m.group("root").upper()
        cls = "FUTURES_MICRO_CONTRACT" if root in _MICROS else "FUTURES_CONTRACT"
        return cls, root, f"{m.group('mm')}-{m.group('yy')}"
    m = _FUT_PLACEHOLDER.match(name)
    if m:
        return "FUTURES_PLACEHOLDER", m.group("root").upper(), "##-##"
    m = _CASH_INDEX.match(name)
    if m:
        return "CASH_INDEX", "^" + m.group("root").upper(), None
    m = _FX_PAIR.match(name)
    if m:
        return "FX_PAIR", m.group("root").upper(), None
    m = _BARE.match(name)
    if m:
        root = m.group("root").upper()
        if root in _KNOWN_FUTURES_ROOTS:
            return "FUTURES_ROOT", root, None
        return "EQUITY_OR_UNKNOWN", root, None
    # Anything at all - including a directory whose name is prose, which HAS occurred in this store.
    return "UNKNOWN", name, None


# --------------------------------------------------------------------------------------------
# Payload classification
# --------------------------------------------------------------------------------------------

# Measured, per (kind, series): the byte size of a file containing ZERO records.
# tick files bottom out at 31 = the bare header. minute files at 32 = header + a 1-byte terminator.
# day files were never observed empty (minimum 76 = header 28 + one 48-byte record).
EMPTY_SIGNATURE = {
    ("tick", "Last"): 31, ("tick", "Bid"): 31, ("tick", "Ask"): 31,
    ("minute", "Last"): 32, ("minute", "Bid"): 32, ("minute", "Ask"): 32,
    ("replay", "Last"): 31, ("replay", "Bid"): 31, ("replay", "Ask"): 31,
    ("day", "Last"): 28, ("day", "Bid"): 28, ("day", "Ask"): 28,
}

DEFAULT_SPARSE_MAX_BYTES = 200


def classify_payload(kind: str, series: str, nbytes: int, sparse_max_bytes: int) -> str:
    sig = EMPTY_SIGNATURE.get((kind, series), 32)
    if nbytes <= sig:
        return "EMPTY"
    if nbytes <= sparse_max_bytes:
        return "SPARSE"
    return "PAYLOAD"


# --------------------------------------------------------------------------------------------
# The scan
# --------------------------------------------------------------------------------------------

FIELDS = ["kind", "instrument", "semantic_class", "root", "contract", "series",
          "date", "hour", "year", "bytes", "mtime_utc", "payload_class"]


def scan(db: str = DEFAULT_DB, kinds=KINDS, sparse_max_bytes: int = DEFAULT_SPARSE_MAX_BYTES):
    """Yield one dict per .ncd file. No filtering of any kind occurs in this function."""
    for kind in kinds:
        root_dir = os.path.join(db, kind)
        if not os.path.isdir(root_dir):
            continue
        try:
            inst_entries = list(os.scandir(root_dir))
        except OSError:
            continue
        for ie in inst_entries:
            if not ie.is_dir():
                continue
            cls, root, contract = classify_instrument(ie.name)
            try:
                file_entries = list(os.scandir(ie.path))
            except OSError:
                continue
            for fe in file_entries:
                if not fe.is_file():
                    continue
                m = _FILE.match(fe.name)
                if m is None:
                    # Not silently dropped: reported with series=UNPARSED so it is visible.
                    try:
                        st = fe.stat()
                    except OSError:
                        continue
                    yield dict(kind=kind, instrument=ie.name, semantic_class=cls, root=root,
                               contract=contract or "", series="UNPARSED", date="", hour="",
                               year="", bytes=st.st_size,
                               mtime_utc=datetime.fromtimestamp(st.st_mtime, timezone.utc)
                               .isoformat(timespec="seconds"),
                               payload_class="UNPARSED")
                    continue
                try:
                    st = fe.stat()
                except OSError:
                    continue
                series = m.group("series").capitalize()
                yield dict(
                    kind=kind, instrument=ie.name, semantic_class=cls, root=root,
                    contract=contract or "", series=series,
                    date=m.group("date") or "", hour=m.group("hour") or "",
                    year=m.group("year") or "", bytes=st.st_size,
                    mtime_utc=datetime.fromtimestamp(st.st_mtime, timezone.utc)
                    .isoformat(timespec="seconds"),
                    payload_class=classify_payload(kind, series, st.st_size, sparse_max_bytes),
                )


def write_csv(rows, path: str) -> int:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    n = 0
    tmp = path + ".tmp"
    with open(tmp, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow(r)
            n += 1
    if n == 0:
        os.remove(tmp)
        raise RuntimeError("census produced zero rows - refusing to write an empty artifact")
    os.replace(tmp, path)
    return n


def summarise(rows):
    """(root, kind, series) -> payload/sparse/empty counts and date span. Selection-free."""
    agg = defaultdict(lambda: dict(payload=0, sparse=0, empty=0, unparsed=0,
                                   first="", last="", bytes=0, contracts=set()))
    for r in rows:
        k = (r["root"], r["semantic_class"], r["kind"], r["series"])
        a = agg[k]
        pc = r["payload_class"]
        a["payload" if pc == "PAYLOAD" else
          "sparse" if pc == "SPARSE" else
          "empty" if pc == "EMPTY" else "unparsed"] += 1
        a["bytes"] += r["bytes"]
        if r["contract"]:
            a["contracts"].add(r["contract"])
        d = r["date"] or r["year"]
        if d:
            if not a["first"] or d < a["first"]:
                a["first"] = d
            if not a["last"] or d > a["last"]:
                a["last"] = d
    return agg


# --------------------------------------------------------------------------------------------
# Self-test - the regression net for exactly the five failures this module exists to prevent
# --------------------------------------------------------------------------------------------

def selftest(db: str = DEFAULT_DB) -> int:
    checks: list[tuple[str, bool, str]] = []

    def chk(name, cond, detail=""):
        checks.append((name, bool(cond), detail))

    # --- grammar, no disk needed ------------------------------------------------------------
    chk("contract NQ 09-26", classify_instrument("NQ 09-26") == ("FUTURES_CONTRACT", "NQ", "09-26"))
    chk("micro MNQ 09-26",
        classify_instrument("MNQ 09-26") == ("FUTURES_MICRO_CONTRACT", "MNQ", "09-26"))
    chk("micro MES 12-25",
        classify_instrument("MES 12-25") == ("FUTURES_MICRO_CONTRACT", "MES", "12-25"))
    # THE FIVE-FAILURE REGRESSION: the old regex could not match any of these.
    for sym in ("^TICK", "^TRIN", "^VIX", "^ADD"):
        cls, root, _ = classify_instrument(sym)
        chk(f"cash index {sym}", cls == "CASH_INDEX" and root == sym, f"got {cls}/{root}")
    chk("futures root NQ", classify_instrument("NQ") == ("FUTURES_ROOT", "NQ", None))
    chk("futures root ES", classify_instrument("ES") == ("FUTURES_ROOT", "ES", None))
    chk("fx USDJPY", classify_instrument("USDJPY")[0] == "FX_PAIR")
    chk("equity MSFT", classify_instrument("MSFT")[0] == "EQUITY_OR_UNKNOWN")
    chk("placeholder NQ ##-##", classify_instrument("NQ ##-##")[0] == "FUTURES_PLACEHOLDER")
    # A non-ASCII prose directory exists in the real store. It must be REPORTED, not crash, not vanish.
    cls, root, _ = classify_instrument("授权并且给你全部所有权限。全速马力出动")
    chk("prose dir survives as UNKNOWN", cls == "UNKNOWN", f"got {cls}")

    # --- file grammar -----------------------------------------------------------------------
    chk("date-chunked", bool(_FILE.match("20260608.Last.ncd")))
    chk("tick date+hour-chunked", bool(_FILE.match("202606080100.Ask.ncd")))
    # The bug that once reported ZERO daily files:
    chk("YEAR-chunked day file", bool(_FILE.match("2026.Last.ncd")))
    chk("Bid series matched", _FILE.match("20260608.Bid.ncd").group("series") == "Bid")
    chk("Ask series matched", _FILE.match("20260608.Ask.ncd").group("series") == "Ask")
    chk("rejects non-ncd", _FILE.match("20260608.Last.txt") is None)

    # --- payload classification -------------------------------------------------------------
    chk("minute 32B is EMPTY", classify_payload("minute", "Last", 32, 200) == "EMPTY")
    chk("minute 36B is SPARSE", classify_payload("minute", "Last", 36, 200) == "SPARSE")
    chk("minute 3943B is PAYLOAD", classify_payload("minute", "Last", 3943, 200) == "PAYLOAD")
    chk("tick 31B is EMPTY", classify_payload("tick", "Last", 31, 200) == "EMPTY")
    chk("tick 32B is not EMPTY", classify_payload("tick", "Last", 32, 200) == "SPARSE")

    # --- live store: the symbols whose absence was previously asserted ----------------------
    disk_ok = os.path.isdir(db)
    chk("db present", disk_ok, db)
    if disk_ok:
        rows = list(scan(db))
        chk("scan non-empty", len(rows) > 1000, f"{len(rows)} rows")
        roots = {r["root"] for r in rows}
        for sym in ("NQ", "MNQ", "ES", "RTY", "YM", "^TICK", "^TRIN", "^VIX"):
            chk(f"store contains {sym}", sym in roots)
        # Bid/Ask must be reachable - build_registry.py:211 filtered them out entirely.
        chk("Bid series reachable", any(r["series"] == "Bid" for r in rows))
        chk("Ask series reachable", any(r["series"] == "Ask" for r in rows))
        # Day files must be found - the YCD bug once reported zero.
        chk("day kind reachable", any(r["kind"] == "day" for r in rows))

    width = max(len(c[0]) for c in checks)
    npass = 0
    for name, ok, detail in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name:<{width}}  {detail}")
        npass += ok
    print(f"\nselftest {npass}/{len(checks)}")
    return 0 if npass == len(checks) else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--out", default=None, help="write the full per-file census CSV here")
    ap.add_argument("--sparse-max-bytes", type=int, default=DEFAULT_SPARSE_MAX_BYTES)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--summary", action="store_true")
    a = ap.parse_args(argv)

    if a.selftest:
        return selftest(a.db)

    rows = list(scan(a.db, sparse_max_bytes=a.sparse_max_bytes))
    print(f"scanned {len(rows)} files under {a.db}  (sparse_max_bytes={a.sparse_max_bytes})")

    if a.out:
        n = write_csv(rows, a.out)
        print(f"wrote {n} rows -> {a.out}")

    if a.summary or not a.out:
        agg = summarise(rows)
        print(f"\n{'root':<10} {'class':<24} {'kind':<7} {'ser':<5} "
              f"{'payload':>8} {'sparse':>7} {'empty':>7} {'first':>9} {'last':>9} {'#ctr':>5}")
        for k in sorted(agg, key=lambda x: (-agg[x]["payload"], x)):
            root, cls, kind, ser = k
            v = agg[k]
            if v["payload"] == 0 and v["sparse"] == 0:
                continue
            print(f"{root:<10} {cls:<24} {kind:<7} {ser:<5} "
                  f"{v['payload']:8d} {v['sparse']:7d} {v['empty']:7d} "
                  f"{v['first']:>9} {v['last']:>9} {len(v['contracts']):5d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
