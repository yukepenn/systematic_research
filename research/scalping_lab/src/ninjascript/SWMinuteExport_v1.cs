// SWMinuteExport_v1 — research data exporter: 1-min OHLCV of the PRIMARY series to CSV.
// Historical Strategy Analyzer only; fails closed in realtime; no orders ever.
// Unlocks: GC/CL/RTY/ZN cross-asset r-screen, B1 overnight 2005+, H-D3@1min,
// B-FADE pre-2022 confirmation. Output: Documents\NinjaTrader 8\out\<Tag>_1m.csv
#region Using declarations
using System;
using System.IO;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
#endregion

namespace NinjaTrader.NinjaScript.Strategies
{
    public class SWMinuteExport_v1 : Strategy
    {
        private StreamWriter w;
        private long rows;
        private const long MaxRows = 12000000;

        [NinjaScriptProperty]
        public string Tag { get; set; }

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Name = "SWMinuteExport_v1";
                Calculate = Calculate.OnBarClose;
                IsUnmanaged = false;
                Tag = "minexp";
            }
            else if (State == State.DataLoaded)
            {
                string dir = Path.Combine(Core.Globals.UserDataDir, "out");
                Directory.CreateDirectory(dir);
                w = new StreamWriter(Path.Combine(dir, Tag + "_1m.csv"), false);
                w.WriteLine("time,open,high,low,close,volume");
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
            w.WriteLine(Time[0].ToString("yyyy-MM-dd HH:mm:ss") + ","
                + Open[0].ToString("F2") + "," + High[0].ToString("F2") + ","
                + Low[0].ToString("F2") + "," + Close[0].ToString("F2") + ","
                + Volume[0].ToString("F0"));
            rows++;
        }
    }
}