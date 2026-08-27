#region Using declarations
using System;
using System.IO;
using System.Text;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
#endregion

// SWBarExport_v1 - generic multi-instrument bar exporter. Places NO ORDERS. Historical only,
// fails closed in realtime.
//
// Why this exists: GetBars returns data into the CALLER's context, so it can only ever be a probe.
// Bulk history has to reach disk, and the only route to disk is NinjaScript inside the backtest
// engine. One run exports the primary series plus every instrument named in Symbols, at the
// primary's BarsPeriod, so a single call can cover a whole multi-market universe.
//
// Output: <ExportDir>\<Tag>_bars.csv   columns: symbol,time,open,high,low,close,volume
namespace NinjaTrader.NinjaScript.Strategies
{
    public class SWBarExport_v1 : Strategy
    {
        private StreamWriter w;
        private long lines;
        private const long MaxLines = 50000000;

        [NinjaScriptProperty]
        public string ExportDir { get; set; }
        [NinjaScriptProperty]
        public string Tag { get; set; }
        [NinjaScriptProperty]
        public string Symbols { get; set; }

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Name = "SWBarExport_v1";
                Calculate = Calculate.OnBarClose;
                IsExitOnSessionCloseStrategy = false;
                ExportDir = @"D:\export";
                Tag = "bars";
                Symbols = "";
            }
            else if (State == State.Configure)
            {
                if (Symbols != null && Symbols.Trim().Length > 0)
                {
                    string[] syms = Symbols.Split(',');
                    for (int i = 0; i < syms.Length; i++)
                    {
                        string s = syms[i].Trim();
                        if (s.Length == 0) continue;
                        AddDataSeries(s, BarsPeriod);
                    }
                }
            }
            else if (State == State.DataLoaded)
            {
                Directory.CreateDirectory(ExportDir);
                w = new StreamWriter(Path.Combine(ExportDir, Tag + "_bars.csv"), false, Encoding.ASCII, 1 << 22);
                w.WriteLine("symbol,time,open,high,low,close,volume");
            }
            else if (State == State.Terminated)
            {
                if (w != null) { w.Flush(); w.Close(); w = null; }
            }
        }

        protected override void OnBarUpdate()
        {
            if (State == State.Realtime) return;
            if (w == null || lines >= MaxLines) return;
            int b = BarsInProgress;
            if (b < 0 || CurrentBars[b] < 0) return;
            w.WriteLine(BarsArray[b].Instrument.FullName + ","
                + Times[b][0].ToString("yyyy-MM-dd HH:mm:ss") + ","
                + Opens[b][0].ToString("R") + ","
                + Highs[b][0].ToString("R") + ","
                + Lows[b][0].ToString("R") + ","
                + Closes[b][0].ToString("R") + ","
                + Volumes[b][0].ToString("F0"));
            lines++;
        }
    }
}