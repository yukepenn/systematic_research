"""OTR_R30 Part A amendment 1: quantity-normalized proof via the session-range bound.

"Exit on session close" is CHECKED in every 2026 frame (committed FACT), so no trade spans a
session.  A single trade of quantity q therefore cannot move more index points than the High-Low
range of the one session it lived in:

        largest_win / (20 * q)  <=  max session range in that window

Implied points FALL as q rises, so this places a LOWER bound on q.  Per amendment 1 D3 the test
is asymmetric: it can only EXCLUDE small q, so "q=1 survives" is weak confirmation whereas
"q=1 excluded" is strong refutation.
"""
from __future__ import annotations

import csv
import os
from fractions import Fraction

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(ROOT, "runs", "OTR_R30_ENTRY_EXIT_DECOMP", "out")
Q_CANDIDATES = [1, 2, 4, 5, 8, 10, 13, 20]        # the set that can give -$2600 at a legal tick


def cents(x):
    return int(round(Fraction(str(x)) * 100))


def main():
    tgt = list(csv.DictReader(open(os.path.join(
        ROOT, "research", "original_trader_reconstruction", "screenshot_forensics",
        "derived", "targets_weekly_2026V.csv"), encoding="utf-8")))
    df = pd.read_parquet(os.path.join(ROOT, "research", "scalping_lab", "substrate",
                                      "minute", "NQ", "nq1m_2005_202605.parquet"))
    df["time"] = pd.to_datetime(df["time"])
    sub = df[df["time"] >= "2026-01-01"].reset_index(drop=True)
    t = sub["time"].values.astype("datetime64[s]")
    hi, lo = sub["high"].values, sub["low"].values
    fb = np.zeros(len(sub), bool); fb[0] = True
    fb[1:] = np.diff(t).astype("timedelta64[m]").astype(np.int64) > 60
    sid = np.cumsum(fb) - 1
    LAST = t[-1]
    print(f"local substrate usable to {LAST}\n")

    print("=" * 96)
    print("session ranges per window, and which quantities survive the bound")
    print("=" * 96)
    print(f"{'window':<24}{'maxSessRange':>13}{'largest_win':>13}"
          f"   implied index points per candidate q   -> surviving q")
    rows = []
    survive_all = set(Q_CANDIDATES)
    tested = 0
    for r in tgt:
        a = np.datetime64(pd.Timestamp(r["report_start"]) - pd.Timedelta(days=1)) + np.timedelta64(18, "h")
        b = np.datetime64(pd.Timestamp(r["report_end"])) + np.timedelta64(17, "h")
        if b > LAST:
            print(f"{r['report_start']}->{r['report_end']:<11}{'UNTESTABLE - substrate ends 2026-05-29'  if b > LAST else ''}")
            rows.append(dict(image_id=r["image_id"], window=f"{r['report_start']}->{r['report_end']}",
                             max_session_range="", largest_win=r.get("largest_win_all", ""),
                             surviving_q="UNTESTABLE", note="bars not local / sealed"))
            continue
        m = (t >= a) & (t <= b)
        if not m.any():
            continue
        s = sid[m]
        rng = 0.0
        for k in np.unique(s):
            kk = m.copy(); kk[m] = (s == k)
            rng = max(rng, float(hi[kk].max() - lo[kk].min()))
        lw = cents(r["largest_win_all"]) / 100.0
        ll = abs(cents(r["largest_loss_all"]) / 100.0)
        surv, imp = [], []
        for q in Q_CANDIDATES:
            pw = lw / (20.0 * q); pl = ll / (20.0 * q)
            ok = pw <= rng and pl <= rng
            imp.append(f"q{q}:{pw:.0f}{'' if ok else 'X'}")
            if ok:
                surv.append(q)
        survive_all &= set(surv); tested += 1
        print(f"{r['report_start']}->{r['report_end']:<11}{rng:>13.2f}{lw:>13.2f}   "
              f"{' '.join(imp[:5])}  -> {surv}")
        rows.append(dict(image_id=r["image_id"], window=f"{r['report_start']}->{r['report_end']}",
                         max_session_range=round(rng, 2), largest_win=lw,
                         surviving_q=";".join(map(str, surv)), note=""))

    print("\n" + "=" * 96)
    print("D1 / D2 VERDICT")
    print("=" * 96)
    print(f"  windows testable with local bars : {tested}")
    print(f"  intersection of surviving q      : {sorted(survive_all)}")
    print(f"  D1 (intersection non-empty)      : "
          f"{'PASS' if survive_all else 'FAIL - uniform quantity itself is refuted'}")
    print(f"  q = 1 survives everywhere?       : {'YES' if 1 in survive_all else 'NO'}")
    print(f"  q = 2 survives everywhere?       : {'YES' if 2 in survive_all else 'NO'}")
    if 1 in survive_all and 2 in survive_all:
        print("\n  D2 -> NEITHER is excluded by the session bound.  '130 x 1' and '65 x 2' both")
        print("        remain live.  Per D3 this is the WEAK direction of the test.")
    elif 1 not in survive_all:
        print("\n  D2 -> q=1 EXCLUDED: the 130-point stop is REFUTED (strong direction).")
    else:
        print("\n  D2 -> q=1 survives and q=2 excluded: 130-point stop confirmed independently.")

    # ---- the complementary parity constraint, combined ----
    print("\n" + "=" * 96)
    print("combining with the Part A parity constraint (uniform q within one SA backtest)")
    print("=" * 96)
    odd_forced = []
    for r in tgt:
        if cents(r["commission_total"]) != 0:
            continue
        for k in ("largest_win_all", "largest_loss_all"):
            if r.get(k) and cents(r[k]) % 500 == 0 and (abs(cents(r[k])) // 500) % 2 == 1:
                odd_forced.append((r["image_id"], r["report_end"], k))
    print(f"  SA records with an ODD single-trade cell (forces odd q for that trade): "
          f"{len(odd_forced)}")
    for img, d, k in odd_forced:
        print(f"     {img} {d}  {k}")
    odd_q = [q for q in sorted(survive_all) if q % 2 == 1]
    print(f"\n  q surviving BOTH the session bound AND odd parity: {odd_q}")
    print("  (parity applies only to the records listed above; a Strategy Analyzer run uses one")
    print("   DefaultQuantity, so within THOSE records q must be odd)")
    if odd_q:
        for q in odd_q:
            print(f"     q={q:<3} -> stop = {2600/(20*q):.2f} index points")

    with open(os.path.join(OUT, "quantity_session_bound.csv"), "w", newline="",
              encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)


if __name__ == "__main__":
    main()
