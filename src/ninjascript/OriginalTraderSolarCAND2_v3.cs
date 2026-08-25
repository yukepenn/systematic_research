#region Using declarations
using System;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
#endregion

// OriginalTraderSolarCAND2_v3 — NinjaScript port of OTR-S-CAND2 (directive v3.0 §7),
// the verified model class reconstructing the original trader's early flagship
// (research/original_trader_reconstruction/solar_family/TRACK_S_REPORT.md,
//  runs/OTR_R1_SERIES + runs/OTR_R5_CAND2_WEEKLY_VALIDATION).
//
// Signal engine: recovered Solar core (T1 flips only; no vendor dependency).
// Wrapper (identified components):
//   B1  first-bar-of-session signal drop (matches trader's visible code)
//   T1  stop-and-reverse chains; exit comparison switchable INCLUSIVE/STRICT
//   v3 adds StrictExit: Close < TS instead of Close <= TS. Given the Solar ladder
//   recurrence the two differ ONLY on bars where Close == anchor -/+ S exactly,
//   so STRICT is equivalent to 'exit only on a genuine trend flip'.
//   D   session-equity gate: (a) prior-session net <= -C -> no entries for the
//       first EveningBlockMinutes of the session; (b) armed once session equity
//       high-water >= X (>= X2 before NoonMinute): cum < 0 blocks all entries,
//       K consecutive same-side losses blocks that side; (c) SessionTradeCap on
//       COMPLETED trades; (d) CooldownBars re-entry cooldown after any exit.
//   St  optional intrabar initial protective stop (65 pts era: Jul-2025+;
//       leave OFF for the 2023-2025 master era).
//   R   optional resume latch (second-breakdown crossing of a static level,
//       armed on evenings after early-close sessions) — OFF by default;
//       reference level interval-identified only.
//
// UNKNOWN-CONSTANT WARNING: GateX / GateX2 / GateC are INTERVAL-IDENTIFIED
// (X in [1425,1925]); K=3-consecutive has an equally label-consistent rival
// (4 TOTAL same-side losses). Exposed for forensic testing only — do NOT tune.
//
// NT8-vs-Python semantics note: the Python reference evaluates the gate at the
// FILL bar with the same-bar exit realized first. OnBarClose NT8 cannot do that
// for reversals (the exit fill price is unknown at decision time), so this port
// projects the in-flight trade's PnL with Close[0] as the exit proxy (actual
// fill is next open) and uses decision-bar time for the noon/evening clocks.
// Divergence is bounded to threshold-boundary bars and is MEASURED in the
// parity run (see PARITY_PROTOCOL), not assumed zero. If material, the finding
// is that the trader's own code used decision-close semantics too.
//
// Wrapper session bookkeeping is maintained in OnBarUpdate mirroring the Python
// automaton (fills at next open / stop level / session close at last-bar close),
// independent of NT8 execution events, so gate state cannot desync on
// execution-report quirks. NT8's own trade reporting is untouched.
//
// RESEARCH ONLY: historical Strategy Analyzer use; fails closed in realtime.
namespace NinjaTrader.NinjaScript.Strategies
{
    public class OriginalTraderSolarCAND2_v3 : Strategy
    {
        // Solar core state
        private double anchor;
        private bool   isUp;
        private bool   weak;
        private int    barsSinceExtreme;
        private int    nextWeakBar;
        private bool   initialized;
        private double trailingStopVal;
        private int    signalTradeVal;

        // pending-fill mirror of the reference engine (decided last close, fills this open)
        private const int PEND_NONE = 0, PEND_EXIT = 1, PEND_REV = 2, PEND_ENTRY = 3;
        private int    pendKind;
        private int    pendDir;

        // wrapper session state (own bookkeeping, comm 0)
        private int    posDir;
        private double entryPx;
        private double sessCum;
        private double sessHigh;
        private double priorSessNet;
        private int    consecLossLong;
        private int    consecLossShort;
        private int    tradesThisSession;      // COMPLETED trades (Python n_sess)
        private int    lastExitBar;
        private DateTime sessionFirstBarTime;

        // resume latch state
        private bool   priorSessionEarlyClose;
        private bool   flippedThisSession;
        private bool   wasBelowResumeLevel;
        private int    breakdownCrossings;

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = "OTR-S-CAND2: identified early-flagship reconstruction (research only)";
                Name        = "OriginalTraderSolarCAND2_v3";

                Calculate               = Calculate.OnBarClose;
                EntriesPerDirection     = 1;
                EntryHandling           = EntryHandling.AllEntries;
                DefaultQuantity         = 1;

                IsExitOnSessionCloseStrategy = true;
                ExitOnSessionCloseSeconds    = 30;

                StrictExit            = false;
                BarsRequiredToTrade   = 20;
                MaximumBarsLookBack   = MaximumBarsLookBack.TwoHundredFiftySix;
                OrderFillResolution   = OrderFillResolution.Standard;
                Slippage              = 0;
                StartBehavior         = StartBehavior.WaitUntilFlat;
                TimeInForce           = TimeInForce.Gtc;
                RealtimeErrorHandling = RealtimeErrorHandling.StopCancelClose;

                TrendMultiplier = 90;
                StopMultiplier  = 179;
                SlowdownScan    = 5;
                WeakWeakSplit   = 10;
                StartUp         = false;

                GateX               = 1600;
                GateX2              = 2500;
                GateK               = 3;
                GateC               = 700;
                NoonMinute          = 720;
                EveningBlockMinutes = 360;
                SessionTradeCap     = 20;
                CooldownBars        = 3;

                UseInitialStop = false;
                StopPoints     = 65;

                UseResumeLatch = false;
                ResumeLevel    = 0;
            }
            else if (State == State.DataLoaded)
            {
                initialized = false;
                pendKind = PEND_NONE; pendDir = 0;
                posDir = 0; entryPx = 0;
                sessCum = 0; sessHigh = 0; priorSessNet = 0;
                consecLossLong = 0; consecLossShort = 0;
                tradesThisSession = 0; lastExitBar = -100000;
                sessionFirstBarTime = DateTime.MinValue;
                priorSessionEarlyClose = false; flippedThisSession = false;
                wasBelowResumeLevel = false; breakdownCrossings = 0;
            }
            else if (State == State.Realtime)
            {
                Log("OriginalTraderSolarCAND2_v3 is research-only; disabling.", LogLevel.Error);
                SetState(State.Terminated);
            }
        }

        private void UpdateSolarWave()
        {
            double S  = StopMultiplier * TickSize;
            double px = Close[0];
            signalTradeVal = 0;
            int ev = 0;

            if (!initialized)
            {
                initialized = true;
                isUp = StartUp; anchor = px;
                weak = false; barsSinceExtreme = 0; nextWeakBar = int.MinValue;
            }
            else
            {
                if (isUp)
                {
                    if (px >= anchor) { if (px > anchor) ev = 1; anchor = px; }
                    else if (px < anchor - S) { isUp = false; anchor = px; ev = 2; }  // STRICT
                }
                else
                {
                    if (px <= anchor) { if (px < anchor) ev = 1; anchor = px; }
                    else if (px > anchor + S) { isUp = true; anchor = px; ev = 2; }   // STRICT
                }
            }

            if (ev == 2)
            {
                weak = false; barsSinceExtreme = 0;
                signalTradeVal = isUp ? 1 : -1;
                nextWeakBar = CurrentBar + WeakWeakSplit;
                flippedThisSession = true;
            }
            else if (ev == 1)
            {
                barsSinceExtreme = 0;
                if (weak) { weak = false; nextWeakBar = CurrentBar + WeakWeakSplit; }
            }
            else
            {
                barsSinceExtreme++;
                if (!weak && barsSinceExtreme >= SlowdownScan && CurrentBar >= nextWeakBar)
                {
                    weak = true; nextWeakBar = CurrentBar + WeakWeakSplit;
                }
            }

            trailingStopVal = isUp ? anchor - S : anchor + S;
        }

        private void RealizeExit(double price)
        {
            if (posDir == 0) return;
            double pnl = posDir * (price - entryPx) * Instrument.MasterInstrument.PointValue;
            sessCum += pnl;
            if (sessCum > sessHigh) sessHigh = sessCum;
            if (pnl <= 0) { if (posDir > 0) consecLossLong++; else consecLossShort++; }
            else          { if (posDir > 0) consecLossLong = 0; else consecLossShort = 0; }
            tradesThisSession++;
            lastExitBar = CurrentBar;
            posDir = 0;
        }

        private bool GateAllows(int dir, double projCum, double projHigh, int projTrades,
                                int projConsecL, int projConsecS, int minuteOfDay, int minutesFromOpen)
        {
            if (priorSessNet <= -GateC && minutesFromOpen <= EveningBlockMinutes)
                return false;
            if (projTrades >= SessionTradeCap)
                return false;
            double thr = minuteOfDay >= NoonMinute ? GateX : GateX2;
            if (projHigh >= thr)
            {
                if (projCum < 0) return false;
                int cs = dir > 0 ? projConsecL : projConsecS;
                if (cs >= GateK) return false;
            }
            return true;
        }

        protected override void OnBarUpdate()
        {
            if (BarsInProgress != 0)
                return;

            // ---- session boundary: reset wrapper state (before anything else) ----
            if (Bars.IsFirstBarOfSession)
            {
                pendKind = PEND_NONE; pendDir = 0;      // last-bar decisions never carry over
                priorSessNet = sessCum;
                sessCum = 0; sessHigh = 0;
                consecLossLong = 0; consecLossShort = 0;
                tradesThisSession = 0;
                sessionFirstBarTime = Time[0];
                priorSessionEarlyClose = CurrentBar > 0 && Time[1].Hour < 16;
                flippedThisSession = false;
                wasBelowResumeLevel = false; breakdownCrossings = 0;
            }

            // ---- bookkeeping: pending decisions from last close fill at this open ----
            if (pendKind == PEND_EXIT)
            {
                RealizeExit(Open[0]);
                pendKind = PEND_NONE;
            }
            else if (pendKind == PEND_REV)
            {
                RealizeExit(Open[0]);
                posDir = pendDir; entryPx = Open[0];
                pendKind = PEND_NONE;
            }
            else if (pendKind == PEND_ENTRY)
            {
                posDir = pendDir; entryPx = Open[0];
                pendKind = PEND_NONE;
            }

            UpdateSolarWave();

            // ---- bookkeeping: intrabar initial stop (mirror of NT8 SetStopLoss fill) ----
            if (posDir != 0 && UseInitialStop)
            {
                double lvl = entryPx - posDir * StopPoints;
                bool hit = posDir > 0 ? Low[0] <= lvl : High[0] >= lvl;
                if (hit)
                {
                    bool gapped = posDir > 0 ? Open[0] <= lvl : Open[0] >= lvl;
                    RealizeExit(gapped ? Open[0] : lvl);
                }
            }

            // ---- session close: realize at last-bar close, no decisions ----
            if (Bars.IsLastBarOfSession)
            {
                if (posDir != 0)
                    RealizeExit(Close[0]);
                pendKind = PEND_NONE;
                return;                          // NT8 ExitOnSessionClose does the real flatten
            }

            if (Bars.IsFirstBarOfSession)        // B1: no decisions on the first bar
                return;
            if (CurrentBar < BarsRequiredToTrade)
                return;

            int sig = signalTradeVal;
            int minuteOfDay = Time[0].Hour * 60 + Time[0].Minute;
            int minutesFromOpen = (int)(Time[0] - sessionFirstBarTime).TotalMinutes;
            double pv = Instrument.MasterInstrument.PointValue;

            // ---- holding: inclusive TS-touch exit / stop-and-reverse ----
            bool tsHitLong  = StrictExit ? Close[0] < trailingStopVal : Close[0] <= trailingStopVal;
            bool tsHitShort = StrictExit ? Close[0] > trailingStopVal : Close[0] >= trailingStopVal;
            if (Position.MarketPosition == MarketPosition.Long && tsHitLong)
            {
                bool reverse = false;
                if (sig == -1)
                {
                    double projPnl = (Close[0] - entryPx) * pv;
                    double pc = sessCum + projPnl;
                    double ph = Math.Max(sessHigh, pc);
                    reverse = GateAllows(-1, pc, ph, tradesThisSession + 1,
                        projPnl <= 0 ? consecLossLong + 1 : 0, consecLossShort,
                        minuteOfDay, minutesFromOpen);
                }
                if (reverse) { EnterShort(DefaultQuantity, "Short"); pendKind = PEND_REV; pendDir = -1; }
                else         { ExitLong("L-SolarExit", "Long");      pendKind = PEND_EXIT; }
                return;
            }
            if (Position.MarketPosition == MarketPosition.Short && tsHitShort)
            {
                bool reverse = false;
                if (sig == 1)
                {
                    double projPnl = (entryPx - Close[0]) * pv;
                    double pc = sessCum + projPnl;
                    double ph = Math.Max(sessHigh, pc);
                    reverse = GateAllows(1, pc, ph, tradesThisSession + 1,
                        consecLossLong, projPnl <= 0 ? consecLossShort + 1 : 0,
                        minuteOfDay, minutesFromOpen);
                }
                if (reverse) { EnterLong(DefaultQuantity, "Long"); pendKind = PEND_REV; pendDir = 1; }
                else         { ExitShort("S-SolarExit", "Short");  pendKind = PEND_EXIT; }
                return;
            }

            if (Position.MarketPosition != MarketPosition.Flat || posDir != 0 || pendKind != PEND_NONE)
                return;

            bool cooldownOk = CurrentBar - lastExitBar >= CooldownBars;

            // ---- optional resume latch: second breakdown crossing of a static level ----
            if (UseResumeLatch && ResumeLevel > 0 && priorSessionEarlyClose && !flippedThisSession)
            {
                bool below = Close[0] < ResumeLevel;
                if (below && !wasBelowResumeLevel)
                {
                    breakdownCrossings++;
                    if (breakdownCrossings == 2 && cooldownOk &&
                        GateAllows(-1, sessCum, sessHigh, tradesThisSession,
                                   consecLossLong, consecLossShort, minuteOfDay, minutesFromOpen))
                    {
                        SetInitialStopIfEnabled("Short");
                        EnterShort(DefaultQuantity, "Short");
                        pendKind = PEND_ENTRY; pendDir = -1;
                        return;
                    }
                }
                wasBelowResumeLevel = below;
            }

            // ---- flat: T1 entries under gate + cooldown ----
            if (sig == 0 || !cooldownOk)
                return;
            if (!GateAllows(sig, sessCum, sessHigh, tradesThisSession,
                            consecLossLong, consecLossShort, minuteOfDay, minutesFromOpen))
                return;

            if (sig > 0)
            {
                SetInitialStopIfEnabled("Long");
                EnterLong(DefaultQuantity, "Long");
                pendKind = PEND_ENTRY; pendDir = 1;
            }
            else
            {
                SetInitialStopIfEnabled("Short");
                EnterShort(DefaultQuantity, "Short");
                pendKind = PEND_ENTRY; pendDir = -1;
            }
        }

        private void SetInitialStopIfEnabled(string fromEntrySignal)
        {
            if (UseInitialStop)
                SetStopLoss(fromEntrySignal, CalculationMode.Ticks, StopPoints / TickSize, false);
        }

        #region Properties
        [NinjaScriptProperty]
        [Range(1, 1000)]
        [Display(Name = "Trend Multiplier", Order = 1, GroupName = "1 Solar Wave")]
        public double TrendMultiplier { get; set; }

        [NinjaScriptProperty]
        [Range(1, 2000)]
        [Display(Name = "Stop Multiplier", Order = 2, GroupName = "1 Solar Wave")]
        public double StopMultiplier { get; set; }

        [NinjaScriptProperty]
        [Range(1, 100)]
        [Display(Name = "Slowdown Scan", Order = 3, GroupName = "1 Solar Wave")]
        public int SlowdownScan { get; set; }

        [NinjaScriptProperty]
        [Range(1, 100)]
        [Display(Name = "Weak-Weak Split", Order = 4, GroupName = "1 Solar Wave")]
        public int WeakWeakSplit { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Start Up", Order = 5, GroupName = "1 Solar Wave")]
        public bool StartUp { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Strict Exit (Close < TS, flip-only)", Order = 6, GroupName = "1 Solar Wave")]
        public bool StrictExit { get; set; }

        [NinjaScriptProperty]
        [Range(0, 100000)]
        [Display(Name = "Gate X (armed thr, PM) [INTERVAL-IDENTIFIED]", Order = 1, GroupName = "2 Session Gate")]
        public double GateX { get; set; }

        [NinjaScriptProperty]
        [Range(0, 100000)]
        [Display(Name = "Gate X2 (armed thr, AM) [INTERVAL-IDENTIFIED]", Order = 2, GroupName = "2 Session Gate")]
        public double GateX2 { get; set; }

        [NinjaScriptProperty]
        [Range(1, 20)]
        [Display(Name = "Gate K (consec same-side losses) [RIVAL: 4 total]", Order = 3, GroupName = "2 Session Gate")]
        public int GateK { get; set; }

        [NinjaScriptProperty]
        [Range(0, 100000)]
        [Display(Name = "Gate C (prior-session red) [INTERVAL-IDENTIFIED]", Order = 4, GroupName = "2 Session Gate")]
        public double GateC { get; set; }

        [NinjaScriptProperty]
        [Range(0, 1440)]
        [Display(Name = "Noon Minute (X/X2 switch)", Order = 5, GroupName = "2 Session Gate")]
        public int NoonMinute { get; set; }

        [NinjaScriptProperty]
        [Range(0, 1440)]
        [Display(Name = "Evening Block Minutes", Order = 6, GroupName = "2 Session Gate")]
        public int EveningBlockMinutes { get; set; }

        [NinjaScriptProperty]
        [Range(1, 1000)]
        [Display(Name = "Session Trade Cap (completed)", Order = 7, GroupName = "2 Session Gate")]
        public int SessionTradeCap { get; set; }

        [NinjaScriptProperty]
        [Range(0, 100)]
        [Display(Name = "Cooldown Bars", Order = 8, GroupName = "2 Session Gate")]
        public int CooldownBars { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Use Initial Stop (Jul-2025+ era)", Order = 1, GroupName = "3 Stop Group")]
        public bool UseInitialStop { get; set; }

        [NinjaScriptProperty]
        [Range(1, 1000)]
        [Display(Name = "Initial Stop (points)", Order = 2, GroupName = "3 Stop Group")]
        public double StopPoints { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Use Resume Latch [EXPERIMENTAL]", Order = 1, GroupName = "4 Resume Latch")]
        public bool UseResumeLatch { get; set; }

        [NinjaScriptProperty]
        [Range(0, 1000000)]
        [Display(Name = "Resume Level (static price)", Order = 2, GroupName = "4 Resume Latch")]
        public double ResumeLevel { get; set; }
        #endregion
    }
}
