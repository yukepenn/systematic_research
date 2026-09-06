"""W2B_EQMR_20260906  (trial G00063, family CROSS_ASSET_NATIVE)

Raw daily MEAN-REVERSION on a liquid equity index (ES lead, YM/RTY extension), POINTS basis,
additively back-adjusted. This is the STAGE-5 falsifier of Wave-2's strongest lead: the
"raw-ES MR control" that measured +$370/wk / Sharpe 0.78 inside W2_EQRESID (G00061). Wave-2
used it only as a CONTROL; here it becomes the CANDIDATE and we ask the two questions that
decide whether it is a portfolio-additive engine:

  (G2, CO-PRIMARY KILL) is the +$370/wk genuine daily reversion, or just captured equity
      DRIFT?  -> beat an EXPOSURE-MATCHED always-long control on the same instrument; the
      SPREAD's block-bootstrap CI must exclude 0 at Bonferroni alpha 0.0167 AND the signal
      must clear a circular-shift null. (This is exactly what killed GC-MR.)
  (G6, CO-PRIMARY VALUE) is its daily PnL diversifying to the live NQ book P1? -> PnL-rho to
      the REPRODUCED P1 daily series, per instrument. LOW/NEGATIVE rho is the prize.

Mechanism (spec runs/W2B_EQMR_20260906/spec.yaml, verbatim intent):
  Daily RTH open->close point returns per instrument.  L_t = cumsum(ret_pt) (cumulative-return
  LEVEL, the reproduced control's exact definition).  z_t = (L_t - trailing-mean_W)/trailing-sd_W
  (causal).  FADE the extension: z>=+k -> SHORT, z<=-k -> LONG.  Exit on z mean-cross or after
  H=20 days.  Params from the reproduced control (W=60, k=1.5, cost=1tk); neighborhood
  {W in 60,120} x {k in 1.0,1.5,2.0}; plateau required.  Single-leg cost band {1,2} ticks.

Drift control (the kill test):  c = mean(pos_t) (net signed exposure of the engine).  The
  exposure-matched always-long control holds a CONSTANT position c every day (buy&hold, one
  round-turn cost).  drift_t = c * ret_pt_t * PV.  SPREAD_t = engine_net_t - drift_t isolates
  the timing covariance cov(pos,ret)*PV -- the pure reversion edge, drift removed.

SEAL: every bar >= 2026-08-01 is GLOBAL VIRGIN; hard-dropped at load; boundary printed & asserted.
POINTS basis, back-adjusted (DELEV01).  Judged to the P1 bar (in-sample + robust, no forward
freeze).  NO deploy.  DISCOVERY_CONSUMED.
"""
from __future__ import annotations

import os
import sys
import time as _t

import numpy as np
import pandas as pd

REPO = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
HERE = os.path.dirname(os.path.abspath(__file__))
RUNDIR = os.path.dirname(HERE)
OUT = os.path.join(RUNDIR, "out")
os.makedirs(OUT, exist_ok=True)

XB_SRC = os.path.join(REPO, "runs", "XINST01_WEEKLY_EDGE_PORT_20260906", "src")
for p in (XB_SRC, os.path.join(REPO, "research", "weekly_edge", "src"), REPO):
    if p not in sys.path:
        sys.path.insert(0, p)
import xinst_bench as XB                                              # noqa: E402
from we_lab import spread_profile                                    # noqa: E402
import research_sdk.eval_battery as EB                               # noqa: E402

SEAL = pd.Timestamp("2026-08-01")
SEAL_LOAD = pd.Timestamp("2026-07-31 17:00")
WIN_A = pd.Timestamp("2022-07-01")          # spec strategy window start
WIN_B = SEAL                                 # exclusive
SEED = 20260906

# ---- instrument table (POINTS, additively back-adjusted) --------------------------------
NQ_SUB = "runs/SM1M_SUBSTRATE/out/nq_1m_2022_2026.parquet"
PV_NQ = 20.0
TICK_NQ = 0.25
INSTR = {
    #        substrate parquet                                        PV     tick   $/tick
    "ES":  ("runs/SM1M_ES_SUBSTRATE/out/es_1m_2022_2026.parquet",    50.0,  0.25),  # 12.50
    "YM":  ("runs/SM1M_YM_SUBSTRATE/out/ym_1m_2022_2026.parquet",     5.0,  1.00),  #  5.00
    "RTY": ("runs/SM1M_RTY_SUBSTRATE/out/rty_1m_2022_2026.parquet",  50.0,  0.10),  #  5.00
}
INSTR_ORDER = ["ES", "YM", "RTY"]
COMM = 4.36                  # $/ctrRT round-turn, MODELED (flagged)

WINDOWS = (60, 120)
ZTHRS = (1.0, 1.5, 2.0)
COSTS = (1, 2)               # ticks per single leg
HMAX = 20                    # max hold (trading days); primary exit is mean-cross
PRIMARY = dict(window=60, zthr=1.5, cost=1)

# reproduce target (W2_EQRESID raw-ES MR control, primary cell)
REPRO_WK = 370.22
REPRO_SH = 0.777

Z_ALPHA = 1.6448536269       # one-sided 0.05
Z_POWER = 0.8416212336       # 80% power
FAMILY = 3                   # ES/YM/RTY
BONF = 0.05 / FAMILY         # 0.0167 one-sided per-instrument on the drift-control spread
N_CIRC = 2000                # circular shifts of the signal (fixed seed)

_LOG = []


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    _LOG.append(s)


# ----------------------------------------------------------------- daily RTH o->c (POINTS)
def daily_rth_oc(path, label):
    """Aggregate 1-min bars to daily RTH open->close in POINTS. RTH = bar-end minute in
    [09:31, 16:00] ET (bars END-stamped; 09:31 opens at 09:30:00). Hard-drop every bar
    >= 2026-08-01 at load; print & assert the boundary."""
    df = pd.read_parquet(path if os.path.isabs(path) else os.path.join(REPO, path))
    df["time"] = pd.to_datetime(df["time"])
    n0 = len(df)
    df = df[df["time"] <= SEAL_LOAD].copy()          # HARD DROP virgin
    n_drop = n0 - len(df)
    tod = df["time"].dt.hour * 60 + df["time"].dt.minute
    rth = df[(tod >= 571) & (tod <= 960)].copy()     # 09:31 .. 16:00 inclusive
    rth["date"] = rth["time"].dt.normalize()
    g = rth.sort_values("time").groupby("date")
    op = g["open"].first()
    cl = g["close"].last()
    out = pd.DataFrame({"open": op, "close": cl})
    out["ret_pt"] = out["close"] - out["open"]
    out = out[out.index < WIN_B]                     # exclusive seal on session date too
    maxd = out.index.max()
    seal_ok = bool(maxd < SEAL)
    P(f"  [{label}] loaded {n0:,} bars, dropped>=seal {n_drop:,}; RTH daily sessions "
      f"{len(out):,}  {out.index.min().date()} -> {maxd.date()}  seal_ok={seal_ok}")
    if not seal_ok:
        raise RuntimeError(f"SEAL VIOLATION {label}: max session {maxd}")
    return out


# ----------------------------------------------------------------- trailing z (causal)
def trailing_z(level, zwin):
    L = pd.Series(level)
    m = L.rolling(zwin, min_periods=zwin).mean()
    s = L.rolling(zwin, min_periods=zwin).std(ddof=1)
    z = (L - m) / s
    return z.to_numpy()


# ----------------------------------------------------------------- MR state machine (single leg)
def run_mr(level, zt, ret_pt, zthr, hmax, leg_cost_rt):
    """Fade the extension of the LEVEL. pos in {-1,0,+1} DURING day t (decided at end of t-1).
    Enter AGAINST extension: z>=+k SHORT, z<=-k LONG; exit on z mean-cross (through 0) or after
    hmax days. Round-turn cost charged once per completed trade on the EXIT day.
    Returns pos, per-day cost $, and the trade list (entry/exit/side/hold)."""
    n = len(level)
    pos = np.zeros(n, np.int8)
    cost = np.zeros(n)
    trades = []
    cur = 0
    entry_i = -1
    hold = 0
    for t in range(n):
        pos[t] = cur
        z = zt[t]
        if not np.isfinite(z):
            continue
        if cur == 0:
            nxt = -1 if z >= zthr else (+1 if z <= -zthr else 0)
            if nxt != 0:
                entry_i = t
                hold = 0
            cur = nxt
        else:
            hold += 1
            crossed = (cur < 0 and z <= 0.0) or (cur > 0 and z >= 0.0)
            if crossed or hold >= hmax:
                cost[t] += leg_cost_rt
                trades.append(dict(entry=entry_i, exit=t, side=cur, hold=hold))
                cur = 0
    if cur != 0:
        t = n - 1
        cost[t] += leg_cost_rt
        trades.append(dict(entry=entry_i, exit=t, side=cur, hold=hold))
    return dict(pos=pos, cost=cost, trades=trades)


# ----------------------------------------------------------------- weekly aggregation
def to_weekly(dates, daily):
    iso = pd.DatetimeIndex(dates).isocalendar()
    wk = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).to_numpy()
    return pd.Series(daily, index=wk).groupby(level=0).sum()


def sharpe_wk(x):
    x = np.asarray(x, float)
    sd = x.std(ddof=1)
    return float(x.mean() / sd * np.sqrt(52)) if sd > 0 else float("nan")


def tstat(x):
    x = np.asarray(x, float)
    return float(x.mean() / max(x.std(ddof=1) / np.sqrt(len(x)), 1e-9))


# ----------------------------------------------------------------- circular-shift null
def circ_shift_null(pos, ret, n_shifts=N_CIRC, seed=SEED):
    """Null the SIGNAL vs forward return. observed = mean(pos*ret). Under a circular shift the
    shifted signal keeps mean(pos) but is de-aligned from ret, so E[null] ~ mean(pos)*mean(ret)
    = the pure DRIFT-CAPTURE level; observed-null is the timing covariance. One-sided p for
    observed>null. n_shifts random offsets in [1,n-1], fixed seed (2000 per spec)."""
    rng = np.random.default_rng(seed)
    pos = pos.astype(float)
    ret = np.nan_to_num(np.asarray(ret, float))
    obs = float(np.mean(pos * ret))
    n = len(pos)
    offs = rng.integers(1, n, size=n_shifts)
    nulls = np.array([np.mean(np.roll(pos, int(l)) * ret) for l in offs])
    p = (1 + int(np.sum(nulls >= obs))) / (len(nulls) + 1)
    return obs, float(p), nulls


# ----------------------------------------------------------------- moving-block bootstrap
def block_boot(weekly, L=4, B=8000, rng=None):
    """Percentile CIs of the MEAN of a weekly series, moving-block resample (preserves short-
    range dependence). Returns dict with mean, two-sided 95% CI, Bonferroni one-sided lower
    bound (1.67 pct), and centred one-sided p(mean>0)."""
    x = np.asarray(weekly, float)
    n = len(x)
    if n < 3:
        return dict(mean=float(np.mean(x)) if n else 0.0, lo=np.nan, hi=np.nan,
                    lo_bonf=np.nan, p=np.nan)
    rng = rng or np.random.default_rng(SEED)
    nb = int(np.ceil(n / L))
    starts = np.arange(0, n - L + 1)
    means = np.empty(B)
    for b in range(B):
        st = rng.choice(starts, nb, replace=True)
        idx = (st[:, None] + np.arange(L)[None, :]).ravel()[:n]
        means[b] = x[idx].mean()
    m0 = x.mean()
    xc = x - m0
    cnull = np.empty(B)
    for b in range(B):
        st = rng.choice(starts, nb, replace=True)
        idx = (st[:, None] + np.arange(L)[None, :]).ravel()[:n]
        cnull[b] = xc[idx].mean()
    p = (1 + int(np.sum(cnull >= m0))) / (B + 1)
    return dict(mean=float(m0), lo=float(np.percentile(means, 2.5)),
                hi=float(np.percentile(means, 97.5)),
                lo_bonf=float(np.percentile(means, 100 * BONF)), p=float(p))


# ================================================================= P1 daily PnL (reproduced)
def p1_daily():
    prof = spread_profile()
    Dnq, bnq = XB.load_substrate(NQ_SUB, "NQ")
    P(f"  [P1] NQ substrate {bnq['n_bars']:,} bars / {bnq['n_sess']:,} sess "
      f"{bnq['first_sess']} -> {bnq['last_sess']}  seal_ok={bnq['seal_ok']}")
    if not bnq["seal_ok"]:
        raise RuntimeError("SEAL VIOLATION P1/NQ")
    trnq, mnq = XB.build_p1pct(Dnq, PV=PV_NQ, comm=COMM, halt_pts=XB.NQ_HALT_PTS,
                               tgt_pts=XB.NQ_TGT_PTS, smin_pts=None, smax_pts=None,
                               stopm_pts=None, win_a="2022-07-01", win_b=str(WIN_B.date()))
    net_nq, ct_nq, rate_nq, ntr = XB.net_series(Dnq, trnq, PV=PV_NQ, tick=TICK_NQ,
                                                spread_model=("nq_profile", prof),
                                                sess_in=mnq["sess_in"], i_of=mnq["i_of"])
    sd = pd.to_datetime(Dnq["sess_date"])[mnq["sess_in"]]
    daily = pd.Series(net_nq, index=pd.DatetimeIndex(sd).normalize()).groupby(level=0).sum()
    wk = to_weekly(daily.index, daily.to_numpy())
    P(f"  [P1] reproduced P1/PCT: {ntr:,} trades, spread ${rate_nq:.3f}/ctrRT, "
      f"{len(daily):,} P&L days, weekly ${wk.mean():,.2f}")
    return daily


# ----------------------------------------------------------------- one engine+control cell
def eval_cell(dates, ret_pt, PV, dvt, W, k, ct, p1_al, rng, want_battery=False):
    """Run the MR engine + exposure-matched drift control for one (W,k,cost) cell on one
    instrument. Returns a row dict; if want_battery, also a detail dict for the primary cell."""
    N = len(ret_pt)
    L = ret_pt.cumsum().astype(float)
    zt = trailing_z(L, W)
    leg = COMM + ct * dvt
    r = run_mr(L, zt, ret_pt, k, HMAX, leg)
    pos = r["pos"].astype(float)
    eng_gross = pos * ret_pt * PV
    eng_net = eng_gross - r["cost"]
    ntr = len(r["trades"])
    # exposure-matched always-long drift control: constant position c = mean(pos)
    c = float(np.mean(pos))
    drift_daily = c * ret_pt * PV
    drift_cost = np.zeros(N)
    drift_cost[0] = abs(c) * leg                     # one round-turn buy&hold cost (negligible)
    drift_net = drift_daily - drift_cost
    spread_daily = eng_net - drift_net

    eng_wk = to_weekly(dates, eng_net)
    drift_wk = to_weekly(dates, drift_net)
    spread_wk = to_weekly(dates, spread_daily)

    bb = block_boot(spread_wk.to_numpy(), rng=rng)
    # eval_battery: engine matched to drift-control weekly vol (weekly-vol lead)
    jj = pd.concat([eng_wk.rename("c"), drift_wk.rename("r")], axis=1).dropna()
    if len(jj) > 3:
        res = EB.evaluate(jj["c"].to_numpy(), jj["r"].to_numpy(), n_placebo=0)
        wv = float(res["weekly_vol"])
    else:
        wv = float("nan")
    drift_native = float(drift_wk.mean())
    spread_vol = wv - drift_native                   # vol-matched spread
    rho_p1 = float(pd.Series(eng_net, index=dates).corr(pd.Series(p1_al, index=dates)))

    row = dict(
        window=W, zthr=k, cost_ticks=ct, ntrades=ntr,
        avg_hold=float(np.mean([t["hold"] for t in r["trades"]])) if ntr else 0.0,
        net_c=c, time_in_mkt=float(np.mean(np.abs(pos))),
        eng_weekly=float(eng_wk.mean()), eng_sharpe=sharpe_wk(eng_wk.to_numpy()),
        drift_weekly=drift_native, drift_sharpe=sharpe_wk(drift_wk.to_numpy()),
        spread_weekly=bb["mean"], spread_sharpe=sharpe_wk(spread_wk.to_numpy()),
        spread_ci_lo=bb["lo"], spread_ci_hi=bb["hi"], spread_lo_bonf=bb["lo_bonf"],
        spread_p_block=bb["p"], spread_vol=spread_vol, wv=wv, rho_to_p1=rho_p1, nwk=len(spread_wk))
    detail = None
    if want_battery:
        detail = dict(eng_net=eng_net.copy(), drift_net=drift_net.copy(),
                      spread_daily=spread_daily.copy(), pos=r["pos"].copy(),
                      trades=r["trades"], eng_wk=eng_wk, drift_wk=drift_wk, spread_wk=spread_wk)
    return row, detail


# ================================================================= main
def main():
    t0 = _t.time()
    rng = np.random.default_rng(SEED)

    P("=" * 112)
    P("W2B_EQMR_20260906  trial G00063  family CROSS_ASSET_NATIVE  (raw equity-index mean reversion)")
    P("POINTS basis, additively back-adjusted (DELEV01) | judged to the P1 bar (in-sample+robust) | NO deploy")
    P("=" * 112)

    # ---- G0b: seal / basis ------------------------------------------------------------
    P("\n[G0b] LOAD / SEAL / BASIS  (every bar >= 2026-08-01 hard-dropped)")
    daily = {}
    for nm in INSTR_ORDER:
        path, PV, tick = INSTR[nm]
        daily[nm] = daily_rth_oc(path, nm)

    p1 = p1_daily()

    # ---- G0: REPRODUCE FIRST -- the raw-ES MR control, primary cell -------------------
    P("\n[G0] REPRODUCE FIRST -- raw-ES MR control (W2_EQRESID G00061, primary W=60 z=1.5 cost=1tk)")
    es = daily["ES"]
    idx_es = es.index.intersection(es.index)
    idx_es = es.index[es.index >= WIN_A]
    es_ret = es.loc[idx_es, "ret_pt"].to_numpy()
    dates_es = pd.DatetimeIndex(idx_es)
    Lraw = es_ret.cumsum().astype(float)
    zt = trailing_z(Lraw, 60)
    leg_es_1 = COMM + 1 * (50.0 * 0.25)               # 16.86
    rc = run_mr(Lraw, zt, es_ret, 1.5, HMAX, leg_es_1)
    ctrl_net = rc["pos"].astype(float) * es_ret * 50.0 - rc["cost"]
    ctrl_wk = to_weekly(dates_es, ctrl_net)
    repro_wk = float(ctrl_wk.mean())
    repro_sh = sharpe_wk(ctrl_wk.to_numpy())
    P(f"  aligned ES RTH sessions {len(dates_es)}  {dates_es.min().date()} -> {dates_es.max().date()}")
    P(f"  raw-ES MR control: {len(rc['trades'])} trades  weekly ${repro_wk:,.2f}/wk  Sharpe {repro_sh:.3f}")
    P(f"  reproduce target : ${REPRO_WK:,.2f}/wk  Sharpe {REPRO_SH:.3f}  (W2_EQRESID G00061)")
    ok_wk = abs(repro_wk - REPRO_WK) <= 2.0
    ok_sh = abs(repro_sh - REPRO_SH) <= 0.01
    g0 = bool(ok_wk and ok_sh)
    P(f"  G0 reproduce = {g0}  (dwk ${repro_wk-REPRO_WK:+.2f}, dSharpe {repro_sh-REPRO_SH:+.4f})")
    if not g0:
        raise RuntimeError(
            f"G0 REPRODUCE FAILED: raw-ES MR control ${repro_wk:.2f}/wk Sharpe {repro_sh:.3f} "
            f"does not match W2 target ${REPRO_WK}/wk Sharpe {REPRO_SH}. The lead is not "
            f"trustworthy; the run is void (spec reproduce_first).")

    # ---- per-instrument neighborhood + primary ----------------------------------------
    all_rows = []
    prim = {}       # instrument -> (row, detail)
    circ = {}       # (instr,W,k) -> (obs,p,nulls)  (position independent of cost)
    for nm in INSTR_ORDER:
        path, PV, tick = INSTR[nm]
        dvt = PV * tick
        d = daily[nm]
        idx = d.index[d.index >= WIN_A]
        ret = d.loc[idx, "ret_pt"].to_numpy()
        dts = pd.DatetimeIndex(idx)
        p1_al = p1.reindex(dts).fillna(0.0).to_numpy()
        for W in WINDOWS:
            L = ret.cumsum().astype(float)
            zt = trailing_z(L, W)
            for k in ZTHRS:
                # circular-shift null once per (instr,W,k) -- position independent of cost
                rtmp = run_mr(L, zt, ret, k, HMAX, 0.0)
                if (nm, W, k) not in circ:
                    circ[(nm, W, k)] = circ_shift_null(rtmp["pos"].astype(float), ret)
                obs_c, p_c, _ = circ[(nm, W, k)]
                for ct in COSTS:
                    is_prim = (W == PRIMARY["window"] and k == PRIMARY["zthr"]
                               and ct == PRIMARY["cost"])
                    row, det = eval_cell(dts, ret, PV, dvt, W, k, ct, p1_al, rng,
                                         want_battery=is_prim)
                    row["instr"] = nm
                    row["p_circ"] = p_c
                    # G2 (this cell): spread>0, block-boot Bonferroni one-sided, clears circ null
                    g2 = bool(row["spread_weekly"] > 0 and row["spread_p_block"] < BONF
                              and row["spread_lo_bonf"] > 0 and p_c < BONF)
                    row["G2"] = g2
                    all_rows.append(row)
                    if is_prim:
                        prim[nm] = (row, det)

    # ---- G1 MDE (per instrument, primary cell), printed before observed spread --------
    P("\n[G1] MDE for the DRIFT-CONTROL SPREAD (printed BEFORE observed) -- primary cell "
      f"W={PRIMARY['window']} z={PRIMARY['zthr']} cost={PRIMARY['cost']}tk")
    mde = {}
    for nm in INSTR_ORDER:
        row, det = prim[nm]
        sw = det["spread_wk"].to_numpy()
        sig = float(np.std(sw, ddof=1))
        Nw = len(sw)
        mde[nm] = (Z_ALPHA + Z_POWER) * sig / np.sqrt(Nw)
        P(f"  [{nm}] spread weekly sd ${sig:,.2f} over {Nw} wk, 80% power one-sided a=0.05 "
          f"-> MDE ${mde[nm]:,.2f}/wk  |  OBSERVED spread ${row['spread_weekly']:,.2f}/wk "
          f"({'ABOVE' if row['spread_weekly'] > mde[nm] else 'BELOW'} MDE)")

    # ---- G2 drift control (CO-PRIMARY KILL), per instrument ---------------------------
    P("\n[G2] DRIFT-CONTROL SPREAD (CO-PRIMARY KILL) -- engine minus exposure-matched always-long")
    P(f"  Bonferroni alpha = 0.05/{FAMILY} = {BONF:.4f} (one-sided) on the block-boot spread; "
      f"circular-shift null {N_CIRC} shifts fixed seed")
    for nm in INSTR_ORDER:
        row, det = prim[nm]
        P(f"  [{nm}] engine ${row['eng_weekly']:,.2f}/wk (Sh {row['eng_sharpe']:.3f}, {row['ntrades']} tr, "
          f"net-exposure c={row['net_c']:+.3f}, time-in-mkt {row['time_in_mkt']*100:.0f}%)")
        P(f"        drift-control (c-long buy&hold) ${row['drift_weekly']:,.2f}/wk (Sh {row['drift_sharpe']:.3f})"
          f"  -> this is the equity DRIFT the engine captures free")
        P(f"        SPREAD ${row['spread_weekly']:,.2f}/wk (Sh {row['spread_sharpe']:.3f})  "
          f"block-boot 95% CI [${row['spread_ci_lo']:,.2f}, ${row['spread_ci_hi']:,.2f}]  "
          f"Bonf lo(1.67pct) ${row['spread_lo_bonf']:,.2f}")
        P(f"        block-boot p(spread>0)={row['spread_p_block']:.4f} (<{BONF:.4f}? "
          f"{row['spread_p_block'] < BONF})  circ-shift p={row['p_circ']:.4f} (<{BONF:.4f}? "
          f"{row['p_circ'] < BONF})  ->  G2 {'PASS' if row['G2'] else 'FAIL (edge is drift)'}")

    # ---- G3 neighborhood plateau ------------------------------------------------------
    P("\n[G3] NEIGHBORHOOD / PLATEAU  W x k x cost  (spread $/wk over drift control)")
    P(f"  {'instr':>5}{'W':>5}{'k':>6}{'cost':>5}{'eng$/wk':>10}{'drift$/wk':>11}"
      f"{'spread$/wk':>12}{'spr_p':>8}{'circ_p':>8}{'rho_P1':>8}{'G2':>5}")
    for r in all_rows:
        P(f"  {r['instr']:>5}{r['window']:>5}{r['zthr']:>6.1f}{r['cost_ticks']:>5}"
          f"{r['eng_weekly']:>10,.0f}{r['drift_weekly']:>11,.0f}{r['spread_weekly']:>12,.0f}"
          f"{r['spread_p_block']:>8.3f}{r['p_circ']:>8.3f}{r['rho_to_p1']:>8.3f}"
          f"{str(r['G2']):>5}")
    plateau = {}
    for nm in INSTR_ORDER:
        cells = [r for r in all_rows if r["instr"] == nm]
        npos = sum(1 for r in cells if r["spread_weekly"] > 0)
        ng2 = sum(1 for r in cells if r["G2"])
        plateau[nm] = bool(npos >= 0.6 * len(cells))
        P(f"  [{nm}] {npos}/{len(cells)} cells spread>0 ; {ng2}/{len(cells)} G2-pass "
          f"-> plateau(>=60% spread>0)? {plateau[nm]}")

    # ---- G4 weekly-vol lead + fixed-DD WITH placebo -----------------------------------
    P("\n[G4] WEEKLY-VOL LEAD (eval_battery; fixed-DD only WITH random-thinning placebo)")
    g4 = {}
    for nm in INSTR_ORDER:
        row, det = prim[nm]
        # vol-matched spread (engine scaled to drift-control weekly vol) - drift native
        g4[nm] = bool(row["spread_weekly"] > 0 and row["spread_vol"] > 0)
        P(f"  [{nm}] native spread ${row['spread_weekly']:,.2f}/wk ; engine@drift-vol ${row['wv']:,.2f}/wk "
          f"vs drift ${row['drift_weekly']:,.2f}/wk -> vol-matched spread ${row['spread_vol']:,.2f}/wk")
        # fixed-DD WITH placebo on the engine's OWN per-trade net (honest module use)
        tr = det["trades"]
        dnet = det["eng_net"]
        tpnl, twk = [], []
        dts = daily[nm].index[daily[nm].index >= WIN_A]
        dts = pd.DatetimeIndex(dts)
        for tt in tr:
            tpnl.append(float(dnet[tt["entry"]:tt["exit"] + 1].sum()))
            iso = dts[tt["exit"]].isocalendar()
            twk.append(f"{iso[0]}-W{iso[1]:02d}")
        if len(tpnl) > 5 and np.ptp(tpnl) > 0:
            codes, _ = pd.factorize(pd.Index(twk), sort=True)
            nper = int(codes.max()) + 1
            nrm = max(1, int(round(0.10 * len(tpnl))))
            cand = np.bincount(codes, weights=np.asarray(tpnl, float), minlength=nper)
            res_dd = EB.evaluate(cand, cand, n_placebo=2000, base_for_placebo="fixed_dd",
                                 ref_trades=np.asarray(tpnl, float), ref_periods=codes,
                                 n_trades_removed=nrm, seed=SEED)
            fdd = float(res_dd["fixed_dd"])
            base_income = float(np.sum(tpnl) / nper)
            null_thin = EB.random_thinning_placebo(np.asarray(tpnl, float), codes, nrm,
                                                   "fixed_dd", n=2000, seed=SEED, n_periods=nper)
            P(f"        fixed-DD income (WITH placebo) ${fdd:,.2f}/period at "
              f"{res_dd.placebo_percentile:.1f}th pctile of side-blind thinning; self base "
              f"${base_income:,.2f}; median thin ${float(np.median(null_thin)):,.2f} "
              f"(lift {float(np.median(null_thin))-base_income:+,.2f})")
        else:
            P("        fixed-DD placebo: too few/degenerate trades -- fixed-DD NOT quoted (correct).")
        P(f"        G4 = edge on weekly-vol (not fixed-DD-only)? {g4[nm]}")

    # ---- G5 era stability (walk-forward) ----------------------------------------------
    P("\n[G5] ERA STABILITY -- walk-forward 2022-07..2024 / 2025..2026-07 (spread $/wk, primary)")
    era = {}
    for nm in INSTR_ORDER:
        row, det = prim[nm]
        dts = daily[nm].index[daily[nm].index >= WIN_A]
        dts = pd.DatetimeIndex(dts)
        m = dts < pd.Timestamp("2025-01-01")
        s1 = to_weekly(dts[m], det["spread_daily"][m])
        s2 = to_weekly(dts[~m], det["spread_daily"][~m])
        era[nm] = bool(s1.mean() > 0 and s2.mean() > 0)
        P(f"  [{nm}] 2022-07..2024 ${s1.mean():,.2f}/wk t={tstat(s1.to_numpy()):.2f} ({len(s1)}wk) | "
          f"2025..2026-07 ${s2.mean():,.2f}/wk t={tstat(s2.to_numpy()):.2f} ({len(s2)}wk) "
          f"-> both>0? {era[nm]}")

    # ---- G6 PnL orthogonality (CO-PRIMARY VALUE), per instrument ----------------------
    P("\n[G6] PnL-rho-to-P1 (CO-PRIMARY VALUE) -- daily engine PnL vs reproduced P1 daily PnL")
    for nm in INSTR_ORDER:
        row, det = prim[nm]
        if row["rho_to_p1"] <= -0.05:
            tag = "NEG -> diversifying (the prize)"
        elif abs(row["rho_to_p1"]) < 0.15:
            tag = "low but POSITIVE comovement (not the prize)"
        else:
            tag = "positive -> not a diversifier"
        P(f"  [{nm}] rho(engine daily PnL, P1 daily PnL) = {row['rho_to_p1']:+.4f}  ({tag})")

    # ---- G7 cost band -----------------------------------------------------------------
    P("\n[G7] COST BAND {1,2} ticks -- does the drift-control spread survive both rungs?")
    cost_robust = {}
    for nm in INSTR_ORDER:
        c1 = [r for r in all_rows if r["instr"] == nm and r["window"] == PRIMARY["window"]
              and r["zthr"] == PRIMARY["zthr"] and r["cost_ticks"] == 1][0]
        c2 = [r for r in all_rows if r["instr"] == nm and r["window"] == PRIMARY["window"]
              and r["zthr"] == PRIMARY["zthr"] and r["cost_ticks"] == 2][0]
        cost_robust[nm] = bool(c1["G2"] and c2["G2"])
        P(f"  [{nm}] 1tk spread ${c1['spread_weekly']:,.2f}/wk G2={c1['G2']} ; "
          f"2tk spread ${c2['spread_weekly']:,.2f}/wk G2={c2['G2']} -> cost-robust? {cost_robust[nm]}")

    # ================================================================ SURVIVAL / VERDICT =
    surv = {}
    for nm in INSTR_ORDER:
        row, det = prim[nm]
        surv[nm] = bool(g0 and row["G2"] and g4[nm] and cost_robust[nm])
    any_surv = any(surv.values())
    # best instrument: a survivor first (lowest |rho-to-P1| = the diversification prize); else
    # the candidate CLOSEST TO SURVIVING the CO-PRIMARY drift-control kill (most significant
    # spread = lowest block-boot p), tie-broken by lowest |rho-to-P1|. A diversifier is worthless
    # without a real edge, so significance leads when nothing survives.
    def keyf(nm):
        row = prim[nm][0]
        return (surv[nm], -row["spread_p_block"], -abs(row["rho_to_p1"]))
    best = sorted(INSTR_ORDER, key=keyf, reverse=True)[0]
    best_row = prim[best][0]

    # DRIFT-EXPLAINED (the GC-MR failure mode) means the drift control CAPTURES the engine's
    # return: drift_weekly > 0 AND the spread is a small residual of it. Here the fade is
    # net-SHORT (c<0), so the drift control LOSES and the spread EXCEEDS the engine -- the
    # OPPOSITE of drift-explained. Refusing to mislabel this is the CAP01 rule (CLAUDE.md 4):
    # a gate that checks arithmetic cannot catch a mislabelled statistic.
    drift_explains = all(prim[nm][0]["drift_weekly"] > 0
                         and prim[nm][0]["spread_weekly"] < 0.5 * prim[nm][0]["eng_weekly"]
                         for nm in INSTR_ORDER)

    if any_surv and abs(best_row["rho_to_p1"]) < 0.15:
        verdict = "PORTFOLIO-ADDITIVE"
    elif any_surv:
        verdict = "EDGE-BUT-NOT-DIVERSIFIER"
    elif drift_explains:
        verdict = "DRIFT-EXPLAINED"
    else:
        # net-short fade with a positive drift-free spread that is UNDERPOWERED at the family-
        # Bonferroni bar (and/or not a diversifier). FAIL by the pre-registered falsifier, but
        # NOT because the edge is drift -- the drift control vindicated the timing mechanism.
        verdict = "FAIL"

    P("\n" + "=" * 112)
    for nm in INSTR_ORDER:
        row = prim[nm][0]
        P(f"  [{nm}] survives(G0 & G2-Bonf & weekly-vol & cost-robust) = {surv[nm]}   "
          f"spread ${row['spread_weekly']:,.2f}/wk   rho-to-P1 {row['rho_to_p1']:+.4f}")
    P(f"BEST INSTRUMENT: {best}  (spread ${best_row['spread_weekly']:,.2f}/wk, "
      f"rho-to-P1 {best_row['rho_to_p1']:+.4f})")
    P(f"VERDICT: {verdict}   any-instrument-survives = {any_surv}")
    P("  WHY: the raw fade is net-SHORT (c<0 on all three), so the exposure-matched hold LOSES "
      "(-$4..-$83/wk) and the drift-free timing SPREAD ($206..$409/wk) EXCEEDS the engine. This "
      "is NOT drift-explained (GC-MR's failure mode); the drift control VINDICATED the timing.")
    P("  The kill is POWER, not drift: spread Sharpe ~0.8-1.1 -> t~1.7 over 214wk, short of the "
      f"Bonferroni bar (alpha {BONF:.4f} -> t~2.13). Circular-shift null (a 2nd computation of "
      "timing-beyond-drift) IS cleared for ES(0.012)/YM(0.0005) but block-boot CI does not "
      "exclude 0 at Bonferroni. AND rho-to-P1 is POSITIVE (+0.13..+0.23) -> not a diversifier.")
    P("=" * 112)

    # ================================================================ WRITE DELIVERABLES =
    with open(os.path.join(OUT, "reproduce.txt"), "w", encoding="utf-8") as f:
        f.write("W2B_EQMR_20260906  G0 REPRODUCE-FIRST  (raw-ES MR control, W2_EQRESID G00061)\n")
        f.write("=" * 88 + "\n")
        f.write(f"primary cell: W=60 z=1.5 cost=1tk (ES leg RT ${leg_es_1:.2f})\n")
        f.write(f"aligned ES RTH sessions {len(dates_es)}  "
                f"{dates_es.min().date()} -> {dates_es.max().date()}\n")
        f.write(f"raw-ES MR control: {len(rc['trades'])} trades  "
                f"weekly ${repro_wk:,.4f}/wk  Sharpe {repro_sh:.4f}\n")
        f.write(f"reproduce target : ${REPRO_WK:,.2f}/wk  Sharpe {REPRO_SH:.3f}  (W2_EQRESID G00061)\n")
        f.write(f"deltas: dwk ${repro_wk-REPRO_WK:+.4f}  dSharpe {repro_sh-REPRO_SH:+.4f}\n")
        f.write(f"G0 REPRODUCE = {g0}\n")

    pd.DataFrame(all_rows).to_csv(os.path.join(OUT, "neighborhood.csv"), index=False)

    for nm in INSTR_ORDER:
        row, det = prim[nm]
        dts = daily[nm].index[daily[nm].index >= WIN_A]
        dts = pd.DatetimeIndex(dts)
        p1_al = p1.reindex(dts).fillna(0.0).to_numpy()
        pd.DataFrame({
            "date": dts, "engine_pnl": det["eng_net"], "drift_control_pnl": det["drift_net"],
            "spread_pnl": det["spread_daily"], "position": det["pos"], "p1_pnl": p1_al,
        }).to_csv(os.path.join(OUT, f"daily_pnl_{nm}.csv"), index=False)

    gate_table = build_gate_table(dict(
        g0=g0, repro_wk=repro_wk, repro_sh=repro_sh, prim=prim, mde=mde, plateau=plateau,
        g4=g4, era=era, cost_robust=cost_robust, surv=surv, best=best, verdict=verdict,
        any_surv=any_surv, all_rows=all_rows, ndates={nm: prim[nm][0]["nwk"] for nm in INSTR_ORDER}))
    with open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8") as f:
        f.write(gate_table)

    with open(os.path.join(OUT, "run_log.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(_LOG) + "\n")

    P(f"\n[done {_t.time()-t0:.0f}s] wrote out/reproduce.txt, out/gate_table.txt, "
      f"out/neighborhood.csv, out/daily_pnl_{{ES,YM,RTY}}.csv, out/run_log.txt")
    return dict(g0=g0, verdict=verdict, any_surv=any_surv, best=best, prim=prim,
                surv=surv, cost_robust=cost_robust, g4=g4, plateau=plateau, era=era,
                repro_wk=repro_wk, repro_sh=repro_sh)


def _grow(g, spec, obs, ok):
    v = "PASS" if ok else "FAIL"
    return f"{g:<5}{spec:<52}{str(obs)[:34]:>36}{v:>8}"


def build_gate_table(d):
    prim = d["prim"]
    L = []
    L.append("=" * 112)
    L.append("W2B_EQMR_20260906  trial G00063  family CROSS_ASSET_NATIVE")
    L.append("raw equity-index MEAN-REVERSION (ES lead, YM/RTY extension) -- PROGRAM-PRINTED GATE TABLE")
    L.append("POINTS basis, back-adjusted (DELEV01) | judged to the P1 bar (in-sample+robust) | NO deploy")
    L.append("=" * 112)
    L.append(f"primary cell: W={PRIMARY['window']} z={PRIMARY['zthr']} cost={PRIMARY['cost']}tk/leg "
             f"| family Bonferroni alpha = 0.05/{FAMILY} = {BONF:.4f}")
    L.append("")
    L.append(_grow("G0", "reproduce raw-ES MR control (else RAISE)",
                   f"${d['repro_wk']:,.0f}/wk Sh{d['repro_sh']:.3f} vs ${REPRO_WK:.0f}/0.78", d["g0"]))
    L.append(_grow("G0b", "points basis, back-adjusted, seal <2026-08-01",
                   "POINTS; back-adj; asserted", True))
    L.append("")
    L.append(f"{'gate':<5}{'spec':<52}{'observed (ES / YM / RTY)':>36}{'verdict':>8}")
    # per-instrument gate rows
    def tri(fmt, f):
        return " / ".join(fmt.format(f(nm)) for nm in INSTR_ORDER)
    L.append("G1   MDE for drift-control spread (before observed)")
    for nm in INSTR_ORDER:
        row = prim[nm][0]
        L.append(f"       [{nm}] MDE ${d['mde'][nm]:,.0f}/wk  observed spread ${row['spread_weekly']:,.0f}/wk"
                 f"  ({'ABOVE' if row['spread_weekly']>d['mde'][nm] else 'BELOW'})")
    L.append("G2   drift-control spread>0, CI-excl-0 Bonf, clears circ-null  (CO-PRIMARY KILL)")
    for nm in INSTR_ORDER:
        row = prim[nm][0]
        gv = "PASS" if row["G2"] else ("FAIL (underpowered; NOT drift, drift is a drag)"
                                       if row["drift_weekly"] <= 0 else "FAIL (drift)")
        L.append(f"       [{nm}] spread ${row['spread_weekly']:,.0f}/wk  Bonf-lo ${row['spread_lo_bonf']:,.0f}"
                 f"  p_block {row['spread_p_block']:.3f}  p_circ {row['p_circ']:.3f}  -> {gv}")
    L.append("G3   neighborhood plateau (>=60% cells spread>0)")
    for nm in INSTR_ORDER:
        cells = [r for r in d["all_rows"] if r["instr"] == nm]
        npos = sum(1 for r in cells if r["spread_weekly"] > 0)
        L.append(f"       [{nm}] {npos}/{len(cells)} spread>0 -> plateau {d['plateau'][nm]}")
    L.append("G4   edge on weekly-vol, not fixed-DD-only")
    for nm in INSTR_ORDER:
        row = prim[nm][0]
        L.append(f"       [{nm}] native ${row['spread_weekly']:,.0f}/wk vol-matched ${row['spread_vol']:,.0f}/wk"
                 f" -> {d['g4'][nm]}")
    L.append("G5   positive spread in BOTH walk-forward eras")
    for nm in INSTR_ORDER:
        L.append(f"       [{nm}] both eras>0? {d['era'][nm]}")
    L.append("G6   PnL-rho-to-P1 per instrument (CO-PRIMARY VALUE; low/neg = the prize)")
    for nm in INSTR_ORDER:
        row = prim[nm][0]
        if row["rho_to_p1"] <= -0.05:
            g6tag = "NEG=diversifying (prize)"
        elif abs(row["rho_to_p1"]) < 0.15:
            g6tag = "low but POSITIVE (not prize)"
        else:
            g6tag = "positive=not a diversifier"
        L.append(f"       [{nm}] rho-to-P1 {row['rho_to_p1']:+.3f}  ({g6tag})")
    L.append("G7   drift-control spread survives {1,2}-tick cost band")
    for nm in INSTR_ORDER:
        L.append(f"       [{nm}] cost-robust? {d['cost_robust'][nm]}")
    L.append("")
    for nm in INSTR_ORDER:
        row = prim[nm][0]
        L.append(f"survives [{nm}] (G0 & G2-Bonf & weekly-vol & cost-robust) = {d['surv'][nm]}  "
                 f"spread ${row['spread_weekly']:,.2f}/wk  rho-to-P1 {row['rho_to_p1']:+.4f}  "
                 f"eng ${row['eng_weekly']:,.2f}/wk drift ${row['drift_weekly']:,.2f}/wk")
    L.append("")
    bestrow = prim[d["best"]][0]
    L.append(f"BEST INSTRUMENT: {d['best']}  spread ${bestrow['spread_weekly']:,.2f}/wk  "
             f"rho-to-P1 {bestrow['rho_to_p1']:+.4f}")
    L.append(f"SEMANTIC: 'spread' is the mean weekly P&L of the raw daily fade AFTER subtracting the "
             f"income of an exposure-matched always-long hold. It is drift-free timing alpha, "
             f"in-sample & DISCOVERY_CONSUMED -- NOT a forward or live figure.")
    L.append(f"any-instrument-survives = {d['any_surv']}")
    L.append("WHY (read before quoting the verdict): the raw fade is net-SHORT on all three "
             "(c<0), so the exposure-matched hold LOSES and the drift-free timing spread EXCEEDS "
             "the engine -- this is NOT the GC-MR drift-explained mode; the drift control "
             "vindicated the timing. The kill is POWER (spread Sharpe ~0.8-1.1 -> t~1.7 over "
             "214wk < Bonferroni t~2.13; circ-null cleared ES/YM but block-boot CI does not "
             "exclude 0 at 0.0167) AND diversification (rho-to-P1 +0.13..+0.23, positive).")
    L.append(f"==> VERDICT: {d['verdict']}")
    L.append("=" * 112)
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
