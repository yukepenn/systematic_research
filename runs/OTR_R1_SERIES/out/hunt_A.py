"""FAMILY A hunt: signal-layer gate for SolarWindRKSelTime hidden rule.

Step 1: regenerate signals with pullback_early=False, verify flip parity vs ledger,
and dump T2-layer state features at each labeled flip entry.
"""
import sys, csv
import numpy as np

sys.path.insert(0, r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\research\original_trader_reconstruction\solar_family\src")
sys.path.insert(0, r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\src\analytics")

from otr_engine import load_ledger, run_wrapper, WrapperPolicy
from solarwave import solar_wave, solar_wave_full, SolarWaveParams

LEDGER = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\research\03_reverse_engineering\ledgers\t2_canonical_1m.csv"
FEAT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\runs\OTR_R1_SERIES\out\r12f_flip_features.csv"

bars = load_ledger(LEDGER)
n = bars["n"]
print("bars:", n, bars["time"][0], bars["time"][-1])

o, h, l, c = bars["open"], bars["high"], bars["low"], bars["close"]
st_ledger = bars["signal_trade"]

# regenerate with PE=True and PE=False, both start_up options
for su in (False, True):
    pT = SolarWaveParams(pullback_early=True)
    rT = solar_wave_full(o, h, l, c, pT, start_up=su)
    flips_match = np.array_equal(np.where(np.abs(rT.signal_trade) == 1)[0],
                                 np.where(np.abs(st_ledger) == 1)[0])
    full_match = np.array_equal(rT.signal_trade, st_ledger)
    print(f"start_up={su}: PE=True flips match ledger: {flips_match}, full signal_trade match: {full_match}")
    if flips_match:
        SU = su

pF = SolarWaveParams(pullback_early=False)
rF = solar_wave_full(o, h, l, c, pF, start_up=SU)
rT = solar_wave_full(o, h, l, c, SolarWaveParams(pullback_early=True), start_up=SU)
print("PE=False flips match:", np.array_equal(np.where(np.abs(rF.signal_trade) == 1)[0],
                                              np.where(np.abs(st_ledger) == 1)[0]))
nf2_F = int((np.abs(rF.signal_trade) == 2).sum())
nf2_T = int((np.abs(rT.signal_trade) == 2).sum())
print("T2 count PE=False:", nf2_F, " PE=True:", nf2_T)

# --- instrumented PE=False T2 state: armed(before bar), fire, next_pb ---
def t2_state(o, h, l, c, params, start_up, early):
    p = params
    base = solar_wave(c, p, start_up=start_up)
    is_up = base.is_up
    tv = base.trend_vector
    flip = np.abs(base.signal_trade) == 1
    t3 = np.abs(base.signal_trade) == 3
    nb = len(c)
    fire = np.zeros(nb, bool)
    armed_before = np.zeros(nb, bool)
    armed_after = np.zeros(nb, bool)
    nextpb_arr = np.zeros(nb, np.int64)
    armed = True
    next_pb = -(1 << 60)
    for t in range(nb):
        armed_before[t] = armed
        if flip[t]:
            armed = True
            next_pb = -(1 << 60)
            armed_after[t] = armed
            nextpb_arr[t] = max(next_pb, -1)
            continue
        up = bool(is_up[t])
        if early:
            ext = l[t] if up else h[t]
            beyond = ext < tv[t] if up else ext > tv[t]
            inside = ext > tv[t] if up else ext < tv[t]
            if beyond and armed and t > next_pb and t > 0:
                fire[t] = True
                next_pb = t + p.pullback_split
            if beyond:
                armed = False
            elif inside:
                armed = True
        else:
            open_beyond = o[t] < tv[t] if up else o[t] > tv[t]
            close_beyond = c[t] < tv[t] if up else c[t] > tv[t]
            close_inside = c[t] > tv[t] if up else c[t] < tv[t]
            if (not armed or open_beyond) and close_inside and t > next_pb and t > 0:
                fire[t] = True
                next_pb = t + p.pullback_split
            if close_beyond:
                armed = False
            elif close_inside:
                armed = True
        if t3[t]:
            armed = True
        armed_after[t] = armed
        nextpb_arr[t] = max(next_pb, -1)
    return base, fire, armed_before, armed_after, nextpb_arr, flip, t3, is_up, tv

baseF, fireF, armedB_F, armedA_F, nextpbF, flip, t3, is_up, tv = t2_state(o, h, l, c, pF, SU, early=False)
baseT, fireT, armedB_T, armedA_T, nextpbT, _, _, _, _ = t2_state(o, h, l, c, SolarWaveParams(pullback_early=True), SU, early=True)

# sanity: fires equal the ±2 of solar_wave_full outputs
print("fireF == rF ±2 bars:", np.array_equal(fireF & ~flip, (np.abs(rF.signal_trade) == 2)))
print("fireT == ledger ±2 bars:", np.array_equal(fireT & ~flip, (np.abs(st_ledger) == 2)))

# time index for lookup
time_arr = bars["time"]
tstr = np.array([str(t) for t in time_arr])
idx_of = {s: i for i, s in enumerate(tstr)}

# leg ids: leg = span between flips
leg_id = np.cumsum(flip)  # increments at each flip bar (flip bar belongs to NEW leg)

# per-leg fire info (PE=False)
nlegs = int(leg_id[-1]) + 1
leg_fireF = np.zeros(nlegs, bool)
leg_fire_countF = np.zeros(nlegs, np.int64)
for t in np.where(fireF)[0]:
    leg_fireF[leg_id[t]] = True
    leg_fire_countF[leg_id[t]] += 1
leg_fireT = np.zeros(nlegs, bool)
for t in np.where(fireT)[0]:
    leg_fireT[leg_id[t]] = True

# last fire index (PE=False) before each bar
last_fireF_idx = np.full(n, -1, np.int64)
lf = -1
for t in range(n):
    last_fireF_idx[t] = lf   # last fire STRICTLY before bar t
    if fireF[t]:
        lf = t
last_fireT_idx = np.full(n, -1, np.int64)
lf = -1
for t in range(n):
    last_fireT_idx[t] = lf
    if fireT[t]:
        lf = t

# load label table
rows = []
with open(FEAT, newline="") as f:
    for r in csv.DictReader(f):
        rows.append(r)

print("\nlabel rows:", len(rows))
hdr = ("entry_time cert label dir | sigbar armB_F armA_F fired_prev_legF nfire_prevlegF "
       "barsSinceFireF fireT_prevleg armB_T sinceFireT nextpbF_open")
print(hdr)
for r in rows:
    et = r["entry_time"]
    # fill bar = et ; signal bar = et - 1 min
    i_fill = idx_of.get(et)
    if i_fill is None:
        print(et, "NOT FOUND")
        continue
    s = i_fill - 1
    assert abs(st_ledger[s]) == 1, (et, st_ledger[s])
    prev_leg = leg_id[s] - 1  # leg that just ended at this flip
    bsf = s - last_fireF_idx[s] if last_fireF_idx[s] >= 0 else -1
    bsfT = s - last_fireT_idx[s] if last_fireT_idx[s] >= 0 else -1
    pb_open = 1 if (nextpbF[s - 1] >= 0 and s <= nextpbF[s - 1]) else 0  # inside PB cooldown at flip
    print(f"{et} {r['certainty']:>4} {r['label']:>4} {r['dir']} | {s:6d} "
          f"{int(armedB_F[s])} {int(armedA_F[s])} {int(leg_fireF[prev_leg])} {int(leg_fire_countF[prev_leg]):2d} "
          f"{bsf:6d} {int(leg_fireT[prev_leg])} {int(armedB_T[s])} {bsfT:6d} {pb_open}")
