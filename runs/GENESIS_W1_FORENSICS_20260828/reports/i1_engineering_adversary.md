# TEAM I1 — ENGINEERING-ADVERSARY ATLAS (PROJECT GENESIS)

Date: 2026-08-28. Scope: every bug class this repo has produced, the guard layer, the gaps, and a
certification checklist v1. Every item tagged **RAW FACT** (verified this session by reading the
cited file/commit or executing the cited test) or **RECORDED CLAIM** (a repo document/commit
message asserts it; not independently re-derived this session).

Method: `git log --all` (1,002 commits — RAW FACT) grepped for bug/defect/look-ahead/leak/phase/
VOID/retract/correction/wrong/invalid; then targeted reads of run reports, incident docs, and the
entire `research_sdk/`; then execution of every runnable guard self-test.

---

## PART 1 — THE BUG ATLAS (by class, with precise locations)

### Class A — Silent integer overflow in time arithmetic (the MS-BBO +2.065 s leak)
- **RAW FACT** `research_sdk/timegrid.py:1-23` documents the defect verbatim: `bbo_v1.py:119`
  (`runs/MSBBO_V1_20260828/src/bbo_v1.py:119`, RAW FACT — site confirmed by the 0A scanner run this
  session) computed `step = np.arange(-30, 0) * NS`. On Windows/NumPy 1.26 `np.arange(-30,0)` is
  **int32**; `-30e9` overflows silently; the intended offsets `[-30s,-1s]` became
  `[-2.115s, +2.065s]`, **15 of 30 positive**, so 7 path features read up to **2.065 s past the
  decision instant**.
- **RECORDED CLAIM** (`runs/MSBBO_DEPLOYMENT_FREEZE_20260828/REPORT.md:1-40,87`): the leaky object
  showed **$5,124.76/session, t 6.76**, passed **7 preregistered gates + 4 leak probes**
  (commit `1a188e0`) and all 5 deployment self-parity gates, and beat a *refitted* null at the
  100.0th percentile — **because every null replicate recomputed the same leaky features**. Leak
  worth **$6,910.64/session = 134.8 %** of the result; causal object **−$1,785.88/session**. VOID
  (commit `d5fa86f`). Found on **run 1 of the independent streaming engine**: 13/20 features exact,
  7 off by hundreds of dollars, and the same-instant control `midret_30s` matching exactly.
- **Why the old causality gate missed it** (RAW FACT, `research_sdk/causality.py:18-24`): L1
  asserted `feature_ts < t` for the lookups *at* t and passed with 0 violations — it never examined
  the 30 rolling-path offsets.
- **RAW FACT** (executed): `python research_sdk/test_timegrid.py` → ALL PASS; on this interpreter
  the regression reproduces (native dtype int32, range [-2.115098s, +2.064771s], 15/30 positive).
- **RAW FACT** (executed `audit_defect_classes.py`): 4 currently-overflowing sites, **all** in the
  voided run's preserved sources or the pinned regression test; **one production site** claim of
  commit `dc65bc0` is consistent with the scan.

### Class B — Bar-stamp phase errors (W44/W52; W102c anchor)
- **RAW FACT** `runs/WE_W52_NINJASCRIPT/REPORT.md:44-55`: v1/v2 of the NinjaScript port shifted all
  timestamps −1 minute as a "defensive fix for W44's phase error" on the premise "Python stamps
  start, NT8 stamps end". **The premise was false — both are END-stamped** (bar stamped 09:31 opens
  09:30:00), so **the defensive fix WAS the phase error**: decision agreement 98.767 % with the
  shift, **99.985 % without** (v3, VALIDATED). Origin of the CLAUDE.md §6 END-stamp rule and the
  ≥99 %/2 % parity bands.
- **RECORDED CLAIM** (commit `bfd23ea`, W102c): a subtler recurrence — bars end-stamped means the
  bar stamped 09:30 OPENS at 09:29; W101/W102 anchored the "RTH open drive" one minute inside the
  pre-open. "Not a lookahead, but not free": $675→$560/trade, +98.1 %→+45.1 % portfolio value.
- Guard today: **convention + parity only.** No code artifact asserts stamp semantics.

### Class C — Nulls that share the candidate's defect / mis-specified nulls
- MS-BBO's 100th-percentile null recomputed the leaky features (Class A above) — the null was
  *powerless against the bug class it was supposed to catch* (RECORDED CLAIM, freeze report).
- **RAW FACT** `research/scalping_lab/CAMPAIGN_STATE.md:55-70`: W1-1 Z1 DC-ladder "persistence"
  RETRACTED by W2-0 — omega in `z1_dc_ladder.py` measures TOTAL MOVEMENT ext-to-ext
  (RAW FACT: `amps[k]=abs(ext−prev_ext)`, `z1_dc_ladder.py:24-31`), so the martingale null is r≈2,
  not 1; the "gross positive" was trigger-jump algebra (+0.67–1.3t on a martingale).
- **RECORDED CLAIM** (commit `78a10c7`): WE_W55 "my N3 null was an oracle". (commit `22dff45`):
  MS-LAST adjudication "retract 'martingale', replace a non-null with a real one".
- CLAUDE.md §4 (RAW FACT of text): independent draws inside a correlated family set the bar far too
  high; shared draw per session + circular shifts + effective-K required.
- Guard today: **convention only. No structural guard anywhere checks null construction.**

### Class D — Key-type mismatch joins (numpy.datetime64 vs pandas.Timestamp)
- **RAW FACT** `research_sdk/keysafe.py:1-18`: CARRY00 run 1 — `.unique()` gives datetime64,
  `.groupby()` dict gives Timestamp keys; **every lookup returned None**, reporting ZERO
  simultaneously-live contract pairs for all 25 roots — a completely plausible CLOSED-BY-DATA
  verdict. Caught only by human expectation (ES with 71 contracts cannot have zero overlap).
- **RAW FACT** (scanner executed): **2 at-risk unguarded sites remain**:
  `research/scalping_lab/src/python/w8_bmom.py` (col `date`) and
  `runs/SMV2AK_VOLUME_BARS/src/step1_volume_bars.py` (col `sess_date`).

### Class E — State-machine startup degeneracy (the DC counter mode-0 bug)
- **RAW FACT** `runs/NQ_OPPORTUNITY00_20260828/src/opp00.py:181-186` (comment + fixed code): the
  directional-change counter's mode-0 startup originally used a single shared `ext` that tracked
  whichever way price moved and **could never register a reversal → dc == 0 for every session on
  the first run**. Caught by plausibility ("a 264-point session cannot contain zero 10-point
  reversals"). Fix: track BOTH extremes (`mx`,`mn`) in mode 0. Guard: none structural; the fix is
  local.

### Class F — Window/population filters on the wrong unit
- **The 47-session leak — RAW FACT** `runs/VOLUME_LIQUIDITY_V1_20260828/src/vl_independent.py:171-178`:
  the independent engine originally filtered on `mon >= date_max` — the **WEEK LABEL** — so the week
  stamped Monday 2018-12-31 (running into 2019-01-04) put **47 sessions of the held-back window into
  the development result**. The primary filtered on `date`; the **6E parity gate between the two
  implementations surfaced it**. A blocking assert now exists (`vl_independent.py:195-196`,
  "WINDOW VIOLATION in the independent path").
- **session_date vs session_id — RAW FACT** `research/intraday_opportunity/PROGRAM_B_AMENDMENT_20260828.md:129-140`:
  active sessions 712→**638** (counted by calendar date, but one NQ session spans two dates:
  1,058 sessions vs 1,056 dates); trades/calendar-session 2.27→**2.014** because the numerator was
  the **whole-substrate 2,401** trades including the 2022-01→06 warm-up against an in-window
  population of **2,131**; and the "P1 is RTH-only, 6.5 h" error (session close read as RTH close)
  **propagated into an owner directive** before correction — the costliest variant of this class.
- Guard: `research_sdk/test_session_unit.py` — **RAW FACT executed, 6/6 PASS**, including
  real-ledger checks (2,131 rows, 638 active sessions, 1,058 vs 1,056).

### Class G — Exporter/materialization truncation and data-contract violations
- **12,000,000-row cap — RAW FACT** `runs/ORDERFLOW_EXPAND_20260827/REPORT.md:34-39`: **17 of 48**
  v1 raw NQ tick files sit at exactly 12,000,000 rows — **silently truncated mid-session**
  (s20260206 ends 13:28:44). `SWScalpTickExport_v4` raises the cap to 25 M and rolls per session;
  the largest session seen is 22.8 M rows. The registry carries `known_truncation` per asset
  (RAW FACT, `research/data/build_registry.py:106-123`).
- **ESNQ blind-export incident — RAW FACT** `runs/ESNQ_V1_20260828/INCIDENT_BLIND_EXPORT_20260828.md`:
  the first ESNQ export wrote blind session **s20250813** because **`RunStrategyBacktest`'s `from`
  is a strategy property, not a data-loading bound** — NT8 loaded a full session earlier than
  requested and the session-rolling exporter wrote it. Deleted unread in ~90 s; only file
  size/event counts exposed; session recorded NOT CONSUMED; manifest deliberately NOT mutated.
  Fix: `SWScalpTickExportAllow_v1` allow-list **enforced where bytes are written, FAIL-CLOSED,
  validated against this exact failure** (skipped 20250813, wrote s20250814 only). Standing
  data-contract fact: **a date range is not an isolation mechanism**.
- **RECORDED CLAIM** (commit `846df1e`): 2026-07-17 is a truncated session (ends 10:53, 83 RTH
  bars) inside the extended substrate, found by a harness check looking for something else.
- **RECORDED CLAIM** (`6c90e32`, MS01A): the BBO stream passes freshness, **FAILS ordering**, quote
  size NOT CERTIFIED — delivered object ≠ assumed object, same family as the merge-back-adjusted
  daily series fact.

### Class H — Census/registry blindness from hard-coded scope ("we don't have X" = "we never looked")
- **RAW FACT** `research/data/build_registry.py:197-206`: the NT8 tick-store census row is
  hard-coded `symbol="NQ"`; grep finds **no "MNQ" anywhere in the file**. **RECORDED CLAIM**
  (`research/router/RESEARCH_FRONTIER.md:113` + row 2): this hid an entire **MNQ tick store
  (187 dates / 128 pre-burn, never read)**; same census wave found VX/VXM already in NT8 and $TICK
  to ~2013 (repo believed 2022). **The bug is still unfixed in build_registry.py** — the correction
  lives only in `research/information_frontier/` docs.
- Prior instances (RECORDED CLAIMS): BBO count measured at wrong granularity (`44a8678`);
  262-vs-243 reconciliation (`e2aeff6`); "no blind BBO pool exists" → a genuine Last-only one did
  (`aa55669`); `load_deep` hardcoding a file ending 2026-05-29
  (`research/weekly_edge/STATE_OF_THE_SYSTEM.md:388`); the Databento "713 sessions in the universe"
  = local store only (memory/frontier). Repeated ≥3 times.

### Class I — Full-sample statistics leaking into "causal" features
- **RECORDED CLAIMS**: W37 spec exists to "fix the score's threshold look-ahead" (`7e0a310`); the
  W41 withdrawal was the **4th full-sample-quantile casualty** (`360d800`;
  `research/weekly_edge/STATE_OF_THE_SYSTEM.md:499`); W33 chose features on a full-sample scan
  (`:520`). No scanner exists for this class.

### Class J — Intrabar / derived-substrate look-ahead
- **RAW FACT** `runs/AUCTION04_CLEAN_CAUSAL_SUBSTRATE/src/01_build_clean_substrate.py:1-27`:
  grid1s's `last` is built by `.floor("1s")` + `.last()` — a bucket labeled T aggregates [T, T+1),
  so a row labeled T can contain a trade ~1 s after T (DEFECT 2). Registry now flags it
  (`build_registry.py:163-164`). Same doc, DEFECT 1: markout columns **exactly 4× too large**
  (tick-scaled mid divided by TICK again).
- **RAW FACT** `runs/WE_W42_EXITS/amendment_1.yaml:4-11`: E2/E3/E4 exit arms VOID for look-ahead
  (using bar i's high/low to trigger a fill at bar i), found in self-review; the "best exit result
  in campaign history" withdrawn.

### Class K — Unit/dimension errors
- **RECORDED CLAIMS**: W89 — commission charged per TRADE instead of per ctrRT and a wrong rate
  ($12.99 not $14.65 for BMOM) (`68ea030`); W66 "dimensional defect in the inherited clamp"
  (`c5526a4`); W102 X1_ATR2 — "2.0 × ATR20" was a **one-minute** volatility behind a six-hour hold
  (`aafbfc1`); AUCTION03 4× (Class J). No unit system exists; convention only.

### Class L — DST / timezone / string-vs-instant
- **RAW FACT** `research_sdk/shadow_ledger.py:49-73`: the first version compared timestamps as
  STRINGS; across the EDT→EST change `'2026-11-02T08:30:00-05:00' < '09:00:00-04:00'` as strings
  but is LATER as an instant — a legitimate decision would have been refused as backfill on
  fall-back day. Caught by the shadow preflight **before the first row** (commit `7d02700`).
  Fixed: parse-to-instant, naive stamps refused. **RAW FACT executed**: selftest **11/11** incl.
  the DST case and a deliberate tamper.
- **RECORDED CLAIM** (`research_sdk/README.md:50-58`): EQV04 near-miss 2026-08-11 — EST-season UTC
  offset used on an EDT-season date; only the CME weekend gap prevented a LOCKED_FORWARD read.
  Fixed by `session_boundary.py` (no seasonal branch to get wrong).

### Class M — Import-time destructive file handles / non-atomic writes
- **RAW FACT** `research_sdk/audit_defect_classes.py:252-263` + scanner run: `void_audit.txt` was
  zeroed by a module-level `open(...,"w")` executing on import after a successful run (commit
  `1ded276` "lazy log handle"). CLAUDE.md §7 records the truncate-then-write zeroing of
  `CURRENT_BASELINE.md`. **Scanner today: 10 imported-and-destructive sites remain** (e.g.
  `runs/MSBBO_V1_20260828/src/bbo_v1.py:45`, `runs/W18R2_M5_XINST/src/run_m5.py` ×4, OTR `run_vf1/
  vf4.py`).

### Class N — Prereg violations (spec and result in the same commit)
- **RECORDED CLAIM** `research/registry/REGISTRY_GAP_NOTE.md:88`: HASH01's git-forensic audit found
  **44 run directories** with same-commit spec+results — blindness unverifiable from history.
- **RAW FACT executed**: `prereg_guard.py selftest` PASSES — clean case passes, and the known
  AUCTION04 same-commit violation (`fcaae6c`) is refused.

### Class O — False corrections / under-constrained defect hunts (the meta-bug)
- **RAW FACT** `runs/FWD_DD_RECONCILIATION/REPORT.md:1-33`: the report's own conclusion ("the
  canonical $22,931 was defective") was **RETRACTED same day** — the author matched against the
  wrong comparator (Sunday-ending vs ISO week labels: maxDD differs **5.6 %** on identical trades),
  then searched cost-model variants and reported the argmax as a mechanism (commit `8017301`).
  Related: `6294bc8` (router branch closed one step early; one "control" wasn't), `7ab9019` (two
  W119 figures were comparator artifacts, one a tautology).

### Class P — Hardcoded clocks/instruments in NinjaScript execution surfaces
- **RECORDED CLAIMS**: campaign #3 DEFECT 3 — BMOM EOD flatten hardcoded `hm >= 163900`/`155700`
  never fires on early-close sessions; **39 real margin breaches** under the pre-fix clock, 0 after
  the session-relative fix (`research/archive/campaign3_system_master/BASELINE_MODELS.md:291`,
  `research/system_master/CURRENT_TRUTH.md:317,646`). `LIVE_READINESS.md:92` records a hardcoded
  instrument silently running a decision stack on a deferred contract. NT8 resolves **stale
  classes** from `NinjaTrader.Custom.dll` — hence the rename-per-iteration rule (CLAUDE.md §6).

### Class Q — Design degeneracies visible before P&L (CARRY n_sector=2)
- **RAW FACT** `runs/CARRY_V1_20260828/REPORT.md:84-93`: with `n_sector=2` the centred rank
  `2(i−1)/(n−1)−1` takes only {−1,+1} — 3 of 4 sectors had exactly two roots, so "relative carry"
  was a full-weight binary switch. "Visible in CARRY00's coverage table before the P&L existed —
  it simply was not reasoned through." Guard: none; recorded as a design rule (≥3 roots/sector).

### Class R — Precision/evidence-class over-statement
- **RECORDED CLAIMS**: FWD_BOOTSTRAP Gaussian bands too loose in the dangerous direction
  (`d5ddf51`); V2 — forward bands reported with more precision than they had (`9e76623`);
  CRLF-vs-LF hash instability in the blind manifest (`b3b8df9`; fixed by
  `blindguard.normalized_sha256`, RAW FACT `blindguard.py:40-47`).

---

## PART 2 — GUARD-LAYER INVENTORY (what fires, what is only written down)

| Guard | Guards against | Positive test (shown to fire)? | Status |
|---|---|---|---|
| `timegrid.py` | Class A (int32 time overflow) | **YES — RAW: test_timegrid reproduces bbo_v1.py:119 on this interpreter and asserts rejection; ALL PASS** | structural, **opt-in** |
| `causality.py` (two-sided probe + `probe_rolling_path`) | Classes A, J (incl. engines that stopped reading inputs — the positive clause) | **NO standing selftest/`__main__`** (RAW: grep). Exercised inside `runs/ESNQ_V1_20260828/src/causality_probe.py` only | structural, opt-in, untested standing |
| `keysafe.py` | Class D | **NO selftest** (RAW) | structural, opt-in; 2 at-risk legacy sites remain |
| `session_boundary.py` + `test_session_boundary.py` | Class L, LOCKED_FORWARD reads | **YES — RAW: ALL PASS incl. raising cases** | structural, opt-in |
| `shadow_ledger.py` | backfill, tampering, DST, silent row-dropping | **YES — RAW: 11/11 incl. deliberate tamper + DST-acceptance case** | structural |
| `test_session_unit.py` | Class F (session unit / population) | **YES — RAW: 6/6, synthetic + real ledger** | regression test only — nothing forces new code through it |
| `prereg_guard.py` | Class N | **YES — RAW: selftest refuses the real AUCTION04 violation** | **advisory CLI — RAW: no git hooks, no CI in repo** |
| `blindguard.py` (intersection assert + `BLIND_SPEND_AUTHORIZED` + normalized hash) | Class G/blind spend | **NO selftest** (RAW). The *exporter allow-list* (.cs) was validated against the real failure; blindguard.py itself has no standing test | structural, opt-in |
| `audit_defect_classes.py` | Classes A/D/M repo-wide | Self-validating by execution (RAW run: 0A=4 all in voided/test code, 0C=2 at risk, 0D=10 imported-destructive) | scanner — must be run by hand |
| `SWScalpTickExportAllow_v1` (.cs) | Class G export isolation | **YES — validated against the exact real failure** (RECORDED, incident doc §3) | at the byte-writing layer |
| Parity bands (≥99 % decisions / 2 % trades, W52) + independent second implementation (P0-3 batch-vs-stream, 6E gate) | Classes A, B, F — **empirically the best bug-catcher in the repo** (caught MS-BBO run 1; caught the 47-session leak; 44/44 ESNQ) | n/a (a protocol) | **convention only** |
| CLAUDE.md §4-§7 rules (nulls, evidence tags, atomic writes, spec-first) | C, I, M, N, R | n/a | convention |

**Adoption is the weakness (RAW FACT):** only ~14 non-SDK files import any SDK guard (ESNQ_V1,
VOLUME_LIQUIDITY_V1, AUCTION03/04, DATA03, RR_W001). Nothing — no hook, no CI, no harness —
prevents the next engine from being written without them.

## PART 3 — GAP ANALYSIS: five unguarded surfaces most likely to make the next false alpha

1. **Null construction.** No machine check exists that a null (a) preserves dependence, (b) does
   not recompute the candidate's own possibly-defective features, (c) has the right known-answer
   value on a martingale. This class has already manufactured the campaign's single worst false
   positive (MS-BBO at the 100.0th percentile of its own null) and three retractions (Z1 omega,
   N3 oracle, MS-LAST). Highest-value fix: a null-certification harness (known-answer martingale
   input ⇒ the null must price it at ~50th percentile).
2. **Full-sample statistics inside features/thresholds** (Class I — 4 casualties, zero tooling).
   A scanner for quantile/mean/σ computed over the full frame and then used causally would have
   caught W33/W36/W37/W41.
3. **Guard opt-in-ness itself.** prereg_guard has no hook; the SDK is imported by the newest runs
   only; test_session_unit/test_timegrid run when remembered. The next false alpha does not need a
   new bug class — an old class in a new file suffices (0C's two at-risk sites are live examples).
4. **Census/registry scope hard-coding** (Class H — `build_registry.py:197-206` **still**
   hard-codes NQ; three separate "we don't have X" reversals). Any GENESIS data claim of absence
   needs an enumerate-everything-then-filter discipline, never a filtered enumeration.
5. **Single-implementation results.** Everything that survived long enough to be dangerous was
   killed by an independent re-implementation (streaming vs batch, independent vs primary, NT8 vs
   Python). Where only one implementation exists there is no equivalent guard — parity is a
   convention, not a gate a run must pass to report economics. (Adjacent: unit/cost arithmetic,
   Class K, has no dimensional typing and recurs at ~1 defect per audit wave.)

## PART 4 — CERTIFICATION CHECKLIST v1 FOR GENESIS CANDIDATES
Ordered so each check names the historical bug it would have caught.

1. **Time-arithmetic certification** — all offset/grid construction through `timegrid` (declared
   int64, asserted count/min/max/sign); run `test_timegrid.py` on the *target* interpreter
   (Windows default int is int32 — RAW). *Catches: MS-BBO +2.065 s.*
2. **Two-sided causality probe with emitted consumed-timestamps** — negative clause (corrupt after
   cutoff ⇒ bit-identical) AND positive clause (perturb inside the information set ⇒ family moves);
   `probe_rolling_path` row-by-row `max_source_ts < decision_ts`. *Catches: MS-BBO's gate-evasion,
   dead engines, W42/grid1s intrabar reads.*
3. **Independent second implementation BEFORE economics** — batch vs streaming (or Python vs NT8),
   decision-series ≥99 %, trades within 2 %, every mismatch classified; economics quoted only from
   the parity-certified object. *Catches: MS-BBO (run 1), the 47-session week-label leak (6E gate),
   W52's phase shift.*
4. **Session-unit & window certification** — populations counted by `session_id` never
   `session_date`; window filters on session date never week label; a blocking
   `max(date) < date_max` assert inside every engine; numerator/denominator populations declared in
   the spec and asserted equal. Run `test_session_unit.py`. *Catches: 712→638, 2,401 vs 2,131,
   the 47 sessions.*
5. **Null certification** — shared draw per session-family, circular shifts, effective-K; the null
   pipeline must NOT recompute candidate features; known-answer test: feed a martingale and require
   the null to score it unremarkable. *Catches: MS-BBO's null, Z1 omega r≈2, N3 oracle.*
6. **Known-answer / degeneracy probes on every counter & join** — zero-lag known-answer test on any
   cross-substrate join (W101 practice); `keysafe.assert_resolves` on every dict lookup; refuse
   all-zero / all-constant outputs without an explicit waiver. *Catches: CARRY00 empty join, DC
   counter mode-0, n_sector=2 degeneracy (a spec-time review item: any rank/weight formula
   evaluated at the actual n per group).*
7. **Data-materialization contract** — any file with rows == exporter cap is TRUNCATED until shown
   otherwise; blind-adjacent exports only through the fail-closed allow-list exporter; never treat
   `RunStrategyBacktest from/to` (or any date range) as isolation; verify delivered vs requested
   object (ordering, adjustment, span). *Catches: 12 M cap, ESNQ blind export, MS01A ordering,
   merge-back daily series.*
8. **Timezone/boundary** — windows only via `session_boundary.authorized_backtest_window`
   (BoundaryError before any read); all timestamp comparisons on parsed instants, naive stamps
   refused. *Catches: EQV04 near-miss, shadow DST defect.*
9. **Prereg mechanical check** — `prereg_guard.py check` before the run, `audit` at close; and wire
   it into a hook for GENESIS (it currently binds nothing). *Catches: the 44-directory HASH01
   class.*
10. **Unit & cost audit** — every friction in $/ctrRT with the candidate-specific rate; every
    feature carries a named unit and timescale; any ×/÷ by TICK reviewed for double-scaling.
    *Catches: W89, AUCTION03 4×, X1_ATR2 minutes-as-hours.*
11. **Absence claims at enumeration level** — any "data X does not exist" must come from an
    unfiltered enumeration with the filter applied afterwards and shown; re-run the 0A/0C/0D
    scanner clean before any freeze. *Catches: MNQ/symbol="NQ", $TICK-2013, 262-vs-243; residual
    0C/0D sites.*
12. **Write hygiene** — atomic writes for authoritative docs; no module-level `open(...,'w')` in
    anything importable; normalized hashes for manifests. *Catches: void_audit zeroing,
    CURRENT_BASELINE zeroing, CRLF hash drift.*

## Notes and negative results
- The task phrase "MS-BBO reading +2.065 s while passing 7/7 gates": the discovery run's own commit
  (`1a188e0`) says "all 7 gates + 4 leak probes pass"; the freeze report adds 5/5 self-parity
  gates. Both consistent with the atlas entry.
- The exact phrase "DC counter mode-0" appears nowhere in the repo (RAW); the matching defect is
  the `opp00.py` directional-change startup-state bug documented in Class E. The nearest other
  "counter" defects (OTR VF qty-counter semantics; Z1 DC-ladder omega) are documented separately.
- Guard self-test executions this session (all RAW FACTS): test_timegrid ALL PASS ·
  test_session_unit 6/6 · test_session_boundary ALL PASS · shadow_ledger selftest 11/11 ·
  prereg_guard selftest PASS · audit_defect_classes ran to completion (829 py files).
- No repository or NinjaTrader file was created, modified, or deleted; no data values ≥ 2026-08-01
  were read; no blind-pool file was opened; no CrossTrade tool was called.
