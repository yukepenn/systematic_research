# Wave-4 mechanism-expansion passes (2026-08-08) — EXTERNAL PRIORS, local data decides

Mandated by V4 §51 after Engine-3 slate 2's total failure (6/6 externally-sourced reversion
families dead). Three passes ran under Sonnet 5 with WebSearch access; each generated 6-10
ranked candidates deduped against the killed list, explicitly required to fit the joint-loss-
week signature (SMV2Q: low ER150 t=-6.5, high flip rate t=+3.0) rather than merely being event-
triggered. 24 candidates total. Full per-candidate detail (mechanism/counterparty/observables/
falsification/dedup) is in the workflow journal `wf_df9b739b-161`; this page records the
ranked lists and the selection made for SMV2X (engine-3 slate 3).

## Pass D1 — cross-market lead-lag / session structure (ES/NQ/RTY/YM)
1. Cap-tier information-diffusion catch-up (ES/NQ → RTY laggard)
2. Duration-spread reaction to macro-clock shocks (NQ vs RTY/YM)
3. European multinational-exposure session lead (YM → NQ/RTY RTH catch-up)
4. Passive index-mechanics rebalance flow (NDX-100 cap rule / Russell reconstitution)
5. Cross-sectional systematic-vs-idiosyncratic dispersion catch-up (generalized 3-of-4)
6. Weekend information-diffusion lag (Friday RTH consensus → Monday RTY catch-up)
7. Quarterly roll-week differential liquidity migration / basis convergence
DEFERRED — none committed to a slate this wave: ALL require ES/RTY/YM price series, which are
NOT yet exported/committed in this repo (only NQ 3m/1m substrates exist). Candidates 1 and 5
are near-duplicates (test 1 first if this pass is picked up). Candidate 6 sits closest to the
killed overnight-drift/gap-fade family and needs a head-to-head control before being trusted.

## Pass D2 — volatility / dealer-gamma environment as return engines
1. Cross-index dispersion catch-up (NQ↔RTY / ES↔RTY) — DEFERRED, needs RTY (see D1).
2. **Vol-shock systematic deleveraging cascade** — SELECTED for SMV2X seq 396.
3. Dealer short-gamma closing-hour acceleration (0DTE MOC hedging flow) — NQ/ES 1m only;
   candidate for a future slate; risk of overlap with B-MOM's existing intraday capture flagged
   by the pass itself, needs an incremental-info test vs B-MOM before promotion.
4. Large-gap (overnight) information continuation — HIGH dedup risk (same family as killed
   small-gap fade, opposite sign/size population); deferred pending a documented buffer against
   the killed threshold.
5. **Post-macro-announcement drift (FOMC/CPI continuation)** — SELECTED for SMV2X seq 397.
6. **Post-expiration volatility-expansion breakout (OpEx gamma unclamp)** — SELECTED for
   SMV2X seq 398.
7. Volatility-compression squeeze breakout continuation — MEDIUM-HIGH dedup risk (adjacent to
   killed multi-day balance false-break); deferred.
8. Front/next-month calendar-spread funding-stress proxy — low dedup but high build effort
   (needs individual non-back-adjusted contract series + precise roll dates); deferred.

## Pass D3 — flows / positioning / inventory as return engines
1. Quarter-end pension/60-40 rebalancing flow — candidate for a future slate (moderate dedup
   vs killed month-end tilt; needs explicit differentiation, calendar-anchored to quarter only).
2. Terminal-flow / close-auction continuation on calendar-flagged high-volume sessions — strong
   candidate, low dedup; folded conceptually into engine_398's expiration-day framing this wave,
   full standalone version deferred to a future slate if 398 fails.
3. Turn-of-month institutional cash-inflow long bias — HIGH dedup risk vs killed month-end
   MTD-fade tilt; deferred, needs an explicit zero-correlation check against the killed signal.
4. Pre-FOMC announcement drift (flat through the statement) — near-duplicate of D2#5 (opposite
   window: pre- vs post-announcement); D2#5 selected as the more novel/JL-relevant of the pair;
   this one's literature (Lucca-Moench) is itself flagged decay-disputed by the pass.
5. VIX monthly settlement dealer-hedge unwind — candidate for a future slate; only needs
   settlement calendar (not VIX price data) but the pass discloses anecdotal-only grounding.
6. QQQ creation/redemption volume-conditioned overnight continuation — MODERATE-HIGH dedup
   (explicitly killed "overnight drift long" is the nearest neighbor); deferred.
7. Monthly equity opex gamma-pinning compression — HIGH dedup risk (mean-reversion-to-range,
   close to killed value-area rotation / multi-day false-break with only the trigger swapped
   for a calendar anchor); D2#6's continuation framing was selected instead for this reason.
8. Russell reconstitution day NQ compression/spillover — too few events (4-5) for standalone
   statistical validity per the pass's own assessment; not selected.
9. CTA/vol-target rebalancing calendar clustering — flagged HIGHEST dedup risk in the entire
   24-candidate set (likely restates the killed vol-transition-engine/VR/ER/BOCPD state work);
   not selected, not recommended for a future slate without a fresh mechanism.

## Selection rationale (SMV2X seq 396-398)
The three selected engines are the highest-ranked candidates across all three passes that
require NO new data infrastructure (NQ OHLCV + a hardcoded public event calendar only) and are
explicitly CONTINUATION mechanisms rather than range-reversion — the dimension the passes
themselves converged on as the correct differentiation from the six dead reversion families.
Cross-market candidates (D1 entirely, D2#1) are the next-highest-EVI slate but require an ES/
RTY/YM data export first (mirroring the SM1M NQ 1-minute export done this session) — queued,
not dropped.

## Cross-market data export completed (2026-08-08, same day)
ES/RTY/YM 1-minute bars, 2022-01..2026-07-31, exported via SWMinuteExport_v1 through the true
NT8 Strategy Analyzer engine (same provenance chain as the NQ 1m export):
- `runs/SM1M_ES_SUBSTRATE/out/es_1m_2022_2026.parquet` — 1,620,385 bars (ESU6)
- `runs/SM1M_RTY_SUBSTRATE/out/rty_1m_2022_2026.parquet` — 1,568,111 bars (RTYU6)
- `runs/SM1M_YM_SUBSTRATE/out/ym_1m_2022_2026.parquet` — 1,595,378 bars (YMU6)
All three verified against their NT8 job traces (resolved-instrument name + loaded-bar count)
before conversion; raw CSVs kept outside the repo, parquet + build_meta.json committed.
**These are READ-ONLY CONTEXT instruments.** NQ/MNQ remain the only traded instruments in this
program (V4 §0 hard boundary; V4 §36 explicitly authorizes cross-market context data). This
unblocks Engine-3 slate 4 (cross-market lead-lag/dispersion candidates from pass D1 + D2#1,
listed above) — a frozen spec for slate 4 is the next Engine-3 step, not yet written.
