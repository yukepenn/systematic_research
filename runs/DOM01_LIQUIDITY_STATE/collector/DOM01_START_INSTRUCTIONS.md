# DOM01 collector — owner start steps (do these in NinjaTrader 8's UI)

**Status right now: built and compile-verified, but NOT collecting anything.** The recorder file
is already on disk in NT8's NinjaScript folder. It has not been rebuilt through NT8's own native
compiler, has not been attached to any chart, and is not connected to anything. Nothing will start
collecting until you do the 5 steps below. None of these steps places a trade, touches an account,
or changes a connection's credentials.

Estimated time: under 5 minutes, plus however long it takes you to confirm your Level II
entitlement in step 2.

---

### Step 1 — Rebuild the indicator inside NT8

1. Open NinjaTrader 8.
2. Menu bar → **Tools → Edit NinjaScript → Indicator...**
3. In the list, find **Dom01DepthRecorder_v1** and open it (double-click).
4. Press **F5** (or close and reopen NT8 — either one rebuilds NT8's compiled script library).
5. Look at the **Output** / **Log** window at the bottom. You should see a compile message with
   **0 errors**. (It was already tested to compile cleanly, so this should just work — if you see
   errors here, stop and don't continue to step 3; something changed since the build.)

### Step 2 — Confirm your data connection actually includes Level II / market depth

This is the one genuinely open question — the recorder can only log data your data plan actually
provides.

1. In NT8, go to **Connections → Connection Guide** (or **Connections → [your connection name] →
   Edit**, or check your data vendor's account/License Manager page — wherever your NT8 is set up
   to show your subscribed data packages).
2. Confirm that **Level II / Market Depth** (sometimes called "Order Flow+", "Market Depth Map",
   or similar) is actually included for **NQ** on your current live/data-vendor connection.
   - The only connection currently active on this machine ("Simulation") is a historical-replay
     connection that does **not** include depth — you need your live/broker data connection for
     this, not Simulation.
3. If it's not included, this is the point to stop and either enable/upgrade it with your data
   vendor, or accept that the collector will run but log an empty depth stream (it will still tell
   you this clearly — see step 5).
4. Once confirmed, make sure that connection is **Connected** (green/connected status in NT8's
   Connections panel) before continuing.

### Step 3 — Open an NQ chart on that connection

1. **File → New → Chart...** (or open an existing NQ chart).
2. Pick **NQ** (the current front-month contract) as the instrument.
3. Make sure the chart is using the **live/data-vendor connection** you confirmed in Step 2, not
   Simulation.
4. Any bar period works (1-minute is a reasonable default) — the depth logger runs independently
   of the bar period.

### Step 4 — Add the indicator to that chart

1. Right-click anywhere on the chart → **Indicators...**
2. Find **Dom01DepthRecorder_v1** in the list, select it, click **Add**.
3. Don't change any of the default settings — they're already pointed at the right output folder.
4. Click **OK**.
5. The chart pane will **not** show any new lines or plots — that's expected, this indicator only
   writes files, it doesn't draw anything.

### Step 5 — Confirm it's actually writing data

1. Within a few seconds of clicking OK in Step 4, check this folder:
   `runs/DOM01_LIQUIDITY_STATE/collector/out/`
2. You should see 5 new files starting with `dom01_` (a `_manifest.json` and four `.csv` files).
3. Open the `_manifest.json` file and check two fields:
   - `DataConnectionDisableL2Data` — if this is `true`, your connection is explicitly telling NT8
     not to send depth data (contradicts Step 2 — go back and check your data plan).
   - `DataConnectionStatusAtInit` — should say the connection is connected.
4. Watch the `_depth.csv` file for a minute or two:
   - **Rows appearing** → it's working, Level II data is flowing.
   - **Still empty, but `_heartbeat.csv` is growing** → the collector itself is alive, but your
     feed is not sending depth data — this points back to Step 2's entitlement question, not a
     bug in the recorder.

---

### If something looks wrong

- **Indicator not in the list in Step 4** → Step 1's rebuild didn't take. Repeat Step 1 and
  confirm 0 compile errors before trying again.
- **`_events.csv` shows a `FATAL_ERROR` row** → open that row's `Detail` column for the error
  text; that's the recorder's own self-reported failure reason, not a silent crash.
- **Nothing at all appears in `out/`** → confirm the chart is actually running (not paused/
  historical-only) and that the indicator was added to the correct chart/instrument.

Do not report data from this collector as usable for research until it has also passed the
completeness checks described in
`research/data_forward_sealed/DOM01/README.md` — collection starting is not the same thing as the
data being cleared for use.
