# C01 T0-2 — Oracle Capacity Bound for ML Overlays

_Executed 2026-08-07 against the frozen constants in `C01_WAVE_SPEC.md` §2 T0-2 (committed before
any result was read). Tier-0 instrumentation; consumes 0 R1 trials. DoF: 0 (no constant was
adjusted after seeing results). Basis: REALIZED_ONLY at session granularity — for these
flat-at-session-close members this equals TRUE_MTM per the AUDIT-03 identity._

**VERDICT: PASS — the ML program may proceed to T0-6 feature screens.**

## 1. Engine and data

- Inputs: 13 member fill ledgers `runs/AUDIT02_V3_SWEEP_B/ledgers/b2v3__tf3_sm179_am0_th1_vp460_vm{6..30}_xm0_sc_slip1.csv`
  (1-tick slip, $2.18/fill = $4.36/RT Lifetime commission already in the fills).
- Counterfactual rule: episode-level no-bet ⇒ member flat for that round trip; the trade's net
  (price P&L − both fill commissions) is removed; all other trades untouched. Valid because the
  flip sequence is position-independent (entries are price-determined, not position-determined).
- Round-trip pairing = `audit_mtm.daily_conventions` convention (flat-or-one-lot asserted on every
  ledger; every ledger ends flat). Session date = exit-fill time, 18:00 ET roll, weekend → Monday.
- Portfolio = pooled 13-member equal-weight (1/N) daily P&L on a fixed 1,183-session index
  (2022-01-03 → 2026-07-31), identical across all arms.

## 2. Validation (0% filter vs raw ledgers) — required first, PASSED

Engine net reproduces the raw-ledger signed cash flow **to the penny (max |diff| = $0.00)** for
all 13 members, and engine trade count = fills/2 = header `execs`/2 for all 13:

| member | fills | trades | ledger net $ | engine net $ | diff |
|---|---|---|---|---|---|
| vm6 | 16,984 | 8,492 | 166,144.88 | 166,144.88 | 0.00 |
| vm8 | 11,076 | 5,538 | 170,549.32 | 170,549.32 | 0.00 |
| vm10 | 8,072 | 4,036 | 150,033.04 | 150,033.04 | 0.00 |
| vm12 | 6,166 | 3,083 | 138,883.12 | 138,883.12 | 0.00 |
| vm14 | 4,918 | 2,459 | 241,923.76 | 241,923.76 | 0.00 |
| vm16 | 4,066 | 2,033 | 228,891.12 | 228,891.12 | 0.00 |
| vm18 | 3,360 | 1,680 | 246,515.20 | 246,515.20 | 0.00 |
| vm20 | 2,938 | 1,469 | 245,125.16 | 245,125.16 | 0.00 |
| vm22 | 2,598 | 1,299 | 245,446.36 | 245,446.36 | 0.00 |
| vm24 | 2,320 | 1,160 | 193,737.40 | 193,737.40 | 0.00 |
| vm26 | 2,108 | 1,054 | 132,859.56 | 132,859.56 | 0.00 |
| vm28 | 1,904 | 952 | 165,399.28 | 165,399.28 | 0.00 |
| vm30 | 1,786 | 893 | 249,256.52 | 249,256.52 | 0.00 |

## 3. Baseline (pooled 1/N, all 34,148 trades)

Net **$198,058.82** | Sharpe **1.065** (√252, incl. zero days on the fixed index) | maxDD
**−$39,853.39** | win rate 39.6% | gross wins $26.657M vs gross losses −$24.083M (raw pooled
dollars; net = (W+L)/13). The gross-to-net ratio ≈ 13:1 is the structural fact this whole item
turns on. Top-1% right-tail = 341 trades holding $4.127M raw = **160.3% of pooled baseline net**.

## 4. ORACLE arm (remove worst k% of pooled trades by realized net)

| k% | trades kept | net $ | Sharpe | maxDD $ | DD red % | net cost % | top-1% kept (trades / P&L) |
|---|---|---|---|---|---|---|---|
| 5 | 32,441 | 701,636 | 3.89 | −14,642 | 63.3 | −254.3 | 100 / 100 |
| 10 | 30,733 | 1,001,660 | 5.57 | −9,061 | 77.3 | −405.7 | 100 / 100 |
| 15 | 29,026 | 1,229,525 | 6.91 | −4,798 | 88.0 | −520.8 | 100 / 100 |
| 20 | 27,318 | 1,413,763 | 8.01 | −2,769 | 93.1 | −613.8 | 100 / 100 |
| 25 | 25,611 | 1,564,477 | 8.90 | −1,782 | 95.5 | −689.9 | 100 / 100 |
| 30 | 23,904 | 1,690,040 | 9.67 | −1,119 | 97.2 | −753.3 | 100 / 100 |
| 35 | 22,196 | 1,795,084 | 10.36 | −804 | 98.0 | −806.3 | 100 / 100 |
| 40 | 20,489 | 1,881,649 | 10.93 | −454 | 98.9 | −850.1 | 100 / 100 |
| 45 | 18,781 | 1,951,533 | 11.39 | −313 | 99.2 | −885.3 | 100 / 100 |
| 50 | 17,074 | 2,004,166 | 11.75 | −132 | 99.7 | −911.9 | 100 / 100 |

Negative net cost = net **gain**. Right-tail check: worst-k removal never touches the top-1%
set at any k — **100% of right-tail trades and P&L retained in every oracle cell**. The tail is
not the thing being cut.

## 5. NOISY-ORACLE arm (labels flipped w.p. ε; bet predicted winners; mean of 25 seeds)

| ε | ≈AUC | net $ (±sd) | Sharpe | maxDD $ (±sd) | DD red % | net cost % | top-1% kept (trades / P&L) |
|---|---|---|---|---|---|---|---|
| 0.00 | 1.00 | 2,050,567 | 12.07 | 0 | 100.0 | −935.3 | 100 / 100 |
| 0.10 | 0.90 | 1,662,401 ±10,204 | 10.81 | −1,342 ±431 | 96.6 | −739.3 | 90.7 / 90.6 |
| 0.20 | 0.80 | 1,267,835 ±11,349 | 9.22 | −2,905 ±519 | 92.7 | −540.1 | 80.2 / 80.0 |
| 0.30 | 0.70 | 881,241 ±16,001 | 7.15 | −4,401 ±798 | 89.0 | −344.9 | 70.3 / 70.3 |
| 0.40 | 0.60 | 480,374 ±14,766 | 4.39 | −7,438 ±1,015 | 81.3 | −142.5 | 59.7 / 59.5 |
| **0.45** | **0.55** | **294,708 ±16,285** | **2.83** | **−10,875 ±1,879** | **72.7** | **−48.8** | **55.0 / 54.8** |
| 0.50 | 0.50 | 99,622 ±13,776 | 1.00 | −21,809 ±4,101 | 45.3 | +49.7 | 49.8 / 49.9 |

Right-tail behavior: i.i.d. flips retain the top-1% at exactly the base keep rate (1−ε; e.g.
54.97% observed vs 55% expected at ε=0.45) — **no adverse selection against the tail**; the tail
share cut equals the overall cut, satisfying the wave's structural tail requirement. The ε=0.45
net gain arrives despite losing ~45% of tail P&L because ~45% of the $24.1M loss mass leaves too.

## 6. Frozen gate

- **PASS condition** — ε=0.45 (≈AUC 0.55): DD reduction **72.7%** ≥ 15% ✓ at net cost **−48.8%**
  (a gain) ≤ 10% ✓. Seed-robust: **all 25/25 individual seeds pass** (worst seed: DD red 57.8%,
  net cost −26.3%).
- **REJECT condition not triggered** — break-even (net cost ≤ 0) holds at every ε ≤ 0.45;
  empirical break-even ε ≈ **0.475** (analytic check ε* = |L|/(|L|+W) = 24.083/50.740 = 0.4746 —
  matches), i.e. accuracy ≈ 52.5% / AUC ≈ 0.525 suffices. Far above the ε ≤ 0.40 (AUC > 0.60)
  rejection line.

**VERDICT: PASS. ML program proceeds to T0-6 univariate feature screens.**

## 7. Honest caveats (read before celebrating)

1. **This is a capacity bound, not an achievability result.** The noisy oracle sees each trade's
   own realized label through i.i.d. noise. Real classifier errors are feature-conditional and
   serially correlated (regime-clustered), which degrades DD reduction faster than i.i.d. flips;
   nothing here shows a real feature set attains ε≈0.45-equivalent skill out-of-sample. That is
   exactly what T0-6's purged-CV screens must establish.
2. **The bound is generous because gross ≫ net (13:1).** Any 55/45 win-keeping skew harvests the
   gross spread; the same arithmetic would flatter almost any PF≈1.1 high-turnover book. The gate
   was frozen before results and is reported as specified.
3. DD reduction alone is nearly meaningless here: pure coin-flip filtering (ε=0.5) still "reduces"
   DD 45% by halving exposure while destroying half the net (+49.7% cost). Only the joint
   DD-and-cost condition binds; future overlay claims must never cite DD reduction without cost.
4. Commission asymmetry: removed episodes also remove their $4.36 RT, slightly flattering all
   filters symmetrically; effect is identical across arms and does not move the gate.

## 8. Artifacts

- `research/04_complementary_family/c01_t02_oracle_grid.csv` — oracle arm cells (incl. k=0 validation row).
- `research/04_complementary_family/c01_t02_noisy_grid.csv` — noisy arm, per-ε means/sds over 25 seeds.
- `research/04_complementary_family/c01_t02_cells_raw.csv` — all 186 raw cells (every seed).
- Engine script (session scratchpad): `t02_oracle.py`; seeds `default_rng(20260807 + seed*1009 + int(ε*1000))`, seed ∈ 0..24.
- Registry accounting (seq-0 instrumentation row, counts_as_trial: no) left to the wave
  orchestrator to avoid concurrent-write conflicts with sibling Tier-0 items.
