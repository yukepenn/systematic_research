# DATA03 — Historical Market Replay Inventory: OPEN, acquisition planning stage

**Classification: INFRASTRUCTURE / DATA ACQUISITION. Zero alpha budget.** No price, markout,
return, or price-response content has been read from any `.nrd` file. This report documents what
was acquired, how it's classified, what batch-acquisition options exist, and an urgent storage
finding — nothing here is a research result.

## 1. Proof-day acquisition: CONFIRMED

`db\replay\NQ 09-26\20260715.nrd` — 160,994,081 bytes, sha256
`ec10c5c6837907a313712523ba3cb5a97baec65cc64c26467a9fe3d915f2ad`. Structurally: 2,012,426 fixed
80-byte records (byte-stride detection only, no field-level content decoding attempted or
needed).

**Classification: `GENUINE_NT8_MARKET_REPLAY_L1_PLUS_L2`, acquisition proof = PASS.** Basis,
stated plainly: (1) acquired via NT8's official, documented `Historical Data -> Get Market Replay
data` workflow — the only download path that exists; (2) per the owner, NinjaTrader's own product
documentation states Market Replay files store the synchronized Level I + Level II event sequence
together in one file, to keep them synchronized. This session's own local structural inspection
(record count, file location/format distinct from the `.ncd` L1 tick store) is **consistent with**
this classification but does **not**, on its own, independently prove L2 content — that
distinction is disclosed here for the record, not because the classification is in doubt; the
owner's instruction not to pursue further `.nrd` reverse-engineering is being followed.

## 2. Server-side retention

NinjaTrader's own support-forum threads (not the official help-guide page, which doesn't state a
number) report Market Replay is available for **"up to 90 days"** back from the present.
~90 days back from 2026-08-11 is approximately **2026-05-13** — close to, not identical to, the
suggested probe floor of 2026-05-15. Treated as a planning prior only, per instruction; the actual
boundary is established by the sparse backward probe in `acquisition_plan.yaml`, not assumed.
Sources: [NinjaTrader Support Forum — "Download playback data for a date range?"](https://discourse.ninjatrader.com/forum/ninjatrader-8/platform-technical-support-aa/1163409-download-playback-data-for-a-date-range).

## 3. Batch-acquisition mechanism — researched, NOTHING installed

No MCP/API path exists (confirmed against the full crosstrade tool surface). No general desktop-
automation library is installed in this environment (checked: no `pywinauto`, `uiautomation`,
AutoHotkey). NT8 itself only supports one instrument/date per manual download — confirmed both by
the owner's direct experience and NinjaTrader's own support forum.

### Option A — third-party AddOn (researched, not installed)

| Candidate | Mechanism (as stated) | Source inspectable? | Cost | Notes |
|---|---|---|---|---|
| **AT Market Replay Data Pro** ("NT8 AddOn to download Market Replay by date range"), by ActualTrading, posted on NinjaTrader's own Community/Desktop-SDK forum | Developer states directly: *"It simply automates and organizes the official NinjaTrader Market Replay download workflow"* — does not claim to use undocumented endpoints or extend server availability | **No** — closed-source, sold as ready-to-use | Paid, price not disclosed in-thread | Multi-instrument queueing, date-range prep, weekend-skip, already-downloaded detection, progress tracking. [Source thread](https://discourse.ninjatrader.com/t/nt8-addon-to-download-market-replay-by-date-range/6637). One user caution noted: don't hand-copy tick files across contract folders — not relevant to this workflow. |
| **Essential AddOn Suite — Replay (Playback) Data Downloader and Manager** | Not explicitly disclosed (UI-automation vs. internal API unstated in vendor docs) | **No** — commercial, undisclosed | Paid (free trial mentioned) | [Vendor page](https://essentialaddonsuite.wiki.zoho.com/Replay-Playback-Data-Downloader-and-Manager.html). Mechanism ambiguity is a real gap against the owner's "official workflow only" constraint. |
| MRDD (The Intentional Trader), MZpack, MarketReplay.NET | Not independently verified this pass | Unknown | Paid (implied) | Mentioned in search results; not fetched/verified in depth given the above two already surface the key trade-off (closed-source either way). |

**Assessment**: AT Market Replay Data Pro is the strongest Option-A candidate — narrowly scoped
(only automates the same download workflow already used manually), hosted on NinjaTrader's own
community forum, and explicit that it doesn't touch anything beyond the official mechanism. Its
real limitation against the owner's own criteria is that **no candidate found has inspectable
source** — "whether it merely automates official replay downloads" rests on the vendor's stated
claim, not independent verification, for all of them. **Not installed.** Owner approval required
before any install, per instruction, regardless of which candidate.

### Option B — owner-reviewed/executed UI-automation script

No control-ID/automation-tree information is available for NT8's actual `Get Market Replay data`
dialog in this environment (no way to inspect the live window remotely). Any `pywinauto` script
written now would be a template requiring the owner's own refinement against their real window,
not a ready-to-run script — flagged honestly rather than presented as more finished than it is.
Not started; will build only if the owner picks this path over Option A or C.

### Option C — manual, owner-clicked (current default / fallback)

Zero new risk, zero new dependency. With the (draft, TBD) contract map below, total remaining
click count looks like roughly 35-45 dates, not 50-80 — narrower than originally estimated once
the ~90-day retention prior and the existing L1-overlap evidence are factored in.

## 4. Acquisition plan (living document: `acquisition_plan.yaml`)

Sparse backward probe (Step 3), 1 of 6 already resolved by the proof day:

| Date | Instrument | Status |
|---|---|---|
| 2026-07-31 | NQU6 | not yet probed |
| 2026-07-15 | NQU6 | **ACQUIRED** |
| 2026-07-01 | NQU6 | not yet probed |
| 2026-06-15 | NQU6 | not yet probed |
| 2026-06-01 | NQM6 | not yet probed |
| 2026-05-15 | NQM6 | not yet probed |

Contract map for RAW acquisition (draft, explicitly NOT a scientific roll-date decision):
existing local L1 tick data already shows NQU6 beginning 2026-06-08 while NQM6 continues through
2026-06-12 — reuse that as a starting overlap bracket to widen once the probe establishes the true
earliest date. Final bracket intentionally left open pending probe results.

## 5. URGENT — storage finding on the drive that actually matters

`db/replay` lives under `C:\Users\Yuke Zhang\Documents\NinjaTrader 8\`, i.e. **the C: drive**, not
D: (where this repo and DOM01's live collector output live — D: remains healthy at ~172.7 GiB
free, unaffected). **C: free space dropped fast during this session and is still dropping:
~34.4 GiB -> 31.6 GiB -> 28.0 GiB -> 26.0 GiB -> 25.3 GiB -> 22.2 GiB across roughly the last
30-40 minutes** (last reading: this run's own manifest generation, `out/manifest.json`).
That's now within 7 GiB of this script's own `--fail-free-gib` floor. `db\tick` + `db\replay`
together total only ~10 GB combined (confirmed directly) — nowhere near enough to explain this
drop, so **regular Historical Data tick downloading is the leading suspect** for at least part of
it, but not confirmed. A bounded top-level scan of `AppData` (131 GB total, `AppData\Local` alone
90 GB: Google/Chrome 14 GB, Microsoft 13 GB, NVIDIA 12 GB, Windows Packages 11 GB, ...) found no
single obvious smoking gun in a reasonable search — that search was intentionally bounded and
stopped rather than becoming an unrelated full-disk audit.

**This is a real, live risk independent of the Market Replay campaign** — C: is the Windows
system drive. At ~150 MiB/session, the replay campaign itself (even acquiring all ~40-55 candidate
sessions) would only need ~6-8 GB, which fits inside 25 GiB today — but if whatever is currently
draining C: continues at the observed rate, that's a different, more urgent problem than replay
storage specifically.

**Recommend**: before authorizing any batch acquisition, check Task Manager / Resource Monitor
for whatever is actively writing to C: right now (fastest way to catch a live process), and
consider whether NT8's Historical Data downloads for L1 tick data (still apparently in progress
per the earlier DOM01/DATA02 re-verification) should be paused until this resolves.

## 6. What has NOT happened

No batch download triggered. No AddOn installed. No UI-automation script run. No `.nrd` content
read beyond structural byte-stride counting. No Playback connection touched — DOM01's live
collector remains untouched (re-verified via `dom01_qc_monitor.py`, unchanged state). No mixing
of this substrate with `DOM01_PROSPECTIVE_PROTOCOL.md`'s governance — that reconciliation is
explicitly deferred to a later step per the owner's own instruction.
