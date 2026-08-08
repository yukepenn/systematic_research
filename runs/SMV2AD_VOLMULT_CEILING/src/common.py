"""SMV2AD common helpers -- shared by sub_415/416/417 scripts.
Verbatim reuse of src/analytics/sm01_solarsim.py machinery
(member_states/member_trades/e10_target UNMODIFIED except the explicit smax_ticks
argument already exposed by member_states) plus the SMV2R common_exec.e10_exec
MNQ executor (verbatim copy) and the SMV2T DUAL_HTF transform + DAYONLY_DUAL6040
60/40 portfolio-blend construction (verbatim copy, only the Solar leg substituted).
"""
import sys, os, datetime as dt
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
import sm01_solarsim as sm
from smv2_common import dd_battery

RUN = os.path.join(ROOT, "runs", "SMV2AD_VOLMULT_CEILING")
OUT = os.path.join(RUN, "out")
DEV_END = dt.date(2026, 5, 31)
SEED, BLOCK, NBOOT = 20260808, 5, 10000

INCUMBENT_VMS = list(sm.VMS)  # 6..30 step2, 13 members


# ---------------------------------------------------------------- dev substrate
def load_dev_bars():
    bars = sm.load_bars_3m(os.path.join(ROOT, "runs", "AUDIT03_BARS", "nq_3m_2022_2026.csv"))
    bars = bars[bars["sess_date"] <= DEV_END].reset_index(drop=True)
    return bars


# ------------------------------------------------------------- member ensemble
def build_pend(bars, sig, vms, smax_ticks=1200.0, smin_ticks=40.0):
    """Rebuild the per-member `pend` (order-book target position, what
    e10_target consumes) matrix for the given VolMult list and clamp ceiling.
    member_states/member_trades UNMODIFIED (verified by direct code read);
    only the explicit smax_ticks/smin_ticks kwargs (already part of the
    committed signature) are varied per the spec."""
    close = bars["close"].to_numpy()
    PEND = []
    for vm in vms:
        is_up, flip, s_eff, anchor = sm.member_states(
            close, sig, float(vm), smin_ticks=smin_ticks, smax_ticks=smax_ticks)
        fills, pos, pend = sm.member_trades(bars, is_up, flip, s_eff, anchor)
        PEND.append(pend)
    return np.column_stack(PEND)


# ------------------------------------------------------------------ E10 layer
def e10_exec(bars, tgt, comm_side=sm.MNQ_COMM_SIDE, point_value=sm.MNQ_POINT_VALUE):
    """Verbatim copy of runs/SMV2R_SOLAR_CORE_1/common_exec.e10_exec (instrumented
    e10_sim, MNQ costs, session flatten). Returns (daily_df[sess,net,contracts],
    bar_pos, bar_pnl)."""
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


# ------------------------------------------------------------------ metrics
def metric_row(label, daily, tgt):
    """dd_battery (house frozen definitions) + turnover (tgt_change_bars_pct,
    same convention as SMV2R sub382/sub383) + top-10-day sum."""
    x = daily["net"].to_numpy()
    b = dd_battery(daily["sess"], x, label=label)
    return {
        "arm": label, "n_days": b["n_days"], "net": b["net"],
        "sharpe": b["sharpe"], "maxDD_eod": b["maxDD_eod"], "CDaR_0.95": b["CDaR5"],
        "top10_day_sum": float(np.sort(x)[-10:].sum()),
        "turnover_tgt_change_bars_pct": float((np.diff(tgt) != 0).mean() * 100),
        "avg_contracts_per_day": float(daily["contracts"].mean()),
    }


# ------------------------------------------------------- DUAL_HTF + 60/40 blend
def rha(x):
    return np.sign(x) * np.floor(np.abs(x) + 0.5)


def dual_htf(T, st_bar):
    """Verbatim runs/SMV2T_NOFAST_R2/gate_AD.py dual_htf() -- tilt x1.25 on HTF
    agreement, c1_50 short-halving iff HTF-up, x0.9026, clip +-13, RHA."""
    agree = (np.sign(T) != 0) & (st_bar == np.sign(T))
    m = np.where(agree, 1.25, 1.0)
    s = np.where((T < 0) & (st_bar > 0), 0.5, 1.0)
    return np.clip(rha(T * m * s * 0.9026), -13, 13)


def htf_state(bars):
    """Verbatim SMV2T gate_AD.py HTF construction: prior-session close vs SMA50
    of session closes."""
    sclose = bars.loc[bars["is_last_of_sess"], ["sess_date", "close"]].set_index("sess_date")["close"]
    htf = np.sign(sclose - sclose.rolling(50).mean()).shift(1).to_dict()
    st_bar = np.array([htf.get(d, np.nan) for d in bars["sess_date"]])
    return st_bar


def vm(x, sig):
    return x * (sig / x.std(ddof=1))


def build_portfolio_6040(bars, tgt_solar, label):
    """Rebuild DAYONLY_DUAL6040 with the swapped Solar leg -- verbatim
    runs/SMV2T_NOFAST_R2/gate_E.py construction (DUAL_HTF transform on the raw
    E10 target -> MNQ E10 executor -> 0.6/0.4 equal-vol blend with the frozen,
    UNCHANGED B-MOM E2 next-open leg). Returns (daily_solar_dual, portfolio_series,
    SIG_scalar)."""
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


def champion_curve(cal):
    champ_all = pd.read_csv(os.path.join(ROOT, "runs", "SMV2H_ONECONTRACT", "out", "rerank_curves.csv"),
                             parse_dates=["sess"]).set_index("sess")["60_40"]
    champ = champ_all.reindex(cal)
    assert champ.isna().sum() == 0, "champion curve missing dev sessions"
    return champ
