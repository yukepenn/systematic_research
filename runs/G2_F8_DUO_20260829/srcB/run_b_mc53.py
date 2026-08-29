"""G2_F8_DUO_20260829 sub-run B — MC-53 restricted cross-asset regime states (trial G00038).

Preregistration: outB/spec_resolutions.txt (verbatim card + skeptic transcription, written
BEFORE this program ran) per runs/G2_F8_DUO_20260829/spec.yaml. No parameter search: 60d cov,
90th pctile, 2 states / monthly refit / P>0.7, tercile, 10m MA, 0.5x throttle, 252-obs
burn-in, $33/RT, 2006-2018 discovery are all card/skeptic/resolution constants.
DISCOVERY ON 2006-2018 ONLY; the multi-market panel is loaded with date_max 2018-12-31
INSIDE the read (2019+ never materialized); the max loaded date is printed.
Classification locked: RISK SPECIFICATION / REGIME ROUTING for sizing. No Sharpe printed.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import sys

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

REPO = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, REPO)

from research_sdk.seal_guard import assert_presealed, truncate_presealed
from research_sdk.null_guard import run_circular_null, verify_null_sensitivity

RUN = os.path.join(REPO, "runs", "G2_F8_DUO_20260829")
OUTB = os.path.join(RUN, "outB")

DEEP = os.path.join(REPO, r"research\scalping_lab\substrate\minute\NQ\nq1m_2005_202605.parquet")
PANEL = os.path.join(REPO, r"research\multi_market\out\economic_returns.parquet")
VXN = os.path.join(REPO, r"runs\GENESIS_FREEDATA_CBOE_20260828\certified\idx_VXN_daily.parquet")
DEEP_SHA = "dfd017eff0b031c2be89639fc4ad347d45053867edcdc2600002252b10b627cf"  # run_provenance.txt

DATE_MAX = pd.Timestamp("2018-12-31")          # skeptic discovery restriction (R01)
NQ_CAP = pd.Timestamp("2018-12-31 17:00:00")   # close of last in-window session
APP_START = pd.Timestamp("2006-01-01")
ERA_SPLIT = pd.Timestamp("2012-12-31")          # R12 reported-only
PT_USD, COST_RT = 20.0, 33.0
RV_WIN, BURN_IN = 21, 252
Q_CTRL = 0.90                                   # MC-51-frozen RV throttle decile (R03)
E_ON, E_OFF = 0.5, 1.0
TURB_WIN, TURB_MIN_ROOTS, TURB_MIN_COL, TURB_MIN_ROWS = 60, 18, 55, 40
RIDGE = 1e-8
HMM_MIN_OBS, HMM_ITERS, HMM_TOL, HMM_P = 504, 200, 1e-8, 0.7
CORR_WIN, CORR_MIN = 60, 50
Q_TERC = 2.0 / 3.0
MA_MONTHS = 10
FILL_DAYS = pd.Timedelta("5D")                  # R06 regime-state forward-fill tolerance
N_SHIFTS, SEED = 300, 0
SC = pd.Timedelta(hours=17)

_SEAL = {"n_asserts": 0, "n_dropped": 0}
_LINES: list[str] = []


def say(s: str = "") -> None:
    print(s)
    _LINES.append(s)


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


# ------------------------------------------------------------------ NQ session table
def load_nq_sessions() -> pd.DataFrame:
    f = pq.ParquetFile(DEEP)
    acc: dict = {}
    order: list = []
    prev_label, prev_logc = None, None
    for g in range(f.metadata.num_row_groups):
        t = f.read_row_group(g, columns=["time", "close"]).to_pandas()
        t["time"] = pd.to_datetime(t["time"], format="%Y-%m-%d %H:%M:%S")
        t, nd = truncate_presealed(t, "time", f"NQ deep rg{g}")
        assert_presealed(t, "time", f"NQ deep rg{g}:post")
        _SEAL["n_asserts"] += 1
        _SEAL["n_dropped"] += nd
        t = t[t["time"] <= NQ_CAP]  # discovery cap (R01) — 2019+ NQ rows never used
        if len(t) == 0:
            continue
        if not t["time"].is_monotonic_increasing:
            raise RuntimeError(f"NQ rg{g}: time not monotonic")
        day = t["time"].dt.normalize()
        tod = t["time"] - day
        label = day.where(tod <= SC, day + pd.Timedelta(days=1))
        logc = np.log(t["close"].to_numpy())
        lab = label.to_numpy()
        d = np.diff(logc)
        same = lab[1:] == lab[:-1]
        d_first = np.nan
        if prev_label is not None and lab[0] == prev_label:
            d_first = logc[0] - prev_logc
        dd = np.concatenate([[d_first], np.where(same, d, np.nan)])
        prev_label, prev_logc = lab[-1], logc[-1]
        d2 = np.where(np.isnan(dd), 0.0, np.square(dd))
        ch = pd.DataFrame({"label": lab, "close": t["close"].to_numpy(), "d2": d2})
        gb = ch.groupby("label", sort=False)
        agg = gb.agg(rv=("d2", "sum"), n=("d2", "size"), close=("close", "last"))
        for lb, row in agg.iterrows():
            if lb in acc:
                a = acc[lb]
                a[0] += row["rv"]
                a[1] += int(row["n"])
                a[2] = row["close"]
            else:
                acc[lb] = [row["rv"], int(row["n"]), row["close"]]
                order.append(lb)
    s = pd.DataFrame(
        {"label": order,
         "rv": [acc[k][0] for k in order],
         "n_bars": [acc[k][1] for k in order],
         "close": [acc[k][2] for k in order]}
    )
    if not s["label"].is_monotonic_increasing:
        raise RuntimeError("session labels not monotonic")
    return s.reset_index(drop=True)


# ------------------------------------------------------------------ 2-state Gaussian HMM
def _gauss_b(x, mu, var):
    b = np.exp(-0.5 * (x[:, None] - mu[None, :]) ** 2 / var[None, :]) / np.sqrt(2 * np.pi * var[None, :])
    return np.maximum(b, 1e-300)


def _forward_scaled(B, A, pi):
    """Scaled forward pass; scalar-arithmetic recursion (2 states) for speed.
    Returns (alpha[n,2], c[n])."""
    n = B.shape[0]
    B0, B1 = B[:, 0].tolist(), B[:, 1].tolist()
    A00, A01, A10, A11 = float(A[0, 0]), float(A[0, 1]), float(A[1, 0]), float(A[1, 1])
    a0 = float(pi[0]) * B0[0]
    a1 = float(pi[1]) * B1[0]
    c0 = a0 + a1
    a0 /= c0
    a1 /= c0
    al0, al1, cs = [a0], [a1], [c0]
    for t in range(1, n):
        n0 = (a0 * A00 + a1 * A10) * B0[t]
        n1 = (a0 * A01 + a1 * A11) * B1[t]
        ct = n0 + n1
        a0, a1 = n0 / ct, n1 / ct
        al0.append(a0)
        al1.append(a1)
        cs.append(ct)
    return np.column_stack([al0, al1]), np.asarray(cs)


def _backward_scaled(B, A, c):
    n = B.shape[0]
    B0, B1 = B[:, 0].tolist(), B[:, 1].tolist()
    A00, A01, A10, A11 = float(A[0, 0]), float(A[0, 1]), float(A[1, 0]), float(A[1, 1])
    cl = c.tolist()
    b0, b1 = 1.0, 1.0
    be0, be1 = [0.0] * n, [0.0] * n
    be0[-1], be1[-1] = 1.0, 1.0
    for t in range(n - 2, -1, -1):
        x0 = B0[t + 1] * b0
        x1 = B1[t + 1] * b1
        b0 = (A00 * x0 + A01 * x1) / cl[t + 1]
        b1 = (A10 * x0 + A11 * x1) / cl[t + 1]
        be0[t], be1[t] = b0, b1
    return np.column_stack([be0, be1])


def em2(x):
    med = np.median(x)
    lo, hi = x[x <= med], x[x > med]
    mu = np.array([lo.mean(), hi.mean()])
    var = np.array([max(lo.var(), 1e-12), max(hi.var(), 1e-12)])
    A = np.array([[0.97, 0.03], [0.03, 0.97]])
    pi = np.array([0.5, 0.5])
    prev_ll, conv = -np.inf, False
    for _ in range(HMM_ITERS):
        B = _gauss_b(x, mu, var)
        alpha, c = _forward_scaled(B, A, pi)
        beta = _backward_scaled(B, A, c)
        gamma = alpha * beta
        gamma /= gamma.sum(axis=1, keepdims=True)
        # xi summed over t: A ⊙ (alpha[:-1]^T @ (B[1:]*beta[1:]/c[1:]))  (vectorized)
        Bb = (B[1:] * beta[1:]) / c[1:][:, None]
        xi = A * (alpha[:-1].T @ Bb)
        ll = float(np.log(c).sum())
        pi = gamma[0]
        A = xi / np.maximum(gamma[:-1].sum(axis=0)[:, None], 1e-300)
        A /= A.sum(axis=1, keepdims=True)
        w = gamma.sum(axis=0)
        mu = (gamma * x[:, None]).sum(axis=0) / w
        var = np.maximum((gamma * (x[:, None] - mu[None, :]) ** 2).sum(axis=0) / w, 1e-12)
        if abs(ll - prev_ll) < HMM_TOL * max(1.0, abs(ll)):
            conv = True
            break
        prev_ll = ll
    return {"mu": mu, "var": var, "A": A, "pi": pi}, conv


def filtered_p_hi(x, params):
    mu, var, A, pi = params["mu"], params["var"], params["A"], params["pi"]
    hi = int(np.argmax(mu))
    B = _gauss_b(x, mu, var)
    alpha, _ = _forward_scaled(B, A, pi)
    return alpha[:, hi]


# ------------------------------------------------------------------ scoring machinery
def log1p_path(e, r, close):
    e_prev = np.concatenate([[0.0], e[:-1]])
    cost = COST_RT * np.abs(e - e_prev) / (PT_USD * close)
    return np.log1p(e * r - cost)


def timing_and_path(e, r, close):
    lw = log1p_path(e, r, close)
    ebar = float(np.mean(e))
    lwc = log1p_path(np.full_like(e, ebar), r, close)
    return float(lw.sum() - lwc.sum()), lw, lwc, ebar


def maxdd(lw):
    W = np.exp(np.cumsum(lw))
    return float(np.max(1.0 - W / np.maximum.accumulate(W)))


def expanding_q_shift1(x: pd.Series, q: float, min_obs: int) -> pd.Series:
    return x.expanding(min_periods=min_obs).quantile(q).shift(1)


def make_stat_fn():
    def stat(decisions, base):
        sc = base["scored"].to_numpy()
        e_leg = np.asarray(decisions, dtype=float)[sc]
        r = base["r_next"].to_numpy()[sc]
        close = base["close"].to_numpy()[sc]
        e_rv = base["e_rv"].to_numpy()[sc]
        t_leg, _, _, _ = timing_and_path(e_leg, r, close)
        t_rv, _, _, _ = timing_and_path(e_rv, r, close)
        return t_leg - t_rv
    return stat


def dec_threshold(colq: float):
    def dec(frame):
        x = frame["input"].reset_index(drop=True)
        thr = expanding_q_shift1(x, colq, BURN_IN)
        on = x.notna() & thr.notna() & (x > thr)
        return np.where(on.to_numpy(), E_ON, E_OFF)
    return dec


def dec_fixed(th: float):
    def dec(frame):
        x = frame["input"].to_numpy(dtype=float)
        on = np.isfinite(x) & (x > th)
        return np.where(on, E_ON, E_OFF)
    return dec


def dec_binary(frame):
    x = frame["input"].to_numpy(dtype=float)
    on = np.isfinite(x) & (x == 1.0)
    return np.where(on, E_ON, E_OFF)


# ------------------------------------------------------------------ main
def main():
    say("G2_F8_DUO_20260829 sub-run B — GATE TABLE (printed by program; trial G00038, card MC-53)")
    say("type RISK_SPECIFICATION / REGIME ROUTING — sizing study; NEVER an information-alpha claim. No Sharpe printed.")
    say("DISCOVERY ON 2006-2018 ONLY (skeptic restriction; spec.yaml sub_runs.B). Evidence status: DISCOVERY_CONSUMED.")

    # provenance
    dsha = sha256_file(DEEP)
    if dsha != DEEP_SHA:
        say(f"DEFECT: deep NQ parquet sha256 mismatch ({dsha[:16]}... != provenance)")
        raise SystemExit(1)
    psha, vsha = sha256_file(PANEL), sha256_file(VXN)
    say(f"provenance: deep NQ sha256 MATCHES run_provenance.txt; panel sha256 {psha[:16]}..., VXN sha256 {vsha[:16]}... (recorded as this run's baseline)")

    # ---- loads (every one through seal_guard) ----
    tbl = pq.read_table(PANEL, columns=["date", "root", "ret_usd"],
                        filters=[("date", "<=", DATE_MAX)])
    panel = tbl.to_pandas()
    assert_presealed(panel, "date", "multi-market panel (post-filter)")
    _SEAL["n_asserts"] += 1
    pmax = panel["date"].max()
    say(f"PANEL LOAD: date_max filter <= {DATE_MAX.date()} applied INSIDE the read; "
        f"max loaded date = {pmax.date()} ; rows {len(panel)} ; roots {panel['root'].nunique()} "
        f"; min date {panel['date'].min().date()}  [P-2: 2019+ multi-market NEVER materialized]")
    if pmax > DATE_MAX:
        say("DEFECT: panel filter failed")
        raise SystemExit(1)
    for need in ("NQ", "ZN"):
        if need not in set(panel["root"]):
            say(f"DEFECT: panel missing root {need}")
            raise SystemExit(1)

    ndup = int(panel.duplicated(["date", "root"]).sum())
    say(f"panel duplicate (date,root) rows: {ndup} (first kept)")
    wide = (panel.drop_duplicates(["date", "root"], keep="first")
                 .pivot(index="date", columns="root", values="ret_usd")
                 .sort_index())

    vx = pq.read_table(VXN, columns=["date", "close"]).to_pandas()
    assert_presealed(vx, "date", "VXN certified daily")
    _SEAL["n_asserts"] += 1
    vx = vx[vx["date"] <= DATE_MAX].sort_values("date").reset_index(drop=True)
    if len(vx) == 0:
        say("DEFECT: VXN empty pre-2019")
        raise SystemExit(1)
    say(f"VXN capped: {vx['date'].min().date()} .. {vx['date'].max().date()} ({len(vx)} rows)")

    s = load_nq_sessions()
    say(f"NQ sessions (deep substrate only, capped {NQ_CAP}): {len(s)} sessions "
        f"{s['label'].iloc[0].date()} .. {s['label'].iloc[-1].date()}; "
        f"seal_guard: {_SEAL['n_asserts']} asserts, {_SEAL['n_dropped']} post-seal rows dropped")

    # ---- base series ----
    s["r_next"] = s["close"].shift(-1) / s["close"] - 1.0
    s["target_label"] = s["label"].shift(-1)
    s["rv21"] = s["rv"].rolling(RV_WIN, min_periods=RV_WIN).mean()
    thr_rv = expanding_q_shift1(s["rv21"], Q_CTRL, BURN_IN)
    s["e_rv"] = np.where(s["rv21"].notna() & thr_rv.notna(),
                         np.where(s["rv21"] >= thr_rv, E_ON, E_OFF), np.nan)

    # ---- L1 turbulence ----
    valid = wide.notna().sum(axis=1) >= TURB_MIN_ROOTS
    V = wide.loc[valid]
    dates = V.index.to_numpy()
    M = V.to_numpy()
    n_days, n_roots = M.shape
    turb = np.full(n_days, np.nan)
    for j in range(TURB_WIN, n_days):
        r_d = M[j]
        W = M[j - TURB_WIN:j]
        colsok = ~np.isnan(r_d) & (np.sum(~np.isnan(W), axis=0) >= TURB_MIN_COL)
        if colsok.sum() < 2:
            continue
        Wc = W[:, colsok]
        rows = ~np.isnan(Wc).any(axis=1)
        if rows.sum() < TURB_MIN_ROWS:
            continue
        Ww = Wc[rows]
        mu = Ww.mean(axis=0)
        S = np.cov(Ww, rowvar=False)
        S = S + RIDGE * np.mean(np.diag(S)) * np.eye(S.shape[0])
        try:
            z = np.linalg.solve(S, r_d[colsok] - mu)
        except np.linalg.LinAlgError:
            continue
        turb[j] = float((r_d[colsok] - mu) @ z) / colsok.sum()
    turb_s = pd.DataFrame({"date": dates, "turb": turb}).dropna()
    say(f"L1 turbulence: {len(turb_s)} panel days with a defined distance "
        f"({turb_s['date'].min().date()} .. {turb_s['date'].max().date()}); valid panel days {n_days}, roots {n_roots}")

    # ---- L2 HMM filtered P ----
    hmask = (s["n_bars"] >= 200) & (s["rv"] > 0)
    hx = np.log(s.loc[hmask, "rv"].to_numpy())
    hidx = s.index[hmask].to_numpy()
    hlab = s.loc[hmask, "label"]
    months = hlab.dt.to_period("M")
    p_event = np.full(len(s), np.nan)
    n_refit = n_conv = 0
    uniq = months.unique()
    for m in uniq:
        pos = np.flatnonzero((months == m).to_numpy())
        first = pos[0]
        if first < HMM_MIN_OBS:
            continue
        params, conv = em2(hx[:first])
        n_refit += 1
        n_conv += int(conv)
        pf = filtered_p_hi(hx[: pos[-1] + 1], params)
        p_event[hidx[pos]] = pf[pos]
    if n_refit == 0 or (n_refit - n_conv) / n_refit > 0.10:
        say(f"DEFECT: HMM convergence {n_conv}/{n_refit}")
        raise SystemExit(1)
    s["p_hmm"] = p_event
    say(f"L2 HMM: {n_refit} monthly refits (frozen calendar, expanding, min {HMM_MIN_OBS} obs), "
        f"{n_conv} converged; P(event) defined on {int(np.isfinite(p_event).sum())} sessions")

    # ---- L3 composite ----
    both = wide[["NQ", "ZN"]].dropna()
    corr60 = both["NQ"].rolling(CORR_WIN, min_periods=CORR_MIN).corr(both["ZN"])
    corr_s = pd.DataFrame({"date": both.index, "corr": corr60.to_numpy()}).dropna()

    def asof_join(base_labels: pd.Series, right: pd.DataFrame, col: str) -> tuple[pd.Series, int, int]:
        m = pd.merge_asof(pd.DataFrame({"label": base_labels}), right.rename(columns={right.columns[0]: "date"}),
                          left_on="label", right_on="date", direction="backward", tolerance=FILL_DAYS)
        exact = int((m["date"] == m["label"]).sum())
        filled = int(m[col].notna().sum() - exact)
        return m[col], exact, filled

    s_turb, te, tf = asof_join(s["label"], turb_s[["date", "turb"]], "turb")
    s_corr, ce, cf = asof_join(s["label"], corr_s[["date", "corr"]], "corr")
    s_vxn, ve, vf = asof_join(s["label"], vx[["date", "close"]].rename(columns={"close": "vxn"}), "vxn")
    s["turb"] = s_turb.to_numpy()
    s["corr60"] = s_corr.to_numpy()
    s["vxn"] = s_vxn.to_numpy()
    say(f"R06 joins to sessions (exact / forward-filled<=5d): turb {te}/{tf}, corr60 {ce}/{cf}, VXN {ve}/{vf}")

    def z_exp(x: pd.Series) -> pd.Series:
        mu = x.expanding(min_periods=BURN_IN).mean().shift(1)
        sd = x.expanding(min_periods=BURN_IN).std().shift(1)
        return (x - mu) / sd

    zc = pd.concat([z_exp(s["vxn"]), z_exp(s["rv21"]), z_exp(s["corr60"])], axis=1)
    s["composite"] = zc.mean(axis=1, skipna=False)

    # ---- L4 10m MA ----
    mo = s["label"].dt.to_period("M")
    mclose = s.groupby(mo)["close"].last()
    ma10 = mclose.rolling(MA_MONTHS, min_periods=MA_MONTHS).mean().shift(1)  # last 10 COMPLETED months
    s["ma10"] = mo.map(ma10).to_numpy()
    s["ma_state"] = np.where(np.isfinite(s["ma10"]) & (s["close"] < s["ma10"]), 1.0,
                             np.where(np.isfinite(s["ma10"]), 0.0, np.nan))

    # ---- leg frames ----
    def leg_frame(input_col: str, state_from_thresh: float | None, name: str):
        """Frame starts at the input's FIRST non-NaN row so decision_fn's expanding
        threshold (recomputed inside the frame, real and null alike) sees exactly the
        same history as the s-level series (leading NaNs never count toward
        min_periods). 'scored' additionally requires the threshold to exist."""
        x = s[input_col]
        defined_input = x.notna()
        if state_from_thresh is not None:
            thr = expanding_q_shift1(x, state_from_thresh, BURN_IN)
            defined = defined_input & thr.notna()
        else:
            defined = defined_input
        scored = (defined & s["e_rv"].notna() & s["r_next"].notna()
                  & (s["label"] >= APP_START) & (s["target_label"] <= DATE_MAX))
        if scored.sum() == 0:
            return None
        i0, i1 = int(np.flatnonzero(defined_input)[0]), int(np.flatnonzero(scored)[-1])
        fr = pd.DataFrame({
            "session": s["label"].iloc[i0:i1 + 1].dt.strftime("%Y-%m-%d"),
            "input": x.iloc[i0:i1 + 1].to_numpy(),
            "scored": scored.iloc[i0:i1 + 1].to_numpy(),
            "r_next": s["r_next"].iloc[i0:i1 + 1].to_numpy(),
            "close": s["close"].iloc[i0:i1 + 1].to_numpy(),
            "e_rv": s["e_rv"].iloc[i0:i1 + 1].to_numpy(),
            "target": s["target_label"].iloc[i0:i1 + 1].to_numpy(),
            "rv21": s["rv21"].iloc[i0:i1 + 1].to_numpy(),
        }).reset_index(drop=True)
        return fr

    legs = {
        "L1_TURB": dict(frame=leg_frame("turb", Q_CTRL, "L1"), dec=dec_threshold(Q_CTRL),
                        desc="Mahalanobis turbulence > expanding 90th pct -> 0.5x  [FROZEN PRIMARY]"),
        "L2_HMM": dict(frame=leg_frame("p_hmm", None, "L2"), dec=dec_fixed(HMM_P),
                       desc="2-state Gaussian HMM on log NQ daily RV, filtered P(event)>0.7 -> 0.5x"),
        "L3_COMPOSITE": dict(frame=leg_frame("composite", Q_TERC, "L3"), dec=dec_threshold(Q_TERC),
                             desc="z-composite{VXN,21dRV,60d stock-bond corr} top expanding tercile -> 0.5x"),
        "L4_MA10M": dict(frame=leg_frame("ma_state", None, "L4"), dec=dec_binary,
                         desc="close < 10-month MA -> 0.5x (GTT trend leg)"),
    }
    if legs["L1_TURB"]["frame"] is None:
        say("DEFECT: FROZEN PRIMARY leg has an empty scored subset")
        raise SystemExit(1)

    stat_fn = make_stat_fn()
    results = {}
    say("")
    say("event counts / null bands / MDEs — PRINTED BEFORE VERDICTS (R11/R12):")
    expo_common = {}
    for name, L in legs.items():
        fr = L["frame"]
        if fr is None:
            say(f"  {name}: NO SCORED ROWS — leg not scoreable in the discovery window")
            continue
        dec = L["dec"]
        e_all = dec(fr)
        sc = fr["scored"].to_numpy()
        e_leg = e_all[sc]
        r = fr["r_next"].to_numpy()[sc]
        close = fr["close"].to_numpy()[sc]
        e_rv = fr["e_rv"].to_numpy()[sc]
        tgt = pd.to_datetime(fr["target"].to_numpy()[sc])
        t_leg, lw_leg, lwc_leg, ebar_leg = timing_and_path(e_leg, r, close)
        t_rv, lw_rv, lwc_rv, ebar_rv = timing_and_path(e_rv, r, close)
        delta = t_leg - t_rv
        n_on = int((e_leg == E_ON).sum())
        n_reb = int((np.diff(e_leg) != 0).sum() + 1)
        f_on = n_on / sc.sum()

        # reported-only frequency-matched RV control (R12) — rv21 carried in the frame
        rv21_fr = fr["rv21"].reset_index(drop=True)
        thr_fm = expanding_q_shift1(rv21_fr, 1.0 - f_on, BURN_IN)
        e_fm_all = np.where(rv21_fr.notna().to_numpy() & thr_fm.notna().to_numpy()
                            & (rv21_fr.to_numpy() >= thr_fm.to_numpy()), E_ON, E_OFF)
        e_fm = e_fm_all[sc]
        t_fm, lw_fm, _, _ = timing_and_path(e_fm, r, close)

        # null (shared family seed)
        loader = (lambda fr=fr: fr.copy())
        verify_null_sensitivity(loader, dec, stat_fn, shifts=[1, 7, 61], unit="session")
        null = run_circular_null(loader, dec, stat_fn, n_shifts=N_SHIFTS, unit="session", seed=SEED)
        arr = np.asarray(null["null_stats"])
        p95 = float(np.quantile(arr, 0.95))
        med = float(np.median(arr))
        years = (tgt.max() - tgt.min()).days / 365.25
        era1 = (tgt <= ERA_SPLIT)
        d_era1 = float((lw_leg - lwc_leg - lw_rv + lwc_rv)[era1].sum())
        d_era2 = float((lw_leg - lwc_leg - lw_rv + lwc_rv)[~era1].sum())
        results[name] = dict(frame=fr, delta=delta, t_leg=t_leg, t_rv=t_rv, t_fm=t_fm,
                             null=null, p95=p95, med=med, n=int(sc.sum()), n_on=n_on,
                             n_reb=n_reb, ebar_leg=ebar_leg, ebar_rv=ebar_rv,
                             dd_leg=maxdd(lw_leg), dd_rv=maxdd(lw_rv),
                             d_era1=d_era1, d_era2=d_era2, f_on=f_on,
                             lw_leg=lw_leg, lw_rv=lw_rv, tgt=tgt, years=years)
        expo_common[name] = pd.Series(e_leg, index=tgt)
        say(f"  {name}: scored {int(sc.sum())} sessions {tgt.min().date()}..{tgt.max().date()} | "
            f"state-on {n_on} ({100*f_on:.1f}%) | rebalances {n_reb} | mean e leg {ebar_leg:.4f} vs rv-ctrl {ebar_rv:.4f}")
        say(f"    null ({N_SHIFTS} circular shifts, seed {SEED}, shared family seed): median {med:+.6f}, "
            f"p95 {p95:+.6f} log-wealth -> MDE = {p95:+.6f} over window ({p95/years:+.6f}/yr)")

    # effective K (R10)
    common = None
    for name, e in expo_common.items():
        common = e.index if common is None else common.intersection(e.index)
    rhos = []
    names = list(expo_common)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a = expo_common[names[i]].loc[common].to_numpy()
            b = expo_common[names[j]].loc[common].to_numpy()
            if a.std() > 0 and b.std() > 0:
                rhos.append(abs(float(np.corrcoef(a, b)[0, 1])))
    rho_bar = float(np.mean(rhos)) if rhos else 0.0
    k_eff = len(names) / (1.0 + (len(names) - 1) * rho_bar)
    fam_q = 1.0 - 0.05 / k_eff
    say(f"  family multiplicity (R10): K={len(names)}, rho_bar={rho_bar:.3f} (mean |pairwise corr| of exposures, "
        f"common N={len(common)}), K_eff={k_eff:.2f} -> family-adjusted null quantile {fam_q:.4f}")
    say("")
    say("CAVEATS (printed with results, per spec):")
    say("  * CORR-SIGN LEG NOT RUN: demoted by the skeptic to the confirmation-only shelf — the stock-bond-")
    say("    correlation regime's ENTIRE modern evidence is 2022+ (N-bound: one episode) and sits inside the")
    say("    2019+ multi-market reserve (P-2).")
    say("  * L3_COMPOSITE carries the same caveat: its 60d stock-bond-corr ingredient's modern evidence is")
    say("    2022+-only; its discovery reading here is 2006-2018 covariance data only.")
    say("  * BEX index / FRED macro-gate legs NOT RUN (owner-gated acquisitions, OWNER_QUEUE).")
    say("  * Any survivor is DISCOVERY-grade with its 2019+ confirmation explicitly RESERVED (one future")
    say("    preregistered one-shot, NOT this run).")
    say("")
    say("GATE  SPEC                                                              OBSERVED                                                                    PASS-FAIL")
    verdicts = {}
    for name, R in results.items():
        v1 = R["delta"] > 0
        dd_bar = 1.05 * R["dd_rv"]
        v2 = R["dd_leg"] <= dd_bar
        v3 = R["delta"] > R["p95"]
        fam_bar = float(np.quantile(np.asarray(R["null"]["null_stats"]), fam_q))
        fam_ok = R["delta"] > fam_bar
        ok = v1 and v2 and v3
        verdicts[name] = dict(v1=v1, v2=v2, v3=v3, ok=ok, fam_ok=fam_ok, fam_bar=fam_bar)
        say(f"{name}.V1  DELTA(timing leg - timing rv-ctrl) > 0                         {R['delta']:+.6f}  (timing leg {R['t_leg']:+.6f} vs rv {R['t_rv']:+.6f})                     {'PASS' if v1 else 'FAIL'}")
        say(f"{name}.V2  maxDD(leg) <= 1.05*maxDD(rv-ctrl)                              {100*R['dd_leg']:.4f}% vs bar {100*dd_bar:.4f}% (ctrl {100*R['dd_rv']:.4f}%)                        {'PASS' if v2 else 'FAIL'}")
        say(f"{name}.V3  DELTA > p95 of {N_SHIFTS} circular-shift null                       {R['delta']:+.6f} vs p95 {R['p95']:+.6f} (pct {100*R['null']['percentile']:.1f}%, p_ge {R['null']['p_ge']:.4f})          {'PASS' if v3 else 'FAIL'}")
        say(f"{name}.R12  reported: freq-matched RV ctrl timing {R['t_fm']:+.6f} (DELTA_fm {R['t_leg']-R['t_fm']:+.6f}); era DELTA <=2012 {R['d_era1']:+.6f} / >2012 {R['d_era2']:+.6f}; family bar {fam_bar:+.6f} -> {'clears' if fam_ok else 'below'}")
    say("")
    for name, R in results.items():
        v = verdicts[name]
        tag = "PASS — DISCOVERY-grade; 2019+ one-shot confirmation RESERVED (not this run)" if v["ok"] else "FAIL — a FAIL is a FAIL"
        fam = "" if not v["ok"] else ("  [family-adjusted bar also cleared]" if v["fam_ok"] else "  [FAMILY-MARGINAL: below family-adjusted bar]")
        say(f"VERDICT {name} (G00038): {tag}  [V1 {'P' if v['v1'] else 'F'} V2 {'P' if v['v2'] else 'F'} V3 {'P' if v['v3'] else 'F'}]{fam}")
    n_pass = sum(v["ok"] for v in verdicts.values())
    say(f"VERDICT MC-53 CARD: {n_pass}/{len(verdicts)} legs survive vs the MC-51-frozen RV-only throttle. "
        + ("Total collapse into the RV control — the skeptic's honest expected outcome materialized." if n_pass == 0
           else "Surviving legs are DISCOVERY-grade only; the 2019+ pristine window remains RESERVED."))
    say("LIVE = NO · $0 spent · POINTS/normalized units · no Sharpe printed.")

    # wealth paths
    rows = []
    for name, R in results.items():
        W_leg = np.exp(np.cumsum(R["lw_leg"]))
        W_rv = np.exp(np.cumsum(R["lw_rv"]))
        for d, wl, wr in zip(R["tgt"], W_leg, W_rv):
            rows.append((name, d.date().isoformat(), wl, wr))
    pd.DataFrame(rows, columns=["leg", "date", "w_leg", "w_rv_ctrl"]).to_csv(
        os.path.join(OUTB, "wealth_paths.csv"), index=False)

    with open(os.path.join(OUTB, "gate_table.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(_LINES) + "\n")

    ledger = [{
        "trial_id": "G00038",
        "metrics": {
            "card": "MC-53 cross-asset regime states for sizing (restricted discovery)",
            "window": "target sessions 2006-01-01..2018-12-31 (skeptic restriction; panel date_max 2018-12-31 in-read)",
            "panel_max_loaded_date": str(pmax.date()),
            "legs": {name: {
                "n_scored": R["n"], "n_state_on": R["n_on"], "n_rebalances": R["n_reb"],
                "mean_e_leg": round(R["ebar_leg"], 6), "mean_e_rv_ctrl": round(R["ebar_rv"], 6),
                "timing_leg_logw": round(R["t_leg"], 6), "timing_rv_ctrl_logw": round(R["t_rv"], 6),
                "delta_logw": round(R["delta"], 6),
                "maxdd_leg": round(R["dd_leg"], 6), "maxdd_rv_ctrl": round(R["dd_rv"], 6),
                "null_median": round(R["med"], 6), "null_p95_MDE": round(R["p95"], 6),
                "null_percentile": round(R["null"]["percentile"], 4), "null_p_ge": round(R["null"]["p_ge"], 4),
                "era_delta_le2012": round(R["d_era1"], 6), "era_delta_gt2012": round(R["d_era2"], 6),
                "freq_matched_rv_timing": round(R["t_fm"], 6),
                "gates": {k: bool(verdicts[name][k]) for k in ("v1", "v2", "v3")},
                "result": "PASS" if verdicts[name]["ok"] else "FAIL",
            } for name, R in results.items()},
            "family": {"K": len(names), "rho_bar": round(rho_bar, 4), "K_eff": round(k_eff, 3)},
            "legs_not_run": {"corr_sign": "demoted to confirmation-only shelf (episode inside 2019+ reserve)",
                             "bex_fred": "owner-gated (OWNER_QUEUE)"},
            "classification": "RISK SPECIFICATION / REGIME ROUTING (sizing)",
            "evidence_status": "DISCOVERY_CONSUMED",
            "pristine": "P-2 protected: 2019+ multi-market never loaded; survivors' 2019+ confirmation RESERVED",
        },
        "result": "PASS" if n_pass > 0 else "FAIL",
        "note": ("Card MC-53 restricted per skeptic: discovery 2006-2018 only; four legs (turbulence 90th pct, "
                 "HMM P>0.7, composite tercile, 10m MA) each 0.5x-throttled vs the MC-51-frozen RV-only throttle "
                 "at matched mean exposure (timing components), $33/RT, 300 circular-shift shared-seed null. "
                 "Corr-sign leg demoted (not run); BEX/FRED owner-gated. Resolutions in outB/spec_resolutions.txt."),
    }]
    with open(os.path.join(OUTB, "ledger_result_pending.json"), "w", encoding="utf-8") as f:
        json.dump(ledger, f, indent=2)
    say(f"wrote outB/gate_table.txt, outB/ledger_result_pending.json, outB/wealth_paths.csv")


if __name__ == "__main__":
    main()
