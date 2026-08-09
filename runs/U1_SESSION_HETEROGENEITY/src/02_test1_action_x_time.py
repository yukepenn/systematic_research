"""U1 test 1 -- TIME x ENTRY vs TIME x HOLD vs TIME x REVERSAL (Product B), by session_phase and
RTH/ETH. Canonical window only (is_health_only_bar==False); test5 handles chronology/extension."""
import os, json
import numpy as np, pandas as pd

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
PHASE_ORDER = ["ETH_ASIA", "ETH_EUROPE", "US_PREMARKET", "RTH_OPEN", "RTH_MID", "RTH_CLOSE", "POST_RTH"]

entry_B = pd.read_csv(os.path.join(OUT, "block_entry_B.csv"))
hold_B = pd.read_csv(os.path.join(OUT, "hold_fwd_B.csv"))

entry_B_c = entry_B[~entry_B["is_health_only_bar"]]
hold_B_c = hold_B[~hold_B["is_health_only_bar"]]

print("=" * 100)
print("TEST 1a -- Product B ENTRY: net_pnl by session_phase (canonical window)")
print("=" * 100)
g1 = entry_B_c[entry_B_c["action_B"] == "ENTRY"].groupby("session_phase", observed=True).agg(
    n=("net_pnl", "size"), mean_pnl=("net_pnl", "mean"), sum_pnl=("net_pnl", "sum"),
    win_rate=("net_pnl", lambda x: float((x > 0).mean()))).reindex(PHASE_ORDER)
print(g1.round(2).to_string())
g1.to_csv(os.path.join(OUT, "t1a_entry_B_by_phase.csv"))

print("\nENTRY: net_pnl by RTH vs ETH (canonical)")
g1b = entry_B_c[entry_B_c["action_B"] == "ENTRY"].groupby("is_rth").agg(
    n=("net_pnl", "size"), mean_pnl=("net_pnl", "mean"), sum_pnl=("net_pnl", "sum"),
    win_rate=("net_pnl", lambda x: float((x > 0).mean())))
print(g1b.round(2).to_string())
g1b.to_csv(os.path.join(OUT, "t1a_entry_B_by_rth.csv"))

print("\n" + "=" * 100)
print("TEST 1b -- Product B REVERSAL: net_pnl by session_phase (n=92 total, descriptive only)")
print("=" * 100)
g2 = entry_B_c[entry_B_c["action_B"] == "REVERSAL"].groupby("session_phase", observed=True).agg(
    n=("net_pnl", "size"), mean_pnl=("net_pnl", "mean"), sum_pnl=("net_pnl", "sum")).reindex(PHASE_ORDER)
print(g2.round(2).to_string())
g2.to_csv(os.path.join(OUT, "t1b_reversal_B_by_phase.csv"))
g2b = entry_B_c[entry_B_c["action_B"] == "REVERSAL"].groupby("is_rth").agg(
    n=("net_pnl", "size"), mean_pnl=("net_pnl", "mean"), sum_pnl=("net_pnl", "sum"))
print("\nREVERSAL by RTH vs ETH:")
print(g2b.round(2).to_string())

print("\n" + "=" * 100)
print("TEST 1c -- Product B HOLD: forward-1-bar / forward-5-bar continuation value by session_phase")
print("(canonical window; this is a lightweight preview of U3, one clean table)")
print("=" * 100)
g3 = hold_B_c.groupby("session_phase", observed=True).agg(
    n=("forward1_pnl", "size"),
    mean_fwd1=("forward1_pnl", "mean"), sum_fwd1=("forward1_pnl", "sum"),
    mean_fwd5=("forward5_pnl", "mean"), sum_fwd5=("forward5_pnl", "sum")).reindex(PHASE_ORDER)
print(g3.round(3).to_string())
g3.to_csv(os.path.join(OUT, "t1c_hold_fwd_B_by_phase.csv"))

print("\nHOLD continuation value by RTH vs ETH:")
g3b = hold_B_c.groupby("is_rth").agg(
    n=("forward1_pnl", "size"),
    mean_fwd1=("forward1_pnl", "mean"), sum_fwd1=("forward1_pnl", "sum"),
    mean_fwd5=("forward5_pnl", "mean"), sum_fwd5=("forward5_pnl", "sum"))
print(g3b.round(3).to_string())
g3b.to_csv(os.path.join(OUT, "t1c_hold_fwd_B_by_rth.csv"))

# quick two-sample separation check (mean fwd5 RTH vs ETH, per-bar and annualized-style multiple)
rth_fwd5 = hold_B_c.loc[hold_B_c["is_rth"], "forward5_pnl"].dropna()
eth_fwd5 = hold_B_c.loc[~hold_B_c["is_rth"], "forward5_pnl"].dropna()
summary = {
    "entry_B_rth_mean": float(entry_B_c.loc[(entry_B_c["action_B"] == "ENTRY") & entry_B_c["is_rth"], "net_pnl"].mean()),
    "entry_B_eth_mean": float(entry_B_c.loc[(entry_B_c["action_B"] == "ENTRY") & ~entry_B_c["is_rth"], "net_pnl"].mean()),
    "entry_B_rth_n": int((( entry_B_c["action_B"] == "ENTRY") & entry_B_c["is_rth"]).sum()),
    "entry_B_eth_n": int(((entry_B_c["action_B"] == "ENTRY") & ~entry_B_c["is_rth"]).sum()),
    "hold_fwd5_rth_mean": float(rth_fwd5.mean()), "hold_fwd5_rth_n": int(len(rth_fwd5)),
    "hold_fwd5_eth_mean": float(eth_fwd5.mean()), "hold_fwd5_eth_n": int(len(eth_fwd5)),
}
json.dump(summary, open(os.path.join(OUT, "t1_summary.json"), "w"), indent=2)
print("\n" + json.dumps(summary, indent=2))
print("\nnote: SCALE-IN/DOWN is a Product-A-only action type (Product B is single-lot {-1,0,+1});")
print("covered in test6 (07_test6_product_a.py), not forced into this Product-B table.")
print("\ntest1 complete.")
