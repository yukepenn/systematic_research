#region Using declarations
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
#endregion

// OriginalTraderVolumeVWAP_Proxy_v1 — NinjaScript port of the Track-V PROXY candidate
// (research/original_trader_reconstruction/volume_vwap_family/TRACK_V_REPORT.md).
//
// *** PROXY, NOT THE EXACT ALGORITHM ***
// The trader's strategy uses Volume Base = BidAskPrice_RealVolume, which is not
// reconstructible from minute data. This port implements the best BEHAVIORALLY MATCHED
// interpretation (classification: PARTIAL / MECHANISM UNIDENTIFIED):
//   - volume-at-price histogram of each completed 60-min anchor hour (close-binned),
//     percentile ladder P5/P25/P50/P75/P95 held STATIC through the following hour
//   - trend = Close vs EMA(20) of 1-minute closes
//   - entry: close crossing above P75 in uptrend (below P25 in downtrend), only if not
//     extended beyond the line by more than 10% of ladder depth (P95-P5)
//   - max 3 signals per trend episode, >=5 bars between signals
//   - exit: close crossing the ladder median (P50) against the position; session close
// RESEARCH ONLY: historical Strategy Analyzer use; fails closed in realtime.
namespace NinjaTrader.NinjaScript.Strategies
{
    public class OriginalTraderVolumeVWAP_Proxy_v1 : Strategy
    {
        private Dictionary<double, double> hist;
        private int      barsInAnchor;
        private DateTime curHour;
        private double[] levels;        // applied to the CURRENT bar (from prev completed hour)
        private double[] prevBarLevels; // levels that applied to the PREVIOUS bar
        private double   prevClose;
        private bool     havePrevBar;

        private NinjaTrader.NinjaScript.Indicators.EMA ema20;

        private int  sigCount;
        private int  lastSigBar;
        private int  trendNow;          // +1 up, -1 down, 0 unset

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = "Track-V PROXY candidate (research only; NOT the exact vendor algorithm)";
                Name        = "OriginalTraderVolumeVWAP_Proxy_v1";

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

                TrendPeriod          = 20;
                MaxSignalsPerTrend   = 3;
                SignalSplitBars      = 5;
                CloseThresholdPct    = 10;
            }
            else if (State == State.DataLoaded)
            {
                hist         = new Dictionary<double, double>();
                barsInAnchor = 0;
                curHour      = DateTime.MinValue;
                levels       = null;
                prevBarLevels = null;
                havePrevBar  = false;
                sigCount     = 0;
                lastSigBar   = int.MinValue;
                trendNow     = 0;
                ema20        = EMA(Close, TrendPeriod);
            }
            else if (State == State.Realtime)
            {
                Log("OriginalTraderVolumeVWAP_Proxy_v1 is research-only; disabling.", LogLevel.Error);
                SetState(State.Terminated);
            }
        }

        private double[] PercentilesOf(Dictionary<double, double> h)
        {
            var prices = h.Keys.OrderBy(p => p).ToArray();
            double tot = h.Values.Sum();
            double[] pcts = { 0.05, 0.25, 0.50, 0.75, 0.95 };
            double[] outv = new double[5];
            int k = 0; double cum = 0;
            foreach (var p in prices)
            {
                cum += h[p];
                while (k < 5 && cum / tot >= pcts[k])
                {
                    outv[k] = p; k++;
                }
                if (k >= 5) break;
            }
            for (; k < 5; k++) outv[k] = prices[prices.Length - 1];
            return outv;
        }

        protected override void OnBarUpdate()
        {
            if (BarsInProgress != 0)
                return;

            // ---- anchored histogram bookkeeping (runs on every bar) ----
            DateTime h = new DateTime(Time[0].Year, Time[0].Month, Time[0].Day, Time[0].Hour, 0, 0);
            prevBarLevels = levels;
            if (h != curHour)
            {
                if (barsInAnchor >= 5)
                    levels = PercentilesOf(hist);   // completed hour becomes the static ladder
                curHour = h;
                hist = new Dictionary<double, double>();
                barsInAnchor = 0;
            }
            double bin = Instrument.MasterInstrument.RoundToTickSize(Close[0]);
            double v;
            hist[bin] = (hist.TryGetValue(bin, out v) ? v : 0.0) + Volume[0];
            barsInAnchor++;

            // ---- trend episode tracking ----
            int t = Close[0] > ema20[0] ? 1 : -1;
            if (trendNow == 0 || t != trendNow)
            {
                trendNow = t;
                sigCount = 0;
            }

            if (CurrentBar < BarsRequiredToTrade)
            {
                prevClose = Close[0]; havePrevBar = true;
                return;
            }
            if (levels == null || prevBarLevels == null || !havePrevBar)
            {
                prevClose = Close[0]; havePrevBar = true;
                return;
            }

            double P5 = levels[0], P25 = levels[1], P50 = levels[2], P75 = levels[3], P95 = levels[4];
            double pP25 = prevBarLevels[1], pP75 = prevBarLevels[3];

            // ---- exits first ----
            if (Position.MarketPosition == MarketPosition.Long && Close[0] < P50)
            {
                ExitLong("L-MedExit", "Long");
                prevClose = Close[0];
                return;
            }
            if (Position.MarketPosition == MarketPosition.Short && Close[0] > P50)
            {
                ExitShort("S-MedExit", "Short");
                prevClose = Close[0];
                return;
            }

            // ---- entries ----
            if (Position.MarketPosition == MarketPosition.Flat
                && sigCount < MaxSignalsPerTrend
                && (CurrentBar - lastSigBar) >= SignalSplitBars)
            {
                double depth = P95 - P5;
                double thr   = (CloseThresholdPct / 100.0) * depth;
                int sig = 0;
                if (trendNow > 0 && prevClose <= pP75 && Close[0] > P75 && (Close[0] - P75) <= thr)
                    sig = 1;
                else if (trendNow < 0 && prevClose >= pP25 && Close[0] < P25 && (P25 - Close[0]) <= thr)
                    sig = -1;

                if (sig > 0)
                {
                    EnterLong(DefaultQuantity, "Long");
                    sigCount++; lastSigBar = CurrentBar;
                }
                else if (sig < 0)
                {
                    EnterShort(DefaultQuantity, "Short");
                    sigCount++; lastSigBar = CurrentBar;
                }
            }

            prevClose = Close[0];
            havePrevBar = true;
        }

        #region Properties
        [NinjaScriptProperty]
        [Range(2, 200)]
        [Display(Name = "Trend Period (EMA)", Order = 1, GroupName = "Proxy")]
        public int TrendPeriod { get; set; }

        [NinjaScriptProperty]
        [Range(1, 20)]
        [Display(Name = "Signal Quantity Per Trend", Order = 2, GroupName = "Proxy")]
        public int MaxSignalsPerTrend { get; set; }

        [NinjaScriptProperty]
        [Range(1, 100)]
        [Display(Name = "Signal Split (Bars)", Order = 3, GroupName = "Proxy")]
        public int SignalSplitBars { get; set; }

        [NinjaScriptProperty]
        [Range(0, 100)]
        [Display(Name = "Signal Close Threshold (%)", Order = 4, GroupName = "Proxy")]
        public double CloseThresholdPct { get; set; }
        #endregion
    }
}
