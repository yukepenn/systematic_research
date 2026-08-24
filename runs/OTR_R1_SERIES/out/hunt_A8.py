"""FAMILY A hunt, step 8: raw tape inspection around hard contrasts."""
import sys
import numpy as np

sys.path.insert(0, r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\research\original_trader_reconstruction\solar_family\src")
sys.path.insert(0, r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\src\analytics")
from otr_engine import load_ledger
from solarwave import solar_wave_full, SolarWaveParams

LEDGER = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\research\03_reverse_engineering\ledgers\t2_canonical_1m.csv"
bars = load_ledger(LEDGER)
n = bars["n"]
o, h, l, c, v = bars["open"], bars["high"], bars["low"], bars["close"], bars["volume"]
tstr = np.array([str(t) for t in bars["time"]])
idx_of = {s: i for i, s in enumerate(tstr)}

rF = solar_wave_full(o, h, l, c, SolarWaveParams(pullback_early=False), start_up=False)

def dump(t0, t1):
    i0, i1 = idx_of[t0], idx_of[t1]
    print(f"\n=== {t0} .. {t1} ===")
    print(f"{'time':<20}{'open':>9}{'high':>9}{'low':>9}{'close':>9}{'vol':>7}{'sig':>4}{'st':>3}{'wv':>4}{'TS':>10}{'TV':>10}")
    for i in range(i0, i1 + 1):
        print(f"{tstr[i]:<20}{o[i]:>9.2f}{h[i]:>9.2f}{l[i]:>9.2f}{c[i]:>9.2f}{int(v[i]):>7}"
              f"{rF.signal_trade[i]:>4}{rF.signal_trend[i]:>3}{rF.signal_wave[i]:>4}{rF.trailing_stop[i]:>10.2f}{rF.trend_vector[i]:>10.2f}")

dump("2023-01-03T12:30:00", "2023-01-03T12:52:00")
dump("2023-01-03T13:22:00", "2023-01-03T13:32:00")
dump("2023-01-03T16:00:00", "2023-01-03T16:08:00")
dump("2023-01-05T12:15:00", "2023-01-05T12:25:00")
dump("2023-01-05T13:19:00", "2023-01-05T13:28:00")
dump("2023-01-05T14:11:00", "2023-01-05T14:20:00")
dump("2023-01-05T11:43:00", "2023-01-05T11:51:00")
dump("2023-01-04T21:02:00", "2023-01-04T21:11:00")
dump("2023-01-04T23:31:00", "2023-01-04T23:40:00")
dump("2023-01-05T02:48:00", "2023-01-05T02:56:00")
dump("2023-01-08T18:01:00", "2023-01-08T18:06:00")
dump("2023-01-09T02:38:00", "2023-01-09T02:46:00")
dump("2023-01-16T20:42:00", "2023-01-16T20:52:00")
dump("2023-01-17T05:35:00", "2023-01-17T05:42:00")
dump("2023-01-17T06:41:00", "2023-01-17T06:48:00")
dump("2023-01-17T07:18:00", "2023-01-17T07:24:00")
dump("2023-01-02T21:35:00", "2023-01-02T21:42:00")
