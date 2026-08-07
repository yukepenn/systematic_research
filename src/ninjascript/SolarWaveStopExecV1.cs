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

// SolarWaveStopExecV1 - H-011.
//
// DC01 measured that the close-basis crossing excess is ~23.5 ticks per segment
// ($117.57), i.e. ~89% of all friction, dwarfing commission ($4.36) and 1-tick
// slippage ($9.53) combined. This variant attacks exactly that quantity: instead
// of a market order on the close of the bar that broke the ladder level, it rests
// a STOP order AT the ladder level, so the fill happens intrabar at the level.
//
// Honest semantics: the ladder state still advances on CLOSES (identical to
// SolarWaveOpenV1, so the signal definition is unchanged and comparable), but the
// working order is submitted one bar in advance at the currently-known level, and
// NT8 fills it intrabar. A stop that gaps through fills at the gap price - NT8's
// standard behaviour - which is the conservative side. ExecMode lets the same
// class reproduce the market-on-close baseline for a controlled A/B.
//
// Three arms, so the two changes are never confounded:
//   ExecMode 0 = market on close, flip-bar entry SKIPPED     (= SolarWaveOpenV1, arm A)
//   ExecMode 2 = market on close, always-in stop-and-reverse (arm B)
//   ExecMode 1 = resting stop at the ladder level, always-in (arm C, H-011)
// B - A isolates the skipped flip-bar entry; C - B isolates the fill mechanism.
namespace NinjaTrader.NinjaScript.Strategies
{
    public class SolarWaveStopExecV1 : Strategy
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

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = "H-011: Solar Wave ladder with resting-stop execution";
                Name        = "SolarWaveStopExecV1";

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
                StartTime     = 180000;
                EndTime       = 163000;

                StartUp   = false;
                ExecMode  = 1;
                ExportDir = "";
                Tag       = "h011";
            }
            else if (State == State.Configure)
            {
                log = new StringBuilder(1 << 20);
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
                ? string.Format(CultureInfo.InvariantCulture, "t{0}", EndTime) : "sc";
            string file = string.Format(CultureInfo.InvariantCulture,
                "{0}__tf{1}_sm{2}_tm{3}_ss{4}_wws{5}_est{6}_{7}_slip{8}_L{9}S{10}.csv",
                Tag + "x" + ExecMode, tf, (int)StopMultiplier, (int)TrendMultiplier,
                SlowdownScan, WeakWeakSplit, EntrySignalType, exit, Slippage,
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
                using (StreamWriter w = new StreamWriter(BuildPath(), false))
                {
                    w.WriteLine(string.Format(CultureInfo.InvariantCulture,
                        "# TM={0} SM={1} SS={2} WWS={3} EST={4} TF={5} start={6} end={7} slip={8} instrument={9} period={10} execs={11} execmode={12}",
                        TrendMultiplier, StopMultiplier, SlowdownScan, WeakWeakSplit,
                        EntrySignalType, UseTimeFilter, StartTime, EndTime, Slippage,
                        Instrument != null ? Instrument.FullName : "?",
                        BarsPeriod != null ? BarsPeriod.Value : 0, execCount, ExecMode));
                    w.WriteLine("n,time,bar,name,order_action,market_position,price,qty,commission,wave,signal");
                    w.Write(log.ToString());
                    w.Flush();
                }
            }
            catch (Exception ex)
            {
                Print("SolarWaveStopExecV1 export failed: " + ex.Message);
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
                execution.Commission, signalWaveVal, signalTradeVal));
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
                isUp = StartUp; anchor = px; weak = false;
                barsSinceExtreme = 0; nextWeakBar = int.MinValue; wave = 1;
            }
            else
            {
                if (isUp)
                {
                    if (px >= anchor) { if (px > anchor) ev = 1; anchor = px; }
                    else if (px < anchor - S) { isUp = false; anchor = px; ev = 2; }
                }
                else
                {
                    if (px <= anchor) { if (px < anchor) ev = 1; anchor = px; }
                    else if (px > anchor + S) { isUp = true; anchor = px; ev = 2; }
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
                    wave++; weak = false;
                    signalTradeVal = isUp ? 3 : -3;
                    nextWeakBar = CurrentBar + WeakWeakSplit;
                }
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
            signalWaveVal   = (isUp ? 1 : -1) * wave;
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
                else if (Position.MarketPosition == MarketPosition.Short)
                    ExitShort("S-TimeExit", "Short");
                return;
            }

            if (ExecMode == 1)
            {
                StopExecLogic();
                return;
            }

            int sig = signalTradeVal;
            bool L  = sig > 0 && (EntrySignalType == 0 || sig == EntrySignalType);
            bool Sh = sig < 0 && (EntrySignalType == 0 || -sig == EntrySignalType);

            if (ExecMode == 2)
            {
                // --- arm B: always-in. A flip both closes the old side and opens the new
                // one on the SAME bar, at the same close price; NT8 reverses on a single
                // entry order. Same fills as arm A, but nothing is skipped.
                if (EnableLong && L)        { EnterLong(DefaultQuantity, "Long");  return; }
                if (EnableShort && Sh)      { EnterShort(DefaultQuantity, "Short"); return; }
                double tsB = trailingStopVal;
                if (Position.MarketPosition == MarketPosition.Long && Close[0] <= tsB)
                    ExitLong("L-SolarExit", "Long");
                else if (Position.MarketPosition == MarketPosition.Short && Close[0] >= tsB)
                    ExitShort("S-SolarExit", "Short");
                return;
            }

            // --- arm A / ExecMode 0: market on bar close, flip-bar entry skipped ---
            double ts = trailingStopVal;
            if (Position.MarketPosition == MarketPosition.Long && Close[0] <= ts)
            {
                ExitLong("L-SolarExit", "Long"); return;
            }
            if (Position.MarketPosition == MarketPosition.Short && Close[0] >= ts)
            {
                ExitShort("S-SolarExit", "Short"); return;
            }
            if (Position.MarketPosition != MarketPosition.Flat)
                return;

            if (EnableLong && L)        EnterLong(DefaultQuantity, "Long");
            else if (EnableShort && Sh) EnterShort(DefaultQuantity, "Short");
        }

        // ExecMode 1: the position is always aligned with the ladder direction, and the
        // transition is worked as a resting stop AT the ladder level rather than a market
        // order after the level has already been passed. The level is known at the close
        // of bar t and the order works during bar t+1, so there is no look-ahead.
        private void StopExecLogic()
        {
            double level = trailingStopVal;

            if (Position.MarketPosition == MarketPosition.Long)
            {
                // exit long at the ladder level; if reversal is enabled, the same level
                // is the short entry, so submit a stop-market short entry there.
                if (EnableShort && EntrySignalType == 1)
                    EnterShortStopMarket(0, true, DefaultQuantity, level, "Short");
                else
                    ExitLongStopMarket(0, true, DefaultQuantity, level, "L-SolarExit", "Long");
            }
            else if (Position.MarketPosition == MarketPosition.Short)
            {
                if (EnableLong && EntrySignalType == 1)
                    EnterLongStopMarket(0, true, DefaultQuantity, level, "Long");
                else
                    ExitShortStopMarket(0, true, DefaultQuantity, level, "S-SolarExit", "Short");
            }
            else
            {
                // flat: arm whichever side the ladder would flip into
                if (isUp && EnableShort)
                    EnterShortStopMarket(0, true, DefaultQuantity, level, "Short");
                else if (!isUp && EnableLong)
                    EnterLongStopMarket(0, true, DefaultQuantity, level, "Long");
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
        [NinjaScriptProperty] [Range(1, 1000)]
        [Display(Name = "Trend Multiplier", Order = 1, GroupName = "Solar Wave")]
        public double TrendMultiplier { get; set; }

        [NinjaScriptProperty] [Range(1, 2000)]
        [Display(Name = "Stop Multiplier", Order = 2, GroupName = "Solar Wave")]
        public double StopMultiplier { get; set; }

        [NinjaScriptProperty] [Range(1, 100)]
        [Display(Name = "Slowdown Scan", Order = 3, GroupName = "Solar Wave")]
        public int SlowdownScan { get; set; }

        [NinjaScriptProperty] [Range(1, 100)]
        [Display(Name = "Weak-Weak Split", Order = 4, GroupName = "Solar Wave")]
        public int WeakWeakSplit { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Start Up", Order = 5, GroupName = "Solar Wave")]
        public bool StartUp { get; set; }

        [NinjaScriptProperty] [Range(0, 2)]
        [Display(Name = "Exec Mode", Order = 6, GroupName = "Solar Wave")]
        public int ExecMode { get; set; }

        [NinjaScriptProperty] [Range(0, 3)]
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

        [NinjaScriptProperty] [Range(0, 235959)]
        [Display(Name = "Start Time", Order = 2, GroupName = "Time")]
        public int StartTime { get; set; }

        [NinjaScriptProperty] [Range(0, 235959)]
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
