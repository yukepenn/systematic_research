# FINAL SYSTEMATIC RED TEAM — the consolidated case against the system

_DRAFT 2026-08-07 · branch `post_campaign_audit`. This document aggregates every objection that
survived the campaign red team (`reports/final_red_team.md`,
`research/06_red_team/RED_TEAM_WAVE1C_WAVE2.md`), the audit's independent second red team
(`research/audit/SECOND_RED_TEAM.md`), and the post-audit waves. The campaign rule stands: the
agent that produced a candidate may not be its only reviewer. Nothing below is softened by the
champion's headline numbers; several items cannot be remedied by any amount of wording._

## 1. Standing dissent items from the second red team (§4 — "not remediable by wording")

1. **The E10 pass margin IS thin: 0.003–0.012 Sharpe across the passing rule/basis combinations.**
   If the MNQ fee schedule worsens by ≥$0.10/side, the champion fails its own preregistered gate.
   The economics, not the tracking, are the binding constraint (E13, perfect tracking, fails by
   0.016). The system's executability is one broker price change away from unproven.
2. **The audit's preregistration lead times are minutes, not days.** Procedurally clean, and
   acceptable for reproduction runs where the expectations are already-committed campaign
   ledgers — but epistemically thin for anything else. The audit's certainty is about
   reproduction, not discovery.
3. **Tick-level intraday excursion is unmeasured.** The −$42,204 bar-level TRUE_MTM drawdown
   (R5 theoretical) is itself only a lower bound: 3-minute bar-close marking bounds the true
   tick-level excursion from below by an unmeasured margin. No committed number bounds it from
   above.

## 2. Surviving objections from the campaign red team (`final_red_team.md` §3/§5)

4. **R5 was never shown better than R4.** ΔSharpe +0.087, P(Δ ≤ 0) = 0.358; ex-2025 the entire
   advantage is +0.046. Adaptive underperforms fixed in the low-volatility tercile — the opposite
   of its claimed mechanism. The audit resolved the ranking by execution economics, not by
   statistics; the statistical question remains unresolved forever on this sample.
5. **64% of net comes from ten days.** $198,059 becomes $71,923 (36%) without them. The top 1% of
   trades carry ≈160% of net; the bottom 99% lose money in aggregate. Every dollar of headline
   Sharpe is rented from a handful of sessions that no risk model in this package can predict.
6. **The edge is ~3% from a no-alpha null.** A driftless diffusion gives E[ω] = δ exactly; the
   whole campaign rests on r exceeding 1.0 by about three percent. There is no version of this
   system with a margin of safety.
7. **Deflation cannot certify it.** DSR 0.45–0.55 against the 0.90 bar under the preregistered
   rule; Harvey–Liu haircut Sharpe 0.000; a defensible alternative variance pool gives 0.96. The
   answer is dominated by a judgement call — which cuts against the system exactly as much as
   for it.
8. **No clean out-of-sample window exists and none can be manufactured.** All data through
   2026-07-31 was consumed in discovery. Every "robustness" figure is in-sample robustness.
9. **The short side is dead weight** (ex-2022/2025: −$8,397, Sharpe −0.113). The system is a
   long-NQ tail-harvester with a symmetric costume.
10. **The pattern of the campaign is itself an objection: every absolute-edge test passed and
    every comparative test failed** (`registry/hypotheses.md`, final entry). On 4.6 years of one
    instrument, the data supports "something is here" and refuses every ranking question. A
    reviewer may reasonably read that as "the sample cannot distinguish skill from one regime."

## 3. Post-audit falsifications — new, and worse than the old objections

11. **External portability is refuted, 0-for-4.** ES −$12,455, YM −$21,947, RTY −$17,006,
    CL −$12,218; on CL not one of 13 cells is positive; RTY/CL shape correlations are
    statistically zero (`PORT01_VERDICT.md`). This is no longer a missing test — it is four
    completed tests, all negative, under a preregistered ≥2/3 rule. The mechanism, as
    implemented, lives on one instrument. The candidate mechanical explanation (NQ's lowest
    friction-per-sigma) is itself unflattering: it implies the "edge" may be partly a
    friction-geometry artifact that only NQ's tick structure permits.
12. **Family B is falsified — no diversification exists.** All DR-05 high-value arms resolved
    negative (H1(b) FAIL, H2 dead unbuilt, H3 FAIL −$22,534, H4 dead by dependency, H5
    null-rejected then escalation FAIL 3/6 with a 90.1% top-1% concentration and a stopless
    −$8,544 left tail). The delivered "portfolio" is one family, one instrument, one era, one
    tail. The mandate's endpoint was a multi-family portfolio; the stop condition fired first.
    That is a legitimate stop, not a result.
13. **Single-instrument, single-era dependence.** 2022–2026 NQ contains one bear year inside a
    secular AI-driven bull market in the very index the system trades. 8 of the top-10 days are
    in 2025–26. The system has never seen a regime its own tail did not eventually rescue.

## 4. Process and governance objections

14. **Registry-gap discount for Waves 1c–3.** The entire Wave 1c → 3 program (139 of 229 R1
    trials) ran in a 5.5-hour window with zero contemporaneous registry writes. Reproducible from
    committed ledgers, but spec-before-result is not verifiable; the backfill's own counting is
    internally inconsistent (strict relabel 295–335 vs the committed 229; `WAVE3_report.md`
    counts H-014 as 13 trials, the backfill as 1). The campaign's central positive structural
    claim — "ensembles beat selection" — is the finding most exposed, downgraded from
    "campaign-complete" to "complete over the surviving committed evidence"
    (`research/audit/REGISTRY_GAP_ASSESSMENT.md` (c)).
15. **Vendor P0 human actions are still pending.** The licensed RenkoKings DLL remains reachable
    in git history on every branch, and the remote `research-campaign` tip still tracks the full
    vendor package (private repo is the only mitigation). Two public-exposure windows
    (≈12.5h + ≈10h) already occurred. History erasure (filter-repo + force-push + GitHub GC) and
    the `research-campaign` tip remediation are HUMAN ACTION REQUIRED
    (`research/audit/VENDOR_BINARY_REMEDIATION.md`). Until then the program carries an unresolved
    licensing/governance liability unrelated to, but attached to, the research.
16. **The E10 designation was a design choice made by the audit**, from a menu {E13, E10, E20}
    the thesis did not enumerate, recorded as a design-choice event with committed sensitivity
    (all alternates published with FAIL verdicts; round/floor × session/calendar 4/4 pass). The
    disclosure is complete; the residual fact remains that the one passing discretization is the
    one that was designated.
17. **No master-strategy implementation exists.** The champion's numbers come from a Python
    simulator over member ledgers, not from a compiled NT8 strategy placing E10's net-change
    orders. The implementation gap between "audited simulation" and "runnable strategy" is
    exactly where execution surprises live.

## 5. The two arguments, stated as strongly as the evidence allows

**Strongest argument the system is NOT real:** it is a tail-harvesting artifact of one
instrument's friction geometry in one mostly-bull era — the edge is a ~3% deviation from a
martingale null that transfers to zero of four external markets, loses its statistical
significance the moment any comparative question is asked, concentrates 64% of its profit in ten
days clustered late in the sample, cannot be certified by any deflation procedure, has no second
family to corroborate its mechanism economically, and clears its executability gate by 0.003
Sharpe on a fee schedule the broker can change tomorrow. Every one of those clauses is a
committed, quantified finding of this program's own record.

**Strongest argument it IS real:** the mechanism was confirmed by the campaign's one clean
preregistered control — volatility-normalization beats price-normalization by +0.728 Sharpe at
p = 0.009, a *dissimilar-family* comparison that noise cannot easily produce — sitting on top of
an absolute-edge bootstrap of P(Sharpe ≤ 0) = 0.0020, an overshoot excess present at every
threshold (t up to 31) independent of any strategy, positivity in all five years including the
2022 bear year, fill-by-fill reproducibility from a clone, proven TRUE_MTM accounting, a
fill-model-independent right tail, survival of 2-tick slippage at 87.4% retention, and an
ensemble that beats all 13 of its own members without selecting anything. Nothing in the record
falsifies the NQ edge itself; everything merely bounds how far it extends.

The honest synthesis is the one already frozen into the decision document: **best robust
historical system found under the defined research universe and evidence constraints — and
nothing more.** Not forward-validated, not deployment-ready, no clean OOS, portability refuted.
