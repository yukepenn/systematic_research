#region Using declarations
using System;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
using NinjaTrader.NinjaScript.Indicators;
#endregion

namespace NinjaTrader.NinjaScript.Strategies
{
    public class SolarWaveRKReplicaV0 : Strategy
    {
        private NinjaTrader.NinjaScript.Indicators.RenkoKings
            .RenkoKings_SolarWaveRK solarWave;

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = "Solar Wave RK replication probe";
                Name = "SolarWaveRKReplicaV0";

                Calculate = Calculate.OnBarClose;

                EntriesPerDirection = 1;
                EntryHandling = EntryHandling.AllEntries;
                DefaultQuantity = 1;

                IsExitOnSessionCloseStrategy = true;
                ExitOnSessionCloseSeconds = 30;

                BarsRequiredToTrade = 20;
                MaximumBarsLookBack = MaximumBarsLookBack.TwoHundredFiftySix;

                OrderFillResolution = OrderFillResolution.Standard;
                Slippage = 0;

                StartBehavior = StartBehavior.WaitUntilFlat;
                TimeInForce = TimeInForce.Gtc;
                RealtimeErrorHandling =
                    RealtimeErrorHandling.StopCancelClose;

                TrendMultiplier = 90;
                StopMultiplier = 179;
                SlowdownScan = 5;
                WeakWeakSplit = 10;
                PullbackEarly = true;
                PullbackSplit = 10;

                // 0 = 所有 Signal_Trade
                // 1 = Trend Start
                // 2 = Pullback
                // 3 = Strengthening
                EntrySignalType = 1;

                EnableLong = true;
                EnableShort = true;

                UseTimeFilter = false;
                StartTime = 93000;
                EndTime = 160000;
            }
            else if (State == State.DataLoaded)
            {
                solarWave = RenkoKings_SolarWaveRK(
                    Close,
                    TrendMultiplier,
                    StopMultiplier,
                    SlowdownScan,
                    WeakWeakSplit,
                    PullbackEarly,
                    PullbackSplit
                );

                AddChartIndicator(solarWave);
            }
        }

        protected override void OnBarUpdate()
        {
            if (BarsInProgress != 0)
                return;

            if (CurrentBar < BarsRequiredToTrade)
                return;

            bool allowedTime = IsAllowedTime(ToTime(Time[0]));

            // 时间窗口结束后不再持仓
            if (!allowedTime)
            {
                if (Position.MarketPosition == MarketPosition.Long)
                    ExitLong("L-TimeExit", "Long");

                if (Position.MarketPosition == MarketPosition.Short)
                    ExitShort("S-TimeExit", "Short");

                return;
            }

            double trailingStop = solarWave.TrailingStop[0];

            // 第一版：使用 Solar Wave 自己的 Trailing Stop 作为退出
            if (!double.IsNaN(trailingStop))
            {
                if (Position.MarketPosition == MarketPosition.Long
                    && Close[0] <= trailingStop)
                {
                    ExitLong("L-SolarExit", "Long");
                    return;
                }

                if (Position.MarketPosition == MarketPosition.Short
                    && Close[0] >= trailingStop)
                {
                    ExitShort("S-SolarExit", "Short");
                    return;
                }
            }

            if (Position.MarketPosition != MarketPosition.Flat)
                return;

            int signal =
                (int)Math.Round(solarWave.Signal_Trade[0]);

            bool longSignal =
                signal > 0
                && (EntrySignalType == 0
                    || signal == EntrySignalType);

            bool shortSignal =
                signal < 0
                && (EntrySignalType == 0
                    || -signal == EntrySignalType);

            if (EnableLong && longSignal)
            {
                EnterLong(DefaultQuantity, "Long");
            }
            else if (EnableShort && shortSignal)
            {
                EnterShort(DefaultQuantity, "Short");
            }
        }

        private bool IsAllowedTime(int currentTime)
        {
            if (!UseTimeFilter)
                return true;

            // 普通日内窗口，例如 09:30–16:00
            if (StartTime <= EndTime)
                return currentTime >= StartTime
                    && currentTime <= EndTime;

            // 支持跨午夜窗口
            return currentTime >= StartTime
                || currentTime <= EndTime;
        }

        #region Properties

        [NinjaScriptProperty]
        [Range(1, 1000)]
        [Display(Name = "Trend Multiplier", Order = 1,
            GroupName = "Solar Wave")]
        public double TrendMultiplier { get; set; }

        [NinjaScriptProperty]
        [Range(1, 2000)]
        [Display(Name = "Stop Multiplier", Order = 2,
            GroupName = "Solar Wave")]
        public double StopMultiplier { get; set; }

        [NinjaScriptProperty]
        [Range(1, 100)]
        [Display(Name = "Slowdown Scan", Order = 3,
            GroupName = "Solar Wave")]
        public int SlowdownScan { get; set; }

        [NinjaScriptProperty]
        [Range(1, 100)]
        [Display(Name = "Weak-Weak Split", Order = 4,
            GroupName = "Solar Wave")]
        public int WeakWeakSplit { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Pullback Early", Order = 5,
            GroupName = "Solar Wave")]
        public bool PullbackEarly { get; set; }

        [NinjaScriptProperty]
        [Range(1, 100)]
        [Display(Name = "Pullback Split", Order = 6,
            GroupName = "Solar Wave")]
        public int PullbackSplit { get; set; }

        [NinjaScriptProperty]
        [Range(0, 3)]
        [Display(Name = "Entry Signal Type", Order = 1,
            GroupName = "Entry")]
        public int EntrySignalType { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Enable Long", Order = 2,
            GroupName = "Entry")]
        public bool EnableLong { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Enable Short", Order = 3,
            GroupName = "Entry")]
        public bool EnableShort { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Use Time Filter", Order = 1,
            GroupName = "Time")]
        public bool UseTimeFilter { get; set; }

        [NinjaScriptProperty]
        [Range(0, 235959)]
        [Display(Name = "Start Time", Order = 2,
            GroupName = "Time")]
        public int StartTime { get; set; }

        [NinjaScriptProperty]
        [Range(0, 235959)]
        [Display(Name = "End Time", Order = 3,
            GroupName = "Time")]
        public int EndTime { get; set; }

        #endregion
    }
}