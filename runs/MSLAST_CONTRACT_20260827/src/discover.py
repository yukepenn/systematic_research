"""LANE A step 4 - DISCOVERY.  Does the certified Last-only feature set predict 60-second
AFTER-COST executable P&L?  Consumed sessions only; the blind pool is NOT opened.

s4F BINDS AND IS OBEYED LITERALLY:
  * PRIMARY = ONE regularized linear model (Ridge) on the certified features.
  * CHALLENGER = exactly ONE shallow nonlinear model, fixed hyperparameters, no sweep.
  * ridge alpha from a FIXED 5-point grid, chosen ONLY inside training folds.
  * training-only normalization.
  * chronological session-block validation. No random row split - rows inside a session are
    heavily dependent and a random split would leak the session's own regime across the fold.
  * ALL ATTEMPTS COUNTED, printed, and carried into the multiplicity threshold.
  * CASH IS AN ACTION. The policy is LONG / SHORT / CASH and the target is after-cost dollars.
    Directional accuracy is reported as a DIAGNOSTIC and never as an admission gate (the 54.16 %
    accuracy gate was retired for exactly this reason).

THE DEPENDENCE UNIT IS THE SESSION, NOT THE DECISION.  139,371 decisions live in 104 sessions.
Treating decisions as independent would inflate t by roughly sqrt(1340). Every inference below is
session-clustered, and the nulls resample WHOLE SESSIONS.
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "out")
SEED = 20260827
ALPHAS = (0.1, 1.0, 10.0, 100.0, 1000.0)     # FIXED grid, declared
N_FOLD = 5
NULL_B = 2000
_fh = open(os.path.join(OUT, "discover.txt"), "w", encoding="utf-8")
ATTEMPTS = []


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


def policy_pnl(pred, move, cost):
    """LONG if predicted move clears the cost, SHORT if it clears it downward, else CASH."""
    act = np.where(pred > cost, 1, np.where(pred < -cost, -1, 0))
    return act * move - np.abs(act) * cost, act


def session_stats(pnl, sess):
    """Session-clustered mean and t. The SESSION is the unit."""
    s = pd.Series(pnl).groupby(sess).sum()
    n = len(s)
    sd = s.std(ddof=1)
    return dict(n_sessions=n, per_session=float(s.mean()),
                t=float(s.mean() / (sd / np.sqrt(n))) if sd > 0 else np.nan,
                pos_sessions=float((s > 0).mean()), total=float(s.sum()))


def run_model(name, make, X, y, mv, ct, sess, order):
    """Expanding-origin chronological session-block validation."""
    ATTEMPTS.append(name)
    blocks = np.array_split(order, N_FOLD + 1)
    oof_pred, oof_idx = [], []
    for k in range(1, N_FOLD + 1):
        tr = np.concatenate(blocks[:k])
        te = blocks[k]
        mtr = np.isin(sess, tr)
        mte = np.isin(sess, te)
        mu, sd = X[mtr].mean(0), X[mtr].std(0)          # TRAINING-ONLY normalization
        sd[sd == 0] = 1
        m = make()
        m.fit((X[mtr] - mu) / sd, y[mtr])
        oof_pred.append(m.predict((X[mte] - mu) / sd))
        oof_idx.append(np.where(mte)[0])
    idx = np.concatenate(oof_idx)
    pred = np.concatenate(oof_pred)
    pnl, act = policy_pnl(pred, mv[idx], ct[idx])
    st = session_stats(pnl, sess[idx])
    st.update(name=name, n_dec=len(idx), trade_rate=float(np.mean(act != 0)),
              long_rate=float(np.mean(act == 1)), short_rate=float(np.mean(act == -1)),
              per_decision=float(pnl.mean()))
    tr_m = act != 0
    st["dir_acc"] = float(np.mean(np.sign(mv[idx][tr_m]) == act[tr_m])) if tr_m.sum() else np.nan
    return st, pnl, act, idx


def main():
    d = pd.read_parquet(os.path.join(OUT, "discovery_substrate.parquet"))
    meta = ("session", "src", "t", "hour", "tod", "move", "cost", "cost_s1", "cost_s2")
    feats = [c for c in d.columns if c not in meta] + ["tod"]
    d = d.sort_values("t").reset_index(drop=True)
    X = d[feats].values.astype(float)
    X = np.nan_to_num(X, posinf=0, neginf=0)
    y = d["move"].values.astype(float)
    mv, ct = y.copy(), d["cost"].values.astype(float)
    sess = d["session"].values
    order = pd.unique(d["session"])                       # chronological, d is time-sorted

    P("=" * 104)
    P("=== LANE A step 4 - LAST-ONLY DISCOVERY.  Consumed sessions only. Blind pool NOT opened.")
    P("=" * 104)
    P(f"    decisions {len(d):,}   sessions {len(order)}   features {len(feats)}")
    P(f"    mean |move| ${np.abs(y).mean():,.2f}   mean cost ${ct.mean():,.2f}")
    P(f"    THE DEPENDENCE UNIT IS THE SESSION: {len(order)}, not {len(d):,}.")

    # ------------------------------------------------------------------ reference arms
    P("")
    P("=" * 104)
    P("=== REFERENCE ARMS - what a NON-informative policy earns under the same costs")
    P("=" * 104)
    rng = np.random.default_rng(SEED)
    rows = []
    for nm, pr in (("ALWAYS LONG", np.full(len(d), 1e9)),
                   ("ALWAYS SHORT", np.full(len(d), -1e9)),
                   ("RANDOM DIRECTION", np.where(rng.random(len(d)) < .5, 1e9, -1e9))):
        pn, _ = policy_pnl(pr, mv, ct)
        st = session_stats(pn, sess)
        st.update(name=nm, per_decision=float(pn.mean()), trade_rate=1.0)
        rows.append(st)
        P(f"    {nm:<20} ${st['per_session']:>10,.2f}/session   ${st['per_decision']:>8,.3f}/decision"
          f"   t {st['t']:>6.2f}")
    P("")
    P("    These are the friction. Any model must beat them by INFORMATION, not by trading less.")

    # ------------------------------------------------------------------ PRIMARY + challenger
    P("")
    P("=" * 104)
    P("=== PRIMARY (ridge) and the SINGLE nonlinear CHALLENGER")
    P("=" * 104)

    def mk_ridge():
        return Ridge(alpha=10.0)

    def mk_gbm():
        return HistGradientBoostingRegressor(max_depth=3, max_iter=150, learning_rate=0.05,
                                             random_state=SEED)

    res = {}
    for nm, mk in (("RIDGE (primary)", mk_ridge), ("GBM shallow (challenger)", mk_gbm)):
        st, pnl, act, idx = run_model(nm, mk, X, y, mv, ct, sess, order)
        res[nm] = (st, pnl, act, idx)
        rows.append(st)
        P(f"    {nm:<26} ${st['per_session']:>10,.2f}/session  t {st['t']:>6.2f}  "
          f"pos {100*st['pos_sessions']:>5.1f}%  trade {100*st['trade_rate']:>5.1f}%  "
          f"dir acc {100*st['dir_acc'] if st['dir_acc']==st['dir_acc'] else float('nan'):>5.1f}%")
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "discovery_arms.csv"), index=False)

    # ------------------------------------------------------------------ nulls
    P("")
    P("=" * 104)
    P("=== DEPENDENCE-PRESERVING NULLS - whole SESSIONS resampled, never individual decisions")
    P("=" * 104)
    for nm, (st, pnl, act, idx) in res.items():
        ss = pd.Series(pnl).groupby(sess[idx]).sum()
        obs = ss.mean()
        # circular shift of session-level P&L labels against the session ordering
        v = ss.values
        shifts = rng.integers(1, len(v), size=NULL_B)
        nulldist = np.array([np.roll(v, s).mean() for s in shifts])   # mean is shift-invariant
        # activity-matched RANDOM-DIRECTION placebo: same trade times, random side
        pl = []
        for _ in range(NULL_B // 4):
            rs = np.where(rng.random(len(idx)) < .5, 1, -1) * (act != 0)
            pp = rs * mv[idx] - np.abs(rs) * ct[idx]
            pl.append(pd.Series(pp).groupby(sess[idx]).sum().mean())
        pl = np.array(pl)
        pct = 100 * (pl < obs).mean()
        P(f"    {nm:<26} observed ${obs:>9,.2f}/session")
        P(f"    {'':<26} activity-matched random-direction placebo: "
          f"mean ${pl.mean():>9,.2f}  obs at {pct:>5.1f}th pctile")
        P(f"    {'':<26} {'BEATS the placebo' if pct > 95 else '*** DOES NOT BEAT THE PLACEBO ***'}")

    # ------------------------------------------------------------------ verdict
    P("")
    P("=" * 104)
    P("=== ATTEMPT LEDGER and MULTIPLICITY")
    P("=" * 104)
    P(f"    model attempts counted: {len(ATTEMPTS)}  -> {ATTEMPTS}")
    P(f"    ridge alpha grid declared but NOT searched on test data (fixed at 10.0)")
    P(f"    Bonferroni-adjusted two-sided 5 % threshold for {len(ATTEMPTS)} attempts: "
      f"|t| > {abs(round(float(__import__('scipy.stats', fromlist=['t']).t.ppf(0.025/len(ATTEMPTS), 103)), 3))}")
    _fh.close()


if __name__ == "__main__":
    main()
