# W7-2 — FSS-9: sweep-reclaim trade rules at dynamic/prior levels

Spec: `research/scalping_lab/specs/W7_rt2_discharge.md` §W7-2 (frozen, commit 1d76c14, before readout).
Code: `research/scalping_lab/src/python/w7_fss9_levels.py`. Seed 20260808.
Artifacts: `w7fss9_results.csv` (per-session), `w7fss9_pooled.csv` (120 pooled configs),
`w7fss9_levels.csv` (per-session levels + offsets), `w7fss9_verdict.csv`, `w7fss9_stdout.log`
(full tables; every number below appears there).

## Verdict

**FAMILY FAIL — 0/60 reclaim configs pass, 0/60 continuation configs pass, no plateau
anywhere, under BOTH back-adjustment offset readings.** The FSS-5 sweep-reclaim grammar
applied to the new level class (running RTH-VWAP, PDH, PDL, prior-RTH-close) does not
survive costs. This satisfies the W7-2 leg of the §9 closure condition ("W7-2 fails
pass/plateau").

## What was run (exactly as frozen)

- 37 discovery sessions (2025-08-14 → 2026-05-20; s20250902 quote-dead → 0 decision
  seconds, contributes no trades; epi/day divisors use all 37).
- Levels per session, all in ticks, actual contract space:
  - **VWAP** — running RTH-anchored VWAP from grid1s (`cum(last·vol)/cum(vol)` from
    09:30), usable from 09:45. **Moving level**: sweep, reclaim, and re-arm are all
    evaluated against the CURRENT VWAP value at each second (L[t], never a snapshot).
    Two-sided.
  - **PDH / PDL** — prior trading day's RTH high/low from the 3-min CSV
    (`runs/AUDIT03_BARS/nq_3m_2022_2026.csv`, rows < 2026-06-01 only; RTH = bars
    end-stamped in (09:30, 16:00]), offset-converted. PDH short-side, PDL long-side.
  - **PC** — prior day's RTH close (close of last RTH bar), offset-converted. Two-sided.
- Grammar (FSS-5, frozen): low-side sweep = `mid_low <= L - pierce` (primary 2t,
  neighbors 1t/4t), reclaim = `mid_last >= L + 1t` within 60 s → market entry LONG at
  the reclaim second (high side symmetric → SHORT). Continuation mirror (diagnostic):
  no reclaim within 60 s → enter in sweep direction at t0+60. One trade per sweep
  episode, re-arm |mid − L| ≥ 8t (current L), brackets (24,8) and (32,10), cap 300 s,
  cooldown 60 s, sequential per (level, side). Barriers on per-second mid_high/mid_low,
  same-second both-crossed → ADVERSE. Decisions on RTH quote-alive seconds only.
- Costs C1 = 2.872t, C2 = 4.872t. Day-clustered 95% CI: session bootstrap, 1000 reps.
- Baseline for lift: unconditional census P(target), same bracket and trade direction
  (`artifacts/census/excursion_surface.csv`): (24,8) long 0.2525 / short 0.2488;
  (32,10) long 0.2361 / short 0.2328. (Census cap 600 s vs rule cap 300 s — documented
  mismatch, baseline not re-run; census p_neither ≤ 0.6%, so the distortion is small.)
- Pass rule: net C1 > 0 AND CI_lo > −0.5t. Family verdict by plateau (both primary
  brackets pass AND ≥2/4 pierce neighbors pass; reclaim side only — continuation is
  diagnostic and can never produce a family pass).

## Offset audit (measured, material, documented)

Frozen rule: `offset_s = CSV 09:30 bar close − sechilo mid_last at 09:30:00`, stated
error ~1t (Last-vs-mid), constant within session. The end-stamped CSV 09:30 bar closes
with the last trade BEFORE 09:30:00.000, while the sechilo second STAMPED 09:30:00
ends at 09:30:00.999 — inside the first RTH second. Measured per contract era
(quote-dead session excluded; `w7fss9_stdout.log` lines 40–44):

| era (sessions) | pre0930 offset med/std (t) | lit0930 offset med/std (t) |
|---|---|---|
| s20250814–s20250911 | 3939.8 / 0.89 | 3940.2 / 10.22 |
| s20250922–s20251209 | 2989.8 / 1.01 | 2990.0 / 16.69 |
| s20251222–s20260312 | 1964.0 / 0.87 | 1975.0 / 18.48 |
| s20260317–s20260520 | 1129.0 / 2.03 | 1128.0 / 40.32 |

Pairing the CSV close with the mid prevailing AT the instant 09:30:00 (last pre-open
second, `pre0930`) reproduces the frozen rule's stated ~1t/constant-within-era property
almost exactly; pairing with the 09:30:00-stamped second (`lit0930`) injects the
open-second jump (std 10–40t) into level placement. Both readings were run in full:
**pre0930 = primary, lit0930 = sensitivity. The verdict is FAIL under both**, so
nothing rides on the interpretation. Roll steps between eras (~950/1026/835t) are
cleanly visible; offset within a session is constant by construction (no roll inside a
session). The ~1t Last-vs-mid error remains in all prior-day levels either way.

## Results — primary configs (pierce = 2t, W = 60 s; prior levels at pre0930)

RECLAIM (the family's trade side):

| level/side | dir | brk | epi | epi/d | days | P(tgt) | lift | netC1 (t) | 95% CI | netC2 | pass |
|---|---|---|---|---|---|---|---|---|---|---|---|
| VWAP/low | long | 24/8 | 551 | 14.89 | 35 | 0.2764 | +0.0239 | −2.006 | [−3.239, −0.818] | −4.006 | fail |
| VWAP/low | long | 32/10 | 530 | 14.32 | 35 | 0.2614 | +0.0253 | −1.856 | [−3.316, −0.363] | −3.856 | fail |
| VWAP/high | short | 24/8 | 562 | 15.19 | 35 | 0.2616 | +0.0128 | −2.502 | [−3.730, −1.099] | −4.502 | fail |
| VWAP/high | short | 32/10 | 549 | 14.84 | 35 | 0.2541 | +0.0213 | −2.197 | [−3.935, −0.450] | −4.197 | fail |
| PDH/high | short | 24/8 | 244 | 6.59 | 18 | 0.2746 | +0.0258 | −2.085 | [−3.812, −0.151] | −4.085 | fail |
| PDH/high | short | 32/10 | 237 | 6.41 | 18 | 0.1983 | −0.0345 | −4.543 | [−6.895, −1.955] | −6.543 | fail |
| PDL/low | long | 24/8 | 95 | 2.57 | 10 | 0.3053 | +0.0528 | −1.104 | [−4.354, +2.428] | −3.104 | fail |
| PDL/low | long | 32/10 | 91 | 2.46 | 10 | 0.2418 | +0.0057 | −2.718 | [−6.294, +0.391] | −4.718 | fail |
| PC/low | long | 24/8 | 188 | 5.08 | 19 | 0.2500 | −0.0025 | −2.872 | [−5.205, −0.418] | −4.872 | fail |
| PC/low | long | 32/10 | 185 | 5.00 | 19 | 0.2500 | +0.0139 | −2.345 | [−5.186, +0.764] | −4.345 | fail |
| PC/high | short | 24/8 | 186 | 5.03 | 18 | 0.2043 | −0.0445 | −4.334 | [−5.775, −2.681] | −6.334 | fail |
| PC/high | short | 32/10 | 181 | 4.89 | 18 | 0.1878 | −0.0450 | −4.982 | [−7.070, −2.744] | −6.982 | fail |

CONTINUATION mirror (diagnostic): every cell fails; netC1 range −2.09 to −3.13t with
CI_hi < −0.65t everywhere (all 60 cells); lift −0.8pp to +2.4pp. Episode counts are large (22–102/day)
because on days where price sits persistently beyond a static level every post-cooldown
second re-sweeps — a mechanical property of the frozen grammar (same as W4-C), reported
as-is, not selected on.

Pierce neighbors (1t/4t) and the lit0930 sensitivity: 0 passes anywhere (full tables in
`w7fss9_stdout.log` lines 46–180 and `w7fss9_pooled.csv`). Best cells in the whole
family: PDL/low pre0930 1t (24,8) netC1 −0.872 [−3.761, +2.524] (n = 96, 10 days —
sample-thin, CI spans zero, neighbor (32,10) collapses to −2.937); PC/low lit0930 4t
(32,10) netC1 −0.907 (its pre0930 counterpart is −2.761, i.e., not robust to the
offset reading). No cell satisfies even net C1 > 0.

## Reading of the failure

- **VWAP sweep-reclaim carries a small real conditional edge that costs bury.** All 12
  VWAP reclaim cells show positive lift over the unconditional baseline (+1.3 to
  +2.9pp), across both sides, both brackets, all pierces — a consistent structural
  signal. But the best P(target) is 0.2764 vs break-even 0.3397 at (24,8) / 0.3065 at
  (32,10) under C1: the lift is 3–8pp short of the cost hurdle, exactly the census-gap
  pattern seen throughout the campaign.
- **PDH sweep-reclaim shorts at (24,8)** similarly show +2.1 to +3.6pp lift but stay
  ≥1.7t below water at C1, and the lift vanishes at (32,10).
- **PC/high reclaim shorts are strongly ANTI-edge** (lift −4.5 to −7.6pp at pre0930):
  a sweep above the prior close that "reclaims" back below is followed by upward
  continuation more often than baseline — acceptance above prior close dominates.
- **PDL is sample-limited** (10 unique days touch PDL in 37 sessions); its (24,8)
  cell is the family's best-looking but has n = 95 and a CI from −4.4 to +2.4.
- The continuation mirror confirms no exploitable failure-to-reclaim edge either
  (lift ≈ 0 everywhere, net deeply negative).

## Caveats

- Prior-day levels carry the ~1t Last-vs-mid offset error (frozen, documented above);
  under the lit0930 sensitivity reading they additionally carry 10–40t open-second
  noise — the verdict is invariant to this.
- Census baseline cap is 600 s vs rule cap 300 s (frozen baseline reused, not re-run);
  census "neither" rate ≤ 0.6% bounds the distortion.
- Entries/exits are mid-based per house convention; C1/C2 carry the spread/slippage.
- VWAP is Last·vol-weighted from grid1s per the frozen W7-1 definition; its value is
  not tick-grid-snapped (documented; pierce/reclaim offsets are exact ticks around a
  fractional level).
- 37 sessions, day-clustered CIs; PDH/PDL/PC cells rest on 10–19 active days.

## Registry / closure implications

W7-2 (FSS-9, registry S26 per spec) is a clean kill: the new level class does not
rescue the sweep-reclaim grammar. Combined with W7-1 and W7-3 (other sections), the §9
closure condition's W7-2 leg is satisfied: **fails pass/plateau, both offset readings,
all 120 cells.**
