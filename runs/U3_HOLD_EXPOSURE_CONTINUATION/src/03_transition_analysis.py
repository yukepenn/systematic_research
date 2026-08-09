"""U3 step 3 -- session-transition continuation value (parent task point 2). Compares
forward continuation value for HOLD bars whose CURRENT session_phase differs from the entry
bar's session_phase ("transition") vs bars still within the entry phase ("non-transition"),
plus two concrete named transitions (overnight->RTH, RTH->POST_RTH). Canonical window only.
Also reports mean REMAINING bars per session_phase bucket, since fwd_session mixes "quality of
continuation" with "how much session time is structurally left" -- disclosed explicitly, not
silently blended.
"""
import os
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(ROOT, "runs", "U3_HOLD_EXPOSURE_CONTINUATION", "out")

RTH_PHASES = {"RTH_OPEN", "RTH_MID", "RTH_CLOSE"}
OVERNIGHT_PHASES = {"ETH_ASIA", "ETH_EUROPE"}


def tstat(x):
    x = x.dropna()
    n = len(x)
    if n < 2:
        return np.nan
    s = x.std(ddof=1)
    return float(x.mean() / (s / np.sqrt(n))) if s > 0 else np.nan


def summarize(g, label, horizons=("fwd_1", "fwd_5", "fwd_10", "fwd_20", "fwd_session")):
    rows = []
    for h in horizons:
        y = g[h]
        rows.append({"label": label, "horizon": h, "n": int(y.notna().sum()),
                     "mean": float(y.mean()), "median": float(y.median()), "tstat": tstat(y)})
    return rows


def run_leg(tag):
    print(f"\n=== {tag}: session-transition continuation value ===", flush=True)
    hold = pd.read_parquet(os.path.join(OUT, f"hold_{tag}.parquet"))
    block = pd.read_csv(os.path.join(OUT, f"block_table_{tag}.csv"))
    hold = hold.merge(block[["block_id", "entry_session_phase"]], on="block_id", how="left")
    canon = hold[~hold.is_health_only_bar].copy()
    canon["transition"] = canon["session_phase"] != canon["entry_session_phase"]

    # remaining-bars-in-session context (for the fwd_session confound disclosure): fwd_session
    # mixes "quality of continuation" with "how much session time is structurally left" -- report
    # mean bars_left_in_session per phase so the reader can see the confound directly.
    bars_left = canon.groupby("session_phase")["bars_left_in_session"].mean()
    print("mean bars remaining in session, by CURRENT session_phase (confound disclosure for "
          "fwd_session comparisons -- NOT itself a continuation-value finding):")
    print(bars_left.round(1).to_string())

    rows = []
    rows += summarize(canon[~canon.transition], "NON_TRANSITION (all)")
    rows += summarize(canon[canon.transition], "TRANSITION (all)")

    # concrete case 1: overnight-entered blocks, still-overnight vs now-in-RTH
    overnight_blocks = canon[canon.entry_session_phase.isin(OVERNIGHT_PHASES)]
    still_on = overnight_blocks[overnight_blocks.session_phase.isin(OVERNIGHT_PHASES)]
    now_rth = overnight_blocks[overnight_blocks.session_phase.isin(RTH_PHASES)]
    rows += summarize(still_on, "OVERNIGHT_ENTRY: still overnight (non-transition)")
    rows += summarize(now_rth, "OVERNIGHT_ENTRY: now in RTH (transitioned)")

    # concrete case 2: RTH-entered blocks, still-in-RTH vs now-POST_RTH
    rth_blocks = canon[canon.entry_session_phase.isin(RTH_PHASES)]
    still_rth = rth_blocks[rth_blocks.session_phase.isin(RTH_PHASES)]
    now_post = rth_blocks[rth_blocks.session_phase == "POST_RTH"]
    rows += summarize(still_rth, "RTH_ENTRY: still in RTH (non-transition)")
    rows += summarize(now_post, "RTH_ENTRY: now POST_RTH (transitioned)")

    out_df = pd.DataFrame(rows)
    out_df.to_csv(os.path.join(OUT, f"transition_analysis_{tag}.csv"), index=False)
    print(out_df.pivot(index="label", columns="horizon", values="mean")
          [["fwd_1", "fwd_5", "fwd_10", "fwd_20", "fwd_session"]].round(2).to_string())
    print("\nn per row:")
    print(out_df.pivot(index="label", columns="horizon", values="n")[["fwd_1"]].to_string())
    return out_df


tr_B = run_leg("B")
tr_A = run_leg("A")

print("\n03_transition_analysis.py complete.")
