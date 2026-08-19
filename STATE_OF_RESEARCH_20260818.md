# STATE_OF_RESEARCH — repo-wide consolidation, 2026-08-18

**What this is:** the one-stop current-state map across all four campaigns, produced by a
repo-wide audit (7 parallel area audits + adversarial verification of every claimed
contradiction/staleness, 14 agents, all findings verified against files before use). It is a
**dated snapshot**: `research/system_master/CURRENT_TRUTH.md` remains the running per-wave log
and outranks this file the moment a new wave lands. Every claim here cites where it lives; when
in doubt, follow the pointer, not this summary.

---

## 1. One-screen state

- **Mode: RESEARCH.** No live-trading authorization exists for any object; all research
  NinjaScripts fail closed in realtime. (README.md / BASELINE_MODELS.md)
- **Three shipped baseline objects** (campaign #3), all frozen, byte-identical since 2026-08-09,
  **zero promotions across every wave since** — ~200+ constructions tested and closed with
  discipline. That is the finding, not a stall: the incumbents are robust to five waves of
  adversarial search.
- **Campaigns:** #1 Solar Wave CLOSED 2026-08-07 (frozen champion under quarterly MONITOR-01);
  #2 audit CLOSED 2026-08-07; #3 SYSTEM_MASTER **ACTIVE** (last wave 2026-08-14: HTFMECH01
  closed, frontier re-ranked; next item READY, not started); #4 Scalping Lab **PHASE COMPLETE**
  2026-08-08 (Zone F closed per §34; Program B = 3 parked / 0 frozen; dormant pending forward
  data).
- **DOM / Level-II / Market Replay: PAUSED** since 2026-08-12 (owner risk-control after a
  workstation instability incident). Fail-closed collector; resume only on explicit recorded
  owner re-authorization. Baselines do not depend on DOM by design.
  (`research/system_master/DOM_PAUSE_CLEANUP_20260812.md`)
- **Data honesty:** no pristine historical OOS exists anywhere through 2026-07-31 (SM11 consumed
  the last sealed window on 2026-08-08, for every sleeve). The only virgin data is
  **≥ 2026-08-01**, accruing one quarter per quarter, reserved for scheduled preregistered reads.

## 2. The objects

| | Product A | BEST_ONE_NQ | BEST_ONE_MNQ |
|---|---|---|---|
| File | `src/ninjascript/SolarWaveSMMaster_v4.cs` | `SolarWaveOneContractNQ_v5.cs` | `SolarWaveOneContractMNQ_v5.cs` |
| Net / Sharpe (Python ref, dev 2022-01-03→2026-05-29) | $177,924.40 / 1.1770 | $301,915.92 / 1.1131 | $28,587.10 / 1.0534 |
| NT8 parity | +10.91% residual, EXEC01 leg-audit 1,371/1,371 exact, ~97.8% attributed | +4.13%, fully reconciled | +4.41%, fully reconciled |
| EQV04 canonical parity (2026-08-11) | bit-identical (165,861 bars) | to-the-cent | to-the-cent |
| Health (2026-08-09 reading, data→07-31) | NORMAL_WEAK_REGIME; one 10-13-band POSSIBLE_DECAY flag (re-check at ~1,000 bars) | HEALTHY; rolling-120 WATCH flag (mechanically explained) | same core |

Authority: **`/BASELINE_MODELS.md`** (+ its 2026-08-18 EXEC01/EQV04 annotation). Health:
`research/system_master/CURRENT_EDGE_HEALTH*.md`. Architecture: B-NQ/B-MNQ are two execution
adapters over ONE shared decision core (Solar13 + HTF tilt + B-MOM + hysteresis); Product A is a
related continuous-sizing construction, not a third adapter.

**Dual-champion bookkeeping (worth knowing, not a defect):** campaign #1's frozen champion
(R5-E10 ensemble; 16:44-flatten v2 as live-ops default) is what MONITOR-01 tracks on
locked-forward data; the three objects above are campaign #3's shipped systems and are governed
by BASELINE_MODELS. Both lines are frozen; they are different objects with different ledgers.

## 3. Merged open frontier (all programs, EVI order as of 2026-08-14 + parked items with gates)

**READY now:**
1. **Direction-conditioned HTF construction** — the sharpest actionable lead in the repo.
   HTF's marginal contribution sits below its own randomized-chronology null (PLACEBO01) and
   HTFMECH01 (2026-08-14) showed the cost is direction-concentrated: value-additive long,
   value-destructive short (Product A short side −$22,020). Requires its own preregistration +
   full gate battery. (`research/system_master/ACTIVE_RESEARCH_QUEUE.md` rank 2)
2. **Second literature-scout pass** (auction spillovers, intraday liquidity cycles) — cheap,
   hypothesis-first. (rank 4)

**Parked with explicit gates** (see `research/operational/MONITORING_CALENDAR.md` for all):
B1 challenger (drop-HTF Product B; INCONCLUSIVE Sharpe; `B1_FUTURE_CONFIRMATION_SPEC.md`);
U9/U9B microstructure at larger sample; AUCTION02 batch-2 (160/168 protected sessions intact);
Program-B trio B-MOM/B-FADE/B1-overnight (MONITOR-02, ≥2027-08-01); DOM-M1 (paused);
GAMMA00 (data purchase); cross-market (needs a specific mechanism — generic "ES predicts NQ"
not authorized); capital/portfolio refresh (needs a new capital-relevant finding).

**Named revival conditions (closed, but with an honest door):** U6B (multi-contract scale-up
gap mechanism); overnight sleeve (ablation win P≥0.9 vs day-only at equal vol); Zone-F scalping
(≥+7pp preregistered on discovery AND forward holdout); S2a short side (BARRED until a new spec
survives Tier-0).

**Excluded from re-ranking by standing instruction:** DOM/Replay (paused), B1 historical
tuning, ACTIONMAP01, U6B, generic OHLCV feature mining (8 independent families share one
right-tail-unsafe-or-too-small failure signature).

## 4. Kill / closure ledger — where "do not re-run unchanged" lives

No single file lists every kill; these five together do, and each is authoritative for its era:

| Era | Ledger |
|---|---|
| Campaign #1 axes | `research/frontier.yaml` (2026-08-18 reconciliation block) + `research/registry/rejected_ideas.md` |
| FINAL OPTIMIZATION DIRECTIVE (8 families + Engine-3 slate 15/15) | `RESEARCH_HANDOFF.md` "Do not reopen unchanged" + `runs/S2_SELTIME/R2_*.md` |
| SYSTEM SCIENCE + continuous evolution (U*, R*, SA0, PA*, AUCTION*, M1/M5…) | `research/system_master/RESEARCH_FRONTIER.md` (per-family rows) + `TESTING_LEDGER.csv` + `SYSTEM_SCIENCE_20260809.md` |
| Structural invariance (GRID/PERT/PLACEBO/SIMPLE/HASH/STAT/EQV) | `STRUCTURAL_INVARIANCE_MINIMUM_SYSTEM_SYNTHESIS.md` |
| Scalping Zone F (16 families, ~500 configs, 3 ceilings) | `research/scalping_lab/REJECTED_IDEAS.md` + `reports/ZONE_F_FINAL_VERDICT.md` + `ALPHA_SCOREBOARD.md` |

Rule that binds them all: a closed family may be reopened only by a genuinely new mechanism or
data source with its own preregistration — never by re-running the same grid shifted.

## 5. Unified data boundaries (the single table)

| Window / dataset | Status | Defined by |
|---|---|---|
| ≤ 2026-05-29 (dev, all substrates) | research-consumed; selection allowed under registry discipline | `CONVENTIONS.md` §1 (+ 2026-08-18 boundary-constant correction: cite 2026-05-29) |
| 2026-06-01 → 2026-07-31 (former joint holdout) | **CONSUMED 2026-08-08 by SM11** — for everything, all campaigns | `HOLDOUT_DETERMINATION_20260809.md` |
| ≥ 2026-08-01 | **VIRGIN** — scheduled preregistered reads only (MONITOR-01/02, annual eval) | `research/operational/LOCKED_FORWARD.md`; boundary math `research_sdk/session_boundary.py` |
| Scalping confirmation pool (168 protected sessions) | 8 consumed 2026-08-10 (AMENDMENT_3 batch 1); **160 intact**; 116 lack local BBO (rolling ~1yr server window — OQ-4) | `research/scalping_lab/CONTAMINATION_LEDGER.md`, `PROTECTED_EVIDENCE_BUDGET.md` |
| Tick/BBO substrate | NQ 40 + ES 39 sessions + 8 pool sessions; s20251117 truncated at 12M (re-export pending one NT8 restart) | `substrate/MANIFEST.csv` + **`MANIFEST_NOTES.md`** (src/capped caveats) |
| Minute history | NQ 2006-01-05→2026-05-29, 6,466,783 bars, sha256_16 dfd017ef (holdout never exported) | `substrate/minute/NQ/MANIFEST` |
| DOM / Market Replay | 1 preserved proof file (NQU6 2026-07-15); collection PAUSED; DOM01 governance intact-but-idle | `DOM_PAUSE_CLEANUP_20260812.md`, `data_forward_sealed/DOM01/` |
| Wave-17 suspected access ($75,449.60, window→2026-08-07) | UNVERIFIED — DO NOT CITE; carried permanently in the access ledger | `HOLDOUT_DETERMINATION_20260809.md` ledger; CURRENT_TRUTH Wave-18 §6 |

## 6. Scheduled reads + owner decisions

- **Calendar:** `research/operational/MONITORING_CALENDAR.md` — MONITOR-01 #2 ≥ 2026-11-01
  (quarterly after); annual frozen-champion eval ≥ 2027-08-01; MONITOR-02 Program-B re-read
  ≥ 2027-08-01 (protocol now frozen: `MONITOR02_PROTOCOL.md`); plus all gated items.
- **Owner queue (`OWNER_QUEUE.md`):** OQ-1 **repo is PUBLIC + vendor-DLL remote retention
  UNVERIFIED** (highest-consequence; decision + GitHub Support GC request); OQ-2 exact Lifetime
  commission (sensitivity band already brackets it); OQ-4 (new 2026-08-18) DOM-pause follow-ups —
  two rolling-retention data clocks + the unresolved 2026-08-12 C:-drive space drain.

## 7. Standing rules born from waves (quick reference — each is binding)

- **Spec-first commits**, mechanically enforced: `research_sdk/prereg_guard.py`; per-wave seal
  audit `src/analytics/seal_audit.py`; boundary math `research_sdk/session_boundary.py`.
- **Warmup:** every Strategy-Analyzer comparison states start date + warmup convention;
  continuation basis mandatory; fresh runs discard ≥60 sessions (binding constraint = HTF tilt's
  51 sessions, not sigma460). `research/system_master/WARMUP_STANDARD.md`.
- **O1/O2 scoring:** every owner-utility score reports BOTH aggregation conventions; a verdict
  that flips between them is INCONCLUSIVE and may not be quoted as one number (R3 blind-review
  fallback, binding).
- **Clamp quoting:** "the clamp binds 39.2%" is the widest member's rate; ensemble-level is
  12.94%, any-member 50.6% — quote the right one (Wave-19 §4).
- **Promotion floor for Product A challengers:** Python-only improvements < ~$430/0.24% may not
  be promoted on Python evidence alone (EXEC01 sec70).
- **Engine-#3 bar:** CI_lo>0 at C1, losing-day ρ ≤ 0.25 vs Solar, mechanically distinct
  hypothesis, preregistered, plateau not argmax, right-tail-safe
  (`COMPLEMENTARY_ENGINE_FRONTIER.md` frozen block).
- **Name collision:** "B1" = SYSTEM_MASTER drop-HTF challenger ≠ "B1 overnight" sleeve
  (CURRENT_TRUTH corrections index).
- **Registries:** three-registry reality mapped in `research/registry/README.md` +
  `RUNS_INDEX.csv` (191 run dirs classified).

## 8. Document authority (tie-break order)

1. `CLAUDE.md` — safety boundary + conventions (with its 2026-08-18 current-campaigns addendum).
2. `/BASELINE_MODELS.md` — anything about the 3 objects.
3. `research/system_master/CURRENT_TRUTH.md` (top snapshot + corrections index) — campaign-#3
   state; `ACTIVE_RESEARCH_QUEUE.md` — what's next.
4. `research/system_master/CONVENTIONS.md` (+ dated corrections) — statistical protocol.
5. Registry/state files over prose; run REPORTs over summaries; this file over nothing — it
   points, the pointed-at files govern.

## 9. What the 2026-08-18 consolidation changed (all additive; nothing deleted or rewritten)

New: this file; `research/operational/MONITORING_CALENDAR.md`; `MONITOR02_PROTOCOL.md`;
`research/registry/README.md` + `RUNS_INDEX.csv`; `research/scalping_lab/registry/README.md`;
`substrate/MANIFEST_NOTES.md`; 4 × `runs/*/STATUS.md` pointer notes.
Corrected/banered (append-only): CLAUDE.md, AGENTS.md, MAP.md, RESEARCH_HANDOFF.md,
BASELINE_MODELS.md, OWNER_QUEUE.md (OQ-1a, OQ-4), reports/{latest,leaderboard,portfolio,
robustness}.md, research/CAMPAIGN_STATE.md, NEXT_HANDOFF_CAMPAIGN1_CLOSED.md,
research/frontier.yaml (closure reconciliation), research/registry/{experiments.yaml,
REGISTRY_GAP_NOTE.md}, system_master/{CONVENTIONS, CURRENT_TRUTH, RESEARCH_FRONTIER,
STRUCTURAL_INVARIANCE…, CANONICAL_MATHEMATICAL_SPEC, DRAWDOWN_FRONTIER, INDICATOR_FRONTIER,
ALPHA_THROUGHPUT, STRUCTURE_MAP, SM13_BMOM_DECAY_RULE, README, COMPLEMENTARY_ENGINE_FRONTIER,
ACTIVE_RESEARCH_QUEUE, TESTING_LEDGER.csv (HTFMECH01 catch-up row)}, scalping_lab/{CAMPAIGN_STATE,
ALPHA_SCOREBOARD, FRONTIER.yaml, HYPOTHESES, DATA_INVENTORY, DATA_SUBSTRATE,
reports/ZONE_F_FINAL_VERDICT, registry/experiments.yaml}, runs/DATA03…/REPORT.md (§5 status).
