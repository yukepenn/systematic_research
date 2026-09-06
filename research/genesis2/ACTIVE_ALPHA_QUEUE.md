# ACTIVE ALPHA QUEUE

**State document.** Replenishment rule (README): < 10 DISCOVERED or < 3 MED/HIGH → auto-launch a
new scan wave. Statuses: DISCOVERED → TRIAGED → PREREGISTERED → TESTING → CLOSED / SURVIVED →
FORWARD-QUEUED.

## Health (2026-09-05 — post-Formal-Wave-3, WORLDSCAN-W2, GENESIS III)

> ⚠️ Wave-2 cards (MC-38…56) live in `runs/G2_WORLDSCAN_W2_20260829/out/mechanism_cards_w2.md` +
> `out/skeptic_verdicts_w2.md` — **`WORLD_ALPHA_ATLAS.md` is Wave-1 only** and points here.

**Formal Wave 3 outcomes (all 2026-08-29):** MC-47 CLOSED NULL (`G2_F3_EXECSTATE01` — but the
cost model f(spread,depth,hour) = $21.71/ctrRT was VALIDATED in scope) · MC-40 CLOSED NULL
(`G2_F4_NDX_DELEV02`, −$401.51/event on certified cash NDX) · MC-38/MC-51 CLOSED as growth/sizing
(`G2_F3_VOLSIZE01`; **V2 tail-only PASS banked**: maxDD 18.69 % vs 24.82 %) · MC-53 CLOSED FAIL 0/4
(`G2_F8_DUO`) · MC-43/44/45 EVENTTIME family CLOSED (`G2_F8_DUO`) · MC-46 AUCTREV CLOSED at
certification (`G2_F7`, R_c alone after the F9 re-adjudication; the 15:50-break FACT stays banked)
· MC-54 leg 1 = **ERABREAK01 doctrine line** (intraday-vol era break p 0.0011, binding).
**`G2_F9_P1_SYMCERT`**: incumbent half-passed its own battery — R_d shift-null PASS at the 100.0th
percentile (p 0.0009), R_a concentration FAIL at 236.8 % → **R_a demoted to a CLASSIFICATION rung
for every object**; a quiet shadow quarter is expected behaviour, not decay.

**Still OPEN:** MC-54 legs 2–4 (cheap, NQ-1-min-only) · MC-41 rebound-side rule (the +9.62 pp
fact stands; afternoon-short formulation dead) · MC-42 (banked, no rule) · MC-48 (LOW) · MC-55
(parked until an engine trades 14:00–16:00) · MC-39 (DATA-GATED: VX 1-min has no free backfill) ·
MC-52/56 (blocked on the P-1 reserve) · MC-35 (blocked-as-rescue).
**Closed 2026-09-06 (Formal Wave 4):** MC-50 macro leg **NULL** — premium absent, negative in
3/3 eras, negative even gross (`G2_F10`, G00048); earnings leg stays demoted. ROLL02 killed
exec-series roll gating and re-measured the pooled blackout at $93,173 (G00047).

**Closed 2026-09-06 (Formal Wave 5):** MC-54 leg 2 **NOT-IDENTIFIED** — fixed-window
deseasonalization is 99.5% collinear with raw first-hour vol (VIF 92.9); design dead, scope open
(`G2_F11`, G00052). MC-55 **REFUTED, POWERED, INVERTED** — post-FOMC RV *expands* ×5.66, not
crushes (`G2_F12`, G00053). MC-56 **not run** — its 2022+ VXN↔NQ join is the P-1 reserve.

**Closed 2026-09-06 (Formal Wave 6, workflow `wf_18c63c94-84c`):** Both survivors of the Wave-5
skeptic FAILED, no candidate advanced. **MC-57 ZB rates-state = POWERED+IDENTIFIED NULL** — ZB
makes the NQ vol forecast −4.36% worse (VIF 4.45, n=364); **the last "new raw surface" flag is
retired and MC-35/P1-conditioning stays BLOCKED** (`G2_F13`, G00054). **MC-58 rebound =
CLOSED-AS-GENERIC-MR permanent** — the washout-rebound long loses to the same trigger without the
breadth condition (`G2_F14`, G00055). 🔴 **Frontier assessment: the $0/seal-respecting
incremental-alpha search is credibly EXHAUSTED** — 56 trials, 0 live candidates, and now the one
genuinely new surface is inert on even the vol forecast. Remaining EV is NOT more cards: it is
(1) the execution-cost measurement now in flight (roll-crossover sampling → the MNQ spread + roll
cost, Level-B realized-P&L for the live book), (2) forward evidence accrual (shadow ledger +
sealed ≥2026-08-01), (3) owner-gated SPEND that would open a new surface (Databento execution
falsifier; GAMMA00 options/dealer-state) — an owner decision, not an autonomous one. A new card
wave against the parked LOW bench would be activity, not EV.

**NEW cards, survived the Wave-5 skeptic (`runs/G2_WAVE5_CARDS_20260906/`) — BOTH NOW CLOSED by Wave 6:**
- **MC-57 — rates-complex intraday STATE for NQ (ZB), TRIAGE-HIGH.** ZB 1-min just extracted
  (923 sess). Decision role locked as RISK-SPEC / REGIME-ROUTING (second-moment conditioner),
  never lead-lag/direction (clears ESNQ-null + swing-park). 🔴 **Skeptic amendments are binding
  before it can run:** (1) the HAR+**VXN** baseline consumes the P-1 reserve → **VXN gated OUT of
  both arms**; (2) ZB parquet is additively back-adjusted → **points basis, never percent**
  (DELEV01). Frozen primary: OOS QLIKE/Diebold-Mariano improvement of HAR(NQ-RV)+macro-flags
  augmented with pre-declared ZB terms, ZB∩NQ 2022-12→2026-05-31 (n≈860), MDE-first.
- **MC-58 — MC-41 rebound (long) side, TRIAGE-MED.** Modern leg only (2023→2026-05, n≈154; era
  leg WOULD consume the one-shot pre-2022 $TICK read — gated out). 🔴 **Skeptic's binding caveat:
  the breadth increment's only measured prior (+$143/ev) already fails its control at n=263, so
  the modal result is an inconclusive middle UNDER MDE — "permanent closure of the rebound side"
  is licensed ONLY in the control-wins/≈0 cell; an underpowered middle must NOT be labeled
  closed** (print B1 mean-MDE and B2 increment-MDE before any return table).

**Governance (Wave-5 BBO check, `BBO_GOVERNANCE_MEMO.md`):** the "~129 extractable NQ-BBO
sessions" premise **dissolved under measurement** — 187 census entries are file dates (29 Sundays
fold), 104 already extracted across 3 substrates, true unextracted = **57 sessions; only 2 free**
(2026-06-19, 07-03, both burned-window early-closes, legacy-grade); **55 are frozen-pool members**
(nested 19⊂141⊂160-of-168; ESNQ-15⊂all). Ruling: HOLD on the 55. 🔴 **Exposure found & recorded:
the 2026-09-06 NQ-BBO extraction had materialized SPREAD content on `2026-05-05`, a 19-pool
member** — annotated in `ALPHA_EVIDENCE_CLASSIFICATION.md`, owner-flagged; returns-falsifier
status preserved (spread ≠ outcome), spread-conditioned falsifier compromised for that one date.

**The SWING band lane — TWO READS DONE 2026-09-06, LANE PARKED: its premise is
FALSIFIED-AS-ARGUED** (`G2_SWING01` G00044-46 bucket tables; `G2_SWING02` G00049-51 full-series
weekly overlays — the design the lane's own arithmetic demanded). ⭐ **The measured fact that
kills the premise:** at the 0.0167 family bar and 80 % power with a dependence-preserving null
(~1.3× wider than iid), the detectable edge on the deep spine is **~0.66–0.78 annualized
Sharpe**, not the premised 0.45 — META_ADVERSARY's t≈2 arithmetic ignored the bar+power factor
(3.23) and the null width. VX slope / COT flow / ER-continuation all UNDERPOWERED at read 2
(MDE 3–11× observed); S1 additionally DEFECT (an expanding-window z cannot demean a
regime-shifted signal — the 2008-09 backwardation era leaves a standing −0.25 tilt). **Revival
requires genuinely new observables, or a single-primary design that honestly reaches ~0.5-Sharpe
sensitivity.** Unquotable color, 2-of-2 reads, no gate passed: ER-continuation flips sign
pre/post-2010. Standing constraints unchanged: ratio/cash basis (`G2_F3_DELEV01`),
TSMOM/XSMOM/H7 scopes closed, H1's 2022+ implied-vol reserve untouched (asserted in both reads).

**Replenishment check:** MED tier ≥ 3 → no scan trigger; the binding shortage is *execution of
the registered swing lane*, not new cards.

<details><summary>Health (2026-08-29, post-Formal-Wave-1 — historical)</summary>

**28 live cards** (37 − 4 killed − 4 closed-by-test − 1 measurement-done): 13 MED (bench),
12 LOW (parked), 1 FORWARD-QUEUED, 2 METHODS, 1 DATA-GATED, and MC-35 **BLOCKED-AS-RESCUE** on
P1 (needs a new surface). **Replenishment check: 13 MED ≥ 3 → no trigger; but the HIGH tier is
now EMPTY — the next world-scan wave should target archetypes orthogonal to the wave-1 kills
(short-side mechanisms, event-time/path representations, execution-state) per directive §65.**

</details>

## Formal Wave 2 — CLOSED (2026-08-29)

CLAIMS01: 2 claims SUPPORTED-BEYOND-GEOMETRY (ON-touch, IB-extension — banked as facts, no
strategy licensed) · 4 GEOMETRY-EXPLAINED (incl. the 80% rule at 42.6%) · 1 REFUTED. SWEEP01:
NULL both directions (no reversal edge in the level, no momentum-tell). **MC-07 CLOSED** (its
core claim is geometry). **MC-08 CLOSED at formulation. MC-04 weakened** (extension is real but
the direction claim is definitional — a policy corollary would need a new mechanism).

## Bench (MED, post-Wave-2)

MC-14 pullback policy (parked — needs a living base engine) · MC-04 residue (needs a direction
mechanism, not a rate) · MC-13 late-day hedging (needs a decay story vs H4B's death) · remaining
MED rows per verdicts file — **none currently clears the "materially different from a measured
failure" bar without new representation input. → §65 trigger: REPRESENTATION-SHIFTED SCAN WAVE 2
launches now** (short-side asymmetry, event-time/path topology, execution-state, overnight
structure — archetypes orthogonal to everything measured so far).

## Conversion funnel (§70 — cumulative)

| stage | count |
|---|---:|
| raw leads discovered | ~230 |
| deduped mechanism cards | 37 |
| survived skeptic (MED+) | 18 (+1 fwd, +2 methods, +1 data-gated) |
| formally preregistered | 6 runs / 8 trials (G00015–G00020 + wave 2 pending) |
| information survivors | **0 of 4 alpha mechanisms** (wave 1) |
| after-cost survivors | 0 |
| measurements banked | 2 (EXEC01 cost truth; MAE01 intrabar bound) |
| forward-queued | 1 (LIQREV01) + shadow roster |

**Bottleneck statement, CORRECTED per META_ADVERSARY_01 (2026-08-29):** the earlier claim "what
fails is information content" was an over-read. Honest version: **the intraday gate battery is
blind below ≈ annualized Sharpe 1 at the tested Ns** (a true Sharpe-0.5 edge passes < 10% of the
time); the programme has near-zero information about the modest-edge band, which is *unexplored,
not empty*. The one band where t=2 is reachable at Sharpe ≈ 0.45 — **the 3-session-to-3-month
swing band on the 1,043-week deep spine — is untested across all 56 cards** and is now a
registered lane (mechanism-first; TSMOM/XSMOM exact scopes remain closed; new observables or
representations required).

## Standing corrections from META_ADVERSARY_01

- **MC-49 kill rebased**: killed on its own evidence quality (one 59-day self-flagged ICT repo),
  NOT on SWEEP01's closure — SWEEP01's report explicitly does not cover overnight sub-levels.
  Scope language corrected here; the kill stands on the weaker, honest ground.
- **Anti-tail pipeline fixed (charter §59 restored)**: a candidate PREREGISTERED as a TAIL-CLASS
  object routes concentration as a CLASSIFICATION (crisis-concentration expected), and
  portfolio-marginal runs BEFORE the concentration rung can kill it. AUCTREV's kill stands (it
  was preregistered as a fast-reversion broad edge and its mechanism was falsified by R_c).
- **Two reserves flagged to the OWNER as possibly negative-EVI** (owner decision, not mine):
  (i) the 2022+ implied-vol pristine window guards a confirmation for a lane (H1) measured NULL,
  while blocking the axis whose decisive era it is; (ii) the blind BBO pools guard a falsifier
  lane closed twice by power, while the binding cost row rests on 5.1% overlap.
- **Symmetric certification of the incumbent** preregistered as `G2_F9_P1_SYMCERT` — the
  highest-EVI unplanned action; see spec.
