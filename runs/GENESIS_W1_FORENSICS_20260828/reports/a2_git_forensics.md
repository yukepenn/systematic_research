# TEAM A2 — GIT-HISTORY FORENSICS (PROJECT GENESIS)
Date: 2026-08-28. Repo: `D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research`. Read-only session; no repo file touched; no CrossTrade tool called; no sealed/blind data values read.

Evidence tags: **RAW FACT** = verified by me this session (git command or file read). **RECORDED CLAIM** = a repo document/commit message asserts it.

---

## 0. Repository shape (RAW FACTS)

- `git log --all --oneline | wc -l` = **1,002 commits**, spanning **2026-08-06 → 2026-08-28** (23 calendar days). Branches: only `main` + `origin/main`. All seven campaigns plus the GENESIS reboot happened inside this 23-day window.
- Deletions across the ENTIRE history: **15 files ever deleted** (`git log --all --diff-filter=D --summary`). Full list captured in `scratchpad/deletions.txt`. Nothing that looks like evidence destruction:
  - 2 crash dumps (`grep.exe.stackdump`, commit 8ec5d95), 3 run artifacts, and 2 genuinely superseded docs deleted with written justification: `research/system_master/SYSTEM_SCORECARD.md` + `SYSTEM_FRONTIER.yaml` (commit 0f50d79, 2026-08-09 — "git history preserves them", both recoverable via `git show 0f50d79^:...`, verified).
  - `MAP.md` + `OWNER_QUEUE.md` deleted at root in the info-architecture pass (47959b9, 2026-08-27); OWNER_QUEUE content migrated to `research/operational/OWNER_QUEUE.md` (still referenced by CLAUDE.md Tier 1). Verified the deleted version is recoverable and its OQ-1 (public-repo/vendor-DLL exposure) and OQ-2 (exact Lifetime commission) items exist.
- **No renamed research directories of consequence**; one file rename (`NEXT_HANDOFF.md`, d9fdb39) to fix a campaign #1/#3 collision.
- `runs/` contains **400 run directories**, 270 with `REPORT.md`. Registry files (RAW counts): `research/registry/tested_configs.csv` 227 data rows (seq reaches **498**), `tested_configs_backfill.csv` 296 rows, `RUNS_INDEX.csv` 195 rows, `research/system_master/TESTING_LEDGER.csv` **82 rows**.

## 1. Experiment count per campaign — the search-debt baseline

Method: run-directory prefixes (`ls runs`), registry seq ranges, wave numbering in commit subjects. Counts approximate where stated.

| campaign | window | experiment count (method) | promotions |
|---|---|---|---|
| #1 Solar Wave | 08-06→08-07 | registry seq 1–~232 incl. ~90-config Wave-1 leaderboard (229fd07); runs `SW*`, `FH*` (11), `AUDIT*` (~12) | champion R5-E10 frozen (204c574); H-006 downgraded INCONCLUSIVE, DSR figures withdrawn (9e074f0) |
| #2 post-audit / C01 / E10 | 08-07 | seq 233–290: PORTABILITY-01 (0/3), DM01, B01 wave, C01 Tier-0/1 | E10 Flatten1644 adopted (0bdd9a1); C01 both Tier-1 programs REJECT (927c895) |
| #3 SYSTEM_MASTER | 08-08→08-09 | seq 291–498 (~208 registered experiments incl. red teams); SMV2A–SMV2AJ; FINAL OPTIMIZATION **0/18 promotions** (5b66067→3146cc0) | SM08 HTF tilt + c1_50 promoted, later falsified by placebo (2825b39) |
| #4 scalping_lab | 08-07 | ~25 named readouts (W1–W10, Z1, H-A1, H-D3, FSS-9/10, B01 arms, I-1/I-2, pilots); closed "everything runnable has been run" (4c9ac6d) | 0 frozen; 3 PARKED candidates (204bc5a) — one of them (B-MOM) later became half of P1 |
| #5 breadth_lab + one-shots | 08-18→08-21 | ~14 one-shot families: BREADTH01/02/03, ATRPOOL01, TERMFLOW01, TOMFLOW01, CLOSEREV01, LIQREV01, HTFDIR01, HTFMECH01, ONRANGE01/02, KDJMA01, ENGINE3_SCOUT; TESTING_LEDGER rows into the 70s-80s | 0; engine-#3 axis **0-for-18 + 2 parked regime-locals** (CURRENT_TRUTH.md:67) |
| #6 OTR | 08-23→08-25 | R1–R34, S0–S8, V1–V3, VF1–4, SD1, IMG-0–16; 164-image corpus; 141-row CLAIM_REGISTRY (ea5e728); 39 run dirs | verdict object, not a strategy: owner-ratified BUY-VF (d2fdd52) |
| #7 WEEKLY_EDGE | 08-25→08-27 | **123 preregistered waves** (W01–W123), 123 `WE_*` run dirs, most with 3–10 arms | P1/PCT + XM_CONFLICT both parity-certified (fc8cf85); Slot D = EXECUTABLE_COMPONENT_SET |
| GENESIS-era programs A–C | 08-27→08-28 | ~35 runs: MS01/MS01A, MSLAST, MSBBO×2, TSMOM×3, INT×2, CARRY×2, ESNQ×2, VOLUME×2, OPPORTUNITY00, RR_W000–006, DATAGATE×3, censuses | 0 (MS-BBO-CANDIDATE-1 frozen then VOID) |

**Total ≈ 700+ registered experiments/readouts in 23 days, ~2 surviving executable components.** That is the multiplicity debt any "new" NQ result must be priced against.

## 2. Ranked top-10 forgotten / mis-buried items

### 1. LIQREV01 — passed ALL 8 of its own preregistered gates; frozen out under a doctrine that was later revoked; its scheduled shadow read has been DROPPED from the consolidated calendar
- RECORDED CLAIM (`research/system_master/CURRENT_TRUTH.md` ~115-122; commit 3cf4371, 2026-08-19): Nagel/CGW stress-gated daily reversal, 20-yr minute substrate — "**ALL 8 frozen gates PASS on the letter** (N=455, $579/trade, episode CI [+155,+1061], matched placebo NULL...)". Freeze withheld after red team because evidence is **REGIME-LOCAL(2020+)** and the engine-#3 complementarity role was refuted (profits on Solar's top-decile days).
- The regime-local ground later lost its force: CLAUDE.md §4 records the post-W115 owner doctrine — "**Old-regime failure is a RISK CLASSIFICATION, not a promotion veto**."
- RAW FACT: `grep -i "liqrev\|htfdir" research/operational/MONITORING_CALENDAR.md` → **zero hits** (exit 1), while CURRENT_TRUTH.md:70-71 names "MONITOR-01 #2 ≥2026-11-01: … + HTFDIR01 + LIQREV01 shadows" as the next information events, and `HTFDIR01_DIRECTIONAL_TILT/REPORT.md:67` requests a candidate shadow ledger at each MONITOR-01. Commit 1093ba3 shows the HTFDIR01 shadow-ledger protocol was **owner-authorized 2026-08-19**. The regenerated 2026-08-28 calendar silently lost both shadows. This is a live governance drift, cheap to fix, guarding a full-gate-pass candidate.

### 2. FOLLOW_MORNING (WE_W114/W116) — the strongest modern object since XM, alive on the frontier, decided only by the virgin forward window
- RECORDED CLAIM (`runs/WE_W114_INTRAMOM/REPORT.md:140-161`; commits 781ccea, 82106fc): parameter-free intraday momentum, modern 98.9th percentile, REGIME_LOCAL (16-yr out-of-window fail is behavioural, not cost: implied edge 0.70%→5.62% monotone over four 5-yr blocks). Survives every standalone test; fails only the portfolio-marginal test (ρ +0.279 with base).
- RAW FACT: its forward read IS in `MONITORING_CALENDAR.md` (sealed ≥2026-08-01, frozen 11:48→15:44 geometry). GENESIS must not orphan it.
- Corollary that re-prices the graveyard: W114 §4 — the campaign killed **seven fade mechanisms** and called the family dead; the mirror of those fades earns $179/trade on the same sessions. "They were failing because they were on the wrong side of a live momentum effect." A chunk of the fade graveyard is collateral of an unmodeled momentum regime, not evidence about mean reversion per se.

### 3. The mirrored SHORT sleeve (W61–W63) — best decoupling ever measured, killed by ONE year, with a stated revival condition nobody is monitoring
- RECORDED CLAIM (`research/weekly_edge/PARKED_NOT_DEAD.md:54`): daily ρ **−0.003** with P1, trades **81.5%** of P1's idle sessions, money improvement stable in 95-100% of rolling windows ("most stable improvement in the campaign"), +5.4pp positive weeks, streak halved. Killed by 2026 standalone −10.62 pts/session; revival = trailing-24-month t reverting toward its median +2.1.
- RAW FACT: no calendar row or protocol schedules a re-read of that statistic (grep of MONITORING_CALENDAR). It is exactly the kind of cheap conditional re-read a reboot should institutionalize.

### 4. W40 axis-B vol-expansion event sleeve — a 92nd-vs-95th near-miss whose stated revival condition ("a longer sample") is being satisfied by time itself
- RECORDED CLAIM (`PARKED_NOT_DEAD.md:38`): stress-net +$114/wk standalone, corr +0.01 overall and **−0.25 inside worst-decile weeks** (a true diversifier signature the short-sleeve rows say has never otherwise been found), N1 null 97th; failed binding N2 count-matched null at 92nd vs 95th. Its apparent regime dependence was a FULL-SAMPLE-QUANTILE artifact that vanished under causal re-derivation.
- Sample growth since W40 (2026-08-25) plus the virgin window makes the revival condition testable at essentially zero discovery cost.

### 5. The DOM-pause-blocked cluster — four independent parked families all name the same operationally-paused unlock
- RAW FACT: commit c65ae69 (2026-08-12) — "PAUSE all DOM / Level-II / Market Replay collection after resource-instability incident" (owner risk-control, not falsification).
- RECORDED CLAIMS (`PARKED_NOT_DEAD.md` rows 36, 39, 48, 49): sweep-and-reclaim (W40), MAE structural-invalidation stop (W42), entry-timing family (W54), hold-duration filter (W55 — "the prize is real and large: −15.02 pts/session in sub-37-min trades, 60% of all trades … NOT REACHABLE" from the object's own features) each state tick/DOM intrabar information as the only revival path.
- Memory/Program-C context: MNQ tick 187 dates (128 pre-burn) were never read due to a hard-coded `symbol="NQ"` in build_registry.py (a bug), and Databento GLBX.MDP3 holds ~2,300 CME NQ MBO sessions. The pause is the single operational lever gating four documented families at once.

### 6. The volatility-normalized-offset / ATR-blend family — killed three times by threshold placement, never once by sign
- RECORDED CLAIMS: campaign #1 H-006 passed Wave 2 then was downgraded INCONCLUSIVE with all DSR figures withdrawn (9e074f0); campaign #3 Wave-14 ATR-blend R2 "CLOSED, **closest miss yet**" (6f3b7cc); ATRPOOL01 pooled 2006-2026 re-adjudication **FAIL 0.8910 vs 0.90** red-team-confirmed (e0d69d8 / commit 578 line "ATRPOOL01 FAIL (0.8910 vs 0.90)"); A1A2_ATR_AUDIT — "A1 shows a real, modest, broadly-distributed tail benefit; A2's mechanism test FALSIFIES" (25ec9bd).
- A first-principles researcher should adjudicate this family ONCE, with a preregistered bar chosen before seeing 0.89 again.

### 7. ONRANGE — a verified 96.2% structural fact closed by one-shot POLICY, not by exhaustion
- RECORDED CLAIMS: ONRANGE01 — "owner claim VERIFIED (96.2% RTH breaks ON range, 20y)" (8178106) but first-break continuation monetization fails all economic gates (264d8c4); ONRANGE02 mid-to-extreme −$27/trade (0d213e3). Both "family closed **one-shot**" — the closure budget was a policy choice; exactly two monetizations of a 20-year structural regularity were ever attempted (memory: "overnight-range axis 4-quadrant dead" refers to the same two waves plus quadrant diagnostics).
- Not a promise of alpha — but the file record does not support "the ON-range structure is unmonetizable", only "two specific monetizations fail".

### 8. Deep-history event conditioning — a free, committed 2005-2021 macro calendar that has never been joined to the deep-history objects
- RAW FACT: commit 3de524d (2026-08-07) — "Historical 08:30 release calendar 2005-2021 (BLS primary sources, committed BEFORE W9-3 readout)". Used once (campaign #4 B-FADE read), never since.
- RECORDED CLAIM (W105b, e0dd176): the modern calendar (`c01_announcement_calendar.csv`, 145 rows 2022-2026) shows announcement sessions are 3.9× richer for XM_CONFLICT; "Still absent from disk and UNTESTED: FOMC minutes, mega-cap earnings, roll dates, surprise magnitudes."
- The macro-surprise-magnitude lane is closed N-bound (71 modern sessions, DATAGATE_EVENTRESPONSE) — but N-boundedness is a MODERN-window statement. The 2005-2021 calendar × the 2005+ NQ 1-min substrate (SWMinuteExport, 96/838) gives hundreds of release sessions for the deep-history objects (TSMOM depth 2009, FOLLOW_MORNING 20-yr blocks). Nobody has ever run that join.
- Same category: ES BBO **64 sessions, ZERO ever read** (3180bb5, now on the frontier); 780M order-flow events extracted then lane closed underpowered (c101a7a); VX/VXM already in NT8, $TICK to ~2013, nine unextracted 1-min stores (Program C census).

### 9. Campaign #4's three PARKED scalping candidates — the precedent is that this parking lot produced P1's engine
- RECORDED CLAIM (204bc5a): "Program B resolves to three parked candidates, zero frozen" — B-MOM (regime-local), B-FADE (UNCONFIRMED-POSSIBLY-RECENT, 507ba04), B1-overnight (marginal; "orchestrator declines the freeze", 4833781).
- B-MOM — parked as regime-local in campaign #4 — became **51% of P1's net** in campaign #7 (1e91f84: "this repo has twice judged B-MOM regime-local without connecting it to P1"). The parking lot has already yielded the program's main engine once.
- RAW FACT: MONITOR-02 (2027-08-01, `MONITOR02_PROTOCOL.md`) covers the combined re-read — far away but at least scheduled. B-FADE's status ("possibly-recent") has never been re-read since 2026-08-07 despite W114's momentum finding reframing what fades fight against.

### 10. NIGHT — the overnight displacement channel (W96), an explicitly 2026-shaped object parked on a specificity null
- RECORDED CLAIM (`PARKED_NOT_DEAD.md:56-76`): fails the session-shift null at 88th vs 95th bar, but passes chronology (t24 +$858/wk) and is "overwhelmingly a 2026 object" (−682/−390/+514/+402/**+2,099** by year). Standing facts bought: overnight SHORT is dead (−$41,741; short edge is RTH-only) and overnight friction is $19.77/ctrRT vs P1's $14.52. Revival condition: ≥95th on the session-shift null. As with item 3, nothing schedules the re-read of an object whose one live year is the most recent one.

## 3. Category findings not in the top-10

**(b) Bug-killed families — verified status:**
- **MS-BBO-CANDIDATE-1**: VOID via int32-overflow lookahead (`bbo_v1.py:119`; np.arange(-30,0)*1e9 overflows; 15/30 offsets positive to +2.065s). RAW FACT from `runs/MSBBO_DEPLOYMENT_FREEZE_20260828/out/void_audit.txt`. **Correctly buried**: the corrected causal object was computed and is −$1,785.88/session (RESEARCH_FRONTIER.md:97), and the frontier's no-rerun rationale (discovery budget consumed) is written down (RESEARCH_FRONTIER.md:136-139). Not a revival target.
- **W78–W84 powerless rolling gate** (fd7b05f/9af45f5: oracle battery scored a strictly-dominant object 0%): W85 re-adjudicated and 4 verdicts reversed; pair {BMOM+X9a} got a full honest retest (W86-88, failed specificity 92nd vs 95th; later W103's integer grid puts the pair at zero weight). Handled — but the bug class ("a gate with no power") is a standing lesson for GENESIS gate design.
- **Full-sample-quantile artifact class**: 4 named casualties (W40 axis-B, W41 clock basket, W50 withdrawal 360d800, W40-amendment). All withdrawn/retested; the class is documented. WE_W03's one-bar look-ahead and W42's E2/E3/E4 look-ahead arms were rerun/voided properly.
- **BREADTH01** failed "by frozen letter (era-significance gate-misfit)" (c94f210) and the audit then found "rho-complementarity regime-robust" (c5266a8) — a letter-of-gate kill where the audit partially rehabilitated the mechanism; the 15-ETF TSMOM replication was never re-posed with a fit gate.

**(c) Cost-model corrections and their blast radius:**
- W82 (959b3d4): measured spread at P1's trading times = 2.93 ticks = **$14.65/RT vs the assumed $10** — "C1 stress line optimistic for 82 waves." Direction of error: waves W01–W81 were charged too LITTLE, so historical kills survive; historical passes were repriced (2026 → $249/wk). W89 (36dfb54) made friction candidate-specific (BMOM RTH-only $12.99; X9a charged per-trade not per-contract — "errors partly cancel: 2:3 moves −0.7%").
- W82 amendment 1 (c82c424) RAW-FACT-relevant defect: the 1-min substrate is back-adjusted while the 1s grid is raw front month (constant +282.25 offset) — any future substrate join must respect this.
- CLAUDE.md §6 (binding): research headline (commission + modelled spread) and NT8 net (template, zero slippage) "are not the same quantity" — no family was found that died purely from confusing the two, but W44 caught the shipped C# running a 3× finer clock than the port (fc3ffda) before it could contaminate parity.

**(e) Named-but-never-run:**
- `RESEARCH_FRONTIER.md:46-47` (RAW FACT): row 7 "Does latent state add information beyond raw features? — **NOT RUN** — RR_W001's continuation rule forbids it"; row 8 blocked on #6.
- Deep-research archives: Track I passes A/B/C = **34 engine ideas** (11 auction + 12 DSP + 11 downside-risk, d9ee50d) and "3 mechanism-expansion passes (24 candidates archived)" (7abeb79); Engine-3 consumed only 15-18 of these across 5 slates before the axis was PAUSED by decision rule, not exhaustion (CURRENT_TRUTH.md:67-69 — "OHLCV-substrate engine hunting is PAUSED").
- W83's "Q3/Q4 queued": Q4 WAS carried into W84 (RAW FACT: `runs/WE_W84_Q3/spec.yaml:42`), and W107 ran the AFT lane — the frontier docs are more complete than the commit subjects suggest. The one framed-but-never-waved question: W84's "the real trade is Q0 vs Q1" (3a9e556) was overtaken by the W85 gate-power crisis and never became a wave.

**(d) One-time archives worth knowing exist** (RAW FACTS, from commit --stat / ls): grid1s + sechilo 1-second substrates (d3c62e5); ES/RTY/YM 1-min 1.57-1.62M bars each (713b0d3/65dd499/3151800) — these ARE used (XM_CONFLICT inputs); YM/RTY/CL grids from PORTABILITY-01; 164-image OTR corpus under version control (6d194c0).

## 4. Integrity notes for GENESIS

- The history is append-only in practice: 15 deletions in 1,002 commits, every one explained in its commit message, and the two doc deletions were independently re-confirmed by a second consolidation pass (94efd52). No evidence of history rewriting; failed experiments are retained with their specs.
- The repo's own self-correction density is extreme (retraction/withdrawal commits: 8017301, 2d20fef, 22dff45, 44a8678, fed4831, 32b21f4 among many). The reboot's forensic risk is therefore NOT hidden failure — it is **parked success with unmonitored revival conditions** (items 1, 3, 4, 10) and **calendar/protocol drift during document regeneration** (item 1's dropped shadows being the proven instance).
