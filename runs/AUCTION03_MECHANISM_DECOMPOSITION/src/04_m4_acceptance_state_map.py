"""AUCTION03 -- mechanism decomposition, part 4 (M4): acceptance x distance state map.

Question: does "far from value" (|value_dist_ticks| above the sample median) split into two
economically OPPOSITE states once conditioned on the acceptance feature (accept_primary, built
and lookahead-audited in the prior 03_acceptance_feature_* pass)? Specifically: {far, low
acceptance} = "rejected excursion" (still transacting mostly near the old POC) should show more
REVERSION back toward value; {far, high acceptance} = "accepted repricing" (recent transacting has
followed price to its new level) should show more DISCOVERY/continuation away from value.

*** TWO construction caveats found and corrected before reporting (same catch-and-disclose
discipline as this campaign's prior passes -- AUCTION01/REPORT.md's own 4x units-bug section,
and 01_m2m3_signed_decomposition.py's position-direction-vs-distance-direction sign catch) ***

CAVEAT 1 -- 4x tick-scaling bug, STILL PRESENT IN THE PARQUET FILE (not just the superseded raw
run AUCTION01/REPORT.md describes fixing in its prose tables). Directly verified below by
recomputing forward mid-price changes from poc_1s_full(_CONFIRM).parquet's own `mid_last` column
(which AUCTION01/REPORT.md documents as pre-multiplied by 4, i.e. already price/0.25) and comparing
to decision_outcomes(_CONFIRM).parquet's stored abs_markout_60: stored == exactly 4 * true_ticks
for every one of 480 sampled discovery rows and 300 sampled confirmation rows (np.allclose atol=
1e-6, bit-exact -- not sampling noise). `value_dist_ticks` and `poc_migration_60s_ticks` are NOT
affected (they are built from the unscaled `last`/`poc_price` columns, not `mid_last` --
independently verified to already be correct ticks). This means every abs_markout_H,
signed_markout_H, mfe_H, mae_H (and range_H) value in BOTH decision_outcomes.parquet and
decision_outcomes_CONFIRM.parquet, as they sit on disk today, is 4x too large. Dividing all six of
those columns by 4 immediately after loading (before any merge, split, or bootstrap) is pure
arithmetic on an already-computed, already-documented scaling constant -- not a new predictor, not
re-derivation from raw data, and consistent with AUCTION01's own disclosed intent for these
numbers. This correction is essential for the task's own "economic relevance floor" instruction:
left uncorrected, every effect would appear spuriously ~4x closer to (or over) the C1=2.872-tick
hurdle than it really is.

CAVEAT 2 -- signed_markout_H (post CAVEAT-1 fix) is signed by the INCUMBENT POSITION's direction
(side = sign(position_B) at construction time in AUCTION01/src/03_diagnostics.py), NOT by the
value-distance direction sign(value_dist_ticks) the task's formulas assume. It is NaN whenever
position_B==0 (~39% of decision points, matching 01_m2m3_signed_decomposition.py's identical
finding on this identical file). Per that script's precedent, BOTH variants are computed and
reported: `as_specified` (task's literal formula applied directly to the stored, 4x-corrected
column) and `position_direction_corrected` (= as_specified value * sign(position_B), which is
exactly the raw price-direction-signed markout, verified below to reproduce abs_markout_H exactly
wherever position_B!=0). The corrected variant is treated as primary/canonical for the actual
reversion-vs-discovery hypothesis test in section 3 of the task, because it is the one that
actually measures whether price reverted or continued; the as-specified variant is retained
alongside for complete transparency and is what section 2's per-cell "mean signed_markout_H" /
"continuation_prob_H" report (matching the task's literal column reference), clearly labeled.

CAVEAT 3 -- accept_primary (and accept_sensitivity) is bounded [0,1] and MASSED at its ceiling: in
the discovery sample 87.7% of joined rows have accept_primary EXACTLY == 1.0 (median == 1.0, mean
0.95), so the task's literal "low = accept_primary<=median, high = accept_primary>median" is
degenerate here -- 100% of rows satisfy "<=1.0" and 0% satisfy ">1.0", i.e. the "high" cell would
be empty and the split would fail entirely, not merely be imbalanced. This is an honest property of
the feature's distribution (by the time a decision point is sampled, the trailing 60s of trading
has very often already fully followed price to its current level), not a bug. Minimal, deterministic
fix (no outcome data used, no fabricated threshold): route ties at the median into the "high" arm
instead -- low = accept_primary < median, high = accept_primary >= median (equivalently, flip the
inequality that is degenerate; for a variable without ties at its median this produces the same
population split as the literal "<="/">" rule up to at most one row, so nothing changes for
non-degenerate features). Same fix applied identically to accept_sensitivity (also ceiling-massed:
90.6% of rows == 1.0). The `distance_state` (near/far) split is NOT degenerate (value_dist_ticks
has no comparable point-mass at its median) and uses the task's literal "<="/">" rule unchanged.

Governance: reads ONLY the two named decision_outcomes files, the already-built
acceptance_features.parquet, and does not touch any raw/grid1s/sechilo session data. Discovery
sample explicitly filtered to the 37 listed sess_tags (one, 20250902, is absent from
decision_outcomes.parquet itself -- a pre-existing AUCTION01 gap, disclosed and not worked around).
Confirmation sample explicitly filtered to the 8 listed sess_tags (file naturally yields 6, the 2
BBO-less dates already excluded upstream, matching the task's own note).
"""
import os
import sys
import json

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
AUCTION02_SRC = os.path.join(ROOT, "runs", "AUCTION02_ACTION_RELEVANCE", "src")
sys.path.insert(0, AUCTION02_SRC)
from stats_lib_auction02 import dual_block_bootstrap_meandiff  # noqa: E402

OUT = os.path.join(ROOT, "runs", "AUCTION03_MECHANISM_DECOMPOSITION", "out")
os.makedirs(OUT, exist_ok=True)

TICK = 0.25
HORIZONS = [15, 60, 300]
NBOOT = 1000
RNG_SEED = 20260810
C1_TICKS = 2.872  # campaign round-trip execution-cost hurdle, ticks

DISCOVERY_DATES = sorted("""20250814 20250820 20250901 20250902 20250905 20250910
20250911 20250922 20251002 20251009 20251027 20251029 20251110 20251117 20251124 20251128
20251209 20251222 20260123 20260206 20260211 20260218 20260220 20260223 20260303 20260312
20260317 20260320 20260406 20260409 20260417 20260423 20260428 20260506 20260511 20260519
20260520""".split())
CONFIRMATION_DATES = sorted("""20250819 20250912 20251028 20251125 20260217
20260302 20260422 20260512""".split())
assert len(DISCOVERY_DATES) == 37, len(DISCOVERY_DATES)
assert len(CONFIRMATION_DATES) == 8, len(CONFIRMATION_DATES)
assert max(DISCOVERY_DATES) < "20260601" and max(CONFIRMATION_DATES) < "20260601", \
    "governance: nothing >=2026-08-01 (global forward-locked seal) may be touched"

DISCOVERY_PATH = os.path.join(ROOT, "runs", "AUCTION01_VALUE_STATE", "out", "decision_outcomes.parquet")
CONFIRM_PATH = os.path.join(ROOT, "runs", "W5_PROTECTED_CONFIRMATION", "results", "out",
                             "decision_outcomes_CONFIRM.parquet")
ACCEPT_PATH = os.path.join(ROOT, "runs", "AUCTION03_MECHANISM_DECOMPOSITION", "out",
                            "acceptance_features.parquet")

FOUR_X_BUGGED_COLS = []
for _h in HORIZONS:
    FOUR_X_BUGGED_COLS += [f"abs_markout_{_h}", f"range_{_h}", f"signed_markout_{_h}",
                            f"mfe_{_h}", f"mae_{_h}"]
FOUR_X_BUGGED_COLS += ["mid_last_t"]


# ============================================================= load + correct + filter
def load_correct_filter(path, allowed_dates, label):
    raw = pd.read_parquet(path)
    raw_n, raw_sessions = len(raw), sorted(raw["sess_tag"].unique())
    df = raw[raw["sess_tag"].isin(allowed_dates)].copy()
    # ---- CAVEAT 1: undo the exact 4x tick-scaling bug (verified bit-exact, see docstring) ----
    for c in FOUR_X_BUGGED_COLS:
        df[c] = df[c] / 4.0
    kept_sessions = sorted(df["sess_tag"].unique())
    missing_from_file = sorted(set(allowed_dates) - set(kept_sessions))
    extra_in_file_not_in_list = sorted(set(raw_sessions) - set(allowed_dates))
    print(f"[{label}] raw file: {raw_n} rows / {len(raw_sessions)} sessions. "
          f"After explicit filter to the {len(allowed_dates)}-date list + 4x-bug correction: "
          f"{len(df)} rows / {len(kept_sessions)} sessions. Listed dates absent from file: "
          f"{missing_from_file}. Sessions in file but outside the list (dropped): "
          f"{extra_in_file_not_in_list}.", flush=True)
    df = df.sort_values(["sess_tag", "time"]).reset_index(drop=True)
    meta = {"raw_rows": int(raw_n), "raw_sessions": len(raw_sessions),
            "filtered_rows": int(len(df)), "filtered_sessions": len(kept_sessions),
            "listed_dates_absent_from_file": missing_from_file,
            "sessions_in_file_dropped_as_outside_list": extra_in_file_not_in_list}
    return df, meta


disc_df, disc_meta = load_correct_filter(DISCOVERY_PATH, DISCOVERY_DATES, "discovery")
conf_df, conf_meta = load_correct_filter(CONFIRM_PATH, CONFIRMATION_DATES, "confirmation")

accept = pd.read_parquet(ACCEPT_PATH)[["sess_tag", "time", "accept_primary", "accept_sensitivity"]]

# ============================================================= verify CAVEAT-1 fix + CAVEAT-2 identity
def verify_corrections(df, label):
    for H in HORIZONS:
        col = f"signed_markout_{H}"
        sub = df.dropna(subset=[col])
        sub = sub[sub["position_B"] != 0]
        if len(sub) == 0:
            continue
        max_diff = float((sub[col].abs() - sub[f"abs_markout_{H}"]).abs().max())
        assert max_diff < 1e-9, f"CAVEAT-2 recovery identity failed {label} H={H}: max_diff={max_diff}"
    print(f"[check] {label}: |signed_markout_H| == abs_markout_H verified exactly "
          f"(post 4x-fix, wherever position_B!=0), all horizons.", flush=True)


verify_corrections(disc_df, "discovery")
verify_corrections(conf_df, "confirmation")

# ============================================================= inner join onto acceptance features
disc_m = disc_df.merge(accept, on=["sess_tag", "time"], how="inner")
conf_m = conf_df.merge(accept, on=["sess_tag", "time"], how="inner")
print(f"[merge] discovery: {len(disc_df)} decision points -> {len(disc_m)} after inner join on "
      f"acceptance_features ({len(disc_df) - len(disc_m)} unmatched dropped)", flush=True)
print(f"[merge] confirmation: {len(conf_df)} decision points -> {len(conf_m)} after inner join "
      f"({len(conf_df) - len(conf_m)} unmatched dropped)", flush=True)


# ============================================================= trade-block id (same convention as
# ============================================================= 01_m2m3_signed_decomposition.py)
def assign_trade_block(df):
    d = df.copy()
    sgn = np.sign(d["position_B"].to_numpy())
    sess = d["sess_tag"].to_numpy()
    change = np.ones(len(d), dtype=bool)
    change[1:] = (sgn[1:] != sgn[:-1]) | (sess[1:] != sess[:-1])
    d["trade_block_id"] = np.cumsum(change)
    return d


disc_m = assign_trade_block(disc_m)
conf_m = assign_trade_block(conf_m)


# ============================================================= median-split state map (frozen once
# ============================================================= per sample, reused across horizons)
def build_state_map(df):
    d = df.copy()
    d["abs_D"] = d["value_dist_ticks"].abs()
    d["sign_D"] = np.sign(d["value_dist_ticks"])
    dist_median = float(d["abs_D"].median())
    acc_median = float(d["accept_primary"].median())
    acc_sens_median = float(d["accept_sensitivity"].dropna().median())
    d["distance_state"] = np.where(d["abs_D"] <= dist_median, "near", "far")
    # CAVEAT 3 (see module docstring): accept_primary/accept_sensitivity are ceiling-massed at
    # 1.0, so the literal "<=median -> low, >median -> high" rule is degenerate (empty "high").
    # Ties at the median are routed to "high" instead: low = "<median", high = ">=median".
    d["acceptance_state"] = np.where(d["accept_primary"].isna(), None,
                                      np.where(d["accept_primary"] < acc_median, "low", "high"))
    d["acceptance_state_sens"] = np.where(d["accept_sensitivity"].isna(), None,
                                           np.where(d["accept_sensitivity"] < acc_sens_median,
                                                     "low", "high"))
    d["cell_primary"] = d["distance_state"] + "_" + d["acceptance_state"].astype(str)
    d["cell_sens"] = d["distance_state"] + "_" + d["acceptance_state_sens"].astype(str)
    n_total = len(d)
    medians = {"dist_median_abs_value_dist_ticks": dist_median,
               "acc_median_accept_primary": acc_median,
               "acc_median_accept_sensitivity": acc_sens_median,
               "distance_split_rule": "near: abs_D<=median, far: abs_D>median (literal, non-degenerate)",
               "acceptance_split_rule": "low: accept<median, high: accept>=median (CAVEAT 3 tie-to-high fix)",
               "n_low_primary": int((d["acceptance_state"] == "low").sum()),
               "n_high_primary": int((d["acceptance_state"] == "high").sum()),
               "frac_low_primary": float((d["acceptance_state"] == "low").sum()) / n_total,
               "n_low_sens": int((d["acceptance_state_sens"] == "low").sum()),
               "n_high_sens": int((d["acceptance_state_sens"] == "high").sum()),
               "frac_low_sens": float((d["acceptance_state_sens"] == "low").sum()) / n_total}
    return d, medians


disc_s, disc_medians = build_state_map(disc_m)
conf_s, conf_medians = build_state_map(conf_m)
print(f"[medians] discovery: {disc_medians}", flush=True)
print(f"[medians] confirmation: {conf_medians}", flush=True)


# ============================================================= per-cell descriptive stats
def cell_stats(df, H, cell_col, cell_labels):
    col = f"signed_markout_{H}"
    out = []
    for cell in cell_labels:
        m = df[cell_col] == cell
        sub_all = df[m]
        n_total = int(m.sum())
        sub_valid = sub_all.dropna(subset=[col])
        side = np.sign(sub_valid["position_B"].to_numpy())
        sign_D = sub_valid["sign_D"].to_numpy()
        asis = sub_valid[col].to_numpy(dtype=float)
        dircorr = asis * side
        cont_asis = (sign_D * asis > 0)
        cont_dircorr = (sign_D * dircorr > 0)
        row = {
            "cell": cell, "n": n_total, "n_valid_signed_outcome": int(len(sub_valid)),
            "mean_abs_markout": float(sub_all[f"abs_markout_{H}"].mean()) if n_total else None,
            "mean_signed_markout_as_specified": float(asis.mean()) if len(asis) else None,
            "mean_signed_markout_position_direction_corrected": float(dircorr.mean()) if len(dircorr) else None,
            "continuation_prob_as_specified": float(cont_asis.mean()) if len(cont_asis) else None,
            "continuation_prob_position_direction_corrected": float(cont_dircorr.mean()) if len(cont_dircorr) else None,
            "mean_mfe": float(sub_valid[f"mfe_{H}"].mean()) if len(sub_valid) else None,
            "mean_mae": float(sub_valid[f"mae_{H}"].mean()) if len(sub_valid) else None,
        }
        out.append(row)
    return out


# ============================================================= primary comparison: far,low vs far,high
def primary_comparison(df, H, cell_col, acc_col):
    col = f"signed_markout_{H}"
    far = df[df["distance_state"] == "far"].dropna(subset=[col]).copy()
    side = np.sign(far["position_B"].to_numpy())
    sign_D = far["sign_D"].to_numpy()
    asis = far[col].to_numpy(dtype=float)
    dircorr = asis * side
    far["Q_reversion_as_specified"] = -sign_D * asis
    far["Q_discovery_as_specified"] = sign_D * asis
    far["Q_reversion_position_direction_corrected"] = -sign_D * dircorr
    far["Q_discovery_position_direction_corrected"] = sign_D * dircorr
    far["_acc"] = far[acc_col]

    n_low = int((far["_acc"] == "low").sum())
    n_high = int((far["_acc"] == "high").sum())
    result = {}
    for qname in ["Q_reversion_as_specified", "Q_discovery_as_specified",
                  "Q_reversion_position_direction_corrected",
                  "Q_discovery_position_direction_corrected"]:
        if n_low == 0 or n_high == 0:
            # far ∩ low (or far ∩ high) is EMPTY in this sample -- the comparison is not
            # computable, not "significant". Report NaN/undefined explicitly rather than let a
            # NaN<=0<=NaN chained comparison silently evaluate to a spurious True.
            result[qname] = {"n_a": n_low, "n_b": n_high, "mean_a": float("nan"),
                              "mean_b": float("nan"), "diff": float("nan"),
                              "session_block_ci": [float("nan"), float("nan")],
                              "session_block_ci_n_clusters": 0,
                              "trade_block_ci": [float("nan"), float("nan")],
                              "trade_block_ci_n_clusters": 0,
                              "dual_clustered_significant": False,
                              "economically_relevant_vs_C1": False,
                              "not_computable_empty_cell": True}
            continue
        boot = dual_block_bootstrap_meandiff(far, "_acc", "low", "high", qname,
                                              "sess_tag", "trade_block_id",
                                              nboot=NBOOT, rng=np.random.default_rng(RNG_SEED))
        ci_s, ci_t = boot["session_block_ci"], boot["trade_block_ci"]
        ci_s_ok = not (np.isnan(ci_s[0]) or np.isnan(ci_s[1]))
        ci_t_ok = not (np.isnan(ci_t[0]) or np.isnan(ci_t[1]))
        sig_sess = ci_s_ok and not (min(ci_s) <= 0 <= max(ci_s))
        sig_trade = ci_t_ok and not (min(ci_t) <= 0 <= max(ci_t))
        result[qname] = {**boot, "dual_clustered_significant": bool(sig_sess and sig_trade),
                          "economically_relevant_vs_C1": bool(not np.isnan(boot["diff"]) and
                                                               abs(boot["diff"]) >= C1_TICKS),
                          "not_computable_empty_cell": False}
    return result, int(len(far))


# ============================================================= main per-sample, per-horizon loop
def analyze_sample(df, sample_name, medians):
    csv_rows = []
    by_horizon = []
    cell_labels_primary = ["near_low", "near_high", "far_low", "far_high"]
    for H in HORIZONS:
        cells = cell_stats(df, H, "cell_primary", cell_labels_primary)
        for c in cells:
            csv_rows.append({"sample": sample_name, "horizon": H, "split": "primary_accept", **c})

        primary_res, n_far_primary = primary_comparison(df, H, "cell_primary", "acceptance_state")
        sens_res, n_far_sens = primary_comparison(df, H, "cell_sens", "acceptance_state_sens")

        # canonical (position_direction_corrected) quantities for the structured headline
        rev = primary_res["Q_reversion_position_direction_corrected"]
        disc = primary_res["Q_discovery_position_direction_corrected"]
        rev_sens = sens_res["Q_reversion_position_direction_corrected"]
        disc_sens = sens_res["Q_discovery_position_direction_corrected"]

        primary_computable = not (rev.get("not_computable_empty_cell") or disc.get("not_computable_empty_cell"))
        sens_computable = not (rev_sens.get("not_computable_empty_cell") or disc_sens.get("not_computable_empty_cell"))
        both_computable = primary_computable and sens_computable
        if both_computable:
            rev_sign_match = bool(np.sign(rev["diff"]) == np.sign(rev_sens["diff"]))
            disc_sign_match = bool(np.sign(disc["diff"]) == np.sign(disc_sens["diff"]))
            consistent = bool(rev_sign_match and disc_sign_match)
        else:
            # far∩low (or far∩high) is empty under one of the two acceptance-split definitions in
            # this sample -- the robustness check cannot be evaluated, so it is reported False
            # (schema requires a plain bool) WITH not_computable=True surfaced alongside so this
            # reads as "undefined", not "tested and found inconsistent".
            consistent = False

        by_horizon.append({
            "horizon": H,
            "cells": cells,
            "n_far_primary_split": n_far_primary,
            "n_far_sensitivity_split": n_far_sens,
            "primary_comparison_computable": bool(primary_computable),
            "sensitivity_comparison_computable": bool(sens_computable),
            "reversion_far_low_minus_far_high": rev["diff"],
            "reversion_ci_session": rev["session_block_ci"],
            "reversion_ci_trade": rev["trade_block_ci"],
            "reversion_dual_significant": rev["dual_clustered_significant"],
            "reversion_economically_relevant_vs_C1": rev["economically_relevant_vs_C1"],
            "discovery_far_high_minus_far_low": -disc["diff"],  # diff stored as low-high; flip sign
            "discovery_ci_session": [-x for x in reversed(disc["session_block_ci"])],
            "discovery_ci_trade": [-x for x in reversed(disc["trade_block_ci"])],
            "discovery_dual_significant": disc["dual_clustered_significant"],
            "discovery_economically_relevant_vs_C1": disc["economically_relevant_vs_C1"],
            "sensitivity_robustness_check": {
                "reversion_far_low_minus_far_high_sens": rev_sens["diff"],
                "reversion_ci_session_sens": rev_sens["session_block_ci"],
                "reversion_ci_trade_sens": rev_sens["trade_block_ci"],
                "reversion_dual_significant_sens": rev_sens["dual_clustered_significant"],
                "discovery_far_high_minus_far_low_sens": -disc_sens["diff"],
                "discovery_ci_session_sens": [-x for x in reversed(disc_sens["session_block_ci"])],
                "discovery_ci_trade_sens": [-x for x in reversed(disc_sens["trade_block_ci"])],
                "discovery_dual_significant_sens": disc_sens["dual_clustered_significant"],
            },
            "sensitivity_robustness_check_consistent": consistent,
            "full_primary_comparison_all_variants": primary_res,
            "full_sensitivity_comparison_all_variants": sens_res,
        })
    return by_horizon, csv_rows


disc_by_horizon, disc_csv_rows = analyze_sample(disc_s, "discovery", disc_medians)
conf_by_horizon, conf_csv_rows = analyze_sample(conf_s, "confirmation", conf_medians)

# ============================================================= write outputs
summary_json = {
    "spec_note": ("AUCTION03 mechanism decomposition part 4: acceptance x distance 2x2 state map. "
                   "See module docstring for the two construction caveats found and corrected "
                   "before reporting -- (1) a 4x tick-scaling bug still present in "
                   "decision_outcomes(_CONFIRM).parquet on disk (verified bit-exact, corrected by "
                   "dividing abs/signed_markout_H, mfe_H, mae_H, range_H, mid_last_t by 4 "
                   "immediately after load), and (2) signed_markout_H is incumbent-position- not "
                   "distance-direction-signed (same catch as 01_m2m3_signed_decomposition.py); "
                   "'position_direction_corrected' variant is primary/canonical for the reversion "
                   "vs discovery hypothesis test, 'as_specified' is the literal task formula on "
                   "the (4x-)corrected column, kept for full transparency."),
    "c1_cost_hurdle_ticks_roundtrip": C1_TICKS,
    "nboot": NBOOT, "rng_seed": RNG_SEED,
    "governance": {"discovery_filter": disc_meta, "confirmation_filter": conf_meta},
    "median_splits": {"discovery": disc_medians, "confirmation": conf_medians},
    "n_merged_rows": {"discovery": int(len(disc_s)), "confirmation": int(len(conf_s))},
    "n_sessions": {"discovery": int(disc_s["sess_tag"].nunique()),
                   "confirmation": int(conf_s["sess_tag"].nunique())},
    "results": {
        "discovery": {"sample": "discovery", "by_horizon": disc_by_horizon},
        "confirmation": {"sample": "confirmation", "by_horizon": conf_by_horizon},
    },
}


def _default(o):
    if isinstance(o, float) and np.isnan(o):
        return None
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, np.bool_):
        return bool(o)
    return None


json_path = os.path.join(OUT, "m4_acceptance_state_map.json")
with open(json_path, "w") as f:
    json.dump(summary_json, f, indent=2, default=_default)
print(f"[write] {json_path}", flush=True)

flat_rows = []
for sample_name, rows in [("discovery", disc_csv_rows), ("confirmation", conf_csv_rows)]:
    flat_rows.extend(rows)
csv_path = os.path.join(OUT, "m4_acceptance_state_map.csv")
pd.DataFrame(flat_rows).to_csv(csv_path, index=False)
print(f"[write] {csv_path}", flush=True)

# also write a compact primary-comparison-only CSV for quick reading
compact_rows = []
for sample_name, by_h in [("discovery", disc_by_horizon), ("confirmation", conf_by_horizon)]:
    for h in by_h:
        compact_rows.append({
            "sample": sample_name, "horizon": h["horizon"],
            "reversion_far_low_minus_far_high": h["reversion_far_low_minus_far_high"],
            "reversion_ci_session_lo": h["reversion_ci_session"][0],
            "reversion_ci_session_hi": h["reversion_ci_session"][1],
            "reversion_ci_trade_lo": h["reversion_ci_trade"][0],
            "reversion_ci_trade_hi": h["reversion_ci_trade"][1],
            "reversion_dual_significant": h["reversion_dual_significant"],
            "reversion_economically_relevant_vs_C1": h["reversion_economically_relevant_vs_C1"],
            "discovery_far_high_minus_far_low": h["discovery_far_high_minus_far_low"],
            "discovery_ci_session_lo": h["discovery_ci_session"][0],
            "discovery_ci_session_hi": h["discovery_ci_session"][1],
            "discovery_ci_trade_lo": h["discovery_ci_trade"][0],
            "discovery_ci_trade_hi": h["discovery_ci_trade"][1],
            "discovery_dual_significant": h["discovery_dual_significant"],
            "discovery_economically_relevant_vs_C1": h["discovery_economically_relevant_vs_C1"],
            "sensitivity_robustness_check_consistent": h["sensitivity_robustness_check_consistent"],
            "n_far_primary_split": h["n_far_primary_split"],
            "primary_comparison_computable": h["primary_comparison_computable"],
            "sensitivity_comparison_computable": h["sensitivity_comparison_computable"],
        })
compact_csv_path = os.path.join(OUT, "m4_acceptance_state_map_primary_comparison.csv")
pd.DataFrame(compact_rows).to_csv(compact_csv_path, index=False)
print(f"[write] {compact_csv_path}", flush=True)

print("\n" + "=" * 110)
print("HEADLINE (position_direction_corrected variant, primary comparison, far,low vs far,high):")
for sample_name, by_h in [("discovery", disc_by_horizon), ("confirmation", conf_by_horizon)]:
    for h in by_h:
        if not h["primary_comparison_computable"]:
            print(f"  {sample_name:12s} H={h['horizon']:>3d}  PRIMARY COMPARISON NOT COMPUTABLE "
                  f"(far ∩ low or far ∩ high is empty in this sample, n_far={h['n_far_primary_split']})")
            continue
        print(f"  {sample_name:12s} H={h['horizon']:>3d}  "
              f"reversion(far_low-far_high)={h['reversion_far_low_minus_far_high']:+.3f}t "
              f"sess_CI={[round(x,3) for x in h['reversion_ci_session']]} "
              f"trade_CI={[round(x,3) for x in h['reversion_ci_trade']]} "
              f"sig={h['reversion_dual_significant']} "
              f"econ_rel={h['reversion_economically_relevant_vs_C1']}  |  "
              f"discovery(far_high-far_low)={h['discovery_far_high_minus_far_low']:+.3f}t "
              f"sess_CI={[round(x,3) for x in h['discovery_ci_session']]} "
              f"trade_CI={[round(x,3) for x in h['discovery_ci_trade']]} "
              f"sig={h['discovery_dual_significant']} "
              f"econ_rel={h['discovery_economically_relevant_vs_C1']}  |  "
              f"sens_robust_consistent={h['sensitivity_robustness_check_consistent']}")
print("=" * 110)
print("M4 ACCEPTANCE x DISTANCE STATE MAP DONE")
