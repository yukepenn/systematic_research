# G3_AUCTCONC_20260906 — the CONCESSION half of the auction cycle (AUCTCONC01) — CLOSED

**Ledger:** G00080, family GENESIS3_EVENT (registered before outcomes). **Spec:** `spec.yaml`, committed `a311e59` before results. **Date executed:** 2026-09-06. **Evidence status:** DISCOVERY_CONSUMED (second and last preregistered read of the auction-cycle family; the era split was read for the FIRST time inside this run's gates). Mirror debt honored: every null p ×2 (Bonferroni, 1 of exactly 2 preregistered halves), MDE alpha halved.

**Frozen object:** SHORT the matching future (ZN for 10y, ZB for 30y) at close(D-5); exit at close(D0). Events = the exact 414 mapped auctions in `runs/G3_AUCTCYCLE_20260906/out/event_study.csv` AS-IS; series = that run's certified causal-roll parquets AS-IS (all 5 input shas printed; parquet shas asserted against the certified manifest; conc_A recomputed and matched < 1e-9; meaning cross-checked as close[p]−close[p−5] on 411/411 roll-free windows; seal max 2026-07-31 < 2026-08-01).

## Verdict

**CLOSED — the decision rule's negative branch fired mechanically: G2(portfolio) FAIL. With it the auction-cycle family is FULLY closed (both halves) → FAILURE_MEMORY.**

The concession-short is the most alive-looking object this family produced, and it still does not clear the preregistered bar on the economically honest rendering. The D-5..D0 windows overlap across the two roots at **0.993** — nearly every event double-counts a sibling week — so per spec G6 the gate is carried by the deduplicated one-position-at-a-time portfolio: **207 trades, +$69.92/trade after conservative cost, event-block CI95 [−$67.25, +$207.98]** — the CI includes 0 and G2 fails on that clause, with the mean clause and the null clause (p×2 = 0.0430 < 0.05) both passing. The observed effect sits below the portfolio MDE ($178 at the debt-adjusted alpha): a positive-but-unpowerable result, not a powered kill.

**What the never-read era split showed (first read):** the concession-short is the exact mirror of the rebound's decay — pooled after-cost **−$41.53 (2009-15) / +$186.61 (2016-21) / +$238.12 (2022-26/07)** = **REGIME-LOCAL**, growing in the modern era exactly as the rebound (+$204/−$82/−$439) died. One mechanism-consistent story: the pre-auction concession no longer mean-reverts after the auction — it has become drift that continues. G3 passed decisively pooled (delta vs matched control **+$259.07**, CI [+$78.02, +$448.94]; control days short-lose −$148.54 because rates drifted up). G5 confirms the spec's worry: ES gains **+$507.58 gross** over the same windows (CI excludes 0), so the short side genuinely fights equity beta on those days (short-side z ratio −1.40).

## Gate table (program-printed, verbatim; full log in `out/gate_table.txt`)

```
GATE            SPEC                                                                            OBSERVED                                                                      PASS-FAIL
G1_MDE_FIRST    MDE printed before observed; x2 debt on alpha; pooled floor 300                 pooled MDE $215 @N=411; portfolio MDE $178 @N=207                             PASS
G2_EDGE(PORT)   PORTFOLIO after-cost cons mean>0 AND event-CI ex 0 AND 2xp_shift<.05            mean $+69.92, CI [-67.25,+207.98], px2 0.0430                                 *** FAIL ***
G3_CONTROL      beats matched mkt x weekday non-auction control (short); delta CI ex 0          delta $+259.07, CI [+78.02,+448.94]                                           PASS
G4_ERA          signs 2009-15/2016-21/2022-26; all+ STRUCT / modern-only RL / modern<=0 FAIL    -/+/+ -> REGIME-LOCAL                                                         PASS
G5_SPECIFICITY  ES same-window read printed (short side fights equity beta?)                    ES long gross $+507.58; short cons $-536.94 CI [-937.49,-143.80]              PASS
G6_OVERLAP      overlap fraction + dedup one-position portfolio printed; carries G2             overlap 0.993 (cross-root 0.993); 207 taken of 414                            PASS
G7_COST         ZN $35.61 / ZB $66.86 cons rung asserted; events/yr economics printed           rungs asserted; 23.8 ev/yr pooled, 12.0 trades/yr port                        PASS

DECISION RULE (spec, mechanical): G2(portfolio)=FAIL G3=PASS G4=REGIME-LOCAL -> CLOSED -- auction-cycle family FULLY closed (both halves) -> FAILURE_MEMORY
```

## Key observed numbers (cost basis: MODELED COMMISSION+SPREAD, conservative 2-tick rung gates)

| quantity | POOLED (printed beside, non-gating) | PORTFOLIO (gating) |
|---|---|---|
| n | 411 (3 dropped pre-series) | 207 taken / 204 BUSY / 3 no-outcome (ZN 205, ZB 2) |
| gross / cons / opt per event | +$161.72 / **+$110.53** / +$133.95 | +$105.83 / **+$69.92** / +$85.69 |
| event-block CI95 (cons) | [−$40.84, +$271.42] | **[−$67.25, +$207.98] → includes 0** |
| shared-draw shift null | mean −$71.20 sd $73.77; p_1s .0085 → **×2 .0170** | mean −$52.06 sd $58.71; p_1s .0215 → **×2 .0430** |
| MDE (α 2.5% 1-sided, 80%) | $215 | $178 |
| vs matched control | ctrl −$148.54; **delta +$259.07 CI [+78.02, +448.94]** | ctrl −$82.55; delta +$152.46 CI [−14.48, +306.45] (annex) |
| eras (cons) | **−$41.53 / +$186.61 / +$238.12 → REGIME-LOCAL** | −$111.81 / +$175.43 / +$202.30 (annex) |
| economics | 23.8 ev/yr → +$2,634/yr (double-counts weeks) | **12.0 trades/yr → +$839/yr/contract** |
| annexes | cluster-month CI [−$81.09, +$307.30]; ZN +$27.35 vs ZB +$194.12; originals +$128.91 vs reopenings +$101.24 | — |

Null construction: 2000 circular shifts, MIN_SHIFT 30, one shared uniform draw per iteration across ZN+ZB, seed 20260906; the SAME draws evaluate both renderings. Null event in words: P(a random joint circular placement of the auction-day mask on the ZN/ZB session axes yields a mean after-cost concession-short ≥ observed). CIs: event-block bootstrap, 2000 draws, percentile 2.5/97.5.

## §28 closure block

```
Closed:  observable = ZN+ZB certified causal-roll daily continuous 2009-03-31..2026-07-31 +
  the 414 AS-IS mapped 10y/30y auction events from G00073 (shas printed, era split first-read here)
representation = SHORT matching future close(D-5) -> close(D0); dedup one-position-at-a-time
  portfolio carries the edge gate (0.993 window overlap across roots); matched mkt x weekday
  control (short side); shared-draw circular-shift null, Bonferroni x2 (mirror debt)
event = 10y note / 30y bond auction (originals + reopenings)      horizon = 5 trading days back
target = portfolio after-cost mean > 0 with CI ex 0 and 2x shift-p < .05; beats control; era read
execution = MODELED $4.36 RT + 2-tick conservative (ZN $35.61, ZB $66.86/ctRT)
sample = 411 pooled / 207 portfolio events 2009-04..2026-07 (DISCOVERY_CONSUMED, 2nd/last read)
reason = portfolio CI includes 0 (+$69.92, [-67,+208]) with observed mean below MDE ($178):
  positive, null-clearing (px2 .043), control-beating pooled (+$259, CI ex 0), era REGIME-LOCAL
  (-/+/+ mirror of the rebound's decay) -- but unpowerable at the honest rendering; ~12 trades/yr,
  ~$839/yr/ct gross-of-slippage economics; family closed BOTH halves per the preregistered rule
```

**Still open (adjacent, NOT closed by this run):** intraday paths around the 13:00 ET auction result (owner-gated data); when-issued vs futures basis (no data). **Closed with this run:** the entire daily-representation auction-cycle family — both preregistered halves, all D-window re-parameterizations on this representation.

## Anomalies / declarations (none improvised around)

1. G2 failed solely on the CI clause; mean and null clauses passed on the gating rendering. Recorded FAILED per the mechanical rule; the near-miss character is disclosed, not re-litigated.
2. The dates-only C5 dedup rule (declared before outcomes) yields an effectively ZN-only portfolio (205/207) because 10Y auctions nearly always precede 30Y in the same week — and ZN is the weaker leg ($27 vs $194/event). No alternate ordering rule was tried post-hoc.
3. n_eff = 411 vs the spec's ~406 estimate (backward window drops only 3 early events). Floor 300 passed.
4. All 411 event windows are roll-free (auction weeks never straddle the treasury volume-crossover roll), so the close-diff meaning check was total, not sampled.
5. REPORT.md returned via structured output per harness policy on report files (G00073 precedent); all other spec outputs exist on disk.

## Artifacts (all under `runs/G3_AUCTCONC_20260906/`)

- `src/auction_concession_study.py` — full program incl. declarations C1–C10 (written before outcomes)
- `out/gate_table.txt` — complete program-printed log incl. gate table and decision line
- `out/event_table.csv` — the 414-event pooled table with short-side P&L columns
- `out/portfolio_rendering.csv` — chronological dedup walk: taken/BUSY/NO_OUTCOME per event
- `out/era_table.csv` — the G4 table (pooled gate + portfolio annex)
- `out/verdicts.json` — machine-readable verdicts incl. input shas