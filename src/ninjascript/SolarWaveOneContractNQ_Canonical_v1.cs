// SolarWaveOneContractNQ_Canonical_v1 — EQV04 research-only executable twin of
// SolarWaveOneContractNQ_v5.
//
// Per research/system_master/CANONICAL_MATHEMATICAL_SPEC.md (derived from EQV01's exhaustive
// finite-state proof, 729/729 states, EXACT_EQUIVALENCE): the incumbent's continuous
// `M = WSolar*Tp + WBmom*bmomPos` (WSolar=0.7086, WBmom=2.83) with hysteresis thresholds
// EntryLevel=3.0/ExitLevel=1.0 is replaced here by the proven-exact ALWAYS-INTEGER form
// `Q = Tp + 4*bmomPos`, with hysteresis directly on Q at integer thresholds 5/1 (entry/exit) --
// robust margin, not a thin one (closest any real M value comes to a decision boundary is
// 0.1612, ~18x the max spread the WBmom/WSolar~4 approximation could introduce). TiltRescale
// 0.9026 is replaced by its proven-exact substitute 0.91. THIS IS THE ONLY DECISION-LOGIC
// CHANGE. Every other line (ops rules, BMOM computation, session handling, order submission,
// execution watchdog, instrument guard) is byte-identical to the incumbent, kept that way
// deliberately so this file's sole purpose -- proving executable parity between the real and
// canonical representations -- has the smallest possible diff surface to audit. The incumbent
// SolarWaveOneContractNQ_v5.cs remains the sole source of truth for live/backtest behavior;
// this object is ENGINEERING_ONLY / EQV04, not a promotion, not a parameter change, and not
// intended for standalone use.
//
// ==========================================================================================
// ORIGINAL SolarWaveOneContractNQ_v5 HEADER (kept verbatim below for provenance/diff traceability)
// ==========================================================================================
//
// SolarWaveOneContractNQ_v5 — Product B BEST_ONE_NQ, C4-compliance rebuild.
//
// SUPERSEDES SolarWaveOneContractNQ_Final. Frozen spec: runs/W17_C4_COMPLIANCE/spec.yaml
// (committed at c8330dc BEFORE this file was written). Per that spec's V1-R3 rule this is a
// NEW OBJECT, not a corrected old one; its metrics are not comparable to the pre-fix
// $303,449.00 headline and it is NOT parity-certified until V1-R4 re-parity passes — hence
// _v2, not _Final (NAMING.md reserves _Final for a parity-PASSED shipped artifact).
//
// WHAT CHANGED, AND ONLY THIS:
//   The two session-clock constants are now SESSION-RELATIVE instead of hardcoded:
//        entry block : hm >= 163000  ->  Time[0] >= sessionEnd - 30 min
//        forced flat : hm >= 163900  ->  Time[0] >= sessionEnd - 21 min
//   On a normal 17:00 ET CME Globex close these evaluate to EXACTLY 16:30 and 16:39, so
//   behaviour on all 1,095 normal dev sessions is unchanged by construction. Only the 43
//   holiday early-close sessions (31 at 13:00 ET, 9 at 13:15, 2 at 09:15, 1 at 09:30 —
//   full enumeration in runs/W17_C4_COMPLIANCE/REPORT.md) behave differently.
//
// WHY: BROKER FACT, NinjaTrader Brokerage Lifetime — intraday margin ends 15 minutes prior
// to session close and holiday early closes do NOT extend it; positions must meet INITIAL
// margin ($43,433.67/NQ vs $1,000 intraday) 15 minutes before the EARLY close. The old
// clock-hardcoded rule never fires on an early-close session, so the position was closed
// only by the ExitOnSessionCloseSeconds=30 engine backstop — which fires 30 seconds before
// that close, i.e. ~14.5 minutes INSIDE the initial-margin window. Measured on the real NT8
// trade list: 16 such breaches for BEST_ONE_NQ across the dev window. This file removes them.
// The 21-minute figure preserves the existing 6-minute order-routing buffer ahead of the
// 15-minute broker deadline (research/operational/day_margin_variant/MARGIN_RULES.md §3.1
// recommends 5-7 minutes); it is FROZEN and is not a searched parameter.
//
// NOT CHANGED: every signal / allocator / threshold / hysteresis constant, the realtime
// fail-closed guard, the instrument guard, the effective-parameter logging, and
// IsExitOnSessionCloseStrategy/ExitOnSessionCloseSeconds (kept as a backstop).
//
//     M = WSolar * T' + WBmom * B      (defaults 0.7086 / 2.83, frozen winner arithmetic)
//     T' = clamp(round(T * m * TiltRescale), +/-13), T = round(10 * mean member pending pos)
//     m  = TiltMult when sign(member vote) == prior-session daily SMA(TiltSma) state, else 1
//     B  = frozen W8-1 B-MOM position in {-1, 0, +1}
// Rule (frozen: runs/SM14_ONELOT_DAYMARGIN/spec.yaml, seq 318):
//     LONG 1 when flat and M >= EntryLevel; SHORT 1 when flat and M <= -EntryLevel;
//     flip on opposite entry level; exit flat when M retreats through ExitLevel.
// ATTACH TO: NQ 09-26 (or the then-current front NQ contract) execution chart, 3-MINUTE
// bars, CME US Index Futures ETH template.
// HISTORICAL research result — not a forward guarantee. Regime monitors apply.
// HOT-RELOAD: version class per edit.
// SAFETY: research/backtest only. FAILS CLOSED in realtime. Live enablement is a separate,
// explicit, owner-authorized decision — see research/system_master/LIVE_READINESS_CHECKLIST.md.
// BUILD TAG: SolarWaveOneContractNQ_v5 2026-08-09 (W17 C4-compliance rebuild).

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
    public class SolarWaveOneContractNQ_Canonical_v1 : Strategy
    {
        private const string BuildTag = "SolarWaveOneContractNQ_Canonical_v1 2026-08-10";
        private const string ExpectedInstrumentPrefix = "NQ";

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

        // Session-end tracking for the early-close-aware flatten.
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
                Name = "SolarWaveOneContractNQ_Canonical_v1";
                Calculate = Calculate.OnBarClose;
                IsExitOnSessionCloseStrategy = true;
                ExitOnSessionCloseSeconds = 30;
                BarsRequiredToTrade = 20;
                IsInstantiatedOnEachOptimizationIteration = false;

                SignalInstrument = "NQ 09-26";
                StopMultiplier = 179; SlowdownScan = 5; WeakWeakSplit = 10;
                VolPeriod = 460; SMinTicks = 40; SMaxTicks = 1200;
                TiltSma = 50; TiltMult = 1.25; TiltRescale = 0.91;
                BmomBandDays = 14;
                EntryLevelQ = 5; ExitLevelQ = 1; // canonical integer form of frozen seq-318 EntryLevel/ExitLevel
                ExportDir = ""; Tag = "nq_canonical_v1";
            }
            else if (State == State.Configure)
            {
                AddDataSeries(SignalInstrument, BarsPeriodType.Minute, 3);
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
                sessIter = new SessionIterator(BarsArray[1]);
                execSessionEndTs = DateTime.MinValue;
                execSessIter = new SessionIterator(BarsArray[0]);

                string execName = Instrument != null && Instrument.MasterInstrument != null
                    ? Instrument.MasterInstrument.Name : "";
                instrumentMismatch = !execName.StartsWith(ExpectedInstrumentPrefix,
                    StringComparison.OrdinalIgnoreCase);
                if (instrumentMismatch)
                    Print(string.Format("{0}: ERROR instrument mismatch, attached to '{1}', " +
                        "expected prefix '{2}' -- this build will not trade.",
                        BuildTag, execName, ExpectedInstrumentPrefix));

                Print(string.Format(
                    "{0} | ExecInstrument={1} | SignalInstrument={2} | StopMultiplier={3} | " +
                    "SlowdownScan={4} | WeakWeakSplit={5} | VolPeriod={6} | SMinTicks={7} | " +
                    "SMaxTicks={8} | TiltSma={9} | TiltMult={10} | TiltRescale={11} | " +
                    "EntryLevelQ={12} | ExitLevelQ={13} | BmomBandDays={14} | " +
                    "EntryBlockMinBeforeClose={15} | FlatMinBeforeClose={16}",
                    BuildTag, execName, SignalInstrument, StopMultiplier, SlowdownScan,
                    WeakWeakSplit, VolPeriod, SMinTicks, SMaxTicks, TiltSma, TiltMult,
                    TiltRescale, EntryLevelQ, ExitLevelQ, BmomBandDays,
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
            if (Position.MarketPosition == MarketPosition.Long) return Position.Quantity;
            if (Position.MarketPosition == MarketPosition.Short) return -Position.Quantity;
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
            if (tgt == 0) { if (c > 0) ExitLong(0, c, "XL", ""); else ExitShort(0, -c, "XS", ""); }
            else if (tgt > 0) EnterLong(0, 1, "L");
            else EnterShort(0, 1, "S");
        }

        // W17B execution-series flatten watchdog. Execution series = index 0 (the chart this
        // is attached to), decision/signal series = index 1. Can ONLY move the position
        // toward flat: it never opens, sizes up, or reverses. Inert unless the decision
        // series has gone stale (data gap). Present here for structural symmetry with the
        // MNQ sibling; on this object both series are the same instrument, so it is expected
        // never to fire -- which the W17B run verifies rather than assumes.
        private void ExecWatchdog()
        {
            if (State == State.Realtime) return;
            if (instrumentMismatch) return;
            if (CurrentBar < 1) return;
            if (CurrentBars.Length < 2 || CurrentBars[1] < 1) return;

            if (Bars.IsFirstBarOfSession || execSessionEndTs == DateTime.MinValue)
            {
                execSessIter.GetNextSession(Time[0], true);
                execSessionEndTs = execSessIter.ActualSessionEnd;
            }
            if (execSessionEndTs == DateTime.MinValue) return;

            DateTime execTs = Time[0];
            if (execTs < execSessionEndTs.AddMinutes(-ForcedFlatMinutesBeforeClose)) return;

            DateTime decTs = Times[1][0];
            if (decTs >= execTs.AddMinutes(-DecisionStaleMinutes)) return;   // decision series current

            if (PhysicalPosition() == 0) return;
            lastTarget = 0;
            SubmitTarget(0);
        }

        protected override void OnBarUpdate()
        {
            if (BarsInProgress == 0)
            {
                ExecWatchdog();
                return;
            }
            if (BarsInProgress != 1)
                return;
            if (CurrentBars[1] < 1)
                return;

            // Session-end tracking: refresh on the first bar of each session of the decision
            // series, so the flatten schedule follows the ACTUAL close (17:00 normally,
            // 13:00 / 13:15 / 09:15 / 09:30 on the 43 holiday early closes in the dev window).
            if (BarsArray[1].IsFirstBarOfSession || sessionEndTs == DateTime.MinValue)
            {
                sessIter.GetNextSession(Times[1][0], true);
                sessionEndTs = sessIter.ActualSessionEnd;
            }

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
            int Q = Tp + 4 * bmomPos;

            if (CurrentBars[0] < 1) return;
            int p = PhysicalPosition();
            int tgt = p;

            // Session-relative ops rule. On a 17:00 close these are exactly 16:30 / 16:39,
            // reproducing the pre-fix constants bar-for-bar on every normal session.
            DateTime nowTs = Times[1][0];
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
                    if (Q >= EntryLevelQ) tgt = 1;
                    else if (Q <= -EntryLevelQ) tgt = -1;
                }
            }
            else if (p > 0)
            {
                if (Q <= -EntryLevelQ && !entryBlocked) tgt = -1;
                else if (Q <= ExitLevelQ) tgt = 0;
            }
            else
            {
                if (Q >= EntryLevelQ && !entryBlocked) tgt = 1;
                else if (Q >= -ExitLevelQ) tgt = 0;
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
        [Display(Name = "Signal Instrument", Order = 0, GroupName = "System")]
        public string SignalInstrument { get; set; }
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
        [NinjaScriptProperty] [Display(Name="BMom band days", Order=12, GroupName="Allocator")]
        public int BmomBandDays { get; set; }
        [NinjaScriptProperty] [Display(Name="Entry level Q (canonical integer)", Order=13, GroupName="OneLot")]
        public int EntryLevelQ { get; set; }
        [NinjaScriptProperty] [Display(Name="Exit level Q (canonical integer)", Order=14, GroupName="OneLot")]
        public int ExitLevelQ { get; set; }
        #endregion
    }
}
