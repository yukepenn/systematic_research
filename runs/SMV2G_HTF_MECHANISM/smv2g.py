"""SMV2G — HTF tilt mechanism plateau test (seq 335-342). Identical x1.25 up-weight,
identical implementable rounding, 8 neighbor daily-state definitions. NO selection."""
import sys, os
import numpy as np, pandas as pd
sys.path.insert(0, "src/analytics")
from sm01_solarsim import load_bars_3m, _fill
from smv2_common import dd_battery

OUT = "runs/SMV2G_HTF_MECHANISM/out"; os.makedirs(OUT, exist_ok=True)
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
tgt = bp["tgt"].to_numpy().astype(float)

sclose = bars.loc[bars["is_last_of_sess"], ["sess_date", "close"]].set_index("sess_date")["close"]

def sma_state(w): return np.sign(sclose - sclose.rolling(w).mean())
def ema_state(w): return np.sign(sclose - sclose.ewm(span=w, adjust=False).mean())
def donch_state(w):
    mid = (sclose.rolling(w).max() + sclose.rolling(w).min()) / 2
    return np.sign(sclose - mid)
def ret_state(w): return np.sign(sclose - sclose.shift(w))
def slope_state(w, k):
    sma = sclose.rolling(w).mean()
    return np.sign(sma - sma.shift(k))

states = {
    "n1_SMA20": sma_state(20), "n2_SMA100": sma_state(100), "n3_EMA50": ema_state(50),
    "n4_Donchian50mid": donch_state(50), "n5_ret50": ret_state(50), "n6_ret100": ret_state(100),
    "n7_SMA50slope5": slope_state(50, 5),
}
s50, s200 = sma_state(50), sma_state(200)
dual = pd.Series(np.where((s50 == s200), s50, 0.0), index=s50.index)
states["n8_dual_SMA50and200"] = dual
states["ref_SMA50"] = s50  # reproduction check only

dev_np = dev.to_numpy()
base = sim(bars_dev, np.clip(rha(tgt[dev_np] * 0.9026), -13, 13))
b0 = dd_battery(base.index, base.values, label="base_x0.9026")
print("base: net %.0f sharpe %.3f maxDD %.0f" % (b0["net"], b0["sharpe"], b0["maxDD_eod"]))

rows = [dict(b0)]
for name, st in states.items():
    stp = st.shift(1).to_dict()
    st_bar = np.array([stp.get(d, np.nan) for d in bars["sess_date"]])
    agree = (np.sign(tgt) != 0) & (st_bar == np.sign(tgt))
    Tp = np.clip(rha(tgt * np.where(agree, 1.25, 1.0) * 0.9026), -13, 13)
    d = sim(bars_dev, Tp[dev_np])
    b = dd_battery(d.index, d.values, label=name)
    b["dSharpe_vs_base"] = b["sharpe"] - b0["sharpe"]
    b["dNetDD"] = (b["net"] / b["maxDD_eod"]) - (b0["net"] / b0["maxDD_eod"])
    rows.append(b)
    print("%-22s net %8.0f  sharpe %.3f (%+.3f)  maxDD %8.0f" % (
        name, b["net"], b["sharpe"], b["dSharpe_vs_base"], b["maxDD_eod"]))
df = pd.DataFrame(rows).set_index("label")
df[["net", "sharpe", "dSharpe_vs_base", "maxDD_eod", "worst_month", "calmar"]].to_csv(f"{OUT}/results.csv")
imp = df["dSharpe_vs_base"].drop(index=["base_x0.9026", "ref_SMA50"], errors="ignore") > 0
print("\nneighbors improving Sharpe: %d / %d  (mechanism gate: >=6/8)" % (imp.sum(), len(imp)))
