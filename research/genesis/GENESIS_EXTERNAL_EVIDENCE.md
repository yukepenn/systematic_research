# GENESIS EXTERNAL EVIDENCE — literature verdicts for NQ mechanisms

**State document.** From `runs/GENESIS_W1_FORENSICS_20260828` (F1/F2 full reports, with citations).
External literature motivates experiments; it validates nothing here. Standing haircut:
McLean-Pontiff (JF 2016) — effects run −26% out-of-sample, −58% post-publication.

## DEAD — do not seed hypotheses from these

| effect | killed by |
|---|---|
| overnight drift (2–3am window) | the authors' own 2026 update: ≈0 since 2021 |
| pre-FOMC 24h drift | dead post-2015 (Kurov et al. FRL 2021) |
| day-of-week | dead since ~2004 (Kohers et al.) — note repo never tested it either |
| ES/NQ 1-min lead-lag | arbitraged to milliseconds (Budish QJE 2015; Hasbrouck 2003) |
| single-index TSMOM | existence contested (Huang et al. JFE 2020) + post-2012 lost decade |
| ORB as marketed | un-refereed, leverage-inflated; contradicted net-of-cost on MNQ (arXiv 2605.04004: 14 OHLCV families on 5-min MNQ, nothing survives 2-pt friction) |
| seconds-scale OFI taking | OFI shocks dissipate ≤1s (arXiv 2508.06788); dead at our ≈3.8-tick cost bar |
| VPIN/BVC toxicity products | classification artifact; zero incremental power (Andersen-Bondarenko) |
| GEX dashboards / dealer-gamma labels | mechanism real (Ni et al. RFS 2021) but dealer-sign assumption never validated; OI EOD-stale; 0DTE never enters OI |
| retail queue/liquidity provision | structurally adversely selected at retail latency (Budish; Donnelly-Gan: queue-awareness worth ~2.5% even for professionals) |

## ALIVE with mechanism — hypothesis-atlas seeds, in evidence order

1. **VIX term-structure state as conditioner** — strongest evidence-per-dollar found. Cheng (RFS
   2019): ex-ante VIX premium predicts VX returns, coeff ≈1; VX leads spot intraday (Frijns);
   contango/backwardation as risk regime survives (naive short-vol died 2018-02-05). Data: free
   Cboe files + **VXN** (NQ-native, never used by anyone here).
2. **Intraday momentum via hedging demand** — first half-hour → last half-hour (Gao/Han/Li/Zhou
   JFE 2018; mechanism: gamma hedging + lev-ETF rebalancing, Baltussen et al. JFE 2021;
   replicated in 16 markets). ⚠️ decaying: OOS Sharpe 0.39 (2024–26 replication). Conditioning
   (volatile/high-volume/news days) is where the residual lives. NOTE: overlaps FOLLOW_MORNING
   (W114) — the repo independently found this class alive.
3. **Scheduled-event-day conditioning** — announcement-day premium 10.6 vs 1.0 bps/day
   (Savor-Wilson); macro drift ~30min pre-release is timing/vol structure (Kurov JFQA 2018).
   N-bound for magnitude work, but day-type conditioning needs only the calendar (BLS calendar
   already committed, unjoined).
4. **FOMC-cycle weeks** (Cieslak et al. JF 2019; weeks 0/2/4/6, partial attenuation recorded).
5. **Turn-of-month** (McConnell-Xu FAJ 2008; cross-country, century-scale).
6. **OPEX-week delta-hedge premium** (Stivers-Sun JBF 2013; 0DTE-era break risk noted).
7. **VRP forecasting at weekly-monthly horizon** (Bollerslev-Tauchen-Zhou RFS 2009, >15%
   quarterly R²) — needs implied vol (free VIX/VXN levels suffice for a first pass).
8. **Vol-managed sizing** (Moreira-Muir vs Cederburg caveats) — a RISK SPECIFICATION, not alpha;
   never to be classified as information.

## Data implications (F2)

**Every strongly-evidenced, retail-implementable mechanism above needs ZERO depth history.**
Depth genuinely unlocks only multi-level OFI and queue research — both execution-relevant, not
alpha-relevant, at 1-contract scale. The pending Databento question is therefore an
**execution/cost-model falsifier** (bounded MBP-10 pilot: was $14.44 vs $24.00/RT right?), not an
alpha acquisition. CME futures carry aggressor side natively; BBO-level classification in ES is
near-perfect (Andersen-Bondarenko) — the local ES/NQ BBO stores are sufficient for flow-signing
research if ever needed.
