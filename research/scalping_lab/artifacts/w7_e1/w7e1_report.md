# W7-3 — E1 event-anchored windows: readout (honest sample-limited handling)

Spec: `specs/W7_rt2_discharge.md` §W7-3 (frozen, committed 1d76c14). RT-2 family 1.2 (EVI rank 2).
Code: `src/python/w7_e1_events.py`. Seed 20260808, 1000 reps, day-clustered CIs, C1 = 2.872t.
Every number below appears in `stdout.txt` / `w7e1_tick_sessions.csv` / `w7e1_tick_minutes.csv` /
`w7e1_minute_trades.csv` / `w7e1_minute_summary.csv` in this directory.

## Headline

- **(a) Tick-level: DESCRIPTIVE ONLY (n=4 event sessions).** No kill/pass claim is made or
  possible. The windows are violent but *quote-alive throughout* with spreads normalizing
  within ~5 minutes — the descriptive picture neither confirms nor excludes a tick-level edge.
- **(b) Minute-powered initial-reaction continuation: NEGATIVE** under the frozen verdict
  rule. No horizon has net-C1 > 0 with CI_lo > 0. Release-day continuation is in fact
  significantly *negative* at 15 and 60 min while the placebo is flat.
- **Zone-F variant: UNTESTABLE-IN-CURRENT-TICK-SAMPLE** (recorded either way per spec — see §4).

---

## 1. (a) Tick descriptive — event sessions in the discovery substrate [DESCRIPTIVE, n=4]

Calendar join (`c01_announcement_calendar.csv`, 145 rows) against the 37 sechilo discovery
sessions finds exactly the RT-2-predicted set — 3 pre-RTH 08:30 releases + 1 in-RTH FOMC:

| session | event | window | max up (t) | max down (t) | window close (t) | spread_t med [0,1) min | spread_t med [5,15) | RV ratio vs pre-event baseline | quote-alive |
|---|---|---|---|---|---|---|---|---|---|
| s20250905 | NFP 08:30 | 08:30–09:45 | +489.0 @ +3627s | −212.0 @ +15s | +378.0 | 8.0 | 3.0 | ×3.5 | 1.000 |
| s20250911 | CPI 08:30 | 08:30–09:45 | +191.0 @ +3752s | −439.5 @ +7s | −101.5 | 15.0 | 3.0 | ×4.3 | 1.000 |
| s20251029 | FOMC 14:00 | 14:00–14:30 | +142.5 @ +24s | −188.5 @ +320s | −17.0 | 13.0 | 3.0 | ×1.9 | 1.000 |
| s20260211 | NFP 08:30 | 08:30–09:45 | +883.0 @ +3662s | −0.5 (never below ref) | +587.5 | 12.0 | 3.0 | ×2.3 | 1.000 |

(Excursions in ticks from the last pre-event mid; sechilo mid is in tick units per house
convention. Full per-minute trajectories in `w7e1_tick_minutes.csv`; per-session path
snapshots at +10s…window end in `w7e1_tick_sessions.csv` and `stdout.txt`.)

Descriptive observations (NOT verdicts):

- **Path**: all three 08:30 sessions show a large first-seconds spike (|Δ| 169–246t within
  10s) that does *not* set the window extreme — the max excursion lands ~60 min later
  (+3627s, +3752s, +3662s) in each 08:30 session. s20250911 (CPI) whipsaws: −240.5t at +10s,
  +73.5t at +60s, −272.5t at +300s. s20260211 (NFP) is monotone-trend up (+883t max, never
  trades below the pre-event mid). The FOMC window is two-sided and smaller (+142.5/−188.5t).
- **Spread**: median spread_t jumps from 2–3t pre-event to 8–15t in the first minute, decays
  to 4–6t by minutes 1–5, and is back at ~3t by minutes 5–15. The first-minute spread alone
  (8–15t) is 3–5× C1 — consistent with RT-2's warning that costs in the release minute are
  the binding constraint for a fast variant.
- **Realized vol**: per-minute tick RV in the event window runs ×1.9–×4.3 the pre-event
  baseline (and ×0.96–×1.9 the same-session RTH baseline; the 2025-10-29 FOMC window is
  *calmer* than what followed it — post-14:30 RV ran ×1.75 the window itself).
- **Liquidity state**: quote-alive fraction is 1.000 in every window; the book never goes
  dark at these events in this sample (s20250902 quote-dead is not an event day and is not
  used here).

**LABEL: DESCRIPTIVE.** n=4 (3 + 1). No kill or pass claim is made, per the frozen spec.

## 2. (b) Minute-powered Program-B study — initial-reaction continuation

Frozen design (as specified): 3-min CSV `runs/AUDIT03_BARS/nq_3m_2022_2026.csv`, dev window
only (519,833 rows kept, 2022-01-02 → 2026-05-31; every row ≥ 2026-06-01 dropped at read).
Bars are end-stamped ET. Signal = sign(close of the bar stamped 09:30 [= price at the 09:30
RTH open] − close of the last bar stamped strictly before 08:30 [the 08:27 bar on all 1,134
simulated days]). Trade at the 09:30 bar close in that direction; market exit at the bar
close 15/30/60 min later; C1 = 2.872t. The CSV is back-adjusted, but all quantities are
same-session price *differences*, so the back-adjustment offset cancels exactly; no
cross-session level is used, so the frozen offset rule (and its ~1t Last-vs-mid error)
is not invoked in this section.

Groups: **release** = 08:30 calendar days (NFP/CPI; 104 in dev window, 102 simulated),
**placebo** = weekdays with no calendar event (998), **fomc_only** = FOMC-14:00-only days
(34; the 08:30-anchored signal is not event-anchored for them — reported as sensitivity,
excluded from both primary and placebo). Exclusions: 2023-04-07 and 2026-04-03 (both NFP on
Good Friday; CME halts 09:15 ET, no 09:30 bar), 9 days no 08:00–08:30 bar, 1 day no exit
bar, 1 zero-signal day.

### Pooled results (net C1 ticks/trade; day-clustered 95% bootstrap CI, 1000 reps, seed 20260808)

| group | h (min) | n | net C1 (t) | CI lo | CI hi | gross (t) | win % |
|---|---|---|---|---|---|---|---|
| release | 15 | 102 | **−53.00** | −97.73 | **−0.38** | −50.13 | 39.2 |
| release | 30 | 102 | −47.74 | −113.22 | +17.04 | −44.87 | 44.1 |
| release | 60 | 102 | **−104.74** | −189.54 | **−17.90** | −101.86 | 43.1 |
| placebo | 15 | 998 | +9.33 | −5.46 | +25.01 | +12.20 | 51.0 |
| placebo | 30 | 998 | +2.44 | −17.73 | +23.97 | +5.31 | 49.5 |
| placebo | 60 | 998 | +12.14 | −11.97 | +38.26 | +15.01 | 50.9 |
| fomc_only | 15 | 34 | −23.28 | −78.05 | +35.37 | −20.41 | 41.2 |
| fomc_only | 30 | 34 | −17.78 | −80.58 | +41.40 | −14.91 | 47.1 |
| fomc_only | 60 | 34 | +18.60 | −82.46 | +122.03 | +21.47 | 52.9 |

### Release days by year (net C1 ticks; placebo mean alongside)

| year | h=15 (n) | h=30 | h=60 | placebo h=15 (n) |
|---|---|---|---|---|
| 2022 | −112.16 (24) | −43.96 | −104.37 | +17.06 (225) |
| 2023 | −21.31 (23) | −49.00 | −81.61 | +7.55 (226) |
| 2024 | −78.16 (24) | −84.12 | −141.29 | +13.53 (228) |
| 2025 | −5.65 (22) | +48.54 | +43.72 | +15.37 (226) |
| 2026 (→May) | −24.87 (9) | −192.98 | −430.21 | −30.00 (93) |

No year shows a positive release-day effect with CI_lo > 0 (full CIs in
`w7e1_minute_summary.csv`); the only positive cells (2025 h=30/60) have CIs spanning zero
(−104.3..+202.3 and −160.2..+217.9).

### Frozen verdict rule applied

Promising iff net C1 > 0 with CI_lo > 0 at any exit horizon AND no comparable placebo
effect. **No horizon qualifies (all three release means are negative). Verdict: NEGATIVE.**

The placebo control behaves as a control should: means +2.4 to +12.1t, all CIs spanning
zero, win rates ~50%.

### Post-hoc observation (NOT a tested hypothesis, NOT a verdict input)

Release-day continuation is significantly *negative* at h=15 (CI −97.7..−0.4) and h=60
(CI −189.5..−17.9) while the placebo is flat — i.e., in this dev window the 08:27→09:30
pre-open reaction tends to *revert* over the next hour on NFP/CPI days. A sign-flipped
(fade) rule is outside the frozen spec, was identified only after unblinding, and its
h=15 significance is marginal; if pursued it requires its own preregistered spec and a
fresh sample. Recorded here for the registry, claimed nowhere.

## 3. Sample-size honesty

- Tick-level (Zone F/S resolution): n=4 event sessions → descriptive only, by construction.
- Minute-level: n=102 release days is powered for the reported effect sizes (per-trade
  std ≈ 244–453t; a +30t true effect at h=15 would give CI half-width ≈ ±47t → detectable
  only at ~2σ; the observed effect is negative in any case).
- FOMC-only n=34: sensitivity only; flat within wide CIs.

## 4. Zone-F variant — closure text (required by spec)

**E1-Zone-F (5–120 s event-anchored, tick-resolution entry at/around the release second) is
UNTESTABLE-IN-CURRENT-TICK-SAMPLE.** The discovery substrate contains exactly 4 event
sessions (3 pre-RTH 08:30 releases: 2025-09-05 NFP, 2025-09-11 CPI, 2026-02-11 NFP; 1
in-RTH FOMC: 2025-10-29). No pass/kill statement about the Zone-F variant is made in either
direction; the descriptive tick evidence (§1) — first-minute spreads 8–15t vs C1 = 2.872t,
window extremes set ~60 min after the release, full quote-alive state — is recorded for any
future spec, and the minute-level NEGATIVE in §2 binds only the 15–60 min continuation
mechanism, not the Zone-F variant. This finding does not block Amendment 6 §9 closure on
E1 grounds provided the closure text carries this UNTESTABLE label (spec W7 §verdict:
"E1 sample-limited" is one of RT-1's four honored text conditions).

## 5. Artifacts

- `w7e1_tick_sessions.csv` — per event-session descriptives (path snapshots, excursions, spreads, RV, alive fraction)
- `w7e1_tick_minutes.csv` — per-minute trajectories, event−15 min → window end (4 sessions)
- `w7e1_minute_trades.csv` — all 1,134 simulated days (date, group, signal, entry/exit stamps, gross/net per horizon)
- `w7e1_minute_summary.csv` — pooled + by-year stats with CIs
- `stdout.txt` — full run log (source for every number above)
