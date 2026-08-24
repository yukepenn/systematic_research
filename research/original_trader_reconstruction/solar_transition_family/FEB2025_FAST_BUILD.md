# FEB2025_FAST_BUILD — the RKSelTimeDSTMa transitional build
(directive v3.0 §11, PHASE C4 — 2026-08-24. Separate family; do NOT force into
CAND2. Sources: targets_feb2025_dailies.csv, targets_perday_analysis.csv 0026
rows, PARAMETER_VERSION_TIMELINE, R1 OOS note.)

## Day-by-day arc (trades/day · avg hold · avg loss · build markers)

| Window | n | t/day | hold | avg loss | LL param | comm | Build marker |
|---|---|---|---|---|---|---|---|
| 2/3 | 35 | 25.4 | 38.7 | −586 | — | 4.18 | SolarWindRK LIVE Strategy Performance (already fast!) |
| 2/4-5 | 30 | 14.5 | 69.5 | −743 | — | 4.18 | SolarWindRKSelTime 90/179/5/10/10 |
| 2/6-8 | 4 | — | 33.8 | −2188 | — | 12.54 | **Quantity-3 experiment** (excluded from fitting) |
| 2/9-11 | 10 | 4.8 | 107.7 | −601 | — | 4.18 | slow again |
| 2/12-13 | 20 | 14.5 | 57.1 | −681 | **4000 (new)** | 4.18 | LossLimit first seen |
| 2/15-18 | 4 | 2.9 | 114.8 | −883 | **2500** | 0 | **RKSelTimeDSTMa first seen**; comm ☐ first |
| 2/19-20 | 10 | 7.2 | 75.3 | −448 | none visible | 4.18 | non-LossLimit variant coexists |
| 2/21 | 3 | 4.4 | 129.7 | −834 | — | 4.18 | |
| 2/23-24 | 8 | 5.8 | 116.1 | −504 | — | **5.68** | commission-rate experiment |
| 2/25-26 | 18 | 8.7 | 81.4 | −580 | — | 5.68 | |
| **2/26** | 15 | 15 | — | — | — | — | (0026 per-day row) |
| **2/27** | **90** | **90** | — | **−331** | — | — | **THE fast day** (NVDA-aftermath volatility) |
| 2/28 | 21 | 15.2 | **19.6** | −945 | — | 0 | heavy loss day −9,455 posted honestly |
| 3/2-3 | 26 | 18.8 | 44.7 | −869 | — | 5.68 | |
| 3/4-5 | 70 | **33.8** | 31.8 | −742 | — | 0 | LL −2,440 (no 65-pt stop yet) |
| 3/6-7 | 47 | 22.7 | 31.1 | −596 | — | 0 | **two CHECKED bool params appear** (new tail) |
| 3/9-10 | 33 | 23.9 | 24.4 | −704 | — | 0 | crash Monday, short dominance |
| 3/12-14 | 60 | 21.7 | 41.2 | −619 | — | 0 | first "even trade" |
| 3/15-4/30 | 555 | 17.5 | 41.3 | −753 | — | 4.18 | consolidated fast era |
| 5/1-6/27 | 340 | **8.4** | **84.6** | −692 | — | 4.18 | **slowdown — fast layer retired/retuned** |
| 6/28-7/4 | 16 | 5.8 | 141.9 | −545 | — | 4.18 | back to slow flagship; St/D-M groups appear by ★0062 |

## What changed in the fast build — behavior-derived inferences

1. **The A-panel did NOT change**: 90/179/5/10/10 is still on the 2/28 frame
   (★0029). The 4-10× frequency therefore comes from an ADDITIONAL entry layer
   + tighter exits, not from retuned wave geometry. Our T1-only stream produces
   22 trades on 2/27 vs his 90 (R1 OOS note) — the extra ~68 trades are the
   fast layer alone.
2. **Average loss shrinks to −$331 (≈16.5 NQ pts) on 2/27** while the wave's
   reversal distance is 179 ticks (44.75 pts) — the fast layer has its own
   tight risk, not the wave's. Holds compress to ~20-40 min era-wide.
3. **This is the same layer family the S4 retune later touches**: R5 proved
   A3-A5 (5/10/10→3/6/9) only affect pullback/weak-state machinery, invisible
   to T1 flips — i.e. the trader kept a pullback layer through 2025 and tuned
   its FREQUENCY knobs in Nov. In DSTMa-Feb the layer ran hot; from May-Jun it
   ran slow (8.4 t/day, hold 85); Jul-Oct weekly reports (hp) run ~5-8 t/day.
4. **LossLimit (4000→2500) belongs to THIS branch only** (DSTM). It disappears
   from later panels; the Jul+ D/M pair (4500/2000) is a different group
   (RISK_STATE_MACHINE_2025.md).
5. **No 65-pt stop yet anywhere in Feb-Apr**: largest losses −1,435…−2,440
   through 4/30. The −1,300-cap signature starts with the Jul weekly series →
   St group arrived with the summer build.
6. Commission churn (4.18→12.54(qty3)→0→5.68→0→4.18) is bookkeeping noise, not
   strategy: he experimented with templates then settled on $0 from 2/28
   ("偷懒" admission, EV-035); the 3/15+ windows show $4.18 again on hp captures.

## Open question (preserved, §11)
What exact trigger fires ~68 extra times on a volatile day with ~16-pt average
loss? Constraints: close-basis armed-latch T2 (late mode) is the only recovered
vendor-shaped candidate that adds entries without touching T1 chains, but the
recovered T2 arithmetic could NOT reach 90/day in R1.h replays. The layer is
his own code. Candidate shapes (for a future preregistered test, NOT tuned):
re-entry after stop-out in trend direction, micro-pullback re-arm on each new
extreme, or a second faster wave instance (smaller A2) feeding the same wrapper.
The 2/27 tape (NVDA aftermath) + LossLimit 2500 + avg loss −331 are the
identifying constraints.

## Status
Transitional family DOCUMENTED, out of CAND2 scope. Do not chase further until
the S2/S3 weekly identification (hp-machine build) lands, because the hp build's
suppression/winner-extension signature may BE this layer running in slow mode.
