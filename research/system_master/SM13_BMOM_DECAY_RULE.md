# SM13 — B-MOM Decay Monitor (PREREGISTERED, frozen 2026-08-08)

Frozen BEFORE any monitoring reading. Applies to every deployed variant carrying the
B-MOM leg (PORT_TILT_532 master; SolarWaveSMOneLot_v1).

> _Object-name mapping (appended 2026-08-18; the frozen rule is unchanged): the deployed
> B-MOM-carrying objects are now `SolarWaveSMMaster_v4` (Product A, successor of the
> PORT_TILT_532 master line) and `SolarWaveOneContractNQ_v5` / `SolarWaveOneContractMNQ_v5`
> (Product B). This monitor applies to them identically; readings occur at each MONITOR-01
> cadence date (`research/operational/MONITORING_CALENDAR.md`)._

**Statistic:** rolling 504-session (2-year) mean of the B-MOM leg's daily net C1 $
(1-NQ basis), computed quarterly at each MONITOR-01 reading from the frozen rule's
own ledger extension (sm_bmom.py on fresh bars; the extension read is an evaluation,
not selection).

**Floor (frozen):** $60/day — half the dev-window mean ($284/day was the W8 dev mean;
pre-2022 the rolling mean NEVER sustained above ~$88/day and was mostly < $0, so the
floor sits between the regimes with margin on both sides.

**Rule:** if the rolling mean prints below the floor at TWO consecutive quarterly
readings: the B-MOM leg is DROPPED from operational variants; weights renormalize to
Solar-tilt only (one-lot: WBmom=0; master: 0.7/0/0.3 → then B1's own concentration
monitor governs). Re-admission requires a fresh preregistered spec, not a re-read.

**Also attached:** MONITOR-01 r-statistic alarms (existing protocol) govern the Solar
leg; B1 top-10-night concentration report continues informationally. Next reading due
≥ 2026-11-01 alongside MONITOR-01 #2.
