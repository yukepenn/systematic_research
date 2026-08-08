# SM01 — Canonical Python Substrate: Parity Report

_2026-08-08. Instrumentation run (zero R1 burn). Spec: `runs/SM01_SUBSTRATE/spec.yaml`
(committed before results). Simulator: `src/analytics/sm01_solarsim.py`.
Builder: `runs/SM01_SUBSTRATE/build_substrate.py`._

## Verdict: ALL FOUR GATES PASS

| gate | target | result |
|---|---|---|
| **A** member per-bar positions | `runs/E10MASTER_V1/out/e10m_v1_bars.csv` p6..p30 | **4 diffs in 7,023,016** — all on the single final bar 2026-07-31 16:57 (missing 17:00 boundary bar). FACT |
| **B** member fills | `research/05_open_axes/h006/*.csv` (13 ledgers) | **8/13 members exact on every fill (time, price, action)**; vm6/8/10/12 differ ONLY in the final session-close fill price of 2026-07-31 (boundary bar absent from bar export); vm14 additionally lacks the engine's data-end 17:00 entry+exit pair. Zero diffs anywhere in 2022-01→2026-07-30. FACT |
| **C** E10 daily net | `research/audit/e_variant_daily_vectors.csv` E10_round_session | mean \|daily diff\| **$0.19**, corr **0.9999968**, total $179,158.90 vs $179,361.36 (−0.11%, of which ~$215 is the 2026-07-31 boundary day); 39 sessions differ >$0.01 (audit fill-retiming micro-conventions). FACT |
| **D** cross-source alignment | 1m→3m aggregation; hist parquet vs 2022-26 export | **exact zero**: B01A 1m aggregates to AUDIT03 3m with 0 diffs on all 540,232 bars/4 OHLC fields; hist parquet ≡ B01A on all 1,558,497 overlapping bars (offset 0.0 in every quarter). The 2006→2026 minute parquet and the canonical series are ONE price universe. FACT |

Also reproduced along the way (engine-exactness evidence):
- `tgt_next` (the E10 master's own target column): 1 diff in 540,232 bars (boundary).
- `sum` (vote): 1 diff in 540,232 (boundary).
- Fill counts per member match ledger exec counts exactly (16,984 … 1,786).
- Total trades 34,147 vs audited 34,148 episodes (the boundary episode).

## Conventions recovered and now encoded (for all downstream tracks)

1. σ460 = trailing mean |ΔClose| including the current bar; NaN before bar 30;
   expanding mean to bar 460, exact trailing 460 after. S = clamp(k·σ, 10.0, 300.0)
   price units; fallback 44.75 when σ undefined; **resampled only at flips**.
2. Flips: strict close-cross of anchor∓S. Members enter only on Type-1 flip bars when
   flat; exit when close ≤/≥ (post-update) exit level; exit and entry never same bar.
3. Fills: next-bar OPEN ±1 tick, capped by fill-bar range; session-close exits AT the
   17:00 bar close ±1 tick capped. **Entries decided on a session's last bar are
   dropped by the engine** (verified 2025-06-05 vm20); the sole exception is the
   data-end boundary where the engine fills at the stamp (2026-07-31 vm14).
4. The E10 master aggregates member **pending** positions (post-next-open), i.e.
   `tgt_next = round(10·mean(pend))` clamp ±10, executed at the next bar open.
5. The E10MASTER engine run executes on real MNQ price data; the research-basis
   champion (audit E10_round_session, NQ prices × MNQ point value) is the correct
   Python target and is what this substrate reproduces.

## Outputs

- `out/member_trades.parquet` — 34,147 round trips, 13 members, with per-trade
  MFE/MAE (points), bars-to-MFE/MAE, bars held, entry/exit sessions.
- `out/vote_state_3m.parquet` — per-bar: σ460, vote_pos, vote_pend, n_long/short/flat,
  flips_bar, per-member pending positions.
- `out/e10_daily_py.csv` — Python E10 daily net (session basis), 1,184 sessions.
- `out/build_meta.json` — build metadata.

## Downstream rules

- All ANALYSIS restricted to sessions ≤ 2026-05-31 (CONVENTIONS §1); the substrate
  includes June–July 2026 only so the joint holdout read can reuse this exact code.
- Overlay/portfolio deltas are always computed against THIS simulator's baseline
  (internal consistency), with the audited vectors as the external anchor.
- Pre-2022 extension: resample_3m(nq1m_2005_202605.parquet) — same price universe
  (GATE_D), same simulator; results labeled TRANSITION/HISTORICAL diagnostics.
