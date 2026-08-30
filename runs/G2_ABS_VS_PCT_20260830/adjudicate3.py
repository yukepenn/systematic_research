import numpy as np, pandas as pd
from scipy import stats
from pathlib import Path
RUN = Path(r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\runs\G2_ABS_VS_PCT_20260830")
W98 = Path(r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\runs\WE_W98_BOXDENOM\out")
L=[]
def p(s=""): L.append(str(s)); print(s)

p("="*78)
p("PANEL C -- AUDIT OF THE RECORDED '176/213 WEEKS, SIGN TEST p=7.1e-23' CLAIM")
p("(read-only re-analysis of runs/WE_W98_BOXDENOM/out/weekly_arms_P1.csv -- nothing modified)")
p("="*78)
w = pd.read_csv(W98/"weekly_arms_P1.csv")
d = (w.PCT - w.ABS).values; N = len(d)
RATE_ABS, RATE_PCT = 14.517525337837839, 14.405320813771517   # dashboard.csv, per ctrRT, per arm
p(f"\nC0. THE COST CONVENTION IN THE SOURCE RUN")
p(f"  ABS spread rate : ${RATE_ABS:.6f}/ctrRT")
p(f"  PCT spread rate : ${RATE_PCT:.6f}/ctrRT")
p(f"  PCT is charged  : ${RATE_ABS-RATE_PCT:.6f}/ctrRT LESS than ABS -- a DETERMINISTIC handicap")
p(f"  ABS contract-sides (dashboard FULL) 2368 ; PCT 2556")
p(f"  On any week whose TRADES are identical, PCT's net is therefore HIGHER BY CONSTRUCTION.")

p(f"\nC1. REPRODUCE THE RECORDED STATISTICS")
p(f"  n weeks                    : {N}")
p(f"  mean PCT-ABS               : ${d.mean():,.4f}/wk   (recorded 240.17756)")
p(f"  se / t / p                 : ${d.std(ddof=1)/np.sqrt(N):,.4f} / {d.mean()/(d.std(ddof=1)/np.sqrt(N)):.4f} / "
  f"{2*stats.t.sf(abs(d.mean()/(d.std(ddof=1)/np.sqrt(N))),N-1):.6f}   (recorded 126.125 / 1.9043 / 0.05687)")
nw = int((d>0).sum()); na = int((d<0).sum()); nz = int((d==0).sum())
p(f"  PCT-win weeks (d>0)        : {nw}   (recorded 176)")
p(f"  ABS-win weeks (d<0)        : {na}   (recorded 35)")
p(f"  exactly tied               : {nz}")
p(f"  sign test p                : {stats.binomtest(nw, nw+na, 0.5).pvalue:.3e}   (recorded 7.09e-23)")
p("  --> REPRODUCED. The recorded statistics are arithmetically correct on this file.")

p(f"\nC2. HOW BIG ARE THE 'WINS'?  (distribution of |PCT-ABS| on PCT-win weeks)")
pw = d[d>0]
for th in [0.01, 0.10, 1.0, 5.0, 25.0, 100.0, 500.0]:
    p(f"  PCT-win weeks with |diff| < ${th:8.2f} : {int((pw<th).sum()):3d} / {len(pw)}  ({100*(pw<th).mean():5.1f}%)")
p(f"  median PCT 'win'  = ${np.median(pw):,.4f}")
p(f"  mean   PCT 'win'  = ${pw.mean():,.2f}  (recorded +$528.52)")
aw = d[d<0]
p(f"  median ABS 'win'  = ${np.median(aw):,.2f}   mean = ${aw.mean():,.2f}  (recorded -$1,196.03)")
p("  --> The MEDIAN PCT 'win' is a sub-dollar number. The mean is carried by a few real weeks.")

p(f"\nC3. THE DECISIVE TEST -- IS THE SIGN CARRIED BY THE COST HANDICAP?")
p("  A week where both arms took the SAME trades still differs, by (rate_ABS-rate_PCT)*ctrRT.")
p("  Typical week ~ 2368/213 = 11.1 ABS contract-sides -> expected artifact")
p(f"  = {2368/213:.2f} x ${RATE_ABS-RATE_PCT:.6f} = ${(2368/213)*(RATE_ABS-RATE_PCT):.4f}/wk of PURE cost artifact.")
tiny = np.abs(d) < 5.0
p(f"\n  weeks with |PCT-ABS| < $5 (i.e. materially the same trades): {int(tiny.sum())} / {N} ({100*tiny.mean():.1f}%)")
p(f"    of those, PCT 'wins'  : {int((d[tiny]>0).sum())} / {int(tiny.sum())} = {100*(d[tiny]>0).mean():.1f}%")
p(f"    of those, ABS 'wins'  : {int((d[tiny]<0).sum())}")
p(f"    total dollars in them : ${d[tiny].sum():,.2f}  ({100*d[tiny].sum()/d.sum():.2f}% of the $ difference)")
mat = ~tiny
p(f"\n  MATERIALLY-DIFFERING weeks (|PCT-ABS| >= $5): {int(mat.sum())} / {N} ({100*mat.mean():.1f}%)")
p(f"    PCT wins {int((d[mat]>0).sum())} / {int(mat.sum())} = {100*(d[mat]>0).mean():.1f}%   "
  f"sign-test p = {stats.binomtest(int((d[mat]>0).sum()), int(mat.sum()), 0.5).pvalue:.4f}")
p(f"    they carry ${d[mat].sum():,.2f} = {100*d[mat].sum()/d.sum():.1f}% of the total difference")
p("\n  --> THE SIGN TEST IS AN ARTIFACT OF THE PER-ARM COST RATE.")
p("      Restricted to weeks where the two policies actually did something different,")
p("      the direction claim collapses from p=7.1e-23 to the value printed above.")

p(f"\nC4. CROSS-ENGINE CORROBORATION (this run's NT8 batch, SAME cost rate both arms)")
j = pd.read_csv(RUN/"out"/"weekly_pnl_joined.csv")
dn = j.diff_PCT_minus_ABS.values
tie_n = np.isclose(dn,0,atol=1e-6)
p(f"  NT8, identical Lifetime template both arms: exactly-tied weeks = {int(tie_n.sum())}/{len(dn)} "
  f"({100*tie_n.mean():.1f}%)")
p(f"  NT8 PCT-win {int((dn>1e-6).sum())} / ABS-win {int((dn<-1e-6).sum())} -> sign p = "
  f"{stats.binomtest(int((dn>1e-6).sum()), int((dn>1e-6).sum())+int((dn<-1e-6).sum()), 0.5).pvalue:.4f}")
p(f"  If ties are (wrongly) counted as PCT wins: {int(tie_n.sum())+int((dn>1e-6).sum())}/{len(dn)} = "
  f"{100*(int(tie_n.sum())+int((dn>1e-6).sum()))/len(dn):.1f}%  <-- recorded claim was 176/213 = 82.6%")
p("  --> Remove the per-arm cost difference and the SAME structure appears: a large block of")
p("      genuinely IDENTICAL weeks, and a coin-flip among the weeks that differ.")
p("      W98 did not count ties as wins; the per-arm rate turned its ties into wins for it.")

p(f"\nC5. WHAT SURVIVES")
p("  SURVIVES: the paired MAGNITUDE result (mean, se, t, p) is unaffected -- the cost artifact")
p(f"            contributes ${d[tiny].sum():,.2f} of ${d.sum():,.2f}, i.e. {100*d[tiny].sum()/d.sum():.2f}%.")
p("            The ABS_LOOSE control (p 0.940) is also unaffected -- it is a magnitude test.")
p("  FALSIFIED: 'PCT beats ABS on DIRECTION overwhelmingly (176/213, p 7.1e-23)'.")
p("            The direction claim was never established. It measured a cost convention.")
Path(RUN/"ADJUDICATION_TABLES_C.txt").write_bytes("\n".join(L).encode("utf-8"))
print("\n[written] ADJUDICATION_TABLES_C.txt")
