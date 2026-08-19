# HTFDIR01 — REPORT (readout 2026-08-18; spec frozen at fb44d67 BEFORE any result)

**Verdict: PASS-SCREEN on Product B under the frozen gates — with FOUR BINDING RED-TEAM
CORRECTIONS that any downstream step must carry. FAIL on Product A. No promotion (per spec, none
was possible in this wave). One alpha hypothesis consumed (1 of 2 under the §15 cap).**

## 1. Headline numbers (dev 2022-01-03 → 2026-05-29; certified substrate, gate #1/#2 both PASS)

| | incumbent (SYM) | ARM_LONGONLY | Δ |
|---|---|---|---|
| **B-NQ** net / Sharpe | $301,915.92 / 1.1131 | **$323,979.04 / 1.1984** | +$22,063 / **+0.0853** |
| B-NQ gates | — | G1 P=0.9556 ✓ · G2 LOYO min +0.051, 2022-25 Δnet +$12,334 ✓ · G3 top-10 retention 99.4% ✓ · G4 CDaR 44.5k→41.8k ✓ (maxDD 59.7k→57.6k) · G5 control fails as predicted P=0.062 ✓ · G7 2026 = 44% of Δ (not sole driver) | ALL PASS |
| B-MNQ (shared core; reported, not gated) | $28,482.60 / 1.0491 | $30,725.20 / 1.1355 | P=0.9613, same pattern |
| **Product A** net / Sharpe | $177,924.40 / 1.1770 | $170,594.00 / 1.1797 | **FAIL**: G1 P=0.5422, G2 2022-25 Δnet −$6,106, G3 retention 90.2% |
| A, G6 both conventions | — | ΔJ mixture +0.0211, ΔJ Γ-minimax +0.0518 — same sign, no flip (recorded; A fails on G1/G2/G3 regardless) | |

Sortino 1.884→2.051, Calmar 1.119→1.243, worst month −$22.4k→−$21.5k (B). Positive-day rate
unchanged (46.8%→46.6%) — this construction does not buy daily consistency, it trims a losing
exposure class.

## 2. Red team (4 independent attackers: implementation / statistics / economics / process)

**No kill on any attack.** Implementation reproduced bit-exact (ledger max diff 3.6e-12, all six
bootstrap p-values to <1e-9; make_m_arr proven boolean-equivalent by exhaustive truth table;
session-close flatness on all 540,232 bars; spec-commit-first verified by git + NTFS forensics;
seal CLEAN — nothing ≥2026-08-01 touched). Statistics robust to the iid-day assumption: moving-
block bootstrap L=5/L=20 gives P=0.9572/0.9545 (still ≥0.85); no single-day dependence (ex-best-3
days Δnet +$10,546, ΔSharpe +0.043).

**BINDING CORRECTIONS (all verified by attacker computation):**

1. **Recency concentration.** 86.4% of B's Δnet comes from 2025+2026; pre-2025-04 subsample
   P(ΔSharpe>0)=0.585, post-2025-04 P=0.9946; Δnet inside HTFMECH01's own diagnostic window
   (2023-01→2025-02) is **−$55.76** — the fix earned nothing where the mechanism was diagnosed.
   The frozen gates (LOYO single-year drops; G7's 2026-only tripwire) cannot see a hot window
   straddling 2025/2026; the letter passes, the claim "stable validated mechanism" would be false.
2. **Adverse post-dev extension.** On the only post-hypothesis data (2026-06/07, research-consumed,
   non-promotional): candidate LOSES on both products (B −$1,660, A −$1,711).
3. **Mechanism story corrected.** HTFMECH01's A-side −$22,020 conflated the agreement-up-weight
   and SHORTHALF channels (its counterfactual removed both). Direct decomposition here shows A's
   short-agreement boost was value-ADDITIVE (removing it costs −$8,932 on those bars) — the spec's
   motivating sentence was wrong for A, and A failing is the mechanistically coherent outcome
   (A works the intensive margin on established shorts; B works the extensive margin, where the
   up-weight creates marginal hysteresis-threshold shorts that lost −$22,513 on 3,439 avoided
   bars). A NOTILT placebo partially defuses a pure-short-suppression reading: LONGONLY beats
   no-tilt-at-all on BOTH products (P≈0.94), so the retained long-side up-weight carries real
   value; but a crude NOSHORT diagnostic (Sharpe 1.502) dominates the candidate on the gated
   statistic while failing right-tail retention (45.9%) — the candidate is best understood as
   **a conditional trim of the marginal short class, plus genuine long-side tilt value**, not as
   "new HTF information."
4. **Regime-dependence of the trimmed shorts.** The avoided-short toxicity flips sign: 2024 +$937
   (trim hurt), Jun-Jul 2026 shorts earned ~$43k for the incumbent; 2022Q4 the trim cost −$6.5k
   in a sustained bear. This is partly a bet on continued melt-up squeeze regimes.

Minor: B-MNQ replica's −$104.50 vs certified $28,587.10 root-caused to the genuine-MNQ price
basis (documented residual class, PRICE01/ONE_CONTRACT_FRONTIER); basis cancels to first order in
the paired comparison. G4_pass stored as float; delta-day sign test adverse (49 wins / 73 losses,
p=0.037) with wins concentrated in few large days — the delta itself is right-tail-shaped.

## 3. Disposition (per frozen spec + standing decay-aware doctrine)

- **PASS-SCREEN stands on the letter for Product B.** The next step the spec names — NT8
  executable build + representative-window parity + full promotion battery — is **queued READY,
  gated on its own separate preregistration and owner go-ahead**. It is NOT started.
- **Recommendation to the owner (not self-executed):** given corrections 1–2 (92% of the effect
  in the last 14 months of dev; the freshest 2 months adverse), the cheap decisive evidence is
  FORWARD data, not more history: authorize a **candidate shadow ledger** at each MONITOR-01
  reading (evaluation-only, frozen construction, B1_FUTURE_CONFIRMATION_SPEC §10(a) pattern).
  2–3 quarterly readings distinguish "regime bet that already peaked" from "structural trim"
  before any NT8 build effort is spent.
- **Product A direction-conditioning: CLOSED** (one shot, spent). A materially different A-side
  HTF hypothesis (e.g. the SHORTHALF channel, which this arm never touched) would need its own
  new preregistration and would face the same recency scrutiny.
- HTFMECH01's REPORT gains a correction pointer (its side-decomposition conflates two channels —
  recorded there as an appended note).

## 4. Bookkeeping

Artifacts: `out/htfdir01_results.json`, `out/htfdir01_g6_diagnostics.json`,
`out/daily_ledgers_dev.csv` (all reproduced bit-exact by the red team from committed source).
Seal audit: `daily_ledgers_dev.csv` → DEV (max 2026-05-29); JSONs carry no post-dev dates beyond
the labeled extension aggregates; input bars CSV is CONSUMED-class loaded-then-sliced (permitted,
disclosed). Registry: TESTING_LEDGER.csv row appended this commit. Red-team full outputs: workflow
transcripts (4 attackers, 119 tool calls); key numbers quoted above verbatim.
