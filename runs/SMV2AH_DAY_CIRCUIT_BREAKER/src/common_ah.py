"""SMV2AH_DAY_CIRCUIT_BREAKER common helpers.

Reuses, verbatim, the machinery already committed in this program:
  - src/analytics/sm01_solarsim.py: member_states/member_trades/e10_target
    (Solar substrate, UNMODIFIED).
  - runs/SMV2AD_VOLMULT_CEILING/src/common.py: build_pend, e10_exec (MNQ E10
    net-change executor, bar_pos/bar_pnl already instrumented), dual_htf,
    htf_state, vm(), build_portfolio_6040 (DAYONLY_DUAL6040 60/40 blend
    construction) -- COPIED VERBATIM below (spec explicitly directs re-use of
    this file's vm()/60-40 blend construction).
  - src/analytics/sm_bmom.py / runs/SMV2B_BMOM_EXEC_AUDIT/smv2b.py: the frozen
    W8-1 B-MOM signal logic (band/VWAP breakout) and its E2 next-bar-open fill
    convention (the ledger actually used in the deployed 60/40 blend).

NEW in this run (the mandatory first-step artifact, not built by any prior
run): a bar-by-bar intraday cumulative mark-to-market P&L series for object A
(SOLAR_DUAL_HTF standalone leg) and object B (DAYONLY_DUAL6040 60/40
portfolio), constructed by:
  (a) Solar/DUAL leg: e10_exec's already-instrumented bar_pnl (mark the open
      MNQ position to each bar's own close, realized+unrealized, in a single
      cash+mark bookkeeping loop identical to the frozen E10 executor) --
      NOT reimplemented, only consumed and cumsum'd per session.
  (b) B-MOM leg: NEWLY instrumented bar-by-bar mark-to-market executor
      (bm_generic_exec below) fed by a per-bar TARGET POSITION array
      (build_bm_tgt) that reproduces the frozen E2 (next-3m-bar-open fill,
      zero added slip) signal/fill timing bar-for-bar from smv2b.py's
      bmom_variant(fill_mode="E2", slip_ticks=0.0) -- same band/VWAP signal
      logic, same day_count/hist bookkeeping order, same flat_hm forced exit,
      same "decide at bar close -> fill at next bar's open" timing convention
      already used throughout this codebase's E10 executor (pend_ semantics).
      Round-trip cost (C1_TICKS=2.872 ticks -> $14.36/RT, 1 NQ) is charged in
      full at the bar that CLOSES an open position (whether flattening or
      flipping) -- HYPOTHESIS/interpretive call, disclosed in REPORT.md: the
      frozen ledger nets this cost as a single lump per round trip with no
      bar-level attribution of its own, so a choice of where within the round
      trip to book it is unavoidable; it does not affect the day-end total
      (verified below) and only mildly shapes the intraday MTM path within a
      trading day, which is the only thing sub_426/427 depend on.
  (c) Portfolio combination: the SAME two constant scalars (SIG/BM.std,
      SIG/combo.std) that build_portfolio_6040 already applies to the DAILY
      series are applied identically, bar-by-bar, to the two legs' bar_pnl
      arrays (linearity of vm()'s per-series constant rescale guarantees the
      session-end cumulative sum reconciles exactly to the existing daily
      portfolio series -- verified, not assumed, in sub_426_reconcile.py).
"""
import os
import sys
import datetime as dt

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
import sm01_solarsim as sm
from smv2_common import dd_battery

RUN = os.path.join(ROOT, "runs", "SMV2AH_DAY_CIRCUIT_BREAKER")
OUT = os.path.join(RUN, "out")
DEV_END = dt.date(2026, 5, 31)
SEED = 20260808
INCUMBENT_VMS = list(sm.VMS)

BAND_DAYS = 14
C1_TICKS = 2.872
BM_RT_COST = C1_TICKS * sm.TICK * sm.NQ_POINT_VALUE  # $14.36/RT, 1 NQ


# ---------------------------------------------------------------- dev substrate
def load_dev_bars():
    bars = sm.load_bars_3m(os.path.join(ROOT, "runs", "AUDIT03_BARS", "nq_3m_2022_2026.csv"))
    bars = bars[bars["sess_date"] <= DEV_END].reset_index(drop=True)
    return bars


# ------------------------------------------------------------- member ensemble
def build_pend(bars, sig, vms, smax_ticks=1200.0, smin_ticks=40.0):
    close = bars["close"].to_numpy()
    PEND = []
    for v in vms:
        is_up, flip, s_eff, anchor = sm.member_states(
            close, sig, float(v), smin_ticks=smin_ticks, smax_ticks=smax_ticks)
        fills, pos, pend = sm.member_trades(bars, is_up, flip, s_eff, anchor)
        PEND.append(pend)
    return np.column_stack(PEND)


# ------------------------------------------------------------------ E10 layer (verbatim SMV2AD/SMV2R)
def e10_exec(bars, tgt, comm_side=sm.MNQ_COMM_SIDE, point_value=sm.MNQ_POINT_VALUE):
    n = len(bars)
    open_ = bars["open"].to_numpy(); high = bars["high"].to_numpy()
    low = bars["low"].to_numpy(); close = bars["close"].to_numpy()
    last_of_sess = bars["is_last_of_sess"].to_numpy()
    sess_date = bars["sess_date"].to_numpy()
    cash = 0.0; p = 0; pend_ = 0
    daily = {}; contracts = {}
    prev_equity = 0.0
    bar_pos = np.zeros(n, dtype=int); bar_pnl = np.zeros(n)
    prev_eq_bar = 0.0
    for t in range(n):
        if pend_ != p:
            d = pend_ - p
            side = 1 if d > 0 else -1
            px = sm._fill(open_[t], high[t], low[t], side)
            cash -= d * px * point_value
            cash -= abs(d) * comm_side
            contracts[sess_date[t]] = contracts.get(sess_date[t], 0) + abs(d)
            p = pend_
        if last_of_sess[t] and p != 0:
            side = -1 if p > 0 else 1
            px = sm._fill(open_[t], high[t], low[t], side, at_close=close[t])
            cash += p * px * point_value
            cash -= abs(p) * comm_side
            contracts[sess_date[t]] = contracts.get(sess_date[t], 0) + abs(p)
            p = 0; pend_ = 0
        else:
            pend_ = tgt[t]
        eq_bar = cash + p * close[t] * point_value
        bar_pnl[t] = eq_bar - prev_eq_bar
        prev_eq_bar = eq_bar
        bar_pos[t] = p
        if last_of_sess[t]:
            eq = cash + p * close[t] * point_value
            daily[sess_date[t]] = eq - prev_equity
            prev_equity = eq
            contracts.setdefault(sess_date[t], 0)
    dd = pd.DataFrame({"sess": list(daily.keys()), "net": list(daily.values())})
    dd["contracts"] = [contracts[s] for s in daily.keys()]
    return dd, bar_pos, bar_pnl


# ------------------------------------------------------- DUAL_HTF + 60/40 blend (verbatim SMV2AD)
def rha(x):
    return np.sign(x) * np.floor(np.abs(x) + 0.5)


def dual_htf(T, st_bar):
    agree = (np.sign(T) != 0) & (st_bar == np.sign(T))
    m = np.where(agree, 1.25, 1.0)
    s = np.where((T < 0) & (st_bar > 0), 0.5, 1.0)
    return np.clip(rha(T * m * s * 0.9026), -13, 13)


def htf_state(bars):
    sclose = bars.loc[bars["is_last_of_sess"], ["sess_date", "close"]].set_index("sess_date")["close"]
    htf = np.sign(sclose - sclose.rolling(50).mean()).shift(1).to_dict()
    st_bar = np.array([htf.get(d, np.nan) for d in bars["sess_date"]])
    return st_bar


def vm(x, sig):
    return x * (sig / x.std(ddof=1))


# --------------------------------------------------------------- B-MOM leg (NEW, bar-level)
def rth_3m(bars3):
    t = pd.to_datetime(bars3["time"])
    hm = t.dt.hour * 100 + t.dt.minute
    m = (hm >= 933) & (hm <= 1600)
    out = bars3.loc[m].copy()
    out["hm"] = hm[m]
    out["date"] = t[m].dt.date
    return out


def build_bm_tgt(bars_dev):
    """Bar-by-bar TARGET position array (value decided at bar t's close, to be
    executed at bar t+1's open by bm_generic_exec -- identical pend_ semantics
    to e10_exec/tgt), reproducing smv2b.bmom_variant(fill_mode='E2',
    slip_ticks=0.0) bar-for-bar (same band/VWAP signal, same day_count/hist
    ordering, same flat_hm forced exit). Returns int array length len(bars_dev)."""
    n = len(bars_dev)
    tgt = np.zeros(n, dtype=int)
    r = rth_3m(bars_dev)
    days = []
    for d, g in r.groupby("date", sort=True):
        g = g.sort_values("hm")
        if g["hm"].iloc[0] != 933:
            continue
        days.append((d, g))
    hist = {}
    day_count = 0
    for d, g in days:
        open0930 = g["open"].iloc[0]
        close = g["close"].to_numpy(); vol = g["volume"].to_numpy(); hm = g["hm"].to_numpy()
        idxs = g.index.to_numpy()
        vwap = np.cumsum(close * vol) / np.maximum(np.cumsum(vol), 1e-9)
        nbars = len(g)
        flat_hm = int(hm[hm <= 1557].max()) if (hm <= 1557).any() else None
        cur = 0
        if day_count >= BAND_DAYS:
            for i in range(nbars):
                h = int(hm[i])
                if flat_hm is not None and h == flat_hm:
                    cur = 0
                    tgt[idxs[i]] = cur
                    break
                if h > 1554:
                    tgt[idxs[i]] = cur
                    continue
                past = hist.get(h)
                if past is None or len(past) < 1:
                    tgt[idxs[i]] = cur
                    continue
                m_tod = float(np.mean(past[-BAND_DAYS:]))
                upper, lower = open0930 + m_tod, open0930 - m_tod
                sig = 0
                if close[i] > max(upper, vwap[i]):
                    sig = 1
                elif close[i] < min(lower, vwap[i]):
                    sig = -1
                if sig != 0 and sig != cur:
                    cur = sig
                tgt[idxs[i]] = cur
            else:
                if cur != 0:
                    tgt[idxs[-1]] = 0
        for i in range(nbars):
            hist.setdefault(int(hm[i]), []).append(abs(close[i] - open0930))
        day_count += 1
    return tgt


def bm_generic_exec(bars, tgt):
    """Single-unit (1 NQ) bar-by-bar mark-to-market executor: fills at bar t's
    OPEN (E2 convention, zero added slip -- matches the arm actually used in
    the deployed ledger), round-trip cost BM_RT_COST charged once at the
    closing leg of every round trip (flat or flip). Returns
    (daily_df[sess,net], bar_pos, bar_pnl)."""
    n = len(bars)
    open_ = bars["open"].to_numpy(); close = bars["close"].to_numpy()
    last_of_sess = bars["is_last_of_sess"].to_numpy()
    sess_date = bars["sess_date"].to_numpy()
    cash = 0.0; p = 0; pend_ = 0
    daily = {}; prev_equity = 0.0
    bar_pos = np.zeros(n, dtype=int); bar_pnl = np.zeros(n)
    prev_eq_bar = 0.0
    for t in range(n):
        if pend_ != p:
            d = pend_ - p
            px = open_[t]
            cash -= d * px * sm.NQ_POINT_VALUE
            if p != 0:
                cash -= BM_RT_COST
            p = pend_
        if last_of_sess[t] and p != 0:
            px = close[t]
            cash += p * px * sm.NQ_POINT_VALUE
            cash -= BM_RT_COST
            p = 0; pend_ = 0
        else:
            pend_ = tgt[t]
        eq_bar = cash + p * close[t] * sm.NQ_POINT_VALUE
        bar_pnl[t] = eq_bar - prev_eq_bar
        prev_eq_bar = eq_bar
        bar_pos[t] = p
        if last_of_sess[t]:
            eq = cash + p * close[t] * sm.NQ_POINT_VALUE
            daily[sess_date[t]] = eq - prev_equity
            prev_equity = eq
    dd = pd.DataFrame({"sess": list(daily.keys()), "net": list(daily.values())})
    return dd, bar_pos, bar_pnl


# ------------------------------------------------------------ existing (reference) daily curves
def bm_daily_from_ledger():
    """The EXISTING, already-verified B-MOM E2 leg daily net (used by
    build_portfolio_6040 in production): net_c1_ticks summed per session * $5."""
    bm2 = pd.read_parquet(os.path.join(ROOT, "runs", "SMV2B_BMOM_EXEC_AUDIT", "out",
                                        "ledger_E2_next_open.parquet"))
    BM = (bm2.groupby("sess")["net_c1_ticks"].sum() * 5.0)
    BM.index = pd.to_datetime(BM.index)
    return BM


def session_bounds(bars):
    """Per-session first/last bar POSITION (0-indexed row in bars, which has a
    clean RangeIndex) -- session_id -> (start_pos, end_pos)."""
    pos = np.arange(len(bars))
    sid = bars["sess_id"].to_numpy()
    df = pd.DataFrame({"sid": sid, "pos": pos})
    g = df.groupby("sid")["pos"].agg(["min", "max"])
    return g["min"].to_dict(), g["max"].to_dict()


def tail_pnl(bars, t0, sess_end, tgt_natural_d, tgt_natural_b, mode, use_dual, use_bm,
             p_d0, p_b0):
    """Simulate ONLY bars t0+1..sess_end (inclusive) of a single session under a
    circuit-breaker HALT that was decided at bar t0's close (FREEZE or FLATTEN),
    starting from the KNOWN natural positions p_d0/p_b0 held at bar t0 (bars up
    to and including t0 are identical to the natural/no-breaker path, since the
    halt only affects bars AFTER the trigger). Local cash basis (see module
    docstring reasoning: bar_pnl[t0+1] does not depend on the absolute cash
    level carried into t0, only on the increments from t0+1 onward, so a local
    cash=0 basis anchored at p_d0/p_b0's mark reproduces the true bar_pnl exactly).
    Returns (bar_pnl_d, bar_pnl_b) arrays aligned to bars[t0+1 : sess_end+1]."""
    open_ = bars["open"].to_numpy(); high = bars["high"].to_numpy()
    low = bars["low"].to_numpy(); close = bars["close"].to_numpy()
    last_of_sess = bars["is_last_of_sess"].to_numpy()
    n_tail = sess_end - t0
    bpd = np.zeros(n_tail); bpb = np.zeros(n_tail)
    if n_tail <= 0:
        return bpd, bpb
    cash_d = 0.0; p_d = p_d0; pend_d = p_d0
    cash_b = 0.0; p_b = p_b0; pend_b = p_b0
    prev_eq_d = p_d0 * close[t0] * sm.MNQ_POINT_VALUE
    prev_eq_b = p_b0 * close[t0] * sm.NQ_POINT_VALUE
    frozen_sign_d = 1 if p_d0 > 0 else (-1 if p_d0 < 0 else 0)
    frozen_cap_d = p_d0
    frozen_sign_b = 1 if p_b0 > 0 else (-1 if p_b0 < 0 else 0)
    frozen_cap_b = p_b0
    for k in range(n_tail):
        t = t0 + 1 + k
        nat_d = int(tgt_natural_d[t]) if use_dual else 0
        nat_b = int(tgt_natural_b[t]) if use_bm else 0
        if mode == "FLATTEN":
            pol_d = 0; pol_b = 0
        else:  # FREEZE: no NEW risk added -- cannot increase magnitude beyond the
               # level held at the moment of the freeze; shrink/flip via the
               # underlying reversal signal is unrestricted; if flat at the
               # moment of freeze, no new entry is opened (nothing to "shrink
               # from", opening would be adding new risk).
            if use_dual:
                if frozen_sign_d > 0 and nat_d > 0:
                    pol_d = min(nat_d, frozen_cap_d)
                elif frozen_sign_d < 0 and nat_d < 0:
                    pol_d = max(nat_d, frozen_cap_d)
                elif frozen_sign_d == 0:
                    pol_d = 0
                else:
                    pol_d = nat_d
            else:
                pol_d = 0
            if use_bm:
                if frozen_sign_b > 0 and nat_b > 0:
                    pol_b = min(nat_b, frozen_cap_b)
                elif frozen_sign_b < 0 and nat_b < 0:
                    pol_b = max(nat_b, frozen_cap_b)
                elif frozen_sign_b == 0:
                    pol_b = 0
                else:
                    pol_b = nat_b
            else:
                pol_b = 0
        if use_dual:
            if pend_d != p_d:
                d = pend_d - p_d
                side = 1 if d > 0 else -1
                px = sm._fill(open_[t], high[t], low[t], side)
                cash_d -= d * px * sm.MNQ_POINT_VALUE
                cash_d -= abs(d) * sm.MNQ_COMM_SIDE
                p_d = pend_d
            if last_of_sess[t] and p_d != 0:
                side = -1 if p_d > 0 else 1
                px = sm._fill(open_[t], high[t], low[t], side, at_close=close[t])
                cash_d += p_d * px * sm.MNQ_POINT_VALUE
                cash_d -= abs(p_d) * sm.MNQ_COMM_SIDE
                p_d = 0; pend_d = 0
            else:
                pend_d = pol_d
            eq_d = cash_d + p_d * close[t] * sm.MNQ_POINT_VALUE
            bpd[k] = eq_d - prev_eq_d
            prev_eq_d = eq_d
        if use_bm:
            if pend_b != p_b:
                d = pend_b - p_b
                px = open_[t]
                cash_b -= d * px * sm.NQ_POINT_VALUE
                if p_b != 0:
                    cash_b -= BM_RT_COST
                p_b = pend_b
            if last_of_sess[t] and p_b != 0:
                px = close[t]
                cash_b += p_b * px * sm.NQ_POINT_VALUE
                cash_b -= BM_RT_COST
                p_b = 0; pend_b = 0
            else:
                pend_b = pol_b
            eq_b = cash_b + p_b * close[t] * sm.NQ_POINT_VALUE
            bpb[k] = eq_b - prev_eq_b
            prev_eq_b = eq_b
    return bpd, bpb


def build_objects(bars):
    """Build both objects' EXISTING (reference) daily curves and bar-level pnl
    arrays needed for the intraday MTM construction.

    Returns dict with:
      tgt_solar, Tpp (DUAL target), DUAL_daily (existing, from e10_exec),
      DUAL_bar_pnl, BM_daily_ledger (existing, from frozen ledger),
      BM_tgt, BM_daily_rebuilt (from bm_generic_exec, must match ledger),
      BM_bar_pnl, cal (dev session calendar), SIG (DUAL leg std),
      c_BM, c_combo (the two constant scalars applied by vm()),
      portfolio_daily (existing, from build_portfolio_6040-equivalent calc).
    """
    close = bars["close"].to_numpy()
    sig = sm.sigma_series(close)
    pend = build_pend(bars, sig, INCUMBENT_VMS)
    tgt_solar = sm.e10_target(pend)
    st_bar = htf_state(bars)
    Tpp = dual_htf(tgt_solar.astype(float), st_bar)
    Tpp_i = Tpp.astype(int)
    DUAL_daily, DUAL_bar_pos, DUAL_bar_pnl = e10_exec(bars, Tpp_i)
    cal = pd.to_datetime(DUAL_daily["sess"])
    DUAL = pd.Series(DUAL_daily["net"].to_numpy(), index=cal)

    BM_ledger = bm_daily_from_ledger().reindex(cal).fillna(0.0)

    BM_tgt = build_bm_tgt(bars)
    BM_daily_rebuilt_df, BM_bar_pos, BM_bar_pnl = bm_generic_exec(bars, BM_tgt)
    BM_rebuilt = pd.Series(BM_daily_rebuilt_df.set_index("sess")["net"])
    BM_rebuilt.index = pd.to_datetime(BM_rebuilt.index)
    BM_rebuilt = BM_rebuilt.reindex(cal).fillna(0.0)

    # object B's natural (no-breaker) control uses BM_rebuilt (the SAME bar-level
    # machinery the circuit breaker itself perturbs), not BM_ledger, for perfect
    # internal self-consistency -- the two are identical to the cent (verified
    # in sub_426), so this changes nothing numerically.
    SIG = float(DUAL.std(ddof=1))
    c_BM = SIG / BM_rebuilt.std(ddof=1)
    combo = 0.6 * DUAL + 0.4 * (BM_rebuilt * c_BM)
    c_combo = SIG / combo.std(ddof=1)
    portfolio_daily = combo * c_combo

    return dict(
        bars=bars, sig=sig, tgt_solar=tgt_solar, Tpp=Tpp_i,
        DUAL_daily=DUAL, DUAL_bar_pnl=DUAL_bar_pnl, DUAL_bar_pos=DUAL_bar_pos,
        BM_ledger_daily=BM_ledger, BM_tgt=BM_tgt,
        BM_rebuilt_daily=BM_rebuilt, BM_bar_pnl=BM_bar_pnl, BM_bar_pos=BM_bar_pos,
        cal=cal, SIG=SIG, c_BM=float(c_BM), c_combo=float(c_combo),
        portfolio_daily=portfolio_daily,
    )
