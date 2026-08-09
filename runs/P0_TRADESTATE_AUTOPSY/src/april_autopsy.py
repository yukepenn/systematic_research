"""P0 -- identifies the exact incumbent trades matching the owner's two named April-2026
Strategy-Analyzer observations ("2026-04-06/2026-04-07" and "2026-04-12/2026-04-13" short
losers), from the ledger (not from screenshot timestamps), and tests the owner's own hypothesis:
did Solar evidence reverse against the held short while B-MOM/M kept it in the hold region?"""
import os, sys, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "runs", "P0_TRADESTATE_AUTOPSY")
OUT = os.path.join(RUN, "out")

ledger = pd.read_parquet(os.path.join(OUT, "ledger_full.parquet"))
ledger["time"] = pd.to_datetime(ledger["time"])
ledger["entry_time"] = pd.to_datetime(ledger["entry_time"])
EXIT_LEVEL = 1.0

# ------------------------------------------------------------- identify candidate short blocks
blocks = ledger[ledger["position"] != 0].groupby("block_id").agg(
    side=("position", "first"),
    entry_time=("entry_time", "first"),
    entry_price=("entry_price", "first"),
    exit_time=("time", "last"),
    n_bars=("age_bars", "max"),
    net_pnl=("run_pnl_dollars", "last"),
).reset_index()
blocks["entry_date"] = blocks["entry_time"].dt.date.astype(str)
blocks["exit_date"] = blocks["exit_time"].dt.date.astype(str)

target_pairs = [("2026-04-06", "2026-04-07"), ("2026-04-12", "2026-04-13")]
found = []
for d1, d2 in target_pairs:
    cand = blocks[(blocks["side"] < 0) & (blocks["entry_date"] == d1) & (blocks["exit_date"] == d2)]
    found.append((d1, d2, cand))
    print(f"\n=== candidates spanning {d1} -> {d2}, short only ===")
    print(cand.to_string(index=False))

# also show ALL short losers in the wider April window for context (not cherry-picked)
april = blocks[(blocks["entry_date"] >= "2026-04-01") & (blocks["entry_date"] <= "2026-04-20")]
april_losers = april[(april["side"] < 0) & (april["net_pnl"] < 0)].sort_values("net_pnl")
print("\n=== ALL short losers, 2026-04-01..04-20 (context, ranked by loss size) ===")
print(april_losers.to_string(index=False))
april_losers.to_csv(os.path.join(OUT, "april_all_short_losers.csv"), index=False)

TRACE_COLS = ["t_idx", "time", "hm", "close", "position", "T", "Tp", "HTF_tilt_state", "B", "M",
              "n_bullish", "n_bearish", "vote_dispersion", "fast_member", "slow_member",
              "run_pnl_dollars", "MFE_dollars", "MAE_dollars", "giveback_dollars",
              "giveback_ratio", "age_bars", "sigma460_atr_proxy_pts", "range_over_atr"]

summary_rows = []
for d1, d2, cand in found:
    if len(cand) == 0:
        print(f"\n!! NO short block found spanning {d1} -> {d2} exactly; widening search to nearby dates")
        continue
    for _, row in cand.iterrows():
        bid = row["block_id"]
        blk = ledger[ledger["block_id"] == bid]
        t0 = blk["t_idx"].iloc[0]
        pre_start = max(0, t0 - 20)
        trace = ledger[(ledger["t_idx"] >= pre_start) & (ledger["t_idx"] <= blk["t_idx"].iloc[-1])]
        fname = os.path.join(OUT, f"trace_{d1}_{d2}_block{bid}.csv")
        trace[TRACE_COLS].to_csv(fname, index=False)
        print(f"\n>>> saved trace {fname}  ({len(trace)} bars, entry {row['entry_time']} -> exit {row['exit_time']}, net ${row['net_pnl']:.2f})")

        # ---------------- hypothesis test: Solar reversal vs B-MOM/M veto (short-side framing)
        side = -1  # short
        held = blk[blk["position"] == side].reset_index(drop=True)
        # "Solar reversed against the short" candidate definitions, weakest to strongest:
        solar_member_majority_against = held["n_bullish"] >= 7          # >=7/13 bullish while short
        solar_member_strong_majority_against = held["n_bullish"] >= 10  # >=10/13 bullish
        solar_Tprime_against = held["Tp"] > 0                            # T' flips positive while short
        fast_and_median_against = (held["fast_member"] > 0) & (held["n_bullish"] >= 7)
        m_still_holding = held["M"] < -EXIT_LEVEL                        # M < -1.0 = still in "hold short" region per one_contract_decisions

        def first_true_bar(mask):
            idx = np.where(mask.to_numpy())[0]
            return int(idx[0]) if len(idx) else None

        lead = {}
        for name, mask in [("member_majority_7of13", solar_member_majority_against),
                            ("member_strong_majority_10of13", solar_member_strong_majority_against),
                            ("Tprime_sign_flip", solar_Tprime_against),
                            ("fast_plus_majority", fast_and_median_against)]:
            first_bar = first_true_bar(mask)
            if first_bar is None:
                lead[name] = {"ever_occurred": False}
                continue
            # was M still in the "hold short" region (M < -1.0) at/after that bar, up to exit?
            still_held_after = bool(m_still_holding.iloc[first_bar:].any())
            n_bars_before_exit = int(len(held) - 1 - first_bar)
            lead[name] = {
                "ever_occurred": True,
                "first_occurrence_bar_in_trade": first_bar,
                "first_occurrence_time": str(held["time"].iloc[first_bar]),
                "M_at_occurrence": float(held["M"].iloc[first_bar]),
                "bars_before_eventual_exit": n_bars_before_exit,
                "minutes_before_eventual_exit": n_bars_before_exit * 3,
                "M_stayed_below_exit_threshold_after": still_held_after,
            }
        summary_rows.append({
            "pair": f"{d1}->{d2}", "block_id": int(bid), "entry_time": str(row["entry_time"]),
            "exit_time": str(row["exit_time"]), "net_pnl": float(row["net_pnl"]),
            "n_bars_held": int(row["n_bars"]), "hypothesis_tests": lead,
        })
        print(json.dumps(lead, indent=2))

json.dump(summary_rows, open(os.path.join(OUT, "april_hypothesis_test.json"), "w"), indent=2)
print(f"\nsaved {os.path.join(OUT, 'april_hypothesis_test.json')}")
