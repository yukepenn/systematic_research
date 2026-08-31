# G3_P1GAP01 — RESULT: **FAIL**

**LOCKED (Mode B) challenge of `open_loc_in_on_range` as a SIZING layer on P1.**
Two arms, no grid, no variants. `spec.yaml` was committed before any arm P&L existed and was not
edited. Verdict: **A1_OPENSTRENGTH (`P1SZ_OPENLOC`) FAILS G1, G4b, G5 and G6.**

`NO ORDER PLACED · LIVE = NO · $0 · NOTHING PROMOTED, BUILT OR DEPLOYED`

---

## BASE RATE FIRST (spec §6, trap 3)

`T2_P1SIZE01` ran **two** size maps through **this identical causal budget calibrator** and both
failed on G2 and G5. This class of arm was **0 for 2** in this repository before today. It is now
**0 for 3.** The base rate was stated in the console *before* the first number was printed.

---

## 1. THE TWO GATES THE SPEC SAID TO READ FIRST

### G4b — the feature null that prices the 11-candidate scan → **FAIL**

| | |
|---|---|
| A1 fixed-DD weekly $ | **$1,311.81** |
| 1,000 circular shifts of `open_loc` across 1,187 sessions — p95 | **$1,347.59** |
| null mean / median / max | $1,225.34 / $1,238.93 / $1,446.07 |
| **A1's percentile in the shift null** | **85.4** (146 of 1,000 shifted series beat it) |

The spec named this the gate that matters most, and it is the one that answers the question:
**is it THIS feature on THESE sessions, or would any similarly-distributed session-level series have
done as well?** The answer is that **roughly one shifted series in seven does better.** A1 sits
above the middle of the null — the feature is not *nothing* — but it does not clear the 95th
percentile, and the discovery statistic (p = 0.0000 raw, p = 0.0020 vol-normalised) does not survive
the translation into money. The tail-rate gap the discovery run measured was real as a tail-rate
gap. **It does not pay.**

Note what G4b does that G4 cannot: the shifted arms are rebuilt through the *same* causal
calibrator, so each null draw also spends approximately the same extra contracts. G4b therefore
prices the exposure increase and the feature identity together. G4 does not, which is why G4 passing
here is close to vacuous (see section 4).

### G5 — stability → **FAIL**

| | observed | spec |
|---|---|---|
| rolling 24-month windows where A1 beats A0 on the risk vector | **3 / 25 = 12%** | >= 60% |
| leave-one-calendar-year-out | 4 / 5 | >= 4 / 5 |

Only three of twenty-five windows — all three clustered in **2022-08 → 2022-11** — see A1 beat A0 on
the full risk vector. Under the weaker fixed-DD-only comparator that `T2_P1SIZE01` used, it is
**2 / 25**. The reason is visible in the window table in `out/console.txt`: from 2022-12 onward A1's
maxDD is **$16,132 vs A0's $14,030 (+15.0%)** and later **$22,489 vs $21,200 (+6.1%)**, and A1's
ES95 is worse than A0's in **every single one of the 25 windows**. A1 buys its extra net by
enlarging the left tail.

---

## 2. FULL GATE TABLE (printed by the program — `out/console.txt`)

| GATE | SPEC | OBSERVED | |
|---|---|---|---|
| G0a | 2,439 trades, net to the cent | 2,439 rows, $354,575.96 vs recorded $354,575.96, abs diff = $0.000000 | **PASS** |
| G0b | size-invariance identity | max abs(pnl − qty·(pnl/qty)) = 0.000e+00; max abs(comm − 4.36·qty) = 0.000e+00 | **PASS** |
| G0c | join rate >= 95% | **2,400 / 2,400 = 100.00%**; 0 unmatched | **PASS** |
| G1 | abs(mean ratio − 1) <= 0.02 **and** abs(sum ratio − 1) <= 0.02 | mean 1.2425 / 1.2029, **d = 3.29%**; ctrRT 2,982 / 2,887, d = 3.29% | **FAIL** |
| G2 | net/wk >= A0 **and** ES95/maxDD not worse by >5% | net/wk $1,498.62 vs $1,453.06 ok; ES95 −6,025 vs floor −6,163 ok; maxDD 23,128 vs ceil 24,284 ok | PASS |
| G3 | top-decile share >= 0.80 × A0, trade count identical | 256.5% vs 254.8% (ratio 1.007); 2,400 vs 2,400 | PASS |
| G4 | > p95 of 1,000 own-size permutations | $1,311.81 vs p95 $1,003.12 (pctile 100.0) | PASS |
| **G4b** | **> p95 of 1,000 circular shifts of `open_loc`** | **$1,311.81 vs p95 $1,347.59 (pctile 85.4)** | **FAIL** |
| **G5** | **>=60% of 25 rolling 24m windows and >=4/5 LOYO** | **3/25 = 12%; LOYO 4/5** | **FAIL** |
| G6 | stationary bootstrap (4-wk block, 10,000 draws), 90% CI excludes 0 | mean diff **$45.55/wk**, **CI90 [−$21.30, +$115.40]** — includes 0. t = 1.07 *DIAGNOSTIC ONLY* | **FAIL** |

**Decision rule: ANY fail → recorded FAIL. The population is not redefined.**

---

## 3. THE ELIGIBLE-TRADE COUNT, BESIDE EVERY FIGURE

- Ledger: 2,439 trades. **39 rows dropped as SEALED** (session >= 2026-08-01, $11,653.28) — never
  read into any arm. Arm window: **2,400 trades**, net $342,922.68, 2,887 ctrRT, 236 weeks.
- **ELIGIBLE (entry >= 09:30): 875 = 36.5% of the book**, carrying $166,360 = 48.5% of A0's net.
  The spec's advance estimate was "~43% of trades"; the realised figure is **36.5%**, so the ceiling
  is *tighter* than preregistered, not looser.
- **Sizes actually changed on 95 trades = 4.0% of the book, 10.9% of the eligible set.**
- Book-level A1 − A0 = **+$10,750.80 over 236 weeks = +$45.55/week**, on **95 extra contract round
  turns**.

The effect is small, which is the *right* size for a layer that can touch 4% of trades. Per the
spec's trap 4, a large book-level effect here would have been evidence of a bug. There is no such
evidence — the arithmetic is internally consistent (+$10,751 / 95 extra contracts = **+$113 per
extra contract round turn**, a plausible per-contract number, not an impossible one).

---

## 4. A1 − A0 IN $/WEEK ON ALL THREE COST LINES

| extra $/ctrRT | A0 net/wk | A1 net/wk | **A1 − A0 /wk** | A0 fixDD wk | A1 fixDD wk | A1 − A0 fixDD |
|---|---|---|---|---|---|---|
| **+$0.00** (NT8 $4.36 basis, primary) | $1,453.06 | $1,498.62 | **+$45.55** | $1,271.93 | $1,311.81 | +$39.88 |
| +$14.44 modelled spread | $1,276.42 | $1,316.16 | **+$39.74** | $1,029.86 | $1,061.93 | +$32.06 |
| +$20.65 modelled spread | $1,200.45 | $1,237.69 | **+$37.24** | $937.03 | $966.10 | +$29.07 |

All three lines agree in sign (positive). **They agree on a quantity that G6 cannot distinguish from
zero and that G1 says was not bought with a matched budget.** The sign agreement is therefore not
evidence for the arm; it only says the small positive difference is not a cost artefact.

**G4 is nearly vacuous and should not be quoted as support.** Its null (permute A1's size labels
across all 2,400 trades) destroys the *incumbent's* sizing as well as the feature's, so its mean
collapses to $754.16. Passing it at percentile 100.0 mostly re-confirms that P1's certified quality
score is informative — a fact established in W42/W83 — and says almost nothing about `open_loc`.
The spec anticipated exactly this, which is why G4b exists.

---

## 5. BY CALENDAR YEAR — the direction tilt the spec warned about (trap 5)

| year | n | eligible | A0 net | A1 net | **A1 − A0** | A1−A0 $/wk | A0 ctr | A1 ctr | sizes changed | $ per extra ctr |
|---|---|---|---|---|---|---|---|---|---|---|
| 2022 | 487 | 185 | $44,755 | $44,390 | **−$366** | −$7 | 586 | 593 | 7 | −$52 |
| 2023 | 582 | 256 | $40,370 | $37,332 | **−$3,039** | −$60 | 696 | 729 | 33 | −$92 |
| 2024 | 628 | 210 | $104,889 | $110,098 | **+$5,208** | +$100 | 757 | 793 | 36 | +$145 |
| 2025 | 457 | 143 | $111,331 | $117,352 | **+$6,021** | +$114 | 557 | 566 | 9 | +$669 |
| 2026 | 246 | 81 | $41,576 | $44,503 | **+$2,926** | +$94 | 291 | 301 | 10 | +$293 |
| **ALL** | **2,400** | **875** | **$342,923** | **$353,673** | **+$10,751** | **+$46** | **2,887** | **2,982** | **95** | **+$113** |

**The entire gain is 2024–2026 and the sign is negative in both 2022 and 2023.** P1 is long-only and
`open_loc` is a directional/momentum quantity; 2022 was a bear year and 2024–2025 were strong bull
years. The per-extra-contract column flips sign at exactly that boundary (−$52, −$92 → +$145, +$669,
+$293). This is what a **market-direction tilt** looks like, not what an excursion-magnitude
forecast looks like. It is also why G5's rolling windows collapse: every window that overlaps 2022
loses, and the three windows that win are the three that end inside the 2022 bear market itself.

$6,021 of the 2025 gain arrives on **9 changed sizes**. That is not a distribution; it is a handful
of trades.

---

## 6. WHY G1 FAILED, AND WHY IT WAS NOT PATCHED

The spec's A1 rule is *"s = 2 when `open_loc` >= tau_i, **else the incumbent size**"*, and section 3's
`what_it_does_NOT_do` says *"it never reduces a size below the incumbent's."* Read together those
clauses define a **UNION**, not a replacement: A1 >= A0 pointwise. Section 3 separately asserts the
budget is *"matched BY CONSTRUCTION"* — that assertion is only true under a *replacement* rule, where
the feature's (1 − r) quantile hands back exactly the incumbent's size-2 rate. **Under the union the
two size-2 sets add rather than substitute, so the budget cannot be matched by construction.** G1
measures it and G1 fails:

- feature-selected on eligible: **177 / 875 = 20.2%** (calibrator target mean r = 0.2175 — the
  calibrator did its job)
- incumbent size-2 on eligible: **196 / 875 = 22.4%**
- overlap: **82 of the 177** (46.3%; 39.6 expected if independent, a real 2.07x lift, so `open_loc`
  and the certified quality score *are* positively dependent — but not enough to coincide)
- union: **291**, i.e. **+95 contracts = +3.29%**, against a 2.00% tolerance.

I implemented the rule **as written** and did not resolve the tension in the arm's favour. Changing
"else the incumbent size" to "else 1" would have matched the budget and would also have been an edit
to a locked spec after seeing that G1 failed. That is the parameter rescue section 37 rejects.

**The consequence for G2 must be stated plainly: G2 passed on a 3.29% larger contract budget.** A1's
+$45.55/week was bought with 95 extra contract round turns. Under this spec's own doctrine that is
**LEVERAGE, not information**, and the G2 pass is not quotable as evidence of edge. G4b — which
rebuilds each null through the same calibrator and so spends the same extra contracts — is the
comparison that controls for it, and A1 loses it.

---

## 7. CLASSIFICATION AND CLOSURE

- **Type: MECHANISM-POLICY / RISK SPECIFICATION (Type B)**, as preregistered. Not new alpha, and it
  is not described as such under any reading of this result.
- **Evidence status: DISCOVERY_CONSUMED.** 2026-05-31 → 2026-07-31 was already DIRECTLY_BURNED.
- **`open_loc_in_on_range` is CLOSED as a P1 sizing layer at this formulation.** Per spec section 6
  trap 2 and the prohibitions block, **`gap`, `open_vs_on_high` and `gap_frac_of_prior_range` are
  NOT now tried.** The four survivors were four measurements of one factor; the factor was tested
  once, at the formulation chosen in advance on three stated non-outcome properties, and it did not
  pay. Trying the runner-up because the chosen one failed is the parameter rescue section 37
  rejects, and it is prohibited in this run *and in any successor*.
- What is **not** closed: nothing here says `open_loc` fails to mark P1's right tail. The discovery
  statistic stands. What is closed is that **marking the tail at this strength does not survive
  translation into a sized, budget-matched, cost-charged, era-stable dollar edge.**

---

## 8. METHOD NOTES — decisions made before results, and one honest deviation

1. **Week index.** Weeks are ISO weeks of the **session date** (18:00→17:00), `champion_eval`'s
   documented convention and the join key the spec mandates. The ledger's own `wk` column keys on
   the *entry calendar date* and differs on **178** Sunday-evening trades. Both arms share one
   index, so no gate can turn on the choice; it was fixed before any arm P&L was computed.
2. **G6 primary = the RAW weekly difference**, the literal spec text. The fixed-DD-rescaled variant
   is printed as a labelled diagnostic and **also includes zero**: mean $39.88/wk,
   CI90 [−$20.20, +$99.96]. The verdict does not depend on the choice.
3. **G5's "beats on the risk vector"** was defined as the G2 criterion with a strict `>` on the
   return leg. The weaker fixed-DD-only comparator is printed alongside and is *worse* (2/25).
4. **Deviation, recorded not hidden.** Section 6 above is a reading of an internal tension in the
   locked spec (union vs. "matched by construction"). I resolved it toward the *literal rule text*
   plus the explicit "never reduces a size" clause, and recorded the resulting G1 failure rather
   than the interpretation that would have passed. No second arm was run.
5. Every number in this report is printed by `src/g3_p1gap01.py` into `out/console.txt` and
   `out/gates.json`. No figure was assembled by hand. `research_sdk/champion_eval.py` (selftest
   30/30) supplied the risk vector, the fixed-DD algebra, the ES95/maxDD primitives and the
   Politis-Romano stationary bootstrap; it was imported, never modified.
6. Seal held: the session substrate carries **0 sealed rows**, and the 39 ledger rows with a session
   >= 2026-08-01 were dropped and counted before any arm existed.

---

## ARTIFACTS

`src/g3_p1gap01.py` · `out/console.txt` · `out/gates.json` · `out/arm_ledger.csv` (2,400 rows: per-trade
`open_loc`, `tau`, `r_incumbent`, `qty_A0`, `qty_A1`, `pnl_A0`, `pnl_A1`, `delta`)
