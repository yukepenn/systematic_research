"""R2V1 priority-zero: exact entry-attempt mapping to resolve the n_cancelled=0 anomaly in
construct.py's real simulated trajectory. For EVERY incumbent new-commitment-from-flat event
(1,978 total), runs a FRESH-RESTART simulation of the confirm=2 state machine starting unarmed
at that bar, using ONLY the market-conditional M/entry_blocked_c4/forced_flat_c4 arrays (not the
candidate's own real, path-dependent simulated position) -- this is well-defined regardless of
where the real candidate simulation actually is at that moment, and is the same convention
diagnose.py's M_entry/M_p1/M_p2 columns already used, extended to a full forward resolution
instead of just a 2-bar lookahead.

Taxonomy (precise, since the owner's own A-F list is not fully mutually exclusive as literally
written -- "cancelled" (C) and "never entered before session reset" (E) overlap without a
tie-break rule; this is the disclosed, exact operationalization used here):
    A_SAME_DIRECT    : entered same side as incumbent, exactly 2 bars later, no cancel en route
    B_SAME_REARMED   : entered same side as incumbent, but only after >=1 cancel/re-arm cycle
    D_OPPOSITE       : an entry on the OPPOSITE side confirmed before the same side ever did
    C_CANCELLED_NO_REENTRY : armed at least once and cancelled (reverted to neutral or flipped
                              direction) at least once, but NO entry of any side confirmed
                              before the next forced-flat/entry-blocked session reset
    E_RESET_NO_CANCEL : hit the session reset while still counting up toward confirmation,
                         WITHOUT ever having reverted/cancelled first
    F_OTHER          : anything else (data exhausted without resolving -- not expected to occur)
"""
import os, sys, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "runs", "R1_ADAPTIVE_EXIT", "src"))
import construct as R1

OUT = os.path.join(ROOT, "runs", "R2_ENTRY_TIMING", "out")
n = R1.n; M = R1.M; entry_blocked_c4 = R1.entry_blocked_c4; forced_flat_c4 = R1.forced_flat_c4
ENTRY_LEVEL = R1.ENTRY_LEVEL

P0OUT = os.path.join(ROOT, "runs", "P0_TRADESTATE_AUTOPSY", "out")
ledger = pd.read_parquet(os.path.join(P0OUT, "ledger_full.parquet"),
                          columns=["t_idx", "position", "block_id"])
pos_blocks = ledger[ledger["position"] != 0]
entries = pos_blocks.groupby("block_id").agg(t0=("t_idx", "min"), side=("position", "first")).reset_index()
blocks_summary = pd.read_csv(os.path.join(P0OUT, "block_level_summary.csv"))
entries = entries.merge(blocks_summary[["block_id", "net_pnl", "n_bars"]], on="block_id")

MAX_HORIZON = 3000


def fresh_restart_outcome(t0, incumbent_side):
    armed_side = 0
    armed_bars = 0
    ever_cancelled = False
    t = t0
    steps = 0
    while steps < MAX_HORIZON and t < n:
        if forced_flat_c4[t] or entry_blocked_c4[t]:
            cat = "C_CANCELLED_NO_REENTRY" if ever_cancelled else "E_RESET_NO_CANCEL"
            return {"category": cat, "entry_bar": None, "entry_side": None,
                    "delay_bars": None, "ever_cancelled": ever_cancelled}
        raw = 1 if M[t] >= ENTRY_LEVEL else (-1 if M[t] <= -ENTRY_LEVEL else 0)
        if raw == 0:
            if armed_side != 0:
                ever_cancelled = True
            armed_side = 0
            armed_bars = 0
        elif armed_side == raw:
            armed_bars += 1
            if armed_bars >= 2:
                delay = t - t0
                if raw == incumbent_side and not ever_cancelled and delay == 2:
                    cat = "A_SAME_DIRECT"
                elif raw == incumbent_side:
                    cat = "B_SAME_REARMED"
                else:
                    cat = "D_OPPOSITE"
                return {"category": cat, "entry_bar": t, "entry_side": raw,
                        "delay_bars": delay, "ever_cancelled": ever_cancelled}
        else:
            if armed_side != 0:
                ever_cancelled = True
            armed_side = raw
            armed_bars = 0
        t += 1
        steps += 1
    return {"category": "F_OTHER", "entry_bar": None, "entry_side": None,
            "delay_bars": None, "ever_cancelled": ever_cancelled}


rows = []
for _, r in entries.iterrows():
    t0 = int(r["t0"]); side = int(r["side"])
    outcome = fresh_restart_outcome(t0, side)
    rows.append({
        "block_id": r["block_id"], "incumbent_entry_t0": t0, "incumbent_side": side,
        "incumbent_net_pnl": r["net_pnl"], "incumbent_M_at_entry": float(M[t0]),
        **outcome,
    })
mapping = pd.DataFrame(rows)
mapping.to_csv(os.path.join(OUT, "r2v1_entry_attempt_mapping.csv"), index=False)

print("=== category counts ===")
print(mapping["category"].value_counts())
print("\n=== category counts, dollars (incumbent's own net_pnl for that trade) ===")
print(mapping.groupby("category")["incumbent_net_pnl"].agg(["count", "sum", "mean"]))

# reconcile against the REAL simulated candidate trajectory's own confirmed/cancelled counts
pos_c2 = np.load(os.path.join(OUT, "pos_CONFIRM2.npy"))
real_change = np.r_[True, pos_c2[1:] != pos_c2[:-1]]
real_entries = np.where(real_change & (pos_c2 != 0))[0]
print(f"\nreal simulated candidate trajectory: {len(real_entries)} actual position-block starts "
      f"(vs {len(mapping)} incumbent entry events used for the counterfactual mapping above)")

n_would_enter = (mapping["category"].isin(["A_SAME_DIRECT", "B_SAME_REARMED", "D_OPPOSITE"])).sum()
n_would_cancel_and_stall = (mapping["category"] == "C_CANCELLED_NO_REENTRY").sum()
n_ever_cancelled = mapping["ever_cancelled"].sum()
print(f"\nCounterfactual (fresh-restart) summary: {n_would_enter}/{len(mapping)} would eventually "
      f"enter (any side) before a session reset; {n_would_cancel_and_stall} cancel-and-never-"
      f"reenter-this-session; {n_ever_cancelled} experienced >=1 cancel/re-arm event somewhere "
      f"in their path (this is the TRUE cancellation rate the diagnostic's 77-count and the "
      f"real n_cancelled=0 counter should both be checked against).")

diagnostics = {
    "n_incumbent_entries": int(len(mapping)),
    "category_counts": mapping["category"].value_counts().to_dict(),
    "n_ever_cancelled_anywhere_in_path": int(n_ever_cancelled),
    "n_real_candidate_position_blocks": int(len(real_entries)),
    "pct_A_same_direct": float((mapping["category"] == "A_SAME_DIRECT").mean() * 100),
    "pct_B_same_rearmed": float((mapping["category"] == "B_SAME_REARMED").mean() * 100),
    "pct_D_opposite": float((mapping["category"] == "D_OPPOSITE").mean() * 100),
    "pct_C_cancelled_no_reentry": float((mapping["category"] == "C_CANCELLED_NO_REENTRY").mean() * 100),
    "pct_E_reset_no_cancel": float((mapping["category"] == "E_RESET_NO_CANCEL").mean() * 100),
    "pct_F_other": float((mapping["category"] == "F_OTHER").mean() * 100),
}
json.dump(diagnostics, open(os.path.join(OUT, "r2v1_entry_mapping_summary.json"), "w"), indent=2)
print("\n" + json.dumps(diagnostics, indent=2))
