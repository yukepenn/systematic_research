"""AUCTION03 mechanism decomposition, part 3 -- STEP C full build.

STEP B SELECTION (decided from runs/AUCTION03_MECHANISM_DECOMPOSITION/out/
step_a_candidate_screen.json -- economic clarity, data quality, distributional
behavior ONLY; no outcome/return data was read at any point before this
selection was made):

  PRIMARY     = candidate (b): near-current-price volume acceptance share
                accept_primary = vol_near_cur / (vol_near_cur + vol_near_poc),
                trailing 60s, +/-2 ticks, both bands.
  SENSITIVITY = candidate (a): excursion-side recent volume share
                accept_sensitivity = trailing-60s volume share on the same
                side of the running POC as the current excursion sign(D_t).

  REJECTED: candidate (d) [trailing-60s-VWAP-vs-full-POC divergence, sign-
  matched] -- Step A's own degeneracy check (corr vs |value_dist_ticks|,
  computed WITHOUT looking at any outcome data) found corr=0.998 pooled over
  the 7-session screen subset: candidate (d) is essentially a deterministic
  linear function of information ALREADY published in poc_1s_full.parquet's
  own value_dist_ticks column, so it would add ~no new information. It is
  also unbounded/heavy-right-tailed (pooled mean 184 ticks, p99 992 ticks),
  unlike (a)/(b) which are bounded [0,1] shares -- a real economic-clarity
  weakness (not comparable across sessions/excursion sizes the way a ratio is).

  (a) and (b) both show real, non-degenerate coverage and only modest
  correlation with |D_t| (0.20 / 0.25 respectively -- genuinely adding
  information beyond the existing distance-from-POC state) and are both
  bounded [0,1] with a clean, directly-motivated economic reading ("what
  share of trailing 60s volume is transacting near/with the new price").
  (b) has materially better coverage (99.997% vs 99.4% finite) and slightly
  less ceiling-saturation (87.4% vs 89.5% of rows at exactly 1.0) than (a),
  and matches the task's own motivating language ("are people transacting
  near the new prices") most directly, so (b) is PRIMARY and (a) -- a
  related but structurally different trailing-volume-share operationalization
  (side-of-POC classification instead of distance-band classification) --
  is SENSITIVITY, giving a genuine, non-trivial robustness pairing.

  DISCLOSED LIMITATION (both a and b): each candidate's distribution has a
  substantial ceiling mass (~87-90% of rows exactly at 1.0). This is
  economically real, not literally degenerate (both stay under the task's
  95% saturation disqualifier and retain a genuinely informative bottom-
  quartile spread down to ~0), but it means the *discriminating* power of
  either feature is concentrated in the minority of rows where the feature
  reads meaningfully below 1.0 -- exactly the "rejected excursion, not yet
  accepted" cases this feature family is meant to isolate.

Applies the exact definitions above (no changes) to all 45 permitted
sessions (37 discovery + 8 confirmation). Writes
out/acceptance_features.parquet [sess_tag, time, accept_primary,
accept_sensitivity] and out/acceptance_feature_summary.json.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from acceptance_lib import (
    ROOT, TICK, WINDOW_S, DISCOVERY, CONFIRMATION, SCREEN_SUBSET,
    build_base_session,
    candidate_a_excursion_side_share,
    candidate_b_near_price_acceptance,
)

OUT = os.path.join(ROOT, "runs", "AUCTION03_MECHANISM_DECOMPOSITION", "out")
os.makedirs(OUT, exist_ok=True)

AUCTION01_POC = os.path.join(ROOT, "runs", "AUCTION01_VALUE_STATE", "out", "poc_1s_full.parquet")
CONFIRM_POC = os.path.join(ROOT, "runs", "W5_PROTECTED_CONFIRMATION", "results", "out",
                            "poc_1s_full_CONFIRM.parquet")


def describe(arr: np.ndarray) -> dict:
    arr = np.asarray(arr, dtype=np.float64)
    n = arr.size
    finite = np.isfinite(arr)
    n_finite = int(finite.sum())
    d = {"n": n, "n_finite": n_finite, "coverage": n_finite / n if n else float("nan")}
    if n_finite > 0:
        v = arr[finite]
        d.update({
            "mean": float(np.mean(v)), "std": float(np.std(v)),
            "p01": float(np.percentile(v, 1)), "p25": float(np.percentile(v, 25)),
            "p50": float(np.percentile(v, 50)), "p75": float(np.percentile(v, 75)),
            "p99": float(np.percentile(v, 99)),
            "frac_at_1": float(np.mean(np.abs(v - 1.0) < 1e-9)),
            "frac_at_0": float(np.mean(np.abs(v) < 1e-9)),
        })
    return d


def main():
    all_tags = DISCOVERY + CONFIRMATION
    print(f"[build] {len(all_tags)} sessions total: {len(DISCOVERY)} discovery + {len(CONFIRMATION)} confirmation",
          flush=True)

    poc_ref_discovery = pd.read_parquet(AUCTION01_POC, columns=["sess_tag", "time", "poc_price", "value_dist_ticks"])
    poc_ref_confirm = pd.read_parquet(CONFIRM_POC, columns=["sess_tag", "time", "poc_price", "value_dist_ticks"])

    rows_all = []
    session_diag = {}
    confirm_sessions_included = []

    for tag in all_tags:
        is_confirm = tag in CONFIRMATION
        base = build_base_session(tag)
        a = candidate_a_excursion_side_share(base)
        b, vol_near_cur, vol_near_poc = candidate_b_near_price_acceptance(base)

        df = pd.DataFrame({
            "sess_tag": tag, "time": base["idx"],
            "accept_primary": b, "accept_sensitivity": a,
        })
        rows_all.append(df)

        # correctness crosscheck vs already-published poc_1s_full / poc_1s_full_CONFIRM
        ref = (poc_ref_confirm if is_confirm else poc_ref_discovery)
        ref = ref[ref.sess_tag == tag].sort_values("time")
        mine = pd.DataFrame({"time": base["idx"], "poc_price": base["poc_price_1s"],
                              "value_dist_ticks": base["value_dist_ticks_1s"]})
        cmp = ref.merge(mine, on="time", suffixes=("_ref", "_mine"), how="inner")
        if len(cmp) > 0:
            poc_match = float(np.mean(np.isclose(cmp["poc_price_ref"], cmp["poc_price_mine"], atol=1e-6)))
            vd_match = float(np.mean(np.isclose(cmp["value_dist_ticks_ref"], cmp["value_dist_ticks_mine"],
                                                 atol=1e-6, equal_nan=True)))
        else:
            poc_match, vd_match = float("nan"), float("nan")

        session_diag[tag] = {
            "is_confirmation": is_confirm, "n_1s_rows": base["n"],
            "n_crosscheck_joined": int(len(cmp)),
            "poc_price_match_frac": poc_match, "value_dist_ticks_match_frac": vd_match,
            "accept_primary": describe(b), "accept_sensitivity": describe(a),
        }
        if is_confirm:
            confirm_sessions_included.append(tag)
        print(f"[build] {tag} ({'CONFIRM' if is_confirm else 'discovery'}): {base['n']} rows, "
              f"crosscheck n={len(cmp)} poc_match={poc_match:.4f} vd_match={vd_match:.4f}, "
              f"primary coverage={session_diag[tag]['accept_primary']['coverage']:.4f} "
              f"sensitivity coverage={session_diag[tag]['accept_sensitivity']['coverage']:.4f}", flush=True)
        del base

    full = pd.concat(rows_all, ignore_index=True)
    out_path = os.path.join(OUT, "acceptance_features.parquet")
    full.to_parquet(out_path, compression="zstd", index=False)
    print(f"[build] wrote {out_path}: {len(full)} rows, {full['sess_tag'].nunique()} sessions", flush=True)

    # ---------------------------------------------------------------- pooled summary, DISCOVERY vs CONFIRMATION kept separate
    disc = full[full.sess_tag.isin(DISCOVERY)]
    conf = full[full.sess_tag.isin(CONFIRMATION)]

    summary = {
        "window_s": WINDOW_S, "tick_size": TICK, "band_ticks": 2,
        "primary_definition": (
            "accept_primary = vol_near_cur / (vol_near_cur + vol_near_poc); "
            "vol_near_cur/vol_near_poc = trailing-60s volume within +/-2 ticks of the "
            "current price / running-POC price respectively (candidate b, near-current-price "
            "volume acceptance). Bounded [0,1]; >0.5 = more recent transacting near the new "
            "price than near the old value area."
        ),
        "sensitivity_definition": (
            "accept_sensitivity = trailing-60s volume share on the same side of the running "
            "POC as the current excursion sign(D_t) = sign(value_dist_ticks) (candidate a, "
            "excursion-side recent volume share). NaN when D_t==0 (no excursion)."
        ),
        "rejected_candidate": (
            "candidate d (trailing-60s-VWAP-vs-full-session-POC divergence, sign-matched) "
            "rejected at Step B: corr=0.998 with |value_dist_ticks| in the Step A screen -- "
            "near-collinear with information already in poc_1s_full.parquet, adds ~no new "
            "content; also unbounded/heavy-tailed (mean 184 ticks, p99 992 ticks) unlike the "
            "bounded [0,1] shares (a)/(b)."
        ),
        "screen_subset_step_a": SCREEN_SUBSET,
        "sessions": {
            "discovery_n": len(DISCOVERY), "discovery_tags": DISCOVERY,
            "confirmation_n": len(CONFIRMATION), "confirmation_tags": CONFIRMATION,
            "confirmation_sessions_included": confirm_sessions_included,
            "confirmation_sessions_without_usable_rth_bbo": ["20251125", "20260512"],
            "note": ("Both BBO-less confirmation sessions ARE included in this parquet: "
                     "trade-tick (Last-print) acceptance construction does not require BBO. "
                     "They will simply be absent from any downstream join against "
                     "decision_outcomes_CONFIRM.parquet (which excludes them for BBO reasons), "
                     "same as poc_1s_full_CONFIRM.parquet already does."),
        },
        "row_counts": {"total": int(len(full)), "discovery": int(len(disc)), "confirmation": int(len(conf))},
        "discovery_sample": {
            "accept_primary": describe(disc["accept_primary"].values),
            "accept_sensitivity": describe(disc["accept_sensitivity"].values),
        },
        "confirmation_sample_INTERNAL_PROTECTED_NOT_FORWARD_OOS": {
            "accept_primary": describe(conf["accept_primary"].values),
            "accept_sensitivity": describe(conf["accept_sensitivity"].values),
        },
        "per_session_diagnostics": session_diag,
        "economic_relevance_floor_note": (
            "This task is pure feature construction (no outcome/markout tested). "
            "accept_primary/accept_sensitivity are bounded [0,1] volume-shares, not a "
            "tick-denominated statistic, so the campaign's C1=2.872-ticks round-trip cost "
            "hurdle does not apply directly to the feature itself. It becomes relevant only "
            "once this feature is regressed against forward markouts (H in {15s,60s,300s} or "
            "{1,3,20} bars) in a follow-on step -- at that point any effect must be "
            "contextualized against the 2.872-tick hurdle before being called economically "
            "interesting, per this campaign's standing convention."
        ),
        "no_outcome_data_used": True,
        "significance_testing_performed": False,
    }

    summary_path = os.path.join(OUT, "acceptance_feature_summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"[build] wrote {summary_path}", flush=True)
    print("BUILD DONE", flush=True)


if __name__ == "__main__":
    main()
