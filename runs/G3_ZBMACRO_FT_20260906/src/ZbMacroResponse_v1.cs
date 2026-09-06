// =====================================================================================
// ZbMacroResponse_v1  -  ZBMACRO01 macro-response engine, NinjaScript implementation.
//
// RUN runs/G3_ZBMACRO_FT_20260906/ (ledger G00083).  FT0 frozen by G00079:
//   On NFP_DAY / CPI_DAY sessions (GENESIS_H2_CALENDAR maintained as a calendar CSV):
//   if close(08:45) - close(08:30) < 0 (ZB points, bars END-stamped, ET),
//   SHORT KContracts (k=2) ZB, ledger fill at the CLOSE of the 08:46 bar;
//   EXIT buy at the 15:00 bar close.  No overnight.  No other conditions.
//
// STATUS: NOT COMPILED.  NOT CERTIFIED.  NOT DEPLOYED.  NOT ENABLED.
// 🔴 This file lives in the run directory ONLY.  Copying any .cs into
// Documents/NinjaTrader 8/** rebuilds Custom.dll against the RUNNING real-money book and
// is DEFERRED to the >= 2026-09-21 window (see DEPLOYMENT_PACKET.md).
//
// ARCHITECTURE (single-instrument, by design):
//   series 0 = ZB 1-minute Last.  Signal, fills and clock all on the SAME series.
//   There is no multi-series indexing surface, so the BarsInProgress-relative Position
//   trap (ghost-position postmortem 2026-09-03) cannot arise; Positions[0] is still used
//   explicitly, by convention, with two independent witnesses (see reconciliation).
//
// FILL CONVENTION (the executable claim, and how NT8 realizes it):
//   The signal is known at the close of the bar stamped 08:45.  The frozen object charges
//   one full minute of latency: the ledger books the entry at the CLOSE of the bar stamped
//   08:46.  Under Calculate.OnBarClose this class therefore submits the market order in the
//   OnBarUpdate of the 08:46 bar; NT8 fills it at the next bar's open, i.e. the first print
//   after the 08:46 close.  The ledger's assumed fill is Close[0] of the submit bar (the
//   research quantity); a realtime fill differing from it is logged (FILLPX), never halted
//   on price - exactly the certified P1 convention.  Same convention at the 15:00 exit.
//
// FAIL-CLOSED DOCTRINE (every path enumerated in the run's REPORT.md FT9 audit):
//   missing 08:30 or 08:45 bar        -> no signal, STAND ASIDE, loud log
//   missing 08:46 bar                 -> armed signal EXPIRES unfilled, STAND ASIDE, loud log
//   EARLY-CLOSE session (holiday half-day: template session end <= 15:00 ET)
//                                     -> STAND ASIDE, loud log.  The frozen object requires
//                                        a 15:00 exit; a session that cannot provide one is
//                                        outside the object.  (Measured: NFP on Good Friday
//                                        2026-04-03 is exactly this case - the research
//                                        universe excluded it, so entering would be a
//                                        DIFFERENT object AND an overnight-risk defect.)
//   calendar CSV missing/unparseable  -> zero event days = zero entries in EVERY state,
//                                        plus a realtime halt latch and a daily heartbeat
//   calendar CSV stale (no future ev) -> entries blocked, loud daily log
//   roll window                       -> entries blocked from MIN-over-series rollover
//   reject / cancel / partial fill    -> one-way halt latch
//   ledger vs strategy-position vs executions mismatch -> one-way halt latch
//   EXITS ARE NEVER GATED.  The 15:00 exit fires on the first bar stamped >= 15:00; if no
//   bar prints before session end, the last-bar flatten fail-safe fires (loud).
//
// ATTACH TO: ZB 1-minute Last, CBOT US Treasury futures ETH template,
// "NinjaTrader Brokerage Lifetime" commission, Standard fill, Calculate.OnBarClose.
// Export/diag/cert directories are NEW zbmacro paths - NEVER a \mnq\ directory.
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

namespace NinjaTrader.NinjaScript.Strategies
{
    public class ZbMacroResponse_v1 : Strategy
    {
        // ---- engine inputs ------------------------------------------------------------
        [NinjaScriptProperty] public int    KContracts       { get; set; }  // FT0: k=2
        [NinjaScriptProperty] public string CalendarCsvPath  { get; set; }  // REQUIRED, fail-closed
        [NinjaScriptProperty] public int    CalendarStaleDays{ get; set; }  // warn horizon, days
        // ---- hardening inputs (P1 conventions; every default is INERT) ----------------
        [NinjaScriptProperty] public string ExpectInstrument { get; set; }  // "" = check disabled
        [NinjaScriptProperty] public int    RollLeadDays     { get; set; }
        [NinjaScriptProperty] public string WarmupCertDir    { get; set; }  // "" = off
        [NinjaScriptProperty] public string DiagDir          { get; set; }  // "" = off
        [NinjaScriptProperty] public string ExportDir        { get; set; }  // "" = off
        [NinjaScriptProperty] public bool   TraceOrdersLive  { get; set; }
        [NinjaScriptProperty] public string Tag              { get; set; }

        // ---- calendar -----------------------------------------------------------------
        private HashSet<DateTime> calDates = new HashSet<DateTime>();  // session dates (ET)
        private DateTime calMaxDate  = DateTime.MinValue;
        private bool     calLoaded   = false;   // false => eventDay is false in EVERY state
        private bool     calStale    = false;   // realtime staleness latch (re-evaluated daily)
        private DateTime calHeartbeatFor = DateTime.MinValue;

        // ---- per-session decision state ----------------------------------------------
        private SessionIterator sessIter = null;
        private DateTime sessionEndTs = DateTime.MinValue;
        private bool     earlyClose  = false;   // template session end <= 15:00 ET
        private DateTime sessDate    = DateTime.MinValue;
        private bool     eventDay    = false;
        private double   px0830      = double.NaN;
        private double   px0845      = double.NaN;
        private bool     armedShort  = false;   // r1 < 0 seen at the 08:45 close
        private bool     entryDone   = false;   // one entry attempt per session, ever
        private bool     exitDone    = false;
        private bool     standAsideLogged = false;

        // ---- our own fill ledger (research quantity; fills booked at submit-bar close) -
        private const int ACT_NONE = 0, ACT_ENTER = 1, ACT_EXIT = 2;
        private int    pendingAct = ACT_NONE;
        private double myEntryPx  = 0.0;
        private int    myQty      = 0;          // signed: -KContracts when short
        private double lastAssumedPx = 0.0;

        // ---- [HD-01] shadow fill ledger, realtime only (two independent witnesses) ----
        private int        shFilled   = 0;
        private double     shAvgPx    = 0.0;
        private bool       shTerminal = false;
        private OrderState shState    = OrderState.Unknown;
        private ErrorCode  shError    = ErrorCode.NoError;
        private int        shNetQty   = 0;

        // ---- [HD-02/04] one-way halt latch.  DEFAULT: NOT BLOCKING. ------------------
        private bool   haltEntries          = false;
        private string haltReason           = "";
        private bool   firstRealtimeBarSeen = false;
        private bool   entriesBlockedUntilAgree = false;
        private string configFault          = null;
        private int    hdBlockedLoggedFor   = -1;

        // ---- [HD-06] roll awareness --------------------------------------------------
        private DateTime rollBlockFrom  = DateTime.MaxValue;
        private bool     rollResolved   = false;
        private DateTime rollAlertedFor = DateTime.MinValue;

        // ---- [HD-07/08] warm-up.  DEFAULT: NOT BLOCKING. -----------------------------
        private bool         warmupBlocked = false;
        private List<string> warmupRows    = new List<string>();
        private string       warmupVerdict = "GO";

        // ---- writers -----------------------------------------------------------------
        private StreamWriter export    = null;
        private StreamWriter hdDiag    = null;
        private string       hdDiagDay = "";

        // ============================================================================ logging
        private string HdPrefix() { return "[ZBM " + Name + " " + Tag + "] "; }
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
            if (State != State.Realtime) return;               // M1 + alert.htm semantics
            try
            {
                Alert("ZBM_" + Tag + "_" + id, Priority.High, msg, "", 30,
                      System.Windows.Media.Brushes.Firebrick, System.Windows.Media.Brushes.White);
            }
            catch (Exception) { }
        }

        /// <summary>One-way latch.  Blocks NEW ENTRIES ONLY - exits are never gated.</summary>
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

        /// <summary>THE GATE.  M1: constant true in any backtest.  Order-site only; the
        /// exit path never consults it.</summary>
        private bool EntriesAllowed()
        {
            if (State != State.Realtime) return true;          // M1
            if (haltEntries)              return false;
            if (warmupBlocked)            return false;
            if (entriesBlockedUntilAgree) return false;
            if (RollBlocked())            return false;
            if (!calLoaded)               return false;        // calendar missing = no object
            if (calStale)                 return false;        // calendar stale  = no object
            return true;
        }

        private void NoteBlockedEntry()
        {
            if (State != State.Realtime) return;               // M1
            if (hdBlockedLoggedFor == CurrentBar) return;
            hdBlockedLoggedFor = CurrentBar;
            string s = "ENTRY-BLOCKED halt=" + haltEntries + "(" + haltReason + ") warmup=" + warmupBlocked
                     + " carry=" + entriesBlockedUntilAgree + " roll=" + RollBlocked()
                     + " calLoaded=" + calLoaded + " calStale=" + calStale;
            LogWarn(s);
            HdDiagRow("BLOCKED", s);
        }

        // ---- order-name ownership.  This class submits exactly three signal names. ----
        private static bool IsMine(string n)
        { return n == "ZS" || n == "ZX" || n == "ZXsess"; }

        // ============================================================================ [HD-01]
        // Executions.  M1 first statement.  Match by execution.Name, never by Order/OrderId;
        // work only with the passed-by-value parameters; never read Position in a callback.
        // ============================================================================
        protected override void OnExecutionUpdate(Execution execution, string executionId, double price,
                int quantity, MarketPosition marketPosition, string orderId, DateTime time)
        {
            if (State != State.Realtime) return;               // M1
            if (execution == null || !IsMine(execution.Name)) return;
            int q = quantity; double p = price;
            shAvgPx  = (shFilled + q) > 0 ? (shAvgPx * shFilled + p * q) / (shFilled + q) : 0.0;
            shFilled += q;
            shNetQty += (marketPosition == MarketPosition.Long ? q : -q);
            HdDiagRow("EXEC", "name=" + execution.Name + ";q=" + q + ";px=" + p + ";mp=" + marketPosition
                            + ";cumFilled=" + shFilled + ";avgPx=" + shAvgPx + ";netQty=" + shNetQty);
        }

        // ============================================================================ [HD-02]
        // Order lifecycle.  M1 + M2.  Branch on order.OrderState (current), log both.
        // Rejected -> halt.  Cancelled -> halt (unfilled or partial).  Filled -> terminal.
        // PARTIAL FILL: latch, never adjust - the research object has no partial semantics.
        // ============================================================================
        protected override void OnOrderUpdate(Order order, double limitPrice, double stopPrice, int quantity,
                int filled, double averageFillPrice, OrderState orderState, DateTime time,
                ErrorCode error, string comment)
        {
            if (State != State.Realtime) return;               // M1
            if (order == null || !IsMine(order.Name)) return;
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
        }

        // [HD-13] position audit trail.  LOG ONLY - never drives logic.  M1.
        protected override void OnPositionUpdate(Position position, double averagePrice,
                int quantity, MarketPosition marketPosition)
        {
            if (State != State.Realtime) return;               // M1
            HdDiagRow("POS", "avgPx=" + averagePrice + ";qty=" + quantity + ";mp=" + marketPosition);
        }

        // ============================================================================ [HD-03]
        // Settlement observation at the ledger's booking point.  Quantity differences halt;
        // price differences are logged (FILLPX) - slippage vs the booked bar close is expected.
        // ============================================================================
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

        // ============================================================================ [HD-04]
        // The invariant: ledger vs NT8's STRATEGY position (Positions[0], stated explicitly -
        // never PositionAccount, which on account 2047681 also holds the P1 MNQ book and any
        // manual order).  Third witness: shNetQty from executions.  The transition-carry case
        // blocks entries until the two agree; every subsequent mismatch latches.  M1.
        // WHAT THIS GUARD CANNOT SEE (stated, clean-set rule): an owner/manual close of OUR
        // ZB position reaches neither Positions[0] promptly nor our executions filter; the
        // mismatch is caught at the NEXT bar's reconcile, not at the moment it happens.
        // ============================================================================
        private void AssertLedgerMatchesStrategyPosition(int ledgerQty)
        {
            if (State != State.Realtime) return;               // M1
            NinjaTrader.Cbi.Position p0 = Positions[0];
            int nt8 = (p0.MarketPosition == MarketPosition.Long)  ?  p0.Quantity
                    : (p0.MarketPosition == MarketPosition.Short) ? -p0.Quantity : 0;

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

        // ============================================================================ [HD-06]
        // Roll awareness.  MIN over ALL series (loop kept although this class is single-series:
        // the MX01 lesson is that the guard must survive a series being added later without
        // being rewritten).  Refuses NEW ENTRIES ONLY.  The strategy does NOT roll itself.
        // M1 twice: never called in a backtest; RollBlocked short-circuits on State.
        // ============================================================================
        private void ResolveRollDates(DateTime now)
        {
            if (State != State.Realtime || rollResolved) return;    // M1
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
            if (State != State.Realtime) return false;              // M1
            if (rollBlockFrom == DateTime.MaxValue) return false;
            return HdBarTime().Date >= rollBlockFrom.Date;
        }

        private DateTime HdBarTime()
        { try { return Time[0]; } catch (Exception) { return DateTime.MinValue; } }
        private string HdBarTimeString()
        { try { return Time[0].ToString("yyyy-MM-dd HH:mm:ss", CultureInfo.InvariantCulture); }
          catch (Exception) { return ""; } }

        // ============================================================================ CALENDAR
        // FAIL-CLOSED READER.  A missing/unparseable file leaves calLoaded=false, which makes
        // eventDay false in EVERY state (backtest included: no calendar -> no object -> no
        // trades, never a guess) and blocks realtime entries via EntriesAllowed.  Accepted
        // line format: leading YYYY-MM-DD (extra columns ignored); '#' comments; one header
        // line tolerated.  Dates are exchange-session dates (ET).
        // ============================================================================
        private void LoadCalendar()
        {
            calDates.Clear(); calLoaded = false; calMaxDate = DateTime.MinValue;
            if (string.IsNullOrEmpty(CalendarCsvPath) || !File.Exists(CalendarCsvPath))
            {
                LogErr("CAL-MISSING path='" + (CalendarCsvPath ?? "") + "' - ZERO event days; "
                     + "entries impossible in every state until the calendar exists");
                return;
            }
            try
            {
                foreach (string raw in File.ReadAllLines(CalendarCsvPath))
                {
                    if (raw == null) continue;
                    string s = raw.Trim();
                    if (s.Length < 10 || s.StartsWith("#")) continue;
                    DateTime d;
                    if (DateTime.TryParseExact(s.Substring(0, 10), "yyyy-MM-dd",
                            CultureInfo.InvariantCulture, DateTimeStyles.None, out d))
                    {
                        calDates.Add(d.Date);
                        if (d.Date > calMaxDate) calMaxDate = d.Date;
                    }
                }
                if (calDates.Count == 0)
                {
                    LogErr("CAL-EMPTY path='" + CalendarCsvPath + "' parsed 0 dates - fail-closed");
                    return;
                }
                calLoaded = true;
                LogInfo("CAL-LOADED rows=" + calDates.Count + " maxDate=" + calMaxDate.ToString("yyyy-MM-dd")
                      + " path='" + CalendarCsvPath + "'");
            }
            catch (Exception e)
            {
                calDates.Clear(); calLoaded = false;
                LogErr("CAL-READ-FAILED " + e.Message + " - fail-closed");
            }
        }

        // Realtime daily heartbeat: a fail-closed calendar is SILENTLY idle without one.
        // Stale = no calendar date on/after today -> entries blocked, loud.  M1.
        private void CalendarHeartbeat(DateTime barTs)
        {
            if (State != State.Realtime) return;               // M1
            if (calHeartbeatFor == barTs.Date) return;
            calHeartbeatFor = barTs.Date;

            if (!calLoaded) { LogErr("CAL-HEARTBEAT calendar NOT LOADED - entries impossible"); return; }
            calStale = calMaxDate < barTs.Date;
            DateTime next = DateTime.MaxValue;
            foreach (DateTime d in calDates) if (d >= barTs.Date && d < next) next = d;
            if (calStale)
                LogErr("CAL-STALE maxDate=" + calMaxDate.ToString("yyyy-MM-dd")
                     + " < today - ENTRIES BLOCKED until the calendar is extended");
            else if (calMaxDate < barTs.Date.AddDays(Math.Max(1, CalendarStaleDays)))
                LogWarn("CAL-LOW-RUNWAY maxDate=" + calMaxDate.ToString("yyyy-MM-dd")
                      + " within " + CalendarStaleDays + "d of today - extend the calendar CSV");
            else
                LogInfo("CAL-HEARTBEAT ok rows=" + calDates.Count
                      + " nextEvent=" + (next == DateTime.MaxValue ? "none" : next.ToString("yyyy-MM-dd"))
                      + " maxDate=" + calMaxDate.ToString("yyyy-MM-dd"));
        }

        // ============================================================================ [HD-13]
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
                    string p = Path.Combine(DiagDir, "zbm_" + Tag + "_hardening_" + day + "Z.csv");
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

        // ============================================================================ [HD-07/08]
        // Warm-up table + certificate.  This object has NO rolling accumulators: its only
        // dependencies are the calendar and the session's own 08:30/08:45/08:46 bars, so the
        // gates assert exactly those.  Program-printed, never hand-assembled.
        // ============================================================================
        private static string WarmRow(string gate, int spec, int min, int observed,
                                      ref bool nogo, ref bool degraded)
        {
            bool pass = observed >= spec;
            if (observed < min) nogo = true; else if (!pass) degraded = true;
            return gate + "," + spec + "," + min + "," + observed + ","
                 + (pass ? "PASS" : (observed >= min ? "DEGRADED" : "FAIL"));
        }

        private List<string> BuildWarmupTable()
        {
            List<string> rows = new List<string>();
            bool nogo = false, degraded = false;
            int futureEvents = 0;
            DateTime today = DateTime.Now.Date;
            foreach (DateTime d in calDates) if (d >= today) futureEvents++;
            rows.Add(WarmRow("calendar_loaded", 1,  1, calLoaded ? 1 : 0,  ref nogo, ref degraded));
            rows.Add(WarmRow("calendar_rows",   12, 1, calDates.Count,     ref nogo, ref degraded));
            rows.Add(WarmRow("calendar_future", 1,  1, futureEvents,       ref nogo, ref degraded));
            rows.Add(WarmRow("bars_count",      100, 1, Bars == null ? 0 : Bars.Count, ref nogo, ref degraded));
            warmupVerdict = nogo ? "NO-GO" : (degraded ? "DEGRADED" : "GO");
            return rows;
        }

        private void ReportWarmup(string phase)
        {
            string head = "WARMUP " + phase + " verdict=" + warmupVerdict + " blocked=" + warmupBlocked;
            if (warmupVerdict == "GO") LogInfo(head); else LogErr(head);
            LogInfo("WARMUP-GATE gate,spec,min,observed,pass");
            for (int i = 0; i < warmupRows.Count; i++) LogInfo("WARMUP-GATE " + warmupRows[i]);
            WriteWarmupCertificate(phase);
        }

        private void WriteWarmupCertificate(string phase)
        {
            if (string.IsNullOrEmpty(WarmupCertDir)) return;   // "" = off
            StreamWriter w = null;
            try
            {
                Directory.CreateDirectory(WarmupCertDir);
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
                r.Add("env,instrument," + (Instrument == null ? "?" : Instrument.FullName));
                r.Add("env,expiry," + (Instrument == null ? "?" : Instrument.Expiry.ToString("yyyy-MM-dd")));
                r.Add("env,point_value," + ((Instrument != null && Instrument.MasterInstrument != null)
                        ? Instrument.MasterInstrument.PointValue.ToString(CultureInfo.InvariantCulture) : "?"));
                r.Add("env,tick_size," + ((Instrument != null && Instrument.MasterInstrument != null)
                        ? Instrument.MasterInstrument.TickSize.ToString(CultureInfo.InvariantCulture) : "?"));
                r.Add("env,k_contracts," + KContracts);
                r.Add("env,calendar_path," + (CalendarCsvPath ?? ""));
                r.Add("env,calendar_rows," + calDates.Count);
                r.Add("env,calendar_max," + (calMaxDate == DateTime.MinValue ? "?" : calMaxDate.ToString("yyyy-MM-dd")));
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

        // ============================================================================ [HD-11]
        // Configuration self-assertion.  M4 at the certified configuration.
        // ============================================================================
        private void HdConfigAssert()
        {
            if (Calculate != Calculate.OnBarClose)   configFault = "Calculate=" + Calculate;
            else if (EntriesPerDirection != 1)       configFault = "EPD=" + EntriesPerDirection;
            else if (IsUnmanaged)                    configFault = "IsUnmanaged";
            else if (KContracts < 1)                 configFault = "KContracts=" + KContracts;
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

        // ============================================================================ [HD-05]
        // Instrument identity guard.  OPT-IN ("" = disabled); deployment sets "ZB 12-26".
        // A silently wrong contract (or the CASH 30Y, or a wrong root) halts before any order.
        // ============================================================================
        private static bool TryParseWanted(string want, out string root, out int mm, out int yy)
        {
            root = null; mm = 0; yy = 0;
            if (string.IsNullOrEmpty(want)) return false;
            string[] parts = want.Trim().Split(' ');
            if (parts.Length < 2) return false;
            root = parts[0];
            string[] my = parts[1].Split('-');
            if (my.Length != 2) return false;
            return int.TryParse(my[0], out mm) && int.TryParse(my[1], out yy) && mm >= 1 && mm <= 12;
        }

        private void HdInstrumentGuard()
        {
            if (string.IsNullOrEmpty(ExpectInstrument)) return;          // default = disabled
            string wRoot; int wMm, wYy;
            if (!TryParseWanted(ExpectInstrument, out wRoot, out wMm, out wYy))
            { Halt("ID unparseable ExpectInstrument='" + ExpectInstrument + "'"); return; }
            if (Instrument == null || Instrument.MasterInstrument == null)
            { Halt("ID primary unresolved"); return; }
            if (!string.Equals(Instrument.MasterInstrument.Name, wRoot, StringComparison.OrdinalIgnoreCase))
            { Halt("ID ROOT mismatch got=" + Instrument.MasterInstrument.Name + " want=" + wRoot); return; }
            DateTime ex = Instrument.Expiry;
            if (ex.Month != wMm || (ex.Year % 100) != wYy)
            { Halt("ID MONTH mismatch instrument=" + Instrument.FullName
                 + " expiry=" + ex.ToString("yyyy-MM-dd") + " want=" + ExpectInstrument); return; }
            LogInfo("ID OK instrument=" + Instrument.FullName
                  + " expiry=" + ex.ToString("yyyy-MM-dd") + " want=" + ExpectInstrument);
        }

        // ============================================================================ states
        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = "ZBMACRO01 (G00079 FT0): NFP/CPI 08:30-release response. "
                            + "r1=close(08:45)-close(08:30)<0 -> SHORT k ZB at the 08:46 close, "
                            + "exit at the 15:00 close.  Fail-closed on missing bars and calendar. "
                            + "NOT CERTIFIED, NOT DEPLOYED (run G3_ZBMACRO_FT_20260906).";
                Name = "ZbMacroResponse_v1";
                Calculate = Calculate.OnBarClose;
                EntriesPerDirection = 1;
                EntryHandling = EntryHandling.AllEntries;
                IsExitOnSessionCloseStrategy = false;   // the 15:00 exit is OURS; flatten fail-safe below
                IncludeCommission = true;
                BarsRequiredToTrade = 20;

                KContracts = 2;                          // FT0: k=2 (G00078 decision cell)
                CalendarCsvPath = "";                    // REQUIRED at deploy; "" fails closed
                CalendarStaleDays = 40;
                ExpectInstrument = "";                   // deploy sets "ZB 12-26"
                RollLeadDays = 8;
                WarmupCertDir = ""; DiagDir = ""; ExportDir = "";
                TraceOrdersLive = false;
                Tag = "zbmacro";

                // [HD-09/10] platform properties, declared explicitly (all NT8 defaults).
                RealtimeErrorHandling       = RealtimeErrorHandling.StopCancelClose;
                DisconnectDelaySeconds      = 10;
                StartBehavior               = StartBehavior.WaitUntilFlat;
                IsAdoptAccountPositionAware = false;     // refuse to inherit any account position
                IsUnmanaged                 = false;
                IgnoreOverfill              = false;
            }
            else if (State == State.Configure)
            {
                TraceOrders = TraceOrdersLive;
            }
            else if (State == State.DataLoaded)
            {
                sessIter = new SessionIterator(Bars);
                HdConfigAssert();        // [HD-11]
                HdInstrumentGuard();     // [HD-05] opt-in
                LoadCalendar();          // fail-closed reader
                if (!string.IsNullOrEmpty(ExportDir))
                {
                    try
                    {
                        Directory.CreateDirectory(ExportDir);
                        export = new StreamWriter(Path.Combine(ExportDir, "zbm_" + Tag + ".csv"), false);
                        export.WriteLine("ts,close,sess,event,px0830,px0845,r1,armed,qty,entryPx,exitDone");
                    }
                    catch (Exception e) { export = null; LogErr("EXPORT-OPEN-FAILED " + e.Message); }
                }
            }
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
                if (export != null) { try { export.AutoFlush = true; } catch (Exception) { } }   // [HD-16]
                HdLogTemplate();
                if (haltEntries) LogErr("ENTRIES LATCHED OFF AT START: " + haltReason);
            }
            else if (State == State.Terminated)
            {
                if (export != null) { try { export.Flush(); export.Close(); } catch (Exception) { } export = null; }
                HdCloseWriters();
            }
        }

        // ============================================================================ bars
        protected override void OnBarUpdate()
        {
            if (BarsInProgress != 0) return;               // single-series; explicit anyway
            if (State == State.Realtime) ResolveRollDates(HdBarTime());   // [HD-06] M1
            if (State == State.Realtime && warmupBlocked)
            {
                warmupRows = BuildWarmupTable();
                if (warmupVerdict == "GO") { warmupBlocked = false; ReportWarmup("REARM"); }
            }

            DateTime ts = Time[0];                          // END-stamped, ET session clock
            bool lastBar = Bars.IsLastBarOfSession;

            // ---- 0. settle the order booked on the previous bar (shadow-witness check) --
            int hdAct0 = pendingAct;
            if (pendingAct != ACT_NONE) { ObserveSettlement(hdAct0, KContracts, lastAssumedPx); }
            pendingAct = ACT_NONE;
            AssertLedgerMatchesStrategyPosition(myQty);     // [HD-04]

            // ---- 1. session bookkeeping (18:00 ET boundary; bar stamped >=18:00 is next day) --
            DateTime d = (ts.Hour >= 18) ? ts.Date.AddDays(1) : ts.Date;
            if (d != sessDate)
            {
                // FLATTEN FAIL-SAFE #2: a new session beginning while short means the previous
                // session never printed a bar >= 15:00 AND its last bar was missed - forbidden
                // overnight state.  Exit immediately and latch (this is a defect, not a trade).
                if (myQty < 0)
                {
                    LogErr("OVERNIGHT-CARRY-DETECTED qty=" + myQty + " - flattening NOW");
                    ExitShort(Math.Abs(myQty), "ZXsess", "ZS");
                    myQty = 0; pendingAct = ACT_NONE; exitDone = true;
                    Halt("OVERNIGHT-CARRY");
                }
                sessDate = d;
                eventDay = calLoaded && calDates.Contains(d);
                px0830 = double.NaN; px0845 = double.NaN;
                armedShort = false; entryDone = false; exitDone = false; standAsideLogged = false;

                // EARLY-CLOSE GUARD (fail-closed, from the TEMPLATE, known before any entry):
                // the frozen object exits at the 15:00 close; a session whose template end is
                // at or before 15:00 ET cannot provide that exit and is OUTSIDE the object.
                earlyClose = false;
                try
                {
                    sessIter.GetNextSession(ts, true);
                    sessionEndTs = sessIter.ActualSessionEnd;
                    earlyClose = sessionEndTs <= d.AddHours(15);
                }
                catch (Exception e)
                {   // no template answer -> assume the worst: fail closed
                    earlyClose = true;
                    LogErr("SESSION-END-UNRESOLVED " + e.Message + " - treating as EARLY-CLOSE");
                }
                if (eventDay && earlyClose)
                    LogWarn("EARLY-CLOSE event day " + d.ToString("yyyy-MM-dd") + " sessionEnd="
                          + sessionEndTs.ToString("yyyy-MM-dd HH:mm") + " <= 15:00 - STAND ASIDE");
            }
            CalendarHeartbeat(ts);                          // M1: realtime staleness + heartbeat

            int hm = ts.Hour * 100 + ts.Minute;

            // ---- 2. exact-stamp captures + signal (bars END-stamped: 08:45 bar = 08:44->08:45) --
            if (hm == 830) px0830 = Close[0];
            if (hm == 845)
            {
                px0845 = Close[0];
                if (eventDay && !earlyClose)
                {
                    if (double.IsNaN(px0830))
                    {   // FAIL-CLOSED: missing 08:30 bar -> no signal, stand aside, loud
                        standAsideLogged = true;
                        LogWarn("NO-0830-BAR event day " + d.ToString("yyyy-MM-dd") + " - STAND ASIDE");
                    }
                    else if (px0845 - px0830 < 0)
                    {
                        armedShort = true;
                        LogInfo("SIGNAL r1=" + (px0845 - px0830).ToString("F5", CultureInfo.InvariantCulture)
                              + " < 0 on " + d.ToString("yyyy-MM-dd") + " - SHORT armed for the 08:46 close");
                    }
                }
            }
            if (eventDay && hm > 845 && double.IsNaN(px0845) && !armedShort && !standAsideLogged)
            {   // FAIL-CLOSED: missing 08:45 bar -> the signal cannot exist, stand aside, loud
                standAsideLogged = true;
                LogWarn("NO-0845-BAR event day " + d.ToString("yyyy-MM-dd") + " - STAND ASIDE");
            }

            // ---- 3. entry: ONLY at the bar stamped exactly 08:46 ------------------------
            if (armedShort && !entryDone)
            {
                if (hm == 846)
                {
                    entryDone = true;
                    // THE ONLY ENTRY GATE - order site, never the predicate.  M1 in backtest.
                    if (!EntriesAllowed()) { NoteBlockedEntry(); }
                    else
                    {
                        EnterShort(KContracts, "ZS");
                        myEntryPx = Close[0]; myQty = -KContracts;   // ledger books the 08:46 close
                        lastAssumedPx = Close[0]; pendingAct = ACT_ENTER;
                    }
                }
                else if (hm > 846)
                {   // FAIL-CLOSED: the 08:46 bar never printed -> the armed signal EXPIRES
                    entryDone = true; armedShort = false;
                    LogWarn("NO-0846-BAR event day " + d.ToString("yyyy-MM-dd")
                          + " - armed signal expired UNFILLED, STAND ASIDE");
                }
            }

            // ---- 4. exit: first bar stamped >= 15:00.  NEVER GATED. ---------------------
            if (myQty < 0 && !exitDone && hm >= 1500 && hm < 1800)
            {
                if (hm > 1500)
                    LogWarn("EXIT-SLIP no 15:00 bar printed; exiting on the " + hm + " bar (fail-safe)");
                ExitShort(Math.Abs(myQty), "ZX", "ZS");
                lastAssumedPx = Close[0]; pendingAct = ACT_EXIT;     // ledger books this bar's close
                myQty = 0; exitDone = true;
            }

            // ---- 5. flatten fail-safe #1: session's last bar, still short ---------------
            if (lastBar && myQty < 0)
            {
                LogErr("FLATTEN-FAILSAFE last bar of session still short - flattening at close");
                ExitShort(Math.Abs(myQty), "ZXsess", "ZS");
                lastAssumedPx = Close[0]; pendingAct = ACT_EXIT;
                myQty = 0; exitDone = true;
            }

            // ---- 6. per-bar decision export (parity surface) ----------------------------
            if (export != null)
            {
                export.WriteLine(string.Format(CultureInfo.InvariantCulture,
                    "{0:yyyy-MM-dd HH:mm:ss},{1},{2:yyyy-MM-dd},{3},{4},{5},{6},{7},{8},{9},{10}",
                    ts, Close[0], sessDate, eventDay ? 1 : 0,
                    double.IsNaN(px0830) ? "" : px0830.ToString(CultureInfo.InvariantCulture),
                    double.IsNaN(px0845) ? "" : px0845.ToString(CultureInfo.InvariantCulture),
                    (double.IsNaN(px0830) || double.IsNaN(px0845)) ? ""
                        : (px0845 - px0830).ToString(CultureInfo.InvariantCulture),
                    armedShort ? 1 : 0, myQty,
                    myQty < 0 ? myEntryPx.ToString(CultureInfo.InvariantCulture) : "",
                    exitDone ? 1 : 0));
            }
        }
    }
}
