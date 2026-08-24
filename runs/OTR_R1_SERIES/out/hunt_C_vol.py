"""Family C pass 6: VOLUME-state gates on flip entries.

Candidates: signal-bar volume absolute/relative (vs SMA(N) of volume, vs prior
bar, vs leg averages, session percentile), old-leg volume aggregates.
Separation demand: 8/8 HARD skips, 0/112 takes.
"""
import os, sys
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, r"research\original_trader_reconstruction\solar_family\src"))
sys.path.insert(0, os.path.join(ROOT, r"src\analytics"))
sys.path.insert(0, os.path.join(ROOT, r"runs\OTR_R1_SERIES\out"))

from otr_engine import load_ledger
from solarwave import SolarWaveParams
from hunt_C import instrumented_state, jan_slice, base_trades

LEDGER = os.path.join(ROOT, r"research\03_reverse_engineering\ledgers\t2_canonical_1m.csv")
FEAT = os.path.join(ROOT, r"runs\OTR_R1_SERIES\out\r12f_flip_features.csv")
OUT = os.path.join(ROOT, r"runs\OTR_R1_SERIES\out")

bars = load_ledger(LEDGER)
n = bars["n"]
o, h, l, c, v = bars["open"], bars["high"], bars["low"], bars["close"], bars["volume"]
time = bars["time"]

vsum = np.cumsum(v)
vma = {}
for N in (5, 10, 14, 20, 30, 50, 60, 100, 120, 200, 240, 480):
    m = np.full(n, np.nan)
    m[N-1:] = (vsum[N-1:] - np.concatenate([[0.0], vsum[:-N]])) / N
    vma[N] = m

S = instrumented_state(o, h, l, c, SolarWaveParams())
leg = S["leg"]

sl = jan_slice(bars)
trades = base_trades(sl)
lab = pd.read_csv(FEAT)[["entry_time", "label", "certainty"]]
lmap = dict(zip(lab.entry_time, zip(lab.label, lab.certainty)))

rows = []
for t in trades:
    j = t["entry_i"] - 1
    d = 1 if t["dir"] > 0 else -1
    lb, ct = lmap[t["entry_time"]]
    k = leg[j]
    old = np.flatnonzero(leg == k - 1)
    old_v = v[old] if len(old) else np.array([np.nan])
    row = dict(entry_time=t["entry_time"], d=d, label=lb, certainty=ct,
               v_j=v[j], v_j1=v[j-1], v_j2=v[j-2],
               v_ratio_prev=v[j] / v[j-1] if v[j-1] > 0 else np.nan,
               v_max_j_j1=max(v[j], v[j-1]),
               old_leg_vsum=float(old_v.sum()), old_leg_vmean=float(old_v.mean()),
               v_vs_oldleg=v[j] / old_v.mean() if old_v.mean() > 0 else np.nan)
    for N, m in vma.items():
        row[f"vr{N}"] = v[j] / m[j] if m[j] > 0 else np.nan
        row[f"vr{N}_prev"] = v[j] / m[j-1] if m[j-1] > 0 else np.nan
    rows.append(row)

df = pd.DataFrame(rows)
df.to_csv(os.path.join(OUT, "hunt_C_vol_features.csv"), index=False)

hardskip = (df.label == "SKIP") & (df.certainty == "HARD")
takes = df.label == "TAKE"
sub = df[hardskip | takes]
ys = hardskip[hardskip | takes].to_numpy()

print("1-D separation test per volume feature (skip low  /  skip high):")
print(f"{'feature':>16} {'maxSkip':>10} {'minTake':>10} {'sepLOW':>7} | {'minSkip':>10} {'maxTake':>10} {'sepHIGH':>7}")
for cname in df.columns:
    if cname in ("entry_time", "label", "certainty", "d"):
        continue
    arr = sub[cname].astype(float).to_numpy()
    s = arr[ys]; tk = arr[~ys]
    if np.isnan(s).any() or np.isnan(tk).any():
        continue
    seplow = s.max() < tk.min()      # skip iff feature <= theta
    sephigh = s.min() > tk.max()     # skip iff feature >= theta
    line = (f"{cname:>16} {s.max():10.3f} {tk.min():10.3f} {str(seplow):>7} | "
            f"{s.min():10.3f} {tk.max():10.3f} {str(sephigh):>7}")
    if seplow or sephigh:
        line += "   <<< PERFECT"
    print(line)

# print raw rows for skips and nearest takes for the most promising feature
print("\nHARD skips volume detail:")
cols = ["entry_time", "d", "label", "v_j", "v_j1", "vr20", "vr60", "vr240", "v_vs_oldleg", "v_ratio_prev"]
print(df[hardskip][cols].to_string(index=False))
print("\nSOFT skips volume detail:")
print(df[(df.label == "SKIP") & (df.certainty == "SOFT")][cols].to_string(index=False))
print("\ntakes with lowest vr240:")
print(df[takes].nsmallest(12, "vr240")[cols].to_string(index=False))
print("\ntakes with lowest v_j:")
print(df[takes].nsmallest(12, "v_j")[cols].to_string(index=False))
