# -*- coding: utf-8 -*-
"""W2C_CL_MR_20260906  --  CL short-horizon / multi-day MEAN-REVERSION falsifier.

Preregistered spec: runs/W2C_CL_MR_20260906/spec.yaml  (ledger trial G00065, family
CROSS_ASSET_NATIVE). Judged TO THE P1 BAR. NO DEPLOY. Evidence status DISCOVERY_CONSUMED.

WHAT THIS DOES (exactly the spec)
---------------------------------
Mechanism ...... FADE the extension of the trailing-W daily point-return. signal = z-score of
                 the trailing-W point return R_W,t = P_t - P_{t-W} (W in {5,10}); enter SHORT
                 when z >= +k, LONG when z <= -k (k in {1,1.5,2}); exit on z mean-cross (z back
                 through 0) or a max-hold of H days (H in {2,5}). One round trip per trade
                 (continuous hold -> the "daily hold -> low turnover" the spec assumes). The
                 1-day analog (W=1) is reported as a within-run coherence check.
Data ........... runs/SM1M_CL_SUBSTRATE/out/cl_1m_2022_2026.parquet, aggregated to daily on TWO
                 close bases (POINTS, additively back-adjusted -- DELEV01; CL tick $0.01, PV
                 $1000/pt, $10/tick):
                   PIT  = 14:30 ET pit settlement close (native CL pit 09:00-14:30 per the
                          CL autopsy runs/CROSSASSET_W1_CL_AUTOPSY_20260906/); r = settle-to-settle.
                   FULL = full 24h session close (18:00->17:00 ET); r = close-to-close.
                 SEE the DEVIATION note in REPORT.md on the "o->c" wording: a literal intraday
                 o->c day-trade would cost H round trips per H-day hold, contradicting the
                 spec's own "low turnover" premise, so pit is realized settle-to-settle (the
                 autopsy's own multi-day MR series) and the intraday pit o->c is a diagnostic.
Controls ....... G2 co-primary EDGE = after-cost SPREAD over an EXPOSURE-MATCHED DRIFT CONTROL
                 (constant position = the strategy's mean net exposure; earns the drift, has no
                 timing). Block-bootstrap CI on the weekly spread must EXCLUDE 0, AND the spread
                 must clear a 2000-shift CIRCULAR-SHIFT null (fixed seed 20260906).
                 G6 co-primary = PnL-rho-to-P1 (P1 daily PnL reproduced from the XINST01 bench).
Cost ........... ALL_IN = $4.36/ctrRT commission (MODELED, flagged) + ASSUMED spread {0.5,1,2}
                 ticks x $10/tick. Band reported; realistic rung = 1 tick ($14.36 ALL_IN).
Eval ........... research_sdk.eval_battery, LED BY WEEKLY-VOL; fixed-DD shown ONLY beside its
                 rate-matched random-thinning placebo. Walk-forward 2022-2024 / 2025-2026-07.
Seal ........... >= 2026-08-01 is GLOBAL VIRGIN. The loader hard-drops it and asserts. Nothing
                 dated on/after 2026-08-01 is materialized.

NO order, no strategy enable, no live change. $0.
"""
from __future__ import annotations

import os
import sys
import time as _t

import numpy as np
import pandas as pd

REPO = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
XSRC = os.path.join(REPO, "runs", "XINST01_WEEKLY_EDGE_PORT_20260906", "src")
WESRC = os.path.join(REPO, "research", "weekly_edge", "src")
for p in (XSRC, WESRC, REPO):
    if p not in sys.path:
        sys.path.insert(0, p)

import xinst_bench as XB                                             # noqa: E402
from we_lab import spread_profile                                   # noqa: E402
import research_sdk.eval_battery as EB                              # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "out")
os.makedirs(OUT, exist_ok=True)

# ----------------------------------------------------------------- constants (spec-fixed)
SEED = 20260906
CL_SUB = "runs/SM1M_CL_SUBSTRATE/out/cl_1m_2022_2026.parquet"
NQ_SUB = "runs/SM1M_SUBSTRATE/out/nq_1m_2022_2026.parquet"
WIN_A = "2022-01-03"       # full window start (CL)
WIN_B = "2026-08-01"       # exclusive; == the >=2026-08-01 global virgin seal
CL_PV = 1000.0             # $/point
CL_TICK = 0.01
DV = CL_PV * CL_TICK       # $/tick = 10.0
COMM = 4.36                # MODELED $/ctrRT
SPREAD_TICKS = (0.5, 1.0, 2.0)   # ASSUMED spread band
REALISTIC_TK = 1.0         # realistic rung

WS = (5, 10)               # trailing windows
KS = (1.0, 1.5, 2.0)       # z thresholds
HS = (2, 5)                # max-hold (days)
NORM_N = 100               # z-score normalisation window (FIXED nuisance param, NOT tuned)

# a-priori PRIMARY cell, chosen from the AUTOPSY before any result:
#   the autopsy measured multi-day MR at VR(10)=0.838 / acf(5)=-0.078 -> W=10, reversion
#   horizon ~5d -> H=5, middle threshold k=1.5, on close-to-close returns -> FULL basis.
PRIMARY = dict(basis="FULL", W=10, k=1.5, H=5)

Z_ALPHA = 1.6448536270    # one-sided alpha=0.05
Z_POWER = 0.8416212336    # 80% power

ERA_SPLIT = np.datetime64("2025-01-01")   # walk-forward: 2022-2024 / 2025-2026-07


# ================================================================= daily aggregation
def build_daily(D):
    """From the 1-min substrate D (already seal-dropped by XB.load_substrate) build the two
    daily CLOSE-price series indexed by SESSION DATE, in POINTS.

      PIT  : open of the first pit bar (09:00), close of the last pit bar (14:30 settle).
      FULL : close of the last bar of the whole 18:00->17:00 session.

    Bars are END-stamped, exchange-session time (ET). Pit = end-stamps in [09:01, 14:30]
    (opens 09:00, settles 14:30), per the CL autopsy. Returns a DataFrame indexed by date."""
    t = pd.to_datetime(D["t"])
    mins = (t.hour * 60 + t.minute).to_numpy()
    sid = D["sid"]
    sess_date = pd.to_datetime(D["sess_date"])
    date_of_bar = sess_date[sid]           # each bar -> its trading-session date
    idx = np.arange(len(sid))

    PIT_LO, PIT_HI = 9 * 60 + 1, 14 * 60 + 30
    is_pit = (mins >= PIT_LO) & (mins <= PIT_HI)

    df = pd.DataFrame(dict(date=date_of_bar, idx=idx, o=D["o"], c=D["c"], is_pit=is_pit))
    # FULL close = close of the last bar (max idx) of the date
    full_close = df.loc[df.groupby("date")["idx"].idxmax(), ["date", "c"]].set_index("date")["c"]
    # PIT: first/last pit bar of the date
    pit = df[df.is_pit]
    pit_first = pit.loc[pit.groupby("date")["idx"].idxmin(), ["date", "o"]].set_index("date")["o"]
    pit_last = pit.loc[pit.groupby("date")["idx"].idxmax(), ["date", "c"]].set_index("date")["c"]
    pit_n = pit.groupby("date").size()

    out = pd.DataFrame(index=full_close.index.sort_values())
    out["full_close"] = full_close
    out["pit_open"] = pit_first
    out["pit_close"] = pit_last          # 14:30 settle
    out["pit_nbars"] = pit_n.reindex(out.index).fillna(0).astype(int)
    out["pit_oc"] = out["pit_close"] - out["pit_open"]     # intraday pit o->c (diagnostic)
    return out


def basis_series(daily, basis):
    """Return an ordered (dates, close_price) for the requested execution/signal basis.

    PIT  -> settle close (14:30); only dates with a real pit session (>=250 pit bars).
    FULL -> full-session close; all dates."""
    if basis == "PIT":
        m = daily["pit_nbars"] >= 250
        s = daily.loc[m, "pit_close"].dropna()
    elif basis == "FULL":
        s = daily["full_close"].dropna()
    else:
        raise ValueError(basis)
    s = s.sort_index()
    return s.index.to_numpy(), s.to_numpy(float)


# ================================================================= signal + backtest
def zscore(P, W, N):
    """z-score of the trailing-W point return R_W,t = P_t - P_{t-W}, standardised by the
    rolling mean/std of R_W over the FIXED window N (causal: window ends at t, all known at
    close t). Returns z (NaN during warm-up)."""
    P = np.asarray(P, float)
    R = np.full(len(P), np.nan)
    R[W:] = P[W:] - P[:-W]
    s = pd.Series(R)
    mu = s.rolling(N, min_periods=N).mean()
    sd = s.rolling(N, min_periods=N).std(ddof=1)
    z = (s - mu) / sd
    return z.to_numpy()


def backtest(P, z, k, H, cost):
    """Day-by-day FADE backtest on close price P with z-signal.

    Convention: the position set at close of day i is held to earn day (i+1)'s return.
      pos_d = position DURING day d (earns r_d = P_d - P_{d-1}).
      daily_price_pnl[d] = pos_d * r_d * PV.
    Enter SHORT if z>=+k, LONG if z<=-k (only when flat). Exit on z mean-cross (short: z<=0;
    long: z>=0) OR max-hold H days. One round-trip cost per trade. No re-entry on the exit bar
    (1-bar cooldown) -> low turnover.

    Returns dict with daily arrays (price_pnl, cost_daily, pos) aligned to P, and the trade list."""
    n = len(P)
    r = np.zeros(n)
    r[1:] = P[1:] - P[:-1]
    pos = np.zeros(n)              # position during each day
    price_pnl = np.zeros(n)
    cost_daily = np.zeros(n)
    trades = []
    cur = 0                       # current position side {-1,0,+1}
    entry_i = -1
    held = 0
    for i in range(n):
        # 1) the position carried into day i earns r[i]
        pos[i] = cur
        price_pnl[i] = cur * r[i] * CL_PV
        if np.isnan(z[i]):
            continue
        just_exited = False
        # 2) manage an open position at close of day i
        if cur != 0:
            held += 1
            mean_cross = (cur < 0 and z[i] <= 0) or (cur > 0 and z[i] >= 0)
            max_hold = held >= H
            if mean_cross or max_hold:
                pnl = cur * (P[i] - P[entry_i]) * CL_PV - cost
                trades.append(dict(entry=entry_i, exit=i, side=cur, days=held,
                                   px_pnl=cur * (P[i] - P[entry_i]) * CL_PV, net=pnl,
                                   reason="mean_cross" if mean_cross else "max_hold"))
                cost_daily[i] += cost         # charge the round trip on the exit day
                cur = 0
                entry_i = -1
                held = 0
                just_exited = True
        # 3) fresh entry (not on the exit bar)
        if cur == 0 and not just_exited:
            if z[i] >= k:
                cur = -1
                entry_i = i
                held = 0
            elif z[i] <= -k:
                cur = +1
                entry_i = i
                held = 0
    return dict(pos=pos, price_pnl=price_pnl, cost_daily=cost_daily, trades=trades, r=r)


# ================================================================= weekly / spread helpers
def iso_week(dates):
    s = pd.to_datetime(pd.Series(dates))
    iso = s.dt.isocalendar()
    return (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).to_numpy()


def weekly_sum(dates, daily_vals):
    wk = iso_week(dates)
    ser = pd.Series(daily_vals).groupby(wk).sum()
    return ser


def strat_daily_net(bt, dates):
    """after-cost daily P&L aligned to dates."""
    return bt["price_pnl"] - bt["cost_daily"]


def drift_control_daily(bt):
    """EXPOSURE-MATCHED drift control: a CONSTANT position = mean net exposure, earning the
    market's drift with NO timing and NO cost. control_pnl[d] = mean_pos * r_d * PV."""
    valid = ~np.isnan(bt["pos"])
    mean_pos = float(np.mean(bt["pos"]))     # pos has no NaN (0 during warm-up); mean net exposure
    ctrl = mean_pos * bt["r"] * CL_PV
    return ctrl, mean_pos


def moving_block_ci(x, L=4, B=20000, seed=SEED, lo=2.5, hi=97.5):
    """Moving-block bootstrap CI of the mean of series x."""
    rng = np.random.default_rng(seed)
    x = np.asarray(x, float)
    n = len(x)
    if n < 3:
        return float("nan"), float("nan"), float("nan")
    nb = int(np.ceil(n / L))
    starts = np.arange(0, n - L + 1)
    means = np.empty(B)
    for b in range(B):
        st = rng.choice(starts, nb, replace=True)
        ii = (st[:, None] + np.arange(L)[None, :]).ravel()[:n]
        means[b] = x[ii].mean()
    return float(x.mean()), float(np.percentile(means, lo)), float(np.percentile(means, hi))


def circular_shift_null(pos, r, week_codes, n_weeks, cost_total, obs_weekly_mean,
                        n_shift=2000, seed=SEED):
    """Destroy the signal->forward-return alignment by circularly shifting the POSITION series
    relative to returns (preserves each series' autocorrelation). Recompute the after-cost
    weekly-mean spread under each shift. mean_pos (hence the drift control) is shift-invariant.
    Cost is a near-constant offset (turnover count invariant to a roll) applied as cost_total/T
    per day. One-sided p = (1 + #{null >= obs}) / (n_shift + 1).

    week_codes : integer 0..n_weeks-1 week id for each day (bincount-based aggregation)."""
    rng = np.random.default_rng(seed)
    n = len(pos)
    cost_per_day = cost_total / n
    mean_pos = float(np.mean(pos))
    rpv = r * CL_PV
    base_day = -cost_per_day - mean_pos * rpv     # the shift-invariant part of daily spread
    nulls = np.empty(n_shift)
    offsets = rng.integers(1, n, size=n_shift)
    for j, off in enumerate(offsets):
        sp = np.roll(pos, int(off))
        spread_d = sp * rpv + base_day
        wsum = np.bincount(week_codes, weights=spread_d, minlength=n_weeks)
        nulls[j] = wsum.mean()
    p = (1 + int(np.sum(nulls >= obs_weekly_mean))) / (n_shift + 1)
    return float(p), nulls


# ================================================================= P1 reference (XINST bench)
def reproduce_p1():
    """Reproduce P1 daily PnL from the XINST01 bench (byte-for-byte the STEP-C reproduction)."""
    prof = spread_profile()
    Dnq, bnq = XB.load_substrate(NQ_SUB, "NQ")
    assert bnq["seal_ok"], "NQ seal violation"
    tr, meta = XB.build_p1pct(Dnq, PV=20.0, comm=COMM, halt_pts=XB.NQ_HALT_PTS,
                              tgt_pts=XB.NQ_TGT_PTS, smin_pts=None, smax_pts=None,
                              stopm_pts=None, win_a="2022-07-01", win_b=WIN_B)
    net, ct, rate, ntr = XB.net_series(Dnq, tr, PV=20.0, tick=0.25,
                                       spread_model=("nq_profile", prof),
                                       sess_in=meta["sess_in"], i_of=meta["i_of"])
    sd = pd.to_datetime(Dnq["sess_date"])[meta["sess_in"]]
    p1_daily = pd.Series(net, index=sd.date).groupby(level=0).sum()
    p1_daily.index = pd.to_datetime(p1_daily.index)
    return p1_daily, dict(rate=rate, ntr=ntr, first=str(p1_daily.index.min().date()),
                          last=str(p1_daily.index.max().date()), n=len(p1_daily))


# ================================================================= one cell, full metrics
def eval_cell(dates, P, W, k, H, spread_ticks, p1_weekly=None, full=False):
    """Backtest one (W,k,H) at one cost rung and return the after-cost SPREAD summary. If
    full=True also compute block-boot CI + circular-shift null (heavy) and the eval battery."""
    cost = COMM + spread_ticks * DV
    z = zscore(P, W, NORM_N)
    bt = backtest(P, z, k, H, cost)
    net_daily = strat_daily_net(bt, dates)
    ctrl_daily, mean_pos = drift_control_daily(bt)
    spread_daily = net_daily - ctrl_daily
    # weekly
    wk = iso_week(dates)
    w_net = pd.Series(net_daily).groupby(wk).sum()
    w_ctrl = pd.Series(ctrl_daily).groupby(wk).sum()
    w_spread = pd.Series(spread_daily).groupby(wk).sum()
    w_spread.index = w_net.index
    ntr = len(bt["trades"])
    res = dict(W=W, k=k, H=H, spread_ticks=spread_ticks, cost=cost, ntrades=ntr,
               mean_pos=mean_pos, nweeks=len(w_net),
               raw_weekly=float(w_net.mean()),
               spread_weekly=float(w_spread.mean()),
               spread_daily_arr=spread_daily, net_daily_arr=net_daily,
               ctrl_daily_arr=ctrl_daily, pos_arr=bt["pos"], r_arr=bt["r"],
               trades=bt["trades"], w_spread=w_spread, w_net=w_net, dates=dates)
    if ntr:
        res["avg_hold"] = float(np.mean([t["days"] for t in bt["trades"]]))
        res["win_rate"] = float(np.mean([t["net"] > 0 for t in bt["trades"]]))
    else:
        res["avg_hold"] = 0.0
        res["win_rate"] = 0.0
    return res


def _grow(g, spec, obs, ok):
    v = "PASS" if ok else ("FAIL" if ok is False else str(ok))
    return f"{g:<6}{spec:<50}{str(obs)[:34]:>36}{v:>8}"


# ================================================================= main
def main():
    t0 = _t.time()
    log = []

    def P(*a):
        s = " ".join(str(x) for x in a)
        print(s, flush=True)
        log.append(s)

    P("=" * 108)
    P("W2C_CL_MR_20260906  --  CL short-horizon / multi-day MEAN-REVERSION falsifier (trial G00065)")
    P("  spec: runs/W2C_CL_MR_20260906/spec.yaml   evidence: DISCOVERY_CONSUMED   NO DEPLOY   $0")
    P("=" * 108)

    # ---------- G0: load + SEAL assertion (points basis) ---------------------------------
    Dcl, bnd = XB.load_substrate(CL_SUB, "CL")
    seal_ok = bnd["seal_ok"] and (np.datetime64(bnd["last_sess"]) < np.datetime64("2026-08-01"))
    assert seal_ok, "SEAL VIOLATION: a session on/after 2026-08-01 was materialized"
    P("")
    P(f"G0  substrate CL: {bnd['n_bars']:,} bars / {bnd['n_sess']:,} sessions "
      f"{bnd['first_sess']} -> {bnd['last_sess']}  dropped>=seal {bnd['n_dropped']}")
    P(f"    POINTS basis (additively back-adjusted, DELEV01); PV ${CL_PV:,.0f}/pt, $/tick ${DV:.0f}, tick {CL_TICK}")
    P(f"    SEAL: max session {bnd['last_sess']} < 2026-08-01 ? {seal_ok}   (asserted PASS)")

    daily = build_daily(Dcl)
    P(f"    daily bars: {len(daily)} dates  {daily.index.min().date()} -> {daily.index.max().date()}; "
      f"pit sessions (>=250 bars) {(daily['pit_nbars']>=250).sum()}")

    # ---------- P1 reference (reproduced from the XINST01 bench) --------------------------
    P("")
    P("  reproducing P1 daily PnL from runs/XINST01_WEEKLY_EDGE_PORT_20260906/src/xinst_bench.py ...")
    p1_daily, p1meta = reproduce_p1()
    p1_wk = pd.Series(p1_daily.values, index=iso_week(p1_daily.index.to_numpy()))
    p1_weekly = p1_wk.groupby(level=0).sum()
    P(f"    P1: {p1meta['n']} days {p1meta['first']}->{p1meta['last']}, spread ${p1meta['rate']:.3f}/ctrRT, "
      f"{p1meta['ntr']} trades, weekly-vol ref built  [{_t.time()-t0:.0f}s]")

    # ============================ NEIGHBORHOOD (all cells, both bases, + 1-day analog) ====
    P("")
    P("=" * 108)
    P("NEIGHBORHOOD  (after-cost SPREAD over the exposure-matched drift control, realistic 1-tick cost)")
    P("  cell metrics: raw weekly $, drift-control SPREAD weekly $, block-boot 95% CI on weekly spread,")
    P("  circular-shift null p (2000 shifts, seed 20260906), weekly-vol of spread (matched to P1).")
    P("=" * 108)
    neigh = []
    bases_close = {b: basis_series(daily, b) for b in ("PIT", "FULL")}
    for basis in ("PIT", "FULL"):
        dts, Pc = bases_close[basis]
        wk_codes_b, wk_uniq_b = pd.factorize(iso_week(dts), sort=True)
        n_weeks_b = len(wk_uniq_b)
        for W in (1,) + WS:                     # W=1 is the coherence analog
            for k in KS:
                for H in HS:
                    c = eval_cell(dts, Pc, W, k, H, REALISTIC_TK)
                    # weekly-vol of the spread, matched to P1 (shared ISO weeks)
                    ws = c["w_spread"]
                    j = pd.concat([ws.rename("s"), p1_weekly.rename("p1")], axis=1).dropna()
                    if len(j) > 3 and j["s"].std(ddof=1) > 0:
                        wv = float(EB.evaluate(j["s"].to_numpy(), j["p1"].to_numpy(),
                                               n_placebo=0)["weekly_vol"])
                    else:
                        wv = float("nan")
                    # fast block-boot CI (B=4000) + circ-shift null (2000)
                    m, lo, hi = moving_block_ci(ws.to_numpy(), L=4, B=4000, seed=SEED)
                    cost_total = c["ntrades"] * c["cost"]
                    pnull, _ = circular_shift_null(
                        c["pos_arr"], c["r_arr"], wk_codes_b, n_weeks_b,
                        cost_total, c["spread_weekly"], n_shift=2000, seed=SEED)
                    neigh.append(dict(
                        basis=basis, W=W, k=k, H=H, ntrades=c["ntrades"],
                        avg_hold=round(c["avg_hold"], 2), win_rate=round(c["win_rate"], 3),
                        mean_pos=round(c["mean_pos"], 4), nweeks=c["nweeks"],
                        raw_weekly=round(c["raw_weekly"], 2),
                        spread_weekly=round(c["spread_weekly"], 2),
                        spread_ci_lo=round(lo, 2), spread_ci_hi=round(hi, 2),
                        ci_excl_0=bool(lo > 0),
                        circ_shift_p=round(pnull, 4), clears_null=bool(pnull < 0.05),
                        spread_weekly_vol=round(wv, 2) if np.isfinite(wv) else float("nan"),
                        is_multiday=(W > 1)))
        P(f"  {basis}: {sum(1 for x in neigh if x['basis']==basis)} cells done  [{_t.time()-t0:.0f}s]")

    ndf = pd.DataFrame(neigh)
    ndf.to_csv(os.path.join(OUT, "neighborhood.csv"), index=False)

    # plateau assessment: multi-day (W>1) cells with positive after-cost spread, per basis
    def plateau_stats(basis):
        m = ndf[(ndf.basis == basis) & (ndf.W > 1)]
        pos = (m.spread_weekly > 0).sum()
        ci = (m.ci_excl_0).sum()
        nul = (m.clears_null).sum()
        return len(m), int(pos), int(ci), int(nul)
    P("")
    for basis in ("PIT", "FULL"):
        tot, pos, ci, nul = plateau_stats(basis)
        P(f"  PLATEAU[{basis} multi-day, {tot} cells]: spread>0 in {pos}/{tot} ; "
          f"CI-excludes-0 in {ci}/{tot} ; clears-null in {nul}/{tot}")
    # 1-day vs multi-day coherence (mean spread)
    for basis in ("PIT", "FULL"):
        one = ndf[(ndf.basis == basis) & (ndf.W == 1)]["spread_weekly"].mean()
        multi = ndf[(ndf.basis == basis) & (ndf.W > 1)]["spread_weekly"].mean()
        P(f"  COHERENCE[{basis}]: mean spread 1-day ${one:,.1f}/wk vs multi-day ${multi:,.1f}/wk "
          f"-> multi-day {'>' if multi > one else '<='} 1-day")

    # ============================ PRIMARY cell -- full falsifier ==========================
    P("")
    P("=" * 108)
    P(f"PRIMARY cell (a-priori from the autopsy, BEFORE results): basis={PRIMARY['basis']} "
      f"W={PRIMARY['W']} k={PRIMARY['k']} H={PRIMARY['H']}, realistic 1-tick cost")
    P("=" * 108)
    dts, Pc = bases_close[PRIMARY["basis"]]
    cost = COMM + REALISTIC_TK * DV
    z = zscore(Pc, PRIMARY["W"], NORM_N)
    bt = backtest(Pc, z, PRIMARY["k"], PRIMARY["H"], cost)
    net_daily = strat_daily_net(bt, dts)
    ctrl_daily, mean_pos = drift_control_daily(bt)
    spread_daily = net_daily - ctrl_daily
    wk = iso_week(dts)
    w_net = pd.Series(net_daily).groupby(wk).sum()
    w_ctrl = pd.Series(ctrl_daily).groupby(wk).sum()
    w_spread = pd.Series(spread_daily).groupby(wk).sum()
    w_spread.index = w_net.index
    ntr = len(bt["trades"])
    P(f"  trades {ntr}, avg hold {np.mean([t['days'] for t in bt['trades']]):.2f}d, "
      f"win-rate {np.mean([t['net']>0 for t in bt['trades']]):.3f}, mean net exposure {mean_pos:+.4f}")
    P(f"  raw after-cost weekly ${w_net.mean():,.2f}/wk ; drift-control weekly ${w_ctrl.mean():,.2f}/wk")

    # ---- G1: MDE FIRST (barrier), then observed spread ----------------------------------
    sd_sp = float(np.std(w_spread.to_numpy(), ddof=1))
    nwk = len(w_spread)
    mde = (Z_ALPHA + Z_POWER) * sd_sp / np.sqrt(nwk)
    P("")
    P(f"  G1  MDE for the drift-control SPREAD (80% power, alpha 0.05, weekly-spread sd ${sd_sp:,.0f}, "
      f"{nwk} wk):")
    P(f"      MDE = ${mde:,.2f}/wk   <-- PRINTED BEFORE THE OBSERVED SPREAD (barrier)")
    obs_spread = float(w_spread.mean())
    P(f"      OBSERVED after-cost weekly SPREAD = ${obs_spread:,.2f}/wk "
      f"({'ABOVE' if obs_spread > mde else 'BELOW'} MDE)")

    # ---- G2: spread > 0, block-boot CI excludes 0, clears circular-shift null -----------
    m_ci, ci_lo, ci_hi = moving_block_ci(w_spread.to_numpy(), L=4, B=20000, seed=SEED)
    cost_total = ntr * cost
    wk_codes_p, wk_uniq_p = pd.factorize(iso_week(dts), sort=True)
    pnull, nulls = circular_shift_null(bt["pos"], bt["r"], wk_codes_p, len(wk_uniq_p),
                                       cost_total, obs_spread, n_shift=2000, seed=SEED)
    ci_excl = ci_lo > 0
    clears = pnull < 0.05
    P("")
    P(f"  G2  after-cost SPREAD ${obs_spread:,.2f}/wk ; block-boot 95% CI [${ci_lo:,.2f}, ${ci_hi:,.2f}] "
      f"-> excludes 0 ? {ci_excl}")
    P(f"      circular-shift null (2000 shifts, seed {SEED}): one-sided p = {pnull:.4f} "
      f"-> clears (p<0.05) ? {clears}")
    g2 = bool(obs_spread > 0 and ci_excl and clears)

    # ---- eval battery: weekly-vol lead; fixed-DD ONLY with random-thinning placebo ------
    #      (a) strategy weekly P&L matched to P1's weekly vol
    jn = pd.concat([w_net.rename("cl"), p1_weekly.rename("p1")], axis=1).dropna()
    resb = EB.evaluate(jn["cl"].to_numpy(), jn["p1"].to_numpy(), n_placebo=0)
    #      (b) spread weekly-vol matched to P1
    js = pd.concat([w_spread.rename("s"), p1_weekly.rename("p1")], axis=1).dropna()
    wv_spread = float(EB.evaluate(js["s"].to_numpy(), js["p1"].to_numpy(), n_placebo=0)["weekly_vol"])
    P("")
    P(f"  EVAL BATTERY (LED BY WEEKLY-VOL; {len(jn)} shared ISO weeks with P1):")
    for b in ("native", "weekly_vol", "realized_vol", "gross_exposure"):
        lead = "  <== PRIMARY (strategy P&L)" if b == "weekly_vol" else ""
        P(f"      {b:<16} ${resb[b]:>12,.2f}/wk{lead}")
    P(f"      weekly-vol of the SPREAD (drift-free edge, matched to P1) = ${wv_spread:,.2f}/wk")

    # fixed-DD ONLY beside its rate-matched random-thinning placebo (T2 discipline)
    tp = np.array([t["net"] for t in bt["trades"]], float)
    if ntr > 5:
        tr_wk = iso_week(np.array([dts[t["exit"]] for t in bt["trades"]]))
        codes, uniq = pd.factorize(pd.Index(tr_wk), sort=True)
        # candidate/reference on strategy's own weekly grid (per-trade -> weekly)
        nper = len(w_net)
        # align trade weeks to the strategy weekly grid index
        wk_index = list(w_net.index)
        code_on_grid = np.array([wk_index.index(u) if u in wk_index else 0 for u in uniq])
        per_grid = code_on_grid[codes]
        nrm = max(1, int(round(0.10 * ntr)))
        cand = np.bincount(per_grid, weights=tp, minlength=nper)
        res_dd = EB.evaluate(cand, cand, n_placebo=2000, base_for_placebo="fixed_dd",
                             ref_trades=tp, ref_periods=per_grid, n_trades_removed=nrm,
                             seed=SEED)
        null_dd = EB.random_thinning_placebo(tp, per_grid, nrm, "fixed_dd", n=2000, seed=SEED,
                                             n_periods=nper)
        base_income = tp.sum() / nper
        placebo_med = float(np.median(null_dd))
        P("")
        P(f"  fixed-DD (ORDER STATISTIC -> shown ONLY with placebo): self fixed-DD income "
          f"${base_income:,.2f}/wk ;")
        P(f"      side-blind 10%-thinning median ${placebo_med:,.2f}/wk (lift {placebo_med-base_income:+,.2f}); "
          f"obs at pct {res_dd.placebo_percentile:.1f}")
    else:
        base_income = float("nan"); placebo_med = float("nan")
        P("  fixed-DD: too few trades for a placebo (skipped).")

    # Sharpe / maxDD / return-DD (weekly, native)
    shp = w_net.mean() / max(w_net.std(ddof=1), 1e-9) * np.sqrt(52)
    mdd = EB.max_drawdown(w_net.to_numpy())
    rdd = w_net.sum() / max(mdd, 1e-9)
    P(f"  weekly Sharpe(ann) {shp:.3f} ; maxDD ${mdd:,.0f} ; return/DD {rdd:.2f} (native, spread-agnostic)")

    # ---- G4 weekly-vol placebo: spread edge on weekly-vol (not fixed-DD-only) -----------
    g4 = bool(wv_spread > 0)
    P("")
    P(f"  G4  drift-free edge on WEEKLY-VOL (not fixed-DD-only): weekly-vol(spread) ${wv_spread:,.2f}/wk "
      f"-> {'>0' if g4 else '<=0'}")

    # ---- G5 era stability ----------------------------------------------------------------
    dser = pd.to_datetime(pd.Series(dts))
    era1 = dser.to_numpy() < ERA_SPLIT
    e1w = pd.Series(spread_daily[era1]).groupby(iso_week(dts[era1])).sum()
    e2w = pd.Series(spread_daily[~era1]).groupby(iso_week(dts[~era1])).sum()
    g5 = bool(e1w.mean() > 0 and e2w.mean() > 0)
    P("")
    P(f"  G5  walk-forward SPREAD: 2022-2024 ${e1w.mean():,.2f}/wk ({len(e1w)}wk) | "
      f"2025-2026-07 ${e2w.mean():,.2f}/wk ({len(e2w)}wk) -> both positive ? {g5} "
      f"{'' if g5 else '(REGIME_LOCAL if only one)'}")

    # ---- G6 PnL orthogonality to P1 ------------------------------------------------------
    cl_daily = pd.Series(net_daily, index=pd.to_datetime(dts))
    jd = pd.concat([cl_daily.rename("cl"), p1_daily.rename("p1")], axis=1).dropna()
    rho_d = float(jd["cl"].corr(jd["p1"])) if len(jd) > 2 else float("nan")
    jw = pd.concat([w_net.rename("cl"), p1_weekly.rename("p1")], axis=1).dropna()
    rho_w = float(jw["cl"].corr(jw["p1"])) if len(jw) > 2 else float("nan")
    low_rho = bool(abs(rho_d) < 0.30)
    P("")
    P(f"  G6  PnL-rho-to-P1: daily {rho_d:+.4f} ({len(jd)} shared days) ; weekly {rho_w:+.4f} "
      f"({len(jw)} shared wk) -> low/negative (|rho_d|<0.30) ? {low_rho}")

    # ---- G7 cost band --------------------------------------------------------------------
    band = {}
    for stk in SPREAD_TICKS:
        c = eval_cell(dts, Pc, PRIMARY["W"], PRIMARY["k"], PRIMARY["H"], stk)
        _, blo, bhi = moving_block_ci(c["w_spread"].to_numpy(), L=4, B=8000, seed=SEED)
        band[stk] = dict(spread=c["spread_weekly"], ci_lo=blo, raw=c["raw_weekly"])
    cost_robust = all(band[stk]["spread"] > 0 for stk in SPREAD_TICKS)
    cost_robust_ci = all(band[stk]["ci_lo"] > 0 for stk in SPREAD_TICKS)
    P("")
    P("  G7  cost band (after-cost SPREAD weekly $ ; CI-lo):  " +
      "  ".join(f"{stk}tk ${band[stk]['spread']:,.1f} (lo ${band[stk]['ci_lo']:,.1f})"
                for stk in SPREAD_TICKS))
    P(f"      spread>0 across the whole band ? {cost_robust} ; CI-excludes-0 across band ? {cost_robust_ci}")

    # ---- plateau gate G3 -----------------------------------------------------------------
    tot_p, pos_p, ci_p, nul_p = plateau_stats(PRIMARY["basis"])
    plateau_ok = bool(pos_p >= max(2, int(np.ceil(0.6 * tot_p))))
    P("")
    P(f"  G3  neighborhood plateau [{PRIMARY['basis']} multi-day]: spread>0 in {pos_p}/{tot_p} cells "
      f"-> plateau (>=60%) ? {plateau_ok}")

    # ============================ VERDICT =================================================
    # Distinguish the failure modes on the DRIFT-CONTROL first: how much of the raw edge did
    # the exposure-matched drift control absorb? (raw - spread). If it absorbed the edge ->
    # DRIFT-EXPLAINED. If the spread survives the control in point-estimate but is below MDE /
    # its CI straddles 0 / it does not clear the null -> UNDERPOWERED (cannot distinguish from
    # 0). If the spread is <=0 at realistic cost even before the power question -> FAIL.
    raw_weekly = float(w_net.mean())
    drift_absorbed = raw_weekly - obs_spread
    survives = bool(g2 and clears and g4 and cost_robust and low_rho and plateau_ok)
    if survives:
        verdict = "PORTFOLIO-ADDITIVE"
    elif raw_weekly > 0 and obs_spread <= 0:
        verdict = "DRIFT-EXPLAINED"          # drift control absorbed the positive raw edge
    elif obs_spread <= 0:
        verdict = "FAIL"                     # no positive edge even before the drift control
    elif not g2:
        # positive spread that SURVIVES the drift control in point estimate, but is
        # statistically indistinguishable from 0 (sub-MDE / CI straddles 0 / null uncleared)
        verdict = "underpowered"
    else:
        verdict = "FAIL"                     # g2 ok but a robustness gate (plateau/cost/era) failed
    P("")
    P(f"  DRIFT CONTROL absorbed ${drift_absorbed:,.2f}/wk of the ${raw_weekly:,.2f}/wk raw edge "
      f"(mean net exposure {mean_pos:+.4f}) -> the failure is NOT drift; it is POWER"
      if (raw_weekly > 0 and obs_spread > 0 and not g2) else
      f"  DRIFT CONTROL absorbed ${drift_absorbed:,.2f}/wk of the ${raw_weekly:,.2f}/wk raw edge")
    P(f"  ==> PRIMARY VERDICT: {verdict}   (survives-flag = {survives})")

    # ---- daily_pnl.csv (primary cell, P1 aligned) ----------------------------------------
    dp = pd.DataFrame(dict(
        date=pd.to_datetime(dts),
        cl_strat_net=net_daily,
        cl_drift_control=ctrl_daily,
        cl_spread=spread_daily,
        cl_pos=bt["pos"]))
    dp = dp.set_index("date")
    dp["p1_net"] = p1_daily.reindex(dp.index)
    dp.to_csv(os.path.join(OUT, "daily_pnl.csv"))

    # ============================ GATE TABLE (program-printed) ============================
    gt = []
    gt.append("=" * 108)
    gt.append("W2C_CL_MR_20260906  --  GATE TABLE  (program-printed)   trial G00065 / CROSS_ASSET_NATIVE")
    gt.append(f"PRIMARY cell (a-priori from autopsy): basis={PRIMARY['basis']} W={PRIMARY['W']} "
              f"k={PRIMARY['k']} H={PRIMARY['H']} ; realistic cost 1 tick (ALL_IN ${COMM+DV:.2f}/ctrRT)")
    gt.append("=" * 108)
    gt.append(f"{'gate':<6}{'spec':<50}{'observed':>36}{'verdict':>8}")
    gt.append(_grow("G0", "points basis, max session < 2026-08-01 (seal)",
                    f"{bnd['last_sess']}", seal_ok))
    gt.append(_grow("G1", "MDE printed before observed spread (barrier)",
                    f"MDE ${mde:,.0f} vs obs ${obs_spread:,.0f}", obs_spread > mde))
    gt.append(_grow("G2", "spread>0 & block-boot CI excl 0 & clears null",
                    f"${obs_spread:,.0f} CI[{ci_lo:,.0f},{ci_hi:,.0f}] p{pnull:.3f}", g2))
    gt.append(_grow("G3", "W x k x H plateau of positive spread (>=60%)",
                    f"{pos_p}/{tot_p} multi-day cells >0", plateau_ok))
    gt.append(_grow("G4", "edge on weekly-vol, not fixed-DD-only",
                    f"wv(spread) ${wv_spread:,.0f}/wk", g4))
    gt.append(_grow("G5", "positive spread in BOTH walk-forward eras",
                    f"22-24 ${e1w.mean():,.0f} | 25-26 ${e2w.mean():,.0f}", g5))
    gt.append(_grow("G6", "PnL-rho-to-P1 printed (low/neg = diversifier)",
                    f"daily {rho_d:+.3f} weekly {rho_w:+.3f}", True))
    gt.append(_grow("G7", "survives {0.5,1,2}-tick ALL_IN cost band",
                    f"spread>0 all rungs {cost_robust}", cost_robust))
    gt.append("-" * 108)
    gt.append(f"SURVIVES (G2 & null & weekly-vol & cost-robust & low PnL-rho & plateau) = {survives}")
    gt.append(f"VERDICT = {verdict}")
    gt.append("")
    gt.append("SEMANTICS: every figure is an IN-SAMPLE, pre-seal (<2026-08-01), POINTS-basis, after-cost")
    gt.append("  DISCOVERY_CONSUMED measurement of a ported research mechanism -- NOT a forward or live")
    gt.append("  number, and NOT multiplied by any live-book factor. No order, no enable, $0.")
    gate_txt = "\n".join(gt)
    with open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8") as f:
        f.write(gate_txt + "\n")
    P("")
    P(gate_txt)

    with open(os.path.join(OUT, "run_log.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log) + "\n")

    # summary dict for the caller (printed as the last block)
    summ = dict(verdict=verdict, survives=survives,
                spread_weekly=round(obs_spread, 2), spread_ci=[round(ci_lo, 2), round(ci_hi, 2)],
                spread_ci_excl_0=ci_excl, circ_shift_p=round(pnull, 4), clears_null=clears,
                mde=round(mde, 2), rho_daily=round(rho_d, 4), rho_weekly=round(rho_w, 4),
                low_rho=low_rho, wv_spread=round(wv_spread, 2),
                cost_robust=cost_robust, cost_robust_ci=cost_robust_ci,
                plateau_pos=f"{pos_p}/{tot_p}", plateau_ok=plateau_ok,
                era1=round(float(e1w.mean()), 2), era2=round(float(e2w.mean()), 2), g5=g5,
                raw_weekly=round(raw_weekly, 2), drift_absorbed=round(drift_absorbed, 2),
                mean_net_exposure=round(mean_pos, 4), ntrades=ntr,
                coherence_multiday_gt_1day=bool(
                    ndf[(ndf.basis == PRIMARY["basis"]) & (ndf.W > 1)]["spread_weekly"].mean() >
                    ndf[(ndf.basis == PRIMARY["basis"]) & (ndf.W == 1)]["spread_weekly"].mean()))
    P("")
    P("SUMMARY " + str(summ))
    P(f"[done {_t.time()-t0:.0f}s]  wrote neighborhood.csv, daily_pnl.csv, gate_table.txt, run_log.txt")
    return summ


if __name__ == "__main__":
    main()
