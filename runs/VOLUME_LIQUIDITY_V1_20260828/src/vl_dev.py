"""VOLUME_LIQUIDITY_V1 -- DEVELOPMENT.  ONE SHOT.  Gates D1-D11 frozen in SPEC.md at 4ef441d.

Runs only after vl_certify.py reports PASS on all five clauses.
Held-back (2019-2022) and modern (2023+) windows are NOT touched: date_max is applied at load.
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(RUN))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "research", "multi_market", "src"))
import ncd_day as N                                                          # noqa: E402
import vl_primary as VP                                                      # noqa: E402

OUT = os.path.join(RUN, "out")
DEV = VP.DEV_END
BOOT_B, BOOT_SEED, BOOT_PCTL = 20000, 20260828, 5.0
NULL1_MAX, NULL2_REPS = 500, 500
_fh = open(os.path.join(OUT, "vl_dev.txt"), "w", encoding="utf-8")
R = {}


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


# ------------------------------------------------------------------ metric helpers
def sharpe(w):
    return float(w.mean() / w.std(ddof=1) * math.sqrt(52)) if w.std(ddof=1) > 0 else float("nan")


def maxdd(w):
    c = np.cumsum(w)
    pk = np.maximum.accumulate(c)
    dd = pk - c
    i = int(np.argmax(dd))
    return float(dd.max()), i


def dd_duration(w):
    c = np.cumsum(w)
    pk, run, best = -np.inf, 0, 0
    for x in c:
        if x >= pk:
            pk, run = x, 0
        else:
            run += 1
            best = max(best, run)
    return int(best)


def es5(w):
    k = max(1, int(math.ceil(0.05 * len(w))))
    return float(np.sort(w)[:k].mean())


def block_bootstrap(w, B=BOOT_B, seed=BOOT_SEED, pctl=BOOT_PCTL):
    n = len(w)
    L = int(round(n ** (1.0 / 3.0)))
    nb = int(math.ceil(n / L))
    rng = np.random.default_rng(seed)
    starts = rng.integers(0, n, size=(B, nb))
    off = np.arange(L)
    idx = (starts[:, :, None] + off[None, None, :]).reshape(B, nb * L)[:, :n] % n
    means = w[idx].mean(axis=1)
    return dict(n_weeks=n, L=L, B=B, seed=seed,
                mean=float(w.mean()), boot_mean=float(means.mean()),
                boot_sd=float(means.std(ddof=1)),
                lower_bound=float(np.percentile(means, pctl)),
                distinct=int(len(np.unique(np.round(means, 9)))))


def long_basket(pos, e, slip=VP.SLIP_TICKS_PRIMARY):
    """Equal-risk LONG-ONLY multi-market basket: RISK_SCORE == +1 for every eligible root."""
    p = pos.copy()
    p["RISK_SCORE"] = 1.0
    p["n_raw"] = p["RISK_SCORE"] * VP.RISK_BUDGET / p["SIGMA"]
    p["gross_i"] = VP.RISK_BUDGET
    gs = p.groupby(["monday", "sector"])["gross_i"].transform("sum")
    gt = p.groupby("monday")["gross_i"].transform("sum")
    sc = np.where(gs / gt > VP.SECTOR_CAP, VP.SECTOR_CAP * gt / np.maximum(gs, 1e-12), 1.0)
    p["n"] = p["n_raw"] * sc
    d, _ = VP.simulate(p, e, slip_ticks=slip)
    return VP.weekly_net(d)


# ================================================================== BASELINE
P("=" * 112)
P("=== VOLUME_LIQUIDITY_V1 -- DEVELOPMENT RESULT.  ONE SHOT.  Gates frozen at 4ef441d.")
P("=" * 112)
base = VP.run(date_max=DEV)
pos, daily, sides = base["pos"], base["daily"], base["sides"]
wk = base["weekly"]
w = wk["net"].values
_, e_full = VP.load_inputs()
e_dev = e_full[e_full["date"] < DEV]
assert daily["date"].max() < DEV
P(f"    window            {daily['date'].min().date()} -> {daily['date'].max().date()}   "
  f"(asserted < {DEV.date()})")
P(f"    weeks             {len(wk):,}      roots {pos['root'].nunique()}   "
  f"sectors {pos['sector'].nunique()}")
P(f"    (root, week) pos  {len(pos):,}      daily rows {len(daily):,}")

gross, cost, net = float(wk["gross"].sum()), float(wk["cost"].sum()), float(wk["net"].sum())
cd = cost / abs(gross) if gross else float("nan")
mdd, _ = maxdd(w)
pos["gross_risk"] = pos["n"].abs() * pos["SIGMA"]
pos["net_risk"] = pos["n"] * pos["SIGMA"]
gr = pos.groupby("monday")["gross_risk"].sum()
nr = pos.groupby("monday")["net_risk"].sum()

P("")
P("--- 7A  ECONOMICS  (PRIMARY cost model: $4.36 RT + 1 tick, charged per side)")
P(f"    gross P&L                  ${gross:>16,.2f}")
P(f"    costs                      ${cost:>16,.2f}")
P(f"    NET P&L                    ${net:>16,.2f}")
P(f"    cost / |gross|             {cd:>16.2%}")
P(f"    weekly mean                ${float(w.mean()):>16,.2f}")
P(f"    weekly median              ${float(np.median(w)):>16,.2f}")
P(f"    weekly sd                  ${float(w.std(ddof=1)):>16,.2f}")
P(f"    annualized weekly Sharpe   {sharpe(pd.Series(w)):>16.3f}")
P(f"    max drawdown               ${mdd:>16,.2f}")
P(f"    drawdown duration (weeks)  {dd_duration(w):>16d}")
P(f"    ES 5%                      ${es5(w):>16,.2f}")
P(f"    positive-week rate         {float((w>0).mean()):>16.2%}")
P(f"    total sides traded         {float(daily['sides'].sum()):>16,.1f}  "
  f"(= {float(daily['sides'].sum())/2:,.1f} contract round turns)")
P(f"    sides per week             {float(daily['sides'].sum())/len(wk):>16,.2f}")
P(f"    avg ex-ante gross risk     ${float(gr.mean()):>16,.2f} /day-sd")
P(f"    avg NET directional risk   ${float(nr.mean()):>16,.2f} /day-sd   "
  f"({float(nr.mean()/gr.mean()):+.3%} of gross)")
lon = float(daily.loc[daily["n"] > 0, "pnl_net"].sum())
sho = float(daily.loc[daily["n"] < 0, "pnl_net"].sum())
P(f"    LONG-leg net               ${lon:>16,.2f}     (LOW-participation sleeve)")
P(f"    SHORT-leg net              ${sho:>16,.2f}     (HIGH-participation sleeve)")

P("")
P("--- 7A  ROOT AND SECTOR DECOMPOSITION")
br = daily.groupby("root")["pnl_net"].sum().sort_values(ascending=False)
bs = daily.groupby("sector")["pnl_net"].sum().sort_values(ascending=False)
pr, ps = br[br > 0].sum(), bs[bs > 0].sum()
P(f"    {'root':<6}{'net':>14}{'share of +root':>16}   |   {'sector':<14}{'net':>14}{'share of +sector':>18}")
sl = list(bs.items())
for i, (rt, vv) in enumerate(br.items()):
    left = f"    {rt:<6}{vv:>14,.0f}{(vv/pr if pr>0 else np.nan):>16.1%}"
    if i < len(sl):
        s, sv = sl[i]
        P(f"{left}   |   {s:<14}{sv:>14,.0f}{(sv/ps if ps>0 else np.nan):>18.1%}")
    else:
        P(left)
top_root_share = float(br.max() / pr) if pr > 0 else float("nan")
top_sec_share = float(bs.max() / ps) if ps > 0 else float("nan")

P("")
P("--- 7A  CHRONOLOGY")
yr = daily.copy()
yr["y"] = yr["date"].dt.year
ys = yr.groupby("y")["pnl_net"].sum()
P("    calendar year:  " + "  ".join(f"{int(y)} {v:>+9,.0f}" for y, v in ys.items()))
blocks = np.array_split(w, 4)
bsum = [float(b.sum()) for b in blocks]
bidx = np.array_split(np.array(wk.index), 4)
for i, (b, ix) in enumerate(zip(bsum, bidx)):
    P(f"    block {i+1}  {pd.Timestamp(ix[0]).date()} -> {pd.Timestamp(ix[-1]).date()}  "
      f"{len(ix):>3} wk   net ${b:>+12,.2f}")
nblocks_pos = int(sum(b > 0 for b in bsum))

posw = w[w > 0]
tot_posw = float(posw.sum())
srt = np.sort(w)[::-1]
P(f"    top 1 / 5 / 10 weeks as share of total POSITIVE weekly contribution: "
  f"{srt[0]/tot_posw:.1%} / {srt[:5].sum()/tot_posw:.1%} / {srt[:10].sum()/tot_posw:.1%}")
top10_share = float(srt[:10].sum() / tot_posw)

P("")
P("--- 7A  CONTRIBUTION BY DISTANCE TO A CAUSAL ROLL  (VOLUME00 residual risk: +-1 ratio 1.481)")
vsub = pd.read_parquet(os.path.join(ROOT, "runs", "VOLUME00_20260828", "out",
                                    "volume_substrate.parquet"),
                       columns=["root", "date", "roll_dist"])
dj = daily.merge(vsub, on=["root", "date"], how="left")
dj["band"] = pd.cut(dj["roll_dist"], [-1, 1, 3, 5, 10 ** 9],
                    labels=["<=1", "2-3", "4-5", ">5"])
rb = dj.groupby("band", observed=False)["pnl_net"].agg(["sum", "count"])
for b, rr in rb.iterrows():
    P(f"    distance {str(b):<5} rows {int(rr['count']):>7,}   net ${rr['sum']:>+14,.2f}   "
      f"{rr['sum']/net if net else np.nan:>8.1%} of total net")

P("")
P("--- 7E  STATIC-LONG CONTAMINATION DIAGNOSTIC")
lb = long_basket(pos, e_dev)
common = wk.index.intersection(lb.index)
x, y = lb.loc[common, "net"].values, wk.loc[common, "net"].values
beta = float(np.polyfit(x, y, 1)[0])
alpha = float(np.polyfit(x, y, 1)[1])
r2 = float(np.corrcoef(x, y)[0, 1] ** 2)
gr_lb = VP.RISK_BUDGET * pos.groupby("monday")["root"].count().mean()
match_scale = float(gr.mean() / (pos.groupby("monday")["SIGMA"].count().mean() * VP.RISK_BUDGET))
P(f"    equal-risk LONG-ONLY basket net       ${float(lb['net'].sum()):>16,.2f}")
P(f"    exposure-matched static benchmark     ${float(lb['net'].sum()*match_scale):>16,.2f}  "
  f"(scale {match_scale:.4f})")
P(f"    beta of strategy on the basket        {beta:>16.4f}")
P(f"    intercept (weekly $)                  ${alpha:>16,.2f}")
P(f"    R^2                                   {r2:>16.4f}")
P(f"    avg NET directional exposure          {float(nr.mean()/gr.mean()):>16.3%} of gross risk")
P("    (NOT residualized after the fact -- this adjudicates interpretation, not a repair)")

P("")
P("--- 7A  LEAVE-ONE-OUT  (full re-run each time: dropping a root changes its sector's demean)")
roots = sorted(pos["root"].unique())
loo_r = {}
for rt in roots:
    keep = [x for x in roots if x != rt]
    loo_r[rt] = float(VP.run(date_max=DEV, roots=keep)["weekly"]["net"].sum())
    P(f"    drop {rt:<4} -> net ${loo_r[rt]:>+14,.2f}   "
      f"{'OK' if loo_r[rt] > 0 else '*** NEGATIVE ***'}")
loo_min = min(loo_r.values())
secs = sorted(pos["sector"].unique())
loo_s = {}
for s in secs:
    keep = [x for x in roots if N.SECTOR[x] != s]
    loo_s[s] = float(VP.run(date_max=DEV, roots=keep)["weekly"]["net"].sum())
    P(f"    drop sector {s:<14} -> net ${loo_s[s]:>+14,.2f}")

P("")
P("--- 7B  DEPENDENCE-AWARE UNCERTAINTY  (circular block bootstrap, frozen before running)")
bsr = block_bootstrap(w)
for k, v in bsr.items():
    P(f"    {k:<16} {v}")
rng = np.random.default_rng(BOOT_SEED)
iid = np.array([w[rng.integers(0, len(w), len(w))].mean() for _ in range(2000)])
P(f"    (diagnostic only) IID bootstrap 5th pctile  ${float(np.percentile(iid,5)):,.2f}")

P("")
P("--- 5C  PURE COST STRESS  (position path FROZEN; only the cost rate changes)")
ds, _ = VP.simulate(pos, e_dev, slip_ticks=VP.SLIP_TICKS_STRESS, frozen_sides=sides)
wks = VP.weekly_net(ds)
net_s = float(wks["net"].sum())
same_path = float((ds["n"].values - daily["n"].values).__abs__().max())
same_sides = float((ds["sides"].values - daily["sides"].values).__abs__().max())
P(f"    max |d position| vs primary   {same_path:.3e}   (must be 0 -- the path is frozen)")
P(f"    max |d sides|    vs primary   {same_sides:.3e}   (must be 0)")
P(f"    PRIMARY  net ${net:>14,.2f}    cost ${cost:>12,.2f}")
P(f"    STRESS   net ${net_s:>14,.2f}    cost ${float(wks['cost'].sum()):>12,.2f}")
P(f"    net_stress <= net_primary : {'PASS' if net_s <= net else '*** FAIL - ARITHMETIC ***'}")

P("")
P("--- 7C  NULL 1  TEMPORAL ASSOCIATION  (ONE SHARED whole-week circular shift per replicate)")
vv, _ = VP.load_inputs()
vv = vv[vv["date"] < DEV]
nmin = int(vv[vv["vol_usable"] & vv["eligible"]].groupby("root").size().min())
kmax = min(NULL1_MAX, nmin // 5 - 1)
P(f"    shortest eligible volume series {nmin:,} sessions -> {nmin//5-1} distinct whole-week shifts")
P(f"    using the EXHAUSTIVE set k = 1..{kmax} (cap {NULL1_MAX})")
n1 = []
for k in range(1, kmax + 1):
    n1.append(float(VP.run(date_max=DEV, shift_weeks=k)["weekly"]["net"].sum()))
    if k % 50 == 0:
        P(f"      ... {k}/{kmax}")
n1 = np.array(n1)
P(f"    replicates {len(n1)}   distinct values {len(np.unique(np.round(n1,6)))}  "
  f"{'(>=2 PASS)' if len(np.unique(np.round(n1,6)))>=2 else '*** DEGENERATE ***'}")
P(f"    null net: min ${n1.min():,.0f}  p50 ${np.percentile(n1,50):,.0f}  "
  f"p95 ${np.percentile(n1,95):,.0f}  max ${n1.max():,.0f}")
p1 = float((n1 < net).mean() * 100)
P(f"    REAL ${net:,.2f}  ->  percentile of its own null: {p1:.1f}th   requires > 95.0")

P("")
P("--- 7D  NULL 2  WITHIN-SECTOR SIGNAL-IDENTITY PLACEBO")
n2 = []
for i in range(NULL2_REPS):
    n2.append(float(VP.run(date_max=DEV, permute_signal_seed=BOOT_SEED + i)["weekly"]["net"].sum()))
    if (i + 1) % 100 == 0:
        P(f"      ... {i+1}/{NULL2_REPS}")
n2 = np.array(n2)
P(f"    replicates {len(n2)}   distinct {len(np.unique(np.round(n2,6)))}")
P(f"    null net: min ${n2.min():,.0f}  p50 ${np.percentile(n2,50):,.0f}  "
  f"p95 ${np.percentile(n2,95):,.0f}  max ${n2.max():,.0f}")
p2 = float((n2 < net).mean() * 100)
P(f"    REAL ${net:,.2f}  ->  percentile: {p2:.1f}th   requires > 95.0")

P("")
P("--- 8A  SIGN MIRROR  (DIAGNOSTIC ONLY -- a winning mirror CLOSES V1, it does not invert it)")
mir = float(VP.run(date_max=DEV, sign=-1.0)["weekly"]["net"].sum())
P(f"    mirror net ${mir:,.2f}   vs real ${net:,.2f}")

# ================================================================== GATES
P("")
P("=" * 112)
P("=== DEVELOPMENT GATE TABLE  D1-D11  (frozen in SPEC.md at 4ef441d, before any result)")
P("=" * 112)
sh = sharpe(pd.Series(w))
G = [("D1  PRIMARY after-cost net > 0", f"${net:,.2f}", net > 0),
     ("D2  annualized weekly Sharpe >= 0.50", f"{sh:.3f}", sh >= 0.50),
     ("D3  block-bootstrap lower 95% > 0", f"${bsr['lower_bound']:,.2f}",
      bsr["lower_bound"] > 0),
     ("D4  PURE COST STRESS net > 0", f"${net_s:,.2f}", net_s > 0),
     ("D5  cost / |gross| <= 25%", f"{cd:.2%}", cd <= 0.25),
     ("D6  net > 0 in >= 3 of 4 blocks", f"{nblocks_pos} of 4", nblocks_pos >= 3),
     ("D7a top root <= 35% of +root contribution", f"{top_root_share:.1%}",
      top_root_share <= 0.35),
     ("D7b top sector <= 50% of +sector contribution", f"{top_sec_share:.1%}",
      top_sec_share <= 0.50),
     ("D8  leave-one-root-out all net > 0", f"min ${loo_min:,.0f}", loo_min > 0),
     ("D9  temporal null, real > 95th pctile", f"{p1:.1f}th", p1 > 95.0),
     ("D10 identity placebo, real > 95th pctile", f"{p2:.1f}th", p2 > 95.0),
     ("D11 top 10 positive weeks <= 50%", f"{top10_share:.1%}", top10_share <= 0.50)]
P(f"    {'GATE':<50}{'OBSERVED':>22}   VERDICT")
for nm, ob, ok in G:
    P(f"    {nm:<50}{ob:>22}   {'PASS' if bool(ok) else '*** FAIL ***'}")
fails = [nm for nm, _, ok in G if not bool(ok)]
verdict = ("DEVELOPMENT-SUPPORTED / DISCOVERY-GRADE" if not fails
           else "VOLUME_LIQUIDITY_V1 - NO CANDIDATE / CLOSED AT EXACT SCOPE")
P("")
P("=" * 112)
P(f"=== VERDICT: {verdict}")
P("=" * 112)
P(f"    blocking failures: {fails if fails else 'none'}")

R = dict(window=[str(daily["date"].min().date()), str(daily["date"].max().date())],
         weeks=int(len(wk)), roots=int(pos["root"].nunique()), positions=int(len(pos)),
         gross=gross, cost=cost, net=net, cost_drag=cd, weekly_mean=float(w.mean()),
         weekly_median=float(np.median(w)), weekly_sd=float(w.std(ddof=1)), sharpe=sh,
         maxdd=mdd, dd_duration=dd_duration(w), es5=es5(w),
         positive_week_rate=float((w > 0).mean()), sides=float(daily["sides"].sum()),
         avg_gross_risk=float(gr.mean()), avg_net_risk=float(nr.mean()),
         long_leg=lon, short_leg=sho,
         by_root={k: float(v) for k, v in br.items()},
         by_sector={k: float(v) for k, v in bs.items()},
         top_root_share=top_root_share, top_sector_share=top_sec_share,
         by_year={int(k): float(v) for k, v in ys.items()}, blocks=bsum,
         blocks_positive=nblocks_pos, top10_share=top10_share,
         bootstrap=bsr, stress_net=net_s,
         null1=dict(n=int(len(n1)), pctile=p1, p95=float(np.percentile(n1, 95)),
                    median=float(np.median(n1))),
         null2=dict(n=int(len(n2)), pctile=p2, p95=float(np.percentile(n2, 95)),
                    median=float(np.median(n2))),
         mirror_net=mir, beta_long_basket=beta, alpha_weekly=alpha, r2=r2,
         long_basket_net=float(lb["net"].sum()),
         loo_root={k: float(v) for k, v in loo_r.items()},
         loo_sector={k: float(v) for k, v in loo_s.items()},
         gates=[dict(gate=n, observed=o, passed=bool(k)) for n, o, k in G],
         blocking_failures=fails, verdict=verdict)
json.dump(R, open(os.path.join(OUT, "vl_dev.json"), "w", encoding="utf-8"), indent=2, default=str)
wk.to_csv(os.path.join(OUT, "vl_dev_weekly.csv"))
daily.groupby(["root"])["pnl_net"].sum().to_csv(os.path.join(OUT, "vl_dev_root.csv"))
np.save(os.path.join(OUT, "vl_dev_null1.npy"), n1)
np.save(os.path.join(OUT, "vl_dev_null2.npy"), n2)
_fh.close()
