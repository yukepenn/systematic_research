VERDICT: **CONFIRMED-WITH-CORRECTIONS**

Both files exist at the claimed paths with the claimed line counts (578 / 371). The script re-runs clean (exit 0) and reproduces **every** number in the MD — I found no transcription error anywhere. The measurement layer is sound and I re-derived the headline by two independent paths that reconcile to $0.00 / 7 s.f. The defects are in the **inferential layer**, one real second-order code bug, and undisclosed data-quality/governance issues.

---

## DEFECTS

**D1 — MATERIAL. The report's central conclusion ("the gross edge collapsed") is statistically unsupported and is unmarked INFERENCE.**
`V4_FRICTION.md:329-331` — *"BEST_ONE_NQ's gross fell from 54.7 ticks/RT in 2022 to 2.76 ticks/RT in 2026"*, and the orchestrator summary states *"the gross edge per trade, which is what actually collapsed"*.
Independent per-trade test (gross ticks/RT, mean ± 1.96·SE):
| year | NQ | n | t |
|---|---|---|---|
|2022|52.80 ± 55.59|443|1.86|
|2023|12.65 ± 31.99|454|0.77|
|2024|33.73 ± 46.46|440|1.42|
|2025|40.37 ± 69.90|453|1.13|
|2026|0.82 ± 100.50|185|0.02|

**Welch 2022-vs-2026: diff 51.98 ticks, t = 0.89.** Not one yearly mean is individually distinguishable from zero. The "collapse" is entirely inside trade-level noise. The report carries **zero** uncertainty quantification — no CI, no t-stat, no bootstrap, no PBO/DSR — despite `src/analytics/trials.py` existing for exactly this. §3 carefully labels DIRECT vs INFERENCE (`:190`); §5 does not, and §5 is where the causal claim lives.

**D2 — MATERIAL. The headline negative is 0.001 SE from zero, and every ratio derived from it has a noise denominator.**
`V4_FRICTION.md:112,129,135-141,244-247`. BEST_ONE_NQ 2026: 185 trades, per-trade sd $3,487, **SE(sum) = $47,428**; net −$46.60 is **0.0010 SE from zero**.
- Drop the single best trade → **−$13,307.24**. Drop the single worst → **+$6,622.76**. The sign of the report's most-emphasised result is decided by one trade in 185.
- `FS_comm = 1.0613` has denominator G = $760 (0.24% of window G). One additional average-sized 2026 winner (+$3,139) moves it to **0.2069** and breakeven from 0.94x to ~3.9x.
- `V4_FRICTION.md:25-27` guards only for `G <= 0`. That is the wrong condition — the hazard is near-zero G, and the report's own flagship ratio is precisely the case the guard was written to catch. Quoting 1.0613 / 0.94x / Sharpe −0.0014 is spurious precision.

**D3 — MATERIAL, selective reporting. 45 sessions of the most recent Product A data were read, excluded, and never reported — and they run opposite to the narrative.**
`V4_FRICTION.md:6-7,175`; `v4_friction.py:231,254`. The 1,056 post-dev fills span **2026-06-01..2026-07-31, 45 sessions, net +$34,997.10** (53.3% positive days; $777.71/session vs the dev average of $155.67/session). Excluding them from a dev-window ledger is correct discipline; stating "excluded from every figure here" **without the magnitude** is not, when §2/§5 argue "2026 is where the edge reached the friction floor." Self-applied caveat: n=45 is far too short for any magnitude claim (Sharpe SE ≈ 2.4), and per `research/operational/LOCKED_FORWARD.md` this window is "research-consumed / in-sample era", so it is not clean OOS either. **The defect is the silence, not the sign.**
Related open item the report never addresses: `LOCKED_FORWARD.md` gives the frozen champion as TRUE_MTM $179,361.36 on 2022-01..2026-07; the report reconciles only to `nt8_dev_battery` (dev window) and never to that canonical figure.

**D4 — REAL BUG (second-order). The "flat-to-flat cycles" are not flat-to-flat.**
`v4_friction.py:238-247`:
```python
for i, d in enumerate(f["delta"].to_numpy()):
    if pos == 0:
        cur += 1
```
A fill that flips the position **through** zero (e.g. +2 → −1) never sets `pos == 0`, so the closing round trip and the newly opened one are merged into one "cycle". **89 in-dev fills cross zero**; a reversal-aware reconstruction yields **4,805 cycles, not 4,711 (+94)**.
Corrected per-cycle stats vs the report (`V4_FRICTION.md:48,57-63,322-323`):

| | report | corrected |
|---|---|---|
| cycles | 4,711 | 4,805 |
| win rate | 0.2534 | 0.2541 |
| payoff | 3.4916 | 3.4748 |
| PF | 1.1854 | 1.1838 |
| avg net/RT | $37.64 | $36.90 |
| avg win / avg loss | $949.61 / −$271.97 | $935.34 / −$269.18 |
| avg comm/RT | $5.09 | $4.99 |

**Unaffected:** net, G, G_raw, comm, slip, every FS ratio, every Sharpe, every breakeven multiple, and the entire per-CONTRACT tick ledger (18,443 contract-RT = qty/2, correct). Both constructions sum to $177,315.10 exactly. But the contaminated numbers are exactly the ones §5 uses to rebut the task's premise.

**D5 — MATERIAL for a report whose authority rests on session accounting: undisclosed bar gaps, and a 44th "early close" that conflicts with the wave's established 43.**
`V4_FRICTION.md:33-34` presents *"The NQ and MNQ grids independently yield 1,139 dev sessions"* as validation. Actual:
- `runs/AUDIT03_BARS/nq_3m_2022_2026.csv`: **13 dev sessions with internal gaps, 487 missing 3-min bars** (2025-11-28 −215 bars ≈10.75h; 2022-11-07 −211 bars ≈10.6h).
- `runs/PRODUCTB_ONECONTRACT_FINAL/out/mnq_3m_raw.csv`: **11 sessions, 446 missing bars** (same two worst).
- The grids **disagree on the shape of 2 dev sessions**: NQ's 2023-04-05 ends 14:03 (MNQ's ends 17:00); MNQ's 2026-05-29 ends 16:57 (truncation). The "independent agreement on 1,139" is count-level only.
- Non-17:00 dev sessions = **44 per grid, not 43** (31×13:00, 9×13:15, 2×09:15, 1×09:30 = 43). NQ's 44th is the 2023-04-05 data hole; MNQ's is file truncation. So the NQ exit the `is_last` rule classified as a session-close backstop at 14:03 is a data artefact, not a session close.
- Numerical impact on the ledger is ~nil (0 fills landed off-grid inside dev), but the report leans hard on early-close rigour (`:195-200`) and mentions none of this.

**D6 — MINOR. "Cross-checks (all pass exactly)" is inaccurate — one does not — and its stated cause was never demonstrated.**
`V4_FRICTION.md:76-81`. Daily vol $2,109.058 vs battery $2,109.452; Sharpe 1.171747 vs 1.1715277. Honestly disclosed in the same paragraph, but under a header asserting the opposite. The stated cause ("session attribution of a handful of boundary fills") is asserted with no supporting diff and no count. **My independent test:** a pure 18:00-ET-roll session map with no bar grid at all reproduces the agent's daily vol to **$2,109.058053** — 7 s.f. So the agent's two candidate conventions agree and the whole residual sits on the battery side, in `runs/SMV2M_MASTER_BUILD/parity.py:43-50` (`np.searchsorted` against the *twin* ledger's session last-bar times, whose grid is missing bars). That mechanism is consistent with the guess, so I could **not refute** it — but it was never shown, and not one disagreeing fill was located.

**D7 — MATERIAL over-claim. §4's turnover attribution is apples-to-oranges, inflated 10x for the NQ object.**
`V4_FRICTION.md:301-303`: *"driven almost entirely by turnover: BEST_ONE_NQ trades 3,950 contract-sides where the 1m unscaled arm trades 140,526."* NQ point value is 10x MNQ's — 3,950 NQ sides = **39,500 MNQ-equivalent sides**, so the real notional-normalised ratio is **3.56x, not 35.6x**. And the residual is not turnover: friction per notional-unit-side is **$0.718 for NQ vs $1.15 for MNQ (1.60x)**, because MNQ's commission is ~3x NQ's per notional. The friction *share* (0.0855) is scale-invariant and correct; the causal attribution and its supporting figures are not.

**D8 — GOVERNANCE, minor. No spec, no pre-registration, undeclared output path.**
`runs/W17_C4_COMPLIANCE/spec.yaml` was frozen at c8330dc (2026-08-08 23:13) for a different purpose (`type: compliance_fix_not_an_alpha_trial`, `hypothesis_free: true`). Its `outputs:` (`spec.yaml:153-157`) names only the two `.cs` files, `c4_audit.py`, and `REPORT.md`. Grep for `V4|v4|friction` in spec.yaml returns **nothing** — no V4/V4a pre-registration exists. Per CLAUDE.md's run-dir contract this deliverable has no spec. Mitigating: the declared `REPORT.md` does not exist and other agents (`O1_OBJECTIVE.md`, `v1d_*`, `v1f_*`) did the same this wave, so it is a wave-wide pattern, not unilateral. **The report never claims a pre-registration**, so this is not a false pre-registration claim. Reporting both FS definitions post-hoc is the honest handling and I do not count it against them.

**D9 — MINOR.** `v4_friction.py:307`: `win_rate_net` denominator includes zero-P&L cycles while payoff/PF exclude them (Product A 0.2534 vs 0.2536 implied by payoff×PF algebra). Immaterial.

**D10 — MINOR framing.** §3 titled "Slippage — DIRECT evidence" and `:17` "Not assumed — read off the bars." What is directly evidenced is that the **backtest's configured** 1-tick slippage is embedded in fill prices, not anything about real slippage. `:190-193` does caveat this ("a within-backtest statement"), and `G_raw` is a counterfactual, not an observable — yet it is the denominator of `FS_house` throughout.

**D11 — MINOR omission.** Headline Sharpes (1.1717 / 1.1171 / 0.9212) are whole-dev in-sample figures for objects selected on this same window, presented with no selection-bias caveat. §6's caveat list never mentions overfitting, PBO, or DSR.

---

## WHAT I TRIED TO BREAK AND COULD NOT

1. **Existence/content.** Both files present, 578 / 371 lines as claimed. Working-tree diff vs 9d84ddf is exactly the 6-line diagnostic they described — verified.
2. **Every number in the MD.** Re-ran the script and diffed all ledger, band, slippage, house-comparison and cross-check blocks against the prose. **No discrepancy.** The only hand-edits are substituting "n/a" for MNQ-2026 FS and breakeven, where the script emits NaN / −16.071 — correct substitutions.
3. **Product A net, independent path** (raw 18:00-ET roll, no bar grid, fill-level, no cycle construction): **$177,315.10, delta $0.0000**.
4. **Product A daily vol/Sharpe, independent path:** $2,109.058053 / 1.171747 — matches to 7 s.f.
5. **Product B, independent path:** NQ $303,449.00 / vol $3,785.9131 / Sharpe 1.117099; MNQ $28,900.70 / $437.2382 / 0.921227; 2026 slices −$46.60/−0.001391 and −$3,417.70/−0.909162. All match.
6. **Silent row drops.** `CAL_NQ == CAL_MNQ == CAL_SMM`, 1,139 each, **symmetric difference empty** — so `reindex(calendar, fill_value=0)` (`v4_friction.py:278`) drops nothing. `n_trades_outside_dev` = 0; whole-file net == dev net for both Product B objects.
7. **Sharpe convention.** Matches the house docstring verbatim (`src/analytics/sm_metrics.py:4-5,12,28`: all sessions, flat days = 0, ann 252, ddof 1). Zero-filling is the **conservative** direction (NQ 1.1484 unfilled → 1.1171 filled; 1,078/1,139 active days).
8. **Slippage base-price rule — adversarial stress test.** Agent's rule: **0** of 1,975 NQ exits, **0** of 1,561 MNQ exits, **0** of 25,825 Product A fills outside {0, +1} tick. "Always open": 17 NQ / 1,003 MNQ / 35 Product A violations. "Always close": 1,881 NQ / 479 MNQ. "`is_last`→close" for Product A: **exactly 2** violations — independently confirming their §3 method note ("mis-priced exactly two Product A fills") to the fill. The rule is the only one of four that works; it is not a fudge.
9. **Timestamp / bar-end convention.** No off-by-one: 0 fill timestamps off-grid inside dev for all three objects, and the +1-tick concentration is self-validating (a bar misalignment would randomise displacement, not concentrate it at exactly one tick).
10. **Double-counted commission.** Product A: $0.65/contract on 26,881/26,881 fills = $23,975.90 = 0.65 × 36,886 exactly. Product B: `(exit−entry)·dir·PV − pnl` = $4.36 / $1.30, max residual 9.1e-13 / 5.6e-17.
11. **Look-ahead.** None. Bar high/low used only post hoc to explain zero-slip fills, never to price or select.
12. **Unseeded bootstrap.** No bootstrap exists anywhere; the Sharpe-0.5 bisection (`:344-361`) is deterministic.
13. **Locked-forward / old-regime leak.** **Zero** input rows at or after 2026-08-01 and zero before 2022-01-01 across all three data files. No 2006-2021 data touched. No CrossTrade/NT8 tool called or needed.
14. **Session-boundary straddling.** Entry-session ≠ exit-session count is 0 for both Product B objects under both the bar-grid map *and* my independent roll; Product A ends flat on 1,139/1,139 sessions. Daily attribution is unambiguous; no trade straddles the 18:00 roll.
15. **Early-close handling.** Could not find a single mispriced early-close fill. The incidental v1e corroboration (short entries on the final bar of 2022-02-21 13:00 and 2025-12-24 13:15) reproduces exactly.
16. **Table arithmetic.** Yearly slices sum to the full-dev row for all three objects on G_raw, slip, comm, net, RT count and session count; tick figures reproduce from dollars; breakeven = G/C; ±25% spans = 0.5·C/net. All close.

---

## FILES I WROTE (scratchpad only; **no repo file was created, edited or deleted**)

- `C:\Users\YUKEZH~1\AppData\Local\Temp\claude\D--OneDrive---Washington-University-in-St--Louis-TradingResearch-systematic-research\bfb80633-2ca8-4554-803e-2bd6cbeeb4c1\scratchpad\redteam_v4.py`
- `C:\Users\YUKEZH~1\AppData\Local\Temp\claude\D--OneDrive---Washington-University-in-St--Louis-TradingResearch-systematic-research\bfb80633-2ca8-4554-803e-2bd6cbeeb4c1\scratchpad\redteam_v4b.py`
- `C:\Users\YUKEZH~1\AppData\Local\Temp\claude\D--OneDrive---Washington-University-in-St--Louis-TradingResearch-systematic-research\bfb80633-2ca8-4554-803e-2bd6cbeeb4c1\scratchpad\redteam_v4c.py`
- `C:\Users\YUKEZH~1\AppData\Local\Temp\claude\D--OneDrive---Washington-University-in-St--Louis-TradingResearch-systematic-research\bfb80633-2ca8-4554-803e-2bd6cbeeb4c1\scratchpad\v4_rerun.txt` (full stdout of their script, re-run)
- `C:\Users\YUKEZH~1\AppData\Local\Temp\claude\D--OneDrive---Washington-University-in-St--Louis-TradingResearch-systematic-research\bfb80633-2ca8-4554-803e-2bd6cbeeb4c1\scratchpad\v4_rerun.json`

## FILES REVIEWED
- `D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\runs\W17_C4_COMPLIANCE\V4_FRICTION.md`
- `D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\runs\W17_C4_COMPLIANCE\src\v4_friction.py`
- `D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\runs\W17_C4_COMPLIANCE\spec.yaml`
- `D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\runs\SMV2M_MASTER_BUILD\parity.py`
- `D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\src\analytics\sm_metrics.py`
- `D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\research\operational\LOCKED_FORWARD.md`
- plus all 6 declared input artifacts.

**Recommended minimum corrections before this is cited:** add CIs/t-stats to §2 and §5 and downgrade the "collapse" claim to unmarked-inference-with-caveat (D1/D2); disclose the +$34,997.10 excluded Jun–Jul 2026 slice (D3); relabel "4,711 flat-to-flat cycles" and its per-cycle stats (D4); fix the §4 turnover sentence (D7).