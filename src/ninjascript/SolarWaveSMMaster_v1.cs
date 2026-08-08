// SolarWaveSMMaster_v1 — DAYONLY_DUAL6040 consolidated master (SMV2M, seq 371).
//
// ONE strategy, ONE consolidated MNQ target, day-only, no B1:
//     M = round( KSolar * Tpp + KBmom * B ), clamp +/-13     (max reachable ~12)
//     Tpp = clamp(round(T * m * s * TiltRescale), +/-13)
//       T = clamp(round(10 * mean member pending pos), +/-10)   (13 virtual V3 members)
//       m = TiltMult  iff T != 0 and prior-session SMA(TiltSma) state == sign(T)
//       s = ShortHalf iff T < 0  and prior-session state is UP        (c1_50, SMV2E promoted)
//     B = frozen W8-1 B-MOM virtual position in {-1,0,+1} (14d slot bands + RTH VWAP, flat >= 15:57)
// Frozen constants (runs/SMV2M_MASTER_BUILD/spec.yaml, derived from committed rerank curves):
//     KSolar = 0.728654   KBmom = 2.934159   TiltRescale = 0.9026
// Ops (frozen): decision bars (NT end-stamps) 16:30-18:00 no position increases and no
// reversal entries; >= 16:39 target 0 (fills ~16:42, flat before the 16:45 margin cliff);
// IsExitOnSessionCloseStrategy backstop for early closes.
// ATTACH TO: MNQ ##-## 3-minute (execution). SignalInstrument NQ merge-back-adjusted drives signals.
// Python twin: runs/SMV2M_MASTER_BUILD/twin.py — dev (<=2026-05-31): net $179,289, Sharpe 1.19,
// maxDD -$16,821 (EOD), 25,452 contract-fills. HISTORICAL research result, not a forward guarantee.
//
// SAFETY: research/backtest only. FAILS CLOSED in realtime: OnBarUpdate exits before any order
// submission when State == State.Realtime. Never enable on Sim101/live. HOT-RELOAD: version class.

#region Using declarations
using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Globalization;
using System.IO;
using System.Text;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
#endregion

namespace NinjaTrader.NinjaScript.Strategies
{
    public class SolarWaveSMMaster_v1 : Strategy
    {
        private const int NMEM = 13;
        private static readonly double[] VolMults =
            { 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30 };

        private double volSum; private int volCount; private double prevClose = double.NaN;

        private bool[] mIsUp = new bool[NMEM];
        private double[] mAnchor = new double[NMEM];
        private double[] mSEff = new double[NMEM];
        private int[] mSig = new int[NMEM];
        private int[] mPos = new int[NMEM];
        private int[] mPending = new int[NMEM];
        private bool initialized;

        private readonly List<double> sessCloses = new List<double>();
        private int tiltState;

        private readonly Dictionary<int, List<double>> slotHist = new Dictionary<int, List<double>>();
        private readonly Dictionary<int, double> todaySlots = new Dictionary<int, double>();
        private double open0930, vwapPV, vwapV; private bool rthOpen;
        private int bmomPos; private int rthDayCount;

        private StreamWriter barLog;
        private StringBuilder fillLog;
        private int execCount;
        private int lastTarget;

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Name = "SolarWaveSMMaster_v1";
                Calculate = Calculate.OnBarClose;
                IsExitOnSessionCloseStrategy = true;
                ExitOnSessionCloseSeconds = 30;
                BarsRequiredToTrade = 20;
                IsInstantiatedOnEachOptimizationIteration = false;
                EntriesPerDirection = 100;
                EntryHandling = EntryHandling.AllEntries;
                DefaultQuantity = 1;
                StartBehavior = StartBehavior.WaitUntilFlat;
                TimeInForce = TimeInForce.Gtc;
                RealtimeErrorHandling = RealtimeErrorHandling.StopCancelClose;
                MaximumBarsLookBack = MaximumBarsLookBack.TwoHundredFiftySix;

                SignalInstrument = "NQ 09-26";
                StopMultiplier = 179; SlowdownScan = 5; WeakWeakSplit = 10;
                VolPeriod = 460; SMinTicks = 40; SMaxTicks = 1200;
                TiltSma = 50; TiltMult = 1.25; TiltRescale = 0.9026; ShortHalf = 0.5;
                KSolar = 0.728654; KBmom = 2.934159; BmomBandDays = 14;
                ExportDir = ""; Tag = "smm_v1";
            }
            else if (State == State.Configure)
            {
                AddDataSeries(SignalInstrument, BarsPeriodType.Minute, 3);
                fillLog = new StringBuilder(1 << 20);
                execCount = 0;
            }
            else if (State == State.DataLoaded)
            {
                volSum = 0; volCount = 0; prevClose = double.NaN;
                initialized = false; tiltState = 0; bmomPos = 0; rthDayCount = 0;
                rthOpen = false; lastTarget = 0;
            }
            else if (State == State.Terminated)
            {
                Flush();
            }
        }

        private double CausalSigma()
        {
            if (volCount < 30) return double.NaN;
            return volSum / volCount;
        }
        private void UpdateVol()
        {
            double c0 = Closes[1][0];
            if (!double.IsNaN(prevClose))
            {
                volSum += Math.Abs(c0 - prevClose); volCount++;
                if (volCount > VolPeriod)
                {
                    int n = Math.Min(VolPeriod, CurrentBars[1]);
                    double s = 0;
                    for (int i = 0; i < n; i++)
                        s += Math.Abs(Closes[1][i] - Closes[1][i + 1]);
                    volSum = s; volCount = n;
                }
            }
            prevClose = c0;
        }
        private double ResolveS(double volMult)
        {
            double sig = CausalSigma();
            double ts = BarsArray[1].Instrument.MasterInstrument.TickSize;
            if (double.IsNaN(sig) || sig <= 0) return StopMultiplier * ts;
            double s = volMult * sig;
            double lo = SMinTicks * ts, hi = SMaxTicks * ts;
            if (s < lo) s = lo;
            if (s > hi) s = hi;
            return s;
        }

        private void UpdateMachine(int m)
        {
            double px = Closes[1][0];
            mSig[m] = 0;
            if (!initialized)
            {
                mIsUp[m] = false; mAnchor[m] = px; mSEff[m] = ResolveS(VolMults[m]);
                return;
            }
            if (mIsUp[m])
            {
                if (px >= mAnchor[m]) mAnchor[m] = px;
                else if (px < mAnchor[m] - mSEff[m])
                { mIsUp[m] = false; mSEff[m] = ResolveS(VolMults[m]); mAnchor[m] = px; mSig[m] = -1; }
            }
            else
            {
                if (px <= mAnchor[m]) mAnchor[m] = px;
                else if (px > mAnchor[m] + mSEff[m])
                { mIsUp[m] = true; mSEff[m] = ResolveS(VolMults[m]); mAnchor[m] = px; mSig[m] = 1; }
            }
        }

        private void Decide(int m)
        {
            if (CurrentBars[1] < BarsRequiredToTrade) { mPending[m] = mPos[m]; return; }
            double xl = mIsUp[m] ? mAnchor[m] - mSEff[m] : mAnchor[m] + mSEff[m];
            if (mPos[m] > 0 && Closes[1][0] <= xl) { mPending[m] = 0; return; }
            if (mPos[m] < 0 && Closes[1][0] >= xl) { mPending[m] = 0; return; }
            if (mPos[m] != 0) { mPending[m] = mPos[m]; return; }
            mPending[m] = mSig[m];
        }

        private void BmomBar(int hm, bool sessEnd)
        {
            if (hm == 93300)
            {
                open0930 = Opens[1][0]; vwapPV = 0; vwapV = 0; rthOpen = true;
                todaySlots.Clear(); bmomPos = 0;
            }
            if (!rthOpen || hm < 93300 || hm > 160000)
            {
                if (sessEnd) EndRthDay();
                return;
            }
            double c = Closes[1][0], v = Volumes[1][0];
            vwapPV += c * v; vwapV += v;
            double vwap = vwapV > 0 ? vwapPV / vwapV : c;
            todaySlots[hm] = Math.Abs(c - open0930);

            if (hm <= 155400 && rthDayCount >= BmomBandDays)
            {
                List<double> past;
                if (slotHist.TryGetValue(hm, out past) && past.Count >= 1)
                {
                    int k = Math.Min(BmomBandDays, past.Count);
                    double s = 0;
                    for (int i = past.Count - k; i < past.Count; i++) s += past[i];
                    double mtod = s / k;
                    double upper = open0930 + mtod, lower = open0930 - mtod;
                    int sig = 0;
                    if (c > Math.Max(upper, vwap)) sig = 1;
                    else if (c < Math.Min(lower, vwap)) sig = -1;
                    if (sig != 0) bmomPos = sig;
                }
            }
            if (hm >= 155700) bmomPos = 0;
            if (sessEnd) EndRthDay();
        }
        private void EndRthDay()
        {
            if (!rthOpen) return;
            foreach (var kv in todaySlots)
            {
                List<double> lst;
                if (!slotHist.TryGetValue(kv.Key, out lst))
                { lst = new List<double>(); slotHist[kv.Key] = lst; }
                lst.Add(kv.Value);
                if (lst.Count > 60) lst.RemoveAt(0);
            }
            rthDayCount++; rthOpen = false;
        }

        private int PhysicalPosition()
        {
            if (Position.MarketPosition == MarketPosition.Long) return Position.Quantity;
            if (Position.MarketPosition == MarketPosition.Short) return -Position.Quantity;
            return 0;
        }

        private void SubmitNetChange(int tgt)
        {
            int c = PhysicalPosition();
            if (tgt == c) return;
            if (tgt == 0)
            {
                if (c > 0) ExitLong(0, c, "XL", "");
                else       ExitShort(0, -c, "XS", "");
            }
            else if (tgt > 0)
            {
                if (c < 0)        EnterLong(0, tgt, "L");          // managed auto-reversal
                else if (tgt > c) EnterLong(0, tgt - c, "L");
                else              ExitLong(0, c - tgt, "XL", "");
            }
            else
            {
                if (c > 0)        EnterShort(0, -tgt, "S");        // managed auto-reversal
                else if (tgt < c) EnterShort(0, c - tgt, "S");
                else              ExitShort(0, tgt - c, "XS", "");
            }
        }

        protected override void OnBarUpdate()
        {
            if (BarsInProgress != 1)
                return;
            if (CurrentBars[1] < 1)
                return;

            // 1. virtual member fills at this bar's open
            for (int m = 0; m < NMEM; m++) mPos[m] = mPending[m];

            // 2. shared sigma + member machines on this bar's close
            UpdateVol();
            for (int m = 0; m < NMEM; m++) UpdateMachine(m);
            if (!initialized) initialized = true;
            for (int m = 0; m < NMEM; m++) Decide(m);

            bool sessEnd = BarsArray[1].IsLastBarOfSession;
            int hm = ToTime(Times[1][0]);
            BmomBar(hm, sessEnd);

            // 3. session end: members zeroed; HTF state from session closes INCLUDING this one,
            //    effective from the next session (matches twin rolling(50).shift(1))
            if (sessEnd)
            {
                for (int m = 0; m < NMEM; m++) { mPos[m] = 0; mPending[m] = 0; }
                sessCloses.Add(Closes[1][0]);
                if (sessCloses.Count >= TiltSma)
                {
                    double s = 0;
                    for (int i = sessCloses.Count - TiltSma; i < sessCloses.Count; i++) s += sessCloses[i];
                    tiltState = Math.Sign(Closes[1][0] - s / TiltSma);
                }
                if (sessCloses.Count > 600) sessCloses.RemoveAt(0);
            }

            // 4. consolidated target: T -> Tpp (tilt + c1_50) -> M
            int sumNext = 0;
            for (int m = 0; m < NMEM; m++) sumNext += mPending[m];
            int T = Math.Max(-10, Math.Min(10, (int)Math.Round(sumNext / 13.0 * 10.0, MidpointRounding.AwayFromZero)));
            double mm = (T != 0 && tiltState != 0 && Math.Sign(T) == tiltState) ? TiltMult : 1.0;
            double ss = (T < 0 && tiltState > 0) ? ShortHalf : 1.0;
            int Tpp = Math.Max(-13, Math.Min(13, (int)Math.Round(T * mm * ss * TiltRescale, MidpointRounding.AwayFromZero)));
            double M = KSolar * Tpp + KBmom * bmomPos;
            int tgtRaw = Math.Max(-13, Math.Min(13, (int)Math.Round(M, MidpointRounding.AwayFromZero)));

            // 5. frozen ops rule (NT end-stamps)
            int cur = PhysicalPosition();
            int tgt = tgtRaw;
            if (hm >= 163900 && hm < 180000)
            {
                tgt = 0;
            }
            else if (hm >= 163000 && hm < 180000)
            {
                if (tgtRaw == 0 || cur == 0) tgt = 0;
                else if (Math.Sign(tgtRaw) != Math.Sign(cur)) tgt = 0;
                else tgt = Math.Abs(tgtRaw) > Math.Abs(cur) ? cur : tgtRaw;
            }

            // 6. bar ledger
            if (barLog == null && !string.IsNullOrEmpty(ExportDir)) OpenBarLog();
            if (barLog != null)
                barLog.WriteLine(string.Format(CultureInfo.InvariantCulture,
                    "{0:yyyy-MM-ddTHH:mm:ss},{1},{2},{3},{4},{5},{6},{7},{8}",
                    Times[1][0], sessEnd ? 1 : 0, T, Tpp, bmomPos, tgtRaw, tgt, cur, tiltState));

            // 7. FAIL CLOSED: no realtime order flow, ever (research mandate)
            if (State == State.Realtime)
                return;

            // 8. physical submission (never on the session's last bar: engine exit owns the close)
            if (sessEnd) return;
            if (CurrentBars[0] < 1 || CurrentBars[1] < BarsRequiredToTrade) return;
            lastTarget = tgt;
            SubmitNetChange(tgt);
        }

        protected override void OnExecutionUpdate(Execution execution, string executionId,
            double price, int quantity, MarketPosition marketPosition, string orderId,
            DateTime time)
        {
            if (fillLog == null || execution == null || execution.Order == null)
                return;
            fillLog.AppendLine(string.Format(CultureInfo.InvariantCulture,
                "{0},{1:yyyy-MM-ddTHH:mm:ss},{2},{3},{4},{5},{6},{7},{8},{9}",
                execCount++, time, execution.Name,
                execution.Instrument != null ? execution.Instrument.FullName : "?",
                execution.Order.OrderAction, marketPosition, price, quantity,
                execution.Commission, lastTarget));
        }

        private void OpenBarLog()
        {
            try
            {
                if (!Directory.Exists(ExportDir)) Directory.CreateDirectory(ExportDir);
                barLog = new StreamWriter(Path.Combine(ExportDir, Tag + "_bars.csv"), false);
                barLog.WriteLine(string.Format(CultureInfo.InvariantCulture,
                    "# SolarWaveSMMaster_v1 KS={0} KB={1} tilt={2}/{3}/{4} short={5} band={6}",
                    KSolar, KBmom, TiltSma, TiltMult, TiltRescale, ShortHalf, BmomBandDays));
                barLog.WriteLine("time,sess_end,T,Tpp,B,tgt_raw,tgt_ops,phys,tilt_state");
            }
            catch (Exception ex)
            {
                Print("SolarWaveSMMaster_v1 bar log open failed: " + ex.Message);
                barLog = null; ExportDir = "";
            }
        }

        private void Flush()
        {
            try
            {
                if (barLog != null) { barLog.Flush(); barLog.Dispose(); barLog = null; }
                if (!string.IsNullOrEmpty(ExportDir) && fillLog != null)
                {
                    if (!Directory.Exists(ExportDir)) Directory.CreateDirectory(ExportDir);
                    using (StreamWriter w = new StreamWriter(Path.Combine(ExportDir, Tag + "_fills.csv"), false))
                    {
                        w.WriteLine("# SolarWaveSMMaster_v1 execs=" + execCount);
                        w.WriteLine("n,time,name,instrument,order_action,market_position,price,qty,commission,target");
                        w.Write(fillLog.ToString());
                        w.Flush();
                    }
                }
            }
            catch (Exception ex)
            {
                Print("SolarWaveSMMaster_v1 export failed: " + ex.Message);
            }
        }

        #region Properties
        [NinjaScriptProperty]
        [Display(Name = "Signal Instrument", Order = 0, GroupName = "System")]
        public string SignalInstrument { get; set; }
        [NinjaScriptProperty] [Display(Name="StopMultiplier (sigma fallback ticks)", Order=1, GroupName="Solar")]
        public double StopMultiplier { get; set; }
        [NinjaScriptProperty] [Display(Name="SlowdownScan", Order=2, GroupName="Solar")]
        public int SlowdownScan { get; set; }
        [NinjaScriptProperty] [Display(Name="WeakWeakSplit", Order=3, GroupName="Solar")]
        public int WeakWeakSplit { get; set; }
        [NinjaScriptProperty] [Display(Name="VolPeriod", Order=4, GroupName="Solar")]
        public int VolPeriod { get; set; }
        [NinjaScriptProperty] [Display(Name="SMinTicks", Order=5, GroupName="Solar")]
        public double SMinTicks { get; set; }
        [NinjaScriptProperty] [Display(Name="SMaxTicks", Order=6, GroupName="Solar")]
        public double SMaxTicks { get; set; }
        [NinjaScriptProperty] [Display(Name="Tilt SMA sessions", Order=7, GroupName="Tilt")]
        public int TiltSma { get; set; }
        [NinjaScriptProperty] [Display(Name="Tilt multiplier", Order=8, GroupName="Tilt")]
        public double TiltMult { get; set; }
        [NinjaScriptProperty] [Display(Name="Tilt rescale", Order=9, GroupName="Tilt")]
        public double TiltRescale { get; set; }
        [NinjaScriptProperty] [Display(Name="Short halving (c1_50)", Order=10, GroupName="Tilt")]
        public double ShortHalf { get; set; }
        [NinjaScriptProperty] [Display(Name="K Solar (MNQ per Tpp unit)", Order=11, GroupName="Allocator")]
        public double KSolar { get; set; }
        [NinjaScriptProperty] [Display(Name="K BMom (MNQ at B=+-1)", Order=12, GroupName="Allocator")]
        public double KBmom { get; set; }
        [NinjaScriptProperty] [Display(Name="BMom band days", Order=13, GroupName="Allocator")]
        public int BmomBandDays { get; set; }
        [NinjaScriptProperty] [Display(Name="Export Dir", Order=14, GroupName="Export")]
        public string ExportDir { get; set; }
        [NinjaScriptProperty] [Display(Name="Tag", Order=15, GroupName="Export")]
        public string Tag { get; set; }
        #endregion
    }
}
