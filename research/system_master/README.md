# SYSTEM_MASTER — NQ Systematic Master Program

Opened 2026-08-08 by owner master directive (verbatim: `OWNER_DIRECTIVE_20260808.txt` in this
directory). This is a **new higher-level program**: it consumes all Solar / scalping-lab /
Program-B evidence as inputs and designs a **system** (engines + risk overlay + allocator +
one NT8 execution layer), not another strategy.

Mission: **maximize robust risk-adjusted geometric growth of the total NQ system in the
current regime**, with drawdown, time-underwater and monthly consistency as first-class
objectives. Historical research only — no live trading, no Sim101, no account interaction,
no touching virgin data (≥ 2026-08-01).

## Inherited fixed points (do not re-litigate)

- **Champion / comparator:** executable **R5-E10** (13 × SolarWaveOpenV3, StartUp=false,
  ThresholdMode 1, VolPeriod 460, clamp 40–1200t, VolMult 6..30; target = round(10 × mean
  member position) MNQ, max 10; net-change execution; session-close flatten).
  TRUE_MTM 2022-01→2026-07: net $179,361.36, Sharpe 0.9671, DD −$41,252.
  Operational default: v2 (16:44 flatten), −5.35% net, corr 0.9972.
- **Solar parameter optimization is CLOSED.** Sleeves (Type-2/3), wave conditioning,
  threshold engineering as a class, chop vetoes, short gating, announcement conditioning,
  vol-surprise exposure, ML suppression overlays: all falsified/closed — see
  `EVIDENCE_MAP_RAW.md` and the two campaign registries. New work must be mechanically
  different and is filtered against those registries before any spec is frozen.
- **B-MOM** is reclassified **RECENT_REGIME_CHALLENGER** (owner directive §2E/§15):
  frozen rule, no retuning; evaluated for current-regime portfolio value.
- Top 1% of Solar trades ≈ 160% of net; **right-tail retention is a hard gate** on every
  overlay (see CONVENTIONS.md §6).

## Program structure (8 parallel tracks)

| # | Track | Output |
|---|---|---|
| 1 | Solar drawdown autopsy | `SOLAR_DRAWDOWN_ATLAS.md` |
| 2 | Stop / exit overlay frontier | `STOP_OVERLAY_FRONTIER.md` |
| 3 | Ensemble-internal confidence → exposure shape | (folds into 2/7 frontier docs) |
| 4 | Multi-timeframe + trend-quality features (conditional on Solar) | `INDICATOR_FEATURE_FRONTIER.md` |
| 5 | B-MOM recent-regime challenger + portfolio | `RECENT_REGIME_BMOM.md` |
| 6 | Complementary engine factory | `COMPLEMENTARY_ENGINES.md` |
| 7 | Portfolio synthesis + risk normalization + leverage | `PORTFOLIO_FRONTIER.md`, `LEVERAGE_FRONTIER.md` |
| 8 | NT8 master architecture + final package | `NINJATRADER_MASTER_SPEC.md`, `FINAL_NQ_SYSTEM.md` |

## Files

- `CONVENTIONS.md` — **frozen evaluation conventions** (regime windows, metric suite, gates,
  costs, bootstrap protocol). Committed before any new result was read. Binding.
- `CURRENT_STATE.md` — live program state, updated after every wave.
- `SYSTEM_FRONTIER.yaml` — machine-readable hypothesis frontier.
- `HYPOTHESIS_LEDGER.md` — every hypothesis: proposed → duplicate-checked → frozen → verdict.
- `EVIDENCE_MAP_RAW.md` — structured extraction of all prior-campaign evidence (12 readers).
- `runs/SM##_*` under repo `runs/` — every experiment, spec.yaml committed before read.
- Registry: continue `research/registry/tested_configs.csv` at **seq 291**.

## Governance

Thin, but three rules are absolute: (1) spec frozen + committed before any result read;
(2) append-only registries, no deletion of evidence; (3) every conclusion labeled
FACT / INFERENCE / HYPOTHESIS / EXTERNAL PRIOR. Waves must deliver at least one of:
trade-rule result, kill, promotion, drawdown improvement, portfolio improvement, or an
Analyzer-runnable implementation. Reports alone are not progress.
