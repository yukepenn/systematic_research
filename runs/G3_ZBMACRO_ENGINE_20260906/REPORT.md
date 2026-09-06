# G3_ZBMACRO_ENGINE_20260906 — ZBMACRO01 engine construction + adversarial skeptic (ledger G00079, family GENESIS3_ENGINE)

**Verdict (mechanical, preregistered decision rule): `ZBMACRO01 ENGINE FROZEN-READY` — G_delay = PASS AND skeptic = SURVIVES → ledger PASS. FT0 is licensed: freeze rule + entry convention close(08:46) + k=2.**
**Evidence status: DISCOVERY_CONSUMED (every table)** — same substrate as the G00067 screen and G00072 falsifier; nothing here is forward evidence; no baseline is touched.

**The engine object (FT0 freeze candidate):** on GENESIS_H2_CALENDAR NFP_DAY/CPI_DAY sessions, if close(08:45)−close(08:30) < 0 (ZB points), SHORT k=2 ZB **filled at the close of the 08:46 bar** (one full minute of latency charged), exit at the 15:00 close. No overnight, no other conditioning. Cost BASIS=MODELED ALL_IN: PRIMARY $66.86/RT (comm $4.36 + 1 tk/side), STRESS $129.36/RT.

**Code:** `src/run_engine.py` (executable preregistration; every ambiguity resolution fixed in its header before results — paired-bootstrap seed 20260910, monotonicity operationalization, NaN-drop fallback, roll ASSUMED-PROXY, skeptic kill criteria). Artifacts: `out/delay_curve.csv`, `out/maemfe.csv`, `out/dossier.md`, `out/skeptic.md`, `out/gate_table.txt`, `out/run_log.txt`.

## Gate table (program-printed; full version in `out/gate_table.txt`)

| GATE | SPEC | OBSERVED | PASS/FAIL |
|---|---|---|---|
| E0_seal_identity | seals; trades.csv sha; 40-trade exact repro from substrate; joint identity (878/39, ρ 4dp) | substrate max sess 2026-07-31; sha `2454…8273` MATCH; dates/fwd/r1 EXACT<1e-9; joint OK ρ_d −0.0058 ρ_w +0.1004 | PASS |
| G_delay ⛔ | 08:46 net > 0 AND paired-block-bootstrap CI95 excludes 0 → PASS; else ≥60% retention & monotone → FAST-EXEC; else KILLED | net46 **+$186.3/ct**, profit CI95 **[+44.8, +432.4]**, retention **1.048**, monotone False (fallback never reached) → **PASS** | **PASS** |
| D_dossier | drift, battery (weekly-vol lead, no DD-normalized income), MAE/MFE, worst-5, calendar, margin (ASSUMED), capacity (stated), orthogonality k=2 — all printed | all sections printed; battery LEAD = 08:46 executable arm; thinning placebo N/A stated | PASS |
| S_skeptic ⛔ | four preregistered lenses, kill criteria fixed before results, mechanical verdict | duplication/fragility/regime/implementation all NO-KILL → **SURVIVES** | **PASS** |

⛔ = blocking. **Decision rule (spec verbatim): G_delay ∈ {PASS, FAST-EXECUTION-REQUIRED} AND skeptic SURVIVES → ledger PASS → FT0 freeze licensed.** Observed: PASS + SURVIVES → **ledger PASS**.

## 1. THE DECISIVE QUESTION — the delay curve (and what it actually showed)

Same 40 events, same signal r1 = c(08:45)−c(08:30), same 15:00 exit; only the fill is delayed. Paired moving-block bootstrap (L=5, B=2000, seed 20260910, ONE shared draw across arms so curve differences are never bootstrap noise). n_dropped = 0 and fresh-bar count 40/40 at every entry minute (no as-of fill was ever used at an entry).

| entry | n | gross move pt | net $/ct PRIMARY | CI95 profit $/ct | STRESS $/ct | retention vs 08:45 |
|---|---|---|---|---|---|---|
| 08:45 | 40 | −0.2445 | +177.7 | [+48.0, +428.5] | +115.2 | 1.000 |
| **08:46** | 40 | −0.2531 | **+186.3** | **[+44.8, +432.4]** | +123.8 | **1.048** |
| 08:47 | 40 | −0.2703 | +203.5 | [+59.7, +450.4] | +141.0 | 1.145 |
| 08:48 | 40 | −0.2695 | +202.7 | [+64.4, +444.1] | +140.2 | 1.141 |
| 08:50 | 40 | −0.2641 | +197.2 | [+55.0, +435.5] | +134.7 | 1.110 |

**The spec's latency fear is REFUTED, not merely survived.** The premise (from the G00072 neighborhood: the 08:50 cell retains only ~$17.7 of $177.7) conflated two objects: that cell **re-conditioned the signal on r(08:50)**; this curve holds the signal fixed at the 08:45 read and delays only the fill. Held fixed, the curve is flat-to-slightly-better with delay — the D1 drift table shows the mean path ticks UP ~+0.026 pt through 08:47 before the down-drift begins, so a delayed short enters at a marginally better price. The engine is **not latency-fragile at the 1–5 minute scale**; the executable 08:46 claim is if anything conservative vs 08:45. (The monotone-decay fallback clause is False, but mechanically irrelevant: the primary clause passed.)

## 2. Per-minute drift 08:45→09:15 (full table in `out/dossier.md`)

Cumulative short-$ per ct from the 08:45 close: −$8.6 (08:46) … −$19.5 (08:50) … +$25.0 (09:00), +$61.7 (09:15). Share of the eventual 15:00 mean move realized: **−8.0% by 08:50, 25.2% by 09:15**. Checkpoints (gross $/ct short): 09:30 +40.6, 10:30 +53.9, 12:00 +146.9, 14:00 +240.6, 15:00 +244.5. **Most of the edge accrues 10:30→14:00, not in the first minutes** — consistent with slow repricing, and the reason fill latency does not matter.

## 3. eval_battery (weekly-vol LEAD; LEAD arm = executable 08:46)

- **08:46 executable (LEAD), k=1:** Sharpe_wk **0.91** (mean $39.6/wk, sd $313.7/wk on the 188-wk calendar grid); total $7,451 = **$2,074/yr** on 11.1 tr/yr; k=2 ≈ **$4,148/yr**.
- 08:45 research reference, k=1: Sharpe_wk 0.86; $1,978/yr (reproduces G00072 G9).
- Path descriptors ($ ONLY, k=1): weekly maxDD $1,674 / CDaR95 $1,333 (08:46); k=2 linear: $3,347 / $2,667. **No income is normalized by any fixed-DD/CDaR figure; no trade-removal rule is evaluated → thinning placebo N/A (stated).**

## 4. MAE/MFE and worst-5 anatomy (executable 08:46 entry; `out/maemfe.csv`)

- MAE mean 0.417 pt ($417/ct), median 0.375, p90 0.797, **max 1.531 pt ($1,531/ct)**; MFE mean 0.641 pt, max 2.188 pt. Winners' (n=23) MAE mean 0.213 pt vs losers' (n=17) 0.693 pt — losers are identifiably adverse early, but no intraday stop is part of the frozen object (adding one would be retuning).
- Worst 5: 2023-01-12 CPI −$1,160.6; 2023-10-06 NFP −$879.4; 2025-12-16 NFP −$723.1; 2024-01-11 CPI −$629.4; 2024-08-14 CPI −$598.1. Three of five were near-flat or positive at 09:15 and lost in the afternoon — the loss profile is the drift reversing, not the entry.

## 5. Calendar honesty

- NFP+CPI same-session overlaps among the 40: **0**. Weekdays: Fri 21, Thu 7, Tue 6, Wed 6.
- NFP not on Friday (holiday/shifted releases): **3** — 2025-07-03, 2025-12-16 (a worst-5 trade), 2026-02-11.
- Roll windows (**ASSUMED-PROXY**: last session of Feb/May/Aug/Nov; the merged back-adjusted chain carries only the rolled contract's volume, so the TRUE volume crossover is NOT measurable here): event days within ±3 sessions: **2** — 2023-06-02 (d=2), **2023-09-01 (d=1, one of the top-3 winners — flagged)**.

## 6. Session, margin, capacity, orthogonality

- Entry 08:45–08:46 ET, flat at 15:00 → intraday only, **no overnight margin**. ZB day margin **ASSUMED ~$2,000/ct (FLAGGED, not broker-verified; no broker surface touched)**; k=2 ≈ $4,000 for ~6h14m on ~11 days/yr.
- Capacity: ZB top-of-book is among the deepest CME treasury books; k=2 negligible. **Stated, not proven.**
- Orthogonality (G00078 joint series AS-IS): ρ(ZB k=2, P1) daily **−0.0058**, weekly **+0.1004** (scale-invariant in k, shown); k=2 LIVE_SCALE marginal weekly-vol Sharpe **+0.0923** — reproduces G00078 exactly.

## 7. Adversarial skeptic (kill criteria preregistered in the src header; full prose `out/skeptic.md`)

| Lens | Kill criterion (preregistered) | Observed | Verdict |
|---|---|---|---|
| L1 duplication | tradable-known AND arbitraged: last-half after-cost mean ≥ 0 | last-20 mean −0.1363 pt (+$136/ct, still profitable through 2026); G00072 shift-null mean POSITIVE (generic down-momentum loses) | NO KILL → mechanism LABEL: behavioral underreaction / slow repricing of the 08:30 surprise |
| L2 fragility | G_delay = KILLED-AT-EXECUTION | G_delay = PASS | NO KILL. Stated most-likely-nothing: tail-carried n=40 (66% in 3 trades), \|mean\| < own MDE_80, drawn from the G00067 event-screen family — irreducible at n=40, discharged only by forward trades |
| L3 regime | both chronology halves wrong-sign | −0.2191 / −0.1363 pt, both profitable | NO KILL. Prospective FT-stage monitor proposed: KILL if cumulative forward after-cost mean ≤ 0 at n_fwd ≥ 20; REVIEW below −$100/ct at n_fwd ≥ 10 (~2 yr to kill point at 11 tr/yr — stated) |
| L4 implementation | blocking impossibility (cannot be fail-closed in NT8) | none — 7 FT4–FT9 risks enumerated (new class, ZB roll table from scratch under the LATCHING guard, 15:00 flatten fail-safe, stand-aside on missing 08:30/08:45 bars, calendar heartbeat, unmeasured ZB spread → STRESS arm +$123.8/ct is the honest floor, ASSUMED margin) | NO KILL |

**SKEPTIC VERDICT: SURVIVES.** The Lens-2 fragility statement and the Lens-3 forward monitor are **binding riders** on the FT0 license.

## Caveats (binding)

1. **DISCOVERY_CONSUMED, every table.** This run creates zero forward evidence. FT0 freezes an object; it does not deploy, promote, or touch any of the four baselines or the live book.
2. The retention > 1.0 readings on the delay curve are the same 40 in-sample events measured at slightly different prices — they say "no latency cliff," not "delay adds edge." The executable claim stays at 08:46.
3. The n=40 / tail-carried / below-MDE_80 fragility is unchanged from G00072 and is carried forward verbatim as the engine's stated risk.
4. ZB spread (1 tk/side) is modeled, never measured on this box; margin is ASSUMED; roll flags are ASSUMED-PROXY. None of these is quotable as verified fact at later stages.
5. One trade (2026-06-05) sits in the globally BURNED 2026-05-31→07-31 window (labeled since G00072).

## Next step per decision rule

**FT0: freeze the engine (rule + entry convention close(08:46) + k=2), then FT1–FT10 in a later run.** The Lens-3 chronology-half monitor and the Lens-2 fragility statement must enter the FT-stage preregistration. No deploy, no promotion, no baseline change.