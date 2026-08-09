"""R2 -- formalizes (as a committed, reproducible script) the tail-dollar-attribution and 2-tick
cost-stress checks for the CONFIRM2 candidate, run ad hoc during construction and independently
re-verified by an adversarial review agent this same wave. Written after seeing the construction
result -- disclosed process deviation from spec.yaml's own "child spec before testing a parameter"
discipline; the underlying numbers were independently reproduced from scratch by a fresh
adversarial agent that did not write construct.py, so they are trustworthy, but this script did
not exist as a preregistered artifact before the candidate ran. Treat R2 as first-pass evidence
requiring early NT8 validation, not a final promotion, per directive sec28-29."""
import os, sys, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "runs", "R1_ADAPTIVE_EXIT", "src"))
import construct as R1
import sm01_solarsim as sm

OUT = os.path.join(ROOT, "runs", "R2_ENTRY_TIMING", "out")
P0OUT = os.path.join(ROOT, "runs", "P0_TRADESTATE_AUTOPSY", "out")

pos_ctrl = np.load(os.path.join(ROOT, "runs", "R1_ADAPTIVE_EXIT", "out", "pos_control.npy"))
pos_c2 = np.load(os.path.join(OUT, "pos_CONFIRM2.npy"))
_, _, bpnl_ctrl = R1.onelot_exec(pos_ctrl, R1.COMM_NQ, R1.PV_NQ, R1.open_, R1.high, R1.low, R1.close)
_, _, bpnl_c2 = R1.onelot_exec(pos_c2, R1.COMM_NQ, R1.PV_NQ, R1.open_, R1.high, R1.low, R1.close)
np.save(os.path.join(OUT, "barpnl_CONTROL_NQ.npy"), bpnl_ctrl)
np.save(os.path.join(OUT, "barpnl_CONFIRM2_NQ.npy"), bpnl_c2)

# ---------------------------------------------------------------- tail dollar attribution
ledger = pd.read_parquet(os.path.join(P0OUT, "ledger_full.parquet"), columns=["t_idx", "block_id", "position"])
tb = pd.read_csv(os.path.join(P0OUT, "block_level_summary.csv"))
pos_blocks = ledger[ledger["position"] != 0]
span = pos_blocks.groupby("block_id")["t_idx"].agg(["min", "max"])
tb = tb.merge(span, on="block_id")
n = len(tb)
tb_sorted = tb.sort_values("net_pnl")


def bucket(frac, top):
    k = max(1, int(round(n * frac)))
    return tb_sorted.iloc[-k:] if top else tb_sorted.iloc[:k]


results = {}
for label, frac, top in [("top1pct", 0.01, True), ("top5pct", 0.05, True), ("top10pct", 0.10, True),
                          ("bottom1pct", 0.01, False), ("bottom5pct", 0.05, False), ("bottom10pct", 0.10, False)]:
    b = bucket(frac, top)
    ctrl_sum = float(b["net_pnl"].sum())
    # +2 bar buffer: candidate's confirmed entry into the same episode can start up to
    # confirm_bars=2 bars later than control's; span end is extended by the same margin so a
    # delayed-but-still-captured trade isn't clipped by the window itself.
    cand_sum = float(sum(bpnl_c2[row["min"]:row["max"] + 2].sum() for _, row in b.iterrows()))
    results[label] = {"n": len(b), "ctrl_sum": ctrl_sum, "cand_sum_over_same_spans": cand_sum,
                       "delta": cand_sum - ctrl_sum,
                       "retention_or_improvement": cand_sum / ctrl_sum if top else cand_sum - ctrl_sum}
    print(f"{label}: n={len(b)} ctrl={ctrl_sum:.2f} cand={cand_sum:.2f} delta={cand_sum-ctrl_sum:.2f}")

net_tail_effect = (results["top10pct"]["delta"]) + (results["bottom10pct"]["delta"])
print(f"\nnet top10+bottom10 tail dollar effect: {net_tail_effect:.2f} (positive = net beneficial)")
results["net_top10_plus_bottom10_tail_effect"] = net_tail_effect

# ---------------------------------------------------------------- 2-tick cost stress
TICK = sm.TICK
def _fill_2tick(open_, high, low, side, at_close=None):
    base = at_close if at_close is not None else open_
    px = base + side * TICK * 2
    return min(px, high) if side > 0 else max(px, low)


orig_fill = sm._fill
sm._fill = _fill_2tick
R1._fill = _fill_2tick
daily_ctrl_2t, _, _ = R1.onelot_exec(pos_ctrl, R1.COMM_NQ, R1.PV_NQ, R1.open_, R1.high, R1.low, R1.close)
daily_c2_2t, _, _ = R1.onelot_exec(pos_c2, R1.COMM_NQ, R1.PV_NQ, R1.open_, R1.high, R1.low, R1.close)
row_ctrl_2t = R1.battery_row("CTRL_2TICK", daily_ctrl_2t)
row_c2_2t = R1.battery_row("CONFIRM2_2TICK", daily_c2_2t)
sm._fill = orig_fill; R1._fill = orig_fill

cost_stress = {
    "control_2tick": {"net": row_ctrl_2t["net"], "sharpe": row_ctrl_2t["sharpe"]},
    "confirm2_2tick": {"net": row_c2_2t["net"], "sharpe": row_c2_2t["sharpe"]},
    "survives_2tick_stress": bool(row_c2_2t["sharpe"] > row_ctrl_2t["sharpe"] and row_c2_2t["net"] > row_ctrl_2t["net"]),
}
print(f"\n2-tick stress: control net={row_ctrl_2t['net']:.2f} sharpe={row_ctrl_2t['sharpe']:.3f} | "
      f"confirm2 net={row_c2_2t['net']:.2f} sharpe={row_c2_2t['sharpe']:.3f} | "
      f"survives={cost_stress['survives_2tick_stress']}")

json.dump({"tail_attribution": results, "cost_stress": cost_stress},
          open(os.path.join(OUT, "tail_and_cost_stress_results.json"), "w"), indent=2)
print("\nsaved tail_and_cost_stress_results.json")
