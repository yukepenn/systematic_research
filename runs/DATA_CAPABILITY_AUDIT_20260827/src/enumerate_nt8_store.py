"""DATA_CAPABILITY_AUDIT - enumerate the LOCAL NinjaTrader 8 historical data store.

RUN CLASS: AUDIT. Reads FILENAMES AND SIZES ONLY. It does not decode a single price.

Why that matters: the >= 2026-08-01 forward pool is SEALED (VIRGIN). Enumerating file names
tells us WHICH SESSIONS EXIST without reading any outcome, so the seal is untouched by this
audit. Every date >= 2026-08-01 is tagged SEALED in the output and is excluded from the
"usable now" totals, so no downstream job can pick it up by accident.

NT8 db layout, verified empirically on this machine:
    db/day/<INSTRUMENT>/<YYYYMMDD>.<Last|Bid|Ask>.ncd
    db/minute/<INSTRUMENT>/<YYYYMMDD>.<Last|Bid|Ask>.ncd
    db/tick/<INSTRUMENT>/<YYYYMMDDHH00>.<Last|Bid|Ask>.ncd     <- hourly chunks
    db/replay/<INSTRUMENT>/<YYYYMMDD>.nrd                       <- Market Replay
"""
from __future__ import annotations

import os
import re
import sys
from collections import defaultdict

import pandas as pd

DB = os.path.join(os.path.expanduser("~"), "Documents", "NinjaTrader 8", "db")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")
os.makedirs(OUT, exist_ok=True)

SEAL = "2026-08-01"          # >= this is VIRGIN. Never counted as usable.
NCD = re.compile(r"^(\d{8})(\d{4})?\.(Last|Bid|Ask)\.ncd$", re.I)
# db/day chunks by YEAR, not by date: "2026.Last.ncd". Verified empirically -- an earlier
# version of this scan used only the 8-digit form and silently reported ZERO daily files.
YCD = re.compile(r"^(\d{4})\.(Last|Bid|Ask)\.ncd$", re.I)
ROOT_OF = re.compile(r"^([A-Z0-9]{1,4})\s+(\d{2})-(\d{2})$")


def scan(kind: str):
    """Return per-(instrument, series) date sets for db/<kind>."""
    base = os.path.join(DB, kind)
    if not os.path.isdir(base):
        return {}, {}
    dates, nbytes = defaultdict(set), defaultdict(int)
    for inst in sorted(os.listdir(base)):
        d = os.path.join(base, inst)
        if not os.path.isdir(d):
            continue
        with os.scandir(d) as it:
            for e in it:
                m = NCD.match(e.name)
                if m:
                    ymd, _hh, series = m.groups()
                else:
                    m = YCD.match(e.name)
                    if not m:
                        continue
                    ymd, series = m.group(1) + "0000", m.group(2)   # year-chunked
                key = (inst, series.capitalize())
                dates[key].add(ymd)
                try:
                    nbytes[key] += e.stat().st_size
                except OSError:
                    pass
    return dates, nbytes


def main():
    rows = []
    keep = {}                      # (kind, root, series) -> set of ISO dates, deduped
    for kind in ("day", "minute", "tick"):
        dates, nbytes = scan(kind)
        for (inst, series), ds in dates.items():
            m = ROOT_OF.match(inst)
            k = (kind, m.group(1) if m else inst, series.capitalize())
            yearly = sorted(ds)[0].endswith("0000")
            keep.setdefault(k, set()).update(
                (f"{d[:4]}-01-01" if yearly else f"{d[:4]}-{d[4:6]}-{d[6:8]}") for d in ds)
        for (inst, series), ds in dates.items():
            ds = sorted(ds)
            # year-chunked (day) entries carry the sentinel MMDD=0000
            yearly = ds[0].endswith("0000")
            iso = [(f"{d[:4]}-01-01" if yearly else f"{d[:4]}-{d[4:6]}-{d[6:8]}") for d in ds]
            usable = [x for x in iso if x < SEAL]
            sealed = [x for x in iso if x >= SEAL]
            m = ROOT_OF.match(inst)
            rows.append(dict(
                kind=kind, instrument=inst, root=m.group(1) if m else inst,
                series=series, granularity="year" if yearly else "date",
                n_dates=len(iso), first=iso[0], last=iso[-1],
                n_usable=len(usable), usable_last=usable[-1] if usable else "",
                n_sealed=len(sealed), mb=round(nbytes[(inst, series)] / 1e6, 2)))

    # Market Replay
    rep = os.path.join(DB, "replay")
    if os.path.isdir(rep):
        for inst in sorted(os.listdir(rep)):
            d = os.path.join(rep, inst)
            if not os.path.isdir(d):
                continue
            ds = sorted(f[:8] for f in os.listdir(d) if f.lower().endswith(".nrd"))
            if not ds:
                continue
            iso = [f"{x[:4]}-{x[4:6]}-{x[6:8]}" for x in ds]
            usable = [x for x in iso if x < SEAL]
            mb = sum(os.path.getsize(os.path.join(d, f)) for f in os.listdir(d)
                     if f.lower().endswith(".nrd")) / 1e6
            m = ROOT_OF.match(inst)
            rows.append(dict(
                kind="replay", instrument=inst, root=m.group(1) if m else inst,
                series="Replay", granularity="date",
                n_dates=len(iso), first=iso[0], last=iso[-1],
                n_usable=len(usable), usable_last=usable[-1] if usable else "",
                n_sealed=len(iso) - len(usable), mb=round(mb, 2)))

    M = pd.DataFrame(rows).sort_values(["kind", "root", "instrument", "series"])
    M.to_csv(os.path.join(OUT, "instrument_matrix.csv"), index=False)

    # ---------------------------------------------------------------- retention by root
    ret = []
    for (kind, root, series), g in M.groupby(["kind", "root", "series"]):
        # DISTINCT session dates across all contract vintages of this root. Overlapping
        # contracts double-count in the gross figure; only this deduped number bears on power.
        alld = sorted(keep.get((kind, root, series), set()))
        usable = [d for d in alld if d < SEAL]
        ret.append(dict(kind=kind, root=root, series=series,
                        n_contracts=g["instrument"].nunique(),
                        first=g["first"].min(), last=g["last"].max(),
                        inst_dates_gross=int(g["n_dates"].sum()),
                        distinct_dates=len(alld), distinct_usable=len(usable),
                        usable_first=usable[0] if usable else "",
                        usable_last=usable[-1] if usable else "",
                        sealed=len(alld) - len(usable), mb=round(g["mb"].sum(), 1)))
    R = pd.DataFrame(ret).sort_values(["kind", "series", "distinct_usable"],
                                      ascending=[True, True, False])
    R.to_csv(os.path.join(OUT, "retention_matrix.csv"), index=False)

    P = lambda *a: print(*a, flush=True)
    P("=" * 110)
    P("=== NT8 LOCAL STORE - filenames and sizes only. No price was decoded. Seal untouched.")
    P("=" * 110)
    for kind in ("day", "minute", "tick", "replay"):
        s = M[M["kind"] == kind]
        if s.empty:
            continue
        P(f"\n--- db/{kind}:  {s['instrument'].nunique()} instruments, "
          f"{s['root'].nunique()} roots, {s['mb'].sum()/1000:.2f} GB")
        for series in ("Last", "Bid", "Ask", "Replay"):
            t = s[s["series"] == series]
            if not t.empty:
                P(f"      {series:<7} {t['instrument'].nunique():>4} instruments  "
                  f"{int(t['n_dates'].sum()):>7,} inst-dates  "
                  f"{t['first'].min()} -> {t['last'].max()}  {t['mb'].sum()/1000:>7.2f} GB")
    P("")
    P("=" * 110)
    P("=== DISTINCT USABLE SESSION DATES (< 2026-08-01), deduped across contract vintages.")
    P("=== This is the ONLY count that bears on power. Instrument-dates double-count overlaps.")
    P("=" * 110)
    for kind in ("tick", "minute", "replay"):
        t = R[(R["kind"] == kind)].sort_values("distinct_usable", ascending=False)
        if t.empty:
            continue
        P(f"\n--- db/{kind}")
        for _, r in t.iterrows():
            if r["distinct_usable"] == 0 and r["sealed"] == 0:
                continue
            P(f"    {r['root']:<6} {r['series']:<6} {r['distinct_usable']:>6,} usable  "
              f"({r['usable_first']} -> {r['usable_last']})  "
              f"+{r['sealed']:>3} sealed  {r['n_contracts']:>3} contracts  {r['mb']:>8.1f} MB")

    P("")
    P("--- db/day  (year-chunked; per-date counts are not visible from filenames)")
    d = R[R["kind"] == "day"]
    P(f"    {d['root'].nunique()} roots, {int(d['n_contracts'].sum())} contract folders, "
      f"earliest year {d['first'].min()[:4]}, latest {d['last'].max()[:4]}")
    print(f"\nwrote {OUT}\\instrument_matrix.csv  and  retention_matrix.csv")


if __name__ == "__main__":
    sys.exit(main())
