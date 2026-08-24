"""FAMILY A hunt, step 5: decision-tree discovery over expanded feature bank."""
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
o, h, l, c, vol = bars["open"], bars["high"], bars["low"], bars["close"], bars["volume"]
time_arr = bars["time"]
sess_id = bars["session_id"]
first_bar = bars["first_bar"]
tstr = np.array([str(t) for t in time_arr])
idx_of = {s: i for i, s in enumerate(tstr)}
mod = (time_arr - time_arr.astype("datetime64[D]")).astype("timedelta64[s]").astype(np.int64) // 60
dow = ((time_arr.astype("datetime64[D]").astype(np.int64) + 4) % 7).astype(np.int64)  # 0=Mon? 1970-01-01 Thu=3 -> +4 => Mon=0

base = solar_wave(c, SolarWaveParams(), start_up=False)
rF = solar_wave_full(o, h, l, c, SolarWaveParams(pullback_early=False), start_up=False)
flip = np.abs(base.signal_trade) == 1
fireF = np.abs(rF.signal_trade) == 2
anchor = base.anchor

# anchor-update tracker
anch_upd = np.zeros(n, np.int64)  # last bar index where anchor changed
last_u = 0
for t in range(1, n):
    if anchor[t] != anchor[t - 1]:
        last_u = t
    anch_upd[t] = last_u

leg_id = np.cumsum(flip)
nlegs = int(leg_id[-1]) + 1
leg_start = np.zeros(nlegs, np.int64)
for t in np.where(flip)[0]:
    leg_start[leg_id[t]] = t
leg_fireF = np.zeros(nlegs, np.int64)
for t in np.where(fireF)[0]:
    leg_fireF[leg_id[t]] += 1

def ema(x, span):
    a = 2.0 / (span + 1.0)
    out = np.empty_like(x, dtype=float)
    out[0] = x[0]
    for i in range(1, len(x)):
        out[i] = out[i - 1] + a * (x[i] - out[i - 1])
    return out

flip_cum = np.cumsum(flip)
fire_cum = np.cumsum(fireF)

sess_open_px = np.zeros(n); sess_hi = np.zeros(n); sess_lo = np.zeros(n); mis = np.zeros(n, np.int64)
cur_o = np.nan; cur_h = -np.inf; cur_l = np.inf; cur0 = 0
prev_close = np.zeros(n); last_c = np.nan; cur_pc = np.nan
for t in range(n):
    if first_bar[t]:
        cur_o = o[t]; cur_h = -np.inf; cur_l = np.inf; cur0 = t; cur_pc = last_c
    cur_h = max(cur_h, h[t]); cur_l = min(cur_l, l[t])
    sess_open_px[t] = cur_o; sess_hi[t] = cur_h; sess_lo[t] = cur_l; mis[t] = t - cur0
    prev_close[t] = cur_pc
    last_c = c[t]

rows = list(csv.DictReader(open(FEAT, newline="")))
S = []; D = []; LAB = []; CERT = []; ET = []
for r in rows:
    i_fill = idx_of[r["entry_time"]]
    S.append(i_fill - 1)
    D.append(1 if r["dir"] == "L" else -1)
    LAB.append(1 if r["label"] == "TAKE" else 0)
    CERT.append(r["certainty"]); ET.append(r["entry_time"])
S = np.array(S); D = np.array(D); LAB = np.array(LAB); CERT = np.array(CERT); ET = np.array(ET)

# per-label features
feats = {}
def addf(name, vals):
    feats[name] = np.asarray(vals, dtype=float)

sig = S
addf("dir", D)
addf("mod", mod[sig])
addf("mis", mis[sig])
addf("dow", dow[sig])
addf("legB", sig - leg_start[leg_id[sig] - 1])
addf("leg2B", np.where(leg_id[sig] >= 2, leg_start[np.maximum(leg_id[sig] - 1, 0)] - leg_start[np.maximum(leg_id[sig] - 2, 0)], -1))
addf("drop_bars", sig - anch_upd[sig - 1])  # bars since old leg's last extreme
addf("drop_speed", 44.75 / np.maximum(sig - anch_upd[sig - 1], 1))
prev_leg = leg_id[sig] - 1
addf("nF1", leg_fireF[prev_leg])
addf("nF2", np.where(prev_leg >= 1, leg_fireF[np.maximum(prev_leg - 1, 0)], -1))
addf("marg", D * (c[sig] - base.trailing_stop[sig - 1]))
addf("rng", h[sig] - l[sig])
addf("body", np.abs(c[sig] - o[sig]))
addf("cvo_s", D * (c[sig] - sess_open_px[sig]))
addf("cvo_raw", c[sig] - sess_open_px[sig])
addf("cvpc_s", D * (c[sig] - prev_close[sig]))
addf("sess_range", sess_hi[sig] - sess_lo[sig])
addf("pos_in_range_s", D * ((c[sig] - sess_lo[sig]) / np.maximum(sess_hi[sig] - sess_lo[sig], 1e-9) - 0.5))
addf("c_sesshi", c[sig] - sess_hi[sig])
addf("c_sesslo", c[sig] - sess_lo[sig])
for W in (15, 30, 60, 120, 240):
    addf(f"flips_last{W}", flip_cum[sig] - flip_cum[np.maximum(sig - W, 0)])
    addf(f"fires_last{W}", fire_cum[sig] - fire_cum[np.maximum(sig - W, 0)])
for N in (30, 60, 120, 240, 480):
    momN = c[sig] - c[np.maximum(sig - N, 0)]
    addf(f"mom{N}_s", D * momN)
    addf(f"mom{N}_raw", momN)
e200 = ema(c, 200); e500 = ema(c, 500); e1000 = ema(c, 1000)
addf("c_ema200_s", D * (c[sig] - e200[sig]))
addf("c_ema500_s", D * (c[sig] - e500[sig]))
addf("c_ema1000_s", D * (c[sig] - e1000[sig]))
addf("vol", vol[sig])
v60 = ema(vol, 60)
addf("vol_rel", vol[sig] / np.maximum(v60[sig], 1))
addf("v60", v60[sig])
addf("weak_prev", np.abs(rF.signal_trend[sig - 1]))
addf("wave_end", np.abs(rF.signal_wave[sig - 1]))
addf("day_idx", sess_id[sig])
# time since previous flip's previous... previous flip time-of-day
prevflip_mod = np.zeros(len(sig))
for k, s_ in enumerate(sig):
    pf = leg_start[leg_id[s_] - 1]
    prevflip_mod[k] = mod[pf]
addf("prevflip_mod", prevflip_mod)

X = np.column_stack([feats[k] for k in feats])
names = list(feats)
y = LAB
w = np.where(CERT == "HARD", 100.0, np.where(CERT == "SOFT", 3.0, 1.0))

from sklearn.tree import DecisionTreeClassifier, export_text
for depth in (2, 3, 4):
    for msl in (1, 2):
        t = DecisionTreeClassifier(max_depth=depth, min_samples_leaf=msl, random_state=0)
        t.fit(X, y, sample_weight=w)
        pred = t.predict(X)
        hard = CERT == "HARD"; softm = CERT == "SOFT"; epsm = CERT == "EPS"
        he = int((pred[hard] != y[hard]).sum()); se = int((pred[softm] != y[softm]).sum()); ee = int((pred[epsm] != y[epsm]).sum())
        print(f"depth={depth} msl={msl}: hard_err={he} soft_err={se} eps_err={ee}")
        if he == 0:
            print(export_text(t, feature_names=names, max_depth=depth))
