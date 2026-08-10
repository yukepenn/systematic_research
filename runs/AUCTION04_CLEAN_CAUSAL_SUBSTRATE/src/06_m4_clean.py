"""AUCTION04_CLEAN_CAUSAL_SUBSTRATE -- M4 replication: acceptance x distance state map on the
clean, certified-causal substrate.

Straight re-run of AUCTION03_MECHANISM_DECOMPOSITION/src/04_m4_acceptance_state_map.py's exact
procedure (2x2 median-split state map: distance_state {near,far} x acceptance_state {low,high},
same cell metrics, same primary far_low-vs-far_high comparison, same dual-clustered [session-block
+ trade-block, 1000 reps each] bootstrap, same accept_sensitivity robustness check, H in
{15,60,300}, both discovery and confirmation samples) -- with ONLY the value_dist_ticks / markout
side of the join swapped for the clean, certified-causal substrate
(runs/AUCTION04_CLEAN_CAUSAL_SUBSTRATE/out/clean_decision_outcomes(.parquet|_CONFIRM.parquet)).
acceptance_features.parquet (accept_primary/accept_sensitivity) is untouched, reused exactly as
built by AUCTION03 -- it was constructed directly from raw trade prints without using grid1s's
`last` column and passed its own independent lookahead audit (per task instruction, not rebuilt
here).

WHAT IS DIFFERENT FROM THE ORIGINAL SCRIPT, AND WHY
-----------------------------------------------------
CAVEAT 1 in the original (4x tick-scaling bug on abs/signed_markout_H, mfe_H, mae_H, range_H) does
NOT need correcting here -- it is fixed AT THE SOURCE. AUCTION04's
01_build_clean_substrate.py docstring traces the bug to a double tick-division (build_sechilo.py
already stores mid in tick units; 03_diagnostics.py then divided the already-tick-scaled
difference by TICK again). The clean substrate's forward-outcome columns
(abs_markout_ticks_H/signed_markout_ticks_H/mfe_ticks_H/mae_ticks_H/range_ticks_H) are computed
as `end_mid - base` directly (both operands already in tick units, no re-division -- see that
script's process_session()), so they are already correct ticks on disk. This script therefore
does NOT divide by 4; it only renames the `*_ticks_H` columns to the `*_H` names the rest of this
pipeline (and CAVEAT 2/3 logic below) expects. A sanity check below independently confirms the
fix took effect: for matched (sess_tag,time) decision points also present in the original
(buggy) file, clean abs_markout_H is verified to sit near original_stored/4 (median absolute
relative deviation reported, not asserted exactly-equal, since the clean substrate also carries
DEFECT 2's fix and a different mid-price rebuild path -- small legitimate differences are
expected; a ~4x-scale match, not a 1x-scale match, is the diagnostic that matters).

The original DEFECT 2 (grid1s's `last` column mislabeling bucket-end trades as bucket-start,
giving value_dist_ticks's numerator a ~1s lookahead smear) is also fixed at the source: the clean
substrate's value_dist_ticks is built from `causal_last_t`, a strict searchsorted(time<=t) causal
lookup directly against raw bip==0 trade prints (01_build_clean_substrate.py's causal_lookup()),
independently certified causal with zero violations across 378 sampled timestamps
(03_causality_audit.py, overall_verdict = ZERO_VIOLATIONS_CERTIFIED_CLEAN). This script trusts
that certification (per task instruction) and does not re-derive value_dist_ticks itself; it is
read directly off clean_decision_outcomes(.parquet|_CONFIRM.parquet).

CAVEAT 2 from the original (signed_markout_H is signed by the INCUMBENT POSITION's direction,
side = sign(position_B), NOT by sign(value_dist_ticks)) STILL APPLIES UNCHANGED: the clean
substrate's process_session() builds signed_markout_ticks_H with the identical
`sm[i] = s * (end_mid - base)`, s = sign(position_B) convention (see that script, HORIZONS loop).
Both `as_specified` (task's literal formula) and `position_direction_corrected`
(= as_specified * sign(position_B), the canonical variant for the reversion-vs-discovery test)
are computed and reported exactly as in the original.

CAVEAT 3 from the original (accept_primary/accept_sensitivity ceiling-massed at 1.0, degenerate
literal "<=median"/">median" split; ties routed to "high" instead) STILL APPLIES UNCHANGED --
acceptance_features.parquet is the identical, un-rebuilt file.

Governance: reads ONLY clean_decision_outcomes(.parquet|_CONFIRM.parquet) (this run's own
already-built, already-certified output) and the frozen acceptance_features.parquet (read-only,
AUCTION03 output). Does not touch any raw/grid1s/sechilo session data directly, and does not
modify any file under AUCTION01/AUCTION02/AUCTION03/W5_PROTECTED_CONFIRMATION. Same 37 discovery /
8 confirmation-listed (6 BBO-usable) date lists as the original, unchanged.
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

OUT = os.path.join(ROOT, "runs", "AUCTION04_CLEAN_CAUSAL_SUBSTRATE", "out")
os.makedirs(OUT, exist_ok=True)

TICK = 0.25
HORIZONS = [15, 60, 300]
NBOOT = 1000
RNG_SEED = 20260810  # identical seed to the original M4 script (procedure frozen unchanged)
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

# ---- clean, certified-causal substrate (this run's own output) replaces the original two files
DISCOVERY_PATH = os.path.join(OUT, "clean_decision_outcomes.parquet")
CONFIRM_PATH = os.path.join(OUT, "clean_decision_outcomes_CONFIRM.parquet")
# ---- acceptance feature untouched: reused exactly as built by AUCTION03 (task instruction)
ACCEPT_PATH = os.path.join(ROOT, "runs", "AUCTION03_MECHANISM_DECOMPOSITION", "out",
                            "acceptance_features.parquet")
# ---- original (defect-bearing) file, read ONLY for the read-only CAVEAT-1-fix sanity check below
ORIG_DISCOVERY_PATH = os.path.join(ROOT, "runs", "AUCTION01_VALUE_STATE", "out",
                                    "decision_outcomes.parquet")

# clean substrate column names -> the *_H names the rest of this (unchanged-procedure) pipeline
# expects, matching the original script's schema exactly.
RENAME_MAP = {}
for _h in HORIZONS:
    RENAME_MAP[f"abs_markout_ticks_{_h}"] = f"abs_markout_{_h}"
    RENAME_MAP[f"range_ticks_{_h}"] = f"range_{_h}"
    RENAME_MAP[f"signed_markout_ticks_{_h}"] = f"signed_markout_{_h}"
    RENAME_MAP[f"mfe_ticks_{_h}"] = f"mfe_{_h}"
    RENAME_MAP[f"mae_ticks_{_h}"] = f"mae_{_h}"


# ============================================================= load + filter (no 4x correction:
# ============================================================= clean substrate already correct)
def load_correct_filter(path, allowed_dates, label):
    raw = pd.read_parquet(path)
    raw_n, raw_sessions = len(raw), sorted(raw["sess_tag"].unique())
    df = raw[raw["sess_tag"].isin(allowed_dates)].copy()
    df = df.rename(columns=RENAME_MAP)
    kept_sessions = sorted(df["sess_tag"].unique())
    missing_from_file = sorted(set(allowed_dates) - set(kept_sessions))
    extra_in_file_not_in_list = sorted(set(raw_sessions) - set(allowed_dates))
    print(f"[{label}] clean substrate file: {raw_n} rows / {len(raw_sessions)} sessions. "
          f"After explicit filter to the {len(allowed_dates)}-date list (no 4x correction needed "
          f"-- fixed at source, see module docstring): {len(df)} rows / {len(kept_sessions)} "
          f"sessions. Listed dates absent from file: {missing_from_file}. Sessions in file but "
          f"outside the list (dropped): {extra_in_file_not_in_list}.", flush=True)
    df = df.sort_values(["sess_tag", "time"]).reset_index(drop=True)
    meta = {"raw_rows": int(raw_n), "raw_sessions": len(raw_sessions),
            "filtered_rows": int(len(df)), "filtered_sessions": len(kept_sessions),
            "listed_dates_absent_from_file": missing_from_file,
            "sessions_in_file_dropped_as_outside_list": extra_in_file_not_in_list}
    return df, meta


disc_df, disc_meta = load_correct_filter(DISCOVERY_PATH, DISCOVERY_DATES, "discovery")
conf_df, conf_meta = load_correct_filter(CONFIRM_PATH, CONFIRMATION_DATES, "confirmation")

accept = pd.read_parquet(ACCEPT_PATH)[["sess_tag", "time", "accept_primary", "accept_sensitivity"]]


# ============================================================= sanity check: CAVEAT-1 fix took
# ============================================================= effect at the source (~4x scale
# ============================================================= vs the original buggy file, on the
# ============================================================= matched (sess_tag,time) subset --
# ============================================================= NOT an exact-equality check, since
# ============================================================= the clean substrate also carries
# ============================================================= the independent DEFECT-2 fix and a
# ============================================================= separately-rebuilt mid-price path.
def sanity_check_4x_fix_at_source():
    orig = pd.read_parquet(ORIG_DISCOVERY_PATH,
                            columns=["sess_tag", "time", "abs_markout_60"])
    orig = orig[orig["sess_tag"].isin(DISCOVERY_DATES)].copy()
    m = disc_df[["sess_tag", "time", "abs_markout_60"]].merge(
        orig, on=["sess_tag", "time"], suffixes=("_clean", "_orig_buggy"))
    m = m.dropna(subset=["abs_markout_60_clean", "abs_markout_60_orig_buggy"])
    m = m[(m["abs_markout_60_clean"] > 0) & (m["abs_markout_60_orig_buggy"] > 0)]
    ratio = m["abs_markout_60_orig_buggy"] / m["abs_markout_60_clean"]
    med_ratio = float(ratio.median())
    print(f"[sanity check] CAVEAT-1 fix at source: matched {len(m)} (sess_tag,time) decision "
          f"points present in both the clean substrate and the original buggy "
          f"decision_outcomes.parquet. median(orig_buggy_abs_markout_60 / clean_abs_markout_60) "
          f"= {med_ratio:.3f} (expect ~4.0 if the 4x bug is fixed at source and both files are "
          f"otherwise measuring the same underlying quantity; not expected to be exactly 4.0 row "
          f"-by-row because the clean substrate independently rebuilds mid-price from sechilo and "
          f"also fixes DEFECT 2).", flush=True)
    return {"n_matched": int(len(m)), "median_ratio_orig_over_clean": med_ratio}


sanity_4x = sanity_check_4x_fix_at_source()


# ============================================================= verify CAVEAT-2 identity (still
# ============================================================= applies: signed_markout_H is
# ============================================================= incumbent-position-signed, both in
# ============================================================= the original and in this clean
# ============================================================= substrate's identical formula)
def verify_corrections(df, label):
    for H in HORIZONS:
        col = f"signed_markout_{H}"
        sub = df.dropna(subset=[col])
        sub = sub[sub["position_B"] != 0]
        if len(sub) == 0:
            continue
        max_diff = float((sub[col].abs() - sub[f"abs_markout_{H}"]).abs().max())
        assert max_diff < 1e-6, f"CAVEAT-2 recovery identity failed {label} H={H}: max_diff={max_diff}"
    print(f"[check] {label}: |signed_markout_H| == abs_markout_H verified exactly "
          f"(clean substrate, wherever position_B!=0), all horizons.", flush=True)


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
# ============================================================= the original / 01_m2m3_signed_
# ============================================================= decomposition.py)
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

# ============================================================= compare cell populations vs the
# ============================================================= original (frozen, read-only) run --
# ============================================================= does the corrected, less-noisy
# ============================================================= value_dist_ticks change how many
# ============================================================= rows land in the far_low cell?
def load_original_cell_counts():
    orig_csv = os.path.join(ROOT, "runs", "AUCTION03_MECHANISM_DECOMPOSITION", "out",
                             "m4_acceptance_state_map.csv")
    o = pd.read_csv(orig_csv)
    o = o[(o["split"] == "primary_accept") & (o["horizon"] == 15)][["sample", "cell", "n"]]
    return {(r["sample"], r["cell"]): int(r["n"]) for _, r in o.iterrows()}


orig_counts = load_original_cell_counts()
cell_population_comparison = []
for sample_name, by_h in [("discovery", disc_by_horizon), ("confirmation", conf_by_horizon)]:
    cells15 = by_h[0]["cells"]  # H=15 cell populations are identical across H by construction
    for c in cells15:
        key = (sample_name, c["cell"])
        cell_population_comparison.append({
            "sample": sample_name, "cell": c["cell"],
            "n_clean": c["n"], "n_original_buggy_substrate": orig_counts.get(key),
            "delta": (c["n"] - orig_counts[key]) if key in orig_counts else None,
        })
print("\n[cell population comparison, clean vs original substrate, H=15 cells (identical across H)]")
for r in cell_population_comparison:
    print(f"  {r}")

far_low_still_nearly_empty = {
    "discovery": {
        "n_clean": next(c["n"] for c in disc_by_horizon[0]["cells"] if c["cell"] == "far_low"),
        "n_original": orig_counts.get(("discovery", "far_low")),
        "frac_of_discovery_sample_clean": (
            next(c["n"] for c in disc_by_horizon[0]["cells"] if c["cell"] == "far_low")
            / len(disc_s)),
    },
    "confirmation": {
        "n_clean": next(c["n"] for c in conf_by_horizon[0]["cells"] if c["cell"] == "far_low"),
        "n_original": orig_counts.get(("confirmation", "far_low")),
        "frac_of_confirmation_sample_clean": (
            next(c["n"] for c in conf_by_horizon[0]["cells"] if c["cell"] == "far_low")
            / len(conf_s)),
    },
}
print(f"\n[far_low cell, clean vs original] {far_low_still_nearly_empty}")

# ============================================================= write outputs
summary_json = {
    "spec_note": ("AUCTION04 replication of AUCTION03's M4 acceptance x distance 2x2 state map, "
                   "identical procedure, with value_dist_ticks/markout columns sourced from the "
                   "clean, certified-causal substrate (clean_decision_outcomes(.parquet|_CONFIRM"
                   ".parquet), zero causality violations across 378 sampled timestamps -- see "
                   "runs/AUCTION04_CLEAN_CAUSAL_SUBSTRATE/out/causality_audit_results.json) "
                   "instead of the original decision_outcomes(.parquet|_CONFIRM.parquet). "
                   "acceptance_features.parquet (accept_primary/accept_sensitivity) is unchanged, "
                   "reused as-is per task instruction. See module docstring for what changed vs "
                   "the original script: CAVEAT 1 (4x tick-scaling bug) is fixed at the substrate "
                   "source, no correction applied here (only a column rename); CAVEAT 2 "
                   "(signed_markout_H is incumbent-position- not distance-direction-signed) still "
                   "applies unchanged, both 'as_specified' and 'position_direction_corrected' "
                   "variants reported, the latter canonical; CAVEAT 3 (accept_primary/"
                   "accept_sensitivity ceiling-massed at 1.0, tie-to-high median-split fix) still "
                   "applies unchanged (acceptance_features.parquet untouched)."),
    "c1_cost_hurdle_ticks_roundtrip": C1_TICKS,
    "nboot": NBOOT, "rng_seed": RNG_SEED,
    "sanity_check_4x_fix_at_source": sanity_4x,
    "governance": {"discovery_filter": disc_meta, "confirmation_filter": conf_meta},
    "median_splits": {"discovery": disc_medians, "confirmation": conf_medians},
    "n_merged_rows": {"discovery": int(len(disc_s)), "confirmation": int(len(conf_s))},
    "n_sessions": {"discovery": int(disc_s["sess_tag"].nunique()),
                   "confirmation": int(conf_s["sess_tag"].nunique())},
    "cell_population_comparison_vs_original_substrate": cell_population_comparison,
    "far_low_cell_still_nearly_empty": far_low_still_nearly_empty,
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


json_path = os.path.join(OUT, "m4_clean_state_map.json")
with open(json_path, "w") as f:
    json.dump(summary_json, f, indent=2, default=_default)
print(f"[write] {json_path}", flush=True)

flat_rows = []
for sample_name, rows in [("discovery", disc_csv_rows), ("confirmation", conf_csv_rows)]:
    flat_rows.extend(rows)
csv_path = os.path.join(OUT, "m4_clean_state_map.csv")
pd.DataFrame(flat_rows).to_csv(csv_path, index=False)
print(f"[write] {csv_path}", flush=True)

print("\n" + "=" * 110)
print("HEADLINE (position_direction_corrected variant, primary comparison, far,low vs far,high) "
      "-- CLEAN SUBSTRATE:")
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
print("M4 CLEAN SUBSTRATE ACCEPTANCE x DISTANCE STATE MAP DONE")
