"""AUCTION03 -- mechanism decomposition, part 1: signed value-reversion vs signed value-discovery.

Question (never tested before): does distance from the running POC (`value_dist_ticks`, signed)
predict subsequent price REVERSION back toward value, or CONTINUATION/DISCOVERY further away from
value? AUCTION01's D4 only established that |value_dist| and poc_share predict subsequent ABSOLUTE
expansion magnitude (direction-agnostic) -- this pass disambiguates direction.

GOVERNANCE: reads ONLY the two already-built decision_outcomes parquets named in the task (no
regeneration, no new raw/grid1s/sechilo touch, no session outside the two explicitly-provided
lists). DISCOVERY sample is explicitly filtered to the 37 listed sess_tags (dropping anything else
present in the raw file, and reporting any listed date NOT found in the file rather than
inventing/forcing it in). CONFIRMATION sample is explicitly filtered to the 8 listed sess_tags
(file naturally yields 6 -- 20251125/20260512 have no usable RTH BBO and are already absent from
the source parquet, matching the task's own note).

*** CONSTRUCTION CAVEAT FOUND AND CORRECTED BEFORE REPORTING (same "too-good-to-be-true" catch-and
-disclose discipline as AUCTION01's own 4x units-bug fix -- see that REPORT.md) ***
`signed_markout_H` in decision_outcomes.parquet is NOT the raw signed price change. Per
AUCTION01/src/03_diagnostics.py line ~66-68, it is built as
    side = sign(position_B);  signed_markout_H = side * (mid(t+H) - mid_last_t) / TICK
i.e. it is already signed by the INCUMBENT POSITION's direction (a column built for AUCTION01's D6
diagnostic, "POC migration x incumbent direction"), not by raw price direction. It is NaN whenever
position_B==0 (flat), which drops ~39% of all decision points from ANY analysis that uses this
column, regardless of what predicate is applied to it -- a real, disclosed, data-availability
limitation of this file that cannot be worked around without re-reading poc_1s_full.parquet, which
is out of scope (task specifies exactly two input files).

Naively plugging this column into the task's literal formula
    Q_reversion = -sign(D_t) * signed_markout_H ,  Q_discovery = +sign(D_t) * signed_markout_H
computes something that mixes TWO different signs (distance-from-value direction, and the
incumbent's CURRENT position direction) that are empirically correlated in this sample
(corr(sign(value_dist_ticks), sign(position_B)) = +0.382 among position_B!=0 rows -- verified
below). Because side flips row-by-row independent of whether the price itself reverted or
continued, the literal-column quantity can invert sign relative to true price reversion/discovery
purely as a function of which way the incumbent B-system happened to be positioned at that moment
-- NOT what "does distance from value predict price reversion" is actually asking.

This is exactly and only recoverable (algebraically exact, verified below: |signed_markout_H| ==
abs_markout_H whenever position_B!=0) via
    raw_signed_markout_H = signed_markout_H * sign(position_B) == (mid(t+H)-mid_last_t)/TICK
This is pure arithmetic on two already-existing, already-computed columns in the two files named
in the task (no new data, no new predictor, no new horizon, no new threshold -- NOT a "sweep").

Both variants are computed and written in full to the output CSV/JSON for complete transparency.
The CORRECTED (raw-price) variant is treated as primary/canonical throughout this report and in
the structured summary, because it is the one that actually answers the stated question; the
AS-SPECIFIED (literal-column) variant is retained alongside, clearly labeled, as a disclosed
diagnostic showing what the naive read would have produced and by how much it differs.
"""
import os
import json
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
DISCOVERY_PATH = os.path.join(ROOT, "runs", "AUCTION01_VALUE_STATE", "out", "decision_outcomes.parquet")
CONFIRM_PATH = os.path.join(ROOT, "runs", "W5_PROTECTED_CONFIRMATION", "results", "out",
                             "decision_outcomes_CONFIRM.parquet")
OUT_DIR = os.path.join(ROOT, "runs", "AUCTION03_MECHANISM_DECOMPOSITION", "out")
os.makedirs(OUT_DIR, exist_ok=True)

HORIZONS = [15, 60, 300]
NBOOT = 1000
RNG_SEED = 20260810
C1_COST_HURDLE_TICKS = 2.872  # campaign's established round-trip execution-cost hurdle

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
    "governance: nothing >=2026-06-01 may be touched"


# ============================================================= load + explicit-filter
def load_and_filter(path, allowed_dates, label):
    raw = pd.read_parquet(path)
    raw_n, raw_sessions = len(raw), sorted(raw["sess_tag"].unique())
    df = raw[raw["sess_tag"].isin(allowed_dates)].copy()
    kept_sessions = sorted(df["sess_tag"].unique())
    missing_from_file = sorted(set(allowed_dates) - set(kept_sessions))
    extra_in_file_not_in_list = sorted(set(raw_sessions) - set(allowed_dates))
    print(f"[{label}] raw file: {raw_n} rows / {len(raw_sessions)} sessions. "
          f"After explicit filter to the {len(allowed_dates)}-date list: {len(df)} rows / "
          f"{len(kept_sessions)} sessions. Listed dates absent from file: {missing_from_file}. "
          f"Sessions in file but outside the list (dropped): {extra_in_file_not_in_list}.", flush=True)
    df = df.sort_values(["sess_tag", "time"]).reset_index(drop=True)
    return df, {
        "raw_rows": int(raw_n), "raw_sessions": len(raw_sessions),
        "filtered_rows": int(len(df)), "filtered_sessions": len(kept_sessions),
        "listed_dates_absent_from_file": missing_from_file,
        "sessions_in_file_dropped_as_outside_list": extra_in_file_not_in_list,
    }


disc_df, disc_meta = load_and_filter(DISCOVERY_PATH, DISCOVERY_DATES, "discovery")
conf_df, conf_meta = load_and_filter(CONFIRM_PATH, CONFIRMATION_DATES, "confirmation")


# ============================================================= trade-block id
def assign_trade_block(df):
    """Contiguous run of sign(position_B) within a session = one 'trade' clustering unit, matching
    U0's own segment_and_mfe_mae block_id_B convention (change point = sign(position_B) differs
    from previous row), adapted with an explicit forced break at every session boundary since this
    substrate is a sparse 30s-cadence decision-point sample (not U0's dense continuous bar grid) --
    the same kind of disclosed, minimal adaptation AUCTION01/AUCTION02 already made elsewhere in
    this lineage (e.g. first-half/second-half chronological split standing in for year-by-year).
    Computed BEFORE any row is dropped for D_t==0 or outcome-NaN, so a same-signed nonzero episode
    that is interrupted by a flat (position_B==0) stretch is correctly split into two blocks (not
    silently re-merged by later filtering)."""
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
# ---- signed_markout_H is not NaN) before using it anywhere
for name, d in [("discovery", disc_df), ("confirmation", conf_df)]:
    for H in HORIZONS:
        col = f"signed_markout_{H}"
        sub = d.dropna(subset=[col])
        sub = sub[sub["position_B"] != 0]
        if len(sub) == 0:
            continue
        max_diff = float((sub[col].abs() - sub[f"abs_markout_{H}"]).abs().max())
        assert max_diff < 1e-9, f"recovery identity failed {name} H={H}: max_diff={max_diff}"
print("[check] recovery identity |signed_markout_H| == abs_markout_H verified exactly "
      "(wherever position_B!=0) for both samples, all horizons.", flush=True)


# ============================================================= bootstrap helpers (dual-clustered)
def _group_index(keys_arr):
    codes, uniques = pd.factorize(keys_arr)
    return len(uniques), [np.where(codes == g)[0] for g in range(len(uniques))]


def dual_clustered_bootstrap_mean(values, sess_keys, trade_keys, nboot=NBOOT, seed=RNG_SEED):
    """Session-block AND trade-block clustered bootstrap CI on a simple mean. Both must exclude 0
    for "dual-clustered-significant" per this campaign's established bar (AUCTION01 spec.yaml /
    AUCTION02 REPORT.md stats_lib_auction02.dual_block_bootstrap_* pattern)."""
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


# ============================================================= tercile assignment (frozen once
# ============================================================= per sample, reused across horizons)
def assign_terciles(df):
    """|D_t| terciles, fit on ALL rows in the sample with a defined (nonzero) D_t -- i.e. the same
    population D4 itself used (not restricted to position_B!=0), then reused unchanged for every
    horizon's outcome test. Matches this lineage's qcut_frozen 'fit once, reuse' convention."""
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
        # extremely unlikely given continuous tick distances at n in the thousands, but fall back
        # to rank-based equal-count terciles rather than fabricate a threshold
        d["tercile"] = pd.qcut(d["D_t"].abs().rank(method="first"), 3, labels=["near", "mid", "far"])
    return d, n_zero, [float(x) for x in edges]


disc_t, disc_n_zero, disc_edges = assign_terciles(disc_df)
conf_t, conf_n_zero, conf_edges = assign_terciles(conf_df)
print(f"[terciles] discovery: dropped {disc_n_zero} D_t==0 rows, |D_t| tercile edges={disc_edges}",
      flush=True)
print(f"[terciles] confirmation: dropped {conf_n_zero} D_t==0 rows, |D_t| tercile edges={conf_edges}",
      flush=True)


# ============================================================= main per-sample, per-horizon loop
def analyze_sample(d_t, sample_name):
    results = {"sample": sample_name, "n_sessions": int(d_t["sess_tag"].nunique()),
               "n_decision_points_nonzero_D": int(len(d_t)), "by_horizon": []}
    for H in HORIZONS:
        col = f"signed_markout_{H}"
        valid = d_t[col].notna()
        sub = d_t[valid].copy()
        n_dropped_nan_outcome = int((~valid).sum())
        n_dropped_flat_position = int(((d_t["position_B"] == 0) & (~valid)).sum())
        n_dropped_boundary = n_dropped_nan_outcome - n_dropped_flat_position

        side = np.sign(sub["position_B"].to_numpy())
        assert (side != 0).all(), "position_B must be nonzero wherever signed_markout_H is defined"
        sign_D = sub["sign_D"].to_numpy()
        asis = sub[col].to_numpy(dtype=float)               # literal stored column, as specified
        corrected = asis * side                              # recovered raw signed price change (ticks)

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
            # continuation_prob_H = P(sign(D_t)*signed_markout_H > 0 | far tercile) == P(Q_discovery>0|far)
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

# ---- corr(sign(D_t), sign(position_B)) headline number (pooled across horizons is identical per
# ---- sample since it only depends on rows with position_B!=0 & D_t!=0 -- report once per sample
# ---- using H=60 as representative, matching the check computed inline above)
corr_sign_by_sample = {
    "discovery": disc_results["by_horizon"][1]["corr_signD_signPositionB"],
    "confirmation": conf_results["by_horizon"][1]["corr_signD_signPositionB"],
}

# ============================================================= sign-stability discovery vs confirmation
def far_mean(results, H, variant, quantity):
    for h in results["by_horizon"]:
        if h["horizon"] == H:
            return h["variants"][variant][quantity]["far_mean_ticks"]
    return None


def sign_stability_string(quantity, variant="position_direction_corrected"):
    parts = []
    all_same = True
    ref_sign = None
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

# ============================================================= write outputs
summary_json = {
    "spec_note": "AUCTION03 mechanism decomposition part 1: signed value-reversion vs signed "
                 "value-discovery. See module docstring for the signed_markout_H construction "
                 "caveat (position-direction- vs raw-price-signed) that was found and corrected "
                 "before reporting; 'position_direction_corrected' variant is primary/canonical, "
                 "'as_specified' variant is the literal task formula on the stored column, kept "
                 "for full transparency.",
    "c1_cost_hurdle_ticks_roundtrip": C1_COST_HURDLE_TICKS,
    "nboot": NBOOT, "rng_seed": RNG_SEED,
    "governance": {"discovery_filter": disc_meta, "confirmation_filter": conf_meta},
    "tercile_edges_abs_value_dist_ticks": {"discovery": disc_edges, "confirmation": conf_edges},
    "rows_dropped_zero_distance": {"discovery": disc_n_zero, "confirmation": conf_n_zero},
    "corr_signD_signPositionB_by_sample": corr_sign_by_sample,
    "sign_stable_discovery_vs_confirmation": sign_stability,
    "results": {"discovery": disc_results, "confirmation": conf_results},
}
json_path = os.path.join(OUT_DIR, "m2m3_signed_decomposition.json")
with open(json_path, "w") as f:
    json.dump(summary_json, f, indent=2, default=lambda o: None if isinstance(o, float) and np.isnan(o) else o)
print(f"[write] {json_path}", flush=True)

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
csv_path = os.path.join(OUT_DIR, "m2m3_signed_decomposition.csv")
pd.DataFrame(rows).to_csv(csv_path, index=False)
print(f"[write] {csv_path}", flush=True)

print("\n" + "=" * 100)
print("HEADLINE (position_direction_corrected variant, primary):")
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
