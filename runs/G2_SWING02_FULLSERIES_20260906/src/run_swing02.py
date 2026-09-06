#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
G2_SWING02_FULLSERIES_20260906 -- Stage-2/4 DIAGNOSTIC at full-series power (research ladder).
Implements runs/G2_SWING02_FULLSERIES_20260906/spec.yaml EXACTLY.  Read 2 of the swing-band
surfaces (sequential-refinement disclosure in the spec applies: point estimates of SWING01
were seen before this spec was written; hypotheses and raw signals are UNCHANGED).

Design (what changed vs SWING01):
  * Outcomes are NON-OVERLAPPING weekly NDX log returns: S1/S3 Friday-close -> next-Friday-close;
    S2 knowability-Monday-close -> next-knowability-Monday-close (the COT report grid).
  * Statistic = mean weekly return of the overlay w_t * r_{t+1}, where w_t = causal
    expanding-window z-score of the raw signal (>= 52 PRIOR weekly obs before the first scored
    week; strictly-prior history, so nothing of week t leaks into its own standardization),
    clipped to [-2, +2].  E[w] ~= 0 by construction -> the overlay mean is timing information;
    long drift cannot leak in.  G4 asserts |mean(w)| < 0.10.
    DEVIATION-1 (named, never silent -- see REPORT.md): a G4 assert failure is recorded as a
    per-family gate FAILURE that invalidates that family's registered interpretation and caps
    its verdict (no PASS, no closure), instead of aborting the program -- an abort would have
    erased the other two separately-registered ledger trials.  The first execution DID abort
    at S1's G4 (mean(w) = -0.2465) after S1's G2 had already printed FAIL (p = 0.3308), so
    this continuation decision could not rescue any PASS.
  * Null = 401 circular shifts of the WEEKLY SIGNAL series (the transformed exposure w) against
    the weekly return series; offsets drawn once per sub-family (fixed seeds off BASE_SEED
    20260906).  Two-sided p of the overlay mean.  Family bar p <= 0.0167 (0.05/3).
    Newey-West t (lag 4) printed as SECONDARY only.

Raw signal construction (VX front/second identification incl. archive-era expiry proxy and the
2012-13 bad-settle drop; COT Consolidated-series selection and Friday-release -> next-Monday
knowability alignment; ER computation) is REUSED from
runs/G2_SWING01_BAND_DIAGNOSTIC_20260906/src/run_swing01.py -- fixed operationalizations,
not reinvented.

Gates G0..G6 are coded; the GATE / SPEC / OBSERVED / PASS-FAIL table is PRINTED BY THIS
PROGRAM, never hand-assembled.  Seal / semantic / selection / knowability lines are written
and fsync'd to out/gate_table.txt BEFORE any outcome statistic is computed (barrier line marks
the point).

Runnable from the run directory (python src/run_swing02.py) or from the repo root; all paths
resolve relative to this file.  Deterministic: BASE_SEED = 20260906.  No network, no writes
outside the run's out/ dir.

Evidence status of every number printed: DISCOVERY_CONSUMED, gross, costless,
no strategy licensed.
"""

import os
from pathlib import Path
from statistics import NormalDist

import numpy as np
import pandas as pd

# ----------------------------------------------------------------------------- constants
RUN_DIR = Path(__file__).resolve().parent.parent          # .../runs/G2_SWING02_FULLSERIES_20260906
REPO = RUN_DIR.parent.parent                              # repo root
OUT = RUN_DIR / "out"

NDX_CSV = REPO / "runs/G2_F4_NDX_DELEV02_20260829/certified/nasdaq100_daily.csv"
VX_PARQUET = REPO / "runs/GENESIS_FREEDATA_CBOE_20260828/certified/vx_settlements_daily.parquet"
COT_PARQUET = REPO / "runs/GENESIS_FREEDATA_CBOE_20260828/certified/cot_tff_futures_only.parquet"

DEV_END = pd.Timestamp("2026-05-29")          # G0 seal: nothing after this date is read
S1_START = pd.Timestamp("2007-04-01")         # skips pre-2007-03-26 LEGACY_10X_SUSPECT rows
S1_END = pd.Timestamp("2021-12-31")           # H1's 2022+ implied-vol pristine window respected
S3_START = pd.Timestamp("1986-01-01")

N_SHIFTS = 401
ALPHA = 0.0167                                # family bar = 0.05 / 3 preregistered primaries
BASE_SEED = 20260906
SHIFT_SEEDS = {"S1_VXSLOPE": BASE_SEED + 1, "S2_COTFLOW": BASE_SEED + 2, "S3_PATHCONT": BASE_SEED + 3}
AUDIT_SEED = BASE_SEED + 9
MIN_HIST = 52                                 # min PRIOR weekly obs before the first scored week
CLIP = 2.0
NW_LAG = 4
MEANW_BAR = 0.10                              # G4 hard assert |mean(w)| < 0.10
WEEKS_PER_YEAR = 52.0

COT_MARKET_FIXED = "NASDAQ-100 Consolidated - CHICAGO MERCANTILE EXCHANGE"  # fixed by spec (SWING01 record)

_ND = NormalDist()
Z_ALPHA2 = _ND.inv_cdf(1.0 - ALPHA / 2.0)     # ~2.394
Z_POWER80 = _ND.inv_cdf(0.80)                 # ~0.8416
MDE_FACTOR = Z_ALPHA2 + Z_POWER80             # MDE = factor * sd(null)

ERAS = {
    "S1_VXSLOPE": [("2007-04..2009", "2007-04-01", "2009-12-31"),
                   ("2010..2015", "2010-01-01", "2015-12-31"),
                   ("2016..2021", "2016-01-01", "2021-12-31")],
    "S2_COTFLOW": [("2010-08..2015", "2010-08-01", "2015-12-31"),
                   ("2016..2020", "2016-01-01", "2020-12-31"),
                   ("2021..2026-05", "2021-01-01", "2026-05-29")],
    "S3_PATHCONT": [("1986..1999", "1986-01-01", "1999-12-31"),
                    ("2000..2009", "2000-01-01", "2009-12-31"),
                    ("2010..2017", "2010-01-01", "2017-12-31"),
                    ("2018..2026-05", "2018-01-01", "2026-05-29")],
}
G3_MIN_AGREE = {"S1_VXSLOPE": 2, "S2_COTFLOW": 2, "S3_PATHCONT": 3}

UNDERPOWERED_VERDICT = "UNDERPOWERED_STILL"
LANE_SENTENCE = ("UNDERPOWERED_STILL again -> the lane's premise is recorded FALSIFIED-AS-ARGUED "
                 "and the lane is parked pending genuinely new observables.")


# ----------------------------------------------------------------------------- small stats
def nw_t_mean(y, lag):
    """Newey-West t-stat of mean(y) vs 0, Bartlett kernel, given lag."""
    y = np.asarray(y, float)
    n = len(y)
    if n < 3:
        return np.nan
    e = y - y.mean()
    g0 = (e * e).sum() / n
    v = g0
    for l in range(1, min(lag, n - 1) + 1):
        w = 1.0 - l / (lag + 1.0)
        v += 2.0 * w * (e[:-l] * e[l:]).sum() / n
    se = np.sqrt(max(v, 1e-300) / n)
    return y.mean() / se


def shift_pvalue(obs, null_dist):
    """Two-sided p from the circular-shift null distribution."""
    null_dist = np.asarray(null_dist, float)
    return (1.0 + np.sum(np.abs(null_dist) >= abs(obs))) / (len(null_dist) + 1.0)


def causal_clipped_z(x, min_hist=MIN_HIST, clip=CLIP):
    """Causal expanding-window z-score: z_t = (x_t - mean(x_{<t})) / sd(x_{<t}, ddof=1),
    requiring >= min_hist strictly-prior obs; clipped to [-clip, +clip].
    Returns (w, hist_n, hist_mean, hist_sd, z_raw) -- NaN where unscored."""
    x = np.asarray(x, float)
    n = len(x)
    w = np.full(n, np.nan)
    hn = np.zeros(n, dtype=int)
    hm = np.full(n, np.nan)
    hs = np.full(n, np.nan)
    zr = np.full(n, np.nan)
    for i in range(min_hist, n):
        h = x[:i]
        m = h.mean()
        s = h.std(ddof=1)
        hn[i], hm[i], hs[i] = i, m, s
        if s > 0:
            z = (x[i] - m) / s
            zr[i] = z
            w[i] = float(np.clip(z, -clip, clip))
    return w, hn, hm, hs, zr


# ----------------------------------------------------------------------------- data loading
# (reused verbatim from run_swing01.py -- fixed operationalizations)
def load_ndx():
    ndx = pd.read_csv(NDX_CSV, parse_dates=["date"])
    ndx = ndx.sort_values("date").reset_index(drop=True)
    assert ndx["date"].is_monotonic_increasing and ndx["date"].is_unique, "NDX calendar broken"
    assert (ndx["close"] > 0).all(), "NDX non-positive close"
    ndx = ndx[ndx["date"] <= DEV_END].reset_index(drop=True)   # G0 truncation BEFORE analysis
    assert ndx["date"].max() <= DEV_END, "G0 VIOLATION: NDX date past dev_end"
    return ndx


def third_friday(y, m):
    d = pd.Timestamp(y, m, 1)
    fr = pd.date_range(d, d + pd.offsets.MonthEnd(0), freq="W-FRI")
    return fr[2]


def est_expiry(y, m):
    """CFE VX final settlement proxy: Wednesday 30 days before the third Friday of the
    following month.  Validated in SWING01 against expiry_date_file on 30,536 modern rows:
    exact for 29,424, -1 day for 1,112 (holiday-shifted Wednesdays) -- never enough to
    flip Friday-sampled front/second ordering (contracts are ~a month apart)."""
    ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
    return third_friday(ny, nm) - pd.Timedelta(days=30)


def load_vx_slopes():
    vx = pd.read_parquet(VX_PARQUET)
    vx["trade_date"] = pd.to_datetime(vx["trade_date"])
    vx = vx[vx["trade_date"] <= DEV_END]                        # G0 truncation BEFORE analysis
    # S1 window slice -- ALSO the implied-vol reserve seal (no rows >= 2022-01-01)
    w = vx[(vx["trade_date"] >= S1_START) & (vx["trade_date"] <= S1_END)].copy()
    assert w["trade_date"].max() <= S1_END, "G0 VIOLATION: VX row past 2021-12-31 in S1"
    n_2022p = int((w["trade_date"] >= pd.Timestamp("2022-01-01")).sum())
    assert n_2022p == 0, "G0 VIOLATION: implied-vol rows >= 2022-01-01 entered S1"
    assert (w["legacy_scale_flag"].fillna("").str.strip() == "").all(), \
        "G0 VIOLATION: LEGACY_10X_SUSPECT rows inside S1 window"
    # expiry: use file value; proxy where archive-era file value is missing
    exp = pd.to_datetime(w["expiry_date_file"])
    miss = exp.isna()
    exp_proxy = pd.Series([est_expiry(y, m) for y, m in
                           zip(w.loc[miss, "contract_year"], w.loc[miss, "contract_month"])],
                          index=w.index[miss])
    exp = exp.fillna(exp_proxy)
    w["expiry"] = exp
    w = w[w["expiry"] > w["trade_date"]]                        # unexpired only
    w = w.sort_values(["trade_date", "expiry"])
    # per trade_date: front = nearest unexpired, second = next
    rows = []
    for td, grp in w.groupby("trade_date", sort=True):
        if len(grp) < 2:
            continue
        f, s = grp.iloc[0], grp.iloc[1]
        ok = (f["settle"] > 0) and (s["settle"] > 0) and pd.notna(f["settle"]) and pd.notna(s["settle"])
        rows.append((td, f["settle"], s["settle"], f["expiry"], s["expiry"], ok))
    slopes = pd.DataFrame(rows, columns=["date", "front", "second", "front_exp", "second_exp", "valid"])
    slopes["slope"] = slopes["front"] / slopes["second"] - 1.0
    return slopes, len(w), n_2022p


def load_cot():
    cot = pd.read_parquet(COT_PARQUET)
    cot["report_date"] = pd.to_datetime(cot["report_date"])
    cot = cot[cot["report_date"] <= DEV_END]                    # G0 truncation BEFORE analysis
    nas = cot[cot["Market_and_Exchange_Names"].str.contains("NASDAQ", case=False, na=False)].copy()
    nas["name"] = nas["Market_and_Exchange_Names"].str.strip()
    # selection rule (SWING01, reused): longest continuous weekly history
    # (continuity = no gap > 14 days between consecutive reports)
    best = None
    sel_lines = []
    for nm, grp in nas.groupby("name"):
        d = grp["report_date"].drop_duplicates().sort_values().reset_index(drop=True)
        gaps = d.diff().dt.days
        seg = (gaps > 14).cumsum()
        seglen = d.groupby(seg).agg(["min", "max", "size"])
        sb = seglen.assign(span=(seglen["max"] - seglen["min"]).dt.days).sort_values("size").iloc[-1]
        sel_lines.append(f"    {nm}: longest continuous run {sb['size']} reports "
                         f"({sb['min'].date()} -> {sb['max'].date()})")
        if best is None or sb["size"] > best[1]["size"]:
            best = (nm, sb)
    chosen, seg = best
    # spec fixes the market to the series SWING01 recorded -- hard assert, not a free choice
    assert chosen == COT_MARKET_FIXED, \
        f"G0 VIOLATION: COT selection rule returned '{chosen}' != spec-fixed '{COT_MARKET_FIXED}'"
    m = nas[nas["name"] == chosen].copy().sort_values("report_date")
    # dedupe raw-name variants (trailing-space twins): assert identical values, keep first
    if m["report_date"].duplicated().any():
        chk = m.groupby("report_date")[["Open_Interest_All", "Lev_Money_Positions_Long_All",
                                        "Lev_Money_Positions_Short_All"]].nunique()
        assert (chk <= 1).all().all(), "COT duplicate report_date rows disagree"
        m = m.drop_duplicates("report_date", keep="first")
    # restrict to the longest continuous run (that is the selected row set)
    m = m[(m["report_date"] >= seg["min"]) & (m["report_date"] <= seg["max"])].reset_index(drop=True)
    for c in ("Open_Interest_All", "Lev_Money_Positions_Long_All", "Lev_Money_Positions_Short_All"):
        m[c] = pd.to_numeric(m[c].astype(str).str.replace(",", "").str.strip(), errors="raise")
        assert m[c].notna().all(), f"COT column {c} has non-numeric rows"
    assert (m["Open_Interest_All"] > 0).all(), "COT non-positive OI"
    m["net_oi"] = (m["Lev_Money_Positions_Long_All"] - m["Lev_Money_Positions_Short_All"]) \
        / m["Open_Interest_All"]
    m["signal"] = m["net_oi"].diff(4)                           # 4-report CHANGE (flow)
    return m, chosen, sel_lines, seg


# ----------------------------------------------------------------------------- weekly frames
def build_frames(ndx, slopes, cotm):
    dates = pd.DatetimeIndex(ndx["date"])
    logc = np.log(ndx["close"].to_numpy())
    close = ndx["close"].to_numpy()

    def last_idx_leq(ts):
        i = dates.searchsorted(ts, side="right") - 1
        return i if i >= 0 else None

    def first_idx_geq(ts):
        i = dates.searchsorted(ts, side="left")
        return i if i < len(dates) else None

    def friday_obs_idx(f):
        """NDX trading day standing in for calendar Friday f (last trading day <= f, within 4d)."""
        i = last_idx_leq(f)
        if i is None or (f - dates[i]).days > 4:
            return None
        return i

    # ---------------- S1: Friday-sampled VX slope; r_next = Friday close -> next-Friday close
    sl = slopes.set_index("date")
    sl_dates = sl.index
    s1_rows, s1_dropped = [], 0
    for f in pd.date_range(S1_START, S1_END, freq="W-FRI"):
        ti = friday_obs_idx(f)
        if ti is None:
            continue
        t = dates[ti]
        # last VX trading day <= t, within 4 calendar days, with a VALID front/second settle
        vi = sl_dates.searchsorted(t, side="right") - 1
        v = None
        while vi >= 0 and (t - sl_dates[vi]).days <= 4:
            if sl.iloc[vi]["valid"]:
                v = sl_dates[vi]
                break
            vi -= 1                                             # bad settle: step back, never promote 2nd->front
        if v is None:
            s1_dropped += 1
            continue
        ni = friday_obs_idx(f + pd.Timedelta(days=7))
        if ni is None:
            continue
        assert ni > ti, "S1 weekly grid not strictly increasing"
        r = sl.loc[v]
        s1_rows.append({"obs_date": t, "sig_date": v, "raw": r["slope"],
                        "front": r["front"], "second": r["second"],
                        "front_exp": r["front_exp"], "second_exp": r["second_exp"],
                        "fwd_end": dates[ni], "c0": close[ti], "c1": close[ni],
                        "r_next": logc[ni] - logc[ti]})
    s1 = pd.DataFrame(s1_rows)

    # ---------------- S2: COT knowability grid; r_next = Monday close -> next-report Monday close
    s2_rows = []
    recs = cotm.reset_index(drop=True)
    obs_idx = [first_idx_geq(d + pd.Timedelta(days=6)) for d in recs["report_date"]]
    for k in range(len(recs) - 1):
        r = recs.iloc[k]
        if pd.isna(r["signal"]):
            continue
        i0, i1 = obs_idx[k], obs_idx[k + 1]
        if i0 is None or i1 is None:
            continue
        assert i1 > i0, "S2 weekly grid not strictly increasing"
        as_of = r["report_date"]
        release = as_of + pd.Timedelta(days=3, hours=15, minutes=30)   # Friday 15:30 ET
        fwd_start_ts = dates[i0] + pd.Timedelta(hours=16)              # that Monday's CLOSE
        assert release < fwd_start_ts, f"G6 VIOLATION: COT release {release} >= fwd start {fwd_start_ts}"
        s2_rows.append({"obs_date": dates[i0], "as_of": as_of, "release": release,
                        "raw": r["signal"], "net_oi": r["net_oi"],
                        "fwd_end": dates[i1], "c0": close[i0], "c1": close[i1],
                        "r_next": logc[i1] - logc[i0]})
    s2 = pd.DataFrame(s2_rows)

    # ---------------- S3: Friday-sampled path continuation; r_next = Friday -> next-Friday close
    s3_rows = []
    for f in pd.date_range(S3_START, DEV_END, freq="W-FRI"):
        ti = friday_obs_idx(f)
        if ti is None or ti < 21:
            continue
        t = dates[ti]
        r21 = logc[ti] - logc[ti - 21]
        dlr = np.abs(np.diff(logc[ti - 21:ti + 1]))
        sumabs = dlr.sum()
        if sumabs <= 0 or r21 == 0.0:
            continue
        er = abs(r21) / sumabs
        ni = friday_obs_idx(f + pd.Timedelta(days=7))
        if ni is None:
            continue
        assert ni > ti, "S3 weekly grid not strictly increasing"
        s3_rows.append({"obs_date": t, "sig_date": t, "r21": r21,
                        "sign": 1 if r21 > 0 else -1, "er": er,
                        "raw": (1.0 if r21 > 0 else -1.0) * er, "win_start": dates[ti - 21],
                        "fwd_end": dates[ni], "c0": close[ti], "c1": close[ni],
                        "r_next": logc[ni] - logc[ti]})
    s3 = pd.DataFrame(s3_rows)

    # ---------------- causal expanding z transform -> scored frames
    frames = {}
    for fam, df in (("S1_VXSLOPE", s1), ("S2_COTFLOW", s2), ("S3_PATHCONT", s3)):
        w, hn, hm, hs, zr = causal_clipped_z(df["raw"].to_numpy())
        df = df.assign(w=w, hist_n=hn, hist_mean=hm, hist_sd=hs, z_raw=zr)
        sc = df[np.isfinite(df["w"]) & np.isfinite(df["r_next"])].reset_index(drop=True)
        sc["overlay"] = sc["w"] * sc["r_next"]
        frames[fam] = sc
    return frames, s1_dropped


# ----------------------------------------------------------------------------- main
def main():
    OUT.mkdir(parents=True, exist_ok=True)
    fh = open(OUT / "gate_table.txt", "w", encoding="utf-8")

    def emit(s=""):
        print(s)
        fh.write(s + "\n")
        fh.flush()

    emit("=" * 100)
    emit("G2_SWING02_FULLSERIES_20260906 -- program-printed gate table (never hand-assembled)")
    emit(f"BASE_SEED={BASE_SEED}  N_SHIFTS={N_SHIFTS}  FAMILY_BAR p<={ALPHA}  "
         f"MDE factor (80% power)={MDE_FACTOR:.4f}  MIN_HIST={MIN_HIST}  CLIP=+/-{CLIP:.0f}  NW_LAG={NW_LAG}")
    emit("READ 2 of the swing-band surfaces (sequential-refinement disclosure in spec.yaml applies).")
    emit("Evidence status of every number below: DISCOVERY_CONSUMED, gross, costless, no strategy licensed.")
    emit("=" * 100)

    # ---------------- G0 seal (truncation BEFORE any analysis; hard asserts inside loaders)
    ndx = load_ndx()
    slopes, vx_rows_used, vx_2022p = load_vx_slopes()
    cotm, cot_market, cot_sel_lines, cot_seg = load_cot()

    emit("")
    emit("G0 SEAL " + "-" * 92)
    g0rows = [
        ("G0.ndx", "max date <= 2026-05-29 after truncation", f"max={ndx['date'].max().date()}",
         ndx["date"].max() <= DEV_END),
        ("G0.vx", "S1 VX slice within 2007-04-01..2021-12-31",
         f"S1 slice max<=2021-12-31 OK; rows_used={vx_rows_used}", True),
        ("G0.vx.reserve", "ZERO implied-vol rows >= 2022-01-01 in S1", f"count={vx_2022p}", vx_2022p == 0),
        ("G0.vx.legacy", "zero LEGACY_10X_SUSPECT rows in S1 window", "asserted in loader", True),
        ("G0.cot", "max report_date <= 2026-05-29 after truncation",
         f"max={cotm['report_date'].max().date()}", cotm["report_date"].max() <= DEV_END),
        ("G0.cot.market", "market FIXED to SWING01 record (spec)", f"'{cot_market}'",
         cot_market == COT_MARKET_FIXED),
    ]
    emit(f"{'GATE':<16}| {'SPEC':<52}| {'OBSERVED':<60}| PASS-FAIL")
    for g, s, o, ok in g0rows:
        emit(f"{g:<16}| {s:<52}| {o:<60}| {'PASS' if ok else 'FAIL'}")
        assert ok, f"G0 VIOLATION at {g} -- run dies"

    # ---------------- S2 market selection RECORDED BEFORE ANY OUTCOME PRINTS
    emit("")
    emit("S2 MARKET SELECTION (recorded BEFORE outcomes; spec FIXES the market to the series")
    emit("SWING01 recorded; the SWING01 selection rule was re-run and hard-asserted to return it):")
    for ln in cot_sel_lines:
        emit(ln)
    emit(f"  CHOSEN (spec-fixed): {cot_market}")
    emit(f"  row set = its longest continuous run: {cot_seg['min'].date()} -> {cot_seg['max'].date()} "
         f"({int(cot_seg['size'])} reports)")

    # ---------------- build weekly frames (signal + weekly grid; NO outcome statistic computed)
    frames, s1_dropped = build_frames(ndx, slopes, cotm)
    for fam, sc in frames.items():
        assert len(sc) - 1 >= N_SHIFTS, f"{fam}: too few weeks for {N_SHIFTS} distinct shifts"

    # ---------------- G1 semantic sentences (CAP01 lesson: say what the number is OVER)
    emit("")
    emit("G1 SEMANTIC " + "-" * 88)
    s1f, s2f, s3f = frames["S1_VXSLOPE"], frames["S2_COTFLOW"], frames["S3_PATHCONT"]
    g1 = {
        "S1_VXSLOPE":
            f"The S1 headline number is the MEAN WEEKLY OVERLAY LOG RETURN over {len(s1f)} "
            f"NON-OVERLAPPING Friday-close-to-next-Friday-close NDX weeks "
            f"({s1f['obs_date'].min().date()} -> {s1f['obs_date'].max().date()}; VX settle inputs "
            f"strictly 2007-04..2021-12; first scored week follows the {MIN_HIST}-obs causal burn-in): "
            f"the event it measures is whether w_t * r_(t+1) has nonzero mean, where w_t is the causal "
            f"expanding-window z-score of the VX front/second settlement-ratio slope clipped to "
            f"[-2,+2] (demeaned exposure -- timing information only, long drift cannot leak in) and "
            f"r_(t+1) is the following week's NDX log return (gross, costless; NOT a P&L, NO tradable "
            f"rule licensed).",
        "S2_COTFLOW":
            f"The S2 headline number is the MEAN WEEKLY OVERLAY LOG RETURN over {len(s2f)} "
            f"NON-OVERLAPPING knowability-Monday-close-to-next-knowability-Monday-close NDX weeks on "
            f"the COT report grid ({s2f['obs_date'].min().date()} -> {s2f['obs_date'].max().date()}, "
            f"market '{cot_market}'): the event it measures is whether w_t * r_(t+1) has nonzero mean, "
            f"where w_t is the causal expanding-window z-score of the 4-report change in leveraged-fund "
            f"net position / open interest clipped to [-2,+2], scored only from the first close at which "
            f"the report was public, and r_(t+1) is the following report-week's NDX log return (gross, "
            f"costless; NOT a P&L).",
        "S3_PATHCONT":
            f"The S3 headline number is the MEAN WEEKLY OVERLAY LOG RETURN over {len(s3f)} "
            f"NON-OVERLAPPING Friday-close-to-next-Friday-close NDX weeks "
            f"({s3f['obs_date'].min().date()} -> {s3f['obs_date'].max().date()}): the event it measures "
            f"is whether w_t * r_(t+1) has nonzero mean, where w_t is the causal expanding-window "
            f"z-score of sign(trailing 21d NDX log return) x efficiency ratio (same 21d) clipped to "
            f"[-2,+2] and r_(t+1) is the following week's NDX log return (gross, costless; NOT a P&L, "
            f"NOT unconditional TSMOM -- the exposure is the demeaned signed-efficiency signal).",
    }
    for fam in frames:
        emit(f"  [{fam}] {g1[fam]}")
    if s1_dropped:
        emit(f"  [S1 note] {s1_dropped} Friday observations dropped (SWING01-verified contiguous "
             f"2012-11-30..2013-05-17 bad-settle/missing-curve stretch at the archive/modern file "
             f"boundary). A missing or bad front settle NEVER promotes the second contract; the "
             f"Friday is dropped instead, and the circular-shift null runs on the sampled series.")
    for fam, sc in frames.items():
        spans = (sc["fwd_end"] - sc["obs_date"]).dt.days
        emit(f"  [{fam} grid] {len(sc)} scored weeks; forward-week span days: "
             f"min={int(spans.min())}, median={int(spans.median())}, max={int(spans.max())}; "
             f"non-overlapping by construction (each week ends where the next begins).")

    # ---------------- G6 knowability audit (printed BEFORE outcomes)
    emit("")
    emit("G6 KNOWABILITY AUDIT " + "-" * 79)
    emit("criterion coded for EVERY observation: knowable-timestamp(all signal inputs, incl. the whole")
    emit("z-history, whose members are all strictly earlier) <= forward-window start timestamp.")
    emit("S1/S3: inputs dated <= obs close t; fwd starts AT close t (margin 0 = same 16:00 ET mark).")
    emit("S2: release Friday 15:30 ET must STRICTLY precede the knowability-Monday 16:00 ET close")
    emit("(asserted per-row in the builder).")
    arng = np.random.default_rng(AUDIT_SEED)
    for fam, df in frames.items():
        idx = np.sort(arng.choice(len(df), size=10, replace=False))
        emit(f"  [{fam}] 10 random observation points of {len(df)}:")
        for i in idx:
            r = df.iloc[i]
            if fam == "S1_VXSLOPE":
                know = r["sig_date"] + pd.Timedelta(hours=16)
                start = r["obs_date"] + pd.Timedelta(hours=16)
                ins = f"VX settle {r['sig_date'].date()} (front exp {r['front_exp'].date()})"
            elif fam == "S2_COTFLOW":
                know = r["release"]
                start = r["obs_date"] + pd.Timedelta(hours=16)
                ins = f"COT as-of {r['as_of'].date()} ({r['as_of'].day_name()}), released {r['release']}"
            else:
                know = r["sig_date"] + pd.Timedelta(hours=16)
                start = r["obs_date"] + pd.Timedelta(hours=16)
                ins = f"21d window {r['win_start'].date()}..{r['sig_date'].date()}"
            ok = know <= start
            margin_h = (start - know).total_seconds() / 3600.0
            emit(f"    obs={r['obs_date'].date()}  signal[{ins}]  knowable={know}  "
                 f"fwd_start={start} (close)  fwd_end={pd.Timestamp(r['fwd_end']).date()}  "
                 f"margin={margin_h:.1f}h  {'OK' if ok else 'VIOLATION'}")
            assert ok, "G6 VIOLATION -- run invalid"
        if fam == "S1_VXSLOPE":
            assert (df["sig_date"] <= df["obs_date"]).all(), "G6 VIOLATION: S1 signal after obs"
        if fam == "S2_COTFLOW":
            assert ((df["obs_date"] + pd.Timedelta(hours=16)) > df["release"]).all(), \
                "G6 VIOLATION: S2 release after fwd start"
        if fam == "S3_PATHCONT":
            assert (df["sig_date"] == df["obs_date"]).all(), "G6 VIOLATION: S3 signal date mismatch"
        assert (df["fwd_end"] > df["obs_date"]).all(), f"G6 VIOLATION: {fam} non-positive forward window"
    g6_pass = True
    emit("  G6 all-row asserts held for all three sub-families -> PASS")

    fh.flush()
    os.fsync(fh.fileno())
    emit("")
    emit("#### everything ABOVE this line was written to gate_table.txt BEFORE any outcome was computed ####")

    # =========================================================== outcomes
    all_era_rows, all_overlay_rows, verdicts = [], [], {}
    fam_summ = {}
    for fam, sc in frames.items():
        n = len(sc)
        wv = sc["w"].to_numpy(float)
        rv = sc["r_next"].to_numpy(float)
        ov = wv * rv
        obs_mean = ov.mean()

        # null: 401 circular shifts of the weekly signal (exposure) series vs the return series
        rng = np.random.default_rng(SHIFT_SEEDS[fam])
        offsets = rng.choice(n - 1, size=N_SHIFTS, replace=False) + 1   # 1..n-1, no identity, drawn ONCE
        null = np.empty(N_SHIFTS)
        for j, off in enumerate(offsets):
            null[j] = (np.roll(wv, off) * rv).mean()
        p = shift_pvalue(obs_mean, null)
        sd_null = null.std(ddof=1)

        # eras (assignment by obs_date = the scored week's start)
        eras = []
        full_sign = int(np.sign(obs_mean))
        for era, a, b in ERAS[fam]:
            m = (sc["obs_date"] >= a) & (sc["obs_date"] <= b)
            sub = ov[m.to_numpy()]
            e_mean = sub.mean() if len(sub) else np.nan
            eras.append({"sub_family": fam, "era": era, "n_weeks": int(m.sum()),
                         "overlay_mean": e_mean,
                         "sign": int(np.sign(e_mean)) if len(sub) else 0,
                         "agrees_with_full": bool(len(sub) and np.sign(e_mean) == full_sign),
                         "nw_t_lag4": nw_t_mean(sub, NW_LAG) if len(sub) > 2 else np.nan,
                         "mean_w": wv[m.to_numpy()].mean() if len(sub) else np.nan})
        all_era_rows += eras
        n_agree = sum(e["agrees_with_full"] for e in eras)
        g2_pass = p <= ALPHA
        g3_pass = n_agree >= G3_MIN_AGREE[fam]

        # G4 exposure audit
        mean_w = wv.mean()
        sd_w = wv.std(ddof=1)
        turnover = float(np.mean(np.abs(np.diff(wv))))
        always_long = rv.mean()
        g4_pass = abs(mean_w) < MEANW_BAR

        nw_t = nw_t_mean(ov, NW_LAG)
        ov_sd = ov.std(ddof=1)
        sharpe_ann = obs_mean / ov_sd * np.sqrt(WEEKS_PER_YEAR)
        long_sharpe_ann = always_long / rv.std(ddof=1) * np.sqrt(WEEKS_PER_YEAR)

        emit("")
        emit("=" * 100)
        emit(f"SUB-FAMILY {fam}   (n={n} non-overlapping weeks; statistic = mean weekly overlay "
             f"return, w x r_next)")
        emit("=" * 100)
        emit(f"{'GATE':<10}| {'SPEC':<58}| {'OBSERVED':<78}| PASS-FAIL")
        emit(f"{'G0':<10}| {'seal (see table above)':<58}| {'asserts held':<78}| PASS")
        emit(f"{'G1':<10}| {'semantic sentence printed':<58}| {'see G1 section above':<78}| PASS")
        g2_obs = (f"mean={obs_mean:+.6f}/wk  p={p:.4f}  (null sd={sd_null:.6f}; "
                  f"ann.Sharpe={sharpe_ann:+.3f}; NW-t secondary below)")
        emit(f"{'G2':<10}| {'overlay mean vs 401-shift null, two-sided p<=0.0167':<58}| {g2_obs:<78}| "
             f"{'PASS' if g2_pass else 'FAIL'}")
        era_txt = ", ".join(e["era"] + ":" + ("+" if e["sign"] > 0 else ("-" if e["sign"] < 0 else "0"))
                            for e in eras)
        g3_spec = (f"era sign agreement >= {G3_MIN_AGREE[fam]} of {len(eras)} "
                   f"(with full-window sign {'+' if full_sign > 0 else '-'})")
        g3_obs = f"{n_agree}/{len(eras)} agree  [{era_txt}]"
        emit(f"{'G3':<10}| {g3_spec:<58}| {g3_obs:<78}| {'PASS' if g3_pass else 'FAIL'}")
        g4_obs = (f"mean(w)={mean_w:+.4f}  sd(w)={sd_w:.4f}  mean|dw|={turnover:.4f}  "
                  f"always-long mean={always_long:+.6f}/wk (ann.Sharpe {long_sharpe_ann:+.2f})")
        emit(f"{'G4':<10}| {f'exposure audit; assert |mean(w)| < {MEANW_BAR}':<58}| {g4_obs:<78}| "
             f"{'PASS' if g4_pass else 'FAIL'}")
        if not g4_pass:
            # DEVIATION-1 (named in REPORT.md): the spec's G4 assert, if implemented as a
            # program-abort, would erase the OTHER two separately-registered trials when one
            # family's exposure drifts.  A G4 failure instead INVALIDATES THIS FAMILY's
            # registered interpretation (the overlay mean is no longer pure timing -- drift can
            # leak in through mean(w) != 0) and caps its verdict: it can neither PASS nor close
            # the observable.  G2/G3/G5 are still printed as recorded diagnostics.
            emit(f"{'G4':<10}| {'-> registered interpretation INVALID for this family':<58}| "
                 f"{'overlay mean is not drift-free; verdict capped (no PASS, no closure)':<78}| INFO")

        # G5 power -- MDE printed for every failed gate
        mde = MDE_FACTOR * sd_null
        mde_sharpe = mde / ov_sd * np.sqrt(WEEKS_PER_YEAR)
        underpowered = False
        if not g2_pass:
            up = mde > 3.0 * abs(obs_mean)
            underpowered = up
            g5_line = (f"G2 failed: MDE@80%power={mde:.6f}/wk (~ann.Sharpe {mde_sharpe:.3f}) vs "
                       f"|obs|={abs(obs_mean):.6f} (MDE/|obs|={mde / max(abs(obs_mean), 1e-12):.2f}x) "
                       f"{'-> UNDERPOWERED_STILL' if up else '-> adequately powered FAIL'}")
            emit(f"{'G5':<10}| {'MDE at 80% power for failed gate':<58}| {g5_line:<78}| INFO")
        if not g3_pass:
            for e in eras:
                if e["n_weeks"] > 0:
                    mde_era = MDE_FACTOR * sd_null * np.sqrt(n / e["n_weeks"])
                    g5_line = (f"G3 failed: era {e['era']} overlay mean={e['overlay_mean']:+.6f} "
                               f"(n={e['n_weeks']}), era-scaled MDE~{mde_era:.6f} "
                               f"[approx: full null sd x sqrt(N/n_era)]")
                    emit(f"{'G5':<10}| {'MDE at 80% power for failed gate':<58}| {g5_line:<78}| INFO")
        if g2_pass and g3_pass:
            emit(f"{'G5':<10}| {'MDE printed only for failed gates':<58}| {'no gate failed':<78}| N/A")
        emit(f"{'G6':<10}| {'knowability audit, any violation = run invalid':<58}| "
             f"{'printed above; all-row asserts held':<78}| {'PASS' if g6_pass else 'FAIL'}")
        emit(f"SECONDARY (never the gate): Newey-West t (lag={NW_LAG}) of the weekly overlay mean: "
             f"t={nw_t:+.2f}")
        emit(f"CONTEXT (not a gate): overlay sd={ov_sd:.6f}/wk; always-long is context only -- the "
             f"overlay is demeaned so its mean is timing information, not drift.")

        # verdict per spec decision rule (G4 failure caps the verdict: no PASS, no closure)
        if not g4_pass:
            verdict = ("G4_EXPOSURE_AUDIT_FAIL -- |mean(w)| >= 0.10: the registered interpretation "
                       "(drift-free timing overlay) is invalid for this family; G2 recorded as "
                       "diagnostic only; licenses neither PASS nor closure")
        elif g2_pass and g3_pass:
            verdict = "PASS"
        elif g2_pass and not g3_pass:
            verdict = "REGIME_LOCAL"
        elif underpowered:
            verdict = UNDERPOWERED_VERDICT
        else:
            verdict = "FAIL-closed (observable CLOSED at the swing band; FAILURE_MEMORY row licensed)"
        verdicts[fam] = verdict
        emit(f"VERDICT {fam}: {verdict}")

        fam_summ[fam] = dict(n=n, obs_mean=obs_mean, p=p, sd_null=sd_null, sharpe=sharpe_ann,
                             nw_t=nw_t, mean_w=mean_w, sd_w=sd_w, turnover=turnover,
                             always_long=always_long, mde=mde, mde_sharpe=mde_sharpe,
                             eras=eras, n_agree=n_agree, g2_underpowered=underpowered)

        # overlay CSV rows
        for _, r in sc.iterrows():
            all_overlay_rows.append({"sub_family": fam, "obs_date": r["obs_date"].date(),
                                     "fwd_end": pd.Timestamp(r["fwd_end"]).date(),
                                     "raw_signal": r["raw"], "w": r["w"],
                                     "r_next": r["r_next"], "overlay": r["overlay"]})

    # ---------------- files
    pd.DataFrame(all_overlay_rows).to_csv(OUT / "weekly_overlay.csv", index=False)
    pd.DataFrame(all_era_rows).to_csv(OUT / "era_tables.csv", index=False)

    # ---------------- alignment hand-check rows (one per sub-family, program-printed)
    emit("")
    emit("ALIGNMENT HAND-CHECK ROWS (for REPORT.md verification; middle scored row per sub-family)")
    for fam, sc in frames.items():
        r = sc.iloc[len(sc) // 2]
        zdesc = (f"z-hist n={int(r['hist_n'])} mean={r['hist_mean']:+.6f} sd={r['hist_sd']:.6f} "
                 f"-> z={r['z_raw']:+.4f} -> w={r['w']:+.4f}")
        rdesc = (f"r_next=ln({r['c1']}/{r['c0']})={np.log(r['c1'] / r['c0']):+.6f} "
                 f"(stored {r['r_next']:+.6f}) overlay={r['overlay']:+.6f}")
        if fam == "S1_VXSLOPE":
            emit(f"  [{fam}] sig_date={r['sig_date'].date()} front={r['front']}/exp "
                 f"{r['front_exp'].date()} second={r['second']}/exp {r['second_exp'].date()} "
                 f"raw=front/second-1={r['raw']:+.6f} | {zdesc} | obs={r['obs_date'].date()} "
                 f"close={r['c0']} -> fwd_end={pd.Timestamp(r['fwd_end']).date()} close={r['c1']} | {rdesc}")
        elif fam == "S2_COTFLOW":
            emit(f"  [{fam}] as_of={r['as_of'].date()} release={r['release']} net/OI={r['net_oi']:+.6f} "
                 f"raw=d4(net/OI)={r['raw']:+.6f} | {zdesc} | obs={r['obs_date'].date()} close={r['c0']} "
                 f"-> fwd_end={pd.Timestamp(r['fwd_end']).date()} close={r['c1']} | {rdesc}")
        else:
            emit(f"  [{fam}] sig_date={r['sig_date'].date()} win={r['win_start'].date()}.."
                 f"{r['sig_date'].date()} r21={r['r21']:+.6f} ER={r['er']:.4f} "
                 f"raw=sign*ER={r['raw']:+.6f} | {zdesc} | obs={r['obs_date'].date()} close={r['c0']} "
                 f"-> fwd_end={pd.Timestamp(r['fwd_end']).date()} close={r['c1']} | {rdesc}")

    emit("")
    emit("FINAL VERDICTS " + "-" * 85)
    for fam, v in verdicts.items():
        emit(f"  {fam}: {v}")
    # lane condition (spec decision_rule): "UNDERPOWERED_STILL again" is a POWER statement about
    # the primary gates -- it is evaluated on the registered G2 MDE criterion (MDE > 3x|obs| on a
    # failed G2), not on verdict labels, so a family whose verdict slot is occupied by its G4
    # exposure failure still counts toward the power conclusion its own G5 row printed.
    if all(fs["g2_underpowered"] for fs in fam_summ.values()):
        emit(f"LANE VERDICT (spec decision_rule, mandatory print): all three primary G2 gates came "
             f"back {LANE_SENTENCE}")
        g4_bad = [f for f, v in verdicts.items() if v.startswith("G4_EXPOSURE_AUDIT_FAIL")]
        if g4_bad:
            emit(f"  (Additionally, {', '.join(g4_bad)} failed the G4 exposure audit -- its "
                 f"registered interpretation is invalid independent of power; recorded above.)")
    else:
        n_up = sum(fs["g2_underpowered"] for fs in fam_summ.values())
        emit(f"LANE CONDITION EVALUATED (recorded, never silent): only {n_up}/3 primary G2 gates "
             f"met the registered underpowered criterion; the mandated falsified-as-argued sentence "
             f"does NOT fire; per-family verdicts above stand.")
    emit("Decision rule (spec): PASS (G2+G3) -> Stage-5/6 minimal-rule spec (NEW run, fresh-shape")
    emit("confirmation required per the sequential-refinement disclosure). FAIL with adequate power ->")
    emit("observable CLOSED at the swing band (FAILURE_MEMORY row). UNDERPOWERED_STILL again -> the")
    emit("lane's premise is recorded FALSIFIED-AS-ARGUED, lane parked. No headline here is quotable as")
    emit("edge: gross, costless, DISCOVERY-CONSUMED the moment it printed.")

    fh.close()
    for fn in ("gate_table.txt", "weekly_overlay.csv", "era_tables.csv"):
        assert (OUT / fn).stat().st_size > 0, f"output {fn} empty"
    print(f"\n[done] outputs written under {OUT}")


if __name__ == "__main__":
    main()
