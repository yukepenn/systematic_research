# VF_SIGNAL_GENERATOR_v2 — LAYER A specification (indicator, pure function)

**Written** 2026-08-24 under MASTER DIRECTIVE v4.0 §22 (corrected two-layer architecture).
**Companion:** `VF_WRAPPER_v2.md` (Layer B, regression plan, provisional-conclusion list).
**This file is a SPECIFICATION, not code.** No `.py` file was modified, no backtest was run,
nothing in `original_screenshot/` was touched. Every quotation below was re-extracted from
`ninZaVWAPFlux-TraderManual.pdf` (SHA-256 `d34b50daa2db4caa28077efdccc6427263b57bdd0fd84ddc422b9d96e500390b`)
in this pass with `pdftotext -layout`, read-only.

**Status vocabulary, one token per claim:** FACT / REPRODUCED / INFERENCE / UNKNOWN /
FALSIFIED. Observation and interpretation are never combined in one sentence. Backtest P&L
and §40 distance are **never** admissible as selectors of a vendor semantic.

---

## 1. The defect this specification corrects

### 1.1 Vendor semantics (FACT, verbatim, re-extracted this pass)

Manual §2.11, p.10:

> "Signal Quantity Per Trend": Specifies the maximum number of trade signals allowed
> to appear within the same support or resistance zone.
>
> For example, if Signal Quantity Per Trend = 4, it means that only 4 same-direction signals are
> allowed to appear within a single trend.
> Note: It is not recommended to set this value too high. When price repeatedly tests the same
> support or resistance zone, the reliability of signals generated at that zone gradually
> decreases. Limiting the number of signals per trend helps prevent over-trading within a single
> trend.

Manual §2.13, p.11:

> "Signal Split (Bars)": Specifies the minimum bar distance required between two
> consecutive signals in the same direction.
>
> For example, in the illustration above, if Signal Split (Bars) = 30, it means the current Buy
> signal must be at least 30 bars away from the previous Buy signal.

Manual §4, p.15 (the vendor's own architecture instruction):

> You can rely on the signals below to build your own strategy:
> • Signal Trend: 1 = bullish, -1 = bearish
> • Signal Trade: 1 = bullish, -1 = bearish

**FACT.** Both suppression parameters are defined over **signals**, in an object the vendor
calls "the indicator", whose output the vendor then tells the customer to consume from a
separately-authored strategy. Nothing in the manual makes either parameter aware of a
position, an order, a fill, or an account. This was already recorded correctly in
`VENDOR_SIGNAL_USAGE_MODEL.md` Layer-C item 2 ("Signal suppression is Layer A, not Layer C").

### 1.2 What our code actually does (FACT, code audit, `run_r7_signal_id.py`)

`run_member()` maintains `cnt = {1: 0, -1: 0}` and `last_sig = {1: …, -1: …}` and advances
them at exactly **two** sites:

- line 147 — inside the `X_OPP` exit branch, when a stop-and-reverse actually happens;
- line 154 — inside the entry branch, guarded by `if pos == 0 and sig != 0 and pe == 0`.

`run_r7b_signal_id.py` inherits the identical coupling (lines 101, 107).

**FACT.** Therefore `cnt` and `last_sig` count **executed entries and reversals**, not
signals. A bar that satisfies trend + rail touch + close confirmation + the CLV filter while
the wrapper is already in a position produces `sig != 0`, passes or fails the gate, and then
falls through to the entry branch, where `pos != 0` blocks it — and the counters never move.
It leaves no trace anywhere: `run_member` returns only `trades`, and the run directory
(`runs/OTR_R7_VF_SIGNAL_ID/out/`) contains only `r7_grid.csv`, `r7_summary.csv`,
`r7b_grid.csv`, `r7b_summary.csv` — per-window aggregates and per-member trade totals.

**FACT.** No stored artifact in the campaign contains a VF **signal** count. Every number we
have ever quoted as "signal density" is a **trade** count.

### 1.3 The four consequences (INFERENCE, each traced to the code above)

1. **The `QtyPerTrend` cap is systematically under-consumed.** Under the vendor semantics the
   budget of 3 is spent by signals *appearing*; under ours it is spent only by signals
   *traded*. A trend episode in which the wrapper is occupied can never exhaust the cap.
2. **The `Split` clock is systematically stale.** `last_sig` holds the last *traded* bar, so
   the "minimum bar distance between two consecutive signals" is measured from the wrong
   event; the gate `(i - last_sig) < SPLIT` therefore blocks less often than the vendor rule.
3. **Both errors run in the same direction: our suppression is too weak.** Whatever signal
   density the vendor's rule would produce, ours produces a *differently* thinned stream that
   no setting of `QtyPerTrend` or `Split` can reproduce — because the error is in *which
   events advance the state*, not in the thresholds. **It cannot be fixed by tuning.**
4. **The error is entangled with the exit.** In `run_r7_signal_id.py` the `X_OPP` exit tests
   `sig == -pos` **after** the gate has already zeroed `sig` (lines 132-134 precede 137-147),
   so a suppression state that is itself position-dependent decides whether a reversal
   happens. Signal generation, suppression and execution are one closed loop. This is the same
   defect class as the single `tr` array documented in `TREND_MODEL_ADJUDICATION.md` §0.

### 1.4 What is NOT claimed here

- **UNKNOWN** whether the vendor's own build counts pre- or post-`Split` candidates against
  the `Qty` budget, resets per zone or per trend, or uses one counter or two (§4).
- **UNKNOWN** whether the *trader's* build carries vendor semantics for these fields at all —
  under H3/H4 (`EV039_REAUDIT.md` Part D, all five hypotheses live) his `Signal Split (Bars)`
  need not mean what ninZa's means.
- This document does not claim the corrected architecture will fit better. Fit is not the
  argument and may not become the argument (`CLOSE_THRESHOLD_ADJUDICATION.md` §0).

---

## 2. Architecture

```
                 ┌──────────────────────────── LAYER A — INDICATOR ────────────────────────────┐
  bars ─────────►│ vf_layers ──► vf_rails ──► fair_value                                       │
  panel ────────►│      │            │                                                          │
  semantics ────►│      ▼            ▼                                                          │
  zones (opt) ──►│  vf_trend ──► signal_trend (±1 / ±2)     vf_cum_delta ──► signal_cum_delta   │
                 │      │                    │                     │                            │
                 │      └────────► vf_trade_raw ◄──────────────────┘                            │
                 │                     │  raw candidates                                        │
                 │                     ▼                                                        │
                 │            vf_suppress  ← Qty budget + Split clock live HERE                 │
                 │                     │      (advanced by EVERY emission, never by a trade)    │
                 └─────────────────────┼────────────────────────────────────────────────────────┘
                                       ▼  VFIndicatorOutput  (frozen, read-only)
                 ┌──────────────────── LAYER B — STRATEGY WRAPPER ─────────────────────────────┐
                 │ enter / decline / reverse / exit / stop / session-flat / risk               │
                 │ NO write path back into Layer A. See VF_WRAPPER_v2.md                       │
                 └────────────────────────────────────────────────────────────────────────────┘
```

**The one-way rule (binding).** `vf_indicator` has no parameter, field, or side channel that
could carry position, PnL, order or account state. `vf_wrapper` receives a fully-computed,
immutable `VFIndicatorOutput` and may only read it. Enforcement is specified in §8.

---

## 3. Data contracts and exact signatures — LAYER A

All arrays are 1-D of length `n` and index-aligned to `bars.time` unless a shape is given.
`np.nan` marks "not computable"; sentinel `0` in an integer state series marks "not valid"
and appears **only** where `valid[i] == False` (§5.3).

### 3.1 Input: bars

```python
@dataclass(frozen=True)
class Bars:
    time:   np.ndarray  # datetime64[s], strictly increasing, exchange-session time (ET)
    open:   np.ndarray  # float64
    high:   np.ndarray  # float64
    low:    np.ndarray  # float64
    close:  np.ndarray  # float64
    volume: np.ndarray  # float64  (contract volume; UNIT volume only if volume_base is UpDownTick_UnitVolume)
    bid_volume: np.ndarray | None = None   # None ⇒ BidAskPrice_RealVolume is NOT computable (§3.2 note)
    ask_volume: np.ndarray | None = None
    session_first: np.ndarray = None       # bool, True on the first bar of an NQ session (18:00 ET)
    session_last:  np.ndarray = None       # bool, True on the last bar of an NQ session (17:00 ET)
```

**Contract.** `session_first` / `session_last` are computed once, by
`research_sdk/session_boundary.py` conventions, and passed in — Layer A never re-derives
session structure from gap heuristics. (R7 derives them inline from a >60-minute gap test,
`run_r7_signal_id.py` lines 168-170; that heuristic is retained only as a fallback and must
be recorded in the run spec when used.)

### 3.2 Input: the vendor panel (the 13 fields, plus the separately-grouped 14th)

```python
@dataclass(frozen=True)
class VFPanel:
    volume_base:                str   # 'BidAskPrice_RealVolume'|'UpDownTick_RealVolume'|'UpDownTick_UnitVolume'
    anchor_period_min:          int   # trader: 60
    vwap_amount:                int   # trader: 5
    trend_period:               int   # trader: 20
    trend_ma_type:              str   # trader: 'EMA'
    level_max_pct:              float # trader: 95
    level_upper_pct:            float # trader: 75
    level_median_pct:           float # trader: 50
    level_lower_pct:            float # trader: 25
    level_min_pct:              float # trader: 5
    signal_qty_per_trend:       int   # trader: 3
    signal_close_threshold_pct: float # trader: 10
    signal_split_bars:          int   # trader: 5
    # --- NOT one of the 13; sits under a separate "General" group in the vendor's own panel
    #     (FACT, EV039_REAUDIT.md A.2) and is ABSENT from every trader frame (FACT, V-010) ---
    zone_period: int | None = None    # None ⇒ zone module disabled; UNKNOWN for the trader
```

- **FACT.** The trader's values, frozen 2026-02-13 → 2026-08-14, are
  `BidAskPrice_RealVolume / 60 / 5 / 20 / EMA / 95 / 75 / 50 / 25 / 5 / 3 / 10 / 5`
  (EV-019, V-001/V-002/V-003; label-confirmed in OTRIMG-0146).
- **Precondition (contract).** `level_max_pct ≥ level_upper_pct ≥ level_median_pct ≥
  level_lower_pct ≥ level_min_pct`. Plot names are bound by NAME, not by sort order; a
  non-monotone panel is **undefined behaviour** and must raise, not silently re-sort.
- **Note on `volume_base`.** Manual §2.1 defines `BidAskPrice_RealVolume` per tick against
  bid/ask. On 1-minute bars that classification is not available; every VF run to date uses a
  bar-data stand-in. The stand-in **must be named in `VFSemantics.delta_proxy`** (§3.3) and
  must never be silently labelled `BidAskPrice_RealVolume`.

### 3.3 Input: the unsettled semantics (nothing may default silently)

```python
@dataclass(frozen=True)
class VFSemantics:
    # --- cloud geometry: UNKNOWN as a class (V-024, VF_ARCHITECTURE_REOPEN.md) ---
    lifecycle:      str   # 'L1a'|'L1b'|'L1c'|'L2a'|'L2b'|'L3a'|'L3b'|'L4'
    rail_formula:   str   # 'F1'|'F1x'|'F2'|'F3'     (F1x NOT IMPLEMENTED — build gap)
    price_input:    str   # 'close'|'hlc3'           (V-029 UNKNOWN)
    # --- trend (TREND_MODEL_ADJUDICATION.md §4-§5) ---
    trend_direction: str  # 'TD-0'..'TD-6'
    trend_strength:  str  # 'TS-0'|'TS-1'|'TS-2'|'TS-3'
    # --- trade trigger ---
    pullback:        str  # 'P_IN'|'P_Q75'|'P_MED'   (U2, UNKNOWN)
    close_confirm:   str  # 'C_DIR'|'C_REC'
    close_cell:      str  # 'C1'|'C2'|'C3'|'C4'      (= H1c | H1b | H-FIGURE | H1a)
    # --- suppression (§4 of this file; the manual does not settle any of these) ---
    qty_reset:       str  # 'QR-1'..'QR-7'
    qty_scope:       str  # 'QD-DIR'|'QD-BOTH'
    qty_consume:     str  # 'QC-EMIT'|'QC-CANDIDATE'
    split_scope:     str  # 'SS-GLOBAL'|'SS-EPISODE'|'SS-SESSION'
    suppress_order:  str  # 'SO-SPLIT-FIRST'|'SO-QTY-FIRST'
    # --- inputs and version ---
    delta_proxy:     str  # 'sign(close-open)*volume' | 'bidask_tick' | 'updowntick' | 'none'
    build_date:      datetime.date   # the vendor build being modelled — gates §7 version rules
```

**Contract.** `VFSemantics` has **no defaults**. Every field must be supplied explicitly by
the run spec and echoed into `runs/<run_id>/spec.yaml` before results are read. A semantic
choice that is not in the spec file did not happen.

### 3.4 Optional input: the zone module

```python
@dataclass(frozen=True)
class ZoneSeries:
    zone_id:    np.ndarray  # int64 per bar, -1 = no active zone
    zone_hi:    np.ndarray  # float64, NaN where zone_id == -1
    zone_lo:    np.ndarray  # float64
```

**Status: NOT IMPLEMENTED, and required by `QR-4`/`QR-5`.** Manual §2.14, verbatim:

> "Zone Period" defines the cycle used by the indicator to identify static S/R zones.
>
> A higher value results in fewer S/R zones, as stronger price movement over a longer cycle is
> required for a zone to form.
>
> Conversely, a lower value produces more frequent S/R zones.

The construction ("derived from major swing highs and lows", manual §1) is **UNKNOWN** in
detail. Passing `zones=None` is legal and forces `qty_reset ∈ {QR-1, QR-2, QR-3, QR-6, QR-7}`;
selecting `QR-4`/`QR-5` with `zones=None` must raise, not fall back.

### 3.5 Output

```python
@dataclass(frozen=True)
class VFIndicatorOutput:
    # ---- geometry ----
    layers:      np.ndarray  # (n, vwap_amount) float64 — RAW layer VWAPs, ascending-sorted per bar,
                             #   NaN before the population is complete. NEW: never exposed before.
    layer_age:   np.ndarray  # (n, vwap_amount) int64 — bars since each sorted layer's birth, -1 if NaN
    rails:       np.ndarray  # (n, 5) float64, column order [Min, Lower, Median, Upper, Max]
    fair_value:  np.ndarray  # (n,) float64 == rails[:, 2]   (manual §2.8: FairValue ≡ the Median rail)
    # ---- vendor state series ----
    signal_trend:     np.ndarray  # int8; {+1,-1} for build_date < 2026-02-24, {+2,+1,-1,-2} after.
                                  #   0 ONLY where valid == False.  (No 0 in either vendor alphabet — FACT)
    signal_cum_delta: np.ndarray  # int8 {1,-1,0}; all-zero where build_date < 2026-02-09 (series did not exist)
    signal_trade:     np.ndarray  # int8 {1,-1,0} — THE EMITTED STREAM, post-suppression. This is the
                                  #   series a vendor wrapper reads. Emission is position-independent.
    # ---- audit surface (NEW — this is exactly what the defect made unobservable) ----
    signal_trade_raw: np.ndarray  # int8 {1,-1,0} — candidates BEFORE Qty/Split suppression
    suppress_reason:  np.ndarray  # int8: 0 not-suppressed, 1 qty-cap, 2 split, 3 both, 4 invalid-bar
    episode_id:       np.ndarray  # int64 — the Qty-reset episode this bar belongs to (per §4)
    qty_used:         np.ndarray  # (n, 2) int32 — running budget per direction [long, short] at bar close
    bars_since_emit:  np.ndarray  # (n, 2) int32 — bars since the last EMITTED same-direction signal
    valid:            np.ndarray  # bool — rails computable AND warm-up complete
    # ---- provenance ----
    panel:      VFPanel
    semantics:  VFSemantics
    input_hash: str          # sha256 over (bars, panel, semantics) — see §8
```

**Post-conditions (assertable without any market knowledge):**

- `signal_trade[i] != 0  ⇒  signal_trade_raw[i] == signal_trade[i]` (suppression never invents).
- `signal_trade_raw[i] != 0 and signal_trade[i] == 0  ⇔  suppress_reason[i] in (1, 2, 3)`.
- `valid[i] == False  ⇒  signal_trend[i] == 0 and signal_trade_raw[i] == 0`.
- `signal_trend[i] == 0  ⇒  valid[i] == False` (the alphabet has no 0 — FACT, manual §4 and
  the current product page both; `TREND_MODEL_ADJUDICATION.md` §5.1).
- Every array is `writeable = False`.

### 3.6 The top-level signature

```python
def vf_indicator(bars: Bars,
                 panel: VFPanel,
                 semantics: VFSemantics,
                 zones: ZoneSeries | None = None) -> VFIndicatorOutput:
    """PURE. Deterministic. Knows nothing about positions, orders, fills, PnL or accounts.

    FORBIDDEN in this signature, forever: position, equity, trade list, fill price,
    account, contract count, stop level, risk state, or any object derived from them.
    """
```

### 3.7 The internal sub-functions (each independently testable)

```python
def vf_layers(time, price, volume, period_min, amount, lifecycle) -> (layers, layer_age)
def vf_rails(layers, pcts, formula) -> rails                    # pcts ordered [min, lower, median, upper, max]
def vf_trend(bars, rails, fair_value, panel, semantics) -> signal_trend      # ±1 / ±2, latched, no 0
def vf_cum_delta(bars, panel, semantics) -> signal_cum_delta                 # {1,-1,0}
def vf_trade_raw(bars, rails, signal_trend, signal_cum_delta, panel, semantics) -> signal_trade_raw
def vf_suppress(signal_trade_raw, episode_id, panel, semantics, bars) \
        -> (signal_trade, suppress_reason, qty_used, bars_since_emit)
def vf_episodes(signal_trend, zones, semantics, bars) -> episode_id          # §4
```

**`vf_suppress` is the heart of this specification.** Its signature contains no position
argument and no trade argument, and it is called exactly once per `vf_indicator` call, before
any wrapper exists. That single fact is the whole correction.

Reference semantics for `vf_suppress` (stated as a rule, not as code):

```
for each bar i in order:
    d = signal_trade_raw[i]
    if d == 0: continue
    split_ok = (i - last_emit[d]) >= panel.signal_split_bars          # §2.13 "at least N bars away"
    qty_ok   = qty_used[episode_id[i]][key(d)] < panel.signal_qty_per_trend
    (order of evaluation and of budget consumption governed by semantics.suppress_order
     and semantics.qty_consume — §4.3, §4.4)
    if split_ok and qty_ok:
        signal_trade[i] = d
        last_emit[d] = i
        qty_used[episode][key(d)] += 1        # ← advances on EMISSION, unconditionally
    else:
        suppress_reason[i] = 1|2|3
```

**Binding contract, stated in the language of the defect:** the counter advances when the
indicator **emits** a signal. It advances when the wrapper is flat, when the wrapper is
already long, when the wrapper is already short, when the wrapper declines the signal for any
reason, and when no wrapper exists at all.

---

## 4. `QtyPerTrend` — the reset rule as an explicit rival set

### 4.1 Why a rival set is mandatory (FACT)

The manual contradicts itself inside §2.11. The **definition** sentence scopes the cap to a
**zone**: "the maximum number of trade signals allowed to appear within the same support or
resistance zone." The **example** sentence scopes it to a **trend**: "only 4 same-direction
signals are allowed to appear within a single trend." The **Note** uses both in consecutive
clauses ("When price repeatedly tests the same support or resistance zone … Limiting the
number of signals per trend"). The parameter's own **name** says trend.

**FACT: the vendor document does not determine the reset rule of its own parameter.** This is
the same failure mode already established for `Signal Close Threshold`
(`CLOSE_THRESHOLD_ADJUDICATION.md` §3.2) and it is recorded in
`CLAIM_REGISTRY_2026.csv` terms as UNKNOWN, not as a modelling choice.

Additional structural fact: the manual's §4 alphabet is 2-state (`1 = bullish, -1 = bearish`)
and the current product page's is 4-state (`2 / 1 / -1 / -2`). A rule that resets on "a change
in the trend state" therefore means **different things in different builds** — which is why
QR-2 and QR-3 must be separated (they are indistinguishable in every stored R7/R7b result,
because `tr` there carries only two values).

### 4.2 Axis 1 — the reset boundary (`qty_reset`)

| id | reset when… | episode = | vendor warrant | requires | status |
|---|---|---|---|---|---|
| **QR-1** RUN | the `signal_trend` **value** changes (any change, including ±1 ↔ ±2) | maximal run of a constant trend value | §2.11 example sentence ("within a single trend"), read as "while the trend series holds one value" | — | **what R7/R7b implement** (`if ti != prev_tr`, lines 111-113 / 68-70), and under the 2-state series in those runs it is indistinguishable from QR-2 and QR-3 |
| **QR-2** FLIP | `sign(signal_trend)` changes (+ ↔ −) | maximal run of a constant trend **sign** | §2.11 example, read as "while the market is in one directional trend" | — | UNKNOWN. **Differs from QR-1 only for a 4-state build**, i.e. only from 2026-02-24 |
| **QR-3** STRENGTH | `|signal_trend|` changes (weak ↔ strong) **also** resets, in addition to sign | run of constant (sign, strength) | none in the manual — the manual's build has no strength | — | UNKNOWN, and **anachronistic before 2026-02-24** (§7). Included because QR-1's literal code behaviour *becomes* QR-3 the moment a 4-state series is supplied |
| **QR-4** ZONE | the active `zone_id` changes | one static S/R zone | §2.11 **definition** sentence — the strongest single textual warrant | `ZoneSeries` | UNKNOWN, **NOT IMPLEMENTABLE today** (§3.4). Note: under QR-4 a trend flip does **not** reset the budget |
| **QR-5** ZONE×TREND | either the zone or the trend sign changes | (zone_id, trend sign) pair | the §2.11 Note, which names both in one breath | `ZoneSeries` | UNKNOWN, NOT IMPLEMENTABLE today. Strictest member |
| **QR-6** ROLLING | never resets; the cap is "at most `Qty` emissions in the trailing `W` bars" | n/a | **none** | a free constant `W` | **control only.** Violates the zero-free-constant rule of `TREND_MODEL_ADJUDICATION.md` §3; run it to bound the family, never to fit |
| **QR-7** SESSION | `session_first[i]` | one NQ session | **none** | — | **control only.** Included because our wrapper flattens at every session close, which makes QR-7 look attractive for the wrong reason |

**Ranking on warrant, not on fit:** QR-4 carries the definition sentence; QR-1/QR-2 carry the
example sentence; QR-5 carries the Note; QR-3 carries nothing textual but is the literal
behaviour of the incumbent code under a 4-state series; QR-6/QR-7 carry nothing and are
controls. **No member may be selected by §40 distance.**

### 4.3 Axis 2 — counter scope (`qty_scope`)

| id | rule | vendor warrant |
|---|---|---|
| **QD-DIR** | two independent budgets, one per direction | §2.11 **example**: "only 4 **same-direction** signals"; consistent with §2.13's same-direction split. **What R7 implements** (`cnt = {1: 0, -1: 0}`) |
| **QD-BOTH** | one shared budget for both directions | §2.11 **definition**: "the maximum number of **trade signals**" — unqualified by direction |

**FACT.** These two readings come from two consecutive sentences of the same paragraph. The
axis is therefore forced, not invented, and it is **orthogonal** to QR-*: the full rival set is
the product QR-* × QD-*.

### 4.4 Axis 3 — what consumes the budget (`qty_consume`)

| id | rule | note |
|---|---|---|
| **QC-EMIT** | only an emitted signal decrements the budget; a Split-blocked candidate does not | Reads "allowed to **appear**" as "appear on the chart". **What R7 implements**, and the reading this spec treats as the default |
| **QC-CANDIDATE** | any qualifying candidate consumes budget, even one the Split gate suppresses | Reads the cap as a limit on *tests of the zone* rather than on *drawn markers* |

Interacts with `suppress_order`: `SO-SPLIT-FIRST` (evaluate Split, then Qty — R7's effective
order given its single combined `or` test and emit-only increment) versus `SO-QTY-FIRST`.
Under `QC-EMIT` the order is immaterial; under `QC-CANDIDATE` it changes the result.

### 4.5 The `Split` clock — scope rivals (`split_scope`)

Manual §2.13 attaches **no** episode qualification to the split; it is a bare distance between
consecutive same-direction signals.

| id | rule | vendor warrant | status |
|---|---|---|---|
| **SS-GLOBAL** | one `last_emit` per direction for the whole series; never reset | the literal §2.13 sentence | **default**; matches R7's *structure* (R7 never resets `last_sig`), though not its *content* |
| **SS-EPISODE** | `last_emit` resets at each `episode_id` boundary | none | rival, recorded because the two suppressors otherwise interact across episode walls |
| **SS-SESSION** | `last_emit` resets at `session_first` | none | rival; **the only one that matters for the trader's `Split = 5`**, where a 5-bar clock rarely survives an overnight gap anyway |

**Comparator (FACT):** "at least 30 bars away" ⇒ emit iff `i - last_emit >= split_bars`. R7's
`(i - last_sig) < SPLIT → suppress` is the same comparator and is **correct**; only the event
it measures from is wrong.

### 4.6 The one rule that is NOT a rival

**Binding, not a candidate:** whichever QR/QD/QC/SS combination is selected, the counters and
the clock are advanced by **emissions of `vf_suppress`**, never by an entry, a reversal, a
fill, or any wrapper decision. That is the correction; it is not part of the search space.

---

## 5. The rest of Layer A — pinned versus open

### 5.1 Pinned by the manual (FACT)

| object | vendor sentence (verbatim, this pass) | consequence for Layer A |
|---|---|---|
| VWAP Amount | "Defines the number of recent VWAP layers used to construct the VWAP bands … if VWAP Amount = 5, the indicator will use the five most recent VWAP layers to calculate the Highest, Upper, Median, Lower, and Lowest levels." | `layers` has exactly `vwap_amount` columns; the five rails are a function of that population and of nothing else |
| Fair Value | §2.8: "'Level: Median (%)': defines the threshold for the Fair Value plot within the VWAP bands." | `fair_value ≡ rails[:, 2]`. (V-038 records a live rival family in which FVP is a separately-computed object; if that is ever adopted, this identity must be broken explicitly, not quietly) |
| Trend Period | §2.4: "'Trend Period': defines the averaging period of price used to determine the market trend." | the MA smooths **price**; it may never touch cloud geometry. Changing `trend_period` must leave `layers` and `rails` bit-identical — an assertable unit test |
| Trend MA Type | §2.5: "The moving average type (can choose from 11 popular moving-average types)" | `trend_ma_type` is an enum, not a boolean; trader's value EMA (FACT, OTRIMG-0146) |
| trade signals | §1 bullet: "Trade signals (pullback signals)" | the trigger family is a *pullback* family; this is the only public word we have for it |
| the five plots | §1 bullet: "The VWAP Bands are formed by 5 primary plots: Max [glyph] Upper [glyph] Median [glyph] Lower [glyph] Low." (the separator is an unmapped symbol-font glyph; rendered here as `[glyph]`) | **FACT, new this pass:** §1 names the bottom plot **"Low"** while §2.10 names the parameter **"Level: Min (%)"**. Recorded, not resolved; the array column is named `Min` after the parameter |

### 5.2 Open, and carried as `VFSemantics` fields

| field | rival set | adjudication document |
|---|---|---|
| `lifecycle` | L1a/L1b/L1c · L2a/L2b · L3a/L3b · L4 | `VF_ARCHITECTURE_REOPEN.md` §1 — class is **UNKNOWN** (V-024) |
| `rail_formula` | F1 percentile-linear · F1x exclusive/NIST (**not implemented**) · F2 nearest-rank · F3 min-max (disfavoured lifecycle-invariantly, §3.4 there) | same, §3 |
| `price_input` | close · hlc3 | V-029 UNKNOWN |
| `trend_direction` | TD-0 … TD-6 | `TREND_MODEL_ADJUDICATION.md` §4 |
| `trend_strength` | TS-0 … TS-3 | same, §5.2 |
| `close_cell` | C1 (=H1c) · C2 (=H1b) · C3 (=H-FIGURE, **never tested**) · C4 (=H1a) | `CLOSE_THRESHOLD_ADJUDICATION.md` §3 |
| `pullback`, `close_confirm` | P_IN/P_Q75/P_MED × C_DIR/C_REC | U2, UNKNOWN; §2.12's worked figure bears on it (`TREND_MODEL_ADJUDICATION.md` §9) |
| `qty_reset`, `qty_scope`, `qty_consume`, `split_scope`, `suppress_order` | §4 above | **this document** |

### 5.3 Warm-up and validity

- `valid[i] = (rails[i] all finite)`. Under L1b/L2b that is the first bar at which the
  population reaches `vwap_amount` members with positive volume (`vf_core.vf_levels` line 70).
- **The warm-up `0` trend state of R7 is not admissible** (`TREND_MODEL_ADJUDICATION.md` §3):
  the vendor alphabet has no 0. Layer A must therefore either (a) leave `valid=False` and emit
  no signals until the first classification is possible, or (b) apply a declared
  first-classification rule. Choice (a) is the default; (b) requires a `VFSemantics` field if
  ever used. Under **no** circumstances may a 0 state appear where `valid == True`.

---

## 6. Invariants and unit tests (deterministic; none uses market data)

**I1 — purity.** `vf_indicator(bars, panel, sem)` called twice returns bit-identical arrays.

**I2 — position-independence (the defect test).** For any two wrapper configurations `cfgA`,
`cfgB`: run `vf_indicator` once, run `vf_wrapper` under both, then assert
`sha256(ind) == input_hash` unchanged and `signal_trade` bit-identical. **Under the R7
architecture this test cannot even be written**, because there is no `signal_trade` array —
that is the diagnostic value of the test.

**I3 — cloud/trend orthogonality.** Varying `trend_period` or `trend_ma_type` leaves
`layers`, `rails`, `fair_value` bit-identical.

**I4 — cap saturation.** For any synthetic bar series and any `QR`/`QD`, the number of emitted
signals of one direction inside one `episode_id` is `≤ signal_qty_per_trend`, exactly, with no
dependence on any wrapper.

**I5 — split spacing.** Consecutive same-direction emissions satisfy
`i₂ - i₁ >= signal_split_bars`, exactly, with no dependence on any wrapper.

**I6 — monotonicity of suppression.** Increasing `signal_split_bars` or decreasing
`signal_qty_per_trend`, all else fixed, cannot increase the emitted count. (Under the R7
architecture this is **not** guaranteed, because suppression feeds the `X_OPP` exit, which
changes position occupancy, which changes what gets counted — a second, independent symptom of
the closed loop.)

**I7 — alphabet conformance.** `set(signal_trend[valid]) ⊆ {+1,-1}` for
`build_date < 2026-02-24` and `⊆ {+2,+1,-1,-2}` on or after; `0 ∉ signal_trend[valid]`.

**I8 — version gating.** `build_date < 2026-02-09 ⇒ signal_cum_delta` is all-zero and any
semantics that reads it must raise (`TS-1`/`TS-2` are unavailable before that date).

**I9 — adversarial rails.** Retain `vf_core._tests()`'s population `[100,101,102,103,140]`:
F1→103.0, F2→103.0, F3→130.0 at p=75 (REPRODUCED, V-032). Add the F1x cell once implemented.

---

## 7. Version discipline (binding, inherited from `run_r7b_signal_id.py`)

| window | `signal_trend` alphabet | `signal_cum_delta` | admissible `trend_strength` |
|---|---|---|---|
| 2026-01-11 → 2026-02-08 | {+1, −1} | **does not exist** | TS-0 only |
| 2026-02-09 → 2026-02-23 | {+1, −1} | available | TS-0 only (no strength state exists in the series) |
| 2026-02-24 → present | {+2, +1, −1, −2} | available | TS-0 / TS-2 / TS-3 (TS-1 carries a free constant) |

**Credit and requirement (FACT).** `run_r7b_signal_id.py` already implements this correctly
(`UPGRADE = 2026-02-24`, gate applied only where `post[i]`, lines 24 and 90-92). Layer A must
enforce it at the type level: a semantics/`build_date` pair that is anachronistic raises.

**Consequence for QR-3.** A strength-triggered reset cannot exist before 2026-02-24. The
trader's first visible VF panel is 2026-02-13 (OTRIMG-0117), i.e. inside the two-state band, so
any QR-3 result fitted across the full in-sample window is anachronistic for the first weeks.

---

## 8. Enforcement of the one-way rule

1. `VFIndicatorOutput` is a frozen dataclass; every array has `writeable = False` set before
   return.
2. `input_hash = sha256` over the byte contents of `bars`, the `VFPanel` field values, the
   `VFSemantics` field values, and the module version. Recomputed after each wrapper run in
   tests (I2).
3. `vf_wrapper` receives `VFIndicatorOutput` **by value only**; it has no reference to
   `vf_indicator`, to `VFPanel`, or to `VFSemantics` except through the frozen copy carried on
   the output object for provenance.
4. **Static rule for review:** no identifier from the set {`pos`, `position`, `epx`, `trades`,
   `pnl`, `equity`, `stop`, `account`, `contracts`, `fill`} may appear anywhere in the Layer A
   module. A grep for that set is part of the run checklist.
5. Layer A is computed **once per (bars, panel, semantics)** and reused across the entire
   wrapper grid. A grid of `k` wrapper configurations must produce exactly one
   `VFIndicatorOutput` and `k` `WrapperOutput`s. If a grid recomputes the indicator per member,
   the separation is not real.

---

## 9. The counter-relocation bound (the Layer-A half of the preregistered prediction)

**Claim (deterministic, provable without running anything, stated here so that the regression
in `VF_WRAPPER_v2.md` §6 has a falsifiable floor).**

Hold fixed: the bar series, the trend series `tr`, the episode partition induced by `tr`, and
the raw candidate set `C = {i : signal_trade_raw[i] != 0}`. Let

- `E_v2` = the number of signals emitted by `vf_suppress` under `QR-1 / QD-DIR / QC-EMIT /
  SS-GLOBAL`, i.e. the exact rival that R7's structure implies;
- `E_R7` = the number of events that advanced R7's `cnt` / `last_sig`, which by §1.2 is exactly
  R7's set of entries and stop-and-reverses.

Then **`E_v2 ≥ E_R7`, per (episode, direction) and hence in total.**

*Proof sketch.* Within one (episode, direction), both procedures select a subset of `C`
subject to (i) pairwise spacing `≥ split_bars` measured from the previously selected element
of that same subset, and (ii) cardinality `≤ qty_per_trend`. R7's selection is additionally
required to arrive at a bar where the wrapper is flat or reversible. `vf_suppress` selects
earliest-first, which is the maximum-cardinality selection under a minimum-gap constraint;
capping both at the same `qty_per_trend` preserves the inequality. R7's selection is a feasible
set for the same constraints, hence no larger. ∎

**Two consequences that make this useful rather than decorative:**

- It converts "the signal count should go up" from an expectation into a **bound**. If an
  implementation reports `E_v2 < E_R7` on the same substrate with the same `tr` and the same
  `C`, the implementation is **wrong** — the bound is the acceptance test, not a finding.
- It says nothing whatever about the resulting **trade** count, which can move in either
  direction (`VF_WRAPPER_v2.md` §6.4). Signals up does not imply trades up; the interesting
  prediction is the one the bound does *not* cover.

---

## 10. What this document does not fix

- It does not choose a lifecycle, a rail formula, a trend rule, or a close-threshold cell.
  Those remain UNKNOWN and are carried as explicit `VFSemantics` fields so that no result can
  ever again be reported without them.
- It does not implement the zone module, so `QR-4`/`QR-5` — which carry the strongest textual
  warrant of any reset rule — remain untestable. **This is now the highest-value build gap in
  the VF programme**, alongside `F1x`.
- It does not touch the question of whether the *trader's* build carries vendor semantics for
  these fields at all (H1..H5 all live, `EV039_REAUDIT.md` Part D).

---

*Sources re-extracted this pass, read-only: `ninZaVWAPFlux-TraderManual.pdf` §1, §2.3, §2.4,
§2.5, §2.11, §2.12, §2.13, §2.14, §4. Code audited read-only: `src/vf_core.py`,
`src/run_r7_signal_id.py`, `src/run_r7b_signal_id.py`. Artifacts read read-only:
`runs/OTR_R7_VF_SIGNAL_ID/out/r7_summary.csv`, `r7b_summary.csv`, `r7_grid.csv`.
Companion adjudications: `VF_ARCHITECTURE_REOPEN.md`, `CLOSE_THRESHOLD_ADJUDICATION.md`,
`TREND_MODEL_ADJUDICATION.md`, `../vendor_forensics/EV039_REAUDIT.md`,
`VENDOR_SIGNAL_USAGE_MODEL.md`. No `.py` file was modified, no backtest was run, no original
screenshot was altered.*
