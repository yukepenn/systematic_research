"""AUCTION02 -- Step 4: small combination-discovery sandbox, discovery-set only. Per sec17: max
2-way interactions, using only STATE_INFORMATION_LIBRARY.csv states already marked
reusable_as_state or reusable_for_interaction in {YES,MAYBE}, simple linear-interaction OLS +
Delta-R^2 (COMBO01's own b3 methodology), at most 2 candidates tested here (not "hundreds of
pairwise tests"), motivated directly by Step 1 (real signed value_dist_ticks effect) and Step 2
(value_dist_ticks NOT redundant with U6B's quality state; incremental dR2=+0.075 at H=20 on
Product-A scale-up bars).

Candidate 1: Auction(far tercile) x U6B quality-state(low) on Product-A scale-up subsequent
  20-bar markout -- directly motivated by Step 2's own incremental-value finding.
Candidate 2: Auction(far tercile) x |M|-magnitude(strong tercile, structural incumbent state) on
  the broader Product-A/B in-direction signed_markout -- tests whether Step 1's core effect is
  conviction-dependent.
"""
import os, sys, json
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from stats_lib_auction02 import ols_r2, dual_block_bootstrap_meandiff

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(ROOT, "runs", "AUCTION02_ACTION_RELEVANCE", "out")
RNG = np.random.default_rng(20260809)
NBOOT = 1000

df = pd.read_parquet(os.path.join(OUT, "action_substrate.parquet"))
ok = df[df["analysis_ok"]].copy()
results = {}


def interaction_cell(sub, dummy1, dummy2, ycol, sess_col, label):
    s = sub.dropna(subset=[dummy1, dummy2, ycol]).copy()
    s["_inter"] = s[dummy1] * s[dummy2]
    r2_add, coef_add, n = ols_r2(s, [dummy1, dummy2], ycol)
    r2_int, coef_int, _ = ols_r2(s, [dummy1, dummy2, "_inter"], ycol)
    delta = r2_int - r2_add
    b3 = float(coef_int[-1])

    sessions = s[sess_col].unique()
    codes, uniques = pd.factorize(s[sess_col].to_numpy())
    idx_by_group = [np.where(codes == g)[0] for g in range(len(uniques))]
    boots = np.full(NBOOT, np.nan)
    arr = s[[dummy1, dummy2, "_inter", ycol]].to_numpy(dtype=float)
    for b in range(NBOOT):
        picks = RNG.integers(0, len(uniques), size=len(uniques))
        idx = np.concatenate([idx_by_group[g] for g in picks])
        if len(idx) < 10:
            continue
        X = np.column_stack([np.ones(len(idx)), arr[idx, 0], arr[idx, 1], arr[idx, 2]])
        y = arr[idx, 3]
        try:
            coef, *_ = np.linalg.lstsq(X, y, rcond=None)
            boots[b] = coef[-1]
        except Exception:
            continue
    boots = boots[~np.isnan(boots)]
    lo, hi = (np.percentile(boots, [2.5, 97.5]) if len(boots) else (np.nan, np.nan))

    cell = {"label": label, "n": n, "n_sessions": len(sessions), "r2_additive": r2_add,
            "r2_interaction": r2_int, "delta_r2": delta, "b3_interaction_coef": b3,
            "b3_session_block_CI": [float(lo), float(hi)]}
    print(f"[step4] {label}: n={n} sessions={len(sessions)} R2_add={r2_add:.5f} "
          f"R2_int={r2_int:.5f} dR2={delta:+.5f} b3={b3:.4f} sessCI={[lo,hi]}", flush=True)
    return cell


# ============================================================= Candidate 1: Auction x U6B-quality
# on Product-A scale-up bars (motivated by Step 2's dR2(auction|quality)=+0.075 at H=20)
u0 = pd.read_parquet(os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet"),
                      columns=["sess_date", "is_health_only_bar", "action_A", "target_exposure_A", "vote_dispersion"])
canon_events = u0[(~u0["is_health_only_bar"]) & (u0["action_A"].isin(["ENTRY", "SCALE_IN"]))]
VOTE_THRESH = float(np.quantile(canon_events["vote_dispersion"].to_numpy() *
                                 np.sign(canon_events["target_exposure_A"].to_numpy()), 2.0 / 3.0))
assert abs(VOTE_THRESH - 6.0) < 1e-6

scaleup = ok[ok["action_A"].isin(["ENTRY", "SCALE_IN"])].copy()
change_sign = np.sign(scaleup["target_exposure_A"].to_numpy())
scaleup["htf_agree_code_local"] = scaleup["HTF_tilt_state"].to_numpy() * change_sign
scaleup["vote_dispersion_aligned"] = scaleup["vote_dispersion"].to_numpy() * change_sign
scaleup["quality_high_u6b"] = ((scaleup["htf_agree_code_local"] == 1) |
                                (scaleup["vote_dispersion_aligned"] >= VOTE_THRESH)).astype(int)
scaleup["quality_low_dummy"] = 1 - scaleup["quality_high_u6b"]
vd_cuts = scaleup["abs_value_dist_ticks"].quantile([1/3, 2/3]).tolist()
scaleup["auction_far_dummy"] = (scaleup["abs_value_dist_ticks"] >= vd_cuts[1]).astype(int)

results["candidate1_auction_x_u6b_quality"] = {
    "n_scaleup_bars": len(scaleup), "n_trades": int(scaleup["block_id_A"].nunique()),
    "n_sessions": int(scaleup["sess_tag"].nunique()), "vd_far_cut": vd_cuts[1],
    "cells": [
        interaction_cell(scaleup, "auction_far_dummy", "quality_low_dummy", f"signed_markout_{H}_A",
                          "sess_tag", f"candidate1_H{H}")
        for H in [3, 20]
    ],
}

# ============================================================= Candidate 2: Auction x |M|-magnitude
# (structural incumbent state) on the broader in-direction samples, both products
for prod, dir_col, m_col, trade_col in [("A", "target_exposure_A", "M_A_raw", "block_id_A"),
                                          ("B", "position_B", "M", "block_id_B")]:
    sub = ok[ok[dir_col] != 0].copy()
    sub["m_abs"] = sub[m_col].abs()
    vd_cuts2 = sub["abs_value_dist_ticks"].quantile([1/3, 2/3]).tolist()
    m_cuts = sub["m_abs"].quantile([1/3, 2/3]).tolist()
    sub["auction_far_dummy"] = (sub["abs_value_dist_ticks"] >= vd_cuts2[1]).astype(int)
    sub["m_strong_dummy"] = (sub["m_abs"] >= m_cuts[1]).astype(int)
    cells = [interaction_cell(sub, "auction_far_dummy", "m_strong_dummy", f"signed_markout_{H}_{prod}",
                               "sess_tag", f"candidate2_{prod}_H{H}") for H in [3, 20]]
    results[f"candidate2_auction_x_Mmagnitude_{prod}"] = {
        "n": len(sub), "vd_far_cut": vd_cuts2[1], "m_strong_cut": m_cuts[1], "cells": cells,
    }

with open(os.path.join(OUT, "step4_results.json"), "w") as f:
    json.dump(results, f, indent=2, default=float)
print("\nSTEP4 COMBINATION SANDBOX DONE")
