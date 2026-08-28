# TEAM A1 — Documentation-layer census and claim classification
**PROJECT GENESIS wave 1 · 2026-08-28 · READ-ONLY session.** Repo HEAD at census: `51a9cc6` (GENESIS COMMIT B); working tree clean at session start.

Classification vocabulary (per GENESIS charter §Epistemic rules): **RAW FACT** = verified by me this session from a run artifact or filesystem; **RAW FACT (artifact concordance)** = I verified the quoted figure appears verbatim in the cited `runs/<ID>/REPORT.md`, but did NOT recompute it from data; **RECORDED CLAIM** = a repo document asserts it; **INTERPRETATION**; **GOVERNANCE RULE**; **RETRACTED**.

---

## 1. Campaign map (numbering authority: `research/INDEX.md:63-75`)

| # | campaign | state doc | status per INDEX | headline (as recorded) |
|---|---|---|---|---|
| 1 | Solar Wave | `research/CAMPAIGN_STATE.md` | CLOSED 2026-08-07 | vendor indicator 100% reverse-engineered (2,035,869 bars, 9 configs, 0 mismatches — corrected up from a wrong 1,436,860); central result "the deliverable is a region, not a parameter": R4 all-21-cells Sharpe **0.892** on the 1,424-session calendar, net $159,424, maxDD −$35,669, positive all 5 years; PBO 0.56–0.66 with negative IS→OOS slope (`research/CAMPAIGN_STATE.md:58-80`) |
| 2 | independent audit | `research/audit/AUDIT_EXECUTIVE.md` | CLOSED 2026-08-07 | (not read this session; INDEX row only) — `runs/AUDIT*` = 11 dirs |
| 3 | SYSTEM_MASTER (+ breadth_lab) | `research/system_master/CURRENT_TRUTH.md` | CLOSED 2026-08-21 per INDEX; **newest section header inside is 2026-08-19f** (RAW FACT, grep of `^## `) | zero promotions; breadth trilogy BREADTH01/02/03 all CLOSED_FAIL (03 failed by year-block CI_lo −0.51%); engine-3 candidates 0-for-18; ATRPOOL01 FAIL by 0.009; all remaining levers owner-gated (GAMMA00 $80–199/mo, breadth funding, CrossTrade) or calendar-gated (MONITOR-01 #2 ≥2026-11-01) |
| 4 | Scalping Lab | `research/scalping_lab/CAMPAIGN_STATE.md` | **dormant** | PHASE COMPLETE 2026-08-08: 3 parked Program-B candidates, 0 frozen, Zone F closed; W2-0 null audit RETRACTED W1-1 "real persistence/gross positive" (null r≈2 not 1); E10 Flatten1644 CONFIRMED_ADOPT (net −5.35%, tail retention 95.8%) |
| 5 | complementary families | `research/04_complementary_family/` | closed | (per INDEX; no single state doc read) |
| 6 | OTR / VWAP Flux | `research/original_trader_reconstruction/CURRENT_TRUTH.md` (newest section 2026-08-24l) + `FINAL_ANSWER_20260825.md` | closed | 8-skeptic audit: **0 CONFIRMED / 2 REFUTED / 6 WEAKER_THAN_STATED**; 2023 reproduced at trade level for 11 days / 88 constrained cells (two paths, ~2% of the 4,351-trade window); 2025/2026 "not reconstructed at all"; owner R33: buy VWAP Flux as instrument, not proof |
| 7 | WEEKLY_EDGE | `research/weekly_edge/CURRENT_BASELINE.md` (2026-08-27, through W123 + RR_W000–006) | **LIVE — the only active campaign** | four baselines below; "no candidate" as of 2026-08-28; frontier rank 1 = prospective shadow accumulation |

**GENESIS itself**: `research/genesis/GENESIS_CHARTER.md` exists (RAW FACT), opened 2026-08-28; commits `f507ea9` (COMMIT A: charter) and `51a9cc6` (COMMIT B: search ledger, selftest 9/9). `runs/GENESIS*` = **0** directories yet (RAW FACT).

## 2. The four baselines — objects, economics, evidence tags

Consistent across all three owners (`CURRENT_BASELINE.md:24-49`, `README.md:36-54`, `EXECUTION_MANIFEST.md:22-29`). All figures below are RECORDED CLAIMS whose headline numbers I verified as RAW FACT (artifact concordance) in the cited run reports.

| slot | object | headline economics | evidence tag | run |
|---|---|---|---|---|
| **A** RESEARCH_SINGLE | `P1/PCT` (13-member Solar ratchet ensemble, OR-gated B-MOM, long-only, per-contract session box −$1,300/+$1,000) | $1,394/wk raw · **$1,230/wk at fixed $20,245 maxDD** · 56.3% positive weeks · maxDD $22,931 · t 4.16 · window 2022-07-01→2026-08-01, 1,058 sessions, 213 weeks | **DISCOVERY_CONSUMED** (`CURRENT_BASELINE.md:48-49`) | `runs/WE_W103_CONSOLIDATE/` — 1,230 / 20,245 / 22,931 confirmed present in REPORT.md ✔ |
| **B** RESEARCH_PORTFOLIO_FRONTIER | `{P1/PCT + XM_CONFLICT}` inverse-vol | **$2,012/wk at fixed DD** · maxDD $11,489 · 59.2% · t 4.90; RECONCILED to 0.000000 on all 5 figures; ⚠ best-of-six selection optimism **$245.71/wk (13.9%)** → honest selection-adjusted causal B **≈$1,750–1,800/wk**; XM hedge mechanism INVERTED (ρ 0.086→0.369; payoff when P1 loses +$598→−$1,243) | **DISCOVERY_CONSUMED**; Portfolio B evidence class **REGIME-LOCAL (inherited)** (`ALPHA_EVIDENCE:42`) | `runs/WE_W103_CONSOLIDATE/` + `runs/PORTFOLIO_B_RECONCILIATION_20260827/` — 2,012 / 11,489 confirmed ✔ |
| **C** EXECUTABLE_SINGLE | `WeeklyEdgeP1PCT_v1` (sha256[0:16] `ee4c765bc5cab230`, cert commit `fc8cf85`) | parity 2026-08-27: 2,131 Py vs 2,137 NT8 trades (+0.28%) · matched 99.672% · weekly ρ 0.9852 · 1,908/2,124 trades reproduce to $0.00 | **PARITY-CERTIFIED · NOT ENABLED** | `runs/WE_P1PCT_PARITY_20260827/` — 99.672 / 0.9852 / 1,908 / 2,137 confirmed ✔ |
| **D** EXECUTABLE_COMPONENT_SET | `WeeklyEdgeP1PCT_v1` + `WeeklyEdgeXMConflict_v2` (`2ec00dd4d0a11b99`) | XM parity: desired_direction 99.715% · 347 vs 346 trades · broad_composite max\|diff\| 0.000000; v1 SUPERSEDED (armed on early-close holidays, must not run) | both legs **individually PARITY-CERTIFIED · NOT ENABLED**; ⚠ **NOT portfolio B** — integer-contract mapping unselected (owner OQ-6), `EXECUTABLE_PORTFOLIO` **PENDING** | `runs/WE_XM_PARITY_20260827/` — 99.715 (2 hits) / 346 confirmed ✔ |

GOVERNANCE RULE (all three docs): EXECUTABLE ≠ PARITY-CERTIFIED ≠ LIVE-ENABLED; **LIVE ENABLED = NO** everywhere; cost models differ (research = $4.36/ctrRT + modelled spread P1 $14.44 / XM $12.50; NT8 = commission only, zero slippage) so research and NT8 nets are never comparable.

## 3. Headline-claim classification table

| claim | source | classification | run ID |
|---|---|---|---|
| A/B/C/D economics rows above | CURRENT_BASELINE §0 | RAW FACT (artifact concordance) | WE_W103_CONSOLIDATE, WE_P1PCT_PARITY_20260827, WE_XM_PARITY_20260827 |
| 59% of P1 decisions have negative causal marginal value; mean +$162.79, sd $2,123.55; top 107 events = 104.9% of sum | CURRENT_BASELINE §RR_W001 | RAW FACT (artifact concordance: 162.79×2, 2,123.55 in REPORT.md) | RR_W001_ACTION_VALUE_LEDGER |
| Action-value information NULL (51.0th pctile of refitted null; known-null control at 77.0th) | CURRENT_BASELINE §7, frontier | RECORDED CLAIM | RR_W002A_ACTION_VALUE_INFORMATION |
| HTF NULL; X9a NOT ADMITTED (name collision — `w72:X9a` contains P1, ρ +0.613); box worth keeping (all relaxations 16–41% worse at fixed DD); coverage gap 0.38% | CURRENT_BASELINE §6, frontier | RECORDED CLAIM | RR_W004, RR_W003, RR_W005, RR_W006 |
| Event response CLOSED-BY-DATA/UNDERPOWERED (153/2,131 decisions, MDE 9.8× bar, needs ~96× N ≈ 220 yr) — never NULL | frontier, CURRENT_BASELINE | RECORDED CLAIM + GOVERNANCE RULE | DATAGATE_EVENTRESPONSE_20260827 |
| MS-BBO-CANDIDATE-1 **VOID — read the future** (int32 overflow, 15/30 offsets positive to +2.065 s; leak 134.8%; causal object −$1,785.88/session) | ALPHA_EVIDENCE:45, frontier:97 | RETRACTED (the $5,125/session, t 6.76, 7/7-gates claim) — void verified: `2.065`, `int32` present in REPORT.md ✔ | MSBBO_DEPLOYMENT_FREEZE_20260828 |
| ESNQ_V1 CLOSED: net −$18,113.79, −$503.16/session, OOF corr +0.0034, 0/4 quartiles; blind EFFECTIVE_14 unspent | frontier:99 | RAW FACT (artifact concordance: all three figures in REPORT.md) ✔ | ESNQ_V1_20260828 |
| VOLUME_LIQUIDITY_V1 CLOSED 10/12 gates: gross −$17,033.50 pre-cost, net −$54,330.30, mirror also loses; bounded at \|r\|≈0.02 | frontier:101 | RAW FACT (artifact concordance) ✔ | VOLUME_LIQUIDITY_V1_20260828 |
| CARRY_V1 CLOSED C6/C7 (Sharpe 0.719 but SI = 84.1% of positive contribution); validation + holdout NOT READ | ALPHA_EVIDENCE:46 | RECORDED CLAIM | CARRY_V1_20260828 |
| TSMOM all roles CLOSED (V1 dev 3/6; V2 G3; TAIL-H1 4/5); 2023–26 TSMOM holdout now CONSUMED (earlier "unspent" corrected) | ALPHA_EVIDENCE:55-57 | RECORDED CLAIM (with recorded self-correction) | TSMOM_V1/V2, TSMOM_TAIL_H1 |
| Order flow CLOSED-BY-POWER "needs 998, 713 exist, unreachable at ANY coverage" | ALPHA_EVIDENCE:60 | **RETRACTED-IN-PART but row not updated** — frontier changelog (Program C, line 447) withdraws the arithmetic: 713 = local NT8 store; Databento GLBX.MDP3 ≈ 2,300 sessions CME NQ MBO from 2017 | DATAGATE_ORDERFLOW_V2_20260827 vs INFORMATION_FRONTIER_00_20260828 |
| "The free surfaces are exhausted" | earlier frontier text | **RETRACTED 2026-08-28** — VX/VXM in NT8, $TICK to ~2013, MNQ tick 187 dates hidden by `build_registry.py` hard-coded `symbol="NQ"`, 9 unextracted 1-min stores | INFORMATION_FRONTIER_00_20260828 |
| Frontier rank 1 = PROSPECTIVE SHADOW (start 2026-09-01 18:00 ET, roster P1/PCT · XM_v2 · P1/ABS; only remaining owner action = starting it) | frontier:102, PROSPECTIVE_SHADOW.md | RECORDED CLAIM + GOVERNANCE RULE (no backfill; S26/S52/S104 specified NOT ARMED; zero order path) | PROSPECTIVE_SHADOW_PREFLIGHT_20260828 (11/11 verified ✔) |
| BBO blind pool: 19 sessions (18 pristine, 1 metadata-exposed), falsifier-grade only (MDE $2,996/session) | ALPHA_EVIDENCE:49 | RECORDED CLAIM (hash-frozen; 84a8575a…=CRLF hash, 92010fc6…=normalized — recorded reconciliation, not a conflict) | BBO_COMPLETENESS_RECENSUS_V1_20260828 |
| ES BBO = 79 sessions: 44 ESNQ-consumed · 15 blind (14 effective) · 20 genuinely unread | ALPHA_EVIDENCE:50 | RECORDED CLAIM (supersedes the changelog's "64 fully unread" — correction recorded in-row) | ESNQ_V1_20260828/out/es_recensus.json |
| Reference trader RETIRED as benchmark ($42.79/in-market-hr vs P1's $96.18) | ALPHA_EVIDENCE:54 | RECORDED CLAIM / INTERPRETATION | NQ_OPPORTUNITY00_20260828 |
| Data seals: ≥2026-08-01 VIRGIN (~19 sessions); 2026-05-31→07-31 BURNED; 2022-07→2026-05-30 DISCOVERY_CONSUMED (123 waves) | CLAUDE.md §5, CURRENT_BASELINE §5, frontier §13 | GOVERNANCE RULE | — |
| Locked-forward champion R5-E10 (TRUE_MTM $179,361.36, Sharpe 0.9671) frozen; MONITOR-01 #2 due ≥2026-11-01, annual eval ≥2027-08-01 | LOCKED_FORWARD.md (2026-08-07 — campaign-3/4-era doc) | RECORDED CLAIM + GOVERNANCE RULE | — |

## 4. Runs census (RAW FACT — directory counts, `ls` on runs/)

**400 run directories total.** By prefix: `WE_*` 123 (= 121 `WE_W*` incl. WE_W44_NT8PARITY, + WE_P1PCT_PARITY_20260827 + WE_XM_PARITY_20260827) · `SM*` 54 (campaign #3; incl. 4 `SM1M*`) · `OTR*` 39 · `SW*` 24 (campaign #1) · `FH*` 11 · `AUDIT*` 11 (campaign #2) · `RR_W*` 7 · `MS*` 6 · `DATA*` 5 · `DATAGATE*` 3, `TSMOM*` 3, `VOLUME*` 3, `FWD*` 3 · `CARRY*` 2, `ESNQ*` 2, `E10*` 2, `INT0*` 2, `C01T*` 2 · singletons incl. GAMMA00_SCOPING-class, INFORMATION_FRONTIER_00_20260828, PROSPECTIVE_SHADOW_PREFLIGHT_20260828, NQ_OPPORTUNITY00, BBO_COMPLETENESS_RECENSUS_V1, ASSET_CENSUS, PORTFOLIO_B_RECONCILIATION · long tail of campaign-1/3/4 IDs (W1*–W19*, B0*, U9*, etc.). **`GENESIS*`: 0.**

## 5. Contradictions found (every one located this session)

1. **README.md self-contradiction (both lines dated "current as of 2026-08-28")** — `README.md:58` "ESNQ_V1 is the ACTIVE research object — PRE-DEVELOPMENT-RESULT… No ESNQ alpha evidence exists yet" vs `README.md:69` "ESNQ_V1 CLOSED (net −$18,113.79…)". RAW FACT.
2. **README vs frontier + filesystem** — `README.md:70` "VOLUME/LIQUIDITY… never been alpha-tested… rank-1 lane, designed but not run" vs `RESEARCH_FRONTIER.md:101` (V1 CLOSED, 10/12 gates failed) and the existing `runs/VOLUME_LIQUIDITY_V1_20260828/` (RAW FACT). README also names the wrong rank-1 (volume, not prospective shadow). README is stale by ≥1 same-day revision.
3. **PROSPECTIVE_SHADOW.md vs frontier/preflight run** — shadow_ledger self-test "**9/9**" (`PROSPECTIVE_SHADOW.md:84,129`) vs "**11/11** after the DST string-vs-instant fix" (`RESEARCH_FRONTIER.md:448`; `runs/PROSPECTIVE_SHADOW_PREFLIGHT_20260828/REPORT.md` contains 11/11 — RAW FACT). The shadow doc predates the preflight and was not updated.
4. **ALPHA_EVIDENCE_CLASSIFICATION.md:60 vs frontier Program C** — order-flow row still asserts "needs 998 sessions; **713 exist**. Unreachable at any coverage" as current, after `RESEARCH_FRONTIER.md:447` retracted that arithmetic (713 = local store; ~2,300 acquirable). The frontier's own row 9 (line 48) carries the same stale phrasing but is inside a block labelled HISTORICAL.
5. **RESEARCH_FRONTIER.md:407** — owner-gated table row "Market internals (TICK/ADD/TRIN) — **no data exists at all**" contradicts INT01/INT02 having consumed internals data (`ALPHA_EVIDENCE:58-59`, runs exist — RAW FACT) and Program C's "$TICK to ~2013".
6. **Campaign numbering** — `system_master/CURRENT_TRUTH.md:3` "CAMPAIGN #5 (breadth_lab) opened" vs `INDEX.md:73` "#5 complementary families". Two different campaigns claim the number 5.
7. **Closure status of #4** — `README.md:24` "Six are closed" vs `INDEX.md:72` "#4 Scalping Lab (**dormant**)".
8. **Closure date of #3** — `INDEX.md:71` "closed 2026-08-21" vs newest `CURRENT_TRUTH.md` section header 2026-08-19f (RAW FACT; the 08-21 close may live only in commits).
9. **Seal-register pointer** — `CLAUDE.md §5` names `LOCKED_FORWARD.md` the seal register, but that file (2026-08-07, campaign-3/4-era R5-E10 freeze) records only the ≥2026-08-01 virgin boundary — the 2026-05-31→07-31 **BURNED** span appears nowhere in it (it lives in `CURRENT_BASELINE.md:332`). Also boundary phrasing differs from scalping-lab's holdout "2026-06-01→07-31" (`scalping_lab/CAMPAIGN_STATE.md:26`) — likely a session-boundary (18:00 ET) convention, not a substantive conflict.
10. **ES BBO count drift, recorded** — frontier changelog "64 pre-seal, ZERO outcome-consumed" (ASSET CENSUS entry, line 455) vs current "79 = 44+15+20" (`ALPHA_EVIDENCE:50`, which flags the 64 as "stale twice over"). Self-corrected, but the stale number remains quotable from the changelog.
11. **Two order-flow gate figures in circulation** — 71/2,131 (3.3%), MDE $564 (`CURRENT_BASELINE:411`, DATAGATE_ORDERFLOW) vs 141/2,139, MDE 4.61× (`RESEARCH_FRONTIER:48`, V2 after free extraction). Different waves; a reader quoting "the" order-flow gate can pick either.
12. **CURRENT_BASELINE.md is one day behind the frontier** — dated 2026-08-27 (through W123/RR_W006); knows nothing of the MSBBO void, ESNQ/CARRY/VOLUME closures, Program B/C, or the shadow promotion. Its §7 "the next runnable item is engineering, not discovery" is superseded by the frontier's rank-1 = shadow. The A–D slots themselves are unchanged and consistent.

## 6. Notes for other GENESIS teams

- The documentation layer's internal correction discipline is high (retractions carried in place with reasons), but **freshness is uneven**: RESEARCH_FRONTIER.md is the only doc current to 2026-08-28 end-of-day; README/PROSPECTIVE_SHADOW/ALPHA_EVIDENCE each lag it in at least one load-bearing row.
- Evidence-status vocabulary is used consistently: A/B are DISCOVERY_CONSUMED; nothing anywhere claims FORWARD evidence exists ("the project has ZERO prospective evidence" — PROSPECTIVE_SHADOW.md, RECORDED CLAIM).
- Blind pools stated precisely: NQ BBO 19 (18 pristine/1 metadata-exposed) · ESNQ effective 14 of 15 · NQ Last-only 141 (frozen at `fd7b05f`) · ES BBO 20 unread outside any manifest. All listed as ASSETS, not questions.
- $0 spent; every owner spend gate unexercised; DOM/L2/Replay PAUSED since 2026-08-12 (`research/system_master/DOM_PAUSE_CLEANUP_20260812.md` per CLAUDE.md).
