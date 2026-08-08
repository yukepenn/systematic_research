"""W5-C5 — Predictability-ceiling test (Amendment 6 par.8). MEASUREMENT, not a strategy.
Frozen spec: research/scalping_lab/specs/W5_programs_wave.md section C5 (committed before
readout). Seed 20260808; 1000 bootstrap reps; session (day-clustered) resampling.

Frozen-spec interpretation notes (documented in w5c5_report.md):
- Decision clock: every 30th quote-alive RTH second (dec_idx[::30]) — identical to the
  census excursion-surface clock, so the C1 economic-gap comparison is apples-to-apples.
- Features: the 27-column census causal library (trailing windows only, incl. time-of-day)
  rebuilt exactly as in opportunity_census.py. Rows with t < 300 (insufficient trailing
  history) or any NaN feature are dropped and counted.
- Labels: target-first booleans for (+24,-8) and (+32,-10), long and short, per-second
  hi/lo scan starting at t+1 (never t), cap 600 s, conservative same-second-both-crossed
  -> adverse (label 0). Neither-hit rows excluded per label, counts reported.
- Models: (1) L2 logistic regression, StandardScaler fit INSIDE each fold on training
  sessions only; (2) HistGradientBoostingClassifier(max_depth=3, early_stopping=True)
  [its internal early-stopping holdout is a random 10% of TRAINING rows only — no
  validation-session contact]. pyGAM used only if importable.
- Validation: chronological session-grouped expanding 5-fold: 37 sessions sorted by date,
  split into 5 consecutive blocks; blocks 2..5 are the 4 validation folds; training =
  all sessions strictly earlier than the block. NO pooled-then-split preprocessing.
- Leakage guards, both printed: (1) empirical no-overlap test — perturbing hi/lo at the
  decision second t leaves every label unchanged (scan starts t+1); (2) train/validation
  session disjointness + strict chronological ordering asserted in every fold.
- Top decile: within each validation fold, rows with predicted p >= 90th percentile of
  that fold's validation predictions. LIFT = pooled top-decile realized P(target) minus
  pooled validation baseline P(target); day-clustered CI = resample validation sessions
  (seed 20260808, 1000 reps), recompute both terms per rep.
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
LABELS = [("long", 1, 24, 8), ("long", 1, 32, 10),
          ("short", -1, 24, 8), ("short", -1, 32, 10)]
C1_GAP = {("long", 24, 8): 0.0873, ("short", 24, 8): 0.0909,
          ("long", 32, 10): 0.0703, ("short", 32, 10): 0.0737}
FEATS = ["ret5", "ret10", "ret30", "ret60", "ret300", "rv60", "rv300", "tv60", "eff60",
         "range300", "dist_hi", "dist_lo", "secs_since_hi", "secs_since_lo",
         "trades10", "trades60", "vol10", "vol60", "upd10", "upd60", "sflow10",
         "sflow60", "act_accel", "nsflow60", "spread", "spread60", "tod"]

SH = "research/scalping_lab/substrate/sechilo/NQ"
GR = "research/scalping_lab/substrate/grid1s/NQ"
OUTD = "research/scalping_lab/artifacts/w5_c5"
os.makedirs(OUTD, exist_ok=True)

try:
    import pygam  # noqa: F401
    HAVE_PYGAM = True
except Exception:
    HAVE_PYGAM = False


@njit(cache=True)
def label_scan(ml, hi, lo, starts, dirsign, A, B, cap):
    """Target-first label per start. Scan begins at t0+1 (label never overlaps the
    feature second t0). 1 = target first, 0 = adverse first (same-second both-crossed
    -> adverse, conservative), -1 = neither hit within cap."""
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
    """House-pattern merge + census causal feature library + 4 label columns on the
    every-30s decision clock. Returns clock-row DataFrame."""
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

    R = F.iloc[starts].copy().reset_index(drop=True)
    for dname, dv, A, B in LABELS:
        R[f"lab_{dname}_{A}_{B}"] = label_scan(ml, hi, lo, starts, dv, float(A),
                                               float(B), CAP)
    return R, ml, hi, lo


def leakage_probe(tag, n_probe=200):
    """ASSERTION 1: perturbing hi/lo at the decision second t must leave every label
    unchanged (the label window starts at t+1). Empirical, per-row test."""
    R, ml, hi, lo = build_session(tag)
    starts = R["t"].values.astype(np.int64)
    rng = np.random.default_rng(SEED)
    pick = rng.choice(len(starts), size=min(n_probe, len(starts)), replace=False)
    n_checked = 0
    for j in pick:
        t0 = starts[j]
        hi2 = hi.copy()
        lo2 = lo.copy()
        hi2[t0] = ml[t0] + 1000.0   # would instantly hit any barrier if second t leaked
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


def perm_importance(model, Xv, yv, rng, nrep=3):
    """Mean Brier increase on the validation block when one feature is permuted."""
    p0 = model.predict_proba(Xv)[:, 1]
    b0 = brier(yv, p0)
    imp = np.zeros(len(FEATS))
    for j in range(len(FEATS)):
        acc = 0.0
        for _ in range(nrep):
            Xp = Xv.copy()
            Xp[:, j] = Xp[rng.permutation(len(Xp)), j]
            acc += brier(yv, model.predict_proba(Xp)[:, 1]) - b0
        imp[j] = acc / nrep
    return imp


def lift_with_ci(dfp, top_mask):
    """Pooled top-decile P, baseline P, lift, and day-clustered (session-bootstrap)
    95% CIs for both the lift and the top-decile P. Seed 20260808, 1000 reps."""
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


def main():
    print(f"W5-C5 predictability-ceiling | seed={SEED} reps={NREPS} clock={CLOCK}s "
          f"cap={CAP}s minhist={MINHIST}s")
    print(f"pyGAM importable: {HAVE_PYGAM}"
          + ("" if HAVE_PYGAM else "  -> GAM skipped (per spec: only if present)"))
    sessions = sorted(os.path.basename(p)[:-8]
                      for p in glob.glob(os.path.join(SH, "s*.parquet")))
    print(f"sessions: {len(sessions)}  ({sessions[0]} .. {sessions[-1]})")

    # ---- ASSERTION 1: feature/label window no-overlap (empirical perturbation) ----
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
        print(tag, "rows:", len(R), flush=True)
    D = pd.concat(frames, ignore_index=True)
    n_raw = len(D)
    lab_cols = [f"lab_{d}_{A}_{B}" for d, _, A, B in LABELS]
    n_hist = int((D["t"] < MINHIST).sum())
    D = D[D["t"] >= MINHIST]
    n_nan = int(D[FEATS].isna().any(axis=1).sum())
    D = D.dropna(subset=FEATS).reset_index(drop=True)
    D["date"] = pd.to_datetime(D["session"].str[1:], format="%Y%m%d")
    print(f"\nclock rows: {n_raw} raw | dropped t<{MINHIST}: {n_hist} | "
          f"dropped NaN-feature: {n_nan} | modeling rows: {len(D)}")
    neither = {c: int((D[c] == -1).sum()) for c in lab_cols}
    for c in lab_cols:
        print(f"  {c}: neither-hit excluded {neither[c]} "
              f"({100 * neither[c] / len(D):.2f}%) | "
              f"P(target) over decided rows: "
              f"{(D[c] == 1).sum() / max(1, (D[c] >= 0).sum()):.4f}")
    D.to_parquet(os.path.join(OUTD, "w5c5_dataset.parquet"), index=False)
    ds = D.groupby("session").agg(rows=("t", "size"), **{
        f"neither_{d}_{A}_{B}": (f"lab_{d}_{A}_{B}", lambda x: int((x == -1).sum()))
        for d, _, A, B in LABELS})
    ds.to_csv(os.path.join(OUTD, "w5c5_dataset_summary.csv"))

    # ---- folds: chronological session-grouped expanding 5-fold ----
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

    # ---- models x labels ----
    def make_models():
        return {
            "logit": Pipeline([("sc", StandardScaler()),
                               ("lr", LogisticRegression(penalty="l2", C=1.0,
                                                         solver="lbfgs",
                                                         max_iter=2000))]),
            "hgb": HistGradientBoostingClassifier(max_depth=3, early_stopping=True,
                                                  max_iter=300, random_state=SEED),
        }

    oof_rows, met_rows, cal_rows, foldlift_rows, imp_rows = [], [], [], [], []
    for dname, dv, A, B in LABELS:
        lc = f"lab_{dname}_{A}_{B}"
        lab_id = f"{dname}_{A}_{B}"
        sub = D[D[lc] >= 0]
        for mname in make_models().keys():
            preds, imp_acc, imp_w = [], np.zeros(len(FEATS)), 0.0
            fold_brier_rows = []
            for v, tr, va in folds:
                trd = sub[sub["session"].isin(tr)]
                vad = sub[sub["session"].isin(va)]
                Xtr = trd[FEATS].values.astype(np.float64)
                ytr = (trd[lc] == 1).values.astype(int)
                Xva = vad[FEATS].values.astype(np.float64)
                yva = (vad[lc] == 1).values.astype(int)
                model = make_models()[mname]
                model.fit(Xtr, ytr)
                p = model.predict_proba(Xva)[:, 1]
                base_tr = ytr.mean()
                preds.append(pd.DataFrame(dict(session=vad["session"].values,
                                               t=vad["t"].values, fold=v, y=yva, p=p,
                                               base_tr=base_tr)))
                rng = np.random.default_rng(SEED + v)
                imp = perm_importance(model, Xva, yva, rng)
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
            oof_rows.append(P)

            bri = brier(P["y"].values, P["p"].values)
            bri_base = brier(P["y"].values, P["base_tr"].values)
            # top decile per fold
            top = np.zeros(len(P), bool)
            for v, _, _ in folds:
                m = P["fold"].values == v
                thr = np.quantile(P.loc[m, "p"].values, 0.9)
                top[m & (P["p"].values >= thr)] = True
            res = lift_with_ci(P[["session", "y"]], top)
            # per-fold lifts (stability)
            fl = []
            for v, _, _ in folds:
                m = P["fold"].values == v
                pf = P.loc[m]
                tf = top[m]
                l_v = pf.loc[tf, "y"].mean() - pf["y"].mean()
                fl.append(l_v)
                foldlift_rows.append(dict(label=lab_id, model=mname, fold=v,
                                          n_val=int(m.sum()), n_top=int(tf.sum()),
                                          base_P=pf["y"].mean(),
                                          top_P=pf.loc[tf, "y"].mean(), lift=l_v,
                                          brier=fold_brier_rows[v - 1]["brier"],
                                          brier_base=fold_brier_rows[v - 1]
                                          ["brier_base"]))
            gap = C1_GAP[(dname, A, B)]
            pass5 = (res["lift"] >= 0.05) and (res["lift_lo"] > 0)
            stable7 = (res["lift"] >= 0.07) and (res["lift_lo"] > 0) and \
                      all(x > 0 for x in fl)
            met_rows.append(dict(label=lab_id, model=mname, n_val=res["n_all"],
                                 n_top=res["n_top"], brier=bri, brier_base=bri_base,
                                 brier_skill=1 - bri / bri_base,
                                 base_P=res["p_all"], top_P=res["p_top"],
                                 ptop_lo=res["ptop_lo"], ptop_hi=res["ptop_hi"],
                                 lift=res["lift"], lift_lo=res["lift_lo"],
                                 lift_hi=res["lift_hi"],
                                 fold_lifts=";".join(f"{x:+.4f}" for x in fl),
                                 c1_gap=gap, lift_minus_gap=res["lift"] - gap,
                                 pass_5pp=pass5, pass_7pp_stable=stable7))
            # calibration table: 10 equal-count bins on pooled validation predictions
            q = np.quantile(P["p"].values, np.linspace(0, 1, 11))
            q[0], q[-1] = -np.inf, np.inf
            binid = np.digitize(P["p"].values, q[1:-1])
            for bidx in range(10):
                m = binid == bidx
                if m.sum() == 0:
                    continue
                cal_rows.append(dict(label=lab_id, model=mname, bin=bidx,
                                     n=int(m.sum()),
                                     p_pred_mean=float(P.loc[m, "p"].mean()),
                                     p_real=float(P.loc[m, "y"].mean())))
            imp_mean = imp_acc / imp_w
            order = np.argsort(-imp_mean)
            for rank, j in enumerate(order):
                imp_rows.append(dict(label=lab_id, model=mname, rank=rank + 1,
                                     feature=FEATS[j],
                                     brier_increase=float(imp_mean[j])))
            print(f"\n--- {lab_id} | {mname} ---")
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
            print("  perm importance top-8: "
                  + ", ".join(f"{FEATS[j]}({imp_mean[j] * 1e4:.2f}e-4)"
                              for j in order[:8]))
            print("  calibration (bin: mean-pred -> realized, n):")
            ct = [r for r in cal_rows if r["label"] == lab_id and r["model"] == mname]
            for r in ct:
                print(f"    b{r['bin']}: {r['p_pred_mean']:.4f} -> {r['p_real']:.4f} "
                      f"(n={r['n']})")

    OOF = pd.concat(oof_rows, ignore_index=True)
    OOF.to_parquet(os.path.join(OUTD, "w5c5_oof_predictions.parquet"), index=False)
    pd.DataFrame(met_rows).to_csv(os.path.join(OUTD, "w5c5_metrics.csv"), index=False)
    pd.DataFrame(cal_rows).to_csv(os.path.join(OUTD, "w5c5_calibration.csv"),
                                  index=False)
    pd.DataFrame(foldlift_rows).to_csv(os.path.join(OUTD, "w5c5_fold_lifts.csv"),
                                       index=False)
    pd.DataFrame(imp_rows).to_csv(os.path.join(OUTD, "w5c5_perm_importance.csv"),
                                  index=False)

    M = pd.DataFrame(met_rows)
    print("\n=== SUMMARY vs frozen interpretation ===")
    print(M[["label", "model", "base_P", "top_P", "lift", "lift_lo", "lift_hi",
             "c1_gap", "pass_5pp", "pass_7pp_stable"]].to_string(index=False))
    any5 = bool(M["pass_5pp"].any())
    any7 = bool(M["pass_7pp_stable"].any())
    best = M.loc[M["lift"].idxmax()]
    print(f"\nbest lift: {best['label']} {best['model']} "
          f"{100 * best['lift']:+.2f}pp CI [{100 * best['lift_lo']:+.2f},"
          f"{100 * best['lift_hi']:+.2f}]pp vs C1 gap {100 * best['c1_gap']:.2f}pp")
    if any7:
        print("FROZEN VERDICT: >=7pp stable lift found -> freeze model form, "
              "conversion spec next wave.")
    elif any5:
        print("FROZEN VERDICT: >=5pp lift (CI excl. 0) found but not >=7pp stable -> "
              "information set NOT declared insufficient; no conversion trigger.")
    else:
        print("FROZEN VERDICT: NO label/model reaches top-decile lift >=5pp with CI "
              "excluding 0 -> information set declared INSUFFICIENT (input to "
              "Amendment 6 par.9 closure).")
    print("\nW5C5 DONE")


if __name__ == "__main__":
    main()
