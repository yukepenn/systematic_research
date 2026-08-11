# SIMPLE01 — SPEC — Frozen Candidate Manifest (Task 1)

**Role discipline (binding on this document and on whoever executes SIMPLE01 from it):** this
manifest was written by the SPEC agent under campaign directive sec71-72. No backtest was run, no
PnL/Sharpe/net figure for any Product A/B rung was computed or viewed while writing it. Every
construction below is derived from a direct, line-cited read of the incumbent `.cs` files and from
finite-state proofs already on record (`EQV01_BEHAVIORAL_CANONICALIZATION`), not from any
performance intuition about which rung "should" win. **This document freezes WHAT gets tested, not
whether any of it works.**

**Objective this ladder serves** (per governance constraints, restated so it is never lost in
execution): identify the simplest architecture that cannot be shown to be materially worse than the
full incumbent — not the highest-Sharpe variant. If more than one rung passes the Task-2 margins,
the SIMPLEST passing rung is preferred, not the best-performing one.

**Sources read in full before writing this document:**
`src/ninjascript/SolarWaveSMMaster_v4.cs`, `src/ninjascript/SolarWaveOneContractNQ_v5.cs`,
`research/system_master/CANONICAL_MATHEMATICAL_SPEC.md`,
`research/system_master/EQV01_BEHAVIORAL_CANONICALIZATION/REPORT.md`,
`research/system_master/PLACEBO01_COMPONENT_CAUSALITY/REPORT.md` (context only — a causality
diagnostic on the CURRENT full systems, not a SIMPLE01 result; read for motivation, not for any
number about a SIMPLE01 candidate, none of which exist yet).

---

## 0. Shared vocabulary (both products, verified against code)

Both products share one upstream pipeline before they diverge:

```
sumNext  = sum of 13 virtual Solar members' pending signal, in [-13,13]
T        = clip(-10,10, round_away(sumNext/13.0 * 10.0))
tiltState = sign(lastSessionClose - SMA_50(session closes))          in {-1,0,1}
bmomPos  = RTH breakout/VWAP-band state, in {-1,0,1}  (BmomBar(), identical logic both files)
```

`tiltState` is the **sole HTF signal**. `bmomPos` is the **sole B-MOM signal**. Both are computed by
identical code in both `.cs` files (line ranges below). Everything the two products do differently
happens strictly downstream of these three shared quantities.

---

## 1. Product B — `SolarWaveOneContractNQ_v5.cs` (`SolarWaveOneContractMNQ_v5.cs` is decision-logic
identical; instrument-only differences, verified by diff of the two files' `OnBarUpdate` bodies)

### 1.1 Where HTF actually touches the decoder — verified, not assumed

Direct read, `SolarWaveOneContractNQ_v5.cs:405-410`:

```csharp
int sumNext = 0;
for (int m = 0; m < NMEM; m++) sumNext += mPending[m];
int T = Math.Max(-10, Math.Min(10, (int)Math.Round(sumNext / 13.0 * 10.0, ...)));
double mm = (sumNext != 0 && tiltState != 0 && Math.Sign(sumNext) == tiltState) ? TiltMult : 1.0;
int Tp = Math.Max(-13, Math.Min(13, (int)Math.Round(T * mm * TiltRescale, ...)));
double M = WSolar * Tp + WBmom * bmomPos;
```

`tiltState` appears **exactly once** in this entire file's decision path: inside `mm`'s ternary
condition on line 408. It is not read anywhere else in `OnBarUpdate`, `BmomBar`, `UpdateMachine`,
`Decide`, or the hysteresis block (lines 424-445). `bmomPos` appears **exactly once** in the
decision path too: as an additive term in `M` on line 410. Neither signal has any second,
independent entry point into Product B's routing decision.

**Verdict on the owner's proposed 4-rung ladder (B0→B1→B2→B_FULL): B2 ("Solar+B-MOM+HTF") and
B_FULL (the unmodified incumbent) are the identical construction — there is no fourth rung.**
"Solar+B-MOM+HTF" *is* "`mm` computed from the real `tiltState`, plus `bmomPos` real" — which is
exactly what the incumbent file already does with no modification. Constructing a separate "B2" would
require literally re-deriving the incumbent unchanged and giving it a second name. **B2 is dropped
as redundant with B_FULL, not tested as a separate object.** The corrected ladder has **three**
rungs, not four.

*(This matches, independently, `CANONICAL_MATHEMATICAL_SPEC.md`'s own summary table: for Product B
it lists exactly one behaviorally meaningful lever beyond the Solar/B-MOM blend — the `mm` gate —
and no second HTF touchpoint anywhere in that document either.)*

### 1.2 Frozen Product B ladder — exact constructions

All three rungs keep IDENTICAL: the 13-member Solar ensemble, `VolPeriod/SMinTicks/SMaxTicks`,
`TiltRescale`, `WSolar`, the hysteresis state machine and its thresholds
(`EntryLevel=3.0/ExitLevel=1.0`), `forceFlat`/`entryBlocked` session-timing gates, and
`BmomBandDays` where B-MOM is present. Only the two forcings below change.

| Rung | `mm` | `bmomPos` | Construction |
|---|---|---|---|
| **B0** (Solar only) | forced `1.0` | forced `0` | `Tp = clip(round(T · 1.0 · TiltRescale)); M = WSolar·Tp` (the `WBmom·bmomPos` term drops out identically since `bmomPos≡0`) |
| **B1** (Solar + B-MOM) | forced `1.0` | **real** | `Tp = clip(round(T · 1.0 · TiltRescale)); M = WSolar·Tp + WBmom·bmomPos` |
| **B_FULL** (incumbent, unmodified) | **real** | **real** | exactly `SolarWaveOneContractNQ_v5.cs` / `_MNQ_v5.cs` as shipped, byte-for-byte |

Well-posedness: forcing `mm≡1.0` requires no counterfactual state — `mm`'s own formula never
references anything that becomes undefined when its ternary is replaced by a constant. Forcing
`bmomPos≡0` is likewise a pure term-drop (`bmomPos` enters `M` only additively). **No hybrid-state
risk exists for the Product B ladder**: `mm` and `bmomPos` are architecturally independent — neither
one's real value is computed from, or gates, the other — so any of the four `{mm real/forced} ×
{bmomPos real/forced}` cells is well-defined. B0/B1/B_FULL is the subset of that 2×2 grid the owner's
nested ladder actually needs (the fourth cell, `mm` real / `bmomPos` forced, i.e. "HTF only, no
B-MOM," is a legitimate, equally well-posed construction but is **not part of the frozen ladder** —
the owner's proposal never asked for it, Product A's ladder already covers the analogous
"HTF-marginal-value-in-isolation" question via A2, and adding it here would be scope creep this SPEC
agent was not asked to authorize).

---

## 2. Product A — `SolarWaveSMMaster_v4.cs`

### 2.1 Where `ss` (short-halving) and `mm` (HTF up-weight) touch the decoder — verified

Direct read, `SolarWaveSMMaster_v4.cs:357-364`:

```csharp
int T = Math.Max(-10, Math.Min(10, (int)Math.Round(sumNext / 13.0 * 10.0, ...)));
double mm = (T != 0 && tiltState != 0 && Math.Sign(T) == tiltState) ? TiltMult : 1.0;
double ss = (T < 0 && tiltState > 0) ? ShortHalf : 1.0;
int Tpp = Math.Max(-13, Math.Min(13, (int)Math.Round(T * mm * ss * TiltRescale, ...)));
double M = KSolar * Tpp + KBmom * bmomPos;
int tgtRaw = Math.Max(-13, Math.Min(13, (int)Math.Round(M, ...)));
```

`bmomPos` is **not gated by either `mm` or `ss`** — it enters `M` as its own independent additive
term regardless of what `Tpp` did. The owner's A0 ("Solar+B-MOM continuous decoder") therefore
correctly keeps `bmomPos` real throughout the *entire* A ladder; only `mm` and `ss` are ever forced.
This is a real structural difference from the Product B ladder, where B-MOM itself is what B0→B1
ablates — **Product A's ladder never removes B-MOM; it only removes/isolates the two `tiltState`
usages (`mm`, `ss`).**

### 2.2 Mutual-exclusivity proof — resolving sec39's "impossible hybrid state" warning directly

`mm` fires iff `T≠0 ∧ tiltState≠0 ∧ sign(T)=tiltState`.
`ss` fires iff `T<0 ∧ tiltState>0`.

**Claim: `mm` and `ss` can never both fire on the same bar, for any `(T, tiltState)` in the real
domain.** Proof by cases:

- If `ss` fires: `T<0` and `tiltState>0` ⟹ `sign(T)=-1 ≠ +1=tiltState` ⟹ `mm`'s third condition
  (`sign(T)=tiltState`) is false ⟹ `mm` does not fire.
- If `mm` fires: `sign(T)=tiltState`, so either (`T>0, tiltState>0`) or (`T<0, tiltState<0`). The
  first case fails `ss`'s `T<0` requirement; the second fails `ss`'s `tiltState>0` requirement.
  Either way `ss` does not fire.

So at most one of `{mm active, ss active, neither}` is ever true on a given bar in the real,
unmodified code — **this is a fact about the incumbent's own logic, not an artifact of testing it.**
This is independently corroborated by `EQV01_BEHAVIORAL_CANONICALIZATION/REPORT.md` §3, whose
exhaustive 84-state enumeration for Product A found the same thing from a different angle: the cell
`(mm=1.25, ss=0.5)` is **"structurally impossible in real execution... tested anyway, still
matched."**

**Consequence for sec39.** Constructing "A1 = ss real, mm forced to 1.0" never asks what happens on a
bar where the real code's own `mm` branch would have fired differently under some counterfactual —
because on every bar where `ss` is genuinely active in the real code, `mm` was *already* inactive
(=1.0) there. Forcing `mm≡1.0` while leaving `ss` real therefore reproduces the real code's own
`ss`-active bars EXACTLY, and only changes behavior on the (disjoint) set of bars where the real
code's `mm` was actually active — which is precisely the ablation A1 is supposed to measure. The
symmetric argument holds for A2. **No impossible hybrid state exists here; A1 and A2 are both
well-posed and are RETAINED, not dropped.**

**What A1/A2 are NOT, and this matters for how they should be read downstream (Task 3 elaborates):**
because `mm` and `ss` never co-fire, A1 and A2 do not represent points on a single increasing-
complexity chain the way B0→B1→B_FULL does. They are two **siblings** of A0 (one factor added at a
time), and A_FULL is the cell where both are real — a 2×2 factorial in `{ss, mm}`, not a 4-rung
chain. This is stated explicitly because the owner's phrasing ("A0 → A1 → A2 → A_FULL") reads
left-to-right as if each arrow were cumulative; it is not, and treating it as cumulative would
silently misdescribe A2 as "A1 + HTF" (i.e., both real) when the actual frozen construction for A2
is "HTF real, short-halving forced OFF."

### 2.3 Frozen Product A ladder — exact constructions

All four cells keep IDENTICAL: the 13-member Solar ensemble, `TiltRescale`, `KSolar`, `KBmom`,
`BmomBandDays`, `bmomPos` (always real), and the ops-layer session-close/entry-block rules.

| Rung | `mm` | `ss` | Construction |
|---|---|---|---|
| **A0** (Solar+B-MOM, no HTF, no short-halving) | forced `1.0` | forced `1.0` | `Tpp = clip(round(T · TiltRescale)); tgtRaw = clip(round(KSolar·Tpp + KBmom·bmomPos))` |
| **A1** (+ short-halving only) | forced `1.0` | **real** | `Tpp = clip(round(T · ss · TiltRescale)); tgtRaw = clip(round(KSolar·Tpp + KBmom·bmomPos))` |
| **A2** (+ HTF up-weight only) | **real** | forced `1.0` | `Tpp = clip(round(T · mm · TiltRescale)); tgtRaw = clip(round(KSolar·Tpp + KBmom·bmomPos))` |
| **A_FULL** (incumbent, unmodified) | **real** | **real** | exactly `SolarWaveSMMaster_v4.cs` as shipped, byte-for-byte |

No rung is dropped for Product A — all four cells of the factorial are well-posed per §2.2. The one
correction versus the owner's sketch is the **relationship** between A1/A2 and A_FULL (siblings of
A0, not a chain through each other), not the existence of any rung.

---

## 3. Frozen ladder summary

| Product | Rungs (frozen, final) | Owner's original count | Correction made |
|---|---|---|---|
| B | B0, B1, B_FULL — **3 rungs** | 4 (B0,B1,B2,B_FULL) | B2 ≡ B_FULL exactly (HTF's only touchpoint, `mm`, is what "B2" would have turned on — that's already B_FULL); dropped as redundant |
| A | A0, A1, A2, A_FULL — **4 rungs, factorial not chain** | 4 (A0,A1,A2,A_FULL) | Rung count unchanged; corrected the STRUCTURE from an implied 4-link chain to a 2×2 factorial in `{ss, mm}` (proven well-posed via mutual exclusivity, §2.2); no rung dropped |

**A1 and A2 have a distinct role from A0 and B0/B1.** Because `mm`/`ss` never co-fire, A1 and A2 keep
`tiltState`'s own computation (`TiltSma=50` SMA) fully live and change only which of two mutually-
exclusive usages of it is active. They exist to let a later stage causally attribute A_FULL−A0's gap
between short-halving and HTF up-weight separately (continuing, not duplicating, PLACEBO01's
component-causality program) — **not** because either is expected, by construction alone, to be a
materially simpler deployable system in its own right. Task 3 (`02_SPEC_complexity_metric.md`)
quantifies this: A1/A2 do not clear the frozen "meaningful complexity reduction" bar on their own,
while A0 does. This is a structural fact about the construction, established before any candidate is
scored — it is not a prediction about which rung will perform best.

---

## 4. Explicitly out of scope for this manifest

- No rung beyond the ones tabulated above is authorized. In particular: no "B-HTF-only, no B-MOM"
  cell (§1.2), no re-fit of `KSolar/KBmom/WSolar/WBmom/EntryLevel/ExitLevel`, no new hysteresis
  width, no change to the ops-layer session-close/entry-block/watchdog logic for any rung — every
  rung inherits that layer unmodified from its product's incumbent file.
- This document does not authorize running any of these seven candidates. Execution is a separate,
  future task, gated on `01_SPEC_frozen_margins.md` and `02_SPEC_complexity_metric.md` also being
  frozen (both written alongside this file) and on each execution run getting its own immutable
  `runs/SIMPLE01_<rung>/spec.yaml` per this repo's standing run-governance convention.
- No incumbent `.cs` file was modified, and none should be to execute this ladder — every rung is
  reproducible as a parameter-forcing variant of the existing files' own Python/analytics twins (or a
  literal copy of the `.cs` decision block with two lines constant-folded), never a rewrite of the
  shipped NinjaScript objects themselves.
