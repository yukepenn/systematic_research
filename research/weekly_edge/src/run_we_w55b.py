"""WE_W55 phase 2 (amendment_2) - the MULTIVARIATE causal model phase 1 never tested.

Phase 1 tested sixteen features ONE AT A TIME against a per-trade target and stopped. That
licenses "no single feature predicts per-unit P&L above |rho| 0.11". It does NOT license
"there is no information" - multivariate combinations, interactions and a different target
were never tried, and the prize is unchanged: trades held under 37 minutes cost -15.02
pts/session and are 60 % of all trades.

The danger is named in the amendment and it governs the whole file: 1,942 entries, 16 features,
and I already know the answer I want. So the binding null is LABEL PERMUTATION - the same
fitting procedure run on shuffled labels. A model that cannot beat its own procedure on noise
is a description of the sample, not a finding.

Reported against the owner's actual objective: consistency first, Sharpe demoted.
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
from run_we_w51c import setup, dd_profile                                # noqa: E402
from we_features import build_universe                                   # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W55_DURATION", "out")
os.makedirs(OUT, exist_ok=True)
MINHIST = 500            # entries before the model may predict
TRAIN = 750             # trailing entries in the training window
REFIT = 50              # refit cadence, in entries
LAM = 10.0              # ridge penalty on standardised features
RATES = (0.05, 0.10, 0.15, 0.20, 0.25, 0.30)      # blocking-rate grid (scan-matched)
NDRAW = 200
SHORT_MIN = 37.0
RNG = np.random.default_rng(20260855)


def ridge_fit(Xt, yt, lam=LAM):
    Xa = np.hstack([Xt, np.ones((len(Xt), 1))])
    G = Xa.T @ Xa + lam * np.eye(Xa.shape[1])
    G[-1, -1] -= lam                                # do not penalise the intercept
    try:
        return np.linalg.solve(G, Xa.T @ yt)
    except np.linalg.LinAlgError:
        return np.zeros(Xa.shape[1])


def ridge_pred(Xp, w):
    return np.hstack([Xp, np.ones((len(Xp), 1))]) @ w


def walk_forward_scores(F, y):
    """Causal predictions: at entry j the model saw only entries < j. Returns nan before MINHIST."""
    n = len(y)
    out = np.full(n, np.nan)
    w = None
    for j in range(MINHIST, n):
        if w is None or (j - MINHIST) % REFIT == 0:
            lo = max(0, j - TRAIN)
            Xt, yt = F[lo:j], y[lo:j]
            mu, sg = Xt.mean(0), Xt.std(0)
            sg = np.where(sg > 1e-12, sg, 1.0)
            w = ridge_fit((Xt - mu) / sg, yt - yt.mean())
            ctx = (mu, sg, yt.mean())
        mu, sg, ym = ctx
        out[j] = float(ridge_pred(((F[j:j + 1] - mu) / sg), w)[0] + ym)
    return out


def main():
    t0 = _time.time()
    D, X, TG, st, en = setup()
    n, tarr, sid = D["n"], D["t"], D["sid"]
    o, c = D["o"], D["c"]
    wkmap = {s: D["wk"][s] for s in range(D["n_sess"])}
    out = open(os.path.join(OUT, "w55b.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    sess_in = np.array([s for s in range(D["n_sess"]) if A <= tarr[st[s]] < B])
    NS = len(sess_in)
    in_win = np.zeros(D["n_sess"], bool); in_win[sess_in] = True
    sess_wk = np.array([wkmap[s] for s in range(D["n_sess"])])
    keys_w = sorted(set(sess_wk[sess_in]))
    wk_idx = np.array([keys_w.index(sess_wk[s]) for s in sess_in])
    NW = len(keys_w)

    def build(pos):
        base = fills_daily(D, pos, halt=1300, target=1000)
        e = np.array([i_of(x["et"]) for x in base if A <= np.datetime64(x["et"]) < B])
        if len(e) < 300:
            return None
        sc_, _ = causal_score(X, e, window=WIN)
        sz = np.where(sc_ >= 3, 2, 1).astype(np.int8)
        return [x for x in fills_qexit(D, pos, sz, sc_) if in_win[int(sid[i_of(x["et"])])]]

    posL = (vote(TG, D, X, +1) >= 0.5).astype(np.int8)
    trs = build(posL)
    pts = sum(x["pnl"] for x in trs) / PV / NS
    P_(f"=== B1 GATE: {pts:.2f} pts/session over {NS} sessions (expect 14.72) -> "
       f"{'PASS' if abs(pts - 14.72) < 0.6 else 'FAIL - VOID'} [{_time.time()-t0:.0f}s]")
    if abs(pts - 14.72) >= 0.6:
        out.close(); return

    # ---------------- stretches, so a blocked entry is DELETED and never delayed ----------
    want = np.zeros(n, np.int8); want[1:] = posL[:-1]; want[D["fb"]] = 0
    starts, ends = [], []
    for s in sess_in:
        a, b = st[s], en[s]
        w_ = want[a:b]
        d = np.diff(np.concatenate([[0], w_, [0]]))
        for u_, v_ in zip(np.where(d == 1)[0], np.where(d == -1)[0] - 1):
            starts.append(a + int(u_)); ends.append(a + int(v_))
    starts, ends = np.array(starts), np.array(ends)
    str_of_bar = np.full(n, -1, np.int64)
    for j in range(len(starts)):
        str_of_bar[starts[j]:ends[j] + 1] = j

    ei = np.array([i_of(x["et"]) for x in trs])
    dur = np.array([(np.datetime64(x["xt"]) - np.datetime64(x["et"]))
                    / np.timedelta64(1, "m") for x in trs], float)
    u = np.array([x.get("u", 1) for x in trs], float)
    pnl = np.array([x["pnl"] for x in trs], float)
    per_unit = pnl / u
    str_of_trade = str_of_bar[ei]

    # ---------------- the feature matrix, all 16, no in-sample selection -----------------
    F_, _C = build_universe(D)
    nMem = np.zeros(n, np.int16)
    for mem in MEMBERS:
        nMem += (TG[mem] > 0).astype(np.int16)
    nThr = np.zeros(n, np.int16)
    for q in QS:
        ok = np.ones(n, bool) if q is None else ((X["norm"] <= 0) | (X["ratio"] >= q))
        nThr += ok.astype(np.int16)
    vm = np.concatenate([[0.0], (nMem.astype(float) * nThr.astype(float)
                                 * (1 + X["dL"].astype(float)))[:-1]])
    FEATS = {"runlen": X["runlen"], "delta_mag": X["delta_mag"], "dist_open": X["dist_open"],
             "dist_vwap": X["dist_vwap"], "ratio": X["ratio"], "prev_ret": X["prev_ret"],
             "atr_l": X["atr_l"], "vote_margin": vm, "churn60": F_["churn60"],
             "path_eff": F_["path_eff"], "bar_range_rel": F_["bar_range_rel"],
             "mom_align": F_["mom_align"], "rv_expansion": F_["rv_expansion"],
             "bars_since_open": F_["bars_since_open"], "sess_extension": F_["sess_extension"],
             "or_pos": F_["or_pos"]}
    FM = np.column_stack([np.nan_to_num(v[ei], nan=0.0, posinf=0.0, neginf=0.0)
                          for v in FEATS.values()])
    P_(f"   {len(trs)} entries x {FM.shape[1]} features | trailing train {TRAIN}, "
       f"refit every {REFIT}, ridge lambda {LAM}, no prediction before entry {MINHIST}")

    # ---------------- analytic evaluation, validated below --------------------------------
    sp_all = np.zeros(D["n_sess"])
    for x in trs:
        sp_all[int(sid[i_of(x["et"])])] += x["pnl"]
    sp0 = sp_all[sess_in]
    trade_sess = np.array([int(sid[e]) for e in ei])
    sess_pos = {s: k for k, s in enumerate(sess_in)}

    def analytic(block_mask):
        sp = sp0.copy()
        for k in np.flatnonzero(block_mask):
            sp[sess_pos[trade_sess[k]]] -= pnl[k]
        return sp

    def metrics(sp, name=""):
        v = np.bincount(wk_idx, weights=sp, minlength=NW)
        dp = dd_profile(v)
        k = 20245.0 / max(dp["maxdd"], 1e-9)
        vv = v * k
        spk = sp * k
        traded = sp != 0
        # longest losing streaks
        def streak(a):
            b_ = m_ = 0
            for z in a:
                b_ = b_ + 1 if z < 0 else 0
                m_ = max(m_, b_)
            return m_
        sd = vv.std(ddof=1)
        return dict(arm=name,
                    daypos=100 * float((sp > 0).mean()),
                    trdpos=100 * float((sp[traded] > 0).mean()) if traded.any() else 0.0,
                    wkpos=100 * float((v > 0).mean()),
                    dstreak=streak(sp), wstreak=streak(v),
                    medday=float(np.median(spk)), medwk=float(np.median(vv)),
                    weekly=float(vv.mean()), dd_top5=dp["dd_mean_top5"] * k,
                    ulcer=dp["ulcer"] * k, worst=float(vv.min()),
                    annshrp=float(vv.mean() / sd * np.sqrt(52)) if sd > 0 else 0.0,
                    ntr=int((sp != 0).sum()))
    HDR = (f"{'arm':<34}{'day+%':>7}{'trdD+%':>8}{'wk+%':>7}{'dStrk':>7}{'wStrk':>7}"
           f"{'medWk$':>9}{'weekly$':>10}{'top5DD':>9}{'ulcer':>8}{'worst$':>9}{'shrp':>7}")

    def show(r):
        P_(f"{r['arm']:<34}{r['daypos']:>7.1f}{r['trdpos']:>8.1f}{r['wkpos']:>7.1f}"
           f"{r['dstreak']:>7}{r['wstreak']:>7}{r['medwk']:>9,.0f}{r['weekly']:>10,.0f}"
           f"{r['dd_top5']:>9,.0f}{r['ulcer']:>8,.0f}{r['worst']:>9,.0f}{r['annshrp']:>7.2f}")
    base = metrics(sp0, "P1 INCUMBENT")

    # validate the analytic path against the full pipeline on one real arm
    P_(f"\n{'='*120}\n=== PHASE 2: three causal walk-forward models [{_time.time()-t0:.0f}s]")
    P_(f"{'='*120}")
    P_("All at a FIXED $20,245 max drawdown, so weekly$ is comparable across rows.")
    P_("Consistency first (Charter Amendment 2): Sharpe is a diagnostic and decides nothing.\n")
    TARGETS = {"M1 ridge on per-unit P&L": per_unit,
               "M2 logistic-ish on win/loss": (per_unit > 0).astype(float),
               "M3 on SHORT-trade label": -(dur < SHORT_MIN).astype(float)}
    P_(HDR)
    show(base)
    rows = [base]
    scores = {}
    for nm, y in TARGETS.items():
        s_ = walk_forward_scores(FM, y)
        scores[nm] = s_
        ok = np.isfinite(s_)
        for rate in RATES:
            thr = np.quantile(s_[ok], rate)
            blk = ok & (s_ <= thr)
            r = metrics(analytic(blk), f"{nm} @{int(rate*100)}%")
            r["rate"] = rate; r["model"] = nm
            r["blocked"] = int(blk.sum())
            r["blocked_pnl"] = float(pnl[blk].sum())
            show(r); rows.append(r)
        P_("")
    R = pd.DataFrame(rows)
    R.to_csv(os.path.join(OUT, "model.csv"), index=False)

    # in-sample sanity: how well does each model actually rank out-of-sample?
    P_(f"=== out-of-sample rank quality of each model (Spearman on the predicted entries) ===")
    for nm, s_ in scores.items():
        ok = np.isfinite(s_)
        rho = float(pd.Series(s_[ok]).corr(pd.Series(per_unit[ok]), method="spearman"))
        rho_d = float(pd.Series(s_[ok]).corr(pd.Series(dur[ok]), method="spearman"))
        P_(f"   {nm:<34} rho vs per-unit P&L {rho:+.3f} | vs duration {rho_d:+.3f} "
           f"| n = {int(ok.sum())}")

    # ---------------- validate the analytic path ------------------------------------------
    best = max([r for r in rows if r["arm"] != "P1 INCUMBENT"], key=lambda r: r["weekly"])
    s_ = scores[best["model"]]; ok = np.isfinite(s_)
    blk = ok & (s_ <= np.quantile(s_[ok], best["rate"]))
    kill = np.zeros(n, bool)
    for k in np.flatnonzero(blk):
        j = str_of_trade[k]
        if j >= 0:
            kill[starts[j]:ends[j] + 1] = True
    trl = build((posL.astype(bool) & ~kill).astype(np.int8))
    spf = np.zeros(D["n_sess"])
    for x in trl:
        spf[int(sid[i_of(x["et"])])] += x["pnl"]
    full = metrics(spf[sess_in], f"{best['arm']} FULL PIPELINE")
    P_(f"\n=== analytic vs full pipeline on the best arm ===")
    P_(HDR)
    show(best); show(full)
    err = abs(full["weekly"] - best["weekly"]) / max(abs(best["weekly"]), 1e-9)
    P_(f"   weekly$ error {100*err:.1f} % -> analytic nulls "
       f"{'ACCEPTED' if err < 0.05 else 'REJECTED, would need full-pipeline nulls'}")

    # ---------------- PHASE 3: the nulls ---------------------------------------------------
    P_(f"\n{'='*120}\n=== PHASE 3: NULLS. N1 label permutation is the binding one "
       f"[{_time.time()-t0:.0f}s]")
    P_(f"{'='*120}")
    P_("N1 refits the ENTIRE pipeline on shuffled labels. If the real model does not beat its")
    P_("own procedure applied to noise, it is a description of the sample and the branch dies.\n")

    def best_over_rates(s_):
        okk = np.isfinite(s_)
        if okk.sum() < 100:
            return None
        b = None
        for rate in RATES:
            m_ = metrics(analytic(okk & (s_ <= np.quantile(s_[okk], rate))))
            if b is None or m_["weekly"] > b["weekly"]:
                b = m_
        return b
    real = {nm: best_over_rates(s_) for nm, s_ in scores.items()}
    P_(f"{'model':<34}{'real best $':>13}{'N1 mean':>10}{'N1 pct':>9}{'N2 mean':>10}"
       f"{'N2 pct':>9}{'N3 mean':>10}{'N3 pct':>9}{'verdict':>10}")
    nulls = []
    for nm, y in TARGETS.items():
        rb = real[nm]
        if rb is None:
            continue
        n1, n2, n3 = [], [], []
        okk = np.isfinite(scores[nm])
        rate_n = float(np.mean([r["rate"] for r in rows
                                if r.get("model") == nm and r["arm"] == rb["arm"]] or [0.15]))
        for _ in range(NDRAW):
            yp = RNG.permutation(y)
            b = best_over_rates(walk_forward_scores(FM, yp))
            if b:
                n1.append(b["weekly"])
        for _ in range(NDRAW):
            b = None
            for rate in RATES:
                m_ = np.zeros(len(pnl), bool)
                idx = RNG.choice(np.flatnonzero(okk), int(rate * okk.sum()), replace=False)
                m_[idx] = True
                mm = metrics(analytic(m_))
                if b is None or mm["weekly"] > b["weekly"]:
                    b = mm
            n2.append(b["weekly"])
        for _ in range(NDRAW):        # N3: duration-biased random, no delay cost
            b = None
            for rate in RATES:
                pw = 1.0 / np.maximum(dur, 1.0)
                pw = pw / pw.sum()
                idx = RNG.choice(len(pnl), int(rate * len(pnl)), replace=False, p=pw)
                m_ = np.zeros(len(pnl), bool); m_[idx] = True
                mm = metrics(analytic(m_))
                if b is None or mm["weekly"] > b["weekly"]:
                    b = mm
            n3.append(b["weekly"])
        a1, a2, a3 = np.array(n1), np.array(n2), np.array(n3)
        p1 = 100 * float((a1 < rb["weekly"]).mean()) if len(a1) else 0.0
        p2 = 100 * float((a2 < rb["weekly"]).mean())
        p3 = 100 * float((a3 < rb["weekly"]).mean())
        P_(f"{nm:<34}{rb['weekly']:>13,.0f}{a1.mean() if len(a1) else 0:>10,.0f}{p1:>8.1f}%"
           f"{a2.mean():>10,.0f}{p2:>8.1f}%{a3.mean():>10,.0f}{p3:>8.1f}%"
           f"{('PASS' if (p1 >= 95 and p3 >= 95) else 'fail'):>10}")
        nulls.append(dict(model=nm, real=rb["weekly"], n1=float(a1.mean()) if len(a1) else 0,
                          n1_pct=p1, n2=float(a2.mean()), n2_pct=p2,
                          n3=float(a3.mean()), n3_pct=p3))
    pd.DataFrame(nulls).to_csv(os.path.join(OUT, "nulls2.csv"), index=False)
    P_(f"\n   incumbent weekly at its own drawdown: ${base['weekly']:,.0f}")
    P_(f"   preregistered bar: N1 label permutation AND N3 both >= 95th percentile.")
    if nulls and not any(x["n1_pct"] >= 95 and x["n3_pct"] >= 95 for x in nulls):
        P_(f"   -> NO MODEL CLEARS. Recorded per the falsifier: the same fitting procedure on")
        P_(f"      SHUFFLED labels does as well, so the multivariate branch is closed for this")
        P_(f"      feature set and this target. It does NOT close nonlinear learners, other")
        P_(f"      feature sets, session-level targets, or other objects.")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
