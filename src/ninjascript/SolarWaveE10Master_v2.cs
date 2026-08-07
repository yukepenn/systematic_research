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

// SolarWaveE10Master_v2 — the R5-E10 executable champion as ONE NinjaScript strategy.
//
// 13 VIRTUAL SolarWaveOpenV3 member state machines (VolMult 6..30 step 2, ThresholdMode 1,
// VolPeriod 460, clamp [SMinTicks, SMaxTicks] ticks, AnchorMode 0 = running close extreme,
// EntrySignalType 1, StartUp = false, session-close flat) are updated on every PRIMARY
// (NQ 3-min) bar close. The physical target is round(10 * mean virtual position), clamped
// [-10, +10], executed as NET CHANGES in MNQ on an added same-period series via the managed
// approach (barsInProgressIndex = 1 overloads).
//
// Virtual member fill mechanics replicate the engine behaviour proven from the committed
// AUDIT02_V3_SWEEP_B ledgers:
//   * decision at bar N close -> virtual fill at bar N+1 open (Calculate.OnBarClose market);
//   * orders pending at a session's LAST bar close never fill (zero first-bar-of-session
//     fills in 16,984 member executions) -> pendings are dropped at session close;
//   * session-close engine exits execute AT the close -> members zeroed on the last bar.
// The physical MNQ position is flattened by the engine (IsExitOnSessionCloseStrategy).
//
// The vol/anchor/signal code is transplanted VERBATIM from SolarWaveOpenV3 (same arithmetic
// order, same MaximumBarsLookBack) so every double is bit-identical to the audited members.
// sigma460 is shared (single computation per primary bar); each member samples it at ITS
// trend birth via ResolveS(volMult).
//
// Exports (ExportDir):
//   <Tag>_bars.csv  : per-primary-bar ledger — time, 13 member positions AT bar close,
//                     sum, close target, next-open target, physical MNQ position.
//   <Tag>_fills.csv : per-execution ledger — action, price, qty, commission, target.
//
// SAFETY: research/backtest only. Never enable, deploy, or connect to Sim101/live.
namespace NinjaTrader.NinjaScript.Strategies
{
    public class SolarWaveE10Master_v2 : Strategy
    {
        private const int NMEM = 13;

        // ---- shared volatility state (primary closes; verbatim V3 semantics) ----
        private double volSum;
        private double prevClose;
        private int    volCount;

        // ---- per-member V3 state machines ----
        private double[] mVolMult;
        private double[] mAnchor;
        private double[] mSEff;
        private bool[]   mIsUp;
        private bool[]   mWeak;
        private int[]    mBarsSinceExtreme;
        private int[]    mNextWeakBar;
        private int[]    mWave;
        private int[]    mSig;      // signalTradeVal this bar
        private bool     initialized;

        // ---- virtual execution state ----
        private int[] mPos;         // member position effective THROUGH current bar close
        private int[] mPending;     // member position effective at NEXT bar open

        private int targetQty;      // physical MNQ target (effective next open)

        private StreamWriter barLog;
        private StringBuilder fillLog;
        private int execCount;

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = "R5-E10 executable champion: 13 virtual SolarWaveOpenV3 members -> round(10*mean) MNQ net-change execution";
                Name        = "SolarWaveE10Master_v2";

                Calculate               = Calculate.OnBarClose;
                EntriesPerDirection     = 100;
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

                // V3 member constants (frozen R5-E10 spec)
                StopMultiplier = 179;      // sigma-warmup fallback only (ThresholdMode 1)
                SlowdownScan   = 5;
                WeakWeakSplit  = 10;
                VolPeriod      = 460;
                SMinTicks      = 40;
                SMaxTicks      = 1200;
                Flatten1644    = true;

                ExecInstrument = "MNQ 09-26";
                ExportDir      = "";
                Tag            = "e10m_v2";
            }
            else if (State == State.Configure)
            {
                AddDataSeries(ExecInstrument, BarsPeriodType.Minute, 3);
                fillLog = new StringBuilder(1 << 20);
                execCount = 0;
            }
            else if (State == State.DataLoaded)
            {
                initialized = false;
                volSum = 0; volCount = 0; prevClose = double.NaN;

                mVolMult          = new double[NMEM];
                mAnchor           = new double[NMEM];
                mSEff             = new double[NMEM];
                mIsUp             = new bool[NMEM];
                mWeak             = new bool[NMEM];
                mBarsSinceExtreme = new int[NMEM];
                mNextWeakBar      = new int[NMEM];
                mWave             = new int[NMEM];
                mSig              = new int[NMEM];
                mPos              = new int[NMEM];
                mPending          = new int[NMEM];
                for (int m = 0; m < NMEM; m++)
                    mVolMult[m] = 6.0 + 2.0 * m;      // 6, 8, ..., 30
                targetQty = 0;
            }
            else if (State == State.Terminated)
            {
                Flush();
            }
        }

        // ---- verbatim V3: causal mean |close - close[1]| over trailing VolPeriod bars ----
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
                    int n = Math.Min(VolPeriod, CurrentBar);
                    double s = 0;
                    for (int i = 0; i < n; i++)
                        s += Math.Abs(Close[i] - Close[i + 1]);
                    volSum = s; volCount = n;
                }
            }
            prevClose = Close[0];
        }

        private double ResolveS(double volMult)
        {
            double sig = CausalSigma();
            if (double.IsNaN(sig) || sig <= 0)
                return StopMultiplier * TickSize;
            double s = volMult * sig;
            double lo = SMinTicks * TickSize, hi = SMaxTicks * TickSize;
            if (s < lo) s = lo;
            if (s > hi) s = hi;
            return s;
        }

        // ---- verbatim V3 state machine, AnchorMode 0 (candidate extreme = Close[0]) ----
        private void UpdateMachine(int m)
        {
            double px = Close[0];
            mSig[m] = 0;
            int ev = 0;

            if (!initialized)   // first bar: all members seed identically (StartUp=false)
            {
                mIsUp[m] = false; mAnchor[m] = px;
                mSEff[m] = ResolveS(mVolMult[m]);
                mWeak[m] = false; mBarsSinceExtreme[m] = 0;
                mNextWeakBar[m] = int.MinValue; mWave[m] = 1;
            }
            else
            {
                double cand = px;
                if (mIsUp[m])
                {
                    if (cand >= mAnchor[m])
                    {
                        if (cand > mAnchor[m]) ev = 1;
                        mAnchor[m] = cand;
                    }
                    else if (px < mAnchor[m] - mSEff[m])
                    {
                        mIsUp[m] = false; ev = 2;
                        mSEff[m] = ResolveS(mVolMult[m]);   // frozen at trend birth
                        mAnchor[m] = px;
                    }
                }
                else
                {
                    if (cand <= mAnchor[m])
                    {
                        if (cand < mAnchor[m]) ev = 1;
                        mAnchor[m] = cand;
                    }
                    else if (px > mAnchor[m] + mSEff[m])
                    {
                        mIsUp[m] = true; ev = 2;
                        mSEff[m] = ResolveS(mVolMult[m]);
                        mAnchor[m] = px;
                    }
                }
            }

            if (ev == 2)
            {
                mWeak[m] = false; mBarsSinceExtreme[m] = 0; mWave[m] = 1;
                mSig[m] = mIsUp[m] ? 1 : -1;
                mNextWeakBar[m] = CurrentBar + WeakWeakSplit;
            }
            else if (ev == 1)
            {
                mBarsSinceExtreme[m] = 0;
                if (mWeak[m])
                {
                    mWave[m]++; mWeak[m] = false;
                    mSig[m] = mIsUp[m] ? 3 : -3;
                    mNextWeakBar[m] = CurrentBar + WeakWeakSplit;
                }
            }
            else
            {
                mBarsSinceExtreme[m]++;
                if (!mWeak[m] && mBarsSinceExtreme[m] >= SlowdownScan && CurrentBar >= mNextWeakBar[m])
                {
                    mWeak[m] = true; mNextWeakBar[m] = CurrentBar + WeakWeakSplit;
                }
            }
        }

        // ---- verbatim V3 OnBarUpdate order logic mapped to the virtual book ----
        // (ExitMultiplier 0 -> exit level IS the reversal level; EntrySignalType 1)
        private void Decide(int m)
        {
            if (CurrentBar < BarsRequiredToTrade)
            {
                mPending[m] = mPos[m];
                return;
            }

            double xl = mIsUp[m] ? mAnchor[m] - mSEff[m] : mAnchor[m] + mSEff[m];
            if (mPos[m] > 0 && Close[0] <= xl) { mPending[m] = 0; return; }
            if (mPos[m] < 0 && Close[0] >= xl) { mPending[m] = 0; return; }
            if (mPos[m] != 0)                  { mPending[m] = mPos[m]; return; }

            int sig = mSig[m];
            if (sig == 1)       mPending[m] = 1;    // EntrySignalType == 1: flips only
            else if (sig == -1) mPending[m] = -1;
            else                mPending[m] = 0;
        }

        private int PhysicalPosition()
        {
            if (Positions == null || Positions.Length < 2 || Positions[1] == null)
                return 0;
            if (Positions[1].MarketPosition == MarketPosition.Long)  return Positions[1].Quantity;
            if (Positions[1].MarketPosition == MarketPosition.Short) return -Positions[1].Quantity;
            return 0;
        }

        private void SubmitNetChange(int tgt)
        {
            int c = PhysicalPosition();
            if (tgt == c)
                return;
            if (tgt == 0)
            {
                if (c > 0)      ExitLong(1, c, "XL", "");
                else            ExitShort(1, -c, "XS", "");
            }
            else if (tgt > 0)
            {
                if (c < 0)          EnterLong(1, tgt, "L");          // managed auto-reversal
                else if (tgt > c)   EnterLong(1, tgt - c, "L");
                else                ExitLong(1, c - tgt, "XL", "");
            }
            else
            {
                if (c > 0)          EnterShort(1, -tgt, "S");        // managed auto-reversal
                else if (tgt < c)   EnterShort(1, c - tgt, "S");
                else                ExitShort(1, tgt - c, "XS", "");
            }
        }

        protected override void OnBarUpdate()
        {
            if (BarsInProgress != 0)
                return;

            // 1. pending virtual orders fill at THIS bar's open
            for (int m = 0; m < NMEM; m++)
                mPos[m] = mPending[m];

            // 2. shared sigma + member state machines on this bar's close
            UpdateVol();
            for (int m = 0; m < NMEM; m++)
                UpdateMachine(m);
            if (!initialized)
                initialized = true;

            // 3. member decisions -> positions effective next open
            for (int m = 0; m < NMEM; m++)
                Decide(m);

            // 4. session close: engine exits AT the close; pending orders are cancelled
            bool sessEnd = Bars.IsLastBarOfSession;
            if (sessEnd)
            {
                for (int m = 0; m < NMEM; m++) { mPos[m] = 0; mPending[m] = 0; }
            }

            // 5. physical target from next-open member book: round(10 * mean), clamp +/-10
            int sumNext = 0, sumClose = 0;
            for (int m = 0; m < NMEM; m++) { sumNext += mPending[m]; sumClose += mPos[m]; }
            int tgtNext  = (int)Math.Round((sumNext  / 13.0) * 10.0);
            int tgtClose = (int)Math.Round((sumClose / 13.0) * 10.0);
            if (tgtNext  >  10) tgtNext  =  10;
            if (tgtNext  < -10) tgtNext  = -10;
            if (tgtClose >  10) tgtClose =  10;
            if (tgtClose < -10) tgtClose = -10;
            targetQty = tgtNext;

            // 6. per-bar ledger row
            if (barLog == null && !string.IsNullOrEmpty(ExportDir))
                OpenBarLog();
            if (barLog != null)
            {
                StringBuilder sb = new StringBuilder(128);
                sb.Append(Time[0].ToString("yyyy-MM-ddTHH:mm:ss", CultureInfo.InvariantCulture));
                sb.Append(',').Append(CurrentBar).Append(',').Append(sessEnd ? 1 : 0);
                for (int m = 0; m < NMEM; m++)
                    sb.Append(',').Append(mPos[m]);
                sb.Append(',').Append(sumClose)
                  .Append(',').Append(tgtClose)
                  .Append(',').Append(tgtNext)
                  .Append(',').Append(PhysicalPosition());
                barLog.WriteLine(sb.ToString());
            }

            // 7. physical net-change submission (never on the session's last bar:
            //    the engine session-close exit owns the close, and pending orders
            //    would be cancelled anyway — proven member behaviour)
            if (sessEnd)
                return;
            if (CurrentBar < BarsRequiredToTrade)
                return;
            if (CurrentBars.Length < 2 || CurrentBars[1] < BarsRequiredToTrade)
                return;
            // Flatten1644: physical book targets 0 from the 16:42-stamped bar close
            // (market exit fills at next bar open ~16:42:0x ET), so the position never
            // crosses the 16:45 ET initial-margin cutoff. Virtual members untouched.
            bool late = Flatten1644
                && Time[0].TimeOfDay >= new TimeSpan(16, 42, 0)
                && Time[0].TimeOfDay <= new TimeSpan(17, 0, 0);
            SubmitNetChange(late ? 0 : targetQty);
        }

        protected override void OnExecutionUpdate(Execution execution, string executionId,
            double price, int quantity, MarketPosition marketPosition, string orderId,
            DateTime time)
        {
            if (fillLog == null || execution == null || execution.Order == null)
                return;
            fillLog.AppendLine(string.Format(CultureInfo.InvariantCulture,
                "{0},{1:yyyy-MM-ddTHH:mm:ss},{2},{3},{4},{5},{6},{7},{8},{9},{10}",
                execCount++, time, CurrentBar, execution.Name,
                execution.Instrument != null ? execution.Instrument.FullName : "?",
                execution.Order.OrderAction, marketPosition, price, quantity,
                execution.Commission, targetQty));
        }

        private void OpenBarLog()
        {
            try
            {
                if (!Directory.Exists(ExportDir))
                    Directory.CreateDirectory(ExportDir);
                barLog = new StreamWriter(Path.Combine(ExportDir, Tag + "_bars.csv"), false);
                StringBuilder h = new StringBuilder();
                h.Append("time,bar,sess_end");
                for (int m = 0; m < NMEM; m++)
                    h.Append(",p").Append((int)mVolMult[m]);
                h.Append(",sum,tgt_close,tgt_next,phys");
                barLog.WriteLine(string.Format(CultureInfo.InvariantCulture,
                    "# SolarWaveE10Master_v2 SM={0} SS={1} WWS={2} VP={3} smin={4} smax={5} exec={6} instrument={7} period={8}",
                    StopMultiplier, SlowdownScan, WeakWeakSplit, VolPeriod, SMinTicks, SMaxTicks,
                    ExecInstrument, Instrument != null ? Instrument.FullName : "?",
                    BarsPeriod != null ? BarsPeriod.Value : 0));
                barLog.WriteLine(h.ToString());
            }
            catch (Exception ex)
            {
                Print("SolarWaveE10Master_v2 bar log open failed: " + ex.Message);
                barLog = null;
                ExportDir = "";   // do not retry every bar
            }
        }

        private void Flush()
        {
            try
            {
                if (barLog != null)
                {
                    barLog.Flush(); barLog.Dispose(); barLog = null;
                }
                if (!string.IsNullOrEmpty(ExportDir) && fillLog != null)
                {
                    if (!Directory.Exists(ExportDir))
                        Directory.CreateDirectory(ExportDir);
                    using (StreamWriter w = new StreamWriter(Path.Combine(ExportDir, Tag + "_fills.csv"), false))
                    {
                        w.WriteLine(string.Format(CultureInfo.InvariantCulture,
                            "# SolarWaveE10Master_v2 execs={0} exec_instrument={1}", execCount, ExecInstrument));
                        w.WriteLine("n,time,bar,name,instrument,order_action,market_position,price,qty,commission,target");
                        w.Write(fillLog.ToString());
                        w.Flush();
                    }
                }
            }
            catch (Exception ex)
            {
                Print("SolarWaveE10Master_v2 export failed: " + ex.Message);
            }
        }

        #region Properties
        [NinjaScriptProperty] [Range(1, 4000)]
        [Display(Name = "Stop Multiplier (warmup fallback)", Order = 1, GroupName = "Members")]
        public double StopMultiplier { get; set; }

        [NinjaScriptProperty] [Range(1, 100)]
        [Display(Name = "Slowdown Scan", Order = 2, GroupName = "Members")]
        public int SlowdownScan { get; set; }

        [NinjaScriptProperty] [Range(1, 100)]
        [Display(Name = "Weak-Weak Split", Order = 3, GroupName = "Members")]
        public int WeakWeakSplit { get; set; }

        [NinjaScriptProperty] [Range(30, 20000)]
        [Display(Name = "Vol Period", Order = 4, GroupName = "Members")]
        public int VolPeriod { get; set; }

        [NinjaScriptProperty] [Range(1, 4000)]
        [Display(Name = "S Min Ticks", Order = 5, GroupName = "Members")]
        public int SMinTicks { get; set; }

        [NinjaScriptProperty] [Range(1, 8000)]
        [Display(Name = "S Max Ticks", Order = 6, GroupName = "Members")]
        public int SMaxTicks { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Flatten 16:44 ET", Order = 0, GroupName = "Execution")]
        public bool Flatten1644 { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Exec Instrument", Order = 1, GroupName = "Execution")]
        public string ExecInstrument { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Export Dir", Order = 1, GroupName = "Export")]
        public string ExportDir { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Tag", Order = 2, GroupName = "Export")]
        public string Tag { get; set; }
        #endregion
    }
}
