"""XM_EXEC_COST_AUDIT_V1 — ADDENDUM 2 (Y8..Y11). Robustness only; changes no gate.

Y8  instantaneous-quote fragility: the point estimate uses the quote AT the instant, exactly
    as G2_EXEC01 did. A transient 38-tick book is not what a market order pays. Re-measure
    with (a) the median quoted spread over [t, t+10s], and (b) the ACTUAL trade prints in
    [t, t+5s] versus the substrate bar-open the backtest assumed. Reported as a robustness
    band around the frozen headline, never as a replacement for it.
Y9  minute-by-minute decomposition of the Y5 delay result: entry-only vs exit-only, and how
    much of XM's gross lives in the single minute 09:45->09:46.
Y10 delay ladder 1..5 minutes, entry-only, on the frozen action set.
Y11 the joint question: XM economics under (measured spread) AND (a realistic entry-timing
    slip), which is the cost model we would actually fund.
"""
from __future__ import annotations

import os
import sys
import time as _time

os.environ.setdefault("MPLBACKEND", "Agg")

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "runs", "XM_EXEC_COST_AUDIT_V1_20260831")
OUT = os.path.join(RUN, "out")
SRC = os.path.join(ROOT, "research", "weekly_edge", "src")
sys.path.insert(0, SRC)
sys.path.insert(0, ROOT)

from research_sdk.seal_guard import assert_presealed                     # noqa: E402
import run_we_w01 as W1                                                  # noqa: E402
from run_we_w01 import PV, COMM_RT                                       # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w51 import session_frames                                    # noqa: E402
from run_we_w51c import dd_profile                                       # noqa: E402

T0 = _time.time()
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
DDT = 20245.0
TICK, TICKV = 0.25, 5.0
STALE_NS = 5_000_000_000
ONE_MIN = np.timedelta64(60, "s")
ANCH, DEC, ENTM, EXITNB = 571, 585, 586, 946
V2_DIR = os.path.join(ROOT, "research", "data_microstructure_v2", "raw", "NQ")
ESNQ_NQ = os.path.join(ROOT, "research", "data_esnq", "parquet", "NQ")
V1_DIR = os.path.join(ROOT, "research", "scalping_lab", "substrate", "raw", "NQ")


def log(*a):
    print(f"[{_time.time()-T0:6.0f}s]", *a, flush=True)


def main():
    L = []

    def G(*a):
        s = " ".join(str(x) for x in a)
        L.append(s)
        print(s, flush=True)

    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr, sid = D["n"], D["t"], D["sid"]
    o, c = D["o"], D["c"]
    st_, en_, _ = session_frames(D)
    NSESS = D["n_sess"]
    sdate = pd.to_datetime(D["sess_date"])
    mod = ((tarr - tarr.astype("datetime64[D]")).astype("timedelta64[s]")
           .astype(np.int64) // 60).astype(np.int32)
    win = np.array([A <= tarr[st_[s]] < B for s in range(NSESS)])
    sess_in = np.flatnonzero(win)
    iso = sdate.isocalendar()
    wk = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).to_numpy()[sess_in]
    assert_presealed(pd.DataFrame({"t": pd.to_datetime(tarr)}), "t", "substrate")
    date_of = {sdate[s].strftime("%Y%m%d"): s for s in range(NSESS)}
    TT = pd.read_csv(os.path.join(OUT, "xm_trades.csv"), dtype={"sess_date": str})
    TT["sess_date"] = TT["sess_date"].str.zfill(8)
    SM = pd.read_csv(os.path.join(OUT, "session_offsets.csv"), dtype={"date": str})
    SM["date"] = SM["date"].str.zfill(8)
    OFF = {r.date: r.offset for r in SM.itertuples() if r.status == "ok"}
    CK = pd.read_csv(os.path.join(OUT, "clock_spread.csv"), dtype={"date": str})
    CK["date"] = CK["date"].str.zfill(8)

    G("=" * 112)
    G("XM_EXEC_COST_AUDIT_V1_20260831 — ADDENDUM 2 (Y8..Y11). Robustness only.")
    G("=" * 112)

    # ------------------------------------------------------------------- Y8
    G("")
    G("Y8 — INSTANTANEOUS-QUOTE FRAGILITY: what a market order would actually meet")
    G("    (a) median quoted spread over [t, t+10s]   (b) actual trade prints in [t, t+5s]")
    inv = {}
    for d_ in sorted({f[1:9] for f in os.listdir(V2_DIR) if f.endswith(".parquet")}):
        inv[d_] = os.path.join(V2_DIR, f"s{d_}.parquet")
    with open(os.path.join(ROOT, "research", "data_esnq", "ALLOWLIST_DEV_44.txt"),
              "r", encoding="utf-8") as f:
        allow = {ln.strip() for ln in f if ln.strip()}
    for d_ in sorted({f[1:9] for f in os.listdir(ESNQ_NQ) if f.endswith(".parquet")} & allow):
        inv.setdefault(d_, os.path.join(ESNQ_NQ, f"s{d_}.parquet"))
    for d_ in sorted({f[1:9] for f in os.listdir(V1_DIR)
                      if f.endswith(".parquet") and "_rth" not in f}
                     - {"20250811", "20250924", "20260430"}):
        inv.setdefault(d_, os.path.join(V1_DIR, f"s{d_}.parquet"))

    def at2(mv):
        ix = np.full(NSESS, -1, np.int64)
        m_ = mod == mv
        ix[sid[m_]] = np.flatnonzero(m_)
        return ix

    IE, IX = at2(ENTM), at2(EXITNB)
    rows = []
    for d_ in sorted(inv):
        if d_ not in date_of or d_ not in OFF:
            continue
        s = date_of[d_]
        tb = pq.read_table(inv[d_], columns=["bip", "time", "price"])
        qt = tb.column("time").to_numpy().astype("datetime64[ns]")
        qb = tb.column("bip").to_numpy()
        qp = tb.column("price").to_numpy()
        del tb
        assert_presealed(pd.DataFrame({"time": qt}), "time", f"quotes s{d_}")
        bt = qt[qb == 1].astype("int64"); bp = qp[qb == 1]
        at_ = qt[qb == 2].astype("int64"); ap = qp[qb == 2]
        lt = qt[qb == 0].astype("int64"); lp = qp[qb == 0]
        if len(bt) == 0 or len(at_) == 0:
            continue
        off = float(OFF[d_])
        for role, IDX in (("entry", IE), ("exit", IX)):
            bar = int(IDX[s])
            if bar < 0:
                continue
            t0 = int((tarr[bar] - ONE_MIN).astype("datetime64[ns]").astype("int64"))
            # (a) 10-second forward window of quoted spread, sampled on a 100 ms grid
            grid = t0 + np.arange(0, 10_001, 100, dtype="int64") * 1_000_000
            ib = np.searchsorted(bt, grid, side="right") - 1
            ia = np.searchsorted(at_, grid, side="right") - 1
            gm = (ib >= 0) & (ia >= 0)
            if gm.sum() < 20:
                continue
            spr = (ap[np.maximum(ia, 0)] - bp[np.maximum(ib, 0)])[gm]
            spr = spr[np.isfinite(spr) & (spr >= 0)]
            if len(spr) < 20:
                continue
            # (b) actual trade prints in the first 5 s vs the substrate bar OPEN
            m5 = (lt >= t0) & (lt < t0 + 5_000_000_000)
            pr = lp[m5] - off        # corrected onto the substrate's price frame
            openpx = float(o[bar])
            rows.append(dict(
                date=d_, role=role,
                inst_spread_tk=float((ap[max(ia[0], 0)] - bp[max(ib[0], 0)]) / TICK)
                if (ib[0] >= 0 and ia[0] >= 0) else np.nan,
                win10_med_tk=float(np.median(spr) / TICK),
                win10_mean_tk=float(np.mean(spr) / TICK),
                n_prints_5s=int(m5.sum()),
                print_max_minus_open=float(pr.max() - openpx) if m5.sum() else np.nan,
                print_min_minus_open=float(pr.min() - openpx) if m5.sum() else np.nan,
                print_range_tk=float((pr.max() - pr.min()) / TICK) if m5.sum() else np.nan))
    Y8 = pd.DataFrame(rows)
    Y8.to_csv(os.path.join(OUT, "y8_window_robustness.csv"), index=False)
    for role in ("entry", "exit"):
        g = Y8[Y8["role"] == role]
        G(f"  {role:<6} n={len(g):<3}  instant mean {g['inst_spread_tk'].mean():.2f} tk  |  "
          f"[t,t+10s] median-of-median {g['win10_med_tk'].median():.2f}, "
          f"mean-of-median {g['win10_med_tk'].mean():.2f} tk")
        G(f"         actual prints in [t,t+5s]: median count {g['n_prints_5s'].median():.0f}, "
          f"median print-range {g['print_range_tk'].median():.1f} tk, "
          f"mean print-range {g['print_range_tk'].mean():.1f} tk")
    rt_inst = TICKV * (Y8[Y8.role == "entry"]["inst_spread_tk"].mean()
                       + Y8[Y8.role == "exit"]["inst_spread_tk"].mean()) / 2.0
    rt_w10 = TICKV * (Y8[Y8.role == "entry"]["win10_med_tk"].mean()
                      + Y8[Y8.role == "exit"]["win10_med_tk"].mean()) / 2.0
    G(f"  RT spread cost: instantaneous ${rt_inst:.2f}  vs  10-second-median ${rt_w10:.2f}")
    G("  -> the frozen headline uses the INSTANTANEOUS measure (G2_EXEC01's method, kept for")
    G("     comparability with P1). The 10 s figure is the honest lower rail of the band.")
    bad = Y8[(Y8.role == "entry") & (Y8.inst_spread_tk >= 12)]
    if len(bad):
        G("  the widest instantaneous entries, re-read over 10 s:")
        for _, r_ in bad.sort_values("inst_spread_tk", ascending=False).head(6).iterrows():
            G(f"    {r_['date']}  instant {r_['inst_spread_tk']:.0f} tk -> 10s median "
              f"{r_['win10_med_tk']:.1f} tk  (prints in 5 s: {int(r_['n_prints_5s'])}, "
              f"range {r_['print_range_tk']:.0f} tk)")

    # ------------------------------------------------------------------- Y9 / Y10
    G("")
    G("Y9 — WHERE THE MINUTE MATTERS: entry-only vs exit-only delay (frozen action set)")

    def delay(d_ent, d_exit):
        dl = np.zeros(NSESS)
        for r_ in TT.itertuples():
            s = int(r_.sess)
            e2, x2 = int(r_.eti) + d_ent, int(r_.xti) + d_exit
            ep2 = o[e2] if (0 <= e2 < n and sid[e2] == s) else float(r_.epx)
            xp2 = o[x2] if (0 <= x2 < n and sid[x2] == s) else float(r_.xpx)
            dl[s] += int(r_.d) * ((xp2 - ep2) - (float(r_.xpx) - float(r_.epx))) * PV
        w_ = pd.Series(dl[sess_in]).groupby(wk).sum()
        return (float(w_.mean()), float(w_.std(ddof=1) / np.sqrt(len(w_))),
                float(dl[sess_in].sum()))

    for lab, de, dx in (("entry +1 min only", 1, 0), ("exit +1 min only", 0, 1),
                        ("both +1 min", 1, 1)):
        m_, se_, tot = delay(de, dx)
        G(f"  {lab:<20} delta ${m_:+8.2f}/wk (SE ${se_:.2f}, t {m_/max(se_,1e-9):+.2f})  "
          f"total ${tot:+,.0f}  = {100*m_/936.32:+.1f}% of XM's weekly")
    first_min = float(sum(int(r_.d) * (o[int(r_.eti) + 1] - o[int(r_.eti)]) * PV
                          for r_ in TT.itertuples() if int(r_.eti) + 1 < n
                          and sid[int(r_.eti) + 1] == int(r_.sess)))
    gross_tot = float(TT["gross"].sum())
    G(f"  gross earned in the SINGLE minute 09:45->09:46 : ${first_min:,.0f} = "
      f"{100*first_min/gross_tot:.1f}% of XM's ${gross_tot:,.0f} gross, on "
      f"{1.0/360*100:.2f}% of its holding time")
    G("")
    G("Y10 — ENTRY-DELAY LADDER (exit unchanged)")
    for k in (1, 2, 3, 5, 10):
        m_, se_, tot = delay(k, 0)
        G(f"  entry +{k:>2} min : ${m_:+8.2f}/wk (t {m_/max(se_,1e-9):+.2f})  "
          f"cumulative {100*m_/936.32:+.1f}% of weekly")

    # ------------------------------------------------------------------- Y11
    G("")
    G("Y11 — THE COST MODEL WE WOULD ACTUALLY FUND")
    gs = np.zeros(NSESS)
    traded = np.zeros(NSESS, bool)
    for r_ in TT.itertuples():
        gs[int(r_.sess)] = float(r_.gross)
        traded[int(r_.sess)] = True

    def econ(spread, extra_slip_usd, label):
        C = COMM_RT + spread + extra_slip_usd
        ser = np.where(traded, gs - C, 0.0)
        w_ = pd.Series(ser[sess_in]).groupby(wk).sum().to_numpy()
        dp = dd_profile(w_)
        return dict(scenario=label, all_in=C, net=float(ser[sess_in].sum()),
                    weekly=float(w_.mean()), maxdd=float(dp["maxdd"]),
                    fixdd=float(w_.mean()) * DDT / max(dp["maxdd"], 1e-9),
                    t=float(w_.mean()) / max(w_.std(ddof=1) / np.sqrt(len(w_)), 1e-9))

    m1, _, _ = delay(1, 0)
    slip_per_trade = -m1 * len(pd.unique(wk)) / len(TT)     # $/trade equivalent of a 1-min slip
    rows2 = [econ(12.50, 0.0, "A booked model"),
             econ(18.42, 0.0, "B measured spread (X1)"),
             econ(20.08, 0.0, "C measured spread (X2 clock)"),
             econ(28.42, 0.0, "D measured + 1 tk/leg"),
             econ(18.42, slip_per_trade * 0.25, "E measured + 15 s slip proxy"),
             econ(18.42, slip_per_trade, "F measured + FULL 1-min slip"),
             econ(28.42, slip_per_trade, "G pessimistic + FULL 1-min slip")]
    E2 = pd.DataFrame(rows2)
    E2.to_csv(os.path.join(OUT, "funded_scenarios.csv"), index=False)
    base = float(E2.loc[0, "weekly"])
    G(f"  1-minute entry slip is worth ${slip_per_trade:,.2f}/trade "
      f"(${-m1:.2f}/wk) — for scale, the ENTIRE booked round-turn cost is $16.86/trade")
    G(f"{'scenario':<32}{'all-in $/RT':>12}{'net total':>13}{'$/wk':>9}{'% booked':>10}"
      f"{'maxDD':>10}{'t':>7}")
    for _, r_ in E2.iterrows():
        G(f"{r_['scenario']:<32}{r_['all_in']:>12.2f}{r_['net']:>13,.0f}"
          f"{r_['weekly']:>9.2f}{100*r_['weekly']/base:>9.1f}%{r_['maxdd']:>10,.0f}"
          f"{r_['t']:>7.2f}")
    G("")
    G("compliance: read-only; no blind session; no sealed value; no order/deploy; no policy;")
    G("no model fitted; $0.")
    G(f"wall {_time.time()-T0:.0f}s")
    with open(os.path.join(OUT, "addendum2.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
