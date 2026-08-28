# `VOLUME_LIQUIDITY_V1` — bounded design brief. **NO ALPHA RUN IN THIS WAVE.**

Design only: EVI, data contract, mechanism. **No features built, no model fitted, no P&L computed.**

| | |
|---|---|
| **why this lane** | genuinely new information · already local · costs nothing to reach · spends **no** protected pool |
| **MAXIMUM HISTORICAL EVIDENCE CLASS** | **DISCOVERY-GRADE.** Declared *now*, before any result |
| **what it is not** | not TSMOM+volume · not carry+volume · not a rescue of a dead family · not a feature zoo · not a model zoo |

---

## 1. Why this ranks first, stated without enthusiasm

**Contract volume is present in every `.ncd` record of the multi-market store and has only ever been
used as the roll criterion — never as a signal input.** That makes it a genuinely distinct
information surface from outright trend (`TSMOM`, closed) and from price-curve slope (`CARRY_V1`,
closed): those read *price*, this reads *participation*.

| | |
|---|---|
| data cost | **zero** — already local, already unmerged, already contract-identified |
| protected pools spent | **none** — not the NQ BBO 19, not `EFFECTIVE_14`, not the 141-session Last-only pool, not the ≥2026-08-01 seal |
| infrastructure reuse | causal active-contract engine · basis-safe self-financing returns · roll ledger · declared cycles/sectors/point values — all already built and unit-tested |

## 2. ⚠️ The ceiling, declared before anything is measured

**Every usable historical date in this substrate is already outcome-consumed** — 2009–2018 by TSMOM
development and CARRY development, 2019–2022 by TSMOM V2 validation, 2023–2026 by TSMOM TAIL-H1.

> ### **MAXIMUM HISTORICAL EVIDENCE CLASS = DISCOVERY-GRADE.**
> **No historical slice can promote a positive result to "validated."** There is no unread window
> and none can be manufactured. A positive result's only next stage is **freeze → prospective
> shadow** under the existing NO-BACKFILL rule.

This must be stated in the SPEC *before* the run, so that a good number cannot later be argued into
a stronger class. It also lowers the lane's EVI honestly — and it still ranks first, because every
alternative is either closed, more expensive, or spends an irreversible asset.

## 3. ONE mechanism — the choice to be frozen, and the ones rejected

The next wave must commit to **exactly one** economically coherent mechanism. The candidate:

> ### **LIQUIDITY-RISK PREMIUM: within-sector, markets whose participation is abnormally LOW
> ### relative to their own recent norm should command a return premium for bearing illiquidity.**

| | |
|---|---|
| economic story | thin participation ⇒ wider effective spreads, higher inventory risk, greater price impact ⇒ compensation demanded by those willing to hold |
| why it is not trend | it reads **volume**, not past returns; it is deliberately **agnostic to direction of price** |
| why it is not carry | it reads **participation**, not the near/deferred **price** relationship |
| why within-sector | a raw cross-sector volume level encodes **contract size and tick conventions**, not liquidity — the same error `CARRY_V1` §39 was built to avoid |

**Rejected in advance, with reasons, so they cannot be tried after a failure:** volume *momentum*
(that is trend wearing a hat) · volume × trend interactions (a rescue of a closed family) ·
open-interest proxies (not certified in this store) · turnover ranking across sectors (encodes
contract size) · any "volume confirms price" construction (it is a filter on a dead signal).

## 4. Data contract — what must be certified BEFORE a signal exists

A `VOLUME00` capability gate, on the `CARRY00` pattern, answering **from data, not assumption**:

- per root: volume coverage, zero-volume days, roll-window distortion, holiday/early-close effects;
- **is the volume in `db/day` the traded contract's own volume, or a merged front-month copy?**
  `TSMOM_DATA_CONTRACT` proved four ES "contracts" report **identical** volume through the merged
  path. **The unmerged store must be re-verified for volume specifically** — that check was done for
  *price*, and volume is a different field;
- roll-window contamination: volume **collapses** into expiry by construction. A liquidity signal
  that fires on expiring contracts would be measuring the calendar, not the market. The active
  contract's volume must be taken from the causal active-contract engine, with the pre-expiry buffer
  binding;
- eligibility declared on **coverage only**, never on how the backtest looks.

## 5. Frozen design skeleton (to be committed as a SPEC before any P&L)

| element | commitment |
|---|---|
| signal | `liq_score = −(log volume − trailing median log volume) / trailing sd`, strictly lagged, **within-sector centred rank** in [−1, +1] |
| why the log | volume is right-skewed by orders of magnitude; a level difference would be dominated by the largest contract |
| why a *negative* sign | the premium is claimed for **low** participation. **The sign is fixed by the economic story before the run and may not be flipped afterwards** |
| target | the existing **basis-safe self-financing** economic return |
| rebalance | **weekly**, information through the prior eligible close |
| sizing | strictly lagged 63-day vol; equal risk across active sectors |
| costs | $4.36 RT + 1 tick primary, 2 ticks stress, charged to **position changes only**; turnover and cost/gross **mandatory** |
| model | **no ML.** A single deterministic ranking rule — one primary, zero challengers |
| causality | two-sided probe (`research_sdk/causality.py`) + `timegrid` offsets, **both blocking pre-candidate gates** |
| gates | C1–C8 on the `CARRY_V1` pattern, including **concentration** — the gate that closed carry |
| chronology | 2009–2018 development. ⚠️ **Named honestly: not an unread window.** Family-specific first computation of a volume signal, on dates whose outcomes are already consumed |

## 6. What would make this lane fail fast, and that is a feature

- **volume is merged, not per-contract** → `CLOSED-BY-DATA` before a signal is written;
- **the effect is one sector or one root** → C6/C7 close it, exactly as they closed `CARRY_V1` at
  Sharpe 0.719;
- **turnover eats it** → the `TSMOM V1` failure mode, and the cost diagnostic is mandatory;
- **it is trend in disguise** → correlation with the TSMOM signal is a required diagnostic, and a
  high value closes the lane rather than being tuned away.

## 7. What this brief deliberately does not do

No feature is built. No model is fitted. No P&L exists. **The next wave must commit a SPEC — one
mechanism, one target, one causal construction, one primary model, one evidence ceiling — before a
single number is produced.** The mechanism above is a *proposal for that SPEC*, not a preregistration.
