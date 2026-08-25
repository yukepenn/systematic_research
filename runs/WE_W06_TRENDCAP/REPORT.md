# WE_W06 — TREND CAPTURE · REPORT

Spec preregistered (hypotheses declared before phase 1 was read). All variants causal.

## PHASE 1 — the answer to "为什么抓不到趋势", quantified

**Available per session** (perfect-foresight single trade, 1,187 sessions):
mean **346.2 points = $6,925** at 1 NQ.

| sleeve | captured | capture ratio | trades/session | pts/session |
|---|---|---|---|---|
| S1 | 19,315 pts | **4.70 %** | 11.21 | 16.3 |
| S4.narrow6.gdl | 19,240 pts | **4.68 %** | 4.88 | 16.2 |
| S4.all13.h1300.gdl | 14,763 pts | 3.59 % | 2.24 | 12.4 |
| **HIM** (21 displayed weeks, gross) | ~9,030 pts | **~24.8 %** | ~16.7 | ~86 |

**He captures roughly 5× more of the available move than we do**, at ~3.4× our trade rate
(vs our best sleeve). Caveats: his figure is gross, display-selected (R34), and over his best
observed stretch; ours is net over 4.6 years. The order of magnitude survives all of that.

### Where our capture leaks (mutually exclusive, per session)

| | no trade | **wrong side** | late entry | early exit | **chop loss** |
|---|---|---|---|---|---|
| S1 | 0.8 % | **23.5 %** | 20.8 % | 20.1 % | **34.9 %** |
| S4.narrow6.gdl | 3.1 % | **33.0 %** | 24.5 % | 15.2 % | **24.1 %** |
| S4.all13.h1300.gdl | 4.9 % | 27.6 % | 29.4 % | 7.8 % | 30.3 % |

**~58 % of sessions fail for one of two reasons: we are on the wrong side, or we are on the
right side and get chopped.** Timing (late/early) is the smaller problem. When we do trade a
session well, we enter within ~16 bars of the move's start (S4n) and exit ~54 bars before its
end — i.e., **entry timing is近乎 fine; the exit leaves the tail of the move on the table, but
that is third-order compared with direction and chop.**

## PHASE 2 — all five declared hypotheses FAILED to improve risk-adjusted performance

Marginal vs BASE (S4.narrow6.gdl), dev Sharpe / $per-trade / worst week:

| hypothesis | Δ Sharpe | Δ $/trade | Δ worst week | verdict |
|---|---|---|---|---|
| H1 re-entry | **+0.000** | +0.0 | +0 | **INERT** — never fired; the hysteresis already prevents the one-bar flicker H1 was designed to exploit. Not "no effect": *untestable as specified*. |
| H2 pyramid @20 pts | +0.004 | **+47.6** ($104.5 — his level) | **−$23,065** | **LEVERAGE, NOT EDGE**: dollars and tail scale together, Sharpe flat. |
| H2 pyramid @40 pts | −0.001 | +37.8 | −$19,233 | same |
| H3 early-RTH flow entries | **−0.053** | −20.8 | −$6,009 | **REJECTED** |
| H4 hold longer (exit 0) | −0.012 | +1.9 | −$916 | rejected on dev |
| H4 hold longer (exit −1) | −0.033 | +23.3 | −$4,319 | rejected on dev — **but holdout Sharpe 1.216 (88.9 % weeks)**, a dev/holdout conflict. Holdout is on its 5th read; per campaign rules this is NOT chased. Flagged for the virgin read only. |
| H5 two-speed (fast+slow) | +0.000 | +14.5 | −$1,326 | Sharpe-neutral; the dollar gain is two sleeves' scale |

**Nothing here improves the edge.** H2's headline — per-trade expectancy reaching $104.5,
matching his $103 — is pure position scaling: the worst week degrades in the same proportion.
Recording this explicitly because "$/trade at his level" would be a tempting, false headline.

## The gap this run exposes in its own design

The two dominant leakage classes — **wrong side (23–33 %)** and **chop loss (24–35 %)** —
had **no declared hypothesis**. Every hypothesis I preregistered attacked timing/exits, which
phase 1 then showed to be the *smaller* problem. Correct response: do NOT invent
direction/chop hypotheses post-hoc against this same data. **W07 preregisters the direction
and chop problem as its explicit target**, which is also where the vendor question re-enters:
our free delta proxy bought +0.02–0.03 Sharpe; the official `Signal_Trend` / `Signal_Cum_Delta`
attack precisely the wrong-side class.

## Standing conclusion after six waves

We know exactly what is wrong with our system now, in one sentence:
**we are on the wrong side or chopped in ~58 % of sessions, and we harvest under 5 % of the
day's available move, while he harvests ~25 %.** More exits, more re-entries, more size and
more speed variants do not fix that — measured, not assumed. **Direction quality is the
binding problem**, and that is an information problem, not a wrapper problem.
