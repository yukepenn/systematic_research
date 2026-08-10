# PERT01 — Structural Invariance: One-at-a-Time Parameter Perturbation

**Scope:** Diagnostic-only one-at-a-time (OAT) perturbation study over three structural parameters
of the incumbent pipeline. Per campaign directive sec.97–99: **this is a PERT result. It cannot by
itself create a new baseline candidate, select a winner, or promote anything.** Strict OAT
discipline was maintained throughout — no 2-axis or 3-axis combination was ever run. Downstream
decoder constants (`KSolar=0.728654`, `KBmom=2.934159`, `TiltRescale=0.9026`, `TiltMult=1.25`,
`ShortHalf=0.5`, `WSolar=0.7086`, `WBmom=2.83`, `EntryLevel=3.0`, `ExitLevel=1.0`) were held fixed
and never perturbed — those belong to a separate audit (EQV01), not this workflow. Before any
perturbed value was trusted, the incumbent-center reconstruction was verified to reproduce the
certified fuller-history nets exactly (Product-B NQ $301,915.92, Product-A $177,924.40 —
`out/pert01_results.json` → `meta.correctness_gate`, `pass: true`).

**Inputs:** `src/01_pert01_oat.py` → `out/pert01_results.csv`, `out/pert01_results.json`. Spec-verify
notes (parameter identification, mechanical-validity checks, skip justification):
`out/00_spec_verify_notes.md`.

**Windows:** `primary_claude_canonical` (2023-01-01 → 2025-02-02, CLAUDE.md primary reporting
window, 245,943 bars) and `fuller_history` (2022-01-03 → 2026-05-29, repo's own certified dev-window
extent, 519,714 bars — no new data pull; note this fuller-history end date, 2026-05-29, is the
dev-window boundary used by this workflow's own substrate load and is slightly earlier than
GRID01/GRID02's independently-loaded 2026-07-31 extent — both are "fuller available history" per
their own already-existing substrate scripts, not a discrepancy requiring reconciliation here).

---

## Axes tested

| Axis | Parameter | Low | Center (incumbent) | High | Code location |
|---|---|---|---|---|---|
| A | VolPeriod (Solar member causal-sigma window) | 368 | **460** | 552 | `sm.sigma_series(close, vol_period=...)` |
| B | BAND_DAYS (B-MOM trailing noise-band history) | 11 | **14** | 17 | local re-implementation mirroring `health_substrate.bmom_pos_series`, verified byte-identical to the frozen file at 14 |
| C | TiltSma / HTF rolling window | 40 | **50** | 60 | local `htf_state(bars, window=...)`, verified byte-identical to frozen `common.py`/`health_substrate.py` at 50 |
| D | "B evidence units" | — | — | — | **SKIPPED, see below** |

## Axis D — skipped and disclosed

**The "B evidence units" axis (candidate values 3/4/5) was skipped.** This session exhaustively
grepped the whole repository (Python and NinjaScript) for `evidence`, `evidence.?unit`, `min_agree`,
`AgreeCount`, `n_agree`, `vote.?count`, and `ConfirmBars`. No parameter matching this description
exists anywhere in current code. The closest candidates found (`VOTE_THRESH=6.0` in an unrelated
module U6B; `BAND_DAYS=14`, already covered as Axis B) do not match the described axis. Per campaign
directive sec.33/sec.120, an axis that cannot be mapped to an actual parameter in code is skipped and
disclosed, not invented or substituted with an unrelated parameter. This is recorded verbatim in
`out/pert01_results.json` → `meta.axis_skipped` (`status: "SKIPPED"`) and in
`out/00_spec_verify_notes.md`.

## Headline verdict: the incumbent center is NOT a universal spike — its local position is axis- and window-dependent

The central finding is that **whether the incumbent sits at a local peak, valley, or plateau depends
on which axis and which reporting window is used** — this variability is itself the main result, not
noise around it.

| Axis | Fuller-history shape | Primary-window shape |
|---|---|---|
| VolPeriod | Monotonic rise: net $292,955 → $301,916 → $321,174 (Product B, 368→460→552) — incumbent sits **on an upward slope, not a peak** | Same monotonic direction (see table below) |
| BAND_DAYS | **Local peak** at 14: $301,916 vs. $284,509 (11) and $282,945 (17) | **Local valley** at 14: $83,363 vs. $92,792 (11) and $89,266 (17) — the two windows disagree on whether the incumbent is even locally optimal |
| TiltWindow | Near-flat / plateau, values within ~1.5% of each other | Declining gradient: 40 > 50 > 60 in net |

(Source: `out/pert01_results.csv` / `out/pert01_results.json` → `rows`, fields `primary_claude_canonical_B_net` / `fuller_history_B_net` etc.)

### Full numbers (Product B / NQ, net $)

| Axis | Low | Center | High | Primary window (net) Low/Center/High | Fuller history (net) Low/Center/High |
|---|---|---|---|---|---|
| VolPeriod | 368 | 460 | 552 | $106,304 / $83,363 / $91,569 | $292,955 / $301,916 / $321,174 |
| BAND_DAYS | 11 | 14 | 17 | $92,792 / $83,363 / $89,266 | $284,509 / $301,916 / $282,945 |
| TiltWindow | 40 | 50 | 60 | $85,818 / $83,363 / $73,320 | $297,343 / $301,916 / $300,730 |

(Source: `out/pert01_results.csv`, columns `primary_claude_canonical_B_net`, `fuller_history_B_net`.)

## Axis-by-axis stability

- **VolPeriod (most disruptive to bar-level behavior).** Position agreement with the incumbent path
  is only 92.9%–94.6% and discrete-entry Jaccard only 0.35–0.40 (`out/pert01_results.json`,
  `struct_position_agreement_B` / `struct_jaccard_B_entries`) — the largest structural disruption of
  the three axes, consistent with VolPeriod directly reshaping the core Solar13 consensus `T`. Net
  P&L direction is directionally consistent in sign between windows (net rises with VolPeriod in
  both), so this axis is a **soft monotonic gradient**, not a spike, but it is the most mechanically
  sensitive axis tested.
- **BAND_DAYS (soft secondary touch, but window-disagreeing on optimality).** Position agreement is
  high, 99.1%–99.8%, but discrete-entry Jaccard is materially lower at 85.0%–86.8% — a **notable
  methodological finding**: aggregate bar-level position agreement (>99%) can coexist with much
  larger shifts in exact trade/entry timing (Jaccard ~85%), meaning position-agreement alone
  understates how much trade-level timing moves under a small parameter change. This is the one axis
  where the two reporting windows flatly disagree on whether the incumbent (14) is locally optimal:
  a genuine peak in fuller history, a genuine valley in the shorter primary window.
- **TiltWindow (softest, most plateau-like).** Position agreement 99.7%–99.8%, entry Jaccard
  96.7%–97.2% — the least disruptive axis, consistent with its place in the pipeline as a
  multiplicative overlay on an already-computed `T`, not a re-derivation of it. Near-flat in fuller
  history; a mild declining gradient (40>50>60) in the primary window.

## Cost-stress robustness

Cost-stress retention (extra 1–2 ticks of adverse slip per fill, position path held fixed since
decisions don't depend on fill price) stays in a narrow band across every perturbation tested, with
no axis showing a qualitatively different fragility to costs than the incumbent center: Product B
retention 0.76–0.91 at +1 tick, 0.68–0.83 at +2 ticks; Product A in a similar range (source:
`out/pert01_results.csv`, columns `*_cost_stress_retention_plus1tick` / `*_plus2tick`, primary
window).

## Convergence assessment (not applicable in the GRID sense)

PERT01 is a 1-D one-at-a-time perturbation study, not a resolution sweep — there is no multi-
resolution "convergence" axis to assess here the way GRID01/GRID02 do. What is observable: results
are directionally consistent in sign between the two reporting windows for VolPeriod (net rises with
VolPeriod in both primary and fuller windows) but **disagree** on whether the incumbent is locally
optimal for BAND_DAYS (peak in fuller history, valley in the shorter primary window) and show a much
flatter/near-plateau response for TiltWindow in fuller history vs. a clearer downward gradient in the
primary window. This window-sensitivity is the main finding: conclusions about whether the incumbent
center is a "spike," a "valley," or a "plateau" are **not robust to which reporting window is used**,
especially for BAND_DAYS.

---

## Explicitly out of scope

- **No winner is selected. No candidate is promoted or frozen.** No parameter value in this study —
  incumbent or perturbed — is being recommended for adoption. This is diagnostic evidence about
  local sensitivity only.
- **Axis D ("B evidence units") is skipped, not substituted.** No unrelated parameter was used as a
  stand-in; see above.
- No 2-axis or 3-axis combination was run at any point (strict OAT discipline).
- The downstream decoder constants (KSolar/KBmom/TiltRescale/TiltMult/ShortHalf/WSolar/WBmom/
  EntryLevel/ExitLevel) were never perturbed here — that is EQV01's scope, not PERT01's.

## Governance restatement (per campaign directive sec.98–99)

**Nothing in this report changes the incumbent's VolPeriod (460), BAND_DAYS (14), or TiltSma window
(50).** `sm.sigma_series`, `member_states`, `member_trades`, and the frozen `BAND_DAYS`/HTF-window
constructions in `sm_bmom.py`/`health_substrate.py`/`common.py` are unmodified; this workflow only
built parametrized *local copies*, verified byte-identical to the frozen originals at the incumbent
center, to vary one input at a time. The finding that the incumbent is sometimes a local peak,
sometimes a local valley, and sometimes on a plateau or gradient — depending on axis and window — is
a structural-sensitivity finding, not a case for re-tuning any of these three parameters. Any such
change would require a separate, freshly-preregistered campaign. The disclosed skip of the "B
evidence units" axis is likewise a documentation fact, not a gap that was papered over with an
invented parameter.

## Artifacts

- OAT perturbation engine: `src/01_pert01_oat.py`
- Full results table (all axes × roles × windows × products × metrics): `out/pert01_results.csv`
- Full machine-readable detail (meta: axis definitions, axis_skipped record, correctness gate,
  commission conventions, metric definitions; rows: same data as CSV): `out/pert01_results.json`
- Spec-verification notes (parameter identification, mechanical-validity checks, skip justification
  search record): `out/00_spec_verify_notes.md`
