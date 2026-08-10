"""AUCTION03 mechanism decomposition, part 3 -- STEP A candidate screen.

Implements 3 of the 4 candidate "new-value acceptance" concepts (a, b, d;
c -- persistence -- is skipped, 2 is the task's stated minimum and three
gives a more informed Step B selection) on a 7-session subset spread across
the full date range, disclosed here BEFORE any candidate is computed or any
outcome/return data is looked at:

    SCREEN_SUBSET = 20250814, 20250910, 20251009, 20251117, 20260123,
                    20260317, 20260520   (all discovery-set, span Aug'25..May'26)

Also cross-checks this script's own from-scratch causal running-POC / 1s
value_dist_ticks reconstruction against AUCTION01's already-published
poc_1s_full.parquet for these 7 sessions (a correctness gate on the shared
groundwork before trusting any candidate built on top of it).

Selection (Step B) is done by a human-readable reading of this diagnostics
JSON against three criteria ONLY: economic clarity, data quality (coverage /
no NaN-inf blowup / no near-constant degeneracy), reasonable distributional
behavior. No outcome/return column is read anywhere in this script.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from acceptance_lib import (
    ROOT, TICK, WINDOW_S, SCREEN_SUBSET,
    build_base_session,
    candidate_a_excursion_side_share,
    candidate_b_near_price_acceptance,
    candidate_d_local_value_divergence,
)

OUT = os.path.join(ROOT, "runs", "AUCTION03_MECHANISM_DECOMPOSITION", "out")
os.makedirs(OUT, exist_ok=True)

AUCTION01_POC = os.path.join(ROOT, "runs", "AUCTION01_VALUE_STATE", "out", "poc_1s_full.parquet")


def describe(arr: np.ndarray) -> dict:
    arr = np.asarray(arr, dtype=np.float64)
    n = arr.size
    finite = np.isfinite(arr)
    n_finite = int(finite.sum())
    n_nan = int(np.isnan(arr).sum())
    n_inf = int(np.isinf(arr).sum())
    d = {
        "n": n, "n_finite": n_finite, "n_nan": n_nan, "n_inf": n_inf,
        "coverage": n_finite / n if n else float("nan"),
    }
    if n_finite > 0:
        v = arr[finite]
        d.update({
            "mean": float(np.mean(v)), "std": float(np.std(v)),
            "min": float(np.min(v)), "p01": float(np.percentile(v, 1)),
            "p25": float(np.percentile(v, 25)), "p50": float(np.percentile(v, 50)),
            "p75": float(np.percentile(v, 75)), "p99": float(np.percentile(v, 99)),
            "max": float(np.max(v)),
        })
    return d


def saturation_check(arr: np.ndarray, lo=0.0, hi=1.0, tol=1e-9) -> dict:
    arr = np.asarray(arr, dtype=np.float64)
    finite = arr[np.isfinite(arr)]
    if finite.size == 0:
        return {"frac_at_lo": float("nan"), "frac_at_hi": float("nan"), "frac_at_bound": float("nan")}
    at_lo = np.mean(np.abs(finite - lo) < tol)
    at_hi = np.mean(np.abs(finite - hi) < tol)
    return {"frac_at_lo": float(at_lo), "frac_at_hi": float(at_hi), "frac_at_bound": float(at_lo + at_hi)}


def main():
    print(f"[screen] STEP A subset (disclosed before any computation): {SCREEN_SUBSET}", flush=True)
    print(f"[screen] window={WINDOW_S}s tick={TICK}", flush=True)

    auction01_poc = pd.read_parquet(AUCTION01_POC, columns=["sess_tag", "time", "poc_price", "value_dist_ticks"])

    results = {"screen_subset": SCREEN_SUBSET, "window_s": WINDOW_S, "sessions": {}}
    a_all, b_all, d_all, absD_all, elapsed_all = [], [], [], [], []
    crosscheck = {}

    for tag in SCREEN_SUBSET:
        base = build_base_session(tag)
        a = candidate_a_excursion_side_share(base)
        b, vol_near_cur, vol_near_poc = candidate_b_near_price_acceptance(base)
        d, vwap60 = candidate_d_local_value_divergence(base)
        absD = np.abs(base["value_dist_ticks_1s"])
        elapsed = np.arange(base["n"]) / max(base["n"] - 1, 1)

        # ---- correctness cross-check vs AUCTION01's own published poc_1s_full
        ref = auction01_poc[auction01_poc.sess_tag == tag].sort_values("time")
        mine = pd.DataFrame({"time": base["idx"], "poc_price": base["poc_price_1s"],
                              "value_dist_ticks": base["value_dist_ticks_1s"]})
        cmp = ref.merge(mine, on="time", suffixes=("_ref", "_mine"), how="inner")
        poc_match = float(np.mean(np.isclose(cmp["poc_price_ref"], cmp["poc_price_mine"], atol=1e-6)))
        vd_match = float(np.mean(np.isclose(cmp["value_dist_ticks_ref"], cmp["value_dist_ticks_mine"],
                                             atol=1e-6, equal_nan=True)))
        crosscheck[tag] = {
            "n_ref_rows": int(len(ref)), "n_mine_rows": int(len(mine)), "n_joined": int(len(cmp)),
            "poc_price_match_frac": poc_match, "value_dist_ticks_match_frac": vd_match,
        }
        print(f"[screen] {tag}: crosscheck vs AUCTION01 poc_1s_full -> n_joined={len(cmp)} "
              f"poc_match={poc_match:.4f} value_dist_match={vd_match:.4f}", flush=True)

        results["sessions"][tag] = {
            "n_1s_rows": base["n"],
            "candidate_a_excursion_side_share": describe(a),
            "candidate_a_saturation": saturation_check(a, 0.0, 1.0),
            "candidate_b_near_price_share": describe(b),
            "candidate_b_saturation": saturation_check(b, 0.0, 1.0),
            "candidate_d_local_value_divergence_ticks": describe(d),
            "crosscheck_vs_auction01": crosscheck[tag],
        }
        a_all.append(a); b_all.append(b); d_all.append(d)
        absD_all.append(absD); elapsed_all.append(elapsed)
        del base

    a_all = np.concatenate(a_all); b_all = np.concatenate(b_all); d_all = np.concatenate(d_all)
    absD_all = np.concatenate(absD_all); elapsed_all = np.concatenate(elapsed_all)
    results["pooled_7session"] = {
        "candidate_a_excursion_side_share": describe(a_all),
        "candidate_a_saturation": saturation_check(a_all, 0.0, 1.0),
        "candidate_b_near_price_share": describe(b_all),
        "candidate_b_saturation": saturation_check(b_all, 0.0, 1.0),
        "candidate_d_local_value_divergence_ticks": describe(d_all),
    }
    finite_mask = np.isfinite(a_all) & np.isfinite(b_all) & np.isfinite(d_all)
    results["pooled_7session"]["pairwise_corr"] = {
        "a_vs_b": float(np.corrcoef(a_all[finite_mask], b_all[finite_mask])[0, 1]),
        "a_vs_d": float(np.corrcoef(a_all[finite_mask], d_all[finite_mask])[0, 1]),
        "b_vs_d": float(np.corrcoef(b_all[finite_mask], d_all[finite_mask])[0, 1]),
        "n_finite_all_three": int(finite_mask.sum()),
    }
    # Degeneracy check: is each candidate just a proxy for |D_t| (already-
    # existing value_dist_ticks) or for raw elapsed session time, rather than
    # adding information AT a given D_t / time? (No outcome/return data used.)
    fa = np.isfinite(a_all); fb = np.isfinite(b_all); fd = np.isfinite(d_all)
    results["pooled_7session"]["degeneracy_vs_existing_state"] = {
        "corr_a_vs_absD": float(np.corrcoef(a_all[fa], absD_all[fa])[0, 1]),
        "corr_b_vs_absD": float(np.corrcoef(b_all[fb], absD_all[fb])[0, 1]),
        "corr_d_vs_absD": float(np.corrcoef(d_all[fd], absD_all[fd])[0, 1]),
        "corr_a_vs_elapsed_session_time": float(np.corrcoef(a_all[fa], elapsed_all[fa])[0, 1]),
        "corr_b_vs_elapsed_session_time": float(np.corrcoef(b_all[fb], elapsed_all[fb])[0, 1]),
        "corr_d_vs_elapsed_session_time": float(np.corrcoef(d_all[fd], elapsed_all[fd])[0, 1]),
    }

    out_path = os.path.join(OUT, "step_a_candidate_screen.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[screen] wrote {out_path}", flush=True)
    print("SCREEN DONE", flush=True)


if __name__ == "__main__":
    main()
