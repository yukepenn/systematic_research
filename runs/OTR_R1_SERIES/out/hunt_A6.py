"""FAMILY A hunt, step 6: price-level context dump for every labeled event."""
import sys, csv
import numpy as np

sys.path.insert(0, r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\research\original_trader_reconstruction\solar_family\src")
from otr_engine import load_ledger

LEDGER = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\research\03_reverse_engineering\ledgers\t2_canonical_1m.csv"
FEAT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\runs\OTR_R1_SERIES\out\r12f_flip_features.csv"

bars = load_ledger(LEDGER)
n = bars["n"]
o, h, l, c = bars["open"], bars["high"], bars["low"], bars["close"]
time_arr = bars["time"]
first_bar = bars["first_bar"]
tstr = np.array([str(t) for t in time_arr])
idx_of = {s: i for i, s in enumerate(tstr)}
mod = (time_arr - time_arr.astype("datetime64[D]")).astype("timedelta64[s]").astype(np.int64) // 60

sess_open = np.zeros(n); sess_hi = np.zeros(n); sess_lo = np.zeros(n)
prev_hi = np.zeros(n); prev_lo = np.zeros(n); prev_cl = np.zeros(n)
rth_open = np.zeros(n)  # 09:30 open of current session (nan before)
cur_o = np.nan; cur_h = -np.inf; cur_l = np.inf
p_h = np.nan; p_l = np.nan; p_c = np.nan
last_c = np.nan; cur_rth = np.nan
for t in range(n):
    if first_bar[t]:
        p_h, p_l, p_c = cur_h, cur_l, last_c
        cur_o = o[t]; cur_h = -np.inf; cur_l = np.inf; cur_rth = np.nan
    if mod[t] == 571 and np.isnan(cur_rth):  # bar ending 09:31 -> open at 09:30
        cur_rth = o[t]
    cur_h = max(cur_h, h[t]); cur_l = min(cur_l, l[t])
    sess_open[t] = cur_o; sess_hi[t] = cur_h; sess_lo[t] = cur_l
    prev_hi[t] = p_h; prev_lo[t] = p_l; prev_cl[t] = p_c
    rth_open[t] = cur_rth
    last_c = c[t]

rows = list(csv.DictReader(open(FEAT, newline="")))
print(f"{'entry_time':<20}{'cert':>5}{'lab':>5} d {'close':>9}{'sopen':>9}{'shi':>9}{'slo':>9}"
      f"{'rthO':>9}{'pHi':>9}{'pLo':>9}{'pCl':>9}")
for r in rows:
    s = idx_of[r["entry_time"]] - 1
    print(f"{r['entry_time']:<20}{r['certainty']:>5}{r['label']:>5} {r['dir']} {c[s]:>9.2f}{sess_open[s]:>9.2f}"
          f"{sess_hi[s]:>9.2f}{sess_lo[s]:>9.2f}{rth_open[s]:>9.2f}{prev_hi[s]:>9.2f}{prev_lo[s]:>9.2f}{prev_cl[s]:>9.2f}")
