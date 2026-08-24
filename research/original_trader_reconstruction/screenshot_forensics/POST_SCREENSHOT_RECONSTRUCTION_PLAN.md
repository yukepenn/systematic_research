# POST-SCREENSHOT RECONSTRUCTION PLAN (directive §59 — gate for reopening backtests)

Written after 100% first-pass + >11% pixel QC. No broad universes; every test below
targets an image-anchored object with preregistered acceptance windows.

## Track R1 — S-era exact wrapper re-adjudication (highest priority, free)
Target objects: master (0002: 2023-01-01→2025-02-02, +$292,172.82 / 4,351 tr / WR
40.29% / PF 1.18 / DD −32,677.42 / hold 94.15m / comm $4.18/RT / slippage 0) + the
Feb-2025 daily runs (0007: 2/4-5 −$3,805.40, 30 tr; 0010; 0012; 0014) which have
FULL engine settings visible (lookback 256, BarsRequired 20, Standard fill, Break at
EOD, <Use instrument settings>).
- R1.1: rerun OTR-S-CAND1 on our canonical series with commission $4.18/RT and
  compare to the master row-set; the trader's own numbers replace the owner-relayed
  targets (net now has cents).
- R1.2: NEW constraint — trading-hours template = instrument default (24h), so any
  SelTime window is code-internal. Fit the window ONLY via the multi-window daily
  runs of Feb-2025 (2-day reports give sharp filters: 30/4/10/20/4/10/3/8 trades per
  window constrain entry gating hard).
- R1.3: LossLimit(2500/4000) semantics test against 0014/0016 windows (reports with
  those params active, net −2,555/+5,956): per-session halt vs per-trade.
- Acceptance: trades ±5%, WR ±2pp, PF ±0.05, hold ±10%, largest-loss family match.

## Track R2 — S2/S3 accretion-era models (2025-07→12)
- R2.1: add 65-pt initial / 30-pt trailing stop pair to CAND1; test against the
  −$1,300-cap weeks (0073-0095 series); the St group gives the spec directly.
- R2.2: A-param retune 90/180/3/6/9 variant against Nov-Dec weekly rows.
- R2.3: daily money pair (D 4500 / M 2000) as session halt/target overlay; test
  whether any weekly report's daily distribution shows 4500/2000 truncation.

## Track R3 — V-era flagship (2026-02→08)
- R3.1: re-target VF4 clone to the SA weekly series with the now-known wrapper:
  head window candidate [16,0,10,15], 130-pt (vs 2×65) stop → the −2600/−1300 mix
  in Feb-Mar discriminates the microstructure.
- R3.2: OF1/OF2 classifier feeds the BidAskPrice_RealVolume input on the two stored
  BBO sessions; chart-parity vs 0146-era windows.
- R3.3: variant-B (0150) is a NEW free target: 30/70/2/20 + [14,6] + [3,0,12,0] on
  the 5/31-6/5 window (+14,540, 82 tr, hold/WR visible) — small search space.
- Purchase decision (owner-gated): VWAP Flux remains the only justified oracle;
  needed ONLY if R3.1 residuals stay above tolerance after the wrapper fix.

## Track R4 — account layer
- R4.1: overlay reconstructed sleeves (R1/R2 flagship + R3) against the June-2026
  TP frames (23-33 tr/day, 20-34m holds, $1.04/side) to bound sleeve count/mix.
- R4.2: LAYER-2 economics: apply $2.08/RT + 1-tick slippage to all replicas
  (author's own ×0.9/×1.1 rule as sanity check).

## Guardrails
- LOCKED_FORWARD ≥2026-08-01 untouched for tuning (0164's 8/2-14 window is a
  REPORTED target only; no market-data tuning there).
- Every run: prereg spec.yaml before readout; tolerance bands preregistered above;
  no PnL-maximizing parameter search anywhere.
