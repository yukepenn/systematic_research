# DR-E — GLOBAL STRATEGY REVIEW (owner-requested, 2026-08-08)

Four external-evidence research lanes (retail scalp viability; slower intraday anomalies;
portfolio construction around the proven Solar engine; cost/horizon engineering) run with
web access, synthesized against every local fact this program has measured. Full lane
outputs with citations preserved in the workflow journal; sources include Chague et
al. (SSRN 3423101), Barber/Lee/Liu/Odean (JFM 2014), Baron/Brogaard/Kirilenko (HFT
profits), Aquilina/Budish/O'Neill (QJE latency races), Gao/Han/Li/Zhou (JFE 2018) +
Rosa (2022) decay, NY Fed overnight-drift note, Man/Harvey vol-managed + Cederburg
critique, Moskowitz/Ooi/Pedersen + Baltussen cross-asset trend, Moallemi/Yuan queue
value, McLean/Pontiff publication decay. All external numbers are EXTERNAL PRIOR until
locally reproduced.

## 1. The four-lane convergence

**Lane A (scalp viability): Zone F is externally corroborated dead — not locally
unlucky.** The per-event edge pool at seconds horizons is ~0.5 ticks and is allocated by
latency rank (top-6 firms win >80% of races); the retail market-order taker is the
documented profit SOURCE of HFT (account-level CME data), not a competitor. The only
large-sample retail index-futures day-trading study: 97% of persistent day traders lose
net of fees. Our 8/8 preregistered kills, the P(target) 0.20–0.30 vs BE 0.31–0.40 wall,
and the measured passive-fill adverse selection are the predicted result. Honest prior
that more Zone-F search (as defined) finds a robust edge: **~5%**.

**Lane D (horizon arithmetic): the friction floor sits near 30–60 minutes.** Local
measurement: median RTH |move| ≈ 19t@1min, 42t@5min, 116t@30min, 270t@2h (~h^0.57).
Required capture rate (honest 3.5t RT / median move): 18%@1min, 8.4%@5min, 3.0%@30min,
1.3%@2h. A realistic PF-1.1-class engine captures ~4% (Solar measured: 10.95t gross at
108-min holds ≈ 4% of the 2h move). ⇒ arithmetic breakeven ≈ 15min; comfortable
viability ≥ 30–60min. **≤5min holds are arithmetically dead at market-order friction.**

**Lane B (where documented edges live): 30min–multi-day, in basis points.** Surviving
candidates for us, in order: intraday momentum family (last-half-hour + noise-area/VWAP
variants — CONTESTED in the literature, cheap to resolve on our 2005–2026 minute data,
but predicted highly correlated with Solar); overnight close→open premium (the only
Solar-ORTHOGONAL stream by construction — Solar is flat by 16:44; must verify post-2018
aliveness; the famous 2–3am component is officially dead); announcement-day conditioning
(overlay, not standalone — pre-FOMC drift died post-2015); turn-of-month (low prior).
Dead: day-of-week, sub-minute anything.

**Lane C (portfolio math): the cheapest certain win is sizing, and the real second-engine
route is cross-ASSET, not cross-index.** Full Kelly for a Sharpe≈0.97, ~$80k/yr/contract
engine ≈ 1 NQ per ~$85k equity — a small account running 1 NQ is likely AT/ABOVE full
Kelly, actively hurting geometric growth; MNQ granularity at 0.25–0.4 Kelly is pure
arithmetic improvement (margin was never the binder). ES/YM/RTY ports are near-worthless
as diversifiers (underlying ρ≈0.93; a second long-only engine only adds value if its
standalone Sharpe > ρ×0.97). Cross-asset persistence (GC/CL screen) is externally
supported (trend is near-universal; cross-class strategy ρ is low) and reuses 100% of
our validated machinery — including the W2-0-corrected null discipline, which now makes
the r-screen scientifically sound (matched sign-flip nulls per instrument, DIRECT
economics only). A genuinely ρ≤0.3 second engine of equal Sharpe ⇒ portfolio Sharpe
+~29%, geometric growth +~67%; at ρ≥0.5 it is leverage in disguise — kill.

## 2. Local-evidence overrides (where lanes conflict with what we measured)

- Meta-labeling/regime overlays ON SOLAR (lane A's R4): local falsifications win —
  day-level state signals (AUC 0.556–0.575) and every suppression variant were
  tail-adverse at PF 1.11. That axis stays CLOSED. The only admissible new angle is
  mechanically different DATA: per-trade micro-state scoring (spread/flow at entry
  time) from the scalp campaign's tick substrate — data that did not exist during
  Family-A research. Role-B/C per Amendment 4 §11 applied to Solar as the base engine.
- Vol-targeted sizing: admissible ONLY as continuous fractional-Kelly scaling (lane C
  R1); anything that suppresses trades re-enters the falsified axis and is banned.
- Intraday-momentum family: H-A1's kill (rest-of-day→last-30min, 3-min bars, decayed
  post-2022) stands; the broader family is mechanically different but must pass the
  correlation pre-gate (predicted ρ>0.5 vs Solar) BEFORE any build spend.

## 3. THE GLOBAL PROGRAM (ranked; each item preregistered before readout)

**P0 — Sizing policy (immediate, zero data cost, certain sign).** Compute fractional-
Kelly MNQ schedule for R5-E10 v2 from existing daily_equity ledgers; stationary-
bootstrap DD at c∈{0.25,0.35,0.5}; freeze the schedule + a mechanical de-risking
trigger tied to MONITOR-01. This is where geometric growth actually comes from.

**P1 — Execution dollars on the proven engine (uses existing BBO substrate).**
(a) Patient-exit overlay test: limit-at-touch posted early for TIME-TRIGGERED exits
(16:44 flatten etc.), forced cross at deadline — time-triggered orders carry no
information, so adverse selection should not apply; expected +0.5–1t/exit ≈ +10% of
Solar net if it survives. (b) Stop/exit realism audit: through-print stop slippage and
touch-no-fill rates from our own tick data. Signal-entry patience expected to FAIL
(momentum non-fills concentrate in the best trades) — tested to close it.

**P2 — Second-engine search, hard-gated by correlation (<0.3 daily, ≤0 losing-day).**
(a) Overnight premium 16:44→09:30 on NQ 2005–2026 minute data (orthogonal by
construction; MNQ prototype — overnight needs full margin; post-2018 subsample
decisive). (b) Intraday-momentum family — but FIRST compute its daily P&L from
existing minute data and correlate against Solar's ledger; if ρ≥0.5 (predicted),
reject without building. (c) Cross-asset r-screen: GC, CL, RTY, ZN minute bars through
the DC ladder WITH per-instrument sign-flip nulls and per-instrument friction
conversion; survivors (prior: GC/CL genuine test, ZN expected spread-bound, ES/YM
expected correlation-killed) get a Solar-class strategy build.

**P3 — Scalp campaign disposition.** (a) **Zone F formally CLOSED** (externally
corroborated; REJECTED_IDEAS entry cites lanes A+D; reopen only if some preregistered
family shows ≥+7pp lift on discovery AND holdout). (b) **Horizon-floor gate adopted:
no new family with median hold <30min RTH** unless preregistered capture-rate evidence
clears 2× friction/median-move. (c) ONE final migration experiment (doubles as the
CLEAN-seed test and the §34 verdict): CLEAN/DIRTY conditioning at 10–60min holds,
40–80t brackets, C1+C2, sealed-holdout-eligible if discovery passes. If it fails, the
campaign declares **NO QUALIFIED FAST NQ SCALPING EDGE FOUND IN THE TESTED RESEARCH
UNIVERSE** per mandate §34 — with the search now externally cross-validated.
(d) Substrate is NOT wasted: it becomes (i) the execution-realism lab for P1, (ii)
per-trade micro-state features for Solar role-B/C, (iii) the ES/cross-market regime
feature source at ≥1min lags.

**P4 — Explicitly closed (do not fund):** seconds-scale ES lead-lag (consumed inside
microsecond races); retail queue/market-making and "join queue early" families (no MBO
data, queue value accrues to the front, our own fills measured adversely selected);
regime suppression on Solar; standalone pre-FOMC drift; day-of-week; ES/YM index ports
except through the free r-screen; MNQ for scalp economics (corrected C1 4.6t).

## 4. What this answers for the owner

The manual experience ("几十秒抓 5 个点") is real as a PATH property — median 60s MFE is
exactly 20t — but the census, the path toll, the eight kills, and the external record
agree it is not harvestable by a retail flow-taker at that horizon: the favorable
excursion exists, the after-cost claim on it does not. The discretionary skill, if it
exists, lives in selectivity+location at MINUTES scale — which is exactly where the
surviving research program (P2/P3c) now points. The scalping campaign's real product is
the substrate, the execution numbers, the corrected null discipline, and a hard,
externally-corroborated boundary of where NOT to spend the next year.

Stop-condition note: this review satisfies the "remaining high-EVI hypotheses" audit of
mandate §35; the campaign continues with P0–P3 as the funded queue.
