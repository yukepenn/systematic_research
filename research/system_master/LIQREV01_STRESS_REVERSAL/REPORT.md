# LIQREV01 — REPORT (readout 2026-08-19; spec frozen at 9775c0a BEFORE the run)

**Verdict: ALL 8 FROZEN GATES PASS ON THE LETTER — CANDIDATE FREEZE WITHHELD by orchestrator
adjudication after the red team (the W9-B1 precedent: a letter-pass whose substantive claims the
red team refutes does not freeze). Status: PARKED — REGIME-LOCAL(2020+), engine-#3 role REFUTED,
resolution by forward data (added to the MONITOR-01 shadow protocol). Second and final alpha
hypothesis of this wave (cap 2/2).**

## 1. Headline (dev substrate 2007-03-02 → 2026-05-29, C1 costs)

N=455 (243 long / 212 short) · net **$263,646** ($579/trade) · episode-block bootstrap CI
[+$155, +$1,061] · long cell +$552/t AND short cell +$611/t · calm placebo −$43/t (CI spans 0) ·
3×3 plateau all positive, monotone in stress percentile · top-1% share 33.6% · worst trade
−$23,134 · losing-day ρ vs Solar 0.062. Gates G1–G8b: all PASS as frozen.

## 2. Red team (4 attackers, all bit-exact reproductions; no implementation kill)

**What SURVIVED attack (genuinely in the result's favor):**
- **No lookahead; fill realism robust**: entry delayed to 15:59 / 16:03 / next-day 09:30 open
  all keep G2 (down to $528/t, CI_lo +$147). The edge accrues in the NEXT day's RTH
  ($542/t of gross), not the overnight gap ($51/t) — reversal-shaped, not gap-shaped.
- **The stress conditioning is real**: a properly MATCHED placebo (calm days matched to each
  stress trade on signed point move, 452/455 within 20% caliper) returns −$162/t, CI [−474,+146]
  — same-size moves on calm days earn nothing; the state carries a ~$740/trade spread.
- Roll/splice not a driver; costs robust (3× commission + 2-tick slip: $561/t, CI_lo +$136);
  no trade-overlap double-counting; stationary block bootstraps keep CI_lo>0.

**What KILLED the claims (binding, each verified by computation):**
1. **All statistical evidence is post-2020.** Pre-2020 (301 trades, 13 years, 47 episodes):
   +$12.2/t, episode CI [−171, +187] — G2 fails standalone on two-thirds of the sample.
   Post-2020 (154 trades): +$1,688/t, CI [+687, +2,546]. 98.6% of net post-2020; pre-2016 net
   −$14,353 with BOTH cells negative. Top-3 episodes (COVID-2020, Apr-2022, Mar-2025) = 64.7%
   of net from 9.7% of trades; ex-top-3 episode CI spans zero. Effective N ≈ 5 macro events.
2. **The mechanism label is wrong.** The trailing-252-percentile state assigns ZERO stress
   sessions to 2009 (late-2008 saturates the window) and 68/67 to calm 2014/2024; the
   mechanism-canonical clusters (2008-09 = Nagel's own sample; 2015-16) are NEGATIVE. What
   passed is "vol-acceleration-gated reversal worked 2020-2026", not a 20-year
   intermediary-capital premium. G3's 5-of-7 is sign-noise (only 2020 individually significant).
3. **Engine-#3 (diversification) role REFUTED.** On the 2022-26 overlap with the certified
   Solar B ledger: LIQREV's profit lands almost entirely on Solar's TOP-decile days (+$148,934
   on 14 days; excluding them −$1,978); on Solar's BOTTOM-decile days LIQREV nets −$46,517;
   LIQREV traded ZERO times inside Solar's entire maxDD window (2025-04→07); worst combined day
   −$29,853 (76% worse than any Solar-alone day); combo ΔSharpe +0.18 with CI [−0.32, +0.70] —
   statistically nothing. G7's losing-day-corr gate (0.062, PASS) measured a scale-free
   functional blind to this level shift — the decision-relevant number was in the same results
   file (−$46,028) and non-gating. Per OWNER_DIRECTIVE §19/§22 (complementarity measured in the
   drawdown region), this is an anti-complement / right-tail amplifier of Solar.
   Mitigating note: on Solar's 20 single worst days LIQREV was mildly positive (+$9,079); the
   damage concentrates on mid-decile crash days (2025-04-04: Solar −$6.7k + LIQREV −$23.1k).
4. **Standalone it is not investable**: 20-yr grid Sharpe 0.680 with a 7.2-YEAR underwater
   stretch (2011→2018); one trade = 16.0% of 20 years of net.

**Defects to the run itself (disclosed, direction mostly favorable):**
- G8e was implemented as a ret-z proxy, not the spec's overnight-gap flag; the proxy excluded
  exactly the largest winner. The CORRECT flag (computed by the red team from minute data)
  excludes 7 trades netting −$18,881 → ex-flag per-trade **rises** to $631. The published G8e
  row is superseded by this one.
- Episode definition deviated (trade-gap runs, 75, vs spec's stress-session runs, 66);
  spec-conformant CI [+151, +1,065] — immaterial. G6 max-single-share checked the largest
  winner only (worst loser 8.8%, unaffected). Substrate defects found and logged: a missing
  week 2014-01-27..31 + scattered missing weekdays; 13:00-halt holiday Globex sessions pass the
  200-bar filter (11 entries/15 exits on thin days, net −$15,695, conservative direction).

## 3. Disposition (frozen going forward)

- **PARKED — REGIME-LOCAL(2020+).** No candidate freeze, no portfolio-integration step. The
  Nagel/structural-premium framing is struck from the record; the honest object is a real,
  fill-robust, placebo-clean **post-2020 vol-acceleration reversal effect** with effective
  N≈5 episodes and refuted diversification value.
- **Forward resolution**: added as a second frozen construction to
  `research/operational/MONITOR01_SHADOW_HTFDIR01.md` (amended before any reading exists) —
  quarterly evaluation-only ledger extension; ADVANCE requires the forward window to show BOTH
  positive economics AND non-negative P&L on Solar's forward losing days (the exact functional
  the dev window failed); KILL on the protocol's standard adverse thresholds.
- The stress-state infrastructure (rv5 percentile series, matched-placebo machinery) is
  retained as reusable analytics. The three queued scout candidates (CLOSEREV, TOM-FLOW,
  TERMFLOW) remain for a FUTURE wave — this wave's alpha budget (2/2) is exhausted.

## 4. Bookkeeping

Artifacts: `out/liqrev01_results.json`, `liqrev01_trades.csv`, `liqrev01_placebo_trades.csv`
(all reproduced bit-exact by 4 independent attackers). Seal: substrate ends 2026-05-29; nothing
≥2026-06 exists in any input (verified twice). Registry: TESTING_LEDGER row this commit.
Red-team full outputs: workflow transcripts (4 attackers, 65 tool calls).
