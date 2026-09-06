# G3_CLROLLCONG_20260906 — GSCI roll congestion, the Goldman roll (G00094, family GENESIS3_RV)

**Verdict: CLOSED-AS-COMPETED-AWAY (permanent). G1 PASS · G2 FAIL · G3 PASS-AS-PRINTED · G4 FAIL ·
G5 PASS — the mechanical decision rule (`G2+G4 both fail -> CLOSED-AS-COMPETED-AWAY`) fired,
delivering the card's own expected, bankable outcome.** The congestion premium the folklore family
predicts — the F1-F2 calendar spread paid to a LONG-back/SHORT-front position through business
days 5-9 of the month — does not exist in CL at daily-close granularity from 2009 onward: pooled
gross **+0.047 pt = +$47/month-trade**, indistinguishable from random circularly-shifted window
placements (**p 0.2913** over 1,307 shifts; normal-tail cross-check z +0.63, p 0.26), **+$7/month
after conservative cost** with a bootstrap CI spanning zero, and only **47.5% of months positive
gross** — a coin flip. The impaired-arb conditional, the only revival path, also fails.

Evidence status of every number in this report: **DISCOVERY** (first read of this representation;
consumed by this read). Wave 7 world-scan card #19. Program: `src/clrollcong.py`; full
program-printed output in `out/gate_table.txt` (= `run_stdout.txt`).

## The mechanism and the frozen object

The S&P GSCI (and BCOM-family) indices roll front→back on business days 5-9 of each month — once
a large, documented effect ("the Goldman roll"), then arbitraged away post-~2010. Frozen object:
CL primary (GC/SI reported where pairable); per calendar month M, F1 = delivery M+1, F2 = delivery
M+2 (exactly GSCI's CL schedule); business days realized on F1's own trading calendar; entry close
bd4, exit close bd9; R = ΔS in POINTS with S = F2 − F1; R > 0 = congestion-trade profit.
Per-contract day store via `ncd_day.py` (unmerged path; sha256
`17603bdc722d30f386b013d35a33f8b2cb510d8b7ea6fdbc07f0274bf01baec9`), both legs required
simultaneously. Twelve frozen-interpretation notes (I1-I12) recorded in the program header before
any result was computed. GC pairing cycle [2,4,6,8,12] (October: not an index month, and the
store's `GC 10-*` directories are empty); SI [3,5,7,9,12]. RNG seed 20260906, 10,000 bootstrap
draws, month = block unit.

## Pairing coverage (measured honestly, as tasked — the TSYROLL-style store gaps, only worse)

- **CL census 211 months (2009-01..2026-07); usable for the primary 80** (span 2009-04..2015-11).
  3 months lose F1 entirely (empty 2009 dirs); **128 months lose the F2 window**.
- The loss is **systematic, not random, and it beheads the modern era**: every CL contract with
  delivery **≥ 2016-02** carries only ~its final 22 rows (the month before its LTD). The F2 leg
  (delivery M+2) is therefore born ~day 16-18 of month M and **can never overlap business days
  5-9**. No CL calendar spread is measurable in the first half of ANY month after 2016-01 in this
  store. Data absence, not market absence — itemized per month in `out/monthly_panel.csv`.
- GC/SI are far less truncated: **GC 142/211 usable, SI 154/211, both spanning 2009-04..2026-07**
  — they carry the era-3 read that CL cannot.
- Consequence disclosed up front: the CL decay curve is store-truncated at 2015-11, the CL era-3
  cell is EMPTY, and the 2020 negative-price episode (the canonical impaired-arb month) is not in
  the CL panel.

## Gate-by-gate (all cells; program-printed table in `out/gate_table.txt`)

**G1 MDE first (PASS):** printed before any observed mean. Monthly window-return sd 0.2775 pt →
**MDE (one-sided 5%, 80% power) = 0.0771 pt = $77/month-trade** at N=80 (census 211; shortfall is
data absence, itemized).

**G2 pooled vs circular-shift null (FAIL):** pooled gross **+0.04713 pt = +$47.13**; after-cost
CONS **+0.00713 pt = +$7.13** (clause A technically positive); month-bootstrap 95% CI
[−0.0497, +0.0725] pt straddles zero; share>0 gross 47.5%, net-cons 38.8%. Shift null (in words:
the probability that a circularly-shifted placement of the 5-day window over the same daily
spread-change series yields pooled drift ≥ the observed bd5-9 placement): **p_1s = 0.2913** over
1,307 exhaustive shifts (placebo mean +0.0057, sd 0.0658 pt); second computation via the placebo
distribution's normal tail: z +0.629, p 0.2647 — the two agree. The flagged-day construction
T0 = +0.04713 equals the per-month pooled mean (same event two ways). Clause B fails → **G2 FAIL**.

**G3 era thirds (PASS-AS-PRINTED) — the decay read, the deliverable:**

| root | era | n | gross pt | net-cons pt | 95% CI (net-cons) | share>0 |
|---|---|---|---|---|---|---|
| CL | 2009-14 | 69 | +0.0335 | −0.0065 | [−0.0713, +0.0671] | 43.5% |
| CL | 2015-20 | 11 | +0.1327 | +0.0927 | [+0.0118, +0.1691] | 72.7% |
| CL | 2021-26 | 0 | — | — | EMPTY (store-limited) | — |
| GC | 2009-14 | 67 | +0.0866 | −0.3134 | [−0.4746, −0.1343] | 56.7% |
| GC | 2015-20 | 39 | +0.3846 | −0.0154 | [−0.3436, +0.4256] | 61.5% |
| GC | 2021-26 | 36 | +0.4306 | +0.0306 | [−0.2056, +0.2945] | 63.9% |
| SI | 2009-14 | 67 | +0.0075 | −0.0125 | [−0.0264, +0.0018] | 55.2% |
| SI | 2015-20 | 44 | −0.0003 | −0.0203 | [−0.0310, −0.0089] | 43.2% |
| SI | 2021-26 | 43 | +0.0084 | −0.0116 | [−0.0206, −0.0021] | 55.8% |

The decay curve's honest shape: **there was nothing left to decay by 2009.** CL 2009-14 is flat
gross (+0.033 pt vs MDE 0.077) and negative after cost; SI is gross-flat in all three eras; GC
gross actually RISES across eras (+0.087 → +0.385 → +0.431 pt — anti-decay) but never clears its
own cost rung with a CI (cons $40 = 0.4 pt; era-3 CI spans zero). Supplementary non-gating reads:
CL equal-n thirds (2009-04..2011-06 / 2011-07..2013-09 / 2013-10..2015-11) print gross
+0.083 / −0.032 / +0.092 pt — noise around zero, no monotone structure; GC/SI actual-roll-months-
only subsets show the same cost-dead picture (`out/era_thirds.csv`).

**G4 impaired-arb conditional (FAIL):** vol20 (trailing-20-close log-return sd of the F1 outright
at bd4) valid for 79/80 months; full-sample tercile cuts q33 0.0135 / q67 0.0195. **TOP
(impaired-arb) n=27: net-cons +0.0037 pt, CI [−0.0522, +0.0593]; REST n=52: −0.0054 pt; matched
unconditional control n=79: −0.0023 pt** (printed in the same table, same wave). Delta (TOP−REST)
**+0.0091 pt, bootstrap 95% CI [−0.0928, +0.1065]** — clause B fails → **G4 FAIL**. The only
revival path is closed at this representation; note it could only ever have spoken for 2009-15
(store truncation), and the 2020 episode is absent.

**G5 cost (PASS):** MODELED, SPREAD_ONLY, {1,2}-tick band per leg per RT, 2 legs × 1 RT per
month-trade: CL $20/$40 (0.02/0.04 pt), GC $20/$40 (0.2/0.4 pt), SI $50/$100 (0.01/0.02 pt); cons
rung gates every net figure. COMMISSION_ONLY info, non-gating: 2 × $4.36 = $8.72. Tick headers
asserted == declared on every loaded contract (CL 209 @ 0.01, GC 89 @ 0.1, SI 89 @ 0.005).

**Decision (mechanical):** G2 FAIL and G4 FAIL → **CLOSED-AS-COMPETED-AWAY, permanent.**

## What this means (attribution, no promotion)

1. **The Goldman-roll congestion premium is absent from the start of this sample.** The
   literature's effect died ~2010; at daily-close granularity 2009-14 CL already shows nothing
   (gross +$33/month, 43.5% positive), so this run measures the corpse, not the decay — and that
   is the bankable read: the folklore family retires.
2. **Cost dominates whatever residue exists.** Gross +$47/month vs a conservative $40 spread bill
   +$8.72 commission; held every usable month the trade nets ~$86/yr per 1-lot spread — and the
   placement is statistically indistinguishable from any other week of the month (p 0.29).
3. **The impaired-arb story finds no support where it can be tested** (2009-15 vol terciles,
   delta CI dead-center on zero), and cannot be tested where it would bite hardest (2020) in this
   store.

## §28 closure block

```
Closed:  observable = per-contract CL (GC/SI secondary) day-store F1-F2 calendar spreads
  (ncd_day.py, contract-id keyed, unmerged path, both legs required simultaneously)
representation = monthly GSCI roll window: F1=delivery M+1, F2=M+2 (CL); business days from F1's
  own calendar; LONG back / SHORT front held close(bd4) -> close(bd9), POINTS
event = index roll congestion, business days 5-9 of every month     horizon = 5 trading days
target = calendar-spread drift paid by predictable index roll flow ("the Goldman roll")
conditional = trailing-20d vol tercile of the F1 outright (impaired-arb cell) with matched
  unconditional control
execution = MODELED {1,2}-tick per-leg band (SPREAD_ONLY), cons rung gates; commission info $8.72
sample = CL months 2009-04..2015-11, 80/211 census usable (systematic store truncation post
  2016-01 itemized: final-month-only contracts make F2 unobservable in bd5-9); GC 142, SI 154
  months through 2026-07; MDE $77/month
reason = COMPETED-AWAY / NULL AT ARRIVAL: pooled gross +$47/mo indistinguishable from shifted
  window placements (p 0.291, 1307 shifts; z-cross-check agrees); net-cons +$7/mo, CI spans 0;
  47.5% of months positive. Era read: CL 2009-14 flat, SI flat all eras, GC gross anti-decay but
  cost-swamped in all eras. Impaired-arb cell delta +0.009 pt CI [-0.093,+0.107] -> G4 FAIL.
  G2+G4 both fail -> mechanical closure, the card's own expected outcome.
```

Adjacent-open (not leads): (a) CL 2016+ at this representation needs per-contract daily data the
store does not hold (every post-2016-01 contract is final-month-only) — an external daily source
would reopen the era-3 cell, including the 2020 negative-price impaired-arb episode; (b) the
CL 2015-only cell (n=11, net-cons CI [+0.012, +0.169], the oil-glut storage-congestion year) is a
disclosed anomaly, multiplicity-unadjusted, unconfirmed by the frozen G4 path — it would need a
pre-registered storage-constraint conditional on new data before it is anything; (c) intraday
roll-window microstructure — no local intraday energy data at $0.

## Anomalies / disclosures

- **The CL store truncation is the run's biggest fact after the verdict itself**: 128/211 months
  unpairable because every CL contract with delivery ≥ 2016-02 carries only its final ~22 rows.
  Same failure family TSYROLL documented on ZN/ZB (their 2016/2019/2022/2025 truncations), but
  here it is every year from 2016 — the era-thirds deliverable is CL-truncated at 2015-11 and
  era 3 is carried by the GC/SI secondaries.
- **CL era2 (=2015 only, n=11) prints net-cons CI [+0.012, +0.169] excluding zero** — 8/11 months
  positive in the oil-glut year. Non-gating, 1 of 9 era cells, DISCOVERY, in-sample; 7 of its 11
  months sit inside the TOP vol tercile, which still fails G4. Recorded as adjacent-open above.
- GC absurd-spread screen fired on 2025-07 and 2026-07; investigated: **real** Aug→Dec gold carry
  (S(bd4) = $55.1 and $57.5 at gold $3,346.5 / $4,051.8) — a rates-driven contango level, not a
  data defect. Merged-path contamination screen (identical F1/F2 volumes): 0 hits on all roots.
- Telescoping identity asserted on every usable month (endpoint R == sum of the 5 daily ΔS);
  seal asserted (max date used 2026-07-31 < 2026-08-01); one benign floating-point zero
  (CL 2015-10 gross −4e-14).
- Frozen-interpretation notes I1-I12 (pair rule, window rule, validity, null construction, gate
  clauses, vol rule, eras, cost, seal, RNG, identity gates, decision rule) were written into the
  program header before any result was computed; the spec's unnamed "G2 PASS" branch was never
  needed.
- The G2 p-value's event is stated in words and computed two independent ways (shift rank 0.2913,
  placebo-normal tail 0.2647) per the CAP01 rule — both agree.
- REPORT.md was not written by this pod (harness rule on report files, per TSYROLL precedent, not
  tunneled around); this document is returned in the structured output for the orchestrator to
  place at `runs/G3_CLROLLCONG_20260906/REPORT.md`.

## Outputs

- `out/gate_table.txt` — full program output incl. GATE/SPEC/OBSERVED/PASS-FAIL table (= `run_stdout.txt`)
- `out/monthly_panel.csv` — 633 root-months: pair ids, status (gap anatomy), window dates, R gross/net rungs, vol20, tercile inputs, era, identity flags
- `out/era_thirds.csv` — frozen eras × roots + supplementary CL thirds and GC/SI roll-month tables
- `out/verdicts.json` — machine-readable gates, headline numbers, decision
- `src/clrollcong.py` — the frozen program (interpretation notes I1-I12 in header)
- `run_stdout.txt`, `run_stderr.txt`