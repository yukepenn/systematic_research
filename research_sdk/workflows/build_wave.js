export const meta = {
  name: 'build-wave',
  description: 'Stages 8-10: take a frozen surviving candidate to an executable, parity-certified, live-ready NT8 object',
  whenToUse: 'ONLY after a candidate has cleared standalone economics AND the adversarial kill. Invoke with args {candidate, spec_path, mechanism, python_ref, instrument, session_template, expected_direction}.',
  phases: [
    { title: 'Build', detail: 'independent implementation + NinjaScript in parallel' },
    { title: 'Parity', detail: 'trade-for-trade research <-> NT8' },
    { title: 'Readiness', detail: 'warm-up, rollover, logging, account, fills' },
    { title: 'Adversary', detail: 'NT8 deployment adversary tries to break it' },
  ],
}

// ---- args contract -----------------------------------------------------------------------------
const A = args || {}
const CAND = A.candidate || 'UNNAMED_CANDIDATE'
const SPEC = A.spec_path || '(no spec path supplied)'
const MECH = A.mechanism || '(no mechanism supplied)'
const PYREF = A.python_ref || '(no python reference supplied)'
const INSTR = A.instrument || 'NQ 09-26'
const HOURS = A.session_template || 'CME US Index Futures ETH'
const DIRN = A.expected_direction || '(unstated)'

const REPO = 'D:\\OneDrive - Washington University in St. Louis\\TradingResearch\\systematic_research'
const NT8 = 'C:\\Users\\Yuke Zhang\\Documents\\NinjaTrader 8'

if (!A.candidate) {
  log('⛔ REFUSING TO RUN: no `candidate` in args. This wave is not a research tool - it only ' +
      'promotes an ALREADY-SURVIVING frozen object. Supply {candidate, spec_path, mechanism, python_ref}.')
  return { refused: true, reason: 'no candidate supplied' }
}

const CTX = `
BUILD WAVE — stages 8-10 for candidate **${CAND}**.
Spec: ${SPEC}
Mechanism (frozen, do NOT reinterpret): ${MECH}
Research reference implementation: ${PYREF}
Target instrument: ${INSTR} | session template: ${HOURS} | expected direction: ${DIRN}
Repo ${REPO} | NT8 ${NT8}

⛔ THIS WAVE DOES NOT DO RESEARCH. The mechanism is FROZEN. You may not change a threshold, a
   horizon, a sign, a feature, or a session window. If the object does not survive implementation,
   the correct outcome is a FAILED BUILD REPORT, not a modified object. Re-tuning here is the exact
   post-hoc rescue the project forbids.
⛔ DATABENTO OUT OF SCOPE. ⛔ NO DOM/L2 restart.
⛔ READ-ONLY on the LIVE book (P1PCT_v3 dep_9c51536a7045 / XMConflict_v4 dep_27ff47e7e3b7 on paper
   DEMO8383477). Do NOT stop, disable, modify or redeploy the incumbent. Backtests on the isolated
   Backtest account are fine. A new candidate may be deployed ONLY to paper and ONLY after Stage 9
   passes, and even then LIVE real money stays NO.

HARD-WON PLATFORM RULES — each cost real work to learn, violating one silently breaks the object:
 1. NEW CLASS NAME for every functional iteration (_v2, _v3...). NEVER rename a parity-certified
    class. NT8 keeps compiled types in NinjaTrader.Custom.dll until restart, so a stale type can
    resolve; verify by RESOLVING the class, never by trusting a compile flag.
 2. Put every realtime-only addition behind \`if (State != State.Realtime) return;\` (the "M1" gate).
    State.Transition/Realtime NEVER occur in a Strategy Analyzer backtest - that makes such code
    inert BY CONSTRUCTION and makes parity a guarantee rather than a hope. Ship
    \`Print("HARDENING-STATE-MARK " + State)\` as the falsifier and assert ZERO such lines in backtest.
 3. Strategy Analyzer IGNORES DaysToLoad. Manual/parity backtests must start >= 1 year early and set
    Maximum bars look back = Infinite. Deploys must pass DaysToLoad >= 330 (measured convergence:
    ~9 months for decision state, ~10.5 months for position SIZE, which binds).
 4. READ THE CLOSED-TRADE SUM, never the summary NetProfit - NetProfit also counts a position open at
    the window edge (that discrepancy is exactly $1,741.28 on the P1 reference run).
 5. Costs: the Backtest account must carry a commission template ("NinjaTrader Brokerage Lifetime",
    $4.36/ctrRT). An NT8 net is NOT the research headline - research additionally charges a modelled
    spread, and the MEASURED spread ran ~$20.65/ctrRT vs $14.44 modelled.
 6. On a multi-series strategy read \`instruments[]\` and \`currentBars[0]\` - the scalar
    instrumentName/current_bar report a SECONDARY series and will look like a huge bar regression.
 7. Count strategies with ListAllStrategies. The deployment REGISTRY carries STALE rows
    (DisableStrategy does not clear it) and has reported 3 deployments when 2 strategies existed.
 8. ⚠️ NEVER diagnose a writer from file LENGTH. A directory-reported size of 0 on an open handle is
    a METADATA ARTIFACT - a 46,313,472-byte file reported 0 B for over an hour. READ the file.
 9. GetBars silently returns CACHED data with success:true when a range abuts a cache boundary or
    exceeds a bar cap. The tell is LATENCY: a real fetch ~750-1300 ms, a cache return ~10-15 ms.
10. Never restart while positioned - every stop in this book is SYNTHETIC and dies with the strategy.

Label every claim VERIFIED or INFERRED with file:line, a log line, or a computation you ran.`

const SCH = {
  type: 'object',
  properties: {
    stage: { type: 'string' },
    status: { type: 'string', enum: ['PASS', 'FAIL', 'BLOCKED'] },
    findings: { type: 'array', items: { type: 'object', properties: {
      point: { type: 'string' },
      status: { type: 'string', enum: ['VERIFIED', 'INFERRED', 'UNCERTAIN'] },
      evidence: { type: 'string' } }, required: ['point', 'status', 'evidence'] } },
    artifacts: { type: 'array', items: { type: 'string' } },
    blocking_issue: { type: 'string' },
  }, required: ['stage', 'status', 'findings'],
}

phase('Build')
const built = await parallel([
  () => agent(CTX + `
STAGE 8a — INDEPENDENT RE-IMPLEMENTATION. Write a SECOND implementation of ${CAND} from the FROZEN
SPEC ALONE. ⛔ Do NOT read ${PYREF} while writing it - the entire value is independence, and this
project has repeatedly found real defects (including an int32 overflow that read 2.065 seconds into
the future) ONLY because an independent implementation disagreed. After yours runs, diff the decision
series against the reference and CLASSIFY every disagreement. Zero, or every difference explained.`,
    { label: 'build:independent', phase: 'Build', schema: SCH }),

  () => agent(CTX + `
STAGE 8b — NINJASCRIPT. Write ${CAND} as a NinjaScript strategy into ${NT8}\\bin\\Custom\\Strategies.
Mirror the certified house style: Calculate.OnBarClose; managed orders; EntriesPerDirection=1; an
INTERNAL fill ledger so the engine's state does not depend on when NT8 updates SystemPerformance;
ExportDir per-bar decision ledger; WarmupCertDir certificate with explicit gates; DiagDir event rows;
an ExpectInstrument month guard; and a roll guard.
⚠️ ON THE ROLL GUARD, LEARN FROM THE INCUMBENT'S DEFECT: its guard latches (resolves ONCE) and asks
GetNextRolloverDate at the ROOT level, so it cannot tell that you already rolled - re-enabling inside
the window blocks entries PERMANENTLY while the book looks healthy. Compare against the BOUND series'
OWN expiry instead, and make the guard re-resolvable.
Then compile and VERIFY BY RESOLVING THE CLASS (SearchNinjaScriptSymbols), not by a compile flag.`,
    { label: 'build:ninjascript', phase: 'Build', schema: SCH }),
])

phase('Parity')
const parity = await agent(CTX + `
STAGE 9 — PARITY, research <-> NT8. Run the NT8 class through RunStrategyBacktest on the isolated
Backtest account over the spec's window with ${HOURS}, Standard fill, 0 slippage, the Lifetime
commission template. Compare TRADE-FOR-TRADE against the research reference on at least: entry
timestamp, entry price, quantity, P&L, exit timestamp, exit price, signal name.
Binding verdict bands (CLAUDE.md §6): decision agreement >= 99% AND trade counts within 2% =
VALIDATED; 90-99% = classify EVERY mismatch; < 90% = not the same object, FAIL.
⭐ COMPARE DECISIONS BEFORE DOLLARS, AND NEVER TUNE UNTIL P&L MATCHES - that instruction has caught
real defects here and hiding one would be worse than failing.
Also assert ZERO "HARDENING-STATE-MARK" lines in the backtest output (the M1 falsifier).

=== BUILD ===
` + JSON.stringify(built.filter(Boolean), null, 1),
  { label: 'parity', phase: 'Parity', schema: SCH })

phase('Readiness')
const ready = await agent(CTX + `
STAGE 10 — LIVE READINESS. Do NOT hand-roll the acceptance set: run
\`python ${REPO}\\research_sdk\\live_readiness_check.py --selftest\` then \`--tags <newtag>\` and
report its output verbatim. It encodes R1-R8, and R1 (ROLL-PLAN must be in the FUTURE) is the only
check that catches a permanently-latched book that passes every other test.
Additionally establish and report: minimum DaysToLoad for state convergence for THIS object (do not
assume 365 transfers - it was measured for P1); rollover-safe re-enable dates; session-template
correctness (an RTH template silently deletes trades for any engine that trades outside RTH - it
would delete ~62% of P1's entries); account targeting (⚠️ a second Provider-50 account 2047681 exists
on this box - assert the account explicitly); and expected fills vs the modelled convention.
Produce a DEPLOYMENT PACKET: exact class, parameters, instrument, quantity, account, warm-up, the
verification commands, and a ROLLBACK to the current M_11 in one step.
Assign exactly one label: RESEARCH_ONLY / PAPER_READY / LIVE_READY. LIVE_READY does NOT auto-enable
orders - the owner retains real-money authorization.

=== PARITY ===
` + JSON.stringify(parity, null, 1),
  { label: 'readiness', phase: 'Readiness', schema: SCH })

phase('Adversary')
const adv = await parallel([
  () => agent(CTX + `
YOU ARE THE NT8 DEPLOYMENT ADVERSARY. Assume ${CAND} will break in production. Try to break it.
Attack: duplicate strategy instances; stale compiled types resolving instead of the new one; a
partial roll (all series must move together); wrong account; wrong quantity; restart state; a
disconnected or partial data feed; order rejection; stuck orders; orphan positions; paper/live
mismatch; fill logging; clock/timezone/DST; early closes; holiday sessions; and session-ID semantics
(the 23-hour 18:00->17:00 session is the unit, NEVER the calendar date).
Report anything that would be a LIVE BLOCKER, and say plainly whether you would let this trade.`,
    { label: 'adv:deployment', phase: 'Adversary', schema: SCH }),

  () => agent(CTX + `
YOU ARE THE STATISTICAL ADVERSARY. Assume ${CAND}'s edge is FALSE. Kill it.
Check: look-ahead and timestamp leakage; population/denominator mismatch; session-vs-calendar-date
confusion; open-trade and window-edge artifacts; back-adjustment effects; cost conditional on the
alpha state (if the object earns exactly when liquidity is worst, average cost is optimistic);
multiplicity across everything tried to reach it; concentration (top 1 / top 5 / top 10% / ex-top-1 /
ex-top-5 / leave-one-year-out); whether a RATE-MATCHED RANDOM control matching its trade count does
as well; and whether one year or one tail episode carries the result.
⛔ Weekly returns here are highly concentrated - a plain t-stat is ONE DIAGNOSTIC, not the test. Use
block/stationary bootstrap and tail-aware nulls. Default to killed when uncertain.`,
    { label: 'adv:statistical', phase: 'Adversary', schema: SCH }),
])

const bad = [parity, ready].concat(adv.filter(Boolean)).filter(x => x && x.status !== 'PASS')
log(`build wave for ${CAND}: ${bad.length === 0 ? 'ALL STAGES PASS' : bad.length + ' stage(s) not PASS'}`)

return {
  candidate: CAND,
  build: built.filter(Boolean),
  parity: parity,
  readiness: ready,
  adversaries: adv.filter(Boolean),
  overall: bad.length === 0 ? 'PASS' : 'NOT_READY',
  blocking: bad.map(x => `${x.stage}: ${x.blocking_issue || x.status}`),
}
