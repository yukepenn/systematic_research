# W19R1_SELECTIVITY — RESULTS

Run against `spec.yaml` (frozen `d4926a4`) **exactly as written, unmodified**, per owner directive
"FINAL OPTIMIZATION DIRECTIVE" §5 S1 ("Run the already-frozen W19R1 spec unchanged first. Do not
rewrite history."). The D7-boundary split required by the same directive is reported below as a
**separate addendum** (§5), not as a change to the frozen gate logic. Code: `src/scores_transform.py`,
`src/run.py`. Control cross-check against the frozen reference curve
(`runs/SMV2AD_VOLMULT_CEILING/out/e10_daily_dev_control_1200.csv`): **1,139/1,139 matched, max
abs diff 1.8e-12 — PASS.**

## Headline

**Both arms are CONFIRMED-NOT-BENEFICIAL under the frozen gates.** That is the binding verdict and
neither is a CANDIDATE this wave, per the spec's own rule ("No adoption this wave regardless of
outcome"). But the frozen spec pre-registered a disclosure that turns out to matter more than the
pass/fail line:

**arm_TOD's cross-instrument cohort table shows NQ's own D4 time-of-day structure is NOT present
on ES/RTY/YM.** D4 (Wave 18) found NQ's worst cohort is EVENING (26.0% of bars, −9.2% of P&L). On
ES/RTY/YM — averaged, P&L-fraction of each cohort — **RTH is the worst cohort (−72.8% of total net
P&L, i.e. structurally negative) and OVERNIGHT is the best (+148.1%)**; EVENING is middling
(+24.6%). **These do not match.** Per the frozen spec's own pre-registered instruction (§4
mandatory disclosures): *"If it is NOT present, that is the headline finding of this run and it
must be stated as such, because it would mean D4's cohort split is an NQ-specific artifact and the
program has been reasoning from it wrongly."* Stated as instructed: **D4's EVENING-is-worst finding
looks like an NQ-specific artifact, not a general index-futures property.** This also explains
mechanically why arm_TOD underperforms: it was built to suppress/boost cohorts by an ES/RTY/YM
ranking that assigns NQ's own worst cohort (EVENING) a *middling*, not low, score — the score is
aimed at the wrong target for NQ specifically.

## 1. Gate 0 — exposure neutrality (invalidation, checked first)

| arm | Σ\|T'\|/Σ\|T\| | contracts/day ratio | clamp-pinned % (arm / control) | VALID |
|---|---:|---:|---:|---|
| arm_ER | 1.0035 | 1.0230 | 2.17% / 1.98% | **YES** |
| arm_TOD | 0.9930 | 0.9598 | 1.86% / 1.98% | **YES** |

Both arms are inside the ±5% band on both measures — neither is secretly an exposure/de-risking
change wearing a selectivity costume (the exact failure mode M1's red team diagnosed). This is a
real result: the mechanical exposure-neutrality machinery (§1 of the spec) works as designed.

## 2. Gate A — legacy triple

| arm | Sharpe (ctrl→arm) | ΔSharpe | CDaR (ctrl→arm) | ΔCDaR (+better) | top10 house | top10 own | gate_sharpe | gate_CDaR | gate_top10 | **AND** |
|---|---|---:|---|---:|---:|---:|---|---|---|---|
| arm_ER | 0.709→0.702 | −0.0069 | 27,162→27,541 | −379 | 101.2% | 101.2% | FAIL | FAIL | pass | **FAIL** |
| arm_TOD | 0.709→0.700 | −0.0089 | 27,162→25,300 | +1,862 | 86.2% | 88.2% | FAIL | pass | FAIL | **FAIL** |

arm_ER fails cleanly on both Sharpe and CDaR — no ambiguity. arm_TOD's CDaR genuinely improves
(the only one of the six gate-A cells that clears its bar for either arm) but Sharpe worsens and
top-10-day retention (86.2% house / 88.2% own — the two differ by 2 points here, not the 20 the
W18R1 red team found, but both reported per that lesson) misses the 95% bar by a wide margin.

## 3. Gate B — chronology

| arm | yearly sign agree | ≥4/5 | survives excising final 106 sessions | **PASS** |
|---|---:|---|---|---|
| arm_ER | 2/5 | FAIL | FAIL | **FAIL** |
| arm_TOD | 4/5 | pass | **FAIL** | **FAIL** |

Yearly table (ΔSharpe, arm − control):

| year | arm_ER | arm_TOD |
|---|---:|---:|
| 2022 | +0.019 | +0.001 |
| 2023 | −0.030 | +0.058 |
| 2024 | −0.018 | +0.130 |
| 2025 | −0.020 | **−0.149** |
| 2026 (106-day stub) | +0.006 | +0.037 |

arm_TOD clears the yearly-sign bar (4 of 5 years positive) but **fails the second half of gate B**:
with the final 106 sessions excised, the trimmed-sample Sharpe/CDaR AND-rule no longer holds. This
is not a contradiction — it is exactly what you'd expect if arm_TOD's CDaR advantage is
concentrated disproportionately in the stub (CDaR $38,582→$34,231 in the stub alone, a $4.4k
improvement against a ~$27k full-sample CDaR base) rather than spread evenly across the whole
window. **2025 is arm_TOD's one clearly bad year** (−0.149, an order of magnitude larger than any
other year's delta in either direction) — a single-year effect this large should raise the same
concern gate B exists to catch, even though the yearly count alone clears the bar.

## 4. Gate C — cross-instrument (arm_ER only; binding)

| instrument | role | ΔSharpe | ΔCDaR ratio | sign-agree both |
|---|---|---:|---:|---|
| NQ | KNOWN | −0.0069 | −0.0140 | — (excluded from count) |
| ES | NEW | −0.0218 | +0.0055 | FAIL |
| RTY | NEW | −0.0173 | −0.0155 | FAIL |
| YM | NEW | −0.0061 | −0.0123 | FAIL |

**0 of 3 new instruments sign-agree** (bar: 2 of 3). arm_ER's NQ result is independently
reconstructed here from the same code path as the main run and matches the main gate_A row to
machine precision (internal-consistency assertion in `run.py`, passed) — the cross-instrument
failure is not a rebuild artifact. arm_TOD's gate C is correctly non-binding (circularity declared
in advance, spec §3) but is included above via the mandatory cohort disclosure instead (headline).

## 5. ADDENDUM — D7-boundary split (separately preregistered per owner directive §5 S1, not a
gate, does not change §1-4's verdict)

| arm | window | n days | ΔSharpe | ΔCDaR (control→arm) |
|---|---|---:|---:|---|
| arm_ER | pre 2024-08-05 | 669 | +0.0007 | 16,312→16,455 |
| arm_ER | post 2024-08-05 | 470 | −0.0153 | 31,488→31,937 |
| arm_ER | pre 2026-01-02 | 1,033 | −0.0095 | 22,517→22,858 |
| arm_ER | 2026 stub | 106 | +0.0065 | 38,582→39,135 |
| arm_TOD | pre 2024-08-05 | 669 | **+0.0821** | 16,312→15,128 |
| arm_TOD | post 2024-08-05 | 470 | **−0.0976** | 31,488→28,797 |
| arm_TOD | pre 2026-01-02 | 1,033 | −0.0087 | 22,517→21,376 |
| arm_TOD | 2026 stub | 106 | +0.0368 | 38,582→34,231 |

**arm_TOD's verdict is boundary-dependent, and per R5 that flip IS the finding, not the pooled
statistic.** Split at the (weakly-identified, candidate-only) D7 boundary of 2024-08-05: arm_TOD
looks like a genuine improvement pre-boundary (ΔSharpe +0.082, CDaR also better) and a clear
deterioration post-boundary (ΔSharpe −0.098). Both halves show CDaR moving in arm_TOD's favor, so
the CDaR direction is at least consistent across the split even though Sharpe is not.

**Required low-power caveat, stated per R5's pre-registration requirement before this table was
read**: D7 established that the incumbent (Solar leg) is itself degraded in the 2026 stub (Sharpe
−0.387 vs a full-dev mean well above zero). arm_TOD's stub-period "improvement" (ΔSharpe +0.037,
CDaR $4.4k better) is measured **against that degraded reference**, so it is genuinely ambiguous
whether arm_TOD is protective in a way that would hold up against a healthy incumbent, or whether
it simply trades less badly than an already-broken control during a period where almost anything
would look relatively better. This run cannot distinguish those two explanations and does not
attempt to; a successor test that conditions on the incumbent's own health, not just calendar time,
would be required to.

Calendar-year splits are the `yearly.csv` table in §3 above (2024 alone: arm_TOD +0.130, comfortably
inside the pre-boundary window; 2025 alone: −0.149, the single largest-magnitude year for either
arm in either direction, sitting entirely in the post-boundary window). The D7-boundary split and
the calendar-year split tell the same story from two different angles.

## 6. Interpretive disclosures (frozen spec did not fully pin these down; stated explicitly, not
silently decided)

1. **arm_TOD's score is built once from the full 2022-2026 ES/RTY/YM window**, not causally
   re-estimated bar-by-bar — a structural-property claim, not an adaptive signal. The
   exposure-neutrality transform applied on top of it (s̄_causal, k(d)) IS fully causal. If arm_TOD
   is ever revisited, a causal/expanding version of the cohort ranking is the natural next step.
2. **Rank-normalisation of the 3 cohort scores** uses `(rank−0.5)/3` → {1/6, 3/6, 5/6}; not pinned
   down by the frozen spec text.
3. **First-session / first-150-bar cold starts**: `s̄_causal := s_t` for the very first session
   (g_raw=1 trivially); ER150 uses a shortened window for the first ~150 bars of the whole dev
   series. Affects a negligible fraction of bars (<0.03%), disclosed for completeness.
4. **top10 "arm's own dates" retention** = arm's P&L summed over arm's own top-10 best days,
   divided by control's P&L summed over that same date set (the W18R1 red team's requested
   disclosure; formula choice stated since the frozen spec names the disclosure but not its exact
   formula).

## Verdict (frozen rule, unchanged by the addendum)

```
arm_ER:  gate_0 PASS, gate_A FAIL, gate_B FAIL, gate_C FAIL (0/3)  -> CONFIRMED-NOT-BENEFICIAL
arm_TOD: gate_0 PASS, gate_A FAIL, gate_B FAIL, gate_C non-binding -> CONFIRMED-NOT-BENEFICIAL
```

No adoption this wave. Alpha budget: 2 of 2 consumed (arm_ER, arm_TOD), per spec header.

## What this run actually establishes, for the successor (S2 / Priority 4)

1. **arm_ER (ER150 selectivity) is closed** — fails cleanly, no boundary nuance rescues it, and the
   cross-instrument replication actively contradicts it (0/3, wrong sign on the KNOWN cell too on
   Sharpe). Do not re-test ER150 as a standalone selectivity score without a genuinely different
   construction.
2. **D4's NQ time-of-day cohort structure (EVENING worst) does not transfer to ES/RTY/YM (where
   RTH is worst).** Any future SelTime construction (S2) must not assume NQ's own descriptive
   cohort split generalises across instruments, and — more importantly for S2's within-NQ design —
   this is a data point that D4's finding could still be a genuine NQ-specific structural property
   (not necessarily wrong, just not corroborated cross-instrument the way this run hoped). S2
   should treat D4's NQ cohort split as an NQ-native candidate, not something requiring
   cross-instrument confirmation to use.
3. **arm_TOD's boundary-dependent result is a genuine, if inconclusive, finding**, not noise to be
   discarded: something about the incumbent's relationship to time-of-day P&L structure changed
   around mid-2024, in the same direction D7's market-variable panel separately detected a
   structural shift (BIC-preferred STEP, weakly-identified date). Whether that is causally the same
   phenomenon is not established here and is flagged as an open question for S2, not answered by
   it.
