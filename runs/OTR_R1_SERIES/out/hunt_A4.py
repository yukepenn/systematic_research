"""FAMILY A hunt, step 4: near-miss analysis of single-feature rules + volume features."""
import sys, csv
import numpy as np

sys.path.insert(0, r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\research\original_trader_reconstruction\solar_family\src")
sys.path.insert(0, r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\src\analytics")

from otr_engine import load_ledger
from solarwave import solar_wave, SolarWaveParams

LEDGER = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\research\03_reverse_engineering\ledgers\t2_canonical_1m.csv"
FEAT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\runs\OTR_R1_SERIES\out\r12f_flip_features.csv"

bars = load_ledger(LEDGER)
n = bars["n"]
o, h, l, c, v = bars["open"], bars["high"], bars["low"], bars["close"], bars["volume"]
time_arr = bars["time"]
sess_id = bars["session_id"]
first_bar = bars["first_bar"]
tstr = np.array([str(t) for t in time_arr])
idx_of = {s: i for i, s in enumerate(tstr)}
mod = (time_arr - time_arr.astype("datetime64[D]")).astype("timedelta64[s]").astype(np.int64) // 60

F = {}
base = solar_wave(c, SolarWaveParams(), start_up=False)

def ema(x, span):
    a = 2.0 / (span + 1.0)
    out = np.empty_like(x, dtype=float)
    out[0] = x[0]
    for i in range(1, len(x)):
        out[i] = out[i - 1] + a * (x[i] - out[i - 1])
    return out

# volume features
F["vol"] = v.astype(float)
for N in (14, 60, 240):
    F[f"vol_ema{N}"] = ema(v, N)
F["vol_rel60"] = v / np.maximum(ema(v, 60), 1.0)

# scaled ladders again (for reference in near-miss listing)
for k in (2.0, 3.0, 4.0):
    p = SolarWaveParams(offset_multiplier_trend=90 * k, offset_multiplier_stop=179 * k)
    r = solar_wave(c, p, start_up=False)
    F[f"L1m_x{k}_up"] = np.where(r.is_up, 1.0, -1.0)
    F[f"L1m_x{k}_c_tv"] = c - r.trend_vector

for N in (100, 200, 500, 1000, 2000):
    F[f"c_ema{N}"] = c - ema(c, N)
for N in (60, 120, 240, 480):
    m_ = np.empty(n); m_[:N] = 0.0; m_[N:] = c[N:] - c[:-N]
    F[f"mom{N}"] = m_

rows = list(csv.DictReader(open(FEAT, newline="")))
S = []; D = []; LAB = []; CERT = []; ET = []
for r in rows:
    i_fill = idx_of[r["entry_time"]]
    S.append(i_fill - 1)
    D.append(1 if r["dir"] == "L" else -1)
    LAB.append(1 if r["label"] == "TAKE" else 0)
    CERT.append(r["certainty"]); ET.append(r["entry_time"])
S = np.array(S); D = np.array(D); LAB = np.array(LAB); CERT = np.array(CERT); ET = np.array(ET)
hard = CERT == "HARD"

best = []
for name, arr in F.items():
    fv = arr[S]
    for mode, x in (("signed", fv * D), ("raw", fv.astype(float)), ("abs", np.abs(fv.astype(float)))):
        xs = np.unique(x[hard])
        if len(xs) < 2:
            continue
        thr = np.concatenate([[xs[0] - 1], (xs[:-1] + xs[1:]) / 2.0, [xs[-1] + 1]])
        for th in thr:
            for sense in (1, -1):
                pred = (sense * (x - th)) > 0
                nerr = int((pred[hard] != (LAB[hard] == 1)).sum())
                best.append((nerr, name, mode, sense, float(th),
                             tuple(ET[hard][pred[hard] != (LAB[hard] == 1)])))
best.sort(key=lambda r: r[0])
seen = set()
print("near-misses (per feature/mode best):")
for b in best:
    key = (b[1], b[2])
    if key in seen:
        continue
    seen.add(key)
    if b[0] <= 3:
        print(f"  err={b[0]}  {b[1]:>14} {b[2]:>7} sense={b[3]:+d} thr={b[4]:.3f}  miss={list(b[5])}")
