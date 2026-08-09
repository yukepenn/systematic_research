#region Using declarations
using System;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using System.Globalization;
using System.IO;
using System.Text;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
#endregion

// BarExportV1 - plain OHLCV bar exporter, no indicator and no vendor dependency.
// Used to feed the directional-change / overshoot analytics (DR-01, DR-04) with
// full-history price data without burning any strategy search-space configs.
namespace NinjaTrader.NinjaScript.Strategies
{
    public class BarExportV1 : Strategy
    {
        private StringBuilder buf;
        private int rows;

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = "Plain OHLCV bar exporter; trades nothing";
                Name = "BarExportV1";
                Calculate = Calculate.OnBarClose;
                IsExitOnSessionCloseStrategy = false;
                BarsRequiredToTrade = 0;
                MaximumBarsLookBack = MaximumBarsLookBack.TwoHundredFiftySix;
                ExportPath = "";
            }
            else if (State == State.Configure)
            {
                buf = new StringBuilder(1 << 22);
                rows = 0;
            }
            else if (State == State.Terminated)
            {
                Flush();
            }
        }

        private void Flush()
        {
            if (string.IsNullOrEmpty(ExportPath) || buf == null)
                return;
            try
            {
                string dir = Path.GetDirectoryName(ExportPath);
                if (!string.IsNullOrEmpty(dir) && !Directory.Exists(dir))
                    Directory.CreateDirectory(dir);
                using (StreamWriter w = new StreamWriter(ExportPath, false))
                {
                    w.WriteLine(string.Format(CultureInfo.InvariantCulture,
                        "# instrument={0} period={1} tick={2} rows={3}",
                        Instrument != null ? Instrument.FullName : "?",
                        BarsPeriod != null ? BarsPeriod.ToString() : "?", TickSize, rows));
                    w.WriteLine("time,open,high,low,close,volume,fbos");
                    w.Write(buf.ToString());
                    w.Flush();
                }
            }
            catch (Exception ex)
            {
                Print("BarExportV1 failed: " + ex.Message);
            }
        }

        protected override void OnBarUpdate()
        {
            if (BarsInProgress != 0 || buf == null)
                return;
            buf.AppendLine(string.Format(CultureInfo.InvariantCulture,
                "{0:yyyy-MM-ddTHH:mm:ss},{1},{2},{3},{4},{5},{6}",
                Time[0], Open[0], High[0], Low[0], Close[0], Volume[0],
                Bars.IsFirstBarOfSession ? 1 : 0));
            rows++;
        }

        [NinjaScriptProperty]
        [Display(Name = "Export Path", Order = 1, GroupName = "Export")]
        public string ExportPath { get; set; }
    }
}
