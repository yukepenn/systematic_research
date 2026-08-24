# Local Artifact Search — ninZa VWAP Flux (2026-08-24)

Directive §29 (OTR campaign #6). Question: does any ninZa VWAP Flux artifact exist on THIS
(researcher's) machine that could serve as a reconstruction oracle without purchase?
Method: plain-text and file-name/metadata search ONLY. No DLL was opened, decompiled, or
string-dumped; binary files were enumerated by name/size/timestamp only. All paths below are
on the researcher's machine — none of this is the original trader's environment.

## 1. What was searched

| Location | Method |
|---|---|
| `C:\Users\Yuke Zhang\Documents\NinjaTrader 8\` (full tree: bin/Custom incl. Indicators/Strategies/AddOns/BarsTypes, templates/, workspaces/ incl. recovery, db/, trace/, log/, cache/, tmp/, import/, export/, incoming/, ninZa.co/, strategyanalyzerlogs/, Config.xml, UI.xml, NTInstall/NTAutoUpdate logs) | case-insensitive ripgrep over text extensions (`.cs .xml .txt .log .csproj .config .json .csv .md .htm .html`); directory listings for binary artifacts (names/dates/sizes only) |
| `C:\Users\Yuke Zhang\Documents\NinjaTrader 8 Backup\` | full-tree file enumeration — **empty (0 files)** |
| `C:\Program Files\` and `C:\Program Files (x86)\` | directory scan for NinjaTrader installs — none present (user-profile install only) |
| `C:\Users\Yuke Zhang\Downloads\` | file-NAME scan for `ninza / vwap / flux / renko` |
| Repo `D:\...\systematic_research\` | grep for `VWAPFlux / VWAP_Flux / ninZaVWAP` (to separate our own notes/replicas) |

Terms searched (case-insensitive): `ninZaVWAPFlux, VWAPFlux, VWAP_Flux, "VWAP Flux", ninZa,
Signal_Trade, Signal_Trend, Signal_Cum_Delta, BidAskPrice_RealVolume, AnchorPeriod,
QuantityPerTrend, CloseThreshold, SignalSplit, HelloWin`.

## 2. Exact hits

### 2a. VWAP-Flux-specific terms — ZERO hits
`ninZaVWAPFlux, VWAPFlux, VWAP_Flux, "VWAP Flux", Signal_Trend, Signal_Cum_Delta,
BidAskPrice_RealVolume, AnchorPeriod, QuantityPerTrend, CloseThreshold, SignalSplit, HelloWin`
— **no match in any text file anywhere under the NT8 tree, the (empty) backup, or Downloads.**
No file NAME containing `vwap`/`flux` exists except stock NT8
`bin\Custom\MarketAnalyzerColumns\@VWAP.cs` (NinjaTrader's own factory column, unrelated).

### 2b. `Signal_Trade` — 179 files, ALL our own replica code (category b)
- `C:\Users\Yuke Zhang\Documents\NinjaTrader 8\bin\Custom\Strategies\SolarWaveRKReplicaV0.cs`
  — line 127: `(int)Math.Round(solarWave.Signal_Trade[0]);` — OUR campaign-#1 replica strategy
  reading the `Signal_Trade` series of the **licensed RenkoKings_SolarWaveRK** indicator.
- `...\NinjaTrader 8\strategyanalyzerlogs\@@@SolarWaveRKReplicaV0_2026_08_05..11_*.cs`
  (178 files) — Strategy Analyzer's automatic per-run snapshots of that same file. Not vendor code.

Interpretation: `Signal_Trade` is a ninZa-framework naming convention that RenkoKings
SolarWaveRK (distributed via ninZa packaging) also exposes. Its presence here proves the
NAMING convention is shared across ninZa-packaged products; it is NOT a VWAP Flux artifact.

### 2c. `ninZa` — 282 occurrences in 46 files, all the RenkoKings dependency set (category a)
Every occurrence resolves to the six support assemblies that ship WITH the licensed
RenkoKings SolarWaveRK package; none is VWAP Flux:
- `Config.xml` lines 279–284: vendor-assembly registration of `NinZaResources_NT8.dll,
  NinZaATR_NT8.dll, NinZaHelperMFI_NT8.dll, NinZaHelperRSI_NT8.dll, NinZaHelperSMMA_NT8.dll,
  NinZaHelperStochastic_NT8.dll` (line 286 = RenkoKings_SolarWaveRK_NT8.dll).
- `bin\Custom\NinjaTrader.Custom.csproj` lines 57–79 + 413–419: the same 6 ninZa references +
  RenkoKings, and their generated wrapper `.cs` includes.
- Every session log `log\log.2026*.txt` / `trace\trace.2026*.txt` (2026-08-05 → 2026-08-23):
  exactly the same 6 lines per session, e.g. `Vendor assembly 'NinZaATR_NT8' version='1.0.0.1'
  loaded.` — **no other ninZa assembly was ever loaded in any recorded session.**
- `UI.xml` lines 92–98 and `workspaces\recovery\Default Yuke-2026-08-05-21-18-01.xml`
  lines 1177–1231: chart instances of the `ninZaResources` license/resource indicator only.
- `bin\Custom\NinZa*_NT8.cs` (6 files): NT8-generated public wrapper sources (plain text,
  lawful to read) — constructors expose ATR/MFI/RSI/SMMA/Stochastic helpers and the
  parameterless `ninZaResources()`; no Signal_* series, no VWAP anything.

### 2d. Binary inventory (file names + timestamps ONLY; nothing opened)
`bin\Custom` vendor DLLs: `NinZaATR_NT8.dll, NinZaHelperMFI_NT8.dll, NinZaHelperRSI_NT8.dll,
NinZaHelperSMMA_NT8.dll, NinZaHelperStochastic_NT8.dll` (all 2025-03-21),
`RenkoKings_SolarWaveRK_NT8.dll` (2025-03-22), `NinZaResources_NT8.dll` (2026-07-23),
`CrossTrade_AddOn_v1.13.9.dll` (2026-08-04), plus license-state files
`NinZaResources_Data.dat` / `NinZaResources_Time.dat` (2026-08-16) and
`ninZa.co\ninZaResources\Whogo.dll` (64 bytes, 2026-08-16 — ninZa licensing marker).
`cache\*.Reflection.dat` names mirror exactly the same 7 vendor assemblies — no VWAPFlux was
ever reflected/compiled on this machine.
`NinjaTrader.Vendor.cs` (plain text): wraps only RenkoKings_SolarWaveRK and NinjaTrader's own
OrderFlowVWAP (NT Lifetime Order Flow suite — unrelated to ninZa VWAP Flux).
`Downloads`: `NinZaResources_NT8.zip` (2026-08-05), `RenkoKings_SolarWaveRK_NT8.zip`
(2026-08-05), `RenkoKings_SolarWaveRK-TraderManual.pdf` — no VWAP Flux package or trial.
`templates\Indicator\`: only `RenkoKings_SolarWaveRK` presets (MajorTrend/MinorTrend, 2025-03-21).
`import\ / export\ / incoming\`: empty.

### 2e. Our own custom sources present (category b, for completeness)
`bin\Custom\Strategies\`: SolarWaveRKReplicaV0, SolarWaveSMMaster_v4/_Canonical_v1,
SolarWaveOneContractNQ_v5/_v6_R2CONFIRM/_B1_v1/_Canonical_v1, SolarWaveOneContractMNQ_v5/_B1_v1/
_Canonical_v1, SWScalpTickExport_v3, W18CompileTrigger.
`bin\Custom\Indicators\Dom01DepthRecorder_v1.cs`; `AddOns\McpSandbox\*.dll` (our compiled
sandbox strategies). All Solar/Renko-related, none VWAP-Flux-related.
Repo-side, the only `VWAPFlux` text hits are our own forensics notes
(`vendor_forensics\PUBLIC_SOURCE_LEDGER.md`, `PURCHASE_GATE.md`).

## 3. Conclusion

**Direct ninZa VWAP Flux component evidence: NOT FOUND.**
- No VWAP Flux DLL, wrapper .cs, trial package, import zip, template, workspace reference,
  compile record, reflection cache entry, or assembly-load log line exists anywhere on this
  machine. Session logs covering the entire install lifetime (2026-08-05 → 2026-08-23) show
  only the six RenkoKings-bundled ninZa support assemblies ever loading.
- Every ninZa artifact present is (a) vendor-origin support machinery bundled with the
  LICENSED RenkoKings SolarWaveRK package; every `Signal_Trade` hit is (b) our own replica
  code reading the RenkoKings indicator.

**Local oracle path short of purchase: NONE.** There is no dormant trial or leftover component
that could be lawfully executed as a VWAP Flux oracle. The only locally verifiable fact useful
to reconstruction is indirect: the shared ninZa packaging convention (`Signal_Trade` series
naming, `ninZaResources` licensing companion, `*_NT8` wrapper pattern) observed on the
RenkoKings product, which supports naming/structure inferences about VWAP Flux but provides no
numerical ground truth. Any output-level oracle therefore remains gated on
`vendor_forensics\PURCHASE_GATE.md` (owner decision), or on non-local evidence (screenshots,
public documentation) already tracked in `PUBLIC_SOURCE_LEDGER.md`.

*Search executed 2026-08-24; read-only; no NT8 file was modified; no binary content was read.*
