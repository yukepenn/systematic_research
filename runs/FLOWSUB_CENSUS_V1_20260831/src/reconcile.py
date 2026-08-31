"""FLOWSUB_CENSUS_V1 -- STEP 5.  Reconcile every competing count against ONE inventory.

DATA-ONLY.  File names + file sizes.  No .ncd payload byte is decoded here.

Counts in circulation, each from a different run, none of them wrong at its own object:
   319 / 196 / 123   B1 census, CALENDAR DATES from filename stems, no payload filter
   310 / 99 / 47 / 164   ORDERFLOW_EXPAND + BBO_RECENSUS, pre-seal DATE rows, 23-hour rule
   116 RTH-complete, 104 consumed, 19 blind      BBO_RECENSUS
   243 Last-usable ceiling, 102 materialized, 141 blind   DATA_ASSET_REGISTRY
   48                DATA_CENSUS_20260826, MATERIALIZED parquet in the OLD substrate
"""
from __future__ import annotations

import os
import re
from collections import defaultdict

import pandas as pd

DB = os.path.join(os.path.expanduser("~"), "Documents", "NinjaTrader 8", "db", "tick")
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(HERE, "out")
NCD = re.compile(r"^(\d{8})(\d{2})00\.(Last|Bid|Ask)\.ncd$", re.I)
EMPTY_MAX = 32
SEAL, BURN0 = "2026-08-01", "2026-05-31"
EVENING = [19, 20, 21, 22, 23]
DAYLAB = [0] + list(range(1, 18))
RTH = set(range(10, 17))
L = []


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    L.append(s)


def scan(payload_filter: bool):
    have = defaultdict(set)
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
                if payload_filter and e.stat().st_size <= EMPTY_MAX:
                    continue
                ymd, hh, s = m.group(1), int(m.group(2)), m.group(3).capitalize()
                have[(f"{ymd[:4]}-{ymd[4:6]}-{ymd[6:8]}", s)].add(hh)
    return have


def mats(p):
    out = set()
    if os.path.isdir(p):
        for f in os.listdir(p):
            m = re.match(r"^s(\d{8})\.parquet$", f)
            if m:
                g = m.group(1)
                out.add(f"{g[:4]}-{g[4:6]}-{g[6:]}")
    return out


def table(have):
    dates = sorted({d for d, _ in have})
    rows = []
    for iso in dates:
        prev = str((pd.Timestamp(iso) - pd.Timedelta(days=1)).date())
        rec = {"date": iso, "dow": pd.Timestamp(iso).day_name(),
               "sealed": iso >= SEAL, "burned": BURN0 <= iso < SEAL}
        for s in ("Last", "Bid", "Ask"):
            ev, dy = have.get((prev, s), set()), have.get((iso, s), set())
            rec[s + "_sess_h"] = (len([h for h in EVENING if h in ev])
                                  + len([h for h in DAYLAB if h in dy]))
            rec[s + "_frac"] = round(rec[s + "_sess_h"] / 23, 3)
            rec[s + "_day_labels"] = len(dy)
            rec[s + "_rth_ok"] = RTH <= dy
        rec["quote_frac"] = min(rec["Bid_frac"], rec["Ask_frac"])
        rec["old_class"] = ("NONE" if rec["quote_frac"] <= 0.05
                            else ("PARTIAL" if rec["quote_frac"] <= 0.90 else "FULL"))
        rec["rth_complete_LBA"] = rec["Last_rth_ok"] and rec["Bid_rth_ok"] and rec["Ask_rth_ok"]
        # date-level presence (B1's object)
        rec["has_last_file"] = (have.get((iso, "Last"), set()) != set())
        rec["has_bbo_file"] = (have.get((iso, "Bid"), set()) != set()
                               and have.get((iso, "Ask"), set()) != set())
        # session-level object
        rec["session_exists"] = rec["Last_sess_h"] > 0
        rec["last_usable"] = rec["Last_frac"] >= 0.90
        rec["bbo_any_sess"] = rec["quote_frac"] > 0
        rows.append(rec)
    return pd.DataFrame(rows)


def main():
    old_sub, v2_sub = (mats(os.path.join(ROOT, "research/scalping_lab/substrate/raw/NQ")),
                       mats(os.path.join(ROOT, "research/data_microstructure_v2/raw/NQ")))
    cons = old_sub | v2_sub

    for pf in (False, True):
        D = table(scan(pf))
        tag = "PAYLOAD>32B" if pf else "NAMES ONLY "
        P("=" * 100)
        P(f"=== RECONCILIATION  [{tag}]   NQ tick store, {len(D)} calendar dates with any file")
        P("=" * 100)
        nl, nb = int(D.has_last_file.sum()), int(D.has_bbo_file.sum())
        P(f"  B1 OBJECT (calendar dates)     Last {nl}   BBO {nb}   Last-only {nl - nb}"
          f"        [claim 319 / 196 / 123]")
        S = D[D.session_exists]
        P(f"  SESSION OBJECT (s(D)=D-1 18:00->D 17:00)   trade-bearing sessions {len(S)}")
        # where do the extra dates go?
        evening_only = D[~D.session_exists]
        P(f"  dates that are EVENING-ONLY (their data belongs to the NEXT session) "
          f"{len(evening_only)}")
        P(f"     day-of-week of those dates: {dict(evening_only.dow.value_counts())}")
        P(f"     => {nl} calendar dates  -  {len(evening_only)} evening-only  =  {len(S)} sessions")
        P("")
        pre = D[~D.sealed]
        P(f"  --- pre-seal date rows (BBO_RECENSUS object) n={len(pre)}   [claim 310]")
        vc = pre.old_class.value_counts()
        P(f"      old 23-hour class   FULL {int(vc.get('FULL',0))}  "
          f"PARTIAL {int(vc.get('PARTIAL',0))}  NONE {int(vc.get('NONE',0))}"
          f"        [claim 99 / 47 / 164]")
        P(f"      NEW rth_complete (Last&Bid&Ask, labels 10-16) "
          f"{int(pre.rth_complete_LBA.sum())}        [claim 116]")
        pre = pre.copy()
        pre["consumed"] = pre.date.isin(cons)
        P(f"      materialized OLD {int(pre.date.isin(old_sub).sum())}  "
          f"v2 {int(pre.date.isin(v2_sub).sum())}  EITHER {int(pre.consumed.sum())}"
          f"        [claim 48 / 58 / 104]")
        P(f"      rth_complete AND NOT materialized "
          f"{int((pre.rth_complete_LBA & ~pre.consumed).sum())}        [claim 19]")
        P(f"      old FULL AND NOT materialized "
          f"{int(((pre.old_class=='FULL') & ~pre.consumed).sum())}        [claim 1]")
        P("")
        P(f"  --- Last-usable ceiling (DATA_ASSET_REGISTRY object)")
        P(f"      pre-seal date rows with Last_frac>=0.90 {int((pre.Last_frac>=0.90).sum())}"
          f"        [claim 243]")
        P(f"      of those, materialized {int(((pre.Last_frac>=0.90) & pre.consumed).sum())}"
          f"        [claim 102]")
        P(f"      of those, NOT materialized "
          f"{int(((pre.Last_frac>=0.90) & ~pre.consumed).sum())}        [claim 141]")
        P("")
        if pf:
            D.to_csv(os.path.join(OUT, "reconcile_dates.csv"), index=False)
            # ---- the honest headroom table, session object, payload filtered
            P("=" * 100)
            P("=== HEADROOM, SESSION OBJECT, PAYLOAD FILTERED, ERA-SPLIT")
            P("=" * 100)
            S = D[D.session_exists].copy()
            S["consumed"] = S.date.isin(cons)
            S["era"] = ["SEALED" if r.sealed else ("BURNED" if r.burned else "PRE_BURN")
                        for r in S.itertuples()]
            g = S.groupby("era")
            P(f"  {'era':<9} {'sessions':>9} {'consumed':>9} {'free':>6} "
              f"{'free&BBO_RTH':>13} {'free&Lastonly>=0.90':>21}")
            for e in ("PRE_BURN", "BURNED", "SEALED"):
                if e not in g.groups:
                    continue
                E = g.get_group(e)
                free = E[~E.consumed]
                P(f"  {e:<9} {len(E):>9} {int(E.consumed.sum()):>9} {len(free):>6} "
                  f"{int(free.rth_complete_LBA.sum()):>13} "
                  f"{int(((~free.bbo_any_sess) & (free.Last_frac>=0.90)).sum()):>21}")
            P("")
    with open(os.path.join(OUT, "reconcile.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
