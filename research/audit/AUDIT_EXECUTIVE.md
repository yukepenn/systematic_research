# POST_CAMPAIGN_AUDIT_01 — executive summary

_2026-08-07 · branch `post_campaign_audit` (from campaign HEAD `e5079e1`) ·
constitution: Research_Thesis.txt v2 (`3bc5a3a`) · executed and adversarially
reviewed same day · **zero new R1 trials consumed**._

## Verdict: PASS

All twelve pass criteria of the audit specification are met. The campaign's core
evidence is genuine, deterministic, and now reproducible from a clone; its two
headline candidates are separated for the first time by execution economics; and
the whole package survived an independent four-lens adversarial review
(`SECOND_RED_TEAM.md` — every headline number independently recomputed, exact).

## The seven results that matter

1. **R5 is real and reproducible.** All 13 members re-executed **fill-by-fill
   identical** to the committed ledgers. One recipe defect found and fixed: the
   published reproduction recipe said `StartUp=true`; the truth is `false`.
2. **The published V3/V4 analysis was confounded** — the two committed ledger sets
   differed in StartUp as well as the tick-snap. Both reproduce exactly under
   their as-run configs; the clean comparison upholds the published conclusion:
   trade paths NOT_EQUIVALENT (members to −49%), ensembles PERFORMANCE_SIMILAR_ONLY
   (corr 0.9952, ΔSharpe +0.019, CI [−0.064, +0.094]).
3. **Published risk metrics were honest at their granularity.** Session-realized
   P&L IS true MTM (proven to the cent, all 34 members). New disclosure: bar-level
   intraday max DD is deeper — R5 −$42,204 (vs −$39,126 daily), R4 −$39,494
   (vs −$35,669); 3-minute marking still bounds tick-level excursion from below.
4. **R5 is executable; R4 is not (at acceptable cost).** E10 — round(10 × mean
   member position) MNQ, max 10 — retains 90.6% of net, ΔSharpe −0.097 (gate
   −0.10; pass margin thin but robust across round/floor × session/calendar
   bases, 4/4). Every discrete R4 variant fails by 0.17–0.24. The penalty is
   entirely the MNQ commission multiple ($1.30/RT × 10 vs $4.36/RT, verified
   empirically); rounding granularity is a non-issue (corr 0.9985, top-10-day
   retention 98.6%).
5. **Cost claims corrected by measurement**: slip-2 retains 87.4% of R5 net (not
   "half" — that language belonged to high-turnover plateau cells); slip-3 ≈ 75%
   floor. Paths are slippage-invariant.
6. **No fill artifact.** High Order Fill Resolution changes ≤1.1% of net
   (favorable on balance); the right tail is fill-model-independent; Standard is
   conservative.
7. **Governance**: the repository was found PUBLIC again with the vendor package
   still TRACKED at HEAD — re-privatized, untracked at tip, ignore-guarded,
   SHA-256 evidence manifests committed. History erasure and the
   `research-campaign` remote tip remain **HUMAN ACTION REQUIRED**
   (`VENDOR_BINARY_REMEDIATION.md`).

## Frozen going forward

**Family-A reference = executable R5-E10** (13 × SolarWaveOpenV3 virtual members,
StartUp=false, ThresholdMode 1, VolPeriod 460, clamp 40–1200 ticks, VolMult 6–30;
target = round(10 × mean position) MNQ; net-change execution; session-close
flatten; TRUE_MTM Sharpe 0.9671, net $179,361). Theoretical R5 is its research
proxy (corr 0.9985). R4-21 = theoretical robustness benchmark only. Solar
parameter optimization stays closed.

## What the audit does NOT establish (unchanged)

No clean OOS exists; ES portability remains failed; the top 1% of trades still
carries ~160% of net; the short side has no standalone edge; DSR remains
inconclusive under the preregistered rule; nothing here is forward-validated or
deployment-ready. The strongest honest claim is unchanged in kind and stronger in
degree: *best robust historical system found under the defined research universe,
now with verified reproducibility and a costed executable form.*

## Transition

POST_AUDIT_TRANSITION is active per the constitution: RESEARCH_WAVE_B01
(failed directional change + value reacceptance) is preregistered
(`research/04_complementary_family/B01_WAVE_SPEC.md`) with Family-B comparisons
against executable R5-E10 (primary) and theoretical R4 (secondary — its
executable form failed gates; adaptation flagged in NEXT_HANDOFF.md).
Roadmap: `NEXT_RESEARCH_ROADMAP.md`.
