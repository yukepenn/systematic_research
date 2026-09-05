// =====================================================================================
// WeeklyEdgeXMConflict_v5  -  HARDENED SHADOW of the PARITY-CERTIFIED WeeklyEdgeXMConflict_v2.
//
// RUN runs/G2_LIVE_HARDENING_20260830/ - built to HARDENING_SPEC.md, 2026-08-30.
//
// STATUS: NOT CERTIFIED. NOT DEPLOYED. NOT ENABLED. A shadow, never a replacement.
//
// THE GOVERNING CONSTRAINT (spec 0): this file is the certified file PLUS additions.
// Every certified line below is BYTE-IDENTICAL to WeeklyEdgeXMConflict_v2.  The only
// modified lines are the class declaration and the Name= string.  Every hardening block
// is marked [HD-xx] and is inert in a Strategy Analyzer backtest by one of four
// mechanisms, each named at its site:
//   M1  State == State.Realtime gate  (Transition/Realtime never occur in the Analyzer)
//   M2  event that never fires historically (rejection / broker cancel / disconnect)
//   M3  platform property whose semantics are realtime-only
//   M4  branch provably unreachable with the certified parameter set
// THE INVERSION RULE (spec 0.2): every gate flag defaults to NOT BLOCKING and is only
// ever set to blocking inside an M1 gate.  There is no operator checkbox in the entry path.
// EXITS ARE NEVER GATED.  NOTHING SELF-CORRECTS: on divergence we halt new entries and log.
//
// The certified header follows, unmodified.
// =====================================================================================
// ---------------------------------------------------------------------------------------------
// v2 DIFF vs v1 (WE_XM_PARITY_20260827): identity (class/Name/Tag) + ONE functional guard.
// v1 reproduced the research object EXACTLY on all 1,012 normal sessions (desired_direction
// 100.0000 %, broad_composite max |diff| 0.000000) and diverged on 15 EARLY-CLOSE sessions only.
// v2 declines a session whose 15:45/15:46 exit bar cannot exist, matching the reference.
// ---------------------------------------------------------------------------------------------
// =====================================================================================
// WeeklyEdgeXMConflict_v1 - the FIRST cross-market SIGNAL strategy in this repository.
//
// OBJECT (runs/WE_W101_DIRECTION, WE_W102_XMENGINE, WE_W102c, WE_W105_XMAUDIT):
//   anchor  = OPEN of the bar stamped 09:31  (== the 09:30:00 print; bars are BAR-END stamped)
//   decide  = CLOSE of the bar stamped 09:45
//   drive   = sign(close_0945 - anchor)
//   broad   = mean over {ES, RTY, YM} of  log(close_0945 / anchor_0931) / sigma60(that market)
//             where sigma60 is the SAMPLE std (ddof = 1) of that market's own anchor->decision
//             log return over the previous up-to-60 sessions, EXCLUDING today.
//   TAKE the trade only when sign(broad) != 0 AND sign(broad) != drive  ("NQ moves alone")
//   entry   = market, submitted on the 09:45 bar close -> fills at the 09:46 OPEN
//   exit    = market, submitted on the 15:45 bar close -> fills at the 15:46 OPEN
//   size    = 1. NO alpha stop (W102's stop curve: 20 -> 300 pts, none beat no-stop).
//
// EVIDENCE: 348 trades, 54.3 % hit, $560/trade, $195,003 net, 2022-07 -> 2026-08.
//   rho(weekly, P1/PCT) = +0.081 full window.
// AND THE CAVEATS, which travel with the code:
//   * ~20 of 348 trades carry 85 % of the money (W105).
//   * rho with P1 is +0.464 over the trailing six months against +0.081 full-window (W105).
//   * REGIME_LOCAL BY DATA AVAILABILITY - ES/RTY/YM substrates begin 2022-01-02, so no
//     2006-2021 test exists and none can be built.
//   * W104: this is an RTH OPENING-AUCTION object. It does NOT generalise to other segments.
//   * The only intra-trade risk control is the CLOCK. Worst historical adverse excursion
//     -$10,865 (543 pts) - a SAMPLE MAXIMUM, NOT A BOUND. See DisasterStopPoints below.
//
// STATUS: RESEARCH_ONLY. Not enabled. The owner alone enables real capital.
//
// ---------------------------------------------------------------------------------------
// MULTI-SERIES ENGINEERING - every item the directive requires, solved and stated
// ---------------------------------------------------------------------------------------
// AddDataSeries      : three added series, ES / RTY / YM, 1-minute, declared in State.Configure
//                      in a FIXED order so BarsArray indices are deterministic: 1=ES 2=RTY 3=YM.
// Instrument names   : PARAMETERS, not literals. runs/WE_W44_NT8PARITY/amendment_2.yaml records
//                      a hardcoded instrument silently running the whole decision stack on a
//                      deferred contract (net -$24,269 -> +$8,326). They are also VERIFIED at
//                      State.DataLoaded and a mismatch hard-blocks every order.
// BarsInProgress     : ALL logic runs in BIP 0. Every other BIP returns immediately. The added
//                      series are read, never traded.
// Unindexed accessors: FORBIDDEN in this file. Time[0]/Close[0] are BIP-RELATIVE - inside a
//                      non-zero BIP handler they are that series' own values. Cost a whole silent
//                      no-op version once already (SolarWaveOneContractMNQ_B1_v1.cs:393-401).
//                      Everything here uses Times[i][0] / Closes[i][0] / CurrentBars[i].
// CurrentBars guard  : every series must have >= 1 bar before anything is read.
// Staleness          : a secondary series whose latest bar is older than MaxStaleMinutes at the
//                      anchor or at the decision DISQUALIFIES THE SESSION. NinjaScript hands you
//                      the last bar at or before the primary's time; without this guard a halted
//                      or thin secondary would be silently forward-filled into the composite.
// Session semantics  : SessionIterator on BarsArray[0]. ForcedFlatMin before ActualSessionEnd.
//                      An early close therefore flattens correctly WITHOUT a hardcoded 16:00 -
//                      hardcoded end-of-RTH clocks are the recurring bug in this repo.
// Early close        : if the session ends before the 15:45 bar, the forced-flat fires first and
//                      the position is closed. No trade is left open across a session boundary.
// Holidays           : a session with no 09:31 bar or no 09:45 bar simply never arms. No trade.
// Missing bars       : anchorReady / decisionReady are explicit flags, not inferred from time.
// Rolls              : the primary and all three secondaries MUST use the same roll/merge
//                      convention. The repo convention is NT8's default MergeBackAdjusted
//                      continuous contract. A mixed convention corrupts the composite silently,
//                      so the instrument names are logged once at DataLoaded for the record.
// Live front month   : set the four instrument parameters to the CURRENT front contracts, or use
//                      continuous symbols if the platform is configured for them. There is no
//                      auto-roll here by design - an auto-roll that disagrees with the research
//                      substrate would be an unrecorded parameter.
// Timestamps         : all four series are 1-minute and BAR-END stamped. The composite is built
//                      only from bars whose timestamps are verified aligned at read time.
// =====================================================================================

#region Using declarations
using System;
using System.Collections.Generic;
using System.IO;
using System.Globalization;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
#endregion

namespace NinjaTrader.NinjaScript.Strategies
{
    public class WeeklyEdgeXMConflict_v5 : Strategy
    {
        [NinjaScriptProperty] public string EsInstrument      { get; set; }
        [NinjaScriptProperty] public string RtyInstrument     { get; set; }
        [NinjaScriptProperty] public string YmInstrument      { get; set; }
        [NinjaScriptProperty] public int    AnchorHm          { get; set; }   // 93100
        [NinjaScriptProperty] public int    DecisionHm        { get; set; }   // 94500
        [NinjaScriptProperty] public int    ExitHm            { get; set; }   // 154500
        [NinjaScriptProperty] public int    SigmaLookback     { get; set; }   // 60 sessions
        [NinjaScriptProperty] public int    SigmaMinHist      { get; set; }   // 20 sessions
        [NinjaScriptProperty] public int    MaxStaleMinutes   { get; set; }   // 3
        [NinjaScriptProperty] public int    ForcedFlatMin     { get; set; }   // 21
        [NinjaScriptProperty] public double CommissionRT      { get; set; }   // 4.36
        [NinjaScriptProperty] public double DisasterStopPoints{ get; set; }   // 0 = OFF
        [NinjaScriptProperty] public int    Qty               { get; set; }   // 1
        [NinjaScriptProperty] public string ExportDir         { get; set; }
        [NinjaScriptProperty] public string Tag               { get; set; }
        // ---- [HD] HARDENING INPUTS.  Every one defaults to an INERT value.

        // ---- [HD-23] account witness + position bus.  All four default to a SAFE, NON-GATING
        //      configuration: PosBusDir "" disables the bus entirely and AcctWitnessMode DETECT
        //      never changes an order.  Turning on ENFORCE is an OWNER decision and is correct
        //      ONLY on an account that no human trades by hand -- see LIVE_SAFETY_FINDINGS.
        [NinjaScriptProperty] public string PosBusDir       { get; set; }   // HD-23, "" = OFF
        [NinjaScriptProperty] public string AcctWitnessMode { get; set; }   // OFF|DETECT|ENFORCE
        [NinjaScriptProperty] public int    PosBusStaleSec  { get; set; }   // HD-23, 300
        [NinjaScriptProperty] public int    AcctConfirmBars { get; set; }   // HD-23, 2
        // [HD-24] owner DECLARES this is the only strategy on the account, so peers = 0 is
        //         KNOWN rather than unknown and the witness can arm without a bus.
        //         Default FALSE: an undeclared account stays BLIND, and BLIND never gates.
        [NinjaScriptProperty] public bool   SoleStrategyOnAccount { get; set; }   // HD-24, false
        [NinjaScriptProperty] public int    RollLeadDays                 { get; set; }   // HD-06, 8
        [NinjaScriptProperty] public string WarmupCertDir                { get; set; }   // HD-08, "" = off
        [NinjaScriptProperty] public string DiagDir                      { get; set; }   // HD-13, "" = off
        [NinjaScriptProperty] public bool   ExportStampUtc               { get; set; }   // HD-13, false
        [NinjaScriptProperty] public bool   TraceOrdersLive              { get; set; }   // HD-09, false
        [NinjaScriptProperty] public bool   EmergencyFlattenOnDeadSeries { get; set; }   // HD-12, true

        // ---- series indices, fixed by the order of the AddDataSeries calls
        private const int NQ = 0, ES = 1, RTY = 2, YM = 3;

        // ---- per-session state
        private double anchorNq;
        private double[] anchorX = new double[4];
        private bool anchorReady, decisionReady, sessionDisqualified;
        private DateTime sessionEndTs = DateTime.MinValue;
        private SessionIterator sessIter;

        // ---- causal sigma history: each market's anchor->decision log return, one per session
        private List<double>[] hist = new List<double>[4];

        // ---- our own ledger, mirroring the Python reference exactly
        private const int ACT_NONE = 0, ACT_ENTER = 1, ACT_EXIT = 2;
        private int pendingAct = ACT_NONE, pendingDir = 0;
        private double myEntryPx = 0.0;
        private int myPos = 0;
        private double realizedPnl = 0.0;
        private bool instrumentMismatch = false;
        private StreamWriter export = null;

        // ---- values carried into the export row
        private double lastDrive = 0.0, lastComposite = double.NaN;
        private int lastConflict = 0, lastDesired = 0;
        // =========================================================================================
        // ==== [HD] HARDENING REGION - ADDED CODE ONLY.  No certified field is written here. ======
        // =========================================================================================

        // ---- [HD-01] shadow fill ledger, realtime only.  Parallel to, never a replacement for,
        //      the certified ledger.  M1.
        private int        shFilled   = 0;        // cumulative executed qty for the order in flight
        private double     shAvgPx    = 0.0;      // qty-weighted average fill price
        private bool       shTerminal = false;    // Filled / Rejected / Cancelled seen
        private OrderState shState    = OrderState.Unknown;
        private ErrorCode  shError    = ErrorCode.NoError;
        private int        shNetQty   = 0;        // signed position implied by executions alone

        // ---- [HD-02/03/04/11] the one-way halt latch.  DEFAULT: NOT BLOCKING (spec 0.2).
        private bool   haltEntries             = false;
        private string haltReason              = "";
        private bool   firstRealtimeBarSeen    = false;
        private bool   entriesBlockedUntilAgree= false;
        private string configFault             = null;
        private int    hdBlockedLoggedFor      = -1;

        // ---- [HD-06] roll awareness
        private DateTime rollBlockFrom  = DateTime.MaxValue;
        private bool     rollResolved   = false;
        private DateTime rollAlertedFor = DateTime.MinValue;

        // ---- [HD-07/08] warm-up.  DEFAULT: NOT BLOCKING.
        private bool         warmupBlocked = false;
        private List<string> warmupRows    = new List<string>();
        private string       warmupVerdict = "GO";

        // ---- [HD-13] realtime-only diagnostics, written to a SEPARATE file.  The certified
        //      per-bar export format is frozen; no column is added, removed or reordered.
        private StreamWriter hdDiag    = null;
        private string       hdDiagDay = "";

        // ---- [HD-15] sessionEndTs staleness detector
        private DateTime hdStaleLoggedFor = DateTime.MinValue;

        // ---- [HD-12] dead-secondary emergency flatten, submitted at most once
        private bool hdDeadFlattenSubmitted = false;

        // ---- logging channels.  Headless account strategy: Log() is primary (Control Center Log
        //      tab is the only reviewable-after-the-fact channel), Print() secondary, Alert() only
        //      from State.Realtime (alert.htm: calls in any other State are silently ignored).
        //      Draw.* is useless here - no chart surface exists.
        private string HdPrefix() { return "[HD " + Name + " " + Tag + "] "; }

        private void LogInfo(string m)
        { try { Log(HdPrefix() + m, LogLevel.Information); Print(HdPrefix() + m); } catch (Exception) { } }

        private void LogWarn(string m)
        { try { Log(HdPrefix() + m, LogLevel.Warning); Print(HdPrefix() + m); } catch (Exception) { }
          HdAlert("warn", m); }

        private void LogErr(string m)
        { try { Log(HdPrefix() + m, LogLevel.Error); Print(HdPrefix() + m); } catch (Exception) { }
          HdAlert("err", m); }

        private void HdAlert(string id, string msg)
        {
            if (State != State.Realtime) return;               // M1 + alert.htm
            try
            {
                Alert("HD_" + Tag + "_" + id, Priority.High, msg, "", 30,
                      System.Windows.Media.Brushes.Firebrick, System.Windows.Media.Brushes.White);
            }
            catch (Exception) { }
        }

        /// <summary>One-way latch. Blocks NEW ENTRIES ONLY - exits are never gated (spec 0 rule 4).</summary>
        private void Halt(string reason)
        {
            if (!haltEntries) { haltEntries = true; haltReason = reason; }
            LogErr("HALT " + reason);
        }


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
                NinjaTrader.Cbi.Position pa = PositionAccount;
                if (pa == null) return false;
                q = (pa.MarketPosition == MarketPosition.Long)  ?  pa.Quantity
                  : (pa.MarketPosition == MarketPosition.Short) ? -pa.Quantity : 0;
                return true;
            }
            catch (Exception) { return false; }
        }

        private string HdExecInstrumentName()
        { try { return Instrument.FullName; } catch (Exception) { return "?"; } }

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
            // [HD-24] THE SOLE-STRATEGY DECLARATION.  Added 2026-09-05.
            // Without this, an account running exactly ONE strategy is BLIND -- there is no peer
            // to publish a bus file, PosBusDir is empty, this returns false, acctArmed stays
            // false, and ENFORCE silently becomes a NO-OP.  That is the exact configuration the
            // live account has had since XM was withdrawn, so the strongest available guard was
            // unreachable in the only configuration that can actually use it.
            // When the owner DECLARES this is the sole strategy on the account, `others = 0` is
            // not a guess -- it is known, and the witness arms.
            // ⚠️ WHAT IT STILL CANNOT SEE: manual trading by a human. That remains provably
            // unattributable from the account alone.  It does not need to be attributed: the
            // clamp's guarantee is one-sided and holds regardless -- AN EXIT MAY NEVER TAKE THE
            // ACCOUNT ACROSS FLAT AGAINST ME, so it can only ever submit FEWER contracts than
            // asked, and can therefore never CREATE an unowned position.  A hand-flattened
            // account makes the exit submit ZERO, which is exactly right.
            // 🔴 THE DECLARATION IS THE OWNER'S AND IT IS LOAD-BEARING.  Setting it true while a
            // second strategy trades this account would let this leg subtract the other leg's
            // position as if it were the owner's, and clamp a real exit to zero.
            if (SoleStrategyOnAccount && string.IsNullOrEmpty(PosBusDir)) return true;   // others = 0, DECLARED
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

        private void ResetShadow()
        {
            shFilled = 0; shAvgPx = 0.0; shTerminal = false;
            shState = OrderState.Unknown; shError = ErrorCode.NoError;
        }

        /// <summary>THE GATE. M1: in any backtest this is a constant true on every bar.</summary>
        private bool EntriesAllowed()
        {
            if (State != State.Realtime) return true;          // M1 - provably inert in a backtest
            if (haltEntries)             return false;
            if (warmupBlocked)           return false;
            if (entriesBlockedUntilAgree)return false;
            if (RollBlocked())           return false;
            return true;
        }

        private void NoteBlockedEntry()
        {
            if (State != State.Realtime) return;               // M1 (unreachable otherwise)
            if (hdBlockedLoggedFor == CurrentBar) return;
            hdBlockedLoggedFor = CurrentBar;
            string s = "ENTRY-BLOCKED halt=" + haltEntries + "(" + haltReason + ") warmup=" + warmupBlocked
                     + " carry=" + entriesBlockedUntilAgree + " roll=" + RollBlocked();
            LogWarn(s);
            HdDiagRow("BLOCKED", s);
        }

        // =========================================================================================
        // [HD-01] executions.  M1 first statement.  Match by execution.Name - never by
        // execution.Order (an execution can arrive before the order update on a partial fill) and
        // never by OrderId ("is NOT a unique value, since it can change throughout an order's
        // lifetime").  Work only with the PASSED-BY-VALUE parameters; never read Position.Quantity
        // from inside a fill callback.
        // =========================================================================================
        protected override void OnExecutionUpdate(Execution execution, string executionId, double price,
                int quantity, MarketPosition marketPosition, string orderId, DateTime time)
        {
            if (State != State.Realtime) return;               // M1
            if (execution == null || !IsMine(execution.Name)) return;
            int q = quantity; double p = price;                // passed-by-value discipline
            shAvgPx  = (shFilled + q) > 0 ? (shAvgPx * shFilled + p * q) / (shFilled + q) : 0.0;
            shFilled += q;
            shNetQty += (marketPosition == MarketPosition.Long ? q : -q);
            HdDiagRow("EXEC", "name=" + execution.Name + ";q=" + q + ";px=" + p + ";mp=" + marketPosition
                            + ";cumFilled=" + shFilled + ";avgPx=" + shAvgPx + ";netQty=" + shNetQty);
        }

        // =========================================================================================
        // [HD-02] order lifecycle.  M1 + M2 (in the Analyzer no order is ever rejected or
        // broker-cancelled, so even without M1 these branches are unreachable).  Branch on
        // order.OrderState (CURRENT); log the orderState parameter (THIS update) - they differ.
        // Only Filled / Rejected / Cancelled are terminal ("in real-time, some stop orders may
        // only reach 'Accepted' state").  PARTIAL FILL: latch, do not adjust - the research object
        // has no partial-fill semantics and inventing one would be an unrecorded parameter.
        // =========================================================================================
        protected override void OnOrderUpdate(Order order, double limitPrice, double stopPrice, int quantity,
                int filled, double averageFillPrice, OrderState orderState, DateTime time,
                ErrorCode error, string comment)
        {
            if (State != State.Realtime) return;               // M1
            if (order == null || !IsMine(order.Name)) return;

            // historical -> realtime conversion, once, defensively.  We never Cancel/Change an
            // order, so the "modified a historical order" disable cannot occur, but it costs nothing.
            if (order.IsBacktestOrder) { Order rt = GetRealtimeOrder(order); if (rt != null) order = rt; }

            shState = order.OrderState;
            shError = error;

            HdDiagRow("ORDER", "name=" + order.Name + ";updState=" + orderState + ";curState=" + order.OrderState
                             + ";filled=" + order.Filled + ";qty=" + order.Quantity
                             + ";avgFill=" + order.AverageFillPrice + ";err=" + error
                             + ";comment=" + (comment == null ? "" : comment));

            if (order.OrderState == OrderState.Rejected)
                Halt("REJECT name=" + order.Name + " err=" + error + " comment=" + comment);
            else if (order.OrderState == OrderState.Cancelled)
            {
                shTerminal = true;
                if (order.Filled == 0) Halt("CANCELLED-UNFILLED name=" + order.Name);
                else                   Halt("CANCELLED-PARTIAL name=" + order.Name + " filled=" + order.Filled);
            }
            else if (order.OrderState == OrderState.Filled)
                shTerminal = true;
            // Working / Accepted / PartFilled / Suspended / AcceptedByRisk / TriggerPending: not terminal.
        }

        // [HD-13] position audit trail. LOG ONLY - never drives logic (event ordering is not
        // guaranteed on simultaneous fills).  M1.
        protected override void OnPositionUpdate(Position position, double averagePrice,
                int quantity, MarketPosition marketPosition)
        {
            if (State != State.Realtime) return;               // M1
            HdDiagRow("POS", "avgPx=" + averagePrice + ";qty=" + quantity + ";mp=" + marketPosition);
        }

        // =========================================================================================
        // [HD-03] non-terminal / zero / partial fill at the certified settlement point.
        // Takes COPIES and writes nothing back.  A fill-PRICE difference is logged, not halted
        // (real slippage is expected; halting on it would stop the book on ordinary drift).
        // A QUANTITY difference is halted - it makes the ledger structurally wrong.  M1.
        // =========================================================================================
        private void ObserveSettlement(int actJustSettled, int reqQty, double assumedFillPx)
        {
            if (State != State.Realtime) return;               // M1
            if (actJustSettled == ACT_NONE) return;

            if (!shTerminal)             Halt("NON-TERMINAL order at settlement; ledger booked an assumed fill");
            else if (shFilled == 0)      Halt("ZERO-FILL settlement; ledger moved, account did not");
            else if (shFilled != reqQty) Halt("PARTIAL-FILL " + shFilled + "/" + reqQty + "; no research semantics");
            else if (Math.Abs(shAvgPx - assumedFillPx) > 1e-9)
                LogInfo("FILLPX assumed=" + assumedFillPx + " actual=" + shAvgPx);

            HdDiagRow("FILLPX", "act=" + actJustSettled + ";reqQty=" + reqQty + ";assumed=" + assumedFillPx
                              + ";actual=" + shAvgPx + ";filled=" + shFilled
                              + ";terminal=" + shTerminal + ";state=" + shState + ";err=" + shError);
            ResetShadow();
        }

        // =========================================================================================
        // [HD-04] the invariant: ledger vs NT8's STRATEGY position, never PositionAccount.
        // Position is "position related information that pertains to an instance of a strategy";
        // PositionAccount is the REAL ACCOUNT net, which on this account holds P1 + XM + anything
        // manual, so neither ledger would match it on most bars of a two-leg book.
        // PositionAccount appears IN THE LOG LINE ONLY and never gates a decision.
        // Three-way check: ledger vs Position vs shNetQty (executions) - two independent witnesses.
        // The transition-carry case blocks entries UNTIL THE TWO AGREE (self-healing); every
        // subsequent mismatch latches.  M1.
        // =========================================================================================
        private void AssertLedgerMatchesStrategyPosition(int ledgerQty)
        {
            if (State != State.Realtime) return;               // M1

            int nt8 = (Position.MarketPosition == MarketPosition.Long)  ?  Position.Quantity
                    : (Position.MarketPosition == MarketPosition.Short) ? -Position.Quantity : 0;

            if (!firstRealtimeBarSeen)
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
            }
            if (nt8 != ledgerQty || shNetQty != ledgerQty)
                Halt("RECONCILE-BREAK ledger=" + ledgerQty + " strategyPosition=" + nt8
                   + " execImplied=" + shNetQty + " accountPosition=" + HdAccountPositionString());
        }

        private string HdAccountPositionString()
        {
            try { return PositionAccount.Quantity + "(" + PositionAccount.MarketPosition + ")"; }
            catch (Exception) { return "?"; }
        }

        // =========================================================================================
        // [HD-06] expiry awareness / fail-safe roll.  Refuses NEW ENTRIES ONLY; exits untouched.
        // The strategy does NOT roll, does NOT flatten and does NOT disable itself - an auto-roll
        // that disagrees with the research substrate would be an unrecorded parameter.
        // TRAP: Instrument.Expiry on this install is the CONTRACT-MONTH MARKER (first of month),
        // NOT the last trading day.  Never use it as a trading deadline.  HD-05 owns identity,
        // HD-06 owns the clock, and the clock comes from GetNextRolloverDate.
        // M1 twice over: ResolveRollDates is NEVER CALLED in a backtest (so no rollover-collection
        // side effect is possible), and RollBlocked short-circuits on State.
        // =========================================================================================
        private void ResolveRollDates(DateTime now)
        {
            if (State != State.Realtime || rollResolved) return;      // M1
            rollResolved = true;
            try
            {
                DateTime earliest = DateTime.MaxValue;
                string detail = "";
                for (int i = 0; i < BarsArray.Length; i++)
                {
                    if (BarsArray[i] == null || BarsArray[i].Instrument == null
                        || BarsArray[i].Instrument.MasterInstrument == null) continue;
                    DateTime rd = BarsArray[i].Instrument.MasterInstrument.GetNextRolloverDate(now);
                    detail += (i > 0 ? " " : "") + "s" + i + "=" + BarsArray[i].Instrument.FullName
                            + ":" + rd.ToString("yyyy-MM-dd");
                    if (rd > DateTime.MinValue && rd < DateTime.MaxValue && rd < earliest) earliest = rd;
                }
                if (earliest < DateTime.MaxValue)
                    rollBlockFrom = earliest.Date.AddDays(-Math.Max(0, RollLeadDays));
                LogWarn("ROLL-PLAN blockNewEntriesFrom="
                      + (rollBlockFrom == DateTime.MaxValue ? "never" : rollBlockFrom.ToString("yyyy-MM-dd"))
                      + " leadDays=" + RollLeadDays + " earliestStoredRollover="
                      + (earliest == DateTime.MaxValue ? "none" : earliest.ToString("yyyy-MM-dd"))
                      + " [" + detail + "]");
            }
            catch (Exception e)
            {
                LogErr("ROLL-RESOLVE-FAILED " + e.Message);
                rollBlockFrom = DateTime.MaxValue;
            }
        }

        private bool RollBlocked()
        {
            if (State != State.Realtime) return false;                // M1
            if (rollBlockFrom == DateTime.MaxValue) return false;
            return HdBarTime().Date >= rollBlockFrom.Date;
        }

        // =========================================================================================
        // [HD-07/HD-08] warm-up assertion and certificate.
        // BarsRequiredToTrade = 20 is NOT the warm-up requirement.  An under-warm object does not
        // fail closed: it looks exactly like a working strategy while trading a DIFFERENT object.
        // The table is PRINTED BY THE PROGRAM, never assembled by hand.
        // There is NO AllowDegradedWarmup property: a checkbox that lets a non-object trade is not
        // a hardening.  Running short is a redeployment decision, not a runtime toggle.
        // History is measured with Bars.Count / Bars.GetTime(0) / CurrentBar - NEVER by deep bar
        // indexing, which would throw under MaximumBarsLookBack = TwoHundredFiftySix.
        // M1 + the inversion rule: State.Transition never occurs in the Analyzer, so warmupBlocked
        // stays false for the entire backtest and the gate is a constant true.
        // =========================================================================================
        private static string WarmRow(string gate, int spec, int min, int observed,
                                      ref bool nogo, ref bool degraded)
        {
            bool pass = observed >= spec;
            if (observed < min) nogo = true; else if (!pass) degraded = true;
            return gate + "," + spec + "," + min + "," + observed + ","
                 + (pass ? "PASS" : (observed >= min ? "DEGRADED" : "FAIL"));
        }

        private void ReportWarmup(string phase)
        {
            string head = "WARMUP " + phase + " verdict=" + warmupVerdict
                        + " blocked=" + warmupBlocked;
            if (warmupVerdict == "GO") LogInfo(head); else LogErr(head);
            LogInfo("WARMUP-GATE gate,spec,min,observed,pass");
            for (int i = 0; i < warmupRows.Count; i++) LogInfo("WARMUP-GATE " + warmupRows[i]);
            WriteWarmupCertificate(phase);
        }

        private void WriteWarmupCertificate(string phase)
        {
            if (string.IsNullOrEmpty(WarmupCertDir)) return;   // default "" = off (2nd inertness reason)
            StreamWriter w = null;
            try
            {
                Directory.CreateDirectory(WarmupCertDir);
                // UTC-stamped: with NumberRestartAttempts a flaky connection can trigger several
                // full warm-up replays in minutes and their certificates must NOT overwrite.
                string utc = DateTime.UtcNow.ToString("yyyyMMdd_HHmmss");
                w = new StreamWriter(Path.Combine(WarmupCertDir,
                        "warmup_" + Tag + "_" + utc + "Z.csv"), false);
                w.WriteLine("strategy,tag,utc,verdict,gate,spec,min,observed,pass");
                string lead = Name + "," + Tag + "," + utc + "Z," + warmupVerdict + ",";
                for (int i = 0; i < warmupRows.Count; i++) w.WriteLine(lead + warmupRows[i]);
                w.WriteLine("env,phase," + phase);
                w.WriteLine("env,DaysToLoad," + DaysToLoad);
                w.WriteLine("env,current_bar," + CurrentBar);
                foreach (string r in HdEnvRows()) w.WriteLine(r);
                w.Flush();
            }
            catch (Exception e) { try { LogErr("CERT-WRITE-FAILED " + e.Message); } catch (Exception) { } }
            finally { if (w != null) { try { w.Close(); } catch (Exception) { } } }
        }

        // =========================================================================================
        // [HD-13] realtime-only diagnostics.  A SEPARATE FILE - the certified per-bar export
        // format is frozen.  M1 plus the empty-string default: two independent inertness reasons.
        // =========================================================================================
        private void HdDiagRow(string tag, string payload)
        {
            if (State != State.Realtime) return;               // M1
            if (string.IsNullOrEmpty(DiagDir)) return;
            try
            {
                string day = DateTime.UtcNow.ToString("yyyyMMdd");
                if (hdDiag == null || hdDiagDay != day)
                {
                    if (hdDiag != null) { try { hdDiag.Flush(); hdDiag.Close(); } catch (Exception) { } hdDiag = null; }
                    Directory.CreateDirectory(DiagDir);
                    string p = Path.Combine(DiagDir, "we_" + Tag + "_hardening_" + day + "Z.csv");
                    bool fresh = !File.Exists(p);
                    hdDiag = new StreamWriter(p, true);
                    if (fresh) hdDiag.WriteLine("utc,bar_ts,tag,payload");
                    hdDiagDay = day;
                }
                hdDiag.WriteLine(DateTime.UtcNow.ToString("yyyy-MM-dd HH:mm:ss.fff", CultureInfo.InvariantCulture)
                    + "," + HdBarTimeString() + "," + tag
                    + ",\"" + (payload == null ? "" : payload.Replace("\"", "'")) + "\"");
                hdDiag.Flush();
            }
            catch (Exception) { }
        }

        private void HdCloseWriters()
        {
            if (hdDiag != null) { try { hdDiag.Flush(); hdDiag.Close(); } catch (Exception) { } hdDiag = null; }
        }

        // ---- order-name ownership. XM submits exactly four signal names.
        private static bool IsMine(string n)
        { return n == "XM_L" || n == "XM_S" || n == "XM_X" || n == "XM_DIS"; }

        private DateTime HdBarTime()
        { try { return Times[NQ][0]; } catch (Exception) { return DateTime.MinValue; } }

        private string HdBarTimeString()
        { try { return Times[NQ][0].ToString("yyyy-MM-dd HH:mm:ss", CultureInfo.InvariantCulture); }
          catch (Exception) { return ""; } }

        // =========================================================================================
        // [HD-07] XM gate list - PER SERIES, never in aggregate.  An aggregate hides the
        // subset-composite failure: a market whose sigma is NaN is skipped, so comp = acc/cnt is
        // the mean over a SUBSET of {ES, RTY, YM}, silently.  An under-warm XM does not stop; it
        // trades a DIFFERENT SIGNAL.
        // =========================================================================================
        private List<string> BuildWarmupTable()
        {
            List<string> rows = new List<string>();
            string[] nm = { "NQ", "ES", "RTY", "YM" };
            bool nogo = false, degraded = false;
            for (int i = 1; i < 4; i++)
            {
                int obs = (hist != null && hist[i] != null) ? hist[i].Count : 0;
                rows.Add(WarmRow("xm_hist_" + nm[i], SigmaLookback, SigmaMinHist, obs, ref nogo, ref degraded));
            }
            warmupVerdict = nogo ? "NO-GO" : (degraded ? "DEGRADED" : "GO");
            return rows;
        }

        // [HD-14] the strategy states its own session template, closing AUDIT E2 from the inside.
        private List<string> HdEnvRows()
        {
            List<string> r = new List<string>();
            string[] nm = { "NQ", "ES", "RTY", "YM" };
            try
            {
                for (int i = 0; i < 4; i++)
                {
                    if (BarsArray == null || BarsArray.Length <= i || BarsArray[i] == null)
                    { r.Add("env,series_" + i + "," + nm[i] + ",MISSING"); continue; }
                    NinjaTrader.Data.Bars b = BarsArray[i];
                    r.Add("env,series_" + i + "_count," + b.Count);
                    r.Add("env,series_" + i + "_first_time," + (b.Count > 0
                            ? b.GetTime(0).ToString("yyyy-MM-dd HH:mm:ss") : "?"));
                    r.Add("env,series_" + i + "_instrument," + (b.Instrument == null ? "?" : b.Instrument.FullName));
                    r.Add("env,series_" + i + "_expiry," + (b.Instrument == null ? "?"
                            : b.Instrument.Expiry.ToString("yyyy-MM-dd")));
                    r.Add("env,series_" + i + "_trading_hours," + (b.TradingHours == null ? "?" : b.TradingHours.Name));
                    r.Add("env,series_" + i + "_current_bar," + CurrentBars[i]);
                }
                r.Add("env,session_begin," + (sessIter == null ? "?" : sessIter.ActualSessionBegin.ToString("yyyy-MM-dd HH:mm:ss")));
                r.Add("env,session_end," + (sessIter == null ? "?" : sessIter.ActualSessionEnd.ToString("yyyy-MM-dd HH:mm:ss")));
                r.Add("env,instrument_mismatch," + instrumentMismatch);
                r.Add("env,roll_block_from," + (rollBlockFrom == DateTime.MaxValue ? "never" : rollBlockFrom.ToString("yyyy-MM-dd")));
                r.Add("env,config_fault," + (configFault == null ? "none" : configFault));
            }
            catch (Exception e) { r.Add("env,ERROR," + e.Message); }
            return r;
        }

        private void HdLogTemplate()
        {
            string s = "TEMPLATE";
            foreach (string row in HdEnvRows()) s += " | " + row.Substring(4);
            LogInfo(s);
        }

        // =========================================================================================
        // [HD-11] configuration self-assertion.  M4: with the certified configuration
        // (OnBarClose, EPD 1, managed, 1-Minute on ALL FOUR series) configFault stays null.
        // Blocking is via the SAME EntriesAllowed() gate, so exits still run.
        // =========================================================================================
        private void HdConfigAssert()
        {
            if (Calculate != Calculate.OnBarClose)   configFault = "Calculate=" + Calculate;
            else if (EntriesPerDirection != 1)       configFault = "EPD=" + EntriesPerDirection;
            else if (IsUnmanaged)                    configFault = "IsUnmanaged";
            else if (BarsPeriod == null || BarsPeriod.BarsPeriodType != BarsPeriodType.Minute
                                       || BarsPeriod.Value != 1)
                configFault = "period=" + (BarsPeriod == null ? "null"
                            : (BarsPeriod.BarsPeriodType + "/" + BarsPeriod.Value));
            else
            {
                for (int i = 1; i < 4 && configFault == null; i++)
                {
                    if (BarsArray == null || BarsArray.Length <= i || BarsArray[i] == null
                        || BarsArray[i].BarsPeriod == null
                        || BarsArray[i].BarsPeriod.BarsPeriodType != BarsPeriodType.Minute
                        || BarsArray[i].BarsPeriod.Value != 1)
                        configFault = "series" + i + "_period";
                }
            }
            if (configFault != null)
            {
                haltEntries = true; haltReason = "CONFIG " + configFault;
                LogErr("CONFIG-FAULT " + configFault);
            }
        }

        // =========================================================================================
        // [HD-05] THE CERTIFIED DEFECT, CLOSED.  The certified guard reduces "ES 09-26" to "ES"
        // and asks FullName.StartsWith("ES") - and "ESZ6".StartsWith("ES") is TRUE, so THE CONTRACT
        // MONTH IS NEVER CHECKED.  Roll NQ to December while a secondary stays on September and the
        // guard stays false: the strategy trades December NQ against September secondaries and
        // reports itself healthy.
        // The certified loop above is left BYTE-IDENTICAL and this guard runs AFTER it.  Because
        // the certified loop only ever SETS instrumentMismatch = true, running a strictly stronger
        // test afterwards is exactly equivalent to replacing it with the conjunction - and it keeps
        // the certified lines untouched.
        // Compare the OBJECT, not a formatted string: MasterInstrument.Name for the root, and
        // Instrument.Expiry Month/Year for the contract month (on this install Expiry is the
        // contract-month marker, first of month, which is precisely what Month/Year supports).
        // M4: with the certified parameters (ES/RTY/YM 09-26 against primary NQ 09-26, all four
        // Expiry = 2026-09-01) clauses (a), (b) and (c) all pass and instrumentMismatch stays false.
        // =========================================================================================
        private static bool TryParseWanted(string want, out string root, out int mm, out int yy)
        {
            root = null; mm = 0; yy = 0;
            if (string.IsNullOrEmpty(want)) return false;
            string[] parts = want.Trim().Split(' ');
            if (parts.Length < 2) return false;                // "ES" alone -> not parseable
            root = parts[0];
            string[] my = parts[1].Split('-');
            if (my.Length != 2) return false;
            return int.TryParse(my[0], out mm) && int.TryParse(my[1], out yy) && mm >= 1 && mm <= 12;
        }

        private void HdInstrumentGuard()
        {
            string[] want = { null, EsInstrument, RtyInstrument, YmInstrument };
            string[] nm   = { "NQ", "ES", "RTY", "YM" };
            string report = "HD05";
            try
            {
                if (BarsArray == null || BarsArray.Length < 4 || Instrument == null
                    || Instrument.MasterInstrument == null)
                { instrumentMismatch = true; LogErr("HD05 primary or series unresolved"); return; }

                DateTime px = Instrument.Expiry;
                report += " primary=" + Instrument.FullName + ":" + px.ToString("yyyy-MM-dd");

                for (int i = 1; i < 4; i++)
                {
                    if (BarsArray[i] == null || BarsArray[i].Instrument == null
                        || BarsArray[i].Instrument.MasterInstrument == null)
                    { instrumentMismatch = true; report += " " + nm[i] + "=UNRESOLVED"; break; }

                    DateTime ex = BarsArray[i].Instrument.Expiry;
                    report += " " + nm[i] + "=" + BarsArray[i].Instrument.FullName
                            + ":" + ex.ToString("yyyy-MM-dd") + "(want " + want[i] + ")";

                    string wRoot; int wMm, wYy;
                    if (!TryParseWanted(want[i], out wRoot, out wMm, out wYy))
                    { instrumentMismatch = true; report += " UNPARSEABLE"; break; }

                    // (a) ROOT - against MasterInstrument.Name, not a StartsWith on a formatted string
                    if (!string.Equals(BarsArray[i].Instrument.MasterInstrument.Name, wRoot,
                                       StringComparison.OrdinalIgnoreCase))
                    { instrumentMismatch = true; report += " ROOT-MISMATCH"; break; }

                    // (b) CONTRACT MONTH - the half that was missing
                    if (ex.Month != wMm || (ex.Year % 100) != wYy)
                    { instrumentMismatch = true; report += " MONTH-MISMATCH"; break; }

                    // (c) CROSS-SERIES: every secondary on the SAME contract month as the PRIMARY.
                    //     This is the partial-roll case the certified guard cannot see.
                    if (ex.Month != px.Month || ex.Year != px.Year)
                    { instrumentMismatch = true; report += " CROSS-SERIES-MISMATCH vs primary "
                                                        + px.ToString("yyyy-MM-dd"); break; }
                }
            }
            catch (Exception e) { instrumentMismatch = true; report += " EXCEPTION=" + e.Message; }

            report += " -> instrumentMismatch=" + instrumentMismatch;
            if (instrumentMismatch) LogErr(report); else LogInfo(report);
        }

        // =========================================================================================
        // [HD-12] H4: the certified dead-secondary early return sits ABOVE the exit logic, so a
        // secondary that never produces a first bar makes the whole OnBarUpdate return and THE EXIT
        // PATH NEVER RUNS - coupling the ability to close an NQ position to the health of three
        // unrelated feeds, with no error and no alert.
        // This observer runs IMMEDIATELY BEFORE the untouched certified return, on exactly the same
        // bars.  It is the ONE place a hardened class submits an order the certified class would
        // not: realtime only, only with a dead feed AND an open position, behind a property.
        // THE LEDGER IS DELIBERATELY NOT ADJUSTED - the resulting permanent RECONCILE-BREAK is the
        // intended visible state: loud, halted, operator-resolved.  M1.
        // =========================================================================================
        private void HdDeadSeriesObserver()
        {
            if (State != State.Realtime) return;               // M1
            bool secReady = true;
            string cb = "";
            for (int i = 0; i < 4; i++)
            {
                int c = (CurrentBars != null && CurrentBars.Length > i) ? CurrentBars[i] : -1;
                cb += (i > 0 ? "," : "") + c;
                if (i >= 1 && c < 1) secReady = false;
            }
            if (secReady) return;

            LogErr("DEAD-SERIES currentBars=[" + cb + "] myPos=" + myPos
                 + "; the certified early return is about to skip the EXIT path");
            HdDiagRow("DEADSERIES", "currentBars=[" + cb + "];myPos=" + myPos);

            if (myPos != 0 && EmergencyFlattenOnDeadSeries && !hdDeadFlattenSubmitted)
            {
                hdDeadFlattenSubmitted = true;
                { int _q = HdExitQty(Qty, myPos > 0);
                  if (_q > 0) { if (myPos > 0) ExitLong(_q, "XM_X", "XM_L"); else ExitShort(_q, "XM_X", "XM_S"); } }
                ResetShadow();   // [HD-21] hygiene: this path never reaches ObserveSettlement
                Halt("DEAD-SERIES flatten submitted; ledger deliberately NOT adjusted");
            }
        }

        // =========================================================================================
        // The once-per-bar realtime hook.  M1 first statement.  TRAP 2 respected: no accumulator
        // write is ever gated, so hist[i] keeps advancing while entries are blocked.
        // =========================================================================================
        private void HdRealtimeBarHook()
        {
            if (State != State.Realtime) return;               // M1
            ResolveRollDates(HdBarTime());

            if (warmupBlocked)
            {
                warmupRows = BuildWarmupTable();
                if (warmupVerdict == "GO") { warmupBlocked = false; ReportWarmup("REARM"); }
            }

            try
            {
                double lateSec = (DateTime.Now - Times[NQ][0]).TotalSeconds;
                if (lateSec > 90.0)
                    HdDiagRow("LATE", "barTs=" + HdBarTimeString() + ";lateSec="
                            + lateSec.ToString("F1", CultureInfo.InvariantCulture));
            }
            catch (Exception) { }

            if (RollBlocked() && rollAlertedFor != HdBarTime().Date)
            {
                rollAlertedFor = HdBarTime().Date;
                LogErr("ROLL-BLOCK new entries refused from " + rollBlockFrom.ToString("yyyy-MM-dd")
                     + "; EXITS ARE NOT GATED; the four legs roll on FOUR DIFFERENT DATES and the"
                     + " roll itself is an owner reconfigure of all four series, not a code action");
            }
        }

        // [HD-13] XMAGE - the D1 cross-market realtime race, measured without changing behaviour.
        private void HdXmAgeRow(string which, DateTime ts)
        {
            if (State != State.Realtime) return;               // M1
            if (string.IsNullOrEmpty(DiagDir)) return;
            string[] nm = { "NQ", "ES", "RTY", "YM" };
            string p = "which=" + which + ";nqTs=" + ts.ToString("yyyy-MM-dd HH:mm:ss");
            try
            {
                for (int i = 1; i < 4; i++)
                {
                    if (CurrentBars[i] < 1) { p += ";" + nm[i] + "=NOBAR"; continue; }
                    p += ";" + nm[i] + "Ts=" + Times[i][0].ToString("yyyy-MM-dd HH:mm:ss")
                       + ";" + nm[i] + "AgeMin=" + (ts - Times[i][0]).TotalMinutes.ToString("F2", CultureInfo.InvariantCulture)
                       + ";" + nm[i] + "Close=" + Closes[i][0].ToString(CultureInfo.InvariantCulture);
                }
            }
            catch (Exception e) { p += ";ERR=" + e.Message; }
            HdDiagRow("XMAGE", p);
        }

        // =========================================================================================
        // [HD-15] sessionEndTs staleness, by symmetry with P1.  DETECT ONLY.  M1.
        // =========================================================================================
        private void HdSessionEndStaleCheck(DateTime ts, bool firstBar)
        {
            if (State != State.Realtime) return;               // M1
            if (firstBar || sessionEndTs == DateTime.MinValue) return;
            if (ts <= sessionEndTs) return;
            if (hdStaleLoggedFor == ts.Date) return;
            hdStaleLoggedFor = ts.Date;
            LogErr("SESSIONEND-STALE bar=" + ts.ToString("yyyy-MM-dd HH:mm:ss")
                 + " sessionEndTs=" + sessionEndTs.ToString("yyyy-MM-dd HH:mm:ss")
                 + "; the session's first bar was missed.  DETECT ONLY, nothing re-derived.");
        }

        // ==== [HD] END OF HARDENING REGION =======================================================


        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description               = "WEEKLY_EDGE XM_CONFLICT: NQ opening drive taken only "
                                          + "when ES/RTY/YM disagree. RTH opening-auction object.";
                Name                      = "WeeklyEdgeXMConflict_v5";
                Calculate                 = Calculate.OnBarClose;
                EntriesPerDirection       = 1;
                EntryHandling             = EntryHandling.AllEntries;
                IsExitOnSessionCloseStrategy = false;   // we flatten ourselves, session-relative
                IncludeCommission         = true;
                BarsRequiredToTrade       = 20;

                EsInstrument       = "ES 09-26";
                RtyInstrument      = "RTY 09-26";
                YmInstrument       = "YM 09-26";
                AnchorHm           = 93100;
                DecisionHm         = 94500;
                ExitHm             = 154500;
                SigmaLookback      = 60;
                SigmaMinHist       = 20;
                MaxStaleMinutes    = 3;
                ForcedFlatMin      = 21;
                CommissionRT       = 4.36;
                DisasterStopPoints = 0.0;     // OFF by default. See the header: no level selected.
                Qty                = 1;
                ExportDir          = "";
                Tag                = "xm2";
                // ---- [HD] hardening defaults.  All inert.  Tag is UNCHANGED so the per-bar export
                //      filename is identical between the certified and the hardened class.
                Description = Description + "  HARDENED SHADOW (G2_LIVE_HARDENING_20260830) - "
                            + "realtime reconciliation, warm-up assertion, roll block, FIXED "
                            + "instrument-month guard.  NOT CERTIFIED, NOT DEPLOYED.";
                RollLeadDays = 8; WarmupCertDir = ""; DiagDir = "";
                // [HD-23] SAFE DEFAULTS: bus off, witness DETECT-only, nothing gated.
                PosBusDir = ""; AcctWitnessMode = "DETECT"; PosBusStaleSec = 300; AcctConfirmBars = 2;
                SoleStrategyOnAccount = false;   // [HD-24] undeclared => BLIND => never gates
                ExportStampUtc = false; TraceOrdersLive = false;
                EmergencyFlattenOnDeadSeries = true;   // inert: M1-gated

                // ---- [HD-09/HD-10] declared platform properties (spec 4).  M3.
                RealtimeErrorHandling       = RealtimeErrorHandling.StopCancelClose;  // NT8 default, explicit
                DisconnectDelaySeconds      = 10;                                     // install default, explicit
                StartBehavior               = StartBehavior.WaitUntilFlat;            // NT8 default, explicit
                IsAdoptAccountPositionAware = false;                                  // refuse to inherit
                IsUnmanaged                 = false;                                  // managed approach retained
                IgnoreOverfill              = false;                                  // NT8 handles overfills
                // RestartsWithinMinutes / SetOrderQuantity / MaximumBarsLookBack:
                //   DELIBERATELY NOT DECLARED - see WeeklyEdgeP1PCT_v2.cs and spec 4 for the reasons.
            }
            else if (State == State.Configure)
            {
                // FIXED ORDER. BarsArray indices 1,2,3 are relied on everywhere below.
                AddDataSeries(EsInstrument,  BarsPeriodType.Minute, 1);
                AddDataSeries(RtyInstrument, BarsPeriodType.Minute, 1);
                AddDataSeries(YmInstrument,  BarsPeriodType.Minute, 1);
                TraceOrders = TraceOrdersLive;   // [HD-09] property defaults FALSE
            }
            else if (State == State.DataLoaded)
            {
                sessIter = new SessionIterator(BarsArray[NQ]);
                for (int i = 0; i < 4; i++) hist[i] = new List<double>();

                // VERIFY the added series are what was asked for. A mismatch hard-blocks orders
                // rather than trading a silently wrong composite.
                string[] want = { null, EsInstrument, RtyInstrument, YmInstrument };
                if (BarsArray == null || BarsArray.Length < 4) instrumentMismatch = true;
                else
                {
                    for (int i = 1; i < 4; i++)
                    {
                        if (BarsArray[i] == null || BarsArray[i].Instrument == null
                            || BarsArray[i].Instrument.MasterInstrument == null)
                        { instrumentMismatch = true; break; }
                        string got = BarsArray[i].Instrument.FullName;
                        if (string.IsNullOrEmpty(got) || string.IsNullOrEmpty(want[i])
                            || !got.StartsWith(want[i].Split(' ')[0], StringComparison.OrdinalIgnoreCase))
                        { instrumentMismatch = true; break; }
                    }
                }
                HdInstrumentGuard();     // [HD-05] the certified guard above is UNTOUCHED; this one
                                         //         adds the contract-month and cross-series clauses.
                HdConfigAssert();        // [HD-11] M4
                if (!string.IsNullOrEmpty(ExportDir))
                {
                    try
                    {
                        Directory.CreateDirectory(ExportDir);
                        // [HD-13] ExportStampUtc defaults FALSE -> certified filename preserved.
                        // [HD-22] path remembered so a retry reopens the SAME file; first open
                        // keeps append:false and the header, so parity sees the identical file.
                        exportPath = Path.Combine(ExportDir, ExportStampUtc
                            ? ("we_xm_" + Tag + "_" + DateTime.UtcNow.ToString("yyyyMMdd_HHmmss") + "Z.csv")
                            : ("we_xm_" + Tag + ".csv"));
                        export = new StreamWriter(exportPath, false);
                        export.WriteLine("timestamp,nq_open,nq_high,nq_low,nq_close,"
                            + "es_close,es_move,rty_close,rty_move,ym_close,ym_move,"
                            + "nq_drive,broad_composite,conflict_flag,desired_direction,"
                            + "decision_ready,entry_request,exit_request,position,realized_pnl");
                    }
                    catch (Exception ex)
                    {
                        // [HD-22] WAS: `catch (Exception) { export = null; }` -- silent, and with
                        // no retry anywhere in the class.  That single line killed the live P1
                        // forward ledger on 2026-09-01 and nothing reported it.
                        export = null;
                        LogErr("EXPORT-OPEN-FAILED " + ex.GetType().Name + ": " + ex.Message
                             + " path=" + (exportPath == null ? "?" : exportPath)
                             + " -- HdExportEnsure will retry every realtime bar.");
                    }
                }
            }
            // ---- [HD-07/08/14] added states.  NEITHER OCCURS IN A STRATEGY ANALYZER BACKTEST -
            // that is the M1 claim, and the HARDENING-STATE-MARK line below is its falsifier (V2c):
            // the backtest output must contain ZERO such lines.
            else if (State == State.Transition)
            {
                Print("HARDENING-STATE-MARK " + State);
                warmupRows    = BuildWarmupTable();
                warmupBlocked = (warmupVerdict != "GO");
            }
            else if (State == State.Realtime)
            {
                Print("HARDENING-STATE-MARK " + State);
                warmupRows    = BuildWarmupTable();
                warmupBlocked = (warmupVerdict != "GO");
                ReportWarmup("START");
                // [HD-16] DURABLE FORWARD DECISION LEDGER.  v2 flushed the per-bar export ONLY at
                //   State.Terminated.
                //   ⚠️ CORRECTION, recorded because the first diagnosis was WRONG: this does NOT
                //   lose the session.  StreamWriter spills its user-space buffer to the OS
                //   continuously, so the file is populated all along - MEASURED on the unfixed
                //   class 2026-08-31: 46,313,472 bytes / 353,766 rows, current to the minute.
                //   A directory-reported size of 0 while the handle is open is a METADATA
                //   ARTIFACT, not data loss.  NEVER diagnose this from Get-ChildItem length.
                //   The REAL and much smaller exposure is the UN-FLUSHED USER-SPACE TAIL (~KB,
                //   tens of rows), which is lost when the process is KILLED rather than closed -
                //   i.e. exactly the "NT8 restart wiped the strategies" event already on record.
                //   AutoFlush removes that tail.  Worth doing; not the catastrophe first claimed.
                //   AutoFlush is set HERE, inside the State.Realtime block, which by THIS FILE'S
                //   OWN M1 claim (see header) never occurs in a Strategy Analyzer backtest.
                //   Consequences, both deliberate: historical replay stays BUFFERED and fast, and
                //   the change is inert in backtest BY CONSTRUCTION - trade-for-trade identity is
                //   guaranteed rather than merely expected, and HARDENING-STATE-MARK remains its
                //   falsifier.  No decision, threshold, size or order path is touched.
                if (export != null) { try { export.AutoFlush = true; } catch (Exception) { } }
                HdLogTemplate();
                if (haltEntries) LogErr("ENTRIES LATCHED OFF AT START: " + haltReason);
            }
            else if (State == State.Terminated)
            {
                if (export != null) { try { export.Flush(); export.Close(); } catch (Exception) {} export = null; }
                HdCloseWriters();   // [HD-13]
            }
        }

        private static double SampleStd(List<double> v, int lookback, int minHist)
        {
            int n = v.Count;
            if (n < minHist) return double.NaN;
            int k = Math.Min(lookback, n);
            double m = 0.0;
            for (int i = n - k; i < n; i++) m += v[i];
            m /= k;
            double s = 0.0;
            for (int i = n - k; i < n; i++) { double d = v[i] - m; s += d * d; }
            return (k > 1) ? Math.Sqrt(s / (k - 1)) : double.NaN;   // ddof = 1, matches pandas
        }

        /// <summary>latest secondary bar must be no older than MaxStaleMinutes vs the primary</summary>
        private bool SeriesFresh(int i, DateTime nqTs)
        {
            if (CurrentBars[i] < 1) return false;
            double age = (nqTs - Times[i][0]).TotalMinutes;
            return age >= -0.5 && age <= MaxStaleMinutes;
        }

        protected override void OnBarUpdate()
        {
            // ---- ALL logic is on the primary. The added series are read, never traded.
            if (BarsInProgress != NQ) return;
            if (CurrentBars[NQ] < 1) return;
            HdDeadSeriesObserver();   // [HD-12] M1: runs BEFORE the certified return below

            for (int i = 1; i < 4; i++) if (CurrentBars[i] < 1) return;
            HdRealtimeBarHook();      // [HD-06/07/13] M1


            DateTime ts   = Times[NQ][0];
            bool firstBar = BarsArray[NQ].IsFirstBarOfSession;
            bool lastBar  = BarsArray[NQ].IsLastBarOfSession;
            int hm        = ts.Hour * 10000 + ts.Minute * 100;

            // [HD-03] copies taken BEFORE the certified settlement block, which is untouched.
            int hdAct0 = pendingAct, hdQty0 = Math.Abs(myPos) * Qty;
            // ---- 0. settle whatever was submitted on the previous bar; it filled at THIS open
            if (pendingAct == ACT_EXIT)
            {
                realizedPnl += myPos * (Opens[NQ][0] - myEntryPx)
                             * Instrument.MasterInstrument.PointValue * Qty
                             - CommissionRT * Qty;
                myPos = 0;
            }
            else if (pendingAct == ACT_ENTER)
            {
                myEntryPx = Opens[NQ][0];
                myPos = pendingDir;
            }
            int entryReq = (pendingAct == ACT_ENTER) ? pendingDir : 0;
            int exitReq  = (pendingAct == ACT_EXIT) ? 1 : 0;
            pendingAct = ACT_NONE; pendingDir = 0;
            // [HD-03]/[HD-04], both M1.
            ObserveSettlement(hdAct0, (hdAct0 == ACT_ENTER) ? Qty : hdQty0, Opens[NQ][0]);
            AssertLedgerMatchesStrategyPosition(myPos * Qty);
            AcctWitness(myPos * Qty);          // [HD-23] the FOURTH witness: the ACCOUNT
            HdExportEnsure();              // [HD-22] keep the forward ledger alive

            // ---- 1. session bookkeeping. Session-RELATIVE, never a hardcoded end-of-day clock.
            if (firstBar || sessionEndTs == DateTime.MinValue)
            {
                sessIter.GetNextSession(ts, true);
                sessionEndTs = sessIter.ActualSessionEnd;
                anchorReady = false; decisionReady = false; sessionDisqualified = false;
                lastDrive = 0.0; lastComposite = double.NaN;
                lastConflict = 0; lastDesired = 0;
            }
            HdSessionEndStaleCheck(ts, firstBar);   // [HD-15] M1, detect only
            bool forceFlat = ts >= sessionEndTs.AddMinutes(-ForcedFlatMin);

            // ---- 2. the ANCHOR bar (09:31): its OPEN is the 09:30:00 print
            if (hm == AnchorHm && !anchorReady)
            {
                HdXmAgeRow("ANCHOR", ts);   // [HD-13] D1 measurement, M1
                bool fresh = true;
                for (int i = 1; i < 4; i++) if (!SeriesFresh(i, ts)) fresh = false;
                if (!fresh) sessionDisqualified = true;     // no stale forward-fill, ever
                else
                {
                    anchorNq = Opens[NQ][0];
                    for (int i = 1; i < 4; i++) anchorX[i] = Closes[i][0];
                    anchorReady = true;
                }
            }

            // ---- 3. the DECISION bar (09:45)
            if (hm == DecisionHm && anchorReady && !decisionReady && !sessionDisqualified)
            {
                HdXmAgeRow("DECISION", ts);   // [HD-13] D1 measurement, M1
                bool fresh = true;
                for (int i = 1; i < 4; i++) if (!SeriesFresh(i, ts)) fresh = false;
                if (!fresh) sessionDisqualified = true;
                else
                {
                    double drive = Math.Sign(Closes[NQ][0] - anchorNq);
                    double acc = 0.0; int cnt = 0;
                    for (int i = 1; i < 4; i++)
                    {
                        if (anchorX[i] <= 0 || Closes[i][0] <= 0) continue;
                        double r = Math.Log(Closes[i][0] / anchorX[i]);
                        double sg = SampleStd(hist[i], SigmaLookback, SigmaMinHist);
                        if (!double.IsNaN(sg) && sg > 1e-12) { acc += r / sg; cnt++; }
                        hist[i].Add(r);          // appended AFTER use -> today is never in its own sigma
                    }
                    double comp = (cnt > 0) ? acc / cnt : double.NaN;
                    double xs = double.IsNaN(comp) ? 0.0 : Math.Sign(comp);
                    lastDrive = drive; lastComposite = comp;
                    lastConflict = (xs != 0.0 && drive != 0.0 && xs != drive) ? 1 : 0;
                    lastDesired = (lastConflict == 1) ? (int)drive : 0;
                    decisionReady = true;

                    // v2 PARITY FIX (WE_XM_PARITY_20260827). The research object drops any
                    // session whose 15:45/15:46 exit bar does not exist - export_xm_reference.py:
                    // "a signal with no tradeable bar is not a trade". v1 armed anyway and traded
                    // 15 holiday half-days over four years that the research economics never
                    // measured. sessionEndTs comes from the trading-hours template and is known at
                    // 09:45, so this test is CAUSAL - it reads no future bar.
                    DateTime exitTs = ts.Date.AddMinutes((ExitHm / 10000) * 60
                                                       + ((ExitHm / 100) % 100) + 1);
                    bool exitBarExists = exitTs < sessionEndTs.AddMinutes(-ForcedFlatMin);
                    if (!exitBarExists) lastDesired = 0;

                    if (lastDesired != 0 && myPos == 0 && !forceFlat && !instrumentMismatch)
                    {
                        // [HD-04/06/07/11] THE ONLY GATE.  TRAP 1: gate the ORDER SITE, never the
                        // predicate - the exit path at section 5 must never be affected.  The two
                        // certified statements below are byte-identical and simply do not run when
                        // blocked.  M1: EntriesAllowed() is a constant true outside State.Realtime.
                        if (!EntriesAllowed()) { NoteBlockedEntry(); } else {
                        if (lastDesired > 0) EnterLong(Qty, "XM_L"); else EnterShort(Qty, "XM_S");
                        pendingAct = ACT_ENTER; pendingDir = lastDesired;
                        }
                    }
                }
            }

            // ---- 4. the DISASTER stop. OPERATIONAL, not alpha. OFF unless the owner sets it.
            if (myPos != 0 && DisasterStopPoints > 0.0 && pendingAct == ACT_NONE)
            {
                double adverse = myPos * (Lows[NQ][0] - myEntryPx);
                if (myPos < 0) adverse = myPos * (Highs[NQ][0] - myEntryPx);
                if (adverse <= -DisasterStopPoints)
                {
                    { int _q = HdExitQty(Qty, myPos > 0);
                      if (_q > 0) { if (myPos > 0) ExitLong(_q, "XM_DIS", "XM_L"); else ExitShort(_q, "XM_DIS", "XM_S"); } }
                    pendingAct = ACT_EXIT;
                }
            }

            // ---- 5. the ALPHA exit: the clock, and nothing else
            if (myPos != 0 && pendingAct == ACT_NONE && (hm >= ExitHm || forceFlat || lastBar))
            {
                HdDiagRow("SESSFLAT", "hm=" + hm + ";forceFlat=" + forceFlat + ";lastBar=" + lastBar
                                    + ";myPos=" + myPos + ";myEntryPx=" + myEntryPx);   // [HD-13] M1
                { int _q = HdExitQty(Qty, myPos > 0);
                  if (_q > 0) { if (myPos > 0) ExitLong(_q, "XM_X", "XM_L"); else ExitShort(_q, "XM_X", "XM_S"); } }
                pendingAct = ACT_EXIT;
            }

            // ---- 6. per-bar export: SIGNAL and DECISION states, not just P&L
            if (export != null)
            {
                var ci = CultureInfo.InvariantCulture;
                double esM  = (anchorReady && anchorX[ES]  > 0) ? Math.Log(Closes[ES][0]  / anchorX[ES])  : double.NaN;
                double rtyM = (anchorReady && anchorX[RTY] > 0) ? Math.Log(Closes[RTY][0] / anchorX[RTY]) : double.NaN;
                double ymM  = (anchorReady && anchorX[YM]  > 0) ? Math.Log(Closes[YM][0]  / anchorX[YM])  : double.NaN;
                export.WriteLine(string.Join(",",
                    ts.ToString("yyyy-MM-dd HH:mm:ss", ci),
                    Opens[NQ][0].ToString(ci), Highs[NQ][0].ToString(ci),
                    Lows[NQ][0].ToString(ci),  Closes[NQ][0].ToString(ci),
                    Closes[ES][0].ToString(ci),  esM.ToString(ci),
                    Closes[RTY][0].ToString(ci), rtyM.ToString(ci),
                    Closes[YM][0].ToString(ci),  ymM.ToString(ci),
                    lastDrive.ToString(ci), lastComposite.ToString(ci),
                    lastConflict.ToString(ci), lastDesired.ToString(ci),
                    (decisionReady ? 1 : 0).ToString(ci),
                    entryReq.ToString(ci), exitReq.ToString(ci),
                    myPos.ToString(ci), realizedPnl.ToString(ci)));
            }
        }
    }
}
