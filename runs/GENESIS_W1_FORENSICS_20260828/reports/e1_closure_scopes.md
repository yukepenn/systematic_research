# TEAM E1 — CLOSURE-SCOPE ATLAS (PROJECT GENESIS)

Date of read: 2026-08-28. All repository reads were READ-ONLY. No data values >= 2026-08-01 were
read; no blind-pool file was opened; no mcp__crosstrade tool was called.

**Evidence tags used throughout:**
- **RAW FACT** = I read the cited file this session and the statement matches its text.
- **RECORDED CLAIM** = a repo document asserts it; I did not independently recompute it.

Note that nearly everything below is by construction "RAW FACT that the repo RECORDS X" — I
verified the documents say what I report, not the underlying computations. Where I could
cross-check documents against each other, I say so.

---

## 0. MASTER TABLE

| family | exact tested spec | verdict | closure scope AS RECORDED | closure scope ACTUALLY SUPPORTED | classification | OPEN REMAINDER |
|---|---|---|---|---|---|---|
| TSMOM V1 (multi-mkt dev) | 21 CORE roots, `mean(sign(R21,R63,R126,R252))`, inverse-vol→equal-risk-per-root→per-sector, daily rebalance, $4.36+1-tick PRIMARY/2-tick STRESS, dev 2009-03-30→2018-12-31 (2,265 days) | FAIL G2 (Sharpe 0.226), G3 (5/9 yrs), G6 (72.3 % equity) | DEVELOPMENT-ONLY, DISCOVERY-CONSUMED | same | CORRECTLY CLOSED AT SCOPE | none inside family (V2/H1 spent the clean windows); cost-drag finding (47.2 %) motivates only low-turnover constructions, which are forbidden as rescues |
| TSMOM V2 (252d slow) | byte-identical machinery, signal = `sign(R252)` only, validation 2019-01-01→2022-12-31 one shot | FAIL V2-G3 (2/4 positive yrs; 5/6 gates pass, Sharpe 0.577) | steady-premium claim CLOSED at this specification; 2019–2022 consumed | same | CORRECTLY CLOSED AT SCOPE | the run itself names the only legitimate follow-up (tail-hedge role) — and H1 then tested and killed it |
| TSMOM-TAIL-H1 | byte-identical 252d object, claim = portfolio tail diversifier; expanding inverse-vol allocator, 26w warmup; window 2023-01-01→2026-05-30, 178 weeks, one shot, ONE-SIDED BLIND (TSMOM leg blind, incumbent leg discovery-consumed) | 4/5 gates FAIL (Δ fixed-DD −$1,602/wk; worst-decile mean −$169.70); G5 pass = dilution trap | TSMOM CLOSED for this campaign, both roles; ρ=0.013 but no return = "ballast, not a hedge" | same | CORRECTLY CLOSED AT SCOPE | "TSMOM (all roles)" label in ALPHA_EVIDENCE row 55 is 2 tested roles, not all conceivable roles — but every within-family variant is spec-forbidden and both clean windows are consumed. Genuinely open: XSMOM (cross-sectional) on the futures substrate — never tested anywhere |
| CARRY_V1 | 10 roots / 4 sectors, front-vs-second slope, centred within-sector rank, weekly rebalance, dev 2009–2018, $4.36+1-tick | FAIL C6 (SI = 84.1 % of +root) & C7 (metals 98.5 %); 6/8 pass incl. two-sided causality | "carry CLOSED at this specification"; explicitly NOT closed: curve info in general, other maturity pairs, other normalisations, ≥3-roots-per-sector universes | same — and the report documents the structural cause (n_sector=2 degenerates rank to ±1 in 3 of 4 sectors) | CORRECTLY CLOSED AT SCOPE (universe structurally defective, and named as such) | ALPHA_EVIDENCE standing question #4: curve information on a universe with ≥3 roots/sector. 2019–2022 and 2023–2026-05-30 NEVER READ. SI/GC metals-only explicitly forbidden (post-hoc subpopulation) |
| VOLUME_LIQUIDITY_V1 | 21 roots, ROOT_TOTAL log1p volume z vs 63-session median/MAD, sector demean, clip ±3, weekly long-low/short-high, 40 % sector cap, 2010-03-23→2018-12-31 (458 wks) | 10/12 gates FAIL; gross −$17,033 BEFORE costs; 56.5th/39.8th pctile of its own two nulls; mirror also loses | NO CANDIDATE / CLOSED AT EXACT SCOPE; negative BOUNDED: \|r\|<~0.02 weekly invisible at n=444 | same — exemplary bounded closure | CORRECTLY CLOSED AT SCOPE | sub-detection-threshold effects (need breadth/N); note SPEC §9 forbids OI, volume×trend, ML etc. **as rescues of this family** — a fresh preregistered OI family is not literally the same object but inherits the discovery-consumed window |
| W111 intraday volume (weekly_edge) | 5 mechanisms (decay slope/ratio, effort-no-result, absorb bar, exhaust extreme), decide 11:48, fill 11:49, hold 15:44, size 1, no stop, 1,012 sessions; secondary 10:01→11:29 | PRIMARY −$233/trade at 0.0th pctile of coin null; 3 of 5 BELOW 5th pctile of volume-decile-matched null (anti-predictive) | baseline §6: "volume exhaustion (0.0th pctile, three of five anti-predictive)"; baseline §7: "1-min participation: anti-predictive" | anti-predictiveness demonstrated ONLY at this afternoon fade geometry + this direction rule | mildly OVER-GENERALIZED in the §7 shorthand ("1-min participation: anti-predictive" with no geometry qualifier); the §6 entry is fine | volume information at other decision events / other geometries / non-fade uses. Also W111 produced the W108 correction: class-conditional signatures are definitional without an unconditional control |
| MS-BBO (CANDIDATE-1) | 58 quote-complete sessions (48 evaluated), RTH 60 s grid 10:00→15:30, 20 features, frozen model, MAX_FILL_WAIT 1,000 ms | **VOID — LOOK-AHEAD**: `np.arange(-30,0)*NS` int32 overflow put 15/30 path offsets up to +2.065 s AFTER t; leak worth 134.8 % of the $5,125/session result; causal object −$1,786/session, OOF corr 0.0072 | all §1/§3 figures, 7 gates, 4+1 leak probes VOID; corrected object recorded consumed-and-closed, NOT a new candidate; not inverted | same | **CLOSED BY DEFECT** (the discovery run); the causal re-read is discovery-grade negative on consumed data — BBO information itself is neither confirmed nor cleanly falsified | ALPHA_EVIDENCE standing question #3: ES+NQ joint sub-minute quote state (baseline void ⇒ non-incremental form); the 19-session NQ BBO blind pool (falsifier-grade only, MDE $2,996/session, n=19; EFFECTIVE_14 is a SUBSET of it, not a second shot); ~20 genuinely unread ES BBO sessions |
| MS-LAST (V1) | certified order-invariant Last-only features (23; tick-rule family DROPPED — 274 % order-sensitivity), 60 s clock+horizon, lookbacks 60/300/900 s, Ridge + shallow GBM (2 attempts), frozen TOD cost schedule incl. $2.50 Last-vs-mid surcharge, 104 consumed sessions / 139,371 decisions | Ridge −$987/session (22.4th pctile of activity-matched placebo); refitted session-block null NOT beaten (1.0th pctile = churn); upper 95 % bound −$569 < both materiality bars ($246/$49) | FALSIFIED-NULL-CLOSED **narrow**: this feature family + horizon + model budget + policy + costs. NOT closed: Last-only alpha generally, other horizons, other feature classes, 60 s predictability as such | same — AFTER a same-day 4-part adjudication correction (martingale claim RETRACTED; fake np.roll null replaced; "CI∋0 ⇒ no information" invalid; MDE denominator fixed to 2.86×/14.37× materiality) | CORRECTLY CLOSED AT SCOPE **after correction**; first version was OVER-GENERALIZED (martingale) and PARTLY DEFECTIVE (shift-invariant null) — both caught in-repo | 141-session Last-only blind pool UNSPENT, reserved for a genuinely different mechanism; other horizons/feature classes |
| ESNQ_V1 | ES↔NQ price-side, 60 s horizon, 11 relative-by-construction features, Ridge, 200 ms ES embargo, 44 dev sessions (36 OOF), frozen cost | X1 −$18,114 net, X5 stress, X7 0/4 quartiles FAIL (X6 non-adjudicative on a negative object); OOF corr +0.0034; NQ-only control also negative | CLOSED at exact scope; NOT closed: other horizons, other feature classes, sub-100 ms semantics | same; one recorded ORDER-OF-OPERATIONS BREACH (P0-3 parity finished after economics; 0 action disagreements found, so object unaffected) | CORRECTLY CLOSED AT SCOPE | ESNQ_BLIND_EFFECTIVE_14 UNSPENT (power 0.000 at mu_claim $0 → withheld); ES tick/BBO→NQ (tick-level, not 1-min) recorded UNTESTED in ALPHA_EVIDENCE row 64 |
| order-flow→P1 (closed twice) | v1: coverage gate before any feature — 71 P1 entries / 3.3 % of surface, MDE $564/entry = 4× mean. v2: extracted 780 M events → 104 sessions, 141 entries, MDE $517 = 4.61× mean on full-horizon target; ceiling: needs 998 sessions vs "713 exist" | CLOSED-BY-DATA / UNDERPOWERED (v1); CLOSED-BY-POWER "unreachable at any coverage" (v2, echoed in ALPHA_EVIDENCE row 60) | "needs 998; 713 exist; unreachable at any coverage" | **the arithmetic is WITHDRAWN**: INFORMATION_FRONTIER_00 F1 — 713 was the LOCAL NT8 store ceiling, not the universe; Databento GLBX.MDP3 has ~2,300 CME NQ MBO sessions from 2017. Closure holds only at current holdings | **CLOSED BY POWER**, but the "at any coverage" clause was OVER-GENERALIZED — already retracted in-repo (F1) | rank-1 acquisition candidate in the EVI ranking; session-scoped target needs ~455 covered sessions (achievable); nothing was ever TESTED — no feature, no model |
| breadth_lab (campaign #5) | BREADTH01: 12-1 monthly sign TSMOM, 15 ETFs, 2003–2026. BREADTH02: bond-slope + div-yield carry, 2003–2026. BREADTH03: Simon-Campasano contango-conditional short-VIXY, 2011–2026. All preregistered one-shots | all three CLOSED_FAIL_ONE_SHOT | free-data tier "fully adjudicated"; trend/VRP real-but-insignificant at free-data sample sizes; carry dead post-2020 | BREADTH01 failed on an **era-significance gate-misfit** (its own ledger says so; disclosed G2 CI_lo +0.84 %/yr PASSED, ρ_losing +0.04, +3–4 %/yr on Solar losing days both eras); BREADTH03 was a priced coin-flip that "landed tails" (Sharpe 0.506, year-block CI_lo −0.51 %) | BREADTH01: **CLOSED BY DEFECT** (gate design, acknowledged in-ledger); BREADTH03: **CLOSED BY POWER**; BREADTH02: correctly closed | funded breadth (40–60 futures markets) is the recorded unlock; NEW since closure: VX/VXM futures found already in NT8 at $0 (F3) — the VRP family's data constraint has materially changed since BREADTH03 used an ETF proxy |
| ONRANGE01 (overnight break) | Part 1 diagnostic + ARM_A first-break continuation, N=4,961, 2006–2026, C1 costs; spec frozen pre-P&L | claim TRUE (96.2 % break) but G2/G3/G7/G9 FAIL: +$29.8/trade, CIs span zero, top-1 % = 2.76× net, longs-only carry | family CLOSED one-shot; offset/exit/window re-skins ineligible | same; G4 placebo arm's execution model invalid (gap-through fill defect) — disclosed and NOT used in the verdict; real-arm bias favorable ⇒ FAIL strengthened | CORRECTLY CLOSED AT SCOPE (defect disclosed, non-verdict-bearing) | overnight range as a **conditioner** (not trigger) is genuinely different and is live in campaign #7 (on_range_rel is XM's tail-magnitude marker, W110/W123) |
| ONRANGE02 (mid→edge) | drift-to-nearer-ON-extreme from RTH open, N=5,122, 2006–2026, ARM_B stop variant, mirror arithmetic | −$27.0/trade, year-block CI entirely negative; mirror ≈ −$1.7 net after friction | with ONRANGE01: "overnight-range axis mapped in all four quadrants on 20 years"; family CLOSED one-shot | supported for the four tested quadrant OBJECTS (unconditional, RTH-open-anchored, no-stop/opposite-stop) | CORRECTLY CLOSED AT SCOPE; the "all four quadrants" phrasing is about the 2×2 trigger/mirror grid and is fair | G8 disclosure: +$138k on Solar losing days (ρ −0.17) — "overpriced insurance"; a conditional/cheapened version was never tested (and is barred as a re-skin within campaign #3, which is itself closed) |
| KDJMA01 | KDJ(9,3,3)+MA120 5-min ladder, 20-pt stop, ladder exits, session-close flat, 20 yrs, N=43,951, C1 costs; MA127 disclosure arm | net −$796,946; **gross −$3.77/trade BEFORE costs**; negative 20/21 years | family CLOSED one-shot; param re-skins ineligible; the 26×/31× owner claim priced as survivorship | same; construction caveats disclosed (KDJ params unknown in source, overnight behavior unspecified) — margin (CI upper −$12.8) dwarfs reading variance | CORRECTLY CLOSED AT SCOPE | none of value |
| seasonality / time-of-day | (a) W18R1_M1_VOLSEASON: TOD vol-seasonality re-scaling of E10 threshold, 3-min slots, gates Sharpe/CDaR/top-10-retention. (b) WE_W32/W41: bar-clock granularity. (c) W38: hour-of-day short restriction. (d) day-of-week: never run | (a) arm_FULL 0/3, axis closed unconditionally post-red-team — but premise CONFIRMED at 11.04× TOD spread; (b) W32 all-arms-rejected then **overturned** by W41 on the true engine (3-min clock adopted); (c) failed circular-shift null at 65th pctile = generic exposure reduction | (a) closed as threshold-modulation policy inside E10; (b) W41 supersedes W32; (c) parked | (a) the INFORMATION (TOD vol profile, RTH carries 81 % of P&L on 35 % of bars) is not closed — only that policy; (d) scalping-lab P4's "day-of-week closed permanently" sits in a SUPERSEDED record resting on DR-E external priors that Amendment 6 formally reclassified as PRIOR | (a) correctly closed at scope; (b) **W32 = CLOSED BY DEFECT** (harness dropped HTF tilt/hysteresis/combiner), caught by W41's B1c reproduction gate; (d) **never actually closed by evidence** | day-of-week / calendar seasonality on NQ has NO in-repo preregistered test; TOD vol profile as an input to a NEW object is untested |
| macro-event families | DATAGATE_EVENTRESPONSE: CPI/NFP/FOMC calendar (129 in-window events, 71 effective event sessions), P1 decision surface reach 153/2,131 = 7.18 %; MDE $1,896.67 = 9.8× lane-scaled bar ($194.06); one macro event = one observation (§20) | CLOSED-BY-DATA; "UNDERPOWERED, not NULL"; ~96× N (≈220 yrs) needed; F4: surprise magnitudes cannot move an N-bound gate at any price | same — a model-free calendar constraint | same | **CLOSED BY POWER** (properly labeled; nothing tested) | more event TYPES (PPI, claims, PCE, ISM, auctions) → ~280 sessions, MDE ~5× bar — better, still short; note the event FLAG is a live component of XM's tail-winner state (W110) and XM is NOT an event trade (W105B: $408/trade on 304 non-announcement trades) |
| HTFMECH01 (campaign #3) | diagnostic decomposition of HTF tilt's marginal net by year and by side (sign(T_bar)); zero construction | REAL, direction-concentrated finding (short-side −$22,020 for Product A) — then CORRECTED by HTFDIR01: the counterfactual conflated the agreement up-weight with the SHORTHALF overlay; short-AGREEMENT boost is value-ADDITIVE (−$8,932 to remove) | diagnostic only, no promotion; combined-mechanism tables stand, single-channel attribution corrected | same | NOT A CLOSURE — a diagnostic whose attribution needed (and got) a correction | direction-conditioned HTF multiplier named as a preregistrable lead — never built (campaign #3 closed). Separately, campaign #7's HTF→P1-action-value surface is CLOSED NULL (RR_W004: 61.5th pctile, known-null control at 77.0th beats both real arms) — that closes HTF FEATURES → ACTION VALUE, not HTF structure generally |
| OPPORTUNITY00 (flat sessions) | frozen arming identity `K·g·(1+dL) ≥ 16` verified 0 disagreements / 1,620,044 bars; 1,058 sessions = 638 active / 420 flat; A-C1..A-C5 preregistered | A-C1 PASS 77.9 % (flat sessions are NOT quiet — 84 % of active range, ≥3 ten-point reversals on 100 %); **A-C2 FAIL — decisive**: only two identifiable state families, both pre-disqualified (entry-threshold mining forbidden; mirrored short leg falsified 5×) | original text "found no third family" — CORRECTED 2026-08-28: no third **admissible** family **within the currently owned and examined surface**, under preregistered governance; explicitly NOT established: flat sessions unpredictable, price info exhausted, density research closed | the correction is the supported scope; closure is BY GOVERNANCE, not by proof of non-existence | CORRECTLY CLOSED AT SCOPE **after the correction**; the original sentence was OVER-GENERALIZED and the repo caught it | the 39.7 % coverage hole is real and moving; P1_NEAR_ARM_STATE exists (median flat M_max 2.830 vs threshold 3.0 with the Solar term at zero); any NEW information surface that arms flat sessions is fair game — what is barred is loosening P1's threshold or reviving the short leg |
| scalping_lab (campaign #4) | Zone F (5–120 s holds, 8–32 t moves) via ~14 killed families + predictability-ceiling C5/C5b (best top-decile lift +2.42/+3.21 pp vs 7–10 pp needed) + FSS-9/FSS-10/E1 + independent red team | "NO QUALIFIED FAST NQ SCALPING EDGE FOUND IN THE TESTED RESEARCH UNIVERSE" per Amendment 6 §9, WITH RT-1's four scope conditions (regime 2025-08→2026-05; FSS-6 absent-not-falsified; UNRESOLVED list carried — B1 overnight power catch-22, S2a short side; ceiling library/clock-relative, E1 sample-limited) | as stated, conditioned | supported as conditioned; the EARLIER DR-E-based closure ("Zone F externally corroborated dead", 30-min floor, day-of-week etc.) was OVER-GENERALIZED and formally WITHDRAWN by Amendment 6 (external evidence reclassified as PRIOR) | CORRECTLY CLOSED AT SCOPE (final form); the interim closure was the over-generalization and was repaired | 3 parked Program-B candidates (B-MOM regime-local PF 1.013 on 16 unseen years; B-FADE OOS = 1/30 of IS; B1 overnight) forward-monitored, re-read ≥ 2027-08; regime scope means post-2026-05 fast-microstructure is untested |
| Solar Wave era (frontier.yaml etc.) | ES_PORTABILITY: blind transfer of NQ-calibrated k to ES (Sharpe −0.329; "fitting k separately per instrument was NOT done"). PORTABILITY_01: YM/RTY/CL strict-1/N transfer 0/3 → with ES 0-for-4. B01 family-B all arms negative; C2 sleeve interaction destroys adaptive core; WAVE_INDEX conditioning null; C01T2 NQ-block K-scaling falsified; H007 split-exit, H011 stop-execution failed | as listed; "NQ-SPECIFIC alpha confirmed; structural-alpha claims removed" | portability closures are about PARAMETER TRANSFER, not per-instrument viability — frontier.yaml says so itself; weekly_edge W43 later re-derived the two dimensional constants per instrument and still failed, but records that the SIGNAL family itself was never re-derived per instrument | transfer closures CORRECTLY SCOPED in the yaml; the shorthand "NQ-specific alpha confirmed" drifts broader than 0-for-4 transfer evidence; B01's F04/F05/F07/F08 were deprioritized on **inherited**, not direct, negative evidence (the yaml says "inherited") | mostly CORRECTLY CLOSED AT SCOPE; two flagged shorthands | per-instrument re-derivation of the full signal family (VolMult set, sigma window, throttle) on ES/RTY/YM — explicitly named open in PARKED_NOT_DEAD row W43; F04/05/07/08 were never directly tested |

---

## 1. Cross-cutting findings (the reboot-relevant part)

### 1.1 The repo's closures are, in final form, unusually well scoped — because it keeps correcting them
RAW FACT: at least seven closure statements were narrowed or voided by in-repo corrections
*after* first being recorded too broadly:
1. MS-LAST "martingale" → retracted same day; fake null replaced (`runs/MSLAST_CONTRACT_20260827/REPORT.md:9-63`).
2. OPPORTUNITY00 "no third family" → scope-corrected to "no admissible family within the owned
   surface" (`runs/NQ_OPPORTUNITY00_20260828/REPORT.md:1-20`).
3. ALPHA_EVIDENCE first version flattened everything to STRUCTURAL → replaced
   (`research/operational/ALPHA_EVIDENCE_CLASSIFICATION.md:9-14`).
4. W32 clock verdict → overturned by W41 on the true engine (`runs/WE_W41_CLOCK2/REPORT.md:1-14`).
5. W108 fade-class signature → shown definitional by W111's unconditional control
   (`runs/WE_W111_VOLDECAY/REPORT.md:75-97`).
6. Order-flow "998 needed vs 713 exist" → 713 exposed as local-store ceiling, arithmetic withdrawn
   (`runs/INFORMATION_FRONTIER_00_20260828/REPORT.md:18`).
7. MS-BBO candidate → VOID on int32 look-ahead found by independent re-implementation
   (`runs/MSBBO_DEPLOYMENT_FREEZE_20260828/REPORT.md:1-50`).
The reboot should treat FIRST-VERSION closure sentences as suspect and FINAL-version scope
paragraphs as the binding object.

### 1.2 CLOSED BY DEFECT list (tests that were themselves buggy)
- **MS-BBO-CANDIDATE-1** — the only outright void: `np.arange(-30,0)*NS` int32 overflow; leak =
  134.8 % of result. Its OWN L2 lag probe (−$1,490/session) was the bug announcing itself and was
  explained away ("consistent with a fast-decaying signal") — RAW FACT,
  `runs/MSBBO_DEPLOYMENT_FREEZE_20260828/REPORT.md:92-116`. Note the meta-lesson recorded there:
  nulls/placebos/mirrors CANNOT detect feature look-ahead because every replicate inherits it
  (line 130-134).
- **WE_W32** — harness dropped HTF tilt/hysteresis/combiner; verdict overturned by W41.
- **W111 secondary geometry, first run** — 40-bar minimum longer than the 31-bar window; repaired,
  primary bit-identical (`runs/WE_W111_VOLDECAY/REPORT.md:66-73`).
- **ONRANGE01 G4 placebo** — invalid gap-through fills; disclosed, non-verdict-bearing (verdict
  overdetermined by G2/G3/G7/G9) (`research/system_master/ONRANGE01_OVERNIGHT_BREAK/REPORT.md:31-41`).
- **MS-LAST original "dependence-preserving null"** — `np.roll(v,s).mean()` is shift-invariant;
  all 85 replicates equalled the observed statistic; replaced by a refitted session-block null.
- **MS01A quote-location** — same-millisecond quotes admitted; 69.6 % "inside spread" → 8.9 %
  corrected; the COST conclusion survived (`runs/MSLAST_CONTRACT_20260827/REPORT.md:111-138`).
- **BREADTH01** — era-significance gate misfit acknowledged in its own ledger row; the disclosed
  economics partially PASSED (`research/breadth_lab/CAMPAIGN_STATE.md:14`).

### 1.3 CLOSED BY POWER list (no hypothesis was ever tested)
- Order-flow → P1 action value (twice; see master table; arithmetic ceiling withdrawn by F1).
- Event response (71 effective sessions; MDE 9.8× lane bar; "UNDERPOWERED, not NULL" —
  `runs/DATAGATE_EVENTRESPONSE_20260827/REPORT.md:11-14,61-79`).
- BREADTH03 VRP (priced coin-flip; landed tails).
- INT02 partial: strong-materiality ($246/session) closed, WEAK $49/session NOT (upper bound
  +$68.16) — RECORDED CLAIM, `ALPHA_EVIDENCE_CLASSIFICATION.md:58`.
- MS-LAST as an equivalence test: MDE 2.86× the strong materiality bar — equivalence held because
  the point estimate was far negative, not because the test was precise (RAW FACT, correction 1D).
- BBO blind pool: n=19 ⇒ MDE $2,996/session — "can FALSIFY a large claim, cannot CONFIRM a modest
  one" (RECORDED CLAIM, `ALPHA_EVIDENCE_CLASSIFICATION.md:49`).

### 1.4 Named over-generalizations still worth guarding against
1. "TSMOM (all roles) CLOSED" (row 55) — two roles tested. Defensible because every variant is
   spec-forbidden, but a reboot should read it as "both TESTED roles".
2. "1-min participation: anti-predictive" (CURRENT_BASELINE §7) — established at one afternoon
   fade geometry, five mechanisms.
3. "NQ-specific alpha confirmed" (frontier.yaml PORTABILITY_01) — supported claim is 0-for-4
   PARAMETER TRANSFER after costs; per-instrument signal-family re-derivation never done
   (PARKED_NOT_DEAD row W43 keeps this open explicitly).
4. Scalping-lab P4 "closed permanently: … pre-FOMC standalone, day-of-week …" — lives in a
   SUPERSEDED record based on DR-E external priors that Amendment 6 formally demoted to PRIOR.
   Day-of-week seasonality has NO in-repo preregistered test (RAW FACT: grep of REJECTED_IDEAS.md
   and Amendment 6 finds no day-of-week entry; the only appearance is the superseded P4 list in
   `research/scalping_lab/CAMPAIGN_STATE.md:209-211`).
5. B01's F04/F05/F07/F08 "deprioritized with inherited negative evidence" — inherited, not direct.
6. Baseline §6's "seven fade mechanisms killed → family dead" — CURRENT_BASELINE itself carries
   the standing correction ("too strong"; kills constrain the CLOCK, not the class; whether
   reversal sessions can be monetised is UNKNOWN) — `CURRENT_BASELINE.md:348-353`.

### 1.5 Protected assets a reboot must not touch (all RECORDED CLAIM, cross-consistent across 4 docs)
- ≥2026-08-01 seal (VIRGIN); 2026-05-31→07-31 BURNED.
- NQ BBO 19-session blind pool (18 pristine, 1 metadata-exposed; eligibility frozen at `022c543`).
- ESNQ_BLIND_EFFECTIVE_14 — a STRICT SUBSET of the BBO 19, not an independent shot.
- ~20 genuinely unread ES BBO sessions (of 79 RTH-complete; 44 consumed by ESNQ dev, 15 in the
  original blind manifest).
- 141-session Last-only pool (never touched; reserved for a genuinely different mechanism).
- CARRY validation 2019–2022 and holdout 2023–2026-05-30 (never read).
- VOLUME 2019–2022 and 2023→2026-07-31 (never read).
- TSMOM: NOTHING left — V2 consumed 2019–2022, H1 consumed 2023–2026-05-30.

### 1.6 The frontier as the repo records it (RECORDED CLAIM, F1–F5)
`runs/INFORMATION_FRONTIER_00_20260828/REPORT.md`: the free tier is NOT exhausted — VX/VXM futures
already in NT8 (never named in any repo data doc); $TICK back to ~2013 (~9–13 free years vs
believed 2022); MNQ tick 187 dates invisible due to a hard-coded `symbol="NQ"` in
build_registry.py (a bug, not an absence); nine unextracted 1-min stores; free Cboe OI; unprobed
COT. Rank-1 paid candidate: Databento GLBX.MDP3 NQ depth/MBO (~2,300 sessions), the only item that
reverses a recorded permanent closure. Standing warning applied there: four consecutive negatives
in the adjacent microstructure lane; `uncorrelated + unprofitable = ballast`.

### 1.7 What a genuinely different hypothesis could still test (union of OPEN REMAINDER column)
1. **Depth/MBO order flow at scale** (Databento; reverses the only "permanent" closure; needs
   fresh preregistration + P0-3-grade independent parity before any model).
2. **ES+NQ joint sub-minute quote state → 60 s NQ** (non-incremental form; data-capable at 59
   sessions; export-gated).
3. **Curve/carry on a ≥3-roots-per-sector universe** (CARRY00 shows FX closed-by-data; RTY/RB/HO/HG
   recoverable free).
4. **XSMOM on the futures substrate** (never tested; substrate exists and is certified).
5. **VX/VXM term-structure conditioning / VRP with real futures** (data newly known to exist at $0;
   BREADTH03's ETF-proxy power bound no longer binds).
6. **A new observable that arms P1-flat sessions** (must be neither a loosened threshold nor the
   short leg; the near-arm state M∈[2.83,3.0) is the descriptive lead).
7. **Day-of-week / calendar seasonality** — genuinely untested; low prior, cheap.
8. **Per-instrument signal-family re-derivation on ES/RTY/YM** (PARKED_NOT_DEAD W43).
9. **More event TYPES** for the macro lane (gets MDE from 9.8× to ~5× the bar — still short; only
   worth it bundled with other uses of the calendar).
10. **Forward/prospective evidence** — the shadow protocol (preflight READY) and the calendar-gated
    sealed-pool reads; for TSMOM/scalping parked candidates, forward re-reads are the ONLY clean
    windows left.

### 1.8 Chronology caution for the reboot
The repo dates several key events 2026-08-27/28 (TSMOM V2, H1, CARRY_V1, MS-BBO void,
INFORMATION_FRONTIER_00, GENESIS commits A/B) — RAW FACT from `git log` and file headers. The
environment header for this session says 2026-08-18; the working tree and MEMORY reflect the
2026-08-28 state. All statements above are made against the tree as read.

---

## 2. Citation index (primary sources read this session)
- `research/weekly_edge/CURRENT_BASELINE.md` (full read)
- `research/operational/ALPHA_EVIDENCE_CLASSIFICATION.md` (full read)
- `runs/TSMOM_V2_SLOWTREND_20260827/{REPORT.md,SPEC.md}`; `runs/TSMOM_TAIL_H1_20260828/{REPORT.md,SPEC.md}`
- `research/multi_market/TSMOM_V1_DEVELOPMENT.md` (gates §1–§3)
- `runs/CARRY_V1_20260828/REPORT.md`
- `runs/VOLUME_LIQUIDITY_V1_20260828/REPORT.md`; `runs/WE_W111_VOLDECAY/REPORT.md`
- `runs/MSBBO_DEPLOYMENT_FREEZE_20260828/REPORT.md`; `runs/MSBBO_V1_20260828/{SPEC.md,CORRECTION_20260828.md}`
- `runs/MSLAST_CONTRACT_20260827/REPORT.md`
- `runs/ESNQ_V1_20260828/REPORT.md` (incl. §H exact-scope paragraph, lines 197–201)
- `runs/DATAGATE_ORDERFLOW_20260827/README.md`; `runs/DATAGATE_ORDERFLOW_V2_20260827/REPORT.md`
- `runs/DATAGATE_EVENTRESPONSE_20260827/REPORT.md`
- `runs/INFORMATION_FRONTIER_00_20260828/REPORT.md`
- `runs/NQ_OPPORTUNITY00_20260828/REPORT.md` (incl. 2026-08-28 scope correction)
- `research/breadth_lab/CAMPAIGN_STATE.md`
- `research/system_master/{ONRANGE01_OVERNIGHT_BREAK,ONRANGE02_MID_TO_EDGE,KDJMA01_5M_LADDER,HTFMECH01_TILT_MECHANISM}/REPORT.md`
- `runs/W18R1_M1_VOLSEASON/REPORT.md`; `runs/WE_W32_CLOCK/REPORT.md`; `runs/WE_W41_CLOCK2/REPORT.md`
- `research/scalping_lab/CAMPAIGN_STATE.md`
- `research/frontier.yaml` (status extraction + failed-entry bodies)
- `research/weekly_edge/PARKED_NOT_DEAD.md` (full read)
- `runs/WE_W56_BREADTH/REPORT.md` (header)
