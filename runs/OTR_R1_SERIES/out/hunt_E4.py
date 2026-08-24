"""Family E step 4: bar-level context around skipped vs taken flips."""
import sys
import numpy as np

sys.path.insert(0, r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\research\original_trader_reconstruction\solar_family\src")
sys.path.insert(0, r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\src\analytics")
from otr_engine import load_ledger
from solarwave import solar_wave_full, SolarWaveParams

LEDGER = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\research\03_reverse_engineering\ledgers\t2_canonical_1m.csv"
bars = load_ledger(LEDGER)
n = bars["n"]
opn, high, low, close = bars["open"], bars["high"], bars["low"], bars["close"]
st = bars["signal_trade"]
late = solar_wave_full(opn, high, low, close, SolarWaveParams(pullback_early=False))
stL = late.signal_trade
ts, tv = bars["trailing_stop"], bars["trend_vector"]
sw, str_ = bars["signal_wave"], bars["signal_trend"]
time_strs = [str(t) for t in bars["time"]]
tidx = {t: i for i, t in enumerate(time_strs)}

flips = np.where(np.abs(st) == 1)[0]

# for each labeled flip event print: flip bar detail + events within the dying leg and
# the following leg (early T2/T3, late T2)
events = [
    ("SKIP", "2023-01-03T12:37:00"), ("TAKE", "2023-01-03T12:48:00"),
    ("SKIP", "2023-01-03T13:28:00"), ("TAKE", "2023-01-03T16:04:00"),
    ("SKIP", "2023-01-04T21:07:00"), ("SKIP", "2023-01-04T23:36:00"),
    ("TAKE", "2023-01-05T02:52:00"),
    ("SKIP", "2023-01-05T12:21:00"), ("SKIP", "2023-01-05T13:24:00"),
    ("SKIP", "2023-01-05T14:16:00"), ("TAKE", "2023-01-05T19:33:00"),
    ("SKIP", "2023-01-08T18:02:00"), ("TAKE", "2023-01-09T02:42:00"),
    ("SKIP", "2023-01-12T13:39:00"), ("TAKE", "2023-01-12T14:54:00"),
    ("SKIP", "2023-01-12T19:17:00"), ("TAKE", "2023-01-12T20:36:00"),
    ("TAKE", "2023-01-02T21:39:00"), ("TAKE", "2023-01-17T18:04:00"),
]
for lab, t in events:
    i = tidx[t] - 1
    d = int(np.sign(st[i]))
    k = int(np.searchsorted(flips, i))
    pf = flips[k - 1] if k > 0 else 0
    nf = flips[k + 1] if k + 1 < len(flips) else n - 1
    breach = d * (close[i] - ts[i - 1])
    # events in dying leg (pf..i) and new leg (i..nf)
    def ev(a, b, arr, mag):
        w = np.where(np.abs(arr[a + 1:b]) == mag)[0] + a + 1
        return [time_strs[j][11:16] + ("+" if arr[j] > 0 else "-") for j in w]
    print(f"{lab} {t[5:16]} dir={'L' if d>0 else 'S'} breach={breach:.2f} "
          f"bar o/h/l/c={opn[i]:.2f}/{high[i]:.2f}/{low[i]:.2f}/{close[i]:.2f} "
          f"legs: prev {i-pf}b next {nf-i}b")
    print(f"    dyingleg E-T2 {ev(pf, i, st, 2)} E-T3 {ev(pf, i, st, 3)} L-T2 {ev(pf, i, stL, 2)}")
    print(f"    newleg   E-T2 {ev(i, nf, st, 2)} E-T3 {ev(i, nf, st, 3)} L-T2 {ev(i, nf, stL, 2)}")
