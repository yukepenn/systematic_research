# CANONICAL_MATHEMATICAL_SPEC

**Status:** derived 2026-08-10 from `EQV01_BEHAVIORAL_CANONICALIZATION/REPORT.md`, whose three
hypotheses all resolved to **EXACT_EQUIVALENCE** over their full reachable finite state spaces
(243/243, 729/729, 252/252 states — zero mismatches). Per campaign directive sec.21/105: **this is
a specification/representation document, not an alpha promotion.** The incumbent NinjaScript files
(`SolarWaveSMMaster_v4.cs`, `SolarWaveOneContractNQ_v5.cs`, `SolarWaveOneContractMNQ_v5.cs`) remain
the sole source of truth for live/backtest behavior and are unmodified. This document exists so the
system can be *explained* with the minimum exact behavioral representation — nothing here licenses
building `SolarWaveSMMaster_Canonical_v1.cs` etc. (that is EQV04, a separate, still-gated phase
requiring EQV02/EQV03 to pass first).

## Shared latent score

Both products decode from the same two upstream states:

- **`Tpp` / `Tp`** — the Solar13-consensus, tilt-adjusted, (Product A only: short-halving-adjusted)
  integer in `[-13,13]`. Derived from `sumNext` (the 13-member ensemble's raw pending-signal sum,
  integer in `[-13,13]`) and `tiltState` (sign of a 50-session SMA-relative close comparison,
  `{-1,0,1}`).
- **`bmomPos`** — the B-MOM state, a finite integer in `{-1,0,1}` (proven exhaustively this session
  by tracing `BmomBar()` in both `.cs` files — not a continuous quantity).

**Common evidence-score form, proven exact:**

```
Q = Tpp_or_Tp + 4 · bmomPos
```

is an exact (not approximate) integer reparametrization of each product's real weighted sum
`W_solar · Tpp_or_Tp + W_bmom · bmomPos`, in the specific sense that decoding `Q` through each
product's own rounding/clipping or hysteresis produces bit-identical routing decisions to the real
code, across every reachable state. **This holds despite `W_bmom/W_solar` not being exactly 4 for
either product** (Product A: 4.0268, Product B: 3.9938) — see the per-product sections below for
exactly why the quantization still lands exact, and how thin that margin is for Product A
specifically.

## Product A decoder — `SolarWaveSMMaster_v4.cs`

**Original implementation constants** (unchanged, still the sole live-behavior source):
`TiltMult=1.25, TiltRescale=0.9026, ShortHalf=0.5, KSolar=0.728654, KBmom=2.934159`.

```
T    = clip(-10,10, round_away(sumNext/13.0 * 10.0))
mm   = (T≠0 ∧ tiltState≠0 ∧ sign(T)=tiltState) ? 1.25 : 1.0
ss   = (T<0 ∧ tiltState>0) ? 0.5 : 1.0
Tpp  = clip(-13,13, round_away(T·mm·ss·0.9026))
tgtRaw = clip(-13,13, round_away(0.728654·Tpp + 2.934159·bmomPos))
```

**Proven-exact canonical form:**

```
Q_A    = Tpp + 4·bmomPos
target_A = clip(-13,13, round_away(0.73 · Q_A))
```

`0.73` and `4` are **REPRESENTATIONAL DECIMALS** for this canonical form — they stand in for
`KSolar=0.728654` (−0.18% off) and `KBmom/KSolar=4.0268` (+0.67% off) respectively, and the
substitution is proven behaviorally exact over all 243 reachable states. **This margin is real but
thin**: the tightest realized safety margin anywhere in the domain is `+0.00591` (at `|Tpp|=9`,
`bmomPos` matching sign). A future re-fit of `KSolar`/`KBmom` could plausibly break this specific
equivalence — it is not a structural guarantee, and should be re-proven (not assumed) if those
constants are ever touched.

**`ss` (short-halving)** is a genuine **BEHAVIORALLY MEANINGFUL PARAMETER**, not representational —
it is a real, disclosed long/short asymmetry with no Product-B analog (see below).

## Product B controller — `SolarWaveOneContractNQ_v5.cs` / `SolarWaveOneContractMNQ_v5.cs`

**Original implementation constants:** `WSolar=0.7086, WBmom=2.83, EntryLevel=3.0, ExitLevel=1.0`
(the latter two commented in the source as *"frozen seq-318, not a free parameter"*).

```
T   = clip(-10,10, round_away(sumNext/13.0 * 10.0))
mm  = (sumNext≠0 ∧ tiltState≠0 ∧ sign(sumNext)=tiltState) ? 1.25 : 1.0
Tp  = clip(-13,13, round_away(T·mm·0.9026))
M   = 0.7086·Tp + 2.83·bmomPos                          [continuous; never rounded/clamped]

hysteresis (Schmitt-trigger state machine, forceFlat always overrides to flat):
  flat:  M≥3.0  → long   |  M≤−3.0 → short
  long:  M≤−3.0 → short (reversal)  |  M≤1.0  → flat   |  else hold
  short: M≥3.0  → long (reversal)   |  M≥−1.0 → flat   |  else hold
```

**Proven-exact canonical form:**

```
Q_B = Tp + 4·bmomPos                    [always integer-valued: Tp integer + 4·bmomPos integer]
hysteresis on Q_B: entry ≥5 / ≤−5, exit ≤1 / ≥−1
```

**This is the exact integer quantization of the real continuous boundary, not a coincidental
near-miss.** `EntryLevel/WSolar = 3.0/0.7086 = 4.2337` and `ExitLevel/WSolar = 1.0/0.7086 = 1.4112`
— because `Q_B` is always an integer, any real threshold in `(4,5]` quantizes to the identical
routing decision as `5`, and any threshold in `[1,2)` quantizes identically to `1`; `4.2337` and
`1.4112` both fall inside those intervals. A structural check across all 27 `Q_B` values with
multiple contributing `(Tp, bmomPos)` source pairs found zero boundary-straddling collisions, with
the closest any real `M` value comes to a decision boundary being `0.1612` — roughly 18× the
`≈0.0088` maximum spread the `WBmom/WSolar≈4` approximation could introduce. **`5/1` in `Q_B`-space
is therefore a REPRESENTATIONALLY EXACT, not approximate, restatement of `EntryLevel=3.0/
ExitLevel=1.0` in `M`-space** — a materially more robust equivalence than Product A's, given the
much larger safety margin.

**Genuine, preserved asymmetries vs. Product A** (not unified into a prettier shared equation,
because the real code does not support that):
- Product B's `mm` gate uses `sign(sumNext)`, not `sign(T)` (proven this session to never actually
  diverge over `sumNext`'s reachable domain, but the code itself is written this way).
- Product B has **no `ss` short-halving term at all** — a real, permanent difference from Product A.
- Product B's `M` is **never rounded or clamped** before the hysteresis comparison; Product A's `M`
  is always rounded and clamped to `[-13,13]` before use as `tgtRaw`.

## `TiltRescale`: 0.9026 vs. 0.91

Proven **REPRESENTATIONAL_PRECISION** for both products, unconditionally, across 252/252 states
(two products × two independent enumeration methodologies each) — substituting `0.91` for the real
`0.9026` (a +0.82% relative change) never flips a single rounded/clamped integer output anywhere in
either product's reachable state space. This is the one canonicalization question in this document
with zero caveats or thin margins attached.

## Summary table — representational vs. behaviorally meaningful

| Quantity | Real value | Canonical substitute | Classification |
|---|---|---|---|
| `KSolar` (Product A) | 0.728654 | 0.73 | Representational (thin margin — see caveat above) |
| `KBmom/KSolar` (Product A) | 4.0268 | 4 | Representational (thin margin — see caveat above) |
| `EntryLevel/ExitLevel` in `Q_B`-space (Product B) | 4.2337 / 1.4112 | 5 / 1 | Representational (robust margin) |
| `TiltRescale` | 0.9026 | 0.91 | Representational (robust, unconditional) |
| `ss` short-halving (Product A only) | 0.5 when `T<0 ∧ tiltState>0` | — | **Behaviorally meaningful**, no A/B unification possible |
| `TiltMult`, `ShortHalf`, ensemble grid, `VolPeriod`, `BAND_DAYS`, `TiltSma` horizon | as coded | — | Structural/architecture choices — real research decisions, not decimal precision (see PERT01/GRID01 for their own robustness science) |

## What this document is not

This is not proof that a `SolarWaveSMMaster_Canonical_v1.cs` file would parity-match the incumbent
over real market data (`EQV02`, full-history array equality — not yet run) or in live NT8 execution
(`EQV04` — gated on `EQV02`/`EQV03` passing, not yet attempted). It is a finite-state proof only.
It also does not license any parameter change: `KSolar`, `KBmom`, `TiltRescale`, `EntryLevel`, and
`ExitLevel` remain exactly what they are in the incumbent files.
