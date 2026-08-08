# Red-team verification — SMV2H2_ONELOT_CONFIRM (seq 358-360)

_Statistical red team, V4 §48 mandatory pass. 2026-08-08. Independent recomputation
script (scratchpad, not committed); all inputs = this run's out/ artifacts, the parent
canonical curves, and the two substrate parquets. Verdict: **CONFIRMED**._

## 1. Spec freeze and letter-exactness

- spec.yaml committed at 0a9cf3f (2026-08-08 12:09:17 -0400, "specs FROZEN before any
  read") — BEFORE any out/ artifact was written (12:18-12:20). Working-tree spec is
  byte-identical to the committed spec (`git diff 0a9cf3f -- spec.yaml` empty).
- Gate A implemented letter-exact: block=5, B=10000, seed=20260808, paired (one shared
  circular-block index set), statistic_1 = per-path dSharpe (A_dom - SM14),
  statistic_2 = per-path dCDaR_0.95 (SM14 - A_dom), threshold 0.85 applied ONLY to
  center s7 (seq 351) on both instruments; s5/s9 held to point-delta plateau support
  only. gate_A.csv contains exactly the 6 preregistered cells (3 seq x 2 inst) — no
  extra cells, no post-hoc selection.
- Gate B implemented letter-exact: window 2006-01-05..2021-12-31 (verified from
  gate_B_daily_curves.csv and the hist parquet itself), c1 net >= net(SM14) - $10,000,
  c2 maxDD <= 1.25x, c3 trades/yr <= 1.5x (evaluated under both entries and fills
  conventions, both pass — no convention shopping). Kill screen (< -$25k year) and
  top-10-day retention both computed and reported as spec requires.
- Policy/state code replicates runs/SMV2H_ONECONTRACT/smv2h.py line-for-line
  (run_policy, pol_hyst, pol_dominant, HTF shift(1), 1.25 tilt, 0.5 short-halving,
  0.9026, clip +-13, M = 0.7086*T + 2.83*B, ops windows 1639 / 1630-1803). Empirically
  confirmed by the exact reconciliation (below).
- Decision rule applied as frozen: fail_any_gate -> SM14 retained, A-dominant recorded
  CONFIRMATION-FAILED with both failing gates named. No promotion language anywhere.

## 2. Independent recomputations (all MATCH)

From out/regen_daily_curves.csv (own code, no executor imports):
- Point dSharpe / dCDaR, all 6 cells, both instruments: match gate_A.csv to <1e-9
  (e.g. s7 MNQ +0.185711 / +$1,355.50; s7 NQ +0.180685 / +$13,008.76).
- Bootstrap replication with spec seed 20260808: P(dSharpe>0) = 0.7169 MNQ / 0.7117 NQ,
  P(dCDaR>0) = 0.6391 / 0.6318 — identical to gate_A.csv to 4 decimals.
  Seed-sensitivity probe (seed 12345): 0.7147/0.7089 and 0.6435/0.6363 — the FAIL vs
  the 0.85 bar is robust to seed and cannot plausibly flip on the circular-vs-strict
  moving-block construction choice (miss is ~0.14-0.22 in probability).
- Cross-check regen vs parent runs/SMV2H_ONECONTRACT/out/daily_curves.csv (my own
  comparison): max abs daily diff exactly 0.0 on all four MNQ curves, n=1139.
- Gate B from gate_B_daily_curves.csv: net A $29,708.80, net SM14 $46,866.36, gap
  -$17,157.56 (c1 FAIL), maxDD $21,101.92 vs $59,122.92 ratio 0.3569 (c2 PASS),
  Sharpe 0.2297 vs 0.1742, 2020/2021 deltas -$17,562/-$66,963, head-to-head wins
  11/16, worst years 2021 -$9,231 (A) / 2009 -$14,661 (SM14), no year < -$25k — all
  match gate_B_summary.json and the REPORT.
- Top-10 retention: 0.7722 MNQ / 0.7729 NQ recomputed — warning correctly fires (<0.90).
- LOYO 350/MNQ: d_net -2161/+1179/+1023/+3896/+3390, dSharpe -0.42/+0.24/+0.28/+0.44/
  +1.06 — reproduces the addendum exactly.
- Bridge (independent): T = clip(rha(10*vote_pend/13), +-10) equals e10_bar_pnl tgt on
  519,714/519,714 dev bars, 0 mismatches (my own recomputation from the parquets).
- Hist substrate: 2006-01-05 -> 2021-12-31, 1,764,049 bars, confirmed NO OHLC columns —
  the close+-1-tick fill approximation was forced by the substrate and is applied
  identically to both policies (disclosed in spec AND report).

## 3. Lookahead / leakage scan (clean)

- Dev window: prefix mask <= 2026-05-31 applied immediately after load in both
  executors (with a prefix assertion in gate A); regen curves end 2026-05-29; hist ends
  2021-12-31. No data >= 2026-08-01 touched; June/July 2026 excluded entirely.
- HTF state uses .shift(1) (prior-session close vs SMA50) — causal. B-MOM bands use
  only prior days' history (append after the day's position loop), VWAP is cumulative
  within day, BAND_DAYS burn-in enforced — causal, and verbatim from the frozen parent.
- Executor fill ordering: pend set at bar t from desired[t] AFTER the fill step, so a
  decision at bar t fills at bar t+1 (open on dev, close on hist) — decisions strictly
  precede fills in both replays.
- No re-fitting anywhere: all constants (0.9026, 0.7086, 2.83, thr 5/7/9, a=3,b=1)
  are frozen parent values; zero new dev selection, per budget.

## 4. Report language

FACT/INFERENCE/HYPOTHESIS labels used correctly; the kill is the headline; the
"challenger looked better on every point estimate" material is explicitly quarantined
as INFERENCE and does not soften the mechanical verdict; the right-tail warning and
kill screen are reported prominently. No overclaim found.

## 5. Nits (non-blocking, none affect the verdict)

1. REPORT says dev reconciliation "max abs daily difference = 0.0"; crosscheck_dev.csv
   records 4.55e-13 on three curves (in-memory float vs CSV round-trip noise). My own
   CSV-to-CSV comparison IS exactly 0.0. Immaterial; wording slightly stronger than the
   artifact.
2. Spec's method line says "moving-block bootstrap"; the implementation is the house
   circular-block scheme (smv2_common.boot_ci_mean construction — verified identical to
   src/analytics/smv2_common.py lines 52-59). Disclosed in REPORT and caveats;
   seed/construction sensitivity cannot flip a 0.71-vs-0.85 miss.
3. Run outputs (scripts, out/, REPORT.md) are uncommitted; spec.yaml itself WAS
   committed pre-execution, satisfying the freeze requirement. Commit of results is an
   orchestrator action (executor was barred from git).
4. Spec's "trades/yr" is ambiguous between entries and fills; executor evaluated both
   (ratios 0.416/0.417, both pass) — transparent, no gate move.

## Verdict

**CONFIRMED.** Gates applied letter-exact, all recomputed numbers match, no leakage
found, kill recorded honestly, SM14 retention and the "one new bounded family" next
action follow the frozen decision rule.
