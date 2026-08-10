# PLACEBO01 — B-MOM causal placebo test — PREREGISTRATION

**Written 2026-08-10, BEFORE any placebo realization is generated or looked at**, per campaign
directive sec50. This file fixes the number of randomizations, the seed family, and the exact
null construction. `01_bmom_placebo.py` asserts its own runtime constants equal the values below
before writing any result — if a future edit changes `N_REPS`/`BASE_SEED`/the null construction
without updating this file first, the script fails closed rather than silently drifting from what
was preregistered.

**Provenance note (added after the fact, does not change any content below):** this file was
originally written to `out/PREREGISTRATION.md`, a generic filename. That directory is shared with
at least two concurrently-running sibling placebo workflows in this same session (an HTF placebo
and a sizing placebo, targeting the same `PLACEBO01_COMPONENT_CAUSALITY/out/` directory with their
own generically-named `PREREGISTRATION.md`/`preregistration.json` files), and the generic filename
was overwritten by one of those siblings after this file was written but before `01_bmom_placebo.py`
finished running. The content below is recovered byte-for-byte from this task's own original write
(same session, same tool call, prior to the collision) — it was genuinely written and committed to
this reasoning trace BEFORE `01_bmom_placebo.py` was ever executed, and `01_bmom_placebo.py`'s own
hardcoded `N_REPS=500`/`BASE_SEED=20260810` constants (which do not depend on this file's content
at runtime — the script only checked the generic path's existence, not its content) match this
record exactly. Re-saved here under a collision-resistant filename for a durable, correctly
attributed record.

## 1. Number of randomizations

**N_REPS = 500** (>= the recommended 200 floor). Chosen for percentile resolution: with 500 draws
the empirical percentile of the real B-MOM contribution is resolvable to 0.2% granularity (1/500),
comfortably below the coarseness that would make a "real lands at the 97th vs 99th percentile"
distinction noise. Computationally cheap (~500 x ~0.35s per rep-pair of exec loops on the
canonical-window slice, ~3 minutes total) so there is no cost-driven reason to use fewer.

## 2. Seed family

**BASE_SEED = 20260810.** Replicate `i` (`i = 0 .. 499`) uses its own `numpy.random.default_rng(
seed=BASE_SEED + i)` instance, used for exactly one draw (the circular-shift offset `K` for that
replicate) and nothing else. Fully deterministic and reproducible: rerunning the script with the
same code produces byte-identical `K` values and therefore byte-identical placebo results. No
time-seeded or unseeded randomness anywhere in this workflow.

## 3. Null construction (decided before any placebo result is generated or inspected)

**Unit being shifted**: the REAL, unperturbed `bmomPos` bar-level array (`{-1,0,+1}`), restricted
to the canonical window (2023-01-01 .. 2025-02-02, `grid_core.CANON_MASK`), as ALREADY certified
by `grid_core.py`'s own import-time self-check against the campaign's certified dev-window nets
(Product A $177,924.40, Product B $301,915.92) — see correctness gate in the main script.

**Session universe for the shift**: the `M` unique trading sessions whose `sess_date` falls inside
the canonical window (a closed, self-contained pool — donor sessions are drawn ONLY from other
sessions already inside the same window, never from outside it). This is a deliberate design
choice (disclosed, not hidden): it makes the shuffle an exact bijection on the same multiset of
real per-session B-MOM paths that are already present in the window, so activation frequency,
state-duration distribution, time-of-day distribution, year composition, and volatility
composition are preserved by construction (not merely approximately) — every real session path
that existed in the window before the shuffle is still present exactly once after it, just glued
to a different day.

**Shift mechanism**: for replicate `i`, draw a single integer offset `K_i ~ Uniform{1, ..., M-1}`
(via that replicate's own seeded RNG, `rng.integers(1, M)`). Order the `M` canonical-window
sessions chronologically (`sessions_c[0..M-1]`). Session at chronological rank `r` receives the
COMPLETE, INTACT bmomPos path that real session `sessions_c[(r + K_i) mod M]` produced — the
donor's own within-day sequence (activation timing, duration of each {-1,0,1} state, values at
every RTH time-of-day slot 09:33..15:57) is reused byte-for-byte, only its calendar-day label
changes. Because `K_i != 0 (mod M)`, no session can ever receive its own real path back — this is
a genuine placebo shuffle, not an identity no-op, for every single one of the `M` sessions
simultaneously (a true circular shift, exactly as specified in the task instructions — NOT an
independent per-session random permutation, which would not preserve the block/serial structure
the task explicitly asked to keep intact).

**Within-day reattachment rule**: donor and target sessions do not always share an identical
intraday bar grid (the ~43 CME holiday early closes in this history end before the regular 16:00
ET RTH close). Reattachment is done by TIME-OF-DAY (`hm = hour*100+minute`), not by raw bar
position: target bar at time-of-day `h` receives the donor session's own bmomPos value at that
SAME `h` if the donor session actually had a bar at `h`; if the donor session had already ended
(early close) before `h`, the target bar is set flat (`0`) for that slot — the same value the
donor's own path would have shown had it continued (B-MOM is always flat after its own session's
close). This is the rule that best preserves "time-of-day distribution" as stated in the task
instructions, and only touches the minority of donor/target pairs that involve an early-close
session on either side. Bars outside RTH (09:33-16:00 ET) are always 0 for both real and placebo
B-MOM (B-MOM never holds a position overnight), so they need no reattachment logic.

**What stays real / unperturbed in every replicate**: the Solar13 signal (`T`), the HTF tilt state,
the C4 entry-block/forced-flat overlay clocks, and both products' decoder formulas and frozen
constants (`KSolar=0.728654, KBmom=2.934159, TiltRescale=0.9026, TiltMult=1.25, ShortHalf=0.5` for
Product A; `WSolar=0.7086, WBmom=2.83, EntryLevel=3.0, ExitLevel=1.0` for Product B) — ONLY the
`bmomPos` array fed into each product's `M` computation is replaced by that replicate's shuffled
version. No constant is perturbed here (that is EQV01/PERT01's job, not this workflow's).

## 4. Comparison baseline and statistic

`solar_only`: the same exact pipeline (both products) with `bmomPos` set identically to 0 for
every bar in the canonical window (B-MOM entirely removed, Solar+HTF alone) — NOT the real full
incumbent. This isolates B-MOM's own marginal contribution.

For each replicate `i` and each product `P in {A, B}`, compute on the canonical-window daily net
series (via `dd_battery`): `net`, `sharpe`, `maxDD_eod`, and `turnover` (total contracts changed
hands, `sum(abs(diff(bar_pos)))`, with an implicit leading flat state). Null draw:
`Delta_placebo[i, P, metric] = placebo[i, P, metric] - solar_only[P, metric]`.

`Delta_real[P, metric] = real_full[P, metric] - solar_only[P, metric]` (real, unshuffled B-MOM).

**Reported statistic**: the empirical percentile of `Delta_real[P, metric]` within the 500-draw
null distribution `{Delta_placebo[i, P, metric]}_{i=0..499}`, computed as
`100 * (count(Delta_placebo <= Delta_real) + 0.5*count(Delta_placebo == Delta_real)) / N_REPS`,
reported separately for net, Sharpe, drawdown, and turnover deltas, separately for Product A and
Product B. This percentile — not a binary "beats placebo yes/no" — is the primary output.

## 5. Correctness gate (must pass before any placebo result is trusted)

1. `grid_core.py`'s own import-time self-check: the incumbent (real, unshuffled) grid reproduces
   the campaign's certified dev-window (2022-01-03..2026-05-31) nets EXACTLY for both products
   (Product A $177,924.40, Product B $301,915.92) — this module is imported, not reimplemented,
   so this check runs automatically and fails loudly (`AssertionError`) if it does not hold.
2. An additional check specific to this script: slicing the canonical-window bars BEFORE running
   the per-bar execution loop (done here, for speed — canonical window is <half the full history)
   must reproduce IDENTICAL per-bar PnL to slicing grid_core's full-history execution AFTER running
   it. This is expected to hold exactly because both products are flat at every session close (no
   state ever carries across a session boundary, confirmed structurally in both execution loops
   below and in CLAUDE.md's own frozen conventions) and the canonical window's start (2023-01-01)
   falls exactly on a session boundary — checked explicitly, not assumed, before any placebo
   replicate runs.

## 6. What this test is NOT

This is falsification science, not an alpha trial (sec50). A reassuring null (real B-MOM lands in
the tail, beating essentially all placebo draws) and a concerning result (real B-MOM looks like a
typical placebo draw, i.e. its benefit is indistinguishable from just adding un-informed exposure/
turnover) are both being actively sought and will both be reported with equal rigor. No placebo
draw is discarded, re-rolled, or chosen after being seen.
