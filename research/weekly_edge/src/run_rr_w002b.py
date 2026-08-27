"""RR_W002A modelling stage - expanding prequential walk-forward, dependence-preserving nulls, gates.

Spec: runs/RR_W002A_ACTION_VALUE_INFORMATION/spec.yaml (f5d4e01). Reads the causality-gated feature
matrix built by run_rr_w002a.py.

STAGE A INFORMATION ONLY. Nothing here becomes a policy, a threshold or a rule.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_we_w01 as W1                                                   # noqa: E402
from run_we_w01 import ROOT                                               # noqa: E402
from run_we_w17 import load_deep                                          # noqa: E402

OUT = os.path.join(ROOT, "runs", "RR_W002A_ACTION_VALUE_INFORMATION", "out")
A, B = np.datetime64("2022-07-01"), np.datetime64("2026-08-01")
SEED, NSHIFT, FIRST_FIT, BLOCK, RIDGE_ALPHA = 2002, 200, 250, 63, 10.0

ARM1 = ["causal_quality_score", "quality_score_is_warmup", "size_at_entry",
        "strategy_session_pnl_before_per_ctr", "entry_ordinal_in_session"]
ARM2 = ["dist_open", "dist_vwap", "runlen", "delta_mag", "prev_ret", "atr_l",
        "nq_move_5m", "nq_move_15m", "nq_move_30m", "nq_path_eff_30m",
        "nq_atr_z", "session_move_so_far"]
ARM3 = ["minute_of_session"]
NEG = ["rel_volume_1m", "xm_support_mag_15m"]
VOL_ONLY = ["atr_l", "nq_atr_z"]

_t0 = _time.time()
_fh = open(os.path.join(OUT, "rr_w002b.txt"), "w", encoding="utf-8")


def P_(*a):
    print(*a, flush=True)
    print(*a, file=_fh)
    _fh.flush()


def el():
    return f"[{_time.time() - _t0:6.0f}s]"


def walk(Xf, y, cols, sess_pos, folds, model):
    """Expanding prequential walk-forward. Scaling and imputation fitted on TRAIN ONLY."""
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
        if model == "M0":
            pred[te] = y[tr].mean()
        elif model == "M2":
            m = Ridge(alpha=RIDGE_ALPHA).fit(Xtr, y[tr]); pred[te] = m.predict(Xte)
        elif model == "M3":
            m = HistGradientBoostingRegressor(max_depth=2, max_iter=200, learning_rate=0.03,
                                              min_samples_leaf=100, random_state=SEED)
            m.fit(Xtr, y[tr]); pred[te] = m.predict(Xte)
    return pred


def rho(pred, y):
    g = np.isfinite(pred) & np.isfinite(y)
    if g.sum() < 30 or np.nanstd(pred[g]) == 0:
        return 0.0
    return float(spearmanr(pred[g], y[g]).statistic)


def main():
    P_("=" * 124)
    P_("=== RR_W002A - MODELLING STAGE.  Spec f5d4e01.  STAGE A INFORMATION ONLY.")
    P_("=== No router, no policy, no abstention, no sizing, no exit change, no HMM.")
    P_("=" * 124)

    F = pd.read_csv(os.path.join(OUT, "features.csv"))
    F["session_date"] = pd.to_datetime(F["session_date"])
    F = F.sort_values(["session_date", "entry_ordinal_in_session"]).reset_index(drop=True)
    y = F["target_full"].to_numpy()
    P_(f"{el()} {len(F):,} decisions   target = delta_total_window   "
       f"mean ${y.mean():,.2f}  sd ${y.std(ddof=1):,.2f}")

    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    sd_all = pd.to_datetime(D["sess_date"])
    cal = np.array(sorted(d for d in sd_all if A <= np.datetime64(d) < B))
    P_(f"{el()} {len(cal):,} in-window CALENDAR sessions define the walk-forward axis")
    cal_pos = {pd.Timestamp(d): j for j, d in enumerate(cal)}
    sess_pos = F["session_date"].map(cal_pos).to_numpy()

    folds = []
    lo = FIRST_FIT
    while lo < len(cal):
        folds.append((lo, lo, min(lo + BLOCK, len(cal))))
        lo += BLOCK
    P_(f"{el()} {len(folds)} expanding folds: first fit after {FIRST_FIT} sessions, "
       f"{BLOCK}-session test blocks")

    # ---------------------------------------------------------------- can each gate statistic fail?
    P_("")
    P_("    CAN THESE STATISTICS TAKE A FAILING VALUE?  (RR_W001's G4 could not, and nobody noticed)")
    P_(f"      H1 rank corr > 0            : rho is signed and unbounded in sign -> CAN FAIL")
    P_(f"      H2 above null p95           : the null is refitted, so a real model can land below -> CAN FAIL")
    P_(f"      H3 beats every control      : controls are fitted on the same folds -> CAN FAIL")
    P_(f"      H4 top-minus-bottom > 0     : the target has {100*(y<0).mean():.1f} % negative values -> CAN FAIL")
    P_(f"      H5 sign positive in >=60 %  : per-fold rho is signed -> CAN FAIL")
    P_(f"      H6 negative controls null   : they are fitted identically to the real arms -> CAN FAIL")

    SETS = {
        "M0_BASE_RATE": (ARM1[:1], "M0"),
        "M1_EXPERT_SCORE_ONLY": (["causal_quality_score"], "M1"),
        "CTRL_TIME_ONLY": (ARM3, "M2"),
        "CTRL_VOL_ONLY": (VOL_ONLY, "M2"),
        "ARM1_INTERNAL": (ARM1, "M2"),
        "ARM2_NQ_STATE": (ARM2, "M2"),
        "PRIMARY_ARM1+2+3_RIDGE": (ARM1 + ARM2 + ARM3, "M2"),
        "ARM1+2+3_SHALLOW_GBM": (ARM1 + ARM2 + ARM3, "M3"),
        "NEGCTRL_KNOWN_NULL": (NEG, "M2"),
    }
    P_("")
    P_("=" * 124)
    P_("=== 1. OUT-OF-SAMPLE PERFORMANCE.  Pooled across all test folds.")
    P_("=" * 124)
    P_(f"{'cell':<26}{'features':>9}{'OOS rho':>10}{'OOS R2':>10}{'folds +':>10}"
       f"{'Q5-Q1 $':>12}{'monotone':>10}")
    res = {}
    for name, (cols, mdl) in SETS.items():
        if mdl == "M1":
            p_ = F["causal_quality_score"].to_numpy().astype(float)
            p_ = np.where(np.isfinite(p_), p_, np.nan)
            p_[sess_pos < FIRST_FIT] = np.nan
        else:
            p_ = walk(F, y, cols, sess_pos, folds, mdl)
        g = np.isfinite(p_) & np.isfinite(y)
        r = rho(p_, y)
        ss = float(1 - np.sum((y[g] - p_[g]) ** 2) / np.sum((y[g] - y[g].mean()) ** 2)) \
            if mdl not in ("M1",) and np.nanstd(p_[g]) > 0 else np.nan
        fr = []
        for tr_hi, te_lo, te_hi in folds:
            m = (sess_pos >= te_lo) & (sess_pos < te_hi) & g
            if m.sum() >= 30:
                fr.append(rho(p_[m], y[m]))
        fpos = float(np.mean([x > 0 for x in fr])) if fr else np.nan
        if np.nanstd(p_[g]) > 0:
            q = pd.qcut(pd.Series(p_[g]).rank(method="first"), 5, labels=False)
            qm = [float(y[g][q == i].mean()) for i in range(5)]
            tmb = qm[4] - qm[0]
            mono = all(qm[i] <= qm[i + 1] for i in range(4))
        else:
            qm, tmb, mono = [np.nan] * 5, np.nan, False
        res[name] = dict(rho=r, r2=ss, fpos=fpos, tmb=tmb, mono=mono, qm=qm,
                         n=int(g.sum()), folds=fr, pred=p_)
        P_(f"{name:<26}{len(cols):>9}{r:>10.4f}{ss:>10.4f}{100*fpos:>9.0f}%"
           f"{tmb:>12,.0f}{str(mono):>10}")

    # ---------------------------------------------------------------- nulls
    P_("")
    P_("=" * 124)
    P_("=== 2. DEPENDENCE-PRESERVING NULL.  The ENTIRE walk-forward is refitted inside every shift.")
    P_("=== The target is circularly shifted by WHOLE SESSIONS, so within-session structure and the")
    P_("=== target's own autocorrelation survive and only the alignment is destroyed.")
    P_("=" * 124)
    bnd = np.flatnonzero(np.diff(sess_pos, prepend=-1) != 0)
    rng = np.random.default_rng(SEED)
    offs = rng.choice(bnd[1:], size=min(NSHIFT, len(bnd) - 1), replace=False)
    P_(f"    {len(offs)} shifts, drawn from the {len(bnd):,} session-boundary offsets")
    NULLED = ["PRIMARY_ARM1+2+3_RIDGE", "ARM1+2+3_SHALLOW_GBM", "NEGCTRL_KNOWN_NULL",
              "ARM1_INTERNAL", "ARM2_NQ_STATE"]
    P_("")
    P_(f"{'cell':<26}{'real rho':>10}{'null p50':>10}{'null p95':>10}{'percentile':>12}{'verdict':>9}")
    nullres = {}
    for name in NULLED:
        cols, mdl = SETS[name]
        dist = []
        for k, off in enumerate(offs):
            ysh = np.roll(y, int(off))
            dist.append(rho(walk(F, ysh, cols, sess_pos, folds, mdl), ysh))
        dist = np.array(dist)
        pct = 100.0 * float((dist < res[name]["rho"]).mean())
        nullres[name] = dict(p50=float(np.percentile(dist, 50)),
                             p95=float(np.percentile(dist, 95)), pct=pct)
        P_(f"{name:<26}{res[name]['rho']:>10.4f}{nullres[name]['p50']:>10.4f}"
           f"{nullres[name]['p95']:>10.4f}{pct:>11.1f}%"
           f"{('PASS' if pct >= 95 else 'fail'):>9}")
        P_(f"{el()}   ... {name} null complete")

    # ---------------------------------------------------------------- gates
    prim = res["PRIMARY_ARM1+2+3_RIDGE"]
    ctrl_best = max(res[c]["rho"] for c in
                    ("M0_BASE_RATE", "M1_EXPERT_SCORE_ONLY", "CTRL_TIME_ONLY", "CTRL_VOL_ONLY"))
    negpass = [n for n in ("NEGCTRL_KNOWN_NULL",) if nullres[n]["pct"] >= 95]
    P_("")
    P_("=" * 124)
    P_("=== 3. THE PREREGISTERED GATE TABLE.  Every clause is a coded assertion.")
    P_("=" * 124)
    g = [
        ("H1", "primary OOS rank correlation > 0", f"{prim['rho']:.4f}", prim["rho"] > 0),
        ("H2", "primary exceeds the 95th percentile of its own refitted null",
         f"{nullres['PRIMARY_ARM1+2+3_RIDGE']['pct']:.1f}th",
         nullres["PRIMARY_ARM1+2+3_RIDGE"]["pct"] >= 95),
        ("H3", "primary beats EVERY simple control",
         f"{prim['rho']:.4f} vs best control {ctrl_best:.4f}", prim["rho"] > ctrl_best),
        ("H4", "quintile monotonicity AND top-minus-bottom > 0",
         f"mono={prim['mono']}  Q5-Q1 ${prim['tmb']:,.0f}",
         bool(prim["mono"]) and prim["tmb"] > 0),
        ("H5", "per-fold rank correlation positive in >= 60 % of folds",
         f"{100*prim['fpos']:.0f}%", prim["fpos"] >= 0.60),
        ("H6", "BOTH negative controls FAIL the null (else the pipeline is broken)",
         f"{'none cleared' if not negpass else 'CLEARED: ' + str(negpass)}", not negpass),
    ]
    P_(f"{'gate':<6}{'spec':<62}{'observed':>34}{'verdict':>10}")
    for gg, spec, obsv, ok in g:
        P_(f"{gg:<6}{spec:<62}{obsv:>34}{('PASS' if ok else 'FAIL'):>10}")
    pd.DataFrame([dict(gate=x[0], spec=x[1], observed=x[2], verdict="PASS" if x[3] else "FAIL")
                  for x in g]).to_csv(os.path.join(OUT, "gates.csv"), index=False)
    allp = all(x[3] for x in g)
    P_("")
    P_(f"    ALL GATES: {'PASS' if allp else 'NOT ALL PASS'}")

    # ---------------------------------------------------------------- detail
    P_("")
    P_("=" * 124)
    P_("=== 4. DETAIL - quintiles, folds, incremental arms, tails")
    P_("=" * 124)
    P_("    PRIMARY score-quintile mean action value (Q1 = lowest predicted):")
    P_("      " + "  ".join(f"Q{i+1} ${prim['qm'][i]:,.0f}" for i in range(5)))
    P_("")
    P_("    PRIMARY per-fold OOS rank correlation (every fold printed, never only the pooled):")
    P_("      " + "  ".join(f"{x:+.3f}" for x in prim["folds"]))
    P_("")
    P_("    INCREMENTAL ARMS (pooled OOS rho):")
    for nm in ("ARM1_INTERNAL", "ARM2_NQ_STATE", "PRIMARY_ARM1+2+3_RIDGE", "ARM1+2+3_SHALLOW_GBM"):
        P_(f"      {nm:<26}{res[nm]['rho']:>9.4f}")
    P_("")
    bestk = max(res[n]["rho"] for n in NULLED)
    P_(f"    BEST-OF-K over the {len(NULLED)} nulled cells: rho {bestk:.4f}. The multiplicity bar is")
    P_(f"    printed HERE beside the primary rather than as a footnote - W112's recorded error.")
    P_("")
    top = np.nanpercentile(y, 90)
    gp = np.isfinite(prim["pred"])
    P_("    RIGHT-TAIL IDENTIFICATION - can the primary rank the extreme-POSITIVE decile?")
    from sklearn.metrics import roc_auc_score
    for lab, tgt in (("top decile", (y >= top).astype(int)),
                     ("bottom decile", (y <= np.nanpercentile(y, 10)).astype(int))):
        try:
            auc = roc_auc_score(tgt[gp], prim["pred"][gp])
        except Exception:                                            # noqa: BLE001
            auc = np.nan
        P_(f"      {lab:<16} AUC {auc:.4f}")
    P_("")
    bd = F["session_date"]
    burn = ((bd >= "2026-05-31") & (bd <= "2026-07-31")).to_numpy()
    P_("    EVIDENCE STATUS: whole window DISCOVERY_CONSUMED; 2026-05-31 -> 07-31 DIRECTLY_BURNED")
    P_(f"      burned slice: {int(burn.sum()):,} decisions ({100*burn.mean():.2f} %)")
    P_("")
    P_("    POWER LIMITATION, restated because it is binding: RR_W001's G3 showed this sample cannot")
    P_("    certify SMALL economic improvements (smallest detectable per-decision gain $41-80 against")
    P_("    a $13.93 bar). An INFORMATION result here does NOT overturn that and is not economics.")
    pd.DataFrame({k: v["pred"] for k, v in res.items()}).assign(
        target_full=y, session_date=F["session_date"]).to_csv(
        os.path.join(OUT, "predictions.csv"), index=False)
    P_(f"\n{el()} done")
    _fh.close()


if __name__ == "__main__":
    main()
