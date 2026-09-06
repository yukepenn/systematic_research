# G3_ZBMACRO_CLASSP_20260906 — EXPLORATORY Class-P pre-read for ZBMACRO01 (ledger G00078, family GENESIS3_DECISION)

**Verdict (mechanical, preregistered decision rule at k=2 LIVE_SCALE): `STACK-MEMBER` — clauses (a), (b), (c) all PASS (ledger PASS).**
**Evidence status: DISCOVERY_CONSUMED + EXPLORATORY** — a pre-read on the same consumed substrate; it licenses ONLY the next research stage (ZBMACRO01 engine construction: frozen rule restated, eval_battery full pass, adversarial skeptic, THEN fast-track consideration). **It is NOT a deploy decision, not forward evidence, and touches no baseline.**

**Question:** ZBMACRO01 cleared its falsifier (G00072, 10/10) but is small (~$2k/yr/ct, ~11 trades/yr). Before spending engine-construction + skeptic effort, is it a rational STACK MEMBER next to P1?

## Inputs (shas program-printed)

- **ZB leg:** `runs/G3_ZBMACRO_FALSIFIER_20260906/out/trades.csv` AS-IS, sha256 `245431500d42becbc6ed8c8f07c0696e9057346d3b52cad05d8976bb2d8e2273`, n=40 trades 2023-01-12..2026-06-05, PRIMARY cost arm (comm $4.36 + 1 tk/side, BASIS=MODELED ALL_IN), $ per 1 ZB ct, exit-day attributed.
- **P1 leg:** `runs/WE_W56_BREADTH/out/p1_daily.csv` AS-IS, sha256 `9bc2d7f7000653b4d15f82b9ac9bf76ac25ec4cdbdb008d382453ec082a75357`, 607 days 2022-07-05..2026-05-29. **DISCLOSED: Python-chain P1 figures are ~2.0% optimistic** (double-lagged ATR, `we_fastctx.py:81`); stated, not corrected.
- **Joint calendar (falsifier-G9-identical):** ZB substrate sessions inside the P1 span, both series zero-filled: **2022-12-27..2026-05-29, 878 sessions, 39/40 trades in overlap** (2026-06-05 outside the P1 span — excluded, disclosed). Identity clause: ρ_d **−0.0058**, ρ_w **+0.1004** reproduce the G00072-quoted −0.006/+0.100 at 3 dp. Seals asserted (all inputs < 2026-08-01; substrate ≤ 2026-07-31).
- **Scale bases (both printed):** LIVE_SCALE = P1 × 0.30 NQ-equivalent (deployed MnqPerNq=3) vs ZB × k; RESEARCH_FULL = P1 × 1.00 vs ZB × k; k ∈ {1, 2, 4}.
- **Code:** `src/run_classp.py` (executable preregistration; all ambiguity resolutions fixed in its header before results). Artifacts: `out/classp_table.csv` (all 6 cells), `out/joint_series.csv`, `out/gate_table.txt`, `out/run_log.txt`.

## Gate table (program-printed; full version in `out/gate_table.txt`)

| GATE | SPEC | OBSERVED | PASS/FAIL |
|---|---|---|---|
| C0_seal_identity | seals hold; joint calendar reproduces G00072-G9 (878 sess, 39/40, ρ −0.006/+0.100 @3dp) | 2022-12-27..2026-05-29, 878 sess, 39/40, ρ_d −0.0058 ρ_w +0.1004 | PASS |
| CP_a_marginal_sharpe ⛔ | k=2 LIVE_SCALE: marginal weekly-vol Sharpe (book − P1-alone) > 0 | 2.2796 − 2.1874 = **+0.0923** | **PASS** |
| CP_b_tail_ratios ⛔ | k=2 LIVE_SCALE: maxDD ratio ≤ 1.02 AND CDaR5 ratio ≤ 1.02 | maxDD **0.9588** ($6,573→$6,302); CDaR5 **0.9869** ($4,806→$4,743) | **PASS** |
| CP_c_no_harm ⛔ | k=2 LIVE_SCALE: losing-P1-week conditional ZB mean > −$50/wk | **+$45.94/wk** over 71 losing weeks | **PASS** |
| R_all_cells | all 6 basis×k cells + decile table + concentration + margin note printed | 6/6 cells; T2 3 rows; T3/T4 printed | PASS |
| R_probability_clause | any probability-style statement computed 2 ways, OR none quoted | none quoted | PASS |

⛔ = the three decision clauses. **All PASS → `STACK-MEMBER` (ledger G00078 PASS).**

## Key numbers (all DISCOVERY_CONSUMED + EXPLORATORY)

- **Stack table (178-week grid, Sharpe = mean/sd·√52; tails on daily $):**

| basis | k | S_p1 | S_book | ΔS | condL $/wk | worst wk p1→book | rMDD | rCDaR5 |
|---|---|---|---|---|---|---|---|---|
| LIVE_SCALE | 1 | 2.187 | 2.283 | +0.096 | +23.0 | −2,225→−2,225 | 0.783 | 0.847 |
| **LIVE_SCALE** | **2** | **2.187** | **2.280** | **+0.092** | **+45.9** | **−2,225→−3,700** | **0.959** | **0.987** |
| LIVE_SCALE | 4 | 2.187 | 2.123 | −0.064 | +91.9 | −2,225→−6,709 | 1.417 | 1.420 |
| RESEARCH_FULL | 1 | 2.187 | 2.228 | +0.041 | +23.0 | −7,418→−7,418 | 0.935 | 0.915 |
| RESEARCH_FULL | 2 | 2.187 | 2.258 | +0.071 | +45.9 | −7,418→−7,418 | 0.870 | 0.861 |
| RESEARCH_FULL | 4 | 2.187 | 2.289 | +0.102 | +91.9 | −7,418→−8,323 | 0.776 | 0.861 |

  At the decision cell (k=2 live) the book's maxDD and CDaR5 are *smaller* than P1-alone (diversification), and the marginal weekly-vol Sharpe is +0.092. **k=4 at live scale over-sizes the leg**: marginal Sharpe turns negative and the tails blow through (1.42×) — the k-grid brackets the sensible size from both ends.
- **No-harm detail:** 71 of 178 weeks have P1 < 0; ZB weekly mean over ALL of them is +$45.9 (k=2). Active-only honesty: only 13 losing-P1 weeks had a ZB trade; active-only mean +$125.5/wk at k=1. This is **no-harm, not hedging** — exactly the spec's framing.
- **P1 bottom-decile days (worst 88 of 878):** ZB active on 3 (chance ≈ 3.9): +$308.1, −$816.9, +$808.1 (k=1) — sum +$299. No tail-coincidence signal either way at this n.
- **Annual economics:** full ledger $1,978/yr/ct on 11.1 trades/yr → k=2 ≈ **$3,957/yr**; joint window (39 tr) $2,125/yr/ct. Small dollars, stated.
- **Concentration honesty:** top-3 trades = $4,706 of $7,107 net = **66%** (2023-10-12, 2023-06-13, 2023-09-01). Tail-carried (G00072 drop-k: +$91/ct at k=2, +$18 at k=5). ~11 trades/yr is a very small effective N.
- **Margin/capital (ASSUMED, flagged — no broker surface touched):** intraday-only object, day margin binds; at an ASSUMED ~$2,000/ct: k=2 ≈ 39% of the ~$10.2k live account tied up for 6h15m on ~11 days/yr; **k=4 is capital-implausible at current size.** Broker figure requires verification before any later stage quotes it.
- **No probability-style statement is quoted in this run** (CAP01 clause satisfied on its "none quoted" arm).
- eval_battery guard: maxDD/CDaR appear only as dollar path descriptives and book-vs-P1 ratios; no DD-normalized income; nothing thinned (a leg is added, never removed) → no thinning placebo owed.

## Caveats (binding)

1. **EXPLORATORY + DISCOVERY_CONSUMED, every table.** Same consumed substrate as the G00067 screen and G00072 falsifier; nothing here is forward evidence; ~2.0% P1-chain optimism disclosed.
2. **The marginal Sharpe (+0.09) is a point estimate on 39 overlapping trades with 66% of PnL in 3 trades.** No interval is claimed for it; the STACK-MEMBER bar was preregistered as sign + tail + no-harm clauses, not as a significance claim.
3. One ledger trade (2026-06-05) sits in the globally BURNED 2026-06→07 window and outside the joint calendar; the joint-window net ($7,267) exceeds the full-ledger net ($7,107) because that excluded trade was a −$161 loser — stated to prevent misreading.
4. The ZB day-margin figure is ASSUMED and flagged; the capital note is not quotable beyond this pre-read without a broker-verified number.
5. STACK-MEMBER licenses engine construction ONLY. **EXECUTABLE · PARITY-CERTIFIED · LIVE-ENABLED remain three separate, untouched statuses; nothing here changes any baseline or the live book.**

## Next step per decision rule

ZBMACRO01 engine construction: frozen rule restated, eval_battery full pass, adversarial skeptic, THEN fast-track consideration. No deploy, no promotion.