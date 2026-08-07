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

// SolarWaveOpenV4 - SolarWaveOpenV3 plus ThresholdMode 2 (price-proportional).
//
// H-014, the decisive control on H-006. If a threshold proportional to PRICE performs
// like one proportional to VOLATILITY, then "volatility normalisation" is not a
// mechanism - it is just "a threshold that varies over time", and the H-006 mechanism
// claim dies. DC02 showed price-normalisation sits between fixed-tick and vol in
// stabilising the overshoot ratio, so this is a live possibility, not a formality.
//
//   ThresholdMode 0 : S = StopMultiplier * tick                  (vendor behaviour)
//   ThresholdMode 1 : S = VolMult * sigma_birth                  (H-006)
//   ThresholdMode 2 : S = PriceBp/10000 * close_birth            (H-014)
//
// Modes 1 and 2 both sample ONCE at trend birth so the trailing stop stays monotone.
// Class renamed from V3 per the campaign's hot-reload rule; V3 is left untouched.
namespace NinjaTrader.NinjaScript.Strategies
{
    public class SolarWaveOpenV4 : Strategy
    {
        private double anchor;
        private double sEff;
        private bool   isUp;
        private bool   weak;
        private int    barsSinceExtreme;
        private int    nextWeakBar;
        private int    wave;
        private bool   initialized;

        private double trailingStopVal;
        private double exitLevelVal;
        private int    signalTradeVal;
        private int    signalWaveVal;

        private double volSum;
        private double prevClose;
        private int    volCount;

        private StringBuilder log;
        private int execCount;

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = "Open directional-change engine: fixed / volatility / price thresholds";
                Name        = "SolarWaveOpenV4";

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
                VolPeriod      = 460;
                VolMult        = 18.0;
                PriceBp        = 25.0;
                SMinTicks      = 40;
                SMaxTicks      = 1200;
                ExitMultiplier = 0;

                EntrySignalType = 1;
                EnableLong      = true;
                EnableShort     = true;

                UseTimeFilter = false;
                StartTime     = 180000;
                EndTime       = 163000;

                ExportDir = "";
                Tag       = "v4";
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
            string sym = Instrument != null ? Instrument.MasterInstrument.Name : "UNK";
            string file = string.Format(CultureInfo.InvariantCulture,
                "{0}__{1}_tf{2}_sm{3}_am{4}_th{5}_vp{6}_vm{7}_bp{8}_xm{9}_{10}_slip{11}.csv",
                Tag, sym, tf, (int)StopMultiplier, AnchorMode, ThresholdMode, VolPeriod,
                VolMult.ToString("0.##", CultureInfo.InvariantCulture),
                PriceBp.ToString("0.##", CultureInfo.InvariantCulture),
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
                        "# TM={0} SM={1} SS={2} WWS={3} anchor={4} thresh={5} volperiod={6} volmult={7} pricebp={8} smin={9} smax={10} exitmult={11} EST={12} TF={13} end={14} slip={15} instrument={16} tick={17} pointvalue={18} period={19} execs={20}",
                        TrendMultiplier, StopMultiplier, SlowdownScan, WeakWeakSplit,
                        AnchorMode, ThresholdMode, VolPeriod, VolMult, PriceBp,
                        SMinTicks, SMaxTicks, ExitMultiplier, EntrySignalType,
                        UseTimeFilter, EndTime, Slippage,
                        Instrument != null ? Instrument.FullName : "?",
                        TickSize,
                        Instrument != null ? Instrument.MasterInstrument.PointValue : 0,
                        BarsPeriod != null ? BarsPeriod.Value : 0, execCount));
                    w.WriteLine("n,time,bar,name,order_action,market_position,price,qty,commission,wave,signal");
                    w.Write(log.ToString());
                    w.Flush();
                }
            }
            catch (Exception ex)
            {
                Print("SolarWaveOpenV4 export failed: " + ex.Message);
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

        private double CausalSigma()
        {
            if (volCount < 30) return double.NaN;
            return volSum / volCount;
        }

        private void UpdateVol()
        {
            if (ThresholdMode != 1) { prevClose = Close[0]; return; }
            if (!double.IsNaN(prevClose))
            {
                volSum += Math.Abs(Close[0] - prevClose); volCount++;
                if (volCount > VolPeriod)
                {
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
            double s;
            if (ThresholdMode == 1)
            {
                double sig = CausalSigma();
                if (double.IsNaN(sig) || sig <= 0) return StopMultiplier * TickSize;
                s = VolMult * sig;
            }
            else if (ThresholdMode == 2)
            {
                // price-proportional: PriceBp basis points of the current close.
                // Uses only the closed bar, so it is causal by construction.
                s = PriceBp / 10000.0 * Close[0];
            }
            else
            {
                return StopMultiplier * TickSize;
            }
            double lo = SMinTicks * TickSize, hi = SMaxTicks * TickSize;
            if (s < lo) s = lo;
            if (s > hi) s = hi;
            // snap to the tick grid so the ladder stays on tradable prices
            return Math.Round(s / TickSize) * TickSize;
        }

        private double CandidateExtreme(bool up)
        {
            if (AnchorMode == 1) return up ? High[0] : Low[0];
            if (AnchorMode == 2)
            {
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
                    if (cand >= anchor) { if (cand > anchor) ev = 1; anchor = cand; }
                    else if (px < anchor - sEff)
                    {
                        isUp = false; ev = 2; sEff = ResolveS(); anchor = CandidateExtreme(false);
                    }
                }
                else
                {
                    if (cand <= anchor) { if (cand < anchor) ev = 1; anchor = cand; }
                    else if (px > anchor + sEff)
                    {
                        isUp = true; ev = 2; sEff = ResolveS(); anchor = CandidateExtreme(true);
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
            if (BarsInProgress != 0) return;
            UpdateSolarWave();
            if (CurrentBar < BarsRequiredToTrade) return;

            if (!IsAllowedTime(ToTime(Time[0])))
            {
                if (Position.MarketPosition == MarketPosition.Long)
                    ExitLong("L-TimeExit", "Long");
                else if (Position.MarketPosition == MarketPosition.Short)
                    ExitShort("S-TimeExit", "Short");
                return;
            }

            double xl = exitLevelVal;
            if (!double.IsNaN(xl))
            {
                if (Position.MarketPosition == MarketPosition.Long && Close[0] <= xl)
                { ExitLong("L-SolarExit", "Long"); return; }
                if (Position.MarketPosition == MarketPosition.Short && Close[0] >= xl)
                { ExitShort("S-SolarExit", "Short"); return; }
            }

            if (Position.MarketPosition != MarketPosition.Flat) return;

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

        [NinjaScriptProperty] [Range(0, 2)]
        [Display(Name = "Threshold Mode", Order = 2, GroupName = "Axes")]
        public int ThresholdMode { get; set; }

        [NinjaScriptProperty] [Range(30, 20000)]
        [Display(Name = "Vol Period", Order = 3, GroupName = "Axes")]
        public int VolPeriod { get; set; }

        [NinjaScriptProperty] [Range(0.5, 200.0)]
        [Display(Name = "Vol Mult", Order = 4, GroupName = "Axes")]
        public double VolMult { get; set; }

        [NinjaScriptProperty] [Range(0.5, 500.0)]
        [Display(Name = "Price Bp", Order = 5, GroupName = "Axes")]
        public double PriceBp { get; set; }

        [NinjaScriptProperty] [Range(1, 4000)]
        [Display(Name = "S Min Ticks", Order = 6, GroupName = "Axes")]
        public int SMinTicks { get; set; }

        [NinjaScriptProperty] [Range(1, 8000)]
        [Display(Name = "S Max Ticks", Order = 7, GroupName = "Axes")]
        public int SMaxTicks { get; set; }

        [NinjaScriptProperty] [Range(0, 4000)]
        [Display(Name = "Exit Multiplier", Order = 8, GroupName = "Axes")]
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
