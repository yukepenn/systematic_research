"""V2 resume-level decoder — fire-frequency audit of the surviving candidates.

For every session in the sample where the wave direction at the session open
persists from the prior session (resume-armed state), simulate each surviving
mechanism from bar 2 (B1) until the first |signal_trade|==1 flip inside the
session (after which the T1 chain governs), and count fires. A genuine resume
rule must be RARE (we know of exactly one: MLK 20:47) — a mechanism that fires
dozens of times cannot be the trader's, since the target has FEWER trades
(4351) than the no-resume INT model (5011).

Also verifies the C104 near-miss path (dip to 14108.25 without re-crossing).
"""
import sys
import numpy as np

SRC = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\research\original_trader_reconstruction\solar_family\src"
sys.path.insert(0, SRC)
from otr_engine import load_ledger

LEDGER = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\research\03_reverse_engineering\ledgers\t2_canonical_1m.csv"
L = load_ledger(LEDGER)
t, o, h, lo, c, v = L["time"], L["open"], L["high"], L["low"], L["close"], L["volume"]
fb, sid = L["first_bar"], L["session_id"]
st = L["signal_trade"]
wave = L["signal_wave"]
TICK = 0.25
def S(x): return np.datetime_as_string(x, unit="s")

n_sess = sid[-1] + 1
sess_bars = [np.where(sid == k)[0] for k in range(n_sess)]

# per-session refs
def prior_refs(k):
    ps = sess_bars[k - 1]
    times = [S(t[i])[11:16] for i in ps]
    cash = ps[[x >= "09:31" for x in times]]
    r = {"prior_last_close": c[ps[-1]],
         "prior_sess_mid": (h[ps].max() + lo[ps].min()) / 2}
    if len(cash):
        r["prior_cash_low"] = lo[cash].min()
        r["prior_cash_high"] = h[cash].max()
    else:
        r["prior_cash_low"] = lo[ps].min()
        r["prior_cash_high"] = h[ps].max()
    return r

def orig_entry_before(i_first):
    flips = np.where(np.abs(st[:i_first]) == 1)[0]
    if len(flips) == 0: return None
    j = flips[-1]
    if j + 1 >= i_first: return None   # flip on last prior bar; entry = first bar open
    return o[j + 1]

def episode2_fire(closes, times, Lv, side, strict=True):
    in_breach = False; episode = 0
    for k, x in enumerate(closes):
        if side < 0:
            b = x < Lv if strict else x <= Lv
        else:
            b = x > Lv if strict else x >= Lv
        if b and not in_breach:
            episode += 1
            if episode >= 2: return times[k]
        in_breach = b
    return None

def band_fire(closes, times, Lv, side, bandticks, strict=True):
    for k in range(1, len(closes)):
        x = closes[k]
        if side < 0:
            b = x < Lv if strict else x <= Lv
            if b and closes[k - 1] > Lv + bandticks * TICK: return times[k]
        else:
            b = x > Lv if strict else x >= Lv
            if b and closes[k - 1] < Lv - bandticks * TICK: return times[k]
    return None

cands = [
    ("episode2 orig_entry+19t",     "orig_entry",       19, "episode2", None),
    ("episode2 orig_entry+20t",     "orig_entry",       20, "episode2", None),
    ("episode2 prior_cash_low+27t", "prior_cash_low",   27, "episode2", None),
    ("episode2 prior_sess_mid-29t", "prior_sess_mid",  -29, "episode2", None),
    ("episode2 prior_last_close+13t","prior_last_close",13, "episode2", None),  # C104-fail, for reference
    ("band3 prior_last_close+13t",  "prior_last_close", 13, "band", 3),
    ("band3 orig_entry+19t",        "orig_entry",       19, "band", 3),
]

results = {nm: [] for nm, *_ in cands}
armed_sessions = 0
for k in range(1, n_sess):
    idx = sess_bars[k]
    if len(idx) < 10: continue
    ps = sess_bars[k - 1]
    dir_open = 1 if wave[idx[0]] > 0 else -1
    dir_prior = 1 if wave[ps[-1]] > 0 else -1
    # armed: wave persisted across the boundary AND no flip on the first bar
    if dir_open != dir_prior or abs(st[idx[0]]) == 1:
        continue
    armed_sessions += 1
    # simulate until first flip in session (exclusive), from bar 2
    flips = [j for j in idx[1:] if abs(st[j]) == 1]
    stop_i = flips[0] if flips else idx[-1]
    widx = [j for j in idx[1:] if j < stop_i]
    if not widx: continue
    closes = [c[j] for j in widx]; times = [S(t[j]) for j in widx]
    refs = prior_refs(k)
    refs["orig_entry"] = orig_entry_before(idx[0])
    side = dir_prior   # resume in the prior direction
    for nm, ref, d, mech, barg in cands:
        rv = refs.get(ref)
        if rv is None: continue
        # level displaced toward the trade side by d ticks:
        # short: L = ref + d ; long: L = ref - d   (mirror used in the scan)
        Lv = rv + d * TICK if side < 0 else rv - d * TICK
        if mech == "episode2":
            ft = episode2_fire(closes, times, Lv, side, strict=True)
        else:
            ft = band_fire(closes, times, Lv, side, barg, strict=True)
        if ft: results[nm].append(ft)

print(f"sessions total={n_sess}, resume-armed (wave persisted, no first-bar flip)={armed_sessions}\n")
for nm, *_ in cands:
    r = results[nm]
    mlk_hit = any(x.startswith("2023-01-16T20:47") for x in r)
    print(f"{nm:34s} fires={len(r):4d}  MLK-20:47-included={mlk_hit}")
    for x in r[:8]:
        print(f"    {x}")
    if len(r) > 8: print(f"    ... ({len(r)-8} more)")

# --- verify the C104 near-miss for orig_entry mirror (L=14119.25) ------------
print("\nC104 verification (orig_entry mirror L=14124.00-4.75=14119.25):")
idx = None
for i in np.where(fb)[0]:
    if S(t[i]).startswith("2023-01-04T18:01"):
        idx = np.where(sid == sid[i])[0]; break
w = [i for i in idx[1:] if S(t[i]) <= "2023-01-04T21:05:00"]
below = [(S(t[i]), c[i]) for i in w if c[i] <= 14119.25]
print(f"  closes <= 14119.25 in 18:02..21:05: {len(below)}; first={below[0] if below else None} last={below[-1] if below else None}")
after_first_below = False; recross = None
for i in w:
    if c[i] <= 14119.25: after_first_below = True
    elif after_first_below and c[i] > 14119.25:
        recross = (S(t[i]), c[i]); break
print(f"  re-cross above 14119.25 before 21:06: {recross}")
lowwin = [(S(t[i]), c[i]) for i in w if S(t[i]) >= "2023-01-04T19:50:00"]
print("  path 19:50..21:05 every 5th bar:")
for row in lowwin[::5]:
    print(f"    {row[0]} close={row[1]}")
