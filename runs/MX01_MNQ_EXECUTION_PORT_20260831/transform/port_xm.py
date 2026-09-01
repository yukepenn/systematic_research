# -*- coding: utf-8 -*-
"""MX-01: derive WeeklyEdgeXMConflictMnq_v1 from the certified WeeklyEdgeXMConflict_v4.

Same discipline as port_p1.py: every edit asserted to match EXACTLY ONCE.

XM is the easier of the two legs and the reason is worth recording: it has NO
dollar-denominated decision parameter at all. realizedPnl is accounting-only, CommissionRT is
decision-inert, and DisasterStopPoints is in POINTS and defaults OFF. The decision is
sign(NQ drive) vs sign(z-scored ES/RTY/YM composite), plus clocks and staleness. So Qty is a
pure multiplier on an unchanged decision, and the port is: add MNQ as series 4, route orders
there, multiply by MnqPerNq.

SERIES MAP
    0 NQ   primary, the DECISION instrument (const NQ = 0 is unchanged)
    1 ES   signal
    2 RTY  signal
    3 YM   signal
    4 MNQ  EXECUTION ONLY - never a signal, never in the staleness/sigma/anchor loops
"""
import hashlib
import io
import os
import sys

SRC = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\research\weekly_edge\ninjascript\WeeklyEdgeXMConflict_v4.cs"
OUT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\research\weekly_edge\ninjascript\WeeklyEdgeXMConflictMnq_v1.cs"

CERTIFIED_SHA = "0360f894724cfd1fe59eb2a3a14d434b6e8a082eb2f25ba483e97ff2b854bae8"

with io.open(SRC, "r", encoding="utf-8-sig", newline="") as f:
    src = f.read()
EOL = "\r\n" if "\r\n" in src else "\n"
src = src.replace("\r\n", "\n")

raw = open(SRC, "rb").read()
got = hashlib.sha256(raw).hexdigest()
print("line ending: %s" % ("CRLF" if EOL == "\r\n" else "LF"))
print("source sha256 = %s" % got)
print("expected      = %s  %s" % (CERTIFIED_SHA, "MATCH" if got == CERTIFIED_SHA else "*** DIFFERENT ***"))

EDITS = []


def edit(tag, old, new):
    EDITS.append((tag, old, new))


# ------------------------------------------------------------------ 1. identity
edit("MX-ID-1",
     "public class WeeklyEdgeXMConflict_v4 : Strategy",
     "public class WeeklyEdgeXMConflictMnq_v1 : Strategy")

edit("MX-ID-2",
     '                Name                      = "WeeklyEdgeXMConflict_v4";',
     '                Name                      = "WeeklyEdgeXMConflictMnq_v1";')

# ------------------------------------------------------------------ 2. new inputs
edit("MX-PROP",
     "        [NinjaScriptProperty] public bool   EmergencyFlattenOnDeadSeries { get; set; }   // HD-12, true",
     "        [NinjaScriptProperty] public bool   EmergencyFlattenOnDeadSeries { get; set; }   // HD-12, true\n"
     "\n"
     "        // ---- [MX-01] MNQ EXECUTION PORT.  The ONLY additions to the input surface.\n"
     "        [NinjaScriptProperty] public string MnqInstrument                { get; set; }   // MX, \"MNQ 09-26\"\n"
     "        [NinjaScriptProperty] public int    MnqPerNq                     { get; set; }   // MX, 3\n"
     "        [NinjaScriptProperty] public string ExpectMnq                    { get; set; }   // MX, \"\" = off")

# ------------------------------------------------------------------ 3. series index
edit("MX-CONST",
     "        // ---- series indices, fixed by the order of the AddDataSeries calls\n"
     "        private const int NQ = 0, ES = 1, RTY = 2, YM = 3;",
     "        // ---- series indices, fixed by the order of the AddDataSeries calls\n"
     "        // [MX-01] MNQ is appended LAST so every existing index and every 'i < 4' signal loop\n"
     "        //         keeps its certified meaning.  MNQ is an EXECUTION series: it never enters\n"
     "        //         the anchor, the sigma history, the composite, or the staleness test.\n"
     "        private const int NQ = 0, ES = 1, RTY = 2, YM = 3, MNQ = 4;\n"
     "        private bool   mxExecBlocked   = false;\n"
     "        private string mxExecReason    = \"\";\n"
     "        private int    mxExecLoggedFor = -1;")

# ------------------------------------------------------------------ 4. defaults
edit("MX-DEFAULT",
     "                EmergencyFlattenOnDeadSeries = true;   // inert: M1-gated",
     "                EmergencyFlattenOnDeadSeries = true;   // inert: M1-gated\n"
     "                // [MX-01] execution port defaults.\n"
     "                MnqInstrument = \"MNQ 09-26\"; MnqPerNq = 3; ExpectMnq = \"\";")

# ------------------------------------------------------------------ 5. the execution series
edit("MX-CONFIGURE",
     "                AddDataSeries(YmInstrument,  BarsPeriodType.Minute, 1);\n"
     "                TraceOrders = TraceOrdersLive;   // [HD-09] property defaults FALSE",
     "                AddDataSeries(YmInstrument,  BarsPeriodType.Minute, 1);\n"
     "                // [MX-01] THE EXECUTION SERIES, index 4.  Appended after the three signal\n"
     "                //         series so indices 1/2/3 keep the meaning the FIXED ORDER comment\n"
     "                //         above depends on.  Orders only; no decision reads it.\n"
     "                AddDataSeries(MnqInstrument, BarsPeriodType.Minute, 1);\n"
     "                TraceOrders = TraceOrdersLive;   // [HD-09] property defaults FALSE")

# ------------------------------------------------------------------ 6. readiness hook
edit("MX-HOOK",
     "            HdRealtimeBarHook();      // [HD-06/07/13] M1",
     "            HdRealtimeBarHook();      // [HD-06/07/13] M1\n"
     "            MxExecReadiness();        // [MX-01] gates ENTRIES only")

# ------------------------------------------------------------------ 7. order sites (4)
edit("MX-ORDER-ENTER",
     '                        if (lastDesired > 0) EnterLong(Qty, "XM_L"); else EnterShort(Qty, "XM_S");',
     '                        // [MX-01] Qty stays in NQ UNITS everywhere; the multiply is HERE ONLY.\n'
     '                        if (lastDesired > 0) EnterLong(MNQ, Qty * MnqPerNq, "XM_L");\n'
     '                        else                 EnterShort(MNQ, Qty * MnqPerNq, "XM_S");')

edit("MX-ORDER-DIS",
     '                    if (myPos > 0) ExitLong(Qty, "XM_DIS", "XM_L"); else ExitShort(Qty, "XM_DIS", "XM_S");',
     '                    if (myPos > 0) ExitLong(MNQ, Qty * MnqPerNq, "XM_DIS", "XM_L");\n'
     '                    else           ExitShort(MNQ, Qty * MnqPerNq, "XM_DIS", "XM_S");')

# the ALPHA exit (section 5) - disambiguated by its surrounding pendingAct line
edit("MX-ORDER-EXIT",
     '                if (myPos > 0) ExitLong(Qty, "XM_X", "XM_L"); else ExitShort(Qty, "XM_X", "XM_S");\n'
     '                pendingAct = ACT_EXIT;',
     '                if (myPos > 0) ExitLong(MNQ, Qty * MnqPerNq, "XM_X", "XM_L");\n'
     '                else           ExitShort(MNQ, Qty * MnqPerNq, "XM_X", "XM_S");\n'
     '                pendingAct = ACT_EXIT;')

# the DEAD-SERIES emergency flatten (HD-12)
edit("MX-ORDER-DEAD",
     '                if (myPos > 0) ExitLong(Qty, "XM_X", "XM_L"); else ExitShort(Qty, "XM_X", "XM_S");\n'
     '                Halt("DEAD-SERIES flatten submitted; ledger deliberately NOT adjusted");',
     '                if (myPos > 0) ExitLong(MNQ, Qty * MnqPerNq, "XM_X", "XM_L");\n'
     '                else           ExitShort(MNQ, Qty * MnqPerNq, "XM_X", "XM_S");\n'
     '                Halt("DEAD-SERIES flatten submitted; ledger deliberately NOT adjusted");')

# ------------------------------------------------------------------ 8. reconciliation
edit("MX-RECON",
     "            ObserveSettlement(hdAct0, (hdAct0 == ACT_ENTER) ? Qty : hdQty0, Opens[NQ][0]);\n"
     "            AssertLedgerMatchesStrategyPosition(myPos * Qty);",
     "            // [MX-01] both witnesses count MNQ contracts, so the NQ-unit ledger converts HERE.\n"
     "            //         Opens[NQ][0] stays the assumed fill price: it is the DECISION\n"
     "            //         instrument's open, which is what realizedPnl was certified against.\n"
     "            //         A real MNQ fill differing from it is logged FILLPX, never halted.\n"
     "            ObserveSettlement(hdAct0, ((hdAct0 == ACT_ENTER) ? Qty : hdQty0) * MnqPerNq, Opens[NQ][0]);\n"
     "            AssertLedgerMatchesStrategyPosition(myPos * Qty * MnqPerNq);")

edit("MX-POSITION",
     "            int nt8 = (Position.MarketPosition == MarketPosition.Long)  ?  Position.Quantity\n"
     "                    : (Position.MarketPosition == MarketPosition.Short) ? -Position.Quantity : 0;",
     "            // [MX-01] Positions[MNQ], never Position.  On a multi-series strategy Position\n"
     "            //         tracks the series in progress - always NQ here, i.e. permanently flat -\n"
     "            //         which would make this invariant vacuously true and silently delete the\n"
     "            //         reconciliation.  Index explicitly.  Fully qualified: bare `Position` is\n"
     "            //         CS0118 (a property on StrategyBase, not a type).  Verified by compile.\n"
     "            NinjaTrader.Cbi.Position pex = Positions[MNQ];\n"
     "            int nt8 = (pex.MarketPosition == MarketPosition.Long)  ?  pex.Quantity\n"
     "                    : (pex.MarketPosition == MarketPosition.Short) ? -pex.Quantity : 0;")

edit("MX-ACCTPOS",
     "            try { return PositionAccount.Quantity + \"(\" + PositionAccount.MarketPosition + \")\"; }\n"
     "            catch (Exception) { return \"?\"; }",
     "            // [MX-01] the ACCOUNT position on the traded (MNQ) instrument.  LOG ONLY.\n"
     "            try { return PositionsAccount[MNQ].Quantity + \"(\" + PositionsAccount[MNQ].MarketPosition + \")\"; }\n"
     "            catch (Exception) { return \"?\"; }")

# ------------------------------------------------------------------ 9. entry gate
edit("MX-GATE",
     "            if (entriesBlockedUntilAgree)return false;\n"
     "            if (RollBlocked())           return false;\n"
     "            return true;",
     "            if (entriesBlockedUntilAgree)return false;\n"
     "            if (RollBlocked())           return false;\n"
     "            if (mxExecBlocked)           return false;   // [MX-01] MNQ not tradeable\n"
     "            return true;")

edit("MX-BLOCKLOG",
     '            string s = "ENTRY-BLOCKED halt=" + haltEntries + "(" + haltReason + ") warmup=" + warmupBlocked\n'
     '                     + " carry=" + entriesBlockedUntilAgree + " roll=" + RollBlocked();',
     '            string s = "ENTRY-BLOCKED halt=" + haltEntries + "(" + haltReason + ") warmup=" + warmupBlocked\n'
     '                     + " carry=" + entriesBlockedUntilAgree + " roll=" + RollBlocked()\n'
     '                     + " exec=" + mxExecBlocked + "(" + mxExecReason + ")";')

# ------------------------------------------------------------------ 10. guards extended to MNQ
edit("MX-HD05",
     '            string[] want = { null, EsInstrument, RtyInstrument, YmInstrument };\n'
     '            string[] nm   = { "NQ", "ES", "RTY", "YM" };\n'
     '            string report = "HD05";\n'
     '            try\n'
     '            {\n'
     '                if (BarsArray == null || BarsArray.Length < 4 || Instrument == null',
     '            // [MX-01] the EXECUTION series is added to the HARDENED guard, not the certified\n'
     '            //         one above it.  Clause (c) - every secondary on the primary\'s contract\n'
     '            //         month - now also catches "decision on NQ 09-26, fills on MNQ 12-26",\n'
     '            //         which is the single worst silent failure this port could have.\n'
     '            string[] want = { null, EsInstrument, RtyInstrument, YmInstrument, MnqInstrument };\n'
     '            string[] nm   = { "NQ", "ES", "RTY", "YM", "MNQ" };\n'
     '            string report = "HD05";\n'
     '            try\n'
     '            {\n'
     '                if (BarsArray == null || BarsArray.Length < 5 || Instrument == null')

edit("MX-HD05-LOOP",
     "                for (int i = 1; i < 4; i++)\n"
     "                {\n"
     "                    if (BarsArray[i] == null || BarsArray[i].Instrument == null\n"
     "                        || BarsArray[i].Instrument.MasterInstrument == null)\n"
     "                    { instrumentMismatch = true; report += \" \" + nm[i] + \"=UNRESOLVED\"; break; }",
     "                for (int i = 1; i < 5; i++)\n"
     "                {\n"
     "                    if (BarsArray[i] == null || BarsArray[i].Instrument == null\n"
     "                        || BarsArray[i].Instrument.MasterInstrument == null)\n"
     "                    { instrumentMismatch = true; report += \" \" + nm[i] + \"=UNRESOLVED\"; break; }")

edit("MX-DEADSERIES",
     "            bool secReady = true;\n"
     "            string cb = \"\";\n"
     "            for (int i = 0; i < 4; i++)",
     "            bool secReady = true;\n"
     "            string cb = \"\";\n"
     "            // [MX-01] i < 5: a dead EXECUTION series is at least as serious as a dead signal\n"
     "            //         series - it means the exit path cannot be routed.  Detect it loudly.\n"
     "            for (int i = 0; i < 5; i++)")

edit("MX-ENVROWS",
     '            List<string> r = new List<string>();\n'
     '            string[] nm = { "NQ", "ES", "RTY", "YM" };\n'
     '            try\n'
     '            {\n'
     '                for (int i = 0; i < 4; i++)',
     '            List<string> r = new List<string>();\n'
     '            string[] nm = { "NQ", "ES", "RTY", "YM", "MNQ" };\n'
     '            try\n'
     '            {\n'
     '                for (int i = 0; i < 5; i++)')

edit("MX-ENV2",
     '                r.Add("env,config_fault," + (configFault == null ? "none" : configFault));',
     '                r.Add("env,config_fault," + (configFault == null ? "none" : configFault));\n'
     '                r.Add("env,mnq_per_nq," + MnqPerNq);\n'
     '                r.Add("env,qty_nq_units," + Qty);')

edit("MX-CALLGUARD",
     "                HdInstrumentGuard();     // [HD-05] the certified guard above is UNTOUCHED; this one\n"
     "                                         //         adds the contract-month and cross-series clauses.",
     "                HdInstrumentGuard();     // [HD-05] the certified guard above is UNTOUCHED; this one\n"
     "                                         //         adds the contract-month and cross-series clauses,\n"
     "                                         //         and [MX-01] the execution series.\n"
     "                MxInstrumentGuard();     // [MX-01] M4, opt-in (ExpectMnq defaults to \"\")")

# ------------------------------------------------------------------ 11. the MX block
edit("MX-BLOCK",
     "        // ==== [HD] END OF HARDENING REGION =======================================================",
     r'''        // =========================================================================================
        // [MX-01] EXECUTION-SERIES READINESS.  Gates ENTRIES only; exits are never gated.
        // Deliberately NOT folded into the certified early return at the top of OnBarUpdate: a
        // return there would skip the sigma-history append (hist[i].Add) and silently change the
        // decision object on every subsequent session.  TRAP 1, restated: gate the ORDER SITE.
        // =========================================================================================
        private void MxExecReadiness()
        {
            if (State != State.Realtime) { mxExecBlocked = false; return; }   // M1

            string why = null;
            try
            {
                if (BarsArray == null || BarsArray.Length <= MNQ || BarsArray[MNQ] == null)
                    why = "NO-SERIES";
                else if (CurrentBars == null || CurrentBars.Length <= MNQ || CurrentBars[MNQ] < 1)
                    why = "NO-BAR";
                else if (MnqPerNq < 1)
                    why = "MnqPerNq=" + MnqPerNq;
                else if (!SeriesFresh(MNQ, Times[NQ][0]))
                    why = "STALE ageMin="
                        + (Times[NQ][0] - Times[MNQ][0]).TotalMinutes.ToString("F2", CultureInfo.InvariantCulture);
            }
            catch (Exception e) { why = "EXCEPTION " + e.Message; }

            bool was = mxExecBlocked;
            mxExecBlocked = (why != null);
            mxExecReason  = (why == null) ? "" : why;

            if (mxExecBlocked && mxExecLoggedFor != CurrentBar)
            {
                mxExecLoggedFor = CurrentBar;
                LogErr("MX-EXEC-BLOCKED " + mxExecReason + "; entries refused, EXITS NOT GATED");
                HdDiagRow("MXEXEC", "blocked=1;why=" + mxExecReason);
            }
            else if (was && !mxExecBlocked)
            {
                LogInfo("MX-EXEC-CLEARED");
                HdDiagRow("MXEXEC", "blocked=0");
            }
        }

        // [MX-01] identity guard for the EXECUTION series.  A silently wrong execution contract is
        // the worst failure available to this port: every decision right, every fill on the wrong
        // instrument.  Halts rather than merely flagging.
        private void MxInstrumentGuard()
        {
            if (string.IsNullOrEmpty(ExpectMnq)) return;                 // default = disabled
            string wRoot; int wMm, wYy;
            if (!TryParseWanted(ExpectMnq, out wRoot, out wMm, out wYy))
            { Halt("MX01 unparseable ExpectMnq='" + ExpectMnq + "'"); return; }
            if (BarsArray == null || BarsArray.Length <= MNQ || BarsArray[MNQ] == null
                || BarsArray[MNQ].Instrument == null
                || BarsArray[MNQ].Instrument.MasterInstrument == null)
            { Halt("MX01 execution series unresolved"); return; }

            // Fully qualified: bare `Instrument` is CS0118 here (property on NinjaScriptBase).
            NinjaTrader.Cbi.Instrument ex = BarsArray[MNQ].Instrument;
            if (!string.Equals(ex.MasterInstrument.Name, wRoot, StringComparison.OrdinalIgnoreCase))
            { Halt("MX01 ROOT mismatch got=" + ex.MasterInstrument.Name + " want=" + wRoot); return; }
            DateTime xd = ex.Expiry;
            if (xd.Month != wMm || (xd.Year % 100) != wYy)
            { Halt("MX01 MONTH mismatch instrument=" + ex.FullName
                 + " expiry=" + xd.ToString("yyyy-MM-dd") + " want=" + ExpectMnq); return; }
            if (Instrument != null && (Instrument.Expiry.Month != xd.Month
                                    || Instrument.Expiry.Year  != xd.Year))
            { Halt("MX01 CROSS-SERIES exec=" + xd.ToString("yyyy-MM-dd")
                 + " primary=" + Instrument.Expiry.ToString("yyyy-MM-dd")); return; }

            LogInfo("MX01 exec OK instrument=" + ex.FullName + " expiry=" + xd.ToString("yyyy-MM-dd")
                  + " want=" + ExpectMnq + " mnqPerNq=" + MnqPerNq
                  + " pointValue=" + ex.MasterInstrument.PointValue
                  + " tickSize=" + ex.MasterInstrument.TickSize);
        }

        // ==== [HD] END OF HARDENING REGION =======================================================''')

# ------------------------------------------------------------------ 12. header
edit("MX-HEADER",
     "// =====================================================================================\n"
     "// WeeklyEdgeXMConflict_v4  -  HARDENED SHADOW of the PARITY-CERTIFIED WeeklyEdgeXMConflict_v2.",
     r'''// =====================================================================================
// WeeklyEdgeXMConflictMnq_v1  -  MNQ EXECUTION PORT of WeeklyEdgeXMConflict_v4.
//
// RUN runs/MX01_MNQ_EXECUTION_PORT_20260831/.  Owner instruction 2026-08-31: run the book on
// the live account at 3/10 size using MNQ.
//
// ZERO decision parameters changed.  XM makes that easy in a way P1 does not, and the reason
// is worth stating because it is the whole safety argument for this leg:
//   XM HAS NO DOLLAR-DENOMINATED DECISION PARAMETER.
//   * realizedPnl (section 0) is ACCOUNTING ONLY - traced through the file, it is read by the
//     export writer and by nothing else.  It never gates an entry or an exit.
//   * CommissionRT feeds realizedPnl and only realizedPnl, so it is DECISION-INERT.
//   * DisasterStopPoints is in INDEX POINTS, not dollars, and defaults to 0 = OFF.
//   The decision is sign(NQ 09:30->09:45 drive) against sign(the z-scored ES/RTY/YM composite),
//   plus the clock and the staleness guard.  None of that has a size or a currency in it.
//   So Qty is a pure multiplier on an unchanged decision.
//
// SERIES MAP
//   0 NQ    primary.  THE DECISION INSTRUMENT.  anchor, drive, sigma, clocks, session iterator.
//   1 ES    signal      2 RTY   signal      3 YM    signal
//   4 MNQ   EXECUTION ONLY.  Never in the anchor loop, the sigma history, the composite, or
//           SeriesFresh's signal test.  A stale MNQ blocks the ENTRY (MxExecReadiness); it does
//           NOT disqualify the session, because session disqualification is a DECISION and MNQ
//           is not allowed to make decisions.  That distinction is the port's core invariant.
//
// MNQ IS APPENDED LAST so that every certified 'i < 4' loop keeps its exact meaning and the
// FIXED ORDER contract on indices 1/2/3 is preserved verbatim.
//
// THE LEDGER IS IN NQ UNITS.  Qty stays 1; myPos stays +/-1; realizedPnl keeps the PRIMARY's
// PointValue, so the per-bar export is BYTE-IDENTICAL to the certified object's and decision
// parity is CHECKABLE rather than asserted.  MnqPerNq multiplies at exactly six sites, all
// marked [MX-01]: four order calls and two reconciliation compares.
//
// SIZE MAPPING: XM trades 1 NQ either way.  At MnqPerNq=3 that is 3 MNQ = 0.30 NQ.
//   MnqPerNq is an INPUT: 1 / 2 / 3 are all deployable without a rebuild.
//
// STATUS: NOT CERTIFIED.  NOT ENABLED.  Derived mechanically by scratchpad/port_xm.py, whose
// asserts guarantee every edit matched exactly once against the certified source.
// =====================================================================================
// =====================================================================================
// WeeklyEdgeXMConflict_v4  -  HARDENED SHADOW of the PARITY-CERTIFIED WeeklyEdgeXMConflict_v2.''')

# ================================================================== apply
out = src
for tag, old, new in EDITS:
    n = out.count(old)
    if n != 1:
        print("*** FAIL %s: matched %d times (need exactly 1)" % (tag, n))
        print("    pattern head: %r" % old[:140])
        sys.exit(1)
    out = out.replace(old, new, 1)
    print("  ok  %-16s  %+6d chars" % (tag, len(new) - len(old)))

FORBIDDEN = [
    ("WeeklyEdgeXMConflict_v4 : Strategy", "old class declaration survived"),
    ('Name                      = "WeeklyEdgeXMConflict_v4"', "old Name survived"),
    ('EnterLong(Qty, "XM_L")', "un-ported entry call"),
    ('EnterShort(Qty, "XM_S")', "un-ported entry call"),
    ('ExitLong(Qty, ', "un-ported exit call"),
    ('ExitShort(Qty, ', "un-ported exit call"),
]
for tok, why in FORBIDDEN:
    if tok in out:
        print("*** FAIL forbidden token present (%s): %r" % (why, tok))
        sys.exit(1)

MUST_KEEP = [
    "AnchorHm           = 93100;",
    "DecisionHm         = 94500;",
    "ExitHm             = 154500;",
    "SigmaLookback      = 60;",
    "SigmaMinHist       = 20;",
    "MaxStaleMinutes    = 3;",
    "ForcedFlatMin      = 21;",
    "CommissionRT       = 4.36;",
    "DisasterStopPoints = 0.0;",
    "Qty                = 1;",
    'Tag                = "xm2";',
    "double drive = Math.Sign(Closes[NQ][0] - anchorNq);",
    "lastConflict = (xs != 0.0 && drive != 0.0 && xs != drive) ? 1 : 0;",
    "lastDesired = (lastConflict == 1) ? (int)drive : 0;",
    "for (int i = 1; i < 4; i++) if (!SeriesFresh(i, ts)) fresh = false;",
    "for (int i = 1; i < 4; i++) if (CurrentBars[i] < 1) return;",
    "if (BarsInProgress != NQ) return;",
    "* Instrument.MasterInstrument.PointValue * Qty",
    "bool exitBarExists = exitTs < sessionEndTs.AddMinutes(-ForcedFlatMin);",
]
print("\nDECISION-PARAMETER AUDIT (each must survive byte-identical):")
bad = 0
for m in MUST_KEEP:
    ok = m in out
    if not ok:
        bad += 1
    print("  %s  %s" % ("ok " if ok else "***", m[:88]))
# SeriesFresh signal loop must appear TWICE (anchor bar and decision bar) and MNQ must not be in it
n_fresh = out.count("for (int i = 1; i < 4; i++) if (!SeriesFresh(i, ts)) fresh = false;")
print("  %s  SeriesFresh signal loop occurs %d times (expect 2: anchor + decision)"
      % ("ok " if n_fresh == 2 else "***", n_fresh))
if n_fresh != 2:
    bad += 1
if bad:
    print("*** %d certified constructs missing/wrong" % bad)
    sys.exit(1)

with io.open(OUT, "w", encoding="utf-8", newline="") as f:
    f.write(out.replace("\n", EOL))

print("\nwrote %s" % OUT)
print("  bytes %d -> %d   (+%d)" % (len(raw), os.path.getsize(OUT), os.path.getsize(OUT) - len(raw)))
print("  sha256 %s" % hashlib.sha256(open(OUT, "rb").read()).hexdigest())
