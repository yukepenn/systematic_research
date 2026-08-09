## VERDICT: **CONFIRMED-WITH-CORRECTIONS**

All three files exist, contain what is claimed, and every headline number I re-derived by an independent path reproduced **exactly**. The machinery is sound and the pre-registration is genuine (git-provable). But the **sign of the headline scalar** — the one thing §5.1 is built around — is set by three under-disclosed convention choices, and the CDaR materiality verdict rests on the single most favorable of three methods, mislabeled "worst".

---

## DEFECTS

**D1 — HEADLINE-FLIPPING. `P_ruin` = max over 3 methods, `CE_g` = arithmetic *mean* over 3 methods. Not pre-registered, never listed as a weakness.**
`src/analytics/primary_objective.py:682-686` (`p_ruin_daily = max(head)` on line 683, `ce_g = np.mean([...])` on line 685).
Pre-reg §2.3 (committed at 9d84ddf, line 274) specifies `P_ruin = max over the three bootstrap methods`; it says **nothing** about combining `CE_g` across methods. The word "pooled" appears exactly twice in the 744-line report — `O1_OBJECTIVE.md:403` and `:425`, both inside result tables — never in §2 (the formal-definition section), never in §7 ("Open weaknesses"). Computed self-consistently *within* the method that produces the headline `P_ruin` (moving5):

| | as reported | self-consistent (moving5) |
|---|---:|---:|
| J, daily barrier, C=$100k, L=1 | **+0.0210** | **−0.0088** |
| J, intraday barrier | −0.1935 | −0.2292 |

Across 8 independent seeds with my own generators: J(pooled) **8/8 positive** (mean +0.0183); J(self-consistent) **8/8 negative** (mean −0.0119, range −0.0356..−0.0035). §5.1's "at the close the product at 1× on $100,000 scores marginally positive" and §6.3's "The objective itself flips sign: J = +0.021 (daily) vs −0.194 (intraday)" are both convention artifacts. I checked every other row of §5.3/§5.5/§5.6 — **only the headline row flips**; all others keep their sign.

**D2 — The CDaR materiality bar is decided on the most favorable method, and that method is labeled "worst".**
`primary_objective.py:805-808`: `cdar_matched_ratio_worst = float(max(ratios))`, then `material = max(ratios) >= 1.20`. Report `O1_OBJECTIVE.md:635` reads "**1.295** (worst method)". Per-method matched ratios (§6.2, reproduced by me exactly): moving5 **1.150**, moving20 **1.197**, stationary60 **1.295**. **Two of three pre-registered headline methods FAIL the pre-registered ≥1.20 bar** — including moving5, which the report itself designates as the worst method for `P_ruin`. Pre-reg §1.8 bar 1 says "(worst method)"; bar 2 names no method, so the selection was post-hoc. `max` is anti-conservative here: it is the method most favorable to the hypothesis.

**D3 — No Monte-Carlo standard error anywhere, on a scalar whose sign is the entire point.**
8-seed study (my generators): moving5 `P_ruin` mean 0.3273, **sd 0.0070**; seed 20260808 returns 0.3185, the *lowest* of the eight. J(pooled) sd 0.0074. Worse: the module's **own** test prints `[PASS] 1 determinism ... J=-0.010215` at `n_boot=300` (`test_primary_objective.py:75-81`) — the headline scalar is **negative** at a lower resample count, and this appears in the shipped test output. The report quotes "+0.0210" to 4 dp with no band. Same applies to §5.4's "turns over near L ≈ 0.6" at n_boot=500, where the L=0.5/0.6/0.7 spread (0.1851/0.1954/0.1736) is ~1 MC sd.

**D4 — λ is derived on a non-compounded growth convention but multiplies a compounded one; the mismatch biases λ low, and correcting it also flips the sign.**
`O1_OBJECTIVE.md:141`: `g_ref = ln(1 + 177315.1/100000)/(1139/252) = 0.2256` (verified: 0.225668). That is the house *non-compounded* `logG`. But `CE_g` is the *compounded* fixed-fraction log growth. On the same $100k base under the objective's own compounding, the twin's realized g is **0.3419** (I recomputed: final equity $469,020 over 1,139 sessions). Re-deriving λ consistently: 9 × 0.3419 / 2 = **1.54** → J = 0.3395 − 1.54×0.3185 = **−0.1505**. λ is disclosed as a preference, but its stated *derivation* is internally inconsistent with the quantity it penalizes, in the direction that produces a positive J.

**D5 — §2.2 point 3 is factually wrong, and it carries the stated rationale for the whole absorbing construction.**
`O1_OBJECTIVE.md:266-268`: "Absorbed paths keep a **finite, negative** terminal log wealth (the barrier level), so ruin drags `CE_g` down". Measured at the headline point (637 ruined paths of 2000): terminal log wealth mean **+0.1046**, median +0.0283, max +1.2484, min −0.3080 — **53.5% of ruined paths terminate POSITIVE**. Absorption costs only 0.0544 of CE_g (0.3642 → 0.3097). So §1.3's "The absorbing choice is itself the reason a leverage that maximizes naive mean growth is not optimal" (`:99-100`) is false: ~85% of the turnover in J is the λ·P_ruin term, not absorption.

**D6 — The headline "×1.497" compares two non-overlapping drawdown episodes ten months apart.**
`O1_OBJECTIVE.md:588`. Daily max DD 18.7719% troughs **2026-05-22** (peak at session index 1062); intraday max DD 28.1026% occurs **2025-07-30 15:51**. Episode-matched: on the intraday-max session the daily-close DD is **15.82%** (ratio 1.776); on the daily-max session the intraday DD is **19.85%** (ratio 1.058). The prose at `:594-596` ("Same trades, same fills, same capital — only the observation frequency differs") implies a like-for-like statistic that a max/max ratio is not. *The binary ruin claim is unaffected and survives* — first intraday 25% breach at 2025-07-14 09:51, close never breaches.

**D7 — The effect filed under "nulls" is larger than the effect declared MATERIAL, and the two are never placed side by side.**
Within the daily leg alone, method choice moves CDaR₀.₉₅ from 0.1461 (stat60) to 0.2033 (moving5) = **×1.391**, versus the intraday/daily matched ratio of at most **×1.295**. Same for ruin: daily-close `P_ruin` spread across methods **0.285**, versus the intraday-vs-daily gap **0.179**. Both figures appear in the report (§5.2 null #1, §6.2), but never in the same comparison, so a reader is not told that the O1a signal is smaller than the modelling-choice noise it sits inside.

**D8 — The module's own output contradicts the report's §5.3 null.**
`primary_objective.py:673-680` + `:825-826` return `capital_map_rule_capital_needed_at_thr` at the **H=504** horizon: moving5 $171,305 / moving20 $123,311 / **stationary60 $99,490**. §5.3 (`O1_OBJECTIVE.md:470-480`) instead quotes the full-1,139-session convention ($200,045/$140,204/$110,338 — which I reproduced exactly) and concludes "**the pre-registered C = $100,000 is BELOW the entire capital-map band ($110k–$200k)**". Under the module's own returned numbers, $100,000 is **above** the bottom of the band ($99,490). Two conventions ship in one deliverable; the null holds under only one and the report does not say so.

**D9 — Shipped `min_unit` path is broken, and its test certifies the broken number.**
`primary_objective.py:850-886`, line 862: `u = np.floor(u / min_unit) * min_unit`. At the module's own defaults (C=$100k, L=1, min_unit=1), u → 0 the first time equity dips below $100,000, after which equity is constant and u stays 0 **forever**. Measured on 500 moving5 paths: **89.2% freeze permanently**; CE_g collapses 0.295 → **0.0322**, P_ruin 0.324 → **0.004**. `test_primary_objective.py:224-228` asserts only `np.isfinite(J)` and prints `J=0.0265` as a PASS. §2.1 (`:251-253`) advertises it as "floor-to-multiple rounding for objects where that matters". Off by default, so no headline is affected — but it is a live trap the test blesses.

**D10 — The LOCKED-FORWARD guard is silently vacuous on undated input, while the provenance dict claims it was applied.**
`primary_objective.py:146-151`: `_index_is_datelike` does `pd.to_datetime(idx[:5])`, which **succeeds** on an integer RangeIndex (ints read as ns since epoch). Verified: `load_daily_pnl(np.array([100.,-50.,25.]))` returns `flags['dated'] = True`, `warnings = []`, index `[1970-01-01, 1970-01-01.000000001, ...]`. The documented behaviour at `:91-92` ("array-like (no dates; window guards are skipped and that is flagged)") **never fires**. Same for a 1-column DataFrame. No reported number is affected (all inputs were dated), but this is precisely the guard the campaign's locked-forward rule rests on.

**D11 — Three code paths populate the same key `cdar_frac` with two different statistics.**
`_path_stats` (`:344-355`) returns `cdar_frac = 1 − exp(−mean(worst-k **log** drawdowns))`; `_fixed_fraction_rounded_stats` (`:883`) and `_fixed_contract_stats` (`:913`) return the **arithmetic** mean of drawdown *fractions*. Independent arithmetic value for the realized path: 14.2606% vs the module/report 14.2838%. Small (0.023 pp), but `cdar_dollar_at_capital = cdar_frac × capital` (`:669`) then presents a log-space mean as dollars.

**D12 — `R3` field ignores leverage inconsistently within one dict.** `primary_objective.py:677` scales by leverage (`mdd * leverage > cap`); `:679` `capital_needed_at_thr` uses the **unlevered** p95. Identical at L=1; in `leverage_curve` the capital-needed field is silently constant across the grid.

**D13 — 16 sessions with unexplained intraday data holes, reported as benign range.** The 43 early closes are all correctly present (last-bar clock: 31×13:00, 9×13:15, 2×09:15, 1×09:30 — matches the brief exactly). But **16 further** sessions are short without an early close: 15 end at 17:00 with 420–459 bars, one ends 14:03; **2022-11-07 has 249 bars against a full 17:00 close**, and **2025-11-28 (a 13:15 close that should be 385 bars) has only 170** — a 56% hole. `O1_OBJECTIVE.md:396` quotes "170–460 per session" as normal variation; `integrity.intraday_construction` emits only min/max, no gap flag. Direction is conservative for O1a (fewer observation points ⇒ understated intraday risk), but it is undetected.

**D14 — Filing/governance.** Delivered into `runs/W17_C4_COMPLIANCE/`, whose committed `spec.yaml` declares `experiment: MEGA_PROMPT_V6_WAVE17_W0_V1R3`, `type: compliance_fix_not_an_alpha_trial` — a C4 execution-compliance run. No spec.yaml covers this work. `grep` finds **zero** mention of `O1_OBJECTIVE` or `primary_objective` in `research/registry/`, `research/CAMPAIGN_STATE.md`, `research/frontier.yaml`, or `reports/`. CLAUDE.md requires both. (Possibly the orchestrator's job — flagging so it is not lost.)

**D15 — Undisclosed padding bias (minor).** `build_session_logpath` (`:408-413`) pads to a 460-bar grid; 4,226 of 523,940 cells (0.807%) are padding, during which cum and peak freeze, so each short session's *end*-of-day drawdown is repeated up to 290× inside the bar-level CDaR sample (k_bar = 11,592 of 231,840). Deflationary, small, and the frequency-matched headline statistic is immune — but undisclosed.

---

## WHAT I TRIED TO BREAK AND COULD NOT

1. **File existence/content.** All three exist: `primary_objective.py` 1,000 lines (1,001 committed at 8b71aa9, minus one `import warnings` removed at 1c3a7d7), `test_primary_objective.py` 263 lines, `O1_OBJECTIVE.md` 744 lines with §0–§9 as claimed.
2. **Pre-registration ordering — DIRECT and provable.** §0–§2.5 (309 lines, contains zero result numbers) committed at **9d84ddf, 2026-08-08 23:29:13**; module committed at **8b71aa9, 23:38:18** (9 min later); results appended at **1c3a7d7, 23:41:01**. `git diff 9d84ddf 1c3a7d7 -- O1_OBJECTIVE.md` = **435 insertions, 0 deletions** — the pre-registration text was not altered after the numbers existed. This is the strongest form of this evidence available.
3. **Self-test.** I ran it: **16/16 PASS, 5.6 s**, plain `python`. Report §4 says 5.9 s — immaterial.
4. **Column identity (§4's naming-collision flag).** Independently ran `smv2i_lib.repro_gate()`: `champ` (published DUAL6040) vs column `_B` → max abs diff **2.0e-11**; `DUAL` (Solar leg) vs `_A` → **1.8e-12**. The collision flag is correct and load-bearing.
5. **Single realized path — fully independent re-derivation.** I rebuilt equity in **dollar space with an explicit sequential loop** (no `log1p`, different aggregation, different code): daily maxDD **18.7719%** (report 18.77), intraday **28.1026%** (28.10), ratio **1.4971** (1.497), matched CDaR ratio **1.6347** (1.634), bar-level 22.5910% (22.61). Solar leg: 24.4680% / 25.8938% / 1.0583 / 1.2010 (report 24.47 / 25.89 / 1.058 / 1.199). **Reconciles.**
6. **Bootstrap — fully independent.** My own moving-block and stationary-step generators + dollar-space `cumprod` + own absorbing logic, at seed 20260808: moving5 **0.3185 / CE_g 0.3097**, moving20 **0.1205 / 0.3468**, stationary60 **0.0335 / 0.3619**, J **+0.0210**. Every digit matches. **Reconciles.**
7. **Capital map.** My generator on the NQ series: **109,176.998 / 91,485.344 / 81,956.618** vs committed `capital_map_nq.csv` — exact. On the research curve: **$50,011.29 / $35,051.10 / $27,584.44** → $200,045 / $140,204 / $110,338, matching §5.3 exactly.
8. **C-P3 — stronger than claimed.** Committed `runs/SMV2I_CURVE_READS/out/c_p3_pcurves.csv` holds **exactly 0.1422** and **0.4298**; `reproduce_cp3` returns those bit-for-bit, not merely "within 0.001".
9. **§5.3 / §5.4 / §5.5 / §5.6 / §5.7 tables.** Every row re-run and matched to 4 dp, including twin net $179,288.70, twin J −0.0488, fixed_contracts J +0.1162, scale invariance (L=0.5/C=$100k ≡ L=1.0/C=$200,045), λ=2 → −0.2975. Legacy triple cross-checks against committed `nt8_dev_battery.csv` (TWIN_dev CDaR5 14,151.47, maxDD_eod 16,821.2). Top-10 share 0.5906 on 10/1,139 sessions confirmed independently.
10. **Look-ahead.** None found. Every statistic is a function of realized in-sample observations; block resampling draws only from realized data; no forward information enters any barrier, peak, or threshold. Paths start fresh at C.
11. **Session-boundary / 18:00 roll / early-close splicing.** Clean. The bootstrap resamples **whole sessions**; the intraday leg carries each session's entire bar vector; no session is ever split. I verified `is_last_of_sess` == `tail(1)` of every group, `sess_id`/`time` monotone, and `intraday_mtm_{A,B}` == within-session `cumsum(bar_pnl_{A,B})` at **exactly 0.0**.
12. **NT8 fill-timestamp convention.** Not reachable: the module never touches fills or trade times, only an already-reconciled per-bar MTM artifact.
13. **Double-counted commission.** None — the module consumes an already-net P&L series and never applies a commission.
14. **Locked-forward leakage.** `twin_daily.csv` max date **2026-07-31** (< 2026-08-01), so no raise; 45 post-dev sessions truncated as claimed and recorded. Parquet spans 2022-01-03 → 2026-05-29 only. **No 2006-2021 data is touched anywhere**, so the mechanism-evidence-only rule is not at risk.
15. **Seed hygiene / seed shopping.** Every generator takes a fresh `np.random.default_rng(seed)`; 20260808 is the house default and was pre-registered; across 8 seeds it produced the **lowest** moving5 `P_ruin` of the eight (favorable) but a mid-pack J — no evidence of shopping.
16. **Near-zero denominators.** `top10_day_share` guards `net <= 0`; `historical_intraday_vs_daily` guards zero-denominator ratios; the +597% relative gap sits on a 0.0335 denominator but is reported alongside the absolute, and the headline uses moving5.
17. **Silently dropped rows.** None. n=1,139 throughout; the only drop (45 twin sessions) is counted, warned, and surfaced in `load_flags`.
18. **No MCP/CrossTrade use, no writes outside the three paths, no commit/push by the agent.** Module imports only `math/os/pathlib/numpy/pandas`. Working tree clean; all three commits are orchestrator commits.

---

**Files read (not modified):** `D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\src\analytics\primary_objective.py`, `...\src\analytics\test_primary_objective.py`, `...\runs\W17_C4_COMPLIANCE\O1_OBJECTIVE.md`, `...\runs\W17_C4_COMPLIANCE\spec.yaml`, `...\runs\SMV2AH_DAY_CIRCUIT_BREAKER\out\intraday_mtm_series.parquet`, `...\runs\SMV2M_MASTER_BUILD\out\twin_daily.csv`, `...\runs\SMV2M_MASTER_BUILD\out\nt8_dev_battery.csv`, `...\runs\SMV2M_MASTER_BUILD\out\nt8\smm_v2_bars.csv`, `...\runs\PRODUCTB_ONECONTRACT_FINAL\out\capital_map_nq.csv`, `...\runs\SMV2I_CURVE_READS\{smv2i_lib.py, step2_cp3.py, out\c_p3_pcurves.csv}`.

**Red-team scripts written (scratchpad only):** `C:\Users\YUKEZH~1\AppData\Local\Temp\claude\D--OneDrive---Washington-University-in-St--Louis-TradingResearch-systematic-research\bfb80633-2ca8-4554-803e-2bd6cbeeb4c1\scratchpad\{rt_indep.py, rt_boot.py, rt_checks.py, rt_absorb.py, o1_at_9d84ddf.md}`.