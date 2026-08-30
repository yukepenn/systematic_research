> ⚠️ **FROZEN 2026-08-30, BEFORE the shadow's first row and before the paper book's first
> session.** Thresholds set in advance precisely so they cannot be chosen after seeing forward
> data. Amending any number below after 2026-08-30 18:00 ET requires a recorded owner decision
> stating what was known at the time.

# XM CORRELATION RULE — the book's live risk, preregistered

## The finding this rule exists for (measured 2026-08-30, consumed data 2022-W27..2026-W31)

The justification originally recorded for including XM — *"it diversifies P1's LOSSES"*
(W110: ρ|P1<0 = −0.165) — **has decayed and reversed**:

| window | ρ(P1,XM) weekly | XM mean on P1-losing weeks | XM>0 share there |
|---|---:|---:|---:|
| first half (≈2022-07→2024-07) | **−0.101** | **+$1,488** | 50% |
| second half | +0.182 | −$100 | 43% |
| last 52 weeks | +0.269 | −$689 | 36% |
| **last 26 weeks / 2026** | **+0.410** | **−$727** | **31%** |

This continues the deterioration the repo already flagged (`PROSPECTIVE_SHADOW.md`: hedge payoff
+$598 → −$1,243; P(XM<0 \| P1<0) 0.200 → 0.500). It is now **0.69** in 2026.

## What the book's case rests on NOW (restated honestly)

**Not** "XM hedges P1". The surviving case is: **two independently profitable streams whose
correlation, while rising, is still far below 1** — which still improves risk-adjusted income:

| | P1 alone | **P1+XM (M_11)** | XM alone |
|---|---:|---:|---:|
| full-sample fixed-DD $/wk | $1,395 | **$2,318** | $994 |
| 2026 fixed-DD $/wk | $1,722 | **$2,475** | $994 |

**The failure mode this creates:** if ρ keeps climbing, the book degenerates into ~2× leverage on
one factor while still being sized as if it were two.

## PREREGISTERED THRESHOLDS (evaluated on shadow/paper data only, from 2026-09-01)

Evaluated at each MONITORING_CALENDAR checkpoint, never ad hoc, on trailing-26-week windows of
the forward stream (a minimum of **26 completed forward weeks** must exist — no earlier read):

| # | condition | consequence |
|---|---|---|
| **W1 WATCH** | trailing-26wk ρ(P1,XM) ≥ **+0.50** | record it; no action; re-check next checkpoint |
| **W2 REVIEW** | trailing-26wk ρ ≥ **+0.65** *or* XM's mean P&L on P1-losing weeks ≤ **−$1,000** with n ≥ 8 such weeks | the book's fixed-DD advantage is re-measured on forward data; if it is no longer > P1 alone, the mapping goes back to the owner with a recommendation |
| **W3 DEMOTE** | trailing-26wk ρ ≥ **+0.80** | XM's marginal case is treated as REFUTED forward; recommend running P1 alone until a new joint case is made. **Recommendation only — never an automatic change to a live/paper deployment.** |
| **N1 null-guard** | any of the above computed on fewer than 26 forward weeks | **NOT EVALUABLE** — record and wait. Under-powered reads are the failure this file exists to prevent |

**Symmetric clause (so this is not a one-sided tripwire):** if trailing-26wk ρ falls back below
**+0.10** *and* XM's P1-losing-week mean returns above **+$500**, record HEDGE-RESTORED — the
original W110 mechanism is behaving again. Both directions get written down.

## What does NOT follow from this file

⛔ No change to tonight's deployment. Both legs are individually certified, individually
profitable, and the combination still measures better than P1 alone on consumed data. This file
sets the conditions under which that conclusion would be revisited on **forward** evidence, and
nothing else. `LIVE ENABLED = NO`.
