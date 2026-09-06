#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ROLL02_EXECSERIES_GATING_20260906  --  trial G00047  --  preregistered diagnostic.

Prices the ROLL01 'per-series gating' claim: what would the book have earned in the strip of
days recovered if blockNewEntriesFrom derived from the EXECUTION series' rollover only
(MNQ/YM-like latest-equity-index date) instead of the MIN over every loaded series.

SAME OBJECT AS G3_ROLLCOST_00_20260831, PROVEN:
  G3's src/ is absent from its run directory, so its construction was recovered by exact
  fingerprint against every figure it published and is REPRODUCED HERE TO THE DOLLAR before
  anything new is computed (step 1 aborts the run on any mismatch).  Fingerprint result
  (unique over the searched grid of date-basis x window-end x per-leg roll-offset):
    - one roll date per quarter: R = third Friday of Mar/Jun/Sep/Dec (all series collapsed);
    - trade classified by the CALENDAR DATE of its ENTRY timestamp;
    - observed window = [R-8, R+1] inclusive (R+1 is a Saturday, so identical to [R-8, R]);
    - 'same-day re-enable' variant = [R-8, R-1]; 'lead 4' variant = [R-4, R+1].
  CONSEQUENCE (spec deviation, stated up front): G3's single third-Friday date IS the
  MNQ/YM-like latest-equity-index rollover date, so G3's published window is ALREADY the
  exec-series-gated window.  The live all-series guard blocks EARLIER (stored rollovers:
  NQ = R-2  [machine-verified 2026-09: NQ 09-16 vs MNQ 09-18, blockFrom 09-08 = 09-16 - 8],
  ES = R-4  [earliest; the XM leg's context series]).  Therefore the recovered strip lies
  in [R-off-8, R-8) with off = 2 (P1) / 4 (XM), OUTSIDE G3's window, and the reconciliation
  identity takes the form
      all_series_blackout_net  =  strip_net  +  remaining_blackout_net
  with remaining_blackout == G3's published cut, reproduced to the dollar (G5).

Ledger: the exact G00041 owner-authorized read G3 consumed
  runs/G2_AUG_INCUMBENT_READ_20260830/out/{p1,xm}_trades_full.csv
  (P1 2439 trades / XM 378 = 2817, span 2022-01-02..2026-08-25, total net $537,352.88).
Cost basis: COMMISSION_ONLY ($4.36/ctrRT Lifetime), inherited from that ledger -- the same
basis as every G3 figure.  Evidence class: DISCOVERY_CONSUMED, in-sample.

Deterministic: stationary bootstrap seeded SEED=20260906; no other randomness.
Reads nothing dated >= 2026-08-26; the VIRGIN seal (>= 2026-08-01 market data) is not touched
(the ledger's 2026-08 rows are DIRECTLY_BURNED under G00041, already consumed by G3).
"""

import csv
import datetime as dt
import os
import random

# ----------------------------------------------------------------------------- constants
SEED = 20260906
N_BOOT = 10000
MEAN_BLOCK = 5          # stationary bootstrap expected block length (trades)
LEAD = 8                # RollLeadDays, same as the guard and as G3

REPO = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(REPO, "runs", "ROLL02_EXECSERIES_GATING_20260906")
OUT = os.path.join(RUN, "out")
LEDGER_DIR = os.path.join(REPO, "runs", "G2_AUG_INCUMBENT_READ_20260830", "out")

# stored-rollover offset of the EARLIEST loaded series vs the latest-equity-index date R:
#   P1 leg: NQ rolls 2 calendar days before MNQ (machine-verified 2026-09: 09-16 vs 09-18)
#   XM leg: ES rolls earliest, 4 calendar days before the MNQ/YM-like date
MIN_SERIES_OFFSET = {"P1": 2, "XM": 4}

# G3_ROLLCOST_00_20260831/out/console.txt published figures (reproduction targets, $-rounded)
G3_PUB = {
    "observed_n": 291, "observed_net": 106106, "total_n": 2817, "total_net": 537353,
    "sameday_n": 269, "sameday_net": 81566,
    "lead4_n": 192, "lead4_net": 81595,
    "leg": {"P1": (250, 2439, 47685, 354576), "XM": (41, 378, 58421, 182777)},
    "by_year": {2022: -13521, 2023: 13796, 2024: 48197, 2025: 29774, 2026: 27860},
}

# CME full-closure holidays that fall inside any strip below (checked exhaustively for
# 2022-2026 Mar/Jun/Sep/Dec strips; only Labor Day Mondays inside XM's Sep strips qualify).
HOLIDAYS_IN_STRIPS = {dt.date(2022, 9, 5), dt.date(2023, 9, 4)}


# ----------------------------------------------------------------------------- helpers
def third_friday(year, month):
    d = dt.date(year, month, 15)
    while d.weekday() != 4:
        d += dt.timedelta(days=1)
    return d


ROLLS = [third_friday(y, m) for y in range(2022, 2027) for m in (3, 6, 9, 12)]


def load_leg(leg):
    path = os.path.join(LEDGER_DIR, f"{leg.lower()}_trades_full.csv")
    rows = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            et = dt.datetime.strptime(r["et"], "%Y-%m-%d %H:%M:%S")
            rows.append((et, float(r["pnl"])))
    rows.sort(key=lambda t: t[0])
    return rows


def in_any_window(d, lo_off, hi_off):
    """calendar date d inside [R - lo_off, R + hi_off] for some quarterly R -> that R."""
    for R in ROLLS:
        if R - dt.timedelta(days=lo_off) <= d <= R + dt.timedelta(days=hi_off):
            return R
    return None


def classify(rows, lo_off, hi_off):
    hits = []
    for et, p in rows:
        R = in_any_window(et.date(), lo_off, hi_off)
        if R is not None:
            hits.append((et, p, R))
    return hits


def weekdays_between(a, b):
    """count Mon-Fri days in [a, b] inclusive."""
    n, d = 0, a
    while d <= b:
        if d.weekday() < 5:
            n += 1
        d += dt.timedelta(days=1)
    return n


def stationary_bootstrap_sums(x, n_boot, mean_block, seed):
    """Politis-Romano stationary bootstrap (circular); statistic = sum of a length-n resample."""
    rng = random.Random(seed)
    n = len(x)
    p = 1.0 / mean_block
    sums = []
    for _ in range(n_boot):
        s = 0.0
        i = rng.randrange(n)
        for _ in range(n):
            s += x[i]
            i = rng.randrange(n) if rng.random() < p else (i + 1) % n
        sums.append(s)
    sums.sort()
    return sums


def money(v):
    return f"${v:,.2f}"


# ----------------------------------------------------------------------------- main
def main():
    os.makedirs(OUT, exist_ok=True)
    L = []            # gate-table / console lines

    def say(s=""):
        L.append(s)
        print(s)

    P1 = load_leg("P1")
    XM = load_leg("XM")
    legs = {"P1": P1, "XM": XM}

    say("=" * 100)
    say("ROLL02_EXECSERIES_GATING_20260906   trial G00047   seed %d   %s" % (SEED, dt.date.today()))
    say("Prices exec-series-only roll gating: net in the strip [allSeriesBlock, execSeriesBlock).")
    say("Cost basis COMMISSION_ONLY ($4.36/ctrRT); evidence DISCOVERY_CONSUMED, in-sample.")
    say("=" * 100)

    # ---------------- step 1: reproduce G3_ROLLCOST_00 to the dollar (same-object proof)
    say("")
    say("STEP 1 - G3_ROLLCOST_00 reproduction (must match to the dollar or this run aborts)")
    checks = []

    obs = {g: classify(rows, LEAD, 1) for g, rows in legs.items()}     # [R-8, R+1]
    same = {g: classify(rows, LEAD, -1) for g, rows in legs.items()}   # [R-8, R-1]
    lead4 = {g: classify(rows, 4, 1) for g, rows in legs.items()}      # [R-4, R+1]

    n_obs = sum(len(v) for v in obs.values())
    net_obs = sum(p for v in obs.values() for _, p, _ in v)
    n_tot = len(P1) + len(XM)
    net_tot = sum(p for _, p in P1) + sum(p for _, p in XM)
    checks += [("observed trades", n_obs, G3_PUB["observed_n"]),
               ("observed net $", round(net_obs), G3_PUB["observed_net"]),
               ("total trades", n_tot, G3_PUB["total_n"]),
               ("total net $", round(net_tot), G3_PUB["total_net"]),
               ("same-day trades", sum(len(v) for v in same.values()), G3_PUB["sameday_n"]),
               ("same-day net $", round(sum(p for v in same.values() for _, p, _ in v)),
                G3_PUB["sameday_net"]),
               ("lead-4 trades", sum(len(v) for v in lead4.values()), G3_PUB["lead4_n"]),
               ("lead-4 net $", round(sum(p for v in lead4.values() for _, p, _ in v)),
                G3_PUB["lead4_net"])]
    for g in ("P1", "XM"):
        pn, ptot, pnet, ptotnet = G3_PUB["leg"][g]
        checks += [(f"{g} in-window trades", len(obs[g]), pn),
                   (f"{g} total trades", len(legs[g]), ptot),
                   (f"{g} in-window net $", round(sum(p for _, p, _ in obs[g])), pnet),
                   (f"{g} total net $", round(sum(p for _, p in legs[g])), ptotnet)]
    yr = {}
    for g in ("P1", "XM"):
        for et, p, _ in obs[g]:
            yr[et.year] = yr.get(et.year, 0.0) + p
    for y, tgt in sorted(G3_PUB["by_year"].items()):
        checks.append((f"in-window net {y} $", round(yr.get(y, 0.0)), tgt))

    ok = True
    for name, got, want in checks:
        flag = "OK " if got == want else "MISMATCH"
        if got != want:
            ok = False
        say(f"   {name:26s} observed {got:>10,}   published {want:>10,}   {flag}")
    if not ok:
        say("ABORT: G3_ROLLCOST_00 could not be reproduced exactly - not the same object.")
        raise SystemExit(1)
    say("   -> all 21 published figures reproduced to the dollar: SAME LEDGER, SAME WINDOWS.")

    # ---------------- step 2: the one-rule change - strips and the three window families
    #   all-series window  = [R - off - 8, R + 1]   (what the live guard actually does)
    #   exec-series window = [R - 8,      R + 1]   (== G3's published window, proven above)
    #   recovered strip    = [R - off - 8, R - 8)  (off = 2 for P1, 4 for XM)
    say("")
    say("STEP 2 - recovered strip per quarter (one rule changed: block from exec-series date only)")
    strip, allw = {}, {}
    for g, rows in legs.items():
        off = MIN_SERIES_OFFSET[g]
        allw[g] = classify(rows, LEAD + off, 1)
        strip[g] = [(et, p, R) for et, p, R in allw[g]
                    if et.date() < R - dt.timedelta(days=LEAD)]

    # per-leg observable quarters: strip fully inside the leg's ledger span
    quarters = {}
    for g, rows in legs.items():
        first, last = rows[0][0].date(), rows[-1][0].date()
        off = MIN_SERIES_OFFSET[g]
        quarters[g] = [R for R in ROLLS
                       if R - dt.timedelta(days=LEAD + off) >= first
                       and R - dt.timedelta(days=LEAD + 1) <= last]

    csv_path = os.path.join(OUT, "strip_by_quarter.csv")
    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["quarter_roll_date", "leg", "strip_start", "strip_end_incl",
                    "strip_trading_days", "trades", "net"])
        for g in ("P1", "XM"):
            off = MIN_SERIES_OFFSET[g]
            for R in quarters[g]:
                lo = R - dt.timedelta(days=LEAD + off)
                hi = R - dt.timedelta(days=LEAD + 1)
                days = weekdays_between(lo, hi) - sum(
                    1 for h in HOLIDAYS_IN_STRIPS if lo <= h <= hi)
                hits = [(et, p) for et, p, RR in strip[g] if RR == R]
                w.writerow([R.isoformat(), g, lo.isoformat(), hi.isoformat(), days,
                            len(hits), f"{sum(p for _, p in hits):.2f}"])
    say(f"   wrote {csv_path}")

    p1_strip_net = sum(p for _, p, _ in strip["P1"])
    xm_strip_net = sum(p for _, p, _ in strip["XM"])
    p1_days = []
    for R in quarters["P1"]:
        lo = R - dt.timedelta(days=LEAD + MIN_SERIES_OFFSET["P1"])
        hi = R - dt.timedelta(days=LEAD + 1)
        p1_days.append(weekdays_between(lo, hi)
                       - sum(1 for h in HOLIDAYS_IN_STRIPS if lo <= h <= hi))
    p1_days_per_q = sum(p1_days) / len(p1_days)

    span_wk = ((max(P1[-1][0], XM[-1][0]).date() - min(P1[0][0], XM[0][0]).date()).days) / 7.0
    say(f"   P1 strip [R-10,R-8): {len(strip['P1'])} trades  net {money(p1_strip_net)}  "
        f"over {len(quarters['P1'])} quarters  ({money(p1_strip_net / len(quarters['P1']))}/qtr, "
        f"{money(p1_strip_net / span_wk)}/wk on the ledger span)")
    say(f"   XM strip [R-12,R-8): {len(strip['XM'])} trades  net {money(xm_strip_net)}  "
        f"over {len(quarters['XM'])} quarters   [XM: in observation - secondary arm]")

    # ---------------- gates
    say("")
    say("=" * 100)
    say("GATE TABLE  (GATE / SPEC / OBSERVED / PASS-FAIL)  - printed by the program")
    say("=" * 100)
    results = {}

    # G1_money -------------------------------------------------------------------------
    x = [p for _, p, _ in sorted(strip["P1"], key=lambda t: t[0])]
    sums = stationary_bootstrap_sums(x, N_BOOT, MEAN_BLOCK, SEED)
    ci_lo, ci_hi = sums[int(0.05 * N_BOOT)], sums[int(0.95 * N_BOOT) - 1]
    frac_le0 = sum(1 for s in sums if s <= 0) / len(sums)
    yr_strip = {y: 0.0 for y in range(2022, 2027)}
    for et, p, _ in strip["P1"]:
        yr_strip[et.year] += p
    n_pos = sum(1 for v in yr_strip.values() if v > 0)
    ci_excl_0 = (ci_lo > 0) or (ci_hi < 0)
    g1 = ci_excl_0 and (n_pos >= 3)
    results["G1_money"] = g1
    say("G1_money")
    say("   SPEC    : P1-only pooled strip net: stationary-bootstrap CI90 excludes 0 AND net")
    say("             positive in >= 3 of calendar years 2022..2026; else KILL family.")
    say(f"   OBSERVED: strip net {money(p1_strip_net)} (n={len(x)} trades); stationary bootstrap")
    say(f"             (B={N_BOOT}, mean block {MEAN_BLOCK}, seed {SEED}) CI90 = "
        f"[{money(ci_lo)}, {money(ci_hi)}]  -> excludes 0: {ci_excl_0}"
        f"  (P(resample sum <= 0) = {frac_le0:.3f})")
    say("             by-year strip net: " + ", ".join(
        f"{y} {money(v)}" for y, v in sorted(yr_strip.items()))
        + f"  -> positive in {n_pos}/5 years (need >=3: {n_pos >= 3})")
    say(f"   PASS-FAIL: {'PASS' if g1 else 'FAIL -> KILL'}")

    # G2_frequency ---------------------------------------------------------------------
    say("G2_frequency")
    p1_first, p1_last = P1[0][0].date(), P1[-1][0].date()
    base_wd = weekdays_between(p1_first, p1_last)
    base_rate = len(P1) / base_wd
    strip_rate = len(strip["P1"]) / sum(p1_days)
    ratio = strip_rate / base_rate
    base_rate_cal = len(P1) / ((p1_last - p1_first).days + 1)
    strip_rate_cal = len(strip["P1"]) / (len(quarters["P1"]) * MIN_SERIES_OFFSET["P1"])
    g2_restate = ratio < 0.5
    results["G2_frequency"] = True  # informational gate: always evaluable; restate if needed
    say("   SPEC    : print strip entry rate vs baseline entry rate; if strip < 50% of baseline,")
    say("             restate every headline at the measured rate.")
    say(f"   OBSERVED: P1 strip {strip_rate:.3f} entries/trading-day ({len(strip['P1'])}/{sum(p1_days)})"
        f" vs baseline {base_rate:.3f} ({len(P1)}/{base_wd} weekdays) -> ratio {ratio:.1%}")
    say(f"             (calendar-day basis: strip {strip_rate_cal:.3f} vs baseline {base_rate_cal:.3f}"
        f" -> ratio {strip_rate_cal / base_rate_cal:.1%})")
    say(f"   PASS-FAIL: ratio {ratio:.1%} >= 50% -> headlines stand at face value"
        if not g2_restate else
        f"   PASS-FAIL: ratio {ratio:.1%} < 50% -> HEADLINES RESTATED at measured rate")

    # G3_materiality -------------------------------------------------------------------
    g3 = p1_days_per_q > 1.0
    results["G3_materiality"] = g3
    say("G3_materiality_vs_latch_kill")
    say("   SPEC    : P1-only recovered TRADING days per quarter must exceed 1.0 (the bar at")
    say("             which DRAWDOWN_ANATOMY killed the latch-fix as immaterial); else KILL.")
    say(f"   OBSERVED: {p1_days_per_q:.2f} trading days/quarter "
        f"({sum(p1_days)} days over {len(p1_days)} quarters; strip = Tue+Wed before expiry week)")
    say(f"   PASS-FAIL: {'PASS' if g3 else 'FAIL -> KILL'}")

    # G4_risk_premise ------------------------------------------------------------------
    results["G4_risk_premise"] = None
    say("G4_risk_premise")
    say('   SPEC    : "OPEN by construction: the strip is only free if the execution series is')
    say('             genuinely tradable there. This gate is NOT decidable from local data (no')
    say('             historical back-month quotes exist) and is explicitly deferred to the')
    say('             2026-09 crossover quote capture now running')
    say('             (research/operational/roll_quotes/quotes.csv). The report must print it as')
    say('             OPEN - a G1-G3 PASS with G4 open licenses further measurement, never a')
    say('             build."')
    say("   OBSERVED: deferred by construction; nothing in this run can close it.")
    say("   PASS-FAIL: OPEN")

    # G5_semantic ----------------------------------------------------------------------
    say("G5_semantic")
    say("   SPEC    : one sentence per headline stating its population/event; and the identity")
    say("             strip_net + remaining_blackout_net = blackout net must reconcile to the $.")
    say("   HEADLINE SEMANTICS:")
    say(f"     - '{money(p1_strip_net)} P1 strip net' is the sum of COMMISSION_ONLY P&L of the "
        f"{len(strip['P1'])} historical P1")
    say("       trades (of 2439, 2022-01-02..2026-08-25, in-sample, DISCOVERY_CONSUMED) whose ENTRY")
    say("       calendar date fell on the 2 trading days [R-10, R-8) before each of 18 quarterly")
    say("       third-Friday rolls - the days the live all-series guard blocks but an exec-series-")
    say("       only guard would not.  It is NOT forward, NOT a strategy, and says nothing about")
    say("       fills (G4 OPEN).")
    say(f"     - '{money(xm_strip_net)} XM strip net' is the same event over the 4-day strip "
        f"[R-12, R-8) for the")
    say("       XM leg (in observation - secondary); negative means the earlier all-series block")
    say("       historically HELPED that leg.")
    say(f"     - '{p1_days_per_q:.2f} recovered days/quarter' counts CME trading days (Mon-Fri minus")
    say("       full closures) inside the P1 strip, averaged over the 18 observable quarters.")
    say("   RECONCILIATION (all-series window = strip + remaining blackout, per leg, to the $):")
    recon_ok = True
    for g in ("P1", "XM"):
        all_net = sum(p for _, p, _ in allw[g])
        rem_net = sum(p for _, p, _ in obs[g])           # exec window == G3's published window
        st_net = sum(p for _, p, _ in strip[g])
        n_ok = len(allw[g]) == len(strip[g]) + len(obs[g])
        d_ok = abs(all_net - (st_net + rem_net)) < 0.005
        g3_ok = round(rem_net) == G3_PUB["leg"][g][2]
        recon_ok &= n_ok and d_ok and g3_ok
        say(f"     {g}: strip {money(st_net)} + remaining {money(rem_net)} = "
            f"all-series {money(all_net)}   trades {len(strip[g])}+{len(obs[g])}={len(allw[g])}"
            f"   remaining==G3 published ${G3_PUB['leg'][g][2]:,}: {g3_ok}")
    pooled_all = sum(p for g in legs for _, p, _ in allw[g])
    say(f"     pooled: strip {money(p1_strip_net + xm_strip_net)} + remaining "
        f"{money(net_obs)} = all-series {money(pooled_all)}   remaining==G3 published "
        f"$106,106: {round(net_obs) == 106106}")
    say("     NOTE (preregistration premise corrected): G3's published window is PROVEN above to")
    say("     be the exec-series window itself (its single third-Friday table IS the MNQ/YM-like")
    say("     date), so 'remaining blackout' EQUALS G3's cut and the strip lies OUTSIDE it; the")
    say("     identity holds with G3's number as the remaining-blackout term.  Under the spec's")
    say("     literal premise (G3 window = all-series window) the strip would be EMPTY - a")
    say("     degenerate reading recorded as a deviation in REPORT.md, not used.")
    results["G5_semantic"] = recon_ok
    say(f"   PASS-FAIL: {'PASS (reconciles to the dollar)' if recon_ok else 'FAIL'}")

    # ---------------- verdict
    say("")
    say("=" * 100)
    kill = (not results["G1_money"]) or (not results["G3_materiality"])
    verdict = "KILL" if kill else "PASS-gated-on-G4"
    say(f"VERDICT: {verdict}")
    if kill:
        say("  Per the preregistered decision rule: per-series roll gating is CLOSED as")
        say("  not-worth-building; the blackout stands as the price of the fail-safe.")
    else:
        say("  G1-G3 PASS with G4 OPEN: licenses further measurement only (crossover quote")
        say("  capture), never a build; any successor needs a new ROLL03 spec, a new class name")
        say("  and full re-certification (owner decision).")
    say("=" * 100)

    with open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
