# TEAM J1 — SKEPTICAL REVIEW OF PROJECT GENESIS PREMISES

Session date 2026-08-28. READ-ONLY session; no repo/NT8 file touched; no CrossTrade tool called;
no data value ≥2026-08-01 read; no blind-pool content opened. Evidence tags: **RAW FACT** = I
verified the artifact/text/count myself this session; **RECORDED CLAIM** = a repo document asserts
it. Note that most "numbers" here are RAW FACTS *about what artifacts say* and RECORDED CLAIMS
*about the market* — that two-level distinction is applied throughout.

---

## P1 — "The incumbent P1/PCT earns ~$1,230/week net with the recorded population"

**VERDICT: HOLDS WITH CAVEATS as internally consistent backtest arithmetic; UNSUPPORTED as a
statement of expected forward income.**

### The evidence chain (all RAW FACT that the artifacts say this)

- `runs/WE_W103_CONSOLIDATE/out/components.csv:2` — `P1_PCT, 2401 trades, weekly 1393.57,
  fixdd 1230.36, maxdd 22930.67, t 4.164`. This is the terminal artifact of the headline.
- `runs/WE_W103_CONSOLIDATE/REPORT.md:47` quotes the same row; window 2022-07-01→2026-08-01,
  1,058 sessions, 213 weeks (`CURRENT_BASELINE.md:327`).
- Scaling arithmetic checks out: 1,393.57 × (20,245 / 22,930.67) = 1,230.4 ✓ (RAW FACT, recomputed).
- `research/weekly_edge/FROZEN_INCUMBENT_20260827.md:90` freezes $1,230 as the forward reference.

### The $1,166 episode — retracted-then-unretracted, and what survives it (RAW FACT of the record)

Commit sequence (git log, RAW FACT): `5cc4825` freeze → `3b5af8a` "the canonical $22,931 was
DEFECTIVE. The headline was 5.2 % too high" ($1,166.24) → `8017301` RETRACTION, same day
(2026-08-27). `runs/FWD_DD_RECONCILIATION/REPORT.md:1-31` carries the retraction banner.

What a hostile reader keeps from the episode:

1. **The retraction is arithmetically sound but the exposure it opened is real.** The same trade
   stream under a Sunday-ending week label gives maxDD **$24,212.92**; ISO-week-on-session-date
   gives **$22,930.67** — a **5.6 % swing in the risk denominator from bucketing convention alone**
   (`FWD_DD_RECONCILIATION/REPORT.md:24-27`). The convention that survives is the one already
   embedded in the W103 code (`run_we_w103.py`, per the retraction), so it does trace to the
   original artifact — but it was implicit in code, canonized as "the convention" only *after* the
   discrepancy surfaced, and it is the flattering one of the two. The headline's fixed-DD figure is
   convention-dependent in its last ~5 %: **$1,166–$1,230 is the honest quotation band.**
2. **The fixed-DD metric uses the coarsest drawdown.** The same report's invariance table
   (REPORT.md:60-68): trade-level maxDD **$29,454**, session **$28,052**, weekly **$24,213** (their
   rebuild). "Weekly $ at fixed $20,245 max DD" is leverage-invariant, as claimed — but the $20,245
   is a *weekly-resolution* DD. At the same scaling, the realized trade-level DD is ~28 % deeper
   (~$26,000, k-scaled). Any consumer treating $20,245 as "the drawdown you would have felt" is
   wrong by construction.
3. **A residual was never closed**: the retracted analysis left $78 (0.34 %) unexplained between its
   `pnl_commonly` rebuild and $22,931, and the 213-week (W103) vs 211-week (FWD rebuild) count gap
   is not reconciled anywhere I found.

### "The recorded population" is not one population (RAW FACT — four artifacts, four counts)

| artifact | count |
|---|---|
| `WE_W103_CONSOLIDATE/out/components.csv` | **2,401** trades |
| `runs/FWD_DD_RECONCILIATION/REPORT.md:63` (RR_W001 ledger) | **2,139** trades |
| `EXECUTION_MANIFEST.md:42` / CURRENT_BASELINE (decision events) | **2,131** Python |
| NT8 parity | **2,137** trades |

Likely reconcilable (unit-trades vs entries vs decision events, e.g. 2,139 entries with 262 size-2
= 2,401 unit-trades), but **no document reconciles the four**. "$/trade" claims silently depend on
which denominator; a reboot inheriting "the recorded population" inherits an ambiguity.

### Cost model and reproduction status

- The $1,230 is net of $4.36/ctrRT commission **plus a modelled spread of $14.44/ctrRT** that
  exists only in the Python world (`EXECUTION_MANIFEST.md:73-78`). NT8 charges commission only.
- **What was independently reproduced (NT8 Strategy Analyzer): the decision series, not the
  economics.** Parity = 99.672 % matched, weekly ρ 0.9852, net −1.05 % **commission-only on both
  sides** (`EXECUTION_MANIFEST.md:42`). The spread model — worth roughly $14.44 × ~2,400 unit-trades
  ≈ $35k over the window, i.e. ~11 % of gross — has never been validated against real fills.
  RECORDED CLAIM: it comes from `WE_W82_FILLAUDIT` on 45 tick sessions of a 2025-08→2026-05
  microstructure sample, extrapolated to 2022-2026.
- **Evidence class under hostile reading:** the repo's own tag is right — `DISCOVERY_CONSUMED`
  (`CURRENT_BASELINE.md:48-49`). It is a FACT about one Python backtest (internally reproducible to
  $0.33), decision-level cross-validated in NT8, **zero forward evidence** (forward ledger empty,
  `EXECUTION_MANIFEST.md:131-135`; shadow not started). The repo's own bootstrap gives
  **P(13-week forward cum < 0) = 14.5 %** even taking the number at face value
  (`FWD_DD_RECONCILIATION/REPORT.md:123`). It must never be quoted as expected forward income.

---

## P2 — "The 4 protected pools are intact"

**VERDICT: HOLDS WITH CAVEATS — and the premise's own pointer is wrong.**

**The pointer is wrong (RAW FACT):** `research/operational/LOCKED_FORWARD.md` is the campaign-#3
champion freeze (R5-E10, 2026-08-07) plus the global ≥2026-08-01 virgin-data rule. **It names no
pools.** Pool truth is distributed across `research/operational/ALPHA_EVIDENCE_CLASSIFICATION.md`,
`research/data/DATA_ASSET_REGISTRY.md`, `research/information_frontier/*`, and individual run
reports. A reboot that "verifies pools from LOCKED_FORWARD.md" verifies nothing.

**The four pools as actually recorded (all RECORDED CLAIM):**

1. **NQ BBO blind pool, 19 sessions** — 18 pristine-never-materialized, **1 (`2025-08-13`)
   METADATA-EXPOSED** in the exporter incident; eligibility rule frozen at `022c543`, manifest
   hash-frozen at `17bbb2d` (`ALPHA_EVIDENCE_CLASSIFICATION.md:49`). ⚠️ The as-recorded manifest
   sha256 (`84a8575a…`) turned out to be a CRLF working-tree hash; the normalized hash
   (`92010fc6…2b8e`) was substituted post-hoc — content identical, but the freeze hash itself needed
   a correction. MDE $2,996/session at n=19: **falsifier-grade only**.
2. **ESNQ blind pool, original 15 → EFFECTIVE 14** — one session transiently materialized during
   the recorded exporter incident (README.md:64-68). "Intact" is already false for n=15; the repo's
   defense is quarantine, not prevention. ⚠️ `INFORMATION_FRONTIER_00` REPORT.md:71 records this
   pool is a **strict subset of the BBO 19** — "not a second shot."
3. **141-session Last-only tick pool** — unextracted, frozen with hashes at `fd7b05f`
   (`RESEARCH_FRONTIER.md:90`). ⚠️ Near-miss recorded: `CURRENT_INFORMATION_MAP.md:33` shows these
   141 were listed as a *free extraction item* before a same-day governance correction struck it
   ("free in dollars, NOT free in governance"). Intactness survived by self-catch, not by mechanism.
4. **SEALED forward pool ≥2026-08-01** — "~19 sessions as of 2026-08-27", location "not read"
   (`DATA_ASSET_REGISTRY.md:70`).

**Has anything read them? No mechanical answer exists.** RAW FACT: I found no access-log mechanism
for pool files anywhere (grep for access/read logs returns only unrelated docs; the one
`research/data_forward_sealed/DOM01/README.md` hit was not opened, per seal rules). Intactness rests
on (a) frozen content hashes for the 141 and the BBO manifest — which prove *definition* integrity,
not *non-access* — and (b) incident self-reporting, which has already fired twice. **"Intact" is a
claim the repo cannot affirmatively prove about the NT8 `.ncd` store; it can only prove it hasn't
recorded a violation.** Disk-side verification is another team's task.

---

## P3 — "2026-05-31..07-31 BURNED, ≥08-01 SEALED" — structural or conventional?

**VERDICT: PARTLY STRUCTURAL, MOSTLY CONVENTIONAL. Sealed dates can be read today without any
loud failure.**

What actually stands between an agent and sealed data:

- **Physical absence (the strongest layer, but accidental):** the materialized research substrates
  end before the seal — `nq1m_2005_202605.parquet` ends 2026-05-29, `nq_1m_2022_2026.parquet` ends
  2026-07-31 (`DATA_ASSET_REGISTRY.md:48-49`). `load_deep()` (`research/weekly_edge/src/run_we_w17.py:28-51`,
  RAW FACT) filters only by the caller-supplied window — **no seal assertion anywhere in the load
  path**. It cannot serve sealed data only because the files stop.
- **Opt-in guards:** `research_sdk/session_boundary.py:145-158` (`assert_not_locked_forward`,
  `authorized_backtest_window`) raise `BoundaryError` — but only if called. Nothing wraps the data
  layer; `prereg_guard.py` gates spec-before-result, not data dates. Build-time enforcement exists
  in exactly one place I found: internals are "hard-dropped at build" (`DATA_ASSET_REGISTRY.md:56-58`).
- **The live holes, recorded by the repo itself** (`runs/INFORMATION_FRONTIER_00_20260828/REPORT.md:75-76`,
  RECORDED CLAIM): "several 1-min stores run to **2026-08-27** and the NQ tick store to
  **2026-08-11** — truncation must be enforced in the harness, not assumed." Sealed-date values sit
  on this machine right now. Any `pd.read_parquet`/`.ncd` read of those stores, any fresh NT8
  export, or any CrossTrade `GetBars`/`RunStrategyBacktest` with `to` past the boundary reads
  sealed data **silently** — those tools do not consult `session_boundary.py`.
- **BURNED is a label, not a lock (by design):** W103's t3m/t6m/2026-YTD rows overlap the burned
  span and are freely computed and quoted (`WE_W103_CONSOLIDATE/REPORT.md:104`). Correct under the
  doctrine (burned = no fresh-evidence claims), but a reboot must understand nothing stops a read.

**What the reboot must do differently:** treat the seal as enforced by *agent discipline plus file
absence*, not by the system; mandate `authorized_backtest_window()` before every windowed read; and
treat every CrossTrade-capable agent as a seal hazard (this wave's ban on `mcp__crosstrade__*` is
the correct control — it must persist beyond this wave).

---

## P4 — "The free-tier findings (VX in NT8, $TICK 2013, MNQ tick) are real"

**VERDICT: UNSUPPORTED as stated ("usable history"); plausible as leads. Every claim is a
presence/probe claim, and the repo's own history says presence ≠ usable.**

Source: `research/information_frontier/CURRENT_INFORMATION_MAP.md` + `runs/INFORMATION_FRONTIER_00_20260828/REPORT.md`
(both 2026-08-28, RECORDED CLAIMS), found "by probing the connection and the disk."

- **VX/VXM "already in NT8, daily AND 1-minute, multiple contract months."** No date range, depth,
  or session count is stated anywhere. NT8's local db holds what was cached: the registry's own
  recently-added stores (6J, ZN, MGC) begin **2025-12-30** (`DATA_ASSET_REGISTRY.md:66-68`) — the
  base-rate expectation for an unnamed instrument in the db is *months of cache, not a history*.
  "Term structure" additionally needs overlapping months and a causal roll; the registry documents
  that this provider serves no continuous contracts and displays **decade-ambiguous symbols**
  (`ES 12-06` and `ES 12-16` both "ESZ6", `DATA_ASSET_REGISTRY.md:33-37`). File presence in the db
  does not imply one usable year of term structure.
- **$TICK back to ~2013.** The entire evidence is bars returned at **two point probes**
  (2013-01-02, 2015-01-02 — `INFORMATION_FRONTIER_00/REPORT.md:19`). Two points prove nothing about
  continuity, gap structure, or methodology consistency of a computed breadth index across 13 years.
  The repo has already convicted probe grids once in the *other* direction ("2016 probe... not a
  measured floor — nothing beneath 2016 was ever asked", `DATA_ASSET_REGISTRY.md:26-31`); grids
  mislead symmetrically. And the payoff is overstated: the store's $TICK is RTH-only, covering
  **35.7 % of P1 decisions** — a "permanent ceiling" (`DATA_ASSET_REGISTRY.md:160-163`) that more
  years do not lift, while internals→P1-action-value is already CLOSED (INT01) and internals→direct
  return produced NO CANDIDATE (INT02).
- **MNQ tick, 187 dates / 128 pre-burn.** "187 dates" is a **FILE-PRESENCE count** — the exact class
  the registry's standing rule forbids from power claims ("INSTRUMENT-DATES ARE NOT DISTINCT USABLE
  SESSIONS", `DATA_ASSET_REGISTRY.md:9-20`; NQ's own deflation ran 310 → 243 Last-usable → 99
  quote-usable). Expect material attrition before "128 usable pre-burn sessions." The `symbol="NQ"`
  bug in `build_registry.py` is a real finding about *why it was invisible*, not evidence about
  *what the files contain*. And the same window (2025-08→2026-05) that made the NQ signed-flow lane
  CLOSED-BY-POWER (998 needed) binds MNQ too; "a separate order book" is a hypothesis — MNQ/NQ flow
  is heavily arbitraged, and a same-day sibling census (`runs/ASSET_CENSUS_20260828/REPORT.md:49`)
  calls micros "same underlying... zero new information" in the daily/curve context. The two docs
  are in tension in scope, which is itself the caution.
- **Meta-attack:** the census's own moral — "'we don't have X' meant 'this repo hasn't fetched X'" —
  inverts cleanly: **"the connection has X" is a claim about a probe, not about coverage.** The same
  epistemic error, opposite sign. F5 in the same report shows the memory/frontier layer carrying a
  stale rank for an already-closed lane — this document layer churns within single days.

**What the reboot must do differently:** treat F2/F3/R10 as *census tasks with a mandatory
usable-session deflation step*, not as data assets; require date-range + gap census before any EVI
number is attached; never let "in NT8" enter a power calculation.

---

## P5 — "P1's economics survive its own selection debt: 123 waves, ~400 runs"

**VERDICT: UNSUPPORTED — the debt is real, only locally policed, and globally unquantified.**

- **Counts (RAW FACT):** `runs/` contains **400 run directories**; **121** `WE_W*` wave dirs + 2
  `WE_*_PARITY_*` = **123** `WE_*`. The "123 waves" claim is accurate as a directory count.
- **What multiplicity control exists:** per-wave, per-scan permutation checks (W55, W57, W71's
  216-cell context, RR_W002B/C best-of-K bars — RAW FACT via grep of `research/weekly_edge`).
  **No global cross-wave deflator exists anywhere.** The only quantified selection cost in the
  campaign is Portfolio B's best-of-six: **$245.71/wk (13.9 %) observable — "and that is the
  OBSERVABLE part only"** (`CURRENT_BASELINE.md:27`). P1 itself — 13-member ensemble, 4 combiners,
  32-config vote, OR-gate, throttle q=0.8, delta gate, quality-sizing threshold, box levels, PCT
  denomination — is a ~10-choice composite, every choice adopted on the same 1,058 sessions.
- **The honest deflation a hostile reader applies:**
  1. The largest single recent increment, ABS→PCT (+$345/wk, +39 %), is recorded by the repo itself
     as **"Direction overwhelming, dollars not established. Forward data decides"** (paired
     magnitude p 0.057-0.058, `ALPHA_EVIDENCE_CLASSIFICATION.md:52`), and it **reverses −31.4 % on
     2006-2021** with 90.8 % of its gross difference in 53 sessions. Deflated headline floor:
     **$885/wk (ABS)**.
  2. Adopted steps cleared ~95th-99th-percentile nulls — but across ≥121 waves of scans, several
     such clearances are *expected by chance*. Per-wave gates control per-wave error, not
     campaign-wise error.
  3. Week-convention sensitivity adds the $1,166 variant.
  - **Deserved quotation: "$900–$1,230/wk, in-sample, post-selection, regime-local, with
    P(13-wk forward loss) ≈ 15 % on its own bootstrap."** The naked $1,230 and t=4.16 deserve the
    repo's own tag — DISCOVERY_CONSUMED — read strictly: *not a forecast*.
  - The one genuinely held-out support is the Solar/B-MOM core's 2006-2021 deep-history read
    (W17-era) — consumed once, early, ~100 waves of subsequent modern-window tuning ago.

---

## P6 — The reboot directive itself: implicit assumptions that could be false

1. **"Verify pools from LOCKED_FORWARD.md"** — wrong register (see P2). The directive's own map of
   the repo is one revision stale in places; several of its premise-statements ("~$1,230 with the
   recorded population", "4 pools in LOCKED_FORWARD") embed the drift they ask me to audit.
2. **Assumes repo docs are mutually consistent on a given day.** RAW FACT of contradiction:
   `ALPHA_EVIDENCE_CLASSIFICATION.md:60` still says order flow is "Unreachable at any coverage
   (998 needed, 713 exist)" while `CURRENT_INFORMATION_MAP.md` C1 (same date, 2026-08-28) withdraws
   exactly that arithmetic (~2,300 Databento sessions). The standing-questions list in
   ALPHA_EVIDENCE was corrected **twice in one day** (lines 96-111). "One authoritative source per
   fact" is aspirational; GENESIS agents must diff-check any fact they inherit across ≥2 docs.
3. **Assumes the clock is trustworthy.** The repo records a harness clock reporting **2026-08-18**
   while documents said 08-27/28 (`CURRENT_INFORMATION_MAP.md:63-64`); my own session's clock
   flipped 08-18 → 08-28 mid-session (RAW FACT). Every seal boundary and every "pre-read"
   attestation is a date comparison; a wrong clock silently converts sealed into unsealed.
4. **Assumes 12 parallel agents are observers.** They are wave 124. Twelve agents reading the same
   burned substrate and proposing conclusions is itself a selection event; unless GENESIS
   preregisters its synthesis rule (how the 12 reports combine, decided before reading them), the
   reboot manufactures the very selection debt it audits. Also: any GENESIS agent with live
   CrossTrade access is a seal hazard (P3) — the tool ban must be program-wide, not J1-specific.
5. **Assumes "the incumbent's number" is one number.** Four trade counts, two week counts, two DD
   conventions, two cost models (P1). Premises should be stated as artifact + line, never as a
   number.
6. **Assumes parity certification ≈ independent reproduction of economics.** It is decision-level,
   commission-only (net −1.05 % different). The spread model — the difference between $1,390/wk and
   $1,230/wk-class figures — has never been reproduced outside Python.
7. **Assumes document stability.** The frontier flipped from "free surfaces exhausted" to "NOT
   exhausted" within a day; MS-BBO went 7/7-gates-passed → VOID (int32 overflow look-ahead) within a
   day. Any premise inherited by 11 agents should carry its commit SHA, because it may be retracted
   before the wave ends — the $1,166 episode shows retraction latency of hours in *both* directions.

---

## Summary table

| premise | verdict |
|---|---|
| P1 backtest arithmetic | HOLDS WITH CAVEATS ($1,166-1,230 band; population ambiguity; weekly-resolution DD) |
| P1 as forward income | UNSUPPORTED (DISCOVERY_CONSUMED; zero forward evidence) |
| P2 pools intact | HOLDS WITH CAVEATS (2 recorded exposure incidents; no access-log mechanism; wrong register pointed to) |
| P3 seal structural | PARTLY — physical absence + opt-in asserts; silent read paths exist today (NT8 stores to 08-27, CrossTrade tools) |
| P4 free-tier "real" | UNSUPPORTED as usable history; plausible as census leads |
| P5 survives selection debt | UNSUPPORTED — globally unquantified; honest band $900-1,230 in-sample |
| P6 directive assumptions | Multiple false/fragile: stale pointers, doc contradictions, clock trust, 12-agent multiplicity |
