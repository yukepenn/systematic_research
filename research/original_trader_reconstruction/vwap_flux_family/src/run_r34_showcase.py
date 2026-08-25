"""OTR_R34 (spec preregistered): the METHODOLOGY EQUALIZER.

Displays OUR OWN clean-room VF family the way HE displays his system — per-week best
configuration, gross of commission — and compares that sheet against (a) his actual sheet and
(b) our honestly-frozen configurations, on the identical 21 comparable SA weeks.

All machinery is imported unchanged from run_r32_joint / run_r30c: same 288-config grid, same
bars, same windows, same entry-time weekly attribution. The ONLY new code is weekly net
book-keeping and sheet construction. Nothing here is promoted; per spec, net P&L is the OBJECT
OF STUDY (the display statistic), not a mechanism selector.
"""
from __future__ import annotations

import csv
import os
import sys

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "research", "original_trader_reconstruction",
                                "solar_family", "src"))
from run_r7_signal_id import ema, trend_states                             # noqa: E402
from run_r30c_exitfamilies import layer_b_exit                             # noqa: E402
from run_r32_joint import layer_a_v2, mkbars, HOLDOUT_SRC, EXCLUDE_TP      # noqa: E402

OUT = os.path.join(ROOT, "runs", "OTR_R34_METHODOLOGY_EQUALIZER", "out")
os.makedirs(OUT, exist_ok=True)
DATA = os.path.join(ROOT, "research", "original_trader_reconstruction", "data")
COMMISSION_RT = 4.36
INCUMBENT = "D_MOM|G_WITH|P_MED|C_DIR|X_OPP"
LEADING = "D_MOM|G_WITH|P_IN|C_REC|X_TRAIL_PTS:80"


def week_net(trl, a, b):
    w = [x for x in trl if a <= np.datetime64(x["et"]) <= b]
    return float(sum(x["pnl"] for x in w)), len(w)


def main():
    tg_all = list(csv.DictReader(open(os.path.join(
        ROOT, "research", "original_trader_reconstruction", "screenshot_forensics",
        "derived", "targets_weekly_2026V.csv"), encoding="utf-8")))

    # ---------------- windows: identical construction to run_r32_joint ----------------------
    df = pd.read_parquet(os.path.join(ROOT, "research", "scalping_lab", "substrate",
                                      "minute", "NQ", "nq1m_2005_202605.parquet"))
    df["time"] = pd.to_datetime(df["time"])
    seg = df[(df["time"] >= "2026-01-11") & (df["time"] <= "2026-05-29 17:00")].reset_index(drop=True)
    fb_bars, fb_atr = mkbars(seg)
    fit_wins = []
    for r in tg_all:
        if pd.Timestamp(r["report_end"]) > pd.Timestamp("2026-05-29") or r["image_id"] in EXCLUDE_TP:
            continue
        a = np.datetime64(pd.Timestamp(r["report_start"]) - pd.Timedelta(days=1)) + np.timedelta64(18, "h")
        b = np.datetime64(pd.Timestamp(r["report_end"])) + np.timedelta64(17, "h")
        fit_wins.append((r, a, b))

    hold_sets = []
    for r in tg_all:
        src = HOLDOUT_SRC.get(r["report_start"])
        if src is None or r["image_id"] in EXCLUDE_TP:
            continue
        d = pd.read_csv(os.path.join(DATA, src)); d["time"] = pd.to_datetime(d["time"])
        a = pd.Timestamp(r["report_start"]) - pd.Timedelta(days=1) + pd.Timedelta(hours=18)
        b = pd.Timestamp(r["report_end"]) + pd.Timedelta(hours=17)
        sub = d[(d["time"] >= a - pd.Timedelta(days=3)) & (d["time"] <= b)].reset_index(drop=True)
        if len(sub) < 500:
            continue
        bb, aa = mkbars(sub)
        tr2 = trend_states("T_C", bb["c"], bb["l"], bb["h"], bb["lv"], ema(bb["c"], 20))
        hold_sets.append((r, bb, aa, tr2, np.datetime64(a), np.datetime64(b)))

    weeks = sorted([r["image_id"] for r, _, _ in fit_wins] +
                   [r["image_id"] for r, _, _, _, _, _ in hold_sets],
                   key=lambda i: pd.Timestamp(next(x for x in tg_all if x["image_id"] == i)["report_start"]))
    his = {r["image_id"]: float(r["net_all"]) for r in tg_all}
    print(f"comparable weeks: {len(weeks)} (fit {len(fit_wins)} + holdout {len(hold_sets)})")

    trend_fit = trend_states("T_C", fb_bars["c"], fb_bars["l"], fb_bars["h"], fb_bars["lv"],
                             ema(fb_bars["c"], 20))

    CFG = [(D, G, P, C, X, xp)
           for D in ("D_MOM", "D_FADE")
           for G in ("G_NONE", "G_WITH", "G_AGAINST")
           for P in ("P_IN", "P_Q75", "P_MED")
           for C in ("C_DIR", "C_REC")
           for X, xp in (("X_OPP", None), ("X_TREND", None), ("X_FV", None), ("X_BAND", None),
                         ("X_TRAIL_PTS", 25), ("X_TRAIL_PTS", 50), ("X_TRAIL_PTS", 80),
                         ("X_TARGET", 60))]

    # ---------------- 288 x 21 weekly gross-net matrix --------------------------------------
    M, N = {}, {}          # cfg -> {image_id: gross_net}, {image_id: n_trades}
    for k, (D, G, P, C, X, xp) in enumerate(CFG):
        name = f"{D}|{G}|{P}|{C}|{X}{'' if xp is None else ':'+str(xp)}"
        sig = layer_a_v2(fb_bars, trend_fit, D, G, P, C, "H1a")
        trl = layer_b_exit(fb_bars, trend_fit, sig, fb_atr, X, xp)
        M[name], N[name] = {}, {}
        for r, a, b in fit_wins:
            g, n = week_net(trl, a, b)
            M[name][r["image_id"]], N[name][r["image_id"]] = g, n
        for r, bb, aa, tr2, a, b in hold_sets:
            s2 = layer_a_v2(bb, tr2, D, G, P, C, "H1a")
            t2 = layer_b_exit(bb, tr2, s2, aa, X, xp)
            g, n = week_net(t2, a, b)
            M[name][r["image_id"]], N[name][r["image_id"]] = g, n
        if (k + 1) % 48 == 0:
            print(f"  ... {k+1}/{len(CFG)}", flush=True)

    # ---------------- B1 harness ------------------------------------------------------------
    fit_ids = [r["image_id"] for r, _, _ in fit_wins]
    inc_fit_trades = sum(N[INCUMBENT][i] for i in fit_ids)
    ok = abs(inc_fit_trades - 1512) <= 2
    print(f"\nB1: incumbent fit trades = {inc_fit_trades}  -> {'PASS' if ok else 'FAIL - RUN VOID'}")
    if not ok:
        return

    # ---------------- the five sheets -------------------------------------------------------
    v1_cfg = {w: max(M, key=lambda c: M[c][w]) for w in weeks}
    v2_cfg = {}
    for j, w in enumerate(weeks):
        v2_cfg[w] = INCUMBENT if j == 0 else max(M, key=lambda c: M[c][weeks[j - 1]])

    def sheet(getter):
        return {w: getter(w) for w in weeks}

    sheets = {
        "HIS": sheet(lambda w: his[w]),
        "FROZEN_INCUMBENT_gross": sheet(lambda w: M[INCUMBENT][w]),
        "FROZEN_INCUMBENT_net": sheet(lambda w: M[INCUMBENT][w] - COMMISSION_RT * N[INCUMBENT][w]),
        "FROZEN_LEADING_gross": sheet(lambda w: M[LEADING][w]),
        "FROZEN_LEADING_net": sheet(lambda w: M[LEADING][w] - COMMISSION_RT * N[LEADING][w]),
        "SHOWCASE_V1": sheet(lambda w: M[v1_cfg[w]][w]),
        "SHOWCASE_V2": sheet(lambda w: M[v2_cfg[w]][w]),
    }

    print(f"\n{'sheet':<26}{'pos/21':>8}{'total':>13}{'mean':>10}{'best':>11}{'worst':>11}")
    summary = {}
    for nm, s in sheets.items():
        v = list(s.values())
        summary[nm] = dict(pos=sum(1 for x in v if x > 0), total=sum(v),
                           mean=np.mean(v), best=max(v), worst=min(v))
        d = summary[nm]
        print(f"{nm:<26}{d['pos']:>5}/21{d['total']:>13,.0f}{d['mean']:>10,.0f}"
              f"{d['best']:>11,.0f}{d['worst']:>11,.0f}")

    # preregistered readouts
    A1 = summary["SHOWCASE_V1"]["pos"] >= 0.8 * 21 and \
        summary["SHOWCASE_V1"]["total"] >= summary["HIS"]["total"]
    A2 = summary["SHOWCASE_V1"]["total"] < 0.5 * summary["HIS"]["total"]
    gap_his = summary["HIS"]["total"] - summary["FROZEN_INCUMBENT_net"]["total"]
    gap_v1 = summary["SHOWCASE_V1"]["total"] - summary["FROZEN_INCUMBENT_net"]["total"]
    print(f"\nA1 (V1 >=80% pos AND total >= HIS): {A1}")
    print(f"A2 (V1 total < 50% of HIS):         {A2}")
    print(f"A3 methodology share of the total gap: {gap_v1/gap_his if gap_his else float('nan'):.2f}"
          f"   (V1-frozen {gap_v1:,.0f} / HIS-frozen {gap_his:,.0f})")
    print(f"A4 V2 total {summary['SHOWCASE_V2']['total']:,.0f} "
          f"(frozen {summary['FROZEN_INCUMBENT_net']['total']:,.0f} <-> V1 {summary['SHOWCASE_V1']['total']:,.0f})")

    # ---------------- outputs ---------------------------------------------------------------
    with open(os.path.join(OUT, "weekly_net_matrix.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["cfg"] + weeks)
        for c in M:
            w.writerow([c] + [round(M[c][i], 2) for i in weeks])
    with open(os.path.join(OUT, "sheets.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["image_id", "report_start"] + list(sheets) + ["v1_cfg", "v2_cfg"])
        for i in weeks:
            rs = next(x for x in tg_all if x["image_id"] == i)["report_start"]
            w.writerow([i, rs] + [round(sheets[nm][i], 2) for nm in sheets] +
                       [v1_cfg[i], v2_cfg[i]])
    print(f"\nwritten: {OUT}\\weekly_net_matrix.csv, sheets.csv")


if __name__ == "__main__":
    main()
