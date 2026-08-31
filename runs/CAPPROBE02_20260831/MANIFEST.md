# CAPPROBE02 — FROZEN DATASET MANIFEST (market internals, 1-minute)

Spec preregistered and committed `e04286a` **before** any provider call in this lane.
**No economic statistic was computed. No P&L. No strategy touched. $0 spent.**

Companion machine-readable artefact: `manifest.json`.

---

## 0. Headline

| | before this lane | after |
|---|---:|---:|
| `^TICK` payload sessions | 1,963¹ | **3,402** |
| `^TRIN` payload sessions | 1,179¹ | **3,400** |
| `^TRIN` pre-2022 sessions | **3** | **2,254** |
| joinable `^TICK ∩ ^TRIN` pre-2022 | ~0 | **2,250** |

¹ counted under the *inherited* `<=32 B` rule, which this lane found wrong — see §2. The true
pre-lane payload counts were lower still.

**`^TRIN` went from 3 pre-2022 sessions to 2,254 (99.43 % of the trading calendar) for $0.**

---

## 1. Per-symbol manifest

### `^TICK` — NYSE cumulative tick
| field | value |
|---|---|
| store | `C:\Users\Yuke Zhang\Documents\NinjaTrader 8\db\minute\^TICK` |
| provider symbol | `$TICK` (NT8 resolves `^TICK` → `$TICK`) |
| payload sessions | **3,402** |
| empty / non-session files | 323 |
| date min → max (payload) | **2012-12-31 → 2026-08-28** |
| median payload | 3,294 B |
| bar interval | 1 minute, END-stamped |
| session coverage | **RTH only**, first bar 09:31, last bar 16:00 ET (~390 bars/session) |
| evidence status | 2013–2021 **PRE-FROZEN / UNSPENT**; 2022-07→2026-07-31 **DISCOVERY_CONSUMED**; ≥2026-08-01 **SEALED/VIRGIN** (4 files, counted not read) |

### `^TRIN` — NYSE short-term trading index (Arms)
| field | value |
|---|---|
| store | `…\db\minute\^TRIN` |
| provider symbol | `$TRIN` |
| payload sessions | **3,400** |
| empty / non-session files | 312 |
| date min → max (payload) | **2013-01-02 → 2026-07-31** |
| median payload | 2,406 B |
| session coverage | RTH only, 09:31 → 16:00 ET |
| evidence status | as `^TICK`; **0 files ≥2026-08-01** |

### `^VIX` — probed, NOT a fetch boundary
2022-01-03 → 2026-07-31, 1,155 payload sessions, median 4,021 B. **Pre-2022 is a genuine DATA
boundary, not a fetch boundary.** Three probes — 2013-03-13, 2019-06-12, 2021-06-15 — each returned
`count: 0` on a *real* fetch (455 / 303 / 306 ms, i.e. not cache). Unlike `^TICK`/`^TRIN`, no
backfill is available. Recorded so nobody re-probes it, and so the CAPPROBE01 result is not
over-generalised to "all internals go back to 2013".

### `^ADD` — not served at all
Store directory exists but holds **0 files**. Probes at 2019-03-13 *and* 2025-06-11 both returned
`count: 0` on real fetches (415 / 314 ms). Absent in the modern window too, so this is a
subscription/entitlement absence, not a history-depth question.

---

## 2. ⚠️ THE INHERITED EMPTY-SIGNATURE WAS WRONG — corrected before it was used

The lane was handed *"empty-residue signature is `<=32 B` against a payload median ~3,298 B — USE IT."*
Measuring it first showed the distribution is **trimodal, not bimodal**:

| band | `^TICK` | `^TRIN` | `^VIX` | what it is |
|---|---:|---:|---:|---|
| exactly 32 B | 231 | 219 | 166 | probe residue |
| **33–200 B** (36,37,40,41,43,48,49,53) | **62** | **32** | **21** | **also empty — 113/115 fall on a Saturday or Sunday** |
| 201–2,000 B | 1 | 11 | 1 | genuine **half-sessions** (13:00 closes) + 1 anomaly |
| > 2,000 B | 2,154 | 1,136 | 1,154 | full sessions |

Nothing at all sits between 200 B and 800 B. The `<=32 B` rule counts the whole 33–200 B weekend
band as payload and **inflates every coverage figure it touches**.

**FROZEN RULE FOR THIS RUN — `EMPTY <= 200 B`, `PAYLOAD > 200 B`.** All numbers here use it.

Half-session subclass (1,767–1,964 B) is real payload and is retained: 1 file in `^TICK`, **43** in
`^TRIN` — Thanksgiving-Friday, Christmas-Eve and July-3rd 13:00 closes.

---

## 3. Coverage vs the NYSE trading calendar

Denominator = actual NYSE trading days (holiday table in `gaps.py`, incl. 2018-12-05 Bush closure
and 2025-01-09 Carter day of mourning).

| year | `^TICK` | | `^TRIN` | |
|---|---:|---:|---:|---:|
| 2013 | 252/252 | 100 % | 252/252 | 100 % |
| 2014 | 243/252 | 96.4 % | 243/252 | 96.4 % |
| 2015 | 247/252 | 98.0 % | 247/252 | 98.0 % |
| 2016 | 249/252 | 98.8 % | 252/252 | 100 % |
| 2017 | 251/251 | 100 % | 251/251 | 100 % |
| 2018 | 251/251 | 100 % | 251/251 | 100 % |
| 2019 | 252/252 | 100 % | 252/252 | 100 % |
| 2020 | 254/253 | 100 %ᵃ | 254/253 | 100 %ᵃ |
| 2021 | 251/252 | 99.6 % | 252/252 | 100 % |
| **2013–2021** | **2,250/2,267** | **99.25 %** | **2,254/2,267** | **99.43 %** |

ᵃ one **non-calendar extra**: `20201018`, a **Sunday**, present in both symbols at 822 B (`^TICK`)
and 671 B (`^TRIN`) — the only files in the whole store between 200 B and 1,700 B. Anomalous;
**flagged, not silently kept**. Any consumer should drop it by calendar join, not by size.

### Genuine provider holes (a real fetch returned `count: 0`)
- **2014-03-17 → 03-27** (9 sessions)
- **2015-10-12 → 10-16** (5 sessions)

These are **identical in `^TICK` and `^TRIN`** — two symbols fetched by different requests, missing
exactly the same dates. That mutual corroboration is why they are classified as **provider-side
outages, not fetch failures.** They are not recoverable by retry.

- **2016-02-01, 02-02**: `^TICK` only (real fetch, `count: 0`); `^TRIN` *has* both.

### Not-recovered, but recoverable in principle (2 sessions, 0.09 %)
`^TICK` **2016-06-01** and **2021-04-01**. Both blocked by the NT8 cache-shadow (§4), not by absence
— `^TRIN` holds both dates, so the sessions exist upstream. ~6 retry framings were tried.

---

## 4. Acquisition method — and the trap that actually bites

The inherited warning was *"a multi-year range hits a bar cap and returns a cached tail."* True but
**understated**: a **single-year** request also truncates. Every year fetched as one call came back
as a **half-year tail** — 2014, 2016, 2019, 2021 all landed exactly Jul 1 → Dec 31 (~129 sessions
≈ 50 k bars), which is the real cap.

A second, sharper trap was found and is **not** documented anywhere in the repo:

> **THE CACHE-SHADOW.** If the calendar day immediately before `from` already has a file, NT8 serves
> the request **from cache and never contacts the provider** — returning bars that can lie *outside*
> the requested range entirely.

It is discriminable at a glance:

| | real fetch | cache-shadow |
|---|---|---|
| `clientExecMs` | **~300–2,250 ms** | **~10–50 ms** |
| returned bars | inside the requested range | last cached bar *before* it |

`clientExecMs` is a reliable, zero-cost fetch/cache discriminator and should be checked on every
acquisition call. **`limit` is NOT safe for verification** — a shadowed call still returns
plausible-looking bars. Only the on-disk file is authoritative.

**Working recipe (used for the whole `^TRIN` backfill, 18/18 chunks succeeded):** request
**half-year chunks in reverse chronological order**, newest first. Going backwards, the day before
each `from` is never yet cached, so the shadow can never trigger. Forward order fails
systematically.

---

## 5. Timestamp semantics (verify before any join)

- `GetBars` returns **UTC**, `Z`-suffixed (`2013-03-13T20:00:00.0000000Z`) — *not* ET. This differs
  from the CLAUDE.md §6 note that payload timestamps are exchange-session time; it holds for this
  tool and must be converted explicitly.
- Bars are **END-stamped** (CLAUDE.md §6). The last RTH bar is **20:00 Z in EDT / 21:00 Z in EST**,
  both = **16:00 ET**. The bar stamped 09:31 ET opens 09:30:00. **No ±1-minute shift.**
- Local `.ncd` files are named by **session date**, `YYYYMMDD.Last.ncd`.
- DST is carried by the UTC offset, so a naive UTC→ET conversion **must be instant-based**, not
  string-based — the same defect class already caught once in `shadow_runner` preflight.

## 6. ⚠️ The `volume` field is NOT zero pre-2017 — and is still not flow

`research/data_internals/MANIFEST.csv` records *"volume is 0 on every bar"*. That is true of the
**2022–2026** extract only. In the newly acquired window `volume` is frequently **~59–61**:

| probe | volume |
|---|---:|
| `$TRIN` 2013-03-13, `$TICK` 2014-02-11, `$TICK` 2016-04-29, `$TRIN` 2016-06-30 | 59–61 |
| `$TICK` 2016-12-30, 2017-06-14, 2018-06-14, `$TICK`/`$TRIN` 2019+ | 0 |

≈60 per minute ≈ one increment per second: a **feed-sampling artefact**, not market participation.
These are indices, not traded contracts. **`volume` must never be treated as flow**, and any feature
touching it would see a spurious structural break around 2017 that is a *data-format* change, not a
market regime change. The boundary was not pinned to an exact date (both values appear in 2016).

---

## 7. ⚠️ VERIFICATION OF THE INHERITED N ARITHMETIC — right number, wrong conclusion

Handed: *"joinable N ~1,147 → ~3,380 (2.95×) ⇒ MDE ×0.58. VERIFY THAT ARITHMETIC; do not inherit it."*

**At the session level it is CONFIRMED.** Measured: 1,146 modern (`^TICK ∩ ^TRIN`, 2022-01-03 →
2026-07-31) + 2,250 pre-2022 = **3,396**, ratio **2.962×**, `1/√2.962` = **×0.581**. Claim was
2.95× / ×0.58. **Accurate.**

**But the gate's `n` is not sessions.** `runs/INTERNALS_ACQUIRE_20260827/REPORT.md` line 58 sets the
bar on **n = 764 P1 scoring entries** that are inside RTH *and* on a covered session — not on 1,147
sessions. Rescaling on entries at the measured modern rate (764/1,146 = 0.667 RTH entries per
covered session) gives ≈1,499 projected pre-2022 entries, pooled n ≈ 2,263 — the same 2.962×. So
the arithmetic survives the change of unit, **but only under an unmeasured assumption**: that P1's
per-session RTH entry rate, `sd`, and mean are era-stable. Measuring that requires running P1 over
2013–2021, which is P&L work this lane is forbidden to do.

**And the gain is only realisable by pooling — which is exactly what is forbidden.**

| | n | MDE factor | gate (was 1.07× mean) | |
|---|---:|---:|---:|---|
| modern only (today) | 764 | 1.000 | **1.07×** | fails by 7 % |
| **pooled** pre-2022 + modern | 2,263 | 0.581 | 0.62× | ⛔ **ERABREAK01 p=0.0011 forbids this** |
| era-stratified — modern stratum | 764 | 1.000 | **1.07×** | **STILL FAILS, unchanged** |
| era-stratified — pre-2022 stratum | ~1,499 | 0.714 | 0.76× | old regime only |

> ### The backfill does **NOT** rescue the modern gate.
> Era-stratified — the only admissible treatment under ERABREAK01 — the modern stratum's `n` is
> **still 764** and the lane **still fails by 7 %**. The ×0.58 improvement exists *only* in the
> pooled quantity, and pooling pre-2022 with modern to move a bar is precisely
> "manufacture power" as the directive names it.

**What the acquisition genuinely buys** is a separately-powered **old-regime stratum (n ≈ 1,499)**
usable as the *discovery* half of a preregistered discovery/confirmation split — real and valuable,
but a different claim from "the gate now passes."

⚠️ **The confirmation half is compromised before it starts.** 2022-07 → 2026-07-31 is
DISCOVERY_CONSUMED across ~123 waves, and that is nearly all of the modern internals window
(2022-01-03 → 2026-07-31). The only clean confirmation set is the VIRGIN window ≥2026-08-01, which
currently holds **4 `^TICK` sessions and 0 `^TRIN` sessions**. Confirmation power must **accrue
forward**; it cannot be bought.

---

## 8. ⛔ The permanent ceiling this does not touch

`^TICK` / `^TRIN` / `^VIX` are **RTH-only** — first bar 09:31, last 16:00 ET, verified across every
year in §3. P1 makes **~62–64 %** of its decisions outside RTH. Internals can never speak to roughly
two-thirds of P1's decision set. **This is a property of the strategy, not of the data, and no
acquisition at any price removes it.** This backfill raises `n` on the RTH minority only.

## 9. Evidence status and spending rules (binding)

| window | status |
|---|---|
| 2013-01-02 → 2021-12-31 | **PRE-FROZEN / UNSPENT** — admissible only era-stratified, or as the discovery half of a preregistered split. Carries family-selection debt from prior campaigns. |
| 2022-01-03 → 2026-05-30 | mostly **DISCOVERY_CONSUMED** (~123 waves from 2022-07) |
| 2026-05-31 → 2026-07-31 | **BURNED** |
| ≥ 2026-08-01 | **SEALED / VIRGIN** — 4 `^TICK` files counted by filesystem metadata only, never read |

**ACQUISITION IS FREE. SPENDING IT IS A SEPARATE OWNER DECISION.** Nothing here licenses a
statistic; §7 argues the most obvious intended use is not admissible as framed.

## 10. Reproduction

`gaps.py` (calendar diff) and `manifest.py` (manifest builder) — filesystem metadata only, no `.ncd`
parsed, nothing ≥2026-08-01 read. Both in this run directory.
