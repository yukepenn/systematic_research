"""FAMILY A hunt, step 3: wide deterministic feature bank + single-feature threshold scan.

Gate model: entry at flip (dir d) allowed iff RULE(features at signal bar s, d).
Scan rules of forms:
  (i)  allow iff f_signed > theta   where f_signed = f * d (direction-conditioned)
  (ii) allow iff f_signed < theta
  (iii) allow iff f_raw > theta / < theta (direction-neutral)
Pass = all HARD labels correct. Report EPS/SOFT agreement for passing rules.
"""
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
o, h, l, c = bars["open"], bars["high"], bars["low"], bars["close"]
time_arr = bars["time"]
sess_id = bars["session_id"]
first_bar = bars["first_bar"]
tstr = np.array([str(t) for t in time_arr])
idx_of = {s: i for i, s in enumerate(tstr)}
mod = (time_arr - time_arr.astype("datetime64[D]")).astype("timedelta64[s]").astype(np.int64) // 60

# ---------- feature bank (per 1-min bar) ----------
F = {}  # name -> array

# core ladder (1-min) for reference distances
base = solar_wave(c, SolarWaveParams(), start_up=False)
F["c_minus_anchor"] = c - base.anchor
F["ladder_up"] = np.where(base.is_up, 1.0, -1.0)

# scaled 1-min ladders (slower trend gates)
for k in (1.5, 2.0, 3.0, 4.0, 6.0):
    p = SolarWaveParams(offset_multiplier_trend=90 * k, offset_multiplier_stop=179 * k)
    r = solar_wave(c, p, start_up=False)
    tag = f"L1m_x{k}"
    F[f"{tag}_up"] = np.where(r.is_up, 1.0, -1.0)
    F[f"{tag}_c_tv"] = c - r.trend_vector
    F[f"{tag}_c_ts"] = c - r.trailing_stop
    F[f"{tag}_weak"] = np.abs(r.signal_trend).astype(float)  # 1 weak, 2 strong
    F[f"{tag}_strend"] = r.signal_trend.astype(float)

# HTF resampled ladders: m-minute session-aligned groups, state = last completed group
def htf_ladder(m, om_t=90.0, om_s=179.0):
    # group id per bar
    mins_in_sess = np.zeros(n, np.int64)
    cur0 = 0
    for t in range(n):
        if first_bar[t]:
            cur0 = t
        mins_in_sess[t] = t - cur0
    grp = mins_in_sess // m
    # group close bars: last bar of each (session, grp)
    is_last_of_grp = np.zeros(n, bool)
    for t in range(n - 1):
        if sess_id[t + 1] != sess_id[t] or grp[t + 1] != grp[t]:
            is_last_of_grp[t] = True
    is_last_of_grp[-1] = True
    gc_idx = np.where(is_last_of_grp)[0]
    gclose = c[gc_idx]
    r = solar_wave(gclose, SolarWaveParams(offset_multiplier_trend=om_t, offset_multiplier_stop=om_s), start_up=False)
    # per 1-min bar: index of last completed group (searchsorted)
    # completed at bar t means gc_idx <= t  -> state index = count-1
    pos = np.searchsorted(gc_idx, np.arange(n), side="right") - 1
    up = np.where(pos >= 0, np.where(r.is_up[np.clip(pos, 0, None)], 1.0, -1.0), 0.0)
    tv = np.where(pos >= 0, r.trend_vector[np.clip(pos, 0, None)], np.nan)
    ts_ = np.where(pos >= 0, r.trailing_stop[np.clip(pos, 0, None)], np.nan)
    stw = np.where(pos >= 0, r.signal_trend[np.clip(pos, 0, None)], 0)
    return up, tv, ts_, stw

for m in (2, 3, 5, 10, 15, 30, 60):
    up, tv2, ts2, stw = htf_ladder(m)
    tag = f"HTF{m}"
    F[f"{tag}_up"] = up
    F[f"{tag}_c_tv"] = c - tv2
    F[f"{tag}_c_ts"] = c - ts2
    F[f"{tag}_strend"] = stw.astype(float)
    F[f"{tag}_weak"] = np.abs(stw).astype(float)

# EMAs / SMAs
def ema(x, span):
    a = 2.0 / (span + 1.0)
    out = np.empty_like(x)
    out[0] = x[0]
    for i in range(1, len(x)):
        out[i] = out[i - 1] + a * (x[i] - out[i - 1])
    return out

for N in (20, 50, 100, 200, 500, 1000):
    F[f"c_ema{N}"] = c - ema(c, N)

for N in (20, 50, 100, 200):
    sma = np.convolve(c, np.ones(N) / N, mode="full")[:n]
    sma[:N] = c[:N]
    F[f"c_sma{N}"] = c - sma

# momentum
for N in (5, 15, 30, 60, 120, 240):
    m_ = np.empty(n)
    m_[:N] = 0.0
    m_[N:] = c[N:] - c[:-N]
    F[f"mom{N}"] = m_

# RSI(14) on 1-min
def rsi(x, per=14):
    d = np.diff(x, prepend=x[0])
    up = np.clip(d, 0, None)
    dn = np.clip(-d, 0, None)
    ru = ema(up, 2 * per - 1)
    rd = ema(dn, 2 * per - 1)
    return 100.0 - 100.0 / (1.0 + ru / np.maximum(rd, 1e-9))

F["rsi14"] = rsi(c) - 50.0
F["rsi14_60"] = rsi(c, 60) - 50.0

# ATR-ish rolling range (points)
tr = np.maximum(h - l, np.maximum(np.abs(h - np.roll(c, 1)), np.abs(l - np.roll(c, 1))))
tr[0] = h[0] - l[0]
for N in (14, 60, 240):
    F[f"atr{N}"] = ema(tr, N)

# session running stats
sess_open_px = np.zeros(n); sess_hi = np.zeros(n); sess_lo = np.zeros(n)
cur_o = np.nan; cur_h = -np.inf; cur_l = np.inf
for t in range(n):
    if first_bar[t]:
        cur_o = o[t]; cur_h = -np.inf; cur_l = np.inf
    cur_h = max(cur_h, h[t]); cur_l = min(cur_l, l[t])
    sess_open_px[t] = cur_o; sess_hi[t] = cur_h; sess_lo[t] = cur_l
F["c_sessopen"] = c - sess_open_px
F["sess_range"] = sess_hi - sess_lo
F["c_sesshi"] = c - sess_hi
F["c_sesslo"] = c - sess_lo
F["c_sessmid"] = c - 0.5 * (sess_hi + sess_lo)
F["pos_in_range"] = np.where(sess_hi > sess_lo, (c - sess_lo) / np.maximum(sess_hi - sess_lo, 1e-9), 0.5) - 0.5

# prior session close & change; overnight gap
prev_close = np.zeros(n); cur_pc = np.nan; last_c = np.nan
for t in range(n):
    if first_bar[t]:
        cur_pc = last_c
    prev_close[t] = cur_pc
    last_c = c[t]
F["c_prevclose"] = c - prev_close

# time features
F["mod"] = mod.astype(float)
F["minutes_since_sopen"] = np.zeros(n)
cur0 = 0
mis = np.zeros(n)
for t in range(n):
    if first_bar[t]:
        cur0 = t
    mis[t] = t - cur0
F["minutes_since_sopen"] = mis

# flips-in-last-window churn
flip1 = np.abs(base.signal_trade) == 1
flip_cum = np.cumsum(flip1)
for W in (30, 60, 120, 240):
    ch = np.empty(n)
    ch[:W] = flip_cum[:W]
    ch[W:] = flip_cum[W:] - flip_cum[:-W]
    F[f"flips_last{W}"] = ch.astype(float)

# ---------- label rows ----------
rows = list(csv.DictReader(open(FEAT, newline="")))
S = []; D = []; LAB = []; CERT = []; ET = []
for r in rows:
    i_fill = idx_of[r["entry_time"]]
    S.append(i_fill - 1)
    D.append(1 if r["dir"] == "L" else -1)
    LAB.append(1 if r["label"] == "TAKE" else 0)
    CERT.append(r["certainty"])
    ET.append(r["entry_time"])
S = np.array(S); D = np.array(D); LAB = np.array(LAB); CERT = np.array(CERT)
hard = CERT == "HARD"
soft = CERT == "SOFT"
eps = CERT == "EPS"

print(f"labels: {len(S)} total, hard {hard.sum()} (take {int((LAB[hard]==1).sum())}, skip {int((LAB[hard]==0).sum())}), "
      f"eps {eps.sum()}, soft {soft.sum()}")

results = []
for name, arr in F.items():
    fv = arr[S]
    for mode in ("signed_gt", "raw_gt", "raw_abs_gt"):
        if mode == "signed_gt":
            x = fv * D
        elif mode == "raw_gt":
            x = fv.astype(float)
        else:
            x = np.abs(fv.astype(float))
        # candidate thresholds: midpoints of sorted unique values
        xs = np.unique(x[hard])
        if len(xs) < 2:
            continue
        thr = (xs[:-1] + xs[1:]) / 2.0
        for th in thr:
            for sense in (1, -1):  # allow iff sense*(x-th) > 0
                pred = (sense * (x - th)) > 0
                if np.all(pred[hard] == (LAB[hard] == 1)):
                    n_eps_bad = int((pred[eps] != (LAB[eps] == 1)).sum())
                    n_soft_bad = int((pred[soft] != (LAB[soft] == 1)).sum())
                    results.append((name, mode, sense, float(th), n_eps_bad, n_soft_bad))

print(f"\nHARD-perfect single rules found: {len(results)}")
results.sort(key=lambda r: (r[4] + r[5],))
for r in results[:60]:
    print(f"  {r[0]:>18} {r[1]:>10} sense={r[2]:+d} thr={r[3]:.3f}  eps_bad={r[4]} soft_bad={r[5]}")
