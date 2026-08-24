#region Using declarations
using System;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
#endregion

// OriginalTraderSolarSelTime_v1 — NinjaScript port of OTR-S-CAND1, the Track-S
// reconstruction candidate of the original trader's SolarWindRKSelTime
// (research/original_trader_reconstruction/solar_family/TRACK_S_REPORT.md).
//
// Signal engine: byte-identical to SolarWaveOpenV1 (recovered Solar core, no vendor
// dependency). Wrapper (the reconstructed part):
//   - entries on Type-1 (flip) AND Type-3 (strengthening) signals when flat
//   - STOP-AND-REVERSE directly on opposite Type-1 flips (inside the time window)
//   - exit when Close TOUCHES the end-of-bar TrailingStop (inclusive - S0-certified
//     touch semantics), plus exit-on-session-close
//   - SelTime: entries/reversals only inside [StartTime, EndTime] (default 04:00-16:00
//     ET); force-flat outside the window (TimeExit)
// Classification: PARTIALLY RECONSTRUCTED (hold -20% residual); NOT an optimization.
// RESEARCH ONLY: historical Strategy Analyzer use; fails closed in realtime.
namespace NinjaTrader.NinjaScript.Strategies
{
    public class OriginalTraderSolarSelTime_v1 : Strategy
    {
        private double anchor;
        private bool   isUp;
        private bool   weak;
        private int    barsSinceExtreme;
        private int    nextWeakBar;
        private int    wave;
        private bool   initialized;

        private double trailingStopVal;
        private double trendVectorVal;
        private int    signalTradeVal;

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = "OTR-S-CAND1: reconstructed SolarWindRKSelTime wrapper (research only)";
                Name        = "OriginalTraderSolarSelTime_v1";

                Calculate               = Calculate.OnBarClose;
                EntriesPerDirection     = 1;
                EntryHandling           = EntryHandling.AllEntries;
                DefaultQuantity         = 1;

                IsExitOnSessionCloseStrategy = true;
                ExitOnSessionCloseSeconds    = 30;

                BarsRequiredToTrade  = 20;
                MaximumBarsLookBack  = MaximumBarsLookBack.TwoHundredFiftySix;
                OrderFillResolution  = OrderFillResolution.Standard;
                Slippage             = 0;
                StartBehavior        = StartBehavior.WaitUntilFlat;
                TimeInForce          = TimeInForce.Gtc;
                RealtimeErrorHandling = RealtimeErrorHandling.StopCancelClose;

                TrendMultiplier = 90;
                StopMultiplier  = 179;
                SlowdownScan    = 5;
                WeakWeakSplit   = 10;
                StartUp         = false;

                EnableT3Entry   = true;
                ReverseOnFlip   = true;
                EnableLong      = true;
                EnableShort     = true;

                UseTimeFilter = true;
                StartTime     = 40000;    // 04:00 ET
                EndTime       = 160000;   // 16:00 ET
            }
            else if (State == State.DataLoaded)
            {
                initialized = false;
            }
            else if (State == State.Realtime)
            {
                // Research-only object: never operate in realtime.
                Log("OriginalTraderSolarSelTime_v1 is research-only; disabling.", LogLevel.Error);
                SetState(State.Terminated);
            }
        }

        private void UpdateSolarWave()
        {
            double S  = StopMultiplier  * TickSize;
            double V  = TrendMultiplier * TickSize;
            double px = Close[0];

            signalTradeVal = 0;
            int ev = 0;

            if (!initialized)
            {
                initialized      = true;
                isUp             = StartUp;
                anchor           = px;
                weak             = false;
                barsSinceExtreme = 0;
                nextWeakBar      = int.MinValue;
                wave             = 1;
            }
            else
            {
                if (isUp)
                {
                    if (px >= anchor)
                    {
                        if (px > anchor) ev = 1;
                        anchor = px;
                    }
                    else if (px < anchor - S)        // STRICT: touching does not flip
                    {
                        isUp = false; anchor = px; ev = 2;
                    }
                }
                else
                {
                    if (px <= anchor)
                    {
                        if (px < anchor) ev = 1;
                        anchor = px;
                    }
                    else if (px > anchor + S)        // STRICT
                    {
                        isUp = true; anchor = px; ev = 2;
                    }
                }
            }

            if (ev == 2)
            {
                weak = false; barsSinceExtreme = 0; wave = 1;
                signalTradeVal = isUp ? 1 : -1;
                nextWeakBar = CurrentBar + WeakWeakSplit;
            }
            else if (ev == 1)
            {
                barsSinceExtreme = 0;
                if (weak)
                {
                    wave++;
                    weak = false;
                    signalTradeVal = isUp ? 3 : -3;
                    nextWeakBar = CurrentBar + WeakWeakSplit;
                }
            }
            else
            {
                barsSinceExtreme++;
                if (!weak && barsSinceExtreme >= SlowdownScan && CurrentBar >= nextWeakBar)
                {
                    weak = true;
                    nextWeakBar = CurrentBar + WeakWeakSplit;
                }
            }

            trailingStopVal = isUp ? anchor - S : anchor + S;
            trendVectorVal  = isUp ? anchor - V : anchor + V;
        }

        protected override void OnBarUpdate()
        {
            if (BarsInProgress != 0)
                return;

            UpdateSolarWave();

            if (CurrentBar < BarsRequiredToTrade)
                return;

            bool allowedTime = IsAllowedTime(ToTime(Time[0]));

            // SelTime force-flat outside the window
            if (!allowedTime)
            {
                if (Position.MarketPosition == MarketPosition.Long)
                    ExitLong("L-TimeExit", "Long");
                if (Position.MarketPosition == MarketPosition.Short)
                    ExitShort("S-TimeExit", "Short");
                return;
            }

            int sig = signalTradeVal;

            // exit / reverse (touch semantics: inclusive comparison, end-of-bar stop)
            if (Position.MarketPosition == MarketPosition.Long && Close[0] <= trailingStopVal)
            {
                if (ReverseOnFlip && sig == -1 && EnableShort)
                    EnterShort(DefaultQuantity, "Short");     // NT8 reverses in one fill
                else
                    ExitLong("L-SolarExit", "Long");
                return;
            }
            if (Position.MarketPosition == MarketPosition.Short && Close[0] >= trailingStopVal)
            {
                if (ReverseOnFlip && sig == 1 && EnableLong)
                    EnterLong(DefaultQuantity, "Long");
                else
                    ExitShort("S-SolarExit", "Short");
                return;
            }

            if (Position.MarketPosition != MarketPosition.Flat)
                return;

            // entries when flat: Type 1 always; Type 3 when enabled
            bool entrySig = sig != 0 && (Math.Abs(sig) == 1 || (Math.Abs(sig) == 3 && EnableT3Entry));
            if (!entrySig)
                return;

            if (sig > 0 && EnableLong)
                EnterLong(DefaultQuantity, "Long");
            else if (sig < 0 && EnableShort)
                EnterShort(DefaultQuantity, "Short");
        }

        private bool IsAllowedTime(int currentTime)
        {
            if (!UseTimeFilter) return true;
            if (StartTime <= EndTime)
                return currentTime >= StartTime && currentTime < EndTime;
            return currentTime >= StartTime || currentTime < EndTime;
        }

        #region Properties
        [NinjaScriptProperty]
        [Range(1, 1000)]
        [Display(Name = "Trend Multiplier", Order = 1, GroupName = "Solar Wave")]
        public double TrendMultiplier { get; set; }

        [NinjaScriptProperty]
        [Range(1, 2000)]
        [Display(Name = "Stop Multiplier", Order = 2, GroupName = "Solar Wave")]
        public double StopMultiplier { get; set; }

        [NinjaScriptProperty]
        [Range(1, 100)]
        [Display(Name = "Slowdown Scan", Order = 3, GroupName = "Solar Wave")]
        public int SlowdownScan { get; set; }

        [NinjaScriptProperty]
        [Range(1, 100)]
        [Display(Name = "Weak-Weak Split", Order = 4, GroupName = "Solar Wave")]
        public int WeakWeakSplit { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Start Up", Order = 5, GroupName = "Solar Wave")]
        public bool StartUp { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Enable T3 Entry", Order = 1, GroupName = "Wrapper")]
        public bool EnableT3Entry { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Reverse On Flip", Order = 2, GroupName = "Wrapper")]
        public bool ReverseOnFlip { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Enable Long", Order = 3, GroupName = "Wrapper")]
        public bool EnableLong { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Enable Short", Order = 4, GroupName = "Wrapper")]
        public bool EnableShort { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Use Time Filter", Order = 1, GroupName = "SelTime")]
        public bool UseTimeFilter { get; set; }

        [NinjaScriptProperty]
        [Range(0, 235959)]
        [Display(Name = "Start Time", Order = 2, GroupName = "SelTime")]
        public int StartTime { get; set; }

        [NinjaScriptProperty]
        [Range(0, 235959)]
        [Display(Name = "End Time", Order = 3, GroupName = "SelTime")]
        public int EndTime { get; set; }
        #endregion
    }
}
