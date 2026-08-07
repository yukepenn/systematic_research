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

// SolarWaveOpenX2 - open Solar Wave core (no vendor reference) + execution ledger
// export whose filename is derived from the effective parameters, so a single
// NT8 optimization sweep produces one ledger per parameter cell.
// Signal engine identical to SolarWaveOpenV1 (RE01 penny-exact vs vendor).
namespace NinjaTrader.NinjaScript.Strategies
{
    public class SolarWaveOpenX2 : Strategy
    {
        private double anchor;
        private bool   isUp;
        private bool   weak;
        private int    barsSinceExtreme;
        private int    nextWeakBar;
        private int    wave;
        private bool   initialized;

        private double trailingStopVal;
        private int    signalTradeVal;
        private int    signalWaveVal;

        private StringBuilder log;
        private int    execCount;
        private int    pendingWave;
        private int    pendingSignal;

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = "Open Solar Wave core + sweep-aware execution ledger export";
                Name        = "SolarWaveOpenX2";

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
                EndTime       = 163000;

                StartUp   = false;
                ExportDir = "";
                Tag       = "run";
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

        private string BuildPath()
        {
            int tf = BarsPeriod != null ? BarsPeriod.Value : 0;
            string exit = UseTimeFilter
                ? string.Format(CultureInfo.InvariantCulture, "t{0}", EndTime)
                : "sc";
            string file = string.Format(CultureInfo.InvariantCulture,
                "{0}__tf{1}_sm{2}_tm{3}_ss{4}_wws{5}_est{6}_{7}_slip{8}_L{9}S{10}.csv",
                Tag, tf, (int)StopMultiplier, (int)TrendMultiplier, SlowdownScan,
                WeakWeakSplit, EntrySignalType, exit, Slippage,
                EnableLong ? 1 : 0, EnableShort ? 1 : 0);
            return Path.Combine(ExportDir, file);
        }

        private void Flush()
        {
            if (string.IsNullOrEmpty(ExportDir) || log == null)
                return;
            try
            {
                if (!Directory.Exists(ExportDir))
                    Directory.CreateDirectory(ExportDir);
                string path = BuildPath();
                using (StreamWriter w = new StreamWriter(path, false))
                {
                    w.WriteLine(string.Format(CultureInfo.InvariantCulture,
                        "# TM={0} SM={1} SS={2} WWS={3} EST={4} TF={5} start={6} end={7} slip={8} instrument={9} period={10} execs={11} long={12} short={13}",
                        TrendMultiplier, StopMultiplier, SlowdownScan, WeakWeakSplit,
                        EntrySignalType, UseTimeFilter, StartTime, EndTime, Slippage,
                        Instrument != null ? Instrument.FullName : "?",
                        BarsPeriod != null ? BarsPeriod.Value : 0, execCount,
                        EnableLong, EnableShort));
                    w.WriteLine("n,time,bar,name,order_action,market_position,price,qty,commission,wave,signal");
                    w.Write(log.ToString());
                    w.Flush();
                }
            }
            catch (Exception ex)
            {
                Print("SolarWaveOpenX2 export failed: " + ex.Message);
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
            signalWaveVal   = sign * wave;
        }

        protected override void OnBarUpdate()
        {
            if (BarsInProgress != 0)
                return;

            UpdateSolarWave();

            if (CurrentBar < BarsRequiredToTrade)
                return;

            if (!IsAllowedTime(ToTime(Time[0])))
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
        [Display(Name = "Export Dir", Order = 1, GroupName = "Export")]
        public string ExportDir { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Tag", Order = 2, GroupName = "Export")]
        public string Tag { get; set; }

        #endregion
    }
}
