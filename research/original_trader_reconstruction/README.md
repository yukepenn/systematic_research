# ORIGINAL TRADER RECONSTRUCTION (OTR) — Campaign #6

**Opened 2026-08-23 under OWNER MASTER DIRECTIVE v1.0 (2026-08-23). This is the SOLE active
research mission. All prior products/campaigns are frozen reference material only.**

## Mission

Reconstruct as faithfully as possible the original NQ systematic trader who inspired the
Solar research program. This is SYSTEM IDENTIFICATION / REVERSE ENGINEERING, not return
maximization. The primary question: *what was this trader actually running, how did it
evolve, what mechanics explain observed behavior, and can we reproduce the observed
historical fingerprints from our existing data?* Only after faithful reconstruction do we
ask whether it remains economically profitable under realistic costs.

## Non-negotiables (from directive §1)

- Historical research only. NO live trading / broker / Sim101 / Playback / realtime
  recorder / CrossTrade.
- Respect LOCKED_FORWARD (≥2026-08-01 virgin) — reconstruction must not consume sealed
  data; already-consumed history may be used freely for reconstruction (NOT as "pristine OOS").
- Prior closed-campaign conclusions ("no more alpha", "space exhausted") are NOT reasons to
  stop — they answered different questions.
- Never fabricate missing labels/parameters/formulas. Four evidence classes strictly
  maintained: CLASS A (directly observed) / B (validated by prior research) / C
  (high-confidence inference, labeled) / D (unknown). Never silently promote C/D → A.
- A candidate matching net PnL but wrong on trade count / WR / hold / payoff / DD / side
  behavior is NOT a successful reconstruction (§17). Reproducing the LOSSES (esp.
  2026-03-22→03-27, −$42,235) matters as much as the winners (§20, §29).
- Do not force every screenshot into one strategy — the author ran MULTIPLE strategies (§18).
- Notes posts that mirror a report are ONE observation with two artifacts, not two samples (§25).
- Do not optimize the trader into something else (§47). Net PnL is a MEDIUM-priority
  fingerprint; count/frequency/WR/PF/hold/payoff/DD are HIGH.

## Strategy families (see FAMILY_MAP.md)

| Track | Family | Status |
|---|---|---|
| S | SolarWindRKSelTime (early, 2023-2025, 90/179/5/10/10) | ACTIVE — first priority |
| SD | RKSelTimeDSTM… + LossLimit 2500/4000 | queued (Phase 4) |
| V | Volume/VWAP/RealVolume (2026, params fully visible) | queued (Phase 6-7, data-gated) |
| B | Unknown multi-block | queued (Phase 5) |
| P | Multi-strategy / account combination | queued (Phase 9) |

## File map

- `AUTHOR_STATEMENTS.md` — direct author statements (Class A evidence)
- `EVIDENCE_LEDGER.csv` — every screenshot-derived observation
- `TARGET_WINDOWS.csv` — all fingerprint target windows with full metrics
- `AUTHOR_REPORTED_NQ_RESULT_TIMELINE.csv` — §24 weekly timeline (NOT one-strategy YTD)
- `FAMILY_MAP.md` — family definitions, knowns/unknowns
- `IDENTIFICATION_OBJECTIVE.md` — reconstruction-distance score + tolerance bands
- `HYPOTHESIS_LEDGER.csv` — every tested hypothesis (multiple-testing control, §34)
- `RECONSTRUCTION_SCORECARD.md` — side-by-side ORIGINAL vs REPLICA per candidate
- `COST_MODEL.md` — Layer-1 screenshot parity vs Layer-2 economic reality (§28)
- `UNKNOWN_FIELDS.md` — Class-D registry (cropped tokens, unknown semantics)
- `DATA_AUDIT.md` — substrate coverage vs target windows, per-window feasibility
- `CURRENT_TRUTH.md` — campaign chronology (prepend-newest)
- subdirs: `solar_family/ solar_dstm_family/ volume_vwap_family/ multiblock_family/
  account_combination/ ninjatrader_parity/ final/`
- Run prefix: `OTR` under `runs/`

## Phase plan (directive §51)

0 evidence bootstrap → 1 campaign structure/ledgers/data audit → 2 reproduce Type-1
baseline → 3 Track S wrapper (arbitration/pullback/SelTime/exit/re-entry) → 4 Track SD
LossLimit → 5 Track B identification → 6 real-volume data audit → 7 Track V → 8
cross-window validation → 9 Track P account layer → 10-11 NinjaScript + parity → 12 cost
reconciliation → 13 historical stress → 14 final package.

Stopping per family (§49): high-confidence reconstruction, OR three meaningfully different
mechanism passes without frontier improvement, OR blocked by missing data/source. Final
classifications (§40): RECONSTRUCTED–HIGH / RECONSTRUCTED–MODERATE / PARTIALLY /
BEHAVIORALLY MATCHED MECHANISM UNIDENTIFIED / BLOCKED BY MISSING DATA / REJECTED.
