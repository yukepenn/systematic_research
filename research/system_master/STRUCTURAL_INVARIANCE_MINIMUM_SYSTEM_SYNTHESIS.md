> _Supersede note (2026-08-18) on three forward-looking statements below: (1) **EQV04 was
> subsequently attempted and PASSED bit-identical** (2026-08-11, `runs/EQV04_NT8_CANONICAL_PARITY/
> REPORT.md`); (2) **DOM01** went live 2026-08-11 and was **PAUSED** 2026-08-12
> (`DOM_PAUSE_CLEANUP_20260812.md`); (3) the named HTF future-work target was actioned as
> **HTFMECH01** (closed 2026-08-14, diagnostic: HTF cost is short-side-concentrated —
> `HTFMECH01_TILT_MECHANISM/REPORT.md`), with a direction-conditioned construction queued READY.
> Everything else stands as written._

# STRUCTURAL_INVARIANCE_MINIMUM_SYSTEM_SYNTHESIS

**Date:** 2026-08-10. **Repo SHA at synthesis time:** `121e3f65a3794b00d3272bf008c05f4af7ade85b`
(`origin/main`, verified in sync). **Incumbents unchanged throughout this campaign:**
`src/ninjascript/SolarWaveSMMaster_v4.cs` (Product A), `SolarWaveOneContractNQ_v5.cs` /
`SolarWaveOneContractMNQ_v5.cs` (Product B). No incumbent file was modified by anything below.

**What this campaign was:** aggressive, structured falsification of the incumbent architecture —
not a search for a better system. Three lanes: (A) structural invariance / minimum-system / causal
falsification / selection-robustness on the incumbent itself; (B) a clean-causal-substrate
replication of the prior wave's Auction findings; (C) DOM01 forward-collection maintenance. Zero
new protected-pool sessions were consumed. Nothing `>=2026-08-01` was touched.

## 0. What ran and what didn't

| Phase | Status | One-line result |
|---|---|---|
| P0 repo truth | done | HEAD/origin in sync throughout; no discrepancy found |
| P1 AUCTION04 (Lane B) | done | Clean substrate certified (0/378 causality violations); falsified AUCTION03's own "poc_price is exactly causal" claim; M5 confirmed (Case A), M2/M3 downgraded to sub-cost-hurdle (Case B) |
| P2 EQV01 | done | All 3 canonicalization hypotheses EXACT_EQUIVALENCE over full finite state space |
| P3 EQV02 | done | Full-history arrays bit-identical, both products, including the operational overlay |
| EQV03 | done | PnL bit-identical; EQV04 cleared but not attempted (see §9) |
| P4 HASH01 | done | Trial-count bracket updated to 499-653; behavioral dedup on the one processable family; surfaced a preregistration-gap finding about this campaign's own work |
| P5 EXEC01 | done | Product A execution parity leg-verified, zero decision-layer defect, ~97.8% of the +10.91% residual explained |
| P6/P7 GRID01/GRID02 | done | No cliffs; G13 not an isolated spike; broad VolMult band monetized |
| P8 PERT01 | done | VolPeriod sits on a slope not a peak; BAND_DAYS flips peak/valley by reporting window; "B evidence units" axis skipped (no matching parameter in code) |
| P9 SIMPLE01 (+completion) | done | Zero rungs pass; B1 (Product B, drop HTF) isolated to one inconclusive Sharpe margin after closing a data gap |
| P10 PLACEBO01 | done | HTF underperforms its own randomized-chronology null for both products; B-MOM mixed (real tail value, unconfirmed net value); hysteresis reassuring-not-decisive; sizing result resolved as substantially a null-construction artifact |
| P11 INFL01 | **not run as a separate phase** | concentration/influence checks (best-day removal, LOSO, top-3 removal) were embedded directly in AUCTION03/04, SIMPLE01's red-team pass, and PLACEBO01 rather than run as one more standalone pass — see §11 for why this is disclosed as a scope decision, not an omission |
| P12 STAT01 | done | Bonferroni haircut stays at 0.000 at the wider bracket (one new N=90 exception); PBO and SPA both correctly declined (no defensible input) |
| P13 EQV04 | **cleared, not attempted** | requires live NT8 NinjaScript compile-and-verify; a different, more consequential tooling step — see §9 |
| P14 BLIND01 | **folded into P9** | SIMPLE01 already implemented the full SPEC/EXECUTION/STATISTICAL/RED-TEAM/ADJUDICATOR blind separation at its own scope; a second campaign-wide blind pass was judged to add procedure without new evidence, given every phase already red-teamed or adversarially stress-tested its own claims |
| P15 synthesis | **this document** | — |

## 1. Canonical mathematical equivalence (EQV01–03)

All three of the owner's proposed simplification hypotheses are **exactly** equivalent to the
incumbent decoders over the complete reachable state space (not sampled) and over the full
historical record (245,943–540,232 bars, both products):

- **Product A** (`Q_A = Tpp + 4·bmomPos`, `target = clip(round_away(0.73·Q_A))`): 243/243 states
  exact. **The margin is thin** — the tightest realized safety margin anywhere in the domain is
  `+0.00591`, and EQV02 confirmed this exact knife-edge case is genuinely reached in real history
  (2022-01-24). A future re-fit of `KSolar`/`KBmom` could break this specific equivalence; it should
  be re-proven, not assumed, if those constants are ever touched.
- **Product B** (`Q_B = Tp + 4·bmomPos`, hysteresis `±5/±1` on `Q_B`): 729/729 states exact, and
  **robust** — the closest any real `M` value comes to a decision boundary is 18× the
  coefficient-approximation spread. Resolved a real discrepancy along the way: the owner's raw
  recollection of Product B's thresholds ("+5/+1 on `M`") does not match the deployed code
  (`EntryLevel=3.0`, `ExitLevel=1.0`) — but the recalled numbers *are* the exact integer
  quantization of that real boundary once expressed in `Q_B`-space. Both facts are true and
  non-contradictory; see `EQV01_BEHAVIORAL_CANONICALIZATION/REPORT.md` §2 for the full resolution.
- **`TiltRescale`** (0.9026 vs. 0.91): unconditional REPRESENTATIONAL_PRECISION for both products,
  no caveats, across 252/252 tested states.

Per campaign convention this is a **specification/representation finding, not an alpha promotion**
— the incumbent files are unchanged and remain the sole source of live/backtest behavior regardless
of outcome. See `CANONICAL_MATHEMATICAL_SPEC.md` for the full written-out equivalence.

## 2. Structural robustness (GRID01, GRID02, PERT01)

**Reassuring:** G7→G13→G25 (Solar ensemble resolution) converge smoothly in aggregate risk-adjusted
terms; G13 is not an isolated performance spike. Both disclosed endpoint neighbors ([5,29], [7,31])
match or beat the [6,30] center on both products in both windows — no cliff, a broad scale band is
monetized, not a narrow optimum.

**Not uniformly reassuring:** PERT01's one-at-a-time perturbation found genuine heterogeneity.
`VolPeriod` (368/460/552) shows a **monotonic increasing gradient** in both reporting windows — the
incumbent value of 460 sits on a slope, not a peak (552 does better in-sample on every metric
tested) — and it is also the most structurally disruptive axis (bar-level position agreement only
92.9–94.6%). `BAND_DAYS` (11/14/17) is a genuine **local peak in the fuller 2022–2026 history but a
local valley in the shorter canonical 2023–2025 window** — the two reporting windows disagree on
whether the incumbent is even locally optimal on this axis. `TiltSma` (40/50/60) is comparatively
flat. None of this authorizes re-tuning — it is diagnostic evidence only, and no winner was selected
anywhere in this lane, per the campaign's own zero-alpha-budget rule for this class of work.

## 3. Causal falsification (PLACEBO01)

The single most important finding of this campaign. Four preregistered causal placebo tests, N and
seed fixed before any result was seen:

- **B-MOM: MIXED.** An extreme, tail-significant drawdown-timing benefit for Product B (real B-MOM
  beats all 500 placebo draws on marginal max-drawdown reduction) — real informational content, not
  merely exposure. But net-PnL/Sharpe marginal contribution is only comparable-to-placebo for both
  products (88.8th–94.2nd percentile, short of the 95th-percentile tail-significance bar), and
  Product A carries a genuine turnover/cost penalty (100th percentile — worse than every placebo
  draw).
- **HTF: CONCERNING.** Real marginal net/Sharpe contribution sits **below the null median for both
  products** (27.8th–32.1st percentile) — a randomly-time-shuffled HTF chronology would, on
  average, have added more value than the real, correctly-aligned one. This was the
  preregistration's own explicitly anticipated falsification scenario, not a post-hoc
  reinterpretation.
- **Hysteresis(3,1): directionally favorable, not decisive.** Beats the median of a
  turnover-matched generic churn-reducer on Sharpe/net/DD (69th–87th percentile) but does not clear
  the 95th-percentile tail-significance bar.
- **Product-A sizing:** an apparently contradictory raw result (100th-percentile PnL/contract,
  0th-percentile marginal-exposure gradient) was investigated and resolved as **substantially a
  turnover/bar-composition artifact** of the null construction (permutation destroys real sizing's
  smooth autocorrelation, inflating turnover 11.4× and mechanically distorting the gradient
  comparison). One real, denominator-matched residual caveat survives the artifact correction:
  PnL/exposure-hour sits at the 15.2nd percentile — directionally unfavorable, not tail-significant.

Per the campaign's own standing rule, none of this by itself justifies removing any component — B-
MOM's tail-significant drawdown value despite unremarkable net/Sharpe is a live counter-example
within the same report. But HTF's result is the weakest evidence any component produced this
campaign, and it directly motivated §4.

## 4. Minimum-system ladder (SIMPLE01 + completion pass)

Blind-adjudicated non-inferiority test — SPEC froze exact candidate constructions (derived from the
real `.cs` files, not assumed) and margins before any performance was seen; STATISTICAL agents
tested fully anonymized labels, never told which was the incumbent; RED-TEAM attacked with full
visibility; ADJUDICATOR mapped labels back only at the end.

**Zero rungs pass for either product — `A_FULL`/`B_FULL` remain the only certified constructions.**
But the detail is not a clean rejection:

- **Product B — `B0`** (drop B-MOM *and* HTF) clearly fails (Sharpe non-inferiority `P=0.058`,
  far below the 0.90 bar). **`B1`** (drop HTF only, keep B-MOM) is a genuine near-miss: after the
  completion pass closed a data gap (trade-level retention, previously never computed), `B1` clears
  *every single frozen margin except one* — the Sharpe margin, which lands in the preregistered
  **INCONCLUSIVE** band (`P=0.847`, just short of 0.90, with 0.985 correlation to `B_FULL` — high
  power in principle, still short of the bar). This is not an economic rejection; it is a
  statistically underpowered near-miss, precisely isolated.
- **Product A — `A0`** (drop HTF entirely) and **`A2`** (keep the HTF up-weight, drop
  short-halving) both clearly fail multiple margins. **`A1`** (keep short-halving, drop only the
  specific `TiltMult` HTF up-weight multiplier) passes *every* statistical and risk margin tested
  but is construction-ineligible under the frozen complexity rule (it drops only one parameter,
  short of the "≥2 parameters without a module drop" bar) — a genuine **component-redundancy**
  finding (the `TiltMult` multiplier specifically doesn't materially matter) rather than a
  promotable architectural simplification.

**This is directly coherent with §3**: HTF is now the component with the weakest evidence across
two independent, differently-constructed tests (a causal placebo *and* a non-inferiority ladder),
while B-MOM and short-halving both look load-bearing — their removal clearly fails in both tests.
Per the campaign's standing rule (sec108–109), none of this — including `B1`'s near-pass — auto-
promotes anything; a passing simplification would still require the full battery (tail-risk stress,
capital-frontier interaction, NT8-executable proof) before promotion could even be considered, and
none of that is run here.

## 5. Trial-count reconciliation and behavioral deduplication (HASH01)

The honest trial-count bracket, recomputed today (not trusted from the 2026-08-07 note), is
**499–653** — up from `REGISTRY_GAP_NOTE.md`'s **229–383**, almost entirely from 270 post-gap-note
trial-slots the original note never covered. Zero double-counting between the two registry CSVs was
confirmed. Behavioral policy-hash deduplication was run on the one family with a reusable substrate
this session (the VolMult-grid family, 7 raw configs): exactly one exact duplicate found, and the
family's own eigenvalue participation ratio (≈1.0–1.07 of a maximum of 7) shows it was a deliberate
density probe around one policy, not 7 distinct strategies — scoped explicitly to ~1.1–1.4% of the
registry, not extrapolated further.

**A more important finding fell out of this task's own git-forensic method**: nearly all of *this
session's own structural-invariance work* — AUCTION01 through STAT01 — lacks git-verifiable
preregistration (spec and results routinely land in the same commit, or no `spec.yaml` exists at
all). This echoes, in a milder and contemporaneous-not-reconstructed form, the exact governance
failure `REGISTRY_GAP_NOTE.md` already disclosed once for Waves 1c–3. It was documented additively
in that same note rather than smoothed over, and practice changed prospectively (frozen specs now
committed separately and first, demonstrated on SIMPLE01's own completion pass) — no history was
rewritten.

## 6. Selection-robustness statistics (STAT01)

Reusing the repo's own existing, previously-validated Harvey-Liu/DSR implementation
(`src/analytics/trials.py`), the Bonferroni haircut Sharpe stays at **0.000** (fails BHY) for both
`A_FULL` and `B_FULL` at every trial count `N≥229` — unchanged qualitatively from the prior
229–383 bracket at the new, wider 499–653 bracket. One genuinely new finding: at `N=90` (the only
trial count with an unbroken, contemporaneously-committed paper trail), **some signal survives**
correction (`A_FULL 0.377`, `B_FULL 0.135`) — a threshold effect never isolated in this exact form
before, reported as a finding, not as grounds to prefer the more flattering assumption. The
Bailey–López de Prado DSR stays in the 0.002–0.05 range across the whole bracket under the
campaign's own preregistered `V`, but is dominated far more by that `V` assumption than by `N` —
confirming a prior campaign finding ("the answer is dominated by a judgement call, not the data")
still holds at the wider bracket. **PBO and SPA were both correctly declined**, not forced: the one
available candidate family is too small and too collinear for CSCV, and no candidate-generating
exercise this campaign (SIMPLE01, GRID01, GRID02, PERT01) ever adjudicated anything as superior to
its own benchmark, so SPA has no input to test.

## 7. Product-A execution-dollar attribution (EXEC01)

Closes a long-standing open item. Leg-by-leg reconciliation across 9 deliberately-selected
representative periods (55 sessions, chosen from turnover/exposure/reversal extremes *before*
opening any NT8 record): **1,371/1,371 order-level legs matched 1:1, zero unexplained dollars.**
100% of the sample residual attributes to the same two already-disclosed, non-defect conventions
used to explain the one-contract objects (94.4% one-tick fill convention, 5.6% genuine-MNQ price
basis) — no decision-layer defect found in any leg examined. Extrapolated to the full history:
~97.8% of the documented +10.91% residual explained. Sets a conservative forward bar (~$430/0.24%
of net) below which no future Product-A challenger may be promoted on Python evidence alone.

## 8. Auction clean-substrate replication (AUCTION04)

Rebuilt the Auction substrate with strict event-time construction and explicit units; a 378-
timestamp automated causality audit certified the new substrate clean (0 violations) — and, in the
process, **falsified** AUCTION03's own claim (based on 9 manual spot checks) that `poc_price` was
already exactly causal: 1/378 checks found a genuine leak (−60 ticks). Re-running the identical
bounded M1–M5 slate on the clean substrate:

- **M2/M3 (signed reversion): CASE B.** Same sign, same robustness/fragility pattern survives, but
  the corrected magnitude at its one significant horizon (+1.911 ticks) is **below** the 2.872-tick
  cost hurdle — AUCTION03's own economic-relevance framing had compared against 4×-inflated values.
  Real signal, not economically actionable as tested.
- **M5 (incumbent-aligned action-value deterioration): CASE A, essentially unchanged.** Independent
  confirmation on certified-clean data (not just internal stress-testing on defective data) that
  this is real signal, not a lookahead artifact.

No Auction policy was built. No protected-pool session was opened. This campaign's own directive
explicitly stops Auction policy research after this clean replication regardless of verdict.

## 9. What remains genuinely open, not run this campaign

- **EQV04** (research-only canonical NinjaScript objects + NT8 parity certification): explicitly
  *cleared* by EQV01–03 all passing, but not attempted. This requires live NT8 compile-and-verify
  (the same category of action DOM01 already used safely — research-only, no order placement) but
  is a materially different, more consequential tooling step than the pure-Python work in this
  campaign, and deserves its own careful, sequential (not highly-parallelized) execution rather
  than being folded into this wave.
- **DOM01 forward collection**: unchanged from Wave 5. Compiled and compile-verified against live
  NT8; never attached to a chart; a sealed forward vault and exact numbered owner instructions
  exist. The single remaining step (confirm Level-II entitlement, attach the indicator) is a manual
  NT8 UI/entitlement action outside pure code scope.
- **A genuinely completed B1 near-miss**: `B1`'s single remaining blocker is a statistically
  underpowered Sharpe margin, not an economic failure. A larger sample (more history, or a
  different reporting window) could in principle resolve this one way or the other — not attempted
  here, since it would require either more chronological data than currently exists or a
  methodological change to the frozen margin itself, both out of this task's scope.

## 10. Primary questions answered (directive Q1–Q18)

**Q1. Are the decimal weights behaviorally meaningful or representational?** Representational for
`KSolar`/`KBmom` (Product A, thin margin), the `Q_B` hysteresis thresholds (Product B, robust
margin), and `TiltRescale` (both, robust). `ss` (short-halving) is behaviorally meaningful — no
clean unification with Product B exists because Product B has no analogous term.

**Q2. Is there an exact common integer evidence-score interpretation?** Yes — `Q = Tpp/Tp + 4·bmomPos`
for both products, proven exact over the full reachable domain (§1).

**Q3. Does Solar consensus converge as scale-grid resolution changes?** Yes, smoothly, G7→G13→G25
(§2). The one exception (G49) is value- not density-sensitive.

**Q4. Are 460/14/50 broad structural choices or isolated spikes?** Mixed. `TiltSma`≈flat.
`BAND_DAYS`=14 is window-dependent (peak in one window, valley in another). `VolPeriod`=460 is on a
monotonic slope, not a peak, in both windows — the least reassuring of the three (§2).

**Q5. Does B-MOM beat activation-matched placebos?** Mixed — real drawdown-timing value (tail-
significant), unconfirmed net-PnL/Sharpe value (§3).

**Q6. Does HTF beat slow-state placebos?** No — below the null median for both products (§3), and
its removal is the closest near-miss in the independent non-inferiority ladder (§4). The weakest-
evidenced component this campaign.

**Q7. Does hysteresis beat turnover-matched null controls?** Directionally yes, not tail-
significant (§3).

**Q8. Does Product-A sizing beat exposure-matched permutations?** The headline contradiction was an
artifact; one real, non-tail-significant residual caveat (PnL/exposure-hour) survives (§3).

**Q9/Q10. Is a simpler Product B or Product A non-inferior?** No rung passes for either product
today; the closest calls (`B1`, `A1`) are blocked by an inconclusive statistical margin and a
construction-eligibility rule respectively, not by a clear economic failure (§4).

**Q11. How much of global trial burden is representational duplication?** Only measurable for
~1.1–1.4% of the registry (the VolMult-grid family): 6/7 behaviorally distinct, but effectively
~1 independent dimension by correlation. Not extrapolated to the full registry (§5).

**Q12. What does DSR say under all defensible trial-count assumptions?** Haircut stays at 0.000 for
`N≥229`, unchanged at the wider 499–653 bracket; some signal survives only at the narrowest,
most-defensible `N=90`. The Bailey DSR is dominated by the `V` assumption, not `N` (§6).

**Q13. What does PBO say within bounded families?** Correctly declined — no family both large and
diverse enough exists in the recoverable evidence (§6).

**Q14. What does SPA say about simplification challengers?** Correctly declined — no candidate this
campaign was ever adjudicated as superior to its benchmark (§6).

**Q15. Is Product-A research/executable dollar reconciliation sufficient for small-candidate
claims?** Yes as of this campaign — leg-verified to zero unexplained dollars on 9 representative
periods, ~97.8% of the full-history residual explained, a concrete forward bar established (§7).

**Q16. Does clean Auction data preserve the prior M2/M3/M5 findings?** M5 yes (Case A). M2/M3
survives structurally but loses economic significance once correctly unit-scaled (Case B) (§8).

**Q17. What is the simplest architecture currently defensible?** The full incumbent, for both
products — nothing simpler was certified. But HTF is the component whose removal comes closest to
non-inferior, and whose independent causal evidence is weakest; it is the natural target for any
future, better-powered re-test.

**Q18. What uncertainty remains fundamentally unresolvable without future data?** `B1`'s Sharpe
margin (needs more independent sessions than currently exist to resolve INCONCLUSIVE into PASS or
FAIL); the campaign-wide selection-bias question (the lost Waves 1c–3 preregistration, and now this
session's own milder echo of the same gap, cannot be statistically restored per sec66); and, as
always, no historical audit of any kind can establish future profitability.

## 11. Final structural interpretation

Per directive sec107, forcing a single verdict (A/B/C/D) would misrepresent genuinely mixed
evidence. The honest composite reading:

**A structurally coherent core (Solar consensus + B-MOM + short-halving) that survives deliberate
attempts to falsify and simplify it, carrying one specific overengineered-or-at-least-currently-
unproven overlay (HTF), sitting on top of selection-adjusted historical evidence that remains weak
by every measure computed here — unchanged from before this campaign, at a materially wider and
more honestly-bounded trial-count bracket.** B-MOM and short-halving both survive real attempts at
removal (placebo tests, non-inferiority ladder) with clear, if not uniformly tail-significant,
evidence of value. HTF fails to beat its own randomized-chronology null on the metrics that matter
most (net/Sharpe, both products) and is the only component whose removal produces a genuine
near-miss in an independently-designed, blind-adjudicated ladder. None of this authorizes removing
HTF today — the near-miss is a statistical power problem, not a clean failure, and per this
campaign's own standing rule, passing a placebo or a non-inferiority test is not itself a promotion
criterion. It is, however, the single clearest, best-evidenced lead this campaign produced for a
*future*, better-powered structural test — precisely the kind of finding sec111 anticipates:
report brittleness, do not fix it in the same campaign.

Selection-adjusted evidence for the raw historical Sharpe magnitude remains weak throughout (§6),
consistent with — not contradicted by — the structural evidence above: a coherent mechanism can
exist and be worth defending on falsification grounds even while its measured historical magnitude
cannot be strongly distinguished from what ~500-650 trials would produce by chance. The strongest
defensible statement, per sec113's own required register: **the architecture appears structurally
coherent and robust across multiple deliberately degraded and falsified representations, with one
specific component (HTF) carrying materially weaker independent evidence than the rest, but
historical Sharpe magnitude remains subject to selection and regime uncertainty that this campaign's
own statistics could not resolve either way.** No guarantee of future profitability is made or
implied by anything in this document.
