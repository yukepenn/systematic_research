# Directive v4.0 §45 — required end-of-pass answers

2026-08-24. Every answer carries a status token. Where evidence cannot decide, the answer is
UNKNOWN and rivals are kept. Runs: `OTR_R11_INVERSE` (+ amendments 1–4),
`OTR_R12_PARAM_INTERVENTION`, and the R13–R24 readouts they authorise.

---

**1. Which original-trader facts are truly direct?**
The A1–A5 panel values 90/179/5/10/10 and the strategy name; NQ 1-minute, Qty 1; the
machine labels; the daily/weekly report cell values themselves; the author's own statements
(incl. "fully automated", "amateur"). Newly added this pass, and directly derivable rather
than modelled: **commission $4.18/RT in 2023, $5.68/RT in Feb-2025, $0 in the 2025 weekly
reports** (each read off the report's own arithmetic). See `CLAIM_REGISTRY.csv`, 141 rows.

**2. Which CAND2 claims survive the conditional-label correction?**
Only IMPLEMENTATION_PARITY (Python ↔ NinjaScript ↔ NT8 engine). "Verified model class" and
"42/42 cent-exact ground-truth labels" are **retired**. CAND2's exit rule and its D-gate are
now both partly falsified (Q13, Q6). What survives intact is the T1 stop-and-reverse
skeleton and the B1 first-bar drop.

**3. What does NT8 Daily / Exit-Time grouping actually mean?**
**CALENDAR date of the exit timestamp** — REPRODUCED. The session-date reading yields 8/11
days and **zero** global paths; the calendar reading yields 11/11 and a global path. The
discriminating trades are the three that both enter and exit inside 18:00–23:59.
A previous note recording this as NOT SEPARABLE was correct about the inclusive-exit model
and wrong about the trader's.

**4. How much identification do MAE/MFE/ETD add?**
Decisive. ETD is redundant (`ETD = MFE − net profit`, 90/90). MAE and MFE are path
statistics that no P&L-matching trade subset can fake, and the $5-tick lattice makes their
daily sums **exact integers**. They are the reason 11 days collapse to one trade path
instead of many. Without them the whole reconstruction below is unreachable.

**5. Which Solar event universe reproduces every visible daily aggregate?**
**T1 only.** All six universes were tested under both exit rules; every solvable day
everywhere solves with `min_extra = 0`.

**6. Which events are MUST_TAKE / MUST_SKIP?**
All of them, for the recovered window: the global solution fixes every one of the 105 T1
decisions in 2023-01-03…17 (89 TAKE, 16 DECLINE). Status **INVARIANT_LABELS**, conditional
on (T1-only, STRICT, calendar rows) — not observed labels.

**7. Can T1-only still survive?**
Not only survives — it is the answer. Adding T2 or T3 entries never creates an explanation
and never rescues a failing day.

**8. Do T2E/T2L/T3 explain the A3-A5 intervention?**
In event space, yes and asymmetrically: the retune moves **T3 by +38.6 %** and **T2 by only
+3.0 %**, while A3/A4/A5 are *exactly* invisible to T1 (Jaccard 1.000000). Attribution:
A4→T3, A3→T3, A5→T2 only, A2→T1 timing jitter. So the missing 2025 layer — if there is one —
points at **T3/strengthening, not "pullback"**. This does not transfer to 2023, where the
inverse proves T3 entries are unused.

**9. What is the most defensible 2023–2025 original strategy after this pass?**
For **2023**: an always-in **stop-and-reverse machine on Solar T1 flips**, strict exit
(exit only on a genuine flip), no pullback layer, no strengthening layer, no fixed stop,
flat only at session close and at rare suppressions. For **2025**: the same skeleton plus a
documented 65-point initial stop and a suppression layer that is not yet identified; the
exit rule is **not separable** there (Q13).

**10. How close is it to the master?**
On the only cent-level evidence we have — the 11 visible daily rows — it is **exact**:
89 trades, every one of 88 report cells reproduced, cumulative net $8,032.98 matching an
unconstrained cell. Against the approximate screenshot-derived EARLY_LONG master
(n≈4351, net≈$292k) the best current variant is +5.2 % on count and −11 % on net. The
cent-level result is the stronger evidence (§48); the master figure is a rounded reading.

**11. Residual: data/contract/roll vs missing logic?**
**Not data.** Contract/merge is analytically excluded for Jan-2023 (no roll in window; P&L,
MAE and MFE are all differences, so a back-adjustment offset cancels identically), and the
90/90 MAE/MFE certification proves our bars reproduce NT8's High and Low, not just closes.
The residual is **missing logic**, specifically in the suppression layer.

**12. Does the late-2025 machine split survive controls?**
Yes, and it is large: on 28 standalone weekly windows the dev machine fits at mean §40
distance 0.280 / +8.8 % count error, the hp machine at 0.422 / +41.1 %. Still **INFERENCE**
as to *what* the machine label proxies.

**13. What remains unknown about the exit rule and the 65/75 stop group?**
The **exit comparison is genuinely era-split evidence**: in 2023 STRICT is the only rule
that admits any global path (INCLUSIVE gives zero); on the 2025 weeklies INCLUSIVE is
*marginally better* (0.376 vs 0.389 with the 65-pt stop). Both are kept alive for 2025 per
§6. The 65-pt stop is retained for 2025 on independent evidence and is **FALSIFIED for
2023** (70–200 pts, 26 configurations, zero solutions).

**14. What explains 2025-02-27 without invention?**
Nothing yet. R10 falsified the TrendVector-cycle fast machine; no replacement was invented.
Status **UNRESOLVED_ANOMALOUS_BUILD**.

**15–16. Is the 2026 VF block one composite panel? Which frames are the same strategy?**
Measured from scrollbar geometry across 22 frames (612 transcribed rows): verdicts **A and B**
— mostly one long composite parameter list seen at different scroll offsets, plus genuine
version changes; leaning **against** "distinct strategies", with one cluster **D**
(unresolved). See `vwap_flux_family/2026_PANEL_TOPOLOGY.md`.

**17. Which VWAP lifecycle is best supported, and by what?**
**UNKNOWN — reopened.** ACTIVE-anchor was previously recorded as solved; ninZa's public
pages describe segmented "most recent / previous / earlier" windows. Our morphology
measurements still favour ACTIVE but they compare our model against our model, not against
the vendor. A third reading (sliding window) and a fourth (band-refresh) are also admitted.
The min-max rail formula stays rejected — and that rejection is now shown to be
**lifecycle-invariant**.

**18. Does fixing signal-vs-entry Qty/Split semantics improve VF?**
Not yet measured. The defect is **confirmed by code reading** (`run_r7_signal_id.py`
increments the counters only on executed entries/SAR), the corrected two-layer architecture
is specified (`VF_SIGNAL_GENERATOR_v2.md`, `VF_WRAPPER_v2.md`), and every R7/R8 conclusion
that inherits the defect is named there.

**19. Manual CloseThreshold semantics vs H1a?** Both kept alive. That H1a scores better is
**not** evidence of vendor semantics; the poor showing of the manual-literal reading is
recorded as possible evidence that our cloud/trend/wrapper is wrong instead.

**20. How much of the 2026 gap remains?** Unchanged this pass — the VF work was
architectural, not numerical, and its numbers are provisional pending the Layer-A rebuild.

**21. Is the −42k week still a discriminator?** Yes, untouched.

**22. Evidence of licensed VF use vs reimplementation?**
Materially weakened this pass. **EV-039's premise does not hold**: no frame in the corpus
shows Tick Replay state *and* `BidAskPrice_RealVolume` together — Tick Replay is legible only
in seven Feb-2025 Solar-era frames, and every 2026 frame lacks the row entirely. The
conjunction was assembled across a family change and twelve months. Additionally the vendor
manual explicitly invites user-written wrappers ("you can rely on the signals below to build
your own strategy"), so a custom wrapper is **not** evidence of reimplementation. H1–H5 all
live; "zero artifacts on our machine" is retracted as invalid evidence.

**23–25. What would buying VWAP Flux resolve, and is $300 justified now?**
It would resolve vendor-level rail formula, lifecycle, and Signal_Trade timing. It would
**not** resolve whether the trader's build follows vendor semantics (V-102), which is the
binding uncertainty. **Verdict: PREMATURE.** The free surface is not exhausted — the VF
re-audit identified unexploited free measurements (rail extraction from the vendor's own
archived manual PNGs; the vendor's published videos), and the Layer-A rebuild has not run.
Purchase gate stays **CLOSED**.

**26. Any reason to buy another order-flow product?** No.

**27. What original-strategy mechanisms remain missing?**
(a) The **suppression layer** — 16 declines out of 105 decisions in 2023, and no threshold
rule over 15 observable state features reaches ≤2 errors; the incumbent D-gate scores
87/105. (b) Whatever drives the 2025 over-trading (+41 % on hp weeks). (c) The 2025-02-27
build. (d) The 2026 trigger composition.

**28. Next highest-EVI experiment.**
Extend the global inverse to the **Feb-2025 daily table** (OTRIMG-0026, 2 days with full
MAE/MFE) — the same machinery, a different era, and the only other cent-level daily surface
in the corpus. It would test directly whether the 2023 mechanism (T1-only, strict, no stop)
still holds after the risk stack appears, and it needs no new data and no purchase.

---

## Honest ledger of preregistered predictions that FAILED this pass

| prediction | outcome |
|---|---|
| STRICT moves the master count/hold toward target (amendment 1) | **FAILED** (+5.2 %→+7.8 %); confounded by a gate fitted under INCLUSIVE |
| every D-gate component is necessary (amendment 2) | **FAILED** — 3 of 6 never bind; the C-block scope is falsified |
| an early fixed stop explains the three hard days (amendment 3) | **FALSIFIED** — 26 configurations, zero solutions |
| a global path exists under the calendar rule (amendment 4) | **PASSED**, but only after the reporting window was extended past 17:00 — the first attempt failed for a boundary reason, not a model reason |
| T1 near-invariant under the retune, J > 0.97 (R12 P1) | **FAILED as written** (J = 0.9053); the intended claim held far more strongly (A3/A4/A5 → J = 1.000000), the mis-specification was mine |
