# OTR_R28_2026_ARCHAEOLOGY — report

Spec + amendment 1 preregistered before readout (`spec.yaml`, `amendment_1.yaml`).
Directive v5.0 P1 / §21 / §22 / §24 / §26 / §30 / §31 / §41 / §53.
Code: `vwap_flux_family/src/run_r28_archaeology.py`, `run_r28b_lattice.py`, `run_r28c_lattice.py`.

No backtests were run. No new data. Nothing from the locked-forward window.

---

## 0. The constraint that reshapes directive v5.0's P1

§21 asks to "stitch the complete June–August 2026 parameter panel" and §53 asks what fraction of
"every visible mature-2026 parameter" has a defensible origin. The already-committed scrollbar
measurement answers a prior question that changes both:

| era | panel extent | rows photographed | **never photographed** |
|---|---|---|---|
| Feb-2026 | ~211–224 rows | ~41 | **~80 %** |
| **Aug-2026** | **~523 rows** | **~30** | **~94 %** |

There is no coverage to stitch. §53's denominator is therefore **not** "every parameter he had" but
"every parameter we can see", and the two differ by a factor of ~17 in August. Stated plainly so the
parameter-origin matrix is not mistaken for a map of his strategy.

What *is* recoverable is the panel's **length over time**, which is measurable in every frame and
covers the unphotographed region. That is C1/C2 below.

---

## 1. C1 — the extent series resolves four discrete BUILD EVENTS

`E = (T/21.7)·(T/h)` with ±1 px thumb-edge noise propagated analytically
(`out/panel_extent_series.csv`, `out/build_events.csv`).

**P1_1 PASS.** σ(2026-07-31, h=35) / σ(2026-02-13, h=90) = **6.50** (predicted > 5). Late-2026
extents are far less certain than early ones; every conclusion below respects that.

**P1_3 PASS.** Four week-over-week deltas exceed +4σ. Under the preregistered decision rule these,
and only these, are build events:

| week ending | extent | Δ rows | n·σ | note |
|---|---|---|---|---|
| **2026-02-06** | 77 → 176 | **+99** | +56.7 | the list more than doubles |
| **2026-02-13** | 176 → 211 | **+35** | +11.9 | the week VF13 first appears |
| **2026-03-14** | 218 → 293 | **+75** | +14.4 | +34 % in one week |
| **2026-07-10** | 417 → 496 | **+79** | +4.8 | weakest of the four |

Everything else in the series is noise or marginal. In particular the +47 rows at 2026-07-31 is
**+2.27σ — not a build event**, because at h=35 a single pixel is worth ~15 rows.

**P1_2 FAILED as stated, and the failure is instructive.** One negative delta exceeds 2σ:
2026-04-13 → 2026-04-17, −18.6 rows (−2.53σ). That is the *only* frame pair where the pane
geometry changes drastically — OTRIMG-0136 has track height **681 px**, 33 px taller than any
other frame in the corpus. σ_T = 1 px is badly wrong for that pair. Recorded as a
**measurement confound at a geometric outlier, not as evidence that rows were removed**, and
OTRIMG-0136 is flagged as geometrically anomalous for all future use. The prediction is marked
FAILED rather than quietly rewritten.

### The 2026-02-13 coincidence is the useful one

The +35-row event at 2026-02-13 is the same week the VF13 block first appears (V4 in
`2026_PANEL_TOPOLOGY.md`: 0113/0115 end in the 75/20/46/30 run, 0117 onward end in VF13).
**The VF13 block is 13 rows. The build event is 35 ± 3.** So VF arrived *together with* roughly
22 further rows that are not VF and were never photographed. Adding VWAP Flux was not a
drop-in — it came with a wrapper.

---

## 2. C2 — build events versus behaviour: **R-DECOUPLED**

Aligning the four events against the 24-row weekly fingerprint (§40 fields, never net alone):

| build event | that week's fingerprint | next week |
|---|---|---|
| 2026-02-06 (+99) | n=111, wr 36.9, pf 1.11, hold 35.3 | n=62, wr 38.7, pf 1.23, hold 57.4 |
| 2026-02-13 (+35) | n=62, wr 38.7, pf 1.23, hold 57.4 | n=62, wr 43.6, pf 1.26, hold 56.6 |
| 2026-03-14 (+75) | n=76, wr 38.2, pf 1.21, hold 49.8 | n=67, wr 40.3, pf 1.23, hold 53.7 |
| 2026-07-10 (+79) | n=162, wr 38.9, pf 1.09, hold 38.7 | n=223, wr 38.6, pf 1.36, hold 40.2 |

The **largest single behavioural break in all of 2026 — the −$42,235 catastrophe week ending
2026-03-27 (wr 28.3, pf 0.36)** — falls on a delta of **−4.0 rows (−0.58σ), i.e. no panel change
at all.** And the +75-row build event two weeks earlier produced a fingerprint
(n=76, wr 38.2, pf 1.21) indistinguishable from its neighbours.

**Verdict: R-DECOUPLED** *as measured*. Panel growth and behavioural change are not aligned.

**CORRECTED 2026-08-25 (owner epistemic correction).** The original text continued "…a market event
meeting a fixed rule set, not a build regression". That over-reads the measurement. The extent
series measures the **total number of declared properties** and nothing else; a build change that
rewrites logic while leaving the property count unchanged is invisible to it, and ~85 % of the pane
is unobserved regardless. **"No visible panel change" is not "no change."**

**P2_2 consequence, registered in advance and now triggered:** the ~470 unphotographed August rows
**cannot be assumed to be trading logic**. §19's premise — that a visible-but-unrecognised filter
explains 2,730 → 1,214 — is weakened accordingly. A ~500-row list that grows +12.7 rows/week while
the traded fingerprint stays flat is more consistent with options, plots, alerts, per-sleeve
toggles or disabled blocks than with active suppression logic. This does **not** prove the
suppression layer is absent; it removes the reason to expect it is sitting photographed-but-
unrecognised.

---

## 3. C3 — the cent lattice reads out the live account

### P3_1 PASS — every 2026 Strategy Analyzer number is GROSS of commission

All 22 zero-commission records have **every** cell (net, gross profit/loss, largest win/loss,
net long/short) on the exact $5 lattice; not one off-lattice cell. Independently corroborated by a
committed FACT: "Include commission" is UNCHECKED in the NT8 tail of every bottom-scrolled frame.

Consequence, quantified: **1,854 trades, $204,395 reported across the 22 windows.** True net is
lower by 1,854 × c — between **−$2,188 (−1.1 %)** and **−$11,458 (−5.6 %)** over the commission
interval established below. His 2026 headline figures are overstated by that much.

*(Consistency check: the 17 windows through 2026-05-29 sum to exactly 1,214 trades — the figure
used as his trade count in the VF work. The two derivations agree.)*

### P3_2 FAIL, then amendment 1 — position size is NOT uniform

No (instrument, quantity, commission) triple explains the two June Trade Performance records under
a **uniform** position size. Their own residues show why — `382, 382, 264` on the four
single-trade cells. Solving the single-trade cells first (n = 1, so the unknown is a small integer
contract count):

| record | cell | reported net | contracts | gross | index points | ticks |
|---|---|---|---|---|---|---|
| OTRIMG-0152 | largest win | 6,798.82 | 1 | 6,800.00 | 340.00 | 1360 |
| OTRIMG-0152 | largest loss | −3,046.18 | 1 | −3,045.00 | 152.25 | 609 |
| **OTRIMG-0154** | **largest win** | **5,277.64** | **2** | **5,280.00** | **132.00** | **528** |
| OTRIMG-0154 | largest loss | −1,426.18 | 1 | −1,425.00 | 71.25 | 285 |

One commission explains all four, and every implied gross is an exact tick multiple.

**The scale-free finding (independent of knowing the commission):** OTRIMG-0154's largest winning
trade carries **exactly twice** the commission of the other three extreme trades. Commission is
proportional to contracts, so **that trade was twice the size**. Live position sizing is
non-uniform — while every Strategy Analyzer backtest in the corpus is qty 1.

**Instrument = NQ, and three rivals are eliminated:**
- **ES excluded on residues** — zero commissions in $0.01–$15.00 explain all four cells.
- **MNQ and MES excluded on physics** — they survive the residue test but imply the four extreme
  trades were 3,400 / 1,522 / 1,320 / 712 index points (MNQ) or 1,360 / 609 / 528 / 285 ES points
  (MES). Those are not week-scale index moves. Under NQ the same cells read 340 / 152 / 132 / 71
  points, which are.

**P5_3 PASS — commission is a congruence class, not a number.** Residues fix only the *product*
(commission per contract) × (contracts). The interval, per §6:
**c × q ≡ $1.18 (mod $5.00)**; if the three single-contract extremes were indeed 1 contract, then
**c ∈ {$1.18, $6.18, $11.18}**. A unique 2026 commission rate is **not** recoverable and must not
be claimed. For reference the established series is $4.18/RT (2023) and $5.68/RT (Feb-2025);
$6.18 is the member of the class nearest that trend, but this is plausibility, not evidence.

### P5_2 DISCRIMINATOR — fires for the multi-strategy model, with a caveat

Carrying the survivors into the aggregate cells (imposing m_long+m_short = m_all and
m_win+m_loss = m_all, both identities verified to the cent), NQ at c=$1.18 requires
**m_all ≥ 415 for OTRIMG-0152 (n=136) — at least 3.05 contract-round-turns per trade** — while the
same record's largest win and largest loss are single-contract trades.

**CORRECTED 2026-08-25 (owner epistemic correction).** What the 2× commission proves is that
**at least one executed trade/position carried a total quantity of 2** — i.e. account exposure was
not globally constrained to exactly one NQ at all times. That is new and important.

It does **not** prove multiple strategies caused it. All remain live: a single strategy trading
2 lots · scale-in · two overlapping sleeves · NT8 execution grouping merging fills into one
reported trade. The author's own statement that he ran several strategies is already independent
direct evidence and does not need this result to carry it.

No single (instrument, commission, position-size) story explains both records' aggregates *and*
their extremes comfortably — consistent with aggregation, but not establishing it.

**Named caveat / falsifier.** The aggregate leg assumes NT8 reports gross profit, gross loss and
the long/short split on the same net-of-commission basis as net profit. The exact accounting
identities justify that, but a flat per-*order* fee component (rather than purely per-contract)
would break the model without any multi-strategy explanation. That alternative is **not excluded**
and is recorded as live.

---

## 4. C4 — the 130-point hard stop is confirmed structurally

| observation | value |
|---|---|
| records with largest loss **exactly** −$2,600.00 | **18 of 24 (75 %)** |
| records strictly inside the cap | 4 |
| records exceeding it | 2 |

A 75 % spike on one exact value is a hard stop, not a distribution. −$2,600 / $20 = **130.00 index
points**.

**P4_1 PASS for RIVAL B (gap overshoot).** Both overshoots are one-sided and correctly ordered:

| record | loss | points | overshoot | fill type |
|---|---|---|---|---|
| OTRIMG-0162 | −2,820.00 | 141.00 | **+11.00 pts** | backtest (NT8 Standard fill: a stop fills at the bar open when the open gaps past it) |
| OTRIMG-0152 | −3,046.18 | 152.31 | **+22.31 pts** | live (gap **plus** real slippage) |

RIVAL B predicts live ≥ backtest. Observed 22.31 ≥ 11.00. RIVAL A (a drifting or different stop)
predicts no such ordering. The two apparent contradictions of the 130-point hypothesis turn out to
**confirm** it.

---

## 5. What this run established (status tokens per §43)

- **FACT** — 94 % of the August-2026 parameter list and 80 % of the February list were never
  photographed. §21's stitch target does not exist.
- **REPRODUCED** — four build events at >4σ; the catastrophe week has none.
- **INFERENCE** — R-DECOUPLED: panel growth is not aligned with behavioural change, weakening
  §19's premise that the suppression layer is photographed-but-unrecognised.
- **FACT** — all 22 SA records lie exactly on the $5 lattice with commission excluded; his 2026
  figures are gross, overstated by 1.1–5.6 %.
- **FACT** — one extreme trade carried exactly 2× the commission of three others: live position
  size is non-uniform. Instrument is NQ; ES excluded on residues, MNQ/MES on physics.
- **INFERENCE** — the aggregate/extreme tension supports §30's account-level model, with the
  per-order-fee alternative explicitly left live.
- **REPRODUCED** — the 130-point stop: 18/24 exact hits, one-sided overshoot, live > backtest.

## 6. What this run did NOT establish

- It did not identify a single vendor component. No LEVEL-A evidence was produced or claimed.
- It did not recover any unphotographed parameter row, and no method in this run can.
- It did not determine the commission rate — only a congruence class.
- It did not determine how many strategies the live account runs, only that "exactly one qty-1
  NQ strategy" does not fit.
