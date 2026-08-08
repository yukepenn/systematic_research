# W8-3 — A-EXIT: patient execution on Solar's time-triggered exits (readout)

Spec: `specs/W8_programs_final.md` §W8-3 (frozen, committed cf7041f). DR-E R1, Arms A+B.
Code: `src/python/w8_aexit.py`. Seed 20260808, 1000 reps, day-clustered (session-resampled)
bootstrap CIs. Every number below appears in `stdout.txt` / `w8aexit_orders.csv` /
`w8aexit_summary.csv` in this directory. No data at or after 2026-06-01 was read
(fills truncated at load; newest substrate session is s20260520).

## Headline

- **Arm A (16:4x flatten exits): VERDICT = CLOSE THE PASSIVE TRACK** under the frozen rule
  (adopt-for-ops iff CI_lo > 0). No W has CI_lo > 0:
  W=30 mean +0.000t CI[−2.750, +3.131]; W=60 mean +2.290t CI[−1.549, +5.670];
  W=120 mean +3.452t CI[−0.521, +7.068]. Point estimates at W=60/120 are *above* the
  frozen expectation (+0.5–1t/exit) but the sample (31 orders / 30 sessions) cannot
  separate them from zero against per-order dispersion of −41t…+61t.
- **Arm B (signal entries): frozen expectation "≤ 0" is CONSISTENT with the data**
  (in-sample characterization): mean saving is negative at every W
  (−0.592t / −1.114t / −0.767t for W=5/30/60), never significantly positive, and the
  misses are catastrophic exactly as the momentum-non-fill mechanism predicts
  (mean miss −7.7t at W=5 worsening to −26.0t at W=60). No patient variant is adoptable
  for entries.

## 1. Data (FACT)

- Fills: `runs/E10MASTER_V2/out/e10m_v2_fills.csv` (skiprows=1), 39,777 rows raw,
  38,320 kept after the hard `< 2026-06-01` truncation. All fills are minute-stamped
  (seconds == :00 verified). One fill stamped exactly 17:00 (session-close boundary,
  2023, outside the substrate) — documented, harmless.
- Substrate: sechilo 37 sessions ∩ grid1s 40 sessions = **37 discovery sessions**
  (s20250814 … s20260520). Fills landing on them: 1,252 across all 37.
- Session mapping: session tag = END date; fills with hour ≥ 18 map to the next
  calendar day's tag (18:00→17:00 ET sessions).
- **Arm A sample**: 31 exit fills (order_action Sell/BuyToCover, minutes 16:42–16:45)
  on 30 sessions — 30 stamped 16:45, 1 stamped 16:42 (s20260520 carries a 16:42 partial
  flatten plus the 16:45 flatten). 7 of 37 sessions were already flat at 16:4x.
- **Arm B sample**: 632 entry fills (Buy/SellShort outside 16:42–16:45; names all S/L)
  on all 37 sessions. Zero Buy/SellShort fills inside the 16:4x window needed excluding.
- Same-minute grouping (frozen: one order per minute, qty summed): merged 0 multi-fill
  minutes — 31 and 632 orders stand. Order qty is in MNQ units (Arm A 1–9, Arm B 1–5).
- Simulated order×W rows: 1,989 (31×3 + 632×3); 0 dropped for missing quote state;
  6 legs used the last-prior-second quote (grid asof fallback).

## 2. Mechanics as implemented (documented conventions)

- **Minute-stamp convention (mandated documentation)**: fills are minute-stamped, so the
  fill minute's :00 second is taken as the reference second T. For the flatten exits this
  anchors the template at 16:45:00 (the fills carry the END stamp of the 16:44-flatten
  3-min bar; the spec's worked anchor "16:44:00" was written pre-readout — the mechanics
  are identical, anchored at the actual fill minute).
- Baseline = market cross at T from grid1s (sell→bid(T), buy→ask(T)). grid1s bid/ask are
  PRICES; per-second state is the last quote in the second, forward-filled (causal
  end-of-second state per `build_grid1s.py`). Price deltas are converted to NQ ticks
  by /0.25.
- Arm A: patient limit posted at post = T−W (W ∈ {30,60,120}s) at the posting second's
  opposite touch (sell→ask(post), buy→bid(post)); deadline D = T+59 (the fill minute's
  :59; spec: "before 16:44:59").
- Arm B: marketable-limit posted at post = T at the opposite touch; patience W ∈ {5,30,60}s;
  deadline D = T+W.
- Fill condition (house trade-through convention): filled iff sechilo mid — which is in
  TICKS (= price×4) — crosses THROUGH the limit by ≥ 1 tick in seconds [post+1, D−1]
  inclusive (posting second excluded because the grid state is end-of-second; deadline
  second excluded because it is the forced-cross second). Sell limit L: mid_high ≥ L×4+1;
  buy limit L: mid_low ≤ L×4−1. Sechilo is sparse (event seconds only); absent seconds
  cannot fill.
- Unfilled → forced cross at D's touch (sell→bid(D), buy→ask(D)).
- Saving (NQ ticks, + = patient better): sell (realized−baseline)/0.25;
  buy (baseline−realized)/0.25. Dollars: ticks × qty × $0.50/MNQ-tick.
- Three orders were independently re-derived from the raw parquets during review and
  match the pipeline exactly (s20250820 W=30 −6.0t forced / W=60 +12.0t filled;
  s20250814 Arm B 19:48 W=30 −6.0t forced).

## 3. Arm A — time-triggered flatten exits [IN-SAMPLE CHARACTERIZATION, n=31 orders / 30 sessions]

| W (s) | n | fill rate | mean saving (t/order) | 95% CI (day-clustered) | qty-wtd mean (t) | total $ | n miss | miss mean (t) | miss qty-wtd (t) | miss $ | q05/q25/q50/q75/q95 (t) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 30 | 31 | 0.806 | +0.000 | [−2.750, +3.131] | +0.683 | +$34.50 | 6 | +0.000 | −1.238 | −$13.00 | −9.5 / −4.5 / −1.0 / +4.0 / +16.5 |
| 60 | 31 | 0.839 | +2.290 | [−1.549, +5.670] | +2.149 | +$108.50 | 5 | +0.400 | +0.154 | +$1.00 | −25.5 / −1.5 / +2.0 / +9.5 / +17.5 |
| 120 | 31 | 0.806 | +3.452 | [−0.521, +7.068] | +5.416 | +$273.50 | 6 | +1.167 | +0.923 | +$6.00 | −20.5 / −1.0 / +6.0 / +9.5 / +23.0 |

- The P&L-weighted (qty-weighted) miss cost is mild for Arm A: misses at the deadline
  cross re-price by only −1.2t (W=30) to +0.9t (W=120) qty-weighted — a time-triggered
  exit into the 16:45 minute faces no momentum adverse selection on average.
- What drives the dispersion is not spread capture but drift between T−W and T: the limit
  is posted at the touch W seconds early, so the patient exit effectively trades W seconds
  ahead of the flatten (best +61t on s20260520 16:45 W=60; worst −41t on the s20260520
  16:42 partial, −30t on s20260206 W=60). Per-order detail for all 93 rows is printed in
  `stdout.txt` and stored in `w8aexit_orders.csv`.
- INFERENCE: with ~11–14t per-order sigma and n=31, a true +0.5–1t/exit effect (the frozen
  expectation) is far below detectability here; even the observed +2.3 to +3.5t point
  estimates do not clear a day-clustered CI. The dollar upside at point estimate is also
  small (≤ ~$9/session at current MNQ sizing).

**FROZEN VERDICT RULE applied (FACT): no W has CI_lo > 0 → NOT adopt-for-ops; the passive
(patient-exit) track CLOSES.**

## 4. Arm B — signal entries [IN-SAMPLE CHARACTERIZATION, n=632 orders / 37 sessions]

| W (s) | n | fill rate | mean saving (t/order) | 95% CI (day-clustered) | qty-wtd mean (t) | total $ | n miss | miss mean (t) | miss qty-wtd (t) | miss $ | q05/q25/q50/q75/q95 (t) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 5 | 632 | 0.650 | −0.592 | [−1.341, +0.153] | −0.233 | −$90.50 | 221 | −7.706 | −7.681 | −$975.50 | −17.0 / −1.0 / +2.0 / +3.0 / +6.0 |
| 30 | 632 | 0.824 | −1.114 | [−2.299, +0.082] | −0.683 | −$265.50 | 111 | −22.099 | −22.512 | −$1,407.00 | −26.8 / +2.0 / +3.0 / +4.0 / +6.0 |
| 60 | 632 | 0.859 | −0.767 | [−2.025, +0.532] | −0.290 | −$112.50 | 89 | −25.966 | −26.724 | −$1,309.50 | −22.5 / +2.0 / +3.0 / +4.0 / +6.0 |

- The mechanism is exactly the frozen expectation: fills harvest ~the spread (median +2
  to +3t) but the 14–35% of orders that never fill are the ones where price ran — the
  P&L-weighted miss cost grows monotonically with patience (−7.7t → −22.5t → −26.7t
  qty-weighted) and swamps the spread capture at every W.
- Secondary side split (in `stdout.txt`): SellShort entries are significantly *negative*
  at all W (e.g., W=30: −2.174t CI[−3.921, −0.472]); Buy entries are pointwise positive
  but never significant (W=60: +1.070t CI[−0.167, +2.245]). No adoptable variant; any
  buy-side-only idea would be post-hoc and is not pursued (falsified-axes discipline).

## 5. Worked examples (FACT — full detail in `stdout.txt`)

1. **EX1 filled exit** — s20250814, BuyToCover 3 MNQ stamped 16:45:00. T=16:45:00;
   posted 16:44:00 at bid 23885.00 (95,540 sechilo ticks; needs mid ≤ 95,539t);
   sechilo traded through at 16:44:08 → realized 23885.00 vs baseline ask(T) 23885.75
   → **+3.0t (+$4.50)**.
2. **EX2 unfilled exit (benign miss)** — s20250902, Sell 4 MNQ stamped 16:45:00.
   Posted 16:44:00 at ask 23438.25 (needs mid ≥ 93,754t); never traded through by
   16:45:59 → forced cross at deadline bid 23437.50 = baseline bid(T) 23437.50
   → **0.0t ($0.00)**.
3. **EX3 unfilled entry (momentum miss)** — s20250814 session, Buy 1 MNQ stamped
   2025-08-13 19:48:00, W=30. Posted at bid 23951.50 (needs mid ≤ 95,805t); min sechilo
   mid_low in window 95,806.5 → no fill; forced cross at 19:48:30 ask 23953.75 vs
   baseline ask(T) 23952.25 → **−6.0t (−$3.00)** — price walked away, the classic
   momentum non-fill.

## 6. Verdict and disposition

- **Arm A: CLOSE THE PASSIVE TRACK** (frozen rule: CI_lo ≤ 0 at every W). FACT.
- **Arm B: consistent with the frozen "≤ 0" expectation; nothing adoptable.** IN-SAMPLE
  CHARACTERIZATION.
- INFERENCE (not a verdict): the Arm A point estimates (+2.3 to +3.5t at W=60/120) leave
  the door open that a real but small saving exists; detecting it would need on the order
  of 10× more flatten exits with substrate coverage. If the tick-substrate library grows
  materially (e.g., post SWScalpTickExport_v2), a re-run of this exact frozen template is
  the cheap follow-up. No new spec is opened now; the track closes per the frozen rule.
