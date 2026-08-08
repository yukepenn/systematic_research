"""V2 frontier re-rank: DUAL_HTF Solar core + BMOM E2, weight plateau per directive §24."""
import sys, os
import numpy as np, pandas as pd
sys.path.insert(0, "src/analytics")
from sm01_solarsim import load_bars_3m, _fill
from smv2_common import dd_battery, boot_ci_mean

OUT = "runs/SMV2H_ONECONTRACT/out"
def rha(x): return np.sign(x) * np.floor(np.abs(x) + 0.5)

bars = load_bars_3m()
sess = pd.to_datetime(bars["sess_date"]); dev = sess <= pd.Timestamp("2026-05-31")
bars_dev = bars[dev].reset_index(drop=True)
bp = pd.read_parquet("runs/SM01_SUBSTRATE/out/e10_bar_pnl.parquet")
T = bp["tgt"].to_numpy().astype(float)
sclose = bars.loc[bars["is_last_of_sess"], ["sess_date", "close"]].set_index("sess_date")["close"]
htf = np.sign(sclose - sclose.rolling(50).mean()).shift(1).to_dict()
st_bar = np.array([htf.get(d, np.nan) for d in bars["sess_date"]])
agree = (np.sign(T) != 0) & (st_bar == np.sign(T))
Tpp = np.clip(rha(T * np.where(agree, 1.25, 1.0) * np.where((T < 0) & (st_bar > 0), 0.5, 1.0) * 0.9026), -13, 13)

def sim(bars, tgt, comm=0.65, pv=2.0):
    n = len(bars)
    o = bars["open"].to_numpy(); h = bars["high"].to_numpy(); l = bars["low"].to_numpy()
    c = bars["close"].to_numpy(); last = bars["is_last_of_sess"].to_numpy()
    sd = bars["sess_date"].to_numpy()
    cash = 0.0; p = 0; pend = 0; daily = {}; prev = 0.0
    for t in range(n):
        if pend != p:
            d = pend - p; side = 1 if d > 0 else -1
            px = _fill(o[t], h[t], l[t], side)
            cash -= d * px * pv; cash -= abs(d) * comm
            p = pend
        if last[t] and p != 0:
            side = -1 if p > 0 else 1
            px = _fill(o[t], h[t], l[t], side, at_close=c[t])
            cash += p * px * pv; cash -= abs(p) * comm; p = 0; pend = 0
        else:
            pend = int(tgt[t])
        if last[t]:
            eq = cash + p * c[t] * pv
            daily[sd[t]] = eq - prev; prev = eq
    s = pd.Series(daily); s.index = pd.to_datetime(s.index); return s

DUAL = sim(bars_dev, Tpp[dev.to_numpy()])
DUAL.to_csv(f"{OUT}/solar_dual_htf_daily.csv")
cal = DUAL.index
bm2 = pd.read_parquet("runs/SMV2B_BMOM_EXEC_AUDIT/out/ledger_E2_next_open.parquet")
BM = (bm2.groupby("sess")["net_c1_ticks"].sum() * 5.0)
BM.index = pd.to_datetime(BM.index); BM = BM.reindex(cal).fillna(0.0)

SIG = DUAL.std(ddof=1)
def vm(x): return x * (SIG / x.std(ddof=1))
rows = []
curves = {}
for wname, ws, wb in [("80_20", .8, .2), ("70_30", .7, .3), ("60_40", .6, .4), ("50_50", .5, .5)]:
    p = vm(ws * DUAL + wb * vm(BM))
    b = dd_battery(cal, p.values, label=f"DAYONLY_DUAL_BMOM_{wname}")
    rows.append(b); curves[wname] = p
# references on same equal-vol basis
old = pd.read_csv("runs/SMV2C_B1_ABLATION/out/curves.csv", parse_dates=["sess"]).set_index("sess")
for ref in ["P1_tilt+bmom_625_375", "P3_tilt+bmom+b1_532"]:
    r = old[ref] * (SIG / old[ref].std(ddof=1))
    rows.append(dd_battery(old.index, r.values, label=ref))
rows.append(dd_battery(cal, vm(DUAL).values, label="SOLAR_DUAL_HTF_alone"))
df = pd.DataFrame(rows).set_index("label")
keep = ["net", "sharpe", "sortino", "calmar", "maxDD_eod", "CDaR5", "worst_month",
        "rolling60_min", "longest_TUW_days", "pos_month_pct", "pos_week_pct"]
print(df[keep].round(2).to_string())
df[keep].to_csv(f"{OUT}/rerank_portfolios.csv")
# plateau-center candidate vs old P1
best = vm(0.7 * DUAL + 0.3 * vm(BM))
diff = best.values - old["P1_tilt+bmom_625_375"].reindex(cal).fillna(0).values * (SIG / old["P1_tilt+bmom_625_375"].std(ddof=1))
lo, hi, p = boot_ci_mean(diff, n_boot=4000)
print(f"\n70/30 DUAL vs old P1 (equal vol): mean {diff.mean():+.1f}/d  P(>0)={p:.3f}")
pd.DataFrame({"sess": cal, **{k: v.values for k, v in curves.items()}, "DUAL": DUAL.values,
              "BM_E2": BM.values}).to_csv(f"{OUT}/rerank_curves.csv", index=False)
