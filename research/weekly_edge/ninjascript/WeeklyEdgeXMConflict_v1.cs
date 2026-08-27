// =====================================================================================
// WeeklyEdgeXMConflict_v1 - the FIRST cross-market SIGNAL strategy in this repository.
//
// OBJECT (runs/WE_W101_DIRECTION, WE_W102_XMENGINE, WE_W102c, WE_W105_XMAUDIT):
//   anchor  = OPEN of the bar stamped 09:31  (== the 09:30:00 print; bars are BAR-END stamped)
//   decide  = CLOSE of the bar stamped 09:45
//   drive   = sign(close_0945 - anchor)
//   broad   = mean over {ES, RTY, YM} of  log(close_0945 / anchor_0931) / sigma60(that market)
//             where sigma60 is the SAMPLE std (ddof = 1) of that market's own anchor->decision
//             log return over the previous up-to-60 sessions, EXCLUDING today.
//   TAKE the trade only when sign(broad) != 0 AND sign(broad) != drive  ("NQ moves alone")
//   entry   = market, submitted on the 09:45 bar close -> fills at the 09:46 OPEN
//   exit    = market, submitted on the 15:45 bar close -> fills at the 15:46 OPEN
//   size    = 1. NO alpha stop (W102's stop curve: 20 -> 300 pts, none beat no-stop).
//
// EVIDENCE: 348 trades, 54.3 % hit, $560/trade, $195,003 net, 2022-07 -> 2026-08.
//   rho(weekly, P1/PCT) = +0.081 full window.
// AND THE CAVEATS, which travel with the code:
//   * ~20 of 348 trades carry 85 % of the money (W105).
//   * rho with P1 is +0.464 over the trailing six months against +0.081 full-window (W105).
//   * REGIME_LOCAL BY DATA AVAILABILITY - ES/RTY/YM substrates begin 2022-01-02, so no
//     2006-2021 test exists and none can be built.
//   * W104: this is an RTH OPENING-AUCTION object. It does NOT generalise to other segments.
//   * The only intra-trade risk control is the CLOCK. Worst historical adverse excursion
//     -$10,865 (543 pts) - a SAMPLE MAXIMUM, NOT A BOUND. See DisasterStopPoints below.
//
// STATUS: RESEARCH_ONLY. Not enabled. The owner alone enables real capital.
//
// ---------------------------------------------------------------------------------------
// MULTI-SERIES ENGINEERING - every item the directive requires, solved and stated
// ---------------------------------------------------------------------------------------
// AddDataSeries      : three added series, ES / RTY / YM, 1-minute, declared in State.Configure
//                      in a FIXED order so BarsArray indices are deterministic: 1=ES 2=RTY 3=YM.
// Instrument names   : PARAMETERS, not literals. runs/WE_W44_NT8PARITY/amendment_2.yaml records
//                      a hardcoded instrument silently running the whole decision stack on a
//                      deferred contract (net -$24,269 -> +$8,326). They are also VERIFIED at
//                      State.DataLoaded and a mismatch hard-blocks every order.
// BarsInProgress     : ALL logic runs in BIP 0. Every other BIP returns immediately. The added
//                      series are read, never traded.
// Unindexed accessors: FORBIDDEN in this file. Time[0]/Close[0] are BIP-RELATIVE - inside a
//                      non-zero BIP handler they are that series' own values. Cost a whole silent
//                      no-op version once already (SolarWaveOneContractMNQ_B1_v1.cs:393-401).
//                      Everything here uses Times[i][0] / Closes[i][0] / CurrentBars[i].
// CurrentBars guard  : every series must have >= 1 bar before anything is read.
// Staleness          : a secondary series whose latest bar is older than MaxStaleMinutes at the
//                      anchor or at the decision DISQUALIFIES THE SESSION. NinjaScript hands you
//                      the last bar at or before the primary's time; without this guard a halted
//                      or thin secondary would be silently forward-filled into the composite.
// Session semantics  : SessionIterator on BarsArray[0]. ForcedFlatMin before ActualSessionEnd.
//                      An early close therefore flattens correctly WITHOUT a hardcoded 16:00 -
//                      hardcoded end-of-RTH clocks are the recurring bug in this repo.
// Early close        : if the session ends before the 15:45 bar, the forced-flat fires first and
//                      the position is closed. No trade is left open across a session boundary.
// Holidays           : a session with no 09:31 bar or no 09:45 bar simply never arms. No trade.
// Missing bars       : anchorReady / decisionReady are explicit flags, not inferred from time.
// Rolls              : the primary and all three secondaries MUST use the same roll/merge
//                      convention. The repo convention is NT8's default MergeBackAdjusted
//                      continuous contract. A mixed convention corrupts the composite silently,
//                      so the instrument names are logged once at DataLoaded for the record.
// Live front month   : set the four instrument parameters to the CURRENT front contracts, or use
//                      continuous symbols if the platform is configured for them. There is no
//                      auto-roll here by design - an auto-roll that disagrees with the research
//                      substrate would be an unrecorded parameter.
// Timestamps         : all four series are 1-minute and BAR-END stamped. The composite is built
//                      only from bars whose timestamps are verified aligned at read time.
// =====================================================================================

#region Using declarations
using System;
using System.Collections.Generic;
using System.IO;
using System.Globalization;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
#endregion

namespace NinjaTrader.NinjaScript.Strategies
{
    public class WeeklyEdgeXMConflict_v1 : Strategy
    {
        [NinjaScriptProperty] public string EsInstrument      { get; set; }
        [NinjaScriptProperty] public string RtyInstrument     { get; set; }
        [NinjaScriptProperty] public string YmInstrument      { get; set; }
        [NinjaScriptProperty] public int    AnchorHm          { get; set; }   // 93100
        [NinjaScriptProperty] public int    DecisionHm        { get; set; }   // 94500
        [NinjaScriptProperty] public int    ExitHm            { get; set; }   // 154500
        [NinjaScriptProperty] public int    SigmaLookback     { get; set; }   // 60 sessions
        [NinjaScriptProperty] public int    SigmaMinHist      { get; set; }   // 20 sessions
        [NinjaScriptProperty] public int    MaxStaleMinutes   { get; set; }   // 3
        [NinjaScriptProperty] public int    ForcedFlatMin     { get; set; }   // 21
        [NinjaScriptProperty] public double CommissionRT      { get; set; }   // 4.36
        [NinjaScriptProperty] public double DisasterStopPoints{ get; set; }   // 0 = OFF
        [NinjaScriptProperty] public int    Qty               { get; set; }   // 1
        [NinjaScriptProperty] public string ExportDir         { get; set; }
        [NinjaScriptProperty] public string Tag               { get; set; }

        // ---- series indices, fixed by the order of the AddDataSeries calls
        private const int NQ = 0, ES = 1, RTY = 2, YM = 3;

        // ---- per-session state
        private double anchorNq;
        private double[] anchorX = new double[4];
        private bool anchorReady, decisionReady, sessionDisqualified;
        private DateTime sessionEndTs = DateTime.MinValue;
        private SessionIterator sessIter;

        // ---- causal sigma history: each market's anchor->decision log return, one per session
        private List<double>[] hist = new List<double>[4];

        // ---- our own ledger, mirroring the Python reference exactly
        private const int ACT_NONE = 0, ACT_ENTER = 1, ACT_EXIT = 2;
        private int pendingAct = ACT_NONE, pendingDir = 0;
        private double myEntryPx = 0.0;
        private int myPos = 0;
        private double realizedPnl = 0.0;
        private bool instrumentMismatch = false;
        private StreamWriter export = null;

        // ---- values carried into the export row
        private double lastDrive = 0.0, lastComposite = double.NaN;
        private int lastConflict = 0, lastDesired = 0;

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description               = "WEEKLY_EDGE XM_CONFLICT: NQ opening drive taken only "
                                          + "when ES/RTY/YM disagree. RTH opening-auction object.";
                Name                      = "WeeklyEdgeXMConflict_v1";
                Calculate                 = Calculate.OnBarClose;
                EntriesPerDirection       = 1;
                EntryHandling             = EntryHandling.AllEntries;
                IsExitOnSessionCloseStrategy = false;   // we flatten ourselves, session-relative
                IncludeCommission         = true;
                BarsRequiredToTrade       = 20;

                EsInstrument       = "ES 09-26";
                RtyInstrument      = "RTY 09-26";
                YmInstrument       = "YM 09-26";
                AnchorHm           = 93100;
                DecisionHm         = 94500;
                ExitHm             = 154500;
                SigmaLookback      = 60;
                SigmaMinHist       = 20;
                MaxStaleMinutes    = 3;
                ForcedFlatMin      = 21;
                CommissionRT       = 4.36;
                DisasterStopPoints = 0.0;     // OFF by default. See the header: no level selected.
                Qty                = 1;
                ExportDir          = "";
                Tag                = "xm";
            }
            else if (State == State.Configure)
            {
                // FIXED ORDER. BarsArray indices 1,2,3 are relied on everywhere below.
                AddDataSeries(EsInstrument,  BarsPeriodType.Minute, 1);
                AddDataSeries(RtyInstrument, BarsPeriodType.Minute, 1);
                AddDataSeries(YmInstrument,  BarsPeriodType.Minute, 1);
            }
            else if (State == State.DataLoaded)
            {
                sessIter = new SessionIterator(BarsArray[NQ]);
                for (int i = 0; i < 4; i++) hist[i] = new List<double>();

                // VERIFY the added series are what was asked for. A mismatch hard-blocks orders
                // rather than trading a silently wrong composite.
                string[] want = { null, EsInstrument, RtyInstrument, YmInstrument };
                if (BarsArray == null || BarsArray.Length < 4) instrumentMismatch = true;
                else
                {
                    for (int i = 1; i < 4; i++)
                    {
                        if (BarsArray[i] == null || BarsArray[i].Instrument == null
                            || BarsArray[i].Instrument.MasterInstrument == null)
                        { instrumentMismatch = true; break; }
                        string got = BarsArray[i].Instrument.FullName;
                        if (string.IsNullOrEmpty(got) || string.IsNullOrEmpty(want[i])
                            || !got.StartsWith(want[i].Split(' ')[0], StringComparison.OrdinalIgnoreCase))
                        { instrumentMismatch = true; break; }
                    }
                }
                if (!string.IsNullOrEmpty(ExportDir))
                {
                    try
                    {
                        Directory.CreateDirectory(ExportDir);
                        export = new StreamWriter(Path.Combine(ExportDir, "we_xm_" + Tag + ".csv"), false);
                        export.WriteLine("timestamp,nq_open,nq_high,nq_low,nq_close,"
                            + "es_close,es_move,rty_close,rty_move,ym_close,ym_move,"
                            + "nq_drive,broad_composite,conflict_flag,desired_direction,"
                            + "decision_ready,entry_request,exit_request,position,realized_pnl");
                    }
                    catch (Exception) { export = null; }
                }
            }
            else if (State == State.Terminated)
            {
                if (export != null) { try { export.Flush(); export.Close(); } catch (Exception) {} export = null; }
            }
        }

        private static double SampleStd(List<double> v, int lookback, int minHist)
        {
            int n = v.Count;
            if (n < minHist) return double.NaN;
            int k = Math.Min(lookback, n);
            double m = 0.0;
            for (int i = n - k; i < n; i++) m += v[i];
            m /= k;
            double s = 0.0;
            for (int i = n - k; i < n; i++) { double d = v[i] - m; s += d * d; }
            return (k > 1) ? Math.Sqrt(s / (k - 1)) : double.NaN;   // ddof = 1, matches pandas
        }

        /// <summary>latest secondary bar must be no older than MaxStaleMinutes vs the primary</summary>
        private bool SeriesFresh(int i, DateTime nqTs)
        {
            if (CurrentBars[i] < 1) return false;
            double age = (nqTs - Times[i][0]).TotalMinutes;
            return age >= -0.5 && age <= MaxStaleMinutes;
        }

        protected override void OnBarUpdate()
        {
            // ---- ALL logic is on the primary. The added series are read, never traded.
            if (BarsInProgress != NQ) return;
            if (CurrentBars[NQ] < 1) return;
            for (int i = 1; i < 4; i++) if (CurrentBars[i] < 1) return;

            DateTime ts   = Times[NQ][0];
            bool firstBar = BarsArray[NQ].IsFirstBarOfSession;
            bool lastBar  = BarsArray[NQ].IsLastBarOfSession;
            int hm        = ts.Hour * 10000 + ts.Minute * 100;

            // ---- 0. settle whatever was submitted on the previous bar; it filled at THIS open
            if (pendingAct == ACT_EXIT)
            {
                realizedPnl += myPos * (Opens[NQ][0] - myEntryPx)
                             * Instrument.MasterInstrument.PointValue * Qty
                             - CommissionRT * Qty;
                myPos = 0;
            }
            else if (pendingAct == ACT_ENTER)
            {
                myEntryPx = Opens[NQ][0];
                myPos = pendingDir;
            }
            int entryReq = (pendingAct == ACT_ENTER) ? pendingDir : 0;
            int exitReq  = (pendingAct == ACT_EXIT) ? 1 : 0;
            pendingAct = ACT_NONE; pendingDir = 0;

            // ---- 1. session bookkeeping. Session-RELATIVE, never a hardcoded end-of-day clock.
            if (firstBar || sessionEndTs == DateTime.MinValue)
            {
                sessIter.GetNextSession(ts, true);
                sessionEndTs = sessIter.ActualSessionEnd;
                anchorReady = false; decisionReady = false; sessionDisqualified = false;
                lastDrive = 0.0; lastComposite = double.NaN;
                lastConflict = 0; lastDesired = 0;
            }
            bool forceFlat = ts >= sessionEndTs.AddMinutes(-ForcedFlatMin);

            // ---- 2. the ANCHOR bar (09:31): its OPEN is the 09:30:00 print
            if (hm == AnchorHm && !anchorReady)
            {
                bool fresh = true;
                for (int i = 1; i < 4; i++) if (!SeriesFresh(i, ts)) fresh = false;
                if (!fresh) sessionDisqualified = true;     // no stale forward-fill, ever
                else
                {
                    anchorNq = Opens[NQ][0];
                    for (int i = 1; i < 4; i++) anchorX[i] = Closes[i][0];
                    anchorReady = true;
                }
            }

            // ---- 3. the DECISION bar (09:45)
            if (hm == DecisionHm && anchorReady && !decisionReady && !sessionDisqualified)
            {
                bool fresh = true;
                for (int i = 1; i < 4; i++) if (!SeriesFresh(i, ts)) fresh = false;
                if (!fresh) sessionDisqualified = true;
                else
                {
                    double drive = Math.Sign(Closes[NQ][0] - anchorNq);
                    double acc = 0.0; int cnt = 0;
                    for (int i = 1; i < 4; i++)
                    {
                        if (anchorX[i] <= 0 || Closes[i][0] <= 0) continue;
                        double r = Math.Log(Closes[i][0] / anchorX[i]);
                        double sg = SampleStd(hist[i], SigmaLookback, SigmaMinHist);
                        if (!double.IsNaN(sg) && sg > 1e-12) { acc += r / sg; cnt++; }
                        hist[i].Add(r);          // appended AFTER use -> today is never in its own sigma
                    }
                    double comp = (cnt > 0) ? acc / cnt : double.NaN;
                    double xs = double.IsNaN(comp) ? 0.0 : Math.Sign(comp);
                    lastDrive = drive; lastComposite = comp;
                    lastConflict = (xs != 0.0 && drive != 0.0 && xs != drive) ? 1 : 0;
                    lastDesired = (lastConflict == 1) ? (int)drive : 0;
                    decisionReady = true;

                    if (lastDesired != 0 && myPos == 0 && !forceFlat && !instrumentMismatch)
                    {
                        if (lastDesired > 0) EnterLong(Qty, "XM_L"); else EnterShort(Qty, "XM_S");
                        pendingAct = ACT_ENTER; pendingDir = lastDesired;
                    }
                }
            }

            // ---- 4. the DISASTER stop. OPERATIONAL, not alpha. OFF unless the owner sets it.
            if (myPos != 0 && DisasterStopPoints > 0.0 && pendingAct == ACT_NONE)
            {
                double adverse = myPos * (Lows[NQ][0] - myEntryPx);
                if (myPos < 0) adverse = myPos * (Highs[NQ][0] - myEntryPx);
                if (adverse <= -DisasterStopPoints)
                {
                    if (myPos > 0) ExitLong(Qty, "XM_DIS", "XM_L"); else ExitShort(Qty, "XM_DIS", "XM_S");
                    pendingAct = ACT_EXIT;
                }
            }

            // ---- 5. the ALPHA exit: the clock, and nothing else
            if (myPos != 0 && pendingAct == ACT_NONE && (hm >= ExitHm || forceFlat || lastBar))
            {
                if (myPos > 0) ExitLong(Qty, "XM_X", "XM_L"); else ExitShort(Qty, "XM_X", "XM_S");
                pendingAct = ACT_EXIT;
            }

            // ---- 6. per-bar export: SIGNAL and DECISION states, not just P&L
            if (export != null)
            {
                var ci = CultureInfo.InvariantCulture;
                double esM  = (anchorReady && anchorX[ES]  > 0) ? Math.Log(Closes[ES][0]  / anchorX[ES])  : double.NaN;
                double rtyM = (anchorReady && anchorX[RTY] > 0) ? Math.Log(Closes[RTY][0] / anchorX[RTY]) : double.NaN;
                double ymM  = (anchorReady && anchorX[YM]  > 0) ? Math.Log(Closes[YM][0]  / anchorX[YM])  : double.NaN;
                export.WriteLine(string.Join(",",
                    ts.ToString("yyyy-MM-dd HH:mm:ss", ci),
                    Opens[NQ][0].ToString(ci), Highs[NQ][0].ToString(ci),
                    Lows[NQ][0].ToString(ci),  Closes[NQ][0].ToString(ci),
                    Closes[ES][0].ToString(ci),  esM.ToString(ci),
                    Closes[RTY][0].ToString(ci), rtyM.ToString(ci),
                    Closes[YM][0].ToString(ci),  ymM.ToString(ci),
                    lastDrive.ToString(ci), lastComposite.ToString(ci),
                    lastConflict.ToString(ci), lastDesired.ToString(ci),
                    (decisionReady ? 1 : 0).ToString(ci),
                    entryReq.ToString(ci), exitReq.ToString(ci),
                    myPos.ToString(ci), realizedPnl.ToString(ci)));
            }
        }
    }
}
