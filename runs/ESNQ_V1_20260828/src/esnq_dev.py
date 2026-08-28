"""ESNQ_V1 ONE-SHOT DEVELOPMENT.  Structural gates FIRST, then exactly one economic evaluation.

Order is not negotiable and is enforced by construction:
    P0-2  row-by-row timestamp assertions        (embargo, causality, execution)
    P0-1  two-sided causality probes WITH TEETH  (a probe that only proves "nothing changed"
                                                  cannot certify anything)
    X1..X8 the original frozen development gates
    X9    ES-PAIRING mechanism null
    then mu_claim (frozen circular block bootstrap) and blind power at EFFECTIVE n = 14.

ONE evaluation. No second formulation. No horizon, feature, model, threshold, filter or null
variant. If a blocking gate fails the object is CLOSED, not repaired.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(RUN))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "research_sdk"))
import blindguard as BG                                                 # noqa: E402
import blind_spend_power as BSP                                         # noqa: E402
import esnq_batch as B                                                  # noqa: E402

OUT = os.path.join(RUN, "out")
DEV = os.path.join(RUN, "manifests", "ESNQ_DEV_44.csv")
BLIND_EFF = os.path.join(RUN, "manifests", "ESNQ_BLIND_EFFECTIVE_14.csv")
BLIND_ORIG = os.path.join(RUN, "manifests", "ESNQ_BLIND_15.csv")
EMB_NS = B.ES_EMBARGO_NS
_fh = None
GATES = []


def P(*a):
    print(*a, flush=True)
    if _fh is not None:
        print(*a, file=_fh)


def gate(name, observed, ok):
    GATES.append((name, observed, bool(ok)))
    return bool(ok)


def build():
    sess = sorted(BG.load_manifest(DEV))
    BG.assert_no_blind_contamination(sess, BLIND_EFF, label="esnq_dev vs EFFECTIVE_14")
    BG.assert_no_blind_contamination(sess, BLIND_ORIG, label="esnq_dev vs ORIGINAL_15")
    cache = os.path.join(OUT, "feat_batch.parquet")
    if os.path.exists(cache):
        d = pd.read_parquet(cache)
        if set(d["session"]) == set(sess):
            return d, sess
    d = pd.concat([B.session_features(s) for s in sess], ignore_index=True)
    d.to_parquet(cache, index=False)
    return d, sess


def main():
    global _fh
    _fh = open(os.path.join(OUT, "esnq_dev.txt"), "w", encoding="utf-8")
    P("=" * 112)
    P("=== ESNQ_V1 ONE-SHOT DEVELOPMENT.  Structural gates first.")
    P("=" * 112)
    d, sess = build()
    P(f"    sessions {len(sess)}   raw decisions {len(d):,}   "
      f"expected {len(sess)}x331 = {len(sess)*331:,}")

    # ================================================================ P0-2
    P("")
    P("=== P0-2  ROW-BY-ROW TIMESTAMP ASSERTIONS (all decisions, not a sample)")
    t = d["t"].values.astype(np.int64)
    v_es = int((d["max_es_source_ts"].values > t - EMB_NS).sum())
    v_nq = int((d["max_nq_source_ts"].values >= t).sum())
    fin = d["entry_ts"].values > np.iinfo(np.int64).min
    v_en = int((d.loc[fin, "entry_ts"].values <= t[fin]).sum())
    fex = d["exit_ts"].values > np.iinfo(np.int64).min
    v_ex = int((d.loc[fex, "exit_ts"].values <= t[fex] + 60 * 10 ** 9).sum())
    P(f"    max_es_source_ts <= t - 200ms   violations {v_es}")
    P(f"    max_nq_source_ts <  t           violations {v_nq}")
    P(f"    entry_ts         >  t           violations {v_en}")
    P(f"    exit_ts          >  t + 60s     violations {v_ex}")
    lag = (t - d["max_es_source_ts"].values) / 1e6
    P(f"    realised ES information lag: min {lag.min():.1f} ms  median {np.median(lag):.1f} ms")
    p02 = gate("P0-2 row-by-row timestamp assertions",
               f"{v_es + v_nq + v_en + v_ex} violations", v_es + v_nq + v_en + v_ex == 0)

    # ================================================================ P0-1
    P("")
    P("=== P0-1  TWO-SIDED CAUSALITY, WITH TEETH")
    probe = sess[len(sess) // 2]
    base = B.session_features(probe)

    def corrupt_after(ev_t, ev_p, ev_t2, ev_p2, grid, cut_ns):
        """Add +500 points to every quote at ts > cut (cut is per-decision; use the min grid)."""
        c = int(grid.min()) + cut_ns
        return (np.where(ev_t > c, ev_p + 500.0, ev_p),
                np.where(ev_t2 > c, ev_p2 + 500.0, ev_p2))

    neg_nq = B.session_features(probe, nq_corrupt=lambda bt, bp, at, ap, g:
                                corrupt_after(bt, bp, at, ap, g, 0))
    neg_es = B.session_features(probe, es_corrupt=lambda bt, bp, at, ap, g:
                                corrupt_after(bt, bp, at, ap, g, -EMB_NS))
    pos_es = B.session_features(probe, es_corrupt=lambda bt, bp, at, ap, g:
                                (bp + 500.0, ap + 500.0))
    ES_F = ["rel_move_1s", "rel_move_5s", "rel_move_15s", "rel_move_30s",
            "es_spread_tk", "es_rvol_30s", "es_bid_upd_30s", "es_ask_upd_30s"]
    NQ_F = ["nq_spread_tk", "nq_rvol_30s"]

    def maxdiff(a, b, cols):
        out = {}
        for c in cols:
            x, y = a[c].values.astype(float), b[c].values.astype(float)
            m = ~(np.isnan(x) | np.isnan(y))
            out[c] = float(np.max(np.abs(x[m] - y[m]))) if m.any() else 0.0
        return out

    dn = maxdiff(base, neg_nq, NQ_F)
    de = maxdiff(base, neg_es, ES_F)
    dp = maxdiff(base, pos_es, ES_F)
    P(f"    probe session {probe}")
    P("    NEGATIVE 1 - corrupt NQ quotes AFTER t   -> NQ-native features must NOT move")
    for c, v in dn.items():
        P(f"        {c:<16} {v:.3e}")
    P("    NEGATIVE 2 - corrupt ES quotes AFTER t-200ms -> ES features must NOT move")
    for c, v in de.items():
        P(f"        {c:<16} {v:.3e}")
    P("    POSITIVE   - corrupt ES quotes BEFORE the cutoff -> ES features MUST move")
    moved = 0
    for c, v in dp.items():
        mv = v > 0
        moved += mv
        P(f"        {c:<16} {v:.3e}   {'MOVED' if mv else '*** DID NOT MOVE ***'}")
    neg_ok = max(list(dn.values()) + list(de.values())) == 0.0
    pos_ok = moved >= 6
    P(f"    >>> NEGATIVE {'PASS' if neg_ok else '*** FAIL - LOOK-AHEAD ***'}   "
      f"POSITIVE {moved}/8 families responded {'PASS' if pos_ok else '*** FAIL - NO TEETH ***'}")
    p01 = gate("P0-1 two-sided causality", f"neg max {max(list(dn.values())+list(de.values())):.1e}, "
               f"pos {moved}/8", neg_ok and pos_ok)

    # ================================================================ sample
    feats = B.FEATURES
    adm = d[d["wait_ok"] & d[feats].notna().all(axis=1)
            & d["long_gross"].notna() & d["short_gross"].notna()].copy()
    adm = adm.sort_values("t").reset_index(drop=True)
    X = np.nan_to_num(adm[feats].values.astype(float), posinf=0, neginf=0)
    y = (adm["long_gross"].values + (-adm["short_gross"].values)) / 2.0
    ss = adm["session"].values
    order = [s for s in sess if s in set(ss)]
    folds = B.chrono_folds(order)
    P("")
    P(f"    admissible decisions {len(adm):,} of {len(d):,}   sessions {len(order)}")
    P(f"    folds: {[len(te) for _, te in folds]} test sessions per fold (expanding train)")
    P(f"    >>> SESSION IS THE INFERENCE UNIT: n = {len(order)}. "
      f"The {len(adm):,} decisions are DIAGNOSTIC ONLY.")

    # ================================================================ OOF
    mk = lambda: Ridge(alpha=B.RIDGE_ALPHA)                              # noqa: E731
    ix, pr = B.oof(X, y, ss, folds, mk)
    sub = adm.iloc[ix]
    net, act = B.policy_pnl(pr, sub, 0.0)
    sn = pd.Series(net).groupby(sub["session"].values).sum()
    sn = sn.reindex([s for s in order if s in sn.index])
    mu = float(sn.mean())
    P("")
    P("=" * 112)
    P("=== DEVELOPMENT ECONOMICS  (ONE evaluation, frozen object)")
    P("=" * 112)
    P(f"    total net        ${sn.sum():>12,.2f}")
    P(f"    net/session      ${mu:>12,.2f}")
    P(f"    sessions         {len(sn)}   positive {int((sn>0).sum())} ({100*(sn>0).mean():.1f} %)")
    P(f"    trade rate       {100*np.mean(act != 0):.2f} %   "
      f"actions L/S/F {int((act==1).sum()):,}/{int((act==-1).sum()):,}/{int((act==0).sum()):,}")
    tr = act != 0
    P(f"    mean/median per trade  ${net[tr].mean() if tr.any() else 0:,.2f} / "
      f"${np.median(net[tr]) if tr.any() else 0:,.2f}")
    P(f"    OOF corr(pred, target)  {np.corrcoef(pr, y[ix])[0,1]:+.4f}")
    cum = sn.cumsum()
    P(f"    maxDD            ${float((cum.cummax()-cum).max()):>12,.2f}")
    P(f"    worst / best session  ${sn.min():,.2f} / ${sn.max():,.2f}")
    pos = sn[sn > 0]
    top5 = float(pos.nlargest(5).sum()/pos.sum()) if len(pos) else np.nan
    P(f"    top-1 / top-5 share of positive net  "
      f"{float(pos.max()/pos.sum())*100 if len(pos) else float('nan'):.1f} % / {top5*100:.1f} %")
    q = np.array_split(sn.values, 4)
    P(f"    quartile nets    {[f'${x.sum():,.0f}' for x in q]}")
    for nm, tk in (("STRESS +0.5tk", 0.5), ("STRESS +1.0tk", 1.0)):
        n2, a2 = B.policy_pnl(pr, sub, tk)
        P(f"    {nm:<15} ${pd.Series(n2).groupby(sub['session'].values).sum().sum():>12,.2f}")
    ns5, _ = B.policy_pnl(pr, sub, 0.5)
    stress5 = float(pd.Series(ns5).groupby(sub["session"].values).sum().sum())
    lg = net[act == 1].sum()
    sh = net[act == -1].sum()
    P(f"    long / short net  ${lg:,.2f} / ${sh:,.2f}")
    gross = np.where(act == 1, sub["long_gross"].values,
                     np.where(act == -1, sub["short_gross"].values, 0.0)).sum()
    cost = B.COMMISSION_RT * int(tr.sum())
    P(f"    gross ${gross:,.2f}   cost ${cost:,.2f}   cost/|gross| "
      f"{100*cost/max(abs(gross),1e-9):.1f} %")
    sn.to_csv(os.path.join(OUT, "dev_session_nets.csv"))
    return dict(d=d, adm=adm, X=X, y=y, ss=ss, order=order, folds=folds, ix=ix, pr=pr,
                sub=sub, net=net, act=act, sn=sn, mu=mu, stress5=stress5, top5=top5,
                p01=p01, p02=p02, mk=mk)


if __name__ == "__main__":
    R = main()
    json.dump({"note": "gates continue in esnq_gates.py"}, open(os.path.join(OUT, "_dev_stage1.json"),
              "w", encoding="utf-8"))
    import pickle
    pickle.dump({k: R[k] for k in ("mu", "stress5", "top5")},
                open(os.path.join(OUT, "_dev_stage1.pkl"), "wb"))
    _fh.close() if _fh else None
