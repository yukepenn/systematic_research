"""SM03 — disaster stop arms per frozen spec. Run AFTER spec committed."""
import sys, os, json, time
sys.path.insert(0, "src/analytics")
import numpy as np, pandas as pd
import sm01_solarsim as sm
import sm_metrics as smm

OUT = "runs/SM03B_DISASTER_STOP_INTRABAR/out"
os.makedirs(OUT, exist_ok=True)
DEV_END = pd.Timestamp("2026-05-31").date()
H1_END = pd.Timestamp("2024-03-31")

BANDS = {"fast": [6, 8, 10, 12], "mid": [14, 16, 18, 20, 22], "slow": [24, 26, 28, 30]}
ARMS = [
    (301, "mid_only_1.0",  {"mid": 1.0}),
    (302, "mid_only_1.25", {"mid": 1.25}),
    (303, "mid_slow_1.0",  {"mid": 1.0, "slow": 1.0}),
    (304, "mid_slow_1.25", {"mid": 1.25, "slow": 1.25}),
    (305, "tiered",        {"fast": 1.5, "mid": 1.0, "slow": 1.25}),
    (306, "all_1.25",      {"fast": 1.25, "mid": 1.25, "slow": 1.25}),
]

def band_of(vm):
    return next(b for b, vs in BANDS.items() if vm in vs)

def run_universe(bars, stop_map):
    """stop_map: band->m or {} for base. Returns (trades_df, pend_matrix)."""
    close = bars.close.to_numpy()
    sig = sm.sigma_series(close)
    PEND, trades = [], []
    for vm in sm.VMS:
        m = stop_map.get(band_of(vm))
        is_up, flip, s_eff, anchor = sm.member_states(close, sig, float(vm))
        fills, pos, pend = sm.member_trades(bars, is_up, flip, s_eff, anchor,
                                            stop_mult=m)
        PEND.append(pend)
        tr = sm.fills_to_trades(fills)
        tr["vm"] = vm
        trades.append(tr)
    tr = pd.concat(trades, ignore_index=True)
    tr["entry_sess"] = bars.sess_date.to_numpy()[tr.entry_bar]
    tr["exit_sess"] = bars.sess_date.to_numpy()[tr.exit_bar]
    return tr, np.column_stack(PEND)

def e10_daily(bars, pend):
    tgt = sm.e10_target(pend)
    d = sm.e10_sim(bars, tgt)
    d["sess"] = pd.to_datetime(d["sess"])
    return d.set_index("sess")["net"]

def evaluate(tag, bars_dev, base_tr, base_daily, stop_map, bars_hist, base_hist_daily):
    tr, pend = run_universe(bars_dev, stop_map)
    daily = e10_daily(bars_dev, pend)
    dev = daily[daily.index.date <= DEV_END]
    base_dev = base_daily[base_daily.index.date <= DEV_END]

    m_new = smm.metrics(dev); m_base = smm.metrics(base_dev)
    # matched-vol logG
    scale = smm.vol_match_scale(dev, base_dev.std(ddof=1))
    m_scaled = smm.metrics(dev * scale)

    # right-tail retention: match on (vm, entry_time)
    bt = base_tr[pd.to_datetime(base_tr.entry_time).dt.date <= DEV_END]
    nt = tr[pd.to_datetime(tr.entry_time).dt.date <= DEV_END]
    ret = smm.right_tail_retention(bt, nt, key=("vm", "entry_time"))
    # top-10 day retention
    top10 = base_dev.nlargest(10)
    ret10 = float(daily.reindex(top10.index).sum() / top10.sum())

    # H1/H2 delta (unscaled mean daily delta)
    delta = (dev - base_dev.reindex(dev.index).fillna(0))
    h1 = delta[delta.index <= H1_END].mean()
    h2 = delta[delta.index > H1_END].mean()

    # bootstrap P(dSharpe<=0)
    bb = smm.block_bootstrap_delta(dev.to_numpy(), base_dev.reindex(dev.index).fillna(0).to_numpy(),
                                   stat=lambda v: v.mean()/ (v.std(ddof=1)+1e-12))
    # historical stress
    tr_h, pend_h = run_universe(bars_hist, stop_map)
    dh = e10_daily(bars_hist, pend_h)
    mh = smm.metrics(dh); mh_base = smm.metrics(base_hist_daily)

    n_stops = int((nt.exit_reason.str.contains("DisasterStop")).sum())
    row = {
        "arm": tag, "n_stops_dev": n_stops,
        "net": m_new["net"], "d_net": m_new["net"] - m_base["net"],
        "sharpe": m_new["sharpe"], "d_sharpe": m_new["sharpe"] - m_base["sharpe"],
        "logG_mv": m_scaled["logG_100k"], "d_logG_mv": m_scaled["logG_100k"] - m_base["logG_100k"],
        "max_dd": m_new["max_dd"], "d_max_dd_pct": (m_new["max_dd"] - m_base["max_dd"]) / abs(m_base["max_dd"]) * 100,
        "es5": m_new["es5_daily"], "d_es5_pct": (m_new["es5_daily"] - m_base["es5_daily"]) / abs(m_base["es5_daily"]) * 100,
        "worst_month": m_new["worst_month"], "d_wm_pct": (m_new["worst_month"] - m_base["worst_month"]) / abs(m_base["worst_month"]) * 100,
        "top1pct_retention": ret["retention"], "top10day_retention": ret10,
        "h1_delta": h1, "h2_delta": h2, "p_dsharpe_leq0": bb["p_leq_0"],
        "hist_max_dd": mh["max_dd"], "hist_d_dd_pct": (mh["max_dd"] - mh_base["max_dd"]) / abs(mh_base["max_dd"]) * 100,
        "hist_net": mh["net"], "hist_base_net": mh_base["net"],
    }
    return row

t0 = time.time()
bars_dev = sm.load_bars_3m()
h = pd.read_parquet("research/scalping_lab/substrate/minute/NQ/nq1m_2005_202605.parquet")
h["time"] = pd.to_datetime(h["time"])
bars_hist = sm.resample_3m(h[h["time"] < "2022-01-01"].reset_index(drop=True))

base_tr, base_pend = run_universe(bars_dev, {})
base_daily = e10_daily(bars_dev, base_pend)
_, base_pend_h = run_universe(bars_hist, {})
base_hist_daily = e10_daily(bars_hist, base_pend_h)
print("base ready", round(time.time()-t0, 1), flush=True)

rows = []
for seq, tag, stop_map in ARMS:
    r = evaluate(tag, bars_dev, base_tr, base_daily, stop_map, bars_hist, base_hist_daily)
    r["seq"] = seq
    rows.append(r)
    print(tag, "done", round(time.time()-t0, 1), flush=True)

df = pd.DataFrame(rows)
df.to_csv(f"{OUT}/results.csv", index=False)
pd.set_option("display.width", 250)
print(df.round(3).to_string(index=False))
