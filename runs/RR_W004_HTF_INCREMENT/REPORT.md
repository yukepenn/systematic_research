# RR_W004 — HIGHER-TIMEFRAME STATE ADDS NOTHING

| | |
|---|---|
| spec | `spec.yaml`, committed **`50ddd4f`** before this code existed |
| code | `run_rr_w004_htf.py` |
| stage | **A — INFORMATION ONLY.** No router, no policy, no sizing, no exit change, no HMM |
| seal | untouched · `DISCOVERY_CONSUMED` throughout · 2026-05-31 → 07-31 `DIRECTLY_BURNED` |
| promoted | **nothing** |

> ### **H1 PASS · H2 FAIL · H3 FAIL · H4 PASS · H5 PASS → NOT ALL PASS.**
> ### **HIGHER-TIMEFRAME moves from `LIGHT` to `CLOSED`.**
> ### ⚠️ **H1 and H4 passed on a comparison between two arms that are both worse than chance.
> ### Their passing carries no evidential weight, and §3 says why.**

---

## 1. Both blocking gates passed first

**Causality.** All six HTF features are immune to their own decision bar (0.0 % moved), and the
injected probes behave: `PROBE_LEAK_close_i` → **DROP** (100 % moved by its own bar),
`PROBE_SAFE_close_prev` → **KEEP**. Nothing was dropped, nothing was hand-repaired.

**Pipeline reproduction.** The claim that everything except the HTF arm is inherited unchanged from
RR_W002A is not asserted — it is certified:

| | |
|---|---:|
| RR_W002A primary rank correlation | **−0.0302** |
| reproduced here | **−0.0302** ✅ |

## 2. The arms

Target: `delta_total_window`, 2,131 decisions, 13 expanding prequential folds, ridge only.

| arm | features | OOS ρ | vs `X_ONLY` | folds + |
|---|---:|---:|---:|---:|
| `X_ONLY` (RR_W002A's primary) | 18 | −0.0302 | — | 54 % |
| `HTF_ONLY` | 6 | −0.0184 | +0.0118 | 38 % |
| **`X_PLUS_HTF`** | **24** | **−0.0185** | **+0.0117** | 31 % |
| `NEGCTRL` (known-null) | 2 | −0.0345 | −0.0043 | 62 % |

### The nulls — entire walk-forward refitted inside every shift

| arm | real ρ | null p50 | null p95 | **percentile** | |
|---|---:|---:|---:|---:|---|
| `X_PLUS_HTF` | −0.0185 | −0.0292 | +0.0411 | **61.5th** | fail |
| `HTF_ONLY` | −0.0184 | −0.0436 | +0.0329 | **71.0th** | fail |
| `NEGCTRL` | −0.0345 | −0.0785 | +0.0370 | **77.0th** | fail |

## 3. Why the two "passes" are worthless — and this is the point of the wave

**H1 asked whether `X_PLUS_HTF` beats `X_ONLY`.** It does: −0.0185 against −0.0302. **But both are
negative**, and both sit below the median of their own nulls. H1 is therefore a pass at *being less
bad than something already worse than chance*. It is not evidence that HTF carries information.

**H4 asked whether the increment is positive in ≥ 60 % of folds.** It is, at 62 %. **But it is an
increment between two negative quantities**, and adding HTF made the fold-level *sign* consistency
**worse**, from 54 % to **31 %**.

```
per-fold X_ONLY : +0.008 -0.286 +0.003 +0.071 +0.116 -0.132 -0.063 -0.081 +0.014 +0.183 -0.067 -0.157 +0.003
per-fold X+HTF  : -0.050 -0.223 -0.012 -0.017 +0.075 -0.075 -0.016 -0.027 +0.024 +0.209 +0.011 -0.103 -0.063
```

**H2 and H3 are the gates that actually test for information, and both fail.** `X_PLUS_HTF` lands at
the **61.5th** percentile of its own refitted null; `HTF_ONLY` standing alone at the **71.0th**.

> ### ⚠️ **The known-null negative control sits at the 77.0th percentile — HIGHER than either real
> ### arm.** A family this campaign has already proven carries nothing (W111 1-minute volume, W122
> ### cross-market intraday support) out-scores both HTF arms against the same null. That is the same
> ### pattern RR_W002A found, and it is the cleanest available statement that there is nothing here.

**This is exactly the shape that invites "promising, needs tuning."** Two gates pass, the pooled
number improves, and a fold-count crosses a threshold. **That reading is refused.** The gates that
carry the evidential load are the ones comparing against a refitted null, and they fail — while the
negative control beats the real arms. **No horizon, no additional feature and no different model is
authorised by this result.**

## 4. What this closes

**HIGHER-TIMEFRAME → `CLOSED`.** It was the last surface `INFORMATION_COVERAGE` marked `LIGHT`, its
only prior evidence was `HTFMECH01` from **campaign #3 on a different object**, and it had never been
tested at `P1/PCT`'s own decision events. Now it has been, incrementally and against the strongest
null this campaign builds.

> ### **With this, the statement *"no tested current information surface separates `P1` action
> ### quality"* is COMPLETE rather than partial.**

**What it does not close.** HTF is untested as a *standalone directional* mechanism, and untested for
`XM_CONFLICT` or `FOLLOW_MORNING`. This wave asked one question — does it add incremental information
about `P1/PCT` action value — and answered it.

**Prior honoured.** The spec said the honest expectation was another null, and gave two reasons: HTF
is a transformation of an NQ path already labelled `DEEP`, and RR_W002A had already returned null for
a 12-feature within-session NQ arm. **Running it anyway was still right** — leaving a surface
un-closed on a low prior is precisely how *"not separable by any information source currently held"*
became an overclaim, and correcting that cost more than this wave did.

## 5. Continuation

| | |
|---|---|
| **outcome** | **FAIL — HTF adds nothing.** `LIGHT` → `CLOSED` |
| **next** | frontier rows 4–5, both **LOW** and both engineering: selective box un-latching, book coverage |
| **the only high-ceiling rows left** | order flow, options, a wider event calendar — **all owner-gated acquisition** |
| **router / HMM** | remain **DE-PRIORITISED** and **NOT RUN** |
| **promoted / demoted** | **nothing** |
