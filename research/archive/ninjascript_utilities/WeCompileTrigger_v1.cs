#region Using declarations
using System;
using NinjaTrader.NinjaScript;
#endregion

// Inert stub written only to trigger NinjaTrader's own recompile of the Custom folder so that
// WeeklyEdgeP1_v1.cs (copied in separately) is built into NinjaTrader.Custom.dll.
// It draws nothing, calculates nothing, and holds no state.
namespace NinjaTrader.NinjaScript.Indicators
{
	public class WeCompileTrigger_v1 : Indicator
	{
		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Name = "WeCompileTrigger_v1";
				Description = "Inert compile trigger for campaign #7 WEEKLY_EDGE. Does nothing.";
				Calculate = Calculate.OnBarClose;
				IsOverlay = false;
				DisplayInDataBox = false;
				PaintPriceMarkers = false;
			}
		}

		protected override void OnBarUpdate() { }
	}
}
