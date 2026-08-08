"""SMV2M twin — Python twin of SolarWaveSMMaster_v1 (DAYONLY_DUAL6040 consolidated master).

Frozen spec: runs/SMV2M_MASTER_BUILD/spec.yaml (seq 371). NO alpha choices here:
Tpp construction verbatim from committed runs/SMV2H_ONECONTRACT/smv2h.py; B-MOM pending-position
generator copied VERBATIM from the same file (certified vs frozen generator 1333/1333);
K_SOLAR/K_BMOM derived from committed rerank_curves.csv (reproduction verified at freeze).
"""
import sys, os
import numpy as np, pandas as pd

sys.path.insert(0, "src/analytics")
from sm01_solarsim import load_bars_3m, _fill
from sm_bmom import rth_3m, BAND_DAYS
from smv2_common import dd_battery

OUT = "runs/SMV2M_MASTER_BUILD/out"; os.makedirs(OUT, exist_ok=True)
K_SOLAR, K_BMOM = 0.728654, 2.934159          # frozen, spec.yaml
MNQ_COMM, MNQ_PV = 0.65, 2.0

def rha(x): return np.sign(x) * np.floor(np.abs(x) + 0.5)

# ---------------- substrate (identical to smv2h.py) ----------------
print("substrate ...")
bars = load_bars_3m()
sess = pd.to_datetime(bars["sess_date"]); dev = (sess <= pd.Timestamp("2026-05-31")).to_numpy()
bp = pd.read_parquet("runs/SM01_SUBSTRATE/out/e10_bar_pnl.parquet")
T = bp["tgt"].to_numpy().astype(float)
sclose = bars.loc[bars["is_last_of_sess"], ["sess_date", "close"]].set_index("sess_date")["close"]
htf = np.sign(sclose - sclose.rolling(50).mean()).shift(1).to_dict()
st_bar = np.array([htf.get(d, np.nan) for d in bars["sess_date"]])
agree = (np.sign(T) != 0) & (st_bar == np.sign(T))
m = np.where(agree, 1.25, 1.0)
s = np.where((T < 0) & (st_bar > 0), 0.5, 1.0)
Tpp = np.clip(rha(T * m * s * 0.9026), -13, 13)

# ---------------- B-MOM pending positions (VERBATIM copy of smv2h.py bmom_pos_series) ----------------
def bmom_pos_series(bars3):
    r = rth_3m(bars3)
    pos_arr = np.zeros(len(bars3))
    hist, day_count = {}, 0
    for d, g in r.groupby("date", sort=True):
        g = g.sort_values("hm")
        if g["hm"].iloc[0] != 933:
            continue
        open0930 = g["open"].iloc[0]
        close = g["close"].to_numpy(); vol = g["volume"].to_numpy(); hm = g["hm"].to_numpy()
        vwap = np.cumsum(close * vol) / np.maximum(np.cumsum(vol), 1e-9)
        gidx = g.index.to_numpy()
        pos = 0
        flat_hm = int(hm[hm <= 1557].max()) if (hm <= 1557).any() else None
        if day_count >= BAND_DAYS:
            for i in range(len(g)):
                h = int(hm[i])
                if flat_hm is not None and h == flat_hm:
                    pos = 0
                    pos_arr[gidx[i]] = pos
                    break
                if h > 1554:
                    pos_arr[gidx[i]] = pos
                    continue
                past = hist.get(h)
                if past is not None and len(past) >= 1:
                    m_tod = float(np.mean(past[-BAND_DAYS:]))
                    upper, lower = open0930 + m_tod, open0930 - m_tod
                    if close[i] > max(upper, vwap[i]): pos = 1
                    elif close[i] < min(lower, vwap[i]): pos = -1
                pos_arr[gidx[i]] = pos
        for i in range(len(g)):
            hist.setdefault(int(hm[i]), []).append(abs(close[i] - open0930))
        day_count += 1
    return pos_arr

print("bmom state ...")
B = bmom_pos_series(bars)

# ---------------- consolidated target + frozen ops rule ----------------
M_raw = np.clip(rha(K_SOLAR * Tpp + K_BMOM * B), -13, 13)

hm = (bars["time"].dt.hour * 10000 + bars["time"].dt.minute * 100 +
      bars["time"].dt.second).to_numpy()          # NT END-stamp convention

def ops_target(M_t, cur, hm_t):
    if 163900 <= hm_t < 180000:
        return 0
    if 163000 <= hm_t < 180000:                   # no increases / no reversal entries
        if M_t == 0:
            return 0
        if cur == 0:
            return 0
        if np.sign(M_t) != np.sign(cur):
            return 0
        return cur if abs(M_t) > abs(cur) else int(M_t)
    return int(M_t)

# ---------------- executor (rerank sim() semantics + multi-contract net change) ----------------
print("executor ...")
o = bars["open"].to_numpy(); h = bars["high"].to_numpy(); l = bars["low"].to_numpy()
c = bars["close"].to_numpy(); last = bars["is_last_of_sess"].to_numpy()
sd = bars["sess_date"].to_numpy()
n = len(bars)
cash = 0.0; p = 0; pend = 0; prev_eq = 0.0
daily = {}
ledger = np.zeros((n, 5))                          # Tpp, B, M_raw, tgt_ops, pos_after
fills = []
for t in range(n):
    if pend != p:                                  # fill at THIS bar open (+-1 tick capped)
        d = pend - p; side = 1 if d > 0 else -1
        px = _fill(o[t], h[t], l[t], side)
        cash -= d * px * MNQ_PV; cash -= abs(d) * MNQ_COMM
        fills.append((bars["time"].iloc[t], d, px))
        p = pend
    if last[t] and p != 0:                         # session-close backstop exit AT close
        side = -1 if p > 0 else 1
        px = _fill(o[t], h[t], l[t], side, at_close=c[t])
        cash += p * px * MNQ_PV; cash -= abs(p) * MNQ_COMM
        fills.append((bars["time"].iloc[t], -p, px))
        p = 0; pend = 0
    else:
        pend = ops_target(int(M_raw[t]), p, int(hm[t]))
    ledger[t] = (Tpp[t], B[t], M_raw[t], pend, p)
    if last[t]:
        eq = cash + p * c[t] * MNQ_PV
        daily[sd[t]] = eq - prev_eq; prev_eq = eq

twin = pd.Series(daily); twin.index = pd.to_datetime(twin.index)
twin.to_csv(f"{OUT}/twin_daily.csv")
led = pd.DataFrame(ledger, columns=["Tpp", "B", "M_raw", "tgt_ops", "pos"])
led.insert(0, "time", bars["time"].to_numpy()); led["sess_date"] = sd
led.to_parquet(f"{OUT}/twin_bar_ledger.parquet")
pd.DataFrame(fills, columns=["time", "delta", "price"]).to_csv(f"{OUT}/twin_fills.csv", index=False)

# ---------------- reads: dev metrics + budget vs research champion ----------------
twin_dev = twin[twin.index <= "2026-05-31"]
rc = pd.read_csv("runs/SMV2H_ONECONTRACT/out/rerank_curves.csv", parse_dates=["sess"]).set_index("sess")
champ = rc["60_40"].reindex(twin_dev.index)

bat_twin = dd_battery(twin_dev.index, twin_dev.values, label="MASTER_TWIN_dev")
bat_champ = dd_battery(champ.index, champ.values, label="RESEARCH_60_40_dev")
bat = pd.DataFrame([bat_twin, bat_champ]).set_index("label")
bat.to_csv(f"{OUT}/twin_battery.csv")

corr = float(np.corrcoef(twin_dev.values, champ.values)[0, 1])
ret = float(twin_dev.sum() / champ.sum())
sig_ratio = float(twin_dev.std(ddof=1) / champ.std(ddof=1))
res = {"daily_corr_vs_research": corr, "net_retention": ret, "sigma_ratio": sig_ratio,
       "twin_net_dev": float(twin_dev.sum()), "champ_net_dev": float(champ.sum()),
       "twin_maxDD": float(bat_twin.get("maxDD_eod", np.nan)),
       "champ_maxDD": float(bat_champ.get("maxDD_eod", np.nan)),
       "n_fills": len(fills), "max_abs_target": int(np.abs(M_raw).max())}
pd.Series(res).to_csv(f"{OUT}/twin_vs_research.csv")
print(pd.Series(res).to_string())
cols = ["net", "sharpe", "maxDD_eod", "CDaR5", "worst_month", "longest_TUW_days"]
print(bat[[c_ for c_ in cols if c_ in bat.columns]].round(2).to_string())
