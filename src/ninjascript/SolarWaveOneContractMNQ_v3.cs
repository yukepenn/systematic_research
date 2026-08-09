// SolarWaveOneContractMNQ_v3 — Product B BEST_ONE_MNQ, C4-compliance rebuild.
//
// SUPERSEDES SolarWaveOneContractMNQ_Final, WHICH IS BROKEN. Frozen spec:
// runs/W17_C4_COMPLIANCE/spec.yaml (committed at c8330dc BEFORE this file was written).
// Per that spec's V1-R3 rule this is a NEW OBJECT, not a corrected old one: 67.6% of the
// old object's exits happened ~18 minutes later than intended, so its $28,900.70 headline
// describes a different policy and is NOT a comparison baseline. _v2, not _Final, because
// NAMING.md reserves _Final for a parity-PASSED artifact and V1-R4 re-parity has not run.
//
// ---------------------------------------------------------------------------------------
// DEFECT 1 — CROSS-SERIES ORDER ARRANGEMENT (the reason the old file never flattened).
// SolarWaveOneContractMNQ_Final ran its entire decision inside a BarsInProgress==1 (NQ
// signal) event while the EXECUTION instrument sat on the PRIMARY series, and submitted
// orders with barsInProgressIndex 0. That is the exact arrangement recorded as a defect in
// research/system_master/KNOWN_ERRORS_AND_CORRECTIONS.md #7 ("v1 attached to the MNQ
// execution instrument as PRIMARY and submitted index-0 orders from signal-series (BIP1)
// events... the primary Position did not advance between successive signal-bar decisions"),
// whose stated RULE is: signals on PRIMARY, execution on the ADDED series via Positions[1].
// MEASURED CONSEQUENCE on the real NT8 trade list (1,561 trades): 100.0% of exits were
// either a managed auto-reversal (30.9%) or an engine session-close backstop (67.6% at
// 17:00 + 1.4% at holiday early closes). ZERO voluntary strategy-submitted exits, ever.
// FIX: adopt the parity-proven SolarWaveSMMaster_v2 / E10Master_v2 arrangement verbatim —
// signal instrument on the PRIMARY series, MNQ execution as the ADDED series at index 1,
// position read through Positions[1], orders submitted with barsInProgressIndex 1. That
// arrangement is parity-proven at 0 mismatches over 540,232 decision bars.
// ATTACH-TO THEREFORE CHANGES: attach to an NQ 3-minute chart, set ExecInstrument="MNQ 09-26".
//
// DEFECT 2 — HOLIDAY EARLY CLOSES (shared with the NQ object and with Product A).
// The flatten schedule is now SESSION-RELATIVE instead of hardcoded:
//        entry block : hm >= 163000  ->  Time[0] >= sessionEnd - 30 min
//        forced flat : hm >= 163900  ->  Time[0] >= sessionEnd - 21 min
// On a normal 17:00 ET close these are exactly 16:30 and 16:39, so normal-session behaviour
// is unchanged by construction; only the 43 early-close sessions in the dev window differ.
// BROKER FACT (NinjaTrader Brokerage Lifetime): intraday margin ends 15 minutes before the
// session close and holiday early closes do NOT extend it — initial margin ($4,343.38/MNQ
// vs $100 intraday) is required 15 minutes before the EARLY close.
// The 21-minute figure preserves the existing 6-minute order-routing buffer ahead of the
// 15-minute broker deadline (MARGIN_RULES.md §3.1 recommends 5-7 minutes). FROZEN, not searched.
// ---------------------------------------------------------------------------------------
//
// NOT CHANGED: every signal / allocator / threshold / hysteresis constant, the realtime
// fail-closed guard, the instrument guard (now checking the ADDED execution series), the
// effective-parameter logging, and IsExitOnSessionCloseStrategy/ExitOnSessionCloseSeconds.
//
//     M = WSolar * T' + WBmom * B      (defaults 0.7086 / 2.83, frozen winner arithmetic)
//     T' = clamp(round(T * m * TiltRescale), +/-13), T = round(10 * mean member pending pos)
//     m  = TiltMult when sign(member vote) == prior-session daily SMA(TiltSma) state, else 1
//     B  = frozen W8-1 B-MOM position in {-1, 0, +1}
// Rule (frozen: runs/SM14_ONELOT_DAYMARGIN/spec.yaml, seq 318):
//     LONG 1 when flat and M >= EntryLevel; SHORT 1 when flat and M <= -EntryLevel;
//     flip on opposite entry level; exit flat when M retreats through ExitLevel.
// ATTACH TO: NQ 09-26 3-MINUTE chart, CME US Index Futures ETH template, with
// ExecInstrument = "MNQ 09-26" (the traded leg, $100 day margin).
// HISTORICAL research result — not a forward guarantee. Regime monitors apply.
// HOT-RELOAD: version class per edit.
// SAFETY: research/backtest only. FAILS CLOSED in realtime. Live enablement is a separate,
// explicit, owner-authorized decision — see research/system_master/LIVE_READINESS_CHECKLIST.md.
// BUILD TAG: SolarWaveOneContractMNQ_v3 2026-08-09 (W17 C4-compliance rebuild).

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
    public class SolarWaveOneContractMNQ_v3 : Strategy
    {
        private const string BuildTag = "SolarWaveOneContractMNQ_v3 2026-08-09";
        private const string ExpectedExecPrefix = "MNQ";

        // Session-relative flatten schedule. Equal to 16:30 / 16:39 on a 17:00 close.
        private const int EntryBlockMinutesBeforeClose = 30;
        private const int ForcedFlatMinutesBeforeClose = 21;

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

        private bool instrumentMismatch;

        private SessionIterator sessIter;
        private DateTime sessionEndTs = DateTime.MinValue;

        // W17B: the execution series gets its own flatten authority. The 16:45 obligation is
        // a property of the TRADED leg's margin, not of the signal leg's data availability.
        private SessionIterator execSessIter;
        private DateTime execSessionEndTs = DateTime.MinValue;
        // Watchdog fires only when the decision series has fallen this far behind the
        // execution series -- i.e. a genuine data gap. Normal lag between two synchronised
        // 3-minute series is 0 or one bar, so 15 minutes cannot trip on normal data.
        private const int DecisionStaleMinutes = 15;

        // Diagnostic fills ledger (same pattern as the parity-proven SolarWaveSMMaster_v2).
        // Writes only; places no orders and changes no decision. Inert when ExportDir is "".
        private StringBuilder fillLog;
        private int execCount;
        private int lastTarget;

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Name = "SolarWaveOneContractMNQ_v3";
                Calculate = Calculate.OnBarClose;
                IsExitOnSessionCloseStrategy = true;
                ExitOnSessionCloseSeconds = 30;
                BarsRequiredToTrade = 20;
                IsInstantiatedOnEachOptimizationIteration = false;

                ExecInstrument = "MNQ 09-26";
                StopMultiplier = 179; SlowdownScan = 5; WeakWeakSplit = 10;
                VolPeriod = 460; SMinTicks = 40; SMaxTicks = 1200;
                TiltSma = 50; TiltMult = 1.25; TiltRescale = 0.9026;
                WSolar = 0.7086; WBmom = 2.83; BmomBandDays = 14;
                EntryLevel = 3.0; ExitLevel = 1.0; // frozen seq-318, not a free parameter
                ExportDir = ""; Tag = "mnq_v3";
            }
            else if (State == State.Configure)
            {
                // KNOWN_ERRORS #7 arrangement: signals stay on the PRIMARY series; the traded
                // instrument is the ADDED series at index 1.
                AddDataSeries(ExecInstrument, BarsPeriodType.Minute, 3);
                fillLog = new StringBuilder(1 << 20);
                execCount = 0; lastTarget = 0;
            }
            else if (State == State.Terminated)
            {
                Flush();
            }
            else if (State == State.DataLoaded)
            {
                volSum = 0; volCount = 0; prevClose = double.NaN;
                initialized = false; tiltState = 0; bmomPos = 0; rthDayCount = 0;
                rthOpen = false;
                sessionEndTs = DateTime.MinValue;
                sessIter = new SessionIterator(BarsArray[0]);
                execSessionEndTs = DateTime.MinValue;
                execSessIter = new SessionIterator(BarsArray[1]);

                // Execution-instrument guard now checks the ADDED series, which is the leg
                // that actually receives orders.
                string execName = BarsArray.Length > 1 && BarsArray[1] != null
                    && BarsArray[1].Instrument != null
                    && BarsArray[1].Instrument.MasterInstrument != null
                    ? BarsArray[1].Instrument.MasterInstrument.Name : "";
                string sigName = Instrument != null && Instrument.MasterInstrument != null
                    ? Instrument.MasterInstrument.Name : "";
                instrumentMismatch = !execName.StartsWith(ExpectedExecPrefix,
                        StringComparison.OrdinalIgnoreCase)
                    || !sigName.Equals("NQ", StringComparison.OrdinalIgnoreCase);
                if (instrumentMismatch)
                    Print(string.Format("{0}: ERROR arrangement mismatch. primary(signal)='{1}' "
                        + "expected 'NQ'; added(execution)='{2}' expected prefix '{3}'. "
                        + "This build will not trade.",
                        BuildTag, sigName, execName, ExpectedExecPrefix));

                Print(string.Format(
                    "{0} | SignalPrimary={1} | ExecInstrument(added idx1)={2} | StopMultiplier={3} | " +
                    "SlowdownScan={4} | WeakWeakSplit={5} | VolPeriod={6} | SMinTicks={7} | " +
                    "SMaxTicks={8} | TiltSma={9} | TiltMult={10} | TiltRescale={11} | " +
                    "WSolar={12} | WBmom={13} | BmomBandDays={14} | EntryLevel={15} | " +
                    "ExitLevel={16} | EntryBlockMinBeforeClose={17} | FlatMinBeforeClose={18}",
                    BuildTag, sigName, execName, StopMultiplier, SlowdownScan,
                    WeakWeakSplit, VolPeriod, SMinTicks, SMaxTicks, TiltSma, TiltMult,
                    TiltRescale, WSolar, WBmom, BmomBandDays, EntryLevel, ExitLevel,
                    EntryBlockMinutesBeforeClose, ForcedFlatMinutesBeforeClose));
            }
        }

        private double CausalSigma()
        {
            if (volCount < 30) return double.NaN;
            return volSum / volCount;
        }
        private void UpdateVol()
        {
            double c0 = Close[0];
            if (!double.IsNaN(prevClose))
            {
                volSum += Math.Abs(c0 - prevClose); volCount++;
                if (volCount > VolPeriod)
                {
                    int n = Math.Min(VolPeriod, CurrentBar);
                    double s = 0;
                    for (int i = 0; i < n; i++)
                        s += Math.Abs(Close[i] - Close[i + 1]);
                    volSum = s; volCount = n;
                }
            }
            prevClose = c0;
        }
        private double ResolveS(double volMult)
        {
            double sig = CausalSigma();
            double ts = TickSize;   // primary = signal instrument (NQ)
            if (double.IsNaN(sig) || sig <= 0) return StopMultiplier * ts;
            double s = volMult * sig;
            double lo = SMinTicks * ts, hi = SMaxTicks * ts;
            if (s < lo) s = lo;
            if (s > hi) s = hi;
            return s;
        }

        private void UpdateMachine(int m)
        {
            double px = Close[0];
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
            if (CurrentBar < BarsRequiredToTrade) { mPending[m] = mPos[m]; return; }
            double xl = mIsUp[m] ? mAnchor[m] - mSEff[m] : mAnchor[m] + mSEff[m];
            if (mPos[m] > 0 && Close[0] <= xl) { mPending[m] = 0; return; }
            if (mPos[m] < 0 && Close[0] >= xl) { mPending[m] = 0; return; }
            if (mPos[m] != 0) { mPending[m] = mPos[m]; return; }
            mPending[m] = mSig[m];
        }

        private void BmomBar(int hm, bool sessEnd)
        {
            if (hm == 93300)
            {
                open0930 = Open[0]; vwapPV = 0; vwapV = 0; rthOpen = true;
                todaySlots.Clear(); bmomPos = 0;
            }
            if (!rthOpen || hm < 93300 || hm > 160000)
            {
                if (sessEnd) EndRthDay();
                return;
            }
            double c = Close[0], v = Volume[0];
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

        // KNOWN_ERRORS #7 RULE: read the position of the ADDED execution series explicitly.
        private int PhysicalPosition()
        {
            if (Positions == null || Positions.Length < 2 || Positions[1] == null)
                return 0;
            if (Positions[1].MarketPosition == MarketPosition.Long) return Positions[1].Quantity;
            if (Positions[1].MarketPosition == MarketPosition.Short) return -Positions[1].Quantity;
            return 0;
        }
        private void SubmitTarget(int tgt)
        {
            // FAIL CLOSED: no realtime order flow, ever (research mandate).
            if (State == State.Realtime)
                return;
            if (instrumentMismatch)
                return;
            int c = PhysicalPosition();
            if (tgt == c) return;
            // Hard cap: never more than 1 net contract, never pyramided/averaged.
            if (Math.Abs(tgt) > 1) tgt = Math.Sign(tgt);
            if (tgt == 0) { if (c > 0) ExitLong(1, c, "XL", ""); else ExitShort(1, -c, "XS", ""); }
            else if (tgt > 0) EnterLong(1, 1, "L");
            else EnterShort(1, 1, "S");
        }

        // W17B execution-series flatten watchdog. Signal series = index 0, execution = index 1.
        // Can ONLY move the position toward flat: it never opens, sizes up, or reverses.
        // Inert unless the decision series has gone stale (data gap), which is the only case
        // in which the ordinary decision path cannot reach its own flatten deadline.
        private void ExecWatchdog()
        {
            if (State == State.Realtime) return;
            if (instrumentMismatch) return;
            if (CurrentBars.Length < 2 || CurrentBars[1] < 1) return;

            if (BarsArray[1].IsFirstBarOfSession || execSessionEndTs == DateTime.MinValue)
            {
                execSessIter.GetNextSession(Times[1][0], true);
                execSessionEndTs = execSessIter.ActualSessionEnd;
            }
            if (execSessionEndTs == DateTime.MinValue) return;

            DateTime execTs = Times[1][0];
            if (execTs < execSessionEndTs.AddMinutes(-ForcedFlatMinutesBeforeClose)) return;

            DateTime decTs = CurrentBar >= 0 ? Time[0] : DateTime.MinValue;
            if (decTs >= execTs.AddMinutes(-DecisionStaleMinutes)) return;   // decision series current

            if (PhysicalPosition() == 0) return;
            lastTarget = 0;
            SubmitTarget(0);
        }

        protected override void OnBarUpdate()
        {
            if (BarsInProgress == 1)
            {
                ExecWatchdog();
                return;
            }
            if (BarsInProgress != 0)
                return;
            if (CurrentBar < 1)
                return;

            if (Bars.IsFirstBarOfSession || sessionEndTs == DateTime.MinValue)
            {
                sessIter.GetNextSession(Time[0], true);
                sessionEndTs = sessIter.ActualSessionEnd;
            }

            for (int m = 0; m < NMEM; m++) mPos[m] = mPending[m];

            UpdateVol();
            for (int m = 0; m < NMEM; m++) UpdateMachine(m);
            if (!initialized) initialized = true;
            for (int m = 0; m < NMEM; m++) Decide(m);

            bool sessEnd = Bars.IsLastBarOfSession;
            int hm = ToTime(Time[0]);
            BmomBar(hm, sessEnd);

            if (sessEnd)
            {
                for (int m = 0; m < NMEM; m++) { mPos[m] = 0; mPending[m] = 0; }
                sessCloses.Add(Close[0]);
                if (sessCloses.Count > TiltSma)
                {
                    double s = 0;
                    for (int i = sessCloses.Count - TiltSma; i < sessCloses.Count; i++) s += sessCloses[i];
                    tiltState = Math.Sign(Close[0] - s / TiltSma);
                }
                if (sessCloses.Count > 600) sessCloses.RemoveAt(0);
            }

            int sumNext = 0;
            for (int m = 0; m < NMEM; m++) sumNext += mPending[m];
            int T = Math.Max(-10, Math.Min(10, (int)Math.Round(sumNext / 13.0 * 10.0, MidpointRounding.AwayFromZero)));
            double mm = (sumNext != 0 && tiltState != 0 && Math.Sign(sumNext) == tiltState) ? TiltMult : 1.0;
            int Tp = Math.Max(-13, Math.Min(13, (int)Math.Round(T * mm * TiltRescale, MidpointRounding.AwayFromZero)));
            double M = WSolar * Tp + WBmom * bmomPos;

            if (CurrentBars.Length < 2 || CurrentBars[1] < 1) return;
            int p = PhysicalPosition();
            int tgt = p;

            DateTime nowTs = Time[0];
            bool entryBlocked = sessionEndTs != DateTime.MinValue
                && nowTs >= sessionEndTs.AddMinutes(-EntryBlockMinutesBeforeClose);
            bool forceFlat = sessionEndTs != DateTime.MinValue
                && nowTs >= sessionEndTs.AddMinutes(-ForcedFlatMinutesBeforeClose);

            if (forceFlat)
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
            lastTarget = tgt;
            SubmitTarget(tgt);
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

        private void Flush()
        {
            try
            {
                if (string.IsNullOrEmpty(ExportDir) || fillLog == null) return;
                if (!Directory.Exists(ExportDir)) Directory.CreateDirectory(ExportDir);
                using (StreamWriter w = new StreamWriter(Path.Combine(ExportDir, Tag + "_fills.csv"), false))
                {
                    w.WriteLine("# " + BuildTag + " execs=" + execCount);
                    w.WriteLine("n,time,name,instrument,order_action,market_position,price,qty,commission,target");
                    w.Write(fillLog.ToString());
                    w.Flush();
                }
            }
            catch (Exception ex)
            {
                Print(BuildTag + " fills flush failed: " + ex.Message);
            }
        }

        #region Properties
        [NinjaScriptProperty]
        [Display(Name = "Execution Instrument", Order = 0, GroupName = "System")]
        public string ExecInstrument { get; set; }
        [NinjaScriptProperty] [Display(Name="Export dir (diagnostic ledger)", Order=15, GroupName="Diag")]
        public string ExportDir { get; set; }
        [NinjaScriptProperty] [Display(Name="Export tag", Order=16, GroupName="Diag")]
        public string Tag { get; set; }
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
