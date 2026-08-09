## VERDICT: CONFIRMED-WITH-CORRECTIONS

All 12 claimed files exist and contain what is claimed. I re-derived the central headline by three independent paths and got exact agreement. The defects below are real but none overturns the primary null (§3) or the FOMC-only P&L finding (§2b); one of them (#1) flips the §3 answer for one object under an assumption the report never states.

---

## DEFECTS

**1. §3's entire "no crossover exists" answer rests on an unstated assumption; under the alternative reading it fails for Product A.**
`src/v1f_eventdays.py:490-493` (`MARGIN` dict has no `initial_4x`) and `:539-569` (`leverage_table` never forms the product). The report treats 4X as multiplying *day* margin only. Under 4X × **initial** margin, Product A binds in **15 of 60** capital-map rows, min ratio **0.503×** (thr 0.20/0.25/0.30 at stress 1.0/1.25/1.5). B-NQ 1.57× and B-MNQ 2.29× still clear. This is not academic: `V1F_EVENTDAY.md:297-305` constructs a "worst-case stack" that is precisely the case where both windows are simultaneously live (early close + event day: 2023-04-07, 2025-07-03, 2026-04-03) and asserts "still does not bind (initial-margin ratio ≥ 2.01×)" — that 2.01× is **1X** initial. "There is no crossover to report because none exists" (`:260`) is conditional on an assumption that is never named.

**2. The 2026 "tiering artifact" explanation is not supported by the data.**
`V1F_EVENTDAY.md:211-215`. The three `UNVERIFIED` 2026 FOMC dates (2026-01-28, 03-18, 04-29) match the actually-published 2026 FOMC calendar. Adding them leaves the 2026 event bucket **positive for all three objects** (A +$13,830→+$14,666; B-NQ +$18,638→+$17,742; B-MNQ +$1,727→+$1,632), and 2026 FOMC mean/session is **+$279 / −$299 / −$32** against 2022-25's −$738 / −$991 / −$162. So the reversal is *not* caused by "2026's CORE set contains zero FOMC sessions." The defensible statement is "3 sessions is far too thin to conclude anything" (2026-03-18 +$7,051 and 2026-04-29 −$7,532 for B-NQ nearly cancel) — not "an artifact of the provenance tiering, not new evidence."

**3. The 2023-04-05/06 merge is a cruder repair than one that was available, and it corrupts the DILATED number.**
`src/v1f_eventdays.py:358-370`. The committed fills ledger re-buckets the pair **exactly**: 04-05 = +$509.70, 04-06 = +$1,856.50. My reconstruction matches `nt` to the cent on all 1,137 other dev sessions. The merge books $2,366.20 to 04-05 and **$0** to 04-06. Because 2023-04-06 ∈ DILATED but 2023-04-05 ∉ DILATED (adjacency to the 2023-04-07 NFP session), the merge moves $1,856.50 *out* of the dilated set: reported **+$14,993.20**, exact **+$16,849.70**. Sign and conclusion unchanged.

**4. Contaminated rows shipped in a committed artifact with no in-file warning.**
`out/v1f_event_attribution.csv`, object `PRODUCT_A_rawNTbucketing`, calendar `DILATED_core_pm1`: net_event **−$111,980.90**, share **−63.15%**, placebo p **0.0393** — a pure bucketing artifact that reads as a significant finding. The report warns only about *capital-map* contamination (`V1F_EVENTDAY.md:355-359`), never about the attribution rows, and the CSV carries no flag column.

**5. Negative-denominator ratio, unflagged.**
`src/v1f_eventdays.py:447`: `share_ok = abs(tot) > 0.05*sum|g|` tests magnitude, not **sign**. B-MNQ 2026: net_total −$3,417.70, net_event **+$1,726.50**, `pnl_share_event = −50.5%`, `pnl_share_meaningful=True`. `V1F_EVENTDAY.md:202` prints "−50.5%" in a column whose every other cell means "event days destroyed X% of profit"; here event days *made* money in a losing year. B-NQ 2026 (−399.96%) is flagged; this one is not.

**6. Release-exposure table has no baseline; the statistic carries no event-specific information.**
`src/v1f_eventdays.py:744-759`; `V1F_EVENTDAY.md:239-247`. Measured baseline on **non-event** sessions at the same clock: 14:00 → **97.7%** non-flat, mean|pos| **4.06** (vs 100% / 3.31 on FOMC); 08:30 → **81.8%** non-flat (vs 79.2% on NFP). The book is essentially always live, and event-day exposure is at or slightly *below* baseline. The narrow claim ("not flat, so margin is not moot") survives; the implied finding does not.

**7. Transcription error.** `V1F_EVENTDAY.md:272` reports Product A @ $5,000,000 as "4 / 17 / **51**"; `out/v1f_capital_grid.csv` says **52**.

**8. "Dev window only" claim is false for one input (immaterial).** `src/v1f_eventdays.py:732`: `a_peak = int(bars["phys"].abs().max())` runs on the full `smm_v2_bars.csv`, which extends to **2026-07-31** — 20,518 bars lie past the dev-window end. `a_peak=11` drives every Product A margin and notional figure in §3. Contradicts the docstring (`:25-27`) and `V1F_EVENTDAY.md:4-6`. Verified **immaterial**: peak is 11 in every individual year and 11 restricted to mapped dev sessions. The separate claim "no data ≥ 2026-08-01 was read" is **true**.

**9. The stated reconciliation cannot validate what it is offered to validate.** `V1F_EVENTDAY.md:106-109` offers the three matching net totals as validation of the *session-bucketed* series. A net sum is invariant to bucketing; it establishes only that no rows were dropped. (The bucketing is in fact correct — I tested it separately, below — but the report's evidence does not show that.)

**10. Shutdown handling is one-sided.** `src/v1f_eventdays.py:250-265` downgrades 12 shutdown-window dates to `UNVERIFIED` and drops them from CORE, but their *actual* rescheduled dates (e.g. the Sept-2025 Employment Situation, released 2025-11-20) sit inside the dev window and remain in the **control** group. Sensitivity is tested only for removing uncertain dates, never for genuine event days misclassified as non-event.

**11. PCE accuracy disclosed asymmetrically.** `V1F_EVENTDAY.md:67-69` gives PCE "9/12 exact" but omits the within-3-days figure, which `out/v1f_summary.json` records as **also 9/12** — all three PCE misses are >3 calendar days off. CPI gets both figures (11/12, 12/12). PCE carries the report's most prominent positive (+$49,539 B-NQ).

**12. No pre-registration exists for V1f.** `spec.yaml` is exclusively the C4 compliance fix; its only `PRE-REGISTERED` item (`spec.yaml:120-126`) is the zero-breach compliance bar. Nothing in `spec.yaml`, `O1_OBJECTIVE.md` or `REPORT.md` pre-registers the V1f calendar, the CORE tier rule, the 4 worst-day cuts, or the 8 calendars. The report never claims otherwise and discloses multiplicity — but its count ("8 calendars × 3 real objects") omits the **4 worst-day definitions**; the only "significant" tail result for A and B-NQ is bottom-5% at p=0.043, i.e. 1 of 4 cuts. (Stated in prose at `:133-138`, so a completeness gap, not concealment.)

*Incidental:* the agent's "no commit made" is accurate for itself, but the v1f artifacts **are** already in git (commits `9d84ddf`, `8b71aa9`); working tree is clean.

---

## WHAT I TRIED TO BREAK AND COULD NOT

1. **The calendar.** Regenerated FOMC 2022-25 (32 dates) and all NFP releases 2022-01..2026-05 from my own independent knowledge. **Zero set difference** against their CORE, both directions (81 dates / 81 sessions). Their CPI-2022 and PCE-2023 checkpoint "truth" values are all correct; the 2025-01-03→2025-01-10 NFP override is correct; the 2026 FOMC extrapolation is correct.
2. **The session calendar.** Rebuilt from a *different file by a different mechanism* (`mnq_3m_raw.csv` + `fbos` cumsum, not the NQ file via `load_bars_3m`): **1,139 dev sessions, 2022-01-03 .. 2026-05-29** — exact match. The 18:00 ET roll is handled correctly (118 bars before 2022-01-03 correctly belong to session 2022-01-03).
3. **Product A headline, fully independent path.** Rebuilt daily P&L from the **fills ledger** (signed cash flow × PV=2 minus per-fill commission; final position exactly 0): total **$212,312.20** = `parity_daily_aligned.nt` total to the cent; dev subset **$177,315.10** = committed headline; agrees with `nt` per-session on 1,137/1,139 sessions. **CORE event net −$22,519.90, share −12.70%** by all three routes — exactly as reported. No commission double-count.
4. **Product B headlines + the NT8 bar-end timestamp trap.** Re-bucketed both trade lists through my independent session map: B-NQ **−$36,766.96 / −12.12%**, B-MNQ **−$8,407.90 / −29.09%** — exact. Re-ran bucketing on **entry_time** instead of exit_time: identical to the cent, proving no trade spans a session boundary and that NT8's fill-bar-end stamping shifts nothing across the 18:00 roll.
5. **All of §3's leverage arithmetic.** Break-even multipliers 273.19× / 398.12× / 87.36×; break-even thr 20.49 / 29.86 / 6.55; notional leverage 1.473× / 1.011× / 4.606× vs 100.6× permitted; DD/4X 68.30–545.88 / 99.53–777.62 / 21.84–240.66; margin utilisation 0.32%–1.50%. All reproduce. `capital_map()` is genuinely equivalent in body, grids and seed (20260808) to `runs/PRODUCTB_ONECONTRACT_FINAL/build_parity_and_metrics.py:188-230`.
6. **The statistics.** `hypergeom.sf(hits-1, n, k, m)` argument order is correct; m=12 / m=57 and expectations 0.711 / 1.778 / 0.853 / 4.054 all correct. **Every cell of the §2a table matches `v1f_event_attribution.csv` exactly.**
7. **The key negative.** Confirmed directly: **0 of Product A's worst-10 sessions are FOMC** (2 are NFP: 2025-03-07, 2022-05-06).
8. **Bootstrap seeding.** All three RNG sites explicitly seeded (`SEED=20260809` re-seeded per `attribute()` call at `:376-383`; `capital_map` seed 20260808 at `:497`). No unseeded `np.random`; sets feed only order-independent `.isin()`. Verified by inspection — I did **not** execute their script, since it would overwrite committed outputs.
9. **Early-close census.** 44 sessions with last bar <17:00 `{0915:2, 0930:1, 1300:31, 1315:9, 1403:1}`, 43 genuine, CORE overlap = 2023-04-07 / 2025-07-03 / 2026-04-03. Matches `spec.yaml` V1e. (Mild circularity: `:777` hardcodes the four hm values the spec already stated — but the 31/9/2/1 counts do fall out of the data.)
10. **§5.2's gap claim.** Next-largest |nt−tw| after the pair is exactly **$1,561.50**, and exactly **4** sessions exceed $1,000. Correct.
11. **Look-ahead / regime leakage.** None. Release dates are announced in advance and nothing is fitted. No 2006-2021 data touched (earliest bar 2022-01-02 18:03). No data ≥2026-08-01 read — every source ends 2026-07-31.
12. **Null prominence.** Genuinely well done: the NFP null, the PCE-positive, the dilation sign-flip, the 0-of-worst-10, and the §3 null are all bolded in the report and carried into the §4 disposition. The B6 "not promoted" conclusion is correctly argued on both channels.

---

## PATHS

Reviewed (not modified): `D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\runs\W17_C4_COMPLIANCE\V1F_EVENTDAY.md`, `...\spec.yaml`, `...\src\v1f_eventdays.py`, `...\src\v1f_event_calendar.csv`, and all 9 `...\out\v1f_*.{csv,json}`.

Review scripts I wrote (scratchpad only): `C:\Users\YUKEZH~1\AppData\Local\Temp\claude\D--OneDrive---Washington-University-in-St--Louis-TradingResearch-systematic-research\bfb80633-2ca8-4554-803e-2bd6cbeeb4c1\scratchpad\rt_v1f.py`, `...\rt_v1f2.py`, `...\rt_v1f3.py`.

No file of theirs was edited; no commit made; no NT8/CrossTrade tool used.