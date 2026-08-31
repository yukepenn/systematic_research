"""T2_ORBSHORT_20260831 — PART A2: decomposition, controls, tail audit, incumbent overlap.

Runs only after part_a_orb.py has PASSED G_A1..G_A3 (reproduction gate).
Every table here is preregistered in spec.yaml part_a.decompositions_preregistered.
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np
import pandas as pd

REPO = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(REPO, "runs", "T2_ORBSHORT_20260831")
OUT = os.path.join(RUN, "out")
PARQUET = os.path.join(REPO, "runs", "SM1M_SUBSTRATE", "out", "nq_1m_2022_2026.parquet")
P1_CSV = os.path.join(REPO, "runs", "G2_AUG_INCUMBENT_READ_20260830", "out", "p1_trades_full.csv")
XM_CSV = os.path.join(REPO, "runs", "G2_AUG_INCUMBENT_READ_20260830", "out", "xm_trades_full.csv")

PT, RT = 20.0, 18.80
RNG = np.random.default_rng(20260831)
L = []


def ap(s=""):
    L.append(s)
    print(s, flush=True)


def session_id(ts):
    d = ts.dt.normalize()
    return (d + pd.to_timedelta((ts.dt.hour >= 18).astype(int), unit="D")).dt.date


def iso_week(dates):
    iso = pd.to_datetime(pd.Series(list(dates))).dt.isocalendar()
    return pd.Series((iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).values,
                     index=list(dates))


def wk_metrics(w):
    n = len(w); mu = float(w.mean()); sd = float(w.std(ddof=1))
    t = mu / sd * math.sqrt(n) if sd > 0 else float("nan")
    eq = w.cumsum(); dd = float((eq.cummax() - eq).max())
    return dict(n_weeks=n, mean=mu, sd=sd, t=t, maxdd=dd, total=float(w.sum()),
                pct_pos=float((w > 0).mean() * 100), worst=float(w.min()))


def stat_boot(x, nrep, mb, rng):
    n = len(x); p = 1.0 / mb; out = np.empty(nrep)
    for r in range(nrep):
        idx = np.empty(n, dtype=np.int64); i = rng.integers(n)
        for j in range(n):
            idx[j] = i
            i = rng.integers(n) if rng.random() < p else (i + 1) % n
        out[r] = x[idx].mean()
    return out


def main():
    df = pd.read_parquet(PARQUET).sort_values("time").reset_index(drop=True)
    df["sid"] = session_id(df["time"])
    df["hm"] = df["time"].dt.hour * 100 + df["time"].dt.minute
    sessions = pd.Index(sorted(df["sid"].unique()))
    week_of = iso_week(sessions)
    week_grid = pd.Index(pd.unique(week_of.values))

    def to_weekly(s):
        s = pd.Series(s, index=sessions).fillna(0.0)
        return s.groupby(week_of.values).sum().reindex(week_grid, fill_value=0.0)

    orb = pd.read_csv(os.path.join(OUT, "orb_trades.csv"), parse_dates=["entry_ts"])
    orb["sid"] = pd.to_datetime(orb["sid"]).dt.date
    orb_w = to_weekly(orb.set_index("sid")["net"])

    ap("=" * 108)
    ap("PART A2 — ORB (B3, 30-min OR) DECOMPOSITION.  Population 2022-01-03..2026-07-31, 1,133 trades, 239 wks")
    ap("=" * 108)

    # ---------- 1. legs ----------
    ap("\n1. DIRECTION SYMMETRY — the leg decomposition the scoreboard never printed")
    ap(f"{'leg':<10}{'n':>6}{'gross pts':>12}{'net $':>13}{'$/trade':>10}{'win%':>8}{'wk mean':>10}{'wk t':>8}")
    legrows = {}
    for name, sel in [("LONG", orb["dir"] == 1), ("SHORT", orb["dir"] == -1), ("BOTH", orb["dir"] != 0)]:
        sub = orb[sel]
        w = to_weekly(sub.set_index("sid")["net"])
        mm = wk_metrics(w)
        legrows[name] = dict(n=len(sub), gross_pts=float(sub["gross"].sum() / PT),
                             net=float(sub["net"].sum()), per_trade=float(sub["net"].mean()),
                             win=float((sub["net"] > 0).mean() * 100), **mm)
        ap(f"{name:<10}{len(sub):>6}{sub['gross'].sum()/PT:>12,.1f}{sub['net'].sum():>13,.0f}"
           f"{sub['net'].mean():>10,.0f}{(sub['net']>0).mean()*100:>8.1f}{mm['mean']:>10,.0f}{mm['t']:>8.2f}")

    # ---------- 2. controls at the SAME bars ----------
    ap("\n2. CONTROLS AT THE SAME ENTRY BARS  (the drift control B3 never had; ORB01 FAILED its version)")
    bar_open = df.set_index(["sid", "hm"])["open"]
    b1559 = df[df["hm"] == 1559].set_index("sid")["close"]
    c_open = np.array([bar_open.loc[(s, h)] for s, h in zip(orb["sid"], orb["entry_hm"])], dtype=float)
    c_exit = orb["exit_px"].values
    ctrl_long = (c_exit - c_open) * PT - RT                       # C1 long at same bar's open
    ctrl_flip = -(orb["gross"].values) - RT                       # C2 opposite side, same fills
    # C3: always-long every session at the 10:01 open (ORB01's O3 shape, at B3's clock)
    o1001 = df[df["hm"] == 1001].set_index("sid")["open"]
    common = o1001.index.intersection(b1559.index)
    ctrl_alwayslong = (b1559.loc[common] - o1001.loc[common]) * PT - RT
    for nm, arr, idx in [("ORB (real)", orb["net"].values, orb["sid"].values),
                         ("C1 long @ same bars", ctrl_long, orb["sid"].values),
                         ("C2 flip @ same bars", ctrl_flip, orb["sid"].values),
                         ("C3 long 10:01 all sess", ctrl_alwayslong.values, np.array(list(common)))]:
        w = to_weekly(pd.Series(arr, index=idx).groupby(level=0).sum())
        mm = wk_metrics(w)
        ap(f"{nm:<24} n={len(arr):>5}  net ${arr.sum():>10,.0f}  $/tr {arr.mean():>7,.0f}  "
           f"wk ${mm['mean']:>7,.0f}  t {mm['t']:>5.2f}  maxDD ${mm['maxdd']:>9,.0f}")
    ap(f"  --> ORB minus C1 (does DIRECTION SELECTION add anything?) = "
       f"${orb['net'].sum() - ctrl_long.sum():,.0f} over 1,133 bars")

    # ---------- 3. per-year, LOYO ----------
    ap("\n3. ERA STABILITY")
    orb["year"] = pd.to_datetime(pd.Series(list(orb["sid"]))).dt.year.values
    ap(f"{'year':<7}{'n':>6}{'nL':>5}{'nS':>5}{'net $':>12}{'long $':>12}{'short $':>12}")
    for y, sub in orb.groupby("year"):
        ap(f"{y:<7}{len(sub):>6}{(sub['dir']==1).sum():>5}{(sub['dir']==-1).sum():>5}"
           f"{sub['net'].sum():>12,.0f}{sub[sub['dir']==1]['net'].sum():>12,.0f}"
           f"{sub[sub['dir']==-1]['net'].sum():>12,.0f}")
    ap(f"\n{'excl year':<11}{'net $':>12}{'wk mean':>10}{'wk t':>8}{'n_wk':>6}")
    for y in sorted(orb["year"].unique()):
        sub = orb[orb["year"] != y]
        keep = [s for s in sessions if s.year != y]
        wo = week_of.loc[keep]
        wg = pd.Index(pd.unique(wo.values))
        w = pd.Series(sub.set_index("sid")["net"], index=keep).fillna(0.0).groupby(wo.values).sum().reindex(wg, fill_value=0.0)
        mm = wk_metrics(w)
        ap(f"{y:<11}{sub['net'].sum():>12,.0f}{mm['mean']:>10,.0f}{mm['t']:>8.2f}{mm['n_weeks']:>6}")

    # ---------- 4. tail audit ----------
    ap("\n4. TAIL AUDIT (mandatory for every impressive result)")
    s = np.sort(orb["net"].values)[::-1]
    tot = s.sum()
    for q, lab in [(0.01, "top 1%"), (0.05, "top 5%"), (0.10, "top 10%")]:
        k = max(1, int(round(q * len(s))))
        ap(f"  {lab:<9} = {k:>4} trades = ${s[:k].sum():>10,.0f} = {s[:k].sum()/tot*100:>7.1f}% of net")
    ap(f"  net ex-top-1  = ${tot - s[0]:>10,.0f}")
    ap(f"  net ex-top-5  = ${tot - s[:5].sum():>10,.0f}")
    ap(f"  median trade  = ${np.median(orb['net']):>10,.0f}   win rate {(orb['net']>0).mean()*100:.1f}%")
    wsort = np.sort(orb_w.values)[::-1]
    ap(f"  top 10 WEEKS  = ${wsort[:10].sum():>10,.0f} = {wsort[:10].sum()/tot*100:.1f}% of net")

    # ---------- 5. bootstrap ----------
    ap("\n5. STATIONARY BLOCK BOOTSTRAP on the weekly net series (10,000 reps, mean block 4 wks)")
    bs = stat_boot(orb_w.values, 10000, 4.0, RNG)
    ap(f"  weekly mean ${orb_w.mean():,.0f}   bootstrap 95% CI [${np.percentile(bs,2.5):,.0f}, ${np.percentile(bs,97.5):,.0f}]"
       f"   P(mean<=0) = {(bs<=0).mean():.4f}")

    # ---------- 6. entry-time ----------
    ap("\n6. ENTRY-TIME PROFILE")
    q = orb["entry_hm"].quantile([0.25, 0.5, 0.75])
    ap(f"  entry hm p25/median/p75 = {int(q.iloc[0])} / {int(q.iloc[1])} / {int(q.iloc[2])}")
    orb["hr"] = orb["entry_hm"] // 100
    ap(f"  {'hour':<6}{'n':>6}{'net $':>12}{'$/tr':>9}")
    for h, sub in orb.groupby("hr"):
        ap(f"  {h:<6}{len(sub):>6}{sub['net'].sum():>12,.0f}{sub['net'].mean():>9,.0f}")

    # ---------- 7. incumbent overlap ----------
    ap("\n" + "=" * 108)
    ap("7. OVERLAP WITH THE INCUMBENT M_11  (P1/PCT + XM_CONFLICT, NT8 certified trade files)")
    ap("=" * 108)
    p1 = pd.read_csv(P1_CSV, parse_dates=["et", "xt"])
    xm = pd.read_csv(XM_CSV, parse_dates=["et", "xt"])
    for nm, d in [("P1", p1), ("XM", xm)]:
        d["sid"] = session_id(d["et"])
        d["hm"] = d["et"].dt.hour * 100 + d["et"].dt.minute
    p1w = p1[p1["sid"].isin(set(sessions))]
    xmw = xm[xm["sid"].isin(set(sessions))]
    ap(f"  in-window trades: P1 {len(p1w)} of {len(p1)} (Aug dropped)   XM {len(xmw)} of {len(xm)}")
    ap(f"  P1 entry-hour histogram: " +
       ", ".join(f"{h}h:{c}" for h, c in sorted(p1w['et'].dt.hour.value_counts().items())))
    ap(f"  XM entry-hour histogram: " +
       ", ".join(f"{h}h:{c}" for h, c in sorted(xmw['et'].dt.hour.value_counts().items())))
    p1_sess = p1w.groupby("sid")["pnl"].sum()
    xm_sess = xmw.groupby("sid")["pnl"].sum()
    p1_w = to_weekly(p1_sess)
    xm_w = to_weekly(xm_sess)
    m11_w = p1_w + xm_w
    ap(f"\n  in-window nets: P1 ${p1_sess.sum():,.0f}  XM ${xm_sess.sum():,.0f}  M_11 ${p1_sess.sum()+xm_sess.sum():,.0f}"
       f"  ORB ${orb['net'].sum():,.0f}")
    for nm, w in [("P1", p1_w), ("XM", xm_w), ("M_11", m11_w), ("ORB", orb_w)]:
        mm = wk_metrics(w)
        ap(f"  {nm:<6} wk ${mm['mean']:>7,.0f}  t {mm['t']:>5.2f}  maxDD ${mm['maxdd']:>9,.0f}  "
           f"%pos {mm['pct_pos']:>5.1f}  worst ${mm['worst']:>9,.0f}")

    ap("\n  CORRELATIONS (weekly, common ISO grid, n=%d)" % len(week_grid))
    W = pd.DataFrame({"ORB": orb_w, "P1": p1_w, "XM": xm_w, "M11": m11_w})
    ap("  pearson:\n" + W.corr().round(3).to_string())
    ap("  spearman:\n" + W.corr(method="spearman").round(3).to_string())
    S = pd.DataFrame({"ORB": pd.Series(orb.set_index("sid")["net"], index=sessions).fillna(0.0),
                      "P1": pd.Series(p1_sess, index=sessions).fillna(0.0),
                      "XM": pd.Series(xm_sess, index=sessions).fillna(0.0)})
    ap(f"  session-level pearson ORB~P1 {S['ORB'].corr(S['P1']):.3f}   ORB~XM {S['ORB'].corr(S['XM']):.3f}")

    # ---------- 8. P1-FLAT sessions ----------
    ap("\n8. ORB ACTIVITY AND ECONOMICS ON P1-FLAT SESSIONS  (with the matched unconditional control)")
    p1_active = set(p1w["sid"])
    orb_idx = orb.set_index("sid")
    flat = [s for s in sessions if s not in p1_active]
    act = [s for s in sessions if s in p1_active]
    ap(f"  sessions: total {len(sessions)}  P1-ACTIVE {len(act)} ({len(act)/len(sessions)*100:.1f}%)  "
       f"P1-FLAT {len(flat)} ({len(flat)/len(sessions)*100:.1f}%)")
    for nm, grp in [("P1-FLAT", flat), ("P1-ACTIVE", act), ("ALL (control)", list(sessions))]:
        sub = orb_idx.reindex([s for s in grp if s in orb_idx.index])
        if len(sub) == 0:
            continue
        ap(f"  {nm:<15} ORB trades {len(sub):>5} ({len(sub)/len(grp)*100:>5.1f}% of the group)   "
           f"net ${sub['net'].sum():>10,.0f}   $/trade {sub['net'].mean():>7,.0f}   "
           f"long {int((sub['dir']==1).sum()):>4} / short {int((sub['dir']==-1).sum()):>4}")
    # Welch on $/trade flat vs active
    a = orb_idx.reindex([s for s in flat if s in orb_idx.index])["net"].values
    b = orb_idx.reindex([s for s in act if s in orb_idx.index])["net"].values
    se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    ap(f"  contrast FLAT-minus-ACTIVE $/trade = ${a.mean()-b.mean():,.0f}  Welch t = {(a.mean()-b.mean())/se:.2f}")

    # ---------- 9. directional co-exposure ----------
    ap("\n9. SAME-DIRECTION CONCENTRATION (P1 is long-only; how much of ORB is long alongside it?)")
    long_on_active = orb_idx.reindex([s for s in act if s in orb_idx.index])
    ap(f"  ORB entries on P1-ACTIVE sessions: {len(long_on_active)}   of which LONG "
       f"{int((long_on_active['dir']==1).sum())} ({(long_on_active['dir']==1).mean()*100:.1f}%)")
    ap(f"  ORB LONG net on P1-ACTIVE sessions ${long_on_active[long_on_active['dir']==1]['net'].sum():,.0f}; "
       f"ORB SHORT net there ${long_on_active[long_on_active['dir']==-1]['net'].sum():,.0f}")

    # ---------- 10. marginal value at COMMON TOTAL BOOK RISK ----------
    ap("\n10. MARGINAL VALUE OF ORB TO M_11 AT COMMON TOTAL BOOK RISK (weekly maxDD-matched)")
    base = wk_metrics(m11_w)
    ap(f"  M_11 alone:  wk ${base['mean']:,.0f}  maxDD ${base['maxdd']:,.0f}  "
       f"$/wk per $1 of maxDD = {base['mean']/base['maxdd']:.5f}")
    for k in (0.25, 0.5, 1.0):
        comb = m11_w + k * orb_w
        mm = wk_metrics(comb)
        scale = base["maxdd"] / mm["maxdd"]
        ap(f"  M_11 + {k:>4.2f}xORB: wk ${mm['mean']:>7,.0f}  maxDD ${mm['maxdd']:>9,.0f}  "
           f"t {mm['t']:>5.2f}  ->  rescaled to M_11 maxDD: ${mm['mean']*scale:>7,.0f}/wk  "
           f"(delta {mm['mean']*scale-base['mean']:+,.0f})")

    txt = "\n".join(L) + "\n"
    open(os.path.join(OUT, "part_a2_decomposition.txt"), "w", encoding="utf-8").write(txt)
    pd.DataFrame({"ORB": orb_w, "P1": p1_w, "XM": xm_w, "M11": m11_w}).to_csv(
        os.path.join(OUT, "weekly_series.csv"))


if __name__ == "__main__":
    sys.exit(main())
