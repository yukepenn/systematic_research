#region Using declarations
using System;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
#endregion

// SolarWaveOpenV1 — open-source reconstruction of the Solar Wave RK core.
// NO vendor assembly reference. The entire signal engine is the recovered
// recurrence documented in research/03_reverse_engineering/SOLARWAVE_MATH.md:
//   one state variable (running close extreme since trend start), two affine
//   offset lines, and a bar-counter automaton for the wave/strength layer.
// Entry/exit logic is byte-for-byte the same policy as SolarWaveRKReplicaV0
// so that results are directly comparable.
namespace NinjaTrader.NinjaScript.Strategies
{
    public class SolarWaveOpenV1 : Strategy
    {
        // --- recovered indicator state ---
        private double anchor;          // running extreme of Close since trend start
        private bool   isUp;            // current trend direction
        private bool   weak;            // trend "slowing" flag
        private int    barsSinceExtreme;
        private int    nextWeakBar;
        private int    wave;            // impulse-leg counter within the trend
        private bool   initialized;

        // --- per-bar outputs (mirror the vendor's public Series) ---
        private double trailingStopVal;
        private double trendVectorVal;
        private int    signalTradeVal;
        private int    signalTrendVal;
        private int    signalWaveVal;

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = "Open reconstruction of Solar Wave RK core (no vendor dependency)";
                Name        = "SolarWaveOpenV1";

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

                EntrySignalType = 1;
                EnableLong      = true;
                EnableShort     = true;

                UseTimeFilter = false;
                StartTime     = 93000;
                EndTime       = 160000;

                StartUp = false;   // initial trend direction seed
            }
            else if (State == State.DataLoaded)
            {
                initialized = false;
            }
        }

        // The recovered recurrence. Runs on EVERY bar, before any trade gating,
        // so the state machine sees the same bar sequence the vendor indicator does.
        private void UpdateSolarWave()
        {
            double S  = StopMultiplier  * TickSize;
            double V  = TrendMultiplier * TickSize;
            double px = Close[0];

            signalTradeVal = 0;
            int ev = 0;   // 0 = nothing, 1 = new extreme, 2 = trend flip

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
                signalTradeVal = isUp ? 1 : -1;                 // Type 1: trend start
                nextWeakBar = CurrentBar + WeakWeakSplit;
            }
            else if (ev == 1)
            {
                barsSinceExtreme = 0;
                if (weak)
                {
                    wave++;
                    weak = false;
                    signalTradeVal = isUp ? 3 : -3;             // Type 3: strengthening
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

            int sign        = isUp ? 1 : -1;
            trailingStopVal = isUp ? anchor - S : anchor + S;
            trendVectorVal  = isUp ? anchor - V : anchor + V;
            signalTrendVal  = sign * (weak ? 1 : 2);
            signalWaveVal   = sign * wave;
        }

        protected override void OnBarUpdate()
        {
            if (BarsInProgress != 0)
                return;

            UpdateSolarWave();                       // state advances on every bar

            if (CurrentBar < BarsRequiredToTrade)
                return;

            bool allowedTime = IsAllowedTime(ToTime(Time[0]));

            if (!allowedTime)
            {
                if (Position.MarketPosition == MarketPosition.Long)
                    ExitLong("L-TimeExit", "Long");
                if (Position.MarketPosition == MarketPosition.Short)
                    ExitShort("S-TimeExit", "Short");
                return;
            }

            double trailingStop = trailingStopVal;

            if (!double.IsNaN(trailingStop))
            {
                if (Position.MarketPosition == MarketPosition.Long && Close[0] <= trailingStop)
                {
                    ExitLong("L-SolarExit", "Long");
                    return;
                }
                if (Position.MarketPosition == MarketPosition.Short && Close[0] >= trailingStop)
                {
                    ExitShort("S-SolarExit", "Short");
                    return;
                }
            }

            if (Position.MarketPosition != MarketPosition.Flat)
                return;

            int signal = signalTradeVal;

            bool longSignal  = signal > 0 && (EntrySignalType == 0 || signal == EntrySignalType);
            bool shortSignal = signal < 0 && (EntrySignalType == 0 || -signal == EntrySignalType);

            if (EnableLong && longSignal)
                EnterLong(DefaultQuantity, "Long");
            else if (EnableShort && shortSignal)
                EnterShort(DefaultQuantity, "Short");
        }

        private bool IsAllowedTime(int currentTime)
        {
            if (!UseTimeFilter) return true;
            if (StartTime <= EndTime)
                return currentTime >= StartTime && currentTime <= EndTime;
            return currentTime >= StartTime || currentTime <= EndTime;
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
        [Range(0, 3)]
        [Display(Name = "Entry Signal Type", Order = 1, GroupName = "Entry")]
        public int EntrySignalType { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Enable Long", Order = 2, GroupName = "Entry")]
        public bool EnableLong { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Enable Short", Order = 3, GroupName = "Entry")]
        public bool EnableShort { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Use Time Filter", Order = 1, GroupName = "Time")]
        public bool UseTimeFilter { get; set; }

        [NinjaScriptProperty]
        [Range(0, 235959)]
        [Display(Name = "Start Time", Order = 2, GroupName = "Time")]
        public int StartTime { get; set; }

        [NinjaScriptProperty]
        [Range(0, 235959)]
        [Display(Name = "End Time", Order = 3, GroupName = "Time")]
        public int EndTime { get; set; }

        #endregion
    }
}
