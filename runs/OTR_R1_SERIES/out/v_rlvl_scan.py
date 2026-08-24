"""V2 resume-level decoder — systematic mechanism x reference-level scan.

Facts driving the design (from v_rlvl_explore.py dump):
  MLK evening (2023-01-16 18:00 session): decision at 20:47 close (14713.00),
  fill 20:48 open 14712.75. BUT closes 20:36 (14712.00), 20:37 (14712.00),
  20:38 (14709.25) are all BELOW 14713.00, and closes recover to 14715-14721
  during 20:39-20:46. Therefore NO static "first close beyond L" can pick
  20:47: the mechanism needs state (an episode/latch) or a late start.

Mechanisms scanned (level L = ref + delta ticks, delta signed TOWARD the trade
side, i.e. short: L = ref + d, breach = close <= L (incl) or < L (strict);
long mirror: L = ref - d, breach = close >= L / > L):
  M1  first close beyond L (static/first-breach)                [expected fail]
  M2  first CrossBeyond (prev not beyond, now beyond)           [expected fail]
  M3  SECOND breach episode start (breach run -> recovery -> new breach run);
      a session starting already-beyond counts as episode 1 in progress
  M4  Nth close beyond L (N=2..4)
  M8  band plunge-through: prev close not-beyond U = L +/- b ticks (outside a
      band), current close beyond L (single-bar cross of the whole band)
  M9  first close beyond L with decisions starting only at session bar >= N
      (BarsRequiredToTrade-style late start) -- reported as (N range, L range)
  VWAP dynamic ref with same mechanisms.

Requirements:
  MLK  (short resume): first fire at EXACTLY 2023-01-16T20:47, none earlier.
  C104 (long analog, 01-04 evening): NO fire 18:02..21:05 (wave flips 21:06).
  C108 (long analog, 01-08 Sunday):  NO fire 18:02..02:40 (flip 02:41).
  C108s (short analog from Friday refs, for mechanisms without a
        wave-direction cancel): NO fire 18:02..02:40.
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
st, ts, tv = L["signal_trade"], L["trailing_stop"], L["trend_vector"]
TICK = 0.25

def S(x): return np.datetime_as_string(x, unit="s")

def sess_idx(prefix):
    for i in np.where(fb)[0]:
        if S(t[i]).startswith(prefix):
            return np.where(sid == sid[i])[0]
    raise KeyError(prefix)

mlk = sess_idx("2023-01-16T18:01")
c104 = sess_idx("2023-01-04T18:01")
c108 = sess_idx("2023-01-08T18:01")

def window(idx, t_end):
    """decision bars: skip first bar (B1), keep bars with time <= t_end"""
    return [i for i in idx[1:] if S(t[i]) <= t_end]

W_MLK = window(mlk, "2023-01-16T20:47:00")
W_104 = window(c104, "2023-01-04T21:05:00")
W_108 = window(c108, "2023-01-09T02:40:00")
TRIG = "2023-01-16T20:47:00"

# --- original entry prices (open of bar after last |st|==1 flip before session)
def orig_entry_before(i_first):
    flips = [j for j in range(i_first) if abs(st[j]) == 1]
    j = flips[-1]
    return o[j + 1], S(t[j]), 1 if st[j] > 0 else -1

oe_mlk, oe_mlk_t, oe_mlk_d = orig_entry_before(mlk[0])
oe_104, oe_104_t, oe_104_d = orig_entry_before(c104[0])
oe_108, oe_108_t, oe_108_d = orig_entry_before(c108[0])
print(f"orig entries: MLK {oe_mlk} (flip {oe_mlk_t} dir {oe_mlk_d}) | "
      f"C104 {oe_104} (flip {oe_104_t} dir {oe_104_d}) | C108 {oe_108} (flip {oe_108_t} dir {oe_108_d})")

# --- per-session reference values -------------------------------------------
def prior_stats(idx):
    ps = np.where(sid == sid[idx[0]] - 1)[0]
    times = [S(t[i])[11:16] for i in ps]
    cash = ps[[i >= "09:31" for i in times]]
    return {
        "prior_last_close": c[ps[-1]],
        "prior_sess_high": h[ps].max(), "prior_sess_low": lo[ps].min(),
        "prior_sess_mid": (h[ps].max() + lo[ps].min()) / 2,
        "prior_cash_high": h[cash].max(), "prior_cash_low": lo[cash].min(),
        "prior_cash_mid": (h[cash].max() + lo[cash].min()) / 2,
        "prior_cash_lastclose": c[cash[-1]],
    }

def refs_for(idx, orig_entry):
    r = prior_stats(idx)
    i0 = idx[0]
    r.update({
        "firstbar_low": lo[i0], "firstbar_high": h[i0],
        "firstbar_open": o[i0], "firstbar_close": c[i0],
        "orig_entry": orig_entry,
        "TS_at_open": ts[i0], "TV_at_open": tv[i0],
        "round100_near": None,  # handled separately
    })
    return r

R_MLK = refs_for(mlk, oe_mlk)
R_104 = refs_for(c104, oe_104)
R_108 = refs_for(c108, oe_108)
for nm, r in [("MLK", R_MLK), ("C104", R_104), ("C108", R_108)]:
    print(nm, {k: (round(val, 3) if val is not None else None) for k, val in r.items()})

# dynamic refs: TS/TV series, VWAP series (typical price and close-price)
def vwap_series(idx, mode="tpc"):
    px = (h[idx] + lo[idx] + c[idx]) / 3 if mode == "tpc" else c[idx]
    cv = np.cumsum(v[idx]); cpv = np.cumsum(px * v[idx])
    return cpv / np.maximum(cv, 1e-9)

# --- mechanism evaluators ----------------------------------------------------
def first_fire(closes, times, levels, side, mech, strict=True, nth=2, band=0):
    """levels: array same length as closes (level at each decision bar).
    side +1 long / -1 short. Returns fire time or None.
    Mechanisms: 'first', 'cross', 'episode2', 'nth', 'band'."""
    def beyond(x, Lv):
        if side < 0:
            return x < Lv if strict else x <= Lv
        return x > Lv if strict else x >= Lv
    prev_b = None
    episode = 0          # number of completed/started breach episodes
    in_breach = False
    count = 0
    for k, (x, Lv) in enumerate(zip(closes, levels)):
        b = beyond(x, Lv)
        if mech == "first":
            if b: return times[k]
        elif mech == "cross":
            if b and prev_b is False: return times[k]
        elif mech == "episode2":
            if b and not in_breach:
                episode += 1
                if episode >= 2: return times[k]
            in_breach = b
        elif mech == "nth":
            if b:
                count += 1
                if count >= nth: return times[k]
        elif mech == "band":
            if k > 0 and b:
                U = Lv + band * TICK * (1 if side < 0 else -1)
                if not beyond(closes[k - 1], U):
                    # prev close was outside the band (not beyond U)
                    if side < 0 and closes[k - 1] > U: return times[k]
                    if side > 0 and closes[k - 1] < U: return times[k]
        prev_b = b
    return None

def run_case(widx, level_arr, side, mech, strict, nth=2, band=0):
    closes = [c[i] for i in widx]
    times = [S(t[i]) for i in widx]
    return first_fire(closes, times, level_arr, side, mech, strict, nth, band)

# --- the scan ----------------------------------------------------------------
static_refs = ["prior_last_close", "prior_cash_lastclose", "orig_entry",
               "firstbar_low", "firstbar_high", "firstbar_open", "firstbar_close",
               "prior_sess_high", "prior_sess_low", "prior_sess_mid",
               "prior_cash_high", "prior_cash_low", "prior_cash_mid",
               "TS_at_open", "TV_at_open"]

mechs = [("first", None), ("cross", None), ("episode2", None),
         ("nth", 2), ("nth", 3), ("nth", 4),
         ("band", 2), ("band", 3), ("band", 4), ("band", 6), ("band", 8)]

survivors = []
firstfire_doc = {}   # (ref, delta, mech, strict) -> mlk fire time, for doc

deltas = range(-80, 81)
for ref in static_refs:
    for d in deltas:
        Lm = R_MLK[ref] + d * TICK          # short: level ABOVE ref for d>0
        lev_mlk = [Lm] * len(W_MLK)
        for mech, arg in mechs:
            for strict in (True, False):
                nth = arg if mech == "nth" else 2
                band = arg if mech == "band" else 0
                ft = run_case(W_MLK, lev_mlk, -1, mech, strict, nth, band)
                if ft != TRIG:
                    continue
                # controls: long mirror L = ref - d
                L4 = R_104[ref] - d * TICK
                L8 = R_108[ref] - d * TICK
                f4 = run_case(W_104, [L4] * len(W_104), +1, mech, strict, nth, band)
                f8 = run_case(W_108, [L8] * len(W_108), +1, mech, strict, nth, band)
                # short analog on C108 (no wave-direction cancel case)
                L8s = R_108[ref] + d * TICK
                f8s = run_case(W_108, [L8s] * len(W_108), -1, mech, strict, nth, band)
                survivors.append({
                    "ref": ref, "delta_ticks": d, "L_mlk": Lm,
                    "mech": mech + (f"({arg})" if arg else ""), "strict": strict,
                    "c104": f4 or "SILENT", "c108_long": f8 or "SILENT",
                    "c108_short": f8s or "SILENT",
                })

# VWAP dynamic
for mode in ("tpc", "close"):
    vw_mlk = vwap_series(mlk, mode)
    vw_104 = vwap_series(c104, mode)
    vw_108 = vwap_series(c108, mode)
    pos_m = {i: k for k, i in enumerate(mlk)}
    pos_4 = {i: k for k, i in enumerate(c104)}
    pos_8 = {i: k for k, i in enumerate(c108)}
    for d in deltas:
        lev_mlk = [vw_mlk[pos_m[i]] + d * TICK for i in W_MLK]
        for mech, arg in mechs:
            for strict in (True, False):
                nth = arg if mech == "nth" else 2
                band = arg if mech == "band" else 0
                ft = run_case(W_MLK, lev_mlk, -1, mech, strict, nth, band)
                if ft != TRIG:
                    continue
                l4 = [vw_104[pos_4[i]] - d * TICK for i in W_104]
                l8 = [vw_108[pos_8[i]] - d * TICK for i in W_108]
                f4 = run_case(W_104, l4, +1, mech, strict, nth, band)
                f8 = run_case(W_108, l8, +1, mech, strict, nth, band)
                survivors.append({
                    "ref": f"VWAP[{mode}]", "delta_ticks": d, "L_mlk": "dyn",
                    "mech": mech + (f"({arg})" if arg else ""), "strict": strict,
                    "c104": f4 or "SILENT", "c108_long": f8 or "SILENT",
                    "c108_short": "n/a",
                })

print(f"\n=== MLK-exact candidates found: {len(survivors)}")
for srow in survivors:
    ok = srow["c104"] == "SILENT" and srow["c108_long"] == "SILENT"
    print(("PASS " if ok else "fail ") + str(srow))

# --- documentation: where do the NAMED simple candidates first fire on MLK? --
print("\n=== named static candidates, mechanism M1 (first close beyond), MLK:")
named = {
    "prior_last_close+0": R_MLK["prior_last_close"],
    "prior_last_close+13t(3.25)": R_MLK["prior_last_close"] + 3.25,
    "cash_1300_close (=same)": R_MLK["prior_cash_lastclose"],
    "orig_entry 14708.50": R_MLK["orig_entry"],
    "orig_entry+18t(4.50)": R_MLK["orig_entry"] + 4.5,
    "firstbar_low 14715": R_MLK["firstbar_low"],
    "firstbar_low-1t": R_MLK["firstbar_low"] - 0.25,
    "firstbar_low-5t": R_MLK["firstbar_low"] - 1.25,
    "prior_cash_low 14706.50": R_MLK["prior_cash_low"],
    "prior_sess_mid 14720.50": R_MLK["prior_sess_mid"],
    "prior_cash_mid 14745.625": R_MLK["prior_cash_mid"],
    "TV_at_open 14731.25": R_MLK["TV_at_open"],
    "TS_at_open 14753.50": R_MLK["TS_at_open"],
    "round 14700": 14700.0,
    "round 14710": 14710.0,
    "round 14712.5": 14712.5,
}
for nm, Lv in named.items():
    for strict in (True, False):
        ft = run_case(W_MLK, [Lv] * len(W_MLK), -1, "first", strict)
        print(f"  {nm:32s} L={Lv:10.3f} strict={strict}  first close-beyond: {ft}")

# --- M9 late-start: what (start_bar N, L) makes FIRST close-beyond land 20:47?
print("\n=== M9 late-start (BarsRequired-style): (N, L) with first breach at 20:47")
mlk_times = [S(t[i]) for i in mlk]
sol = []
for N in range(0, 170):
    widx = [i for k, i in enumerate(mlk) if k >= N and S(t[i]) <= TRIG]
    if not widx: continue
    for d in range(int(14709 / TICK), int(14716 / TICK) + 1):
        Lv = d * TICK
        ft = run_case(widx, [Lv] * len(widx), -1, "first", True)
        if ft == TRIG:
            sol.append((N, Lv))
if sol:
    Ns = sorted(set(n for n, _ in sol))
    print(f"  start-bar N range: {Ns[0]}..{Ns[-1]} "
          f"(bar {Ns[0]} = {mlk_times[Ns[0]]}, bar {Ns[-1]} = {mlk_times[Ns[-1]]})")
    for N in (Ns[0], Ns[-1]):
        Ls = sorted(Lv for n, Lv in sol if n == N)
        print(f"    N={N}: L in [{Ls[0]}, {Ls[-1]}]")
else:
    print("  none")

# --- context: min/max closes in control windows (for the report)
print("\n=== control window extremes:")
print(f"  C104 closes 18:02..21:05: min={min(c[i] for i in W_104)} max={max(c[i] for i in W_104)}  "
      f"prior_last_close={R_104['prior_last_close']}")
print(f"  C108 closes 18:02..02:40: min={min(c[i] for i in W_108)} max={max(c[i] for i in W_108)}  "
      f"prior_last_close={R_108['prior_last_close']}")
