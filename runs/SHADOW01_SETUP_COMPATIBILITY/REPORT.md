# SHADOW01 — raw-opportunity / shadow-setup serial-dependence diagnostic

**Disposition: CLOSED — null not practically rejected.** A real, chronologically-stable,
block-bootstrap-significant serial-dependence signal was found, but its economic magnitude
(ΔR²≈0.0002-0.0019) is far too small to be actionable — an order of magnitude below even R4/R5's
already-modest, non-hard-filter-safe findings (ΔR²≈0.009-0.012). Per the addendum's own stated
closure criterion ("if the null cannot be rejected economically and robustly: CLOSE SHADOW01"),
this closes cleanly. No streak-filter or any other construction was attempted (explicitly
forbidden per addendum B7 without a preceding diagnostic establishing a broad, stable, causal
relationship — this diagnostic does not establish one).

## Correctness gate: PASS

The shadow position path (Product-B's own `build_pos_seq` hysteresis state machine, called
verbatim with `entry_blocked` forced to all-False and `forced_flat_c4`/session-close unchanged)
is byte-for-byte identical to the real certified incumbent path for the first 449 bars (up to
the first bar `entry_blocked_c4` is ever True) — proving `entry_blocked_c4` is the only
behavioral difference introduced. Only 8 of 519,714 bars (0.00%) differ overall between shadow
and real paths, consistent with C4's own already-established small footprint (SA0: C4 mainly
governs *exits*, not entries).

## Opportunity-event construction

1,981 shadow events on the canonical window (2022-01-03..2026-05-29), essentially matching SA0's
own certified 1,978 real position-blocks (the ~3-event difference is exactly the handful of
entries C4 would have blocked). **99.8% of shadow events were also executed by the real
incumbent** — confirming C4's entry-selectivity effect on *which* opportunities occur is small,
consistent with prior findings. Side split: 1,061 short / 920 long.

## Serial-dependence test (addendum B3-B4)

10 preregistered recent-shadow-state features (10-event rolling lookback), tested against
`V_next` = the immediately following shadow event's own net_pnl, residualized against
(|M| tercile × vol tercile) exactly as R4/R5/U5 did:

| feature | raw ρ | residualized ρ | ΔR² | n |
|---|---:|---:|---:|---:|
| last_outcome_sign | -0.0355 | -0.0334 | 0.00010 | 1,971 |
| recent_wl_last3 | -0.0291 | -0.0273 | 0.00042 | 1,971 |
| rolling_expectancy_10 | -0.0642 | -0.0689 | 0.00135 | 1,971 |
| rolling_median_10 | -0.0126 | -0.0159 | 0.00106 | 1,971 |
| **rolling_mfe_10** | **-0.1010** | **-0.1000** | 0.00020 | 1,971 |
| rolling_mae_10 | 0.0503 | 0.0445 | 0.00166 | 1,971 |
| loss_severity_10 | 0.0603 | 0.0548 | 0.00003 | 1,971 |
| follow_through_speed_10 | -0.0578 | -0.0584 | 0.00190 | 1,971 |
| loss_rate_10 | 0.0398 | 0.0426 | 0.00191 | 1,971 |
| right_tail_rate_10 | -0.0639 | -0.0649 | 0.00056 | 1,971 |

Baseline R² (M_abs + vol_tercile alone) = 0.00009 — the whole system barely explains individual
shadow-event outcomes from state alone, so even the best ΔR² above (0.0019) is tiny in both
relative and absolute terms.

## Strongest feature: `rolling_mfe_10` (mean MFE of the last 10 shadow events)

The single strongest residualized relationship (ρ=-0.100): elevated recent shadow-event MFE
predicts a *weaker* next event, a mild mean-reversion-in-setup-quality pattern.

- **Redundancy check (addendum B5)**: NOT redundant with organization — Spearman vs
  `trend_efficiency_20` = 0.016, vs `range_efficiency_20` = 0.034 (both far below the 0.5
  redundancy threshold). Adding it on top of M+vol+organization improves R² by only +0.00015
  (0.00192→0.00207) — a genuinely independent but vanishingly small increment.
- **Session split**: ETH ρ=-0.135 (n=929) vs RTH ρ=-0.063 (n=1,042) — the effect is roughly
  2x stronger in ETH, an interesting but, given the tiny base effect, still economically minor
  distinction.
- **Chronology**: same-signed in **5/5 canonical years** (2022 -0.078, 2023 -0.072, 2024 -0.140,
  2025 -0.061, 2026 -0.090) — genuinely stable.
- **Session-block bootstrap** (1,000 resamples, blocked by `sess_date_start` per addendum B2's
  clustering requirement): observed ρ=-0.100, 95% CI=[-0.148, -0.054], **excludes 0** — this is
  statistically real, not a fluke of treating 1,971 non-independent-in-time events as i.i.d.
- **Right-tail check**: top-20 shadow events' own prior `rolling_mfe_10` (mean 3,530) sits
  *below* bottom-20 losers' (mean 4,228), both above the population mean (2,023) — i.e. both
  tails follow elevated recent MFE, just to different degrees. This is the same
  overlapping-tails signature R5's `direction_x_volume` showed (real bulk direction, no clean
  tail separation) — not right-tail-*damaging* in the R1/R3/U3/U4B sense (it doesn't
  concentrate in winners specifically), but also not a clean discriminator.

## Verdict

**Statistically real, economically negligible.** The null of "setup outcomes have no useful
memory" is technically rejectable in a narrow statistical sense (bootstrap CI excludes 0,
5/5-year sign stability) for exactly one of ten preregistered features — but the effect size
(ΔR²≈0.0002 raw, ≈0.0015 incremental beyond organization/session) is roughly 5-10x smaller than
R4/R5's own already-modest, not-hard-filter-safe findings, which themselves were never
constructed into a trading rule. With n≈1,971 events, even a true effect this small will clear a
95% bootstrap CI — this is exactly the gap between statistical and economic significance the
addendum itself warns about (sec 50, distinguishing "recent PnL != future proof" and demanding
"meaningfully AND stably" different, not just detectably different).

**CLOSED per addendum B4's own stated criterion.** No streak-filter or other construction
attempted (forbidden per B7 absent a broad, stable, *economically* meaningful relationship, which
this is not). Interaction with U8's organization-transition feature (addendum B6) is moot — there
is no independent SHADOW01 signal large enough to be worth combining with anything. Product-B and
Product-A both unchanged; no translation attempted (addendum B8, moot given the closure).
