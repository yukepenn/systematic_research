"""OTR_OF1: causal quote-rule trade classification + proxy-vs-real diagnostics."""
import json
import os

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RAW = os.path.join(ROOT, "research", "scalping_lab", "substrate", "raw", "NQ")
OUT = os.path.join(ROOT, "runs", "OTR_OF1_BIDASK_CLASSIFIER", "out")
os.makedirs(OUT, exist_ok=True)
TICK = 0.25
PCTS = (5, 25, 50, 75, 95)


def classify(df):
    bip = df["bip"].values
    px = df["price"].values
    vol = df["volume"].values.astype(np.float64)
    n = len(df)
    side = np.zeros(n, dtype=np.int8)  # only for trades: +1 buy, -1 sell
    method = np.zeros(n, dtype=np.int8)  # 1 at-ask, 2 at-bid, 3 tick-rule-inside, 4 tick-rule-noquote
    bid = np.nan
    ask = np.nan
    last_side = 0
    last_px = np.nan
    for i in range(n):
        b = bip[i]
        if b == 1:
            bid = px[i]
        elif b == 2:
            ask = px[i]
        else:
            p = px[i]
            if not np.isnan(bid) and not np.isnan(ask) and bid < ask:
                if p >= ask:
                    side[i] = 1; method[i] = 1
                elif p <= bid:
                    side[i] = -1; method[i] = 2
                else:
                    if not np.isnan(last_px) and p != last_px:
                        side[i] = 1 if p > last_px else -1
                    else:
                        side[i] = last_side
                    method[i] = 3
            else:
                if not np.isnan(last_px) and p != last_px:
                    side[i] = 1 if p > last_px else -1
                else:
                    side[i] = last_side
                method[i] = 4
            if side[i] != 0:
                last_side = side[i]
            last_px = p
    return side, method


def per_session(name):
    df = pd.read_parquet(os.path.join(RAW, f"{name}.parquet"))
    side, method = classify(df)
    tr = df[df["bip"] == 0].copy()
    tr["side"] = side[df["bip"].values == 0]
    tr["method"] = method[df["bip"].values == 0]
    stats = {
        "n_trades": int(len(tr)), "total_volume": float(tr["volume"].sum()),
        "at_ask_pct": round(float((tr["method"] == 1).mean() * 100), 2),
        "at_bid_pct": round(float((tr["method"] == 2).mean() * 100), 2),
        "inside_tickrule_pct": round(float((tr["method"] == 3).mean() * 100), 2),
        "noquote_tickrule_pct": round(float((tr["method"] == 4).mean() * 100), 2),
        "buy_vol_pct": round(float(tr.loc[tr["side"] == 1, "volume"].sum() / tr["volume"].sum() * 100), 2),
    }
    # 1-min aggregates
    tr["minute"] = tr["time"].dt.floor("min")
    g = tr.groupby("minute")
    agg = pd.DataFrame({
        "buy_vol": tr[tr["side"] == 1].groupby("minute")["volume"].sum(),
        "sell_vol": tr[tr["side"] == -1].groupby("minute")["volume"].sum(),
        "tot_vol": g["volume"].sum(),
        "pv": g.apply(lambda x: (x["price"] * x["volume"]).sum(), include_groups=False),
        "n_trades": g.size(),
        "close": g["price"].last(),
    }).fillna(0.0)
    agg["delta"] = agg["buy_vol"] - agg["sell_vol"]
    agg.to_parquet(os.path.join(OUT, f"{name}_1m.parquet"))

    # proxy-vs-real diagnostics per clock hour
    tr["hour"] = tr["time"].dt.floor("h")
    vdisp, ladder_disp = [], []
    for h, grp in tr.groupby("hour"):
        if grp["volume"].sum() < 1000:
            continue
        vwap_real = (grp["price"] * grp["volume"]).sum() / grp["volume"].sum()
        m = agg[(agg.index >= h) & (agg.index < h + pd.Timedelta(hours=1))]
        if m["tot_vol"].sum() <= 0:
            continue
        vwap_proxy = (m["close"] * m["tot_vol"]).sum() / m["tot_vol"].sum()
        vdisp.append(abs(vwap_real - vwap_proxy) / TICK)
        # volume-at-price percentile lines: real (tick trades) vs minute-close-binned
        def plines(prices, vols):
            o = np.argsort(prices)
            p, v = np.asarray(prices)[o], np.asarray(vols)[o]
            cum = np.cumsum(v) / v.sum()
            return [p[min(int(np.searchsorted(cum, q / 100)), len(p) - 1)] for q in PCTS]
        real = plines(grp["price"].values, grp["volume"].values)
        prox = plines(m["close"].values, m["tot_vol"].values)
        ladder_disp.append([abs(a - b) / TICK for a, b in zip(real, prox)])
    ladder_disp = np.array(ladder_disp)
    diag = {
        "hours": int(len(vdisp)),
        "vwap_displacement_ticks_mean": round(float(np.mean(vdisp)), 2),
        "vwap_displacement_ticks_max": round(float(np.max(vdisp)), 2),
        "ladder_displacement_ticks_mean_by_pct": {str(q): round(float(ladder_disp[:, k].mean()), 2) for k, q in enumerate(PCTS)},
        "ladder_displacement_ticks_max_by_pct": {str(q): round(float(ladder_disp[:, k].max()), 2) for k, q in enumerate(PCTS)},
    }
    return stats, diag


res = {}
for name in ("s20260511", "s20260512"):
    print(f"[OF1] {name} ...", flush=True)
    stats, diag = per_session(name)
    res[name] = {"classification": stats, "proxy_vs_real": diag}
    print(json.dumps(res[name], indent=1), flush=True)

with open(os.path.join(OUT, "results.json"), "w") as f:
    json.dump(res, f, indent=1)
print("[OF1] done", flush=True)
