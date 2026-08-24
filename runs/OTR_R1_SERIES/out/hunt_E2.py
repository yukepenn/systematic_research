"""Family E hunt, step 2: feature matrix at labeled flips + brute-force conjunction search.

SKIP iff (A AND B) where A,B are thresholded predicates. Require zero HARD errors,
minimize SOFT+EPS errors.
"""
import sys, csv, itertools, json
import numpy as np

sys.path.insert(0, r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\research\original_trader_reconstruction\solar_family\src")
sys.path.insert(0, r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\src\analytics")
from otr_engine import load_ledger
from solarwave import solar_wave_full, solar_wave, SolarWaveParams

LEDGER = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\research\03_reverse_engineering\ledgers\t2_canonical_1m.csv"
FEAT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\runs\OTR_R1_SERIES\out\r12f_flip_features.csv"

bars = load_ledger(LEDGER)
n = bars["n"]
opn, high, low, close, vol = bars["open"], bars["high"], bars["low"], bars["close"], bars["volume"]
first_bar = bars["first_bar"]; sess_id = bars["session_id"]
time_arr = bars["time"]
st = bars["signal_trade"]

late = solar_wave_full(opn, high, low, close, SolarWaveParams(pullback_early=False))
st_late = late.signal_trade

# ---- per-bar helper series ----
secs = (time_arr - time_arr.astype("datetime64[D]")).astype("timedelta64[s]").astype(np.int64)
mod = (secs // 60).astype(np.int64)
dow = ((time_arr.astype("datetime64[D]").astype(np.int64) + 4) % 7)  # 0=Sun..6=Sat? 1970-01-01=Thu=4

# session-anchored cumulative for VWAP / open / cumvol / bars-since-open
sess_start_idx = np.zeros(n, dtype=np.int64)
cur = 0
for i in range(n):
    if first_bar[i]:
        cur = i
    sess_start_idx[i] = cur
bars_since_open = np.arange(n) - sess_start_idx

typ_px = (high + low + close) / 3.0
pv = typ_px * vol
cum_pv = np.cumsum(pv); cum_v = np.cumsum(vol)


def sess_cum(x_cum, i):
    s = sess_start_idx[i]
    base = x_cum[s - 1] if s > 0 else 0.0
    return x_cum[i] - base


# rolling TR / ranges
prev_c = np.concatenate([[close[0]], close[:-1]])
tr = np.maximum(high, prev_c) - np.minimum(low, prev_c)
cs_tr = np.cumsum(tr)


def sma_tr(i, w):
    a = max(0, i - w + 1)
    return (cs_tr[i] - (cs_tr[a - 1] if a > 0 else 0.0)) / (i - a + 1)


def roll_range(i, w):
    a = max(0, i - w + 1)
    return high[a:i + 1].max() - low[a:i + 1].min()


def roll_min(i, w):
    a = max(0, i - w + 1)
    return low[a:i + 1].min()


cs_vol = np.cumsum(vol)


def sma_vol(i, w):
    a = max(0, i - w + 1)
    return (cs_vol[i] - (cs_vol[a - 1] if a > 0 else 0.0)) / (i - a + 1)


# prev session last close
prev_sess_close = np.full(n, np.nan)
last_close_of_prev = np.nan
for i in range(n):
    if first_bar[i] and i > 0:
        last_close_of_prev = close[i - 1]
    prev_sess_close[i] = last_close_of_prev

# flip indices over whole series
flip_idx = np.where(np.abs(st) == 1)[0]
flip_pos = {int(i): k for k, i in enumerate(flip_idx)}

# slow solar ladders on 1-min closes
slow = {}
for k in (1.5, 2.0, 3.0):
    r = solar_wave(close, SolarWaveParams(offset_multiplier_trend=90 * k,
                                          offset_multiplier_stop=179 * k))
    slow[k] = r

# HTF solar on resampled closes (5m,15m,30m): use bars where (mod % m == m-1)... simpler:
# resample by taking every m-th bar close within the series (approximation via bar count)
htf = {}
for m in (5, 15, 30, 60):
    idxs = np.where((bars_since_open % m) == (m - 1))[0]
    r = solar_wave(close[idxs], SolarWaveParams())
    # map back: for bar i, last completed HTF bar = last idx <= i
    htf[m] = (idxs, r)


def htf_state(m, i):
    idxs, r = htf[m]
    j = np.searchsorted(idxs, i, side="right") - 1
    if j < 0:
        return 0, 1, np.nan, np.nan
    up = 1 if r.is_up[j] else -1
    weak = 1 if abs(r.signal_trend[j]) == 1 else 0
    return up, weak, r.trend_vector[j], r.trailing_stop[j]


# labels
labels = []
with open(FEAT, newline="") as f:
    for row in csv.DictReader(f):
        labels.append(row)

time_strs = [str(t) for t in time_arr]
tidx = {t: i for i, t in enumerate(time_strs)}

# true-run session state (only TAKE rows count), grouped by session_end_day
state_rows = []
prev_day = None
for row in labels:
    day = row["session_end_day"]
    if day != prev_day:
        cum = 0.0; peak = 0.0; nt = 0; nl = 0; cl = 0
        side_cum = {1: 0.0, -1: 0.0}; side_cl = {1: 0, -1: 0}
        last_pnl = 0.0; last_side_pnl = {1: 0.0, -1: 0.0}
        last_exit = {1: np.nan, -1: np.nan}; last_entry = {1: np.nan, -1: np.nan}
        last_exit_any = np.nan
        prev_day = day
    d = 1 if row["dir"] == "L" else -1
    state_rows.append(dict(cum=cum, peak=peak, dd=peak - cum, nt=nt, nl=nl, cl=cl,
                           side_cum=side_cum[d], side_cl=side_cl[d],
                           opp_cum=side_cum[-d], opp_cl=side_cl[-d],
                           last_pnl=last_pnl, last_same_pnl=last_side_pnl[d],
                           last_exit_same=last_exit[d], last_entry_same=last_entry[d],
                           last_exit_any=last_exit_any))
    if row["label"] == "TAKE":
        p = float(row["pnl_this_trade"])
        fill_i = tidx[row["entry_time"]]
        e_px = opn[fill_i]
        x_px = e_px + d * (p + 4.18) / 20.0
        cum += p; peak = max(peak, cum); nt += 1
        side_cum[d] += p
        if p < 0:
            nl += 1; cl += 1; side_cl[d] += 1
        else:
            cl = 0; side_cl[d] = 0
        last_pnl = p; last_side_pnl[d] = p
        last_entry[d] = e_px; last_exit[d] = x_px; last_exit_any = x_px

# ---- build feature matrix ----
feat_names = []
rows_X = []
y = []          # 1 = SKIP
cert = []
meta = []
for ri, row in enumerate(labels):
    i = tidx[row["entry_time"]] - 1   # entry_time = FILL bar; decision/flip bar is i-1
    assert abs(st[i]) == 1, (row["entry_time"], st[i])
    d = 1 if row["dir"] == "L" else -1
    s = sess_start_idx[i]
    sess_vwap = sess_cum(cum_pv, i) / max(sess_cum(cum_v, i), 1e-9)
    sess_open_px = opn[s]
    k = flip_pos[i]
    pf = flip_idx[k - 1] if k > 0 else max(0, i - 1)
    leg_bars = i - pf
    leg_amp = abs(close[i] - close[pf])
    # events in prior leg (exclusive of flip bars)
    seg = slice(pf + 1, i)
    n_t2_e = int(np.sum(np.abs(st[seg]) == 2))
    n_t2_l = int(np.sum(np.abs(st_late[seg]) == 2))
    n_t3 = int(np.sum(np.abs(st[seg]) == 3))
    stt = state_rows[ri]
    # structure: previous same-direction flip close, previous same-dir leg extreme
    prev_same_flip_close = np.nan
    prev_same_leg_ext = np.nan
    kk = k - 1
    while kk >= 0:
        fj = flip_idx[kk]
        if st[fj] == st[i]:
            prev_same_flip_close = close[fj]
            nxt = flip_idx[kk + 1]
            seg2 = close[fj:nxt]
            prev_same_leg_ext = seg2.max() if d > 0 else seg2.min()
            break
        kk -= 1
    sess_hi = high[s:i + 1].max(); sess_lo = low[s:i + 1].min()
    hi_i = s + int(np.argmax(high[s:i + 1])); lo_i = s + int(np.argmin(low[s:i + 1]))
    up5, wk5, tv5, ts5 = htf_state(5, i)
    up15, wk15, tv15, ts15 = htf_state(15, i)
    up30, wk30, tv30, ts30 = htf_state(30, i)
    up60, wk60, tv60, ts60 = htf_state(60, i)
    f = {
        "mod": mod[i], "dow": dow[i], "mins_open": bars_since_open[i],
        "dir": d, "leg_bars": leg_bars, "leg_amp": leg_amp,
        "wave_prev": abs(late.signal_wave[i - 1]),
        "weak_prev": 1 if abs(late.signal_trend[i - 1]) == 1 else 0,
        "n_t2_early": n_t2_e, "n_t2_late": n_t2_l, "n_t3": n_t3,
        "vwap_dist": d * (close[i] - sess_vwap),
        "sessopen_dist": d * (close[i] - sess_open_px),
        "prevclose_dist": d * (close[i] - prev_sess_close[i]),
        "atr14": sma_tr(i, 14), "atr60": sma_tr(i, 60),
        "range60": roll_range(i, 60), "range240": roll_range(i, 240),
        "range_sess": high[s:i + 1].max() - low[s:i + 1].min(),
        "vol_bar": vol[i], "vol_ratio15": vol[i] / max(sma_vol(i, 15), 1e-9),
        "sess_cumvol": sess_cum(cs_vol, i),
        "mom30": d * (close[i] - close[max(0, i - 30)]),
        "mom60": d * (close[i] - close[max(0, i - 60)]),
        "mom120": d * (close[i] - close[max(0, i - 120)]),
        "flips120": int(np.sum(np.abs(st[max(0, i - 120):i + 1]) == 1)),
        "flips60": int(np.sum(np.abs(st[max(0, i - 60):i + 1]) == 1)),
        "overnight": 1 if (mod[i] >= 1080 or mod[i] < 570) else 0,
        "gap_next": d * (opn[i + 1] - close[i]),
        "bar_range": high[i] - low[i], "bar_body": d * (close[i] - opn[i]),
        "breach": d * (close[i] - (bars["trailing_stop"][i - 1] if i > 0 else np.nan)),
        "cum": stt["cum"], "dd": stt["dd"], "nt": stt["nt"], "nl": stt["nl"],
        "cl": stt["cl"], "side_cum": stt["side_cum"], "side_cl": stt["side_cl"],
        "opp_cum": stt["opp_cum"], "opp_cl": stt["opp_cl"],
        "last_pnl": stt["last_pnl"], "last_same_pnl": stt["last_same_pnl"],
        "slow15_al": d * (1 if slow[1.5].is_up[i] else -1),
        "slow2_al": d * (1 if slow[2.0].is_up[i] else -1),
        "slow3_al": d * (1 if slow[3.0].is_up[i] else -1),
        "slow15_wk": 1 if abs(slow[1.5].signal_trend[i]) == 1 else 0,
        "slow2_wk": 1 if abs(slow[2.0].signal_trend[i]) == 1 else 0,
        "slow15_tvd": d * (close[i] - slow[1.5].trend_vector[i]),
        "slow2_tvd": d * (close[i] - slow[2.0].trend_vector[i]),
        "htf5_al": d * up5, "htf5_wk": wk5, "htf5_tvd": d * (close[i] - tv5),
        "htf15_al": d * up15, "htf15_wk": wk15, "htf15_tvd": d * (close[i] - tv15),
        "htf30_al": d * up30, "htf30_wk": wk30, "htf30_tvd": d * (close[i] - tv30),
        "htf60_al": d * up60, "htf60_wk": wk60,
        # structure / memory features
        "hh_flip": d * (close[i] - prev_same_flip_close) if not np.isnan(prev_same_flip_close) else 0.0,
        "hh_ext": d * (close[i] - prev_same_leg_ext) if not np.isnan(prev_same_leg_ext) else 0.0,
        "dist_sess_ext_fav": (sess_hi - close[i]) if d > 0 else (close[i] - sess_lo),
        "dist_sess_ext_adv": (close[i] - sess_lo) if d > 0 else (sess_hi - close[i]),
        "bars_since_fav_ext": (i - hi_i) if d > 0 else (i - lo_i),
        "sess_range_pos": (close[i] - sess_lo) / max(sess_hi - sess_lo, 1e-9),
        "mins_to_close": (1020 - mod[i]) % 1440,
        "nflips_sess": int(np.sum(np.abs(st[s:i + 1]) == 1)),
        "vs_last_exit_same": d * (close[i] - stt["last_exit_same"]) if not np.isnan(stt["last_exit_same"]) else 0.0,
        "vs_last_entry_same": d * (close[i] - stt["last_entry_same"]) if not np.isnan(stt["last_entry_same"]) else 0.0,
        "vs_last_exit_any": d * (close[i] - stt["last_exit_any"]) if not np.isnan(stt["last_exit_any"]) else 0.0,
        "leg_ret_signed": d * (close[i] - close[pf]),
        "range30": roll_range(i, 30),
        "chop_ratio": leg_amp / max(roll_range(i, max(leg_bars, 1)), 1e-9),
    }
    if not feat_names:
        feat_names = list(f.keys())
    rows_X.append([float(f[k2]) for k2 in feat_names])
    y.append(1 if row["label"] == "SKIP" else 0)
    cert.append(row["certainty"])
    meta.append((row["entry_time"], row["dir"], row["label"], row["certainty"]))

X = np.array(rows_X); y = np.array(y); cert = np.array(cert)
hardm = cert == "HARD"; softm = cert == "SOFT"
print("rows", X.shape, "skips", y.sum(), "hard", hardm.sum())

np.save("hunt_E_X.npy", X); np.save("hunt_E_y.npy", y)
json.dump({"feat_names": feat_names, "meta": meta}, open("hunt_E_meta.json", "w"))

# ---- predicate pool: (feat, op, thr) ----
preds = []
for j, name in enumerate(feat_names):
    vals = np.unique(X[:, j])
    if len(vals) < 2:
        continue
    thrs = (vals[:-1] + vals[1:]) / 2
    if len(thrs) > 60:
        qs = np.linspace(0, 1, 61)[1:-1]
        thrs = np.unique(np.quantile(X[:, j], qs))
    for t in thrs:
        preds.append((j, "<=", t, X[:, j] <= t))
        preds.append((j, ">=", t, X[:, j] > t))
print("predicates:", len(preds))

# ---- single predicates: SKIP iff P ----
def score(mask):
    errs = mask != y
    return errs[hardm].sum(), errs[softm].sum(), errs[~hardm & ~softm].sum()

best_single = []
for (j, op, t, m) in preds:
    he, se, ee = score(m)
    if he == 0:
        best_single.append((se + ee, se, ee, feat_names[j], op, t))
best_single.sort()
print("\nsingle predicates with 0 HARD errors:", len(best_single))
for b in best_single[:15]:
    print(b)

# ---- pairs: SKIP iff A AND B ----
# prune: A must at least cover all HARD skips (mask True on all hard skips)
hard_skip = hardm & (y == 1)
hard_take = hardm & (y == 0)
cands = [(j, op, t, m) for (j, op, t, m) in preds if m[hard_skip].all()]
print("\ncandidates covering all HARD skips:", len(cands))
results = []
for a in range(len(cands)):
    ja, opa, ta, ma = cands[a]
    for b in range(a + 1, len(cands)):
        jb, opb, tb, mb = cands[b]
        if ja == jb:
            continue
        m = ma & mb
        he, se, ee = score(m)
        results.append((he, se + ee, se, ee, feat_names[ja], opa, round(ta, 3),
                        feat_names[jb], opb, round(tb, 3), a, b))
results.sort()
print("\nbest conjunctions (hard_err, soft+eps_err):", len(results))
seen = set()
shown = 0
for r in results:
    key = (r[4], r[7])
    if key in seen:
        continue
    seen.add(key)
    print(r[:10])
    shown += 1
    if shown >= 30:
        break

# detail failing rows for top-3 distinct
seen = set(); shown = 0
for r in results:
    key = (r[4], r[7])
    if key in seen:
        continue
    seen.add(key)
    a, b = r[10], r[11]
    m = cands[a][3] & cands[b][3]
    errs = np.where(m != y)[0]
    print("\nRULE", r[4], cands[a][1], round(cands[a][2], 3), "AND", r[7], cands[b][1], round(cands[b][2], 3))
    for e in errs:
        print("   MISS", meta[e], "pred_skip" if m[e] else "pred_take")
    shown += 1
    if shown >= 3:
        break
