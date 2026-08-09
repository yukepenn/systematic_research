"""
U4 step 3 -- right-tail check (directive point 3): does the checkpoint-level giveback_ratio
separation found in step 2 (losers show elevated giveback_ratio as early as +15/+30 minutes
post-entry) survive contact with the giant/crisis short winners -- the largest short blocks
by net_pnl, both products, ALL available history (canonical + health-only, since a giant
crisis winner could in principle occur in either window; both are checked and reported
separately)?

Method: for the top-N largest short winners by net_pnl (N=20 primary, N=40 as a robustness
check), trace the SAME checkpoints as step 2 and report the full distribution (not just
median) of giveback_ratio and M_change/fast_member state at plus15/plus30/pre_worst -- the
checkpoints where step 2 found the sharpest loser/winner median separation. A candidate
"de-risk if giveback_ratio > threshold at +15/+30min" rule is tail-UNSAFE if any material
fraction of these giant winners would have crossed that threshold early (and gone on to
recover into a giant winner anyway).
"""
import json
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = ROOT + r"\runs\U4_SHORT_MECHANISM\out"

bars = pd.read_parquet(OUT + r"\u4_bars_with_features.parquet").set_index("t_idx", drop=False)
blocks_B = pd.read_parquet(OUT + r"\blocks_B_short.parquet")
blocks_A = pd.read_parquet(OUT + r"\blocks_A_short.parquet")

CHECKPOINTS = ["entry", "plus15", "plus30", "first_mdecay", "first_fastflip", "pre_worst"]


def trace_block(bars, entry_t_idx, n_bars, position_sign, pnl_col, giveback_col, bar_pnl_col):
    idxs = list(range(entry_t_idx, entry_t_idx + n_bars))

    def snap(row_tidx, age_bars):
        row = bars.loc[row_tidx]
        return {
            "M_change": float(row["M_change"]), "fast_member": int(row["fast_member"]),
            "giveback_ratio": float(row[giveback_col]), "run_pnl_so_far": float(row[pnl_col]),
            "age_bars": int(age_bars),
        }

    out = {"entry": snap(entry_t_idx, 1)}
    for name, offset in [("plus15", 5), ("plus30", 10)]:
        target = entry_t_idx + offset
        out[name] = snap(target, offset + 1) if target <= idxs[-1] else None

    mdecay_tidx = None
    for t in idxs[1:]:
        if bars.at[t, "M_change"] * position_sign < 0:
            mdecay_tidx = t
            break
    out["first_mdecay"] = snap(mdecay_tidx, mdecay_tidx - entry_t_idx + 1) if mdecay_tidx else None

    fastflip_tidx = None
    for t in idxs[1:]:
        if bars.at[t, "fast_member"] * position_sign < 0:
            fastflip_tidx = t
            break
    out["first_fastflip"] = snap(fastflip_tidx, fastflip_tidx - entry_t_idx + 1) if fastflip_tidx else None

    bp = bars.loc[idxs, bar_pnl_col]
    worst_tidx = bp.idxmin()
    if worst_tidx > idxs[0]:
        pre_tidx = worst_tidx - 1
        out["pre_worst"] = snap(pre_tidx, pre_tidx - entry_t_idx + 1)
    else:
        out["pre_worst"] = None
    return out


def righttail_table(blocks_df, pnl_col, giveback_col, bar_pnl_col, topn, window_label):
    top = blocks_df.nlargest(topn, "net_pnl")
    rows = []
    for _, b in top.iterrows():
        trace = trace_block(bars, int(b["entry_t_idx"]), int(b["n_bars"]), -1,
                             pnl_col, giveback_col, bar_pnl_col)
        for cp in CHECKPOINTS:
            st = trace[cp]
            row = {"window": window_label, "block_id": b.get("block_id_B", b.get("block_id_A")),
                   "net_pnl": b["net_pnl"], "n_bars": b["n_bars"], "checkpoint": cp,
                   "reached": st is not None}
            if st is not None:
                row.update(st)
            rows.append(row)
    return pd.DataFrame(rows), top


print("=== Product B giant short winners: right-tail check ===")
canon_B = blocks_B[~blocks_B["is_health_only_bar"]]
alltime_B = blocks_B  # canonical + health-only, checked separately below

rt_B_canon, top20_B_canon = righttail_table(canon_B, "run_pnl_B_dollars", "giveback_ratio_B",
                                             "bar_pnl_B_nq_dollars", 20, "canonical_top20")
rt_B_all, top20_B_all = righttail_table(alltime_B, "run_pnl_B_dollars", "giveback_ratio_B",
                                         "bar_pnl_B_nq_dollars", 20, "alltime_incl_healthonly_top20")
rt_B40, top40_B_canon = righttail_table(canon_B, "run_pnl_B_dollars", "giveback_ratio_B",
                                         "bar_pnl_B_nq_dollars", 40, "canonical_top40")

rt_B = pd.concat([rt_B_canon, rt_B_all, rt_B40], ignore_index=True)
rt_B.to_csv(OUT + r"\righttail_trace_B.csv", index=False)

print("Top-20 canonical short winners net range:", top20_B_canon["net_pnl"].min(), "to",
      top20_B_canon["net_pnl"].max())
print("How many of top-20 differ between canonical-only and all-time (incl. health-only)?",
      len(set(top20_B_canon["block_id_B"]) - set(top20_B_all["block_id_B"])), "canonical-only",
      "swapped for health-only entrants")

# candidate threshold from step 2: loser20 median giveback_ratio at plus15 = 0.63, plus30 = 0.79
CANDIDATE_THRESHOLDS = {"plus15": 0.63, "plus30": 0.79}

for label, rt, topset in [("canonical top-20", rt_B_canon, top20_B_canon),
                           ("all-time (incl. health-only) top-20", rt_B_all, top20_B_all),
                           ("canonical top-40", rt_B40, top40_B_canon)]:
    print(f"\n-- {label} --")
    for cp in ["plus15", "plus30", "pre_worst"]:
        sub = rt[(rt["checkpoint"] == cp) & (rt["reached"])]
        if len(sub) == 0:
            print(f"  {cp}: no blocks reached this checkpoint")
            continue
        gvals = sub["giveback_ratio"]
        n_total = (rt["checkpoint"] == cp).sum()
        thr = CANDIDATE_THRESHOLDS.get(cp)
        frac_over = (gvals > thr).mean() if thr else np.nan
        print(f"  {cp}: n_reached={len(sub)}/{n_total}, giveback_ratio "
              f"median={gvals.median():.3f} p90={gvals.quantile(.9):.3f} "
              f"max={gvals.max():.3f}"
              + (f", frac > loser-median-threshold({thr})={frac_over:.2%}" if thr else ""))
        if thr and frac_over > 0:
            hit_blocks = sub.loc[gvals > thr, ["block_id", "net_pnl", "giveback_ratio"]]
            print(f"    giant winners that WOULD be flagged at {cp} by threshold {thr}:")
            print("   ", hit_blocks.to_string(index=False))

print("\n=== Product A giant short winners: right-tail check ===")
canon_A = blocks_A[~blocks_A["is_health_only_bar"]]
alltime_A = blocks_A
rt_A_canon, top20_A_canon = righttail_table(canon_A, "run_pnl_A_dollars", "giveback_ratio_A",
                                             "bar_pnl_A_dollars", 20, "canonical_top20")
rt_A_all, top20_A_all = righttail_table(alltime_A, "run_pnl_A_dollars", "giveback_ratio_A",
                                         "bar_pnl_A_dollars", 20, "alltime_incl_healthonly_top20")
rt_A = pd.concat([rt_A_canon, rt_A_all], ignore_index=True)
rt_A.to_csv(OUT + r"\righttail_trace_A.csv", index=False)

CANDIDATE_THRESHOLDS_A = {"plus15": 1.02, "plus30": 0.84}  # from step2 Product A loser20 medians
for label, rt in [("canonical top-20", rt_A_canon), ("all-time top-20", rt_A_all)]:
    print(f"\n-- Product A {label} --")
    for cp in ["plus15", "plus30", "pre_worst"]:
        sub = rt[(rt["checkpoint"] == cp) & (rt["reached"])]
        if len(sub) == 0:
            print(f"  {cp}: no blocks reached this checkpoint")
            continue
        gvals = sub["giveback_ratio"]
        thr = CANDIDATE_THRESHOLDS_A.get(cp)
        frac_over = (gvals > thr).mean() if thr else np.nan
        print(f"  {cp}: n_reached={len(sub)}, giveback_ratio median={gvals.median():.3f} "
              f"p90={gvals.quantile(.9):.3f} max={gvals.max():.3f}"
              + (f", frac > loser-median-threshold({thr})={frac_over:.2%}" if thr else ""))

# ---------------------------------------------------------------------------
# Summary log
# ---------------------------------------------------------------------------
summary = {}
for cp in ["plus15", "plus30"]:
    sub = rt_B_canon[(rt_B_canon["checkpoint"] == cp) & (rt_B_canon["reached"])]
    thr = CANDIDATE_THRESHOLDS[cp]
    summary[f"B_canon_top20_{cp}_frac_over_thr"] = float((sub["giveback_ratio"] > thr).mean()) if len(sub) else None
    summary[f"B_canon_top20_{cp}_max_giveback"] = float(sub["giveback_ratio"].max()) if len(sub) else None
for cp in ["plus15", "plus30"]:
    sub = rt_A_canon[(rt_A_canon["checkpoint"] == cp) & (rt_A_canon["reached"])]
    thr = CANDIDATE_THRESHOLDS_A[cp]
    summary[f"A_canon_top20_{cp}_frac_over_thr"] = float((sub["giveback_ratio"] > thr).mean()) if len(sub) else None
    summary[f"A_canon_top20_{cp}_max_giveback"] = float(sub["giveback_ratio"].max()) if len(sub) else None

with open(OUT + r"\righttail_check_log.json", "w") as f:
    json.dump(summary, f, indent=2, default=str)
print("\n", json.dumps(summary, indent=2))
