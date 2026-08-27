"""WE_W110b - correcting W110's OWN tail-winner null, plus two smaller repairs.

THE DEFECT, mine. W110 built leave-one-out predictions with the TRUE labels and then tested them
against a null that permuted the labels while HOLDING THE PREDICTIONS FIXED. With 20 positives out
of 348, dropping one still leaves 19 in the training set, so the prediction vector is heavily
informed by the label vector as a whole. Permuting labels afterwards destroys a relationship the
model was built to have, which makes the null far too easy to beat. A 99.7th percentile computed
that way is not evidence.

THE FIX: permute the labels FIRST, then re-run the entire cross-validated fit on the permuted
labels, so the null model gets exactly the same opportunity to overfit that the real one had. That
is the only null that answers the question asked.

Also repaired here:
  * tie-aware percentiles for the DISCRETE downside statistics (a real value of 0 against a null
    with mass at 0 was printed as "0.0th percentile", which overstates it);
  * a feature ablation, because if the whole result is "announcement day plus a wide overnight
    range" then that is what should be written down, not a ten-feature model.

STILL MEASUREMENT ONLY. Nothing here may create a filter.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT                                              # noqa: E402
from sklearn.linear_model import LogisticRegression                      # noqa: E402
from sklearn.model_selection import StratifiedKFold                      # noqa: E402
from sklearn.preprocessing import StandardScaler                         # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W110_XMDIVERSE", "out")
FEATS = ["drive_pts", "abs_comp_z", "divergence", "nq_sigma", "morn_vol_rel",
         "gap_pts", "on_range_rel", "is_long", "dow", "is_ann"]
NPERM = 400
NFOLD = 10
SEED = 1100


def auc_of(p, y):
    r = pd.Series(p).rank().to_numpy()
    n1, n0 = int(y.sum()), int((~y).sum())
    return (r[y].sum() - n1 * (n1 + 1) / 2.0) / max(n1 * n0, 1)


def cv_auc(X, y, seed):
    """stratified K-fold out-of-fold predictions, scaler fit INSIDE each fold."""
    pred = np.full(len(y), np.nan)
    skf = StratifiedKFold(n_splits=NFOLD, shuffle=True, random_state=seed)
    for tr, te in skf.split(X, y):
        sc = StandardScaler().fit(X[tr])
        lr = LogisticRegression(C=0.5, max_iter=2000)
        lr.fit(sc.transform(X[tr]), y[tr])
        pred[te] = lr.predict_proba(sc.transform(X[te]))[:, 1]
    return auc_of(pred, y)


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "xmdiverse_b.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    rng = np.random.default_rng(SEED)
    F = pd.read_csv(os.path.join(OUT, "trade_features.csv"))
    W = pd.read_csv(os.path.join(OUT, "weekly.csv"))
    P_(f"    {len(F)} XM trades, {len(W)} weeks reloaded from W110's own artifacts.")

    # ------------------------------------------------------------------ tie-aware percentiles
    P_("")
    P_("=" * 124)
    P_("=== 1. TIE-AWARE PERCENTILES for the DISCRETE downside statistics")
    P_("===    W110 printed 'fraction of shifts strictly below the real value'. For a statistic")
    P_("===    whose null has mass exactly AT the real value that reads as 0.0th percentile and")
    P_("===    overstates the finding. Reported here as the exceedance probability instead.")
    P_("=" * 124)
    p1w, xmw = W["p1"].to_numpy(), W["xm"].to_numpy()
    NW = len(p1w)

    def jw10(a, b):
        return float(len(set(np.argsort(a)[:10].tolist()) & set(np.argsort(b)[:10].tolist())))

    def jdd(a, b):
        sa, sb = a.std(ddof=1), b.std(ddof=1)
        w = (1 / sa) / ((1 / sa) + (1 / sb))
        e = np.cumsum(w * a + (1 - w) * b)
        pk = np.maximum.accumulate(e)
        u = e < pk - 1e-9
        best = cur = 0
        for x in u:
            cur = cur + 1 if x else 0
            best = max(best, cur)
        return float(best)

    for nm, fn in (("joint worst-10 overlap", jw10), ("joint drawdown, weeks", jdd)):
        real = fn(p1w, xmw)
        nul = np.array([fn(p1w, np.roll(xmw, k)) for k in range(1, NW)])
        le = float(np.mean(nul <= real))
        P_(f"    {nm:<24} REAL {real:>7.1f}   null mean {nul.mean():>7.2f}   "
           f"P(null <= real) = {le:.3f}   -> "
           f"{'as good or better by chance in ' + f'{100*le:.1f} %' + ' of shifts' if le > 0.05 else 'BEYOND the null (p < 0.05)'}")

    # ------------------------------------------------------------------ the corrected AUC null
    P_("")
    P_("=" * 124)
    P_("=== 2. THE CORRECTED TAIL-WINNER NULL")
    P_(f"===    {NPERM} permutations, and each one RE-RUNS the whole {NFOLD}-fold cross-validated")
    P_("===    fit on its permuted labels, so the null model gets exactly the same opportunity to")
    P_("===    overfit that the real one had. The scaler is fitted inside each fold.")
    P_("=" * 124)
    X = F[FEATS].to_numpy()
    g = np.all(np.isfinite(X), axis=1)
    X = X[g]
    pnl = F["pnl"].to_numpy()[g]
    P_(f"{'cut':<10}{'% of net':>10}{'real AUC':>11}{'null mean':>11}{'null p95':>10}"
       f"{'p-value':>10}{'verdict':>24}")
    keep = {}
    for TOPK in (20, 10, 5):
        y = np.zeros(len(X), bool)
        y[np.argsort(-pnl)[:TOPK]] = True
        real = cv_auc(X, y, SEED)
        nul = np.empty(NPERM)
        for b in range(NPERM):
            nul[b] = cv_auc(X, rng.permutation(y), SEED + 1 + b)
        pv = float(np.mean(nul >= real))
        keep[TOPK] = (y, real, nul, pv)
        P_(f"{'top ' + str(TOPK):<10}{100*pnl[y].sum()/pnl.sum():>9.0f}%{real:>11.3f}"
           f"{nul.mean():>11.3f}{np.percentile(nul, 95):>10.3f}{pv:>10.3f}"
           f"{('MECHANISM-CONSISTENT' if pv < 0.05 else 'NOT IDENTIFIABLE'):>24}")
    P_("")
    P_("    For reference, W110's defective figures were 0.697 / 0.758 / 0.863 at the 99.7th,")
    P_("    99.9th and 99.9th percentiles. Those are WITHDRAWN and replaced by the line above.")

    # ------------------------------------------------------------------ ablation
    P_("")
    P_("=" * 124)
    P_("=== 3. FEATURE ABLATION - is the whole result just 'announcement day + wide overnight'?")
    P_("=" * 124)
    y20 = keep[20][0]
    P_(f"{'feature set':<38}{'AUC':>8}{'delta vs full':>15}")
    full = keep[20][1]
    P_(f"{'ALL 10 FEATURES':<38}{full:>8.3f}{0.0:>15.3f}")
    for drop in FEATS:
        ii = [i for i, f_ in enumerate(FEATS) if f_ != drop]
        a = cv_auc(X[:, ii], y20, SEED)
        P_(f"{'drop ' + drop:<38}{a:>8.3f}{a-full:>15.3f}")
    P_("")
    for sub in (["is_ann"], ["on_range_rel"], ["is_ann", "on_range_rel"],
                ["is_ann", "on_range_rel", "divergence"],
                [f for f in FEATS if f not in ("is_ann", "on_range_rel")]):
        ii = [i for i, f_ in enumerate(FEATS) if f_ in sub]
        a = cv_auc(X[:, ii], y20, SEED)
        P_(f"{'ONLY ' + ' + '.join(sub):<38}{a:>8.3f}{a-full:>15.3f}")

    P_("")
    P_("    THE CAVEAT THAT TRAVELS WITH EVERY NUMBER ABOVE: 'tail winner' is defined by the P&L of")
    P_("    these same 348 trades. Cross-validation controls OVERFITTING, it does not create a")
    P_("    holdout. This is a DESCRIPTIVE claim about which pre-entry states the big winners came")
    P_("    from. It is NOT a demonstration that the next big winner can be picked in advance, and")
    P_("    the spec forbids turning any of it into a filter.")
    P_(f"\n[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
