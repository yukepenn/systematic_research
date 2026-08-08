"""SM06 — frozen champion on 2006-2021. Run AFTER spec.yaml committed."""
import sys, time, json, os
sys.path.insert(0, "src/analytics")
import numpy as np, pandas as pd
import sm01_solarsim as sm
import sm_metrics as smm

OUT = "runs/SM06_SOLAR_HISTORY/out"
os.makedirs(OUT, exist_ok=True)
t0 = time.time()

h = pd.read_parquet("research/scalping_lab/substrate/minute/NQ/nq1m_2005_202605.parquet")
h["time"] = pd.to_datetime(h["time"])
h = h[h["time"] < "2022-01-01"].reset_index(drop=True)
bars = sm.resample_3m(h)
print("hist 3m bars:", len(bars), bars.time.min(), "->", bars.time.max(), flush=True)

close = bars.close.to_numpy()
sig = sm.sigma_series(close)
POS, PEND = [], []
trades_all = []
high = bars.high.to_numpy(); low = bars.low.to_numpy()
for vm in sm.VMS:
    is_up, flip, s_eff, anchor = sm.member_states(close, sig, float(vm))
    fills, pos, pend = sm.member_trades(bars, is_up, flip, s_eff, anchor)
    POS.append(pos); PEND.append(pend)
    tr = sm.fills_to_trades(fills)
    tr["vm"] = vm
    mfe = np.empty(len(tr)); mae = np.empty(len(tr))
    for i, r in enumerate(tr.itertuples()):
        hi_ = high[r.entry_bar:r.exit_bar+1]; lo_ = low[r.entry_bar:r.exit_bar+1]
        if r.side == 1:
            mfe[i] = (hi_ - r.entry_px).max(); mae[i] = (r.entry_px - lo_).max()
        else:
            mfe[i] = (r.entry_px - lo_).max(); mae[i] = (hi_ - r.entry_px).max()
    tr["mfe_pts"] = mfe; tr["mae_pts"] = mae
    tr["bars_held"] = tr.exit_bar - tr.entry_bar
    trades_all.append(tr)
    print(f"vm{vm}: {len(tr)} trades", flush=True)

pend = np.column_stack(PEND); pos = np.column_stack(POS)
trades = pd.concat(trades_all, ignore_index=True)
trades["entry_sess"] = bars.sess_date.to_numpy()[trades.entry_bar]
trades["exit_sess"] = bars.sess_date.to_numpy()[trades.exit_bar]
trades.to_parquet(f"{OUT}/member_trades_hist.parquet", index=False)

vote = pd.DataFrame({
    "time": bars.time, "sess_date": bars.sess_date, "close": bars.close,
    "sess_id": bars.sess_id, "is_last_of_sess": bars.is_last_of_sess,
    "sigma460": sig, "vote_pos": pos.sum(axis=1), "vote_pend": pend.sum(axis=1),
    "flips_bar": 0,
})
vote.to_parquet(f"{OUT}/vote_state_3m_hist.parquet", index=False)

tgt = sm.e10_target(pend)
daily = sm.e10_sim(bars, tgt)
daily.to_csv(f"{OUT}/e10_daily_hist.csv", index=False)

# stats
daily["sess"] = pd.to_datetime(daily["sess"])
d = daily.set_index("sess")["net"]
d = d.iloc[20:]  # warmup exclusion per spec
x = d.to_numpy()

rng = np.random.default_rng(20260808)
n = len(x); block = 5; nb = int(np.ceil(n/block))
means = np.empty(10_000)
for i in range(10_000):
    st = rng.integers(0, n, nb)
    idx = (st[:, None] + np.arange(block)[None, :]).ravel() % n
    means[i] = x[idx[:n]].mean()
ci_lo, ci_hi = np.percentile(means, [2.5, 97.5])

yearly = d.groupby(d.index.year).sum()
blocks = {"2006-09": d["2006":"2009"].sum(), "2010-13": d["2010":"2013"].sum(),
          "2014-17": d["2014":"2017"].sum(), "2018-21": d["2018":"2021"].sum()}
block_ci = {}
for name, years in [("2006-09", ("2006", "2009")), ("2010-13", ("2010", "2013")),
                    ("2014-17", ("2014", "2017")), ("2018-21", ("2018", "2021"))]:
    xx = d[years[0]:years[1]].to_numpy()
    nn = len(xx); nbb = int(np.ceil(nn/block))
    ms = np.empty(5000)
    for i in range(5000):
        st = rng.integers(0, nn, nbb)
        idx = (st[:, None] + np.arange(block)[None, :]).ravel() % nn
        ms[i] = xx[idx[:nn]].mean()
    block_ci[name] = (float(np.percentile(ms, 2.5)), float(np.percentile(ms, 97.5)))

m = smm.metrics(d)
n_pos_years = int((yearly > 0).sum())

# frozen interpretation
if x.mean() > 0 and ci_lo > 0 and n_pos_years >= 10:
    verdict = "STRUCTURAL"
elif x.mean() > 0 and not any(hi < 0 for lo, hi in block_ci.values()):
    verdict = "REGIME_SENSITIVE_POSITIVE"
elif ci_hi < 0:
    verdict = "CONTRADICTED"
else:
    verdict = "REGIME_LOCAL"

res = {
    "n_sessions": int(n), "net_total": float(x.sum()),
    "mean_daily": float(x.mean()), "ci_lo": float(ci_lo), "ci_hi": float(ci_hi),
    "pos_years": n_pos_years, "years": {int(k): float(v) for k, v in yearly.items()},
    "blocks": {k: float(v) for k, v in blocks.items()},
    "block_ci": block_ci, "sharpe": m["sharpe"], "max_dd": m["max_dd"],
    "verdict": verdict, "runtime_s": round(time.time()-t0, 1),
}
with open(f"{OUT}/result.json", "w") as f:
    json.dump(res, f, indent=2)
print(json.dumps(res, indent=2))
