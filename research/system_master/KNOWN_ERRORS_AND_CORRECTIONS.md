# KNOWN_ERRORS_AND_CORRECTIONS (append-only)

1. **SM14 result script never committed** (V1, 2026-08-08). The one-lot numbers in
   `runs/SM14_ONELOT_DAYMARGIN/out/results.csv` came from an uncommitted inline script.
   Canonical spec-literal replay (`runs/SMV2A_DD_RECONCILE/smv2a.py`) differs ≤2.5%:
   MNQ net $27,974 vs $27,287; maxDD −$5,963 vs −$6,374; NQ $296,885 vs $298,040.
   Canonical numbers govern from 2026-08-08. Rule: no result without committed code.
2. **"22.5%/yr at P(DD>25%)≤5%" was single-method (L5)** (SM09). Corrected to the
   method-robust band 21.4-35.5%; honest headline 21.4% (worst method). Direction of
   the error was conservative-side by luck, not by design.
3. **Holdout language**: June/July 2026 was called "holdout" in V1 docs; it is a
   consumed, overlay-level quasi-holdout. NO globally pristine historical OOS exists
   through 2026-07-31. All V1 "holdout" mentions must be read with this correction.
4. **Tilt rescale 0.9296 → 0.9026** (V1, already disclosed in SM11 report): draft
   quoted from memory; frozen object was the formula; exact dev value 0.9026.
5. **SMV2H replacement gate mis-specified** (V2, 2026-08-08): daily-MEAN bootstrap
   cannot certify risk-shaped (DD/Sharpe) improvements — cells winning all 5 risk
   metrics at equal net score P≈0.5 by construction. Consequence: A-dominant family
   held at CHALLENGER despite dominating the board. Next wave gates on ΔSharpe/ΔCDaR.
6. **B-MOM daily artifacts carry C1 friction (2.872t/RT)**, a stress convention, not
   the actual NQ commission (0.872t). All B-MOM-containing numbers are therefore
   friction-conservative by ~2t/RT ≈ $10/trade.
7. **SolarWaveSMMaster_v1 order-engine arrangement bug** (SMV2M, 2026-08-08): v1
   attached to the MNQ execution instrument as PRIMARY and submitted index-0 orders
   from signal-series (BIP1) events. In the Analyzer engine the primary Position did
   not advance between successive signal-bar decisions, and with EntriesPerDirection=100
   the net-change engine re-entered every bar without bound (238,099 fills, single fills
   up to qty 1037, meaningless -$163M "net"). SolarWaveSMOneLot_v1 was immune only by
   accident: it never set EntriesPerDirection, so NT8's default (1) deduplicated the
   re-entries. RULE: multi-contract net-change masters MUST use the E10Master_v2
   arrangement — signals on PRIMARY, execution on the ADDED series via Positions[1] —
   which is parity-proven 0/540,232. v1 evidence preserved in
   runs/SMV2M_MASTER_BUILD/out/nt8_v1_failed/; corrected class = SolarWaveSMMaster_v2.
