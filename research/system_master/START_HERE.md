# START_HERE — historical campaign notes (superseded as a current-entry point)

**Current entry point: [`/README.md`](../../README.md) and [`/BASELINE_MODELS.md`](../../BASELINE_MODELS.md)
(repo root).** This file is retired from that role as of 2026-08-09 — its body below is one
wave stale (predates DEFECT 3, the `_v4`/`_v5` versions, and full-history parity certification)
and is kept only for its still-accurate historical framing of how the program's underlying
concepts (Solar, tilt, c1_50, B-MOM) fit together conceptually. Do not treat anything below as
current-state fact; check `/BASELINE_MODELS.md` for that.

## Historical campaign notes (2026-08-08, one wave stale — read `/BASELINE_MODELS.md` for current state)

_If a claim here conflicts with an older doc, CURRENT_TRUTH.md + SUPERSEDED_CONCLUSIONS.md win.
Nothing is "production ready" or "OOS proven"._

## The objects
- **Solar (E10)**: 13 copies of one dual-anchor trend rule (SolarWave V3 adaptive,
  VolMult 6..30) on NQ 3-min; position = round(10 × mean member position), 0-10 MNQ.
  The return backbone. Regime-local: pre-2022 it made nothing for 16 years.
- **HTF Tilt (SM08)**: ×1.25 exposure when Solar's vote agrees with the prior-session
  daily SMA50 state. Passed every gate; mechanism (not cell) confirmed 7/8 neighbors.
- **c1_50 (SMV2E)**: halve Solar SHORTS when HTF is UP. Passed (P=0.922, crisis
  retention 72%). Tilt + c1_50 together = **SOLAR_DUAL_HTF** (the current Solar core).
- **B-MOM**: intraday momentum — 09:30-anchored noise band (14-day same-slot mean) +
  RTH VWAP filter, long/short breakout, flat 15:57. Frozen W8-1 rule; causal execution
  audited (E2). Independent engine; losing-day correlation to Solar ≈ 0.04.
- **B1**: overnight long-bias sleeve. DEMOTED to experimental (failed ablation gate).
- **PORT_TILT_532**: V1's champion (0.5 tilt-Solar/0.3 BMOM/0.2 B1). Superseded.
- **DAYONLY_DUAL6040**: current champion — 0.6 SOLAR_DUAL_HTF + 0.4 vm(B-MOM), all
  day-only (flat before 16:45). Equal-vol: Sharpe 1.26, maxDD −$18.1k, worst mo −$6.9k.
- **OneLot**: exactly-one-contract day-only variants. FINAL holder = SM14 hysteresis
  (SolarWaveSMOneLot_v1.cs, registered in NT8). CHALLENGER = A-dominant policy
  (B-MOM first, Solar only at |T″|≥5; Sharpe 1.30 MNQ / 1.37 NQ; NQ DD −$47k vs −$58.5k).

## References vs challengers vs experimental
Reference (frozen): Solar E10, W8-1 B-MOM, SM14 OneLot, PORT_TILT_532 (V1 record).
Champion (candidate composition): DAYONLY_DUAL6040. Challenger: A-dominant OneLot.
Experimental: B1, everything in NEXT_RESEARCH_QUEUE.

## Corrected claims (full list: KNOWN_ERRORS_AND_CORRECTIONS.md)
DD numbers across different vol bases were never comparable; leverage headline trimmed
to worst-method; June/July 2026 is a CONSUMED quasi-holdout (no pristine OOS exists);
SM14 numbers re-canonicalized (+2.5%); B-MOM artifacts carry stress friction.

## What still needs to be proven
1. A-dominant OneLot must pass a properly-specified replacement gate (ΔSharpe/ΔCDaR).
2. NinjaTrader Strategy Analyzer parity for the one-lot strategy (compilation ≠ parity).
3. DAYONLY_DUAL6040 NinjaScript master + parity (NINJATRADER_PARITY.md).
4. Old-regime stress of the new compositions (2006-2021 substrate exists for Solar).
5. A third genuinely different engine (see COMPLEMENTARY_ENGINE_FRONTIER.md queue).

## House rules that bite
Specs committed BEFORE reads; append-only registry (seq at 357); killed axes must not
be re-tested (registry + EVIDENCE_MAP); right-tail retention ≥90% for overlays; crisis
retention ≥60% for anything cutting shorts; no argmax cells — plateau centers only;
every DD claim names its risk basis; ≥2026-08-01 data is VIRGIN (do not read).
