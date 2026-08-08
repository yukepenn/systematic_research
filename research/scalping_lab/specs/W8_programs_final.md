# W8 — post-closure funded program (frozen before readout, 2026-08-08)

Four runnable studies; the rest of the program is data-blocked pending the next NT8
restart (minute exporter). Conventions as prior waves; seed 20260808; dev windows only.

## W8-1 — B-MOM: intraday momentum family build (Program B; gate passed W5-B2)
Mechanically different from killed H-A1 (retry terms met): noise-band + VWAP
always-monitoring construction on the 3-min CSV (2022-01→2026-05-31, dev only).
Frozen rule: RTH bars 09:30–16:00; noise band around the 09:30 open: upper/lower =
open ± m_tod, where m_tod = trailing 14-day mean of |close(slot) − open| per 3-min slot
(same slot-of-day, prior days only); RTH-anchored VWAP from bar close×volume.
LONG when close > max(upper, VWAP); SHORT when close < min(lower, VWAP); flat
otherwise-signal persistence: hold until opposite signal or 15:57 close-out (always
flat overnight). One position, 1 NQ, C1 per round trip (2.872t), C2 stress.
Report: trades/day, net/trade (t), PF, win rate, yearly split, day-clustered CI on
daily P&L, max DD, concentration (top-5 days), AND measured daily-P&L correlation vs
Solar net_v1 + losing-day correlation (the deciding diversification numbers).
Frozen promotion gate: daily net C1 > 0 with CI_lo > 0, PF ≥ 1.10, ρ_full < 0.3,
losing-day ρ ≤ 0.1, top-5-day concentration < 40% → candidate freezes for engine
parity + Tier-1. Neighbors (reported, never selected): 10/20-day noise windows.

## W8-2 — B-FADE: release-day fade (NEW preregistration of the W7-3 post-hoc mirror)
HONESTY CLAUSE (frozen): the fade direction was OBSERVED on this same dev sample
(continuation net −53t@15min ⇒ implied fade ≈ +47t@15min); therefore the dev readout
is CHARACTERIZATION, NOT CONFIRMATION. Rule: 08:30 release days (calendar), at the
09:30 bar close enter AGAINST sign(09:30 close − pre-release 08:27 close); exits
{15,30,60} min; C1. Report: net/trade + CI (labeled in-sample), by event type
(NFP/CPI), by year, concentration, drawdown path, placebo (non-release days, same
rule off the 09:30-vs-08:27 sign). CONFIRMATION PLAN (frozen): pre-2022 minute data
(2005–2021, unseen, pending exporter) is the primary out-of-sample test; sealed
holdout only at Tier-3 if pre-2022 passes. No promotion from this wave.

## W8-3 — A-EXIT: patient execution on Solar's time-triggered exits (DR-E R1, Arm A+B)
Data: runs/E10MASTER_V2/out/e10m_v2_fills.csv (skiprows=1; MNQ prices = NQ index
levels; minute-stamped) ∩ 37-session discovery substrate (grid1s bid/ask, sechilo).
Arm A (time-triggered 16:4x exits): for each flatten exit fill (16:42–16:45) on a
substrate session: baseline = market cross at 16:44:00 (sell→bid, buy→ask from grid1s
at that second); patient = limit at the touch (sell→ask, buy→bid) posted at 16:44−W,
W ∈ {30,60,120}s; filled iff sechilo mid crosses THROUGH the limit by ≥1t before
16:44:59 (house trade-through convention); unfilled → forced cross at the deadline
second's opposite touch. Metric: realized − baseline per exit (ticks), fill rate,
net mean saving with day-clustered CI, and P&L-weighted miss cost.
Arm B (signal entries in window, non-16:4x Buy/SellShort fills): marketable-limit at
touch with patience W ∈ {5,30,60}s then cross; same accounting. Frozen expectations
recorded: Arm A positive ~+0.5–1t/exit; Arm B ≤ 0 (momentum non-fills). Verdict rule:
adopt-for-ops iff Arm A saving CI_lo > 0; close the passive track if ≤ 0.

## W8-4 — ROLE-B feasibility: entry-time micro-state vs Solar per-trade P&L
Reconstruct v2 round trips inside the 37 discovery sessions from the fills sequence
(signed qty × price, commission included; verify aggregate vs daily_v1_v2.csv net_v2
on those dates). For each trade: entry-minute micro features from grid1s/sechilo
(spread_t mean, sflow60, upd60, rv60, eff60, dist from session hi/lo, minutes-since-
open) at the entry timestamp. Deliverable: per-feature quintile table of subsequent
trade P&L, day-clustered CIs, and a leakage-guarded logistic (win/loss) with
chronological folds — MEASUREMENT of whether micro-state carries per-trade quality
information (roles B/C). No filter is adopted from this wave; any rule needs a new
spec + walk-forward + the falsified-axes review (day-level regime axes stay closed).

Blocked queue (needs owner NT8 restart; scripts staged to bin\Custom this wave):
SWMinuteExport_v1 (1-min Last 2005+ export: GC/CL/RTY/ZN screen, B1 2005+, H-D3@1min,
B-FADE pre-2022 confirmation) + SWScalpTickExport_v2 (20M cap re-export s20251117).
Artifacts: `artifacts/w8_*/`. Registry S28-S31.
