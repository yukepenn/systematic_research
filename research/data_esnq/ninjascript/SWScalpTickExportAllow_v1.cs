#region Using declarations
using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
#endregion

// SWScalpTickExportAllow_v1 = SWScalpTickExport_v4 with ONE change, and it is a safety change:
// an ALLOW-LIST. The exporter physically CANNOT write a session that is not on the list.
//
// WHY THIS EXISTS. On 2026-08-28 a single-session export was requested with
//     from = 2025-08-13T22:00:00Z  (= 2025-08-13 18:00 ET, the open of session 2025-08-14)
// and NT8 loaded bars back to 2025-08-12 18:00 ET - a FULL SESSION EARLIER than requested - so
// SWScalpTickExport_v4 wrote s20250813_ticks.csv. Session 2025-08-13 is in the ESNQ BLIND manifest.
// The file was deleted unread, but the lesson is a data contract, not an accident:
//
//     RunStrategyBacktest's `from` DOES NOT BOUND THE DATA THE STRATEGY SEES.
//
// A date range is therefore NOT a safe isolation mechanism for a blind pool. The allow-list is,
// because it is enforced at the only place that writes bytes.
//
// AllowListFile: a text file, one session date per line, format yyyyMMdd (a leading 's' and any
// CSV remainder after a comma are tolerated, so a manifest column can be pasted in). If the file
// is missing or empty the strategy writes NOTHING and says so - it fails CLOSED, never open.
namespace NinjaTrader.NinjaScript.Strategies
{
    public class SWScalpTickExportAllow_v1 : Strategy
    {
        private StreamWriter w;
        private DateTime curSession = DateTime.MinValue;
        private long lines, nLast, nBid, nAsk;
        private DateTime tMin, tMax;
        private const long MaxLines = 25000000;
        private HashSet<string> allow = new HashSet<string>();
        private HashSet<string> skipped = new HashSet<string>();
        private bool allowLoaded;

        [NinjaScriptProperty]
        public string ExportDir { get; set; }
        [NinjaScriptProperty]
        public string Prefix { get; set; }
        [NinjaScriptProperty]
        public string AllowListFile { get; set; }

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Name = "SWScalpTickExportAllow_v1";
                Calculate = Calculate.OnEachTick;
                IsExitOnSessionCloseStrategy = false;
                ExportDir = @"D:\export";
                Prefix = "s";
                AllowListFile = "";
            }
            else if (State == State.Configure)
            {
                AddDataSeries(null, new BarsPeriod { BarsPeriodType = BarsPeriodType.Tick, Value = 1, MarketDataType = MarketDataType.Bid });
                AddDataSeries(null, new BarsPeriod { BarsPeriodType = BarsPeriodType.Tick, Value = 1, MarketDataType = MarketDataType.Ask });
            }
            else if (State == State.DataLoaded)
            {
                Directory.CreateDirectory(ExportDir);
                LoadAllow();
            }
            else if (State == State.Terminated)
            {
                CloseCurrent();
                WriteSkipLog();
            }
        }

        private void LoadAllow()
        {
            allow.Clear();
            allowLoaded = false;
            try
            {
                if (!string.IsNullOrEmpty(AllowListFile) && File.Exists(AllowListFile))
                {
                    foreach (string raw in File.ReadAllLines(AllowListFile))
                    {
                        string s = raw.Trim();
                        if (s.Length == 0) continue;
                        int c = s.IndexOf(',');
                        if (c >= 0) s = s.Substring(0, c);
                        s = s.Trim().Replace("-", "");
                        if (s.StartsWith("s") || s.StartsWith("S")) s = s.Substring(1);
                        if (s.Length == 8)
                        {
                            long probe;
                            if (long.TryParse(s, out probe)) allow.Add(s);
                        }
                    }
                    allowLoaded = allow.Count > 0;
                }
            }
            catch (Exception) { allowLoaded = false; }

            // FAIL CLOSED. An unreadable or empty allow-list must export nothing, never everything.
            using (StreamWriter lg = new StreamWriter(Path.Combine(ExportDir, "_allowlist_status.txt"), false, Encoding.ASCII))
            {
                lg.WriteLine("allow_list_file=" + AllowListFile);
                lg.WriteLine("loaded=" + (allowLoaded ? "1" : "0"));
                lg.WriteLine("n_allowed=" + allow.Count);
                lg.WriteLine("policy=FAIL_CLOSED: if loaded=0 nothing is written");
            }
        }

        private void WriteSkipLog()
        {
            using (StreamWriter lg = new StreamWriter(Path.Combine(ExportDir, "_skipped_sessions.txt"), true, Encoding.ASCII))
            {
                foreach (string s in skipped) lg.WriteLine(s);
            }
        }

        private void CloseCurrent()
        {
            if (w == null) return;
            w.Flush();
            w.Close();
            w = null;
            string man = Path.Combine(ExportDir, "_manifest.csv");
            bool hdr = !File.Exists(man);
            using (StreamWriter m = new StreamWriter(man, true, Encoding.ASCII))
            {
                if (hdr) m.WriteLine("session,rows,trades,bid_ev,ask_ev,t_min,t_max,capped,src");
                m.WriteLine(Prefix + curSession.ToString("yyyyMMdd") + "," + lines + "," + nLast
                    + "," + nBid + "," + nAsk + ","
                    + tMin.ToString("yyyy-MM-dd HH:mm:ss.fffffff") + ","
                    + tMax.ToString("yyyy-MM-dd HH:mm:ss.fffffff") + ","
                    + (lines >= MaxLines ? "1" : "0") + ",SWScalpTickExportAllow_v1");
            }
        }

        protected override void OnBarUpdate()
        {
            if (State == State.Realtime) return;
            int b = BarsInProgress;
            if (b < 0 || CurrentBars[b] < 0) return;
            DateTime t = Times[b][0];
            DateTime sess = t.AddHours(6).Date;
            if (sess != curSession)
            {
                CloseCurrent();
                curSession = sess;
                lines = 0; nLast = 0; nBid = 0; nAsk = 0;
                tMin = t; tMax = t;
                string key = sess.ToString("yyyyMMdd");
                if (allowLoaded && allow.Contains(key))
                {
                    w = new StreamWriter(Path.Combine(ExportDir, Prefix + key + "_ticks.csv"), false, Encoding.ASCII, 1 << 22);
                    w.WriteLine("bip,time,price,volume");
                }
                else
                {
                    w = null;                    // NOT ALLOWED: no writer is ever opened
                    skipped.Add(key);
                }
            }
            if (w == null || lines >= MaxLines) return;
            w.WriteLine(b.ToString() + ","
                + t.ToString("yyyy-MM-dd HH:mm:ss.fffffff") + ","
                + Closes[b][0].ToString("F2") + ","
                + Volumes[b][0].ToString("F0"));
            lines++;
            if (b == 0) nLast++; else if (b == 1) nBid++; else nAsk++;
            if (t < tMin) tMin = t;
            if (t > tMax) tMax = t;
        }
    }
}
