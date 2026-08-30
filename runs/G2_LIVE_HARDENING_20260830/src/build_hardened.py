# -*- coding: utf-8 -*-
"""
G2_LIVE_HARDENING_20260830 - BUILDER
Produces WeeklyEdgeP1PCT_v2.cs and WeeklyEdgeXMConflict_v3.cs from byte copies of the
certified sources by EXACT ANCHORED INSERTION.  Every certified line is preserved
byte-for-byte; only the class-name line and the Name= line are modified.
Certified sources are opened READ-ONLY and never written.
"""
import io, os, sys, hashlib, difflib

SRC = r"C:\Users\Yuke Zhang\Documents\NinjaTrader 8\bin\Custom\Strategies"
OUT = os.environ.get("HD_OUT", SRC)
RUN = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\runs\G2_LIVE_HARDENING_20260830"

# ============================================================================================
# helpers
# ============================================================================================
class Builder(object):
    """Works on a \\n-normalised copy; the file's original newline convention is restored on write.
    Certified lines therefore stay byte-identical."""
    def __init__(self, text):
        self.crlf = ("\r\n" in text)
        self.text = text.replace("\r\n", "\n")

    def _find_unique(self, anchor):
        n = self.text.count(anchor)
        if n != 1:
            raise SystemExit("ANCHOR NOT UNIQUE (%d hits): %r" % (n, anchor[:120]))
        return self.text.index(anchor)

    def insert_after(self, anchor, payload):
        i = self._find_unique(anchor)
        j = i + len(anchor)
        self.text = self.text[:j] + payload + self.text[j:]

    def insert_before(self, anchor, payload):
        i = self._find_unique(anchor)
        self.text = self.text[:i] + payload + self.text[i:]

    def replace_line(self, anchor, new):
        i = self._find_unique(anchor)
        self.text = self.text[:i] + new + self.text[i + len(anchor):]

    def prepend(self, payload):
        self.text = payload + self.text


def sha256(b):
    return hashlib.sha256(b).hexdigest()


# ============================================================================================
# SHARED HARDENING TEXT (parameterised per strategy)
# ============================================================================================

HEADER = """// =====================================================================================
// {NEW}  -  HARDENED SHADOW of the PARITY-CERTIFIED {OLD}.
//
// RUN runs/G2_LIVE_HARDENING_20260830/ - built to HARDENING_SPEC.md, 2026-08-30.
//
// STATUS: NOT CERTIFIED. NOT DEPLOYED. NOT ENABLED. A shadow, never a replacement.
//
// THE GOVERNING CONSTRAINT (spec 0): this file is the certified file PLUS additions.
// Every certified line below is BYTE-IDENTICAL to {OLD}.  The only
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
"""

# --------------------------------------------------------------------------------------------
# the hardening region: fields + methods.  {STRAT} substitutions differ P1 vs XM.
# --------------------------------------------------------------------------------------------
REGION_COMMON_FIELDS = """
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
"""

REGION_XM_EXTRA_FIELDS = """
        // ---- [HD-12] dead-secondary emergency flatten, submitted at most once
        private bool hdDeadFlattenSubmitted = false;
"""

REGION_LOGGING = """
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
"""

REGION_ORDER_CALLBACKS = """
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
"""

REGION_SETTLEMENT = """
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
"""

REGION_ROLL = """
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
"""

REGION_WARMUP_HEAD = """
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
"""

REGION_DIAG = """
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
                    + ",\\"" + (payload == null ? "" : payload.Replace("\\"", "'")) + "\\"");
                hdDiag.Flush();
            }
            catch (Exception) { }
        }

        private void HdCloseWriters()
        {
            if (hdDiag != null) { try { hdDiag.Flush(); hdDiag.Close(); } catch (Exception) { } hdDiag = null; }
        }
"""

# --------------------------------------------------------------------------------------------
# P1-SPECIFIC region parts
# --------------------------------------------------------------------------------------------
P1_REGION_SPECIFIC = """
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
"""

# --------------------------------------------------------------------------------------------
# XM-SPECIFIC region parts
# --------------------------------------------------------------------------------------------
XM_REGION_SPECIFIC = """
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
                if (myPos > 0) ExitLong(Qty, "XM_X", "XM_L"); else ExitShort(Qty, "XM_X", "XM_S");
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
"""

REGION_END = """
        // ==== [HD] END OF HARDENING REGION =======================================================
"""

# ============================================================================================
# STATE-CHANGE BLOCKS (shared shape)
# ============================================================================================
STATE_TRANSITION_REALTIME = """            // ---- [HD-07/08/14] added states.  NEITHER OCCURS IN A STRATEGY ANALYZER BACKTEST -
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
"""

# ============================================================================================
# BUILD P1
# ============================================================================================
def build_p1():
    src = os.path.join(SRC, "WeeklyEdgeP1PCT_v1.cs")
    raw = io.open(src, "rb").read()
    text = raw.decode("utf-8")
    b = Builder(text)

    b.prepend(HEADER.format(NEW="WeeklyEdgeP1PCT_v2", OLD="WeeklyEdgeP1PCT_v1"))

    # [M-1] class declaration
    b.replace_line("    public class WeeklyEdgeP1PCT_v1 : Strategy",
                   "    public class WeeklyEdgeP1PCT_v2 : Strategy")

    # [A-1] new inputs
    b.insert_after("        [NinjaScriptProperty] public string Tag            { get; set; }", """
        // ---- [HD] HARDENING INPUTS.  Every one defaults to an INERT value, so the historical
        //      path is unchanged and any deviation is recorded in DisplayParameters / GetStrategyState.
        [NinjaScriptProperty] public int    RollLeadDays     { get; set; }   // HD-06, 8
        [NinjaScriptProperty] public string WarmupCertDir    { get; set; }   // HD-08, "" = off
        [NinjaScriptProperty] public string DiagDir          { get; set; }   // HD-13, "" = off
        [NinjaScriptProperty] public bool   ExportStampUtc   { get; set; }   // HD-13, false = certified name
        [NinjaScriptProperty] public bool   TraceOrdersLive  { get; set; }   // HD-09, false = NT8 default
        [NinjaScriptProperty] public string ExpectInstrument { get; set; }   // HD-05, "" = check disabled""")

    # [A-2] hardening region
    region = (REGION_COMMON_FIELDS + REGION_LOGGING + REGION_ORDER_CALLBACKS
              + REGION_SETTLEMENT + REGION_ROLL + REGION_WARMUP_HEAD + REGION_DIAG
              + P1_REGION_SPECIFIC + REGION_END)
    b.insert_after("        private StreamWriter export = null;", region)

    # [M-2] Name
    b.replace_line('                Name = "WeeklyEdgeP1PCT_v1";',
                   '                Name = "WeeklyEdgeP1PCT_v2";')

    # [A-3] defaults + platform properties
    b.insert_after('                ExportDir = ""; Tag = "p1pct";', """
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
                ConnectionLossHandling      = ConnectionLossHandling.StopStrategy;    // CHANGE from Recalculate
                DisconnectDelaySeconds      = 10;                                     // install default, explicit
                NumberRestartAttempts       = 0;                                      // CHANGE from 4
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
                //   Calculate: DO NOT TOUCH.  Every one is part of the certified object.""")

    # [A-4] Configure branch (the certified P1 file has none)
    b.insert_before("            else if (State == State.DataLoaded)", """            // ---- [HD-09] TraceOrders routed through a property that defaults FALSE, so identity
            //      is free and the audit trail is available on a paper deployment.  M4 at default.
            else if (State == State.Configure)
            {
                TraceOrders = TraceOrdersLive;
            }
""")

    # [A-5] DataLoaded: config assert + instrument guard
    b.insert_after("                sessIter = new SessionIterator(Bars);", """
                HdConfigAssert();        // [HD-11] M4
                HdInstrumentGuard();     // [HD-05] M4, opt-in (ExpectInstrument defaults to "")""")

    # [A-6] ExportStampUtc wrap
    b.replace_line(
        '                        export = new StreamWriter(Path.Combine(ExportDir, "we_p1pct_" + Tag + ".csv"), false);',
        '''                        // [HD-13] ExportStampUtc defaults FALSE -> the certified filename is used
                        // and the parity harness gets the exact file it expects.  The certified
                        // statement below is byte-identical.
                        if (ExportStampUtc) { export = new StreamWriter(Path.Combine(ExportDir,
                            "we_p1pct_" + Tag + "_" + DateTime.UtcNow.ToString("yyyyMMdd_HHmmss") + "Z.csv"), false); } else {
                        export = new StreamWriter(Path.Combine(ExportDir, "we_p1pct_" + Tag + ".csv"), false);
                        }''')

    # [A-7] Transition / Realtime states
    b.insert_before("""            else if (State == State.Terminated)""", STATE_TRANSITION_REALTIME)

    # [A-8] Terminated: close hardening writers
    b.insert_after("                if (export != null) { try { export.Flush(); export.Close(); } catch (Exception) { } export = null; }",
                   "\n                HdCloseWriters();   // [HD-13]")

    # [A-9] realtime bar hook
    b.insert_after("            if (BarsInProgress != 0) return;",
                   "\n            HdRealtimeBarHook();   // [HD-06/07/13] M1: returns immediately unless State.Realtime\n")

    # [A-10] settlement capture
    b.insert_before("            // ---- 0. settle any order submitted on the previous bar; it filled at THIS open ----",
                    """            // [HD-03] copies taken BEFORE the certified settlement block, which is untouched.
            int hdAct0 = pendingAct, hdSize0 = pendingSize, hdQty0 = myQty;
""")

    # [A-11] settlement observer + reconciliation
    b.insert_after("            pendingAct = ACT_NONE;", """
            // [HD-03] observe what the certified block just ASSUMED, then [HD-04] reconcile the
            // ledger against NT8's strategy position and against the executions.  Both are M1.
            ObserveSettlement(hdAct0, (hdAct0 == ACT_ENTER) ? hdSize0 : hdQty0, Open[0]);
            AssertLedgerMatchesStrategyPosition(myQty);""")

    # [A-12] HD-15
    b.insert_after("""                sessionEndTs = sessIter.ActualSessionEnd;
            }""", "\n            HdSessionEndStaleCheck(pyTs, firstBar);   // [HD-15] M1, detect only")

    # [A-13] SESSFLAT diagnostic
    b.insert_after("""            if (lastBar && myQty > 0)
            {""", """
                HdDiagRow("SESSFLAT", "closePx=" + Close[0] + ";myQty=" + myQty + ";myEntryPx=" + myEntryPx
                                    + ";sessPnl=" + sessPnl);   // [HD-13] M1""")

    # [A-14] THE ENTRY GATE.  Certified line kept byte-identical; only wrapped.
    b.replace_line("""            else if (myQty == 0 && wantLong && pendingAct == ACT_NONE)
            {
                pendingSize = size; EnterLong(size, "L"); pendingAct = ACT_ENTER;
            }""", """            else if (myQty == 0 && wantLong && pendingAct == ACT_NONE)
            {
                // [HD-04/06/07/11] THE ONLY GATE.  TRAP 1: gate the ORDER SITE, never wantLong -
                // wantLong is read at the EXIT branch above and gating the predicate would INVERT
                // the exit whenever the gate is shut.  TRAP 2: no accumulator write is gated; the
                // certified statement below is byte-identical and simply does not run when blocked.
                // M1: EntriesAllowed() is a constant true whenever State != State.Realtime.
                if (!EntriesAllowed()) { NoteBlockedEntry(); } else {
                pendingSize = size; EnterLong(size, "L"); pendingAct = ACT_ENTER;
                }
            }""")

    return raw, b


# ============================================================================================
# BUILD XM
# ============================================================================================
def build_xm():
    src = os.path.join(SRC, "WeeklyEdgeXMConflict_v2.cs")
    raw = io.open(src, "rb").read()
    text = raw.decode("utf-8")
    b = Builder(text)

    b.prepend(HEADER.format(NEW="WeeklyEdgeXMConflict_v3", OLD="WeeklyEdgeXMConflict_v2"))

    b.replace_line("    public class WeeklyEdgeXMConflict_v2 : Strategy",
                   "    public class WeeklyEdgeXMConflict_v3 : Strategy")

    b.insert_after("        [NinjaScriptProperty] public string Tag               { get; set; }", """
        // ---- [HD] HARDENING INPUTS.  Every one defaults to an INERT value.
        [NinjaScriptProperty] public int    RollLeadDays                 { get; set; }   // HD-06, 8
        [NinjaScriptProperty] public string WarmupCertDir                { get; set; }   // HD-08, "" = off
        [NinjaScriptProperty] public string DiagDir                      { get; set; }   // HD-13, "" = off
        [NinjaScriptProperty] public bool   ExportStampUtc               { get; set; }   // HD-13, false
        [NinjaScriptProperty] public bool   TraceOrdersLive              { get; set; }   // HD-09, false
        [NinjaScriptProperty] public bool   EmergencyFlattenOnDeadSeries { get; set; }   // HD-12, true""")

    region = (REGION_COMMON_FIELDS + REGION_XM_EXTRA_FIELDS + REGION_LOGGING
              + REGION_ORDER_CALLBACKS + REGION_SETTLEMENT + REGION_ROLL
              + REGION_WARMUP_HEAD + REGION_DIAG + XM_REGION_SPECIFIC + REGION_END)
    b.insert_after("        private int lastConflict = 0, lastDesired = 0;", region)

    b.replace_line('                Name                      = "WeeklyEdgeXMConflict_v2";',
                   '                Name                      = "WeeklyEdgeXMConflict_v3";')

    b.insert_after('                Tag                = "xm2";', """
                // ---- [HD] hardening defaults.  All inert.  Tag is UNCHANGED so the per-bar export
                //      filename is identical between the certified and the hardened class.
                Description = Description + "  HARDENED SHADOW (G2_LIVE_HARDENING_20260830) - "
                            + "realtime reconciliation, warm-up assertion, roll block, FIXED "
                            + "instrument-month guard.  NOT CERTIFIED, NOT DEPLOYED.";
                RollLeadDays = 8; WarmupCertDir = ""; DiagDir = "";
                ExportStampUtc = false; TraceOrdersLive = false;
                EmergencyFlattenOnDeadSeries = true;   // inert: M1-gated

                // ---- [HD-09/HD-10] declared platform properties (spec 4).  M3.
                RealtimeErrorHandling       = RealtimeErrorHandling.StopCancelClose;  // NT8 default, explicit
                ConnectionLossHandling      = ConnectionLossHandling.StopStrategy;    // CHANGE from Recalculate
                DisconnectDelaySeconds      = 10;                                     // install default, explicit
                NumberRestartAttempts       = 0;                                      // CHANGE from 4
                StartBehavior               = StartBehavior.WaitUntilFlat;            // NT8 default, explicit
                IsAdoptAccountPositionAware = false;                                  // refuse to inherit
                IsUnmanaged                 = false;                                  // managed approach retained
                IgnoreOverfill              = false;                                  // NT8 handles overfills
                // RestartsWithinMinutes / SetOrderQuantity / MaximumBarsLookBack:
                //   DELIBERATELY NOT DECLARED - see WeeklyEdgeP1PCT_v2.cs and spec 4 for the reasons.""")

    # TraceOrders in the existing Configure branch
    b.insert_after("                AddDataSeries(YmInstrument,  BarsPeriodType.Minute, 1);",
                   "\n                TraceOrders = TraceOrdersLive;   // [HD-09] property defaults FALSE")

    # HD-05 hardened guard + HD-11, AFTER the untouched certified verification block
    b.insert_after("""                        { instrumentMismatch = true; break; }
                    }
                }""", """
                HdInstrumentGuard();     // [HD-05] the certified guard above is UNTOUCHED; this one
                                         //         adds the contract-month and cross-series clauses.
                HdConfigAssert();        // [HD-11] M4""")

    b.replace_line(
        '                        export = new StreamWriter(Path.Combine(ExportDir, "we_xm_" + Tag + ".csv"), false);',
        '''                        // [HD-13] ExportStampUtc defaults FALSE -> certified filename preserved.
                        if (ExportStampUtc) { export = new StreamWriter(Path.Combine(ExportDir,
                            "we_xm_" + Tag + "_" + DateTime.UtcNow.ToString("yyyyMMdd_HHmmss") + "Z.csv"), false); } else {
                        export = new StreamWriter(Path.Combine(ExportDir, "we_xm_" + Tag + ".csv"), false);
                        }''')

    b.insert_before("            else if (State == State.Terminated)", STATE_TRANSITION_REALTIME)

    b.insert_after("                if (export != null) { try { export.Flush(); export.Close(); } catch (Exception) {} export = null; }",
                   "\n                HdCloseWriters();   // [HD-13]")

    # HD-12 observer immediately BEFORE the untouched certified early return
    b.insert_after("            if (CurrentBars[NQ] < 1) return;",
                   "\n            HdDeadSeriesObserver();   // [HD-12] M1: runs BEFORE the certified return below\n")

    b.insert_after("            for (int i = 1; i < 4; i++) if (CurrentBars[i] < 1) return;",
                   "\n            HdRealtimeBarHook();      // [HD-06/07/13] M1\n")

    b.insert_before("            // ---- 0. settle whatever was submitted on the previous bar; it filled at THIS open",
                    """            // [HD-03] copies taken BEFORE the certified settlement block, which is untouched.
            int hdAct0 = pendingAct, hdQty0 = Math.Abs(myPos) * Qty;
""")

    b.insert_after("            pendingAct = ACT_NONE; pendingDir = 0;", """
            // [HD-03]/[HD-04], both M1.
            ObserveSettlement(hdAct0, (hdAct0 == ACT_ENTER) ? Qty : hdQty0, Opens[NQ][0]);
            AssertLedgerMatchesStrategyPosition(myPos * Qty);""")

    b.insert_after("""                lastConflict = 0; lastDesired = 0;
            }""", "\n            HdSessionEndStaleCheck(ts, firstBar);   // [HD-15] M1, detect only")

    b.insert_after("""            if (hm == AnchorHm && !anchorReady)
            {""", '\n                HdXmAgeRow("ANCHOR", ts);   // [HD-13] D1 measurement, M1')

    b.insert_after("""            if (hm == DecisionHm && anchorReady && !decisionReady && !sessionDisqualified)
            {""", '\n                HdXmAgeRow("DECISION", ts);   // [HD-13] D1 measurement, M1')

    b.replace_line("""                    if (lastDesired != 0 && myPos == 0 && !forceFlat && !instrumentMismatch)
                    {
                        if (lastDesired > 0) EnterLong(Qty, "XM_L"); else EnterShort(Qty, "XM_S");
                        pendingAct = ACT_ENTER; pendingDir = lastDesired;
                    }""", """                    if (lastDesired != 0 && myPos == 0 && !forceFlat && !instrumentMismatch)
                    {
                        // [HD-04/06/07/11] THE ONLY GATE.  TRAP 1: gate the ORDER SITE, never the
                        // predicate - the exit path at section 5 must never be affected.  The two
                        // certified statements below are byte-identical and simply do not run when
                        // blocked.  M1: EntriesAllowed() is a constant true outside State.Realtime.
                        if (!EntriesAllowed()) { NoteBlockedEntry(); } else {
                        if (lastDesired > 0) EnterLong(Qty, "XM_L"); else EnterShort(Qty, "XM_S");
                        pendingAct = ACT_ENTER; pendingDir = lastDesired;
                        }
                    }""")

    b.insert_after("""            if (myPos != 0 && pendingAct == ACT_NONE && (hm >= ExitHm || forceFlat || lastBar))
            {""", """
                HdDiagRow("SESSFLAT", "hm=" + hm + ";forceFlat=" + forceFlat + ";lastBar=" + lastBar
                                    + ";myPos=" + myPos + ";myEntryPx=" + myEntryPx);   // [HD-13] M1""")

    return raw, b


# ============================================================================================
def diffstat(old_text, new_text, label):
    o = old_text.splitlines()
    n = new_text.splitlines()
    sm = difflib.SequenceMatcher(None, o, n, autojunk=False)
    added = 0; removed = 0; changed = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "insert":  added += (j2 - j1)
        elif tag == "delete": removed += (i2 - i1)
        elif tag == "replace":
            changed += max(i2 - i1, j2 - j1)
    return dict(label=label, old_lines=len(o), new_lines=len(n),
                added=added, removed=removed, changed=changed)


def main():
    results = []
    for fn, outname in ((build_p1, "WeeklyEdgeP1PCT_v2.cs"),
                        (build_xm, "WeeklyEdgeXMConflict_v3.cs")):
        raw, b = fn()
        old_text = raw.decode("utf-8").replace("\r\n", "\n")
        new_text = b.text
        st = diffstat(old_text, new_text, outname)
        out_text = new_text.replace("\n", "\r\n") if b.crlf else new_text
        data = out_text.encode("utf-8")
        p = os.path.join(OUT, outname)
        f = open(p, "wb"); f.write(data); f.close()
        st["sha256"] = sha256(data)
        st["path"] = p
        st["bytes"] = len(data)
        results.append((st, old_text, new_text))

        # write the unified diff into the run directory for the record
        d = "\n".join(difflib.unified_diff(old_text.splitlines(), new_text.splitlines(),
                       fromfile="certified", tofile=outname, lineterm="", n=2))
        io.open(os.path.join(RUN, outname.replace(".cs", ".diff.txt")), "w",
                encoding="utf-8").write(d)

    for st, o, n in results:
        print(st["label"], "| old", st["old_lines"], "-> new", st["new_lines"],
              "| added", st["added"], "| changed", st["changed"], "| removed", st["removed"],
              "| sha256", st["sha256"])

if __name__ == "__main__":
    main()
