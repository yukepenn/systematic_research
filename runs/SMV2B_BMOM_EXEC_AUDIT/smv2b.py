"""SMV2B — B-MOM causal execution audit (frozen W8-1 signals; fill timing varied).
E0 signal-close | E2 next-3m-open | E3=E2+1t | E4=E2+2t ; E1 = 1s-after subsample (grid1s).
"""
import sys, os, glob, json
import numpy as np, pandas as pd
sys.path.insert(0, "src/analytics")
from sm01_solarsim import load_bars_3m
from sm_bmom import bmom_trades, rth_3m, TICK, TICK_USD, C1_TICKS, C2_TICKS, BAND_DAYS
from smv2_common import dd_battery, boot_ci_mean

OUT = "runs/SMV2B_BMOM_EXEC_AUDIT/out"
os.makedirs(OUT, exist_ok=True)
NQ_RT_TICKS = 0.872  # $4.36 RT actual Lifetime / $5 per tick


def bmom_variant(bars3, fill_mode="E0", slip_ticks=0.0):
    """Frozen W8-1 signal logic; fills per fill_mode. Returns trade ledger."""
    r = rth_3m(bars3)
    days = []
    for d, g in r.groupby("date", sort=True):
        g = g.sort_values("hm")
        if g["hm"].iloc[0] != 933:
            continue
        days.append((d, g))
    hist, day_count, trades = {}, 0, []
    slip = slip_ticks * TICK
    for d, g in days:
        open0930 = g["open"].iloc[0]
        close = g["close"].to_numpy(); op = g["open"].to_numpy()
        vol = g["volume"].to_numpy(); hm = g["hm"].to_numpy()
        vwap = np.cumsum(close * vol) / np.maximum(np.cumsum(vol), 1e-9)
        pos = 0; entry_px = np.nan; entry_hm = None
        flat_hm = int(hm[hm <= 1557].max()) if (hm <= 1557).any() else None
        nbars = len(g)

        def fillpx(i, side):
            """side=+1 buy, -1 sell; fill for a decision made at bar i close."""
            if fill_mode == "E0":
                base = close[i]
            else:  # E2 family: next bar open; fall back to signal close if no next bar
                base = op[i + 1] if i + 1 < nbars else close[i]
            return base + side * slip

        def book(i, exit_hm, reason):
            nonlocal pos, entry_px, entry_hm
            exit_px = fillpx(i, -pos)
            pts = (exit_px - entry_px) * pos
            gross_t = pts / TICK
            trades.append({"sess": d, "side": "L" if pos > 0 else "S",
                           "entry_hm": entry_hm, "exit_hm": exit_hm,
                           "entry_px": entry_px, "exit_px": exit_px, "exit_reason": reason,
                           "pts": pts, "gross_ticks": gross_t})
            pos = 0; entry_px = np.nan; entry_hm = None

        if day_count >= BAND_DAYS:
            for i in range(nbars):
                h = int(hm[i])
                if flat_hm is not None and h == flat_hm:
                    if pos != 0:
                        book(i, h, "closeout")
                    break
                if h > 1554:
                    continue
                past = hist.get(h)
                if past is None or len(past) < 1:
                    continue
                m_tod = float(np.mean(past[-BAND_DAYS:]))
                upper, lower = open0930 + m_tod, open0930 - m_tod
                sig = 0
                if close[i] > max(upper, vwap[i]):
                    sig = 1
                elif close[i] < min(lower, vwap[i]):
                    sig = -1
                if sig != 0 and sig != pos:
                    if pos != 0:
                        book(i, h, "flip")
                    pos = sig
                    entry_px = fillpx(i, sig)
                    entry_hm = h
            else:
                if pos != 0:
                    book(nbars - 1, int(hm[-1]), "closeout")
        for i in range(nbars):
            hist.setdefault(int(hm[i]), []).append(abs(close[i] - open0930))
        day_count += 1
    t = pd.DataFrame(trades)
    for nm, c in [("net_c1_ticks", C1_TICKS), ("net_c2_ticks", C2_TICKS), ("net_nq_ticks", NQ_RT_TICKS)]:
        t[nm] = t["gross_ticks"] - c
    return t


def battery(trades, cost_col, label):
    d = trades.groupby("sess")[cost_col].sum() * TICK_USD
    d.index = pd.to_datetime(d.index)
    b = dd_battery(d.index, d.values, label=label)
    w = trades[cost_col] > 0
    b["trades"] = len(trades); b["win_pct"] = w.mean()
    gp = trades.loc[trades[cost_col] > 0, cost_col].sum(); gl = -trades.loc[trades[cost_col] <= 0, cost_col].sum()
    b["PF"] = gp / gl if gl > 0 else np.inf
    b["avg_ticks"] = trades[cost_col].mean()
    b["long_net"] = trades.loc[trades.side == "L", cost_col].sum() * TICK_USD
    b["short_net"] = trades.loc[trades.side == "S", cost_col].sum() * TICK_USD
    srt = np.sort(trades[cost_col].to_numpy())[::-1]
    k = max(1, int(0.01 * len(srt)))
    b["top1pct_share"] = srt[:k].sum() / max(srt.sum(), 1e-9)
    lo, hi, pgt0 = boot_ci_mean(d.values)
    b["ci_lo_daily"], b["ci_hi_daily"], b["P_mean_gt0"] = lo * TICK_USD / TICK_USD, hi, pgt0
    return b, d


print("loading bars ...")
bars = load_bars_3m()
sess = pd.to_datetime(bars["sess_date"])
dev = (sess <= pd.Timestamp("2026-05-31"))
bars_dev = bars[dev].reset_index(drop=True)

print("validating E0 vs frozen generator ...")
t_frozen = bmom_trades(bars_dev)
t_e0 = bmom_variant(bars_dev, "E0", 0.0)
assert len(t_frozen) == len(t_e0), (len(t_frozen), len(t_e0))
assert np.allclose(t_frozen["net_c1_ticks"], t_e0["net_c1_ticks"]), "E0 mismatch"
print("E0 == frozen generator:", len(t_e0), "trades")

arms = {"E0_signal_close": ("E0", 0.0), "E2_next_open": ("E2", 0.0),
        "E3_next_open_+1t": ("E2", 1.0), "E4_next_open_+2t": ("E2", 2.0)}
rows, dailies, ledgers = [], {}, {}
for name, (fm, st) in arms.items():
    t = bmom_variant(bars_dev, fm, st)
    ledgers[name] = t
    for cost in ("net_c1_ticks", "net_nq_ticks"):
        b, dser = battery(t, cost, f"{name}|{cost}")
        rows.append(b)
        if cost == "net_c1_ticks":
            dailies[name] = dser
res = pd.DataFrame(rows).set_index("label")
cols = ["trades", "net", "sharpe", "sortino", "calmar", "maxDD_eod", "worst_month",
        "rolling60_min", "win_pct", "PF", "avg_ticks", "long_net", "short_net",
        "top1pct_share", "P_mean_gt0"]
res[cols].to_csv(f"{OUT}/results.csv")
print(res[cols].round(3).to_string())

# annual breakdown (C1)
ann = pd.DataFrame({k: v.groupby(v.index.year).sum() for k, v in dailies.items()})
ann.to_csv(f"{OUT}/annual.csv"); print(ann.round(0).to_string())

# per-trade fill drift E0 vs E2
e0, e2 = ledgers["E0_signal_close"], ledgers["E2_next_open"]
if len(e0) == len(e2):
    drift = (e2["gross_ticks"] - e0["gross_ticks"])
    print("fill drift per trade (E2-E0): mean %.2f t, median %.2f t, p10 %.1f, p90 %.1f"
          % (drift.mean(), drift.median(), drift.quantile(0.1), drift.quantile(0.9)))
    json.dump({"n": len(drift), "mean_t": float(drift.mean()), "median_t": float(drift.median())},
              open(f"{OUT}/fill_drift.json", "w"))

# ---- E1 subsample on grid1s (40 sessions): 1-second-after fill at bid/ask ----
print("E1 subsample ...")
g1files = sorted(glob.glob("research/scalping_lab/substrate/grid1s/NQ/*.parquet"))
recs = []
e2i = ledgers["E2_next_open"].copy()
e2i["sessT"] = pd.to_datetime(e2i["sess"])
for f in g1files:
    d0 = pd.read_parquet(f, columns=["time", "last", "bid", "ask"])
    d0["time"] = pd.to_datetime(d0["time"])
    sd = d0["time"].iloc[-1].date()  # session labeled by end date
    day_tr = e2i[e2i["sessT"].dt.date == sd]
    if not len(day_tr):
        continue
    d0 = d0.set_index("time").sort_index()
    for _, tr in day_tr.iterrows():
        for leg, hmv, side in (("entry", tr.entry_hm, 1 if tr.side == "L" else -1),
                               ("exit", tr.exit_hm, -1 if tr.side == "L" else 1)):
            if hmv is None or (isinstance(hmv, float) and np.isnan(hmv)):
                continue
            hh, mm = divmod(int(hmv), 100)
            tsig = pd.Timestamp(sd).replace(hour=hh, minute=mm) + pd.Timedelta(seconds=1)
            w = d0.loc[tsig: tsig + pd.Timedelta(seconds=10)]
            if not len(w):
                continue
            q = w.iloc[0]
            px1s = q["ask"] if side > 0 else q["bid"]
            if np.isnan(px1s):
                px1s = q["last"]
            recs.append({"sess": str(sd), "leg": leg, "side": side, "px_1s": px1s})
e1df = pd.DataFrame(recs)
e1df.to_csv(f"{OUT}/e1_subsample_fills.csv", index=False)
print("E1 subsample fills:", len(e1df))

# ---- portfolio impact: PORT_TILT_532 with E2 leg ----
print("portfolio impact ...")
cal = pd.DatetimeIndex(sorted(sess[dev].unique()))
tiltd = pd.read_csv("runs/SM08_HTF_TILT/out/tilt50_rounded_daily.csv")
tiltd.columns = ["sess", "net"]; tiltd["sess"] = pd.to_datetime(tiltd["sess"])
T = tiltd.set_index("sess")["net"].reindex(cal).fillna(0.0)
b1n = pd.read_csv("research/scalping_lab/artifacts/w9_b1/w9b1_nightly.csv", parse_dates=["exit_session_date"])
b1dev = b1n[(b1n.exit_session_date >= cal[0]) & (b1n.exit_session_date <= cal[-1])]
B1 = b1dev.groupby("exit_session_date")["net2.0_usd"].sum().reindex(cal).fillna(0.0)
SIG_F1 = 2338.66
out_port = []
for name in ("E0_signal_close", "E2_next_open", "E3_next_open_+1t"):
    BMd = dailies[name].reindex(cal).fillna(0.0)
    for mode in ("frozen_scale", "rule_recomputed"):
        sc_b = 0.6588 if mode == "frozen_scale" else SIG_F1 / BMd.std(ddof=1)
        port = 0.5 * 0.9904 * T + 0.3 * sc_b * BMd + 0.2 * 0.8270 * B1
        port = port * (SIG_F1 / port.std(ddof=1))  # rescale rule to F1 sigma
        b = dd_battery(cal, port.values, label=f"PORT_TILT_532|{name}|{mode}")
        out_port.append(b)
pp = pd.DataFrame(out_port).set_index("label")
pp[["net", "sharpe", "maxDD_eod", "worst_month", "calmar"]].to_csv(f"{OUT}/port_impact.csv")
print(pp[["net", "sharpe", "maxDD_eod", "worst_month", "calmar"]].round(2).to_string())
for k, v in ledgers.items():
    v.to_parquet(f"{OUT}/ledger_{k}.parquet")
print("done")
