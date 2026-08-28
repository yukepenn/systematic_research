"""LANE A step 0 - CAN THE 141-SESSION BLIND POOL SUPPORT A STRICTLY CHRONOLOGICAL TEST?

Directive s5. "Blind outcome != automatically chronological OOS." The blind sessions overlap the
same calendar era as the consumed discovery sessions, so chronology has to be SOLVED, not assumed.

THIS SCRIPT READS METADATA ONLY - session dates, instruments, coverage fractions. It does NOT open
a single blind price file. Choosing a cutoff after seeing blind P&L would destroy the pool, so the
cutoff must be selected from sample size alone, by a rule fixed before the table is inspected.

    PREDECLARED SELECTION RULE, fixed here, before the table below is computed:
      * discovery arm    >= 60 sessions   (enough to fit a small causal model with >= 3
                                           chronological validation blocks of >= 20 sessions)
      * confirmation arm >= 60 sessions   (the SESSION is the dependence unit; 60 sessions gives
                                           MDE = 2.80/sqrt(60) = 0.36 sd on a per-session mean)
      * among cutoffs satisfying BOTH, take the one MAXIMISING min(discovery, confirmation),
        i.e. the most balanced adequately-powered split. Ties -> earliest cutoff.
      * P&L PLAYS NO PART. The rule is a function of COUNTS ONLY.
"""
from __future__ import annotations

import os
import re

import numpy as np
import pandas as pd

ROOT = (r"D:\OneDrive - Washington University in St. Louis\TradingResearch"
        r"\systematic_research")
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)
MIN_DISC, MIN_CONF = 60, 60          # PREDECLARED above, before any table was seen
_fh = open(os.path.join(OUT, "chronology.txt"), "w", encoding="utf-8")


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


def sess_dates(d):
    out = set()
    if not os.path.isdir(d):
        return out
    for f in os.listdir(d):
        m = re.match(r"^s(\d{8})", f)
        if m:
            out.add(pd.Timestamp(m.group(1)).normalize())
    return out


def main():
    blind = pd.read_csv(os.path.join(ROOT, "runs/MICRO_DISCOVERY_CONFIRMATION_SPLIT/out/"
                                           "MICRO_BLIND_CONFIRMATION_POOL.csv"))
    blind["date"] = pd.to_datetime(blind["date"])
    v1 = sess_dates(os.path.join(ROOT, "research/scalping_lab/substrate/raw/NQ"))
    v2 = sess_dates(os.path.join(ROOT, "research/data_microstructure_v2/raw/NQ"))
    consumed = sorted(v1 | v2)

    P("=" * 100)
    P("=== LANE A step 0 - CHRONOLOGY OF THE BLIND POOL.  METADATA ONLY, NO PRICE FILE OPENED.")
    P("=" * 100)
    P(f"    consumed (v1 {len(v1)} + v2 {len(v2)}, union)   {len(consumed):>4}   "
      f"{consumed[0].date()} -> {consumed[-1].date()}")
    P(f"    BLIND, never extracted                    {len(blind):>4}   "
      f"{blind['date'].min().date()} -> {blind['date'].max().date()}")
    P("")
    P("    >>> THE TWO POOLS OVERLAP IN CALENDAR TIME. Blindness and chronology are different")
    P("    >>> properties and only one of them is already established.")

    # ------------------------------------------------------------------ the cutoff table
    cands = pd.date_range("2025-09-01", "2026-06-01", freq="MS")
    cd = pd.Series(consumed)
    rows = []
    for t in cands:
        nd = int((cd < t).sum())
        nc = int((blind["date"] > t).sum())
        rows.append(dict(cutoff=t.date(), discovery_before=nd, blind_after=nc,
                         min_arm=min(nd, nc), adequate=(nd >= MIN_DISC and nc >= MIN_CONF)))
    tab = pd.DataFrame(rows)
    P("")
    P("=" * 100)
    P("=== STRICTLY CHRONOLOGICAL CANDIDATE CUTOFFS  (discovery < T  <  blind)")
    P("=" * 100)
    P(f"    {'cutoff':>12}{'discovery':>12}{'blind':>8}{'min arm':>10}   adequate "
      f"(>={MIN_DISC}/{MIN_CONF})")
    P("    " + "-" * 62)
    for r in rows:
        P(f"    {str(r['cutoff']):>12}{r['discovery_before']:>12}{r['blind_after']:>8}"
          f"{r['min_arm']:>10}   {'YES' if r['adequate'] else 'no'}")
    tab.to_csv(os.path.join(OUT, "cutoff_table.csv"), index=False)

    ok = tab[tab["adequate"]]
    P("")
    P("=" * 100)
    if len(ok):
        best = ok.sort_values(["min_arm", "cutoff"], ascending=[False, True]).iloc[0]
        P(f"=== STRICT CHRONOLOGY IS AVAILABLE.  cutoff {best['cutoff']}  "
          f"discovery {best['discovery_before']}  blind {best['blind_after']}")
        P("=== Selected by the predeclared max-min rule on COUNTS ALONE.")
    else:
        P("=== *** NO STRICTLY CHRONOLOGICAL SPLIT IS ADEQUATELY POWERED. ***")
        P("=" * 100)
        b = tab.sort_values("min_arm", ascending=False).iloc[0]
        P(f"    The best any cutoff achieves is min arm = {b['min_arm']} at {b['cutoff']} "
          f"(discovery {b['discovery_before']}, blind {b['blind_after']}).")
        P(f"    The rule required {MIN_DISC}/{MIN_CONF}. It is NOT relaxed to manufacture a pass.")
        P("")
        P("    WHY, structurally: the blind pool ENDS 2026-05-08 while the consumed pool runs to")
        P(f"    {consumed[-1].date()}. Pushing the cutoff later buys discovery sessions by")
        P("    destroying blind ones, and the blind pool is front-loaded in the SAME months the")
        P("    consumed pool covers. There is no cutoff where one cleanly precedes the other.")
        P("")
        P("    >>> THEREFORE THE POOL IS CLASSIFIED, HONESTLY AND PERMANENTLY, AS:")
        P("    >>>")
        P("    >>>     BLIND SAMPLE HOLDOUT   -   its price content has never been read")
        P("    >>>     NOT a strict time-forward holdout   -   it interleaves with discovery")
        P("    >>>")
        P("    >>> Chronology is NOT manufactured. A claim built on it may say 'never seen these")
        P("    >>> outcomes'. It may NOT say 'confirmed out-of-time', and it does NOT substitute")
        P("    >>> for prospective evidence.")

    # -------------------------------------------- what the interleaving actually looks like
    P("")
    P("=" * 100)
    P("=== MONTHLY INTERLEAVING - the reason chronology fails, shown rather than asserted")
    P("=" * 100)
    cm = cd.dt.to_period("M").value_counts().sort_index()
    bm = blind["date"].dt.to_period("M").value_counts().sort_index()
    months = sorted(set(cm.index) | set(bm.index))
    P(f"    {'month':>10}{'consumed':>11}{'blind':>8}   {'':<24}")
    P("    " + "-" * 56)
    for m in months:
        c, b = int(cm.get(m, 0)), int(bm.get(m, 0))
        bar = "#" * c + "." * b
        P(f"    {str(m):>10}{c:>11}{b:>8}   {bar:<24}")
    P("")
    P("    '#' consumed   '.' blind.  Both appear in nearly every month of the overlap.")

    pd.DataFrame(dict(session=[f"s{d:%Y%m%d}" for d in consumed],
                      date=[d.date() for d in consumed])).to_csv(
        os.path.join(OUT, "consumed_sessions.csv"), index=False)
    P("")
    P(f"    wrote out/cutoff_table.csv and out/consumed_sessions.csv ({len(consumed)} rows)")
    _fh.close()


if __name__ == "__main__":
    main()
