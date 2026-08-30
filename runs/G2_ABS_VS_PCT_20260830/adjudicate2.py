import numpy as np, pandas as pd
from scipy import stats
from pathlib import Path
RUN = Path(r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\runs\G2_ABS_VS_PCT_20260830")
OUT = RUN / "out"
L = []
def p(s=""): L.append(str(s)); print(s)

w = pd.read_csv(OUT/"weekly_pnl_joined.csv", parse_dates=["week_monday"]).sort_values("week_monday").reset_index(drop=True)
tA = pd.read_csv(OUT/"trades_ABS.csv", parse_dates=["entry_time","exit_time","session_date","week_monday"])
tP = pd.read_csv(OUT/"trades_PCT.csv", parse_dates=["entry_time","exit_time","session_date","week_monday"])
d = w.diff_PCT_minus_ABS.values; N = len(w)

p("="*78); p("ADJUDICATION -- PANEL B (mechanism, exposure, fragility)"); p("="*78)

# ---- exposure / sizing confound check
p("\nB1. SIZING / EXPOSURE CONFOUND CHECK  (CLAUDE.md: leverage must not masquerade as alpha)")
for lbl,t in [("ABS",tA),("PCT",tP)]:
    vc = t.qty.value_counts().sort_index().to_dict()
    p(f"  {lbl}: trades={len(t)}  qty mix={vc}  contract-sides={t.qty.sum()}  "
      f"all-long={set(t.direction)=={'Long'}}")
p(f"  contract-sides PCT/ABS ratio = {tP.qty.sum()/tA.qty.sum():.4f}  "
  f"(exposure difference, not a sizing multiplier)")
p(f"  commission paid : ABS ${tA.commission.sum():,.2f}   PCT ${tP.commission.sum():,.2f}")

# ---- entry-key decomposition, by qty-aware key
def key(t): return t.entry_time.astype(str)+"|"+t.direction+"|"+t.qty.astype(str)
kA,kP = set(key(tA)), set(key(tP))
sh = kA & kP
mA = tA[key(tA).isin(sh)].set_index(key(tA)[key(tA).isin(sh)]).sort_index()
mP = tP[key(tP).isin(sh)].set_index(key(tP)[key(tP).isin(sh)]).sort_index()
p("\nB2. DECOMPOSITION OF THE $45,009.80 DIFFERENCE BY ENTRY KEY (time|dir|qty)")
p(f"  shared entries        : {len(sh)}")
p(f"  ABS-only entries      : {len(kA-kP)}   net ${tA[~key(tA).isin(sh)].net_currency.sum():>12,.2f}")
p(f"  PCT-only entries      : {len(kP-kA)}   net ${tP[~key(tP).isin(sh)].net_currency.sum():>12,.2f}")
mA2 = mA[~mA.index.duplicated()]; mP2 = mP[~mP.index.duplicated()]
com = mA2.index.intersection(mP2.index)
a,b = mA2.loc[com], mP2.loc[com]
same_exit = (a.exit_time.values == b.exit_time.values)
p(f"  of the {len(com)} deduped shared entries: identical exit_time {same_exit.sum()} "
  f"({100*same_exit.mean():.1f}%), different exit {int((~same_exit).sum())}")
p(f"    net on IDENTICAL-exit shared trades : ABS ${a[same_exit].net_currency.sum():,.2f}  "
  f"PCT ${b[same_exit].net_currency.sum():,.2f}  (diff ${b[same_exit].net_currency.sum()-a[same_exit].net_currency.sum():,.2f})")
p(f"    net on DIFFERENT-exit shared trades : ABS ${a[~same_exit].net_currency.sum():,.2f}  "
  f"PCT ${b[~same_exit].net_currency.sum():,.2f}  (diff ${b[~same_exit].net_currency.sum()-a[~same_exit].net_currency.sum():,.2f})")
p("  -> ATTRIBUTION: the difference is (i) EXIT PLACEMENT on shared entries and")
p("     (ii) EXTRA ENTRIES PCT takes that ABS does not. Both are MECHANISM-POLICY,")
p("     not NEW INFORMATION: identical bars, identical entry signal, different stop metric.")

# ---- signed concentration, honest version
p("\nB3. SIGNED CONCENTRATION (the honest version)")
pos = d[d>1e-6]; neg = d[d<-1e-6]
p(f"  PCT-better weeks : {len(pos):3d}  total +${pos.sum():,.2f}")
p(f"  ABS-better weeks : {len(neg):3d}  total  ${neg.sum():,.2f}")
p(f"  tied weeks       : {N-len(pos)-len(neg):3d}")
p(f"  NET             = ${d.sum():,.2f}  = {100*d.sum()/pos.sum():.1f}% of the gross PCT-better total")
srt = np.sort(pos)[::-1]
p(f"  the 5 best PCT weeks alone: +${srt[:5].sum():,.2f} = {100*srt[:5].sum()/d.sum():.0f}% of the NET difference")
p(f"  the 11 best (top 5% of N) : +${srt[:11].sum():,.2f} = {100*srt[:11].sum()/d.sum():.0f}% of the NET difference")
p(f"  -> the net advantage is the RESIDUAL of two large offsetting piles; removing the")
p(f"     5 largest |diff| weeks moves the mean from +$210.33/wk to -$8.02/wk (t=-0.13).")
# how many weeks to flip
o = np.argsort(-d); cum = np.cumsum(d[o]); k = int(np.argmax(cum >= d.sum()))
p(f"  weeks needed to account for the entire net difference: {k+1} of {N} "
  f"({100*(k+1)/N:.1f}%) -- the other {N-k-1} weeks net ${d.sum()-cum[k]:,.2f}")

# ---- price-level mechanism test
p("\nB4. IS THERE A MECHANISM? (a % stop widens with price; a point stop does not)")
pxA = tA.groupby("week_monday").entry_price.mean()
w2 = w.set_index("week_monday").join(pxA.rename("px")).dropna(subset=["px"])
r = stats.pearsonr(w2.px, w2.diff_PCT_minus_ABS)
rs = stats.spearmanr(w2.px, w2.diff_PCT_minus_ABS)
p(f"  corr(weekly NQ level, weekly PCT-ABS diff): pearson r={r[0]:+.3f} p={r[1]:.4f} | "
  f"spearman rho={rs[0]:+.3f} p={rs[1]:.4f}  (n={len(w2)})")
q = pd.qcut(w2.px, 4, labels=["Q1 low px","Q2","Q3","Q4 high px"])
g = w2.groupby(q, observed=True).agg(wks=("diff_PCT_minus_ABS","size"), mean_diff=("diff_PCT_minus_ABS","mean"),
                                     tot_diff=("diff_PCT_minus_ABS","sum"), px_mid=("px","median"))
p(g.to_string(float_format=lambda x: f"{x:,.2f}"))
p("  reading: the ABS point-stop becomes a TIGHTER PERCENTAGE as NQ rises; the PCT stop does not.")
p("  So a PCT>ABS gap that GROWS with price level is mechanically expected, not necessarily luck.")
p("  But note this cuts both ways: it makes the gap a function of the 2022-26 PRICE PATH,")
p("  and the 2026 sub-window (30 wks, +$28,662 = 64% of the total) is where it lands.")

# ---- rolling
p("\nB5. ROLLING 52-WEEK MEAN DIFF (sign stability)")
rr = pd.Series(d, index=w.week_monday).rolling(52).mean().dropna()
p(f"  fraction of 52wk windows with PCT ahead : {100*(rr>0).mean():.1f}%  (n={len(rr)})")
p(f"  min ${rr.min():,.2f}/wk on {rr.idxmin().date()}   max ${rr.max():,.2f}/wk on {rr.idxmax().date()}")
for y in [2023,2024,2025,2026]:
    s = rr[rr.index.year==y]
    if len(s): p(f"   {y}: mean ${s.mean():>9,.2f}/wk  range [${s.min():>9,.2f}, ${s.max():>9,.2f}]  frac>0 {100*(s>0).mean():5.1f}%")

# ---- did ABS ever lead on cumulative equity
p("\nB6. CUMULATIVE-EQUITY LEAD")
cA = np.cumsum(w.net_ABS.values); cP = np.cumsum(w.net_PCT.values); lead = cP-cA
p(f"  weeks PCT cumulative >= ABS : {int((lead>=0).sum())}/{N} ({100*(lead>=0).mean():.1f}%)")
p(f"  max ABS lead ${-lead.min():,.2f} (wk {w.week_monday.iloc[int(np.argmin(lead))].date()}); "
  f"final PCT lead ${lead[-1]:,.2f}")

# ---- MDE restated against the research claim
p("\nB7. THE +39% CLAIM vs WHAT THIS WINDOW CAN RESOLVE")
sd = d.std(ddof=1); se = sd/np.sqrt(N)
p(f"  recorded research claim  : ABS->PCT = +39.0% weekly dollars at fixed DD ($885 -> $1,231)")
p(f"  this window, fixed $20,245 DD (trade-seq DD): ABS $855.89/wk -> PCT $1,071.02/wk = +25.1%")
p(f"  this window, raw net/week: ABS $1,280.20 -> PCT $1,490.53 = +16.4%")
p(f"  MDE at |t|=2             : ${2*se:,.2f}/wk = +19.1% of ABS net/week")
p(f"  => a +39% effect WOULD have been detectable (${0.39*w.net_ABS.mean():,.2f}/wk vs MDE ${2*se:,.2f}/wk,")
p(f"     {0.39*w.net_ABS.mean()/(2*se):.2f}x the MDE). It was not observed at that size here.")
p(f"  => the +16.4% actually observed is 0.86x the MDE: UNDERPOWERED by construction.")

Path(RUN/"ADJUDICATION_TABLES_B.txt").write_bytes("\n".join(L).encode("utf-8"))
print("\n[written] ADJUDICATION_TABLES_B.txt")
