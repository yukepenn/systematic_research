"""NON-GATE APPENDIX to TICK01ERA / TICK01ERA2. Reads NO outcome, moves NO gate, changes NO verdict.

Both era runs are already committed. This exists only because the source CSVs live OUTSIDE the repo
(Documents/NinjaTrader 8/out/era/, hash-pinned in each run's out/manifest.csv), so the one
descriptive fact that most sharply characterises the frozen event definition would otherwise not be
durably preserved:

    across the six named crisis windows the -1000 trigger was supposed to select, it fires in some
    and NEVER fires in the largest one.

Only $TICK closes are read. No NQ, no return, no P&L, no gate.
"""
from __future__ import annotations

import os

import pandas as pd

ERA = os.path.join(os.path.expanduser("~"), "Documents", "NinjaTrader 8", "out", "era")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")
assert os.path.isdir(OUT), OUT
TRIG = -1000.0

WINDOWS = [
    ("Aug-2015 devaluation", 2015, "2015-08-17", "2015-09-04"),
    ("Jan-2016 selloff",     2016, "2016-01-04", "2016-01-29"),
    ("Feb-2018 VIX spike",   2018, "2018-02-01", "2018-02-16"),
    ("Oct-2018 selloff",     2018, "2018-10-01", "2018-10-31"),
    ("Dec-2018 selloff",     2018, "2018-12-01", "2018-12-31"),
    ("Feb/Mar-2020 COVID",   2020, "2020-02-19", "2020-03-31"),
]

lines = []


def P(s=""):
    print(s, flush=True)
    lines.append(s)


P("=" * 104)
P("=== NON-GATE APPENDIX: does the frozen -1000 trigger fire in the crises it was meant to select?")
P("=== $TICK 1-min CLOSES only. No outcome, no return, no gate. Source CSVs hash-pinned in")
P("=== runs/TICK01ERA*_20260831/out/manifest.csv")
P("=" * 104)
P(f"    {'window':<24}{'sessions':>10}{'min close':>12}{'closes <= -1000':>18}"
  f"{'sessions with one':>20}")
cache = {}
for name, year, a, b in WINDOWS:
    if year not in cache:
        d = pd.read_csv(os.path.join(ERA, f"era{year}_bars.csv"))
        d["time"] = pd.to_datetime(d["time"])
        d = d[d["symbol"] == "$TICK"].copy()
        d["d"] = d["time"].dt.normalize()
        cache[year] = d
    d = cache[year]
    w = d[(d["d"] >= pd.Timestamp(a)) & (d["d"] <= pd.Timestamp(b))]
    hit = w[w["close"] <= TRIG]
    P(f"    {name:<24}{w['d'].nunique():>10,}{w['close'].min():>12,.0f}{len(hit):>18,}"
      f"{hit['d'].nunique():>20,}")

P("")
P("    THE ONE THAT MATTERS - every session of the COVID crash, $TICK daily close range:")
d = cache[2020]
w = d[(d["d"] >= pd.Timestamp("2020-02-19")) & (d["d"] <= pd.Timestamp("2020-03-31"))]
g = w.groupby("d")["close"].agg(["min", "max", "size"])
for dt_, r in g.iterrows():
    flag = "  <== fires" if r["min"] <= TRIG else ""
    P(f"      {dt_.date()}  min {r['min']:>8,.0f}   max {r['max']:>8,.0f}   bars {int(r['size'])}{flag}")
P("")
P(f"    March 2020 minimum $TICK close over the whole month: "
  f"{d[(d['d'] >= '2020-03-01') & (d['d'] <= '2020-03-31')]['close'].min():,.0f}")
P("    >>> The frozen -1000 trigger NEVER FIRES in March 2020 - the largest volatility event in")
P("    >>> the entire 2013-2026 sample. The event is not 'capitulation': it is a breadth extreme")
P("    >>> that a FIXED absolute threshold catches on sharp intraday breaks from a higher level")
P("    >>> and misses entirely when the market gaps down and stays down. That is a property of")
P("    >>> the DEFINITION, and it is a further reason the closure is a MECHANISM closure.")
P("    >>> It licenses NO new threshold. Choosing one now, having seen this, would be exactly the")
P("    >>> post-hoc threshold search every spec in this family forbids.")

with open(os.path.join(OUT, "crisis_appendix.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
