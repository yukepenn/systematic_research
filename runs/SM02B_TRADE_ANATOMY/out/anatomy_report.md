# SM02B_TRADE_ANATOMY — trade-path anatomy report

**Run:** `runs/SM02B_TRADE_ANATOMY/` (INSTRUMENTATION, burn 0). **Date:** 2026-08-08.
**Substrate:** `runs/SM01_SUBSTRATE/out/member_trades.parquet` (34,147 trades) + `vote_state_3m.parquet` + `e10_daily_py.csv`, joined to `runs/AUDIT03_BARS/nq_3m_2022_2026.csv` highs/lows.
**Dev window:** entry_sess ≤ 2026-05-31 → **32,744 trades over 1,139 sessions**. All CIs: day-clustered circular block bootstrap (cluster = entry session, block=5, B=2,000, seed 20260808), 95% percentile intervals. Bands: fast vm6–12, mid vm14–22, slow vm24–30. $ figures are NQ member scale ($20/pt, net of $2.18/side + embedded 1-tick slip).
**Everything below is in-sample MEASUREMENT for SM03/SM04 spec design — no strategy claim, no selection.**

Builder: `anatomy_build.py` (this dir). Tables: `out/anatomy_tables/t0…t6c`. Headline: `out/headline.json`.

## 0. S_entry recovery (t0_s_validation.csv)

- **FACT:** S at trend birth is recovered **exactly**: recomputing `member_states` per member (parity-gated simulator) and reading `s_eff[entry_bar−1]` equals `clamp(vm·sigma460[entry_bar−1], 10.0, 300.0)` for **all 34,147 trades (max |diff| = 0.0; 0 fallback cases)**. The flip fires at entry_bar−1 (close decision), fill at entry_bar open; every entry has `flip[entry_bar−1]≠0` (asserted).
- FACT: 900 trades (2.6%) sit at the 300-pt upper clamp; 8 at the 10-pt lower clamp. Using sigma at entry_bar instead of entry_bar−1 would err by up to 24.4 pts (median rel. diff 0.20%) — the eb−1 form is the exact one and is what all normalizations below use.
- FACT: reconstructed running MFE/MAE paths reproduce the substrate's final `mfe_pts`/`mae_pts` to <1e−9 for every trade (window = bars[entry_bar : exit_bar] inclusive, from 3-min highs/lows vs entry fill px).

Dev pooled base rates (FACT): win rate 39.33%; mean win +$1,876 / mean loss −$1,125; gross +$24.15M / −$22.36M (PF 1.080); **net $1.796M**; top-1% (net ≥ $8,431, n=328) sums to **$3.71M = 207% of total net**.

## 1. MFE/MAE distributions, winners vs losers (t1_mfe_mae_dist.csv)

- FACT (pooled): winners median MFE/S = 1.87 (q75 2.77), median MAE/S = **0.29** (q90 0.77). Losers median MFE/S = 0.42, median MAE/S = **0.95** (q75 1.22, q90 1.56) — losers routinely trade *through* 1.0·S adverse because the Solar exit (anchor−S ratchet) reacts slower than a fixed-S stop.
- FACT: winners take their worst heat early (median bars_to_mae = 3) and their peak late (median bars_to_mfe = 40, bars_held 61); losers peak early (median bars_to_mfe = 5) then bleed (median bars_to_mae = 19, bars_held 25).
- FACT: session-close exits produce 37.6% of winners (79.8% in slow band) vs 9.9% of losers — the right tail is disproportionately trend-into-close.

## 2. Progress curves (t2_progress_curves.csv)

P(final net>0 | running MFE < q·S by bar b, still open) and E[remaining net] (final − mark at bar-b close):

- FACT: no-progress populations have depressed win rates — e.g. MFE<0.25S by b=10: P(win)=0.314 [0.299,0.328] vs 0.545 for the progress complement; by b=20: 0.299 vs 0.588.
- **FACT (decisive): E[remaining net] of no-progress trades is POSITIVE at every pooled (b,q) cell** — e.g. b=10,q=0.25: +$75/trade [−13,+163], sum +$0.85M; b=20,q=0.50: +$104 [+18,+195], sum +$1.28M. The many small bleeds are paid for by rare large late recoveries.
- INFERENCE: a pure "no progress by bar b → exit" rule (D-family time stop, un-gated) destroys value in expectation at every horizon tested. Low P(win) ≠ negative remaining expectancy in a 39%-win/fat-tail book.

## 3. Stop-trigger populations — decision-critical (t3a_stop_grid.csv, t3b_mae_crossing.csv, t3c_catastrophe.csv)

### (a) time-to-progress × current-MAE grid (b ∈ {5,10,20,40,80,160}, q ∈ {0.25,0.5}, m ∈ {0,0.25,0.5,1.0})

- **FACT: no pooled cell has E[remaining net] with CI entirely below zero.** Most negative pooled points: b=10,q=0.5,m=1.0: −$75 [−157,+3.0], n=672; b=5,q=0.25,m=1.0: −$52 [−127,+24], n=596. m=0 cells are all positive (see §2).
- **FACT: the only clearly-negative cells are MID band, m=1.0:** b=5,q=0.25: E[rem]=−$264 [−410,−146], n=60, P(win)=0.000, 0 top-1% hits; b=5,q=0.5: −$248 [−385,−137], n=67; b=40,q=0.5: −$268 [−467,−40], n=59. Populations are small (~60 trades / 4.4y; ~$16k each).
- INFERENCE: once MAE ≥ 1.0·S is required, the b/q coordinates add nothing — the trigger population is essentially "crossed 1.0·S adverse", best measured at first crossing (below).

### First-crossing of MAE ≥ m·S (t3b; remaining marked at crossing-bar close)

| group | m | n crossed | P(recover to net>0) | E[rem from cross] [CI] | Σ rem | top-1% crossed |
|---|---|---|---|---|---|---|
| pooled | 0.25 | 26,423 (81%) | 0.271 | +$32.7 [−14,+84] | +$863k | 161 |
| pooled | 0.50 | 20,429 (62%) | 0.169 | +$3.2 [−32,+40] | +$65k | 48 |
| **pooled** | **1.00** | **9,418 (29%)** | **0.041 [0.037,0.046]** | **−$14.0 [−26.8,−0.23]** | **−$131.7k** | **4 (1.2%)** |
| pooled | 1.50 | 2,395 | 0.019 | −$3.9 [−17,+11] | −$9.4k | 2 |
| pooled | 2.00 | 736 | 0.018 | +$5.4 [−9,+22] | +$4.0k | 1 |
| **mid** | **1.00** | **1,799** | **0.018 [0.011,0.026]** | **−$43.6 [−73.8,−11.3]** | **−$78.4k** | **0** |
| fast | 1.00 | 7,042 | 0.049 | −$8.2 [−22.1,+6.1] | −$57.4k | 2 (2.8% of fast top1) |
| slow | 1.00 | 577 | 0.014 | +$7.1 [−70,+100] | +$4.1k | 2 |

- **FACT: the only pooled threshold with CI-negative remaining expectancy is m=1.0·S** (barely: CI-hi −$0.23). Cutting at the crossing-bar close would have added +$131.7k = **7.3% of dev net**, touching 4/328 (1.2%) of top-1% trades.
- **FACT: the effect is concentrated in the MID band** (−$43.6/crossing, CI clean, +$78.4k = 8.6% of mid net, **zero** top-1% touches — no mid top-1% trade ever exceeded MAE 0.913·S). Fast is directionally negative but CI-straddling and touches 2.8% of fast top-1% (> 2% bar); slow is valueless (+).
- FACT: below 1.0·S, stopping is expected-value-destructive (m=0.25: forgoes +$863k); above ~1.5·S there is almost nothing left to save (only 2.2% of trades ever reach 2·S).

### (b) Catastrophe table (t3c)

- FACT: final loss ≥ 1.0·S: 5,911 trades, −$9.43M = **42.2% of gross losses**; ≥1.5·S: 590 tr, −$1.13M (5.1%); ≥2·S: 160 tr, −$0.43M (1.9%); ≥3·S: 39 tr, −$0.15M (0.7%). Dollar basis: ≥$2k: 2,907 tr, −$8.84M; ≥$4k: 428 tr, −$2.19M; ≥$8k: 2 tr, −$18k.
- FACT: P(recovery to net>0 | interim MAE ≥ thr) = **4.1% at 1.0·S**, 1.9% at 1.5·S, 1.8% at 2·S, 1.9% at 3·S. Trades that ever cross 1.0·S carry total net −$12.52M.
- FACT: touch-basis excess loss beyond 1.0·S (Σ over final losers of loss − 1.0·S·$20) = $1.44M — an upper bound on what a perfect intrabar 1.0·S stop could save; the implementable bar-close-marked figure is the t3b +$131.7k. The gap is gap-through: by the crossing bar's close the price is already well past the threshold. Realistic resting-stop capture lies between, nearer the close-marked number.
- INFERENCE: a disaster stop is a **loss-distribution reshaper** (removes the −2·S..−5·S final-loss region that holds ~$1.1–1.4M of excess loss) far more than an expectancy engine (+$0.13M close-marked). Its value for SM03 is DD/logG-shaped, not mean-shaped, and must be re-simulated (stops change subsequent re-entry state — not modeled here).

## 4. Entry-state conditioning (t4a/t4b/t4c) — SM04 design input

### (e) |vote_pend| at the decision bar (entry_bar−1), pooled:

| bucket | n | frac | win rate | mean net | net share | top-1% share |
|---|---|---|---|---|---|---|
| 0–3 | 13,833 | 42.2% | 0.383 [0.372,0.393] | +$18.9 | **14.6%** | 14.9% (49) |
| 4–6 | 8,845 | 27.0% | 0.395 | +$64.8 | 31.9% | 25.6% |
| 7–9 | 5,725 | 17.5% | 0.405 | +$55.4 | 17.7% | 20.4% |
| 10–13 | 4,341 | **13.3%** | 0.407 | +$148.4 | **35.9%** | **39.0% (128)** |

- FACT: win rate is monotone in |vote_pend|; the top consensus bucket carries 2.7× its trade-share in net and 2.9× in top-1% membership. But the bottom bucket still holds 49 of 328 top-1% trades — zeroing it would breach the 90% right-tail retention gate margin cheaply (~15% of tail count, $0.5M of top-1% net).
- CAVEAT: mean-net CIs per bucket all straddle 0 (day clustering, huge variance); ordering is suggestive (INFERENCE), share numbers are FACT.

### flips20 (member flips in the 20 bars ending at decision): FACT — bucket 5+ holds 53% of trades, 49% of net and 68.9% of top-1%; sparse-flip entries (bucket 1) hold only 3.7% of top-1%. Consensus-cluster entries are where the tail lives.

### sigma460 percentile (dev bar distribution): FACT — non-monotone: net concentrates in q[0.2,0.4) (+$1.06M) and q[0.8,1.0) (+$0.95M) while q[0.4,0.8) is ≈ −$0.28M; **59.8% of top-1% trades enter in the top sigma quintile** (only 2.1% in the bottom). HYPOTHESIS territory only — the non-monotonicity is a warning against any vol filter without a mechanism story.

## 5. Loss clustering (t5a/t5b) — decision-critical (d)

- **FACT (trade level, same member): no loss clustering.** P(loss | ≥1 prior consecutive loss) = 0.601 [0.590,0.611] vs base 0.607; ≥2: 0.596; ≥3: 0.600. And E[net | streak≥2] = +$87 [+16,+162], E[net | streak≥3] = +$101 [+16,+199] — **higher** than base +$55, CI-positive. Slow band after ≥3 losses: E[net] = +$610 [+131,+1165].
- **FACT (E10 day level): mild anti-persistence.** P(day<0 | prior day<0) = 0.568 [0.526,0.608] vs base 0.590 vs 0.620 after an up day; E[next day | prior day<0] = **+$195 [+11,+374]** vs unconditional +$104. After 2/3 consecutive down days: P(down) 0.553/0.559, E[next] +$194/+$232 (CIs straddle).
- INFERENCE: any de-risking triggered by recent losses (skip-after-loss, daily-loss shutdown, streak-based sizing) cuts into **above-average** expectancy days/trades. The E10 book earns its money on 41% of days (59.0% of E10 dev days are negative; dev E10 net $119.0k/1,139 days) — loss-reactive throttles are structurally anti-edge here.

## 6. Right-tail anatomy & protection constraints (t6a/t6b/t6c) — decision-critical (c)

- FACT: top-1% = 328 trades (≥$8,431), Σ +$3.71M = 207% of dev net; median net $10.5k, median bars_held 168 (8.4h).
- **FACT — MAE constraint m\*:** worst interim MAE/S of top-1%: q50 0.24, q90 0.60, q95 0.76, **q98 = 0.90**, q99 0.99, max 2.34. So pooled **m\* ≈ 0.90·S**; per band: fast 1.53 (max 2.34), mid 0.81 (max **0.913**), slow 0.90 (max 1.37). A 1.0·S stop touches 4/328 = 1.2% pooled (≤2% ✓), **0% of mid** top-1%, but 2.8% of fast top-1% (✗ per-band).
- **FACT — time-to-progress constraint: there is NO (b,q) pure time-stop that is right-tail-safe.** Even the loosest cell (b=160, q=0.25) stops 17/328 = 5.2% of top-1% ($166k of tail net); b=20,q=0.25 stops 26.2%; b=5,q=0.5 stops 66.8%. Bars-to-first-0.5·S-MFE among top-1%: q50 17, q75 87, q90 151, **q95 211, q98 297**; to 1.0·S: q50 39.5, q95 287. A quarter of eventual top-1% winners still show MFE < 0.31·S after 80 bars (4h).
- FACT: with an MAE gate the grid becomes safe: all (b,q) cells with m ≥ 1.0 touch ≤1 top-1% trade (≤0.3%); m=0.5 cells touch ≤6 (≤1.8%) — safety comes from the MAE gate, not from (b,q).
- INFERENCE: the right tail is slow, deep-breathing, and session-long. Any exposure-reduction rule must key off adverse excursion (≥1.0·S; ≥1.55·S if applied inside the fast band) and never off elapsed-time-without-progress.

## Design implications for SM03/SM04 (INFERENCE unless noted)

1. **Kill the pure D-family time-to-progress stop.** E[remaining] positive in every pooled cell (FACT) + ≥5% top-1% incidence at every (b,q) (FACT).
2. The only defensible stop is a **disaster stop at ≥1.0·S adverse excursion**, valued as tail-shape reshaping (removes 42% of gross-loss mass region; recovery odds 4%) with modest close-marked expectancy (+7.3% of net pooled; concentrated in mid band, CI-clean there, zero mid tail touches). Fast band: raise to ≥1.55·S or exempt. Slow band: no evidence of value. Must be validated by full re-simulation (re-entry interaction) in SM03, per-band, against gates §6.6/6.7.
3. **No loss-reactive throttles** at member or E10-day level (FACT: post-loss expectancy is at-or-above base at both levels).
4. SM04 sizing: |vote_pend| at entry is a real monotone quality axis (share FACTs); any down-weighting of the 0–3 bucket must budget for its 15% share of top-1% count — the §6.6 tail-retention gate binds quickly.
5. sigma-percentile filters: not supported (non-monotone); high-sigma states are where the tail lives — never down-weight top-quintile sigma entries.

## Caveats

1. All measurement in-sample on dev; no rule was selected or optimized here. Grid cells were pre-declared in the spec/task.
2. "Remaining net" marks at the decision/crossing bar **close**; a real stop fills next bar open (±1 tick) or intrabar with gap-through. Close-marking understates savable loss vs a resting intrabar stop (touch-basis upper bound $1.44M at 1.0·S) but is the honest 3-min bar-close-decision figure.
3. Substrate MFE/MAE windows include the exit bar's full range even for Solar exits that filled at the exit bar's open — interim extremes near exit are slightly overstated; first crossings at the exit bar were assigned remaining = 0.
4. Stop/exposure counterfactuals ignore state interaction: a stopped member would re-enter only on the next flip; true system deltas require re-simulation (SM03).
5. Day-clustered bootstrap treats within-session trades as one cluster; member loss-streaks spanning sessions are reweighted approximately. E10 day-level conditional CIs use within-block consecutive tuples (block=5), so long-streak conditionals (k=3) rest on few effective blocks.
6. B=2,000 (spec speed choice) vs program-standard 10,000; percentile CIs, not studentized.
7. Top-1% defined pooled on dev net; per-band top-1% counts (71/144/113) are small — band-level 2% statements have ±1-trade granularity.
