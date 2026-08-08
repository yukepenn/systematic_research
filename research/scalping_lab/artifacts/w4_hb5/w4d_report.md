# W4-D — H-B5: spike continuation vs reversal (classification → one frozen trade readout)

Date: 2026-08-07 (run). Spec: `research/scalping_lab/specs/W4_alpha_wave1.md` §W4-D (frozen).
Code: `research/scalping_lab/src/python/w4d_hb5.py`. Seed 20260808, 1000 session-bootstrap reps.
Data: 37 L2 discovery sessions, sechilo+grid1s merge, RTH quote-alive decisions,
conservative same-second-both-crossed→adverse barrier rule. All numbers below appear in
`w4d_stdout.txt` / `w4d_episodes.csv` / `w4d_cells.csv` / `w4d_trade_readout.csv`.

## Definition (frozen)

Spike: |mid_last(t) − mid_last(t−10s)| ≥ 16t on RTH quote-alive seconds; 60s episode
collapse (first second wins). From the spike second: CONT = further +12t in spike
direction before −8t against within 300s; REV = mirror; NEITHER otherwise.

## Pooled classification (FACT)

- Episodes: **10,061** across **36** unique sessions (of 37; s20250902 produced none); **271.92 episodes/day**.
- Direction: 5,047 up-spikes / 5,014 down-spikes.
- **P(CONT) = 0.3902** (day-clustered 95% CI [0.3810, 0.3992]), **P(REV) = 0.4065**, **P(NEITHER) = 0.2033**.
- NEITHER breakdown: 2,044 both-adverse whipsaws, 1 cap-unresolved.
- Up-spikes: P(CONT)=0.3931, P(REV)=0.4060, P(NEITHER)=0.2009 (n=5,047).
- Down-spikes: P(CONT)=0.3873, P(REV)=0.4071, P(NEITHER)=0.2056 (n=5,014).

INFERENCE: pooled, a 16t/10s spike has no continuation edge — REV is slightly more
likely than CONT and the CI excludes P(CONT) ≥ 0.41.

## Conditioner cells — P(CONT) vs pooled 0.3902 (FACT)

| cell | n | sessions | P(CONT) | P(REV) | P(NEITHER) | dev | qualifies |
|---|---|---|---|---|---|---|---|
| near_news=False | 10053 | 36 | 0.3899 | 0.4067 | 0.2033 | −0.0003 | no |
| near_news=True | 8 | 1 | 0.7500 | 0.1250 | 0.1250 | +0.3598 | no (n<100, sess<15) |
| pretrend=aligned | 4801 | 36 | 0.3866 | 0.4139 | 0.1995 | −0.0036 | no |
| pretrend=opposite | 5234 | 36 | 0.3936 | 0.3993 | 0.2071 | +0.0034 | no |
| pretrend=zero | 26 | 18 | 0.3846 | 0.5000 | 0.1154 | −0.0056 | no |
| spread≤2 | 5395 | 36 | 0.3874 | 0.4104 | 0.2022 | −0.0028 | no |
| spread>2 | 4666 | 36 | 0.3935 | 0.4021 | 0.2045 | +0.0033 | no |
| **ret≤0.25** | **1509** | **36** | **0.8701** | 0.0417 | 0.0881 | **+0.4799** | **YES** |
| ret>0.25 | 8552 | 36 | 0.3055 | 0.4709 | 0.2236 | −0.0847 | no |
| block 0930_1030 | 1992 | 36 | 0.3710 | 0.4162 | 0.2129 | −0.0192 | no |
| block 1030_1200 | 2613 | 36 | 0.3934 | 0.4137 | 0.1929 | +0.0032 | no |
| block 1200_1400 | 2891 | 35 | 0.4044 | 0.3895 | 0.2062 | +0.0141 | no |
| block 1400_1600 | 2565 | 34 | 0.3860 | 0.4109 | 0.2031 | −0.0043 | no |

Scheduled-news conditioner: **EVALUABLE** — calendar
`research/04_complementary_family/c01_announcement_calendar.csv` (145 rows, columns
date/event/time_et/source, all time_et parseable) was usable. NFP/CPI at 08:30 ET are
pre-RTH so only FOMC 14:00 windows can overlap RTH spikes; only 8 near-news episodes
(1 session) exist in the discovery sample, so the cell cannot qualify under the frozen
n≥100 / ≥15-session gates.

## Frozen trigger and the single trade readout (FACT)

Exactly one cell qualified: **ret_cell=ret≤0.25** (first-10s retracement ≤ 25% of the
16t spike), n=1,509, 36 sessions, dev +0.4799. Favored direction = CONT (spike
direction). Per the frozen rule: enter at spike-end+10s, bracket (24,8), cap 300s,
cooldown 60s.

| slice | trades | trades/day | unique days | tgt/adv/cap | P(tgt-first) | net C1 (t) | 95% CI (C1) | net C2 (t) | gross (t) |
|---|---|---|---|---|---|---|---|---|---|
| ALL | 1386 | 37.459 | 36 | 321/1065/0 | 0.2316 | **−3.461** | [−4.126, −2.797] | −5.461 | −0.589 |
| LONG | 752 | 20.324 | 36 | 164/588/0 | 0.2181 | −3.893 | [−4.805, −2.923] | −5.893 | −1.021 |
| SHORT | 634 | 17.135 | 36 | 157/477/0 | 0.2476 | −2.948 | [−3.926, −1.946] | −4.948 | −0.076 |

INFERENCE: break-even P(tgt-first) for (24,8) is (8+2.872)/32 = 0.340 at C1 and
(8+4.872)/32 = 0.402 at C2 (derived from frozen costs); observed 0.2316 is far below
both, and the C1 CI upper bound is < 0 in every slice.

## Verdict: KILL (definitive B)

- FACT: pooled, spikes carry no continuation edge (P(CONT) 0.3902 < P(REV) 0.4065).
- FACT: the one qualifying conditioner (ret≤0.25, P(CONT)=0.8701) does NOT survive its
  own frozen trade readout: net C1 −3.461t/trade, CI [−4.126, −2.797], negative in both
  directions.
- INFERENCE: the ret≤0.25 classification edge is mechanically pre-entry — a low
  first-10s retracement largely means the +12t continuation is already underway (or
  done) inside the 10s conditioning window; by the frozen entry at spike-end+10s the
  move is consumed and the (24,8) bracket buys the top. The classification asymmetry is
  real but not exploitable at the frozen entry; no cell shopping beyond the frozen
  criterion is permitted, so the family is closed.

Artifacts: `w4d_stdout.txt` (full run log), `w4d_episodes.csv` (10,061 labeled
episodes), `w4d_cells.csv` (13 conditioner cells), `w4d_trade_readout.csv` (1,386
trades), this report.
