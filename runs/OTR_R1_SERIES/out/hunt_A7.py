"""FAMILY A hunt, step 7: A3/A4/A5 role-swap scan.

Recompute weak/wave/T3 layer and T2 layer under permuted (slowdown_scan, weak_weak_split,
pullback_split) assignments of (5,10,10); flips unchanged. Scan simple gates from these
streams for HARD-label separation.
"""
import sys, csv, itertools
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
tstr = np.array([str(t) for t in bars["time"]])
idx_of = {s: i for i, s in enumerate(tstr)}

rows = list(csv.DictReader(open(FEAT, newline="")))
S = np.array([idx_of[r["entry_time"]] - 1 for r in rows])
D = np.array([1 if r["dir"] == "L" else -1 for r in rows])
LAB = np.array([1 if r["label"] == "TAKE" else 0 for r in rows])
CERT = np.array([r["certainty"] for r in rows])
ET = np.array([r["entry_time"] for r in rows])
hard = CERT == "HARD"

def scan(x, name):
    """x: value per label; test all threshold/sense gates; return best hard errors."""
    out = []
    xs = np.unique(x[hard])
    thr = np.concatenate([[xs[0] - 0.5], (xs[:-1] + xs[1:]) / 2.0, [xs[-1] + 0.5]]) if len(xs) > 1 else [xs[0] - 0.5, xs[0] + 0.5]
    best = (99, None)
    for th in thr:
        for sense in (1, -1):
            pred = (sense * (x - th)) > 0
            nerr = int((pred[hard] != (LAB[hard] == 1)).sum())
            if nerr < best[0]:
                miss = list(ET[hard][pred[hard] != (LAB[hard] == 1)])
                best = (nerr, (name, sense, float(th), miss))
    return best

results = []
for ss, wws, ps in set(itertools.permutations([5, 10, 10])) | {(5, 5, 10), (10, 10, 10), (5, 10, 5)}:
    for pe in (False, True):
        p = SolarWaveParams(slowdown_scan=ss, weak_weak_split=wws, pullback_split=ps, pullback_early=pe)
        r = solar_wave_full(o, h, l, c, p, start_up=False)
        strend = r.signal_trend
        swave = r.signal_wave
        st = r.signal_trade
        fire = np.abs(st) == 2
        t3 = np.abs(st) == 3
        flip = np.abs(st) == 1
        # per-bar last fire / last t3
        last_fire = np.full(n, -10**9); last_t3 = np.full(n, -10**9)
        lf = lt = -10**9
        for t in range(n):
            if fire[t]: lf = t
            if t3[t]: lt = t
            last_fire[t] = lf; last_t3[t] = lt
        leg_id = np.cumsum(flip)
        leg_fire = np.zeros(int(leg_id[-1]) + 2, np.int64)
        for t in np.where(fire)[0]:
            leg_fire[leg_id[t]] += 1
        tag = f"ss{ss}_wws{wws}_ps{ps}_pe{int(pe)}"
        cand = {
            "weak_prev": np.abs(strend[S - 1]).astype(float),
            "wave_prev": np.abs(swave[S - 1]).astype(float),
            "bars_since_fire": (S - last_fire[S]).astype(float),
            "bars_since_t3": (S - last_t3[S]).astype(float),
            "fires_prev_leg": leg_fire[leg_id[S] - 1].astype(float),
        }
        for nm, x in cand.items():
            nerr, info = scan(np.clip(x, -1e6, 1e6), f"{tag}:{nm}")
            results.append((nerr, info))

results.sort(key=lambda r: r[0])
for nerr, info in results[:25]:
    print(f"err={nerr}  {info[0]:>40} sense={info[1]:+d} thr={info[2]:.2f} miss={info[3]}")
