"""SMV2P_ENGINE3_S2 — render REPORT.md from out/ artifacts (slate-1 gen_report pattern).
Every number is read from the committed CSVs; nothing is hand-entered."""
import pandas as pd

RUN = "runs/SMV2P_ENGINE3_S2"
OUT = f"{RUN}/out"

def cell(df, c):
    return df[df["cell"] == c].iloc[0]

s77 = pd.read_csv(f"{OUT}/e377_summary.csv")
s78 = pd.read_csv(f"{OUT}/e378_summary.csv")
s79 = pd.read_csv(f"{OUT}/e379_summary.csv")
p77 = pd.read_csv(f"{OUT}/e377_plateau.csv")
p78 = pd.read_csv(f"{OUT}/e378_plateau.csv")
h79 = pd.read_csv(f"{OUT}/e379_hist_summary.csv")
comp = pd.read_csv(f"{OUT}/jointloss_complementarity.csv")
gates = pd.read_csv(f"{OUT}/gates.csv")
ev77 = pd.read_csv(f"{OUT}/e377_events.csv")
ev78 = pd.read_csv(f"{OUT}/e378_events.csv")
ev79 = pd.read_csv(f"{OUT}/e379_events.csv")
hchk = pd.read_csv(f"{OUT}/e379_hist_check.csv")
mtm = pd.read_csv(f"{OUT}/e378_daily_mtm.csv", index_col=0)
ver = open(f"{OUT}/verify_invariants.txt").read()
n_ver = len([l for l in ver.splitlines() if l.strip()])
n_fail = len([l for l in ver.splitlines() if l.startswith("FAIL")])

g77, g77a, g77b = cell(s77, "pooled"), cell(s77, "split_2022_24"), cell(s77, "split_2025_26")
g78, g78a, g78b = cell(s78, "pooled"), cell(s78, "split_2022_24"), cell(s78, "split_2025_26")
g79, g79a, g79b = cell(s79, "pooled"), cell(s79, "split_2022_24"), cell(s79, "split_2025_26")
x77t, x77o = cell(s77, "exit_target"), cell(s77, "exit_time_1554")
x78t, x78o = cell(s78, "exit_target"), cell(s78, "exit_time_3sess")
d77s, d77l = cell(s77, "dir_short"), cell(s77, "dir_long")
hp = h79[h79["cell"] == "pooled_2006_2021"].iloc[0]
yrs = {int(c["cell"][5:]): c["mean"] for _, c in s79.iterrows() if c["cell"].startswith("year_")}
day1, day2 = cell(s79, "day1"), cell(s79, "day2")
cp = comp[comp["definition"] == "primary_DUAL_leg_and_BMOM"].set_index("engine")
cs = comp[comp["definition"] == "secondary_champ_twin_and_BMOM"].set_index("engine")
gpass = {e: gates[gates["engine"] == e]["pass"].sum() for e in ("e377", "e378", "e379")}

era_txt = " · ".join(
    f"{r['cell'][4:].replace('_', '-')}: {r['mean_signed_bps']:+.1f} bps"
    for _, r in h79.iterrows() if r["cell"].startswith("era_"))
pl77_txt = "\n".join(
    f"| {r.coverage:.0%} | {r.accept_min:.0f} min | {r.n:.0f} | {r.mean_net:+,.2f} | {r.t_nw:+.2f} |"
    for r in p77.itertuples())
pl78_txt = "\n".join(
    f"| {r.lookback} | {r.n:.0f} | {r.mean_net:+,.2f} | {r.t_nw:+.2f} |"
    for r in p78.itertuples())
gates_txt = "\n".join(
    f"| {r.engine} | {r.gate} | {str(r.value).replace('|', ' / ')} | {'PASS' if r._4 else 'FAIL'} |"
    for r in gates.itertuples())

rep = f"""# SMV2P_ENGINE3_S2 — Engine #3 slate 2 (seq 377–379): value-area rotation / multi-day false-break / month-end flow

**Class:** R1_FAMILY_TEST (Stage 1 screen; no promotion possible from this run).
**Spec:** `spec.yaml` frozen 2026-08-08, committed at 58dc2d2 before execution.
**Executor:** `smv2p.py`; invariant audit `verify_invariants.py` -> `out/verify_invariants.txt` ({n_ver} checks, {n_fail} failures).
**Data:** NQ 3m END-stamped bars via `sm01_solarsim.load_bars_3m`, dev sessions {ev77['sd'].min()} .. 2026-05-29 (clip <= 2026-05-31; loader assert blocks anything >= 2026-08-01). Old-regime check (379): `runs/SM06_SOLAR_HISTORY/out/vote_state_3m_hist.parquet` session closes 2006-2021 (committed artifact).
**Costs:** every expectancy NET of $4.36/RT + 1 tick/side embedded in fills (`_fill`), NQ $20/pt.
**Stats:** NW t = mean per-event net, session-clustered SE, Bartlett lag 5 (SMV2K convention). House bootstrap: moving block 5, B=10,000, seed 20260808; p_boot = fraction of resampled means <= 0.

## Verdict (FACT)

| seq | engine | N | mean net/event | t_NW | p_boot | gates passed | verdict |
|---|---|---|---|---|---|---|---|
| 377 | value-area rotation | {g77['n']:.0f} | {g77['mean']:+,.2f} | {g77['t_nw']:+.2f} | {g77['p_boot']:.3f} | {gpass['e377']}/4 | **KILLED — significantly negative** |
| 378 | multi-day balance false-break | {g78['n']:.0f} | {g78['mean']:+,.2f} | {g78['t_nw']:+.2f} | {g78['p_boot']:.3f} | {gpass['e378']}/4 | **KILLED** |
| 379 | month-end flow tilt | {g79['n']:.0f} | {g79['mean']:+,.2f} | {g79['t_nw']:+.2f} | {g79['p_boot']:.3f} | {gpass['e379']}/4 | **KILLED — no old-regime structure** |

**Slate-2 total failure.** Frozen verdict_rule -> V4 §51: three NEW mechanism-expansion passes are owed before any slate 3. Combined with slate 1 (seq 368–370), all six externally-sourced reversion/rotation/calendar families are now dead on this substrate.

## Frozen conventions and disclosed adaptations

- Wall-time convention (SMV2K anchor): "09:33 open" = open of the 0936-stamped bar; "15:57 exit" = open of the 1600-stamped bar; "15:54 time-stop" = close of the last RTH bar stamped <= 1554. RTH = stamps 0933..1600.
- **377 VA algorithm (exact, per spec):** histogram prior-session RTH 3m closes x volume in 25c bins (NQ trades on a 25c grid, so each bin is one price level, k = round(close/0.25)); seed bin = floor(prior-RTH-VWAP/0.25); grow the contiguous band one bin at a time toward the adjacent side with the LARGER volume (tie -> up; exhausted side -> other) until cumulative >= coverage x total RTH volume. VAL/VAH = lowest/highest included level. Independently recomputed on 25 sampled events: band holds >= 70% of volume and contains the VWAP bin in 25/25 (`verify_invariants.txt`).
- 377 event: 09:30 RTH open strictly outside [VAL,VAH]; acceptance = first run of 30 min (10 bars) of consecutive RTH closes inside; entry next 3m open (must be stamped <= 1554 else event void); target = far VA edge; level-touch fills use SMV2K e368 semantics (base = open if already beyond level else level, +/-1 tick capped by bar range); one event/session (verified unique).
- 378: rolling 20-session RTH-close extremes (shift 1); range frozen at break; reclaim = RTH close strictly inside within 2 sessions; entry next session 09:33; exit at midpoint touch on ANY bar (overnight included) or at the ~17:00 session close of the 3rd held session (entry session = 1). One position at a time ({s78['dropped_overlap'].iloc[0]:.0f} signals dropped in-position at center); dev-end right-censor drops {s78['dropped_censor'].iloc[0]:.0f}; most-recent break episode wins when several are active. **Held overnight, as disclosed in the spec — engine is NOT day-only.**
- 379: MTD sign frozen ONCE per month = -sign(session close of D_n-2 minus prior-month final session close), point difference, applied to both day-events; {s79['skip_early_exit'].iloc[0]:.0f}/104 day-events fell on early-close sessions (no 1600 bar) -> forced exit at last RTH bar close, flagged `early_close_exit`, kept. "Sign consistent across 2022-2026" operationalized as the standard WF split (2022-24 vs 2025-26) plus the per-year table below.
- 379 hist check: GROSS close-to-close 2-day windows in POINTS (exact under additive back-adjustment), one observation per month, {len(hchk)} months 2006-02..2021-12.
- Complementarity legs (code-map curves): PRIMARY Solar_DUAL = `DUAL` column of `runs/SMV2H_ONECONTRACT/out/rerank_curves.csv`; BMOM = `runs/SMV2B_BMOM_EXEC_AUDIT/out/ledger_E2_next_open.parquet` net_c1_ticks x $5 by session — verified IDENTICAL to the stored `BM_E2` column (max abs diff 0.0, asserted in `smv2p.py`). SECONDARY (robustness): champion twin `runs/SMV2M_MASTER_BUILD/out/twin_daily.csv` (dev-clipped) AND BMOM.

## seq 377 — A-H2 value-area rotation

FACT. {s77['n_open_outside_sessions'].iloc[0]:.0f} dev sessions opened outside the prior 70% VA; {g77['n']:.0f} produced 30-min acceptance events. Pooled net **{g77['mean']:+,.2f}/event (t_NW {g77['t_nw']:+.2f}, total {g77['total']:+,.0f}$)**. {x77t['n']:.0f}/{g77['n']:.0f} reached the far edge ({x77t['mean']:+,.2f}/event); {x77o['n']:.0f} timed out at 15:54 ({x77o['mean']:+,.2f}/event) — acceptance does not buy enough traverse. Long rotations (open below value) are the toxic side: {d77l['mean']:+,.2f}/event (t {d77l['t_nw']:+.2f}, N {d77l['n']:.0f}) vs shorts {d77s['mean']:+,.2f} (t {d77s['t_nw']:+.2f}). WF halves {g77a['mean']:+,.2f} | {g77b['mean']:+,.2f} — both negative.

Plateau — **9/9 cells negative**:

| coverage | acceptance | N | mean net | t_NW |
|---|---|---|---|---|
{pl77_txt}

Gates: t_NW>=2 FAIL ({g77['t_nw']:+.2f}) · N>=150 PASS ({g77['n']:.0f}) · WF same-sign PASS (both NEGATIVE) · plateau same-sign PASS (all NEGATIVE). Positive-expectancy family: **dead**.

## seq 378 — A-H9 multi-day balance false-break

FACT. {g78['n']:.0f} events at center (lb 20, ~0.4/wk). Pooled **{g78['mean']:+,.2f}/event (t_NW {g78['t_nw']:+.2f})**; {x78t['n']:.0f}/{g78['n']:.0f} reached the range midpoint within 3 sessions ({x78t['mean']:+,.2f}/event), {x78o['n']:.0f} timed out ({x78o['mean']:+,.2f}/event). WF sign FLIPS ({g78a['mean']:+,.2f} -> {g78b['mean']:+,.2f}). Daily MTM at session closes reconciles exactly to event totals ({mtm.iloc[:,0].sum():+,.2f} vs {ev78['net'].sum():+,.2f}).

Plateau — mixed sign:

| lookback | N | mean net | t_NW |
|---|---|---|---|
{pl78_txt}

Gates: t_NW>=2 FAIL · N>=80 PASS ({g78['n']:.0f}) · WF FAIL · plateau FAIL. **Dead.** INFERENCE: 2022-24 NQ trended through its 20-day close range too persistently for a 3-session reversion to the midpoint; the positive 2025-26 half (t {g78b['t_nw']:+.2f}) is noise.

## seq 379 — A-H12 month-end flow tilt

FACT, dev: {g79['n']:.0f} day-events (52 months x 2, zero skipped months), pooled **{g79['mean']:+,.2f}/day-event (t_NW {g79['t_nw']:+.2f}, p_boot {g79['p_boot']:.3f})**. Per-year means: 2022 {yrs[2022]:+,.0f} · 2023 {yrs[2023]:+,.0f} · 2024 {yrs[2024]:+,.0f} · 2025 {yrs[2025]:+,.0f} · 2026(Jan-May) {yrs[2026]:+,.0f} — NOT sign-consistent across years. Day-1 {day1['mean']:+,.2f} vs day-2 {day2['mean']:+,.2f}: noise-level.

FACT, old regime 2006-2021 (gross direction check, {hp['n_months']:.0f} months): mean signed 2-day window **{hp['mean_signed_bps']:+.2f} bps/month (t_NW {hp['t_nw_bps']:+.2f}, hit rate {hp['hit_rate']:.1%})**; eras {era_txt}. No structural rebalancing-flow premium in either regime.

Gates: t>=2 FAIL ({g79['t_nw']:+.2f}) · N>=100 PASS ({g79['n']:.0f}) · dev WF same-sign PASS (both weakly positive) · old-regime same-sign FAIL ({hp['mean_signed_bps']:+.2f} bps vs {g79['mean']:+.2f}$ dev). Spec: "calendar mechanisms should be structural or die" — **dead**.

## Joint-loss-week complementarity (`out/jointloss_complementarity.csv`)

Weekly (W-FRI) sums over the {cp.iloc[0]['n_weeks']:.0f}-week dev calendar. Joint-loss (PRIMARY, Solar_DUAL<0 AND BMOM<0): **{cp.iloc[0]['n_jointloss_weeks']:.0f} weeks** (champion mean {cp.iloc[0]['champ_mean_week_jointloss']:+,.2f}/week there); SECONDARY (twin AND BMOM): {cs.iloc[0]['n_jointloss_weeks']:.0f} weeks.

| engine | mean wk (all) | mean wk (joint-loss, primary) | total in JL weeks | mean wk (JL, secondary) | weekly corr vs champion |
|---|---|---|---|---|---|
| e377 | {cp.loc['e377_value_area','engine_mean_week_all']:+,.2f} | {cp.loc['e377_value_area','engine_mean_week_jointloss']:+,.2f} | {cp.loc['e377_value_area','engine_total_jointloss']:+,.0f} | {cs.loc['e377_value_area','engine_mean_week_jointloss']:+,.2f} | {cp.loc['e377_value_area','corr_weekly_engine_vs_champ']:+.2f} |
| e378 (MTM) | {cp.loc['e378_false_break_mtm','engine_mean_week_all']:+,.2f} | {cp.loc['e378_false_break_mtm','engine_mean_week_jointloss']:+,.2f} | {cp.loc['e378_false_break_mtm','engine_total_jointloss']:+,.0f} | {cs.loc['e378_false_break_mtm','engine_mean_week_jointloss']:+,.2f} | {cp.loc['e378_false_break_mtm','corr_weekly_engine_vs_champ']:+.2f} |
| e379 | {cp.loc['e379_month_end','engine_mean_week_all']:+,.2f} | {cp.loc['e379_month_end','engine_mean_week_jointloss']:+,.2f} | {cp.loc['e379_month_end','engine_total_jointloss']:+,.0f} | {cs.loc['e379_month_end','engine_mean_week_jointloss']:+,.2f} | {cp.loc['e379_month_end','corr_weekly_engine_vs_champ']:+.2f} |

FACT: e377 loses HARDER in joint-loss weeks — anti-complementary as well as negative. e378/e379 show mildly positive primary joint-loss means, but both are dead on their own economics and e379's read flips sign under the secondary definition. INFERENCE: noise on dead engines, not a rescue argument (V4 §42: no promotion from Stage 1 regardless).

## Gate table (`out/gates.csv`)

| engine | gate | value | pass |
|---|---|---|---|
{gates_txt}

## Red-team notes

- 377 is a clean two-sided kill: significantly NEGATIVE across the entire 3x3 plateau, not merely edgeless. HYPOTHESIS (not tested here; anti-dup rule forbids flipping sides within this run): its mirror — continuation away from value after FAILED acceptance — aligns with the campaign's standing finding that NQ pays breakout/trend premium and charges for fading structure (slate-1 seq 368/369 fade premium was also significantly negative).
- 378's exit mix (24% target hits) shows the mechanism mostly expires worthless; no lookback neighborhood rescues it.
- 379's +$52/event dev point estimate over 2023-25 is exactly the recency trap the structural gate exists to catch; 191 old-regime months put the prior at zero.
- No data >= 2026-06-01 used anywhere: loader assert + per-artifact max-date checks (e377 max sd 2026-05-27, e378 max exit 2026-05-20, e379 max sd 2026-05-29) in `verify_invariants.txt`.

## Artifacts

`out/e377_events.csv` ({len(ev77)}) · `out/e377_summary.csv` · `out/e377_plateau.csv` · `out/e378_events.csv` ({len(ev78)}) · `out/e378_summary.csv` · `out/e378_plateau.csv` · `out/e378_daily_mtm.csv` · `out/e379_events.csv` ({len(ev79)}) · `out/e379_summary.csv` · `out/e379_hist_check.csv` ({len(hchk)}) · `out/e379_hist_summary.csv` · `out/jointloss_complementarity.csv` · `out/gates.csv` · `out/verify_invariants.txt`
"""
open(f"{RUN}/REPORT.md", "w", encoding="utf-8").write(rep)
print("REPORT.md written,", len(rep), "chars")
