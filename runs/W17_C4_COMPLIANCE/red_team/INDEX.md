# Wave-17 red team — index and ingested corrections

Four independent adversarial reviews, one per companion analysis, each instructed to try to
**break** the work rather than confirm it. Full verdicts in this directory, verbatim, unedited.
Per C6, corrections live here and in the run REPORTs — **never** in a frozen `spec.yaml`.

| analysis | verdict | material defects |
|---|---|---|
| V4/V4a friction ledger | **CONFIRMED-WITH-CORRECTIONS** | 7 (2 headline-affecting, 1 real code bug) |
| O1/O1a primary objective | **CONFIRMED-WITH-CORRECTIONS** | 15 (2 headline-flipping) |
| V1f event-day margin | **CONFIRMED-WITH-CORRECTIONS** | 12 (1 conditional-conclusion, 1 contaminated artifact) |
| V1d closure | **CONFIRMED-WITH-CORRECTIONS** | 12 (all disclosure/method; verdict unchanged) |

No verdict was REFUTED, and no headline compliance result (the C4 audit, the flatten fixes,
the 0-breach outcomes) was challenged — those were measured by the orchestrator on NT8's own
execution ledgers and were outside these four agents' scope.

---

## Corrections ingested, in order of how much they change what a reader should believe

### 1. **The "2026 edge collapse" narrative is statistically unsupported. Retracted.**
*(V4 red team D1/D2 — the single most important correction of this wave.)*

`V4_FRICTION.md` §5 and my own `reports/OWNER_STATUS.html` presented BEST_ONE_NQ's 2026 partial
year (net **−$46.60**, 106 sessions) as the disclosure to look at hardest, framed as the gross
edge falling to the friction floor. The red team's independent test:

- Per-trade gross, ticks/RT, mean ± 1.96·SE: 2022 **52.80 ± 55.59**, 2023 12.65 ± 31.99,
  2024 33.73 ± 46.46, 2025 40.37 ± 69.90, 2026 **0.82 ± 100.50**.
  **Not one yearly mean is individually distinguishable from zero.** Welch 2022-vs-2026:
  t = **0.89**. The "collapse" sits entirely inside trade-level noise.
- The −$46.60 headline is **0.0010 SE from zero** (185 trades, per-trade sd $3,487,
  SE(sum) ≈ $47,428). Drop the single best trade → −$13,307. Drop the single worst →
  **+$6,623**. The sign is decided by one trade in 185.
- The report carried **no** uncertainty quantification on this claim, despite
  `src/analytics/trials.py` existing for exactly that.

**Ingested:** the collapse claim is withdrawn. What survives is the descriptive fact that the
2026 partial slice is small and near zero, and that at the coded commission rate its breakeven
multiple is 0.94× — which is a statement about that slice's arithmetic, not evidence of decay.
`OWNER_STATUS.html` has been corrected.

### 2. **Selective silence: 45 excluded sessions run opposite to the narrative.**
*(V4 D3.)* Product A's fill ledger extends past the dev window: **2026-06-01..2026-07-31,
45 sessions, net +$34,997.10** ($777.71/session vs the dev average $155.67). Excluding them
from a dev-window ledger is correct discipline; reporting the exclusion **without the
magnitude**, while arguing "2026 is where the edge met the friction floor," is not.
Disclosed here. Caveats that must travel with it: n = 45 is far too short for any magnitude
claim (Sharpe SE ≈ 2.4), and per `LOCKED_FORWARD.md` June/July 2026 is research-CONSUMED, so
it is **not** clean out-of-sample either. **The defect was the silence, not the sign.**

### 3. **Real code bug: "flat-to-flat cycles" were not flat-to-flat.** *(V4 D4.)*
`v4_friction.py` incremented its cycle counter only on `pos == 0`, so a fill flipping *through*
zero merged a closing round trip with the newly opened one. 89 in-dev fills cross zero →
**4,805 cycles, not 4,711**. Corrected per-cycle stats: win rate 0.2534 → 0.2541, payoff
3.4916 → 3.4748, PF 1.1854 → 1.1838, avg net/RT $37.64 → $36.90.
**Unaffected:** net, gross, commission, slippage, every friction share, every Sharpe, every
breakeven multiple, and the whole per-contract tick ledger. Note this is the *same class* of
reconstruction error the orchestrator hit in `c4_audit.py` (position rebuilt from the wrong
field) — twice in one wave, which is a signal about the method, not the analyst.

### 4. **V1f's "no crossover exists" is conditional on an unnamed assumption.** *(V1f D1.)*
The analysis applied the 4× multiplier to **day** margin only. Under 4× × **initial** margin,
Product A binds in **15 of 60** capital-map rows (min ratio 0.503×); both Product B objects
still clear (1.57× / 2.29×). The report's flat claim "there is no crossover to report because
none exists" must be read as *conditional on 4× applying to day margin*. **The headline
verdict — that drawdown-based sizing, not margin, is the binding constraint for Product B —
survives; for Product A it does not survive the alternative reading.** B6's disposition
(stays optional, not promoted to a feasibility constraint) is unchanged for Product B.

### 5. **Two headline-flipping issues in O1/O1a.** *(O1 D1, D4.)*
`P_ruin` is taken as the **max** over the three bootstrap methods while `CE_g` is the
arithmetic **mean** over them — an asymmetry that was never pre-registered and never listed as
a weakness; and λ was derived on a non-compounded growth convention but multiplies a compounded
one, biasing λ low. Correcting either flips the sign of the objective in the worked example.
**Consequence: the O1 module is NOT yet fit to score anything.** The pre-registration, the
formal construction and the intraday-path machinery stand; the aggregation rule and λ
calibration must be fixed and re-pre-registered **before** the O2 retro-scoring pass. O2 is
therefore blocked, which is the correct outcome — better a blocked O2 than a scored one on a
sign-unstable scalar. Also D9: the shipped `min_unit` path is broken and its own test certifies
the broken number; D13: 16 dev sessions carry unexplained intraday data holes
(2022-11-07 has 249 bars against a full close; 2025-11-28 has 170 against an expected 385).

### 6. **Governance gap, and it is mine.** *(O1 D14, V1f D12, V1d D12.)*
All four companion analyses were delivered into `runs/W17_C4_COMPLIANCE/`, whose frozen
`spec.yaml` covers **only** the C4 compliance fix. None of them was pre-registered, and none
appeared in `research/registry/`. That is a real violation of the campaign's own
spec-before-results discipline and it was the orchestrator's scoping error, not the agents'.
**Remediated the only honest way available:** registry rows **454–457** record each analysis
*and* its red-team verdict, and each is explicitly labelled **NOT PRE-REGISTERED**, so the
multiple-testing ledger reflects what actually happened rather than a tidier version of it.
None of the four proposes promoting anything, so no alpha budget was consumed — but the
disclosure stands regardless.

### 7. **Data-quality findings that outlive this wave.** *(V4 D5, V1d D1/D9, O1 D13.)*
The NQ and MNQ 3-minute grids are **not** interchangeable: 13 NQ dev sessions have internal
gaps (487 missing bars) and 11 MNQ sessions (446), and the two grids disagree on the shape of
2 sessions. Counting non-17:00 sessions per grid gives **44**, not 43 — the 44th is the
2023-04-05 data hole (NQ) or file truncation (MNQ), not a calendar early close. **The wave's
43-early-close figure is correct as a calendar statement** (31×13:00, 9×13:15, 2×09:15,
1×09:30) and the C4 audit is unaffected, because it keys on the session-close clock rather
than on bar counts. But any future work that infers session shape from bar counts must handle
this. Filed as a standing caution.

### 8. Smaller items, ingested without narrative impact
V4 D6 (a "cross-checks all pass exactly" header over a paragraph disclosing one that does not
— 0.02% on Product A's daily vol), D7 (a turnover attribution inflated 10× by not normalising
NQ's point value: the true notional-normalised ratio is 3.56×, not 35.6×); V1f D3 (a coarse
2023-04-05/06 merge that moves $1,856.50 out of the DILATED bucket; sign and conclusion
unchanged), D4 (a contaminated `PRODUCT_A_rawNTbucketing` row shipped in a committed CSV with
no flag column — **treat that row as an artifact, not a finding**), D5 (an unflagged
negative-denominator share), D7 (a 51-vs-52 transcription error); V1d D3 (its most-cited table
is not reproducible from the shipped script). Every one is recorded here rather than quietly
fixed, per C7.

### 9. What the red team tried to break and **could not**
The friction ledger's core arithmetic (Product A's net rebuilt independently from the
26,881-fill ledger reconciles to **$0.00** against the committed battery); the slippage
measurement (every fill displaced exactly 1 tick adverse except where the bar's own range
truncated it, 527/527 on Product A); the 43-early-close calendar (matches exactly on the
last-bar clock); V1d's verdict (removing the 16:30 block adds 3 entries across 1,139 sessions
— the conclusion holds under every reconstruction tried); and V1f's session bucketing
(independently reproduced to the cent on 1,137 of 1,139 sessions).

---

*Minor: run artifacts are dated 2026-08-09, matching the owner directive's own date, while the
local environment clock read 2026-08-08 23:xx when they were written. Noted so the one-day
offset in `date_frozen` fields is not later mistaken for backdating.*
