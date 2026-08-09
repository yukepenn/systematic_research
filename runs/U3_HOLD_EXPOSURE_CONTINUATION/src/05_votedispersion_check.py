"""U3 step 5 -- secondary candidate check: vote_dispersion (Solar13 consensus spread) as a
state-only (non-transition) continuation-value lead from point 1's bucket scan. Same chronology +
right-tail discipline as step 4, applied to this second candidate."""
import os
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(ROOT, "runs", "U3_HOLD_EXPOSURE_CONTINUATION", "out")


def run_leg(tag):
    print(f"\n{'=' * 90}\n{tag}: vote_dispersion chronology (fwd_5, mean $, low vs high tercile)\n{'=' * 90}")
    hold = pd.read_parquet(os.path.join(OUT, f"hold_{tag}.parquet"))
    canon = hold[~hold.is_health_only_bar]
    rows = []
    for yr, g in canon.groupby("year"):
        low = g[g.vote_dispersion_tercile == "low"]["fwd_5"]
        high = g[g.vote_dispersion_tercile == "high"]["fwd_5"]
        rows.append({"year": yr, "low_n": len(low), "low_mean": low.mean(),
                      "high_n": len(high), "high_mean": high.mean(), "high_minus_low": high.mean() - low.mean()})
    health = hold[hold.is_health_only_bar]
    low_h = health[health.vote_dispersion_tercile == "low"]["fwd_5"]
    high_h = health[health.vote_dispersion_tercile == "high"]["fwd_5"]
    rows.append({"year": "2026-06/07 (HEALTH-ONLY)", "low_n": len(low_h), "low_mean": low_h.mean(),
                 "high_n": len(high_h), "high_mean": high_h.mean(), "high_minus_low": high_h.mean() - low_h.mean()})
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, f"votedispersion_chronology_{tag}.csv"), index=False)
    print(df.round(2).to_string(index=False))

    n_years_positive = int((df.iloc[:5]["high_minus_low"] > 0).sum())
    print(f"\nhigh > low in {n_years_positive}/5 canonical years")

    # right-tail check: what fraction of top-20 winners' HOLD bars sit in the LOW dispersion
    # (flagged-weak) tercile?
    block = pd.read_csv(os.path.join(OUT, f"block_table_{tag}.csv"))
    canon_blocks = block[~block.is_health_only_bar].dropna(subset=["net_pnl"])
    top20 = canon_blocks.nlargest(20, "net_pnl")
    top20_bars = hold[hold.block_id.isin(top20.block_id)]
    frac_low = (top20_bars.vote_dispersion_tercile == "low").mean()
    frac_low_pop = (canon.vote_dispersion_tercile == "low").mean()
    print(f"\nfraction of top-20 winners' HOLD bars in LOW vote_dispersion tercile: {frac_low:.3f} "
          f"(population baseline: {frac_low_pop:.3f})")

    # per-block: does each top-20 winner have a NET NEGATIVE bar_pnl sum during its own low-dispersion bars?
    tail_rows = []
    for bid in top20.block_id:
        bars = hold[(hold.block_id == bid) & (hold.vote_dispersion_tercile == "low")]
        if len(bars):
            tail_rows.append({"block_id": bid, "n_low_disp_bars": len(bars),
                               "sum_bar_pnl_low_disp": bars.bar_pnl.sum()})
    tail_df = pd.DataFrame(tail_rows)
    tail_df.to_csv(os.path.join(OUT, f"votedispersion_righttail_{tag}.csv"), index=False)
    print(tail_df.round(2).to_string(index=False))
    if len(tail_df):
        n_neg = int((tail_df.sum_bar_pnl_low_disp < 0).sum())
        print(f"{n_neg}/{len(tail_df)} top-20 winners net NEGATIVE during their own low-dispersion hold bars")


run_leg("B")
run_leg("A")
print("\n05_votedispersion_check.py complete.")
