using System;
using System.Globalization;
using System.IO;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;

namespace NinjaTrader.NinjaScript.Strategies
{
    // POST_CAMPAIGN_AUDIT_01 bar exporter: writes the exact primary-series bars the
    // Strategy Analyzer engine feeds a strategy (merged/back-adjusted, Calculate.OnBarClose).
    // Trades nothing. Vendor-free. Added for AUDIT-03 (true bar-level MTM): no committed
    // bar series covered the extended 2022-01 -> 2026-07 window before this.
    public class AuditBarExport1 : Strategy
    {
        private StreamWriter w;

        [NinjaScriptProperty]
        public string ExportPath { get; set; }

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Name = "AuditBarExport1";
                Calculate = Calculate.OnBarClose;
                IsExitOnSessionCloseStrategy = false;
                BarsRequiredToTrade = 0;
                IsInstantiatedOnEachOptimizationIteration = true;
                ExportPath = "";
            }
            else if (State == State.Terminated)
            {
                if (w != null)
                {
                    try { w.Flush(); w.Close(); } catch (Exception) { }
                    w = null;
                }
            }
        }

        protected override void OnBarUpdate()
        {
            if (BarsInProgress != 0) return;
            if (string.IsNullOrEmpty(ExportPath)) return;
            if (w == null)
            {
                w = new StreamWriter(ExportPath, false);
                w.WriteLine("time,open,high,low,close,volume,first_bar_of_session");
            }
            w.WriteLine(string.Format(CultureInfo.InvariantCulture,
                "{0:yyyy-MM-ddTHH:mm:ss},{1:R},{2:R},{3:R},{4:R},{5:R},{6}",
                Time[0], Open[0], High[0], Low[0], Close[0], Volume[0],
                Bars.IsFirstBarOfSession ? 1 : 0));
        }
    }
}
