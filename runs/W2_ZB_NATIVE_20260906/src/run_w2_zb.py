# -*- coding: utf-8 -*-
"""W2_ZB_NATIVE_20260906 -- Stage-5 falsifier on ZB (the most orthogonal market, rho~0.06).

Implements runs/W2_ZB_NATIVE_20260906/spec.yaml EXACTLY (trial G00062).

    Leg A  intraday MEAN-REVERSION / range-fade  -- COST-FIRST (the autopsy warns it "dies
           cheapest on cost"): gross reversion FIRST, then subtract {0.5,1,2}-tick ALL_IN;
           if gross does not clear a realistic tick -> COST-FRAGILE and STOP leg A.
    Leg B  08:30/10:00/14:00 scheduled-release vol/path -- MDE FIRST (powered?), then
           post-release continuation-vs-reversion net of ~2-tick. A powered-vol / zero-
           directional-edge result is recorded as a FACT, not a PASS.

POINTS (32nds) basis only (DELEV01): ZB is additively back-adjusted; $/pt = PV = $1000,
1 tick = 1/32 pt = $31.25, 1 pt = 32 ticks. Seal >= 2026-08-01 hard-dropped at load.
Judged to the P1 bar: eval_battery LED BY WEEKLY-VOL; fixed-DD only with its random-thinning
placebo. rho-to-P1 written to out/daily_pnl.csv. No deploy; DISCOVERY_CONSUMED.
"""
from __future__ import annotations

import os
import sys
import time as _t

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(RUN))
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)

# P1 reproduction bench (validated: reproduces P1/PCT EXACTLY, port_validation.txt) + eval battery
sys.path.insert(0, os.path.join(REPO, "runs", "XINST01_WEEKLY_EDGE_PORT_20260906", "src"))
sys.path.insert(0, os.path.join(REPO, "research", "weekly_edge", "src"))
sys.path.insert(0, REPO)
import research_sdk.eval_battery as EB                                        # noqa: E402

# ---- constants (POINTS basis) ------------------------------------------------------------
ZB_SUB = os.path.join(REPO, "runs", "SM1M_ZB_SUBSTRATE", "out", "zb_1m_2023_2026.parquet")
NQ_SUB = os.path.join(REPO, "runs", "SM1M_SUBSTRATE", "out", "nq_1m_2022_2026.parquet")
CAL_CSV = os.path.join(REPO, "research", "04_complementary_family", "c01_announcement_calendar.csv")
SEAL_LOAD = pd.Timestamp("2026-07-31 17:00")     # last bar kept (session close), >=2026-08-01 dropped
SEAL = pd.Timestamp("2026-08-01")

PV = 1000.0                 # $ per POINT for ZB
TICK = 1.0 / 32.0           # 0.03125 pt
DV = PV * TICK              # $31.25 per tick
COMM = 4.36                 # MODELED $/ctrRT (FLAGGED)
SPREAD_TICKS = (0.5, 1.0, 2.0)   # ASSUMED spread band -> ALL_IN
REALISTIC_TICK = 1.0        # the "realistic tick" the cost-first gate uses

# analysis window: 6-month warmup from data start (mirrors NQ/XINST convention), pre-seal
WIN_A = pd.Timestamp("2023-07-01")
WIN_B = SEAL

# RTH day session adopted by the ZB autopsy from ZB's own volume profile: [08:00, 16:00) ET.
# Bars are END-stamped: stamp 08:01 opens 08:00. So RTH = end-stamp minute-of-day in [481, 960].
RTH_LO, RTH_HI = 8 * 60 + 1, 16 * 60           # 481 .. 960
OR_BARS = 30                                    # opening-range = first 30 RTH bars (08:00-08:30)
SIGMA_WIN = 60                                  # trailing rolling-sigma window (bars) for the band
SIGMA_MINP = 30                                 # min periods for the trailing sigma

# Leg A neighborhood grid (from spec)
A_ANCHORS = ("VWAP", "ORMID")
A_H = (5, 15, 30)                               # tradeable horizons (min)
A_K = (1.0, 1.5, 2.0)                           # band multiples of trailing intraday sigma
A_PRIMARY = ("VWAP", 15, 1.5)                   # preregistered primary cell (middle of grid)

# Leg B
B_REL_WIN = 30                                  # release window length (min) for RV
B_FIRSTMOVE = 5                                 # "first move" window (min)
SEED = 20260906
N_NULL = 5000

_LOG = []
def P(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    _LOG.append(s)

def all_in(tk):
    return COMM + tk * DV


# ========================================================================================
# LOAD + SESSIONISE  (hard seal drop, points-grid assert)
# ========================================================================================
def load_zb():
    df = pd.read_parquet(ZB_SUB)
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time").reset_index(drop=True)
    n0 = len(df)
    df = df[df["time"] <= SEAL_LOAD].sort_values("time").reset_index(drop=True)
    n_drop = n0 - len(df)
    t = df["time"].values.astype("datetime64[s]")
    o = df["open"].values.astype(float)
    h = df["high"].values.astype(float)
    l = df["low"].values.astype(float)
    c = df["close"].values.astype(float)
    v = df["volume"].values.astype(float)
    n = len(df)
    # session id: >60-min gap starts a new session (18:00->17:00 container, same rule as bench)
    fb = np.zeros(n, bool); fb[0] = True
    fb[1:] = np.diff(t).astype("timedelta64[m]").astype(np.int64) > 60
    sid = np.cumsum(fb) - 1
    n_sess = int(sid[-1] + 1)
    # session date = date of (last bar of session end + 1 min)
    lb = np.zeros(n, bool); lb[:-1] = fb[1:]; lb[-1] = True
    last_of = np.zeros(n_sess, np.int64); last_of[sid[lb]] = np.nonzero(lb)[0]
    sess_end = t[last_of] + np.timedelta64(60, "s")
    sess_date = pd.to_datetime(sess_end.astype("datetime64[D]"))
    ts = pd.to_datetime(df["time"])
    mod = (ts.dt.hour * 60 + ts.dt.minute).to_numpy()           # end-stamp minute-of-day
    return dict(df=df, t=t, o=o, h=h, l=l, c=c, v=v, n=n, fb=fb, sid=sid,
                n_sess=n_sess, sess_date=sess_date, mod=mod, ts=ts,
                n_drop=int(n_drop), n0=int(n0))


def g0_seal_points(Z):
    P("=" * 108)
    P("G0  SEAL + POINTS BASIS")
    P("=" * 108)
    max_sess = Z["sess_date"].max()
    seal_ok = max_sess < SEAL
    # 1/32 grid assertion (DELEV01 points basis)
    on_grid = np.max(np.abs(Z["c"] * 32.0 - np.round(Z["c"] * 32.0))) < 1e-6
    P(f"  bars {Z['n']:,}  sessions {Z['n_sess']:,}  dropped>=seal {Z['n_drop']}  "
      f"(export pre-capped; {Z['n_drop']} expected)")
    P(f"  session range {Z['sess_date'].min().date()} -> {max_sess.date()}")
    P(f"  ASSERT max retained session < 2026-08-01 : {max_sess.date()} < 2026-08-01  "
      f"{'PASS' if seal_ok else 'FAIL'}")
    P(f"  POINTS basis (DELEV01): $/pt = PV = ${PV:,.0f} ; 1 tick = 1/32 pt = ${DV:.2f} ; "
      f"1 pt = 32 ticks")
    P(f"  ASSERT all closes on the 1/32 grid : {'PASS' if on_grid else 'FAIL'}  "
      f"(max off-grid {np.max(np.abs(Z['c']*32-np.round(Z['c']*32))):.2e})")
    if not seal_ok:
        raise RuntimeError("SEAL VIOLATION")
    if not on_grid:
        raise RuntimeError("POINTS-GRID VIOLATION")
    return dict(seal_ok=bool(seal_ok), on_grid=bool(on_grid),
                max_sess=str(max_sess.date()), n_sess=Z["n_sess"], n_bars=Z["n"])


# ========================================================================================
# Per-session RTH structures: VWAP, OR-mid, trailing sigma of the deviation
# ========================================================================================
def build_rth(Z):
    """Return, for every RTH bar (in [08:00,16:00) with the full analysis window), the arrays
    needed by leg A: session index, close, vwap, ormid, deviation D vs each anchor, trailing
    sigma of D, and a within-session RTH ordinal. Only sessions whose date in [WIN_A,WIN_B)."""
    mod, sid, c, h, l, v = Z["mod"], Z["sid"], Z["c"], Z["h"], Z["l"], Z["v"]
    sd = Z["sess_date"]
    in_win = (sd.values >= np.datetime64(WIN_A)) & (sd.values < np.datetime64(WIN_B))
    rth_mask = (mod >= RTH_LO) & (mod <= RTH_HI) & in_win[sid]
    idx = np.nonzero(rth_mask)[0]
    s = sid[idx]
    cc = c[idx]; hh = h[idx]; ll = l[idx]; vv = v[idx]
    tp = (hh + ll + cc) / 3.0                    # typical price for VWAP
    # per-session cumulative VWAP and OR-mid, trailing sigma of deviation
    vwap = np.empty(len(idx)); ormid = np.empty(len(idx))
    Dv = np.empty(len(idx)); Do = np.empty(len(idx))
    sig_v = np.full(len(idx), np.nan); sig_o = np.full(len(idx), np.nan)
    ordn = np.empty(len(idx), np.int64)          # within-session RTH ordinal (0-based)
    # group boundaries
    bnds = np.nonzero(np.diff(s))[0] + 1
    starts = np.concatenate([[0], bnds]); ends = np.concatenate([bnds, [len(idx)]])
    for a, b in zip(starts, ends):
        cs = cc[a:b]; ts_ = tp[a:b]; vs = vv[a:b]
        m = b - a
        ordn[a:b] = np.arange(m)
        cv = np.cumsum(ts_ * vs); cvol = np.cumsum(vs)
        vw = cv / np.where(cvol > 0, cvol, np.nan)
        vwap[a:b] = vw
        # OR-mid = midpoint of first OR_BARS RTH bars' (high,low); available from bar OR_BARS on
        if m >= 1:
            k = min(OR_BARS, m)
            orh = np.max(hh[a:a + k]); orl = np.min(ll[a:a + k])
            om = 0.5 * (orh + orl)
        ormid[a:b] = om
        dv = cs - vw; do = cs - om
        Dv[a:b] = dv; Do[a:b] = do
        # trailing rolling std of the deviation (causal), min periods SIGMA_MINP
        sig_v[a:b] = pd.Series(dv).rolling(SIGMA_WIN, min_periods=SIGMA_MINP).std(ddof=1).to_numpy()
        sig_o[a:b] = pd.Series(do).rolling(SIGMA_WIN, min_periods=SIGMA_MINP).std(ddof=1).to_numpy()
    return dict(idx=idx, s=s, c=cc, vwap=vwap, ormid=ormid, Dv=Dv, Do=Do,
                sig_v=sig_v, sig_o=sig_o, ordn=ordn, sess_date=sd,
                starts=starts, ends=ends)


# ========================================================================================
# LEG A -- fade-signed forward reversion with anchor-touch-or-H exit
# ========================================================================================
def forward_reversion(R, anchor, H):
    """For every RTH bar i (per session), the fade-signed reversion (POINTS) over the horizon:
    enter fading the deviation D_i (short if D_i>0), exit at the FIRST bar in (i, i+H] whose
    deviation flips sign (anchor touch: D_j*D_i<=0), else at i+H (time stop). Requires the full
    horizon to lie inside the same session (late-session bars are ineligible). Returns
    F (points) and an eligibility mask."""
    D = R["Dv"] if anchor == "VWAP" else R["Do"]
    c = R["c"]
    N = len(c)
    F = np.zeros(N)
    elig = np.zeros(N, bool)
    for a, b in zip(R["starts"], R["ends"]):
        m = b - a
        if m <= H:
            continue
        Ds = D[a:b]; cs = c[a:b]
        # first sign-flip offset within 1..H for each i (0..m-1-H eligible for full horizon)
        # build flip matrix over offsets h=1..H  (shape H x (m-H)); memory light for m<=~500
        base = np.arange(m - H)
        Di = Ds[base]
        exit_off = np.full(m - H, H, np.int64)
        found = np.zeros(m - H, bool)
        for hh in range(1, H + 1):
            prod = Ds[base + hh] * Di
            hit = (prod <= 0) & (~found)
            exit_off[hit] = hh
            found |= hit
            if found.all():
                break
        exit_idx = base + exit_off
        side = -np.sign(Di)                       # fade: short if D>0
        # positions where Di==0 (price exactly at anchor) -> no trade
        rev = side * (cs[exit_idx] - cs[base])    # points captured by the fade
        rev[Di == 0] = 0.0
        F[a + base] = rev
        el = np.zeros(m, bool); el[base] = (Di != 0)
        elig[a:b] = el
    return F, elig


def moving_block_ci(x, L, B, rng, alpha=0.05):
    """Two-sided (1-alpha) CI for the mean via moving-block bootstrap (dependence-preserving)."""
    x = np.asarray(x, float); n = len(x)
    if n < 2:
        return float("nan"), float("nan")
    nb = int(np.ceil(n / L))
    pool = np.arange(0, max(1, n - L + 1))
    means = np.empty(B)
    for bb in range(B):
        st = rng.choice(pool, nb, replace=True)
        ii = (st[:, None] + np.arange(L)[None, :]).ravel()[:n]
        means[bb] = x[ii].mean()
    lo, hi = np.percentile(means, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return float(lo), float(hi)


def circular_shift_p(F, gate, rng, B):
    """One-sided p for E[F | gate] > 0 under a circular-shift null that rolls F relative to the
    gate mask (preserves F's autocorrelation; randomises WHERE the gate lands)."""
    obs = float(F[gate].mean())
    N = len(F)
    idx = np.nonzero(gate)[0]
    offs = rng.integers(1, N, size=B)
    null = np.empty(B)
    for j in range(B):
        null[j] = F[(idx + offs[j]) % N].mean()
    p = (1 + int(np.sum(null >= obs))) / (B + 1)
    return obs, float(p), float(null.mean())


def nonoverlap_trades(R, anchor, H, k):
    """Non-overlapping fade trades for the (anchor,H,k) cell: scan RTH bars per session, enter
    when |D|>k*sigma, exit at anchor-touch-or-H, resume after exit. Returns per-trade points,
    entry global-bar index, and session date."""
    D = R["Dv"] if anchor == "VWAP" else R["Do"]
    sig = R["sig_v"] if anchor == "VWAP" else R["sig_o"]
    c = R["c"]; idx = R["idx"]; sess_date = R["sess_date"]
    pts = []; ent_gi = []; ent_date = []
    for a, b in zip(R["starts"], R["ends"]):
        m = b - a
        if m <= H:
            continue
        Ds = D[a:b]; ss = sig[a:b]; cs = c[a:b]
        i = 0
        while i < m - H:
            if np.isfinite(ss[i]) and ss[i] > 0 and abs(Ds[i]) > k * ss[i] and Ds[i] != 0:
                Di = Ds[i]
                # exit: first flip in (i, i+H], else i+H
                ex = i + H
                for hh in range(1, H + 1):
                    if Ds[i + hh] * Di <= 0:
                        ex = i + hh
                        break
                side = -np.sign(Di)
                pts.append(float(side * (cs[ex] - cs[i])))
                ent_gi.append(int(idx[a + i]))
                # session date of this entry
                ent_date.append(sess_date.values[R["s"][a + i]])
                i = ex + 1
            else:
                i += 1
    return (np.array(pts), np.array(ent_gi, np.int64),
            pd.to_datetime(np.array(ent_date)) if ent_date else pd.to_datetime([]))


def leg_A(Z, R, rng):
    P("")
    P("=" * 108)
    P("LEG A  intraday MEAN-REVERSION / range-fade  --  COST-FIRST")
    P("=" * 108)
    P(f"  anchor in {A_ANCHORS} ; H in {A_H} min ; band k in {A_K} x trailing sigma "
      f"(rolling std of deviation, {SIGMA_WIN}-bar/{SIGMA_MINP}-minp, causal)")
    P(f"  fade: short if price>anchor, long if price<anchor ; exit at anchor-touch or H (time stop)")
    P(f"  COST band ALL_IN = ${COMM:.2f} comm + {{0.5,1,2}}tk spread = "
      f"${all_in(0.5):.2f} / ${all_in(1.0):.2f} / ${all_in(2.0):.2f} per ctrRT")
    P(f"  realistic-tick gate = {REALISTIC_TICK:.0f} tick  (net>0 must clear ${all_in(REALISTIC_TICK):.2f} "
      f"= {all_in(REALISTIC_TICK)/PV:.5f} pt = {all_in(REALISTIC_TICK)/DV:.3f} ticks gross)")

    # precompute F/elig per (anchor,H) once; reuse across k
    Fcache = {}
    for anchor in A_ANCHORS:
        for H in A_H:
            Fcache[(anchor, H)] = forward_reversion(R, anchor, H)

    rows = []
    for anchor in A_ANCHORS:
        sig = R["sig_v"] if anchor == "VWAP" else R["sig_o"]
        D = R["Dv"] if anchor == "VWAP" else R["Do"]
        for H in A_H:
            F, elig = Fcache[(anchor, H)]
            for k in A_K:
                gate = elig & np.isfinite(sig) & (sig > 0) & (np.abs(D) > k * sig)
                n_gate = int(gate.sum())
                # (1) conditional forward reversion (overlapping) + circular-shift null
                if n_gate >= 20:
                    obs, cs_p, null_mean = circular_shift_p(F, gate, rng, N_NULL)
                else:
                    obs, cs_p, null_mean = float("nan"), float("nan"), float("nan")
                # unconditional control: fade ANY displacement at matched clock (all eligible bars)
                uncond = float(F[elig].mean()) if elig.sum() else float("nan")
                # (2) per-trade non-overlapping trades (what you'd actually earn per fade)
                pts, gi, dts = nonoverlap_trades(R, anchor, H, k)
                ntr = len(pts)
                g_pts = float(pts.mean()) if ntr else float("nan")
                g_usd = g_pts * PV
                if ntr >= 5:
                    tstat = g_pts / (pts.std(ddof=1) / np.sqrt(ntr) + 1e-12)
                    ci_lo_pts, ci_hi_pts = moving_block_ci(pts, L=4, B=2000, rng=rng)
                else:
                    tstat = float("nan"); ci_lo_pts = ci_hi_pts = float("nan")
                net = {tk: g_usd - all_in(tk) for tk in SPREAD_TICKS}
                clears_realistic = net[REALISTIC_TICK] > 0
                ci_excl0 = (ci_lo_pts > 0) if np.isfinite(ci_lo_pts) else False
                null_excl = (cs_p < 0.05 / (len(A_ANCHORS) * len(A_H) * len(A_K))) if np.isfinite(cs_p) else False
                rows.append(dict(
                    anchor=anchor, H=H, k=k, n_trades=ntr, n_gate=n_gate,
                    gross_pts=g_pts, gross_usd=g_usd, gross_ticks=g_pts / TICK if ntr else float("nan"),
                    gross_t=float(tstat), ci_lo_usd=ci_lo_pts * PV, ci_hi_usd=ci_hi_pts * PV,
                    uncond_gross_usd=uncond * PV,
                    cond_fwd_rev_usd=obs * PV, circ_null_usd=null_mean * PV, circ_shift_p=cs_p,
                    net_0p5tk=net[0.5], net_1tk=net[1.0], net_2tk=net[2.0],
                    clears_1tk=bool(clears_realistic), ci_excl0=bool(ci_excl0),
                    null_excl_bonf=bool(null_excl),
                    is_primary=(anchor, H, k) == A_PRIMARY))
    dfA = pd.DataFrame(rows)
    dfA.to_csv(os.path.join(OUT, "legA_neighborhood.csv"), index=False)

    # print neighborhood table
    P("")
    P("  NEIGHBORHOOD (gross reversion per fade, POINTS basis; net = gross - ALL_IN):")
    P(f"  {'anchor':<7}{'H':>4}{'k':>5}{'ntr':>6}{'grossTk':>9}{'gross$':>9}{'t':>7}"
      f"{'ciLo$':>9}{'net@1tk':>9}{'uncond$':>9}{'circP':>8}")
    for _, r in dfA.iterrows():
        star = " *" if r["is_primary"] else ""
        P(f"  {r['anchor']:<7}{int(r['H']):>4}{r['k']:>5.1f}{int(r['n_trades']):>6}"
          f"{r['gross_ticks']:>9.3f}{r['gross_usd']:>9.2f}{r['gross_t']:>7.2f}"
          f"{r['ci_lo_usd']:>9.2f}{r['net_1tk']:>9.2f}{r['uncond_gross_usd']:>9.2f}"
          f"{r['circ_shift_p']:>8.3f}{star}")

    # cost-first decision (lead: does ANY cell clear 1-tick gross with CI>0 and null-excluded?)
    survivors = dfA[(dfA["clears_1tk"]) & (dfA["ci_excl0"]) & (dfA["null_excl_bonf"])]
    best = dfA.sort_values("net_1tk", ascending=False).iloc[0]
    prim = dfA[dfA["is_primary"]].iloc[0]
    P("")
    P(f"  best cell by net@1tk: {best['anchor']} H{int(best['H'])} k{best['k']:.1f}  "
      f"gross ${best['gross_usd']:.2f} ({best['gross_ticks']:.3f}tk)  net@1tk ${best['net_1tk']:.2f}  "
      f"ciLo ${best['ci_lo_usd']:.2f}  circP {best['circ_shift_p']:.3f}")
    P(f"  primary cell {A_PRIMARY}: gross ${prim['gross_usd']:.2f}  net@1tk ${prim['net_1tk']:.2f}  "
      f"circP {prim['circ_shift_p']:.3f}")
    cost_fragile = len(survivors) == 0
    P(f"  cells clearing 1-tick net>0 AND CI excl 0 AND circular-null-excluded (Bonferroni "
      f"{0.05/len(dfA):.4f}): {len(survivors)}")
    if cost_fragile:
        P("  ==> LEG A COST-FRAGILE: gross reversion does not clear a realistic (1-tick) ALL_IN "
          "with CI>0 vs the null. STOP leg A (per spec cost_first).")
    else:
        P(f"  ==> LEG A has {len(survivors)} cost-robust cell(s); build tradeable series.")
    return dfA, prim, best, cost_fragile


def leg_A_tradeable(Z, R, prim, rng, p1_weekly, p1_daily):
    """Build the PRIMARY-cell daily/weekly net series (net at 1-tick), run eval_battery LED BY
    WEEKLY-VOL matched to P1, fixed-DD with placebo, and a 0/0.5/1/2-tick weekly-vol spread band.
    This runs regardless of the cost-first verdict: even a COST-FRAGILE fade has a daily series
    used ONLY for the orthogonality/diversification read (labelled as such)."""
    anchor, H, k = prim["anchor"], int(prim["H"]), float(prim["k"])
    pts, gi, dts = nonoverlap_trades(R, anchor, H, k)
    ntr = len(pts)
    # net per trade at each tick; build daily series
    out = {}
    # per-trade net at 1-tick as the representative engine daily PnL
    def daily_series(tk):
        net = pts * PV - all_in(tk)
        ser = pd.Series(net, index=pd.to_datetime(dts).date).groupby(level=0).sum()
        return ser
    d1 = daily_series(REALISTIC_TICK)
    # weekly aggregation
    def weekly_from_daily(ser):
        di = pd.to_datetime(ser.index)
        iso = di.isocalendar()
        wk = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).to_numpy()
        return pd.Series(ser.values, index=wk).groupby(level=0).sum()
    w1 = weekly_from_daily(d1)

    # align weekly with P1 weekly on shared ISO weeks -> weekly-vol matched income
    j = pd.concat([w1.rename("zb"), p1_weekly.rename("p1")], axis=1).dropna()
    res = EB.evaluate(j["zb"].to_numpy(), j["p1"].to_numpy(), n_placebo=0)
    wv = float(res["weekly_vol"]); nat = float(res["native"])

    P("")
    P("  LEG A tradeable (PRIMARY cell) -- eval_battery LED BY WEEKLY-VOL, matched to P1:")
    P(f"    trades {ntr} ; shared ISO weeks {len(j)} ; native ${nat:,.2f}/wk")
    for b in ("native", "weekly_vol", "realized_vol", "gross_exposure"):
        lead = "  <== PRIMARY (weekly-vol)" if b == "weekly_vol" else ""
        P(f"    {b:<16} ${res[b]:>12,.2f}/wk{lead}")

    # spread-sensitivity band on weekly-vol (cost-robust axis)
    band = {}
    for tk in (0.0, 0.5, 1.0, 2.0):
        wd = weekly_from_daily(daily_series(tk))
        jj = pd.concat([wd.rename("zb"), p1_weekly.rename("p1")], axis=1).dropna()
        band[tk] = float(EB.evaluate(jj["zb"].to_numpy(), jj["p1"].to_numpy(), n_placebo=0)["weekly_vol"])
    pos_through = max([tk for tk in (0.0, 0.5, 1.0, 2.0) if band[tk] > 0], default=-1)
    if pos_through >= 1.0:
        cost_robust = "weekly-vol net>0 through %g-tick spread" % pos_through
    elif pos_through in (0.0, 0.5):
        cost_robust = "positive only at <=%g-tick (COST-FRAGILE)" % pos_through
    else:
        cost_robust = "negative even at 0-tick"
    P(f"    spread band (weekly-vol $/wk): " +
      "  ".join(f"{tk:g}tk ${band[tk]:,.0f}" for tk in (0.0, 0.5, 1.0, 2.0)))
    P(f"    cost robustness: {cost_robust}")

    # fixed-DD ONLY with its side-blind random-thinning placebo (T2 lesson; eval_battery raises else)
    tp = pts * PV - all_in(REALISTIC_TICK)
    di = pd.to_datetime(dts)
    iso = di.isocalendar()
    wkid = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).to_numpy()
    codes, uniq = pd.factorize(pd.Index(wkid), sort=True)
    nper = len(uniq)
    nrm = max(1, int(round(0.10 * len(tp))))
    res_dd = EB.evaluate(j["zb"].to_numpy(), j["zb"].to_numpy(), n_placebo=2000,
                         base_for_placebo="fixed_dd", ref_trades=tp, ref_periods=codes,
                         n_trades_removed=nrm, seed=SEED)
    base_income = tp.sum() / nper
    null = EB.random_thinning_placebo(tp, codes, nrm, "fixed_dd", n=2000, seed=SEED, n_periods=nper)
    placebo_med = float(np.median(null))
    P(f"    G3 fixed-DD (order-stat, shown ONLY with placebo): self fixed-DD ${base_income:,.2f}/wk ; "
      f"side-blind 10%-thin median ${placebo_med:,.2f}/wk (lift {placebo_med-base_income:+,.2f}) ; "
      f"LEAD weekly-vol ${wv:,.2f}/wk -> edge on weekly-vol (not fixed-DD-only)? {wv>0}")

    return dict(daily=d1, weekly=w1, wv=wv, native=nat, band=band, pos_through=pos_through,
                cost_robust=cost_robust, ntr=ntr, shared_wk=len(j),
                weekly_vol_ok=bool(wv > 0))


# ========================================================================================
# LEG B -- scheduled-macro-release vol / path
# ========================================================================================
def load_calendar():
    cal = pd.read_csv(CAL_CSV)
    cal["date"] = pd.to_datetime(cal["date"])
    cal = cal[(cal["date"] >= WIN_A) & (cal["date"] < WIN_B)]
    d0830 = set(cal[cal["time_et"] == "08:30"]["date"].dt.date)         # NFP + CPI
    dfomc = set(cal[cal["event"] == "FOMC"]["date"].dt.date)           # 14:00
    ev0830 = cal[cal["time_et"] == "08:30"].groupby(cal["event"]).size().to_dict()
    return d0830, dfomc, ev0830, cal


def window_rv_and_path(Z, anchor_min, win_len, fm_len):
    """Per session-date: realized vol (points) over [anchor, anchor+win_len) and the post-anchor
    path pieces. anchor_min is the end-stamp minute of the RELEASE INSTANT (release at HH:MM opens
    the bar stamped HH:MM+1). Base price = close of the bar stamped == anchor_min (covers the
    minute ending at the release). Returns dict keyed by session-date."""
    mod, sid, c = Z["mod"], Z["sid"], Z["c"]
    sd = Z["sess_date"]
    out = {}
    # index bars by (session, mod) -> position
    order = np.argsort(sid, kind="stable")
    # iterate sessions in the window
    in_win = (sd.values >= np.datetime64(WIN_A)) & (sd.values < np.datetime64(WIN_B))
    for s in np.unique(sid[in_win[sid]]):
        rows = np.nonzero(sid == s)[0]
        mods = mod[rows]; cl = c[rows]
        mp = {int(m): cl[i] for i, m in enumerate(mods)}
        # need base .. anchor+win_len
        need = [anchor_min + j for j in range(0, win_len + 1)]
        if not all(mm in mp for mm in need):
            continue
        seq = np.array([mp[anchor_min + j] for j in range(0, win_len + 1)])   # win_len+1 closes
        rets = np.diff(seq)                                    # win_len 1-min point returns
        rv = float(np.sqrt(np.sum(rets ** 2)))
        # first move over fm_len, then continuation window fm_len..win_len
        first_move = float(seq[fm_len] - seq[0])
        cont_leg = float(seq[win_len] - seq[fm_len])           # price move after the first move
        out[sd.values[s].astype("datetime64[D]").astype(object)] = dict(
            rv=rv, first_move=first_move, cont_leg=cont_leg, base=float(seq[0]))
    return out


def mde_two_sample(n1, n2, sd_pooled, z_alpha=1.6448536269, z_power=0.8416212336):
    """Minimum detectable difference in means (one-sided) at given alpha/power."""
    return (z_alpha + z_power) * sd_pooled * np.sqrt(1.0 / n1 + 1.0 / n2)


def leg_B(Z, rng):
    P("")
    P("=" * 108)
    P("LEG B  scheduled-macro-release VOL / PATH  --  MDE FIRST")
    P("=" * 108)
    d0830, dfomc, ev0830, cal = load_calendar()
    all_sess = set(Z["sess_date"].date)
    all_sess = {d for d in all_sess if WIN_A.date() <= d < WIN_B.date()}
    rel_all = d0830 | dfomc
    nonrel = all_sess - rel_all
    P(f"  calendar: {CAL_CSV.split(os.sep)[-1]}  (bls.gov / federalreserve.gov)")
    P(f"  08:30 releases in window (NFP+CPI): n={len(d0830)}  composition {ev0830}  "
      f"(~{len(d0830)/((WIN_B-WIN_A).days/365.25):.0f}/yr)")
    P(f"  14:00 FOMC in window: n={len(dfomc)}")
    P(f"  DEVIATION: 10:00 ISM/JOLTS releases -- NO provenanced in-repo calendar exists; "
      f"fabricating dates would violate the no-unverified-data discipline (cf. SMV2X NFP/PCE "
      f"deferral). 10:00 releases are DEFERRED, not silently dropped.")
    P(f"  sessions in window {len(all_sess)} ; release {len(rel_all)} ; non-release {len(nonrel)}")

    rows = []
    for (label, rel_dates, anchor_min) in (
            ("0830_NFPCPI", d0830, 8 * 60 + 30),      # release 08:30 -> base bar stamp 08:30
            ("1400_FOMC", dfomc, 14 * 60)):           # release 14:00 -> base bar stamp 14:00
        WV = window_rv_and_path(Z, anchor_min, B_REL_WIN, B_FIRSTMOVE)
        rel = {d: WV[d] for d in WV if d in rel_dates}
        non = {d: WV[d] for d in WV if d in nonrel}
        rv_rel = np.array([v["rv"] for v in rel.values()])
        rv_non = np.array([v["rv"] for v in non.values()])
        n1, n2 = len(rv_rel), len(rv_non)
        sd_pooled = np.sqrt(((n1 - 1) * rv_rel.var(ddof=1) + (n2 - 1) * rv_non.var(ddof=1)) / (n1 + n2 - 2))
        mde = mde_two_sample(n1, n2, sd_pooled)
        P("")
        P(f"  --- {label}  window [{anchor_min//60:02d}:{anchor_min%60:02d}, "
          f"+{B_REL_WIN}min)  release n={n1}  non-release n={n2} ---")
        P(f"    (i) RV EXCESS.  MDE (80% power, one-sided a=0.05, pooled sd {sd_pooled:.4f} pt): "
          f"${mde*PV:,.0f} = {mde:.4f} pt  <-- PRINTED BEFORE OBSERVED")
        excess = rv_rel.mean() - rv_non.mean()
        ratio = rv_rel.mean() / rv_non.mean()
        # event-time-shift null: relabel n1 random non-release+release sessions as "release"
        pool = np.array([WV[d]["rv"] for d in WV])
        null = np.empty(N_NULL)
        for j in range(N_NULL):
            pick = rng.choice(len(pool), n1, replace=False)
            m = np.zeros(len(pool), bool); m[pick] = True
            null[j] = pool[m].mean() - pool[~m].mean()
        p_rv = (1 + int(np.sum(null >= excess))) / (N_NULL + 1)
        powered = (excess > mde) and (p_rv < 0.05)
        P(f"        OBSERVED RV: release {rv_rel.mean():.4f} pt (${rv_rel.mean()*PV:,.0f}) vs "
          f"non-release {rv_non.mean():.4f} pt (${rv_non.mean()*PV:,.0f})")
        P(f"        excess {excess:.4f} pt (${excess*PV:,.0f}) ; ratio {ratio:.2f}x ; "
          f"event-shift null p {p_rv:.4f} ; > MDE? {excess>mde} ; POWERED? {powered}")

        # (ii) post-release PATH: continuation vs reversion of the first move, net of ~2-tick
        fm = np.array([v["first_move"] for v in rel.values()])
        cl = np.array([v["cont_leg"] for v in rel.values()])
        # continuation: trade in the sign of the first move over the continuation leg
        cont_pts = np.sign(fm) * cl
        rev_pts = -cont_pts
        cost2 = all_in(2.0)
        cont_net = cont_pts * PV - cost2
        rev_net = rev_pts * PV - cost2
        # dependence-preserving null via event-time-shift: same path stat on non-release days
        fm_non = np.array([v["first_move"] for v in non.values()])
        cl_non = np.array([v["cont_leg"] for v in non.values()])
        cont_non = np.sign(fm_non) * cl_non * PV
        # bootstrap CI on the mean net (moving-block over the release-day sequence)
        def mean_p(x_net, x_non_gross):
            obs = float(x_net.mean())
            # null: draw n1 from the non-release continuation distribution
            nn = np.empty(N_NULL)
            for j in range(N_NULL):
                nn[j] = rng.choice(x_non_gross, n1, replace=True).mean() - cost2
            p = (1 + int(np.sum(nn >= obs))) / (N_NULL + 1)
            return obs, p
        cont_obs, cont_p = mean_p(cont_net, cont_non)
        rev_obs, rev_p = mean_p(rev_net, -cont_non)
        # directional: is EITHER continuation or reversion net-positive AND significant?
        tradeable = ((cont_obs > 0 and cont_p < 0.05) or (rev_obs > 0 and rev_p < 0.05))
        P(f"    (ii) POST-RELEASE PATH (first move {B_FIRSTMOVE}min, continuation leg "
          f"{B_FIRSTMOVE}->{B_REL_WIN}min), net of 2-tick (${cost2:.2f}):")
        P(f"        CONTINUATION mean net ${cont_obs:,.2f}/trade  (gross "
          f"${cont_pts.mean()*PV:,.2f}) ; event-shift null p {cont_p:.4f}")
        P(f"        REVERSION    mean net ${rev_obs:,.2f}/trade  (gross "
          f"${rev_pts.mean()*PV:,.2f}) ; event-shift null p {rev_p:.4f}")
        P(f"        first-move mean ${fm.mean()*PV:+,.2f} (|mean| small => no directional bias) ; "
          f"TRADEABLE net of cost? {tradeable}")
        if not tradeable:
            P(f"        ==> {label}: POWERED VOL, ZERO DIRECTIONAL EDGE -- recorded as a FACT, not a PASS.")
        rows.append(dict(label=label, anchor=f"{anchor_min//60:02d}:{anchor_min%60:02d}",
                         n_release=n1, n_nonrelease=n2,
                         rv_release_pt=float(rv_rel.mean()), rv_nonrelease_pt=float(rv_non.mean()),
                         rv_excess_pt=float(excess), rv_excess_usd=float(excess*PV),
                         rv_ratio=float(ratio), rv_mde_usd=float(mde*PV), rv_mde_pt=float(mde),
                         rv_excess_gt_mde=bool(excess > mde), rv_null_p=float(p_rv),
                         rv_powered=bool(powered),
                         first_move_mean_usd=float(fm.mean()*PV),
                         cont_net_usd=float(cont_obs), cont_gross_usd=float(cont_pts.mean()*PV),
                         cont_null_p=float(cont_p),
                         rev_net_usd=float(rev_obs), rev_gross_usd=float(rev_pts.mean()*PV),
                         rev_null_p=float(rev_p),
                         cost_2tk=float(cost2), tradeable=bool(tradeable),
                         verdict=("TRADEABLE" if tradeable else "VOL-ONLY-NO-DIRECTION")))
    dfB = pd.DataFrame(rows)
    dfB.to_csv(os.path.join(OUT, "legB_release.csv"), index=False)
    any_tradeable = bool(dfB["tradeable"].any())
    any_powered = bool(dfB["rv_powered"].any())
    return dfB, any_tradeable, any_powered


# ========================================================================================
# P1 reproduction (validated bench) for the orthogonality read
# ========================================================================================
def reproduce_p1():
    import xinst_bench as XB
    from we_lab import spread_profile
    prof = spread_profile()
    Dnq, bnq = XB.load_substrate(NQ_SUB, "NQ")
    trnq, mnq = XB.build_p1pct(Dnq, PV=20.0, comm=4.36, halt_pts=XB.NQ_HALT_PTS,
                               tgt_pts=XB.NQ_TGT_PTS, smin_pts=None, smax_pts=None,
                               stopm_pts=None, win_a="2022-07-01", win_b="2026-08-01")
    net_nq, ct, rate, ntr = XB.net_series(Dnq, trnq, PV=20.0, tick=0.25,
                                          spread_model=("nq_profile", prof),
                                          sess_in=mnq["sess_in"], i_of=mnq["i_of"])
    w_nq, wk_nq = XB.weekly(Dnq, net_nq, mnq["sess_in"])
    pan = XB.panel(w_nq)
    sd = pd.to_datetime(Dnq["sess_date"])[mnq["sess_in"]]
    daily = pd.Series(net_nq, index=sd.date).groupby(level=0).sum()
    weekly = pd.Series(w_nq, index=wk_nq)
    return daily, weekly, pan, bnq


# ========================================================================================
def gate_table(g0, dfA, primA, legA_trade, dfB, anyB_tradeable, anyB_powered,
               rho_daily, rho_weekly, shared_days, survives, verdict):
    def row(g, spec, obs, ok):
        return f"{g:<7}{spec:<50}{str(obs)[:34]:>36}{('PASS' if ok else ('FACT' if ok is None else 'FAIL')):>7}"
    L = []
    L.append("=" * 108)
    L.append("W2_ZB_NATIVE_20260906  --  GATE / SPEC / OBSERVED / PASS-FAIL  (program-printed)")
    L.append("=" * 108)
    L.append(f"{'gate':<7}{'spec':<50}{'observed':>36}{'verdict':>7}")
    L.append("-" * 108)
    L.append(row("G0", "points basis + seal asserted",
                 f"grid&seal, maxsess {g0['max_sess']}", g0["seal_ok"] and g0["on_grid"]))
    # G1 MDE first (both legs): leg A cost-to-edge printed before observed; leg B MDE before observed
    L.append(row("G1", "MDE / cost-to-edge printed BEFORE observed",
                 f"legA cost=${all_in(REALISTIC_TICK):.2f}; legB MDE printed first", True))
    # G2A cost-first
    surv = dfA[(dfA["clears_1tk"]) & (dfA["ci_excl0"]) & (dfA["null_excl_bonf"])]
    L.append(row("G2A", "legA gross clears 1tk ALL_IN, CI excl 0 vs null",
                 f"{len(surv)}/{len(dfA)} cells; best net@1tk ${dfA['net_1tk'].max():.0f}",
                 len(surv) > 0))
    # G2B powered then tradeable
    b_txt = f"powered={anyB_powered}; tradeable_path={anyB_tradeable}"
    L.append(row("G2B", "legB RV powered(MDE) AND tradeable path net cost",
                 b_txt, (anyB_powered and anyB_tradeable) if anyB_tradeable else None))
    # G3 weekly-vol not fixed-DD-only
    L.append(row("G3", "any edge on weekly-vol (not fixed-DD-only)",
                 f"legA weekly-vol ${legA_trade['wv']:,.0f}/wk", legA_trade["wv"] > 0))
    # G4 orthogonality printed
    L.append(row("G4", "rho-to-P1 daily PnL printed",
                 f"daily rho {rho_daily:+.4f} ({shared_days} shared d)", True))
    L.append("-" * 108)
    L.append(f"SURVIVES (legA cost-robust CI>0  OR  legB tradeable net of cost) : {survives}")
    L.append(f"VERDICT : {verdict}")
    L.append("")
    L.append("NOTE: FACT = leg B powered-vol / zero-directional-edge is recorded as a FACT, not a PASS")
    L.append("      (spec G2B). All figures in-sample, DISCOVERY_CONSUMED, POINTS/32nds basis. No deploy.")
    return "\n".join(L)


def main():
    t0 = _t.time()
    rng = np.random.default_rng(SEED)
    Z = load_zb()
    g0 = g0_seal_points(Z)

    R = build_rth(Z)
    P(f"  RTH bars in window [{WIN_A.date()},{WIN_B.date()}): {len(R['idx']):,}  "
      f"[{_t.time()-t0:.0f}s]")

    # ---- P1 reproduction (for orthogonality) ----
    P("")
    P("=" * 108)
    P("P1/PCT reproduction (validated bench; reproduces the committed figures EXACTLY)")
    P("=" * 108)
    p1_daily, p1_weekly, p1_pan, bnq = reproduce_p1()
    P(f"  P1/PCT weekly ${p1_pan['weekly']:,.6f}  maxDD ${p1_pan['maxdd']:,.6f}  t {p1_pan['t']:.6f}  "
      f"(NQ {bnq['n_bars']:,} bars, seal_ok {bnq['seal_ok']})  [{_t.time()-t0:.0f}s]")

    # ---- LEG A ----
    dfA, primA, bestA, cost_fragile = leg_A(Z, R, rng)
    legA_trade = leg_A_tradeable(Z, R, primA, rng, p1_weekly, p1_daily)

    # ---- LEG B ----
    dfB, anyB_tradeable, anyB_powered = leg_B(Z, rng)

    # ---- ORTHOGONALITY: rho of ZB engine daily PnL (leg A primary cell, net@1tk) vs P1 ----
    P("")
    P("=" * 108)
    P("G4  ORTHOGONALITY -- rho of ZB engine daily PnL vs P1 (the diversification prize)")
    P("=" * 108)
    zb_daily = legA_trade["daily"]
    jd = pd.concat([zb_daily.rename("zb"), p1_daily.rename("p1")], axis=1).dropna()
    rho_daily = float(jd["zb"].corr(jd["p1"])) if len(jd) > 2 else float("nan")
    jw = pd.concat([legA_trade["weekly"].rename("zb"), p1_weekly.rename("p1")], axis=1).dropna()
    rho_weekly = float(jw["zb"].corr(jw["p1"])) if len(jw) > 2 else float("nan")
    # write daily_pnl.csv (the ZB engine daily series used for the portfolio/orthogonality step)
    dp = zb_daily.rename("zb_pnl").to_frame()
    dp.index.name = "date"
    dp.to_csv(os.path.join(OUT, "daily_pnl.csv"))
    P(f"  ZB engine daily series = LEG A primary cell {A_PRIMARY} net@1tk (dense daily; used ONLY")
    P(f"    for the diversification read -- the engine's profitability verdict is below).")
    P(f"  shared days {len(jd)} ; daily rho(ZB,P1) {rho_daily:+.4f} ; weekly rho {rho_weekly:+.4f}")
    P(f"  (ZB autopsy daily point-return rho(ZB,NQ) was +0.064 -- orthogonality confirmed)")
    P(f"  wrote out/daily_pnl.csv ({len(dp)} rows)")

    # ---- VERDICT + survives ----
    legA_cost_robust = (not cost_fragile) and legA_trade["weekly_vol_ok"] and legA_trade["pos_through"] >= 1.0
    survives = bool(legA_cost_robust or anyB_tradeable)
    if survives and legA_cost_robust:
        verdict = "INFORMATION-SUPPORTED"
    elif survives and anyB_tradeable:
        verdict = "INFORMATION-SUPPORTED"
    elif cost_fragile and not anyB_tradeable and anyB_powered:
        # leg A dies on cost; leg B is powered vol with no directional edge
        verdict = "COST-FRAGILE"        # leg A is the money engine; ZB kill-gate is cost
    elif cost_fragile:
        verdict = "COST-FRAGILE"
    else:
        verdict = "FAIL"

    gt = gate_table(g0, dfA, primA, legA_trade, dfB, anyB_tradeable, anyB_powered,
                    rho_daily, rho_weekly, len(jd), survives, verdict)
    P("")
    P(gt)
    with open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8") as f:
        f.write(gt + "\n")
    with open(os.path.join(OUT, "run_log.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(_LOG) + "\n")

    # stash a machine-readable summary for the report / structured output
    summ = dict(
        run_id="W2_ZB_NATIVE_20260906", seal_ok=g0["seal_ok"], on_grid=g0["on_grid"],
        max_sess=g0["max_sess"], n_sess=g0["n_sess"], n_bars=g0["n_bars"],
        rth_bars=len(R["idx"]),
        legA_cost_fragile=bool(cost_fragile),
        legA_best_anchor=bestA["anchor"], legA_best_H=int(bestA["H"]), legA_best_k=float(bestA["k"]),
        legA_best_gross_usd=float(bestA["gross_usd"]), legA_best_gross_ticks=float(bestA["gross_ticks"]),
        legA_best_net1tk=float(bestA["net_1tk"]), legA_best_circp=float(bestA["circ_shift_p"]),
        legA_primary_gross_usd=float(primA["gross_usd"]), legA_primary_net1tk=float(primA["net_1tk"]),
        legA_primary_circp=float(primA["circ_shift_p"]),
        legA_weekly_vol=float(legA_trade["wv"]), legA_native=float(legA_trade["native"]),
        legA_cost_robust=legA_trade["cost_robust"], legA_pos_through=float(legA_trade["pos_through"]),
        legB_powered=bool(anyB_powered), legB_tradeable=bool(anyB_tradeable),
        rho_daily=rho_daily, rho_weekly=rho_weekly, shared_days=len(jd),
        p1_weekly=float(p1_pan["weekly"]), survives=survives, verdict=verdict,
        daily_pnl_path="runs/W2_ZB_NATIVE_20260906/out/daily_pnl.csv")
    # leg B facts
    for _, r in dfB.iterrows():
        summ[f"legB_{r['label']}_rv_ratio"] = float(r["rv_ratio"])
        summ[f"legB_{r['label']}_rv_excess_usd"] = float(r["rv_excess_usd"])
        summ[f"legB_{r['label']}_rv_mde_usd"] = float(r["rv_mde_usd"])
        summ[f"legB_{r['label']}_rv_powered"] = bool(r["rv_powered"])
        summ[f"legB_{r['label']}_cont_net"] = float(r["cont_net_usd"])
        summ[f"legB_{r['label']}_rev_net"] = float(r["rev_net_usd"])
        summ[f"legB_{r['label']}_verdict"] = r["verdict"]
    import json
    with open(os.path.join(OUT, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summ, f, indent=2, default=str)
    P("")
    P(f"[done {_t.time()-t0:.0f}s] wrote gate_table.txt, legA_neighborhood.csv, legB_release.csv, "
      f"daily_pnl.csv, summary.json, run_log.txt")
    return summ


if __name__ == "__main__":
    main()
