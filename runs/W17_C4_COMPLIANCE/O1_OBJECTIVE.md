# O1 + O1a — THE PRIMARY OBJECTIVE FUNCTION

_Run dir: `runs/W17_C4_COMPLIANCE/`. Module: `src/analytics/primary_objective.py`.
Self-test: `src/analytics/test_primary_objective.py` (plain `python`, no pytest)._

**What this document is.** The existing "Sharpe AND CDaR AND top-10-day-retention" triple is
three independent hard gates. Three hard gates cannot express a trade-off: an object that buys
a large CDaR improvement with a small Sharpe give-up is rejected identically to one that
destroys both. That is why the triple has deadlocked. This document pre-registers, defines,
implements and verifies a **single scalar** in its place: expected log growth at a stated
target leverage, minus an explicit ruin-probability penalty. The legacy triple survives as
**reported diagnostics only** — it is no longer a gate.

**What this document is NOT.** It is not a selection or ranking pass. Nothing is promoted,
demoted, re-ranked or killed here. O2 retro-scoring of past objects is a separate, later,
separately pre-registered pass. The one real evaluation below (Product A) exists so that the
objective is demonstrated on a real series, not so that Product A is scored against anything.

**Nothing here establishes that future profitability is achievable.** Every number below is a
statistic of a fixed historical sample and of resamples of that sample.

---

## §0 Order of work (auditable)

This section, §1 and §2 were written to disk **before** the module was written and before any
objective value, growth rate, ruin probability, or intraday/daily gap was computed.

The only code executed before this section was written was the reproduction of **already-
published, already-committed** figures, used solely to confirm that the repo's bootstrap
machinery behaves as its committed artifacts say it does:

- `runs/PRODUCTB_ONECONTRACT_FINAL/out/capital_map_nq.csv` p95 max-drawdown values
  (L5 / L20 / stat60), and
- the C-P3 disclosure probabilities in `research/system_master/DRAWDOWN_FRONTIER.md`
  (P(2y maxDD > $25k) = 0.142 stationary-20 / 0.430 moving-5).

Both reproduced exactly (§4). No number produced by the new objective had been computed.

---

## §1 PRE-REGISTRATION (written before any number was computed)

Every value below is fixed here and is not to be searched, tuned, or moved to make a result
look better. Each is derived from an already-published committed figure or an existing house
convention, and the derivation is given.

### 1.1 Capital  —  **C = $100,000**

Two independent grounds, both pre-existing:

1. It is the frozen house base. `src/analytics/sm_metrics.py` sets `BASE = 100_000.0` and every
   `logG_100k` / `ulcer_pct_100k` figure this program has published is on it.
   `runs/SMV2F_LEVERAGE_ROBUST/smv2f.py` sets `CAP = 100_000.0` and every published leverage-
   frontier number (`f_star`, `median_growth`) is on it.
2. It is close to what the capital-map rule itself returns for an object of this size. The
   house capital-map convention is
   `capital_needed = p95(bootstrapped max-$-drawdown) / thr`
   (`runs/PRODUCTB_ONECONTRACT_FINAL/build_parity_and_metrics.py::capital_map`).

**Cross-check to be reported, not to be used to move C**: the capital-map rule is applied to
the evaluated object at `thr = 0.25` and the resulting `capital_needed` is reported alongside
the $100,000 result. If the two differ materially, the objective is reported at **both**
capital levels. C is not adjusted after seeing the number.

### 1.2 Target leverage  —  **L = 1.0** (headline), grid {0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 3.0} reported

Why 1.0:

1. It is the **deployed champion size** — one unit of the product as it actually exists. Any
   other headline leverage would be a number the program has never run.
2. It is exactly the **contested point**. The standing C-P3 disclosure
   (`research/system_master/DRAWDOWN_FRONTIER.md`, seq 362) says that at L = 1.0 the bootstrap
   probability of a 2-year max drawdown exceeding $25,000 is **0.142 / 0.430 / 0.157** across
   three methods — all above the 10% comfort cap — so the DD-constrained scale factor L\* is
   **below 1.0 under every method**. A new objective whose whole purpose is to price the
   growth/ruin trade-off must be quoted at the leverage where that trade-off is live.
3. Quoting a grid around it shows the shape of the objective without making any grid point a
   recommendation. **No leverage is recommended by this document.**

### 1.3 Ruin threshold  —  **peak-to-trough drawdown of the levered account reaching 25%**, absorbing

The instruction is that ruin be defined against the equity the capital map actually assumes,
not an arbitrary number. The capital map funds the account as `p95 max-$-DD / thr`: an account
funded at `thr = 0.25` is, **by construction**, an account for which a 25% peak-to-trough
drawdown consumes *the entire drawdown budget it was funded for*. So:

> **RUIN (primary, R1)** = at any observation point in the evaluation horizon, the levered
> account's drawdown from its own running high-water mark reaches **25%**.

`thr = 0.25` is the mid-grid tolerance of the committed capital maps
(`thr ∈ {0.10, 0.15, 0.20, 0.25, 0.30}`) and is the one `smv2f.py` itself prints as its headline
("Median growth at P(DD>25%)<=5%"). The drawdown-from-running-peak form is verbatim smv2f's own
`dd = 1 - eq/peak`.

This is **not** "equity reached zero". It means the account is no longer the account the
capital map assumed and the operator must de-lever or stop. It is modelled as **absorbing**:
on breach, the path stops compounding and terminal wealth is frozen at the breach level. The
absorbing choice is itself the reason a leverage that maximizes naive mean growth is not
optimal.

Two secondary ruin readings are reported, never used as the headline:

- **R2 (hard margin floor)** — equity falls below the day margin required to carry the object's
  maximum position under the broker's stated 4× pre-release stress. Product A's frozen target
  clip gives max |position| = 11 MNQ (verified from `smm_v2_bars.csv`); MNQ day margin $100 →
  `11 × $100 × 4 = $4,400` per unit of leverage. Meaningful only in fixed-contract mode; in
  fixed-fraction mode margin/equity is constant so R2 is a static feasibility test, not a
  crossing event. Reported either way.
- **R3 (C-P3 comparability)** — max drawdown over a 504-session path exceeding **$25,000** at
  L = 1.0, i.e. the published disclosure, so the new module's numbers can be laid directly
  beside the old ones.

Also reported separately: **P(equity ≤ 0)**, the true bankruptcy probability, which at these
leverages is expected to be far smaller than P(R1) and must not be conflated with it.

### 1.4 Evaluation horizon  —  **H = 504 sessions (2 years)**

Chosen to match C-P3 exactly (`runs/SMV2I_CURVE_READS/step2_cp3.py` uses `path_len = 504`), so
the new ruin probability is directly comparable to the published 0.14–0.43 band. The
full-sample horizon (all dev sessions, ≈4.5 years) is reported as a secondary.

### 1.5 Ruin penalty  —  **λ = 1.0 yr⁻¹**, grid {0, 0.5, 1.0, 2.0, 5.0} reported

The primary scalar is

```
    J(L)  =  CE_g(L)  −  λ · P_ruin(L)
```

where `CE_g` is the certainty-equivalent (= expected log) growth rate, annualized, computed on
the **absorbing** paths, and `P_ruin` is the R1 probability over the horizon H.

Derivation of λ — an **out-of-horizon opportunity cost**, so that it does not double-count the
in-horizon loss (the log loss suffered while drawing down to the barrier is already inside
`CE_g`, because the absorbing path terminates at the barrier level):

- Reference log growth rate `g_ref`. From the committed published headline in
  `research/system_master/CURRENT_TRUTH.md` — executable dev net **$177,315.1 over 1,139
  sessions** — and the house $100k base and the house non-compounded `logG` convention:
  `g_ref = ln(1 + 177315.1/100000) / (1139/252) = 1.0198 / 4.5198 = 0.2256 /yr`.
  This is a *published prior figure*, not a number produced by this run.
- Intended franchise horizon `H_f = 10 years`; evaluation horizon `H = 2 years`; a ruin event
  is on average reached near the middle of the evaluation window, so it forfeits
  `H_f − H/2 = 9` further years of compounding.
- Forfeited log wealth per ruin event ≈ `9 × 0.2256 = 2.03`. Amortized over the H = 2 year
  window in which the objective is expressed: `λ = 2.03 / 2 = 1.015 ≈ **1.0 yr⁻¹**`.

**Interpretation, stated so it can be argued with:** λ = 1.0 means *one percentage point of
2-year ruin probability must be paid for by one percentage point of annualized log growth.*
A λ-grid is reported so a reader who rejects the 10-year franchise assumption can read the
objective at their own λ. λ is a **preference parameter, not an estimate**; it is disclosed,
not defended as true.

### 1.6 Bootstrap  —  the three methods of the committed capital map, `n_boot = 2000`, `seed = 20260808`

`runs/PRODUCTB_ONECONTRACT_FINAL/build_parity_and_metrics.py::capital_map` uses exactly three:

| name | method | as coded |
|---|---|---|
| `moving5` | circular moving block, block length **5** | `idx_moving_block(5)` |
| `moving20` | circular moving block, block length **20** | `idx_moving_block(20)` |
| `stationary60` | stationary (Politis–Romano), mean block **60** | `idx_stationary(60)` |

**Correction to the task's guess, stated explicitly**: the task anticipated "likely iid,
circular block, and stationary block". The committed capital map contains **no iid method** —
its trio is two circular-block lengths plus one stationary. The module uses the *actual*
committed trio as the three headline methods. An **iid** method is implemented and reported
**additionally, as a diagnostic**, because `src/analytics/validation.py::bootstrap_risk`
already establishes the iid-vs-block understatement ratio as a house diagnostic. iid is never
one of the three headline numbers.

All three are reported, plus **the spread (max − min)**. **Headline `P_ruin` = the maximum
across the three**, following the house convention that the band is quoted and the worst
member is the one acted on (C-P3's "HEADLINE = worst (smallest) L\* across methods").

`seed = 20260808` is the house default (`smv2_common`, `sm_metrics`, `smv2i_lib`, `smv2f`).
`n_boot = 2000` matches the capital map and smv2f. Every generator takes a fresh
`np.random.default_rng(seed)`, so the module is deterministic given the seed and each method is
independently reproducible.

### 1.7 Legacy triple — demoted to DIAGNOSTICS

Daily Sharpe (ann 252, ddof 1), CDaR_0.95 ($, house convention = mean of the worst 5% of the
end-of-day dollar drawdown series), and top-10-day retention/share are computed and returned
under a key explicitly named as non-gating. **They are not gates, not thresholds, and not
selection inputs.** They exist so that a reader who knows the old numbers can locate the object.

### 1.8 O1a — pre-registered hypothesis and materiality bars

**Hypothesis (owner's, restated):** daily-close CDaR understates the tail risk that matters for
a levered account, because a levered account experiences margin pressure intraday, not at the
close.

The weak inequality `P_ruin(intraday) ≥ P_ruin(daily-close)` is a **tautology** given identical
resampled session sequences and a strictly larger set of observation points, so confirming it
proves nothing. The research question is entirely one of **magnitude**. Pre-registered bars,
fixed before computation:

- **MATERIAL** if, at the headline leverage, `P_ruin(intraday) − P_ruin(daily-close) ≥ 0.02`
  absolute **or** `≥ 20%` relative (worst method).
- **MATERIAL** if the frequency-matched CDaR ratio `CDaR_intraday / CDaR_daily-close ≥ 1.20`.
- Otherwise **IMMATERIAL** — and if it is immaterial the report will say so in exactly those
  words, with the same prominence as a positive result.

"Frequency-matched CDaR" is defined now, not after: the naive comparison (worst 5% of ~232,000
bar-level drawdowns vs worst 5% of 504 day-level drawdowns) is not apples-to-apples, because
the two samples have different sizes and different serial structure. The matched statistic
reduces the intraday path to **one observation per session — that session's worst
drawdown-from-running-peak** — giving exactly 504 observations, the same as the daily-close
series, and takes CDaR_0.95 over those. Both the naive and the matched numbers are reported;
the **matched** one is the headline.

Both legs are computed on **identical** resampled session index matrices, so the gap is a
paired comparison and not a sampling artefact.

---

## §2 The objective, formally — every modelling choice stated

### 2.1 From a dollar P&L path to log returns given finite capital

The product is a futures strategy: its output is a dollar P&L series `x_d`, not a return
series. A growth rate does not exist until an account equity is named. Two constructions are
implemented; the primary is stated and the other is reported.

**(a) `leverage_mode="fixed_fraction"` — PRIMARY.** Position size is reset at each session open
so that exposure stays proportional to current equity: units held on day *d* =
`L · E_{d-1} / C`. Then

```
    E_d = E_{d-1} · (1 + L · x_d / C)          r_d = L · x_d / C
    log-increment  ℓ_d = log1p(L · x_d / C)
```

This is the construction under which expected log growth is even well-defined (it is the
fixed-fraction / Kelly setting), and it is **verbatim the construction already used by
`runs/SMV2F_LEVERAGE_ROBUST/smv2f.py`**: `r = f * pnl[idx] / CAP; eq = cumprod(1 + r)`.
Leverage is therefore applied as a **constant multiplier in return space**, equivalently as a
contract count that is re-set daily in proportion to equity.

**(b) `leverage_mode="fixed_contracts"` — SECONDARY.** Units held = `L`, constant; equity
drifts: `E_d = C + L · Σ x`. This is what actually happens if the operator never resizes, and
it is the construction the **capital map** implicitly assumes (it cum-sums dollars and never
compounds). Reported alongside.

**Contract granularity — disclosed limitation.** Fixed-fraction rebalancing is continuous in
the model. Real futures contracts are integers. Product A's unit is itself a fractional
portfolio blend (60/40 vol-matched), so continuous rescaling is a closer description of it than
integer-lot rounding would be; but at small capital the rounding error is real and the model
overstates how finely the operator can track the target fraction. An optional `min_unit`
argument implements floor-to-multiple rounding for objects where that matters; it is **off** by
default and off for the worked example. Flagged, not fixed.

### 2.2 Paths that cross zero equity

If `L · x_d / C ≤ −1` the naive equity goes non-positive and `log` is undefined. Handling:

1. The R1 barrier (25% drawdown) is checked at **every** observation point and is **absorbing**.
   Any single move large enough to take equity through zero necessarily passes the 25% barrier
   first *at that same observation point*, so in practice ruin absorbs before the log blows up.
2. Belt and braces: the return is clipped at `−1 + 1e-12` before `log1p`, and every path where
   the clip bound, i.e. `1 + L·x/C ≤ 0`, was hit is **counted and returned** under
   `integrity.n_paths_equity_nonpositive`. That count is a reported number, not a silent fix.
   If it is non-zero the growth figures at that leverage are declared unreliable.
3. Absorbed paths keep a **finite, negative** terminal log wealth (the barrier level), so ruin
   drags `CE_g` down rather than producing `−inf`. This is why the barrier is defined at a
   positive equity level and not at zero.

### 2.3 The scalar

```
    CE_g   = (252 / H) · mean_over_paths[ log(W_H / W_0) ]        (absorbing)
    P_ruin = max over the three bootstrap methods of  P(R1 breached within H)
    J      = CE_g − λ · P_ruin
```

`CE_g` is the certainty-equivalent growth rate under log utility, which is what "expected log
growth" means: a log-utility operator is indifferent between the random path and a certain
growth rate of `CE_g`. Mean, median and the 5th/95th percentiles of per-path annualized log
growth are all returned; the mean is the CE.

### 2.4 The intraday path

For session *d* the committed artifact gives `mtm_t` = cumulative mark-to-market **within** that
session, reset to 0 at the session open, with `mtm_end = x_d` exactly. Because size is set at
the session open and does not change during the session,

```
    E(t) = E_open,d · (1 + L · mtm_t / C)        ℓ(t) = ℓ_open,d + log1p(L · mtm_t / C)
```

so the within-session log path depends only on that session's own MTM vector and on `L` — not
on the equity level. The whole intraday equity path is therefore an exact concatenation of
per-session log paths, and its session-end values reproduce the daily recursion of §2.1 **to
the cent, by construction**. The intraday and daily legs are the same model observed at two
frequencies, which is precisely what makes the gap interpretable.

Bootstrap resampling is at the **session** level, carrying each session's entire intraday bar
vector. The identical index matrices drive both legs.

### 2.5 No look-ahead

Every quantity is a function of the realized in-sample series only. Block resampling draws from
the realized sample; no future information enters any statistic. Locked-forward data
(≥ 2026-08-01) is refused by the loader with an exception, and any session beyond the dev end
(2026-05-29) is truncated with the truncation recorded in the returned dict.

### 2.6 A structural property worth stating

In `fixed_fraction` mode the objective depends on `L` and `C` **only through the ratio `L/C`**
(exposure per dollar of equity), because the ruin barrier is relative and the log increments are
`log1p(L·x/C)`. "Leverage at $100k" and "capital at 1×" are therefore the *same axis*, not two.
This is confirmed numerically in §5.3 (J at L = 0.5 / C = $100,000 equals J at L = 1.0 /
C = $200,045 to 4 decimals). It matters because it means the capital cross-check of §1.1 and the
leverage grid of §1.2 are one sweep, not two.

---

## §3 Module API

`src/analytics/primary_objective.py`

```python
primary_objective(pnl_path, capital=100_000.0, leverage=1.0, *,
                  intraday_path=None, intraday_col=None,
                  ruin_dd_frac=0.25, lam=1.0, horizon_sessions=504,
                  n_boot=2000, seed=20260808,
                  methods=("moving5","moving20","stationary60"),
                  diagnostic_methods=("iid",),
                  leverage_mode="fixed_fraction", absorbing=True,
                  cdar_alpha=0.95, baseline_daily=None,
                  min_unit=None, dev_window="truncate", ...) -> dict
```

`pnl_path` accepts a path to `.csv`/`.parquet`, a `pd.Series` (date-indexed), a `pd.DataFrame`,
or a bare array. Returned keys:

| key | contents |
|---|---|
| `primary.objective_J` | **the scalar** `J = CE_g − λ·P_ruin` |
| `primary.ce_log_growth_ann` | expected / certainty-equivalent log growth rate, annualized |
| `primary.p_ruin` | headline ruin probability = worst of the three methods |
| `primary.objective_J_by_lambda` | J over the λ grid |
| `primary.objective_J_intraday_barrier` | same J with the barrier checked every 3-min bar |
| `growth.per_method` | mean / median / q05 / q95 of per-path annualized log growth |
| `growth.historical_single_path` | the one realized path, flagged as one path |
| `ruin.daily_close` / `ruin.intraday` / `ruin.gap` | O1a, per method, plus spread and materiality |
| `ruin.R2_margin_floor`, `ruin.R3_cp3_comparability`, `ruin.p_equity_nonpositive` | secondary ruin reads |
| `tail.daily_close` / `tail.intraday` / `tail.gap` | CDaR (bar-level and frequency-matched), maxDD |
| `legacy_diagnostics_NOT_GATES` | Sharpe, CDaR_0.95($), maxDD($), top-10-day share/retention |
| `integrity` | clipping counts, intraday reconciliation, truncation, warnings |
| `spec` | every input echoed, including seed and n_boot |

Helpers: `leverage_curve(...)`, `historical_intraday_vs_daily(...)`,
`reproduce_capital_map(...)`, `reproduce_cp3(...)`, `make_indices(...)`,
`legacy_diagnostics(...)`.

---

## §4 Verification — the machinery is this repo's machinery (DIRECT)

`python src/analytics/test_primary_objective.py` → **16/16 PASS** (5.9 s).

The two load-bearing cases:

| case | claim | result |
|---|---|---|
| 3 | `reproduce_capital_map` on the exact daily series behind `runs/PRODUCTB_ONECONTRACT_FINAL/out/capital_map_nq.csv` returns the committed p95 max-drawdowns | L5 **109,176.998**, L20 **91,485.344**, stat60 **81,956.618** — max abs diff vs committed CSV **5.8e-11** |
| 4 | `reproduce_cp3` on the DUAL6040 champion returns the published C-P3 probabilities | stationary20 **0.1422** (published 0.142), moving5 **0.4298** (published 0.430) |

Other cases: determinism under a fixed seed (bit-identical J); seed sensitivity bounded;
analytic closed form on a constant P&L series (`CE_g = 252·log1p(0.005)` to 1e-12); zero
leverage → J = 0; P_ruin monotone in leverage; intraday ≥ daily on identical resampled paths;
intraday session-end log returns reconcile to the daily series at **0.0** max abs difference;
legacy Sharpe identical to `smv2_common.dd_battery`; legacy CDaR identical to the
`smv2i_lib.cdar` convention; the LOCKED-FORWARD guard raises; post-dev truncation is recorded;
absorbing == non-absorbing when no path ruins; `fixed_contracts` and `min_unit` paths run.

**A naming collision that must not propagate.** In
`runs/SMV2AH_DAY_CIRCUIT_BREAKER/out/intraday_mtm_series.parquet`, column **`_A` is the
SOLAR_DUAL_HTF standalone leg** and column **`_B` is DAYONLY_DUAL6040**, which is the research
curve of **"Product A" = SolarWaveSMMaster_v2**. The worked example below uses **`_B`**.
Verified: column `_B`'s session-end series equals the published DUAL6040 champion curve
(`runs/SMV2I_CURVE_READS/smv2i_lib.repro_gate`) to **2.0e-11**.

---

## §5 Worked example — Product A (SolarWaveSMMaster_v2)

**This is a demonstration that the objective runs on a real series. It is not a ranking, not a
selection, and not a recommendation of any leverage or capital.**

Series: the research curve (DAYONLY_DUAL6040), **1,139 sessions, 2022-01-03 → 2026-05-29, net
$194,416.04**, with its bar-by-bar intraday twin (519,714 three-minute bars, 170–460 per
session). Settings are the §1 pre-registration verbatim: C = $100,000, L = 1.0, R1 = 25%
peak-to-trough absorbing, H = 504 sessions, n_boot = 2,000, seed = 20260808.

### 5.1 The headline scalar

| quantity | value |
|---|---:|
| **CE_g** — expected (certainty-equivalent) log growth, annualized, pooled over the three methods | **+0.3395 /yr** |
| **P_ruin** — daily-close barrier, worst of three (`moving5`) | **0.3185** |
| **J = CE_g − λ·P_ruin**, λ = 1.0 | **+0.0210** |
| **P_ruin** — **intraday** barrier, worst of three (`moving5`) | **0.4975** |
| **J with the intraday barrier** | **−0.1935** |

**The sign of the objective at the pre-registered headline point depends on whether the barrier
is watched at the close or watched intraday.** At the close the product at 1× on $100,000
scores marginally positive; watched at every 3-minute bar — which is when a levered account
actually experiences margin pressure — it scores **negative**. This is reported as prominently
as the positive number because it is the more operationally faithful one.

### 5.2 Every component, per method (no silent picking)

Expected log growth, annualized, absorbing paths:

| method | mean (= CE_g) | median | q05 | q95 | non-absorbing mean |
|---|---:|---:|---:|---:|---:|
| moving5 | 0.3097 | 0.3202 | −0.1058 | 0.7172 | 0.3642 |
| moving20 | 0.3468 | 0.3569 | −0.0171 | 0.6515 | 0.3681 |
| stationary60 | 0.3619 | 0.3620 | +0.1310 | 0.6090 | 0.3675 |
| _iid (DIAGNOSTIC, not a headline method)_ | _0.2744_ | _0.2601_ | _−0.1238_ | _0.7581_ | _0.3698_ |
| **pooled over the three** | **0.3395** | | | | |

Ruin probability, R1 (25% peak-to-trough, absorbing), H = 504 sessions:

| method | daily-close | intraday | gap (abs) | gap (rel) |
|---|---:|---:|---:|---:|
| moving5 | 0.3185 | 0.4975 | **+0.1790** | +56.2% |
| moving20 | 0.1205 | 0.2425 | **+0.1220** | +101.2% |
| stationary60 | 0.0335 | 0.2335 | **+0.2000** | +597.0% |
| _iid (DIAGNOSTIC)_ | _0.5360_ | _0.6890_ | _+0.1530_ | _+28.5%_ |
| **headline (worst of three)** | **0.3185** | **0.4975** | **+0.1790** | **+56.2%** |
| **spread (max − min over three)** | **0.2850** | **0.2640** | | |

> **NEGATIVE RESULT, stated as prominently as the positives: the method spread is enormous.**
> Daily-close P_ruin ranges from **0.0335 to 0.3185** — a factor of **9.5** — across three
> resampling methods that are all defensible and all already in use in this repo. The headline
> number is **method-determined at least as much as it is data-determined**. Any future use of
> this objective that quotes a single ruin probability without the band is misleading.
>
> A second, uncomfortable observation: the ordering is monotone in block length
> (iid 0.536 > moving5 0.319 > moving20 0.121 > stationary60 0.034). Shorter blocks give larger
> drawdowns, i.e. this series' own serial structure is drawdown-**dampening**, and the
> "conservative" house convention of quoting the worst method therefore lands on the method that
> most nearly **destroys** that structure. "Conservative" here means "closest to iid", which is
> a modelling choice, not a fact about the strategy. Flagged, not resolved.

Secondary ruin reads:

- **R2 (hard margin floor, $4,400/unit = 11 MNQ × $100 day margin × 4× pre-release stress):** not
  binding. In `fixed_fraction` mode margin/equity is constant, so R2 is a static feasibility
  test — feasible up to L = 22.7 at $100,000. In `fixed_contracts` mode, P(equity < $4,400) =
  **0.0000** under all three headline methods (0.0005 under iid).
- **P(equity ≤ 0) = 0.0000** under all three methods. **True bankruptcy is not the binding risk
  at this leverage; exhausting the funded drawdown budget is.** These two must never be conflated.
- **R3 (C-P3 comparability), P(2-year max $ drawdown > $25,000) at L = 1.0:**
  moving5 **0.420**, moving20 **0.168**, stationary60 **0.048**.
  Published C-P3: 0.430 (moving5, B = 5,000), 0.142 (stationary_pr20), 0.157 (joint-loss 2×).
  The moving5 agreement is exact once resample count is matched (§4 case 4 gives 0.4298 at
  B = 5,000). **The capital map's `stationary60` is a materially milder method than C-P3's
  `stationary_pr20`** (0.048 vs 0.142) — different mean block length *and* a different stationary
  formulation (per-step restart vs geometric block lengths). Both are implemented in the module
  under distinct names so this can never again be conflated.

### 5.3 Capital cross-check against the house capital-map rule

Capital map for this object, committed full-length convention, m = 1.0:

| method | p95 max $ DD | capital needed @ thr 0.25 |
|---|---:|---:|
| L5 (moving5) | $50,011.29 | **$200,045** |
| L20 (moving20) | $35,051.10 | **$140,204** |
| stat60 (stationary60) | $27,584.44 | **$110,338** |

> **The pre-registered C = $100,000 is BELOW the entire capital-map band ($110k – $200k) for this
> object.** The pre-registration is not adjusted after the fact (§1.1 said it would not be); the
> discrepancy is reported and the objective is quoted at the capital-map capitals as well:

| capital (rule) | L | CE_g | P_ruin (worst of 3) | **J** |
|---|---:|---:|---:|---:|
| $100,000 (house base) | 1.0 | 0.3395 | 0.3185 | **+0.0210** |
| $110,338 (stat60 rule) | 1.0 | 0.3213 | 0.2310 | **+0.0903** |
| $140,204 (L20 rule) | 1.0 | 0.2695 | 0.0840 | **+0.1855** |
| $200,045 (L5 rule) | 1.0 | 0.1970 | 0.0085 | **+0.1885** |

Scale invariance confirmed: J at (L = 0.5, C = $100,000) = **0.18851** vs J at (L = 1.0,
C = $200,045) = **0.18846** — the same point on the L/C axis (§2.6).

### 5.4 Shape of the objective in leverage (NOT a recommendation)

Daily-close barrier, n_boot = 2,000:

| L | CE_g | P_ruin | spread | **J** |
|---:|---:|---:|---:|---:|
| 0.00 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| 0.25 | 0.1021 | 0.0000 | 0.0000 | +0.1021 |
| 0.50 | 0.1970 | 0.0085 | 0.0085 | +0.1885 |
| 0.75 | 0.2804 | 0.1095 | 0.1080 | +0.1709 |
| **1.00** | **0.3395** | **0.3185** | **0.2850** | **+0.0210** |
| 1.25 | 0.3567 | 0.6015 | 0.4530 | −0.2448 |
| 1.50 | 0.3209 | 0.8120 | 0.3360 | −0.4911 |
| 2.00 | 0.1669 | 0.9760 | 0.0365 | −0.8091 |
| 3.00 | 0.0908 | 0.9995 | 0.0005 | −0.9087 |

Finer read around the turn (n_boot = 500, disclosed as a reduced resample count):

| L | J (daily barrier) | J (intraday barrier) |
|---:|---:|---:|
| 0.4 | 0.1528 | 0.1528 |
| 0.5 | 0.1851 | **0.1851** |
| 0.6 | **0.1954** | 0.1623 |
| 0.7 | 0.1736 | 0.1291 |
| 0.8 | 0.1337 | 0.0529 |

The objective turns over near L ≈ 0.6 on the daily-close barrier and near L ≈ 0.5 on the
intraday barrier — **watching the barrier intraday moves the turning point down by roughly one
sixth.** This is a *shape*, reported because the whole point of a scalar is that it has one.
**It is not a leverage recommendation and no leverage is adopted by this document.** The
turning point moves with λ, with capital, with the rebalancing convention, and with the choice
of bootstrap method, all of which are shown to matter by more than the difference between grid
points.

### 5.5 Rebalancing-convention sensitivity (NEGATIVE result)

| convention | CE_g | P_ruin (worst of 3) | J |
|---|---:|---:|---:|
| `fixed_fraction` (primary; size reset daily to L·E/C) | 0.3395 | 0.3185 | **+0.0210** |
| `fixed_contracts` (secondary; L contracts, never resized) | 0.2807 | 0.1645 | **+0.1162** |

**J moves by 0.095 — more than four times the headline value itself — purely on the choice of
rebalancing convention**, because a non-rebalanced account does not scale exposure up as equity
grows and so spends less of its life at high exposure. Neither convention is wrong; the number
is simply not convention-free. Anyone quoting J must quote the mode.

### 5.6 Executable twin cross-check

The NT8-executable daily P&L series for `SolarWaveSMMaster_v2` is **not a committed per-day
artifact in this repo** — only the summary battery (`runs/SMV2M_MASTER_BUILD/out/nt8_dev_battery.csv`,
net $177,315.10). The closest committed executable daily series is the twin
(`runs/SMV2M_MASTER_BUILD/out/twin_daily.csv`, dev slice net $179,288.70; 45 post-dev sessions
were truncated by the loader and the truncation is recorded). Evaluated identically:

| series | net (dev) | CE_g | P_ruin (m5 / m20 / s60) | J |
|---|---:|---:|---|---:|
| research curve (DUAL6040) | $194,416.04 | 0.3395 | 0.3185 / 0.1205 / 0.0335 | +0.0210 |
| executable twin | $179,288.70 | 0.3067 | 0.3555 / 0.1385 / 0.0405 | **−0.0488** |

**The executable twin scores negative at the headline point even on the daily-close barrier.**
The research-to-executable step costs about 0.070 of J here. Disclosed gap: the twin's net is
1.1% above the true NT8-executable net, so the executable figure above is, if anything,
optimistic.

### 5.7 Legacy triple — REPORTED DIAGNOSTICS, NOT GATES

| diagnostic | research curve | executable twin | SOLAR_DUAL_HTF leg |
|---|---:|---:|---:|
| daily Sharpe (ann 252) | 1.2642 | 1.1858 | 0.8992 |
| CDaR_0.95 ($, 1 unit) | $14,322.23 | $14,151.47 | $20,447.47 |
| max DD ($, 1 unit) | $18,131.66 | $16,821.20 | $25,697.80 |
| top-10-day share of net | 0.5906 | 0.6199 | 0.8182 |

`top10_day_retention_vs_baseline` returns `None` unless a baseline series is supplied, because
"retention" is inherently relative; the absolute share is reported instead. These four numbers
are returned under `legacy_diagnostics_NOT_GATES` and are **not** thresholds.

> **A fragility the new scalar does NOT price:** 10 sessions out of 1,139 (0.9%) produce **59%**
> of the research curve's net. Expected log growth is computed on the realized sample and
> therefore inherits that concentration; block resampling preserves it rather than testing it.
> The objective replaces three deadlocked gates — it does not solve right-tail dependence,
> multiple testing, or regime change, and it must not be presented as if it did.

---

## §6 O1a — the intraday path vs the daily close

**Question (pre-registered §1.8):** does daily-close CDaR understate the tail risk that matters
for leverage, and by how much? The weak inequality is a tautology, so only magnitude counts.

### 6.1 DIRECT evidence — the single realized path (no resampling)

Product A, C = $100,000, L = 1.0, the actual 1,139 dev sessions:

| | daily close | intraday (3-min bars) | ratio |
|---|---:|---:|---:|
| max drawdown (fraction of high-water mark) | **18.77%** | **28.10%** | **1.497** |
| CDaR_0.95, frequency-matched | 14.28% | 23.33% | **1.634** |
| CDaR_0.95, bar-level | 14.28% | 22.61% | 1.583 |
| **hits the 25% ruin barrier?** | **NO** | **YES** | — |

**The realized historical path of Product A, levered 1× on $100,000, does not ruin when the
account is inspected only at the close and does ruin when the same account is inspected
intraday.** Same trades, same fills, same capital — only the observation frequency differs.
That is the cleanest possible statement of the hypothesis, and it is DIRECT evidence from one
path, not an inference.

Same read on the standalone SOLAR_DUAL_HTF leg: daily-close max DD 24.47% → intraday 25.89%
(ratio 1.058), matched CDaR ratio 1.199, and it too crosses the 25% barrier intraday having not
crossed it at the close.

An unplanned observation that follows from the two objects together, reported because it is
material: the 60/40 blend's advantage over the standalone leg is **much smaller intraday than at
the close**. At the close the blend cuts max DD from 24.47% to 18.77% (−23%); intraday it cuts
it only from 25.89% to 28.10% — i.e. **not at all; the blend is worse intraday**. The
diversification benefit this program has been booking is substantially a close-sampling artefact.
This is an INFERENCE from two objects on one dev window and is not established; it is flagged as
a candidate for its own pre-registered test.

### 6.2 Bootstrap evidence — the gap at the headline leverage

Identical resampled session sequences drive both legs (paired comparison).

| method | P_ruin daily | P_ruin intraday | Δ abs | Δ rel |
|---|---:|---:|---:|---:|
| moving5 | 0.3185 | 0.4975 | +0.1790 | +56.2% |
| moving20 | 0.1205 | 0.2425 | +0.1220 | +101.2% |
| stationary60 | 0.0335 | 0.2335 | +0.2000 | +597.0% |
| headline (worst) | 0.3185 | 0.4975 | **+0.1790** | **+56.2%** |

Frequency-matched CDaR_0.95 (mean over paths, as a fraction of capital):

| method | daily close | intraday (matched) | ratio | bar-level ratio | max-DD ratio |
|---|---:|---:|---:|---:|---:|
| moving5 | 0.2033 ($20,329) | 0.2338 ($23,379) | 1.150 | 1.108 | 1.129 |
| moving20 | 0.1647 ($16,475) | 0.1973 ($19,728) | 1.197 | 1.142 | 1.165 |
| stationary60 | 0.1461 ($14,611) | 0.1893 ($18,927) | **1.295** | 1.235 | 1.247 |

### 6.3 VERDICT against the pre-registered bars

| pre-registered bar | measured | verdict |
|---|---|---|
| P_ruin gap ≥ 0.02 abs **or** ≥ 20% rel | **+0.179 abs, +56.2% rel** (worst method) | **MATERIAL** |
| frequency-matched CDaR ratio ≥ 1.20 | **1.295** (worst method) | **MATERIAL** |

**The hypothesis is SUPPORTED. Daily-close CDaR understates the tail risk that matters for
leverage, on this object, in this dev window, by both pre-registered measures.** Quantified:

- **Ruin probability at the headline leverage is understated by 18 percentage points
  (0.319 → 0.498), a 56% relative understatement.**
- **Frequency-matched CDaR is understated by 15%–30% depending on method (worst 1.295).**
- **The single realized path flips from not-ruined to ruined.**
- **The objective itself flips sign: J = +0.021 (daily) vs −0.194 (intraday).**

Replication on a second object (SOLAR_DUAL_HTF leg, n_boot = 500): gap +0.176 abs / +32.1% rel,
matched CDaR ratio 1.205 — **MATERIAL on both bars there too.** So the finding is not specific
to the blended portfolio.

### 6.4 Where the gap lives — and where it does not (the honest qualification)

n_boot = 500 for this sweep (reduced count, disclosed):

| L | P_ruin daily | P_ruin intraday | Δ abs | Δ rel | matched CDaR ratio (worst) |
|---:|---:|---:|---:|---:|---:|
| 0.25 | 0.000 | 0.000 | 0.000 | — | 1.362 |
| 0.50 | 0.008 | 0.008 | 0.000 | 0.0% | 1.335 |
| 0.75 | 0.116 | 0.186 | +0.070 | +60.3% | 1.311 |
| 1.00 | 0.324 | 0.508 | +0.184 | +56.8% | 1.289 |
| 1.50 | 0.798 | 0.948 | +0.150 | +18.8% | 1.250 |
| 2.00 | 0.982 | 0.998 | +0.016 | +1.6% | 1.216 |

**The ruin gap is not uniformly material.** It is ~zero at low leverage (nothing ruins either
way), peaks in the L ≈ 0.75–1.5 band, and collapses at high leverage (everything ruins either
way). It happens to be largest **exactly in the operating region**, which is why it matters, but
a reader must not generalize "intraday adds 18 points of ruin probability" — that is true near
L = 1 and false at L = 0.3 and at L = 2. The **CDaR** ratio, by contrast, is materially above 1
at every leverage tested (1.22–1.36) and rises as leverage falls.

### 6.5 What this does NOT establish

- It does not establish that a broker would have liquidated. R1 is *the funded drawdown budget
  exhausted*, not a margin call. The true margin floor (R2) was never hit in any resampled path.
- It does not establish anything about the future, only about the dev window 2022-01-03 →
  2026-05-29.
- The intraday series is available **only for the research curve**, not for the NT8-executable
  object. §5.6 shows the executable twin scores ~0.07 of J *worse* on the daily barrier, so the
  executable object's intraday-barrier J is very likely worse than −0.19 — but that is an
  **INFERENCE**, not a measurement, and building the executable intraday MTM series is the
  obvious follow-up.
- Only one dev window, two objects, one instrument. Not a general fact about futures strategies.

---

## §7 What changes, and what does not

**Changes.** The primary objective for anything intended to be levered is `J` at a stated
`(C, L, λ, barrier, mode)`, with the ruin band across all three methods quoted alongside. The
legacy triple is demoted to diagnostics. A trade-off can now be expressed: an object that buys
ruin-probability reduction with growth is scored, not deadlocked.

**Does not change.** No object is promoted, demoted or re-ranked here. No leverage is adopted.
The C-P3 disclosure stands unmodified. The §1 pre-registration was not moved after the numbers
were seen — the capital cross-check (§5.3) landed *against* the pre-registered capital and the
pre-registration was reported as-is rather than adjusted.

**Open weaknesses of this objective, stated plainly.**
1. `P_ruin` varies ~9.5× across three legitimate methods; the "worst of three" convention picks
   the most nearly-iid method (§5.2).
2. `J` moves by more than its own headline value on the rebalancing convention (§5.5).
3. `λ` is a preference parameter. At λ = 2 the object is negative at L = 1 even on the daily
   barrier (`J = −0.298`). The λ grid is always reported.
4. Expected log growth on a resampled realized sample cannot see regime change and does not
   price the 59%-of-net-in-10-days concentration.
5. Contract granularity is modelled optionally (`min_unit`) and is off by default.
6. **Nothing here establishes that future profitability is achievable.**

---

## §8 O2 boundary

O2 (retro-scoring past objects with this objective) is a **separate, later, separately
pre-registered pass**. Nothing in this document may be used to rank objects. The Product A
evaluation exists solely so that the objective has been exercised end-to-end on a real series
with real artifacts.

---

## §9 Files

| path | what |
|---|---|
| `src/analytics/primary_objective.py` | the module (new) |
| `src/analytics/test_primary_objective.py` | self-test, plain `python`, 16/16 PASS (new) |
| `runs/W17_C4_COMPLIANCE/O1_OBJECTIVE.md` | this report (new) |

Inputs read (all pre-existing, none modified):
`runs/SMV2AH_DAY_CIRCUIT_BREAKER/out/intraday_mtm_series.parquet`,
`runs/SMV2M_MASTER_BUILD/out/twin_daily.csv`,
`runs/SMV2M_MASTER_BUILD/out/nt8/smm_v2_bars.csv`,
`runs/PRODUCTB_ONECONTRACT_FINAL/out/{nt_trades_nq.csv, capital_map_nq.csv}`,
`runs/SMV2I_CURVE_READS/smv2i_lib.py`, `src/analytics/{sm_metrics,smv2_common,validation,sm01_solarsim}.py`.

Reproduce every number in §5–§6:

```
python src/analytics/test_primary_objective.py
python -c "import sys;sys.path.insert(0,'src/analytics');import pandas as pd,primary_objective as PO;\
idf=pd.read_parquet('runs/SMV2AH_DAY_CIRCUIT_BREAKER/out/intraday_mtm_series.parquet');\
e=idf[idf.is_last_of_sess];d=pd.Series(e.intraday_mtm_B.to_numpy(float),index=pd.to_datetime(e.sess_date.to_numpy()));\
import json;print(json.dumps(PO.primary_objective(d,intraday_path=idf,intraday_col='intraday_mtm_B')['primary'],indent=1))"
```

seed = 20260808, n_boot = 2000 (500 where explicitly disclosed), horizon = 504 sessions.
