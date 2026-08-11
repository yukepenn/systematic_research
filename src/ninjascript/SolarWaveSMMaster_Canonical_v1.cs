// SolarWaveSMMaster_Canonical_v1 — EQV04 research-only executable twin of SolarWaveSMMaster_v4.
//
// Per research/system_master/CANONICAL_MATHEMATICAL_SPEC.md (derived from EQV01's exhaustive
// finite-state proof, 243/243 states, EXACT_EQUIVALENCE): the incumbent's
// `M = KSolar*Tpp + KBmom*bmomPos` (KSolar=0.728654, KBmom=2.934159) is replaced here by the
// proven-exact integer form `Q = Tpp + 4*bmomPos; target = round(0.73*Q)`, and TiltRescale
// 0.9026 is replaced by its proven-exact substitute 0.91. THIS IS THE ONLY DECISION-LOGIC
// CHANGE. Every other line (ops rules, BMOM computation, session handling, order submission,
// execution watchdog) is byte-identical to the incumbent, kept that way deliberately so this
// file's sole purpose -- proving executable parity between the real and canonical
// representations -- has the smallest possible diff surface to audit. The incumbent
// SolarWaveSMMaster_v4.cs remains the sole source of truth for live/backtest behavior; this
// object is ENGINEERING_ONLY / EQV04, not a promotion, not a parameter change, and not
// intended for standalone use. See research/system_master/CANONICAL_MATHEMATICAL_SPEC.md.
//
// ==========================================================================================
// ORIGINAL SolarWaveSMMaster_v4 HEADER (kept verbatim below for provenance/diff traceability)
// ==========================================================================================
//
// SolarWaveSMMaster_v4 — DAYONLY_DUAL6040 consolidated master (SMV2M, seq 371).
//
// v3 = v2 + the two C4 flatten fixes already proven on both Product B objects
// (runs/W18E_PRODUCTA_C4/spec.yaml, frozen before this file existed):
//   C2 session-relative cutoffs via SessionIterator.ActualSessionEnd, so the flatten also
//      fires on the 43 holiday early-close sessions. On a 17:00 close sessionEnd-30/-21 min
//      evaluate to exactly 16:30/16:39, so all 1,138 normal sessions are unchanged BY
//      CONSTRUCTION. v2 hardcoded 163000/163900 and therefore never fired on an early close,
//      leaving only NT8's 30-second engine backstop -- which fires ~14.5 min INSIDE the
//      initial-margin window. 39 measured breaches.
//   C3 execution-series flatten watchdog (BarsInProgress == 1), gated on decision-series
//      staleness > 15 min, able to move only toward FLAT. Uses Times[0][0]/CurrentBars[0]:
//      the unindexed Time[0]/CurrentBar are BarsInProgress-RELATIVE and silently read the
//      wrong series inside a BIP-1 handler (this is what made W17B's _v3 a silent no-op).
// Nothing else changes. Model constants, series arrangement, and the realtime FAIL-CLOSED
// guard are untouched.
//
// v2 FIXES v1's order-engine arrangement bug: v1 attached to MNQ primary and submitted
// index-0 orders from signal-series (BIP1) events; Position did not advance between
// signal-bar decisions, and with EntriesPerDirection=100 entries stacked without limit
// (238,099 fills, max qty 1037 — see runs/SMV2M_MASTER_BUILD/out/nt8 v1 ledgers).
// v2 uses the PROVEN SolarWaveE10Master_v2 arrangement (0/540,232 bar parity):
//   primary series = SIGNAL instrument (NQ merge-back-adjusted, 3-min) drives all math;
//   AddDataSeries(ExecInstrument MNQ 3-min) = index 1; positions via Positions[1];
//   net-change orders submitted with barsInProgressIndex 1 during BIP0 processing.
//
// Model (frozen, runs/SMV2M_MASTER_BUILD/spec.yaml):
//     M = round( KSolar * Tpp + KBmom * B ), clamp +/-13
//     Tpp = clamp(round(T * m * s * TiltRescale), +/-13)
//       T = clamp(round(10 * mean member pending pos), +/-10)   (13 virtual V3 members)
//       m = TiltMult  iff T != 0 and prior-session SMA(TiltSma) state == sign(T)
//       s = ShortHalf iff T < 0  and prior-session state is UP        (c1_50)
//     B = frozen W8-1 B-MOM virtual position in {-1,0,+1}
//     KSolar = 0.728654   KBmom = 2.934159   TiltRescale = 0.9026
// Ops: 16:30-18:00 decision bars no increases/reversals; >= 16:39 target 0 (flat < 16:45 cliff);
// session-close engine exit as backstop.
// SAFETY: research/backtest only. FAILS CLOSED in realtime (returns before any submission).
// HOT-RELOAD: version the class name on every edit.

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

// ---------------------------------------------------------------------------------------
// v4 FIX (2026-08-09, V1R4 parity forensics) -- DEFECT 3: BMOM leg's own end-of-RTH
// flatten was still a HARDCODED CLOCK (`hm >= 155700`), never migrated when C2/C3 made the
// entry-block/forced-flat overlay session-relative. On a holiday session that ends before
// 15:57 ET (e.g. 2025-02-17 Presidents Day, CME halts 13:00-18:00), hm never reaches 155700,
// so a non-zero bmomPos from that truncated RTH day survives UNFLATTENED into the following
// overnight session -- confirmed on real NT8 output: an extra, wrong short entry at
// 2025-02-17 18:06 ET (M=-4.25 with the stale bmomPos=-1 vs the correct M=-1.42 at
// bmomPos=0). Checked against the Python twin's session-close bar for every truncated
// session in the dev window: 11 of 44 early closes have bmomPos != 0 at the boundary and
// would trigger this. FIX: `bmomPos` now also flattens on the session's own last bar
// (`sessEnd`), matching how the Solar members already reset on sessEnd two lines below and
// matching the Python twin's data-driven `flat_hm` behaviour exactly. One-line change, no
// signal/weight/threshold touched. See runs/V1R4_NT8_PARITY/ for the forensics.
// ---------------------------------------------------------------------------------------
namespace NinjaTrader.NinjaScript.Strategies
{
    public class SolarWaveSMMaster_Canonical_v1 : Strategy
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

        // ---- C2/C3 (W18E). Minutes-before-ACTUAL-session-close, not wall-clock constants.
        private const int EntryBlockMinutesBeforeClose = 30;   // == 16:30 on a 17:00 close
        private const int ForcedFlatMinutesBeforeClose = 21;   // == 16:39 on a 17:00 close
        private const int DecisionStaleMinutes = 15;           // C3 watchdog trigger
        private SessionIterator sessIter;                      // over the PRIMARY (signal) series
        private DateTime sessionEndTs = DateTime.MinValue;
        private SessionIterator execSessIter;                  // over the EXECUTION series
        private DateTime execSessionEndTs = DateTime.MinValue;

        private StreamWriter barLog;
        private StringBuilder fillLog;
        private int execCount;
        private int lastTarget;

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Name = "SolarWaveSMMaster_Canonical_v1";
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
                OrderFillResolution = OrderFillResolution.Standard;
                Slippage = 0;

                ExecInstrument = "MNQ 09-26";
                StopMultiplier = 179; SlowdownScan = 5; WeakWeakSplit = 10;
                VolPeriod = 460; SMinTicks = 40; SMaxTicks = 1200;
                TiltSma = 50; TiltMult = 1.25; TiltRescale = 0.91; ShortHalf = 0.5;
                QWeight = 0.73; BmomBandDays = 14;
                ExportDir = ""; Tag = "smm_canonical_v1";
            }
            else if (State == State.Configure)
            {
                AddDataSeries(ExecInstrument, BarsPeriodType.Minute, 3);
                fillLog = new StringBuilder(1 << 20);
                execCount = 0;
            }
            else if (State == State.DataLoaded)
            {
                volSum = 0; volCount = 0; prevClose = double.NaN;
                initialized = false; tiltState = 0; bmomPos = 0; rthDayCount = 0;
                rthOpen = false; lastTarget = 0;
                sessIter = new SessionIterator(BarsArray[0]);
                sessionEndTs = DateTime.MinValue;
                if (BarsArray.Length > 1)
                {
                    execSessIter = new SessionIterator(BarsArray[1]);
                    execSessionEndTs = DateTime.MinValue;
                }
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
            double ts = TickSize;
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
            if (hm >= 155700 || sessEnd) bmomPos = 0;
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
            if (Positions == null || Positions.Length < 2 || Positions[1] == null)
                return 0;
            if (Positions[1].MarketPosition == MarketPosition.Long) return Positions[1].Quantity;
            if (Positions[1].MarketPosition == MarketPosition.Short) return -Positions[1].Quantity;
            return 0;
        }

        private void SubmitNetChange(int tgt)
        {
            int c = PhysicalPosition();
            if (tgt == c) return;
            if (tgt == 0)
            {
                if (c > 0) ExitLong(1, c, "XL", "");
                else       ExitShort(1, -c, "XS", "");
            }
            else if (tgt > 0)
            {
                if (c < 0)        EnterLong(1, tgt, "L");          // managed auto-reversal
                else if (tgt > c) EnterLong(1, tgt - c, "L");
                else              ExitLong(1, c - tgt, "XL", "");
            }
            else
            {
                if (c > 0)        EnterShort(1, -tgt, "S");        // managed auto-reversal
                else if (tgt < c) EnterShort(1, c - tgt, "S");
                else              ExitShort(1, tgt - c, "XS", "");
            }
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

            // C2: resolve THIS session's actual close from the trading-hours template
            // (honours the 43 holiday early closes; a hardcoded clock does not).
            if (Bars.IsFirstBarOfSession || sessionEndTs == DateTime.MinValue)
            {
                sessIter.GetNextSession(Time[0], true);
                sessionEndTs = sessIter.ActualSessionEnd;
            }

            // 1. virtual member fills at this bar's open
            for (int m = 0; m < NMEM; m++) mPos[m] = mPending[m];

            // 2. shared sigma + member machines on this bar's close
            UpdateVol();
            for (int m = 0; m < NMEM; m++) UpdateMachine(m);
            if (!initialized) initialized = true;
            for (int m = 0; m < NMEM; m++) Decide(m);

            bool sessEnd = Bars.IsLastBarOfSession;
            int hm = ToTime(Time[0]);
            BmomBar(hm, sessEnd);

            // 3. session end: members zeroed; HTF state from session closes INCLUDING this one,
            //    effective next session (matches twin rolling(50).shift(1))
            if (sessEnd)
            {
                for (int m = 0; m < NMEM; m++) { mPos[m] = 0; mPending[m] = 0; }
                sessCloses.Add(Close[0]);
                if (sessCloses.Count >= TiltSma)
                {
                    double s = 0;
                    for (int i = sessCloses.Count - TiltSma; i < sessCloses.Count; i++) s += sessCloses[i];
                    tiltState = Math.Sign(Close[0] - s / TiltSma);
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
            int Q = Tpp + 4 * bmomPos;
            int tgtRaw = Math.Max(-13, Math.Min(13, (int)Math.Round(QWeight * Q, MidpointRounding.AwayFromZero)));

            // 5. frozen ops rule (NT end-stamps)
            int cur = PhysicalPosition();
            int tgt = tgtRaw;
            DateTime nowTs = Time[0];
            bool forceFlat = sessionEndTs != DateTime.MinValue
                && nowTs >= sessionEndTs.AddMinutes(-ForcedFlatMinutesBeforeClose);
            bool entryBlocked = sessionEndTs != DateTime.MinValue
                && nowTs >= sessionEndTs.AddMinutes(-EntryBlockMinutesBeforeClose);
            if (forceFlat)
            {
                tgt = 0;
            }
            else if (entryBlocked)
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
                    Time[0], sessEnd ? 1 : 0, T, Tpp, bmomPos, tgtRaw, tgt, cur, tiltState));

            // 7. FAIL CLOSED: no realtime order flow, ever (research mandate)
            if (State == State.Realtime)
                return;

            // 8. physical submission (never on the session's last bar: engine exit owns the close)
            if (sessEnd) return;
            if (CurrentBar < BarsRequiredToTrade) return;
            if (CurrentBars.Length < 2 || CurrentBars[1] < 1) return;
            lastTarget = tgt;
            SubmitNetChange(tgt);
        }

        // C3 (W18E): the EXECUTION series gets its own flatten authority when the decision
        // series has gone stale across the deadline (e.g. a signal-series data gap). It can
        // only ever move the target toward FLAT, and it is FAIL-CLOSED in realtime like every
        // other submission path in this file.
        private void ExecWatchdog()
        {
            if (State == State.Realtime) return;                 // C5: never in realtime
            if (execSessIter == null) return;
            if (CurrentBars.Length < 2 || CurrentBars[1] < 1) return;

            if (BarsArray[1].IsFirstBarOfSession || execSessionEndTs == DateTime.MinValue)
            {
                execSessIter.GetNextSession(Times[1][0], true);
                execSessionEndTs = execSessIter.ActualSessionEnd;
            }
            if (execSessionEndTs == DateTime.MinValue) return;

            DateTime execTs = Times[1][0];
            if (execTs < execSessionEndTs.AddMinutes(-ForcedFlatMinutesBeforeClose)) return;

            // Times[0][0]/CurrentBars[0], NEVER Time[0]/CurrentBar: the unindexed accessors are
            // BarsInProgress-relative and would return THIS series' own timestamp here, which
            // is exactly the defect that made W17B's _v3 watchdog a silent no-op.
            if (CurrentBars[0] < 0) return;
            DateTime decTs = Times[0][0];
            if (decTs >= execTs.AddMinutes(-DecisionStaleMinutes)) return;

            if (PhysicalPosition() == 0) return;
            lastTarget = 0;
            SubmitNetChange(0);
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
                    "# SolarWaveSMMaster_Canonical_v1 QW={0} tilt={1}/{2}/{3} short={4} band={5}",
                    QWeight, TiltSma, TiltMult, TiltRescale, ShortHalf, BmomBandDays));
                barLog.WriteLine("time,sess_end,T,Tpp,B,tgt_raw,tgt_ops,phys,tilt_state");
            }
            catch (Exception ex)
            {
                Print("SolarWaveSMMaster_Canonical_v1 bar log open failed: " + ex.Message);
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
                        w.WriteLine("# SolarWaveSMMaster_Canonical_v1 execs=" + execCount);
                        w.WriteLine("n,time,name,instrument,order_action,market_position,price,qty,commission,target");
                        w.Write(fillLog.ToString());
                        w.Flush();
                    }
                }
            }
            catch (Exception ex)
            {
                Print("SolarWaveSMMaster_Canonical_v1 export failed: " + ex.Message);
            }
        }

        #region Properties
        [NinjaScriptProperty]
        [Display(Name = "Exec Instrument", Order = 0, GroupName = "System")]
        public string ExecInstrument { get; set; }
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
        [NinjaScriptProperty] [Display(Name="Q Weight (canonical, MNQ per Q unit)", Order=11, GroupName="Allocator")]
        public double QWeight { get; set; }
        [NinjaScriptProperty] [Display(Name="BMom band days", Order=13, GroupName="Allocator")]
        public int BmomBandDays { get; set; }
        [NinjaScriptProperty] [Display(Name="Export Dir", Order=14, GroupName="Export")]
        public string ExportDir { get; set; }
        [NinjaScriptProperty] [Display(Name="Tag", Order=15, GroupName="Export")]
        public string Tag { get; set; }
        #endregion
    }
}
