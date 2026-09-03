"""build_hd23_challenger.py -- deterministic source patcher for the HD-20..23 challenger.

WHY A PATCHER AND NOT FOUR HAND-WRITTEN FILES
    The four target classes are 1148-1415 lines each and 96% of every one of them is the
    CERTIFIED decision object.  Hand-copying them to apply four fixes would put the certified
    region at risk on every keystroke, and the diff would be unreviewable.  Every edit here is
    an EXACT-STRING anchor that must match EXACTLY ONCE or the build aborts, so the patcher
    cannot silently land a change in the wrong place, and cannot silently miss one.

    The output is verified by `verify_hd23_challenger.py`, which asserts that OUTSIDE the
    patched hunks the two files are byte-identical apart from the class rename.

WHAT IS BEING FIXED  (all four bought with a measured live failure, all four dated)

  [HD-20] WARM-UP SHADOW SEED          -- fixes 1,218 live RECONCILE-BREAK errors, 2026-09-01/02
        `shNetQty` is built ONLY from realtime OnExecutionUpdate, so it is 0 on every (re)start.
        The warm-up carry branch compares `nt8` to `ledgerQty` and RETURNS -- it never looks at
        the third witness.  So any restart while holding a position passes warm-up and then
        halts on the NEXT bar with `execImplied=0`.  MEASURED: XM restarted 2026-09-01 13:22:01
        (its once-per-Realtime ROLL-PLAN line), held short 3, and halted at 13:23:00.  It then
        emitted 1,218 error lines over two days and refused every entry, while
        `ListAllStrategies` still reported it Realtime, enabled and healthy.
        FIX: the shadow's domain BEGINS at the first realtime bar.  Seed it there, and re-seed
        when a carry resolves.  This is not "making the check pass" -- it is stating the
        shadow's domain, which the original code never did.

  [HD-21] SESSION-FLATTEN SHADOW LEAK  -- latent, P1 family only, never yet fired
        `ResetShadow()` is reachable from ONE place: `ObserveSettlement`, which early-returns on
        ACT_NONE.  The session-close flatten submits `XLsess` and sets `pendingAct = ACT_NONE`,
        so its fill increments `shFilled` and is never cleared.  The next entry then settles
        with `shFilled = 2*qty` and halts on a bogus `PARTIAL-FILL 6/3`, blocking entries for
        the life of the instance while exits keep working.  XM does not have this: every XM exit
        site sets ACT_EXIT.  (XM's DEAD-SERIES flatten also skips it, but it Halts on the same
        line, so no further entry is reachable; it is reset here for hygiene, not for safety.)

  [HD-22] EXPORT WRITER: FAIL LOUD, THEN RETRY  -- killed the live P1 ledger, 2026-09-01 00:41
        `catch (Exception) { export = null; }` is SILENT and there is no retry anywhere in the
        class.  Two instances enabled 3 s apart: the first won the file handle, the second
        failed silently, and disabling the FIRST removed the only writer.  The ledger was dead
        for the rest of the day and nothing in NT8, in the strategy state, or in the account
        reported it.  FIX: log at ERROR (the channel `writer_watchdog --halts` greps) and retry
        every bar.  The retry opens with append:true so a second instance can never truncate
        the rows the first one wrote -- which is the exact shape of the original kill.
        The FIRST open keeps append:false and still writes the header, so the parity harness
        sees the identical file it always saw.

  [HD-23] ACCOUNT WITNESS + POSITION BUS  -- the incident of 2026-09-03
        11:05  the strategy bought 6 MNQ                  account +6   ledger +6
        11:16  the owner sold 6 MNQ by hand               account  0   ledger +6   <-- invisible
        15:57  the strategy exited: "sell 6"              account -6   ledger  0   <-- OPENED
        16:48  Tradovate AutoLiq bought 6 to cover        account  0
        All three existing witnesses AGREED the whole time, because all three describe what THIS
        INSTANCE DID, and none describes what the ACCOUNT HOLDS.  "Sell 6" closes a long 6 and
        opens a short 6 with the same bytes; only the account distinguishes them.

        !! WHAT THIS GUARD CANNOT SEE, stated next to what it can (CLAUDE.md section 4) !!
        The account position is a SUM: this leg + the other leg + anything a human does by hand.
        From the account ALONE it is PROVABLY IMPOSSIBLE to distinguish "my 6 were closed by
        someone else" from "someone else opened 6 against me" -- they are the same account
        event, and FIFO attribution is a broker convention, not a fact.  The position bus
        removes the OTHER LEG from the sum by having each leg publish its own position.  It
        CANNOT remove manual trading.  Therefore ENFORCE is correct ONLY on an account no human
        trades by hand; on a hand-traded account DETECT is the only honest setting.
        DETECT IS THE DEFAULT.  A guard that would misfire is worse than no guard.

M1 DISCIPLINE (unchanged from the certified classes)
    Every added method's first statement is `if (State != State.Realtime) return;` or returns
    the un-modified argument, so the whole patch set is PROVABLY INERT in a Strategy Analyzer
    backtest.  `HARDENING-STATE-MARK` remains its falsifier.

USAGE
    python build_hd23_challenger.py [--check]
"""
from __future__ import annotations

import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
NS = os.path.abspath(os.path.join(HERE, "..", "ninjascript"))


class PatchError(RuntimeError):
    """Raised when an anchor does not match exactly once. Never caught."""


# =============================================================================================
# patch primitives -- every one asserts EXACTLY ONE match
# =============================================================================================
def _count(text: str, anchor: str) -> int:
    return text.count(anchor)


def replace_once(text: str, anchor: str, new: str, tag: str) -> str:
    n = _count(text, anchor)
    if n != 1:
        raise PatchError(f"{tag}: anchor matched {n} times, expected exactly 1\n---\n{anchor[:400]}")
    return text.replace(anchor, new, 1)


def insert_before(text: str, anchor: str, block: str, tag: str) -> str:
    return replace_once(text, anchor, block + anchor, tag)


def insert_after(text: str, anchor: str, block: str, tag: str) -> str:
    return replace_once(text, anchor, anchor + block, tag)


# =============================================================================================
# the injected C# -- one template, parameterised by how each class names its exec series
# =============================================================================================
FIELDS_AND_HELPERS = r'''
        // =========================================================================================
        // ==== [HD-20..23]  ADDED 2026-09-03 AFTER A LIVE INCIDENT.  ADDED CODE ONLY. ============
        //      No certified field is written in this region and no decision reads anything here.
        // =========================================================================================

        // ---- [HD-21] the session-close flatten books its P&L INLINE and sets pendingAct=ACT_NONE,
        //      so ObserveSettlement's `if (actJustSettled == ACT_NONE) return;` skips it -- and
        //      ResetShadow() is reachable from NOWHERE ELSE.  shFilled then carries that fill into
        //      the NEXT entry, whose settlement reads 2*qty and halts on a bogus PARTIAL-FILL,
        //      blocking entries for the life of the instance while exits keep working.
        //      Fix: remember the flatten, observe it on the next bar, reset the shadow.  M1.
        private bool   sessFlatPending = false;
        private int    sessFlatQty     = 0;
        private double sessFlatPx      = 0.0;

        // ---- [HD-22] export writer: FAIL LOUD, THEN RETRY.
        //      The original `catch (Exception) { export = null; }` was SILENT and nothing in the
        //      class ever retried.  MEASURED 2026-09-01 00:41 ET: two instances enabled 3 s apart,
        //      the second failed silently, disabling the FIRST removed the only writer, and the
        //      live forward ledger was dead for the rest of the day while every health surface --
        //      NT8, the strategy state, the account -- reported normal.
        private string exportPath      = null;
        private int    exportFailBars  = 0;
        private int    exportLoggedFor = -1;

        // ---- [HD-23] ACCOUNT WITNESS.  See the file header of build_hd23_challenger.py for the
        //      incident this exists for, and for the PROOF that the account alone cannot arbitrate
        //      a hand-traded account.  Modes: OFF / DETECT / ENFORCE.  DEFAULT DETECT.
        private const string ACCTW_OFF = "OFF", ACCTW_DETECT = "DETECT", ACCTW_ENFORCE = "ENFORCE";
        private int    acctBreakBars   = 0;
        private int    acctLoggedFor   = -1;
        private int    acctLastExpected= 0;
        private int    acctLastActual  = 0;
        private int    acctLastOthers  = 0;
        private bool   acctArmed       = false;   // false => BLIND => never gates anything
        private bool   acctDegraded    = false;
        private string acctDegradedWhy = "";
        private string posBusPath      = null;

        /// <summary>[HD-23] the ACCOUNT position on the traded instrument, signed. M1-safe.
        /// Returns false when it cannot be read -- which is BLIND, never "flat".  Returning 0 on
        /// failure would be the exact mistake this whole patch exists to stop.</summary>
        private bool HdAccountSignedQty(out int q)
        {
            q = 0;                                                     // C# definite assignment
            if (State != State.Realtime) return false;                 // M1
            try
            {
                NinjaTrader.Cbi.Position pa = __ACCT__;
                if (pa == null) return false;
                q = (pa.MarketPosition == MarketPosition.Long)  ?  pa.Quantity
                  : (pa.MarketPosition == MarketPosition.Short) ? -pa.Quantity : 0;
                return true;
            }
            catch (Exception) { return false; }
        }

        private string HdExecInstrumentName()
        { try { return __INSTR__.FullName; } catch (Exception) { return "?"; } }

        /// <summary>[HD-23] publish THIS leg's position so the OTHER leg can subtract it from the
        /// account.  Deliberately NOT the `export` StreamWriter: that holds a long-lived handle and
        /// has its own death mode (HD-22).  Each write is a whole small file moved into place, so a
        /// failed write leaves the PREVIOUS value with an OLD timestamp -- which reads as STALE,
        /// which is the honest answer -- and never a fresh-looking wrong one.  M1.</summary>
        private void PosBusPublish(int mySignedExecQty)
        {
            if (State != State.Realtime) return;                       // M1
            if (string.IsNullOrEmpty(PosBusDir)) return;
            try
            {
                if (posBusPath == null)
                {
                    Directory.CreateDirectory(PosBusDir);
                    posBusPath = Path.Combine(PosBusDir, "posbus_" + Tag + ".csv");
                }
                string line = DateTime.UtcNow.ToString("yyyy-MM-dd HH:mm:ss", CultureInfo.InvariantCulture)
                            + "," + Tag + "," + HdExecInstrumentName() + "," + mySignedExecQty;
                string tmp = posBusPath + ".tmp";
                File.WriteAllText(tmp, line);
                if (File.Exists(posBusPath)) File.Replace(tmp, posBusPath, null);
                else                         File.Move(tmp, posBusPath);
            }
            catch (Exception ex) { HdDiagRow("POSBUS", "publish_failed=" + ex.GetType().Name); }
        }

        /// <summary>[HD-23] sum every OTHER leg's published position on MY exec instrument.
        /// Returns false when the bus is unusable -- that is BLIND, and BLIND NEVER GATES.
        /// A peer that is STALE is still COUNTED, because a disabled strategy keeps its position on
        /// the account, so its last published value stays true; the staleness is reported, not
        /// silently dropped.  A peer that has NEVER published is invisible and contributes 0 --
        /// that is the residual hole, and it is why ENFORCE requires a dedicated account.</summary>
        private bool PosBusReadOthers(out int others, out string why)
        {
            others = 0; why = "";                                      // C# definite assignment
            if (State != State.Realtime) { why = "not_realtime"; return false; }   // M1
            if (string.IsNullOrEmpty(PosBusDir)) { why = "posbus_dir_unset"; return false; }
            try
            {
                string me = HdExecInstrumentName();
                if (me == "?") { why = "exec_instrument_unreadable"; return false; }
                string[] files = Directory.GetFiles(PosBusDir, "posbus_*.csv");
                foreach (string f in files)
                {
                    string bn = Path.GetFileNameWithoutExtension(f);
                    if (bn == "posbus_" + Tag) continue;                       // that row is me
                    string[] p = File.ReadAllText(f).Trim().Split(',');
                    if (p.Length < 4) { why = "malformed:" + bn; return false; }
                    if (p[2] != me) continue;                                  // other instrument
                    int q;
                    if (!int.TryParse(p[3], out q)) { why = "badqty:" + bn; return false; }
                    DateTime tsx;
                    if (!DateTime.TryParseExact(p[0], "yyyy-MM-dd HH:mm:ss", CultureInfo.InvariantCulture,
                            System.Globalization.DateTimeStyles.None, out tsx))
                    { why = "badts:" + bn; return false; }
                    others += q;
                    double ageSec = (DateTime.UtcNow - tsx).TotalSeconds;
                    if (ageSec > Math.Max(1, PosBusStaleSec))
                    {
                        acctDegraded = true;
                        acctDegradedWhy = "peer_stale:" + bn + " age=" + (int)ageSec + "s q=" + q
                                        + " (still counted: a stopped leg keeps its position)";
                    }
                }
                return true;
            }
            catch (Exception ex) { why = "read_failed:" + ex.GetType().Name; return false; }
        }

        /// <summary>[HD-23] THE FOURTH WITNESS.  Compares the ACCOUNT against (me + published
        /// peers).  DETECT logs at ERROR and changes nothing.  ENFORCE additionally latches the
        /// halt and lets HdExitQty clamp an exit that the account cannot support.  M1.</summary>
        private void AcctWitness(int myLedgerExecQty)
        {
            if (State != State.Realtime) return;                       // M1
            if (AcctWitnessMode == ACCTW_OFF) { acctArmed = false; return; }

            acctDegraded = false; acctDegradedWhy = "";
            PosBusPublish(myLedgerExecQty);

            int others; string why; int actual;
            bool ok = PosBusReadOthers(out others, out why);
            if (ok && !HdAccountSignedQty(out actual)) { ok = false; why = "account_position_unreadable"; actual = 0; }
            else if (!ok) actual = 0;
            else HdAccountSignedQty(out actual);

            if (!ok)
            {
                acctArmed = false;
                if (acctLoggedFor != CurrentBar)
                {
                    acctLoggedFor = CurrentBar;
                    LogWarn("ACCT-WITNESS-BLIND " + why + " -- the account CANNOT be checked this "
                          + "bar; entries and exits are UNCHANGED.  A blind guard must not gate.");
                }
                return;
            }
            acctArmed = true;
            acctLastExpected = myLedgerExecQty + others;
            acctLastActual   = actual;
            acctLastOthers   = others;

            if (acctLastExpected == acctLastActual) { acctBreakBars = 0; return; }

            acctBreakBars++;
            string msg = "ACCT-MISMATCH expected=" + acctLastExpected + " actual=" + acctLastActual
                       + " mine=" + myLedgerExecQty + " peers=" + others
                       + " bars=" + acctBreakBars + " mode=" + AcctWitnessMode
                       + (acctDegraded ? " DEGRADED(" + acctDegradedWhy + ")" : "");
            HdDiagRow("ACCTW", msg);
            if (acctBreakBars < Math.Max(1, AcctConfirmBars))
            {
                if (acctLoggedFor != CurrentBar)
                { acctLoggedFor = CurrentBar; LogWarn(msg + " (unconfirmed, waiting for fill propagation)"); }
                return;
            }
            if (acctLoggedFor != CurrentBar) { acctLoggedFor = CurrentBar; LogErr(msg); }
            if (AcctWitnessMode == ACCTW_ENFORCE) Halt("ACCT-DIVERGENCE " + msg);
        }

        /// <summary>[HD-23] ENFORCE only: an exit must never take the ACCOUNT past flat AGAINST me,
        /// because that is not an exit -- it is an ENTRY in the opposite direction.  Returns `want`
        /// unchanged in every other case, and ALWAYS outside State.Realtime (M1).</summary>
        private int HdExitQty(int want, bool iAmLong)
        {
            if (State != State.Realtime)            return want;       // M1
            if (AcctWitnessMode != ACCTW_ENFORCE)   return want;
            if (!acctArmed)                         return want;       // BLIND never gates
            if (acctLastExpected == acctLastActual) return want;
            int myImplied = acctLastActual - acctLastOthers;           // what the ACCOUNT says is mine
            int have = iAmLong ? myImplied : -myImplied;
            int safe = Math.Max(0, Math.Min(want, have));
            if (safe != want)
                LogErr("EXIT-CLAMPED want=" + want + " safe=" + safe + " acctImpliedMine=" + myImplied
                     + " -- the account cannot support this exit; submitting " + safe
                     + " so that it CANNOT OPEN a position.  The ledger is torn down regardless.");
            return safe;
        }

        /// <summary>[HD-22] keep the forward decision ledger alive.  Called once per realtime bar.
        /// Retries with append:true so a second instance can never truncate the first one's rows --
        /// which is exactly how the live P1 ledger died on 2026-09-01.  M1.</summary>
        private void HdExportEnsure()
        {
            if (State != State.Realtime) return;                       // M1
            if (string.IsNullOrEmpty(ExportDir)) return;
            if (export != null) { exportFailBars = 0; return; }
            exportFailBars++;
            if (exportLoggedFor != CurrentBar)
            {
                exportLoggedFor = CurrentBar;
                LogErr("EXPORT-DEAD bars=" + exportFailBars + " path=" + (exportPath == null ? "?" : exportPath)
                     + " -- the forward decision ledger is NOT being written.  Trading is unaffected; "
                     + "EVIDENCE IS BEING LOST.  Retrying every bar.");
            }
            try
            {
                Directory.CreateDirectory(ExportDir);
                if (exportPath == null) return;                         // never guessed, only reused
                StreamWriter w = new StreamWriter(exportPath, true);
                w.AutoFlush = true;
                export = w;
                LogWarn("EXPORT-REOPENED after " + exportFailBars + " bar(s), append=true");
                exportFailBars = 0;
            }
            catch (Exception ex) { HdDiagRow("EXPORT", "retry_failed=" + ex.GetType().Name); }
        }

'''

# ---------------------------------------------------------------------------------------------
# [HD-20] warm-up shadow seed -- identical text in all four classes
# ---------------------------------------------------------------------------------------------
WARMUP_OLD = '''            if (!firstRealtimeBarSeen)
            {
                firstRealtimeBarSeen = true;
                if (nt8 != ledgerQty)
                {
                    entriesBlockedUntilAgree = true;
                    LogWarn("WARMUP-CARRY-NONFLAT ledger=" + ledgerQty + " strategyPosition=" + nt8);
                }
                else LogInfo("WARMUP-CARRY-FLAT ledger=" + ledgerQty + " strategyPosition=" + nt8);
                return;
            }
            if (entriesBlockedUntilAgree)
            {
                if (nt8 == ledgerQty) { entriesBlockedUntilAgree = false; LogInfo("CARRY-RESOLVED"); }
                return;
            }'''

WARMUP_NEW = '''            if (!firstRealtimeBarSeen)
            {
                firstRealtimeBarSeen = true;
                // [HD-20] SEED THE THIRD WITNESS.  shNetQty is built ONLY from realtime
                // OnExecutionUpdate, so it is 0 on every (re)start -- including a restart that
                // CARRIES A POSITION, where both structural witnesses read N and the shadow reads
                // 0.  The original code compared only nt8 to ledgerQty here and then RETURNED, so
                // the mismatch surfaced one bar later as a RECONCILE-BREAK that could never clear.
                // MEASURED: XM restarted 2026-09-01 13:22:01 holding short 3 and halted at
                // 13:23:00; 1,218 error lines over two days; entries refused; every health surface
                // still green.  Seeding is not "making the check pass": it STATES THE SHADOW'S
                // DOMAIN, which begins at this instant.  WHAT IT CANNOT SEE: any fill before now.
                shNetQty = nt8;
                ResetShadow();
                if (nt8 != ledgerQty)
                {
                    entriesBlockedUntilAgree = true;
                    LogWarn("WARMUP-CARRY-NONFLAT ledger=" + ledgerQty + " strategyPosition=" + nt8
                          + " execImplied<-seeded=" + shNetQty);
                }
                else LogInfo("WARMUP-CARRY-AGREE ledger=" + ledgerQty + " strategyPosition=" + nt8
                           + " execImplied<-seeded=" + shNetQty);
                return;
            }
            if (entriesBlockedUntilAgree)
            {
                if (nt8 == ledgerQty)
                {
                    // [HD-20] re-seed on resolution for the same reason: the shadow saw none of
                    // the fills that produced the position we have just agreed on.
                    shNetQty = nt8; ResetShadow();
                    entriesBlockedUntilAgree = false;
                    LogInfo("CARRY-RESOLVED execImplied<-seeded=" + shNetQty);
                }
                return;
            }'''

# ---------------------------------------------------------------------------------------------
# [HD-22] the silent catch
# ---------------------------------------------------------------------------------------------
CATCH_OLD = "                    catch (Exception) { export = null; }"
CATCH_NEW = '''                    catch (Exception ex)
                    {
                        // [HD-22] WAS: `catch (Exception) { export = null; }` -- silent, and with
                        // no retry anywhere in the class.  That single line killed the live P1
                        // forward ledger on 2026-09-01 and nothing reported it.
                        export = null;
                        LogErr("EXPORT-OPEN-FAILED " + ex.GetType().Name + ": " + ex.Message
                             + " path=" + (exportPath == null ? "?" : exportPath)
                             + " -- HdExportEnsure will retry every realtime bar.");
                    }'''

# ---------------------------------------------------------------------------------------------
# per-file configuration
# ---------------------------------------------------------------------------------------------
P1_EXPORT_OLD = '''                        if (ExportStampUtc) { export = new StreamWriter(Path.Combine(ExportDir,
                            "we_p1pct_" + Tag + "_" + DateTime.UtcNow.ToString("yyyyMMdd_HHmmss") + "Z.csv"), false); } else {
                        export = new StreamWriter(Path.Combine(ExportDir, "we_p1pct_" + Tag + ".csv"), false);
                        }'''
P1_EXPORT_NEW = '''                        // [HD-22] the path is REMEMBERED so a retry reopens the SAME file.
                        // The first open keeps append:false and still writes the header, so the
                        // parity harness receives the byte-identical file it has always received.
                        exportPath = Path.Combine(ExportDir, ExportStampUtc
                            ? ("we_p1pct_" + Tag + "_" + DateTime.UtcNow.ToString("yyyyMMdd_HHmmss") + "Z.csv")
                            : ("we_p1pct_" + Tag + ".csv"));
                        export = new StreamWriter(exportPath, false);'''

XM_EXPORT_OLD = '''                        if (ExportStampUtc) { export = new StreamWriter(Path.Combine(ExportDir,
                            "we_xm_" + Tag + "_" + DateTime.UtcNow.ToString("yyyyMMdd_HHmmss") + "Z.csv"), false); } else {
                        export = new StreamWriter(Path.Combine(ExportDir, "we_xm_" + Tag + ".csv"), false);
                        }'''
XM_EXPORT_NEW = '''                        // [HD-22] path remembered so a retry reopens the SAME file; first open
                        // keeps append:false and the header, so parity sees the identical file.
                        exportPath = Path.Combine(ExportDir, ExportStampUtc
                            ? ("we_xm_" + Tag + "_" + DateTime.UtcNow.ToString("yyyyMMdd_HHmmss") + "Z.csv")
                            : ("we_xm_" + Tag + ".csv"));
                        export = new StreamWriter(exportPath, false);'''

PROPS = '''
        // ---- [HD-23] account witness + position bus.  All four default to a SAFE, NON-GATING
        //      configuration: PosBusDir "" disables the bus entirely and AcctWitnessMode DETECT
        //      never changes an order.  Turning on ENFORCE is an OWNER decision and is correct
        //      ONLY on an account that no human trades by hand -- see LIVE_SAFETY_FINDINGS.
        [NinjaScriptProperty] public string PosBusDir       { get; set; }   // HD-23, "" = OFF
        [NinjaScriptProperty] public string AcctWitnessMode { get; set; }   // OFF|DETECT|ENFORCE
        [NinjaScriptProperty] public int    PosBusStaleSec  { get; set; }   // HD-23, 300
        [NinjaScriptProperty] public int    AcctConfirmBars { get; set; }   // HD-23, 2
'''

DEFAULTS = '''
                // [HD-23] SAFE DEFAULTS: bus off, witness DETECT-only, nothing gated.
                PosBusDir = ""; AcctWitnessMode = "DETECT"; PosBusStaleSec = 300; AcctConfirmBars = 2;'''


FILES = [
    dict(
        src="WeeklyEdgeP1PCTMnq_v1.cs", dst="WeeklyEdgeP1PCTMnq_v2.cs",
        old_cls="WeeklyEdgeP1PCTMnq_v1", new_cls="WeeklyEdgeP1PCTMnq_v2",
        acct="PositionsAccount[EXEC]", instr="Instruments[EXEC]",
        export_old=P1_EXPORT_OLD, export_new=P1_EXPORT_NEW,
        settle="            ObserveSettlement(hdAct0, ((hdAct0 == ACT_ENTER) ? hdSize0 : hdQty0) * MnqPerNq, Open[0]);",
        assert_call="            AssertLedgerMatchesStrategyPosition(myQty * MnqPerNq);",
        acct_arg="myQty * MnqPerNq",
        family="P1", book="LIVE-MNQ",
        exits=[
            ('                ExitLong(EXEC, myQty * MnqPerNq, "XLsess", "L");',
             '                sessFlatPending = true; sessFlatQty = myQty * MnqPerNq; sessFlatPx = Close[0];  // [HD-21]\n'
             '                { int _q = HdExitQty(myQty * MnqPerNq, true); if (_q > 0) ExitLong(EXEC, _q, "XLsess", "L"); }'),
            ('                ExitLong(EXEC, myQty * MnqPerNq, "XL", "L"); pendingAct = ACT_EXIT;',
             '                { int _q = HdExitQty(myQty * MnqPerNq, true); if (_q > 0) ExitLong(EXEC, _q, "XL", "L"); }\n'
             '                pendingAct = ACT_EXIT;'),
        ],
    ),
    dict(
        src="WeeklyEdgeXMConflictMnq_v1.cs", dst="WeeklyEdgeXMConflictMnq_v2.cs",
        old_cls="WeeklyEdgeXMConflictMnq_v1", new_cls="WeeklyEdgeXMConflictMnq_v2",
        acct="PositionsAccount[MNQ]", instr="Instruments[MNQ]",
        export_old=XM_EXPORT_OLD, export_new=XM_EXPORT_NEW,
        settle="            ObserveSettlement(hdAct0, ((hdAct0 == ACT_ENTER) ? Qty : hdQty0) * MnqPerNq, Opens[NQ][0]);",
        assert_call="            AssertLedgerMatchesStrategyPosition(myPos * Qty * MnqPerNq);",
        acct_arg="myPos * Qty * MnqPerNq",
        family="XM", book="LIVE-MNQ",
        exits=[
            ('                if (myPos > 0) ExitLong(MNQ, Qty * MnqPerNq, "XM_X", "XM_L");\n'
             '                else           ExitShort(MNQ, Qty * MnqPerNq, "XM_X", "XM_S");\n'
             '                Halt("DEAD-SERIES flatten submitted; ledger deliberately NOT adjusted");',
             '                { int _q = HdExitQty(Qty * MnqPerNq, myPos > 0);\n'
             '                  if (_q > 0) { if (myPos > 0) ExitLong(MNQ, _q, "XM_X", "XM_L");\n'
             '                                else           ExitShort(MNQ, _q, "XM_X", "XM_S"); } }\n'
             '                ResetShadow();   // [HD-21] hygiene: this path never reaches ObserveSettlement\n'
             '                Halt("DEAD-SERIES flatten submitted; ledger deliberately NOT adjusted");'),
            ('                    if (myPos > 0) ExitLong(MNQ, Qty * MnqPerNq, "XM_DIS", "XM_L");\n'
             '                    else           ExitShort(MNQ, Qty * MnqPerNq, "XM_DIS", "XM_S");',
             '                    { int _q = HdExitQty(Qty * MnqPerNq, myPos > 0);\n'
             '                      if (_q > 0) { if (myPos > 0) ExitLong(MNQ, _q, "XM_DIS", "XM_L");\n'
             '                                    else           ExitShort(MNQ, _q, "XM_DIS", "XM_S"); } }'),
            ('                if (myPos > 0) ExitLong(MNQ, Qty * MnqPerNq, "XM_X", "XM_L");\n'
             '                else           ExitShort(MNQ, Qty * MnqPerNq, "XM_X", "XM_S");\n'
             '                pendingAct = ACT_EXIT;',
             '                { int _q = HdExitQty(Qty * MnqPerNq, myPos > 0);\n'
             '                  if (_q > 0) { if (myPos > 0) ExitLong(MNQ, _q, "XM_X", "XM_L");\n'
             '                                else           ExitShort(MNQ, _q, "XM_X", "XM_S"); } }\n'
             '                pendingAct = ACT_EXIT;'),
        ],
    ),
    dict(
        src="WeeklyEdgeP1PCT_v3.cs", dst="WeeklyEdgeP1PCT_v4.cs",
        old_cls="WeeklyEdgeP1PCT_v3", new_cls="WeeklyEdgeP1PCT_v4",
        acct="PositionAccount", instr="Instrument",
        export_old=P1_EXPORT_OLD, export_new=P1_EXPORT_NEW,
        settle="            ObserveSettlement(hdAct0, (hdAct0 == ACT_ENTER) ? hdSize0 : hdQty0, Open[0]);",
        assert_call="            AssertLedgerMatchesStrategyPosition(myQty);",
        acct_arg="myQty",
        family="P1", book="PAPER-NQ",
        exits=[
            ('                ExitLong(myQty, "XLsess", "L");',
             '                sessFlatPending = true; sessFlatQty = myQty; sessFlatPx = Close[0];  // [HD-21]\n'
             '                { int _q = HdExitQty(myQty, true); if (_q > 0) ExitLong(_q, "XLsess", "L"); }'),
            ('                ExitLong(myQty, "XL", "L"); pendingAct = ACT_EXIT;',
             '                { int _q = HdExitQty(myQty, true); if (_q > 0) ExitLong(_q, "XL", "L"); }\n'
             '                pendingAct = ACT_EXIT;'),
        ],
    ),
    dict(
        src="WeeklyEdgeXMConflict_v4.cs", dst="WeeklyEdgeXMConflict_v5.cs",
        old_cls="WeeklyEdgeXMConflict_v4", new_cls="WeeklyEdgeXMConflict_v5",
        acct="PositionAccount", instr="Instrument",
        export_old=XM_EXPORT_OLD, export_new=XM_EXPORT_NEW,
        settle="            ObserveSettlement(hdAct0, (hdAct0 == ACT_ENTER) ? Qty : hdQty0, Opens[NQ][0]);",
        assert_call="            AssertLedgerMatchesStrategyPosition(myPos * Qty);",
        acct_arg="myPos * Qty",
        family="XM", book="PAPER-NQ",
        exits=[
            ('                if (myPos > 0) ExitLong(Qty, "XM_X", "XM_L"); else ExitShort(Qty, "XM_X", "XM_S");\n'
             '                Halt("DEAD-SERIES flatten submitted; ledger deliberately NOT adjusted");',
             '                { int _q = HdExitQty(Qty, myPos > 0);\n'
             '                  if (_q > 0) { if (myPos > 0) ExitLong(_q, "XM_X", "XM_L"); else ExitShort(_q, "XM_X", "XM_S"); } }\n'
             '                ResetShadow();   // [HD-21] hygiene: this path never reaches ObserveSettlement\n'
             '                Halt("DEAD-SERIES flatten submitted; ledger deliberately NOT adjusted");'),
            ('                    if (myPos > 0) ExitLong(Qty, "XM_DIS", "XM_L"); else ExitShort(Qty, "XM_DIS", "XM_S");',
             '                    { int _q = HdExitQty(Qty, myPos > 0);\n'
             '                      if (_q > 0) { if (myPos > 0) ExitLong(_q, "XM_DIS", "XM_L"); else ExitShort(_q, "XM_DIS", "XM_S"); } }'),
            ('                if (myPos > 0) ExitLong(Qty, "XM_X", "XM_L"); else ExitShort(Qty, "XM_X", "XM_S");\n'
             '                pendingAct = ACT_EXIT;',
             '                { int _q = HdExitQty(Qty, myPos > 0);\n'
             '                  if (_q > 0) { if (myPos > 0) ExitLong(_q, "XM_X", "XM_L"); else ExitShort(_q, "XM_X", "XM_S"); } }\n'
             '                pendingAct = ACT_EXIT;'),
        ],
    ),
]

SESSFLAT_SETTLE = '''            // [HD-21] settle the PREVIOUS bar's session-close flatten before anything else.
            // Its fill incremented shFilled and, because that path sets pendingAct = ACT_NONE,
            // ObserveSettlement would skip it and ResetShadow -- reachable from nowhere else --
            // would never run.  The leak then halts the NEXT entry on a bogus PARTIAL-FILL.
            if (sessFlatPending)
            { ObserveSettlement(ACT_EXIT, sessFlatQty, sessFlatPx); sessFlatPending = false; }
'''

ACCTW_CALL = '''            AcctWitness(__ARG__);          // [HD-23] the FOURTH witness: the ACCOUNT
            HdExportEnsure();              // [HD-22] keep the forward ledger alive
'''


def build_one(cfg: dict, check_only: bool) -> tuple[str, str]:
    src = os.path.join(NS, cfg["src"])
    dst = os.path.join(NS, cfg["dst"])
    with open(src, "rb") as fh:
        raw = fh.read().decode("utf-8")
    # The certified sources are CRLF.  Every anchor in this file is written with LF, so patch in
    # LF space and restore the ORIGINAL line ending on write -- a class that silently changed
    # line endings would produce a meaningless diff against the certified file.
    crlf = "\r\n" in raw
    t = raw.replace("\r\n", "\n")
    orig = t

    # ---- 0. class rename FIRST so nothing injected below gets renamed by accident
    n = t.count(cfg["old_cls"])
    if n < 1:
        raise PatchError(f"{cfg['src']}: class name {cfg['old_cls']} not found")
    t = t.replace(cfg["old_cls"], cfg["new_cls"])

    # ---- 1. fields + helpers, immediately before ResetShadow (unique in every file)
    helpers = (FIELDS_AND_HELPERS
               .replace("__ACCT__", cfg["acct"])
               .replace("__INSTR__", cfg["instr"]))
    t = insert_before(t, "        private void ResetShadow()", helpers, f"{cfg['src']}:HELPERS")

    # ---- 2. [HD-20] warm-up shadow seed
    t = replace_once(t, WARMUP_OLD, WARMUP_NEW, f"{cfg['src']}:HD-20")

    # ---- 3. [HD-22] export path + loud catch
    t = replace_once(t, cfg["export_old"], cfg["export_new"], f"{cfg['src']}:HD-22-open")
    t = replace_once(t, CATCH_OLD, CATCH_NEW, f"{cfg['src']}:HD-22-catch")

    # ---- 4. [HD-21] settle the session-close flatten (P1 family only)
    if cfg["family"] == "P1":
        t = insert_before(t, cfg["settle"], SESSFLAT_SETTLE, f"{cfg['src']}:HD-21-settle")

    # ---- 5. [HD-23] the fourth witness, immediately after the third
    t = insert_after(t, cfg["assert_call"],
                     "\n" + ACCTW_CALL.replace("__ARG__", cfg["acct_arg"]).rstrip("\n"),
                     f"{cfg['src']}:HD-23-call")

    # ---- 6. exit sites
    for i, (old, new) in enumerate(cfg["exits"]):
        t = replace_once(t, old, new, f"{cfg['src']}:EXIT{i}")

    # ---- 7. properties + defaults
    t = insert_before(t, "        [NinjaScriptProperty] public int    RollLeadDays", PROPS,
                      f"{cfg['src']}:PROPS")
    t = insert_after(t, "                RollLeadDays = 8; WarmupCertDir = \"\"; DiagDir = \"\";",
                     DEFAULTS, f"{cfg['src']}:DEFAULTS")

    if t == orig:
        raise PatchError(f"{cfg['src']}: no change produced")

    out = t.replace("\n", "\r\n") if crlf else t
    if not check_only:
        # atomic: build the whole file in memory, encode, write bytes, replace
        data = out.encode("utf-8")
        tmp = dst + ".tmp"
        with open(tmp, "wb") as fh:
            fh.write(data)
        if os.path.getsize(tmp) == 0:
            raise PatchError(f"{cfg['dst']}: refusing to publish an empty file")
        os.replace(tmp, dst)
    return dst, hashlib.sha256(out.encode("utf-8")).hexdigest()


def main() -> int:
    check_only = "--check" in sys.argv
    print("=" * 92)
    print("HD-20..23 CHALLENGER BUILD" + ("  [CHECK ONLY, nothing written]" if check_only else ""))
    print("=" * 92)
    rows = []
    for cfg in FILES:
        dst, h = build_one(cfg, check_only)
        rows.append((cfg["book"], cfg["family"], cfg["old_cls"], cfg["new_cls"], h))
        print(f"  OK  {cfg['book']:<10} {cfg['family']:<3} {cfg['old_cls']:<26} -> {cfg['new_cls']:<26} {h[:16]}")
    print("-" * 92)
    print(f"  {len(rows)}/4 classes patched.  NOTHING WAS COPIED INTO NT8.  Deployment is an owner")
    print("  action at the 2026-09-21 roll window, when both live legs are down and flat.")
    print("=" * 92)
    return 0


if __name__ == "__main__":
    sys.exit(main())
