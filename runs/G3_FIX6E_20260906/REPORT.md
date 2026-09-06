# G3_FIX6E_20260906 — month-end London 4pm fix equity-hedge rebalancing in 6E

**Ledger G00091 · family GENESIS3_EVENT · world-scan card #23 · executed 2026-09-06 · spec frozen before results (`spec.yaml`).**

## VERDICT: **FAIL — CLOSED AT SCOPE (§28)**

All three preregistered outcome gates failed, and not by inches on one clause — **the slope is ~zero everywhere the card could live.** The fix-day 6E return has no relationship to the month's ES performance: full-sample slope **−0.0018** (boot 95% CI [−0.0282, +0.0249], shift p₁ 0.545), i.e. a +1-sd equity month (+4.13% ES MTD) predicts a fix-day 6E move of **−$9/event** where the mechanism demanded a positive one. The reversal leg is wrong-signed (+0.0101, ~0). The card's own kill clause fires directly: **post-2015 slope −0.0015, CI [−0.0234, +0.0188] — "~0" exactly as the reform-decay test defines dead** — but so is the pre-2015 slope (−0.0039), so this is not decay; the effect is absent in daily data across the whole sample. Conditioning to top-tercile |signal| months — "where the card says survivability lives" — *inverts* the sign: mechanism-direction fix-day P&L is **−$89/event gross** there (vs +$47 unconditionally), against a $10.61–$16.86 cost rung.

**Power honesty (G1, printed first):** MDE slope 0.0289 → at the top-tercile mean |signal| (6.38% ES MTD) the detectable fix-day effect is ~0.0018 pts ≈ **16 bps ≈ $230/event at 80% power**. The card's own documented effect band ("tens of bps on strong-signal month-ends", Melvin-Prins lineage) sits at or above that bar, so this is a **powered null against the card's stated band** (underpowered only for ≤~10 bp effects, which would be sub-cost anyway). All validity gates passed; the outcome gates failed and are recorded failed.

## Construction (frozen object, implemented exactly; pins declared in `src/fix6e.py` header before results)

- **Inputs AS-IS, no rebuild**: ES `runs/G3_AUCTCYCLE_20260906/out/es_daily.parquet` sha256 `249921cb6d790b8478910fabbc480e0ac82a3d20a206b38fedb34fa1b2054f91` (identity-gate maxerr 0.0, roll causal — AUCTCYCLE manifest); 6E `runs/DAILY_6E_EXTRACT_AUTOPSY_20260906/out/6e_daily.parquet` sha256 `af70be2d857019b932be715feb8d3362233da6f9278f6e75687b121e8aa19eae` (reproduces certified s7 transport exactly; 6E roll = effectively fixed 5-day pre-expiry, s6-sanctioned and named). Both shas asserted in-program; seal asserted (max session 2026-07-31 < 2026-08-01, both).
- **Event axis**: joint ES∩6E sessions (4,166; 2009-03-31 → 2026-07-31). T = last joint day of month m (the fix day); windows: FIX = close(T−1)→close(T), REV = close(T)→close(T+3), both sums of self-financing causal-roll 6E POINT returns.
- **Signal** (spec: "MTD ES return through T-2", causal): sum of ES point returns (prev-month last joint close → T−2 close) ÷ **raw unadjusted** ES close at prev-EOM — fraction units, basis-free numerator, never a back-adjusted level (DELEV01-safe; ES levels moved ~8× over the sample, raw points would not be cross-era comparable). One-day causal buffer T−2 → T−1 by construction (176/176 events verified).
- **Inference**: OLS slopes; circular event-block bootstrap CIs (N=2000, block 6, (signal,fix,rev) rows resampled jointly); OLS-normal CI printed as second computation; shared-draw circular-shift null (one offset per draw applied to BOTH legs). Seed 20260906.
- **G4 pin**: reform date 2015-02-15 (WM/R 5-minute window effective); "post-2015 slope ~ 0" operationalized as PASS iff slope_post > 0 AND post-era boot CI excludes 0.

## Key numbers (all `DISCOVERY_CONSUMED`, in-sample; costs MODELED = commission + k-tick)

| leg | slope | boot 95% CI | OLS-normal CI (2nd) | p_shift(1s) |
|---|---:|---:|---:|---:|
| FIX close(T−1)→close(T) | **−0.00182** | [−0.02824, +0.02490] | [−0.02455, +0.02092] | 0.5452 |
| REV close(T)→close(T+3) | **+0.01007** | [−0.03888, +0.04781] | [−0.03529, +0.05544] | 0.6577 |

| era | n | fix slope | boot 95% CI | rev slope |
|---|---:|---:|---:|---:|
| PRE (<2015-02-15) | 62 | −0.00390 | [−0.07518, +0.06820] | +0.05051 |
| POST | 114 | **−0.00150** | [−0.02338, +0.01884] | −0.00762 |

- Events: 205 candidate months → **176 computed** (29 integrity drops: no_prev_month 1, short_month 7, short_next 1, signal_unclean 17, fix_unclean 0, rev_unclean 3 — ledger closes exactly). Honest count below the spec's ~210: the ES 2025-summer store hole removes 2025-07/08 from the axis entirely, and ES/6E gap guards eat the rest. Span 2009-04 → 2026-05.
- Conditional table (|signal| terciles, both signs, matched unconditional controls in the same table — `out/tercile_table.csv`): ALL 176: fix −$1/event; ALL sig>0 (n=118): +$34; ALL sig<0 (n=58): −$73; **top tercile sig>0 (n=40): −$129** (mechanism says positive); top tercile sig<0 (n=19): +$7 (mechanism says negative). The sign pattern that weakly matches the mechanism in the full sample disappears exactly where the card said it would concentrate.
- G5 cost: 1 RT 6E/event; rungs $10.61 (1-tick) / $16.86 (2-tick); top-tercile mechanism-direction net **−$100 / −$106 per event**.

## Banked either way (control-table facts, not edge claims)

- **The generic month-end 6E fix-day drift is ~zero**: unconditional mean −0.00001 pts (−$1/event, n=176); mean |fix-day move| 0.00484 pts (~42 bps) — any tens-of-bps flow component would have been visible against this.
- The unconditional 3-day post-month-end 6E drift is also ~zero (−$58/event).

## Gate table

Program-printed in `out/gate_table.txt` (GATE/SPEC/OBSERVED/PASS-FAIL): G0a–G0g, G1, G5, G6, G7 PASS; **G2 FAIL, G3 FAIL, G4 FAIL**. Decision rule applied mechanically (spec verbatim): G2+G3+G4 not all PASS → closed at scope.

## §28 closure block

```
Closed:  observable = 6E causal-roll daily point returns (certified extract, sha af70be2d..) + ES causal-roll
  daily point returns (AUCTCYCLE build AS-IS, sha 249921cb..), 2009-03..2026-07
representation = month-end fix event study: fix-day 6E return close(T-1)->close(T) and reversal
  close(T)->close(T+3) regressed on MTD ES self-financing return through T-2 (fraction units, raw-level
  denominator, causal); |signal|-tercile conditional table both signs with matched unconditional controls;
  era split at the 2015-02-15 WM/R reform
event = 176 month-ends (205 candidates - 29 integrity drops), PRE 62 / POST 114     horizon = 1d fix + 3d revert
target = preregistered conjunction: fix slope > 0 with boot CI excluding 0 AND revert slope < 0 AND
  post-2015 slope > 0 with boot CI excluding 0
execution = screen-level cost only ($4.36 commission + {1,2}-tick 6E, 1 RT/event, MODELED)
sample = 2009-04..2026-05 month-ends (DISCOVERY_CONSUMED)
reason = slope ~ZERO everywhere: full -0.0018 (CI [-0.028,+0.025], p1 .55), post-2015 -0.0015 (CI
  [-0.023,+0.019]) -- the card's own kill clause ("dead if post-2015 slope ~ 0") fires, and pre-2015 is
  just as dead (-0.0039), so it is absence, not decay; reversal wrong-signed (+0.0101); top-|signal|-tercile
  mechanism-direction P&L -$89/event GROSS (inverts where the card said survivability lives); MDE $230/event
  at top-tercile signal = powered against the card's documented tens-of-bps band.
```
Still open (adjacent): NOT closed by this run — the fix flow at **intraday** resolution (the documented effect is concentrated in the minutes around the 4pm London fix; a daily close-to-close window drowns it in ~42 bps of average daily noise — this run closes the *daily-representation* card only, which is exactly the survivability the world-scan card was built to test); quarter-end (vs month-end) hedge rebalancing with bond-inclusive signals (different signal object); other FX roots in the daily panel (6B/6J) under a NEW mechanism card — though this result prices the same daily representation there as near-certainly null. Any intraday reopening requires 6E intraday data, which the repo does not hold and which is owner-gated SPEND (Databento fork) — priced, not pursued.

## Outputs

- `out/gate_table.txt` — program-printed report + gate table
- `out/regression.csv` — all 176 events: anchors, signal, base close, fix/rev legs (pts and $), era, tercile, sign
- `out/tercile_table.csv` — conditional table with matched unconditional controls
- `out/verdicts.json` — machine-readable verdict + gates; `out/inputs_manifest.json` — shas, provenance, identity/roll evidence
- `src/fix6e.py` — the program (all pins in the header, declared before results)

## Notes / anomalies (none improvised around)

1. Spec's "~210 month-ends" → honest 176: ES 2025-summer hole (2025-07/08 absent from the joint axis entirely), ES 2026-06-09..12 hole (kills the 2026-06 signal window), 6E 2016-01 27-day outage, plus standard month-integrity guards. Drop ledger closes exactly (205 − 29 = 176).
2. Spec is silent on signal units → pinned in the code header before results: fraction units = points sum ÷ raw unadjusted prev-EOM ES close (basis-free numerator; the DELEV01 %-on-back-adjusted trap cannot enter because the denominator is the true held-front level).
3. Spec is silent on the operational meaning of "post-2015 slope ~ 0" and the reform date → pinned before results: 2015-02-15; G4 PASS iff post slope > 0 AND post-era block-boot CI excludes 0.
4. G3's frozen clause is SIGN-ONLY ("reversal-leg slope opposite-signed") and was implemented sign-only with the CI printed as informational; it failed on sign regardless (+0.0101).
5. The 6E roll is effectively a fixed 5-day pre-expiry rule (1 volume-crossover / 69 pre-expiry overrides) — an s6-sanctioned, *named* property of the certified input, not a deviation.
6. Family note (world-scan dedup clause): this card shares the month-end calendar family with G3_MEREBAL (G00077). Within-run nulls are shared-draw; both family members are now closed, so no cross-run multiplicity adjustment is pending on a survivor.
7. |signal|-tercile cuts are full-sample (descriptive, declared, not gate-bearing); the gates never touch the terciles.
8. This REPORT.md was returned via structured output (harness refused the file write for subagents); orchestrator to place it at `runs/G3_FIX6E_20260906/REPORT.md`. `SEARCH_LEDGER.jsonl` untouched (read-only for pods); G00091 RESULT row is the orchestrator's.