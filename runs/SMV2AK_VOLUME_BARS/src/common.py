"""SMV2AK_VOLUME_BARS common helpers -- shared by sub_438..442 scripts.

Verbatim reuse of src/analytics/sm01_solarsim.py machinery (member_states/
member_trades/e10_target UNMODIFIED) plus the SMV2AD common.py e10_exec (MNQ
executor, verbatim copy) and DUAL_HTF + DAYONLY_DUAL6040 60/40 portfolio-blend
construction (verbatim copy, only the Solar leg substituted) -- reused from
runs/SMV2AD_VOLMULT_CEILING/src/common.py line-for-line (import path differs
only because this run lives in a different directory; every formula/constant
below is unchanged from that file, cross-checked by hand against it).

New machinery specific to this run: session-tagging of raw 1-minute bars
(IDENTICAL gap-heuristic to sm01_solarsim.resample_3m(), applied to build
sess_id/sess_date/is_last_of_sess on the raw 1m frame BEFORE any volume-bar
aggregation) and build_volume_bars() (sub_438's construction).
"""
import sys, os, datetime as dt
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
import sm01_solarsim as sm
from smv2_common import dd_battery

RUN = os.path.join(ROOT, "runs", "SMV2AK_VOLUME_BARS")
OUT = os.path.join(RUN, "out")
DEV_END = dt.date(2026, 5, 31)  # same cutoff every SMV2A* dev script uses; actual
                                  # last dev session is 2026-05-29 (1139 sessions,
                                  # matches SMV2AE/SMV2AI/SMV2AD's own dev calendar)

INCUMBENT_VMS = list(sm.VMS)  # 6..30 step2, 13 members

SM1M_PATH = os.path.join(ROOT, "runs", "SM1M_SUBSTRATE", "out", "nq_1m_2022_2026.parquet")
HIST1M_PATH = os.path.join(ROOT, "research", "scalping_lab", "substrate", "minute", "NQ",
                            "nq1m_2005_202605.parquet")


# ---------------------------------------------------------------- dev substrate (3m, for control)
def load_dev_bars_3m():
    bars = sm.load_bars_3m(os.path.join(ROOT, "runs", "AUDIT03_BARS", "nq_3m_2022_2026.csv"))
    bars = bars[bars["sess_date"] <= DEV_END].reset_index(drop=True)
    return bars


# ---------------------------------------------------------------- session tagging (1m raw)
def tag_sessions(df1m: pd.DataFrame) -> pd.DataFrame:
    """IDENTICAL gap-heuristic session tagging to sm01_solarsim.resample_3m()'s
    internal convention (gap>1h => new session; sess_date = date of the LAST bar
    in the session; is_last_of_sess flags that bar) -- applied directly to the
    raw 1-minute frame instead of after 3-minute resampling. This is the same
    convention SMV2AF_1MIN_RESCALE_R2 gate C validated against the SM06 hist
    3m calendar (99.93% session match) for the native 1m hist file."""
    df = df1m.sort_values("time").reset_index(drop=True).copy()
    t = pd.to_datetime(df["time"])
    df["time"] = t
    gap = t.diff() > pd.Timedelta(hours=1)
    df["first_bar_of_session"] = gap | (df.index == 0)
    df["sess_id"] = df["first_bar_of_session"].cumsum()
    last_time = df.groupby("sess_id")["time"].transform("max")
    df["sess_date"] = last_time.dt.date
    df["is_last_of_sess"] = df["time"].eq(last_time)
    return df


# ---------------------------------------------------------------- sub_438: volume bars
def build_volume_bars(df1m_tagged: pd.DataFrame, V: float) -> pd.DataFrame:
    """Aggregate consecutive session-tagged 1-minute bars into volume bars that
    close the instant cumulative volume SINCE THE VOLUME BAR'S OWN OPEN reaches
    threshold V. SESSION-BOUNDED: a volume bar never spans a session boundary;
    the final partial bar of a session (volume < V when the session ends) is
    closed at the session's last 1-minute bar's close, as-is (not merged
    forward, not dropped, not padded).

    Vectorized construction (no Python loop): cumvol_prev_t = sum of volumes of
    all PRIOR 1m bars within the current session (0 at session start); the
    volume-bar index within the session is floor(cumvol_prev_t / V) -- this
    correctly assigns every 1m bar to the volume-bar that was still "open" at
    its start, and closes that volume-bar (however much it overshoots V by, in
    the rare case a single 1m bar's own volume exceeds V) the instant its
    inclusion pushes the running total to/past V. Equivalent to the greedy
    "accumulate until >=V, then reset" definition for every possible input.
    """
    df = df1m_tagged.copy()
    df["cumvol_prev"] = df.groupby("sess_id")["volume"].cumsum() - df["volume"]
    df["vbar_in_sess"] = np.floor(df["cumvol_prev"] / V).astype(np.int64)
    df["vbar_key"] = df["sess_id"].astype(np.int64) * 1_000_000 + df["vbar_in_sess"]

    g = df.groupby("vbar_key", sort=True)
    out = pd.DataFrame({
        "open": g["open"].first(),
        "high": g["high"].max(),
        "low": g["low"].min(),
        "close": g["close"].last(),
        "volume": g["volume"].sum(),
        "time": g["time"].last(),
        "first_time": g["time"].first(),
        "sess_id": g["sess_id"].first(),
        "sess_date": g["sess_date"].first(),
        "n_1m_bars": g["volume"].count(),
        "is_last_of_sess": g["is_last_of_sess"].max().astype(bool),
    }).reset_index(drop=True)
    out = out.sort_values("time").reset_index(drop=True)
    out["first_bar_of_session"] = out["sess_id"].ne(out["sess_id"].shift(1))
    out["elapsed_sec"] = (out["time"] - out["first_time"]).dt.total_seconds() + 60.0
    return out


# ------------------------------------------------------------- member ensemble
def build_pend(bars, sig, vms, smax_ticks=1200.0, smin_ticks=40.0):
    """member_states/member_trades UNMODIFIED (verified by direct code read);
    only the sigma array `sig` and VolMult list `vms` fed in are varied."""
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
    """Verbatim copy of runs/SMV2AD_VOLMULT_CEILING/src/common.py e10_exec
    (instrumented e10_sim, MNQ costs, session flatten via is_last_of_sess).
    Returns (daily_df[sess,net,contracts], bar_pos, bar_pnl)."""
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
        "n_tgt_changes": int((np.diff(tgt) != 0).sum()),
        "avg_contracts_per_day": float(daily["contracts"].mean()),
        "total_contracts_traded": float(daily["contracts"].sum()),
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
    of session closes. Works at ANY bar cadence (only needs is_last_of_sess /
    sess_date / close)."""
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
    UNCHANGED B-MOM E2 next-open leg). `bars`/`tgt_solar` may be at ANY bar
    cadence (3m or volume bars) -- only is_last_of_sess/sess_date/close/
    open/high/low are used. Returns (DUAL_daily_series, portfolio_series,
    SIG_scalar, Tpp)."""
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


# ---------------------------------------------------------- hist (2006-2021) executor
TICK = 0.25; NQ_COMM = 2.18; NQ_PV = 20.0


def run_policy_hist(df, desired, comm=NQ_COMM, pv=NQ_PV):
    """Verbatim runs/SMV2AD_VOLMULT_CEILING/src/sub417_old_regime.py /
    runs/SMV2AI_ATR_BLEND/src/step3_old_regime.py run_policy_hist (SMV2H2
    gate-B executor convention on the close-only hist substrate: decisions at
    bar close, fills at THIS bar's close +-1 tick [close-only, no intrabar
    high/low cap -- the established hist-era convention this program has used
    every prior time, kept verbatim here even though the native 1m hist file
    does carry real OHLC], session-close flatten, 16:30-18:03 ops window with
    a hard flatten at 16:39). Works at ANY bar cadence (3m or hist volume
    bars) -- only close/is_last_of_sess/time/sess_date are used."""
    n = len(df)
    c = df["close"].to_numpy(); last = df["is_last_of_sess"].to_numpy()
    tm = pd.to_datetime(df["time"])
    hm = tm.dt.hour.to_numpy() * 100 + tm.dt.minute.to_numpy()
    sd = df["sess_date"].to_numpy()
    cash = 0.0; p = 0; pend_ = 0; daily = {}; prev = 0.0
    fills = 0; entries = 0
    for t in range(n):
        if pend_ != p:
            d = pend_ - p; side = 1 if d > 0 else -1
            px = c[t] + side * TICK
            cash -= d * px * pv; cash -= abs(d) * comm
            if pend_ != 0:
                entries += 1
            p = pend_; fills += 1
        if last[t] and p != 0:
            side = -1 if p > 0 else 1
            px = c[t] + side * TICK
            cash += p * px * pv; cash -= abs(p) * comm
            fills += 1; p = 0; pend_ = 0
        else:
            want = int(desired[t])
            if hm[t] == 1639:
                pend_ = 0
            elif 1630 <= hm[t] < 1803:
                pend_ = p if hm[t] < 1639 else 0
            else:
                pend_ = want
        if last[t]:
            eqv = cash + p * c[t] * pv
            daily[sd[t]] = eqv - prev; prev = eqv
    dl = pd.Series(daily); dl.index = pd.to_datetime(dl.index)
    return dl, fills, entries


def battery_hist(dl):
    net = dl.values; eqd = np.cumsum(net); pk = np.maximum.accumulate(eqd); dd = pk - eqd
    k = max(1, int(0.05 * len(net)))
    sd_ = net.std(ddof=1)
    return {"n_days": len(net), "net": net.sum(),
            "sharpe": net.mean() / sd_ * np.sqrt(252) if sd_ > 0 else np.nan,
            "maxDD_eod": dd.max(), "CDaR5": np.sort(dd)[::-1][:k].mean()}
