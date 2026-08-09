# R2 confirm=2 candidate — early NT8/CrossTrade executable validation

Per directive sec28-29's standing rule (validate a genuinely-promotable candidate against real
NT8 BEFORE spending further Python-side robustness budget). This is a SPOT-CHECK on a
representative window, not a full-history certification — matching the same scope the campaign
used for the incumbent's own first NT8 checks before its full chunked certification.

## What was built and deployed

`src/ninjascript/SolarWaveOneContractNQ_v6_R2CONFIRM.cs` — a CHALLENGER object, built by copying
the current incumbent `SolarWaveOneContractNQ_v5` and adding ONLY the entry-confirmation overlay
(`ConfirmBars=2`, frozen from the Python grid): a new commitment from flat is armed on the side
it first crosses `EntryLevel` and only submitted once that side has held for 2 additional bars.
Everything else (Solar members, B-MOM, tilt, session-relative C4 flatten, DEFECT-3 fix) is
byte-identical to `_v5`. The incumbent file is untouched; this is a new, separately-named research
object (`Name`/`Tag`/`BuildTag` all distinct), not a supersession.

Compiled clean (`CompileNinjaScript`, in-memory, 0 errors/warnings) before being written to NT8's
live NinjaScript folder (`WriteNinjaScriptFile`) and run via `RunStrategyBacktest`.

## Result 1 — cold-start spot-check (2025-01-01 -> 2025-04-30, ZERO warmup)

NT8 net **$30,605.24** (140 trades) vs Python confirm=2 (full 2022+ continuation state)
**$36,001.00** for the same window — an 15% gap. **Not treated as a defect**: this campaign
already established (Product A's original "23% discrepancy," `PRODUCT_A_CERTIFICATE.md`) that a
cold NT8 start against a warmup-dependent decision layer (`TiltSma=50` sessions,
`BmomBandDays=14`, `VolPeriod=460` bars) produces exactly this kind of gap, and it is a warmup
artifact, not a logic error.

## Result 2 — warmup-corrected (2024-04-01 -> 2025-04-30, 9-month warmup, same methodology as the incumbent's own certificates)

| | net $ | n trades |
|---|---:|---:|
| NT8, entry-time filter on 2025-01-01..2025-04-30 | **$35,210.36** | **149** |
| Python confirm=2, same window | **$36,001.00** | **149** |
| difference | **-$790.64 (-2.2%)** | **exact match** |

**Trade count matches EXACTLY (149 vs 149).** Net-profit residual is -2.2%, smaller than every
one of this campaign's own already-certified full-history residuals for the incumbent (NQ +4.13%,
MNQ +4.41%, Product A +10.91%) and consistent in direction/magnitude with the same two disclosed,
non-defect conventions found and exactly reconciled there (NT8's real Standard-fill vs Python's
synthetic 1-tick adverse-slip approximation; NT8's boundary trade-list serialization quirk).
Raw NT8 result: `out/nt8_v6_confirm2_2024apr_2025apr_trades.json` /
`out/nt8_v6_confirm2_2024apr_2025apr_trades.csv`.

Note: NT8's own reported `NetProfit` performance-summary figure for the full 2024-04-01..
2025-04-30 window ($98,448.24) differs from the sum of the closed-trades list ($96,172.60,
465 trades) by $2,275.64 -- this is the same already-documented "position open at data end
counted in totals but possibly missing from the serialized trade list" convention noted in
CLAUDE.md, not a new anomaly, and does not affect the entry-time-filtered eval-window comparison
above (which uses the closed-trades list on both sides, consistently).

## Verdict

**Early NT8 validation: PASSED (spot-check).** The C# entry-confirmation overlay behaves as
intended on live NT8 output: exact trade-count agreement and a small, directionally-explicable
net-profit residual, on a real 13-month window spanning both regimes already used for the
incumbent's own certificates. This substantially de-risks the Python-side R2 finding — it is not
a Python-only artifact.

## What this does NOT establish yet (still required before promotion, unchanged from REPORT.md)

- Full multi-year chunked NT8 certification (only one 13-month window checked here, not the
  7-block full-history harness the incumbent has).
- MNQ-side NT8 validation (only NQ was checked; Python shows MNQ moves with NQ as expected since
  it is the same decision sequence, but this has not been independently confirmed on live NT8
  MNQ execution).
- Leg-by-leg (not just aggregate net + count) proof, the standard this campaign holds the
  incumbent to for full certification.
- Formal LOYO / rolling-window statistical robustness test (Python-side, not yet run).
- A proper preregistered child spec for the confirm_bars parameter choice (process gap disclosed
  in REPORT.md).

R2 status remains **VALIDATING**, now with real, passing NT8 evidence in hand rather than
Python-only evidence — a materially stronger position than before this check, not yet a
promotion.
