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

// SolarWaveOpenV3 - the open directional-change engine, generalised along the three
// axes the recovered mathematics unlocked. No vendor reference anywhere.
//
//   AnchorMode      H-008  0 = running CLOSE extreme      (vendor behaviour)
//                          1 = running HIGH/LOW extreme
//                          2 = close-confirmed HIGH/LOW extreme
//   ThresholdMode   H-006  0 = S is a fixed tick count    (vendor behaviour)
//                          1 = S = VolMult * sigma, sampled ONCE at trend birth
//                              (sigma = causal SMA of |close - close[1]|, VolPeriod bars),
//                              clamped to [SMinTicks, SMaxTicks]
//   ExitMultiplier  H-007  <= 0 disables (exit and reversal share one distance, vendor
//                          behaviour). > 0 exits the position at ExitMultiplier ticks
//                          while the TREND still only flips at the reversal distance,
//                          so the strategy can sit flat between the two.
//
// Every axis defaults to the vendor behaviour, so the default configuration must
// reproduce SolarWaveOpenV1 (and therefore the frozen baseline) exactly. That is the
// gate test, run before any result is read.
//
// Execution is market-on-close only: H-011 established that intrabar fills desynchronise
// from close-based ladder state (research/02_solar_refinements/WAVE1C_report.md sec 3).
namespace NinjaTrader.NinjaScript.Strategies
{
    public class SolarWaveOpenV3 : Strategy
    {
        private double anchor;          // running extreme, per AnchorMode
        private double sEff;            // effective reversal distance in price units
        private bool   isUp;
        private bool   weak;
        private int    barsSinceExtreme;
        private int    nextWeakBar;
        private int    wave;
        private bool   initialized;

        private double trailingStopVal; // anchor -/+ sEff        (reversal level)
        private double exitLevelVal;    // anchor -/+ exitDist    (position exit level)
        private int    signalTradeVal;
        private int    signalWaveVal;

        private double volSum;          // rolling |dclose| accumulator
        private double prevClose;
        private int    volCount;

        private StringBuilder log;
        private int execCount;

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = "Open directional-change engine: anchor / threshold / split-exit axes";
                Name        = "SolarWaveOpenV3";

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

                AnchorMode     = 0;
                ThresholdMode  = 0;
                VolPeriod      = 1380;
                VolMult        = 14.0;
                SMinTicks      = 40;
                SMaxTicks      = 800;
                ExitMultiplier = 0;

                EntrySignalType = 1;
                EnableLong      = true;
                EnableShort     = true;

                UseTimeFilter = false;
                StartTime     = 180000;
                EndTime       = 163000;

                ExportDir = "";
                Tag       = "v3";
            }
            else if (State == State.Configure)
            {
                log = new StringBuilder(1 << 20);
                execCount = 0;
            }
            else if (State == State.DataLoaded)
            {
                initialized = false;
                volSum = 0; volCount = 0; prevClose = double.NaN;
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
                "{0}__tf{1}_sm{2}_am{3}_th{4}_vp{5}_vm{6}_xm{7}_{8}_slip{9}.csv",
                Tag, tf, (int)StopMultiplier, AnchorMode, ThresholdMode, VolPeriod,
                VolMult.ToString("0.##", CultureInfo.InvariantCulture),
                ExitMultiplier, exit, Slippage);
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
                        "# TM={0} SM={1} SS={2} WWS={3} anchor={4} thresh={5} volperiod={6} volmult={7} smin={8} smax={9} exitmult={10} EST={11} TF={12} end={13} slip={14} instrument={15} period={16} execs={17}",
                        TrendMultiplier, StopMultiplier, SlowdownScan, WeakWeakSplit,
                        AnchorMode, ThresholdMode, VolPeriod, VolMult, SMinTicks, SMaxTicks,
                        ExitMultiplier, EntrySignalType, UseTimeFilter, EndTime, Slippage,
                        Instrument != null ? Instrument.FullName : "?",
                        BarsPeriod != null ? BarsPeriod.Value : 0, execCount));
                    w.WriteLine("n,time,bar,name,order_action,market_position,price,qty,commission,wave,signal");
                    w.Write(log.ToString());
                    w.Flush();
                }
            }
            catch (Exception ex)
            {
                Print("SolarWaveOpenV3 export failed: " + ex.Message);
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

        // causal mean |close - close[1]| over the trailing VolPeriod bars, in price units
        private double CausalSigma()
        {
            if (volCount < 30)
                return double.NaN;
            return volSum / volCount;
        }

        private void UpdateVol()
        {
            if (!double.IsNaN(prevClose))
            {
                double a = Math.Abs(Close[0] - prevClose);
                volSum += a; volCount++;
                if (volCount > VolPeriod)
                {
                    // drop the oldest by re-seeding from the available window; NT8 keeps
                    // MaximumBarsLookBack bars, so recompute over the true window instead
                    int n = Math.Min(VolPeriod, CurrentBar);
                    double s = 0;
                    for (int i = 0; i < n; i++)
                        s += Math.Abs(Close[i] - Close[i + 1]);
                    volSum = s; volCount = n;
                }
            }
            prevClose = Close[0];
        }

        private double ResolveS()
        {
            if (ThresholdMode == 0)
                return StopMultiplier * TickSize;
            double sig = CausalSigma();
            if (double.IsNaN(sig) || sig <= 0)
                return StopMultiplier * TickSize;
            double s = VolMult * sig;
            double lo = SMinTicks * TickSize, hi = SMaxTicks * TickSize;
            if (s < lo) s = lo;
            if (s > hi) s = hi;
            return s;
        }

        // the value that would extend the anchor on this bar, per AnchorMode
        private double CandidateExtreme(bool up)
        {
            if (AnchorMode == 1)
                return up ? High[0] : Low[0];
            if (AnchorMode == 2)
            {
                // close-confirmed high/low: use the extreme only when the close agrees
                // with the trend direction on this bar, else fall back to the close
                bool agrees = up ? Close[0] >= Open[0] : Close[0] <= Open[0];
                if (agrees) return up ? High[0] : Low[0];
            }
            return Close[0];
        }

        private void UpdateSolarWave()
        {
            UpdateVol();
            double px = Close[0];
            signalTradeVal = 0;
            int ev = 0;

            if (!initialized)
            {
                initialized = true;
                isUp = StartUp; anchor = CandidateExtreme(StartUp);
                sEff = ResolveS();
                weak = false; barsSinceExtreme = 0; nextWeakBar = int.MinValue; wave = 1;
            }
            else
            {
                double cand = CandidateExtreme(isUp);
                if (isUp)
                {
                    if (cand >= anchor)
                    {
                        if (cand > anchor) ev = 1;
                        anchor = cand;
                    }
                    else if (px < anchor - sEff)
                    {
                        isUp = false; ev = 2;
                        sEff = ResolveS();                 // frozen at trend birth
                        anchor = CandidateExtreme(false);
                    }
                }
                else
                {
                    if (cand <= anchor)
                    {
                        if (cand < anchor) ev = 1;
                        anchor = cand;
                    }
                    else if (px > anchor + sEff)
                    {
                        isUp = true; ev = 2;
                        sEff = ResolveS();
                        anchor = CandidateExtreme(true);
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

            trailingStopVal = isUp ? anchor - sEff : anchor + sEff;
            double exitDist = ExitMultiplier > 0 ? ExitMultiplier * TickSize : sEff;
            exitLevelVal = isUp ? anchor - exitDist : anchor + exitDist;
            signalWaveVal = (isUp ? 1 : -1) * wave;
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

            // Position exit uses exitLevelVal. With ExitMultiplier <= 0 this level IS the
            // reversal level, reproducing the vendor policy exactly. With a smaller
            // ExitMultiplier the position leaves early and the strategy waits flat until
            // the trend itself flips at the (larger) reversal distance.
            double xl = exitLevelVal;
            if (!double.IsNaN(xl))
            {
                if (Position.MarketPosition == MarketPosition.Long && Close[0] <= xl)
                {
                    ExitLong("L-SolarExit", "Long");
                    return;
                }
                if (Position.MarketPosition == MarketPosition.Short && Close[0] >= xl)
                {
                    ExitShort("S-SolarExit", "Short");
                    return;
                }
            }

            if (Position.MarketPosition != MarketPosition.Flat)
                return;

            int sig = signalTradeVal;
            bool L  = sig > 0 && (EntrySignalType == 0 || sig == EntrySignalType);
            bool Sh = sig < 0 && (EntrySignalType == 0 || -sig == EntrySignalType);
            if (EnableLong && L)        EnterLong(DefaultQuantity, "Long");
            else if (EnableShort && Sh) EnterShort(DefaultQuantity, "Short");
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
        [Display(Name = "Trend Multiplier", Order = 1, GroupName = "Core")]
        public double TrendMultiplier { get; set; }

        [NinjaScriptProperty] [Range(1, 4000)]
        [Display(Name = "Stop Multiplier", Order = 2, GroupName = "Core")]
        public double StopMultiplier { get; set; }

        [NinjaScriptProperty] [Range(1, 100)]
        [Display(Name = "Slowdown Scan", Order = 3, GroupName = "Core")]
        public int SlowdownScan { get; set; }

        [NinjaScriptProperty] [Range(1, 100)]
        [Display(Name = "Weak-Weak Split", Order = 4, GroupName = "Core")]
        public int WeakWeakSplit { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Start Up", Order = 5, GroupName = "Core")]
        public bool StartUp { get; set; }

        [NinjaScriptProperty] [Range(0, 2)]
        [Display(Name = "Anchor Mode", Order = 1, GroupName = "Axes")]
        public int AnchorMode { get; set; }

        [NinjaScriptProperty] [Range(0, 1)]
        [Display(Name = "Threshold Mode", Order = 2, GroupName = "Axes")]
        public int ThresholdMode { get; set; }

        [NinjaScriptProperty] [Range(30, 20000)]
        [Display(Name = "Vol Period", Order = 3, GroupName = "Axes")]
        public int VolPeriod { get; set; }

        [NinjaScriptProperty] [Range(0.5, 200.0)]
        [Display(Name = "Vol Mult", Order = 4, GroupName = "Axes")]
        public double VolMult { get; set; }

        [NinjaScriptProperty] [Range(1, 4000)]
        [Display(Name = "S Min Ticks", Order = 5, GroupName = "Axes")]
        public int SMinTicks { get; set; }

        [NinjaScriptProperty] [Range(1, 8000)]
        [Display(Name = "S Max Ticks", Order = 6, GroupName = "Axes")]
        public int SMaxTicks { get; set; }

        [NinjaScriptProperty] [Range(0, 4000)]
        [Display(Name = "Exit Multiplier", Order = 7, GroupName = "Axes")]
        public int ExitMultiplier { get; set; }

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
