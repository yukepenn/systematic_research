"""V3 MASTER-GAP HUNTER — diagnostic pass.

Re-runs run_r1g.run_integrated(X=1600,K=3,C=1000,entry_types=(1,)) (the registered
INT_T1only cell) and maps WHERE the +660 excess trades / -47.6k net gap lives:
month-by-month, session-time buckets, weekday, direction, hold-length, exit kind.
Writes v_mg_diag.json. No existing file modified.
"""
import json
import os
import sys
from collections import defaultdict

import numpy as np

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
SRC = os.path.join(ROOT, "research", "original_trader_reconstruction", "solar_family", "src")
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, SRC)
from otr_engine import load_ledger, POINT_VALUE, BARS_REQUIRED  # noqa: E402
from solarwave import SolarWaveParams, solar_wave_full  # noqa: E402

OUT = os.path.join(ROOT, "runs", "OTR_R1_SERIES", "out")

print("[v_mg_diag] loading ledger + late-mode signals ...", flush=True)
b = load_ledger(os.path.join(ROOT, "research", "03_reverse_engineering", "ledgers", "t2_canonical_1m.csv"))
res = solar_wave_full(b["open"], b["high"], b["low"], b["close"],
                      SolarWaveParams(pullback_early=False), start_up=False)
st = res.signal_trade.astype(np.int64)
ts_arr = res.trailing_stop
n = b["n"]
close, opn = b["close"], b["open"]
first_bar, last_bar = b["first_bar"], b["last_bar"]
tarr = b["time"]
mod = ((tarr - tarr.astype("datetime64[D]")).astype("timedelta64[s]").astype(np.int64) // 60).astype(np.int64)

sess_open_i = np.zeros(n, dtype=np.int64)
cur = 0
for i in range(n):
    if first_bar[i]:
        cur = i
    sess_open_i[i] = cur
mins_open = ((tarr - tarr[sess_open_i]).astype("timedelta64[s]").astype(np.int64) // 60).astype(np.int64)

COMM = 2.09


def run_integrated(X, K, C, entry_types=(1,), use_b1=True, use_gate=True):
    trades = []
    pos = 0
    entry_px = 0.0
    entry_i = -1
    pend_entry = 0
    pend_exit = False
    pend_reverse = 0
    cum = 0.0
    high = 0.0
    consec = {1: 0, -1: 0}
    prior = 0.0

    def realize(i_exit, px_exit, kind):
        nonlocal pos, cum, high
        pnl = pos * (px_exit - entry_px) * POINT_VALUE - 2 * COMM
        trades.append({"dir": pos, "entry_i": entry_i, "exit_i": i_exit,
                       "entry_time": str(tarr[entry_i]), "exit_time": str(tarr[i_exit]),
                       "pnl": pnl, "exit_kind": kind,
                       "hold_min": float((tarr[i_exit] - tarr[entry_i]).astype("timedelta64[s]").astype(np.int64)) / 60.0})
        cum += pnl
        high = max(high, cum)
        if pnl <= 0:
            consec[pos] += 1
        else:
            consec[pos] = 0
        pos = 0

    def gate_ok(d, i):
        if not use_gate:
            return True
        if prior <= -C and mins_open[i] <= 360:
            return False
        if high >= X and mod[i] >= 720:
            if cum < 0:
                return False
            if consec[d] >= K:
                return False
        return True

    for i in range(n):
        if first_bar[i]:
            prior = cum
            cum = 0.0
            high = 0.0
            consec = {1: 0, -1: 0}
        if pend_exit and pos != 0:
            realize(i, opn[i], "flip")
            pend_exit = False
        if pend_reverse != 0:
            if pos != 0:
                realize(i, opn[i], "flip")
            if gate_ok(pend_reverse, i):
                pos = pend_reverse
                entry_px, entry_i = opn[i], i
            pend_reverse = 0
        if pend_entry != 0 and pos == 0:
            if gate_ok(pend_entry, i):
                pos = pend_entry
                entry_px, entry_i = opn[i], i
            pend_entry = 0
        pend_entry = 0
        sig = st[i]
        if last_bar[i]:
            if pos != 0:
                realize(i, close[i], "session_close")
            pend_exit = False
            pend_entry = 0
            pend_reverse = 0
            continue
        decision_allowed = not (use_b1 and first_bar[i])
        if pos != 0:
            line = ts_arr[i]
            if not np.isnan(line):
                hit = (pos > 0 and close[i] <= line) or (pos < 0 and close[i] >= line)
                if hit:
                    if decision_allowed and sig == -pos and abs(sig) == 1 and i >= BARS_REQUIRED:
                        pend_reverse = sig
                    else:
                        pend_exit = True
                    continue
        if pos == 0 and sig != 0 and i >= BARS_REQUIRED and decision_allowed:
            if abs(sig) in entry_types:
                pend_entry = 1 if sig > 0 else -1
    return trades


tr = run_integrated(1600, 3, 1000)
p = np.array([t["pnl"] for t in tr])
d = np.array([t["dir"] for t in tr])
print(f"[v_mg_diag] INT_T1only reproduced: n={len(tr)} net={p.sum():.2f} "
      f"L={int((d>0).sum())} S={int((d<0).sum())}", flush=True)

# ---- target facts (r11_master.json) ----
TARGET = {"n": 4351, "L": 2166, "S": 2185, "net": 292172.82, "long_net": 214911.12,
          "short_net": 77261.70, "wr_l": 41.97, "wr_s": 38.63, "pf_l": 1.27, "pf_s": 1.09,
          "hold_l": 105.85, "hold_s": 82.56, "tpd": 8.26}

sess_id = b["session_id"]
n_sessions_total = int(first_bar.sum())

# session end-date per session id (labels sessions by their ENDING day, like the trader's table)
last_idx = {}
for i in range(n):
    last_idx[sess_id[i]] = i
sess_end_day = {sid: str(tarr[i])[:10] for sid, i in last_idx.items()}

# sessions per month (by session end day)
sess_per_month = defaultdict(int)
for sid, day in sess_end_day.items():
    sess_per_month[day[:7]] += 1

# ---- month-by-month ----
bym = defaultdict(list)
for t in tr:
    m = sess_end_day[sess_id[t["entry_i"]]][:7]
    bym[m].append(t)

ratio = TARGET["n"] / len(tr)
print("\n=== MONTH-BY-MONTH (sim INT_T1only; session keyed by end day) ===")
print(f"{'month':8} {'sess':>4} {'n':>4} {'t/day':>6} {'net':>10} {'L':>4} {'S':>4} "
      f"{'wr%':>5} {'holdL':>6} {'holdS':>6} {'net/day':>8}")
month_rows = []
for m in sorted(bym):
    ts_ = bym[m]
    pp = np.array([t["pnl"] for t in ts_])
    dd_ = np.array([t["dir"] for t in ts_])
    hh = np.array([t["hold_min"] for t in ts_])
    ns = sess_per_month[m]
    row = {"month": m, "sessions": ns, "n": len(ts_), "tpd": round(len(ts_) / ns, 2),
           "net": round(float(pp.sum()), 2), "L": int((dd_ > 0).sum()), "S": int((dd_ < 0).sum()),
           "wr": round(float((pp > 0).mean() * 100), 1),
           "holdL": round(float(hh[dd_ > 0].mean()), 1) if (dd_ > 0).any() else None,
           "holdS": round(float(hh[dd_ < 0].mean()), 1) if (dd_ < 0).any() else None,
           "net_per_day": round(float(pp.sum()) / ns, 1)}
    month_rows.append(row)
    print(f"{m:8} {ns:>4} {len(ts_):>4} {row['tpd']:>6} {row['net']:>10.0f} {row['L']:>4} {row['S']:>4} "
          f"{row['wr']:>5} {row['holdL']:>6} {row['holdS']:>6} {row['net_per_day']:>8}")

tpd_all = len(tr) / n_sessions_total
print(f"\nsim trades/day overall = {tpd_all:.2f}  target = {TARGET['tpd']}  "
      f"(uniform target-equivalent ratio {ratio:.3f})")

# year splits
for yr in ("2023", "2024", "2025"):
    ts_ = [t for t in tr if sess_end_day[sess_id[t['entry_i']]].startswith(yr)]
    ns = sum(v for k, v in sess_per_month.items() if k.startswith(yr))
    if ts_:
        pp = np.array([t["pnl"] for t in ts_])
        print(f"{yr}: n={len(ts_)} sess={ns} t/day={len(ts_)/ns:.2f} net={pp.sum():.0f}")

# ---- direction split vs target ----
print("\n=== DIRECTION SPLIT vs TARGET ===")
for lbl, mask in (("LONG", d > 0), ("SHORT", d < 0)):
    pp = p[mask]
    w = pp > 0
    gl = pp[~w].sum()
    print(f"{lbl}: n={mask.sum()} net={pp.sum():.0f} wr={w.mean()*100:.2f} "
          f"pf={pp[w].sum()/-gl:.3f}")
print(f"TARGET LONG: n=2166 net=214911 wr=41.97 pf=1.27 | SHORT: n=2185 net=77262 wr=38.63 pf=1.09")

# ---- entry time-of-day buckets ----
print("\n=== ENTRY TIME BUCKETS (ET, bar-end stamp) ===")
mod_e = np.array([mod[t["entry_i"]] for t in tr])


def bucket(m):
    if m >= 1080:      # 18:00-24:00
        return "eve_18-24"
    if m < 360:        # 00:00-06:00
        return "night_00-06"
    if m < 720:        # 06:00-12:00
        return "morn_06-12"
    return "day_12-17"


byb = defaultdict(list)
for t, m in zip(tr, mod_e):
    byb[bucket(m)].append(t)
for k in ("eve_18-24", "night_00-06", "morn_06-12", "day_12-17"):
    ts_ = byb[k]
    pp = np.array([t["pnl"] for t in ts_])
    hh = np.array([t["hold_min"] for t in ts_])
    w = pp > 0
    gl = pp[~w].sum()
    print(f"{k:12} n={len(ts_):4} net={pp.sum():9.0f} wr={w.mean()*100:5.1f} "
          f"pf={pp[w].sum()/-gl:5.3f} avg={pp.mean():7.1f} hold={hh.mean():6.1f}")

# ---- weekday ----
print("\n=== WEEKDAY of entry (0=Mon) ===")
wd_e = ((np.array([t["entry_i"] for t in tr]) * 0 +
         (np.array([tarr[t["entry_i"]] for t in tr]).astype("datetime64[D]").astype(np.int64) + 3) % 7))
for wd in range(7):
    mask = wd_e == wd
    if mask.sum() == 0:
        continue
    pp = p[mask]
    print(f"wd{wd}: n={mask.sum():4} net={pp.sum():9.0f} avg={pp.mean():7.1f} wr={(pp>0).mean()*100:5.1f}")

# ---- hold buckets ----
print("\n=== HOLD-LENGTH BUCKETS ===")
hh_all = np.array([t["hold_min"] for t in tr])
for lo, hi in ((0, 5), (5, 15), (15, 30), (30, 60), (60, 120), (120, 240), (240, 1e9)):
    mask = (hh_all >= lo) & (hh_all < hi)
    pp = p[mask]
    if mask.sum():
        print(f"hold[{lo:>4},{hi if hi<1e9 else 'inf':>4}): n={mask.sum():4} net={pp.sum():9.0f} "
              f"avg={pp.mean():7.1f} wr={(pp>0).mean()*100:5.1f}")

# ---- exit kind ----
print("\n=== EXIT KIND ===")
byk = defaultdict(list)
for t in tr:
    byk[t["exit_kind"]].append(t["pnl"])
for k, v in byk.items():
    v = np.array(v)
    print(f"{k}: n={len(v)} net={v.sum():.0f} avg={v.mean():.1f}")

# ---- per-session trade-count distribution ----
print("\n=== TRADES PER SESSION distribution ===")
per_sess = defaultdict(int)
for t in tr:
    per_sess[sess_id[t["entry_i"]]] += 1
cnts = np.array([per_sess.get(s, 0) for s in range(n_sessions_total)])
print(f"mean={cnts.mean():.2f} med={np.median(cnts):.0f} max={cnts.max()} "
      f"p90={np.percentile(cnts,90):.0f} p99={np.percentile(cnts,99):.0f}")
for k in range(0, 26):
    c = int((cnts == k).sum())
    if c:
        print(f"  {k:>2} trades: {c:3} sessions", end="")
        if (k + 1) % 4 == 0:
            print()
print()
hi_sessions = sorted([(s, c) for s, c in per_sess.items() if c >= 15], key=lambda x: -x[1])[:15]
print("busiest sessions:", [(sess_end_day[s], c) for s, c in hi_sessions])

# what fraction of net loss lives in >=N-trade sessions ("chop days")
for thr in (10, 12, 15):
    hs = {s for s, c in per_sess.items() if c >= thr}
    pp = np.array([t["pnl"] for t in tr if sess_id[t["entry_i"]] in hs])
    nn = len(pp)
    print(f"sessions with >= {thr} trades: {len(hs)} sess, {nn} trades, net={pp.sum():.0f}")

with open(os.path.join(OUT, "v_mg_diag.json"), "w") as f:
    json.dump({"months": month_rows,
               "overall": {"n": len(tr), "net": round(float(p.sum()), 2),
                           "tpd": round(tpd_all, 3)}}, f, indent=1)
print("[v_mg_diag] done", flush=True)
