// SolarWaveSMOneLot_v1 — SYSTEM_MASTER one-lot day-margin strategy (SM14, seq 318 adopted).
//
// Collapses the SYSTEM_MASTER winner (PORT_TILT_532, B1 leg excluded) to a single
// contract via sign-with-hysteresis on the consolidated MNQ-unit target
//     M = WSolar * T' + WBmom * B      (defaults 0.7086 / 2.83, frozen winner arithmetic)
//     T' = clamp(round(T * m * TiltRescale), +/-13), T = round(10 * mean member pending pos)
//     m  = TiltMult when sign(member vote) == prior-session daily SMA(TiltSma) state, else 1
//     B  = frozen W8-1 B-MOM position in {-1, 0, +1}
// Rule (frozen: runs/SM14_ONELOT_DAYMARGIN/spec.yaml, repo systematic_research):
//     LONG 1 when flat and M >= EntryLevel; SHORT 1 when flat and M <= -EntryLevel;
//     flip on opposite entry level; exit flat when M retreats through ExitLevel;
//     no new entries on decision bars 16:30-18:00 ET; forced flat decided at the
//     16:39-close bar (fills ~16:39-16:42, before the 16:45 intraday-margin cutoff);
//     IsExitOnSessionCloseStrategy remains as backstop (early-close days).
// ATTACH TO: the execution instrument (MNQ ##-## recommended, $100 day margin;
// NQ ##-## supported), 3-MINUTE bars, 24/7 or CME US Index Futures ETH template.
// SignalInstrument (NQ continuous, back-adjusted merge) drives all signal math.
// Dev evidence 2022-01..2026-05 (Python twin, runs/SM14_ONELOT_DAYMARGIN):
//   1 MNQ: net $27,287, Sharpe 1.004, maxDD -$6,374, worst month -$2,105
//   1 NQ : net $298,040, Sharpe 1.098, maxDD -$58,887 (commissions cheaper/notional)
// HISTORICAL research result — not a forward guarantee. Regime monitors apply
// (MONITOR-01 r-statistic; B-MOM decay floor). HOT-RELOAD: version class per edit.
// SAFETY: research/backtest only. FAILS CLOSED in realtime (SubmitTarget returns before
// any order submission when State == State.Realtime). Live enablement is a separate,
// explicit, owner-authorized decision — see research/system_master/LIVE_READINESS_CHECKLIST.md.
// This guard was retrofitted 2026-08-08 (SMV2AH audit): earlier revisions of this file had
// no code-level realtime guard, unlike SolarWaveSMMaster_v2.cs, and relied entirely on
// operating discipline. Added for defense-in-depth; not itself a claim of live-readiness.

#region Using declarations
using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
#endregion

namespace NinjaTrader.NinjaScript.Strategies
{
    public class SolarWaveSMOneLot_v1 : Strategy
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

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Name = "SolarWaveSMOneLot_v1";
                Calculate = Calculate.OnBarClose;
                IsExitOnSessionCloseStrategy = true;
                ExitOnSessionCloseSeconds = 30;
                BarsRequiredToTrade = 20;
                IsInstantiatedOnEachOptimizationIteration = false;

                SignalInstrument = "NQ 09-26";
                StopMultiplier = 179; SlowdownScan = 5; WeakWeakSplit = 10;
                VolPeriod = 460; SMinTicks = 40; SMaxTicks = 1200;
                TiltSma = 50; TiltMult = 1.25; TiltRescale = 0.9026;
                WSolar = 0.7086; WBmom = 2.83; BmomBandDays = 14;
                EntryLevel = 3.0; ExitLevel = 1.0;
            }
            else if (State == State.Configure)
            {
                AddDataSeries(SignalInstrument, BarsPeriodType.Minute, 3);
            }
            else if (State == State.DataLoaded)
            {
                volSum = 0; volCount = 0; prevClose = double.NaN;
                initialized = false; tiltState = 0; bmomPos = 0; rthDayCount = 0;
                rthOpen = false;
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
        private void SubmitTarget(int tgt)
        {
            // FAIL CLOSED: no realtime order flow, ever (research mandate) — matches
            // SolarWaveSMMaster_v2.cs's guard. See header SAFETY note (retrofitted 2026-08-08).
            if (State == State.Realtime)
                return;
            int c = PhysicalPosition();
            if (tgt == c) return;
            if (tgt == 0) { if (c > 0) ExitLong(0, c, "XL", ""); else ExitShort(0, -c, "XS", ""); }
            else if (tgt > 0) EnterLong(0, 1, "L");
            else EnterShort(0, 1, "S");
        }

        protected override void OnBarUpdate()
        {
            if (BarsInProgress != 1)
                return;
            if (CurrentBars[1] < 1)
                return;

            for (int m = 0; m < NMEM; m++) mPos[m] = mPending[m];

            UpdateVol();
            for (int m = 0; m < NMEM; m++) UpdateMachine(m);
            if (!initialized) initialized = true;
            for (int m = 0; m < NMEM; m++) Decide(m);

            bool sessEnd = BarsArray[1].IsLastBarOfSession;
            int hm = ToTime(Times[1][0]);
            BmomBar(hm, sessEnd);

            if (sessEnd)
            {
                for (int m = 0; m < NMEM; m++) { mPos[m] = 0; mPending[m] = 0; }
                sessCloses.Add(Closes[1][0]);
                if (sessCloses.Count > TiltSma)
                {
                    double s = 0;
                    for (int i = sessCloses.Count - TiltSma; i < sessCloses.Count; i++) s += sessCloses[i];
                    tiltState = Math.Sign(Closes[1][0] - s / TiltSma);
                }
                if (sessCloses.Count > 600) sessCloses.RemoveAt(0);
            }

            int sumNext = 0;
            for (int m = 0; m < NMEM; m++) sumNext += mPending[m];
            int T = Math.Max(-10, Math.Min(10, (int)Math.Round(sumNext / 13.0 * 10.0, MidpointRounding.AwayFromZero)));
            double mm = (sumNext != 0 && tiltState != 0 && Math.Sign(sumNext) == tiltState) ? TiltMult : 1.0;
            int Tp = Math.Max(-13, Math.Min(13, (int)Math.Round(T * mm * TiltRescale, MidpointRounding.AwayFromZero)));
            double M = WSolar * Tp + WBmom * bmomPos;

            if (CurrentBars[0] < 1) return;
            int p = PhysicalPosition();
            int tgt = p;
            bool entryBlocked = (hm >= 163000 && hm <= 180000);
            if (hm >= 163900 && hm < 180000)
            {
                tgt = 0;
            }
            else if (p == 0)
            {
                if (!entryBlocked)
                {
                    if (M >= EntryLevel) tgt = 1;
                    else if (M <= -EntryLevel) tgt = -1;
                }
            }
            else if (p > 0)
            {
                if (M <= -EntryLevel && !entryBlocked) tgt = -1;
                else if (M <= ExitLevel) tgt = 0;
            }
            else
            {
                if (M >= EntryLevel && !entryBlocked) tgt = 1;
                else if (M >= -ExitLevel) tgt = 0;
            }
            SubmitTarget(tgt);
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
        [NinjaScriptProperty] [Display(Name="W Solar", Order=10, GroupName="Allocator")]
        public double WSolar { get; set; }
        [NinjaScriptProperty] [Display(Name="W BMom", Order=11, GroupName="Allocator")]
        public double WBmom { get; set; }
        [NinjaScriptProperty] [Display(Name="BMom band days", Order=12, GroupName="Allocator")]
        public int BmomBandDays { get; set; }
        [NinjaScriptProperty] [Display(Name="Entry level a", Order=13, GroupName="OneLot")]
        public double EntryLevel { get; set; }
        [NinjaScriptProperty] [Display(Name="Exit level b", Order=14, GroupName="OneLot")]
        public double ExitLevel { get; set; }
        #endregion
    }
}
