#region Using declarations
using System;
using System.IO;
using System.Text;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
#endregion

// v3 = v1 verbatim with 20M row cap (v2 had a single-arg AddDataSeries overload bug:
// secondary series binding failed silently in the engine harness). Historical only;
// fails closed in realtime; no orders. Compile at next F5/restart.
namespace NinjaTrader.NinjaScript.Strategies
{
    public class SWScalpTickExport_v3 : Strategy
    {
        private StreamWriter w;
        private long lines;
        private const long MaxLines = 20000000;

        [NinjaScriptProperty]
        public string ExportDir { get; set; }
        [NinjaScriptProperty]
        public string Tag { get; set; }

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Name = "SWScalpTickExport_v3";
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