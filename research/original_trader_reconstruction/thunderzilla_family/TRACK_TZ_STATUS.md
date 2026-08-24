# TRACK TZ — ThunderZilla status (re-evaluated 2026-08-24, owner directive §1/§12)

**Classification: MEDIUM / CONDITIONAL HYPOTHESIS (downgraded per owner ruling).
Search continues; NO purchase; not treated as identified.**

## Why downgraded (evidence recap)

1. "Signal Quantity Per Trend" is NOT a unique TZ fingerprint — it is a documented VWAP
   Flux parameter (manual §2.11), and the EV-006 screenshot containing that label is now
   identified as VWAP Flux. The TZ changelog match (2025-08-11) remains real but
   redundant as an identifier.
2. TZ is documented Renko-exclusive (ninZaRenko/KingRenko$); the confirmed 2026 system
   runs on NQ 1-minute primary.
3. TZ's documented parameter structure (MA Type/Period/Smoothing×3/Stop Offset/Qty Per
   Flat) does NOT match any EV-007 multi-block group.
4. Not installed locally (EV-021).

## What keeps it alive

- Same vendor ecosystem; Signal_Trade alphabet (±1 start / ±2 slowdown / ±3 pullback /
  ±4 move-stop) is Solar-DNA — a natural upgrade path for this trader.
- The settings screenshots crop below "Signal Quantity Per Flat" — unseen rows exist.
- Bar types of the EV-007 screenshots are UNKNOWN (if any shows Renko bars or a
  secondary Renko series, TZ re-upgrades immediately).

## §12 investigation items

- "Did any original SA strategy add an internal secondary KingRenko/ninZaRenko series
  while showing a 1-minute primary?" — NOT DETERMINABLE from transcribed evidence; the
  original screenshot IMAGES are needed (repo contains zero image files). → owner input.
- "Do any screenshots show TZ-specific MA Type/Period/multi-smoothing/Stop Offset/Qty
  Per Flat?" — the documented TZ numeric signature would read like
  [enum][num 60-100][bool][enum][10][num 60-150][1]. No EV-007 block matches this shape.
  The pair-groups like [14, 6] resemble Renko BAR settings (X/Y), not TZ parameters —
  if the trader ran ANY Renko-based sleeve, such pairs could appear in a Data Series
  pane rather than an indicator pane. → flagged for the layout-matching matrix.

## Standing conclusion

TZ remains a candidate for a POSSIBLE OTHER SLEEVE (not the main 1-min Volume/VWAP
strategy). Upgrade triggers: (a) a screenshot showing Renko bars / TZ-specific labels;
(b) a below-crop TZ parameter list matching an EV-007 block; (c) owner recollection of
the vendor/system name for the multi-block screenshots.
