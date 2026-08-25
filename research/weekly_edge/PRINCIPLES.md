# WEEKLY_EDGE — PRINCIPLES (原理存档, kept current; started 2026-08-25)

Owner asked that the principles be saved for later research ("记得保存原理"). This file is the
mechanism record: WHAT each component is, WHY it should make money, and WHAT the evidence
says. Every claim carries its run. Corrections are appended, never erased.

## 0. What we did NOT build

**VWAP Flux was NOT reconstructed.** Two different things exist and must not be conflated:
- the clean-room VF *geometry approximation* (campaign #6) — fit to reproduce the trader's
  2026 weekly stats; as a money system it is DOES_NOT_EXIST at stress frictions (W01);
- the **delta proxy** — one documented INPUT CONCEPT from the VF manual (the
  `UpDownTick_RealVolume` volume-classification mode) implemented at 1-min bar granularity
  (signed volume by close direction, session-anchored cumsum). A concept, not the product.
  The vendor's Fair Value engine and `Signal_Trade` trigger remain purchasable only.

## 1. Architecture (first principles)

```
information engines (state machines)          risk & exposure           composition
────────────────────────────────────          ───────────────           ───────────
S1  Solar T1 flip + D-gate (2023-derived)     session-level $ halt      integer weights
S4  Solar13 ensemble + tilt + hysteresis      (h1300/h2600)             over weekly-
S5  B-MOM RTH breakout (decayed)              context gates (lagged):   independent
CD  cum-delta transition (marginal)             flow-side (delta),      sleeves
MO  osc-overlap reversal (dead)                 value-side (FV)
```
Money = engine expectancy × risk truncation × diversification across ENGINES (never across
exits of the same entries — W01 P4).

## 2. Mechanisms and their evidence (post W03-amendment-1, all lag-correct)

| mechanism | why it should work | measured |
|---|---|---|
| **Session-level $ halt** | our losses accumulate intra-week/intra-session (W02 measured: tail ≠ single trades) → truncate the accumulation process, not the trade | the ONLY mechanism that puts a config under −$15k worst week while keeping ≥55 % pos (W03: S4.all13.h1300.gdl, −$12,915) |
| **Delta context gate** | trade only with the session's realized flow direction; flow leads price at 1-min | **+0.02–0.03 Sharpe** portfolio marginal, real but modest (the 0.355 version was look-ahead, VOID) |
| **Hysteresis (3,1)** | entry conviction ≠ exit conviction; asymmetric bands suppress churn | +0.03–0.04 Sharpe, +$12.8/trade vs no-hysteresis (W04) |
| **HTF tilt (50-session)** | trade bigger with the higher-timeframe wind | +0.03 Sharpe, +$12.0/trade vs no-tilt (W04) |
| **D-gate (S1)** | stop trading after the session turns hostile | +$42k over the master window, −646 trades (r13 archive) |
| Ensemble averaging | diversify threshold noise | weak alone (0.028 Solar-only vs best atom 0.106) — averaging is NOT where expectancy comes from (W04) |
| Bolt-on skew exits | "let winners run" | **FALSIFIED** on our entries (W01 F2: every variant destroys $/trade) |
| Per-trade $ caps | his −$2,600 unit | **inert on our sleeves** (W02: 142/13,301 trades touched) — risk units do not transplant across architectures |
| Weekly loss limit | truncate bad weeks | regime-dependent; locks in losses, kills hit rate on dev (W01) |

## 3. The money, explained (as far as it is)

Honest 4.4-year frozen capability (net, stress-surviving): **~57–62 % positive weeks,
$1.2–2.7k/wk per 1–2 contracts, worst week −$13k…−$27k** depending on where you sit on the
tail-vs-mean frontier. Per-trade expectancy of the bar-clearing config **$110.5 > his $103**.
The remaining gap to "比他多比他稳" is the LEFT TAIL of portfolios (halts fix members, not
yet combinations) and the fact that no candidate has passed an untouched out-of-sample test —
the 9-week holdout is exhausted (4 reads) and June–July 2026 was a favourable regime.

## 4. Standing epistemic rules (each bought with a real mistake)

1. Gates/masks carry **decision-bar information only** (W03 am.1: close-at-open look-ahead).
2. **Explainability review before any freeze** — asking "where does the money come from"
   caught the look-ahead.
3. Never quote dev-sorted holdout rows as expectations (R34; W03 §multiplicity).
4. Session-flat conventions, $4.36/RT base, C1 stress line on everything.
5. Corrections propagate to every citing document, with the original preserved.

## 5. Open questions for the next researcher (possibly us, later)

- Can the halt be made regime-aware without becoming a fitted parameter?
- Does true tick delta (48-session substrate) agree with the 1-min proxy where they overlap?
  If yes, the proxy is validated backward; if no, the gate's real value may be higher.
- Would the official VF `Signal_Trend/Signal_Cum_Delta` (if purchased) beat the proxy gate?
- Portfolio-level tail: same-direction concentration cap (never yet implemented cleanly).
