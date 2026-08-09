"""W18R1_M1_VOLSEASON common helpers.

Verbatim reuse of runs/SMV2AI_ATR_BLEND/src/common.py (which is itself a line-for-line
reuse of runs/SMV2AD_VOLMULT_CEILING/src/common.py). The ONLY additions are the slot
machinery and the causal seasonal-factor estimator required by this run's frozen spec;
every formula and constant reused from the prior file is unchanged, cross-checked by hand.
"""
import sys, os, datetime as dt
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
import sm01_solarsim as sm
from smv2_common import dd_battery

RUN = os.path.join(ROOT, "runs", "W18R1_M1_VOLSEASON")
OUT = os.path.join(RUN, "out")
DEV_END = dt.date(2026, 5, 29)      # last dev session; CONVENTIONS.md states the boundary as
                                    # 2026-05-31 and 2026-05-29 is the last session <= it.
INCUMBENT_VMS = list(sm.VMS)        # 6..30 step 2, 13 members
WARMUP_SESSIONS = 60                # frozen in spec; NOT swept
SLOT_MINUTES = 3


def load_dev_bars(path=None):
    path = path or os.path.join(ROOT, "runs", "AUDIT03_BARS", "nq_3m_2022_2026.csv")
    bars = sm.load_bars_3m(path)
    bars = bars[bars["sess_date"] <= DEV_END].reset_index(drop=True)
    return bars


# ------------------------------------------------------------------ slots
def slot_index(bars):
    """slot = bar-END time-of-day in exchange (ET) time at 3-minute granularity, 0..479.

    Time-of-day, NOT bar index within session, per the frozen spec: bar index is corrupted
    by the 13 NQ dev sessions with internal gaps and by the 43 holiday early closes.
    """
    t = pd.to_datetime(bars["time"])
    return ((t.dt.hour * 60 + t.dt.minute) // SLOT_MINUTES).to_numpy().astype(int)


def abs_dclose(bars):
    """|Delta close| on the SAME convention sm01_solarsim.sigma_series uses:
    d = |diff(close, prepend=close[0])| with d[0] = 0. Diffs span session boundaries exactly
    as the incumbent's sigma460 does — this is deliberate, not an oversight."""
    close = bars["close"].to_numpy()
    d = np.abs(np.diff(close, prepend=close[0]))
    d[0] = 0.0
    return d


def causal_seasonal_factor(bars, warmup_sessions=WARMUP_SESSIONS):
    """Per-bar causal seasonal factor f, frozen spec §step2_estimator.

    Estimated ONCE PER SESSION at the session boundary from sessions STRICTLY BEFORE it:
        raw_s(d) = mean |dclose| in slot s over all bars in sessions < d
        W(d)     = (total |dclose| over all prior bars) / (total prior bars)
        f_s(d)   = raw_s(d) / W(d)          -> E[f] = 1 under the historical slot distribution
    Slots never yet observed get f = 1. f == 1 everywhere until `warmup_sessions` complete
    prior sessions exist.

    Returns (f_bar, f_snapshots) where f_bar[t] is the factor in force at bar t and
    f_snapshots is a dict {sess_date: f_vector(480)} taken at each session start.
    """
    d = abs_dclose(bars)
    slot = slot_index(bars)
    sess = bars["sess_date"].to_numpy()

    n = len(bars)
    n_slots = 480
    sum_d = np.zeros(n_slots)
    cnt = np.zeros(n_slots)
    tot_d = 0.0
    tot_n = 0
    n_prior_sessions = 0

    f_bar = np.ones(n)
    snapshots = {}

    # pending accumulators for the session currently being traversed (added only at its end,
    # so nothing from the current session can leak into its own factor)
    pend_sum = np.zeros(n_slots)
    pend_cnt = np.zeros(n_slots)
    pend_tot_d = 0.0
    pend_tot_n = 0

    cur_f = np.ones(n_slots)
    cur_sess = sess[0]
    snapshots[cur_sess] = cur_f.copy()

    for t in range(n):
        if sess[t] != cur_sess:
            # session boundary: fold the finished session in, then re-estimate
            sum_d += pend_sum; cnt += pend_cnt
            tot_d += pend_tot_d; tot_n += pend_tot_n
            pend_sum[:] = 0.0; pend_cnt[:] = 0.0
            pend_tot_d = 0.0; pend_tot_n = 0
            n_prior_sessions += 1
            if n_prior_sessions >= warmup_sessions and tot_n > 0:
                W = tot_d / tot_n
                with np.errstate(invalid="ignore", divide="ignore"):
                    raw = np.where(cnt > 0, sum_d / np.where(cnt > 0, cnt, 1.0), np.nan)
                cur_f = np.where(np.isfinite(raw) & (W > 0), raw / W, 1.0)
            else:
                cur_f = np.ones(n_slots)
            cur_sess = sess[t]
            snapshots[cur_sess] = cur_f.copy()
        f_bar[t] = cur_f[slot[t]]
        pend_sum[slot[t]] += d[t]; pend_cnt[slot[t]] += 1
        pend_tot_d += d[t]; pend_tot_n += 1
    return f_bar, snapshots


# ------------------------------------------------------------- member ensemble
def build_pend(bars, sig, vms=None, smax_ticks=1200.0, smin_ticks=40.0):
    """Verbatim SMV2AI common.build_pend. member_states/member_trades UNMODIFIED; only the
    sigma array fed in is varied."""
    vms = vms or INCUMBENT_VMS
    PEND = []
    for vm in vms:
        is_up, flip, s_eff, anchor = sm.member_states(
            bars["close"].to_numpy(), sig, float(vm),
            smin_ticks=smin_ticks, smax_ticks=smax_ticks)
        fills, pos, pend = sm.member_trades(bars, is_up, flip, s_eff, anchor)
        PEND.append(pend)
    return np.column_stack(PEND)


def build_pend_with_flips(bars, sig, vms=None, smax_ticks=1200.0, smin_ticks=40.0):
    vms = vms or INCUMBENT_VMS
    PEND, FLIPS = [], []
    for vm in vms:
        is_up, flip, s_eff, anchor = sm.member_states(
            bars["close"].to_numpy(), sig, float(vm),
            smin_ticks=smin_ticks, smax_ticks=smax_ticks)
        fills, pos, pend = sm.member_trades(bars, is_up, flip, s_eff, anchor)
        PEND.append(pend); FLIPS.append(flip)
    return np.column_stack(PEND), np.column_stack(FLIPS)


# ------------------------------------------------------------------ E10 layer
def e10_exec(bars, tgt, comm_side=sm.MNQ_COMM_SIDE, point_value=sm.MNQ_POINT_VALUE):
    """Verbatim copy of runs/SMV2AI_ATR_BLEND/src/common.py e10_exec."""
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
            dq = pend_ - p
            side = 1 if dq > 0 else -1
            px = sm._fill(open_[t], high[t], low[t], side)
            cash -= dq * px * point_value
            cash -= abs(dq) * comm_side
            contracts[sess_date[t]] = contracts.get(sess_date[t], 0) + abs(dq)
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


# ------------------------------------------------------------------ metrics
def metric_row(label, daily, tgt):
    """Verbatim SMV2AI common.metric_row (house frozen definitions)."""
    x = daily["net"].to_numpy()
    b = dd_battery(daily["sess"], x, label=label)
    return {
        "arm": label, "n_days": b["n_days"], "net": b["net"],
        "sharpe": b["sharpe"], "maxDD_eod": b["maxDD_eod"], "CDaR_0.95": b["CDaR5"],
        "sortino": b["sortino"], "calmar": b["calmar"],
        "top10_day_sum": float(np.sort(x)[-10:].sum()),
        "worst_day": float(x.min()), "worst_month": b["worst_month"],
        "pos_day_pct": b["pos_day_pct"],
        "turnover_tgt_change_bars_pct": float((np.diff(tgt) != 0).mean() * 100),
        "avg_contracts_per_day": float(daily["contracts"].mean()),
    }


# ------------------------------------------------------- DUAL_HTF + 60/40 blend
def rha(x):
    return np.sign(x) * np.floor(np.abs(x) + 0.5)


def dual_htf(T, st_bar):
    """Verbatim runs/SMV2T_NOFAST_R2/gate_AD.py dual_htf()."""
    agree = (np.sign(T) != 0) & (st_bar == np.sign(T))
    m = np.where(agree, 1.25, 1.0)
    s = np.where((T < 0) & (st_bar > 0), 0.5, 1.0)
    return np.clip(rha(T * m * s * 0.9026), -13, 13)


def htf_state(bars):
    """Verbatim SMV2T gate_AD.py HTF construction."""
    sclose = bars.loc[bars["is_last_of_sess"], ["sess_date", "close"]].set_index("sess_date")["close"]
    htf = np.sign(sclose - sclose.rolling(50).mean()).shift(1).to_dict()
    return np.array([htf.get(d, np.nan) for d in bars["sess_date"]])


def vm(x, sig):
    return x * (sig / x.std(ddof=1))


def build_portfolio_6040(bars, tgt_solar):
    """Verbatim SMV2AI common.build_portfolio_6040 (B-MOM leg UNCHANGED)."""
    st_bar = htf_state(bars)
    Tpp = dual_htf(tgt_solar.astype(float), st_bar)
    daily_dual, _, _ = e10_exec(bars, Tpp.astype(int))
    cal = pd.to_datetime(daily_dual["sess"])
    DUAL = pd.Series(daily_dual["net"].to_numpy(), index=cal)

    bm2 = pd.read_parquet(os.path.join(ROOT, "runs", "SMV2B_BMOM_EXEC_AUDIT", "out",
                                        "ledger_E2_next_open.parquet"))
    BM = (bm2.groupby("sess")["net_c1_ticks"].sum() * 5.0)
    BM.index = pd.to_datetime(BM.index)
    BM = BM.reindex(cal).fillna(0.0)

    SIG = float(DUAL.std(ddof=1))
    portfolio = vm(0.6 * DUAL + 0.4 * vm(BM, SIG), SIG)
    return DUAL, portfolio, SIG, Tpp
