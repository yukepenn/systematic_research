"""Family E hunt: skeptic/combinatorial gate search for SolarWindRKSelTime.

Step 1: load ledger + labels; verify EARLY signals reproduce; compute LATE signals.
Step 2: test the stop-at-anchor fill predicate: TAKE iff next bar OPEN is at/beyond
        the flip bar close (buy stop at anchor for longs, sell stop for shorts).
"""
import sys, csv
import numpy as np

sys.path.insert(0, r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\research\original_trader_reconstruction\solar_family\src")
sys.path.insert(0, r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\src\analytics")

from otr_engine import load_ledger
from solarwave import solar_wave_full, SolarWaveParams

LEDGER = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\research\03_reverse_engineering\ledgers\t2_canonical_1m.csv"
FEAT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\runs\OTR_R1_SERIES\out\r12f_flip_features.csv"

bars = load_ledger(LEDGER)
n = bars["n"]
print("bars:", n, bars["time"][0], "->", bars["time"][-1])

# recompute EARLY + LATE signals from OHLC
early = solar_wave_full(bars["open"], bars["high"], bars["low"], bars["close"],
                        SolarWaveParams(pullback_early=True))
late = solar_wave_full(bars["open"], bars["high"], bars["low"], bars["close"],
                       SolarWaveParams(pullback_early=False))
print("EARLY signal_trade match vs ledger:", float(np.mean(early.signal_trade == bars["signal_trade"])))
print("flip bars identical EARLY vs LATE:",
      bool(np.all((np.abs(early.signal_trade) == 1) == (np.abs(late.signal_trade) == 1))))

# labels
labels = []
with open(FEAT, newline="") as f:
    for row in csv.DictReader(f):
        labels.append(row)
print("label rows:", len(labels))

# map entry_time -> flip bar index. Entry time in CSV is the FLIP bar end-stamp
# (decision bar), fill at next bar open.
time_strs = np.array([str(t) for t in bars["time"]])
tidx = {t: i for i, t in enumerate(time_strs)}

st = bars["signal_trade"]
opn, close, high, low = bars["open"], bars["close"], bars["high"], bars["low"]

print("\n=== Predicate P1: next bar OPEN at/beyond flip close (stop-at-anchor fill) ===")
hdr = f"{'entry_time':<20}{'dir':<4}{'label':<6}{'cert':<6}{'nxt_open-close':>14}  P1(>=0/<=0) P1s(strict)"
print(hdr)
res = []
for row in labels:
    et = row["entry_time"].replace("T", "T")
    i = tidx.get(et)
    if i is None:
        print("MISSING BAR", et); continue
    d = 1 if row["dir"] == "L" else -1
    sig = st[i]
    gap = (opn[i + 1] - close[i]) * d
    p1 = gap >= 0        # take iff open at-or-beyond
    p1s = gap > 0        # strict
    res.append((row, i, d, gap, p1, p1s))
    lab = row["label"]
    ok1 = (lab == "TAKE") == p1
    ok1s = (lab == "TAKE") == p1s
    flag = "" if ok1 else "  <-- P1 MISS"
    print(f"{et:<20}{row['dir']:<4}{lab:<6}{row['certainty']:<6}{gap*d:>14.2f}  "
          f"{str(p1):<10} {str(p1s):<10}{flag}")

for name, k in [("P1 >=0", 4), ("P1 strict", 5)]:
    nh = sh = eh = 0; nH = sS = eE = 0
    for r in res:
        lab = r[0]["label"]; cert = r[0]["certainty"]
        ok = (lab == "TAKE") == r[k]
        if cert == "HARD": nH += 1; nh += ok
        elif cert == "SOFT": sS += 1; sh += ok
        else: eE += 1; eh += ok
    print(f"{name}: HARD {nh}/{nH}  SOFT {sh}/{sS}  EPS {eh}/{eE}")
