# U6B — Product-A scale-RATE conditioned on state quality: NOT PROMOTED

Persisted here by the orchestrating session from the subagent's returned text — its Write tool
blocked direct creation of this file. **The closest-to-promising result found in this campaign's
diagnostic history** — real, correctly-signed, right-tail-safe by design — but the effect is
simply too small.

## Correctness gate: PASS, plus a stronger check than the standard net-dollar gate

CONTROL (rate limiter disabled) reproduces the certified canonical Product-A net exactly
($177,924.40). Additionally: CONTROL's bar-by-bar position array is **identical, bar-for-bar, to
`u0_state_table.parquet`'s own `target_exposure_A` column** across all 540,232 bars.

## Construction

Preregistered quality composite (single, no black-box): at any bar where the incumbent's own
C4-gated target constitutes a scale-up (fresh ENTRY or SCALE_IN with `|tgt|>|p|`), quality="high"
if `htf_agree_code==1` OR `vote_dispersion_aligned >= VOTE_THRESH` (=6.0, the top-tercile cutoff
computed once, non-circularly, from the canonical ENTRY+SCALE_IN population, n=11,620, held
fixed across both grid cells and the extension); else "low". Base rate: 29.6% of canonical
scale-up bars read quality="low". Mechanism: quality="low" scale-up bars cap the step at
`max(1, floor(f·|gap|))` contracts instead of jumping straight to target. The `max(1,…)` floor is
a disclosed, necessary deviation — without it, single-contract low-quality scale-ups (the
majority of Product-A moves) would get a step of 0, silently turning the rate limiter into a
permanent block and reintroducing the right-tail failure mode U6 already closed. De-risking,
high-quality, and non-scale-up bars are always 100% unmodified.

## Headline numbers (canonical window)

| | CONTROL | F0.5 | F0.7 |
|---|---:|---:|---:|
| Net | $177,924.40 | $178,213.70 (+$289.30, +0.16%) | $178,531.30 (+$606.90, +0.34%) |
| Sharpe | 1.1770 | 1.1808 (+0.32%) | 1.1823 (+0.45%) |
| Sortino | 2.3371 | 2.3565 (+0.83%) | 2.3533 (+0.69%) |
| Calmar | 2.2896 | 2.2615 (−1.23%) | 2.3207 (+1.36%) |
| maxDD_eod | $17,192.9 | $17,434.8 (worse, +1.4%) | $17,020.8 (better, −1.0%) |
| CDaR95 | $14,323.1 | $14,284.4 (better) | $14,254.0 (better) |
| worst_month | −$7,495.5 | −$8,060.0 (worse, +7.5%) | −$7,821.0 (worse, +4.3%) |
| pos_day_pct | 44.16% | 44.07% | 44.25% |

**2022-2025-only delta (R2V1/R2B/U4B "wash" test, <1% of control's 2022-2025 net =
$167,570.20 → wash threshold $1,675.70):** F0.5 = +$843.20 (0.503%), F0.7 = +$970.10 (0.579%).
**Both fall under the 1% wash threshold** — the preregistered falsification condition.

Chronology note (genuinely different signature than every prior entry-timing family in this
campaign): unlike R2V1/R2B (100% of headline was a 2026-stub artifact), the 2026 Jan-May portion
is *negative* here for both candidates while 2022-2025 carries all the (tiny) positive edge —
this candidate is not a recency artifact, it just isn't large enough to matter. Full LOYO battery
shows a consistent, small, favorable direction on nearly every metric for both cells.

## Right-tail check (U6's own published top-20/bottom-20 canonical blocks)

**Top-20 all-time winners: ZERO dollars of impact from either grid cell** (window-summed delta =
$0.00). Mean fraction of each winning block's own scale-up bars reading quality="low" = 7.9% —
low exposure, and what little exists never binds. Clean confirmation the asymmetric, never-block
design works as intended. **Bottom-20 all-time losers: small negative (not protective) effect** —
mean fraction quality-low = 20.2% (2.6x winners' rate, consistent with U6's original finding),
net window delta −$34.50 for both cells (2 blocks damaged, 1 improved, 17/20 unchanged) — trivial
in dollars but directionally the wrong sign; pacing a losing entry's arrival marginally worsened
it (likely a slightly worse average fill-price path from splitting the entry).

## Mechanistic explanation for the negligible effect size

Of 12,085–12,603 scale-up bars per candidate, only 602 (F0.5) / 475 (F0.7) — under 5% — are
actually meaningfully paced. The rest of the "quality-low" scale-ups hit the mandatory
`max(1,·)` floor (85.6%/88.3%) because the gap is already just 1 contract — Product A's
scale-ups are dominated by single-contract increments, which the anti-block-floor safeguard
(required to avoid the rule silently becoming a filter) makes immune to pacing by construction.
Turnover/cost: total contracts traded fell slightly while fill-count rose (more/smaller
transactions); net effect on commission was a small saving, not a drag — costs are not what
kills this candidate.

## Verdict: NOT PROMOTED

Both grid cells trigger the preregistered falsification condition (2022-2025-only delta <1% of
control net). Not an ambiguous "genuinely promising on all axes" result warranting adversarial
re-verification: maxDD_eod, worst_month, and Calmar get worse under F0.5, and even where every
metric improves (F0.7, LOYO slice) the magnitude is sub-1% almost everywhere. The mechanism is
real and correctly asymmetric by design (zero top-20 damage, confirming the safety property it
was built for), and chronologically genuinely different/better-behaved than every prior
entry-timing family in this campaign (edge concentrated in 2022-2025, not 2026) — but the effect
size U6's own EVI ranking already flagged as the smallest of the four wave-2 candidates
(ΔR²<0.003, rank-biserial ≤0.17) proves, on construction, simply too small to clear this
campaign's promotion bar. Both Product-A and Product-B baselines remain unchanged.
