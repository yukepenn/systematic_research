# A1A2_ATR_AUDIT — RESULTS

Reused `SMV2AJ_ATR_BLEND_R2`'s frozen w=0.75 blend exactly as published — no re-simulation, no
refit. Self-check: the raw-target reconstruction's untitled Solar net ($119,008.90) correctly
differs from `curves.csv`'s `DUAL_CONTROL` ($138,280.00, the HTF-**tilted** leg) — documented, not
an error; A1/A2 use `curves.csv`'s own tilted columns for all portfolio-level analysis. Code:
`src/run.py`.

## A1 — drawdown complementarity: genuinely helps, modestly, almost everywhere it was asked to

| stress period | n | mean Δ (blend − control) | improved / total |
|---|---:|---:|---|
| worst 5% days | 56 | **+$64.07** | 31 / 50 (rest ~flat) |
| CDaR₀.₉₅ tail-episode days | 56 | +$47.35 | — |
| joint Solar+BMOM loss weeks | 50 | +$21.73/week | 26 / 50 |
| top-10 longest drawdown episodes | 10 | +$597.73 | 6 / 10 |
| full sample | 1,139 days | +$5.74/day ($6,535 total) | — |

ATR's blend is **directionally positive on every stress slice tested**, including the specific
joint Solar+BMOM loss weeks the program's own unifying diagnosis names as the hardest case — but
the improvement is modest (roughly matching the full-sample average, not concentrated), and the
top-10-longest-episodes split (6 of 10 improved, but a positive mean driven by a few large
improvements) shows it is not uniformly protective even there. This is consistent with, not a
contradiction of, the closed CDaR-prong failure (P(ΔCDaR>0)=0.753): a real but not statistically
overwhelming tail benefit.

## A2 — the pre-registered mechanism test FAILS: ATR's benefit does not concentrate where
intrabar noise exceeds close-to-close noise

| tercile (by session R_dev = ATR/σ460 − 1) | mean Δ | P(mean>0), bootstrap |
|---|---:|---:|
| LOW_R_DEV | +$3.87 | 0.701 |
| MID_R_DEV | **+$10.04** | **0.971** |
| HIGH_R_DEV | +$3.31 | 0.665 |

**The falsification pre-registered in spec.yaml §2 fires: HIGH_R_DEV is NOT the largest tercile —
it is tied for smallest with LOW_R_DEV, and MID_R_DEV (not HIGH) carries essentially the entire
statistically-supported benefit** (P>0=0.971 vs 0.70/0.66 for the other two). **A3 does not run
this wave, per the pre-registered gate.**

This is a real, informative negative result, not a non-finding: ATR's advantage is not doing what
its own mechanistic story claims (correcting for understated intrabar noise). Per directive §7 A2's
own framing, this makes the NQ-only headline result **more suspicious, not less** — whatever ATR is
capturing, it is not preferentially active in the sessions where its stated justification predicts
it should be.

## Disposition

**ATR 75/25 remains CLOSED as a Sharpe/CDaR-improving weight (unchanged).** A1 shows a genuine,
modest, broadly-distributed tail benefit that does not, on its own, overturn that closure (it is
consistent with the already-measured 0.753 CDaR-prong probability, not evidence of something
stronger hiding underneath). A2 falsifies the specific mechanism the directive asked to test, so
**no conditional ATR construction (A3) is proposed this wave.** The ATR axis is closed for this
campaign at both the direct-weight level (prior waves) and the reframed drawdown/mechanism level
(this run) — a future ATR idea needs a genuinely different construction, per the standing
`W18R2_M5_XINST` instruction, not another blend weight or another R_dev-conditioned variant of
this same one. No red team required (diagnostic + falsified mechanism, no promotion proposed).
