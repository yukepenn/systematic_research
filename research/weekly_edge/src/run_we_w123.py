"""WE_W123 - XM SESSION-TAIL INFORMATION. STAGE A ONLY. No veto is built.

Spec: runs/WE_W123_XMTAIL/spec.yaml, committed BEFORE this ran.

W119: XM is active on 33 % of sessions and present in 69.8 % of the book's worst-decile sessions.
Is there PRE-09:45 information that distinguishes its tail-loss trades from ordinary ones?

The target is declared in the spec before any fit, the feature set is FROZEN to exactly W110's
committed columns so no new search occurs, and the null is W110b's corrected construction: each
permutation RE-RUNS the entire cross-validated fit.

SMALL N. 348 trades, 35 in the tail. Only a large effect is interpretable and the report leads with
that.
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

OUT = os.path.join(ROOT, "runs", "WE_W123_XMTAIL", "out")
os.makedirs(OUT, exist_ok=True)
W110O = os.path.join(ROOT, "runs", "WE_W110_XMDIVERSE", "out")
LEDGER = os.path.join(ROOT, "runs", "WE_W119_BOOKLOSS", "out", "book_loss_ledger.csv")
FEATS = ["drive_pts", "abs_comp_z", "divergence", "nq_sigma", "morn_vol_rel",
         "gap_pts", "on_range_rel", "is_long", "dow", "is_ann"]
NPERM = 400
NFOLD = 10
SEED = 123


def auc_of(p, y):
    r = pd.Series(p).rank().to_numpy()
    n1, n0 = int(y.sum()), int((~y).sum())
    return (r[y].sum() - n1 * (n1 + 1) / 2.0) / max(n1 * n0, 1)


def cv_auc(X, y, seed):
    pred = np.full(len(y), np.nan)
    skf = StratifiedKFold(n_splits=min(NFOLD, int(y.sum())), shuffle=True, random_state=seed)
    for tr, te in skf.split(X, y):
        sc = StandardScaler().fit(X[tr])
        lr = LogisticRegression(C=0.5, max_iter=2000)
        lr.fit(sc.transform(X[tr]), y[tr])
        pred[te] = lr.predict_proba(sc.transform(X[te]))[:, 1]
    return auc_of(pred, y)


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "xmtail.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    rng = np.random.default_rng(SEED)
    F = pd.read_csv(os.path.join(W110O, "trade_features.csv"))
    X = F[FEATS].to_numpy()
    g = np.all(np.isfinite(X), axis=1)
    X = X[g]
    pnl = F["pnl"].to_numpy()[g]
    P_(f"    {len(F)} XM trades, {int(g.sum())} with all {len(FEATS)} frozen features finite")
    P_("")
    P_("    ***  SMALL-N WAVE, stated first as the spec requires  ***")
    P_(f"    {len(pnl)} trades; the tail-loss group is {int(0.10*len(pnl))} of them. A logistic on")
    P_("    ten features with ~35 positives is at the edge of what cross-validation can adjudicate.")
    P_("    A NULL RESULT HERE MEANS 'not detectable at n=348', NOT 'no such information exists'.")

    TARGETS = {}
    q10 = np.percentile(pnl, 10)
    q05 = np.percentile(pnl, 5)
    TARGETS["TAIL_LOSS worst 10%"] = pnl <= q10
    TARGETS["TAIL_LOSS worst 5%"] = pnl <= q05
    if "mae" in F.columns:
        mae = F["mae"].to_numpy()[g]
        TARGETS["worst-decile MAE"] = mae <= np.percentile(mae, 10)
    TARGETS["TAIL_WINNER top 10% (W110 symmetry check)"] = pnl >= np.percentile(pnl, 90)

    # ------------------------------------------------------------------ stage 1
    P_("")
    P_("=" * 122)
    P_("=== STAGE 1 - per-feature stratification, simple and first (section 26)")
    P_("=" * 122)
    y0 = TARGETS["TAIL_LOSS worst 10%"]
    P_(f"    TAIL_LOSS worst 10 %: n={int(y0.sum())}, mean ${pnl[y0].mean():,.0f} vs "
       f"${pnl[~y0].mean():,.0f} for the rest")
    P_("")
    P_(f"{'feature':<16}{'tail mean':>12}{'rest mean':>12}{'tail med':>12}{'rest med':>12}"
       f"{'perm p':>9}")
    for f_ in FEATS:
        x = F[f_].to_numpy()[g]
        d0 = float(x[y0].mean() - x[~y0].mean())
        nul = np.empty(2000)
        for b in range(2000):
            p_ = rng.permutation(y0)
            nul[b] = float(x[p_].mean() - x[~p_].mean())
        pv = float(np.mean(np.abs(nul) >= abs(d0)))
        P_(f"{f_:<16}{x[y0].mean():>12.3f}{x[~y0].mean():>12.3f}"
           f"{np.median(x[y0]):>12.3f}{np.median(x[~y0]):>12.3f}{pv:>9.3f}"
           + ("  *" if pv < 0.05 else ""))

    # ------------------------------------------------------------------ stage 2
    P_("")
    P_("=" * 122)
    P_("=== STAGE 2 - one regularised logistic, frozen features, W110b's CORRECTED null")
    P_(f"===   {NPERM} permutations, each RE-RUNNING the entire cross-validated fit.")
    P_("=" * 122)
    P_(f"{'target':<44}{'n pos':>7}{'real AUC':>11}{'null mean':>11}{'null p95':>10}"
       f"{'p-value':>10}")
    RES = {}
    for lab, y in TARGETS.items():
        if y.sum() < 12:
            P_(f"{lab:<44}{int(y.sum()):>7}   too few positives"); continue
        real = cv_auc(X, y, SEED)
        nul = np.array([cv_auc(X, rng.permutation(y), SEED + 1 + b) for b in range(NPERM)])
        pv = float(np.mean(nul >= real))
        RES[lab] = (real, nul, pv)
        P_(f"{lab:<44}{int(y.sum()):>7}{real:>11.3f}{nul.mean():>11.3f}"
           f"{np.percentile(nul,95):>10.3f}{pv:>10.3f}")

    # ------------------------------------------------------------------ gates
    P_("")
    P_("=" * 122)
    P_("=== GATES - every clause coded (section 29)")
    P_("=" * 122)
    real, nul, pv = RES["TAIL_LOSS worst 10%"]
    p95 = float(np.percentile(nul, 95))
    G = [("G1", "TAIL_LOSS AUC > permutation-null p95", f"{real:.3f} vs {p95:.3f}", real > p95)]
    P_(f"{'gate':<6}{'spec':<50}{'observed':>22}{'verdict':>10}")
    for gg, spec, obsv, ok in G:
        P_(f"{gg:<6}{spec:<50}{obsv:>22}{('PASS' if ok else 'FAIL'):>10}")
    passed = all(x[3] for x in G)
    P_("")
    P_(f"    STAGE-A VERDICT: "
       f"{'TAIL-LOSS INFORMATION FOUND' if passed else 'NO DETECTABLE TAIL-LOSS INFORMATION'}")

    # ------------------------------------------------------------------ the asymmetry
    P_("")
    P_("=" * 122)
    P_("=== THE SYMMETRY CHECK - W110 found tail WINNERS identifiable at AUC 0.735 on these")
    P_("===   same features and this same n. Are LOSERS?")
    P_("=" * 122)
    for lab in ("TAIL_LOSS worst 10%", "TAIL_WINNER top 10% (W110 symmetry check)"):
        if lab in RES:
            r_, n_, p_ = RES[lab]
            P_(f"    {lab:<44} AUC {r_:.3f}   p {p_:.3f}   "
               f"{'IDENTIFIABLE' if p_ < 0.05 else 'not identifiable'}")
    P_("")
    P_("    If winners are identifiable on exactly these features and losers are not, that")
    P_("    ASYMMETRY is itself the finding: XM's right tail has a causal pre-entry signature")
    P_("    and its left tail does not.")

    # ------------------------------------------------------------------ upper bound only
    P_("")
    P_("=" * 122)
    P_("=== SESSION-TAIL CONTRIBUTION - restated, AS AN UPPER BOUND ONLY. Not a policy.")
    P_("=" * 122)
    L = pd.read_csv(LEDGER)
    q = L["book_pnl"].quantile(0.10)
    tail = L["book_pnl"] <= q
    P_(f"    book worst decile: {int(tail.sum())} sessions carrying "
       f"${float(L.loc[tail,'book_pnl'].sum()):,.0f}")
    P_(f"    XM active in {int((tail & L['xm_active']).sum())} of them "
       f"({100*float((tail & L['xm_active']).mean()/max(tail.mean(),1e-9)):.1f} %), "
       f"against a {100*float(L['xm_active'].mean()):.1f} % overall activation rate")
    P_(f"    XM dollars inside the book's worst decile: "
       f"${float(L.loc[tail,'xm_pnl'].sum()):,.0f}")
    P_("")
    P_("    An ORACLE that removed XM's own worst-decile trades would recover "
       f"${-float(pnl[TARGETS['TAIL_LOSS worst 10%']].sum()):,.0f} - but that oracle knows the")
    P_("    outcome. Stage A just measured whether it is knowable in advance. Per the spec, no")
    P_("    veto is built, tested or costed here, and any future improvement of this kind is")
    P_("    classified as RISK POLICY or CATASTROPHE CONTROL, never as alpha (section 31).")
    pd.DataFrame([dict(target=k, auc=v[0], p=v[2]) for k, v in RES.items()]).to_csv(
        os.path.join(OUT, "targets.csv"), index=False)
    P_(f"\n[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
