"""H0 sec9 -- short-side year-by-year + 2026 Jan-May-stub vs Jun-Jul-extension split (mirrors SA0
sec18's short-side deep dive, Product-A version -- Product A has its own short-halving overlay so
this is not a re-derivation of Product B's finding). sec10 -- state-mix stability: P(entry M_A_raw
tercile | year), does Product A see a different mix of entry-quality opportunities in 2026 (mirrors
SA0 sec9's distribution-shift-vs-relationship-shift test)."""
import os, sys, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
trips = pd.read_csv(os.path.join(OUT, "trip_ledger_A.csv"), parse_dates=["entry_sess", "exit_sess"])
CANONICAL_END = pd.Timestamp("2026-05-31")

# ============================================================== SEC9 -- SHORT-SIDE DEEP DIVE
print("=" * 90, "\nSEC9 -- SHORT-SIDE (Product A) YEAR-BY-YEAR + 2026 SPLIT\n", "=" * 90, sep="")
shorts = trips[trips["side"] < 0].copy()
by_year = shorts.groupby("year").agg(n=("net_pnl", "size"), mean_pnl=("net_pnl", "mean"),
                                      sum_pnl=("net_pnl", "sum"),
                                      win_rate=("net_pnl", lambda x: float((x > 0).mean())))
print(by_year.round(2))
by_year.to_csv(os.path.join(OUT, "sec9_short_side_by_year.csv"))

y2026_shorts = shorts[shorts["year"] == 2026].copy()
y2026_shorts["sub_period"] = np.where(y2026_shorts["entry_sess"] <= CANONICAL_END,
                                       "2026 Jan-May (stub, canonical)", "2026 Jun-Jul (health-only ext)")
sub2026 = y2026_shorts.groupby("sub_period").agg(n=("net_pnl", "size"), mean_pnl=("net_pnl", "mean"),
                                                  sum_pnl=("net_pnl", "sum"),
                                                  win_rate=("net_pnl", lambda x: float((x > 0).mean())))
print("\n2026 short-side split (Product A):")
print(sub2026.round(2))
sub2026.to_csv(os.path.join(OUT, "sec9_short_side_2026_split.csv"))

# long-side comparison for the same split (context)
longs = trips[trips["side"] > 0].copy()
y2026_longs = longs[longs["year"] == 2026].copy()
y2026_longs["sub_period"] = np.where(y2026_longs["entry_sess"] <= CANONICAL_END,
                                      "2026 Jan-May (stub, canonical)", "2026 Jun-Jul (health-only ext)")
sub2026_long = y2026_longs.groupby("sub_period").agg(n=("net_pnl", "size"), mean_pnl=("net_pnl", "mean"),
                                                       sum_pnl=("net_pnl", "sum"),
                                                       win_rate=("net_pnl", lambda x: float((x > 0).mean())))
print("\n2026 long-side split (Product A), for context:")
print(sub2026_long.round(2))

short_summary = {
    "by_year": by_year.round(2).to_dict(orient="index"),
    "sub2026_short": sub2026.round(2).to_dict(orient="index"),
    "sub2026_long": sub2026_long.round(2).to_dict(orient="index"),
}
json.dump(short_summary, open(os.path.join(OUT, "sec9_short_side_summary.json"), "w"), indent=2, default=str)

# ============================================================== SEC10 -- STATE-MIX STABILITY
print("\n" + "=" * 90, "\nSEC10 -- STATE-MIX STABILITY: P(entry |M_A_raw| tercile | year)\n", "=" * 90, sep="")
trips["M_abs"] = trips["entry_M_A_raw"].abs()
# NOTE: M_A_raw is the ROUNDED/CLAMPED desired exposure before C4 partial-size gating (integer-
# valued, verified: np.allclose(M_A_raw, round(M_A_raw)) == True across all 540,232 bars) -- NOT a
# continuous pre-round score despite UNIFIED_STATE_MAP.md's column description. 82% of Product-A
# trip entries occur at exactly |M_A_raw|==1 (the natural minimal-conviction entry, since Product
# A's discrete decision has no separate entry threshold above 0 the way Product B's ENTRY_LEVEL=3
# does -- ANY nonzero rounded M triggers entry). This concentration makes a standard qcut tercile
# split degenerate (33rd/50th/67th percentiles all land on 1.0) -- fixed conviction bins used
# instead: 1 (minimal/threshold), 2-3 (moderate), >=4 (strong, requires B-MOM alignment or HTF-tilt
# boost to reach). Fixed BEFORE inspecting by-year results below.
bins = [-0.5, 1.5, 3.5, 20]
labels = ["weak(|M|=1)", "mid(|M|=2-3)", "strong(|M|>=4)"]
trips["M_tercile"] = pd.cut(trips["M_abs"], bins=bins, labels=labels)

state_freq = trips.groupby(["year", "M_tercile"], observed=True).size().groupby(level=0).apply(lambda x: x / x.sum())
print("P(M_tercile | year) -- distribution of entry quality by year:")
print(state_freq.unstack().round(3))
state_freq.unstack().to_csv(os.path.join(OUT, "sec10_state_mix_by_year.csv"))

print("\nconditional mean trip net_pnl BY M_tercile BY year (does 2026 pay worse for the same state?):")
cond = trips.groupby(["M_tercile", "year"], observed=True)["net_pnl"].agg(["size", "mean"]).reset_index()
piv = cond.pivot(index="M_tercile", columns="year", values="mean")
print(piv.round(2))
piv_n = cond.pivot(index="M_tercile", columns="year", values="size")
print("\n(n per cell)")
print(piv_n)
piv.to_csv(os.path.join(OUT, "sec10_conditional_pnl_by_year_tercile.csv"))

print("\n[H0] sec9/sec10 complete.")
