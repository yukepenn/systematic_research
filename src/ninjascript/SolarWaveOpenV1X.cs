#region Using declarations
using System;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using System.Globalization;
using System.IO;
using System.Text;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
#endregion

// SolarWaveOpenV1X - SolarWaveOpenV1 plus an execution-level ledger export.
// Signal engine is byte-identical to SolarWaveOpenV1 (recovered open math, no
// vendor reference). The export captures every fill from OnExecutionUpdate so
// Tier-2 analytics run in pandas instead of shipping multi-MB payloads.
namespace NinjaTrader.NinjaScript.Strategies
{
    public class SolarWaveOpenV1X : Strategy
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
        private int    signalTrendVal;
        private int    signalWaveVal;

        private StringBuilder log;
        private int execCount;
        // context of the bar on which the entry signal was generated
        private int  pendingWave;
        private int  pendingSignal;

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = "Open Solar Wave core + execution ledger export";
                Name        = "SolarWaveOpenV1X";

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

                StartUp = false;
                ExportPath = "";
            }
            else if (State == State.Configure)
            {
                log = new StringBuilder();
                execCount = 0;
            }
            else if (State == State.DataLoaded)
            {
                initialized = false;
            }
            else if (State == State.Terminated)
            {
                Flush();
            }
        }

        private void Flush()
        {
            if (string.IsNullOrEmpty(ExportPath) || log == null)
                return;
            try
            {
                string dir = Path.GetDirectoryName(ExportPath);
                if (!string.IsNullOrEmpty(dir) && !Directory.Exists(dir))
                    Directory.CreateDirectory(dir);
                using (StreamWriter w = new StreamWriter(ExportPath, false))
                {
                    w.WriteLine(string.Format(CultureInfo.InvariantCulture,
                        "# TM={0} SM={1} SS={2} WWS={3} EST={4} TF={5} start={6} end={7} slip={8} instrument={9} period={10} execs={11}",
                        TrendMultiplier, StopMultiplier, SlowdownScan, WeakWeakSplit,
                        EntrySignalType, UseTimeFilter, StartTime, EndTime, Slippage,
                        Instrument != null ? Instrument.FullName : "?",
                        BarsPeriod != null ? BarsPeriod.ToString() : "?", execCount));
                    w.WriteLine("n,time,bar,name,order_action,market_position,price,qty,commission,wave,signal");
                    w.Write(log.ToString());
                    w.Flush();
                }
            }
            catch (Exception ex)
            {
                Print("SolarWaveOpenV1X export failed: " + ex.Message);
            }
        }

        protected override void OnExecutionUpdate(Execution execution, string executionId,
            double price, int quantity, MarketPosition marketPosition, string orderId,
            DateTime time)
        {
            if (log == null || execution == null || execution.Order == null)
                return;
            log.AppendLine(string.Format(CultureInfo.InvariantCulture,
                "{0},{1:yyyy-MM-ddTHH:mm:ss},{2},{3},{4},{5},{6},{7},{8},{9},{10}",
                execCount++, time, CurrentBar, execution.Name,
                execution.Order.OrderAction, marketPosition, price, quantity,
                execution.Commission, pendingWave, pendingSignal));
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
                    else if (px < anchor - S)
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
                    else if (px > anchor + S)
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

            UpdateSolarWave();

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
            {
                pendingWave = signalWaveVal; pendingSignal = signal;
                EnterLong(DefaultQuantity, "Long");
            }
            else if (EnableShort && shortSignal)
            {
                pendingWave = signalWaveVal; pendingSignal = signal;
                EnterShort(DefaultQuantity, "Short");
            }
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

        [NinjaScriptProperty]
        [Display(Name = "Export Path", Order = 1, GroupName = "Export")]
        public string ExportPath { get; set; }

        #endregion
    }
}
