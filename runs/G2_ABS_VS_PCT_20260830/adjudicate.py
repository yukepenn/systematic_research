#!/usr/bin/env python
"""
G2_ABS_VS_PCT_20260830 -- ADJUDICATION
Paired analysis of the runner's two matched NT8 weekly P&L series.
Reads only from out/. Writes only ADJUDICATION_TABLES.txt in the run dir.
"""
import numpy as np, pandas as pd
from scipy import stats
from pathlib import Path

RUN = Path(r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\runs\G2_ABS_VS_PCT_20260830")
OUT = RUN / "out"
L = []
def p(s=""):
    L.append(str(s)); print(s)

w = pd.read_csv(OUT / "weekly_pnl_joined.csv", parse_dates=["week_monday"])
w = w.sort_values("week_monday").reset_index(drop=True)
tA = pd.read_csv(OUT / "trades_ABS.csv", parse_dates=["entry_time", "exit_time", "session_date"])
tP = pd.read_csv(OUT / "trades_PCT.csv", parse_dates=["entry_time", "exit_time", "session_date"])

N = len(w)
d = w["diff_PCT_minus_ABS"].values            # PCT - ABS
netP, netA = w["net_PCT"].values, w["net_ABS"].values

p("=" * 78)
p("G2 ABS-vs-PCT ADJUDICATION  (paired: same weeks, same engine, same bars, same costs)")
p("=" * 78)
p(f"window            : {w.week_monday.min().date()} .. {w.week_monday.max().date()} (ISO week Mondays)")
p(f"paired weeks N    : {N}")
p(f"cost convention   : NT8 Lifetime $4.36/ctrRT, 0 slippage. NOT the research cost model.")
p(f"identity check    : sum(net_PCT-net_ABS) - sum(diff) = {netP.sum()-netA.sum()-d.sum():.6f}")

# ---------------------------------------------------------------- 1. TOTALS
p("\n" + "-" * 78)
p("1. TOTALS")
p("-" * 78)
nA, nP = int(w.n_ABS.sum()), int(w.n_PCT.sum())
tot = pd.DataFrame({
    "arm":       ["ABS (WeeklyEdgeP1_v3)", "PCT (WeeklyEdgeP1PCT_v1)"],
    "net_$":     [netA.sum(), netP.sum()],
    "trades":    [nA, nP],
    "net/week_$":[netA.sum()/N, netP.sum()/N],
    "net/trade_$":[netA.sum()/nA, netP.sum()/nP],
})
p(tot.to_string(index=False, float_format=lambda x: f"{x:,.2f}"))
dD = netP.sum() - netA.sum()
p(f"\nPCT - ABS  net difference : ${dD:,.2f}")
p(f"PCT - ABS  as % of ABS    : {100*dD/netA.sum():+.2f}%")
p(f"PCT - ABS  per week       : ${dD/N:,.2f}/wk")
p(f"trade-count difference    : PCT {nP} vs ABS {nA}  ({nP-nA:+d}, {100*(nP-nA)/nA:+.1f}%)")

# how much of the series is literally identical
tie = np.isclose(d, 0.0, atol=1e-6)
p(f"\nweeks with IDENTICAL P&L  : {tie.sum()}/{N} ({100*tie.mean():.1f}%)  <- the two objects agree here")
p(f"weeks that actually differ: {(~tie).sum()}/{N} ({100*(~tie).mean():.1f}%)")

# ---------------------------------------------------------------- 2. PAIRED TEST
p("\n" + "-" * 78)
p("2. PAIRED WEEKLY TEST  (H0: mean weekly PCT-ABS = 0)")
p("-" * 78)
mean_d, sd_d = d.mean(), d.std(ddof=1)
se_iid = sd_d / np.sqrt(N)
t_iid = mean_d / se_iid
p_iid = 2 * stats.t.sf(abs(t_iid), N - 1)

def nw_se(x, L_lag):
    x = x - x.mean(); n = len(x); g0 = (x @ x) / n; s = g0
    for l in range(1, L_lag + 1):
        gl = (x[l:] @ x[:-l]) / n
        s += 2 * (1 - l / (L_lag + 1)) * gl
    return np.sqrt(max(s, 1e-12) / n)

L_auto = int(np.floor(4 * (N / 100) ** (2 / 9)))          # Newey-West rule of thumb
se_nw = nw_se(d, L_auto)
t_nw = mean_d / se_nw
p_nw = 2 * stats.norm.sf(abs(t_nw))

p(f"mean weekly diff (PCT-ABS) : ${mean_d:,.2f}/wk")
p(f"sd of weekly diff          : ${sd_d:,.2f}")
p(f"iid  SE / t / p            : ${se_iid:,.2f}  t={t_iid:+.3f}  p={p_iid:.4f}")
p(f"Newey-West(L={L_auto}) SE/t/p  : ${se_nw:,.2f}  t={t_nw:+.3f}  p={p_nw:.4f}")
p(f"95% CI (iid) on mean diff  : [${mean_d-1.96*se_iid:,.2f}, ${mean_d+1.96*se_iid:,.2f}]/wk")
p(f"95% CI (NW)  on mean diff  : [${mean_d-1.96*se_nw:,.2f}, ${mean_d+1.96*se_nw:,.2f}]/wk")

# stationary block bootstrap on weeks (preserves dependence)
rng = np.random.default_rng(20260830)
B, bl = 20000, 4
nb = int(np.ceil(N / bl))
boot = np.empty(B)
for b in range(B):
    st = rng.integers(0, N, nb)
    idx = np.concatenate([(np.arange(s, s + bl) % N) for s in st])[:N]
    boot[b] = d[idx].mean()
p_boot = 2 * min((boot <= 0).mean(), (boot >= 0).mean())
p(f"block bootstrap (bl={bl}, B={B}) two-sided p = {p_boot:.4f}   CI [${np.percentile(boot,2.5):,.2f}, ${np.percentile(boot,97.5):,.2f}]")

# Wilcoxon on non-tied weeks
nz = d[~tie]
try:
    ws, wp = stats.wilcoxon(nz)
    p(f"Wilcoxon signed-rank (non-tied n={len(nz)}) : W={ws:.0f}  p={wp:.4f}")
except Exception as e:
    p(f"Wilcoxon: {e}")

p("\nSIGN TEST on weekly wins")
winP = int((d > 1e-6).sum()); winA = int((d < -1e-6).sum()); ties = int(tie.sum())
sp = stats.binomtest(winP, winP + winA, 0.5).pvalue
p(f"  PCT-better weeks : {winP}")
p(f"  ABS-better weeks : {winA}")
p(f"  tied  weeks      : {ties}")
p(f"  excl. ties       : {winP}/{winP+winA} = {100*winP/(winP+winA):.1f}%   sign-test p = {sp:.4f}")
sp_all = stats.binomtest(winP, N, 0.5).pvalue
p(f"  incl. ties as N  : {winP}/{N} = {100*winP/N:.1f}%   p = {sp_all:.4f}")
p("  NOTE: the repo's recorded '176/213 weeks' cannot be a weekly-P&L sign count on a series")
p("        that is exactly tied in a large share of weeks; it is a different statistic.")

# ---------------------------------------------------------------- 3. RISK-NORMALISED
p("\n" + "-" * 78)
p("3. RISK-NORMALISED  (fixed drawdown $20,245)")
p("-" * 78)
def dd_from(series):
    eq = np.cumsum(series); pk = np.maximum.accumulate(np.concatenate([[0.0], eq]))[1:]
    return float((pk - eq).max())
ddA_w, ddP_w = dd_from(netA), dd_from(netP)
ddA_t = dd_from(tA.net_currency.values)   # trade-sequence (intra-week) DD
ddP_t = dd_from(tP.net_currency.values)
FIX = 20245.0
rows = []
for lbl, net, ddw, ddt, n in [("ABS", netA.sum(), ddA_w, ddA_t, nA), ("PCT", netP.sum(), ddP_w, ddP_t, nP)]:
    rows.append([lbl, net, net/N, ddw, ddt, net/ddt, (net/N)*(FIX/ddt), (net/N)*(FIX/ddw)])
rn = pd.DataFrame(rows, columns=["arm", "net_$", "net/wk_$", "maxDD_weekly_$", "maxDD_trade_$",
                                 "MAR(net/DD)", f"net/wk @${FIX:,.0f}DD (trade-DD)", f"net/wk @${FIX:,.0f}DD (weekly-DD)"])
p(rn.to_string(index=False, float_format=lambda x: f"{x:,.2f}"))
sA = FIX / ddA_t; sP = FIX / ddP_t
p(f"\nscale to ${FIX:,.0f} DD (trade-sequence DD): ABS x{sA:.3f}   PCT x{sP:.3f}")
gapfix = (netP.sum()/N)*sP - (netA.sum()/N)*sA
p(f"fixed-DD net/week gap PCT-ABS : ${gapfix:+,.2f}/wk  "
  f"({100*gapfix/((netA.sum()/N)*sA):+.1f}% vs ABS)" if (netA.sum()/N)*sA != 0 else "")
p(f"raw    net/week gap PCT-ABS   : ${dD/N:+,.2f}/wk ({100*dD/netA.sum():+.1f}%)")
p(f"deeper drawdown belongs to    : {'PCT' if ddP_t>ddA_t else 'ABS'} "
  f"(trade-DD ABS ${ddA_t:,.0f} vs PCT ${ddP_t:,.0f}; ratio PCT/ABS = {ddP_t/ddA_t:.3f})")

# ---------------------------------------------------------------- 4. CONCENTRATION
p("\n" + "-" * 78)
p("4. CONCENTRATION OF THE DIFFERENCE")
p("-" * 78)
order = np.argsort(-np.abs(d))
tot_d = d.sum()
p(f"total net difference to explain: ${tot_d:,.2f}")
for frac in [0.01, 0.02, 0.05, 0.10, 0.25]:
    k = max(1, int(round(frac * N)))
    s = d[order[:k]].sum()
    p(f"  top {frac*100:5.1f}% of weeks by |diff| = {k:3d} wk : ${s:12,.2f}  = {100*s/tot_d:7.1f}% of the net difference")
for k in [1, 3, 5, 10, 20]:
    s = d[order[:k]].sum()
    p(f"  top {k:3d} weeks                       : ${s:12,.2f}  = {100*s/tot_d:7.1f}%")
gross = np.abs(d).sum()
k5 = max(1, int(round(0.05 * N)))
p(f"\n  GROSS (sum |diff|) = ${gross:,.2f}; top 5% of weeks hold "
  f"{100*np.abs(d)[order[:k5]].sum()/gross:.1f}% of GROSS  (repo analogue of the 90.8%/53-of-1058 claim)")
p(f"  net difference / gross difference = {100*tot_d/gross:.1f}%  (signal-to-churn of the contrast)")
p("\n  largest 10 weekly differences:")
top = w.iloc[order[:10]][["week_monday", "net_PCT", "net_ABS", "diff_PCT_minus_ABS", "n_PCT", "n_ABS"]]
p(top.to_string(index=False, float_format=lambda x: f"{x:,.2f}"))
# leave-one-out fragility
loo = np.array([ (np.delete(d, i).mean()) for i in range(N)])
p(f"\n  leave-one-week-out mean diff range: ${loo.min():,.2f} .. ${loo.max():,.2f} (full ${mean_d:,.2f})")
dd_ = np.delete(d, order[0])
tt = dd_.mean()/(dd_.std(ddof=1)/np.sqrt(N-1))
p(f"  drop the single largest week -> mean ${dd_.mean():,.2f}/wk, t={tt:+.3f}, "
  f"p={2*stats.t.sf(abs(tt), N-2):.4f}")
dd5 = np.delete(d, order[:5])
tt5 = dd5.mean()/(dd5.std(ddof=1)/np.sqrt(N-5))
p(f"  drop the 5 largest weeks     -> mean ${dd5.mean():,.2f}/wk, t={tt5:+.3f}, "
  f"p={2*stats.t.sf(abs(tt5), N-6):.4f}")

# ---------------------------------------------------------------- 5. ERA SPLIT
p("\n" + "-" * 78)
p("5. ERA SPLIT")
p("-" * 78)
half = N // 2
segs = [("H1", 0, half), ("H2", half, N)]
yrs = sorted(w.week_monday.dt.year.unique())
rows = []
for lbl, a, b in segs:
    seg = d[a:b]; sA_ = netA[a:b].sum(); sP_ = netP[a:b].sum()
    se = seg.std(ddof=1)/np.sqrt(len(seg)); tv = seg.mean()/se
    rows.append([lbl, f"{w.week_monday.iloc[a].date()}..{w.week_monday.iloc[b-1].date()}", len(seg),
                 sA_, sP_, sP_-sA_, seg.mean(), tv, 2*stats.t.sf(abs(tv), len(seg)-1),
                 int((seg>1e-6).sum()), int((seg<-1e-6).sum())])
es = pd.DataFrame(rows, columns=["era","span","wks","ABS_net","PCT_net","diff","mean_diff/wk","t","p","PCTwin","ABSwin"])
p(es.to_string(index=False, float_format=lambda x: f"{x:,.2f}"))
p("")
rows = []
for y in yrs:
    m = (w.week_monday.dt.year == y).values
    seg = d[m]
    rows.append([y, m.sum(), netA[m].sum(), netP[m].sum(), seg.sum(), seg.mean(),
                 int((seg>1e-6).sum()), int((seg<-1e-6).sum()), int(np.isclose(seg,0,atol=1e-6).sum())])
ys = pd.DataFrame(rows, columns=["year","wks","ABS_net","PCT_net","diff","mean/wk","PCTwin","ABSwin","tie"])
p(ys.to_string(index=False, float_format=lambda x: f"{x:,.2f}"))

# ---------------------------------------------------------------- 6. MDE
p("\n" + "-" * 78)
p("6. MINIMUM DETECTABLE EFFECT")
p("-" * 78)
mde_iid = 2 * se_iid; mde_nw = 2 * se_nw
p(f"at |t| = 2, N = {N} weeks, sd = ${sd_d:,.2f}:")
p(f"  MDE (iid SE) = ${mde_iid:,.2f}/wk  = ${mde_iid*N:,.0f} over the window")
p(f"  MDE (NW  SE) = ${mde_nw:,.2f}/wk  = ${mde_nw*N:,.0f} over the window")
p(f"  observed     = ${mean_d:,.2f}/wk  -> observed / MDE(iid) = {mean_d/mde_iid:.2f}x")
p(f"  as % of ABS net/week (${netA.sum()/N:,.2f}): MDE = {100*mde_iid/(netA.sum()/N):.1f}%")
for tgt_t in [2.0]:
    need = (tgt_t * sd_d / mean_d) ** 2 if mean_d != 0 else np.inf
    p(f"  weeks needed for |t|={tgt_t:.0f} at the OBSERVED effect size: {need:,.0f} "
      f"({need/52:.1f} years) -> {need-N:,.0f} MORE weeks ({(need-N)/52:.1f} yr)")
# power of the shadow window
p(f"\n  forward shadow power: at the observed ${mean_d:,.2f}/wk and sd ${sd_d:,.2f},")
for hz in [13, 26, 52, 104]:
    pw = stats.norm.sf(1.96 - abs(mean_d)/(sd_d/np.sqrt(hz)))
    p(f"    {hz:3d} shadow weeks ({hz/52:.2f} yr): power = {100*pw:4.1f}%")

# ---------------------------------------------------------------- extra: where does the diff come from
p("\n" + "-" * 78)
p("7. MECHANISM CHECK -- is the difference information or exposure?")
p("-" * 78)
def key(t): return t.entry_time.astype(str) + "|" + t.direction
kA, kP = set(key(tA)), set(key(tP))
p(f"  shared entry(time,dir) keys : {len(kA & kP)}")
p(f"  ABS-only                    : {len(kA - kP)}")
p(f"  PCT-only                    : {len(kP - kA)}")
mA = tA[key(tA).isin(kA & kP)]; mP = tP[key(tP).isin(kA & kP)]
p(f"  net on shared trades        : ABS ${mA.net_currency.sum():,.2f}  PCT ${mP.net_currency.sum():,.2f} "
  f"(diff ${mP.net_currency.sum()-mA.net_currency.sum():,.2f})")
p(f"  net on ABS-only trades      : ${tA[~key(tA).isin(kA & kP)].net_currency.sum():,.2f} "
  f"({len(kA-kP)} trades)")
p(f"  net on PCT-only trades      : ${tP[~key(tP).isin(kA & kP)].net_currency.sum():,.2f} "
  f"({len(kP-kA)} trades)")
p(f"  decision-series agreement   : {100*len(kA & kP)/len(kA | kP):.2f}% of the union of entries")

Path(RUN / "ADJUDICATION_TABLES.txt").write_bytes("\n".join(L).encode("utf-8"))
print("\n[written] ADJUDICATION_TABLES.txt")
