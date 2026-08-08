// SWScalpTickExport_v2 — same as v1 but 20M row cap (re-export monster sessions like
// s20251117 that truncated at 12M). Historical only; fails closed in realtime; no orders.
// Output: Documents\NinjaTrader 8\out\<Tag>_ticks.csv  (bip,time,price,volume; header row)
#region Using declarations
using System;
using System.IO;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
#endregion

namespace NinjaTrader.NinjaScript.Strategies
{
    public class SWScalpTickExport_v2 : Strategy
    {
        private StreamWriter w;
        private long rows;
        private const long MaxRows = 20000000;

        [NinjaScriptProperty]
        public string Tag { get; set; }

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Name = "SWScalpTickExport_v2";
                Calculate = Calculate.OnBarClose;
                Tag = "tickexp2";
            }
            else if (State == State.Configure)
            {
                AddDataSeries(new BarsPeriod { BarsPeriodType = BarsPeriodType.Tick, Value = 1, MarketDataType = MarketDataType.Bid });
                AddDataSeries(new BarsPeriod { BarsPeriodType = BarsPeriodType.Tick, Value = 1, MarketDataType = MarketDataType.Ask });
            }
            else if (State == State.DataLoaded)
            {
                string dir = Path.Combine(Core.Globals.UserDataDir, "out");
                Directory.CreateDirectory(dir);
                w = new StreamWriter(Path.Combine(dir, Tag + "_ticks.csv"), false);
                w.WriteLine("bip,time,price,volume");
                rows = 0;
            }
            else if (State == State.Terminated)
            {
                if (w != null) { w.Flush(); w.Close(); w = null; }
            }
        }

        protected override void OnBarUpdate()
        {
            if (State == State.Realtime) return;   // fail closed
            if (w == null || rows >= MaxRows) return;
            w.WriteLine(BarsInProgress + ","
                + Times[BarsInProgress][0].ToString("yyyy-MM-dd HH:mm:ss.fffffff") + ","
                + Closes[BarsInProgress][0].ToString("F2") + ","
                + Volumes[BarsInProgress][0].ToString("F0"));
            rows++;
        }
    }
}