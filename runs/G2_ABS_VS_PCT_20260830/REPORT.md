# G2_ABS_VS_PCT — RESULT: **PCT weakly dominates; and the recorded "direction" claim is FALSIFIED as a cost artifact**

Owner question (2026-08-30): *does P1/ABS actually make more money than P1/PCT?* Settled on the
same engine, window, bars, and cost template for both arms (NT8 Strategy Analyzer, NQ 09-26 1-min,
ETH, Lifetime commission, 0 slippage). 214 paired ISO weeks. Machine tables in
`ADJUDICATION_TABLES{,_B,_C}.txt`; series in `out/`.

> ## **ABS does NOT make more money than PCT.** PCT leads by **$45,009.80 (+16.4%)** — but the
> ## advantage is **not statistically established** (p 0.051–0.087), **5 of 214 weeks carry all of
> ## it**, and the repo's headline *direction* claim turns out to be an artifact.

## 1. The falsified claim — this is the load-bearing finding

`PROSPECTIVE_SHADOW.md:70` and `ALPHA_EVIDENCE_CLASSIFICATION.md:52` record:
*"PCT beats ABS on direction overwhelmingly (176/213 weeks, sign test p 7.1e-23)."*

**That number is a cost artifact.** Reproducing every W98 figure exactly from
`runs/WE_W98_BOXDENOM/out/weekly_arms_P1.csv` exposes the defect: **W98 charged each arm its OWN
spread rate** — ABS $14.517525 vs PCT $14.405321/ctrRT — a deterministic **$0.112205 discount to
PCT on every contract**. Consequently:

- **149 of 213 weeks have |diff| < $5**, and **147 of those are counted as "PCT wins"** — median
  win **$1.23**, together carrying **0.33% of the dollars**.
- On the **64 genuinely divergent weeks, PCT wins 29 (45.3%), p = 0.532** — **ABS wins most of the
  weeks where the two objects actually differ.**
- Same-cost replication reproduces the structure (ties-as-wins → 174/214 = 81.3% vs the recorded
  82.6%), confirming the mechanism rather than a transcription error.

**⇒ The direction claim must be struck.** What survives W98 is the magnitude question and the
`ABS_LOOSE` control (+$5.81, p 0.940, CI [−146, +157], powered to exclude $240).

## 2. What is true, at same cost

| | net | trades | $/wk | maxDD (weekly) | fixed-DD $/wk | %pos |
|---|---:|---:|---:|---:|---:|---:|
| **PCT** | **$318,972.40** | 2,137 | **$1,490.53** | **$21,610** | **$1,071.02** | 57.5% |
| ABS | $273,962.60 | 2,011 | $1,280.20 | $26,038 | $855.89 | 55.6% |

- **Paired weekly difference +$210.33/wk**, sd $1,788: iid t 1.72 (p 0.087), Newey–West(4)
  p 0.063, block bootstrap p 0.051. **Sign test on non-tied weeks: 42/82 = 51.2%, p 0.912.**
- **PCT weakly dominates**: it earns more *and* draws down less. The recorded **+39%** is really
  **+25.1%** at fixed DD on this same-cost basis.
- **132 of 214 weeks (61.7%) are byte-identical** — at size 1 the two objects are identical by
  construction; only 82 weeks can differ at all.

## 3. Why it is fragile

- **Concentration: the top 5 weeks carry 103.7% of the difference.** Remove them and the result is
  **−$8.02/wk, p 0.900, sign flipped**.
- **Era-unstable**: H1 p 0.04, H2 p 0.30, 2024 wrong sign, and **2026 alone (30 weeks) carries 64%**.
- **Mechanism (clean finding):** the 1,970 shared entries have **identical exits and exactly $0.00
  P&L difference**. The entire gap is **167 PCT-only entries (+$31,688)** and **41 ABS-only
  (−$13,322)** — i.e. **session-halt EXPOSURE, not exit management.**
- Power: MDE **$244.49/wk (+19.1%)**; observed effect is **0.86× MDE**. The recorded +39% *would*
  have been detected (2.04×). ~289 weeks needed.

## 4. ⭐ The shadow CANNOT settle this — which answers the roster question

The repo's standing line was *"burned data cannot settle it; running both from a common future
timestamp can."* **Half of that is now wrong and the other half is under-powered:**

- **Direction is settled NOW, for free, against the claim** (§1). No forward data required.
- **Magnitude cannot be settled by the shadow: power is 13.3% at 52 weeks and 22.3% at 104** —
  roughly **5× under-powered**. An inconclusive shadow result would say nothing, and must never be
  read as pro-ABS.

**⇒ Do NOT deploy P1/ABS as a shadow control.** It would consume operational attention for a test
that cannot conclude. The powered alternative, if the question is ever worth money: a **halt-event
study over the ~208 divergent decisions with a matched unconditional control**.

## 5. Decision

**KEEP PCT** — it dominates weakly on both axes and is the certified, deployed object. The honest
quotation changes: **"PCT dominates ABS in-sample on both return and drawdown; neither leg's
superiority is statistically established, and the recorded 176/213 direction result is withdrawn
as a cost artifact."**

## Process notes (both worth keeping)

- The runner **deliberately ran to 2026-07-31, not 08-30**: the August burn was authorized for
  `P1/PCT` and `XM_CONFLICT_v2` **only**, and `P1/ABS` is a third, separately-rostered object.
  Correct call — it protected a seal the orchestrator's own instruction would have crossed.
- Both agents independently noticed the paper deployments had changed mid-run (the orchestrator's
  swap to the hardened classes) and flagged it as *not theirs* rather than assuming.
- ⚠️ **Preregistration honesty:** this run's `spec.yaml` was written by the runner at run time and
  committed **with** the results, not before them. Disclosed, not backdated. The analysis is
  descriptive/adjudicative on already-consumed data, but it does not carry preregistered status.
