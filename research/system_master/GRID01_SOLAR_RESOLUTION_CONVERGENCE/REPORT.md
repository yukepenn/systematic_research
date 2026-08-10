# GRID01 — Solar Ensemble Resolution: Convergence Diagnostic

**Scope:** Diagnostic-only sweep over Solar13's ensemble member count/spacing. Per campaign
directive sec.97–99: **this is a GRID result. It cannot by itself create a new baseline candidate,
select a winner, or promote anything.** `build_pend`/`member_states`/`member_trades` are unmodified
throughout — only the `vms` list fed into `build_pend` (`runs/W18R1_M1_VOLSEASON/src/common.py`)
varies. B-MOM (`BAND_DAYS=14`), HTF tilt (`rolling(50)`), the force-flat clock, and both product
decoders' constants are held exactly at governed values throughout (`KSolar=0.728654`,
`KBmom=2.934159`, `TiltRescale=0.9026`, `TiltMult=1.25`, `ShortHalf=0.5` for Product A;
`WSolar=0.7086`, `WBmom=2.83`, `EntryLevel=3.0`, `ExitLevel=1.0` for Product B). Before any grid
value was trusted, the incumbent-center (G13) reconstruction was self-verified byte/dollar-exact
against the repo's own certified dev-window nets (Product A $177,924.40, Product B $301,915.92 as
of 2026-05-31) — see `out/grid01_full_detail.json` → `self_check`.

**Inputs:** `src/grid_core.py`, `src/run_grid01.py` →
`out/grid01_performance.csv`, `out/grid01_state_agreement_vs_G13.csv`,
`out/grid01_solar_e10_only_context.csv`, `out/grid01_full_detail.json`.

**Windows:** CANONICAL_2023_2025 (2023-01-01 → 2025-02-02, CLAUDE.md primary reporting window) and
FULL_2022_2026 (2022-01-03 → 2026-07-31, fuller history already loaded by the repo's own substrate
— no new data pull).

---

## Grids tested

| Grid | Members | Spacing | Values |
|---|---|---|---|
| G7 | 7 | even step-4 | 6,10,14,18,22,26,30 |
| G13 | 13 (**incumbent**) | even step-2 | 6,8,10,...,30 |
| G25 | 25 | dense step-1 | 6,7,8,...,30 |
| G49 | 24 | half-integer offset, step-1 | 6.5,7.5,...,29.5 (spec-verify-disclosed as mechanically valid; see governance note below) |

## Headline verdict: CONVERGES, with one disclosed exception

**G7 → G13 → G25, along the incumbent's own even-integer spacing pattern, converge smoothly.**
Moving from 7 to 13 to 25 members produces no discontinuity, no spike, and no cliff in
aggregate risk-adjusted performance, in either window:

| Window | Metric | G7 | G13 (incumbent) | G25 |
|---|---|---|---|---|
| Canonical | Product-A net / Sharpe | $51,743 / 1.077 | $49,704 / 1.030 | $49,704 / 1.001 |
| Canonical | Product-B net / Sharpe | $80,967 / 0.906 | $83,363 / 0.879 | $77,719 / 0.807 |
| Full | Product-A net / Sharpe | $226,502 / 1.364 | $212,894 / 1.307 | $219,522 / 1.328 |
| Full | Product-B net / Sharpe | $354,097 / 1.263 | $360,591 / 1.213 | $376,444 / 1.274 |

(Source: `out/grid01_performance.csv`, rows `grid ∈ {G7,G13,G25}`.)

**G13 is not an isolated performance spike among G7/G25 — it sits inside a smoothly-varying band,
not at a discontinuity.** Canonical Product-A Sharpe spans 1.00–1.08 and Product-B Sharpe spans
0.81–0.91 across the three integer grids; full-window Product-A Sharpe spans 1.31–1.36 and
Product-B spans 1.21–1.27. This holds **despite** bar-level state agreement with G13 being only
moderate — T-target exact-match against G13 ranges 47.0%–74.1% and entry-set Jaccard 44.6%–59.6%
across G7/G25 (`out/grid01_state_agreement_vs_G13.csv`, `T_target_exact_agree_pct` /
`productB_entry_jaccard`, canonical window). **Divergence is in *when* trades happen (bar-level
paths), not in whether the ensemble as a whole delivers comparable risk-adjusted money** — a
methodological distinction worth carrying into any future diagnostic that reasons from bar-level
agreement alone.

**G49 (24-member, half-integer-offset grid) is the one outlier.** It underperforms all three
integer grids on both products in both windows:

| Window | Product | G13 (incumbent) | G49 |
|---|---|---|---|
| Canonical | A Sharpe | 1.030 | 0.956 |
| Canonical | B Sharpe | 0.879 | 0.710 |
| Full | A net | $212,894 | $221,175 |
| Full | B net | $360,591 | $323,978 |

(Source: `out/grid01_performance.csv`, `grid=G49`.) G49's state agreement with G13 is comparable to
or better than G7's (T-target exact-match 59.2% canonical, entry Jaccard 46.3% — see
`out/grid01_state_agreement_vs_G13.csv`), yet its performance is worse than G7's. **This reads as
evidence the edge is sensitive to the *exact threshold values* chosen for VolMult, not that finer
ensemble resolution per se degrades performance** — G49 does not add resolution along the
incumbent's own spacing pattern, it shifts every member to a different specific value.

## Governance note on G49

G49's candidate list (6.5..29.5, step 1.0, 24 members) was confirmed mechanically valid before use:
`member_states`'s `vol_mult` parameter is a genuine continuous `float` in both the Python replica
(`sm01_solarsim.py`, `resolve_s()`: `min(max(vol_mult*s, lo), hi)`, no indexing/lookup/int-cast) and
the underlying NinjaScript (`VolMult`/`VolMults` are `double`/`double[]` throughout; the one
`(int)mVolMult[m]` cast found repo-wide feeds only a cosmetic debug-label string, never a trading
decision). G49 was deliberately chosen non-coincident with the 13 incumbent members or any endpoint
perturbation set, to stress-test resolution independent of value choice — full reasoning recorded
in this workflow's spec-verify notes and reused verbatim in the governance-constraint header of this
task.

## Convergence assessment, in full

Behavior converges smoothly along the incumbent's own spacing pattern (G7→G13→G25), not a spike:
canonical Product-A net $47.0k–$51.7k / Sharpe 0.96–1.08; Product-B net $67.5k–$83.4k / Sharpe
0.71–0.91; full-window Product-A net $213k–$226k / Sharpe 1.31–1.36; Product-B net $324k–$376k /
Sharpe 1.08–1.27 (full range across all four grids including G49; the three integer grids alone are
tighter still). Bar-level agreement with G13 (T-target exact match 47%–74%, entry Jaccard 45%–61%)
shows the underlying trade paths diverge materially bar-to-bar even as aggregate outcomes stay
similar. G13 is not an outlier/local-optimum spike relative to G7/G25. The one true outlier is G49,
the worst performer on both products in both windows — consistent with sensitivity to the exact
VolMult values rather than to ensemble density per se.

---

## Explicitly out of scope

- **No winner is selected. No candidate is promoted or frozen.** This is a diagnostic report on
  resolution-convergence behavior of an existing, unmodified ensemble mechanism, per campaign
  directive sec.97–99.
- G49's underperformance is reported as a diagnostic observation about value-sensitivity, not as a
  case for re-optimizing VolMult values — that would be a new, separately-preregistered campaign.
- GRID02 (endpoint perturbation) is a separate sibling report; its results are not restated here
  beyond the cross-reference that G13/[6,30] is the shared incumbent-center row in both grids.

## Governance restatement (per campaign directive sec.98–99)

**Nothing in this report changes the incumbent Solar13 ensemble, its 13 members, or its VolMult
values.** `build_pend`, `member_states`, and `member_trades` remain unmodified; the incumbent
`INCUMBENT_VMS` list in `runs/W18R1_M1_VOLSEASON/src/common.py` is untouched. This diagnostic answers
a structural question — "does the system's behavior converge as ensemble resolution changes, or is
the incumbent a fragile spike?" — and the answer is **converges smoothly along the incumbent's own
spacing pattern**, with one disclosed, value-sensitivity-driven exception (G49). That answer is not,
and must not be read as, a recommendation to change the ensemble, add members, or re-optimize
VolMult values. Any such change would require a separate, freshly-preregistered campaign.

## Artifacts

- Core sweep logic: `src/grid_core.py`
- Runner + self-check gate: `src/run_grid01.py`
- Performance by grid × window × product: `out/grid01_performance.csv`
- Bar-level / state-level agreement vs. G13: `out/grid01_state_agreement_vs_G13.csv`
- Solar-only (pre-B-MOM/pre-tilt) context: `out/grid01_solar_e10_only_context.csv`
- Full machine-readable detail (grids, windows, self-check, constants held fixed): `out/grid01_full_detail.json`
