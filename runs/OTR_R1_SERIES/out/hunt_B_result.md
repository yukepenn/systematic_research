# hunt_B_result.md — FAMILY B (session/calendar mechanics) — hidden entry-gate hunt

Scripts: `hunt_B.py` (label/feature build), `hunt_B_sim.py` (gated engine clone, certified
identical to `otr_engine.run_wrapper(reverse_on_flip=True)` when ungated: 127/127 Jan trades,
same 8 hard-skip mismatches), `hunt_B_mine.py` (separator mining), `hunt_B_battery.py`
(all candidates, reproducible). Feature matrices: `hunt_B_labelfeatures.csv`,
`hunt_B_matrix.csv`, `hunt_B_matrix2.csv`. Battery JSON: `hunt_B_battery.json`.

Base (gate = none): 5,403 trades, net 216,890.46, WR 39.46, PF 1.104, DD −37,746, hold 96.24.
Target: 4,351 trades, net 292,172.82, WR 40.29, PF 1.18, DD −32,677, hold 94.15.

## 1. BEST DEFENSIBLE RULE (Family B): B1 — first-bar-of-session signal drop

Pseudo-code (NT8 semantics, decisions at bar close):

    on bar close i:
        if Bars.IsFirstBarOfSession:   # bar stamped 18:01 ET (or first bar after any break)
            return                      # no entry decision on this bar; exits unaffected
        ... normal T1 flip entry / stop-and-reverse logic ...

Evidence FOR:
- The author's own editor screenshot (OTRIMG-0053) shows `if (Bars.IsFirstBarOfSession)` in
  the strategy source.
- It is the ONLY mechanism found that discriminates the HARD pair
  L@2023-01-08T18:02 SKIP (signal bar 18:01 = first bar of the Sunday session) vs
  S@2023-01-17T18:04 TAKE (signal bar 18:03, third bar) with ZERO collateral damage:
  no other labeled flip in the Jan slice signals on a session's first bar.

Scorecard (42 hard rows = 34 hard takes + 8 hard skips):
- hard takes preserved 34/34; hard skips reproduced 1/8 (L@18:02); extra entries 0;
  SOFT/EPS: 0 takes lost, 0 soft skips fixed. Net hard rows passed: 35/42.
Master aggregate: 5,373 trades (2687L/2686S), net 217,410.86, WR 39.51, PF 1.105,
DD −36,095.44, hold 94.98 (L 106.79 / S 83.16). vs base: −30 trades, net +520,
DD +1,651 better, hold moves 96.24 → 94.98 (target 94.15). Small but everywhere-positive.

## 2. Exploratory add-on: B3 — entry block for the first N bars of a re-open session
(only sessions whose open follows ≥2 calendar days without bars: Sunday opens and
holiday re-opens)

    allow_entry(i) = !IsFirstBarOfSession
                     and !(session_reopen_gap_days >= 2 and bars_since_session_open < N)

Label-safe for all N in [1, 450] (earliest labeled take on a re-open session is
S@01:33 on 2023-01-16, bar ~452). Master sweep (with B1):
N=60: net 223,570 | N=240: net 232,907 (max; +16,017 vs base; WR 39.76, PF 1.115,
DD −36,946, hold 90.88) | N=360: 225,581 | N=450: 219,963.
CAUTION: the curve is non-monotone and only ONE label point (18:02, already explained by B1)
touches this rule — N is aggregate-tuned, an overfit risk. Treat as a candidate for
prereg-style out-of-slice testing (Feb 2023 per-day tables), not as identified truth.

## 3. FALSIFIED Family-B candidates (with the exact counter-label)
- B2 all-session open block N≥3 min: kills EPS take S@2023-01-17T18:04 (signal 3 min
  after open). Only N=1..2 survives ⇒ collapses to B1.
- B4 block whole re-open session: kills HARD takes S@02:42 / L@04:27 / S@12:46 on 01-09.
- B6 block shortened (holiday) sessions: kills EPS takes S@01:33 / L@06:21 / S@12:54 on
  the MLK 13:00-early-close session. The trader DID trade the shortened session.
- B7 block session following an early close: kills EPS takes on 01-17 (L@07:21 ...)
  and would forbid the required missing −274.18 short. Master also worsens (203,653).
- B5 Sunday-evening block (18:00-24:00 of re-open sessions): label-safe, net 224,470 —
  subsumed by B3 sweep; same caveat.
- Holiday-calendar keying beyond the above: the Jan-2 evening (session after the New-Year
  full holiday) has a HARD TAKE (L@21:39, held overnight) — any "block after cash-closed
  day" rule dies on it; only weekend (gap≥2) versions survive, i.e. B3/B5.

## 4. KEY NEGATIVE: weekday-clock windows (SELTIME_W) pass all HARD labels but are
FALSIFIED by the master aggregate
Gate: drop first-bar signals; block Tue LONGS 12:30-17:00; block Wed 18:00-24:00 (both
dirs); block Thu 12:20-14:30 (both dirs) — signal-bar clock, ET.
Result: hard_ok = TRUE (42/42 hard rows exact — the only candidate found that does this),
1 soft violation (S@13:29 on 01-12 blocked). BUT master: 4,983 trades, net 119,236
(−97,654 vs base, −173k vs target), PF 1.061. Repeating those windows weekly for two years
destroys the account; the trader's aggregate proves his gate did NOT repeat weekly.
CONCLUSION: the Jan-slice hard labels alone are satisfiable by calendar numerology —
hard-label fit without aggregate movement is NOT identification. Any future candidate
must pass BOTH.

## 5. The missing 01-17 trade (short 14712.75 → 14726.25, −274.18 net)
- Exit is clean: the 07:20 flip signal fills at 07:21 open = 14726.25 exactly.
- Entry fill 14712.75 = open of bars 20:48 (01-16 eve), 05:39, 06:45 ⇒ signal bar
  20:47, 05:38 or 06:44.
- NO Solar event exists on any of those signal bars, in EARLY or in regenerated
  PullbackEarly=FALSE (LATE) mode: nearest LATE T2 shorts fire 20:12 (fill 14725.75) and
  02:19 (fill 14698.25); T3s fire 20:55+ (fill 14703.5). The vendor pullback timer cannot
  be re-phased to fire at 20:47. 05:38 is additionally implausible for any close-cross
  rule (close 05:37 == close 05:38 == 14712.00).
- Tested and failed as the trigger: session-VWAP cross (no cross at any candidate bar);
  prior-session VWAP (14724.04); prior-day pivot (14717.00 — crossed at 20:46, fill
  14715.00 ≠); flatten-price 14710 cross (fires 20:53); session-open 14716 cross (first
  fires ~20:43, fill 14713.50 ≠); EMA(N) crosses — EMA34/50/55 DO cross up exactly at
  06:44 (fill 14712.75 ✓) but the flat window 18:01→07:20 contains 42-48 such up-crosses,
  so a bare EMA-cross rule would have entered hours earlier; no arming condition found
  that selects 06:44 (or 20:47) uniquely.
- STATUS: resume-after-early-close is the right FAMILY for this trade (only early close in
  slice, position was flattened short at 13:00 with the Solar trend still short, and the
  system re-entered short during that same trend leg), but the exact deterministic trigger
  remains UNIDENTIFIED.

## 6. Cross-family disproofs established while hunting (do not re-propose without new state)
All evaluated in TRUE-system context (position/PnL streams reconstructed from labels;
taken trades' exits equal base exits — verified cent-logic).
- Per-direction consecutive-loss lockout (2 losses): S@16:04 TAKEN with S-consec=1 after
  12:48 loss vs S@12:21 SKIPPED with S-consec=1. Dead both thresholds.
- Session cum-PnL, per-direction session cum-PnL, calendar-day cum-PnL (incl.
  "only after 12:00" variants): L@20:14 TAKEN on 01-03 evening with session cumL=−465.90
  and calendar-day cumL<0; S@20:36 TAKEN on 01-12 evening with day cum=−2,957.
- Dying-leg wave/trend state: L@19:33 TAKE (old_wave −4) vs L@19:17 SKIP (−3);
  S@18:04 TAKE (+4) vs S@21:07 SKIP (+2). Signal_Trend at flip: 7/8 hard skips weak but
  29/34 hard takes also weak.
- Higher-timeframe Solar (5/15/30/60-min, session-anchored) direction/strength agreement:
  best single covers 4/8 skips with 40+ take violations.
- EMA(20/60/120/240/480/960/1440) side-of-price gates, gap/level filters (vs session open,
  prior close, session range position): no separation (skipped longs sit ABOVE the EMAs
  on 01-03 PM).
- Exhaustive mining: ~120 features × thresholds, all 2-term conjunctions, OR-pairs of pure
  conjunctions, positives = 8 hard skips, negatives = all 112 takes: NO pure separator
  exists in this feature space. The discriminator is not among standard bar/season/PnL
  state variables.
- Structural facts that any future candidate must honor: (a) skips are context-dependent,
  not clock-dependent — every skip time has a take at a conflicting coordinate on another
  day; (b) on 01-03 PM only LONGS are off while shorts trade to 16:04; on 01-05 from 12:21
  BOTH are off; on 01-12 PM/eve only LONGS are off; on 01-04 eve BOTH are off yet the
  NEXT morning trades resume at 02:52; (c) exit-on-session-close is certainly ON
  (S@16:04 held to 17:00 close is cent-exact); (d) evening entries are legal per se
  (L@21:39 held overnight, HARD).

## 7. Honest assessment
Family B contributes one near-certain mechanic (B1 first-bar signal drop — it is the only
clean explanation of the 18:02-vs-18:04 discrimination and matches the source-code
screenshot) and one label-safe aggregate-positive exploratory block (B3 re-open opening
block, +16k net at N=240, selection-risk flagged). Family B CANNOT explain the seven
remaining HARD skips: they sit mid-afternoon/evening on ordinary weekdays at coordinates
where other days have takes, and the one calendar construction that fits them all
(weekday windows) is decisively rejected by the 2023-2025 aggregate (−98k). The remaining
gate is state/event-driven and day-specific; its state variable is outside the ~120-feature
space mined here. The missing-trade mechanism (early-close resume) is real but its exact
trigger is unresolved; its entry bar carries no Solar event, which independently proves the
strategy contains at least one non-Solar entry trigger — consistent with the successor
strategy's "Ma" suffix (a moving-average trigger exists in the author's later code), though
no EMA rule tested selects the bar uniquely.
