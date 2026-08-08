# SOLAR DRAWDOWN ATLAS (draft)

_SM02_DD_ATLAS, 2026-08-08. INSTRUMENTATION (zero R1 burn). Spec: `runs/SM02_DD_ATLAS/spec.yaml`._
_Data: `runs/SM01_SUBSTRATE/out/{e10_daily_py.csv, member_trades.parquet, vote_state_3m.parquet}`,
dev window sessions ≤ 2026-05-31 (1,139 sessions, 32,744 member trades, 519,714 bars).
Analysis code: `runs/SM02_DD_ATLAS/analyze_dd.py`. Seed 20260808; block-5 circular bootstrap, B=10,000._

**Conventions used here.** Episode = maximal underwater stretch of the E10 cumulative daily
(peak session = last session at the running high; decline window = first underwater session
through the trough session, inclusive). All trade decomposition is computed on the DECLINE
window only (that is where the depth accrues); recovery is reported but not decomposed.
Trades are assigned by `exit_sess` (realized P&L) while the daily is MTM — the window
trade-sum / 13 reproduces the daily depth at ratio 0.86–1.05 across all ten episodes (FACT),
so the assignment is faithful. Member-trade dollars are 13× the E10-executable scale;
"E10-eq" = member $ / 13. S at entry approximated as clamp(vm·σ460(entry_bar), 10, 300)
(flip-bar S may differ marginally; 44.75 fallback touches only the first 30 bars of 2022).

## 0. Dev baselines (FACT)

| quantity | value |
|---|---|
| dev E10 net / daily mean / daily sd | +$119,008.9 / +$104.5 / $2,338.7 |
| dev trade net (member $): mean / median / q05 / q95 | +$54.85 / −$329.36 / −$2,589.36 / +$4,000.64 |
| dev false-start rate (net<0 ∧ MFE<0.5·S) | 34.07% of trades; aggregate −$16.46M member (−$1.27M E10-eq) gross |
| dev flip density (flips/bar) | 0.1129 |
| dev mean \|vote_pend\| at entries | 5.131 |
| dev σ460 mean | 6.537 pts |
| dev long / short net (member $) | +$1,502,820 / +$293,266 |
| sessions at equity peak | 58 / 1,139 = 5.1% (2022: 18, 2023: 5, 2024: 14, 2025: 15, 2026: 6) |

The trade distribution is left-median / right-tail-carried: the median trade loses $329;
q25..q75 of trades average −$277; all of the net comes from the >q95 band (mean +$6,637).
This shape is the master key to the atlas: **a drawdown can be produced either by fattening
the left tail or simply by the right tail failing to arrive on schedule.** (FACT)

## 1. Path-level null: the drawdown census is NORMAL VARIANCE (FACT)

Block-5 circular bootstrap of the dev daily (B=10,000, dev-length paths, seed 20260808):

| statistic | bootstrap | realized |
|---|---|---|
| max-DD median (p25, p75) | −$45,378 (−$57,520, −$36,672) | **−$40,207.6** |
| P(max-DD ≤ −$40,208) | **64.3%** | — |
| episodes ≤ −$10k per path: mean (p05–p95) | 8.20 (3–13) | **8** |

The realized worst drawdown is SHALLOWER than the bootstrap median, and the count of ≥$10k
episodes matches the bootstrap mean almost exactly. Given the E10's own daily distribution,
the entire observed drawdown census is unremarkable — there is no evidence of episode-level
"broken regime" beyond what the marginal daily distribution already implies. (FACT)
Design corollary: DD-targeted overlays must beat a null in which these episodes are the
ordinary cost of the distribution's shape. (INFERENCE)

## 2. Episode register (all episodes ≤ −$10k, plus top-10 by depth; n=10 of 38 total)

E10-executable dollars. Decline = peak→trough sessions; TUW = peak→recovery.

| ep | peak | trough | recovery | depth | decline | TUW | NQ move in decline | dominant class |
|---|---|---|---|---|---|---|---|---|
| E01 | 2026-02-12 | 2026-05-29 | **UNRECOVERED at dev end** | **−$40,208** | 76 | 76+ | **+21.2%** (range 29.9%) | LEFT_TAIL_EXCESS |
| E02 | 2024-09-03 | 2024-12-05 | 2025-04-08 | −$28,005 | 67 | 153 | +10.7% | RIGHT_TAIL_ABSENCE |
| E03 | 2022-06-07 | 2022-07-15 | 2022-09-13 | −$22,128 | 28 | 70 | −4.3% | NO_PROGRESS_BLEED |
| E04 | 2025-04-10 | 2025-07-28 | 2025-09-02 | −$20,791 | 76 | 102 | **+24.3%** | RIGHT_TAIL_ABSENCE |
| E05 | 2022-02-24 | 2022-03-08 | 2022-04-26 | −$17,570 | 8 | 42 | −4.1% | LEFT_TAIL_EXCESS |
| E06 | 2025-11-20 | 2025-12-10 | 2026-02-02 | −$17,097 | 14 | 50 | +7.0% | SIDE_SPECIFIC_SHORT |
| E07 | 2023-01-09 | 2023-03-21 | 2023-08-24 | −$14,866 | 51 | **163** | +10.9% | RIGHT_TAIL_ABSENCE |
| E08 | 2022-04-26 | 2022-05-12 | 2022-06-03 | −$12,162 | 12 | 28 | −5.8% | LEFT_TAIL_EXCESS |
| E09 | 2022-09-13 | 2022-11-07 | 2022-11-10 | −$9,558 | 39 | 42 | −7.2% | NO_PROGRESS_BLEED |
| E10 | 2023-09-20 | 2023-11-09 | 2024-01-03 | −$8,867 | 36 | 73 | +0.7% | RIGHT_TAIL_ABSENCE |

FACT: **six of ten episodes — and the four largest post-2022 ones — occurred while NQ was
RISING.** The E10 does not primarily draw down when the market crashes; it draws down when
the market rallies in a way the ensemble is positioned against (short) or cannot ride (gap-up
staircase). 2022's bear market produced only whipsaw/bleed episodes of ≤ $22k.

## 3. Winner-absence vs loser-accumulation attribution (FACT)

Gap = window trade sum − (n_trades × dev mean trade). Band contributions from dev-quantile
bands (q05/q25/q75/q95 of the dev trade distribution); shares are of the (negative) gap.
Member $ except last column.

| ep | n_tr | gap (member $) | left-tail (<q05) share | right-tail (>q95) share | f<q05 (dev 5%) | f>q95 (dev 5%) | verdict |
|---|---|---|---|---|---|---|---|
| E01 | 2,142 | −622,418 | **0.99** | −0.55 (right tail SURPLUS +$340k) | **12.5%** | 7.2% | loser accumulation, both tails fat |
| E02 | 1,903 | −438,556 | −0.21 (left tail BETTER) | **0.83** | 3.9% | 2.5% | winner absence |
| E03 | 805 | −345,786 | 0.14 | 0.41 | 6.0% | 2.7% | mixed bleed (mid-bands 0.30) |
| E04 | 2,072 | −365,723 | 0.15 | **0.56** | 5.6% | 4.0% | winner absence (small winners only) |
| E05 | 243 | −237,174 | **0.64** | 0.23 | **20.6%** | 2.1% | loser accumulation |
| E06 | 389 | −234,099 | 0.37 | 0.36 | 11.6% | 1.5% | both |
| E07 | 1,441 | −244,670 | −0.60 (left tail BETTER) | **1.57** | 2.6% | 1.4% | pure winner absence |
| E08 | 414 | −184,184 | **0.80** | −0.14 (right tail surplus) | **15.0%** | 4.8% | loser accumulation |
| E09 | 1,101 | −180,543 | 0.47 | 0.05 | 7.7% | 5.9% | left tail + mid-band bleed |
| E10 | 1,055 | −174,224 | −0.70 (left tail BETTER) | **1.60** | 2.2% | 1.2% | pure winner absence |

Two clean, roughly equal families (FACT):

- **Winner-absence episodes** (E02, E04, E07, E10; −$72,529 of depth = 37.9% of the register):
  big-winner frequency collapses to 1.2–4.0% vs the dev 5%; the left tail is NORMAL OR BETTER
  than dev in three of the four. Nothing "goes wrong" trade-by-trade — the +$6.6k-class
  winners simply stop arriving. Stops/exit-tightening cannot prevent these; only more
  right-tail capture or lower exposure during their conditions could.
- **Loser-accumulation episodes** (E01, E05, E08; −$69,939 = 36.6%): f(<q05) runs 2.5–4×
  its dev frequency; these are the high-σ windows (σ460 1.52–1.63× dev) where S is wide,
  per-trade losses are large in dollars, and violent two-sided tape whipsaws entries.
- Remainder: mixed bleeds (E03, E09) and one side-specific squeeze (E06).

Trade-count-matched iid bootstrap percentiles are ≤0.5% for every episode, but this is NOT
usable evidence of abnormality: the 13 members trade one signal family and their trades are
strongly cross-correlated, so iid trade resampling wildly understates variance (CAVEAT).
The honest per-episode scale is the daily z (−0.90 to −2.78) and the §1 path bootstrap.

## 4. Cross-episode taxonomy: what recurs and what never fires

Dominant-class dollar shares of the −$191,251 register (FACT):

| class | episodes (dominant) | $ share | also triggered (secondary) |
|---|---|---|---|
| RIGHT_TAIL_ABSENCE | E02 E04 E07 E10 | −$72,529 (37.9%) | — |
| LEFT_TAIL_EXCESS | E01 E05 E08 | −$69,939 (36.6%) | — |
| NO_PROGRESS_BLEED | E03 E09 | −$31,686 (16.6%) | also in E01 E02 E07 E10 (6/10 total) |
| SIDE_SPECIFIC_SHORT | E06 | −$17,097 (8.9%) | also in E01 E02 E04 (4/10 total) |
| SIDE_SPECIFIC_LONG | — | — | E07 E08 (2/10) |
| VOL_SHOCK (σ +30%+ vs prior 20 sess) | — | — | E08 (+57%) |
| VOL_COLLAPSE (σ −20%+) | — | — | E04 (−44%) |
| SESSION_SPECIFIC | — | — | E01 (09:30–11:30 = 65% of bucket losses), E09 (02–08:30 = 61%) |
| **CHOP_CLUSTER** | **never** | — | flip-density ratio 0.95–1.21 in all episodes (threshold 1.25) |
| **HIGH_DISAGREEMENT** | **never** | — | \|vote_pend\| at entries 0.89–1.11× dev (threshold ≤0.85) |
| **FALSE_START_CLUSTER** | **never** | — | FS rate 34.1–42.0% vs dev 34.07%; ratio ≤1.23 everywhere (threshold 1.25) |
| NORMAL_VARIANCE | — (episode level) | — | but the WHOLE CENSUS is normal at path level (§1) |

Three falsifications worth recording (FACT):
1. **Drawdowns are not chop clusters.** Flip density is statistically flat inside every episode.
2. **Drawdowns are not disagreement regimes.** Entry-time \|vote_pend\| barely moves.
3. **False starts do not cluster.** The 34% false-start rate is a near-constant structural
   cost (−$16.5M member gross over dev), not an episodic phenomenon. Overlays that try to
   detect "false-start regimes" have no target. (INFERENCE from the three FACTs above)

What DOES recur (FACT): the **short side**. Window short-side P&L (member $): E01 −635,370,
E02 −332,794, E04 −362,259, E06 −200,614 — the four post-2023 majors are all short-bleed
episodes, jointly −$117.8k E10-eq of short losses while longs were net POSITIVE inside three
of the four windows. Dev-wide short net is only +$22.6k E10-eq (+$293k member), and its
yearly path is regime-lumpy: 2022 +$406k, 2023 −$13k, 2024 −$16k, 2025 +$361k, 2026(≤May)
−$445k member. The entire short book's dev profit is one bear year (2022) plus one crash
spring (2025); everything else it gives back inside rallies. (FACT)

## 5. Deep dive 1 — E01, the Feb→May 2026 −$40.2k bleed (the "Feb→Jun $40k" episode)

Peak 2026-02-12 at cum +$159,216; trough 2026-05-29 = **the final dev session** — the
episode was still AT its maximum depth when the dev window closed. Depth −$40,207.6 is
therefore a LOWER BOUND on the episode's eventual depth; the June–July holdout has not been
read and nothing here uses it. (FACT)

Monthly anatomy (E10 daily $; member trade $ for sides):

| month | E10 net | worst day | short (member) | long (member) | n_tr | FS rate |
|---|---|---|---|---|---|---|
| 2026-02 (from 13th) | −10,573 | −5,149 (02-13) | −37,304 | −112,267 | 349 | 40% |
| 2026-03 | +2,442 | −5,564 (03-23) | −24,503 | +77,594 | 618 | 40% |
| 2026-04 | −18,212 | −4,077 | **−347,729** | +108,894 | 617 | 40% |
| 2026-05 | −13,865 | −5,034 | **−225,834** | +56,226 | 558 | 40% |

- NQ rose +21.2% peak→trough (25,313 → 30,672) with a 29.9% intra-window range: a violent
  V (Feb–Mar break, then a two-month melt-up). σ460 averaged 9.92 = 1.52× dev. (FACT)
- Feb opened the hole two-sided (longs −$112k member in the break), then Apr+May shorts
  alone lost −$573.6k member (−$44.1k E10-eq) while longs earned +$165k — **the drawdown from
  April onward is one thing: shorts repeatedly initiated into a high-σ melt-up.** (FACT)
- Attribution: left tail 12.5% frequency (2.5× dev) AND right tail 7.2% (1.45× dev) — both
  tails fat, left fatter. This was not winner-absence: winners arrived (+$340k right-tail
  surplus vs expectation) and were overwhelmed. With σ high, S≈clamp(vm·9.9)pts is wide, so
  each wrong entry costs 1.5–2× a normal-year loser in dollars. (FACT)
- Losses concentrated 09:30–11:30 ET: −$371.9k member of a −$505k window total (65% of
  bucket losses; SESSION_SPECIFIC). The RTH morning was where the squeeze bars lived. (FACT)
- Flip density 0.99× dev, FS-rate ratio 1.14, |vote_pend| 0.96× — no chop, no disagreement,
  no false-start signature. The members were CONFIDENTLY wrong on the short side. (FACT)

HYPOTHESIS (for overlay design, untested): an exposure governor keyed on
(σ460 ≥ ~1.4× its 1-year mean) ∧ (price above a slow anchor) that halves SHORT entry size
would have attacked ~$44k E10-eq of this episode's short bleed while leaving the long book
untouched; it must be tested against gate 6 (right-tail retention) and against 2022, where
shorts in high σ made +$406k member.

## 6. Deep dive 2 — the longest underwater stretches

**Longest single episode TUW: E07 — 163 sessions (2023-01-09 → 2023-08-24), depth only
−$14.9k.** The signature pure winner-absence episode: NQ ROSE +10.9% during the decline
window, yet f(>q95)=1.4% (vs 5%) and the left tail was BETTER than dev (share −0.60). σ460
ran at 0.80× dev — the 2023 melt-up was low-σ, gappy, staircase-shaped; a 3-minute
trend engine cannot compound overnight-gap trends into intra-session runners, so the
+$6.6k-class winners never printed. Recovery took five further months because the same
low-σ regime also capped winner size on the way back. (FACT + INFERENCE)

**The 2024-09 → 2025-09 underwater complex (the true worst stretch): 257 sessions with
only 4 sessions at the equity high.** E02 (peak 2024-09-03, recovered 2025-04-08) rolled
into E04 (peak 2025-04-10) after just three sessions at the high; E04 recovered 2025-09-02.
Combined: effectively ONE YEAR underwater at depths reaching −$28k. E02 was winner-absence
+ short bleed into the Q4-2024 rally (Nov 2024 alone: shorts −$184k member); E04 was
winner-absence + VOL_COLLAPSE (σ −44% vs prior 20 sessions) as shorts fought the +24.3%
post-April-2025 V-recovery (Jun+Jul shorts −$258k member). (FACT)

Calendar-year at-peak counts sharpen this: 2023 saw 5/258 sessions at the high, 2026 (Jan–May)
6/106, and the full dev only 5.1%. **Being underwater ~95% of sessions is this system's
normal state; 6–12-month TUW is within one dev window's realized experience twice over.**
(FACT; and consistent with §1's bootstrap null.)

## 7. Session-bucket structure (member $, decline windows)

Dev-wide bucket net: 18–02: +$525.8k; 02–08:30: +$490.0k; 08:30–09:30: **−$10.8k**;
09:30–11:30: +$877.9k; 11:30–15: **−$247.8k**; 15–17: +$161.0k. (FACT; trade assigned to
the bucket of its ENTRY; avg hold 3.4h, so P&L spans buckets — descriptive only.)

Within episodes, the loss bucket wanders (E01: 09:30–11:30; E02: 02–08:30 and 11:30–15;
E09: 02–08:30) — only two episodes clear the 60% SESSION_SPECIFIC bar. The structurally
negative dev buckets (11:30–15 midday, 08:30–09:30 open-auction) lose in AND out of
drawdowns: that is a standing-cost observation, not a drawdown mechanism. (FACT)

## 8. Design implications (INFERENCE unless noted)

1. **Respect the right-tail gate.** 37.9% of register depth is pure winner-absence with
   left tails at-or-better than dev. No stop, no exit tightening, no entry filter that
   sacrifices winners can improve these episodes; they are the fallow field of the crop the
   system farms. Gate 6 (≥90% top-1%/top-10 retention) is exactly the right constraint.
2. **The short book is the one concentrated lever.** Short-side losses dominate the four
   post-2023 majors (−$118k E10-eq inside those windows) while the dev-total short book earns
   only +$22.6k E10-eq. Conditioning SHORT exposure (not long) on rally/recovery context is
   the highest-value overlay target this atlas identifies — but 2022 (+$406k member shorts)
   proves a static haircut fails; it must be regime-conditional, and the evidence for the
   asymmetry is regime-local (2024–2026). HYPOTHESIS to test, not a conclusion.
3. **Per-trade dollar-loss caps address the LEFT_TAIL_EXCESS family** (36.6% of depth, all
   in σ ≥1.5× windows where S is wide): a cap that scales sub-linearly with σ (or an MAE
   stop at fraction of S) targets E01/E05/E08-type dollars. Must verify right-tail retention:
   E01's window right tail was 1.45× dev — the same wide-S bars carry the winners.
4. **Do not build chop/disagreement/false-start regime filters for DD control.** All three
   signatures are flat inside every episode (§4). Falsified as drawdown predictors.
5. **σ460 20-session change marks turning points, weakly**: VOL_SHOCK preceded E08, VOL_COLLAPSE
   defined E04 (post-spike V-recovery = short-killer). Worth one conditioning test; only 2/10
   episodes carry the signature.
6. **Portfolio/TUW budgeting**: any sizing or capital plan must survive 8–12 months underwater
   and a −$45k median bootstrap max-DD (realized −$40.2k is the 64th percentile — i.e.
   LUCKY). Complementary engines whose losing days decorrelate from "NQ rallying against
   the vote" (the E01/E02/E04/E06 state) attack the actual DD driver; engines that hedge
   crashes do not (2022-style bears produced the SMALLER half of the register).
7. **E01 is live risk context** (FACT): the system entered the holdout at maximum drawdown,
   still deepening on the last dev session. Any monitoring spec (MONITOR-01) should treat
   −$40.2k as an open, not closed, episode.

## 9. Caveats

- Trade-level iid bootstrap percentiles (dd_trade_decomp.boot_pct) overstate abnormality;
  members are 13 correlated copies of one signal. Use z_daily and the §1 path bootstrap.
- Decline-window decomposition only; recovery phases not decomposed.
- exit_sess (realized) vs MTM daily mismatch is bounded by the 0.86–1.05 depth-reproduction
  ratios; E07 (0.86) is the loosest.
- S_entry uses σ460 at entry_bar, not the flip-bar S actually frozen by the engine (close
  approximation per SM01 conventions; affects the FS classification marginally).
- Session-bucket P&L assigns full trade net to the entry bucket.
- Episode E01 depth/duration are lower bounds (dev boundary); holdout untouched.
- Class thresholds (ratio 1.25, shares 0.5/0.6, σ ±30/−20%, etc.) were fixed before reading
  per-episode results within this run, but are still author-chosen constants; the band
  attribution (§3) is threshold-free and is the primary evidence.

## Machine outputs

- `out/dd_episodes.csv` — episode register (all 10 selected; timing, depth, recovery, classes).
- `out/dd_trade_decomp.csv` — full per-episode decomposition (sides, buckets, FS, flip, vote,
  σ, band contributions, bootstrap columns, price context).
- `out/dd_baselines.json` — dev baselines, path-bootstrap results, yearly side/at-peak tables.
- `out/deep_dive_monthly.txt` — monthly anatomy of E01/E02/E04/E07.
