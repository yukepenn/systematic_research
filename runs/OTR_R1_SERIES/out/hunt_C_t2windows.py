"""Family C: list LATE-mode T2 fires inside truth-flat windows (Jan 2023)."""
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

wins = [
    ("01-02 eve warmup up-leg", "2023-01-02T18:01", "2023-01-02T21:38"),
    ("01-03 12:38-12:47 up",    "2023-01-03T12:38", "2023-01-03T12:47"),
    ("01-03 13:29-16:03 up",    "2023-01-03T13:29", "2023-01-03T16:03"),
    ("01-04 eve 18:01-21:05 up","2023-01-04T18:01", "2023-01-04T21:05"),
    ("01-04 21:07-23:34 down",  "2023-01-04T21:07", "2023-01-04T23:34"),
    ("01-04/05 23:37-02:50 up", "2023-01-04T23:37", "2023-01-05T02:50"),
    ("01-05 12:22-13:23 up",    "2023-01-05T12:22", "2023-01-05T13:23"),
    ("01-05 13:25-14:15 down",  "2023-01-05T13:25", "2023-01-05T14:15"),
    ("01-05 14:17-17:00 up",    "2023-01-05T14:17", "2023-01-05T17:00"),
    ("01-08 eve 18:02-02:41 up","2023-01-08T18:02", "2023-01-09T02:41"),
    ("01-12 eve 18:01-19:15 dn","2023-01-12T18:01", "2023-01-12T19:15"),
    ("01-12 eve 19:18-20:34 up","2023-01-12T19:18", "2023-01-12T20:34"),
    ("01-16 eve 18:01-07:20 dn","2023-01-16T18:01", "2023-01-17T07:20"),
]
print("LATE-mode T2 fires in truth-flat windows:")
for name, t0, t1 in wins:
    a, b = np.datetime64(t0), np.datetime64(t1)
    m = (time >= a) & (time <= b) & S["fire_late"]
    idx = np.flatnonzero(m)
    fires = [(str(time[i]), "L" if S["is_up"][i] else "S",
              float(c[i]), float(o[i+1]) if i+1 < bars["n"] else np.nan) for i in idx]
    print(f"  {name}: {len(idx)} fires")
    for f in fires:
        print(f"      fire@{f[0]} dir={f[1]} close={f[2]} next_open={f[3]}")

# Also EARLY-mode fires in 01-16 eve for comparison, and check the 20:47 candidate
a, b = np.datetime64("2023-01-16T18:01"), np.datetime64("2023-01-17T07:20")
m = (time >= a) & (time <= b) & S["fire_early"]
print("\nEARLY-mode fires 01-16 eve:", [str(time[i]) for i in np.flatnonzero(m)])
