# R2B — pullback→reclaim adaptive entry — formal verdict

**VERDICT: NOT PROMOTED.** Candidate frozen at K=6 bars, no re-tuning. Incumbent
(`SolarWaveOneContractNQ_v5`/`MNQ_v5`) unchanged throughout.

## Audit of prior evidence

`runs/R2_ENTRY_TIMING/spec.yaml` PLANNED a pullback/reclaim diagnostic but
`runs/R2_ENTRY_TIMING/src/diagnose.py` never implemented it — only score-persistence (R2-A) was
built; R2's actual construction (confirm_bars, a FIXED delay regardless of price path) is a
materially different mechanism. Confirmed genuinely untested; R2B is a new hypothesis, not a
rerun.

## Diagnostic: a real, monotonic, price-path effect

Pullback magnitude (max adverse excursion within 6 bars, in ATR units) is strongly, monotonically
associated with worse outcome: no-pullback entries mean +$1,001.53 (61% win rate) down to
1.0+-ATR-pullback entries mean -$286.48 (34% win rate); Spearman -0.32. Given a pullback occurred,
reclaiming within the window matters enormously: reclaimed mean +$453.96 (47% win) vs
not-reclaimed mean -$671.37 (24% win). Right-tail pre-check: only 3/20 top winners show literally
zero pullback (confirming a no-pullback fallback is mandatory, not optional) — 5/20 show a
pullback that does NOT reclaim within 6 bars, meaning a hard-cancel-on-no-reclaim design would
have damaged the right tail; the constructed candidate therefore uses a bounded-delay fallback
(commit at bar K regardless) rather than cancellation.

## Construction, and a caught-and-fixed look-ahead bug

First implementation computed the reclaim decision from a bar's own close and applied it to the
SAME bar's position (filled within that bar's own OHLC) — an unlagged look-ahead, exactly the same
error class caught in `SA0_SYSTEM_STRUCTURE`'s sec9 B-MOM raw-standalone test. It produced an
obviously-too-good Sharpe 5.69 / net $1.39M, which exposed the bug rather than being a real
finding. Fixed with the same pend→p one-bar lag every other decision-layer function in this
codebase uses (`build_pos_seq`, `one_contract_decisions`). Corrected result: NQ net $325,299.12
(+7.7%), Sharpe 1.252 (+12.4%), maxDD $53,691 (better than control's $59,717), CDaR95 $39,791
(better), 3,638 trades (vs 3,868), MNQ net $31,070 (+8.7%), Sharpe 1.196 (+13.6%). Top-20
same-span retention 93.6%.

## Chronology — the SAME disqualifying pattern found in R2V1

| year | net delta | Sharpe (ctrl/cand) |
|---|---:|---|
| 2022 | +$237.84 | 1.901 / 1.958 |
| 2023 | +$4,853.24 | 0.699 / 0.853 |
| 2024 | -$7,712.80 | 1.304 / 1.184 |
| 2025 | -$1,929.20 | 1.144 / 1.189 |
| 2026 stub (106 sessions) | **+$27,934.12** | 0.053 / 0.937 |

**2022-2025-only: net delta = -$4,550.92 (a wash, slightly negative — NOT an improvement.)** The
full-history headline (+$23,383.20) is driven ENTIRELY by the 2026 stub. **LOYO-2026 confirms
exactly**: removing 2026 leaves delta -$4,550.92, matching the 2022-2025-only figure precisely.
Rolling-window deltas are unstable (54.8%/54.8%/50.6% of 60/120/252-session windows positive; min
rolling-60 delta -$14,738). Block bootstrap: P(delta net>0)=78.1%, but this pools the whole
5-year sample including the stub-concentrated tail, so it does not independently rescue the
finding (same caveat R2V1 applied to its own 82.2% figure). 2-tick cost stress shows the identical
split: 2022-2025 stress delta ≈ -$3,521, 2026-stub stress delta = +$28,104.

## The cross-mechanism finding this run adds to the record

**Two structurally different entry-timing mechanisms — R2's fixed 2-bar delay (regardless of
price path) and R2B's adaptive price-path reclaim-gating — both independently show the identical
"no edge in 2022-2025, entire headline from the 2026 stub" signature.** This was not obvious in
advance: R2B is a genuinely different construction (variable delay, price-conditioned, with a
no-pullback fast-path) built specifically to be conceptually distinct from R2's closed axis. Its
convergence on the same 2026-stub-dependency pattern is stronger evidence than either result alone
that SOMETHING about entry-timing mechanisms as a class interacts favorably with the already-
flagged-anomalous 2026 regime (`CURRENT_TRUTH.md` Wave-19), not that either specific mechanism
happens to be lucky. This does not identify the causal reason (no regime story is invented here,
per directive sec42), but it is a genuine addition to the record for any future entry-timing idea:
expect this same pattern until 2026 data accumulates enough to test out-of-stub, or until a
mechanistic explanation is independently verified.

## Disposition

**NOT PROMOTED.** `v5` incumbents unchanged, not re-tuned. R2B's construction is archived as
rejected research evidence (no NinjaScript object built — chronology already disqualifies before
that budget would be spent, per directive sec47's ordering rule). No MNQ-specific further
breakdown or NT8 validation performed (correctly withheld). Campaign continues automatically to
R4 per directive priority order.

**What would change this verdict**: the same standard R2V1 set — additional out-of-stub data
showing the edge persists, or an independently-verified (not post-hoc) causal explanation for why
2026 specifically favors delayed/reclaim-gated entries.
