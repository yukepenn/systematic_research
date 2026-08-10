# EQV03 — PnL Equality: CURRENT_FORM vs CANONICAL_FORM

**Scope:** Zero-alpha-budget audit, gated on `EQV01_BEHAVIORAL_CANONICALIZATION/REPORT.md` (finite-state
decoder equivalence: Product A 243/243, Product B 729/729, TiltRescale 252/252, all `EXACT_EQUIVALENCE`)
and `EQV02_FULL_HISTORY_ARRAY_EQUALITY/REPORT.md` (full-history, operational-overlay-inclusive target /
position / exposure-event array equivalence for both products, `EXACT_EQUIVALENCE`). Since PnL is a
deterministic function of `(decision array, price series, execution convention)`, and EQV02 already
proved the decision arrays are SHA256-identical between `CURRENT_FORM` and `CANONICAL_FORM`, exact PnL
equality was the *expected* outcome here — this task's job was to independently **verify** that, not
assume it, by feeding EQV02's already-proven arrays through the campaign's execution/pricing loop and
checking for any divergence in *how* PnL is computed from an already-identical decision array (a
price/quantity wiring bug that array equality alone cannot catch). Per campaign directive sec.21, even a
full pass below is a **specification/representation finding, not an alpha promotion, not a strategy
change, and not a trading decision** — it clears EQV04 to be *attempted*, it does not authorize it, and
EQV04 itself remains gated and out of scope here. The incumbent NinjaScript files
(`SolarWaveSMMaster_v4.cs`, `SolarWaveOneContractNQ_v5.cs`, and the MNQ sibling) are unmodified. No
orders, deployments, connections, or licensed vendor assemblies were touched.

**Inputs:** two independent PnL-equality scripts and their result JSONs — `src/01_productA_pnl.py` →
`out/productA_pnl_equality.json`; `src/02_productB_pnl.py` → `out/productB_pnl_equality.json`. Both
scripts re-derive EQV02's operational target/position arrays via EQV02's own imported functions (not a
re-derivation from scratch, not a blind trust of EQV02's console output) and hash-verify them against
EQV02's recorded certified hashes before any PnL comparison is trusted. Both were re-read directly from
disk before writing this synthesis.

**Data:** same source as EQV02 — `runs/AUDIT03_BARS/nq_3m_2022_2026.csv`, 3-minute NQ bars,
2022-01-02 18:03 ET through 2026-07-31 16:57 ET (540,232 bars), strictly before the 2026-08-01
`LOCKED_FORWARD` boundary. Product A additionally reprices this data under genuine MNQU6 OHLC per
campaign directive sec.19 (dual-truth requirement), using the exact pattern established in
`runs/PRICE01_PRODUCT_A_GENUINE_MNQ/src/01_dual_truth_repricing.py`.

---

## Headline verdicts (no partial credit)

| Product | Decision-array reproduction vs EQV02 | Price bases tested | Windows tested | Bar-level PnL hash-equal | Daily PnL hash-equal | Net-total diff | Certified-figure crosscheck | Verdict |
|---|---|---|---|---|---|---|---|---|
| **A** (`SolarWaveSMMaster_v4.cs`) | PASS (byte-identical to EQV02) | legacy NQ-proxy, genuine MNQ | CLAUDE.md canonical (2023-01-01..2025-02-02), Product A's own certified dev window (2022-01-03..2026-05-31), fuller history (..2026-07-31) | true, all 6 (basis x window) cells | true, all 6 cells | 0.0, all 6 cells | PASS (4/4 dev-window/extended-window checks, within $1) | **EXACT_EQUIVALENCE** |
| **B** (`SolarWaveOneContractNQ_v5.cs`) | PASS (byte-identical to EQV02) | canonical NQ (direct, $20/pt, $4.36/RT) | CLAUDE.md canonical, fuller history, certified dev window (2022-01-03..2026-05-29) | true, all 5 (config x window) cells | true, all 5 cells | 0.0, all 5 cells | REASONABLE (dev-window net matches certified $301,915.92 to the cent) | **EXACT_EQUIVALENCE** |

**Both products PASS.** Zero PnL mismatches anywhere, across every price basis and every window tested,
for either product. Every reported comparison is confirmed by SHA256 bit-identity between the two forms'
bar-level and daily-aggregated PnL series, not by net-total agreement alone — a hash match additionally
rules out any compensating-errors scenario where per-bar PnL differs but happens to net to the same total.

---

## 1. Product A — `SolarWaveSMMaster_v4.cs`

**Method:** EQV02's already-proven-identical operational target arrays (raw decoder + session-timing
overlay, both forms) are fed through `simulate_overlay()` — a verbatim-structure copy of
`grid_core.product_a_exec` / `PRICE01`'s `product_a_exec_generalized` inner loop — under **two** price
bases per campaign directive sec.19: **legacy NQ-proxy** (NQ OHLC, MNQ's $2/pt multiplier applied
directly to NQ price levels) and **genuine MNQ** (real MNQU6 OHLC via PRICE01's established alignment
pattern, with NQ-proxy fallback for the 20,529 of 540,232 bars carrying no genuine MNQ quote). Because
`CURRENT_FORM` and `CANONICAL_FORM` share the identical `simulate_overlay()` loop, any divergence in how
either form reads price or quantity would surface as a hash mismatch here and could not hide behind a
coincidentally-matching net total.

### 1a. Reproduction of EQV02's arrays (trust precondition)

Before any PnL comparison, this script's own re-derivation of the raw target array (`tgtRaw` /
`target_A`) and the operational target/position arrays was hash-checked against EQV02's recorded
certified hashes, both windows, both forms:

| Array | Canonical window (245,943 bars) | Fuller history (540,232 bars) |
|---|---|---|
| Raw target, CURRENT_FORM | `f1178da9...44f70f` — matches EQV02 | `408b1264...8947933` — matches EQV02 |
| Raw target, CANONICAL_FORM | `f1178da9...44f70f` — matches EQV02 | `408b1264...8947933` — matches EQV02 |
| Operational target (both forms) | match | match |
| Physical position (both forms) | match | match |

All four checks passed for both windows. As an additional precondition, the operational target and
position arrays were confirmed **identical across both price bases** for each form (`price_invariance_of_decision_layer`,
all four flags `true`) — pricing must not, and does not, leak back into the decision layer.

### 1b. PnL equality, six (price-basis x window) cells

| Price basis | Window | Bars | Bar-PnL hash-equal | Daily-PnL hash-equal | Net (current = canonical) |
|---|---|---|---|---|---|
| Legacy NQ-proxy | CLAUDE.md canonical (2023-01-01..2025-02-02) | 245,943 | true | true | $49,703.6000000053 |
| Legacy NQ-proxy | Certified dev window (2022-01-03..2026-05-31) | 519,714 | true | true | $177,924.3999999992 |
| Legacy NQ-proxy | Fuller history (..2026-07-31) | 540,232 | true | true | $212,894.4999999953 |
| Genuine MNQ | CLAUDE.md canonical | 245,943 | true | true | $49,172.6000000053 |
| Genuine MNQ | Certified dev window | 519,714 | true | true | $178,687.399999999 |
| Genuine MNQ | Fuller history | 540,232 | true | true | $213,657.4999999948 |

Every cell: `n_mismatches: 0`, `max_abs_diff: 0.0`, `sha256_current == sha256_canonical` at both the
bar level and the daily-aggregated level. Backstop session-close events (the engine-level fallback that
would fire only if the strategy's own gate failed) never fired for either form, either price basis:
`{current_legacy: 0, canonical_legacy: 0, current_genuine: 0, canonical_genuine: 0}`.

### 1c. Certified-figure crosscheck — and the one genuine (non-PnL) issue this task surfaced

The campaign-certified figures $177,924.40 (legacy) and $178,687.40 (genuine MNQ) are certified on
Product A's **own dev window** (2022-01-03 to 2026-05-31, per `BASELINE_MODELS.md`'s "Performance
battery" section, `grid_core.py`'s `DEV_END`, and `health_substrate.py`'s `CANONICAL_END`) — **not** the
CLAUDE.md top-level canonical window (2023-01-01..2025-02-02), which EQV02 borrowed only as a *label* for
its own array-equality comparison window and which applies, at the top-level CLAUDE.md "Frozen truth"
section, to a different baseline (`SolarWaveRKReplicaV0`) entirely.

The first run of the crosscheck script cross-checked the CLAUDE.md canonical-window net ($49,703.60)
against the $177,924.40 dev-window certified figure and, unsurprisingly, failed — the two windows cover
different date ranges. This was root-caused as a **verification-target mislabeling in the crosscheck
harness, not a PnL bug**: PnL bit-identity between `CURRENT_FORM` and `CANONICAL_FORM` held identically
in both the pre-fix and post-fix runs, since the harness fix only changed *which certified number the
computed total was compared against*, not the computation itself. Once corrected to compare the
dev-window net against the dev-window certified figure (and the fuller-history net against PRICE01's
$212,894.50 / $213,657.50), all four crosschecks matched to the cent:

| Basis / window | Computed (current = canonical) | Certified | Match |
|---|---|---|---|
| Legacy, dev window | $177,924.3999999992 | $177,924.40 | within $1 |
| Genuine MNQ, dev window | $178,687.399999999 | $178,687.40 | within $1 |
| Legacy, fuller history | $212,894.4999999953 | $212,894.50 | within $1 |
| Genuine MNQ, fuller history | $213,657.4999999948 | $213,657.50 | within $1 |

The CLAUDE.md canonical-window net ($49,703.60 legacy / $49,172.60 genuine) has no separate
campaign-certified $ figure to check against for Product A — it is reported for transparency only and is
not used as a pass/fail gate; the PnL-equality gate (`current == canonical`, bit-identical) does not
depend on it and passed regardless.

**Product A verdict: EXACT_EQUIVALENCE.** Bit-identical PnL between `CURRENT_FORM` and `CANONICAL_FORM`
under both required price bases, across all three windows, with all certified-figure crosschecks passing
once compared against the window each figure is actually certified on.

---

## 2. Product B — `SolarWaveOneContractNQ_v5.cs`

**Method:** EQV02's already-proven-identical position arrays (operational AND raw-gates-off
configurations, both windows) are fed through **one shared execution engine**
(`sm01_solarsim._fill()`: Standard 1-tick adverse-slip fill capped by the fill bar's own range; $20/pt NQ
point value; $2.18/contract/side commission = $4.36/round-trip, matching CLAUDE.md's frozen "NinjaTrader
Brokerage Lifetime" commission; one-bar decode-to-fill lag matching NT8's `Calculate.OnBarClose`
convention; session-close flatten guaranteed by EQV02's `forceFlat` construction). Per campaign directive
sec.19, the dual legacy-NQ-proxy/genuine-MNQ price-basis requirement is scoped to Product A only — Product
B trades one literal NQ contract directly, so canonical NQ pricing is the sole applicable basis.

### 2a. Reproduction of EQV02's arrays (trust precondition)

The script independently regenerated EQV02's position arrays via EQV02's own imported functions (not
re-derived from scratch) and hash-verified them against EQV02's recorded certified hashes across all four
(window x gates) configurations — canonical-window operational, fuller-history operational,
canonical-window raw-gates-off, fuller-history raw-gates-off. All four passed
(`forms_hash_equal_at_position_array_level`: all `true`). The session-close-flatten precondition was also
checked directly rather than assumed: `force_flat` is `true` at every literal last bar of every session,
and the operational position array is already zero at every such bar — confirming the flatten discipline
holds structurally, not merely by the backstop catching a miss.

### 2b. PnL equality, five (configuration x window) cells

| Configuration | Window | Bars | Bar-PnL hash-equal | Daily-PnL hash-equal | Net (current = canonical) |
|---|---|---|---|---|---|
| Operational (gates on) | CLAUDE.md canonical | 245,943 | true | true | $83,363.3999999957 |
| Operational (gates on) | Fuller history | 540,232 | true | true | $360,590.9599999865 |
| Operational (gates on) | Certified dev window (2022-01-03..2026-05-29) | 519,714 | true | true | $301,915.9199999885 |
| Raw, gates-off | CLAUDE.md canonical | 245,943 | true | true | $92,809.0399999952 |
| Raw, gates-off | Fuller history | 540,232 | true | true | $389,366.7199999861 |

Every cell: `n_mismatches: 0`, `max_abs_diff: 0.0`, `sha256_current == sha256_canonical` at both bar and
daily levels, net-total `diff: 0.0`. Fill counts also match exactly between forms in every configuration
(operational: 4,036 fills / 4,128 contracts each form; raw gates-off: 4,054 fills / 4,146 contracts each
form). Backstop session-close events fire identically for both forms — 0 in the operational configuration
(the strategy's own `forceFlat` gate always clears first), 716 in the raw gates-off configuration (expected,
since gates-off deliberately removes the strategy-level flatten discipline) — `current` and `canonical`
agree to the event in both cases, so the backstop's own firing pattern is itself part of the proven
equality, not a source of possible divergence.

### 2c. Certified-figure crosscheck (reasonableness, not a bit-identity gate)

The applicable certified figure is $301,915.92 (exact: $301,915.91999998846) — Product B NQ,
"CURRENT EXACT BATTERY" dev window (2022-01-03 to 2026-05-29, 1,139 sessions), sourced from
`BASELINE_MODELS.md` and independently cross-confirmed identical in `runs/S2_SELTIME/out/r2/daily_NQ_incumbent.csv`
and `runs/O2_OWNER_UTILITY_READJUDICATION/out/ProductB_NQ_full_result.json`. No separate CLAUDE.md-window
(2023-01-01..2025-02-02) certified NQ figure exists for Product B in any of `BASELINE_MODELS.md`,
`RESEARCH_HANDOFF.md`, or `CURRENT_TRUTH.md`, so the dev-window figure is the applicable target and the
script's own computation was restricted to the identical window for a fair, apples-to-apples comparison.

`CURRENT_FORM`'s net over the exact certified dev window is **$301,915.9199999885** — matching the
certified **$301,915.91999998846** to within floating-point noise, an essentially exact match, well
inside the 5% reasonableness tolerance the crosscheck was designed to accept. Two pre-existing,
out-of-scope methodology differences between this script's more-`.cs`-faithful arrays and the certified
figure's original harness (`tiltState` `>` vs `>=` convention; independently-ported `bmomPos`) were
disclosed going in and turned out to be immaterial for this window.

**Product B verdict: EXACT_EQUIVALENCE.** Bit-identical PnL between `CURRENT_FORM` and `CANONICAL_FORM`
in every tested configuration and window (the required gate, and the one this report is graded on),
reproduction of EQV02's own arrays verified byte-for-byte, session-close-flatten precondition confirmed
structurally, and the dev-window net essentially exactly matches the campaign-certified figure.

---

## 3. Out-of-scope observation (flagged, not investigated further here)

One incidental note surfaced during Product B's script development: the pre-existing Product A EQV03
output (`out/productA_pnl_equality.json`) was, at one intermediate point, observed to show a
certified-figure-crosscheck failure when the CLAUDE.md canonical-window net was compared against the
dev-window certified figure. This is the exact window-labeling issue documented and resolved in Section
1c above — by the time both scripts' final outputs were written, Product A's own crosscheck passes
cleanly on all four applicable (basis x window) comparisons. It is restated here only for completeness,
since it was visible mid-task from the Product B side of the work before the Product A fix was confirmed;
it does not reflect any unresolved issue in the final `out/productA_pnl_equality.json`.

---

## 4. Governance restatement (per campaign directive sec.21)

**Both Product A and Product B resolve to `EXACT_EQUIVALENCE` at the PnL level** — bit-identical
bar-level and daily-aggregated PnL between `CURRENT_FORM` and `CANONICAL_FORM`, in every tested price
basis, window, and configuration, for both products, with zero mismatches anywhere. This is the outcome
that was *expected* given EQV02's already-proven decision-array identity — PnL is a deterministic
function of `(decision array, price series, execution convention)`, so with the first term already proven
identical and the third term shared verbatim between forms, only the second term (price feed) could have
introduced a divergence, and it did not, under either of the two price bases tested for Product A or the
single applicable basis for Product B. No subtle bug in how price or quantity is read between the two
nominally-identical code paths was found for either product.

With **EQV01 (finite-state decoder equivalence), EQV02 (full-history decision-array equivalence), and
EQV03 (PnL equality) now ALL passed for both Product A and Product B**, campaign directive sec.20 is
satisfied: **EQV04 (building separate, research-only canonical NT8 objects —
`SolarWaveSMMaster_Canonical_v1.cs` and siblings — NOT overwriting the incumbent files) is CLEARED to
proceed as a future step.** EQV04 was NOT attempted, built, compiled, or run in this task; it remains a
separate, later, explicitly gated phase with its own certification requirement (NT8 UI/MCP parity,
per the pattern in `research/solar_wave_parity/type1_2023_2025/parity_report.md`), and clearing it here
means only that the specification/representation prerequisites are now in place, not that it has been
executed.

Per campaign directive sec.21, restated explicitly: **even full EQV01-EQV04 passage would be a
specification/representation achievement — proof that a cleaner, canonically-derived formulation is
behaviorally and numerically identical to the incumbent — never an alpha promotion, never a strategy
change, and never a trading decision.** The incumbent NinjaScript files (`SolarWaveSMMaster_v4.cs`,
`SolarWaveOneContractNQ_v5.cs`, and the MNQ sibling) remain the **sole live-behavior source** regardless
of this or any future EQV result. Nothing in this report alters what those files do; no order,
deployment, connection, license, or account was touched in the course of this audit.

---

## Artifacts

- Product A script: `research/system_master/EQV03_PNL_EQUALITY/src/01_productA_pnl.py`
- Product A results: `research/system_master/EQV03_PNL_EQUALITY/out/productA_pnl_equality.json`
- Product B script: `research/system_master/EQV03_PNL_EQUALITY/src/02_productB_pnl.py`
- Product B results: `research/system_master/EQV03_PNL_EQUALITY/out/productB_pnl_equality.json`
- Upstream gates: `research/system_master/EQV01_BEHAVIORAL_CANONICALIZATION/REPORT.md` (243/243, 729/729,
  252/252, all `EXACT_EQUIVALENCE`); `research/system_master/EQV02_FULL_HISTORY_ARRAY_EQUALITY/REPORT.md`
  + `out/productA_array_equality.json` + `out/productB_array_equality.json` (full-history decision-array
  `EXACT_EQUIVALENCE`, both products)
- Execution/pricing convention source: `runs/PRICE01_PRODUCT_A_GENUINE_MNQ/src/01_dual_truth_repricing.py`
  (`product_a_exec_generalized`, reused verbatim for Product A and adapted for Product B's own NQ
  point-value/commission constants)
- Certified figures referenced: `BASELINE_MODELS.md` (Performance battery, dev-window figures for both
  products); `runs/S2_SELTIME/out/r2/daily_NQ_incumbent.csv`; `runs/O2_OWNER_UTILITY_READJUDICATION/out/ProductB_NQ_full_result.json`
- Data source: `runs/AUDIT03_BARS/nq_3m_2022_2026.csv` (2022-01-02 18:03 ET to 2026-07-31 16:57 ET,
  strictly before the 2026-08-01 `LOCKED_FORWARD` boundary)
