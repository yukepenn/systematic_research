"""SW01: join exported per-bar Solar state ledger to the R01 trade ledger; attribution."""
import hashlib
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
LEDGER = os.path.join(ROOT, "research", "01_diagnostics", "sw01_bar_ledger.csv")
TRADES = os.path.join(ROOT, "runs", "SW00_R01", "trades.parquet")
OUT_JSON = os.path.join(ROOT, "research", "01_diagnostics", "SW01_attribution.json")
OUT_PARQ = os.path.join(ROOT, "research", "01_diagnostics", "sw01_trades_tagged.parquet")

out = {}

bars = pd.read_csv(LEDGER, parse_dates=["time"])
out["n_bars"] = int(len(bars))
out["value_profile"] = {c: bars[c].value_counts(dropna=False).head(9).to_dict()
                        for c in ("signal_trade", "signal_trend", "signal_wave")}

trend_sign = np.sign(bars["signal_trend"].fillna(0.0))
bars["trend_sign"] = trend_sign
# episode = maximal run of constant nonzero trend sign
change = (trend_sign != trend_sign.shift()).cumsum()
bars["episode"] = np.where(trend_sign != 0, change, np.nan)
flip = (trend_sign != trend_sign.shift()) & (trend_sign != 0) & (trend_sign.shift().notna())
for W in (60, 120):
    bars[f"flips_{W}"] = flip.rolling(W, min_periods=1).sum()
    delta = bars["close"].diff().abs()
    bars[f"eff_{W}"] = (bars["close"].diff(W).abs() / delta.rolling(W, min_periods=2).sum()).clip(0, 1)
bars["vol_60"] = bars["close"].pct_change().rolling(60, min_periods=30).std() * np.sqrt(60)
bars["stop_dist_ticks"] = (bars["close"] - bars["trailing_stop"]).abs() / 0.25
bars["wave_abs"] = bars["signal_wave"].abs()

n_epi = bars["episode"].nunique()
epi_len = bars.groupby("episode").size()
out["episodes"] = dict(count=int(n_epi), median_len_bars=float(epi_len.median()),
                       p90_len=float(epi_len.quantile(0.9)), max_len=int(epi_len.max()))

t = pd.read_parquet(TRADES)
bt = bars.set_index("time")
idx = bt.index

# signal bar = last ledger bar strictly BEFORE the entry fill timestamp
pos = idx.searchsorted(t["entry_time"].values, side="left") - 1
valid = pos >= 0
sig = bt.iloc[pos[valid]]
t = t.loc[valid].reset_index(drop=True).join(
    sig.reset_index(drop=True)[["signal_trade", "signal_trend", "signal_wave", "episode",
                                 "flips_60", "flips_120", "eff_60", "eff_120",
                                 "vol_60", "stop_dist_ticks", "wave_abs", "trend_sign"]]
)
out["n_trades_joined"] = int(len(t))
# integrity: EntrySignalType=1 -> signal_trade at signal bar must equal trade side
match = (t["signal_trade"] == t["side"]).mean()
out["entry_signal_match_pct"] = round(100 * float(match), 3)
out["entry_signal_mismatches"] = int((t["signal_trade"] != t["side"]).sum())

def agg(g):
    wins = g[g.profit > 0]["profit"]; loss = g[g.profit < 0]["profit"]
    return pd.Series(dict(n=len(g), net=round(g.profit.sum(), 0), avg=round(g.profit.mean(), 2),
                          win_pct=round(100 * (g.profit > 0).mean(), 1),
                          pf=round(wins.sum() / -loss.sum(), 3) if len(loss) and loss.sum() < 0 else None))

# per-episode PnL concentration
epi_pnl = t.groupby("episode")["profit"].sum().sort_values(ascending=False)
k = max(1, int(len(epi_pnl) * 0.10))
out["episode_concentration"] = dict(
    n_episodes_traded=int(len(epi_pnl)), top_decile_episode_net=round(float(epi_pnl.head(k).sum()), 0),
    total_net=round(float(epi_pnl.sum()), 0),
    pct_episodes_positive=round(100 * float((epi_pnl > 0).mean()), 1))

def qb(s, q):
    try:
        return pd.qcut(s, q, duplicates="drop")
    except ValueError:
        return pd.cut(s, q)

t["flip_bucket"] = pd.cut(t["flips_120"], [-0.1, 1, 2, 3, 99], labels=["0-1", "2", "3", "4+"])
t["eff_q"] = qb(t["eff_120"], 4)
t["vol_t"] = qb(t["vol_60"], 3)
t["stopdist_q"] = qb(t["stop_dist_ticks"], 4)
t["wave_bucket"] = pd.cut(t["wave_abs"], [-0.1, 1, 2, 99], labels=["w<=1", "w2", "w3+"])

for key in ("flip_bucket", "eff_q", "vol_t", "stopdist_q", "wave_bucket"):
    out[f"by_{key}"] = t.groupby(key, observed=True).apply(agg, include_groups=False).reset_index().to_dict("records")

# interaction preregistered in thesis (chop veto): high flips AND low efficiency
mask = (t["flips_120"] >= 3) & (t["eff_120"] <= 0.30)
out["chop_cell"] = dict(n=int(mask.sum()), net=round(float(t.loc[mask, "profit"].sum()), 0),
                        avg=round(float(t.loc[mask, "profit"].mean()), 2) if mask.sum() else None,
                        complement_net=round(float(t.loc[~mask, "profit"].sum()), 0))

for c in ("flip_bucket", "eff_q", "vol_t", "stopdist_q", "wave_bucket"):
    t[c] = t[c].astype(str)
t.to_parquet(OUT_PARQ, index=False)
with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1, default=str)
print(json.dumps(out, indent=1, default=str))
