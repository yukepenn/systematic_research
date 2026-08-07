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

// SolarWaveSleeveV1 - controlled signal architectures C0..C4 on the complete open model.
//
// The full Type-2 recovery (RE02) makes this possible: all three signal types are now
// generated natively with zero vendor dependency, so sleeves can be composed and each
// one's incremental value measured against the Type-1 core.
//
// A Python attribution on the exact model (research/09_type0/TYPE0_ATTRIBUTION.md) found
// Type-3 re-entries worth +$73.55 per marginal trade and a monotone rise in per-trade
// economics with the wave index. This class exists to confirm or kill that in the engine.
//
//   SignalMask   bitmask of permitted ENTRY types: 1=T1, 2=T2, 4=T3 (so 5 = T1+T3, 7 = all)
//   MaxReentries max T2/T3 entries per trend episode (0 = none, i.e. pure T1 core)
//   MinWave      minimum wave index at entry (1 = no filter)
//   MaxWave      maximum wave index at entry (0 = no cap)
//
// SignalMask=1, MaxReentries=0 reproduces the Type-1 core exactly - the gate test.
namespace NinjaTrader.NinjaScript.Strategies
{
    public class SolarWaveSleeveV1 : Strategy
    {
        private double anchor, sEff;
        private bool   isUp, weak, initialized;
        private int    barsSinceExtreme, nextWeakBar, wave;
        private double trailingStopVal;
        private int    signalTradeVal, signalWaveVal;

        private double volSum, prevClose;
        private int    volCount;

        private int    episode;          // increments on every flip
        private int    entryEpisode;     // episode in which the open position was entered
        private int    reentriesUsed;
        private int    lastEpisodeSeen;

        private StringBuilder log;
        private int execCount;

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = "Controlled signal architectures on the complete open Solar model";
                Name        = "SolarWaveSleeveV1";

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
                PullbackSplit   = 10;
                PullbackEarly   = true;
                StartUp         = false;

                ThresholdMode = 0;
                VolPeriod     = 460;
                VolMult       = 18.0;
                SMinTicks     = 40;
                SMaxTicks     = 1200;

                SignalMask   = 1;
                MaxReentries = 0;
                MinWave      = 1;
                MaxWave      = 0;

                EnableLong  = true;
                EnableShort = true;

                UseTimeFilter = false;
                StartTime     = 180000;
                EndTime       = 163000;

                ExportDir = "";
                Tag       = "sleeve";
            }
            else if (State == State.Configure)
            {
                log = new StringBuilder(1 << 20); execCount = 0;
            }
            else if (State == State.DataLoaded)
            {
                initialized = false; volSum = 0; volCount = 0; prevClose = double.NaN;
                episode = 0; entryEpisode = -1; reentriesUsed = 0; lastEpisodeSeen = -1;
                hasCrossed = false; nextPB = int.MinValue;
            }
            else if (State == State.Terminated) Flush();
        }

        private string BuildPath()
        {
            int tf = BarsPeriod != null ? BarsPeriod.Value : 0;
            string sym = Instrument != null ? Instrument.MasterInstrument.Name : "UNK";
            string file = string.Format(CultureInfo.InvariantCulture,
                "{0}__{1}_tf{2}_sm{3}_th{4}_vm{5}_mask{6}_re{7}_w{8}-{9}_slip{10}.csv",
                Tag, sym, tf, (int)StopMultiplier, ThresholdMode,
                VolMult.ToString("0.##", CultureInfo.InvariantCulture),
                SignalMask, MaxReentries, MinWave, MaxWave, Slippage);
            return Path.Combine(ExportDir, file);
        }

        private void Flush()
        {
            if (string.IsNullOrEmpty(ExportDir) || log == null) return;
            try
            {
                if (!Directory.Exists(ExportDir)) Directory.CreateDirectory(ExportDir);
                using (StreamWriter w = new StreamWriter(BuildPath(), false))
                {
                    w.WriteLine(string.Format(CultureInfo.InvariantCulture,
                        "# TM={0} SM={1} SS={2} WWS={3} PS={4} PE={5} thresh={6} volmult={7} mask={8} reentries={9} minwave={10} maxwave={11} slip={12} instrument={13} period={14} execs={15}",
                        TrendMultiplier, StopMultiplier, SlowdownScan, WeakWeakSplit,
                        PullbackSplit, PullbackEarly, ThresholdMode, VolMult, SignalMask,
                        MaxReentries, MinWave, MaxWave, Slippage,
                        Instrument != null ? Instrument.FullName : "?",
                        BarsPeriod != null ? BarsPeriod.Value : 0, execCount));
                    w.WriteLine("n,time,bar,name,order_action,market_position,price,qty,commission,wave,signal");
                    w.Write(log.ToString()); w.Flush();
                }
            }
            catch (Exception ex) { Print("SolarWaveSleeveV1 export failed: " + ex.Message); }
        }

        protected override void OnExecutionUpdate(Execution execution, string executionId,
            double price, int quantity, MarketPosition marketPosition, string orderId, DateTime time)
        {
            if (log == null || execution == null || execution.Order == null) return;
            log.AppendLine(string.Format(CultureInfo.InvariantCulture,
                "{0},{1:yyyy-MM-ddTHH:mm:ss},{2},{3},{4},{5},{6},{7},{8},{9},{10}",
                execCount++, time, CurrentBar, execution.Name, execution.Order.OrderAction,
                marketPosition, price, quantity, execution.Commission, signalWaveVal, signalTradeVal));
        }

        private double CausalSigma() { return volCount < 30 ? double.NaN : volSum / volCount; }

        private void UpdateVol()
        {
            if (ThresholdMode != 1) { prevClose = Close[0]; return; }
            if (!double.IsNaN(prevClose))
            {
                volSum += Math.Abs(Close[0] - prevClose); volCount++;
                if (volCount > VolPeriod)
                {
                    int n = Math.Min(VolPeriod, CurrentBar); double s = 0;
                    for (int i = 0; i < n; i++) s += Math.Abs(Close[i] - Close[i + 1]);
                    volSum = s; volCount = n;
                }
            }
            prevClose = Close[0];
        }

        private double ResolveS()
        {
            if (ThresholdMode != 1) return StopMultiplier * TickSize;
            double sig = CausalSigma();
            if (double.IsNaN(sig) || sig <= 0) return StopMultiplier * TickSize;
            double s = VolMult * sig;
            double lo = SMinTicks * TickSize, hi = SMaxTicks * TickSize;
            if (s < lo) s = lo; if (s > hi) s = hi;
            return Math.Round(s / TickSize) * TickSize;
        }

        // --- Type-2 state, exactly as recovered in RE02 ---
        private bool hasCrossed;
        private int  nextPB;

        private void UpdateSolarWave()
        {
            UpdateVol();
            double px = Close[0];
            signalTradeVal = 0;
            int ev = 0;

            if (!initialized)
            {
                initialized = true; isUp = StartUp; anchor = px; sEff = ResolveS();
                weak = false; barsSinceExtreme = 0; nextWeakBar = int.MinValue; wave = 1;
            }
            else
            {
                if (isUp)
                {
                    if (px >= anchor) { if (px > anchor) ev = 1; anchor = px; }
                    else if (px < anchor - sEff) { isUp = false; ev = 2; sEff = ResolveS(); anchor = px; }
                }
                else
                {
                    if (px <= anchor) { if (px < anchor) ev = 1; anchor = px; }
                    else if (px > anchor + sEff) { isUp = true; ev = 2; sEff = ResolveS(); anchor = px; }
                }
            }

            bool isT3 = false;
            if (ev == 2)
            {
                weak = false; barsSinceExtreme = 0; wave = 1; episode++;
                signalTradeVal = isUp ? 1 : -1;
                nextWeakBar = CurrentBar + WeakWeakSplit;
                hasCrossed = false; nextPB = int.MinValue;      // flip resets the T2 latch
            }
            else
            {
                if (ev == 1)
                {
                    barsSinceExtreme = 0;
                    if (weak) { wave++; weak = false; isT3 = true;
                                signalTradeVal = isUp ? 3 : -3;
                                nextWeakBar = CurrentBar + WeakWeakSplit; }
                }
                else
                {
                    barsSinceExtreme++;
                    if (!weak && barsSinceExtreme >= SlowdownScan && CurrentBar >= nextWeakBar)
                    { weak = true; nextWeakBar = CurrentBar + WeakWeakSplit; }
                }

                // Type 2: intrabar excursion beyond TrendVector, sticky latch, PS spacing
                double V  = TrendMultiplier * TickSize;
                double tv = isUp ? anchor - V : anchor + V;
                double ext = isUp ? Low[0] : High[0];
                bool beyond = isUp ? ext <  tv : ext >  tv;
                bool inside = isUp ? ext >  tv : ext <  tv;
                if (PullbackEarly)
                {
                    if (beyond && !hasCrossed && CurrentBar > nextPB)
                    { signalTradeVal = isUp ? 2 : -2; nextPB = CurrentBar + PullbackSplit; }
                    if (beyond) hasCrossed = true; else if (inside) hasCrossed = false;
                }
                if (isT3) hasCrossed = false;                   // the one wave-layer coupling
            }

            trailingStopVal = isUp ? anchor - sEff : anchor + sEff;
            signalWaveVal   = (isUp ? 1 : -1) * wave;
        }

        protected override void OnBarUpdate()
        {
            if (BarsInProgress != 0) return;
            UpdateSolarWave();
            if (CurrentBar < BarsRequiredToTrade) return;

            if (episode != lastEpisodeSeen) { reentriesUsed = 0; lastEpisodeSeen = episode; }

            if (!IsAllowedTime(ToTime(Time[0])))
            {
                if (Position.MarketPosition == MarketPosition.Long)  ExitLong("L-TimeExit", "Long");
                else if (Position.MarketPosition == MarketPosition.Short) ExitShort("S-TimeExit", "Short");
                return;
            }

            double ts = trailingStopVal;
            if (Position.MarketPosition == MarketPosition.Long && Close[0] <= ts)
            { ExitLong("L-SolarExit", "Long"); return; }
            if (Position.MarketPosition == MarketPosition.Short && Close[0] >= ts)
            { ExitShort("S-SolarExit", "Short"); return; }
            if (Position.MarketPosition != MarketPosition.Flat) return;

            int sig = signalTradeVal;
            if (sig == 0) return;
            int k = Math.Abs(sig);
            int bit = k == 1 ? 1 : (k == 2 ? 2 : 4);
            if ((SignalMask & bit) == 0) return;

            if (k != 1)
            {
                if (reentriesUsed >= MaxReentries) return;
                int wv = Math.Abs(signalWaveVal);
                if (wv < MinWave) return;
                if (MaxWave > 0 && wv > MaxWave) return;
            }

            bool L = sig > 0, Sh = sig < 0;
            if (EnableLong && L)
            { if (k != 1) reentriesUsed++; entryEpisode = episode; EnterLong(DefaultQuantity, "Long"); }
            else if (EnableShort && Sh)
            { if (k != 1) reentriesUsed++; entryEpisode = episode; EnterShort(DefaultQuantity, "Short"); }
        }

        private bool IsAllowedTime(int t)
        {
            if (!UseTimeFilter) return true;
            if (StartTime <= EndTime) return t >= StartTime && t <= EndTime;
            return t >= StartTime || t <= EndTime;
        }

        #region Properties
        [NinjaScriptProperty][Range(1,1000)][Display(Name="Trend Multiplier",Order=1,GroupName="Core")]
        public double TrendMultiplier { get; set; }
        [NinjaScriptProperty][Range(1,4000)][Display(Name="Stop Multiplier",Order=2,GroupName="Core")]
        public double StopMultiplier { get; set; }
        [NinjaScriptProperty][Range(1,100)][Display(Name="Slowdown Scan",Order=3,GroupName="Core")]
        public int SlowdownScan { get; set; }
        [NinjaScriptProperty][Range(1,100)][Display(Name="Weak-Weak Split",Order=4,GroupName="Core")]
        public int WeakWeakSplit { get; set; }
        [NinjaScriptProperty][Range(1,100)][Display(Name="Pullback Split",Order=5,GroupName="Core")]
        public int PullbackSplit { get; set; }
        [NinjaScriptProperty][Display(Name="Pullback Early",Order=6,GroupName="Core")]
        public bool PullbackEarly { get; set; }
        [NinjaScriptProperty][Display(Name="Start Up",Order=7,GroupName="Core")]
        public bool StartUp { get; set; }

        [NinjaScriptProperty][Range(0,1)][Display(Name="Threshold Mode",Order=1,GroupName="Threshold")]
        public int ThresholdMode { get; set; }
        [NinjaScriptProperty][Range(30,20000)][Display(Name="Vol Period",Order=2,GroupName="Threshold")]
        public int VolPeriod { get; set; }
        [NinjaScriptProperty][Range(0.5,200.0)][Display(Name="Vol Mult",Order=3,GroupName="Threshold")]
        public double VolMult { get; set; }
        [NinjaScriptProperty][Range(1,4000)][Display(Name="S Min Ticks",Order=4,GroupName="Threshold")]
        public int SMinTicks { get; set; }
        [NinjaScriptProperty][Range(1,8000)][Display(Name="S Max Ticks",Order=5,GroupName="Threshold")]
        public int SMaxTicks { get; set; }

        [NinjaScriptProperty][Range(1,7)][Display(Name="Signal Mask",Order=1,GroupName="Sleeve")]
        public int SignalMask { get; set; }
        [NinjaScriptProperty][Range(0,20)][Display(Name="Max Reentries",Order=2,GroupName="Sleeve")]
        public int MaxReentries { get; set; }
        [NinjaScriptProperty][Range(1,50)][Display(Name="Min Wave",Order=3,GroupName="Sleeve")]
        public int MinWave { get; set; }
        [NinjaScriptProperty][Range(0,50)][Display(Name="Max Wave",Order=4,GroupName="Sleeve")]
        public int MaxWave { get; set; }

        [NinjaScriptProperty][Display(Name="Enable Long",Order=1,GroupName="Entry")]
        public bool EnableLong { get; set; }
        [NinjaScriptProperty][Display(Name="Enable Short",Order=2,GroupName="Entry")]
        public bool EnableShort { get; set; }
        [NinjaScriptProperty][Display(Name="Use Time Filter",Order=1,GroupName="Time")]
        public bool UseTimeFilter { get; set; }
        [NinjaScriptProperty][Range(0,235959)][Display(Name="Start Time",Order=2,GroupName="Time")]
        public int StartTime { get; set; }
        [NinjaScriptProperty][Range(0,235959)][Display(Name="End Time",Order=3,GroupName="Time")]
        public int EndTime { get; set; }
        [NinjaScriptProperty][Display(Name="Export Dir",Order=1,GroupName="Export")]
        public string ExportDir { get; set; }
        [NinjaScriptProperty][Display(Name="Tag",Order=2,GroupName="Export")]
        public string Tag { get; set; }
        #endregion
    }
}
