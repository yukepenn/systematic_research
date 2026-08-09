"""
U4 step 2 -- multi-checkpoint matched analysis (directive point 2), right-tail check
(point 3), and chronology + health-only split (point 4).

Checkpoints traced along each short block's own path:
  entry            -- first bar of block (age=1)
  plus15           -- +15 minutes = +5 bars (age = entry_age+5), clipped to block end
  plus30           -- +30 minutes = +10 bars (age = entry_age+10), clipped to block end
  first_mdecay     -- first bar (after entry) where M_change opposes the position
                       (M_change>0 for shorts) -- "first M-decay signal"
  first_fastflip   -- first bar (after entry) where fast_member opposes the position
                       (fast_member>0 for shorts) -- "first fast-Solar reversal"
  pre_worst        -- the bar immediately BEFORE the single worst adverse bar-pnl bar in
                       the block ("peak-to-worst-acceleration point")

Primary comparison group: bottom-20 short losers vs top-20 short winners by net_pnl,
CANONICAL WINDOW ONLY (is_health_only_bar==False) -- consistent with campaign convention
that all formal comparisons use the canonical window; June-July-2026 health-only blocks are
reported separately in the chronology section, never blended into this comparison.

Also traces the two P0-matched blocks (3743, 3757) specifically, and a nearest-neighbor
entry-state match replication of SA0 sec15 as a sanity check that entry-only matching still
shows no separation in this table (cross-check, not re-derivation).
"""
import json
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = ROOT + r"\runs\U4_SHORT_MECHANISM\out"

bars = pd.read_parquet(OUT + r"\u4_bars_with_features.parquet")
bars = bars.set_index("t_idx", drop=False)
blocks_B = pd.read_parquet(OUT + r"\blocks_B_short.parquet")
blocks_A = pd.read_parquet(OUT + r"\blocks_A_short.parquet")

CHECKPOINTS = ["entry", "plus15", "plus30", "first_mdecay", "first_fastflip", "pre_worst"]

FEATURES = [
    "M", "abs_M", "M_change", "M_slope_20", "fast_member", "vote_dispersion",
    "downtrend_age_M", "downtrend_age_fast", "reversal_freq_20", "sigma460_atr_proxy_pts",
    "vwap_disp_atr", "clv_signed", "HTF_tilt_state", "giveback_ratio", "run_pnl_so_far",
    "age_bars",
]


def trace_block(bars, block_id_col, pnl_col, giveback_col, entry_t_idx, n_bars, position_sign,
                 bar_pnl_col):
    """Return dict[checkpoint_name] -> feature dict (or None if unreached)."""
    idxs = list(range(entry_t_idx, entry_t_idx + n_bars))
    blk = bars.loc[idxs]
    out = {}

    def snap(row_tidx, age_bars):
        row = bars.loc[row_tidx]
        return {
            "t_idx": int(row_tidx),
            "M": float(row["M"]), "abs_M": float(abs(row["M"])),
            "M_change": float(row["M_change"]), "M_slope_20": float(row["M_slope_20"]),
            "fast_member": int(row["fast_member"]), "vote_dispersion": int(row["vote_dispersion"]),
            "downtrend_age_M": int(row["downtrend_age_M"]),
            "downtrend_age_fast": int(row["downtrend_age_fast"]),
            "reversal_freq_20": float(row["reversal_freq_20"]),
            "sigma460_atr_proxy_pts": float(row["sigma460_atr_proxy_pts"]),
            "vwap_disp_atr": float(row["vwap_disp_atr"]),
            "clv_signed": float(row["clv_signed"]),
            "HTF_tilt_state": float(row["HTF_tilt_state"]),
            "giveback_ratio": float(row[giveback_col]),
            "run_pnl_so_far": float(row[pnl_col]),
            "age_bars": int(age_bars),
        }

    # entry
    out["entry"] = snap(entry_t_idx, 1)

    # plus15 / plus30 (5 / 10 bars after entry), clipped to block end
    for name, offset in [("plus15", 5), ("plus30", 10)]:
        target = entry_t_idx + offset
        if target <= idxs[-1]:
            out[name] = snap(target, offset + 1)
        else:
            out[name] = None  # block ended before this checkpoint

    # first M-decay signal: first bar (age>=2) where M_change * position_sign < 0
    mdecay_tidx = None
    for t in idxs[1:]:
        if bars.at[t, "M_change"] * position_sign < 0:
            mdecay_tidx = t
            break
    out["first_mdecay"] = snap(mdecay_tidx, mdecay_tidx - entry_t_idx + 1) if mdecay_tidx else None

    # first fast-member flip against position: fast_member * position_sign < 0 (strict)
    fastflip_tidx = None
    for t in idxs[1:]:
        if bars.at[t, "fast_member"] * position_sign < 0:
            fastflip_tidx = t
            break
    out["first_fastflip"] = snap(fastflip_tidx, fastflip_tidx - entry_t_idx + 1) if fastflip_tidx else None

    # pre_worst: bar immediately before the single worst adverse bar_pnl in the block
    bp = bars.loc[idxs, bar_pnl_col]
    worst_tidx = bp.idxmin()
    if worst_tidx > idxs[0]:
        pre_tidx = worst_tidx - 1
        out["pre_worst"] = snap(pre_tidx, pre_tidx - entry_t_idx + 1)
        out["pre_worst"]["worst_bar_pnl"] = float(bp.min())
        out["pre_worst"]["worst_bar_t_idx"] = int(worst_tidx)
    else:
        out["pre_worst"] = None  # worst bar IS the entry bar, nothing "before" it in-block

    return out


def trace_group(blocks_df, bars, block_id_col, pnl_col, giveback_col, bar_pnl_col,
                 position_sign_fn, label):
    rows = []
    for _, b in blocks_df.iterrows():
        entry_t_idx = int(b["entry_t_idx"])
        n_bars = int(b["n_bars"])
        pos_sign = position_sign_fn(b)
        trace = trace_block(bars, block_id_col, pnl_col, giveback_col, entry_t_idx, n_bars,
                             pos_sign, bar_pnl_col)
        for cp in CHECKPOINTS:
            st = trace[cp]
            row = {"block_id": b[block_id_col], "group": label, "net_pnl": b["net_pnl"],
                   "n_bars": n_bars, "checkpoint": cp, "reached": st is not None}
            if st is not None:
                row.update(st)
            rows.append(row)
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Product B: canonical-window bottom-20 / top-20 short blocks + P0 blocks
# ---------------------------------------------------------------------------
canon_B = blocks_B[~blocks_B["is_health_only_bar"]].copy()
bottom20_B = canon_B.nsmallest(20, "net_pnl")
top20_B = canon_B.nlargest(20, "net_pnl")
p0_B = blocks_B[blocks_B["block_id_B"].isin([3743, 3757])]

print("Product B canonical shorts: bottom-20 net range", bottom20_B["net_pnl"].min(),
      "to", bottom20_B["net_pnl"].max())
print("Product B canonical shorts: top-20 net range", top20_B["net_pnl"].min(),
      "to", top20_B["net_pnl"].max())
print("P0-matched blocks found:", p0_B[["block_id_B", "net_pnl", "entry_time"]].to_dict("records"))

trace_loser_B = trace_group(bottom20_B, bars, "block_id_B", "run_pnl_B_dollars",
                             "giveback_ratio_B", "bar_pnl_B_nq_dollars",
                             lambda b: -1, "loser20")
trace_winner_B = trace_group(top20_B, bars, "block_id_B", "run_pnl_B_dollars",
                              "giveback_ratio_B", "bar_pnl_B_nq_dollars",
                              lambda b: -1, "winner20")
trace_p0_B = trace_group(p0_B, bars, "block_id_B", "run_pnl_B_dollars",
                          "giveback_ratio_B", "bar_pnl_B_nq_dollars",
                          lambda b: -1, "p0_named")

trace_B = pd.concat([trace_loser_B, trace_winner_B, trace_p0_B], ignore_index=True)
trace_B.to_csv(OUT + r"\checkpoint_trace_B.csv", index=False)
print(f"Wrote checkpoint_trace_B.csv ({len(trace_B)} rows)")

# ---------------------------------------------------------------------------
# Product A: canonical-window bottom-20 / top-20 short blocks
# ---------------------------------------------------------------------------
canon_A = blocks_A[~blocks_A["is_health_only_bar"]].copy()
bottom20_A = canon_A.nsmallest(20, "net_pnl")
top20_A = canon_A.nlargest(20, "net_pnl")

print("\nProduct A canonical shorts: bottom-20 net range", bottom20_A["net_pnl"].min(),
      "to", bottom20_A["net_pnl"].max())
print("Product A canonical shorts: top-20 net range", top20_A["net_pnl"].min(),
      "to", top20_A["net_pnl"].max())

trace_loser_A = trace_group(bottom20_A, bars, "block_id_A", "run_pnl_A_dollars",
                             "giveback_ratio_A", "bar_pnl_A_dollars",
                             lambda b: -1, "loser20")
trace_winner_A = trace_group(top20_A, bars, "block_id_A", "run_pnl_A_dollars",
                              "giveback_ratio_A", "bar_pnl_A_dollars",
                              lambda b: -1, "winner20")
trace_A = pd.concat([trace_loser_A, trace_winner_A], ignore_index=True)
trace_A.to_csv(OUT + r"\checkpoint_trace_A.csv", index=False)
print(f"Wrote checkpoint_trace_A.csv ({len(trace_A)} rows)")

# ---------------------------------------------------------------------------
# Checkpoint-by-checkpoint summary: reach-rate + feature medians, loser vs winner
# ---------------------------------------------------------------------------
def summarize(trace_df, label):
    out = []
    for cp in CHECKPOINTS:
        sub = trace_df[trace_df["checkpoint"] == cp]
        for grp in ["loser20", "winner20"]:
            g = sub[sub["group"] == grp]
            reached = g[g["reached"]]
            row = {
                "product": label, "checkpoint": cp, "group": grp,
                "n_total": len(g), "n_reached": len(reached),
                "reach_rate": len(reached) / len(g) if len(g) else np.nan,
            }
            for feat in FEATURES:
                if feat in reached.columns and len(reached):
                    row[f"{feat}_median"] = float(reached[feat].median())
                    row[f"{feat}_mean"] = float(reached[feat].mean())
            if len(reached) and "M_change" in reached.columns:
                row["frac_M_change_adverse"] = float((reached["M_change"] > 0).mean())
            if len(reached) and "fast_member" in reached.columns:
                row["frac_fast_member_adverse"] = float((reached["fast_member"] > 0).mean())
            if len(reached) and "age_bars" in reached.columns:
                row["lead_bars_to_block_end_median"] = float(
                    (g.loc[reached.index, "n_bars"] - reached["age_bars"]).median())
            out.append(row)
    return pd.DataFrame(out)

summary_B = summarize(trace_B[trace_B["group"] != "p0_named"], "B")
summary_A = summarize(trace_A, "A")
summary_B.to_csv(OUT + r"\checkpoint_summary_B.csv", index=False)
summary_A.to_csv(OUT + r"\checkpoint_summary_A.csv", index=False)

print("\n=== Product B checkpoint summary (loser20 vs winner20) ===")
cols_show = ["checkpoint", "group", "n_reached", "reach_rate", "M_change_median",
             "frac_M_change_adverse", "fast_member_median", "frac_fast_member_adverse",
             "giveback_ratio_median", "run_pnl_so_far_median", "lead_bars_to_block_end_median"]
print(summary_B[cols_show].to_string(index=False))

print("\n=== Product A checkpoint summary (loser20 vs winner20) ===")
print(summary_A[cols_show].to_string(index=False))

# P0 blocks individually
print("\n=== P0-matched blocks (3743, 3757), checkpoint values ===")
print(trace_p0_B[["block_id", "checkpoint", "reached", "M_change", "fast_member",
                   "giveback_ratio", "run_pnl_so_far", "age_bars"]].to_string(index=False))

# ---------------------------------------------------------------------------
# Entry-only nearest-neighbor sanity check (replicate SA0 sec15 style, this table)
# ---------------------------------------------------------------------------
print("\n=== Entry-only NN matched-winner-rate sanity check (SA0 sec15 replication, B shorts) ===")
feat_cols = ["entry_T", "entry_sigma460", "entry_vote_dispersion", "entry_htf_agrees_short",
             "entry_minutes_since_rth_open"]
pool = canon_B.copy()
pool["outcome_win"] = pool["net_pnl"] > 0
z = pool[["entry_T", "entry_sigma460", "entry_vote_dispersion", "entry_minutes_since_rth_open"]].copy()
z = (z - z.mean()) / z.std()
z["entry_htf_agrees_short"] = pool["entry_htf_agrees_short"].astype(float) * 2.0  # weight categorical
Z = z.to_numpy()
pool_idx = pool.index.to_numpy()

matched_rates = []
for _, loser in bottom20_B.iterrows():
    li = pool.index[pool["block_id_B"] == loser["block_id_B"]][0]
    lz = Z[pool.index.get_loc(li)]
    dist = np.sqrt(((Z - lz) ** 2).sum(axis=1))
    dist[pool.index.get_loc(li)] = np.inf
    nn_order = np.argsort(dist)[:10]
    matched_win_rate = pool.iloc[nn_order]["outcome_win"].mean()
    matched_rates.append(matched_win_rate)
unconditional_rate = (canon_B["net_pnl"] > 0).mean()
print(f"Mean matched-winner-rate across 20 losers (entry-state NN, k=10): "
      f"{np.mean(matched_rates):.3f}, median {np.median(matched_rates):.3f}")
print(f"Unconditional short-block win rate (canonical, Product B): {unconditional_rate:.3f}")

log = {
    "n_short_blocks_B_canonical": len(canon_B),
    "n_short_blocks_A_canonical": len(canon_A),
    "bottom20_B_range": [float(bottom20_B["net_pnl"].min()), float(bottom20_B["net_pnl"].max())],
    "top20_B_range": [float(top20_B["net_pnl"].min()), float(top20_B["net_pnl"].max())],
    "bottom20_A_range": [float(bottom20_A["net_pnl"].min()), float(bottom20_A["net_pnl"].max())],
    "top20_A_range": [float(top20_A["net_pnl"].min()), float(top20_A["net_pnl"].max())],
    "entry_only_NN_matched_winner_rate_mean": float(np.mean(matched_rates)),
    "entry_only_NN_matched_winner_rate_median": float(np.median(matched_rates)),
    "unconditional_win_rate_B_canonical": float(unconditional_rate),
}
with open(OUT + r"\checkpoint_analysis_log.json", "w") as f:
    json.dump(log, f, indent=2, default=str)
print("\n", json.dumps(log, indent=2))
