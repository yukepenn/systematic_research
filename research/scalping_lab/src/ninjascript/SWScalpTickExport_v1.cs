#region Using declarations
using System;
using System.IO;
using System.Text;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
#endregion

// Scalping-lab session exporter: Last/Bid/Ask 1-tick events to <Tag>_ticks.csv.
// Places NO orders. Fail-closed in realtime. One backtest run = one session.
namespace NinjaTrader.NinjaScript.Strategies
{
    public class SWScalpTickExport_v1 : Strategy
    {
        private StreamWriter w;
        private long lines;
        private const long MaxLines = 12000000;

        [NinjaScriptProperty]
        public string ExportDir { get; set; }
        [NinjaScriptProperty]
        public string Tag { get; set; }

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Name = "SWScalpTickExport_v1";
                Calculate = Calculate.OnEachTick;
                IsExitOnSessionCloseStrategy = false;
                ExportDir = @"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\research\scalping_lab\runs\EXPORT01\out";
                Tag = "session";
            }
            else if (State == State.Configure)
            {
                AddDataSeries(null, new BarsPeriod { BarsPeriodType = BarsPeriodType.Tick, Value = 1, MarketDataType = MarketDataType.Bid });
                AddDataSeries(null, new BarsPeriod { BarsPeriodType = BarsPeriodType.Tick, Value = 1, MarketDataType = MarketDataType.Ask });
            }
            else if (State == State.DataLoaded)
            {
                Directory.CreateDirectory(ExportDir);
                w = new StreamWriter(Path.Combine(ExportDir, Tag + "_ticks.csv"), false, Encoding.ASCII, 1 << 22);
                w.WriteLine("bip,time,price,volume");
            }
            else if (State == State.Terminated)
            {
                if (w != null) { w.Flush(); w.Close(); w = null; }
            }
        }

        protected override void OnBarUpdate()
        {
            if (State == State.Realtime) return; // historical research only
            if (w == null || lines >= MaxLines) return;
            w.WriteLine(BarsInProgress.ToString() + ","
                + Times[BarsInProgress][0].ToString("yyyy-MM-dd HH:mm:ss.fffffff") + ","
                + Closes[BarsInProgress][0].ToString("F2") + ","
                + Volumes[BarsInProgress][0].ToString("F0"));
            lines++;
        }
    }
}
