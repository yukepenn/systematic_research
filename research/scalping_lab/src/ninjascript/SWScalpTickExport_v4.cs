#region Using declarations
using System;
using System.IO;
using System.Text;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
#endregion

// v4 = v3 verbatim (Last + Bid + Ask 1-tick series, NO ORDERS, historical only, fails closed in
// realtime) with ONE change: the output file ROLLS PER SESSION DATE. A single backtest range can
// therefore export many sessions without the single-file row cap truncating any of them - which is
// what silently truncated 17 of the existing substrate files at exactly 12,000,000 rows.
//
// Session date = (t + 6h).Date, which maps the 18:00 ET open onto the following calendar day. That
// is the convention the existing substrate MANIFEST already uses and it was verified against it.
namespace NinjaTrader.NinjaScript.Strategies
{
    public class SWScalpTickExport_v4 : Strategy
    {
        private StreamWriter w;
        private DateTime curSession = DateTime.MinValue;
        private long lines, nLast, nBid, nAsk;
        private DateTime tMin, tMax;
        private const long MaxLines = 25000000;

        [NinjaScriptProperty]
        public string ExportDir { get; set; }
        [NinjaScriptProperty]
        public string Prefix { get; set; }

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Name = "SWScalpTickExport_v4";
                Calculate = Calculate.OnEachTick;
                IsExitOnSessionCloseStrategy = false;
                ExportDir = @"D:\export";
                Prefix = "s";
            }
            else if (State == State.Configure)
            {
                AddDataSeries(null, new BarsPeriod { BarsPeriodType = BarsPeriodType.Tick, Value = 1, MarketDataType = MarketDataType.Bid });
                AddDataSeries(null, new BarsPeriod { BarsPeriodType = BarsPeriodType.Tick, Value = 1, MarketDataType = MarketDataType.Ask });
            }
            else if (State == State.DataLoaded)
            {
                Directory.CreateDirectory(ExportDir);
            }
            else if (State == State.Terminated)
            {
                CloseCurrent();
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
                    + (lines >= MaxLines ? "1" : "0") + ",SWScalpTickExport_v4");
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
                w = new StreamWriter(Path.Combine(ExportDir, Prefix + sess.ToString("yyyyMMdd") + "_ticks.csv"), false, Encoding.ASCII, 1 << 22);
                w.WriteLine("bip,time,price,volume");
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