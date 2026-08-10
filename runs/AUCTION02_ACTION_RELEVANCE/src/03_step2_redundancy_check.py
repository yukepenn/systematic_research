"""AUCTION02 -- Step 2 (redundancy sub-question): is Auction state (value_dist_ticks / poc_share)
REDUNDANT with U6B's own quality state (htf_agree_code_local / vote_dispersion_aligned), or
incrementally informative on top of it, at Product-A scale-up bars? Per the directive: do NOT
tune U6B itself -- VOTE_THRESH is reproduced exactly as U6B's own spec.yaml/01_construct_and_
validate.py defines it (top-tercile cutoff of vote_dispersion_aligned over the FULL canonical
ENTRY+SCALE_IN population, fixed once, never re-derived on our smaller tick-covered subset).
"""
import os, sys, json
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

sys.path.insert(0, os.path.dirname(__file__))
from stats_lib_auction02 import ols_r2

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
U0_PATH = os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet")
OUT = os.path.join(ROOT, "runs", "AUCTION02_ACTION_RELEVANCE", "out")
RNG = np.random.default_rng(20260809)
NBOOT = 1000

# ---------------------------------------------------------------- reproduce U6B's VOTE_THRESH
# EXACTLY (byte-identical population/definition to U6B/src/01_construct_and_validate.py) -- this
# is a REPRODUCTION for redundancy-testing purposes, not a re-derivation; U6B itself is not tuned.
u0 = pd.read_parquet(U0_PATH, columns=["sess_date", "is_health_only_bar", "action_A",
                                        "target_exposure_A", "HTF_tilt_state", "vote_dispersion"])
canon_events = u0[(~u0["is_health_only_bar"]) & (u0["action_A"].isin(["ENTRY", "SCALE_IN"]))]
change_sign_full = np.sign(canon_events["target_exposure_A"].to_numpy())
vd_aligned_full = canon_events["vote_dispersion"].to_numpy() * change_sign_full
VOTE_THRESH = float(np.quantile(vd_aligned_full, 2.0 / 3.0))
print(f"[step2] reproduced VOTE_THRESH={VOTE_THRESH} on n={len(canon_events)} canonical ENTRY+SCALE_IN "
      f"bars (U6B's own reported value: 6.0)", flush=True)
assert abs(VOTE_THRESH - 6.0) < 1e-6, "VOTE_THRESH reproduction must match U6B's own reported constant exactly"

# ---------------------------------------------------------------- our 37-session, RTH+liquid,
# tick-covered scale-up bars
df = pd.read_parquet(os.path.join(OUT, "action_substrate.parquet"))
ok = df[df["analysis_ok"]].copy()
scaleup_all_indirection = df[df["action_A"].isin(["ENTRY", "SCALE_IN"])]
scaleup = ok[ok["action_A"].isin(["ENTRY", "SCALE_IN"])].copy()
print(f"[step2] scale-up bars: {len(scaleup_all_indirection)} in the 37-session in-direction universe, "
      f"{len(scaleup)} survive RTH+liquid+matched (analysis_ok) -- trades={scaleup['block_id_A'].nunique()}, "
      f"sessions={scaleup['sess_tag'].nunique()}", flush=True)

change_sign = np.sign(scaleup["target_exposure_A"].to_numpy())
scaleup["change_sign"] = change_sign
scaleup["htf_agree_code_local"] = scaleup["HTF_tilt_state"].to_numpy() * change_sign
scaleup["vote_dispersion_aligned"] = scaleup["vote_dispersion"].to_numpy() * change_sign
scaleup["quality_high_u6b"] = ((scaleup["htf_agree_code_local"] == 1) |
                                (scaleup["vote_dispersion_aligned"] >= VOTE_THRESH)).astype(int)
frac_quality_low = float((scaleup["quality_high_u6b"] == 0).mean())
print(f"[step2] on this 37-session scale-up subset: quality_high_u6b rate={1-frac_quality_low:.4f} "
      f"(quality-low rate={frac_quality_low:.4f}; U6B's own full-canonical-population rate was 70.4% high / 29.6% low)",
      flush=True)

results = {"vote_thresh_reproduced": VOTE_THRESH,
           "n_scaleup_indirection_universe": int(len(scaleup_all_indirection)),
           "n_scaleup_analysis_ok": int(len(scaleup)),
           "n_trades": int(scaleup["block_id_A"].nunique()), "n_sessions": int(scaleup["sess_tag"].nunique()),
           "quality_high_rate": float(1 - frac_quality_low)}

# ---------------------------------------------------------------- redundancy: correlation between
# Auction state and U6B's quality state at scale-up bars
redund = {}
for pred in ["abs_value_dist_ticks", "poc_share"]:
    r_bin, p_bin = spearmanr(scaleup[pred], scaleup["quality_high_u6b"])
    r_cont, p_cont = spearmanr(scaleup[pred], scaleup["vote_dispersion_aligned"])
    redund[pred] = {"spearman_vs_quality_high_binary": float(r_bin), "p_naive": float(p_bin),
                     "spearman_vs_vote_dispersion_aligned_continuous": float(r_cont)}
    print(f"[step2] redundancy: {pred} vs quality_high_u6b: rho={r_bin:.4f} (p={p_bin:.4f}); "
          f"vs vote_dispersion_aligned (continuous): rho={r_cont:.4f}", flush=True)
results["redundancy_correlation"] = redund

# ---------------------------------------------------------------- incremental value: does
# value_dist_ticks_abs add anything to signed_markout_H beyond quality_high_u6b alone?
incr = {}
for H in [1, 3, 20]:
    ycol = f"signed_markout_{H}_A"
    sub = scaleup.dropna(subset=[ycol, "abs_value_dist_ticks", "quality_high_u6b"])
    r2_base, coef_base, n_base = ols_r2(sub, ["quality_high_u6b"], ycol)
    r2_ext, coef_ext, n_ext = ols_r2(sub, ["quality_high_u6b", "abs_value_dist_ticks"], ycol)
    delta = r2_ext - r2_base
    # reverse direction: does U6B quality add anything beyond Auction alone?
    r2_base2, _, _ = ols_r2(sub, ["abs_value_dist_ticks"], ycol)
    delta_reverse = r2_ext - r2_base2

    # session-block bootstrap on the value_dist_ticks_abs coefficient in the extended model
    sessions = sub["sess_tag"].unique()
    by_sess = {s: g for s, g in sub.groupby("sess_tag")}
    boots = []
    for _ in range(NBOOT):
        pick = RNG.choice(sessions, size=len(sessions), replace=True)
        parts = [by_sess[s] for s in pick if s in by_sess]
        if not parts:
            continue
        bs = pd.concat(parts, ignore_index=True)
        if len(bs) < 10:
            continue
        _, coef_b, _ = ols_r2(bs, ["quality_high_u6b", "abs_value_dist_ticks"], ycol)
        boots.append(coef_b[-1])
    lo, hi = (np.percentile(boots, [2.5, 97.5]) if boots else (np.nan, np.nan))

    incr[f"H{H}"] = {"n": n_ext, "r2_quality_only": r2_base, "r2_quality_plus_auction": r2_ext,
                      "delta_r2_auction_on_top_of_quality": delta,
                      "delta_r2_quality_on_top_of_auction": delta_reverse,
                      "auction_coef_in_extended_model": float(coef_ext[-1]),
                      "auction_coef_session_block_CI": [float(lo), float(hi)]}
    print(f"[step2] H={H}: n={n_ext} R2(quality only)={r2_base:.5f} R2(quality+auction)={r2_ext:.5f} "
          f"dR2(auction|quality)={delta:+.5f} dR2(quality|auction)={delta_reverse:+.5f} "
          f"auction_coef={coef_ext[-1]:.4f} sessCI={[lo,hi]}", flush=True)
results["incremental_value"] = incr

with open(os.path.join(OUT, "step2_redundancy_results.json"), "w") as f:
    json.dump(results, f, indent=2, default=float)
print("\nSTEP2 REDUNDANCY CHECK DONE")
