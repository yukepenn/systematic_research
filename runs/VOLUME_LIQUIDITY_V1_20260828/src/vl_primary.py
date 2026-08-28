"""VOLUME_LIQUIDITY_V1 -- PRIMARY implementation.  VECTORIZED dataframe path.

Executes runs/VOLUME_LIQUIDITY_V1_20260828/SPEC.md.  Every constant below is frozen in that SPEC,
committed at 4ef441d BEFORE any volume alpha P&L existed.

IMPLEMENTATION RESOLUTIONS -- committed with the engine, BEFORE any P&L.  Each is forced by
implementation reality and none is chosen by looking at an outcome:

  R1 STALENESS.  For ISO week W the decision cutoff is Monday(W), exclusive.  A root participates
     only if its most recent eligible volume observation d_i satisfies
     Monday(W) - 7 days <= d_i < Monday(W).  "Traded in the last week" -- not a tuned parameter.
  R2 ELIGIBLE-COMPACTED LOOKBACK.  MED63/MAD63 are the median / MAD of the prior 63 ELIGIBLE LV
     observations, i.e. the rolling window runs over the compacted eligible series, not over
     calendar rows.  This is the SPEC's literal wording ("prior 63 eligible LV observations").
  R3 SIGMA POPULATION.  sd of the prior 63 daily ret_usd rows of that root in the certified
     substrate, strictly lagged (shift(1) then rolling(63)).
  R4 MID-WEEK ELIGIBILITY LOSS.  A position is set at the cutoff and held across the week on every
     session where the root has a return row and remains price-eligible.  If eligibility lapses
     mid-week the root simply stops accruing; the exit cost is charged at the next weekly boundary
     by the |delta n| rule.  Coverage is 99.97-100 %, so this is rare by construction.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(RUN))
sys.path.insert(0, os.path.join(ROOT, "research", "multi_market", "src"))
import ncd_day as N                                                          # noqa: E402

VOL00 = os.path.join(ROOT, "runs", "VOLUME00_20260828", "out")
MMOUT = os.path.join(ROOT, "research", "multi_market", "out")

# ---- FROZEN IN THE SPEC ------------------------------------------------------------------
LOOKBACK = 63
MAD_SCALE = 1.4826
ZFLOOR = 1e-6                 # division-by-zero guard, NOT a parameter
CLIP = 3.0
SIGMA_WIN = 63
RISK_BUDGET = 1000.0          # $ of daily-P&L sd per root at |RISK_SCORE| = 1 (scale constant)
SECTOR_CAP = 0.40
COMMISSION_RT = 4.36
SLIP_TICKS_PRIMARY = 1.0
SLIP_TICKS_STRESS = 2.0
STALE_DAYS = 7
SEAL = pd.Timestamp("2026-08-01")
DEV_END = pd.Timestamp("2019-01-01")     # development is strictly before this
BOOT_L_FORMULA = "round(n_weeks ** (1/3))"
BOOT_B, BOOT_SEED = 20000, 20260828

TICK = {"ES": 0.25, "NQ": 0.25, "YM": 1.0, "ZT": 1.0 / 128, "ZF": 1.0 / 128, "ZN": 1.0 / 64,
        "ZB": 1.0 / 32, "6E": 0.00005, "6J": 0.0000005, "6B": 0.0001, "6A": 0.0001,
        "6C": 0.00005, "6S": 0.0001, "CL": 0.01, "NG": 0.001, "GC": 0.1, "SI": 0.005,
        "ZC": 0.25, "ZW": 0.25, "ZM": 0.1, "ZL": 0.01}


def cost_per_side(root, slip_ticks):
    return (COMMISSION_RT + slip_ticks * TICK[root] * N.PV[root]) / 2.0


# ============================================================================ INPUTS
def load_inputs():
    v = pd.read_parquet(os.path.join(VOL00, "volume_substrate.parquet"),
                        columns=["root", "sector", "date", "vol", "vol_usable", "eligible"])
    e = pd.read_parquet(os.path.join(MMOUT, "economic_returns.parquet"),
                        columns=["date", "root", "sector", "ret_usd", "eligible", "rolled"])
    v = v[v["date"] < SEAL].sort_values(["root", "date"]).reset_index(drop=True)
    e = e[e["date"] < SEAL].sort_values(["root", "date"]).reset_index(drop=True)
    return v, e


# ============================================================================ FEATURES
def build_features(v: pd.DataFrame) -> pd.DataFrame:
    """LV -> MED63/MAD63 over the prior 63 ELIGIBLE observations -> ZVOL.  Strictly lagged."""
    ok = v["vol_usable"].values & v["eligible"].values & v["vol"].notna().values
    w = v[ok].copy()
    w["LV"] = np.log1p(w["vol"].astype(float))
    out = []
    for r, g in w.groupby("root", sort=False):
        g = g.sort_values("date").copy()
        lv = g["LV"]
        prior = lv.shift(1)                                   # STRICTLY before the observation
        g["MED63"] = prior.rolling(LOOKBACK, min_periods=LOOKBACK).median()
        g["MAD63"] = prior.rolling(LOOKBACK, min_periods=LOOKBACK).apply(
            lambda a: np.median(np.abs(a - np.median(a))), raw=True)
        g["ZVOL"] = (g["LV"] - g["MED63"]) / np.maximum(MAD_SCALE * g["MAD63"], ZFLOOR)
        out.append(g)
    f = pd.concat(out, ignore_index=True)
    return f[["root", "sector", "date", "LV", "MED63", "MAD63", "ZVOL"]].dropna(subset=["ZVOL"])


def build_sigma(e: pd.DataFrame) -> pd.DataFrame:
    out = []
    for r, g in e.groupby("root", sort=False):
        g = g.sort_values("date").copy()
        g["SIGMA"] = g["ret_usd"].shift(1).rolling(SIGMA_WIN, min_periods=SIGMA_WIN).std(ddof=1)
        out.append(g[["root", "date", "SIGMA"]])
    return pd.concat(out, ignore_index=True)


# ============================================================================ POSITIONS
def iso_monday(d: pd.Series) -> pd.Series:
    return d - pd.to_timedelta(d.dt.weekday, unit="D")


def build_weekly_positions(feat, sig, e, sign=+1.0):
    """VECTORIZED: one merge_asof per (root, week) -- no day-by-day state machine anywhere."""
    e = e.copy()
    e["monday"] = iso_monday(e["date"])
    weeks = e.loc[e["eligible"], ["root", "sector", "monday"]].drop_duplicates()
    weeks = weeks.sort_values(["monday", "root"]).reset_index(drop=True)

    src = feat.merge(sig, on=["root", "date"], how="inner").dropna(subset=["SIGMA"])
    src = src[src["SIGMA"] > 0].sort_values(["date", "root"]).reset_index(drop=True)

    m = pd.merge_asof(weeks.sort_values("monday"), src.sort_values("date"),
                      left_on="monday", right_on="date", by="root",
                      direction="backward", allow_exact_matches=False)
    m = m.dropna(subset=["ZVOL", "SIGMA"])
    m = m[(m["monday"] - m["date"]).dt.days <= STALE_DAYS].copy()      # R1 staleness
    m = m.rename(columns={"date": "cutoff_date", "sector_x": "sector"})
    if "sector_y" in m.columns:
        m = m.drop(columns=["sector_y"])

    # ---- within-sector demean, then the frozen signal
    m["sec_mean_z"] = m.groupby(["monday", "sector"])["ZVOL"].transform("mean")
    m["RELZ"] = m["ZVOL"] - m["sec_mean_z"]
    m["S"] = np.clip(sign * (-m["RELZ"]), -CLIP, CLIP)
    m["RISK_SCORE"] = m["S"] / CLIP
    m["n_raw"] = m["RISK_SCORE"] * RISK_BUDGET / m["SIGMA"]

    # ---- sector gross-risk cap: ONE deterministic pass, CAP DOWN ONLY
    m["gross_i"] = m["RISK_SCORE"].abs() * RISK_BUDGET
    gs = m.groupby(["monday", "sector"])["gross_i"].transform("sum")
    gt = m.groupby("monday")["gross_i"].transform("sum")
    share = np.where(gt > 0, gs / gt, 0.0)
    scale = np.where(share > SECTOR_CAP, SECTOR_CAP * gt / np.maximum(gs, 1e-12), 1.0)
    m["sector_scale"] = scale
    m["n"] = m["n_raw"] * m["sector_scale"]
    return m[["monday", "root", "sector", "cutoff_date", "ZVOL", "RELZ", "S", "RISK_SCORE",
              "SIGMA", "sector_scale", "n"]].sort_values(["monday", "root"]).reset_index(drop=True)


# ============================================================================ SIMULATION
def simulate(pos, e, slip_ticks=SLIP_TICKS_PRIMARY, frozen_sides=None):
    """Daily P&L and costs.  If frozen_sides is given, the position path is REUSED EXACTLY and
    only the cost rate changes -- that is the PURE COST STRESS.

    The (root, week) GRID carries every week in which a root has an eligible session, with n = 0
    where the signal is absent.  Building the grid rather than only the weeks a position exists is
    what makes an EXIT cost get charged: a root that drops out is a change from n to 0, and |dn|
    prices it.  Charging only on weeks a position exists would silently under-charge turnover."""
    e = e.copy()
    e["monday"] = iso_monday(e["date"])
    ee = e[e["eligible"]].copy()
    grid = ee[["root", "monday"]].drop_duplicates()
    grid = grid.merge(pos[["monday", "root", "n"]], on=["root", "monday"], how="left")
    grid["n"] = grid["n"].fillna(0.0)
    grid = grid.sort_values(["root", "monday"]).reset_index(drop=True)

    d = ee.merge(grid, on=["root", "monday"], how="left")
    d["n"] = d["n"].fillna(0.0)
    d["pnl_gross"] = d["n"] * d["ret_usd"]

    if frozen_sides is None:
        g = grid.copy()
        g["n_prev"] = g.groupby("root")["n"].shift(1).fillna(0.0)
        g["sides_rebal"] = (g["n"] - g["n_prev"]).abs()
        first = d.groupby(["root", "monday"])["date"].min().reset_index()
        reb = g.merge(first, on=["root", "monday"], how="inner")[["root", "date", "sides_rebal"]]
        rollc = d.loc[d["rolled"] == 1, ["root", "date", "n"]].copy()
        rollc["sides_roll"] = 2.0 * rollc["n"].abs()
        sides = d[["root", "date"]].merge(reb, on=["root", "date"], how="left") \
                                   .merge(rollc[["root", "date", "sides_roll"]],
                                          on=["root", "date"], how="left")
        sides["sides"] = sides["sides_rebal"].fillna(0.0) + sides["sides_roll"].fillna(0.0)
        frozen_sides = sides[["root", "date", "sides"]]

    d = d.merge(frozen_sides, on=["root", "date"], how="left")
    d["sides"] = d["sides"].fillna(0.0)
    d["cost"] = d["sides"] * d["root"].map(lambda r: cost_per_side(r, slip_ticks))
    d["pnl_net"] = d["pnl_gross"] - d["cost"]
    return d.sort_values(["date", "root"]).reset_index(drop=True), frozen_sides


def weekly_net(daily):
    d = daily.copy()
    d["monday"] = iso_monday(d["date"])
    w = d.groupby("monday").agg(gross=("pnl_gross", "sum"), cost=("cost", "sum"),
                                net=("pnl_net", "sum")).sort_index()
    return w


def run(sign=+1.0, slip_ticks=SLIP_TICKS_PRIMARY, vol_mod=None, ret_mod=None,
        date_max=None, roots=None, permute_signal_seed=None, shift_weeks=None):
    v, e = load_inputs()
    if roots is not None:
        v, e = v[v["root"].isin(roots)], e[e["root"].isin(roots)]
    if vol_mod is not None:
        v = vol_mod(v)
    if ret_mod is not None:
        e = ret_mod(e)
    if shift_weeks:
        v = _shift_volume_whole_weeks(v, shift_weeks)
    feat = build_features(v)
    sig = build_sigma(e)
    pos = build_weekly_positions(feat, sig, e, sign=sign)
    if permute_signal_seed is not None:
        pos = _permute_within_sector(pos, permute_signal_seed)
    if date_max is not None:
        pos = pos[pos["monday"] < date_max]
        e = e[e["date"] < date_max]
    daily, sides = simulate(pos, e, slip_ticks=slip_ticks)
    return dict(pos=pos, daily=daily, sides=sides, weekly=weekly_net(daily), feat=feat, sig=sig)


# ---------------------------------------------------------------- NULL MACHINERY (SPEC 7C/7D)
def _shift_volume_whole_weeks(v, k):
    """NULL 1: ONE SHARED circular shift, in whole weeks, applied identically to every root.
    Preserves the cross-sectional dependence of participation and the sector-demean structure;
    destroys ONLY the alignment between volume and future return."""
    out = []
    for r, g in v.groupby("root", sort=False):
        g = g.sort_values("date").copy()
        n = len(g)
        s = int(round(k * 5)) % n if n else 0          # 5 trading sessions == one whole week
        g["vol"] = np.roll(g["vol"].values, s)
        g["vol_usable"] = np.roll(g["vol_usable"].values, s)
        out.append(g)
    return pd.concat(out, ignore_index=True)


def _permute_within_sector(pos, seed):
    """NULL 2: permute the frozen signal ACROSS ROOTS WITHIN SECTOR at each rebalance.
    Preserves the signal distribution, active-root count, risk scaling (each root keeps its own
    SIGMA), sector structure and turnover architecture.  Destroys the root-to-own-liquidity map."""
    rng = np.random.default_rng(seed)
    p = pos.copy()
    newS = p["S"].values.copy()
    for (_, _), idx in p.groupby(["monday", "sector"]).groups.items():
        ii = np.asarray(idx)
        if len(ii) > 1:
            newS[ii] = p["S"].values[rng.permutation(ii)]
    p["S"] = newS
    p["RISK_SCORE"] = p["S"] / CLIP
    p["n_raw"] = p["RISK_SCORE"] * RISK_BUDGET / p["SIGMA"]
    p["gross_i"] = p["RISK_SCORE"].abs() * RISK_BUDGET
    gs = p.groupby(["monday", "sector"])["gross_i"].transform("sum")
    gt = p.groupby("monday")["gross_i"].transform("sum")
    share = np.where(gt > 0, gs / gt, 0.0)
    p["sector_scale"] = np.where(share > SECTOR_CAP, SECTOR_CAP * gt / np.maximum(gs, 1e-12), 1.0)
    p["n"] = p["n_raw"] * p["sector_scale"]
    return p.drop(columns=["gross_i"])
