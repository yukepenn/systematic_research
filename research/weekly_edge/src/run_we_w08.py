"""WE_W08 PULLBACK (spec preregistered): the untested entry family.

Confirm-then-chase engines pay the confirmation in basis. A pullback engine defines the trend,
waits for a retracement AGAINST it, and enters on the resumption bar — better basis, more of
the move ahead. Fully causal: trend and swing state are read at i-1, fills at o[i].
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT, PV, COMM_RT, STRESS_RT, load, week_table, summarize, sm14_1m
from run_we_w03 import cd_signals                                        # noqa: E402
from run_we_w06a import available_move                                   # noqa: E402
from run_we_w07 import ema_np, session_metrics                           # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W08_PULLBACK", "out")
os.makedirs(OUT, exist_ok=True)


def pullback_trades(D, trend, R, exit_kind, exit_par, stop=130.0,
                    allow_long=None, allow_short=None, max_per_leg=3, min_gap=15):
    """Pullback-into-trend engine. trend[] is already lagged by the caller."""
    t, o, h, l, c = D["t"], D["o"], D["h"], D["l"], D["c"]
    fb, lb, n = D["fb"], D["lb"], D["n"]
    trades = []
    pos = 0; epx = 0.0; eti = -1; peak = 0.0
    leg_dir = 0; leg_ext = 0.0; leg_origin = 0.0; leg_n = 0; last_entry = -10 ** 9
    armed = False
    pend = 0

    for i in range(n):
        # ---- fill any pending entry at this bar's open -------------------------------
        if pend != 0 and pos == 0 and not fb[i]:
            pos = pend; epx, eti = o[i], i; peak = o[i]
            leg_n += 1; last_entry = i
        pend = 0

        # ---- manage open position (intrabar) -----------------------------------------
        if pos != 0:
            lvl = epx - pos * stop
            if (l[i] <= lvl) if pos > 0 else (h[i] >= lvl):
                gap = (o[i] <= lvl) if pos > 0 else (o[i] >= lvl)
                px = o[i] if gap else lvl
                trades.append(dict(d=pos, et=str(t[eti]), xt=str(t[i]),
                                   pnl=pos * (px - epx) * PV - COMM_RT))
                pos = 0
        if pos != 0:
            inval = leg_origin
            hit = None
            if (l[i] <= inval) if pos > 0 else (h[i] >= inval):
                hit = o[i] if ((o[i] <= inval) if pos > 0 else (o[i] >= inval)) else inval
            elif exit_kind == "X_TRAIL_PTS":
                tl = peak - pos * exit_par
                if (l[i] <= tl) if pos > 0 else (h[i] >= tl):
                    hit = o[i] if ((o[i] <= tl) if pos > 0 else (o[i] >= tl)) else tl
            elif exit_kind == "X_TARGET":
                tg = epx + pos * exit_par
                if (h[i] >= tg) if pos > 0 else (l[i] <= tg):
                    hit = o[i] if ((o[i] >= tg) if pos > 0 else (o[i] <= tg)) else tg
            elif exit_kind == "X_TREND" and int(trend[i]) == -pos:
                hit = c[i]
            if hit is not None:
                trades.append(dict(d=pos, et=str(t[eti]), xt=str(t[i]),
                                   pnl=pos * (float(hit) - epx) * PV - COMM_RT))
                pos = 0
            else:
                peak = max(peak, h[i]) if pos > 0 else min(peak, l[i])

        # ---- session close -----------------------------------------------------------
        if lb[i]:
            if pos != 0:
                trades.append(dict(d=pos, et=str(t[eti]), xt=str(t[i]),
                                   pnl=pos * (c[i] - epx) * PV - COMM_RT))
                pos = 0
            leg_dir = 0; armed = False; leg_n = 0
            continue

        # ---- trend leg bookkeeping (uses trend[i], already lagged) --------------------
        td = int(trend[i])
        if td != leg_dir:
            leg_dir = td; leg_ext = c[i]; leg_origin = c[i]; leg_n = 0; armed = False
        elif td != 0:
            if (c[i] > leg_ext) if td > 0 else (c[i] < leg_ext):
                leg_ext = c[i]; armed = False
        if td == 0 or leg_dir == 0:
            continue

        # ---- pullback arming and resumption trigger ----------------------------------
        span = abs(leg_ext - leg_origin)
        if span > 0:
            retr = (leg_ext - c[i]) if td > 0 else (c[i] - leg_ext)
            if retr >= R * span:
                armed = True
        if (armed and pos == 0 and leg_n < max_per_leg
                and (i - last_entry) >= min_gap and i >= 20):
            resume = (c[i] > c[i - 1]) if td > 0 else (c[i] < c[i - 1])
            if resume:
                ok = ((td > 0 and (allow_long is None or allow_long[i])) or
                      (td < 0 and (allow_short is None or allow_short[i])))
                if ok:
                    pend = td; armed = False
    return trades


def main():
    t0 = _time.time()
    D = load()
    n_sess, tarr = D["n_sess"], D["t"]
    idx = np.arange(D["n"])
    starts = np.zeros(n_sess, np.int64); ends = np.zeros(n_sess, np.int64)
    for s in range(n_sess):
        m = idx[D["sid"] == s]
        starts[s], ends[s] = m[0], m[-1] + 1
    avail = np.zeros(n_sess); adir = np.zeros(n_sess, np.int8)
    for s in range(n_sess):
        avail[s], adir[s], _, _ = available_move(D["c"], starts[s], ends[s])
    big = avail >= 500
    print(f"available ready; big days {big.mean()*100:.1f}% [{_time.time()-t0:.0f}s]",
          flush=True)

    def lag_i8(a):
        return np.concatenate([[0], a[:-1]]).astype(np.int8)

    def lag_b(a):
        return np.concatenate([[True], a[:-1]])
    _, cd_arr = cd_signals(D)
    aL, aS = lag_b(cd_arr >= 0), lag_b(cd_arr <= 0)

    tg = sm14_1m(D, 460, return_targets=True, volmults=[6, 8, 10, 12, 14, 16])
    TR = {"TR_SOLAR": lag_i8(np.sign(tg).astype(np.int8)),
          "TR_EMA": lag_i8(np.sign(ema_np(D["c"], 20) - ema_np(D["c"], 100)).astype(np.int8))}
    print(f"trends ready [{_time.time()-t0:.0f}s]", flush=True)

    out = open(os.path.join(OUT, "pullback.txt"), "w", encoding="utf-8")

    def P(*a):
        print(*a, flush=True); print(*a, file=out)

    P(f"available {avail.sum():,.0f} pts / {n_sess} sessions; big-day (>=500 pts) share "
      f"{100*big.mean():.1f}% carrying {100*avail[big].sum()/avail.sum():.1f}% of all points")
    P(f"reference: S1 1.45 pts/trade capture 4.70% | S4n.gdl 3.32 pts/trade capture 4.68%\n")
    P(f"{'variant':<34}{'n':>7}{'pts/tr':>8}{'CAPT%':>7}{'bigCAP':>8}{'smlCAP':>8}"
      f"{'RIGHT':>7}{'WRONG':>7}{'CHOP':>7}{'wkMean':>8}{'wkPos':>7}{'wkWorst':>9}"
      f"{'wkShrp':>8}{'strs':>7}")
    rows = []
    for tn, tr in TR.items():
        for R in (0.236, 0.382, 0.5):
            for xk, xp in (("X_TREND", None), ("X_TRAIL_PTS", 80), ("X_TARGET", 120)):
                for gn, (gl, gs) in (("nogate", (None, None)), ("gdl", (aL, aS))):
                    trl = pullback_trades(D, tr, R, xk, xp, allow_long=gl, allow_short=gs)
                    if len(trl) < 200:
                        continue
                    for x in trl:
                        x["d"] = x["d"]
                    sm_ = session_metrics(D, trl, avail, adir, tarr)
                    # big/small day capture
                    bys = {}
                    for x in trl:
                        i = int(min(np.searchsorted(tarr, np.datetime64(x["et"])), D["n"] - 1))
                        bys[int(D["sid"][i])] = bys.get(int(D["sid"][i]), 0.0) + x["pnl"] / PV
                    capv = np.zeros(n_sess)
                    for s, p in bys.items():
                        capv[s] = p
                    bcap = 100 * capv[big].sum() / avail[big].sum()
                    scap = 100 * capv[~big].sum() / avail[~big].sum()
                    wt = week_table(trl, D, lambda x: x["xt"])
                    r = summarize(wt, D, "dev")
                    stress = np.array(r["_net"]) - STRESS_RT * np.array(r["_ntr"])
                    ppt = sum(x["pnl"] for x in trl) / PV / len(trl)
                    nm = f"{tn}|R{R}|{xk}{'' if xp is None else xp}|{gn}"
                    P(f"{nm:<34}{len(trl):>7}{ppt:>8.2f}{sm_['CAPTURE']:>7}{bcap:>8.2f}"
                      f"{scap:>8.2f}{sm_['RIGHT']:>7}{sm_['WRONG']:>7}{sm_['CHOP']:>7}"
                      f"{r['mean']:>8,.0f}{r['pos']:>7.1f}{r['worst']:>9,.0f}"
                      f"{r['sharpe']:>8.3f}{stress.mean():>7,.0f}")
                    rows.append(dict(variant=nm, n=len(trl), pts_per_trade=round(ppt, 2),
                                     capture=sm_["CAPTURE"], big_capture=round(bcap, 2),
                                     small_capture=round(scap, 2), **{k: sm_[k] for k in
                                     ("RIGHT", "WRONG", "CHOP", "NOTRADE")},
                                     wk_mean=round(r["mean"]), wk_pos=round(r["pos"], 1),
                                     wk_worst=round(r["worst"]),
                                     wk_sharpe=round(r["sharpe"], 3),
                                     stress=round(float(stress.mean()))))
    sm = pd.DataFrame(rows)
    sm.to_csv(os.path.join(OUT, "summary.csv"), index=False)
    short = sm[(sm["capture"] > 5.5) & (sm["wk_sharpe"] >= 0.193) & (sm["stress"] > 0)]
    P(f"\nSHORTLIST (capture>5.5% AND wkSharpe>=0.193 AND stress>0): {len(short)}")
    if len(short):
        P(short.sort_values("capture", ascending=False).head(10).to_string(index=False))
    else:
        P("F1 FIRED: no pullback variant exceeds 5.5% capture -> the ceiling is not an "
          "entry-geometry artifact.")
        P("\nbest by capture regardless:")
        P(sm.sort_values("capture", ascending=False).head(8)[
            ["variant", "n", "pts_per_trade", "capture", "big_capture", "small_capture",
             "RIGHT", "wk_sharpe", "stress"]].to_string(index=False))
        P("\nbest by pts_per_trade:")
        P(sm.sort_values("pts_per_trade", ascending=False).head(8)[
            ["variant", "n", "pts_per_trade", "capture", "big_capture", "wk_mean",
             "wk_sharpe", "stress"]].to_string(index=False))
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
