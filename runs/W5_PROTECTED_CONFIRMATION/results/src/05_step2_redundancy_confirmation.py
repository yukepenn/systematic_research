"""W5_PROTECTED_CONFIRMATION Family 2, step_b (redundancy replication) + primary endpoint (3).
Byte-identical reuse of runs/AUCTION02_ACTION_RELEVANCE/src/03_step2_redundancy_check.py's
VOTE_THRESH reproduction (from the FULL canonical U0 history -- unrelated to tick data, so this
reproduction is identical to the discovery pass's, asserted ==6.0, never re-derived) and
redundancy-correlation methodology, applied to the 8-session confirmation action_substrate's
Product-A scale-up (ENTRY/SCALE_IN) bars.
"""
import os, json
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
U0_PATH = os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet")
OUT = os.path.join(ROOT, "runs", "W5_PROTECTED_CONFIRMATION", "results", "out")
RNG = np.random.default_rng(20260809)
NBOOT = 1000

# ---------------------------------------------------------------- reproduce U6B's VOTE_THRESH
# EXACTLY (byte-identical to U6B/AUCTION02's own reproduction -- full canonical history, unrelated
# to the tick/BBO protected pool, so this is unchanged from the discovery pass by construction)
u0 = pd.read_parquet(U0_PATH, columns=["sess_date", "is_health_only_bar", "action_A",
                                        "target_exposure_A", "HTF_tilt_state", "vote_dispersion"])
canon_events = u0[(~u0["is_health_only_bar"]) & (u0["action_A"].isin(["ENTRY", "SCALE_IN"]))]
change_sign_full = np.sign(canon_events["target_exposure_A"].to_numpy())
vd_aligned_full = canon_events["vote_dispersion"].to_numpy() * change_sign_full
VOTE_THRESH = float(np.quantile(vd_aligned_full, 2.0 / 3.0))
print(f"[step2-confirm] reproduced VOTE_THRESH={VOTE_THRESH} on n={len(canon_events)} canonical ENTRY+SCALE_IN "
      f"bars (U6B's own reported value: 6.0, frozen, never re-derived on the confirmation pool)", flush=True)
assert abs(VOTE_THRESH - 6.0) < 1e-6, "VOTE_THRESH reproduction must match U6B's own reported constant exactly"

df = pd.read_parquet(os.path.join(OUT, "action_substrate_CONFIRM.parquet"))
ok = df[df["analysis_ok"]].copy()
scaleup_all_indirection = df[df["action_A"].isin(["ENTRY", "SCALE_IN"])]
scaleup = ok[ok["action_A"].isin(["ENTRY", "SCALE_IN"])].copy()
print(f"[step2-confirm] scale-up bars: {len(scaleup_all_indirection)} in the 8-session in-direction universe, "
      f"{len(scaleup)} survive RTH+liquid+matched (analysis_ok) -- trades={scaleup['block_id_A'].nunique()}, "
      f"sessions={scaleup['sess_tag'].nunique()}", flush=True)

results = {"vote_thresh_reproduced": VOTE_THRESH,
           "n_scaleup_indirection_universe": int(len(scaleup_all_indirection)),
           "n_scaleup_analysis_ok": int(len(scaleup)),
           "n_trades": int(scaleup["block_id_A"].nunique()) if len(scaleup) else 0,
           "n_sessions": int(scaleup["sess_tag"].nunique()) if len(scaleup) else 0}

if len(scaleup) < 10:
    print(f"[step2-confirm] n={len(scaleup)} scale-up analysis_ok bars -- too small for a "
          f"meaningful redundancy/incremental-value test; reporting the count honestly, not "
          f"forcing a correlation.", flush=True)
    results["redundancy_correlation"] = None
    results["incremental_value"] = None
else:
    change_sign = np.sign(scaleup["target_exposure_A"].to_numpy())
    scaleup["change_sign"] = change_sign
    scaleup["htf_agree_code_local"] = scaleup["HTF_tilt_state"].to_numpy() * change_sign
    scaleup["vote_dispersion_aligned"] = scaleup["vote_dispersion"].to_numpy() * change_sign
    scaleup["quality_high_u6b"] = ((scaleup["htf_agree_code_local"] == 1) |
                                    (scaleup["vote_dispersion_aligned"] >= VOTE_THRESH)).astype(int)
    frac_quality_low = float((scaleup["quality_high_u6b"] == 0).mean())
    print(f"[step2-confirm] on this 8-session scale-up subset: quality_high_u6b rate={1-frac_quality_low:.4f} "
          f"(quality-low rate={frac_quality_low:.4f}; discovery pass rate was 81.3% high / 18.7% low)", flush=True)
    results["quality_high_rate"] = float(1 - frac_quality_low)

    redund = {}
    for pred in ["abs_value_dist_ticks", "poc_share"]:
        r_bin, p_bin = spearmanr(scaleup[pred], scaleup["quality_high_u6b"])
        r_cont, p_cont = spearmanr(scaleup[pred], scaleup["vote_dispersion_aligned"])
        redund[pred] = {"spearman_vs_quality_high_binary": float(r_bin), "p_naive": float(p_bin),
                         "spearman_vs_vote_dispersion_aligned_continuous": float(r_cont)}
        print(f"[step2-confirm] redundancy: {pred} vs quality_high_u6b: rho={r_bin:.4f} (p={p_bin:.4f}); "
              f"vs vote_dispersion_aligned (continuous): rho={r_cont:.4f}", flush=True)
    results["redundancy_correlation"] = redund

    incr = {}
    for H in [1, 3, 20]:
        ycol = f"signed_markout_{H}_A"
        sub = scaleup.dropna(subset=[ycol, "abs_value_dist_ticks", "quality_high_u6b"])
        if len(sub) < 10:
            incr[f"H{H}"] = {"n": len(sub), "note": "n<10, skipped"}
            continue

        def ols_r2(frame, x_cols, y_col):
            s = frame.dropna(subset=x_cols + [y_col])
            X = s[x_cols].to_numpy(dtype=float)
            X = np.column_stack([np.ones(len(X)), X])
            y = s[y_col].to_numpy(dtype=float)
            coef, *_ = np.linalg.lstsq(X, y, rcond=None)
            yhat = X @ coef
            ss_res = np.sum((y - yhat) ** 2); ss_tot = np.sum((y - y.mean()) ** 2)
            r2 = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan
            return r2, coef, len(s)

        r2_base, coef_base, n_base = ols_r2(sub, ["quality_high_u6b"], ycol)
        r2_ext, coef_ext, n_ext = ols_r2(sub, ["quality_high_u6b", "abs_value_dist_ticks"], ycol)
        delta = r2_ext - r2_base
        r2_base2, _, _ = ols_r2(sub, ["abs_value_dist_ticks"], ycol)
        delta_reverse = r2_ext - r2_base2

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
        print(f"[step2-confirm] H={H}: n={n_ext} R2(quality only)={r2_base:.5f} R2(quality+auction)={r2_ext:.5f} "
              f"dR2(auction|quality)={delta:+.5f} auction_coef={coef_ext[-1]:.4f} sessCI={[lo,hi]}", flush=True)
    results["incremental_value"] = incr

with open(os.path.join(OUT, "step2_redundancy_results_CONFIRM.json"), "w") as f:
    json.dump(results, f, indent=2, default=float)
print("\nSTEP2_REDUNDANCY_CONFIRM DONE")
