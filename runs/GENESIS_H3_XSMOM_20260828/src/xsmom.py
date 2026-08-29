"""GENESIS_H3_XSMOM - futures cross-sectional momentum, discovery 2009-2018 ONLY.

Executes runs/GENESIS_H3_XSMOM_20260828/spec.yaml EXACTLY. Every ambiguity resolution
was recorded in out/spec_resolutions.txt BEFORE this program produced any number
(R1-R18 referenced throughout). Trial G00012.

FROZEN SIGNAL (spec):
    formation  trailing 252-session economic return skipping the most recent 21
               sessions (12-1), on the root's own session sequence (R5)
    rank       across ALL roots jointly; long top 6 / short bottom 6; >= 18 valid
               else the rebalance is skipped and counted (R6, R8)
    weights    per-leg inverse-vol (63-session trailing sd of ret_usd, R7), shares
               capped at 3x equal-weight (0.5) cap-down-only, leg scaled to a 10%
               annualized vol target on C = $1,000,000 notional, linear risk summation
               (R9 - pure scale w.r.t. every gate)
    rebalance  Friday close (last session of a COMPLETED ISO week, R4/R18); fills at
               the next session's open via the substrate's overnight/intraday split
               (R10)

COSTS (R11): $4.36/ctrRT commission + spread ticks PER SIDE (1 primary / 3 stress);
turnover |dn| = one-way fills; roll close+reopen charged on carried positions.
Tick table reused verbatim from runs/VOLUME_LIQUIDITY_V1_20260828/src/vl_primary.py.

SEAL / WINDOW ISOLATION: the parquet is read with date filters INSIDE the read call
(2009-01-01 .. 2018-12-31); 2019+ (a fortiori the >= 2026-08-01 virgin seal) is never
loaded. The loaded frame passes research_sdk.seal_guard.assert_presealed.

GATES X1-X4 are printed by THIS program as GATE/SPEC/OBSERVED/PASS-FAIL. A FAIL is a
FAIL. No parameter search of any kind exists in this file.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(RUN))
sys.path.insert(0, ROOT)

from research_sdk import seal_guard                                     # noqa: E402
from research_sdk import null_guard                                     # noqa: E402

OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)

# ---- FROZEN BY SPEC (no grid, no search) -----------------------------------------
DATE_MIN = "2009-01-01"
DATE_MAX = "2018-12-31"            # held-back 2019+ NEVER loaded (filter at read, R2)
FORM_WIN, FORM_SKIP = 252, 21      # 12-1 convention (R5)
VOL_WIN = 63                       # trailing daily vol (R7)
N_LEG = 6                          # long top 6 / short bottom 6
MIN_VALID = 18                     # else skip-and-count
CAP_MULT = 3.0                     # weights capped at 3x equal-weight
VOL_TARGET_ANN = 0.10              # 10% annualized per leg
CAPITAL = 1_000_000.0              # notional scale (R9: gate-invariant)
COMMISSION_RT = 4.36
TICKS_PRIMARY, TICKS_STRESS = 1.0, 3.0   # per SIDE (spec cost_model; R11)
STALE_DAYS = 7                     # R6(a)
HALF_SPLIT = pd.Timestamp("2013-12-31")  # X4
NULL_SEED = 20260828
NULL_MIN_SHIFTS = 300
SENS_SHIFTS = [1, 7, 101]

# TICK table reused VERBATIM from runs/VOLUME_LIQUIDITY_V1_20260828/src/vl_primary.py
# (lines 56-59) - covers exactly the 21 CORE roots. Point values come from the
# parquet's own point_value column.
TICK = {"ES": 0.25, "NQ": 0.25, "YM": 1.0, "ZT": 1.0 / 128, "ZF": 1.0 / 128, "ZN": 1.0 / 64,
        "ZB": 1.0 / 32, "6E": 0.00005, "6J": 0.0000005, "6B": 0.0001, "6A": 0.0001,
        "6C": 0.00005, "6S": 0.0001, "CL": 0.01, "NG": 0.001, "GC": 0.1, "SI": 0.005,
        "ZC": 0.25, "ZW": 0.25, "ZM": 0.1, "ZL": 0.01}

V_LEG = VOL_TARGET_ANN * CAPITAL / np.sqrt(252.0)      # daily USD vol target per leg

_fh = None


def P(*a):
    print(*a, flush=True)
    if _fh is not None:
        print(*a, file=_fh)


# ============================================================================ LOAD
def load_panel() -> pd.DataFrame:
    """WINDOW ISOLATION AT LOAD (R2): the date_max filter is applied INSIDE the read
    call. No row >= 2019-01-01 ever enters memory."""
    path = os.path.join(ROOT, "research", "multi_market", "out", "economic_returns.parquet")
    df = pd.read_parquet(
        path,
        columns=["date", "root", "sector", "point_value", "ret_points", "overnight",
                 "intraday", "rolled", "eligible"],
        filters=[("date", ">=", pd.Timestamp(DATE_MIN)), ("date", "<=", pd.Timestamp(DATE_MAX))],
    )
    # SEAL: every data load passes seal_guard (trivially pre-seal here, asserted anyway)
    seal_guard.assert_presealed(df, "date", "GENESIS_H3_XSMOM load economic_returns")
    assert df["date"].max() <= pd.Timestamp(DATE_MAX), "WINDOW ISOLATION VIOLATION"
    assert df["date"].min() >= pd.Timestamp(DATE_MIN), "WINDOW ISOLATION VIOLATION"
    df = df.sort_values(["root", "date"]).reset_index(drop=True)
    df["ret_usd"] = df["ret_points"] * df["point_value"]
    df["ov_usd"] = df["overnight"] * df["point_value"]
    df["id_usd"] = df["intraday"] * df["point_value"]
    return df


# ============================================================================ GRID
def rebalance_dates(df: pd.DataFrame) -> pd.DatetimeIndex:
    """Last session of each COMPLETED ISO week on the union calendar (R4, R18)."""
    days = pd.DatetimeIndex(np.sort(df["date"].unique()))
    iso = days.isocalendar()
    key = iso["year"].astype(int) * 100 + iso["week"].astype(int)
    s = pd.Series(days, index=key.values)
    last = s.groupby(level=0).max().sort_values()
    # R18: keep only ISO weeks whose Sunday ends on/before DATE_MAX
    iso_end = last + pd.to_timedelta(6 - last.dt.weekday, unit="D")
    keep = last[iso_end <= pd.Timestamp(DATE_MAX)]
    return pd.DatetimeIndex(keep.values)


def per_root_arrays(df: pd.DataFrame) -> dict:
    """Per-root numpy state: dates, cum economic return, trailing 63d sigma, splits."""
    state = {}
    for r, g in df.groupby("root", sort=True):
        g = g.sort_values("date")
        ret = g["ret_usd"].to_numpy(float)
        state[r] = dict(
            dates=g["date"].to_numpy("datetime64[ns]"),
            ret=ret,
            cum=np.cumsum(ret),
            sig=pd.Series(ret).rolling(VOL_WIN, min_periods=VOL_WIN).std(ddof=1).to_numpy(),
            ov=g["ov_usd"].to_numpy(float),
            iday=g["id_usd"].to_numpy(float),
            rolled=g["rolled"].to_numpy(int),
            elig=g["eligible"].to_numpy(bool),
        )
    return state


def build_week_frame(state: dict, rebs: pd.DatetimeIndex):
    """One row per (rebalance week, root), rectangular (R14). Decision inputs F/sigma/
    qual; base-only columns H, roll_fill, roll_in, side-rate ingredients."""
    roots = sorted(state.keys())
    rows = []
    reb_ns = rebs.to_numpy("datetime64[ns]")
    n_weeks = len(rebs)
    for r in roots:
        st = state[r]
        d = st["dates"]
        # decision index j: last session <= rebalance date
        j = np.searchsorted(d, reb_ns, side="right") - 1
        # fill index f: first session > rebalance date
        f = np.searchsorted(d, reb_ns, side="right")
        nd = len(d)
        cum0 = np.concatenate(([0.0], st["cum"]))                       # cum0[i] = sum ret[:i]
        for k in range(n_weeks):
            jj, ff = int(j[k]), int(f[k])
            fe = int(f[k + 1]) if k + 1 < n_weeks else nd               # next week's fill (excl)
            # ---- decision inputs (R5-R7)
            F = sig = np.nan
            qual = False
            if jj >= 0:
                stale = (reb_ns[k] - d[jj]) > np.timedelta64(STALE_DAYS, "D")
                if not stale and st["elig"][jj] and jj >= FORM_WIN + FORM_SKIP:
                    F = st["cum"][jj - FORM_SKIP] - st["cum"][jj - FORM_SKIP - FORM_WIN]
                    sg = st["sig"][jj]
                    if np.isfinite(sg) and sg > 0:
                        sig = sg
                        qual = np.isfinite(F)
            # ---- base outcome columns (R10, R11) - NEVER touched by decision_fn
            if ff < nd:
                # H = intraday of fill + full ret of interior sessions + overnight of next fill
                H = st["iday"][ff] + (cum0[fe] - cum0[ff + 1])
                if fe < nd:
                    H += st["ov"][fe]
                roll_fill = int(st["rolled"][ff])
                roll_in = int(st["rolled"][ff + 1:fe].sum())
            else:
                H, roll_fill, roll_in = 0.0, 0, 0
            rows.append((k, pd.Timestamp(reb_ns[k]), r, F, sig, qual, H, roll_fill, roll_in))
    fr = pd.DataFrame(rows, columns=["slot", "reb_date", "root", "F", "sigma", "qual",
                                     "H", "roll_fill", "roll_in"])
    fr = fr.sort_values(["slot", "root"], kind="stable").reset_index(drop=True)
    return fr, roots


# ============================================================================ DECISION
def make_decision_fn(roots, tick_usd_vec):
    n_roots = len(roots)

    def decision_fn(frame: pd.DataFrame) -> np.ndarray:
        """FROZEN selection + weights + carry rule, black-box on (possibly shifted)
        inputs. Returns flat contracts array aligned to frame rows."""
        F = frame["F"].to_numpy(float).reshape(-1, n_roots)
        S = frame["sigma"].to_numpy(float).reshape(-1, n_roots)
        Q = frame["qual"].to_numpy(bool).reshape(-1, n_roots)
        W = F.shape[0]
        pos = np.zeros((W, n_roots))
        prev = np.zeros(n_roots)
        for k in range(W):
            ok = Q[k] & np.isfinite(F[k]) & np.isfinite(S[k]) & (S[k] > 0)
            if ok.sum() < MIN_VALID:
                pos[k] = prev                                   # skip-and-count: carry (R6)
                continue
            idx = np.flatnonzero(ok)
            order = idx[np.argsort(F[k][idx], kind="stable")]   # asc; ties by root (stable)
            short_idx, long_idx = order[:N_LEG], order[-N_LEG:]
            n = np.zeros(n_roots)
            for leg_idx, sgn in ((long_idx, +1.0), (short_idx, -1.0)):
                u = 1.0 / S[k][leg_idx]
                s = u / u.sum()
                s = np.minimum(s, CAP_MULT / N_LEG)             # cap-down-only (R9)
                lam = V_LEG / float((s * S[k][leg_idx]).sum())  # leg vol target, linear
                n[leg_idx] = sgn * lam * s
            pos[k] = n
            prev = n
        return pos.ravel()

    return decision_fn


def weekly_pnl(pos_flat: np.ndarray, base: pd.DataFrame, n_roots: int, ticks: float,
               side_rate_vec: np.ndarray):
    """Score positions against the ORIGINAL alignment (R10/R11). Returns per-week
    gross/cost/net arrays and per-(week,root) matrices."""
    N = pos_flat.reshape(-1, n_roots)
    H = base["H"].to_numpy(float).reshape(-1, n_roots)
    RF = base["roll_fill"].to_numpy(float).reshape(-1, n_roots)
    RI = base["roll_in"].to_numpy(float).reshape(-1, n_roots)
    prevN = np.vstack([np.zeros(n_roots), N[:-1]])
    gross = N * H
    turn = np.abs(N - prevN)                                    # one-way fills (R11)
    rolls = 2.0 * (RF * np.abs(prevN) + RI * np.abs(N))         # sides from rolls (R11)
    cost = (turn + rolls) * side_rate_vec[None, :]
    return gross, cost, turn


def make_statistic_fn(n_roots: int, side_rate_primary: np.ndarray):
    def statistic_fn(decisions: np.ndarray, base: pd.DataFrame) -> float:
        gross, cost, _ = weekly_pnl(decisions, base, n_roots, TICKS_PRIMARY, side_rate_primary)
        return float((gross.sum(axis=1) - cost.sum(axis=1)).mean())
    return statistic_fn


# ============================================================================ MAIN
def main():
    global _fh
    _fh = open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8")
    P("=" * 110)
    P("=== GENESIS_H3_XSMOM_20260828 - cross-sectional momentum, discovery 2009-2018 ONLY (trial G00012)")
    P("=== spec frozen; resolutions R1-R18 recorded in out/spec_resolutions.txt BEFORE any number below")
    P("=" * 110)

    df = load_panel()
    P(f"    loaded rows {len(df):,}   roots {df['root'].nunique()}   "
      f"dates {df['date'].min().date()} -> {df['date'].max().date()}   "
      f"(2019+ NEVER loaded: filter inside read_parquet; seal_guard PASS)")

    pv = df.groupby("root")["point_value"].first()
    sector_of = df.groupby("root")["sector"].first().to_dict()
    state = per_root_arrays(df)
    roots = sorted(state.keys())
    assert set(roots) == set(TICK), "tick table / universe mismatch"
    n_roots = len(roots)
    tick_usd = np.array([TICK[r] * float(pv[r]) for r in roots])
    side_primary = COMMISSION_RT / 2.0 + TICKS_PRIMARY * tick_usd
    side_stress = COMMISSION_RT / 2.0 + TICKS_STRESS * tick_usd

    rebs_all = rebalance_dates(df)
    frame_all, _ = build_week_frame(state, rebs_all)
    qual_count = frame_all.groupby("slot")["qual"].sum()
    tradable = qual_count >= MIN_VALID
    if not tradable.any():
        raise RuntimeError("no tradable rebalance in discovery")
    k0 = int(tradable[tradable].index.min())
    n_warmup_skip = int((~tradable[tradable.index < k0]).sum())
    n_mid_skip = int((~tradable[tradable.index >= k0]).sum())
    P(f"    ISO-week rebalances in window: {len(rebs_all)}   "
      f"first tradable: {rebs_all[k0].date()} (warmup skips before it: {n_warmup_skip})   "
      f"mid-sample skipped-and-counted: {n_mid_skip}")

    # frame from the first tradable rebalance onward (R14); re-slot 0..W-1
    frame = frame_all[frame_all["slot"] >= k0].copy()
    frame["slot"] = frame["slot"] - k0
    frame = frame.sort_values(["slot", "root"], kind="stable").reset_index(drop=True)
    rebs = rebs_all[k0:]
    W = len(rebs)
    P(f"    weekly grid: {W} rebalance weeks   universe {n_roots} roots, "
      f"{len(set(sector_of.values()))} sectors")

    decision_fn = make_decision_fn(roots, tick_usd)
    statistic_fn = make_statistic_fn(n_roots, side_primary)

    # ---- REAL run --------------------------------------------------------------
    pos_flat = decision_fn(frame)
    grossM, costM, turnM = weekly_pnl(pos_flat, frame, n_roots, TICKS_PRIMARY, side_primary)
    _, costM_s, _ = weekly_pnl(pos_flat, frame, n_roots, TICKS_STRESS, side_stress)
    wk_gross = grossM.sum(axis=1)
    wk_cost = costM.sum(axis=1)
    wk_net = wk_gross - wk_cost
    wk_net_s = wk_gross - costM_s.sum(axis=1)
    net_p, net_s = float(wk_net.sum()), float(wk_net_s.sum())
    sd_w = float(wk_net.std(ddof=1))
    t_weekly = float(wk_net.mean() / (sd_w / np.sqrt(W)))
    mde = 2.0 * sd_w / np.sqrt(W)
    # roll-cost diagnostic (gates use the roll-inclusive model, R11)
    diag_cost_noroll = (turnM * side_primary[None, :]).sum()
    P("")
    P(f"    PRIMARY (1 tick/side): gross ${wk_gross.sum():>12,.0f}   cost ${wk_cost.sum():>11,.0f}"
      f"   net ${net_p:>12,.0f}   weekly t {t_weekly:+.3f}")
    P(f"    STRESS  (3 ticks/side): net ${net_s:>12,.0f}")
    P(f"    DIAGNOSTIC only - net without roll close/reopen costs: "
      f"${float(wk_gross.sum() - diag_cost_noroll):>12,.0f}")
    P(f"    POWER (spec power_note): N_w={W} weeks, weekly sd ${sd_w:,.0f} -> "
      f"MDE for t=2.0 is ${mde:,.0f}/week (${mde * 52:,.0f}/yr) on C=$1,000,000")

    # ---- attribution -----------------------------------------------------------
    root_gross = pd.Series(grossM.sum(axis=0), index=roots)
    root_cost = pd.Series(costM.sum(axis=0), index=roots)
    root_net = root_gross - root_cost
    pos_g = root_gross[root_gross > 0]
    top_root_share = float(pos_g.max() / pos_g.sum()) if len(pos_g) else 1.0
    top_root_name = pos_g.idxmax() if len(pos_g) else "-"
    sec_net = root_net.groupby(pd.Series(sector_of)).sum()
    loso = {s: net_p - float(sec_net[s]) for s in sec_net.index}
    n_loso_pos = int(sum(v > 0 for v in loso.values()))
    P("")
    P("    per-root net (primary) and gross:")
    for r in root_net.sort_values(ascending=False).index:
        P(f"        {r:<4} {sector_of[r]:<13} gross ${root_gross[r]:>11,.0f}   net ${root_net[r]:>11,.0f}")
    P("    leave-one-sector-out net (primary, contribution-exclusion per R13):")
    for s, v in sorted(loso.items()):
        P(f"        without {s:<13} ${v:>12,.0f}   {'>0' if v > 0 else '<=0'}")

    # ---- halves (X4) -----------------------------------------------------------
    reb_ts = pd.DatetimeIndex(rebs)
    h1 = reb_ts <= HALF_SPLIT
    net_h1, net_h2 = float(wk_net[h1].sum()), float(wk_net[~h1].sum())
    P("")
    P(f"    halves: 2009-2013 net ${net_h1:,.0f} ({int(h1.sum())} wks)   "
      f"2014-2018 net ${net_h2:,.0f} ({int((~h1).sum())} wks)")

    # ---- X3 null (null_guard: sensitivity FIRST, then full circular null) -------
    P("")
    P("    X3 null construction (research_sdk.null_guard, unit = week blocks):")
    loader = lambda: frame.copy()                                        # noqa: E731
    sens = null_guard.verify_null_sensitivity(loader, decision_fn, statistic_fn,
                                              shifts=SENS_SHIFTS, unit="slot")
    P(f"        sensitivity: real {sens['real_stat']:+.2f}  spread {sens['spread']:.2f}  "
      f"across shifts {SENS_SHIFTS} -> null HAS teeth")
    assert W - 1 >= NULL_MIN_SHIFTS, f"only {W-1} possible shifts < {NULL_MIN_SHIFTS}"
    res = null_guard.run_circular_null(loader, decision_fn, statistic_fn,
                                       n_shifts=W - 1, unit="slot", seed=NULL_SEED)
    null_stats = np.asarray(res["null_stats"])
    q95 = float(np.percentile(null_stats, 95))
    real_stat = res["real_stat"]
    assert abs(real_stat - wk_net.mean()) <= 1e-6 * max(1.0, abs(wk_net.mean())), \
        "engine/null parity violation"
    P(f"        {len(null_stats)} circular shifts (all distinct; >= {NULL_MIN_SHIFTS} required)   "
      f"real weekly mean ${real_stat:,.2f}   null q95 ${q95:,.2f}   "
      f"null mean ${null_stats.mean():,.2f}   percentile {100*res['percentile']:.1f}%   "
      f"p_ge {res['p_ge']:.4f}")

    # ---- GATE TABLE (printed by program) ----------------------------------------
    x1a, x1b, x1c = net_p > 0, net_s > 0, t_weekly >= 2.0
    x1 = x1a and x1b and x1c
    x2a, x2b = top_root_share <= 0.40, n_loso_pos >= 5
    x2 = x2a and x2b
    x3 = real_stat > q95
    x4 = (net_h1 > 0) and (net_h2 > 0)
    rows = [
        ("X1a net@PRIMARY > 0",        "> $0",            f"${net_p:,.0f}",                x1a),
        ("X1b net@3-TICK STRESS > 0",  "> $0",            f"${net_s:,.0f}",                x1b),
        ("X1c weekly clustered t",     ">= 2.0",          f"{t_weekly:+.3f}",              x1c),
        ("X2a top-root +gross share",  "<= 40%",          f"{100*top_root_share:.1f}% ({top_root_name})", x2a),
        ("X2b LOSO net > 0 sectors",   ">= 5 of 6",       f"{n_loso_pos} of {len(loso)}",  x2b),
        ("X3  real vs null q95",       f"> ${q95:,.2f}",  f"${real_stat:,.2f}",            x3),
        ("X4a net 2009-2013 > 0",      "> $0",            f"${net_h1:,.0f}",               net_h1 > 0),
        ("X4b net 2014-2018 > 0",      "> $0",            f"${net_h2:,.0f}",               net_h2 > 0),
    ]
    P("")
    P("=" * 110)
    P("=== PREREGISTERED GATES (spec.yaml, frozen before results existed)")
    P("=" * 110)
    P(f"    {'GATE':<28} {'SPEC':>14} {'OBSERVED':>26}   PASS-FAIL")
    P("    " + "-" * 84)
    for nm, spec, obs, good in rows:
        P(f"    {nm:<28} {spec:>14} {obs:>26}   {'PASS' if good else '*** FAIL ***'}")
    allpass = x1 and x2 and x3 and x4
    P("")
    P(f"    X1 {'PASS' if x1 else 'FAIL'}   X2 {'PASS' if x2 else 'FAIL'}   "
      f"X3 {'PASS' if x3 else 'FAIL'}   X4 {'PASS' if x4 else 'FAIL'}")
    P("=" * 110)
    P(f"=== VERDICT: {'ALL X1-X4 PASS -> candidate proceeds (independent implementation next; held-back read stays FUTURE)' if allpass else 'GATE FAILURE -> NULL, family closed at this formulation'}")
    P("=" * 110)

    # ---- outputs ----------------------------------------------------------------
    wk = pd.DataFrame({"reb_date": reb_ts.date, "gross": wk_gross, "cost_primary": wk_cost,
                       "net_primary": wk_net, "net_stress": wk_net_s,
                       "n_qual": qual_count.loc[k0:].values,
                       "skipped": (~tradable.loc[k0:]).values.astype(int)})
    wk.to_csv(os.path.join(OUT, "weekly_series.csv"), index=False)
    cb = pd.DataFrame({"root": roots,
                       "sector": [sector_of[r] for r in roots],
                       "gross": root_gross.values, "cost_primary": root_cost.values,
                       "net_primary": root_net.values})
    cb["pos_gross_share"] = np.where(cb["gross"] > 0, cb["gross"] / pos_g.sum(), 0.0)
    cb.to_csv(os.path.join(OUT, "contribution_by_root.csv"), index=False)

    metrics = {
        "weeks": W, "warmup_skips": n_warmup_skip, "mid_sample_skips": n_mid_skip,
        "net_primary_usd": round(net_p, 2), "net_stress_usd": round(net_s, 2),
        "gross_usd": round(float(wk_gross.sum()), 2),
        "cost_primary_usd": round(float(wk_cost.sum()), 2),
        "weekly_t": round(t_weekly, 4), "weekly_mean_usd": round(float(wk_net.mean()), 2),
        "weekly_sd_usd": round(sd_w, 2), "mde_t2_usd_per_week": round(mde, 2),
        "top_root_pos_gross_share": round(top_root_share, 4), "top_root": str(top_root_name),
        "loso_positive_sectors": n_loso_pos,
        "null_shifts": int(len(null_stats)), "null_q95_usd": round(q95, 2),
        "null_percentile": round(res["percentile"], 4), "null_p_ge": round(res["p_ge"], 4),
        "net_2009_2013_usd": round(net_h1, 2), "net_2014_2018_usd": round(net_h2, 2),
        "gates": {"X1": bool(x1), "X2": bool(x2), "X3": bool(x3), "X4": bool(x4)},
        "capital_scale_usd": CAPITAL, "evidence_status": "DISCOVERY_CONSUMED",
    }
    result = "PASS" if allpass else "NULL"
    note = ("XSMOM 12-1 top6/bottom6 across 21 CORE roots, vol-scaled legs at 10% ann target; "
            "primary $4.36RT+1 tick/side incl. roll close/reopen; gates "
            f"X1 {'P' if x1 else 'F'} X2 {'P' if x2 else 'F'} X3 {'P' if x3 else 'F'} "
            f"X4 {'P' if x4 else 'F'}; resolutions R1-R18 recorded pre-computation; "
            "2019+ never loaded (filtered inside read).")
    with open(os.path.join(OUT, "ledger_result_pending.json"), "w", encoding="utf-8") as fh:
        json.dump({"trial_id": "G00012", "metrics": metrics, "result": result, "note": note},
                  fh, indent=2)
    P(f"\n    outputs written: gate_table.txt, weekly_series.csv, contribution_by_root.csv, "
      f"ledger_result_pending.json  (result: {result})")
    _fh.close()
    return result


if __name__ == "__main__":
    main()
