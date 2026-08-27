# WE_W90 — B-MOM'S TWO SIDES, AS SLEEVES · REPORT

Preregistered (`spec.yaml`). Owner directive §7. Every falsifier was written before the read.

> ## **H1 PASS · H2 PASS · H3 does not fire · H4 GENERIC · and a number I reported before
> ## compaction is WITHDRAWN.**
> ## The short leg is real, it is decorrelated from everything in the repository, and its
> ## decorrelation is **STRUCTURAL rather than informational** — it is the same finding as
> ## W89's, one level down. **Nothing is promoted.**

---

## 0. `CORRECTION` — withdrawing my own pre-compaction number

I reported *"BMOM trades long AND short: 573 long ($166,047, $289.8/trade, 48.9 % win) / 579
short ($86,216, $148.9/trade, 43.4 % win)"*, and that figure is written into the header of
`WeeklyEdgeBmom_v1.cs`. The spec required this rebuild to report a disagreement rather than
quietly replace it. It disagrees:

| | pre-compaction (WITHDRAWN) | **this rebuild** |
|---|---|---|
| long trades / net | 573 / $166,047 | **518 / $168,567** |
| short trades / net | 579 / $86,216 | **525 / $83,691** |
| $/trade long / short | $289.8 / $148.9 | **$325.4 / $159.4** |
| win % long / short | 48.9 % / 43.4 % | **50.2 % / 43.6 %** |

The earlier count was 10 % high on trades and the totals reconcile to a different trade list —
it was computed in an uncommitted heredoc, which is precisely why the repo rule says **no
prose-only number**. The `.cs` header is corrected in the same commit as this report.
**The direction of the finding is unchanged: B-MOM is genuinely bi-directional and its short
side is worth $83,691, one third of the object's net.**

## 1. `FACT` — the attribution split (NOT tradeable, and labelled so)

| side | trades | share | net | $/trade | win % | median trade |
|---|---|---|---|---|---|---|
| LONG | 518 | 49.7 % | **$168,567** | $325.4 | 50.2 % | +$23.1 |
| SHORT | 525 | 50.3 % | **$83,691** | $159.4 | 43.6 % | **−$864.4** |
| both | 1,043 | 100 % | $252,258 | $241.9 | 46.9 % | −$434.4 |

The session box halts on **combined** realised P&L, so these two series are coupled by
construction and neither can be run from this split. That is why measurement B exists.

## 2. `FACT` — re-simulated as real sleeves, each with its own box

Net of W89's candidate-specific **$12.99/contract round turn**:

| sleeve | trades | ctrRT/wk | weekly $ | wk + % | streak | max DD | top-5 DD | worst week | wk$ @ fixed DD |
|---|---|---|---|---|---|---|---|---|---|
| BMOM_L | 677 | 3.18 | $573 | 54.9 % | 5 | $41,547 | $26,392 | −$16,543 | $279 |
| BMOM_S | 692 | 3.25 | $277 | 46.5 % | 8 | $51,830 | $36,612 | −$16,949 | $108 |
| **BMOM_B (incumbent)** | **1,043** | **4.90** | **$1,121** | **56.8 %** | **4** | **$44,603** | **$27,795** | **−$16,970** | **$509** |
| BMOM_L + BMOM_S separately | 1,369 | 6.43 | $850 | 52.6 % | 4 | $56,239 | $36,571 | **−$33,492** | $306 |

> **The incumbent shared-box object beats the sum of its own parts on every column.** Splitting
> the box produces **31 % more trades** (1,369 vs 1,043), **24 % less money**, and **doubles the
> worst week** (−$33,492 vs −$16,970). `REPRODUCED` — this is W51b/W53's day/night finding
> (*"the session box belongs on the COMBINED book; per-book boxes are 25 % worse on drawdown"*)
> holding on a partition it was never tested on.

## 3. H1 `PASS`, and the qualification matters more than the pass

Charter amendment 2 (a) — the only chronology gate — with sessions, weeks, trades, mean and SE:

| sleeve | period | weeks | trades | weekly $ | SE | **t** | wk + % |
|---|---|---|---|---|---|---|---|
| BMOM_L | full | 213 | 677 | $573 | $369 | 1.55 | 54.9 % |
| | **t24** | 105 | 315 | **$431** | $626 | **0.69** | 53.3 % |
| | t12 | 53 | 159 | $205 | $854 | 0.24 | 50.9 % |
| BMOM_S | full | 213 | 692 | $277 | $364 | 0.76 | 46.5 % |
| | **t24** | 105 | 326 | **$401** | $608 | **0.66** | 48.6 % |
| | t12 | 53 | 162 | **$797** | $856 | 0.93 | **54.7 %** |
| BMOM_B | full | 213 | 1,043 | $1,121 | $464 | **2.42** | 56.8 % |
| | t24 | 105 | 484 | $1,310 | $784 | 1.67 | 59.0 % |
| | t12 | 53 | 241 | $1,417 | $1,133 | 1.25 | 60.4 % |

**H1 passes** — BMOM_S is +$401/week over the trailing 24 months. But read the t column:

> `FACT` **Neither half is individually significant at any horizon. Only the combination is**
> (full-window t = 2.42 against 1.55 and 0.76). The parts are not two objects that happen to be
> bundled; the bundle is the object and the parts are underpowered pieces of it.

And note the *reversal in the last year*: over the trailing 12 months the **short** side is the
productive one (**$797/week, 54.7 % positive**) and the long side has essentially stopped
(**$205/week, 50.9 %**). On 53 weeks that is t = 0.93 vs 0.24 — `WEAK`, not a finding, but it is
the opposite of what the campaign's long-only prior would predict and it is recorded.

## 4. H2 `PASS` — and the whole weekly-ρ matrix, which changes the stream census

| weekly ρ | BMOM_L | BMOM_S | BMOM_B | X9a | P1 | SHORT |
|---|---|---|---|---|---|---|
| **BMOM_L** | 1.000 | **−0.093** | 0.605 | **+0.060** | +0.407 | −0.010 |
| **BMOM_S** | −0.093 | 1.000 | 0.542 | **−0.030** | **−0.093** | +0.371 |
| BMOM_B | 0.605 | 0.542 | 1.000 | +0.009 | +0.287 | +0.261 |
| X9a | +0.060 | −0.030 | +0.009 | 1.000 | **+0.613** | +0.027 |
| P1 | +0.407 | −0.093 | +0.287 | +0.613 | 1.000 | +0.156 |

- **H2 passes**: weekly ρ(BMOM_L, BMOM_S) = **−0.093** (daily +0.030 — the unit matters again).
- **Underwater-curve ρ = +0.041**, which is W56's criterion for a sleeve that actually pays.
- **BMOM_S is ρ < 0.2 with everything in the repository except the old mirrored SHORT sleeve**
  (+0.371): −0.093 with BMOM_L, −0.030 with X9a, **−0.093 with P1**.

### The census, recomputed on weekly ρ

Maximal set with all pairwise |ρ| < 0.20:

> **{BMOM_L, BMOM_S, X9a} — K = 3**, up from W88's 2.
> (An equally-sized alternative exists: {BMOM_L, X9a, SHORT}. P1 cannot join either — it is
> +0.407 with BMOM_L and +0.613 with X9a.)

**Three things must travel with that number or it is misleading:**

1. `INFERENCE` **the decorrelation is STRUCTURAL, not informational.** BMOM_L and BMOM_S are the
   two signs of ONE latched channel: within a session, when one holds a position the other
   cannot. They are mutually exclusive in time by construction. This is the same mechanism W89
   found one level up (BMOM is 100 % RTH, X9a is 62.6 % overnight). **Low ρ here is a clock
   fact, not evidence of independent information.**
2. `FACT` **W74's K-requirement assumes streams "at our quality".** BMOM_L and BMOM_S carry
   t = 0.69 and 0.66 over the trailing 24 months against P1's much stronger record. **Two weak
   streams are not two P1-quality streams and the 76 %-positive-week arithmetic does not
   accept them at face value.** Recomputing W74's bootstrap with heterogeneous stream quality is
   now an owed measurement and is queued.
3. `FACT` **both halves are NEGATIVE in 2026** (§6). Under W88's stricter recency gate
   ("positive in the full window AND 2025 AND 2026") **neither half is admissible** and K stays
   at 2. Under the charter's actual text — *effective over roughly the trailing two years* —
   both pass. **The census answer depends on which gate you read, and the charter's text is the
   binding one.** Stated both ways rather than picking the flattering one.

## 5. H3 does not fire — one box, not two

| leg | two boxes | one box | winner |
|---|---|---|---|
| weekly $ at fixed DD | $306.1 | **$508.7** | ONE |
| positive-week % | 52.6 % | **56.8 %** | ONE |
| raw mean top-5 DD | $36,571 | **$27,795** | ONE |

**0 of 3.** The incumbent construction is correct and this closes the question.

## 6. H4 `GENERIC` — the short leg is exposure, not special information

200 removals of the same number of BMOM trades, matched on trade count **and** contract-minutes
of exposure, scored on the 2:3 basket's three gate legs:

| leg | real (short kept) | null mean | null p95 | **percentile** |
|---|---|---|---|---|
| weekly $ at fixed DD | $1,183 | $866 | $1,341 | **86.5 %** |
| positive-week % | 57.7 % | 55.4 % | 58.7 % | **81.0 %** |
| raw mean top-5 DD | $57,273 | $63,735 | $48,584 | **73.5 %** |

Bar was ≥95th on all three. **It clears none of them.**

Against the direct alternative (basket with the short leg simply deleted): money $1,183 vs
$1,101, positive weeks 57.7 % vs 54.5 %, **top-5 drawdown $57,273 vs $56,699 — the short leg
makes the drawdown slightly WORSE.**

> **The honest answer to the owner's four-way question.** Does the short side provide
> *standalone expectancy*? — yes, but weakly (t = 0.76 full, 0.66 over two years).
> *Different regime exposure*? — partly (§7). *Genuine drawdown offset*? — **no; it is at the
> 73rd percentile of its own null and it worsens the basket's top-5 drawdown.**
> *Or merely lower-quality production*? — **that is the closest description**: $159/trade against
> $325, 43.6 % win against 50.2 %, and a median trade of **−$864**.
>
> **It is kept**, because it adds money and positive weeks and removing it is what makes the
> basket worse on two of three legs — but it must be described as *additional roughly-independent
> events*, which is mechanism law 6 (`tail protection comes from many roughly-independent events
> per week`), and **not** as a second source of information.

## 7. H5 — per year, weekly $ (calendar partition, causal)

| sleeve | 2022 | 2023 | 2024 | 2025 | **2026** |
|---|---|---|---|---|---|
| BMOM_L | $782 | $912 | $526 | $807 | **−$531** |
| BMOM_S | $760 | **$11** | $112 | $714 | **−$164** |
| **BMOM_B** | $1,584 | $823 | $1,099 | $1,814 | **+$7** |
| X9a | $639 | **$0** | $1,993 | $627 | **$1,438** |

- **2023 is where the two sides separate**: long +$912, short +$11. The short side did nothing
  in the year the long side carried.
- **2026 is where they both stop.** BMOM_B's whole year is **+$7/week** — the regime-local
  problem stated as sharply as it can be. W67 measured B-MOM's 2026 contribution to P1 at
  **−16.6 % of net**; this is the standalone version of the same fact.
- **X9a is the complement**: $0/week in 2023, $1,438/week in 2026. `SUPPORTED` — the pair's
  value is that the two components fail in different years, which is what ρ = +0.009 encodes.

## 8. Verdict against the preregistered decision rule

> H1 PASS + H2 PASS → *"BMOM_S is a THIRD CANDIDATE STREAM and goes to its own
> champion-vs-challenger wave. It is NOT promoted here."*

Applied literally that is the outcome, and it is **weakened by three things this wave measured
and the spec did not anticipate**: the decorrelation is structural rather than informational
(§4.1), both halves are individually insignificant (§3), and the short leg fails its own
specificity null (§6). **The correct status is therefore: BMOM_S is a candidate stream whose
independence is a clock artifact and whose contribution is generic.** That is worth pursuing on
the *clock* axis — which is where W75's live brief already pointed — and not worth pursuing as
"we found a short edge".

**Nothing is promoted. The incumbent BMOM_B construction survives every test in this wave.**

## 9. Files
`out/sides.txt` · `out/sleeves_daily.csv` · `out/rho.csv` · `out/null_short.csv` ·
`out/per_year.csv` · code `research/weekly_edge/src/run_we_w90.py`
