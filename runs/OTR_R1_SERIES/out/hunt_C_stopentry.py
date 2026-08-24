"""Family C pass 5: STOP-CONFIRMATION ENTRY hypothesis.

Entry on a T1 flip is a STOP order at the flip-bar close (direction of the new
trend), instead of a market order:
  long flip at bar j (signal close C=close[j]):  buy stop @ C
    - open[j+1] >= C  -> fill at open[j+1]   (== base market fill, cent-exact)
    - open[j+1] <  C  -> fills at C iff high[j+1] >= C   (price 'confirms')
    - else            -> expires (life = 1 bar)  -> SKIP
  short flip: mirrored.

Predictions:
  HARD-day TAKEs  : d*(open[j+1]-close[j]) >= 0        (fill at open)
  HARD-day SKIPs  : d*(open[j+1]-close[j]) < 0 AND no touch of C on bar j+1
                    (and, for longer order life L, no touch for L bars)
  EPS-day TAKEs   : mostly >=0; the few adverse ones touched C -> fill at C
                    (entry differs from base by |open-C| = the price epsilon)
  SOFT-day SKIPs  : adverse AND no touch.
"""
import os, sys
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, r"research\original_trader_reconstruction\solar_family\src"))
sys.path.insert(0, os.path.join(ROOT, r"src\analytics"))
sys.path.insert(0, os.path.join(ROOT, r"runs\OTR_R1_SERIES\out"))

from otr_engine import load_ledger
from hunt_C import jan_slice, base_trades

LEDGER = os.path.join(ROOT, r"research\03_reverse_engineering\ledgers\t2_canonical_1m.csv")
FEAT = os.path.join(ROOT, r"runs\OTR_R1_SERIES\out\r12f_flip_features.csv")

bars = load_ledger(LEDGER)
o, h, l, c = bars["open"], bars["high"], bars["low"], bars["close"]
time = bars["time"]
last_bar = bars["last_bar"]

sl = jan_slice(bars)
trades = base_trades(sl)
lab = pd.read_csv(FEAT)[["entry_time", "label", "certainty"]]
lmap = dict(zip(lab.entry_time, zip(lab.label, lab.certainty)))

print(f"{'entry_time':>19} {'d':>2} {'label':>5} {'cert':>4} {'gap=d*(o1-C)':>12} "
      f"{'touch1':>6} {'touchN(<=flip)':>13} {'pred(V1)':>8} ok")

n_ok = n_bad = 0
rows = []
for t in trades:
    j = t["entry_i"] - 1
    d = 1 if t["dir"] > 0 else -1
    C = c[j]
    gap = d * (o[j + 1] - C)
    # touch on bar j+1
    touch1 = (h[j + 1] >= C) if d > 0 else (l[j + 1] <= C)
    # touch any bar until leg end (next opposite flip) or session end
    k = j + 1
    touchN = False
    first_touch = None
    while k < bars["n"]:
        tt = (h[k] >= C) if d > 0 else (l[k] <= C)
        if tt:
            touchN = True
            first_touch = str(time[k])
            break
        if last_bar[k] or (abs(bars["signal_trade"][k]) == 1 and np.sign(bars["signal_trade"][k]) != d):
            break
        k += 1
    lb, ct = lmap[t["entry_time"]]
    # V1 prediction: TAKE iff gap >= 0 or touch1
    pred = "TAKE" if (gap >= 0 or touch1) else "SKIP"
    ok = pred == lb
    n_ok += ok; n_bad += (not ok)
    rows.append(dict(entry_time=t["entry_time"], d=d, label=lb, cert=ct, gap=gap,
                     touch1=touch1, touchN=touchN, first_touch=first_touch, pred=pred, ok=ok))
    flag = "" if ok else "   <-- MISMATCH"
    print(f"{t['entry_time']:>19} {d:>2} {lb:>5} {ct:>4} {gap:12.2f} {str(touch1):>6} "
          f"{str(touchN):>13} {pred:>8} {flag}")

print(f"\nV1 (life=1 bar): {n_ok}/{len(trades)} labels reproduced")

df = pd.DataFrame(rows)
print("\nby certainty:")
for ct in ("HARD", "EPS", "SOFT"):
    s = df[df.cert == ct]
    print(f"  {ct}: {s.ok.sum()}/{len(s)}")
print("\nHARD takes with adverse gap (must be zero for cent-exactness):")
print(df[(df.cert == "HARD") & (df.label == "TAKE") & (df.gap < 0)].to_string(index=False))
print("\nEPS takes with adverse gap (these are the epsilon fills, entry=C):")
print(df[(df.cert == "EPS") & (df.label == "TAKE") & (df.gap < 0)].to_string(index=False))
print("\nmismatches:")
print(df[~df.ok].to_string(index=False))
