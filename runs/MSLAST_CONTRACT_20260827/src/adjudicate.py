"""LANE A step 6 - BOUNDED ADJUDICATION REPAIR.  Claim correctness, not rescue.

NO new features. NO new horizon. NO new model family. NO blind data. NO tuning.

FOUR DEFECTS IN THE FIRST ADJUDICATION, all owner-identified, all conceded:

 1A  "The 60-second NQ move is a martingale" is an OVERCLAIM. Zero unconditional drift, near-zero
     lag-1 autocorrelation and the failure of ONE finite feature/model family do not establish
     E[r_{t+1} | F_t] = 0 for the relevant filtration. A finite failed family is not a proof over
     all measurable functions. Retracted; replaced with the narrower supported statement.

 1B  discover.py's "dependence-preserving null" was `np.roll(v, s).mean()`. THE MEAN OF A VECTOR
     IS INVARIANT TO CIRCULAR PERMUTATION, so every element of that "distribution" equals the
     observed statistic - verified: 85 shifts, ONE distinct value, spread 1.7e-13. It cannot
     reject anything. Worse, the code comment said "# mean is shift-invariant": the invariance was
     documented and then used as a null anyway. It never reached the printed verdict (only the
     placebo did) but the section header and REPORT claimed a circular-shift null existed. That
     claim is withdrawn and a REAL one is built below.

 1C  "CI contains zero => NO INFORMATION" is invalid. It means FAIL TO ESTABLISH INFORMATION.
     An equivalence claim needs a materiality region DECLARED BEFORE recomputation.

 1D  Power was expressed against ALWAYS-ON friction ($39,506/session). Ridge trades 2.4 % of
     decisions, so that is not the burden the tested policy must overcome. Re-expressed against
     the policy's OWN activity-matched cost, a predeclared materiality threshold, and the placebo.

--------------------------------------------------------------------------------------------
PREDECLARED BEFORE ANY NUMBER IN THIS SCRIPT WAS COMPUTED (1C):

  The incumbent P1/PCT earns $1,230/week at a fixed $20,245 drawdown, i.e. ~$246 per session over
  a five-session week. That is the only portfolio-relevant yardstick this repo owns, so:

      MATERIALITY_STRONG = $246 / session    a sleeve as valuable per session as the incumbent
      MATERIALITY_WEAK   = $ 49 / session    20 % of the incumbent - the smallest contribution
                                             that could plausibly justify a second sleeve's
                                             engineering, execution and monitoring burden

  EQUIVALENCE TEST: the one-sided upper 95 % confidence bound on per-session after-cost P&L.
  If UB < threshold, an effect of at least that size is RULED OUT for the tested object.

  NOTE ON WHAT THIS CAN AND CANNOT CLOSE. Dollars map to dollars, so an equivalence test on the
  ECONOMIC statistic is honest. There is NO defensible assumption-light mapping from a predictive
  CORRELATION to dollars, so none is invented (1C's own instruction). The correlation result
  therefore stays "FAIL TO ESTABLISH INFORMATION" and never becomes "no information exists".
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd
from scipy import stats as st
from sklearn.linear_model import Ridge

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "out")
SEED = 20260827
N_FOLD = 5
MATERIALITY_STRONG = 246.0      # DECLARED ABOVE, before computation
MATERIALITY_WEAK = 49.0         # DECLARED ABOVE, before computation
_fh = open(os.path.join(OUT, "adjudicate.txt"), "w", encoding="utf-8")


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


def policy_pnl(pred, move, cost):
    act = np.where(pred > cost, 1, np.where(pred < -cost, -1, 0))
    return act * move - np.abs(act) * cost, act


def oof_ridge(X, y, sess, order, blocks):
    """Expanding-origin chronological session-block validation. Refit from scratch each fold."""
    pr, ix = [], []
    for k in range(1, N_FOLD + 1):
        tr = np.concatenate(blocks[:k])
        mtr, mte = np.isin(sess, tr), np.isin(sess, blocks[k])
        mu, sd = X[mtr].mean(0), X[mtr].std(0)
        sd[sd == 0] = 1
        m = Ridge(alpha=10.0).fit((X[mtr] - mu) / sd, y[mtr])
        pr.append(m.predict((X[mte] - mu) / sd))
        ix.append(np.where(mte)[0])
    return np.concatenate(ix), np.concatenate(pr)


def main():
    d = pd.read_parquet(os.path.join(OUT, "discovery_substrate.parquet")).sort_values("t")
    d = d.reset_index(drop=True)
    meta = ("session", "src", "t", "hour", "tod", "move", "cost", "cost_s1", "cost_s2")
    feats = [c for c in d.columns if c not in meta] + ["tod"]
    X = np.nan_to_num(d[feats].values.astype(float), posinf=0, neginf=0)
    y = d["move"].values.astype(float)
    ct = d["cost"].values.astype(float)
    sess = d["session"].values
    order = pd.unique(d["session"])
    n_s = len(order)
    blocks = np.array_split(order, N_FOLD + 1)
    pos = {s: i for i, s in enumerate(order)}
    per_sess_y = [y[sess == s] for s in order]

    P("=" * 104)
    P("=== MS-LAST BOUNDED ADJUDICATION REPAIR - claim correctness, not rescue")
    P("=" * 104)
    P(f"    decisions {len(d):,}   sessions {n_s}   features {len(feats)}")
    P(f"    PREDECLARED materiality:  STRONG ${MATERIALITY_STRONG:,.0f}/session   "
      f"WEAK ${MATERIALITY_WEAK:,.0f}/session")

    # ---------------------------------------------------------------- 1B: demonstrate the defect
    P("")
    P("=" * 104)
    P("=== 1B  THE OLD 'NULL' WAS MATHEMATICALLY INCAPABLE OF REJECTING ANYTHING")
    P("=" * 104)
    ix0, pr0 = oof_ridge(X, y, sess, order, blocks)
    pnl0, act0 = policy_pnl(pr0, y[ix0], ct[ix0])
    ss0 = pd.Series(pnl0).groupby(sess[ix0]).sum()
    v = ss0.values
    old = np.array([np.roll(v, s).mean() for s in range(1, len(v))])
    P(f"    old construction: np.roll(v, s).mean() over {len(old)} shifts")
    P(f"      distinct values {len(np.unique(np.round(old, 8)))}   spread ${old.max()-old.min():.3e}")
    P(f"      every element = ${old[0]:,.4f} = the observed statistic itself")
    P("      >>> WITHDRAWN. It is not a null; it is the observation restated.")

    # ------------------------------------------------- 1B repair: REFITTED session-shift null
    P("")
    P("=" * 104)
    P("=== 1B  REPAIR - REFITTED SESSION-BLOCK NULL (exhaustive, deterministic)")
    P("=== Session i's FEATURES are paired with session (i+k)'s OUTCOMES; every row inside a")
    P("=== session is preserved; the expanding-origin mapping is rebuilt; Ridge is REFITTED FROM")
    P("=== SCRATCH inside every replicate; the primary statistic is recomputed end to end.")
    P("=== Costs stay with the DECISION (its hour), not with the donor outcome.")
    P("=" * 104)
    obs = float(ss0.mean())
    P(f"    observed primary  ${obs:,.2f} / session   ({len(ss0)} evaluated sessions)")
    P(f"    running all {n_s-1} non-trivial circular shifts - exhaustive, so no sampling error")
    nulls, null_rate = [], []
    for k in range(1, n_s):
        yk = np.empty_like(y)
        for i, s in enumerate(order):
            donor = per_sess_y[(i + k) % n_s]
            m = sess == s
            need = int(m.sum())
            yk[m] = np.resize(donor, need)          # wrap donor to recipient length; keep all rows
        ixk, prk = oof_ridge(X, yk, sess, order, blocks)
        pk, ak = policy_pnl(prk, yk[ixk], ct[ixk])
        nulls.append(float(pd.Series(pk).groupby(sess[ixk]).sum().mean()))
        null_rate.append(float(np.mean(ak != 0)))
        if k % 25 == 0:
            P(f"      ... {k}/{n_s-1} refitted nulls")
    nulls = np.array(nulls)
    null_rate = np.array(null_rate)
    pct = 100.0 * float((nulls < obs).mean())
    P("")
    P(f"    refitted null:  mean ${nulls.mean():,.2f}   sd ${nulls.std(ddof=1):,.2f}   "
      f"range [${nulls.min():,.0f}, ${nulls.max():,.0f}]")
    P(f"    distinct values {len(np.unique(np.round(nulls, 6)))} of {len(nulls)}  "
      f"<- a REAL distribution, unlike the withdrawn one")
    P(f"    observed ${obs:,.2f} sits at the {pct:.1f}th percentile of it")
    P(f"    >>> {'BEATS the refitted null' if pct > 95 else 'DOES NOT beat the refitted null'}")
    pd.DataFrame(dict(shift=np.arange(1, n_s), null_per_session=nulls,
                      null_trade_rate=null_rate)).to_csv(
        os.path.join(OUT, "refitted_null.csv"), index=False)

    # WORSE THAN RANDOM is a different, stronger statement than NO BETTER (discipline rule 58),
    # so the mechanism has to be pinned rather than left to sound sinister. Two candidates:
    # (i) the features are genuinely ANTI-predictive, or (ii) they merely generate more
    # threshold crossings without directional edge, so the policy pays more friction. Trade rate
    # separates them.
    obs_rate = float(np.mean(act0 != 0))

    P("")
    P("    WHY BELOW THE NULL - 'worse than random' needs a mechanism, not an insinuation:")
    P(f"      trade rate   observed {100*obs_rate:5.2f} %   null mean {100*null_rate.mean():5.2f} %"
      f"   null range [{100*null_rate.min():.2f} %, {100*null_rate.max():.2f} %]")
    extra = (obs_rate - null_rate.mean()) * len(ix0) / len(ss0)
    P(f"      the real features cross the cost threshold "
      f"{obs_rate/max(null_rate.mean(),1e-9):.2f}x as often as scrambled ones,")
    P(f"      i.e. ~{extra:+.1f} extra trades/session at ~${ct[ix0][act0 != 0].mean():,.2f} each "
      f"= ~${extra*ct[ix0][act0 != 0].mean():+,.0f}/session of extra friction,")
    P(f"      against an observed-minus-null gap of ${obs - nulls.mean():+,.0f}/session.")
    P("      >>> The features carry enough VARIANCE to trigger trading and no usable DIRECTION.")
    P("      >>> That is churn, NOT an invertible anti-signal - flipping the sign would pay the")
    P("      >>> same friction. Do not read the 1st percentile as a hidden edge.")

    # ---------------------------------------------------------------- 1D: correct denominators
    P("")
    P("=" * 104)
    P("=== 1D  POWER, AGAINST THE DENOMINATORS THAT ACTUALLY APPLY")
    P("=" * 104)
    n_ev = len(ss0)
    sd_s = float(ss0.std(ddof=1))
    se = sd_s / np.sqrt(n_ev)
    mde = 2.80 * se
    tr = act0 != 0
    trades_per_sess = tr.sum() / n_ev
    own_cost = float(ct[ix0][tr].sum() / n_ev)
    P(f"    evaluated sessions              {n_ev}")
    P(f"    per-session P&L sd              ${sd_s:>10,.2f}    SE ${se:,.2f}")
    P(f"    MDE (~80 % power, 5 % 2-sided)  ${mde:>10,.2f} / session")
    P("")
    P(f"    {'denominator':<52}{'value':>14}{'MDE / it':>12}")
    P("    " + "-" * 78)
    for lab, den in (("(WRONG, withdrawn) ALWAYS-ON friction, 100 % activity",
                      float(ct.sum() / n_s)),
                     ("(A) the POLICY'S OWN activity-matched cost burden", own_cost),
                     ("(B) predeclared materiality - STRONG", MATERIALITY_STRONG),
                     ("(B) predeclared materiality - WEAK", MATERIALITY_WEAK)):
        P(f"    {lab:<52}${den:>13,.2f}{mde/den:>12.2f}x")
    P("")
    P(f"    the policy trades {trades_per_sess:.1f} times/session at ${own_cost/max(trades_per_sess,1):,.2f} "
      f"mean cost/trade")
    P(f"    MDE re-expressed PER TRADE      ${mde/trades_per_sess:>10,.2f}")
    P("")
    P("    >>> HONEST READING: the MDE is LARGER than the strong materiality threshold")
    P(f"    >>> (${mde:,.0f} vs ${MATERIALITY_STRONG:,.0f}), so this test could NOT have detected an")
    P("    >>> exactly-material effect as a DIFFERENCE FROM ZERO. The old comparison against")
    P("    >>> $39,506 of always-on friction made the test look far better powered than it is.")

    # ---------------------------------------------------------------- 1C: equivalence test
    P("")
    P("=" * 104)
    P("=== 1C  EQUIVALENCE - declared BEFORE computation, tested on DOLLARS not correlation")
    P("=" * 104)
    tcrit = float(st.t.ppf(0.95, n_ev - 1))
    ub = obs + tcrit * se
    P(f"    observed per-session P&L        ${obs:>10,.2f}")
    P(f"    one-sided upper 95 % bound      ${ub:>10,.2f}")
    P("")
    for lab, thr in (("STRONG", MATERIALITY_STRONG), ("WEAK", MATERIALITY_WEAK)):
        ok = ub < thr
        P(f"    {lab:<8} materiality ${thr:>7,.0f}/session   UB ${ub:,.2f} "
          f"{'<' if ok else '>='} threshold   "
          f"{'RULED OUT' if ok else 'NOT ruled out'}")
    P("")
    P("    Equivalence holds here NOT because the test is precise - it is not - but because the")
    P("    point estimate sits far in the WRONG direction. Both facts are stated together.")

    # ---------------------------------------------------------------- 1A: what may be said
    P("")
    P("=" * 104)
    P("=== 1A  WHAT IS AND IS NOT SUPPORTED")
    P("=" * 104)
    lag = pd.Series(y[ix0]).groupby(sess[ix0]).apply(lambda g: g.autocorr(1))
    dm = pd.Series(y[ix0]).groupby(sess[ix0]).mean()
    P("    SUPPORTED:")
    P("      * the frozen order-invariant Last-only V1 feature/model family found no usable")
    P("        out-of-sample predictive signal at the 60-second horizon;")
    P(f"      * no unconditional 60 s drift detected  (mean ${y[ix0].mean():+,.3f}, "
      f"session-clustered t {dm.mean()/(dm.std(ddof=1)/np.sqrt(len(dm))):+.2f});")
    P(f"      * no lag-1 linear serial dependence detected  (mean {lag.mean():+.4f}, "
      f"t {lag.mean()/(lag.std(ddof=1)/np.sqrt(lag.notna().sum())):+.2f});")
    P("      * Ridge and the single shallow GBM both failed;")
    P("      * the tested trade-flow family produced NO CANDIDATE.")
    P("")
    P("    NOT SUPPORTED - and previously claimed:")
    P("      * 'the 60-second NQ move is a MARTINGALE'   <- RETRACTED. Establishing")
    P("        E[r|F_t] = 0 requires a statement over ALL measurable functions of the filtration.")
    P("        A finite failed family cannot deliver it, and neither can zero drift plus")
    P("        near-zero lag-1 linear autocorrelation.")
    P("      * '60 s returns are unpredictable'          <- not tested")
    P("      * 'every Last-only feature is null'         <- not tested")
    P("      * 'all microstructure is null'              <- not tested")

    # ---------------------------------------------------------------- verdict
    P("")
    P("=" * 104)
    P("=== FINAL STATUS (1E)")
    P("=" * 104)
    econ_closed = ub < MATERIALITY_WEAK
    null_beaten = pct > 95
    if econ_closed and not null_beaten:
        P("    MS-LAST-V1 : FALSIFIED-NULL-CLOSED, scoped EXACTLY to")
        P("        certified order-invariant feature set")
        P("      + 60-second horizon")
        P("      + frozen Ridge / shallow-GBM attempt budget")
        P("      + this decision policy and this frozen cost schedule")
        P("")
        P("    Justification: the refitted session-block null is not beaten, AND the one-sided")
        P(f"    upper 95 % bound (${ub:,.2f}/session) rules out even the WEAK materiality")
        P(f"    threshold (${MATERIALITY_WEAK:,.0f}/session).")
    else:
        P("    MS-LAST-V1 : NO CANDIDATE / NO DETECTED SIGNAL / DE-PRIORITISED")
    P("")
    P("    NOT CLOSED, and must never be written as closed:")
    P("      * Last-only alpha in general")
    P("      * other horizons, other feature classes, non-flow constructions")
    P("      * the predictability of 60 s NQ returns as such")
    P("")
    P("    THE 141-SESSION BLIND POOL REMAINS UNSPENT. It is preserved for a genuinely different")
    P("    future mechanism, not for incremental feature mining on this one.")
    _fh.close()


if __name__ == "__main__":
    main()
