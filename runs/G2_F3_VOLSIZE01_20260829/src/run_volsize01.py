"""G2_F3_VOLSIZE01_20260829 — MC-51 extremes-only vol-managed sizing (trial G00025)
with the MC-38 HAR race nested as the vol-input arm (trial G00026).

Preregistered spec: runs/G2_F3_VOLSIZE01_20260829/spec.yaml (FROZEN).
Ambiguity resolutions R01-R20: out/spec_resolutions.txt (written BEFORE this program ran).
Gate table is PRINTED BY THIS PROGRAM (GATE/SPEC/OBSERVED/PASS-FAIL). No parameter
search occurs anywhere in this file: 21/5/22 windows, 252-obs burn-in, 0.10/0.90
deciles, 1.5x/0.5x/1.0x, $33/RT, the 2006-2017/2018-2026-05 split, NW lag 5 and the
10%/50% throttle are all spec/resolution constants. RISK SPECIFICATION only — no
information-alpha claim, no Sharpe computed or printed.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import sys
from datetime import date

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

REPO = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, REPO)

from research_sdk.seal_guard import assert_presealed, truncate_presealed
from research_sdk.session_boundary import assert_not_locked_forward
from research_sdk.null_guard import run_circular_null, verify_null_sensitivity

RUN_DIR = os.path.join(REPO, "runs", "G2_F3_VOLSIZE01_20260829")
OUT = os.path.join(RUN_DIR, "out")

DEEP = os.path.join(REPO, r"research\scalping_lab\substrate\minute\NQ\nq1m_2005_202605.parquet")
MODERN = os.path.join(REPO, r"runs\SM1M_SUBSTRATE\out\nq_1m_2022_2026.parquet")
PROV_HASHES = {  # runs/GENESIS_REPRO_INCUMBENT_20260828/out/run_provenance.txt
    DEEP: "dfd017eff0b031c2be89639fc4ad347d45053867edcdc2600002252b10b627cf",
    MODERN: "87aa53f007aa47b9ee10d0080317a3cde8d22b55aa368267fa9a4aed7435295d",
}

PT_USD = 20.0          # NQ $/pt
COST_RT = 33.0         # $/RT per rebalance contract (spec)
RV_WIN = 21            # plain 21d RV window (spec)
BURN_IN = 252          # min prior obs for expanding deciles (R06)
Q_LO, Q_HI = 0.10, 0.90
E_LO, E_MID, E_HI = 1.5, 1.0, 0.5   # bottom-decile / mid / top-decile exposure (spec)
APP_START = pd.Timestamp("2006-01-01")
APP_END = pd.Timestamp("2026-05-31")
DEEP_LAST = pd.Timestamp("2021-12-31")
ERA1_END = pd.Timestamp("2015-12-31")
TRAIN_FIRST, TRAIN_LAST = pd.Timestamp("2006-01-01"), pd.Timestamp("2017-12-31")
TEST_FIRST, TEST_LAST = pd.Timestamp("2018-01-01"), pd.Timestamp("2026-05-31")
MIN_BARS = 200         # R14 degenerate-session filter (HAR pairs only)
FLOOR_F = 1e-10        # R14 forecast floor
NW_LAG = 5             # R15
DD_TRIG, DD_CUT = 0.10, 0.5   # R13 expected-fail throttle
SC = pd.Timedelta(hours=17)   # session close tod
ON_END = pd.Timedelta(hours=9, minutes=30)

_SEAL = {"n_asserts": 0, "n_dropped": 0}


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------- streaming pass
def stream_sessions(path: str, is_str_time: bool, ctx: str) -> pd.DataFrame:
    """One pass, row-group by row-group (bounded memory). Per session: close (17:00
    session close = last bar), n_bars, rv (full-session sum of squared 1-min log
    returns, within-session diffs only), rsneg (negative-return part), onrv
    (overnight-segment part, tod>17:00 or tod<=09:30), close_0930 (last bar <=09:30).
    Seal: truncate_presealed per chunk + assert_presealed (counts recorded)."""
    f = pq.ParquetFile(path)
    acc: dict[pd.Timestamp, list] = {}   # label -> [rv, rsneg, onrv, n, last_close, c0930]
    prev_label, prev_logc = None, None
    prev_last_ts = None
    for g in range(f.metadata.num_row_groups):
        t = f.read_row_group(g, columns=["time", "close"]).to_pandas()
        if is_str_time:
            t["time"] = pd.to_datetime(t["time"], format="%Y-%m-%d %H:%M:%S")
        t, nd = truncate_presealed(t, "time", f"{ctx} rg{g}")
        assert_presealed(t, "time", f"{ctx} rg{g}:post")
        _SEAL["n_asserts"] += 1
        _SEAL["n_dropped"] += nd
        if len(t) == 0:
            continue
        if not t["time"].is_monotonic_increasing:
            raise RuntimeError(f"{ctx} rg{g}: time not monotonic")
        if prev_last_ts is not None and t["time"].iloc[0] < prev_last_ts:
            raise RuntimeError(f"{ctx} rg{g}: row-group ordering broken")
        prev_last_ts = t["time"].iloc[-1]

        day = t["time"].dt.normalize()
        tod = t["time"] - day
        label = day.where(tod <= SC, day + pd.Timedelta(days=1))
        logc = np.log(t["close"].to_numpy())
        lab_np = label.to_numpy()
        # within-session diffs; chunk-boundary continuation handled via prev_*
        d = np.diff(logc)
        same = lab_np[1:] == lab_np[:-1]
        d_first = np.nan
        if prev_label is not None and lab_np[0] == prev_label:
            d_first = logc[0] - prev_logc
        dd = np.concatenate([[d_first], np.where(same, d, np.nan)])
        prev_label, prev_logc = lab_np[-1], logc[-1]

        tod_np = tod.to_numpy()
        on = (tod_np > SC.to_timedelta64()) | (tod_np <= ON_END.to_timedelta64())
        is0930 = tod_np <= ON_END.to_timedelta64()
        d2 = np.square(dd)
        ch = pd.DataFrame({
            "label": lab_np, "close": t["close"].to_numpy(),
            "d2": np.where(np.isnan(dd), 0.0, d2),
            "d2n": np.where(np.isnan(dd) | (dd >= 0), 0.0, d2),
            "d2o": np.where(np.isnan(dd) | ~on, 0.0, d2),
            "c0930": np.where(is0930, t["close"].to_numpy(), np.nan),
        })
        grp = ch.groupby("label", sort=True)
        agg = grp.agg(rv=("d2", "sum"), rsneg=("d2n", "sum"), onrv=("d2o", "sum"),
                      n=("d2", "size"), last_close=("close", "last"),
                      c0930=("c0930", "last"))
        for lab, row in agg.iterrows():
            lab = pd.Timestamp(lab)
            rec = [row["rv"], row["rsneg"], row["onrv"], int(row["n"]),
                   row["last_close"], row["c0930"]]
            if lab in acc:
                o = acc[lab]
                rec = [o[0] + rec[0], o[1] + rec[1], o[2] + rec[2], o[3] + rec[3],
                       rec[4], rec[5] if np.isfinite(rec[5]) else o[5]]
            acc[lab] = rec
        del t, ch, grp, agg
    out = pd.DataFrame(
        [(k, v[0], v[1], v[2], v[3], v[4], v[5]) for k, v in sorted(acc.items())],
        columns=["session", "rv", "rsneg", "onrv", "n_bars", "close", "c0930"])
    print(f"loaded [{ctx}]: {len(out)} sessions ({out['session'].min().date()} .. "
          f"{out['session'].max().date()})")
    return out


# ---------------------------------------------------------------- frozen policy
def exposures_from_rv(rv: pd.Series) -> np.ndarray:
    """R05/R06 frozen rule: input = rolling-21 mean of RV (incl. current); expanding
    STRICTLY-PRIOR deciles with >=252 prior obs; 1.5x bottom / 0.5x top / 1.0x else.
    NaN thresholds -> 1.0 (those positions are never scored)."""
    rv21 = rv.rolling(RV_WIN, min_periods=RV_WIN).mean()
    prior = rv21.shift(1)
    q10 = prior.expanding(min_periods=BURN_IN).quantile(Q_LO)
    q90 = prior.expanding(min_periods=BURN_IN).quantile(Q_HI)
    v, lo, hi = rv21.to_numpy(), q10.to_numpy(), q90.to_numpy()
    e = np.full(len(v), E_MID)
    with np.errstate(invalid="ignore"):
        e[np.less_equal(v, lo, where=np.isfinite(lo), out=np.zeros(len(v), bool))] = E_LO
        e[np.greater_equal(v, hi, where=np.isfinite(hi), out=np.zeros(len(v), bool))] = E_HI
    return e


def path_stats(e: np.ndarray, r: np.ndarray, p: np.ndarray, charge_rebalance=True):
    """R07/R08 wealth math on a scored subset. Entry from flat charged; control gets
    entry cost only. Returns dict with paths and summary."""
    de = np.diff(e, prepend=0.0)
    cost = COST_RT * np.abs(de) / (PT_USD * p) if charge_rebalance else np.zeros_like(r)
    ret_s = e * r - cost
    ebar = float(np.mean(np.abs(e)))
    cost_c = np.zeros_like(r)
    cost_c[0] = COST_RT * ebar / (PT_USD * p[0])
    ret_c = ebar * r - cost_c
    lw_s = np.cumsum(np.log1p(ret_s))
    lw_c = np.cumsum(np.log1p(ret_c))
    def maxdd(lw):
        w = np.exp(lw)
        return float(np.max(1.0 - w / np.maximum.accumulate(w)))
    return {"ebar": ebar, "ret_s": ret_s, "ret_c": ret_c, "lw_s": lw_s, "lw_c": lw_c,
            "logw_s": float(lw_s[-1]), "logw_c": float(lw_c[-1]),
            "maxdd_s": maxdd(lw_s), "maxdd_c": maxdd(lw_c),
            "n_rebal": int(np.sum(np.abs(de[1:]) > 0)),
            "timing": float(lw_s[-1] - lw_c[-1])}


# ---------------------------------------------------------------- DM / QLIKE
def qlike(y: np.ndarray, f: np.ndarray) -> np.ndarray:
    z = y / f
    return z - np.log(z) - 1.0


def dm_test(la: np.ndarray, lb: np.ndarray, lag: int = NW_LAG):
    """DM stat on d = la - lb with Newey-West HAC (Bartlett, lag L), two-sided p."""
    d = la - lb
    n = len(d)
    dbar = float(np.mean(d))
    dc = d - dbar
    g0 = float(np.dot(dc, dc)) / n
    v = g0
    for l in range(1, lag + 1):
        gl = float(np.dot(dc[l:], dc[:-l])) / n
        v += 2.0 * (1.0 - l / (lag + 1.0)) * gl
    se = math.sqrt(max(v, 1e-300) / n)
    stat = dbar / se
    pval = 2.0 * (1.0 - 0.5 * (1.0 + math.erf(abs(stat) / math.sqrt(2.0))))
    return {"n": n, "mean_diff": dbar, "se": se, "stat": stat, "p": pval,
            "mde_mean_diff": 1.96 * se}


def ols_fit(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return beta


# ================================================================ main
def main() -> None:
    print("G2_F3_VOLSIZE01_20260829 — driver start")
    print("data_esnq NOT read by this run (no ES leg in spec) — ALLOWLIST_DEV_44 not "
          "exercised. Blind pools untouched. No CrossTrade calls. $0 spent.")

    # -------- provenance hash check (R01/R20)
    hash_ok = True
    for pth, want in PROV_HASHES.items():
        got = sha256_file(pth)
        ok = got == want
        hash_ok &= ok
        print(f"provenance sha256 {'MATCH' if ok else 'MISMATCH'}: {os.path.basename(pth)} {got[:16]}...")
    if not hash_ok:
        raise RuntimeError("DEFECT: substrate hash mismatch vs GENESIS_REPRO_INCUMBENT provenance")
    assert_not_locked_forward(date(2026, 5, 31))

    # -------- streaming session pass (bounded memory)
    deep = stream_sessions(DEEP, True, "VOLSIZE01:deep")
    modern = stream_sessions(MODERN, False, "VOLSIZE01:modern")
    deep = deep[deep["session"] <= DEEP_LAST].copy()
    modern = modern[(modern["session"] >= pd.Timestamp("2022-01-01"))
                    & (modern["session"] <= APP_END)].copy()
    deep["substrate"] = "deep"
    modern["substrate"] = "modern"
    tab = pd.concat([deep, modern], ignore_index=True).sort_values("session").reset_index(drop=True)
    if tab["session"].duplicated().any():
        raise RuntimeError("DEFECT: duplicate session labels across substrates")
    assert_presealed(tab, "session", "VOLSIZE01:session-table")
    _SEAL["n_asserts"] += 1

    # -------- splice-week drop set (R03): ISO week (2022, 1)
    iso = tab["session"].dt.isocalendar()
    dropset = (iso["year"].to_numpy() == 2022) & (iso["week"].to_numpy() == 1)
    n_dropweek = int(dropset.sum())

    # -------- returns and validity (R04)
    n = len(tab)
    close = tab["close"].to_numpy()
    lab = tab["session"].to_numpy()
    sub = tab["substrate"].to_numpy()
    r_next = np.full(n, np.nan)
    r_next[:-1] = close[1:] / close[:-1] - 1.0
    r_valid = np.zeros(n, dtype=bool)
    r_valid[:-1] = (sub[1:] == sub[:-1]) & ~dropset[1:]
    r_valid &= np.isfinite(r_next)

    # -------- exposures (real arrangement) + scored set
    e_real = exposures_from_rv(tab["rv"])
    rv21 = tab["rv"].rolling(RV_WIN, min_periods=RV_WIN).mean()
    q_valid = rv21.shift(1).expanding(min_periods=BURN_IN).quantile(Q_LO).notna().to_numpy()
    i0 = int(np.argmax(q_valid)) if q_valid.any() else n
    scored = q_valid & (tab["session"].to_numpy() >= np.datetime64(APP_START)) & r_valid
    SCORED = np.flatnonzero(scored)
    if len(SCORED) < 1000:
        raise RuntimeError("DEFECT: scored set implausibly small")
    first_usable = pd.Timestamp(lab[SCORED[0]])
    print(f"first usable date (expanding-decile calibration ready, R06): "
          f"{first_usable.date()}  [positional burn-in row {i0}, {len(SCORED)} scored sessions]")

    rS = r_next[SCORED]
    pS = close[SCORED]
    target_lab = lab[SCORED + 1]   # era assignment by target session (R11)

    # -------- primary MC-51 paths
    prim = path_stats(e_real[SCORED], rS, pS)
    eS = e_real[SCORED]
    n_lo = int(np.sum(eS == E_LO)); n_hi = int(np.sum(eS == E_HI)); n_mid = int(np.sum(eS == E_MID))

    # era split (R11), global matched ebar control
    era1 = target_lab <= np.datetime64(ERA1_END)
    dlog = np.log1p(prim["ret_s"]) - np.log1p(prim["ret_c"])
    imp_e1 = float(np.sum(dlog[era1])); imp_e2 = float(np.sum(dlog[~era1]))

    # -------- V3 null (R10): one code path via closures
    frame = pd.DataFrame({"session": tab["session"], "rv": tab["rv"]})
    loader = lambda: frame

    def decision_fn(f: pd.DataFrame) -> np.ndarray:
        return exposures_from_rv(f["rv"])

    def statistic_fn(decisions: np.ndarray, base: pd.DataFrame) -> float:
        e = decisions[SCORED]
        de = np.diff(e, prepend=0.0)
        cost = COST_RT * np.abs(de) / (PT_USD * pS)
        ret_s = e * rS - cost
        ebar = float(np.mean(np.abs(e)))
        cost_c = np.zeros_like(rS); cost_c[0] = COST_RT * ebar / (PT_USD * pS[0])
        ret_c = ebar * rS - cost_c
        return float(np.sum(np.log1p(ret_s)) - np.sum(np.log1p(ret_c)))

    sens = verify_null_sensitivity(loader, decision_fn, statistic_fn, shifts=[1, 7, 61],
                                   unit="session")
    print(f"null sensitivity VERIFIED first: real={sens['real_stat']:.6f} "
          f"spread={sens['spread']:.6f} over probe shifts [1,7,61] — the null can move")
    null = run_circular_null(loader, decision_fn, statistic_fn, n_shifts=300,
                             unit="session", seed=0)
    nstats = np.asarray(null["null_stats"], dtype=float)
    p95 = float(np.percentile(nstats, 95))
    med = float(np.median(nstats))
    v3_real = float(null["real_stat"])
    assert abs(v3_real - prim["timing"]) < 1e-12, "code-path divergence real stat"

    # -------- expected-fail drawdown throttle (R13, reported not gated)
    e_thr = np.empty(len(SCORED))
    state, w, hwm, eprev = 1.0, 1.0, 1.0, 0.0
    lw_thr = np.empty(len(SCORED))
    for k in range(len(SCORED)):
        e_thr[k] = state
        cost = COST_RT * abs(state - eprev) / (PT_USD * pS[k])
        w *= 1.0 + state * rS[k] - cost
        lw_thr[k] = math.log(w)
        eprev = state
        if w >= hwm:
            hwm = w; state = 1.0
        elif (hwm - w) / hwm > DD_TRIG:
            state = DD_CUT
    thr = path_stats(e_thr, rS, pS)

    # -------- MC-38 HAR race (G00026)
    rv = tab["rv"].to_numpy(); rsn = tab["rsneg"].to_numpy(); onv = tab["onrv"].to_numpy()
    nb = tab["n_bars"].to_numpy(); c0930 = tab["c0930"].to_numpy()
    rv_w = tab["rv"].rolling(5, min_periods=5).mean().to_numpy()
    rv_m = tab["rv"].rolling(22, min_periods=22).mean().to_numpy()
    rv21a = rv21.to_numpy()
    on_ret2 = np.full(n, np.nan)
    ok_on = np.zeros(n, dtype=bool)
    ok_on[1:] = (sub[1:] == sub[:-1]) & ~dropset[1:] & ~dropset[:-1] & np.isfinite(c0930[1:])
    on_ret2[ok_on] = np.square(np.log(c0930[ok_on] / close[np.flatnonzero(ok_on) - 1]))

    # pair (features at i -> target rv[i+1]) validity, one COMMON sample (R14)
    pair_ok = np.zeros(n, dtype=bool)
    pair_ok[:-1] = ((sub[1:] == sub[:-1]) & ~dropset[1:] & ~dropset[:-1]
                    & (rv[1:] > 0) & (nb[1:] >= MIN_BARS) & (nb[:-1] >= MIN_BARS))
    feats_ok = (np.isfinite(rv_w) & np.isfinite(rv_m) & np.isfinite(rv21a)
                & np.isfinite(on_ret2) & (rv > 0))
    pair_ok[:-1] &= feats_ok[:-1]
    n_bars_excl = int(np.sum((nb < MIN_BARS)))
    tlab_all = np.full(n, np.datetime64("NaT"), dtype="datetime64[ns]")
    tlab_all[:-1] = lab[1:]
    tr_m = pair_ok & (tlab_all >= np.datetime64(TRAIN_FIRST)) & (tlab_all <= np.datetime64(TRAIN_LAST))
    te_m = pair_ok & (tlab_all >= np.datetime64(TEST_FIRST)) & (tlab_all <= np.datetime64(TEST_LAST))
    TR = np.flatnonzero(tr_m); TE = np.flatnonzero(te_m)
    y_tr = rv[TR + 1]; y_te = rv[TE + 1]

    def design(ix, model):
        if model == "M1":
            return np.column_stack([np.ones(len(ix)), rv[ix], rv_w[ix], rv_m[ix]])
        return np.column_stack([np.ones(len(ix)), rsn[ix], (rv - rsn)[ix],
                                rv_w[ix], rv_m[ix], onv[ix], on_ret2[ix]])

    b1 = ols_fit(design(TR, "M1"), y_tr)
    b2 = ols_fit(design(TR, "M2"), y_tr)
    f0 = rv21a[TE]
    f1 = design(TE, "M1") @ b1
    f2 = design(TE, "M2") @ b2
    n_floor = int(np.sum(f1 < FLOOR_F) + np.sum(f2 < FLOOR_F) + np.sum(f0 < FLOOR_F))
    f0 = np.maximum(f0, FLOOR_F); f1 = np.maximum(f1, FLOOR_F); f2 = np.maximum(f2, FLOOR_F)
    L0 = qlike(y_te, f0); L1 = qlike(y_te, f1); L2 = qlike(y_te, f2)
    m0, m1, m2 = float(L0.mean()), float(L1.mean()), float(L2.mean())
    dm21 = dm_test(L2, L1)   # FROZEN PRIMARY: HAR+RS-+ON vs HAR-RV
    dm10 = dm_test(L1, L0)
    dm20 = dm_test(L2, L0)
    means = {"M0_plain21dRV": m0, "M1_HAR_RV": m1, "M2_HAR_RSneg_ON": m2}
    winner = min(means, key=means.get)
    mc38_pass = (dm21["mean_diff"] < 0) and (dm21["p"] < 0.05)

    # -------- secondary sizing column (R16, reported only)
    win_f = {"M0_plain21dRV": f0, "M1_HAR_RV": f1, "M2_HAR_RSneg_ON": f2}[winner]
    g = pd.Series(np.full(n, np.nan)); g.iloc[TE] = win_f
    gs = g.iloc[TE].reset_index(drop=True)
    prior = gs.shift(1)
    q10s = prior.expanding(min_periods=BURN_IN).quantile(Q_LO).to_numpy()
    q90s = prior.expanding(min_periods=BURN_IN).quantile(Q_HI).to_numpy()
    vs = gs.to_numpy()
    e_sec_local = np.full(len(vs), E_MID)
    with np.errstate(invalid="ignore"):
        e_sec_local[np.less_equal(vs, q10s, where=np.isfinite(q10s), out=np.zeros(len(vs), bool))] = E_LO
        e_sec_local[np.greater_equal(vs, q90s, where=np.isfinite(q90s), out=np.zeros(len(vs), bool))] = E_HI
    sec_usable_local = np.isfinite(q10s) & np.isfinite(q90s)
    sec_pos = TE[sec_usable_local]
    sec_mask_scored = np.isin(SCORED, sec_pos)
    SEC = SCORED[sec_mask_scored]
    e_sec_by_pos = dict(zip(TE[sec_usable_local], e_sec_local[sec_usable_local]))
    e_sec = np.array([e_sec_by_pos[i] for i in SEC])
    r_sec = r_next[SEC]; p_sec = close[SEC]
    sec = path_stats(e_sec, r_sec, p_sec) if len(SEC) > 50 else None
    prim_on_sec = path_stats(e_real[SEC], r_sec, p_sec) if len(SEC) > 50 else None
    sec_first = pd.Timestamp(lab[SEC[0]]).date() if len(SEC) > 50 else None

    # -------- V gates
    v1 = prim["timing"] > 0
    v2 = prim["maxdd_s"] <= 1.05 * prim["maxdd_c"]
    v3 = v3_real > p95
    v4 = (imp_e1 > 0) and (imp_e2 > 0)
    mc51_pass = v1 and v2 and v3 and v4
    ef_materialized = thr["timing"] < 0

    # -------- gate table (printed by program)
    L = []
    A = L.append
    A("G2_F3_VOLSIZE01_20260829 — GATE TABLE (printed by program; trials G00025 MC-51, G00026 MC-38)")
    A("type RISK_SPECIFICATION — sizing study; NEVER an information-alpha claim. No Sharpe printed (spec honesty clause).")
    A(f"window: sessions {APP_START.date()} .. {APP_END.date()} (pre-burn; deep substrate <=2021-12-31, modern 2022+; splice ISO-week 2022-W01 dropped: {n_dropweek} sessions)")
    A(f"evidence status: DISCOVERY_CONSUMED. seal_guard: {_SEAL['n_asserts']} asserts, {_SEAL['n_dropped']} post-seal rows mechanically dropped. data_esnq NOT read (ALLOWLIST_DEV_44 not exercised). provenance sha256 both substrates MATCH.")
    A(f"first usable date (expanding-decile calibration, R06 — PRINTED PER SPEC CLAUSE): {first_usable.date()}")
    A("")
    A("event counts / matched-exposure enforcement / null band — PRINTED BEFORE VERDICTS (R17):")
    A(f"  scored sessions {len(SCORED)} | decile occupancy: bottom(1.5x) {n_lo}, mid(1.0x) {n_mid}, top(0.5x) {n_hi} | rebalances {prim['n_rebal']}")
    A(f"  MATCHED MEAN EXPOSURE (V1 clause, IN-TABLE): strategy mean|e| = {np.mean(np.abs(eS)):.6f}  vs  control constant e = {prim['ebar']:.6f}  -> MATCHED (control scaled to strategy's realized mean |exposure|)")
    A(f"  V3 null band (300 circular shifts of the sizing series, seed 0): median {med:+.6f}, p95 {p95:+.6f} log-wealth — p95 is the minimum detectable timing component (MDE proxy)")
    A(f"  MC-38 test pairs n={dm21['n']} | mean QLIKE M0 {m0:.4f} M1 {m1:.4f} M2 {m2:.4f} | DM MDE (|mean QLIKE diff| for p=0.05 at observed HAC se) = {dm21['mde_mean_diff']:.5f}")
    A("")
    obs_v1 = (f"logW strat {prim['logw_s']:+.6f} vs control {prim['logw_c']:+.6f} "
              f"(diff {prim['timing']:+.6f}) at matched e={prim['ebar']:.4f}")
    obs_v2 = (f"maxDD strat {prim['maxdd_s']:.4%} vs control {prim['maxdd_c']:.4%} "
              f"(bar {1.05 * prim['maxdd_c']:.4%})")
    obs_v3 = (f"real {v3_real:+.6f} vs null p95 {p95:+.6f} "
              f"(pct {float(null['percentile']) * 100:.1f}%, p_ge {float(null['p_ge']):.4f}, 300 shifts)")
    obs_v4 = (f"era1 {imp_e1:+.6f} ({int(era1.sum())} sess), "
              f"era2 {imp_e2:+.6f} ({int((~era1).sum())} sess)")
    obs_m38 = (f"mean QLIKE diff {dm21['mean_diff']:+.5f} (M2-M1), "
               f"DM {dm21['stat']:+.3f}, p {dm21['p']:.4g}")
    A(f"{'GATE':<6}{'SPEC':<74}{'OBSERVED':<86}{'PASS-FAIL'}")
    A(f"{'V1':<6}{'net geometric growth > constant-exposure control AT MATCHED MEAN EXPOSURE':<74}"
      f"{obs_v1:<86}{'PASS' if v1 else 'FAIL'}")
    A(f"{'V2':<6}{'maxDD not worse than control by more than 5% (rel., R09)':<74}"
      f"{obs_v2:<86}{'PASS' if v2 else 'FAIL'}")
    A(f"{'V3':<6}{'timing component above p95 of >=300 circular-shift nulls':<74}"
      f"{obs_v3:<86}{'PASS' if v3 else 'FAIL'}")
    A(f"{'V4':<6}{'era split 2006-2015 / 2016-2026-05: growth improvement > 0 in BOTH (R11)':<74}"
      f"{obs_v4:<86}{'PASS' if v4 else 'FAIL'}")
    A(f"{'MC38':<6}{'HAR+RS-+ON beats HAR-RV on test QLIKE, DM p<0.05 (frozen primary)':<74}"
      f"{obs_m38:<86}{'PASS' if mc38_pass else 'FAIL'}")
    A("")
    A(f"EXPECTED-FAIL leg (R13, reported NOT gated): drawdown-throttle (cut 50% after 10% DD, restore at HW):")
    A(f"  mean|e| {thr['ebar']:.4f}; logW {thr['logw_s']:+.6f} vs its matched control {thr['logw_c']:+.6f} (diff {thr['timing']:+.6f}); "
      f"maxDD {thr['maxdd_s']:.4%} vs control {thr['maxdd_c']:.4%}; rebalances {thr['n_rebal']} "
      f"-> preregistered EXPECTED-FAIL {'MATERIALIZED (growth worse than matched control)' if ef_materialized else 'DID NOT MATERIALIZE (growth better — still not gated, recorded honestly)'}")
    A("")
    A(f"SECONDARY sizing column (R16, reported only; DM winner = {winner}):")
    if sec is not None:
        A(f"  subset {sec_first} .. {APP_END.date()} ({len(SEC)} sessions, own 252-obs burn-in): "
          f"winner-input timing {sec['timing']:+.6f} (maxDD {sec['maxdd_s']:.4%} vs ctrl {sec['maxdd_c']:.4%}, mean|e| {sec['ebar']:.4f}) | "
          f"primary-input on SAME subset: timing {prim_on_sec['timing']:+.6f} (maxDD {prim_on_sec['maxdd_s']:.4%}, mean|e| {prim_on_sec['ebar']:.4f})")
    else:
        A("  secondary subset too small to report (<50 sessions)")
    A("")
    A(f"VERDICT MC-51 (G00025): {'PASS — SURVIVED-DISCOVERY (RISK SPECIFICATION; routes to robustness, NOT promotion, NOT P1 application)' if mc51_pass else 'FAIL — closed at this formulation (a FAIL is a FAIL)'}"
      f"  [V1 {'P' if v1 else 'F'} V2 {'P' if v2 else 'F'} V3 {'P' if v3 else 'F'} V4 {'P' if v4 else 'F'}]")
    A(f"VERDICT MC-38 (G00026): {'PASS — QLIKE improvement significant; winner feeds SECONDARY column only' if mc38_pass else 'FAIL — sharper vol input not significantly better at this formulation'}"
      f"  [winner by mean test QLIKE: {winner}]")
    table = "\n".join(L)
    print(table)
    with open(os.path.join(OUT, "gate_table.txt"), "wb") as fh:
        fh.write(table.encode("utf-8"))

    # -------- dm_table.txt
    D = []
    D.append("G2_F3_VOLSIZE01_20260829 — MC-38 HAR race (trial G00026), printed by program")
    D.append(f"target: next-session full-session RV from 1-min log returns (R05); frozen split train {TRAIN_FIRST.date()}..{TRAIN_LAST.date()} / test {TEST_FIRST.date()}..{TEST_LAST.date()}")
    D.append(f"pairs: train n={len(TR)}, test n={len(TE)} (common sample all models; sessions with <{MIN_BARS} bars excluded: {n_bars_excl}; forecasts floored: {n_floor}); VXN add-on DROPPED per spec")
    D.append(f"M1 HAR-RV coefs [1,RV_d,RV_w,RV_m]: {np.array2string(b1, precision=6)}")
    D.append(f"M2 HAR+RS-+ON coefs [1,RS-,RS+,RV_w,RV_m,ONRV,ONret2]: {np.array2string(b2, precision=6)}")
    D.append(f"mean test QLIKE: M0 plain21dRV {m0:.6f} | M1 HAR-RV {m1:.6f} | M2 HAR+RS-+ON {m2:.6f}   winner: {winner}")
    D.append(f"DM (NW lag {NW_LAG}, two-sided): M2-M1 diff {dm21['mean_diff']:+.6f} stat {dm21['stat']:+.4f} p {dm21['p']:.6g}  <- FROZEN PRIMARY GATE")
    D.append(f"                                 M1-M0 diff {dm10['mean_diff']:+.6f} stat {dm10['stat']:+.4f} p {dm10['p']:.6g}")
    D.append(f"                                 M2-M0 diff {dm20['mean_diff']:+.6f} stat {dm20['stat']:+.4f} p {dm20['p']:.6g}")
    D.append(f"PASS(MC-38) = M2 beats M1, DM p<0.05 -> {'PASS' if mc38_pass else 'FAIL'}")
    dmt = "\n".join(D)
    print("\n" + dmt)
    with open(os.path.join(OUT, "dm_table.txt"), "wb") as fh:
        fh.write(dmt.encode("utf-8"))

    # -------- wealth_paths.csv (scored set)
    wp = pd.DataFrame({
        "session": pd.to_datetime(lab[SCORED]).strftime("%Y-%m-%d"),
        "close": pS, "r_next": rS,
        "e_primary": eS, "ret_strat": prim["ret_s"], "logW_strat": prim["lw_s"],
        "ret_ctrl_matched": prim["ret_c"], "logW_ctrl_matched": prim["lw_c"],
        "e_throttle": e_thr, "logW_throttle": lw_thr,
    })
    wp["e_secondary"] = np.nan
    wp["logW_secondary"] = np.nan
    if sec is not None:
        wp.loc[sec_mask_scored, "e_secondary"] = e_sec
        wp.loc[sec_mask_scored, "logW_secondary"] = sec["lw_s"]
    wp.to_csv(os.path.join(OUT, "wealth_paths.csv"), index=False)

    # -------- ledger pending (LIST of 2)
    ledger = [
        {
            "trial_id": "G00025",
            "metrics": {
                "card": "MC-51 extremes-only vol-managed sizing",
                "window": f"{first_usable.date()}..{APP_END.date()} scored sessions (app window 2006-01-01..2026-05-31)",
                "n_scored": int(len(SCORED)), "n_bottom_decile_15x": n_lo,
                "n_top_decile_05x": n_hi, "n_mid_10x": n_mid,
                "n_rebalances": prim["n_rebal"],
                "mean_abs_exposure": round(prim["ebar"], 6),
                "logw_strategy": round(prim["logw_s"], 6),
                "logw_control_matched": round(prim["logw_c"], 6),
                "timing_component_logw": round(prim["timing"], 6),
                "maxdd_strategy": round(prim["maxdd_s"], 6),
                "maxdd_control": round(prim["maxdd_c"], 6),
                "null_p95": round(p95, 6), "null_median": round(med, 6),
                "null_percentile": round(float(null["percentile"]), 4),
                "null_p_ge": round(float(null["p_ge"]), 4), "n_shifts": 300,
                "era1_improvement_logw": round(imp_e1, 6),
                "era2_improvement_logw": round(imp_e2, 6),
                "gates": {"V1": bool(v1), "V2": bool(v2), "V3": bool(v3), "V4": bool(v4)},
                "expected_fail_throttle": {
                    "timing_logw": round(thr["timing"], 6),
                    "maxdd": round(thr["maxdd_s"], 6),
                    "maxdd_control": round(thr["maxdd_c"], 6),
                    "materialized": bool(ef_materialized), "gated": False},
                "secondary_column": None if sec is None else {
                    "winner_input": winner, "n": int(len(SEC)),
                    "timing_logw": round(sec["timing"], 6),
                    "primary_on_same_subset_timing_logw": round(prim_on_sec["timing"], 6)},
                "classification": "RISK SPECIFICATION",
                "evidence_status": "DISCOVERY_CONSUMED",
            },
            "result": "PASS" if mc51_pass else "FAIL",
            "note": ("Extremes-only (bottom/top expanding-decile of plain 21d RV -> 1.5x/0.5x) vs "
                     "constant control at matched mean exposure (enforced in gate table), $33/RT per "
                     "rebalance contract, one-contract-notional base, first usable "
                     f"{first_usable.date()}. Gates V1-V4; drawdown-throttle EXPECTED-FAIL leg reported "
                     "not gated. Resolutions R01-R20 in out/spec_resolutions.txt. No Sharpe quoted. "
                     "No P1 application (spec prohibition)."),
        },
        {
            "trial_id": "G00026",
            "metrics": {
                "card": "MC-38 HAR race (nested vol-input arm)",
                "split": "train 2006-2017 / test 2018-2026-05-31 (frozen)",
                "n_train": int(len(TR)), "n_test": int(len(TE)),
                "mean_qlike_M0_plain21dRV": round(m0, 6),
                "mean_qlike_M1_HAR_RV": round(m1, 6),
                "mean_qlike_M2_HAR_RSneg_ON": round(m2, 6),
                "dm_M2_vs_M1": {"diff": round(dm21["mean_diff"], 6), "stat": round(dm21["stat"], 4), "p": float(f"{dm21['p']:.6g}")},
                "dm_M1_vs_M0": {"diff": round(dm10["mean_diff"], 6), "stat": round(dm10["stat"], 4), "p": float(f"{dm10['p']:.6g}")},
                "dm_M2_vs_M0": {"diff": round(dm20["mean_diff"], 6), "stat": round(dm20["stat"], 4), "p": float(f"{dm20['p']:.6g}")},
                "winner": winner, "vxn_addon": "DROPPED per spec",
                "evidence_status": "DISCOVERY_CONSUMED",
            },
            "result": "PASS" if mc38_pass else "FAIL",
            "note": ("QLIKE/DM race {plain 21d RV, HAR-RV, HAR+RS-+ON} for next-session NQ RV; frozen "
                     "primary comparison M2 vs M1 (skeptic text); winner feeds ONLY the secondary "
                     "sizing column so MC-51/MC-38 verdicts stay separable."),
        },
    ]
    with open(os.path.join(OUT, "ledger_result_pending.json"), "wb") as fh:
        fh.write(json.dumps(ledger, indent=2).encode("utf-8"))
    print("\noutputs written: gate_table.txt, dm_table.txt, wealth_paths.csv, ledger_result_pending.json")


if __name__ == "__main__":
    main()
