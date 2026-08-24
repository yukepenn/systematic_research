"""V2 resume-level decoder — early-close scoping and per-candidate predictions.

The frequency audit showed every surviving level+latch fires 43..291 times if a
resume is armed on every wave-persisting session — impossible given the target
has FEWER trades (4351) than the no-resume INT model (5011). The natural rare
arming event is exactly what makes MLK unique: the prior session ENDED EARLY
(13:00 holiday close). This script:
  1. enumerates every early-close session in the sample,
  2. for the evening after each, runs the surviving candidates and prints the
     predicted resume fire time (or SILENT) -> discriminating predictions that
     can be checked against the trader's per-day table,
  3. prints wave persistence info for each such evening.
"""
import sys
import numpy as np

SRC = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\research\original_trader_reconstruction\solar_family\src"
sys.path.insert(0, SRC)
from otr_engine import load_ledger

LEDGER = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\research\03_reverse_engineering\ledgers\t2_canonical_1m.csv"
L = load_ledger(LEDGER)
t, o, h, lo, c = L["time"], L["open"], L["high"], L["low"], L["close"]
fb, sid = L["first_bar"], L["session_id"]
st, wave = L["signal_trade"], L["signal_wave"]
TICK = 0.25
def S(x): return np.datetime_as_string(x, unit="s")

n_sess = sid[-1] + 1
sess_bars = [np.where(sid == k)[0] for k in range(n_sess)]

def episode2_fire(closes, times, Lv, side, strict=True):
    in_breach = False; episode = 0
    for k, x in enumerate(closes):
        b = (x < Lv if strict else x <= Lv) if side < 0 else (x > Lv if strict else x >= Lv)
        if b and not in_breach:
            episode += 1
            if episode >= 2: return times[k]
        in_breach = b
    return None

def first_fire(closes, times, Lv, side, strict=True):
    for k, x in enumerate(closes):
        b = (x < Lv if strict else x <= Lv) if side < 0 else (x > Lv if strict else x >= Lv)
        if b: return times[k]
    return None

def orig_entry_before(i_first):
    flips = np.where(np.abs(st[:i_first]) == 1)[0]
    if len(flips) == 0 or flips[-1] + 1 >= i_first: return None
    return o[flips[-1] + 1]

# 1. early-close sessions: last bar stamped before 16:30 (normal = 17:00)
early = []
for k in range(n_sess):
    last = sess_bars[k][-1]
    hhmm = S(t[last])[11:16]
    if hhmm < "16:30":
        early.append((k, S(t[last])))
print(f"early-close sessions (last bar < 16:30): {len(early)}")
for k, tm in early:
    print(f"  session {k}: ends {tm}")

# 2. predictions on each following evening
cand_refs = [
    ("orig_entry", (18, 19, 20, 21)),
    ("prior_cash_low", (26, 27, 28, 29)),
    ("prior_sess_mid", (-30, -29, -28, -27)),
    ("prior_last_close", (12, 13, 14, 15)),
]
print("\n=== per-evening predictions (episode2 latch, strict close-beyond; delta toward trade side) ===")
for k, tm in early:
    if k + 1 >= n_sess: break
    idx = sess_bars[k + 1]
    ps = sess_bars[k]
    dir_prior = 1 if wave[ps[-1]] > 0 else -1
    dir_open = 1 if wave[idx[0]] > 0 else -1
    flip_first = abs(st[idx[0]]) == 1
    flips = [j for j in idx[1:] if abs(st[j]) == 1]
    stop_i = flips[0] if flips else idx[-1] + 1
    widx = [j for j in idx[1:] if j < stop_i]
    closes = [c[j] for j in widx]; times = [S(t[j]) for j in widx]
    times_hm = [x[11:16] for x in times]
    ref_vals = {}
    p_times = [S(t[i])[11:16] for i in ps]
    cash = ps[[x >= "09:31" for x in p_times]]
    ref_vals["prior_last_close"] = c[ps[-1]]
    ref_vals["prior_cash_low"] = lo[cash].min() if len(cash) else lo[ps].min()
    ref_vals["prior_sess_mid"] = (h[ps].max() + lo[ps].min()) / 2
    ref_vals["orig_entry"] = orig_entry_before(idx[0])
    print(f"\nevening after early close {tm}  (session {k+1}: {S(t[idx[0]])}) "
          f"prior_dir={'L' if dir_prior>0 else 'S'} open_dir={'L' if dir_open>0 else 'S'} "
          f"flip_on_first_bar={flip_first} first_flip_in_session={S(t[flips[0]]) if flips else 'none'}")
    if dir_open != dir_prior or flip_first:
        print("  [resume disarmed: wave flipped at/before evening open]")
        continue
    side = dir_prior
    for ref, ds in cand_refs:
        rv = ref_vals.get(ref)
        if rv is None:
            print(f"  {ref}: ref undefined"); continue
        outs = []
        for d in ds:
            Lv = rv + d * TICK if side < 0 else rv - d * TICK
            ft = episode2_fire(closes, times, Lv, side)
            outs.append(f"d={d}t L={Lv:.2f} -> {ft[11:16] if ft else 'SILENT'}")
        print(f"  {ref} ({rv}): " + " | ".join(outs))
