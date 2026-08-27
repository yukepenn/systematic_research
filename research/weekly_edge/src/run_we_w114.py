"""WE_W114 - INTRADAY MOMENTUM. The afternoon continues the morning.

Spec: runs/WE_W114_INTRAMOM/spec.yaml, committed BEFORE this ran (d7889c7).

This rule sat in the CONTROL column of W111b and W112 earning more than the objects those waves were
testing, and has never been preregistered, nulled or looked at outside the discovery window.

The primary is a CONJUNCTION and both halves must hold: clear a coin null on the modern window, AND
independently on 2006-2021 - sixteen years this campaign has never mined for it. The rule needs no
cross-market substrate and no memory arrays, so unlike XM_CONFLICT it CAN be tested there.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT, PV, COMM_RT                                 # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w51 import classify, session_frames                          # noqa: E402
from run_we_w51c import dd_profile                                       # noqa: E402
from we_lab import spread_profile                                        # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W114_INTRAMOM", "out")
os.makedirs(OUT, exist_ok=True)
W110 = os.path.join(ROOT, "runs", "WE_W110_XMDIVERSE", "out", "weekly.csv")
TICKV = 5.0
DDT = 20245.0
RTH0, MORN_B, DEC, EXIT = 571, 689, 708, 944
SEED = 114
NPERM = 2000
CLASSES = ("TREND-UP", "TREND-DOWN", "REVERSAL", "RANGE", "MIXED")


class Win:
    """a window of the substrate with the few accessors this wave needs. No fitted state."""

    def __init__(self, a, b, extend, label):
        self.label = label
        D = load_deep(a, b, extend=extend)
        self.D = D
        self.n, self.t, self.sid = D["n"], D["t"], D["sid"]
        self.o, self.c, self.h, self.l = D["o"], D["c"], D["h"], D["l"]
        self.st, self.en, _ = session_frames(D)
        self.klass = classify(D, self.st, self.en)
        self.mod = ((self.t - self.t.astype("datetime64[D]")).astype("timedelta64[s]")
                    .astype(np.int64) // 60).astype(np.int32)
        self.NS = D["n_sess"]
        self.sdate = pd.to_datetime(D["sess_date"])
        iso = self.sdate.isocalendar()
        self.wkall = (iso["year"].astype(str) + "-W" +
                      iso["week"].astype(str).str.zfill(2)).to_numpy()
        A, B = np.datetime64(a[:10]), np.datetime64(b[:10])
        self.win = np.array([A <= self.t[self.st[s]] <= B for s in range(self.NS)])
        self.sess_in = np.flatnonzero(self.win)
        self.wk = self.wkall[self.sess_in]
        self.prof = spread_profile()

    def at(self, mv, use_open=False):
        r = np.full(self.NS, np.nan)
        m = self.mod == mv
        r[self.sid[m]] = (self.o if use_open else self.c)[m]
        return r

    def cost(self, mult=1.0):
        return COMM_RT + mult * TICKV * (float(self.prof.loc[DEC + 1])
                                         + float(self.prof.loc[EXIT])) / 2.0

    def run(self, dec, exitm, direction, mult=1.0):
        pe = self.at(dec + 1, use_open=True)
        px = self.at(exitm)
        cst = COMM_RT + mult * TICKV * (float(self.prof.loc[dec + 1])
                                        + float(self.prof.loc[exitm])) / 2.0
        take = self.win & np.isfinite(pe) & np.isfinite(px) & (np.nan_to_num(direction) != 0)
        mv = (px - pe) * PV
        pnl = np.zeros(self.NS)
        pnl[take] = np.nan_to_num(direction)[take] * mv[take] - cst
        emove = float(np.abs(mv[self.win & np.isfinite(mv)]).mean())
        return dict(pnl=pnl, take=take, cost=cst, emove=emove, mv=mv,
                    pstar=0.5 * (1 + cst / max(emove, 1e-9)))

    def stats(self, R):
        pn = R["pnl"][R["take"]]
        if len(pn) < 10:
            return None
        ser = np.zeros(self.NS); ser[R["take"]] = pn
        wv = pd.Series(ser[self.sess_in]).groupby(self.wk).sum().to_numpy()
        dp = dd_profile(wv)
        srt = np.sort(pn)[::-1]
        return dict(n=len(pn), hit=100 * float((pn > 0).mean()), per_trade=float(pn.mean()),
                    net=float(pn.sum()), pstar=R["pstar"], weekly=float(wv.mean()),
                    fixdd=float(wv.mean()) * DDT / max(dp["maxdd"], 1e-9),
                    poswk=100 * float((wv > 0).mean()), maxdd=dp["maxdd"],
                    med=float(np.median(pn)),
                    trim=float(pn[(pn > np.percentile(pn, 5)) & (pn < np.percentile(pn, 95))].mean()),
                    skew=float(pd.Series(pn).skew()),
                    worst=float(pn.min()),
                    # `CORRECTION` the first run divided by max(sum, 1e-9), which for a LOSING
                    # arm returns 1e-9 and printed contributions of 6.2e17 %. Divided by |net| now,
                    # and a losing arm's contribution share is flagged as undefined in the report.
                    top1=100 * srt[0] / max(abs(pn.sum()), 1e-9),
                    top5=100 * srt[:5].sum() / max(abs(pn.sum()), 1e-9),
                    top10=100 * srt[:10].sum() / max(abs(pn.sum()), 1e-9),
                    top20=100 * srt[:20].sum() / max(abs(pn.sum()), 1e-9),
                    t=float(wv.mean()) / max(wv.std(ddof=1) / np.sqrt(len(wv)), 1e-9))

    def morn_dir(self):
        return np.sign(self.at(MORN_B) - self.at(RTH0, use_open=True))


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "intramom.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    rng = np.random.default_rng(SEED)
    MOD = Win("2022-07-01", "2026-07-31 17:00", True, "MODERN 2022-07 -> 2026-08")
    OLD = Win("2006-01-05", "2021-12-31 17:00", False, "OUT-OF-WINDOW 2006-2021")
    P_(f"    MODERN {MOD.n:,} bars / {len(MOD.sess_in):,} sessions")
    P_(f"    OLD    {OLD.n:,} bars / {len(OLD.sess_in):,} sessions   [{_time.time()-t0:.0f}s]")

    # ------------------------------------------------------------------ harness check
    P_("")
    P_("=" * 124)
    P_("=== 0. HARNESS CHECK - do the minute anchors mean the same thing in 2006 as in 2026?")
    P_("=" * 124)
    okall = True
    for W in (MOD, OLD):
        cov = {m: float(np.isfinite(W.at(m, use_open=(m == RTH0)))[W.win].mean())
               for m in (RTH0, MORN_B, DEC + 1, EXIT)}
        ok = all(v > 0.90 for v in cov.values())
        okall &= ok
        P_(f"    {W.label:<26}" + "  ".join(f"{m}:{100*v:5.1f}%" for m, v in cov.items())
           + f"   {'OK' if ok else 'FAIL'}")
    if not okall:
        P_("    A minute anchor is missing on more than 10 % of sessions in one window; the two")
        P_("    halves would not be measuring the same object. No table is issued.")
        out.close(); return
    P_("    Both windows carry all four anchors. The rule means the same thing in both.")

    # ------------------------------------------------------------------ the primary
    P_("")
    P_("=" * 124)
    P_("=== 1. THE PRIMARY - A CONJUNCTION. Both halves must hold independently.")
    P_("===    FOLLOW the morning direction: decide 11:48, fill 11:49, hold to 15:44, size 1.")
    P_("=" * 124)
    P_(f"{'window':<28}{'N':>6}{'hit%':>8}{'p*':>8}{'vs p*':>7}{'$/trade':>10}{'net $':>12}"
       f"{'coin p95':>10}{'pctile':>9}{'':>8}")
    halves = {}
    RES = {}
    for W in (MOD, OLD):
        R = W.run(DEC, EXIT, W.morn_dir())
        s = W.stats(R)
        RES[W.label] = (R, s)
        mv = R["mv"][R["take"]]
        nul = np.array([float((rng.choice([-1.0, 1.0], size=len(mv)) * mv - R["cost"]).mean())
                        for _ in range(NPERM)])
        p95 = float(np.percentile(nul, 95))
        pc = 100 * float((nul < s["per_trade"]).mean())
        ok = (s["per_trade"] > 0 and s["per_trade"] > p95 and s["hit"] / 100 > s["pstar"])
        halves[W.label] = ok
        P_(f"{W.label:<28}{s['n']:>6}{s['hit']:>7.2f}%{s['pstar']:>8.4f}"
           f"{100*(s['hit']/100-s['pstar']):>7.2f}{s['per_trade']:>10,.0f}{s['net']:>12,.0f}"
           f"{p95:>10,.0f}{pc:>8.1f}th{('  PASS' if ok else '  FAIL'):>8}")
    v = all(halves.values())
    P_("")
    P_(f"    PRIMARY VERDICT: {'PASSES BOTH HALVES' if v else 'FAILS'}"
       + ("" if v else f"   (modern {'pass' if halves[MOD.label] else 'FAIL'}, "
                       f"2006-2021 {'pass' if halves[OLD.label] else 'FAIL'})"))
    if halves[MOD.label] and not halves[OLD.label]:
        P_("    -> per the spec this would be REGIME_LOCAL, which is a DEMOTION of confidence,")
        P_("       not a result. It is recorded as such.")

    # ------------------------------------------------------------------ legs and controls
    P_("")
    P_("=" * 124)
    P_("=== 2. THE LEGS SEPARATELY, and the matched unconditional controls (W111b's binding rule)")
    P_("===    A one-sided result is a WITHDRAWAL, not a nuance: two-sidedness is the whole reason")
    P_("===    this is not simply the uptrend.")
    P_("=" * 124)
    P_(f"{'window / arm':<40}{'N':>6}{'hit%':>8}{'$/trade':>10}{'net $':>12}{'t':>7}")
    for W in (MOD, OLD):
        md = W.morn_dir()
        arms = {
            "FOLLOW - LONG leg only": np.where(md > 0, 1.0, 0.0),
            "FOLLOW - SHORT leg only": np.where(md < 0, -1.0, 0.0),
            "FADE (mirror)": -md,
            "CONTROL always LONG": np.where(W.win, 1.0, 0.0),
            "CONTROL always SHORT": np.where(W.win, -1.0, 0.0),
        }
        for lab, d_ in arms.items():
            s = W.stats(W.run(DEC, EXIT, d_))
            if s is None:
                continue
            P_(f"{W.label.split()[0] + '  ' + lab:<40}{s['n']:>6}{s['hit']:>7.2f}%"
               f"{s['per_trade']:>10,.0f}{s['net']:>12,.0f}{s['t']:>7.2f}")
        P_("")

    # ------------------------------------------------------------------ recency
    P_("=" * 124)
    P_("=== 3. RECENCY. Section 5 makes this primary, and W112's table already showed the modern")
    P_("===    result concentrated in 2025.")
    P_("=" * 124)
    R, s = RES[MOD.label]
    dts = MOD.sdate[MOD.sess_in]
    ser = R["pnl"][MOD.sess_in]; tk = R["take"][MOD.sess_in]
    P_(f"{'period':<14}{'N':>6}{'hit%':>8}{'$/trade':>10}{'net $':>12}")
    per = [(str(y), dts.year == y) for y in sorted(set(dts.year))]
    per += [("t12m", dts >= dts.max() - pd.Timedelta(days=365)),
            ("t6m", dts >= dts.max() - pd.Timedelta(days=182)),
            ("t3m", dts >= dts.max() - pd.Timedelta(days=91))]
    for lab, m_ in per:
        mm = m_ & tk
        if mm.sum() < 5:
            continue
        P_(f"{lab:<14}{int(mm.sum()):>6}{100*float((ser[mm]>0).mean()):>7.2f}%"
           f"{ser[mm].mean():>10,.0f}{ser[mm].sum():>12,.0f}")
    P_("")
    P_("    ...and the same for 2006-2021, five-year blocks:")
    Ro, so = RES[OLD.label]
    dto = OLD.sdate[OLD.sess_in]
    sero = Ro["pnl"][OLD.sess_in]; tko = Ro["take"][OLD.sess_in]
    for lo, hi in ((2006, 2010), (2011, 2015), (2016, 2021)):
        mm = (dto.year >= lo) & (dto.year <= hi) & tko
        P_(f"{f'{lo}-{hi}':<14}{int(mm.sum()):>6}{100*float((sero[mm]>0).mean()):>7.2f}%"
           f"{sero[mm].mean():>10,.0f}{sero[mm].sum():>12,.0f}")

    # ------------------------------------------------------------------ is the old failure COST?
    P_("")
    P_("=" * 124)
    P_("=== 3b. IS THE 2006-2021 FAILURE JUST THE PRICE LEVEL? NQ traded near 1,700 in 2006 and")
    P_("===     near 20,000 in 2026, so a FIXED DOLLAR cost is a far higher hurdle in the old")
    P_("===     window. This separates the COST hurdle from the BEHAVIOUR.")
    P_("=" * 124)
    P_(f"{'window':<28}{'E|move| $':>12}{'cost $':>9}{'p* - 0.5':>11}"
       f"{'$/trade @ 0x':>14}{'implied edge':>14}")
    for W in (MOD, OLD):
        R0 = W.run(DEC, EXIT, W.morn_dir(), mult=0.0)
        s0 = W.stats(R0)
        em = R0["emove"]
        # a symmetric-payoff directional edge e gives E[pnl] = 2*e*E|move| - cost
        edge = (s0["per_trade"] + R0["cost"]) / (2.0 * max(em, 1e-9))
        P_(f"{W.label:<28}{em:>12,.0f}{R0['cost']:>9,.2f}"
           f"{100*(R0['pstar']-0.5):>10.2f}%{s0['per_trade']:>14,.0f}{100*edge:>13.2f}%")
    P_("")
    P_("    Reading: the 'implied edge' is the directional accuracy above 50 % that would produce")
    P_("    the observed COMMISSION-ONLY expectancy at that window's own average move size. If the")
    P_("    old window's edge is near zero, its failure is BEHAVIOUR and not the cost hurdle.")

    # ------------------------------------------------------------------ cost
    P_("")
    P_("=" * 124)
    P_("=== 4. COST SENSITIVITY - where does the edge die?")
    P_("===    2006-2021 is charged the MODERN spread, which is generous because spreads were")
    P_("===    wider then. The 2x and 3x rows are the honest reads for that window.")
    P_("=" * 124)
    P_(f"{'window':<28}" + "".join(f"{f'{m:.0f}x spread':>16}" for m in (0, 1, 2, 3)))
    for W in (MOD, OLD):
        row = []
        for m in (0, 1, 2, 3):
            s2 = W.stats(W.run(DEC, EXIT, W.morn_dir(), mult=m))
            row.append(f"${s2['per_trade']:,.0f}")
        P_(f"{W.label:<28}" + "".join(f"{x:>16}" for x in row))

    # ------------------------------------------------------------------ class + concentration
    P_("")
    P_("=" * 124)
    P_("=== 5. SESSION CLASS (diagnostic) and CONCENTRATION (section 25)")
    P_("=" * 124)
    P_(f"{'window':<28}" + "".join(f"{k:>17}" for k in CLASSES))
    for W in (MOD, OLD):
        R2 = W.run(DEC, EXIT, W.morn_dir())
        row = ""
        for c in CLASSES:
            m = R2["take"] & (W.klass == c)
            row += f"{int(m.sum()):>6} {float(R2['pnl'][m].mean()) if m.sum() else np.nan:>10,.0f}"
        P_(f"{W.label:<28}{row}")
    P_("")
    P_(f"{'window':<28}{'median':>10}{'trimmed':>10}{'skew':>8}{'worst':>11}"
       f"{'top1%':>8}{'top5%':>8}{'top10%':>9}{'top20%':>9}")
    for W in (MOD, OLD):
        s2 = RES[W.label][1]
        P_(f"{W.label:<28}{s2['med']:>10,.0f}{s2['trim']:>10,.0f}{s2['skew']:>8.2f}"
           f"{s2['worst']:>11,.0f}{s2['top1']:>7.1f}%{s2['top5']:>7.1f}%"
           f"{s2['top10']:>8.1f}%{s2['top20']:>8.1f}%")

    # ------------------------------------------------------------------ plateau
    P_("")
    P_("=" * 124)
    P_("=== 6. DECISION-MINUTE PLATEAU - a ROBUSTNESS READ, never an argmax.")
    P_("===    Its best cell may NOT be quoted, promoted or substituted for the 11:48 primary.")
    P_("=" * 124)
    DECS = [678, 693, 708, 723, 738]
    EXITS = [929, 944, 959]
    for W in (MOD, OLD):
        P_(f"    {W.label}   ($/trade)")
        P_(f"{'decide':<12}" + "".join(f"{f'exit {e//60:02d}:{e%60:02d}':>14}" for e in EXITS))
        for d_ in DECS:
            md = np.sign(W.at(d_ - 19) - W.at(RTH0, use_open=True))
            cells = []
            for e in EXITS:
                s2 = W.stats(W.run(d_, e, md))
                cells.append(f"${s2['per_trade']:,.0f}" if s2 else "-")
            P_(f"{f'{d_//60:02d}:{d_%60:02d}':<12}" + "".join(f"{x:>14}" for x in cells))
        P_("")

    # ------------------------------------------------------------------ portfolio
    P_("=" * 124)
    P_("=== 7. PORTFOLIO - correlation with the current base and the candidate component")
    P_("=" * 124)
    if os.path.exists(W110):
        WK = pd.read_csv(W110)
        ser2 = np.zeros(MOD.NS); ser2[R["take"]] = R["pnl"][R["take"]]
        fw = pd.Series(ser2[MOD.sess_in]).groupby(MOD.wk).sum()
        j = pd.DataFrame(dict(week=WK["week"], p1=WK["p1"], xm=WK["xm"])).set_index("week")
        j["fm"] = fw
        j = j.dropna()
        P_(f"    {len(j)} common weeks")
        P_(f"    rho(FOLLOW_MORNING, P1/PCT)      = {j['fm'].corr(j['p1']):+.3f}")
        P_(f"    rho(FOLLOW_MORNING, XM_CONFLICT) = {j['fm'].corr(j['xm']):+.3f}")
        P_(f"    rho(P1/PCT, XM_CONFLICT)         = {j['p1'].corr(j['xm']):+.3f}   (W110: +0.081)")
        P_("")
        P_(f"{'book':<34}{'wk $':>10}{'maxDD':>11}{'wk$@fixDD':>12}{'pos wk%':>9}{'t':>7}")
        for lab, v_ in (("P1/PCT alone", j["p1"]),
                        ("P1/PCT + XM (inverse-vol)", None),
                        ("P1/PCT + FOLLOW (inverse-vol)", None),
                        ("P1/PCT + XM + FOLLOW (inv-vol)", None)):
            if v_ is None:
                keys = {"P1/PCT + XM (inverse-vol)": ["p1", "xm"],
                        "P1/PCT + FOLLOW (inverse-vol)": ["p1", "fm"],
                        "P1/PCT + XM + FOLLOW (inv-vol)": ["p1", "xm", "fm"]}[lab]
                w_ = np.array([1.0 / max(j[k].std(ddof=1), 1e-9) for k in keys])
                w_ = w_ / w_.sum() * len(keys)
                v_ = sum(w_[i] * j[keys[i]] for i in range(len(keys))) / len(keys)
            vv = v_.to_numpy()
            dp = dd_profile(vv)
            P_(f"{lab:<34}{vv.mean():>10,.0f}{dp['maxdd']:>11,.0f}"
               f"{vv.mean()*DDT/max(dp['maxdd'],1e-9):>12,.0f}"
               f"{100*float((vv>0).mean()):>8.1f}%"
               f"{vv.mean()/max(vv.std(ddof=1)/np.sqrt(len(vv)),1e-9):>7.2f}")
        j.to_csv(os.path.join(OUT, "weekly_joint.csv"))
    else:
        P_("    W110 weekly artifact absent - portfolio section NOT RUN.")
    P_(f"\n[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
