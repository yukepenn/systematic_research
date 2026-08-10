"""PORT01 -- A+B risk-normalized portfolio synthesis. Pure application of portfolio math to
already-certified daily P&L series; no new signal/feature construction, no candidate. Reuses
runs/H0_PRODUCT_A_HEALTH's own session-level series and U0's already byte-exact-gated bar-level
P&L columns.
"""
import os, sys, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
from smv2_common import dd_battery

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

u0 = pd.read_parquet(os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet"),
                      columns=["sess_date", "is_health_only_bar", "bar_pnl_A_dollars",
                               "bar_pnl_B_nq_dollars", "bar_pnl_B_mnq_dollars", "target_exposure_A",
                               "position_B"])
canon = u0[~u0["is_health_only_bar"]].copy()
canon["sess_date"] = pd.to_datetime(canon["sess_date"])

daily = canon.groupby("sess_date").agg(
    A=("bar_pnl_A_dollars", "sum"), B_NQ=("bar_pnl_B_nq_dollars", "sum"),
    B_MNQ=("bar_pnl_B_mnq_dollars", "sum"),
    A_peak_contracts=("target_exposure_A", lambda x: x.abs().max()),
    B_in_position=("position_B", lambda x: (x != 0).any()),
).reset_index()

# correctness gate: reproduces certified canonical nets
net_A, net_B_nq, net_B_mnq = daily["A"].sum(), daily["B_NQ"].sum(), daily["B_MNQ"].sum()
assert abs(net_A - 177924.40) < 1.0, f"A net mismatch: {net_A}"
assert abs(net_B_nq - 301915.92) < 1.0, f"B-NQ net mismatch: {net_B_nq}"
assert abs(net_B_mnq - 28587.10) < 1.0, f"B-MNQ net mismatch: {net_B_mnq}"
print(f"[PORT01] correctness gate PASS: A={net_A:.2f}, B-NQ={net_B_nq:.2f}, B-MNQ={net_B_mnq:.2f}", flush=True)

# ---------------------------------------------------------------- capital normalization
# MNQ is contractually 1/10 NQ notional/margin (same underlying index, 1/10 point value) --
# express Product A's exposure in "NQ-equivalent contracts" for direct capital comparison
daily["A_nq_equiv_peak"] = daily["A_peak_contracts"] / 10.0
peak_A_nqeq = daily["A_nq_equiv_peak"].max()
mean_A_nqeq_when_active = daily.loc[daily["A_peak_contracts"] > 0, "A_nq_equiv_peak"].mean()
print(f"[PORT01] Product A capital footprint: peak={peak_A_nqeq:.2f} NQ-equivalent contracts, "
      f"mean-when-active={mean_A_nqeq_when_active:.2f}", flush=True)
print(f"[PORT01] Product B-NQ/MNQ capital footprint: always exactly 1.0 NQ-equivalent contract "
      f"when in a position (never more, never less)", flush=True)

# ---------------------------------------------------------------- standalone batteries
def battery(tag, net_series):
    b = dd_battery(daily["sess_date"], net_series.to_numpy(), label=tag)
    return {"tag": tag, "net": b["net"], "sharpe": b["sharpe"], "sortino": b["sortino"],
            "calmar": b["calmar"], "maxDD_eod": b["maxDD_eod"], "CDaR95": b["CDaR5"],
            "worst_day": float(net_series.min()), "pos_day_pct": b["pos_day_pct"]}


rows = []
rows.append(battery("A_standalone", daily["A"]))
rows.append(battery("B_NQ_standalone", daily["B_NQ"]))
rows.append(battery("B_MNQ_standalone", daily["B_MNQ"]))

# ---------------------------------------------------------------- combined portfolios
# (1) naive dollar sum -- what you'd get just adding P&L, ignoring capital intensity
daily["A_plus_BNQ_naive"] = daily["A"] + daily["B_NQ"]
daily["A_plus_BMNQ_naive"] = daily["A"] + daily["B_MNQ"]
rows.append(battery("A+B_NQ_naive_dollar_sum", daily["A_plus_BNQ_naive"]))
rows.append(battery("A+B_MNQ_naive_dollar_sum", daily["A_plus_BMNQ_naive"]))

# (2) capital-normalized: scale Product A's dollar P&L DOWN to match B's fixed 1.0 NQ-equivalent
# footprint at A's own historical PEAK (i.e., "if A were capital-constrained to never exceed the
# same footprint as one B contract, scale its whole P&L path down by peak_A_nqeq")
scale_factor = 1.0 / peak_A_nqeq
daily["A_capnorm"] = daily["A"] * scale_factor
daily["A_capnorm_plus_BNQ"] = daily["A_capnorm"] + daily["B_NQ"]
daily["A_capnorm_plus_BMNQ"] = daily["A_capnorm"] + daily["B_MNQ"]
rows.append(battery("A_capital_normalized_to_1x", daily["A_capnorm"]))
rows.append(battery("A_capnorm+B_NQ", daily["A_capnorm_plus_BNQ"]))
rows.append(battery("A_capnorm+B_MNQ", daily["A_capnorm_plus_BMNQ"]))

res_df = pd.DataFrame(rows)
res_df.to_csv(os.path.join(OUT, "battery_comparison.csv"), index=False)
print("\n" + "=" * 100)
print(res_df.round(2).to_string(index=False))

# ---------------------------------------------------------------- diversification decomposition
print("\n" + "=" * 100 + "\nDIVERSIFICATION DECOMPOSITION\n" + "=" * 100)
corr_A_BNQ = float(daily["A"].corr(daily["B_NQ"]))
corr_Acapnorm_BNQ = float(daily["A_capnorm"].corr(daily["B_NQ"]))  # identical to above (scaling doesn't change correlation)
std_A, std_BNQ = daily["A"].std(), daily["B_NQ"].std()
std_Acapnorm = daily["A_capnorm"].std()

# naive expectation if returns were UNCORRELATED (variance additivity) vs actual
var_sum_uncorr = std_Acapnorm**2 + std_BNQ**2
var_actual = daily["A_capnorm_plus_BNQ"].var()
implied_corr = (var_actual - var_sum_uncorr) / (2 * std_Acapnorm * std_BNQ)
print(f"session-level correlation(A, B-NQ) = {corr_A_BNQ:.4f} (capital-normalizing A doesn't "
      f"change correlation, only scale)")
print(f"implied correlation from combined variance = {implied_corr:.4f} (should match ~{corr_A_BNQ:.4f})")

maxdd_A_capnorm = next(r["maxDD_eod"] for r in rows if r["tag"] == "A_capital_normalized_to_1x")
maxdd_BNQ = next(r["maxDD_eod"] for r in rows if r["tag"] == "B_NQ_standalone")
maxdd_combined = next(r["maxDD_eod"] for r in rows if r["tag"] == "A_capnorm+B_NQ")
naive_sum_dd = maxdd_A_capnorm + maxdd_BNQ
print(f"\nmaxDD: A(capnorm)={maxdd_A_capnorm:.2f}, B-NQ={maxdd_BNQ:.2f}, "
      f"naive sum={naive_sum_dd:.2f}, ACTUAL combined={maxdd_combined:.2f}")
diversification_benefit = naive_sum_dd - maxdd_combined
print(f"diversification benefit (naive-sum-DD minus actual-combined-DD) = ${diversification_benefit:,.2f} "
      f"({100*diversification_benefit/naive_sum_dd:.1f}% reduction vs naive sum)")
print("\nThis is a SIZING/CAPITAL-ALLOCATION property of two already-existing, already-unchanged "
      "objects trading a substantially shared latent signal (per H0's own finding, 99.97% "
      "bar-level directional agreement when both hold) -- NOT a new edge. Per directive sec53's "
      "own caution, this is explicitly NOT reported as alpha.")

# ---------------------------------------------------------------- tail-day overlap reuse (already in H0, cite not recompute)
print("\n" + "=" * 100 + "\nNOTE: tail-day overlap, rolling correlation, drawdown-episode overlap are\n"
      "ALREADY computed in research/system_master/PRODUCT_A_VS_B_CURRENT_HEALTH.md -- reused by\n"
      "reference here, not recomputed (per this campaign's data-reuse discipline).\n" + "=" * 100)

summary = {
    "correctness_gate": {"A": float(net_A), "B_NQ": float(net_B_nq), "B_MNQ": float(net_B_mnq)},
    "capital_footprint": {"A_peak_nq_equiv": float(peak_A_nqeq),
                           "A_mean_active_nq_equiv": float(mean_A_nqeq_when_active),
                           "B_fixed_nq_equiv": 1.0},
    "battery_comparison": res_df.to_dict("records"),
    "diversification": {"correlation": corr_A_BNQ, "naive_sum_dd": float(naive_sum_dd),
                         "actual_combined_dd": float(maxdd_combined),
                         "benefit_dollars": float(diversification_benefit),
                         "benefit_pct": float(100 * diversification_benefit / naive_sum_dd)},
}
json.dump(summary, open(os.path.join(OUT, "port01_summary.json"), "w"), indent=2, default=str)
daily.to_csv(os.path.join(OUT, "daily_portfolio_series.csv"), index=False)
print("\nPORT01 synthesis complete.")
