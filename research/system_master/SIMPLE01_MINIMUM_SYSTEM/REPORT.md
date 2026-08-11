# SIMPLE01 — Minimum System: Adjudication (Task 4, campaign directive sec76)

**Role discipline.** This report is written by the adjudicator, after the SPEC (Tasks 1-3, frozen
before any candidate existed), the blind statistical evaluation (two independent agents, one per
product, working on anonymized labels), and the red-team review were all already complete and frozen.
The un-blinding mapping below is applied for the first time in this document. No margin, window, or
threshold is altered from what `01_SPEC_frozen_margins.md` and `02_SPEC_complexity_metric.md` already
fixed; this task only reads the sealed results, maps labels back to real architectures, and applies
the preregistered pass/fail logic — including refusing to certify a margin the red team showed cannot
currently be certified.

**Headline result, stated up front so it is not buried:** **zero rungs pass, for either product.**
`SolarWaveSMMaster_v4.cs` (Product A) and `SolarWaveOneContractNQ_v5.cs` (Product B) both remain, on
this evidence, the simplest architectures on their respective ladders that cannot be shown non-worse
by every frozen margin simultaneously. This is a valid, informative null result (sec110) — not an
inconclusive task. Section 5 explains what each ablated component appears to be earning its keep by
contributing.

---

## 0. Label un-blinding

| Blind label | Real architecture | Rung role |
|---|---|---|
| Q | **B0** | Product B, Solar-only (`mm`, `bmomPos` both forced neutral) |
| Z | **B1** | Product B, Solar + B-MOM (`mm` forced 1.0, `bmomPos` real) |
| M | **B_FULL** | Product B incumbent, `SolarWaveOneContractNQ_v5.cs`, unmodified |
| W | **A0** | Product A, Solar + B-MOM, no HTF (`mm`, `ss` both forced 1.0) |
| K | **A1** | Product A, + short-halving only (`ss` real, `mm` forced 1.0) |
| R | **A2** | Product A, + HTF up-weight only (`mm` real, `ss` forced 1.0) |
| V | **A_FULL** | Product A incumbent, `SolarWaveSMMaster_v4.cs`, unmodified |

Per `00_SPEC_candidate_manifest.md`, Product B's ladder is 3 rungs (B2 is construction-identical to
B_FULL and was dropped as redundant before blinding), and Product A's ladder is a 2×2 factorial in
`{ss, mm}` (A1/A2 are siblings of A0, not a chain — `mm` and `ss` are proven mutually exclusive on the
real domain, so both are well-posed, but neither is "A0 plus a bit more of the other").

All figures below are dev-window (`CONVENTIONS.md` CURRENT, 2022-01-01→2026-05-31, n=1,139 sessions),
the sole gating window per `01_SPEC_frozen_margins.md` §1.1. The legacy canonical window and the
June-July characterization panel are non-gating by the same frozen spec and are not re-litigated here.

---

## 1. Product B — un-blinded ladder results

### 1.1 B0 (Solar-only) vs. B_FULL

| Margin | Result | Detail |
|---|---|---|
| 3.1 Sharpe non-inferiority | **FAIL** | P[Sharpe_B0 ≥ Sharpe_FULL − 0.10] = 0.0584; point diff −0.570; 90% CI [−1.170, 0.026]; corr(B0,FULL)=0.814 |
| 3.2 CDaR ≤1.10×FULL | **FAIL** | point ratio 1.397; bootstrap mean ratio 1.338, P[ratio≤1.10]=0.357 |
| 3.3 Intraday DD ≤1.15×FULL | **FAIL** | reported ratio 1.281; red-team-corrected authoritative ratio 1.196 (see §3.1) — still fails the 1.15 cap either way |
| 3.4 Retention (day AND trade) | **FAIL** | day-leg 0.813 < 0.90 bar — fails outright, trade-leg never reached |
| 3.5 After-cost positive | PASS | dev net $130,413 |
| 3.6 Cost-stress positive | PASS | +1 tick/side dev net $115,608 |
| 3.7 Annual sign-match ≥4/5 | PASS | 5/5 years same sign as FULL |
| 3.8 Concentration gate | PASS (vacuous) | B0's dev net is below B_FULL's in every window — no incremental advantage exists to concentrate |
| 3.9 Complexity reduction | PASS | drops 2 full modules (B-MOM, HTF) |

**Overall: FAIL.** B0 fails four of nine margins, including the two most economically central ones
(Sharpe, CDaR) by a wide margin, not a borderline one. Dropping both B-MOM and HTF costs Product B
materially on return-adjusted performance, tail risk, and worst-day retention simultaneously.

### 1.2 B1 (Solar + B-MOM, no HTF) vs. B_FULL

| Margin | Result | Detail |
|---|---|---|
| 3.1 Sharpe non-inferiority | **INCONCLUSIVE** | P[Sharpe_B1 ≥ Sharpe_FULL − 0.10] = 0.8473 — inside the frozen [0.80, 0.90) inconclusive band, short of the 0.90 pass bar; point diff −0.011; 90% CI [−0.180, 0.157]; corr(B1,FULL)=0.985 (very high, as the spec's own power table anticipated for a near-neighbor rung) |
| 3.2 CDaR ≤1.10×FULL | PASS | point ratio 0.946; bootstrap mean 1.024, P[ratio≤1.10]=0.776 |
| 3.3 Intraday DD ≤1.15×FULL | PASS | reported ratio 0.927; red-team-corrected authoritative ratio 0.936 — still passes either way |
| 3.4 Retention (day AND trade) | **FAIL to certify** | day-leg 0.9941 ≥ 0.90 (passes), but the trade-level leg required jointly by `CONVENTIONS.md` gate 6 was never computed for any of the 7 rungs (execution scripts exported session-level P&L only) — red team rates this DATA_UNAVAILABLE, HIGH severity, and explicitly states no rung can be certified as clearing the complete margin on this evidence |
| 3.5 After-cost positive | PASS | dev net $293,626.92 |
| 3.6 Cost-stress positive | PASS | +1 tick/side dev net $275,826.92 |
| 3.7 Annual sign-match ≥4/5 | PASS | 5/5 years same sign as FULL |
| 3.8 Concentration gate | PASS (vacuous) | B1's dev net is below B_FULL's in every window |
| 3.9 Complexity reduction | PASS | drops 1 full module (HTF) |

**Overall: FAIL — the closest near-miss on the entire ladder, but a genuine, not a cosmetic, miss.**
Two separate margins fail to clear: the Sharpe margin lands in the preregistered INCONCLUSIVE band
(directionally supportive, high correlation to FULL, but short of the 0.90 bar by a margin the spec's
own power analysis says is plausibly within this test's noise floor for a high-ρ near-neighbor — yet
INCONCLUSIVE was frozen in advance specifically as "not a pass," not as a discretionary judgment call
available at adjudication time); and the retention margin's jointly-required trade-level leg is
missing evidence entirely, so even the day-leg's clean pass cannot be promoted to a full margin PASS.
Removing HTF from Product B therefore reads as **plausibly cheap but not proven cheap** — the honest
statement given the frozen rules, not "should have passed."

### 1.3 Product B summary

No Product B rung passes. `SolarWaveOneContractNQ_v5.cs` (B_FULL) remains the simplest Product B
construction that clears every frozen margin — because it is the only one that clears them at all.

---

## 2. Product A — un-blinded ladder results

### 2.1 A0 (Solar + B-MOM, no HTF, no short-halving) vs. A_FULL

| Margin | Result | Detail |
|---|---|---|
| 3.1 Sharpe non-inferiority | **FAIL** | P = 0.2239; 90% CI of diff [−0.3513, −0.0108]; corr(A0,FULL)=0.9737 |
| 3.2 CDaR ≤1.10×FULL | **FAIL** | point ratio 1.2726; bootstrap mean ratio 1.1577 — both exceed the cap |
| 3.3 Intraday DD ≤1.15×FULL | PASS | ratio 1.0459 |
| 3.4 Retention (day AND trade) | **FAIL to certify** | day-leg 0.9018 ≥ 0.90 passes, but trade-level leg DATA_UNAVAILABLE for all rungs — cannot be certified regardless |
| 3.5 After-cost positive | PASS | |
| 3.6 Cost-stress positive | PASS | net_stress(+1 tick/side) = $132,936.2 |
| 3.7 Annual sign-match ≥4/5 | PASS | 5/5 years |
| 3.8 Concentration gate | PASS (vacuous) | incremental advantage vs. FULL is negative (−$25,363.2 dev) |
| 3.9 Complexity reduction | PASS | drops the full HTF module (both `mm` and `ss` forced neutral) |

**Overall: FAIL.** A0 fails Sharpe and CDaR outright (not borderline: CDaR exceeds the 1.10 cap by
15-27 points depending on point vs. bootstrap estimate). Dropping HTF entirely costs Product A on both
return-adjusted performance and tail risk.

### 2.2 A1 (+ short-halving only, HTF up-weight forced off) vs. A_FULL

| Margin | Result | Detail |
|---|---|---|
| 3.1 Sharpe non-inferiority | PASS | P = 0.9077; 90% CI [−0.1114, 0.0187]; corr(A1,FULL)=0.995 |
| 3.2 CDaR ≤1.10×FULL | PASS | point ratio 0.9779; bootstrap mean 0.9715 |
| 3.3 Intraday DD ≤1.15×FULL | PASS | ratio 0.8795 |
| 3.4 Retention (day AND trade) | **FAIL to certify** | day-leg 0.9018 passes numerically **but is identical to A0's day-leg value to 10+ significant figures** (red team, independently reproduced from raw CSVs) — proof that A_FULL's own top-10 dev-window days are untouched by `ss` either way, so this metric has zero power to distinguish A0 from A1 here; both rungs also clear the bar by only 0.18 percentage points, a razor-thin, largely coincidental pass, not a robust property of either construction. Trade-level leg is DATA_UNAVAILABLE for every rung, same as elsewhere. |
| 3.5 After-cost positive | PASS | |
| 3.6 Cost-stress positive | PASS | net_stress(+1 tick/side) = $143,189.1 |
| 3.7 Annual sign-match ≥4/5 | PASS | 5/5 years |
| 3.8 Concentration gate | PASS (vacuous) | incremental advantage vs. FULL is negative (−$18,135.3 dev) |
| 3.9 Complexity reduction | **FAIL** | 0 full modules dropped vs. FULL — the HTF module (`tiltState`/`TiltSma`) stays fully live via the `ss` branch; only 1 incremental parameter (`TiltMult`) drops, short of the ≥2-without-a-module-drop bar frozen in `02_SPEC_complexity_metric.md` §4 |

**Overall: FAIL — but for a different reason than A0/A2.** A1 is the one rung on either ladder whose
*statistical/risk margins are all clean*: Sharpe, CDaR, and intraday-DD all pass comfortably, with the
highest candidate/FULL correlation on the whole board (0.995). It still fails overall for two
independent reasons that neither wait on nor depend on the statistics: (i) `02_SPEC_complexity_metric.md`
was frozen, from construction alone, **before any candidate was scored**, precisely to prevent a
statistically-clean-but-architecturally-trivial ablation from being read as "the simpler system" —
A1 keeps the entire HTF signal computation and its `TiltSma` state live, forcing only one downstream
usage constant, so it is construction-ineligible for promotion under margin 3.9 regardless of how it
performs; (ii) the retention margin's trade-level leg is unavailable for this rung too. This is a
genuine, disclosed finding — HTF's *up-weight* usage (`mm`) may be doing more work than its
*short-halving* usage (`ss`) inside Product A — but it is a causal-attribution result (continuing
PLACEBO01's program), not a promotion candidate; the manifest said as much before A1 was ever run
(`00_SPEC_candidate_manifest.md` §2.3: A1/A2 "exist for causal attribution only... not because either
is expected, by construction alone, to be a materially simpler deployable system").

### 2.3 A2 (+ HTF up-weight only, short-halving forced off) vs. A_FULL

| Margin | Result | Detail |
|---|---|---|
| 3.1 Sharpe non-inferiority | **FAIL** | P = 0.4071; 90% CI [−0.2656, 0.0165]; corr(A2,FULL)=0.9835 |
| 3.2 CDaR ≤1.10×FULL | **FAIL** | point ratio 1.2594; bootstrap mean ratio 1.1731 |
| 3.3 Intraday DD ≤1.15×FULL | **FAIL** | ratio 1.1664 (+16.64%, exceeds the +15% cap) |
| 3.4 Retention (day AND trade) | FAIL to certify (moot) | day-leg 1.0 passes; trade-level DATA_UNAVAILABLE; margin already fails via 3.1/3.2/3.3 regardless |
| 3.5 After-cost positive | PASS | |
| 3.6 Cost-stress positive | PASS | net_stress(+1 tick/side) = $150,066.0 |
| 3.7 Annual sign-match ≥4/5 | PASS | 5/5 years |
| 3.8 Concentration gate | PASS (vacuous) | incremental advantage vs. FULL is negative (−$7,227.9 dev) |
| 3.9 Complexity reduction | **FAIL** | same reasoning as A1: 0 modules dropped (HTF stays live via `mm`), only 1 parameter (`ShortHalf`) drops |

**Overall: FAIL, decisively.** Unlike A1, A2 fails on the statistics too — Sharpe, CDaR, and intraday
DD all miss their bars — in addition to the same construction-level complexity disqualification as A1.
Read together with A1's clean statistical pass, this is the report's clearest single causal signal:
**short-halving (`ss`) looks removable on these margins; the HTF up-weight (`mm`) does not.** Removing
`mm` specifically (A2) reproduces most of A0's damage (fails the same three risk/return margins A0
fails), while removing `ss` specifically (A1) reproduces none of it. This is directionally consistent
with, and sharpens, PLACEBO01's HTF finding cited in this task's framing — but it is a statement about
which of HTF's two usages carries the value, not evidence that HTF as a whole is removable (A0, which
removes both, fails the same way A2 does).

### 2.4 Product A summary

No Product A rung passes. A0 fails outright on Sharpe/CDaR. A2 fails outright on Sharpe/CDaR/intraday-DD
plus the complexity gate. A1 clears every statistical/risk margin cleanly but is construction-ineligible
for promotion under the frozen complexity rule (and shares the trade-level data gap with every other
rung) — `02_SPEC_complexity_metric.md` determined this from construction alone, before any candidate
was scored, specifically to prevent exactly this outcome from being mistaken for a pass.
`SolarWaveSMMaster_v4.cs` (A_FULL) remains the simplest Product A construction that clears every
frozen margin.

---

## 3. Red-team findings, integrated (not just appended)

Full attack log and findings are on record in the sealed red-team report supplied to this task. The
two substantive failures found, and their effect on the verdicts above:

### 3.1 Product B intraday-DD blob defect (MEDIUM severity, confirmed, non-decision-changing)

The "Execution Product B (raw)" summary blob supplied to the Product B statistical agent duplicated
`maxDD_eod` into the `maxDD_bar_intraday` field for five cells (B0-canonical, B1-canonical, B1-dev,
B_FULL-canonical, B_FULL-dev), verified by direct diff against the authoritative
`execution_productB_raw.json` on disk. The dev-window ratios used in §1 above are the **red-team-
corrected** figures (B0/B_FULL: 1.281→1.196; B1/B_FULL: 0.927→0.936), independently re-derived from
the correct on-disk JSON. Neither correction flips a verdict: B0 still fails the 1.15 cap (1.196>1.15)
and B1 still passes it (0.936≤1.15). Root cause reads as a transcription slip in blob-authoring, not a
pipeline defect — but the blob should be regenerated verbatim from the raw JSON before being relied on
for any future closer call, since the next such call may not have this much margin to absorb the error.

### 3.2 Missing trade-level retention data (HIGH severity, applies to all 7 rungs, both products)

`01_SPEC_frozen_margins.md` §3.4 explicitly restored the trade-level leg of the retention margin
specifically because dropping it "would silently weaken an already-frozen campaign-wide standard"
(`CONVENTIONS.md` gate 6's joint AND requirement). `execution_productA.py` / `execution_productB.py`
exported only session-level daily P&L, never per-trade P&L, for any rung. This is why every row of
§1-2 above marks the retention margin "FAIL to certify" rather than a clean PASS even where the day-leg
number itself clears 0.90 — this is not this adjudicator softening the frozen rule; it is applying it:
a margin requiring A-AND-B cannot be marked PASS when B was never measured. **This finding does not
change today's headline result** (every rung already fails on other grounds, principally Sharpe/CDaR
for B0/A0/A2, and the complexity gate for A1/A2), but it means that even B1 and A1 — the two rungs that
came closest — cannot be described as "passing except for one disclosed caveat." They are missing a
required piece of frozen evidence outright.

### 3.3 A0-vs-A1 retention metric insensitivity (LOW-MEDIUM severity, informational)

Documented in §2.2 above: A0 and A1 produce numerically identical day-retention values (10+ significant
figures) because neither `ss` nor its absence touches A_FULL's own top-10 dev-window days. This does
not change any verdict (A0 already fails elsewhere; A1's day-leg pass was never the thing keeping it
out) but is worth carrying forward: this specific metric, on this specific window, has no power to
discriminate `ss` on/off, so a future task should not lean on it for that question.

### 3.4 Standing risks the red team flagged but which do not change this task's verdicts

Recorded for completeness, none decision-changing here: (i) ~50-session HTF-SMA warmup dilutes the
first ~4-5% of the dev window uniformly across every rung, including A_FULL/B_FULL — not a differential
confound; (ii) the pairwise Sharpe margin's 90% bootstrap threshold carries no family-wise correction
across the 5 simultaneously-tested non-reference rungs, and the DSR-lite context in the blind results
explicitly disclaims it is not a rigorous trials-adjusted p-value — a standing caveat for any future
closer call, and part of a longer campaign history (EQV01, PLACEBO01, GRID01, PERT01, SM11) that this
task's margins do not adjust for; (iii) a repo-wide DEV_END inconsistency (2026-05-31 vs. 2026-05-29
in different files) is confirmed harmless for this specific pipeline (both resolve to the same session
set) but remains unresolved campaign-wide; (iv) `CAPITAL_FRONTIER.md`'s disclosed P_ruin/worst-case-DD
figures, which the SPEC agent used to justify the unloosened risk margins, were taken on faith by the
red team, not independently re-audited in this pass.

**Net effect of the red-team review on this adjudication: zero verdict flips, one HIGH-severity
completeness gap (§3.2) that independently forecloses certifying ANY rung regardless of its other
margins, and one MEDIUM-severity data defect (§3.1) that is confirmed non-decision-changing but should
be fixed before it is relied on again.**

---

## 4. Complexity-based ranking among passers

**Not applicable — the passer set is empty for both products.** Per campaign directive sec42, had
multiple rungs passed, the simplest (not the highest-Sharpe) would have been preferred; the
pre-computed complexity ordering that would have applied is recorded here for completeness only:

- Product B, by ascending complexity: B0 (P=10,B=6 baseline + 0 incremental) < B1 (+2P,+1B) < B_FULL (+4P,+2B,+0.5X). B0 would have been preferred over B1 had both passed.
- Product A, by ascending complexity: A0 (P=8,B=0 baseline + 2 incremental) < {A1, A2} (each +4P,+2B, construction-ineligible for promotion regardless) < A_FULL (+5P,+3B,+1X). A0 would have been the only eligible passer among {A0,A1,A2} even if A1/A2 had cleared every statistical margin, because A1/A2 are barred from promotion by margin 3.9 on construction grounds alone.

No ranking step was actually exercised because no rung reached the point of needing one.

---

## 5. Why each ablated component appears to earn its complexity

Stated plainly, from the pattern of margin failures above, as a summary of what this task's evidence
suggests without overclaiming beyond what a single non-inferiority ladder can show:

- **Product B's B-MOM module** — removing it (B0 vs. B1) is the difference between failing four
  margins and having only one (Sharpe) land in INCONCLUSIVE with the rest clean. B-MOM looks like it is
  carrying real weight for Product B specifically.
- **Product B's HTF module** — removing it alone (B1) leaves every risk margin clean and the Sharpe
  margin in the INCONCLUSIVE band, not a clear FAIL — the closest near-miss on either ladder. This is
  directionally consistent with PLACEBO01's finding that HTF's causal contribution sits below its own
  randomized-chronology null's median for both products, cited in this task's framing as context. It
  does not confirm HTF is removable — INCONCLUSIVE is a disclosed non-pass, and the trade-level
  retention leg is separately unmeasured — but it is the one place on the whole board where "HTF may be
  earning less than its complexity" is not contradicted by the evidence gathered here.
- **Product A's HTF module as a whole (both `mm` and `ss`)** — removing both (A0) fails Sharpe and
  CDaR outright. HTF earns its complexity for Product A when considered as a unit.
- **Product A's short-halving usage (`ss`) in isolation** — removing only this (A1) passes every
  statistical/risk margin cleanly at the highest candidate/FULL correlation on the board (0.995).
  Taken at face value, `ss` looks like it contributes little on these specific margins — but A1 cannot
  be promoted regardless, because it does not drop a whole module and is barred by the frozen
  complexity gate (3.9) from ever counting as "the simpler system," by design, before any candidate was
  scored.
- **Product A's HTF up-weight usage (`mm`) in isolation** — removing only this (A2, keeping `ss` real)
  reproduces A0's failure pattern almost exactly (fails Sharpe, CDaR, and additionally intraday-DD).
  Of HTF's two usages in Product A, `mm` looks like it is where nearly all of HTF's value actually
  lives; `ss` looks close to redundant on top of it (though, per §3.3, the retention metric that would
  have been the second line of evidence for this has no power to weigh in either way).

---

## 6. What this task does and does not establish

**Does establish:**
- Under the frozen SIMPLE01 margins, no simplification of either Product A or Product B clears the
  complete, preregistered non-inferiority bar on the primary dev window (2022-01-01→2026-05-31).
- A0, B0, and A2 fail decisively on economically central margins (Sharpe and/or CDaR), not on
  technicalities.
- B1 and A1 are the two genuine near-misses, for different reasons: B1's Sharpe margin lands in the
  preregistered INCONCLUSIVE band (a disclosed non-pass, not a coin-flip judgment call); A1 clears
  every statistical/risk margin but is barred from promotion by the complexity gate itself, which was
  frozen from construction alone before any performance was known, precisely to prevent this outcome
  from reading as a pass.
- A genuine, evidence-based (not merely construction-based) attribution result: within Product A's HTF
  module, the up-weight usage (`mm`) appears to carry materially more of HTF's value than the
  short-halving usage (`ss`) does, on this ladder and this window.
- A completeness gap, applying uniformly to all 7 rungs in both products, that independently forecloses
  certifying any rung against the full frozen margin set as currently evidenced: the trade-level leg
  of the retention margin (§3.2) was never computed.

**Does not establish:**
- That A_FULL or B_FULL is "optimal," "necessary," or immune to a better-evidenced future
  simplification — only that no rung tested here clears the bar on this evidence.
- That HTF is safe to remove from Product B — B1's Sharpe result is INCONCLUSIVE, not a pass, and the
  retention margin was never fully evidenced for it either.
- Anything about NT8-executable behavior, live-fill slippage, capital-frontier interaction, or
  multi-product portfolio effects for any rung — this task is a pure backtested-analytics non-
  inferiority screen on daily P&L reconstructions, nothing more.
- **Even in a hypothetical world where a rung had passed every margin here, that would not have been a
  promotion** (campaign directive sec108-109). A passing simplification would still require the full
  battery before promotion could even be considered — for Product A: tail-risk stress, capital-frontier
  interaction, and NT8-executable proof (compiled strategy, live-parity backtest, not just the Python
  analytics twin); for Product B: the same, plus NQ/MNQ shared-core parity. **None of that battery is
  run in this task, for either product, and would not have been run even had a rung passed** — this
  task answers "can this simplification be shown non-worse on the frozen dev-window screen," nothing
  more.
- **No new baseline candidate is being proposed by this task.** Zero rungs pass, so there is nothing to
  carry forward into `research/frontier.yaml` or `research/CAMPAIGN_STATE.md` as a candidate baseline.
  A_FULL and B_FULL remain the only certified constructions for their respective products.

---

## 7. Recommended follow-ups (non-binding — this task does not authorize any of them)

1. Export per-trade P&L for all 7 rungs (reconstructable from the execution scripts' existing
   `bar_pos`/`bar_pnl` arrays per the red team's note) and re-evaluate margin 3.4 in full for B1 and A1
   specifically — the two rungs where every other margin is either passing or inconclusive-not-failing,
   and where this is the only genuinely open question left.
2. Regenerate the Product B intraday-DD blob verbatim from `execution_productB_raw.json` before it is
   reused for any future call closer than this one.
3. If HTF's marginal Product-B value remains a live question, a dedicated higher-power test targeting
   B1-vs-B_FULL specifically (longer window if one becomes available without touching CONSUMED or
   VIRGIN territory, or a design with lower candidate/FULL correlation sensitivity) would resolve the
   current INCONCLUSIVE more decisively than repeating this same test would.
4. A1's clean statistical result is worth carrying into a future causal-attribution task (extending
   PLACEBO01) even though it cannot be a SIMPLE01 promotion candidate — the finding that `mm` and `ss`
   contribute unevenly to Product A's HTF value is new and specific.

---

*Inputs to this adjudication: `00_SPEC_candidate_manifest.md`, `01_SPEC_frozen_margins.md`,
`02_SPEC_complexity_metric.md` (all frozen pre-performance), `out/statistical_family1_blind.json`
(Product B), `out/statistical_family2_blind.json` (Product A), the sealed red-team report, and the
label-mapping key supplied at un-blinding. No new computation was run in this task; all figures above
are read from the sealed inputs (red-team-corrected where the red team found and confirmed a specific
transcription defect, per §3.1).*

---

## 8. ADDENDUM — Completion pass (closes §3.1 and §3.2's two open gaps; §7 item 1-2 executed)

**Status: additive only.** Nothing above this line is edited, retracted, or reinterpreted. This
addendum executes the two follow-ups §3's red-team review left open — the missing trade-level leg of
margin 3.4 (§3.2 above, HIGH severity) and the Product-B intraday-DD blob defect (§3.1 above, MEDIUM
severity) — against a preregistration frozen and committed *before* either gap was computed
(`out/03_SPEC_completion_pass_preregistration.md`, commit `6ffe82d`), per the practice this program
adopted 2026-08-10. No margin, window, threshold, bootstrap, or complexity rule from
`01_SPEC_frozen_margins.md` / `02_SPEC_complexity_metric.md` is touched, loosened, or re-derived here.
Method, code, and full numeric output: `src/04_completion_pass.py`, `out/completion_pass_results.json`.

### 8.1 Headline answer, stated plainly first

**Nothing flips to an overall PASS.** All 5 rungs (A0, A1, A2, B0, B1) still FAIL the complete frozen
non-inferiority ladder, exactly as this report's original headline said. This is not a foregone
conclusion — it was checked, not assumed — and it is exactly what the data show.

The one place the newly-completed evidence *does* change something: **margin 3.4 (retention) is now
fully certified, in both directions, for every rung** — where §1-2 above could previously only say
"FAIL to certify" (day-leg passed, trade-leg never measured) for A0, A1, and B1:

| Rung | Day-leg (already known) | Trade-leg (NEW) | Margin 3.4 now | Previously reported as |
|---|---:|---:|---|---|
| A0 vs A_FULL | 0.9018 (pass) | 0.8938 (**fail**, <0.90) | **FAIL** | "FAIL to certify" |
| A1 vs A_FULL | 0.9018 (pass) | 0.8507 (**fail**, <0.90) | **FAIL** | "FAIL to certify" |
| A2 vs A_FULL | 1.0000 (pass) | 0.9675 (pass) | **PASS** | "FAIL to certify (moot)" |
| B0 vs B_FULL | 0.8131 (already fail) | 0.7387 (fail) | **FAIL** | FAIL (day-leg alone already failed it) |
| B1 vs B_FULL | 0.9941 (pass) | 0.9132 (pass) | **PASS** | "FAIL to certify" |

For A0, A2, and B0 this is moot — all three were already blocked on other, independent grounds
(Sharpe/CDaR for A0/B0, Sharpe/CDaR/intraday-DD for A2), so completing margin 3.4 changes their
evidence record but not their verdict. **A1 was already blocked by the construction-level complexity
gate (3.9)** regardless of statistics, so its new trade-leg FAIL is likewise moot to its outcome. **B1
is the one rung where this newly-computed leg is not moot**: its day-leg already passed (0.9941) and
its trade-leg now also passes (0.9132) — margin 3.4 moves from "FAIL to certify" to a genuine,
fully-evidenced **PASS** for B1. That narrows B1's sole remaining blocker to margin 3.1 (Sharpe), which
stays **INCONCLUSIVE**, unchanged (no new bootstrap was run in this pass — that number is not
recomputed here). **B1 therefore still does not pass the full margin set: INCONCLUSIVE is a
preregistered non-pass, so B1's overall verdict remains FAIL, exactly as originally reported.**

**Direct answer to "does this change B1's or A1's status": no.** B1's overall verdict is unchanged
(FAIL, both before and after) — what changed is *why*: it now fails on exactly one clean, well-evidenced
margin (Sharpe, INCONCLUSIVE) instead of two margins including one that could not previously be fully
evidenced. A1's overall verdict is unchanged (FAIL, both before and after) for an unrelated, independent
reason that this pass does not touch: construction-level complexity (margin 3.9), which the trade-level
result does not affect either way.

### 8.2 What was computed, and how (method summary; full detail in `completion_pass_results.json`)

- **Gap 1 (trade-level retention leg of margin 3.4).** Per-trade P&L was reconstructed for all 7 rungs
  directly from the `bar_pos`/`bar_pnl` arrays already computed by the byte-for-byte-reused rung
  construction functions in `src/execution_productA.py` / `execution_productB.py` (verified bar-for-bar
  identical to `grid_core`'s own reference execution, and dev-window net reproduces the certified
  $177,924.40 / $301,915.92 figures exactly — both integrity gates pass). A trade = a maximal contiguous
  run of nonzero, same-signed `bar_pos`; trade P&L = `sum(bar_pnl)` over that run — the definition frozen
  in the preregistration, itself a mechanical instantiation of `CONVENTIONS.md` gate 6 ("top-1% trade
  P&L retention ≥ 90% ... vs baseline"), quoted verbatim in the code and reproduced here:

  > 6. HARD RIGHT-TAIL GATE for anything that modifies Solar exposure or exits: top-1% trade P&L
  > retention ≥ 90% AND top-10 day retention ≥ 90% vs baseline; any state down-weighted below baseline
  > must hold top-1% P&L share ≤ its session share.

  Retention ratio = (candidate's own trade P&L, summed over trades occurring on the same dates as
  FULL's own top-1%-by-P&L trades) ÷ (FULL's own top-1% trades' P&L sum) — the day-level
  `top10_day_retention()` pattern generalized from day-index to trade-date, per the preregistration.
  `k = max(1, floor(0.01 × n_trades_FULL))`, matching the house CDaR truncation convention; this is the
  one implementation-level choice not otherwise specified by the frozen spec, and it is disclosed as
  such (`TOP1PCT_K_RULE` in the output) rather than silently picked. Gate 6's third clause ("any state
  down-weighted below baseline must hold top-1% P&L share ≤ its session share") is quoted but **not**
  separately operationalized: it targets continuous down-weighting of individual Solar member states,
  and SIMPLE01's ladder is an all-or-nothing whole-module ablation (`mm`/`ss`/`bmomPos` forced to a
  constant or left fully real) with no intermediate "down-weighted" state for the clause to attach to —
  this is disclosed in the output (`notes_on_gate_6_third_clause`) rather than fabricating a formula for
  a case the clause does not describe.
- **Gap 2 (Product-B intraday-DD blob defect).** Every `maxDD_bar_intraday_MTM_proxy` cell was
  regenerated by direct programmatic read of `execution_productB_raw.json` (the authoritative source),
  never hand-transcribed. Corrected dev-window ratios: **B0/B_FULL 1.281 → 1.196207** (still exceeds the
  1.15 cap — still FAIL) and **B1/B_FULL 0.927 → 0.935889** (still clears the 1.15 cap — still PASS).
  The red team's restated corrected figures were independently reproduced from source, not merely
  trusted. Product A's raw-JSON intraday-DD ratios were cross-checked against this report's §2 figures
  and found to already match exactly — no defect found on the Product A side. **Neither correction flips
  any margin 3.3 PASS/FAIL, for either product.**
- **A material implementation finding, disclosed rather than silently absorbed.** This substrate's
  execution loop books a closed position's exit fill (commission + adverse-tick realization) on the bar
  *immediately after* `bar_pos` returns to 0 (a "signal evaluated on bar t, executed at bar t+1's open"
  convention). Taken literally, the frozen trade definition ("maximal contiguous run of *nonzero*
  `bar_pos`") therefore excludes each trade's own exit cost from its own reconstructed P&L — a real
  property of this substrate's bar-level fill timing, not a reconstruction bug, and worth ≈4-9% of each
  rung's dev-window net summed across trades. The literal definition is used as PRIMARY (it is what the
  preregistration froze), alongside a disclosed exit-inclusive robustness variant (identical trade
  boundaries, count, and dates; absorbs the deferred exit-fill bar into its own trade). **Both variants
  agree on every single PASS/FAIL, for all 5 rungs** (e.g. B1's trade-leg retention: 0.9132 literal vs.
  0.9122 exit-inclusive — both ≥0.90) — the conclusion is not an artifact of this bookkeeping nuance.

### 8.3 Full updated verdict table, all 5 rungs (supersedes nothing in §1-2 above — this is the
completed version of the same table)

| Rung | 3.1 Sharpe | 3.2 CDaR | 3.3 Intraday DD (corrected) | 3.4 Retention (day AND trade, now complete) | 3.5-3.8 | 3.9 Complexity | **Overall** |
|---|---|---|---|---|---|---|---|
| A0 vs A_FULL | FAIL | FAIL | PASS (1.046) | **FAIL** (trade 0.894<0.90) | PASS | PASS | **FAIL** (unchanged) |
| A1 vs A_FULL | PASS | PASS | PASS (0.879) | **FAIL** (trade 0.851<0.90) | PASS | FAIL | **FAIL** (unchanged) |
| A2 vs A_FULL | FAIL | FAIL | FAIL (1.166) | **PASS** (trade 0.967) | PASS | FAIL | **FAIL** (unchanged) |
| B0 vs B_FULL | FAIL | FAIL | FAIL (1.196, corrected) | **FAIL** (day 0.813 already <0.90) | PASS | PASS | **FAIL** (unchanged) |
| B1 vs B_FULL | **INCONCLUSIVE** | PASS | PASS (0.936, corrected) | **PASS** (trade 0.913, newly certified) | PASS | PASS | **FAIL** (unchanged — INCONCLUSIVE is a non-pass) |

**Zero rungs pass overall.** This is the same null result §0/§1-2 already reported, now with every
margin's evidence complete for every rung rather than one leg of one margin outstanding.

### 8.4 Standing caveat restated (campaign directive sec108-109) — even where 8.3 shows a clean PASS row

**No rung here passes every margin, so this caveat does not have anything to apply to today** — restated
in full regardless, because it is the standing rule for this whole program and because a reader
skimming the 8.1 table alone could otherwise mistake B1's or A2's new margin-3.4 PASS for a promotion
signal: **passing this (or any) non-inferiority ladder does not auto-promote anything.** Per this
report's own §6 ("Does not establish," restated, not superseded, by this addendum): even in a
hypothetical world where a rung cleared every single frozen margin, that would not itself be a
promotion. A passing simplification would still require the full battery — tail-risk stress,
capital-frontier interaction, and NT8-executable proof (a compiled strategy, live-parity backtest, not
just this Python analytics twin), plus, for Product B, NQ/MNQ shared-core parity — before promotion
could even be considered. **None of that battery is run in this addendum, for any rung, and would not
have been run even had a rung's overall verdict flipped to PASS.** This task, both originally and in
this completion pass, answers only "can this simplification be shown non-worse on the frozen dev-window
screen" — nothing more.

### 8.5 What changed in this document as a direct result of this pass

- §1.2 (B1) and §2.1-2.2 (A0, A1)'s "FAIL to certify" / "DATA_UNAVAILABLE" retention rows are now fully
  evidenced (see 8.3); their *overall* verdicts (FAIL, FAIL, FAIL) are unchanged.
- §3.1's red-team-corrected DD ratios (1.281→1.196, 0.927→0.936) are independently reproduced by direct
  computation from source, not merely carried forward on trust.
- §3.2's HIGH-severity completeness gap is closed: the trade-level leg is now computed and reported for
  all 7 rungs.
- §7 items 1 and 2 (recommended follow-ups) are executed by this addendum.
- No figure in §1, §2, §3, §4, §5, §6, or §7 above is edited or retracted — this addendum only adds the
  previously-missing evidence and restates the resulting (unchanged) verdicts.

*Inputs to this addendum: `out/03_SPEC_completion_pass_preregistration.md` (frozen and committed before
either gap was computed), `src/execution_productA.py` / `execution_productB.py` (rung construction
reused verbatim), `out/execution_productA_raw.json` / `out/execution_productB_raw.json` (authoritative
source for the DD-blob fix and cross-checks), `research/system_master/CONVENTIONS.md` (gate 6, quoted
verbatim), and this report's own §1-§2 (unchanged margins quoted, not recomputed). Full numeric output,
including every integrity cross-check referenced above: `out/completion_pass_results.json`. Generated by
`src/04_completion_pass.py`.*
