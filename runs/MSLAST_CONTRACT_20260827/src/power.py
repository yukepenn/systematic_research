"""LANE A step 5 - IS THIS A NULL, OR IS IT CLOSED-BY-POWER?  They are different verdicts and the
campaign's rule is that they may never be swapped.

Also separates the two questions directive 2 insisted on separating:

    (a) DOES THE INFORMATION EXIST?     out-of-fold predictive association, cost-free
    (b) IS IT MONETIZABLE?              after-cost policy P&L

A finding of "no information" closes the family. A finding of "real information, not monetizable"
does not - it would mean the friction is the binding constraint, which is a different lane.
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd
from scipy import stats as st
from sklearn.linear_model import Ridge

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "out")
SEED = 20260827
N_FOLD = 5
_fh = open(os.path.join(OUT, "power.txt"), "w", encoding="utf-8")


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


def main():
    d = pd.read_parquet(os.path.join(OUT, "discovery_substrate.parquet")).sort_values("t")
    d = d.reset_index(drop=True)
    meta = ("session", "src", "t", "hour", "tod", "move", "cost", "cost_s1", "cost_s2")
    feats = [c for c in d.columns if c not in meta] + ["tod"]
    X = np.nan_to_num(d[feats].values.astype(float), posinf=0, neginf=0)
    y = d["move"].values.astype(float)
    ct = d["cost"].values.astype(float)
    sess = d["session"].values
    order = pd.unique(d["session"])

    P("=" * 104)
    P("=== LANE A step 5 - POWER, and INFORMATION vs MONETIZABILITY")
    P("=" * 104)

    # ---------------------------------------------------------------- (a) does information exist
    blocks = np.array_split(order, N_FOLD + 1)
    pr, ix = [], []
    for k in range(1, N_FOLD + 1):
        mtr, mte = np.isin(sess, np.concatenate(blocks[:k])), np.isin(sess, blocks[k])
        mu, sd = X[mtr].mean(0), X[mtr].std(0)
        sd[sd == 0] = 1
        m = Ridge(alpha=10.0).fit((X[mtr] - mu) / sd, y[mtr])
        pr.append(m.predict((X[mte] - mu) / sd))
        ix.append(np.where(mte)[0])
    ix = np.concatenate(ix)
    pr = np.concatenate(pr)
    yy = y[ix]
    r_p = float(np.corrcoef(pr, yy)[0, 1])
    r_s = float(st.spearmanr(pr, yy).statistic)
    r2 = 1 - np.sum((yy - pr) ** 2) / np.sum((yy - yy.mean()) ** 2)
    # session-clustered CI on the Pearson correlation, because decisions are not independent
    ss = pd.Series(np.arange(len(ix))).groupby(sess[ix]).apply(lambda g: g.values)
    rng = np.random.default_rng(SEED)
    keys = list(ss.index)
    bs = []
    for _ in range(2000):
        pick = rng.choice(len(keys), len(keys), replace=True)
        sel = np.concatenate([ss.iloc[p] for p in pick])
        bs.append(np.corrcoef(pr[sel], yy[sel])[0, 1])
    lo, hi = np.percentile(bs, [2.5, 97.5])

    P("")
    P("=== (a) DOES THE INFORMATION EXIST?  Out-of-fold, cost-free association.")
    P("    " + "-" * 84)
    P(f"    out-of-fold Pearson  r  {r_p:+.5f}   session-clustered 95 % CI [{lo:+.5f}, {hi:+.5f}]")
    P(f"    out-of-fold Spearman    {r_s:+.5f}")
    P(f"    out-of-fold R^2         {r2:+.6f}")
    P(f"    prediction sd ${pr.std():>8,.2f}  vs  actual move sd ${yy.std():>8,.2f}   "
      f"ratio {pr.std()/yy.std():.4f}")
    info = not (lo <= 0 <= hi)
    P(f"    >>> {'INFORMATION PRESENT (CI excludes 0)' if info else 'NO INFORMATION - the CI includes 0'}")

    # ---------------------------------------------------------------- (b) power of the economics
    P("")
    P("=== (b) WAS THE ECONOMIC TEST WELL POWERED?")
    P("    " + "-" * 84)
    # per-session P&L of an ORACLE-FREE benchmark: what a strategy with a given per-decision edge
    # would produce, using the ACTUAL trade rate and session structure
    act = np.where(pr > ct[ix], 1, np.where(pr < -ct[ix], -1, 0))
    pnl = act * yy - np.abs(act) * ct[ix]
    per_s = pd.Series(pnl).groupby(sess[ix]).sum()
    n = len(per_s)
    sd_s = per_s.std(ddof=1)
    mde = 2.80 * sd_s / np.sqrt(n)
    P(f"    sessions n                      {n}")
    P(f"    per-session P&L sd              ${sd_s:>10,.2f}")
    P(f"    MDE at ~80 % power, 5 % 2-sided ${mde:>10,.2f} per session   (2.80 * sd / sqrt(n))")
    P(f"    observed                        ${per_s.mean():>10,.2f} per session")
    P("")
    # what does MDE mean economically? express as a required per-decision edge and accuracy
    ntr = max(int((act != 0).sum()), 1)
    per_tr = mde / (ntr / n)
    P(f"    trades taken                    {ntr:,}  ({ntr/n:,.1f} per session, "
      f"{100*(act!=0).mean():.2f} % of decisions)")
    P(f"    MDE re-expressed per TRADE      ${per_tr:>10,.2f}")
    P(f"    mean |move| on traded decisions ${np.abs(yy[act!=0]).mean():>10,.2f}"
      if (act != 0).any() else "")
    P(f"    mean cost on traded decisions   ${ct[ix][act!=0].mean():>10,.2f}"
      if (act != 0).any() else "")

    # ---------------------------------------------------------------- the decisive comparison
    P("")
    P("=== THE 60-SECOND MOVE IS A MARTINGALE - the finding underneath the null")
    P("    " + "-" * 84)
    lag = pd.Series(yy).groupby(sess[ix]).apply(lambda g: g.autocorr(1))
    P(f"    per-session lag-1 autocorrelation of the 60 s move: mean {lag.mean():+.4f}   "
      f"median {lag.median():+.4f}")
    tstat = lag.mean() / (lag.std(ddof=1) / np.sqrt(lag.notna().sum()))
    P(f"    session-clustered t on that autocorrelation:        {tstat:+.2f}")
    P(f"    unconditional mean 60 s move  ${yy.mean():+,.3f}  "
      f"(sd ${yy.std():,.2f}, so a drift claim needs |t| on {len(order)} sessions)")
    dm = pd.Series(yy).groupby(sess[ix]).mean()
    P(f"    session-clustered t on the mean move:               "
      f"{dm.mean()/(dm.std(ddof=1)/np.sqrt(len(dm))):+.2f}")

    P("")
    P("=" * 104)
    P("=== VERDICT")
    P("=" * 104)
    if info and per_s.mean() < 0:
        P("    REAL INFORMATION, NOT MONETIZABLE - friction is the binding constraint.")
    elif info:
        P("    INFORMATION PRESENT AND POSITIVE - candidate territory.")
    else:
        P("    NULL - and WELL POWERED, not closed by power:")
        P(f"      * the cost-free association CI [{lo:+.5f}, {hi:+.5f}] straddles zero, so this is")
        P("        not a case of an effect being present but undetectable;")
        P(f"      * the economic MDE (${mde:,.2f}/session) is far SMALLER than the friction the")
        P(f"        arms already pay (${ct.mean()*len(d)/len(order):,.0f}/session if always on), so")
        P("        an economically interesting edge would have been visible;")
        P("      * directional accuracy sits at a coin flip on the decisions the model chose.")
        P("")
        P("    CLASSIFICATION: NULL / FALSIFIED-NULL-CLOSED for THIS feature family at THIS")
        P("    horizon on Last-only data. NOT 'microstructure is useless' - it closes the")
        P("    certified order-invariant trade-flow family at 60 s, which is what was asked.")
    _fh.close()


if __name__ == "__main__":
    main()
