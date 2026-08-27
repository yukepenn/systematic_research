"""WE_W111 - VOL-EXHAUST / ABSORB. The #1 row of the coverage matrix, third attempt.

Spec: runs/WE_W111_VOLDECAY/spec.yaml, committed BEFORE this ran (f01b5fe).

The two prior failures were MINE, not the market's. W100's gates accepted ~92 % of the target leg
and could not separate anything; W106's VOL_DECAY fired on 3 of 1,058 sessions and could not be
measured at all. Both were SPECIFICATION failures. Every mechanism here is CONTINUOUS so the rate
calibrator can bind, and a preregistered SPECIFICATION GATE reports anything defined on under 15 %
of sessions as UNTESTED rather than folding a meaningless zero into a primary.

Geometry is deliberately identical to W108 so these land in the same session-class table.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT, PV                                          # noqa: E402
from we_lanes import LaneBench, RATES                                    # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W111_VOLDECAY", "out")
os.makedirs(OUT, exist_ok=True)
RTH0 = 571                      # 09:31, the true RTH open under end-stamping
PRIMARY = (708, 944)            # decide 11:48, fill 11:49, hold to 15:44   == W108
SECONDARY = (601, 689)          # decide 10:01, fill 10:02, hold to 11:29   == W106
GATE = 0.15                     # spec: a direction defined on < 15 % of sessions is UNTESTED
SEED = 111
CLASSES = ("TREND-UP", "TREND-DOWN", "REVERSAL", "RANGE", "MIXED")


def build_vol(L, dec, minbars):
    """Five participation mechanisms, all computed from bars stamped at or before `dec`.

    `CORRECTION` the first run hardcoded minbars=40, which is fine for the 138-bar PRIMARY window
    but is LONGER THAN THE ENTIRE 31-bar SECONDARY window, so it silently voided four of the five
    secondary cells - they were reported as UNTESTED when in fact they had never been given a
    chance to compute. Same family of defect as W104's ON_ASIA cell. The guard is now sized to its
    window. The PRIMARY is bit-identical either way: no session has 25-39 bars in 09:31-11:48.
    """
    NS = L.NS
    o0 = L.at(RTH0, use_open=True)
    cD = L.at(dec)
    prev = np.sign(cD - o0)                       # the prevailing move at the decision bar
    absm = L.agg(RTH0, dec, "absmove")
    tot = L.agg(RTH0, dec, "vol")
    peff = np.abs(cD - o0) / np.maximum(absm, 1e-9)
    medv = pd.Series(tot).rolling(250, min_periods=60).median().shift(1).to_numpy()

    m = (L.mod >= RTH0) & (L.mod <= dec)
    ii = np.flatnonzero(m)
    df = pd.DataFrame(dict(s=L.sid[ii], mod=L.mod[ii], v=L.v[ii], o=L.o[ii],
                           c=L.c[ii], h=L.h[ii], l=L.l[ii]))
    v1 = np.full(NS, np.nan); v2 = np.full(NS, np.nan)
    v4 = np.full(NS, np.nan); d4 = np.zeros(NS)
    v5 = np.full(NS, np.nan); d5 = np.zeros(NS)
    for s, g in df.groupby("s", sort=False):
        if s >= NS or len(g) < minbars:
            continue
        g = g.sort_values("mod")
        v_ = g["v"].to_numpy(); o_ = g["o"].to_numpy(); c_ = g["c"].to_numpy()
        h_ = g["h"].to_numpy(); l_ = g["l"].to_numpy()
        md = float(np.median(v_)) or 1.0

        # V1 - Spearman(bar index, volume) over the last 20 bars, NEGATED so HIGH = decay
        w = v_[-20:]
        if len(w) == 20 and len(np.unique(w)) > 1:
            rk = pd.Series(w).rank().to_numpy()
            v1[s] = -float(np.corrcoef(np.arange(20.0), rk)[0, 1])

        # V2 - last 10 bars' mean volume vs the 20 before them, INVERTED so HIGH = drain
        if len(v_) >= 30:
            rec = float(np.mean(v_[-10:])); pri = float(np.mean(v_[-30:-10]))
            if rec > 0:
                v2[s] = pri / rec

        # V4 - the highest-volume bar is NOT the biggest body and closes near its own middle
        j = int(np.argmax(v_))
        body = np.abs(c_ - o_)
        brank = float((body < body[j]).mean())            # 1.0 would mean it IS the biggest body
        rr = h_[j] - l_[j]
        loc = 0.5 if rr <= 0 else float((c_[j] - l_[j]) / rr)
        v4[s] = (v_[j] / md) * (1.0 - brank) * (1.0 - 2.0 * abs(loc - 0.5))
        d4[s] = -np.sign(c_[j] - o_[j]) if c_[j] != o_[j] else -prev[s]

        # V5 - the session extreme was made on a participation spike that has since drained
        up = (h_.max() - o_[0]) >= (o_[0] - l_.min())
        k = int(np.argmax(h_)) if up else int(np.argmin(l_))
        after = v_[k + 1:k + 11]
        if len(after) >= 3:
            v5[s] = (v_[k] / md) / max(float(np.mean(after)) / md, 1e-9)
        d5[s] = -1.0 if up else 1.0

    v3 = (tot / np.maximum(medv, 1e-9)) * (1.0 - peff)
    return {
        "V1_DECAY_SLOPE":  (v1, -prev),
        "V2_DECAY_RATIO":  (v2, -prev),
        "V3_EFFORT_NO_RES": (v3, -prev),
        "V4_ABSORB_BAR":   (v4, d4),
        "V5_EXHAUST_EXTREME": (v5, d5),
    }, dict(tot=tot, prev=prev, peff=peff)


def run_geometry(L, dec, exitm, P_, tag, rng, do_decile_null, minbars):
    MECH, ctx = build_vol(L, dec, minbars)

    P_("")
    P_("=" * 126)
    P_(f"=== [{tag}] STEP 1 - THE SPECIFICATION GATE + feature distributions. No P&L yet.")
    P_(f"===   BINDING: a mechanism whose DIRECTION is non-zero on < {GATE:.0%} of in-window")
    P_("===   sessions is reported as UNTESTED and does NOT enter the primary. That is the")
    P_("===   W106 lesson - its VOL_DECAY fired on 3 of 1,058 sessions and its zero was averaged")
    P_("===   into a primary as though it were a measurement.")
    P_("=" * 126)
    nw = int(L.win.sum())
    P_(f"{'mechanism':<21}{'defined':>9}{'nonzero dir':>13}{'rate':>8}{'p25':>11}{'p50':>11}"
       f"{'p75':>11}{'gate':>10}")
    live = {}
    for k, (sc, di) in MECH.items():
        d = L.win & np.isfinite(sc)
        nz = d & (np.nan_to_num(di) != 0)
        rate = float(nz.sum()) / max(nw, 1)
        ok = rate >= GATE
        if ok:
            live[k] = (sc, di)
        P_(f"{k:<21}{int(d.sum()):>9}{int(nz.sum()):>13}{rate:>8.1%}"
           + (f"{np.nanpercentile(sc[d], 25):>11.3f}{np.nanpercentile(sc[d], 50):>11.3f}"
              f"{np.nanpercentile(sc[d], 75):>11.3f}" if d.sum() else f"{'-':>33}")
           + f"{('PASS' if ok else 'UNTESTED'):>10}")
    P_("")
    P_(f"    {len(live)} of {len(MECH)} mechanisms enter the primary. Thresholds now FROZEN as")
    P_("    trailing causal quantiles. Economics follows.")
    if not live:
        P_("    NO MECHANISM IS MEASURABLE. Per the spec these cells stay UNTESTED, not NULL.")
        return None

    P_("")
    P_("=" * 126)
    P_(f"=== [{tag}] STEP 2 - ECONOMICS. Decide {dec//60:02d}:{dec%60:02d}, fill next open, "
       f"hold to {exitm//60:02d}:{exitm%60:02d}, size 1, no stop.")
    P_("=" * 126)
    P_(f"{'mechanism':<21}{'rate':>6}{'N':>6}{'hit%':>8}{'p*':>8}{'vs p*':>7}{'$/trade':>10}"
       f"{'net $':>11}{'wk$@fixDD':>11}{'t':>6}")
    rows, cells, prim = [], [], []
    accept50 = {}
    for k, (sc, di) in live.items():
        for r in RATES:
            ok = LaneBench.accept(sc, r)
            des = np.nan_to_num(np.where(ok, di, 0)).astype(np.int8)
            pnl, take, cost, em = L.trade(des, dec, exitm)
            st = L.stats(pnl, take, cost, em)
            if st is None:
                P_(f"{k:<21}{r:>6.2f}   too few"); continue
            P_(f"{k:<21}{r:>6.2f}{st['n']:>6}{st['hit']:>7.2f}%{st['p_star']:>8.4f}"
               f"{100*(st['hit']/100-st['p_star']):>7.2f}{st['per_trade']:>10,.0f}"
               f"{st['net']:>11,.0f}{st['fixdd']:>11,.0f}{st['t']:>6.2f}")
            rows.append(dict(mech=k, rate=r, **st))
            mv = ((L.at(exitm) - L.at(dec + 1, use_open=True)) * PV)[take]
            cells.append((mv, cost))
            if abs(r - 0.50) < 1e-9:
                prim.append((mv, cost))
                accept50[k] = (take, des, cost)
        P_("")
    if not rows:
        return None
    DF = pd.DataFrame(rows)
    DF.to_csv(os.path.join(OUT, f"cells_{tag}.csv"), index=False)

    P_("    CONTROLS - what an unconditional trade earns at this exact geometry:")
    for lab, d_ in (("always LONG", 1), ("always SHORT", -1)):
        pnl, take, cost, em = L.trade(np.where(L.win, d_, 0).astype(np.int8), dec, exitm)
        st = L.stats(pnl, take, cost, em)
        P_(f"{'CONTROL ' + lab:<21}{'':>6}{st['n']:>6}{st['hit']:>7.2f}%{st['p_star']:>8.4f}"
           f"{100*(st['hit']/100-st['p_star']):>7.2f}{st['per_trade']:>10,.0f}"
           f"{st['net']:>11,.0f}{st['fixdd']:>11,.0f}{st['t']:>6.2f}")

    pv_ = float(DF[np.isclose(DF["rate"], 0.50)]["per_trade"].mean())
    mn, _ = LaneBench.coin_null(prim, rng)
    _, mx = LaneBench.coin_null(cells, rng)
    p95m, p95x = float(np.nanpercentile(mn, 95)), float(np.nanpercentile(mx, 95))
    P_("")
    P_("=" * 126)
    P_(f"=== [{tag}] THE PRIMARY: equal-weight mean of $/trade across the {len(live)} mechanisms "
       f"that PASSED the gate, at the 50 % arm")
    P_("=" * 126)
    P_(f"    real ${pv_:,.0f}/trade   coin null mean ${np.nanmean(mn):,.0f} p95 ${p95m:,.0f}"
       f"  -> {100*float(np.nanmean(mn < pv_)):.1f}th percentile")
    P_(f"    VERDICT: {'PASSES' if pv_ > p95m else 'FAILS'}"
       f"     best-of-{len(cells)} bar for individual cells ${p95x:,.0f}")

    # ------------------------------------------------------------- the mandated confound test
    if do_decile_null:
        P_("")
        P_("=" * 126)
        P_(f"=== [{tag}] THE MANDATED CONFOUND TEST - VOLUME-DECILE-MATCHED NULL")
        P_("===   The coverage matrix names this exact falsifier for this exact row: if the effect")
        P_("===   does not survive holding volume rank fixed, it is measuring session SIZE.")
        P_("=" * 126)
        tot = ctx["tot"]
        elig = L.win & np.isfinite(tot) & np.isfinite(L.at(dec + 1, use_open=True)) & \
            np.isfinite(L.at(exitm))
        dec_id = np.full(L.NS, -1)
        qs = np.nanpercentile(tot[elig], np.arange(10, 100, 10))
        dec_id[elig] = np.searchsorted(qs, tot[elig])
        pools = {d: np.flatnonzero(elig & (dec_id == d)) for d in range(10)}
        P_(f"{'mechanism':<21}{'real $/tr':>11}{'matched null mean':>19}{'p5':>9}{'p95':>9}"
           f"{'percentile':>12}{'verdict':>10}")
        for k, (take, des, cost) in accept50.items():
            real = float(((L.at(exitm) - L.at(dec + 1, use_open=True)) * PV * des - cost)[take]
                         .mean())
            hist = np.bincount(dec_id[take], minlength=10)
            draws = np.empty(500)
            mvfull = (L.at(exitm) - L.at(dec + 1, use_open=True)) * PV
            for b in range(500):
                pick = []
                for d in range(10):
                    if hist[d] == 0 or len(pools[d]) == 0:
                        continue
                    pick.append(rng.choice(pools[d], size=min(hist[d], len(pools[d])),
                                           replace=False))
                idx = np.concatenate(pick) if pick else np.array([], int)
                draws[b] = float((mvfull[idx] * des[idx] - cost).mean()) if len(idx) else np.nan
            p95d = float(np.nanpercentile(draws, 95))
            p05d = float(np.nanpercentile(draws, 5))
            pc = 100 * float(np.nanmean(draws < real))
            vd = ("BEATS" if real > p95d else ("WORSE" if real < p05d else "MATCHED"))
            P_(f"{k:<21}{real:>11,.0f}{np.nanmean(draws):>19,.0f}{p05d:>9,.0f}{p95d:>9,.0f}"
               f"{pc:>11.1f}th{vd:>10}")
        P_("")
        P_("")

    P_("")
    P_("=" * 126)
    P_(f"=== [{tag}] BY SESSION CLASS at the 50 % arm - directly comparable to W108's five fades")
    P_("=" * 126)
    P_(f"{'mechanism':<21}" + "".join(f"{k:>17}" for k in CLASSES))
    for k, (sc, di) in live.items():
        ok = LaneBench.accept(sc, 0.50)
        des = np.nan_to_num(np.where(ok, di, 0)).astype(np.int8)
        pnl, take, _, _ = L.trade(des, dec, exitm)
        bc = L.by_class(pnl, take)
        P_(f"{k:<21}" + "".join(f"{bc[c][0]:>6} {bc[c][1]:>10,.0f}" for c in CLASSES))
    return DF


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "voldecay.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    L = LaneBench()
    rng = np.random.default_rng(SEED)
    P_(f"    substrate {L.n:,} bars / {len(L.sess_in):,} in-window sessions "
       f"[{_time.time()-t0:.0f}s]")
    P_("")
    P_("    PRIMARY geometry is W108's. SECONDARY is W106's, reported separately and NEVER")
    P_("    averaged into the primary.")

    run_geometry(L, PRIMARY[0], PRIMARY[1], P_, "PRIMARY", rng, do_decile_null=True,
                 minbars=40)
    run_geometry(L, SECONDARY[0], SECONDARY[1], P_, "SECONDARY", rng, do_decile_null=False,
                 minbars=25)

    P_(f"\n[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
