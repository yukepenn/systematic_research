"""FAMILY A hunt, step 2: rich per-flip feature dump + brute rule scan."""
import sys, csv
import numpy as np

sys.path.insert(0, r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\research\original_trader_reconstruction\solar_family\src")
sys.path.insert(0, r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\src\analytics")

from otr_engine import load_ledger
from solarwave import solar_wave, solar_wave_full, SolarWaveParams

LEDGER = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\research\03_reverse_engineering\ledgers\t2_canonical_1m.csv"
FEAT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\runs\OTR_R1_SERIES\out\r12f_flip_features.csv"

bars = load_ledger(LEDGER)
n = bars["n"]
o, h, l, c = bars["open"], bars["high"], bars["low"], bars["close"]
st_ledger = bars["signal_trade"]
time_arr = bars["time"]
tstr = np.array([str(t) for t in time_arr])
idx_of = {s: i for i, s in enumerate(tstr)}

pF = SolarWaveParams(pullback_early=False)
rF = solar_wave_full(o, h, l, c, pF, start_up=False)
base = solar_wave(c, SolarWaveParams(), start_up=False)
anchor = base.anchor
is_up = base.is_up
tv = base.trend_vector
ts = base.trailing_stop
flip = np.abs(base.signal_trade) == 1
fireF = np.abs(rF.signal_trade) == 2
t3 = np.abs(base.signal_trade) == 3
strend = rF.signal_trend
swave = rF.signal_wave

# bars since anchor update (stagnation)
bse = np.zeros(n, np.int64)
for t in range(1, n):
    bse[t] = 0 if (anchor[t] != anchor[t - 1] or flip[t]) else bse[t - 1] + 1

leg_id = np.cumsum(flip)
nlegs = int(leg_id[-1]) + 1
leg_start = np.zeros(nlegs, np.int64)
for t in np.where(flip)[0]:
    leg_start[leg_id[t]] = t
leg_fireF = np.zeros(nlegs, np.int64)
for t in np.where(fireF)[0]:
    leg_fireF[leg_id[t]] += 1
leg_t3 = np.zeros(nlegs, np.int64)
for t in np.where(t3)[0]:
    leg_t3[leg_id[t]] += 1

last_fireF = np.full(n, -1, np.int64)
lf = -1
for t in range(n):
    last_fireF[t] = lf
    if fireF[t]:
        lf = t

mod = (time_arr - time_arr.astype("datetime64[D]")).astype("timedelta64[s]").astype(np.int64) // 60
sess_id = bars["session_id"]
first_bar = bars["first_bar"]
# session open price
sess_open_px = np.zeros(n)
cur = np.nan
for t in range(n):
    if first_bar[t]:
        cur = o[t]
    sess_open_px[t] = cur

rows = list(csv.DictReader(open(FEAT, newline="")))
print(f"{'entry_time':<20}{'cert':>5}{'lab':>5} d | {'mod':>5}{'wkT':>4}{'legB':>5}{'leg2B':>6}{'wave':>5}"
      f"{'nF1':>4}{'nF2':>4}{'t3c':>4}{'bsF':>5}{'marg':>7}{'rng':>6}{'body':>7}{'bse':>4}{'cvo':>7}{'mtmX':>8}{'lastTrPnL':>10}")

recs = []
prev_trade_pnl_by_exit_bar = {}
# reconstruct base-run trade pnl of trade exiting at each flip fill: use r12f pnl_this_trade of PREVIOUS row same session? simpler: r12f rows are sequential base trades; trade k exits at entry fill of trade k+1 when exit_kind == 'flip'
for k, r in enumerate(rows):
    if r["exit_kind"] == "flip" and k + 1 < len(rows):
        prev_trade_pnl_by_exit_bar[rows[k + 1]["entry_time"]] = float(r["pnl_this_trade"])

for r in rows:
    et = r["entry_time"]
    i_fill = idx_of[et]
    s = i_fill - 1
    d = 1 if r["dir"] == "L" else -1
    lg = leg_id[s]           # new leg (starts at s)
    prev_lg = lg - 1         # leg that just ended
    same_dir_prev = lg - 2   # previous leg of same direction
    legB = s - leg_start[prev_lg]
    leg2B = leg_start[prev_lg] - leg_start[same_dir_prev] if same_dir_prev >= 0 else -1
    weak_prev = abs(strend[s - 1])          # 1 = weak, 2 = strong at bar before flip
    wave_end = abs(swave[s - 1])
    nF1 = leg_fireF[prev_lg]
    nF2 = leg_fireF[same_dir_prev] if same_dir_prev >= 0 else -1
    t3c = leg_t3[prev_lg]
    bsF = s - last_fireF[s] if last_fireF[s] >= 0 else 9999
    marg = d * (c[s] - ts[s - 1])           # how far close punched through the old stop
    rng = h[s] - l[s]
    body = abs(c[s] - o[s])
    cvo = (c[s] - sess_open_px[s]) * d      # close vs session open, signed by dir
    mtmX = np.nan
    # MTM of the exiting base trade at s close: prev trade entry px = open of its fill bar
    ptp = prev_trade_pnl_by_exit_bar.get(et, np.nan)
    recs.append(dict(et=et, cert=r["certainty"], lab=r["label"], d=d, s=s, mod=int(mod[s]),
                     weak_prev=weak_prev, legB=int(legB), leg2B=int(leg2B), wave_end=int(wave_end),
                     nF1=int(nF1), nF2=int(nF2), t3c=int(t3c), bsF=int(bsF), marg=float(marg),
                     rng=float(rng), body=float(body), bse=int(bse[s]), cvo=float(cvo),
                     prevpnl=ptp))
    print(f"{et:<20}{r['certainty']:>5}{r['label']:>5} {r['dir']} | {int(mod[s]):>5}{weak_prev:>4}{legB:>5}{leg2B:>6}"
          f"{wave_end:>5}{nF1:>4}{nF2:>4}{t3c:>4}{min(bsF,9999):>5}{marg:>7.2f}{rng:>6.2f}{body:>7.2f}{bse[s]:>4}"
          f"{cvo:>7.1f}{'':>8}{ptp if ptp==ptp else 0:>10.2f}")

import json
json.dump(recs, open(r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\runs\OTR_R1_SERIES\out\hunt_A_recs.json", "w"))
