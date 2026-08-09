"""V1f -- SCHEDULED-EVENT DAYS AS A *LEVERAGE* CONSTRAINT (not a selectivity idea).

BROKER FACT (MEGA PROMPT V6 wave 17, owner-supplied, NinjaTrader Brokerage Lifetime):
    "Intraday margin may be set to 4X standard rates at least 15 minutes before key
     economic news releases, and margin may be raised in real time without notice."
    NQ  day margin $1,000  -> $4,000 at 4X ; initial (overnight) margin $43,433.67
    MNQ day margin $  100  -> $  400 at 4X ; initial (overnight) margin $ 4,343.38

WHAT THIS SCRIPT DOES
  1. Builds an auditable scheduled-event calendar for the dev window
     2022-01-03 .. 2026-05-29 (FOMC decision days, CPI, NFP/Employment Situation,
     PCE/Personal Income & Outlays), with an explicit per-date provenance TIER.
     -> written next to this script as v1f_event_calendar.csv
  2. Attributes realized session P&L of the three campaign objects to those sessions
     (share of net, share of worst-day losses, per-year), with placebo and
     date-dilation robustness.
  3. Answers THE LEVERAGE QUESTION: at each capital level in the *existing committed*
     capital maps, does drawdown-based sizing bind first, or does 4X event-day margin?

HONEST FRAMING (repeated in the report, non-negotiable):
  The 4X policy applies GOING FORWARD. No backtest in this repo ever experienced it.
  Nothing here is a correction to historical P&L. It is a constraint on DEPLOYABLE
  leverage only. Historical returns are NOT restated as if the multiplier had applied.

  2006-2021 data is NOT touched anywhere in this script. Every magnitude below comes
  from the dev window 2022-01-03..2026-05-29 only. Data >= 2026-08-01 is
  LOCKED-FORWARD and is not read.

RUN:  python runs/W17_C4_COMPLIANCE/src/v1f_eventdays.py
"""
import os
import sys
import json
from datetime import date, timedelta

import numpy as np
import pandas as pd
from scipy.stats import hypergeom

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
os.chdir(ROOT)
sys.path.insert(0, "src/analytics")

SRC = "runs/W17_C4_COMPLIANCE/src"
OUT = "runs/W17_C4_COMPLIANCE/out"
os.makedirs(OUT, exist_ok=True)

DEV_START = pd.Timestamp("2022-01-03")
DEV_END = pd.Timestamp("2026-05-29")   # dev window per LOCKED_FORWARD.md
SEED = 20260809

# ===========================================================================
# SECTION A -- SCHEDULED-EVENT CALENDAR
# ===========================================================================
# PROVENANCE TIERS (recorded per row in the CSV; never averaged away):
#   RULE            deterministic published rule, validated below against checkpoints
#   RECALL          hardcoded from model recall of a published calendar; NOT verified
#                   against a live source (no web access permitted for this task)
#   RULE_APPROX     rule that is known NOT to be exact; measured hit-rate reported
#   UNVERIFIED      cannot be established: 2025-26 federal-shutdown disruption window,
#                   or forward extrapolation. Carried in the CSV but excluded from the
#                   CORE calendar and reported as a sensitivity.
# ---------------------------------------------------------------------------

def us_federal_holidays(y0=2021, y1=2027):
    """Federal holidays incl. the Sat->Fri / Sun->Mon observance rule.
    Used only to (a) shift BLS releases off holidays, (b) count business days."""
    out = set()

    def nth_weekday(y, m, wd, n):
        d = date(y, m, 1)
        d += timedelta(days=(wd - d.weekday()) % 7)
        return d + timedelta(days=7 * (n - 1))

    def last_weekday(y, m, wd):
        d = date(y, m + 1, 1) - timedelta(days=1) if m < 12 else date(y, 12, 31)
        return d - timedelta(days=(d.weekday() - wd) % 7)

    def observed(d):
        if d.weekday() == 5:
            return d - timedelta(days=1)
        if d.weekday() == 6:
            return d + timedelta(days=1)
        return d

    for y in range(y0, y1 + 1):
        out.add(observed(date(y, 1, 1)))
        out.add(nth_weekday(y, 1, 0, 3))            # MLK
        out.add(nth_weekday(y, 2, 0, 3))            # Washington's Birthday
        out.add(last_weekday(y, 5, 0))              # Memorial Day
        out.add(observed(date(y, 6, 19)))           # Juneteenth (federal from 2021)
        out.add(observed(date(y, 7, 4)))
        out.add(nth_weekday(y, 9, 0, 1))            # Labor Day
        out.add(nth_weekday(y, 10, 0, 2))           # Columbus Day
        out.add(observed(date(y, 11, 11)))          # Veterans Day
        out.add(nth_weekday(y, 11, 3, 4))           # Thanksgiving
        out.add(observed(date(y, 12, 25)))
    out.add(date(2025, 1, 9))   # National Day of Mourning (Carter) -- one-off federal closure
    return out


FED_HOL = us_federal_holidays()


def is_bd(d):
    return d.weekday() < 5 and d not in FED_HOL


def prev_bd(d):
    while not is_bd(d):
        d -= timedelta(days=1)
    return d


def nth_bd_of_month(y, m, n):
    d = date(y, m, 1)
    c = 0
    while True:
        if is_bd(d):
            c += 1
            if c == n:
                return d
        d += timedelta(days=1)


def last_friday(y, m):
    d = date(y + (m == 12), (m % 12) + 1, 1) - timedelta(days=1)
    return d - timedelta(days=(d.weekday() - 4) % 7)


# ---- 2025-26 federal shutdown: BLS/BEA release schedules were disrupted -----
# The Oct 1 - mid-Nov 2025 federal shutdown delayed/cancelled BLS and BEA releases
# (the Sept-2025 Employment Situation slipped out of its scheduled slot; at least one
# monthly CPI was not published on schedule). The exact re-scheduled dates cannot be
# established without a source, so every RULE/RULE_APPROX BLS/BEA date whose scheduled
# day falls in this window is downgraded to UNVERIFIED rather than guessed.
SHUTDOWN_LO = date(2025, 10, 1)
SHUTDOWN_HI = date(2026, 1, 31)


def shutdown_hit(d):
    return SHUTDOWN_LO <= d <= SHUTDOWN_HI


# --------------------------- NFP / Employment Situation ---------------------
# RULE (documented by BLS): the Employment Situation is released on the THIRD FRIDAY
# after the conclusion of the reference week, where the reference week is the
# Sunday-Saturday week containing the 12th of the reference month. If that Friday is a
# federal holiday the release moves to the preceding business day.
# This reproduces the familiar "first Friday of the following month" in most months and
# correctly handles the months where it is the second Friday.
NFP_OVERRIDES = {
    # rule date -> (actual date, reason).  RECALL tier.
    date(2025, 1, 3): (date(2025, 1, 10),
                       "BLS annual schedule placed the Dec-2024 Employment Situation on "
                       "Jan 10 2025; Jan 9 2025 was a federal closure (Day of Mourning)"),
}


def nfp_release(ref_y, ref_m):
    twelfth = date(ref_y, ref_m, 12)
    # Sunday-Saturday week containing the 12th: Saturday that ends it
    # python weekday(): Mon=0..Sun=6 ; Sunday-start week -> offset
    dow_sun_start = (twelfth.weekday() + 1) % 7          # Sun=0 .. Sat=6
    week_end_sat = twelfth + timedelta(days=(6 - dow_sun_start))
    d = week_end_sat
    fridays = 0
    while fridays < 3:
        d += timedelta(days=1)
        if d.weekday() == 4:
            fridays += 1
    tier, note = "RULE", "BLS third-Friday-after-reference-week rule"
    if d in NFP_OVERRIDES:
        d, why = NFP_OVERRIDES[d]
        tier, note = "RECALL", "override: " + why
    elif d in FED_HOL:
        d = prev_bd(d)
        tier, note = "RULE", "third-Friday rule, shifted off federal holiday to prior business day"
    return d, tier, note


# --------------------------------- CPI --------------------------------------
# NO exact public rule exists. RULE_APPROX used: the 8th business day of the release
# month (federal holidays excluded). Hit-rate against checkpoints is MEASURED below and
# printed; it is NOT assumed. All CPI rows carry tier RULE_APPROX (or UNVERIFIED).
CPI_CHECKPOINTS = {   # RECALL, used ONLY to measure the rule's accuracy, not as data
    (2022, 1): date(2022, 1, 12), (2022, 2): date(2022, 2, 10), (2022, 3): date(2022, 3, 10),
    (2022, 4): date(2022, 4, 12), (2022, 5): date(2022, 5, 11), (2022, 6): date(2022, 6, 10),
    (2022, 7): date(2022, 7, 13), (2022, 8): date(2022, 8, 10), (2022, 9): date(2022, 9, 13),
    (2022, 10): date(2022, 10, 13), (2022, 11): date(2022, 11, 10), (2022, 12): date(2022, 12, 13),
}


def cpi_release(rel_y, rel_m):
    return nth_bd_of_month(rel_y, rel_m, 8), "RULE_APPROX", "8th business day of the release month"


# --------------------------------- PCE --------------------------------------
# BEA Personal Income & Outlays. RULE_APPROX: the last Friday of the release month.
# Hit-rate measured below against checkpoints and reported; known to fail in
# Nov/Dec (holiday pull-forward) and occasionally Feb.
PCE_CHECKPOINTS = {
    (2023, 1): date(2023, 1, 27), (2023, 2): date(2023, 2, 24), (2023, 3): date(2023, 3, 31),
    (2023, 4): date(2023, 4, 28), (2023, 5): date(2023, 5, 26), (2023, 6): date(2023, 6, 30),
    (2023, 7): date(2023, 7, 28), (2023, 9): date(2023, 9, 29), (2023, 10): date(2023, 10, 27),
}


def pce_release(rel_y, rel_m):
    return last_friday(rel_y, rel_m), "RULE_APPROX", "last Friday of the release month"


# --------------------------------- FOMC -------------------------------------
# 8 scheduled meetings/yr; the DECISION lands on the second day at 14:00 ET.
# 2022-2025 are RECALL (published years in advance, heavily referenced).
# 2026 is UNVERIFIED (forward extrapolation of the published pattern).
FOMC_RECALL = {
    2022: ["01-26", "03-16", "05-04", "06-15", "07-27", "09-21", "11-02", "12-14"],
    2023: ["02-01", "03-22", "05-03", "06-14", "07-26", "09-20", "11-01", "12-13"],
    2024: ["01-31", "03-20", "05-01", "06-12", "07-31", "09-18", "11-07", "12-18"],
    2025: ["01-29", "03-19", "05-07", "06-18", "07-30", "09-17", "10-29", "12-10"],
}
FOMC_2026_EXTRAP = ["01-28", "03-18", "04-29", "06-17", "07-29", "09-16", "10-28", "12-09"]


def build_calendar():
    rows = []
    # FOMC
    for y, days in FOMC_RECALL.items():
        for md in days:
            rows.append(dict(date=date(y, int(md[:2]), int(md[3:])), series="FOMC",
                             tier="RECALL", ref_period=f"{y}-{md[:2]}",
                             basis="published FOMC calendar (8 scheduled meetings/yr, "
                                   "decision on day 2 at 14:00 ET); model recall, unverified"))
    for md in FOMC_2026_EXTRAP:
        rows.append(dict(date=date(2026, int(md[:2]), int(md[3:])), series="FOMC",
                         tier="UNVERIFIED", ref_period=f"2026-{md[:2]}",
                         basis="2026 FOMC calendar EXTRAPOLATED from the published pattern; "
                               "not established"))
    # NFP / CPI / PCE -- reference months Dec 2021 .. Apr 2026
    for y in range(2021, 2027):
        for m in range(1, 13):
            if (y, m) < (2021, 12) or (y, m) > (2026, 5):
                continue
            # NFP: reference month (y,m) releases in the following month
            d, tier, note = nfp_release(y, m)
            if shutdown_hit(d) and tier != "RECALL":
                tier, note = "UNVERIFIED", note + " | 2025-26 shutdown disruption window"
            rows.append(dict(date=d, series="NFP", tier=tier, ref_period=f"{y}-{m:02d}",
                             basis=note))
            # CPI/PCE keyed by RELEASE month
            d, tier, note = cpi_release(y, m)
            if shutdown_hit(d):
                tier, note = "UNVERIFIED", note + " | 2025-26 shutdown disruption window"
            rows.append(dict(date=d, series="CPI", tier=tier, ref_period=f"rel {y}-{m:02d}",
                             basis=note))
            d, tier, note = pce_release(y, m)
            if shutdown_hit(d):
                tier, note = "UNVERIFIED", note + " | 2025-26 shutdown disruption window"
            rows.append(dict(date=d, series="PCE", tier=tier, ref_period=f"rel {y}-{m:02d}",
                             basis=note))
    cal = pd.DataFrame(rows)
    cal["date"] = pd.to_datetime(cal["date"])
    cal = cal[(cal["date"] >= DEV_START) & (cal["date"] <= DEV_END)]
    cal = cal.sort_values(["date", "series"]).reset_index(drop=True)
    return cal


def measure_rule_accuracy():
    res = {}
    hit = tot = w1 = 0
    for (y, m), truth in CPI_CHECKPOINTS.items():
        d, _, _ = cpi_release(y, m)
        tot += 1
        hit += int(d == truth)
        w1 += int(abs((d - truth).days) <= 3)
    res["CPI_rule_exact"] = f"{hit}/{tot}"
    res["CPI_rule_within_3cal_days"] = f"{w1}/{tot}"
    hit = tot = w1 = 0
    for (y, m), truth in PCE_CHECKPOINTS.items():
        d, _, _ = pce_release(y, m)
        tot += 1
        hit += int(d == truth)
        w1 += int(abs((d - truth).days) <= 3)
    res["PCE_rule_exact"] = f"{hit}/{tot}"
    res["PCE_rule_within_3cal_days"] = f"{w1}/{tot}"
    # NFP rule vs a handful of RECALL checkpoints
    nfp_ck = {(2021, 12): date(2022, 1, 7), (2022, 1): date(2022, 2, 4),
              (2022, 2): date(2022, 3, 4), (2022, 3): date(2022, 4, 1),
              (2022, 9): date(2022, 10, 7), (2023, 4): date(2023, 5, 5),
              (2023, 12): date(2024, 1, 5), (2024, 11): date(2024, 12, 6),
              (2024, 12): date(2025, 1, 10), (2025, 6): date(2025, 7, 3),
              (2022, 12): date(2023, 1, 6), (2024, 1): date(2024, 2, 2)}
    hit = tot = 0
    for (y, m), truth in nfp_ck.items():
        d, _, _ = nfp_release(y, m)
        tot += 1
        hit += int(d == truth)
    res["NFP_rule_exact"] = f"{hit}/{tot}"
    return res


# ===========================================================================
# SECTION B -- P&L SERIES FOR THE THREE OBJECTS
# ===========================================================================
def session_map():
    """bar timestamp -> session date, from the campaign's own 3-min NQ bar file
    (identical construction to runs/PRODUCTB_ONECONTRACT_FINAL/build_parity_and_metrics.py)."""
    from sm01_solarsim import load_bars_3m
    bars = load_bars_3m()
    sd = pd.to_datetime(bars["sess_date"])
    bars = bars[sd <= pd.Timestamp("2026-05-31")]
    return dict(zip(bars["time"], bars["sess_date"])), sorted(pd.to_datetime(bars["sess_date"].unique()))


def product_b_daily(path, bar2sess, sess_index):
    """Session-bucket the committed NT8 trade list, mirroring
    runs/PRODUCTB_ONECONTRACT_FINAL/build_parity_and_metrics.py exactly: map the RAW
    (unshifted) exit_time through the project's own bar->sess_date map; on the one
    documented unmapped exit fall back to the exit timestamp's calendar date."""
    t = pd.read_csv(path, parse_dates=["entry_time", "exit_time"])
    s = t["exit_time"].map(bar2sess)
    n_unmapped = int(s.isna().sum())
    sess = pd.to_datetime(pd.Series(np.where(s.isna(),
                                             t["exit_time"].dt.normalize().astype("datetime64[ns]"),
                                             pd.to_datetime(s.astype(str), errors="coerce"))))
    t = t.assign(sess=sess.values)
    bad = ~t["sess"].isin(sess_index)
    assert bad.sum() == 0, f"{bad.sum()} trades land on a non-session date"
    return t.groupby("sess")["pnl"].sum(), n_unmapped


# --- 2023-04-05/06 boundary pair: HOUSE CONVENTION, NOT A NEW REPAIR ---------------
# runs/SMV2M_MASTER_BUILD/out/parity_daily_aligned.csv column 'nt' (the NT8-executable
# daily curve for Product A) mis-buckets the fills of the 2023-04-05 / 2023-04-06 pair:
#   nt : 2023-04-05 = +129,340.30 , 2023-04-06 = -126,974.10  (pair sum +2,366.20)
#   tw : 2023-04-05 =     +600.70 , 2023-04-06 =   +1,358.20  (pair sum +1,958.90)
# These are the ONLY two dev-window sessions where |nt - tw| exceeds $1,562 (next largest
# gap $1,561.50; only 4 sessions exceed $1,000). Cause: the holiday-template session
# boundary parity.py already flags -- 2023-04-07 was Good Friday, a 09:15 ET early close.
# Engine totals are unaffected; it is a reconciliation-bucketing artifact, not P&L.
#
# runs/SMV2Q_DIAGNOSTICS/smv2q.py line 49 already established the house convention:
# "merge the 2023-04-05/06 data-gap boundary pair". This script follows that precedent
# (merged value booked to 2023-04-05, 2023-04-06 set to 0.0 so the 1,139-session calendar
# is preserved). VERIFIED: this reproduces runs/SMV2M_MASTER_BUILD/out/nt8_dev_battery.csv
# EXACTLY (net 177,315.09999995603 / daily_vol 2,109.4522724752574 / sharpe
# 1.1715277061807747 / maxDD_eod 18,894.300000003248 / CDaR5 14,905.358928573), i.e. the
# committed Product A battery was itself computed on the merged series.
# The RAW (unmerged) series is carried through the whole analysis as a second object so
# the effect of the artifact is visible rather than assumed away. On the raw series
# maxDD_eod = $129,916.90 and Sharpe = 0.428 -- any bootstrap capital map built on the
# raw column is badly contaminated.
A_PAIR = (pd.Timestamp("2023-04-05"), pd.Timestamp("2023-04-06"))


def product_a_daily(merge_pair=False):
    """Product A = SolarWaveSMMaster_v2, NT8 EXECUTABLE curve, already reconciled in
    runs/SMV2M_MASTER_BUILD/out/parity_daily_aligned.csv (column 'nt')."""
    d = pd.read_csv("runs/SMV2M_MASTER_BUILD/out/parity_daily_aligned.csv",
                    index_col=0, parse_dates=True)
    s = d["nt"].copy()
    if merge_pair and A_PAIR[0] in s.index and A_PAIR[1] in s.index:
        s.loc[A_PAIR[0]] = s.loc[A_PAIR[0]] + s.loc[A_PAIR[1]]
        s.loc[A_PAIR[1]] = 0.0
    return s


# ===========================================================================
# SECTION C -- ATTRIBUTION
# ===========================================================================
def attribute(daily, ev_sessions, label, rng):
    """daily: Series indexed by session date (dev window, all sessions).
    ev_sessions: set of session dates flagged as scheduled-event sessions."""
    s = daily.copy()
    n = len(s)
    is_ev = s.index.isin(ev_sessions)
    k = int(is_ev.sum())
    tot = float(s.sum())
    ev_net = float(s[is_ev].sum())
    non_net = tot - ev_net

    neg = s[s < 0]
    ev_loss = float(neg[neg.index.isin(ev_sessions)].sum())
    tot_loss = float(neg.sum())

    out = {
        "object": label, "n_sessions": n, "n_event_sessions": k,
        "event_session_share": k / n,
        "net_total": tot, "net_event": ev_net, "net_nonevent": non_net,
        "pnl_share_event": ev_net / tot if tot else np.nan,
        "mean_pnl_event": float(s[is_ev].mean()), "mean_pnl_nonevent": float(s[~is_ev].mean()),
        "loss_dollars_total": tot_loss, "loss_dollars_event": ev_loss,
        "loss_share_event": ev_loss / tot_loss if tot_loss else np.nan,
    }

    # ---- worst-day definitions ----
    order = s.sort_values()
    for tag, m in [("worst10", 10), ("worst25", 25),
                   ("bottom1pct", int(np.ceil(0.01 * n))), ("bottom5pct", int(np.ceil(0.05 * n)))]:
        sel = order.iloc[:m]
        hits = int(sel.index.isin(ev_sessions).sum())
        exp = m * k / n
        # hypergeometric: P(X >= hits) drawing m sessions from n, k of which are event
        p = float(hypergeom.sf(hits - 1, n, k, m)) if hits > 0 else 1.0
        out[f"{tag}_m"] = m
        out[f"{tag}_event_hits"] = hits
        out[f"{tag}_expected"] = exp
        out[f"{tag}_lift"] = hits / exp if exp else np.nan
        out[f"{tag}_p_onesided"] = p
        out[f"{tag}_dollars"] = float(sel.sum())
        out[f"{tag}_dollars_event"] = float(sel[sel.index.isin(ev_sessions)].sum())

    # ---- placebo: random session sets of the same size ----
    x = s.to_numpy()
    idx = np.arange(n)
    nb = 10000
    draws = np.array([rng.choice(idx, size=k, replace=False) for _ in range(nb)])
    plc_net = x[draws].sum(axis=1)
    out["placebo_pnl_share_p_low"] = float((plc_net <= ev_net).mean())
    out["placebo_pnl_share_p_high"] = float((plc_net >= ev_net).mean())
    out["placebo_net_event_q05"] = float(np.quantile(plc_net, 0.05))
    out["placebo_net_event_q95"] = float(np.quantile(plc_net, 0.95))
    return out


def per_year(daily, ev_sessions, label):
    rows = []
    for y, g in daily.groupby(daily.index.year):
        is_ev = g.index.isin(ev_sessions)
        k = int(is_ev.sum())
        neg = g[g < 0]
        negev = neg[neg.index.isin(ev_sessions)]
        m = 10
        order = g.sort_values().iloc[:m]
        tot = float(g.sum())
        # a P&L SHARE is meaningless when the denominator is near zero -- flag, don't hide
        share_ok = abs(tot) > 0.05 * float(np.abs(g).sum())
        rows.append(dict(object=label, year=int(y), n_sessions=len(g), n_event=k,
                         event_share=k / len(g),
                         net_total=tot, net_event=float(g[is_ev].sum()),
                         pnl_share_event=(float(g[is_ev].sum() / tot) if tot else np.nan),
                         pnl_share_meaningful=bool(share_ok),
                         loss_total=float(neg.sum()), loss_event=float(negev.sum()),
                         loss_share_event=float(negev.sum() / neg.sum()) if neg.sum() else np.nan,
                         worst10_event_hits=int(order.index.isin(ev_sessions).sum()),
                         worst10_expected=m * k / len(g),
                         worst_day=float(g.min()),
                         worst_day_is_event=bool(g.idxmin() in ev_sessions),
                         partial_year=bool(len(g) < 200)))
    return pd.DataFrame(rows)


def per_series(daily, cal, sess_index, label):
    """Split the CORE effect by release series so a single series cannot hide behind the
    pooled number (FOMC and NFP have different provenance AND different mechanics)."""
    rows = []
    for series, sub in cal.groupby("series"):
        d = pd.DatetimeIndex(sorted(set(sub["date"])))
        evs = set(d[d.isin(sess_index)])
        if not evs:
            continue
        g = daily
        is_ev = g.index.isin(evs)
        neg = g[g < 0]
        negev = neg[neg.index.isin(evs)]
        rows.append(dict(object=label, series=series, tier=",".join(sorted(sub["tier"].unique())),
                         n_event_sessions=int(is_ev.sum()),
                         net_event=float(g[is_ev].sum()),
                         mean_pnl_event=float(g[is_ev].mean()),
                         mean_pnl_nonevent=float(g[~is_ev].mean()),
                         loss_share_event=float(negev.sum() / neg.sum()) if neg.sum() else np.nan,
                         pos_day_frac_event=float((g[is_ev] > 0).mean()),
                         pos_day_frac_nonevent=float((g[~is_ev] > 0).mean())))
    return pd.DataFrame(rows)


# ===========================================================================
# SECTION D -- LEVERAGE / MARGIN
# ===========================================================================
MARGIN = {
    "NQ":  dict(day=1000.0, day_4x=4000.0, initial=43433.67, pv=20.0),
    "MNQ": dict(day=100.0,  day_4x=400.0,  initial=4343.38,  pv=2.0),
}


def capital_map(daily, stress_mults=(1.0, 1.25, 1.5, 2.0),
                thrs=(0.10, 0.15, 0.20, 0.25, 0.30), nb=2000, seed=20260808):
    """VERBATIM convention of runs/PRODUCTB_ONECONTRACT_FINAL/build_parity_and_metrics.py
    (same function body, same seed, same methods/grids) so that a map computed here for
    Product A is directly comparable to the two committed Product B maps."""
    x = daily.to_numpy(dtype=float)
    n_ = len(x)
    rng = np.random.default_rng(seed)

    def idx_moving_block(L):
        nb_ = int(np.ceil(n_ / L))
        starts = rng.integers(0, n_, size=(nb, nb_))
        idx = (starts[:, :, None] + np.arange(L)[None, None, :]) % n_
        return idx.reshape(nb, -1)[:, :n_]

    def idx_stationary(mean_L):
        p = 1.0 / mean_L
        idx = np.empty((nb, n_), dtype=np.int64)
        cur_i = rng.integers(0, n_, size=nb)
        for t in range(n_):
            jump = rng.random(nb) < p
            cur_i = np.where(jump, rng.integers(0, n_, size=nb), (cur_i + 1) % n_)
            idx[:, t] = cur_i
        return idx

    methods = {"L5": idx_moving_block(5), "L20": idx_moving_block(20),
               "stat60": idx_stationary(60)}
    rows = []
    for m in stress_mults:
        xs = x * m
        for mname, idx in methods.items():
            paths = xs[idx]
            eq = np.cumsum(paths, axis=1)
            peak = np.maximum.accumulate(eq, axis=1)
            dd = peak - eq
            p95 = np.percentile(dd.max(axis=1), 95)
            for thr in thrs:
                rows.append({"stress_mult": m, "method": mname, "thr": thr,
                             "p95_maxdd_dollar": float(p95),
                             "capital_needed": float(p95 / thr)})
    return pd.DataFrame(rows)


def leverage_table(cmap, inst, contracts_per_unit, label):
    """For every row of the capital map, compare DD-based sizing against margin caps.

    Convention taken from the committed maps: `capital_needed` is the capital that
    supports ONE UNIT of the product (Product B: 1 contract; Product A: one copy of the
    master, whose peak physical size is `contracts_per_unit` contracts). At capital C,
    DD-based unit count = floor(C / capital_needed).
    Margin caps at capital C: floor(C / (contracts_per_unit * margin_per_contract)).
    """
    mg = MARGIN[inst]
    rows = []
    for _, r in cmap.iterrows():
        cn = r["capital_needed"]
        per_unit_1x = contracts_per_unit * mg["day"]
        per_unit_4x = contracts_per_unit * mg["day_4x"]
        per_unit_init = contracts_per_unit * mg["initial"]
        rows.append(dict(
            object=label, instrument=inst, stress_mult=r["stress_mult"],
            method=r["method"], thr=r["thr"],
            capital_per_unit_dd=cn,
            margin_per_unit_1x=per_unit_1x,
            margin_per_unit_4x=per_unit_4x,
            margin_per_unit_initial=per_unit_init,
            ratio_dd_over_margin_4x=cn / per_unit_4x,
            ratio_dd_over_margin_initial=cn / per_unit_init,
            # multiplier on DAY margin that would be needed for margin to bind
            breakeven_margin_multiplier=cn / per_unit_1x,
            # the DD tolerance thr at which the two would coincide
            breakeven_thr_for_4x=r["p95_maxdd_dollar"] / per_unit_4x,
            binds_first="drawdown" if cn > per_unit_4x else "margin_4x",
        ))
    return pd.DataFrame(rows)


def capital_grid_table(cmap, inst, contracts_per_unit, label, caps):
    mg = MARGIN[inst]
    rows = []
    for C in caps:
        nd = np.floor(C / cmap["capital_needed"].to_numpy())
        rows.append(dict(
            object=label, instrument=inst, capital=C,
            units_dd_min=int(nd.min()), units_dd_median=float(np.median(nd)),
            units_dd_max=int(nd.max()),
            units_margin_1x=int(np.floor(C / (contracts_per_unit * mg["day"]))),
            units_margin_4x=int(np.floor(C / (contracts_per_unit * mg["day_4x"]))),
            units_margin_initial=int(np.floor(C / (contracts_per_unit * mg["initial"]))),
            binding_at_max_dd_sizing=("drawdown" if nd.max() <=
                                      np.floor(C / (contracts_per_unit * mg["day_4x"]))
                                      else "margin_4x"),
            margin_utilisation_4x_at_median_dd_sizing=(
                float(np.median(nd)) * contracts_per_unit * mg["day_4x"] / C),
        ))
    return pd.DataFrame(rows)


# ===========================================================================
# MAIN
# ===========================================================================
def main():
    rng = np.random.default_rng(SEED)
    report = {}

    # ---------- A. calendar ----------
    cal = build_calendar()
    cal_out = cal.copy()
    cal_out["date"] = cal_out["date"].dt.strftime("%Y-%m-%d")
    cal_out.to_csv(f"{SRC}/v1f_event_calendar.csv", index=False)
    acc = measure_rule_accuracy()
    print("rule accuracy vs recall checkpoints:", acc)
    print("\ncalendar tier x series counts:")
    print(pd.crosstab(cal["series"], cal["tier"]).to_string())
    report["rule_accuracy"] = acc
    report["tier_counts"] = pd.crosstab(cal["series"], cal["tier"]).to_dict()

    bar2sess, sessions = session_map()
    sess_index = pd.DatetimeIndex(sessions)
    print(f"\ndev sessions: {len(sess_index)}  {sess_index.min().date()} .. {sess_index.max().date()}")

    def to_sessions(sub):
        """Map release calendar dates to trading sessions. A release at 08:30 or 14:00 ET
        on date D falls inside the CME session whose sess_date (= date of the 17:00 ET
        close) is D. Dates that are not trading sessions are dropped and counted."""
        d = pd.DatetimeIndex(sorted(set(sub["date"])))
        keep = d.isin(sess_index)
        return set(d[keep]), int((~keep).sum())

    CORE = cal[cal["tier"].isin(["RULE", "RECALL"])]
    APPROX = cal[cal["tier"].isin(["RULE", "RECALL", "RULE_APPROX"])]
    ALL = cal
    core_ev, core_drop = to_sessions(CORE)
    approx_ev, approx_drop = to_sessions(APPROX)
    all_ev, all_drop = to_sessions(ALL)
    fomc_ev, _ = to_sessions(cal[cal["series"] == "FOMC"])
    nfp_ev, _ = to_sessions(cal[cal["series"] == "NFP"])
    print(f"CORE  (RULE+RECALL = FOMC + NFP): {len(core_ev)} sessions (non-session dates dropped: {core_drop})")
    print(f"+APPROX (adds CPI+PCE rule dates): {len(approx_ev)} (dropped: {approx_drop})")
    print(f"ALL   (adds UNVERIFIED):          {len(all_ev)} (dropped: {all_drop})")

    # dilated: +/- 1 business day around CORE
    dil = set()
    for d in core_ev:
        dil.add(d)
        for k in (-1, 1):
            dd = d + pd.Timedelta(days=k)
            while dd not in sess_index and abs((dd - d).days) < 6:
                dd += pd.Timedelta(days=k)
            if dd in sess_index:
                dil.add(dd)
    print(f"DILATED (CORE +/- 1 trading session): {len(dil)}")

    report["calendar_sizes"] = {"CORE": len(core_ev), "PLUS_APPROX": len(approx_ev),
                                "ALL": len(all_ev), "FOMC": len(fomc_ev), "NFP": len(nfp_ev),
                                "DILATED": len(dil), "n_sessions": len(sess_index),
                                "n_unverified_rows": int((cal["tier"] == "UNVERIFIED").sum()),
                                "n_rule_approx_rows": int((cal["tier"] == "RULE_APPROX").sum()),
                                "n_rule_rows": int((cal["tier"] == "RULE").sum()),
                                "n_recall_rows": int((cal["tier"] == "RECALL").sum())}

    # ---------- B. P&L series ----------
    objs = {}
    a_raw = product_a_daily(merge_pair=False)
    a_rep = product_a_daily(merge_pair=True)
    objs["PRODUCT_A_SMMasterV2_MNQ"] = a_rep[(a_rep.index >= DEV_START) & (a_rep.index <= DEV_END)]
    objs["PRODUCT_A_rawNTbucketing"] = a_raw[(a_raw.index >= DEV_START) & (a_raw.index <= DEV_END)]
    # integrity check against the committed battery (house-convention series)
    from smv2_common import dd_battery
    _b = dd_battery(objs["PRODUCT_A_SMMasterV2_MNQ"].index,
                    objs["PRODUCT_A_SMMasterV2_MNQ"].values, label="chk")
    _c = pd.read_csv("runs/SMV2M_MASTER_BUILD/out/nt8_dev_battery.csv").iloc[0]
    for _k in ("n_days", "net", "daily_vol", "sharpe", "maxDD_eod"):
        assert abs(float(_b[_k]) - float(_c[_k])) < 1e-6, (_k, _b[_k], _c[_k])
    print("integrity: Product A merged series reproduces committed nt8_dev_battery.csv "
          "(n_days/net/daily_vol/sharpe/maxDD_eod) exactly")
    n_unmapped = {}
    for tag, path in [("PRODUCT_B_BEST_ONE_NQ", "runs/PRODUCTB_ONECONTRACT_FINAL/out/nt_trades_nq.csv"),
                      ("PRODUCT_B_BEST_ONE_MNQ", "runs/PRODUCTB_ONECONTRACT_FINAL/out/nt_trades_mnq.csv")]:
        s, nu = product_b_daily(path, bar2sess, sess_index)
        n_unmapped[tag] = nu
        s = s.reindex(sess_index).fillna(0.0)
        objs[tag] = s[(s.index >= DEV_START) & (s.index <= DEV_END)]
    for k, v in objs.items():
        print(f"{k:28s} n={len(v):5d}  net={v.sum():14,.2f}")
    print("committed reference nets: A(NT8 exec) 177,315.10 | B-NQ 303,449.00 | B-MNQ 28,900.70")
    print("trades needing the calendar-date fallback:", n_unmapped)
    report["net_check"] = {k: float(v.sum()) for k, v in objs.items()}
    report["nt_trades_unmapped_fallback"] = n_unmapped

    # ---------- C. attribution ----------
    rows = []
    for label, s in objs.items():
        for calname, evs in [("CORE_FOMC_NFP", core_ev), ("FOMC_only", fomc_ev),
                             ("NFP_only", nfp_ev), ("PLUS_APPROX_cpi_pce", approx_ev),
                             ("ALL_incl_unverified", all_ev), ("DILATED_core_pm1", dil)]:
            r = attribute(s, evs, label, rng)
            r["calendar"] = calname
            rows.append(r)
    att = pd.DataFrame(rows)
    cols = ["object", "calendar"] + [c for c in att.columns if c not in ("object", "calendar")]
    att = att[cols]
    att.to_csv(f"{OUT}/v1f_event_attribution.csv", index=False)

    py = pd.concat([per_year(s, core_ev, label) for label, s in objs.items()])
    py.to_csv(f"{OUT}/v1f_event_attribution_by_year.csv", index=False)
    ps = pd.concat([per_series(s, cal, sess_index, label) for label, s in objs.items()])
    ps.to_csv(f"{OUT}/v1f_event_attribution_by_series.csv", index=False)

    keep_cols = ["object", "calendar", "n_event_sessions", "event_session_share", "net_total",
                 "net_event", "pnl_share_event", "loss_share_event", "mean_pnl_event",
                 "mean_pnl_nonevent", "worst10_event_hits", "worst10_expected",
                 "worst10_p_onesided", "worst25_event_hits", "worst25_expected",
                 "worst25_p_onesided", "bottom1pct_event_hits", "bottom1pct_expected",
                 "bottom1pct_p_onesided", "bottom5pct_event_hits", "bottom5pct_expected",
                 "bottom5pct_p_onesided", "placebo_pnl_share_p_low"]
    for cn in ["CORE_FOMC_NFP", "PLUS_APPROX_cpi_pce", "ALL_incl_unverified", "DILATED_core_pm1",
               "FOMC_only", "NFP_only"]:
        print(f"\n--- attribution ({cn}) ---")
        print(att[att["calendar"] == cn][keep_cols].to_string(index=False))
    print("\n--- per year (CORE) ---")
    print(py.to_string(index=False))
    print("\n--- per series (all tiers) ---")
    print(ps.to_string(index=False))

    # ---------- D. leverage ----------
    cmap_nq = pd.read_csv("runs/PRODUCTB_ONECONTRACT_FINAL/out/capital_map_nq.csv")
    cmap_mnq = pd.read_csv("runs/PRODUCTB_ONECONTRACT_FINAL/out/capital_map_mnq.csv")
    cmap_a = capital_map(objs["PRODUCT_A_SMMasterV2_MNQ"])
    cmap_a.to_csv(f"{OUT}/v1f_capital_map_productA.csv", index=False)

    bars = pd.read_csv("runs/SMV2M_MASTER_BUILD/out/nt8/smm_v2_bars.csv", comment="#")
    bars["time"] = pd.to_datetime(bars["time"])
    a_peak = int(bars["phys"].abs().max())
    bars["sess"] = pd.to_datetime(bars["time"].map(bar2sess).astype(str), errors="coerce")
    ev_bars = bars[bars["sess"].isin(core_ev)]
    a_peak_ev = int(ev_bars["phys"].abs().max())
    print(f"\nProduct A peak physical size: {a_peak} MNQ (all dev sessions), "
          f"{a_peak_ev} MNQ on CORE event sessions")
    report["product_a_peak_contracts"] = {"all": a_peak, "event_sessions": a_peak_ev}

    # --- early-close (initial-margin-breach) sessions that are ALSO event sessions ----
    from sm01_solarsim import load_bars_3m
    ab = load_bars_3m()
    ab = ab[pd.to_datetime(ab["sess_date"]) <= pd.Timestamp("2026-05-31")]
    lastbar = ab[ab["is_last_of_sess"]].copy()
    lastbar["hm"] = lastbar["time"].dt.hour * 100 + lastbar["time"].dt.minute
    early = pd.to_datetime(lastbar.loc[lastbar["hm"] < 1700, "sess_date"].astype(str))
    early_set = set(early)
    overlap = sorted(early_set & core_ev)
    print(f"early-close sessions in dev window: {len(early_set)}; "
          f"also CORE event sessions: {len(overlap)} -> {[str(d.date()) for d in overlap]}")
    report["early_close_x_event"] = {"n_early_close": len(early_set),
                                     "n_overlap_core": len(overlap),
                                     "overlap": [str(d.date()) for d in overlap]}

    # --- notional leverage implied by DD sizing vs permitted by 4X day margin ---------
    px = float(ab.loc[ab["is_last_of_sess"], "close"].median())
    report["nq_median_session_close_dev"] = px
    notional = {"NQ": px * 20.0, "MNQ": px * 2.0}
    print(f"median dev session close = {px:.1f} -> notional/contract NQ ${notional['NQ']:,.0f}, "
          f"MNQ ${notional['MNQ']:,.0f}")

    lev = pd.concat([
        leverage_table(cmap_nq, "NQ", 1, "PRODUCT_B_BEST_ONE_NQ"),
        leverage_table(cmap_mnq, "MNQ", 1, "PRODUCT_B_BEST_ONE_MNQ"),
        leverage_table(cmap_a, "MNQ", a_peak, "PRODUCT_A_SMMasterV2_MNQ"),
    ])
    lev["notional_per_unit"] = lev.apply(
        lambda r: notional[r["instrument"]] * (a_peak if r["object"].startswith("PRODUCT_A") else 1),
        axis=1)
    lev["notional_leverage_at_dd_sizing"] = lev["notional_per_unit"] / lev["capital_per_unit_dd"]
    lev["notional_leverage_permitted_by_4x_margin"] = lev["notional_per_unit"] / lev["margin_per_unit_4x"]
    lev.to_csv(f"{OUT}/v1f_leverage_binding.csv", index=False)

    grid = pd.concat([
        capital_grid_table(cmap_nq, "NQ", 1, "PRODUCT_B_BEST_ONE_NQ",
                           [100_000, 250_000, 500_000, 1_000_000, 2_500_000, 5_000_000, 10_000_000]),
        capital_grid_table(cmap_mnq, "MNQ", 1, "PRODUCT_B_BEST_ONE_MNQ",
                           [25_000, 50_000, 100_000, 250_000, 500_000, 1_000_000, 2_500_000]),
        capital_grid_table(cmap_a, "MNQ", a_peak, "PRODUCT_A_SMMasterV2_MNQ",
                           [50_000, 100_000, 250_000, 500_000, 1_000_000, 2_500_000, 5_000_000]),
    ])
    grid.to_csv(f"{OUT}/v1f_capital_grid.csv", index=False)

    print("\n--- leverage: DD-based capital per unit vs margin per unit ---")
    summ = lev.groupby(["object", "instrument"]).agg(
        capital_per_unit_dd_min=("capital_per_unit_dd", "min"),
        capital_per_unit_dd_max=("capital_per_unit_dd", "max"),
        margin_per_unit_1x=("margin_per_unit_1x", "first"),
        margin_per_unit_4x=("margin_per_unit_4x", "first"),
        margin_per_unit_initial=("margin_per_unit_initial", "first"),
        ratio_dd_over_4x_min=("ratio_dd_over_margin_4x", "min"),
        ratio_dd_over_4x_max=("ratio_dd_over_margin_4x", "max"),
        ratio_dd_over_initial_min=("ratio_dd_over_margin_initial", "min"),
        breakeven_mult_min=("breakeven_margin_multiplier", "min"),
        breakeven_thr_for_4x_min=("breakeven_thr_for_4x", "min"),
        notional_lev_at_dd_sizing_max=("notional_leverage_at_dd_sizing", "max"),
        notional_lev_permitted_4x=("notional_leverage_permitted_by_4x_margin", "first"),
        n_rows_margin_binds=("binds_first", lambda x: int((x == "margin_4x").sum())),
        n_rows=("binds_first", "size"),
    ).reset_index()
    print(summ.to_string(index=False))
    summ.to_csv(f"{OUT}/v1f_leverage_summary.csv", index=False)
    print("\n--- capital grid ---")
    print(grid.to_string(index=False))

    report["leverage_summary"] = json.loads(summ.to_json(orient="records"))
    with open(f"{OUT}/v1f_summary.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
    print("\nWROTE:")
    for p in [f"{SRC}/v1f_event_calendar.csv", f"{OUT}/v1f_event_attribution.csv",
              f"{OUT}/v1f_event_attribution_by_year.csv",
              f"{OUT}/v1f_event_attribution_by_series.csv",
              f"{OUT}/v1f_capital_map_productA.csv",
              f"{OUT}/v1f_leverage_binding.csv", f"{OUT}/v1f_capital_grid.csv",
              f"{OUT}/v1f_leverage_summary.csv", f"{OUT}/v1f_summary.json"]:
        print(" ", p)


if __name__ == "__main__":
    main()
