"""WE_W102c - ADVERSARIAL CHECKS ON `XM_CONFLICT` BEFORE IT IS REPORTED AS A FRONTIER CHANGE.

Directive V4 section 16: run an adversarial audit when a result materially changes the frontier or
a candidate is about to become live-ready. This qualifies on both. Four attacks, each able to kill
it:

  A. ANCHOR. This repo's bars are END-STAMPED and `we_channels` treats 09:31 as the RTH open bar.
     W101/W102 anchored the drive at the bar stamped 09:30, whose OPEN is the 09:29 price - one
     minute EARLY, inside the pre-open. Not a lookahead, but a mislabel. Does the result survive
     the true RTH anchor?
  B. THE OBVIOUS CONFOUND. When ES/RTY/YM disagree with NQ, NQ's own drive is probably SMALL.
     XM_CONFLICT may simply be selecting small-drive sessions. Null: subsamples matched on |drive|
     decile, not merely on count.
  C. COMPOSITE FRAGILITY. Does it need all three markets and that exact z-average, or does any
     reasonable construction work? If only one arrangement works it is a fit, not a mechanism.
  D. LATENCY. The fill is the 09:46 bar's OPEN, which under end-stamping is the price AT 09:45 -
     the campaign's standard next-bar convention, but a ZERO-latency assumption. What does a
     realistic delay cost?
"""
from __future__ import annotations

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
from run_we_w51 import session_frames                                    # noqa: E402
from we_lab import spread_profile                                        # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W102_XMENGINE", "out")
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
TICKV = 5.0
EXITM = 945
NSUB = 2000
SEED = 1022
XM = {"ES": "runs/SM1M_ES_SUBSTRATE/out/es_1m_2022_2026.parquet",
      "RTY": "runs/SM1M_RTY_SUBSTRATE/out/rty_1m_2022_2026.parquet",
      "YM": "runs/SM1M_YM_SUBSTRATE/out/ym_1m_2022_2026.parquet"}


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "adversarial.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    prof = spread_profile()
    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr, sid = D["n"], D["t"], D["sid"]
    o, c = D["o"], D["c"]
    st_, en_, _ = session_frames(D)
    mod = ((tarr - tarr.astype("datetime64[D]")).astype("timedelta64[s]")
           .astype(np.int64) // 60).astype(np.int32)
    NSESS = D["n_sess"]
    win = np.array([A <= tarr[st_[s]] < B for s in range(NSESS)])
    nq = pd.DataFrame({"time": pd.to_datetime(tarr), "nq": c}).set_index("time")
    XD = {}
    for k, path in XM.items():
        d_ = pd.read_parquet(os.path.join(ROOT, path), columns=["time", "close"])
        d_["time"] = pd.to_datetime(d_["time"])
        XD[k] = nq.join(d_.set_index("time")["close"].rename(k), how="left")[k].to_numpy()

    def at(mv, arr, use_open=False):
        r = np.full(NSESS, np.nan)
        m_ = mod == mv
        r[sid[m_]] = (o[m_] if use_open else arr[m_])
        return r
    P_("=" * 118)
    P_("=== A. THE ANCHOR. Bars are END-STAMPED; we_channels treats 09:31 as the RTH open bar,")
    P_("===    so the bar stamped 09:30 opens at the 09:29 price - one minute inside the pre-open.")
    P_("=" * 118)

    def build(anchor_mod, dec_mod, ent_mod, mk_xm, delay=0):
        p_a = at(anchor_mod, o, use_open=True)
        p_d = at(dec_mod, c)
        p_e = at(ent_mod + delay, o, use_open=True)
        p_x = at(EXITM, c)
        drive = np.sign(p_d - p_a)
        xs = mk_xm(anchor_mod, dec_mod)
        okm = (win & np.isfinite(p_a) & np.isfinite(p_d) & np.isfinite(p_e) &
               np.isfinite(p_x) & np.isfinite(xs) & (drive != 0) & (xs != 0))
        conflict = okm & (xs != drive)
        cst = COMM_RT + TICKV * (float(prof.loc[ent_mod + delay]) +
                                 float(prof.loc[EXITM])) / 2.0
        pnl = drive * (p_x - p_e) * PV - cst
        return drive, okm, conflict, pnl, np.abs(p_d - p_a)

    def xm3(anchor_mod, dec_mod):
        acc = np.zeros(NSESS); cnt = np.zeros(NSESS)
        for k in XM:
            a_ = at(anchor_mod, XD[k]); b_ = at(dec_mod, XD[k])
            r_ = np.log(b_ / a_)
            s_ = pd.Series(r_).rolling(60, min_periods=20).std().shift(1).to_numpy()
            z = r_ / np.maximum(s_, 1e-12)
            g = np.isfinite(z)
            acc[g] += z[g]; cnt[g] += 1
        return np.sign(np.where(cnt > 0, acc / np.maximum(cnt, 1), np.nan))

    def summ(tag, drive, okm, conflict, pnl):
        m = conflict
        return dict(tag=tag, n=int(m.sum()), share=100 * m.sum() / max(okm.sum(), 1),
                    per_trade=float(pnl[m].mean()), hit=100 * float((pnl[m] + 0 > 0).mean()),
                    net=float(pnl[m].sum()))
    P_(f"{'anchor':<28}{'n':>6}{'share':>8}{'$/trade':>10}{'hit%':>8}{'net $':>11}")
    rows = []
    for tag, am, dm, em in (("09:30 bar (=09:29 px) W101", 570, 585, 586),
                            ("09:31 bar (=TRUE RTH open)", 571, 585, 586),
                            ("09:31 anchor, decide 09:46", 571, 586, 587)):
        dr, okm, cf, pn, adr = build(am, dm, em, xm3)
        s_ = summ(tag, dr, okm, cf, pn)
        rows.append(s_)
        P_(f"{tag:<28}{s_['n']:>6}{s_['share']:>7.1f}%{s_['per_trade']:>10,.0f}"
           f"{s_['hit']:>7.1f}%{s_['net']:>11,.0f}")
    P_("")
    P_("    A one-minute anchor shift is a labelling question, not a tuning knob. If the result")
    P_("    only survives at one of these it is an artifact of the anchor.")

    # ---------------------------------------------------------------- B. the confound
    P_("")
    P_("=" * 118)
    P_("=== B. THE OBVIOUS CONFOUND: is XM_CONFLICT just SMALL-DRIVE sessions?")
    P_("=" * 118)
    dr, okm, cf, pn, adr = build(570, 585, 586, xm3)
    conf = okm & ~cf
    P_(f"    |drive| on CONFLICT sessions  mean {adr[cf].mean():.2f} pts   "
       f"median {np.median(adr[cf]):.2f}")
    P_(f"    |drive| on CONFIRM  sessions  mean {adr[conf].mean():.2f} pts   "
       f"median {np.median(adr[conf]):.2f}")
    _verdict = ("CONFLICT sessions ARE smaller-drive; the confound is real and is matched below"
                if adr[cf].mean() < adr[conf].mean() else "NOT smaller-drive")
    P_(f"    ratio {adr[cf].mean()/adr[conf].mean():.3f}  -> {_verdict}")
    idx = np.flatnonzero(okm)
    dec = pd.qcut(pd.Series(adr[idx]), 10, labels=False, duplicates="drop").to_numpy()
    want = pd.Series(dec[np.isin(idx, np.flatnonzero(cf))]).value_counts().sort_index()
    rng = np.random.default_rng(SEED)
    pool = {d_: idx[dec == d_] for d_ in np.unique(dec)}
    nullv = np.empty(NSUB)
    for b_ in range(NSUB):
        pick = np.concatenate([rng.choice(pool[d_], size=min(k_, len(pool[d_])), replace=False)
                               for d_, k_ in want.items()])
        nullv[b_] = pn[pick].mean()
    real = float(pn[cf].mean())
    P_("")
    P_("    |drive|-DECILE-MATCHED subsample null - same count in each of 10 |drive| deciles:")
    P_(f"    real ${real:,.0f}/trade   null mean ${nullv.mean():,.0f} sd ${nullv.std(ddof=1):,.0f}"
       f"   p95 ${np.percentile(nullv,95):,.0f}   -> "
       f"{100*float((nullv < real).mean()):.1f}th percentile of {NSUB}")

    # ---------------------------------------------------------------- C. composite fragility
    P_("")
    P_("=" * 118)
    P_("=== C. COMPOSITE FRAGILITY. Does it need all three markets and that exact z-average?")
    P_("=" * 118)

    def mk_one(kk):
        def f(am, dm):
            a_ = at(am, XD[kk]); b_ = at(dm, XD[kk])
            return np.sign(np.log(b_ / a_))
        return f

    def mk_vote(am_, dm_):
        sgn = np.zeros(NSESS)
        for k in XM:
            a_ = at(am_, XD[k]); b_ = at(dm_, XD[k])
            sgn = sgn + np.nan_to_num(np.sign(np.log(b_ / a_)))
        return np.sign(sgn)

    def mk_raw(am_, dm_):
        acc = np.zeros(NSESS); cnt = np.zeros(NSESS)
        for k in XM:
            a_ = at(am_, XD[k]); b_ = at(dm_, XD[k])
            r_ = np.log(b_ / a_)
            g = np.isfinite(r_)
            acc[g] += r_[g]; cnt[g] += 1
        return np.sign(np.where(cnt > 0, acc / np.maximum(cnt, 1), np.nan))
    P_(f"{'composite':<30}{'n':>6}{'share':>8}{'$/trade':>10}{'hit%':>8}{'net $':>11}")
    crows = []
    for tag, f in (("ES/RTY/YM z-average (W101)", xm3),
                   ("ES/RTY/YM raw-return average", mk_raw),
                   ("ES/RTY/YM 2-of-3 sign vote", mk_vote),
                   ("ES alone", mk_one("ES")),
                   ("RTY alone", mk_one("RTY")),
                   ("YM alone", mk_one("YM"))):
        dr2, ok2, cf2, pn2, _ = build(570, 585, 586, f)
        s_ = summ(tag, dr2, ok2, cf2, pn2)
        crows.append(s_)
        P_(f"{tag:<30}{s_['n']:>6}{s_['share']:>7.1f}%{s_['per_trade']:>10,.0f}"
           f"{s_['hit']:>7.1f}%{s_['net']:>11,.0f}")
    pd.DataFrame(crows).to_csv(os.path.join(OUT, "composite_variants.csv"), index=False)

    # ---------------------------------------------------------------- D. latency
    P_("")
    P_("=" * 118)
    P_("=== D. LATENCY. The fill is the 09:46 bar's OPEN = the price AT 09:45 under end-stamping.")
    P_("===    That is the campaign's standard next-bar convention and a ZERO-latency assumption.")
    P_("=" * 118)
    P_(f"{'fill delay':<16}{'n':>6}{'$/trade':>10}{'hit%':>8}{'net $':>11}{'vs 0 min':>11}")
    base = None
    lrows = []
    for dly in (0, 1, 2, 5, 10, 15):
        dr3, ok3, cf3, pn3, _ = build(570, 585, 586, xm3, delay=dly)
        v = float(pn3[cf3].mean())
        if base is None:
            base = v
        P_(f"{'+'+str(dly)+' min':<16}{int(cf3.sum()):>6}{v:>10,.0f}"
           f"{100*float((pn3[cf3]>0).mean()):>7.1f}%{float(pn3[cf3].sum()):>11,.0f}"
           f"{100*(v/base-1):>10.1f}%")
        lrows.append(dict(delay=dly, per_trade=v, n=int(cf3.sum())))
    pd.DataFrame(lrows).to_csv(os.path.join(OUT, "latency.csv"), index=False)
    P_(f"\n[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
