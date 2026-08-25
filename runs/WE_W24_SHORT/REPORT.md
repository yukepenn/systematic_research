# WE_W24 — SHORT ENGINES · REPORT

Five short designs built from the short side's own opportunity (not mirrored). **Falsifier
FIRED: none adopted.**

| short engine | trades | net | wk mean | % pos | worst | Sharpe | combined Sharpe |
|---|---|---|---|---|---|---|---|
| X1 vol-expansion r≥1.5 | 975 | $50,392 | $296 | 42.9 % | −$13,432 | 0.088 | 0.251 |
| **X0 plain mirror (W23)** | 3,019 | $53,551 | $265 | 45.5 % | −$8,269 | 0.067 | **0.248 (63.4 % weeks)** |
| X1 vol-expansion r≥1.2 | 1,553 | $7,679 | $41 | 38.6 % | −$10,161 | 0.012 | 0.231 |
| X3 fast exit 30 / 60 bars | 7,782 / 4,439 | −$32k / −$32k | −$160 / −$158 | 45.5 / 44.1 % | −$12k / −$14k | −0.037 / −0.032 | 0.212 / 0.196 |
| X2 breakdown of prior low | 2,631 | −$67,759 | −$351 | 32.6 % | −$22,607 | −0.086 | 0.207 |
| **X5 drift-aware (control)** | 1,021 | −$30,810 | −$400 | 35.1 % | −$6,766 | **−0.103** | 0.228 |

## The surprise: "don't fight the drift" makes shorts WORSE

X5 — short only while the 50-session HTF tilt is negative — was included as the control and is
the **worst engine in the wave** (−0.103, the plain mirror is +0.067). Restricting shorts to
established downtrends removes the fast, mean-reverting breaks that are the only short-side
production, and leaves the slow grinding declines that a trend engine handles badly. My own
design hypothesis is falsified by its own control.

Vol-expansion is the only idea with signal (0.088 at r≥1.5), and it is still too weak to adopt.

## Verdict, stated as the spec required
**On NQ in this regime the short side is a hit-rate diversifier, not a source of edge.** It
belongs in the final system sized as *insurance*, not as production.

## The objective-dependent exception (important)

Under the campaign's Sharpe-based adoption rule, nothing is adopted. Under the owner's stated
objective — **weekly consistency** — the plain-mirror three-sleeve version is the right pick:

| | Sharpe | wk mean | **% positive weeks** | worst |
|---|---|---|---|---|
| E5halt + S1 (reference) | **0.259** | $2,508 | 59.5 % | **−$21,514** |
| + plain mirror short | 0.248 | $2,769 | **63.4 %** | −$24,667 |

+3.9 pp positive weeks and +$261/week, for −0.011 Sharpe and −$3,153 of tail. Both objects are
kept; the choice is an objective choice, not an evidence question.
