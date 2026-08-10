# MOM01 — intraday momentum (Baltussen et al. JFE 2021) diagnostic on NQ

**Disposition: CLEAN_NULL.** The rest-of-day → last-half-hour momentum effect does not replicate
robustly in this campaign's own NQ data (insignificant, sign-unstable across years). Independent
of that, `rROD` is highly redundant with state already in the shared substrate (`vwap_dist_pts`
r=0.92, `M` r=0.72–0.80). No trading policy was built, per this family's own instruction.

## Correctness gate (passed before any result was read)

`u0_state_table.parquet`'s own build-time gate already reproduces the certified Product-B nets
exactly; re-verified here directly from the columns this analysis reads:
canonical-window `bar_pnl_B_nq_dollars` sums to **$301,915.92** (certified: $301,915.92) and
`bar_pnl_B_mnq_dollars` to **$28,587.10** (certified: $28,587.10) — exact match, both to the
penny. Health-only-extension incremental NQ net: **+$58,675.04** (consistent with
UNIFIED_STATE_MAP.md's documented $360,590.96 extended total = $301,915.92 + $58,675). No new
backtest engine, no new pricing convention, no new decision logic was introduced by this
analysis — pure re-expression of already-certified columns.

## Construction (Step 1)

Per RTH session: `p_open` = OPEN of the bar at `minutes_since_rth_open==3` (the 09:30:00 ET
print — bar timestamps mark bar END, so the 09:30–09:33 bar opens exactly at 09:30:00);
`p_1530` = CLOSE of the bar at `minutes_to_rth_close==30` (closes exactly at 15:30:00);
`p_close` = CLOSE of the bar at `minutes_to_rth_close==0` (closes exactly at 16:00:00 — this bar
is `is_rth==True` even though `session_phase` mislabels it `POST_RTH`, a disclosed boundary quirk
of that column, not used here for the price pull). `rROD = ln(p_1530/p_open)`,
`rLH = ln(p_close/p_1530)`. Of 1,181 total RTH sessions, **1,138 have all three marks** (43
dropped as short/gapped RTH days, e.g. holiday-truncated sessions); 1,095 fall in the canonical
window (`is_health_only_bar==False`) and 43 in the health-only extension.

## Step 2 — does rROD predict rLH in this data?

OLS `rLH ~ 1 + rROD`, canonical window, n=1,095:

| | slope (β_ROD) | t-stat | p (two-tailed) | R² | Pearson | Spearman |
|---|---:|---:|---:|---:|---:|---:|
| **canonical, full** | +0.0114 | +1.433 | 0.152 | 0.00188 | +0.0433 | −0.0018 |

**Literature cross-check** (Baltussen et al. Table B1, NQ): β_ROD=6.36, t=7.97 — highly
significant, robust. Our result is **directionally the same sign in the pooled point estimate**
(positive) but **statistically indistinguishable from zero** (p=0.15, R²<0.2%) and, critically,
**not stable year to year**:

| year | n | slope | t-stat | R² | Spearman |
|---|---:|---:|---:|---:|---:|
| 2022 | 250 | +0.0385 | +2.302 | 0.0209 | **+0.1409** |
| 2023 | 247 | −0.0073 | −0.431 | 0.0008 | −0.0454 |
| 2024 | 249 | −0.0156 | −0.788 | 0.0025 | −0.0632 |
| 2025 | 247 | +0.0088 | +0.566 | 0.0013 | **−0.0998** |
| 2026 (partial, Jan–May, canonical) | 102 | −0.0328 | −1.451 | 0.0206 | −0.0761 |
| **2026-06..07 (health-only ext., separate)** | 43 | −0.0342 | −0.755 | 0.0137 | −0.1809 |

Only **2022** shows a sizable, literature-consistent, individually-significant positive
relationship (t=2.30, Spearman +0.14). Every other slice is near zero, negative in slope, or
sign-ambiguous (2025: positive slope but negative Spearman). The health-only extension is also
negative. **This is a genuine, honestly-reported non-replication of the effect's strength and
stability, not a sign reversal** (the full-sample point estimate keeps the literature's sign but
carries none of its statistical power) — flagged per the family's own too-good/cross-check
instruction, in the direction of "weaker/less stable than the source paper," which is the less
alarming of the two possible surprises but still decisively fails the pre-registered replication
bar (`disposition_rule`: insignificant t-stat, negligible R², unstable sign → **CLEAN_NULL**).
Plausible explanations (not further chased, diagnostic-only pass): Baltussen et al. pool NQ with
1974–2020 daily data at a scale (decades, possibly volatility-normalized returns) this 4.4-year,
3-minute-bar sample cannot match in statistical power; the effect may also be regime-dependent
and 2022 (the campaign's most volatile year) may be idiosyncratically favorable to it.

## Step 3 — is rROD just a repackaging of existing state at 15:30 ET?

Pearson / Spearman correlation of `rROD` against the contemporaneous 15:30 bar's state,
canonical window, n=1,095:

| feature | Pearson | Spearman | verdict |
|---|---:|---:|---|
| `vwap_dist_pts` | **+0.9237** | **+0.9206** | near-definitional overlap |
| `M` | **+0.7249** | **+0.7958** | **highly redundant** (campaign threshold: \|corr\|>0.6–0.7) |
| `B` | **+0.6646** | **+0.7555** | **highly redundant** |
| `Tp` | +0.5299 | +0.5567 | moderate, below strict threshold |
| `T` | +0.5343 | +0.5594 | moderate, below strict threshold |
| `close_slope_20` | +0.3897 | +0.3477 | modest |
| `close_slope_20_atr` | +0.3704 | +0.3568 | modest |
| `ret_20` | +0.4119 | +0.3642 | modest |
| `ret_5` | +0.1854 | +0.1603 | weak |
| `HTF_tilt_state` | −0.0110 | −0.0243 | unrelated (different, slower timescale) |

**Reported plainly, per the family's own instruction not to search for a way to call this novel:
`rROD` is highly redundant with state the substrate already carries.** `vwap_dist_pts` at 15:30
is r=0.92 with rROD — expected on inspection since both measure "how far has price drifted from
a same-session reference established earlier that day," so this is a real but largely mechanical
overlap. `M` (r=0.72–0.80) and `B` (r=0.66–0.76) — the actual decision-score and B-MOM leg — also
comfortably cross the campaign's own 0.6–0.7 "highly redundant" bar. Only the slower Solar13-
derived `Tp`/`T` (0.53–0.56) and the shorter-horizon `ret_20`/`close_slope_20` (0.35–0.41,
different window: 60 min vs rROD's full 360 min) carry moderate-to-weak, non-fully-redundant
correlation.

## Step 4 — forward value of Product B's own last-30-minute action

`window_pnl_B` = Σ `bar_pnl_B_nq_dollars` over the 11 bars with `0 ≤ minutes_to_rth_close ≤ 30`
per session (the $ Product B actually earned in its own last-30-min window, whatever it did).
**Pre-registered structural note, confirmed before reading results**: `entry_blocked_c4` spans
the entire T-30min→close window and `forced_flat_c4` fires at T-21min (both from the certified
`health_substrate.py` construction) — so `position_B` can only **hold-then-be-forced-flat** or
stay flat in this window; it can never freshly enter or reverse. Product B therefore structurally
can only capture roughly the **first ~9 of the literature's 30 minutes** (15:30–~15:39) before
C4 flattens it — a real mismatch between the paper's rLH window and what this system's own C4
rule lets it realize, independent of whether the effect itself is present.

Bucket-residualized (M-strength tercile × vol tercile, same framework as R4/R5/EXP01/ICT02),
canonical window:

| sample | n | raw ρ(rROD, pnl) | resid ρ(rROD) | resid ρ(rROD·side) | ΔR² (+rROD) | ΔR² (+rROD·side) |
|---|---:|---:|---:|---:|---:|---:|
| FULL (incl. flat) | 1,095 | −0.0131 | −0.0072 | +0.0480 | +0.00001 | **+0.00725** |
| HELD ONLY (`position_B`≠0 at 15:30) | 783 | −0.0029 | −0.0037 | +0.0447 | +0.00001 | **+0.00822** |

The **raw (unaligned) rROD adds essentially zero** (ΔR² +0.00001) — expected, since P&L sign
depends on trade direction, not the raw sign of the day's return. **Side-aligned `rROD·side`**
(the natural directional form) adds a small but non-trivial ΔR² (+0.007 to +0.008). Year-by-year
(held-only, residualized Spearman of `rROD·side`): 2022 +0.076, 2023 +0.009, 2024 **−0.049**,
2025 +0.071, 2026(partial) +0.118 — 4 of 5 years positive but one clearly negative and all
magnitudes small; full-sample (incl. flat) is 5/5 positive but ranges only 0.008–0.099. Given
(a) Step 3 already shows `position_B`'s sign is itself substantially explained by the same-day
price action that produces rROD (B: r=0.66–0.76), much of the "alignment" step is re-deriving
information already implicit in the position, not adding a genuinely independent predictor, and
(b) the C4 structural mismatch above caps how much of any last-30-min effect Product B could ever
realize regardless. **No genuinely new, stable, exploitable incremental value found.**

## Too-good-to-be-true / leakage gate

`rROD`'s measurement window (09:30–15:30) does not overlap `rLH`'s (15:30–16:00) — Step 2 is
causally clean by construction. `window_pnl_B`'s window (15:30–16:00) does not overlap `rROD`'s
(09:30–15:30) either — Step 4 is causally clean too. `M`/`position_B` at the 15:30 bar are
available before both outcome windows realize. No result here is "too good" — the headline is a
null/weak result throughout, so this gate mainly served to confirm the modest Step-4 ΔR² isn't
an artifact of the position-alignment step accidentally reading forward information: it isn't
(`position_B` at 15:30 is fixed before the window it's evaluated against begins).

## Disposition

**CLEAN_NULL**, per the pre-registered `disposition_rule` (spec.yaml), triggered at its first
branch: Step 2's replication is insignificant (t=1.433, p=0.15, R²=0.0019) and sign-unstable
across 3 of 5 canonical years plus the health-only extension — a genuine, honestly-reported
failure to replicate Baltussen et al.'s NQ-specific finding at this sample's scale/frequency, not
a sign reversal. This is compounded, not rescued, by Step 3: even where the pooled point estimate
keeps the literature's sign, `rROD` itself is highly redundant with state the shared substrate
already carries (`vwap_dist_pts` r=0.92, `M` r=0.72–0.80, `B` r=0.66–0.76) — so it would not have
been new causal information for construction purposes even had Step 2 replicated cleanly. Step 4
confirms no meaningful, stable, exploitable incremental value for Product B's own last-30-minute
action (ΔR² ≤0.008, one of five years wrong-signed), further capped by a genuine structural
mismatch: Product B's own C4 forced-flat rule only lets it realize the first ~9 of the
literature's 30-minute window before flattening. **No trading policy constructed**, per the
family's own diagnostic-only instruction — this is a closing diagnostic result, not a lead
deferred for a future construction pass.

## Files

- `runs/MOM01_INTRADAY_MOMENTUM/spec.yaml` — frozen before results were read
- `runs/MOM01_INTRADAY_MOMENTUM/src/01_intraday_momentum.py` — analysis script (reads only
  `runs/U0_UNIFIED_STATE/out/u0_state_table.parquet`)
- `runs/MOM01_INTRADAY_MOMENTUM/out/mom01_sessions.csv` — session-level rROD/rLH/state table
  (1,138 sessions)
- `runs/MOM01_INTRADAY_MOMENTUM/out/mom01_summary.json` — all regression/correlation results
