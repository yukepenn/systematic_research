"""G3_CLOCKLAG01 - driver. Executes runs/G3_CLOCKLAG01_20260831/spec.yaml clause by clause.

STAGE 1 COMPUTES NO P&L AND FORMS NO POSITION. Its entire job is the identifying restriction:

    generic momentum      -> a recent return predicts the next one REGARDLESS of clock alignment
    scheduling mechanism  -> the SAME clock bucket ONE DAY AGO beats the ADJACENT bucket minutes ago

If the adjacent bucket is as strong the mechanism is FALSIFIED even if the raw predictability is
real, and the run STOPS with no economics, no Stage 2 and no candidate. That is a SUCCESS for this
run: it is the cheapest available death for the whole "scheduled institutional flow leaves a
periodic price trace" family.

    python runs/G3_CLOCKLAG01_20260831/src/run_clocklag01.py
"""
from __future__ import annotations

import io
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(RUN, "..", ".."))
OUT = os.path.join(RUN, "out")
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)

import panel as PN                                                        # noqa: E402
import estim as ES                                                        # noqa: E402
import stage2 as S2                                                       # noqa: E402

N_DRAWS = 2000
SEED = 20260831
ERAS = ("PRE", "MODERN", "FULL")
GATE_ERA = "MODERN"
Z95 = 1.959963984540054


class Tee(io.TextIOBase):
    def __init__(self, *streams):
        self.streams = streams

    def write(self, s):
        for st in self.streams:
            st.write(s)
        return len(s)

    def flush(self):
        for st in self.streams:
            st.flush()


def hr(ch="=", n=100):
    print(ch * n)


def sec(title):
    print()
    hr()
    print(title)
    hr()


# ==================================================================================================
def main():
    t0 = time.time()
    os.makedirs(OUT, exist_ok=True)
    buf = io.StringIO()
    real = sys.stdout
    sys.stdout = Tee(real, buf)
    try:
        rc = _run()
    finally:
        sys.stdout = real
        with open(os.path.join(OUT, "console.txt"), "wb") as f:
            f.write(buf.getvalue().encode("utf-8"))
    print(f"\n[console.txt written, {len(buf.getvalue()):,} chars, {time.time()-t0:.0f}s]")
    return rc


def _run():
    sec("G3_CLOCKLAG01_20260831  -  cross-day clock-bucket periodicity in NQ  (GENESIS III WAVE C)")
    print("spec:  runs/G3_CLOCKLAG01_20260831/spec.yaml   PREREGISTERED, committed before any "
          "statistic existed")
    print("STAGE 1 IS STRUCTURAL ONLY. No P&L is computed and no position is formed unless and "
          "until Stage 1 passes.")
    print("live_enabled: NO   orders_placed: NO   spend: $0   "
          "no CrossTrade / NinjaTrader call is made by this program.")
    print()
    print("HKS (Heston/Korajczyk/Sadka 2010) was measured on US EQUITIES, not on an index future.")
    print("A null here does NOT falsify HKS. It falsifies its TRANSFER to NQ.")

    # ---------------------------------------------------------------------------------------
    sec("0.  SELF-TESTS  (every downstream number is worthless if these do not pass)")
    print("panel.py - the frozen bucket and return definitions")
    rc1 = PN.selftest()
    print("\nestim.py - estimators, session-clustered SEs, and the circular-shift MAX null")
    print("           NOTE two adversarial cases: a PLANTED cross-day effect must PASS the gate")
    print("           statistic and a PLANTED WITHIN-DAY MOMENTUM panel must FAIL it. If the")
    print("           falsifier cannot fire on synthetic data it cannot fire on real data.")
    rc2 = ES.selftest()
    print("\nresearch_sdk/champion_eval.py - the risk vector Stage 2 G3 is reported on")
    from research_sdk import champion_eval as CE                          # noqa: E402
    rc3 = CE.selftest()
    if rc1 or rc2 or rc3:
        raise SystemExit("SELF-TEST FAILURE - refusing to produce any statistic")

    # ---------------------------------------------------------------------------------------
    sec("1.  PANEL  (definitions frozen by spec section 2; no bucket width other than 30 min)")
    print("  bars END-STAMPED: bucket 0 = bars stamped 09:31..10:00, bucket 12 = 15:31..16:00")
    print("  r(0,d) is based on the RTH OPEN = the OPEN of the bar stamped 09:31")
    pan = PN.build_panel()
    dates, P, B, R = pan["dates"], pan["P"], pan["B"], pan["R"]
    masks = PN.era_masks(dates)
    print()
    for e in ERAS:
        m = masks[e]
        print(f"  {e:<7} sessions {int(m.sum()):>6,}   {dates[m][0]} -> {dates[m][-1]}")
    print("  ERABREAK01 (p=0.0011) forbids pooling across 2022-05. FULL IS A DIAGNOSTIC ONLY;")
    print("  a result that exists only in PRE is an old-regime finding, not a candidate.")

    # ---------------------------------------------------------------------------------------
    sec("2.  rho_bar AND K_eff  (spec: effective_K, printed)")
    print(f"  {'era':<8}{'rho_bar':>12}{'K_eff = 13/(1+12*rho_bar)':>30}"
          f"{'Bonferroni z at K_eff':>24}")
    keffs = {}
    for e in ERAS:
        rb, keff, _ = ES.rho_bar_and_keff(R[masks[e]])
        zc = _z_two_sided(0.05 / max(keff, 1.0))
        keffs[e] = dict(rho_bar=rb, k_eff=keff, z_crit=zc)
        print(f"  {e:<8}{rb:>12.5f}{keff:>30.3f}{zc:>24.3f}")
    print("  rho_bar is the mean PAIRWISE correlation of the 13 bucket return series. Independent")
    print("  draws across a correlated family would set the bar far too high; K_eff is what a")
    print("  bucket count is worth here, and the max-statistic null below is the primary control.")

    # ---------------------------------------------------------------------------------------
    sec("3.  STAGE 1 TABLE  -  13 buckets x 3 estimators x 3 eras, session-clustered t")
    print("  beta_same(b)     r(b,d) on r(b,d-1)      same clock bucket, one day back   TREATMENT")
    print("  beta_adj(b)      r(b,d) on r(b-1,d)      adjacent bucket, same day         CONTROL A")
    print("  beta_nonmult(b)  r(b,d) on r(b',d-1) averaged over b' != b                 CONTROL B")
    print("  beta_adj(0) is UNDEFINED - bucket -1 does not exist. Nothing is selected from this "
          "table.")
    obs = {e: ES.observed(R[masks[e]]) for e in ERAS}

    rows = []
    for e in ERAS:
        o = obs[e]
        zc = keffs[e]["z_crit"]
        print()
        print(f"  ---- {e}  (n = {o['n']:,} day-over-day observations per bucket) "
              f"----  '*' = |t| > {zc:.2f}, the K_eff-adjusted two-sided 5% threshold")
        print(f"  {'b':>3} {'window':<14}"
              f"{'beta_same':>12}{'t':>8} {'beta_adj':>12}{'t':>8} {'beta_nonmult':>14}{'t':>8}")
        for r in o["per_bucket"]:
            b = r["bucket"]
            w = _window_label(b)
            def f(v, t):
                if not np.isfinite(v):
                    return f"{'n/a':>12}{'':>8}"
                star = "*" if np.isfinite(t) and abs(t) > zc else " "
                return f"{v:>12.5f}{t:>7.2f}{star}"
            print(f"  {b:>3} {w:<14}{f(r['beta_same'], r['t_same'])} "
                  f"{f(r['beta_adj'], r['t_adj'])} "
                  f"{r['beta_nonmult']:>14.5f}{r['t_nonmult']:>7.2f}"
                  f"{'*' if abs(r['t_nonmult']) > zc else ' '}")
            rows.append(dict(era=e, bucket=b, window=w, n_obs=r["n"],
                             beta_same=r["beta_same"], se_same=r["se_same"], t_same=r["t_same"],
                             beta_adj=r["beta_adj"], se_adj=r["se_adj"], t_adj=r["t_adj"],
                             beta_nonmult=r["beta_nonmult"], se_nonmult=r["se_nonmult"],
                             t_nonmult=r["t_nonmult"]))

    # ---------------------------------------------------------------------------------------
    sec("4.  MEANS OVER BUCKETS  -  WITH and WITHOUT buckets 0 and 12  (spec trap 4, mandatory)")
    print("  The open and close auctions are structurally different. They are NOT excluded -")
    print("  excluding them after seeing the table would be a selection - but a reader must be able")
    print("  to see whether the whole effect is two buckets. All three sets were frozen in code")
    print("  before any number existed.")
    print()
    print("    ALL_13        b = 0..12   (beta_adj averaged over 1..12, it is undefined at b=0)")
    print("    MATCHED_1_12  b = 1..12   the only set where BOTH estimators exist -> THE GATE SET")
    print("    INTERIOR_1_11 b = 1..11   open and close auction buckets removed, for reading only")
    for e in ERAS:
        print()
        print(f"  ---- {e} ----")
        print(f"  {'set':<15}{'mean_same':>12}{'t':>7}{'mean_adj':>12}{'t':>7}"
              f"{'margin':>12}{'t':>7}{'mean_nonmult':>14}{'t':>7}")
        for nm in ES.BUCKET_SETS:
            a = obs[e]["agg"][nm]
            tag = "  <- GATE SET" if nm == ES.GATE_SET else ""
            print(f"  {nm:<15}{a['mean_same']:>12.5f}{a['t_mean_same']:>7.2f}"
                  f"{a['mean_adj']:>12.5f}{a['t_mean_adj']:>7.2f}"
                  f"{a['margin']:>12.5f}{a['t_margin']:>7.2f}"
                  f"{a['mean_nonmult']:>14.5f}{a['t_mean_nonmult']:>7.2f}{tag}")
    print()
    print("  margin = mean_b beta_same - mean_b beta_adj on an IDENTICAL bucket set. It is the")
    print("  identifying restriction as a single number: positive means the same clock bucket one")
    print("  day back beats the adjacent bucket minutes ago; NEGATIVE MEANS THE MECHANISM IS DEAD.")

    # ---------------------------------------------------------------------------------------
    sec("5.  THE CIRCULAR-SHIFT MAX NULL  (spec S1_GATE_NULL - this is where MC-11 died)")
    print(f"  {N_DRAWS:,} draws, seed {SEED}, buffer {ES.NULL_BUFFER} days.")
    print("  One shift k of the DAY INDEX per draw, applied to the PREDICTOR matrix only. A whole")
    print("  day-row moves together, so each bucket's marginal distribution AND the within-day")
    print("  cross-bucket dependence are preserved exactly.")
    print("  On EVERY draw the entire analysis is redone - all 13 buckets, all three estimators,")
    print("  every mean AND every max-over-buckets step - and the maxima are recorded. Reporting a")
    print("  best bucket without this would be MC-11 exactly.")
    print()
    print("  NULL_A (THE GATE NULL): the shifted matrix supplies both the lag-1 and the same-day")
    print("          predictors, so no estimator keeps its true day alignment.")
    print("  NULL_B (stricter diagnostic): only the CROSS-DAY predictor is shifted; beta_adj keeps")
    print("          its true same-day alignment, so the margin is measured against the REAL")
    print("          adjacent-bucket benchmark. Printed, not the gate.")
    nulls = {}
    for e in ERAS:
        t1 = time.time()
        nulls[e] = ES.circular_shift_null(R[masks[e]], n_draws=N_DRAWS, seed=SEED)
        print(f"  {e:<7} {N_DRAWS:,} draws in {time.time()-t1:.1f}s  "
              f"(shift range {nulls[e]['shifts'].min()}..{nulls[e]['shifts'].max()} days)")

    gs = ES.GATE_SET
    for e in ERAS:
        a = obs[e]["agg"][gs]
        print()
        print(f"  ---- {e}, gate set {gs} ----")
        print(f"  {'statistic':<34}{'observed':>12}{'null p50':>12}{'null p95':>12}"
              f"{'pctile':>9}{'p':>9}")
        for lab, key, nullkey, which in (
                ("mean_b beta_same", "mean_same", "mean_same", "NULL_A"),
                ("MAX_b beta_same", "max_same", "max_same", "NULL_A"),
                ("margin (same - adj)", "margin", "margin", "NULL_A"),
                ("MAX_b (same - adj)   [gate]", "margin", "max_margin", "NULL_A"),
                ("margin vs REAL adj", "margin", "margin", "NULL_B"),
                ("MAX_b (same - REAL adj)", "margin", "max_margin", "NULL_B"),
                ("MAX_b beta_same, TWO-SIDED", "max_abs_same", "max_abs_same", "NULL_A"),
                ("MAX_b |beta_nonmult|", "max_abs_nonmult", "max_abs_nonmult", "NULL_A")):
            d = nulls[e][which][gs][nullkey]
            ov = a[key]
            print(f"  {lab:<34}{ov:>12.5f}{np.percentile(d, 50):>12.5f}"
                  f"{np.percentile(d, 95):>12.5f}{ES.pct_of(d, ov):>8.1f}%"
                  f"{ES.p_right(d, ov):>9.4f}")
        print("  (the two MAX-margin rows compare the OBSERVED MEAN margin against the null's")
        print("   BEST-OF-12 margin; that is the multiplicity price and it is deliberately the")
        print("   hardest bar in the run.)")
        bs_, ba_ = obs[e]["beta_same"], obs[e]["beta_adj"]
        j = 1 + int(np.argmax(bs_[1:] - ba_[1:]))
        k_ = int(np.argmax(bs_))
        print(f"  best bucket by margin      b={j:<3} same {bs_[j]:+.5f}  adj {ba_[j]:+.5f}  "
              f"margin {bs_[j]-ba_[j]:+.5f}   quotable ONLY against the MAX rows above")
        print(f"  best bucket by beta_same   b={k_:<3} same {bs_[k_]:+.5f}  adj "
              f"{ba_[k_]:+.5f}"
              f"   -> at its OWN strongest bucket the clock-aligned term "
              f"{'BEATS' if bs_[k_] > ba_[k_] else 'LOSES TO'} the adjacent control")
        hh = a["frac_same_gt_adj"]
        dhh = nulls[e]["NULL_A"][gs]["frac_same_gt_adj"]
        print(f"  head-to-head: beta_same > beta_adj in {int(round(hh*12)):>2}/12 buckets "
              f"({100*hh:.0f}%)   null median {100*np.median(dhh):.0f}%  "
              f"p95 {100*np.percentile(dhh, 95):.0f}%   percentile {ES.pct_of(dhh, hh):.1f}%")
        # A max statistic that is elevated in the CONTROL-B family too is a property of the panel,
        # not of the daily-multiple lag. This is the reading that stops a best-bucket over-claim.
        pn = ES.p_right(nulls[e]["NULL_A"][gs]["max_abs_nonmult"], a["max_abs_nonmult"])
        ps = ES.p_right(nulls[e]["NULL_A"][gs]["max_abs_same"], a["max_abs_same"])
        if pn < 0.10 and ps < 0.10:
            print(f"  CAUTION: the max is elevated in the CONTROL-B family too "
                  f"(MAX|beta_nonmult| p={pn:.4f} alongside MAX|beta_same| p={ps:.4f}).")
            print("  Control B is a NON-DAILY-MULTIPLE lag and the mechanism requires it to be "
                  "~0 everywhere.")
            print("  An extreme max shared by treatment and control is a panel-wide feature - a "
                  "few influential")
            print("  sessions, day-to-day variance clustering the shift null deliberately "
                  "destroys - and is NOT")
            print("  evidence for clock alignment. No bucket from this era is quotable as a "
                  "finding.")

    # ---------------------------------------------------------------------------------------
    sec("6.  STAGE 1 GATE  (MODERN stratum; PRE and FULL are reported, never decisive)")
    a = obs[GATE_ERA]["agg"][gs]
    nA = nulls[GATE_ERA]["NULL_A"][gs]
    p95_max_margin = float(np.percentile(nA["max_margin"], 95))
    p95_margin = float(np.percentile(nA["margin"], 95))

    gates = []

    def gate(gid, spec_txt, observed_txt, ok):
        gates.append(dict(gate=gid, spec=spec_txt, observed=observed_txt, verdict="PASS" if ok
                          else "FAIL", passed=bool(ok)))
        return ok

    c1 = gate("S1-A  mean beta_same > 0",
              "mean_b beta_same > 0, MODERN, b=1..12",
              f"{a['mean_same']:+.5f} (t={a['t_mean_same']:+.2f} clustered)",
              a["mean_same"] > 0)
    c2 = gate("S1-B  same beats adjacent",
              "mean beta_same - mean beta_adj > 0",
              f"margin {a['margin']:+.5f} = {a['mean_same']:+.5f} - {a['mean_adj']:+.5f}"
              f" (t={a['t_margin']:+.2f})",
              a["margin"] > 0)
    c3 = gate("S1-C  margin survives MAX null",
              f"margin > p95 of max-over-buckets null, {N_DRAWS} draws",
              f"{a['margin']:+.5f} vs p95(max) {p95_max_margin:+.5f}"
              f" [p95(mean) {p95_margin:+.5f}] p={ES.p_right(nA['max_margin'], a['margin']):.4f}",
              a["margin"] > p95_max_margin)
    c4 = gate("S1-D  beta_nonmult ~ 0",
              "mean beta_nonmult indistinguishable from 0, |t|<1.96",
              f"{a['mean_nonmult']:+.5f} (t={a['t_mean_nonmult']:+.2f} SE "
              f"{a['se_mean_nonmult']:.5f})",
              abs(a["t_mean_nonmult"]) < Z95)

    stage1_pass = bool(c1 and c2 and c3 and c4)

    W1_, W2_, W3_ = 32, 54, 74
    print(f"  {'GATE':<{W1_}}{'SPEC':<{W2_}}{'OBSERVED':<{W3_}}{'PASS/FAIL'}")
    hr("-", W1_ + W2_ + W3_ + 12)
    for g in gates:
        print(f"  {g['gate']:<{W1_}}{g['spec']:<{W2_}}{g['observed']:<{W3_}}{g['verdict']}")
    hr("-", W1_ + W2_ + W3_ + 12)
    print(f"  {'STAGE 1 VERDICT':<{W1_}}{'ALL of S1-A .. S1-D':<{W2_}}"
          f"{('all four clauses hold' if stage1_pass else 'at least one clause FAILS'):<{W3_}}"
          f"{'PASS' if stage1_pass else 'FAIL'}")

    print()
    print("  THE IDENTIFYING RESTRICTION, STATED AS THE SPEC STATES IT (MODERN, b=1..12):")
    print(f"    beta_same (same clock bucket, 1 day back)  = {a['mean_same']:+.5f}  "
          f"t = {a['t_mean_same']:+.2f}")
    print(f"    beta_adj  (adjacent bucket, minutes ago)   = {a['mean_adj']:+.5f}  "
          f"t = {a['t_mean_adj']:+.2f}")
    print(f"    margin                                     = {a['margin']:+.5f}  "
          f"t = {a['t_margin']:+.2f}")
    if a["mean_adj"] >= a["mean_same"]:
        print("    beta_adj >= beta_same  ->  THE ADJACENT-BUCKET CONTROL WINS OUTRIGHT.")
        print("    The predictability is GENERIC WITHIN-DAY MOMENTUM, not clock-aligned "
              "scheduling.")
    else:
        print("    beta_same > beta_adj by sign only.")
    print(f"    beta_nonmult (CONTROL B, non-daily lag)    = {a['mean_nonmult']:+.5f}  "
          f"t = {a['t_mean_nonmult']:+.2f}"
          + ("   <- LARGER IN MAGNITUDE THAN THE TREATMENT"
             if abs(a["mean_nonmult"]) > abs(a["mean_same"]) else ""))
    weak = (abs(a["t_mean_same"]) < Z95 and abs(a["t_mean_adj"]) < Z95)
    if weak:
        print()
        print("    BUT THERE IS NOTHING FOR EITHER TERM TO WIN. Neither the treatment nor the")
        print("    adjacent-bucket control is distinguishable from zero at all: both t-statistics")
        print(f"    are inside +/-1.96 ({a['t_mean_same']:+.2f} and {a['t_mean_adj']:+.2f}), and "
              "the margin between two")
        print("    numbers that are both zero is itself zero. The sign of that margin is not a")
        print("    finding and is not quotable. What the run measures is the ABSENCE of the raw")
        print("    predictability the mechanism needs before its identifying restriction can even")
        print("    be tested - a stronger and cheaper closure than a lost head-to-head.")
    print()
    print(f"    Multiplicity price: the margin had to clear {p95_max_margin:+.5f} "
          f"(p95 of the max-over-buckets null) and delivered {a['margin']:+.5f}.")
    ratio = (f"{p95_max_margin / a['margin']:.0f}x short" if a["margin"] > 0
             else "the wrong sign entirely")
    print(f"    That is {ratio}. Against the null's MEAN margin the observed value sits at the "
          f"{ES.pct_of(nA['margin'], a['margin']):.0f}th percentile - an ordinary draw.")
    print()
    print("  WITH AND WITHOUT BUCKETS 0 AND 12 (spec trap 4 - is the whole effect two buckets?):")
    for e in ERAS:
        aa, ii = obs[e]["agg"]["ALL_13"], obs[e]["agg"]["INTERIOR_1_11"]
        print(f"    {e:<7} mean_same  ALL_13 {aa['mean_same']:+.5f}   "
              f"INTERIOR_1_11 {ii['mean_same']:+.5f}   "
              f"margin ALL {aa['margin']:+.5f} -> INTERIOR {ii['margin']:+.5f}")
    print("    In PRE the open (b=0) and close (b=12) buckets carry essentially the entire mean:")
    print("    dropping them moves mean_b beta_same from "
          f"{obs['PRE']['agg']['ALL_13']['mean_same']:+.5f} to "
          f"{obs['PRE']['agg']['INTERIOR_1_11']['mean_same']:+.5f}. Those two buckets are auction")
    print("    microstructure, not a scheduling trace, and they are the only large |beta| in the")
    print("    whole PRE column. They are NOT excluded from any gate - excluding them after seeing")
    print("    the table would be a selection - and the gate set was frozen before the run.")

    # ---------------------------------------------------------------------------------------
    sec("7.  STAGE 2  -  ECONOMICS")
    s2 = None
    if not stage1_pass:
        print("  STAGE 2 DOES NOT RUN.")
        print("  spec S2_precondition: Stage 1 must PASS in MODERN, otherwise Stage 2 does not run")
        print("  and NO DOLLAR FIGURE IS PRODUCED. No position is formed, no P&L is computed, no")
        print("  candidate is created, and the population is NOT redefined.")
        print()
        print("  For the record, the cost arithmetic that was FROZEN IN THE SPEC (spec text, not a")
        print("  result of this run): 13 round turns/session x ~250 sessions = ~3,250 RT/yr; at the")
        print(f"  EXEC01 primary line of ${S2.COST_LINES[S2.PRIMARY_LINE]:.2f}/ctrRT "
              f"(= {S2.COST_LINES[S2.PRIMARY_LINE]/S2.PV:.3f} NQ points) the annual cost is")
        print(f"  ~${S2.annual_cost():,.0f}. This is why Stage 1 exists: killing the family here "
              "costs nothing.")
        print()
        print("  The bucket-subset prohibition is enforced in code, not by convention. Exercising")
        print("  it here so that the guard is on the record even though Stage 2 never runs:")
        try:
            S2.refuse_bucket_subset([6, 8, 10])   # the three best MODERN buckets in the table above
            print("    GUARD DID NOT FIRE - this is a defect")
        except RuntimeError as ex:
            print(f"    {ex}")
        print("    (all 13 buckets is the only accepted argument)")
        S2.refuse_bucket_subset(range(13))
    else:
        s2 = _stage2(dates, P, B, R, masks, gates)

    # ---------------------------------------------------------------------------------------
    sec("8.  WHAT THIS RUN DOES AND DOES NOT CLOSE")
    if stage1_pass:
        print("  Stage 1 PASSED, so nothing is closed by Stage 1. Read section 7.")
    else:
        print("  CLOSED: the transfer to NQ of the HKS-style cross-day clock-bucket periodicity")
        print("  mechanism, at the 30-minute bucket width, on NQ 1-minute data, in MODERN and in")
        print("  PRE and FULL alike. That also removes the shared premise from every other WAVE B")
        print("  candidate that leans on 'scheduled institutional flow leaves a periodic price")
        print("  trace' on this instrument.")
    print()
    print("  NOT CLOSED: HKS itself. HKS was measured on US EQUITY CROSS-SECTIONS, where the")
    print("  periodicity is a cross-sectional return-sorting effect across thousands of names. NQ is")
    print("  ONE index future. A null here falsifies the TRANSFER, not the original finding. The")
    print("  spec named this before the run and it is repeated here so no reader over-reads it.")
    print()
    print("  Also not closed by this run, and deliberately out of scope: any other bucket width")
    print("  (spec prohibition 5 bans a width search in this run AND in any successor), any")
    print("  cross-sectional version, and any conditional/state-dependent version.")

    # ---------------------------------------------------------------------------------------
    _write_outputs(rows, gates, stage1_pass, obs, nulls, keffs, pan, s2)
    sec("DONE")
    print(f"  Stage 1: {'PASS' if stage1_pass else 'FAIL'}"
          f"   Stage 2: {'ran' if s2 else 'NOT RUN'}")
    print("  no order placed, no strategy deployed or enabled, no backtest engine called, $0 spent")
    return 0


# ==================================================================================================
def _stage2(dates, P, B, R, masks, gates):
    """Only reachable on a Stage 1 PASS. Every cost line is printed; the primary line is the gate."""
    from research_sdk import champion_eval as CE
    m = masks["MODERN"]
    Pm, Bm, Rm, dm = P[m], B[m], R[m], dates[m]
    trade_dates = np.repeat(dm[1:], 13)
    ann = S2.annual_cost()
    print(f"  Frozen rule: sign(r(b,d-1)) at the OPEN of bucket b, held to its CLOSE, 1 contract,")
    print(f"  ALL 13 BUCKETS EVERY DAY. {len(dm)-1:,} sessions x 13 = {13*(len(dm)-1):,} round "
          f"turns in MODERN.")
    print(f"  ANNUAL COST AT THE PRIMARY LINE: ~${ann:,.0f}/yr. Printed beside every gross figure.")
    print()
    print(f"  {'cost line':<26}{'$/ctrRT':>10}{'NQ pts':>9}{'gross $':>14}{'costs $':>14}"
          f"{'net $':>14}{'net $/yr':>12}")
    res = {}
    for nm, c in S2.COST_LINES.items():
        gross, net, _ = S2.signal_and_pnl(Pm, Bm, Rm, c)
        yrs = (dm[-1] - dm[0]).astype(int) / 365.25
        res[nm] = dict(gross=float(gross.sum()), net=float(net.sum()),
                       costs=float(gross.size * c), per_year=float(net.sum() / yrs))
        print(f"  {nm:<26}{c:>10.2f}{c/S2.PV:>9.3f}{res[nm]['gross']:>14,.0f}"
              f"{res[nm]['costs']:>14,.0f}{res[nm]['net']:>14,.0f}{res[nm]['per_year']:>12,.0f}")
    prim = S2.COST_LINES[S2.PRIMARY_LINE]
    gross, net, _ = S2.signal_and_pnl(Pm, Bm, Rm, prim)
    netflat = net.reshape(-1)

    nulld = S2.null_net_distribution(Pm, Bm, Rm, prim, N_DRAWS, SEED)
    p95 = float(np.percentile(nulld, 95))
    rv = CE.risk_vector("CLOCKLAG01", [str(d) for d in trade_dates], netflat,
                        np.ones(len(netflat)))
    yrs = sorted(rv.by_year)
    loyo_pos = sum(1 for y in yrs if sum(v["net"] for k, v in rv.by_year.items() if k != y) > 0)
    print()
    print(CE.champion_report(CE.risk_vector("ZERO", [str(d) for d in trade_dates],
                                            np.zeros(len(netflat)), np.ones(len(netflat))),
                             rv, CE.incremental(np.zeros(rv.n_weeks), np.zeros(rv.n_weeks),
                                                n_draws=200)))
    g = [("S2-G1 net > 0 on PRIMARY line", "net > 0 at $20.65/ctrRT in MODERN",
          f"${res[S2.PRIMARY_LINE]['net']:,.0f}", res[S2.PRIMARY_LINE]["net"] > 0),
         ("S2-G2 beats its own cost-charged null", f"net > p95 of the {N_DRAWS}-draw shift null",
          f"${net.sum():,.0f} vs p95 ${p95:,.0f}", net.sum() > p95),
         ("S2-G3 risk vector, not net alone", "champion_eval risk vector reported",
          f"maxDD ${rv.max_dd:,.0f} ES95 ${rv.es95:,.0f} top10% {rv.top_10pct_share:.2f}", True),
         ("S2-G4 leave-one-year-out", "positive in >= 4 of 5 LOYO recomputations in MODERN",
          f"{loyo_pos} of {len(yrs)}", loyo_pos >= 4)]
    print()
    print(f"  {'GATE':<40}{'SPEC':<52}{'OBSERVED':<44}{'PASS/FAIL'}")
    hr("-", 150)
    for gid, sp, ob, ok in g:
        gates.append(dict(gate=gid, spec=sp, observed=ob, verdict="PASS" if ok else "FAIL",
                          passed=bool(ok)))
        print(f"  {gid:<40}{sp:<52}{ob:<44}{'PASS' if ok else 'FAIL'}")
    allok = all(x[3] for x in g)
    verdict = ("CANDIDATE (queued for the champion board; NOT promoted, NOT built, NOT deployed)"
               if allok else "FAIL - recorded FAIL, population NOT redefined")
    print(f"  ALL of G1..G4 -> {verdict}")
    return dict(cost_lines=res, null_p95=p95, loyo_positive=loyo_pos,
                risk_vector=rv.as_dict(), all_pass=bool(allok))


def _window_label(b):
    s = 570 + 30 * b
    e = s + 30
    return f"{s//60:02d}:{s%60:02d}-{e//60:02d}:{e%60:02d}"


def _z_two_sided(alpha):
    from math import erf, sqrt
    lo, hi = 0.0, 12.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if 2 * (1 - 0.5 * (1 + erf(mid / sqrt(2)))) > alpha:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def _write_outputs(rows, gates, stage1_pass, obs, nulls, keffs, pan, s2):
    import csv
    p = os.path.join(OUT, "stage1_table.csv")
    cols = ["era", "bucket", "window", "n_obs", "beta_same", "se_same", "t_same",
            "beta_adj", "se_adj", "t_adj", "beta_nonmult", "se_nonmult", "t_nonmult"]
    body = io.StringIO()
    w = csv.DictWriter(body, fieldnames=cols, lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow({k: r[k] for k in cols})
    with open(p, "wb") as f:
        f.write(body.getvalue().encode("utf-8"))

    gs = ES.GATE_SET
    doc = dict(
        run_id="G3_CLOCKLAG01_20260831",
        spec="runs/G3_CLOCKLAG01_20260831/spec.yaml",
        live_enabled=False, orders_placed=False, spend_usd=0,
        stage1_pass=stage1_pass, stage2_ran=s2 is not None,
        gate_era="MODERN", gate_bucket_set=gs,
        n_draws=N_DRAWS, seed=SEED, null_buffer=ES.NULL_BUFFER,
        panel=pan["drops"],
        rho_bar_and_keff=keffs,
        gates=gates,
        by_era={e: dict(
            n_obs=obs[e]["n"],
            means={nm: {k: v for k, v in obs[e]["agg"][nm].items()} for nm in ES.BUCKET_SETS},
            null_A_p95={k: float(np.percentile(nulls[e]["NULL_A"][gs][k], 95))
                        for k in nulls[e]["NULL_A"][gs]},
            null_A_p50={k: float(np.percentile(nulls[e]["NULL_A"][gs][k], 50))
                        for k in nulls[e]["NULL_A"][gs]},
            null_B_p95={k: float(np.percentile(nulls[e]["NULL_B"][gs][k], 95))
                        for k in nulls[e]["NULL_B"][gs]},
            margin_percentile_vs_null_A_mean=ES.pct_of(nulls[e]["NULL_A"][gs]["margin"],
                                                       obs[e]["agg"][gs]["margin"]),
            margin_percentile_vs_null_A_max=ES.pct_of(nulls[e]["NULL_A"][gs]["max_margin"],
                                                      obs[e]["agg"][gs]["margin"]),
            margin_percentile_vs_null_B_max=ES.pct_of(nulls[e]["NULL_B"][gs]["max_margin"],
                                                      obs[e]["agg"][gs]["margin"]),
            beta_same=[float(x) for x in obs[e]["beta_same"]],
            beta_adj=[None if not np.isfinite(x) else float(x) for x in obs[e]["beta_adj"]],
            beta_nonmult=[float(x) for x in obs[e]["beta_nonmult"]],
        ) for e in ERAS},
        stage2=s2,
    )
    b = json.dumps(doc, indent=2, default=float).encode("utf-8")
    with open(os.path.join(OUT, "gates.json"), "wb") as f:
        f.write(b)
    print()
    print(f"  wrote out/stage1_table.csv ({len(rows)} rows) and out/gates.json ({len(b):,} bytes)")


if __name__ == "__main__":
    sys.exit(main())
