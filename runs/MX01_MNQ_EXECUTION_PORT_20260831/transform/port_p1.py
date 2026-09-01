# -*- coding: utf-8 -*-
"""MX-01: derive WeeklyEdgeP1PCTMnq_v1 from the certified WeeklyEdgeP1PCT_v3.

THE GOVERNING CONSTRAINT, and the reason this is a script and not hand-editing:
the certified SIGNAL computation must be provably byte-identical. Every edit below is
asserted to match EXACTLY ONCE. If the certified file ever changes under us, an assert
fires instead of a silent mis-patch.

ARCHITECTURE
    primary series 0 = NQ  -> every signal, every clock, every threshold. UNTOUCHED.
    added  series 1 = MNQ  -> order routing ONLY. Never read for a decision.
    the ledger (myQty / pendingSize / sessPnl) stays in NQ CONTRACT UNITS, so
      * the session box (HaltDollars/TargetDollars, per-contract, NQ PointValue) is untouched
      * the per-bar export stays byte-identical and parity stays checkable
    MnqPerNq multiplies at exactly three kinds of site: the order calls and the two
    reconciliation comparisons. Nowhere else.
"""
import hashlib
import io
import os
import sys

SRC = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\research\weekly_edge\ninjascript\WeeklyEdgeP1PCT_v3.cs"
OUT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\research\weekly_edge\ninjascript\WeeklyEdgeP1PCTMnq_v1.cs"

CERTIFIED_SHA = "a9ccc2331d78aea43b1eefeff24189d0277a4cdfb718f2b817f56f7ef60f6be6"

with io.open(SRC, "r", encoding="utf-8-sig", newline="") as f:
    src = f.read()

# The certified file is CRLF.  Normalise to \n for editing so the patterns below can be written
# readably, then restore the original ending on write.  NEVER edit against mixed endings: the
# first attempt at this silently matched 0 times on every multi-line pattern.
EOL = "\r\n" if "\r\n" in src else "\n"
src = src.replace("\r\n", "\n")
print("line ending: %s" % ("CRLF" if EOL == "\r\n" else "LF"))

raw = open(SRC, "rb").read()
got = hashlib.sha256(raw).hexdigest()
print("source sha256 = %s" % got)
print("expected      = %s  %s" % (CERTIFIED_SHA, "MATCH" if got == CERTIFIED_SHA else "*** DIFFERENT ***"))

EDITS = []


def edit(tag, old, new):
    EDITS.append((tag, old, new))


# ------------------------------------------------------------------ 1. identity
edit("MX-ID-1",
     "public class WeeklyEdgeP1PCT_v3 : Strategy",
     "public class WeeklyEdgeP1PCTMnq_v1 : Strategy")

edit("MX-ID-2",
     '                Name = "WeeklyEdgeP1PCT_v3";',
     '                Name = "WeeklyEdgeP1PCTMnq_v1";')

# ------------------------------------------------------------------ 2. new inputs
edit("MX-PROP",
     '        [NinjaScriptProperty] public string ExpectInstrument { get; set; }   // HD-05, "" = check disabled',
     '        [NinjaScriptProperty] public string ExpectInstrument { get; set; }   // HD-05, "" = check disabled\n'
     '\n'
     '        // ---- [MX-01] MNQ EXECUTION PORT.  The ONLY additions to the input surface.\n'
     '        [NinjaScriptProperty] public string MnqInstrument   { get; set; }   // MX, "MNQ 09-26"\n'
     '        [NinjaScriptProperty] public int    MnqPerNq        { get; set; }   // MX, 3 = 3/10 of one NQ\n'
     '        [NinjaScriptProperty] public string ExpectMnq       { get; set; }   // MX, "" = check disabled')

# ------------------------------------------------------------------ 3. series constants + gate state
edit("MX-FIELD",
     "        // ---- [HD-06] roll awareness",
     "        // ---- [MX-01] series indices.  SIG carries EVERY decision; EXEC carries every order.\n"
     "        //      Nothing reads EXEC for a decision - that is the whole invariant of this port.\n"
     "        private const int SIG = 0, EXEC = 1;\n"
     "        private bool mxExecBlocked   = false;   // MNQ series not tradeable -> block ENTRIES only\n"
     "        private string mxExecReason  = \"\";\n"
     "        private int  mxExecLoggedFor = -1;\n"
     "\n"
     "        // ---- [HD-06] roll awareness")

# ------------------------------------------------------------------ 4. defaults
edit("MX-DEFAULT",
     "                RollLeadDays = 8; WarmupCertDir = \"\"; DiagDir = \"\";\n"
     "                ExportStampUtc = false; TraceOrdersLive = false; ExpectInstrument = \"\";",
     "                RollLeadDays = 8; WarmupCertDir = \"\"; DiagDir = \"\";\n"
     "                ExportStampUtc = false; TraceOrdersLive = false; ExpectInstrument = \"\";\n"
     "                // [MX-01] execution port defaults.\n"
     "                MnqInstrument = \"MNQ 09-26\"; MnqPerNq = 3; ExpectMnq = \"\";")

# ------------------------------------------------------------------ 5. add the execution series
edit("MX-CONFIGURE",
     "            else if (State == State.Configure)\n"
     "            {\n"
     "                TraceOrders = TraceOrdersLive;\n"
     "            }",
     "            else if (State == State.Configure)\n"
     "            {\n"
     "                // [MX-01] THE EXECUTION SERIES.  Index 1 by construction - it is the only\n"
     "                //         AddDataSeries call in this file.  Read for orders, never for a decision.\n"
     "                AddDataSeries(MnqInstrument, BarsPeriodType.Minute, 1);\n"
     "                TraceOrders = TraceOrdersLive;\n"
     "            }")

# ------------------------------------------------------------------ 6. BarsInProgress guard
# OnBarUpdate's first certified statement, located by its own comment block.
edit("MX-BIP",
     "            DateTime pyTs = Time[0];\n"
     "            bool firstBar = Bars.IsFirstBarOfSession;\n"
     "            bool lastBar  = Bars.IsLastBarOfSession;",
     "            // [MX-01] EVERY line below this point runs on the NQ series ONLY, exactly as the\n"
     "            //         certified single-series object did.  The MNQ series drives no logic and\n"
     "            //         must not advance the accumulators - a second OnBarUpdate call per minute\n"
     "            //         would double-feed sigma, ATR, VWAP and the quality quantiles.\n"
     "            //         THIS RETURN IS THE ENTIRE ISOLATION OF THE PORT.\n"
     "            if (BarsInProgress != SIG) return;\n"
     "            MxExecReadiness();\n"
     "\n"
     "            DateTime pyTs = Time[0];\n"
     "            bool firstBar = Bars.IsFirstBarOfSession;\n"
     "            bool lastBar  = Bars.IsLastBarOfSession;")

# ------------------------------------------------------------------ 7. order sites
edit("MX-ORDER-ENTER",
     '                pendingSize = size; EnterLong(size, "L"); pendingAct = ACT_ENTER;',
     '                // [MX-01] size stays in NQ UNITS in the ledger; the multiply happens HERE ONLY.\n'
     '                pendingSize = size; EnterLong(EXEC, size * MnqPerNq, "L"); pendingAct = ACT_ENTER;')

edit("MX-ORDER-XLSESS",
     '                ExitLong(myQty, "XLsess", "L");',
     '                ExitLong(EXEC, myQty * MnqPerNq, "XLsess", "L");')

edit("MX-ORDER-XL",
     '                ExitLong(myQty, "XL", "L"); pendingAct = ACT_EXIT;',
     '                ExitLong(EXEC, myQty * MnqPerNq, "XL", "L"); pendingAct = ACT_EXIT;')

# ------------------------------------------------------------------ 8. reconciliation in MNQ units
edit("MX-RECON",
     "            ObserveSettlement(hdAct0, (hdAct0 == ACT_ENTER) ? hdSize0 : hdQty0, Open[0]);\n"
     "            AssertLedgerMatchesStrategyPosition(myQty);",
     "            // [MX-01] the two witnesses (NT8 strategy position, executions) count MNQ contracts,\n"
     "            //         so the NQ-unit ledger is converted HERE ONLY.  Open[0] is the NQ open: the\n"
     "            //         ledger's assumed fill price is deliberately the DECISION instrument's, which\n"
     "            //         is what the session box was calibrated on.  A real MNQ fill differing from it\n"
     "            //         is logged by ObserveSettlement as FILLPX, never halted.\n"
     "            ObserveSettlement(hdAct0, ((hdAct0 == ACT_ENTER) ? hdSize0 : hdQty0) * MnqPerNq, Open[0]);\n"
     "            AssertLedgerMatchesStrategyPosition(myQty * MnqPerNq);")

edit("MX-POSITION",
     "            int nt8 = (Position.MarketPosition == MarketPosition.Long)  ?  Position.Quantity\n"
     "                    : (Position.MarketPosition == MarketPosition.Short) ? -Position.Quantity : 0;",
     "            // [MX-01] Positions[EXEC], never Position.  On a multi-series strategy Position\n"
     "            //         tracks the series currently in progress, which is always SIG here - i.e.\n"
     "            //         permanently flat, which would make this invariant vacuously true and\n"
     "            //         silently delete the reconciliation.  Index explicitly.\n"
     "            //         MUST be fully qualified: bare `Position` is CS0118 (it is a property\n"
     "            //         on StrategyBase, not a type).  Verified by compile probe, not assumed.\n"
     "            NinjaTrader.Cbi.Position pex = Positions[EXEC];\n"
     "            int nt8 = (pex.MarketPosition == MarketPosition.Long)  ?  pex.Quantity\n"
     "                    : (pex.MarketPosition == MarketPosition.Short) ? -pex.Quantity : 0;")

edit("MX-ACCTPOS",
     "            try { return PositionAccount.Quantity + \"(\" + PositionAccount.MarketPosition + \")\"; }\n"
     "            catch (Exception) { return \"?\"; }",
     "            // [MX-01] the ACCOUNT position on the traded (MNQ) instrument.  LOG ONLY.\n"
     "            try { return PositionsAccount[EXEC].Quantity + \"(\" + PositionsAccount[EXEC].MarketPosition + \")\"; }\n"
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

# ------------------------------------------------------------------ 10. the MX block
edit("MX-BLOCK",
     "        // ==== [HD] END OF HARDENING REGION =======================================================",
     r'''        // =========================================================================================
        // [MX-01] EXECUTION-SERIES READINESS.  The MNQ series is the ONLY thing this port adds to
        // the risk surface, so it gets its own gate rather than being folded into an existing one.
        //
        // IT GATES ENTRIES ONLY.  Exits are never gated - the same rule the hardening region obeys.
        // If MNQ dies while we are positioned, blocking the exit would strand a live position; the
        // exit is submitted, and if it cannot be routed NT8 reports it and the reconciliation halts.
        //
        // It is NOT folded into the certified early-return, because a return would skip the
        // accumulator writes and silently change the decision object.  TRAP 1, restated: gate the
        // ORDER SITE, never the predicate.
        // =========================================================================================
        private void MxExecReadiness()
        {
            if (State != State.Realtime) { mxExecBlocked = false; return; }   // M1

            string why = null;
            try
            {
                if (BarsArray == null || BarsArray.Length <= EXEC || BarsArray[EXEC] == null)
                    why = "NO-SERIES";
                else if (CurrentBars == null || CurrentBars.Length <= EXEC || CurrentBars[EXEC] < 1)
                    why = "NO-BAR";
                else if (MnqPerNq < 1)
                    why = "MnqPerNq=" + MnqPerNq;
                else
                {
                    double age = (Times[SIG][0] - Times[EXEC][0]).TotalMinutes;
                    if (age < -0.5 || age > 3.0)
                        why = "STALE ageMin=" + age.ToString("F2", CultureInfo.InvariantCulture);
                }
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

        // [MX-01] identity guard for the EXECUTION series, by symmetry with HD-05 on the primary.
        // A silently wrong execution contract is the single worst failure this port can have: every
        // decision would be right and every fill would be on the wrong instrument.
        private void MxInstrumentGuard()
        {
            if (string.IsNullOrEmpty(ExpectMnq)) return;                 // default = disabled
            string wRoot; int wMm, wYy;
            if (!TryParseWanted(ExpectMnq, out wRoot, out wMm, out wYy))
            { Halt("MX01 unparseable ExpectMnq='" + ExpectMnq + "'"); return; }
            if (BarsArray == null || BarsArray.Length <= EXEC || BarsArray[EXEC] == null
                || BarsArray[EXEC].Instrument == null
                || BarsArray[EXEC].Instrument.MasterInstrument == null)
            { Halt("MX01 execution series unresolved"); return; }

            // Fully qualified: bare `Instrument` is CS0118 here (property on NinjaScriptBase).
            NinjaTrader.Cbi.Instrument ex = BarsArray[EXEC].Instrument;
            if (!string.Equals(ex.MasterInstrument.Name, wRoot, StringComparison.OrdinalIgnoreCase))
            { Halt("MX01 ROOT mismatch got=" + ex.MasterInstrument.Name + " want=" + wRoot); return; }
            DateTime xd = ex.Expiry;
            if (xd.Month != wMm || (xd.Year % 100) != wYy)
            { Halt("MX01 MONTH mismatch instrument=" + ex.FullName
                 + " expiry=" + xd.ToString("yyyy-MM-dd") + " want=" + ExpectMnq); return; }

            // CROSS-SERIES: the execution contract must be the SAME month as the decision contract.
            // Trading MNQ 12-26 off NQ 09-26 signals is a partial roll and is not this object.
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

edit("MX-CALLGUARD",
     "                HdConfigAssert();        // [HD-11] M4\n"
     "                HdInstrumentGuard();     // [HD-05] M4, opt-in (ExpectInstrument defaults to \"\")",
     "                HdConfigAssert();        // [HD-11] M4\n"
     "                HdInstrumentGuard();     // [HD-05] M4, opt-in (ExpectInstrument defaults to \"\")\n"
     "                MxInstrumentGuard();     // [MX-01] M4, opt-in (ExpectMnq defaults to \"\")")

# ------------------------------------------------------------------ 11. env rows
edit("MX-ENV",
     '                r.Add("env,config_fault," + (configFault == null ? "none" : configFault));',
     '                r.Add("env,config_fault," + (configFault == null ? "none" : configFault));\n'
     '                r.Add("env,mnq_per_nq," + MnqPerNq);\n'
     '                r.Add("env,exec_instrument," + ((BarsArray != null && BarsArray.Length > EXEC\n'
     '                        && BarsArray[EXEC] != null && BarsArray[EXEC].Instrument != null)\n'
     '                        ? BarsArray[EXEC].Instrument.FullName : "?"));\n'
     '                r.Add("env,exec_bars," + ((BarsArray != null && BarsArray.Length > EXEC\n'
     '                        && BarsArray[EXEC] != null) ? BarsArray[EXEC].Count : -1));')

# ------------------------------------------------------------------ 12. header
edit("MX-HEADER",
     "// =====================================================================================\n"
     "// WeeklyEdgeP1PCT_v3  -  HARDENED SHADOW of the PARITY-CERTIFIED WeeklyEdgeP1PCT_v1.",
     r'''// =====================================================================================
// WeeklyEdgeP1PCTMnq_v1  -  MNQ EXECUTION PORT of WeeklyEdgeP1PCT_v3.
//
// RUN runs/MX01_MNQ_EXECUTION_PORT_20260831/.  Owner instruction 2026-08-31: run the book on
// the live account at 3/10 size using MNQ, because the live account holds ~USD 10.2k.
//
// WHAT THIS IS: the certified decision object, executing on a different contract.
// WHAT THIS IS NOT: a new strategy, a re-parameterisation, or a re-tuning.  ZERO decision
// parameters changed.  HaltDollars=1300, TargetDollars=1000, CommissionRT=4.36 are UNCHANGED,
// and that is not an oversight - see THE SESSION-BOX INVARIANT below.
//
// THE ARCHITECTURE, and why it is this way rather than "just attach it to MNQ":
//   series 0 (SIG)  = NQ  1-minute.  EVERY signal, clock, threshold, quantile and accumulator.
//   series 1 (EXEC) = MNQ 1-minute.  Orders ONLY.  Never read by a decision.
//   Attaching the certified object directly to MNQ would recompute the ENTIRE decision stack on
//   a different tape.  MNQ's cumulative delta and volume normalisation are NOT NQ's, and both
//   feed the vote: dL = (lagCumDelta >= 0) enters `nMemLong * nThr * (1 + dL) >= 16` directly.
//   The decision would drift for a reason that has nothing to do with the edge.  Here it cannot:
//   the MNQ series is write-only from the strategy's point of view.
//
// THE SESSION-BOX INVARIANT - the one piece of arithmetic that makes the port safe:
//   sessPnl accumulates `(px - entry) * PointValue - CommissionRT` PER CONTRACT and is NOT
//   multiplied by quantity (W98 per-contract box, see the two accumulation sites).  PointValue
//   is the PRIMARY's, i.e. NQ's 20.  So the box is a per-NQ-contract dollar threshold:
//   -1300 = -65.0 index points, +1000 = +50.0 index points.  It is INVARIANT to how many MNQ
//   we actually trade, and scaling it would MOVE those point thresholds and change the object.
//   Scaling HaltDollars by 3/10 would put the loss halt at -195 points instead of -65 and the
//   session box would effectively stop firing.  It is deliberately NOT scaled.
//
// THE LEDGER IS IN NQ UNITS.  myQty / pendingSize / the export's `qty` column all count NQ
//   contracts, exactly as certified, so the per-bar export is BYTE-IDENTICAL to the certified
//   object's and decision parity is CHECKABLE rather than asserted.  MnqPerNq multiplies at
//   exactly five sites, all marked [MX-01]: three order calls and two reconciliation compares.
//
// SIZE MAPPING: P1 trades 1 or 2 NQ.  At MnqPerNq=3 that is 3 or 6 MNQ = 0.30 / 0.60 NQ.
//   MnqPerNq is an INPUT, not a constant: 1 / 2 / 3 are all deployable without a rebuild.
//
// STATUS: NOT CERTIFIED.  NOT ENABLED.  Derived mechanically by scratchpad/port_p1.py, whose
// asserts guarantee every edit matched exactly once against the certified source.
// =====================================================================================
// =====================================================================================
// WeeklyEdgeP1PCT_v3  -  HARDENED SHADOW of the PARITY-CERTIFIED WeeklyEdgeP1PCT_v1.''')

# ================================================================== apply
out = src
for tag, old, new in EDITS:
    n = out.count(old)
    if n != 1:
        print("*** FAIL %s: matched %d times (need exactly 1)" % (tag, n))
        print("    pattern head: %r" % old[:120])
        sys.exit(1)
    out = out.replace(old, new, 1)
    print("  ok  %-16s  %+6d chars" % (tag, len(new) - len(old)))

# ---- forbidden-token audit: prove nothing that must not appear, appears.
FORBIDDEN = [
    ("WeeklyEdgeP1PCT_v3 : Strategy", "old class declaration survived"),
    ('Name = "WeeklyEdgeP1PCT_v3"', "old Name survived"),
]
for tok, why in FORBIDDEN:
    if tok in out:
        print("*** FAIL forbidden token present (%s): %r" % (why, tok))
        sys.exit(1)

# ---- the decision-parameter audit: these MUST still be at certified values.
MUST_KEEP = [
    "HaltDollars = 1300.0; TargetDollars = 1000.0; CommissionRT = 4.36;",
    "VolPeriod = 460; SMinTicks = 40; SMaxTicks = 1200; StopMultiplier = 179;",
    "TiltSma = 50; TiltMult = 1.25; TiltRescale = 0.9026;",
    "WSolar = 0.7086; WBmom = 2.83; BmomBandDays = 14;",
    "EntryLevel = 3.0; ExitLevel = 1.0;",
    "EntryBlockMin = 30; ForcedFlatMin = 21;",
    "QualWindow = 250; QualMinHist = 100;",
    "UseQualitySize = true; UseSessionBox = true;",
    'ExportDir = ""; Tag = "p1pct";',
    "bool voteOK = (nMemLong * nThr * (1 + dL)) >= 16;",
    "lastScore = sc; size = (sc >= 3) ? 2 : 1;",
    "sessPnl += (Open[0] - myEntryPx) * Instrument.MasterInstrument.PointValue",
    "sessPnl += (Close[0] - myEntryPx) * Instrument.MasterInstrument.PointValue",
    "if (UseSessionBox && (sessPnl <= -HaltDollars || sessPnl >= TargetDollars))",
    "for (int m = 0; m < NMEMB; m++) mS[m] = StopMultiplier * TickSize;",
]
print("\nDECISION-PARAMETER AUDIT (each must survive byte-identical):")
bad = 0
for m in MUST_KEEP:
    ok = m in out
    if not ok:
        bad += 1
    print("  %s  %s" % ("ok " if ok else "***", m[:88]))
if bad:
    print("*** %d certified constructs missing" % bad)
    sys.exit(1)

with io.open(OUT, "w", encoding="utf-8", newline="") as f:
    f.write(out.replace("\n", EOL))

print("\nwrote %s" % OUT)
print("  bytes %d -> %d   (+%d)" % (len(raw), os.path.getsize(OUT), os.path.getsize(OUT) - len(raw)))
print("  sha256 %s" % hashlib.sha256(open(OUT, "rb").read()).hexdigest())
