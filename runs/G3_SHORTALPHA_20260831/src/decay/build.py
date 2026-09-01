"""G3_SHORTALPHA / decay - STAGE 1: build the objects and cache them.

Spec: runs/G3_SHORTALPHA_20260831/src/decay/spec.yaml (committed before this ran).

Two substrates, on purpose:

  CORE  = run_we_w51c.setup(), i.e. load_deep("2022-01-01", "2026-07-31 17:00") with extend
          OFF. This is the EXACT substrate W61 and W73 used. Because extend is off the base
          parquet ends 2026-05-29 16:59, so W61's "2026" is Jan-May only. This pass exists to
          reproduce the object and clear gates G1/G2 - nothing else.

  FULL  = load_deep("2006-01-01", "2026-07-31 17:00", extend=True). The same construction over
          the whole legal history, which (i) extends 2026 through July, adding the ~44 sessions
          W61 never saw, and (ii) gives the sleeve a PRE era so ERABREAK01's stratification can
          be applied to the sleeve itself instead of only to the market.

Nothing is tuned. The vote, the fills, the halt/target and the session box are imported, not
re-implemented. The only thing re-implemented here is the ratchet's leg instrumentation, and it
is re-implemented ONLY to make the rolling sigma O(1) per bar instead of O(460); it is checked
against W73's published leg table as a control.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

WE = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\research\weekly_edge\src"
sys.path.insert(0, WE)
from run_we_w01 import ROOT, PV, COMM_RT, sm14_1m                        # noqa: E402
from run_we_w17 import load_deep                                        # noqa: E402
from run_we_w19 import MEMBERS                                          # noqa: E402
from run_we_w26 import fills_daily                                      # noqa: E402
from run_we_w35 import fills_qexit                                      # noqa: E402
from run_we_w37 import causal_score                                     # noqa: E402
from run_we_w38 import vote, sfills                                     # noqa: E402
from run_we_w39 import WIN                                              # noqa: E402
from run_we_w51 import A as W61_A, B as W61_B                           # noqa: E402
from run_we_w51c import setup                                           # noqa: E402
from we_quality import build_context                                    # noqa: E402

RUN = os.path.join(ROOT, "runs", "G3_SHORTALPHA_20260831")
OUT = os.path.join(RUN, "out")
CACHE = os.path.join(OUT, "_decay_cache")
os.makedirs(CACHE, exist_ok=True)

SEAL = np.datetime64("2026-08-01")
TICK = 0.25
VOLMULTS = (6, 16, 30)          # W73's three probes; 16 is the declared PRIMARY
ZZ_THRESH = (20.0, 40.0, 80.0)  # state-blind zigzag thresholds, points


# ==================================================================================================
def assert_seal(D, tag, log):
    mx = D["t"].max()
    ok = mx < SEAL
    log(f"   SEAL ASSERTION [{tag}]: max bar {mx} < {SEAL}  ->  {'PASS' if ok else 'VIOLATION'}")
    if not ok:
        raise SystemExit("SEAL VIOLATION - refusing to continue")
    return ok


def targets_local(D):
    """The vendor member targets, cached under THIS run so no other wave's directory is written
    to. Identical call to run_we_w38.targets, different cache location."""
    key = f"{D['n']}_{int(abs(D['c']).sum())}"
    TG = {}
    for k, v in MEMBERS.items():
        f = os.path.join(CACHE, f"tg_{k}_{key}.npy")
        if os.path.exists(f):
            TG[k] = np.load(f)
            continue
        t1 = _time.time()
        TG[k] = sm14_1m(D, 460, return_targets=True, volmults=v)
        np.save(f, TG[k])
        print(f"   targets {k} built [{_time.time()-t1:.0f}s]", flush=True)
    return TG


def rolling_absdiff_mean(c, vol_period=460, minobs=30):
    """Exactly the sigma the vendor ratchet carries: mean |dClose| over the last `vol_period`
    diffs (all available diffs while fewer than that), NaN until `minobs` diffs exist.

    The reference implementation recomputes sum(list[-460:]) every bar, which is O(460) per bar
    and unusable over 5.4M bars. This is the same number by prefix sums."""
    n = len(c)
    dif = np.zeros(n)
    dif[1:] = np.abs(np.diff(c))
    cs = np.concatenate([[0.0], np.cumsum(dif)])          # cs[k] = sum(dif[:k])
    i = np.arange(n)
    cnt = np.minimum(i, vol_period)                        # diffs in the window at bar i
    lo = np.maximum(i - cnt + 1, 1)
    s = cs[i + 1] - cs[lo]
    cntf = cnt.astype(float)
    with np.errstate(invalid="ignore", divide="ignore"):
        sg = np.where(cntf >= minobs, s / np.maximum(cntf, 1.0), np.nan)
    return sg


def ratchet_legs_fast(c, volmult, vol_period=460, smin=40 * TICK, smax=1200 * TICK,
                      stopm=179 * TICK):
    """W73's ratchet_legs, arithmetic-identical, with the O(1) sigma above.

    Returns one row per COMPLETED leg: direction, start bar, bars, mfe (max favourable
    excursion in the leg's own direction), mae, terminal retracement, and the S in force."""
    n = len(c)
    sg = rolling_absdiff_mean(c, vol_period)
    Sn = np.where(np.isnan(sg) | (sg <= 0), stopm, np.clip(volmult * sg, smin, smax))
    up = False
    anchor = float(c[0])
    S = float(Sn[0])
    cur_dir, cur_i0, cur_a0, cur_S, cur_mfe, cur_mae = -1, 0, float(c[0]), S, 0.0, 0.0
    rd = []; ri = []; rb = []; rf = []; ra = []; rr = []; rs = []
    for i in range(1, n):
        px = float(c[i])
        fav = (px - cur_a0) if up else (cur_a0 - px)
        if fav > cur_mfe:
            cur_mfe = fav
        if fav < cur_mae:
            cur_mae = fav
        flip = False
        if up:
            if px >= anchor:
                anchor = px
            elif px < anchor - S:
                flip = True
        else:
            if px <= anchor:
                anchor = px
            elif px > anchor + S:
                flip = True
        if flip:
            rd.append(cur_dir); ri.append(cur_i0); rb.append(i - cur_i0)
            rf.append(cur_mfe); ra.append(cur_mae)
            rr.append(abs(anchor - px)); rs.append(cur_S)
            up = not up
            S = float(Sn[i]); anchor = px
            cur_dir, cur_i0, cur_a0, cur_S = (1 if up else -1), i, px, S
            cur_mfe = cur_mae = 0.0
    return pd.DataFrame(dict(dir=rd, i0=ri, bars=rb, mfe=rf, mae=ra, retrace=rr, S=rs))


def zigzag(c, st, en, thresh):
    """State-blind, engine-blind zigzag on 1-minute closes, per session, no look-ahead credit
    for a swing still in progress at the close. A swing is COUNTED only if its magnitude is at
    least `thresh`, which also makes the initial state harmless."""
    ns = len(st)
    nd = np.zeros(ns); pdn = np.zeros(ns); nu = np.zeros(ns); pup = np.zeros(ns)
    for s in range(ns):
        a, b = st[s], en[s]
        x = c[a:b]
        if len(x) < 3:
            continue
        piv = float(x[0]); ext = float(x[0]); d = -1
        for j in range(1, len(x)):
            v = float(x[j])
            if d < 0:
                if v < ext:
                    ext = v
                elif v - ext >= thresh:
                    mag = piv - ext
                    if mag >= thresh:
                        nd[s] += 1; pdn[s] += mag
                    piv = ext; d = 1; ext = v
            else:
                if v > ext:
                    ext = v
                elif ext - v >= thresh:
                    mag = ext - piv
                    if mag >= thresh:
                        nu[s] += 1; pup[s] += mag
                    piv = ext; d = -1; ext = v
    return nd, pdn, nu, pup


# ==================================================================================================
def session_bounds(D):
    sid, n_sess, n = D["sid"], D["n_sess"], D["n"]
    st = np.searchsorted(sid, np.arange(n_sess), side="left")
    en = np.searchsorted(sid, np.arange(n_sess), side="right")
    return st, en


def build_short(D, X, TG, log, tag):
    """The mirrored short sleeve, W61's construction, unmodified: plain mirrored vote at 0.5,
    one contract, same halt/target, same session box, flat at session close."""
    fs = vote(TG, D, X, -1)
    posS = -(fs >= 0.5).astype(np.int8)
    tr = sfills(D, posS, halt=1300.0, target=1000.0)
    log(f"   [{tag}] short sleeve raw trades: {len(tr):,}")
    return tr


def build_long(D, X, TG, log, tag, ent_lo=None, ent_hi=None):
    """P1, exactly as every wave builds it (the B1 gate object). `ent_lo/ent_hi` restrict which
    entries feed the causal quantile history - W61 restricts them to its window, so the CORE
    pass must too or the sizing differs on the first MINHIST entries."""
    posL = (vote(TG, D, X, +1) >= 0.5).astype(np.int8)
    base = fills_daily(D, posL, halt=1300, target=1000)
    tarr, n = D["t"], D["n"]

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))
    ets = [np.datetime64(x["et"]) for x in base]
    keep = [i_of(str(e)) for e in ets
            if (ent_lo is None or e >= ent_lo) and (ent_hi is None or e < ent_hi)]
    e = np.array(keep)
    sc, _ = causal_score(X, e, window=WIN)
    sz = np.where(sc >= 3, 2, 1).astype(np.int8)
    tr = fills_qexit(D, posL, sz, sc)
    log(f"   [{tag}] P1 raw trades: {len(tr):,} (causal-score history from {len(e):,} entries)")
    return tr


def trades_frame(trades, D):
    tarr, n, sid = D["t"], D["n"], D["sid"]
    sdate = D["sess_date"]
    ei = np.searchsorted(tarr, np.array([np.datetime64(x["et"]) for x in trades]))
    xi = np.searchsorted(tarr, np.array([np.datetime64(x["xt"]) for x in trades]))
    ei = np.minimum(ei, n - 1); xi = np.minimum(xi, n - 1)
    s = sid[ei]
    u = np.array([x["u"] for x in trades], float)
    pnl = np.array([x["pnl"] for x in trades], float)
    gross = pnl + COMM_RT * u
    return pd.DataFrame(dict(
        sess=s, date=pd.to_datetime(sdate[s]), entry_i=ei, exit_i=xi,
        bars=(xi - ei).astype(int), u=u, d=[x["d"] for x in trades],
        pnl436=pnl, gross_pts=gross / (PV * np.maximum(u, 1.0)),
        entry_px=D["o"][ei], exit_px=D["c"][xi]))


# ==================================================================================================
def main():
    t0 = _time.time()
    logf = open(os.path.join(CACHE, "build.log"), "w", encoding="utf-8")

    def log(*a):
        print(*a, flush=True); print(*a, file=logf); logf.flush()

    log("=" * 110)
    log("G3_SHORTALPHA / decay - STAGE 1 BUILD")
    log("=" * 110)

    # ---------------------------------------------------------------- CORE (W61/W73 exact)
    log("\n[CORE] rebuilding W61/W73's exact object (setup(), extend OFF)")
    D, X, TG, _st, _en = setup()
    assert_seal(D, "CORE", log)
    log(f"   substrate {D['n']:,} bars, {D['n_sess']} sessions "
        f"({D['t'].min()} .. {D['t'].max()})  [{_time.time()-t0:.0f}s]")
    stC, enC = session_bounds(D)
    tarr = D["t"]
    sess_in = np.array([s for s in range(D["n_sess"]) if W61_A <= tarr[stC[s]] < W61_B])
    in_win = np.zeros(D["n_sess"], bool); in_win[sess_in] = True
    NS = len(sess_in)

    trL = build_long(D, X, TG, log, "CORE", ent_lo=W61_A, ent_hi=W61_B)
    trS = build_short(D, X, TG, log, "CORE")
    dfL = trades_frame(trL, D); dfS = trades_frame(trS, D)
    dfL = dfL[in_win[dfL["sess"].values]].reset_index(drop=True)
    dfS = dfS[in_win[dfS["sess"].values]].reset_index(drop=True)
    ptsL = dfL["pnl436"].sum() / PV / NS
    ptsS = dfS["pnl436"].sum() / PV / NS
    log(f"\n   CORE window {W61_A} .. {W61_B}: {NS} sessions")
    log(f"   G1 B1 GATE  : P1 {ptsL:.2f} pts/session (W61 expect 14.72 +-0.60, W73 got 14.86)"
        f"  -> {'PASS' if abs(ptsL - 14.72) < 0.6 else 'FAIL - VOID'}")
    log(f"   G2 OBJECT   : short {len(dfS):,} trades (expect 2,225 +-2%), {ptsS:.2f} pts/session"
        f" (expect 6.00 +-0.30) -> "
        f"{'PASS' if abs(len(dfS)-2225) <= 45 and abs(ptsS-6.00) <= 0.30 else 'FAIL'}")
    dfS.to_csv(os.path.join(CACHE, "core_short_trades.csv"), index=False)
    dfL.to_csv(os.path.join(CACHE, "core_long_trades.csv"), index=False)
    sdC = pd.to_datetime(D["sess_date"])[sess_in]
    dayS = np.zeros(D["n_sess"]); np.add.at(dayS, dfS["sess"].values, dfS["pnl436"].values)
    dayL = np.zeros(D["n_sess"]); np.add.at(dayL, dfL["sess"].values, dfL["pnl436"].values)
    pd.DataFrame(dict(date=sdC.strftime("%Y-%m-%d"), p1=dayL[sess_in],
                      short=dayS[sess_in])).to_csv(
        os.path.join(CACHE, "core_daily.csv"), index=False)
    log(f"   [core cached] [{_time.time()-t0:.0f}s]")

    # W73 leg-geometry control on the CORE substrate
    log("\n[CORE] ratchet leg control against W73's published table (retrace/S medians):")
    log(f"   {'VolMult':<9}{'dir':<7}{'legs':>8}{'medBars':>9}{'medMFE':>9}{'medRetr':>9}"
        f"{'medS':>9}{'retr/S':>9}   W73 pub")
    W73REF = {(6, "up"): 1.1332, (6, "down"): 1.1309, (16, "up"): 1.0654, (16, "down"): 1.0576,
              (30, "up"): 1.0397, (30, "down"): 1.0304}
    for vm in VOLMULTS:
        lg = ratchet_legs_fast(D["c"], vm)
        for dd, nm in ((1, "up"), (-1, "down")):
            g = lg[lg["dir"] == dd]
            rs = float(np.median(g["retrace"] / g["S"]))
            log(f"   {vm:<9}{nm:<7}{len(g):>8,}{np.median(g['bars']):>9.0f}"
                f"{np.median(g['mfe']):>9.2f}{np.median(g['retrace']):>9.2f}"
                f"{np.median(g['S']):>9.2f}{rs:>9.4f}   {W73REF[(vm, nm)]:.4f}")

    del D, X, TG, dfL, dfS, trL, trS

    # ---------------------------------------------------------------- FULL history
    log(f"\n[FULL] loading 2006-01-01 .. 2026-07-31 17:00 with extend=True "
        f"[{_time.time()-t0:.0f}s]")
    D = load_deep("2006-01-01", "2026-07-31 17:00", extend=True)
    assert_seal(D, "FULL", log)
    log(f"   substrate {D['n']:,} bars, {D['n_sess']} sessions "
        f"({D['t'].min()} .. {D['t'].max()})  [{_time.time()-t0:.0f}s]")
    X = build_context(D)
    log(f"   context built [{_time.time()-t0:.0f}s]")
    TG = targets_local(D)
    log(f"   targets built [{_time.time()-t0:.0f}s]")
    stF, enF = session_bounds(D)
    trS = build_short(D, X, TG, log, "FULL")
    dfS = trades_frame(trS, D)
    dfS.to_csv(os.path.join(CACHE, "full_short_trades.csv"), index=False)
    trL = build_long(D, X, TG, log, "FULL")
    dfL = trades_frame(trL, D)
    dfL.to_csv(os.path.join(CACHE, "full_long_trades.csv"), index=False)
    log(f"   fills done [{_time.time()-t0:.0f}s]")

    # per-session frame: exposure, price geometry, opportunity
    ns = D["n_sess"]
    sdate = pd.to_datetime(D["sess_date"])
    c, o, h, l = D["c"], D["o"], D["h"], D["l"]
    dif = np.zeros(D["n"]); dif[1:] = np.diff(c)
    dif[stF] = 0.0                                   # no cross-session diff
    absmove = np.zeros(ns); upmove = np.zeros(ns); dnmove = np.zeros(ns)
    np.add.at(absmove, D["sid"], np.abs(dif))
    np.add.at(upmove, D["sid"], np.maximum(dif, 0))
    np.add.at(dnmove, D["sid"], -np.minimum(dif, 0))
    sess = pd.DataFrame(dict(
        sess=np.arange(ns), date=sdate, year=sdate.year, bars=(enF - stF),
        s_open=o[stF], s_close=c[enF - 1],
        s_high=np.array([h[a:b].max() for a, b in zip(stF, enF)]),
        s_low=np.array([l[a:b].min() for a, b in zip(stF, enF)]),
        absmove=absmove, upmove=upmove, dnmove=dnmove))
    sess["ret"] = sess["s_close"] - sess["s_open"]

    for nm, df in (("short", dfS), ("long", dfL)):
        v = np.zeros(ns); np.add.at(v, df["sess"].values, df["pnl436"].values)
        sess[f"{nm}_pnl436"] = v
        v = np.zeros(ns); np.add.at(v, df["sess"].values, (df["bars"] * df["u"]).values)
        sess[f"{nm}_cmin"] = v
        v = np.zeros(ns); np.add.at(v, df["sess"].values, np.ones(len(df)))
        sess[f"{nm}_ntr"] = v
        v = np.zeros(ns); np.add.at(v, df["sess"].values, (df["gross_pts"] * df["u"]).values)
        sess[f"{nm}_gross_pts"] = v

    # O1: ratchet-native opportunity
    log(f"\n[FULL] O1 ratchet-native opportunity [{_time.time()-t0:.0f}s]")
    for vm in VOLMULTS:
        lg = ratchet_legs_fast(c, vm)
        s_of = D["sid"][lg["i0"].values]
        for dd, nm in ((-1, f"dn{vm}"), (1, f"up{vm}")):
            m = lg["dir"].values == dd
            cnt = np.zeros(ns); np.add.at(cnt, s_of[m], 1.0)
            mfe = np.zeros(ns); np.add.at(mfe, s_of[m], lg["mfe"].values[m])
            bar = np.zeros(ns); np.add.at(bar, s_of[m], lg["bars"].values[m].astype(float))
            sess[f"o1_{nm}_n"] = cnt
            sess[f"o1_{nm}_mfe"] = mfe
            sess[f"o1_{nm}_bars"] = bar
        log(f"   VolMult {vm}: {len(lg):,} legs [{_time.time()-t0:.0f}s]")

    # O2: state-blind zigzag
    log(f"\n[FULL] O2 state-blind zigzag [{_time.time()-t0:.0f}s]")
    for th in ZZ_THRESH:
        nd, pdn, nu, pup = zigzag(c, stF, enF, th)
        sess[f"o2_dn{int(th)}_n"] = nd
        sess[f"o2_dn{int(th)}_pts"] = pdn
        sess[f"o2_up{int(th)}_n"] = nu
        sess[f"o2_up{int(th)}_pts"] = pup
        log(f"   thresh {th:.0f} pts: down {nd.sum():,.0f} swings, up {nu.sum():,.0f} "
            f"[{_time.time()-t0:.0f}s]")

    sess.to_csv(os.path.join(CACHE, "full_sessions.csv"), index=False)
    log(f"\n[cached] {len(sess):,} sessions -> full_sessions.csv  [{_time.time()-t0:.0f}s]")

    # cross-check: does the FULL substrate reproduce the CORE object on the shared window?
    cd = pd.read_csv(os.path.join(CACHE, "core_daily.csv"))
    cd["date"] = pd.to_datetime(cd["date"])
    mg = cd.merge(sess[["date", "short_pnl436", "long_pnl436"]], on="date", how="inner")
    log(f"\n[CROSS-CHECK] {len(mg)} shared sessions between CORE and FULL")
    log(f"   short: CORE ${mg['short'].sum():,.0f} vs FULL ${mg['short_pnl436'].sum():,.0f}"
        f"  | daily rho {np.corrcoef(mg['short'], mg['short_pnl436'])[0,1]:+.4f}"
        f"  | identical sessions "
        f"{100*float(np.isclose(mg['short'], mg['short_pnl436']).mean()):.1f} %")
    log(f"   P1   : CORE ${mg['p1'].sum():,.0f} vs FULL ${mg['long_pnl436'].sum():,.0f}"
        f"  | daily rho {np.corrcoef(mg['p1'], mg['long_pnl436'])[0,1]:+.4f}")
    log(f"\ndone [{_time.time()-t0:.0f}s]")
    logf.close()


if __name__ == "__main__":
    main()
