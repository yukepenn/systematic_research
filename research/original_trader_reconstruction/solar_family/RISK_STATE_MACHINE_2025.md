# RISK_STATE_MACHINE_2025 — the author's 2025 risk stack, layer by layer
(directive v3.0 §10, PHASE C4 — 2026-08-24. Evidence-synthesis; every layer keeps
its own identification status. Do NOT blend layers into one "loss limit".)

## Layer chronology (from PARAMETER_VERSION_TIMELINE + reports)

| First seen | Layer | Panel evidence | Identified behavior | Status |
|---|---|---|---|---|
| 2025-02-13 (0014) | **Session LossLimit (DSTM)** | `LossLimit 4000`, → `2500` by 2/18 | session-scoped loss cutoff in the DSTM branch; semantics tested in R1.3, INCONCLUSIVE at the then-base | Feb-2025 only; superseded |
| by Jul-2025 (★0062) | **Daily money pair D/M** | `☑ 4500? 2000?` → ★0077 `M…[E✔ D 4500 M 2000]` | E = enable; literal session-cum halts (M=+2000 profit / D=−4500 loss) **REJECTED for the dev/CAND2 build** (R5: over-suppresses −27.6%); partially explanatory for hp-machine weeks (+39.5%→+13.5%) but erratic | semantics OPEN; NOT literal cum-halt on the flagship |
| by Jul-2025 (★0062) | **Stop group St…** | `[In 65 / Tr 30 / I 65 / M 20]` → 11/7 +46,36 → 11/14 row3 65→75 → 1/17 46/36→46/30 | see per-field table below | partially identified |
| always | **Session-equity gate (D-gate)** | not a panel group (hard-coded) | CAND2 wrapper: prior-red evening block (C≈700, 360 min), armed X≈1600 PM / X2≈2500 AM, K=3 same-side consec losses, ~20 trade/session cap, 3-bar cooldown | STRUCTURE CONFIRMED (42/42 labels); constants interval-identified |
| always | **Exit-on-session-close** | checkbox + EV-036 (16:59:30 ET flatten) | last-bar close realization (S0-certified) | CONFIRMED |

## St… stop-group per-field state (6 rows by 11/14: [65/30/75/20/46/36])

| Row | Label initial | Value(s) | Leading semantics | Evidence | Status |
|---|---|---|---|---|---|
| 1 | In… | 65 | **Initial protective stop, 65 pts, intrabar, gap-through fills** | −1,300.00 exact caps in 8/28 weekly reports incl. Dec/Jan; R2 G1 reproduces | **CONFIRMED** |
| 2 | Tr… | 30 | trailing distance 30 pts, **NOT always-on** (falsified); armed-after-activation shape (G3) viable | R2 | partial |
| 3 | I… | 65 → **75** (11/14) | NOT the initial stop (R5: −1300 exacts persist after the change; −1,500.00 exact appears 1/4-week SHORT side) → second stop tier; **directional (short-side?) stop hypothesis OPEN** | R5 LL anatomy: era-B LL>1300 rows are mostly short-side (−1410/−1490/−1500/−1385) while longs cap at −1300 | OPEN |
| 4 | M… | 20 | trailing ACTIVATION threshold (+20 pts favorable) | R2 G3 viable | plausible |
| 5 | (new 11/7) | 46 | unknown; unchanged through 1/17 | — | UNKNOWN |
| 6 | (new 11/7) | 36 → 30 (1/17) | unknown | — | UNKNOWN |

## What the R5 largest-loss anatomy adds (new, 2026-08-24)
- Exact −1,300.00 rows appear in BOTH eras and BOTH sides → In=65 persists all year.
- Losses beyond −1,300 (−1,360…−1,540) cluster 3-12 pts past the cap → consistent
  with 1-min gap-through fills, EXCEPT the exact −1,500.00 (75.00 pts, 1/4/2026
  short) which is a fill AT a 75-pt level → row-3=75 is live for SOME trades.
- Discriminating experiment (queued): rerun era-B weeks with long-stop 65 /
  short-stop 75 vs both-65, score LL_long/LL_short columns per week.

## Interaction map (who can cut a trade / a session)
1. Per-position: In=65-pt initial stop (intrabar) → then trailing (30, armed ~+20).
2. Per-session (flagship, hard-coded): D-gate arming/blocking + ~20-trade cap +
   evening block after a red prior session.
3. Per-session (panel, enabled): D/M money pair — semantics NOT literal halts on
   the dev build; hypotheses left: (a) applies to a DIFFERENT strategy instance
   (hp machine), (b) units/scope differ (e.g. intraday floating, not realized cum),
   (c) enable-checkbox off on dev despite panel capture timing.
4. Account layer: none observed in 2025 SA slices (Qty 1 throughout; the one
   Quantity-3 experiment week W0206 excluded).
