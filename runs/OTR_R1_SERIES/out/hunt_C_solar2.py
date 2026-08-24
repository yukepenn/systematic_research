"""Family C pass 7: second Solar ladder (stop multiplier S2) as direction gate.

Gate: entry dir d at signal bar j allowed iff sign(solar2.is_up[j]) == d
(variants: at j-1; or must DISAGREE). Scan S2 over a grid of tick offsets.
Score vs 8 HARD skips / 112 takes.
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
n = bars["n"]
c = bars["close"]

sl = jan_slice(bars)
trades = base_trades(sl)
lab = pd.read_csv(FEAT)[["entry_time", "label", "certainty"]]
lmap = dict(zip(lab.entry_time, zip(lab.label, lab.certainty)))
J = [(t["entry_i"] - 1, 1 if t["dir"] > 0 else -1, *lmap[t["entry_time"]], t["entry_time"])
     for t in trades]
hard_or_take = [(j, d, lb) for j, d, lb, ct, et in J if lb == "TAKE" or ct == "HARD"]


def ladder_dir(S_pts):
    """core close ladder direction per bar (start_up=False)."""
    is_up = False
    anchor = c[0]
    out = np.empty(n, dtype=np.int8)
    for t in range(n):
        px = c[t]
        if t > 0:
            if is_up:
                if px >= anchor:
                    anchor = px
                elif px < anchor - S_pts:
                    is_up, anchor = False, px
            else:
                if px <= anchor:
                    anchor = px
                elif px > anchor + S_pts:
                    is_up, anchor = True, px
        out[t] = 1 if is_up else -1
    return out

print(f"{'S2_ticks':>8} {'variant':>10} {'skipOK/8':>8} {'takeOK/112':>10}")
best = []
for s2t in (30, 45, 60, 70, 80, 90, 100, 110, 120, 135, 150, 160, 170, 190, 200,
            220, 240, 260, 280, 300, 330, 358, 400, 450, 500, 600, 716):
    d2 = ladder_dir(s2t * 0.25)
    for lagname, lag in (("at_j", 0), ("at_j-1", 1)):
        for mode in ("agree", "disagree"):
            sok = tok = 0
            for j, d, lb in hard_or_take:
                a = d2[j - lag] == d
                allowed = a if mode == "agree" else (not a)
                if lb == "TAKE":
                    tok += allowed
                else:
                    sok += (not allowed)
            best.append((sok + tok, s2t, lagname, mode, sok, tok))
            if sok >= 5 or (sok + tok) >= 116:
                print(f"{s2t:>8} {lagname+'/'+mode:>10} {sok:>8} {tok:>10}")

best.sort(reverse=True)
print("\ntop 12 overall:")
for tot, s2t, lagname, mode, sok, tok in best[:12]:
    print(f"  S2={s2t} {lagname} {mode}: skips {sok}/8, takes {tok}/112, total {tot}/120")
