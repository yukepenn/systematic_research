"""SMV2R sub_382 — vol memory (seq 382). Rebuild the 13-member ensemble with sigma
memory N in {230, 460 incumbent, 920}; E10 execution (round(10*mean pending), clamp
+-10, MNQ costs, session flatten, fills via _fill) on dev (sessions <= 2026-05-31).
Verdict rule (frozen spec): incumbent is a plateau iff neither neighbor beats it by
>20% on Sharpe AND CDaR simultaneously.
"""
import sys, os, json, time, datetime as dt
import numpy as np, pandas as pd

RUN = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\runs\SMV2R_SOLAR_CORE_1"
sys.path.insert(0, RUN)
from common_exec import sm, e10_exec, metric_row, ROOT

OUT = os.path.join(RUN, "out")
DEV_END = dt.date(2026, 5, 31)
t0 = time.time()

bars = sm.load_bars_3m(os.path.join(ROOT, "runs", "AUDIT03_BARS", "nq_3m_2022_2026.csv"))
bars = bars[bars["sess_date"] <= DEV_END].reset_index(drop=True)
close = bars.close.to_numpy()
LO, HI = 40 * sm.TICK, 1200 * sm.TICK

rows = []
extras = {}
dailies = {}
for N in (230, 460, 920):
    sig = sm.sigma_series(close, vol_period=N)
    PEND = []
    s_at_flip = []     # S_eff resolved at trend flips (threshold actually used)
    clamp_lo = clamp_hi = n_flip = 0
    for vm in sm.VMS:
        is_up, flip, s_eff, anchor = sm.member_states(close, sig, float(vm))
        fills, pos, pend = sm.member_trades(bars, is_up, flip, s_eff, anchor)
        PEND.append(pend)
        fmask = flip != 0
        sf = s_eff[fmask]
        s_at_flip.append(sf)
        raw = vm * sig[fmask]
        fin = np.isfinite(raw)
        clamp_lo += int((raw[fin] <= LO).sum()); clamp_hi += int((raw[fin] >= HI).sum())
        n_flip += int(fin.sum())
    pend = np.column_stack(PEND)
    tgt = sm.e10_target(pend)
    daily, bar_pos, bar_pnl = e10_exec(bars, tgt)
    dailies[N] = daily
    r = metric_row(f"N{N}" + ("_incumbent" if N == 460 else ""), daily)
    sflip = np.concatenate(s_at_flip)
    r.update({
        "vol_period": N,
        "S_at_flip_p10_pts": float(np.percentile(sflip, 10)),
        "S_at_flip_p50_pts": float(np.percentile(sflip, 50)),
        "S_at_flip_p90_pts": float(np.percentile(sflip, 90)),
        "n_flips_all_members": int(n_flip),
        "clamp_lo_pct_at_flip": clamp_lo / n_flip * 100,
        "clamp_hi_pct_at_flip": clamp_hi / n_flip * 100,
        "tgt_change_bars_pct": float((np.diff(tgt) != 0).mean() * 100),
    })
    rows.append(r)
    print(f"N={N} done net={r['net']:.0f} sharpe={r['sharpe']:.3f} "
          f"CDaR5={r['CDaR5']:.0f} {time.time()-t0:.0f}s", flush=True)

df = pd.DataFrame(rows)
df.to_csv(os.path.join(OUT, "vol_memory.csv"), index=False)

inc = df[df.vol_period == 460].iloc[0]
verdict = {}
for N in (230, 920):
    nb = df[df.vol_period == N].iloc[0]
    beats = (nb.sharpe > 1.2 * inc.sharpe) and (nb.CDaR5 < 0.8 * inc.CDaR5)
    verdict[f"N{N}_dominates"] = bool(beats)
verdict["plateau"] = not (verdict["N230_dominates"] or verdict["N920_dominates"])
with open(os.path.join(OUT, "vol_memory_verdict.json"), "w") as f:
    json.dump(verdict, f, indent=2)
for N, d in dailies.items():
    d.to_csv(os.path.join(OUT, f"daily_volmem_N{N}.csv"), index=False)
print(df.to_string(index=False))
print(json.dumps(verdict, indent=2))
