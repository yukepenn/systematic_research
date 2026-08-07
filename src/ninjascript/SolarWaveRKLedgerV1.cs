#region Using declarations
using System;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using System.Globalization;
using System.IO;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
using NinjaTrader.NinjaScript.Indicators;
#endregion

namespace NinjaTrader.NinjaScript.Strategies
{
    public class SolarWaveRKLedgerV1 : Strategy
    {
        private NinjaTrader.NinjaScript.Indicators.RenkoKings
            .RenkoKings_SolarWaveRK solarWave;
        private StreamWriter writer;

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = "SW01 per-bar Solar state ledger exporter; trades nothing";
                Name = "SolarWaveRKLedgerV1";
                Calculate = Calculate.OnBarClose;
                IsExitOnSessionCloseStrategy = false;
                BarsRequiredToTrade = 0;
                MaximumBarsLookBack = MaximumBarsLookBack.TwoHundredFiftySix;
                ExportPath = @"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\research\01_diagnostics\sw01_bar_ledger.csv";
            }
            else if (State == State.DataLoaded)
            {
                solarWave = RenkoKings_SolarWaveRK(Close, 90, 179, 5, 10, true, 10);
            }
            else if (State == State.Terminated)
            {
                if (writer != null)
                {
                    writer.Flush();
                    writer.Close();
                    writer = null;
                }
            }
        }

        protected override void OnBarUpdate()
        {
            if (BarsInProgress != 0)
                return;

            if (writer == null)
            {
                writer = new StreamWriter(ExportPath, false);
                writer.WriteLine(
                    "time,close,signal_trade,signal_trend,signal_wave,trailing_stop,trend_vector");
            }

            writer.WriteLine(string.Format(CultureInfo.InvariantCulture,
                "{0:yyyy-MM-ddTHH:mm:ss},{1},{2},{3},{4},{5},{6}",
                Time[0], Close[0],
                solarWave.Signal_Trade[0], solarWave.Signal_Trend[0],
                solarWave.Signal_Wave[0], solarWave.TrailingStop[0],
                solarWave.TrendVector[0]));
        }

        [NinjaScriptProperty]
        [Display(Name = "Export Path", Order = 1, GroupName = "Export")]
        public string ExportPath { get; set; }
    }
}
