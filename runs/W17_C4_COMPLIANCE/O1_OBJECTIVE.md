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

---
