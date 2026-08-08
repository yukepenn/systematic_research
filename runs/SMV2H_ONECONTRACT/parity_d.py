"""Track D: OneLot Strategy Analyzer parity — NT full-window trades vs canonical Python replay."""
import json, sys
import numpy as np, pandas as pd
sys.path.insert(0, "src/analytics")
from sm01_solarsim import load_bars_3m, _fill
from sm_bmom import rth_3m, BAND_DAYS

NTJSON = r"C:\Users\Yuke Zhang\.claude\projects\D--OneDrive---Washington-University-in-St--Louis-TradingResearch-systematic-research\bfb80633-2ca8-4554-803e-2bd6cbeeb4c1\tool-results\mcp-crosstrade-GetMcpJob-1786200451076.txt"
OUT = "runs/SMV2H_ONECONTRACT/out"

d = json.load(open(NTJSON, encoding="utf-8"))
res = d["result"]
perf = res["performance"]["all"]
print("NT: NetProfit %.2f  trades %d  window %s -> %s" % (
    perf["NetProfit"], len(res["trades"]), res["from"], res["to"]))
rows = []
for t in res["trades"]:
    e, x = t["entry"], t["exit"]
    rows.append({"dir": 1 if e["market_position"] == "Long" else -1,
                 "entry_time": pd.Timestamp(e["time"]), "entry_px": e["price"],
                 "exit_time": pd.Timestamp(x["time"]), "exit_px": x["price"],
                 "pnl": t["ProfitCurrency"]})
nt = pd.DataFrame(rows).sort_values("entry_time").reset_index(drop=True)
nt.to_csv(f"{OUT}/nt_trades_full.csv", index=False)

# ---- python canonical replay with fill logging (SM14 form: old M, hyst 3/1, NQ) ----
def rha(x): return np.sign(x) * np.floor(np.abs(x) + 0.5)
bars = load_bars_3m()
sess = pd.to_datetime(bars["sess_date"]); dev = sess <= pd.Timestamp("2026-05-31")
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
o = bars_dev["open"].to_numpy(); h = bars_dev["high"].to_numpy(); l = bars_dev["low"].to_numpy()
c = bars_dev["close"].to_numpy(); last = bars_dev["is_last_of_sess"].to_numpy()
tm = bars_dev["time"]
hm_arr = tm.dt.hour.to_numpy() * 100 + tm.dt.minute.to_numpy()
NQ_COMM, NQ_PV = 2.18, 20.0
a_, b_ = 3, 1
cash = 0.0; p = 0; pend = 0
fills = []
sd = bars_dev["sess_date"].to_numpy()
daily = {}; prev = 0.0
for t in range(n):
    if pend != p:
        dta = pend - p; side = 1 if dta > 0 else -1
        px = _fill(o[t], h[t], l[t], side)
        cash -= dta * px * NQ_PV; cash -= abs(dta) * NQ_COMM
        # fill time = open of bar t = end-stamp of bar t-1; use bar t's END - 3min
        fills.append({"time_open": tm.iloc[t] - pd.Timedelta(minutes=3), "d": dta, "px": px})
        p = pend
    if last[t] and p != 0:
        side = -1 if p > 0 else 1
        px = _fill(o[t], h[t], l[t], side, at_close=c[t])
        cash += p * px * NQ_PV; cash -= abs(p) * NQ_COMM
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
        eq = cash + p * c[t] * NQ_PV
        daily[sd[t]] = eq - prev; prev = eq
py_daily = pd.Series(daily); py_daily.index = pd.to_datetime(py_daily.index)
pf = pd.DataFrame(fills)
print("PY: net %.2f  fills %d" % (py_daily.sum(), len(pf)))

# pair python fills into round trips
rt = []; pos = 0; ent = None
for _, f in pf.iterrows():
    d0 = int(f["d"])
    if pos == 0:
        pos = d0; ent = f
    else:
        if abs(d0) == 2:  # flip: close + open
            rt.append({"dir": pos, "entry_time": ent["time_open"], "entry_px": ent["px"],
                       "exit_time": f["time_open"], "exit_px": f["px"]})
            pos = pos + d0; ent = f
        else:
            rt.append({"dir": pos, "entry_time": ent["time_open"], "entry_px": ent["px"],
                       "exit_time": f["time_open"], "exit_px": f["px"]})
            pos = 0; ent = None
pyt = pd.DataFrame(rt)
pyt["pnl"] = (pyt["exit_px"] - pyt["entry_px"]) * pyt["dir"] * NQ_PV - 2 * NQ_COMM
pyt.to_csv(f"{OUT}/py_trades_full.csv", index=False)
print("PY round trips:", len(pyt))

# ---- reconcile ----
ntd = nt.copy()
ntd["sess"] = ntd["exit_time"].dt.date
nt_daily = ntd.groupby("sess")["pnl"].sum()
nt_daily.index = pd.to_datetime(nt_daily.index)
# align on union calendar
calu = py_daily.index.union(nt_daily.index)
pa = py_daily.reindex(calu).fillna(0.0); na = nt_daily.reindex(calu).fillna(0.0)
print("daily corr: %.6f" % pa.corr(na))
print("net: PY %.0f  NT %.0f  delta %.0f" % (pa.sum(), na.sum(), na.sum() - pa.sum()))
print("max |daily delta|: %.0f" % (na - pa).abs().max())
# time-matched trades
ntk = set(zip(nt["entry_time"], nt["dir"]))
pyk = set(zip(pyt["entry_time"], pyt["dir"]))
inter = ntk & pyk
print("trades: NT %d  PY %d  entry-time+dir matched %d (%.1f%%)" % (
    len(nt), len(pyt), len(inter), 100 * len(inter) / max(len(nt), 1)))
# largest daily mismatches
dd_ = (na - pa).abs().sort_values(ascending=False)
print("worst 5 daily deltas:"); print(dd_.head(5).to_string())
