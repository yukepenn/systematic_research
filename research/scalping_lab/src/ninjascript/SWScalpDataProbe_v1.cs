#region Using declarations
using System;
using System.IO;
using System.Text;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
#endregion

// DATAPROBE01 — scalping_lab capability probe. Places NO orders. Fail-closed in realtime.
// Primary series: run on 1-Tick Last. Adds 1-Tick Bid and 1-Tick Ask series to test
// whether NT historical servers provide them. Exports every event with full timestamp
// precision so resolution (s vs ms) is directly observable.
namespace NinjaTrader.NinjaScript.Strategies
{
    public class SWScalpDataProbe_v1 : Strategy
    {
        private StreamWriter w;
        private long lines;
        private const long MaxLines = 3000000;

        [NinjaScriptProperty]
        public string ExportDir { get; set; }

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Name = "SWScalpDataProbe_v1";
                Calculate = Calculate.OnEachTick;
                IsUnmanaged = false;
                IsExitOnSessionCloseStrategy = false;
                ExportDir = @"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\research\scalping_lab\runs\DATAPROBE01\out";
            }
            else if (State == State.Configure)
            {
                AddDataSeries(null, new BarsPeriod { BarsPeriodType = BarsPeriodType.Tick, Value = 1, MarketDataType = MarketDataType.Bid });
                AddDataSeries(null, new BarsPeriod { BarsPeriodType = BarsPeriodType.Tick, Value = 1, MarketDataType = MarketDataType.Ask });
            }
            else if (State == State.DataLoaded)
            {
                Directory.CreateDirectory(ExportDir);
                w = new StreamWriter(Path.Combine(ExportDir, "probe_ticks.csv"), false, Encoding.ASCII, 1 << 20);
                w.WriteLine("bip,bar,time,price,volume");
            }
            else if (State == State.Terminated)
            {
                if (w != null) { w.Flush(); w.Close(); w = null; }
            }
        }

        protected override void OnBarUpdate()
        {
            if (State == State.Realtime) return; // fail closed: historical research only
            if (w == null || lines >= MaxLines) return;
            w.WriteLine(BarsInProgress.ToString() + "," + CurrentBars[BarsInProgress].ToString() + ","
                + Times[BarsInProgress][0].ToString("yyyy-MM-dd HH:mm:ss.fffffff") + ","
                + Closes[BarsInProgress][0].ToString("F2") + ","
                + Volumes[BarsInProgress][0].ToString("F0"));
            lines++;
        }
    }
}
