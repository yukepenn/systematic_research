# TASK V2 — RESUME-LEVEL DECODER (MLK-evening short, fill 20:48 open 14712.75)

Scripts: `v_rlvl_explore.py` (bar dumps), `v_rlvl_scan.py` (+ `v_rlvl_scan_out.txt`,
mechanism x reference x offset scan), `v_rlvl_freq.py` (all-session fire frequency),
`v_rlvl_early.py` (early-close scoping + per-evening predictions). Data:
`t2_canonical_1m.csv` via `otr_engine.load_ledger`.

## 0. The decisive data fact (kills every "first close beyond L" candidate)

MLK evening closes: 20:35 = 14714.00, **20:36 = 14712.00, 20:37 = 14712.00,
20:38 = 14709.25** (bounce: 20:39 = 14715.25 ... 20:41 = 14721.25, 20:43 =
14713.75, 20:44-46 = 14715.75/14717.25/14716.00), **20:47 = 14713.00** (trigger).
Three closes 18:02..20:46 sit BELOW the trigger close. Therefore **no memoryless
"first close beyond a static level" rule — with ANY reference level — can select
20:47.** The mechanism must carry state. (Session min close before 20:47 =
14709.25; min low = 14708.75.)

First-fire times of the requested static candidates (M1 first-close-beyond, short):
| candidate | level | first fire |
|---|---|---|
| prior session last-bar close 14710.00 (= 13:00 cash close) | 14710.00 | 20:38 |
| prior last close + 13t | 14713.25 | 20:36 |
| original entry 14708.50 | 14708.50 | never |
| original entry + 18t | 14713.00 | 20:36 |
| first-bar low 14715.00 | 14715.00 | 20:35 |
| first-bar low − 1..8t | 14714.75..14713.00 | 20:35..20:38 |
| prior cash LOW 14706.50 / HIGH 14784.75 / mid 14745.625 | — | never / never / ~18:0x |
| prior full-session mid 14720.50 | 14720.50 | 20:15 |
| TrendVector 14731.25 / TrailingStop 14753.50 (any small offset) | — | 18:01-19:0x |
| round numbers 14712.50 / 14710 / 14700 | — | 20:36 / 20:38 / never |
| evening VWAP (typical or close basis, any offset −80..+80t, any mechanism) | dyn | never lands on 20:47 |
| vendor T2, either mode, any PS/WWS | — | impossible: T2 pivots on TV = 14731.25; the 20:47 bar's high is 14715.25, ~16 pts inside — no parameterization reaches it |
| session-template variants (Break-at-EOD, 17:00 CT vs 18:00 ET) | — | irrelevant: the Solar Wave recurrence is a pure close-price ladder (`solar_wave()` uses no session information), so template choice cannot move any signal to 20:47 |

## 1. The surviving mechanism (data-forced): SECOND-BREAKDOWN LATCH

Fire = the start of the SECOND breach episode of a static level L:
closes break below L (episode 1 = 20:36-20:38, not taken), fully recover
(close >= L at 20:39), then break below L again → decision bar 20:47, market
order, fill 20:48 open = 14712.75 exactly. A "failed-breakdown → retest →
continuation" re-entry, trivially coded in NinjaScript with one bool latch.

Exact-first-fire window on MLK: **L ∈ (14713.00, 14713.75] with strict `Close < L`**
(equivalently L ∈ [14713.00, 14713.50] with `Close <= L`).
- L = 14713.00 strict fires one bar late (20:48 decision → 20:49 fill). Excluded.
- L ≥ 14714.00 fires at 20:43 (close 14713.75). Excluded.
- So the brief's "(14713.00, ~14714.9]" tightens to **(14713.00, 14713.75]**.
An order-based reading (sell-stop/limit at L) is excluded: any resting stop ≥
14711.75 fills intrabar at 20:44 or earlier; a limit at L fills on the 20:39
bounce at L. Only close-decision + next-open market matches 14712.75@20:48.

Grid scan (15 refs x 161 offsets x 11 mechanisms x 2 strictness): 380 combos
reproduce MLK 20:47 exactly; after the two control silences 129 remain, in
three families: episode-2 latch (sharp, few refs), one-bar "band plunge"
(prev close > L+b, close < L — degenerate: passes for many refs/b, unnatural,
ranked last), Nth-close-count (all fail controls), late-start (below).

## 2. Reference attachments for L, ranked

Controls used (mirrored level, long side): 01-04 evening must be silent
18:02..21:05 (closes ranged 14108.25..14151.5; wave flipped short 21:06) and
01-08 Sunday must be silent 18:02..02:40 (closes 14270.0..14323.5).

**R1. original entry price + ~5 pts: L = 14708.50 + {4.75, 5.00, 5.25}
(19-21 ticks) = 14713.25/14713.50/14713.75.** Passes both controls (01-04
mirror 14124.00−4.75 = 14119.25: price stays above all evening, dips below only
21:03-21:05 and never re-crosses before the 21:06 flip — silent by 3 bars;
01-08 mirrors silent both sides). Semantics: "re-establish the flattened short
on the second dip back to within ~5 pts of the original entry."

**R2. prior day cash-session LOW + ~7 pts: L = 14706.50 + {6.75, 7.00, 7.25}.**
Passes both controls with wide margins (mirror levels far from control price
action); lowest spurious-fire count of all candidates (43 vs 127/80/291 under
always-armed). Semantics weaker (offset above a low for a short is odd).

**R3. prior full-session midpoint − ~7 pts: L = 14720.50 − {6.75, 7.00, 7.25}.**
Passes both controls; ref+offset least natural; 80 always-armed fires.

**R4 (conditional). prior session last close (= the 13:00 flatten price) + ~3.5
pts: L = 14710.00 + {3.25, 3.50, 3.75}.** Semantically the best resume anchor
("price back at/below where I was flattened, second test") but **fails the
01-04 control if armed on normal evenings** (mirror 14126.50: dip 19:58-20:02,
re-cross fires 20:03). Viable ONLY if the resume arms exclusively after an
EARLY-CLOSE session (below), which makes 01-04/01-08 out of scope.

Also-rans: late-start (BarsRequiredToTrade-style) first-breach works only for
start bar N ∈ [158,166] (= 20:39..20:47, 158-166 minutes into the session) with
L ∈ [14713.25, 14713.75+] — no natural constant lands there; ranked below all
of the above. Band-plunge family: passes controls for many (ref, band) combos
= under-constrained, kept only as a formal possibility.

## 3. WHY a resume exists only after the MLK early close

Frequency audit (`v_rlvl_freq.py`): if the resume were armed on every session
where the wave persists across the boundary (508 of 539 sessions — the state
"position existed at prior session close" is nearly always true for this
stop-and-reverse system), the surviving candidates fire 43-291 times. The
target has FEWER trades (4,351) than the no-resume INT model (5,011), so
always-armed is impossible. The arming event must be rare, and the natural one
is exactly what distinguishes 2023-01-16: **the prior session ended EARLY
(13:00 holiday close) with the wave un-flipped** — the position was force-
flattened 4 hours before the normal 17:00 close, and the system re-establishes
it after the 18:00 reopen on a confirmed second breakdown. On 01-04 the 17:00
close was a NORMAL close (and the long side never confirmed before the 21:06
flip anyway); on 01-08 the wave flipped long on the first bar, disarming any
prior-direction (short) resume immediately.

The sample has 23 early-close sessions (`v_rlvl_early.py` list). Discriminating
predictions for the following evenings (episode-2 latch, prior-direction resume;
wave persisted in every case except none — all 23 evenings are armed):
- 2023-02-20 (S): R1 fires 18:12, R2 20:49, R3 18:09-18:11, R4 18:14
- 2023-04-05 20:01 evening (L): R1 20:09, R2/R3 SILENT, R4 03:13
- 2023-04-09 Sun (S): all four SILENT (flip 18:16 ends the window)
- 2023-05-29 (S): R1 18:18-19, R2 SILENT, R3 18:11, R4 18:11
- 2023-06-19 (S): R1 SILENT, R2 18:32-56, R3 SILENT, R4 19:27
- 2023-07-03 (L): R1 00:30, R2 SILENT, R3 03:49, R4 00:37-43
- 2023-07-04 (L): R1 21:36, R2 SILENT, R3 SILENT, R4 19:43
- 2023-09-04 (S): R1 SILENT, R2 20:16, R3 mostly SILENT, R4 19:57
- 2023-11-23 (L): R1 21:07-08, R2 SILENT, R3 18:05-19:54, R4 21:07-08
- 2023-11-26 Sun (S): R1 SILENT, R2 18:34, R3 SILENT, R4 SILENT
- 2024-01-15 (S): R1 SILENT, R2 18:33-34, R3 SILENT, R4 SILENT
- 2024-02-19 (L): all SILENT; 2024-05-27 (L): all SILENT
- 2024-06-19 (L): R1/R2 SILENT, R3 18:18, R4 18:57-58
- 2024-07-03 (L): R1 21:47-48, R2/R3/R4 SILENT
- 2024-07-04 (S): R1 19:23-25, R2 SILENT, R3 18:35, R4 18:07
- 2024-09-02 (L): all SILENT; 2024-11-28 (L): only R4 18:41; 2024-12-01 Sun (L): only R4 18:05
- 2024-12-25 (L): all SILENT
- 2025-01-09 (S): R1 18:11, R2 18:15-16, R3/R4 SILENT
- 2025-01-20 (L): all SILENT
Checking the trader's cent-exact day table for extra evening trades on these
dates discriminates R1/R2/R3/R4 sharply (e.g. 2024-12-25, 2024-09-02,
2024-05-27, 2024-02-19, 2025-01-20 must show NO evening resume under all four;
2023-02-20 evening separates all four by entry time).

## 4. Bottom line

- Mechanism (unique, data-forced): decision at bar close, market fill next
  open; static level L ∈ (14713.00, 14713.75]; entry on the SECOND close-below
  episode of the evening (first breakdown 20:36-38 latched, recovery 20:39,
  re-break 20:47 → short 14712.75 @ 20:48 open).
- Level identity, ranked: R1 orig-entry+~5pt > R2 prior-cash-low+~7pt > R3
  prior-sess-mid−~7pt > R4 prior-flatten-close+~3.5pt (R4 leads on semantics
  but needs early-close-only arming to survive the 01-04 control).
- Arming: only after an early-close (holiday) session with the wave un-flipped;
  always-armed variants over-fire 43-291x and are excluded by the target's
  trade count.
- Falsified outright: every first-touch static level in the brief's list,
  VWAP any form, vendor T2 any mode/parameters, session-template variants,
  Nth-close counts, resting stop/limit order mechanics.
