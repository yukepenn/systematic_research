# CAMPAIGN #7 — WEEKLY_EDGE (opened 2026-08-25, owner directive)

## Mission (owner's words, 2026-08-25)
> 先把我们产品拆开，放在1min上面。用他的思路学习到了来做做。总之你看看能不能继续每周赚钱。
> 用到现在的所有思考，各种策略思考不同参数。但是用1min bar or less。
> 最主要还是2026后要每周赚钱。还要比他多比他稳。

Decompose our shipped products into sleeves on NQ 1-minute bars, apply everything learned from
the OTR reconstruction (campaign #6), and build toward **weekly profitability after 2026 —
more and steadier than the original trader's displayed record.**

## Honest goal definition (binding)
"每周都赚钱" is NOT promised and NOT the success criterion — the trader himself displays only
16/21 positive weeks with a −$42,235 week, and R34 proved weekly-green sheets are trivially
manufactured in-sample. The measurable target, evaluated ONLY on frozen configs, net of
frictions, out of sample:

| metric | his displayed benchmark (21 comparable weeks, GROSS) | our target (NET, frozen) |
|---|---|---|
| positive-week rate | 76 % (16/21) | **> 76 %** |
| mean weekly net | $8,583 | **> $8,583** (NQ scale) |
| worst week | −$42,235 | **materially better** |

Asymmetry disclosed: his side is gross-of-commission and display-selected; ours is net and
frozen. Beating his numbers under our measurement standard is therefore a STRICTER bar.

## Binding constraints (inherited, never relax)
1. **Safety boundary** (CLAUDE.md, verbatim force): research/backtest only; never place orders,
   never enable/deploy, never touch Sim101/real accounts, never modify the vendor assembly.
   Deployment decisions belong to the owner alone.
2. **LOCKED_FORWARD**: data ≥ 2026-08-01 is VIRGIN. Build/select on ≤ 2026-07-31 only. Forward
   consumption ONLY via a preregistered champion-vs-challenger protocol written BEFORE the read
   (LOCKED_FORWARD.md), naturally aligned with MONITOR-01 reading #2 (≥ 2026-11-01).
3. **Spec-first**: every run gets `runs/WE_*/spec.yaml` committed before results are read.
4. **No weekly retuning, ever** (R34: V2 transfer is NEGATIVE — $8,130 vs frozen $30,028).
   No selection on net P&L alone; weekly Sharpe + positive-rate + worst-week jointly.
5. **Frictions floor** (CONVENTIONS §3): NQ $4.36/RT base; stress line C1 = 2.872 ticks/RT
   (≈ $14.36/RT all-in). "A result that is positive only below these frictions does not exist."
6. MNQ note: no MNQ bar data exists; MNQ = NQ bars + MNQ economics ($2/pt, $1.30/RT), the
   established convention. All design work here is NQ-denominated.

## What campaign #6 taught us (the design priors of this campaign)
- **Per-trade expectancy, not frequency, is the entire gap** (R34 am.2: his $103/trade gross vs
  our clone's $18.6 at HIGHER frequency).
- **Positive skew** is his money structure (WR 35–45 %, payoff ~1.9, right-tail winners);
  his mature August build trades LESS (~51/wk) and earns MORE per trade ($237).
- **A hard, unconditional per-trade dollar risk cap** (his −$2,600 in 18/24 weeks).
- **The wrapper (entry acceptance / exits / risk / session) is where expectancy lives**, not in
  ever-more signal indicators.
- 1-min decision cadence with tick-informed inputs is his architecture; bar resolution itself
  is not an edge.

## Assets
- Engines (Python, parquet-ready): CAND2+D-gate (`solar_family/src/run_r13_strict_master.py`),
  recovered Solar Wave vendor math (`src/analytics/solarwave.py`), VF clean-room
  (`vwap_flux_family/src`: layer_a_v2 / layer_b_exit / vf_levels / trend_states).
- Products decomposed (scout 2026-08-25): Solar13 ensemble (13 members, VolMult 6–30, sigma =
  trailing mean |Δclose| over VolPeriod 460, clamp [40,1200] ticks) + HTF tilt (50-session SMA,
  ×1.25, rescale 0.9026) + B-MOM RTH breakout (14-day time-of-day band + session VWAP) →
  Product B combiner M = 0.7086·Tp + 2.83·bmom, hysteresis(3.0, 1.0), session filters
  16:30 block / 16:39 flat. Full detail in `runs/WE_W01_SLEEVE_MAP/scout/`.
- Data: NQ 1-min continuous 2022-01-02 18:01 → 2026-07-31 16:59
  (`runs/SM1M_SUBSTRATE/out/nq_1m_2022_2026.parquet`); deep history to 2006 in the scalping-lab
  substrate; NQ tick/BBO 48 sessions 2025-08→2026-05 for later tick-informed inputs.
- Vendor manuals: 18 PDFs in `research/original_trader_reconstruction/vendor_docs/` — signal
  semantics extraction in progress; documented-concept sleeves (S/R zones, OB/OS overlap,
  delta) are W02 material. ninZa free helpers (ATR/MFI/RSI/SMMA/Stoch) installed locally.

## Roadmap
- **W01 SLEEVE_MAP** (now): port the product sleeves to 1-min NQ + Solar×skew-exit grid + VF
  configs; weekly-P&L map on dev (2022-01→2026-05-29) + holdout (2026-06-01→07-31); fixed
  portfolio combos + weekly loss-limit overlay. Output: the honest weekly-profitability map.
- **W02**: manual-derived sleeves (SJB-zone, Multi-Osc overlap, delta-confirm) + VF-oracle
  sleeves if/when the owner buys VWAP Flux (campaign #6 §R33 protocol).
- **W03**: portfolio construction + risk overlays on the surviving sleeves; freeze a champion.
- **FORWARD**: preregister the champion-vs-challenger read; first read at MONITOR-01 #2
  cadence (≥ 2026-11-01, ~13 virgin weeks by then). Then quarterly.

## Status
- 2026-08-25: campaign opened. W01 spec committed; run in progress.
- 2026-08-25 (later): **W01 COMPLETE** (`runs/WE_W01_SLEEVE_MAP/REPORT.md`). Harness PASS to
  the cent. Shortlist EMPTY under R2 — the binding constraint is the worst-week tail. F2
  FIRED: bolt-on skew exits destroy expectancy on our entries. Best objects: **P2 = S1+S4**
  (dev 60.9 % pos / $2,553/wk / Sharpe 0.226) and **S4 = SM14 ported to 1-min** (holdout
  $8,836/wk · 77.8 % · worst −$9,195 · $447/trade — the only object meeting all three
  benchmark numbers, on 9 weeks only). VF clean-room configs and the VF manual preset are
  DOES_NOT_EXIST at stress. B-MOM negative on holdout (decay watch confirmed). W02 = add
  information (tick features, SJB-zone/Multi-Osc sleeves, VF oracle post-purchase); W03 =
  tail control that preserves hit rate.

- 2026-08-25 (later still): **W02 COMPLETE** (`runs/WE_W02_COMPOSER/REPORT.md`). ZERO of
  101 configs clear the preregistered dev tail bar -> no champion, reported honestly. Key
  measurement: per-trade dollar caps are nearly inert on our sleeves (S1 loses 142/13,301
  trades to a 65-pt cap) because **our tail is intra-week accumulation, not single-trade
  catastrophe** -> tail control must be session-level (generalize the D-gate), not
  trade-level. Composition lifts dev Sharpe to 0.267 but 3-sleeve overlap worsens the tail.
  W03 = session-level halts + regime weights (tail axis) and new information bases
  (trend-capture / reversal-zone / delta / overlap - owner freed the base from Solar).

- 2026-08-25 (night): **W03 + W04 COMPLETE.** W03: FIRST 4 configs clear the dev tail bar;
  the **delta-proxy gate** (VF manual's up/down-tick mode as 1-min context) is the best
  mechanism found so far (S4.narrow6.gdl dev Sharpe 0.355, $104.6/trade ~ his $103; champion
  candidate $143.9/trade) but the candidate FAILED holdout confirm (0.180<0.30) -> no
  champion, per prereg. Session halts do what per-trade caps could not. MO base dead; CD
  marginal (better as gate). W04 atoms: single members weak (best 0.106); hysteresis and
  tilt both carry positive marginal value; expectancy lives in the INTERACTION (fast members
  x flow gate x session halt). W05 = freeze challengers C1/C2/C3 + preregister the virgin
  champion-vs-challenger forward read (>=2026-11-01). Holdout now read 4x - exhausted.

- 2026-08-25 (correction): **W03 amendment 1 — look-ahead in context gates** (entry-bar close
  admitted fills at entry-bar open), caught in self-review before any freeze. Lag-corrected
  rerun: the 0.355 headline was substantially artifact; delta gate's REAL marginal is
  +0.02-0.03 Sharpe; `S4.all13.h1300.gdl` still clears the dev tail bar ($110.5/trade, worst
  -$12,915) but fails holdout confirm -> still no champion. Session halts unaffected.
  New standing rule: gates must carry decision-bar info only; explainability review before
  any freeze.

## Relationship to campaign #6 (OTR)
OTR stays open (purchase gate awaiting owner action; free follow-ups queued). #7 consumes #6's
conclusions but never its sealed evidence. Nothing in #7 feeds back into #6's identification
claims.
