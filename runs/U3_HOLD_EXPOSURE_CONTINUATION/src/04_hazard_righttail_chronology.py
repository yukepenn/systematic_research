"""U3 step 4 -- hazard framing (point 3), chronology + health-only extension (point 4), and the
mandatory right-tail check (standing rigor) for the single strongest finding: overnight-entered
positions (ETH_ASIA/ETH_EUROPE) show depressed/negative fixed-horizon continuation value WHILE
STILL in the overnight session, which recovers sharply once the session transitions into RTH
(established descriptively in 03_transition_analysis.py). This is a MEASUREMENT INSTRUMENT only,
explicitly not a production rule (spec.yaml construction_gate: none authorized)."""
import os
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(ROOT, "runs", "U3_HOLD_EXPOSURE_CONTINUATION", "out")

OVERNIGHT_PHASES = {"ETH_ASIA", "ETH_EUROPE"}
RTH_PHASES = {"RTH_OPEN", "RTH_MID", "RTH_CLOSE"}


def hazard_row(g, label):
    row = {"label": label, "n": len(g)}
    for N in [5, 10, 20]:
        y = g[f"fwd_{N}"]
        row[f"P(fwd_{N}>0)"] = float((y > 0).mean())
        row[f"P(reversal_within_{N})"] = float(g[f"reversal_within_{N}"].mean())
    return row


def run_leg(tag):
    print(f"\n{'=' * 90}\n{tag}: HAZARD FRAMING (point 3)\n{'=' * 90}", flush=True)
    hold = pd.read_parquet(os.path.join(OUT, f"hold_{tag}.parquet"))
    block = pd.read_csv(os.path.join(OUT, f"block_table_{tag}.csv"))
    hold = hold.merge(block[["block_id", "entry_session_phase", "net_pnl"]], on="block_id", how="left")
    canon = hold[~hold.is_health_only_bar].copy()

    rows = []
    rows.append(hazard_row(canon, "ALL HOLD bars (baseline)"))
    for s, lbl in [(1, "side=long"), (-1, "side=short")]:
        rows.append(hazard_row(canon[canon.side == s], lbl))
    for b in ["low", "mid", "high"]:
        rows.append(hazard_row(canon[canon.vote_dispersion_tercile == b], f"vote_dispersion={b}"))
    for b in ["low", "mid", "high"]:
        rows.append(hazard_row(canon[canon.vol_tercile == b], f"vol_tercile={b}"))
    for b in [True, False]:
        rows.append(hazard_row(canon[canon.B_engaged == b], f"B_engaged={b}"))

    overnight_blocks = canon[canon.entry_session_phase.isin(OVERNIGHT_PHASES)]
    still_on = overnight_blocks[overnight_blocks.session_phase.isin(OVERNIGHT_PHASES)]
    now_rth = overnight_blocks[overnight_blocks.session_phase.isin(RTH_PHASES)]
    rows.append(hazard_row(still_on, "OVERNIGHT-ENTRY, still overnight (flagged state)"))
    rows.append(hazard_row(now_rth, "OVERNIGHT-ENTRY, transitioned to RTH"))

    hz = pd.DataFrame(rows)
    hz.to_csv(os.path.join(OUT, f"hazard_table_{tag}.csv"), index=False)
    print(hz.round(4).to_string(index=False))

    # -----------------------------------------------------------------
    # chronology of the flagged state (canonical years, separately 2026 health-only)
    # -----------------------------------------------------------------
    print(f"\n--- {tag}: chronology of the flagged state (fwd_5, mean $) ---")
    chrono_rows = []
    for yr, g in canon.groupby("year"):
        ob = g[g.entry_session_phase.isin(OVERNIGHT_PHASES)]
        so = ob[ob.session_phase.isin(OVERNIGHT_PHASES)]
        nr = ob[ob.session_phase.isin(RTH_PHASES)]
        chrono_rows.append({"year": yr, "still_overnight_n": len(so), "still_overnight_mean_fwd5": so.fwd_5.mean(),
                             "transitioned_rth_n": len(nr), "transitioned_rth_mean_fwd5": nr.fwd_5.mean()})
    # health-only extension (2026-06/07), reported separately, never blended
    health = hold[hold.is_health_only_bar]
    ob_h = health[health.entry_session_phase.isin(OVERNIGHT_PHASES)]
    so_h = ob_h[ob_h.session_phase.isin(OVERNIGHT_PHASES)]
    nr_h = ob_h[ob_h.session_phase.isin(RTH_PHASES)]
    chrono_rows.append({"year": "2026-06/07 (HEALTH-ONLY, observational)", "still_overnight_n": len(so_h),
                         "still_overnight_mean_fwd5": so_h.fwd_5.mean(), "transitioned_rth_n": len(nr_h),
                         "transitioned_rth_mean_fwd5": nr_h.fwd_5.mean()})
    chrono_df = pd.DataFrame(chrono_rows)
    chrono_df.to_csv(os.path.join(OUT, f"chronology_overnight_hold_{tag}.csv"), index=False)
    print(chrono_df.round(2).to_string(index=False))

    # -----------------------------------------------------------------
    # mandatory right-tail check: top-20 all-time winning blocks (canonical window)
    # -----------------------------------------------------------------
    print(f"\n--- {tag}: RIGHT-TAIL CHECK on top-20 all-time winning blocks (canonical) ---")
    canon_blocks = block[~block.is_health_only_bar].dropna(subset=["net_pnl"])
    top20 = canon_blocks.nlargest(20, "net_pnl")
    top20_overnight = top20[top20.entry_session_phase.isin(OVERNIGHT_PHASES)]
    print(f"{len(top20_overnight)}/20 top winners were entered overnight (ETH_ASIA/ETH_EUROPE)")

    # for each such top-20 block, sum the bar_pnl over ITS OWN "still overnight" hold bars
    tail_rows = []
    for _, r in top20_overnight.iterrows():
        bid = r["block_id"]
        bars = hold[(hold.block_id == bid) & (hold.session_phase.isin(OVERNIGHT_PHASES))]
        tail_rows.append({"block_id": bid, "net_pnl": r["net_pnl"],
                           "n_still_overnight_hold_bars": len(bars),
                           "sum_bar_pnl_during_still_overnight": bars.bar_pnl.sum()})
    tail_df = pd.DataFrame(tail_rows)
    if len(tail_df):
        tail_df.to_csv(os.path.join(OUT, f"righttail_overnight_check_{tag}.csv"), index=False)
        print(tail_df.round(2).to_string(index=False))
        n_negative = int((tail_df["sum_bar_pnl_during_still_overnight"] < 0).sum())
        print(f"\n{n_negative}/{len(tail_df)} of these top-20-overnight-entered winners were THEMSELVES "
              f"net negative during their own 'still overnight' phase "
              f"(population-level still-overnight fwd_5 mean = {still_on.fwd_5.mean():.2f} for reference)")
    else:
        print("(no top-20 winners were entered overnight for this leg)")

    return hz, chrono_df, tail_df if len(tail_rows) else None


hz_B, chrono_B, tail_B = run_leg("B")
hz_A, chrono_A, tail_A = run_leg("A")

print("\n04_hazard_righttail_chronology.py complete.")
