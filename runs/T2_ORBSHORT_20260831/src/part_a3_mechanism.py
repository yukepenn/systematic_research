"""T2_ORBSHORT_20260831 — PART A3: what IS the ORB control, and how fragile is it?

Mechanism decomposition, cost stress, circular-shift null, marginal-value bootstrap,
and the M_11-drawdown read. NO opening-range length is varied anywhere (barred).
Also: the state-matched placebo and opposite-sign read for Part B's S1, added as
DIAGNOSTICS after both arms had already been recorded FAILED at their frozen gates.
"""
from __future__ import annotations

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
RNG = np.random.default_rng(2026083101)
L = []


def ap(s=""):
    L.append(s); print(s, flush=True)


def session_id(ts):
    d = ts.dt.normalize()
    return (d + pd.to_timedelta((ts.dt.hour >= 18).astype(int), unit="D")).dt.date


def iso_week(dates):
    iso = pd.to_datetime(pd.Series(list(dates))).dt.isocalendar()
    return pd.Series((iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).values,
                     index=list(dates))


def wk(w):
    n = len(w); mu = float(w.mean()); sd = float(w.std(ddof=1))
    t = mu / sd * math.sqrt(n) if sd > 0 else float("nan")
    eq = w.cumsum(); dd = float((eq.cummax() - eq).max())
    return dict(mean=mu, t=t, maxdd=dd, total=float(w.sum()))


def stat_boot_idx(n, nrep, mb, rng):
    p = 1.0 / mb
    for r in range(nrep):
        idx = np.empty(n, dtype=np.int64); i = rng.integers(n)
        for j in range(n):
            idx[j] = i
            i = rng.integers(n) if rng.random() < p else (i + 1) % n
        yield idx


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

    b931 = df[df["hm"] == 931].set_index("sid")
    b1000 = df[df["hm"] == 1000].set_index("sid")
    b1001 = df[df["hm"] == 1001].set_index("sid")
    b1559 = df[df["hm"] == 1559].set_index("sid")["close"]
    opens = df.set_index(["sid", "hm"])["open"]

    ap("=" * 106)
    ap("PART A3 — MECHANISM, FRAGILITY, COST, NULL")
    ap("=" * 106)

    # ---- D1: is the OR STRUCTURE load-bearing, or is this just the sign of the first 30 min? ----
    ap("\nD1. IS THE OPENING RANGE LOAD-BEARING?  (no length is varied; B3's own 09:30-10:00 window)")
    common = b931.index.intersection(b1000.index).intersection(b1001.index).intersection(b1559.index)
    sgn = np.sign(b1000.loc[common, "close"].values - b931.loc[common, "open"].values)
    sgn = np.where(sgn == 0, 1, sgn)
    e = b1001.loc[common, "open"].values
    x = b1559.loc[common].values
    d1_net = sgn * (x - e) * PT - RT
    d1w = to_weekly(pd.Series(d1_net, index=list(common)))
    m = wk(d1w)
    ap(f"  D1 'sign of the 09:30->10:00 move', enter 10:01 open, exit 15:59, same cost:")
    ap(f"     n={len(common)}  net ${d1_net.sum():,.0f}  $/tr ${d1_net.mean():,.0f}  "
       f"wk ${m['mean']:,.0f}  t {m['t']:.2f}  maxDD ${m['maxdd']:,.0f}")
    ap(f"  B3 (the range-break object):  net ${orb['net'].sum():,.0f}  $/tr "
       f"${orb['net'].mean():,.0f}  wk $1,043  t 2.19  maxDD $60,782")
    # direction agreement
    sgn_map = dict(zip(list(common), sgn))
    agree = np.mean([sgn_map.get(s, 0) == d for s, d in zip(orb["sid"], orb["dir"])])
    ap(f"  direction agreement B3 vs 30-min sign: {agree*100:.1f}%")
    ap(f"  weekly corr(B3, D1) = {orb_w.corr(d1w):.3f}")

    # ---- D2: cost stress ----
    ap("\nD2. COST STRESS (the directive's warning: a research headline and an NT8 net are not the same)")
    for c, lab in [(4.36, "NT8 template only (M_11's basis)"), (18.80, "GENESIS baseline (headline)"),
                   (25.01, "ORB01's measured basis"), (33.00, "ORB01 stress")]:
        n = orb["gross"].sum() - c * len(orb)
        w = to_weekly(pd.Series(orb["gross"].values - c, index=orb["sid"].values).groupby(level=0).sum())
        mm = wk(w)
        ap(f"  ${c:>6.2f}/ctrRT  {lab:<34} net ${n:>10,.0f}  wk ${mm['mean']:>6,.0f}  t {mm['t']:.2f}")

    # ---- D3: whole-session circular-shift null ----
    ap("\nD3. WHOLE-SESSION CIRCULAR-SHIFT NULL (300 shifts; decisions move, outcomes do not)")
    dec = orb.set_index("sid")[["dir", "entry_hm"]]
    sess_list = [s for s in sessions if s in b1559.index]
    pos = {s: i for i, s in enumerate(sess_list)}
    dec_list = [(dec.loc[s, "dir"], dec.loc[s, "entry_hm"]) if s in dec.index else None
                for s in sess_list]
    exitpx = {s: float(b1559.loc[s]) for s in sess_list}

    def stat_for_shift(k):
        tot = 0.0
        for i, s in enumerate(sess_list):
            d = dec_list[(i - k) % len(sess_list)]
            if d is None:
                continue
            key = (s, int(d[1]))
            if key not in opens.index:
                continue
            o = float(opens.loc[key])
            tot += d[0] * (exitpx[s] - o) * PT - RT
        return tot

    real = stat_for_shift(0)
    ks = RNG.choice(np.arange(1, len(sess_list)), size=300, replace=False)
    null = np.array([stat_for_shift(int(k)) for k in ks])
    ap(f"  (statistic uses bar-OPEN fills so real and null are the same estimator)")
    ap(f"  real ${real:,.0f}   null mean ${null.mean():,.0f}  p95 ${np.percentile(null,95):,.0f}  "
       f"percentile {(null<real).mean()*100:.1f}   p_ge {(null>=real).mean():.4f}")
    ap(f"  null spread (max-min) ${null.max()-null.min():,.0f}  -> the null moves; it has teeth")

    # ---- D4: ex-tail weekly t, and marginal-value bootstrap ----
    ap("\nD4. FRAGILITY OF THE HEADLINE t")
    srt = orb.sort_values("net", ascending=False)
    for k in (1, 5, 11):
        sub = srt.iloc[k:]
        w = to_weekly(sub.set_index("sid")["net"])
        mm = wk(w)
        ap(f"  ex-top-{k:<3} net ${mm['total']:>10,.0f}  wk ${mm['mean']:>6,.0f}  t {mm['t']:.2f}")
    ap("  (LOYO weekly t from A2: 1.85 / 2.01 / 1.74 / 1.94 / 2.29 — only excl-2026 stays above 2.0)")

    p1 = pd.read_csv(P1_CSV, parse_dates=["et"]); p1["sid"] = session_id(p1["et"])
    xm = pd.read_csv(XM_CSV, parse_dates=["et"]); xm["sid"] = session_id(xm["et"])
    p1w = to_weekly(p1[p1["sid"].isin(set(sessions))].groupby("sid")["pnl"].sum())
    xmw = to_weekly(xm[xm["sid"].isin(set(sessions))].groupby("sid")["pnl"].sum())
    m11 = p1w + xmw
    ap("\nD5. MARGINAL VALUE OF 0.25xORB, BOOTSTRAPPED (stationary, 2,000 reps, mean block 4 wks)")
    A = m11.values; B = orb_w.values
    deltas = []
    for idx in stat_boot_idx(len(A), 2000, 4.0, RNG):
        a, b = A[idx], B[idx]
        ea = np.cumsum(a); dda = float((np.maximum.accumulate(ea) - ea).max())
        c = a + 0.25 * b
        ec = np.cumsum(c); ddc = float((np.maximum.accumulate(ec) - ec).max())
        if dda > 0 and ddc > 0:
            deltas.append(c.mean() * dda / ddc - a.mean())
    deltas = np.array(deltas)
    ap(f"  point estimate +$572/wk at matched maxDD;  bootstrap median ${np.median(deltas):,.0f}  "
       f"95% CI [${np.percentile(deltas,2.5):,.0f}, ${np.percentile(deltas,97.5):,.0f}]  "
       f"P(delta<=0) = {(deltas<=0).mean():.3f}")
    ap("  ⚠ 0.25x is one of three preregistered weights (0.25/0.5/1.0) and is the best of the three:")
    ap("    treat +$572 as a BEST-OF-3 figure, and 0.25 contracts is not an executable integer size.")

    # ---- D6: behaviour in the M_11 drawdown ----
    ap("\nD6. WHAT ORB DID DURING THE INCUMBENT'S 2026 DRAWDOWN (no filter is being built from this)")
    for lab, lo, hi in [("2026-06-01..2026-07-31", "2026-06-01", "2026-07-31"),
                        ("2026-01-01..2026-07-31", "2026-01-01", "2026-07-31"),
                        ("2022-01-03..2022-12-31", "2022-01-03", "2022-12-31")]:
        sel = [s for s in sessions if str(lo) <= str(s) <= str(hi)]
        ow = orb.set_index("sid")["net"].reindex(sel).fillna(0.0).sum()
        pw = p1[p1["sid"].isin(sel)]["pnl"].sum()
        xw = xm[xm["sid"].isin(sel)]["pnl"].sum()
        ap(f"  {lab}: ORB ${ow:>10,.0f}   P1 ${pw:>10,.0f}   XM ${xw:>10,.0f}   M_11 ${pw+xw:>10,.0f}")

    # ---- D7: Part B S1 diagnostics (post-verdict, labelled) ----
    ap("\nD7. POST-VERDICT DIAGNOSTICS ON S1 (both arms were already recorded FAILED above)")
    s1 = pd.read_csv(os.path.join(OUT, "short_trades_S1.csv"))
    s1["sid"] = pd.to_datetime(s1["sid"]).dt.date
    # state-matched placebo: random entry slot on the SAME triggered sessions
    slots = s1["entry_hm"].values
    real_pt = float(s1["net"].mean())
    draws = np.empty(1000)
    for r in range(1000):
        acc = []
        for s in s1["sid"]:
            hh = int(RNG.choice(slots))
            key = (s, hh)
            if key not in opens.index:
                continue
            acc.append((float(opens.loc[key]) - float(b1559.loc[s])) * PT - RT)
        draws[r] = np.mean(acc)
    ap(f"  STATE-MATCHED placebo (random entry minute on the SAME 772 triggered sessions):")
    ap(f"     null mean ${draws.mean():,.0f}  p5 ${np.percentile(draws,5):,.0f}  "
       f"p95 ${np.percentile(draws,95):,.0f}  REAL ${real_pt:,.0f}  "
       f"percentile {(draws<real_pt).mean()*100:.1f}")
    ap(f"  OPPOSITE SIGN at the identical bars (a measured fact, NOT a candidate — the sign was")
    ap(f"  preregistered SHORT and a profitable flip is a FAILURE of the stated mechanism):")
    flip = -(s1["gross"].values) - RT
    fw = to_weekly(pd.Series(flip, index=s1["sid"].values).groupby(level=0).sum())
    mm = wk(fw)
    ap(f"     n={len(flip)}  net ${flip.sum():,.0f}  $/tr ${flip.mean():,.0f}  wk ${mm['mean']:,.0f}  "
       f"t {mm['t']:.2f}   [this is DISCOVERY_CONSUMED and inherits the whole fade graveyard]")

    open(os.path.join(OUT, "part_a3_mechanism.txt"), "w", encoding="utf-8").write("\n".join(L) + "\n")


if __name__ == "__main__":
    sys.exit(main())
