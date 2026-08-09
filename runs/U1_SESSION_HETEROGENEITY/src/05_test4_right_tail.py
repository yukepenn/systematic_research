"""U1 test 4 -- right-tail check, same discipline R3/R4/R5 used: do the top-20 all-time winning
Product-B blocks concentrate in / get excluded by an RTH-ETH or session_phase split? Canonical
window only (the whole-history top-20 is computed over canonical entries, matching the campaign's
'all-time' convention used by R3/R4/R5's own right-tail checks on the same P0 block ledger)."""
import os, json
import numpy as np, pandas as pd

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")

entry_B = pd.read_csv(os.path.join(OUT, "block_entry_B.csv"))
entry_B_c = entry_B[~entry_B["is_health_only_bar"]].copy()

print("=" * 100)
print("TEST 4 -- top-20 all-time winning Product-B blocks: session_phase / RTH-ETH membership")
print("=" * 100)
top20 = entry_B_c.sort_values("net_pnl", ascending=False).head(20)
cols = ["t_idx", "sess_date", "action_B", "side", "M_abs", "vol_tercile", "session_phase", "is_rth", "net_pnl"]
print(top20[cols].round(2).to_string(index=False))
top20.to_csv(os.path.join(OUT, "t4_top20_winners_B.csv"), index=False)

n_rth = int(top20["is_rth"].sum())
n_eth = int((~top20["is_rth"]).sum())
phase_counts = top20["session_phase"].value_counts().reindex(
    ["ETH_ASIA", "ETH_EUROPE", "US_PREMARKET", "RTH_OPEN", "RTH_MID", "RTH_CLOSE", "POST_RTH"], fill_value=0)
print(f"\ntop-20 winners: {n_rth}/20 RTH, {n_eth}/20 ETH")
print("\ntop-20 winners by session_phase:")
print(phase_counts.to_string())

# base rate for comparison: what fraction of ALL entries are RTH / in each phase?
base_rth = float(entry_B_c["is_rth"].mean())
base_phase = entry_B_c["session_phase"].value_counts(normalize=True).reindex(phase_counts.index, fill_value=0.0)
print(f"\nbase rate (all {len(entry_B_c)} canonical entries+reversals): {base_rth:.1%} RTH")
print("\nbase rate by phase:")
print(base_phase.round(3).to_string())

print("\ncomparison -- top-20 share vs base-rate share, by phase:")
cmp_df = pd.DataFrame({"top20_share": (phase_counts / 20).round(3), "base_rate_share": base_phase.round(3)})
cmp_df["ratio"] = (cmp_df["top20_share"] / cmp_df["base_rate_share"].replace(0, np.nan)).round(2)
print(cmp_df.to_string())
cmp_df.to_csv(os.path.join(OUT, "t4_top20_vs_baserate_by_phase.csv"))

# also: worst-20 losers, for symmetry (does the losing tail also concentrate anywhere?)
bottom20 = entry_B_c.sort_values("net_pnl", ascending=True).head(20)
n_rth_bot = int(bottom20["is_rth"].sum())
print(f"\nbottom-20 losers: {n_rth_bot}/20 RTH, {20-n_rth_bot}/20 ETH  (for symmetry check)")
bottom20.to_csv(os.path.join(OUT, "t4_bottom20_losers_B.csv"), index=False)
bottom_phase_counts = bottom20["session_phase"].value_counts().reindex(phase_counts.index, fill_value=0)
print("\nbottom-20 losers by session_phase:")
print(bottom_phase_counts.to_string())

summary = {
    "top20_n_rth": n_rth, "top20_n_eth": n_eth, "base_rate_rth": base_rth,
    "bottom20_n_rth": n_rth_bot, "bottom20_n_eth": 20 - n_rth_bot,
    "top20_phase_counts": phase_counts.to_dict(),
    "bottom20_phase_counts": bottom_phase_counts.to_dict(),
    "verdict_note": ("A phase-based split is tail-DANGEROUS if any phase/RTH-ETH bucket the "
                      "heterogeneity tests (1-3) flag as 'weak'/'exclude' also contains a "
                      "disproportionate share of these top-20 winners -- read this table "
                      "against tests 1-3's own flagged buckets, not in isolation."),
}
json.dump(summary, open(os.path.join(OUT, "t4_summary.json"), "w"), indent=2)
print("\n" + json.dumps({k: v for k, v in summary.items() if k != "verdict_note"}, indent=2))
print("\ntest4 complete.")
