# U1 — session-phase heterogeneity of the state→economics mapping

**Disposition: CLOSED — diagnostic complete, no candidate constructed.** Not a re-run of R3/S2's
closed "block 02:00-08:00 ET" question — this tests whether the *mapping* from state (M/M_A_raw,
vol) to forward economics changes by session phase (interaction/heterogeneity), never a blanket
eligibility filter. Canonical window (`is_health_only_bar==False`) is primary throughout; the
June-July-2026 extension is reported separately, never blended. (Persisted here by the
orchestrating session from the subagent's returned text — its Write tool blocked direct creation
of this file.)

## Test 1 — TIME × action-type (Product B: ENTRY/HOLD/REVERSAL)

ENTRY: ETH mean **$224.93** (n=823) vs RTH mean **$116.07** (n=1,067) — ETH ~1.9x RTH. HOLD
forward-5-bar continuation value: **opposite direction** — RTH **$11.62**/5-bar (n=100,313) vs
ETH **$4.81** (n=92,410). REVERSAL (n=92, 84 RTH/8 ETH) too small on the ETH side to interpret.

**R3 cross-check**: `ETH_EUROPE` (03:00-07:57 ET) is U0's closest analog to R3's closed
EUROPE_PREUS window. This run independently reproduces R3's finding via a completely different
method — ENTRY quality there is net positive ($129.73 mean, n=303), while its HOLD continuation
value is the weakest of all 7 phases ($0.612/5-bar).

## Test 2 — Interaction OLS (`np.linalg.lstsq`, no black box)

(2a) `net_pnl ~ M_abs + vol_tercile_code + is_rth + M_abs:is_rth` (B ENTRY, n=1,890): interaction
coef **-286.42** (se=169.07, t=-1.69), implied M_abs slope $371.88/unit in ETH vs $85.46/unit in
RTH; R²=0.00437 (ΔR²=+0.00152 vs no-interaction baseline).

(2b) categorical session_phase interaction (baseline=ETH_ASIA): `M_abs:phase[RTH_MID]`=-935.14
(t=**-2.66**), `M_abs:phase[RTH_OPEN]`=-797.14 (t=**-2.22**) — the strongest statistical signal
in the whole run; R²=0.00775 (ΔR²=+0.00475).

## Test 3 — Residualized (M-strength × vol tercile) bucket, RTH vs ETH

Pooled: RTH residual -$74.29 vs ETH +$96.32 (gap -$170.61). 3/9 buckets (all "mid" M-strength)
are ETH-empty — a genuine discreteness artifact (Product-B's entry-M is a near-discrete
Tp-integer ladder; the "mid" tercile isolates M_abs=4.2472, never realized outside RTH in this
window) — flagged unreliable, excluded. Of 6 buckets with n≥15 both sides: **5/6 favor ETH**,
1/6 (strong_mid) favors RTH.

## Test 4 — Right-tail check (Product B)

Top-20 all-time winning blocks: **13/20 (65%) ETH** vs 41.8% base rate (1.56x; ETH_ASIA alone
2.31x). Bottom-20 losers ≈ base rate. **ETH is tail-rich, not tail-poor** — any RTH-favoring
reading of Tests 1-3 argues for treating ETH conviction as a stronger positive signal, never for
suppressing ETH.

## Test 5 — Chronology

ENTRY (ETH>RTH): positive in **4/5 canonical years**, and the extension strongly confirms it
(ETH $1,553.80 vs RTH -$543.01). HOLD (RTH>ETH): positive in only **3/5 canonical years**, and
the extension is **essentially flat** (+$0.49 gap) — this effect does not clearly replicate into
the most recent regime.

## Test 6 — Product A lightweight (ENTRY, SCALE_IN)

ENTRY: RTH $52.01 vs ETH $46.20 (n=779/2,704) — only a 13% gap, opposite-signed/weak vs Product
B's ~94% ETH premium; OLS interaction t=-1.19, R²=0.00064; residualized buckets mixed-sign.
SCALE_IN forward-5-bar continuation: RTH **$11.20** vs ETH **$1.10** (n=5,557/2,580, ~10x) —
**same direction as Product B's HOLD finding**, the strongest cross-product corroboration in
this run. Right-tail: top-20 Product-A trips 18/20 (90%) ETH vs 77.6% base rate (1.16x) — same
"tail-rich" pattern, weaker magnitude.

## Per-relationship verdicts

| # | Relationship | Verdict | Effect size |
|---|---|---|---|
| 1 | B ENTRY, ETH vs RTH | **H1, moderate confidence** | ETH +$108.86/entry (~1.9x), 4/5 yrs + extension agree |
| 2 | B HOLD continuation, RTH vs ETH | **H1, LOW confidence — not chronologically robust** | RTH +$6.81/5-bar pooled, only 3/5 yrs same sign, flat in extension |
| 3 | M_abs:is_rth interaction (B ENTRY) | **Weak H1, not independent** | coef -286.42, t=-1.69 — restates #1 |
| 4 | M_abs:session_phase interaction (B ENTRY) | **H1, moderate confidence — strongest signal in run** | RTH_MID t=-2.66, RTH_OPEN t=-2.22, ΔR²=+0.00475 |
| 5 | Residualized bucket, RTH vs ETH (B ENTRY) | **H1, moderate confidence** | 5/6 reliable buckets favor ETH |
| 6 | A ENTRY, RTH vs ETH | **H0 — no material session-conditioning** | RTH +$5.81 (~13%, opposite sign from B), mixed-sign buckets |
| 7 | A SCALE_IN continuation, RTH vs ETH | **H1, moderate-to-good confidence — cross-product corroboration** | RTH +$10.10/5-bar (~10x), same direction as #2 |

**Overall pattern:** entry-quality heterogeneity (ETH favors Product B's entries) is real-but-
moderate and does **not** generalize to Product A (H0). The **continuation/hold-value
heterogeneity (RTH>ETH while holding/scaling) DOES generalize across both products** (#2 and #7
agree in sign) — this cross-product agreement is more persuasive than either single-product
result, even though #2 alone looked chronologically shaky.

## NOT YET TESTED / NOT AUTHORIZED FOR CONSTRUCTION THIS RUN

If a future, separately preregistered U3-adjacent family wanted to act on relationships #2/#7,
the smallest defensible construction would be: whatever single global hold/exposure-layer
parameter that future family defines (e.g. a giveback-conditioned trim, hold-duration cap, or
risk-scaling factor) keeps one campaign-wide value everywhere, plus one small delta that applies
only while a position is being *held* (never entered) during ETH hours (`is_rth==False`). This is
not an entry filter — no ENTRY/REVERSAL bar is touched, so it does not revisit R3/S2's closed
ground — and it is a continuous small delta, not a binary block. Directly extends what R3 already
left open (a HOLD/EXPOSURE-layer mechanism targeting the bar-level bleed, "not built here") with
independent cross-product corroboration via a different method. Any future family building this
would still need to (a) define the base parameter (U3's job), (b) show it clears a bar at least
as high as R1's CONFIRMED-NOT-BENEFICIAL closure for a different state variable (giveback), and
(c) pass the full R2V1-style promotion gate. **Not evaluated, not parameterized, not built here.**
