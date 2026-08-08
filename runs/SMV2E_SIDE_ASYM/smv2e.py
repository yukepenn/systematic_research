"""SMV2E — long/short asymmetry on Solar E10 (seq 328-334). Integer-contract implementable:
short targets scaled then rounded; replayed through the certified net-change executor."""
import sys, os
import numpy as np, pandas as pd
sys.path.insert(0, "src/analytics")
from sm01_solarsim import load_bars_3m, _fill
from smv2_common import dd_battery, boot_ci_mean

OUT = "runs/SMV2E_SIDE_ASYM/out"; os.makedirs(OUT, exist_ok=True)
MNQ_COMM, MNQ_PV = 0.65, 2.0

def rha(x): return np.sign(x) * np.floor(np.abs(x) + 0.5)

def sim(bars, tgt):
    n = len(bars)
    o = bars["open"].to_numpy(); h = bars["high"].to_numpy(); l = bars["low"].to_numpy()
    c = bars["close"].to_numpy(); last = bars["is_last_of_sess"].to_numpy()
    sd = bars["sess_date"].to_numpy()
    cash = 0.0; p = 0; pend = 0; daily = {}; prev = 0.0
    for t in range(n):
        if pend != p:
            d = pend - p; side = 1 if d > 0 else -1
            px = _fill(o[t], h[t], l[t], side)
            cash -= d * px * MNQ_PV; cash -= abs(d) * MNQ_COMM
            p = pend
        if last[t] and p != 0:
            side = -1 if p > 0 else 1
            px = _fill(o[t], h[t], l[t], side, at_close=c[t])
            cash += p * px * MNQ_PV; cash -= abs(p) * MNQ_COMM
            p = 0; pend = 0
        else:
            pend = int(tgt[t])
        if last[t]:
            eq = cash + p * c[t] * MNQ_PV
            daily[sd[t]] = eq - prev; prev = eq
    s = pd.Series(daily); s.index = pd.to_datetime(s.index); return s

bars = load_bars_3m()
sess = pd.to_datetime(bars["sess_date"]); dev = sess <= pd.Timestamp("2026-05-31")
bars_dev = bars[dev].reset_index(drop=True)
bp = pd.read_parquet("runs/SM01_SUBSTRATE/out/e10_bar_pnl.parquet")
tgt = bp["tgt"].to_numpy()[dev.to_numpy()].astype(float)

# HTF state (SMA50 prior-session, smv2a reconstruction)
sclose = bars.loc[bars["is_last_of_sess"], ["sess_date", "close"]].set_index("sess_date")["close"]
state = np.sign(sclose - sclose.rolling(50).mean()).shift(1).to_dict()
st_bar = np.array([state.get(d, np.nan) for d in bars_dev["sess_date"]])

arms = {}
for s_mult, name in [(1.0, "s100"), (0.75, "s75"), (0.5, "s50"), (0.25, "s25"), (0.0, "s0_longonly")]:
    arms[name] = np.where(tgt < 0, rha(tgt * s_mult), tgt)
arms["c1_htfup_short50"] = np.where((tgt < 0) & (st_bar > 0), rha(tgt * 0.5), tgt)
arms["c2_counterHTF_50"] = np.where(((tgt < 0) & (st_bar > 0)) | ((tgt > 0) & (st_bar < 0)),
                                    rha(tgt * 0.5), tgt)

# session returns for crisis days
scl = sclose.copy(); sret = scl.pct_change()
sret_dev = sret[sret.index <= pd.Timestamp("2026-05-31").date()]
worst20 = pd.to_datetime(pd.Series(sret_dev.nsmallest(20).index))

res, dailies = [], {}
for name, tg in arms.items():
    d = sim(bars_dev, tg)
    dailies[name] = d
    b = dd_battery(d.index, d.values, label=name)
    b["net_2022"] = d[d.index.year == 2022].sum()
    b["crisis20_net"] = d[d.index.isin(worst20)].sum()
    res.append(b)
df = pd.DataFrame(res).set_index("label")
ref22, refcr = df.loc["s100", "net_2022"], df.loc["s100", "crisis20_net"]
df["crisis_retention"] = df["crisis20_net"] / refcr
df["equal_vol_maxDD"] = df["maxDD_eod"] * (df.loc["s100", "daily_vol"] / df["daily_vol"])
keep = ["net", "sharpe", "calmar", "maxDD_eod", "equal_vol_maxDD", "worst_month",
        "net_2022", "crisis20_net", "crisis_retention", "pos_month_pct"]
df[keep].to_csv(f"{OUT}/results.csv")
print(df[keep].round(2).to_string())
pd.DataFrame(dailies).to_csv(f"{OUT}/daily_curves.csv")
