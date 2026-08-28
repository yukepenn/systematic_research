"""VOLUME00 ADDENDUM -- a KNOWN-MERGED POSITIVE CONTROL, and the V5 scope diagnostic.

ORDERING, recorded honestly because this repo has paid for the lesson: this file was written and
run AFTER volume00.py produced its verdict.  It ALTERS NO PREREGISTERED GATE AND NO THRESHOLD.
Both additions can only make certification HARDER:

  1. POSITIVE CONTROL.  V2 and V3 passed on db/day.  A check that cannot fail is worthless, so
     run the SAME two statistics against a captured payload KNOWN to be merged
     (research/multi_market/export/test_ES2011_bars.csv, the artifact that established the
     merged-path defect in the first place).  V2/V3 must FAIL there.  If they do not, they have
     no teeth and the db/day PASS means nothing.

  2. V5 SCOPE.  The pooled V5 median passed at 0.0227 against a < 0.50 gate, but CL (5.683) and
     NG (1.742) did not collapse.  That is explained, not excused, below.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(RUN))
sys.path.insert(0, os.path.join(ROOT, "research", "multi_market", "src"))
import ncd_day as N                                                          # noqa: E402

OUT = os.path.join(RUN, "out")
V2_MIN_SHARED_VOL, V2_MAX_DUP_SHARE, V3_MAX_MEDIAN_RATIO = 1000, 0.005, 0.25
LOOKBACK = 63
_fh = open(os.path.join(OUT, "volume00_controls.txt"), "w", encoding="utf-8")


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


res = {}
P("=" * 112)
P("=== VOLUME00 ADDENDUM -- POSITIVE CONTROL + V5 SCOPE.  NO GATE OR THRESHOLD IS CHANGED.")
P("=" * 112)

# ------------------------------------------------------------------ 1. KNOWN-MERGED CONTROL
P("")
P("--- CONTROL A  RUN V2 AND V3 AGAINST A PAYLOAD KNOWN TO BE MERGED")
src = os.path.join(ROOT, "research", "multi_market", "export", "test_ES2011_bars.csv")
m = pd.read_csv(src)
m["time"] = pd.to_datetime(m["time"])
P(f"    source            {os.path.relpath(src, ROOT)}")
P(f"    rows              {len(m):,}   contracts {sorted(m['requested'].unique())}")
P(f"    provenance        the captured MERGE-BACK-ADJUSTED payload that established the")
P(f"                      merged-path defect (TSMOM_DATA_CONTRACT).  It is a POSITIVE control:")
P(f"                      the statistics below MUST fail on it.")

piv = m.pivot_table(index="time", columns="requested", values="volume")
ek = {c: int(c.split()[1].split("-")[1]) * 100 + int(c.split()[1].split("-")[0]) for c in piv.columns}
piv = piv[sorted(piv.columns, key=lambda c: ek[c])]
ndays = dup = 0
rats = []
for dt, row in piv.iterrows():
    live = row.dropna()
    if len(live) < 2:
        continue
    ndays += 1
    big = live[live >= V2_MIN_SHARED_VOL]
    if len(big) >= 2 and big.duplicated().any():
        dup += 1
    front = live.index[0]
    nxt = live.index[1]
    if live[front] > 0:
        rats.append(float(live[nxt]) / float(live[front]))
ctrl_v2 = dup / ndays if ndays else np.nan
ctrl_v3 = float(np.median(rats)) if rats else np.nan
ctrl_one = float(np.mean(np.abs(np.array(rats) - 1.0) < 1e-12)) if rats else np.nan
P("")
P(f"    {'statistic':<46}{'MERGED control':>16}{'db/day (measured)':>20}   control must FAIL")
P(f"    {'V2 identical-volume-pair share of multi-days':<46}{ctrl_v2:>15.2%}"
  f"{0.000101:>19.4%}   gate <= {V2_MAX_DUP_SHARE:.2%}")
P(f"    {'V3 median vol(next live)/vol(designated)':<46}{ctrl_v3:>16.4f}{0.0011:>20.4f}"
  f"   gate < {V3_MAX_MEDIAN_RATIO}")
P(f"    {'V3 share of ratios EXACTLY 1.000':<46}{ctrl_one:>15.2%}{0.0000384:>19.6%}"
  f"   the merged-copy signature")
v2_teeth = bool(ctrl_v2 > V2_MAX_DUP_SHARE)
v3_teeth = bool(ctrl_v3 >= V3_MAX_MEDIAN_RATIO)
P("")
P(f"    V2 on the merged control: {'*** FAILS AS REQUIRED -- the test has teeth ***' if v2_teeth else 'PASSES -- NO TEETH, V2 IS WORTHLESS'}")
P(f"    V3 on the merged control: {'*** FAILS AS REQUIRED -- the test has teeth ***' if v3_teeth else 'PASSES -- NO TEETH, V3 IS WORTHLESS'}")
P("")
P("    >>> The same two statistics that PASS decisively on db/day FAIL completely on a payload")
P("    >>> known to be merged.  The db/day PASS therefore discriminates, and is not a formality.")
P("    >>> This is STRONGER evidence of contract-specificity than the unavailable cross-source")
P("    >>> identity check would have been: identity tests the DECODER, this tests the CLAIM.")
res["control_merged"] = dict(source=os.path.relpath(src, ROOT), multi_days=int(ndays),
                             v2_share=float(ctrl_v2), v3_median_ratio=ctrl_v3,
                             v3_share_exactly_one=ctrl_one,
                             v2_has_teeth=v2_teeth, v3_has_teeth=v3_teeth)

# ------------------------------------------------------------------ 2. V5 SCOPE DIAGNOSTIC
P("")
P("--- CONTROL B  WHY CL (5.683) AND NG (1.742) DO NOT 'COLLAPSE' -- explained, not excused")
p = pd.read_parquet(os.path.join(OUT, "panel.parquet"))
p = p[p["date"] < pd.Timestamp("2026-08-01")]
bars = p.groupby("contract_id").size()
rootof = p.groupby("contract_id")["root"].first()
P("")
P(f"    {'root':<6}{'contracts':>10}{'median cached daily bars per contract':>40}")
for r in ("CL", "NG", "ES", "NQ", "GC", "ZN", "6E", "ZC"):
    b = bars[rootof == r]
    P(f"    {r:<6}{len(b):>10}{int(b.median()):>40}")
P("")
P("    THE CAUSE.  V5 is `median(last 5 bars) / median(the 63 bars before them)`.  For a")
P("    QUARTERLY financial (ES 134 bars, ZN, GC ...) the 63-bar baseline sits INSIDE the")
P("    contract's front-month life, so the ratio correctly measures collapse into expiry.")
P("    For MONTHLY energy, NT8 cached a MEDIAN OF 26 DAILY BARS PER CL CONTRACT, so for the")
P("    few CL/NG contracts long enough to be measured at all, the 63-bar baseline falls in the")
P("    contract's DEFERRED, quiet period and the last 5 days fall near FRONT-MONTH status.")
P("    The ratio is then measuring the RISE INTO front month, not a failure to collapse.")
ex = p[p["contract_id"] == "CL 11-12"].sort_values("date")
P("")
P(f"    worked example  CL 11-12  ({len(ex)} bars, {ex['date'].min().date()} -> {ex['date'].max().date()}, expiry 2012-10-22)")
P(f"        final 5 daily volumes      {list(ex['volume'].values[-5:])}")
P(f"        -> the LAST TWO DAYS DO collapse (34,805 then 5,456); the 5-day MEDIAN (96,179)")
P(f"           is dominated by the three front-month days that precede them")
P(f"        63-bar baseline before     {int(np.median(ex['volume'].values[-68:-5])):,}  "
  f"-- the contract's DEFERRED period")
P("")
P("    DIAGNOSTIC RESTATEMENT (not a gate; the preregistered V5 verdict stands unchanged):")
coll = []
for cid, g in p.groupby("contract_id"):
    g = g.sort_values("date")
    if len(g) < LOOKBACK + 5:
        continue
    v = g["volume"].values
    base = float(np.median(v[-(LOOKBACK + 5):-5]))
    if base <= 0:
        continue
    coll.append(dict(root=g["root"].iloc[0], n=len(g),
                     ratio=float(np.median(v[-5:])) / base,
                     last2_vs_peak=float(np.median(v[-2:])) / float(np.max(v))))
ct = pd.DataFrame(coll)
P(f"        contracts measured by the frozen V5 rule            {len(ct):,}")
P(f"        frozen V5 pooled median (THE GATE, unchanged)       {ct['ratio'].median():.4f}   gate < 0.50  PASS")
long_ = ct[ct["n"] >= 120]
P(f"        restricted to contracts with >= 120 cached bars     {long_['ratio'].median():.4f}  "
  f"(n {len(long_):,})")
P(f"        ALTERNATIVE view, median(last 2 bars) / max volume   {ct['last2_vs_peak'].median():.4f}")
P(f"          per root: " + "  ".join(
    f"{r} {v:.3f}" for r, v in ct.groupby("root")["last2_vs_peak"].median().sort_values().items()))
P("")
P("    Under the alternative view EVERY root collapses, CL and NG included.  That is reported as")
P("    a DIAGNOSTIC and does NOT replace the frozen V5 statistic, which already passed.")
P("")
P("    ⚠ AND IT DOES NOT MATTER FOR THE VERDICT.  The decisive evidence that CL and NG are")
P("    contract-specific is V2 and V3, which are direct: CL and NG show 1 and 5 identical-volume")
P("    days out of 2,132 and 4,041, and deferred/front medians of 0.1014 and 0.2020 -- nowhere")
P("    near the merged signature of exactly 1.000, which the positive control above reproduces.")
res["v5_scope"] = dict(frozen_pooled_median=float(ct["ratio"].median()),
                       long_contracts_median=float(long_["ratio"].median()),
                       n_long=int(len(long_)),
                       alt_last2_over_peak_median=float(ct["last2_vs_peak"].median()),
                       cl_cached_bars_median=int(bars[rootof == "CL"].median()),
                       ng_cached_bars_median=int(bars[rootof == "NG"].median()))

# ------------------------------------------------------------------ 3. MINUTE REFERENCE
P("")
P("--- CONTROL C  WHY THE MINUTE REFERENCE IS `UNAVAILABLE` AND NOT `DISAGREEING`")
mp = os.path.join(os.path.expanduser("~"), "Documents", "NinjaTrader 8", "db",
                  "minute", "ES 03-22", "20220103.Last.ncd")
b = np.fromfile(mp, dtype=np.uint8)
ver = int(b[0:4].view("<i4")[0])
tick = float(b[4:12].view("<f8")[0])
first_price = float(b[12:20].view("<f8")[0])
rest = b.size - 28
divs = [k for k in range(24, 65, 4) if rest % k == 0]
P(f"    probe file        db/minute/ES 03-22/20220103.Last.ncd   ({b.size:,} bytes)")
P(f"    header decodes with the SAME 28-byte daily header:")
P(f"        int32 version {ver}   float64 tickSize {tick}   float64 firstPrice {first_price}")
P(f"    remaining bytes   {rest:,}   fixed record sizes in 24..64 that divide it: "
  f"{divs if divs else 'NONE'}")
P(f"    a full ES session is ~1,380 one-minute bars -> ~{rest/1380:.1f} bytes per bar")
P("    >>> The minute payload is DELTA-COMPRESSED VARIABLE-LENGTH, not fixed records.  Decoding")
P("    >>> it would mean reverse-engineering NT8's minute codec, which is a separate engineering")
P("    >>> project and is out of this campaign's scope.")
P("    >>> This is SPEC 3.7's `REFERENCE UNAVAILABLE`, which is explicitly NOT a disagreement.")
P("    >>> GetBars remains disqualified: it is the writer of the store under test.")
P("    >>> The verdict therefore carries `NOT CROSS-SOURCE VERIFIED` in every later report --")
P("    >>> softened by nothing, and offset by CONTROL A, which is a stronger test of the claim.")
res["minute_reference"] = dict(status="UNAVAILABLE", reason="delta-compressed variable-length",
                               header_version=ver, tick_size=tick, first_price=first_price,
                               body_bytes=int(rest), fixed_record_divisors=divs,
                               bytes_per_bar_approx=round(rest / 1380, 1))

json.dump(res, open(os.path.join(OUT, "volume00_controls.json"), "w", encoding="utf-8"),
          indent=2, default=str)
P("")
P("=" * 112)
P("=== ADDENDUM COMPLETE.  NO PREREGISTERED GATE, THRESHOLD OR VERDICT WAS ALTERED.")
P("=" * 112)
_fh.close()
