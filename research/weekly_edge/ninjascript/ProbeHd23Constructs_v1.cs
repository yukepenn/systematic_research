// =============================================================================================
// ProbeHd23Constructs_v1.cs -- SYNTHETIC COMPILE PROBE.  ZERO PROPRIETARY CONTENT.
//
// PURPOSE
//   Prove that every C# / NinjaScript construct INTRODUCED by the HD-20..23 challenger compiles
//   under this NT8 install, WITHOUT transmitting a single line of our strategy source anywhere.
//   There is no signal, no threshold, no parameter value, no ordering logic and no P&L here --
//   only the API surface.  CLAUDE.md section 6 sanctions exactly this: "a 25-line probe caught
//   the CS0118 Position/Instrument are properties trap on this port before any real source
//   existed.  A probe leaks nothing; the full file leaks everything."
//
// WHY IT EXISTS AT ALL
//   The challenger cannot be compiled the normal way today: copying a .cs into
//   bin/Custom/Strategies rebuilds NinjaTrader.Custom.dll for EVERY strategy in the install,
//   including the live real-money legs.  That is forbidden while the book is running.  So the
//   syntax question is answered by this probe INSTEAD, and it is answered at the 2026-09-21 roll
//   window as STEP 1 of the deployment procedure -- before any real source is copied, so a
//   failure aborts the deploy having changed nothing.
//
// CONSTRUCTS UNDER TEST (each one is new in the challenger and appears nowhere in v1)
//   1  private method with `out` parameters, guarded AFTER definite assignment
//   2  NinjaTrader.Cbi.Position from PositionsAccount[i]   (multi-series form)
//   3  NinjaTrader.Cbi.Position from PositionAccount       (single-series form)
//   4  Instruments[i].FullName / Instrument.FullName
//   5  File.WriteAllText / File.Exists / File.Replace(a,b,null) / File.Move / File.ReadAllText
//   6  Directory.GetFiles(dir, pattern) and Path.GetFileNameWithoutExtension
//   7  DateTime.TryParseExact with System.Globalization.DateTimeStyles.None
//   8  int.TryParse(string, out int)
//   9  ternary expression as an argument to Path.Combine
//  10  new StreamWriter(path, append:true) with AutoFlush
//  11  private const string inside a Strategy
//  12  ex.GetType().Name and ex.Message on a caught Exception
//  13  string[] Split(',') on File.ReadAllText(..).Trim()
//
// EXPECTED RESULT: compiles clean.  A CS#### here is a REAL defect in the challenger and must
// be fixed in build_hd23_challenger.py -- never by hand-editing a generated class.
// =============================================================================================
#region Using declarations
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
#endregion

namespace NinjaTrader.NinjaScript.Strategies
{
    public class ProbeHd23Constructs_v1 : Strategy
    {
        // 11 -- const string inside a Strategy
        private const string PW_OFF = "OFF", PW_DETECT = "DETECT", PW_ENFORCE = "ENFORCE";
        private const int SERIES_A = 0, SERIES_B = 1;

        private StreamWriter probeWriter = null;
        private string probePath = null;
        private string probeBusPath = null;

        [NinjaScriptProperty] public string ProbeDir      { get; set; }
        [NinjaScriptProperty] public string ProbeMode     { get; set; }
        [NinjaScriptProperty] public int    ProbeStaleSec { get; set; }
        [NinjaScriptProperty] public bool   ProbeStamp    { get; set; }

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Name = "ProbeHd23Constructs_v1";
                Calculate = Calculate.OnBarClose;
                IsUnmanaged = false;
                ProbeDir = ""; ProbeMode = PW_DETECT; ProbeStaleSec = 300; ProbeStamp = false;
            }
            else if (State == State.Configure)
            {
                // a second series so PositionsAccount[i] / Instruments[i] are legal
                AddDataSeries(BarsPeriodType.Minute, 1);
            }
        }

        // 1 + 2 -- out parameters, guard AFTER definite assignment, multi-series account position
        private bool ProbeAccountSignedQtyMulti(out int q)
        {
            q = 0;
            if (State != State.Realtime) return false;
            try
            {
                NinjaTrader.Cbi.Position pa = PositionsAccount[SERIES_B];
                if (pa == null) return false;
                q = (pa.MarketPosition == MarketPosition.Long)  ?  pa.Quantity
                  : (pa.MarketPosition == MarketPosition.Short) ? -pa.Quantity : 0;
                return true;
            }
            catch (Exception) { return false; }
        }

        // 3 -- single-series account position (the paper classes use this form)
        private bool ProbeAccountSignedQtySingle(out int q)
        {
            q = 0;
            if (State != State.Realtime) return false;
            try
            {
                NinjaTrader.Cbi.Position pa = PositionAccount;
                if (pa == null) return false;
                q = (pa.MarketPosition == MarketPosition.Long)  ?  pa.Quantity
                  : (pa.MarketPosition == MarketPosition.Short) ? -pa.Quantity : 0;
                return true;
            }
            catch (Exception) { return false; }
        }

        // 4 -- both instrument-name forms
        private string ProbeInstrNameMulti()
        { try { return Instruments[SERIES_B].FullName; } catch (Exception) { return "?"; } }

        private string ProbeInstrNameSingle()
        { try { return Instrument.FullName; } catch (Exception) { return "?"; } }

        // 5 + 9 -- whole-file publish with atomic replace
        private void ProbePublish(int signedQty)
        {
            if (State != State.Realtime) return;
            if (string.IsNullOrEmpty(ProbeDir)) return;
            try
            {
                if (probeBusPath == null)
                {
                    Directory.CreateDirectory(ProbeDir);
                    probeBusPath = Path.Combine(ProbeDir, "posbus_probe.csv");
                }
                string line = DateTime.UtcNow.ToString("yyyy-MM-dd HH:mm:ss", CultureInfo.InvariantCulture)
                            + ",probe," + ProbeInstrNameMulti() + "," + signedQty;
                string tmp = probeBusPath + ".tmp";
                File.WriteAllText(tmp, line);
                if (File.Exists(probeBusPath)) File.Replace(tmp, probeBusPath, null);
                else                           File.Move(tmp, probeBusPath);
            }
            catch (Exception ex) { Print("probe publish " + ex.GetType().Name + ": " + ex.Message); }
        }

        // 6 + 7 + 8 + 13 -- directory scan, exact timestamp parse, int parse, split
        private bool ProbeReadOthers(out int others, out string why)
        {
            others = 0; why = "";
            if (State != State.Realtime) { why = "not_realtime"; return false; }
            if (string.IsNullOrEmpty(ProbeDir)) { why = "dir_unset"; return false; }
            try
            {
                string me = ProbeInstrNameMulti();
                if (me == "?") { why = "instrument_unreadable"; return false; }
                string[] files = Directory.GetFiles(ProbeDir, "posbus_*.csv");
                foreach (string f in files)
                {
                    string bn = Path.GetFileNameWithoutExtension(f);
                    if (bn == "posbus_probe") continue;
                    string[] p = File.ReadAllText(f).Trim().Split(',');
                    if (p.Length < 4) { why = "malformed:" + bn; return false; }
                    if (p[2] != me) continue;
                    int q;
                    if (!int.TryParse(p[3], out q)) { why = "badqty:" + bn; return false; }
                    DateTime tsx;
                    if (!DateTime.TryParseExact(p[0], "yyyy-MM-dd HH:mm:ss", CultureInfo.InvariantCulture,
                            System.Globalization.DateTimeStyles.None, out tsx))
                    { why = "badts:" + bn; return false; }
                    others += q;
                    double ageSec = (DateTime.UtcNow - tsx).TotalSeconds;
                    if (ageSec > Math.Max(1, ProbeStaleSec)) Print("probe stale " + bn + " " + (int)ageSec);
                }
                return true;
            }
            catch (Exception ex) { why = "read_failed:" + ex.GetType().Name; return false; }
        }

        // 9 + 10 + 12 -- ternary into Path.Combine, append-mode reopen, loud catch
        private void ProbeExportEnsure()
        {
            if (State != State.Realtime) return;
            if (string.IsNullOrEmpty(ProbeDir)) return;
            if (probeWriter != null) return;
            try
            {
                Directory.CreateDirectory(ProbeDir);
                probePath = Path.Combine(ProbeDir, ProbeStamp
                    ? ("probe_" + DateTime.UtcNow.ToString("yyyyMMdd_HHmmss") + "Z.csv")
                    : "probe.csv");
                StreamWriter w = new StreamWriter(probePath, true);
                w.AutoFlush = true;
                probeWriter = w;
            }
            catch (Exception ex)
            {
                probeWriter = null;
                Print("probe open failed " + ex.GetType().Name + ": " + ex.Message
                    + " path=" + (probePath == null ? "?" : probePath));
            }
        }

        // the exit-clamp shape, with no strategy semantics attached
        private int ProbeClamp(int want, bool iAmLong, int actual, int others)
        {
            if (State != State.Realtime) return want;
            if (ProbeMode != PW_ENFORCE) return want;
            int implied = actual - others;
            int have = iAmLong ? implied : -implied;
            return Math.Max(0, Math.Min(want, have));
        }

        protected override void OnBarUpdate()
        {
            if (BarsInProgress != SERIES_A) return;
            if (State != State.Realtime) return;
            if (CurrentBars[SERIES_A] < 1 || CurrentBars[SERIES_B] < 1) return;

            ProbeExportEnsure();
            ProbePublish(0);

            int others; string why;
            bool ok = ProbeReadOthers(out others, out why);
            int a1, a2;
            bool ok1 = ProbeAccountSignedQtyMulti(out a1);
            bool ok2 = ProbeAccountSignedQtySingle(out a2);
            int clamped = ProbeClamp(3, true, a1, others);

            if (probeWriter != null)
                probeWriter.WriteLine(string.Format(CultureInfo.InvariantCulture,
                    "{0},{1},{2},{3},{4},{5},{6},{7}",
                    Time[0], ok, why, others, ok1, a1, ok2, clamped)
                    + "," + ProbeInstrNameSingle() + "," + PW_OFF);
        }
    }
}
