# GRID02 — Solar Ensemble Endpoint Perturbation: Robustness Diagnostic

**Scope:** Diagnostic-only sweep over Solar13's ensemble endpoint band, holding member count (13)
and spacing (2) fixed and shifting only the `[lo,hi]` VolMult range by ±1. Per campaign directive
sec.97–99: **this is a GRID result. It cannot by itself create a new baseline candidate, select a
winner, or promote anything.** `build_pend`/`member_states`/`member_trades` are unmodified — only
the endpoint values fed into `build_pend`'s `vms` list vary. B-MOM, HTF tilt, the force-flat clock,
and both product decoders' constants are held exactly at governed values throughout (identical set
to GRID01, see that report). The incumbent-center (`[6,30]`, = GRID01's G13) reconstruction was
self-verified byte/dollar-exact against the repo's own certified dev-window nets (Product A
$177,924.40, Product B $301,915.92 as of 2026-05-31) before any endpoint value was trusted — see
`out/grid02_full_detail.json` → `self_check`.

**Inputs:** `src/run_grid02.py` (reuses `GRID01_SOLAR_RESOLUTION_CONVERGENCE/src/grid_core.py`) →
`out/grid02_performance.csv`, `out/grid02_state_agreement_vs_center.csv`,
`out/grid02_deviation_from_center.csv`, `out/grid02_full_detail.json`.

**Windows:** CANONICAL_2023_2025 (2023-01-01 → 2025-02-02, CLAUDE.md primary reporting window) and
FULL_2022_2026 (2022-01-03 → 2026-07-31, fuller history already loaded by the repo's own substrate
— no new data pull).

---

## Endpoints tested

| Band | Members | Values |
|---|---|---|
| `[5,29]` | 13 | 5,7,9,...,29 |
| `[6,30]` (**incumbent/center**, = GRID01 G13) | 13 | 6,8,10,...,30 |
| `[7,31]` | 13 | 7,9,11,...,31 |

## Headline verdict: NO CLIFF — both neighbors perform at least as well as the center

**Both immediate neighbors of the incumbent `[6,30]` band — `[5,29]` and `[7,31]` — perform at
least as well as the center in both windows, on both products.** There is no collapse at either
edge:

| Window | Metric | `[5,29]` | `[6,30]` (center) | `[7,31]` |
|---|---|---|---|---|
| Canonical | Product-A Sharpe | 1.031 | 1.030 | **1.203** |
| Canonical | Product-B Sharpe | **1.026** | 0.879 | 0.874 |
| Full | Product-A Sharpe | 1.399 | 1.307 | **1.420** |
| Full | Product-B Sharpe | **1.405** | 1.213 | 1.269 |

(Source: `out/grid02_performance.csv`.) `[7,31]` improves Product-A Sharpe to 1.203 canonical / 1.420
full (vs. 1.030 / 1.307 at center); `[5,29]` improves Product-B Sharpe to 1.026 canonical / 1.405
full (vs. 0.879 / 1.213 at center). **Neither neighbor collapses relative to the center — if
anything, this three-point comparison shows the center is not the local best of the three points on
either axis.**

Deviation from center, canonical window (`out/grid02_deviation_from_center.csv`):

| Product | Grid | Net $ deviation | % deviation |
|---|---|---|---|
| A | `[5,29]` | −$317 | −0.6% |
| A | `[7,31]` | +$9,606 | **+19.3%** |
| B | `[5,29]` | +$21,368 | **+25.6%** |
| B | `[7,31]` | +$1,188 | +1.4% |

The largest absolute deviations from center — `[7,31]` on Product A (+19.3%) and `[5,29]` on
Product B (+25.6%) — are both **improvements over center, not degradations**. This is reported
descriptively (per task instructions, the largest-deviation figure is not a performance ranking) and
should **not** be read as a case for endpoint re-optimization, which is out of scope for this
diagnostic.

State agreement with the center at the endpoints is moderate, similar in magnitude to GRID01's
resolution steps: T-target exact-match 56.9%–57.4%, entry-set Jaccard vs. center in the same range
as GRID01's G7/G25 comparisons (`out/grid02_state_agreement_vs_center.csv`). As in GRID01, aggregate
risk-adjusted outcomes stay stable (or improve) even though bar-level trade timing diverges
materially — the same methodological caveat applies here: position-agreement metrics alone would
understate how much the endpoint shift changes when trades fire.

## Convergence / robustness assessment, in full

The system does not monetize a narrow endpoint band. Both disclosed neighbors of `[6,30]`
(`[5,29]` and `[7,31]`) match or beat the center on both products in both windows — there is no
cliff, and if anything the center is not the local best of these three predefined points. This
directly answers the stated robustness question in the affirmative (broad band, not a narrow one)
without treating either neighbor's outperformance as a signal to re-optimize endpoints, which is out
of scope for this diagnostic task.

---

## Explicitly out of scope

- **No winner is selected. No candidate is promoted or frozen.** `[7,31]` and `[5,29]` outperforming
  `[6,30]` on one product each is reported as evidence of a broad, non-fragile endpoint band — not
  as a recommendation to move the incumbent's endpoints. That would require a separate,
  freshly-preregistered campaign, and a three-point comparison is far too coarse to support such a
  decision even if it were in scope.
- GRID01 (resolution convergence) is a separate sibling report; `[6,30]` / G13 is the shared
  incumbent-center row in both grids, and its numbers are reproduced identically here and there
  (cross-checked: `out/grid02_performance.csv` row `endpoint_6_30` = `out/grid01_performance.csv`
  row `G13`).

## Governance restatement (per campaign directive sec.98–99)

**Nothing in this report changes the incumbent Solar13 ensemble's endpoints, its 13 members, or any
VolMult value.** `build_pend`, `member_states`, and `member_trades` remain unmodified; the incumbent
`INCUMBENT_VMS` list (`[6,8,...,30]`) in `runs/W18R1_M1_VOLSEASON/src/common.py` is untouched. This
diagnostic answers a structural robustness question — "does the system's performance collapse near
the edges of its VolMult scale band, indicating a narrowly-optimized endpoint, or does it hold up
across a broader band?" — and the answer is **the band is broad; neither neighbor collapses, and
both neighbors match or beat center on at least one product/window combination.** That finding is
not, and must not be read as, a recommendation to change the incumbent's endpoints. Any such change
would require a separate, freshly-preregistered campaign with its own selection criteria.

## Artifacts

- Runner (reuses GRID01's `grid_core.py`): `src/run_grid02.py`
- Performance by endpoint band × window × product: `out/grid02_performance.csv`
- Bar-level / state-level agreement vs. center `[6,30]`: `out/grid02_state_agreement_vs_center.csv`
- Deviation-from-center table (canonical window, descriptive only): `out/grid02_deviation_from_center.csv`
- Full machine-readable detail (grids, windows, self-check, constants held fixed, worst-deviation-neighbor table): `out/grid02_full_detail.json`
