"""Family E step 5: session-start event ledger — what fired between session open and
the first TAKEN trade, per session. Tests T2-resume consistency and evening structure."""
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
is_up = late.is_up
time_strs = [str(t) for t in bars["time"]]
first_bar = bars["first_bar"]

cut = int(np.searchsorted(bars["time"], np.datetime64("2023-01-21")))
sess_starts = [i for i in range(cut) if first_bar[i]]

# first TAKEN trade decision-bar per session (from labels)
first_taken = {
    "2023-01-03": "2023-01-02T21:39:00", "2023-01-04": "2023-01-03T20:14:00",
    "2023-01-05": "2023-01-05T02:52:00", "2023-01-06": "2023-01-05T19:33:00",
    "2023-01-09": "2023-01-09T02:42:00", "2023-01-10": "2023-01-10T02:03:00",
    "2023-01-11": "2023-01-11T02:04:00", "2023-01-12": "2023-01-12T08:31:00",
    "2023-01-13": "2023-01-12T20:36:00", "2023-01-16": "2023-01-16T01:33:00",
    "2023-01-17": "MISSING_T2_2048", "2023-01-18": "2023-01-17T18:04:00",
    "2023-01-19": "2023-01-19T03:16:00", "2023-01-20": "2023-01-20T03:26:00",
}
tidx = {t: i for i, t in enumerate(time_strs)}

for si, s in enumerate(sess_starts):
    e = sess_starts[si + 1] if si + 1 < len(sess_starts) else cut
    day = str(bars["time"][e - 1])[:10]
    ft = first_taken.get(day)
    if ft is None:
        continue
    if ft.startswith("MISSING"):
        stop_i = tidx["2023-01-16T20:48:00"]  # fill bar of the missing short
    else:
        stop_i = tidx[ft]  # fill bar; decision bar is -1
    trend0 = "UP" if is_up[s] else "DN"
    print(f"\n=== session ending {day} | open {time_strs[s]} trend@open={trend0} "
          f"| first taken fill {ft}")
    for i in range(s, min(stop_i, e)):
        evs = []
        if abs(st[i]) == 1:
            evs.append(f"FLIP{'+' if st[i]>0 else '-'}")
        if abs(st[i]) == 3:
            evs.append(f"E-T3{'+' if st[i]>0 else '-'}")
        if abs(st[i]) == 2:
            evs.append(f"E-T2{'+' if st[i]>0 else '-'}")
        if abs(stL[i]) == 2:
            evs.append(f"L-T2{'+' if stL[i]>0 else '-'}")
        if evs:
            print(f"  {time_strs[i][11:16]} {' '.join(evs)} close={close[i]:.2f} "
                  f"nxt_open={opn[i+1]:.2f} trend={'UP' if is_up[i] else 'DN'}")
