"""SA0 sec13 (April-2026 deep explanation) + sec15 (matched-case failure science). Reuses P0's
already-refuted literal B-MOM-veto finding (REPORT.md) verbatim -- does not re-litigate it -- and
extends it with causal-entry-state matched-control search across the other 1,976 blocks."""
import os, sys, json
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
import substrate as S

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
ledger = pd.read_parquet(S.LEDGER_PATH)
block_sum = pd.read_csv(S.BLOCKSUM_PATH)
entry_rows = ledger[(ledger["age_bars"] == 1) & (ledger["position"] != 0)].copy()
merged = block_sum.merge(
    entry_rows[["block_id", "vote_dispersion", "n_bullish", "n_bearish", "HTF_tilt_state",
                "T", "Tp", "B", "hm", "sigma460_atr_proxy_pts", "sess_date", "t_idx"]],
    on="block_id", how="left")


def causal_features(row):
    """Entry-state-only features, all causal (known at entry time), for matching."""
    return np.array([
        row["entry_T"],                       # entry Solar T (signed conviction)
        row["hm"] / 100.0,                     # time-of-day (hour.minute-ish scale)
        row["sigma460_atr_proxy_pts"],         # vol level
        1.0 if np.sign(row["entry_T"]) == row["HTF_tilt_state"] else (0.0 if row["HTF_tilt_state"] == 0 else -1.0),
        row["vote_dispersion"],
    ])


feat_cols = ["entry_T", "hm", "sigma460_atr_proxy_pts", "HTF_tilt_state", "vote_dispersion"]
F = merged[feat_cols].to_numpy(dtype=float)
F_std = (F - np.nanmean(F, axis=0)) / np.nanstd(F, axis=0)
side = merged["side"].to_numpy()


def nearest_matches(block_idx, k=8, exclude_ids=None):
    """k nearest neighbors (standardized Euclidean, entry-causal features only), SAME side,
    excluding the block itself and any ids in exclude_ids."""
    exclude_ids = exclude_ids or set()
    target = F_std[block_idx]
    same_side = side == side[block_idx]
    d = np.linalg.norm(F_std - target, axis=1)
    d = np.where(same_side, d, np.inf)
    d[block_idx] = np.inf
    for bid in exclude_ids:
        pos = merged.index[merged["block_id"] == bid]
        d[pos] = np.inf
    order = np.argsort(d)[:k]
    return merged.iloc[order].assign(match_dist=d[order])


print("=" * 90, "\nSEC13 -- APRIL-2026 DEEP EXPLANATION (matched-control extension)\n", "=" * 90, sep="")
april_ids = [3743, 3757]
april_results = {}
for bid in april_ids:
    idx = merged.index[merged["block_id"] == bid]
    if len(idx) == 0:
        print(f"  block {bid} not found in merged entry table, skipping")
        continue
    idx = idx[0]
    row = merged.iloc[idx]
    matches = nearest_matches(idx, k=8)
    print(f"\n-- block {bid} ({row['sess_date']}, side={row['side']}, entry_T={row['entry_T']}, "
          f"net_pnl={row['net_pnl']:.2f}, HTF={row['HTF_tilt_state']}, hm={row['hm']}, "
          f"vote_dispersion={row['vote_dispersion']}, B={row['B']}) --")
    print(matches[["block_id", "sess_date", "entry_T", "hm", "HTF_tilt_state", "vote_dispersion",
                    "net_pnl", "MFE_dollars", "giveback_ratio", "match_dist"]].round(2).to_string(index=False))
    winners_among_matches = matches[matches["net_pnl"] > 0]
    april_results[str(bid)] = {
        "target_net_pnl": float(row["net_pnl"]), "target_entry_T": float(row["entry_T"]),
        "n_matches": len(matches), "n_winning_matches": int((matches["net_pnl"] > 0).sum()),
        "matches_mean_net_pnl": float(matches["net_pnl"].mean()),
        "best_match_block_id": int(winners_among_matches.iloc[0]["block_id"]) if len(winners_among_matches) else None,
        "best_match_net_pnl": float(winners_among_matches.iloc[0]["net_pnl"]) if len(winners_among_matches) else None,
    }

json.dump(april_results, open(os.path.join(OUT, "sec13_april_matched_controls.json"), "w"), indent=2)

print("\n" + "=" * 90, "\nSEC15 -- MATCHED-CASE FAILURE SCIENCE (top-20 losers)\n", "=" * 90, sep="")
top20_losers = merged.nsmallest(20, "net_pnl")
rows15 = []
for _, r in top20_losers.iterrows():
    idx = merged.index[merged["block_id"] == r["block_id"]][0]
    matches = nearest_matches(idx, k=10)
    n_win = int((matches["net_pnl"] > 0).sum())
    big_win = matches[matches["net_pnl"] > matches["net_pnl"].abs().median() * 2]
    rows15.append({
        "block_id": int(r["block_id"]), "sess_date": r["sess_date"], "side": int(r["side"]),
        "net_pnl": float(r["net_pnl"]), "entry_T": float(r["entry_T"]), "hm": float(r["hm"]),
        "HTF_tilt_state": float(r["HTF_tilt_state"]), "vote_dispersion": float(r["vote_dispersion"]),
        "n_matched_controls": len(matches), "n_matched_winners": n_win,
        "matched_winner_rate": n_win / len(matches),
        "mean_matched_net_pnl": float(matches["net_pnl"].mean()),
        "best_matched_net_pnl": float(matches["net_pnl"].max()),
        "match_feature_dist_mean": float(matches["match_dist"].mean()),
    })
match_df = pd.DataFrame(rows15)
match_df.to_csv(os.path.join(OUT, "sec15_top20_loser_matched_controls.csv"), index=False)
print(match_df.round(2).to_string(index=False))

summary15 = {
    "mean_matched_winner_rate_across_top20_losers": float(match_df["matched_winner_rate"].mean()),
    "median_matched_winner_rate": float(match_df["matched_winner_rate"].median()),
    "interpretation_note": (
        "matched_winner_rate close to the UNCONDITIONAL block winner rate (~41.8%, from sec12) "
        "means entry-state features alone do not distinguish these losers from same-state peers -- "
        "i.e. no early-available signal separates them, consistent with 'the loss is the cost of "
        "capturing the right tail'. A matched_winner_rate well BELOW the unconditional rate would "
        "instead suggest genuine entry-state fragility worth a future preregistered study."),
    "unconditional_block_winner_rate": float((merged["net_pnl"] > 0).mean()),
}
print(json.dumps(summary15, indent=2))
json.dump(summary15, open(os.path.join(OUT, "sec15_summary.json"), "w"), indent=2)

print("\nSA0 sec13/sec15 complete.")
