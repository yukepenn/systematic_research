"""Rebuild the MNQ canonical Python reference using GENUINE MNQU6 prices (exported this run
via BarExportV1 through the real Strategy Analyzer engine -- runs/PRODUCTB_ONECONTRACT_FINAL/
out/mnq_3m_raw.csv), instead of NQ prices scaled by MNQ's point value (the approximation every
prior "1 MNQ" figure in this program has used, per REPORT.md's diagnosed parity gap). Signal
math (M) still derives from NQ per the frozen rule -- only FILL PRICES change.
"""
import json, sys, os
import numpy as np, pandas as pd

sys.path.insert(0, "src/analytics")
from sm01_solarsim import load_bars_3m, _fill
from sm_bmom import rth_3m, BAND_DAYS
from smv2_common import dd_battery
import sm_metrics

OUT = "runs/PRODUCTB_ONECONTRACT_FINAL/out"
NT_JSON = r"C:\Users\Yuke Zhang\.claude\projects\D--OneDrive---Washington-University-in-St--Louis-TradingResearch-systematic-research\bfb80633-2ca8-4554-803e-2bd6cbeeb4c1\tool-results\mcp-crosstrade-GetMcpJob-1786235588552.txt"
MNQ_RAW = f"{OUT}/mnq_3m_raw.csv"
MNQ_COMM, MNQ_PV = 0.65, 2.0

def rha(x):
    return np.sign(x) * np.floor(np.abs(x) + 0.5)

bars = load_bars_3m()
sess = pd.to_datetime(bars["sess_date"])
dev = sess <= pd.Timestamp("2026-05-31")
bars_dev = bars[dev].reset_index(drop=True)
bp = pd.read_parquet("runs/SM01_SUBSTRATE/out/e10_bar_pnl.parquet")
T = bp["tgt"].to_numpy().astype(float)
sclose = bars.loc[bars["is_last_of_sess"], ["sess_date", "close"]].set_index("sess_date")["close"]
htf = np.sign(sclose - sclose.rolling(50).mean()).shift(1).to_dict()
st_bar = np.array([htf.get(dd_, np.nan) for dd_ in bars["sess_date"]])
agree = (np.sign(T) != 0) & (st_bar == np.sign(T))
Tp_old = np.clip(rha(T * np.where(agree, 1.25, 1.0) * 0.9026), -13, 13)

def bmom_pos_series(bars3):
    r = rth_3m(bars3)
    pos_arr = np.zeros(len(bars3)); hist = {}; day_count = 0
    for d_, g in r.groupby("date", sort=True):
        g = g.sort_values("hm")
        if g["hm"].iloc[0] != 933: continue
        open0930 = g["open"].iloc[0]
        close = g["close"].to_numpy(); vol = g["volume"].to_numpy(); hm = g["hm"].to_numpy()
        vwap = np.cumsum(close * vol) / np.maximum(np.cumsum(vol), 1e-9)
        gidx = g.index.to_numpy(); pos = 0
        flat_hm = int(hm[hm <= 1557].max()) if (hm <= 1557).any() else None
        if day_count >= BAND_DAYS:
            for i in range(len(g)):
                h = int(hm[i])
                if flat_hm is not None and h == flat_hm:
                    pos = 0; pos_arr[gidx[i]] = pos; break
                if h > 1554: pos_arr[gidx[i]] = pos; continue
                past = hist.get(h)
                if past is not None and len(past) >= 1:
                    m_tod = float(np.mean(past[-BAND_DAYS:]))
                    up, lo = open0930 + m_tod, open0930 - m_tod
                    if close[i] > max(up, vwap[i]): pos = 1
                    elif close[i] < min(lo, vwap[i]): pos = -1
                pos_arr[gidx[i]] = pos
        for i in range(len(g)):
            hist.setdefault(int(hm[i]), []).append(abs(close[i] - open0930))
        day_count += 1
    return pos_arr

B = bmom_pos_series(bars)
Mp_old = 0.7086 * Tp_old + 2.83 * B
M = Mp_old[dev.to_numpy()]

n = len(bars_dev)
last = bars_dev["is_last_of_sess"].to_numpy()
tm = bars_dev["time"]
hm_arr = tm.dt.hour.to_numpy() * 100 + tm.dt.minute.to_numpy()
sd = bars_dev["sess_date"].to_numpy()
a_, b_ = 3, 1

# ---- load genuine MNQU6 bars and align onto the NQ 3-minute time grid ----
mnq = pd.read_csv(MNQ_RAW, comment="#")
mnq["time"] = pd.to_datetime(mnq["time"])
mnq_idx = mnq.set_index("time")
nq_times = tm.reset_index(drop=True)
aligned = mnq_idx.reindex(nq_times)
n_missing = int(aligned["close"].isna().sum())
print(f"MNQ bars total: {len(mnq)}; aligned to {n} NQ-grid timestamps; missing: {n_missing} "
      f"({100*n_missing/n:.4f}%)")
# forward-fill isolated gaps (thin/no-print bars), disclose count, never fabricate a trend
aligned_ffill = aligned.ffill()
n_ffilled = int(aligned["close"].isna().sum())
o = aligned_ffill["open"].to_numpy(); h = aligned_ffill["high"].to_numpy()
l = aligned_ffill["low"].to_numpy(); c = aligned_ffill["close"].to_numpy()

cash = 0.0; p = 0; pend = 0
fills = []
daily = {}; prev = 0.0
for t in range(n):
    if pend != p:
        dta = pend - p; side = 1 if dta > 0 else -1
        px = _fill(o[t], h[t], l[t], side)
        cash -= dta * px * MNQ_PV; cash -= abs(dta) * MNQ_COMM
        fills.append({"time_open": tm.iloc[t] - pd.Timedelta(minutes=3), "d": dta, "px": px})
        p = pend
    if last[t] and p != 0:
        side = -1 if p > 0 else 1
        px = _fill(o[t], h[t], l[t], side, at_close=c[t])
        cash += p * px * MNQ_PV; cash -= abs(p) * MNQ_COMM
        fills.append({"time_open": tm.iloc[t], "d": -p, "px": px})
        p = 0; pend = 0
    else:
        Mt = M[t]
        if hm_arr[t] == 1639: pend = 0
        elif 1630 <= hm_arr[t] < 1803: pend = p if hm_arr[t] < 1639 else 0
        else:
            if p == 0: pend = 1 if Mt >= a_ else (-1 if Mt <= -a_ else 0)
            elif p == 1: pend = -1 if Mt <= -a_ else (0 if Mt <= b_ else 1)
            else: pend = 1 if Mt >= a_ else (0 if Mt >= -b_ else -1)
    if last[t]:
        eq = cash + p * c[t] * MNQ_PV
        daily[sd[t]] = eq - prev; prev = eq

py_daily = pd.Series(daily); py_daily.index = pd.to_datetime(py_daily.index)
pf = pd.DataFrame(fills)
rt = []; pos = 0; ent = None
for _, f in pf.iterrows():
    d0 = int(f["d"])
    if pos == 0:
        pos = d0; ent = f
    else:
        if abs(d0) == 2:
            rt.append({"dir": pos, "entry_time": ent["time_open"], "entry_px": ent["px"],
                       "exit_time": f["time_open"], "exit_px": f["px"]})
            pos = pos + d0; ent = f
        else:
            rt.append({"dir": pos, "entry_time": ent["time_open"], "entry_px": ent["px"],
                       "exit_time": f["time_open"], "exit_px": f["px"]})
            pos = 0; ent = None
pyt = pd.DataFrame(rt)
pyt["pnl"] = (pyt["exit_px"] - pyt["entry_px"]) * pyt["dir"] * MNQ_PV - 2 * MNQ_COMM
pyt.to_csv(f"{OUT}/py_trades_mnq_genuine.csv", index=False)
py_daily.to_csv(f"{OUT}/py_daily_mnq_genuine.csv", header=["net"])
print(f"PY (genuine MNQ prices): net {py_daily.sum():.2f}  round trips {len(pyt)}")
print(f"PY (old, NQ-scaled approx): net 28676.10 (for comparison)")

# ---- reconcile against the real NT8 MNQ backtest ----
d = json.load(open(NT_JSON, encoding="utf-8"))
res = d["result"]
rows = []
for tt in res["trades"]:
    e, x = tt["entry"], tt["exit"]
    rows.append({"dir": 1 if e["market_position"] == "Long" else -1,
                 "entry_time": pd.Timestamp(e["time"]), "entry_px": e["price"],
                 "exit_time": pd.Timestamp(x["time"]), "exit_px": x["price"],
                 "pnl": tt["ProfitCurrency"]})
nt = pd.DataFrame(rows).sort_values("entry_time").reset_index(drop=True)

OFFSET = pd.Timedelta(minutes=3)
nt["entry_time_open"] = nt["entry_time"] - OFFSET
bar_to_sessdate = dict(zip(bars_dev["time"], bars_dev["sess_date"]))
ntd = nt.copy()
ntd["sess"] = ntd["exit_time"].map(bar_to_sessdate)
n_unmapped = int(ntd["sess"].isna().sum())
if n_unmapped:
    ntd.loc[ntd["sess"].isna(), "sess"] = ntd.loc[ntd["sess"].isna(), "exit_time"].dt.date.astype(str)
nt_daily = ntd.groupby("sess")["pnl"].sum()
nt_daily.index = pd.to_datetime(nt_daily.index)
calu = py_daily.index.union(nt_daily.index)
pa = py_daily.reindex(calu).fillna(0.0); na = nt_daily.reindex(calu).fillna(0.0)
daily_corr = pa.corr(na)
net_py, net_nt = pa.sum(), na.sum()
net_delta_pct = (net_nt - net_py) / abs(net_py) * 100
max_abs_delta = (na - pa).abs().max()
ntk = set(zip(nt["entry_time_open"], nt["dir"]))
pyk = set(zip(pyt["entry_time"], pyt["dir"]))
inter = ntk & pyk
matched_pct = 100 * len(inter) / max(len(nt), 1)
dd_ = (na - pa).abs().sort_values(ascending=False)

parity2 = {
    "instrument": "MNQ_genuine_price_reference",
    "reference_construction": "MNQU6 fills sourced from BarExportV1 (real Strategy Analyzer "
        "engine export), signal math (M) still from NQ per the frozen rule -- fixes the "
        "diagnosed NQ-scaled-price approximation flagged in this run's REPORT.md",
    "n_missing_bars_on_nq_grid": n_missing, "n_ffilled": n_ffilled,
    "py_trades": len(pyt), "nt_trades": len(nt),
    "matched_entry_time_dir": len(inter), "matched_pct": matched_pct,
    "daily_corr": daily_corr, "net_py": float(net_py), "net_nt": float(net_nt),
    "net_delta_pct": net_delta_pct, "max_abs_daily_delta": float(max_abs_delta),
    "pass_decision_parity_995": matched_pct >= 99.5,
    "pass_daily_corr_0999": bool(daily_corr >= 0.999),
    "pass_net_diff_lt_05pct": bool(abs(net_delta_pct) <= 0.5),
    "worst5_daily_deltas": {str(k): v for k, v in dd_.head(5).to_dict().items()},
}
print(json.dumps({k: v for k, v in parity2.items() if k != "worst5_daily_deltas"}, indent=2, default=str))
with open(f"{OUT}/parity_mnq_genuine.json", "w") as f:
    json.dump(parity2, f, indent=2, default=str)

battery = dd_battery(na.index, na.to_numpy(), label="MNQ_Final_NT_vs_genuine_ref")
sm = sm_metrics.metrics(na)
battery.update({"trade_count": len(nt), "es5_daily": sm.get("es5_daily"),
                 "worst_week": sm.get("worst_week")})
with open(f"{OUT}/metric_battery_mnq_genuine.json", "w") as f:
    json.dump(battery, f, indent=2, default=str)
print("DONE")
