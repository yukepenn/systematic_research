"""Supplement: term structure of persistence (short-horizon reversion vs multi-month trend),
extreme-move provenance, and a modeled GC cost band. Feeds STEP 3 ranking. DESCRIPTIVE ONLY."""
from __future__ import annotations
import os, sys
import numpy as np, pandas as pd

RUN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(RUN, "out")
gc = pd.read_parquet(os.path.join(OUT, "gc_daily.parquet"))
a = gc[gc["clean_daily"]].copy().reset_index(drop=True)
rp = a["ret_pct"].values
RNG = np.random.default_rng(11)


def var_ratio(x, k):
    x = np.asarray(x, float); n = len(x); mu = x.mean()
    va1 = np.sum((x - mu) ** 2) / n
    agg = np.convolve(x, np.ones(k), "valid")
    vak = np.sum((agg - k * mu) ** 2) / (n - k + 1)
    return float(vak / (k * va1))


print("=== TERM STRUCTURE OF PERSISTENCE (VR>1 trend, <1 reversion) ===")
for k in (2, 5, 10, 20, 40, 63, 126, 189, 252):
    o = var_ratio(rp, k)
    draws = np.array([var_ratio(np.roll(rp, RNG.integers(1, len(rp))), k) for _ in range(500)])
    print(f"  VR({k:>3}d) = {o:.3f}   shift-null mean {draws.mean():.3f} sd {draws.std():.3f}  "
          f"pctile {np.mean(draws <= o)*100:5.1f}")

print("\n=== TSMOM: trailing-L return -> forward-h return (overlapping, sign & corr) ===")
close = a["close_radj"].values
logc = np.log(close)
for L, h in [(21, 21), (63, 21), (126, 21), (252, 21), (63, 63), (126, 126), (252, 63)]:
    past = logc[L:len(logc)-h] - logc[:len(logc)-h-L]
    fwd = logc[L+h:] - logc[L:len(logc)-h]
    if len(past) < 50:
        continue
    rho = np.corrcoef(past, fwd)[0, 1]
    # sign strategy: mean forward return in direction of past sign
    dir_ret = fwd * np.sign(past)
    t = dir_ret.mean() / (dir_ret.std(ddof=1) / np.sqrt(len(dir_ret)))
    print(f"  L={L:>3}d h={h:>3}d  corr(past,fwd) {rho:+.3f}  "
          f"E[fwd*sign(past)] {dir_ret.mean()*100:+.3f}% [overlap-t {t:+.2f}] n {len(dir_ret)}")

print("\n=== EXTREME MOVES (clean daily) ===")
ex = a.reindex(a["ret_pct"].abs().sort_values(ascending=False).index).head(8)
for _, r in ex.iterrows():
    print(f"  {r['date'].date()}  ret {r['ret_pct']*100:+.2f}%  close {r['close']:.1f}  "
          f"contract {r['held_contract']}  rolled {int(r['rolled'])}")

print("\n=== BUY-AND-HOLD CONTEXT (long gold, no cost) ===")
mu, sd = rp.mean(), rp.std()
print(f"  daily mean {mu*1e4:+.2f}bps sd {sd*100:.3f}%  ann ret ~{mu*252*100:+.1f}%  "
      f"ann vol {sd*np.sqrt(252)*100:.1f}%  naive Sharpe ~{mu/sd*np.sqrt(252):.2f}")
first, last = a['close_radj'].iloc[0], a['close_radj'].iloc[-1]
print(f"  close_radj {first:.0f} -> {last:.0f} over {len(a)} days ({a['date'].iloc[0].date()}"
      f"->{a['date'].iloc[-1].date()})")

print("\n=== MODELED GC COST BAND (for STEP 3 falsifiers; MODELED-STANDARD, not measured) ===")
pv = 100.0  # $/point; tick 0.10 = $10
comm = 4.36  # RT, Lifetime-template proxy
for lab, ticks in [("optimistic 0.5tk", 0.5), ("base 1tk", 1.0), ("conservative 2tk", 2.0),
                   ("stress 3tk", 3.0)]:
    spread = ticks * 10.0  # $/RT (one tick = $10 round trip crossing)
    allin = comm + spread
    # express as bps on a ~$2000 gold level (1 contract notional = 100*2000 = $200,000)
    print(f"  {lab:<18} spread ${spread:5.1f}/RT  all-in ${allin:5.2f}/RT  "
          f"= {allin/(pv*2000)*1e4:.2f} bps of notional  (~{allin/pv/2000*100:.4f}% price move)")
