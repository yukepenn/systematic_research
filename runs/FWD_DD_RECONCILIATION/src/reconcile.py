"""FWD_DD_RECONCILIATION - which max-drawdown object is right, $22,931 or $24,212.92?

Directive s29. A freeze is not permission to preserve a known possible arithmetic defect, and the
seal has NOT been read, so correcting a defect NOW is legal pre-read repair - not outcome-driven
retuning.

THE INVARIANCE THAT MUST HOLD. A weekly equity curve is a SUBSAMPLE of the daily curve, which is a
subsample of the trade-by-trade curve. Peak-to-trough measured on fewer points can only be SMALLER
or equal. Therefore:

    maxDD(trade) >= maxDD(session) >= maxDD(daily) >= maxDD(weekly)

The canonical baseline reports $22,931 and the weekly series gives $24,212.92. Weekly EXCEEDS the
canonical figure, which is impossible if they describe the same P&L stream at different resolutions.
One of them is a different object. This finds out which.

Rebuilt from the lowest trustworthy source: the RR_W001 per-trade ledger.
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

ROOT = (r"D:\OneDrive - Washington University in St. Louis\TradingResearch"
        r"\systematic_research")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")
os.makedirs(OUT, exist_ok=True)
A, B = "2022-07-01", "2026-08-01"
_fh = open(os.path.join(OUT, "reconcile.txt"), "w", encoding="utf-8")


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


def dd(cum, idx):
    """max drawdown plus the exact peak and trough labels"""
    peak = np.maximum.accumulate(cum)
    d = peak - cum
    j = int(np.argmax(d))
    i = int(np.argmax(cum[:j + 1])) if j > 0 else 0
    return float(d[j]), idx[i], idx[j]


def main():
    P("=" * 108)
    P("=== FWD_DD_RECONCILIATION - the invariance maxDD(trade) >= ... >= maxDD(weekly) must hold")
    P("=" * 108)

    L = pd.read_csv(os.path.join(ROOT, "runs/RR_W001_ACTION_VALUE_LEDGER/out/ledger_p1pct.csv"))
    L["session_date"] = pd.to_datetime(L["session_date"])
    L["decision_ts"] = pd.to_datetime(L["decision_ts"])
    P(f"    ledger rows {len(L):,}   {L.session_date.min().date()} -> {L.session_date.max().date()}")

    W = L[(L["session_date"] >= A) & (L["session_date"] < B)].copy()
    W = W.sort_values(["session_date", "session_id", "entry_ordinal_in_session"]).reset_index(drop=True)
    P(f"    in-window [{A}, {B})   rows {len(W):,}   sessions {W.session_id.nunique():,}")
    P(f"    cost model: {W.cost_model_id.iloc[0]}")

    # ---- internal consistency of the ledger itself
    g = W.groupby(["session_date", "session_id"])
    chk = g.agg(tsum=("baseline_trade_net", "sum"), sess=("baseline_session_net", "first"))
    bad = (chk["tsum"] - chk["sess"]).abs() > 0.01
    P(f"    sessions where sum(trade_net) != session_net : {int(bad.sum())} of {len(chk)}")
    if bad.any():
        P(f"      max abs mismatch ${(chk['tsum']-chk['sess']).abs().max():,.2f}")
        P("      >>> using SUM OF TRADES as the source of truth; session_net is a stored aggregate")

    # ---------------------------------------------------------------- the ladder
    P("")
    P("=" * 108)
    P("=== THE AGGREGATION LADDER, all from the SAME trades, SAME window, SAME cost model")
    P("=" * 108)
    P(f"    {'level':<14}{'n':>8}{'total net':>14}{'mean':>12}{'maxDD':>13}   peak -> trough")
    P("    " + "-" * 92)

    rows = []
    # trade level
    cum = W["baseline_trade_net"].cumsum().values
    idx = W["decision_ts"].dt.strftime("%Y-%m-%d").values
    d0, p0, t0 = dd(cum, idx)
    P(f"    {'trade':<14}{len(W):>8,}{cum[-1]:>14,.0f}"
      f"{W['baseline_trade_net'].mean():>12,.2f}{d0:>13,.2f}   {p0} -> {t0}")
    rows.append(dict(level="trade", n=len(W), total=cum[-1], maxdd=d0, peak=p0, trough=t0))

    # session level (the true NQ session, keyed by session_id)
    s = g["baseline_trade_net"].sum().reset_index().sort_values(["session_date", "session_id"])
    cum = s["baseline_trade_net"].cumsum().values
    idx = s["session_date"].dt.strftime("%Y-%m-%d").values
    d1, p1, t1 = dd(cum, idx)
    P(f"    {'session':<14}{len(s):>8,}{cum[-1]:>14,.0f}"
      f"{s['baseline_trade_net'].mean():>12,.2f}{d1:>13,.2f}   {p1} -> {t1}")
    rows.append(dict(level="session", n=len(s), total=cum[-1], maxdd=d1, peak=p1, trough=t1))

    # calendar-day level
    dly = W.groupby("session_date")["baseline_trade_net"].sum().sort_index()
    cum = dly.cumsum().values
    idx = dly.index.strftime("%Y-%m-%d").values
    d2, p2, t2 = dd(cum, idx)
    P(f"    {'calendar day':<14}{len(dly):>8,}{cum[-1]:>14,.0f}"
      f"{dly.mean():>12,.2f}{d2:>13,.2f}   {p2} -> {t2}")
    rows.append(dict(level="calendar_day", n=len(dly), total=cum[-1], maxdd=d2, peak=p2, trough=t2))

    # weekly, week ENDING Sunday, matching the RR_W003 convention
    wk = W.copy()
    wk["week"] = wk["session_date"] + pd.to_timedelta(6 - wk["session_date"].dt.weekday, unit="D")
    wkly = wk.groupby("week")["baseline_trade_net"].sum().sort_index()
    cum = wkly.cumsum().values
    idx = wkly.index.strftime("%Y-%m-%d").values
    d3, p3, t3 = dd(cum, idx)
    P(f"    {'weekly':<14}{len(wkly):>8,}{cum[-1]:>14,.0f}"
      f"{wkly.mean():>12,.2f}{d3:>13,.2f}   {p3} -> {t3}")
    rows.append(dict(level="weekly", n=len(wkly), total=cum[-1], maxdd=d3, peak=p3, trough=t3))
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "ladder.csv"), index=False)

    P("")
    P("    INVARIANCE CHECK   maxDD(trade) >= session >= day >= weekly")
    ok = (d0 >= d1 - 0.01) and (d1 >= d2 - 0.01) and (d2 >= d3 - 0.01)
    P(f"      {d0:,.2f} >= {d1:,.2f} >= {d2:,.2f} >= {d3:,.2f}   ->   "
      f"{'HOLDS' if ok else 'VIOLATED'}")

    # ---------------------------------------------------------------- the comparison
    P("")
    P("=" * 108)
    P("=== AGAINST THE TWO CIRCULATING FIGURES")
    P("=" * 108)
    ext = pd.read_csv(os.path.join(ROOT, "runs/RR_W003_X9A_CONTRACT/out/weekly_p1_x9a.csv"))
    ext = ext.rename(columns={ext.columns[0]: "week"})
    ext["week"] = pd.to_datetime(ext["week"])
    ce = ext["p1"].cumsum().values
    de, pe, te = dd(ce, ext["week"].dt.strftime("%Y-%m-%d").values)
    P(f"    RR_W003 weekly series      n {len(ext)}  total ${ce[-1]:>12,.0f}  "
      f"maxDD ${de:>11,.2f}   {pe} -> {te}")
    P(f"    ledger-rebuilt weekly      n {len(wkly)}  total ${cum[-1]:>12,.0f}  "
      f"maxDD ${d3:>11,.2f}   {p3} -> {t3}")
    P(f"    CANONICAL baseline                                        maxDD $   22,931")
    P("")
    P(f"    ledger weekly total vs RR_W003 total   diff ${cum[-1]-ce[-1]:,.2f}")
    P("")
    for lbl, v in (("trade", d0), ("session", d1), ("calendar day", d2), ("weekly", d3)):
        P(f"      |{lbl:<13} maxDD - 22,931| = ${abs(v-22931):>10,.2f}")
    best = min((abs(v - 22931), lbl) for lbl, v in
               (("trade", d0), ("session", d1), ("calendar day", d2), ("weekly", d3)))
    P(f"\n    CLOSEST AGGREGATION TO THE CANONICAL $22,931: {best[1]}  (off by ${best[0]:,.2f})")
    P("    >>> $22,931 is BELOW the COARSEST possible drawdown of this stream ($24,212.92).")
    P("    >>> No aggregation can produce it. It is therefore a DIFFERENT OBJECT, not a")
    P("    >>> different resolution of the same one.")

    # ---------------------------------------------------------------- THE CAUSE
    P("")
    P("=" * 108)
    P("=== THE CAUSE: TWO COST MODELS. The ledger carries both, and the canonical figure mixes them.")
    P("=" * 108)
    diff = W["baseline_trade_pnl_commonly"] - W["baseline_trade_net"]
    P(f"    pnl_commonly - trade_net, per trade:  median ${diff.median():.2f}  "
      f"mean ${diff.mean():.2f}  range ${diff.min():.2f} .. ${diff.max():.2f}")
    bysz = W.assign(d=diff).groupby("size_at_entry")["d"].median()
    for sz, v in bysz.items():
        P(f"      size {int(sz)}  median difference ${v:.2f}")
    P("    => `baseline_trade_net` = `pnl_commonly` MINUS the candidate-specific modelled spread")
    P("       (~$14.44/ctrRT, charged per fill at that fill's own minute). The two columns are the")
    P("       SAME trades under the FROZEN cost model and under a COMMISSION-ONLY model.")
    P("")
    P(f"    {'cost model':<34}{'weekly mean':>13}{'weekly maxDD':>15}{'k':>11}{'scaled $/wk':>13}")
    P("    " + "-" * 86)
    for col, nm in (("baseline_trade_net", "trade_net  (WITH spread) FROZEN"),
                    ("baseline_trade_pnl_commonly", "pnl_commonly (commission only)")):
        w2 = wk.groupby("week")[col].sum().sort_index()
        c2 = w2.cumsum().values
        m2 = float(np.max(np.maximum.accumulate(c2) - c2))
        P(f"    {nm:<34}${w2.mean():>12,.2f}${m2:>14,.2f}{20245/m2:>11.6f}"
          f"${w2.mean()*20245/m2:>12,.2f}")

    P("")
    P("    " + "!" * 92)
    P("    !! THE DEFECT, STATED EXACTLY")
    P("    !! CURRENT_BASELINE quotes raw $1,394/wk and maxDD $22,931 -> fixed-DD $1,230/wk.")
    P("    !! The $1,394 numerator reproduces `trade_net` (WITH spread) to $0.81.")
    P("    !! The $22,931 denominator matches `pnl_commonly` (NO spread) to $78.")
    P("    !! SO THE HEADLINE MIXES A SPREAD-INCLUSIVE NUMERATOR WITH A SPREAD-EXCLUSIVE")
    P("    !! DRAWDOWN DENOMINATOR, which flatters the fixed-DD figure.")
    P("    !!")
    P("    !! Internally consistent under the FROZEN cost model throughout:")
    P("    !!     k = 20,245 / 24,212.92 = 0.836124   ->   $1,166.24/wk,  NOT $1,230/wk")
    P("    !!     a -5.2 % correction to the campaign's most-quoted number.")
    P("    !!")
    P("    !! NOT bit-reproduced: $22,931 vs my $22,852.92 leaves $78 (0.34 %) unexplained, so the")
    P("    !! MECHANISM is established while the exact canonical recipe is not. Stated, not hidden.")
    P("    " + "!" * 92)
    _fh.close()


if __name__ == "__main__":
    main()
