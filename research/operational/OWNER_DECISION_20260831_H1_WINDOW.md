# OWNER DECISION — 2026-08-31 — `GENESIS_H1` PRISTINE CONFIRMATION WINDOW

## THE DECISION

**Owner authorised, in chat, 2026-08-31: the `GENESIS_H1` pristine one-shot confirmation window may
be consumed.** Verbatim: `允许消耗这个窗口。`

## WHAT EXACTLY IS BEING SPENT

From `runs/GENESIS_H1_VOLSTATE_20260828/spec.yaml`:

```
windows:
  confirmation_one_shot: 2022-01-01 -> 2026-07-31, chronological, frozen rule, read ONCE
```

And the deferral that has been holding it, `runs/G2_F1_COND01_20260829/spec.yaml:10-13`:

> "B2's MC-22 primary wanted VIX daily levels 2022+ — that is H1's PRISTINE VX-family confirmation
> [window] … The VIX-level increment is deferred to a separate one-shot confirmation spec IF gate B
> passes here. **The pristine window is not read by this run.**"

**It is a ONE-SHOT. It can be spent exactly once, ever, on a rule frozen and committed before the
read.** There is no undo. Authorisation is permission, not obligation — declining to spend it on a
weak rule remains the correct action.

## HOW IT IS BEING SPENT — the discipline is not relaxed by the authorisation

This follows the structure recommended to the owner before authorisation was given, and the owner
authorised on that basis:

1. **DISCOVERY, PRE-2022 ONLY** (`G3_VOLSHORT01`, running). Five specifications — VXN levels, VIX
   levels, ex-ante variance and the variance risk premium, VIX term structure and vol-of-vol, and
   *change* rather than level — each attacked by an independent adversary on six axes: the
   realised-vol confound, episode concentration, the anti-filter identity, the overnight sign-flip
   placebo, cost realism at the corrected $20.65/ctrRT floor, and a look-ahead audit.
   **A hard wall at 2022-01-01 is asserted in code and printed.**
2. **FREEZE.** One rule, complete enough that an implementer makes **zero** further choices — vol
   measure, lookback, quantile construction, state definition, entry and exit times, direction per
   state, size, cost line. Any ambiguity is a degree of freedom the one-shot cannot afford. The
   freeze agent is explicitly permitted, and encouraged, to return `recommend_confirmation = false`.
3. **COMMIT the frozen rule** before any 2022+ byte is read.
4. **READ ONCE.** Chronological, no edits, result recorded whatever it is.

## THE THREE ARMS THAT MUST APPEAR TOGETHER

The mechanism claims implied vol is a **signed short direction**, not an exposure gate. That
distinction is the entire difference between this and the ten dead anti-filters, so it is tested
directly rather than assumed:

| arm | construction |
|---|---|
| **(R) ROUTER** | long in the low-vol state, **short** in the high-vol state |
| **(F) FILTER** | long-only, high-vol sessions merely **removed** |
| **(S) SHORT** | always-short on the high-vol sessions **alone** |

**If `net(R) ≈ net(F)`, the router is exposure reduction wearing a costume and dies under the closed
anti-filter family.** If (S) cannot beat a rate-matched random-short placebo, it dies for the same
reason.

## INFERENCE — session-level t-statistics are banned here

High-vol sessions arrive in **episodes**. ~600 raw high-VIX sessions cluster into perhaps 8–14
independent ones, so a session-level t is fiction. Episodes are maximal runs separated by ≥ 10
calendar days; the episode **count** is printed beside every statistic; inference is a whole-episode
block bootstrap with `K_eff = K / (1 + (K−1)·ρ̄)` and `ρ̄` printed. A session-level t may appear
labelled **DIAGNOSTIC ONLY**.

## THE HONEST PRIOR, RECORDED BEFORE THE READ

**I expect this to fail**, and that is why it is worth running rather than being a formality:

- `GENESIS_H1` already measured **neighbouring point estimates running the wrong way** for this
  thesis — stress sessions had *higher* next-session means; VXN/VIX secondary −0.0554%, t −1.87.
- This repo's anti-filter / exposure-reduction record is **ten for ten against random controls**.
- The effective-N problem is **structural, not fixable with more data**: no amount of history turns
  8–14 episodes into 600 independent observations.

**A null here is a real closure** — it retires the volatility-state axis for *direction*, which is
the last cheap short-side idea external mining produced.

## COST FLOOR CORRECTION APPLIED

Every WAVE B candidate assumed ~0.9 NQ points per round turn. `G2_EXEC01_P1_EXECUTION_20260828`
measured **$20.65/ctrRT** all-in (median $20.00, p90 $35.00) on 113 real round turns = **1.03 NQ
points**. All three lines are printed ($4.36 commission-only as a **floor, never a headline**;
$20.65 **primary**; $25.01 standing all-in).

## WHAT THIS AUTHORISATION DOES **NOT** COVER

- It does **not** authorise a real-money order, a deployment, or any change to the live book.
- It does **not** authorise reading the **data seal** (≥ 2026-08-01). The pristine window ends
  2026-07-31 and the seal is untouched.
- It does **not** authorise a second read. If the confirmation fails, the window is **spent** and a
  reparameterised successor is not available — that would be the parameter rescue §37 rejects.
- It covers the **VX-family confirmation window only**, not any other preserved pool.

`LIVE = NO · $0 · NO ORDER PLACED`
