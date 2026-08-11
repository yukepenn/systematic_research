# DOM01 Data Governance — chronological states, readiness rule, protected-pool reservation

Companion to `DOM01_PROSPECTIVE_PROTOCOL.md` (the frozen mechanism, DOM-M1). This document
defines what happens to DOM01 session data *before* any hypothesis is ever tested against it, and
the mechanical rule for deciding when a batch is even eligible to be *proposed* for opening — never
sufficient to open it, per section 2.

## 1. Chronological data states

Four states, assigned per collector run (per `RunId`/manifest), never per individual row. A run
moves strictly forward through these states; it never moves backward, and promotion is always a
recorded, dated event, never implicit.

```
ENGINEERING_BURNIN  ->  SEALED_FORWARD  ->  PROSPECTIVE_DISCOVERY  ->  (read once, then archived)
                                       \->  PROTECTED_CONFIRMATION  ->  (read once, then archived)
```

### `ENGINEERING_BURNIN`

Any DOM01 run collected, or structurally inspected during tool/collector development, before
`DOM01_PROSPECTIVE_PROTOCOL.md`'s own freezing commit (`3b68551`, 2026-08-11). Permanent, terminal
state — an `ENGINEERING_BURNIN` run never promotes to any other state, regardless of later QC
status. Exactly one run qualifies today: `5c8ca242e2d24960a3f2863876541488`
(`StartUtc=2026-08-11T22:03:50Z`). This is not a punitive label — the run is genuinely useful for
exactly what it was used for (building `dom01_qc_monitor.py`, verifying feed semantics in
`DOM01_PROSPECTIVE_PROTOCOL.md` sec1) — it is simply disqualified from ever being counted as
discovery or confirmation evidence, because its structural characteristics were directly observed
before the mechanism was frozen.

### `SEALED_FORWARD`

**The default state for every run collected after the protocol-freeze commit, once it has passed
`dom01_qc_monitor.py` clean (verdict `CLEAN_PASS` or `WARN` with no `FAIL`-level check).** A run
that fails QC stays `SEALED_FORWARD` and is additionally flagged `QC_FAILED` — it does not count
toward the readiness tally in section 3 until re-checked and passing, and the failure cause is
recorded (engineering defect vs. feed-entitlement gap vs. genuinely nothing wrong, per
`dom01_qc_monitor.py`'s own README).

**Crucially: reaching every readiness condition in section 3 does NOT move a run out of
`SEALED_FORWARD`.** Every DOM01 session collected during `LOCKED_FORWARD.md`'s virgin window
(≥2026-08-01) is, by that document's own text, consumable only through explicitly authorized
channels — and `LOCKED_FORWARD.md` predates DOM01's existence, so it says nothing DOM-specific.
The conservative reading, per this task's own instruction, is to treat that silence as **not**
an authorization: DOM data collected inside the virgin window stays sealed by default, the same
way price/OHLCV data in that window would, until the owner separately and explicitly authorizes a
transition for this specific new information class. `SEALED_FORWARD` is where essentially all
real DOM01 data will sit, indefinitely, unless that authorization happens.

### `PROSPECTIVE_DISCOVERY`

A batch of `SEALED_FORWARD` sessions may enter this state **only** via a dated, explicit owner
authorization event, recorded in the ledger this document establishes (section 4) — never
automatically, never merely because section 3's readiness threshold is reached. Once authorized,
sessions in this state may be read exactly once under a genuinely preregistered
`EXPLORATORY_DISCOVERY`-classified run (per `research_sdk/prereg_guard.py`'s run-class taxonomy)
testing DOM-M1 as frozen in `DOM01_PROSPECTIVE_PROTOCOL.md` — no other hypothesis, no feature
sweep. After that one read, the batch is archived (still retained, per `CLAUDE.md`'s "never delete
raw research evidence" rule — "archived" means "not re-read for a second bite," not "deleted").

### `PROTECTED_CONFIRMATION`

Mirrors Auction's own established precedent (`PROTECTED_EVIDENCE_BUDGET.md`,
`W5_PROTECTED_CONFIRMATION`): at the moment discovery is authorized, a held-out fraction of the
then-available `SEALED_FORWARD` sessions is reserved *before* any discovery read happens, and is
never touched by the discovery run. It can only be opened later via its own separate, one-shot
preregistered confirmation protocol — written after discovery's result is known, but before the
protected sessions are read, exactly matching this campaign's standing methodology. Reservation
fraction: **30%** of the batch entering discovery authorization (matching the rough order of
Auction's own 168-of-~200-ish session split precedent, i.e. discovery gets the majority, a genuine
minority is held back) — rounded to the nearest whole session, minimum 5 sessions reserved once
the batch is large enough to split at all.

---

## 2. Why "enough data exists" never bypasses the seal

This section exists because it is the single easiest rule in this document to accidentally
violate under a "we've waited long enough" framing. Restated plainly: **the readiness rule in
section 3 governs a queue, not a gate.** Meeting it means a batch becomes *eligible to be proposed
to the owner* for a `PROSPECTIVE_DISCOVERY` authorization decision. It does not, by itself, open
anything. If the owner does not authorize a transition, `SEALED_FORWARD` sessions stay sealed
indefinitely, exactly like any other virgin-window data under `LOCKED_FORWARD.md` — accumulating
value as evidence, not decaying by sitting unread.

---

## 3. Prospective readiness rule

A batch of `SEALED_FORWARD` sessions becomes **proposal-eligible** (not authorized — see section
2) when all three of the following hold. Every input is a QC-completion or structural-incidence
count; **none is an observed return, PnL, Sharpe, p-value, or candidate-performance figure** — DOM
data is never read for those quantities before an authorization event, so none could be used even
if someone wanted to.

**(a) QC completeness.** Every session in the batch has a `dom01_qc_monitor.py` verdict of
`CLEAN_PASS` or `WARN`-with-zero-`FAIL`, and the cross-run rollup shows no unexplained contract
gap (a rollover is fine and expected; an unexplained multi-day collection gap is not, and must be
understood — engineering cause vs. simply not running that day — before the session counts).

**(b) Minimum QC-passed independent (session-clustered) count**, sized by a standard
cluster-randomized power calculation, not a fixed folklore number:

```
N_sessions >= ceil( DEFF * (z_{1-alpha/2} + z_{power})^2 * (sigma_std / effect_min_std)^2
                     / events_per_session )
```

where:
- `alpha = 0.10`, `power = 0.80` (two-sided 90% CI / 80% power — matches this campaign's existing
  dual-clustered-bootstrap convention throughout Auction/ACTIONMAP01, not a new standard invented
  here).
- `effect_min = 2.872 ticks` (the frozen `C1` cost hurdle, `DOM01_PROSPECTIVE_PROTOCOL.md` sec3.7).
  Standardized via `effect_min_std = effect_min_ticks * TICK / sigma460_bar_H3`, where
  `sigma460_bar_H3` is the **existing, already-public, non-DOM** `sigma460` volatility state's own
  typical 3-bar dispersion — reused exactly as-is from the current live decision object, never
  fit or adjusted for this purpose. This keeps the planning input honest: it sizes the sample
  using how noisy price already is, not any property of the new DOM feature being tested.
- `sigma_std = 1.0` by definition once `effect_min` is expressed in the same standardized units.
- `events_per_session` = the empirically observed mean count of DOM-M1-eligible bars per session
  (section 3.2's eligibility filter: `target_exposure_A(t)≠0` AND `flow(t)≠0` AND ≥1 classifiable
  trade) — a pure **incidence** count, computable from QC-passed structural data alone, without
  ever touching `close(t+H)`.
- `DEFF = 1 + (events_per_session - 1) * ICC`, the standard cluster-design-effect correction for
  within-session autocorrelation of order-flow events; `ICC` (intraclass correlation) is planned
  at **0.10** as a conservative starting assumption (typical range for intraday microstructure
  series; revisit only if `events_per_session`'s own empirical distribution shows something
  clearly different — this is a structural/incidence observation, not an outcome one, so revising
  it does not violate the no-outcome-peeking rule).

As of this document's commit, **zero `SEALED_FORWARD` sessions exist yet** — the one collected run
is `ENGINEERING_BURNIN`. `events_per_session` and the resulting `N_sessions` are therefore not yet
computed; this formula is frozen now so the first real batch is evaluated mechanically, not
improvised under time pressure, the same discipline `research/data_forward_sealed/DOM01/README.md`
already established for completeness reporting.

**(c) No unexplained `QC_FAILED` runs in the candidate window.** A batch with open, uninvestigated
QC failures does not round up to "probably fine" — every `FAIL`-level check in the window must be
resolved (understood and either fixed or explained) before that window's sessions count.

---

## 4. Authorization ledger (append rows here, never edit past rows)

| Date | Event | Sessions affected | Owner decision reference |
|---|---|---|---|
| 2026-08-11 | `DOM01_PROSPECTIVE_PROTOCOL.md` + this document frozen and committed. Zero sessions promoted. | n/a | This commit |

No further rows exist yet. The next row this document expects is either (a) a QC-failure
resolution note, or (b) an explicit owner authorization moving a named batch from
`SEALED_FORWARD` to `PROSPECTIVE_DISCOVERY` with a reserved `PROTECTED_CONFIRMATION` split
recorded in the same row. Nothing else may add a row here.
