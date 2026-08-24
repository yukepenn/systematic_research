"""Family C: solar state around candidate origin bars of the missing -274.18 short."""
import os, sys
import numpy as np

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, r"research\original_trader_reconstruction\solar_family\src"))
sys.path.insert(0, os.path.join(ROOT, r"src\analytics"))
sys.path.insert(0, os.path.join(ROOT, r"runs\OTR_R1_SERIES\out"))

from otr_engine import load_ledger
from solarwave import SolarWaveParams
from hunt_C import instrumented_state

LEDGER = os.path.join(ROOT, r"research\03_reverse_engineering\ledgers\t2_canonical_1m.csv")
bars = load_ledger(LEDGER)
o, h, l, c = bars["open"], bars["high"], bars["low"], bars["close"]
S = instrumented_state(o, h, l, c, SolarWaveParams())
time = bars["time"]

for tstr in ["2023-01-16T20:48", "2023-01-17T05:39", "2023-01-17T06:45"]:
    j = int(np.flatnonzero(time == np.datetime64(tstr + ":00"))[0])
    print(f"\n=== around {tstr} (entry bar j={j}, open={o[j]}) ===")
    for i in range(j - 6, j + 3):
        up = S["is_up"][i]
        tv = S["anchor"][i] + (-(22.5) if up else 22.5)
        ts_ = S["anchor"][i] + (-(44.75) if up else 44.75)
        print(f"  {str(time[i])[5:16]} O={o[i]:9.2f} H={h[i]:9.2f} L={l[i]:9.2f} C={c[i]:9.2f}"
              f" up={int(up)} anch={S['anchor'][i]:9.2f} TV={tv:9.2f} TS={ts_:9.2f}"
              f" ev={S['event'][i]} weak={int(S['weak'][i])} bse={S['bse'][i]:3d}"
              f" w={S['wave'][i]} t3={int(S['t3'][i])} fL={int(S['fire_late'][i])}"
              f" fE={int(S['fire_early'][i])} armL={int(S['armed_late'][i])}"
              f" armE={int(S['armed_early'][i])}")

# any bar in the window whose NEXT open == 14712.75
a, b = np.datetime64("2023-01-16T18:01"), np.datetime64("2023-01-17T07:20")
m = (time >= a) & (time <= b)
idx = np.flatnonzero(m)
hits = [i for i in idx if i + 1 < bars["n"] and o[i + 1] == 14712.75]
print("\nbars in window with next_open == 14712.75:", [str(time[i]) for i in hits])
# weak-transition bars (weak goes False->True) in window
wk = [i for i in idx if S["weak"][i] and not S["weak"][i-1]]
print("weak-declared bars:", [str(time[i]) for i in wk])
t3b = [i for i in idx if S["t3"][i]]
print("T3 bars:", [str(time[i]) for i in t3b])
ev1 = [i for i in idx if S["event"][i] == 1]
print(f"new-extreme bars: {len(ev1)} (first few: {[str(time[i]) for i in ev1[:5]]} ... last: {[str(time[i]) for i in ev1[-5:]]})")
