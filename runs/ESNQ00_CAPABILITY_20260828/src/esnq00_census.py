"""ESNQ00 - ES/NQ sub-minute CAPABILITY census.  A DISK INVENTORY, nothing more.

No outcome data is read. No model is fitted. No gate is evaluated. Preregistration does not bind
because nothing is tested against outcomes - and an ESNQ_V1 would need a full one.

Requires Bid AND Ask AND Last present for RTH hours 09-16 ET on the session date: that covers the
10:00-15:30 decision grid, the 30 s feature warmup before 10:00, and the 15:31 exit leg.

The criterion is VALIDATED against a known answer: all 58 exported v2 sessions must pass it. A
completeness test that disagrees with the substrate it describes is not usable.
"""
from __future__ import annotations

import collections
import os
import re

import pandas as pd

DB = os.path.join(os.path.expanduser("~"), "Documents", "NinjaTrader 8", "db", "tick")
ES = ["ES 09-25", "ES 12-25", "ES 03-26", "ES 06-26", "ES 09-26"]
NQ = ["NQ 09-25", "NQ 12-25", "NQ 03-26", "NQ 06-26", "NQ 09-26"]
NEED = set(range(9, 17))
SEAL = "20260801"


def hours(cids):
    out = collections.defaultdict(set)
    for cid in cids:
        d = os.path.join(DB, cid)
        if not os.path.isdir(d):
            continue
        for f in os.listdir(d):
            m = re.match(r"^(\d{8})(\d{2})00\.(Ask|Bid|Last)\.ncd$", f)
            if m:
                out[(m.group(1), m.group(3))].add(int(m.group(2)))
    return out


def complete(store):
    days = {d for d, _ in store}
    return sorted(d for d in days
                  if all(NEED <= store.get((d, k), set()) for k in ("Bid", "Ask", "Last")))


def main():
    e, n = complete(hours(ES)), complete(hours(NQ))
    both = sorted(set(e) & set(n))
    mf = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))))),
        "research", "data_microstructure_v2", "MANIFEST.csv"))
    exp = set(mf["session_date"].str.replace("-", "", regex=False))
    print(f"NQ RTH-complete {len(n):>4}   {n[0]} .. {n[-1]}")
    print(f"ES RTH-complete {len(e):>4}   {e[0]} .. {e[-1]}")
    print(f"BOTH            {len(both):>4}   {both[0]} .. {both[-1]}")
    print(f"  pre-seal      {len([d for d in both if d < SEAL]):>4}")
    print(f"  exported      {len(set(both) & exp):>4}")
    print(f"  NOT exported  {len([d for d in both if d < SEAL and d not in exp]):>4}")
    ok = len(exp - set(n)) == 0
    print(f"\nCRITERION VALIDATION: {len(set(n) & exp)}/{len(exp)} exported sessions pass  "
          f"{'PASS' if ok else '*** the criterion disagrees with the substrate ***'}")
    assert ok, "completeness criterion rejects sessions that were successfully exported"


if __name__ == "__main__":
    main()
