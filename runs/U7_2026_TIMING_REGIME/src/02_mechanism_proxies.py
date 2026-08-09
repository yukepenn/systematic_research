"""U7 step2 -- mechanism-specific proxies directly tied to what R2V1 (fixed 2-bar delay,
cancel-on-revert) and R2B (6-bar pullback/reclaim gate) actually do at the ENTRY-block level:
  (i)  quick-reversal rate = fraction of ENTRY blocks with block duration <= 2 bars -- exactly
       the population a confirm_bars=2 rule would cancel/redirect.
  (ii) 6-bar-window pullback magnitude in ATR units (R2B's own diagnostic variable), + reclaim
       rate given a pullback occurred.
  (iii) a lightweight delay-proxy P&L delta per block (skip first 2 bars' participation; blocks
        shorter than 3 bars get 0 instead of their full outcome) -- NOT the validated confirm=2
        state machine, a simplified single-pass approximation of it.
Ranks all step1+step2 candidate explanations by effect size and causal linkage.
"""
import os, json
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(ROOT, "runs", "U7_2026_TIMING_REGIME", "out")
PV_NQ = 20.0

df = pd.read_parquet(os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet"))
df["period"] = np.select(
    [(~df["is_health_only_bar"]) & (df["year"] < 2026),
     (~df["is_health_only_bar"]) & (df["year"] == 2026),
     df["is_health_only_bar"]],
    ["P0", "P1", "P2"], default="?"
)

# entry blocks = blocks where position_B != 0 (sign blocks); identify block start bar (action_B=='ENTRY')
nonzero = df[df["position_B"] != 0].copy()
block_len = nonzero.groupby("block_id_B")["age_bars_B"].max().rename("block_len")
block_net_pnl = nonzero.groupby("block_id_B")["run_pnl_B_dollars"].last().rename("block_net_pnl")

# run_pnl at age==2 (or age==block_len if block_len==1) per block -- cumulative pnl through first 2 bars
nonzero["target_age"] = nonzero["block_id_B"].map(block_len).clip(upper=2)
first2 = nonzero[nonzero["age_bars_B"] == nonzero["target_age"]].groupby("block_id_B")["run_pnl_B_dollars"].first()
first2 = first2.rename("pnl_first2")

# MAE at age==6 (or age==block_len if shorter) -- 6-bar-window pullback (R2B's own diagnostic variable)
nonzero["target_age6"] = nonzero["block_id_B"].map(block_len).clip(upper=6)
mae6 = nonzero[nonzero["age_bars_B"] == nonzero["target_age6"]].groupby("block_id_B")["MAE_B_dollars"].first()
mae6 = mae6.rename("MAE_6bar")
run_pnl6 = nonzero[nonzero["age_bars_B"] == nonzero["target_age6"]].groupby("block_id_B")["run_pnl_B_dollars"].first()
run_pnl6 = run_pnl6.rename("run_pnl_6bar")

entries = df[df["action_B"] == "ENTRY"].set_index("block_id_B")
tbl = entries[["sess_date", "year", "period", "sigma460_atr_proxy_pts", "position_B"]].copy()
tbl = tbl.join(block_len).join(block_net_pnl).join(first2).join(mae6).join(run_pnl6)
tbl["pnl_first2"] = tbl["pnl_first2"].fillna(tbl["block_net_pnl"])  # length-1 blocks: first2 == full block
tbl["MAE_6bar"] = tbl["MAE_6bar"].fillna(0.0)
tbl["run_pnl_6bar"] = tbl["run_pnl_6bar"].fillna(tbl["block_net_pnl"])

# (i) quick-reversal rate
tbl["quick_reversal"] = tbl["block_len"] <= 2

# (ii) 6-bar pullback magnitude, ATR units (using entry-bar sigma460)
tbl["pullback_atr_6bar"] = np.where(
    tbl["sigma460_atr_proxy_pts"] > 0,
    (-tbl["MAE_6bar"]) / (tbl["sigma460_atr_proxy_pts"] * PV_NQ), np.nan
)
tbl["had_pullback"] = tbl["MAE_6bar"] < 0
tbl["reclaimed"] = tbl["had_pullback"] & (tbl["run_pnl_6bar"] >= 0)

# (iii) lightweight delay-proxy delta
tbl["delayed_proxy_pnl"] = np.where(tbl["block_len"] >= 3, tbl["block_net_pnl"] - tbl["pnl_first2"], 0.0)
tbl["delay_delta"] = tbl["delayed_proxy_pnl"] - tbl["block_net_pnl"]

tbl.to_csv(os.path.join(OUT, "step2_entry_block_mechanism_table.csv"))
print(f"[U7] entry-block mechanism table: {len(tbl)} blocks")

# ============================================================= summarize by period
print("\n[U7] quick-reversal rate (block_len<=2) by period:")
qr = tbl.groupby("period")["quick_reversal"].agg(["mean", "sum", "count"]).reindex(["P0", "P1", "P2"])
print(qr.to_string())

print("\n[U7] 6-bar pullback magnitude (ATR units) by period, ALL entries:")
pb = tbl.groupby("period")["pullback_atr_6bar"].agg(["mean", "median", "std", "count"]).reindex(["P0", "P1", "P2"])
print(pb.to_string())

print("\n[U7] given a pullback occurred, reclaim rate by period:")
sub = tbl[tbl["had_pullback"]]
rc = sub.groupby("period")["reclaimed"].agg(["mean", "sum", "count"]).reindex(["P0", "P1", "P2"])
print(rc.to_string())

print("\n[U7] lightweight delay-proxy: mean/sum delta ($) per block by period:")
dd = tbl.groupby("period")["delay_delta"].agg(["mean", "sum", "count"]).reindex(["P0", "P1", "P2"])
print(dd.to_string())

# per-year breakdown of delay_delta (chronology, matches R2V1's own convention)
print("\n[U7] delay-proxy sum($) by calendar year (P0 broken out, P1/P2 shown too):")
yr = tbl.groupby("year")["delay_delta"].agg(["sum", "mean", "count"])
print(yr.to_string())

# quick-reversal rate by year
print("\n[U7] quick-reversal rate by calendar year:")
yr_qr = tbl.groupby("year")["quick_reversal"].agg(["mean", "sum", "count"])
print(yr_qr.to_string())

# pullback magnitude by year
print("\n[U7] pullback_atr_6bar mean by calendar year:")
yr_pb = tbl.groupby("year")["pullback_atr_6bar"].agg(["mean", "median", "count"])
print(yr_pb.to_string())

# ============================================================= right-tail check (mandatory per standing rigor)
top20 = df.sort_values("run_pnl_B_dollars", ascending=False)
# use block-level net pnl to identify top-20 all-time winning BLOCKS (dedupe by block_id_B, take max run_pnl per block)
block_final_pnl = tbl["block_net_pnl"].sort_values(ascending=False)
top20_blocks = block_final_pnl.head(20)
top20_tbl = tbl.loc[top20_blocks.index]
print("\n[U7] RIGHT-TAIL CHECK: top-20 all-time winning Product-B blocks --")
print(f"  quick_reversal (block_len<=2) among top-20 winners: {int(top20_tbl['quick_reversal'].sum())}/20")
print(f"  pullback_atr_6bar among top-20 winners: mean={top20_tbl['pullback_atr_6bar'].mean():.3f}, "
      f"n_with_pullback={int(top20_tbl['had_pullback'].sum())}/20, "
      f"n_pullback_not_reclaimed={int((top20_tbl['had_pullback'] & ~top20_tbl['reclaimed']).sum())}/20")
print(f"  delay_delta among top-20 winners: sum=${top20_tbl['delay_delta'].sum():.2f}, "
      f"n_negative(delay would have HURT this winner)={int((top20_tbl['delay_delta'] < 0).sum())}/20")
top20_tbl.to_csv(os.path.join(OUT, "step2_top20_winner_blocks_mechanism.csv"))

bottom20_blocks = block_final_pnl.tail(20)
bottom20_tbl = tbl.loc[bottom20_blocks.index]
print(f"\n[U7] bottom-20 losing blocks: quick_reversal {int(bottom20_tbl['quick_reversal'].sum())}/20, "
      f"delay_delta sum=${bottom20_tbl['delay_delta'].sum():.2f} "
      f"(positive delta = delay would have HELPED this loser)")
bottom20_tbl.to_csv(os.path.join(OUT, "step2_bottom20_loser_blocks_mechanism.csv"))

# ============================================================= consolidated ranking table
print("\n" + "=" * 80)
print("[U7] CONSOLIDATED EFFECT-SIZE RANKING (P1 vs P0, entry/block-level)")
print("=" * 80)

bar_df = pd.read_csv(os.path.join(OUT, "step1_bar_level_shift.csv"))
entry_df = pd.read_csv(os.path.join(OUT, "step1_entry_level_shift.csv"))

rank_rows = []
for _, r in entry_df[entry_df.comparison == "P1_vs_P0"].iterrows():
    rank_rows.append({"variable": r["variable"], "level": "entry_block", "cohens_d": r["cohens_d"],
                       "abs_d": abs(r["cohens_d"])})

# mechanism proxies as their own "variables"
qr_p0 = tbl.loc[tbl.period == "P0", "quick_reversal"].astype(float)
qr_p1 = tbl.loc[tbl.period == "P1", "quick_reversal"].astype(float)
pooled = np.sqrt((qr_p0.std(ddof=1) ** 2 + qr_p1.std(ddof=1) ** 2) / 2)
d_qr = (qr_p1.mean() - qr_p0.mean()) / pooled if pooled > 0 else np.nan
rank_rows.append({"variable": "quick_reversal_rate(block_len<=2)", "level": "mechanism_proxy",
                   "cohens_d": d_qr, "abs_d": abs(d_qr)})

pb_p0 = tbl.loc[tbl.period == "P0", "pullback_atr_6bar"].dropna()
pb_p1 = tbl.loc[tbl.period == "P1", "pullback_atr_6bar"].dropna()
pooled = np.sqrt((pb_p0.std(ddof=1) ** 2 + pb_p1.std(ddof=1) ** 2) / 2)
d_pb = (pb_p1.mean() - pb_p0.mean()) / pooled if pooled > 0 else np.nan
rank_rows.append({"variable": "pullback_atr_6bar", "level": "mechanism_proxy",
                   "cohens_d": d_pb, "abs_d": abs(d_pb)})

rank_df = pd.DataFrame(rank_rows).sort_values("abs_d", ascending=False)
rank_df.to_csv(os.path.join(OUT, "step2_ranking.csv"), index=False)
print(rank_df.to_string(index=False))

print("\n[U7] step2 complete.")
