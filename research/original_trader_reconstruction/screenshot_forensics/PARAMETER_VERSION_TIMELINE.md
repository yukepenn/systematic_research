# PARAMETER VERSION TIMELINE (directive §22B) — from settings panes, personally QC'd frames marked ★

Scroll-position caveat: panes are often scrolled; a group not visible in a frame is
NOT proven absent. "Structural" claims below rest on frames where the relevant group
boundaries are visible. Values cropped at the box edge keep trailing "?".

## S-family strategy panel (SolarWindRKSelTime → RKSelTimeDSTMa → evolved)

| Date (capture) | Strategy name | A1-A5 | Other groups visible | Frame |
|---|---|---|---|---|
| 2025-02-02 | (master run) | 90/179/5/10/10 + Qty 1 | none (pre-LossLimit layout) | ★0002 |
| 2025-02-05 | SolarWindRKSelTime | 90/179/5/10/10 + Qty 1 | FULL PANEL = A1-A5+Quantity ONLY; commission ✔ | ★0007 |
| 2025-02-09..11 | SolarWindRKSelTime | same | same | 0012 |
| 2025-02-13 | (name n/v) | same | + LossLimit 4000 (first seen) | 0014 |
| 2025-02-18 | RKSelTimeDSTMa | 90/179/5/10/10 + Qty 1 | LossLimit 2500; commission ☐ first seen; Commission-template row appears (NT update) | ★0016 |
| 2025-02-23..24 | | | commission template "NinjaTrader Broker…" $5.68/RT experiment | 0022 |
| 2025-02-28 → | | | commission $0 permanently (author later: "偷懒") | 0029+ |
| 2025-07..08 | (pane value-only) | 90/179/5/10/10 | above A1: …180?/140? tail of a group ALREADY present; below: [☑ 4500? 2000?] + [65/30/65] + [Q 1] | ★0062 (8/22) |
| 2025-10-17 | | (scrolled) | M…[E✔ D4500 M2000]; St…[I 65 T 30 I 65 M 20]; Tr…[Q 1]; U…[E✔ E 80]; label initials readable | ★0077 |
| 2025-10-24 | | A5=10 still | same groups; St…= In…65 / Tr…30 / I…65 / M…20 → STOP GROUP (In=Initial, Tr=Trailing) | ★0079 |
| 2025-11-07 | | top group 3/6/9 visible (A3-A5 RETUNED 5/10/10→3/6/9 between 10/24 and 11/7) | St group +46,36 (→6 rows) | 0083 |
| 2025-11-14 | | | St row 65→75 → [65/30/75/20/46/36] complete | 0087 |
| 2025-12-06 | | 90/180?/3/6/9 (A2 179→180±) | [☑10/26/14/198?/180?/140?] above A-group; [☑1]; [☑450?/200?]; [65/30/75/20/46/36]; [1]; [☑80] | ★0093 |
| 2026-01-02 | | | Entries per direction = 1 (O-group) | ★0104 |
| 2026-01-17 | | | 46/36→46/30; +2 checkboxes; +[☑0/2] group; Entries/direction 1→2 (0111) | 0109/0111 |

## 2026 flagship (VF-wrapper strategy)

| Date | Content | Frame |
|---|---|---|
| 2026-02-13 | NEW single-group layout: 15?/60/5/20/[▼]/95/75/50/25/5/3/10/5 — VWAP-Flux stack first visible | 0117 |
| 2026-02-20 | + two checkbox banks (8+7) after the 10/26/14 block | 0119 |
| 2026-04-02 | head [30?]/16/0/10/15 + VF block (60/5/20/EMA/95/75/50/25/5/3/10/5) | 0132 |
| 2026-04-17 | head 10→9 ([16,0,9,15]); trades/day halves, hold doubles that week | 0136 |
| 2026-04-29 | VARIANT panel: [☑10/20/14/198?/180?/140?] + [☑16/6/9] + [☑13,0,13,30,15,0,15,30] (two time windows 13:00-13:30 & 15:00-15:30) | ★0138 |
| 2026-05-02 | reverts to main layout | 0140 |
| 2026-05-23 | FULL LABELS read: Volume Base=BidAskPrice_RealVolume / Anchor Period (Minutes) 60 / VWAP Amount 5 / Trend Period 20 / Trend MA Type EMA / Max-Upper-Median-Lower-Min Percent 95/75/50/25/5 / Signal Quantity Per Trend 3 / Signal Close Threshold (%) 10 / Signal Split (Bars) 5 — colon-less near-ninZa naming | ★0146 |
| 2026-06-05 | VARIANT-2 panel: …30/70/2/20 + [☐☑☑☑ 14 6 ☑ 30 16 0] + [3,0,12,0] + checkbox bank; produced that week's posted +$14,540 | ★0150 |
| 2026-06-07..19 | (TP live frames — no panels) | 0152/0154 |
| 2026-06-26 → 08-14 | main VF layout, values UNCHANGED (3/10/5 tail; full stack re-verified 8/14) + one checked row above Volume Base | 0156/★0164 |

## Constants across every frame
NQ (front contract, MAR25→…→JUN26→SEP26), 1-Minute, Last, Tick Replay off, Break at
EOD ✔, slippage 0, Bars-required 20, lookback 256, Standard (Fastest), exit-on-
session-close ✔ (author: flatten 16:59:30 ET), commission $0 from 2025-02-28 onward.

## Stop/risk lineage (dated)
- ≤2025-10: St… Initial 65 pts → largest losses ≈ −$1,300 caps appear in reports.
- 2026-02-01..06 week: first EXACT −$2,600 largest loss (0115); −1300 co-appears in
  early-2026 short columns; from 2/22 to 8/14 EVERY report's largest loss = exactly
  −$2,600 across BOTH panel families → wrapper/account-level 130-pt (or 2×65-pt)
  hard stop. Never seen in 2025 reports.
- LossLimit 4000→2500 existed only Feb-2025 era (DSTM); D/M group (4500/2000) is the
  later daily-money-management pair (labels D…/M…, enabled by E… checkbox).
