# MC-55 — post-FOMC RV contraction test — REPORT

**Run:** `G2_F12_MC55_FOMCCRUSH_20260906` · **Ledger trial:** G00053 · **Date:** 2026-09-06
**Spec:** `spec.yaml` (committed before results) · **Program:** `src/run_mc55.py` · **Gate table:** `out/gate_table.txt` (program-printed)
**Evidence status of every number in this report: DISCOVERY_CONSUMED.**

## Verdict: **FAIL — and significant in the OPPOSITE (expansion) direction**

The preregistered claim was that NQ realized vol **contracts** after the FOMC release relative to
matched non-FOMC days (post/pre RV ratio LOWER on FOMC days). The measurement decisively refutes it:

| Quantity | Value |
|---|---|
| mean log(RV_post/RV_pre) — FOMC days | **+1.8522** |
| mean log(RV_post/RV_pre) — matched Tue/Wed controls | **+0.1191** |
| **Observed difference T** | **+1.7330 log-units (x5.66 in variance terms)** |
| Two-sided p vs 401-circular-label-shift null (seed 20260906) | **0.0025** (= 1/402 floor; 0 of 401 shifts reached the observed magnitude) |
| MDE at 80% power (printed by the program BEFORE the observed value) | 0.2282 log-units |
| N-BOUND declaration | NOT N-BOUND (MDE <= 3 x plausible 0.30) |
| Preregistered sign (contraction, T < 0) | **VIOLATED** — T is large-positive |
| Era signs (2006-12 / 2013-19 / 2020-26.05) | **pos / pos / pos** (+1.4931 / +1.5709 / +2.1670) — 3/3 stable |
| G5 power language | FAIL is **powered**: MDE (0.228) << 3x observed (5.199) — not UNDERPOWERED_STILL |

Even with the release spike itself excluded (post window starts at T+5 min), NQ realized variance in
the 85 minutes after the statement runs ~5.7x higher, relative to the midday pre-release window, than
the same ratio on matched non-FOMC Tue/Wed days. Both halves of the mechanism run against the card:
the pre-window is the well-known pre-FOMC calm (suppressed denominator) and the post-window stays in
an elevated-vol regime for at least 85 minutes (the press conference lives inside it in the 2013+ era).
The "uncertainty-resolution crush" story, at this horizon and windowing, is simply the wrong sign.

**FAILURE_MEMORY row (per decision_rule):** "NQ post-FOMC RV contraction at N=152: REFUTED with
p at the null floor — the effect is a +1.73 log-unit EXPANSION, stable 3/3 eras. MDE80 = 0.23."
Subtractive-policy content survives in mirror form: the 14:05–15:30 FOMC window is a
persistently-elevated-RV regime, not a crush; any engine that would someday trade that window must
be sized for ~5–6x normal post/pre variance ratios. Banking that reversed fact as a POSITIVE claim
would require its own preregistered trial; nothing here licenses an engine (no engine trades
14:00–16:00 today).

## Realized N vs ~160

- Scheduled decisions on the verified calendar 2006-01 -> 2026-05: **162** (~7.7/yr over 21 calendar
  years; 2020 has 7 — the 2020-03-17/18 meeting was cancelled and superseded by intermeeting
  actions; 2026 is a partial year: Jan/Mar/Apr).
- Excluded, scheduled but not Tue/Wed (the spec's control and shift-null designs are Tue/Wed-only;
  pre-stated in the program header before results): **7 Thursdays** — 2006-06-29, 2007-06-28,
  2012-09-13, 2015-09-17, 2018-11-08, 2020-11-05, 2024-11-07.
- Excluded, Tue/Wed but data-incomplete (pre-stated >=90%-bars rule at all three anchors): **3** —
  2006-05-10 (afternoon gap: 67 post-window bars), 2014-01-29 (session absent from the substrate),
  2010-03-16 (complete at its own 14:15 anchor — 91/86 bars — but a 10:30–12:00 gap of 75<82 bars
  fails the symmetric all-anchor eligibility needed for the anchor-carrying shift null; realized N
  would be 153 under own-anchor-only completeness; immaterial to the verdict).
- **Realized FOMC N = 152** (vs ~160 expected) over an eligible Tue/Wed calendar of **M = 2,073**
  sessions (1,921 controls). Era split: 51 / 53 / 48.

## Excluded unscheduled / intermeeting actions (listed; also removed from the control pool)

2007-08-10 (Fri, liquidity statement) · 2007-08-17 (Fri, discount-rate cut; call 08-16) ·
2008-01-22 (Tue, -75bp intermeeting cut ~08:20 ET; call 01-21) · 2008-03-11 (Tue, TSLF ~08:30 ET;
call 03-10) · 2008-10-08 (Wed, coordinated -50bp cut ~07:00 ET; call 10-07) · 2010-05-09 (Sun,
swap lines) · 2019-10-11 (Fri, bill purchases; call 10-04) · 2020-03-03 (Tue, -50bp cut 10:00 ET) ·
2020-03-15 (Sun, -100bp cut 17:00 ET) · 2020-03-19 (Thu, notation vote: swap lines) · 2020-03-23
(Mon, open-ended-QE statement ~08:00 ET) · 2020-03-31 (Tue, notation vote: FIMA repo) · 2020-08-27
(Thu, framework statement) · 2025-08-22 (Fri, notation vote, per fomccalendars.htm).

Calendar verified against federalreserve.gov/monetarypolicy/fomchistorical{2006..2020}.htm and
fomccalendars.htm (2021–2027) on 2026-09-06, before any RV was computed.

## Per-era release-time anchors (recorded before computing)

Windows are rigid translates of the spec's 14:00-era windows: pre = [T-120m, T-30m], post =
[T+5m, T+90m], ratio = log(RV_post/RV_pre); bars END-stamped, window [a,b] uses closes stamped
a..b inclusive, so the 14:00–14:05 release spike is excluded at every anchor.

| Anchor T (ET) | Applies to | Pre window | Post window |
|---|---|---|---|
| 14:15 | 2006-01-31 .. 2013-01-30, non-presser (49 meetings) | 12:15–13:45 | 14:20–15:45 |
| 12:30 | the eight 2011–2012 press-conference releases (statement 12:30, presser 14:15) | 10:30–12:00 | 12:35–14:00 |
| 14:00 | 2013-03-20 onward | 12:00–13:30 | 14:05–15:30 |

Under the circular-shift null each label carries its anchor; eligibility therefore requires window
completeness at all three anchors (symmetric between treatment and control).

## One hand-checked FOMC day: 2024-12-18 (Wed, 14:00 anchor)

Independently recomputed via a different code path (DatetimeIndex.between_time, separate script):
n_pre = 91 bars, RV_pre = 2.834189e-06; n_post = 86 bars, RV_post = 7.260669e-05;
log-ratio = **+3.2433** — identical to the program's out/fomc_table.csv row (+3.2433, matched
diff +3.273 against the era-3 Wednesday control mean of -0.0297 from out/era_table.csv).
Raw-bar confirmation of the release anchor: the 14:01-stamped bar (covering 14:00–14:01) jumps to
3,294 contracts from 268 the minute before, with a 70-point drop — the statement lands exactly where
the anchor says. (That spike bar is *outside* the post window, which starts at the 14:05 close.)

## Descriptive context (G6 — explicitly not a gate)

Daily dVIX (close-to-close, _VIX.parquet truncated at load to <= 2026-05-29 via parquet row filter;
post-seal rows never materialized): FOMC days -0.418 pts vs control Tue/Wed -0.068 pts
(2006-12: -0.929 vs -0.020 · 2013-19: -0.264 vs -0.061 · 2020-26.05: -0.045 vs -0.127).
So the *implied*-vol crush direction is visible descriptively — VIX does fall on FOMC days — while
realized intraday NQ vol expands: the two legs measure different objects, which is exactly why the
VIX leg was tolerated only as context. dVX (VX futures daily): no certified local store exists in
this repo; leg omitted — it is non-gating by spec and cannot affect the verdict.

## Gates (program-printed in out/gate_table.txt)

G0 seal PASS (max ts 2026-05-29 16:59) · G1 semantic PASS · G2 MDE-before-observed PASS
(MDE80 = 0.2282, not N-BOUND) · **G3 primary FAIL** (p = 0.0025 but sign is expansion, opposite to
preregistration) · G4 era stability PASS in the observed (positive) sign, 3/3 · G5 power PASS
(FAIL is powered; UNDERPOWERED_STILL does not apply) · G6 descriptive-only PASS.

## Deviations from spec (named)

1. **Anchor granularity**: the spec's calendar note gives era anchors "~14:15 pre-2011 / ~14:00 from
   2013" and instructs "use the actual release-time-of-era". The actual 2011–2012 practice was mixed
   — eight press-conference meetings released at 12:30 ET (a 14:15 windowing would have put the
   release *inside* the pre-window for those days) and 2013-01-30 was the last 14:15 release. The
   implementation uses the true three-anchor record above, fixed before computing.
2. **Seven scheduled decisions fall on Thursday**, contradicting the spec's parenthetical "(FOMC
   decisions land Tue/Wed)"; they are excluded and listed (pre-stated before results). Realized
   N = 152 vs ~160.
3. **Intermeeting-action dates removed from the control pool** as well as the treatment set (the
   spec says "EXCLUDED and listed" without specifying the pool; 5 of the 14 fall on Tue/Wed).
4. **dVX half of G6 omitted** — no certified local VX daily store; descriptive-only, non-gating.

Caveats noted, not deviations: control Tue/Wed sessions include FOMC-eve Tuesdays (per the spec's
literal control definition); 2020-03-17/18 (cancelled-meeting week) remain controls by the same
letter; the daily-VIX store is Yahoo-derived, used descriptively only.
