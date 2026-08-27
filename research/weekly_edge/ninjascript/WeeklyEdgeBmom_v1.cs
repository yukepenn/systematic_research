#region Using declarations
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
#endregion

// =====================================================================================
//  WeeklyEdgeBmom_v1  -  campaign #7 WEEKLY_EDGE. The B-MOM leg run STANDALONE.
//
//  Derived from the validated WeeklyEdgeP1_v3 by REMOVING, not adding: the ratchet vote, the
//  range throttle, the delta gate and the causal quality sizing are all bypassed. What remains
//  is the B-MOM channel as a direct +-1 position, 1 contract, inside the SAME session box and
//  the SAME private fill ledger the P1 file was validated with.
//
//  IT TRADES BOTH DIRECTIONS. Measured on 2022-07..2026-07 by WE_W90 (committed artifact,
//  runs/WE_W90_BMOMSIDES/out/sides.txt): 518 long trades ($168,567, $325.4 each, 50.2 % win)
//  and 525 SHORT ($83,691, $159.4 each, 43.6 % win), 1,043 total. P1_v3 is long-only, so the
//  order and ledger blocks below are the one place this file adds rather than removes -
//  `myDir` carries the sign that P1 did not need.
//    CORRECTION: an earlier revision of this header read "573 long ($166,047, $289.8, 48.9 %) /
//    579 short ($86,216, $148.9, 43.4 %)". That came from an uncommitted heredoc and is
//    WITHDRAWN - it was 10 % high on trade count. The direction of the finding is unchanged.
//
//  WHAT W90 ALSO ESTABLISHED, and it belongs on this file rather than in a report nobody opens:
//    * the SHORT leg fails its own count- and contract-minute-matched specificity null (86th /
//      81st / 74th percentile against a 95th bar). It is additional roughly-independent events,
//      NOT a second information source. Median short trade is -$864.
//    * splitting the session box - one box per side - loses on all three legs and DOUBLES the
//      worst week (-$33,492 vs -$16,970). The single shared box below is correct and tested.
//    * neither side is individually significant (t = 0.69 long / 0.66 short over the trailing
//      24 months); only the combination is (full-window t = 2.42). Do not trade one side.
//    * 2026 is +$7/week for the whole object. This is a REGIME-LOCAL engine and that is the
//      single largest disclosed risk in carrying it.
//
//  WHY IT EXISTS: W86-W88 found that BMOM standalone paired with the X9a arm at 2:3 contracts
//  holds the corrected rolling gate in 92 % of 24-month windows and earns P1's money on roughly
//  half the contracts and 35-40 % of the drawdown. Its short leg is worth $86,216 and comes from
//  a completely different mechanism than the mirrored short sleeve the campaign tried and
//  rejected five times (W38, W39, W61, W75, W78).
//
//  THE ONE KNOWN DEVIATION FROM THE PYTHON, MEASURED BEFORE IT WAS WRITTEN
//    Python's `sfills` REVERSES IN ONE BAR: when the target flips +1 -> -1 it books the closing
//    trade at o[i] and opens the new one at o[i], same bar. 47 % of B-MOM's entries arrive that
//    way (519 of 1,105 direction changes).
//    But Python checks the session box AFTER booking the close, and if it trips it sets want = 0
//    and does NOT open. Measured: of 421 attempted reversals, the box trips on the closing leg
//    **374 times (88.8 %)**, so Python actually opens on only 47 of them.
//    A NinjaScript that reversed in one order would therefore open 374 positions the Python
//    never opens - far worse than being late. This file exits on the flip bar and submits the
//    new entry once the exit has settled and the box has been checked, which is exact for the
//    374 and ONE BAR LATE for the 47 - i.e. for 4.3 % of all entries. That is the whole
//    deviation and it is stated here rather than discovered in a parity run.
//
//  ORIGINAL P1_v3 HEADER FOLLOWS - the timestamp convention, the causality note and the fill
//  ledger description all still apply.
//  WeeklyEdgeP1_v3  -  campaign #7 WEEKLY_EDGE, the P1 object, transcribed from the Python.
//
//  THIS IS NOT SolarWaveOneContractNQ_v5. W44 established that the shipped strategy runs its
//  decision stack on a 3-MINUTE secondary series and is roughly half as active as this object
//  (137 flips against 285 over the same window, 73.19 % decision agreement). This file
//  implements the PYTHON object measured at 14.72 pts/session and must be validated against
//  THAT object, which is what runs/WE_W52_NINJASCRIPT does.
//
//  CLOSED FORM (verified bar-for-bar over 1,558,497 bars, max |difference| = 0.0)
//    The 32 voters apply the throttle and delta masks to the TARGET, after the decision stack,
//    so the whole ensemble collapses to
//        vote = nMemLong * nThrottlePass * (1 + deltaGate) / 32
//        vote >= 0.5   <=>   nMemLong * nThrottlePass * (1 + deltaGate) >= 16
//    Only FOUR combiners are needed, and the THIRTEEN ratchet members are SHARED, because a
//    member's state depends only on price and sigma and never on which set it belongs to.
//    The four member sets are prefixes of the same VolMult ladder: 5, 6, 7 and 13 members.
//
//  TIMESTAMP CONVENTION - the detail that silently breaks parity if it is missed
//    The Python substrate stamps a 1-minute bar with its START minute; NinjaTrader stamps it
//    with its END minute. Every comparison and every time-of-day key below therefore uses
//    PyTs = Time[0] - 1 minute. W44 lost a whole read to exactly this class of phase error on
//    the 3-minute grid, so it is made explicit here rather than assumed.
//
//  CAUSALITY
//    Calculate.OnBarClose: OnBarUpdate fires at a bar's CLOSE and a market order fills at the
//    NEXT bar's OPEN. Every feature is built from bar i-1 or earlier, exactly as the Python
//    lags them. Nothing reads the bar it fills on. The strategy also keeps its OWN fill ledger
//    (entry price, size, realised session P&L) so the session box reproduces the Python
//    fills_qexit arithmetic exactly instead of depending on when NinjaTrader updates
//    SystemPerformance.
//
//  Set ExportDir to write a per-bar decision ledger for bar-for-bar parity. Empty disables it.
// =====================================================================================
namespace NinjaTrader.NinjaScript.Strategies
{
    public class WeeklyEdgeBmom_v1 : Strategy
    {
        [NinjaScriptProperty] public int    VolPeriod      { get; set; }
        [NinjaScriptProperty] public double SMinTicks      { get; set; }
        [NinjaScriptProperty] public double SMaxTicks      { get; set; }
        [NinjaScriptProperty] public double StopMultiplier { get; set; }
        [NinjaScriptProperty] public int    TiltSma        { get; set; }
        [NinjaScriptProperty] public double TiltMult       { get; set; }
        [NinjaScriptProperty] public double TiltRescale    { get; set; }
        [NinjaScriptProperty] public double WSolar         { get; set; }
        [NinjaScriptProperty] public double WBmom          { get; set; }
        [NinjaScriptProperty] public int    BmomBandDays   { get; set; }
        [NinjaScriptProperty] public double EntryLevel     { get; set; }
        [NinjaScriptProperty] public double ExitLevel      { get; set; }
        [NinjaScriptProperty] public int    EntryBlockMin  { get; set; }
        [NinjaScriptProperty] public int    ForcedFlatMin  { get; set; }
        [NinjaScriptProperty] public double HaltDollars    { get; set; }
        [NinjaScriptProperty] public double TargetDollars  { get; set; }
        [NinjaScriptProperty] public double CommissionRT   { get; set; }
        [NinjaScriptProperty] public int    QualWindow     { get; set; }
        [NinjaScriptProperty] public int    QualMinHist    { get; set; }
        [NinjaScriptProperty] public bool   UseQualitySize { get; set; }
        [NinjaScriptProperty] public bool   UseSessionBox  { get; set; }
        [NinjaScriptProperty] public string ExportDir      { get; set; }
        [NinjaScriptProperty] public string Tag            { get; set; }

        private static readonly double[] VOLM = { 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30 };
        private static readonly int[] SETLEN = { 5, 6, 7, 13 };     // narrow5 / narrow6 / narrow7 / all13
        private const int NMEMB = 13, NSET = 4;

        // ---- shared ratchet members --------------------------------------------------
        private bool[]   mUp     = new bool[NMEMB];
        private double[] mAnchor = new double[NMEMB];
        private double[] mS      = new double[NMEMB];
        private int[]    mSig    = new int[NMEMB];
        private int[]    mPos    = new int[NMEMB];
        private int[]    mPend   = new int[NMEMB];
        private bool initialized = false;
        private long barCount = 0;

        // ---- sigma ---------------------------------------------------------------------
        private Queue<double> diffs = new Queue<double>();
        private double volSum = 0.0, prevClose = double.NaN;

        // ---- HTF tilt ------------------------------------------------------------------
        private List<double> sessCloses = new List<double>();
        private int tilt = 0;

        // ---- B-MOM ---------------------------------------------------------------------
        private int bmom = 0; private bool rthOpen = false;
        private double open0930 = 0.0, bmVpv = 0.0, bmVv = 0.0;
        private Dictionary<int, double> todaySlots = new Dictionary<int, double>();
        private Dictionary<int, List<double>> slotHist = new Dictionary<int, List<double>>();
        private int rthDays = 0;

        private int[] tgtPrev = new int[NSET];

        // ---- session state --------------------------------------------------------------
        private SessionIterator sessIter;
        private DateTime sessionEndTs = DateTime.MinValue;
        private double sessOpen = 0.0, curSessOpen = 0.0, prevSessRet = 0.0;
        private bool   haveSessHi = false;
        private double sessHiCur = 0.0, sessLoCur = 0.0;      // through THIS bar
        private double sessHiPrev = 0.0, sessLoPrev = 0.0;    // through the PREVIOUS bar
        private bool   havePrevExtremes = false;

        // ---- range throttle history -------------------------------------------------------
        private Dictionary<int, List<double>> rngHist = new Dictionary<int, List<double>>();
        private List<int> todKeys = new List<int>();
        private List<double> todRng = new List<double>();

        // ---- lagged carriers ---------------------------------------------------------------
        private double lagClose = double.NaN, lagAtr = double.NaN, lagVwap = double.NaN;
        private double lagRunLen = 0.0, lagCumDelta = 0.0, lagVolNorm = 1.0;
        private double runLen = 0.0; private int lastSgn = 0;
        private double cumDelta = 0.0, vwPv = 0.0, vwVv = 0.0;
        private Queue<double> trQ = new Queue<double>(); private double trSum = 0.0;
        private Queue<double> volQ = new Queue<double>(); private double volSum240 = 0.0;

        // ---- causal quality score ------------------------------------------------------------
        private List<double> qDistOpen = new List<double>(), qPrevRet = new List<double>(),
                             qRunLen = new List<double>(), qDistVwap = new List<double>(),
                             qDeltaMag = new List<double>();
        private int qCount = 0;

        // ---- our own fill ledger, mirroring Python fills_qexit ---------------------------------
        private const int ACT_NONE = 0, ACT_ENTER = 1, ACT_EXIT = 2;
        private int pendingAct = ACT_NONE, pendingSize = 1, pendingDir = 0;
        private double myEntryPx = 0.0; private int myQty = 0;
        private int myDir = 0;   // +1 long, -1 short, 0 flat. P1_v3 is long-only and has no equivalent.
        private double sessPnl = 0.0; private bool sessStopped = false;
        private int lastScore = 0;

        private StreamWriter export = null;

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = "WEEKLY_EDGE P1: 32-config long-only Solar vote in closed form, "
                            + "range throttle, delta gate, session box, causal quality sizing.";
                Name = "WeeklyEdgeBmom_v1";
                Calculate = Calculate.OnBarClose;
                EntriesPerDirection = 1;
                EntryHandling = EntryHandling.AllEntries;
                IsExitOnSessionCloseStrategy = false;
                IncludeCommission = true;
                BarsRequiredToTrade = 20;

                VolPeriod = 460; SMinTicks = 40; SMaxTicks = 1200; StopMultiplier = 179;
                TiltSma = 50; TiltMult = 1.25; TiltRescale = 0.9026;
                WSolar = 0.7086; WBmom = 2.83; BmomBandDays = 14;
                EntryLevel = 3.0; ExitLevel = 1.0;
                EntryBlockMin = 30; ForcedFlatMin = 21;
                HaltDollars = 1300.0; TargetDollars = 1000.0; CommissionRT = 4.36;
                QualWindow = 250; QualMinHist = 100;
                UseQualitySize = true; UseSessionBox = true;
                ExportDir = ""; Tag = "p1";
            }
            else if (State == State.DataLoaded)
            {
                // TickSize is only reliable once the instrument's data is loaded
                for (int m = 0; m < NMEMB; m++) mS[m] = StopMultiplier * TickSize;
                sessIter = new SessionIterator(Bars);
                if (!string.IsNullOrEmpty(ExportDir))
                {
                    try
                    {
                        Directory.CreateDirectory(ExportDir);
                        export = new StreamWriter(Path.Combine(ExportDir, "we_p1_" + Tag + ".csv"), false);
                        export.WriteLine("pyts,close,nMem,nThr,dL,ratio,voteOK,size,score,qty,sessPnl,stopped,tilt,bmom,t0,t1,t2,t3,sig0,pend0,anch0,s0");
                    }
                    catch (Exception) { export = null; }
                }
            }
            else if (State == State.Terminated)
            {
                if (export != null) { try { export.Flush(); export.Close(); } catch (Exception) { } export = null; }
            }
        }

        private static int RoundAway(double x)
        {
            return (int)(Math.Sign(x) * Math.Floor(Math.Abs(x) + 0.5));
        }

        private double Sigma() { return (diffs.Count >= 30) ? volSum / diffs.Count : double.NaN; }

        private double ResolveS(double mult)
        {
            double sg = Sigma();
            if (double.IsNaN(sg) || sg <= 0) return StopMultiplier * TickSize;
            return Math.Min(Math.Max(mult * sg, SMinTicks * TickSize), SMaxTicks * TickSize);
        }

        private static double Quantile(List<double> src, int window, double q)
        {
            int nAll = src.Count, start = Math.Max(0, nAll - window), k = nAll - start;
            if (k <= 0) return double.NaN;
            double[] a = new double[k]; src.CopyTo(start, a, 0, k); Array.Sort(a);
            if (k == 1) return a[0];
            double pos = q * (k - 1); int lo = (int)Math.Floor(pos); double frac = pos - lo;
            if (lo >= k - 1) return a[k - 1];
            return a[lo] + frac * (a[lo + 1] - a[lo]);
        }

        private static double MedianLast(List<double> src, int window)
        {
            int nAll = src.Count, start = Math.Max(0, nAll - window), k = nAll - start;
            if (k <= 0) return 0.0;
            double[] a = new double[k]; src.CopyTo(start, a, 0, k); Array.Sort(a);
            return (k % 2 == 1) ? a[k / 2] : 0.5 * (a[k / 2 - 1] + a[k / 2]);
        }

        protected override void OnBarUpdate()
        {
            if (BarsInProgress != 0) return;

            // NinjaTrader stamps a bar with its END minute; the Python substrate stamps it with
            // its START minute. Everything below is keyed on the Python convention.
            // VERIFIED, not assumed: the Python substrate stamps a session's first bar 18:01
            // and its last 17:00 for an 18:00->17:00 session, i.e. it is BAR-END stamped -
            // the same convention NinjaTrader uses. v1/v2 shifted by -1 minute as a defensive
            // fix for a difference that does not exist, and that shift WAS the phase error:
            // it armed B-MOM on the wrong bar (bmom agreement 95.3 %, sign inversions) and
            // moved every time-of-day key. No shift.
            DateTime pyTs = Time[0];
            bool firstBar = Bars.IsFirstBarOfSession;
            bool lastBar  = Bars.IsLastBarOfSession;

            // ---- 0. settle any order submitted on the previous bar; it filled at THIS open ----
            if (pendingAct == ACT_EXIT)
            {
                sessPnl += myDir * myQty * (Open[0] - myEntryPx) * Instrument.MasterInstrument.PointValue
                         - CommissionRT * myQty;
                myQty = 0; myDir = 0;
                if (UseSessionBox && (sessPnl <= -HaltDollars || sessPnl >= TargetDollars))
                    sessStopped = true;
            }
            else if (pendingAct == ACT_ENTER)
            {
                myEntryPx = Open[0]; myQty = pendingSize; myDir = pendingDir;
            }
            pendingAct = ACT_NONE;

            if (firstBar || sessionEndTs == DateTime.MinValue)
            {
                sessIter.GetNextSession(Time[0], true);
                sessionEndTs = sessIter.ActualSessionEnd;
            }

            // ---- 1. session reset -------------------------------------------------------------
            if (firstBar)
            {
                for (int k = 0; k < todKeys.Count; k++)
                {
                    List<double> lst;
                    if (!rngHist.TryGetValue(todKeys[k], out lst)) { lst = new List<double>(); rngHist[todKeys[k]] = lst; }
                    lst.Add(todRng[k]);
                    if (lst.Count > 200) lst.RemoveAt(0);
                }
                todKeys.Clear(); todRng.Clear();

                prevSessRet = (curSessOpen != 0.0 && !double.IsNaN(lagClose)) ? (lagClose - curSessOpen) : 0.0;
                curSessOpen = Open[0]; sessOpen = Open[0];
                haveSessHi = false; havePrevExtremes = false;
                cumDelta = 0.0; vwPv = 0.0; vwVv = 0.0;
                sessPnl = 0.0; sessStopped = false;
            }

            int hm  = pyTs.Hour * 10000 + pyTs.Minute * 100;
            int tod = pyTs.Hour * 60 + pyTs.Minute;
            double px = Close[0];

            // ---- 2. ratchet members ------------------------------------------------------------
            for (int m = 0; m < NMEMB; m++) mPos[m] = mPend[m];

            if (!double.IsNaN(prevClose))
            {
                double d = Math.Abs(px - prevClose);
                diffs.Enqueue(d); volSum += d;
                while (diffs.Count > VolPeriod) volSum -= diffs.Dequeue();
            }
            prevClose = px;

            for (int m = 0; m < NMEMB; m++)
            {
                mSig[m] = 0;
                if (!initialized) { mUp[m] = false; mAnchor[m] = px; mS[m] = ResolveS(VOLM[m]); continue; }
                if (mUp[m])
                {
                    if (px >= mAnchor[m]) mAnchor[m] = px;
                    else if (px < mAnchor[m] - mS[m])
                    { mUp[m] = false; mS[m] = ResolveS(VOLM[m]); mAnchor[m] = px; mSig[m] = -1; }
                }
                else
                {
                    if (px <= mAnchor[m]) mAnchor[m] = px;
                    else if (px > mAnchor[m] + mS[m])
                    { mUp[m] = true; mS[m] = ResolveS(VOLM[m]); mAnchor[m] = px; mSig[m] = 1; }
                }
            }
            if (!initialized) initialized = true;

            for (int m = 0; m < NMEMB; m++)
            {
                if (barCount < 20) { mPend[m] = mPos[m]; continue; }
                double xl = mUp[m] ? (mAnchor[m] - mS[m]) : (mAnchor[m] + mS[m]);
                if      (mPos[m] > 0 && px <= xl) mPend[m] = 0;
                else if (mPos[m] < 0 && px >= xl) mPend[m] = 0;
                else if (mPos[m] != 0)            mPend[m] = mPos[m];
                else                              mPend[m] = mSig[m];
            }

            // ---- 3. B-MOM -----------------------------------------------------------------------
            if (hm == 93100)
            {
                open0930 = Open[0]; bmVpv = 0.0; bmVv = 0.0; rthOpen = true;
                todaySlots.Clear(); bmom = 0;
            }
            if (rthOpen && hm >= 93100 && hm <= 160000)
            {
                bmVpv += px * Volume[0]; bmVv += Volume[0];
                double vw = (bmVv > 0) ? bmVpv / bmVv : px;
                todaySlots[hm] = Math.Abs(px - open0930);
                if (hm <= 155400 && rthDays >= BmomBandDays)
                {
                    List<double> past;
                    if (slotHist.TryGetValue(hm, out past) && past.Count > 0)
                    {
                        int kk = Math.Min(14, past.Count); double sum = 0.0;
                        for (int j = past.Count - kk; j < past.Count; j++) sum += past[j];
                        double mtod = sum / kk;
                        int s = 0;
                        if (px > Math.Max(open0930 + mtod, vw)) s = 1;
                        else if (px < Math.Min(open0930 - mtod, vw)) s = -1;
                        if (s != 0) bmom = s;
                    }
                }
                if (hm >= 155700 || lastBar) bmom = 0;
            }
            if (lastBar && rthOpen)
            {
                foreach (KeyValuePair<int, double> kv in todaySlots)
                {
                    List<double> lst;
                    if (!slotHist.TryGetValue(kv.Key, out lst)) { lst = new List<double>(); slotHist[kv.Key] = lst; }
                    lst.Add(kv.Value);
                    if (lst.Count > 60) lst.RemoveAt(0);
                }
                rthDays++; rthOpen = false;
            }

            // ---- 4. session end: zero members, update tilt ---------------------------------------
            if (lastBar)
            {
                for (int m = 0; m < NMEMB; m++) { mPos[m] = 0; mPend[m] = 0; }
                sessCloses.Add(px);
                if (sessCloses.Count > TiltSma)
                {
                    double sum = 0.0;
                    for (int j = sessCloses.Count - TiltSma; j < sessCloses.Count; j++) sum += sessCloses[j];
                    tilt = Math.Sign(px - sum / TiltSma);
                }
                if (sessCloses.Count > 600) sessCloses.RemoveAt(0);
            }

            // ---- 5. four combiners + hysteresis ---------------------------------------------------
            bool blocked   = pyTs >= sessionEndTs.AddMinutes(-EntryBlockMin);
            bool forceFlat = pyTs >= sessionEndTs.AddMinutes(-ForcedFlatMin);

            int nMemLong = 0;
            for (int s = 0; s < NSET; s++)
            {
                int len = SETLEN[s], sumNext = 0;
                for (int m = 0; m < len; m++) sumNext += mPend[m];
                int T = Math.Max(-10, Math.Min(10, RoundAway(sumNext / (double)len * 10.0)));
                double mm = (tilt != 0 && sumNext != 0 && Math.Sign(sumNext) == tilt) ? TiltMult : 1.0;
                int Tp = Math.Max(-13, Math.Min(13, RoundAway(T * mm * TiltRescale)));
                double M = WSolar * Tp + WBmom * bmom;

                int p = firstBar ? 0 : tgtPrev[s];
                int tgt = p;
                if (forceFlat) tgt = 0;
                else if (p == 0)
                {
                    if (!blocked)
                    {
                        if (M >= EntryLevel) tgt = 1;
                        else if (M <= -EntryLevel) tgt = -1;
                    }
                }
                else if (p > 0)
                {
                    if (M <= -EntryLevel && !blocked) tgt = -1;
                    else if (M <= ExitLevel) tgt = 0;
                }
                else
                {
                    if (M >= EntryLevel && !blocked) tgt = 1;
                    else if (M >= -ExitLevel) tgt = 0;
                }
                tgtPrev[s] = tgt;
                if (tgt > 0) nMemLong++;
            }

            // ---- 6. range throttle + delta gate ----------------------------------------------------
            double rngPrev = havePrevExtremes ? (sessHiPrev - sessLoPrev) : 0.0;
            double norm = 0.0; List<double> hist;
            if (rngHist.TryGetValue(tod, out hist) && hist.Count >= 20) norm = MedianLast(hist, 60);
            double ratio = (norm > 0) ? rngPrev / Math.Max(norm, 1e-9) : 1.0;

            int nThr = 1;                                    // the q = none voter always passes
            if (norm <= 0 || ratio >= 0.7) nThr++;
            if (norm <= 0 || ratio >= 0.8) nThr++;
            if (norm <= 0 || ratio >= 0.9) nThr++;

            int dL = (lagCumDelta >= 0) ? 1 : 0;

            // ---- BMOM STANDALONE: the vote, throttle and delta gate above are COMPUTED (so the
            // export stays comparable to P1_v3) but NOT USED. The position is the B-MOM channel.
            bool voteOK = (nMemLong * nThr * (1 + dL)) >= 16;   // computed, unused
            int wantDir = forceFlat ? 0 : bmom;
            if (UseSessionBox && sessStopped) wantDir = 0;

            // ---- 7. causal quality size, computed only at a genuine entry --------------------------
            int size = 1; lastScore = 0;           // BMOM standalone is always 1 contract
            bool wantLong = false;                 // P1's long-only path is disabled here

            if (false && myQty == 0 && wantLong && UseQualitySize)
            {
                double atr = double.IsNaN(lagAtr) ? 1e-9 : Math.Max(lagAtr, 1e-9);
                double fDistOpen = (lagClose - sessOpen) / atr;
                double fPrevRet  = prevSessRet;
                double fRunLen   = lagRunLen;
                double fDistVwap = double.IsNaN(lagVwap) ? 0.0 : (lagClose - lagVwap) / atr;
                double fDeltaMag = Math.Abs(lagCumDelta) / Math.Max(lagVolNorm, 1e-9);

                if (qCount >= QualMinHist)
                {
                    int sc = 0;
                    if (fDistOpen >= Quantile(qDistOpen, QualWindow, 2.0 / 3.0)) sc++;
                    if (fPrevRet  <= Quantile(qPrevRet,  QualWindow, 1.0 / 3.0)) sc++;
                    if (fRunLen   >= Quantile(qRunLen,   QualWindow, 0.9))       sc++;
                    if (fDistVwap >= Quantile(qDistVwap, QualWindow, 2.0 / 3.0)) sc++;
                    if (fDeltaMag >= Quantile(qDeltaMag, QualWindow, 2.0 / 3.0)) sc++;
                    lastScore = sc; size = (sc >= 3) ? 2 : 1;
                }
                qDistOpen.Add(fDistOpen); qPrevRet.Add(fPrevRet); qRunLen.Add(fRunLen);
                qDistVwap.Add(fDistVwap); qDeltaMag.Add(fDeltaMag); qCount++;
            }

            // ---- 8. orders, mirrored by our own ledger --------------------------------------------
            if (lastBar && myQty > 0)
            {
                // safety net: Python closes any open position at the session's last close
                if (myDir > 0) ExitLong(myQty, "XLsess", "L"); else ExitShort(myQty, "XSsess", "S");
                sessPnl += myDir * myQty * (Close[0] - myEntryPx) * Instrument.MasterInstrument.PointValue
                         - CommissionRT * myQty;
                myQty = 0; myDir = 0; pendingAct = ACT_NONE;
            }
            else if (myQty > 0 && wantDir != myDir)
            {
                // any change of direction exits first; the new entry is submitted on the NEXT
                // bar, exactly as the Python fill layer does (it never reverses in one order).
                if (myDir > 0) ExitLong(myQty, "XL", "L"); else ExitShort(myQty, "XS", "S");
                pendingAct = ACT_EXIT;
            }
            else if (myQty == 0 && wantDir != 0 && pendingAct == ACT_NONE)
            {
                pendingSize = 1; pendingDir = wantDir;
                if (wantDir > 0) EnterLong(1, "L"); else EnterShort(1, "S");
                pendingAct = ACT_ENTER;
            }

            if (export != null)
            {
                export.WriteLine(string.Format(CultureInfo.InvariantCulture,
                    "{0:yyyy-MM-dd HH:mm:ss},{1},{2},{3},{4},{5:F4},{6},{7},{8},{9},{10:F2},{11}"
                    + ",{12},{13},{14},{15},{16},{17},{18},{19},{20:F4},{21:F4}",
                    pyTs, px, nMemLong, nThr, dL, ratio, voteOK ? 1 : 0, size, lastScore,
                    myQty, sessPnl, sessStopped ? 1 : 0,
                    tilt, bmom, tgtPrev[0], tgtPrev[1], tgtPrev[2], tgtPrev[3],
                    mSig[0], mPend[0], mAnchor[0], mS[0]));
            }

            barCount++;
            CacheLagged();
        }

        // Everything the NEXT bar's decision may see is frozen here, at THIS bar's close.
        private void CacheLagged()
        {
            double c = Close[0], h = High[0], l = Low[0];

            // this bar's contribution to the session's realised range, recorded for the NEXT bar
            if (!haveSessHi) { sessHiCur = h; sessLoCur = l; haveSessHi = true; }
            else { sessHiCur = Math.Max(sessHiCur, h); sessLoCur = Math.Min(sessLoCur, l); }

            todKeys.Add(Time[0].Hour * 60 + Time[0].Minute);
            todRng.Add(havePrevExtremes ? (sessHiPrev - sessLoPrev) : 0.0);
            sessHiPrev = sessHiCur; sessLoPrev = sessLoCur; havePrevExtremes = true;

            double tr = double.IsNaN(lagClose) ? (h - l)
                      : Math.Max(h - l, Math.Max(Math.Abs(h - lagClose), Math.Abs(l - lagClose)));
            trQ.Enqueue(tr); trSum += tr;
            while (trQ.Count > 14) trSum -= trQ.Dequeue();
            lagAtr = trSum / trQ.Count;

            int sgn = double.IsNaN(lagClose) ? 0 : Math.Sign(c - lagClose);
            cumDelta += sgn * Volume[0];
            lagCumDelta = cumDelta;

            if (sgn != 0 && sgn == lastSgn) runLen += 1;
            else if (sgn != 0) runLen = 1;
            else runLen = 0;
            lastSgn = sgn;
            lagRunLen = runLen * (sgn > 0 ? 1 : (sgn < 0 ? -1 : 0));

            vwPv += c * Volume[0]; vwVv += Volume[0];
            lagVwap = (vwVv > 0) ? vwPv / vwVv : double.NaN;

            volQ.Enqueue(Volume[0]); volSum240 += Volume[0];
            while (volQ.Count > 240) volSum240 -= volQ.Dequeue();
            lagVolNorm = (volQ.Count >= 30) ? volSum240 / volQ.Count : 1.0;

            lagClose = c;
        }
    }
}
