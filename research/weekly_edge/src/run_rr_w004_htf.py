"""RR_W004 - DOES HIGHER-TIMEFRAME STATE ADD INCREMENTAL INFORMATION?

Spec: runs/RR_W004_HTF_INCREMENT/spec.yaml, committed at 50ddd4f BEFORE this file existed.

STAGE A INFORMATION ONLY. No router, no policy, no sizing, no exit change, no HMM.

Everything except the six HTF features is inherited UNCHANGED from RR_W002A. That claim is not
asserted - it is CERTIFIED by reproducing RR_W002A's primary rank correlation (-0.0302) exactly
before any HTF result is read.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.linear_model import Ridge

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_we_w01 as W1                                                   # noqa: E402
from run_we_w01 import ROOT                                               # noqa: E402
from run_we_w17 import load_deep                                          # noqa: E402
from we_fastctx import fast_build_context                                 # noqa: E402

W2OUT = os.path.join(ROOT, "runs", "RR_W002A_ACTION_VALUE_INFORMATION", "out")
OUT = os.path.join(ROOT, "runs", "RR_W004_HTF_INCREMENT", "out")
os.makedirs(OUT, exist_ok=True)
A, B = np.datetime64("2022-07-01"), np.datetime64("2026-08-01")
SEED, NSHIFT, FIRST_FIT, BLOCK, RIDGE_ALPHA = 2002, 200, 250, 63, 10.0
W2A_PRIMARY_RHO = -0.0302

ARM1 = ["causal_quality_score", "quality_score_is_warmup", "size_at_entry",
        "strategy_session_pnl_before_per_ctr", "entry_ordinal_in_session"]
ARM2 = ["dist_open", "dist_vwap", "runlen", "delta_mag", "prev_ret", "atr_l",
        "nq_move_5m", "nq_move_15m", "nq_move_30m", "nq_path_eff_30m",
        "nq_atr_z", "session_move_so_far"]
ARM3 = ["minute_of_session"]
NEG = ["rel_volume_1m", "xm_support_mag_15m"]
HTF = ["htf_ret_5d", "htf_ret_20d", "htf_pdr_pos", "htf_gap", "htf_vol_20d", "htf_trend_r2_20d"]

_t0 = _time.time()
_fh = open(os.path.join(OUT, "rr_w004.txt"), "w", encoding="utf-8")


def P_(*a):
    print(*a, flush=True)
    print(*a, file=_fh)
    _fh.flush()


def el():
    return f"[{_time.time() - _t0:6.0f}s]"


def build_htf(D, X, ent):
    """SLOW SESSION CONTEXT. Every column uses COMPLETED PRIOR SESSIONS plus bars <= i-1."""
    c, h, l_, o = D["c"], D["h"], D["l"], D["o"]
    fb, lb, sid = D["fb"], D["lb"], D["sid"]
    st = np.flatnonzero(fb)
    en = np.flatnonzero(lb)
    s_close, s_high, s_low, s_open = c[en], np.zeros(len(st)), np.zeros(len(st)), o[st]
    for k in range(len(st)):
        s_high[k] = h[st[k]:en[k] + 1].max()
        s_low[k] = l_[st[k]:en[k] + 1].min()
    lr = np.diff(np.log(np.maximum(s_close, 1e-9)), prepend=np.log(max(s_close[0], 1e-9)))

    s = sid[ent].astype(int)                    # this decision's session
    prev = ent - 1
    atr = np.maximum(X["atr_l"][ent], 1e-9)
    out = {}

    def sret(k):
        a_ = s - 1 - k
        ok = a_ >= 0
        r = np.full(len(ent), np.nan)
        r[ok] = np.log(np.maximum(s_close[s[ok] - 1], 1e-9)) - np.log(np.maximum(s_close[a_[ok]], 1e-9))
        return r / atr

    out["htf_ret_5d"] = sret(5)
    out["htf_ret_20d"] = sret(20)

    ok = s - 1 >= 0
    rng = np.where(ok, s_high[np.maximum(s - 1, 0)] - s_low[np.maximum(s - 1, 0)], np.nan)
    out["htf_pdr_pos"] = np.where(ok & (rng > 0),
                                  (c[prev] - s_low[np.maximum(s - 1, 0)]) / np.maximum(rng, 1e-9),
                                  np.nan)
    out["htf_gap"] = np.where(ok, (s_open[s] - s_close[np.maximum(s - 1, 0)]) / atr, np.nan)

    v20 = np.full(len(ent), np.nan)
    r2 = np.full(len(ent), np.nan)
    for j in range(len(ent)):
        a_ = s[j] - 20
        if a_ < 1:
            continue
        seg = lr[a_:s[j]]
        v20[j] = seg.std(ddof=1)
        y = s_close[a_:s[j]]
        xx = np.arange(len(y), dtype=float)
        if len(y) >= 3 and y.std() > 0:
            cc = np.corrcoef(xx, y)[0, 1]
            r2[j] = cc * cc
    out["htf_vol_20d"] = v20 / atr
    out["htf_trend_r2_20d"] = r2
    return out


def walk(Xf, y, cols, sess_pos, folds):
    """Ridge, expanding prequential. IDENTICAL to run_rr_w002b.walk with model='M2'."""
    pred = np.full(len(y), np.nan)
    for tr_hi, te_lo, te_hi in folds:
        tr = sess_pos < tr_hi
        te = (sess_pos >= te_lo) & (sess_pos < te_hi)
        if tr.sum() < 50 or te.sum() == 0:
            continue
        Xtr, Xte = Xf[cols].to_numpy()[tr], Xf[cols].to_numpy()[te]
        med = np.nanmedian(Xtr, axis=0)
        med = np.where(np.isfinite(med), med, 0.0)
        Xtr = np.where(np.isfinite(Xtr), Xtr, med)
        Xte = np.where(np.isfinite(Xte), Xte, med)
        mu, sd = Xtr.mean(0), np.maximum(Xtr.std(0), 1e-9)
        Xtr, Xte = (Xtr - mu) / sd, (Xte - mu) / sd
        pred[te] = Ridge(alpha=RIDGE_ALPHA).fit(Xtr, y[tr]).predict(Xte)
    return pred


def rho(p, y):
    g = np.isfinite(p) & np.isfinite(y)
    if g.sum() < 30 or np.nanstd(p[g]) == 0:
        return 0.0
    return float(spearmanr(p[g], y[g]).statistic)


def main():
    P_("=" * 122)
    P_("=== RR_W004 - DOES HIGHER-TIMEFRAME STATE ADD INCREMENTAL INFORMATION?")
    P_("=== Spec 50ddd4f.  STAGE A INFORMATION ONLY.  Nothing here becomes a policy.")
    P_("=" * 122)

    F0 = pd.read_csv(os.path.join(W2OUT, "features.csv"))
    F0["session_date"] = pd.to_datetime(F0["session_date"])
    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    X = fast_build_context(D)
    tarr, n = D["t"], D["n"]
    LED = pd.read_csv(os.path.join(ROOT, "runs", "RR_W001_ACTION_VALUE_LEDGER", "out",
                                   "ledger_p1pct.csv"))
    LED = LED[LED["in_window_session"]].reset_index(drop=True)
    ent = np.array([int(min(np.searchsorted(tarr, np.datetime64(t)), n - 1))
                    for t in LED["decision_ts"]])
    P_(f"{el()} {len(ent):,} decision bars; building the six HTF columns")
    H = build_htf(D, X, ent)

    # ---------------------------------------------------------------- causality gate
    P_("")
    P_("=" * 122)
    P_("=== 1. CAUSALITY GATE for the HTF arm.  BLOCKING.  Same construction as RR_W002A.")
    P_("=" * 122)
    SEP = 5000
    order = np.sort(ent)
    sel, last = [], -10 ** 9
    for e in order:
        if e - last >= SEP:
            sel.append(int(e)); last = int(e)
    tb = np.array(sel)
    pos = {int(e): j for j, e in enumerate(ent)}
    idx = np.array([pos[int(e)] for e in tb])

    def with_probes(Dx, Xx):
        f = build_htf(Dx, Xx, ent)
        at = np.maximum(Xx["atr_l"][ent], 1e-9)
        f["PROBE_LEAK_close_i"] = Dx["c"][ent] / at
        f["PROBE_SAFE_close_prev"] = Dx["c"][ent - 1] / at
        return f

    Hp = with_probes(D, X)

    def rebuild(shift):
        D2 = {k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in D.items()}
        t_ = tb - shift
        for key, m in (("h", 1.004), ("l", 0.996), ("c", 1.003), ("o", 1.002), ("v", 1.5)):
            D2[key][t_] = D2[key][t_] * m
        return with_probes(D2, fast_build_context(D2))

    LAGS = [0, 1, 400, 2000]
    R = {sh: rebuild(sh) for sh in LAGS}
    rows, keep = [], []
    for k in list(Hp):
        base = Hp[k][idx]
        mv = {sh: float(np.mean(np.abs(np.nan_to_num(base - R[sh][k][idx])) > 1e-9)) for sh in LAGS}
        col = Hp[k]
        causal = mv[0] < 1e-12
        alive = bool(np.nanstd(col) > 0) and len(np.unique(col[np.isfinite(col)])) > 5
        ok = causal and alive
        rows.append(dict(feature=k, own_bar=mv[0], lag1=mv[1], lag400=mv[400], lag2000=mv[2000],
                         verdict="KEEP" if ok else "DROP"))
        if ok and not k.startswith("PROBE_"):
            keep.append(k)
    P_(f"{'feature':<24}{'own bar':>10}{'lag1':>9}{'lag400':>9}{'lag2000':>10}{'verdict':>9}")
    for r in rows:
        P_(f"{r['feature']:<24}{100*r['own_bar']:>9.1f}%{100*r['lag1']:>8.1f}%"
           f"{100*r['lag400']:>8.1f}%{100*r['lag2000']:>9.1f}%{r['verdict']:>9}")
    vb = next(r for r in rows if r["feature"] == "PROBE_LEAK_close_i")["verdict"]
    vg = next(r for r in rows if r["feature"] == "PROBE_SAFE_close_prev")["verdict"]
    P_("")
    P_(f"    SELF-TEST: leak -> {vb} (expect DROP)   lag -> {vg} (expect KEEP)")
    if vb != "DROP" or vg != "KEEP":
        P_("    THE GATE ITSELF IS BROKEN. No model is fitted."); _fh.close(); sys.exit(1)
    P_(f"    KEPT {len(keep)} of {len(HTF)} HTF features: {keep}")
    if not keep:
        P_("    No HTF feature survives. No model is fitted."); _fh.close(); sys.exit(1)

    # ---------------------------------------------------------------- assemble + reproduce
    F = F0.copy()
    for k in keep:
        F[k] = Hp[k]
    F = F.sort_values(["session_date", "entry_ordinal_in_session"]).reset_index(drop=True)
    y = F["target_full"].to_numpy()
    cal = np.array(sorted(d for d in pd.to_datetime(D["sess_date"]) if A <= np.datetime64(d) < B))
    cal_pos = {pd.Timestamp(d): j for j, d in enumerate(cal)}
    sess_pos = F["session_date"].map(cal_pos).to_numpy()
    folds = []
    lo = FIRST_FIT
    while lo < len(cal):
        folds.append((lo, lo, min(lo + BLOCK, len(cal)))); lo += BLOCK

    P_("")
    P_("=" * 122)
    P_("=== 2. PIPELINE REPRODUCTION GATE.  BLOCKING.  Is this the SAME pipeline RR_W002A ran?")
    P_("=" * 122)
    XCOLS = ARM1 + ARM2 + ARM3
    r_x = rho(walk(F, y, XCOLS, sess_pos, folds), y)
    ok = abs(r_x - W2A_PRIMARY_RHO) < 5e-4
    P_(f"    RR_W002A primary rank correlation  {W2A_PRIMARY_RHO:+.4f}")
    P_(f"    reproduced here                    {r_x:+.4f}   {'OK' if ok else 'MISMATCH'}")
    if not ok:
        P_("    The pipeline is NOT unchanged. No incremental claim can be made."); _fh.close(); sys.exit(1)
    P_("    The pipeline is unchanged; the only new thing is the HTF arm.")

    # ---------------------------------------------------------------- arms
    SETS = {"X_ONLY": XCOLS, "HTF_ONLY": keep, "X_PLUS_HTF": XCOLS + keep, "NEGCTRL": NEG}
    P_("")
    P_("=" * 122)
    P_("=== 3. ARMS")
    P_("=" * 122)
    P_(f"{'arm':<16}{'features':>10}{'OOS rho':>11}{'vs X_ONLY':>12}{'folds +':>10}")
    res, preds = {}, {}
    for nm, cols in SETS.items():
        p_ = walk(F, y, cols, sess_pos, folds)
        preds[nm] = p_
        r = rho(p_, y)
        fr = []
        for tr_hi, te_lo, te_hi in folds:
            m = (sess_pos >= te_lo) & (sess_pos < te_hi) & np.isfinite(p_)
            if m.sum() >= 30:
                fr.append(rho(p_[m], y[m]))
        res[nm] = dict(rho=r, folds=fr)
        P_(f"{nm:<16}{len(cols):>10}{r:>11.4f}{r - res['X_ONLY']['rho']:>12.4f}"
           f"{100*float(np.mean([x > 0 for x in fr])):>9.0f}%")

    # per-fold increment
    fx, fh_ = res["X_ONLY"]["folds"], res["X_PLUS_HTF"]["folds"]
    inc_pos = float(np.mean([b_ > a_ for a_, b_ in zip(fx, fh_)]))

    # ---------------------------------------------------------------- nulls
    P_("")
    P_("=" * 122)
    P_("=== 4. NULLS - the ENTIRE walk-forward refitted inside every session-boundary shift")
    P_("=" * 122)
    bnd = np.flatnonzero(np.diff(sess_pos, prepend=-1) != 0)
    rng = np.random.default_rng(SEED)
    offs = rng.choice(bnd[1:], size=min(NSHIFT, len(bnd) - 1), replace=False)
    P_(f"{'arm':<16}{'real rho':>11}{'null p50':>11}{'null p95':>11}{'percentile':>12}{'verdict':>9}")
    nullres = {}
    for nm in ("X_PLUS_HTF", "HTF_ONLY", "NEGCTRL"):
        d_ = np.array([rho(walk(F, np.roll(y, int(o)), SETS[nm], sess_pos, folds), np.roll(y, int(o)))
                       for o in offs])
        pct = 100.0 * float((d_ < res[nm]["rho"]).mean())
        nullres[nm] = pct
        P_(f"{nm:<16}{res[nm]['rho']:>11.4f}{np.percentile(d_, 50):>11.4f}"
           f"{np.percentile(d_, 95):>11.4f}{pct:>11.1f}%{('PASS' if pct >= 95 else 'fail'):>9}")

    # ---------------------------------------------------------------- gates
    P_("")
    P_("=" * 122)
    P_("=== 5. THE PREREGISTERED GATE TABLE")
    P_("=" * 122)
    P_("    can each statistic fail?  rho is signed -> H1 CAN FAIL; the null is refitted -> H2/H3")
    P_("    CAN FAIL; the per-fold increment is signed -> H4 CAN FAIL; H5 is symmetric -> CAN FAIL.")
    P_("")
    g = [
        ("H1", "X_PLUS_HTF rank correlation > X_ONLY's",
         f"{res['X_PLUS_HTF']['rho']:+.4f} vs {res['X_ONLY']['rho']:+.4f}",
         res["X_PLUS_HTF"]["rho"] > res["X_ONLY"]["rho"]),
        ("H2", "X_PLUS_HTF above the 95th percentile of its refitted null",
         f"{nullres['X_PLUS_HTF']:.1f}th", nullres["X_PLUS_HTF"] >= 95),
        ("H3", "HTF_ONLY above the 95th percentile of ITS own null",
         f"{nullres['HTF_ONLY']:.1f}th", nullres["HTF_ONLY"] >= 95),
        ("H4", "the increment is positive in >= 60 % of folds",
         f"{100*inc_pos:.0f}%", inc_pos >= 0.60),
        ("H5", "negative controls FAIL their null",
         f"{nullres['NEGCTRL']:.1f}th", nullres["NEGCTRL"] < 95),
    ]
    P_(f"{'gate':<6}{'spec':<58}{'observed':>26}{'verdict':>10}")
    for gg, spec, obsv, ok_ in g:
        P_(f"{gg:<6}{spec:<58}{obsv:>26}{('PASS' if ok_ else 'FAIL'):>10}")
    pd.DataFrame([dict(gate=x[0], spec=x[1], observed=x[2], verdict="PASS" if x[3] else "FAIL")
                  for x in g]).to_csv(os.path.join(OUT, "gates.csv"), index=False)
    P_("")
    P_(f"    ALL GATES: {'PASS' if all(x[3] for x in g) else 'NOT ALL PASS'}")
    P_("")
    P_("    per-fold X_ONLY   : " + "  ".join(f"{x:+.3f}" for x in fx))
    P_("    per-fold X+HTF    : " + "  ".join(f"{x:+.3f}" for x in fh_))
    P_("")
    P_("    POWER, restated: RR_W001's G3 showed this sample cannot certify SMALL economic")
    P_("    improvements. An information result here would not overturn that in either direction.")
    P_("    EVIDENCE STATUS: DISCOVERY_CONSUMED throughout; 2026-05-31 -> 07-31 DIRECTLY_BURNED.")
    pd.DataFrame(preds).assign(target_full=y, session_date=F["session_date"]).to_csv(
        os.path.join(OUT, "predictions.csv"), index=False)
    P_(f"\n{el()} done")
    _fh.close()


if __name__ == "__main__":
    main()
