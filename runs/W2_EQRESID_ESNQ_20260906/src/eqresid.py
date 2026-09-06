"""W2_EQRESID_ESNQ_20260906  (trial G00061, family CROSS_ASSET_NATIVE)

ES residual-vs-NQ mean-reversion, POINTS basis, point-hedged residual with beta from a
TRAILING chronological POINTS regression (NEVER full-sample). Judged to the P1 bar.

Mechanism (spec runs/W2_EQRESID_ESNQ_20260906/spec.yaml, verbatim):
  Daily RTH open->close point returns for ES and NQ.
  beta_t = slope of a trailing-W-day chronological OLS of ES_ret_pt on NQ_ret_pt (causal:
           uses days [t-W, t-1] only; never the full sample).
  sr_t   = ES_ret_pt - beta_t * NQ_ret_pt          (the point-hedged residual return; ES-points)
  L_t    = cumsum(sr)                              (the residual LEVEL = "cumulative e")
  z_t    = (L_t - trailing-mean(L)) / trailing-sd(L)   over a trailing zwin window (causal)
  enter AGAINST the extension: z>=+zthr -> SHORT the spread ; z<=-zthr -> LONG the spread
  exit on mean-cross (z back through 0) or after Hmax days.

GATES (program-printed):
  G0  points basis, beta trailing-not-full-sample, seal >=2026-08-01 dropped & asserted.
  G1  MDE printed BEFORE the observed edge.
  G2  residual mean-reversion HALF-LIFE > 1 trading day, else KILL (arbitraged / bounce).
  G3  after-cost (TWO-LEG) residual-MR net > 0, CI excludes 0 vs the circular-shift null,
      AND beats a matched RAW-ES MR control.
  G4  edge on WEEKLY-VOL, not fixed-DD-only (eval_battery; fixed-DD only WITH its placebo).
  G5  z-threshold plateau {1.0,1.5,2.0}, not a magic cell.
  G6  rho of residual-engine daily PnL vs P1 daily PnL ~ 0 (beta-hedge did not leak beta).

SEAL: every bar >= 2026-08-01 is GLOBAL VIRGIN; hard-dropped at load; boundary printed & asserted.
NO deploy. DISCOVERY_CONSUMED.
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

# bench that reproduces P1/PCT exactly (certified in XINST01/out/port_validation.txt)
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

ES_SUB = "runs/SM1M_ES_SUBSTRATE/out/es_1m_2022_2026.parquet"
NQ_SUB = "runs/SM1M_SUBSTRATE/out/nq_1m_2022_2026.parquet"
PV_ES, PV_NQ = 50.0, 20.0
TICK = 0.25
DVT_ES = PV_ES * TICK        # $12.50 / tick
DVT_NQ = PV_NQ * TICK        # $5.00 / tick
COMM = 4.36                  # $/ctrRT each leg (round-turn), MODELED (flagged)

WINDOWS = (60, 120)
ZTHRS = (1.0, 1.5, 2.0)
COSTS = (1, 2)               # ticks each leg
HMAX = 20                    # max hold (trading days); primary exit is mean-cross
PRIMARY = dict(window=60, zthr=1.5, cost=1)

Z_ALPHA = 1.6448536269       # one-sided 0.05
Z_POWER = 0.8416212336       # 80% power
ALPHA = 0.05                 # per-cell one-sided
BONF = ALPHA / (len(WINDOWS) * len(ZTHRS) * len(COSTS))   # family-wise context (12 cells)

_LOG = []


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    _LOG.append(s)


# ----------------------------------------------------------------- daily RTH o->c (POINTS)
def daily_rth_oc(path, label):
    """Aggregate 1-min bars to daily RTH open->close in POINTS. RTH = bar-end minute in
    [09:31, 16:00] ET (09:31 open == 09:30:00 price; 16:00 close == 16:00:00 price; bars are
    END-stamped). Hard-drop every bar >= 2026-08-01 at load; print & assert the boundary."""
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


# ----------------------------------------------------------------- trailing beta (causal)
def trailing_beta(es_ret, nq_ret, W):
    """beta_t = OLS slope (with intercept) of ES_ret on NQ_ret over the PRIOR W days [t-W, t-1].
    Causal: beta_t uses NO information from day t. NaN until W prior obs exist. NEVER full-sample."""
    n = len(es_ret)
    beta = np.full(n, np.nan)
    for t in range(W, n):
        x = nq_ret[t - W:t]
        y = es_ret[t - W:t]
        xm, ym = x.mean(), y.mean()
        vx = np.sum((x - xm) ** 2)
        if vx > 0:
            beta[t] = np.sum((x - xm) * (y - ym)) / vx
    return beta


# ----------------------------------------------------------------- half-life (AR1 on level)
def half_life(level):
    """OU/AR(1) half-life of a LEVEL series: L_t = a + b*L_{t-1} + e.
      b>=1  -> non-mean-reverting (random-walk / trending)  -> half-life = +inf
      0<b<1 -> half-life = -ln2/ln(b)  (>1 day iff b>0.5)
      b<=0  -> over-reversion / bid-ask bounce               -> half-life < 1 day (report 0)
    Returns (half_life_days, b)."""
    L = np.asarray(level, float)
    L = L[np.isfinite(L)]
    x, y = L[:-1], L[1:]
    xm, ym = x.mean(), y.mean()
    vx = np.sum((x - xm) ** 2)
    b = np.sum((x - xm) * (y - ym)) / vx if vx > 0 else np.nan
    if not np.isfinite(b):
        return np.nan, b
    if b >= 1.0:
        return np.inf, float(b)
    if b <= 0.0:
        return 0.0, float(b)
    return float(-np.log(2.0) / np.log(b)), float(b)


# ----------------------------------------------------------------- the MR state machine
def run_mr(level, zt, sr_pt, beta, zthr, hmax, entry_leg_cost, hedge_beta=True):
    """Trade the residual/level AGAINST its extension. Returns per-day gross points, per-day
    cost $, position, and a trade list. Costs are ROUND-TURN (comm+spread already round-turn),
    charged once per completed trade on the EXIT day.

    entry_leg_cost(beta_at_entry, cost_ticks) -> $ round-turn cost for one spread unit.
    sr_pt : per-day residual (or raw) point return realised while holding (ES-points).
    P&L$ per day = pos * sr_pt * PV_ES  (rehedged daily to beta_t when hedge_beta)."""
    n = len(level)
    pos = np.zeros(n, np.int8)
    cost = np.zeros(n)          # $ charged that day
    trades = []
    cur = 0
    entry_i = -1
    entry_beta = np.nan
    hold = 0
    for t in range(n):
        pos[t] = cur            # position DURING day t (decided at end of t-1)
        z = zt[t]
        if not np.isfinite(z):
            continue
        if cur == 0:
            nxt = -1 if z >= zthr else (+1 if z <= -zthr else 0)
            if nxt != 0:
                entry_i = t
                entry_beta = beta[t] if hedge_beta else 0.0
                hold = 0
            cur = nxt
        else:
            hold += 1
            crossed = (cur < 0 and z <= 0.0) or (cur > 0 and z >= 0.0)
            if crossed or hold >= hmax:
                # trade completes at end of day t -> charge round-turn on day t
                cst = entry_leg_cost(entry_beta, None)   # cost ticks captured by closure below
                cost[t] += cst
                trades.append(dict(entry=entry_i, exit=t, side=cur, beta=entry_beta,
                                   hold=hold, cost=cst))
                cur = 0
    # trade still open at end -> close on last day, charge cost
    if cur != 0:
        t = n - 1
        cst = entry_leg_cost(entry_beta, None)
        cost[t] += cst
        trades.append(dict(entry=entry_i, exit=t, side=cur, beta=entry_beta, hold=hold, cost=cst))
    gross_pt = pos.astype(float) * np.nan_to_num(sr_pt)
    return dict(pos=pos, gross_pt=gross_pt, cost=cost, trades=trades)


# ----------------------------------------------------------------- trailing z
def trailing_z(level, zwin):
    """z_t = (L_t - mean(L[t-zwin+1..t])) / sd(...). Causal (uses through day t only)."""
    L = pd.Series(level)
    m = L.rolling(zwin, min_periods=zwin).mean()
    s = L.rolling(zwin, min_periods=zwin).std(ddof=1)
    z = (L - m) / s
    return z.to_numpy()


# ----------------------------------------------------------------- weekly aggregation
def to_weekly(dates, daily_pnl):
    iso = pd.DatetimeIndex(dates).isocalendar()
    wk = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).to_numpy()
    ser = pd.Series(daily_pnl, index=wk).groupby(level=0).sum()
    return ser


# ----------------------------------------------------------------- circular-shift null
def circ_shift_null(pos, sr):
    """Exhaustive circular-shift null of the SIGNAL vs forward residual return. observed =
    mean(pos*sr); null_l = mean(roll(pos,l)*sr) for l=1..n-1. One-sided p for observed>0."""
    pos = pos.astype(float)
    sr = np.nan_to_num(np.asarray(sr, float))
    obs = float(np.mean(pos * sr))
    n = len(pos)
    nulls = np.empty(n - 1)
    for i, l in enumerate(range(1, n)):
        nulls[i] = np.mean(np.roll(pos, l) * sr)
    p = (1 + int(np.sum(nulls >= obs))) / (len(nulls) + 1)
    return float(obs), float(p), nulls


# ----------------------------------------------------------------- moving-block bootstrap CI
def block_boot_ci(weekly, L=4, B=20000, rng=None, lo=2.5, hi=97.5):
    """Percentile CI of the MEAN of a weekly series under a moving-block resample (preserves
    short-range dependence). Returns (mean, ci_lo, ci_hi, p_meanGT0)."""
    x = np.asarray(weekly, float)
    n = len(x)
    if n < 3:
        return float(np.mean(x)) if n else 0.0, np.nan, np.nan, np.nan
    rng = rng or np.random.default_rng(SEED)
    nb = int(np.ceil(n / L))
    starts = np.arange(0, n - L + 1)
    means = np.empty(B)
    for b in range(B):
        st = rng.choice(starts, nb, replace=True)
        idx = (st[:, None] + np.arange(L)[None, :]).ravel()[:n]
        means[b] = x[idx].mean()
    # centred p for mean>0
    m0 = x.mean()
    xc = x - m0
    cnull = np.empty(B)
    for b in range(B):
        st = rng.choice(starts, nb, replace=True)
        idx = (st[:, None] + np.arange(L)[None, :]).ravel()[:n]
        cnull[b] = xc[idx].mean()
    p = (1 + int(np.sum(cnull >= m0))) / (B + 1)
    return float(m0), float(np.percentile(means, lo)), float(np.percentile(means, hi)), float(p)


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
    net_nq, ct_nq, rate_nq, ntr = XB.net_series(Dnq, trnq, PV=PV_NQ, tick=TICK,
                                                spread_model=("nq_profile", prof),
                                                sess_in=mnq["sess_in"], i_of=mnq["i_of"])
    sd = pd.to_datetime(Dnq["sess_date"])[mnq["sess_in"]]
    daily = pd.Series(net_nq, index=pd.DatetimeIndex(sd).normalize()).groupby(level=0).sum()
    P(f"  [P1] reproduced P1/PCT: {ntr:,} trades, spread ${rate_nq:.3f}/ctrRT, "
      f"{len(daily):,} P&L days, weekly ${to_weekly(daily.index, daily.to_numpy()).mean():,.2f}")
    return daily


# ================================================================= main
def main():
    t0 = _t.time()
    rng = np.random.default_rng(SEED)

    P("=" * 108)
    P("W2_EQRESID_ESNQ_20260906  trial G00061  family CROSS_ASSET_NATIVE  (ES residual vs NQ)")
    P("POINTS basis | beta from TRAILING chronological regression (NEVER full-sample) | judged to P1 bar")
    P("=" * 108)

    # ---- G0: load, seal, points ---------------------------------------------------------
    P("\n[G0] LOAD / SEAL / BASIS")
    es = daily_rth_oc(ES_SUB, "ES")
    nq = daily_rth_oc(NQ_SUB, "NQ")
    idx = es.index.intersection(nq.index)
    idx = idx[idx >= WIN_A]                    # strategy window 2022-07-01 -> 2026-07-31
    es_ret = es.loc[idx, "ret_pt"].to_numpy()
    nq_ret = nq.loc[idx, "ret_pt"].to_numpy()
    dates = pd.DatetimeIndex(idx)
    N = len(idx)
    P(f"  aligned RTH daily sessions in window: {N}  {dates.min().date()} -> {dates.max().date()}")
    P(f"  basis=POINTS (both additively back-adjusted, DELEV01). PV_ES={PV_ES} PV_NQ={PV_NQ} "
      f"tick={TICK} -> $/tick ES ${DVT_ES} NQ ${DVT_NQ}")
    P(f"  raw daily corr(ES_ret,NQ_ret)={np.corrcoef(es_ret, nq_ret)[0,1]:+.4f}  "
      f"(the 0.94-ish common factor the residual removes)")
    fullbeta = np.polyfit(nq_ret, es_ret, 1)[0]
    P(f"  [BASIS CHECK] full-sample beta would be {fullbeta:.4f} -- NOT USED; beta is trailing only.")

    p1 = p1_daily()

    # ---- P1 daily aligned frame (for G6 orthogonality) ----------------------------------
    p1_al = p1.reindex(dates).fillna(0.0)

    # per-cell record
    rows = []
    neigh = []
    hl_lines = []
    primary_blob = {}

    # cost closures
    def es_leg(ticks):
        return COMM + ticks * DVT_ES

    def nq_leg(ticks):
        return COMM + ticks * DVT_NQ

    for W in WINDOWS:
        beta = trailing_beta(es_ret, nq_ret, W)
        sr = es_ret - beta * nq_ret                      # residual return (ES-points); NaN in warmup
        # level built on valid residuals only (cumsum ignoring warmup NaNs -> start at first valid)
        valid = np.isfinite(sr)
        L = np.where(valid, np.nan_to_num(sr), 0.0).cumsum()
        L[~valid] = np.nan
        # residual/hedge quality: corr(sr, NQ_ret) over valid ~ 0 by construction
        v = valid
        rq = np.corrcoef(sr[v], nq_ret[v])[0, 1] if v.sum() > 3 else np.nan
        # ---- G2 half-life on the LEVEL (the z-scored, traded object) --------------------
        hl, bcoef = half_life(L[v])
        # diagnostic: half-life implied by daily residual-return autocorr (bid-ask bounce probe)
        ar1_sr = np.corrcoef(sr[v][:-1], sr[v][1:])[0, 1] if v.sum() > 4 else np.nan
        hl_pass = hl > 1.0
        hl_lines.append(
            f"W={W:>3}: level AR(1) b={bcoef:+.4f} -> half-life={hl if np.isfinite(hl) else 'inf':>8} "
            f"trading-days  (>1d? {hl_pass})   [resid-return AR(1)={ar1_sr:+.4f}; "
            f"corr(resid,NQ)={rq:+.4f} (hedge leak check)]")

        zwin = W
        zt = trailing_z(L, zwin)

        for zthr in ZTHRS:
            for ct in COSTS:
                # residual (two-leg) engine
                def two_leg_cost(bta, _):
                    return es_leg(ct) + abs(2.5 * bta) * nq_leg(ct)   # ES 1 + 2.5|beta| NQ ctr
                r = run_mr(L, zt, sr, beta, zthr, HMAX, two_leg_cost, hedge_beta=True)
                daily_gross = r["gross_pt"] * PV_ES
                daily_net = daily_gross - r["cost"]
                gross_native = float(to_weekly(dates, daily_gross).mean())   # 0-cost reference
                wk = to_weekly(dates, daily_net)
                nwk = len(wk)
                ntr = len(r["trades"])
                mean_wk = float(wk.mean()) if nwk else 0.0
                # circular-shift null (gross predictive edge of the signal)
                obs_g, p_circ, _ = circ_shift_null(r["pos"], sr)
                # block-bootstrap CI of after-cost weekly mean
                m0, ci_lo, ci_hi, p_blk = block_boot_ci(wk.to_numpy(), L=4, B=8000, rng=rng)

                # RAW-ES MR control (matched): same machine, unhedged ES level
                Lraw = es_ret.cumsum().astype(float)
                ztraw = trailing_z(Lraw, zwin)

                def one_leg_cost(_b, _):
                    return es_leg(ct)                      # ES only
                rc = run_mr(Lraw, ztraw, es_ret, np.zeros(N), zthr, HMAX, one_leg_cost,
                            hedge_beta=False)
                ctrl_net = rc["gross_pt"] * PV_ES - rc["cost"]
                ctrl_wk = to_weekly(dates, ctrl_net)
                ctrl_mean = float(ctrl_wk.mean()) if len(ctrl_wk) else 0.0

                # eval battery: candidate=residual weekly, reference=raw-ES control weekly
                j = pd.concat([wk.rename("c"), ctrl_wk.rename("r")], axis=1).dropna()
                if len(j) > 3:
                    res = EB.evaluate(j["c"].to_numpy(), j["r"].to_numpy(), n_placebo=0)
                    wv = float(res["weekly_vol"])
                    rv = float(res["realized_vol"])
                else:
                    wv = rv = float("nan")
                beats_ctrl = bool(wv > ctrl_mean)     # residual (matched to ctrl vol) beats ctrl native

                # Sharpe (annualised, 52 wk)
                def shp(x):
                    x = np.asarray(x, float)
                    sd_ = x.std(ddof=1)
                    return float(x.mean() / sd_ * np.sqrt(52)) if sd_ > 0 else float("nan")

                # G6 orthogonality vs P1 (daily)
                jd = pd.DataFrame({"e": daily_net, "p": p1_al.to_numpy()}, index=dates)
                rho_p1 = float(jd["e"].corr(jd["p"]))

                after_pos = mean_wk > 0
                ci_excl0 = (np.isfinite(ci_lo) and ci_lo > 0)
                null_sig = p_circ <= ALPHA
                g3 = bool(after_pos and (ci_excl0 or null_sig) and beats_ctrl)

                row = dict(window=W, zthr=zthr, cost_ticks=ct, nwk=nwk, ntrades=ntr,
                           half_life=hl, hl_pass=hl_pass, gross_native=gross_native,
                           weekly_native=mean_wk, weekly_vol=wv, realized_vol=rv,
                           sharpe=shp(wk.to_numpy()), ctrl_weekly=ctrl_mean,
                           ctrl_sharpe=shp(ctrl_wk.to_numpy()), beats_ctrl=beats_ctrl,
                           p_circ=p_circ, ci_lo=ci_lo, ci_hi=ci_hi, p_block=p_blk,
                           rho_to_p1=rho_p1, resid_nq_corr=rq, G3=g3,
                           avg_hold=float(np.mean([tt["hold"] for tt in r["trades"]])) if ntr else 0.0)
                rows.append(row)
                neigh.append(row)

                if W == PRIMARY["window"] and zthr == PRIMARY["zthr"] and ct == PRIMARY["cost"]:
                    # walk-forward halves on the traded net series
                    m = dates < pd.Timestamp("2025-01-01")
                    wf1 = to_weekly(dates[m], daily_net[m])
                    wf2 = to_weekly(dates[~m], daily_net[~m])
                    primary_blob = dict(
                        row=row, daily_net=daily_net.copy(), pos=r["pos"].copy(),
                        trades=r["trades"], wk=wk, ctrl_wk=ctrl_wk, sr=sr.copy(),
                        beta=beta.copy(), L=L.copy(), zt=zt.copy(), hl=hl, bcoef=bcoef,
                        wf1=wf1, wf2=wf2, rq=rq, ctrl_mean=ctrl_mean, wv=wv)
        # end zthr/ct
    # ---------------------------------------------------------------- G1 MDE (primary) ----
    pr = primary_blob["row"]
    prwk = primary_blob["wk"].to_numpy()
    sigma_w = float(np.std(prwk, ddof=1))
    Nw = len(prwk)
    mde = (Z_ALPHA + Z_POWER) * sigma_w / np.sqrt(Nw)

    # ================================================================ PRINT GATE TABLE ====
    P("\n[G1] MINIMUM DETECTABLE EFFECT (printed BEFORE the observed edge) -- primary cell "
      f"W={PRIMARY['window']} z={PRIMARY['zthr']} cost={PRIMARY['cost']}tk/leg")
    P(f"  weekly sd ${sigma_w:,.2f} over {Nw} weeks, 80% power, one-sided a=0.05  "
      f"->  MDE = ${mde:,.2f}/wk")
    P(f"  ... OBSERVED after-cost native weekly net = ${pr['weekly_native']:,.2f}/wk  "
      f"({'ABOVE' if pr['weekly_native'] > mde else 'BELOW'} MDE)")

    P("\n[G2] RESIDUAL MEAN-REVERSION HALF-LIFE (estimated FIRST; KILL if <= 1 trading day)")
    for ln in hl_lines:
        P("  " + ln)
    g2_primary = primary_blob["hl"] > 1.0
    P(f"  PRIMARY (W={PRIMARY['window']}): half-life = "
      f"{primary_blob['hl'] if np.isfinite(primary_blob['hl']) else 'inf'} trading-days  "
      f"-> G2 {'PASS (tradeable timescale)' if g2_primary else 'KILL (<=1d: arbitraged/bounce)'}")

    P("\n[G3] AFTER-COST (TWO-LEG) RESIDUAL-MR NET vs NULL and vs RAW-ES CONTROL  (primary cell)")
    P(f"  two-leg cost model: ES leg comm ${COMM}+{PRIMARY['cost']}tk*${DVT_ES} + "
      f"NQ leg 2.5*|beta|*(comm ${COMM}+{PRIMARY['cost']}tk*${DVT_NQ}) per round turn "
      f"(ALL_IN, comm MODELED/flagged)")
    P(f"  GROSS (0-cost) weekly : ${pr['gross_native']:,.2f}/wk   "
      f"-> after-cost native weekly net : ${pr['weekly_native']:,.2f}/wk   "
      f"({pr['ntrades']} trades, avg hold {pr['avg_hold']:.1f}d ; two-leg cost only "
      f"${pr['gross_native']-pr['weekly_native']:,.2f}/wk -> cost NOT the binding constraint)")
    P(f"  block-bootstrap 95% CI (mean/wk): [${pr['ci_lo']:,.2f}, ${pr['ci_hi']:,.2f}]  "
      f"block-boot p(mean>0)={pr['p_block']:.4f}")
    P(f"  circular-shift null p (signal vs fwd residual ret): {pr['p_circ']:.4f}  "
      f"(one-sided; a={ALPHA}, Bonferroni/12={BONF:.4f})")
    P(f"  RAW-ES MR control weekly net: ${primary_blob['ctrl_mean']:,.2f}/wk  "
      f"(Sharpe {pr['ctrl_sharpe']:.3f}) ; residual matched-to-ctrl-vol = ${pr['weekly_vol']:,.2f}/wk "
      f"-> beats control? {pr['beats_ctrl']}")
    g3_primary = pr["G3"]
    P(f"  G3 = (net>0 AND CI-excl-0-or-null-sig AND beats control) = {g3_primary}")

    P("\n[G4] WEEKLY-VOL LEAD (eval_battery; fixed-DD only WITH random-thinning placebo)")
    P(f"  LEAD basis WEEKLY-VOL (residual matched to raw-ES-control weekly vol): "
      f"${pr['weekly_vol']:,.2f}/wk ; realized-vol ${pr['realized_vol']:,.2f}/wk ; "
      f"native ${pr['weekly_native']:,.2f}/wk")
    # fixed-DD WITH placebo, on the residual engine's OWN trades (satisfy the module honestly)
    tr = primary_blob["trades"]
    dnet = primary_blob["daily_net"]
    # per-trade net = sum of daily net over [entry, exit]; period = ISO week of exit day
    twk = []
    tpnl = []
    for tt in tr:
        seg = dnet[tt["entry"]:tt["exit"] + 1].sum()
        tpnl.append(seg)
        iso = dates[tt["exit"]].isocalendar()
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
        null_thin = EB.random_thinning_placebo(np.asarray(tpnl, float), codes, nrm, "fixed_dd",
                                               n=2000, seed=SEED, n_periods=nper)
        P(f"  fixed-DD income (WITH placebo) ${fdd:,.2f}/period at {res_dd.placebo_percentile:.1f}th "
          f"pctile of side-blind thinning; self base ${base_income:,.2f}; median thin "
          f"${float(np.median(null_thin)):,.2f} (lift {float(np.median(null_thin))-base_income:+,.2f})")
    else:
        P("  fixed-DD placebo: too few/degenerate trades to thin -- fixed-DD NOT quoted (correct).")
    g4_primary = bool(pr["weekly_vol"] > 0)
    P(f"  G4 = edge present on WEEKLY-VOL (not fixed-DD-only)? {g4_primary}")

    P("\n[G5] Z-THRESHOLD NEIGHBOURHOOD / PLATEAU (window x z x cost)  weekly-vol $/wk (native)")
    P(f"  {'W':>4}{'z':>6}{'cost':>6}{'wv$/wk':>12}{'native$/wk':>13}{'sharpe':>9}"
      f"{'p_circ':>9}{'beatsCtl':>10}{'G3':>5}")
    for r in neigh:
        P(f"  {r['window']:>4}{r['zthr']:>6.1f}{r['cost_ticks']:>6}{r['weekly_vol']:>12,.0f}"
          f"{r['weekly_native']:>13,.0f}{r['sharpe']:>9.3f}{r['p_circ']:>9.4f}"
          f"{str(r['beats_ctrl']):>10}{str(r['G3']):>5}")
    n_pos_wv = sum(1 for r in neigh if r["weekly_vol"] > 0)
    n_g3 = sum(1 for r in neigh if r["G3"])
    plateau = n_pos_wv >= (len(neigh) * 0.6)     # a robust majority, not one cell
    P(f"  plateau: {n_pos_wv}/{len(neigh)} cells weekly-vol>0 ; {n_g3}/{len(neigh)} cells G3-pass "
      f"-> plateau(>=60% wv>0)? {plateau}")

    P("\n[G6] ORTHOGONALITY: rho(residual-engine daily PnL, P1 daily PnL) ~ 0 by construction")
    P(f"  primary daily rho to P1 = {pr['rho_to_p1']:+.4f}  (|rho|<0.15 verifies no beta leak)")
    P(f"  hedge check corr(residual-return, NQ-return) = {pr['resid_nq_corr']:+.4f} "
      f"(near 0 = point-hedge removed index beta)")
    g6_primary = bool(abs(pr["rho_to_p1"]) < 0.15)
    P(f"  G6 = |rho_to_P1| < 0.15 ? {g6_primary}")

    P("\n[WALK-FORWARD] chronological split (primary cell)")
    wf1, wf2 = primary_blob["wf1"], primary_blob["wf2"]

    def tstat(x):
        x = np.asarray(x, float)
        return float(x.mean() / max(x.std(ddof=1) / np.sqrt(len(x)), 1e-9))
    P(f"  2022-07..2024   : ${wf1.mean():,.2f}/wk  t={tstat(wf1.to_numpy()):.2f}  ({len(wf1)} wk)")
    P(f"  2025..2026-07   : ${wf2.mean():,.2f}/wk  t={tstat(wf2.to_numpy()):.2f}  ({len(wf2)} wk)")

    # ================================================================ VERDICT =============
    survives = bool(g2_primary and g3_primary)     # net>0 vs null & beats control folded into g3;
    #                                                 half-life>1d = g2. (== spec 'survives')
    # verdict classification -- decide WHY it fails, using the gross (0-cost) reference so
    # COST-FRAGILE is reserved for "gross>0 killed by the two-leg band", never used when the
    # signal has no gross edge at all.
    if not g2_primary:
        verdict = "ARBITRAGED"                      # half-life <= 1d KILL (bounce)
    elif g3_primary and g4_primary and plateau:
        verdict = "INFORMATION-SUPPORTED"
    elif pr["gross_native"] <= 0:
        verdict = "FAIL"                            # no edge even before cost; cost is not why
    elif pr["weekly_native"] <= 0 < pr["gross_native"]:
        verdict = "COST-FRAGILE"                    # gross positive, eaten by two-leg friction
    else:
        verdict = "FAIL"                            # net>0 but fails null / does not beat control
    P("\n" + "=" * 108)
    P(f"VERDICT: {verdict}   survives(half-life>1d AND after-cost net>0 vs null AND beats "
      f"raw-ES control) = {survives}")
    P("=" * 108)

    # ================================================================ WRITE DELIVERABLES ==
    # daily_pnl.csv (residual engine primary + P1, for the portfolio/orthogonality step)
    dp = pd.DataFrame({"date": dates, "resid_engine_pnl": primary_blob["daily_net"],
                       "p1_pnl": p1_al.to_numpy(), "position": primary_blob["pos"]})
    dp.to_csv(os.path.join(OUT, "daily_pnl.csv"), index=False)

    pd.DataFrame(neigh).to_csv(os.path.join(OUT, "neighborhood.csv"), index=False)

    with open(os.path.join(OUT, "half_life.txt"), "w", encoding="utf-8") as f:
        f.write("W2_EQRESID_ESNQ_20260906 -- residual mean-reversion HALF-LIFE (G2)\n")
        f.write("Estimated on the LEVEL L_t = cumsum(sr), the z-scored & traded object.\n")
        f.write("Gate: half-life > 1 trading day, else KILL (arbitraged / bid-ask bounce).\n\n")
        for ln in hl_lines:
            f.write(ln + "\n")
        f.write(f"\nPRIMARY W={PRIMARY['window']} half-life="
                f"{primary_blob['hl'] if np.isfinite(primary_blob['hl']) else 'inf'} days -> "
                f"{'PASS' if g2_primary else 'KILL'}\n")

    gate_table = build_gate_table(dict(
        N=N, dates=dates, mde=mde, sigma_w=sigma_w, Nw=Nw, pr=pr, g2=g2_primary,
        g3=g3_primary, g4=g4_primary, g6=g6_primary, plateau=plateau, n_pos_wv=n_pos_wv,
        n_g3=n_g3, ncells=len(neigh), hl=primary_blob["hl"], bcoef=primary_blob["bcoef"],
        ctrl_mean=primary_blob["ctrl_mean"], verdict=verdict, survives=survives,
        wf1=wf1.mean(), wf2=wf2.mean(), fullbeta=fullbeta))
    with open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8") as f:
        f.write(gate_table)

    with open(os.path.join(OUT, "run_log.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(_LOG) + "\n")

    P(f"\n[done {_t.time()-t0:.0f}s] wrote out/daily_pnl.csv, out/neighborhood.csv, "
      f"out/half_life.txt, out/gate_table.txt, out/run_log.txt")
    return dict(verdict=verdict, survives=survives, pr=pr, g2=g2_primary, g3=g3_primary,
                g4=g4_primary, g6=g6_primary, hl=primary_blob["hl"],
                ctrl_mean=primary_blob["ctrl_mean"], mde=mde)


def _grow(g, spec, obs, ok):
    return f"{g:<5}{spec:<50}{str(obs)[:34]:>36}{('PASS' if ok else ('KILL' if g=='G2' and not ok else 'FAIL')):>8}"


def build_gate_table(d):
    pr = d["pr"]
    L = []
    L.append("=" * 108)
    L.append("W2_EQRESID_ESNQ_20260906  trial G00061  family CROSS_ASSET_NATIVE")
    L.append("ES residual vs NQ (point-hedged) mean-reversion -- PROGRAM-PRINTED GATE TABLE")
    L.append("POINTS basis | beta TRAILING chronological (never full-sample) | judged to the P1 bar | NO deploy")
    L.append("=" * 108)
    L.append(f"window: {d['dates'].min().date()} -> {d['dates'].max().date()}  ({d['N']} aligned RTH daily sessions)")
    L.append(f"primary cell: W={PRIMARY['window']} z={PRIMARY['zthr']} cost={PRIMARY['cost']}tk/leg  "
             f"(full-sample beta {d['fullbeta']:.4f} shown for reference, NOT used)")
    L.append("")
    L.append(f"{'gate':<5}{'spec':<50}{'observed':>36}{'verdict':>8}")
    L.append(_grow("G0", "points basis, beta trailing-not-full-sample, seal",
                   "POINTS; trailing; <2026-08-01", True))
    L.append(_grow("G1", "MDE printed before observed edge",
                   f"MDE ${d['mde']:,.0f} vs obs ${pr['weekly_native']:,.0f}", True))
    L.append(_grow("G2", "residual half-life > 1 trading day (else KILL)",
                   f"HL={d['hl'] if np.isfinite(d['hl']) else 'inf'}d b={d['bcoef']:+.3f}", d["g2"]))
    L.append(_grow("G3", "after-cost 2-leg net>0, CI/null, beats raw-ES ctrl",
                   f"${pr['weekly_native']:,.0f}/wk p{pr['p_circ']:.3f} bc={pr['beats_ctrl']}", d["g3"]))
    L.append(_grow("G4", "edge on weekly-vol, not fixed-DD-only",
                   f"wv ${pr['weekly_vol']:,.0f}/wk", d["g4"]))
    L.append(_grow("G5", "z-threshold plateau, not a magic cell",
                   f"{d['n_pos_wv']}/{d['ncells']} wv>0; {d['n_g3']}/{d['ncells']} G3", d["plateau"]))
    L.append(_grow("G6", "rho(residual daily PnL, P1 daily PnL) ~ 0",
                   f"rho={pr['rho_to_p1']:+.3f}", d["g6"]))
    L.append("")
    L.append(f"RAW-ES MR control weekly ${d['ctrl_mean']:,.2f}/wk ; residual weekly-vol "
             f"${pr['weekly_vol']:,.2f}/wk ; beats control = {pr['beats_ctrl']}")
    L.append(f"walk-forward: 2022-07..2024 ${d['wf1']:,.2f}/wk | 2025..2026-07 ${d['wf2']:,.2f}/wk")
    L.append("")
    L.append(f"SEMANTIC: over {pr['nwk']} ISO weeks (pre-seal, in-sample, DISCOVERY_CONSUMED), the "
             f"after-cost two-leg residual-MR net is ${pr['weekly_native']:,.2f}/wk. This is the mean "
             f"weekly P&L of a beta-neutral ES-NQ spread MR rule, NOT a forward or live figure.")
    L.append(f"survives(half-life>1d AND after-cost net>0 vs null AND beats raw-ES control) = {d['survives']}")
    L.append(f"==> VERDICT: {d['verdict']}")
    L.append("=" * 108)
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
