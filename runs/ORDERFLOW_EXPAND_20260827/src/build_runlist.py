"""Build the extraction runlist: one row per NQ session date that is NOT yet in the substrate.

For each date we must pick the RIGHT CONTRACT. Several contract folders can carry the same date
(the front month and the next one both trade during a roll), so we pick the contract holding the
MOST BYTES for that date -- that is the liquid front month, and it is the series the existing
substrate used.

Session convention, read off the existing MANIFEST rather than assumed:
    sYYYYMMDD  spans  D-1 18:00:00 ET  ->  D 16:59:59 ET
e.g. s20250811 = 2025-08-10 18:00:00.064 -> 2025-08-11 16:59:59.548.

Emits runlist.csv with BOTH the ET window and its UTC translation, because RunStrategyBacktest
documents from/to as ISO-8601 UTC while NT8 payload timestamps are exchange-session ET.
The UTC translation is VERIFIED against a real export before the batch is trusted -- see PILOT.
"""
from __future__ import annotations

import os
import re
from collections import defaultdict
from zoneinfo import ZoneInfo

import pandas as pd

DB = os.path.join(os.path.expanduser("~"), "Documents", "NinjaTrader 8", "db", "tick")
ROOT = (r"D:\OneDrive - Washington University in St. Louis\TradingResearch"
        r"\systematic_research")
SUB = os.path.join(ROOT, "research", "scalping_lab", "substrate", "raw", "NQ")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")
os.makedirs(OUT, exist_ok=True)

SEAL = "2026-08-01"
ET, UTC = ZoneInfo("America/New_York"), ZoneInfo("UTC")
NCD = re.compile(r"^(\d{8})\d{4}\.(Last|Bid|Ask)\.ncd$", re.I)


def load_hourly_truth():
    """CORRECTED classification. Date-level file presence overstated BBO coverage by 52 sessions;
    see src/bbo_hourly_truth.py. Quote completeness is an HOUR-level fact because an NQ session
    spans two calendar dates of .ncd files."""
    f = os.path.join(OUT, "bbo_hourly_truth.csv")
    T = pd.read_csv(f)
    return ({r["date"]: r["cls"] for _, r in T.iterrows()},
            {r["date"]: r["last_frac"] for _, r in T.iterrows()},
            {r["date"]: r["quote_frac"] for _, r in T.iterrows()})


CLS, LASTF, QF = load_hourly_truth()


def main():
    # date -> contract -> {series}, and date -> contract -> bytes
    per = defaultdict(lambda: defaultdict(set))
    size = defaultdict(lambda: defaultdict(float))
    for inst in sorted(os.listdir(DB)):
        if not inst.startswith("NQ "):
            continue
        d = os.path.join(DB, inst)
        if not os.path.isdir(d):
            continue
        with os.scandir(d) as it:
            for e in it:
                m = NCD.match(e.name)
                if not m:
                    continue
                ymd, series = m.group(1), m.group(2).capitalize()
                iso = f"{ymd[:4]}-{ymd[4:6]}-{ymd[6:8]}"
                per[iso][inst].add(series)
                try:
                    size[iso][inst] += e.stat().st_size
                except OSError:
                    pass

    done = set()
    if os.path.isdir(SUB):
        for f in os.listdir(SUB):
            m = re.match(r"^s(\d{8})", f)
            if m:
                g = m.group(1)
                done.add(f"{g[:4]}-{g[4:6]}-{g[6:8]}")

    rows = []
    for iso in sorted(per):
        if iso >= SEAL:                       # VIRGIN. never queued.
            continue
        if iso in done:                       # already in the substrate
            continue
        # front month = the contract with the most bytes on this date
        inst = max(size[iso], key=lambda k: size[iso][k])
        s = per[iso][inst]
        if "Last" not in s:
            continue
        if iso not in CLS:                     # no hourly verdict -> not queued
            continue
        d = pd.Timestamp(iso)
        # PILOT-CORRECTED WINDOW. NT8's Strategy Analyzer treats `from` as a DATE and loads the
        # SESSION DATED that day, which already begins at D-1 18:00 ET. Passing D-1 therefore
        # loads TWO sessions -- verified: from=2025-08-12 produced t_min 2025-08-11 18:00 and a
        # 2-session file. `from` must be midday on D itself, so only session D is loaded.
        f_et = pd.Timestamp(f"{d.date()} 12:00:00", tz=ET)
        t_et = pd.Timestamp(f"{d.date()} 16:59:59", tz=ET)
        rows.append(dict(
            session="s" + iso.replace("-", ""), date=iso, instrument=inst,
            quote_cls=CLS[iso], quote_frac=QF[iso], last_frac=LASTF[iso],
            bbo_complete=CLS[iso] == "FULL",
            from_et=str(f_et)[:19], to_et=str(t_et)[:19],
            from_utc=f_et.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            to_utc=t_et.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            store_mb=round(size[iso][inst] / 1e6, 1)))

    R = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    R.to_csv(os.path.join(OUT, "runlist.csv"), index=False)

    P = print
    R["priority"] = R["quote_cls"].map({"FULL": 1, "PARTIAL": 2, "NONE": 3}).fillna(3)
    R = R.sort_values(["priority", "date"]).reset_index(drop=True)
    P(f"    runlist rows                    {len(R):>5}")
    P(f"    ... quotes FULL   (BBO lane)    {int((R['quote_cls'] == 'FULL').sum()):>5}")
    P(f"    ... quotes PARTIAL              {int((R['quote_cls'] == 'PARTIAL').sum()):>5}")
    P(f"    ... quotes NONE   (flow lane)   {int((R['quote_cls'] == 'NONE').sum()):>5}")
    P(f"    ... Last >= 0.90                {int((R['last_frac'] >= 0.90).sum()):>5}")
    P(f"    date span                       {R['date'].min()} -> {R['date'].max()}")
    P(f"    contracts involved              {sorted(R['instrument'].unique())}")
    P(f"    store bytes implicated          {R['store_mb'].sum()/1000:.2f} GB")
    P("")
    P("    first 5:")
    P(R[["session", "instrument", "bbo_complete", "from_utc", "to_utc", "store_mb"]]
      .head(5).to_string(index=False))
    P(f"\n    wrote {OUT}\\runlist.csv")


if __name__ == "__main__":
    main()
