// =====================================================================================================
// WeeklyEdgeBookM11_v1 - GENESIS II COMBINED BOOK at the ratified M_11 mapping
//                        (P1/PCT x 1 contract  +  XM_CONFLICT_v2 x 1 contract) on NQ.
//
// *** THIS CLASS IS NOT PARITY-CERTIFIED. ***
// The two certified objects are WeeklyEdgeP1PCT_v1.cs and WeeklyEdgeXMConflict_v2.cs. THEY remain
// the reference. This file exists so the owner can run the whole book in ONE Strategy Analyzer run.
//
// WHAT IS COPIED AND WHAT IS NEW
//   COPIED VERBATIM : every signal/state formula of both engines - the 32-voter closed form, the
//                     range throttle, the delta gate, the hysteresis, the per-contract W98 session
//                     box, the causal quality sizing, P1's entry-block/forced-flat clocks; and XM's
//                     09:31 anchor / 09:45 decision, the ES+RTY+YM sigma60 composite, the conflict
//                     rule, the staleness disqualification, the v2 early-close exit-bar test, the
//                     disaster stop and the clock exit. No threshold, formula or ordering changed.
//   NEW             : ONLY the order layer. Each engine's order calls are stripped and replaced by a
//                     per-bar TARGET (p1Target in {0,1,2}, xmTarget in {-1,0,+1}). The account is
//                     driven to netTarget = p1Target + xmTarget by unmanaged market orders on the
//                     delta. Each engine still keeps its OWN internal fill ledger exactly as the
//                     certified file does, so its state machine is decoupled from the account.
//
// THE ONE ECONOMIC DIFFERENCE - NETTING
//   Running the two certified strategies side by side holds TWO independent positions. This class
//   holds ONE netted position. On the minutes where the legs oppose (P1 long, XM short) the netted
//   book crosses fewer contracts, so it pays LESS commission/spread than the two strategies do
//   separately, and its NT8 trade list is NOT the union of the two certified trade lists. The
//   SIGNAL series are identical; the TRADE series is not. Do not quote this class's net as the
//   certified pair's net, and do not quote the certified pair's net as this class's.
//
// COLD START
//   DaysToLoad = 365 is set here (allowed: this class is not certified). P1's causal quality sizing
//   needs QualMinHist = 100 and ideally QualWindow = 250 prior entry observations before it will
//   ever size 2; XM's sigma60 needs SigmaMinHist = 20 prior sessions. A short load silently runs the
//   book in its warm-up regime.
//
// MERGE ADAPTATIONS THAT ARE NOT PURE COPIES (the honest list)
//   1. P1's unindexed accessors (Time[0], Open[0], Close[0], High[0], Low[0], Volume[0], Bars.*)
//      are rewritten to their BIP-explicit forms (Times[0][0], Opens[0][0], ..., BarsArray[0].*).
//      This file is multi-series, where unindexed accessors are BarsInProgress-relative. All P1
//      logic runs at BarsInProgress == 0, so the values are identical - but implicit is a known
//      silent-failure mode in this repo, so it is made explicit.
//   2. P1's TickSize / Instrument.MasterInstrument.PointValue are cached at DataLoaded from
//      BarsArray[0] (p1_tickSize / p1_pointValue). Same instrument, same numbers, no ambiguity.
//   3. XM's global early return `for i in 1..3: if (CurrentBars[i] < 1) return;` CANNOT be global
//      here - it would also skip P1's bar processing during the secondary series' warm-up. It is
//      applied as an XM-ONLY gate (xmSeriesReady). When it is false the XM block does nothing,
//      which is exactly what the certified XM did when it returned.
//   4. Colliding member/property names are prefixed p1_ / XM_ (ForcedFlatMin, CommissionRT,
//      pendingAct, myEntryPx, sessIter, sessionEndTs, export). ExportDir and Tag are SHARED - they
//      only name output files, and the two engines write different file stems.
//   5. Both certified engines run with BarsRequiredToTrade = 20. Under NT8 multi-series rules that
//      requirement now also has to be met by ES/RTY/YM before an order can go out. Only the first
//      handful of bars of the whole load can be affected, and P1 cannot trade there anyway
//      (barCount < 20 pins every ratchet member), but it is a real, stated difference.
//
// STATUS: RESEARCH_ONLY. Not enabled. Backtest account only. The owner alone enables real capital.
// ATTACH TO: NQ 1-minute Last, CME US Index Futures ETH template, "NinjaTrader Brokerage Lifetime"
//            commission, Standard fill, Calculate.OnBarClose.
// =====================================================================================================

#region Using declarations
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
#endregion

namespace NinjaTrader.NinjaScript.Strategies
{
    public class WeeklyEdgeBookM11_v1 : Strategy
    {
        // ================= BOOK-LEVEL CONTROLS =================
        [NinjaScriptProperty] public bool   EnableP1        { get; set; }
        [NinjaScriptProperty] public bool   EnableXM        { get; set; }
        [NinjaScriptProperty] public string ExportDir       { get; set; }
        [NinjaScriptProperty] public string Tag             { get; set; }

        // ================= P1/PCT PARAMETERS (certified values, unchanged) =================
        [NinjaScriptProperty] public int    VolPeriod        { get; set; }
        [NinjaScriptProperty] public double SMinTicks        { get; set; }
        [NinjaScriptProperty] public double SMaxTicks        { get; set; }
        [NinjaScriptProperty] public double StopMultiplier   { get; set; }
        [NinjaScriptProperty] public int    TiltSma          { get; set; }
        [NinjaScriptProperty] public double TiltMult         { get; set; }
        [NinjaScriptProperty] public double TiltRescale      { get; set; }
        [NinjaScriptProperty] public double WSolar           { get; set; }
        [NinjaScriptProperty] public double WBmom            { get; set; }
        [NinjaScriptProperty] public int    BmomBandDays     { get; set; }
        [NinjaScriptProperty] public double EntryLevel       { get; set; }
        [NinjaScriptProperty] public double ExitLevel        { get; set; }
        [NinjaScriptProperty] public int    EntryBlockMin    { get; set; }
        [NinjaScriptProperty] public int    P1_ForcedFlatMin { get; set; }
        [NinjaScriptProperty] public double HaltDollars      { get; set; }
        [NinjaScriptProperty] public double TargetDollars    { get; set; }
        [NinjaScriptProperty] public double P1_CommissionRT  { get; set; }
        [NinjaScriptProperty] public int    QualWindow       { get; set; }
        [NinjaScriptProperty] public int    QualMinHist      { get; set; }
        [NinjaScriptProperty] public bool   UseQualitySize   { get; set; }
        [NinjaScriptProperty] public bool   UseSessionBox    { get; set; }

        // ================= XM_CONFLICT PARAMETERS (certified values, unchanged) =================
        [NinjaScriptProperty] public string EsInstrument       { get; set; }
        [NinjaScriptProperty] public string RtyInstrument      { get; set; }
        [NinjaScriptProperty] public string YmInstrument       { get; set; }
        [NinjaScriptProperty] public int    AnchorHm           { get; set; }
        [NinjaScriptProperty] public int    DecisionHm         { get; set; }
        [NinjaScriptProperty] public int    ExitHm             { get; set; }
        [NinjaScriptProperty] public int    SigmaLookback      { get; set; }
        [NinjaScriptProperty] public int    SigmaMinHist       { get; set; }
        [NinjaScriptProperty] public int    MaxStaleMinutes    { get; set; }
        [NinjaScriptProperty] public int    XM_ForcedFlatMin   { get; set; }
        [NinjaScriptProperty] public double XM_CommissionRT    { get; set; }
        [NinjaScriptProperty] public double DisasterStopPoints { get; set; }
        [NinjaScriptProperty] public int    Qty                { get; set; }

        // ---- series indices, fixed by the order of the AddDataSeries calls
        private const int NQ = 0, ES = 1, RTY = 2, YM = 3;

        // ---- shared fill-ledger action codes. Both certified files declare the SAME three
        // ---- constants with the SAME values (0/1/2); one copy is kept, per-engine state is split.
        private const int ACT_NONE = 0, ACT_ENTER = 1, ACT_EXIT = 2;

        // =====================================================================================
        //  P1/PCT STATE  - transcribed field-for-field from WeeklyEdgeP1PCT_v1.cs
        // =====================================================================================
        private static readonly double[] VOLM = { 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30 };
        private static readonly int[] SETLEN = { 5, 6, 7, 13 };
        private const int NMEMB = 13, NSET = 4;

        private bool[]   mUp     = new bool[NMEMB];
        private double[] mAnchor = new double[NMEMB];
        private double[] mS      = new double[NMEMB];
        private int[]    mSig    = new int[NMEMB];
        private int[]    mPos    = new int[NMEMB];
        private int[]    mPend   = new int[NMEMB];
        private bool initialized = false;
        private long barCount = 0;

        private Queue<double> diffs = new Queue<double>();
        private double volSum = 0.0, prevClose = double.NaN;

        private List<double> sessCloses = new List<double>();
        private int tilt = 0;

        private int bmom = 0; private bool rthOpen = false;
        private double open0930 = 0.0, bmVpv = 0.0, bmVv = 0.0;
        private Dictionary<int, double> todaySlots = new Dictionary<int, double>();
        private Dictionary<int, List<double>> slotHist = new Dictionary<int, List<double>>();
        private int rthDays = 0;

        private int[] tgtPrev = new int[NSET];

        private SessionIterator p1_sessIter;
        private DateTime p1_sessionEndTs = DateTime.MinValue;
        private double sessOpen = 0.0, curSessOpen = 0.0, prevSessRet = 0.0;
        private bool   haveSessHi = false;
        private double sessHiCur = 0.0, sessLoCur = 0.0;
        private double sessHiPrev = 0.0, sessLoPrev = 0.0;
        private bool   havePrevExtremes = false;

        private Dictionary<int, List<double>> rngHist = new Dictionary<int, List<double>>();
        private List<int> todKeys = new List<int>();
        private List<double> todRng = new List<double>();

        private double lagClose = double.NaN, lagAtr = double.NaN, lagVwap = double.NaN;
        private double lagRunLen = 0.0, lagCumDelta = 0.0, lagVolNorm = 1.0;
        private double runLen = 0.0; private int lastSgn = 0;
        private double cumDelta = 0.0, vwPv = 0.0, vwVv = 0.0;
        private Queue<double> trQ = new Queue<double>(); private double trSum = 0.0;
        private Queue<double> volQ = new Queue<double>(); private double volSum240 = 0.0;

        private List<double> qDistOpen = new List<double>(), qPrevRet = new List<double>(),
                             qRunLen = new List<double>(), qDistVwap = new List<double>(),
                             qDeltaMag = new List<double>();
        private int qCount = 0;

        private int p1_pendingAct = ACT_NONE, p1_pendingSize = 1;
        private double p1_myEntryPx = 0.0; private int p1_myQty = 0;
        private double p1_sessPnl = 0.0; private bool p1_sessStopped = false;
        private int lastScore = 0;

        private double p1_tickSize = 0.25, p1_pointValue = 20.0;
        private StreamWriter p1_export = null;

        // =====================================================================================
        //  XM_CONFLICT STATE  - transcribed field-for-field from WeeklyEdgeXMConflict_v2.cs
        // =====================================================================================
        private double anchorNq;
        private double[] anchorX = new double[4];
        private bool anchorReady, decisionReady, sessionDisqualified;
        private DateTime xm_sessionEndTs = DateTime.MinValue;
        private SessionIterator xm_sessIter;

        private List<double>[] hist = new List<double>[4];

        private int xm_pendingAct = ACT_NONE, xm_pendingDir = 0;
        private double xm_myEntryPx = 0.0;
        private int xm_myPos = 0;
        private double xm_realizedPnl = 0.0;
        private bool instrumentMismatch = false;
        private StreamWriter xm_export = null;

        private double lastDrive = 0.0, lastComposite = double.NaN;
        private int lastConflict = 0, lastDesired = 0;

        // =====================================================================================
        //  BOOK / ORDER LAYER STATE  (the only genuinely new code in this file)
        // =====================================================================================
        private const string BOOK_ORDER_NAME = "BOOK";
        private List<Order> bookOrders = new List<Order>();
        private StreamWriter bookExport = null;

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = "GENESIS II combined book M_11: P1/PCT x1 + XM_CONFLICT_v2 x1, netted "
                            + "into one NQ position with unmanaged market orders. NOT parity-certified.";
                Name                         = "WeeklyEdgeBookM11_v1";
                Calculate                    = Calculate.OnBarClose;
                IsUnmanaged                  = true;
                EntriesPerDirection          = 1;
                EntryHandling                = EntryHandling.AllEntries;
                IsExitOnSessionCloseStrategy = false;
                IncludeCommission            = true;
                BarsRequiredToTrade          = 20;

                // NOT certified -> allowed to set, and required: P1's quality window needs 250 prior
                // entry observations and XM's sigma needs 20 prior sessions before either is warm.
                DaysToLoad                   = 365;

                EnableP1 = true; EnableXM = true;
                ExportDir = ""; Tag = "bookm11";

                // ---- P1/PCT certified defaults, byte-identical to WeeklyEdgeP1PCT_v1
                VolPeriod = 460; SMinTicks = 40; SMaxTicks = 1200; StopMultiplier = 179;
                TiltSma = 50; TiltMult = 1.25; TiltRescale = 0.9026;
                WSolar = 0.7086; WBmom = 2.83; BmomBandDays = 14;
                EntryLevel = 3.0; ExitLevel = 1.0;
                EntryBlockMin = 30; P1_ForcedFlatMin = 21;
                HaltDollars = 1300.0; TargetDollars = 1000.0; P1_CommissionRT = 4.36;
                QualWindow = 250; QualMinHist = 100;
                UseQualitySize = true; UseSessionBox = true;

                // ---- XM_CONFLICT_v2 certified defaults, byte-identical
                EsInstrument       = "ES 09-26";
                RtyInstrument      = "RTY 09-26";
                YmInstrument       = "YM 09-26";
                AnchorHm           = 93100;
                DecisionHm         = 94500;
                ExitHm             = 154500;
                SigmaLookback      = 60;
                SigmaMinHist       = 20;
                MaxStaleMinutes    = 3;
                XM_ForcedFlatMin   = 21;
                XM_CommissionRT    = 4.36;
                DisasterStopPoints = 0.0;     // OFF by default. No level has been selected.
                Qty                = 1;
            }
            else if (State == State.Configure)
            {
                // FIXED ORDER. BarsArray indices 1,2,3 are relied on everywhere below.
                AddDataSeries(EsInstrument,  BarsPeriodType.Minute, 1);
                AddDataSeries(RtyInstrument, BarsPeriodType.Minute, 1);
                AddDataSeries(YmInstrument,  BarsPeriodType.Minute, 1);
            }
            else if (State == State.DataLoaded)
            {
                p1_tickSize   = BarsArray[NQ].Instrument.MasterInstrument.TickSize;
                p1_pointValue = BarsArray[NQ].Instrument.MasterInstrument.PointValue;
                for (int m = 0; m < NMEMB; m++) mS[m] = StopMultiplier * p1_tickSize;
                p1_sessIter = new SessionIterator(BarsArray[NQ]);

                xm_sessIter = new SessionIterator(BarsArray[NQ]);
                for (int i = 0; i < 4; i++) hist[i] = new List<double>();

                // VERIFY the added series are what was asked for. A mismatch hard-blocks orders
                // rather than trading a silently wrong composite.
                string[] want = { null, EsInstrument, RtyInstrument, YmInstrument };
                if (BarsArray == null || BarsArray.Length < 4) instrumentMismatch = true;
                else
                {
                    for (int i = 1; i < 4; i++)
                    {
                        if (BarsArray[i] == null || BarsArray[i].Instrument == null
                            || BarsArray[i].Instrument.MasterInstrument == null)
                        { instrumentMismatch = true; break; }
                        string got = BarsArray[i].Instrument.FullName;
                        if (string.IsNullOrEmpty(got) || string.IsNullOrEmpty(want[i])
                            || !got.StartsWith(want[i].Split(' ')[0], StringComparison.OrdinalIgnoreCase))
                        { instrumentMismatch = true; break; }
                    }
                }

                if (!string.IsNullOrEmpty(ExportDir))
                {
                    try
                    {
                        Directory.CreateDirectory(ExportDir);
                        p1_export = new StreamWriter(Path.Combine(ExportDir, "we_p1pct_" + Tag + ".csv"), false);
                        p1_export.WriteLine("pyts,close,nMem,nThr,dL,ratio,voteOK,size,score,qty,sessPnl,stopped,tilt,bmom,t0,t1,t2,t3,sig0,pend0,anch0,s0");
                    }
                    catch (Exception) { p1_export = null; }
                    try
                    {
                        xm_export = new StreamWriter(Path.Combine(ExportDir, "we_xm_" + Tag + ".csv"), false);
                        xm_export.WriteLine("timestamp,nq_open,nq_high,nq_low,nq_close,"
                            + "es_close,es_move,rty_close,rty_move,ym_close,ym_move,"
                            + "nq_drive,broad_composite,conflict_flag,desired_direction,"
                            + "decision_ready,entry_request,exit_request,position,realized_pnl");
                    }
                    catch (Exception) { xm_export = null; }
                    try
                    {
                        bookExport = new StreamWriter(Path.Combine(ExportDir, "we_book_" + Tag + ".csv"), false);
                        bookExport.WriteLine("timestamp,close,p1_target,xm_target,net_target,acct_pos_before,"
                            + "delta,orders_sent,p1_qty,p1_want,p1_size,p1_sess_pnl,p1_stopped,"
                            + "xm_pos,xm_desired,xm_conflict,xm_disq,xm_mismatch,xm_series_ready");
                    }
                    catch (Exception) { bookExport = null; }
                }
            }
            else if (State == State.Terminated)
            {
                if (p1_export   != null) { try { p1_export.Flush();   p1_export.Close();   } catch (Exception) { } p1_export = null; }
                if (xm_export   != null) { try { xm_export.Flush();   xm_export.Close();   } catch (Exception) { } xm_export = null; }
                if (bookExport  != null) { try { bookExport.Flush();  bookExport.Close();  } catch (Exception) { } bookExport = null; }
            }
        }

        // ================= P1 helpers, verbatim =================
        private static int RoundAway(double x)
        {
            return (int)(Math.Sign(x) * Math.Floor(Math.Abs(x) + 0.5));
        }

        private double Sigma() { return (diffs.Count >= 30) ? volSum / diffs.Count : double.NaN; }

        private double ResolveS(double mult)
        {
            double sg = Sigma();
            if (double.IsNaN(sg) || sg <= 0) return StopMultiplier * p1_tickSize;
            return Math.Min(Math.Max(mult * sg, SMinTicks * p1_tickSize), SMaxTicks * p1_tickSize);
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

        // ================= XM helpers, verbatim =================
        private static double SampleStd(List<double> v, int lookback, int minHist)
        {
            int n = v.Count;
            if (n < minHist) return double.NaN;
            int k = Math.Min(lookback, n);
            double m = 0.0;
            for (int i = n - k; i < n; i++) m += v[i];
            m /= k;
            double s = 0.0;
            for (int i = n - k; i < n; i++) { double d = v[i] - m; s += d * d; }
            return (k > 1) ? Math.Sqrt(s / (k - 1)) : double.NaN;   // ddof = 1, matches pandas
        }

        /// <summary>latest secondary bar must be no older than MaxStaleMinutes vs the primary</summary>
        private bool SeriesFresh(int i, DateTime nqTs)
        {
            if (CurrentBars[i] < 1) return false;
            double age = (nqTs - Times[i][0]).TotalMinutes;
            return age >= -0.5 && age <= MaxStaleMinutes;
        }

        // ================= book order helpers (NEW) =================
        private bool BookOrderWorking()
        {
            for (int i = bookOrders.Count - 1; i >= 0; i--)
            {
                Order o = bookOrders[i];
                if (o == null) { bookOrders.RemoveAt(i); continue; }
                OrderState st = o.OrderState;
                if (st == OrderState.Filled || st == OrderState.Cancelled || st == OrderState.Rejected)
                    bookOrders.RemoveAt(i);
            }
            return bookOrders.Count > 0;
        }

        private int SubmitBook(OrderAction action, int quantity)
        {
            if (quantity <= 0) return 0;
            Order o = SubmitOrderUnmanaged(NQ, action, OrderType.Market, quantity, 0, 0, "", BOOK_ORDER_NAME);
            if (o != null) bookOrders.Add(o);
            return 1;
        }

        protected override void OnBarUpdate()
        {
            // ---- ALL logic is on the primary. The added series are read, never traded.
            if (BarsInProgress != NQ) return;
            if (CurrentBars[NQ] < 0) return;

            // XM's certified guards, applied as an XM-ONLY gate (see header adaptation #3).
            // BOTH of them: the certified file returns on `CurrentBars[NQ] < 1` AND on any
            // `CurrentBars[i] < 1`, i = 1..3. Carrying only the second would let XM arm one bar
            // earlier than the certified object does.
            bool xmSeriesReady = CurrentBars[NQ] >= 1;
            for (int i = 1; i < 4; i++) if (CurrentBars[i] < 1) xmSeriesReady = false;

            DateTime pyTs = Times[NQ][0];
            bool firstBar = BarsArray[NQ].IsFirstBarOfSession;
            bool lastBar  = BarsArray[NQ].IsLastBarOfSession;

            // =============================================================================
            //  ENGINE A : P1/PCT.  VERBATIM from WeeklyEdgeP1PCT_v1.cs, order calls stripped.
            // =============================================================================

            // ---- 0. settle any order submitted on the previous bar; it filled at THIS open ----
            if (p1_pendingAct == ACT_EXIT)
            {
                // W98 PER-CONTRACT BOX: the box accumulates pnl/u. Both the point term AND the
                // commission are per contract; dropping only one would be a third convention.
                p1_sessPnl += (Opens[NQ][0] - p1_myEntryPx) * p1_pointValue
                            - P1_CommissionRT;
                p1_myQty = 0;
                if (UseSessionBox && (p1_sessPnl <= -HaltDollars || p1_sessPnl >= TargetDollars))
                    p1_sessStopped = true;
            }
            else if (p1_pendingAct == ACT_ENTER)
            {
                p1_myEntryPx = Opens[NQ][0]; p1_myQty = p1_pendingSize;
            }
            p1_pendingAct = ACT_NONE;

            if (firstBar || p1_sessionEndTs == DateTime.MinValue)
            {
                p1_sessIter.GetNextSession(Times[NQ][0], true);
                p1_sessionEndTs = p1_sessIter.ActualSessionEnd;
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
                curSessOpen = Opens[NQ][0]; sessOpen = Opens[NQ][0];
                haveSessHi = false; havePrevExtremes = false;
                cumDelta = 0.0; vwPv = 0.0; vwVv = 0.0;
                p1_sessPnl = 0.0; p1_sessStopped = false;
            }

            int hm  = pyTs.Hour * 10000 + pyTs.Minute * 100;
            int tod = pyTs.Hour * 60 + pyTs.Minute;
            double px = Closes[NQ][0];

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
                open0930 = Opens[NQ][0]; bmVpv = 0.0; bmVv = 0.0; rthOpen = true;
                todaySlots.Clear(); bmom = 0;
            }
            if (rthOpen && hm >= 93100 && hm <= 160000)
            {
                bmVpv += px * Volumes[NQ][0]; bmVv += Volumes[NQ][0];
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
            bool blocked   = pyTs >= p1_sessionEndTs.AddMinutes(-EntryBlockMin);
            bool forceFlat = pyTs >= p1_sessionEndTs.AddMinutes(-P1_ForcedFlatMin);

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
            double norm = 0.0; List<double> rhist;
            if (rngHist.TryGetValue(tod, out rhist) && rhist.Count >= 20) norm = MedianLast(rhist, 60);
            double ratio = (norm > 0) ? rngPrev / Math.Max(norm, 1e-9) : 1.0;

            int nThr = 1;                                    // the q = none voter always passes
            if (norm <= 0 || ratio >= 0.7) nThr++;
            if (norm <= 0 || ratio >= 0.8) nThr++;
            if (norm <= 0 || ratio >= 0.9) nThr++;

            int dL = (lagCumDelta >= 0) ? 1 : 0;

            bool voteOK = (nMemLong * nThr * (1 + dL)) >= 16;

            // ---- 7. causal quality size, computed only at a genuine entry --------------------------
            int size = 1; lastScore = 0;
            bool wantLong = voteOK && !(UseSessionBox && p1_sessStopped);

            if (p1_myQty == 0 && wantLong && UseQualitySize)
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

            // ---- 8. TARGET instead of orders. The ledger is updated at exactly the sites where the
            //         certified file updated it, so P1's state machine is unchanged.
            int p1Target;
            if (lastBar && p1_myQty > 0)
            {
                // safety net: the Python reference closes any open position at the session's last close
                p1Target = 0;
                p1_sessPnl += (Closes[NQ][0] - p1_myEntryPx) * p1_pointValue
                            - P1_CommissionRT;
                p1_myQty = 0; p1_pendingAct = ACT_NONE;
            }
            else if (p1_myQty > 0 && !wantLong)
            {
                p1Target = 0; p1_pendingAct = ACT_EXIT;
            }
            else if (p1_myQty == 0 && wantLong && p1_pendingAct == ACT_NONE && EnableP1)
            {
                p1_pendingSize = size; p1Target = size; p1_pendingAct = ACT_ENTER;
            }
            else
            {
                p1Target = p1_myQty;     // hold whatever the ledger says we hold
            }
            if (!EnableP1) p1Target = 0;

            if (p1_export != null)
            {
                p1_export.WriteLine(string.Format(CultureInfo.InvariantCulture,
                    "{0:yyyy-MM-dd HH:mm:ss},{1},{2},{3},{4},{5:F4},{6},{7},{8},{9},{10:F2},{11}"
                    + ",{12},{13},{14},{15},{16},{17},{18},{19},{20:F4},{21:F4}",
                    pyTs, px, nMemLong, nThr, dL, ratio, voteOK ? 1 : 0, size, lastScore,
                    p1_myQty, p1_sessPnl, p1_sessStopped ? 1 : 0,
                    tilt, bmom, tgtPrev[0], tgtPrev[1], tgtPrev[2], tgtPrev[3],
                    mSig[0], mPend[0], mAnchor[0], mS[0]));
            }

            barCount++;
            CacheLagged();

            // =============================================================================
            //  ENGINE B : XM_CONFLICT_v2.  VERBATIM, order calls stripped.
            // =============================================================================
            int xmDesired = xm_myPos;
            int entryReq = 0, exitReq = 0;

            if (xmSeriesReady)
            {
                DateTime ts = Times[NQ][0];
                int xhm     = ts.Hour * 10000 + ts.Minute * 100;

                // ---- 0. settle whatever was submitted on the previous bar; it filled at THIS open
                if (xm_pendingAct == ACT_EXIT)
                {
                    xm_realizedPnl += xm_myPos * (Opens[NQ][0] - xm_myEntryPx)
                                    * p1_pointValue * Qty
                                    - XM_CommissionRT * Qty;
                    xm_myPos = 0;
                }
                else if (xm_pendingAct == ACT_ENTER)
                {
                    xm_myEntryPx = Opens[NQ][0];
                    xm_myPos = xm_pendingDir;
                }
                entryReq = (xm_pendingAct == ACT_ENTER) ? xm_pendingDir : 0;
                exitReq  = (xm_pendingAct == ACT_EXIT) ? 1 : 0;
                xm_pendingAct = ACT_NONE; xm_pendingDir = 0;

                xmDesired = xm_myPos;

                // ---- 1. session bookkeeping. Session-RELATIVE, never a hardcoded end-of-day clock.
                if (firstBar || xm_sessionEndTs == DateTime.MinValue)
                {
                    xm_sessIter.GetNextSession(ts, true);
                    xm_sessionEndTs = xm_sessIter.ActualSessionEnd;
                    anchorReady = false; decisionReady = false; sessionDisqualified = false;
                    lastDrive = 0.0; lastComposite = double.NaN;
                    lastConflict = 0; lastDesired = 0;
                }
                bool xmForceFlat = ts >= xm_sessionEndTs.AddMinutes(-XM_ForcedFlatMin);

                // ---- 2. the ANCHOR bar (09:31): its OPEN is the 09:30:00 print
                if (xhm == AnchorHm && !anchorReady)
                {
                    bool fresh = true;
                    for (int i = 1; i < 4; i++) if (!SeriesFresh(i, ts)) fresh = false;
                    if (!fresh) sessionDisqualified = true;     // no stale forward-fill, ever
                    else
                    {
                        anchorNq = Opens[NQ][0];
                        for (int i = 1; i < 4; i++) anchorX[i] = Closes[i][0];
                        anchorReady = true;
                    }
                }

                // ---- 3. the DECISION bar (09:45)
                if (xhm == DecisionHm && anchorReady && !decisionReady && !sessionDisqualified)
                {
                    bool fresh = true;
                    for (int i = 1; i < 4; i++) if (!SeriesFresh(i, ts)) fresh = false;
                    if (!fresh) sessionDisqualified = true;
                    else
                    {
                        double drive = Math.Sign(Closes[NQ][0] - anchorNq);
                        double acc = 0.0; int cnt = 0;
                        for (int i = 1; i < 4; i++)
                        {
                            if (anchorX[i] <= 0 || Closes[i][0] <= 0) continue;
                            double r = Math.Log(Closes[i][0] / anchorX[i]);
                            double sg = SampleStd(hist[i], SigmaLookback, SigmaMinHist);
                            if (!double.IsNaN(sg) && sg > 1e-12) { acc += r / sg; cnt++; }
                            hist[i].Add(r);          // appended AFTER use -> today is never in its own sigma
                        }
                        double comp = (cnt > 0) ? acc / cnt : double.NaN;
                        double xs = double.IsNaN(comp) ? 0.0 : Math.Sign(comp);
                        lastDrive = drive; lastComposite = comp;
                        lastConflict = (xs != 0.0 && drive != 0.0 && xs != drive) ? 1 : 0;
                        lastDesired = (lastConflict == 1) ? (int)drive : 0;
                        decisionReady = true;

                        // v2 PARITY FIX (WE_XM_PARITY_20260827): drop any session whose 15:45/15:46
                        // exit bar does not exist. CAUSAL - sessionEndTs comes from the trading-hours
                        // template and is known at 09:45.
                        DateTime exitTs = ts.Date.AddMinutes((ExitHm / 10000) * 60
                                                           + ((ExitHm / 100) % 100) + 1);
                        bool exitBarExists = exitTs < xm_sessionEndTs.AddMinutes(-XM_ForcedFlatMin);
                        if (!exitBarExists) lastDesired = 0;

                        if (lastDesired != 0 && xm_myPos == 0 && !xmForceFlat && !instrumentMismatch
                            && EnableXM)
                        {
                            xm_pendingAct = ACT_ENTER; xm_pendingDir = lastDesired;
                            xmDesired = lastDesired;
                        }
                    }
                }

                // ---- 4. the DISASTER stop. OPERATIONAL, not alpha. OFF unless the owner sets it.
                if (xm_myPos != 0 && DisasterStopPoints > 0.0 && xm_pendingAct == ACT_NONE)
                {
                    double adverse = xm_myPos * (Lows[NQ][0] - xm_myEntryPx);
                    if (xm_myPos < 0) adverse = xm_myPos * (Highs[NQ][0] - xm_myEntryPx);
                    if (adverse <= -DisasterStopPoints)
                    {
                        xm_pendingAct = ACT_EXIT;
                        xmDesired = 0;
                    }
                }

                // ---- 5. the ALPHA exit: the clock, and nothing else
                if (xm_myPos != 0 && xm_pendingAct == ACT_NONE && (xhm >= ExitHm || xmForceFlat || lastBar))
                {
                    xm_pendingAct = ACT_EXIT;
                    xmDesired = 0;
                }

                // ---- 6. per-bar export: SIGNAL and DECISION states, not just P&L
                if (xm_export != null)
                {
                    CultureInfo ci = CultureInfo.InvariantCulture;
                    double esM  = (anchorReady && anchorX[ES]  > 0) ? Math.Log(Closes[ES][0]  / anchorX[ES])  : double.NaN;
                    double rtyM = (anchorReady && anchorX[RTY] > 0) ? Math.Log(Closes[RTY][0] / anchorX[RTY]) : double.NaN;
                    double ymM  = (anchorReady && anchorX[YM]  > 0) ? Math.Log(Closes[YM][0]  / anchorX[YM])  : double.NaN;
                    xm_export.WriteLine(string.Join(",",
                        ts.ToString("yyyy-MM-dd HH:mm:ss", ci),
                        Opens[NQ][0].ToString(ci), Highs[NQ][0].ToString(ci),
                        Lows[NQ][0].ToString(ci),  Closes[NQ][0].ToString(ci),
                        Closes[ES][0].ToString(ci),  esM.ToString(ci),
                        Closes[RTY][0].ToString(ci), rtyM.ToString(ci),
                        Closes[YM][0].ToString(ci),  ymM.ToString(ci),
                        lastDrive.ToString(ci), lastComposite.ToString(ci),
                        lastConflict.ToString(ci), lastDesired.ToString(ci),
                        (decisionReady ? 1 : 0).ToString(ci),
                        entryReq.ToString(ci), exitReq.ToString(ci),
                        xm_myPos.ToString(ci), xm_realizedPnl.ToString(ci)));
                }
            }

            int xmTarget = xmDesired * Qty;
            if (!EnableXM || instrumentMismatch || !xmSeriesReady) xmTarget = 0;

            // =============================================================================
            //  BOOK : reconcile the account to netTarget with unmanaged market orders.
            //  Stateless and self-healing: delta is always recomputed from the ACTUAL account
            //  position, so a skipped or rejected order is corrected on the next bar.
            // =============================================================================
            int netTarget = p1Target + xmTarget;          // range -1 .. +3 at the M_11 mapping

            int cur = 0;
            if (Position.MarketPosition == MarketPosition.Long)       cur =  Position.Quantity;
            else if (Position.MarketPosition == MarketPosition.Short) cur = -Position.Quantity;

            int delta = netTarget - cur;
            int ordersSent = 0;

            if (delta != 0 && CurrentBars[NQ] >= BarsRequiredToTrade && !BookOrderWorking())
            {
                if (cur >= 0 && netTarget >= 0)
                {
                    if (netTarget > cur) ordersSent += SubmitBook(OrderAction.Buy,  netTarget - cur);
                    else                 ordersSent += SubmitBook(OrderAction.Sell, cur - netTarget);
                }
                else if (cur <= 0 && netTarget <= 0)
                {
                    if (netTarget < cur) ordersSent += SubmitBook(OrderAction.SellShort,  cur - netTarget);
                    else                 ordersSent += SubmitBook(OrderAction.BuyToCover, netTarget - cur);
                }
                else if (cur > 0 && netTarget < 0)
                {
                    // crossing: close the long, then open the short. Two market orders, same bar,
                    // both fill at the next open. Split so NT8 pairs the trades correctly.
                    ordersSent += SubmitBook(OrderAction.Sell,      cur);
                    ordersSent += SubmitBook(OrderAction.SellShort, -netTarget);
                }
                else
                {
                    ordersSent += SubmitBook(OrderAction.BuyToCover, -cur);
                    ordersSent += SubmitBook(OrderAction.Buy,        netTarget);
                }
            }

            if (bookExport != null)
            {
                bookExport.WriteLine(string.Format(CultureInfo.InvariantCulture,
                    "{0:yyyy-MM-dd HH:mm:ss},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11:F2},{12}"
                    + ",{13},{14},{15},{16},{17},{18}",
                    pyTs, px, p1Target, xmTarget, netTarget, cur, delta, ordersSent,
                    p1_myQty, wantLong ? 1 : 0, size, p1_sessPnl, p1_sessStopped ? 1 : 0,
                    xm_myPos, xmDesired, lastConflict, sessionDisqualified ? 1 : 0,
                    instrumentMismatch ? 1 : 0, xmSeriesReady ? 1 : 0));
            }
        }

        // Everything the NEXT bar's decision may see is frozen here, at THIS bar's close.
        // VERBATIM from WeeklyEdgeP1PCT_v1.cs, accessors made BIP-explicit.
        private void CacheLagged()
        {
            double c = Closes[NQ][0], h = Highs[NQ][0], l = Lows[NQ][0];

            // this bar's contribution to the session's realised range, recorded for the NEXT bar
            if (!haveSessHi) { sessHiCur = h; sessLoCur = l; haveSessHi = true; }
            else { sessHiCur = Math.Max(sessHiCur, h); sessLoCur = Math.Min(sessLoCur, l); }

            todKeys.Add(Times[NQ][0].Hour * 60 + Times[NQ][0].Minute);
            todRng.Add(havePrevExtremes ? (sessHiPrev - sessLoPrev) : 0.0);
            sessHiPrev = sessHiCur; sessLoPrev = sessLoCur; havePrevExtremes = true;

            double tr = double.IsNaN(lagClose) ? (h - l)
                      : Math.Max(h - l, Math.Max(Math.Abs(h - lagClose), Math.Abs(l - lagClose)));
            trQ.Enqueue(tr); trSum += tr;
            while (trQ.Count > 14) trSum -= trQ.Dequeue();
            lagAtr = trSum / trQ.Count;

            int sgn = double.IsNaN(lagClose) ? 0 : Math.Sign(c - lagClose);
            cumDelta += sgn * Volumes[NQ][0];
            lagCumDelta = cumDelta;

            if (sgn != 0 && sgn == lastSgn) runLen += 1;
            else if (sgn != 0) runLen = 1;
            else runLen = 0;
            lastSgn = sgn;
            lagRunLen = runLen * (sgn > 0 ? 1 : (sgn < 0 ? -1 : 0));

            vwPv += c * Volumes[NQ][0]; vwVv += Volumes[NQ][0];
            lagVwap = (vwVv > 0) ? vwPv / vwVv : double.NaN;

            volQ.Enqueue(Volumes[NQ][0]); volSum240 += Volumes[NQ][0];
            while (volQ.Count > 240) volSum240 -= volQ.Dequeue();
            lagVolNorm = (volQ.Count >= 30) ? volSum240 / volQ.Count : 1.0;

            lagClose = c;
        }
    }
}
