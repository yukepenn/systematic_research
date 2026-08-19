# MONITOR-02 — Program-B combined forward re-read protocol

**Written and committed 2026-08-18, BEFORE any forward data has been read** (first eligible read
≥ 2027-08-01). This closes a documentation gap: the scalping-lab phase-end ledger scheduled a
"Program-B combined re-read (MONITOR-02)" but no protocol document existed. Nothing here is new
tuning — every verdict rule below is the already-frozen rule from the campaign's own specs,
referenced, not re-derived. The owner may amend this document at any time BEFORE the first read;
after the first read it is frozen like every other read protocol.

## Scope

The three PARKED (0 frozen) Program-B candidates from the scalping-lab campaign
(`research/scalping_lab/ALPHA_SCOREBOARD.md` PHASE END table, `registry/hypothesis_ledger.csv`):

| Candidate | Parked as | Frozen rule source |
|---|---|---|
| B-MOM (14-day noise band + RTH VWAP intraday momentum) | REGIME-LOCAL (2022+ edge shares Solar's regime fuel; no pre-2022 structure; ρ_full 0.347 vs <0.3 gate) | W8-1 spec (rule frozen, zero changes) + W10 verdict |
| B-FADE (08:30-release reaction fade) | POSSIBLY-RECENT (OOS 2006-21 = 1/30th of IS) | W8-2 / W9-3 amended four-way rule (`specs/W9_nq_minute_resolutions.md`) |
| B1 overnight (long last-bar ≤16:45 → next 09:30) | MARGINAL (letter-pass, bootstrap under-converged at 10k reps; top-10 nights 53%) | W5-B1 construction + W9-1 amended decay-aware rule |

## Data

Forward window only: sessions ≥ 2026-08-01 (LOCKED_FORWARD virgin era), accumulated through the
read date. This is an **evaluation read, not selection**: rules are frozen; no parameter may be
touched before, during, or after the read. Minimum accumulation before the primary read:
**12 months of forward sessions** (hence ≥ 2027-08-01). Substrate: same construction code as the
frozen specs (minute/3-min as each rule specifies), built by extending the existing pipelines.

## Frozen verdict rules (referenced, unchanged)

1. **B-MOM**: re-run the frozen W8-1 rule on the forward window. UNPARK-CANDIDATE iff forward
   net C1 CI_lo > 0 (day-clustered, seed 20260808 convention) AND forward ρ vs the Solar ledger
   < 0.3 (the original gate — the W10 finding withdrew any relaxation) AND the forward Solar-leg
   regime is not the sole driver (report the ρ split: full vs losing-day). Anything less: remains
   parked; CI_hi < 0 on ≥12 months: CLOSED.
2. **B-FADE**: apply the W9-3 amended four-way rule to forward release days (~2/month accrual;
   report power explicitly — at ~24-30 events the read may be UNDERPOWERED, which is a recorded
   outcome, not a verdict).
3. **B1 overnight**: apply the W9-1 amended rule (power, no-negative-trend, recent-block point
   estimate, ρ < 0.3) on forward nights, PLUS the W9 orchestrator ruling: the bootstrap must be
   run at ≥10,000 reps and the CI at that precision governs; concentration check (top-10 nights
   share) reported.
4. **Joint report**: one document, `research/operational/monitor02_reading001.md` pattern;
   registry rows appended in `research/scalping_lab/registry/tested_configs.csv` (S36+); results
   also cross-recorded in the system_master wave log if any candidate unparks (an unparked
   candidate enters the standard engine-#3 gate battery in `COMPLEMENTARY_ENGINE_FRONTIER.md` —
   unparking is NOT promotion).

## Relationship to other seals

- Consumes nothing historical; reads only ≥2026-08-01 data, which LOCKED_FORWARD reserves for
  exactly this class of scheduled, preregistered evaluation (MONITOR-01 precedent).
- Does not touch the SYSTEM_MASTER B1 *challenger* (drop-HTF Product-B variant) — that object's
  confirmation is governed separately by `research/system_master/B1_FUTURE_CONFIRMATION_SPEC.md`.
  The name collision is documented in CURRENT_TRUTH's corrections index.
