"""How many NQ sessions are ACTUALLY extractable, and how many does the substrate already have?

The headline "310 NQ tick sessions" is Last-only. The scalping_lab substrate schema is
bip = 0/1/2 = Last/Bid/Ask, and every BBO feature family (microprice, spread, quote imbalance)
needs all three. So the number that governs the BBO lane is the count of dates carrying
Last AND Bid AND Ask -- not the Last count. Those are different numbers here and conflating
them would overstate the lane by ~2x.

Filenames and sizes only. No price decoded. Seal (>= 2026-08-01) excluded from every total.
"""
from __future__ import annotations

import os
import re
from collections import defaultdict

import pandas as pd

DB = os.path.join(os.path.expanduser("~"), "Documents", "NinjaTrader 8", "db", "tick")
SUB = (r"D:\OneDrive - Washington University in St. Louis\TradingResearch"
       r"\systematic_research\research\scalping_lab\substrate")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")
SEAL = "2026-08-01"
NCD = re.compile(r"^(\d{8})\d{4}\.(Last|Bid|Ask)\.ncd$", re.I)


def store(root: str):
    have = defaultdict(set)          # iso date -> {series}
    mb = defaultdict(float)
    for inst in sorted(os.listdir(DB)):
        if not inst.startswith(root + " "):
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
                have[iso].add(series)
                try:
                    mb[iso] += e.stat().st_size / 1e6
                except OSError:
                    pass
    return have, mb


def main():
    P = print
    rows = []
    for root in ("NQ", "ES", "MNQ"):
        have, mb = store(root)
        for iso in sorted(have):
            s = have[iso]
            rows.append(dict(root=root, date=iso, sealed=iso >= SEAL,
                             has_last="Last" in s, has_bid="Bid" in s, has_ask="Ask" in s,
                             bbo_complete={"Last", "Bid", "Ask"} <= s, mb=round(mb[iso], 1)))
    D = pd.DataFrame(rows)
    D.to_csv(os.path.join(OUT, "tick_session_availability.csv"), index=False)

    # what the research substrate already holds
    raw = os.path.join(SUB, "raw", "NQ")
    done = set()
    if os.path.isdir(raw):
        for f in os.listdir(raw):
            m = re.match(r"^s(\d{8})", f)
            if m:
                g = m.group(1)
                done.add(f"{g[:4]}-{g[4:6]}-{g[6:8]}")

    P("=" * 104)
    P("=== EXTRACTABLE NQ/ES TICK SESSIONS  (local NT8 store, filenames only, seal excluded)")
    P("=" * 104)
    for root in ("NQ", "ES", "MNQ"):
        g = D[(D["root"] == root) & (~D["sealed"])]
        if g.empty:
            continue
        P(f"\n--- {root}   {g['date'].min()} -> {g['date'].max()}   {g['mb'].sum()/1000:.2f} GB")
        P(f"    Last present                {int(g['has_last'].sum()):>5}")
        P(f"    Bid  present                {int(g['has_bid'].sum()):>5}")
        P(f"    Ask  present                {int(g['has_ask'].sum()):>5}")
        P(f"    BBO-COMPLETE (Last+Bid+Ask) {int(g['bbo_complete'].sum()):>5}   <- governs every "
          f"quote-based feature")
        P(f"    Last-ONLY (no quotes)       {int((g['has_last'] & ~g['bbo_complete']).sum()):>5}   "
          f"<- still fine for tick-rule signed flow")

    g = D[(D["root"] == "NQ") & (~D["sealed"])]
    tot_last = int(g["has_last"].sum())
    tot_bbo = int(g["bbo_complete"].sum())
    have_bbo = sorted(set(g[g["bbo_complete"]]["date"]) & done)
    new_bbo = sorted(set(g[g["bbo_complete"]]["date"]) - done)
    new_last = sorted(set(g[g["has_last"]]["date"]) - done)

    P("")
    P("=" * 104)
    P("=== AGAINST THE EXISTING 48-SESSION SUBSTRATE")
    P("=" * 104)
    P(f"    substrate raw/NQ session files                 {len(done):>5}")
    P(f"    ... of which BBO-complete in the store         {len(have_bbo):>5}")
    P("")
    P(f"    NQ dates with Last, NOT yet extracted          {len(new_last):>5}   "
      f"-> signed-flow lane would go {len(done)} -> {tot_last}")
    P(f"    NQ dates BBO-complete, NOT yet extracted       {len(new_bbo):>5}   "
      f"-> BBO lane would go {len(have_bbo)} -> {tot_bbo}")
    P("")
    P("    POWER TARGET on record (DATAGATE_ORDERFLOW_20260827): ~300+ overlapping sessions.")
    P(f"      signed-flow (Last only) : {tot_last:>5}  ->  {'MEETS' if tot_last >= 300 else 'SHORT OF'} the target")
    P(f"      BBO / quote features    : {tot_bbo:>5}  ->  {'MEETS' if tot_bbo >= 300 else 'SHORT OF'} the target")

    pd.DataFrame(dict(date=new_bbo)).to_csv(
        os.path.join(OUT, "extractable_bbo_sessions.csv"), index=False)
    pd.DataFrame(dict(date=new_last)).to_csv(
        os.path.join(OUT, "extractable_last_sessions.csv"), index=False)
    P(f"\nwrote tick_session_availability.csv, extractable_bbo_sessions.csv, "
      f"extractable_last_sessions.csv")


if __name__ == "__main__":
    main()
