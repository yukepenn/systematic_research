# DATA AUDIT — substrates vs target windows (Phase 0/1, 2026-08-23)

## Substrates available

| Asset | Coverage | Notes |
|---|---|---|
| Canonical NT8 bar ledger `research/03_reverse_engineering/ledgers/t2_canonical_1m.csv` | 2023-01-02 → 2025-01-31, 737,707 1m bars, OHLC + vendor series | THE exact NQU6 back-adjusted series the canonical Type-1 run used (frozen close archive; SolarWaveRKLedgerV2 export). Preferred substrate for Track S screenshot parity. |
| `research/scalping_lab/substrate/minute/NQ/nq1m_2005_202605.parquet` | 2006-01-05 → 2026-05-29, 6,466,783 1m bars, OHLCV, END-stamped ET | Different back-adjust offsets than canonical ledger (point-differences invariant; levels/ratios not). Known holes: week 2014-01-27..31; 2009-03-27, 2009-06-19, 2013-07-12; 46 thin-RTH days. |
| `runs/SM1M_SUBSTRATE/out/nq_1m_2022_2026.parquet` | 2022-01-02 → 2026-07-31, 1,620,044 1m bars, NQ 09-26 merge | Only in-repo source for 2026-06-01→07-31 minute bars (window CONSUMED by SM11 → usable for reconstruction, NOT clean OOS). ES/RTY/YM twins exist. |
| Tick/L1+L2 `research/scalping_lab/substrate/raw/NQ/` | 48 sessions 2025-08-11 → 2026-05-20 (sampled ~4-6/mo), bip(Last/Bid/Ask), ns time | BBO event streams present except s20250811/s20250924/s20260430 (Last-only). Trade-at-bid/ask NOT stored; quote-rule classification BUILDABLE from raw streams. grid1s (tick-rule sflow) + sechilo derivatives exist. |
| NT8 local cache (outside repo) | NQ 09-26 minute → 2026-08-23; tick 2026-06-08 → 2026-08-11; NQ 06-26 tick 2026-03-15 → 2026-06-12 incl. May Bid/Ask | Re-export would require NT8 tooling (CrossTrade EXCLUDED this campaign) → treat as escalation-gated, not available. |
| `research/data_forward_sealed/DOM01/` | EMPTY (governance docs only) | Nothing usable. |

## Governance boundaries

- Through 2026-07-31: research-CONSUMED → freely usable for RECONSTRUCTION (never claim
  pristine OOS).
- ≥2026-08-01: VIRGIN under LOCKED_FORWARD — consumable only via MONITOR-01 or a
  preregistered protocol. OTR does NOT touch it (directive §1.9).

## Per-window feasibility

| Target window(s) | Family | Feasibility |
|---|---|---|
| EARLY_LONG 2023-01→2025-02 | S | **FEASIBLE (best case)** — canonical ledger = exact NT8 series incl. OHLC for Type-2; cross-check on nq1m parquet for robustness |
| 2025-09 → 2026-05 weeklies | S/SD/V/B | FEASIBLE minute-level (both parquets); tick only on sampled sessions |
| Track V window A 2026-05-10→05-22 | V | Minute FULL; tick exports for 4 sessions (05-11, 05-12 full; 05-19, 05-20 partial/capped + _rth); other sessions' tick NOT in repo (NT8 cache only → gated) |
| 2026-05-31 → 2026-07-31 weeklies | B/V/P | Minute FEASIBLE via SM1M parquet (consumed-not-clean); zero tick |
| Track V window B 2026-08-02→08-14 | V | **GOVERNANCE-BLOCKED** (virgin seal) AND no repo data. Do not touch. |

## Track V data verdict (preliminary, Phase 6 will finalize)

True historical bid/ask-classified volume ("BidAskPrice_RealVolume") does NOT exist as a
stored field. Quote-rule classification is buildable from raw BBO+trade streams for the 48
sampled sessions only (incl. 2 full sessions inside window A). Full-window V-EXACT on
window A: BLOCKED PENDING DATA (would require NT8 cache re-export → CrossTrade, excluded).
V-PROXY (minute OHLCV: e.g. tick-rule/close-position proxies) is feasible on all minute
windows. V-EXACT vs V-PROXY will never be conflated.

## Series-construction facts for §12 audit (Class B)

- Canonical run: "NQ 09-26" → NQU6 MergeBackAdjusted; additive offsets, machine/download
  dependent; point differences and per-trade point PnL are offset-INVARIANT (Solar math is
  difference-based; S is a constant tick distance) — level/ratio stats are not.
- Trader screenshots show contract-specific instruments (NQ MAR25, NQ JUN26): weekly 2026
  windows are per-expiry front-month data; the EARLY_LONG 2023→2025 report must have used
  some continuous/merged series (a single expiry does not span 25 months). Merge-policy
  differences (BackAdjusted vs non-adjusted) do NOT change Solar signal math (difference-
  based), only absolute levels — but NON-back-adjusted concatenation would inject roll
  gaps into close-differences at roll boundaries; since exit-on-session-close keeps every
  trade inside one session, roll-gap sensitivity is limited to signal-state (anchor)
  evolution across the gap. Quantify in S0b if S0 shows unexplained mismatch.
- MNQ vs NQ substrates carry different offsets; never mix bases.
