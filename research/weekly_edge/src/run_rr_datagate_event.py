"""DATAGATE - EVENT RESPONSE. How much of the book's decision surface can a scheduled-event
RESPONSE feature actually reach, and what is the minimum detectable effect at that coverage?

RUN CLASS: AUDIT / ENGINEERING_ONLY. No hypothesis is tested, no feature is fitted, no gate is
read. This asks only whether the question is ASKABLE, using the same instrument that closed the
order-flow lane in runs/DATAGATE_ORDERFLOW_20260827/ before a feature was written.

Directive section 49: if a conclusion depends on unavailable coverage, quantify the required sample
size and the MDE, state exactly what would be needed, mark it, and continue other runnable research.
Directive section 20: the effective N for an event-conditioned question is the number of distinct
EVENT SESSIONS, never the number of downstream decisions.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT                                               # noqa: E402

CAL = os.path.join(ROOT, "research", "04_complementary_family", "c01_announcement_calendar.csv")
LEDGER = os.path.join(ROOT, "runs", "RR_W001_ACTION_VALUE_LEDGER", "out", "ledger_p1pct.csv")
XMREF = os.path.join(ROOT, "research", "weekly_edge", "ninjascript", "reference",
                     "xm_reference_decisions.csv")
OUT = os.path.join(ROOT, "runs", "DATAGATE_EVENTRESPONSE_20260827")
os.makedirs(os.path.join(OUT, "out"), exist_ok=True)
Z80 = 1.959963985 + 0.8416212
fh = open(os.path.join(OUT, "out", "datagate.txt"), "w", encoding="utf-8")


def P_(*a):
    print(*a, flush=True)
    print(*a, file=fh)
    fh.flush()


def mde(sd, n_per_group):
    return Z80 * sd * np.sqrt(2.0 / max(n_per_group, 1e-9))


def main():
    P_("=" * 118)
    P_("=== DATAGATE - EVENT RESPONSE.  Is the question ASKABLE with the calendar we hold?")
    P_("=== No hypothesis is tested. No feature is fitted. No gate is read.")
    P_("=" * 118)

    cal = pd.read_csv(CAL)
    cal["date"] = pd.to_datetime(cal["date"])
    cal["mod"] = cal["time_et"].str.slice(0, 2).astype(int) * 60 + \
        cal["time_et"].str.slice(3, 5).astype(int)
    W = cal[(cal["date"] >= "2022-07-01") & (cal["date"] < "2026-08-01")].copy()
    P_("")
    P_(f"    calendar rows           {len(cal):,}   in-window {len(W):,}")
    P_(f"    distinct event SESSIONS in window: {W['date'].nunique():,}")
    P_(f"{'event':<10}{'n':>6}{'time ET':>10}{'available to a 09:45 decision?':>34}")
    for e, g in W.groupby("event"):
        t = g["time_et"].iloc[0]
        P_(f"{e:<10}{len(g):>6}{t:>10}{('YES - lands pre-open' if g['mod'].iloc[0] < 585 else 'NO - lands at 14:00, after'):>34}")

    L = pd.read_csv(LEDGER)
    L = L[L["in_window_session"]].reset_index(drop=True)
    L["session_date"] = pd.to_datetime(L["session_date"])
    L["mod"] = pd.to_datetime(L["decision_ts"]).dt.hour * 60 + \
        pd.to_datetime(L["decision_ts"]).dt.minute
    ev = W.groupby("date")["mod"].min().rename("ev_mod")
    L = L.join(ev, on="session_date")
    L["on_event_day"] = L["ev_mod"].notna()
    L["after_event"] = L["on_event_day"] & (L["mod"] > L["ev_mod"])

    P_("")
    P_("=" * 118)
    P_("=== 1. COVERAGE of P1/PCT's own decision surface")
    P_("=" * 118)
    P_(f"    in-window P1/PCT decisions                     {len(L):>8,}")
    P_(f"    ... on a scheduled-event session               {int(L['on_event_day'].sum()):>8,}"
       f"   {100 * L['on_event_day'].mean():>6.2f} %")
    P_(f"    ... AND after that session's event time        {int(L['after_event'].sum()):>8,}"
       f"   {100 * L['after_event'].mean():>6.2f} %   <- the reachable surface")
    P_(f"    distinct event SESSIONS carrying >=1 decision  "
       f"{L.loc[L['after_event'], 'session_date'].nunique():>8,}   <- the EFFECTIVE N")
    P_("")
    P_("    Directive section 20: 12 P1 opportunities after one CPI print are ONE macro event, not")
    P_("    twelve. The row above is the sample size that governs every inference in this lane.")

    P_("")
    P_("=" * 118)
    P_("=== 2. MINIMUM DETECTABLE EFFECT at that coverage")
    P_("=" * 118)
    sub = L[L["after_event"]]
    sd_all = float(L["delta_action_value"].std(ddof=1))
    sd_sub = float(sub["delta_action_value"].std(ddof=1))
    nsess = sub["session_date"].nunique()
    realized = float(L["baseline_trade_net"].sum())
    BAR = 0.10 * realized / len(L)
    BAR_LANE = 0.10 * realized / len(sub)
    P_(f"    sd(action value), all decisions                ${sd_all:>10,.2f}")
    P_(f"    sd(action value), reachable subset             ${sd_sub:>10,.2f}   <- event sessions are MORE volatile")
    P_(f"    book-wide materiality bar (per decision)       ${BAR:>10,.2f}")
    P_(f"    LANE-SCALED bar - the same total dollars, earned on the {len(sub):,} reachable")
    P_(f"    decisions instead of all {len(L):,}                    ${BAR_LANE:>10,.2f}")
    P_("")
    P_("    The lane-scaled bar is the fair target. A filter that only acts on 7.18 % of the book")
    P_("    must move those decisions ~14x harder to deliver the same book-level improvement, so")
    P_("    comparing this lane's MDE to the book-wide bar would be a units error.")
    P_("")
    P_(f"{'unit of inference':<40}{'N':>8}{'MDE (top-vs-bottom half)':>28}{'vs lane bar':>14}")
    for lab, nn in (("decisions, treated as independent", len(sub)),
                    ("EVENT SESSIONS (the honest unit)", nsess),
                    ("CPI/NFP sessions only (08:30)",
                     int(W[W["mod"] < 585]["date"].nunique())),
                    ("FOMC sessions only (14:00)",
                     int(W[W["mod"] >= 585]["date"].nunique()))):
        m = mde(sd_sub, nn / 2.0)
        P_(f"{lab:<40}{nn:>8,}{m:>27,.2f}{m / BAR_LANE:>13.1f}x")
    P_("")
    P_("    The MDE is for a top-half-versus-bottom-half split on a response feature - the most")
    P_("    generous two-group contrast available. A quintile contrast is strictly worse.")

    P_("")
    P_("=" * 118)
    P_("=== 3. COVERAGE of the one-shot experts")
    P_("=" * 118)
    xm = pd.read_csv(XMREF)
    xm["session_date"] = pd.to_datetime(xm["session_date"])
    xm = xm[(xm["session_date"] >= "2022-07-01") & (xm["session_date"] < "2026-08-01")]
    xt = xm[(xm["desired_direction"] != 0) & (xm["disqualified"] == 0)]
    pre = set(W[W["mod"] < 585]["date"])
    P_(f"    XM_CONFLICT taken decisions                    {len(xt):>8,}")
    P_(f"    ... on a PRE-OPEN event session (08:30)        "
       f"{int(xt['session_date'].isin(pre).sum()):>8,}"
       f"   {100 * xt['session_date'].isin(pre).mean():>6.2f} %")
    P_("    (FOMC at 14:00 is NOT in XM's information set - its decision is at 09:45.)")
    P_("")
    P_(f"    W105b already measured that XM is NOT an event trade: its 304 non-announcement trades")
    P_(f"    earn $408/trade at 54.9 %. W110 measured the announcement FLAG alone at AUC 0.498.")
    P_(f"    Neither of those closes the RESPONSE question - but both bound how much room is left.")

    P_("")
    P_("=" * 118)
    P_("=== 4. WHAT WOULD MAKE THIS ASKABLE")
    P_("=" * 118)
    BAR_LANE = 0.10 * realized / len(sub)
    need_ratio = (mde(sd_sub, nsess / 2.0) / BAR_LANE) ** 2
    P_(f"    Against the LANE-SCALED bar of ${BAR_LANE:,.2f}, the event-session MDE is")
    P_(f"    ${mde(sd_sub, nsess / 2.0):,.2f} - short by a factor of "
       f"{mde(sd_sub, nsess / 2.0) / BAR_LANE:.1f}x.")
    P_(f"    Power scales with N, so the effective N must rise by {need_ratio:,.0f}x - from "
       f"{nsess:,} event sessions to about {nsess * need_ratio:,.0f}.")
    P_(f"    At roughly {len(W) / 49.0:.1f} scheduled events per month that is on the order of")
    P_(f"    {nsess * need_ratio / (len(W) / 49.0) / 12.0:,.0f} YEARS of additional calendar.")
    P_("")
    P_("    That number is a reductio, not a plan. It is printed to make the shape of the problem")
    P_("    explicit: the constraint is the CALENDAR, and no modelling choice moves it.")
    P_("")
    P_("    Adding event TYPES (PPI, retail sales, claims, PCE, GDP, ISM, auctions) is the only")
    P_("    lever that does not require waiting. It is a data-acquisition question, not a research")
    P_("    question, and it belongs in OWNER_QUEUE rather than in a wave.")
    fh.close()


if __name__ == "__main__":
    main()
