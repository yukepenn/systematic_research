# EQV01 — Code-read notes for byte-exact CURRENT_FORM reimplementation

Scope: ground every fact needed to reimplement Product A (`SolarWaveSMMaster_v4.cs`) and
Product B (`SolarWaveOneContractNQ_v5.cs` / `SolarWaveOneContractMNQ_v5.cs`) decoders, purely
by direct reading of the actual `.cs` files in this repo as of this session. Zero-alpha-budget
audit: mathematical/behavioral equivalence only, no strategy change implied or proposed.

All line numbers below are from the files as they exist right now (git HEAD, no local edits
made — this task is read-only).

---

## 1. Product A — `src/ninjascript/SolarWaveSMMaster_v4.cs`

### 1.1 Decoder, exact lines 357–364

```csharp
int sumNext = 0;
for (int m = 0; m < NMEM; m++) sumNext += mPending[m];
int T = Math.Max(-10, Math.Min(10, (int)Math.Round(sumNext / 13.0 * 10.0, MidpointRounding.AwayFromZero)));
double mm = (T != 0 && tiltState != 0 && Math.Sign(T) == tiltState) ? TiltMult : 1.0;
double ss = (T < 0 && tiltState > 0) ? ShortHalf : 1.0;
int Tpp = Math.Max(-13, Math.Min(13, (int)Math.Round(T * mm * ss * TiltRescale, MidpointRounding.AwayFromZero)));
double M = KSolar * Tpp + KBmom * bmomPos;
int tgtRaw = Math.Max(-13, Math.Min(13, (int)Math.Round(M, MidpointRounding.AwayFromZero)));
```

This **confirms the owner-supplied snippet verbatim** (variable names, operator precedence,
and the `mm`/`ss` split are exactly as given). Line numbers 357–364 match the estimate in the
prompt to the digit — no drift.

### 1.2 `sumNext` — exact definition and reachable range

`sumNext` is a **simple integer sum of the 13 members' `mPending[m]` values** (line 357–358),
no weighting, no normalization inside the sum itself (`/13.0*10.0` happens only in the `T`
line, after the sum).

Each `mPending[m]` is an `int` (`private int[] mPending = new int[NMEM];`, line 82) and is
provably confined to `{-1, 0, 1}` for every reachable state, by induction on `Decide()`
(lines 216–224):
- Base case: C# default-inits `int[]` to all zeros, so at `CurrentBar==0` every `mPending[m]==0`.
- Inductive step: `Decide(m)` sets `mPending[m]` to exactly one of: `0` (flatten branch), the
  prior `mPos[m]` (hold branch — and `mPos[m]` was itself copied from a prior `mPending[m]`, so
  it inherits the same `{-1,0,1}` invariant by induction), or `mSig[m]` (flip branch). `mSig[m]`
  is reset to `0` every bar in `UpdateMachine()` (line 196: `mSig[m] = 0;`) and only ever
  reassigned to the literal `-1` or `1` (lines 206, 212). So `mSig[m] ∈ {-1,0,1}` always, closing
  the induction.
- Session end additionally hard-zeros all 13 (`for (int m...) { mPos[m]=0; mPending[m]=0; }`,
  line 345), which is a no-op on the invariant (0 is already in the set).

**Reachable range of `sumNext`: integers in `[-13, 13]` inclusive**, all 27 values reachable in
principle (13 members, each independently `{-1,0,1}`).

### 1.3 `tiltState` — exact reachable range

`private int tiltState;` (line 86), default-inits to `0`. Only ever reassigned at line 351,
inside the session-end block:
```csharp
tiltState = Math.Sign(Close[0] - s / TiltSma);
```
`Math.Sign(double)` returns exactly `{-1, 0, 1}` (int). **Confirmed: `tiltState ∈ {-1, 0, 1}`**,
nothing else — matches the prompt's assumption exactly.

Note the SMA window **includes the just-closed session's own close** (`sessCloses.Add(Close[0])`
at line 346 happens *before* the SMA sum at lines 347–352), so `tiltState` computed on session
S's last bar is `sign(close[S] - mean(close[S-49..S]))`. Since `T` is forced to `0` on the same
session-end bar (all `mPending` were just zeroed at line 345, so `sumNext==0` on that bar),
this value has no effect on that bar's own `Tpp`; it only takes effect starting the *next*
session's bars, per the file's own comment (lines 341–342) — "matches twin `rolling(50).shift(1)`".

### 1.4 `bmomPos` — exact reachable range/type (the load-bearing question)

`private int bmomPos;` (line 91) — **a genuine 3-state integer, not a continuous value.**
Domain is exactly `{-1, 0, 1}`, proven from `BmomBar()` (lines 226–261):
- Reset to `0` at RTH open (`hm==93300`, line 231) and forced to `0` whenever
  `hm >= 155700 || sessEnd` (line 259, unconditional overwrite — this is the v4-specific fix
  described in the file's own header comment, lines 52–66: bmomPos now *also* flattens on the
  session's own last bar via `sessEnd`, closing a bug where a truncated-RTH holiday session
  could carry a stale nonzero `bmomPos` into the next overnight session).
- The only other assignment is `bmomPos = sig;` (line 256) inside `if (sig != 0)`, where `sig`
  is a local `int` initialized to `0` and only ever set to the literals `1` or `-1` (lines
  254–255). So this branch can only ever write `1` or `-1`, never anything else, and it only
  fires at all when `hm <= 155400 && rthDayCount >= BmomBandDays`.
- **So `bmomPos ∈ {-1, 0, 1}` for its entire lifetime — this is a well-posed finite 3-state
  hypothesis, not a continuous quantity.** (This directly answers the prompt's "matters
  enormously" question: yes, `bmomPos` is exactly as finite as `T`/`Tpp`.)

Traced to the Python analog `bmom_pos_series()` in
`runs/SA0_SYSTEM_STRUCTURE/current_health/src/health_substrate.py` lines 60–91: `pos` is a
plain Python `int` local, initialized `0`, and only ever reassigned the literals `0`, `1`, or
`-1` (lines 76, 84, 86) — **exact structural match** to the `.cs` 3-state domain. The Python
twin's flatten condition uses a precomputed `flat_hm` (last 3-minute slot with `hm <= 1557`,
lines 71/75-76) rather than a literal `hm >= 155700` test; this is a deliberate data-driven
equivalent, and the `.cs` file's own header comment (lines 60-65) explicitly says the v4 fix
was written to match this Python behavior "exactly." I did not re-derive bar-grid alignment
proof that `flat_hm == "the last hm with hm<=1557"` always coincides with the first `hm>=155700`
3-minute bar; this rests on the 3-minute bar grid being aligned to `:00/:03/:06...` from a fixed
session-start anchor, which is true by construction of the data pipeline elsewhere in the repo
but was not re-verified bar-by-bar in this pass. Flag as a low-risk residual assumption, not a
found discrepancy.

### 1.5 Rounding function — exact semantics

`Math.Round(double value, MidpointRounding mode)` — the two-argument `System.Math` overload
that rounds `value` to the nearest **integer** (0 fractional digits) using the supplied
convention, returned as a `double`. Every call site in both files passes
`MidpointRounding.AwayFromZero` explicitly (never the default, which is `ToEven`/banker's
rounding) — so **no banker's-rounding edge cases anywhere in this codebase's decoder path**;
half-integer inputs always round away from zero (`2.5→3`, `-2.5→-3`).

Cast/type sequence at every use site: `double` raw value → `Math.Round(double, MidpointRounding)`
→ `double` (already integral, e.g. `3.0`) → C-style `(int)` cast (truncating, but safe here
because the operand is already an exact integral double of small magnitude — no data loss).

Floating-point midpoint-boundary check for the `T` line specifically: `T` needs
`sumNext*10/13` to land on an exact `.5` for a genuine midpoint case to arise. Solving
`20*sumNext ≡ 0 (mod 13)` with `gcd(20,13)=1` forces `sumNext` to be a multiple of 13; within
the reachable domain `sumNext ∈ {-13,0,13}`. `sumNext=0 → T=0` trivially (no midpoint).
`sumNext=±13 → ±13.0/13.0 = ±1.0` exactly (IEEE-754 same-value division is exact) `*10.0 = ±10.0`
exactly — again not a midpoint, it's an exact integer. **So no genuine `.5`-boundary ambiguity
ever arises in the `T` computation, given `sumNext`'s actual integer domain.** The `Tpp` and
`tgtRaw` lines involve non-rational multipliers (`TiltMult=1.25`, `TiltRescale=0.9026`,
`ShortHalf=0.5`, `KSolar`, `KBmom`) and CAN land arbitrarily close to `.5` boundaries for some
`T`/`mm`/`ss` combinations; a byte-exact Python port must replicate the **exact same operation
order** (`T * mm` first, then `* ss`, then `* TiltRescale` — left-to-right, matching C#
evaluation order) to avoid float-associativity drift near those boundaries. This is a real risk
area for a naive port (e.g. computing `mm*ss*TiltRescale` first and multiplying by `T` last
could differ in the last ULP for some inputs) — flag for the enumeration script to test
op-order-preserving arithmetic specifically, not just "the same formula."

### 1.6 Clip/clamp order — exact, at every step

Uniformly: **round first (inside), clamp second (outside)** at all three steps (`T`, `Tpp`,
`tgtRaw`) — `Math.Max(lo, Math.Min(hi, (int)Math.Round(...)))`. Never clamp-then-round anywhere
in either file. `M` itself (Product A) is *not* separately clamped — only `tgtRaw =
round(clamp-free M)` is clamped; there is no intermediate clamp on `M` before the final round+clamp.

---

## 2. Product B — `src/ninjascript/SolarWaveOneContractNQ_v5.cs`

### 2.1 Decoder + hysteresis, exact lines 405–445

```csharp
int sumNext = 0;
for (int m = 0; m < NMEM; m++) sumNext += mPending[m];
int T = Math.Max(-10, Math.Min(10, (int)Math.Round(sumNext / 13.0 * 10.0, MidpointRounding.AwayFromZero)));
double mm = (sumNext != 0 && tiltState != 0 && Math.Sign(sumNext) == tiltState) ? TiltMult : 1.0;
int Tp = Math.Max(-13, Math.Min(13, (int)Math.Round(T * mm * TiltRescale, MidpointRounding.AwayFromZero)));
double M = WSolar * Tp + WBmom * bmomPos;
...
if (forceFlat) tgt = 0;
else if (p == 0) {
    if (!entryBlocked) {
        if (M >= EntryLevel) tgt = 1;
        else if (M <= -EntryLevel) tgt = -1;
    }
} else if (p > 0) {
    if (M <= -EntryLevel && !entryBlocked) tgt = -1;      // reversal
    else if (M <= ExitLevel) tgt = 0;
} else {                                                    // p < 0
    if (M >= EntryLevel && !entryBlocked) tgt = 1;         // reversal
    else if (M >= -ExitLevel) tgt = 0;
}
```
This **confirms the owner-supplied snippet verbatim**, including the hysteresis state machine
shape. One structural nuance worth flagging: the hysteresis "state" (`long`/`short`/`flat`) is
not held in a separate FSM variable — it is read fresh every bar from `PhysicalPosition()`
(actual broker/simulated position, `p`), lines 307–312 & 413. In a frictionless same-bar-fill
backtest this is extensionally identical to a shadow target-state variable, but a byte-exact
port must track *actual filled position*, not "last submitted target," if it wants to be exact
under any future friction/partial-fill model.

**`M` is never rounded or clamped anywhere in Product B** — confirmed, `double M = WSolar * Tp +
WBmom * bmomPos;` (line 410) flows directly into the `>=`/`<=` comparisons against
`EntryLevel`/`ExitLevel` with no intervening `Math.Round` or `Math.Max/Min` call. This matches
the prompt's note exactly.

**No `ss`/short-halving term anywhere in Product B** — grepped the full file: no `ss` variable,
no `ShortHalf` field, no `[NinjaScriptProperty]` for it. Confirmed absent, not merely unused.
This is a genuine, disclosed asymmetry vs Product A — preserved, not silently symmetrized.

### 2.2 Does `sign(sumNext)` vs `sign(T)` ever actually diverge? — **No, provably never.**

This was flagged in the prompt as something to check rather than assume, so it gets a full
proof rather than a hand-wave:

`T = clip(-10,10, round_away(sumNext * 10/13))`. Given `sumNext` is an integer in `[-13,13]`
(§1.2), the pre-clip value `sumNext*10/13` already lies in `[-10,10]`, so **the clip at this
step is a no-op given the actual reachable domain** (it only matters as defensive code against
domains it can't actually reach). For any nonzero `sumNext`, `|sumNext| >= 1`, so
`|sumNext*10/13| >= 10/13 ≈ 0.7692`, which is `> 0.5` — so `round_away` rounds it to a value of
magnitude `>= 1` with the **same sign** as `sumNext` (because `10/13 > 0`, multiplication
preserves sign, and round-away-from-zero never crosses zero from a value already `>0.5` in
magnitude). Conversely `sumNext=0 → T=0` exactly. Therefore:

- `sign(T) == sign(sumNext)` for every reachable `sumNext`, with no exceptions, and
- `T == 0 ⟺ sumNext == 0`.

**Consequence: Product A's `mm` condition (`T!=0 && tiltState!=0 && sign(T)==tiltState`) and
Product B's `mm` condition (`sumNext!=0 && tiltState!=0 && sign(sumNext)==tiltState`) are
mathematically extensionally identical for every reachable state** — despite being written
against different intermediate variables, they can never produce a different `mm` for the same
underlying member-vote state. **This is not a genuine asymmetry; it's a cosmetic difference in
which intermediate variable the same fact is read off.** (Directly resolves the prompt's
open question — the answer is "cannot diverge," proven, not assumed.)

### 2.3 Any other short-halving-equivalent anywhere in Product B? — No.

Searched the full 522-line file for anything gating on `T<0` combined with `tiltState`/sign
logic beyond the `mm` line above (e.g., a second multiplier, a position-size split, an
alternate threshold branch keyed on short-vs-long). None found. The only asymmetric-by-side
logic in Product B is the ordinary long/short mirror of the hysteresis thresholds themselves
(`EntryLevel`/`-EntryLevel`, `ExitLevel`/`-ExitLevel`), which is a symmetric mirror, not a
halving. Confirmed: **Product B genuinely has zero short-halving equivalent**, matching the
prompt's disclosed-asymmetry framing.

### 2.4 `EntryLevel`/`ExitLevel` defaults — the disclosed recollection discrepancy

Line 145: `EntryLevel = 3.0; ExitLevel = 1.0; // frozen seq-318, not a free parameter`.

**CONFIRMED PROMINENTLY: the actual, current, running code has `EntryLevel=3.0`,
`ExitLevel=1.0` — i.e. `hysteresis(3,1)` — matching `BASELINE_MODELS.md:469`'s own "Discrete
hysteresis(3,1)" description.** The owner's recollection of "+5/+1, -5/-1" does **not** match
the current `.cs` file. I tested against the real code values (3.0/1.0) per the directive, and
I am not silently substituting 5/1 to match the recollection, nor silently testing 3/1 without
flagging the mismatch. **This is a live discrepancy between the owner's stated recollection and
ground truth — surfaced here explicitly, as instructed, not corrected quietly.**

### 2.5 MNQ vs NQ Product B — decision-logic identity check

Diffed `SolarWaveOneContractNQ_v5.cs` against `SolarWaveOneContractMNQ_v5.cs` in full
(545 vs 522 lines). **Every difference is attributable to which series is "signal" (primary,
index 0) vs "execution" (added, index 1):**
- `NQ_v5`: trades NQ itself == the signal instrument, so signal stays primary (index 0),
  no added series is needed for execution (`Position`/`Close[0]`/`Time[0]` used directly).
- `MNQ_v5`: trades MNQ, a *different* instrument from the NQ signal, so it follows the
  `KNOWN_ERRORS_AND_CORRECTIONS.md #7`-mandated arrangement: signal (NQ) stays primary
  (index 0), MNQ execution is the ADDED series (index 1), position read via `Positions[1]`,
  `UpdateVol`/`UpdateMachine`/`Decide`/`BmomBar` all read `Closes[1][0]`/`Times[1][0]` etc.
  instead of the unindexed accessors.
- The `mm`/`Tp`/`M`/hysteresis formulas themselves (lines ~405–445 equivalent) are **byte-
  identical** between the two files modulo this series-indexing substitution — same constants,
  same operators, same branch structure, same rounding/clamp calls. **No decision-logic
  divergence found beyond the already-documented instrument/tick-size/commission-level ones.**
- One additional, purely defensive difference: MNQ_v5's `ExecWatchdog()` carries a `v3->v4`
  code comment (lines 373-380 of the MNQ file) documenting a **prior, already-fixed** bug where
  an earlier version read the wrong BarsInProgress-relative accessor and the watchdog was a
  silent no-op — this is historical/already-resolved, not a currently-live discrepancy between
  the NQ and MNQ files (both current files correctly index `Times[0][0]`/`CurrentBars[0]`
  for the decision series and `Time[0]`/`Times[1][0]` appropriately for the execution series).

### 2.6 A genuine, NOT-previously-flagged asymmetry found: `tiltState` warm-up threshold

While tracing `tiltState` for both products (to make sure it was truly identical machinery),
found a **persistent, real difference not mentioned anywhere in the task's known-facts list**:

- Product A (`SolarWaveSMMaster_v4.cs` line 347): `if (sessCloses.Count >= TiltSma)`
- Product B (`SolarWaveOneContractNQ_v5.cs` line 396, and MNQ_v5 line 421):
  `if (sessCloses.Count > TiltSma)`

This is **`>=` vs `>`** — Product A starts computing a non-zero-eligible `tiltState` one
session earlier than Product B (`Count==TiltSma`, i.e. exactly 50 sessions of history, is
sufficient for A; B requires `Count==TiltSma+1`, i.e. 51 sessions). I checked this is not a
one-off typo: grepped every versioned file in `src/ninjascript/` —
`SolarWaveSMMaster_v1/v2/v3/v4` **all** use `>=` (4/4 files), while
`SolarWaveOneContractNQ_v2/v3/v4/v5/v6_R2CONFIRM`, `SolarWaveOneContractMNQ_v2/v3/v4/v5/Final`,
`SolarWaveOneContractNQ_Final`, and `SolarWaveSMOneLot_v1` **all** use `>` (12/12 files). This
is a **stable, structural convention split between the two product lineages across their
entire version history**, not a slip in one file.

**Practical impact is bounded and almost certainly immaterial**: once both conventions are past
their respective warm-up thresholds (`Count>=51` for both, since Product A's sum window is
always exactly the most recent `TiltSma` closes regardless of how large `Count` grows), they
read from the **identical window of session closes** and produce identical `tiltState` values
thereafter. The divergence is confined to exactly one session near the very start of whatever
price history NT8 has loaded into the chart (which in practice, given the multi-year data
loaded for these strategies, is deep in pre-canonical history) — but it is real, and it means a
literal byte-exact reimplementation of Product B must NOT reuse a shared/cached Product-A-style
`tiltState` array; it needs its own, with the `>` threshold, to be exact all the way back to the
first ~50-51 sessions of loaded history. Flagging per the directive's "document, do not
silently unify" instruction — I have not corrected either file, both stand as coded.

---

## 3. Existing Python port cross-check (`runs/PRICE01_PRODUCT_A_GENUINE_MNQ/src/01_dual_truth_repricing.py`, `product_a_exec_generalized`)

Read the full script (imports from `health_substrate.py` and `sm01_solarsim.py`).

### 3.1 Product A decoder — matches, exactly

Lines 61-69 of `01_dual_truth_repricing.py`:
```python
m_arr = np.where((T_leg != 0) & (tilt_state_ != 0) & (np.sign(T_leg) == tilt_state_), TILTMULT, 1.0)
s_arr = np.where((T_leg < 0) & (tilt_state_ > 0), SHORTHALF, 1.0)
Tpp = np.clip(rha(T_leg * m_arr * s_arr * TILTRESCALE), -13, 13)
M_a = np.clip(rha(KSOLAR * Tpp + KBMOM * B_), -13, 13)
```
with `rha(x) = np.sign(x) * np.floor(np.abs(x) + 0.5)` (the standard round-half-away-from-zero
formula) and constants `KSOLAR, KBMOM, TILTRESCALE, TILTMULT, SHORTHALF = 0.728654, 2.934159,
0.9026, 1.25, 0.5` (line 53) — **byte-identical constants to the `.cs` defaults** (§1). This
independently derived-from-the-`.cs`-file formula (my own read, §1.1) and this pre-existing
Python port are **structurally identical**: same `mm`/`ss` gating conditions, same clamp bounds,
same round-then-clamp order, same operand order inside the rounding call. **No discrepancy
found between my from-scratch `.cs` reading and this existing Python port, for the Product A
decoder specifically** (the one function the task named).

`T` itself is supplied into this function from `health_substrate.py` line 52:
`T = sm.e10_target(PEND).astype(int)`, where `e10_target` (in
`src/analytics/sm01_solarsim.py` lines 303-309) computes `m = member_pos.mean(axis=1)*10; tgt =
sign(m)*floor(abs(m)+0.5); clip(tgt,-10,10)`. Since `member_pos.mean(axis=1)*10 ==
sumNext/13*10` exactly (mean of 13 columns times 10 == sum/13*10), **this independently
confirms the `sumNext` formula (§1.2) end-to-end through the Python port too.**

### 3.2 A genuine discrepancy DOES exist — in the shared `tiltState`, for Product B only

`health_substrate.py` computes a **single, shared** `tilt_state` array (lines 54-57):
```python
sclose = bars.loc[bars["is_last_of_sess"], ["sess_date", "close"]].set_index("sess_date")["close"]
tilt_by_date = np.sign(sclose - sclose.rolling(50).mean()).shift(1).to_dict()
```
`pandas.Series.rolling(50).mean()` defaults `min_periods=window=50`, so it first produces a
non-NaN value once exactly 50 session-closes are available — this is the **Product-A `>=`
convention** (§1.3/§2.6), not Product B's own `>` convention. This same `tilt_state` array is
then reused for **both** legs in this script family: it feeds Product A's `T`/`mm` (via
`01_dual_truth_repricing.py`, matches, per §3.1) **and** it feeds `health_substrate.py`'s own
Product B `M` computation at lines 105-107 (`m_arr = np.where((T!=0)&(tilt_state!=0)&
(np.sign(T)==tilt_state), TILTMULT,1.0); Tp=np.clip(rha(T*m_arr*TILTRESCALE),-13,13); M=WSOLAR*Tp
+WBMOM*np.asarray(B)`).

**So: the existing Python infrastructure's Product-B `M` calculation silently uses the
Product-A-style (`>=`, 50-session) `tiltState` warm-up, not Product B's own `.cs`-coded
(`>`, 51-session) warm-up.** This is a real, if practically tiny (one session, deep in loaded
history, per §2.6), discrepancy between the `.cs` ground truth and the existing Python
tooling — reported per the directive, not silently reconciled. It does not affect the
Product-A-only cross-check the task specifically named (§3.1 matches cleanly), but it is
exactly the kind of finding item 3 asked to surface if found while tracing the surrounding
infrastructure.

### 3.3 Not independently re-verified (out of scope for this pass, flagged for the next phase)

`sm.member_states` / `sm.member_trades` (the per-member anchor/flip/pending state machine that
produces `PEND`, in `src/analytics/sm01_solarsim.py`) were **not** line-by-line diffed against
`UpdateMachine()`/`Decide()` in the `.cs` files in this pass — I only confirmed the *shape*
(13 columns, `{-1,0,1}` pending values via `build_pend` in
`runs/W18R1_M1_VOLSEASON/src/common.py`) matches by construction/typing, not by re-deriving the
volatility-anchor arithmetic itself. If the next phase's enumeration needs bar-level pending-
state parity (not just the T/Tpp/M decoder), that function pair should get the same full-read
treatment this note gave the decoder.

---

## 4. Summary answers to the specific open questions posed

- **`sumNext`**: simple integer sum of 13 members' `{-1,0,1}` pending votes. Range `[-13,13]`,
  all integers reachable in principle.
- **`tiltState`**: `Math.Sign(...)` → exactly `{-1,0,1}`. Two different, persistent warm-up
  thresholds across the codebase (Product A `>=TiltSma`, Product B `>TiltSma`) — a real,
  previously-undocumented (in the task's known-facts) asymmetry, materially inert after warm-up.
- **`bmomPos`**: genuinely finite, `{-1,0,1}`, `int`-typed in both `.cs` and the Python twin.
  The "is 4B even well-posed as a finite-state hypothesis" question resolves to **yes**.
- **Rounding**: `Math.Round(double, MidpointRounding.AwayFromZero)`, no banker's-rounding
  anywhere; `T`'s midpoint case never actually arises given `sumNext`'s integer domain; `Tpp`/
  `tgtRaw` can land near genuine `.5` boundaries and need exact left-to-right operation-order
  replication in any port.
- **Clip/round order**: round first, clamp second, uniformly, at every step, in both products.
- **`sign(sumNext)` vs `sign(T)` in Product B's `mm`**: **provably never diverge** — cosmetic
  variable choice, not a genuine asymmetry. Proved from `T`'s construction, not assumed.
- **Product B `ss`/short-halving**: confirmed genuinely absent, no equivalent anywhere.
- **MNQ vs NQ Product B**: decision logic byte-identical modulo signal/execution series
  indexing; no undocumented logic divergence found.
- **EntryLevel/ExitLevel**: code has `(3.0, 1.0)`, matching `BASELINE_MODELS.md`'s
  "hysteresis(3,1)"; does **not** match the owner's recalled "+5/+1, -5/-1" — flagged
  prominently, tested against the real code value per instruction.
- **Existing Python port** (`product_a_exec_generalized`): matches the `.cs` Product A decoder
  exactly, constants and all. A separate, real discrepancy was found in the *shared*
  `health_substrate.py` `tiltState` array's warm-up convention as applied to **Product B's** M
  calculation (uses Product A's `>=` convention, not Product B's own `.cs` `>` convention) —
  surfaced, not silently fixed.
