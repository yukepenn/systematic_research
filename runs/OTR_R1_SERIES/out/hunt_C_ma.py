"""Family C pass 3: dead-zone directional gates  take iff d*(close - REF) > theta.

REF candidates: SMA/EMA(N), session VWAP, session open, N-bar-ago close (momentum),
solar anchors/legs. For each REF series, test whether a theta exists that separates
all HARD skips (dist <= theta) from ALL 112 labeled takes (dist > theta).
"""
import os, sys
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, r"research\original_trader_reconstruction\solar_family\src"))
sys.path.insert(0, os.path.join(ROOT, r"src\analytics"))
sys.path.insert(0, os.path.join(ROOT, r"runs\OTR_R1_SERIES\out"))

from otr_engine import load_ledger, run_wrapper, WrapperPolicy
from solarwave import SolarWaveParams
from hunt_C import instrumented_state, jan_slice, base_trades

LEDGER = os.path.join(ROOT, r"research\03_reverse_engineering\ledgers\t2_canonical_1m.csv")
FEAT = os.path.join(ROOT, r"runs\OTR_R1_SERIES\out\r12f_flip_features.csv")

bars = load_ledger(LEDGER)
n = bars["n"]
o, h, l, c, v = bars["open"], bars["high"], bars["low"], bars["close"], bars["volume"]
time = bars["time"]
first_bar = bars["first_bar"]

# --- REF series ---
refs = {}
csum = np.cumsum(c)
for N in (10, 20, 30, 50, 60, 90, 100, 120, 150, 180, 200, 240, 300, 360, 420, 480, 600, 720, 900, 1200):
    sma = np.full(n, np.nan)
    sma[N-1:] = (csum[N-1:] - np.concatenate([[0.0], csum[:-N]])) / N
    refs[f"SMA{N}"] = sma
for N in (20, 50, 100, 200, 300, 500):
    a = 2.0 / (N + 1)
    e = np.empty(n); e[0] = c[0]
    for i in range(1, n):
        e[i] = e[i-1] + a * (c[i] - e[i-1])
    refs[f"EMA{N}"] = e
# session vwap (typical price)
tp = (h + l + c) / 3.0
vw = np.empty(n); pv = 0.0; vv = 0.0
sess_open = np.empty(n); so = c[0]
for i in range(n):
    if first_bar[i]:
        pv = 0.0; vv = 0.0; so = o[i]
    pv += tp[i] * v[i]; vv += v[i]
    vw[i] = pv / vv if vv > 0 else c[i]
    sess_open[i] = so
refs["VWAP"] = vw
refs["SESSOPEN"] = sess_open
for N in (15, 30, 60, 90, 120, 180, 240, 360, 480, 720):
    r = np.full(n, np.nan); r[N:] = c[:-N]
    refs[f"CLOSE_LAG{N}"] = r

# solar leg refs
S = instrumented_state(o, h, l, c, SolarWaveParams())
refs["ANCHOR_PREV"] = np.concatenate([[np.nan], S["anchor"][:-1]])
# midline of TS and TV of the OLD trend at j-1: anchor -/+ (S+V)/2
sgn = np.where(S["is_up"], 1.0, -1.0)
mid = S["anchor"] - sgn * (44.75 + 22.5) / 2
refs["OLDMID_PREV"] = np.concatenate([[np.nan], mid[:-1]])

# --- labels on base trades ---
sl = jan_slice(bars)
trades = base_trades(sl)
lab = pd.read_csv(FEAT)[["entry_time", "label", "certainty"]]
lmap = dict(zip(lab.entry_time, zip(lab.label, lab.certainty)))

J = []   # (signal bar index, d, label, certainty, entry_time)
for t in trades:
    j = t["entry_i"] - 1
    lb, ct = lmap[t["entry_time"]]
    J.append((j, 1 if t["dir"] > 0 else -1, lb, ct, t["entry_time"]))

hard_skip = [(j, d, et) for j, d, lb, ct, et in J if lb == "SKIP" and ct == "HARD"]
soft_skip = [(j, d, et) for j, d, lb, ct, et in J if lb == "SKIP" and ct == "SOFT"]
takes = [(j, d, et) for j, d, lb, ct, et in J if lb == "TAKE"]
print(f"takes={len(takes)} hard_skips={len(hard_skip)} soft_skips={len(soft_skip)}")

rows = []
for name, R in refs.items():
    def dist(items):
        return np.array([dd * (c[j] - R[j]) for j, dd, _ in items])
    ds_h = dist(hard_skip); ds_s = dist(soft_skip); dt = dist(takes)
    if np.isnan(ds_h).any() or np.isnan(dt).any():
        continue
    max_skip = ds_h.max(); min_take = dt.min()
    sep = max_skip < min_take
    # how many soft skips fall below a theta between the bounds
    theta = (max_skip + min_take) / 2 if sep else max_skip
    soft_ok = int((ds_s <= theta).sum())
    rows.append((sep, min_take - max_skip, name, max_skip, min_take, soft_ok, len(ds_s)))
rows.sort(key=lambda r: -r[1])
print(f"\n{'sep':>4} {'gap':>9} {'ref':>14} {'maxSkip':>9} {'minTake':>9} soft_covered")
for sep, gap, name, ms, mt, sok, stot in rows:
    print(f"{str(sep):>4} {gap:9.2f} {name:>14} {ms:9.2f} {mt:9.2f}   {sok}/{stot}")
