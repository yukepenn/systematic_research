"""R1.2f: build per-flip feature table with TAKEN/SKIPPED labels (cent-exact days only)."""
import csv
import os
import sys

import numpy as np

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from otr_engine import load_ledger, run_wrapper, WrapperPolicy  # noqa: E402

OUT = os.path.join(ROOT, "runs", "OTR_R1_SERIES", "out")
full = load_ledger(os.path.join(ROOT, "research", "03_reverse_engineering", "ledgers", "t2_canonical_1m.csv"))
cut = int(np.searchsorted(full["time"], np.datetime64("2023-01-21T00:00:00")))
bars = {k: (v[:cut] if isinstance(v, np.ndarray) else v) for k, v in full.items()}
bars["n"] = cut
bars["last_bar"] = bars["last_bar"].copy()
bars["last_bar"][-1] = True

pol = WrapperPolicy(comm_side=2.09, entry_types=(1,), reverse_on_flip=True)
r = run_wrapper(bars, pol)
trades = r["trades"]

# ground-truth labels from unique cent-exact subset diffs (entry time -> label)
SKIP = {"2023-01-03T12:37", "2023-01-03T13:28",
        "2023-01-04T21:07", "2023-01-04T23:36", "2023-01-05T12:21", "2023-01-05T13:24", "2023-01-05T14:16",
        "2023-01-08T18:02",
        "2023-01-12T13:39",          # epsilon day, single removal (soft)
        "2023-01-12T19:17",          # 1/13 removal (soft)
        "2023-01-04T13:25", "2023-01-04T14:07", "2023-01-04T14:11", "2023-01-04T14:18", "2023-01-04T14:25",  # soft
        }
SOFT = {"2023-01-12T13:39", "2023-01-12T19:17",
        "2023-01-04T13:25", "2023-01-04T14:07", "2023-01-04T14:11", "2023-01-04T14:18", "2023-01-04T14:25"}
# days fully certain (every trade labeled): 1/3,1/5,1/9,1/10,1/11 sessions
CERT_DAYS = {"2023-01-03", "2023-01-05", "2023-01-09", "2023-01-10", "2023-01-11"}

st = bars["signal_trade"]
sw = bars["signal_wave"]
strd = bars["signal_trend"]
ts_arr = bars["trailing_stop"]
tv_arr = bars["trend_vector"]
close = bars["close"]
sess_id = bars["session_id"]
first_bar = bars["first_bar"]
tarr = bars["time"]

# session open index per session
sess_open = {}
for i in range(cut):
    if first_bar[i]:
        sess_open[sess_id[i]] = i
last_idx = {}
for i in range(cut):
    last_idx[sess_id[i]] = i
sed = {sid: str(tarr[i])[:10] for sid, i in last_idx.items()}

rows = []
sess_state = {}
for k, t in enumerate(trades):
    ei = t["entry_i"]
    fi = ei - 1  # flip/signal bar
    sid = sess_id[ei]
    day = sed[sid]
    key = str(t["entry_time"])[:16].replace(" ", "T")[:16]
    key = key[:13] + ":" + key[14:16] if "T" in key else key
    key = str(t["entry_time"])[:16]
    key = key.replace(" ", "T")
    label = "SKIP" if key in SKIP else ("TAKE" if day in CERT_DAYS or key not in SOFT else "TAKE")
    cert = "HARD" if (day in CERT_DAYS or key in SKIP and key not in SOFT) else ("SOFT" if key in SOFT else "EPS")
    # rolling session stats from PRIOR labeled-TAKE trades this session (true-system view)
    ss = sess_state.setdefault(sid, {"real": 0.0, "losses": 0, "consec": 0, "consecL": 0, "consecS": 0, "n": 0})
    mins_open = int((tarr[ei] - tarr[sess_open[sid]]).astype("timedelta64[m]").astype(np.int64))
    mod = int((tarr[ei] - tarr[ei].astype("datetime64[D]")).astype("timedelta64[s]").astype(np.int64)) // 60
    dow = int((tarr[ei].astype("datetime64[D]").view("int64") + 4) % 7)  # 0=Mon
    prior_leg_bars = 0
    j = fi - 1
    while j > 0 and abs(st[j]) != 1:
        j -= 1
        prior_leg_bars += 1
    dist_tv = float(close[fi] - tv_arr[fi]) if not np.isnan(tv_arr[fi]) else np.nan
    dist_ts = float(close[fi] - ts_arr[fi]) if not np.isnan(ts_arr[fi]) else np.nan
    rows.append({
        "entry_time": str(t["entry_time"]), "session_end_day": day, "label": label,
        "certainty": cert, "dir": "L" if t["dir"] > 0 else "S",
        "weekday_of_entry": dow, "minutes_of_day_ET": mod, "mins_since_session_open": mins_open,
        "signal_wave": int(sw[fi]), "signal_trend": int(strd[fi]),
        "prior_leg_bars": prior_leg_bars,
        "close_minus_TV_pts": round(dist_tv, 2), "close_minus_TS_pts": round(dist_ts, 2),
        "sess_trades_before": ss["n"], "sess_realized_before": round(ss["real"], 2),
        "sess_losses_before": ss["losses"], "sess_consec_losses_before": ss["consec"],
        "pnl_this_trade": round(t["pnl"], 2), "exit_kind": t["exit_kind"],
        "hold_min": t["hold_min"],
    })
    # update session state AS IF the trade was taken only when label TAKE (true-system view)
    if label == "TAKE":
        ss["n"] += 1
        ss["real"] += t["pnl"]
        if t["pnl"] <= 0:
            ss["losses"] += 1
            ss["consec"] += 1
        else:
            ss["consec"] = 0

with open(os.path.join(OUT, "r12f_flip_features.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print(f"rows={len(rows)} skip={sum(1 for r in rows if r['label']=='SKIP')}")
for r in rows:
    if r["label"] == "SKIP":
        print("SKIP", r["entry_time"], r["dir"], "dow", r["weekday_of_entry"], "mod", r["minutes_of_day_ET"],
              "sopen+", r["mins_since_session_open"], "wave", r["signal_wave"], "trend", r["signal_trend"],
              "legbars", r["prior_leg_bars"], "cumR", r["sess_realized_before"], "consec", r["sess_consec_losses_before"], r["certainty"])
