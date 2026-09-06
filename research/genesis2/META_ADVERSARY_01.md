# META_ADVERSARY_01 — red-team of the entire GENESIS II programme (directive §67)

Written 2026-08-29 by the mandated meta-adversary after 16 formal objects. Scope: the programme's
methods, gates, directive, and conclusions — not any single run. Everything below cites run
artifacts or file:line; power arithmetic uses the normal approximation on the programme's own
printed sd/N. This document is adversarial testimony, not a state document; nothing in it
re-opens a closure by itself.

Evidence base read: `research/genesis2/*` (all 8 docs), `research/genesis/*` (charter, doctrine,
dossier, STATE B, failure map, atlases, scoreboard, all 78 `SEARCH_LEDGER.jsonl` records =
39 trials G00000–G00038), all 16 `runs/G2_F*` REPORTs + `G2_EXEC01`, full gate tables for
`G2_F1_ORB01`, `G2_F1_TICK01`, `G2_F6_AUCTREV01`, plus both world-scan skeptic files.

---

## Q1 — Are the gates selecting AGAINST real-but-modest edges?

**The arithmetic, at the programme's own printed numbers.** ORB01's battery (the wave-1 template):
Nw = 239 weeks, weekly sd $8,647 (`G2_F1_ORB01/out/gate_table.txt:8,54`). t ≥ 2.0 therefore
requires a weekly Sharpe of 2/√239 = 0.129 → **annualized Sharpe ≈ 0.93 in-sample**, i.e. weekly
mean ≥ $1,118.66 — the printed MDE, which is **80% of the entire incumbent's raw net**
($1,394/wk, `MASTER_SCOREBOARD.md:11`). Power of the t-rung alone against a TRUE edge:

| true ann. Sharpe | E[t] at 239 wk | P(pass t≥2) |
|---:|---:|---:|
| 0.3 | 0.64 | ~9% |
| 0.5 | 1.07 | ~18% |
| 0.7 | 1.50 | ~31% |
| 1.0 | 2.14 | ~56% |
| 1.5 | 3.22 | ~89% |

Stack the p95 circular-shift rung (O2) and the raw-dollar control rung (O3) and a true
Sharpe-0.5 two-sided edge passes the full battery **well under 10% of the time**. O3 deserves its
own line: it demands the candidate's *raw net dollars* beat always-long 09:46→15:59 (+$61,013 in
the window, `gate_table.txt:10`) — so a genuine conditioning edge that sits flat part of the time
must out-earn the drift it forgoes, ~$52/session of flatness, in pure alpha. Event-family rungs
are harsher still: TICK01's MDE was **15.1 bps per 15 minutes** at N=63 (`G2_F1_TICK01/out/
gate_table.txt:10`) — a bar only an institutional-desk-scale effect could clear. The batteries
are, by construction, blind to everything below ann. Sharpe ≈ 1 on a 4.6-year window; they can
only ever surface Sharpe-1.5+ objects.

Is that wrong? Half of it is defensible: MDEs are printed before every verdict, closures carry
"5.5× under MDE" language (`FAILURE_MEMORY.md:25`), and with ~39 logged trials an *uncorrected*
t=2.0 is if anything lenient (Bonferroni at 39 would want z≈3.2). The indictable half is the
**routing layer**: `ACTIVE_ALPHA_QUEUE.md:45-48` concludes "the measured bottleneck is the SIGNAL
stage — what fails is information content," and pivots representation. What is actually measured
is that **no Sharpe-≳1 signal exists in these archetypes**; about the modest-edge band
(0.3–0.7 — where surviving retail edges plausibly live) the programme has close to zero
information, by design, and its state documents nowhere say so as a standing detectability floor.

**The incumbent, submitted blind.** Rung by rung on its own discovery window:
- O1a cost gate: PASS (≈$1,324/wk at measured $25.01/RT, `MASTER_SCOREBOARD.md:12`).
- O1b t≥2: PASS trivially (t 4.16 = ann. Sharpe ≈ 2.06 at 213 wk) — **but that t is
  post-selection over ~123 waves/700+ experiments with no deflator**
  (`GENESIS_PRIOR_RESEARCH_ATLAS.md:8-10`); the dossier itself prices the ABS→PCT step at
  p≈0.058 (`GENESIS_INCUMBENT_DOSSIER.md:24`). The gates cannot see this; the W1 skeptic's very
  first attack on MC-01 ("largest multiplicity... hundreds of implicit trials... any fresh spec
  must be single-shot," `skeptic_verdicts.md:33-35`) applies verbatim to P1 and was never applied.
- O3 control: PASS ($1,394 vs B1a $718/wk raw; 8.4× at fixed-DD, `GENESIS_SCOREBOARD.md:11,16`).
- E4-class era-consistency: **CANNOT BE ATTEMPTED** — P1's member pipeline has never been run
  pre-2022; no deep-era diagnostic exists (ORB was forced to print one, line 16 of its gate table).
- R_a-class concentration (top-10% ≤ 40% of net, the rung that killed AUCTREV): **NEVER MEASURED
  for P1.** Momentum-shaped books routinely fail 40%; B-MOM alone is 51% of P1's net
  (`GENESIS_PRIOR_RESEARCH_ATLAS.md:56`).
- R_c-class timing-teeth: the one probe that exists cuts the other way. EXEC01 E3: +1-minute
  delay costs −$90/wk, −6.4%, n.s. — reported as *reassurance* ("P1 is not knife-edge on a minute
  of latency," `G2_EXEC01/REPORT.md:27`). AUCTREV's late-entry degrading only 15% was reported as
  *mechanism falsification* and was fatal (`G2_F7/REPORT.md:18-21`). Same evidence genre,
  opposite valence, chosen by which side of the scoreboard the object sits on.

**Concrete answer: P1 would pass the wave-1 economics battery and has never been shown to pass
the wave-7 certification battery; one rung it structurally cannot attempt.** Challengers face a
strictly harsher exam than anything the champion ever sat.

**VERDICT: INDICTED (two changes).** (1) Publish a standing DETECTABILITY FLOOR note (the table
above, per family), and require every NULL closure to carry "below detectability floor X" where
observed < MDE — the funnel line "signal is the bottleneck" is retracted or requalified.
(2) Run the symmetric certification of P1 (see Q10) — it is not anti-P1 mining; it is the
charter's own §8 applied to the only object that skipped it.

---

## Q2 — Cost assumptions: too harsh or correctly harsh?

**The mean is correctly harsh; the measurement's coverage is the weak point; the ladders
over-extend it.**

- Every cost surprise in this repo's history has been in one direction: $10/RT early-era →
  $14.65 → model $14.44 vs measured $20.65 (`G2_EXEC01/REPORT.md:8-11`; W82 model on the same RTs
  $15.00). Mesfin kills 14 MNQ families at 2-pt friction (`GENESIS_EXTERNAL_EVIDENCE.md:16`).
  The empirical prior favors hostility. Charging $25.01 pooled is defensible.
- **But the $20.65 stands on 131 ctrRT = 5.1% overlap, and the overlap exists only where local
  BBO exists — essentially 2025-08→2026-07** (`GENESIS_DATA_ATLAS.md:11`). All measurement mass
  is the last twelve months; the 20-year event studies (AUCTREV at $35/$40/$45, DELEV02) are
  costed at 2025–26 quote levels with zero pre-2025 spread evidence in either direction. The era
  cut inside the measurement ($17.12 vs $28.69, `G2_EXEC01/REPORT.md:15-16`) shows the number is
  regime-sensitive even within one year.
- **Could true cost be materially lower for patient execution? For P1-class fill-instant
  aggression, no** — E4 (passive available 0.7% of entries) and the 4.30-tk-at-fill-instant
  finding close that door for the incumbent. **For patient objects, the question is open and the
  ladders pretend it is not.** E4's 0.7% measures quoted ≤1-tick availability *at P1's fill
  instants* — the wrong statistic for an overnight/event object that can rest orders across a
  minutes-long window (E3 itself demonstrates minute-scale price slack: −6.4% n.s.). The W2
  skeptic then converts p90 ($35) into class-wide *floors* — "$40/RT stressed-tape," "$35 + $5.25
  ON" (`skeptic_verdicts_w2.md:13-18,345-347`) — which stacks p90 spread × full-spread aggression
  × worst-era regime. That is a hostility *policy*, fine — but then closures produced under it
  must say "dead at hostile-cost policy," and none do.
- The honest resolution is already on the shelf: the Databento MBO execution-falsifier is the
  programme's own top-ranked acquisition (`GENESIS_STATE_B_REPORT.md:99-103`) and would measure
  resting-order adverse selection directly.

**VERDICT: MIXED.** Pooled harshness UPHELD for aggressor-style objects. INDICTED on three
specifics: (a) the 5.1%/recent-era coverage must be stated wherever $20.65 is quoted as "the"
cost; (b) deep-era event studies may not silently inherit 2025–26 quote levels — print a
cost-era caveat in their gate tables; (c) patient/overnight floors are assumption-stacked, and
the class-level $40 floor should be labeled POLICY, not measurement.

---

## Q3 — Wrong horizons?

**Tested:** minutes (ORB, TICK, sweep, exec-timing), same-session, overnight (AUCTREV),
1–3 sessions (H1, DELEV02), plus exactly two weekly-scale objects — H7 COT (one observable) and
H3 XSMOM (cross-sectional structure, not NQ direction). **Structurally never touched: NQ-direction
holding periods from ~3 sessions to ~1 quarter** — the swing band. Scan the 28 live cards plus
both card sets (MC-01…56): nothing in that band; the closest (MC-52 monthly VRP) was triaged LOW
and denied a slot (`skeptic_verdicts_w2.md:198-208`).

Is that justified scope? The implicit defense — N: 4.6 modern years cannot power weekly-scale
modest edges (true; see Q1 table). But the programme owns a 1,043-week deep spine
(2006→2026, `GENESIS_DATA_ATLAS.md:14`), and at 1,043 weeks **t=2 needs only ann. Sharpe ≈ 0.45**
*(⚠️ MEASURED CORRECTION 2026-09-06, `G2_SWING02`: at the 0.05/3 family bar, 80 % power, and a
dependence-preserving null ~1.3× wider than iid, the actually detectable edge is **~0.66–0.78
ann. Sharpe** — the t≈2 arithmetic below understates the bar. The lane was read twice and parked
FALSIFIED-AS-ARGUED; see `ACTIVE_ALPHA_QUEUE.md`.)*
— exactly the modest-edge band Q1 shows is invisible everywhere else. Owner doctrine explicitly
says old-regime failure is a risk classification, not a veto (CLAUDE.md §4), and the ERABREAK
inadmissibility ruling is scoped to *intraday vol statistics* (`G2_F3_ERABREAK01/REPORT.md:7-9`),
not to daily/weekly direction. So the swing band is testable under the programme's own rules, at
the only sample size where its own gates have power against modest edges, at horizons where the
measured $25/RT cost bar — the thing that killed most of the universe (`G2_WORLDSCAN_W1/
REPORT.md:18-20`) — becomes noise (one RT amortized over 10–30 sessions). The hole is not an
evidence-based closure; it is an unexamined default inherited from an intraday-native repo.

**VERDICT: INDICTED.** The next scan wave (already §65-triggered for orthogonal archetypes)
must include a SWING family: 3-session–3-month NQ-direction mechanisms on the deep weekly spine,
with exposure-matched always-long controls (the drift-masquerade guard matters most here — the
programme already owns that control technology).

---

## Q4 — Wrong targets? (vol as the traded object)

The charter objective is trading NQ/MNQ (`GENESIS_CHARTER.md:8-10`); vol-as-target is out of
scope by *directive*, not by evidence. The tension: the programme's own external-evidence file
ranks "VIX term-structure state" as the **"strongest evidence-per-dollar found"** and the cited
mechanism (Cheng RFS 2019: ex-ante VIX premium predicts **VX returns**, coeff ≈ 1,
`GENESIS_EXTERNAL_EVIDENCE.md:24-27`) is native to the VX/VXM instrument — yet it was only ever
tested in its weakest projection, the VX→NQ conditioning join, which came out wrong-signed NULL
(GENESIS_H1). VX daily is certified at $0; VXM is a retail-sized listed future. So the strongest
mechanism the search found cannot be expressed inside the scope, and no owner memo recording
this trade-off exists anywhere in `research/genesis*/`.

Scope is the owner's right, and there are honest reasons to keep it: VX carry is a graveyard
(2018-02-05 recorded, `FAILURE_MEMORY.md:108`), margin/tail asymmetry is real, and one more
instrument multiplies the certification surface. Realized-vol timing of NQ itself *was* tested
(VOLSIZE01) and failed as growth timing. But the decision should be recorded as a decision.

**VERDICT: MIXED — UPHELD as governance, INDICTED as process.** Write the one-page owner memo:
"the top-ranked external mechanism is native to VX/VXM; extending scope costs X (certification,
margin tail, graveyard priors) and buys Y; recommend yes/no." The programme choosing silence
chose for the owner.

---

## Q5 — Academic priors vs practitioner search?

Outcomes of the two scans, by seed class: wave-1 formal picks were all practitioner-rooted
(Crabel ORB/NR7, TICK folklore) — 0/4. Wave-3 picks were academic-rooted (microstructure cost,
era-break, Moreira-Muir sizing, fire-sale spirals) — no alpha survivor either, but they produced
the campaign's two *doctrine* assets (ERABREAK inadmissibility ruling; validated cost model,
`G2_F3_EXECSTATE01/REPORT.md:11-13`). The only two *information* positives (15:50 break,
G00029; breadth divergence, G00030) came from claims whose selling point was **verified negative
space** — nobody had measured them (`skeptic_verdicts_w2.md:129-130`; `G2_F5_TRIO/REPORT.md`).
Meanwhile the heavily-weighted evidence-class hierarchy (peer-review > practitioner) predicted
nothing: published effects arrived pre-decayed exactly as McLean-Pontiff warned (H4B tested a
known-dead effect — defensible as death-date measurement, but a wave slot), and folklore arrived
pre-falsified. Neither direction of the question indicts; the *ranking variable* does.

**VERDICT: MIXED.** Neither over- nor under-valuing is measurable in outcomes — both lanes went
0-for-alpha. The actionable finding: EVI should upweight **unmeasured original claims (negative
space) and expected doctrine value**, and downweight source pedigree, which has now demonstrated
zero predictive power over two scans. The W2 top-6-by-EVI list already drifted this way
(MC-47/54 are doctrine buys); make it explicit in the next scan spec.

---

## Q6 — Are closures being over-generalized AGAIN? (5-closure audit)

1. **ORB01** (`FAILURE_MEMORY.md:23`) vs report/gate table: exact — scope string, control loss,
   "2025 carries all" (LOYO ex-2025 −$24,664), deep sign-flip all verified. CLEAN.
2. **TICK01** (`FAILURE_MEMORY.md:26`) vs report: row says "2022–2026," report scope is
   "−1000/−400 arming, 15-min horizon, 2022–2026-07" — the disarm parameter and end-month are
   dropped. Substantively fine; "44→2/yr" matches. MINOR DRIFT.
3. **SWEEP01** (`FAILURE_MEMORY.md:37`): the closure *text* is exactly scoped, and the report
   even states "Overnight levels and other geometries were not tested and are not implied"
   (`G2_F2_SWEEP01/REPORT.md:19-20`). **But the closure's mechanism interpretation was then used
   predictively**: MC-49 was KILLED because "the closure's mechanism finding already predicts
   this card's outcome" at a different, untested geometry (`skeptic_verdicts_w2.md:157-168`).
   That is a measured-once interpretation doing the work of a measurement at a new scope — the
   exact failure mode FAILURE_MEMORY was built to stop, relocated from closure text to closure
   *application*. (The kill may well be right on the merits — ICT-node evidence, graveyard entry
   shape — but the stated ground is an extrapolation the run report explicitly disclaims.)
4. **VOLSIZE01** (`FAILURE_MEMORY.md:53`): the row omits the run report's own substrate-
   attenuation caveat and recorded revival condition ("retest on a ratio-adjusted series —
   recorded, not scheduled," `G2_F3_VOLSIZE01/REPORT.md:19-23`). A reader of FAILURE_MEMORY alone
   sees an unconditional FAIL. MINOR-TO-REAL DRIFT.
5. **AUCTREV** (`FAILURE_MEMORY.md:71`): exact, even generous — banked facts preserved, reframing
   path stated. CLEAN.

Also credit where due: the NOT-closed guard (`FAILURE_MEMORY.md:110-118`) is an
anti-over-generalization device no prior campaign had, and it demonstrably worked (ORB mechanism
kept distinct from the B3 control). The residual risk is the **pattern layer**: "dead short legs
recur," "fade graveyard 0-for-7" (`FAILURE_MEMORY.md:29-31`; `skeptic_verdicts_w2.md:252-253`)
aggregate heterogeneous formulations into quasi-quantitative priors that now set cost floors and
kill cards.

**VERDICT: MIXED, leaning UPHELD at the text layer; INDICTED at the application layer.** Rule
change: a KILL/closure may cite a prior closure's *mechanism interpretation* only as prior, never
as the dispositive ground, unless the new object is inside the closure's literal scope; and
FAILURE_MEMORY rows must carry their run's recorded revival conditions (fix the VOLSIZE01 row).

---

## Q7 — Is the AUCTREV tail-lesson being over-applied?

Separate the two rungs. **R_c (timing-teeth) was a legitimate kill of the formulation as
preregistered**: the hypothesis was *fast overnight reversion of an EOD dislocation*; late entry
degrading only 15.4% (G00035) falsifies that stated mechanism. UPHELD on the instance — and note
the instance is also a poor "insurance" candidate: it buys crashes (bottom-decile dislocation →
long), so on a long-biased incumbent book it adds crisis beta; the other 480 events sum to
−5,605 pts of carry (`G2_F7/out/S2_robustness.txt` via ledger G00035).

**But the process now hard-codes an anti-tail bias.** Three facts compound:
(a) the R_a gate (top-10% ≤ 40% of net) is a broad-edge criterion that any positively-skewed
object — including, plausibly, the incumbent's own momentum book, see Q1 — fails by nature;
(b) the new standing lesson makes "concentration + timing-teeth rungs mandatory for any
economics survivor" with no tail-class carve-out (`FAILURE_MEMORY.md:73-75`);
(c) the pipeline sequences portfolio-marginal LAST and aborts it on any robustness failure —
S3 never ran (`G2_F7/out/S3_portfolio.txt:6-10`). For a genuine tail object, portfolio-marginal
in stress states **is the primary question**, and the current ordering guarantees it is never
asked. A preregistered-AS-tail candidate (54 paying events, negative carry, crisis convexity)
entering this pipeline today dies at R_a before anyone measures the only thing that could
justify it.

**VERDICT: MIXED — instance UPHELD, class INDICTED.** Create a preregistered TAIL-OBJECT class:
concentration cap replaced by (i) event-count power floor, (ii) carry-cost bound in non-event
periods, (iii) stress-state portfolio-marginal run FIRST, (iv) timing-teeth retained at the
mechanism's claimed timescale. Any crisis-rebound card must still carry the DELEV02 null and the
crisis-beta caveat above.

---

## Q8 — Are engineering guards / reserves suppressing valid work?

- **Substrate law, seal discipline, null_guard: UPHELD.** The DELEV01 catch prevented a false
  NULL from being recorded (the defect verdict is the system working); the blast-radius audit's
  attenuation logic is directionally sound; gate tables show null-teeth verified before use
  (`G2_F6_AUCTREV01/out/gate_table.txt:29`). The virgin seal is the programme's only future
  evidence and NT8 writes into it daily (`GENESIS_DATA_ATLAS.md:22-25`) — keep the wall.
- **The P-1 reserve (2022+ implied-vol→NQ join) is now plausibly negative-EVI.** It was created
  to preserve a confirmation read for survivors of pre-2022 VX discovery. H1 — that discovery
  lane — is NULL, wrong-signed; there is no surviving leg awaiting confirmation and no queued
  consumer (MC-52 denied a slot). Meanwhile the reserve blocks the entire modern implied-vol
  axis, whose decisive era is 2022+ *by mechanism* — the W2 skeptic itself documented the
  deadlock for MC-56: "the admissible window can't confirm and the confirming window is reserve"
  (`skeptic_verdicts_w2.md:247-257`) — and then simply left it standing. A reserve protecting a
  confirmation that can no longer occur, at the cost of a whole axis, protects nothing.
- **The blind BBO pools (19 NQ + ~20 ES sessions) have lost their consumer.** They were reserved
  falsifier-grade for order-flow candidates; that lane is closed by power twice and by cost once
  (`FAILURE_MEMORY.md:89-90,107`). Meanwhile the programme's binding cost row hangs on a 5.1%
  overlap (Q2). Opening a *defined fraction* of the pool for pure execution **measurement** (not
  alpha discovery) carries near-zero selection risk — measurements don't overfit — and would
  multiply the cost-truth N.

**VERDICT: MIXED.** Guards UPHELD in full. Two reserves INDICTED: write the owner decision memo
proposing (1) conversion of P-1 into one structured, family-wise-corrected discovery budget on
2022+ implied vol (knowingly sacrificing confirmation status), and (2) a bounded
execution-measurement carve-out of the ES/NQ blind BBO pool. Both are owner-gated spends of
scientific capital — the point is that *not deciding* is also a spend.

---

## Q9 — Is the multiplicity accounting honest in both directions?

- **Undercount direction (scouts/triage searched hundreds):** materially defused by design —
  triage and formal-wave selection are recorded as mechanism/evidence reasoning *before any
  outcome computation* (`RESUME.md:42-44`; W1 REPORT:4-5), and the cards carry external claims,
  not in-repo backtests. A garden of forking paths pruned on priors, not on the data, does not
  accrue classical selection debt. The honest residual leak: the priors themselves are
  outcome-informed (graveyard base rates, cost truth), so the surviving trial set is tilted
  toward what past data liked — a second-order contamination, worth a sentence in the funnel
  doc, not a deflator.
- **Overcount direction:** yes — of 39 ledger trials, ~10–11 are infrastructure/measurement
  (8 baseline controls, reproduction, data contract, EXEC01, MAE01, ERABREAK, CLAIMS register,
  DC audit); genuine alpha-selection trials number ~20. Quoting "39 trials" as search debt
  overstates ~2×. Conversely single trials bundle up to 11 sub-hypotheses (G00011: 11 day-types;
  G00021: 7 claims) — compensated correctly by within-run family-wise bars (2.85, 2.572,
  K_eff 2.58 in F8). The survivor-carries-debt convention was actually enforced on the one
  survivor (AUCTREV's "1-of-13 atop ~750" sentence). The known gap — no program-level deflator —
  is admitted in writing (`GENESIS_PRIOR_RESEARCH_ATLAS.md:8-10`).
- The one place the books are NOT symmetric is Q1's finding: the multiplicity lens is applied
  with full severity to external cards and never to the incumbent's own t=4.16.

**VERDICT: UPHELD** at the ledger/family level, with two required footnotes: (a) split the
headline count into alpha-trials vs measurements; (b) record the outcome-informed-prior leak as
a standing caveat on triage. The incumbent asymmetry is charged under Q1, not here.

---

## Q10 — The single highest-EVI action with no current plan

**Submit P1/PCT to the exact battery its challengers face — a preregistered symmetric
certification run.** Concretely, on the frozen, reproduced action set (2,131 trades; already
materialized in `G2_EXEC01/out/p1_trades.csv` and MAE01):

1. **Concentration rung**: top-decile trade/week share of net vs the 40% bar that killed AUCTREV.
2. **Timing-teeth rung**: delay-degradation profile (1/5/15-min late entry on the frozen
   decisions) judged at the mechanism's claimed timescale — the same E3 fact currently narrated
   as reassurance gets a preregistered pass/fail meaning.
3. **Era rung**: run the member ensemble on the deep spine 2006–2021 as a *diagnostic* (the
   pipeline needs only NQ 1-min, which exists to 2006) — the same non-gate sign-flip print ORB
   was required to show.
4. **O2-class rung**: dependence-preserving circular-shift null on P1's decision series.

This is measurement/certification of the champion, not anti-P1 supervised mining (no surface is
searched, nothing is fit) — it is charter §8 finally applied to the one object that skipped it.
Why it is the highest-EVI item: every routing decision in the programme — the anti-P1 mining
bar, MC-35 blocked-as-rescue, the shadow roster, the "no candidate beats the incumbent"
executive answer (`GENESIS_STATE_B_REPORT.md:82-88`) — is priced off P1's unexamined status at
exactly these rungs. Either P1 survives its own machine (the scoreboard's authority becomes
real, and the gates' severity is vindicated by a passing example), or it fails a rung the
challengers die on (and the programme learns its exam measures payoff *shape*, not edge —
before the shadow read, not after). Cost: one run; all inputs exist. Runner-ups, already argued
above: the swing-band scan (Q3), the P-1/blind-pool owner memos (Q8), the VX scope memo (Q4).

**VERDICT: INDICTED — by omission.** No queue, card, or calendar entry anywhere schedules this.

---

## Summary table

| Q | subject | verdict |
|---|---|---|
| 1 | gates vs modest edges + blind-P1 | **INDICTED** — detectability floor unstated; certification asymmetric |
| 2 | cost harshness | **MIXED** — mean upheld; coverage/ladders/deep-era indicted |
| 3 | horizons | **INDICTED** — 3-session–3-month swing band untested, testable under own rules |
| 4 | vol as traded object | **MIXED** — scope is owner's; silence about its cost is not |
| 5 | academic vs practitioner | **MIXED** — both 0-for-alpha; pedigree weighting predicts nothing |
| 6 | closure over-generalization | **MIXED** — text layer clean; application layer (MC-49) indicted |
| 7 | tail-lesson over-application | **MIXED** — AUCTREV kill upheld; pipeline now structurally anti-tail |
| 8 | guards/reserves | **MIXED** — guards upheld; P-1 reserve and blind BBO pool negative-EVI |
| 9 | multiplicity honesty | **UPHELD** — with two footnotes required |
| 10 | highest-EVI unplanned action | **INDICTED** — symmetric P1 certification, unscheduled |

Nothing here reopens a closed scope, spends a pool, or touches the seal. Every proposed change
is a spec, a memo, or a measurement. `LIVE ENABLED = NO`.
