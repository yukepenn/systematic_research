# V1d — CLOSURE: late-session entries

**Run:** `runs/W17_C4_COMPLIANCE` · **Item:** V1d · **Date:** 2026-08-09
**Script:** `runs/W17_C4_COMPLIANCE/src/v1d_late_entries.py`
**Full numeric output:** `runs/W17_C4_COMPLIANCE/out/v1d_report.txt`
**Data products:** `out/v1d_census.csv`, `out/v1d_signal_by_tod.csv`, `out/v1d_session_calendar.csv`

**Dev window:** 2022-01-03 .. 2026-05-29, 1,139 sessions. Nothing after 2026-05-29 was read.
No 2006-2021 data was used anywhere in this item.

---

## VERDICT

**V1d = NOT-A-PROBLEM. No `no_new_entry_after` parameter is to be built.** Two independent
reasons, both quantitative:

1. **The parameter already exists.** Both products already carry a coded late-session entry
   rule — Product B's `entryBlocked = (hm >= 163000 && hm <= 180000)` and Product A's
   16:30–18:00 no-open / no-increase / no-reversal clamp — plus a stronger forced-flat at
   16:39. `no_new_entry_after` is not a gap to be filled; it is an existing constant.
   W17's already-frozen **C2** converts it from a hardcoded 16:30 to `sessionEnd − 30 min`,
   which is the only change the evidence supports and it is already specified.

2. **For Product B the rule is nearly inert, because the underlying process does not generate
   late entries.** Removing the 16:30 block entirely adds **3 entries across 1,139 sessions**
   (1,976 → 1,979, +0.15%). Removing the block *and* the 16:39 forced-flat adds **6**
   (+0.30%). An unprotected Product B would open a position inside the final 20 minutes on
   **3 of 1,139 sessions (0.26%)**. There is no distribution here to fit a cutoff to, and
   nothing for a cutoff to remove.

**But the verdict is object-specific, and the contrary half must not be buried:**

3. **For Product A the existing clamp is NOT inert — it is doing real work.** Removing it
   produces **68 additional risk-increasing events**, of which **31 fall within 15 minutes**
   and **38 within 20 minutes** of a session close. Product A has no entry hysteresis, so it
   behaves differently from Product B and the phrase "the problem does not occur" is **false
   for Product A**. The correct statement for Product A is: *the problem is fully suppressed
   by a rule that already exists*, and W17 C2 extends that suppression to the 43 early closes
   where it currently fails.

---

## 1. What Wave 16 got right, and what it got wrong

Wave 16 measured entries in the final N minutes before a **hardcoded 17:00** close and
deferred the item as "too thin to fit a cutoff".

**Right (numerically):** for both Product B objects the session-aware census is *identical*
to the naive one at every N (delta = 0, 0, 0, 0, 0, 0, 0). W16's Product B numbers were not
wrong.

**Wrong (three ways):**

- **Wrong by luck, not by method.** The two censuses agree only because Product B happened to
  hold no position near any of the 43 early closes. That zero is **not statistically
  distinguishable from chance** (§5 below): expected 2.90 (NQ) / 1.60 (MNQ) under a
  clock-matched hazard, observed 0, P(0 | Poisson) = 0.055 / 0.201. The method was unsafe even
  though the answer survived.
- **Wrong for Product A.** Product A's *only* sub-20-minute events in the entire dev window
  — 3 within 15 min, 4 within 20 min, plus 2 stamped exactly at the close — are **all on
  early-close sessions** and are **completely invisible** to a 17:00-anchored measurement.
- **Wrong in framing.** "n ≤ 17 across 1,139 sessions is too thin to fit" treats a near-zero
  count as a sampling deficiency. It is a statement about the generating process, and the
  generating process is measurable (§4).

---

## 2. Session calendar — DIRECT

Derived from `mnq_3m_raw.csv`'s `fbos` first-bar-of-session flag (519,869 bars → 1,139
sessions), cross-checked against the NQ signal series' `IsLastBarOfSession` flag in
`smm_v2_bars.csv`.

| session close (ET) | count |
|---|---:|
| 17:00 (normal) | 1,095 |
| 13:00 | 31 |
| 13:15 | 9 |
| 09:15 (Good Friday) | 2 |
| 09:30 (2025-01-09 Day of Mourning) | 1 |
| 16:57 (**data end 2026-05-29, not an early close**) | 1 |

**43 early closes** — exactly matching the count already established in `spec.yaml` §V1e.

**Two data-quality items surfaced here that are not in the spec (NEW, flagged):**

- **2023-04-05:** the NQ *signal* series has a gap (bars jump 14:03 → 20:03) and NT8 therefore
  flags a spurious "session end" at 14:03. MNQ has a full 460-bar 17:00 session that day. Not
  a real early close. The MNQ-derived calendar is used as truth.
- **2024-04-21 (Sunday):** the NQ signal series has bars from 18:03 that the MNQ execution
  series lacks (MNQ's `fbos` for that session is at 18:27). These are the same 8 bars where
  `phys[i+1] != tgt_ops[i]` (8 of 518,574 within-session pairs; ledger fidelity 99.998%).
  They produce 6 spurious "risk-increase at −2,950 minutes" rows and are excluded as an
  artifact wherever they appear.

---

## 3. Session-aware late-entry census — DIRECT

Counts are of entries whose NT8 execution stamp falls within N minutes of **that session's own
close**. Convention: the stamp is the *close* of the bar the market order filled on;
`Calculate.OnBarClose` means the decision bar and the economic fill are both 3 minutes earlier
(so add 3 minutes to every "minutes before close" figure for true exposure).

### Product B — BEST_ONE_NQ (1,975 entries)

| N (min before that session's close) | 5 | 10 | 15 | 20 | 30 | 45 | 60 |
|---|---:|---:|---:|---:|---:|---:|---:|
| session-aware count | 0 | 0 | 0 | 0 | **3** | **17** | **152** |
| of which on early-close sessions | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| W16 naive-17:00 count | 0 | 0 | 0 | 0 | 3 | 17 | 152 |
| % of 1,139 sessions | 0 | 0 | 0 | 0 | 0.26 | 1.49 | 13.3 |

### Product B — BEST_ONE_MNQ (1,561 entries)

| N | 5 | 10 | 15 | 20 | 30 | 45 | 60 |
|---|---:|---:|---:|---:|---:|---:|---:|
| session-aware count | 0 | 0 | 0 | 0 | **1** | **6** | **98** |
| of which on early-close sessions | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| W16 naive-17:00 count | 0 | 0 | 0 | 0 | 1 | 6 | 98 |

> **MNQ caveat (required, §4 of the task).** `SolarWaveOneContractMNQ_Final` has the confirmed
> KNOWN_ERRORS #7 arrangement defect: it never submits a voluntary **exit** order. That defect
> is on the exit path only — `EnterLong`/`EnterShort` are reached normally, and the 16:30 entry
> block demonstrably works on it (last entry stamp 16:30 = a 16:27 decision, identical to NQ).
> **The MNQ entry timestamps used above are therefore valid evidence.** Everything
> *exit*-derived for MNQ — holding time, per-trade P&L, position-state occupancy, and hence
> the *number* of entries (a broken exit changes how often the object is flat and therefore
> eligible to enter) — is **not** valid and is neither computed nor used in this item. The
> 98-vs-152 gap between MNQ and NQ in the N≤60 cell is a consequence of that defect, not a
> signal difference, and must not be read as one.

### Product A — SolarWaveSMMaster_v2 (scaling allocator, MNQ execution)

Product A has no single "entry"; it re-targets a position in [−13, +13] every bar. Three
risk-increasing event types are counted: `open` (flat → non-flat, 3,478), `increase`
(|position| grows, 8,164), `reversal` (sign flip, 1,335) — **12,977 total**.

| N | 5 | 10 | 15 | 20 | 30 | 45 | 60 |
|---|---:|---:|---:|---:|---:|---:|---:|
| all risk-increasing | 0 | 0 | **3** | **4** | **14** | **101** | **621** |
| — of which **early-close sessions** | 0 | 0 | **3** | **4** | 6 | 8 | 9 |
| open | 0 | 0 | 1 | 1 | 3 | 29 | 95 |
| increase | 0 | 0 | 2 | 3 | 8 | 65 | 298 |
| reversal | 0 | 0 | 0 | 0 | 3 | 7 | 228 |

Independently cross-checked against `smm_v2_fills.csv` (25,825 executions in-window): 3
entry-side (L/S) fills within 15 min of a close, 4 within 20, 14 within 30, 101 within 45,
621 within 60 — exact agreement with the bar-ledger derivation.

**The three events inside 15 minutes, and the two stamped exactly at a close:**

| fill stamp | decision | kind | position | session close |
|---|---|---|---|---|
| 2022-11-25 13:00 | 12:57 | increase | −2 → −3 | 13:15 |
| 2023-07-03 13:00 | 12:57 | open | 0 → +1 | 13:15 |
| 2024-07-03 13:00 | 12:57 | increase | +2 → +3 | 13:15 |
| 2025-07-04 12:42 | 12:39 | increase | −1 → −2 | 13:00 |
| 2023-04-07 08:51 | 08:48 | reversal | −1 → +1 | 09:15 |
| **2022-02-21 13:00** | 12:57 | increase | −4 → **−7** | **13:00 (at the close)** |
| **2025-12-24 13:15** | 13:12 | open | 0 → −1 | **13:15 (at the close)** |

Every one is on an early-close session. The last two are at `minutes_before_close = 0` and
were **silently discarded** by Wave 16's `min_before_close > 0` filter; they are reported here
rather than left out. All seven sit inside V1e's already-counted early-close breach set
(Product A: 38 breaches) — they are not a new defect, and they are removed by C2 (§6).

**Negative result, stated plainly:** on normal 17:00 sessions Product A's latest risk increase
in the entire dev window is a fill stamped 16:30 (decision 16:27), 30 minutes before the close.
There is **no** normal-session Product A event inside 30 minutes. This corroborates
`spec.yaml` §V1-R1's "compliant on normal sessions" finding from a different direction.

---

## 4. MECHANISM — discriminating (a) from (b)

### 4.0 Method and its validation — DIRECT

Product B's allocator signal was reconstructed exactly from the 540,231-bar decision ledger:

```
m   = 1.25 iff T != 0 and sign(T) == tiltState, else 1.0
Tp  = clamp(round_away(T * m * 0.9026), ±13)          # Product B: no ShortHalf term
M_B = 0.7086*Tp + 2.83*B                              # WSolar, WBmom, frozen seq-318
```

Two fidelity checks, both required before any counterfactual is credible:

- The same arithmetic path applied with Product A's constants reproduces the ledger's own
  `Tpp` column at **1.000000** and its `tgt_raw` column at **1.000000** (540,231 bars). The
  reconstruction is bit-exact, not approximate.
- Replaying Product B's one-lot state machine over `M_B` reproduces **1,975 of 1,975** real
  `nt_trades_nq.csv` entries **timestamp-exact (100.0%)**, with 1 extra (a position still open
  at data end) and **0 missed**. The counterfactuals below are therefore run on a verified twin
  of the real object, not a model of it.

### 4.1 Hypothesis (a) — "an existing coded rule blocks them" — REFUTED for Product B, CONFIRMED for Product A

**Product B, counterfactual replay over all 1,139 sessions:**

| configuration | total entries | N≤5 | N≤10 | N≤15 | N≤20 | N≤30 | N≤45 | N≤60 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| as built (16:30 block + 16:39 flat) | 1,976 | 0 | 0 | 0 | 0 | 3 | 17 | 152 |
| **16:30 entry block REMOVED** | 1,979 | 0 | 0 | 0 | 0 | 6 | 20 | 155 |
| **both late rules REMOVED** | 1,982 | 1 | 2 | 3 | 3 | 9 | 23 | 158 |

> **The 16:30 block explains 3 entries out of 1,976 (0.152%).** Both rules together explain 6
> (0.304%). Hypothesis (a) is refuted for Product B: the rule is not what is producing the low
> count. Strip every late-session guard off Product B and it *still* only opens a position
> inside the final 20 minutes on 3 of 1,139 sessions.

**Product A, same counterfactual — the opposite answer:**

| configuration | N≤5 | N≤10 | N≤15 | N≤20 | N≤30 | N≤45 | N≤60 | total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| with the 16:30/16:39 ops clamp | 0 | 0 | 3 | 4 | 14 | 101 | 621 | 12,969 |
| **ops clamp REMOVED entirely** | **7** | **16** | **31** | **38** | **78** | **165** | **685** | 13,037 |

> **For Product A the block IS doing the work.** 31 risk increases inside 15 minutes and 7
> inside 5 minutes would occur without it. This is the "different and more interesting finding"
> the task said must not be suppressed to fit the expected verdict — and it is real, but it
> applies to Product A only.

**Why the two objects differ (INFERENCE, mechanism-level, from the two sources):** Product B
requires a *threshold crossing from a flat state* — open only at |M| ≥ 3.0, close only when M
retreats through 1.0. Product A has **no entry hysteresis at all**: `tgt_raw = round(M)` is
non-zero whenever |M| ≥ 0.5 and is re-evaluated every bar, so a one-unit move in a rounded
continuous target is enough to add risk. A near-frozen M (§4.2) still produces occasional
Product A increments; it almost never produces a Product B crossing.

### 4.2 Hypothesis (b) — "the allocator signal is quiet late in the session"

**The naive form of (b) is FALSE and must not be repeated.** The signal *level* is not low
late in the session:

| window | bars | P(\|M\| ≥ 3.0) |
|---|---:|---:|
| RTH 09:33–15:54 | 143,089 | 58.3% |
| **16:30–16:57** | **10,950** | **43.6%** |
| overnight 18:03–09:30 | 352,537 | 19.0% |

The last half hour sits **above the entry threshold on 43.6% of bars — 2.3× the overnight
rate**. Any claim that the strategy "doesn't want to trade" late in the session is wrong.

**The true form of (b): the signal is FROZEN, not small.** M is a two-term integer step
function, and in the last half hour it stops moving:

| window | bars | P(M changed) | P(T changed) | P(upcross of \|M\|≥3) | upcrossings |
|---|---:|---:|---:|---:|---:|
| RTH 09:33–15:54 | 143,089 | **14.00%** | 14.28% | **1.222%/bar** | 1,749 |
| 16:00–16:27 (entries allowed) | 10,947 | 8.02% | — | 0.758%/bar | 83 |
| 16:30–16:36 (blocked by `entryBlocked`) | 3,285 | 2.71% | — | 0.304%/bar | 10 |
| **16:39–16:57 (blocked by forced-flat)** | **7,665** | **1.71%** | **1.79%** | **0.091%/bar** | **7** |

> **7 entry-threshold upcrossings in 7,665 bars across 1,139 sessions.** A 13× collapse in
> crossing rate versus RTH. Entries need a *crossing*; a frozen signal cannot supply one. That
> is the quantitative reason the count is low, and it is a property of the process, not of the
> rule.
>
> (The 16:39–17:00 window *including* the 17:00 session-end bar shows an inflated 12.67%
> M-change rate. That bar is the engine's session reset — all 13 members are zeroed, so T → 0
> by construction on 89.4% of session-end bars. It is not signal movement and is excluded above.)

**Why M freezes — two coded causes, both measured:**

**(i) B is hard-zeroed at 15:57 and cannot revive until 09:33.** `BmomBar()` sets
`bmomPos = 0` at `hm >= 155700`, and the `hm > 160000` early return means nothing can change it
for the rest of the session or overnight. Measured: `P(B ≠ 0)` = 93.8% at 15:54, **0.0% at
15:57 and on every bar thereafter**. B carries weight 2.83 — **94.3% of the 3.0 entry
threshold** on its own — so once it is dead, an entry requires |Tp| ≥ 5 from the solar term
alone (0.7086 × 5 = 3.54), i.e. a much stronger consensus than is needed at any other time of
day.

**(ii) Tp then freezes because realized movement collapses below the member stop distances.**
Each of the 13 Solar members flips only when price travels `S_m = clamp(VolMult_m × σ, 40..1200
ticks)` from its anchor, VolMult ∈ {6, 8, …, 30}, σ = a causal 460-bar mean of |close-to-close|.

| quantity | value |
|---|---:|
| pooled σ over the dev window | 6.50 NQ points |
| implied member stop distances S | ≈ 39 to 195 points |
| mean \|3-min close change\|, RTH 09:33–15:54 | 11.01 points |
| mean \|3-min close change\|, 16:45–16:57 | **3.06–3.45 points** |
| P(T changed), RTH → 16:57 | 14.28% → **1.37%** (10.4× collapse) |

A ~3.2-point bar cannot breach a 39–195 point stop that was sized on the whole-day σ. Member
flips stop; T stops moving; with B already pinned to 0, M is frozen. *(INFERENCE on the causal
link; the σ, the bar-move series, and the T-change rate are all DIRECT.)*

### 4.3 The 16:00 spike — the one late-session cluster, fully attributed — DIRECT

105 of the 152 NQ entries in the final hour (69%) carry a single stamp: **16:00**, i.e. the
15:57 decision bar. This is not noise; it is the B-shutdown discontinuity in (i) above.

| measurement (1,095 normal sessions) | value |
|---|---:|
| B non-zero on the preceding 15:54 bar | 1,027 |
| \|M\| ≥ 3 at 15:57, actual (B zeroed) | 472 |
| \|M\| ≥ 3 at 15:57, counterfactual (B **not** zeroed) | 642 |
| crossings **created purely by the B shutdown** | **111 (10.1% of sessions)** |
| P(upcross) at the 15:57 bar vs RTH average | 0.1032 vs 0.0121 (**8.5×**) |
| **real BEST_ONE_NQ entries stamped 16:00** | **105** |
| **— of which the B shutdown created the crossing** | **102 (97%)** |

Mechanically: when the solar term opposes B, B suppresses |M| below 3.0 and the object stays
flat; zeroing B at 15:57 removes the suppression and unmasks the solar signal, producing a
deterministic once-per-day entry impulse. The count moves in both directions (642 → 472 bars
above threshold, but 111 *new* crossings), and the entry logic only reacts to the crossings.

**This is a side effect of a rule written for a different purpose, not a designed feature.**
It is recorded here as an observation about the existing objects. **It is not a trading
recommendation, and nothing here establishes that these entries are or will be profitable.**
It is logged for the OWNER_QUEUE as an open question, not acted on in this wave.

---

## 5. NULL RESULT — Product B's zero near early closes is NOT protection

On an early-close session neither hardcoded rule fires (16:30 and 16:39 never arrive), so
Product B is **completely unguarded** in the final hour of those 43 sessions. It nevertheless
took **zero** positions there. That zero is **weak evidence and must not be cited as a
mechanism**:

| object | expected in the final 60 min of the 43 early closes (clock-matched hazard from the 1,095 normal sessions) | observed | P(0 \| Poisson) |
|---|---:|---:|---:|
| BEST_ONE_NQ | 2.90 | 0 | **0.055** |
| BEST_ONE_MNQ | 1.60 | 0 | **0.201** |

43 sessions is simply too few for a ~1-in-15-session hazard to appear. Every mechanism claim in
§4 rests on the 1,095 normal sessions and on the counterfactual replays, **not** on this zero.
Had Product B been left with its hardcoded clock, the exposure on early closes would have been
real and merely unobserved — which is exactly why C2 is a compliance fix and not a P&L trade-off.

---

## 6. C2 already closes the only real hole — DIRECT

W17's frozen C2 replaces the two hardcoded constants with `sessionEnd − 30 min` (entry block)
and `sessionEnd − 21 min` (forced flat). On a 17:00 close these evaluate to exactly 16:30 and
16:39, so normal sessions are unchanged *by construction*. Replayed over all 1,139 sessions:

| object | N≤5 | N≤10 | N≤15 | N≤20 | N≤30 | N≤45 | N≤60 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Product B, as built | 0 | 0 | 0 | 0 | 3 | 17 | 152 |
| Product B, **with C2** | 0 | 0 | 0 | 0 | 3 | 17 | 152 |
| Product A, as built | 0 | 0 | **3** | **4** | 14 | 101 | 621 |
| Product A, **with C2** | **0** | **0** | **0** | **0** | 9 | 96 | 616 |

C2 removes every sub-30-minute event on every object, including the 2 stamped exactly at an
early close. The residual N≤30 entries are fills stamped precisely at `sessionEnd − 30 min`
(decision at −33 min), which is the intended boundary of the existing rule, not a leak.

**The existing entry block, expressed session-relative, IS `no_new_entry_after = sessionEnd −
30 minutes`, on every session type.** There is nothing left for a new parameter to do.

---

## 7. Consistency with established wave context

| established claim | this work |
|---|---|
| 43 holiday early-close sessions (31/9/2/1) | **Confirmed exactly**, independently from `fbos` |
| Product A compliant on normal sessions | **Corroborated** — last normal-session risk increase is a 16:30 fill (16:27 decision); zero inside 30 min |
| BEST_ONE_MNQ exit defect; entries submitted normally | **Corroborated** — MNQ's last entry stamp is 16:30, identical to NQ, so `entryBlocked` demonstrably works on it |
| V1e: all three objects breach the early-close margin window | **Corroborated and extended** — Product A's 7 late early-close risk increases are located and listed by date |
| — | **NEW, flagged:** 2023-04-05 NQ signal-series data gap (spurious 14:03 session end); 2024-04-21 Sunday NQ/MNQ session-open misalignment (8 bars) |

**No contradiction found with any established context item.**

---

## 8. What is explicitly NOT claimed

- No claim that late-session entries are or would be unprofitable. Wave 16's directional P&L
  hint (N≤60 net negative on both instruments) was **not** re-tested here and is **not** part
  of this verdict; the verdict rests only on event counts. Nothing here establishes future
  profitability of anything.
- No parameter was searched, fitted, or tuned. The 30/21-minute figures are C2's, already
  frozen in `spec.yaml`, and were used as-is.
- The MNQ object's entry *counts* are conditioned on a broken exit path and are reported for
  timing evidence only (§3).
- The `runs/W17_C4_COMPLIANCE/out/` directory contains files from other W17 items; this item
  wrote only `v1d_*`.
