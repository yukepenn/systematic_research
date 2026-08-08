"""W6-T2 — Ceiling increment: the decisive FSS-10 measurement (spec
research/scalping_lab/specs/W6_fss10_redteam.md section T2, frozen @ 58a97a3).

Protocol: re-run the W5-C5 predictability-ceiling protocol EXACTLY (same 30s
quote-alive RTH decision clock, same 4 target-first labels (24,8)/(32,10) x
long/short with cap 600s and conservative same-second-both-crossed -> adverse,
same chronological session-grouped expanding 5 folds built from the same
37-session NQ list, same 2 models [L2 logistic w/ StandardScaler inside folds;
HistGradientBoostingClassifier(max_depth=3, early_stopping=True)], both leakage
guards asserted and printed) on TWO feature sets over the SAME rows:
  (a) REPRODUCTION control: the original 27 NQ census features;
  (b) AUGMENTED: 27 NQ + 8 frozen ES features.

ES join (frozen): merge ES sechilo (per-second time/mid_last/n_ev, union-BBO,
tick units) onto the NQ per-second frame on time; ffill es_mid_last with a 5s
staleness limit — if the last ES second-row is older than 5s, ALL ES features
are NaN at that second; ES hi/lo never ffilled (and not used here).

Z-norm (frozen): z_ret60 = ret60 / rolling-600s std of 1s dmid, per instrument,
trailing only, min 300s (=300 non-NaN dmid obs) history.

8 ES features: es_ret30, es_ret60, es_ret300 (es_mid diffs, ES tick units);
es_z_ret60; es_rv60 (rolling 60s std of 1s d(es_mid)); nq_es_z_diff60
(= nq_z_ret60 - es_z_ret60); sign_agree (1.0 if sign(es_ret60)*sign(nq ret60)
> 0 else 0.0; NaN if es_ret60 NaN — ties/zeros count as disagreement);
es_n_ev — DOCUMENTED SUBSTITUTION: the spec names es_spread_t, but the ES
sechilo substrate carries only union-BBO mid (no bid/ask), so ES spread is NOT
constructible; per task instruction es_n_ev (per-second ES event count, 0 on
event-less non-stale seconds, NaN when stale>5s) is substituted.

Same-sample rule (frozen): rows where ANY of the 8 ES features is NaN
(staleness / warmup / truncated es_s20260519 afternoon) are dropped from BOTH
(a) and (b), so the (a)-vs-(b) comparison is paired on identical rows. This is
the ONLY sample difference vs original C5; (a) must reproduce C5 within small
tolerance. Reproduction tolerance (declared before readout): per label/model
|lift_a - lift_C5| <= 2.0pp AND |brier_skill_a - brier_skill_C5| <= 0.02 AND
identical pass_5pp verdicts; exact deltas reported regardless.

Frozen readout per (label, model): top-decile lift in (a) and (b) with
day-clustered CIs; delta lift (b - a) with PAIRED session-bootstrap CI (same
session draws for both runs, seed 20260808, 1000 reps); Brier skills;
permutation importance of the ES features in (b).

Interpretation rule (frozen): if NO label/model in (b) reaches the C5 5pp bar
(lift >= 5pp AND CI_lo > 0) -> FSS-10 NEGATIVE, ES information closed at
retail-accessible lags. If any (b) >= 5pp where (a) < 5pp -> ES adds material
information -> conversion spec next wave.

Seed 20260808; 1000 session-bootstrap reps; day-clustered CIs. LOCAL ONLY.
"""
import glob, os, sys
import numpy as np, pandas as pd
from numba import njit
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.ensemble import HistGradientBoostingClassifier

SEED = 20260808
NREPS = 1000
CAP = 600
CLOCK = 30
MINHIST = 300
NFOLDS = 5
ES_STALE = 5.0     # seconds; frozen join staleness limit
ZWIN = 600         # z-norm: rolling 600s std of 1s dmid
ZMIN = 300         # z-norm: min 300s history
LABELS = [("long", 1, 24, 8), ("long", 1, 32, 10),
          ("short", -1, 24, 8), ("short", -1, 32, 10)]
C1_GAP = {("long", 24, 8): 0.0873, ("short", 24, 8): 0.0909,
          ("long", 32, 10): 0.0703, ("short", 32, 10): 0.0737}
NQ_FEATS = ["ret5", "ret10", "ret30", "ret60", "ret300", "rv60", "rv300",
            "tv60", "eff60", "range300", "dist_hi", "dist_lo", "secs_since_hi",
            "secs_since_lo", "trades10", "trades60", "vol10", "vol60", "upd10",
            "upd60", "sflow10", "sflow60", "act_accel", "nsflow60", "spread",
            "spread60", "tod"]
ES_FEATS = ["es_ret30", "es_ret60", "es_ret300", "es_z_ret60", "es_rv60",
            "nq_es_z_diff60", "sign_agree", "es_n_ev"]
RUNS = [("a_nq27", NQ_FEATS), ("b_nq27_es8", NQ_FEATS + ES_FEATS)]
REPRO_TOL_LIFT = 0.02      # 2.0pp
REPRO_TOL_SKILL = 0.02

SH = "research/scalping_lab/substrate/sechilo/NQ"
GR = "research/scalping_lab/substrate/grid1s/NQ"
ESD = "research/scalping_lab/substrate/sechilo/ES"
C5M = "research/scalping_lab/artifacts/w5_c5/w5c5_metrics.csv"
OUTD = "research/scalping_lab/artifacts/w6_fss10"
os.makedirs(OUTD, exist_ok=True)


@njit(cache=True)
def label_scan(ml, hi, lo, starts, dirsign, A, B, cap):
    """Target-first label per start — VERBATIM from w5_c5_ceiling.py. Scan
    begins at t0+1. 1 = target first, 0 = adverse first (same-second
    both-crossed -> adverse, conservative), -1 = neither hit within cap."""
    out = np.full(starts.shape[0], -1, np.int8)
    n = ml.shape[0]
    for s in range(starts.shape[0]):
        t0 = starts[s]
        m0 = ml[t0]
        end = min(t0 + cap, n - 1)
        for i in range(t0 + 1, end + 1):
            up = hi[i] - m0
            dn = m0 - lo[i]
            if dirsign == 1:
                th = up >= A
                ah = dn >= B
            else:
                th = dn >= A
                ah = up >= B
            if th and ah:
                out[s] = 0
                break
            if ah:
                out[s] = 0
                break
            if th:
                out[s] = 1
                break
    return out


def build_session(tag):
    """C5 house-pattern NQ merge + 27-feature census library + 4 labels on the
    every-30s clock — construction identical to w5_c5_ceiling.build_session —
    PLUS the frozen ES join and the 8 ES feature columns."""
    d0 = pd.to_datetime(tag[1:], format="%Y%m%d")
    g = pd.read_parquet(os.path.join(GR, tag + ".parquet"))
    s = pd.read_parquet(os.path.join(SH, tag + ".parquet"))
    g["time"] = pd.to_datetime(g["time"])
    s["time"] = pd.to_datetime(s["time"])
    f = g.merge(s, on="time", how="left")
    f["mid_last"] = f["mid_last"].ffill()
    f = f[f["mid_last"].notna()].reset_index(drop=True)
    f["mid_high"] = f["mid_high"].fillna(f["mid_last"])
    f["mid_low"] = f["mid_low"].fillna(f["mid_last"])
    ml = f["mid_last"].values.astype(np.float64)
    hi = f["mid_high"].values.astype(np.float64)
    lo = f["mid_low"].values.astype(np.float64)
    n = len(f)
    tod = (f["time"] - d0).dt.total_seconds().values
    upd = (f["bid_upd"] + f["ask_upd"]).values
    upd60 = pd.Series(upd).rolling(60, min_periods=1).sum().values
    dec = (tod >= 9 * 3600 + 1800) & (tod < 16 * 3600) & (upd60 > 0)
    dec_idx = np.where(dec)[0]
    if len(dec_idx) == 0:
        return None, None, None, None
    starts = dec_idx[::CLOCK].astype(np.int64)

    mls = pd.Series(ml)
    dmid = mls.diff()
    F = pd.DataFrame({"session": tag, "t": np.arange(n), "tod": tod})
    for k in (5, 10, 30, 60, 300):
        F[f"ret{k}"] = mls.diff(k).values
    F["rv60"] = dmid.rolling(60).std().values
    F["rv300"] = dmid.rolling(300).std().values
    tv60 = dmid.abs().rolling(60).sum().values
    F["tv60"] = tv60
    F["eff60"] = np.abs(F["ret60"]) / np.where(tv60 > 0, tv60, np.nan)
    F["range300"] = (pd.Series(hi).rolling(300).max()
                     - pd.Series(lo).rolling(300).min()).values
    shi = np.maximum.accumulate(hi)
    slo = np.minimum.accumulate(lo)
    F["dist_hi"] = shi - ml
    F["dist_lo"] = ml - slo
    hidx = pd.Series(np.where(hi >= shi - 1e-9, np.arange(n), np.nan)).ffill().values
    lidx = pd.Series(np.where(lo <= slo + 1e-9, np.arange(n), np.nan)).ffill().values
    F["secs_since_hi"] = np.arange(n) - hidx
    F["secs_since_lo"] = np.arange(n) - lidx
    for k in (10, 60):
        F[f"trades{k}"] = pd.Series(f["trades"].values).rolling(k).sum().values
        F[f"vol{k}"] = pd.Series(f["vol"].values).rolling(k).sum().values
        F[f"upd{k}"] = pd.Series(upd).rolling(k).sum().values
        F[f"sflow{k}"] = pd.Series(f["sflow"].values).rolling(k).sum().values
    F["act_accel"] = F["trades10"] / np.where(F["trades60"] > 0, F["trades60"] / 6.0,
                                              np.nan)
    F["nsflow60"] = F["sflow60"] / np.where(F["vol60"] > 0, F["vol60"], np.nan)
    F["spread"] = f["spread_t"].values
    F["spread60"] = pd.Series(f["spread_t"].values).rolling(60).mean().values

    # ---- ES join (frozen W6 spec) ----
    es = pd.read_parquet(os.path.join(ESD, "es_" + tag + ".parquet"))
    es["time"] = pd.to_datetime(es["time"])
    es = es[["time", "mid_last", "n_ev"]].rename(
        columns={"mid_last": "es_mid_raw", "n_ev": "es_n_ev_raw"})
    fe = f[["time"]].merge(es, on="time", how="left")
    assert len(fe) == n, "ES merge changed row count (duplicate ES seconds?)"
    has_es = fe["es_mid_raw"].notna().values
    last_es = pd.Series(np.where(has_es, tod, np.nan)).ffill().values
    stale = tod - last_es                      # NaN before first ES row
    ok = stale <= ES_STALE                     # False where stale NaN or >5s
    es_mid = np.where(ok, fe["es_mid_raw"].ffill().values, np.nan)
    esm = pd.Series(es_mid)
    es_d = esm.diff()
    F["es_ret30"] = esm.diff(30).values
    F["es_ret60"] = esm.diff(60).values
    F["es_ret300"] = esm.diff(300).values
    es_sig = es_d.rolling(ZWIN, min_periods=ZMIN).std().values
    F["es_z_ret60"] = F["es_ret60"].values / np.where(es_sig > 0, es_sig, np.nan)
    F["es_rv60"] = es_d.rolling(60).std().values
    nq_sig = dmid.rolling(ZWIN, min_periods=ZMIN).std().values
    nq_z = F["ret60"].values / np.where(nq_sig > 0, nq_sig, np.nan)
    F["nq_es_z_diff60"] = nq_z - F["es_z_ret60"].values
    sa = np.sign(F["es_ret60"].values) * np.sign(F["ret60"].values)
    F["sign_agree"] = np.where(
        np.isnan(F["es_ret60"].values) | np.isnan(F["ret60"].values),
        np.nan, (sa > 0).astype(np.float64))
    nev = fe["es_n_ev_raw"].fillna(0.0).values.astype(np.float64)
    F["es_n_ev"] = np.where(ok, nev, np.nan)   # substitution for es_spread_t

    R = F.iloc[starts].copy().reset_index(drop=True)
    for dname, dv, A, B in LABELS:
        R[f"lab_{dname}_{A}_{B}"] = label_scan(ml, hi, lo, starts, dv, float(A),
                                               float(B), CAP)
    return R, ml, hi, lo


def leakage_probe(tag, n_probe=200):
    """ASSERTION 1 (verbatim C5): perturbing hi/lo at the decision second t must
    leave every label unchanged (the label window starts at t+1)."""
    R, ml, hi, lo = build_session(tag)
    starts = R["t"].values.astype(np.int64)
    rng = np.random.default_rng(SEED)
    pick = rng.choice(len(starts), size=min(n_probe, len(starts)), replace=False)
    n_checked = 0
    for j in pick:
        t0 = starts[j]
        hi2 = hi.copy()
        lo2 = lo.copy()
        hi2[t0] = ml[t0] + 1000.0
        lo2[t0] = ml[t0] - 1000.0
        one = np.array([t0], np.int64)
        for dname, dv, A, B in LABELS:
            l_orig = label_scan(ml, hi, lo, one, dv, float(A), float(B), CAP)[0]
            l_pert = label_scan(ml, hi2, lo2, one, dv, float(A), float(B), CAP)[0]
            assert l_orig == l_pert, (
                f"LEAKAGE: label {dname}+{A}/-{B} at t={t0} changed when second t "
                f"was perturbed")
            n_checked += 1
    return n_checked


def brier(y, p):
    return float(np.mean((p - y) ** 2))


def perm_importance(model, Xv, yv, feats, rng, nrep=3):
    """Mean Brier increase on the validation block when one feature is permuted
    (C5 construction, parameterized by feature list)."""
    p0 = model.predict_proba(Xv)[:, 1]
    b0 = brier(yv, p0)
    imp = np.zeros(len(feats))
    for j in range(len(feats)):
        acc = 0.0
        for _ in range(nrep):
            Xp = Xv.copy()
            Xp[:, j] = Xp[rng.permutation(len(Xp)), j]
            acc += brier(yv, model.predict_proba(Xp)[:, 1]) - b0
        imp[j] = acc / nrep
    return imp


def lift_with_ci(dfp, top_mask):
    """Pooled top-decile P, baseline P, lift, day-clustered (session-bootstrap)
    95% CIs — VERBATIM C5. Seed 20260808, 1000 reps."""
    tmp = dfp.assign(top=top_mask)
    per = tmp.groupby("session").agg(all_n=("y", "size"), all_t=("y", "sum"))
    pt = tmp[tmp["top"]].groupby("session").agg(top_n=("y", "size"),
                                               top_t=("y", "sum"))
    per = per.join(pt).fillna(0)
    an = per["all_n"].values.astype(float)
    at = per["all_t"].values.astype(float)
    tn = per["top_n"].values.astype(float)
    tt = per["top_t"].values.astype(float)
    p_all = at.sum() / an.sum()
    p_top = tt.sum() / tn.sum()
    rng = np.random.default_rng(SEED)
    nsess = len(per)
    lifts = np.empty(NREPS)
    ptops = np.empty(NREPS)
    for r in range(NREPS):
        b = rng.choice(nsess, nsess, replace=True)
        tb = tn[b].sum()
        ptops[r] = tt[b].sum() / tb if tb > 0 else np.nan
        lifts[r] = ptops[r] - at[b].sum() / an[b].sum()
    lifts = lifts[~np.isnan(lifts)]
    ptops = ptops[~np.isnan(ptops)]
    return dict(p_all=p_all, p_top=p_top, lift=p_top - p_all,
                lift_lo=float(np.percentile(lifts, 2.5)),
                lift_hi=float(np.percentile(lifts, 97.5)),
                ptop_lo=float(np.percentile(ptops, 2.5)),
                ptop_hi=float(np.percentile(ptops, 97.5)),
                n_top=int(tn.sum()), n_all=int(an.sum()))


def paired_delta_ci(Pa, Pb):
    """Paired session-bootstrap 95% CI for delta(lift) = lift(b) - lift(a).
    Same session draws applied to both runs per rep (day-clustered), seed
    20260808, 1000 reps. Pa/Pb are pooled-OOF frames with session/y/top,
    row-aligned (asserted by caller)."""
    key = sorted(Pa["session"].unique())
    idx = {s: i for i, s in enumerate(key)}
    nsess = len(key)

    def agg(P):
        an = np.zeros(nsess); at = np.zeros(nsess)
        tn = np.zeros(nsess); tt = np.zeros(nsess)
        g = P.groupby("session")
        for s, gg in g:
            i = idx[s]
            an[i] = len(gg); at[i] = gg["y"].sum()
            tn[i] = gg["top"].sum(); tt[i] = gg.loc[gg["top"], "y"].sum()
        return an, at, tn, tt

    an_a, at_a, tn_a, tt_a = agg(Pa)
    an_b, at_b, tn_b, tt_b = agg(Pb)
    assert np.array_equal(an_a, an_b) and np.array_equal(at_a, at_b), \
        "paired delta: per-session row/label counts differ between runs"
    lift_a = tt_a.sum() / tn_a.sum() - at_a.sum() / an_a.sum()
    lift_b = tt_b.sum() / tn_b.sum() - at_b.sum() / an_b.sum()
    rng = np.random.default_rng(SEED)
    deltas = np.empty(NREPS)
    for r in range(NREPS):
        b = rng.choice(nsess, nsess, replace=True)
        ta, tb = tn_a[b].sum(), tn_b[b].sum()
        if ta <= 0 or tb <= 0:
            deltas[r] = np.nan
            continue
        la = tt_a[b].sum() / ta - at_a[b].sum() / an_a[b].sum()
        lb = tt_b[b].sum() / tb - at_b[b].sum() / an_b[b].sum()
        deltas[r] = lb - la
    deltas = deltas[~np.isnan(deltas)]
    return dict(delta=lift_b - lift_a,
                delta_lo=float(np.percentile(deltas, 2.5)),
                delta_hi=float(np.percentile(deltas, 97.5)))


def make_models():
    return {
        "logit": Pipeline([("sc", StandardScaler()),
                           ("lr", LogisticRegression(penalty="l2", C=1.0,
                                                     solver="lbfgs",
                                                     max_iter=2000))]),
        "hgb": HistGradientBoostingClassifier(max_depth=3, early_stopping=True,
                                              max_iter=300, random_state=SEED),
    }


def run_ceiling(D, folds, feats, run_id):
    """One full C5 pass (4 labels x 2 models) on feature list `feats`.
    Model loop is the C5 loop verbatim, with `run` tagged into every output."""
    oof_rows, met_rows, cal_rows, foldlift_rows, imp_rows = [], [], [], [], []
    for dname, dv, A, B in LABELS:
        lc = f"lab_{dname}_{A}_{B}"
        lab_id = f"{dname}_{A}_{B}"
        sub = D[D[lc] >= 0]
        for mname in make_models().keys():
            preds, imp_acc, imp_w = [], np.zeros(len(feats)), 0.0
            fold_brier_rows = []
            for v, tr, va in folds:
                trd = sub[sub["session"].isin(tr)]
                vad = sub[sub["session"].isin(va)]
                Xtr = trd[feats].values.astype(np.float64)
                ytr = (trd[lc] == 1).values.astype(int)
                Xva = vad[feats].values.astype(np.float64)
                yva = (vad[lc] == 1).values.astype(int)
                model = make_models()[mname]
                model.fit(Xtr, ytr)
                p = model.predict_proba(Xva)[:, 1]
                base_tr = ytr.mean()
                preds.append(pd.DataFrame(dict(session=vad["session"].values,
                                               t=vad["t"].values, fold=v, y=yva, p=p,
                                               base_tr=base_tr)))
                rng = np.random.default_rng(SEED + v)
                imp = perm_importance(model, Xva, yva, feats, rng)
                imp_acc += imp * len(yva)
                imp_w += len(yva)
                fold_brier_rows.append(dict(fold=v, n=len(yva),
                                            brier=brier(yva, p),
                                            brier_base=brier(yva,
                                                             np.full(len(yva),
                                                                     base_tr))))
            P = pd.concat(preds, ignore_index=True)
            P["label"] = lab_id
            P["model"] = mname
            P["run"] = run_id

            bri = brier(P["y"].values, P["p"].values)
            bri_base = brier(P["y"].values, P["base_tr"].values)
            top = np.zeros(len(P), bool)
            for v, _, _ in folds:
                m = P["fold"].values == v
                thr = np.quantile(P.loc[m, "p"].values, 0.9)
                top[m & (P["p"].values >= thr)] = True
            P["top"] = top
            oof_rows.append(P)
            res = lift_with_ci(P[["session", "y"]], top)
            fl = []
            for v, _, _ in folds:
                m = P["fold"].values == v
                pf = P.loc[m]
                tf = top[m]
                l_v = pf.loc[tf, "y"].mean() - pf["y"].mean()
                fl.append(l_v)
                foldlift_rows.append(dict(run=run_id, label=lab_id, model=mname,
                                          fold=v, n_val=int(m.sum()),
                                          n_top=int(tf.sum()),
                                          base_P=pf["y"].mean(),
                                          top_P=pf.loc[tf, "y"].mean(), lift=l_v,
                                          brier=fold_brier_rows[v - 1]["brier"],
                                          brier_base=fold_brier_rows[v - 1]
                                          ["brier_base"]))
            gap = C1_GAP[(dname, A, B)]
            pass5 = (res["lift"] >= 0.05) and (res["lift_lo"] > 0)
            stable7 = (res["lift"] >= 0.07) and (res["lift_lo"] > 0) and \
                      all(x > 0 for x in fl)
            met_rows.append(dict(run=run_id, label=lab_id, model=mname,
                                 n_val=res["n_all"], n_top=res["n_top"],
                                 brier=bri, brier_base=bri_base,
                                 brier_skill=1 - bri / bri_base,
                                 base_P=res["p_all"], top_P=res["p_top"],
                                 ptop_lo=res["ptop_lo"], ptop_hi=res["ptop_hi"],
                                 lift=res["lift"], lift_lo=res["lift_lo"],
                                 lift_hi=res["lift_hi"],
                                 fold_lifts=";".join(f"{x:+.4f}" for x in fl),
                                 c1_gap=gap, lift_minus_gap=res["lift"] - gap,
                                 pass_5pp=pass5, pass_7pp_stable=stable7))
            q = np.quantile(P["p"].values, np.linspace(0, 1, 11))
            q[0], q[-1] = -np.inf, np.inf
            binid = np.digitize(P["p"].values, q[1:-1])
            for bidx in range(10):
                m = binid == bidx
                if m.sum() == 0:
                    continue
                cal_rows.append(dict(run=run_id, label=lab_id, model=mname,
                                     bin=bidx, n=int(m.sum()),
                                     p_pred_mean=float(P.loc[m, "p"].mean()),
                                     p_real=float(P.loc[m, "y"].mean())))
            imp_mean = imp_acc / imp_w
            order = np.argsort(-imp_mean)
            for rank, j in enumerate(order):
                imp_rows.append(dict(run=run_id, label=lab_id, model=mname,
                                     rank=rank + 1, feature=feats[j],
                                     is_es=feats[j] in ES_FEATS,
                                     brier_increase=float(imp_mean[j])))
            print(f"\n--- [{run_id}] {lab_id} | {mname} ---")
            print(f"  Brier {bri:.5f} vs baseline {bri_base:.5f} "
                  f"(skill {1 - bri / bri_base:+.4f})")
            print(f"  base P(target) {res['p_all']:.4f} | top-decile P "
                  f"{res['p_top']:.4f} [{res['ptop_lo']:.4f},{res['ptop_hi']:.4f}] "
                  f"(n_top={res['n_top']})")
            print(f"  LIFT {100 * res['lift']:+.2f}pp "
                  f"CI [{100 * res['lift_lo']:+.2f},{100 * res['lift_hi']:+.2f}]pp | "
                  f"C1 gap {100 * gap:.2f}pp | lift-gap "
                  f"{100 * (res['lift'] - gap):+.2f}pp")
            print(f"  fold lifts (pp): "
                  + " ".join(f"{100 * x:+.2f}" for x in fl)
                  + f" | pass>=5pp:{pass5} pass>=7pp-stable:{stable7}")
            print("  perm importance top-10: "
                  + ", ".join(f"{feats[j]}({imp_mean[j] * 1e4:.2f}e-4)"
                              for j in order[:10]))
    return (pd.concat(oof_rows, ignore_index=True), pd.DataFrame(met_rows),
            pd.DataFrame(cal_rows), pd.DataFrame(foldlift_rows),
            pd.DataFrame(imp_rows))


def main():
    print(f"W6-T2 ceiling increment (FSS-10 decisive) | seed={SEED} reps={NREPS} "
          f"clock={CLOCK}s cap={CAP}s minhist={MINHIST}s es_stale<={ES_STALE}s "
          f"zwin={ZWIN}s zmin={ZMIN}s")
    print("es_spread_t SUBSTITUTION: ES sechilo carries union-BBO mid only "
          "(no bid/ask) -> ES spread not constructible; es_n_ev (per-second ES "
          "event count) substituted per task instruction.")
    sessions = sorted(os.path.basename(p)[:-8]
                      for p in glob.glob(os.path.join(SH, "s*.parquet")))
    missing_es = [t for t in sessions
                  if not os.path.exists(os.path.join(ESD, "es_" + t + ".parquet"))]
    assert not missing_es, f"ES sechilo missing for: {missing_es}"
    print(f"sessions: {len(sessions)}  ({sessions[0]} .. {sessions[-1]}) — same "
          f"37-tag list as C5; every tag has an ES partner file")
    print("caveats: NQ s20250902 quote-dead (self-skips, as in C5); "
          "es_s20260519 ES feed truncated at 14:43:22 (afternoon rows drop via "
          "the 5s staleness rule -> excluded from BOTH runs, kept with caveat)")

    # ---- ASSERTION 1: feature/label window no-overlap (empirical) ----
    probe_tag = sessions[len(sessions) // 2]
    nch = leakage_probe(probe_tag)
    print(f"ASSERTION 1 PASSED: label windows start at t+1s and never overlap the "
          f"feature second t — perturbing hi/lo at t left all labels unchanged "
          f"({nch} row-label checks on {probe_tag}).")

    # ---- build dataset ----
    frames = []
    for tag in sessions:
        R, _, _, _ = build_session(tag)
        if R is None:
            print(tag, "SKIPPED: zero quote-alive RTH seconds (dead quote feed; "
                  "same handling as census)", flush=True)
            continue
        frames.append(R)
        n_es_nan = int(R[ES_FEATS].isna().any(axis=1).sum())
        print(tag, "rows:", len(R), "| ES-feature-NaN rows:", n_es_nan, flush=True)
    D = pd.concat(frames, ignore_index=True)
    n_raw = len(D)
    lab_cols = [f"lab_{d}_{A}_{B}" for d, _, A, B in LABELS]
    n_hist = int((D["t"] < MINHIST).sum())
    D = D[D["t"] >= MINHIST]
    n_nan = int(D[NQ_FEATS].isna().any(axis=1).sum())
    D = D.dropna(subset=NQ_FEATS)
    n_c5_equiv = len(D)          # sample the original C5 would have kept
    n_esnan = int(D[ES_FEATS].isna().any(axis=1).sum())
    D = D.dropna(subset=ES_FEATS).reset_index(drop=True)
    D["date"] = pd.to_datetime(D["session"].str[1:], format="%Y%m%d")
    print(f"\nclock rows: {n_raw} raw | dropped t<{MINHIST}: {n_hist} | "
          f"dropped NQ-NaN-feature: {n_nan} | C5-equivalent rows: {n_c5_equiv} | "
          f"dropped ES-feature-NaN (same-sample rule): {n_esnan} | "
          f"modeling rows (BOTH runs): {len(D)}")
    for c in lab_cols:
        neither = int((D[c] == -1).sum())
        print(f"  {c}: neither-hit excluded {neither} "
              f"({100 * neither / len(D):.2f}%) | "
              f"P(target) over decided rows: "
              f"{(D[c] == 1).sum() / max(1, (D[c] >= 0).sum()):.4f}")
    D.to_parquet(os.path.join(OUTD, "t2_dataset.parquet"), index=False)
    ds = D.groupby("session").agg(rows=("t", "size"), **{
        f"neither_{d}_{A}_{B}": (f"lab_{d}_{A}_{B}", lambda x: int((x == -1).sum()))
        for d, _, A, B in LABELS})
    ds.to_csv(os.path.join(OUTD, "t2_dataset_summary.csv"))

    # ---- folds: chronological session-grouped expanding 5-fold (C5 verbatim,
    # built from the SAME 37-session list) ----
    blocks = [list(b) for b in np.array_split(np.array(sessions), NFOLDS)]
    print("\nfold blocks (chronological):")
    for i, b in enumerate(blocks):
        print(f"  block {i}: {len(b)} sessions  {b[0]} .. {b[-1]}")
    folds = []
    for v in range(1, NFOLDS):
        tr = [s for b in blocks[:v] for s in b]
        va = blocks[v]
        assert len(set(tr) & set(va)) == 0, "session appears in train AND validation"
        assert max(tr) < min(va), "training session not strictly earlier than validation"
        folds.append((v, tr, va))
    print("ASSERTION 2 PASSED: in all 4 folds, train/validation session sets are "
          "disjoint and every training session is strictly earlier than every "
          "validation session.")

    # ---- run (a) reproduction control, then (b) augmented, on the SAME rows ----
    all_oof, all_met, all_cal, all_fl, all_imp = [], [], [], [], []
    for run_id, feats in RUNS:
        print(f"\n================ RUN {run_id}: {len(feats)} features "
              f"================")
        oof, met, cal, fl, imp = run_ceiling(D, folds, feats, run_id)
        all_oof.append(oof); all_met.append(met); all_cal.append(cal)
        all_fl.append(fl); all_imp.append(imp)
    OOF = pd.concat(all_oof, ignore_index=True)
    MET = pd.concat(all_met, ignore_index=True)
    OOF.to_parquet(os.path.join(OUTD, "t2_oof_predictions.parquet"), index=False)
    MET.to_csv(os.path.join(OUTD, "t2_metrics.csv"), index=False)
    pd.concat(all_cal, ignore_index=True).to_csv(
        os.path.join(OUTD, "t2_calibration.csv"), index=False)
    pd.concat(all_fl, ignore_index=True).to_csv(
        os.path.join(OUTD, "t2_fold_lifts.csv"), index=False)
    IMP = pd.concat(all_imp, ignore_index=True)
    IMP.to_csv(os.path.join(OUTD, "t2_perm_importance.csv"), index=False)

    # ---- reproduction check: (a) vs original C5 ----
    c5 = pd.read_csv(C5M)
    A = MET[MET["run"] == "a_nq27"].set_index(["label", "model"])
    C = c5.set_index(["label", "model"])
    rep_rows = []
    print("\n=== REPRODUCTION CHECK: run (a) [27 NQ feats, same-sample] vs "
          "original C5 ===")
    print(f"(sample: C5 modeling rows 27299 -> same-sample rows {len(D)}; "
          f"difference = ES-feature-NaN rows, dominated by the truncated "
          f"es_s20260519 afternoon)")
    repro_ok = True
    for key in C.index:
        dl = A.loc[key, "lift"] - C.loc[key, "lift"]
        dk = A.loc[key, "brier_skill"] - C.loc[key, "brier_skill"]
        flip = bool(A.loc[key, "pass_5pp"]) != bool(C.loc[key, "pass_5pp"])
        ok = (abs(dl) <= REPRO_TOL_LIFT) and (abs(dk) <= REPRO_TOL_SKILL) \
            and not flip
        repro_ok &= ok
        rep_rows.append(dict(label=key[0], model=key[1],
                             lift_c5=C.loc[key, "lift"],
                             lift_a=A.loc[key, "lift"], dlift=dl,
                             skill_c5=C.loc[key, "brier_skill"],
                             skill_a=A.loc[key, "brier_skill"], dskill=dk,
                             n_val_c5=int(C.loc[key, "n_val"]),
                             n_val_a=int(A.loc[key, "n_val"]),
                             pass5_c5=bool(C.loc[key, "pass_5pp"]),
                             pass5_a=bool(A.loc[key, "pass_5pp"]),
                             within_tol=ok))
        print(f"  {key[0]:12s} {key[1]:5s} lift C5 {100*C.loc[key,'lift']:+.2f}pp "
              f"-> (a) {100*A.loc[key,'lift']:+.2f}pp (d {100*dl:+.2f}pp) | "
              f"skill C5 {C.loc[key,'brier_skill']:+.4f} -> "
              f"{A.loc[key,'brier_skill']:+.4f} (d {dk:+.4f}) | "
              f"n {int(C.loc[key,'n_val'])}->{int(A.loc[key,'n_val'])} | "
              f"tol_ok={ok}")
    pd.DataFrame(rep_rows).to_csv(os.path.join(OUTD, "t2_repro_comparison.csv"),
                                  index=False)
    if repro_ok:
        print(f"REPRODUCTION PASSED: all 8 label/model cells within tolerance "
              f"(|dlift|<={100*REPRO_TOL_LIFT:.1f}pp, "
              f"|dskill|<={REPRO_TOL_SKILL}, no pass_5pp flip).")
    else:
        print("REPRODUCTION FAILED: at least one cell outside tolerance — per "
              "frozen instruction, STOP: the (b) readout below is NOT "
              "interpretable and no FSS-10 verdict is issued.")

    # ---- paired delta (b) - (a) with day-clustered CI ----
    delta_rows = []
    print("\n=== DELTA top-decile lift: (b) 27NQ+8ES minus (a) 27NQ — paired "
          "session bootstrap ===")
    B_ = MET[MET["run"] == "b_nq27_es8"].set_index(["label", "model"])
    for dname, dv, A_, B__ in LABELS:
        lab_id = f"{dname}_{A_}_{B__}"
        for mname in ("logit", "hgb"):
            Pa = OOF[(OOF["run"] == "a_nq27") & (OOF["label"] == lab_id)
                     & (OOF["model"] == mname)].reset_index(drop=True)
            Pb = OOF[(OOF["run"] == "b_nq27_es8") & (OOF["label"] == lab_id)
                     & (OOF["model"] == mname)].reset_index(drop=True)
            assert np.array_equal(Pa["session"].values, Pb["session"].values)
            assert np.array_equal(Pa["t"].values, Pb["t"].values)
            assert np.array_equal(Pa["y"].values, Pb["y"].values)
            dres = paired_delta_ci(Pa[["session", "y", "top"]],
                                   Pb[["session", "y", "top"]])
            ra = MET[(MET["run"] == "a_nq27") & (MET["label"] == lab_id)
                     & (MET["model"] == mname)].iloc[0]
            rb = MET[(MET["run"] == "b_nq27_es8") & (MET["label"] == lab_id)
                     & (MET["model"] == mname)].iloc[0]
            delta_rows.append(dict(
                label=lab_id, model=mname,
                lift_a=ra["lift"], lift_a_lo=ra["lift_lo"], lift_a_hi=ra["lift_hi"],
                lift_b=rb["lift"], lift_b_lo=rb["lift_lo"], lift_b_hi=rb["lift_hi"],
                delta=dres["delta"], delta_lo=dres["delta_lo"],
                delta_hi=dres["delta_hi"],
                brier_skill_a=ra["brier_skill"], brier_skill_b=rb["brier_skill"],
                d_brier_skill=rb["brier_skill"] - ra["brier_skill"],
                pass5_a=bool(ra["pass_5pp"]), pass5_b=bool(rb["pass_5pp"]),
                pass7_b=bool(rb["pass_7pp_stable"])))
            print(f"  {lab_id:12s} {mname:5s} lift(a) {100*ra['lift']:+.2f}pp "
                  f"[{100*ra['lift_lo']:+.2f},{100*ra['lift_hi']:+.2f}] | "
                  f"lift(b) {100*rb['lift']:+.2f}pp "
                  f"[{100*rb['lift_lo']:+.2f},{100*rb['lift_hi']:+.2f}] | "
                  f"DELTA {100*dres['delta']:+.2f}pp "
                  f"[{100*dres['delta_lo']:+.2f},{100*dres['delta_hi']:+.2f}] | "
                  f"skill {ra['brier_skill']:+.4f}->{rb['brier_skill']:+.4f} | "
                  f"pass5(b)={bool(rb['pass_5pp'])}")
    DL = pd.DataFrame(delta_rows)
    DL.to_csv(os.path.join(OUTD, "t2_delta.csv"), index=False)

    # ---- ES-feature permutation importance in (b) ----
    print("\n=== ES-feature permutation importance in run (b) (rank of 35; "
          "Brier increase x1e4) ===")
    ib = IMP[(IMP["run"] == "b_nq27_es8") & (IMP["is_es"])]
    for (lab_id, mname), gg in ib.groupby(["label", "model"]):
        gg = gg.sort_values("rank")
        print(f"  {lab_id:12s} {mname:5s} "
              + ", ".join(f"{f}(rank {int(rk)}/35, {bi*1e4:.2f})"
                          for f, rk, bi in zip(gg["feature"], gg["rank"],
                                               gg["brier_increase"])))

    # ---- frozen verdict ----
    print("\n=== FROZEN VERDICT (spec T2 interpretation rule) ===")
    if not repro_ok:
        print("VERDICT: REPRODUCTION-FAILED — stopped; no FSS-10 ruling.")
    else:
        any5_b = bool(DL["pass5_b"].any())
        promote = DL[(DL["pass5_b"]) & (~DL["pass5_a"])]
        best = DL.loc[DL["lift_b"].idxmax()]
        print(f"best (b) lift: {best['label']} {best['model']} "
              f"{100*best['lift_b']:+.2f}pp "
              f"[{100*best['lift_b_lo']:+.2f},{100*best['lift_b_hi']:+.2f}] | "
              f"delta {100*best['delta']:+.2f}pp "
              f"[{100*best['delta_lo']:+.2f},{100*best['delta_hi']:+.2f}]")
        if not any5_b:
            print("VERDICT: NO label/model in (b) reaches the C5 5pp bar "
                  "(lift>=5pp AND CI_lo>0) -> FSS-10 NEGATIVE; the ES-"
                  "information hypothesis is CLOSED at retail-accessible lags.")
        elif len(promote) > 0:
            print("VERDICT: (b) reaches >=5pp where (a) does not -> ES adds "
                  "MATERIAL information -> conversion spec next wave. Cells: "
                  + "; ".join(f"{r.label}/{r.model}" for r in promote.itertuples()))
        else:
            print("VERDICT: (b) reaches >=5pp only where (a) already did -> ES "
                  "adds no material increment; FSS-10 NEGATIVE on the "
                  "increment criterion.")
    print("\nW6T2 DONE")


if __name__ == "__main__":
    main()
