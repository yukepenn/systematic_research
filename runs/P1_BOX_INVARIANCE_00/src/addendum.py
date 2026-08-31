"""P1_BOX_INVARIANCE_00 - POST-HOC DIAGNOSTIC ADDENDUM.

⚠ EVERYTHING IN THIS FILE IS POST-HOC. It was written AFTER the gate table was printed and it
  CHANGES NO VERDICT. The preregistered verdict (GATE A PASS / GATE B FAIL, nothing frozen,
  no economics) stands exactly as `box_invariance.py` printed it. These diagnostics exist to
  say WHY, and to expose a substrate defect that invalidates one of the three arms.

Still no P&L anywhere.
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "out"))
ARMS = ("DOLLAR", "PRICEBOX", "SIGMABOX")
PV, COMM_RT, TICK = 20.0, 4.36, 5.0        # 1 NQ tick = 0.25 pt = $5.00

_fh = open(os.path.join(OUT, "addendum.txt"), "w", encoding="utf-8")


def P_(*a):
    print(*a, flush=True)
    print(*a, file=_fh)
    _fh.flush()


T = pd.read_csv(os.path.join(OUT, "sessions_primary.csv"))
TM = pd.read_csv(os.path.join(OUT, "sessions_ratematch.csv"))
G = json.load(open(os.path.join(OUT, "gates.json")))

yrs = T.groupby("year").size()
KEEP = yrs[yrs >= 40].index
Ty = T[T.year.isin(KEEP)]
TMy = TM[TM.year.isin(KEEP)]

P_("=" * 114)
P_("=== P1_BOX_INVARIANCE_00 - POST-HOC DIAGNOSTIC ADDENDUM")
P_("=== ⚠ POST-HOC. Changes no verdict. GATE A PASS / GATE B FAIL stands as printed.")
P_("=" * 114)

# ------------------------------------------------------------------ D4 over-dispersion
P_("")
P_("--- D4  OVER-DISPERSION: the level-free version of C1 -----------------------------------")
P_("    C1 (the preregistered criterion) is a RAW RANGE and is therefore sensitive to both the")
P_("    arm's latch-rate LEVEL and to sampling noise. The statistically correct stability")
P_("    statistic is between-year heterogeneity measured against the binomial sampling floor.")
P_("    ⚠ sessions within a year are NOT independent, so every chi2 below is inflated by the")
P_("    same serial-correlation factor. Read the RATIOS between arms, never the absolute chi2.")
P_("")
P_(f"{'arm':<11}{'r_bar':>8}{'SD(r_y)':>10}{'binom SD':>10}{'ratio':>8}{'chi2':>10}{'df':>5}"
   f"{'excess SD':>11}")
D4 = {}
for a in ARMS:
    ry = Ty.groupby("year")[f"lat_{a}"].mean()
    ny = Ty.groupby("year").size()
    rbar = float(Ty[f"lat_{a}"].mean())
    sd_obs = float(ry.std(ddof=1))
    sd_bin = float(np.sqrt(np.mean(rbar * (1 - rbar) / ny.to_numpy())))
    chi2 = float(np.sum(ny.to_numpy() * (ry.to_numpy() - rbar) ** 2 / (rbar * (1 - rbar))))
    df = len(ry) - 1
    exc = float(np.sqrt(max(sd_obs ** 2 - sd_bin ** 2, 0.0)))
    D4[a] = dict(rbar=rbar, sd_obs=sd_obs, sd_bin=sd_bin, ratio=sd_obs / sd_bin,
                 chi2=chi2, df=df, excess=exc)
    P_(f"{a:<11}{rbar:>8.3f}{sd_obs:>10.4f}{sd_bin:>10.4f}{sd_obs/sd_bin:>8.2f}"
       f"{chi2:>10.0f}{df:>5}{exc:>11.4f}")
P_("")
P_(f"    SIGMABOX's year-to-year dispersion is {D4['DOLLAR']['ratio']/D4['SIGMABOX']['ratio']:.1f}x"
   f" smaller than DOLLAR's relative to the sampling floor, and "
   f"{D4['PRICEBOX']['ratio']/D4['SIGMABOX']['ratio']:.1f}x smaller than PRICEBOX's.")
P_("    It is nonetheless NOT flat: at ratio "
   f"{D4['SIGMABOX']['ratio']:.2f} it is still real heterogeneity, not noise.")

# ------------------------------------------------------------------ D5 leave-one-year-out
P_("")
P_("--- D5  LEAVE-ONE-YEAR-OUT on C1 (the tail audit the directive requires) ------------------")
P_("    The preregistered C1 threshold is range >= 0.20. SIGMABOX printed 0.180 on the primary")
P_("    calibration and 0.204 / 0.207 on the two robustness variants. That is a knife edge, so")
P_("    the honest question is: which single year decides it?")
P_("")
for lab, TT in (("primary", Ty), ("rate-matched", TMy)):
    P_(f"    [{lab}]")
    P_(f"{'':<8}{'drop year':<12}" + "".join(f"{a:>12}" for a in ARMS))
    base = {a: TT.groupby('year')[f'lat_{a}'].mean() for a in ARMS}
    P_(f"{'':<8}{'(none)':<12}" + "".join(f"{base[a].max()-base[a].min():>12.4f}" for a in ARMS))
    worst = []
    for y in sorted(TT.year.unique()):
        r = {a: base[a].drop(y) for a in ARMS}
        worst.append((r["SIGMABOX"].max() - r["SIGMABOX"].min(), y,
                      [r[a].max() - r[a].min() for a in ARMS]))
    worst.sort()
    for v, y, rr in worst[:3] + worst[-2:]:
        P_(f"{'':<8}{y:<12}" + "".join(f"{x:>12.4f}" for x in rr))
    P_("")

# ------------------------------------------------------------------ D6 the fixed-cost floor
P_("--- D6  THE FIXED-COST FLOOR: why NO normalisation is exactly scale-invariant -------------")
P_("    C3b already showed it: rescale prices and leave the $4.36 commission alone and EVERY")
P_("    arm's decision series changes, PRICEBOX and SIGMABOX included. Commission is a fixed")
P_("    dollar term inside the same accumulator the box reads, so a proportional box cannot")
P_("    be proportional at the bottom of the vol range. Here is where that bites.")
P_("")
P_(f"{'year':<7}{'medSig':>8}" + "".join(f"{'$'+a[:3]:>9}{'tk':>7}{'comm%':>8}" for a in ARMS))
for y in sorted(Ty.year.unique()):
    g = Ty[Ty.year == y]
    row = f"{y:<7}{g['sig'].median():>8.0f}"
    for a in ARMS:
        h = float(g[f"halt_{a}"].median())
        row += f"{h:>9,.0f}{h/TICK:>7.0f}{100*COMM_RT/h:>8.2f}"
    P_(row)
P_("")
g06 = Ty[Ty.year <= 2007]
for a in ARMS:
    h = float(g06[f"halt_{a}"].median())
    P_(f"    2006-07 median box, {a:<9} ${h:>8,.0f}  = {h/TICK:>5.0f} ticks   "
       f"commission is {100*COMM_RT/h:>5.2f} % of the whole budget")
P_("    ⚠ THIS is what SIGMABOX's 2006 latch rate of 0.739 is: at a 19-point median session")
P_("    range the vol-scaled box is a ~14-tick budget, small enough that ordinary bid/ask")
P_("    granularity and a fixed commission dominate it. The volatility-scaled box has a FLOOR")
P_("    it cannot scale below, and 2006-2007 is under that floor.")

# ------------------------------------------------------------------ D7 substrate validity
P_("")
P_("--- D7  ⚠ SUBSTRATE DEFECT: one of the three arms reads an invalid quantity ---------------")
P_("    The substrate is `nq1m_2005_202605.parquet`, documented in W9's own spec as an")
P_("    'NQ 09-26 BACK-ADJUSTED merge', and in research/original_trader_reconstruction/")
P_("    DATA_AUDIT.md as: 'Different back-adjust offsets than canonical ledger")
P_("    (POINT-DIFFERENCES INVARIANT; LEVELS/RATIOS NOT).'")
P_("")
P_(f"    Observed here: median session open 2006 = {Ty[Ty.year==2006]['P'].median():,.0f} and")
P_(f"    2026 = {Ty[Ty.year==2026]['P'].median():,.0f}, a ratio of "
   f"{Ty[Ty.year==2026]['P'].median()/Ty[Ty.year==2006]['P'].median():.2f}x, against a median")
P_(f"    session RANGE that goes {Ty[Ty.year==2006]['sig'].median():,.0f} -> "
   f"{Ty[Ty.year==2026]['sig'].median():,.0f} pts, a ratio of "
   f"{Ty[Ty.year==2026]['sig'].median()/Ty[Ty.year==2006]['sig'].median():.1f}x. Ranges are")
P_("    point differences and are trustworthy; the level is a back-adjusted level and is not.")
P_("")
P_("    CONSEQUENCE, per input:")
P_("      DOLLAR    reads no market quantity at all           -> VALID")
P_("      SIGMABOX  reads session (high - low), a POINT DIFF  -> VALID")
P_("      PRICEBOX  reads the session OPEN LEVEL              -> ⚠ INVALID on this substrate")
P_("      C1  latch-rate stability      -> VALID for all arms (C1 reads no level)")
P_("      C5  realized-vol sensitivity  -> VALID (log of a point difference)")
P_("      C4  price-level sensitivity   -> ⚠ magnitude NOT interpretable")
P_("      C2  joint state conditionality-> ⚠ partially contaminated (log P is one of two regressors)")
P_("")
P_("    DOES THE VERDICT SURVIVE? Recompute both gates using ONLY the uncontaminated criteria.")
pr = G["primary"]
valid_breach = {a: int(pr[a]["c1_range"] >= 0.20) + int(abs(pr[a]["c5_delta"]) >= 0.15)
                + int(not G["c3"][a]["a"]) for a in ARMS}
P_(f"      breaches on the 3 uncontaminated criteria {{C1, C3, C5}}: "
   + ", ".join(f"{a} {valid_breach[a]}/3" for a in ARMS))
P_(f"      GATE A needs >= 3 of 5 -> DOLLAR reaches {valid_breach['DOLLAR']} on the "
   f"uncontaminated three alone  ->  "
   f"{'GATE A SURVIVES' if valid_breach['DOLLAR'] >= 3 else 'GATE A DOES NOT SURVIVE'}")
P_("      GATE B failed on clauses (iv)/(v), both driven by C1 alone, which is uncontaminated")
P_("      ->  GATE B's FAIL SURVIVES.")
P_("")
P_("    ⚠ IT ALSO CORRECTS A FIGURE THE DIRECTIVE TREATS AS VERIFIED. 'The box was ~43.4 bp of")
P_("    index in 2022 and ~24.6 bp now' is 65 pts / 14,977 and 65 / 26,423 - both computed on")
P_("    this back-adjusted level. The repo's own DATA_AUDIT says ratios on this series are not")
P_("    valid. The DIRECTION (the box shrank relative to price) is right; the BASIS POINTS are")
P_("    not index basis points and should not be quoted as such.")

# ------------------------------------------------------------------ D8 was C1 even usable?
P_("")
P_("--- D8  I AUDIT MY OWN PREREGISTERED CRITERION ------------------------------------------")
P_("    C1 was declared as a RAW max-min range of 21 annual rates with n_y ~ 150. Before")
P_("    interpreting it, calibrate it against a null in which the rule is EXACTLY invariant:")
P_("    draw each year's latch count as Binomial(n_y, r_bar) and look at the range that pure")
P_("    sampling noise alone produces. 20,000 draws, seed 20260831.")
P_("")
rng = np.random.default_rng(20260831)
ny = Ty.groupby("year").size().to_numpy()
P_(f"{'arm':<11}{'r_bar':>8}{'observed range':>16}{'null p50':>10}{'null p95':>10}"
   f"{'P(range>=0.20)':>16}{'verdict on the criterion':>28}")
D8 = {}
for a in ARMS:
    rbar = float(Ty[f"lat_{a}"].mean())
    sim = rng.binomial(ny[None, :], rbar, size=(20000, len(ny))) / ny[None, :]
    rg = sim.max(1) - sim.min(1)
    obs = float(Ty.groupby("year")[f"lat_{a}"].mean().max()
                - Ty.groupby("year")[f"lat_{a}"].mean().min())
    pge = float(np.mean(rg >= 0.20))
    D8[a] = dict(obs=obs, p50=float(np.percentile(rg, 50)),
                 p95=float(np.percentile(rg, 95)), p_ge_020=pge)
    v = "threshold has NO power" if pge > 0.25 else ("usable" if pge < 0.05 else "weak")
    P_(f"{a:<11}{rbar:>8.3f}{obs:>16.4f}{np.percentile(rg,50):>10.4f}"
       f"{np.percentile(rg,95):>10.4f}{pge:>16.3f}{v:>28}")
P_("")
P_("    ⚠ READ THIS AGAINST MY OWN GATE. For an arm latching near 0.6, an EXACTLY INVARIANT")
P_(f"    rule already produces a median range of {D8['SIGMABOX']['p50']:.3f} and exceeds the")
P_(f"    0.20 threshold {100*D8['SIGMABOX']['p_ge_020']:.0f} % of the time from sampling noise alone.")
_rb = float(Ty["lat_SIGMABOX"].mean())
_sim = rng.binomial(ny[None, :], _rb, size=(40000, len(ny))) / ny[None, :]
_rg = _sim.max(1) - _sim.min(1)
P_("    My C1 threshold therefore could not distinguish a perfectly invariant vol-scaled box")
P_("    from noise. SIGMABOX's three observed ranges sit at these percentiles of the")
P_("    EXACTLY-INVARIANT null: " + ", ".join(
    f"{v:.3f} -> {100*float(np.mean(_rg <= v)):.0f}th (p={float(np.mean(_rg >= v)):.3f})"
    for v in (0.1797, 0.2039, 0.2068)) + ".")
P_("    None of the three is significant at any conventional level: on the criterion I chose,")
P_("    SIGMABOX is statistically indistinguishable from a PERFECTLY invariant rule, and it")
P_("    still failed my gate because the gate was a bare threshold on a noisy statistic.")
P_("    THE GATE IS STILL RECORDED FAILED. A criterion is not repaired after seeing its")
P_("    result. What this licenses is a SUCCESSOR RUN with a criterion that has power -")
P_("    the over-dispersion ratio of D4 - preregistered before it is computed on anything new.")
P_(f"    For DOLLAR the threshold did have power: observed {D8['DOLLAR']['obs']:.3f} against a")
P_(f"    null p95 of {D8['DOLLAR']['p95']:.3f}. GATE A is unaffected by this audit.")

json.dump(dict(d4=D4, d8=D8, valid_breach=valid_breach),
          open(os.path.join(OUT, "addendum.json"), "w"), indent=1)
P_("")
P_("[addendum done - no verdict changed, no P&L computed]")
_fh.close()
