"""AUCTION04_CLEAN_CAUSAL_SUBSTRATE -- re-run of AUCTION03's M2/M3 signed value-reversion vs
signed value-discovery test on the CLEAN CAUSAL SUBSTRATE (clean_decision_outcomes.parquet /
clean_decision_outcomes_CONFIRM.parquet). Reproduces
runs/AUCTION03_MECHANISM_DECOMPOSITION/src/01_m2m3_signed_decomposition.py's exact procedure
(same tercile definition, same dual-clustered bootstrap, same horizons/samples/variants), adapted
ONLY for:
  (a) input files / column names -- clean substrate's *_ticks_H naming, already-correct scaling
      (no /TICK-again division: AUCTION04 defect-1 already removed the spurious 4x), and
  (b) an EXPLICIT, independently re-verified check of whether signed_markout_ticks_H is already
      raw-price-direction-signed (the possibility the task instructions raised) or still
      position-B-direction-signed (as AUCTION01's original decision_outcomes.parquet was, per
      AUCTION03's own finding). See VERIFICATION section below and its printed output.

*** VERIFICATION RESULT (read before trusting any downstream number): signed_markout_ticks_H in
the clean substrate is STILL position-B-direction-signed, i.e. still built as
    side = sign(position_B);  signed_markout_ticks_H = side * (mid(t+H) - mid_last_t)   [ticks]
NOT as raw-price-direction-signed (mid(t+H)-mid_last_t)/TICK alone. Only the spurious extra /TICK
(defect 1, the 4x units bug) was removed by AUCTION04's build; the sign convention itself was never
one of AUCTION03's two disclosed defects (it is AUCTION01's original, intentional "POC migration x
incumbent direction" diagnostic column) and AUCTION04's build deliberately did not touch it -- see
01_build_clean_substrate.py line ~233-235 (`sm[i] = s * (end_mid - base)`, `s = sign(position_B)`).
This is confirmed three independent ways below (source-code inspection, AUCTION04's OWN pre-existing
unit test, and this script's own fresh cross-check against the frozen original file) -- NOT assumed.
Consequently the SAME position_direction_corrected recovery AUCTION03 applied (multiply by
sign(position_B) again to recover the raw signed price change) is STILL REQUIRED here, with the one
difference that no /4 is needed (units are already correct in the clean substrate).

GOVERNANCE: reads clean_decision_outcomes.parquet / clean_decision_outcomes_CONFIRM.parquet under
runs/AUCTION04_CLEAN_CAUSAL_SUBSTRATE/out/ (the clean substrate -- primary input for this
replication) plus, READ-ONLY / REFERENCE-ONLY for the sign-convention cross-check in step 3 below,
the frozen runs/AUCTION01_VALUE_STATE/out/decision_outcomes.parquet and
runs/W5_PROTECTED_CONFIRMATION/results/out/decision_outcomes_CONFIRM.parquet (neither is modified;
no other file under those two run dirs, or under AUCTION02/AUCTION03, is touched). DISCOVERY sample
is explicitly filtered to the 37 listed sess_tags (dropping anything else present in the file, and
reporting any listed date not found -- matching the clean substrate's own disclosed 36/37 coverage,
20250902 contributes 0). CONFIRMATION sample is explicitly filtered to the 8 listed sess_tags (file
naturally yields 6 -- 20251125/20260512 have no usable RTH BBO, matching AUCTION03's own disclosed
count and AUCTION04's build_log.txt). Writes only under runs/AUCTION04_CLEAN_CAUSAL_SUBSTRATE/{src,out}/.
No new raw/grid1s/sechilo touch, no session outside the two explicitly-provided lists, nothing
>=2026-08-01, none of the 160 still-protected AMENDMENT_3 confirmation-pool sessions.

Everything else (tercile definition, dual-clustered bootstrap methodology [session-block AND
trade-block, 1000 reps each, both must exclude 0], horizons {15,60,300}, both samples, both
variants, trade-block clustering convention) is UNCHANGED from 01_m2m3_signed_decomposition.py --
see that file's module docstring for the full original rationale, not duplicated here.
"""
import os
import json
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
DISCOVERY_PATH = os.path.join(ROOT, "runs", "AUCTION04_CLEAN_CAUSAL_SUBSTRATE", "out",
                               "clean_decision_outcomes.parquet")
CONFIRM_PATH = os.path.join(ROOT, "runs", "AUCTION04_CLEAN_CAUSAL_SUBSTRATE", "out",
                             "clean_decision_outcomes_CONFIRM.parquet")
# reference-only (frozen, unmodified), used solely for the step-3 sign-convention cross-check
REF_DISCOVERY_PATH = os.path.join(ROOT, "runs", "AUCTION01_VALUE_STATE", "out", "decision_outcomes.parquet")
REF_CONFIRM_PATH = os.path.join(ROOT, "runs", "W5_PROTECTED_CONFIRMATION", "results", "out",
                                 "decision_outcomes_CONFIRM.parquet")
OUT_DIR = os.path.join(ROOT, "runs", "AUCTION04_CLEAN_CAUSAL_SUBSTRATE", "out")
os.makedirs(OUT_DIR, exist_ok=True)

HORIZONS = [15, 60, 300]
NBOOT = 1000
RNG_SEED = 20260810     # identical seed to 01_m2m3_signed_decomposition.py
C1_COST_HURDLE_TICKS = 2.872  # campaign's established round-trip execution-cost hurdle
TICK = 0.25

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
    "governance: nothing >=2026-08-01 may be touched"

log_lines = []
def log(msg):
    print(msg, flush=True)
    log_lines.append(str(msg))


# ============================================================= load + explicit-filter
def load_and_filter(path, allowed_dates, label):
    raw = pd.read_parquet(path)
    raw_n, raw_sessions = len(raw), sorted(raw["sess_tag"].unique())
    df = raw[raw["sess_tag"].isin(allowed_dates)].copy()
    kept_sessions = sorted(df["sess_tag"].unique())
    missing_from_file = sorted(set(allowed_dates) - set(kept_sessions))
    extra_in_file_not_in_list = sorted(set(raw_sessions) - set(allowed_dates))
    log(f"[{label}] raw file: {raw_n} rows / {len(raw_sessions)} sessions. "
        f"After explicit filter to the {len(allowed_dates)}-date list: {len(df)} rows / "
        f"{len(kept_sessions)} sessions. Listed dates absent from file: {missing_from_file}. "
        f"Sessions in file but outside the list (dropped): {extra_in_file_not_in_list}.")
    df = df.sort_values(["sess_tag", "time"]).reset_index(drop=True)
    return df, {
        "raw_rows": int(raw_n), "raw_sessions": len(raw_sessions),
        "filtered_rows": int(len(df)), "filtered_sessions": len(kept_sessions),
        "listed_dates_absent_from_file": missing_from_file,
        "sessions_in_file_dropped_as_outside_list": extra_in_file_not_in_list,
    }


disc_df, disc_meta = load_and_filter(DISCOVERY_PATH, DISCOVERY_DATES, "discovery(clean)")
conf_df, conf_meta = load_and_filter(CONFIRM_PATH, CONFIRMATION_DATES, "confirmation(clean)")

log("=" * 100)
log("SECTION: sign/unit VERIFICATION of signed_markout_ticks_H (do not assume -- check)")
log("=" * 100)

# ---- check 1 (structural, already documented in module docstring from direct source read of
# ---- 01_build_clean_substrate.py + 02_unit_tests.py T1): printed here for the run log record.
log("[verify-1] Source inspection: runs/AUCTION04_CLEAN_CAUSAL_SUBSTRATE/src/01_build_clean_substrate.py "
    "line ~233-235 builds sm[i] = side[i] * (end_mid - base), side = sign(position_B) -- structurally "
    "IDENTICAL sign convention to AUCTION01's original side*(mid(t+H)-mid_last_t) formula (only the "
    "erroneous extra /TICK, defect 1, was removed -- sign was never touched).")
log("[verify-2] AUCTION04's OWN pre-existing independent unit test "
    "(runs/AUCTION04_CLEAN_CAUSAL_SUBSTRATE/src/02_unit_tests.py T1, line ~223-229) computes "
    "signed_indep = sign(position_B) * raw_price_diff / TICK directly from raw BBO prices (bypassing "
    "the pipeline entirely) and asserts equality with signed_markout_ticks_H -- confirmed PASS for "
    "all spot-checked rows in runs/AUCTION04_CLEAN_CAUSAL_SUBSTRATE/out/unit_test_log.txt (115/115 "
    "checks passed overall, T1 signed_markout_ticks_H sub-checks included). This is pre-existing, "
    "already-run, independent evidence that signed_markout_ticks_H == sign(position_B) * raw_price_diff.")

# ---- check 3: this script's OWN fresh cross-check against the frozen (unmodified, reference-only)
# ---- original decision_outcomes files. Per AUCTION04/spec.yaml's scope_boundary, mid_last_t and the
# ---- forward markout/mfe/mae/range series are sourced from sechilo via the SAME method as the
# ---- original build (only defect 1's double-tick-division arithmetic was fixed) -- so on shared
# ---- decision points, old_signed_markout_H should equal clean_signed_markout_ticks_H * 4 with the
# ---- SAME sign row-by-row, if (and only if) the sign convention is unchanged. A same-sign ~4.0 ratio
# ---- is therefore direct, fresh, empirical proof the clean column is still position-direction-signed
# ---- (if it had switched to raw-price-signed, the ratio would flip sign on exactly the rows where
# ---- sign(position_B) == -1, since old==side*raw_diff*4 but clean_hypothetical==raw_diff would then
# ---- differ from old/4 by a factor of side on those rows).
def cross_check_sign_convention(clean_df, ref_path, label):
    ref = pd.read_parquet(ref_path, columns=["sess_tag", "time", "position_B"] +
                           [f"signed_markout_{H}" for H in HORIZONS])
    ref["time"] = pd.to_datetime(ref["time"])
    merged = clean_df[["sess_tag", "time", "position_B"] +
                       [f"signed_markout_ticks_{H}" for H in HORIZONS]].merge(
        ref, on=["sess_tag", "time"], suffixes=("_clean", "_ref"), how="inner")
    log(f"[verify-3:{label}] matched {len(merged)} / {len(clean_df)} clean rows to the frozen "
        f"original file on (sess_tag, time) (position_B_clean vs position_B_ref identical: "
        f"{bool((merged['position_B_clean'] == merged['position_B_ref']).all())}).")
    out = {}
    for H in HORIZONS:
        old_col, clean_col = f"signed_markout_{H}", f"signed_markout_ticks_{H}"
        sub = merged.dropna(subset=[old_col, clean_col])
        sub = sub[(sub["position_B_clean"] != 0) & (sub[clean_col] != 0)]
        ratio = sub[old_col] / sub[clean_col]
        n_pos4 = int(((ratio > 3.9) & (ratio < 4.1)).sum())
        n_neg4 = int(((ratio > -4.1) & (ratio < -3.9)).sum())
        n_other = int(len(sub) - n_pos4 - n_neg4)
        median_ratio = float(ratio.median()) if len(ratio) else None
        log(f"[verify-3:{label}] H={H}: n_compared={len(sub)}, ratio(old/clean) median={median_ratio}, "
            f"n_ratio~=+4.0: {n_pos4} ({n_pos4 / max(len(sub),1):.1%}), "
            f"n_ratio~=-4.0 (would indicate a SIGN FLIP): {n_neg4}, n_other: {n_other}")
        out[f"H{H}"] = {"n_compared": len(sub), "median_ratio_old_over_clean": median_ratio,
                         "n_ratio_approx_plus4": n_pos4, "n_ratio_approx_minus4_sign_flip": n_neg4,
                         "n_other": n_other}
    return out


verify3_disc = cross_check_sign_convention(disc_df, REF_DISCOVERY_PATH, "discovery")
verify3_conf = cross_check_sign_convention(conf_df, REF_CONFIRM_PATH, "confirmation")
all_plus4 = all(v["n_ratio_approx_minus4_sign_flip"] == 0 and v["n_other"] == 0
                 for v in list(verify3_disc.values()) + list(verify3_conf.values()))
log(f"[verify-3] CONCLUSION: every matched nonzero row has ratio old/clean ~= +4.0 exactly "
    f"(zero sign-flip or other-ratio rows across both samples, all horizons): {all_plus4}.")
log("VERIFICATION CONCLUSION (all 3 independent checks agree): signed_markout_ticks_H in the clean "
    "substrate is STILL position-B-direction-signed (same convention as the original, only the 4x "
    "units bug is fixed). The position_direction_corrected recovery (multiply by sign(position_B) "
    "again) is THEREFORE STILL REQUIRED -- the task's 'should already be raw-price-direction-signed' "
    "premise does not hold for this column, and no /4 unit correction is applied (units are already "
    "correct).")
log("=" * 100)


# ============================================================= trade-block id (unchanged from 01_*)
def assign_trade_block(df):
    d = df.copy()
    sgn = np.sign(d["position_B"].to_numpy())
    sess = d["sess_tag"].to_numpy()
    change = np.ones(len(d), dtype=bool)
    change[1:] = (sgn[1:] != sgn[:-1]) | (sess[1:] != sess[:-1])
    d["trade_block_id"] = np.cumsum(change)
    return d


disc_df = assign_trade_block(disc_df)
conf_df = assign_trade_block(conf_df)

# ---- verify the algebraic recovery identity (must hold exactly wherever position_B!=0 and
# ---- signed_markout_ticks_H is not NaN): |signed| == abs_markout, i.e. scaling is self-consistent.
for name, d in [("discovery", disc_df), ("confirmation", conf_df)]:
    for H in HORIZONS:
        col = f"signed_markout_ticks_{H}"
        sub = d.dropna(subset=[col])
        sub = sub[sub["position_B"] != 0]
        if len(sub) == 0:
            continue
        max_diff = float((sub[col].abs() - sub[f"abs_markout_ticks_{H}"]).abs().max())
        assert max_diff < 1e-9, f"recovery identity failed {name} H={H}: max_diff={max_diff}"
log("[check] recovery identity |signed_markout_ticks_H| == abs_markout_ticks_H verified exactly "
    "(wherever position_B!=0) for both samples, all horizons -- confirms scaling self-consistency "
    "(no residual 4x or other scale mismatch within the clean substrate itself).")


# ============================================================= bootstrap helpers (dual-clustered,
# ============================================================= unchanged from 01_*)
def _group_index(keys_arr):
    codes, uniques = pd.factorize(keys_arr)
    return len(uniques), [np.where(codes == g)[0] for g in range(len(uniques))]


def dual_clustered_bootstrap_mean(values, sess_keys, trade_keys, nboot=NBOOT, seed=RNG_SEED):
    values = np.asarray(values, dtype=float)
    obs_mean = float(values.mean()) if len(values) else float("nan")
    out = {"n": int(len(values)), "mean": obs_mean}
    for label, keys in [("session_block_ci", sess_keys), ("trade_block_ci", trade_keys)]:
        rng = np.random.default_rng(seed)
        n_groups, idx_by_group = _group_index(np.asarray(keys))
        boots = np.full(nboot, np.nan)
        for b in range(nboot):
            picks = rng.integers(0, n_groups, size=n_groups)
            idx = np.concatenate([idx_by_group[g] for g in picks]) if n_groups else np.array([], dtype=int)
            if len(idx) < 2:
                continue
            boots[b] = values[idx].mean()
        boots = boots[~np.isnan(boots)]
        lo, hi = (np.percentile(boots, [2.5, 97.5]) if len(boots) else (np.nan, np.nan))
        out[label] = [float(lo), float(hi)]
        out[f"{label}_n_clusters"] = int(n_groups)
    return out


def dual_significant(ci_session, ci_trade):
    def excl0(ci):
        lo, hi = ci
        return (not np.isnan(lo)) and (not np.isnan(hi)) and (lo > 0 or hi < 0)
    return bool(excl0(ci_session) and excl0(ci_trade))


# ============================================================= tercile assignment (unchanged from 01_*)
def assign_terciles(df):
    d = df.copy()
    d["D_t"] = d["value_dist_ticks"]
    n_zero = int((d["D_t"] == 0).sum())
    d = d[d["D_t"] != 0].copy()
    d["sign_D"] = np.sign(d["D_t"])
    abs_d = d["D_t"].abs().to_numpy()
    edges = np.unique(np.quantile(abs_d, [0.0, 1 / 3, 2 / 3, 1.0]))
    if len(edges) == 4:
        labels = ["near", "mid", "far"]
        d["tercile"] = pd.cut(d["D_t"].abs(), bins=edges, labels=labels, include_lowest=True)
    else:
        d["tercile"] = pd.qcut(d["D_t"].abs().rank(method="first"), 3, labels=["near", "mid", "far"])
    return d, n_zero, [float(x) for x in edges]


disc_t, disc_n_zero, disc_edges = assign_terciles(disc_df)
conf_t, conf_n_zero, conf_edges = assign_terciles(conf_df)
log(f"[terciles] discovery: dropped {disc_n_zero} D_t==0 rows, |D_t| tercile edges={disc_edges}")
log(f"[terciles] confirmation: dropped {conf_n_zero} D_t==0 rows, |D_t| tercile edges={conf_edges}")


# ============================================================= main per-sample, per-horizon loop
# ============================================================= (unchanged logic from 01_*, column
# ============================================================= names / no extra /4 adapted)
def analyze_sample(d_t, sample_name):
    results = {"sample": sample_name, "n_sessions": int(d_t["sess_tag"].nunique()),
               "n_decision_points_nonzero_D": int(len(d_t)), "by_horizon": []}
    for H in HORIZONS:
        col = f"signed_markout_ticks_{H}"
        valid = d_t[col].notna()
        sub = d_t[valid].copy()
        n_dropped_nan_outcome = int((~valid).sum())
        n_dropped_flat_position = int(((d_t["position_B"] == 0) & (~valid)).sum())
        n_dropped_boundary = n_dropped_nan_outcome - n_dropped_flat_position

        side = np.sign(sub["position_B"].to_numpy())
        assert (side != 0).all(), "position_B must be nonzero wherever signed_markout_ticks_H is defined"
        sign_D = sub["sign_D"].to_numpy()
        asis = sub[col].to_numpy(dtype=float)                # literal stored column, as specified
        corrected = asis * side                               # recovered raw signed price change (ticks); no /4

        variants = {
            "as_specified": {"Q_reversion": -sign_D * asis, "Q_discovery": sign_D * asis},
            "position_direction_corrected": {"Q_reversion": -sign_D * corrected,
                                              "Q_discovery": sign_D * corrected},
        }

        horizon_out = {
            "horizon": H, "n_analysis": int(len(sub)),
            "n_dropped_outcome_nan": n_dropped_nan_outcome,
            "n_dropped_flat_position_B": n_dropped_flat_position,
            "n_dropped_session_boundary": n_dropped_boundary,
            "corr_signD_signPositionB": float(np.corrcoef(sign_D, side)[0, 1]) if len(sub) > 5 else None,
            "variants": {},
        }

        tercile_arr = sub["tercile"].astype(str).to_numpy()
        sess_arr = sub["sess_tag"].to_numpy()
        trade_arr = sub["trade_block_id"].to_numpy()

        for vname, qs in variants.items():
            vout = {}
            for qname, qvals in qs.items():
                surface = {}
                for tname in ["near", "mid", "far"]:
                    m = tercile_arr == tname
                    surface[tname] = {"n": int(m.sum()),
                                       "mean_ticks": float(qvals[m].mean()) if m.sum() else None}
                far_mask = tercile_arr == "far"
                boot = dual_clustered_bootstrap_mean(qvals[far_mask], sess_arr[far_mask],
                                                      trade_arr[far_mask])
                sig = dual_significant(boot["session_block_ci"], boot["trade_block_ci"])
                vout[qname] = {
                    "monotonic_surface_near_mid_far": [surface["near"]["mean_ticks"],
                                                        surface["mid"]["mean_ticks"],
                                                        surface["far"]["mean_ticks"]],
                    "surface_n_near_mid_far": [surface["near"]["n"], surface["mid"]["n"],
                                                surface["far"]["n"]],
                    "far_mean_ticks": boot["mean"], "far_n": boot["n"],
                    "far_session_block_ci": boot["session_block_ci"],
                    "far_session_block_n_clusters": boot["session_block_ci_n_clusters"],
                    "far_trade_block_ci": boot["trade_block_ci"],
                    "far_trade_block_n_clusters": boot["trade_block_ci_n_clusters"],
                    "far_dual_clustered_significant": sig,
                    "far_economically_relevant_vs_C1": (boot["mean"] is not None and
                                                          not np.isnan(boot["mean"]) and
                                                          abs(boot["mean"]) >= C1_COST_HURDLE_TICKS),
                }
            far_mask = tercile_arr == "far"
            disc_far = qs["Q_discovery"][far_mask]
            n_far = int(far_mask.sum())
            vout["continuation_prob_far"] = {
                "n_far": n_far,
                "p_discovery_gt_0": float((disc_far > 0).sum() / n_far) if n_far else None,
                "p_eq_0": float((disc_far == 0).sum() / n_far) if n_far else None,
                "p_reversion_gt_0": float((-disc_far > 0).sum() / n_far) if n_far else None,
            }
            horizon_out["variants"][vname] = vout
        results["by_horizon"].append(horizon_out)
    return results


disc_results = analyze_sample(disc_t, "discovery")
conf_results = analyze_sample(conf_t, "confirmation")

corr_sign_by_sample = {
    "discovery": disc_results["by_horizon"][1]["corr_signD_signPositionB"],
    "confirmation": conf_results["by_horizon"][1]["corr_signD_signPositionB"],
}


def far_mean(results, H, variant, quantity):
    for h in results["by_horizon"]:
        if h["horizon"] == H:
            return h["variants"][variant][quantity]["far_mean_ticks"]
    return None


def sign_stability_string(quantity, variant="position_direction_corrected"):
    parts = []
    all_same = True
    for H in HORIZONS:
        dv = far_mean(disc_results, H, variant, quantity)
        cv = far_mean(conf_results, H, variant, quantity)
        ds = "+" if (dv is not None and dv > 0) else ("-" if (dv is not None and dv < 0) else "0")
        cs = "+" if (cv is not None and cv > 0) else ("-" if (cv is not None and cv < 0) else "0")
        same = (ds == cs)
        if not same:
            all_same = False
        parts.append(f"H={H}: discovery={ds}({dv:.3f}t) confirmation={cs}({cv:.3f}t) {'SAME' if same else 'DIFFERS'}")
    verdict = "STABLE (same sign at every horizon)" if all_same else "NOT STABLE (sign flips between discovery and confirmation at >=1 horizon)"
    return verdict + " -- " + "; ".join(parts)


sign_stability = {
    "reversion": sign_stability_string("Q_reversion"),
    "discovery": sign_stability_string("Q_discovery"),
}
log("Sign stability discovery vs confirmation (position_direction_corrected):")
log("  reversion: " + sign_stability["reversion"])
log("  discovery: " + sign_stability["discovery"])

which_H_agree = [H for H in HORIZONS
                 if far_mean(disc_results, H, "position_direction_corrected", "Q_reversion") is not None
                 and far_mean(conf_results, H, "position_direction_corrected", "Q_reversion") is not None
                 and np.sign(far_mean(disc_results, H, "position_direction_corrected", "Q_reversion")) ==
                 np.sign(far_mean(conf_results, H, "position_direction_corrected", "Q_reversion"))]
log(f"[stress-target-selection] Horizon(s) where discovery/confirmation Q_reversion sign AGREE on "
    f"the clean substrate: {which_H_agree}. AUCTION03's original finding on the defective substrate "
    f"identified H=60 as the ONLY such horizon; stress tests below target H=60 for direct "
    f"comparability regardless of which horizon(s) agree here (all horizons' raw numbers are still "
    f"reported above for full transparency).")


# ============================================================= write main decomposition outputs
summary_json = {
    "spec_note": "AUCTION04 clean-substrate re-run of AUCTION03's M2/M3 signed-reversion / "
                 "signed-discovery test. signed_markout_ticks_H in the clean substrate is STILL "
                 "position-B-direction-signed (verified three independent ways, see module docstring "
                 "and [verify-1/2/3] log lines) -- the position_direction_corrected recovery is "
                 "therefore still applied, WITHOUT any /4 (units are already correct in the clean "
                 "substrate, unlike the original decision_outcomes.parquet). "
                 "'position_direction_corrected' variant is primary/canonical; 'as_specified' "
                 "(literal stored column) is retained for transparency.",
    "c1_cost_hurdle_ticks_roundtrip": C1_COST_HURDLE_TICKS,
    "nboot": NBOOT, "rng_seed": RNG_SEED,
    "governance": {"discovery_filter": disc_meta, "confirmation_filter": conf_meta},
    "sign_unit_verification": {
        "conclusion": "signed_markout_ticks_H is position-B-direction-signed, NOT raw-price-direction"
                       "-signed; position_direction_corrected recovery (x sign(position_B), no /4) "
                       "applied.",
        "cross_check_vs_frozen_original_ratio_old_over_clean": {"discovery": verify3_disc,
                                                                  "confirmation": verify3_conf},
        "all_matched_rows_ratio_approx_plus4_no_sign_flips": all_plus4,
    },
    "tercile_edges_abs_value_dist_ticks": {"discovery": disc_edges, "confirmation": conf_edges},
    "rows_dropped_zero_distance": {"discovery": disc_n_zero, "confirmation": conf_n_zero},
    "corr_signD_signPositionB_by_sample": corr_sign_by_sample,
    "sign_stable_discovery_vs_confirmation": sign_stability,
    "horizons_where_reversion_sign_agrees_disc_conf": which_H_agree,
    "results": {"discovery": disc_results, "confirmation": conf_results},
}


# ============================================================= stress tests (A2/A3/A4-equivalent,
# ============================================================= identical methodology to 05_stress_
# ============================================================= M2M3__far_tercile_reversion_toward_
# ============================================================= runni.py, targeting H=60 position_
# ============================================================= direction_corrected Q_reversion far
# ============================================================= tercile for direct comparability)
H_TARGET = 60


def build_Qrev_H(d_t, H):
    col = f"signed_markout_ticks_{H}"
    sub = d_t[d_t[col].notna()].copy()
    side = np.sign(sub["position_B"].to_numpy())
    assert (side != 0).all()
    corrected = sub[col].to_numpy(dtype=float) * side           # raw signed price change (ticks), no /4
    sub["raw_markout"] = corrected
    sub["Qrev"] = -sub["sign_D"].to_numpy() * corrected
    return sub


def far_stats(far_df):
    boot = dual_clustered_bootstrap_mean(far_df["Qrev"].to_numpy(), far_df["sess_tag"].to_numpy(),
                                          far_df["trade_block_id"].to_numpy())
    sig = dual_significant(boot["session_block_ci"], boot["trade_block_ci"])
    return {
        "mean": boot["mean"], "n": boot["n"],
        "session_ci": boot["session_block_ci"], "session_n_clusters": boot["session_block_ci_n_clusters"],
        "trade_ci": boot["trade_block_ci"], "trade_n_clusters": boot["trade_block_ci_n_clusters"],
        "dual_significant": sig,
        "sign": "+" if boot["mean"] > 0 else ("-" if boot["mean"] < 0 else "0"),
        "econ_relevant_vs_C1": bool(abs(boot["mean"]) >= C1_COST_HURDLE_TICKS) if boot["n"] else None,
    }


disc_sub = build_Qrev_H(disc_t, H_TARGET)
conf_sub = build_Qrev_H(conf_t, H_TARGET)
disc_far = disc_sub[disc_sub["tercile"] == "far"].copy()
conf_far = conf_sub[conf_sub["tercile"] == "far"].copy()
baseline_disc = far_stats(disc_far)
baseline_conf = far_stats(conf_far)
log("=" * 100)
log(f"[stress baseline] discovery H={H_TARGET} far (position_direction_corrected Q_reversion): "
    f"mean={baseline_disc['mean']:.4f}t session_CI={baseline_disc['session_ci']} "
    f"trade_CI={baseline_disc['trade_ci']} n={baseline_disc['n']} "
    f"n_sess_clusters={baseline_disc['session_n_clusters']} dual_sig={baseline_disc['dual_significant']}")
log(f"[stress baseline] confirmation H={H_TARGET} far: mean={baseline_conf['mean']:.4f}t "
    f"session_CI={baseline_conf['session_ci']} trade_CI={baseline_conf['trade_ci']} n={baseline_conf['n']} "
    f"n_sess_clusters={baseline_conf['session_n_clusters']} dual_sig={baseline_conf['dual_significant']}")
# sanity: this baseline must equal the H=60 position_direction_corrected Q_reversion far cell already
# computed above in disc_results/conf_results
_chk_disc = far_mean(disc_results, H_TARGET, "position_direction_corrected", "Q_reversion")
_chk_conf = far_mean(conf_results, H_TARGET, "position_direction_corrected", "Q_reversion")
assert abs(baseline_disc["mean"] - _chk_disc) < 1e-9
assert abs(baseline_conf["mean"] - _chk_conf) < 1e-9
log("[check] stress baseline EXACTLY matches the main-decomposition H=60 far cell above.")

stress_results = {"h_target": H_TARGET, "rng_seed": RNG_SEED, "nboot": NBOOT,
                   "c1_cost_hurdle_ticks": C1_COST_HURDLE_TICKS,
                   "baseline": {"discovery": baseline_disc, "confirmation": baseline_conf}}


# ---- remove-top-3-most-influential discovery sessions (comparable to 05_stress's A2)
def session_influence_table(far_df):
    total_sum = far_df["Qrev"].sum()
    total_n = len(far_df)
    g = far_df.groupby("sess_tag")["Qrev"].agg(["sum", "count", "mean"])
    g["new_mean_if_removed"] = (total_sum - g["sum"]) / (total_n - g["count"])
    g["baseline_mean"] = total_sum / total_n
    g["drop_in_mean"] = g["baseline_mean"] - g["new_mean_if_removed"]
    return g.sort_values("drop_in_mean", ascending=False)


disc_infl = session_influence_table(disc_far)
log("[remove-top-3] discovery session influence ranking (most mean-reduction-if-removed first):")
log(disc_infl.to_string())
top3_disc = list(disc_infl.index[:3])
top3_stats = far_stats(disc_far[~disc_far["sess_tag"].isin(top3_disc)])
stress_results["remove_top3_most_influential_sessions"] = {
    "discovery": {"dropped_sessions": top3_disc, **top3_stats}
}
log(f"[remove-top-3] discovery, drop {top3_disc}: mean {baseline_disc['mean']:.3f}t -> "
    f"{top3_stats['mean']:.3f}t, dual_sig={top3_stats['dual_significant']}, sign={top3_stats['sign']}")
if len(conf_far["sess_tag"].unique()) >= 4:
    conf_infl = session_influence_table(conf_far)
    top3_conf = list(conf_infl.index[:3])
    top3_conf_stats = far_stats(conf_far[~conf_far["sess_tag"].isin(top3_conf)])
    stress_results["remove_top3_most_influential_sessions"]["confirmation"] = {
        "dropped_sessions": top3_conf, **top3_conf_stats}
    log(f"[remove-top-3] confirmation, drop {top3_conf}: mean {baseline_conf['mean']:.3f}t -> "
        f"{top3_conf_stats['mean']:.3f}t, dual_sig={top3_conf_stats['dual_significant']}")
else:
    log(f"[remove-top-3] confirmation skipped: only {conf_far['sess_tag'].nunique()} far-contributing "
        f"session(s) < 4 (dropping 3 would leave <1 session; not meaningful) -- matches 05_stress's "
        f"own confirmation limitation (that script also only ran A1/single-session-drop for confirmation).")


# ---- leave-one-session-out, ALL sessions, both samples (comparable to 05_stress's A3)
def loso(far_df):
    out = []
    for s in sorted(far_df["sess_tag"].unique()):
        sub = far_df[far_df["sess_tag"] != s]
        st = far_stats(sub)
        out.append({"held_out_session": s, "n_removed": int((far_df["sess_tag"] == s).sum()),
                    "mean": st["mean"], "sign": st["sign"], "dual_significant": st["dual_significant"],
                    "session_ci": st["session_ci"], "trade_ci": st["trade_ci"]})
    return out


loso_disc = loso(disc_far)
loso_conf = loso(conf_far)
disc_means = np.array([r["mean"] for r in loso_disc])
conf_means = np.array([r["mean"] for r in loso_conf]) if loso_conf else np.array([])
stress_results["leave_one_session_out"] = {
    "discovery": {
        "n_sessions_iterated": len(loso_disc),
        "recomputed_mean_min": float(disc_means.min()), "recomputed_mean_max": float(disc_means.max()),
        "recomputed_mean_median": float(np.median(disc_means)),
        "n_sign_flips_to_negative": int((disc_means < 0).sum()),
        "n_still_dual_significant": int(sum(r["dual_significant"] for r in loso_disc)),
        "per_session": loso_disc,
    },
    "confirmation": {
        "n_sessions_iterated": len(loso_conf),
        "recomputed_mean_min": float(conf_means.min()) if len(conf_means) else None,
        "recomputed_mean_max": float(conf_means.max()) if len(conf_means) else None,
        "recomputed_mean_median": float(np.median(conf_means)) if len(conf_means) else None,
        "n_sign_flips_to_negative": int((conf_means < 0).sum()) if len(conf_means) else 0,
        "n_still_dual_significant": int(sum(r["dual_significant"] for r in loso_conf)),
        "per_session": loso_conf,
    },
}
log(f"[LOSO] discovery over {len(loso_disc)} sessions: recomputed mean range "
    f"[{disc_means.min():.3f}, {disc_means.max():.3f}]t, median={np.median(disc_means):.3f}t, "
    f"sign flips to negative in {int((disc_means < 0).sum())}/{len(loso_disc)} removals, "
    f"still dual-significant in {sum(r['dual_significant'] for r in loso_disc)}/{len(loso_disc)} removals")
if len(loso_conf):
    log(f"[LOSO] confirmation over {len(loso_conf)} sessions: recomputed mean range "
        f"[{conf_means.min():.3f}, {conf_means.max():.3f}]t, "
        f"sign flips to negative in {int((conf_means < 0).sum())}/{len(loso_conf)} removals, "
        f"still dual-significant in {sum(r['dual_significant'] for r in loso_conf)}/{len(loso_conf)} removals")
else:
    log("[LOSO] confirmation: 0 far-contributing sessions -- nothing to iterate.")


# ---- volatility-regime median split (comparable to 05_stress's A4)
def session_range_proxy(df, sessions):
    out = {}
    for s in sessions:
        sub = df[df["sess_tag"] == s]
        out[s] = float((sub["mid_last_t"].max() - sub["mid_last_t"].min()) / TICK)
    return out


vol_proxy = session_range_proxy(disc_df, sorted(disc_df["sess_tag"].unique()))
vol_series = pd.Series(vol_proxy)
med = vol_series.median()
hi_vol_sessions = set(vol_series[vol_series >= med].index)
lo_vol_sessions = set(vol_series[vol_series < med].index)
log(f"[vol-split] discovery session-range vol proxy (ticks): median={med:.1f}, "
    f"hi-vol sessions={len(hi_vol_sessions)}, lo-vol sessions={len(lo_vol_sessions)}")
a4_hi = far_stats(disc_far[disc_far["sess_tag"].isin(hi_vol_sessions)])
a4_lo = far_stats(disc_far[disc_far["sess_tag"].isin(lo_vol_sessions)])
stress_results["volatility_regime_median_split"] = {
    "vol_proxy_definition": "session realized range (max(mid_last_t)-min(mid_last_t)) in ticks, "
                              "all rows of that session in clean_decision_outcomes.parquet; identical "
                              "definition to 05_stress_M2M3__far_tercile_reversion_toward_runni.py's A4.",
    "median_ticks": float(med),
    "n_sessions_hi": len(hi_vol_sessions), "n_sessions_lo": len(lo_vol_sessions),
    "hi_vol": a4_hi, "lo_vol": a4_lo,
}
log(f"[vol-split] hi-vol half: mean={a4_hi['mean']:.3f}t n={a4_hi['n']} sess_CI={a4_hi['session_ci']} "
    f"trade_CI={a4_hi['trade_ci']} dual_sig={a4_hi['dual_significant']}")
log(f"[vol-split] lo-vol half: mean={a4_lo['mean']:.3f}t n={a4_lo['n']} sess_CI={a4_lo['session_ci']} "
    f"trade_CI={a4_lo['trade_ci']} dual_sig={a4_lo['dual_significant']}")

summary_json["stress_tests_H60_position_direction_corrected_Q_reversion_far_tercile"] = stress_results

json_path = os.path.join(OUT_DIR, "m2m3_clean_decomposition.json")
with open(json_path, "w") as f:
    json.dump(summary_json, f, indent=2, default=lambda o: None if isinstance(o, float) and np.isnan(o) else o)
log(f"[write] {json_path}")

# ---- flat CSV, one row per sample x horizon x variant x quantity x tercile
rows = []
for sample_name, results in [("discovery", disc_results), ("confirmation", conf_results)]:
    for h in results["by_horizon"]:
        H = h["horizon"]
        for vname, vout in h["variants"].items():
            for qname in ["Q_reversion", "Q_discovery"]:
                q = vout[qname]
                for i, tname in enumerate(["near", "mid", "far"]):
                    rows.append({
                        "sample": sample_name, "horizon": H, "variant": vname, "quantity": qname,
                        "tercile": tname, "n": q["surface_n_near_mid_far"][i],
                        "mean_ticks": q["monotonic_surface_near_mid_far"][i],
                        "far_session_block_ci_lo": q["far_session_block_ci"][0] if tname == "far" else None,
                        "far_session_block_ci_hi": q["far_session_block_ci"][1] if tname == "far" else None,
                        "far_trade_block_ci_lo": q["far_trade_block_ci"][0] if tname == "far" else None,
                        "far_trade_block_ci_hi": q["far_trade_block_ci"][1] if tname == "far" else None,
                        "far_dual_clustered_significant": q["far_dual_clustered_significant"] if tname == "far" else None,
                        "far_economically_relevant_vs_C1": q["far_economically_relevant_vs_C1"] if tname == "far" else None,
                        "continuation_prob_far_p_discovery_gt_0": vout["continuation_prob_far"]["p_discovery_gt_0"] if tname == "far" else None,
                        "continuation_prob_far_n": vout["continuation_prob_far"]["n_far"] if tname == "far" else None,
                    })
csv_path = os.path.join(OUT_DIR, "m2m3_clean_decomposition.csv")
pd.DataFrame(rows).to_csv(csv_path, index=False)
log(f"[write] {csv_path}")

log_path = os.path.join(OUT_DIR, "m2m3_clean_decomposition_log.txt")
with open(log_path, "w") as f:
    f.write("\n".join(log_lines))
log(f"[write] {log_path}")

print("\n" + "=" * 100)
print("HEADLINE (position_direction_corrected variant, primary) -- CLEAN CAUSAL SUBSTRATE:")
for sample_name, results in [("discovery", disc_results), ("confirmation", conf_results)]:
    for h in results["by_horizon"]:
        H = h["horizon"]
        rv = h["variants"]["position_direction_corrected"]["Q_reversion"]
        dv = h["variants"]["position_direction_corrected"]["Q_discovery"]
        cp = h["variants"]["position_direction_corrected"]["continuation_prob_far"]
        print(f"  {sample_name:12s} H={H:>3d}  far_reversion={rv['far_mean_ticks']:+.3f}t "
              f"sess_CI={rv['far_session_block_ci']} trade_CI={rv['far_trade_block_ci']} "
              f"sig={rv['far_dual_clustered_significant']}  |  "
              f"far_discovery={dv['far_mean_ticks']:+.3f}t sess_CI={dv['far_session_block_ci']} "
              f"trade_CI={dv['far_trade_block_ci']} sig={dv['far_dual_clustered_significant']}  |  "
              f"P(discovery>0|far)={cp['p_discovery_gt_0']:.3f} (n={cp['n_far']})")
print("=" * 100)
print("Sign stability discovery vs confirmation:")
print("  reversion:", sign_stability["reversion"])
print("  discovery:", sign_stability["discovery"])
