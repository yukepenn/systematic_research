"""R3 diagnostic -- is EUROPE_PREUS's (S2's closed window) badness uniform across the clock block,
or concentrated in a narrower state? Full-clock state interaction scan. Per spec.yaml: diagnostic
only, construction gated on finding broad/multi-year/right-tail-safe evidence."""
import os, sys, json
import numpy as np, pandas as pd

SA0_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                        "SA0_SYSTEM_STRUCTURE", "src")
sys.path.insert(0, SA0_SRC)
import substrate as S

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

ledger = pd.read_parquet(S.LEDGER_PATH)
block_sum = pd.read_csv(S.BLOCKSUM_PATH)
entry_rows = ledger[(ledger["age_bars"] == 1) & (ledger["position"] != 0)].copy()
merged = block_sum.merge(
    entry_rows[["block_id", "vote_dispersion", "HTF_tilt_state", "T", "Tp", "B", "hm",
                "sigma460_atr_proxy_pts", "sess_date"]],
    on="block_id", how="left")
merged["year"] = pd.to_datetime(merged["sess_date"]).dt.year
merged["M_at_entry"] = S.WSOLAR * merged["Tp"] + S.WBMOM * merged["B"]
merged["M_strength_tercile"] = pd.qcut(merged["M_at_entry"].abs(), 3, labels=["weak", "mid", "strong"], duplicates="drop")
merged["consensus_tercile"] = pd.qcut(merged["vote_dispersion"].abs(), 3, labels=["low", "mid", "high"], duplicates="drop")
merged["vol_tercile"] = pd.qcut(merged["sigma460_atr_proxy_pts"], 3, labels=["low", "mid", "high"], duplicates="drop")
merged["bmom_engaged"] = merged["B_engaged_during_trade"].map({True: "engaged", False: "not_engaged"})
merged["long_short"] = np.where(merged["side"] > 0, "LONG", "SHORT")

EUROPE_PREUS = (merged["hm"] >= 200) & (merged["hm"] < 800)
merged["in_europe_preus"] = np.where(EUROPE_PREUS, "IN_WINDOW", "OUTSIDE")

print("=" * 90, "\nDIAGNOSTIC 1 -- WITHIN-WINDOW vs OUTSIDE-WINDOW STATE BREAKDOWN\n", "=" * 90, sep="")
for dim in ["M_strength_tercile", "consensus_tercile", "vol_tercile", "bmom_engaged", "long_short"]:
    g = merged.groupby(["in_europe_preus", dim], observed=True).agg(
        n=("net_pnl", "size"), mean_pnl=("net_pnl", "mean"), sum_pnl=("net_pnl", "sum"),
        win_rate=("net_pnl", lambda x: float((x > 0).mean()))).reset_index()
    print(f"\n-- {dim} x in/out EUROPE_PREUS --")
    print(g.round(2).to_string(index=False))
    g.to_csv(os.path.join(OUT, f"diag1_{dim}_x_window.csv"), index=False)

pooled_in = merged[EUROPE_PREUS]
pooled_out = merged[~EUROPE_PREUS]
print(f"\npooled IN_WINDOW: n={len(pooled_in)} mean_pnl={pooled_in['net_pnl'].mean():.2f} "
      f"sum={pooled_in['net_pnl'].sum():.2f} win_rate={float((pooled_in['net_pnl']>0).mean()):.3f}")
print(f"pooled OUTSIDE:   n={len(pooled_out)} mean_pnl={pooled_out['net_pnl'].mean():.2f} "
      f"sum={pooled_out['net_pnl'].sum():.2f} win_rate={float((pooled_out['net_pnl']>0).mean()):.3f}")

print("\n" + "=" * 90, "\nDIAGNOSTIC 2 -- FULL 24H CLOCK x M-STRENGTH INTERACTION (3h bins)\n", "=" * 90, sep="")
merged["clock_3h"] = pd.cut(merged["hm"], bins=list(range(0, 2401, 300)),
                             labels=[f"{h:02d}-{h+3:02d}" for h in range(0, 24, 3)], include_lowest=True)
g2 = merged.groupby(["clock_3h", "M_strength_tercile"], observed=True).agg(
    n=("net_pnl", "size"), mean_pnl=("net_pnl", "mean"), sum_pnl=("net_pnl", "sum"),
    win_rate=("net_pnl", lambda x: float((x > 0).mean())))
print(g2.round(2))
g2.to_csv(os.path.join(OUT, "diag2_clock3h_x_Mstrength.csv"))

# per-clock-bin pooled, for reference / eyeballing where badness concentrates
g2b = merged.groupby("clock_3h", observed=True).agg(
    n=("net_pnl", "size"), mean_pnl=("net_pnl", "mean"), sum_pnl=("net_pnl", "sum"),
    win_rate=("net_pnl", lambda x: float((x > 0).mean())))
print("\npooled by 3h clock bin (reference, not conditioned):")
print(g2b.round(2))

print("\n" + "=" * 90, "\nDIAGNOSTIC 3 -- EXPLAIN S2's FAILURE: WHERE INSIDE EUROPE_PREUS IS THE LOSS CONCENTRATED?\n", "=" * 90, sep="")
in_win = merged[EUROPE_PREUS].copy()
in_win["substate"] = (in_win["M_strength_tercile"].astype(str) + "_M__" +
                       in_win["consensus_tercile"].astype(str) + "_consensus__" +
                       in_win["vol_tercile"].astype(str) + "_vol")
sub = in_win.groupby("substate", observed=True).agg(
    n=("net_pnl", "size"), mean_pnl=("net_pnl", "mean"), sum_pnl=("net_pnl", "sum"),
    win_rate=("net_pnl", lambda x: float((x > 0).mean()))).sort_values("sum_pnl")
sub = sub[sub["n"] >= 5]  # drop tiny cells, per directive's "broad, not isolated point" bar
print(sub.round(2).to_string())
sub.to_csv(os.path.join(OUT, "diag3_europreus_substates.csv"))

# year-by-year for the single worst substate found (if any negative cells exist)
worst = sub.index[0] if len(sub) and sub["sum_pnl"].iloc[0] < 0 else None
if worst:
    worst_rows = in_win[in_win["substate"] == worst]
    yby_worst = worst_rows.groupby("year")["net_pnl"].agg(["size", "sum", "mean"])
    print(f"\nyear-by-year for worst substate '{worst}':")
    print(yby_worst.round(2))
    n_neg_years = int((yby_worst["sum"] < 0).sum())
    print(f"negative in {n_neg_years}/{len(yby_worst)} years")

# is EUROPE_PREUS's pooled badness explained by ANY single conditioning variable alone, or does it
# persist even within the BEST cell of each variable (i.e. is there a "safe" substate)?
print("\nEUROPE_PREUS mean_pnl by M_strength_tercile alone (does strong-M rescue the window?):")
print(in_win.groupby("M_strength_tercile", observed=True)["net_pnl"].agg(["size", "mean", "sum"]).round(2))
print("\nEUROPE_PREUS mean_pnl by consensus_tercile alone:")
print(in_win.groupby("consensus_tercile", observed=True)["net_pnl"].agg(["size", "mean", "sum"]).round(2))
print("\nEUROPE_PREUS mean_pnl by long_short (does one side drive the pooled loss?):")
print(in_win.groupby("long_short", observed=True)["net_pnl"].agg(["size", "mean", "sum"]).round(2))

# year-by-year for the whole EUROPE_PREUS window itself, cross-checking S2's own pre-screen figures
yby_window = in_win.groupby("year")["net_pnl"].agg(["size", "sum", "mean"])
print("\nEUROPE_PREUS pooled year-by-year (cross-check vs S2 spec.yaml's own pre-screen numbers):")
print(yby_window.round(2))

json.dump({
    "pooled_in_window": {"n": int(len(pooled_in)), "mean": float(pooled_in["net_pnl"].mean()),
                          "sum": float(pooled_in["net_pnl"].sum())},
    "pooled_outside": {"n": int(len(pooled_out)), "mean": float(pooled_out["net_pnl"].mean()),
                        "sum": float(pooled_out["net_pnl"].sum())},
    "worst_substate_in_window": worst,
}, open(os.path.join(OUT, "diag_summary.json"), "w"), indent=2)

print("\nR3 diagnostic complete.")
