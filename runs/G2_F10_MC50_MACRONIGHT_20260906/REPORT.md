# G2_F10_MC50_MACRONIGHT_20260906 — REPORT

**Card:** MC-50, macro leg only (GENESIS_II Formal Wave 4). **Ledger trial:** G00048.
**Spec:** `spec.yaml`, committed before results. **Runner:** `src/run_mc50.py` (self-contained, seed `20260906`, K=401 shifts).
**Evidence status of every number below: DISCOVERY_CONSUMED.**

## VERDICT: FAIL

The macro-night hold (long NQ 18:00 → 08:29 into NFP/CPI) shows **no release-night premium at
this scope**. The pooled difference is **negative** — release nights earned *less* than matched
same-weekday non-release nights — with p = 0.64 against the shared circular-shift null, and the
negative sign is unanimous across all three eras. Per the decision rule this writes a
FAILURE_MEMORY row at scope **"NQ overnight hold into NFP/CPI at $40.25 floor, 2006-2026-05"**
(row to be recorded serially by the coordinator; the ledger was not touched by this run).

Anti-rescue note honored: this tested the overnight window *ending at the release morning*, the
window the W2 skeptic ruled genuinely untested by GENESIS_H2; the FAIL closes the macro-night
hold at this scope and does not re-litigate H2.

## G1 semantic sentence (as printed by the program)

> The population is every NQ overnight session 18:00 ET (prior evening) -> 08:29 ET with both
> anchor bars present, session dates 2006-01-01..2026-05-29 (5070 eligible nights); events are
> the 479 NFP/CPI release nights (240 NFP, 239 CPI, 0 tagged both, counted once); controls are
> ALL same-weekday non-release nights in the same era. The event tested is the mean NET point
> P&L per night of 1 long NQ contract ($20/pt) after the $40.25 ALL_IN floor on release nights,
> minus the matched same-weekday same-era control GROSS mean — i.e. whether holding long into
> the release pays more than the ordinary night drift by more than the cost floor.

## Headline numbers

| variant | N events | D_net $/night | D_gross $/night | p (two-sided, 401 shared shifts) |
|---|---|---|---|---|
| **POOLED** | **479** | **−67.26** | **−27.01** | **0.6368** |
| NFP-only (decomposition) | 240 | −101.85 | −61.60 | 0.4627 |
| CPI-only (decomposition) | 239 | −32.51 | +7.74 | 0.9851 |

D_net = release-night net mean (gross − $40.25) minus the matched era×weekday control gross
mean; D_gross = D_net + $40.25 (identity asserted in-program). NFP-only / CPI-only are
decomposition prints, not separate chances.

**Realized N vs expectation:** 479 release nights realized vs the frozen primary's "~450
expected — adequate". Calendars carried 244 NFP + 242 CPI dates in range (union 486, overlap 0);
7 were dropped by the both-bars rule (table below).

## Gate table (program-printed; full copy in `out/gate_table.txt`)

| GATE | SPEC | OBSERVED | PASS-FAIL |
|---|---|---|---|
| G0_seal | max substrate date ≤ 2026-05-29, hard assert | max substrate timestamp = 2026-05-29 16:59:00 | PASS |
| G1_semantic | one printed sentence: population + event | printed (above) | PASS |
| G2_primary | pooled two-sided p ≤ 0.05 vs 401 shared circular shifts | D_net = −67.26 $/night, p = 0.6368 | **FAIL** |
| G3_era_stability | pooled-difference sign agrees in ≥ 2 of 3 eras | signs [−, −, −] vs pooled −; agree 3/3 | PASS |
| G4_gross_decomposition | gross vs net printed; cost-killed branch evaluated | D_gross = −27.01 (p = 0.6368), D_net = −67.26; gross does NOT pass → **not** cost-killed | PRINTED |
| G5_power | MDE@80% on any FAIL; UNDERPOWERED_STILL if MDE > 3×\|observed\| | MDE@80% = 186.13 $/night; literal 3×\|D_net\| = 201.77 → not underpowered by the literal formula; cost-invariant 3×\|departure\| = 92.13 → no-information sub-claim UNDERPOWERED_STILL, closes nothing on its own | PRINTED |

G3 passes on **sign consistency of a negative difference** — the stability is stability of the
*absence/inversion* of the premium, not of the claimed effect. The mechanism's directional claim
(Savor-Wilson-class compensation to the long holder) is contradicted in point estimate in every
era.

## Gross-vs-net split (G4)

Release-night gross mean **+$15.40**/night; net mean **−$24.85**/night; pooled control gross
mean **+$67.45**/night. The premium is negative *before* costs (D_gross = −$27.01), so the
verdict is **not** "cost-killed at the $40.25 floor" — there is no gross edge for a measured
MNQ/NQ spread update to rescue. The 2017–2022 era is the driver: release nights averaged
−$21.87 gross while ordinary matched nights drifted +$86.20 (era D_gross = −$116.51).

## Power (G5) — stated precisely

Null sd = $66.44/night (401 shared shifts); null mean of the NET statistic = −$36.55
(≈ −$40.25, as construction implies); MDE@80% = $186.13/night.

- **Literal spec formula** (|observed| = |D_net| = 67.26): 3×|observed| = 201.77 ≥ MDE → not
  UNDERPOWERED_STILL by the letter of G5.
- **Cost-invariant reading (program-printed caveat):** |D_net| embeds the constant −$40.25
  floor; the observed *information* departure from the null center is −$30.71/night, and
  MDE = 186.13 > 3×30.71 = 92.13 → the "no gross information at all" sub-claim is
  **UNDERPOWERED_STILL** and **"closes nothing on its own"**. A true gross premium of ~$100/night
  (comfortably tradeable) would have been detected with well under 80% power.

What IS closed: the *preregistered tradeable claim* — that the macro-night long pays more than
matched nights by more than the $40.25 floor — observed at −$67.26/night with a unanimous
negative era pattern over 479 events. What is NOT closed: the existence of a small (< ~$186/night
detectable at 80%) gross release-night effect of either sign.

## Exclusions table (release nights dropped by the both-bars rule)

| reason | n | dates |
|---|---|---|
| entry bar missing | 4 | 2006-01-06, 2006-02-03, 2006-12-15, 2010-07-02 |
| exit bar missing | 3 | 2006-03-10, 2006-05-17, 2013-09-17 |
| both missing | 0 | — |
| **TOTAL** | **7** | |

Across all nights (controls included): 116 entry-bar and 3 exit-bar exclusions (sparse early-era
evenings dominate). 20 of the 479 event entries were filled by a bar later than 18:01 but within
the (18:00, 18:30] window.

## Hand-checked example night (NFP, release day 2023-01-06)

Raw substrate bars (END-stamped, exchange-session ET):

- Entry bar stamped `2023-01-05 18:01:00` (covers 18:00→18:01, the session open): close **13989.00** → entry.
- Exit bar stamped `2023-01-06 08:29:00`: close **13920.00** → exit.
- Causality check in the raw tape: the 08:30-stamped bar closes 13912.50, then the bar stamped
  08:31 (covering 08:30→08:31, the release minute) spikes to a high of **14095.00** — the exit
  at the 08:29 close is strictly pre-announcement.
- Gross = (13920.00 − 13989.00) × $20 = −69.00 pts = **−$1,380.00**; net = −1380.00 − 40.25 =
  **−$1,420.25**. Matches `out/night_table.csv` row `2023-01-06` exactly (its era×weekday control
  mean, 2023–2026-05 Fridays, is −$69.63 gross).

## Named operationalizations (none silent; all program-enforced)

1. **Entry-bar tolerance.** "Bar stamped 18:01, else first available bar after 18:00" was capped
   at (18:00, 18:30]; beyond that the night is dropped as entry-missing. Justification: an
   uncapped "first bar after 18:00" could enter hours into the night and change the object; the
   cap affected 0 event nights beyond the 4 excluded (20 late-entry fills, all inside 18:30).
2. **Cost asymmetry, per the frozen primary.** "Net return on NFP/CPI nights … vs matched
   same-weekday non-release nights": the $40.25 ALL_IN floor is charged to the traded (event)
   side only; controls are the untraded drift benchmark at gross mean. Hence D_net = D_gross −
   40.25, which is what makes G4's cost-killed branch a live branch.
3. **Two-sided p is quantile-based** — p = 2·min(P(null ≥ obs), P(null ≤ obs)), obs included —
   not |stat|-around-zero. With the constant −$40.25 embedded in the net statistic, the
   |·|-around-zero form would be degenerate (null centered at −40, biased toward "significant"
   for any near-null observation of the *gross* effect). The quantile form is invariant to the
   constant, and the program asserts p(net series) ≡ p(gross series) — this is also the required
   second, independent computation of the probability event (CAP01 rule). The pooled difference
   itself is additionally recomputed by an independent per-cell weighted code path and asserted
   equal to 1e-9.
4. **G5 dual print.** The literal MDE-vs-3×|D_net| comparison is printed as specified, alongside
   the cost-invariant departure comparison (see Power section), because |D_net| embeds the
   constant floor and a power statement must be about the information effect it gates.

## Decision-rule outcome

FAIL → FAILURE_MEMORY row at scope **"NQ overnight hold into NFP/CPI at $40.25 floor,
2006-2026-05"**, with the G5 rider: the no-information sub-claim at this window is
UNDERPOWERED_STILL (MDE $186/night at 80%) and closes nothing on its own; the tradeable-premium
claim is closed. No strategy is licensed; nothing here touches any baseline or the live book.

## Outputs

- `out/gate_table.txt` — full program-printed run log incl. the gate table
- `out/night_table.csv` — 479 event nights: date, type, timestamps, prices, gross pts, gross/net $, era×weekday control mean
- `out/era_table.csv` — per-era decomposition (counts, means, diffs)
- `out/eligible_nights.csv` — all 5,070 eligible nights (audit/reproduction)
- `out/summary.json` — machine-readable summary
