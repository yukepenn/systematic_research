#region Using declarations
using System;
using System.IO;
using System.Text;
using System.Collections.Generic;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
#endregion

// SWContractFetch_v1 - CACHE WARMER. Places NO ORDERS. Historical data only.
//
// Purpose: trigger NT8 to download TRUE, UNMERGED contract history into
// db\day\<CONTRACT>\<YEAR>.Last.ncd, which Python then reads directly.
//
// Why BarsRequest and not AddDataSeries: AddDataSeries resolves through the instrument's
// MergePolicy, which for futures defaults to MergeBackAdjusted and yields a back-adjusted splice
// (measured: ES 12-11 minus ES 03-11 is EXACTLY -16.000, sd 0.0000, across all of 2010 - that
// constant IS the roll basis). BarsRequest exposes MergePolicy directly, so DoNotMerge can be
// requested WITHOUT mutating any NT8 instrument or global setting.
namespace NinjaTrader.NinjaScript.Strategies
{
    public class SWContractFetch_v1 : Strategy
    {
        private int issued;
        private int done;
        private StreamWriter log;
        private object gate = new object();

        [NinjaScriptProperty]
        public string ExportDir { get; set; }
        [NinjaScriptProperty]
        public string Tag { get; set; }
        [NinjaScriptProperty]
        public string Symbols { get; set; }
        [NinjaScriptProperty]
        public string FromDate { get; set; }
        [NinjaScriptProperty]
        public string ToDate { get; set; }

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Name = "SWContractFetch_v1";
                Calculate = Calculate.OnBarClose;
                IsExitOnSessionCloseStrategy = false;
                ExportDir = @"C:\temp";
                Tag = "fetch";
                Symbols = "";
                FromDate = "2009-01-01";
                ToDate = "2019-12-31";
            }
            else if (State == State.DataLoaded)
            {
                DateTime f = DateTime.Parse(FromDate);
                DateTime t = DateTime.Parse(ToDate);
                try
                {
                    Directory.CreateDirectory(ExportDir);
                    log = new StreamWriter(Path.Combine(ExportDir, Tag + "_fetch.csv"), false, Encoding.ASCII);
                    log.WriteLine("requested,status,bars,detail");
                    log.Flush();
                }
                catch (Exception) { log = null; }

                string[] syms = (Symbols ?? "").Split(',');
                for (int i = 0; i < syms.Length; i++)
                {
                    string s = syms[i].Trim();
                    if (s.Length == 0) continue;
                    try
                    {
                        Instrument inst = Instrument.GetInstrument(s);
                        if (inst == null) { Write(s, "NO_INSTRUMENT", 0, ""); continue; }
                        BarsRequest br = new BarsRequest(inst, f, t);
                        br.BarsPeriod = new BarsPeriod { BarsPeriodType = BarsPeriodType.Day, Value = 1 };
                        br.MergePolicy = MergePolicy.DoNotMerge;
                        string cap = s;
                        issued++;
                        br.Request((req, err, msg) =>
                        {
                            int n = 0;
                            try { if (req != null && req.Bars != null) n = req.Bars.Count; }
                            catch (Exception) { }
                            Write(cap, err.ToString(), n, msg == null ? "" : msg.Replace(",", ";"));
                            try { req.Dispose(); } catch (Exception) { }
                        });
                    }
                    catch (Exception ex) { Write(s, "THREW", 0, ex.GetType().Name); }
                }
            }
            else if (State == State.Terminated)
            {
                try { if (log != null) { log.Flush(); log.Close(); log = null; } }
                catch (Exception) { }
            }
        }

        private void Write(string sym, string status, int bars, string detail)
        {
            lock (gate)
            {
                done++;
                try
                {
                    if (log != null) { log.WriteLine(sym + "," + status + "," + bars.ToString() + "," + detail); log.Flush(); }
                }
                catch (Exception) { }
            }
        }

        protected override void OnBarUpdate() { }
    }
}