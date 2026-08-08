"""SMV2AH sub_426 -- MANDATORY intraday MTM construction + reconciliation gate,
then threshold calibration (DIAGNOSTIC, precedes any circuit-breaker sim).

Step 1 (mandatory, must pass before anything else runs): build the bar-by-bar
cumulative intraday MTM series for object A (SOLAR_DUAL_HTF) and object B
(DAYONLY_DUAL6040), reset to zero at every session open, and verify the
session-end value equals the EXISTING end-of-day daily P&L to the cent, for
EVERY session in dev.

Step 2: empirical distribution of each object's worst intraday running
drawdown per session (min of the intraday cumulative MTM series within each
session); report 1st/2nd/5th/10th percentile per object -- these four
percentile levels ARE (pre-registered) the four sub_427 threshold cells.
"""
import os
import sys
import json

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from common_ah import OUT, load_dev_bars, build_objects, BM_RT_COST

print("loading dev bars ...", flush=True)
bars = load_dev_bars()
n_sessions = bars["sess_id"].nunique()
print(f"n_bars={len(bars)} n_sessions={n_sessions} "
      f"dev range {bars['sess_date'].min()}..{bars['sess_date'].max()}", flush=True)

print("building objects (Solar member ensemble + E10 + DUAL_HTF + B-MOM bar exec) ...", flush=True)
obj = build_objects(bars)

# ---- sanity: rebuilt B-MOM daily (bar executor) vs frozen ledger daily, to the cent ----
bm_diff = (obj["BM_rebuilt_daily"] - obj["BM_ledger_daily"]).abs()
bm_max_diff = float(bm_diff.max())
print(f"B-MOM leg bar-executor vs frozen E2 ledger daily net: max abs diff over "
      f"{len(bm_diff)} sessions = ${bm_max_diff:.6f}", flush=True)

# ---- build per-bar session id / cumulative intraday MTM ----
sess_id = bars["sess_id"].to_numpy()
sess_date = bars["sess_date"].to_numpy()
is_last = bars["is_last_of_sess"].to_numpy()

DUAL_bar = obj["DUAL_bar_pnl"]
BM_bar = obj["BM_bar_pnl"]
c_BM, c_combo = obj["c_BM"], obj["c_combo"]

# object A: intraday cumulative MTM = per-session cumsum of DUAL_bar_pnl
sA = pd.Series(DUAL_bar).groupby(sess_id).cumsum().to_numpy()

# object B: bar-level portfolio pnl = c_combo * (0.6*DUAL_bar + 0.4*c_BM*BM_bar)
port_bar = c_combo * (0.6 * DUAL_bar + 0.4 * c_BM * BM_bar)
sB = pd.Series(port_bar).groupby(sess_id).cumsum().to_numpy()

intraday = pd.DataFrame({
    "sess_id": sess_id, "sess_date": sess_date, "time": bars["time"].to_numpy(),
    "is_last_of_sess": is_last,
    "intraday_mtm_A": sA, "intraday_mtm_B": sB,
    "bar_pnl_A": DUAL_bar, "bar_pnl_B": port_bar,
})

# ---- MANDATORY reconciliation: session-end value == existing daily curve, to the cent ----
end_rows = intraday[intraday["is_last_of_sess"]].copy()
end_rows = end_rows.set_index(pd.to_datetime(end_rows["sess_date"]))

dailyA = obj["DUAL_daily"]  # existing e10_exec daily net, indexed by session ts
dailyB = obj["portfolio_daily"]

chk = pd.DataFrame({
    "sess": end_rows.index,
    "intraday_end_A": end_rows["intraday_mtm_A"].to_numpy(),
    "existing_daily_A": dailyA.reindex(end_rows.index).to_numpy(),
})
chk["abs_diff_A"] = (chk["intraday_end_A"] - chk["existing_daily_A"]).abs()

chkB = pd.DataFrame({
    "sess": end_rows.index,
    "intraday_end_B": end_rows["intraday_mtm_B"].to_numpy(),
    "existing_daily_B": dailyB.reindex(end_rows.index).to_numpy(),
})
chkB["abs_diff_B"] = (chkB["intraday_end_B"] - chkB["existing_daily_B"]).abs()

recon = chk.merge(chkB, on="sess")
recon.to_csv(os.path.join(OUT, "intraday_mtm_construction_check.csv"), index=False)

max_diff_A = float(recon["abs_diff_A"].max())
max_diff_B = float(recon["abs_diff_B"].max())
n_sess_checked = len(recon)
TOL = 0.005  # half a cent

print(f"RECONCILIATION: object A (SOLAR_DUAL_HTF) max abs deviation over "
      f"{n_sess_checked} sessions = ${max_diff_A:.6f}", flush=True)
print(f"RECONCILIATION: object B (DAYONLY_DUAL6040) max abs deviation over "
      f"{n_sess_checked} sessions = ${max_diff_B:.6f}", flush=True)

pass_A = max_diff_A < TOL
pass_B = max_diff_B < TOL
pass_bm_sanity = bm_max_diff < TOL
gate_pass = bool(pass_A and pass_B and pass_bm_sanity)

if not gate_pass:
    print("!!!!! RECONCILIATION GATE FAILED -- construction is wrong, must fix before "
          "proceeding. Halting. !!!!!", flush=True)
    json.dump({
        "gate": "sub426_reconciliation", "pass": False,
        "max_diff_A": max_diff_A, "max_diff_B": max_diff_B,
        "bm_leg_sanity_max_diff": bm_max_diff,
    }, open(os.path.join(OUT, "sub426_reconcile_verdict.json"), "w"), indent=2)
    sys.exit(1)

print("RECONCILIATION GATE PASSED (< $0.005 on every session, both objects).", flush=True)
json.dump({
    "gate": "sub426_reconciliation", "pass": True,
    "n_sessions": n_sess_checked,
    "max_diff_A_dollars": max_diff_A, "max_diff_B_dollars": max_diff_B,
    "bm_leg_bar_executor_vs_ledger_max_diff_dollars": bm_max_diff,
}, open(os.path.join(OUT, "sub426_reconcile_verdict.json"), "w"), indent=2)

# save the intraday MTM series (needed by sub_427/sub_429) -- large, parquet
intraday.to_parquet(os.path.join(OUT, "intraday_mtm_series.parquet"))
print(f"saved intraday_mtm_series.parquet ({len(intraday)} bars)", flush=True)

# ---------------------------------------------------------------------------------
# sub_426: threshold calibration -- worst intraday running drawdown PER SESSION
# (min of the intraday cumulative MTM series within each session, NOT the
# session's final P&L)
# ---------------------------------------------------------------------------------
worst = intraday.groupby("sess_id").agg(
    sess_date=("sess_date", "first"),
    worst_intraday_A=("intraday_mtm_A", "min"),
    worst_intraday_B=("intraday_mtm_B", "min"),
    final_A=("intraday_mtm_A", "last"),
    final_B=("intraday_mtm_B", "last"),
).reset_index()
worst.to_csv(os.path.join(OUT, "worst_intraday_drawdown_per_session.csv"), index=False)

PCTS = [1, 2, 5, 10]
rows = []
for obj_name, col in (("A_SOLAR_DUAL_HTF", "worst_intraday_A"), ("B_DAYONLY_DUAL6040", "worst_intraday_B")):
    x = worst[col].to_numpy()
    for p in PCTS:
        thr = float(np.percentile(x, p))
        rows.append({"object": obj_name, "percentile": p, "threshold_dollars": thr})
    print(f"{obj_name}: n_sessions={len(x)} worst-intraday-DD percentiles "
          + " ".join(f"p{p}=${np.percentile(x, p):.0f}" for p in PCTS), flush=True)

calib = pd.DataFrame(rows)
calib.to_csv(os.path.join(OUT, "threshold_calibration.csv"), index=False)
print(calib.to_string(index=False), flush=True)
print("done sub_426", flush=True)
