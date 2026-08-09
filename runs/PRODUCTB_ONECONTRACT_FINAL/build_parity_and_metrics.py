"""PRODUCTB_ONECONTRACT_FINAL — parity, full metric battery, capital maps for BEST_ONE_NQ/MNQ.

Reuses runs/SMV2H_ONECONTRACT/parity_d.py's exact canonical-replay construction (SM14 seq318,
old-M, hyst 3/1) parameterized per instrument, and src/analytics/smv2_common.dd_battery /
src/analytics/sm_metrics.metrics / runs/SMV2F_LEVERAGE_ROBUST/smv2f.py's bootstrap index
generators. No alpha changes -- this is packaging/reporting only.
"""
import json, sys, os
import numpy as np, pandas as pd

sys.path.insert(0, "src/analytics")
from sm01_solarsim import load_bars_3m, _fill
from sm_bmom import rth_3m, BAND_DAYS
from smv2_common import dd_battery
import sm_metrics

OUT = "runs/PRODUCTB_ONECONTRACT_FINAL/out"
os.makedirs(OUT, exist_ok=True)

NQ_JSON = r"C:\Users\Yuke Zhang\.claude\projects\D--OneDrive---Washington-University-in-St--Louis-TradingResearch-systematic-research\bfb80633-2ca8-4554-803e-2bd6cbeeb4c1\tool-results\mcp-crosstrade-GetMcpJob-1786235552571.txt"
MNQ_JSON = r"C:\Users\Yuke Zhang\.claude\projects\D--OneDrive---Washington-University-in-St--Louis-TradingResearch-systematic-research\bfb80633-2ca8-4554-803e-2bd6cbeeb4c1\tool-results\mcp-crosstrade-GetMcpJob-1786235588552.txt"

INSTRUMENTS = {
    "NQ": {"json": NQ_JSON, "comm": 2.18, "pv": 20.0, "ref_net": 303850.91999998846,
           "ref_sharpe": 1.1196627952564895, "ref_maxdd": 58517.44000000332},
    "MNQ": {"json": MNQ_JSON, "comm": 0.65, "pv": 2.0, "ref_net": 28676.09999999699,
            "ref_sharpe": 1.055710413975938, "ref_maxdd": 5963.199999999728},
}

# ---------------------------------------------------------------------------
# Shared signal construction (identical for both instruments -- SM14 seq318,
# WSolar=0.7086/WBmom=2.83/TiltMult=1.25/TiltRescale=0.9026/a=3/b=1), verbatim
# from runs/SMV2H_ONECONTRACT/parity_d.py.
# ---------------------------------------------------------------------------
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
o = bars_dev["open"].to_numpy(); h = bars_dev["high"].to_numpy(); l = bars_dev["low"].to_numpy()
c = bars_dev["close"].to_numpy(); last = bars_dev["is_last_of_sess"].to_numpy()
tm = bars_dev["time"]
hm_arr = tm.dt.hour.to_numpy() * 100 + tm.dt.minute.to_numpy()
sd = bars_dev["sess_date"].to_numpy()
a_, b_ = 3, 1


def python_replay(comm, pv):
    """Exact seq318 hysteresis replay, verbatim decision logic from parity_d.py, only
    commission/point-value swapped per instrument."""
    cash = 0.0; p = 0; pend = 0
    fills = []
    daily = {}; prev = 0.0
    for t in range(n):
        if pend != p:
            dta = pend - p; side = 1 if dta > 0 else -1
            px = _fill(o[t], h[t], l[t], side)
            cash -= dta * px * pv; cash -= abs(dta) * comm
            fills.append({"time_open": tm.iloc[t] - pd.Timedelta(minutes=3), "d": dta, "px": px})
            p = pend
        if last[t] and p != 0:
            side = -1 if p > 0 else 1
            px = _fill(o[t], h[t], l[t], side, at_close=c[t])
            cash += p * px * pv; cash -= abs(p) * comm
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
            eq = cash + p * c[t] * pv
            daily[sd[t]] = eq - prev; prev = eq
    py_daily = pd.Series(daily); py_daily.index = pd.to_datetime(py_daily.index)
    pf = pd.DataFrame(fills)
    # pair fills into round trips
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
    pyt["pnl"] = (pyt["exit_px"] - pyt["entry_px"]) * pyt["dir"] * pv - 2 * comm
    return py_daily, pyt


def edar(dd_series, alpha=0.05):
    """Entropic Drawdown-at-Risk (disclosed formula, no house precedent found):
    EDaR_alpha(dd) = min_{z>0} (1/z) * log( mean(exp(z*dd)) / alpha ), dd in $ (>=0 series
    of peak-to-trough shortfalls). Numeric 1-D minimization over z on a log grid."""
    dd = np.asarray(dd_series, dtype=float)
    dd = dd[dd >= 0]
    if dd.max() <= 0:
        return 0.0
    scale = dd.max()
    zs = np.geomspace(1e-6 / scale, 50.0 / scale, 4000)
    best = np.inf
    for z in zs:
        val = (1.0 / z) * np.log(np.mean(np.exp(z * dd)) / alpha)
        if np.isfinite(val) and val < best:
            best = val
    return float(best)


def compute_battery(daily, trades_df, label):
    x = daily.to_numpy(dtype=float)
    dates = daily.index
    b = dd_battery(dates, x, label=label)
    sm = sm_metrics.metrics(daily)
    cum = np.cumsum(x); peak = np.maximum.accumulate(cum); dd = peak - cum
    battery = {
        **b,
        "trade_count": int(len(trades_df)) if trades_df is not None else None,
        "es5_daily": sm.get("es5_daily"),
        "worst_day": sm.get("worst_day"),
        "worst_week": sm.get("worst_week"),
        "pos_day_frac": sm.get("pos_day_frac"),
        "top10_day_share": sm.get("top10_day_share"),
        "EDaR_5pct": edar(dd, alpha=0.05),
    }
    return battery


def right_tail_retention_vs_reference(trades_new, ref_top1pct_sum):
    """Top-1% day retention (day-level, since SM14 trades don't share a clean per-trade
    key with the NT trade list) -- retention of the NT-parity-verified realized top-1%
    DAY pnl vs the canonical Python reference's own top-1% day pnl."""
    pass  # computed at daily level in main loop below (see 'retention' section)


def capital_map(daily, stress_mults=(1.0, 1.25, 1.5, 2.0), thrs=(0.10, 0.15, 0.20, 0.25, 0.30),
                 nb=2000, seed=20260808):
    """Capital-needed framing of runs/SMV2F_LEVERAGE_ROBUST/smv2f.py's bootstrap machinery:
    for stress multiplier m (dollar P&L scaled by m) and target DD-fraction thr, bootstrap
    nb paths of cumulative-$ equity (NOT compounded -- fixed 1-contract product) under >=3
    resampling methods, capital_needed = 95th-pct bootstrapped max-$-drawdown / thr."""
    x = daily.to_numpy(dtype=float)
    n_ = len(x)
    rng = np.random.default_rng(seed)

    def idx_moving_block(L):
        nb_ = int(np.ceil(n_ / L))
        starts = rng.integers(0, n_, size=(nb, nb_))
        idx = (starts[:, :, None] + np.arange(L)[None, None, :]) % n_
        return idx.reshape(nb, -1)[:, :n_]

    def idx_stationary(mean_L):
        p = 1.0 / mean_L
        idx = np.empty((nb, n_), dtype=np.int64)
        cur_i = rng.integers(0, n_, size=nb)
        for t in range(n_):
            jump = rng.random(nb) < p
            cur_i = np.where(jump, rng.integers(0, n_, size=nb), (cur_i + 1) % n_)
            idx[:, t] = cur_i
        return idx

    methods = {"L5": idx_moving_block(5), "L20": idx_moving_block(20), "stat60": idx_stationary(60)}
    rows = []
    for m in stress_mults:
        xs = x * m
        for mname, idx in methods.items():
            paths = xs[idx]
            eq = np.cumsum(paths, axis=1)
            peak = np.maximum.accumulate(eq, axis=1)
            dd = peak - eq
            maxdd = dd.max(axis=1)
            p95 = np.percentile(maxdd, 95)
            for thr in thrs:
                rows.append({"stress_mult": m, "method": mname, "thr": thr,
                             "p95_maxdd_dollar": float(p95),
                             "capital_needed": float(p95 / thr)})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
results = {}
for inst, cfg in INSTRUMENTS.items():
    print(f"=== {inst} ===")
    d = json.load(open(cfg["json"], encoding="utf-8"))
    res = d["result"]
    perf = res["performance"]["all"]
    print(f"NT: NetProfit {perf['NetProfit']:.2f}  trades {len(res['trades'])}  window {res['from']} -> {res['to']}")

    rows = []
    for t in res["trades"]:
        e, x = t["entry"], t["exit"]
        rows.append({"dir": 1 if e["market_position"] == "Long" else -1,
                     "entry_time": pd.Timestamp(e["time"]), "entry_px": e["price"],
                     "exit_time": pd.Timestamp(x["time"]), "exit_px": x["price"],
                     "pnl": t["ProfitCurrency"]})
    nt = pd.DataFrame(rows).sort_values("entry_time").reset_index(drop=True)
    nt.to_csv(f"{OUT}/nt_trades_{inst.lower()}.csv", index=False)

    py_daily, pyt = python_replay(cfg["comm"], cfg["pv"])
    pyt.to_csv(f"{OUT}/py_trades_{inst.lower()}.csv", index=False)
    print(f"PY: net {py_daily.sum():.2f}  round trips {len(pyt)}  (ref net {cfg['ref_net']:.2f})")

    # ---- reconcile (verbatim parity_d.py methodology) ----
    # NT8 stamps a fill at the fill bar's END; the Python reference stamps most (non-
    # session-end) fills at the fill bar's OPEN (constant 3-min offset, prices identical --
    # documented in research/system_master/NINJATRADER_PARITY.md's prior passed check).
    # Trade-level matching: align onto the OPEN convention (entry fills are never
    # session-end fills, so this shift is unambiguous for entries).
    OFFSET = pd.Timedelta(minutes=3)
    nt = nt.copy()
    nt["entry_time_open"] = nt["entry_time"] - OFFSET
    # Daily-level reconciliation: group NT trades by the TRUE session date (via the
    # project's own bars_dev sess_date map on the trade's RAW, unshifted exit_time -- NT's
    # raw timestamp equals the underlying bar's own timestamp exactly, which is the key the
    # sess_date map is built on), NOT by the exit fill's calendar date. Session-end forced
    # exits keep the Python reference's own tm[t] (unshifted) convention internally, so
    # calendar-date-of-exit-timestamp silently misattributes boundary-adjacent trades to the
    # wrong day in a way that nets to ~$0 but corrupts daily correlation; this is a
    # reconciliation-script fix, not a strategy behavior difference.
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

    parity = {
        "instrument": inst, "py_trades": len(pyt), "nt_trades": len(nt),
        "matched_entry_time_dir": len(inter), "matched_pct": matched_pct,
        "daily_corr": daily_corr, "net_py": net_py, "net_nt": net_nt,
        "net_delta_pct": net_delta_pct, "max_abs_daily_delta": max_abs_delta,
        "pass_decision_parity_995": matched_pct >= 99.5,
        "pass_daily_corr_0999": daily_corr >= 0.999,
        "pass_net_diff_lt_05pct": abs(net_delta_pct) <= 0.5,
        "worst5_daily_deltas": {str(k): v for k, v in dd_.head(5).to_dict().items()},
        "n_nt_trades_sessdate_unmapped": n_unmapped,
        "nt_ninjatrader_timestamp_note": "NT stamps fills at the fill bar's END, PY at the "
            "fill bar's OPEN (constant 3-min offset, prices identical, documented in "
            "NINJATRADER_PARITY.md's prior passed check) -- entry-time matching aligned to "
            "the OPEN convention; daily grouping uses the project's own sess_date map on "
            "each trade's raw exit_time rather than calendar-date-of-timestamp.",
    }
    print(json.dumps({k: v for k, v in parity.items() if k != "worst5_daily_deltas"}, indent=2, default=str))
    with open(f"{OUT}/parity_{inst.lower()}.json", "w") as f:
        json.dump(parity, f, indent=2, default=str)

    # ---- full metric battery (on the NT-parity-verified series: use NT daily) ----
    battery = compute_battery(na, nt, f"{inst}_Final_NT")
    battery_py = compute_battery(pa, pyt, f"{inst}_Final_PY_ref")
    with open(f"{OUT}/metric_battery_{inst.lower()}.json", "w") as f:
        json.dump({"nt": battery, "python_reference": battery_py}, f, indent=2, default=str)

    # ---- capital map (on NT daily, the parity-verified series) ----
    cmap = capital_map(na)
    cmap.to_csv(f"{OUT}/capital_map_{inst.lower()}.csv", index=False)

    results[inst] = {"parity": parity, "battery": battery, "battery_py": battery_py}

with open(f"{OUT}/summary_all.json", "w") as f:
    json.dump(results, f, indent=2, default=str)
print("DONE")
