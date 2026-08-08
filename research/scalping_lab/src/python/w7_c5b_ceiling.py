"""W7-1 — C5b augmented predictability ceiling (THE decisive measurement).
Spec: research/scalping_lab/specs/W7_rt2_discharge.md section W7-1 (frozen @ 1d76c14).

Protocol: re-run the W5-C5 predictability-ceiling protocol EXACTLY (same 30s
quote-alive RTH decision clock, same 4 target-first labels (24,8)/(32,10) x
long/short with cap 600s and conservative same-second-both-crossed -> adverse,
same chronological session-grouped expanding 5 folds built from the same
37-session NQ list, same 2 models [L2 logistic w/ StandardScaler inside folds;
HistGradientBoostingClassifier(max_depth=3, early_stopping=True)], both leakage
guards asserted and printed) on TWO feature sets over the SAME rows:
  (base_nq27)      the original 27 NQ census features;
  (aug_nq27_new13) 27 NQ + 13 new features in 4 frozen blocks.

The 4 new blocks (frozen, spec W7-1), all TRAILING (may use second t, never t+1):
1. VWAP/value (grid1s last+vol; grid `last` is in POINTS, sechilo mid in TICKS
   -> VWAP converted to ticks via x4; grid is gap-free per-second with `last`
   never NaN, vol==0 seconds contribute 0):
     vwap_dist      = mid - RTH-anchored running VWAP (cum(last*vol)/cum(vol)
                      from the first second with tod >= 09:30:00, inclusive of
                      second t), ticks;
     vwap_slope60   = RTH-VWAP(t) - RTH-VWAP(t-60s), ticks/min (NaN in the
                      first 60s of RTH -> the 09:30:00/09:30:30 clock rows drop
                      under the same-sample rule);
     vwap_dist_full = mid - full-session VWAP (anchored at the 18:00 session
                      file start), ticks.
2. Prior-day levels & context (3-min CSV runs/AUDIT03_BARS/nq_3m_2022_2026.csv,
   back-adjusted space, END-stamped ET bars, HOLDOUT GUARD: rows >= 2026-06-01
   never read). Frozen offset rule: offset_s = (CSV 09:30 bar close on session
   date, x4 to ticks) - (sechilo mid_last at 09:30:00 same date); actual-space
   level = CSV-space level(ticks) - offset_s; offset constant within a session.
   Documented error: CSV close is a LAST price, sechilo is union-BBO MID ->
   measured median |last*4 - mid_last| = 1.0 tick (~1t Last-vs-mid error on all
   converted levels). RTH bars of a date = end-stamps in (09:30, 16:00]; the
   09:30-stamped bar covers 09:27-09:30 and is the open anchor, not an RTH bar.
     pdh_dist    = PDH_actual - mid (ticks; prior day's RTH high);
     pdl_dist    = mid - PDL_actual (ticks; prior day's RTH low);
     pclose_dist = mid - prior-RTH-close_actual (ticks; close of the last RTH
                   bar; on early-close days that is the 13:00 bar — documented);
     on_gap      = CSV 09:30 close(today) - prior RTH close, ticks, CSV-space
                   difference (offset-free by back-adjustment continuity),
                   session-constant;
     prior_day_ret_sign = sign(prior RTH close - prior 09:30 bar close),
                   session-constant in {-1,0,+1}.
3. Event flags (research/04_complementary_family/c01_announcement_calendar.csv:
   date,event,time_et; NFP/CPI 08:30, FOMC 14:00; calendar also filtered to
   < 2026-06-01 — provably immaterial since every session second is > 120 min
   from any June+ release, so clipped values are 999 either way):
     min_since_release = minutes since the most recent release (<= t), clipped:
                   value if <= 120 else 999;  08:30 releases enter via
                   minutes-SINCE at the 09:30 open (= 60.0);
     min_to_release = minutes to the next release (> t), same clipping.
   Never NaN -> this block causes no drops.
4. ES signed flow, H-D1 proper (raw ES trades substrate/raw/ES/es_<tag>.parquet,
   bip==0 rows = trades). Tick-rule sign on consecutive trade prices (up=+1,
   down=-1, unchanged=carry; leading trades before the first price change get 0).
   Per-second signed volume sv = sum(sign*volume); seconds with no ES trade but
   last trade <= 5s old -> sv = 0; if the last ES trade is > 5s old (or none
   yet) the second is ES-stale -> ALL ES-flow features NaN (W6 staleness rule).
     es_sflow10  = rolling 10s sum of sv;
     es_sflow60  = rolling 60s sum of sv;
     es_zsflow60 = es_sflow60 / rolling-600s std of 1s sv (min 300 obs) — the
                   W6 z-norm house pattern applied to signed flow.

Same-sample rule (frozen): rows with NaN in ANY new-block feature are dropped
from BOTH the baseline and augmented runs, so the comparison is paired on
identical rows. Counts and reasons reported per block and per session. (The
spec's anticipated 'first CSV session has no prior day' drop does NOT occur
here: the CSV starts 2022-01 and every one of the 36 modeled sessions
(2025-08-14..2026-05-20) has a prior RTH day and a 09:30 bar — verified.)

Baseline-matrix verification (frozen instruction): the rebuilt pre-drop matrix
must reproduce the committed artifacts/w5_c5/w5c5_dataset.parquet EXACTLY —
row count 27,299, per-session rows and neither-counts equal to
w5c5_dataset_summary.csv, all 27 features allclose and all 4 labels identical,
per-label base rates equal.

Frozen readout per (label, model): top-decile lift baseline vs augmented with
day-clustered CIs; delta (aug - base) with PAIRED session-bootstrap CI (same
session draws both runs); Brier skills; permutation importance of the new
blocks. Reproduction check vs original C5 metrics reported as a DIAGNOSTIC
(W6 tolerances: |dlift| <= 2pp, |dskill| <= 0.02, no pass_5pp flip).

Frozen interpretation (spec W7-1): any augmented cell with lift >= 5pp AND
CI_lo > 0 -> 'conversion spec required'; else 'augmented information set ALSO
insufficient'.

Seed 20260808; 1000 session-bootstrap reps; day-clustered CIs. LOCAL ONLY.
"""
import glob, os, sys
import numpy as np, pandas as pd
from numba import njit
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.ensemble import HistGradientBoostingClassifier

SEED = 20260808
NREPS = 1000
CAP = 600
CLOCK = 30
MINHIST = 300
NFOLDS = 5
ES_STALE = 5.0     # seconds; W6 staleness rule applied to ES trade recency
ZWIN = 600         # z-norm: rolling 600s std of 1s signed volume
ZMIN = 300         # z-norm: min 300 obs
DEV_END = "2026-06-01"   # HOLDOUT GUARD: never read CSV/calendar rows >= this
LABELS = [("long", 1, 24, 8), ("long", 1, 32, 10),
          ("short", -1, 24, 8), ("short", -1, 32, 10)]
C1_GAP = {("long", 24, 8): 0.0873, ("short", 24, 8): 0.0909,
          ("long", 32, 10): 0.0703, ("short", 32, 10): 0.0737}
NQ_FEATS = ["ret5", "ret10", "ret30", "ret60", "ret300", "rv60", "rv300",
            "tv60", "eff60", "range300", "dist_hi", "dist_lo", "secs_since_hi",
            "secs_since_lo", "trades10", "trades60", "vol10", "vol60", "upd10",
            "upd60", "sflow10", "sflow60", "act_accel", "nsflow60", "spread",
            "spread60", "tod"]
VWAP_FEATS = ["vwap_dist", "vwap_slope60", "vwap_dist_full"]
PRIOR_FEATS = ["pdh_dist", "pdl_dist", "pclose_dist", "on_gap",
               "prior_day_ret_sign"]
EVENT_FEATS = ["min_since_release", "min_to_release"]
ESF_FEATS = ["es_sflow10", "es_sflow60", "es_zsflow60"]
BLOCKS = [("vwap", VWAP_FEATS), ("prior_day", PRIOR_FEATS),
          ("event", EVENT_FEATS), ("es_flow", ESF_FEATS)]
NEW_FEATS = VWAP_FEATS + PRIOR_FEATS + EVENT_FEATS + ESF_FEATS
RUNS = [("base_nq27", NQ_FEATS), ("aug_nq27_new13", NQ_FEATS + NEW_FEATS)]
REPRO_TOL_LIFT = 0.02      # 2.0pp (diagnostic, W6 tolerances)
REPRO_TOL_SKILL = 0.02
C5_ROWS = 27299            # frozen verification target

SH = "research/scalping_lab/substrate/sechilo/NQ"
GR = "research/scalping_lab/substrate/grid1s/NQ"
ESRAW = "research/scalping_lab/substrate/raw/ES"
CSVP = "runs/AUDIT03_BARS/nq_3m_2022_2026.csv"
CALP = "research/04_complementary_family/c01_announcement_calendar.csv"
C5DS = "research/scalping_lab/artifacts/w5_c5/w5c5_dataset.parquet"
C5SUM = "research/scalping_lab/artifacts/w5_c5/w5c5_dataset_summary.csv"
C5M = "research/scalping_lab/artifacts/w5_c5/w5c5_metrics.csv"
OUTD = "research/scalping_lab/artifacts/w7_c5b"
os.makedirs(OUTD, exist_ok=True)

RTH_OPEN = 9 * 3600 + 1800    # 34200 = 09:30:00
RTH_CLOSE = 16 * 3600         # 57600 = 16:00:00


@njit(cache=True)
def label_scan(ml, hi, lo, starts, dirsign, A, B, cap):
    """Target-first label per start — VERBATIM from w5_c5_ceiling.py. Scan
    begins at t0+1. 1 = target first, 0 = adverse first (same-second
    both-crossed -> adverse, conservative), -1 = neither hit within cap."""
    out = np.full(starts.shape[0], -1, np.int8)
    n = ml.shape[0]
    for s in range(starts.shape[0]):
        t0 = starts[s]
        m0 = ml[t0]
        end = min(t0 + cap, n - 1)
        for i in range(t0 + 1, end + 1):
            up = hi[i] - m0
            dn = m0 - lo[i]
            if dirsign == 1:
                th = up >= A
                ah = dn >= B
            else:
                th = dn >= A
                ah = up >= B
            if th and ah:
                out[s] = 0
                break
            if ah:
                out[s] = 0
                break
            if th:
                out[s] = 1
                break
    return out


def load_csv_levels():
    """Per-session-date prior-day levels from the 3-min back-adjusted CSV, in
    TICK units (x4), CSV space. HOLDOUT GUARD: rows >= DEV_END dropped on load.
    Returns (levels dict keyed by pd.Timestamp date, n_csv_rows_kept)."""
    csv = pd.read_csv(CSVP, parse_dates=["time"])
    n0 = len(csv)
    csv = csv[csv["time"] < DEV_END].reset_index(drop=True)
    print(f"HOLDOUT GUARD: 3-min CSV rows {n0} -> {len(csv)} after dropping "
          f"time >= {DEV_END} (dev window {csv['time'].min()} .. "
          f"{csv['time'].max()})")
    csv["date"] = csv["time"].dt.normalize()
    csv["tod"] = (csv["time"] - csv["date"]).dt.total_seconds()
    b0930 = csv[csv["tod"] == RTH_OPEN].set_index("date")["close"] * 4.0
    rth = csv[(csv["tod"] > RTH_OPEN) & (csv["tod"] <= RTH_CLOSE)]
    agg = rth.groupby("date").agg(pdh=("high", "max"), pdl=("low", "min"))
    lastbar = rth.sort_values("time").groupby("date").last()
    rth_dates = sorted(agg.index)
    lev = {}
    for d in rth_dates:
        lev[d] = dict(
            own_0930_t=float(b0930[d]) if d in b0930.index else np.nan,
            rth_hi_t=float(agg.loc[d, "pdh"]) * 4.0,
            rth_lo_t=float(agg.loc[d, "pdl"]) * 4.0,
            rth_close_t=float(lastbar.loc[d, "close"]) * 4.0,
            rth_last_stamp=float(lastbar.loc[d, "tod"]))
    return lev, rth_dates


def prior_day_context(d, lev, rth_dates):
    """Levels for session date d taken from the prior RTH date. All ticks,
    CSV space. Returns None if no prior day / missing 09:30 anchors."""
    prior = [x for x in rth_dates if x < d]
    if not prior:
        return None
    p = prior[-1]
    own = lev.get(d, {}).get("own_0930_t", np.nan)
    if d not in lev or not np.isfinite(own):
        # session date itself has no 09:30 CSV bar -> no offset anchor
        return None
    pl = lev[p]
    if not np.isfinite(pl["own_0930_t"]):
        return None
    return dict(prior_date=p, own_0930_t=own,
                pdh_t=pl["rth_hi_t"], pdl_t=pl["rth_lo_t"],
                pclose_t=pl["rth_close_t"],
                on_gap=own - pl["rth_close_t"],
                pd_ret_sign=float(np.sign(pl["rth_close_t"]
                                          - pl["own_0930_t"])),
                prior_last_stamp=pl["rth_last_stamp"])


def load_calendar():
    """Release datetimes (ET), sorted int64 seconds. Filtered < DEV_END (the
    filter is provably immaterial: sessions end 2026-05-20 and any June+
    release is > 120 min away -> clipped to 999 regardless)."""
    c = pd.read_csv(CALP)
    dt = pd.to_datetime(c["date"] + " " + c["time_et"])
    n0 = len(dt)
    dt = dt[dt < pd.Timestamp(DEV_END)].sort_values()
    print(f"calendar: {n0} releases -> {len(dt)} after < {DEV_END} filter "
          f"({dt.min()} .. {dt.max()}); events "
          f"{sorted(c['event'].unique())} at times "
          f"{sorted(c['time_et'].unique())}")
    return dt.astype("int64").values // 10**9


def build_session(tag, LEV, RTH_DATES, REL):
    """C5 house-pattern NQ merge + 27-feature census library + 4 labels on the
    every-30s clock — construction identical to w5_c5_ceiling.build_session —
    PLUS the four frozen W7-1 feature blocks (13 new columns).
    Returns (R, ml, hi, lo, audit) — audit carries the per-session offset."""
    d0 = pd.to_datetime(tag[1:], format="%Y%m%d")
    g = pd.read_parquet(os.path.join(GR, tag + ".parquet"))
    s = pd.read_parquet(os.path.join(SH, tag + ".parquet"))
    g["time"] = pd.to_datetime(g["time"])
    s["time"] = pd.to_datetime(s["time"])

    # ---- BLOCK 1 pre-compute on the full grid (anchors at the 18:00 file
    # start / 09:30 RTH open are independent of the leading-row drop below) ----
    tod_g = (g["time"] - d0).dt.total_seconds().values
    lastp = g["last"].values.astype(np.float64)     # POINTS, never NaN
    volg = g["vol"].values.astype(np.float64)
    pv = lastp * volg
    cs_v = np.cumsum(volg)
    cs_pv = np.cumsum(pv)
    g["vwap_full_t"] = np.where(cs_v > 0, 4.0 * cs_pv / np.where(cs_v > 0,
                                                                 cs_v, 1.0),
                                np.nan)
    rthm = tod_g >= RTH_OPEN
    cs_vr = np.cumsum(volg * rthm)
    cs_pvr = np.cumsum(pv * rthm)
    g["vwap_rth_t"] = np.where(rthm & (cs_vr > 0),
                               4.0 * cs_pvr / np.where(cs_vr > 0, cs_vr, 1.0),
                               np.nan)

    f = g.merge(s, on="time", how="left")
    f["mid_last"] = f["mid_last"].ffill()
    f = f[f["mid_last"].notna()].reset_index(drop=True)
    f["mid_high"] = f["mid_high"].fillna(f["mid_last"])
    f["mid_low"] = f["mid_low"].fillna(f["mid_last"])
    ml = f["mid_last"].values.astype(np.float64)
    hi = f["mid_high"].values.astype(np.float64)
    lo = f["mid_low"].values.astype(np.float64)
    n = len(f)
    tod = (f["time"] - d0).dt.total_seconds().values
    upd = (f["bid_upd"] + f["ask_upd"]).values
    upd60 = pd.Series(upd).rolling(60, min_periods=1).sum().values
    dec = (tod >= 9 * 3600 + 1800) & (tod < 16 * 3600) & (upd60 > 0)
    dec_idx = np.where(dec)[0]
    if len(dec_idx) == 0:
        return None, None, None, None, None
    starts = dec_idx[::CLOCK].astype(np.int64)

    mls = pd.Series(ml)
    dmid = mls.diff()
    F = pd.DataFrame({"session": tag, "t": np.arange(n), "tod": tod})
    for k in (5, 10, 30, 60, 300):
        F[f"ret{k}"] = mls.diff(k).values
    F["rv60"] = dmid.rolling(60).std().values
    F["rv300"] = dmid.rolling(300).std().values
    tv60 = dmid.abs().rolling(60).sum().values
    F["tv60"] = tv60
    F["eff60"] = np.abs(F["ret60"]) / np.where(tv60 > 0, tv60, np.nan)
    F["range300"] = (pd.Series(hi).rolling(300).max()
                     - pd.Series(lo).rolling(300).min()).values
    shi = np.maximum.accumulate(hi)
    slo = np.minimum.accumulate(lo)
    F["dist_hi"] = shi - ml
    F["dist_lo"] = ml - slo
    hidx = pd.Series(np.where(hi >= shi - 1e-9, np.arange(n), np.nan)).ffill().values
    lidx = pd.Series(np.where(lo <= slo + 1e-9, np.arange(n), np.nan)).ffill().values
    F["secs_since_hi"] = np.arange(n) - hidx
    F["secs_since_lo"] = np.arange(n) - lidx
    for k in (10, 60):
        F[f"trades{k}"] = pd.Series(f["trades"].values).rolling(k).sum().values
        F[f"vol{k}"] = pd.Series(f["vol"].values).rolling(k).sum().values
        F[f"upd{k}"] = pd.Series(upd).rolling(k).sum().values
        F[f"sflow{k}"] = pd.Series(f["sflow"].values).rolling(k).sum().values
    F["act_accel"] = F["trades10"] / np.where(F["trades60"] > 0, F["trades60"] / 6.0,
                                              np.nan)
    F["nsflow60"] = F["sflow60"] / np.where(F["vol60"] > 0, F["vol60"], np.nan)
    F["spread"] = f["spread_t"].values
    F["spread60"] = pd.Series(f["spread_t"].values).rolling(60).mean().values

    # ---- BLOCK 1: VWAP features (ticks) ----
    vr = f["vwap_rth_t"].values
    F["vwap_dist"] = ml - vr
    F["vwap_slope60"] = pd.Series(vr).diff(60).values     # ticks per minute
    F["vwap_dist_full"] = ml - f["vwap_full_t"].values

    # ---- BLOCK 2: prior-day levels via the frozen offset rule ----
    ctx = prior_day_context(d0, LEV, RTH_DATES)
    audit = dict(session=tag)
    if ctx is None:
        F["pdh_dist"] = np.nan
        F["pdl_dist"] = np.nan
        F["pclose_dist"] = np.nan
        F["on_gap"] = np.nan
        F["prior_day_ret_sign"] = np.nan
        audit.update(prior_date=None, offset_s=np.nan)
    else:
        pos = int(np.searchsorted(tod, RTH_OPEN))
        if pos >= n or tod[pos] != RTH_OPEN:
            pos = max(0, pos - 1)   # last available second <= 09:30:00
        ml_0930 = ml[pos]
        offset_s = ctx["own_0930_t"] - ml_0930
        pdh_a = ctx["pdh_t"] - offset_s
        pdl_a = ctx["pdl_t"] - offset_s
        pcl_a = ctx["pclose_t"] - offset_s
        F["pdh_dist"] = pdh_a - ml
        F["pdl_dist"] = ml - pdl_a
        F["pclose_dist"] = ml - pcl_a
        F["on_gap"] = ctx["on_gap"]
        F["prior_day_ret_sign"] = ctx["pd_ret_sign"]
        audit.update(prior_date=str(ctx["prior_date"].date()),
                     offset_s=offset_s, csv_0930_t=ctx["own_0930_t"],
                     sechilo_mid_0930=ml_0930, tod_0930_used=tod[pos],
                     pdh_actual_t=pdh_a, pdl_actual_t=pdl_a,
                     pclose_actual_t=pcl_a, on_gap_t=ctx["on_gap"],
                     prior_day_ret_sign=ctx["pd_ret_sign"],
                     prior_last_stamp=ctx["prior_last_stamp"])

    # ---- BLOCK 3: event flags (never NaN) ----
    tsec = f["time"].astype("int64").values // 10**9
    idx = np.searchsorted(REL, tsec, side="right")
    since = np.where(idx > 0, (tsec - REL[np.maximum(idx - 1, 0)]) / 60.0,
                     np.inf)
    to = np.where(idx < len(REL),
                  (REL[np.minimum(idx, len(REL) - 1)] - tsec) / 60.0, np.inf)
    F["min_since_release"] = np.where(since <= 120.0, since, 999.0)
    F["min_to_release"] = np.where(to <= 120.0, to, 999.0)

    # ---- BLOCK 4: ES signed flow from raw trades (tick-rule) ----
    e = pd.read_parquet(os.path.join(ESRAW, "es_" + tag + ".parquet"),
                        columns=["bip", "time", "price", "volume"])
    tr = e[e["bip"] == 0].copy()
    px = tr["price"].values.astype(np.float64)
    dp = np.diff(px, prepend=px[0] if len(px) else 0.0)
    sg = np.sign(dp)
    sg[0] = 0.0
    sgs = pd.Series(sg).replace(0.0, np.nan).ffill().fillna(0.0).values
    tr["sv"] = sgs * tr["volume"].values.astype(np.float64)
    tr["sec"] = tr["time"].str.slice(0, 19)
    per = tr.groupby("sec")["sv"].sum()
    sv_df = pd.DataFrame({"time": pd.to_datetime(per.index),
                          "es_sv_raw": per.values, "es_has": 1.0})
    fe = f[["time"]].merge(sv_df, on="time", how="left")
    assert len(fe) == n, "ES merge changed row count (duplicate ES seconds?)"
    has_es = fe["es_has"].notna().values
    last_es = pd.Series(np.where(has_es, tod, np.nan)).ffill().values
    stale = tod - last_es                     # NaN before first ES trade
    ok = stale <= ES_STALE                    # False where stale NaN or >5s
    sv = np.where(ok, fe["es_sv_raw"].fillna(0.0).values, np.nan)
    svs = pd.Series(sv)
    F["es_sflow10"] = svs.rolling(10).sum().values
    F["es_sflow60"] = svs.rolling(60).sum().values
    sig = svs.rolling(ZWIN, min_periods=ZMIN).std().values
    F["es_zsflow60"] = F["es_sflow60"].values / np.where(sig > 0, sig, np.nan)

    R = F.iloc[starts].copy().reset_index(drop=True)
    for dname, dv, A, B in LABELS:
        R[f"lab_{dname}_{A}_{B}"] = label_scan(ml, hi, lo, starts, dv, float(A),
                                               float(B), CAP)
    return R, ml, hi, lo, audit


def leakage_probe(tag, LEV, RTH_DATES, REL, n_probe=200):
    """ASSERTION 1 (verbatim C5): perturbing hi/lo at the decision second t must
    leave every label unchanged (the label window starts at t+1)."""
    R, ml, hi, lo, _ = build_session(tag, LEV, RTH_DATES, REL)
    starts = R["t"].values.astype(np.int64)
    rng = np.random.default_rng(SEED)
    pick = rng.choice(len(starts), size=min(n_probe, len(starts)), replace=False)
    n_checked = 0
    for j in pick:
        t0 = starts[j]
        hi2 = hi.copy()
        lo2 = lo.copy()
        hi2[t0] = ml[t0] + 1000.0
        lo2[t0] = ml[t0] - 1000.0
        one = np.array([t0], np.int64)
        for dname, dv, A, B in LABELS:
            l_orig = label_scan(ml, hi, lo, one, dv, float(A), float(B), CAP)[0]
            l_pert = label_scan(ml, hi2, lo2, one, dv, float(A), float(B), CAP)[0]
            assert l_orig == l_pert, (
                f"LEAKAGE: label {dname}+{A}/-{B} at t={t0} changed when second t "
                f"was perturbed")
            n_checked += 1
    return n_checked


def brier(y, p):
    return float(np.mean((p - y) ** 2))


def perm_importance(model, Xv, yv, feats, rng, nrep=3):
    """Mean Brier increase on the validation block when one feature is permuted
    (C5 construction, parameterized by feature list)."""
    p0 = model.predict_proba(Xv)[:, 1]
    b0 = brier(yv, p0)
    imp = np.zeros(len(feats))
    for j in range(len(feats)):
        acc = 0.0
        for _ in range(nrep):
            Xp = Xv.copy()
            Xp[:, j] = Xp[rng.permutation(len(Xp)), j]
            acc += brier(yv, model.predict_proba(Xp)[:, 1]) - b0
        imp[j] = acc / nrep
    return imp


def lift_with_ci(dfp, top_mask):
    """Pooled top-decile P, baseline P, lift, day-clustered (session-bootstrap)
    95% CIs — VERBATIM C5. Seed 20260808, 1000 reps."""
    tmp = dfp.assign(top=top_mask)
    per = tmp.groupby("session").agg(all_n=("y", "size"), all_t=("y", "sum"))
    pt = tmp[tmp["top"]].groupby("session").agg(top_n=("y", "size"),
                                               top_t=("y", "sum"))
    per = per.join(pt).fillna(0)
    an = per["all_n"].values.astype(float)
    at = per["all_t"].values.astype(float)
    tn = per["top_n"].values.astype(float)
    tt = per["top_t"].values.astype(float)
    p_all = at.sum() / an.sum()
    p_top = tt.sum() / tn.sum()
    rng = np.random.default_rng(SEED)
    nsess = len(per)
    lifts = np.empty(NREPS)
    ptops = np.empty(NREPS)
    for r in range(NREPS):
        b = rng.choice(nsess, nsess, replace=True)
        tb = tn[b].sum()
        ptops[r] = tt[b].sum() / tb if tb > 0 else np.nan
        lifts[r] = ptops[r] - at[b].sum() / an[b].sum()
    lifts = lifts[~np.isnan(lifts)]
    ptops = ptops[~np.isnan(ptops)]
    return dict(p_all=p_all, p_top=p_top, lift=p_top - p_all,
                lift_lo=float(np.percentile(lifts, 2.5)),
                lift_hi=float(np.percentile(lifts, 97.5)),
                ptop_lo=float(np.percentile(ptops, 2.5)),
                ptop_hi=float(np.percentile(ptops, 97.5)),
                n_top=int(tn.sum()), n_all=int(an.sum()))


def paired_delta_ci(Pa, Pb):
    """Paired session-bootstrap 95% CI for delta(lift) = lift(aug) - lift(base).
    Same session draws applied to both runs per rep (day-clustered), seed
    20260808, 1000 reps — VERBATIM W6."""
    key = sorted(Pa["session"].unique())
    idx = {s: i for i, s in enumerate(key)}
    nsess = len(key)

    def agg(P):
        an = np.zeros(nsess); at = np.zeros(nsess)
        tn = np.zeros(nsess); tt = np.zeros(nsess)
        g = P.groupby("session")
        for s, gg in g:
            i = idx[s]
            an[i] = len(gg); at[i] = gg["y"].sum()
            tn[i] = gg["top"].sum(); tt[i] = gg.loc[gg["top"], "y"].sum()
        return an, at, tn, tt

    an_a, at_a, tn_a, tt_a = agg(Pa)
    an_b, at_b, tn_b, tt_b = agg(Pb)
    assert np.array_equal(an_a, an_b) and np.array_equal(at_a, at_b), \
        "paired delta: per-session row/label counts differ between runs"
    lift_a = tt_a.sum() / tn_a.sum() - at_a.sum() / an_a.sum()
    lift_b = tt_b.sum() / tn_b.sum() - at_b.sum() / an_b.sum()
    rng = np.random.default_rng(SEED)
    deltas = np.empty(NREPS)
    for r in range(NREPS):
        b = rng.choice(nsess, nsess, replace=True)
        ta, tb = tn_a[b].sum(), tn_b[b].sum()
        if ta <= 0 or tb <= 0:
            deltas[r] = np.nan
            continue
        la = tt_a[b].sum() / ta - at_a[b].sum() / an_a[b].sum()
        lb = tt_b[b].sum() / tb - at_b[b].sum() / an_b[b].sum()
        deltas[r] = lb - la
    deltas = deltas[~np.isnan(deltas)]
    return dict(delta=lift_b - lift_a,
                delta_lo=float(np.percentile(deltas, 2.5)),
                delta_hi=float(np.percentile(deltas, 97.5)))


def make_models():
    return {
        "logit": Pipeline([("sc", StandardScaler()),
                           ("lr", LogisticRegression(penalty="l2", C=1.0,
                                                     solver="lbfgs",
                                                     max_iter=2000))]),
        "hgb": HistGradientBoostingClassifier(max_depth=3, early_stopping=True,
                                              max_iter=300, random_state=SEED),
    }


def run_ceiling(D, folds, feats, run_id):
    """One full C5 pass (4 labels x 2 models) on feature list `feats`.
    Model loop is the C5 loop verbatim, with `run` tagged into every output."""
    oof_rows, met_rows, cal_rows, foldlift_rows, imp_rows = [], [], [], [], []
    for dname, dv, A, B in LABELS:
        lc = f"lab_{dname}_{A}_{B}"
        lab_id = f"{dname}_{A}_{B}"
        sub = D[D[lc] >= 0]
        for mname in make_models().keys():
            preds, imp_acc, imp_w = [], np.zeros(len(feats)), 0.0
            fold_brier_rows = []
            for v, tr, va in folds:
                trd = sub[sub["session"].isin(tr)]
                vad = sub[sub["session"].isin(va)]
                Xtr = trd[feats].values.astype(np.float64)
                ytr = (trd[lc] == 1).values.astype(int)
                Xva = vad[feats].values.astype(np.float64)
                yva = (vad[lc] == 1).values.astype(int)
                model = make_models()[mname]
                model.fit(Xtr, ytr)
                p = model.predict_proba(Xva)[:, 1]
                base_tr = ytr.mean()
                preds.append(pd.DataFrame(dict(session=vad["session"].values,
                                               t=vad["t"].values, fold=v, y=yva, p=p,
                                               base_tr=base_tr)))
                rng = np.random.default_rng(SEED + v)
                imp = perm_importance(model, Xva, yva, feats, rng)
                imp_acc += imp * len(yva)
                imp_w += len(yva)
                fold_brier_rows.append(dict(fold=v, n=len(yva),
                                            brier=brier(yva, p),
                                            brier_base=brier(yva,
                                                             np.full(len(yva),
                                                                     base_tr))))
            P = pd.concat(preds, ignore_index=True)
            P["label"] = lab_id
            P["model"] = mname
            P["run"] = run_id

            bri = brier(P["y"].values, P["p"].values)
            bri_base = brier(P["y"].values, P["base_tr"].values)
            top = np.zeros(len(P), bool)
            for v, _, _ in folds:
                m = P["fold"].values == v
                thr = np.quantile(P.loc[m, "p"].values, 0.9)
                top[m & (P["p"].values >= thr)] = True
            P["top"] = top
            oof_rows.append(P)
            res = lift_with_ci(P[["session", "y"]], top)
            fl = []
            for v, _, _ in folds:
                m = P["fold"].values == v
                pf = P.loc[m]
                tf = top[m]
                l_v = pf.loc[tf, "y"].mean() - pf["y"].mean()
                fl.append(l_v)
                foldlift_rows.append(dict(run=run_id, label=lab_id, model=mname,
                                          fold=v, n_val=int(m.sum()),
                                          n_top=int(tf.sum()),
                                          base_P=pf["y"].mean(),
                                          top_P=pf.loc[tf, "y"].mean(), lift=l_v,
                                          brier=fold_brier_rows[v - 1]["brier"],
                                          brier_base=fold_brier_rows[v - 1]
                                          ["brier_base"]))
            gap = C1_GAP[(dname, A, B)]
            pass5 = (res["lift"] >= 0.05) and (res["lift_lo"] > 0)
            stable7 = (res["lift"] >= 0.07) and (res["lift_lo"] > 0) and \
                      all(x > 0 for x in fl)
            met_rows.append(dict(run=run_id, label=lab_id, model=mname,
                                 n_val=res["n_all"], n_top=res["n_top"],
                                 brier=bri, brier_base=bri_base,
                                 brier_skill=1 - bri / bri_base,
                                 base_P=res["p_all"], top_P=res["p_top"],
                                 ptop_lo=res["ptop_lo"], ptop_hi=res["ptop_hi"],
                                 lift=res["lift"], lift_lo=res["lift_lo"],
                                 lift_hi=res["lift_hi"],
                                 fold_lifts=";".join(f"{x:+.4f}" for x in fl),
                                 c1_gap=gap, lift_minus_gap=res["lift"] - gap,
                                 pass_5pp=pass5, pass_7pp_stable=stable7))
            q = np.quantile(P["p"].values, np.linspace(0, 1, 11))
            q[0], q[-1] = -np.inf, np.inf
            binid = np.digitize(P["p"].values, q[1:-1])
            for bidx in range(10):
                m = binid == bidx
                if m.sum() == 0:
                    continue
                cal_rows.append(dict(run=run_id, label=lab_id, model=mname,
                                     bin=bidx, n=int(m.sum()),
                                     p_pred_mean=float(P.loc[m, "p"].mean()),
                                     p_real=float(P.loc[m, "y"].mean())))
            imp_mean = imp_acc / imp_w
            order = np.argsort(-imp_mean)
            for rank, j in enumerate(order):
                imp_rows.append(dict(run=run_id, label=lab_id, model=mname,
                                     rank=rank + 1, feature=feats[j],
                                     is_new=feats[j] in NEW_FEATS,
                                     brier_increase=float(imp_mean[j])))
            print(f"\n--- [{run_id}] {lab_id} | {mname} ---")
            print(f"  Brier {bri:.5f} vs baseline {bri_base:.5f} "
                  f"(skill {1 - bri / bri_base:+.4f})")
            print(f"  base P(target) {res['p_all']:.4f} | top-decile P "
                  f"{res['p_top']:.4f} [{res['ptop_lo']:.4f},{res['ptop_hi']:.4f}] "
                  f"(n_top={res['n_top']})")
            print(f"  LIFT {100 * res['lift']:+.2f}pp "
                  f"CI [{100 * res['lift_lo']:+.2f},{100 * res['lift_hi']:+.2f}]pp | "
                  f"C1 gap {100 * gap:.2f}pp | lift-gap "
                  f"{100 * (res['lift'] - gap):+.2f}pp")
            print(f"  fold lifts (pp): "
                  + " ".join(f"{100 * x:+.2f}" for x in fl)
                  + f" | pass>=5pp:{pass5} pass>=7pp-stable:{stable7}")
            print("  perm importance top-10: "
                  + ", ".join(f"{feats[j]}({imp_mean[j] * 1e4:.2f}e-4)"
                              for j in order[:10]), flush=True)
    return (pd.concat(oof_rows, ignore_index=True), pd.DataFrame(met_rows),
            pd.DataFrame(cal_rows), pd.DataFrame(foldlift_rows),
            pd.DataFrame(imp_rows))


def main():
    print(f"W7-1 C5b augmented predictability ceiling (decisive) | seed={SEED} "
          f"reps={NREPS} clock={CLOCK}s cap={CAP}s minhist={MINHIST}s "
          f"es_trade_stale<={ES_STALE}s zwin={ZWIN}s zmin={ZMIN}")
    print(f"new blocks: vwap{VWAP_FEATS} prior_day{PRIOR_FEATS} "
          f"event{EVENT_FEATS} es_flow{ESF_FEATS} -> {len(NEW_FEATS)} new "
          f"features; runs: {[r for r, _ in RUNS]}")
    print("units: sechilo mid & all distance features in TICKS; grid `last` and "
          "the 3-min CSV in POINTS (x4 to ticks). Documented ~1t error: CSV "
          "closes are LAST prices, sechilo is union-BBO MID (measured median "
          "|last*4 - mid_last| = 1.0t on s20260123).")
    LEV, RTH_DATES = load_csv_levels()
    REL = load_calendar()
    sessions = sorted(os.path.basename(p)[:-8]
                      for p in glob.glob(os.path.join(SH, "s*.parquet")))
    missing_es = [t for t in sessions
                  if not os.path.exists(os.path.join(ESRAW, "es_" + t
                                                     + ".parquet"))]
    assert not missing_es, f"raw ES trades missing for: {missing_es}"
    print(f"sessions: {len(sessions)}  ({sessions[0]} .. {sessions[-1]}) — same "
          f"37-tag list as C5; every tag has a raw-ES partner file")
    print("caveats: NQ s20250902 quote-dead (self-skips, as in C5); "
          "es_s20260519 feed truncated mid-afternoon (rows drop via the 5s "
          "trade-staleness rule -> excluded from BOTH runs); priors of "
          "s20250902/s20251128 are early-close half-days (13:00 close used as "
          "prior RTH close — documented, not dropped)")

    # ---- ASSERTION 1: feature/label window no-overlap (empirical) ----
    probe_tag = sessions[len(sessions) // 2]
    nch = leakage_probe(probe_tag, LEV, RTH_DATES, REL)
    print(f"ASSERTION 1 PASSED: label windows start at t+1s and never overlap "
          f"the feature second t — perturbing hi/lo at t left all labels "
          f"unchanged ({nch} row-label checks on {probe_tag}).")

    # ---- build dataset ----
    frames, audits = [], []
    for tag in sessions:
        R, _, _, _, audit = build_session(tag, LEV, RTH_DATES, REL)
        if R is None:
            print(tag, "SKIPPED: zero quote-alive RTH seconds (dead quote feed; "
                  "same handling as census)", flush=True)
            continue
        frames.append(R)
        audits.append(audit)
        n_new_nan = int(R[NEW_FEATS].isna().any(axis=1).sum())
        print(tag, "rows:", len(R), "| new-block NaN rows:", n_new_nan,
              "| offset_s:", f"{audit.get('offset_s', np.nan):+.1f}t",
              flush=True)
    pd.DataFrame(audits).to_csv(os.path.join(OUTD, "w7c5b_offsets.csv"),
                                index=False)
    D = pd.concat(frames, ignore_index=True)
    n_raw = len(D)
    lab_cols = [f"lab_{d}_{A}_{B}" for d, _, A, B in LABELS]
    n_hist = int((D["t"] < MINHIST).sum())
    D = D[D["t"] >= MINHIST]
    n_nan = int(D[NQ_FEATS].isna().any(axis=1).sum())
    D = D.dropna(subset=NQ_FEATS)
    n_c5_equiv = len(D)          # sample the original C5 kept

    # ---- BASELINE-MATRIX VERIFICATION vs committed C5 artifacts ----
    print(f"\n=== BASELINE-MATRIX VERIFICATION vs committed C5 dataset ===")
    assert n_c5_equiv == C5_ROWS, \
        f"rebuilt C5-equivalent rows {n_c5_equiv} != committed {C5_ROWS}"
    C5D = pd.read_parquet(C5DS)
    assert len(C5D) == C5_ROWS
    A_ = D.sort_values(["session", "t"]).reset_index(drop=True)
    B_ = C5D.sort_values(["session", "t"]).reset_index(drop=True)
    assert (A_["session"].values == B_["session"].values).all() and \
        (A_["t"].values == B_["t"].values).all(), "row identity mismatch vs C5"
    for c in NQ_FEATS:
        assert np.allclose(A_[c].values.astype(float),
                           B_[c].values.astype(float),
                           rtol=1e-9, atol=1e-9, equal_nan=True), \
            f"feature {c} differs from committed C5 dataset"
    for c in lab_cols:
        assert (A_[c].values == B_[c].values).all(), \
            f"label {c} differs from committed C5 dataset"
    summ = pd.read_csv(C5SUM).set_index("session")
    per_sess = D.groupby("session").size()
    assert (per_sess.reindex(summ.index).values == summ["rows"].values).all(), \
        "per-session row counts differ from w5c5_dataset_summary.csv"
    for d, _, A2, B2 in LABELS:
        lc = f"lab_{d}_{A2}_{B2}"
        nei = D[D[lc] == -1].groupby("session").size().reindex(
            summ.index).fillna(0).astype(int)
        assert (nei.values == summ[f"neither_{d}_{A2}_{B2}"].values).all(), \
            f"neither-counts for {lc} differ from w5c5_dataset_summary.csv"
    print(f"VERIFIED: rebuilt baseline matrix == committed w5c5_dataset.parquet "
          f"(rows {C5_ROWS}; 27 features allclose; 4 labels identical; "
          f"per-session rows and neither-counts match "
          f"w5c5_dataset_summary.csv).")
    print("per-label base rates over decided rows (rebuilt == committed):")
    for c in lab_cols:
        br_a = (A_[c] == 1).sum() / max(1, (A_[c] >= 0).sum())
        br_b = (B_[c] == 1).sum() / max(1, (B_[c] >= 0).sum())
        assert abs(br_a - br_b) < 1e-12
        print(f"  {c}: {br_a:.4f}")

    # ---- same-sample rule: drop rows NaN in any new block from BOTH runs ----
    print(f"\n=== SAME-SAMPLE RULE (new-block NaN drops) ===")
    blk_nan = {}
    for bname, bfeats in BLOCKS:
        blk_nan[bname] = int(D[bfeats].isna().any(axis=1).sum())
    n_newnan = int(D[NEW_FEATS].isna().any(axis=1).sum())
    drop_mask = D[NEW_FEATS].isna().any(axis=1)
    drops = D[drop_mask].copy()
    drop_per_sess = drops.groupby("session").agg(
        n_dropped=("t", "size"),
        vwap_nan=("vwap_slope60", lambda x: int(x.isna().sum())),
        es_nan=("es_sflow60", lambda x: int(x.isna().sum())))
    drop_per_sess.to_csv(os.path.join(OUTD, "w7c5b_drops.csv"))
    D = D[~drop_mask].reset_index(drop=True)
    D["date"] = pd.to_datetime(D["session"].str[1:], format="%Y%m%d")
    print(f"clock rows: {n_raw} raw | dropped t<{MINHIST}: {n_hist} | "
          f"dropped NQ-NaN-feature: {n_nan} | C5-equivalent rows: {n_c5_equiv} "
          f"| dropped new-block-NaN (same-sample rule): {n_newnan} | "
          f"modeling rows (BOTH runs): {len(D)}")
    print(f"per-block NaN rows (overlapping): "
          + ", ".join(f"{k}={v}" for k, v in blk_nan.items()))
    print("drop reasons: vwap_slope60 undefined in the first 60s of RTH (the "
          "09:30:00/09:30:30 clock rows of every session); ES-flow NaN from "
          ">5s trade-staleness / z-norm warmup / the truncated es_s20260519 "
          "afternoon. Prior-day and event blocks caused ZERO drops (every "
          "modeled session 2025-08-14..2026-05-20 has a prior RTH day and a "
          "09:30 bar in the 2022+ CSV; the spec's anticipated first-CSV-session "
          "drop does not arise).")
    print("per-session drops:")
    for s_, r in drop_per_sess.iterrows():
        print(f"  {s_}: {int(r['n_dropped'])} "
              f"(vwap-related {int(r['vwap_nan'])}, es-related "
              f"{int(r['es_nan'])})")
    for c in lab_cols:
        neither = int((D[c] == -1).sum())
        print(f"  {c}: neither-hit excluded {neither} "
              f"({100 * neither / len(D):.2f}%) | "
              f"P(target) over decided rows: "
              f"{(D[c] == 1).sum() / max(1, (D[c] >= 0).sum()):.4f}")
    D.to_parquet(os.path.join(OUTD, "w7c5b_dataset.parquet"), index=False)
    ds = D.groupby("session").agg(rows=("t", "size"), **{
        f"neither_{d}_{A}_{B}": (f"lab_{d}_{A}_{B}", lambda x: int((x == -1).sum()))
        for d, _, A, B in LABELS})
    ds.to_csv(os.path.join(OUTD, "w7c5b_dataset_summary.csv"))

    # ---- folds: chronological session-grouped expanding 5-fold (C5 verbatim,
    # built from the SAME 37-session list) ----
    blocks = [list(b) for b in np.array_split(np.array(sessions), NFOLDS)]
    print("\nfold blocks (chronological):")
    for i, b in enumerate(blocks):
        print(f"  block {i}: {len(b)} sessions  {b[0]} .. {b[-1]}")
    folds = []
    for v in range(1, NFOLDS):
        tr = [s for b in blocks[:v] for s in b]
        va = blocks[v]
        assert len(set(tr) & set(va)) == 0, "session appears in train AND validation"
        assert max(tr) < min(va), "training session not strictly earlier than validation"
        folds.append((v, tr, va))
    print("ASSERTION 2 PASSED: in all 4 folds, train/validation session sets "
          "are disjoint and every training session is strictly earlier than "
          "every validation session.")

    # ---- run baseline then augmented on the SAME rows ----
    all_oof, all_met, all_cal, all_fl, all_imp = [], [], [], [], []
    for run_id, feats in RUNS:
        print(f"\n================ RUN {run_id}: {len(feats)} features "
              f"================")
        oof, met, cal, fl, imp = run_ceiling(D, folds, feats, run_id)
        all_oof.append(oof); all_met.append(met); all_cal.append(cal)
        all_fl.append(fl); all_imp.append(imp)
    OOF = pd.concat(all_oof, ignore_index=True)
    MET = pd.concat(all_met, ignore_index=True)
    OOF.to_parquet(os.path.join(OUTD, "w7c5b_oof_predictions.parquet"),
                   index=False)
    MET.to_csv(os.path.join(OUTD, "w7c5b_metrics.csv"), index=False)
    pd.concat(all_cal, ignore_index=True).to_csv(
        os.path.join(OUTD, "w7c5b_calibration.csv"), index=False)
    pd.concat(all_fl, ignore_index=True).to_csv(
        os.path.join(OUTD, "w7c5b_fold_lifts.csv"), index=False)
    IMP = pd.concat(all_imp, ignore_index=True)
    IMP.to_csv(os.path.join(OUTD, "w7c5b_perm_importance.csv"), index=False)

    # ---- reproduction diagnostic: baseline (same-sample) vs original C5 ----
    c5 = pd.read_csv(C5M)
    A3 = MET[MET["run"] == "base_nq27"].set_index(["label", "model"])
    C3 = c5.set_index(["label", "model"])
    rep_rows = []
    print("\n=== REPRODUCTION DIAGNOSTIC: baseline [27 NQ feats, same-sample] "
          "vs original C5 ===")
    print(f"(sample: C5 modeling rows {C5_ROWS} -> same-sample rows {len(D)}; "
          f"difference = new-block NaN rows: RTH-open vwap_slope60 warmup + "
          f"ES-flow staleness/warmup incl. the truncated es_s20260519 "
          f"afternoon)")
    repro_ok = True
    for key in C3.index:
        dl = A3.loc[key, "lift"] - C3.loc[key, "lift"]
        dk = A3.loc[key, "brier_skill"] - C3.loc[key, "brier_skill"]
        flip = bool(A3.loc[key, "pass_5pp"]) != bool(C3.loc[key, "pass_5pp"])
        ok = (abs(dl) <= REPRO_TOL_LIFT) and (abs(dk) <= REPRO_TOL_SKILL) \
            and not flip
        repro_ok &= ok
        rep_rows.append(dict(label=key[0], model=key[1],
                             lift_c5=C3.loc[key, "lift"],
                             lift_base=A3.loc[key, "lift"], dlift=dl,
                             skill_c5=C3.loc[key, "brier_skill"],
                             skill_base=A3.loc[key, "brier_skill"], dskill=dk,
                             n_val_c5=int(C3.loc[key, "n_val"]),
                             n_val_base=int(A3.loc[key, "n_val"]),
                             pass5_c5=bool(C3.loc[key, "pass_5pp"]),
                             pass5_base=bool(A3.loc[key, "pass_5pp"]),
                             within_tol=ok))
        print(f"  {key[0]:12s} {key[1]:5s} lift C5 {100*C3.loc[key,'lift']:+.2f}pp "
              f"-> base {100*A3.loc[key,'lift']:+.2f}pp (d {100*dl:+.2f}pp) | "
              f"skill C5 {C3.loc[key,'brier_skill']:+.4f} -> "
              f"{A3.loc[key,'brier_skill']:+.4f} (d {dk:+.4f}) | "
              f"n {int(C3.loc[key,'n_val'])}->{int(A3.loc[key,'n_val'])} | "
              f"tol_ok={ok}")
    pd.DataFrame(rep_rows).to_csv(os.path.join(OUTD,
                                               "w7c5b_repro_comparison.csv"),
                                  index=False)
    print(("REPRODUCTION DIAGNOSTIC PASSED: all 8 cells within W6 tolerance "
           f"(|dlift|<={100*REPRO_TOL_LIFT:.1f}pp, |dskill|<="
           f"{REPRO_TOL_SKILL}, no pass_5pp flip).") if repro_ok else
          "REPRODUCTION DIAGNOSTIC: at least one cell outside W6 tolerance — "
          "flagged; the decisive W7-1 readout (baseline vs augmented, same "
          "rows) is internal and remains paired, but interpret vs-C5 levels "
          "with caution.")

    # ---- paired delta (aug) - (base) with day-clustered CI ----
    delta_rows = []
    print("\n=== DELTA top-decile lift: augmented minus baseline — paired "
          "session bootstrap ===")
    for dname, dv, A4, B4 in LABELS:
        lab_id = f"{dname}_{A4}_{B4}"
        for mname in ("logit", "hgb"):
            Pa = OOF[(OOF["run"] == "base_nq27") & (OOF["label"] == lab_id)
                     & (OOF["model"] == mname)].reset_index(drop=True)
            Pb = OOF[(OOF["run"] == "aug_nq27_new13") & (OOF["label"] == lab_id)
                     & (OOF["model"] == mname)].reset_index(drop=True)
            assert np.array_equal(Pa["session"].values, Pb["session"].values)
            assert np.array_equal(Pa["t"].values, Pb["t"].values)
            assert np.array_equal(Pa["y"].values, Pb["y"].values)
            dres = paired_delta_ci(Pa[["session", "y", "top"]],
                                   Pb[["session", "y", "top"]])
            ra = MET[(MET["run"] == "base_nq27") & (MET["label"] == lab_id)
                     & (MET["model"] == mname)].iloc[0]
            rb = MET[(MET["run"] == "aug_nq27_new13") & (MET["label"] == lab_id)
                     & (MET["model"] == mname)].iloc[0]
            delta_rows.append(dict(
                label=lab_id, model=mname,
                lift_base=ra["lift"], lift_base_lo=ra["lift_lo"],
                lift_base_hi=ra["lift_hi"],
                lift_aug=rb["lift"], lift_aug_lo=rb["lift_lo"],
                lift_aug_hi=rb["lift_hi"],
                delta=dres["delta"], delta_lo=dres["delta_lo"],
                delta_hi=dres["delta_hi"],
                brier_skill_base=ra["brier_skill"],
                brier_skill_aug=rb["brier_skill"],
                d_brier_skill=rb["brier_skill"] - ra["brier_skill"],
                pass5_base=bool(ra["pass_5pp"]), pass5_aug=bool(rb["pass_5pp"]),
                pass7_aug=bool(rb["pass_7pp_stable"])))
            print(f"  {lab_id:12s} {mname:5s} base {100*ra['lift']:+.2f}pp "
                  f"[{100*ra['lift_lo']:+.2f},{100*ra['lift_hi']:+.2f}] | "
                  f"aug {100*rb['lift']:+.2f}pp "
                  f"[{100*rb['lift_lo']:+.2f},{100*rb['lift_hi']:+.2f}] | "
                  f"DELTA {100*dres['delta']:+.2f}pp "
                  f"[{100*dres['delta_lo']:+.2f},{100*dres['delta_hi']:+.2f}] | "
                  f"skill {ra['brier_skill']:+.4f}->{rb['brier_skill']:+.4f} | "
                  f"pass5(aug)={bool(rb['pass_5pp'])}")
    DL = pd.DataFrame(delta_rows)
    DL.to_csv(os.path.join(OUTD, "w7c5b_delta.csv"), index=False)

    # ---- new-block permutation importance in the augmented run ----
    print("\n=== new-feature permutation importance in augmented run (rank of "
          f"{len(NQ_FEATS) + len(NEW_FEATS)}; Brier increase x1e4) ===")
    ib = IMP[(IMP["run"] == "aug_nq27_new13") & (IMP["is_new"])]
    for (lab_id, mname), gg in ib.groupby(["label", "model"]):
        gg = gg.sort_values("rank")
        print(f"  {lab_id:12s} {mname:5s} "
              + ", ".join(f"{f_}(r{int(rk)},{bi*1e4:.2f})"
                          for f_, rk, bi in zip(gg["feature"], gg["rank"],
                                                gg["brier_increase"])))
    blk_of = {f_: b for b, fl_ in BLOCKS for f_ in fl_}
    print("block-mean Brier increase x1e4 (augmented run, mean over features "
          "in block):")
    ib2 = ib.assign(block=ib["feature"].map(blk_of))
    for (lab_id, mname), gg in ib2.groupby(["label", "model"]):
        bm = gg.groupby("block")["brier_increase"].mean() * 1e4
        print(f"  {lab_id:12s} {mname:5s} "
              + ", ".join(f"{b}={v:.2f}" for b, v in bm.items()))

    # ---- FROZEN VERDICT (spec W7-1 interpretation rule) ----
    print("\n=== FROZEN VERDICT (spec W7-1) ===")
    hits = DL[(DL["lift_aug"] >= 0.05) & (DL["lift_aug_lo"] > 0)]
    best = DL.loc[DL["lift_aug"].idxmax()]
    print(f"best augmented lift: {best['label']} {best['model']} "
          f"{100*best['lift_aug']:+.2f}pp "
          f"[{100*best['lift_aug_lo']:+.2f},{100*best['lift_aug_hi']:+.2f}] | "
          f"delta vs baseline {100*best['delta']:+.2f}pp "
          f"[{100*best['delta_lo']:+.2f},{100*best['delta_hi']:+.2f}]")
    if len(hits) > 0:
        print("VERDICT: CONVERSION SPEC REQUIRED — augmented cell(s) >= 5pp "
              "with CI_lo > 0: "
              + "; ".join(f"{r.label}/{r.model} {100*r.lift_aug:+.2f}pp "
                          f"[{100*r.lift_aug_lo:+.2f},{100*r.lift_aug_hi:+.2f}]"
                          for r in hits.itertuples()))
    else:
        print("VERDICT: NO augmented cell reaches lift >= 5pp with CI_lo > 0 "
              "-> the AUGMENTED information set (census 27 + VWAP + prior-day "
              "levels + event flags + ES signed flow) is ALSO insufficient "
              "(input to Amendment 6 par.9 closure via W7).")
    print("\nW7C5B DONE")


if __name__ == "__main__":
    main()
