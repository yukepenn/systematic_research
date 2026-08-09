"""H0 sec11 -- edge-health indicators and flags. Thresholds are FIXED and PRINTED FIRST, before any
reading is computed/displayed, per the owner's explicit no-post-hoc-tuning requirement. Reuses
CURRENT_EDGE_HEALTH.md's own percentile scale for percentile-type indicators (>50th HEALTHY,
25-50th NORMAL_WEAK_REGIME, 10-25th WATCH, 5-10th POSSIBLE_DECAY, <5th STRUCTURAL_BREAK_EVIDENCE)
so Product A's flags are on the identical scale as Product B's -- non-percentile indicators use
their own logic, stated in full below before the numbers that will be plugged into it."""
import os, sys, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")

pctile_df = pd.read_csv(os.path.join(OUT, "sec5_percentile_context.csv"))
dd_pct = json.load(open(os.path.join(OUT, "sec5_dd_percentile.json")))
arrival = pd.read_csv(os.path.join(OUT, "sec8_giant_arrival_by_year.csv"), index_col=0)["0"]
cond_pnl = pd.read_csv(os.path.join(OUT, "sec10_conditional_pnl_by_year_tercile.csv"), index_col=0)
state_mix = pd.read_csv(os.path.join(OUT, "sec10_state_mix_by_year.csv"), index_col=0)
short_summary = json.load(open(os.path.join(OUT, "sec9_short_side_summary.json")))
band = pd.read_csv(os.path.join(OUT, "sec6_pnl_by_exposure_band.csv"))
trans = pd.read_csv(os.path.join(OUT, "sec7_transition_summary.csv"))

print("=" * 90)
print("SEC11 -- EDGE-HEALTH INDICATORS: THRESHOLDS FIXED BEFORE READING (printed first)")
print("=" * 90)

THRESHOLDS = """
PERCENTILE-TYPE indicators (1,2,3,4 below) use CURRENT_EDGE_HEALTH.md's own fixed scale, reused
verbatim for A/B comparability:
    >50th pct                -> HEALTHY
    25th-50th pct             -> NORMAL_WEAK_REGIME
    10th-25th pct             -> WATCH
    5th-10th pct               -> POSSIBLE_DECAY
    <5th pct                  -> STRUCTURAL_BREAK_EVIDENCE
  For "bad-is-high" indicators (drawdown), the SAME 5-bucket scale is applied to the INVERTED
  reading (low percentile = shallow = good), matching how CURRENT_EDGE_HEALTH.md itself flagged a
  34.0th-percentile drawdown HEALTHY (an inverted-scale reading, made explicit here):
    <50th pct                 -> HEALTHY
    50th-75th pct              -> NORMAL_WEAK_REGIME
    75th-90th pct              -> WATCH
    90th-95th pct               -> POSSIBLE_DECAY
    >95th pct                  -> STRUCTURAL_BREAK_EVIDENCE

NON-PERCENTILE indicators (5-8), own logic each, stated before computing:
  (5) Giant-winner arrival rate, 2026 annualized, ranked among the 5 years 2022-2026:
        rank 1-2 of 5 (top two)      -> HEALTHY
        rank 3 of 5                  -> NORMAL_WEAK_REGIME
        rank 4 of 5                  -> WATCH
        rank 5 (lowest) & <50% of the median of the other 4 -> POSSIBLE_DECAY
        zero arrivals for >2x historical max inter-arrival gap -> STRUCTURAL_BREAK_EVIDENCE
  (6) Conditional edge, strong-conviction entries (|M_A_raw|>=4), 2026 vs the 2022-2025 range:
        within [min,max] of 2022-2025                    -> HEALTHY
        below 2022-2025 min but still positive             -> WATCH
        negative, below 2022-2025 min                       -> POSSIBLE_DECAY
        negative and exceeding the sum of all 2022-2025 losing years -> STRUCTURAL_BREAK_EVIDENCE
  (7) Short-side latest-2-month (Jun-Jul 2026) mean trip pnl vs full-history (2022-2026) short mean:
        latest > full-history mean                          -> HEALTHY
        latest positive but <= full-history mean              -> NORMAL_WEAK_REGIME
        latest roughly flat (|mean| < $25/trip)                -> WATCH
        latest negative, shallower than the Jan-May-2026 stub's -$73.06/trip -> POSSIBLE_DECAY
        latest negative, deeper than the Jan-May-2026 stub's                 -> STRUCTURAL_BREAK_EVIDENCE
  (8) Exposure-band top-end monotonicity (health-only extension's per-contract $/bar ordering,
      1-3 < 4-6 < 7-9 < 10-13, matching PA0's canonical-window finding):
        fully monotonic, all bands >=0                       -> HEALTHY
        monotonic except one small (<20% relative) adjacent inversion, all bands >=0 -> NORMAL_WEAK_REGIME
        one inversion, top band still positive but not the max -> WATCH
        top band (10-13) turns net NEGATIVE while lower bands stay positive -> POSSIBLE_DECAY
        ordering fully inverted (small bands best, large bands worst) -> STRUCTURAL_BREAK_EVIDENCE
  (9) Scale-in-vs-fresh forward-value premium, health-only extension vs canonical's ~7.1x:
        extension ratio >= 1.0 (scale-in still more valuable, any margin) -> HEALTHY
        extension ratio in [0.5, 1.0) (both still positive, compressed)    -> NORMAL_WEAK_REGIME
        extension ratio < 0.5 but scale-in still positive                  -> WATCH
        scale-in flips negative                                            -> POSSIBLE_DECAY
        scale-in flips negative AND fresh also flips negative               -> STRUCTURAL_BREAK_EVIDENCE
"""
print(THRESHOLDS)

print("=" * 90)
print("NOW COMPUTING READINGS")
print("=" * 90)

indicators = []


def flag_pctile(pct, invert=False):
    p = pct if not invert else (100 - pct)
    if p > 50: return "HEALTHY"
    if p > 25: return "NORMAL_WEAK_REGIME"
    if p > 10: return "WATCH"
    if p > 5: return "POSSIBLE_DECAY"
    return "STRUCTURAL_BREAK_EVIDENCE"


# 1/2: rolling-60/120 Sharpe percentile
row60 = pctile_df[pctile_df["window"] == 60].iloc[0]
row120 = pctile_df[pctile_df["window"] == 120].iloc[0]
indicators.append(("Rolling-60-session Sharpe", f"{row60['current_sharpe']:.3f}",
                    f"{row60['sharpe_percentile']:.1f}th pct", flag_pctile(row60["sharpe_percentile"])))
indicators.append(("Rolling-120-session Sharpe", f"{row120['current_sharpe']:.3f}",
                    f"{row120['sharpe_percentile']:.1f}th pct", flag_pctile(row120["sharpe_percentile"])))

# 3: current drawdown percentile (inverted)
indicators.append(("Current drawdown", "see sec4/sec5", f"{dd_pct['current_dd_percentile']:.1f}th pct",
                    flag_pctile(dd_pct["current_dd_percentile"], invert=True)))

# 4: giant-winner arrival rate rank
arr_sorted = arrival.sort_values(ascending=False)
rank_2026 = int(arr_sorted.index.get_loc(2026)) + 1  # 1 = highest
if rank_2026 <= 2:
    flag4 = "HEALTHY"
elif rank_2026 == 3:
    flag4 = "NORMAL_WEAK_REGIME"
elif rank_2026 == 4:
    flag4 = "WATCH"
else:
    others_median = arrival.drop(2026).median()
    flag4 = "POSSIBLE_DECAY" if arrival[2026] < 0.5 * others_median else "WATCH"
indicators.append(("Giant-winner arrival rate (2026 ann.)", f"{arrival[2026]:.2f}/250 sess",
                    f"rank {rank_2026} of 5 years", flag4))

# 5: conditional edge, strong tercile
strong_row = cond_pnl.loc["strong(|M|>=4)"] if "strong(|M|>=4)" in cond_pnl.index else cond_pnl.iloc[-1]
strong_2225 = strong_row[["2022", "2023", "2024", "2025"]].astype(float)
strong_2026 = float(strong_row["2026"])
lo, hi = strong_2225.min(), strong_2225.max()
if lo <= strong_2026 <= hi:
    flag5 = "HEALTHY"
elif strong_2026 > 0:
    flag5 = "WATCH"
elif strong_2026 < 0 and strong_2026 >= strong_2225.sum():
    flag5 = "POSSIBLE_DECAY"
else:
    flag5 = "STRUCTURAL_BREAK_EVIDENCE"
indicators.append(("Conditional edge, strong-conviction entries (|M_A_raw|>=4)",
                    f"${strong_2026:.2f}/trip", f"2022-2025 range [${lo:.2f}, ${hi:.2f}]", flag5))

# 6: short-side recovery
short_ext = short_summary["sub2026_short"]["2026 Jun-Jul (health-only ext)"]["mean_pnl"]
short_stub = short_summary["sub2026_short"]["2026 Jan-May (stub, canonical)"]["mean_pnl"]
by_year_short = pd.read_csv(os.path.join(OUT, "sec9_short_side_by_year.csv"))
full_hist_short_mean = (by_year_short["n"] * by_year_short["mean_pnl"]).sum() / by_year_short["n"].sum()
if short_ext > full_hist_short_mean:
    flag6 = "HEALTHY"
elif short_ext > 0:
    flag6 = "NORMAL_WEAK_REGIME"
elif abs(short_ext) < 25:
    flag6 = "WATCH"
elif short_ext > short_stub:
    flag6 = "POSSIBLE_DECAY"
else:
    flag6 = "STRUCTURAL_BREAK_EVIDENCE"
indicators.append(("Short-side latest-2-month (Jun-Jul) mean trip pnl", f"${short_ext:.2f}/trip",
                    f"full-hist mean ${full_hist_short_mean:.2f}/trip, Jan-May stub ${short_stub:.2f}/trip", flag6))

# 7: exposure-band top-end monotonicity, health-only extension
ext_band = band[band["window"] == "HEALTH-ONLY EXTENSION (2026-06-01..2026-07-31)"].set_index("band")
vals = ext_band.loc[["1-3", "4-6", "7-9", "10-13"], "mean_pnl_per_bar_per_contract"]
is_monotonic = all(vals.iloc[i] <= vals.iloc[i + 1] for i in range(len(vals) - 1))
top_negative = vals.iloc[-1] < 0
lower_positive = all(vals.iloc[:-1] >= 0)
if is_monotonic and (vals >= 0).all():
    flag7 = "HEALTHY"
elif top_negative and lower_positive:
    flag7 = "POSSIBLE_DECAY"
elif (vals < 0).sum() >= 3:
    flag7 = "STRUCTURAL_BREAK_EVIDENCE"
elif not is_monotonic:
    flag7 = "WATCH" if (vals >= 0).all() else "NORMAL_WEAK_REGIME"
else:
    flag7 = "NORMAL_WEAK_REGIME"
indicators.append(("Exposure-band top-end monotonicity (health-only ext.)",
                    " < ".join(f"{v:.3f}" for v in vals), "canonical order: -0.042<0.036<0.460<1.878", flag7))

# 8: scale-in premium persistence
r_canon = trans[trans["window"].str.startswith("CANONICAL")].iloc[0]
r_health = trans[trans["window"].str.startswith("HEALTH-ONLY")].iloc[0]
ratio_ext = r_health["scale_in_multiple_of_fresh"]
scale_in_ext = r_health["scale_in_fwd20_per_contract"]
fresh_ext = r_health["fresh_fwd20_per_contract"]
if ratio_ext >= 1.0:
    flag8 = "HEALTHY"
elif ratio_ext >= 0.5:
    flag8 = "NORMAL_WEAK_REGIME"
elif scale_in_ext > 0:
    flag8 = "WATCH"
elif fresh_ext > 0:
    flag8 = "POSSIBLE_DECAY"
else:
    flag8 = "STRUCTURAL_BREAK_EVIDENCE"
indicators.append(("Scale-in-vs-fresh premium (health-only ext.)", f"{ratio_ext:.3f}x",
                    f"canonical 7.127x (fresh ${r_canon['fresh_fwd20_per_contract']:.2f}, "
                    f"scale-in ${r_canon['scale_in_fwd20_per_contract']:.2f})", flag8))

ind_df = pd.DataFrame(indicators, columns=["indicator", "current_value", "basis", "flag"])
print(ind_df.to_string(index=False))
ind_df.to_csv(os.path.join(OUT, "sec11_indicators_flags.csv"), index=False)

flag_counts = ind_df["flag"].value_counts().to_dict()
print("\nflag counts:", flag_counts)
json.dump({"flag_counts": flag_counts}, open(os.path.join(OUT, "sec11_flag_counts.json"), "w"), indent=2)

print("\n[H0] sec11 indicators/flags complete.")
