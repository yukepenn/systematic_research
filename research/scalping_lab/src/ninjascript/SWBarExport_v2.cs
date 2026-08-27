#region Using declarations
using System;
using System.IO;
using System.Text;
using System.Collections.Generic;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
#endregion

// SWBarExport_v2 = v1 plus FAULT TOLERANCE. Places NO ORDERS. Historical only.
//
// v1 had a defect that only shows up in an inventory: AddDataSeries on an instrument that does not
// exist throws inside Configure, so the strategy never reaches DataLoaded, no CSV is ever opened,
// and the ENTIRE RUN yields nothing - while the job still reports "completed". Two inventory runs
// were lost that way (RTY 09-16 predates CME's Russell listing; old grain contracts likewise).
//
// For an inventory whose whole purpose is discovering which symbols resolve, that is backwards:
// an unresolvable symbol is a RESULT, not a fatal error. v2 wraps each AddDataSeries in try/catch
// and writes the outcome per symbol to <Tag>_symbols.csv, so a run reports what it could and could
// not load instead of dying.
//
// Output: <ExportDir>\<Tag>_bars.csv      symbol,time,open,high,low,close,volume
//         <ExportDir>\<Tag>_symbols.csv   symbol,status,detail
namespace NinjaTrader.NinjaScript.Strategies
{
    public class SWBarExport_v2 : Strategy
    {
        private StreamWriter w;
        private long lines;
        private const long MaxLines = 50000000;
        private List<string> okSyms = new List<string>();
        private List<string> badSyms = new List<string>();

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
                Name = "SWBarExport_v2";
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
                        try
                        {
                            AddDataSeries(s, BarsPeriod);
                            okSyms.Add(s);
                        }
                        catch (Exception ex)
                        {
                            badSyms.Add(s + "|" + ex.GetType().Name);
                        }
                    }
                }
            }
            else if (State == State.DataLoaded)
            {
                Directory.CreateDirectory(ExportDir);
                w = new StreamWriter(Path.Combine(ExportDir, Tag + "_bars.csv"), false, Encoding.ASCII, 1 << 22);
                w.WriteLine("symbol,time,open,high,low,close,volume");

                using (StreamWriter m = new StreamWriter(Path.Combine(ExportDir, Tag + "_symbols.csv"), false, Encoding.ASCII))
                {
                    m.WriteLine("symbol,status,detail");
                    for (int i = 0; i < okSyms.Count; i++) m.WriteLine(okSyms[i] + ",ADDED,");
                    for (int i = 0; i < badSyms.Count; i++)
                    {
                        string[] p = badSyms[i].Split('|');
                        m.WriteLine(p[0] + ",FAILED," + (p.Length > 1 ? p[1] : ""));
                    }
                }
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