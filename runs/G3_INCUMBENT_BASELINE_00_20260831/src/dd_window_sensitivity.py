"""Where does M_11's max drawdown actually come from, and why do two repo runs disagree by 2x?

G2_OQ6_MAPPING_20260830 reports M_11 maxDD = $21,740.44.
G3_INCUMBENT_BASELINE_00 reports M_11 maxDD = $45,138.
Both are in this repository. One of them was the campaign's capital number for a while.

This resolves it. VERIFICATION ONLY - nothing is selected and no window is chosen here.
"""

from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT)
from research_sdk.champion_eval import weekly_from_trades, max_drawdown, fixed_dd_income  # noqa

SRC = os.path.join(ROOT, "runs", "G2_AUG_INCUMBENT_READ_20260830", "out")


def main() -> int:
    P = pd.read_csv(os.path.join(SRC, "p1_trades_full.csv"))
    X = pd.read_csv(os.path.join(SRC, "xm_trades_full.csv"))
    aw = sorted(set(P.wk) | set(X.wk))
    _, wp = weekly_from_trades(P.wk.tolist(), P.pnl.to_numpy(float), aw)
    _, wx = weekly_from_trades(X.wk.tolist(), X.pnl.to_numpy(float), aw)
    aw = np.array(aw)
    comb = wp + wx

    print("=" * 100)
    print("WINDOW SENSITIVITY OF M_11's MAX DRAWDOWN - the quantity the capital plan rests on")
    print("=" * 100)
    print(f"\n{'window':<28}{'weeks':>6}{'net/wk':>10}{'maxDD':>11}{'fixDD/wk':>10}{'worst wk':>11}")

    def row(lab, m):
        w = comb[m]
        mdd, _ = max_drawdown(w)
        print(f"{lab:<28}{len(w):>6}{w.mean():>10,.0f}{mdd:>11,.0f}"
              f"{fixed_dd_income(w, 20245.0):>10,.0f}{w.min():>11,.0f}")

    row("FULL 2021-W52..2026-W35", np.ones(len(aw), bool))
    row("OQ6 2022-W27..2026-W31", (aw >= "2022-W27") & (aw <= "2026-W31"))
    row("from 2022-W27 to end", aw >= "2022-W27")
    row("2022 only", (aw >= "2022-W01") & (aw <= "2022-W52"))
    row("H1 2022 only", (aw >= "2022-W01") & (aw <= "2022-W26"))
    row("2023 onward", aw >= "2023-W01")

    c = np.cumsum(comb)
    pk = np.maximum.accumulate(c)
    dd = pk - c
    i = int(np.argmax(dd))
    j = int(np.argmax(c[:i + 1]))
    print("\nWHERE THE MAXIMUM DRAWDOWN ACTUALLY OCCURS (full window):")
    print(f"  peak {aw[j]} -> trough {aw[i]}   depth ${dd[i]:,.0f}   duration {i - j} weeks")
    dd2 = dd.copy()
    dd2[max(0, j - 5):i + 5] = 0
    i2 = int(np.argmax(dd2))
    j2 = int(np.argmax(c[:i2 + 1]))
    print(f"  second:  {aw[j2]} -> {aw[i2]}   depth ${dd2[i2]:,.0f}   duration {i2 - j2} weeks")
    h1 = (aw >= "2022-W01") & (aw <= "2022-W26")
    print(f"\n  M_11 net over H1 2022 ({int(h1.sum())} weeks): ${comb[h1].sum():,.0f}")

    print("\n" + "=" * 100)
    print("CONCLUSION")
    print("=" * 100)
    print("  M_11's ENTIRE $45,138 maximum drawdown is ONE 12-week episode, 2022-W05 -> 2022-W17.")
    print("  OQ6's window began at 2022-W27, which EXCLUDES that episode completely. That is the")
    print("  whole disagreement. It was not a manipulation - OQ6 used a 'common dev window' for a")
    print("  different purpose (matching an inverse-vol risk share) - but the EFFECT is that the")
    print("  campaign's capital figure was set by a window starting after its worst drawdown.")
    print()
    print("  The residual $28,596 vs $21,740 on the SAME window is a week-attribution difference:")
    print("  OQ6 buckets by ISO week of the ENTRY date and states in its own spec that its")
    print("  convention is 'not identical to W103's bucketing'. This run uses the ledger's own wk")
    print("  column. The structural point does not depend on which is preferred.")
    print()
    print("  ERABREAK01 (p=0.0011) places the 0DTE structural break at 2022-05, so H1 2022 is")
    print("  OLD-REGIME. Under standing owner doctrine (post-W115) old-regime failure is a RISK")
    print("  CLASSIFICATION, NOT a reason to exclude. So $45,138 is the honest drawdown to plan")
    print("  against, and it is carried, not deleted.")
    print()
    print("  NOTE ON LANGUAGE: $45,138 is a DRAWDOWN, not a capital requirement. The retired")
    print("  figures $21,740 and $45,000 were quoted as CAPITAL. They stay retired. A $75-90k")
    print("  capital plan against a $45,138 realised drawdown is roughly 2x coverage and is")
    print("  coherent with this measurement.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
