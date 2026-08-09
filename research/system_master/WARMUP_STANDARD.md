# WARMUP / START-STATE STANDARD — binding from 2026-08-09

_Created under MEGA PROMPT V7 §F, which promotes the Wave-17 start-state finding to a standing
rule. Append-only. This file governs every backtest, every replay, and every comparison against
a NinjaTrader Strategy Analyzer run in this program._

---

## The finding this exists because of

The identical window, the identical code, the identical end date returns
**+$7,426.36 / 174 trades** when a Strategy Analyzer run *starts* at 2026-01-01, and
**−$46.60 / 185 trades** when the same window is *sliced out* of the full 2022-2026 run
(`SolarWaveOneContractNQ_Final`; registry seq 458). A year sliced out of a long backtest and a
run started at the beginning of that year are **different objects**.

---

## R1. The continuation basis is mandatory

Every backtest and every replay used for research **starts at 2022-01-03 or earlier**, and any
reported sub-window is **sliced out of that continuation**. A run that begins at the start of
the window it reports is not a research artifact and may not be used for screening, scoring,
ranking, or any comparison against a continuation number.

## R2. The true binding warmup is **51 sessions**, and it is not what Wave 17 said it was

**Correction to my own Wave-17 statement, made directly per §18.** `CURRENT_TRUTH.md` §8b
attributes the start-state gap to "`sigma460` warms from scratch (~460 bars), `tiltState` needs
50 prior session closes, and B-MOM needs 14 RTH days of slot history", implying the Solar core
is the slow part. **Measured, it is not.** The Solar leg re-synchronizes in **2–4 sessions**:

| fresh start | sessions until the LAST bar where the fresh target differs from the continuation | bars disagreeing |
|---|---:|---:|
| 2023-01-03 | **2** | 663 of 401,922 (0.16%) |
| 2024-01-02 | **3** | 597 of 284,207 (0.21%) |
| 2025-01-02 | **4** | 1,031 of 165,863 (0.62%) |

(`runs/W18R1_M1_VOLSEASON/out/warmup_convergence.csv`; the 13-member E10 target vector was
rebuilt from a cold start at each date and compared bar-for-bar against the continuation.)

The reason is structural and should have been obvious: `member_states` is a directional-change
state machine whose anchor and trend are re-determined by recent price after a few flips, and
`sigma_series` uses an **expanding** mean for `t <= 460` rather than returning NaN — so sigma is
defined immediately and merely noisier, not absent. 460 bars is the window length, **not** the
convergence time.

**What actually binds is the tilt.** `htf_state()` is `sign(session_close − SMA50(session
closes))` with a `.shift(1)`, so it is **undefined until 51 complete prior sessions exist** —
about 2.4 calendar months. B-MOM needs 14 RTH days. For any object carrying the HTF tilt
(which is every Product A and Product B object), **51 sessions is the binding constraint** and
it is exact, not asymptotic: once 50 prior closes exist the SMA is correct, there is no further
convergence.

This also re-explains the Wave-17 gap correctly: a fresh run beginning 2026-01-01 has **no
tilt at all** for its first 51 sessions — roughly half of the Jan→May window — so for half of
that comparison the two objects were structurally different, not merely differently warmed.

## R3. The discard rule

**Discard at least 60 sessions from the head of any fresh run before reading any number from
it.** 60 is the standing figure: it is the smallest round count strictly above the 51-session
binding constraint, and it coincides with the warmup floor independently chosen in
`runs/W18R1_M1_VOLSEASON/spec.yaml` on unrelated grounds.

If an object's state dependencies differ from the ones above, the spec must state its own
maximum and justify it. The 60-session figure is a floor, never a ceiling.

## R4. Every UI comparison must state its start date and warmup convention

A number compared against a NinjaTrader Strategy Analyzer run is **not a comparison** unless
both of these are stated for both sides:

1. the **start date** of the run (not the start of the reported window), and
2. the **warmup convention** — continuation-sliced, or fresh-with-N-sessions-discarded.

A table of recency tiers cut from a continuation must be labelled **CONTINUATION** on every
row. Those rows will not reproduce in the Strategy Analyzer from a same-year start and saying
so is mandatory, not optional. Every tier row in `runs/W18R1_M1_VOLSEASON/out/recency_tiers.csv`
carries this label.

---

## Standing data cautions (this program's running list)

1. **NQ and MNQ 3-minute grids are not interchangeable.** 13 NQ / 11 MNQ dev sessions carry
   internal gaps; counting non-17:00 sessions *by bar shape* gives 44, not the calendar's 43.
   Any work that infers session shape from bar counts must handle this. (Wave 17 red team.)
2. **Warmup / start state** — this document.
3. **The dev boundary is written two ways in the record**: `CONVENTIONS.md:12` says
   **2026-05-31**; `src/analytics/primary_objective.py:64` and
   `runs/W17_C4_COMPLIANCE/src/v1f_eventdays.py:49` say **2026-05-29**. They denote the same
   window (2026-05-29 Friday is the last session ≤ 2026-05-31), but there is no canonical
   constant. New code should state which it means. (Wave 18.)
4. **Cross-instrument grids differ from NQ's.** ES matches NQ session-for-session (1,139); RTY
   and YM have **1,132** sessions, 99.39% coverage. Instruments must be aligned on **session
   date**, never on bar index. Also, at the `to` boundary the ES/RTY/YM exports end at 16:57
   where NQ ends at 17:00 — a one-bar difference on the final session only.
   (`runs/W18R2_M5_XINST/out/substrate_check.csv`, Wave 18.)
