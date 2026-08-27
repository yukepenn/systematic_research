"""RR_W002A addendum - is the ONE positive cell distinguishable from zero?

POST-HOC. NOT PREREGISTERED. Reported as a curiosity with its multiplicity attached, never as a
finding. The preregistered gates are in rr_w002b.txt and they are not re-read here.

Why it is worth running: M1_EXPERT_SCORE_ONLY - the strategy's OWN causal quality score, used
unfitted, with zero parameters - was the only cell of nine with a positive OOS rank correlation
(+0.0131) and a positive top-minus-bottom quintile spread (+$801), while every fitted model landed
at or below its own null. That is exactly the W112 pattern: an unfitted one-line control beating
every fitted model. If it survives its own null it is a MECHANISM-POLICY observation about the
quality layer, not new information - the score is built from features the engine already owns.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT                                               # noqa: E402

OUT = os.path.join(ROOT, "runs", "RR_W002A_ACTION_VALUE_INFORMATION", "out")
SEED, NSHIFT, FIRST_FIT = 2002, 200, 250
_fh = open(os.path.join(OUT, "rr_w002c.txt"), "w", encoding="utf-8")


def P_(*a):
    print(*a, flush=True)
    print(*a, file=_fh)
    _fh.flush()


def rho(p, y):
    g = np.isfinite(p) & np.isfinite(y)
    if g.sum() < 30 or np.nanstd(p[g]) == 0:
        return 0.0
    return float(spearmanr(p[g], y[g]).statistic)


def main():
    P_("=" * 118)
    P_("=== RR_W002A addendum - POST-HOC null for the one positive cell.  NOT PREREGISTERED.")
    P_("=== The preregistered gates stand as recorded. This adds a curiosity, not a finding.")
    P_("=" * 118)

    P = pd.read_csv(os.path.join(OUT, "predictions.csv"))
    y = P["target_full"].to_numpy()
    cells = [c for c in P.columns if c not in ("target_full", "session_date")]
    P["session_date"] = pd.to_datetime(P["session_date"])
    sess = P["session_date"].to_numpy()
    bnd = np.flatnonzero(np.diff(pd.factorize(sess)[0], prepend=-1) != 0)
    rng = np.random.default_rng(SEED)
    offs = rng.choice(bnd[1:], size=min(NSHIFT, len(bnd) - 1), replace=False)

    real = {c: rho(P[c].to_numpy(), y) for c in cells}
    P_("")
    P_(f"    {len(offs)} session-boundary circular shifts of the target.")
    P_("    M1 is UNFITTED - the raw quality score - so the shift alone is the whole null for it.")
    P_("")
    P_("    ⚠ FOR THE FITTED CELLS THIS IS THE WEAKER NULL. Predictions are held fixed while the")
    P_("    target is shifted - which is exactly W110's original error and makes the bar too easy.")
    P_("    The AUTHORITATIVE nulls for fitted cells refit the entire walk-forward inside every")
    P_("    shift and live in rr_w002b.txt. They are not re-read here. Fitted rows below are")
    P_("    printed only so M1 can be compared against the same construction, and both tables")
    P_("    agree on the verdict.")
    P_("")
    P_(f"{'cell':<26}{'real rho':>10}{'null p50':>10}{'null p95':>10}{'percentile':>12}")
    dists = {}
    for c in cells:
        p_ = P[c].to_numpy()
        d = np.array([rho(p_, np.roll(y, int(o))) for o in offs])
        dists[c] = d
        pct = 100.0 * float((d < real[c]).mean())
        P_(f"{c:<26}{real[c]:>10.4f}{np.percentile(d, 50):>10.4f}"
           f"{np.percentile(d, 95):>10.4f}{pct:>11.1f}%")

    P_("")
    P_("=" * 118)
    P_("=== THE MULTIPLICITY BAR - M1 was the BEST OF NINE cells, so a single-cell null is too easy")
    P_("=" * 118)
    stack = np.vstack([dists[c] for c in cells])
    bestk = stack.max(axis=0)
    m1 = real["M1_EXPERT_SCORE_ONLY"]
    pct_single = 100.0 * float((dists["M1_EXPERT_SCORE_ONLY"] < m1).mean())
    pct_bok = 100.0 * float((bestk < m1).mean())
    P_(f"    M1 real rho                                   {m1:>10.4f}")
    P_(f"    single-cell null p95                          "
       f"{np.percentile(dists['M1_EXPERT_SCORE_ONLY'], 95):>10.4f}   percentile {pct_single:.1f}%")
    P_(f"    BEST-OF-{len(cells)} null p95 (the honest bar)          "
       f"{np.percentile(bestk, 95):>10.4f}   percentile {pct_bok:.1f}%")
    P_("")
    P_(f"    verdict against the single-cell bar : {'clears' if pct_single >= 95 else 'DOES NOT CLEAR'}")
    P_(f"    verdict against the best-of-K bar   : {'clears' if pct_bok >= 95 else 'DOES NOT CLEAR'}")
    P_("")
    P_("    W116b measured that independent per-cell draws inflate a best-of-K bar by 1.65x on a")
    P_("    correlated family. Here the shifts are SHARED across cells - one draw per shift applied")
    P_("    to every cell - so the correlation between cells is preserved and the bar is not inflated.")
    P_("")
    P_("    Whatever this shows, it is a statement about the ENGINE'S OWN quality layer, which is")
    P_("    built from features the engine already owns and was fitted on this window. Per the spec's")
    P_("    discovery-consumption rule that is MECHANISM-POLICY, not NEW INFORMATION.")
    _fh.close()


if __name__ == "__main__":
    main()
