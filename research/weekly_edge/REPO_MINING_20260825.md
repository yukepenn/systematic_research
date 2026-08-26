# REPO MINING — production candidates from our OWN research (2026-08-25)

Produced by the `we-mine-repo` workflow: four parallel agents mined campaign #1 (Solar Wave),
campaign #3 (SYSTEM_MASTER), campaign #4 (Scalping Lab) and campaign #6 (OTR) for signals and
mechanisms campaign #7 had never used, then a synthesis agent ranked them by expected
production gain per unit of research effort.

Campaign #7's baseline at the time: E5 box, 10.62 pts/session, 12.90 % of bars in position,
0.0603 pts per bar-in-position (`runs/WE_W30_PRODUCTION2/REPORT.md`).

**Candidate #1 was acted on immediately as `runs/WE_W31_RESTORE`.** The rest are queued here
with their evidence so they are not lost.

---

# RANKED PRODUCTION CANDIDATES FOR CAMPAIGN #7 (7 survive)

Objective throughout: **points/session at 1 contract**, not Sharpe. Baseline = E5 box: 10.62 pts/session, **12.90 % of bars in position**, 0.0603 pts/bar-in-position (`runs\WE_W30_PRODUCTION2\REPORT.md` Q1). W30's own closing question — "raise time-in-market at E5's density, or raise density at S1's time" — is the ranking criterion.

Two diagnostics I ran during this pass (scratchpad only, no repo writes; both on `runs\SM1M_SUBSTRATE\out\nq_1m_2022_2026.parquet`, 1,620,044 bars) are cited below as **[measured now]**.

---

## 1. SESSION-OPEN TREND-STATE RESTORE (Type-3 warm start) — by far the largest lever

**1. What / where.** `research\weekly_edge\src\run_we_w01.py:194-198` — at every session end `sm14_1m` sets `m_pos[m]=0; m_pend[m]=0` for all members, but **does not reset `m_up` / `m_anchor`**. The re-entry rule at `run_we_w01.py:152-161` only takes a position from flat when `m_sig[m] != 0`, i.e. on a *fresh* Type-1 flip. A member sitting mid-up-leg at 17:00 ET is therefore flat for **the entire remainder of that up-leg plus the whole following down-leg** — potentially days. Mechanism prior: `src\analytics\solarwave.py:149-155` (Type-3 STRENGTHEN) and `research\original_trader_reconstruction\solar_family\src\otr_engine.py` `WrapperPolicy.entry_types`.

**2. Evidence.**
- **[measured now]** narrow6 members: trend state is UP on **56.0–59.5 %** of bars but the member is actually LONG on only **26.1 % → 17.7 %** (VolMult 6 → 16). "Up-leg but FLAT" = **29.9 %–41.8 % of all bars**, rising monotonically with VolMult (all13: VolMult 30 = up-leg 62.0 %, long **12.5 %**, up-leg-but-flat **49.6 %**).
- **[measured now]** Ensemble level, narrow6: bars with ≥50 % of members UP = **64.31 %**; bars with ≥50 % of members LONG = **21.93 %**. all13: **62.35 % vs 11.37 %**.
- This is the mechanical cause of W30 Q2's "95.5 % of absent bars = vote below 0.5". Those are **high-agreement** bars, not the unprofitable 0.3–0.5 agreement band W22 already tested and rejected.
- External confirmation, `runs\OTR_S1_ARBITRATION\out\scorecard.csv`: E13_P0 {1,3} vs E1_P0 {1} = **4,143 vs 2,915 trades (+42 %) at unchanged per-trade expectancy ($55.88 vs $54.49) and unchanged PF (1.1502 vs 1.1444)**; net $231,530 vs $158,845. Type-3 alone is independently profitable (E3_P0: PF 1.1225, $45.51/trade). Campaign #1's DM01 explicitly records that "immediate-restore arms" were **deliberately not run**.
- **Not** covered by W06b H1 (`run_we_w06b.py:30-88`): H1 re-arms only within 3 bars of a *one-bar* target dropout and resets `last_dir=0` at `fb[i]`, so it can never fire across a session boundary. W06 logged it as "INERT — never fired… untestable as specified."

**3. 1-min NQ OHLCV: YES.** Close-only; no new data, no new constant.

**4. Why production.** Pure time-in-market — the exact term W30 named. It buys the *high-agreement* absent bars, not the marginal ones, and it disproportionately restores the SLOW members (whose exposure loss is 42–50 % of bars), which is where points-per-trade lives.

**5. Cheapest experiment.** Two lines in `sm14_1m`: at the first bar of each session set `m_pend[m] = +1 if m_up[m] else (-1 if not m_up[m])` (long-only: `+1 if m_up[m] else 0`) instead of 0. Rebuild the 4 target paths, re-score the existing 32-config E5-box harness (`run_we_w19.py` / `run_we_w20.py`), report Δpts/session, Δ%bars-in-position, Δpts-per-bar-in-position, and the same circular-shift null W21/W22 used. ~1 hour of compute. Extension if it works: full Type-2 (PULLBACK) intra-session re-entry, which needs H/L and the `solarwave.py:285-367` latch ported onto the adaptive `tv` array (~30 lines, parity-verified 0 FP/0 FN over 45,825 events).

---

## 2. TIME-OF-DAY-NORMALIZED THRESHOLD CLOCK

**1. What / where.** `sm14_1m` sets `S = clamp(VolMult · σ460, 40t, 1200t)` where σ460 = trailing mean |Δclose| over 460 **1-minute** bars (`run_we_w01.py:104-118`). A 460-minute trailing window *lags* the intraday volatility cycle by ~4 hours, so the threshold is systematically wrong at both ends of the day. Prior art: `research\system_master\CURRENT_TRUTH.md:495-515` (M1, `runs\W18R1_M1_VOLSEASON`).

**2. Evidence.**
- **[measured now, on #7's own substrate]** `f_slot = mean(|Δclose_t| / σ460_t)` by 1-min ET slot, 1,380 slots each ≥200 bars: **min 0.294 (16:49) → max 5.865 (08:31), a 19.95× spread**. 09:31 = 5.261, 09:32 = 4.578, 10:00 = 2.137, 14:00 = 0.761, 19:00 = 0.382, 22:00 = 0.526. So the threshold is **4–6× too tight at the RTH open and the 08:30 release minute, and ~2–3× too wide across the whole Asia/evening block.** M1 measured 11.04× on 3-min bars; at 1-min it is **nearly twice as bad**.
- W06 leakage decomposition (`runs\WE_W06_TRENDCAP\REPORT.md`): **chop loss 24–35 %** and wrong-side 23–33 % are the two dominant leakage classes; timing/exits are third-order. Chop is precisely what a too-tight threshold produces.
- Campaign #1 H-014: volatility-normalised threshold beats price-normalised by **+0.728 Sharpe, p = 0.009** — the campaign's only clean significance result. H-012: estimator lag from 0.13 to 7.96 sessions all works (Sharpe 0.769–1.494), so this is not a fragile axis.
- The one failed construction (M1 arm_FULL: Sharpe 0.5577 vs 0.7092, CDaR $35,498 vs $27,162, top-10 retention 80.5 %) failed for a **measured, avoidable** reason: `S` is frozen at trend birth and flips cluster in high-f slots (E[f|flip] = 1.536 vs E[f|all] = 1.000 ⇒ mean S **+64 %**, flips **−46 %**). CURRENT_TRUTH states the null is "**CONDITIONAL** on this estimator and this application point."

**3. 1-min NQ OHLCV: YES.**

**4. Why production.** Attacks the single largest leakage class directly. Two-sided: fewer whipsaw flips at the open (each avoided whipsaw is a saved 2.872-tick friction event *plus* a preserved position), and tighter thresholds overnight where 39.4 % of bars currently sit under a 2–3× oversized threshold and produce few entries.

**5. Cheapest experiment.** Avoid M1's application point entirely: run the ratchet on a **TOD-devolatilized price path** `p̃_t = p̃_{t-1} + Δclose_t / f_slot(t)` (f from a *prior-days-only* same-slot trailing mean — reuse the leakage-audited construction already in `sm14_1m`'s B-MOM band and `research\scalping_lab\src\python\w8_bmom.py`'s assertion triple), threshold in normalized units, convert fills back to real prices for P&L. Report E[f|flip] and mean S as the first two numbers (M1's failure signature), then Δpts/session and flips/session by ET segment.

---

## 3. MULTI-CLOCK MEMBERS (3-min / 5-min ratchet state, 1-min decisions)

**1. What / where.** Every member in `sm14_1m` advances its ratchet on every 1-min close. The owner mandated a 1-min **decision cadence**, not 1-min **members**. W06b H5 "two-speed" varied VolMult only, not the bar clock; nothing in `research\weekly_edge\src\*.py` resamples the bar series.

**2. Evidence** (campaign #1, `research\02_solar_refinements\WAVE1_report.md` D4; `research\deep_research\DC01_DC02_RESULTS.md`):
- Same 90/179 config, full history: **3m slip-1 $209,314 / $27.18 per trade / daily Sharpe 1.08** vs **1m $161,567 / $15.76 / 0.63**. 3m × SM 150–300 is **16/16 points positive**; the 1m profitable band [170,280] has holes and SM ≤ 150–160 is negative after costs.
- Mixed **1m+3m 18-cell ensemble Sharpe 0.786 vs 1m-only 10-cell 0.717** (+0.069).
- Mechanism, measured: DC01's close-basis crossing excess is **~23.5 ticks = $117.57 per segment = 89 % of ALL friction**, and it is roughly **constant in threshold** (17.9 t at δ=60 → 28.3 t at δ=440). It is a per-*event* tax set by bar volatility, so a coarser clock pays it less often. Slip-2 retention runs vm6 51.6 % → vm30 96.6 %; #7's stress line is $14.36/RT, ~3× the basis those numbers were taken at.

**3. 1-min NQ OHLCV: YES** (resample in-place; `runs\AUDIT03_BARS\nq_3m_2022_2026.csv` also exists).

**4. Why production.** Raises **density** (pts per bar in position) rather than time — the second of W30's two terms — by roughly doubling points per trade and lengthening holds. It also compounds with candidate 1: slower-clock members have longer up-legs and therefore lose *more* exposure to the session reset.

**5. Cheapest experiment.** Add a 5th and 6th member set to the existing 32-config vote: members whose ratchet updates only on 3-min (and 5-min) bar closes, positions still evaluated and filled at 1-min bars. Score as configs 33–48 in the same `run_we_w19/w20` harness. Report pts/session, pts/trade, trades/session and the leave-one-subfamily-out spread (W21's test).

---

## 4. LIQREV01 STRESS-GATED REVERSAL AS A PARALLEL NON-SOLAR SLEEVE

**1. What / where.** `research\system_master\LIQREV01_STRESS_REVERSAL\{SPEC.md, REPORT.md, src\01_liqrev01.py, out\liqrev01_trades.csv}`. rv5 = √(Σ squared 1-min point returns over 5 sessions); Stress = trailing-252 percentile of rv5 ≥ 0.90; LONG if session return ≤ q20 of the trailing 63 days, SHORT if ≥ q80; enter at session close, exit next session close, 1 tick adverse each side, $14.36/RT. **Fully coded, spec frozen 9775c0a before the run.**

**2. Evidence.** Full 2007–2026: N=455, **$579/trade, $263,646**, episode-block CI **[+$155, +$1,061]**, both sides positive, 3×3 plateau all nine cells positive, matched-placebo (calm days matched on signed point move) −$162/t ⇒ the state carries a **~$740/trade spread**. The only construction in 83 SYSTEM_MASTER ledger rows to pass **all 8 frozen gates on the letter**. **[measured now, restricted to #7's era]** 2022+: **96 trades, $1,531/trade, $146,956 total ≈ +$627/week ≈ +31 pts/week** — a **+60 %** add on E5-box's $1,040. Per year: 2022 $36,830 (24 tr) · 2023 **zero trades** · 2024 $24,374 · 2025 $82,604 · 2026 $3,148. **2022 is #7's weakest year (Sharpe 0.102).**

**3. 1-min NQ OHLCV: YES**, 100 %.

**4. Why production.** Different **regime coverage**: it fires only in vol-stress clusters, exactly where a long-only trend vote is halted by its session box or on the wrong side. It is the only non-Solar answer to W25's MODEL-RISK verdict that already has a passing gate record, and W27's finding (non-Solar voters cut Sharpe 0.305→0.23) is about *voting*, not about a parallel sleeve.

**5. Cheapest experiment.** Rerun `src\01_liqrev01.py` unchanged, join `out\liqrev01_trades.csv` to E5-box daily P&L over 2022-01→2026-07, report Δpts/session, joint worst week, and the overlap of LIQREV's winners with E5's top and bottom deciles. **Blockers to carry, not repeat:** 98.6 % of the 20-year net is post-2020; effective N ≈ 5 macro episodes; standalone Sharpe 0.680 with a 7.2-year underwater stretch; the red team found it profits on the SYSTEM_MASTER Solar's **top**-decile days (−$46,517 on its bottom decile) — that specific complementarity must be re-measured against E5-box, not assumed.

---

## 5. GAP-REJECTION FADE AS A PARALLEL NON-SOLAR INTRADAY SLEEVE

**1. What / where.** `research\04_complementary_family\B01_WAVE_SPEC.md:62-64` (rule: gap ≥ 0.35 % faded toward the prior close, 11:30 ET time stop), ledgers `b01e_gap_trades.csv`, `b02_gap_trades_slip1.csv`, escalation `b02_gap_escalation_result.csv`.

**2. Evidence. [measured now from the committed ledger]** 633 trades 2022-01-05 → 2026-07-31, **$118.63/trade, $75,095 total, 2.75 trades/week ⇒ +$326/week ≈ +16 pts/week**; per year −$43.8 / +$162.4 / +$68.4 / +$144.5 / **+$351.3** per trade (2022→2026); 301 long-side / 332 short-side. $108.63/trade at slip-2. Independence gate **PASSED**: losing-day correlation with the Solar book **−0.078**, Solar top-10-day retention **101.7 %**, roll artifact 0.8 %. It failed **only** three tail/consistency gates: top-1 % of trades = 90.1 % of net; worst trade −$8,544 / trade-ES5 −$5,390 **stopless**; 52.7 % of active months positive. Campaign #1 recorded that a stopped/risk-managed variant is a legitimate NEW hypothesis needing fresh preregistration.

**3. 1-min NQ OHLCV: YES.**

**4. Why production.** Additive intraday points in the 09:30–11:30 window on gap days, from a genuinely orthogonal mechanism, with an *improving* per-trade trend into 2026. Its three failures are exactly the class #7 has already proven it can fix at the session level (W22 session halt: circular-shift null at the 98th percentile, p = 0.020).

**5. Cheapest experiment.** Re-derive the 633 events on `nq_1m_2022_2026.parquet` (verify the ledger reproduces), then add one preregistered stop and #7's own session box, and score Δpts/session and joint worst week alongside E5-box. Do **not** tune the 0.35 % or 11:30 constants — a re-tune makes it a new hypothesis under both campaigns' rules.

---

## 6. TRUE-RANGE σ INSTEAD OF CLOSE-ONLY |Δclose|

**1. What / where.** `run_we_w01.py:104-110`: σ is `mean(|close_t − close_{t-1}|)` over 460 bars — it ignores every 1-min bar's intrabar range. Prior art and code: `research\system_master\ATRPOOL01_POOLED_READJUDICATION\{REPORT.md, SPEC.md, src\01_atrpool01.py}` (SMV2AI/AJ/M5 lineage).

**2. Evidence.** **[measured now, #7's substrate]** mean(TR)/mean(|Δclose|) = **1.977**, and **97.0 %** of 1-min bars have TR > |Δclose| — i.e. the close-only estimator understates true 1-min movement by ~2×, a materially larger distortion than the 3-min case SYSTEM_MASTER measured (99.3 % of bars, smaller magnitude). Their calibrated blend `0.75·σ460 + 0.25·(ATR460/2.0255)`: standalone Sharpe **0.746 vs 0.709**, CDaR₀.₉₅ **$25,183 vs $27,162**, top-10-day retention **100.2 %**, flip count **+0.09 %**, portfolio 1.297 vs 1.264, old-regime net gap **+$71,544**. Final pooled 20-year adjudication (n = 5,269): **P(ΔSharpe>0) = 0.9963, CDaR5 −13.4 %**, G3-SPLIT pre-2020 **+$13.39/day CI [+0.48, +26.39]** — it failed **only** a self-imposed 0.90 CDaR bar, by 0.009. The axis is closed for *their* engine, never opened on a 1-min one.

**3. 1-min NQ OHLCV: YES** (needs H/L, which the parquet has).

**4. Why production.** Weakest production case of the seven — their flip count moved +0.09 %, so it is primarily a threshold-shape correction. Included because at 1-min the mis-estimate is ~2× and the change is a **single function** (`sigma()`), so the cost is near zero and it interacts directly with candidates 2 and 3.

**5. Cheapest experiment.** Replace `sigma()` with the 75/25 blend (recalibrating the `/2.0255` normalizer on 1-min bars so mean S is unchanged — report that constant before running), rebuild the 4 target paths, score Δpts/session, flips/session and per-trade points.

---

## 7. RE-ADJUDICATE THE +$1,000 SESSION PROFIT TARGET UNDER THE PRODUCTION OBJECTIVE

**1. What / where.** The session box (`research\weekly_edge\STATE_OF_THE_SYSTEM.md` §1; W26/W27) stops the sleeve at **+$1,000 realized = 50 NQ points**. The owner's stated target is ~100 points/session. **The shipped object cannot exceed 50 points on any session by construction.**

**2. Evidence.** W27 rates the target **weak — 88th percentile, p = 0.120 — "never called proven"**, kept on a four-way improvement. #7's own daily truth: "**the best 5 % of days deliver >100 % of all profit**" (W26). W30 Q2: the box accounts for **4.1 % of absent bars**. Campaign #1's DC01, on the price series with no strategy: median ω/δ = 0.73–0.77 against a mean of 1.07–1.31 ⇒ "**any exit rule that truncates the right tail attacks the only source of profit — a measured constraint, not a stylistic preference**"; exit-reason concentration on the frozen baseline: 279 session-close exits carry **+$189.6k at PF 10.8** while trailing-stop exits net negative; and the 16:30 timed exit that looked dominant on a 2-year window won only **4 of 28 matched pairs on the full history, median −$12,476**. Campaign #1's binding preregistered right-tail gate (`research\04_complementary_family\C01_WAVE_SPEC.md` §1: top-1 %-trade P&L share in any down-weighted state ≤ its session share, stratified block bootstrap block = 5 sessions, 10,000 draws) **has never been applied to #7's box**; it forbade announcement down-weighting at 20.5 % vs 12.2 % and killed all three ML arms at 10.4 % / 0.25 % / 49.4 % retention.

**3. 1-min NQ OHLCV: YES** (a re-score of existing trade lists).

**4. Why production.** Removes a hard mathematical ceiling on the stated objective. Honest expected magnitude is **small (~5 %; W22's pre-box quote was ~$1,118/wk vs the box's $1,060)** — it is here on cost, not size, and because the gate is required before any freeze regardless.

**5. Cheapest experiment.** Re-score the already-computed E5 trade lists with target ∈ {none, $2,000, $3,000, $5,000} × halt held at −$1,300, ranking on **pts/session** with worst-week reported as a constraint rather than an objective; then run the campaign-#1 right-tail gate on both halves of the box. Pure re-scoring, minutes of compute.

---

### Ruthlessly excluded (with the reason)
B-FADE release-day fade — 16 unseen years give **+1.68 t/trade [−6.43, +9.64]**, below #7's own existence bar. · B1 overnight hold — ~2 pts/session, CI_lo −0.338 at 10k reps, not significant at C1 friction, top-10 nights = 53 % of net, and it requires holding through the session close the architecture forbids. · Graded/E10 MNQ exposure, HTFDIR01 tilt, conviction sizing, pyramiding — leverage, banned by #7's own law and already measured in W06b H2 / W10 / W22. · VWAP sweep-reclaim, low-range fade, cross-asset gates, opening-range/overnight direction gates, efficiency chop classifier — all tested and killed in W07/W11/W18. · Lower vote threshold (W22: ≥0.30 gives $1,112/wk vs ≥0.50's $1,118), re-entry H1, early-flow H3, lower exit level H4, two-speed H5 (W06b), NOHYST/NOBLOCK (W04), member-set composition and concurrency (W19/W20/W30 Q3) — already tested by #7. · All exit/stop/trail overlays, loss-reactive throttles, circuit breakers, TV/X_FV/X_TREND exit lines, the 65-pt initial stop, loss-limit semantic C — risk mechanisms that reduce time in market. · Dealer gamma, DOM/L2, options, tick delta, cross-market breadth — data we lack or that failed its own bar.