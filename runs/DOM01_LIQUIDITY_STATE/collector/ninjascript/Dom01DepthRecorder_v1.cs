#region Using declarations
using System;
using System.IO;
using System.Text;
using System.Security.Cryptography;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
#endregion

// =============================================================================================
// Dom01DepthRecorder_v1  --  DOM01 forward-collection Level-II / top-of-book logger.
//
// RESEARCH-ONLY. This file contains NO order-management code anywhere:
//   - No EnterLong / EnterShort / ExitLong / ExitShort / SetStopLoss / SetProfitTarget.
//   - No SubmitOrderUnmanaged / OnOrderUpdate / OnExecutionUpdate.
//   - No Account references of any kind.
// It is built as an Indicator, not a Strategy, specifically so the order-management method
// surface (EnterLong/EnterShort/etc.) does not even EXIST on the base class this script derives
// from -- that is a structural guarantee, not just a coding discipline.
//
// What it does: subscribes (implicitly, via NinjaScript's standard event model -- see report)
// to OnMarketDepth (MBP-level depth-by-price-level events) and OnMarketData (top-of-book
// Last/Bid/Ask) for whatever single instrument it is attached to, and writes every event to
// append-only CSV files on disk, plus a JSON run manifest with source/connection identity,
// schema version, disclosed limitations, and (at Terminated) SHA-256 checksums of each file.
//
// Schema honesty notes (see REPORT.md for full detail):
//   - This is MBP depth (price-level aggregated: side + level/position + price + size +
//     Add/Update/Remove), NOT MBO (no per-order IDs, no order-level granularity).
//   - No queue priority is recorded because the standard NinjaScript OnMarketDepth API does not
//     expose it.
//   - "SeqLocal" columns are collector-generated monotonic counters per output stream, NOT a
//     genuine exchange-assigned match/sequence number (the API exposes no such field).
//   - EventTime is NinjaScript's e.Time exactly as delivered, unmodified. Its precise timezone
//     semantics for live OnMarketDepth/OnMarketData callbacks were NOT independently verified
//     this pass (only the historical "Simulation" connection was available, and per the DOM01
//     finding it does not deliver depth at all). Verify on first live/replay attach -- see
//     REPORT.md.
// =============================================================================================

namespace NinjaTrader.NinjaScript.Indicators
{
    public class Dom01DepthRecorder_v1 : Indicator
    {
        private const string SchemaVersion = "dom01-collector-schema-v1";

        private readonly object sync = new object();

        private string runId;
        private DateTime startUtc;
        private string baseDir;
        private string filePrefix;

        private string manifestPath;
        private string depthPath;
        private string tobPath;
        private string eventsPath;
        private string heartbeatPath;

        private StreamWriter depthWriter;
        private StreamWriter tobWriter;
        private StreamWriter eventsWriter;
        private StreamWriter heartbeatWriter;

        private long depthSeq;
        private long tobSeq;
        private long eventsSeq;
        private long heartbeatSeq;

        private long depthRowsWritten;
        private long tobRowsWritten;
        private bool depthCapReached;
        private bool tobCapReached;

        private DateTime lastDepthRecordedUtc = DateTime.MinValue;
        private DateTime lastTobRecordedUtc = DateTime.MinValue;

        private bool fatalError;
        private int barsSinceHeartbeat;

        // Connection identity captured at first opportunity (DataLoaded, refreshed if unknown).
        private string connTypeName = "UNKNOWN_NOT_CONNECTED_AT_INIT";
        private string connOptionsTypeName = "UNKNOWN_NOT_CONNECTED_AT_INIT";
        private string connDisableL2Data = "UNKNOWN_NOT_CONNECTED_AT_INIT";
        private string connStatusAtInit = "UNKNOWN_NOT_CONNECTED_AT_INIT";

        [NinjaScriptProperty]
        public string ExportDir { get; set; }

        [NinjaScriptProperty]
        public string Tag { get; set; }

        [NinjaScriptProperty]
        public int MaxRowsPerStreamFile { get; set; }

        [NinjaScriptProperty]
        public int FlushEveryNEvents { get; set; }

        [NinjaScriptProperty]
        public bool RecordTopOfBook { get; set; }

        [NinjaScriptProperty]
        public int HeartbeatEveryNBars { get; set; }

        // DOM_PAUSE_CLEANUP_20260812: project-policy fail-closed guard, effective 2026-08-12
        // after a resource-instability incident during heavy DOM/Replay work. Defaults to
        // false (paused) on every fresh add/reload -- NinjaScript re-applies [SetDefaults] on
        // each new instance, so this cannot be silently left "on" from a prior session. Do NOT
        // flip this default to true without explicit, dated owner re-authorization recorded in
        // research/system_master/DOM_PAUSE_CLEANUP_20260812.md and
        // research/data_forward_sealed/DOM01/DOM01_DATA_GOVERNANCE.md.
        [NinjaScriptProperty]
        public bool DomCollectionEnabled { get; set; }

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Name = "Dom01DepthRecorder_v1";
                Description = "Research-only DOM01 forward-collection logger: MBP depth + top-of-book + connection events. No order methods. See runs/DOM01_LIQUIDITY_STATE/collector/REPORT.md. PAUSED by project policy as of 2026-08-12 -- set DomCollectionEnabled=true to override only after explicit owner re-authorization.";
                IsOverlay = false;
                Calculate = Calculate.OnEachTick;
                ExportDir = @"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\runs\DOM01_LIQUIDITY_STATE\collector\out";
                Tag = "dom01";
                MaxRowsPerStreamFile = 20000000;
                FlushEveryNEvents = 500;
                RecordTopOfBook = true;
                HeartbeatEveryNBars = 1;
                DomCollectionEnabled = false;
            }
            else if (State == State.DataLoaded)
            {
                InitializeRun();
            }
            else if (State == State.Realtime)
            {
                WriteEvent("STATE_TRANSITION", "Entered State.Realtime (live event delivery begins here; State.Historical never carries depth locally per DOM01 -- no Market Replay depth files exist on this install).");
            }
            else if (State == State.Terminated)
            {
                FinalizeRun();
            }
        }

        private void InitializeRun()
        {
            if (!DomCollectionEnabled)
            {
                Print("DOM / Level-II collection is paused by project policy. Explicit authorization is required to enable it. " +
                      "See research/system_master/DOM_PAUSE_CLEANUP_20260812.md. This indicator will not open any output files, " +
                      "capture any connection identity, or record any depth/top-of-book/event data while paused.");
                return;
            }

            lock (sync)
            {
                try
                {
                    runId = Guid.NewGuid().ToString("N");
                    startUtc = DateTime.UtcNow;
                    baseDir = ExportDir;
                    Directory.CreateDirectory(baseDir);

                    filePrefix = Tag + "_" + startUtc.ToString("yyyyMMdd_HHmmss") + "_" + runId.Substring(0, 8);
                    manifestPath = Path.Combine(baseDir, filePrefix + "_manifest.json");
                    depthPath = Path.Combine(baseDir, filePrefix + "_depth.csv");
                    tobPath = Path.Combine(baseDir, filePrefix + "_topofbook.csv");
                    eventsPath = Path.Combine(baseDir, filePrefix + "_events.csv");
                    heartbeatPath = Path.Combine(baseDir, filePrefix + "_heartbeat.csv");

                    depthWriter = new StreamWriter(depthPath, false, Encoding.ASCII, 1 << 20);
                    depthWriter.WriteLine("RunId,SeqLocal,RecordedUtc,EventTime,EventTimeKind,Side,Level,Price,Size,Operation,MarketMaker,IsReset,IsTopOfBook");

                    tobWriter = new StreamWriter(tobPath, false, Encoding.ASCII, 1 << 20);
                    tobWriter.WriteLine("RunId,SeqLocal,RecordedUtc,EventTime,EventTimeKind,Type,Price,Size");

                    eventsWriter = new StreamWriter(eventsPath, false, Encoding.ASCII, 1 << 16);
                    eventsWriter.WriteLine("RunId,SeqLocal,RecordedUtc,Category,Detail");

                    heartbeatWriter = new StreamWriter(heartbeatPath, false, Encoding.ASCII, 1 << 16);
                    heartbeatWriter.WriteLine("RunId,SeqLocal,RecordedUtc,BarTime,DepthRowsWritten,TopOfBookRowsWritten,SecondsSinceLastDepthEvent,SecondsSinceLastTobEvent");

                    CaptureConnectionIdentity();
                    WriteManifest(false);
                    WriteEvent("STATE_TRANSITION", "InitializeRun complete at State.DataLoaded. RunId=" + runId);
                }
                catch (Exception ex)
                {
                    fatalError = true;
                    TrySwallow(delegate { File.AppendAllText(Path.Combine(ExportDir ?? ".", "dom01_collector_fatal_errors.txt"), DateTime.UtcNow.ToString("o") + " InitializeRun: " + ex + Environment.NewLine); });
                }
            }
        }

        private void CaptureConnectionIdentity()
        {
            try
            {
                Connection conn = Instrument.GetMarketDataConnection();
                if (conn != null)
                {
                    connTypeName = conn.GetType().Name;
                    connStatusAtInit = conn.Status.ToString() + " / price=" + conn.PriceStatus.ToString();
                    if (conn.Options != null)
                    {
                        connOptionsTypeName = conn.Options.TypeName;
                        connDisableL2Data = conn.Options.DisableL2Data.ToString();
                    }
                }
            }
            catch (Exception ex)
            {
                TrySwallow(delegate { WriteEvent("WARN", "CaptureConnectionIdentity failed: " + ex.Message); });
            }
        }

        protected override void OnMarketDepth(MarketDepthEventArgs e)
        {
            if (State != State.Realtime || fatalError) return;
            lock (sync)
            {
                try
                {
                    if (depthWriter == null || depthCapReached) return;
                    depthSeq++;
                    DateTime recordedUtc = DateTime.UtcNow;
                    lastDepthRecordedUtc = recordedUtc;

                    depthWriter.WriteLine(
                        runId + "," +
                        depthSeq.ToString() + "," +
                        recordedUtc.ToString("yyyy-MM-dd HH:mm:ss.fffffff") + "Z," +
                        e.Time.ToString("yyyy-MM-dd HH:mm:ss.fffffff") + "," +
                        e.Time.Kind.ToString() + "," +
                        e.MarketDataType.ToString() + "," +
                        e.Position.ToString() + "," +
                        e.Price.ToString("R") + "," +
                        e.Volume.ToString() + "," +
                        e.Operation.ToString() + "," +
                        Csv(e.MarketMaker) + "," +
                        e.IsReset.ToString() + "," +
                        (e.Position == 0).ToString());

                    depthRowsWritten++;
                    if (depthRowsWritten % FlushEveryNEvents == 0) depthWriter.Flush();

                    if (depthRowsWritten >= MaxRowsPerStreamFile && !depthCapReached)
                    {
                        depthCapReached = true;
                        depthWriter.Flush();
                        WriteEvent("CAP_REACHED", "depth stream hit MaxRowsPerStreamFile=" + MaxRowsPerStreamFile + "; further depth rows are dropped for this run (file/session boundary, not a silent data loss point -- restart the collector to open a new run).");
                    }
                }
                catch (Exception ex)
                {
                    HandleFatal("OnMarketDepth", ex);
                }
            }
        }

        protected override void OnMarketData(MarketDataEventArgs e)
        {
            if (State != State.Realtime || fatalError || !RecordTopOfBook) return;
            if (e.MarketDataType != MarketDataType.Bid && e.MarketDataType != MarketDataType.Ask && e.MarketDataType != MarketDataType.Last) return;
            lock (sync)
            {
                try
                {
                    if (tobWriter == null || tobCapReached) return;
                    tobSeq++;
                    DateTime recordedUtc = DateTime.UtcNow;
                    lastTobRecordedUtc = recordedUtc;

                    tobWriter.WriteLine(
                        runId + "," +
                        tobSeq.ToString() + "," +
                        recordedUtc.ToString("yyyy-MM-dd HH:mm:ss.fffffff") + "Z," +
                        e.Time.ToString("yyyy-MM-dd HH:mm:ss.fffffff") + "," +
                        e.Time.Kind.ToString() + "," +
                        e.MarketDataType.ToString() + "," +
                        e.Price.ToString("R") + "," +
                        e.Volume.ToString());

                    tobRowsWritten++;
                    if (tobRowsWritten % FlushEveryNEvents == 0) tobWriter.Flush();

                    if (tobRowsWritten >= MaxRowsPerStreamFile && !tobCapReached)
                    {
                        tobCapReached = true;
                        tobWriter.Flush();
                        WriteEvent("CAP_REACHED", "topofbook stream hit MaxRowsPerStreamFile=" + MaxRowsPerStreamFile + "; further top-of-book rows are dropped for this run.");
                    }
                }
                catch (Exception ex)
                {
                    HandleFatal("OnMarketData", ex);
                }
            }
        }

        protected override void OnConnectionStatusUpdate(ConnectionStatusEventArgs e)
        {
            if (fatalError) return;
            try
            {
                string typeName = "UNKNOWN";
                try { if (e.Connection != null) typeName = e.Connection.GetType().Name; } catch (Exception) { }

                string detail = "Connection=" + typeName +
                    " Status:" + e.PreviousStatus.ToString() + "->" + e.Status.ToString() +
                    " PriceStatus:" + e.PreviousPriceStatus.ToString() + "->" + e.PriceStatus.ToString() +
                    " Error=" + e.Error.ToString() +
                    " NativeError=" + (e.NativeError ?? "");

                WriteEvent("CONNECTION_STATUS", detail);
            }
            catch (Exception ex)
            {
                HandleFatal("OnConnectionStatusUpdate", ex);
            }
        }

        protected override void OnBarUpdate()
        {
            if (State != State.Realtime || fatalError) return;
            barsSinceHeartbeat++;
            if (barsSinceHeartbeat < HeartbeatEveryNBars) return;
            barsSinceHeartbeat = 0;
            WriteHeartbeat();
        }

        private void WriteHeartbeat()
        {
            lock (sync)
            {
                try
                {
                    if (heartbeatWriter == null) return;
                    heartbeatSeq++;
                    DateTime nowUtc = DateTime.UtcNow;
                    double secSinceDepth = lastDepthRecordedUtc == DateTime.MinValue ? -1.0 : (nowUtc - lastDepthRecordedUtc).TotalSeconds;
                    double secSinceTob = lastTobRecordedUtc == DateTime.MinValue ? -1.0 : (nowUtc - lastTobRecordedUtc).TotalSeconds;

                    heartbeatWriter.WriteLine(
                        runId + "," +
                        heartbeatSeq.ToString() + "," +
                        nowUtc.ToString("yyyy-MM-dd HH:mm:ss.fffffff") + "Z," +
                        Time[0].ToString("yyyy-MM-dd HH:mm:ss.fffffff") + "," +
                        depthRowsWritten.ToString() + "," +
                        tobRowsWritten.ToString() + "," +
                        secSinceDepth.ToString("F1") + "," +
                        secSinceTob.ToString("F1"));
                    heartbeatWriter.Flush();
                }
                catch (Exception ex)
                {
                    HandleFatal("WriteHeartbeat", ex);
                }
            }
        }

        private void WriteEvent(string category, string detail)
        {
            lock (sync)
            {
                try
                {
                    if (eventsWriter == null) return;
                    eventsSeq++;
                    eventsWriter.WriteLine(
                        (runId ?? "") + "," +
                        eventsSeq.ToString() + "," +
                        DateTime.UtcNow.ToString("yyyy-MM-dd HH:mm:ss.fffffff") + "Z," +
                        Csv(category) + "," +
                        Csv(detail));
                    eventsWriter.Flush();
                }
                catch (Exception)
                {
                    // Best-effort logging only; never let the event logger itself throw upstream.
                }
            }
        }

        private void HandleFatal(string where, Exception ex)
        {
            fatalError = true;
            TrySwallow(delegate { WriteEvent("FATAL_ERROR", where + ": " + ex.Message); });
            TrySwallow(delegate { File.AppendAllText(Path.Combine(baseDir ?? ".", "dom01_collector_fatal_errors.txt"), DateTime.UtcNow.ToString("o") + " " + where + ": " + ex + Environment.NewLine); });
        }

        private void WriteManifest(bool final)
        {
            try
            {
                StringBuilder sb = new StringBuilder();
                sb.Append("{\n");
                sb.Append("  \"SchemaVersion\": \"" + SchemaVersion + "\",\n");
                sb.Append("  \"CollectorClass\": \"Dom01DepthRecorder_v1\",\n");
                sb.Append("  \"RunId\": \"" + runId + "\",\n");
                sb.Append("  \"StartUtc\": \"" + startUtc.ToString("yyyy-MM-ddTHH:mm:ss.fffffffZ") + "\",\n");
                sb.Append("  \"EndUtc\": " + (final ? ("\"" + DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ss.fffffffZ") + "\"") : "null") + ",\n");
                sb.Append("  \"Tag\": \"" + JsonStr(Tag) + "\",\n");
                sb.Append("  \"InstrumentFullName\": \"" + JsonStr(SafeStr(delegate { return Instrument.FullName; })) + "\",\n");
                sb.Append("  \"InstrumentRoot\": \"" + JsonStr(SafeStr(delegate { return Instrument.MasterInstrument.Name; })) + "\",\n");
                sb.Append("  \"ContractExpiry\": \"" + JsonStr(SafeStr(delegate { return Instrument.Expiry == DateTime.MinValue ? "N/A" : Instrument.Expiry.ToString("yyyy-MM-dd"); })) + "\",\n");
                sb.Append("  \"Exchange\": \"" + JsonStr(SafeStr(delegate { return Instrument.Exchange.ToString(); })) + "\",\n");
                sb.Append("  \"TradingHoursTemplateName\": \"" + JsonStr(SafeStr(delegate { return this.TradingHours != null ? this.TradingHours.Name : "N/A"; })) + "\",\n");
                sb.Append("  \"TradingHoursTimeZoneDisplayName\": \"" + JsonStr(SafeStr(delegate { return this.TradingHours != null ? this.TradingHours.TimeZoneDisplayName : "N/A"; })) + "\",\n");
                sb.Append("  \"MachineLocalTimeZoneId\": \"" + JsonStr(TimeZoneInfo.Local.Id) + "\",\n");
                sb.Append("  \"DataConnectionTypeName\": \"" + JsonStr(connTypeName) + "\",\n");
                sb.Append("  \"DataConnectionOptionsTypeName\": \"" + JsonStr(connOptionsTypeName) + "\",\n");
                sb.Append("  \"DataConnectionDisableL2Data\": \"" + JsonStr(connDisableL2Data) + "\",\n");
                sb.Append("  \"DataConnectionStatusAtInit\": \"" + JsonStr(connStatusAtInit) + "\",\n");
                sb.Append("  \"DepthLevelClass\": \"MBP (price-level aggregated depth: side + Position/level + price + size + Add/Update/Remove operation). NOT MBO -- no per-order IDs, no order-level granularity, no queue priority. This is the full field set exposed by NinjaTrader.Data.MarketDepthEventArgs; confirmed by reflection against this NT8 install, not assumed.\",\n");
                sb.Append("  \"SequenceFieldNote\": \"SeqLocal columns are collector-generated monotonic counters per output stream, not an exchange-assigned match/sequence number -- the NinjaScript API exposes no such field.\",\n");
                sb.Append("  \"EventTimeSemanticsNote\": \"EventTime is e.Time exactly as delivered by NinjaScript, unmodified; EventTimeKind records DateTime.Kind for diagnosis. Not independently verified against a live feed this pass -- verify on first live/replay attach by comparing EventTime to RecordedUtc.\",\n");
                sb.Append("  \"KnownLimitations\": [\n");
                sb.Append("    \"MBP depth only, not MBO -- no per-order granularity.\",\n");
                sb.Append("    \"No queue priority -- not exposed by the standard NinjaScript OnMarketDepth API.\",\n");
                sb.Append("    \"SeqLocal is collector-local, not an exchange sequence number.\",\n");
                sb.Append("    \"Depth entitlement on the connected data feed is unconfirmed (DOM01 finding); DataConnectionDisableL2Data above is a direct, queryable signal, not a substitute for a real License Manager / data-plan check.\",\n");
                sb.Append("    \"EventTime timezone semantics for the live callback path are provisional, not independently verified this pass.\",\n");
                sb.Append("    \"No genuine Market Replay depth files exist locally (DOM01/DATA02); this collector only produces meaningful output when attached to a connection that actually serves live or replay-simulated Level II depth.\"\n");
                sb.Append("  ]");
                if (final)
                {
                    sb.Append(",\n  \"FinalCounts\": { \"DepthRows\": " + depthRowsWritten + ", \"TopOfBookRows\": " + tobRowsWritten + ", \"EventsRows\": " + eventsSeq + ", \"HeartbeatRows\": " + heartbeatSeq + " },\n");
                    sb.Append("  \"CapReached\": { \"Depth\": " + depthCapReached.ToString().ToLowerInvariant() + ", \"TopOfBook\": " + tobCapReached.ToString().ToLowerInvariant() + " },\n");
                    sb.Append("  \"FatalErrorOccurred\": " + fatalError.ToString().ToLowerInvariant() + ",\n");
                    sb.Append("  \"FileChecksumsSha256\": {\n");
                    sb.Append("    \"depth.csv\": \"" + Sha256OfFile(depthPath) + "\",\n");
                    sb.Append("    \"topofbook.csv\": \"" + Sha256OfFile(tobPath) + "\",\n");
                    sb.Append("    \"events.csv\": \"" + Sha256OfFile(eventsPath) + "\",\n");
                    sb.Append("    \"heartbeat.csv\": \"" + Sha256OfFile(heartbeatPath) + "\"\n");
                    sb.Append("  }\n");
                }
                else
                {
                    sb.Append("\n");
                }
                sb.Append("}\n");

                File.WriteAllText(manifestPath, sb.ToString());
            }
            catch (Exception ex)
            {
                TrySwallow(delegate { WriteEvent("WARN", "WriteManifest(final=" + final + ") failed: " + ex.Message); });
            }
        }

        private void FinalizeRun()
        {
            lock (sync)
            {
                try
                {
                    WriteEvent("STATE_TRANSITION", "Entered State.Terminated. Flushing and closing all streams.");

                    if (depthWriter != null) { depthWriter.Flush(); depthWriter.Close(); depthWriter = null; }
                    if (tobWriter != null) { tobWriter.Flush(); tobWriter.Close(); tobWriter = null; }
                    if (heartbeatWriter != null) { heartbeatWriter.Flush(); heartbeatWriter.Close(); heartbeatWriter = null; }

                    // Write the final manifest (with checksums) before closing the events stream,
                    // then close events last so the manifest write itself can still log warnings.
                    if (!string.IsNullOrEmpty(manifestPath)) WriteManifest(true);

                    if (eventsWriter != null) { eventsWriter.Flush(); eventsWriter.Close(); eventsWriter = null; }
                }
                catch (Exception ex)
                {
                    TrySwallow(delegate { File.AppendAllText(Path.Combine(baseDir ?? ".", "dom01_collector_fatal_errors.txt"), DateTime.UtcNow.ToString("o") + " FinalizeRun: " + ex + Environment.NewLine); });
                }
            }
        }

        private string Sha256OfFile(string path)
        {
            try
            {
                if (!File.Exists(path)) return "MISSING";
                using (SHA256 sha = SHA256.Create())
                using (FileStream fs = File.OpenRead(path))
                {
                    byte[] hash = sha.ComputeHash(fs);
                    return BitConverter.ToString(hash).Replace("-", "").ToLowerInvariant();
                }
            }
            catch (Exception ex)
            {
                return "ERROR:" + ex.Message;
            }
        }

        private static string Csv(string s)
        {
            if (string.IsNullOrEmpty(s)) return "";
            if (s.IndexOf(',') >= 0 || s.IndexOf('"') >= 0 || s.IndexOf('\n') >= 0 || s.IndexOf('\r') >= 0)
                return "\"" + s.Replace("\"", "\"\"") + "\"";
            return s;
        }

        private static string JsonStr(string s)
        {
            if (s == null) return "";
            return s.Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\r", "").Replace("\n", " ");
        }

        private static string SafeStr(Func<string> f)
        {
            try { return f(); }
            catch (Exception) { return "N/A"; }
        }

        private static void TrySwallow(Action a)
        {
            try { a(); }
            catch (Exception) { }
        }
    }
}
