"""GC (COMEX gold) DAILY extraction + daily autopsy -- metals pod Wave-1 deliverable.

STEP 1  extract per-contract day .ncd (PURE PYTHON, no NT8 recompile) -> causal-roll continuous
        DAILY series in TWO representations (ratio/returns-stitched for % work; point-difference
        back-adjusted for level/range work). Writes out/gc_daily.parquet.
STEP 2  daily autopsy (NQ_RESEARCH_PLAYBOOK.md sec 9 protocol at DAILY resolution): RETURNS,
        DISTRIBUTION, DEPENDENCE, PATH, STRUCTURE + correlation to NQ.

HARD GUARDS obeyed:
  * .ncd read only through research/multi_market/src/ncd_day.py (VOLUME00's 48-byte reader). No
    Custom.dll recompile, no CrossTrade, no order/strategy action.
  * SEAL: every session >= 2026-08-01 hard-dropped at load; boundary printed + asserted.
  * writes ONLY inside runs/DAILY_GC_EXTRACT_AUTOPSY_20260906/.

DESCRIPTIVE ONLY -- no ledger trial, DISCOVERY_CONSUMED. No P&L object, no promotion.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(RUN))
MM = os.path.join(ROOT, "research", "multi_market", "src")
sys.path.insert(0, MM)
import ncd_day as N            # noqa: E402
import roll as R              # noqa: E402
from contract_truth import load_root, validity, usable_start  # noqa: E402

OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
SEAL = pd.Timestamp("2026-08-01")
Y0, Y1 = 2009, 2027
CLEAN_GAP_MAX = 5          # calendar-day gap above which a "daily" return spans a coverage hole
RNG = np.random.default_rng(20260906)

_fh = open(os.path.join(OUT, "autopsy_log.txt"), "w", encoding="utf-8")


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


def sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def tstat(x):
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    if len(x) < 3:
        return np.nan, np.nan, len(x)
    return float(x.mean()), float(x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))), len(x)


# =============================================================== STEP 1  EXTRACT
def build_returns(panel, held):
    """Self-financing point return (identical to roll.economic_returns) PLUS the capital base
    old_close_prev so a basis-free PERCENT return can be formed. Never differences two contracts."""
    o = panel.pivot_table(index="date", columns="contract_id", values="open").sort_index()
    c = panel.pivot_table(index="date", columns="contract_id", values="close").sort_index()
    h = panel.pivot_table(index="date", columns="contract_id", values="high").sort_index()
    lo = panel.pivot_table(index="date", columns="contract_id", values="low").sort_index()
    vol = panel.pivot_table(index="date", columns="contract_id", values="volume").sort_index()
    dates = held.index
    rows = []
    for i in range(1, len(dates)):
        d, dp = dates[i], dates[i - 1]
        tgt, old = held.get(d), held.get(dp)
        if not isinstance(tgt, str) or not isinstance(old, str):
            continue
        try:
            old_c_prev, old_o = c.at[dp, old], o.at[d, old]
            tgt_o, tgt_c = o.at[d, tgt], c.at[d, tgt]
            tgt_h, tgt_l, tgt_v = h.at[d, tgt], lo.at[d, tgt], vol.at[d, tgt]
        except KeyError:
            continue
        if any(pd.isna(x) for x in (old_c_prev, old_o, tgt_o, tgt_c)):
            continue
        overnight = old_o - old_c_prev
        intraday = tgt_c - tgt_o
        rows.append(dict(date=d, held_contract=tgt, old_contract=old,
                         open=tgt_o, high=tgt_h, low=tgt_l, close=tgt_c, volume=int(tgt_v),
                         old_close_prev=old_c_prev,
                         overnight_pts=overnight, intraday_pts=intraday,
                         ret_points=overnight + intraday, rolled=int(old != tgt)))
    df = pd.DataFrame(rows)
    df["ret_pct"] = df["ret_points"] / df["old_close_prev"]
    df["overnight_pct"] = df["overnight_pts"] / df["old_close_prev"]
    df["intraday_pct"] = df["intraday_pts"] / df["old_close_prev"]
    df["cal_gap_days"] = df["date"].diff().dt.days
    df["clean_daily"] = df["cal_gap_days"].fillna(1) <= CLEAN_GAP_MAX
    return df


def extract(root):
    d = load_root(root, Y0, Y1)
    pre_rows, pre_max = len(d), d["date"].max()
    d = d[d["date"] < SEAL].reset_index(drop=True)
    assert d["date"].max() < SEAL, "SEAL VIOLATION"
    led = R.build_roll_ledger(d, root)
    held = R.designated_contract(d, led)
    df = build_returns(d, held)
    # identity gate: my ret_points must equal the certified roll.economic_returns exactly
    er = R.economic_returns(d, held)
    m = df.merge(er[["date", "ret_points"]], on="date", suffixes=("", "_oracle"))
    maxerr = float(np.max(np.abs(m["ret_points"] - m["ret_points_oracle"])))
    assert maxerr < 1e-9, f"identity gate FAILED: {maxerr}"
    return d, led, df, pre_rows, pre_max, maxerr


def main():
    P("=" * 100)
    P("=== GC (COMEX GOLD) DAILY EXTRACT + AUTOPSY  --  metals pod Wave-1 (DESCRIPTIVE, $0)")
    P("=" * 100)
    R.test_no_roll_telescopes(verbose=False)
    R.test_basis_invariance(verbose=False)
    R.test_roll_causality(verbose=False)
    P("    roll.py causal-roll unit tests: telescoping / basis-invariance / causality  ALL PASS")

    # ---------------- STEP 1
    P("")
    P("--- STEP 1  EXTRACT")
    d, led, gc, pre_rows, pre_max, idgate = extract("GC")
    P(f"    reader           research/multi_market/src/ncd_day.py::read_ncd_day (48-byte DAY record)")
    P(f"    raw panel        {pre_rows:,} contract-days, max date {pre_max.date()} (pre-seal)")
    P(f"    SEAL applied     dropped rows with date >= {SEAL.date()}")
    P(f"    retained max     {d['date'].max().date()}   assert < {SEAL.date()}: "
      f"{'PASS' if d['date'].max() < SEAL else '*** FAIL ***'}")
    P(f"    panel after seal {len(d):,} contract-days, {d['contract_id'].nunique()} contracts, "
      f"{d['date'].min().date()} -> {d['date'].max().date()}")
    v = validity(d)
    P(f"    validity         ohlc_bad={v['ohlc_bad']} vol_neg={v['vol_neg']} "
      f"vol_zero={v['vol_zero']} dup_contract_dates={v['dup_contract_dates']}")
    us, ue, ndays, rf = usable_start(d)
    P(f"    usable_start     {us.date()} (>=1 live contract, <=3bd outage) -> {ue.date()}, "
      f"{ndays} clean-contiguous days; roll_overlap_frac {rf:.3f}")
    P(f"    ROLL METHOD      CAUSAL volume-crossover (uses t-1 volume ONLY) + {R.PRE_EXPIRY_BUFFER_DAYS}"
      f"-day pre-expiry safety override (contract mechanics, no future data). One-way, never backward.")
    P(f"    roll ledger      {len(led)} rows: "
      f"{int((led.reason=='VOLUME_CROSSOVER').sum())} volume-crossover, "
      f"{int((led.reason=='PRE_EXPIRY_OVERRIDE').sum())} pre-expiry, "
      f"{int((led.reason=='INITIALISE').sum())} init")
    b = led.dropna(subset=["info_cutoff"])
    causal_ok = bool((pd.to_datetime(b["info_cutoff"]) < pd.to_datetime(b["decision_date"])).all())
    P(f"    causality assert every info_cutoff < decision_date on {len(b)} rolls: "
      f"{'PASS' if causal_ok else '*** FAIL ***'}")
    assert causal_ok
    P(f"    identity gate    my ret_points == roll.economic_returns (max err {idgate:.2e}): PASS")
    P(f"    return-days      {len(gc):,}  {gc['date'].min().date()} -> {gc['date'].max().date()}  "
      f"({int((~gc['clean_daily']).sum())} span a coverage gap >{CLEAN_GAP_MAX}cal-d -> clean_daily=False)")

    # ---- TWO REPRESENTATIONS ------------------------------------------------------------------
    # (a) RATIO / returns-stitched: correct % returns across eras.  close_radj[last]=true close.
    # (b) POINT-DIFFERENCE back-adjusted: correct levels & RANGES.   close_padj[last]=true close.
    r = gc["ret_pct"].fillna(0.0).values
    growth = np.cumprod(1.0 + r)
    last_true_close = float(gc["close"].iloc[-1])
    gc["close_radj"] = last_true_close * growth / growth[-1]
    dp = gc["ret_points"].fillna(0.0).values
    cum = np.cumsum(dp)
    gc["close_padj"] = last_true_close + (cum - cum[-1])
    gc["close_true"] = gc["close"]
    # point-diff back-adjust preserves ranges exactly; carry adjusted O/H/L for level/range work
    adj = gc["close_padj"] - gc["close_true"]
    gc["open_padj"] = gc["open"] + adj
    gc["high_padj"] = gc["high"] + adj
    gc["low_padj"] = gc["low"] + adj

    schema_cols = ["date", "open", "high", "low", "close", "volume",       # RAW held-contract (true)
                   "held_contract", "old_contract", "rolled",
                   "ret_points", "ret_pct", "overnight_pts", "intraday_pts",
                   "overnight_pct", "intraday_pct", "old_close_prev",
                   "close_true", "close_padj", "close_radj",               # continuous representations
                   "open_padj", "high_padj", "low_padj",
                   "cal_gap_days", "clean_daily"]
    gc_out = gc[schema_cols].copy()
    pq = os.path.join(OUT, "gc_daily.parquet")
    gc_out.to_parquet(pq, index=False)
    P(f"    WROTE            {pq}")
    P(f"    representations  (a) close_radj = ratio/returns-stitched  [use for %-return / cross-era]")
    P(f"                     (b) close_padj/open_padj/high_padj/low_padj = point-diff back-adj "
      f"[use for LEVEL / RANGE]; open/high/low/close = RAW true held-contract prices")

    # ---------------- STEP 2  AUTOPSY  (ret_pct, clean_daily only for return stats)
    a = gc[gc["clean_daily"]].copy()
    rp = a["ret_pct"].values
    P("")
    P("=" * 100)
    P(f"--- STEP 2  DAILY AUTOPSY   (n={len(a):,} clean daily returns, ret_pct, "
      f"{a['date'].min().date()} -> {a['date'].max().date()})")
    P("=" * 100)

    tables = {}

    # ---- (RETURNS) ----------------------------------------------------------------------------
    P("")
    P("[RETURNS]")
    m, t, n = tstat(rp)
    ann = m * 252
    P(f"    unconditional daily ret_pct: mean {m*1e4:+.3f} bps  t {t:+.2f}  n {n:,}  "
      f"=> ~{ann*100:+.2f}%/yr drift, ann.vol {a['ret_pct'].std()*np.sqrt(252)*100:.1f}%")
    # day of week
    a["dow"] = a["date"].dt.dayofweek
    dow_rows = []
    for k, lab in [(0, "Mon"), (1, "Tue"), (2, "Wed"), (3, "Thu"), (4, "Fri")]:
        mm, tt, nn = tstat(a.loc[a["dow"] == k, "ret_pct"])
        dow_rows.append(dict(dow=lab, mean_bps=mm*1e4, t=tt, n=nn))
    dow = pd.DataFrame(dow_rows); tables["dow"] = dow
    P("    day-of-week mean ret (bps) [t]:  " +
      "  ".join(f"{x.dow} {x.mean_bps:+.1f}[{x.t:+.1f}]" for x in dow.itertuples()))
    # month seasonality
    a["month"] = a["date"].dt.month
    mo_rows = []
    for k in range(1, 13):
        mm, tt, nn = tstat(a.loc[a["month"] == k, "ret_pct"])
        mo_rows.append(dict(month=k, mean_bps=mm*1e4, t=tt, n=nn))
    mo = pd.DataFrame(mo_rows); tables["month"] = mo
    P("    month-of-year mean ret (bps) [t]:")
    P("      " + "  ".join(f"{x.month:02d}:{x.mean_bps:+.1f}[{x.t:+.1f}]" for x in mo.itertuples()))
    # conditional on prior-day sign
    a["prev"] = a["ret_pct"].shift(1)
    a["prev_gap_ok"] = a["cal_gap_days"].shift(-0)  # already clean subset
    up = a[a["prev"] > 0]["ret_pct"]; dn = a[a["prev"] < 0]["ret_pct"]
    mu, tu, nu = tstat(up); md, td, nd = tstat(dn)
    P(f"    prior-day UP  -> next mean {mu*1e4:+.2f} bps [t {tu:+.2f}] n {nu:,}")
    P(f"    prior-day DOWN-> next mean {md*1e4:+.2f} bps [t {td:+.2f}] n {nd:,}  "
      f"(diff {(mu-md)*1e4:+.2f} bps; >0 => momentum, <0 => reversal)")
    # conditional on prior-day magnitude quintile
    a["prev_absq"] = pd.qcut(a["prev"].abs(), 5, labels=False, duplicates="drop")
    magrows = []
    for q in range(5):
        sub = a[a["prev_absq"] == q]
        mm, tt, nn = tstat(sub["ret_pct"])
        mabs, _, _ = tstat(sub["ret_pct"].abs())
        magrows.append(dict(prev_absmag_q=q, next_mean_bps=mm*1e4, next_t=tt,
                            next_absmean_bps=mabs*1e4, n=nn))
    mag = pd.DataFrame(magrows); tables["prev_magnitude"] = mag
    P("    prior-day |ret| quintile -> next mean / next |ret| (bps):")
    for x in mag.itertuples():
        P(f"      q{x.prev_absmag_q} (small->large): next {x.next_mean_bps:+.2f}[t{x.next_t:+.1f}]  "
          f"next|ret| {x.next_absmean_bps:.1f}  n {x.n:,}")

    # ---- (DISTRIBUTION) -----------------------------------------------------------------------
    P("")
    P("[DISTRIBUTION]")
    s = pd.Series(rp)
    sk = float(s.skew()); ku = float(s.kurt())  # excess kurtosis
    q = np.percentile(rp, [0.1, 1, 5, 25, 50, 75, 95, 99, 99.9])
    P(f"    mean {s.mean()*1e4:+.2f}bps  sd {s.std()*100:.3f}%  skew {sk:+.3f}  exkurt {ku:+.2f}  "
      f"min {rp.min()*100:.2f}%  max {rp.max()*100:.2f}%")
    P(f"    pctiles %: p0.1 {q[0]*100:.2f}  p1 {q[1]*100:.2f}  p5 {q[2]*100:.2f}  p25 {q[3]*100:.2f}"
      f"  p50 {q[4]*100:.2f}  p75 {q[5]*100:.2f}  p95 {q[6]*100:.2f}  p99 {q[7]*100:.2f}  "
      f"p99.9 {q[8]*100:.2f}")
    z = (rp - rp.mean()) / rp.std()
    tailrows = []
    from math import erfc, sqrt
    for k in (2, 3, 4, 5):
        emp = float(np.mean(np.abs(z) > k))
        norm = erfc(k / sqrt(2))
        tailrows.append(dict(k=k, emp_rate=emp, normal_rate=norm,
                             emp_per_yr=emp*252, ratio=(emp/norm if norm > 0 else np.nan)))
    tail = pd.DataFrame(tailrows); tables["tails"] = tail
    P("    tail |z|>k:  " + "  ".join(
        f"k{x.k}: {x.emp_rate*100:.3f}% ({x.emp_per_yr:.1f}/yr) vs N {x.normal_rate*100:.3f}% "
        f"[{x.ratio:.1f}x]" for x in tail.itertuples()))
    # gap (overnight) vs intraday variance decomposition
    ov = a["overnight_pct"].values; ind = a["intraday_pct"].values
    P(f"    overnight(gap) ret: mean {np.nanmean(ov)*1e4:+.2f}bps sd {np.nanstd(ov)*100:.3f}%  |  "
      f"intraday ret: mean {np.nanmean(ind)*1e4:+.2f}bps sd {np.nanstd(ind)*100:.3f}%")
    vov, vin = np.nanvar(ov), np.nanvar(ind)
    P(f"    variance share: overnight {vov/(vov+vin)*100:.1f}%  intraday {vin/(vov+vin)*100:.1f}%  "
      f"corr(on,intra) {np.corrcoef(ov[np.isfinite(ov)&np.isfinite(ind)], ind[np.isfinite(ov)&np.isfinite(ind)])[0,1]:+.3f}")
    # daily true range as % of close
    a["tr_pct"] = (a["high"] - a["low"]) / a["close"]
    P(f"    daily range (high-low)/close: median {a['tr_pct'].median()*100:.3f}%  "
      f"mean {a['tr_pct'].mean()*100:.3f}%  p95 {a['tr_pct'].quantile(.95)*100:.3f}%")

    # ---- (DEPENDENCE) -------------------------------------------------------------------------
    P("")
    P("[DEPENDENCE]")

    def autocorr(x, lags):
        x = np.asarray(x, float); x = x - x.mean(); n = len(x)
        d0 = np.sum(x * x)
        return [float(np.sum(x[l:] * x[:n-l]) / d0) for l in lags]

    lags = [1, 2, 3, 4, 5, 10, 20]
    ac = autocorr(rp, lags)
    P("    return autocorr:  " + "  ".join(f"L{l}:{v:+.3f}" for l, v in zip(lags, ac)))
    ac_abs = autocorr(np.abs(rp), lags)
    ac_sq = autocorr(rp**2, lags)
    P("    |ret| autocorr :  " + "  ".join(f"L{l}:{v:+.3f}" for l, v in zip(lags, ac_abs)))
    P("    ret^2 autocorr :  " + "  ".join(f"L{l}:{v:+.3f}" for l, v in zip(lags, ac_sq)))
    # sign persistence
    sgn = np.sign(rp)
    same = float(np.mean(sgn[1:] == sgn[:-1]))
    p_up = float(np.mean(rp > 0))
    exp_same = p_up**2 + (1 - p_up)**2
    P(f"    sign persistence P(sign_t==sign_t-1) {same*100:.2f}%  vs iid {exp_same*100:.2f}%  "
      f"(P(up)={p_up*100:.2f}%)")
    # variance ratio (Lo-MacKinlay), overlapping
    def var_ratio(x, k):
        x = np.asarray(x, float); n = len(x)
        mu = x.mean()
        va1 = np.sum((x - mu)**2) / n
        agg = np.convolve(x, np.ones(k), "valid")
        vak = np.sum((agg - k*mu)**2) / (n - k + 1)
        return float(vak / (k * va1))
    vr_rows = []
    for k in (2, 5, 10, 20):
        vr_rows.append(dict(horizon=k, VR=var_ratio(rp, k)))
    vr = pd.DataFrame(vr_rows); tables["variance_ratio"] = vr
    P("    variance ratio VR(k) [>1 trend/persistence, <1 reversal]:  " +
      "  ".join(f"k{x.horizon}:{x.VR:.3f}" for x in vr.itertuples()))
    # multi-day return autocorr (non-overlap) -> trend vs reversal at swing horizons
    P("    multi-day (non-overlapping) return autocorr L1:")
    md_rows = []
    for k in (2, 3, 5, 10, 20):
        blk = pd.Series(rp).groupby(np.arange(len(rp)) // k).sum().values
        if len(blk) > 5:
            a1 = autocorr(blk, [1])[0]
            md_rows.append(dict(block_days=k, ac1=a1, n_blocks=len(blk)))
    mdt = pd.DataFrame(md_rows); tables["multiday_ac"] = mdt
    P("      " + "  ".join(f"{x.block_days}d:{x.ac1:+.3f}(n{int(x.n_blocks)})" for x in mdt.itertuples()))

    # circular-shift null context for the two load-bearing dependence facts (descriptive only)
    def shift_null(stat_fn, x, nshift=1000):
        obs = stat_fn(x)
        n = len(x); draws = np.empty(nshift)
        for i in range(nshift):
            s = RNG.integers(1, n)
            draws[i] = stat_fn(np.roll(x, s))
        pct = float(np.mean(draws <= obs))
        return obs, pct, float(draws.mean()), float(draws.std())
    o_ac1, pct_ac1, _, sd_ac1 = shift_null(lambda x: autocorr(x, [1])[0], rp)
    o_vr5, pct_vr5, _, sd_vr5 = shift_null(lambda x: var_ratio(x, 5), rp)
    P(f"    circular-shift null (1000): AC(L1) obs {o_ac1:+.3f} pctile {pct_ac1*100:.1f} "
      f"(null sd {sd_ac1:.3f}) | VR(5) obs {o_vr5:.3f} pctile {pct_vr5*100:.1f} (null sd {sd_vr5:.3f})")

    # ---- (PATH) -------------------------------------------------------------------------------
    P("")
    P("[PATH]")
    # Kaufman efficiency ratio on close_radj over n-day windows
    cl = gc["close_radj"].values
    er_rows = []
    for n_ in (5, 10, 20, 40):
        num = np.abs(cl[n_:] - cl[:-n_])
        den = np.array([np.sum(np.abs(np.diff(cl[i:i+n_+1]))) for i in range(len(cl)-n_)])
        eff = num / np.where(den == 0, np.nan, den)
        er_rows.append(dict(window=n_, mean_ER=float(np.nanmean(eff)),
                            median_ER=float(np.nanmedian(eff))))
    ert = pd.DataFrame(er_rows); tables["efficiency_ratio"] = ert
    P("    Kaufman efficiency ratio (net move / gross path) [higher => trendier]:")
    P("      " + "  ".join(f"{x.window}d mean {x.mean_ER:.3f} med {x.median_ER:.3f}"
                           for x in ert.itertuples()))
    # trend maturation: after m consecutive same-sign days, next-day mean
    P("    trend maturation -- next-day mean ret after m consecutive same-sign days:")
    sgn_s = pd.Series(np.sign(rp))
    runlen = np.zeros(len(rp), dtype=int)
    for i in range(1, len(rp)):
        runlen[i] = runlen[i-1] + 1 if sgn_s[i] == sgn_s[i-1] and sgn_s[i] != 0 else 1
    mat_rows = []
    for m_ in (1, 2, 3, 4, 5):
        idx = np.where(runlen[:-1] >= m_)[0] + 1
        if len(idx) > 10:
            nxt = rp[idx]
            dir_prev = sgn_s.values[idx-1]
            cont = nxt * dir_prev            # >0 => continued in the run's direction
            mm, tt, nn = tstat(cont)
            mat_rows.append(dict(run_ge=m_, next_in_dir_bps=mm*1e4, t=tt, n=nn))
    mat = pd.DataFrame(mat_rows); tables["trend_maturation"] = mat
    for x in mat.itertuples():
        P(f"      run>={x.run_ge}d: next-day-in-run-direction {x.next_in_dir_bps:+.2f} bps "
          f"[t {x.t:+.1f}] n {x.n:,}")

    # ---- (STRUCTURE) + NQ correlation ---------------------------------------------------------
    P("")
    P("[STRUCTURE / CROSS-ASSET]")
    # realized-vol regime persistence: 21d vol autocorr already shown via ret^2; add regime split
    a["rv21"] = a["ret_pct"].rolling(21).std()
    a["rv21_prev"] = a["rv21"].shift(1)
    hi = a[a["rv21_prev"] > a["rv21_prev"].median()]["ret_pct"]
    loo = a[a["rv21_prev"] <= a["rv21_prev"].median()]["ret_pct"]
    P(f"    vol-regime: next |ret| in HIGH-rv21 {hi.abs().mean()*1e4:.1f}bps vs LOW-rv21 "
      f"{loo.abs().mean()*1e4:.1f}bps (vol clustering)")

    # NQ daily returns from the SAME per-contract day store, SAME causal roll -> ret_pct
    dnq, lednq, nq, _, _, idnq = extract("NQ")
    P(f"    NQ built identically: {len(nq):,} return-days {nq['date'].min().date()}->"
      f"{nq['date'].max().date()} (identity gate err {idnq:.0e})")
    j = a[["date", "ret_pct"]].merge(
        nq[nq["clean_daily"]][["date", "ret_pct"]], on="date", suffixes=("_gc", "_nq"))
    rho = float(j["ret_pct_gc"].corr(j["ret_pct_nq"]))
    rho_s = float(j["ret_pct_gc"].corr(j["ret_pct_nq"], method="spearman"))
    P(f"    corr(GC, NQ) daily ret on {len(j):,} shared dates: Pearson {rho:+.3f}  Spearman {rho_s:+.3f}")
    yr_rows = []
    for y, g in j.groupby(j["date"].dt.year):
        if len(g) > 30:
            yr_rows.append(dict(year=int(y), rho=float(g["ret_pct_gc"].corr(g["ret_pct_nq"])), n=len(g)))
    yc = pd.DataFrame(yr_rows); tables["nq_corr_by_year"] = yc
    P("    per-year rho(GC,NQ): " + "  ".join(f"{x.year}:{x.rho:+.2f}" for x in yc.itertuples()))
    P(f"    rho range {yc['rho'].min():+.2f}..{yc['rho'].max():+.2f}, mean {yc['rho'].mean():+.3f} "
      f"-- LOW/near-zero equity correlation is the portfolio prize")

    # ---- write tables + manifest data ---------------------------------------------------------
    for name, tb in tables.items():
        tb.to_csv(os.path.join(OUT, f"autopsy_{name}.csv"), index=False)
    P("")
    P(f"    wrote {len(tables)} autopsy tables to out/autopsy_*.csv")

    manifest = dict(
        rows=int(len(gc_out)), span=[str(gc_out["date"].min().date()), str(gc_out["date"].max().date())],
        contracts=int(d["contract_id"].nunique()),
        roll_method="causal volume-crossover (t-1 volume only) + 5-day pre-expiry override; one-way",
        roll_ledger=dict(volume=int((led.reason == "VOLUME_CROSSOVER").sum()),
                         pre_expiry=int((led.reason == "PRE_EXPIRY_OVERRIDE").sum()),
                         init=int((led.reason == "INITIALISE").sum())),
        seal=str(SEAL.date()), retained_max=str(d["date"].max().date()),
        seal_assert_pass=bool(d["date"].max() < SEAL),
        clean_daily_returns=int(a.shape[0]), gap_spanning_dropped=int((~gc["clean_daily"]).sum()),
        parquet_sha256=sha256_file(pq),
        rho_nq_pearson=rho, rho_nq_spearman=rho_s, rho_nq_shared_dates=int(len(j)),
        identity_gate_maxerr=idgate,
        point_value=N.PV["GC"], tick_size=0.1,
        sample_head=gc_out.head(3).to_dict("records"),
        sample_tail=gc_out.tail(3).to_dict("records"),
    )
    json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8"),
              indent=2, default=str)
    P(f"    parquet sha256   {manifest['parquet_sha256']}")
    P("")
    P("=" * 100)
    P("=== DONE. DESCRIPTIVE ONLY. No P&L object, no ledger trial, no promotion. DISCOVERY_CONSUMED.")
    P("=" * 100)
    _fh.close()


if __name__ == "__main__":
    main()
