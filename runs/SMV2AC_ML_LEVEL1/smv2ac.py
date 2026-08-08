"""SMV2AC_ML_LEVEL1 -- Level-1 interpretable ML screen (seq 413-414).

Frozen spec: runs/SMV2AC_ML_LEVEL1/spec.yaml (committed 2bf5a4f, read before write).

413: joint L2-logistic model on 5 already-computed causal features (sigma460, ER150, flip_rate,
     VR_q26_N780, HTF_agree), walk-forward expanding-window outer CV (6 folds, >=60wk initial
     train, 1wk embargo) with inner 3-fold chronological CV (C in {0.01,0.1,1.0,10.0}) INSIDE
     each outer training window only. OOF diagnostics reported for context (NOT promotion
     criteria per V4 s32).
414: promotion-relevant test -- does the joint model's OOF P(joint-loss) beat a 1-feature
     ER150-only baseline (IDENTICAL protocol) on OOF log-loss, via paired moving-block
     bootstrap (block=4wk, B=10000, seed=20260808, P(improvement>0)>=0.85, the house bar)?

Data reuse (verbatim, per spec CODE MAP -- no new feature engineering):
  - runs/SMV2Y_JOINTLOSS_VIABILITY/out/target_series.csv: the binary joint-loss target
    (joint_loss_next) AND the sigma460/ER150/VR_q26_N780/flip_rate/HTF weekly snapshots
    (state_399_sigma460, state_400_ER150, state_402_VR_q26_N780, state_401_flip_rate,
    control_htf), already aligned to week t's last session and already verified against
    runs/SMV2J_STATE_HARNESS/out/states_dev.csv column names (VR_q26_N780, htf) by the
    original SMV2Y build. Re-verified here (section A) before use.
  - runs/SMV2N_WINDFALL_POLICY / SMV2Z_VIABILITY_POLICY house bootstrap pattern:
    src/analytics/sm_metrics.py:block_bootstrap_delta, reused verbatim for the promotion test
    (block=4 weeks, B=10000, seed=20260808).

Z-scoring convention (spec features section, literal + authoritative): "z-scored using
EXPANDING statistics only (no full-sample scaling, matching every prior JOB1 test in this
program)". NOTE (FACT, documented for the record): smv2y.py's OWN internal OLS regression used
a STATIC (full post-burn-in-sample) zsc() for its state z-scores -- not an expanding one. That
is a genuine internal inconsistency in the source file the CODE MAP points to. This script
follows the SMV2AC spec's own explicit, unambiguous features-section instruction (expanding,
no full-sample scaling) rather than smv2y.py's static zsc() implementation, since the spec text
is the authoritative constraint for THIS run and full-sample scaling would leak future
distributional information into early-fold training rows. Implemented as a running
(Welford-style) mean/std computed causally at each week t using only weeks <= t (inclusive),
generalizing smv2y.py's expanding_quintile bisect-insort machinery (rank -> quantile) to a
continuous expanding mean/std (rank -> z-score). This is a single global causal transform
(computed once, upfront) -- not refit per outer fold -- which is leakage-safe for every fold's
OOF test rows because at any week t only weeks <= t are used, regardless of which fold t later
falls into.
"""
import os, sys, json, math
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import roc_auc_score, log_loss, brier_score_loss
from scipy import stats as sstats

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
os.chdir(ROOT)
sys.path.insert(0, "src/analytics")
from sm_metrics import block_bootstrap_delta  # noqa: E402

RUN = os.path.join(ROOT, "runs", "SMV2AC_ML_LEVEL1")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)

SEED = 20260808
ALT_SEEDS = [1, 2, 3]
VIRGIN_FLOOR = pd.Timestamp("2026-08-01")   # HARD RULE: never touch >= this
DEV_END = pd.Timestamp("2026-05-31")

C_GRID = [0.01, 0.1, 1.0, 10.0]
N_OUTER = 6
MIN_INITIAL_TRAIN = 60
EMBARGO = 1
N_INNER = 3
B_BOOT = 10000
BLOCK_WEEKS = 4

RAW_TO_Z = {
    "sigma460": "z_sigma460",
    "ER150": "z_ER150",
    "flip_rate": "z_flip_rate",
    "VR_q26_N780": "z_VR_q26_N780",
    "HTF_agree": "z_HTF_agree",
}
FEATURES_FULL = ["z_sigma460", "z_ER150", "z_flip_rate", "z_VR_q26_N780", "z_HTF_agree"]
FEATURES_BASELINE = ["z_ER150"]
TARGET = "joint_loss_next"

_log_lines = []
def log(msg):
    s = str(msg)
    print(s)
    _log_lines.append(s)


# =============================================================================================
# A. load target_series.csv, verify columns exist (per orchestrator instruction: "verify exact
#    column names before use, do not rewrite"), assemble the modeling frame.
# =============================================================================================
ts = pd.read_csv("runs/SMV2Y_JOINTLOSS_VIABILITY/out/target_series.csv")
last_sess = pd.to_datetime(ts["week_last_session"])
assert last_sess.max() <= DEV_END, f"target_series.csv leaks past dev_end: max={last_sess.max()}"
assert last_sess.max() < VIRGIN_FLOOR, "target_series.csv touches VIRGIN floor"

RAW_COLS = {
    "state_399_sigma460": "sigma460",
    "state_400_ER150": "ER150",
    "state_401_flip_rate": "flip_rate",
    "state_402_VR_q26_N780": "VR_q26_N780",
    "control_htf": "HTF_agree",
}
for c in list(RAW_COLS.keys()) + ["joint_loss_next", "downside_next", "week_key",
                                    "week_first_session", "week_last_session"]:
    assert c in ts.columns, f"REQUIRED COLUMN MISSING: {c}"
log("column verification PASSED: all required target_series.csv columns present: "
    + ", ".join(list(RAW_COLS.keys()) + ["joint_loss_next", "downside_next"]))

# cross-check the state harness columns this file claims to derive from (per CODE MAP
# instruction: verify VR_q26_N780 / htf column names in states_dev.csv before use)
sd_cols = pd.read_csv("runs/SMV2J_STATE_HARNESS/out/states_dev.csv", nrows=0).columns.tolist()
for need in ["VR_q26_N780", "htf", "ER_n150", "sigma460"]:
    assert need in sd_cols, f"states_dev.csv missing expected column {need}"
log("states_dev.csv column cross-check PASSED: VR_q26_N780, htf, ER_n150, sigma460 present.")

ts = ts.sort_values("week_key").reset_index(drop=True)
D_all = ts.rename(columns=RAW_COLS).copy()

need_cols = list(RAW_COLS.values()) + [TARGET]
mask_valid = D_all[need_cols].notna().all(axis=1)
dropped = D_all.loc[~mask_valid, ["week_key"]]["week_key"].tolist()
log(f"dropped {len(dropped)}/{len(D_all)} weeks with a missing feature or target value: {dropped}")
log("  (9 weeks 202201-202209: HTF_agree undefined during the trailing-50-session SMA warmup; "
    "1 week 202622: joint_loss_next undefined, last row of target_series.csv has no next week)")

D = D_all.loc[mask_valid].reset_index(drop=True)
N = len(D)
assert (D["week_key"].diff().dropna() > 0).all(), "week_key not strictly increasing post-filter"
log(f"usable modeling weeks N={N} (week_key {D['week_key'].min()}..{D['week_key'].max()}, "
    f"{D['week_first_session'].iloc[0]}..{D['week_last_session'].iloc[-1]})")
log(f"base rate joint_loss_next = {D[TARGET].sum():.0f}/{N} = {D[TARGET].mean():.4f}  "
    f"(spec's stated population base rate: 50/230=0.217, computed here on the reduced usable "
    f"N={N} population after dropping HTF warm-up/tail rows -- see REPORT.md for FACT note "
    f"on this N discrepancy vs spec's illustrative '~230-60=~170' OOF estimate)")

meta = {
    "seed": SEED, "alt_seeds": ALT_SEEDS, "C_grid": C_GRID,
    "n_outer": N_OUTER, "min_initial_train": MIN_INITIAL_TRAIN, "embargo_weeks": EMBARGO,
    "n_inner": N_INNER, "B_boot": B_BOOT, "block_weeks": BLOCK_WEEKS,
    "N_full_target_series": int(len(D_all)), "N_dropped_missing": len(dropped),
    "dropped_week_keys": dropped, "N_usable": N,
    "week_key_min": int(D["week_key"].min()), "week_key_max": int(D["week_key"].max()),
    "base_rate_joint_loss_next": float(D[TARGET].mean()),
}


# =============================================================================================
# B. expanding z-score (causal, single global transform -- see module docstring for rationale)
# =============================================================================================
def expanding_zscore(x):
    """Welford-style running mean/std, ddof=1, using only x[0..i] at position i (inclusive,
    matching smv2y.py's expanding_quintile bisect-insort convention of including the current
    observation in its own history). First observation (n=1, std undefined) falls back to
    z=0.0 by convention; this row is provably never a test-fold row (see section C), so the
    convention has zero effect on any OOF prediction -- documented as FACT in REPORT.md."""
    x = np.asarray(x, dtype=float)
    n = len(x)
    z = np.empty(n)
    csum = 0.0
    csumsq = 0.0
    for i in range(n):
        csum += x[i]
        csumsq += x[i] ** 2
        cnt = i + 1
        mean = csum / cnt
        if cnt >= 2:
            var = max((csumsq - cnt * mean ** 2) / (cnt - 1), 0.0)
            sd = math.sqrt(var)
        else:
            sd = np.nan
        z[i] = (x[i] - mean) / sd if (sd == sd and sd > 1e-12) else 0.0  # sd==sd excludes NaN
    return z


for raw, zcol in RAW_TO_Z.items():
    D[zcol] = expanding_zscore(D[raw].to_numpy())
    assert D[zcol].notna().all(), f"NaN produced in expanding z-score for {zcol}"
log("expanding z-scores built for all 5 features (causal, ddof=1, first-obs->0.0 convention).")


# =============================================================================================
# C. outer walk-forward + embargo CV splitter -- BUILT AND VERIFIED BEFORE ANY MODEL FITTING
#    (per orchestrator instruction: this is the single most leakage-prone part of this spec).
# =============================================================================================
def build_outer_folds(n, min_train, n_folds, embargo):
    test_total = n - min_train - n_folds * embargo
    assert test_total > 0, "not enough weeks for the requested fold/embargo design"
    base = test_total // n_folds
    rem = test_total - base * n_folds
    sizes = [base + 1 if i < rem else base for i in range(n_folds)]
    folds = []
    train_end = min_train
    for k in range(n_folds):
        embargo_idx = list(range(train_end, train_end + embargo))
        test_start = train_end + embargo
        test_end = test_start + sizes[k]
        folds.append({
            "fold": k + 1,
            "train_idx": list(range(0, train_end)),
            "embargo_idx": embargo_idx,
            "test_idx": list(range(test_start, test_end)),
        })
        train_end = test_end
    assert train_end == n, f"folds do not exactly tile the sample: train_end={train_end} N={n}"
    return folds


folds = build_outer_folds(N, MIN_INITIAL_TRAIN, N_OUTER, EMBARGO)

splitter_rows = []
all_test_idx = []
for f in folds:
    tr, emb, te = f["train_idx"], f["embargo_idx"], f["test_idx"]
    # ---- embargo genuinely enforced: no training week within 1 week of test start
    gap = te[0] - tr[-1]
    assert emb[0] == tr[-1] + 1 and te[0] == emb[-1] + 1, "embargo not contiguous train->embargo->test"
    assert gap == EMBARGO + 1, f"fold {f['fold']}: embargo gap={gap}, expected {EMBARGO + 1}"
    row = {
        "fold": f["fold"],
        "train_n": len(tr),
        "train_start_week": int(D["week_key"].iloc[tr[0]]),
        "train_end_week": int(D["week_key"].iloc[tr[-1]]),
        "train_start_date": str(D["week_first_session"].iloc[tr[0]]),
        "train_end_date": str(D["week_last_session"].iloc[tr[-1]]),
        "embargo_week_key": int(D["week_key"].iloc[emb[0]]),
        "embargo_dates": f"{D['week_first_session'].iloc[emb[0]]}..{D['week_last_session'].iloc[emb[0]]}",
        "test_n": len(te),
        "test_start_week": int(D["week_key"].iloc[te[0]]),
        "test_end_week": int(D["week_key"].iloc[te[-1]]),
        "test_start_date": str(D["week_first_session"].iloc[te[0]]),
        "test_end_date": str(D["week_last_session"].iloc[te[-1]]),
        "embargo_gap_weeks": gap - 1,
    }
    splitter_rows.append(row)
    log(f"FOLD {f['fold']}: train wk[{row['train_start_week']}..{row['train_end_week']}] "
        f"n={row['train_n']:3d} ({row['train_start_date']}..{row['train_end_date']}) | "
        f"EMBARGO wk {row['embargo_week_key']} ({row['embargo_dates']}) | "
        f"test wk[{row['test_start_week']}..{row['test_end_week']}] n={row['test_n']:3d} "
        f"({row['test_start_date']}..{row['test_end_date']})")
    all_test_idx.extend(te)

# ---- test windows chronologically ordered and non-overlapping across all 6 folds
assert all_test_idx == sorted(all_test_idx), "OOF test indices not chronologically ordered"
assert len(all_test_idx) == len(set(all_test_idx)), "OOF test indices overlap across folds"
# ---- test folds tile the post-burn-in sample exactly, minus the 6 single embargo weeks
embargoed = set(f["embargo_idx"][0] for f in folds)
expected_test_set = set(range(MIN_INITIAL_TRAIN + EMBARGO, N)) - (embargoed - {folds[0]["embargo_idx"][0]})
# (each later fold's embargo week is a *previous* fold's train-extension boundary, not a hole in
#  the overall [min_train+embargo, N) span once later folds' training windows reabsorb it as
#  historical data -- the ONLY index never covered by any test fold is each fold's OWN embargo
#  index at the moment it is embargoed) -- verify by reconstructing directly instead of set algebra:
covered_or_embargoed = set(all_test_idx) | embargoed | set(range(0, MIN_INITIAL_TRAIN))
assert covered_or_embargoed == set(range(N)), "gap in [train | embargo | test] coverage of [0,N)"
log(f"OOF test coverage check PASSED: {len(all_test_idx)} distinct OOF weeks, "
    f"{len(embargoed)} single-week embargo gaps ({sorted(embargoed)}), "
    f"{MIN_INITIAL_TRAIN} initial-train-only weeks -- union covers all N={N} weeks exactly once.")

TOTAL_OOF_N = len(all_test_idx)
meta["total_oof_n"] = TOTAL_OOF_N
meta["fold_sizes_test"] = [f["test_n"] for f in splitter_rows]
log(f"TOTAL OOF weeks across 6 outer test folds: {TOTAL_OOF_N} "
    f"(spec's own rough estimate was ~230-60=~170, based on the full 230-week target_series.csv "
    f"population before the HTF/tail NaN drop; actual usable N={N} -> {TOTAL_OOF_N} OOF weeks; "
    f"documented as FACT in REPORT.md, not adjusted to hit the spec's illustrative number).")

pd.DataFrame(splitter_rows).to_csv(os.path.join(OUT, "cv_splitter.csv"), index=False)
with open(os.path.join(OUT, "cv_splitter_log.txt"), "w") as fh:
    fh.write("\n".join(_log_lines) + "\n")
log("cv_splitter.csv + cv_splitter_log.txt written -- outer CV splitter VERIFIED before any "
    "model fitting begins.")


# =============================================================================================
# D. inner 3-fold chronological CV (hyperparameter selection) + outer fold fit/predict
# =============================================================================================
def fit_fold(D, feat_cols, target_col, fold, C_grid, n_inner, seed, inner_touch_log=None):
    tr_idx = np.array(fold["train_idx"])
    te_idx = np.array(fold["test_idx"])
    Xtr_full = D.loc[tr_idx, feat_cols].to_numpy(dtype=float)
    ytr_full = D.loc[tr_idx, target_col].to_numpy(dtype=float)

    tss = TimeSeriesSplit(n_splits=n_inner)
    inner_ll = {c: [] for c in C_grid}
    local_pos = np.arange(len(tr_idx))
    for itr_pos, ival_pos in tss.split(local_pos):
        # ---- inner CV touches ONLY this outer fold's training window (positions are indices
        #      into tr_idx itself, so this is true by construction; assert explicitly anyway)
        assert set(itr_pos) <= set(local_pos) and set(ival_pos) <= set(local_pos)
        assert set(tr_idx[itr_pos]) <= set(fold["train_idx"])
        assert set(tr_idx[ival_pos]) <= set(fold["train_idx"])
        if inner_touch_log is not None:
            inner_touch_log.append({
                "fold": fold["fold"], "inner_train_n": len(itr_pos), "inner_val_n": len(ival_pos),
                "inner_train_wk_range": (int(D["week_key"].iloc[tr_idx[itr_pos[0]]]),
                                          int(D["week_key"].iloc[tr_idx[itr_pos[-1]]])),
                "inner_val_wk_range": (int(D["week_key"].iloc[tr_idx[ival_pos[0]]]),
                                       int(D["week_key"].iloc[tr_idx[ival_pos[-1]]])),
            })
        Xi_tr, yi_tr = Xtr_full[itr_pos], ytr_full[itr_pos]
        Xi_val, yi_val = Xtr_full[ival_pos], ytr_full[ival_pos]
        if len(np.unique(yi_tr)) < 2:
            continue  # cannot fit a binary logistic model on a single-class inner-train slice
        for c in C_grid:
            m = LogisticRegression(penalty="l2", C=c, class_weight=None, solver="lbfgs",
                                    random_state=seed, max_iter=2000)
            m.fit(Xi_tr, yi_tr)
            p = np.clip(m.predict_proba(Xi_val)[:, 1], 1e-9, 1 - 1e-9)
            inner_ll[c].append(log_loss(yi_val, p, labels=[0, 1]))

    mean_ll = {c: (float(np.mean(v)) if len(v) > 0 else np.inf) for c, v in inner_ll.items()}
    best_C = min(mean_ll, key=mean_ll.get)

    final = LogisticRegression(penalty="l2", C=best_C, class_weight=None, solver="lbfgs",
                                random_state=seed, max_iter=2000)
    final.fit(Xtr_full, ytr_full)
    Xte = D.loc[te_idx, feat_cols].to_numpy(dtype=float)
    yte = D.loc[te_idx, target_col].to_numpy(dtype=float)
    p_te = np.clip(final.predict_proba(Xte)[:, 1], 1e-9, 1 - 1e-9)

    return {
        "fold": fold["fold"], "best_C": best_C, "inner_mean_logloss": mean_ll,
        "coef": dict(zip(feat_cols, final.coef_[0].tolist())),
        "intercept": float(final.intercept_[0]),
        "test_idx": te_idx.tolist(), "p_test": p_te, "y_test": yte,
        "week_key_test": D["week_key"].iloc[te_idx].tolist(),
        "train_n": len(tr_idx),
    }


def run_walkforward(D, feat_cols, target_col, folds, C_grid, n_inner, seed, log_inner=False):
    inner_touch_log = [] if log_inner else None
    results = [fit_fold(D, feat_cols, target_col, f, C_grid, n_inner, seed, inner_touch_log)
               for f in folds]
    return results, inner_touch_log


log("\n=== fitting FULL 5-feature model (main seed) ===")
full_results, inner_touch_log = run_walkforward(D, FEATURES_FULL, TARGET, folds, C_GRID,
                                                  N_INNER, SEED, log_inner=True)
for r in full_results:
    log(f"  fold {r['fold']}: best_C={r['best_C']} train_n={r['train_n']} test_n={len(r['test_idx'])} "
        f"coef={ {k: round(v, 4) for k, v in r['coef'].items()} } intercept={r['intercept']:.4f}")

# ---- inner-CV containment proof written to out/ (explicit, per orchestrator instruction)
pd.DataFrame(inner_touch_log).to_csv(os.path.join(OUT, "inner_cv_containment_check.csv"), index=False)
log("inner_cv_containment_check.csv written: every inner split's train/val week ranges lie "
    "strictly inside its own outer fold's training window (asserted programmatically above).")

log("\n=== fitting BASELINE 1-feature (ER150-only) model, IDENTICAL protocol ===")
base_results, _ = run_walkforward(D, FEATURES_BASELINE, TARGET, folds, C_GRID, N_INNER, SEED)
for r in base_results:
    log(f"  fold {r['fold']}: best_C={r['best_C']} train_n={r['train_n']} test_n={len(r['test_idx'])} "
        f"coef={ {k: round(v, 4) for k, v in r['coef'].items()} } intercept={r['intercept']:.4f}")


# =============================================================================================
# E. assemble OOF predictions (both models), coefficients table
# =============================================================================================
def oof_frame(results, model_name):
    rows = []
    for r in results:
        for wk, p, y in zip(r["week_key_test"], r["p_test"], r["y_test"]):
            ll = -(y * math.log(p) + (1 - y) * math.log(1 - p))
            rows.append({"week_key": wk, "fold": r["fold"], "model": model_name,
                         "p_pred": float(p), "y_true": float(y), "logloss": float(ll)})
    return pd.DataFrame(rows)


oof_full = oof_frame(full_results, "full5")
oof_base = oof_frame(base_results, "baseline_ER150")
assert list(oof_full["week_key"]) == list(oof_base["week_key"]), \
    "full and baseline models produced different OOF week sets -- protocol mismatch"
assert len(oof_full) == TOTAL_OOF_N

oof_all = pd.concat([oof_full, oof_base], ignore_index=True)
oof_all.to_csv(os.path.join(OUT, "oof_predictions.csv"), index=False)
log(f"\noof_predictions.csv written: {len(oof_all)} rows ({TOTAL_OOF_N} weeks x 2 models)")

coef_rows = []
for model_name, results, feat_cols in [("full5", full_results, FEATURES_FULL),
                                        ("baseline_ER150", base_results, FEATURES_BASELINE)]:
    for r in results:
        row = {"model": model_name, "fold": r["fold"], "best_C": r["best_C"],
               "intercept": r["intercept"]}
        for fc in FEATURES_FULL:
            row[fc] = r["coef"].get(fc, np.nan)
        coef_rows.append(row)
fold_coef = pd.DataFrame(coef_rows)
fold_coef.to_csv(os.path.join(OUT, "fold_coefficients.csv"), index=False)
log("fold_coefficients.csv written.")


# =============================================================================================
# F. coefficient stability (full model, honest -- report sign flips, do not average them away)
# =============================================================================================
coef_stability = []
f5 = fold_coef[fold_coef["model"] == "full5"]
for fc in FEATURES_FULL:
    vals = f5[fc].to_numpy(dtype=float)
    signs = np.sign(vals)
    n_pos = int((signs > 0).sum())
    n_neg = int((signs < 0).sum())
    n_flip_folds = min(n_pos, n_neg)  # folds on the minority sign = "flips" relative to majority
    stable_sign = (n_flip_folds == 0)
    near_zero_folds = int((np.abs(vals) < 0.05).sum())
    coef_stability.append({
        "feature": fc, "min_coef": float(vals.min()), "max_coef": float(vals.max()),
        "mean_coef": float(vals.mean()), "n_folds_positive": n_pos, "n_folds_negative": n_neg,
        "sign_consistent_all_6_folds": stable_sign,
        "n_folds_near_zero_lt_0.05": near_zero_folds,
        "stable_nontrivial_contributor": bool(stable_sign and near_zero_folds == 0),
    })
    log(f"COEF STABILITY {fc}: folds+={n_pos} folds-={n_neg} min={vals.min():+.4f} "
        f"max={vals.max():+.4f} near-zero(<0.05)_folds={near_zero_folds} "
        f"-> {'STABLE' if stable_sign and near_zero_folds == 0 else 'NOT STABLE'}")
coef_stab_df = pd.DataFrame(coef_stability)


# =============================================================================================
# G. seed-stability check (full model; refit whole walk-forward pipeline w/ 3 additional seeds)
# =============================================================================================
seed_aucs = {}
y_main = oof_full["y_true"].to_numpy()
p_main = oof_full["p_pred"].to_numpy()
seed_aucs[SEED] = float(roc_auc_score(y_main, p_main))
for s in ALT_SEEDS:
    res_s, _ = run_walkforward(D, FEATURES_FULL, TARGET, folds, C_GRID, N_INNER, s)
    oof_s = oof_frame(res_s, "full5")
    assert list(oof_s["week_key"]) == list(oof_full["week_key"])
    seed_aucs[s] = float(roc_auc_score(oof_s["y_true"].to_numpy(), oof_s["p_pred"].to_numpy()))
seed_auc_vals = np.array(list(seed_aucs.values()))
seed_stability = {
    "seeds": list(seed_aucs.keys()), "aucs": list(seed_aucs.values()),
    "auc_variance": float(np.var(seed_auc_vals, ddof=1)) if len(seed_auc_vals) > 1 else 0.0,
    "auc_range": float(seed_auc_vals.max() - seed_auc_vals.min()),
    "note": "solver='lbfgs' (the sklearn default for penalty='l2') does not use random_state "
            "for anything (no data shuffling, no stochastic step) -- per sklearn docs, "
            "random_state only affects 'sag'/'saga'/'liblinear'. Zero variance across seeds "
            "is therefore the CORRECT, expected result for this solver, not a null check that "
            "silently passed -- documented as FACT in REPORT.md.",
}
log(f"\nSEED STABILITY: AUCs across seeds {seed_aucs} -> variance={seed_stability['auc_variance']:.10f} "
    f"range={seed_stability['auc_range']:.10f}  ({seed_stability['note'][:80]}...)")


# =============================================================================================
# H. OOF diagnostics: AUC, Brier, calibration decile table (both models)
# =============================================================================================
diag_rows = []
calib_rows = []
for model_name, oof_m in [("full5", oof_full), ("baseline_ER150", oof_base)]:
    y = oof_m["y_true"].to_numpy()
    p = oof_m["p_pred"].to_numpy()
    auc = float(roc_auc_score(y, p))
    brier = float(brier_score_loss(y, p))
    mean_ll = float(oof_m["logloss"].mean())
    diag_rows.append({
        "model": model_name, "oof_n": len(oof_m), "oof_auc": auc, "oof_brier": brier,
        "oof_mean_logloss": mean_ll, "oof_base_rate": float(y.mean()),
    })
    log(f"DIAGNOSTICS {model_name}: N={len(oof_m)} AUC={auc:.4f} Brier={brier:.4f} "
        f"meanLogLoss={mean_ll:.4f}")

    tmp = oof_m.copy().sort_values("p_pred").reset_index(drop=True)
    tmp["decile"] = pd.qcut(tmp["p_pred"], 10, labels=False, duplicates="drop")
    for d, grp in tmp.groupby("decile"):
        calib_rows.append({
            "model": model_name, "decile": int(d), "n": len(grp),
            "mean_predicted_p": float(grp["p_pred"].mean()),
            "realized_rate": float(grp["y_true"].mean()),
            "p_range": f"[{grp['p_pred'].min():.4f},{grp['p_pred'].max():.4f}]",
        })
diag_df = pd.DataFrame(diag_rows)
calib_df = pd.DataFrame(calib_rows)
calib_df.to_csv(os.path.join(OUT, "calibration_deciles.csv"), index=False)
log("calibration_deciles.csv written.")


# =============================================================================================
# I. secondary correlation check (continuous downside_next vs OOF P(joint-loss), full model)
# =============================================================================================
oof_full_wk = oof_full.set_index("week_key")
down_next = D.set_index("week_key")["downside_next"]
merged_corr = oof_full_wk.join(down_next, how="left")
assert merged_corr["downside_next"].notna().all(), "downside_next missing on an OOF week"
pear_r, pear_p = sstats.pearsonr(merged_corr["p_pred"], merged_corr["downside_next"])
spear_r, spear_p = sstats.spearmanr(merged_corr["p_pred"], merged_corr["downside_next"])
secondary_corr = {
    "n": int(len(merged_corr)), "pearson_r": float(pear_r), "pearson_p": float(pear_p),
    "spearman_r": float(spear_r), "spearman_p": float(spear_p),
    "note": "higher P(joint-loss) should correlate with MORE NEGATIVE downside_next -> "
            "expect a negative correlation if the model captures real signal.",
}
log(f"\nSECONDARY CORRELATION (OOF P(joint-loss) vs downside_next, full model): "
    f"pearson r={pear_r:+.4f} (p={pear_p:.4f}) spearman r={spear_r:+.4f} (p={spear_p:.4f})")


# =============================================================================================
# J. promotion test (414, THE gate): paired moving-block bootstrap on OOF log-loss difference
# =============================================================================================
merged_ll = oof_full[["week_key", "logloss", "p_pred"]].rename(
    columns={"logloss": "ll_full", "p_pred": "p_full"}).merge(
    oof_base[["week_key", "logloss", "p_pred"]].rename(
        columns={"logloss": "ll_base", "p_pred": "p_base"}), on="week_key", how="inner")
assert len(merged_ll) == TOTAL_OOF_N

ll_base_arr = merged_ll["ll_base"].to_numpy()
ll_full_arr = merged_ll["ll_full"].to_numpy()
boot = block_bootstrap_delta(ll_base_arr, ll_full_arr, block=BLOCK_WEEKS, n_boot=B_BOOT, seed=SEED)
# boot['delta'] = mean(ll_base) - mean(ll_full); positive => full model has LOWER log-loss (better)
p_improvement_gt_0 = 1.0 - boot["p_leq_0"]
PASS_BAR = 0.85
promotion_pass = bool(p_improvement_gt_0 >= PASS_BAR)

mean_ll_base = float(ll_base_arr.mean())
mean_ll_full = float(ll_full_arr.mean())

overall_auc_full = float(diag_df.loc[diag_df["model"] == "full5", "oof_auc"].iloc[0])
overall_auc_base = float(diag_df.loc[diag_df["model"] == "baseline_ER150", "oof_auc"].iloc[0])
auc_delta = overall_auc_full - overall_auc_base

fold_auc_rows = []
for rf, rb in zip(full_results, base_results):
    yf = rf["y_test"]; pf = rf["p_test"]; pb = rb["p_test"]
    if len(np.unique(yf)) < 2:
        auc_f = auc_b = np.nan
        sign = "N/A_single_class"
    else:
        auc_f = float(roc_auc_score(yf, pf))
        auc_b = float(roc_auc_score(yf, pb))
        sign = "+" if auc_f > auc_b else ("-" if auc_f < auc_b else "0")
    fold_auc_rows.append({"fold": rf["fold"], "test_n": len(yf), "auc_full": auc_f,
                          "auc_baseline": auc_b, "auc_delta": (auc_f - auc_b) if auc_f == auc_f else np.nan,
                          "sign": sign})
fold_auc_df = pd.DataFrame(fold_auc_rows)
n_folds_pos_delta = int((fold_auc_df["sign"] == "+").sum())
n_folds_valid = int((fold_auc_df["sign"] != "N/A_single_class").sum())
log(f"\nPER-FOLD AUC (full vs baseline): \n{fold_auc_df.to_string(index=False)}")
log(f"fold-level AUC delta sign-stability: {n_folds_pos_delta}/{n_folds_valid} valid folds favor "
    f"the full model")

# ---- context-only (INFERENCE, NOT the gate) full-sample nested LRT-style diagnostic
full_all = LogisticRegression(penalty="l2", C=1.0, class_weight=None, solver="lbfgs",
                               random_state=SEED, max_iter=2000).fit(
    D[FEATURES_FULL].to_numpy(float), D[TARGET].to_numpy(float))
base_all = LogisticRegression(penalty="l2", C=1.0, class_weight=None, solver="lbfgs",
                               random_state=SEED, max_iter=2000).fit(
    D[FEATURES_BASELINE].to_numpy(float), D[TARGET].to_numpy(float))
p_full_all = np.clip(full_all.predict_proba(D[FEATURES_FULL].to_numpy(float))[:, 1], 1e-9, 1 - 1e-9)
p_base_all = np.clip(base_all.predict_proba(D[FEATURES_BASELINE].to_numpy(float))[:, 1], 1e-9, 1 - 1e-9)
y_all_full = D[TARGET].to_numpy(float)
ll_sum_full = -np.sum(y_all_full * np.log(p_full_all) + (1 - y_all_full) * np.log(1 - p_full_all))
ll_sum_base = -np.sum(y_all_full * np.log(p_base_all) + (1 - y_all_full) * np.log(1 - p_base_all))
# ll_sum_X = sum of per-row logloss = total NEGATIVE log-likelihood (NLL) of model X.
# Standard LR statistic: LR = 2*(LL_full - LL_base) = 2*((-ll_sum_full) - (-ll_sum_base))
#                            = 2*(ll_sum_base - ll_sum_full)
lr_stat = 2.0 * (ll_sum_base - ll_sum_full)
lr_stat = float(max(lr_stat, 0.0))
lr_df = len(FEATURES_FULL) - len(FEATURES_BASELINE)
lr_pvalue = float(sstats.chi2.sf(lr_stat, lr_df))

promo_rows = [
    {"metric": "OOF_N", "value": TOTAL_OOF_N},
    {"metric": "mean_oof_logloss_baseline_ER150", "value": mean_ll_base},
    {"metric": "mean_oof_logloss_full5", "value": mean_ll_full},
    {"metric": "delta_mean_logloss_base_minus_full", "value": mean_ll_base - mean_ll_full},
    {"metric": "bootstrap_block_weeks", "value": BLOCK_WEEKS},
    {"metric": "bootstrap_B", "value": B_BOOT},
    {"metric": "bootstrap_seed", "value": SEED},
    {"metric": "bootstrap_delta_point_estimate_base_minus_full", "value": boot["delta"]},
    {"metric": "bootstrap_delta_ci_lo_2.5pct", "value": boot["ci_lo"]},
    {"metric": "bootstrap_delta_ci_hi_97.5pct", "value": boot["ci_hi"]},
    {"metric": "bootstrap_P_improvement_gt_0", "value": p_improvement_gt_0},
    {"metric": "PASS_bar", "value": PASS_BAR},
    {"metric": "PROMOTION_TEST_PASS", "value": promotion_pass},
    {"metric": "oof_auc_full5", "value": overall_auc_full},
    {"metric": "oof_auc_baseline_ER150", "value": overall_auc_base},
    {"metric": "oof_auc_delta_full_minus_baseline", "value": auc_delta},
    {"metric": "n_outer_folds_auc_delta_positive", "value": n_folds_pos_delta},
    {"metric": "n_outer_folds_auc_delta_valid", "value": n_folds_valid},
    {"metric": "secondary_pearson_r_Pjointloss_vs_downside_next", "value": secondary_corr["pearson_r"]},
    {"metric": "secondary_pearson_p", "value": secondary_corr["pearson_p"]},
    {"metric": "secondary_spearman_r_Pjointloss_vs_downside_next", "value": secondary_corr["spearman_r"]},
    {"metric": "secondary_spearman_p", "value": secondary_corr["spearman_p"]},
    {"metric": "CONTEXT_ONLY_full_sample_LR_stat_2xll_full_vs_baseline", "value": lr_stat},
    {"metric": "CONTEXT_ONLY_full_sample_LR_df", "value": lr_df},
    {"metric": "CONTEXT_ONLY_full_sample_LR_pvalue_chi2", "value": lr_pvalue},
]
promo_df = pd.DataFrame(promo_rows)
promo_df.to_csv(os.path.join(OUT, "promotion_test.csv"), index=False)
fold_auc_df.to_csv(os.path.join(OUT, "fold_auc_detail.csv"), index=False)
log(f"\npromotion_test.csv written. PROMOTION_TEST_PASS={promotion_pass} "
    f"(P(improvement>0)={p_improvement_gt_0:.4f} vs bar {PASS_BAR})")


# =============================================================================================
# K. diagnostics.csv (413 outputs) + final meta/log writeout
# =============================================================================================
diag_df["seed_stability_auc_variance"] = np.where(diag_df["model"] == "full5",
                                                    seed_stability["auc_variance"], np.nan)
diag_df["seed_stability_auc_range"] = np.where(diag_df["model"] == "full5",
                                                seed_stability["auc_range"], np.nan)
diag_df.to_csv(os.path.join(OUT, "diagnostics.csv"), index=False)
coef_stab_df.to_csv(os.path.join(OUT, "coefficient_stability.csv"), index=False)
log("diagnostics.csv + coefficient_stability.csv written.")

meta["promotion_test_pass"] = promotion_pass
meta["p_improvement_gt_0"] = p_improvement_gt_0
meta["seed_stability"] = seed_stability
meta["oof_auc_full5"] = overall_auc_full
meta["oof_auc_baseline"] = overall_auc_base
with open(os.path.join(OUT, "meta.json"), "w") as fh:
    json.dump(meta, fh, indent=2, default=str)
with open(os.path.join(OUT, "run_log.txt"), "w") as fh:
    fh.write("\n".join(_log_lines) + "\n")

log("\nDONE.")
