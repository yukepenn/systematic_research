#region Using declarations
using System;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using System.Globalization;
using System.IO;
using System.Reflection;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
#endregion

namespace NinjaTrader.NinjaScript.Strategies
{
    // RE02 Type-2 recovery OHLC ledger exporter; trades nothing.
    // The vendor indicator is bound through its PUBLIC generated wrapper via
    // reflection so this file has no compile-time vendor-assembly reference
    // (sandbox-compilable). Behaviour is identical to the direct-typed call:
    // the same public wrapper method and the same public Series indexers run.
    public class SolarWaveRKLedgerV2 : Strategy
    {
        private object sw;                    // vendor indicator instance
        private object sTrade, sTrend, sWave, sStop, sVector;
        private PropertyInfo itemProp;        // Series<double> this[int barsAgo]
        private StreamWriter writer;

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = "RE02 Type-2 recovery OHLC ledger exporter; trades nothing";
                Name = "SolarWaveRKLedgerV2";
                Calculate = Calculate.OnBarClose;
                IsExitOnSessionCloseStrategy = false;
                BarsRequiredToTrade = 0;
                MaximumBarsLookBack = MaximumBarsLookBack.TwoHundredFiftySix;

                TrendMultiplier = 90;
                StopMultiplier  = 179;
                SlowdownScan    = 5;
                WeakWeakSplit   = 10;
                PullbackEarly   = true;
                PullbackSplit   = 10;
                ExportPath = @"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\research\03_reverse_engineering\ledgers\t2_export.csv";
            }
            else if (State == State.DataLoaded)
            {
                MethodInfo wrapper = null;
                foreach (MethodInfo m in GetType().GetMethods(BindingFlags.Public | BindingFlags.Instance))
                {
                    if (m.Name == "RenkoKings_SolarWaveRK" && m.GetParameters().Length == 7)
                    {
                        wrapper = m;
                        break;
                    }
                }
                if (wrapper == null)
                    throw new InvalidOperationException(
                        "RenkoKings_SolarWaveRK 7-arg wrapper not found on Strategy");

                sw = wrapper.Invoke(this, new object[] {
                    Close, TrendMultiplier, StopMultiplier,
                    SlowdownScan, WeakWeakSplit, PullbackEarly, PullbackSplit });

                Type it = sw.GetType();
                sTrade  = it.GetProperty("Signal_Trade").GetValue(sw, null);
                sTrend  = it.GetProperty("Signal_Trend").GetValue(sw, null);
                sWave   = it.GetProperty("Signal_Wave").GetValue(sw, null);
                sStop   = it.GetProperty("TrailingStop").GetValue(sw, null);
                sVector = it.GetProperty("TrendVector").GetValue(sw, null);
                itemProp = sTrade.GetType().GetProperty("Item", new Type[] { typeof(int) });
                if (itemProp == null)
                    throw new InvalidOperationException("Series<double> indexer not found");
            }
            else if (State == State.Terminated)
            {
                if (writer != null)
                {
                    writer.Flush();
                    writer.Close();
                    writer = null;
                }
            }
        }

        private double Val(object series)
        {
            return (double)itemProp.GetValue(series, new object[] { 0 });
        }

        protected override void OnBarUpdate()
        {
            if (BarsInProgress != 0)
                return;

            if (writer == null)
            {
                string dir = Path.GetDirectoryName(ExportPath);
                if (!Directory.Exists(dir))
                    Directory.CreateDirectory(dir);
                writer = new StreamWriter(ExportPath, false);
                writer.WriteLine(string.Format(CultureInfo.InvariantCulture,
                    "# params TM={0} SM={1} SS={2} WWS={3} PE={4} PS={5} tick={6} instrument={7} barsPeriod={8}",
                    TrendMultiplier, StopMultiplier, SlowdownScan, WeakWeakSplit,
                    PullbackEarly, PullbackSplit, TickSize, Instrument.FullName,
                    BarsPeriod.ToString()));
                writer.WriteLine("time,bar,open,high,low,close,volume,first_bar_of_session,signal_trade,signal_trend,signal_wave,trailing_stop,trend_vector");
            }

            writer.WriteLine(string.Format(CultureInfo.InvariantCulture,
                "{0:yyyy-MM-ddTHH:mm:ss},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12}",
                Time[0], CurrentBar, Open[0], High[0], Low[0], Close[0], Volume[0],
                Bars.IsFirstBarOfSession ? 1 : 0,
                Val(sTrade), Val(sTrend), Val(sWave), Val(sStop), Val(sVector)));
        }

        #region Properties
        [NinjaScriptProperty]
        [Range(1, 1000)]
        [Display(Name = "Trend Multiplier", Order = 1, GroupName = "Solar Wave")]
        public double TrendMultiplier { get; set; }

        [NinjaScriptProperty]
        [Range(1, 2000)]
        [Display(Name = "Stop Multiplier", Order = 2, GroupName = "Solar Wave")]
        public double StopMultiplier { get; set; }

        [NinjaScriptProperty]
        [Range(1, 100)]
        [Display(Name = "Slowdown Scan", Order = 3, GroupName = "Solar Wave")]
        public int SlowdownScan { get; set; }

        [NinjaScriptProperty]
        [Range(1, 100)]
        [Display(Name = "Weak-Weak Split", Order = 4, GroupName = "Solar Wave")]
        public int WeakWeakSplit { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Pullback Early", Order = 5, GroupName = "Solar Wave")]
        public bool PullbackEarly { get; set; }

        [NinjaScriptProperty]
        [Range(1, 100)]
        [Display(Name = "Pullback Split", Order = 6, GroupName = "Solar Wave")]
        public int PullbackSplit { get; set; }

        [NinjaScriptProperty]
        [Display(Name = "Export Path", Order = 7, GroupName = "Export")]
        public string ExportPath { get; set; }
        #endregion
    }
}
