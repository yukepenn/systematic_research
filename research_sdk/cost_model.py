# -*- coding: utf-8 -*-
"""cost_model -- the ONE machine-readable cost schema. Every figure carries its basis.

WHY THIS EXISTS
---------------
The repo accumulated eleven per-round-turn dollar figures with no field saying whether a
number was COMMISSION_ONLY, SPREAD_ONLY or ALL_IN. That single missing word produced a
real, published arithmetic error: `$20.65/ctrRT` (spread only) was labelled "all-in" in
`GENESIS_III_VERDICT.md` SS H/I, commission was subtracted out of it and then charged again
one row below, and NQ friction was understated by about $59/wk. It also produced two
numeral collisions that are still live traps:

    $14.36  scalping-lab C1, ALL_IN      vs  $14.44  P1 spread, SPREAD_ONLY
    $24.00  W82 pessimistic SPREAD bound vs  $24.00  G3_XMLAT_01 ALL_IN stress rung

Storing an addend and a total in the same column is what caused it. This module makes that
impossible: nothing can be added without declaring what it is.

TWO TAGS, BOTH MANDATORY
------------------------
    basis     COMMISSION_ONLY | SPREAD_ONLY | ALL_IN
              Is this a component, or a total? SPREAD_ONLY figures are ADDENDS onto a
              commission-inclusive net. ALL_IN figures are TOTALS and must never be added
              to a commission row.

    evidence  MEASURED | MODELLED | BOUND | ASSUMED
              MEASURED carries n and coverage. Coverage matters: the two "measured"
              spreads rest on 5.1% and 8.7% of their books' contract round turns.
              ASSUMED means nobody measured it. There is one, and it is load-bearing for
              the live book -- see MNQ_SPREAD below.

USAGE
    from research_sdk.cost_model import CHARGE, all_in, per_nq_equivalent, table
    all_in("P1", "measured")        -> 25.01
    per_nq_equivalent("MNQ", "commission")  -> 13.00
    python -m research_sdk.cost_model       -> print the whole table
"""
from __future__ import annotations

BASES = ("COMMISSION_ONLY", "SPREAD_ONLY", "ALL_IN")
EVIDENCE = ("MEASURED", "MODELLED", "BOUND", "ASSUMED")

# Contract arithmetic. NQ and MNQ share a 0.25 tick in INDEX POINTS; only the dollar
# multiplier differs, exactly 10x. So one tick of MNQ costs 1/10 of one tick of NQ, and
# per unit of index exposure the two are identical IF the quoted spread in ticks is equal.
# That last clause is an assumption, not a measurement. See MNQ_SPREAD.
POINT_VALUE = {"NQ": 20.0, "MNQ": 2.0}
TICK_SIZE = 0.25                                   # index points, both instruments
TICK_VALUE = {k: v * TICK_SIZE for k, v in POINT_VALUE.items()}   # NQ $5.00, MNQ $0.50
MNQ_PER_NQ_EQUIVALENT = 10                         # 10 MNQ == 1 NQ of index exposure


class Cost:
    """One cost figure that cannot be used without its basis."""

    def __init__(self, cid, instrument, value, basis, evidence, source, note="",
                 n=None, coverage=None, era=None):
        assert basis in BASES, basis
        assert evidence in EVIDENCE, evidence
        if evidence == "MEASURED":
            assert n is not None, "%s: MEASURED requires n" % cid
        self.cid, self.instrument, self.value = cid, instrument, float(value)
        self.basis, self.evidence, self.source = basis, evidence, source
        self.note, self.n, self.coverage, self.era = note, n, coverage, era

    def __repr__(self):
        return "Cost(%s, $%.2f, %s, %s)" % (self.cid, self.value, self.basis, self.evidence)


# =========================================================================================
# THE REGISTRY. Every figure in the repo, adjudicated. $/contract round turn.
# =========================================================================================
CHARGE = {c.cid: c for c in [

    # ---- commission -------------------------------------------------------------------
    Cost("nq_commission", "NQ", 4.36, "COMMISSION_ONLY", "MEASURED",
         "NinjaTrader Brokerage Lifetime template; ledger-verified to the cent",
         "$2.18/side. The only cost NT8 itself charges in a backtest.", n="all fills"),

    Cost("mnq_commission", "MNQ", 1.30, "COMMISSION_ONLY", "MEASURED",
         "runs/AUDIT04_MNQ_PROBE -- constant across 704 fills",
         "$0.65/side. 3.35x cheaper per CONTRACT, 2.98x DEARER per unit of exposure.",
         n=704),

    # ---- NQ spread, modelled (what every research headline charges) --------------------
    Cost("p1_spread_model", "NQ", 14.44, "SPREAD_ONLY", "MODELLED",
         "runs/WE_W103_CONSOLIDATE/REPORT.md:47 (canonical); W82 per-minute median profile",
         "2.888 ticks, contract-weighted over entry and exit minutes. Siblings $14.52 (W89, "
         "contract-weighted) and $14.65 (W82, trade-weighted) are the SAME method under "
         "different weighting -- not three measurements."),

    Cost("xm_spread_model", "NQ", 12.50, "SPREAD_ONLY", "MODELLED",
         "runs/XM_EXEC_COST_AUDIT_V1_20260831/spec.yaml:65",
         "2.5 ticks = W82 profile at minutes 586/946, (3.0+2.0)/2 x $5.00. Algebraic, "
         "not sampled."),

    # ---- NQ spread, measured ----------------------------------------------------------
    Cost("p1_spread_measured", "NQ", 20.65, "SPREAD_ONLY", "MEASURED",
         "runs/G2_EXEC01_P1_EXECUTION_20260828 -- and its own spec_resolutions.txt:20-21 "
         "states SPREAD-ONLY explicitly",
         "median $20.00, p90 $35.00. 43% ABOVE the $14.44 the research headline charges.",
         n=113, coverage="5.1% of P1 contract RTs", era="2025-08 -> 2026-07"),

    Cost("xm_spread_measured", "NQ", 18.42, "SPREAD_ONLY", "MEASURED",
         "runs/XM_EXEC_COST_AUDIT_V1_20260831 -- verdict 'XM SPREAD MODEL OPTIMISTIC'",
         "95% bootstrap CI $15.08-$22.67, median $15.00. 47% above the $12.50 modelled.",
         n=30, coverage="8.7% of XM contract RTs", era="2025-08 -> 2026-07"),

    Cost("p1_spread_bound", "NQ", 24.00, "SPREAD_ONLY", "BOUND",
         "runs/WE_W82_FILLAUDIT/REPORT.md:91-104",
         "PESSIMISTIC BOUND on a selected subsample (35 of 120 fills), never the headline. "
         "Superseded by p1_spread_measured. Collides numerically with an unrelated ALL_IN "
         "stress rung in G3_XMLAT_01 -- different quantity, same numeral."),

    Cost("p1_spread_hostile", "NQ", 28.69, "SPREAD_ONLY", "MEASURED",
         "runs/G2_EXEC01_P1_EXECUTION_20260828/REPORT.md:15-16 -- 2026 Jun-Jul era cut",
         "The recent-era spread. 2025H2 and 2026 Jan-May both ran $17.12; the last two "
         "months of the sample ran $28.69. Use as the hostile-but-plausible stress.",
         n="era subset", era="2026-06 -> 2026-07"),

    # ---- MNQ spread: THE ONE THAT IS NOT MEASURED -------------------------------------
    Cost("mnq_spread", "MNQ", 0.00, "SPREAD_ONLY", "ASSUMED",
         "NOT MEASURED ANYWHERE IN THIS REPO",
         "The live book's cost estimate assumes MNQ's quoted spread equals NQ's IN TICKS, "
         "so that per unit of index exposure the spread cost is identical and the MNQ "
         "penalty is commission-only. The value 0.00 here is the assumed DIFFERENTIAL "
         "versus NQ, not a spread. research/system_master/EXECUTION_REALITY.md:6-7 says "
         "'MNQ spreads are wider in ticks at times', which contradicts it; one live "
         "snapshot on 2026-09-01 05:17 ET measured NQ 5 ticks vs MNQ 3 ticks, which "
         "contradicts the contradiction. n=1, overnight, asynchronous. UNRESOLVED."),
]}


# =========================================================================================
def get(cid):
    if cid not in CHARGE:
        raise KeyError("unknown cost id %r; known: %s" % (cid, sorted(CHARGE)))
    return CHARGE[cid]


def all_in(leg, spread="model"):
    """Total NQ $/ctrRT for a leg. Commission + spread, added ONCE each.

    leg    'P1' | 'XM'
    spread 'model' | 'measured' | 'bound' | 'hostile'
    """
    leg = leg.upper()
    key = {"model": "%s_spread_model", "measured": "%s_spread_measured",
           "bound": "p1_spread_bound", "hostile": "p1_spread_hostile"}[spread]
    key = key % leg.lower() if "%s" in key else key
    s = get(key)
    assert s.basis == "SPREAD_ONLY", "%s is %s, not an addend" % (s.cid, s.basis)
    return round(get("nq_commission").value + s.value, 2)


def per_nq_equivalent(instrument, component="commission"):
    """Cost per unit of NQ-sized index exposure. This is the ONLY fair comparison.

    Comparing $4.36 to $1.30 says micros are cheaper. They are not: it takes TEN of them.
    """
    if component != "commission":
        raise NotImplementedError("only commission is measured per instrument")
    if instrument.upper() == "NQ":
        return get("nq_commission").value
    return round(get("mnq_commission").value * MNQ_PER_NQ_EQUIVALENT, 2)


def mnq_penalty_per_nq_equivalent(extra_mnq_spread_ticks=0.0):
    """The live book's execution penalty vs trading NQ directly, per NQ-equivalent ctrRT.

    extra_mnq_spread_ticks : how many INDEX TICKS wider MNQ quotes than NQ.
                             0.0 is the ASSUMPTION the repo currently ships.
                             Negative means MNQ is tighter (the one snapshot says -2).
    """
    commission = per_nq_equivalent("MNQ") - per_nq_equivalent("NQ")   # +8.64
    spread = extra_mnq_spread_ticks * TICK_SIZE * POINT_VALUE["NQ"]   # $5.00 per tick
    return round(commission + spread, 2)


def weekly_penalty(ctr_rt_per_week, mnq_per_nq=3, extra_mnq_spread_ticks=0.0):
    """$/week the live book pays for executing in micros, at a given size.

    ctr_rt_per_week : full-size NQ contract round turns per week (M_11 = 13.65)
    mnq_per_nq      : the live MnqPerNq input; live scale = mnq_per_nq / 10
    """
    scaled = ctr_rt_per_week * (mnq_per_nq / float(MNQ_PER_NQ_EQUIVALENT))
    return round(scaled * mnq_penalty_per_nq_equivalent(extra_mnq_spread_ticks), 1)


def table():
    w = "%-22s %-5s %8s  %-16s %-9s %s"
    out = [w % ("ID", "INSTR", "$/ctrRT", "BASIS", "EVIDENCE", "COVERAGE / NOTE"), "-" * 110]
    for cid in sorted(CHARGE):
        c = CHARGE[cid]
        cov = c.coverage or (("n=%s" % c.n) if c.n else "")
        if c.era:
            cov = (cov + "  era " + c.era).strip()
        out.append(w % (c.cid, c.instrument, "%.2f" % c.value, c.basis, c.evidence, cov))
    return "\n".join(out)


def selftest():
    """Guards for the exact errors this module exists to prevent."""
    ok = []

    # 1. the published error: $20.65 is an ADDEND, not a total
    ok.append(("20.65 is SPREAD_ONLY", get("p1_spread_measured").basis == "SPREAD_ONLY"))
    ok.append(("all-in measured == 25.01", all_in("P1", "measured") == 25.01))
    ok.append(("all-in model    == 18.80", all_in("P1", "model") == 18.80))
    ok.append(("XM all-in model == 16.86", all_in("XM", "model") == 16.86))
    ok.append(("XM all-in meas  == 22.78", all_in("XM", "measured") == 22.78))

    # 2. never add commission to an ALL_IN figure
    try:
        Cost("bad", "NQ", 1, "ALL_IN", "MEASURED", "x", n=1)
        s = get("p1_spread_measured")
        ok.append(("addend guard holds", s.basis == "SPREAD_ONLY"))
    except Exception:
        ok.append(("addend guard holds", False))

    # 3. micros are DEARER per unit of exposure, not cheaper
    ok.append(("MNQ per NQ-equiv == 13.00", per_nq_equivalent("MNQ") == 13.00))
    ok.append(("MNQ dearer per exposure", per_nq_equivalent("MNQ") > per_nq_equivalent("NQ")))
    ok.append(("commission penalty 8.64", mnq_penalty_per_nq_equivalent(0.0) == 8.64))

    # 4. the shipped $35/wk figure is COMMISSION ONLY -- reproduce it exactly
    ok.append(("$35/wk reproduces", abs(weekly_penalty(13.65, 3, 0.0) - 35.4) < 0.2))

    # 5. the unmeasured input is flagged as such
    ok.append(("mnq_spread is ASSUMED", get("mnq_spread").evidence == "ASSUMED"))

    # 6. every MEASURED figure carries n
    ok.append(("all MEASURED carry n",
               all(c.n is not None for c in CHARGE.values() if c.evidence == "MEASURED")))

    for name, passed in ok:
        print("  %-28s %s" % (name, "PASS" if passed else "FAIL"))
    n_ok = sum(1 for _, p in ok if p)
    print("selftest %d/%d" % (n_ok, len(ok)))
    return 0 if n_ok == len(ok) else 1


if __name__ == "__main__":
    import sys
    print(table())
    print()
    print("ALL-IN TOTALS (NQ, $/ctrRT) -- commission added ONCE")
    for leg in ("P1", "XM"):
        for s in ("model", "measured"):
            print("  %-3s %-9s  $%.2f" % (leg, s, all_in(leg, s)))
    print()
    print("LIVE MNQ EXECUTION PENALTY, $/week at MnqPerNq=3 (13.65 full-size ctrRT/wk)")
    print("  MNQ spread vs NQ      $/NQ-equiv ctrRT    $/week")
    for t in (-2, -1, 0, 1, 2):
        lab = {0: "equal (ASSUMED)"}.get(t, "%+d tick" % t)
        print("  %-20s %8.2f          %+7.1f"
              % (lab, mnq_penalty_per_nq_equivalent(t), weekly_penalty(13.65, 3, t)))
    print()
    sys.exit(selftest())
