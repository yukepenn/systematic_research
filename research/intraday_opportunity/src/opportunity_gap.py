"""OPPORTUNITY-DENSITY GAP DECOMPOSITION -- reference trader vs the incumbent.

Directive s5 / s32.  This does NOT design a strategy.  It answers, in dollars, WHY the reference
trader's posted throughput looks larger than P1/PCT's, by equalizing the two objects one axis at a
time and showing what each equalization is worth.

EVERY REFERENCE-SIDE NUMBER IS A PIXEL READ OF ONE STRATEGY-ANALYZER BACKTEST GRID the trader
published himself (frame OTRIMG-0002, window 2023-01-01 -> 2025-02-02, captured 2025-02-02 23:57).
It is a BACKTEST, not an account statement; SLIPPAGE = 0; and per his own testimony he ran several
strategies concurrently, so it is ONE SLEEVE, not his trading.  No per-trade record of his exists
anywhere in the 164-image corpus.  Nothing below can change that.
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "out")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
os.makedirs(OUT, exist_ok=True)
_fh = open(os.path.join(OUT, "opportunity_gap.txt"), "w", encoding="utf-8")


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


# ---------------------------------------------------------------- REFERENCE (pixel-read FACTS)
REF = dict(
    source="OTRIMG-0002 Strategy Analyzer summary, window 2023-01-01 -> 2025-02-02",
    net=292_172.82, trades=4_351, longs=2_166, shorts=2_185,
    win_rate=0.4029, profit_factor=1.1764,
    avg_trade=67.15, avg_win=1_111.73, avg_loss=-637.68,
    maxdd=32_677.42, avg_minutes_in_market=94.15,
    nt8_trades_per_day=8.26, implied_days=526.8,
    commission_total=18_187.18, commission_per_rt=4.18, slippage=0.0, qty=1,
)
# ---------------------------------------------------------------- INCUMBENT (measured this session)
FIXED_DD = 20_245.0
P1_SPREAD_PER_RT = 14.44      # the frozen research cost convention for P1
P1_COMM_PER_RT = 4.36
RTH_MIN = 390.0               # 09:30-16:00 ET
FULL_SESSION_MIN = 1_380.0    # 18:00 -> 17:00 ET, the setting his panel actually carried

led = pd.read_csv(os.path.join(ROOT, "runs", "RR_W001_ACTION_VALUE_LEDGER", "out",
                               "ledger_p1pct.csv"))
w = led[led["in_window_session"]]
P1 = dict(net=float(w["baseline_trade_net"].sum()), trades=int(len(w)),
          sessions_total=1058, sessions_active=int(w["session_id"].nunique()),
          avg_trade=float(w["baseline_trade_net"].mean()),
          mean_hold=float(w["baseline_hold_minutes"].mean()),
          median_hold=float(w["baseline_hold_minutes"].median()),
          maxdd=22_930.67, raw_weekly=1_393.57, fixdd_weekly=1_230.36, weeks=213)

P("=" * 112)
P("=== OPPORTUNITY-DENSITY GAP -- reference trader vs P1/PCT.  Decomposition, not a strategy.")
P("=" * 112)
P(f"    reference source : {REF['source']}")
P("    reference class  : BACKTEST, slippage 0, ONE sleeve of several run concurrently,")
P("                       pixel-read from a screenshot. NOT an account statement.")
P("    incumbent source : runs/RR_W001_ACTION_VALUE_LEDGER (certified), in-window, 1,058 sessions")

# ---------------------------------------------------------------- 1. raw throughput
P("")
P("--- 1. RAW THROUGHPUT, as each object reports itself")
ref_per_day = REF["net"] / REF["implied_days"]
p1_per_active = P1["net"] / P1["sessions_active"]
p1_per_cal = P1["net"] / P1["sessions_total"]
rows = [
    ("trades", f"{REF['trades']:,}", f"{P1['trades']:,}"),
    ("sessions / days", f"{REF['implied_days']:,.1f} (NT8 implied)", f"{P1['sessions_total']:,} total / {P1['sessions_active']:,} active"),
    ("trades per day/session", f"{REF['nt8_trades_per_day']:.2f}",
     f"{P1['trades']/P1['sessions_total']:.3f} cal / {P1['trades']/P1['sessions_active']:.3f} active"),
    ("net", f"${REF['net']:,.2f}", f"${P1['net']:,.2f}"),
    ("NET PER TRADE", f"${REF['avg_trade']:,.2f}", f"${P1['avg_trade']:,.2f}"),
    ("net per day/session", f"${ref_per_day:,.2f}", f"${p1_per_active:,.2f} active / ${p1_per_cal:,.2f} cal"),
    ("win rate", f"{REF['win_rate']:.2%}", "35.0 % (approx, from ledger)"),
    ("mean hold (min)", f"{REF['avg_minutes_in_market']:.2f}", f"{P1['mean_hold']:.2f} (median {P1['median_hold']:.0f})"),
    ("direction", f"{REF['longs']:,} L / {REF['shorts']:,} S  TWO-SIDED", "2,131 L / 0 S  LONG-ONLY"),
    ("max drawdown", f"${REF['maxdd']:,.2f}", f"${P1['maxdd']:,.2f}"),
    ("slippage charged", "$0.00  <-- NONE", f"${P1_SPREAD_PER_RT:.2f}/ctrRT modelled spread"),
]
P(f"    {'quantity':<24}{'REFERENCE (backtest)':>34}{'P1/PCT (research)':>38}")
for a, b, c in rows:
    P(f"    {a:<24}{b:>34}{c:>38}")

P("")
P(f"    >>> The reference makes ${REF['avg_trade']:,.2f} per trade. P1/PCT makes ${P1['avg_trade']:,.2f}.")
P(f"    >>> P1/PCT's EDGE PER TRADE IS {P1['avg_trade']/REF['avg_trade']:.2f}x THE REFERENCE'S,")
P(f"    >>> and P1/PCT pays a spread the reference's backtest never charged.")

# ---------------------------------------------------------------- 2. session length
P("")
P("--- 2. THE SESSION-LENGTH ARTIFACT  (this is the single biggest term)")
ref_in_market = REF["nt8_trades_per_day"] * REF["avg_minutes_in_market"]
P(f"    reference in-market minutes/day = {REF['nt8_trades_per_day']:.2f} trades x "
  f"{REF['avg_minutes_in_market']:.2f} min = {ref_in_market:,.1f} min = {ref_in_market/60:.1f} HOURS")
P(f"    RTH is only {RTH_MIN:.0f} min ({RTH_MIN/60:.1f} h)  ->  RTH-ONLY IS ARITHMETICALLY IMPOSSIBLE.")
P(f"    His panel carried TradingHours = 'Use instrument settings' = the FULL "
  f"{FULL_SESSION_MIN:.0f}-min 18:00->17:00 ET session, and a measured overnight hold exists")
P(f"    (a long 21:39 -> 06:44, +$2,270.82). P1/PCT is FLAT AT EVERY SESSION CLOSE.")
P("")
ref_tph = REF["nt8_trades_per_day"] / (FULL_SESSION_MIN / 60)
p1_tph = (P1["trades"] / P1["sessions_active"]) / (RTH_MIN / 60)
ref_dph = ref_per_day / (FULL_SESSION_MIN / 60)
p1_dph = p1_per_active / (RTH_MIN / 60)
P(f"    {'per AVAILABLE market hour':<34}{'REFERENCE':>16}{'P1/PCT':>16}{'ratio':>12}")
P(f"    {'trades per hour':<34}{ref_tph:>16.3f}{p1_tph:>16.3f}{p1_tph/ref_tph:>11.2f}x")
P(f"    {'net dollars per hour':<34}{ref_dph:>16.2f}{p1_dph:>16.2f}{p1_dph/ref_dph:>11.2f}x")
P("")
P("    >>> PER HOUR OF AVAILABLE MARKET, P1/PCT TRADES MORE OFTEN AND EARNS ~3x MORE.")
P("    >>> The reference's throughput advantage is very largely A LONGER TRADING DAY.")

# ---------------------------------------------------------------- 3. cost equalization
P("")
P("--- 3. EQUALIZE THE COST MODEL  (charge the reference what P1 pays)")
spread_bill = REF["trades"] * P1_SPREAD_PER_RT
comm_delta = REF["trades"] * (P1_COMM_PER_RT - REF["commission_per_rt"])
ref_net_equal = REF["net"] - spread_bill - comm_delta
P(f"    reference net as posted                      ${REF['net']:>14,.2f}")
P(f"    less P1's modelled spread {P1_SPREAD_PER_RT:.2f}/ctrRT x {REF['trades']:,}   "
  f"${-spread_bill:>14,.2f}")
P(f"    less commission top-up ({P1_COMM_PER_RT:.2f}-{REF['commission_per_rt']:.2f})/RT      "
  f"${-comm_delta:>14,.2f}")
P(f"    = reference net ON P1'S COST MODEL           ${ref_net_equal:>14,.2f}   "
  f"({ref_net_equal/REF['net']-1:+.1%})")
P(f"    reference net per trade, re-costed           ${ref_net_equal/REF['trades']:>14,.2f}   "
  f"vs P1's ${P1['avg_trade']:,.2f}")
P("")
P(f"    >>> A HIGH-TURNOVER OBJECT IS FAR MORE EXPOSED TO FRICTION. Charging the reference the")
P(f"    >>> same spread P1 pays removes {spread_bill/REF['net']:.1%} of its entire net.")

# ---------------------------------------------------------------- 4. weekly + fixed-DD
P("")
P("--- 4. PUT BOTH ON WEEKLY DOLLARS AT A COMMON FIXED DRAWDOWN")
ref_wk_posted = ref_per_day * 5.0
ref_wk_equal = (ref_net_equal / REF["implied_days"]) * 5.0
k_ref = FIXED_DD / REF["maxdd"]
k_p1 = FIXED_DD / P1["maxdd"]
P(f"    {'':<44}{'weekly $':>14}{'maxDD':>14}{'k':>10}{'@ fixed DD':>14}")
P(f"    {'REFERENCE as posted (backtest, 0 slippage)':<44}{ref_wk_posted:>14,.2f}"
  f"{REF['maxdd']:>14,.2f}{k_ref:>10.4f}{ref_wk_posted*k_ref:>14,.2f}")
P(f"    {'REFERENCE re-costed on P1 cost model':<44}{ref_wk_equal:>14,.2f}"
  f"{REF['maxdd']:>14,.2f}{k_ref:>10.4f}{ref_wk_equal*k_ref:>14,.2f}")
P(f"    {'P1/PCT (research, spread included)':<44}{P1['raw_weekly']:>14,.2f}"
  f"{P1['maxdd']:>14,.2f}{k_p1:>10.4f}{P1['fixdd_weekly']:>14,.2f}")
r1 = ref_wk_posted * k_ref / P1["fixdd_weekly"]
r2 = ref_wk_equal * k_ref / P1["fixdd_weekly"]
P("")
P(f"    reference / P1 at fixed DD, as posted   {r1:.2f}x")
P(f"    reference / P1 at fixed DD, re-costed   {r2:.2f}x   <<< THE HONEST NUMBER")
P("")
P("    ⚠ THREE REASONS THIS STILL FLATTERS THE REFERENCE:")
P(f"      (a) his maxDD is measured over ~{REF['implied_days']/252:.1f} years, P1's over "
  f"~{P1['weeks']/52:.1f} years. Drawdown grows with observation length, so the SHORTER window")
P("          gets a SMALLER denominator and a LARGER fixed-DD figure. Not corrected here.")
P("      (b) re-costing keeps his maxDD at the posted value, but paying the spread would have")
P("          DEEPENED the drawdown, lowering k further.")
P("      (c) his parameters were re-tuned every 1-3 weeks and the run was made the night before")
P("          deployment: the grid is IN-SAMPLE TO HIMSELF. P1's window is discovery-consumed too,")
P("          but P1's figure is at least a walk-forward-refit object.")

# ---------------------------------------------------------------- 5. attribution
P("")
P("--- 5. WHERE THE POSTED DOLLAR GAP ACTUALLY COMES FROM")
gap = ref_wk_posted - P1["raw_weekly"]
P(f"    posted weekly gap (raw, unnormalized)        ${gap:,.2f}/wk")
P("")
P("    decomposition, each term evaluated by holding the others fixed:")
t_cost = (ref_wk_posted - ref_wk_equal)
n_ref_hours = FULL_SESSION_MIN / 60
n_p1_hours = RTH_MIN / 60
ref_wk_if_rth = ref_dph * n_p1_hours * 5.0
t_session = ref_wk_posted - ref_wk_if_rth
P(f"      COST MODEL          his backtest charges no spread            ${t_cost:>12,.2f}/wk")
P(f"      SESSION LENGTH      {n_ref_hours:.0f}h available vs P1's {n_p1_hours:.1f}h RTH          "
  f"${t_session:>12,.2f}/wk")
P(f"      EDGE PER TRADE      P1 earns ${P1['avg_trade']:.2f} vs his ${REF['avg_trade']:.2f}          "
  f"{'IN P1 FAVOUR':>12}")
P(f"      RISK                his maxDD ${REF['maxdd']:,.0f} vs P1's ${P1['maxdd']:,.0f}     "
  f"{'IN P1 FAVOUR':>12}")
P("")
P("    >>> The two terms that CREATE his advantage are a longer trading day and an uncharged")
P("    >>> spread. The two terms where P1 is ahead are edge per trade and drawdown.")

json.dump(dict(reference=REF, incumbent=P1,
               ref_per_day=ref_per_day, p1_per_active=p1_per_active,
               ref_in_market_min_per_day=ref_in_market,
               trades_per_hour=dict(reference=ref_tph, p1=p1_tph),
               dollars_per_hour=dict(reference=ref_dph, p1=p1_dph),
               ref_net_on_p1_costs=ref_net_equal,
               weekly=dict(ref_posted=ref_wk_posted, ref_recosted=ref_wk_equal,
                           p1_raw=P1["raw_weekly"]),
               fixed_dd=dict(ref_posted=ref_wk_posted*k_ref, ref_recosted=ref_wk_equal*k_ref,
                             p1=P1["fixdd_weekly"], ratio_posted=r1, ratio_recosted=r2)),
          open(os.path.join(OUT, "opportunity_gap.json"), "w", encoding="utf-8"),
          indent=2, default=str)
P("")
P("=" * 112)
_fh.close()
