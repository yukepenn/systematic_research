"""AUCTION04_CLEAN_CAUSAL_SUBSTRATE -- M5 replication (data-integrity replication, NOT a new
alpha trial) of runs/AUCTION03_MECHANISM_DECOMPOSITION/src/02_m5_action_value_residual.py's
incumbent-aligned action-value residual test, on a CAUSALLY-CORRECTED abs_value_dist_ticks
predictor.

WHY THIS SCRIPT EXISTS
-----------------------
AUCTION03's REPORT.md sec6 disclosed two defects, both traced to pre-existing infrastructure:
  (1) decision_outcomes(_CONFIRM).parquet's markout/mfe/mae/range columns are exactly 4x too
      large on disk (units bug). M5 does NOT read decision_outcomes.parquet at all -- it reads
      action_substrate.parquet / action_substrate_CONFIRM.parquet, whose signed_markout_H_{A,B}
      columns are built independently in runs/AUCTION02_ACTION_RELEVANCE/src/
      01_build_action_substrate.py (and its confirmation-pool twin) directly from U0's own
      close/high/low series in raw price POINTS (not sechilo's tick-scaled mid), divided by
      TICK=0.25 exactly once (see that script's `sm = side * (fwd_close - close_arr) / TICK`).
      Defect 1 is therefore NOT PRESENT in action_substrate's outcome columns -- confirmed by
      code inspection, not assumed -- and signed_markout_H_{A,B} is carried over UNCHANGED here.
  (2) value_dist_ticks's 'last'-price numerator inherits a small lookahead bias from grid1s's
      1-second-bucket-labeled-by-window-START convention (bucket T aggregates trades in
      [T,T+1), so a row labeled T can reflect a trade up to ~1s AFTER T). action_substrate.parquet
      /action_substrate_CONFIRM.parquet's OWN value_dist_ticks/abs_value_dist_ticks columns are
      merge_asof'd (backward, 2s tolerance) straight from poc_1s_full.parquet /
      poc_1s_full_CONFIRM.parquet (see 01_build_action_substrate.py line ~136 and
      W5's 03_build_action_substrate_confirmation.py line ~121) -- the SAME defective upstream
      source AUCTION03 diagnosed. Defect 2 THEREFORE IS present in action_substrate's predictor
      and is fixed below.

FIX (defect 2 only; nothing else about M5 is touched)
-------------------------------------------------------
For every (sess_tag, time) decision point that survives action_substrate's own analysis_ok
filter (matched & rth & liquid -- computed by the ORIGINAL AUCTION02/W5 build scripts and left
completely unchanged here), we rebuild value_dist_ticks from scratch as
    (causal_last_t - causal_running_POC_t) / TICK
using a strict timestamp<=t causal cutoff against raw bip==0 trade prints
(research/scalping_lab/substrate/raw/NQ/*.parquet), reusing runs/AUCTION04_CLEAN_CAUSAL_SUBSTRATE
/src/01_build_clean_substrate.py's own causal_running_poc()/causal_lookup()/load_raw_last()
functions VERBATIM (imported directly from that module, not re-typed) -- the exact machinery
that run's spec.yaml and 02_unit_tests.py (T2: 10/10 brute-force spot-check matches) already
certified as exactly causal. abs_value_dist_ticks = |value_dist_ticks| as before. Every other
column (M, M_A_raw, HTF_tilt_state, vote_dispersion, sigma460_atr_proxy_pts, session_phase,
signed_markout_H_{A,B}, mfe/mae/fwd_pnl_H_{A,B}, position_B, target_exposure_A, block_id_*,
analysis_ok, matched, rth, liquid, ...) is carried over from action_substrate(.parquet|_CONFIRM
.parquet) UNCHANGED -- only the value_dist_ticks/abs_value_dist_ticks predictor is rebuilt, per
the task's explicit scope instruction.

Everything downstream of that -- OLS specification (abs_value_dist_ticks + m_abs + sigma460 +
phase dummies), tercile cuts (recomputed fresh on the corrected predictor's own marginal
distribution, exactly the original's preregistered-on-marginal-distribution convention),
dual-clustered (session-block AND trade-block, 1000 reps each) bootstrap CIs, R_aligned
definition (= signed_markout_H_{A,B} directly, per 02_m5_action_value_residual.py's own
documented deviation from the task's literal sign()*signed_markout formula), horizons {1,3,20},
both products, both samples reported separately -- is copied VERBATIM from
02_m5_action_value_residual.py. No other methodology change.

STRESS CHECKS (task-scoped subset: LOSO, remove-top-3-sessions, vol-regime median split; same
methodology as runs/AUCTION03_MECHANISM_DECOMPOSITION/src/
05_stress_M5___value_dist_ticks__conditioned_deter.py, extended to BOTH products since both A and
B show a dual-significant discovery-sample finding in the original M5 output -- the original
stress script only attacked product B because that was the cell explicitly assigned to it; here
both live claims get the same treatment). Contract-month split, the predictor-confound
correlation check, and the raw-tick lookahead spot-check are NOT re-run: causality of this
script's predictor is already independently certified by AUCTION04's own unit tests (T2, 10/10
brute-force matches) and causality_audit (378/378 timestamps, 0 violations) via the identical
reused causal_running_poc/causal_lookup code path -- re-deriving that a third time here would be
redundant, not a stress test of THIS finding.

GOVERNANCE: reads only action_substrate.parquet / action_substrate_CONFIRM.parquet (already-built,
frozen) plus raw bip==0 trade prints for the permitted 37 discovery + 8 confirmation-pool session
tags (research/scalping_lab/substrate/raw/NQ/s<tag>.parquet). No session outside these 45 is
read. Writes only under runs/AUCTION04_CLEAN_CAUSAL_SUBSTRATE/out/.
"""
import os
import sys
import json
import importlib.util

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
AUCTION02_SRC = os.path.join(ROOT, "runs", "AUCTION02_ACTION_RELEVANCE", "src")
AUCTION04_SRC = os.path.join(ROOT, "runs", "AUCTION04_CLEAN_CAUSAL_SUBSTRATE", "src")
sys.path.insert(0, AUCTION02_SRC)
from stats_lib_auction02 import dual_block_bootstrap_meandiff  # noqa: E402

# import 01_build_clean_substrate.py's already-certified causal machinery VERBATIM (module name
# starts with a digit, can't `import` normally -- load by file path instead)
_spec = importlib.util.spec_from_file_location(
    "auction04_build_clean_substrate", os.path.join(AUCTION04_SRC, "01_build_clean_substrate.py"))
auction04_build = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(auction04_build)
load_raw_last = auction04_build.load_raw_last
causal_running_poc = auction04_build.causal_running_poc
causal_lookup = auction04_build.causal_lookup

OUT = os.path.join(ROOT, "runs", "AUCTION04_CLEAN_CAUSAL_SUBSTRATE", "out")
os.makedirs(OUT, exist_ok=True)

HORIZONS = [1, 3, 20]
NBOOT = 1000
RNG = np.random.default_rng(20260810)  # identical seed to the original 02_m5_action_value_residual.py
TICK = 0.25
C1_TICKS = 2.872  # campaign round-trip cost hurdle, ticks -- unchanged

DISCOVERY_DATES = [
    "20250814", "20250820", "20250901", "20250902", "20250905", "20250910",
    "20250911", "20250922", "20251002", "20251009", "20251027", "20251029",
    "20251110", "20251117", "20251124", "20251128", "20251209", "20251222",
    "20260123", "20260206", "20260211", "20260218", "20260220", "20260223",
    "20260303", "20260312", "20260317", "20260320", "20260406", "20260409",
    "20260417", "20260423", "20260428", "20260506", "20260511", "20260519",
    "20260520",
]
CONFIRM_DATES = [
    "20250819", "20250912", "20251028", "20251125", "20260217",
    "20260302", "20260422", "20260512",
]

PRODUCTS = {
    "A": dict(dir_col="target_exposure_A", trade_col="block_id_A", m_abs_src="M_A_raw"),
    "B": dict(dir_col="position_B", trade_col="block_id_B", m_abs_src="M"),
}
PHASE_REF = "RTH_MID"
PHASE_DUMMY_LEVELS = ["RTH_OPEN", "RTH_CLOSE"]  # reference = RTH_MID
X_COLS = ["abs_value_dist_ticks", "m_abs", "sigma460_atr_proxy_pts"] + \
         [f"phase_{lvl}" for lvl in PHASE_DUMMY_LEVELS]

LOG_LINES = []


def log(msg):
    print(msg, flush=True)
    LOG_LINES.append(str(msg))


def _norm_date(s):
    return pd.to_datetime(s).dt.strftime("%Y%m%d")


def make_phase_dummies(sub):
    d = sub.copy()
    for lvl in PHASE_DUMMY_LEVELS:
        d[f"phase_{lvl}"] = (d["session_phase"] == lvl).astype(float)
    return d


# ==================================================================== STEP A: rebuild the predictor
def rebuild_clean_value_dist(df, date_list, label):
    """Overwrites value_dist_ticks / abs_value_dist_ticks in-place (returns a copy) with the
    strictly causal (timestamp<=t) reconstruction, for exactly the rows this run will use
    (date-filtered, analysis_ok==True -- matched/rth/liquid gating is untouched, computed by the
    original build). Every other column is passed through unchanged."""
    d = df.copy()
    d["_datekey"] = _norm_date(d["sess_date"])
    d = d[d["_datekey"].isin(date_list)].copy()
    ok_mask = d["analysis_ok"].to_numpy()
    log(f"[{label}] rows in date range: {len(d)}, analysis_ok: {int(ok_mask.sum())}")

    clean_vd = np.full(len(d), np.nan)
    d = d.reset_index(drop=True)
    tags_needed = sorted(d.loc[d["analysis_ok"], "sess_tag"].unique())
    log(f"[{label}] sessions needing raw-trade causal rebuild: {len(tags_needed)}: {tags_needed}")

    n_no_raw = 0
    for tag in tags_needed:
        last = load_raw_last(tag)
        if last is None or len(last) == 0:
            n_no_raw += 1
            log(f"[{label}] WARNING: {tag} has no raw bip==0 trades -- rows for this session "
                f"will get NaN clean predictor and drop out of the regression")
            continue
        poc = causal_running_poc(last)
        times_arr = poc["time"].values
        price_arr = poc["price"].values.astype(np.float64)
        poc_price_arr = poc["poc_price"].values

        rows_idx = d.index[(d["sess_tag"] == tag) & d["analysis_ok"]].to_numpy()
        q_times = d.loc[rows_idx, "time"].values
        causal_last_t, _ = causal_lookup(times_arr, price_arr, q_times)
        causal_poc_t, _ = causal_lookup(times_arr, poc_price_arr, q_times)
        vd = (causal_last_t - causal_poc_t) / TICK
        clean_vd[rows_idx] = vd

    n_ok = int(ok_mask.sum())
    n_nan_among_ok = int(np.isnan(clean_vd[ok_mask]).sum()) if n_ok else 0
    log(f"[{label}] clean predictor built: {n_ok - n_nan_among_ok}/{n_ok} analysis_ok rows got a "
        f"non-NaN causal value_dist_ticks ({n_nan_among_ok} NaN -- session missing raw data or "
        f"decision point before session's first print; these rows drop out of dropna() downstream "
        f"exactly like any other NaN predictor row would have) | sessions with no raw file: {n_no_raw}")

    d["value_dist_ticks"] = clean_vd
    d["abs_value_dist_ticks"] = np.abs(clean_vd)
    return d


# ==================================================================== STEP B: M5 regression machinery
# (copied verbatim from 02_m5_action_value_residual.py -- no methodology change)
def ols_fit(X, y):
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    yhat = X @ coef
    ss_res = float(np.sum((y - yhat) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan
    return coef, r2


def _group_index(keys_arr):
    codes, uniques = pd.factorize(keys_arr)
    idx_by_group = [np.where(codes == g)[0] for g in range(len(uniques))]
    return len(uniques), idx_by_group


def dual_cluster_ols_coef_ci(sub, y_col, x_cols, sess_col, trade_col, nboot=NBOOT, rng=RNG):
    d = sub.dropna(subset=x_cols + [y_col]).reset_index(drop=True)
    X = np.column_stack([np.ones(len(d)), d[x_cols].to_numpy(dtype=float)])
    y = d[y_col].to_numpy(dtype=float)
    coef_obs, r2_obs = ols_fit(X, y)
    beta_obs = float(coef_obs[1])
    k = X.shape[1]

    out = {"n": len(d), "beta_abs_value_dist_ticks": beta_obs, "r2": r2_obs,
           "coef_all": {c: float(v) for c, v in zip(["intercept"] + x_cols, coef_obs)}}
    for lbl, key_col in [("session_block_ci", sess_col), ("trade_block_ci", trade_col)]:
        n_groups, idx_by_group = _group_index(d[key_col].to_numpy())
        boots = np.full(nboot, np.nan)
        for b in range(nboot):
            picks = rng.integers(0, n_groups, size=n_groups)
            idx = np.concatenate([idx_by_group[g] for g in picks])
            if len(idx) < k + 5:
                continue
            Xb, yb = X[idx], y[idx]
            if np.linalg.matrix_rank(Xb) < k:
                continue
            cb, _ = ols_fit(Xb, yb)
            boots[b] = cb[1]
        boots = boots[~np.isnan(boots)]
        lo, hi = (np.percentile(boots, [2.5, 97.5]) if len(boots) else (np.nan, np.nan))
        out[lbl] = [float(lo), float(hi)]
        out[f"{lbl}_n_clusters"] = n_groups
        out[f"{lbl}_n_boots_used"] = int(len(boots))
    return out


def run_sample(df_clean, sample_label):
    rows = []
    for prod, cfg in PRODUCTS.items():
        sub = df_clean[df_clean[cfg["dir_col"]] != 0].copy()
        sub["m_abs"] = sub[cfg["m_abs_src"]].abs()
        sub = make_phase_dummies(sub)
        n_trades = sub[cfg["trade_col"]].nunique()
        n_sess = sub["sess_tag"].nunique()
        log(f"[{sample_label}] product {prod}: n={len(sub)}, trade_blocks={n_trades}, "
            f"sessions={n_sess}")

        vd_cuts = sub["abs_value_dist_ticks"].quantile([1 / 3, 2 / 3]).tolist()
        sub["vd_tercile"] = pd.cut(sub["abs_value_dist_ticks"],
                                    bins=[-np.inf, vd_cuts[0], vd_cuts[1], np.inf],
                                    labels=["near", "mid", "far"])
        mean_top = float(sub.loc[sub["vd_tercile"] == "far", "abs_value_dist_ticks"].mean())
        mean_bot = float(sub.loc[sub["vd_tercile"] == "near", "abs_value_dist_ticks"].mean())
        tercile_scale = mean_top - mean_bot

        for H in HORIZONS:
            y_col = f"signed_markout_{H}_{prod}"

            raw = dual_block_bootstrap_meandiff(sub, "vd_tercile", "far", "near", y_col,
                                                 "sess_tag", cfg["trade_col"])

            ols = dual_cluster_ols_coef_ci(sub, y_col, X_COLS, "sess_tag", cfg["trade_col"])
            beta = ols["beta_abs_value_dist_ticks"]
            controlled_effect = beta * tercile_scale
            ctrl_ci_sess = [ols["session_block_ci"][0] * tercile_scale,
                             ols["session_block_ci"][1] * tercile_scale]
            ctrl_ci_trade = [ols["trade_block_ci"][0] * tercile_scale,
                              ols["trade_block_ci"][1] * tercile_scale]
            sig_sess = not (min(ctrl_ci_sess) <= 0 <= max(ctrl_ci_sess))
            sig_trade = not (min(ctrl_ci_trade) <= 0 <= max(ctrl_ci_trade))
            significant_dual = bool(sig_sess and sig_trade)
            direction = ("deterioration" if controlled_effect < 0 else "improvement") \
                if significant_dual else "null"

            row = {
                "sample": sample_label, "product": prod, "horizon": H,
                "n": ols["n"], "n_trade_blocks": n_trades, "n_sessions": n_sess,
                "m_abs_source": cfg["m_abs_src"],
                "tercile_cuts_abs_value_dist_ticks": vd_cuts,
                "tercile_scale_far_minus_near_mean_ticks": tercile_scale,
                "raw_diff_top_minus_bottom_tercile": raw["diff"],
                "raw_mean_far": raw["mean_a"], "raw_mean_near": raw["mean_b"],
                "raw_ci_session": raw["session_block_ci"], "raw_ci_trade": raw["trade_block_ci"],
                "raw_n_far": raw["n_a"], "raw_n_near": raw["n_b"],
                "ols_beta_abs_value_dist_ticks_per_tick": beta,
                "ols_r2": ols["r2"], "ols_coef_all": ols["coef_all"],
                "controlled_effect": controlled_effect,
                "controlled_ci_session": ctrl_ci_sess, "controlled_ci_trade": ctrl_ci_trade,
                "ols_session_block_ci_beta": ols["session_block_ci"],
                "ols_trade_block_ci_beta": ols["trade_block_ci"],
                "ols_session_n_clusters": ols["session_block_ci_n_clusters"],
                "ols_trade_n_clusters": ols["trade_block_ci_n_clusters"],
                "significant_session": bool(sig_sess), "significant_trade": bool(sig_trade),
                "significant_dual": significant_dual, "direction": direction,
                "controlled_effect_pct_of_C1": controlled_effect / C1_TICKS,
                "raw_diff_pct_of_C1": raw["diff"] / C1_TICKS,
            }
            rows.append(row)
            log(f"[{sample_label}] {prod} H={H}: raw_diff={raw['diff']:+.4f}t "
                f"(sess_CI={raw['session_block_ci']}, trade_CI={raw['trade_block_ci']}) | "
                f"controlled_effect={controlled_effect:+.4f}t "
                f"(sess_CI={[round(x,4) for x in ctrl_ci_sess]}, "
                f"trade_CI={[round(x,4) for x in ctrl_ci_trade]}) | "
                f"beta={beta:+.6f}t/tick | dual_sig={significant_dual} dir={direction}")
    return rows


# ==================================================================== STEP C: stress checks
# (LOSO, remove-top-3-sessions, vol-regime median split -- same methodology as
# 05_stress_M5___value_dist_ticks__conditioned_deter.py, extended to both products since both A
# and B carry a dual-significant discovery finding in this replication's own main OLS test)
def controlled_effect_for_subset(sub_all, prod, cfg, H, with_ci=True, nboot=NBOOT, rng=None, min_n=20):
    sub = sub_all[sub_all[cfg["dir_col"]] != 0].copy()
    sub["m_abs"] = sub[cfg["m_abs_src"]].abs()
    sub = make_phase_dummies(sub)
    y_col = f"signed_markout_{H}_{prod}"
    d = sub.dropna(subset=X_COLS + [y_col]).reset_index(drop=True)
    if len(d) < min_n:
        return None
    vd_cuts = d["abs_value_dist_ticks"].quantile([1 / 3, 2 / 3]).tolist()
    if vd_cuts[0] == vd_cuts[1]:
        return None
    d["vd_tercile"] = pd.cut(d["abs_value_dist_ticks"], bins=[-np.inf, vd_cuts[0], vd_cuts[1], np.inf],
                              labels=["near", "mid", "far"])
    mean_top = float(d.loc[d["vd_tercile"] == "far", "abs_value_dist_ticks"].mean())
    mean_bot = float(d.loc[d["vd_tercile"] == "near", "abs_value_dist_ticks"].mean())
    scale = mean_top - mean_bot

    X = np.column_stack([np.ones(len(d)), d[X_COLS].to_numpy(dtype=float)])
    y = d[y_col].to_numpy(dtype=float)
    coef, r2 = ols_fit(X, y)
    beta = float(coef[1])
    controlled_effect = beta * scale

    far = d.loc[d["vd_tercile"] == "far", y_col]
    near = d.loc[d["vd_tercile"] == "near", y_col]
    raw_diff = float(far.mean() - near.mean()) if len(far) and len(near) else np.nan

    result = {"n": len(d), "n_sessions": int(d["sess_tag"].nunique()),
              "n_trade_blocks": int(d[cfg["trade_col"]].nunique()),
              "beta": beta, "tercile_scale": scale, "controlled_effect": controlled_effect,
              "raw_diff": raw_diff, "r2": r2}
    if with_ci:
        ols = dual_cluster_ols_coef_ci(d, y_col, X_COLS, "sess_tag", cfg["trade_col"],
                                        nboot=nboot, rng=rng or RNG)
        ci_sess = [ols["session_block_ci"][0] * scale, ols["session_block_ci"][1] * scale]
        ci_trade = [ols["trade_block_ci"][0] * scale, ols["trade_block_ci"][1] * scale]
        sig_sess = not (min(ci_sess) <= 0 <= max(ci_sess))
        sig_trade = not (min(ci_trade) <= 0 <= max(ci_trade))
        result.update({"ci_session": ci_sess, "ci_trade": ci_trade,
                        "n_session_clusters": ols["session_block_ci_n_clusters"],
                        "n_trade_clusters": ols["trade_block_ci_n_clusters"],
                        "significant_session": bool(sig_sess), "significant_trade": bool(sig_trade),
                        "significant_dual": bool(sig_sess and sig_trade)})
    return result


def run_stress(disc_clean, main_rows):
    stress = {}
    for prod, cfg in PRODUCTS.items():
        log("\n" + "=" * 78)
        log(f"STRESS product {prod}: LEAVE-ONE-SESSION-OUT (discovery, point estimates)")
        log("=" * 78)
        sub_full = disc_clean[disc_clean[cfg["dir_col"]] != 0]
        sessions = sorted(sub_full["sess_tag"].unique())
        baseline = {H: next(r for r in main_rows if r["sample"] == "discovery"
                             and r["product"] == prod and r["horizon"] == H) for H in HORIZONS}
        loso = {}
        for H in HORIZONS:
            deltas = []
            for s in sessions:
                sub_loso = disc_clean[disc_clean["sess_tag"] != s]
                res = controlled_effect_for_subset(sub_loso, prod, cfg, H, with_ci=False)
                ce = res["controlled_effect"] if res is not None else np.nan
                deltas.append({"session_removed": s, "controlled_effect": ce})
            loso[H] = deltas
            vals = np.array([r["controlled_effect"] for r in deltas if not np.isnan(r["controlled_effect"])])
            base_ce = baseline[H]["controlled_effect"]
            base_sign = np.sign(base_ce)
            n_same_sign = int((np.sign(vals) == base_sign).sum())
            log(f"[discovery,{prod}] H={H}: LOSO n={len(vals)}/{len(sessions)} | full-sample="
                f"{base_ce:+.3f}t | range=[{vals.min():+.3f},{vals.max():+.3f}]t mean={vals.mean():+.3f}t "
                f"std={vals.std():.3f}t | sign-stable {n_same_sign}/{len(vals)} "
                f"({100*n_same_sign/len(vals):.1f}%)")

        # influence ranking -> top-3 removal
        score = {s: [] for s in sessions}
        for H in HORIZONS:
            base_ce = baseline[H]["controlled_effect"]
            for r in loso[H]:
                if np.isnan(r["controlled_effect"]):
                    continue
                score[r["session_removed"]].append((r["controlled_effect"] - base_ce) / abs(base_ce))
        influence = {s: float(np.mean(v)) if v else np.nan for s, v in score.items()}
        ranked = sorted(influence.items(), key=lambda kv: -kv[1])
        top3 = [ranked[i][0] for i in range(3)]
        log(f"[discovery,{prod}] top-3 most-influential sessions (removing them weakens the "
            f"finding most): {top3}")

        sub_drop = disc_clean[~disc_clean["sess_tag"].isin(top3)]
        top3_res = {}
        for H in HORIZONS:
            res = controlled_effect_for_subset(sub_drop, prod, cfg, H, with_ci=True, nboot=NBOOT, rng=RNG)
            top3_res[H] = res
            base_ce = baseline[H]["controlled_effect"]
            log(f"[discovery,{prod},remove_top3={top3}] H={H}: controlled_effect="
                f"{res['controlled_effect']:+.3f}t (full-sample {base_ce:+.3f}t) | "
                f"n_sessions={res['n_sessions']} | sess_CI={[round(x,3) for x in res['ci_session']]} "
                f"trade_CI={[round(x,3) for x in res['ci_trade']]} | dual_sig={res['significant_dual']}")

        # vol-regime median split by session-mean sigma460_atr_proxy_pts (computed on the
        # PRODUCT-FILTERED subset only -- matches the original stress script's own `disc`, which
        # is already restricted to the product's in-direction rows before this split, NOT the
        # product-agnostic analysis_ok frame)
        sess_sigma = sub_full.groupby("sess_tag")["sigma460_atr_proxy_pts"].mean().sort_values()
        n_sess = len(sess_sigma)
        low_vol = set(sess_sigma.index[: n_sess // 2 + n_sess % 2])
        high_vol = set(sess_sigma.index) - low_vol
        log(f"[discovery,{prod}] low-vol sessions (n={len(low_vol)}): {sorted(low_vol)}")
        log(f"[discovery,{prod}] high-vol sessions (n={len(high_vol)}): {sorted(high_vol)}")
        vol_res = {"low_vol": {}, "high_vol": {}}
        for tag, sess_set in [("low_vol", low_vol), ("high_vol", high_vol)]:
            sub_v = disc_clean[disc_clean["sess_tag"].isin(sess_set)]
            for H in HORIZONS:
                res = controlled_effect_for_subset(sub_v, prod, cfg, H, with_ci=True, nboot=NBOOT, rng=RNG)
                vol_res[tag][H] = res
                if res is None:
                    log(f"[discovery,{prod},{tag}] H={H}: subset too small to fit")
                    continue
                log(f"[discovery,{prod},{tag}] H={H}: controlled_effect={res['controlled_effect']:+.3f}t "
                    f"| n={res['n']}, n_sessions={res['n_sessions']} | "
                    f"sess_CI={[round(x,3) for x in res['ci_session']]} "
                    f"trade_CI={[round(x,3) for x in res['ci_trade']]} | dual_sig={res['significant_dual']}")

        stress[prod] = {
            "loso": {str(H): loso[H] for H in HORIZONS},
            "loso_sign_stability": {
                str(H): {
                    "n": int(np.sum(~np.isnan([r["controlled_effect"] for r in loso[H]]))),
                    "n_same_sign_as_full_sample": int(np.sum(
                        np.sign([r["controlled_effect"] for r in loso[H] if not np.isnan(r["controlled_effect"])])
                        == np.sign(baseline[H]["controlled_effect"]))),
                    "min": float(np.nanmin([r["controlled_effect"] for r in loso[H]])),
                    "max": float(np.nanmax([r["controlled_effect"] for r in loso[H]])),
                    "mean": float(np.nanmean([r["controlled_effect"] for r in loso[H]])),
                    "std": float(np.nanstd([r["controlled_effect"] for r in loso[H]])),
                } for H in HORIZONS
            },
            "influence_ranking": ranked,
            "top3_sessions_removed": top3,
            "remove_top3_results": {str(H): top3_res[H] for H in HORIZONS},
            "vol_split_sessions": {"low_vol": sorted(low_vol), "high_vol": sorted(high_vol)},
            "vol_split_results": {tag: {str(H): vol_res[tag][H] for H in HORIZONS} for tag in vol_res},
        }
    return stress


def main():
    disc_path = os.path.join(ROOT, "runs", "AUCTION02_ACTION_RELEVANCE", "out", "action_substrate.parquet")
    conf_path = os.path.join(ROOT, "runs", "W5_PROTECTED_CONFIRMATION", "results", "out",
                              "action_substrate_CONFIRM.parquet")
    disc_raw = pd.read_parquet(disc_path)
    conf_raw = pd.read_parquet(conf_path)

    log("=" * 78)
    log("STEP A: rebuilding causally-correct value_dist_ticks/abs_value_dist_ticks")
    log("=" * 78)
    disc_clean = rebuild_clean_value_dist(disc_raw, DISCOVERY_DATES, "discovery")
    conf_clean = rebuild_clean_value_dist(conf_raw, CONFIRM_DATES, "confirmation")

    disc_ok = disc_clean[disc_clean["analysis_ok"]].copy()
    conf_ok = conf_clean[conf_clean["analysis_ok"]].copy()
    log(f"[discovery] analysis_ok rows carried into regression: {len(disc_ok)} "
        f"(dates={sorted(disc_ok['_datekey'].unique())})")
    log(f"[confirmation] analysis_ok rows carried into regression: {len(conf_ok)} "
        f"(dates={sorted(conf_ok['_datekey'].unique())})")

    # sanity: compare corrected vs original predictor on the same rows (magnitude check, not a
    # methodology change -- purely diagnostic logging)
    orig_ok = disc_raw.copy()
    orig_ok["_datekey"] = _norm_date(orig_ok["sess_date"])
    orig_ok = orig_ok[orig_ok["_datekey"].isin(DISCOVERY_DATES) & orig_ok["analysis_ok"]]
    merged_cmp = disc_ok[["sess_tag", "time", "abs_value_dist_ticks"]].merge(
        orig_ok[["sess_tag", "time", "abs_value_dist_ticks"]], on=["sess_tag", "time"],
        suffixes=("_clean", "_orig"))
    diff = (merged_cmp["abs_value_dist_ticks_clean"] - merged_cmp["abs_value_dist_ticks_orig"])
    log(f"[diagnostic] discovery abs_value_dist_ticks clean-vs-original: n={len(merged_cmp)}, "
        f"median|diff|={diff.abs().median():.3f}t, mean|diff|={diff.abs().mean():.3f}t, "
        f"max|diff|={diff.abs().max():.3f}t, pct_rows_changed={(diff.abs() > 1e-9).mean()*100:.1f}%")

    log("\n" + "=" * 78)
    log("STEP B: M5 OLS-controlled top-vs-bottom-tercile effect (clean predictor)")
    log("=" * 78)
    all_rows = []
    all_rows += run_sample(disc_ok, "discovery")
    all_rows += run_sample(conf_ok, "confirmation")

    log("\n" + "=" * 78)
    log("STEP C: STRESS CHECKS (LOSO, remove-top-3, vol-regime split; discovery, both products)")
    log("=" * 78)
    stress = run_stress(disc_ok, all_rows)

    # ---------------------------------------------------------------- write outputs
    out_df = pd.DataFrame([{k: v for k, v in r.items()
                             if k not in ("ols_coef_all", "tercile_cuts_abs_value_dist_ticks",
                                          "raw_ci_session", "raw_ci_trade",
                                          "controlled_ci_session", "controlled_ci_trade",
                                          "ols_session_block_ci_beta", "ols_trade_block_ci_beta")}
                            for r in all_rows])
    ci_cols = ["raw_ci_session", "raw_ci_trade", "controlled_ci_session", "controlled_ci_trade",
               "ols_session_block_ci_beta", "ols_trade_block_ci_beta"]
    for col in ci_cols:
        out_df[f"{col}_lo"] = [r[col][0] for r in all_rows]
        out_df[f"{col}_hi"] = [r[col][1] for r in all_rows]
    out_df["tercile_cut_lo"] = [r["tercile_cuts_abs_value_dist_ticks"][0] for r in all_rows]
    out_df["tercile_cut_hi"] = [r["tercile_cuts_abs_value_dist_ticks"][1] for r in all_rows]

    csv_path = os.path.join(OUT, "m5_clean_action_value.csv")
    out_df.to_csv(csv_path, index=False)

    json_path = os.path.join(OUT, "m5_clean_action_value.json")
    with open(json_path, "w") as f:
        json.dump({
            "rows": all_rows, "c1_ticks": C1_TICKS,
            "discovery_dates": DISCOVERY_DATES, "confirmation_dates": CONFIRM_DATES,
            "predictor_correction_diagnostic": {
                "n_compared": int(len(merged_cmp)),
                "median_abs_diff_ticks": float(diff.abs().median()),
                "mean_abs_diff_ticks": float(diff.abs().mean()),
                "max_abs_diff_ticks": float(diff.abs().max()),
                "pct_rows_changed": float((diff.abs() > 1e-9).mean() * 100),
            },
            "stress_checks": stress,
            "notes": (
                "R_aligned = signed_markout_H_{prod} directly (already incumbent-direction-"
                "aligned at action_substrate build time; carried over unchanged from AUCTION02/"
                "W5's build, defect 1 [4x units bug] does not apply to action_substrate's "
                "outcome columns -- see module docstring). value_dist_ticks/abs_value_dist_ticks "
                "rebuilt causally (defect 2 fix) via AUCTION04's certified causal_running_poc/"
                "causal_lookup, reused verbatim. Stress checks (LOSO, remove-top-3, vol-regime "
                "split) run for both products A and B on the discovery sample, since both carry "
                "a dual-significant finding in this replication's main OLS test."
            ),
        }, f, indent=2, default=float)

    log(f"\nWrote {csv_path}")
    log(f"Wrote {json_path}")

    log_path = os.path.join(OUT, "m5_clean_action_value_log.txt")
    with open(log_path, "w") as f:
        f.write("\n".join(LOG_LINES) + "\n")
    log(f"Wrote {log_path}")
    log("M5 CLEAN ACTION-VALUE REPLICATION DONE")


if __name__ == "__main__":
    main()
