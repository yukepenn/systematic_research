# EQV01 — Behavioral Canonicalization: Finite-State Equivalence Proof

**Scope:** Zero-alpha-budget audit. This is a pure mathematical/behavioral equivalence proof over
the finite reachable state space of the incumbent decoders — it is not a new trial, not a search
for a better system, and it does not change the incumbent's economic behavior in any way regardless
of outcome. Per campaign directive sec.21: **even where a hypothesis proves EXACT_EQUIVALENCE below,
that is a specification/representation finding, not an alpha promotion.** The incumbent NinjaScript
files (`SolarWaveSMMaster_v4.cs`, `SolarWaveOneContractNQ_v5.cs` and the MNQ sibling) are unchanged.
No orders, deployments, connections, or licensed vendor assemblies were touched. This document
synthesizes three completed sub-audits; it does not build EQV02 (full-history array equality) or
EQV04 (canonical NT8 files) — those are separate, later, gated phases and are explicitly out of
scope here.

**Inputs:** code-read notes (`out/00_code_read_notes.md`) plus three exhaustive enumeration scripts
and their result JSONs (`src/01_eqv_productA.py` → `out/eqv_productA_results.json`;
`src/02_eqv_productB.py` → `out/eqv_productB_results.json`; `src/03_eqv_tiltrescale.py` →
`out/eqv_tiltrescale_results.json`). All three were re-verified by direct read of the result files
before writing this synthesis.

---

## Headline verdicts (no partial credit)

| # | Hypothesis | Domain enumerated | Result | Verdict |
|---|---|---|---|---|
| 1 | Product A: `target_A = clip(-13,13, round_away(0.73 · (Tpp + 4·bmomPos)))` reproduces `tgtRaw` from `SolarWaveSMMaster_v4.cs` | 243/243 states (sumNext × tiltState × bmomPos, full reachable domain) | 243/243 exact match, 0 mismatches | **EXACT_EQUIVALENCE** |
| 2 | Product B (as owner recalled): `Q_B = Tp + 4·bmomPos` with hysteresis **+5/+1 / −5/−1** reproduces the real M-based hysteresis routing from `SolarWaveOneContractNQ_v5.cs` | 729/729 states (sumNext × tiltState × bmomPos × prior position, forceFlat/entryBlocked = false) | 729/729 exact match, 0 mismatches | **EXACT_EQUIVALENCE** |
| 3 | `TiltRescale = 0.91` (recalled/test) is behaviorally interchangeable with the actual constant `TiltRescale = 0.9026` for both products, post round+clip | 252/252 states across 4 independent enumeration passes (2 products × {full cartesian grid, reachability-aware}) | 252/252 exact match, 0 mismatches | **EXACT_EQUIVALENCE** |

All three hypotheses **PASS** at the required 100.000% exact-match bar. None is rejected. There is
no rounding-up of a partial result anywhere in this report — every number above is a literal exact
count from the enumeration scripts' output.

---

## 1. Product A canonicalization — `SolarWaveSMMaster_v4.cs`

**Real code** (lines ~357–364, re-verified this session):
```
T    = clip(-10,10, round_away(sumNext/13.0*10.0))
mm   = (T!=0 && tiltState!=0 && sign(T)==tiltState) ? TiltMult : 1.0
ss   = (T<0 && tiltState>0) ? ShortHalf : 1.0
Tpp  = clip(-13,13, round_away(T*mm*ss*TiltRescale))
M    = KSolar*Tpp + KBmom*bmomPos
tgtRaw = clip(-13,13, round_away(M))
```
Constants: `TiltMult=1.25, TiltRescale=0.9026, ShortHalf=0.5, KSolar=0.728654, KBmom=2.934159`.

**Proposed canonical form under test:** `Q_A = Tpp + 4·bmomPos`, `target_A = clip(-13,13,
round_away(0.73·Q_A))` — i.e., substituting the round numbers 4 and 0.73 for the real
`KBmom/KSolar` ratio and `KSolar` itself.

**Result: 243/243 exact match (100.000%). EXACT_EQUIVALENCE.** The reachable domain is
`sumNext ∈ [-13,13]` (27 values) × `tiltState ∈ {-1,0,1}` × `bmomPos ∈ {-1,0,1}` = 243 states —
the true reachable domain, not a sample.

**This is not a trivial or coincidental identity — the margin is real but thin.** The coefficients
being substituted are close to, but *not exactly*, round numbers:
- `KBmom/KSolar = 2.934159/0.728654 = 4.026820685812471` — **not exactly 4** (+0.0268 absolute,
  +0.6705% relative error vs. the substituted 4).
- `KSolar = 0.728654` — **not exactly 0.73** (−0.001346 absolute, −0.1844% relative error).

Despite these genuine, non-trivial deviations, every one of the 243 states' true `M` values sits
far enough from a half-integer rounding boundary to absorb the resulting perturbation. The tightest
margin found anywhere in the domain is **+0.00591**, at a five-way-tied cluster of states with
`|Tpp|=9` and `bmomPos` matching `Tpp`'s sign (`M = ±9.492045`, only 0.007955 from the nearest
half-integer boundary, against a coefficient-substitution perturbation of only ±0.002045 — smaller,
and oriented in the direction that does not cross the boundary). This is a knife's-edge-adjacent
pass, not a structurally guaranteed one: a future re-fit of `KSolar`/`KBmom` (e.g., re-optimization)
could plausibly break this equivalence given how thin the tightest margin is. That fragility is
itself a finding, reported here rather than smoothed over.

*(Cross-check: the independently-written Product-A port already in
`runs/PRICE01_PRODUCT_A_GENUINE_MNQ/src/01_dual_truth_repricing.py` matches the `.cs` file exactly —
same constants, gating, clamp order, and rounding formula — corroborating that this session's
re-implementation is not the source of the match.)*

---

## 2. Product B canonicalization + the disclosed threshold discrepancy — `SolarWaveOneContractNQ_v5.cs`

**Real code** (lines ~405–445, re-verified this session):
```
T   = clip(-10,10, round_away(sumNext/13.0*10.0))
mm  = (sumNext!=0 && tiltState!=0 && sign(sumNext)==tiltState) ? TiltMult : 1.0   [sign(sumNext), not sign(T)]
Tp  = clip(-13,13, round_away(T*mm*TiltRescale))    [no ss / short-halving term — real, disclosed asymmetry vs A]
M   = WSolar*Tp + WBmom*bmomPos                     [M is never rounded or clamped — stays continuous]
hysteresis on M, thresholds EntryLevel / ExitLevel, standard Flat/Long/Short state machine,
forceFlat overrides everything.
```
Constants: `WSolar=0.7086, WBmom=2.83, EntryLevel=3.0, ExitLevel=1.0`.

Two structural asymmetries vs. Product A were preserved (not silently unified) per the task's
instruction: (a) Product B's `mm` gate uses `sign(sumNext)`, not `sign(T)` — verified this session
that the two never diverge over `sumNext`'s full integer domain, so the asymmetry is real in the
code but never behaviorally activates; (b) Product B has **no `ss` short-halving term at all** —
this is a genuine, permanent difference from Product A, not an oversight, and was not given a
symmetric equivalent that doesn't exist in the real code.

### 2a. THE DISCLOSED DISCREPANCY — documented prominently, per campaign directive sec.2

**The owner recalled Product B's hysteresis thresholds as "+5/+1, −5/−1".** Direct re-read of
`src/ninjascript/SolarWaveOneContractNQ_v5.cs` line ~145 confirms the **actual deployed values are
`EntryLevel=3.0, ExitLevel=1.0`** — i.e. `hysteresis(3,1)` — explicitly commented in the `.cs` file
itself as **"frozen seq-318, not a free parameter,"** and matching `BASELINE_MODELS.md:469`'s own
independent description, **"Discrete hysteresis(3,1)."** There is no code path, config default, or
alternate documented reading anywhere in the repository under which 5/1 is the current deployed
value. **The recollection does not match the code and is treated here as a memory error, not an
alternate valid configuration of the incumbent system.**

Per the task's explicit instruction, the two questions this raises were tested **separately** and
are reported **separately** below — the owner's hypothesis was tested exactly as recalled, against
the real code, with no silent substitution in either direction.

**(i) As-recalled test (the actual hypothesis under audit):** `Q_B = Tp + 4·bmomPos` with
hysteresis **+5/+1, −5/−1 applied to `Q_B`** (the owner's literal recollection), tested for whether
it reproduces the real code's routing decision — real `M`-based hysteresis with the real
`EntryLevel=3.0, ExitLevel=1.0` (**not** substituting 5/1 into the real code's own state machine).

- **Result: 729/729 exact match (100.000%), 0 mismatches. EXACT_EQUIVALENCE.**
- Domain: `sumNext ∈ [-13,13]` × `tiltState ∈ {-1,0,1}` × `bmomPos ∈ {-1,0,1}` × prior position
  `∈ {-1,0,1}` = 729 states, `forceFlat`/`entryBlocked` both held false (session-timing gates
  orthogonal to this decoder/hysteresis question, per task scope).

**(ii) Diagnostic-correct-threshold check (context only, not the hypothesis under test):** what
threshold on `Q_B` *would* be needed if one wanted `Q_B·WSolar` to equal `M` exactly? Naive scaling
gives `EntryLevel/WSolar = 3.0/0.7086 = 4.2337` and `ExitLevel/WSolar = 1.0/0.7086 = 1.4112` — i.e.
**≈4.23/1.41, not 5/1.** Testing this diagnostic threshold pair directly also scores **729/729
exact matches (100.000%)** — identical to (i).

**Why both (i) and (ii) pass despite 5/1 not being the "naive" scaled value:** `Q_B = Tp + 4·bmomPos`
is *always* integer-valued (both terms integer, coefficient exactly 4). The real code's comparison
operators (`>=`, `<=`) mean any real threshold in `(4, 5]` quantizes to the *same* integer routing
decision as threshold `5`, and any threshold in `[1, 2)` quantizes to the same decision as `1`. The
true continuous boundaries `4.2337`/`1.4112` both fall inside those intervals — so `5/1` is not an
approximation that happens to mostly work, it is **the exact integer quantization of the true
continuous boundary**, not a coincidence. A structural diagnostic across all 27 `Q_B` integer values
with more than one contributing `(Tp, bmomPos)` source pair (where the `WBmom/WSolar ≠ 4` imprecision
could in principle matter) found **zero boundary-straddling collisions**; exact-decimal arithmetic
confirms the closest any of the 39 possible `M` values ever comes to a literal decision boundary is
**0.1612** — roughly 18× larger than the ≈0.0088 max `M`-spread the 4-vs-3.993791 coefficient
approximation could introduce anywhere.

**Separately, and only to quantify the size of the recollection gap** (a supplementary check, not
part of the primary hypothesis test): applying the owner's recalled thresholds **directly to `M`**
(i.e., `EntryLevel=5.0, ExitLevel=1.0` on the real continuous `M`, in place of the real
`EntryLevel=3.0, ExitLevel=1.0`) fires a *different* stateless entry decision on **68 of 243** raw
`(sumNext,tiltState,bmomPos)` decoder states (**27.98%**) versus the real 3.0/1.0-on-`M` behavior.
**This confirms the recollection is not behaviorally close to the deployed code when applied at
face value to `M`** — the reason the as-recalled hypothesis in (i) above nonetheless matches exactly
is that the owner's recalled `Q_B`-space statistic (`Tp + 4·bmomPos`) and thresholds (5/1) form an
internally-consistent alternate coordinate system whose integer quantization happens to land exactly
on the real `M`-space boundaries — not that "5/1 ≈ 3/1" in any direct sense.

### 2b. Bottom line for Product B

- **As-recalled hypothesis (Q_B/hysteresis(5,1)) vs. real code: EXACT_EQUIVALENCE, 729/729.**
- **Real deployed thresholds are EntryLevel=3.0/ExitLevel=1.0, not 5/1** — a genuine, disclosed
  correction to the owner's recollection, now on record. This does not change the incumbent code;
  it changes what description of the incumbent code is accurate going forward.
- The two facts are not in tension: the as-recalled *statistic-and-threshold pair* reproduces the
  real routing exactly, precisely because it is evaluated in a different (but exactly quantization-
  equivalent) coordinate space than "5/1 applied naively to the real EntryLevel/ExitLevel."

---

## 3. `TiltRescale` precision — 0.9026 (actual) vs. 0.91 (recalled/test)

**Result: 252/252 exact match across four independent enumeration passes (100.000%).
EXACT_EQUIVALENCE.**

Two products × two enumeration methodologies each, all matching:
- Product A, full cartesian grid (`T×mm×ss` = 84 states): 84/84 match.
- Product A, reachability-aware (`T×tiltState` = 63 states, unreachable `(mm,ss)` cells identified
  and excluded from the "real" set but tested anyway as a conservative superset): 63/63 match. The
  reachability pass additionally proves Product A's `(mm=1.25, ss=0.5)` cell is **structurally
  impossible** in real execution (`ss=0.5` requires `tiltState=+1` while `T<0`, which forces
  `sign(T)=-1 ≠ tiltState`, collapsing `mm` to 1.0) — tested anyway, still matched.
- Product B, full cartesian grid (`T×mm` = 42 states, no `ss` term — consistent with §2's disclosed
  asymmetry): 42/42 match.
- Product B, reachability-aware (`T×tiltState` = 63 states): 63/63 match.

Relative delta between the two constants is `0.91/0.9026 − 1 = +0.820%`. Despite this, the
coefficient sits far enough from every rounding/clip boundary that it never flips an integer output
anywhere in the finite state space, for either product. **Classification: `TiltRescale`'s precision
(0.9026 vs. 0.91) is REPRESENTATIONAL_PRECISION for this specific downstream rounding/clipping
context — not a behavioral degree of freedom.** This classification is unconditional (100.000%
exact across all four passes), not a "close enough" judgment call.

---

## Cross-cutting notes surfaced during this audit (context, not new hypotheses)

- **`bmomPos` domain** is a finite 3-state integer `{-1,0,1}` in both products (traced exhaustively
  through `BmomBar()` in both `.cs` files), confirming the "finite-state" framing of all three
  hypotheses above was well-posed to begin with, not an approximation of a continuous quantity.
- **Rounding semantics**: all five decoder call sites across both products use
  `Math.Round(double, MidpointRounding.AwayFromZero)` at 0 digits — never the banker's-rounding
  default — verified exhaustively; no genuine `.5` floating-point midpoint case arises for `T`
  itself, but `Tpp`/`Tp`/`tgtRaw`/`M` can land near true `.5` boundaries given the irrational-ish
  multipliers involved, which is why left-to-right IEEE-754 evaluation order was replicated exactly
  in all three enumeration scripts.
- **Independent Python port cross-check**: the existing `product_a_exec_generalized` port in
  `01_dual_truth_repricing.py` matches the `.cs` file byte-for-byte on constants, gating, clamp
  order, and rounding formula.
- **Previously-undisclosed, out-of-scope finding (flagged, not corrected, not acted on):**
  `health_substrate.py` computes a single shared `tilt_state` array via
  `.rolling(50).mean()` (default `min_periods=50`, i.e. Product A's `">="` convention) and reuses
  that *same* array for its own Product-B `M` calculation. The real Product-B `.cs` files compute
  `tiltState` locally using a `">"` (not `">="`) threshold — verified as a consistent split across
  all versioned files in `src/ninjascript/` (4/4 `SMMaster_v*` files use `">="`; 12/12
  `OneContract*`/`OneLot*` files use `">"`). Practical impact is bounded to one session near the
  very start of loaded chart history (both conventions read identical rolling windows once warmed
  up) and is immaterial to canonical-window results, but it is a genuine byte-level mismatch between
  Product B's real code and existing Python tooling that had not been flagged before this session.
  This is noted for the record only; no code was changed and this finding is outside EQV01's scope.

---

## Governance restatement (per campaign directive sec.21)

**All three hypotheses tested in this audit resolve to EXACT_EQUIVALENCE over their full reachable
finite state spaces (243, 729, and 252 states respectively — 0 mismatches in every case).** Under
this campaign's directive, that outcome is explicitly a **specification/representation finding, not
an alpha promotion, not a strategy change, and not a trading decision of any kind.** The incumbent
NinjaScript files (`SolarWaveSMMaster_v4.cs`, `SolarWaveOneContractNQ_v5.cs`, and the MNQ sibling)
are unmodified and remain the sole source of truth for live/backtest behavior; nothing here alters
what those files do, and no order, deployment, connection, license, or account was touched in the
course of this audit. Had any hypothesis been REJECTED, this report would state plainly that the
corresponding proposed simplified equation is not behaviorally interchangeable with the current
implementation and must not be used as a description of it going forward — that caveat does not
apply here because no rejection occurred, but is recorded per the task's instruction for
completeness.

**Separately and independently of the above:** the owner's recollection of Product B's hysteresis
thresholds ("+5/+1, −5/−1") does **not** match the deployed code (`EntryLevel=3.0, ExitLevel=1.0`,
commented "frozen seq-318, not a free parameter"). This is a **documented correction to the
recollection**, not a code change, not a new discrepancy in the code itself, and not evidence
against the as-recalled hypothesis's EXACT_EQUIVALENCE result in §2a(i) — the two facts coexist for
the structural reason explained in §2.

## Explicitly out of scope for this report

EQV02 (full-history array equality against real market data) and EQV04 (canonical NT8 file
generation) are **separate, later phases, gated on this proof passing**, and were **not** built or
run as part of this task.

---

## Artifacts

- Code-read notes: `research/system_master/EQV01_BEHAVIORAL_CANONICALIZATION/out/00_code_read_notes.md`
- Product A: `src/01_eqv_productA.py` → `out/eqv_productA_results.json` (243/243, EXACT_EQUIVALENCE)
- Product B: `src/02_eqv_productB.py` → `out/eqv_productB_results.json` (729/729, EXACT_EQUIVALENCE)
- TiltRescale: `src/03_eqv_tiltrescale.py` → `out/eqv_tiltrescale_results.json` (252/252, EXACT_EQUIVALENCE)
