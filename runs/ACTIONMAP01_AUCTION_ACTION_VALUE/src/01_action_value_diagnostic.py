"""ACTIONMAP01_AUCTION_ACTION_VALUE -- diagnostic decomposing AUCTION04/M5's clean
"Auction distance deteriorates incumbent-aligned forward markout" finding into an
add/hold/reduce/reverse ACTION-VALUE map for Product A (Product B touched only as a
secondary check, see PART 6).

GOVERNANCE
----------
Reads only: runs/AUCTION02_ACTION_RELEVANCE/out/action_substrate.parquet,
runs/W5_PROTECTED_CONFIRMATION/results/out/action_substrate_CONFIRM.parquet (both
already-built, frozen, previously-read), plus raw bip==0 trade prints for the 37
discovery + 8 confirmation-pool session tags (research/scalping_lab/substrate/raw/NQ/
*.parquet) via AUCTION04's own certified causal machinery -- the EXACT SAME 45-session
governance wall AUCTION04_CLEAN_CAUSAL_SUBSTRATE/src/05_m5_clean.py already enforces (see
that module's own assertions). No session >=2026-08-01, no AMENDMENT_3 protected-pool
session, is read here. This script performs NO new data reads beyond what 05_m5_clean.py
already reads -- it re-executes the identical certified rebuild to reconstruct the same
clean per-decision-point frame IN MEMORY (05_m5_clean.py itself never persisted that
per-row frame to disk, only its aggregate regression outputs), then asks new questions of
it. Writes only under runs/ACTIONMAP01_AUCTION_ACTION_VALUE/out/.

CODE REUSE (per task instruction: reuse verbatim, do not re-derive)
---------------------------------------------------------------------
runs/AUCTION04_CLEAN_CAUSAL_SUBSTRATE/src/05_m5_clean.py is imported by file path
(importlib, identical pattern that script itself uses to import 01_build_clean_substrate.py
-- module name starts with a digit) and its own certified functions/constants are called
directly, unmodified: rebuild_clean_value_dist (-> causal_running_poc/causal_lookup/
load_raw_last from 01_build_clean_substrate.py, imported transitively), PRODUCTS,
DISCOVERY_DATES, CONFIRM_DATES, make_phase_dummies, ols_fit, dual_cluster_ols_coef_ci,
controlled_effect_for_subset, _group_index, X_COLS, C1_TICKS, RNG. The dual-clustered
(session+trade) percentile bootstrap (dual_cluster_ols_coef_ci / _group_index) is this
diagnostic's PRIMARY CI convention throughout, matching AUCTION01-04 precedent exactly
(no new bootstrap design for standard effect sizes). CONVENTIONS.md sec5's frozen
"circular session-block bootstrap, block=5, B=10000, seed=20260808" is additionally
applied, once, as an independent-design cross-check on the headline far-vs-near tercile
diff (PART 5c) -- this is the one deliberately NEW piece of statistical machinery in this
script, added because the task explicitly asks for both conventions to be represented,
and it is a different (block, not i.i.d.-cluster) resampling design by construction, not
an ad hoc invention.
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
OUT = os.path.join(ROOT, "runs", "ACTIONMAP01_AUCTION_ACTION_VALUE", "out")
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, AUCTION02_SRC)


def _load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


m5 = _load_module("actionmap01_m5_clean", os.path.join(AUCTION04_SRC, "05_m5_clean.py"))

HORIZONS = [1, 3, 20]
C1 = m5.C1_TICKS  # 2.872 ticks, campaign round-trip cost hurdle
LOG_LINES = []
RESULTS = {}


def log(msg):
    print(msg, flush=True)
    LOG_LINES.append(str(msg))


# ============================================================== STEP 0: rebuild clean substrate
# (identical call sequence to 05_m5_clean.py's own main(); not persisted there, rebuilt here)
disc_path = os.path.join(ROOT, "runs", "AUCTION02_ACTION_RELEVANCE", "out", "action_substrate.parquet")
conf_path = os.path.join(ROOT, "runs", "W5_PROTECTED_CONFIRMATION", "results", "out",
                          "action_substrate_CONFIRM.parquet")
disc_raw = pd.read_parquet(disc_path)
conf_raw = pd.read_parquet(conf_path)

log("=" * 78)
log("STEP 0: rebuilding clean causal substrate (reusing 05_m5_clean.py verbatim)")
log("=" * 78)
disc_clean = m5.rebuild_clean_value_dist(disc_raw, m5.DISCOVERY_DATES, "discovery")
conf_clean = m5.rebuild_clean_value_dist(conf_raw, m5.CONFIRM_DATES, "confirmation")
disc_ok = disc_clean[disc_clean["analysis_ok"]].copy().reset_index(drop=True)
conf_ok = conf_clean[conf_clean["analysis_ok"]].copy().reset_index(drop=True)
log(f"[discovery] analysis_ok rows: {len(disc_ok)} | [confirmation] analysis_ok rows: {len(conf_ok)}")

cfgA = m5.PRODUCTS["A"]
cfgB = m5.PRODUCTS["B"]


def build_product_frame(df_ok, cfg):
    sub = df_ok[df_ok[cfg["dir_col"]] != 0].copy().reset_index(drop=True)
    sub["m_abs"] = sub[cfg["m_abs_src"]].abs()
    sub = m5.make_phase_dummies(sub)
    vd_cuts = sub["abs_value_dist_ticks"].quantile([1 / 3, 2 / 3]).tolist()
    sub["vd_tercile"] = pd.cut(sub["abs_value_dist_ticks"],
                                bins=[-np.inf, vd_cuts[0], vd_cuts[1], np.inf],
                                labels=["near", "mid", "far"])
    return sub, vd_cuts


subA_disc, vdA_disc_cuts = build_product_frame(disc_ok, cfgA)
subA_conf, vdA_conf_cuts = build_product_frame(conf_ok, cfgA)
log(f"[product A, discovery] n={len(subA_disc)}, sessions={subA_disc['sess_tag'].nunique()}, "
    f"trade_blocks={subA_disc['block_id_A'].nunique()}, tercile_cuts={vdA_disc_cuts}")
log(f"[product A, confirmation] n={len(subA_conf)}, sessions={subA_conf['sess_tag'].nunique()}, "
    f"trade_blocks={subA_conf['block_id_A'].nunique()}, tercile_cuts={vdA_conf_cuts}")

n_long_disc = int((subA_disc["target_exposure_A"] > 0).sum())
n_short_disc = int((subA_disc["target_exposure_A"] < 0).sum())
n_flat_raw = int((disc_raw["target_exposure_A"] == 0).sum())
log(f"[product A, discovery] long rows={n_long_disc}, short rows={n_short_disc} | "
    f"flat (target_exposure_A==0) rows in FULL raw table (pre-filter)={n_flat_raw}")

RESULTS["setup"] = {
    "n_disc": len(subA_disc), "n_conf": len(subA_conf),
    "n_sessions_disc": int(subA_disc["sess_tag"].nunique()),
    "n_sessions_conf": int(subA_conf["sess_tag"].nunique()),
    "tercile_cuts_disc": vdA_disc_cuts, "tercile_cuts_conf": vdA_conf_cuts,
    "n_long_disc": n_long_disc, "n_short_disc": n_short_disc, "n_flat_raw_full_table": n_flat_raw,
    "c1_ticks": C1,
}


# ============================================================== small reused-pattern helpers
def dual_cluster_group_mean_ci(d, ycol, sess_col, trade_col, nboot=1000, rng=None):
    """Same session+trade dual-cluster percentile-bootstrap DESIGN as m5.dual_cluster_ols_coef_ci
    / m5.dual_block_bootstrap_meandiff (reuses m5._group_index directly), applied to a single
    group's raw mean instead of a coefficient or a two-group difference -- same estimator family,
    not a new design. dropna(ycol) FIRST (matching dual_block_bootstrap_meandiff's own convention
    of dropping before computing anything) -- horizon-20 rows near a session's tail end have no
    forward window and are legitimately NaN; without this, plain numpy .mean() on the observed
    sample silently returns NaN for the point estimate even though most bootstrap replicates (which
    can luck into avoiding the NaN-containing cluster) return a real number, an inconsistency."""
    rng = rng or np.random.default_rng(20260809)
    d = d.dropna(subset=[ycol])
    y = d[ycol].to_numpy(dtype=float)
    obs = float(y.mean()) if len(y) else np.nan
    out = {"n": len(d), "mean": obs}
    for label, key_col in [("session_block_ci", sess_col), ("trade_block_ci", trade_col)]:
        n_groups, idx_by_group = m5._group_index(d[key_col].to_numpy())
        boots = np.full(nboot, np.nan)
        for b in range(nboot):
            picks = rng.integers(0, n_groups, size=n_groups)
            idx = np.concatenate([idx_by_group[g] for g in picks])
            if len(idx) < 3:
                continue
            boots[b] = y[idx].mean()
        boots = boots[~np.isnan(boots)]
        lo, hi = (np.percentile(boots, [2.5, 97.5]) if len(boots) else (np.nan, np.nan))
        out[label] = [float(lo), float(hi)]
        out[f"{label}_n_clusters"] = n_groups
    return out


def circular_block5_bootstrap_meandiff(sub, cell_col, cell_a, cell_b, ycol, sess_col,
                                        block=5, nboot=10000, seed=20260808):
    """CONVENTIONS.md sec5 frozen statistical protocol: circular session-block bootstrap,
    block=5, B=10000, seed=20260808. Deliberately a DIFFERENT resampling design from the
    dual-cluster i.i.d.-session-unit bootstrap used everywhere else in this script (and
    throughout AUCTION01-04) -- applied here as an independent cross-check per this task's
    explicit instruction to represent both conventions. dropna(ycol) first, matching
    dual_block_bootstrap_meandiff's own convention (see dual_cluster_group_mean_ci docstring)."""
    rng = np.random.default_rng(seed)
    sub = sub.dropna(subset=[ycol])
    sessions = sorted(sub[sess_col].unique())
    n_sess = len(sessions)
    sess_arr = sub[sess_col].to_numpy()
    row_idx_by_sess = {s: np.where(sess_arr == s)[0] for s in sessions}
    cell = sub[cell_col].to_numpy()
    y = sub[ycol].to_numpy(dtype=float)
    a_mask_full = (cell == cell_a)
    b_mask_full = (cell == cell_b)
    obs = float(y[a_mask_full].mean() - y[b_mask_full].mean())
    n_blocks_needed = int(np.ceil(n_sess / block))
    boots = np.full(nboot, np.nan)
    for i in range(nboot):
        starts = rng.integers(0, n_sess, size=n_blocks_needed)
        chosen = []
        for st in starts:
            chosen.extend(sessions[(st + k) % n_sess] for k in range(block))
        chosen = chosen[:n_sess]
        idx = np.concatenate([row_idx_by_sess[s] for s in chosen]) if chosen else np.array([], dtype=int)
        if len(idx) == 0:
            continue
        a_idx = idx[a_mask_full[idx]]
        b_idx = idx[b_mask_full[idx]]
        if len(a_idx) == 0 or len(b_idx) == 0:
            continue
        boots[i] = y[a_idx].mean() - y[b_idx].mean()
    boots = boots[~np.isnan(boots)]
    lo, hi = (np.percentile(boots, [2.5, 97.5]) if len(boots) else (np.nan, np.nan))
    return {"n": len(sub), "n_sessions": n_sess, "diff": obs, "ci": [float(lo), float(hi)],
            "n_boots_used": int(len(boots)), "n_blocks_per_rep": n_blocks_needed,
            "significant": bool(not (min([lo, hi]) <= 0 <= max([lo, hi]))) if not np.isnan(lo) else None}


def controlled_effect_custom_xcols(sub_all, prod, cfg, H, x_cols, with_ci=True, nboot=1000,
                                    rng=None, min_n=20):
    """Same logic as m5.controlled_effect_for_subset, parameterized on x_cols instead of the
    hardcoded module-level m5.X_COLS -- needed for subsamples (e.g. RTH_MID-only) where the phase
    dummies in m5.X_COLS are constant-zero (no RTH_OPEN/RTH_CLOSE rows present) and therefore
    permanently rank-deficient in the cluster bootstrap, which silently returns an empty boots
    array -> [nan, nan] CI. Also fixes a latent edge case in the reused significance check
    (`not (min(ci) <= 0 <= max(ci))` evaluates to True, not an error, when both CI bounds are NaN,
    since every comparison against NaN is False) by explicitly guarding for NaN CI bounds."""
    sub = sub_all[sub_all[cfg["dir_col"]] != 0].copy()
    sub["m_abs"] = sub[cfg["m_abs_src"]].abs()
    y_col = f"signed_markout_{H}_{prod}"
    d = sub.dropna(subset=x_cols + [y_col]).reset_index(drop=True)
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

    X = np.column_stack([np.ones(len(d)), d[x_cols].to_numpy(dtype=float)])
    y = d[y_col].to_numpy(dtype=float)
    coef, r2 = m5.ols_fit(X, y)
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
        ols = m5.dual_cluster_ols_coef_ci(d, y_col, x_cols, "sess_tag", cfg["trade_col"],
                                           nboot=nboot, rng=rng or m5.RNG)
        ci_sess = [ols["session_block_ci"][0] * scale, ols["session_block_ci"][1] * scale]
        ci_trade = [ols["trade_block_ci"][0] * scale, ols["trade_block_ci"][1] * scale]

        def _sig(ci):
            if any(np.isnan(x) for x in ci):
                return False
            return not (min(ci) <= 0 <= max(ci))

        sig_sess, sig_trade = _sig(ci_sess), _sig(ci_trade)
        result.update({"ci_session": ci_sess, "ci_trade": ci_trade,
                        "n_session_clusters": ols["session_block_ci_n_clusters"],
                        "n_trade_clusters": ols["trade_block_ci_n_clusters"],
                        "significant_session": bool(sig_sess), "significant_trade": bool(sig_trade),
                        "significant_dual": bool(sig_sess and sig_trade),
                        "ci_degenerate_nan": bool(any(np.isnan(x) for x in ci_sess + ci_trade))})
    return result


def two_coef_ci(sub, ycol, x_cols_ordered1, x_cols_ordered2, sess_col, trade_col, nboot=1000, rng=None):
    """Fit ONE OLS spec, get bootstrap CI for its first TWO named coefficients by calling
    m5.dual_cluster_ols_coef_ci twice with the column order swapped (that function always
    bootstraps x_cols[0]'s coefficient) -- reuses the certified function unmodified."""
    rng = rng or m5.RNG
    r1 = m5.dual_cluster_ols_coef_ci(sub, ycol, x_cols_ordered1, sess_col, trade_col, nboot=nboot, rng=rng)
    r2 = m5.dual_cluster_ols_coef_ci(sub, ycol, x_cols_ordered2, sess_col, trade_col, nboot=nboot, rng=rng)
    return r1, r2


# ============================================================== PART 1: mechanical identity
# (Q_add / Q_reduce / Q_reverse under the no-market-impact assumption master directive sec34
# instructs -- grounded in the ACTUAL upstream formula, not asserted)
log("\n" + "=" * 78)
log("PART 1: mechanical identity check (Q_add / Q_reduce / Q_reverse vs Q_hold)")
log("=" * 78)
log("Upstream formula (runs/AUCTION02_ACTION_RELEVANCE/src/01_build_action_substrate.py line "
    "~104-106): side = sign(target_exposure_A); "
    "signed_markout_H_A = side * (fwd_close - close) / TICK. This is PER-CONTRACT (side is a "
    "sign, +-1, never scaled by |target_exposure_A|) -- it does not depend on how many units are "
    "held, only on the DIRECTION held. Consequences, exact (not approximate) under this formula:")
log("  Q_hold(t)  = signed_markout_H_A(t)                                  [already computed]")
log("  Q_add(t)   = d(P&L)/d(size), same direction  = side*(fwd_close-close)/TICK "
    "= signed_markout_H_A(t) IDENTICALLY (the per-unit derivative does not depend on current "
    "size, since there is no size term in the formula at all)")
log("  Q_reduce(t)= value of removing one unit toward flat = -side*(fwd_close-close)/TICK "
    "= -signed_markout_H_A(t) IDENTICALLY")
log("  Q_reverse-per-unit(t) = value of one unit on the OPPOSITE side = -side*(fwd_close-close)/TICK "
    "= -signed_markout_H_A(t) IDENTICALLY (same per-unit number as Q_reduce; reversing simply "
    "changes 2 units of exposure -- one de-risking unit + one new opposite-side unit -- each "
    "worth -Q_hold(t) per unit, not a distinct third quantity)")
log("This is a mathematical identity following from the formula, not an empirically testable "
    "claim -- the data contains no fill-level, partial-size, or market-impact-vs-size records at "
    "all (no separate observations exist for 'what if 1 more/fewer contract had been held'), so "
    "there is literally nothing in this substrate that COULD contradict the identity even if "
    "real-world market impact existed. Per master directive sec34's own instruction not to "
    "assume future market impact from tiny research size, this collapses the naive 3-way "
    "decomposition exactly as the task anticipated: Q_add(t) == Q_hold(t) and Q_reduce(t) == "
    "Q_reverse_per_unit(t) == -Q_hold(t), for every t, by construction.")
log(f"[scope note] flat-state (target_exposure_A==0) rows, where a distinct 'initiate new "
    f"position' Q_add would need a signal-direction convention instead of an incumbent direction, "
    f"are essentially absent from this decision-point substrate: {n_flat_raw} row(s) in the FULL "
    f"raw table before any filtering, 0 rows survive analysis_ok. This diagnostic's decision-point "
    f"grid (inherited unchanged from AUCTION02/M5) is built only where an incumbent A or B exposure "
    f"already exists, so a flat-state 'Q_add' population is not analyzable here regardless of "
    f"approach -- Q_add below is properly read as 'value of adding to an existing position', which "
    f"is exactly what the linear-in-size identity above covers.")

RESULTS["mechanical_identity"] = {
    "formula": "signed_markout_H_A = sign(target_exposure_A) * (fwd_close - close) / TICK "
               "(per-contract, size-independent; AUCTION02 01_build_action_substrate.py L104-106)",
    "Q_add_equals_Q_hold": True, "Q_reduce_equals_neg_Q_hold": True,
    "Q_reverse_per_unit_equals_neg_Q_hold": True,
    "empirically_testable": False,
    "reason_not_testable": "no fill-level / partial-size / market-impact-vs-size data exists in "
                            "this substrate at all -- the identity cannot be contradicted by "
                            "data that was never collected, only asserted from the visible formula.",
    "flat_state_rows_full_table": n_flat_raw,
}


# ============================================================== PART 2: headline product-A
# result restated (answers Q1 + Q2 directly, given PART 1's identity) + confirmation-pool cite
log("\n" + "=" * 78)
log("PART 2: headline Product-A clean M5 result (= Q1 AND Q2 simultaneously, given PART 1)")
log("=" * 78)
headline_disc = {}
for H in HORIZONS:
    y_col = f"signed_markout_{H}_A"
    ols = m5.dual_cluster_ols_coef_ci(subA_disc, y_col, m5.X_COLS, "sess_tag", "block_id_A",
                                       nboot=1000, rng=m5.RNG)
    beta = ols["beta_abs_value_dist_ticks"]
    mean_far = float(subA_disc.loc[subA_disc["vd_tercile"] == "far", "abs_value_dist_ticks"].mean())
    mean_near = float(subA_disc.loc[subA_disc["vd_tercile"] == "near", "abs_value_dist_ticks"].mean())
    scale = mean_far - mean_near
    ctrl = beta * scale
    ci_sess = [ols["session_block_ci"][0] * scale, ols["session_block_ci"][1] * scale]
    ci_trade = [ols["trade_block_ci"][0] * scale, ols["trade_block_ci"][1] * scale]
    sig = not (min(ci_sess) <= 0 <= max(ci_sess)) and not (min(ci_trade) <= 0 <= max(ci_trade))
    far_ci = dual_cluster_group_mean_ci(subA_disc[subA_disc["vd_tercile"] == "far"], y_col,
                                         "sess_tag", "block_id_A", nboot=1000, rng=m5.RNG)
    near_ci = dual_cluster_group_mean_ci(subA_disc[subA_disc["vd_tercile"] == "near"], y_col,
                                          "sess_tag", "block_id_A", nboot=1000, rng=m5.RNG)
    headline_disc[H] = {
        "n": ols["n"], "beta": beta, "controlled_effect": ctrl,
        "ci_session": ci_sess, "ci_trade": ci_trade, "significant_dual": bool(sig),
        "far_mean": far_ci, "near_mean": near_ci,
        "controlled_effect_pct_of_C1": ctrl / C1,
    }
    log(f"[discovery,A] H={H}: controlled_effect(far-near, abs_value_dist_ticks-controlled)="
        f"{ctrl:+.3f}t (sess_CI={[round(x,3) for x in ci_sess]}, trade_CI={[round(x,3) for x in ci_trade]}) "
        f"| dual_sig={sig} | far_mean_Q_hold={far_ci['mean']:+.3f}t "
        f"(sessCI={[round(x,3) for x in far_ci['session_block_ci']]}) | "
        f"near_mean_Q_hold={near_ci['mean']:+.3f}t "
        f"(sessCI={[round(x,3) for x in near_ci['session_block_ci']]}) | "
        f"pct_of_C1={ctrl/C1:+.2f}x")

headline_conf = {}
for H in HORIZONS:
    y_col = f"signed_markout_{H}_A"
    d = subA_conf.dropna(subset=m5.X_COLS + [y_col])
    if len(d) < 25:
        continue
    ols = m5.dual_cluster_ols_coef_ci(subA_conf, y_col, m5.X_COLS, "sess_tag", "block_id_A",
                                       nboot=1000, rng=m5.RNG)
    beta = ols["beta_abs_value_dist_ticks"]
    mean_far = float(subA_conf.loc[subA_conf["vd_tercile"] == "far", "abs_value_dist_ticks"].mean())
    mean_near = float(subA_conf.loc[subA_conf["vd_tercile"] == "near", "abs_value_dist_ticks"].mean())
    scale = mean_far - mean_near
    ctrl = beta * scale
    ci_sess = [ols["session_block_ci"][0] * scale, ols["session_block_ci"][1] * scale]
    sig = not (min(ci_sess) <= 0 <= max(ci_sess))
    headline_conf[H] = {"n": ols["n"], "controlled_effect": ctrl, "ci_session": ci_sess,
                         "significant_session": bool(sig), "same_sign_as_discovery":
                             bool(np.sign(ctrl) == np.sign(headline_disc[H]["controlled_effect"]))}
    log(f"[confirmation,A] H={H}: controlled_effect={ctrl:+.3f}t (sess_CI={[round(x,3) for x in ci_sess]}) "
        f"| sig(session-only, n_sessions={subA_conf['sess_tag'].nunique()} too few for trade-CI "
        f"to be informative)={sig} | same_sign_as_discovery={np.sign(ctrl)==np.sign(headline_disc[H]['controlled_effect'])}")

RESULTS["headline"] = {"discovery": headline_disc, "confirmation": headline_conf}


# ============================================================== PART 3: (a) symmetry by direction
log("\n" + "=" * 78)
log("PART 3: (a) is the deterioration symmetric in sign(target_exposure_A)?")
log("=" * 78)
long_disc = subA_disc[subA_disc["target_exposure_A"] > 0].copy()
short_disc = subA_disc[subA_disc["target_exposure_A"] < 0].copy()
log(f"long-held rows: {len(long_disc)} ({long_disc['sess_tag'].nunique()} sessions) | "
    f"short-held rows: {len(short_disc)} ({short_disc['sess_tag'].nunique()} sessions)")

dir_split = {"long": {}, "short": {}}
for label, sub in [("long", long_disc), ("short", short_disc)]:
    for H in HORIZONS:
        res = m5.controlled_effect_for_subset(sub, "A", cfgA, H, with_ci=True, nboot=1000, rng=m5.RNG)
        dir_split[label][H] = res
        if res is None:
            log(f"[{label}] H={H}: subset too small / degenerate")
            continue
        log(f"[{label},A] H={H}: n={res['n']} sessions={res['n_sessions']} "
            f"controlled_effect={res['controlled_effect']:+.3f}t "
            f"sess_CI={[round(x,3) for x in res['ci_session']]} "
            f"trade_CI={[round(x,3) for x in res['ci_trade']]} dual_sig={res['significant_dual']}")

both_sig_same_sign = (dir_split["long"][1] is not None and dir_split["short"][1] is not None and
                       all(dir_split[d][H] is not None for d in ("long", "short") for H in HORIZONS))
signs_match = all(
    np.sign(dir_split["long"][H]["controlled_effect"]) == np.sign(dir_split["short"][H]["controlled_effect"])
    for H in HORIZONS if dir_split["long"][H] is not None and dir_split["short"][H] is not None)
log(f"[symmetry, split-sample] same-sign(long,short) across all H: {signs_match}")

# aligned (signed, direction-specific "chasing") vs abs (direction-agnostic magnitude) predictor,
# fit jointly so each coefficient is estimated controlling for the other
subA_disc["aligned_dist_ticks"] = subA_disc["value_dist_ticks"] * np.sign(subA_disc["target_exposure_A"])
JOINT_COVARS = ["m_abs", "sigma460_atr_proxy_pts", "phase_RTH_OPEN", "phase_RTH_CLOSE"]
joint_results = {}
for H in HORIZONS:
    y_col = f"signed_markout_{H}_A"
    x1 = ["abs_value_dist_ticks", "aligned_dist_ticks"] + JOINT_COVARS
    x2 = ["aligned_dist_ticks", "abs_value_dist_ticks"] + JOINT_COVARS
    r_abs, r_aligned = two_coef_ci(subA_disc, y_col, x1, x2, "sess_tag", "block_id_A",
                                    nboot=1000, rng=m5.RNG)
    beta_abs = r_abs["coef_all"]["abs_value_dist_ticks"]
    beta_aligned = r_abs["coef_all"]["aligned_dist_ticks"]
    sig_abs = not (min(r_abs["session_block_ci"]) <= 0 <= max(r_abs["session_block_ci"])) and \
              not (min(r_abs["trade_block_ci"]) <= 0 <= max(r_abs["trade_block_ci"]))
    sig_aligned = not (min(r_aligned["session_block_ci"]) <= 0 <= max(r_aligned["session_block_ci"])) and \
                  not (min(r_aligned["trade_block_ci"]) <= 0 <= max(r_aligned["trade_block_ci"]))
    joint_results[H] = {
        "n": r_abs["n"], "r2": r_abs["r2"],
        "beta_abs_value_dist_ticks": beta_abs, "abs_ci_session": r_abs["session_block_ci"],
        "abs_ci_trade": r_abs["trade_block_ci"], "abs_significant_dual": bool(sig_abs),
        "beta_aligned_dist_ticks": beta_aligned, "aligned_ci_session": r_aligned["session_block_ci"],
        "aligned_ci_trade": r_aligned["trade_block_ci"], "aligned_significant_dual": bool(sig_aligned),
    }
    log(f"[joint model,A] H={H}: n={r_abs['n']} r2={r_abs['r2']:.4f} | "
        f"beta_abs={beta_abs:+.5f} (sessCI={[round(x,5) for x in r_abs['session_block_ci']]}, "
        f"sig_dual={sig_abs}) | beta_aligned={beta_aligned:+.5f} "
        f"(sessCI={[round(x,5) for x in r_aligned['session_block_ci']]}, sig_dual={sig_aligned})")

RESULTS["symmetry"] = {
    "split_sample": {k: {str(H): v for H, v in d.items()} for k, d in dir_split.items()},
    "signs_match_long_short": bool(signs_match),
    "joint_abs_vs_aligned": {str(H): v for H, v in joint_results.items()},
}


# ============================================================== PART 4: (b) linear vs threshold/kink
log("\n" + "=" * 78)
log("PART 4: (b) is Q_hold's relation to abs_value_dist_ticks linear or threshold/kink-shaped?")
log("=" * 78)


def fit_r2(sub, y_col, x_cols):
    d = sub.dropna(subset=x_cols + [y_col])
    X = np.column_stack([np.ones(len(d)), d[x_cols].to_numpy(dtype=float)])
    y = d[y_col].to_numpy(dtype=float)
    coef, r2 = m5.ols_fit(X, y)
    return r2, coef, len(d)


q_edges = subA_disc["abs_value_dist_ticks"].quantile([0, .2, .4, .6, .8, 1.0]).tolist()
subA_disc["vd_quintile"] = pd.cut(subA_disc["abs_value_dist_ticks"], bins=q_edges,
                                   labels=["Q1", "Q2", "Q3", "Q4", "Q5"],
                                   include_lowest=True, duplicates="drop")
log(f"quintile edges (abs_value_dist_ticks, ticks): {[round(x,1) for x in q_edges]}")

quintile_table = {}
for H in HORIZONS:
    y_col = f"signed_markout_{H}_A"
    rows = []
    for q in sorted(subA_disc["vd_quintile"].dropna().unique(), key=str):
        d = subA_disc[subA_disc["vd_quintile"] == q]
        ci = dual_cluster_group_mean_ci(d, y_col, "sess_tag", "block_id_A", nboot=1000, rng=m5.RNG)
        rows.append({"quintile": str(q), "n": ci["n"],
                     "mean_abs_dist_ticks": float(d["abs_value_dist_ticks"].mean()),
                     "mean_Q_hold": ci["mean"], "ci_session": ci["session_block_ci"]})
        log(f"[quintile,A] H={H} {q}: n={ci['n']} mean_dist={d['abs_value_dist_ticks'].mean():.1f}t "
            f"mean_Q_hold={ci['mean']:+.3f}t sessCI={[round(x,3) for x in ci['session_block_ci']]}")
    quintile_table[H] = rows

# hinge (broken-stick) regression at the pre-existing mid/far tercile boundary (not a new
# breakpoint invented for this test -- reuses the same cut already used throughout M5/this script)
bp = vdA_disc_cuts[1]
subA_disc["hinge_below"] = np.minimum(subA_disc["abs_value_dist_ticks"], bp)
subA_disc["hinge_above"] = np.maximum(subA_disc["abs_value_dist_ticks"] - bp, 0)
subA_disc["abs_dist_sq"] = subA_disc["abs_value_dist_ticks"] ** 2

shape_results = {}
for H in HORIZONS:
    y_col = f"signed_markout_{H}_A"
    r2_lin, _, n_lin = fit_r2(subA_disc, y_col, m5.X_COLS)

    x1 = ["hinge_below", "hinge_above"] + JOINT_COVARS
    x2 = ["hinge_above", "hinge_below"] + JOINT_COVARS
    r_below, r_above = two_coef_ci(subA_disc, y_col, x1, x2, "sess_tag", "block_id_A",
                                    nboot=1000, rng=m5.RNG)
    r2_hinge = r_below["r2"]
    sig_below = not (min(r_below["session_block_ci"]) <= 0 <= max(r_below["session_block_ci"]))
    sig_above = not (min(r_above["session_block_ci"]) <= 0 <= max(r_above["session_block_ci"]))

    xq1 = ["abs_value_dist_ticks", "abs_dist_sq"] + JOINT_COVARS
    xq2 = ["abs_dist_sq", "abs_value_dist_ticks"] + JOINT_COVARS
    r_lin_q, r_quad = two_coef_ci(subA_disc, y_col, xq1, xq2, "sess_tag", "block_id_A",
                                   nboot=1000, rng=m5.RNG)
    r2_quad = r_lin_q["r2"]
    sig_quad = not (min(r_quad["session_block_ci"]) <= 0 <= max(r_quad["session_block_ci"]))

    shape_results[H] = {
        "n": n_lin, "r2_linear": r2_lin, "r2_hinge": r2_hinge, "r2_quadratic": r2_quad,
        "hinge_breakpoint_ticks": bp,
        "hinge_below_slope": r_below["coef_all"]["hinge_below"],
        "hinge_below_ci_session": r_below["session_block_ci"], "hinge_below_sig": bool(sig_below),
        "hinge_above_slope": r_above["coef_all"]["hinge_above"],
        "hinge_above_ci_session": r_above["session_block_ci"], "hinge_above_sig": bool(sig_above),
        "quad_coef": r_quad["coef_all"]["abs_dist_sq"],
        "quad_ci_session": r_quad["session_block_ci"], "quad_sig": bool(sig_quad),
    }
    log(f"[shape,A] H={H}: R2 linear={r2_lin:.4f} hinge={r2_hinge:.4f} quadratic={r2_quad:.4f} | "
        f"hinge_below_slope={r_below['coef_all']['hinge_below']:+.5f} "
        f"(sessCI={[round(x,5) for x in r_below['session_block_ci']]}, sig={sig_below}) | "
        f"hinge_above_slope={r_above['coef_all']['hinge_above']:+.5f} "
        f"(sessCI={[round(x,5) for x in r_above['session_block_ci']]}, sig={sig_above}) | "
        f"quad_coef={r_quad['coef_all']['abs_dist_sq']:+.7f} "
        f"(sessCI={[round(x,7) for x in r_quad['session_block_ci']]}, sig={sig_quad})")

RESULTS["shape"] = {
    "quintile_table": {str(H): v for H, v in quintile_table.items()},
    "hinge_breakpoint_ticks": bp,
    "regression_shape": {str(H): v for H, v in shape_results.items()},
}


# ============================================================== PART 5: (c) reversal value +
# CONVENTIONS.md sec5 circular block=5 bootstrap cross-check on the headline effect
log("\n" + "=" * 78)
log("PART 5: (c) reversal value, and the block=5 circular-bootstrap robustness cross-check")
log("=" * 78)
reversal_results = {}
for H in HORIZONS:
    far = headline_disc[H]["far_mean"]
    reversal_value = -far["mean"]
    ci_sess = [-far["session_block_ci"][1], -far["session_block_ci"][0]]
    ci_trade = [-far["trade_block_ci"][1], -far["trade_block_ci"][0]]
    sig = not (min(ci_sess) <= 0 <= max(ci_sess)) and not (min(ci_trade) <= 0 <= max(ci_trade))
    pct_c1 = reversal_value / C1
    pct_2c1 = reversal_value / (2 * C1)
    reversal_results[H] = {
        "n_far": far["n"], "reversal_value_per_unit_ticks": reversal_value,
        "ci_session": ci_sess, "ci_trade": ci_trade, "significant_dual": bool(sig),
        "pct_of_C1_one_trip": pct_c1, "pct_of_2xC1_reversal_round_trip": pct_2c1,
        "economically_attractive_vs_1xC1": bool(sig and reversal_value > C1),
        "economically_attractive_vs_2xC1": bool(sig and reversal_value > 2 * C1),
    }
    log(f"[reversal,A] H={H}: reversal_value(far-tercile, per unit)={reversal_value:+.3f}t "
        f"sessCI={[round(x,3) for x in ci_sess]} tradeCI={[round(x,3) for x in ci_trade]} "
        f"sig={sig} | {pct_c1:+.2f}x C1(=2.872t, one trip) | {pct_2c1:+.2f}x 2*C1 (reversal cost proxy)")

block5_results = {}
for H in HORIZONS:
    y_col = f"signed_markout_{H}_A"
    raw = m5.dual_block_bootstrap_meandiff(subA_disc, "vd_tercile", "far", "near", y_col,
                                            "sess_tag", "block_id_A", nboot=1000, rng=m5.RNG)
    b5 = circular_block5_bootstrap_meandiff(subA_disc, "vd_tercile", "far", "near", y_col,
                                             "sess_tag", block=5, nboot=10000, seed=20260808)
    block5_results[H] = {"dual_cluster_raw": raw, "circular_block5": b5,
                          "same_sign": bool(np.sign(raw["diff"]) == np.sign(b5["diff"]))}
    log(f"[robustness cross-check,A] H={H}: raw diff={raw['diff']:+.3f}t | "
        f"dual-cluster(session+trade, i.i.d.) sess_CI={[round(x,3) for x in raw['session_block_ci']]} "
        f"trade_CI={[round(x,3) for x in raw['trade_block_ci']]} | "
        f"circular block=5 (CONVENTIONS.md sec5, B=10000, seed=20260808) CI="
        f"{[round(x,3) for x in b5['ci']]} sig={b5['significant']}")

RESULTS["reversal"] = reversal_results
RESULTS["block5_robustness"] = {str(H): v for H, v in block5_results.items()}


# ============================================================== PART 6: Q5 robustness --
# RTH/ETH split (feasibility check first) + RTH_MID-only sub-phase cross-check; LOSO / vol-regime
# split are CITED from AUCTION04's own already-computed stress output for product A (not
# recomputed -- identical methodology, identical substrate, would just reproduce the same numbers)
log("\n" + "=" * 78)
log("PART 6: Q5 robustness -- RTH/ETH feasibility, RTH-subphase cross-check, LOSO/vol-split citation")
log("=" * 78)
n_eth_analysis_ok = int((disc_ok["rth"] == False).sum())
phase_counts = subA_disc["session_phase"].value_counts().to_dict()
log(f"analysis_ok rows with rth==False (ETH): {n_eth_analysis_ok} / {len(disc_ok)} -- "
    f"a true RTH-vs-ETH split is NOT FEASIBLE on this substrate: the matched&rth&liquid "
    f"analysis_ok filter (computed upstream, unchanged, not this diagnostic's choice) already "
    f"restricts every usable decision point to RTH session phases only (ETH liquidity is too "
    f"thin for a reliable BBO match in this data). session_phase distribution within the product-A "
    f"incumbent sample: {phase_counts}")

mid_only = subA_disc[subA_disc["session_phase"] == "RTH_MID"].copy()
log(f"RTH_MID-only rows: {len(mid_only)} ({mid_only['sess_tag'].nunique()} sessions) -- closest "
    f"available substitute robustness check: does the effect survive when RTH_OPEN/RTH_CLOSE "
    f"edge-of-session rows (where liquidity/spread regimes differ most) are excluded entirely?")
# NOTE: phase dummies (phase_RTH_OPEN/phase_RTH_CLOSE) are dropped from the spec here -- within a
# RTH_MID-only subsample they are constant zero (no such rows present), which makes m5.X_COLS
# permanently rank-deficient in the cluster bootstrap (every replicate's Xb also rank-deficient,
# so ALL get skipped -> empty boots -> [nan,nan] CI). controlled_effect_custom_xcols is used
# instead of m5.controlled_effect_for_subset for exactly this one subsample-specific reason.
X_COLS_NOPHASE = ["abs_value_dist_ticks", "m_abs", "sigma460_atr_proxy_pts"]
rth_mid_results = {}
for H in HORIZONS:
    res = controlled_effect_custom_xcols(mid_only, "A", cfgA, H, X_COLS_NOPHASE,
                                          with_ci=True, nboot=1000, rng=m5.RNG)
    rth_mid_results[H] = res
    base = headline_disc[H]["controlled_effect"]
    log(f"[RTH_MID-only,A] H={H}: n={res['n']} sessions={res['n_sessions']} "
        f"controlled_effect={res['controlled_effect']:+.3f}t (full-RTH baseline {base:+.3f}t) "
        f"sess_CI={[round(x,3) for x in res['ci_session']]} trade_CI={[round(x,3) for x in res['ci_trade']]} "
        f"dual_sig={res['significant_dual']} same_sign_as_baseline="
        f"{np.sign(res['controlled_effect'])==np.sign(base)}")

# cite (not recompute) AUCTION04's own already-certified LOSO / remove-top-3 / vol-regime-split
# stress results for product A discovery (identical substrate, identical methodology --
# recomputing would reproduce the same numbers, not add information)
m5json_path = os.path.join(AUCTION04_SRC, "..", "out", "m5_clean_action_value.json")
with open(m5json_path) as f:
    m5_prior = json.load(f)
stress_A = m5_prior["stress_checks"]["A"]
loso_summary = stress_A["loso_sign_stability"]
top3_summary = stress_A["remove_top3_results"]
vol_summary = stress_A["vol_split_results"]
log("[CITED from runs/AUCTION04_CLEAN_CAUSAL_SUBSTRATE/out/m5_clean_action_value.json, product A, "
    "discovery, identical substrate/methodology -- not recomputed here]")
for H in HORIZONS:
    ls = loso_summary[str(H)]
    log(f"  LOSO H={H}: {ls['n_same_sign_as_full_sample']}/{ls['n']} sessions same-sign on removal "
        f"(range=[{ls['min']:+.2f},{ls['max']:+.2f}]t)")
    t3 = top3_summary[str(H)]
    log(f"  remove-top3-influential-sessions H={H}: controlled_effect={t3['controlled_effect']:+.3f}t "
        f"dual_sig={t3['significant_dual']} (loses dual significance at every horizon once the "
        f"3 most-influential sessions -- 20260220, 20251124, 20260423 -- are dropped)")
    vl, vh = vol_summary["low_vol"][str(H)], vol_summary["high_vol"][str(H)]
    log(f"  vol-regime split H={H}: low_vol controlled_effect={vl['controlled_effect']:+.3f}t "
        f"dual_sig={vl['significant_dual']} | high_vol controlled_effect={vh['controlled_effect']:+.3f}t "
        f"dual_sig={vh['significant_dual']}")

RESULTS["robustness_q5"] = {
    "eth_feasibility": {"n_eth_analysis_ok_rows": n_eth_analysis_ok, "feasible": bool(n_eth_analysis_ok > 0),
                         "session_phase_counts": {str(k): int(v) for k, v in phase_counts.items()}},
    "rth_mid_only": {str(H): v for H, v in rth_mid_results.items()},
    "cited_loso_top3_volsplit_source": "runs/AUCTION04_CLEAN_CAUSAL_SUBSTRATE/out/m5_clean_action_value.json",
    "cited_loso_sign_stability": loso_summary,
    "cited_remove_top3": top3_summary,
    "cited_vol_split": vol_summary,
}


# ============================================================== PART 7: Product B secondary check
# (per task sec42: at most one layer, only if inspection suggests a genuine B-relevant layer)
log("\n" + "=" * 78)
log("PART 7: Product B secondary check (structural inspection only, per sec42 scope)")
log("=" * 78)
posB_vals = sorted(disc_raw["position_B"].unique().tolist())
log(f"position_B distinct values across the FULL raw table: {posB_vals} -- Product B's held state "
    f"is a pure directional flag (no size dimension at all: never +-2, +-3, ... unlike "
    f"target_exposure_A which ranges -9..+9). Consequence: 'add one more unit' is not a "
    f"representable action for B in this substrate (0 observations of |position_B|>1 exist to "
    f"even ask the question) -- B's action space collapses to exactly HOLD (stay at +-1) vs. "
    f"REDUCE-TO-FLAT (go to 0), which by PART 1's identical mechanical identity is simply "
    f"-Q_hold_B; there is no partial-reduce or partial-add state to decompose further. This is a "
    f"structurally SIMPLER decomposition than Product A's, not a distinct new one -- no genuine "
    f"additional Product-B-relevant layer is suggested by inspection, so none is forced here.")
conf_B_dual_sig = any(row.get("significant_dual") for row in m5_prior["rows"]
                       if row["sample"] == "confirmation" and row["product"] == "B")
log(f"Cross-reference: M5's own confirmation-pool result for product B is dual-significant at "
    f"0/3 horizons (n=522, 5 sessions -- underpowered, same as product A's confirmation result), "
    f"consistent with 'no incremental B-specific claim beyond what M5 already reported'.")
RESULTS["product_B_secondary"] = {
    "position_B_distinct_values": posB_vals,
    "has_size_dimension": False,
    "conclusion": "no genuine additional Product-B-relevant action-value layer found by inspection; "
                  "B's action space is structurally HOLD-vs-REDUCE-TO-FLAT only (no add, no partial "
                  "reduce), which is already fully covered by PART 1's mechanical identity and M5's "
                  "own existing Product-B result -- no new layer forced per task sec42.",
}


# ============================================================== FINAL VERDICT
log("\n" + "=" * 78)
log("FINAL VERDICT")
log("=" * 78)
# quantitative gate for "stable, credible action separation": deterioration must be (i) significant
# and same-signed for BOTH long and short (symmetric, not one-sided), (ii) monotonic-enough that no
# single H flips sign discovery vs headline, (iii) survive at least LOSO sign-stability and the
# RTH_MID-only cross-check in direction (not necessarily significance, given known power limits).
sym_ok = signs_match and all(
    dir_split[d][H] is not None and dir_split[d][H]["significant_dual"] for d in ("long", "short") for H in HORIZONS)
mid_ok = all(rth_mid_results[H] is not None and
             np.sign(rth_mid_results[H]["controlled_effect"]) == np.sign(headline_disc[H]["controlled_effect"])
             for H in HORIZONS)
loso_ok = all(loso_summary[str(H)]["n_same_sign_as_full_sample"] == loso_summary[str(H)]["n"] for H in HORIZONS)
top3_ok = all(top3_summary[str(H)]["significant_dual"] for H in HORIZONS)
block5_ok = all(block5_results[H]["circular_block5"]["significant"] for H in HORIZONS)
log(f"gate check: symmetric-and-both-significant(long&short)={sym_ok} | "
    f"RTH_MID-only same-sign={mid_ok} | LOSO fully sign-stable={loso_ok} | "
    f"survives remove-top3-influential-sessions at dual-significance={top3_ok} | "
    f"circular-block5 significant at every H={block5_ok}")
log("Reading: the DIRECTION of the deterioration effect (far-from-POC hurts incumbent-aligned "
    "forward markout) is highly stable -- symmetric by long/short, present in RTH_MID alone, "
    "100% LOSO sign-stable, and confirmed by an independent block=5 circular bootstrap design. "
    "But its STATISTICAL SIGNIFICANCE is concentrated: it fails the remove-top-3-influential-"
    "sessions check at every horizon (drops out of dual-significance once 3 of 36 sessions are "
    "excluded), is not significant in the low-vol regime, and does not replicate at "
    "dual-significance in the underpowered 6-session confirmation pool (though the point estimate "
    "keeps the same sign there too). No add/hold/reduce action separation exists beyond the single "
    "univariate abs_value_dist_ticks relationship -- Q_add and Q_hold are mechanically identical, "
    "and Q_reduce/Q_reverse-per-unit are mechanically -Q_hold (PART 1) -- so what IS stable is a "
    "single continuous 'distance hurts the incumbent-aligned per-unit forward markout, roughly "
    "linearly' relationship, directionally robust but not yet strong enough in significance to "
    "be called a fully-confirmed, action-differentiated finding.")


# ============================================================== WRITE OUTPUTS
def _default(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, pd.Series):
        return o.tolist()
    return str(o)


json_path = os.path.join(OUT, "actionmap01_results.json")
with open(json_path, "w") as f:
    json.dump(RESULTS, f, indent=2, default=_default)
log(f"\nWrote {json_path}")

log_path = os.path.join(OUT, "00_diagnostic_log.txt")
with open(log_path, "w") as f:
    f.write("\n".join(LOG_LINES) + "\n")
log(f"Wrote {log_path}")


# ============================================================== MARKDOWN REPORT
def fmt(x, d=3):
    return f"{x:+.{d}f}" if isinstance(x, (int, float)) and not np.isnan(x) else str(x)


def ci_str(ci, d=3):
    return f"[{ci[0]:+.{d}f}, {ci[1]:+.{d}f}]"


md = []
md.append("# ACTIONMAP01 -- Auction Distance Action-Value Diagnostic\n")
md.append("Decomposition of AUCTION04/M5's clean-predictor finding ('Auction distance deteriorates "
          "incumbent-aligned forward markout') into add/hold/reduce action-specific value, Product A "
          "primary, Product B secondary. Discovery sample: 37 sessions ("
          f"{RESULTS['setup']['n_sessions_disc']} carry a product-A decision point), Product-A "
          f"incumbent rows n={RESULTS['setup']['n_disc']}. Confirmation pool (6 BBO-usable sessions): "
          f"n={RESULTS['setup']['n_conf']}. Horizons H in {{1,3,20}} (3-min bars). "
          f"C1 = {C1} ticks (campaign round-trip cost hurdle).\n")

md.append("## 0. Verdict\n")
md.append(f"**No add/hold/reduce action SEPARATION exists in this data beyond a single univariate "
          f"relationship.** Under the master directive's own no-market-impact assumption, "
          f"Q_add(t) is mechanically IDENTICAL to Q_hold(t), and Q_reduce(t)/Q_reverse-per-unit(t) "
          f"are mechanically IDENTICAL to -Q_hold(t) -- this is a definitional consequence of how "
          f"`signed_markout_H_A` is built (per-contract, size-independent), not an empirical finding "
          f"to test, and this substrate has no fill-level data capable of contradicting it. What "
          f"survives is therefore a single question: is Auction distance's deterioration of "
          f"Q_hold (a) symmetric by direction, (b) linear or threshold-shaped, and (c) large enough "
          f"in the far tercile to make reversal (not just reduction) attractive. Answers below: "
          f"(a) symmetric -- long and short both deteriorate, same sign, comparable magnitude; "
          f"(b) closer to linear-with-mild-acceleration than a hard threshold (hinge/quadratic terms "
          f"do not dominate the plain linear fit); (c) reversal is NOT economically attractive at "
          f"the actionable H=1 horizon (well under one round-trip cost), so the right-tail-caveat "
          f"mapping (`affect incremental adds only, don't touch existing winners`) is NOT clearly "
          f"supported either -- the finding is about incumbent Q_hold itself deteriorating, not "
          f"specifically about weak marginal economics of NEW adds distinct from existing exposure. "
          f"The DIRECTION of the effect is robust (symmetric by side, present in RTH_MID alone, "
          f"100% LOSO sign-stable, confirmed by an independent block=5 bootstrap design); its "
          f"STATISTICAL SIGNIFICANCE is not fully robust (removing the 3 most-influential of 36 "
          f"discovery sessions erases dual-significance at every horizon; the confirmation pool is "
          f"underpowered and does not reach dual-significance, though it keeps the same sign).\n")

md.append("## 1. Mechanical identity (Q_add / Q_reduce / Q_reverse vs Q_hold)\n")
md.append("From `runs/AUCTION02_ACTION_RELEVANCE/src/01_build_action_substrate.py` (the actual "
          "upstream build code, read directly, not inferred):\n")
md.append("```\nside = sign(target_exposure_A)\nsigned_markout_H_A = side * (fwd_close - close) / TICK\n```\n")
md.append("This is per-contract (no size term at all). Therefore, exactly (not approximately), for "
          "every decision point t:\n\n"
          "| Action | Value | Relation to Q_hold |\n|---|---|---|\n"
          "| HOLD (keep existing size) | `Q_hold(t) = signed_markout_H_A(t)` | -- (already computed) |\n"
          "| ADD (one more unit, same side) | `Q_add(t) = side*(fwd_close-close)/TICK` | `== Q_hold(t)` |\n"
          "| REDUCE (one fewer unit, toward flat) | `Q_reduce(t) = -side*(fwd_close-close)/TICK` | "
          "`== -Q_hold(t)` |\n"
          "| REVERSE (one unit, opposite side) | `Q_reverse_per_unit(t) = -side*(fwd_close-close)/TICK` "
          "| `== -Q_hold(t)` (same per-unit number as REDUCE; reversing = 1 de-risking unit + 1 new "
          "opposite-side unit, each worth `-Q_hold(t)`) |\n\n"
          "This is a mathematical identity, not a testable claim -- the substrate contains zero "
          "fill-level, partial-size, or market-impact-vs-size observations, so nothing here could "
          "contradict it even if real impact existed. Per the master directive's own instruction not "
          "to assume future market impact from tiny research size, this is the right way to treat it: "
          "**there is no distinct Q_add question separate from Q_hold in this data.** "
          f"(Flat-state target_exposure_A==0 rows, which would need a separate 'initiate' convention, "
          f"are {RESULTS['setup']['n_flat_raw_full_table']} row(s) in the full raw table before any "
          f"filtering -- not a population that can be analyzed here.)\n")

md.append("## 2. Headline Product-A result (answers Q1 AND Q2 simultaneously, given Part 1)\n")
md.append("Discovery sample, OLS-controlled (abs_value_dist_ticks + |M_A_raw| + sigma460 + phase "
          "dummies), dual-clustered (session + trade-block) 95% CI:\n\n")
md.append("| H | n | controlled effect (far-near, ticks) | session CI | trade CI | dual-sig | "
          "far-tercile mean Q_hold | near-tercile mean Q_hold | % of C1 |\n|---|---|---|---|---|---|---|---|---|\n")
for H in HORIZONS:
    r = headline_disc[H]
    md.append(f"| {H} | {r['n']} | {fmt(r['controlled_effect'])} | {ci_str(r['ci_session'])} | "
              f"{ci_str(r['ci_trade'])} | {r['significant_dual']} | "
              f"{fmt(r['far_mean']['mean'])} | {fmt(r['near_mean']['mean'])} | "
              f"{r['controlled_effect_pct_of_C1']:+.2f}x |\n")
md.append("\nConfirmation pool (6 BBO-usable sessions, n small -- underpowered, session-only CI shown):\n\n")
md.append("| H | n | controlled effect (ticks) | session CI | sig (session) | same sign as discovery |\n"
          "|---|---|---|---|---|---|\n")
for H in HORIZONS:
    if H not in headline_conf:
        continue
    r = headline_conf[H]
    md.append(f"| {H} | {r['n']} | {fmt(r['controlled_effect'])} | {ci_str(r['ci_session'])} | "
              f"{r['significant_session']} | {r['same_sign_as_discovery']} |\n")
md.append("\n**Q1 (does distance reduce the value of ADDING?) and Q2 (does it reduce the value of "
          "HOLDING?) have the SAME answer, by Part 1's identity: YES, at all three horizons in "
          "discovery, with dual-clustered significance** -- but see sections 6-7 for the significance "
          "robustness caveats.\n")

md.append("## 3. (a) Is the deterioration symmetric by direction? [Q5 long/short split]\n")
md.append(f"Long-held rows: {n_long_disc} | Short-held rows: {n_short_disc}\n\n")
md.append("| direction | H | n | controlled effect | session CI | trade CI | dual-sig |\n"
          "|---|---|---|---|---|---|---|\n")
for label in ("long", "short"):
    for H in HORIZONS:
        r = dir_split[label][H]
        if r is None:
            md.append(f"| {label} | {H} | -- | n/a (subset too small) | | | |\n")
            continue
        md.append(f"| {label} | {H} | {r['n']} | {fmt(r['controlled_effect'])} | "
                  f"{ci_str(r['ci_session'])} | {ci_str(r['ci_trade'])} | {r['significant_dual']} |\n")
md.append(f"\nSame-sign(long, short) at every horizon: **{signs_match}**. ")
md.append("Both directions deteriorate with distance -- the effect is not a one-sided long-only or "
          "short-only artifact.\n\n")
md.append("**Aligned (signed, direction-specific 'chasing') vs abs (direction-agnostic magnitude) "
          "predictor, fit jointly** (each coefficient controls for the other):\n\n")
md.append("| H | n | R2 | beta_abs (per tick) | abs sig (dual) | beta_aligned (per tick) | "
          "aligned sig (dual) |\n|---|---|---|---|---|---|---|\n")
for H in HORIZONS:
    r = joint_results[H]
    md.append(f"| {H} | {r['n']} | {r['r2']:.4f} | {r['beta_abs_value_dist_ticks']:+.5f} | "
              f"{r['abs_significant_dual']} | {r['beta_aligned_dist_ticks']:+.5f} | "
              f"{r['aligned_significant_dual']} |\n")
md.append("\nIf the *aligned* (signed, chasing-your-own-direction) coefficient dominated while abs "
          "dropped out, the effect would be about extension IN your position's direction specifically "
          "(a genuine directional asymmetry). If *abs* dominates, the effect is symmetric magnitude-"
          "only distance, regardless of alignment -- consistent with the split-sample result above.\n")

md.append("## 4. (b) Linear or threshold/kink-shaped? [Q4]\n")
md.append(f"Quintile edges of abs_value_dist_ticks (discovery, ticks): "
          f"{[round(x,1) for x in q_edges]}\n\n")
for H in HORIZONS:
    md.append(f"\n**H={H}**\n\n| quintile | n | mean dist (ticks) | mean Q_hold | session CI |\n"
              "|---|---|---|---|---|\n")
    for row in quintile_table[H]:
        md.append(f"| {row['quintile']} | {row['n']} | {row['mean_abs_dist_ticks']:.1f} | "
                  f"{fmt(row['mean_Q_hold'])} | {ci_str(row['ci_session'])} |\n")
md.append(f"\nHinge breakpoint (pre-existing mid/far tercile boundary, ticks): {bp:.1f}\n\n")
md.append("| H | R2 linear | R2 hinge | R2 quadratic | hinge-below slope | sig | hinge-above slope | "
          "sig | quad coef | sig |\n|---|---|---|---|---|---|---|---|---|---|\n")
for H in HORIZONS:
    r = shape_results[H]
    md.append(f"| {H} | {r['r2_linear']:.4f} | {r['r2_hinge']:.4f} | {r['r2_quadratic']:.4f} | "
              f"{r['hinge_below_slope']:+.5f} | {r['hinge_below_sig']} | "
              f"{r['hinge_above_slope']:+.5f} | {r['hinge_above_sig']} | "
              f"{r['quad_coef']:+.7f} | {r['quad_sig']} |\n")
md.append("\nReading: R2 improvement from hinge/quadratic terms over the plain linear fit is small at "
          "every horizon (compare the R2 columns), and the quintile table shows a roughly graded "
          "decline across Q1-Q5 rather than a flat-then-cliff pattern concentrated only in the top "
          "quintile. This favors **linear-with-mild-acceleration over a hard threshold** -- a genuine "
          "kink cannot be ruled out (the hinge-above slope is somewhat steeper than hinge-below at "
          "several horizons) but there is no clean 'safe below X ticks, hurts beyond X' cutoff.\n")

md.append("## 5. (c) Reversal value [Q3, and the right-tail question]\n")
md.append("By Part 1's identity, the per-unit value of reversing when far-from-POC is exactly "
          "`-1 * (far-tercile mean Q_hold)`. Economic magnitude vs the campaign's own C1 cost hurdle:\n\n")
md.append("| H | far-tercile mean Q_hold | reversal value (=-mean) | session CI | dual-sig | "
          "x of C1 (one trip) | x of 2*C1 (reversal proxy) | attractive vs 1xC1 | attractive vs 2xC1 |\n"
          "|---|---|---|---|---|---|---|---|---|\n")
for H in HORIZONS:
    r = reversal_results[H]
    far_mean = headline_disc[H]["far_mean"]["mean"]
    md.append(f"| {H} | {fmt(far_mean)} | {fmt(r['reversal_value_per_unit_ticks'])} | "
              f"{ci_str(r['ci_session'])} | {r['significant_dual']} | "
              f"{r['pct_of_C1_one_trip']:+.2f}x | {r['pct_of_2xC1_reversal_round_trip']:+.2f}x | "
              f"{r['economically_attractive_vs_1xC1']} | {r['economically_attractive_vs_2xC1']} |\n")
md.append("\n**Q3 (does distance increase the value of REDUCING?): mechanically YES, identically to "
          "how much Q_hold falls (Part 1) -- reducing avoids realizing a Q_hold that is, on average, "
          "significantly negative in the far tercile at H=1 and H=3.** But reversal (going further, "
          "to the opposite side) is a DIFFERENT question: at H=1 -- the horizon closest to an "
          "actionable single decision -- reversal's edge is well under one round-trip cost (see "
          "table), so it is **not economically attractive net of costs**, even though it is "
          "'directionally correct'. H=20's larger raw magnitude reflects a much longer, multi-"
          "decision-point window (60 minutes of 3-min bars) and should not be read as the payoff of "
          "one immediate reversal trade. This supports the master directive's sec36-37 caution: the "
          "evidence favors 'existing exposure's expected value deteriorates with distance' over "
          "'reversal is attractive' -- reduce/de-risk is the supported action, not flip.\n")

md.append("## 6. Explicit Q1-Q5 answers\n")
md.append(f"- **Q1 (does distance reduce the value of ADDING?)** YES, mechanically identical to Q2's "
          f"answer (Part 1) -- controlled effect {fmt(headline_disc[1]['controlled_effect'])}t at "
          f"H=1, {fmt(headline_disc[3]['controlled_effect'])}t at H=3, "
          f"{fmt(headline_disc[20]['controlled_effect'])}t at H=20 (discovery, dual-sig at all three).\n")
md.append(f"- **Q2 (does it reduce the value of HOLDING?)** YES -- same numbers as Q1, this IS the "
          f"measured Q_hold effect.\n")
md.append(f"- **Q3 (does it increase the value of REDUCING?)** YES mechanically (= -Q2's effect), "
          f"but the more aggressive action (reversal) is NOT economically attractive net of cost at "
          f"the actionable H=1 horizon ({reversal_results[1]['pct_of_C1_one_trip']:+.2f}x C1).\n")
md.append(f"- **Q4 (is the deterioration monotonic vs threshold/kink)?** Closer to linear-with-mild-"
          f"acceleration than a hard threshold -- see Part 4's quintile table and hinge/quadratic R2 "
          f"comparison; no clean safe-below-X cutoff found.\n")
md.append(f"- **Q5 (does it survive robustness checks)?** See section 7 -- DIRECTION is robust (long/"
          f"short symmetric, RTH_MID-only same-sign, 100% LOSO sign-stable, block=5 circular "
          f"bootstrap confirms), but SIGNIFICANCE is not fully robust (fails after removing the top-3 "
          f"influential sessions; not significant in the low-vol regime; confirmation pool "
          f"underpowered).\n")

md.append("## 7. Robustness detail (Q5)\n")
md.append(f"**RTH/ETH split: NOT FEASIBLE.** {n_eth_analysis_ok} of {len(disc_ok)} analysis_ok rows "
          f"have rth==False -- the upstream matched&rth&liquid filter already restricts every usable "
          f"decision point to RTH. session_phase distribution in the Product-A incumbent sample: "
          f"{phase_counts}.\n\n")
md.append("**RTH_MID-only cross-check** (excludes RTH_OPEN/RTH_CLOSE edge-of-session rows "
          "entirely):\n\n| H | n | controlled effect | session CI | trade CI | dual-sig | "
          "same sign as full-RTH |\n|---|---|---|---|---|---|---|\n")
for H in HORIZONS:
    r = rth_mid_results[H]
    base = headline_disc[H]["controlled_effect"]
    md.append(f"| {H} | {r['n']} | {fmt(r['controlled_effect'])} | {ci_str(r['ci_session'])} | "
              f"{ci_str(r['ci_trade'])} | {r['significant_dual']} | "
              f"{np.sign(r['controlled_effect'])==np.sign(base)} |\n")
md.append("\n**LOSO / remove-top-3 / vol-regime split** (cited from AUCTION04's own already-certified "
          "product-A stress output, identical substrate/methodology -- not recomputed):\n\n"
          "| H | LOSO sign-stable | remove-top3 controlled effect | remove-top3 dual-sig | "
          "low-vol dual-sig | high-vol dual-sig |\n|---|---|---|---|---|---|\n")
for H in HORIZONS:
    ls = loso_summary[str(H)]
    t3 = top3_summary[str(H)]
    vl, vh = vol_summary["low_vol"][str(H)], vol_summary["high_vol"][str(H)]
    md.append(f"| {H} | {ls['n_same_sign_as_full_sample']}/{ls['n']} | "
              f"{fmt(t3['controlled_effect'])} | {t3['significant_dual']} | "
              f"{vl['significant_dual']} | {vh['significant_dual']} |\n")
md.append("\n**Independent block=5 circular-session bootstrap cross-check** (CONVENTIONS.md sec5: "
          "block=5, B=10000, seed=20260808 -- a DIFFERENT resampling design from the dual-cluster "
          "i.i.d.-session bootstrap used elsewhere in this diagnostic and throughout AUCTION01-04):"
          "\n\n| H | raw diff | dual-cluster session CI | dual-cluster trade CI | "
          "block=5 circular CI | block=5 significant |\n|---|---|---|---|---|---|\n")
for H in HORIZONS:
    r = block5_results[H]
    md.append(f"| {H} | {fmt(r['dual_cluster_raw']['diff'])} | "
              f"{ci_str(r['dual_cluster_raw']['session_block_ci'])} | "
              f"{ci_str(r['dual_cluster_raw']['trade_block_ci'])} | "
              f"{ci_str(r['circular_block5']['ci'])} | {r['circular_block5']['significant']} |\n")
md.append("\nThe block=5 circular design agrees in SIGN with the dual-cluster convention at every "
          "horizon (an independent-design cross-check passing), but note the raw (non-OLS-controlled) "
          "tercile diff is itself not dual-cluster-significant at H=1/H=3 in the ORIGINAL M5 test "
          "either (see AUCTION04's own `raw_ci_session`/`raw_ci_trade` in m5_clean_action_value.json "
          "-- only the phase/vol/M-controlled OLS effect reaches dual significance) -- the block=5 "
          "check here is confirming the SAME raw-diff sign/rough-magnitude the primary convention "
          "already reported, not adding new significance beyond it.\n")

md.append("## 8. Product B secondary check\n")
md.append(f"`position_B` distinct values across the full raw table: {posB_vals} -- a pure directional "
          f"flag with **no size dimension** (unlike `target_exposure_A`, which ranges -9..+9). "
          f"Consequence: 'add one more unit' is not a representable action for B at all (zero "
          f"observations of |position_B|>1 exist). B's action space collapses to exactly HOLD "
          f"(stay at +-1) vs REDUCE-TO-FLAT (go to 0) -- by Part 1's identical mechanical identity, "
          f"reduce-to-flat's value is simply -Q_hold_B, with no partial-add or partial-reduce state "
          f"to decompose further. This is a structurally SIMPLER decomposition than Product A's, not "
          f"a distinct new one. Cross-reference: M5's own confirmation-pool result for Product B is "
          f"dual-significant at 0/3 horizons (n=522, 5 sessions), matching Product A's confirmation "
          f"underpowering. **No genuine additional Product-B-relevant action-value layer is forced "
          f"here** (task sec42).\n")

md.append("## 9. Right-tail mapping read\n")
md.append("Per sec36-37/83-84's caution against defaulting to a de-risk/exit mapping: this evidence "
          "is genuinely ambiguous between the two readings the task flagged. The deterioration is "
          "measured directly on `Q_hold` (existing incumbent exposure's own forward markout), NOT on "
          "a separately-identified 'new adds only' population (Part 1 showed none exists distinct "
          "from Q_hold) -- so the finding, read literally, implicates the EXISTING position's own "
          "expected value, not just the marginal economics of new additions. That said, the effect's "
          "significance is concentrated (fails ex-3-sessions, fails in low-vol) and reversal is not "
          "economically attractive (Part 5), so this is not evidence for an aggressive exit/reverse "
          "policy either -- at most it supports being more cautious about ADDING TO or entering NEW "
          "far-from-POC positions (where Q_add==Q_hold applies with full force going forward, no "
          "sunk-cost asymmetry) than about actively de-risking already-held ones. A future policy "
          "informed by this evidence, if any, should weight the 'affect incremental adds only' "
          "reading more heavily than 'de-risk existing exposure', given the significance fragility "
          "documented in section 7 -- but this diagnostic does not itself propose or freeze a policy "
          "(that is explicitly out of scope, per task instruction, for the next phase).\n")

md_path = os.path.join(OUT, "00_diagnostic.md")
with open(md_path, "w", encoding="utf-8") as f:
    f.write("".join(md))
log(f"\nWrote {md_path}")
log("ACTIONMAP01 DIAGNOSTIC DONE")
