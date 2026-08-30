// =====================================================================================
// WeeklyEdgeP1PCT_v2  -  HARDENED SHADOW of the PARITY-CERTIFIED WeeklyEdgeP1PCT_v1.
//
// RUN runs/G2_LIVE_HARDENING_20260830/ - built to HARDENING_SPEC.md, 2026-08-30.
//
// STATUS: NOT CERTIFIED. NOT DEPLOYED. NOT ENABLED. A shadow, never a replacement.
//
// THE GOVERNING CONSTRAINT (spec 0): this file is the certified file PLUS additions.
// Every certified line below is BYTE-IDENTICAL to WeeklyEdgeP1PCT_v1.  The only
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
// =====================================================================================
// WeeklyEdgeP1PCT_v1 - P1_v3 WITH THE W98 PER-CONTRACT SESSION BOX. NOTHING ELSE CHANGED.
//
// Derived mechanically from WeeklyEdgeP1_v3.cs. The ONLY functional edit is the session-box
// DENOMINATOR, at its two accumulation sites (the intra-session exit and the session-close
// flatten). Everything else - the 32-config vote, the range throttle, the delta gate, the causal
// quality sizing, the clocks, the order mechanics - is byte-identical to the parity-tested v3.
//
// WHY (runs/WE_W98_BOXDENOM/): a dollar stop on a VARIABLE-SIZE position halts a 2-lot at HALF the
// adverse point move of a 1-lot. P1 runs size 2 on 18.3 % of trades. Measured: loss-halts fired at
// 55.68 points on size-1 sessions and 37.18 on size-2. Per-contract denomination is worth
// +39.0 % weekly $ at a fixed $20,245 drawdown, 53.1 -> 56.3 % positive weeks, maxDD 26,388 ->
// 22,931. The controls carry it: a UNIFORMLY looser dollar box is worth +$6/wk (p = 0.940).
//
// LABEL: REGIME_LOCAL. On 2006-2021 the change REVERSES (-31.4 %) because a $1,300 box was 84 % of
// a typical session's range then and is 19 % now. Keep P1_v3 available for comparison.
//
// BAR TIMESTAMPING (verified, not assumed - runs/WE_W52_NINJASCRIPT/REPORT.md): bars are
// BAR-END stamped in both the Python substrate and NinjaTrader. The first RTH bar is the one
// stamped 09:31 and its OPEN is the 09:30:00 print. There is NO -1 minute shift; v1/v2 applied one
// as a defensive fix for a difference that does not exist and THAT shift was the phase error.
//
// ATTACH TO: NQ 1-minute Last, CME US Index Futures ETH template, "NinjaTrader Brokerage Lifetime"
// commission, Standard fill. Calculate.OnBarClose.
// =====================================================================================
#region Using declarations
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
#endregion

// =====================================================================================
//  WeeklyEdgeP1PCT_v1  -  campaign #7 WEEKLY_EDGE, the P1 object, transcribed from the Python.
//
//  THIS IS NOT SolarWaveOneContractNQ_v5. W44 established that the shipped strategy runs its
//  decision stack on a 3-MINUTE secondary series and is roughly half as active as this object
//  (137 flips against 285 over the same window, 73.19 % decision agreement). This file
//  implements the PYTHON object measured at 14.72 pts/session and must be validated against
//  THAT object, which is what runs/WE_W52_NINJASCRIPT does.
//
//  CLOSED FORM (verified bar-for-bar over 1,558,497 bars, max |difference| = 0.0)
//    The 32 voters apply the throttle and delta masks to the TARGET, after the decision stack,
//    so the whole ensemble collapses to
//        vote = nMemLong * nThrottlePass * (1 + deltaGate) / 32
//        vote >= 0.5   <=>   nMemLong * nThrottlePass * (1 + deltaGate) >= 16
//    Only FOUR combiners are needed, and the THIRTEEN ratchet members are SHARED, because a
//    member's state depends only on price and sigma and never on which set it belongs to.
//    The four member sets are prefixes of the same VolMult ladder: 5, 6, 7 and 13 members.
//
//  TIMESTAMP CONVENTION - the detail that silently breaks parity if it is missed
//    The Python substrate stamps a 1-minute bar with its START minute; NinjaTrader stamps it
//    with its END minute. Every comparison and every time-of-day key below therefore uses
//    the 3-minute grid, so it is made explicit here rather than assumed.
//
//  CAUSALITY
//    Calculate.OnBarClose: OnBarUpdate fires at a bar's CLOSE and a market order fills at the
//    NEXT bar's OPEN. Every feature is built from bar i-1 or earlier, exactly as the Python
//    lags them. Nothing reads the bar it fills on. The strategy also keeps its OWN fill ledger
//    (entry price, size, realised session P&L) so the session box reproduces the Python
//    fills_qexit arithmetic exactly instead of depending on when NinjaTrader updates
//    SystemPerformance.
//
//  Set ExportDir to write a per-bar decision ledger for bar-for-bar parity. Empty disables it.
// =====================================================================================
namespace NinjaTrader.NinjaScript.Strategies
{
    public class WeeklyEdgeP1PCT_v2 : Strategy
    {
        [NinjaScriptProperty] public int    VolPeriod      { get; set; }
        [NinjaScriptProperty] public double SMinTicks      { get; set; }
        [NinjaScriptProperty] public double SMaxTicks      { get; set; }
        [NinjaScriptProperty] public double StopMultiplier { get; set; }
        [NinjaScriptProperty] public int    TiltSma        { get; set; }
        [NinjaScriptProperty] public double TiltMult       { get; set; }
        [NinjaScriptProperty] public double TiltRescale    { get; set; }
        [NinjaScriptProperty] public double WSolar         { get; set; }
        [NinjaScriptProperty] public double WBmom          { get; set; }
        [NinjaScriptProperty] public int    BmomBandDays   { get; set; }
        [NinjaScriptProperty] public double EntryLevel     { get; set; }
        [NinjaScriptProperty] public double ExitLevel      { get; set; }
        [NinjaScriptProperty] public int    EntryBlockMin  { get; set; }
        [NinjaScriptProperty] public int    ForcedFlatMin  { get; set; }
        [NinjaScriptProperty] public double HaltDollars    { get; set; }
        [NinjaScriptProperty] public double TargetDollars  { get; set; }
        [NinjaScriptProperty] public double CommissionRT   { get; set; }
        [NinjaScriptProperty] public int    QualWindow     { get; set; }
        [NinjaScriptProperty] public int    QualMinHist    { get; set; }
        [NinjaScriptProperty] public bool   UseQualitySize { get; set; }
        [NinjaScriptProperty] public bool   UseSessionBox  { get; set; }
        [NinjaScriptProperty] public string ExportDir      { get; set; }
        [NinjaScriptProperty] public string Tag            { get; set; }
        // ---- [HD] HARDENING INPUTS.  Every one defaults to an INERT value, so the historical
        //      path is unchanged and any deviation is recorded in DisplayParameters / GetStrategyState.
        [NinjaScriptProperty] public int    RollLeadDays     { get; set; }   // HD-06, 8
        [NinjaScriptProperty] public string WarmupCertDir    { get; set; }   // HD-08, "" = off
        [NinjaScriptProperty] public string DiagDir          { get; set; }   // HD-13, "" = off
        [NinjaScriptProperty] public bool   ExportStampUtc   { get; set; }   // HD-13, false = certified name
        [NinjaScriptProperty] public bool   TraceOrdersLive  { get; set; }   // HD-09, false = NT8 default
        [NinjaScriptProperty] public string ExpectInstrument { get; set; }   // HD-05, "" = check disabled

        private static readonly double[] VOLM = { 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30 };
        private static readonly int[] SETLEN = { 5, 6, 7, 13 };     // narrow5 / narrow6 / narrow7 / all13
        private const int NMEMB = 13, NSET = 4;

        // ---- shared ratchet members --------------------------------------------------
        private bool[]   mUp     = new bool[NMEMB];
        private double[] mAnchor = new double[NMEMB];
        private double[] mS      = new double[NMEMB];
        private int[]    mSig    = new int[NMEMB];
        private int[]    mPos    = new int[NMEMB];
        private int[]    mPend   = new int[NMEMB];
        private bool initialized = false;
        private long barCount = 0;

        // ---- sigma ---------------------------------------------------------------------
        private Queue<double> diffs = new Queue<double>();
        private double volSum = 0.0, prevClose = double.NaN;

        // ---- HTF tilt ------------------------------------------------------------------
        private List<double> sessCloses = new List<double>();
        private int tilt = 0;

        // ---- B-MOM ---------------------------------------------------------------------
        private int bmom = 0; private bool rthOpen = false;
        private double open0930 = 0.0, bmVpv = 0.0, bmVv = 0.0;
        private Dictionary<int, double> todaySlots = new Dictionary<int, double>();
        private Dictionary<int, List<double>> slotHist = new Dictionary<int, List<double>>();
        private int rthDays = 0;

        private int[] tgtPrev = new int[NSET];

        // ---- session state --------------------------------------------------------------
        private SessionIterator sessIter;
        private DateTime sessionEndTs = DateTime.MinValue;
        private double sessOpen = 0.0, curSessOpen = 0.0, prevSessRet = 0.0;
        private bool   haveSessHi = false;
        private double sessHiCur = 0.0, sessLoCur = 0.0;      // through THIS bar
        private double sessHiPrev = 0.0, sessLoPrev = 0.0;    // through the PREVIOUS bar
        private bool   havePrevExtremes = false;

        // ---- range throttle history -------------------------------------------------------
        private Dictionary<int, List<double>> rngHist = new Dictionary<int, List<double>>();
        private List<int> todKeys = new List<int>();
        private List<double> todRng = new List<double>();

        // ---- lagged carriers ---------------------------------------------------------------
        private double lagClose = double.NaN, lagAtr = double.NaN, lagVwap = double.NaN;
        private double lagRunLen = 0.0, lagCumDelta = 0.0, lagVolNorm = 1.0;
        private double runLen = 0.0; private int lastSgn = 0;
        private double cumDelta = 0.0, vwPv = 0.0, vwVv = 0.0;
        private Queue<double> trQ = new Queue<double>(); private double trSum = 0.0;
        private Queue<double> volQ = new Queue<double>(); private double volSum240 = 0.0;

        // ---- causal quality score ------------------------------------------------------------
        private List<double> qDistOpen = new List<double>(), qPrevRet = new List<double>(),
                             qRunLen = new List<double>(), qDistVwap = new List<double>(),
                             qDeltaMag = new List<double>();
        private int qCount = 0;

        // ---- our own fill ledger, mirroring Python fills_qexit ---------------------------------
        private const int ACT_NONE = 0, ACT_ENTER = 1, ACT_EXIT = 2;
        private int pendingAct = ACT_NONE, pendingSize = 1;
        private double myEntryPx = 0.0; private int myQty = 0;
        private double sessPnl = 0.0; private bool sessStopped = false;
        private int lastScore = 0;

        private StreamWriter export = null;
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

        // ---- order-name ownership. P1 submits exactly three signal names.
        private static bool IsMine(string n)
        { return n == "L" || n == "XL" || n == "XLsess"; }

        private DateTime HdBarTime()
        { try { return Time[0]; } catch (Exception) { return DateTime.MinValue; } }

        private string HdBarTimeString()
        { try { return Time[0].ToString("yyyy-MM-dd HH:mm:ss", CultureInfo.InvariantCulture); }
          catch (Exception) { return ""; } }

        // =========================================================================================
        // [HD-07] P1 gate list, evaluated from the accumulators themselves.
        // qual_entries is the BINDING gate and it is EVENT-driven, not calendar-driven: qCount
        // increments once per ENTRY, so no amount of calendar warm-up guarantees it.  It must be
        // MEASURED.  An under-warm P1 fails OPEN (norm = 0 => all three throttle clauses pass =>
        // nThr = 4 => a far easier vote threshold => it trades MORE than the certified object).
        // =========================================================================================
        private List<string> BuildWarmupTable()
        {
            List<string> rows = new List<string>();
            int rngMin = int.MaxValue;
            foreach (KeyValuePair<int, List<double>> kv in rngHist)
                if (kv.Value != null && kv.Value.Count > 0 && kv.Value.Count < rngMin) rngMin = kv.Value.Count;
            if (rngMin == int.MaxValue) rngMin = 0;

            bool nogo = false, degraded = false;
            rows.Add(WarmRow("sigma_diffs",   VolPeriod,    30,           diffs.Count,      ref nogo, ref degraded));
            rows.Add(WarmRow("tilt_sessions", TiltSma + 1,  TiltSma + 1,  sessCloses.Count, ref nogo, ref degraded));
            rows.Add(WarmRow("bmom_rth_days", BmomBandDays, BmomBandDays, rthDays,          ref nogo, ref degraded));
            rows.Add(WarmRow("rng_sessions",  60,           20,           rngMin,           ref nogo, ref degraded));
            rows.Add(WarmRow("atr_bars",      14,           14,           trQ.Count,        ref nogo, ref degraded));
            rows.Add(WarmRow("volnorm_bars",  240,          30,           volQ.Count,       ref nogo, ref degraded));
            rows.Add(WarmRow("qual_entries",  QualWindow,   QualMinHist,  qCount,           ref nogo, ref degraded));
            warmupVerdict = nogo ? "NO-GO" : (degraded ? "DEGRADED" : "GO");
            return rows;
        }

        // [HD-14] the strategy states its own session template, closing AUDIT E2 from the inside.
        private List<string> HdEnvRows()
        {
            List<string> r = new List<string>();
            try
            {
                r.Add("env,bars_count," + (Bars == null ? -1 : Bars.Count));
                r.Add("env,bars_first_time," + ((Bars != null && Bars.Count > 0)
                        ? Bars.GetTime(0).ToString("yyyy-MM-dd HH:mm:ss") : "?"));
                r.Add("env,trading_hours," + ((Bars != null && Bars.TradingHours != null)
                        ? Bars.TradingHours.Name : "?"));
                r.Add("env,bars_from," + (Bars == null ? "?" : Bars.FromDate.ToString("yyyy-MM-dd")));
                r.Add("env,bars_to," + (Bars == null ? "?" : Bars.ToDate.ToString("yyyy-MM-dd")));
                r.Add("env,instrument," + (Instrument == null ? "?" : Instrument.FullName));
                r.Add("env,expiry," + (Instrument == null ? "?" : Instrument.Expiry.ToString("yyyy-MM-dd")));
                r.Add("env,session_begin," + (sessIter == null ? "?" : sessIter.ActualSessionBegin.ToString("yyyy-MM-dd HH:mm:ss")));
                r.Add("env,session_end," + (sessIter == null ? "?" : sessIter.ActualSessionEnd.ToString("yyyy-MM-dd HH:mm:ss")));
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
        // (OnBarClose, EPD 1, managed, 1-Minute) configFault stays null.  Calculate in particular
        // would TEST CLEAN AND FAIL LIVE: "State.Historical data processes OnBarUpdate() only on
        // the close of each historical bar even if this property is set to OnEachTick".
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
            if (configFault != null)
            {
                haltEntries = true; haltReason = "CONFIG " + configFault;
                LogErr("CONFIG-FAULT " + configFault);
            }
        }

        // =========================================================================================
        // [HD-05] P1 instrument-month guard.  P1 is single-series and the certified file has no
        // guard at all, so this is OPT-IN: ExpectInstrument defaults to "" = check disabled and
        // P1's default behaviour is byte-identical.  M4 + M1 (blocking runs through EntriesAllowed).
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
            if (string.IsNullOrEmpty(ExpectInstrument)) return;          // M4: default = disabled
            string wRoot; int wMm, wYy;
            if (!TryParseWanted(ExpectInstrument, out wRoot, out wMm, out wYy))
            { Halt("HD05 unparseable ExpectInstrument='" + ExpectInstrument + "'"); return; }
            if (Instrument == null || Instrument.MasterInstrument == null)
            { Halt("HD05 primary unresolved"); return; }
            if (!string.Equals(Instrument.MasterInstrument.Name, wRoot, StringComparison.OrdinalIgnoreCase))
            { Halt("HD05 ROOT mismatch got=" + Instrument.MasterInstrument.Name + " want=" + wRoot); return; }
            DateTime ex = Instrument.Expiry;
            if (ex.Month != wMm || (ex.Year % 100) != wYy)
            { Halt("HD05 MONTH mismatch instrument=" + Instrument.FullName
                 + " expiry=" + ex.ToString("yyyy-MM-dd") + " want=" + ExpectInstrument); return; }
            LogInfo("HD05 primary OK instrument=" + Instrument.FullName
                  + " expiry=" + ex.ToString("yyyy-MM-dd") + " want=" + ExpectInstrument);
        }

        // =========================================================================================
        // The once-per-bar realtime hook.  M1 first statement.  Nothing here writes a certified
        // field, and TRAP 2 is respected: no accumulator write is ever gated, so the counters keep
        // advancing while entries are blocked and the re-arm can actually happen.
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
                double lateSec = (DateTime.Now - Time[0]).TotalSeconds;
                if (lateSec > 90.0)
                    HdDiagRow("LATE", "barTs=" + HdBarTimeString() + ";lateSec="
                            + lateSec.ToString("F1", CultureInfo.InvariantCulture));
            }
            catch (Exception) { }

            if (RollBlocked() && rollAlertedFor != HdBarTime().Date)
            {
                rollAlertedFor = HdBarTime().Date;
                LogErr("ROLL-BLOCK new entries refused from " + rollBlockFrom.ToString("yyyy-MM-dd")
                     + "; EXITS ARE NOT GATED; the roll itself is an owner reconfigure, not a code action");
            }
        }

        // =========================================================================================
        // [HD-15] sessionEndTs staleness.  sessionEndTs is refreshed only on IsFirstBarOfSession;
        // a missed 18:01 bar leaves it on the PREVIOUS session's end, making blocked and forceFlat
        // true all day - a silent all-day outage.  DETECT ONLY: re-deriving it would change
        // behaviour.  M1.
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
                 + "; the session's first bar was missed - entries are blocked by the certified"
                 + " clock for the rest of this session.  DETECT ONLY, nothing re-derived.");
        }

        // ==== [HD] END OF HARDENING REGION =======================================================


        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = "WEEKLY_EDGE P1/PCT: P1_v3 with the W98 PER-CONTRACT session box. "
                            + "range throttle, delta gate, session box, causal quality sizing.";
                Name = "WeeklyEdgeP1PCT_v2";
                Calculate = Calculate.OnBarClose;
                EntriesPerDirection = 1;
                EntryHandling = EntryHandling.AllEntries;
                IsExitOnSessionCloseStrategy = false;
                IncludeCommission = true;
                BarsRequiredToTrade = 20;

                VolPeriod = 460; SMinTicks = 40; SMaxTicks = 1200; StopMultiplier = 179;
                TiltSma = 50; TiltMult = 1.25; TiltRescale = 0.9026;
                WSolar = 0.7086; WBmom = 2.83; BmomBandDays = 14;
                EntryLevel = 3.0; ExitLevel = 1.0;
                EntryBlockMin = 30; ForcedFlatMin = 21;
                HaltDollars = 1300.0; TargetDollars = 1000.0; CommissionRT = 4.36;
                QualWindow = 250; QualMinHist = 100;
                UseQualitySize = true; UseSessionBox = true;
                ExportDir = ""; Tag = "p1pct";
                // ---- [HD] hardening defaults.  All inert.  Tag is UNCHANGED so the per-bar export
                //      filename is identical between the certified and the hardened class.
                Description = Description + "  HARDENED SHADOW (G2_LIVE_HARDENING_20260830) - "
                            + "realtime reconciliation, warm-up assertion, roll block, instrument "
                            + "guard.  NOT CERTIFIED, NOT DEPLOYED.";
                RollLeadDays = 8; WarmupCertDir = ""; DiagDir = "";
                ExportStampUtc = false; TraceOrdersLive = false; ExpectInstrument = "";

                // ---- [HD-09/HD-10] declared platform properties (spec 4).  M3: every one of these
                //      is defined in terms of broker rejections, connection loss or strategy start
                //      on an ACCOUNT, so declaring them changes nothing historically.
                RealtimeErrorHandling       = RealtimeErrorHandling.StopCancelClose;  // NT8 default, explicit
                DisconnectDelaySeconds      = 10;                                     // install default, explicit
                StartBehavior               = StartBehavior.WaitUntilFlat;            // NT8 default, explicit
                IsAdoptAccountPositionAware = false;                                  // refuse to inherit
                IsUnmanaged                 = false;                                  // managed approach retained
                IgnoreOverfill              = false;                                  // NT8 handles overfills
                // RestartsWithinMinutes: LEFT AT ITS DEFAULT.  NumberRestartAttempts = 0 already
                //   disables restarts; there is no reason to risk a validation failure.
                // SetOrderQuantity:      DELIBERATELY NOT DECLARED.  Spec 4 gates it on a confirmed
                //   read-back of the effective value, which V0 did not obtain.  Both strategies pass
                //   explicit quantities, so a wrong declaration would silently re-size every trade.
                //   An undeclared property cannot break identity.
                // MaximumBarsLookBack:   DELIBERATELY NOT DECLARED (spec HD-16 recommends omit).
                // Slippage / IncludeTradeHistoryInBacktest / EntriesPerDirection / EntryHandling /
                //   IsExitOnSessionCloseStrategy / IncludeCommission / BarsRequiredToTrade /
                //   Calculate: DO NOT TOUCH.  Every one is part of the certified object.
            }
            // ---- [HD-09] TraceOrders routed through a property that defaults FALSE, so identity
            //      is free and the audit trail is available on a paper deployment.  M4 at default.
            else if (State == State.Configure)
            {
                TraceOrders = TraceOrdersLive;
            }
            else if (State == State.DataLoaded)
            {
                // TickSize is only reliable once the instrument's data is loaded
                for (int m = 0; m < NMEMB; m++) mS[m] = StopMultiplier * TickSize;
                sessIter = new SessionIterator(Bars);
                HdConfigAssert();        // [HD-11] M4
                HdInstrumentGuard();     // [HD-05] M4, opt-in (ExpectInstrument defaults to "")
                if (!string.IsNullOrEmpty(ExportDir))
                {
                    try
                    {
                        Directory.CreateDirectory(ExportDir);
                        // [HD-13] ExportStampUtc defaults FALSE -> the certified filename is used
                        // and the parity harness gets the exact file it expects.  The certified
                        // statement below is byte-identical.
                        if (ExportStampUtc) { export = new StreamWriter(Path.Combine(ExportDir,
                            "we_p1pct_" + Tag + "_" + DateTime.UtcNow.ToString("yyyyMMdd_HHmmss") + "Z.csv"), false); } else {
                        export = new StreamWriter(Path.Combine(ExportDir, "we_p1pct_" + Tag + ".csv"), false);
                        }
                        export.WriteLine("pyts,close,nMem,nThr,dL,ratio,voteOK,size,score,qty,sessPnl,stopped,tilt,bmom,t0,t1,t2,t3,sig0,pend0,anch0,s0");
                    }
                    catch (Exception) { export = null; }
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
                HdLogTemplate();
                if (haltEntries) LogErr("ENTRIES LATCHED OFF AT START: " + haltReason);
            }
            else if (State == State.Terminated)
            {
                if (export != null) { try { export.Flush(); export.Close(); } catch (Exception) { } export = null; }
                HdCloseWriters();   // [HD-13]
            }
        }

        private static int RoundAway(double x)
        {
            return (int)(Math.Sign(x) * Math.Floor(Math.Abs(x) + 0.5));
        }

        private double Sigma() { return (diffs.Count >= 30) ? volSum / diffs.Count : double.NaN; }

        private double ResolveS(double mult)
        {
            double sg = Sigma();
            if (double.IsNaN(sg) || sg <= 0) return StopMultiplier * TickSize;
            return Math.Min(Math.Max(mult * sg, SMinTicks * TickSize), SMaxTicks * TickSize);
        }

        private static double Quantile(List<double> src, int window, double q)
        {
            int nAll = src.Count, start = Math.Max(0, nAll - window), k = nAll - start;
            if (k <= 0) return double.NaN;
            double[] a = new double[k]; src.CopyTo(start, a, 0, k); Array.Sort(a);
            if (k == 1) return a[0];
            double pos = q * (k - 1); int lo = (int)Math.Floor(pos); double frac = pos - lo;
            if (lo >= k - 1) return a[k - 1];
            return a[lo] + frac * (a[lo + 1] - a[lo]);
        }

        private static double MedianLast(List<double> src, int window)
        {
            int nAll = src.Count, start = Math.Max(0, nAll - window), k = nAll - start;
            if (k <= 0) return 0.0;
            double[] a = new double[k]; src.CopyTo(start, a, 0, k); Array.Sort(a);
            return (k % 2 == 1) ? a[k / 2] : 0.5 * (a[k / 2 - 1] + a[k / 2]);
        }

        protected override void OnBarUpdate()
        {
            if (BarsInProgress != 0) return;
            HdRealtimeBarHook();   // [HD-06/07/13] M1: returns immediately unless State.Realtime


            // NinjaTrader stamps a bar with its END minute; the Python substrate stamps it with
            // its START minute. Everything below is keyed on the Python convention.
            // VERIFIED, not assumed: the Python substrate stamps a session's first bar 18:01
            // and its last 17:00 for an 18:00->17:00 session, i.e. it is BAR-END stamped -
            // the same convention NinjaTrader uses. v1/v2 shifted by -1 minute as a defensive
            // fix for a difference that does not exist, and that shift WAS the phase error:
            // it armed B-MOM on the wrong bar (bmom agreement 95.3 %, sign inversions) and
            // moved every time-of-day key. No shift.
            DateTime pyTs = Time[0];
            bool firstBar = Bars.IsFirstBarOfSession;
            bool lastBar  = Bars.IsLastBarOfSession;

            // [HD-03] copies taken BEFORE the certified settlement block, which is untouched.
            int hdAct0 = pendingAct, hdSize0 = pendingSize, hdQty0 = myQty;
            // ---- 0. settle any order submitted on the previous bar; it filled at THIS open ----
            if (pendingAct == ACT_EXIT)
            {
                // W98 PER-CONTRACT BOX: the box accumulates pnl/u, i.e. exactly the Python
                // `spnl += pnl / u` where pnl = u*(px-epx)*PV - COMM*u. Both the point term AND
                // the commission are per contract; dropping only one would be a third convention.
                sessPnl += (Open[0] - myEntryPx) * Instrument.MasterInstrument.PointValue
                         - CommissionRT;
                myQty = 0;
                if (UseSessionBox && (sessPnl <= -HaltDollars || sessPnl >= TargetDollars))
                    sessStopped = true;
            }
            else if (pendingAct == ACT_ENTER)
            {
                myEntryPx = Open[0]; myQty = pendingSize;
            }
            pendingAct = ACT_NONE;
            // [HD-03] observe what the certified block just ASSUMED, then [HD-04] reconcile the
            // ledger against NT8's strategy position and against the executions.  Both are M1.
            ObserveSettlement(hdAct0, (hdAct0 == ACT_ENTER) ? hdSize0 : hdQty0, Open[0]);
            AssertLedgerMatchesStrategyPosition(myQty);

            if (firstBar || sessionEndTs == DateTime.MinValue)
            {
                sessIter.GetNextSession(Time[0], true);
                sessionEndTs = sessIter.ActualSessionEnd;
            }
            HdSessionEndStaleCheck(pyTs, firstBar);   // [HD-15] M1, detect only

            // ---- 1. session reset -------------------------------------------------------------
            if (firstBar)
            {
                for (int k = 0; k < todKeys.Count; k++)
                {
                    List<double> lst;
                    if (!rngHist.TryGetValue(todKeys[k], out lst)) { lst = new List<double>(); rngHist[todKeys[k]] = lst; }
                    lst.Add(todRng[k]);
                    if (lst.Count > 200) lst.RemoveAt(0);
                }
                todKeys.Clear(); todRng.Clear();

                prevSessRet = (curSessOpen != 0.0 && !double.IsNaN(lagClose)) ? (lagClose - curSessOpen) : 0.0;
                curSessOpen = Open[0]; sessOpen = Open[0];
                haveSessHi = false; havePrevExtremes = false;
                cumDelta = 0.0; vwPv = 0.0; vwVv = 0.0;
                sessPnl = 0.0; sessStopped = false;
            }

            int hm  = pyTs.Hour * 10000 + pyTs.Minute * 100;
            int tod = pyTs.Hour * 60 + pyTs.Minute;
            double px = Close[0];

            // ---- 2. ratchet members ------------------------------------------------------------
            for (int m = 0; m < NMEMB; m++) mPos[m] = mPend[m];

            if (!double.IsNaN(prevClose))
            {
                double d = Math.Abs(px - prevClose);
                diffs.Enqueue(d); volSum += d;
                while (diffs.Count > VolPeriod) volSum -= diffs.Dequeue();
            }
            prevClose = px;

            for (int m = 0; m < NMEMB; m++)
            {
                mSig[m] = 0;
                if (!initialized) { mUp[m] = false; mAnchor[m] = px; mS[m] = ResolveS(VOLM[m]); continue; }
                if (mUp[m])
                {
                    if (px >= mAnchor[m]) mAnchor[m] = px;
                    else if (px < mAnchor[m] - mS[m])
                    { mUp[m] = false; mS[m] = ResolveS(VOLM[m]); mAnchor[m] = px; mSig[m] = -1; }
                }
                else
                {
                    if (px <= mAnchor[m]) mAnchor[m] = px;
                    else if (px > mAnchor[m] + mS[m])
                    { mUp[m] = true; mS[m] = ResolveS(VOLM[m]); mAnchor[m] = px; mSig[m] = 1; }
                }
            }
            if (!initialized) initialized = true;

            for (int m = 0; m < NMEMB; m++)
            {
                if (barCount < 20) { mPend[m] = mPos[m]; continue; }
                double xl = mUp[m] ? (mAnchor[m] - mS[m]) : (mAnchor[m] + mS[m]);
                if      (mPos[m] > 0 && px <= xl) mPend[m] = 0;
                else if (mPos[m] < 0 && px >= xl) mPend[m] = 0;
                else if (mPos[m] != 0)            mPend[m] = mPos[m];
                else                              mPend[m] = mSig[m];
            }

            // ---- 3. B-MOM -----------------------------------------------------------------------
            if (hm == 93100)
            {
                open0930 = Open[0]; bmVpv = 0.0; bmVv = 0.0; rthOpen = true;
                todaySlots.Clear(); bmom = 0;
            }
            if (rthOpen && hm >= 93100 && hm <= 160000)
            {
                bmVpv += px * Volume[0]; bmVv += Volume[0];
                double vw = (bmVv > 0) ? bmVpv / bmVv : px;
                todaySlots[hm] = Math.Abs(px - open0930);
                if (hm <= 155400 && rthDays >= BmomBandDays)
                {
                    List<double> past;
                    if (slotHist.TryGetValue(hm, out past) && past.Count > 0)
                    {
                        int kk = Math.Min(14, past.Count); double sum = 0.0;
                        for (int j = past.Count - kk; j < past.Count; j++) sum += past[j];
                        double mtod = sum / kk;
                        int s = 0;
                        if (px > Math.Max(open0930 + mtod, vw)) s = 1;
                        else if (px < Math.Min(open0930 - mtod, vw)) s = -1;
                        if (s != 0) bmom = s;
                    }
                }
                if (hm >= 155700 || lastBar) bmom = 0;
            }
            if (lastBar && rthOpen)
            {
                foreach (KeyValuePair<int, double> kv in todaySlots)
                {
                    List<double> lst;
                    if (!slotHist.TryGetValue(kv.Key, out lst)) { lst = new List<double>(); slotHist[kv.Key] = lst; }
                    lst.Add(kv.Value);
                    if (lst.Count > 60) lst.RemoveAt(0);
                }
                rthDays++; rthOpen = false;
            }

            // ---- 4. session end: zero members, update tilt ---------------------------------------
            if (lastBar)
            {
                for (int m = 0; m < NMEMB; m++) { mPos[m] = 0; mPend[m] = 0; }
                sessCloses.Add(px);
                if (sessCloses.Count > TiltSma)
                {
                    double sum = 0.0;
                    for (int j = sessCloses.Count - TiltSma; j < sessCloses.Count; j++) sum += sessCloses[j];
                    tilt = Math.Sign(px - sum / TiltSma);
                }
                if (sessCloses.Count > 600) sessCloses.RemoveAt(0);
            }

            // ---- 5. four combiners + hysteresis ---------------------------------------------------
            bool blocked   = pyTs >= sessionEndTs.AddMinutes(-EntryBlockMin);
            bool forceFlat = pyTs >= sessionEndTs.AddMinutes(-ForcedFlatMin);

            int nMemLong = 0;
            for (int s = 0; s < NSET; s++)
            {
                int len = SETLEN[s], sumNext = 0;
                for (int m = 0; m < len; m++) sumNext += mPend[m];
                int T = Math.Max(-10, Math.Min(10, RoundAway(sumNext / (double)len * 10.0)));
                double mm = (tilt != 0 && sumNext != 0 && Math.Sign(sumNext) == tilt) ? TiltMult : 1.0;
                int Tp = Math.Max(-13, Math.Min(13, RoundAway(T * mm * TiltRescale)));
                double M = WSolar * Tp + WBmom * bmom;

                int p = firstBar ? 0 : tgtPrev[s];
                int tgt = p;
                if (forceFlat) tgt = 0;
                else if (p == 0)
                {
                    if (!blocked)
                    {
                        if (M >= EntryLevel) tgt = 1;
                        else if (M <= -EntryLevel) tgt = -1;
                    }
                }
                else if (p > 0)
                {
                    if (M <= -EntryLevel && !blocked) tgt = -1;
                    else if (M <= ExitLevel) tgt = 0;
                }
                else
                {
                    if (M >= EntryLevel && !blocked) tgt = 1;
                    else if (M >= -ExitLevel) tgt = 0;
                }
                tgtPrev[s] = tgt;
                if (tgt > 0) nMemLong++;
            }

            // ---- 6. range throttle + delta gate ----------------------------------------------------
            double rngPrev = havePrevExtremes ? (sessHiPrev - sessLoPrev) : 0.0;
            double norm = 0.0; List<double> hist;
            if (rngHist.TryGetValue(tod, out hist) && hist.Count >= 20) norm = MedianLast(hist, 60);
            double ratio = (norm > 0) ? rngPrev / Math.Max(norm, 1e-9) : 1.0;

            int nThr = 1;                                    // the q = none voter always passes
            if (norm <= 0 || ratio >= 0.7) nThr++;
            if (norm <= 0 || ratio >= 0.8) nThr++;
            if (norm <= 0 || ratio >= 0.9) nThr++;

            int dL = (lagCumDelta >= 0) ? 1 : 0;

            bool voteOK = (nMemLong * nThr * (1 + dL)) >= 16;

            // ---- 7. causal quality size, computed only at a genuine entry --------------------------
            int size = 1; lastScore = 0;
            bool wantLong = voteOK && !(UseSessionBox && sessStopped);

            if (myQty == 0 && wantLong && UseQualitySize)
            {
                double atr = double.IsNaN(lagAtr) ? 1e-9 : Math.Max(lagAtr, 1e-9);
                double fDistOpen = (lagClose - sessOpen) / atr;
                double fPrevRet  = prevSessRet;
                double fRunLen   = lagRunLen;
                double fDistVwap = double.IsNaN(lagVwap) ? 0.0 : (lagClose - lagVwap) / atr;
                double fDeltaMag = Math.Abs(lagCumDelta) / Math.Max(lagVolNorm, 1e-9);

                if (qCount >= QualMinHist)
                {
                    int sc = 0;
                    if (fDistOpen >= Quantile(qDistOpen, QualWindow, 2.0 / 3.0)) sc++;
                    if (fPrevRet  <= Quantile(qPrevRet,  QualWindow, 1.0 / 3.0)) sc++;
                    if (fRunLen   >= Quantile(qRunLen,   QualWindow, 0.9))       sc++;
                    if (fDistVwap >= Quantile(qDistVwap, QualWindow, 2.0 / 3.0)) sc++;
                    if (fDeltaMag >= Quantile(qDeltaMag, QualWindow, 2.0 / 3.0)) sc++;
                    lastScore = sc; size = (sc >= 3) ? 2 : 1;
                }
                qDistOpen.Add(fDistOpen); qPrevRet.Add(fPrevRet); qRunLen.Add(fRunLen);
                qDistVwap.Add(fDistVwap); qDeltaMag.Add(fDeltaMag); qCount++;
            }

            // ---- 8. orders, mirrored by our own ledger --------------------------------------------
            if (lastBar && myQty > 0)
            {
                HdDiagRow("SESSFLAT", "closePx=" + Close[0] + ";myQty=" + myQty + ";myEntryPx=" + myEntryPx
                                    + ";sessPnl=" + sessPnl);   // [HD-13] M1
                // safety net: Python closes any open position at the session's last close
                ExitLong(myQty, "XLsess", "L");
                // W98 PER-CONTRACT BOX - the second accumulation site. Both must change together
                // or the box drifts between an intra-session exit and the session-close flatten.
                sessPnl += (Close[0] - myEntryPx) * Instrument.MasterInstrument.PointValue
                         - CommissionRT;
                myQty = 0; pendingAct = ACT_NONE;
            }
            else if (myQty > 0 && !wantLong)
            {
                ExitLong(myQty, "XL", "L"); pendingAct = ACT_EXIT;
            }
            else if (myQty == 0 && wantLong && pendingAct == ACT_NONE)
            {
                // [HD-04/06/07/11] THE ONLY GATE.  TRAP 1: gate the ORDER SITE, never wantLong -
                // wantLong is read at the EXIT branch above and gating the predicate would INVERT
                // the exit whenever the gate is shut.  TRAP 2: no accumulator write is gated; the
                // certified statement below is byte-identical and simply does not run when blocked.
                // M1: EntriesAllowed() is a constant true whenever State != State.Realtime.
                if (!EntriesAllowed()) { NoteBlockedEntry(); } else {
                pendingSize = size; EnterLong(size, "L"); pendingAct = ACT_ENTER;
                }
            }

            if (export != null)
            {
                export.WriteLine(string.Format(CultureInfo.InvariantCulture,
                    "{0:yyyy-MM-dd HH:mm:ss},{1},{2},{3},{4},{5:F4},{6},{7},{8},{9},{10:F2},{11}"
                    + ",{12},{13},{14},{15},{16},{17},{18},{19},{20:F4},{21:F4}",
                    pyTs, px, nMemLong, nThr, dL, ratio, voteOK ? 1 : 0, size, lastScore,
                    myQty, sessPnl, sessStopped ? 1 : 0,
                    tilt, bmom, tgtPrev[0], tgtPrev[1], tgtPrev[2], tgtPrev[3],
                    mSig[0], mPend[0], mAnchor[0], mS[0]));
            }

            barCount++;
            CacheLagged();
        }

        // Everything the NEXT bar's decision may see is frozen here, at THIS bar's close.
        private void CacheLagged()
        {
            double c = Close[0], h = High[0], l = Low[0];

            // this bar's contribution to the session's realised range, recorded for the NEXT bar
            if (!haveSessHi) { sessHiCur = h; sessLoCur = l; haveSessHi = true; }
            else { sessHiCur = Math.Max(sessHiCur, h); sessLoCur = Math.Min(sessLoCur, l); }

            todKeys.Add(Time[0].Hour * 60 + Time[0].Minute);
            todRng.Add(havePrevExtremes ? (sessHiPrev - sessLoPrev) : 0.0);
            sessHiPrev = sessHiCur; sessLoPrev = sessLoCur; havePrevExtremes = true;

            double tr = double.IsNaN(lagClose) ? (h - l)
                      : Math.Max(h - l, Math.Max(Math.Abs(h - lagClose), Math.Abs(l - lagClose)));
            trQ.Enqueue(tr); trSum += tr;
            while (trQ.Count > 14) trSum -= trQ.Dequeue();
            lagAtr = trSum / trQ.Count;

            int sgn = double.IsNaN(lagClose) ? 0 : Math.Sign(c - lagClose);
            cumDelta += sgn * Volume[0];
            lagCumDelta = cumDelta;

            if (sgn != 0 && sgn == lastSgn) runLen += 1;
            else if (sgn != 0) runLen = 1;
            else runLen = 0;
            lastSgn = sgn;
            lagRunLen = runLen * (sgn > 0 ? 1 : (sgn < 0 ? -1 : 0));

            vwPv += c * Volume[0]; vwVv += Volume[0];
            lagVwap = (vwVv > 0) ? vwPv / vwVv : double.NaN;

            volQ.Enqueue(Volume[0]); volSum240 += Volume[0];
            while (volQ.Count > 240) volSum240 -= volQ.Dequeue();
            lagVolNorm = (volQ.Count >= 30) ? volSum240 / volQ.Count : 1.0;

            lagClose = c;
        }
    }
}
