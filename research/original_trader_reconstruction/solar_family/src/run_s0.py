"""OTR_S0_TYPE1_REPRO: reproduce the canonical Type-1 baseline in pure Python.

ARM_LEDGER: vendor-truth signals from the canonical ledger drive the loop.
ARM_PYTHON: recompute signals with src/analytics/solarwave.py, assert series equality.
"""
import json
import os
import sys

import numpy as np

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from otr_engine import load_ledger, run_wrapper, WrapperPolicy  # noqa: E402

LEDGER = os.path.join(ROOT, "research", "03_reverse_engineering", "ledgers", "t2_canonical_1m.csv")
OUT = os.path.join(ROOT, "runs", "OTR_S0_TYPE1_REPRO", "out")
os.makedirs(OUT, exist_ok=True)

TARGET = {"net": 146440.60, "trades": 2915, "max_dd": -22066.60, "pf": 1.132213}

print("[S0] loading canonical ledger ...", flush=True)
bars = load_ledger(LEDGER)
print(f"[S0] bars: {bars['n']}, sessions: {int(bars['first_bar'].sum())}", flush=True)

# ---- ARM_PYTHON series equality (signal engine already proven; cheap re-verify) ----
from solarwave import SolarWaveParams, solar_wave_full  # noqa: E402
res = solar_wave_full(bars["open"], bars["high"], bars["low"], bars["close"],
                      SolarWaveParams(), start_up=False)
sig_eq = int(np.sum(res.signal_trade != bars["signal_trade"]))
wave_eq = int(np.sum(res.signal_wave != bars["signal_wave"]))
print(f"[S0] ARM_PYTHON series equality: signal_trade mismatches={sig_eq}, signal_wave mismatches={wave_eq}", flush=True)

# ---- ARM_LEDGER trading loop ----
pol = WrapperPolicy(name="V0_EST1")
r = run_wrapper(bars, pol)
fp = r["fingerprint"]
print(json.dumps(fp, indent=1), flush=True)

gates = {
    "G_S0_net": abs(fp["net"] - TARGET["net"]) <= 500,
    "G_S0_trades": abs(fp["trades"] - TARGET["trades"]) <= 5,
    "G_S0_pf": abs(fp["pf"] - TARGET["pf"]) <= 0.005,
    "net_diff": round(fp["net"] - TARGET["net"], 2),
    "trades_diff": fp["trades"] - TARGET["trades"],
}
first = r["trades"][0] if r["trades"] else None
result = {
    "spec": "runs/OTR_S0_TYPE1_REPRO/spec.yaml",
    "arm_python_series_equality": {"signal_trade_mismatch": sig_eq, "signal_wave_mismatch": wave_eq},
    "arm_ledger_fingerprint": fp,
    "gates": gates,
    "first_trade": first,
    "target": TARGET,
}
with open(os.path.join(OUT, "results.json"), "w") as f:
    json.dump(result, f, indent=1)

import csv
with open(os.path.join(OUT, "trades_arm_ledger.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(r["trades"][0].keys()))
    w.writeheader()
    w.writerows(r["trades"])

print("[S0] gates:", {k: v for k, v in gates.items()}, flush=True)
