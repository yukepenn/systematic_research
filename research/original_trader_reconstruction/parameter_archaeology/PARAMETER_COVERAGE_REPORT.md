# PARAMETER COVERAGE — the answer to directive v5.0 §53

> §53: *"Of every visible mature-2026 parameter, what fraction has a defensible origin/role?
> List every still-unexplained row. Do not hide unknowns."*

Companion files: `ALL_VISIBLE_PARAMETER_ORIGIN_MATRIX.csv` (105 slots),
`build_matrix.py` (reproduces this arithmetic), `UNEXPLAINED_PARAMETER_LEDGER.csv`.
Sources: `vwap_flux_family/2026_PANEL_TOPOLOGY.md` (committed FACT tables),
`vwap_flux_family/2026_panel_rows.csv` (612 measured rows),
`runs/OTR_R28_2026_ARCHAEOLOGY` (extent series).

---

## 1. The headline number

| August-2026 panel | rows |
|---|---|
| measured extent | **~523** |
| NinjaTrader-8 standard tail (platform, not his) | 26 |
| **his own custom rows** | **~497** |

| coverage of those ~497 custom rows | count | share |
|---|---|---|
| **label photographed** (§43 LEVEL-A eligible) | **13** | **2.6 %** |
| photographed as a value, label never photographed | 66 | 13.3 % |
| **never photographed in any form** | **~418** | **84.1 %** |

**All 13 labelled rows are the VWAP Flux block**, and nothing else. Every other custom parameter
the trader has is either a bare number on screen with no label, or was never on screen at all.

---

## 2. Why this cannot be improved by more research

§5 is binding: a component may not be identified from numeric coincidence. §43 LEVEL A requires
a direct class/product name or a near-exact property-label/order/UI match.

For the 66 value-only slots the labels **do not exist anywhere in the corpus**, and the owner has
confirmed the 164 images are complete. So no amount of vendor research, and no purchase, can
produce a label match for them. The only §5-admissible route left is a match on **control-type
sequence + group-separator position + values**, which is why those sequences are recorded as the
primary fingerprint in the matrix:

| block | n | control-type sequence (the matchable fingerprint) |
|---|---|---|
| HEAD-A | 15 | `GRP·enum·enum·GRP·chk·num·num·num·num·num·num·chk·num·num·num` |
| BANK-1 | 2 | `GRP·chk×8` mask `U,C,C,U,U,C,C,C` |
| BANK-2 | 2 | `GRP·chk×7` mask `U,C,C,U,U,C,C` — **identical first seven to BANK-1** |
| MIDDLE | 21 | `num×4·GRP·chk×4·num·num·chk·num·num·num·GRP·num×4·GRP·chk×5·num·chk` |
| VF-HEAD | 11 | `num·chk·chk·num·num·num·num·num·num·num·chk` |
| VF13 | 13 | `enum·num·num·num·enum·num×8` — **identified** |
| PREVF-TAIL | 15 | `num×4·chk·chk·GRP·num·GRP·chk·num·GRP·chk·num·num` |

BANK-1 and BANK-2 having identical seven-state masks is the strongest structural hint available:
**the list contains repeated blocks.** That is consistent with a per-sleeve or per-condition-set
architecture, and it is the one shape a vendor meta-engine would also produce.

---

## 3. Coverage runs OPPOSITE to the directive's priority order

§50 puts the mature 2026 build first and 2023 last. Measured observability is the reverse:

| build | date | extent | custom rows | photographed | **coverage** |
|---|---|---|---|---|---|
| **pre-VF** | 2026-01-30 | 77 | ~51 | 15 (PREVF-TAIL) | **~29 %** |
| VF arrives | 2026-02-13 | 211 | ~185 | 13 (VF13) | ~7 % |
| head visible | 2026-02-20 | 215 | ~189 | 28 (HEAD-A + banks) | ~15 % |
| middle visible | 2026-06-05 | 408 | ~382 | 21 (MIDDLE) | ~5 % |
| **mature** | **2026-08-14** | **523** | **~497** | **15** | **~3 %** |

**The mature August build is the least observable object in the entire corpus.** The best-observed
2026 build is the *earliest* one — 2026-01-30, at ~51 custom parameters, an ordinary hand-written
NinjaScript strategy size, of which we have nearly a third.

This does not mean abandon August. It means August conclusions will carry ~3 % parameter support
and must be labelled accordingly, while the Jan-2026 build — the direct ancestor of the mature
one, and the last build before VWAP Flux — is where parameter archaeology has actual leverage.

---

## 4. The growth curve, and what it does and does not license

From `runs/OTR_R28_2026_ARCHAEOLOGY`: ~51 custom rows on 2026-01-30 → ~497 on 2026-08-14, a
**10× expansion in 6.5 months**, with four resolvable build events (>4σ):

| week ending | Δ rows | note |
|---|---|---|
| 2026-02-06 | +99 | the list more than doubles |
| 2026-02-13 | +35 | VF13 (13 rows) arrives — **plus ~22 unphotographed rows** |
| 2026-03-14 | +75 | +34 % in one week |
| 2026-07-10 | +79 | weakest of the four |

Two consequences, both registered before readout:

1. **Adding VWAP Flux was not a drop-in.** The 13-row VF block arrived inside a 35-row event, so
   ~22 rows of something else came with it — most plausibly its wrapper. Never photographed.
2. **Growth is DECOUPLED from behaviour.** The −$42,235 catastrophe week (2026-03-27) sits on a
   panel delta of −4.0 rows (−0.58σ): *no build change at all*. A ~500-row list that grows
   +12.7 rows/week while the traded fingerprint stays flat is more consistent with options, plots,
   alerts, per-sleeve toggles or disabled blocks than with active trading logic.

**Consequence for §19.** §19 asks which visible unknown parameter groups account for the
2,730 → 1,705 → 1,214 acceptance gap. The premise — that the suppression layer is
photographed-but-unrecognised — is now weak on two independent counts: only 13 % of his custom
rows are photographed at all, and panel growth does not track behaviour. §19 should not be read as
promising that the missing filter is sitting in the corpus waiting to be recognised.

---

## 5. Consequence for the purchase gate (§34/§35/§36)

§35 sets the gate as: *"Purchase discussion is premature while a large fraction of the final panel
is still unexplained."*

**That condition can never be satisfied.** 97.4 % of the mature panel has no label evidence and
the corpus is fixed. Deferring the purchase decision to "parameter-origin closure" defers it
forever. The decision must therefore rest on other grounds — which is what `PURCHASE_GATE_v2`
already did, and its four measured findings are untouched by this pass.

This is reported as a structural fact about the evidence, not as an argument for or against
buying. §54's answer is given in the campaign report.

---

## 6. Every still-unexplained row

All 66 are enumerated in `UNEXPLAINED_PARAMETER_LEDGER.csv` with block, slot index, control type,
visible value, capture date and the reason the label is unavailable. Nothing is hidden and nothing
is filled in from imagination. Summary by block:

| block | unexplained slots | dates | status |
|---|---|---|---|
| HEAD-A | 15 | 2026-02-20, 2026-04-29 | UNEXPLAINED — top of list, only two frames ever at scroll 0 |
| BANK-1 / BANK-2 | 4 | 2026-02-20 | UNEXPLAINED — repeated-block evidence |
| MIDDLE | 21 | 2026-06-05 | UNEXPLAINED — the only middle-scrolled frame in the corpus |
| VF-HEAD | 11 | 2026-02-13 … 2026-08-14 | UNEXPLAINED — mutable rows above VF13 |
| PREVF-TAIL | 15 | 2026-01-30, 2026-02-06 | UNEXPLAINED — best-covered block, pre-VF build |
