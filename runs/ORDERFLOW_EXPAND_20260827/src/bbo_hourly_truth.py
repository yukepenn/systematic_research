"""CORRECTION to the date-level BBO count. Quote completeness must be judged at HOUR granularity.

The audit's first pass asked "does date D have Bid and Ask .ncd files?" That overstates coverage,
and the overstatement is not small. Two extractions proved it:

  s20260319 -> quotes covered only 2026-03-19 00:00 -> 16:59 ET, with the 03-18 18:00 -> 23:59
               evening leg MISSING, even though date 2026-03-18 "has Bid/Ask files".
  s20260318 -> quotes covered only 2026-03-17 18:00 -> 23:59, with the whole 03-18 day leg missing.

Reason: an NQ session dated D runs D-1 18:00 -> D 17:00 ET, so it draws on TWO calendar dates of
.ncd files. Date 2026-03-18 has exactly ONE Bid hour file. Date-level presence said "complete";
the data says otherwise.

HOUR-LABEL MAPPING, established empirically, not assumed:
  * Last files are missing hour label 18 on EVERY date. The NQ maintenance break is 17:00-18:00 ET.
    => label = ET hour + 1.
  * Check: 20260319 Bid labels 01-23 produced ET 00:00-22:00 coverage on 03-19. Consistent.
  * Check: session s20260318's evening leg (ET 18:00-23:59 on 03-17) came from 20260317 labels
    19-23 plus 20260318 label 00. Both present. Consistent.

So session sD needs, for each of Bid and Ask:
    evening leg : labels 19..23 on date D-1   (ET 18:00 -> 22:59)
    plus label 00 on date D                   (ET 23:00 -> 23:59)
    day leg     : labels 01..17 on date D     (ET 00:00 -> 16:59)

This script reports coverage as a FRACTION of those required hour labels, and classifies. The
DEFINITIVE number is still post-extraction QA on realised events -- this is the planning estimate.
"""
from __future__ import annotations

import os
import re
from collections import defaultdict

import pandas as pd

DB = os.path.join(os.path.expanduser("~"), "Documents", "NinjaTrader 8", "db", "tick")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")
os.makedirs(OUT, exist_ok=True)
SEAL = "2026-08-01"
NCD = re.compile(r"^(\d{8})(\d{2})\d{2}\.(Last|Bid|Ask)\.ncd$", re.I)

EVENING = [19, 20, 21, 22, 23]        # on D-1
DAY = [0] + list(range(1, 18))        # label 00 on D plus 01..17 on D


def main():
    have = defaultdict(set)                    # (date, series) -> {hour labels}
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
                ymd, hh, series = m.group(1), int(m.group(2)), m.group(3).capitalize()
                iso = f"{ymd[:4]}-{ymd[4:6]}-{ymd[6:8]}"
                have[(iso, series)].add(hh)

    dates = sorted({d for d, _ in have})
    rows = []
    for iso in dates:
        if iso >= SEAL:
            continue
        prev = str((pd.Timestamp(iso) - pd.Timedelta(days=1)).date())
        rec = dict(session="s" + iso.replace("-", ""), date=iso)
        for series in ("Last", "Bid", "Ask"):
            ev = have.get((prev, series), set())
            dy = have.get((iso, series), set())
            need = len(EVENING) + len(DAY)
            got = len([h for h in EVENING if h in ev]) + len([h for h in DAY if h in dy])
            rec[series.lower() + "_hours"] = got
            rec[series.lower() + "_frac"] = round(got / need, 3)
        rows.append(rec)

    D = pd.DataFrame(rows)
    D["quote_frac"] = D[["bid_frac", "ask_frac"]].min(axis=1)
    D["cls"] = pd.cut(D["quote_frac"], [-0.01, 0.05, 0.90, 1.01],
                      labels=["NONE", "PARTIAL", "FULL"])
    D.to_csv(os.path.join(OUT, "bbo_hourly_truth.csv"), index=False)

    P = print
    P("=" * 100)
    P("=== NQ QUOTE COVERAGE AT HOUR GRANULARITY  (planning estimate; QA on events is definitive)")
    P("=" * 100)
    P(f"    sessions with any tick file (pre-seal)   {len(D):>5}")
    P(f"    Last coverage >= 0.90                    {int((D['last_frac'] >= 0.90).sum()):>5}")
    P("")
    for c in ("FULL", "PARTIAL", "NONE"):
        n = int((D["cls"] == c).sum())
        P(f"    quotes {c:<8} {n:>5}")
    P("")
    old = int((D["bid_hours"] > 0).sum() & 1) if False else int(
        ((D["bid_hours"] > 0) & (D["ask_hours"] > 0)).sum())
    P(f"    DATE-LEVEL count (the audit's first pass, any Bid+Ask hour at all)   {old:>5}")
    P(f"    HOUR-LEVEL count (>= 90 % of required session hours)                "
      f"{int((D['cls'] == 'FULL').sum()):>5}")
    P(f"    >>> the first pass OVERSTATED usable BBO sessions by "
      f"{old - int((D['cls'] == 'FULL').sum())}")
    P(f"\n    wrote {OUT}\\bbo_hourly_truth.csv")


if __name__ == "__main__":
    main()
