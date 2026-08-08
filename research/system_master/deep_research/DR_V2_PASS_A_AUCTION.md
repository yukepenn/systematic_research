# Deep-research pass A (auction/market-structure), 2026-08-08 — EXTERNAL PRIORS, local data decides

Cost-floor discipline: MNQ OHLCV falsification study (arXiv 2605.04004) killed all 14 continuous per-bar signal families at 2-pt friction → every candidate below is EVENT-CONDITIONED (reference-level or clock-window triggered), targeting ≥3 NQ pts gross/trade. Ranking = edge prior × distinctness from trend-regime fuel.

| rank | hypothesis | trades/day | why it's anti-trend-fuel |
|---|---|---|---|
| 1 | **H1 failed range-break fade** (stop-run reversal at PDH/PDL/ONH/ONL/IB extremes: penetrate ≤0.25×ATR14d, 1m close back inside ≤15min → enter toward VWAP, stop 2t beyond sweep) | 0.5-1.5 | mirror-image of B-MOM; pays on balance days. Osler JF 2003 (stop clustering), Kavajecz-Odders-White |
| 2 | **H3 small-gap fade** (|gap|<0.5×ATR AND open inside prior range → fade to prior close, time-stop 11:30) | 0.4-0.6 | NQ sub-0.3×ATR gaps fill 78%, median 18min; vs B-MOM which goes WITH post-open direction. Lou-Polk-Skouras JFE 2019 |
| 3 | H2 value-area rotation (80%/60% rule: open outside prior VA + 30min acceptance inside → rotate to opposite VA edge) | ~0.2 | responsive rotation, no Solar/B-MOM analog. Dalton; honest base rate ~60% |
| 4 | H9 multi-day balance false-break at 5/20-day extremes (Turtle Soup; close-back-inside conditional) | 1-2/wk | structurally short the fuel Solar burns; swing horizon Solar doesn't trade |
| 5 | H8 midday VWAP-band reversion (11:00-14:00 only; ±2σ same-slot bands; quiet-bar filter) | 0.5-1 | Admati-Pfleiderer dead-zone; SAME slot-σ machinery as B-MOM, OPPOSITE sign, window where B-MOM decays |
| 6 | H7 0DTE round-strike gravitation (after 14:00, low-range days, fade moves off NDX century levels; placebo test at pseudo-levels) | 0.3-0.8 | dealer positive-gamma pinning; era-aligned 2022+. Dim-Eraker-Vilkov |
| 7 | H10 cascade-exhaustion reversal (−2.5σ 30-min move + vol z>3 + range z>3 + rejection close → toward VWAP) | 0.1-0.3 | pays on violent two-way days when Solar whipsaws worst |
| 8 | H12 month-end rebalancing tilt (trading-day-of-month × MTD return sign; turn-of-month drift) | 2-3/mo | calendar flow, zero mechanical contact; needs 2006-2021 structure check (only ~50 dev months) |
| 9 | H6 close-overshoot evening reversion (15:45-16:00 z>2 slot move, opposite-sign day → fade 16:00→18:00/next open) | 2-4/mo | Bogousslavsky-Muravyev; thin-liquidity fragile |
| 10 | H4 last-30-min hedging-flow momentum (first-30m + 13:00-15:30 predictors → 15:30-15:57 with-move) | 0.7 | well-documented (Gao et al. JFE 2018) but correlated with trend fuel; 0DTE era may have inverted it |
| 11 | H5 conditional overnight drift post-down-day | 4-6/mo | DESIGNATED CHEAP KILL: NY Fed 2026 shows unconditional drift ~zero since 2021 |

Portfolio logic: H1/H2/H3/H8/H9 are short the breakout premium Solar+B-MOM are long — they buy back drawdown in balance regimes WITHOUT vetoes or exposure scaling on the trend engines (killed-list compliant). First wave: H1 + H3 (highest prior × cheapest falsification) + H5 (cheap kill); H2/H9 second.

Falsification templates: event studies on 2022-2026 minute bars, conditional forward returns vs unconditional, net t≥2 after $4.36 + 1 tick, N floors stated per engine, walk-forward 2022-24 → 2025-26, PBO on trigger grids. Full citation list in the pass transcript (Osler, Lou-Polk-Skouras, Boyarchenko, Bogousslavsky-Muravyev, Jegadeesh-Wu, Dim-Eraker-Vilkov, Cboe 0DTE, Baltussen et al., Etula et al. Dash-for-Cash, Zarattini ORB, tradingstats gap data).
