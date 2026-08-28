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
# ⚠ CORRECTED 2026-08-28. The FIRST version of this section asserted that P1/PCT is "RTH only,
# flat at every session close" and divided its dollars by 6.5 hours. THAT WAS FALSE and it
# propagated into the owner's directive. Measured from the ledger's own decision timestamps:
# P1/PCT places entries in 23 of 24 hours -- every hour except 17:00, the CME maintenance break.
# 61.7 % of its entries and 45.7 % of its net are OUTSIDE 09:00-15:59 ET.
# "Flat at every session close" means the 17:00 SESSION close, not the 16:00 RTH close.
P("")
P("--- 2. SESSION LENGTH -- and the FIRST VERSION OF THIS SECTION WAS WRONG")
led2 = led[led["in_window_session"]].copy()
led2["h"] = pd.to_datetime(led2["decision_ts"]).dt.hour
hrs = sorted(led2["h"].unique())
n_act = int(led2["session_id"].nunique())
tr = len(led2)
net_ = float(led2["baseline_trade_net"].sum())
inmkt_min = float(led2["baseline_hold_minutes"].sum()) / n_act
rth = led2[(led2["h"] >= 9) & (led2["h"] < 16)]
P(f"    P1/PCT places entries in {len(hrs)} of 24 hours. Missing: "
  f"{[h for h in range(24) if h not in set(hrs)]} (the 17:00 CME maintenance break).")
P(f"    entries OUTSIDE 09:00-15:59 ET : {tr-len(rth):,} of {tr:,} = {(tr-len(rth))/tr:.1%}")
P(f"    net    OUTSIDE 09:00-15:59 ET : ${net_-float(rth['baseline_trade_net'].sum()):,.0f} "
  f"= {(net_-float(rth['baseline_trade_net'].sum()))/net_:.1%} of net")
P("")
P("    >>> THERE IS NO OFF-HOURS COVERAGE GAP. P1/PCT ALREADY TRADES THE WHOLE SESSION.")
P("    >>> The claim 'P1 uses only 6.5 of 23 hours' is RETRACTED. It came from reading")
P("    >>> 'flat at every session close' as the 16:00 RTH close; it is the 17:00 SESSION close.")

ref_inmkt_h = REF["nt8_trades_per_day"] * REF["avg_minutes_in_market"] / 60.0
p1_inmkt_h = inmkt_min / 60.0
P("")
P(f"    The real difference is EXPOSURE TIME, not operating window:")
P(f"    {'':<36}{'REFERENCE':>14}{'P1/PCT':>14}{'ratio':>12}")
P(f"    {'IN-MARKET hours per session':<36}{ref_inmkt_h:>14.2f}{p1_inmkt_h:>14.2f}"
  f"{p1_inmkt_h/ref_inmkt_h:>11.2f}x")
avail = FULL_SESSION_MIN / 60.0
ref_tph = REF["nt8_trades_per_day"] / avail
p1_tph = (tr / n_act) / avail
ref_dph = ref_per_day / avail
p1_dph = (net_ / n_act) / avail
P(f"    {'trades per AVAILABLE hour (23h)':<36}{ref_tph:>14.3f}{p1_tph:>14.3f}"
  f"{p1_tph/ref_tph:>11.2f}x")
P(f"    {'net $ per AVAILABLE hour':<36}{ref_dph:>14.2f}{p1_dph:>14.2f}{p1_dph/ref_dph:>11.2f}x")
ref_dpih = ref_per_day / ref_inmkt_h
p1_dpih = (net_ / n_act) / p1_inmkt_h
P(f"    {'net $ per IN-MARKET hour':<36}{ref_dpih:>14.2f}{p1_dpih:>14.2f}"
  f"{p1_dpih/ref_dpih:>11.2f}x")
ref_dpih_recost = (REF["net"] - REF["trades"] * P1_SPREAD_PER_RT
                   - REF["trades"] * (P1_COMM_PER_RT - REF["commission_per_rt"]))     / REF["implied_days"] / ref_inmkt_h
P(f"    {'  same, reference RE-COSTED':<36}{ref_dpih_recost:>14.2f}{p1_dpih:>14.2f}"
  f"{p1_dpih/ref_dpih_recost:>11.2f}x")
P("")
P("    >>> The reference is EXPOSED 2.7x LONGER but earns LESS PER HOUR OF EXPOSURE.")

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
t_cost = ref_wk_posted - ref_wk_equal
# EXPOSURE term: what the reference would earn per week if exposed only as long as P1 is, at his
# own dollars-per-in-market-hour. This replaces the RETRACTED "session length" term.
ref_wk_if_p1_exposure = ref_dpih * p1_inmkt_h * 5.0
t_exposure = ref_wk_posted - ref_wk_if_p1_exposure
P(f"      COST MODEL          his backtest charges no spread            ${t_cost:>12,.2f}/wk")
P(f"      EXPOSURE TIME       {ref_inmkt_h:.1f} in-market h/day vs P1's {p1_inmkt_h:.1f}      "
  f"${t_exposure:>12,.2f}/wk")
P("      ~~SESSION LENGTH~~  RETRACTED: P1 already trades 23 of 24 hours. What remains is an")
P("                          EXPOSURE-TIME difference - a hold-time and trade-count property, not")
P("                          a window property - and it is NOT free: it carries overnight gap risk")
P("                          and off-hours spread that his zero-slippage backtest never paid.")
P(f"      EDGE PER TRADE      P1 earns ${P1['avg_trade']:.2f} vs his ${REF['avg_trade']:.2f}"
  f"{'IN P1 FAVOUR':>26}")
P(f"      EDGE PER IN-MKT HR  P1 ${p1_dpih:,.2f} vs his ${ref_dpih:,.2f} "
  f"(${ref_dpih_recost:,.2f} re-costed){'IN P1 FAVOUR':>13}")
P(f"      RISK                his maxDD ${REF['maxdd']:,.0f} vs P1's ${P1['maxdd']:,.0f}"
  f"{'IN P1 FAVOUR':>18}")
P("")
P("    >>> His advantage is EXPOSURE TIME plus an UNCHARGED SPREAD.")
P("    >>> P1 is ahead on edge per trade, edge per hour of exposure, and drawdown.")

json.dump(dict(reference=REF, incumbent=P1,
               ref_per_day=ref_per_day, p1_per_active=p1_per_active,
               ref_in_market_hours_per_day=ref_inmkt_h,
               p1_in_market_hours_per_session=p1_inmkt_h,
               trades_per_hour=dict(reference=ref_tph, p1=p1_tph),
               dollars_per_available_hour=dict(reference=ref_dph, p1=p1_dph),
               dollars_per_inmarket_hour=dict(reference=ref_dpih, reference_recosted=ref_dpih_recost, p1=p1_dpih),
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
