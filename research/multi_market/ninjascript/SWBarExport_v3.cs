#region Using declarations
using System;
using System.IO;
using System.Text;
using System.Collections.Generic;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
#endregion

// SWBarExport_v3 = v2 plus CONTRACT IDENTITY and a PER-SERIES MANIFEST. Places NO ORDERS.
// Historical export only.
//
// WHY v3 EXISTS. v2 wrote BarsArray[b].Instrument.FullName as the row key. That is NT8's DISPLAY
// symbol, and it is DECADE-AMBIGUOUS: "ES 12-06" and "ES 12-16" both render as ESZ6. Keying a
// multi-year contract substrate on that field would silently merge two different contracts a
// decade apart. Directive s5: retain the FULL REQUESTED CONTRACT ID alongside every row, and never
// use the display symbol as the unique key.
//
// v3 therefore emits BOTH: the exact string this run ASKED for, and what NT8 RESOLVED it to.
// They are different columns and only the first is a key.
//
// v3 also emits the per-series manifest directive s4 requires, so that "a completed job with
// missing output is FAIL, not success" is checkable from the artifacts rather than assumed:
//   requested, resolved, status, first date, last date, rows, checksum, error
//
// Output: <ExportDir>\<Tag>_bars.csv      requested,resolved,time,open,high,low,close,volume
//         <ExportDir>\<Tag>_manifest.csv  requested,resolved,status,first,last,rows,checksum,error
namespace NinjaTrader.NinjaScript.Strategies
{
    public class SWBarExport_v3 : Strategy
    {
        private StreamWriter w;
        private long lines;
        private const long MaxLines = 50000000;
        private List<string> okSyms = new List<string>();       // index b-1 -> requested id
        private List<string> badSyms = new List<string>();
        private Dictionary<int, long> rows = new Dictionary<int, long>();
        private Dictionary<int, string> firstDt = new Dictionary<int, string>();
        private Dictionary<int, string> lastDt = new Dictionary<int, string>();
        private Dictionary<int, double> chk = new Dictionary<int, double>();

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
                Name = "SWBarExport_v3";
                Calculate = Calculate.OnBarClose;
                IsExitOnSessionCloseStrategy = false;
                ExportDir = @"D:\mm_export";
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
                            okSyms.Add(s);          // ADDED order == BarsInProgress order (1-based)
                        }
                        catch (Exception ex)
                        {
                            badSyms.Add(s + "|" + ex.GetType().Name + ": " + ex.Message.Replace(",", ";").Replace("\n", " "));
                        }
                    }
                }
            }
            else if (State == State.DataLoaded)
            {
                Directory.CreateDirectory(ExportDir);
                w = new StreamWriter(Path.Combine(ExportDir, Tag + "_bars.csv"), false, Encoding.ASCII, 1 << 22);
                w.WriteLine("requested,resolved,time,open,high,low,close,volume");
            }
            else if (State == State.Terminated)
            {
                if (w != null) { w.Flush(); w.Close(); w = null; }
                try
                {
                    using (StreamWriter m = new StreamWriter(Path.Combine(ExportDir, Tag + "_manifest.csv"), false, Encoding.ASCII))
                    {
                        m.WriteLine("requested,resolved,status,first,last,rows,checksum,error");
                        for (int i = 0; i < okSyms.Count; i++)
                        {
                            int b = i + 1;                      // series index for okSyms[i]
                            long n = rows.ContainsKey(b) ? rows[b] : 0;
                            string res = "";
                            try { if (BarsArray != null && b < BarsArray.Length && BarsArray[b] != null) res = BarsArray[b].Instrument.FullName; }
                            catch (Exception) { res = ""; }
                            // A resolved series with ZERO rows is a RESULT (no data in window), not a crash.
                            string status = n > 0 ? "OK" : "ADDED_NO_DATA";
                            m.WriteLine(okSyms[i] + "," + res + "," + status + ","
                                + (firstDt.ContainsKey(b) ? firstDt[b] : "") + ","
                                + (lastDt.ContainsKey(b) ? lastDt[b] : "") + ","
                                + n.ToString() + ","
                                + (chk.ContainsKey(b) ? chk[b].ToString("R") : "0") + ",");
                        }
                        for (int i = 0; i < badSyms.Count; i++)
                        {
                            string[] p = badSyms[i].Split('|');
                            m.WriteLine(p[0] + ",,FAILED_ADD,,,0,0," + (p.Length > 1 ? p[1] : ""));
                        }
                    }
                }
                catch (Exception) { }
            }
        }

        protected override void OnBarUpdate()
        {
            if (State == State.Realtime) return;
            if (w == null || lines >= MaxLines) return;
            int b = BarsInProgress;
            if (b < 1 || CurrentBars[b] < 0) return;      // b == 0 is the ANCHOR series; never exported
            if (b - 1 >= okSyms.Count) return;
            string req = okSyms[b - 1];
            string ts = Times[b][0].ToString("yyyy-MM-dd");
            w.WriteLine(req + ","
                + BarsArray[b].Instrument.FullName + ","
                + ts + ","
                + Opens[b][0].ToString("R") + ","
                + Highs[b][0].ToString("R") + ","
                + Lows[b][0].ToString("R") + ","
                + Closes[b][0].ToString("R") + ","
                + Volumes[b][0].ToString("F0"));
            lines++;
            if (!rows.ContainsKey(b)) { rows[b] = 0; firstDt[b] = ts; chk[b] = 0.0; }
            rows[b] = rows[b] + 1;
            lastDt[b] = ts;
            chk[b] = chk[b] + Closes[b][0] + Volumes[b][0];
        }
    }
}
