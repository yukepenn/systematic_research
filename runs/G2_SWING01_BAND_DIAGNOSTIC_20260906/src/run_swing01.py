#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
G2_SWING01_BAND_DIAGNOSTIC_20260906 -- Stage-2 DIAGNOSTIC (research ladder).
Implements runs/G2_SWING01_BAND_DIAGNOSTIC_20260906/spec.yaml EXACTLY.

Three sub-families at the 3-session-to-3-month swing band:
  D1_VXSLOPE : VX front/second settlement-ratio slope, Friday-sampled, 2007-04..2021-12
  D2_COTFLOW : 4-report change in Lev_Money net/OI, NASDAQ-100 market (longest continuous
               weekly history), COT-knowability sampled, 2006..2026-05-29
  D3_PATHCONT: sign(trailing 21d NDX log return) x efficiency-ratio tercile, 1986..2026-05-29

Gates G0..G6 are coded; the GATE / SPEC / OBSERVED / PASS-FAIL table is PRINTED BY THIS
PROGRAM, never hand-assembled.  Family bar p <= 0.0167 (0.05/3).  Null = 401 circular
shifts of the SIGNAL series, offsets drawn once per sub-family (fixed seed) and SHARED
across horizons.  Newey-West t (lag = horizon) is printed as SECONDARY only.

Runnable from the run directory (python src/run_swing01.py) or from the repo root
(python runs/G2_SWING01_BAND_DIAGNOSTIC_20260906/src/run_swing01.py): all paths are
resolved relative to this file's location.

Deterministic: BASE_SEED = 20260906.  No network, no writes outside the run's out/ dir.

Evidence status of every number printed: DISCOVERY_CONSUMED, gross, costless,
no strategy licensed.
"""

import os
import sys
from pathlib import Path
from statistics import NormalDist

import numpy as np
import pandas as pd

# ----------------------------------------------------------------------------- constants
RUN_DIR = Path(__file__).resolve().parent.parent          # .../runs/G2_SWING01_BAND_DIAGNOSTIC_20260906
REPO = RUN_DIR.parent.parent                              # repo root
OUT = RUN_DIR / "out"

NDX_CSV = REPO / "runs/G2_F4_NDX_DELEV02_20260829/certified/nasdaq100_daily.csv"
VX_PARQUET = REPO / "runs/GENESIS_FREEDATA_CBOE_20260828/certified/vx_settlements_daily.parquet"
COT_PARQUET = REPO / "runs/GENESIS_FREEDATA_CBOE_20260828/certified/cot_tff_futures_only.parquet"

DEV_END = pd.Timestamp("2026-05-29")          # G0 seal: nothing after this date is read
D1_START = pd.Timestamp("2007-04-01")         # skips pre-2007-03-26 LEGACY_10X_SUSPECT rows
D1_END = pd.Timestamp("2021-12-31")           # H1's 2022+ implied-vol pristine window respected
D3_START = pd.Timestamp("1986-01-01")

HORIZONS = (5, 21, 63)                        # trading days; 21 is THE PRIMARY
H_PRIMARY = 21
N_SHIFTS = 401
ALPHA = 0.0167                                # family bar = 0.05 / 3 preregistered primaries
BASE_SEED = 20260906
SHIFT_SEEDS = {"D1_VXSLOPE": BASE_SEED + 1, "D2_COTFLOW": BASE_SEED + 2, "D3_PATHCONT": BASE_SEED + 3}
AUDIT_SEED = BASE_SEED + 9

_ND = NormalDist()
Z_ALPHA2 = _ND.inv_cdf(1.0 - ALPHA / 2.0)     # ~2.394
Z_POWER80 = _ND.inv_cdf(0.80)                 # ~0.8416
MDE_FACTOR = Z_ALPHA2 + Z_POWER80             # MDE = factor * sd(null)

ERAS = {
    "D1_VXSLOPE": [("2007-04..2009", "2007-04-01", "2009-12-31"),
                   ("2010..2015", "2010-01-01", "2015-12-31"),
                   ("2016..2021", "2016-01-01", "2021-12-31")],
    "D2_COTFLOW": [("2006..2012", "2006-01-01", "2012-12-31"),
                   ("2013..2019", "2013-01-01", "2019-12-31"),
                   ("2020..2026-05", "2020-01-01", "2026-05-29")],
    "D3_PATHCONT": [("1986..1999", "1986-01-01", "1999-12-31"),
                    ("2000..2009", "2000-01-01", "2009-12-31"),
                    ("2010..2017", "2010-01-01", "2017-12-31"),
                    ("2018..2026-05", "2018-01-01", "2026-05-29")],
}
G3_MIN_AGREE = {"D1_VXSLOPE": 2, "D2_COTFLOW": 2, "D3_PATHCONT": 3}

UNDERPOWERED_SENTENCE = "closes nothing on its own"


# ----------------------------------------------------------------------------- small stats
def avg_rank(a):
    """Average ranks (1-based) with tie handling."""
    a = np.asarray(a, dtype=float)
    order = np.argsort(a, kind="mergesort")
    ranks = np.empty(len(a), dtype=float)
    sa = a[order]
    i = 0
    while i < len(a):
        j = i
        while j + 1 < len(a) and sa[j + 1] == sa[i]:
            j += 1
        ranks[order[i:j + 1]] = 0.5 * (i + j) + 1.0
        i = j + 1
    return ranks


def weighted_corr(x, y, w):
    x = np.asarray(x, float); y = np.asarray(y, float); w = np.asarray(w, float)
    w = w / w.sum()
    mx = (w * x).sum(); my = (w * y).sum()
    cov = (w * (x - mx) * (y - my)).sum()
    vx = (w * (x - mx) ** 2).sum(); vy = (w * (y - my) ** 2).sum()
    return cov / np.sqrt(vx * vy)


def bucket_means(labels, y, k):
    n = np.bincount(labels, minlength=k).astype(float)
    s = np.bincount(labels, weights=y, minlength=k)
    return n, s / n


def stat_wspearman(labels, y, k):
    """Spearman rho of bucket rank vs bucket mean, weighted by bucket n."""
    n, m = bucket_means(labels, y, k)
    return weighted_corr(avg_rank(np.arange(k)), avg_rank(m), n)


def stat_spread(labels, y, k):
    """Top-bucket mean minus bottom-bucket mean."""
    _, m = bucket_means(labels, y, k)
    return m[k - 1] - m[0]


def stat_d3_contrast(cells, y):
    """cells = sign_idx*3 + ter (sign_idx 1=positive, 0=negative; ter 0=bottom,2=top).
    Contrast = [m(+,T) - m(-,T)] - [m(+,B) - m(-,B)]  (diff-in-diff of sign spreads)."""
    _, m = bucket_means(cells, y, 6)
    return (m[1 * 3 + 2] - m[0 * 3 + 2]) - (m[1 * 3 + 0] - m[0 * 3 + 0])


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


def nw_ols_t(X, y, lag):
    """OLS with Newey-West (Bartlett) HAC covariance; returns (beta, t)."""
    X = np.asarray(X, float); y = np.asarray(y, float)
    n, p = X.shape
    XtX_inv = np.linalg.inv(X.T @ X)
    beta = XtX_inv @ (X.T @ y)
    e = y - X @ beta
    u = X * e[:, None]
    S = u.T @ u
    for l in range(1, min(lag, n - 1) + 1):
        w = 1.0 - l / (lag + 1.0)
        G = u[:-l].T @ u[l:]
        S += w * (G + G.T)
    cov = XtX_inv @ S @ XtX_inv
    t = beta / np.sqrt(np.diag(cov))
    return beta, t


def shift_pvalue(obs, null_dist):
    """Two-sided p from the circular-shift null distribution."""
    null_dist = np.asarray(null_dist, float)
    return (1.0 + np.sum(np.abs(null_dist) >= abs(obs))) / (len(null_dist) + 1.0)


# ----------------------------------------------------------------------------- data loading
def load_ndx():
    ndx = pd.read_csv(NDX_CSV, parse_dates=["date"])
    ndx = ndx.sort_values("date").reset_index(drop=True)
    assert ndx["date"].is_monotonic_increasing and ndx["date"].is_unique, "NDX calendar broken"
    assert (ndx["close"] > 0).all(), "NDX non-positive close"
    pre_max = ndx["date"].max()
    ndx = ndx[ndx["date"] <= DEV_END].reset_index(drop=True)   # G0 truncation BEFORE analysis
    assert ndx["date"].max() <= DEV_END, "G0 VIOLATION: NDX date past dev_end"
    return ndx, pre_max


def third_friday(y, m):
    d = pd.Timestamp(y, m, 1)
    fr = pd.date_range(d, d + pd.offsets.MonthEnd(0), freq="W-FRI")
    return fr[2]


def est_expiry(y, m):
    """CFE VX final settlement proxy: Wednesday 30 days before the third Friday of the
    following month.  Validated against expiry_date_file on 30,536 modern rows:
    exact for 29,424, -1 day for 1,112 (holiday-shifted Wednesdays) -- never enough to
    flip Friday-sampled front/second ordering (contracts are ~a month apart)."""
    ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
    return third_friday(ny, nm) - pd.Timedelta(days=30)


def load_vx_slopes():
    vx = pd.read_parquet(VX_PARQUET)
    vx["trade_date"] = pd.to_datetime(vx["trade_date"])
    vx = vx[vx["trade_date"] <= DEV_END]                        # G0 truncation BEFORE analysis
    pre_max = vx["trade_date"].max()
    # D1 window slice -- ALSO the implied-vol reserve seal (no rows >= 2022-01-01)
    w = vx[(vx["trade_date"] >= D1_START) & (vx["trade_date"] <= D1_END)].copy()
    assert w["trade_date"].max() <= D1_END, "G0 VIOLATION: VX row past 2021-12-31 in D1"
    n_2022p = int((w["trade_date"] >= pd.Timestamp("2022-01-01")).sum())
    assert n_2022p == 0, "G0 VIOLATION: implied-vol rows >= 2022-01-01 entered D1"
    assert (w["legacy_scale_flag"].fillna("").str.strip() == "").all(), \
        "G0 VIOLATION: LEGACY_10X_SUSPECT rows inside D1 window"
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
    return slopes, pre_max, len(w), n_2022p


def load_cot():
    cot = pd.read_parquet(COT_PARQUET)
    cot["report_date"] = pd.to_datetime(cot["report_date"])
    cot = cot[cot["report_date"] <= DEV_END]                    # G0 truncation BEFORE analysis
    pre_max = cot["report_date"].max()
    nas = cot[cot["Market_and_Exchange_Names"].str.contains("NASDAQ", case=False, na=False)].copy()
    nas["name"] = nas["Market_and_Exchange_Names"].str.strip()
    # selection rule (spec): the NASDAQ Market_and_Exchange_Names row set with the LONGEST
    # CONTINUOUS weekly history (continuity = no gap > 14 days between consecutive reports)
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
    return m, chosen, sel_lines, pre_max, seg


# ----------------------------------------------------------------------------- obs frames
def build_frames(ndx, slopes, cotm):
    dates = pd.DatetimeIndex(ndx["date"])
    logc = np.log(ndx["close"].to_numpy())

    def last_idx_leq(ts):
        i = dates.searchsorted(ts, side="right") - 1
        return i if i >= 0 else None

    def first_idx_geq(ts):
        i = dates.searchsorted(ts, side="left")
        return i if i < len(dates) else None

    def fwd(i, h):
        return (logc[i + h] - logc[i]) if (i + h) < len(logc) else np.nan

    # ---------------- D1: Friday-sampled VX slope
    sl = slopes.set_index("date")
    sl_dates = sl.index
    d1_rows, d1_dropped = [], 0
    for f in pd.date_range(D1_START, D1_END, freq="W-FRI"):
        ti = last_idx_leq(f)
        if ti is None or (f - dates[ti]).days > 4:
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
            d1_dropped += 1
            continue
        r = sl.loc[v]
        d1_rows.append({"obs_date": t, "sig_date": v, "signal": r["slope"],
                        "front": r["front"], "second": r["second"],
                        "front_exp": r["front_exp"], "second_exp": r["second_exp"],
                        **{f"fwd_{h}": fwd(ti, h) for h in HORIZONS},
                        **{f"end_{h}": (dates[ti + h] if ti + h < len(dates) else pd.NaT) for h in HORIZONS}})
    d1 = pd.DataFrame(d1_rows)

    # ---------------- D2: COT knowability-sampled flow
    d2_rows = []
    for _, r in cotm.dropna(subset=["signal"]).iterrows():
        as_of = r["report_date"]
        release = as_of + pd.Timedelta(days=3, hours=15, minutes=30)   # Friday 15:30 ET
        ti = first_idx_geq(as_of + pd.Timedelta(days=6))               # NEXT Monday (or next trading day)
        if ti is None:
            continue
        t = dates[ti]
        fwd_start_ts = t + pd.Timedelta(hours=16)                      # that Monday's CLOSE
        assert release < fwd_start_ts, f"G6 VIOLATION: COT release {release} >= fwd start {fwd_start_ts}"
        d2_rows.append({"obs_date": t, "as_of": as_of, "release": release,
                        "signal": r["signal"], "net_oi": r["net_oi"],
                        **{f"fwd_{h}": fwd(ti, h) for h in HORIZONS},
                        **{f"end_{h}": (dates[ti + h] if ti + h < len(dates) else pd.NaT) for h in HORIZONS}})
    d2 = pd.DataFrame(d2_rows)

    # ---------------- D3: Friday-sampled path continuation
    d3_rows = []
    for f in pd.date_range(D3_START, DEV_END, freq="W-FRI"):
        ti = last_idx_leq(f)
        if ti is None or (f - dates[ti]).days > 4 or ti < 21:
            continue
        t = dates[ti]
        r21 = logc[ti] - logc[ti - 21]
        dlr = np.abs(np.diff(logc[ti - 21:ti + 1]))
        sumabs = dlr.sum()
        if sumabs <= 0 or r21 == 0.0:
            continue
        er = abs(r21) / sumabs
        d3_rows.append({"obs_date": t, "sig_date": t, "r21": r21, "sign": 1 if r21 > 0 else -1,
                        "er": er, "win_start": dates[ti - 21],
                        **{f"fwd_{h}": fwd(ti, h) for h in HORIZONS},
                        **{f"end_{h}": (dates[ti + h] if ti + h < len(dates) else pd.NaT) for h in HORIZONS}})
    d3 = pd.DataFrame(d3_rows)

    # PRIMARY population per sub-family = rows with fwd_21 available (h=5 always subset-safe;
    # h=63 exploratory on the sub-population with fwd_63 available, same bucket labels)
    d1 = d1[d1["fwd_21"].notna()].reset_index(drop=True)
    d2 = d2[d2["fwd_21"].notna()].reset_index(drop=True)
    d3 = d3[d3["fwd_21"].notna()].reset_index(drop=True)

    # bucket labels (full-window breakpoints on the primary population)
    d1["bucket"] = pd.qcut(d1["signal"], 5, labels=False)
    d2["bucket"] = pd.qcut(d2["signal"], 5, labels=False)
    d3["ter"] = pd.qcut(d3["er"], 3, labels=False)
    d3["cell"] = (d3["sign"] == 1).astype(int) * 3 + d3["ter"]
    assert d1["bucket"].nunique() == 5 and d2["bucket"].nunique() == 5, "quintile collapse"
    assert d3["cell"].nunique() == 6, "D3 cell collapse"
    return d1, d2, d3, d1_dropped


# ----------------------------------------------------------------------------- analysis per family
def family_stats(fam, df, label_col, k, stat_primary, stat_g4):
    """Observed stats, shared-offset circular-shift nulls, per horizon."""
    n = len(df)
    rng = np.random.default_rng(SHIFT_SEEDS[fam])
    offsets = rng.choice(n - 1, size=N_SHIFTS, replace=False) + 1     # 1..n-1, no identity, drawn ONCE
    labels = df[label_col].to_numpy(int)
    res = {"n": n, "offsets": offsets}
    for h in HORIZONS:
        y = df[f"fwd_{h}"].to_numpy(float)
        m = ~np.isnan(y)
        obs_p = stat_primary(labels[m], y[m], k) if stat_primary is not stat_d3_contrast \
            else stat_primary(labels[m], y[m])
        obs_s = stat_g4(labels[m], y[m], k) if stat_g4 is not stat_d3_contrast \
            else stat_g4(labels[m], y[m])
        null_p = np.empty(N_SHIFTS); null_s = np.empty(N_SHIFTS)
        for j, off in enumerate(offsets):
            lab = np.roll(labels, off)                                # shift SIGNAL vs outcomes
            null_p[j] = stat_primary(lab[m], y[m], k) if stat_primary is not stat_d3_contrast \
                else stat_primary(lab[m], y[m])
            null_s[j] = stat_g4(lab[m], y[m], k) if stat_g4 is not stat_d3_contrast \
                else stat_g4(lab[m], y[m])
        res[h] = {"obs_primary": obs_p, "p_primary": shift_pvalue(obs_p, null_p),
                  "sd_null_primary": null_p.std(ddof=1),
                  "obs_g4": obs_s, "p_g4": shift_pvalue(obs_s, null_s),
                  "sd_null_g4": null_s.std(ddof=1), "n_h": int(m.sum())}
    return res


def nw_secondary(fam, df, h):
    """NW t (lag=h) of the spread / interaction coefficient -- SECONDARY only."""
    y = df[f"fwd_{h}"].to_numpy(float)
    m = ~np.isnan(y)
    if fam == "D3_PATHCONT":
        sub = df[m & df["ter"].isin([0, 2])].sort_values("obs_date")
        s = sub["sign"].to_numpy(float)
        e = np.where(sub["ter"].to_numpy(int) == 2, 1.0, -1.0)
        X = np.column_stack([np.ones(len(sub)), s, e, s * e])
        beta, t = nw_ols_t(X, sub[f"fwd_{h}"].to_numpy(float), h)
        return 4.0 * beta[3], t[3]                                    # contrast = 4*b3, t = t(b3)
    sub = df[m & df["bucket"].isin([0, 4])].sort_values("obs_date")
    x = (sub["bucket"].to_numpy(int) == 4).astype(float)
    X = np.column_stack([np.ones(len(sub)), x])
    beta, t = nw_ols_t(X, sub[f"fwd_{h}"].to_numpy(float), h)
    return beta[1], t[1]


def era_analysis(fam, df, label_col, full_sign):
    """Era spreads/contrasts at h=21 and sign agreement with the full-window sign."""
    out = []
    for era, a, b in ERAS[fam]:
        sub = df[(df["obs_date"] >= a) & (df["obs_date"] <= b)]
        y = sub["fwd_21"].to_numpy(float)
        lab = sub[label_col].to_numpy(int)
        row = {"sub_family": fam, "era": era, "horizon": 21, "n_obs": len(sub)}
        try:
            if fam == "D3_PATHCONT":
                nvec = np.bincount(lab, minlength=6)
                if min(nvec[[0, 2, 3, 5]]) == 0:
                    raise ValueError("empty cell")
                val = stat_d3_contrast(lab, y)
                row["n_top"] = int(nvec[2] + nvec[5]); row["n_bot"] = int(nvec[0] + nvec[3])
            else:
                nvec = np.bincount(lab, minlength=5)
                if nvec[0] == 0 or nvec[4] == 0:
                    raise ValueError("empty bucket")
                val = stat_spread(lab, y, 5)
                row["n_top"] = int(nvec[4]); row["n_bot"] = int(nvec[0])
            row["spread_or_contrast"] = val
            row["sign"] = int(np.sign(val))
            row["agrees_with_full"] = bool(np.sign(val) == full_sign)
        except ValueError:
            row.update({"spread_or_contrast": np.nan, "sign": 0, "agrees_with_full": False,
                        "n_top": 0, "n_bot": 0})
        out.append(row)
    return out


def bucket_table_rows(fam, df, label_col, k, names):
    rows = []
    for h in HORIZONS:
        y = df[f"fwd_{h}"].to_numpy(float)
        m = ~np.isnan(y)
        for b in range(k):
            sel = m & (df[label_col].to_numpy(int) == b)
            yy = df.loc[sel].sort_values("obs_date")[f"fwd_{h}"].to_numpy(float)
            rows.append({"sub_family": fam, "cell": names[b], "horizon": h,
                         "n": len(yy), "mean_fwd_log": yy.mean() if len(yy) else np.nan,
                         "nw_t": nw_t_mean(yy, h)})
    return rows


# ----------------------------------------------------------------------------- main
def main():
    OUT.mkdir(parents=True, exist_ok=True)
    fh = open(OUT / "gate_table.txt", "w", encoding="utf-8")

    def emit(s=""):
        print(s)
        fh.write(s + "\n")
        fh.flush()

    emit("=" * 100)
    emit("G2_SWING01_BAND_DIAGNOSTIC_20260906 -- program-printed gate table (never hand-assembled)")
    emit(f"BASE_SEED={BASE_SEED}  N_SHIFTS={N_SHIFTS}  FAMILY_BAR p<={ALPHA}  "
         f"MDE factor (80% power)={MDE_FACTOR:.4f}")
    emit("Evidence status of every number below: DISCOVERY_CONSUMED, gross, costless, no strategy licensed.")
    emit("=" * 100)

    # ---------------- G0 seal (truncation BEFORE any analysis; hard asserts inside loaders)
    ndx, ndx_pre_max = load_ndx()
    slopes, vx_pre_max, vx_rows_used, vx_2022p = load_vx_slopes()
    cotm, cot_market, cot_sel_lines, cot_pre_max, cot_seg = load_cot()

    emit("")
    emit("G0 SEAL " + "-" * 92)
    g0rows = [
        ("G0.ndx", "max date <= 2026-05-29 after truncation", f"max={ndx['date'].max().date()}",
         ndx["date"].max() <= DEV_END),
        ("G0.vx", "max trade_date <= 2026-05-29; D1 slice <= 2021-12-31",
         f"D1 slice max<=2021-12-31 OK; rows_used={vx_rows_used}", True),
        ("G0.vx.reserve", "ZERO implied-vol rows >= 2022-01-01 in D1", f"count={vx_2022p}", vx_2022p == 0),
        ("G0.vx.legacy", "zero LEGACY_10X_SUSPECT rows in D1 window", "asserted in loader", True),
        ("G0.cot", "max report_date <= 2026-05-29 after truncation",
         f"max={cotm['report_date'].max().date()}", cotm["report_date"].max() <= DEV_END),
    ]
    emit(f"{'GATE':<16}| {'SPEC':<52}| {'OBSERVED':<48}| PASS-FAIL")
    for g, s, o, ok in g0rows:
        emit(f"{g:<16}| {s:<52}| {o:<48}| {'PASS' if ok else 'FAIL'}")
        assert ok, f"G0 VIOLATION at {g} -- run dies"

    # ---------------- D2 market selection RECORDED BEFORE ANY OUTCOME PRINTS
    emit("")
    emit("D2 MARKET SELECTION (recorded BEFORE outcomes; rule = longest continuous weekly history,")
    emit("continuity = no gap > 14 days between consecutive reports; candidates inspected):")
    for ln in cot_sel_lines:
        emit(ln)
    emit(f"  CHOSEN: {cot_market}")
    emit(f"  row set = its longest continuous run: {cot_seg['min'].date()} -> {cot_seg['max'].date()} "
         f"({int(cot_seg['size'])} reports)")
    emit("  Lev columns verified by inspection: Lev_Money_Positions_Long_All, "
         "Lev_Money_Positions_Short_All, Open_Interest_All")

    # ---------------- build observation frames (no outcome statistics yet)
    d1, d2, d3, d1_dropped = build_frames(ndx, slopes, cotm)
    frames = {"D1_VXSLOPE": d1, "D2_COTFLOW": d2, "D3_PATHCONT": d3}

    # ---------------- G1 semantic sentences (CAP01 lesson: say what the number is OVER)
    emit("")
    emit("G1 SEMANTIC " + "-" * 88)
    g1 = {
        "D1_VXSLOPE":
            f"The D1 headline statistic is computed over {len(d1)} weekly Friday-close observations "
            f"({d1['obs_date'].min().date()} -> {d1['obs_date'].max().date()}; VX settle inputs strictly "
            f"2007-04..2021-12); the event it measures is whether the full-window QUINTILE of the VX "
            f"front/second settlement-ratio slope is monotonically associated with the MEAN forward "
            f"21-trading-day NDX log return (gross, costless conditional means; NOT a P&L, NOT "
            f"next-session timing, NO tradable rule).",
        "D2_COTFLOW":
            f"The D2 headline statistic is computed over {len(d2)} weekly COT-knowability observations "
            f"({d2['obs_date'].min().date()} -> {d2['obs_date'].max().date()}, market '{cot_market}'); "
            f"the event it measures is whether the QUINTILE of the 4-report change in leveraged-fund "
            f"net position / open interest is monotonically associated with the MEAN forward "
            f"21-trading-day NDX log return measured from the first close at which the report was "
            f"public (gross, costless conditional means; NOT a P&L).",
        "D3_PATHCONT":
            f"The D3 headline statistic is computed over {len(d3)} weekly Friday-close observations "
            f"({d3['obs_date'].min().date()} -> {d3['obs_date'].max().date()}); the event it measures "
            f"is whether the CONTINUATION SPREAD (mean forward 21-trading-day NDX log return after a "
            f"positive trailing-21d sign minus after a negative sign) is LARGER in the top "
            f"efficiency-ratio tercile than in the bottom tercile -- an interaction contrast of "
            f"conditional means (gross, costless; NOT a P&L, NOT unconditional TSMOM).",
    }
    for fam in frames:
        emit(f"  [{fam}] {g1[fam]}")
    if d1_dropped:
        emit(f"  [D1 note] {d1_dropped} Friday observations dropped (verified contiguous "
             f"2012-11-30..2013-05-17): at the archive/modern file boundary the certified store has "
             f"only ONE live contract per session 2012-11-26..2012-12-19, zero rows 2012-12-20..31, "
             f"and settle=0 across the whole curve for 95 sessions 2013-01-02..2013-05-17. A missing "
             f"or bad front settle NEVER promotes the second contract; the Friday is dropped instead.")

    # ---------------- G6 knowability audit (printed BEFORE outcomes)
    emit("")
    emit("G6 KNOWABILITY AUDIT " + "-" * 79)
    emit("criterion coded for EVERY observation: knowable-timestamp(all signal inputs) <= forward-window")
    emit("start timestamp. D1/D3: inputs dated <= obs close t; fwd starts AT close t (the preregistered")
    emit("close-to-close population; margin 0 = same 16:00 ET mark). D2: release Friday 15:30 ET must")
    emit("STRICTLY precede the next-Monday 16:00 ET close (asserted per-row in the builder).")
    arng = np.random.default_rng(AUDIT_SEED)
    for fam, df in frames.items():
        idx = np.sort(arng.choice(len(df), size=10, replace=False))
        emit(f"  [{fam}] 10 random observation points of {len(df)}:")
        for i in idx:
            r = df.iloc[i]
            if fam == "D1_VXSLOPE":
                know = r["sig_date"] + pd.Timedelta(hours=16)
                start = r["obs_date"] + pd.Timedelta(hours=16)
                ins = f"VX settle {r['sig_date'].date()} (front exp {r['front_exp'].date()})"
            elif fam == "D2_COTFLOW":
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
                 f"fwd_start={start} (close)  fwd_end_21={pd.Timestamp(r['end_21']).date()}  "
                 f"margin={margin_h:.1f}h  {'OK' if ok else 'VIOLATION'}")
            assert ok, "G6 VIOLATION -- run invalid"
        if fam == "D1_VXSLOPE":
            assert (df["sig_date"] <= df["obs_date"]).all(), "G6 VIOLATION: D1 signal after obs"
        if fam == "D2_COTFLOW":
            assert ((df["obs_date"] + pd.Timedelta(hours=16)) > df["release"]).all(), \
                "G6 VIOLATION: D2 release after fwd start"
    g6_pass = True
    emit("  G6 all-row asserts held for all three sub-families -> PASS")

    fh.flush()
    os.fsync(fh.fileno())
    emit("")
    emit("#### everything ABOVE this line was written to gate_table.txt BEFORE any outcome was computed ####")

    # =========================================================== outcomes
    fam_cfg = {
        "D1_VXSLOPE": dict(label_col="bucket", k=5, primary=stat_wspearman, g4=stat_spread,
                           names=[f"Q{i+1}" for i in range(5)]),
        "D2_COTFLOW": dict(label_col="bucket", k=5, primary=stat_wspearman, g4=stat_spread,
                           names=[f"Q{i+1}" for i in range(5)]),
        "D3_PATHCONT": dict(label_col="cell", k=6, primary=stat_d3_contrast, g4=stat_d3_contrast,
                            names=["neg/ER_bot", "neg/ER_mid", "neg/ER_top",
                                   "pos/ER_bot", "pos/ER_mid", "pos/ER_top"]),
    }

    all_bucket_rows, all_era_rows, verdicts = [], [], {}
    for fam, cfg in fam_cfg.items():
        df = frames[fam]
        st = family_stats(fam, df, cfg["label_col"], cfg["k"], cfg["primary"], cfg["g4"])
        all_bucket_rows += bucket_table_rows(fam, df, cfg["label_col"], cfg["k"], cfg["names"])

        # G3 eras (h=21; sign agreement with the full-window spread/contrast sign)
        full_g4 = st[H_PRIMARY]["obs_g4"]
        full_sign = int(np.sign(full_g4))
        eras = era_analysis(fam, df, cfg["label_col"], full_sign)
        all_era_rows += eras
        n_agree = sum(e["agrees_with_full"] for e in eras)
        g3_pass = n_agree >= G3_MIN_AGREE[fam]

        s21 = st[H_PRIMARY]
        g2_pass = s21["p_primary"] <= ALPHA
        g4_pass = s21["p_g4"] <= ALPHA
        nw_b, nw_t = nw_secondary(fam, df, H_PRIMARY)

        emit("")
        emit("=" * 100)
        emit(f"SUB-FAMILY {fam}   (n={st['n']}, primary horizon h={H_PRIMARY}; h=5/63 exploratory, "
             f"CANNOT generate a PASS)")
        emit("=" * 100)
        emit(f"{'GATE':<10}| {'SPEC':<58}| {'OBSERVED':<70}| PASS-FAIL")
        emit(f"{'G0':<10}| {'seal (see table above)':<58}| {'asserts held':<70}| PASS")
        emit(f"{'G1':<10}| {'semantic sentence printed':<58}| {'see G1 section above':<70}| PASS")
        pname = "weighted Spearman(bucket rank, bucket mean fwd21)" if fam != "D3_PATHCONT" \
            else "interaction contrast (topER sign-spread - botER sign-spread)"
        g2_spec = pname + " vs 401-shift null, p<=0.0167"
        g2_obs = ("stat={:+.6f}  p={:.4f}  (null sd={:.6f})"
                  .format(s21["obs_primary"], s21["p_primary"], s21["sd_null_primary"]))
        emit(f"{'G2':<10}| {g2_spec:<58}| {g2_obs:<70}| {'PASS' if g2_pass else 'FAIL'}")
        era_txt = ", ".join(e["era"] + ":" + ("+" if e["sign"] > 0 else ("-" if e["sign"] < 0 else "0"))
                            for e in eras)
        g3_spec = ("era sign agreement >= {} of {} (with full-window sign {})"
                   .format(G3_MIN_AGREE[fam], len(eras), "+" if full_sign > 0 else "-"))
        g3_obs = "{}/{} agree  [{}]".format(n_agree, len(eras), era_txt)
        emit(f"{'G3':<10}| {g3_spec:<58}| {g3_obs:<70}| {'PASS' if g3_pass else 'FAIL'}")
        g4name = "top-minus-bottom quintile spread vs null, p<=0.0167" if fam != "D3_PATHCONT" \
            else "contrast IS the spread (sign diff-in-diff), same null"
        g4_obs = ("spread={:+.6f}  p={:.4f}  (null sd={:.6f})"
                  .format(s21["obs_g4"], s21["p_g4"], s21["sd_null_g4"]))
        emit(f"{'G4':<10}| {g4name:<58}| {g4_obs:<70}| {'PASS' if g4_pass else 'FAIL'}")

        # G5 power -- MDE printed for every failed gate
        g5_lines, underpowered = [], False
        if not g2_pass:
            mde = MDE_FACTOR * s21["sd_null_primary"]
            up = mde > 3.0 * abs(s21["obs_primary"])
            underpowered |= up
            g5_lines.append(f"G2 failed: MDE@80%power={mde:.6f} vs |obs|={abs(s21['obs_primary']):.6f} "
                            f"(MDE/|obs|={mde/max(abs(s21['obs_primary']),1e-12):.2f}x) "
                            f"{'-> UNDERPOWERED_STILL' if up else '-> adequately powered FAIL'}")
        if not g4_pass:
            mde = MDE_FACTOR * s21["sd_null_g4"]
            up = mde > 3.0 * abs(s21["obs_g4"])
            underpowered |= up
            g5_lines.append(f"G4 failed: MDE@80%power={mde:.6f} vs |obs|={abs(s21['obs_g4']):.6f} "
                            f"(MDE/|obs|={mde/max(abs(s21['obs_g4']),1e-12):.2f}x) "
                            f"{'-> UNDERPOWERED_STILL' if up else '-> adequately powered FAIL'}")
        if not g3_pass:
            for e in eras:
                if e["n_obs"] > 0:
                    mde_era = MDE_FACTOR * s21["sd_null_g4"] * np.sqrt(st["n"] / e["n_obs"])
                    g5_lines.append(f"G3 failed: era {e['era']} spread={e['spread_or_contrast']:+.6f} "
                                    f"(n={e['n_obs']}), era-scaled MDE~{mde_era:.6f} "
                                    f"[approx: full null sd x sqrt(N/n_era)]")
        if g5_lines:
            for ln in g5_lines:
                emit(f"{'G5':<10}| {'MDE at 80% power for failed gate':<58}| {ln:<70}| INFO")
        else:
            emit(f"{'G5':<10}| {'MDE printed only for failed gates':<58}| {'no gate failed':<70}| N/A")
        emit(f"{'G6':<10}| {'knowability audit, any violation = run invalid':<58}| "
             f"{'printed above; all-row asserts held':<70}| {'PASS' if g6_pass else 'FAIL'}")

        # secondary NW t + exploratory horizons
        emit(f"SECONDARY (never the gate): Newey-West t (lag={H_PRIMARY}) of the h=21 "
             f"{'spread' if fam != 'D3_PATHCONT' else 'interaction coefficient'}: "
             f"est={nw_b:+.6f}, t={nw_t:+.2f}")
        for h in (5, 63):
            sh = st[h]
            emit(f"EXPLORATORY h={h} (cannot PASS): primary stat={sh['obs_primary']:+.6f} "
                 f"p={sh['p_primary']:.4f} | spread/contrast={sh['obs_g4']:+.6f} p={sh['p_g4']:.4f} "
                 f"(n={sh['n_h']}, shared offsets)")

        # verdict
        if g2_pass and g4_pass and g3_pass:
            verdict = "PASS"
        elif g2_pass and g4_pass and not g3_pass:
            verdict = "REGIME_LOCAL"
        elif underpowered:
            verdict = f"UNDERPOWERED_STILL -- {UNDERPOWERED_SENTENCE}"
        else:
            verdict = "FAIL-closed"
        verdicts[fam] = verdict
        emit(f"VERDICT {fam}: {verdict}")

    # ---------------- bucket means quick-view + files
    emit("")
    emit("=" * 100)
    emit("BUCKET / CELL MEANS (h=21, log fwd return; full tables in out/bucket_tables.csv)")
    bt = pd.DataFrame(all_bucket_rows)
    for fam in fam_cfg:
        sub = bt[(bt["sub_family"] == fam) & (bt["horizon"] == 21)]
        emit(f"  [{fam}] " + "  ".join(f"{r['cell']}:{r['mean_fwd_log']:+.5f}(n={r['n']},t={r['nw_t']:+.1f})"
                                       for _, r in sub.iterrows()))
    et = pd.DataFrame(all_era_rows)
    bt.to_csv(OUT / "bucket_tables.csv", index=False)
    et.to_csv(OUT / "era_tables.csv", index=False)

    # ---------------- alignment hand-check rows (one per sub-family, program-printed)
    emit("")
    emit("ALIGNMENT HAND-CHECK ROWS (for REPORT.md verification)")
    for fam, df in frames.items():
        r = df.iloc[len(df) // 2]
        i0 = pd.DatetimeIndex(ndx["date"]).searchsorted(r["obs_date"])
        c0 = float(ndx["close"].iloc[i0]); c21 = float(ndx["close"].iloc[i0 + 21])
        if fam == "D1_VXSLOPE":
            emit(f"  [{fam}] sig_date={r['sig_date'].date()} front={r['front']}/exp {r['front_exp'].date()} "
                 f"second={r['second']}/exp {r['second_exp'].date()} slope={r['signal']:+.6f} | "
                 f"obs(fwd start)={r['obs_date'].date()} close={c0} | fwd_end_21={pd.Timestamp(r['end_21']).date()} "
                 f"close={c21} | fwd_21=ln({c21}/{c0})={np.log(c21/c0):+.6f} (stored {r['fwd_21']:+.6f})")
        elif fam == "D2_COTFLOW":
            emit(f"  [{fam}] as_of={r['as_of'].date()} release={r['release']} net/OI={r['net_oi']:+.6f} "
                 f"signal(d4)={r['signal']:+.6f} | obs(fwd start)={r['obs_date'].date()} close={c0} | "
                 f"fwd_end_21={pd.Timestamp(r['end_21']).date()} close={c21} | "
                 f"fwd_21=ln({c21}/{c0})={np.log(c21/c0):+.6f} (stored {r['fwd_21']:+.6f})")
        else:
            emit(f"  [{fam}] sig_date={r['sig_date'].date()} win={r['win_start'].date()}..{r['sig_date'].date()} "
                 f"r21={r['r21']:+.6f} sign={r['sign']} ER={r['er']:.4f} ter={r['ter']} | "
                 f"obs(fwd start)={r['obs_date'].date()} close={c0} | fwd_end_21={pd.Timestamp(r['end_21']).date()} "
                 f"close={c21} | fwd_21=ln({c21}/{c0})={np.log(c21/c0):+.6f} (stored {r['fwd_21']:+.6f})")

    emit("")
    emit("FINAL VERDICTS " + "-" * 85)
    for fam, v in verdicts.items():
        emit(f"  {fam}: {v}")
    emit("Decision rule (spec): PASS -> Stage-5/6 preregistered minimal-rule spec (NEW run). FAIL ->")
    emit("closed at the stated scope. REGIME_LOCAL -> recorded, revival needs a mechanism for the era")
    emit("break. No headline here is quotable as edge: conditional means, gross, costless,")
    emit("DISCOVERY-CONSUMED the moment they printed.")

    fh.close()
    for fn in ("gate_table.txt", "bucket_tables.csv", "era_tables.csv"):
        assert (OUT / fn).stat().st_size > 0, f"output {fn} empty"
    print(f"\n[done] outputs written under {OUT}")


if __name__ == "__main__":
    main()
