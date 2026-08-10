# EQV02 — Full-History Array Equality: CURRENT_FORM vs CANONICAL_FORM

**Scope:** Zero-alpha-budget audit, gated on
`research/system_master/EQV01_BEHAVIORAL_CANONICALIZATION/REPORT.md` (all three canonicalization
hypotheses proved `EXACT_EQUIVALENCE` over their full reachable finite-state spaces: Product A
243/243, Product B 729/729, TiltRescale 252/252). EQV01 was a pure single-step, stateless decoder
enumeration over the *abstract* domain. EQV02 asks two questions EQV01 could not: **(1)** does every
*real historical* bar actually land inside that enumerated domain, and **(2)** does the equivalence
survive the genuinely new ground of the **operational overlay** — Product A's forced-flat/entry-block
session-timing gates and Product B's `forceFlat`/`entryBlocked` gates plus the full **time-sequenced,
path-dependent hysteresis state walk** (not a single-step transition) — run bar-by-bar over real
session clocks against real historical data. Per campaign directive sec.21, even a full pass below is
a **specification/representation finding, not an alpha promotion, not a strategy change, and not a
trading decision** — it does not authorize EQV04 (canonical NT8 file generation) by itself; EQV04
remains a separate, later, gated phase. The incumbent NinjaScript files (`SolarWaveSMMaster_v4.cs`,
`SolarWaveOneContractNQ_v5.cs`, and the MNQ sibling) are unmodified. No orders, deployments,
connections, or licensed vendor assemblies were touched.

**Inputs:** two independent array-equality scripts and their result JSONs —
`src/01_productA_full_history.py` -> `out/productA_array_equality.json`;
`src/02_productB_full_history.py` -> `out/productB_array_equality.json`. Both were re-read directly
from disk before writing this synthesis (not taken on trust from the scripts own console output).

**Data:** `runs/AUDIT03_BARS/nq_3m_2022_2026.csv`, 3-minute NQ bars, 2022-01-02 18:03 ET through
2026-07-31 16:57 ET (540,232 bars), strictly before the 2026-08-01 `LOCKED_FORWARD` boundary (asserted
in code in both scripts). No bar at or after 2026-08-01 was read or used.

---

## Headline verdicts (no partial credit)

| Product | Raw (pre-overlay) array hash-equal | Operational (post-overlay) array hash-equal | Exposure/event-sequence hash-equal (incl. timestamps/qty) | All historical states inside EQV01 domain | Out-of-domain states found | Verdict |
|---|---|---|---|---|---|---|
| **A** (`SolarWaveSMMaster_v4.cs`) | true | true | true | true (243/243 states actually visited) | 0 | **EXACT_EQUIVALENCE** |
| **B** (`SolarWaveOneContractNQ_v5.cs`) | true | true | true | true | 0 | **EXACT_EQUIVALENCE** |

**Both products PASS.** Canonical window (2023-01-01T06:00:00Z to 2025-02-02T22:59:59Z per CLAUDE.md):
0 mismatches out of 245,943 bars for either product. Secondary/bonus fuller window (2022-01-02 to
2026-07-31, 540,232 bars): 0 mismatches for either product. Every SHA256 hash pair reported below is
bit-identical between `CURRENT_FORM` and `CANONICAL_FORM` — this is stronger than a per-bar
0-mismatch count alone, since a hash match additionally rules out any alignment/off-by-one error in
how the two forms arrays were compared.

---

## 1. Product A — `SolarWaveSMMaster_v4.cs`

**CURRENT_FORM:** the real decoder (`tgtRaw = clip(-13,13, round_away(KSolar*Tpp + KBmom*bmomPos))`,
`KSolar=0.728654, KBmom=2.934159`) plus the real operational overlay
(`EntryBlockMinutesBeforeClose=30`, `ForcedFlatMinutesBeforeClose=21`, verified this session from
`src/ninjascript/SolarWaveSMMaster_v4.cs` lines 94-95).
**CANONICAL_FORM:** `target_A = clip(-13,13, round_away(0.73*(Tpp + 4*bmomPos)))`, run through the
*identical* shared `simulate_overlay()` code path so any divergence found could only come from the
decoder substitution itself, never from a second, independently-written overlay implementation.

### 1a. Domain completeness (the first genuinely new finding)

Every one of the 540,232 historical bars (sumNext, tiltState, bmomPos) triple was checked against
EQV01's enumerated 243-state domain (sumNext in [-13,13], tiltState in {-1,0,1},
bmomPos in {-1,0,1}). **Result: 0 out-of-domain states found, and — stronger than mere
coverage — all 243 enumerated states were actually visited historically.** EQV01's finite-state proof
is therefore not merely *applicable* to real market history; against this data it is **empirically
exhaustive**, not just theoretically exhaustive. Had even one historical bar landed outside the
enumerated domain, that would have been an EQV01 domain-completeness failure in its own right, flagged
separately from any A-vs-canonical mismatch — no such case arose.

As part of this check, T was independently re-derived from sumNext via the exact
`clip(-10,10, round_away(sumNext/13*10))` formula and cross-checked against `grid_core.py`'s own
`e10_target(PEND)` output: match, 0 discrepancies over all 540,232 bars — a from-scratch
re-derivation, not a trust assumption on the shared upstream array.

### 1b. Raw decoder equality

`tgtRaw` (CURRENT_FORM) vs `target_A` (CANONICAL_FORM), bar-by-bar:

| Window | Bars | Mismatches | SHA256 (both forms) |
|---|---|---|---|
| Canonical (2023-01-03 to 2025-01-31 sessions) | 245,943 | 0 | `f1178da9...44f70f` (identical) |
| Fuller history (2022-01-03 to 2026-07-31) | 540,232 | 0 | `408b1264...8947933` (identical) |

The real historical margin analysis (the same near-miss diagnostic EQV01 ran over the *enumerated*
domain, here run over the *actual* historical M values) found the tightest safety margin any real
bar ever came to a rounding-direction flip is **+0.005910**, at bar 7,251 (**2022-01-24 15:36 ET**,
sumNext=13, tiltState=0, bmomPos=+1, T=10, Tpp=9, M_current=9.492045) — this is EQV01's
theoretically-tightest enumerated case (|Tpp|=9, margin +0.00591), now confirmed to be a **genuinely
reachable historical state**, not just an abstract corner of the domain. It falls inside the fuller
secondary window, outside the canonical window, and is reported for completeness since it is the
single closest call in the entire re-derivation.

### 1c. Operational overlay equality (the genuinely new ground)

Applying the shared `simulate_overlay()` path (real `EntryBlockMinutesBeforeClose=30` /
`ForcedFlatMinutesBeforeClose=21` gates) to both forms raw target arrays:

| Window | Operational target array | Physical position array | Exposure-change events |
|---|---|---|---|
| Canonical (245,943 bars) | 0 mismatches, SHA256 `88ec854a...805a29a` identical | 0 mismatches, SHA256 `64ad5563...7c092de` identical | 11,292 = 11,292 events, full sequence (bar, timestamp, quantity, resulting position) SHA256-identical, quantity-only sub-hash also identical, 16,786 = 16,786 total contracts traded |
| Fuller history (540,232 bars) | 0 mismatches, SHA256 `67327bb5...d2782507` identical | 0 mismatches, SHA256 `fe717bac...8c164526` identical | 25,441 = 25,441 events, full sequence and quantity sub-hash identical, 38,470 = 38,470 total contracts traded |

The engine session-close backstop (the fallback that would force-flat at the literal data boundary
if the strategy own gate failed to fire first) **never fired for either form, in either window (0
occurrences)** — the `ForcedFlatMinutesBeforeClose=21` gate always cleared positions with margin to
spare on its own, so this is not a case where equivalence is trivially guaranteed by a backstop
papering over a gate divergence.

### 1d. Self-checks (why this script own numbers should be trusted)

Before comparing forms, CURRENT_FORM own re-derivation was cross-checked twice against
independently-certified figures: (1) `tgtRaw` matches `grid_core.py`'s own `product_a_exec()` `M_a`
array exactly (`tgtRaw_vs_grid_core_product_a_exec_M_a: true`); (2) this script independently-written
overlay/pricing loop reproduces the certified dev-window net **$177,924.40** to the cent
($177,924.3999999992 vs certified $177,924.40, `match_within_1usd: true`), with `bar_pos` matching
`grid_core`'s own position array exactly. Both checks passed before any A-vs-canonical comparison was
run, so a bug in the shared harness would have surfaced here first, not been masked by a coincidental
match between two buggy forms.

**Product A verdict: EXACT_EQUIVALENCE, full history, both the raw decoder and the operational
overlay layer, canonical window and fuller window alike.**

---

## 2. Product B — `SolarWaveOneContractNQ_v5.cs`

**CURRENT_FORM:** the real continuous M = 0.7086*Tp + 2.83*bmomPos, real `hysteresis(EntryLevel=3.0,
ExitLevel=1.0)` state machine on M, with the real `forceFlat`/`entryBlocked` session-timing gates
applied bar-by-bar exactly per the .cs (elif control-flow shape reproduced, not approximated).
**CANONICAL_FORM:** Q_B = Tp + 4*bmomPos, `hysteresis(entry=5, exit=1)` on Q_B, identical
`forceFlat`/`entryBlocked` gates. Unlike Product A, this comparison is inherently **stateful and
path-dependent** — hysteresis carries a from-position across bars — so it is a genuine, non-trivial
extension beyond EQV01's single-step, forceFlat/entryBlocked-held-false enumeration.

### 2a. Domain completeness

All historical (sumNext, tiltState, bmomPos, priorPosition) states fell inside EQV01's enumerated
729-state domain — sumNext is structurally bounded to [-13,13] as a sum of 13 members each in
{-1,0,1}, and tiltState, bmomPos, priorPosition are all structurally bounded to {-1,0,1} by
construction, so this is confirmed by structural argument as well as by exhaustive check. **0
out-of-domain states found** — EQV01's exhaustiveness claim upheld, not contradicted, for Product B as
well.

Note on independence: Product B tiltState was built fresh and separately in this script using its
own real ">" convention (`sessCloses.Count > TiltSma`), deliberately **not** reusing the shared
`health_substrate.py` array ">=" convention (an already-disclosed, out-of-scope byte-level mismatch
flagged in EQV01's "Cross-cutting notes" section). The two conventions differ for exactly **one session**
(2022-03-14/15, bars 23,299-23,759), landing entirely outside the canonical window, confirmed immaterial
to this result.

### 2b. Raw and operational equality, four independent configurations

| Configuration | Bars | Mismatched bars | Position-array SHA256 (both forms) | Events (current = canonical) | Event-sequence SHA256 (both forms) |
|---|---|---|---|---|---|
| Canonical window, operational (gates on) | 245,943 | 0 | `1aad09c3...6c30dafd` identical | 1,830 = 1,830 | `0806cfd4...ed02bcca2` identical |
| Canonical window, raw gates-off | 245,943 | 0 | `7eb63fb9...8db96678` identical | 1,832 = 1,832 | `91253d4e...0752778d0` identical |
| Fuller history, operational (gates on) | 540,232 | 0 | `2c501558...9bea6b7b3` identical | 4,036 = 4,036 | `aa659a75...656e66` identical |
| Fuller history, raw gates-off | 540,232 | 0 | `a4d75a20...296b874b9` identical | 4,054 = 4,054 | `1012d448...747753c60` identical |

(The gates-off configuration isolates the genuine time-sequenced hysteresis carry-over from the
operational overlay contribution — both pass independently of each other, so a pass in the
operational row cannot be attributed solely to the gates masking a hysteresis-layer divergence, and
vice versa.)

### 2c. The operational overlay was genuinely, non-trivially exercised

`entryBlocked` fired on **5,929 of 245,943 canonical-window bars (2.4%)**, `forceFlat` on **4,312**
bars, including **1,617 bars that were entryBlocked-but-not-yet-forceFlat** — the specific
interaction state EQV01's stateless, gates-held-false enumeration never touched. This is the genuinely
new ground EQV01 did not cover, and it was exercised at meaningful frequency, not merely present in a
formality pass.

A specific control-flow interaction was checked and confirmed structurally identical in both forms:
when entryBlocked suppresses a reversal (M <= -EntryLevel or M >= EntryLevel true, but
entryBlocked=true), the real .cs elif chain silently falls through to the exit condition
instead of holding position — because any M that would trigger a reversal always also satisfies the
exit threshold. This "blocked-reversal-downgrades-to-plain-exit" pattern fired **722 times** over the
full history and is reproduced identically by construction in both forms, since both share the exact
same if/elif shape and the exact same forceFlat/entryBlocked boolean inputs (fed from the same
upstream arrays in both forms, so this could not have silently diverged undetected).

### 2d. Known, previously-disclosed data artifact — confirmed immaterial to this result

The NQ 09-26 3-minute feed gap on **2023-04-05 14:03 to 20:03 ET** (documented previously in
`runs/W17_C4_COMPLIANCE/src/v1d_late_entries.py`) falls inside the canonical window and causes NT8's
own IsFirstBarOfSession/IsLastBarOfSession to misread it as an early session close. This script
session grouping reproduces that real (bug-and-all) historical behavior rather than diverging from it.
Because it drives the forceFlat/entryBlocked/sessEnd inputs **identically** for both forms, it
cannot by itself cause CURRENT_FORM and CANONICAL_FORM to disagree with each other — confirmed: it
did not (0 mismatches in the window containing it).

### 2e. MNQ sibling — scope note, not independently re-run

`SolarWaveOneContractMNQ_v5.cs` was spot-checked this session via a byte-for-byte diff against the NQ
file: every formula, threshold, and control-flow branch of the decision layer (member ensemble,
BmomBar, tiltState, T/mm/Tp/M, Q_B, hysteresis, forceFlat/entryBlocked) is identical
between the two files; the only differences are which BarsArray index plays signal vs. execution
role — an instrument-wiring difference orthogonal to the math under test. **The MNQ object itself was
not independently re-run bar-by-bar in this task**; this result relies on the diff plus prior sessions
verification for that object, and is flagged here as a scope boundary rather than folded silently into
the headline verdict above (which covers the NQ object only).

**Product B verdict: EXACT_EQUIVALENCE, full history, raw decoder, time-sequenced hysteresis state
walk, and the operational forceFlat/entryBlocked overlay together, canonical window and fuller
window alike, in all four tested configurations.**

---

## 3. Out-of-domain-state check — explicit statement

Per task instruction: if any real historical bar's state had fallen outside EQV01's enumerated domain,
that would itself have been an important finding (EQV01's domain-completeness claim would have been
wrong), independent of and prior to any CURRENT_FORM-vs-CANONICAL_FORM mismatch question. **This did
not happen for either product.** all_historical_states_within_eqv01_domain: true and
out_of_domain_states_found: [] for both Product A (540,232/540,232 bars checked against the 243-state
domain, all 243 states actually visited) and Product B (540,232/540,232 bars checked against the
729-state domain, structurally bounded by construction). EQV01's finite-state enumeration is confirmed
exhaustive against real market history, not merely against its own abstract domain definition.

---

## 4. Governance restatement (per campaign directive sec.21)

**Both Product A and Product B resolve to EXACT_EQUIVALENCE at the full-history array level** —
0 mismatches out of 245,943 canonical-window bars and 0 mismatches out of 540,232 fuller-window bars,
for both the raw (pre-overlay) decoder arrays and the operational (post-overlay) target/position/event
arrays, with every reported comparison additionally confirmed by SHA256 bit-identity rather than
per-bar counting alone. **This extends — it does not merely repeat — EQV01's finite-state proof**: it
extends coverage from the abstract enumerated domain to real historical data (confirming empirical, not
just theoretical, exhaustiveness), and it extends scope from the single-step stateless decoder core to
the genuinely new ground of the time-sequenced, path-dependent operational overlay (session-timing
gates for Product A; forceFlat/entryBlocked/hysteresis state-carry for Product B) — ground EQV01's
own scope explicitly excluded.

Per campaign directive sec.21, **this is a specification/representation finding, not an alpha
promotion, not a strategy change, and not a trading decision of any kind.** The incumbent NinjaScript
files (SolarWaveSMMaster_v4.cs, SolarWaveOneContractNQ_v5.cs, and the MNQ sibling) are unmodified
and remain the sole source of truth for live/backtest behavior; nothing in this report alters what
those files do, and no order, deployment, connection, license, or account was touched in the course of
this audit.

**EQV02 passing for both products clears the way for EQV03 (if planned) and, ultimately, EQV04
(canonical NT8 file generation) to be attempted — subject to whatever additional gates EQV03 imposes.
EQV02 passing does not itself authorize EQV04**; EQV04 remains a separate, later, explicitly gated
phase with its own certification requirement (NT8 parity), not reached or attempted by this report.
Had either product's array equality failed anywhere in this task, this report would state plainly which
product failed, the root cause, and that **EQV04 must NOT proceed for that product** until the mismatch
is resolved — no such failure occurred for either product, so that clause does not apply here, but is
recorded per task instruction for completeness.

---

## Artifacts

- Product A script: `research/system_master/EQV02_FULL_HISTORY_ARRAY_EQUALITY/src/01_productA_full_history.py`
- Product A results: `research/system_master/EQV02_FULL_HISTORY_ARRAY_EQUALITY/out/productA_array_equality.json`
- Product B script: `research/system_master/EQV02_FULL_HISTORY_ARRAY_EQUALITY/src/02_productB_full_history.py`
- Product B results: `research/system_master/EQV02_FULL_HISTORY_ARRAY_EQUALITY/out/productB_array_equality.json`
- Upstream gate: `research/system_master/EQV01_BEHAVIORAL_CANONICALIZATION/REPORT.md` (243/243, 729/729, 252/252, all EXACT_EQUIVALENCE)
- Reference spec: `research/system_master/CANONICAL_MATHEMATICAL_SPEC.md`
- Data source: `runs/AUDIT03_BARS/nq_3m_2022_2026.csv` (2022-01-02 18:03 ET to 2026-07-31 16:57 ET, strictly before the 2026-08-01 LOCKED_FORWARD boundary)
