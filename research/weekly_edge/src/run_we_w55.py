"""WE_W55 phase 1 - RESOLVE THE CONTRADICTION before spending a backtest.

W54 measured that trades held under 37 minutes cost -15.02 pts/session and are 55 % of all
trades, and that duration is strongly forecastable at entry (runlen Spearman 0.404). It also
measured that the SAME features carry no positive information about P&L (runlen -0.101), even
though realised duration and realised P&L are almost perfectly monotone in each other.

At most two of those three statements can be simple. This script decides which, with exact
accounting and a preregistered STOPPING RULE: if no causal feature bucket refuses entries that
are materially negative PER UNIT, the wave stops here and records the honest conclusion.

Nothing is adopted in this file and no arm is built.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT, PV                                          # noqa: E402
from run_we_w19 import MEMBERS, QS                                       # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w38 import targets, vote                                     # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w51 import session_frames, A, B                              # noqa: E402
from run_we_w51c import setup                                            # noqa: E402
from we_features import build_universe                                   # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W55_DURATION", "out")
os.makedirs(OUT, exist_ok=True)
NB = 5                    # causal-rank buckets
HIST = 250                # trailing entries used for the causal rank


def main():
    t0 = _time.time()
    D, X, TG, st, en = setup()
    n, tarr, sid = D["n"], D["t"], D["sid"]
    out = open(os.path.join(OUT, "duration2.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    sess_in = np.array([s for s in range(D["n_sess"]) if A <= tarr[st[s]] < B])
    NS = len(sess_in)
    in_win = np.zeros(D["n_sess"], bool); in_win[sess_in] = True

    def build(pos, sizing=True):
        base = fills_daily(D, pos, halt=1300, target=1000)
        ent = np.array([i_of(x["et"]) for x in base if A <= np.datetime64(x["et"]) < B])
        sc, _ = causal_score(X, ent, window=WIN)
        sz = (np.where(sc >= 3, 2, 1) if sizing else np.ones(n)).astype(np.int8)
        return [x for x in fills_qexit(D, pos, sz, sc)
                if in_win[int(sid[i_of(x["et"])])]]

    posL = (vote(TG, D, X, +1) >= 0.5).astype(np.int8)
    trs = build(posL)
    trs1 = build(posL, sizing=False)
    pts = sum(x["pnl"] for x in trs) / PV / NS
    P_(f"=== B1 GATE: {pts:.2f} pts/session over {NS} sessions (expect 14.72) -> "
       f"{'PASS' if abs(pts - 14.72) < 0.6 else 'FAIL - VOID'} [{_time.time()-t0:.0f}s]")
    if abs(pts - 14.72) >= 0.6:
        out.close(); return

    # ---------------- the feature universe available AT ENTRY ---------------------------
    F, _C = build_universe(D)
    nMem = np.zeros(n, np.int16)
    for mem in MEMBERS:
        nMem += (TG[mem] > 0).astype(np.int16)
    nThr = np.zeros(n, np.int16)
    for q in QS:
        ok = np.ones(n, bool) if q is None else ((X["norm"] <= 0) | (X["ratio"] >= q))
        nThr += ok.astype(np.int16)
    prod = nMem.astype(float) * nThr.astype(float) * (1 + X["dL"].astype(float))
    vote_margin = np.concatenate([[0.0], prod[:-1]])       # lagged to the entry bar
    FEATS = {"runlen": X["runlen"], "delta_mag": X["delta_mag"], "dist_open": X["dist_open"],
             "dist_vwap": X["dist_vwap"], "ratio": X["ratio"], "prev_ret": X["prev_ret"],
             "atr_l": X["atr_l"], "vote_margin": vote_margin,
             "churn60": F["churn60"], "path_eff": F["path_eff"],
             "bar_range_rel": F["bar_range_rel"], "mom_align": F["mom_align"],
             "rv_expansion": F["rv_expansion"], "bars_since_open": F["bars_since_open"],
             "sess_extension": F["sess_extension"], "or_pos": F["or_pos"]}

    def frame(trades):
        ei = np.array([i_of(x["et"]) for x in trades])
        dur = np.array([(np.datetime64(x["xt"]) - np.datetime64(x["et"]))
                        / np.timedelta64(1, "m") for x in trades], float)
        u = np.array([x.get("u", 1) for x in trades], float)
        pnl = np.array([x["pnl"] for x in trades], float)
        return ei, dur, u, pnl, pnl / u
    ei, dur, u, pnl, per_unit = frame(trs)
    ei1, dur1, u1, pnl1, per_unit1 = frame(trs1)
    P_(f"   sized object {len(trs)} trades | flat-lot object {len(trs1)} trades "
       f"({sum(x['pnl'] for x in trs1)/PV/NS:.2f} pts/session)")

    # =====================================================================================
    # PHASE 1a / 1b - X1 (size confound) and X2 (non-monotonicity)
    # =====================================================================================
    P_(f"\n{'='*104}\n=== PHASE 1a: is the P&L column's flat correlation a SIZE confound? (X1)")
    P_(f"{'='*104}")
    P_(f"{'feature at entry':<20}{'rho vs dur':>12}{'rho vs $ (sized)':>18}"
       f"{'rho vs $ PER UNIT':>19}{'rho vs $ flat-lot obj':>23}")

    def sp(a, b):
        ok = np.isfinite(a) & np.isfinite(b)
        return float(pd.Series(a[ok]).corr(pd.Series(b[ok]), method="spearman"))
    rows = []
    for k, arr in FEATS.items():
        v, v1 = arr[ei], arr[ei1]
        r = dict(feature=k, rho_dur=sp(v, dur), rho_sized=sp(v, pnl),
                 rho_unit=sp(v, per_unit), rho_flat=sp(v1, pnl1),
                 rho_dur_flat=sp(v1, dur1))
        rows.append(r)
        P_(f"{k:<20}{r['rho_dur']:>12.3f}{r['rho_sized']:>18.3f}{r['rho_unit']:>19.3f}"
           f"{r['rho_flat']:>23.3f}")
    R = pd.DataFrame(rows)
    R.to_csv(os.path.join(OUT, "contradiction.csv"), index=False)
    d_max = R["rho_unit"].abs().max()
    P_(f"\n   X1 verdict: per-unit correlations are "
       + ("MATERIALLY different from sized ones - the size confound is real"
          if (R["rho_unit"] - R["rho_sized"]).abs().max() > 0.05 else
          "essentially identical to sized ones - X1 is ELIMINATED")
       + f" (largest |rho| vs per-unit P&L = {d_max:.3f})")

    P_(f"\n{'='*104}\n=== PHASE 1b: is duration -> P&L monotone in the pairs or only in the means? (X2)")
    P_(f"{'='*104}")
    P_(f"   Spearman(duration, per-unit P&L) on raw pairs      : {sp(dur, per_unit):+.3f}")
    P_(f"   Spearman(duration, sized P&L)    on raw pairs      : {sp(dur, pnl):+.3f}")
    dq = np.quantile(dur, np.arange(0, 1.01, 0.1))
    dm, pm = [], []
    for k in range(10):
        m = (dur >= dq[k]) & (dur <= dq[k + 1]) if k == 9 else (dur >= dq[k]) & (dur < dq[k + 1])
        if m.any():
            dm.append(dur[m].mean()); pm.append(per_unit[m].mean())
    P_(f"   Spearman on the 10 DECILE MEANS                    : "
       f"{sp(np.array(dm), np.array(pm)):+.3f}")
    P_(f"   -> X2 verdict: "
       + ("the relation lives in the MEANS, not the pairs - a feature that predicts duration"
          " need not inherit it" if abs(sp(dur, per_unit)) < 0.5 else
          "the relation is strong pair-by-pair too"))
    P_(f"   per-unit P&L by size bucket: size 1 {per_unit[u == 1].mean():+,.0f} $ "
       f"({int((u == 1).sum())} trades) | size 2 {per_unit[u == 2].mean():+,.0f} $ "
       f"({int((u == 2).sum())} trades)")

    # =====================================================================================
    # PHASE 1c / 1d - THE GRID AND THE STOPPING RULE
    # =====================================================================================
    P_(f"\n{'='*104}\n=== PHASE 1c/1d: causal trailing-rank buckets - duration AND per-unit P&L")
    P_(f"{'='*104}")
    SHORT_MIN = 37.0        # W54's boundary: holds under 37 min cost -15.02 pts/session
    P_(f"Rank of each entry against the PRIOR {HIST} entries only. SHORT is defined as W54")
    P_(f"defined it - a hold under {SHORT_MIN:.0f} minutes - which W54 priced at -15.02 pts/session in")
    P_(f"aggregate across {100*float((dur < SHORT_MIN).mean()):.0f} % of all trades.\n")

    def causal_rank(v):
        r = np.full(len(v), np.nan)
        for j in range(HIST, len(v)):
            h = v[max(0, j - HIST):j]
            h = h[np.isfinite(h)]
            if len(h) >= 50 and np.isfinite(v[j]):
                r[j] = float((h < v[j]).mean())
        return r
    short = dur < SHORT_MIN
    best = []
    P_(f"{'feature':<18}{'bucket':>8}{'n':>7}{'mean dur':>10}{'P(short)':>10}"
       f"{'per-unit $':>12}{'total $':>12}{'pts/sess':>10}")
    for k, arr in FEATS.items():
        rk = causal_rank(arr[ei])
        ok = np.isfinite(rk)
        if ok.sum() < 500:
            continue
        for b in range(NB):
            hi = ((b + 1) / NB) if b < NB - 1 else 1.0001
            m = ok & (rk >= b / NB) & (rk < hi)
            if m.sum() < 60:
                continue
            row = dict(feature=k, bucket=b, n=int(m.sum()), dur=float(dur[m].mean()),
                       pshort=float(short[m].mean()), unit=float(per_unit[m].mean()),
                       tot=float(pnl[m].sum()), pts=float(pnl[m].sum() / PV / NS))
            best.append(row)
    Bf = pd.DataFrame(best)
    Bf.to_csv(os.path.join(OUT, "buckets.csv"), index=False)
    # print only the buckets that matter: the most negative per-unit bucket of each feature
    for k in FEATS:
        q = Bf[Bf["feature"] == k]
        if not len(q):
            continue
        w = q.loc[q["unit"].idxmin()]
        P_(f"{k:<18}{int(w['bucket']):>8}{int(w['n']):>7}{w['dur']:>10.0f}"
           f"{100*w['pshort']:>9.1f}%{w['unit']:>12,.0f}{w['tot']:>12,.0f}{w['pts']:>10.2f}")
    P_(f"\n   (the row shown per feature is that feature's WORST causal bucket by per-unit P&L)")

    base_short = float(short.mean())
    base_unit = float(per_unit.mean())
    P_(f"\n   baseline: P(short) = {100*base_short:.1f} %, mean per-unit P&L = "
       f"${base_unit:,.0f} over {len(trs)} trades")
    cand = Bf[(Bf["unit"] < 0) & (Bf["n"] >= 100)].sort_values("pts")

    # --- MULTIPLICITY, applied to phase 1's OWN scan (amendment_1) --------------------
    # Phase 1 is itself a scan: 16 features x 5 buckets. W53's rule says a scanned quantity
    # must be compared against a null that is scanned the same way. So: hold the bucket
    # memberships fixed, permute the per-unit P&L across entries, and ask how many negative
    # buckets and how negative a minimum a STRUCTURELESS assignment produces.
    P_(f"\n=== MULTIPLICITY CHECK on phase 1's own {len(Bf)}-bucket scan (amendment_1) ===")
    masks = []
    for _, w in Bf.iterrows():
        if w["n"] >= 100:
            rk = causal_rank(FEATS[w["feature"]][ei])
            b = int(w["bucket"])
            hi = ((b + 1) / NB) if b < NB - 1 else 1.0001
            masks.append(np.isfinite(rk) & (rk >= b / NB) & (rk < hi))
    RNG = np.random.default_rng(20260855)
    nneg, minmean = [], []
    for _ in range(500):
        p = RNG.permutation(per_unit)
        mm = np.array([p[m].mean() for m in masks])
        nneg.append(int((mm < 0).sum())); minmean.append(float(mm.min()))
    nneg = np.array(nneg); minmean = np.array(minmean)
    obs_n = int(len(cand))
    obs_min = float(cand["unit"].min()) if len(cand) else 0.0
    P_(f"   observed: {obs_n} negative buckets (n>=100), most negative ${obs_min:,.0f}/unit")
    P_(f"   permuted: {nneg.mean():.1f} negative buckets on average "
       f"(5th-95th pct {np.percentile(nneg,5):.0f}-{np.percentile(nneg,95):.0f}), "
       f"most negative ${minmean.mean():,.0f} on average "
       f"(5th pct ${np.percentile(minmean,5):,.0f})")
    p_n = float((nneg >= obs_n).mean())
    p_min = float((minmean <= obs_min).mean())
    P_(f"   p(as many negative buckets by chance) = {p_n:.3f}   "
       f"p(one as negative by chance) = {p_min:.3f}")
    survives = (p_n < 0.05) or (p_min < 0.05)
    P_(f"   -> {'SURVIVES multiplicity' if survives else 'DOES NOT SURVIVE - chance produces this or more'}")
    if not survives:
        cand = cand.iloc[0:0]
    P_(f"\n=== THE PREREGISTERED STOPPING RULE ===")
    if not len(cand):
        P_("   NO causal bucket of >= 100 entries has negative per-unit P&L.")
        P_("   -> X3 RECORDED: the -15.02 is not reachable through these features. The wave")
        P_("      STOPS at phase 1. Duration is forecastable; profitability is not.")
    else:
        P_(f"   {len(cand)} causal buckets (n >= 100) have NEGATIVE per-unit P&L. The five that")
        P_(f"   cost the most, i.e. the best refusal candidates:")
        P_(f"{'feature':<18}{'bucket':>8}{'n':>7}{'P(short)':>10}{'per-unit $':>12}"
           f"{'pts/sess refused':>18}")
        for _, w in cand.head(5).iterrows():
            P_(f"{w['feature']:<18}{int(w['bucket']):>8}{int(w['n']):>7}"
               f"{100*w['pshort']:>9.1f}%{w['unit']:>12,.0f}{w['pts']:>18.2f}")
        tot = float(cand.head(5)["pts"].sum())
        P_(f"\n   -> phase 2 is AUTHORISED. Naive upper bound if all five were refused with no")
        P_(f"      side effects: {-tot:+.2f} pts/session. That is NOT an achievable result -")
        P_(f"      the buckets overlap, refusing an entry changes the session box and the")
        P_(f"      trailing quantile pool, and the nulls have not been run.")
    P_(f"\n=== STATUS: diagnostic, nothing adopted, no arm built. ===")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
