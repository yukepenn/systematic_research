# GENESIS II — RESUME STATE

> ## ⚡ ACTIVE 2026-09-06: CROSS-ASSET campaign — Waves 0+1 DONE, Wave 2 (native engines) running.
> Wave 1 (all 7 markets autopsied) headline: **NQ is the momentum OUTLIER; everything else
> mean-reverts.** ρ-to-NQ: ES 0.94 / RTY 0.75 / YM 0.74 / ZB 0.06 / GC 0.07 / CL 0.05 / 6E 0.15.
> Wave 2 running `wf_30d97d8a-790` (trials G00060 GC-MR, G00061 ES-NQ resid, G00062 ZB-native) →
> adversarial verify survivors → **portfolio pre-read (NQ + survivor)**. **On resume:** read the
> workflow journal / `runs/W2_*/out/`, record ledger G00060-62 SERIALLY (survives→needs verify;
> tokens PASS/FAIL/NULL/DEFECT), update FUTURES_ALPHA_MAP + MECHANISM_TRANSFER_MATRIX + CAMPAIGN_
> STATE, commit. The prize = a PORTFOLIO-ADDITIVE orthogonal engine (GC-MR best shot, ES-resid
> orthogonal-by-construction). HEAD `1fdb983`. Wave 2b: CL (EIA/shock-MR) + GC-vol + 6E + YM-resid.
> Success bar = P1-class in-sample+robust (NO forward freeze — owner). ⏰ roll cron through 09-22.

> ## (prior) CROSS-ASSET Wave 0 DONE, Wave 1 running.
> Owner reframe: transfer the NQ RESEARCH PROCESS (not P1) to other futures; prize = multi-engine
> low-corr PORTFOLIO. Home `research/cross_asset/` (CAMPAIGN_STATE, FUTURES_ALPHA_MAP,
> MECHANISM_TRANSFER_MATRIX, NQ_RESEARCH_PLAYBOOK, DATA_INVENTORY). HEAD `2287c5d`+.
> **THREE things running concurrently:**
> (1) XINST01 Lane-A transfer benchmark `wf_d97689db-200` (ES/RTY/YM/ZB, trials G00056-59) —
>     record ledger serially on completion; verify NQ-reproduction gate first.
> (2) CL extraction (agent) — recompile-path in a session break (live verified flat/closed);
>     on completion verify P1 intact + freeze a CL discovery/holdout boundary before any signal.
> (3) Wave-1 autopsies `wf_2e68fa9b-5b0` (ES/RTY/YM/ZB descriptive science + synthesis) — on
>     completion fill MECHANISM_TRANSFER_MATRIX descriptive cells + preregister the ranked Wave-2
>     NATIVE hypotheses (weight orthogonality; ZB is the a-priori prize).
> Data reality CONFIRMED: intraday-ready = NQ/ES/RTY/YM/ZB(+MNQ excl); CL needs extraction (now);
> GC/6E/SI/NG = DAILY-ONLY. ⏰ roll-crossover cron still due through 09-22.

> ## (prior) CROSS-INSTRUMENT extension XINST01 running as workflow `wf_d97689db-200`.
> **Owner directive (2026-09-06): don't buy data; instead apply the NQ/P1 approach to other big
> futures (ES/gold/FX/commodities) and build the same weekly-edge object.** XINST01 ports the
> P1/PCT mechanism to **ES/RTY/YM/ZB** (trials G00056-59) with a no-mining transfer rule + a hard
> NQ-reproduction gate; gold/FX/CL data-gated (thin local 1-min / needs recompile-path extraction).
> Spec `ebafdba`. **On resume:** read the workflow journal / `runs/XINST01_.../out/`, verify the
> port reproduced NQ P1/PCT to the dollar (if not, ALL instrument results are void — fix the port,
> re-run), then **record ledger G00056-59 SERIALLY**, update the queue + a new CROSS-INSTRUMENT
> state doc, commit. The prize is a LOW-corr positive-edge instrument (ZB) = an XM-replacement
> diversifier from a known mechanism. If ZB survives + verifies -> preregister the forward read.
> Resume with `resumeFromRunId: wf_d97689db-200` if it died mid-flight.
>
> (Wave 6 done: MC-57 ZB-forecast NULL, MC-58 rebound CLOSED-permanent; $0 intraday-alpha search
> declared exhausted; HEAD `b105899`. This extension is the owner's chosen next direction.)

> ## (prior) Formal Wave 6 ran as workflow `wf_18c63c94-84c`.
> Two formal tests + adversarial verify of any survivor: **MC-57 ZB rates-state** RV-forecast
> (G00054, the new-surface flagship — a PASS unblocks conditioning P1) + **MC-58 breadth rebound**
> profit test (G00055). Specs committed `b264405`, transcribing the Wave-5 skeptic's frozen
> primaries. **On resume:** read the workflow journal (or `runs/G2_F13_*`/`G2_F14_*/out/`), then
> **record ledger results SERIALLY** (G00054, G00055) with valid tokens PASS/FAIL/NULL/DEFECT/
> ABORTED (NOT-IDENTIFIED/CLOSED-BY-POWER map to DEFECT/NULL), update FAILURE_MEMORY +
> ACTIVE_ALPHA_QUEUE, commit. If MC-57 SURVIVES + verifies CONFIRMED → preregister Wave 7:
> ZB-state conditioning of P1 (MC-35 unblocked, the profit test). Resume the workflow with
> `resumeFromRunId: wf_18c63c94-84c` if it died mid-flight.
> ⏰ Also: recreate the roll-crossover quote cron every session through 09-22
> ([[roll-crossover-sampling-20260906]] in memory); first real sample due ≥18:00 ET tonight.
>
> (Wave 5 done: MC-54 NOT-IDENTIFIED, MC-55 refuted the FOMC vol-crush/expansion, HEAD `a583767`.)

> ## ⚠️ UPDATE 2026-08-28 ~23:00+: **SESSION RESUMED after the limit reset — the pause below is
> ## HISTORICAL.** Current state: all 16 scout reports committed
> (`runs/G2_WORLDSCAN_W1_20260828/partial_snapshot/`, 16/16 at `f25fbde`); **EXEC01 completed**
> (spread model OPTIMISTIC, $20.65/ctrRT measured — `runs/G2_EXEC01_P1_EXECUTION_20260828`,
> trial G00015, scoreboard stress row applied at `431d749`); **B1 dedup re-running as a
> file-based agent** (writes `runs/G2_WORLDSCAN_W1_20260828/out/mechanism_cards.md`), B2 skeptic
> follows, then atlas/queue + Formal Wave 1 selection. Ledger 16/16 closed.

*(original pause record, kept for history)*

**PAUSED BY EXECUTION LIMIT — NOT RESEARCH-COMPLETE.** Directive: "PROJECT GENESIS II —
CONTINUOUS NQ ALPHA HUNT" (owner, 2026-08-28). Next session resumes here.

## Exact state

- HEAD at pause: `d3aaf01` (= origin/main, tree clean at commit time)
- LIVE = NO · $0 spent · seal intact · all pools unspent · shadow start 2026-09-01 18:00 ET (OWNER)
- Ledger: `research/genesis/SEARCH_LEDGER.jsonl` — 30 records, 15 trials, 15 closed, 0 open,
  chain verified. GENESIS II adds trials to THIS ledger (README rule 1).

## Active workflow at pause (results may need manual recovery)

- **WORLD DISCOVERY WAVE 1** — workflow run `wf_f37e445c-70a` (task `wvx4exvid`), launched
  ~2026-08-28 evening: 16 scouts (a1-academic … a14-mlrep + a15-repo + a16-data) → B1 dedup
  (20–40 mechanism cards + family tree + source graph) → B2 skeptic (kill/triage + top-8 EVI +
  3–6 Formal-Wave-1 pick).
- Script: `...\707cc7ae-...\workflows\scripts\genesis2-world-discovery-w1-wf_f37e445c-70a.js`
- Journal (full agent returns): `...\707cc7ae-...\subagents\workflows\wf_f37e445c-70a\journal.jsonl`
- Scout full reports on disk (survive session end): scratchpad
  `C:\Users\YUKEZH~1\AppData\Local\Temp\claude\D--OneDrive---...\707cc7ae-...\scratchpad\`
  files `g2w1_a1_academic.md … g2w1_a16_data.md`, `g2w1_cards.md` (B1), `g2w1_skeptic.md` (B2).
- **RECOVERY RULE**: if the workflow finished, read `journal.jsonl` / the two synthesis files; if
  it died mid-flight, the per-scout scratchpad files still hold the leads — synthesize from those
  (or resume the workflow with `resumeFromRunId: wf_f37e445c-70a`, cached prefix replays free).

## Next automatic actions (in order)

1. Recover Wave-1 scan output (rule above) → write `WORLD_ALPHA_ATLAS.md`,
   `ACTIVE_ALPHA_QUEUE.md`, `STRATEGY_FAMILY_TREE.md`, `SOURCE_GRAPH.md`; commit.
2. Select 3–6 distinct mechanisms (selection reasoning = mechanism/evidence only, BEFORE any
   outcome computation), check each against `FAILURE_MEMORY.md`, preregister specs
   (`runs/G2_*/spec.yaml` committed pre-result), register ledger trials, launch Formal Wave 1.
3. Standing internal lanes (from the directive, not yet started): fresh ORB campaign decision ·
   P1 execution-quality audit lane · LIQREV01 production-readiness dossier (A15 scout may have
   drafted) · registry NQ-hard-code fix.
4. Queue replenishment rule active (README): <10 DISCOVERED or <3 MED/HIGH → new scan wave.

## Unresolved defects / owner items

Planted NT8 injection instrument (Id 699839150754599) — owner deletion recommended, untouched.
Owner actions pending: shadow start (2026-09-01) · Databento execution-falsifier decision (packet
exists, price obtainable $0) · spend gate CLOSED.

## Protected assets (unchanged)

≥2026-08-01 seal · 05-31→07-31 burned · NQ BBO 19 · ~20 ES BBO · 141 Last-only · H1's 2022+ VX
window · H3's 2019+ multi-market window.
