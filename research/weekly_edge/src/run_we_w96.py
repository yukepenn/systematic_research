"""WE_W96 - THE OVERNIGHT DISPLACEMENT CHANNEL, TRADED DIRECTLY.

Spec: runs/WE_W96_NIGHTCHAN/spec.yaml, committed BEFORE this ran.

B-MOM is 100 % RTH (W89) and its entire interquartile entry range is 09:33-09:39 (W91). The same
mechanism - "price has travelled further from the session anchor than it typically does by this
time of day" - is defined overnight too, because the slot-of-day statistic is computed over all
bars. Nobody has ever traded it there. This builds that object at frozen parameters.
"""
from __future__ import annotations

import itertools
import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_we_w01 as W1                                                  # noqa: E402
from run_we_w01 import ROOT, PV, COMM_RT                                 # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w38 import sfills                                            # noqa: E402
from run_we_w51c import dd_profile                                       # noqa: E402
from run_we_w93 import build                                             # noqa: E402
from we_channels import session_clock, _mtod                             # noqa: E402
from we_fastctx import fast_build_context                                # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W96_NIGHTCHAN", "out")
os.makedirs(OUT, exist_ok=True)
W76OUT = os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out")
W79OUT = os.path.join(ROOT, "runs", "WE_W79_CLIQUE", "out")
W82OUT = os.path.join(ROOT, "runs", "WE_W82_FILLAUDIT", "out")
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
DDT = 20245.0
TICK, C_X9A, C_BMOM = 0.25, 14.55, 12.99
RT_X9A = 10.79
NDRAW = 200
RNG = np.random.default_rng(20260896)


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "night.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr, sid, lb, fb = D["n"], D["t"], D["sid"], D["lb"], D["fb"]
    c, o = D["c"], D["o"]
    X = fast_build_context(D)
    z = np.load(os.path.join(W76OUT, "mem_ext.npz"))
    mem, bmom, tilt = z["mem"], z["bmom"], z["tilt"]
    st = np.zeros(D["n_sess"], np.int64); st[sid[fb]] = np.flatnonzero(fb)
    sess_in = np.array([s for s in range(D["n_sess"]) if A <= tarr[st[s]] < B])
    in_win = np.zeros(D["n_sess"], bool); in_win[sess_in] = True
    inw = np.array([in_win[s] for s in sid])
    sdate = pd.to_datetime(D["sess_date"])[sess_in]
    iso = sdate.isocalendar()
    wk = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).to_numpy()
    yr = sdate.year.to_numpy()
    NWk = len(set(wk))
    P_(f"=== {len(sess_in)} sessions / {NWk} weeks [{_time.time()-t0:.0f}s]")

    # ------------------------------------------------------------------ THE CHANNEL
    hhmmss, seg, in_rth, n_seg = session_clock(D)
    sess_open = pd.Series(o).groupby(sid).transform("first").to_numpy()
    all_bars = np.ones(n, bool)
    mtod = _mtod(np.abs(c - sess_open), seg, hhmmss, in_rth, mask=all_bars)
    hi, lo = sess_open + mtod, sess_open - mtod
    night = (hhmmss >= 180000) | (hhmmss < 93000)
    live = night & (seg >= 14)
    raw = np.where(live & (c > np.nan_to_num(hi, nan=np.inf)), 1,
                   np.where(live & (c < np.nan_to_num(lo, nan=-np.inf)), -1, 0)).astype(np.int8)
    s_ = pd.Series(np.where(raw != 0, raw, np.nan))
    NIGHT = s_.groupby(sid).ffill().fillna(0.0).to_numpy()
    NIGHT[~night] = 0.0                       # dead for the whole RTH + post window
    NIGHT = NIGHT.astype(np.int8)
    P_(f"    NIGHT channel: fires on {100*(NIGHT!=0)[inw].mean():.2f} % of in-window bars, "
       f"{100*(NIGHT>0)[inw & (NIGHT!=0)].mean():.1f} % long")
    P_(f"    BMOM channel : fires on {100*(bmom!=0)[inw].mean():.2f} % of in-window bars "
       f"(for reference)")
    both = (NIGHT != 0) & (bmom != 0) & inw
    P_(f"    bars where BOTH fire: {int(both.sum()):,} "
       f"({100*both.sum()/max(inw.sum(),1):.4f} %) - disjoint by construction")

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    def keep(t):
        return [x for x in t if in_win[int(sid[i_of(x["et"])])]]

    def daily(t):
        sp = np.zeros(D["n_sess"])
        for x in t:
            sp[int(sid[i_of(x["et"])])] += x["pnl"]
        return sp[sess_in]

    def cmin(t):
        v = np.zeros(n)
        for x in t:
            a_, b_ = i_of(x["et"]), i_of(x["xt"])
            v[a_:(b_ + 1 if lb[b_] else b_)] += x["u"]
        return float(v[inw].sum())

    def pan(v, cost_wk, msk=None):
        m = np.ones(len(v), bool) if msk is None else msk
        w = pd.Series(v[m]).groupby(wk[m]).sum().to_numpy() - cost_wk
        if len(w) < 8:
            return None
        dp = dd_profile(w)
        stk = max((len(list(g)) for c_, g in itertools.groupby(w < 0) if c_), default=0)
        return dict(nwk=len(w), wkpos=100 * float((w > 0).mean()), weekly=float(w.mean()),
                    maxdd=dp["maxdd"], top5=dp["dd_mean_top5"], worst=float(w.min()),
                    streak=int(stk), weekly_dd=float(w.mean()) * DDT / max(dp["maxdd"], 1e-9),
                    se=float(w.std(ddof=1) / np.sqrt(len(w))))

    TRN = keep(sfills(D, NIGHT, halt=1300.0, target=1000.0))
    P_(f"    NIGHT traded directly: {len(TRN):,} trades, "
       f"net ${sum(x['pnl'] for x in TRN):,.0f}, "
       f"{sum(x['u'] for x in TRN)/NWk:.2f} ctrRT/wk [{_time.time()-t0:.0f}s]")
    L = [x for x in TRN if x["d"] > 0]; S = [x for x in TRN if x["d"] < 0]
    for nm, g in (("LONG", L), ("SHORT", S)):
        if not g:
            continue
        p = np.array([x["pnl"] for x in g])
        P_(f"      {nm:<6} {len(g):>5,} trades  ${p.sum():>11,.0f}  ${p.mean():>7.1f}/trade  "
           f"{100*(p>0).mean():.1f} % win")

    # ------------------------------------------------------------------ its OWN friction
    P_("")
    P_("=== ITS OWN FRICTION (W89's method - never assume the champion's cost line)")
    prof = pd.read_csv(os.path.join(W82OUT, "spread_by_minute.csv")).set_index("mod")["sp_tk"]
    F = pd.DataFrame([dict(t=pd.Timestamp(x["et"]), u=x["u"]) for x in TRN]
                     + [dict(t=pd.Timestamp(x["xt"]), u=x["u"]) for x in TRN])
    F["mod"] = F["t"].dt.hour * 60 + F["t"].dt.minute
    w_ = F.groupby("mod")["u"].sum()
    com = prof.index.intersection(w_.index)
    tk = float((prof.loc[com] * (w_.loc[com] / w_.loc[com].sum())).sum())
    C_NIGHT = tk * TICK * PV
    rtN = sum(x["u"] for x in TRN) / NWk
    P_(f"    {tk:.3f} ticks = ${C_NIGHT:.2f} per contract round turn "
       f"(BMOM $12.99 RTH-only, X9a $14.55, P1 $14.52)")
    P_(f"    {rtN:.2f} contract RT/week -> ${C_NIGHT*rtN:,.0f}/week of spread")

    # ------------------------------------------------------------------ hourly breakdown
    P_("")
    P_("=== HOURLY BREAKDOWN - if the money is 08:00-09:29 this is B-MOM's opening drive")
    hr = np.array([pd.Timestamp(x["et"]).hour for x in TRN])
    pn = np.array([x["pnl"] for x in TRN])
    P_(f"{'entry hour (ET)':<18}{'trades':>9}{'net $':>12}{'share':>9}{'$/trade':>10}")
    hrows = []
    tot = pn.sum()
    for h in sorted(set(hr)):
        m = hr == h
        P_(f"{f'{h:02d}:00':<18}{int(m.sum()):>9,}{pn[m].sum():>12,.0f}"
           f"{100*pn[m].sum()/tot if tot else 0:>8.1f}%{pn[m].mean():>10.1f}")
        hrows.append(dict(hour=int(h), trades=int(m.sum()), net=float(pn[m].sum()),
                          per_trade=float(pn[m].mean())))
    pd.DataFrame(hrows).to_csv(os.path.join(OUT, "hourly.csv"), index=False)
    pre = pn[(hr >= 8) & (hr < 10)].sum()
    P_(f"    08:00-09:59 share of net: {100*pre/tot if tot else 0:.1f} %  "
       f"-> {'THIS IS THE OPENING DRIVE, not a night engine' if tot and pre/tot > 0.5 else 'not concentrated in the pre-open'}")

    # ------------------------------------------------------------------ H1 recency
    P_("")
    P_("=== H1: the only chronology gate")
    ALL = np.ones(len(sess_in), bool)
    t24 = np.asarray(sdate >= pd.Timestamp("2024-08-01"))
    t12 = np.asarray(sdate >= pd.Timestamp("2025-08-01"))
    SER = daily(TRN)
    P_(f"{'period':<8}{'weeks':>7}{'wk $':>10}{'SE':>9}{'t':>7}{'wk+%':>8}{'maxDD':>10}")
    for lab, m in (("full", ALL), ("t24", t24), ("t12", t12)):
        a = pan(SER, C_NIGHT * rtN, m)
        P_(f"{lab:<8}{a['nwk']:>7}{a['weekly']:>10,.0f}{a['se']:>9,.0f}"
           f"{a['weekly']/max(a['se'],1e-9):>7.2f}{a['wkpos']:>7.1f}%{a['maxdd']:>10,.0f}")
    a24 = pan(SER, C_NIGHT * rtN, t24)
    h1 = a24["weekly"] > 0
    P_(f"    H1 (t24 weekly > 0): {a24['weekly']:,.0f} -> {'PASS' if h1 else 'FAIL'}")
    P_("")
    P_(f"{'per-year wk $':<16}" + "".join(f"{y:>10}" for y in sorted(set(yr))))
    line = f"{'NIGHT':<16}"
    yrows = []
    for y in sorted(set(yr)):
        a = pan(SER, C_NIGHT * rtN, yr == y)
        line += f"{a['weekly']:>10,.0f}"
        yrows.append(dict(year=int(y), weekly=a["weekly"], wkpos=a["wkpos"]))
    P_(line)
    pd.DataFrame(yrows).to_csv(os.path.join(OUT, "per_year.csv"), index=False)

    # ------------------------------------------------------------------ H2 independence
    P_("")
    P_("=== H2: WEEKLY rho against the library (daily quoted only to show the unit matters)")
    d = pd.read_csv(os.path.join(W76OUT, "streams_extended.csv"))
    cl = pd.read_csv(os.path.join(W79OUT, "members.csv"))
    VL, VS = build(D, mem, bmom, tilt, X)
    tgtN = np.where(VL & VS, 0, np.where(VL, 1, np.where(VS, -1, 0))).astype(np.int8)
    NFser = daily(keep(sfills(D, tgtN, halt=1300.0, target=1000.0)))
    LIB = {"P1": d["P1"].to_numpy(), "X9a": cl["X9a"].to_numpy(),
           "BMOM": cl["BMOM"].to_numpy(), "SHORT": d["SHORT"].to_numpy(), "NETFUSE_1": NFser}
    WN = pd.Series(SER).groupby(wk).sum()
    P_(f"{'vs':<12}{'WEEKLY rho':>12}{'daily rho':>12}{'<0.20?':>9}")
    ok2 = True
    rrows = []
    for k, v in LIB.items():
        rw = float(np.corrcoef(WN, pd.Series(v).groupby(wk).sum())[0, 1])
        rd = float(np.corrcoef(SER, v)[0, 1])
        ok2 &= abs(rw) < 0.20
        P_(f"{k:<12}{rw:>12.3f}{rd:>12.3f}{'yes' if abs(rw)<0.20 else 'NO':>9}")
        rrows.append(dict(vs=k, weekly=rw, daily=rd))
    pd.DataFrame(rrows).to_csv(os.path.join(OUT, "rho.csv"), index=False)
    P_(f"    H2 (|weekly rho| < 0.20 against ALL): {'PASS' if ok2 else 'FAIL'}")
    if ok2:
        P_("    HONEST READING, written in the spec before the read: temporal disjointness")
        P_("    produces low rho BY CONSTRUCTION. This is the SAME mechanism on a different")
        P_("    clock, not a different mechanism. It counts for portfolio arithmetic and it is")
        P_("    NOT evidence of independent information.")

    # ------------------------------------------------------------------ H3 null
    P_("")
    P_("=== H3: session-shift null (W72's, which the incumbent B-MOM channel cleared at 100th)")
    starts = np.flatnonzero(fb); bnd = list(starts) + [n]
    blocks = [(bnd[i], bnd[i + 1]) for i in range(len(bnd) - 1)]
    NB = len(blocks)
    real_pts = sum(x["pnl"] + COMM_RT * x["u"] for x in TRN) / PV / len(sess_in)
    ks = RNG.choice(np.arange(1, NB), size=min(NDRAW, NB - 1), replace=False)
    nn = []
    for j, k in enumerate(ks):
        v2 = np.zeros(n, np.int8)
        for i, (a_, b_) in enumerate(blocks):
            sa, sb = blocks[(i + int(k)) % NB]
            m = min(b_ - a_, sb - sa)
            v2[a_:a_ + m] = NIGHT[sa:sa + m]
        tr2 = keep(sfills(D, v2, halt=1300.0, target=1000.0))
        if tr2:
            nn.append(sum(x["pnl"] + COMM_RT * x["u"] for x in tr2) / PV / len(sess_in))
        if (j + 1) % 50 == 0:
            P_(f"      {j+1}/{len(ks)} [{_time.time()-t0:.0f}s]")
    nn = np.array(nn)
    pct = 100 * float((nn < real_pts).mean())
    P_(f"    real {real_pts:.3f} pts/session   null mean {nn.mean():.3f}   "
       f"p95 {np.percentile(nn,95):.3f}   percentile {pct:.1f} %")
    h3 = pct >= 95
    P_(f"    H3 (>= 95th): {'PASS' if h3 else 'FAIL'}")
    pd.DataFrame(dict(pts=nn)).to_csv(os.path.join(OUT, "null_shift.csv"), index=False)

    # ------------------------------------------------------------------ H4 portfolio
    P_("")
    P_("=== H4: does adding NIGHT to the 2:3 basket help? (inverse-vol, fixed in advance)")
    BMd, X9d = cl["BMOM"].to_numpy(), cl["X9a"].to_numpy()
    base = 2 * BMd + 3 * X9d
    cbase = 2 * C_BMOM * (sum(x["u"] for x in keep(sfills(D, np.where(
        tarr >= D["sess_end"][sid] - np.timedelta64(21 * 60, "s"), 0, bmom).astype(np.int8),
        halt=1300.0, target=1000.0))) / NWk) + 3 * C_X9A * RT_X9A
    sds = np.array([BMd.std(), X9d.std(), SER.std()])
    ivw = (1 / sds) / (1 / sds).sum()
    P_(f"    inverse-vol weights BMOM {ivw[0]:.3f} / X9a {ivw[1]:.3f} / NIGHT {ivw[2]:.3f}")
    tri = ivw[0] * BMd + ivw[1] * X9d + ivw[2] * SER
    rt_bm = sum(x["u"] for x in keep(sfills(D, np.where(
        tarr >= D["sess_end"][sid] - np.timedelta64(21 * 60, "s"), 0, bmom).astype(np.int8),
        halt=1300.0, target=1000.0))) / NWk
    ctri = ivw[0] * C_BMOM * rt_bm + ivw[1] * C_X9A * RT_X9A + ivw[2] * C_NIGHT * rtN
    pair2 = (2 * BMd + 3 * X9d) / 5.0
    cpair2 = (2 * C_BMOM * rt_bm + 3 * C_X9A * RT_X9A) / 5.0
    ds = pd.Series(sdate)
    ends = pd.date_range(ds.min() + pd.DateOffset(months=24), ds.max(), freq="ME")

    def gate(v, cv, bs, cb):
        cc = dict(m=0, w=0, dd=0, a=0, n=0)
        for e in ends:
            msk = np.asarray((ds > e - pd.DateOffset(months=24)) & (ds <= e))
            if msk.sum() < 300:
                continue
            x_ = pan(v, cv, msk); y_ = pan(bs, cb, msk)
            if x_ is None or y_ is None:
                continue
            cc["n"] += 1
            a1 = x_["weekly_dd"] > y_["weekly_dd"]; a2 = x_["wkpos"] > y_["wkpos"]
            a3 = x_["top5"] < y_["top5"]
            cc["m"] += a1; cc["w"] += a2; cc["dd"] += a3; cc["a"] += (a1 and a2 and a3)
        nn_ = max(cc["n"], 1)
        return {k: 100 * v_ / nn_ for k, v_ in cc.items() if k != "n"} | {"n": cc["n"]}
    P_("    oracle battery (precondition):")
    ok = True
    for k, v in {"pair + $200/sess": pair2 + 200.0, "pair + $500/sess": pair2 + 500.0,
                 "pair losses halved": np.where(pair2 < 0, pair2 * .5, pair2)}.items():
        g = gate(v, cpair2, pair2, cpair2)
        P_(f"      {k:<22} ALL-THREE {g['a']:>5.0f} %")
        ok &= g["a"] >= 75
    P_(f"      -> gate {'USABLE' if ok else 'BROKEN - NO VERDICT'}")
    if ok:
        g = gate(tri, ctri, pair2, cpair2)
        P_(f"    3-sleeve (inv-vol) vs the 2:3 pair, {g['n']} windows:")
        P_(f"      money {g['m']:>5.0f} %   wk+% {g['w']:>5.0f} %   top-5 DD {g['dd']:>5.0f} %"
           f"   ALL-THREE {g['a']:>5.0f} %")
        a_t = pan(tri, ctri); a_p = pan(pair2, cpair2)
        P_("")
        P_(f"{'':<20}{'wk $':>9}{'wk+%':>8}{'maxDD':>10}{'top5DD':>9}{'worst':>10}"
           f"{'wk$@fixDD':>11}")
        for nmx, a in (("2:3 pair (1 unit)", a_p), ("+ NIGHT (inv-vol)", a_t)):
            P_(f"{nmx:<20}{a['weekly']:>9,.0f}{a['wkpos']:>7.1f}%{a['maxdd']:>10,.0f}"
               f"{a['top5']:>9,.0f}{a['worst']:>10,.0f}{a['weekly_dd']:>11,.0f}")
        nl = sum([a_t["weekly_dd"] > a_p["weekly_dd"], a_t["wkpos"] > a_p["wkpos"],
                  a_t["top5"] < a_p["top5"]])
        P_(f"    H4 (>= 2 of 3 full-window legs): {nl}/3 "
           f"{'PASS' if nl >= 2 else 'FAIL'}   [gate ALL-THREE {g['a']:.0f} %]")
        pd.DataFrame([dict(obj="pair", **a_p), dict(obj="pair+NIGHT", **a_t)]).to_csv(
            os.path.join(OUT, "portfolio.csv"), index=False)
    pd.DataFrame({"date": sdate.strftime("%Y-%m-%d"), "NIGHT": SER}).to_csv(
        os.path.join(OUT, "night_daily.csv"), index=False)
    P_(f"\n[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
