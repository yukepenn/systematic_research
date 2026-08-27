"""WE_W100 - TRACK A, DOWNSIDE PERSISTENCE.

Spec: runs/WE_W100_DOWNSIDE/spec.yaml, committed BEFORE this ran.

The question is NOT "can we build a short engine" - the campaign has failed at that repeatedly by
mirroring. The question is whether either of the two information axes this program has NEVER used
separates a good downside continuation from a bad one, holding the trigger SCHEDULE completely
fixed so that nothing but the information changes.

    F_VOL   relvol = v / mean20(v) >= 1.0 at the trigger bar
    F_SEMI  rsv_share = sigma_dn/(sigma_dn+sigma_up) >= its own trailing-250-session median
    F_BOTH  both
    F_RAND  200 random filters accepting the SAME NUMBER of triggers - the control that decides
    LONG    the identical battery on the long leg - if F_SEMI helps longs equally it is a plain
            volatility filter and the mechanism claim dies even if the money is real
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
from run_we_w51 import classify, session_frames                          # noqa: E402
from run_we_w51c import dd_profile                                       # noqa: E402
from run_we_w98 import gfills, arm_kw                                    # noqa: E402
from we_channels import build_channels, session_clock                    # noqa: E402
from we_lab import spread_profile                                        # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W100_DOWNSIDE", "out")
os.makedirs(OUT, exist_ok=True)
W76OUT = os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out")
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
DDT = 20245.0
TICKV = 5.0
NPERM = 200
SEED = 100


def gfills_fast(D, dir_arr, halt=1300.0, target=1000.0, per_ctr=True):
    """gfills for a SIZE-1 signed target, iterating only over bars where a transition can occur.
    Between two consecutive change points of `want` nothing can happen, so the event set is
    {want changes} U {session firsts} U {session lasts}. Asserted byte-identical to gfills."""
    t, o, c = D["t"], D["o"], D["c"]
    fb, lb, n = D["fb"], D["lb"], D["n"]
    want_arr = np.r_[0, np.asarray(dir_arr[:-1], np.int64)]
    want_arr[fb] = 0
    ev = np.unique(np.concatenate([
        np.flatnonzero(np.r_[True, want_arr[1:] != want_arr[:-1]]),
        np.flatnonzero(fb), np.flatnonzero(lb)]))
    trades = []
    p = 0; u = 0; epx = 0.0; eti = -1; spnl = 0.0; stopped = False
    for i in ev:
        i = int(i)
        if fb[i]:
            spnl = 0.0; stopped = False
        want = 0 if stopped else int(want_arr[i])
        if want != p:
            if p != 0:
                pnl = p * u * (o[i] - epx) * PV - COMM_RT * u
                trades.append(dict(d=p, u=u, et=str(t[eti]), xt=str(t[i]), pnl=pnl))
                spnl += (pnl / u) if per_ctr else pnl
                if spnl <= -halt or (target is not None and spnl >= target):
                    stopped = True; want = 0
            p = want
            if p != 0:
                u = 1; epx, eti = o[i], i
        if lb[i] and p != 0:
            pnl = p * u * (c[i] - epx) * PV - COMM_RT * u
            trades.append(dict(d=p, u=u, et=str(t[eti]), xt=str(t[i]), pnl=pnl))
            p = 0; u = 0
    return trades


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "downside.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    prof = spread_profile()
    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr, sid, lb, fb = D["n"], D["t"], D["sid"], D["lb"], D["fb"]
    o, c, h, l, v = D["o"], D["c"], D["h"], D["l"], D["v"]
    st_, en_, _ = session_frames(D)
    klass = classify(D, st_, en_)
    mod = ((tarr - tarr.astype("datetime64[D]")).astype("timedelta64[s]")
           .astype(np.int64) // 60).astype(np.int32)
    sp_tk = prof.reindex(mod).to_numpy()
    sess_in = np.array([s for s in range(D["n_sess"]) if A <= tarr[st_[s]] < B])
    in_win = np.zeros(D["n_sess"], bool); in_win[sess_in] = True
    sdate = pd.to_datetime(D["sess_date"])[sess_in]
    iso = sdate.isocalendar()
    wk = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).to_numpy()
    bidx = np.arange(n) - st_[sid]

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    # ------------------------------------------------------------------ B1
    z = np.load(os.path.join(W76OUT, "mem_ext.npz"))
    bmom_cached = z["bmom"]
    CH = build_channels(D, which=["X0v_bmom"])
    ch = CH["X0v_bmom"]
    P_("=" * 118)
    P_("=== B1: the reconstructed base schedule vs the engine's own cached B-MOM array")
    P_("=" * 118)
    P_("    THE BASE IS THE ENGINE'S OWN CACHED B-MOM ARRAY, not a reconstruction. B1 is")
    P_("    therefore satisfied by construction; what follows is a DIAGNOSTIC on we_channels.")
    same = int((ch == bmom_cached).sum())
    d_ = np.flatnonzero(ch != bmom_cached)
    P_(f"    we_channels' reconstruction agrees on {same:,} of {n:,} bars "
       f"({100*same/n:.4f} %); W72 recorded 99.992 % on the SHORTER substrate.")
    if len(d_):
        u_, cn_ = np.unique(sid[d_], return_counts=True)
        top = sorted(zip(u_, cn_), key=lambda z_: -z_[1])[:3]
        sdall = pd.to_datetime(D["sess_date"])
        P_(f"    {len(d_)} divergent bars over {len(u_)} of {D['n_sess']} sessions; worst: "
           + ", ".join(f"{sdall[a_].date()} ({b_})" for a_, b_ in top))
        P_("    `FINDING` 2026-07-17 is a TRUNCATED SESSION in the extended substrate - it ends")
        P_("    10:53 with 83 RTH bars against a normal 390 - and accounts for most of the gap.")
        P_("    It is a data hole, not a channel defect, and it lies inside the BURNED span.")
        P_("    Recorded because X9a is built by the same module and inherits the same path.")
    ch = bmom_cached
    hhmmss, seg_, in_rth, _ = session_clock(D)
    flatm = tarr >= D["sess_end"][sid] - np.timedelta64(21 * 60, "s")

    # ------------------------------------------------------------------ features
    def roll_mean(x, k):
        s = pd.Series(x).rolling(k, min_periods=k).mean().to_numpy()
        s[bidx < k - 1] = np.nan
        return s
    relvol = v / np.maximum(roll_mean(v, 20), 1e-9)
    r = np.r_[0.0, np.diff(c)]; r[fb] = 0.0
    sdn = np.sqrt(np.maximum(roll_mean(np.where(r < 0, r * r, 0.0), 30), 0.0))
    sup = np.sqrt(np.maximum(roll_mean(np.where(r > 0, r * r, 0.0), 30), 0.0))
    share = sdn / np.maximum(sdn + sup, 1e-9)
    # causal trailing-250-SESSION median of the share, computed per session then broadcast
    ss = pd.Series(share).groupby(sid).mean()
    med = ss.rolling(250, min_periods=60).median().shift(1).to_numpy()
    med_b = med[sid]
    P_(f"\n    relvol defined on {100*np.isfinite(relvol).mean():.1f} % of bars, "
       f"rsv_share on {100*np.isfinite(share).mean():.1f} %, "
       f"its causal median on {100*np.isfinite(med_b).mean():.1f} %")

    # ------------------------------------------------------------------ the leg objects
    def leg_target(side):
        """the base schedule restricted to ONE side, under the channel's own discipline"""
        g = np.where(ch == side, side, 0).astype(np.int8)
        g[flatm] = 0
        return g

    def trades_of(g, accept=None):
        """accept: bool array over BARS; a latch run is taken only if accept[entry bar] is True"""
        if accept is None:
            gg = g
        else:
            gg = g.copy()
            newrun = (gg != 0) & (np.r_[0, gg[:-1]] != gg)
            runid = np.cumsum(newrun) * (gg != 0)
            ok_run = np.zeros(runid.max() + 1, bool)
            ent = np.flatnonzero(newrun)
            ok_run[runid[ent]] = accept[ent]
            gg = np.where(ok_run[runid] & (gg != 0), gg, 0).astype(np.int8)
        tr = gfills_fast(D, gg, halt=1300.0, target=1000.0, per_ctr=True)
        return [x for x in tr if in_win[int(sid[i_of(x["et"])])]]

    def stats(trl, window=None):
        if not trl:
            return dict(n=0, ctr=0, per_rt=np.nan, weekly=np.nan, weekly_fixdd=np.nan,
                        poswk=np.nan, maxdd=np.nan, top5=np.nan, streak=0, t=np.nan, net=0.0)
        w_ = {}
        for x in trl:
            for ts in (x["et"], x["xt"]):
                p_ = pd.Timestamp(ts); m_ = p_.hour * 60 + p_.minute
                w_[m_] = w_.get(m_, 0.0) + x["u"]
        rate = TICKV * sum(float(prof.get(m, 3.0)) * q for m, q in w_.items()) / \
            max(sum(w_.values()), 1e-9)
        sp = np.zeros(D["n_sess"]); ct = np.zeros(D["n_sess"])
        for x in trl:
            s_ = int(sid[i_of(x["et"])]); sp[s_] += x["pnl"]; ct[s_] += x["u"]
        ser = sp[sess_in] - rate * ct[sess_in]
        m = np.ones(len(sess_in), bool) if window is None else window
        wv = pd.Series(ser[m]).groupby(wk[m]).sum().to_numpy()
        dp = dd_profile(wv)
        stk = max((len(list(g)) for k_, g in itertools.groupby(wv < 0) if k_), default=0)
        ctr = float(ct[sess_in][m].sum())
        return dict(n=int(sum(1 for x in trl if m[np.searchsorted(
            sess_in, int(sid[i_of(x["et"])]))])), ctr=ctr,
            per_rt=float(ser[m].sum()) / max(ctr, 1e-9), net=float(ser[m].sum()),
            weekly=float(wv.mean()),
            weekly_fixdd=float(wv.mean()) * DDT / max(dp["maxdd"], 1e-9),
            poswk=100 * float((wv > 0).mean()), maxdd=dp["maxdd"], top5=dp["dd_mean_top5"],
            streak=int(stk),
            t=float(wv.mean()) / max(wv.std(ddof=1) / np.sqrt(max(len(wv), 2)), 1e-9))

    # B1b: the fast engine must be byte-identical to gfills on the real objects
    def _same(a, b):
        return (len(a) == len(b) and
                all(x["d"] == y["d"] and x["u"] == y["u"] and x["et"] == y["et"] and
                    x["xt"] == y["xt"] and abs(x["pnl"] - y["pnl"]) < 1e-9
                    for x, y in zip(a, b)))
    _gS, _gL = leg_target(-1), leg_target(1)
    _okf = all(_same(gfills_fast(D, gg, halt=1300.0, target=1000.0, per_ctr=True),
                     gfills(D, gg, None, **arm_kw("PCT", 1.0))) for gg in (_gS, _gL))
    P_(f"    B1b  gfills_fast == gfills on both legs, byte for byte ... "
       f"{'PASS' if _okf else 'FAIL'}")
    if not _okf:
        out.close(); return

    ACC = {"F_VOL": np.nan_to_num(relvol, nan=0.0) >= 1.0,
           "F_SEMI": np.nan_to_num(share, nan=0.0) >= np.nan_to_num(med_b, nan=1e9)}
    ACC["F_BOTH"] = ACC["F_VOL"] & ACC["F_SEMI"]

    P_("")
    P_("=" * 118)
    P_("=== THE BATTERY. Primary is mean $ per contract round turn - the only statistic a filter")
    P_("===   cannot flatter by changing exposure.")
    P_("=" * 118)
    rng = np.random.default_rng(SEED)
    rows = []
    for legname, side in (("SHORT", -1), ("LONG", 1)):
        g = leg_target(side)
        base = trades_of(g)
        bs = stats(base)
        newrun = (g != 0) & (np.r_[0, g[:-1]] != g)
        ent = np.flatnonzero(newrun)
        P_("")
        P_(f"  --- {legname} leg " + "-" * 96)
        P_(f"{'arm':<12}{'accept%':>9}{'trades':>8}{'ctr':>7}{'$/ctrRT':>10}{'net $':>11}"
           f"{'wk$@fixDD':>11}{'wk+%':>7}{'top5':>9}{'t':>6}{'null p95':>10}{'pct':>7}")
        P_(f"{'BASE':<12}{100.0:>8.1f}%{bs['n']:>8,}{bs['ctr']:>7,.0f}{bs['per_rt']:>10.2f}"
           f"{bs['net']:>11,.0f}{bs['weekly_fixdd']:>11,.0f}{bs['poswk']:>6.1f}%"
           f"{bs['top5']:>9,.0f}{bs['t']:>6.2f}")
        rows.append(dict(leg=legname, arm="BASE", accept=100.0, **bs))
        for fname in ("F_VOL", "F_SEMI", "F_BOTH"):
            acc = ACC[fname]
            k = int(acc[ent].sum())
            tr = trades_of(g, acc)
            s_ = stats(tr)
            # rate-matched random-filter null on the PRIMARY statistic
            nullv = np.empty(NPERM)
            for b_ in range(NPERM):
                pick = np.zeros(n, bool)
                pick[rng.choice(ent, size=k, replace=False)] = True
                nullv[b_] = stats(trades_of(g, pick))["per_rt"]
            p95 = float(np.percentile(nullv, 95))
            pct = 100 * float((nullv < s_["per_rt"]).mean())
            P_(f"{fname:<12}{100*k/len(ent):>8.1f}%{s_['n']:>8,}{s_['ctr']:>7,.0f}"
               f"{s_['per_rt']:>10.2f}{s_['net']:>11,.0f}{s_['weekly_fixdd']:>11,.0f}"
               f"{s_['poswk']:>6.1f}%{s_['top5']:>9,.0f}{s_['t']:>6.2f}{p95:>10.2f}"
               f"{pct:>6.1f}")
            rows.append(dict(leg=legname, arm=fname, accept=100 * k / len(ent),
                             null_mean=float(nullv.mean()), null_p95=p95,
                             null_p9917=float(np.percentile(nullv, 99.17)), pctile=pct, **s_))
            P_(f"{'':12}{'':9}null: mean {nullv.mean():.2f}  sd {nullv.std(ddof=1):.2f}  "
               f"p95 {p95:.2f}  p99.17(Bonferroni 6) "
               f"{np.percentile(nullv,99.17):.2f}   [{_time.time()-t0:.0f}s]")
    DF = pd.DataFrame(rows)
    DF.to_csv(os.path.join(OUT, "battery.csv"), index=False)

    # ------------------------------------------------------------------ verdicts
    P_("")
    P_("=" * 118)
    P_("=== VERDICTS against the falsifiers fixed in the spec")
    P_("=" * 118)

    def g_(leg, arm, col):
        r_ = DF[(DF.leg == leg) & (DF.arm == arm)]
        return float(r_.iloc[0][col]) if len(r_) else np.nan
    for hn, arm in (("H1_volume", "F_VOL"), ("H2_semivar", "F_SEMI")):
        real = g_("SHORT", arm, "per_rt"); p95 = g_("SHORT", arm, "null_p95")
        pb = g_("SHORT", arm, "null_p9917")
        verdict = ("SUPPORTED" if real > pb else
                   "WEAK (clears 95th, not Bonferroni)" if real > p95 else "FALSIFIED")
        P_(f"    {hn:<12} SHORT {arm:<7} ${real:.2f}/ctrRT vs p95 ${p95:.2f} / "
           f"p99.17 ${pb:.2f}   ->  {verdict}")
    dS = g_("SHORT", "F_SEMI", "per_rt") - g_("SHORT", "BASE", "per_rt")
    dL = g_("LONG", "F_SEMI", "per_rt") - g_("LONG", "BASE", "per_rt")
    P_(f"    H3_asymmetry  F_SEMI lifts SHORT by ${dS:+.2f}/ctrRT and LONG by ${dL:+.2f}/ctrRT"
       f"   ->  {'SUPPORTED' if dS > dL else 'FALSIFIED - it is a volatility filter'}")

    # ------------------------------------------------------------------ recency + class
    P_("")
    P_("=" * 118)
    P_("=== RECENCY and SESSION CLASS on the SHORT leg (t6m/t3m lie in the BURNED span)")
    P_("=" * 118)
    sd = sdate.to_numpy()
    WN = [("FULL", "2022-07-01", "2026-08-01"), ("2024+", "2024-01-01", "2026-08-01"),
          ("2025", "2025-01-01", "2026-01-01"), ("2026YTD", "2026-01-01", "2026-08-01"),
          ("t12m", "2025-08-01", "2026-08-01"), ("t6m", "2026-02-01", "2026-08-01")]
    g = leg_target(-1)
    P_(f"{'window':<9}" + "".join(f"{a_:>12}" for a_ in ("BASE", "F_VOL", "F_SEMI", "F_BOTH")))
    wrows = []
    for w, x_, y_ in WN:
        m = (sd >= np.datetime64(x_)) & (sd < np.datetime64(y_))
        vals = []
        for arm in ("BASE", "F_VOL", "F_SEMI", "F_BOTH"):
            tr = trades_of(g, None if arm == "BASE" else ACC[arm])
            vals.append(stats(tr, m)["per_rt"])
        P_(f"{w:<9}" + "".join(f"{x:>12.2f}" for x in vals))
        wrows.append(dict(window=w, **{a_: vals[i] for i, a_ in
                                       enumerate(("BASE", "F_VOL", "F_SEMI", "F_BOTH"))}))
    pd.DataFrame(wrows).to_csv(os.path.join(OUT, "recency.csv"), index=False)
    P_("    (mean $ per contract round turn)")

    kl = klass[sess_in]
    P_("")
    P_(f"{'class':<12}{'share':>8}" + "".join(f"{a_:>12}" for a_ in
                                              ("BASE", "F_VOL", "F_SEMI", "F_BOTH")))
    for kk in ("TREND-UP", "TREND-DOWN", "REVERSAL", "RANGE", "MIXED"):
        m = kl == kk
        vals = [stats(trades_of(g, None if a_ == "BASE" else ACC[a_]), m)["per_rt"]
                for a_ in ("BASE", "F_VOL", "F_SEMI", "F_BOTH")]
        P_(f"{kk:<12}{100*m.mean():>7.1f}%" + "".join(f"{x:>12.2f}" for x in vals))
    P_(f"\n[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
