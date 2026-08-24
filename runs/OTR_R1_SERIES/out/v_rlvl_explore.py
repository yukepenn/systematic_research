"""V2 resume-level decoder — exploration dump.

Dump the three evenings of interest with full bar detail so candidate
reference levels can be computed exactly:
  - 2023-01-16 18:00 ET evening (MLK early-close resume SHORT filled 20:48 @14712.75)
  - 2023-01-08 18:00 ET Sunday evening (control: NO resume; wave long since 18:01)
  - 2023-01-04 18:00 ET evening (control: NO resume; prior position long, flip 21:06)
Plus prior-session stats (last bar close, session high/low, cash 09:30-13:00 or
09:30-16:00 high/low/mid, last close) needed for the candidate levels.
"""
import sys, os
import numpy as np

SRC = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\research\original_trader_reconstruction\solar_family\src"
sys.path.insert(0, SRC)
from otr_engine import load_ledger

LEDGER = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\research\03_reverse_engineering\ledgers\t2_canonical_1m.csv"

L = load_ledger(LEDGER)
t = L["time"]
o, h, lo, c, v = L["open"], L["high"], L["low"], L["close"], L["volume"]
fb, lb, sid = L["first_bar"], L["last_bar"], L["session_id"]
st, wave, ts, tv, strend = L["signal_trade"], L["signal_wave"], L["trailing_stop"], L["trend_vector"], L["signal_trend"]

def s(ts64):
    return np.datetime_as_string(ts64, unit="s")

def session_index_of_first_bar(date_hhmm):
    """Return session id of the session whose first bar time string startswith date_hhmm."""
    idxs = np.where(fb)[0]
    for i in idxs:
        if s(t[i]).startswith(date_hhmm):
            return sid[i], i
    return None, None

def dump_session(first_bar_prefix, tmin=None, tmax=None, label=""):
    sidv, i0 = session_index_of_first_bar(first_bar_prefix)
    mask = sid == sidv
    idx = np.where(mask)[0]
    print(f"\n===== {label} session id={sidv}: {s(t[idx[0]])} .. {s(t[idx[-1]])}  nbars={len(idx)}")
    for i in idx:
        tim = s(t[i])
        hhmm = tim[11:16]
        if tmin is not None and (tim < tmin or tim > tmax):
            continue
        print(f"{tim} O={o[i]:9.2f} H={h[i]:9.2f} L={lo[i]:9.2f} C={c[i]:9.2f} V={v[i]:7.0f} st={st[i]:2d} wave={wave[i]:2d} tr={strend[i]:2d} TS={ts[i]:9.2f} TV={tv[i]:9.2f}{' FB' if fb[i] else ''}{' LB' if lb[i] else ''}")
    return sidv, idx

def prior_session_stats(sidv):
    mask = sid == sidv
    idx = np.where(mask)[0]
    print(f"\n--- prior session id={sidv}: {s(t[idx[0]])} .. {s(t[idx[-1]])} nbars={len(idx)}")
    print(f"  last bar: {s(t[idx[-1]])} O={o[idx[-1]]} H={h[idx[-1]]} L={lo[idx[-1]]} C={c[idx[-1]]}")
    print(f"  session HIGH={h[idx].max()} LOW={lo[idx].min()} MID={(h[idx].max()+lo[idx].min())/2}")
    # cash session 09:30 -> end (day part)
    times = [s(t[i])[11:16] for i in idx]
    cash = [i for i, tm in zip(idx, times) if tm >= "09:31"]  # bars stamped at close
    if cash:
        ca = np.array(cash)
        print(f"  cash(>=09:31) HIGH={h[ca].max()} LOW={lo[ca].min()} MID={(h[ca].max()+lo[ca].min())/2} lastC={c[ca[-1]]} firstO={o[ca[0]]}")
    # day part (everything after 08:00)
    day = [i for i, tm in zip(idx, times) if tm >= "08:01" and tm <= "17:00"]
    if day:
        da = np.array(day)
        print(f"  day(08:01-17:00) HIGH={h[da].max()} LOW={lo[da].min()} MID={(h[da].max()+lo[da].min())/2}")
    return idx

# ---- MLK evening
sid_mlk, idx_mlk = dump_session("2023-01-16T18:01", "2023-01-16T18:00", "2023-01-16T21:10", "MLK evening (resume)")
# also dump around exit next morning
print("\n(exit window 07:15-07:25)")
for i in idx_mlk:
    tim = s(t[i])
    if "2023-01-17T07:15" <= tim <= "2023-01-17T07:25":
        print(f"{tim} O={o[i]} H={h[i]} L={lo[i]} C={c[i]} TS={ts[i]} TV={tv[i]} wave={wave[i]}")
prior_session_stats(sid_mlk - 1)

# session-min running close before 20:47 on MLK evening
print("\nMLK evening: closes chronology 18:01-20:48 (min tracking)")
mn = None
for i in idx_mlk:
    tim = s(t[i])
    if tim > "2023-01-16T20:48":
        break
    mn = c[i] if mn is None else min(mn, c[i])
print(f"  min close over 18:01..20:46 window computed separately below")
mn2 = None
for i in idx_mlk:
    tim = s(t[i])
    if tim >= "2023-01-16T20:47":
        break
    mn2 = c[i] if mn2 is None else min(mn2, c[i])
print(f"  min close 18:01..20:46 = {mn2}")
mn3 = None
for i in idx_mlk:
    tim = s(t[i])
    if tim >= "2023-01-16T20:47":
        break
    mn3 = lo[i] if mn3 is None else min(mn3, lo[i])
print(f"  min LOW  18:01..20:46 = {mn3}")

# ---- control 1: 01-08 Sunday evening
sid_c1, idx_c1 = dump_session("2023-01-08T18:01", "2023-01-08T18:00", "2023-01-08T19:00", "01-08 Sunday evening (control)")
prior_session_stats(sid_c1 - 1)
# closes max before 02:41 flip
mx = None; mxlo=None
for i in idx_c1:
    tim = s(t[i])
    if tim >= "2023-01-09T02:41":
        break
    mx = c[i] if mx is None else max(mx, c[i])
    mxlo = h[i] if mxlo is None else max(mxlo, h[i])
print(f"  01-08 evening: max close 18:01..02:40 = {mx}, max high = {mxlo}")
# wave states early
print("  wave at first bars:", [(s(t[i])[11:16], wave[i], st[i]) for i in idx_c1[:5]])

# ---- control 2: 01-04 evening
sid_c2, idx_c2 = dump_session("2023-01-04T18:01", "2023-01-04T18:00", "2023-01-04T19:00", "01-04 evening (control)")
prior_session_stats(sid_c2 - 1)
mx = None; mxh=None
for i in idx_c2:
    tim = s(t[i])
    if tim >= "2023-01-04T21:06":
        break
    mx = c[i] if mx is None else max(mx, c[i])
    mxh = h[i] if mxh is None else max(mxh, h[i])
print(f"  01-04 evening: max close 18:01..21:05 = {mx}, max high = {mxh}")
print("  wave/st around 21:00-21:10:", [(s(t[i])[11:16], wave[i], st[i]) for i in idx_c2 if "2023-01-04T21:00" <= s(t[i]) <= "2023-01-04T21:10"])
