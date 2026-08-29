"""G2_F2_CLAIMS01_20260829 — descriptive claim register (directive §45). Trial G00021.

Six frozen auction/level practitioner claims tested against a dependence-preserving
PAIRING NULL: circular shift of the per-session LEVEL set across sessions against
unshifted paths (>=300 shifts, whole-session unit, ONE shared shift per replication
across all claims for the family statistic). No strategy, no P&L, no threshold search.

Spec: runs/G2_F2_CLAIMS01_20260829/spec.yaml (FROZEN).
Resolutions: out/spec_resolutions.txt (written BEFORE any affected number).
Every load passes research_sdk.seal_guard; nothing >= 2026-08-01 is read or persisted.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import sys
import time as _time
from datetime import date

import numpy as np
import pandas as pd

REPO = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, REPO)

from research_sdk.seal_guard import assert_presealed, truncate_presealed          # noqa: E402
from research_sdk.session_boundary import assert_not_locked_forward               # noqa: E402

RUN = os.path.join(REPO, "runs", "G2_F2_CLAIMS01_20260829")
OUT = os.path.join(RUN, "out")
DET = os.path.join(OUT, "claim_details")
os.makedirs(DET, exist_ok=True)

PARQUET = os.path.join(REPO, r"runs\SM1M_SUBSTRATE\out\nq_1m_2022_2026.parquet")
EXPECTED_SHA = "87aa53f007aa47b9ee10d0080317a3cde8d22b55aa368267fa9a4aed7435295d"

FIRST, LAST = date(2022, 1, 1), date(2026, 7, 31)
NSLOT = 390                       # RTH slots: 09:31 (slot 0) .. 16:00 (slot 389), END-stamped
S_0959, S_1000, S_1001, S_1030, S_1031, S_1100, S_1545, S_1600 = 28, 29, 30, 59, 60, 89, 374, 389
BIN = 1.25                        # 5 ticks
VA_FRAC = 0.70
VWAP_DIST = 20.0                  # pts, CL6 09:59 condition
FWD_MIN = 15
N_SHIFTS = 300
SEED_SHIFTS = 0
N_CTRL_DRAWS = 1000
SEED_CTRL = 1
MDE_K = 2.80                      # ~80% power, two-sided 5% (TICK01 convention)
Z95 = 1.96
PROBES = [1, 7, 61]

ROWS = ["CL1_ON_touch", "CL2_VA80_traversal", "CL3a_IB_extension", "CL3b_IBbreak_close_dir",
        "CL4_PDHL_touch", "CL5_trend_zeroVWAPcross", "CL6_VWAP_first_touch"]
CLAIM_DIR = {r: +1 for r in ROWS}  # every claim direction is ABOVE the null (resolutions R4)

_log = open(os.path.join(OUT, "claims01_log.txt"), "w", encoding="utf-8")


def P(*a):
    print(*a, flush=True)
    print(*a, file=_log)
    _log.flush()


# ---------------------------------------------------------------------------- load
def load() -> pd.DataFrame:
    h = hashlib.sha256()
    with open(PARQUET, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    got = h.hexdigest()
    P(f"substrate: {PARQUET}")
    P(f"  sha256 {got}")
    if got != EXPECTED_SHA:
        raise SystemExit("DEFECT: substrate sha256 does not match GENESIS_REPRO_INCUMBENT provenance")
    P("  hash MATCHES runs\\GENESIS_REPRO_INCUMBENT_20260828\\out\\run_provenance.txt")
    df = pd.read_parquet(PARQUET)
    df, n_drop = truncate_presealed(df, "time", "CLAIMS01:load")
    assert_presealed(df, "time", "CLAIMS01:post-truncate")
    P(f"seal_guard PASS: {n_drop} sealed row(s) mechanically dropped; frame certified pre-seal")
    assert_not_locked_forward(LAST)
    t = df["time"]
    df["session"] = t.dt.date.where(t.dt.hour < 18, (t + pd.Timedelta(days=1)).dt.date)
    df = df[(df["session"] >= FIRST) & (df["session"] <= LAST)]
    df = df.sort_values("time", kind="stable").reset_index(drop=True)
    P(f"loaded: {len(df):,} bars, {df['session'].nunique():,} raw sessions "
      f"({df['session'].min()} .. {df['session'].max()})")
    P("data_esnq NOT read. No VIX / $TICK / ES / BBO object touched. Volume = the substrate's own "
      "certified `volume` column.")
    return df


# ---------------------------------------------------------------------------- per-session objects
def build(df: pd.DataFrame):
    t = df["time"]
    tod = t.dt.hour * 60 + t.dt.minute
    is_rth = (tod >= 9 * 60 + 31) & (tod <= 16 * 60)
    is_on = (tod >= 18 * 60 + 1) | (tod <= 9 * 60 + 30)

    # universe = sessions with >=1 RTH bar, chronological
    sess_rth = np.sort(df.loc[is_rth, "session"].unique())
    keep = df["session"].isin(sess_rth)
    df = df[keep].reset_index(drop=True)
    t = df["time"]; tod = (t.dt.hour * 60 + t.dt.minute).to_numpy()
    is_rth = (tod >= 9 * 60 + 31) & (tod <= 16 * 60)
    is_on = (tod >= 18 * 60 + 1) | (tod <= 9 * 60 + 30)
    smap = {s: i for i, s in enumerate(sess_rth)}
    code = df["session"].map(smap).to_numpy()
    N = len(sess_rth)
    P(f"universe: {N:,} sessions with >=1 RTH bar in [{FIRST}, {LAST}]")

    hi = df["high"].to_numpy(float); lo = df["low"].to_numpy(float)
    op = df["open"].to_numpy(float); cl = df["close"].to_numpy(float)
    vol = df["volume"].to_numpy(float)

    # ---- whole-session facts (W51 taxonomy) + session VWAP (18:00-anchored)
    g = pd.DataFrame({"c": code, "h": hi, "l": lo, "o": op, "x": cl})
    agg = g.groupby("c").agg(sh=("h", "max"), sl=("l", "min"), so=("o", "first"), sx=("x", "last"))
    sess_h = agg["sh"].to_numpy(); sess_l = agg["sl"].to_numpy()
    sess_o = agg["so"].to_numpy(); sess_x = agg["sx"].to_numpy()
    body = sess_x - sess_o; rng_s = sess_h - sess_l
    trend = (rng_s > 1e-9) & (np.abs(body) >= 0.60 * rng_s)

    tp = (hi + lo + cl) / 3.0
    pv = pd.Series(tp * vol).groupby(code).cumsum().to_numpy()
    cv = pd.Series(vol).groupby(code).cumsum().to_numpy()
    with np.errstate(invalid="ignore", divide="ignore"):
        vwap_bar = np.where(cv > 0, pv / cv, np.nan)

    # ---- RTH grids
    slot = tod - (9 * 60 + 31)
    r = np.flatnonzero(is_rth)
    def grid(vals, fill=np.nan):
        gr = np.full((N, NSLOT), fill)
        gr[code[r], slot[r]] = vals[r]
        return gr
    hi_g = grid(hi); lo_g = grid(lo); cl_g = grid(cl); vw_g = grid(vwap_bar)
    op_g = grid(op)
    # RTH open = open of first RTH bar
    first_slot = np.where(np.isfinite(op_g).any(1), np.argmax(np.isfinite(op_g), 1), -1)
    assert (first_slot >= 0).all()
    open_rth = op_g[np.arange(N), first_slot]
    # RTH close = close of last RTH bar
    rev = np.isfinite(cl_g)[:, ::-1]
    last_slot = NSLOT - 1 - np.argmax(rev, 1)
    close_rth = cl_g[np.arange(N), last_slot]
    mh = np.nanmax(np.where(np.isfinite(hi_g), hi_g, -np.inf), 1)
    ml = np.nanmin(np.where(np.isfinite(lo_g), lo_g, np.inf), 1)

    # ffill session VWAP across RTH slots (within session)
    idx = np.where(np.isfinite(vw_g), np.arange(NSLOT)[None, :], -1)
    lastv = np.maximum.accumulate(idx, 1)
    vw_f = np.where(lastv >= 0, np.take_along_axis(vw_g, np.maximum(lastv, 0), 1), np.nan)

    # ---- overnight extremes
    o = np.flatnonzero(is_on)
    on_hi = np.full(N, np.nan); on_lo = np.full(N, np.nan)
    if len(o):
        ga = pd.DataFrame({"c": code[o], "h": hi[o], "l": lo[o]}).groupby("c").agg(
            h=("h", "max"), l=("l", "min"))
        on_hi[ga.index.to_numpy()] = ga["h"].to_numpy()
        on_lo[ga.index.to_numpy()] = ga["l"].to_numpy()
    has_on = np.isfinite(on_hi)

    # ---- IB (slots 0..59) and post-IB availability
    ib_hi = np.nanmax(np.where(np.isfinite(hi_g[:, :S_1031]), hi_g[:, :S_1031], -np.inf), 1)
    ib_lo = np.nanmin(np.where(np.isfinite(lo_g[:, :S_1031]), lo_g[:, :S_1031], np.inf), 1)
    has_ib = np.isfinite(ib_hi) & (ib_hi > -np.inf)
    ib_hi = np.where(has_ib, ib_hi, np.nan); ib_lo = np.where(has_ib, ib_lo, np.nan)
    has_post = np.isfinite(hi_g[:, S_1031:]).any(1)

    # ---- prior-RTH volume profile -> VAH/VAL/POC per session
    rr = r
    L = np.minimum(lo[rr], hi[rr]); H = np.maximum(lo[rr], hi[rr]); V = vol[rr]; C = code[rr]
    lob = np.floor(L / BIN).astype(np.int64); hib = np.floor(H / BIN).astype(np.int64)
    span = hib - lob + 1
    ridx = np.repeat(np.arange(len(rr)), span)
    offs = np.arange(span.sum()) - np.repeat(np.cumsum(span) - span, span)
    b = lob[ridx] + offs
    binlo = b * BIN; binhi = binlo + BIN
    width = H[ridx] - L[ridx]
    ovl = np.minimum(H[ridx], binhi) - np.maximum(L[ridx], binlo)
    w = np.where(width > 0, np.clip(ovl, 0, None) / np.where(width > 0, width, 1.0), 1.0 / span[ridx])
    pvol = pd.DataFrame({"c": C[ridx], "b": b, "v": V[ridx] * w}).groupby(["c", "b"])["v"].sum()
    vah = np.full(N, np.nan); val = np.full(N, np.nan); poc = np.full(N, np.nan)
    for c_, sub in pvol.groupby(level=0):
        bins = sub.index.get_level_values(1).to_numpy()
        vv = sub.to_numpy()
        tot = vv.sum()
        if tot <= 0:
            continue
        # dense array over occupied range
        b0, b1 = bins.min(), bins.max()
        dense = np.zeros(b1 - b0 + 1)
        dense[bins - b0] = vv
        mean_bin = float(np.sum((bins - b0) * vv) / tot)
        top = np.flatnonzero(dense == dense.max())
        p = int(top[np.argmin(np.abs(top - mean_bin))]) if len(top) > 1 else int(top[0])
        lo_i = hi_i = p; acc = dense[p]
        while acc < VA_FRAC * tot:
            below = dense[lo_i - 1] if lo_i > 0 else -1.0
            above = dense[hi_i + 1] if hi_i < len(dense) - 1 else -1.0
            if below < 0 and above < 0:
                break
            if below >= above:      # tie -> lower (frozen)
                lo_i -= 1; acc += dense[lo_i]
            else:
                hi_i += 1; acc += dense[hi_i]
        val[c_] = (b0 + lo_i) * BIN
        vah[c_] = (b0 + hi_i + 1) * BIN
        poc[c_] = (b0 + p) * BIN + BIN / 2
    prof_ok = np.isfinite(vah)

    # ---- level-offset objects (from each session's own RTH open; prior refs internal)
    dONH = on_hi - open_rth; dONL = on_lo - open_rth
    dIBH = ib_hi - open_rth; dIBL = ib_lo - open_rth
    dVAH = np.full(N, np.nan); dVAL = np.full(N, np.nan)
    dPDH = np.full(N, np.nan); dPDL = np.full(N, np.nan)
    dVAH[1:] = vah[:-1] - open_rth[1:]; dVAL[1:] = val[:-1] - open_rth[1:]
    dPDH[1:] = mh[:-1] - open_rth[1:]; dPDL[1:] = ml[:-1] - open_rth[1:]
    va_ok = np.zeros(N, bool); va_ok[1:] = prof_ok[:-1]
    pd_ok = np.zeros(N, bool); pd_ok[1:] = True
    dVW = vw_f - open_rth[:, None]

    # ---- path offset grids and CL6 forward-return grid
    mh_off = mh - open_rth; ml_off = ml - open_rth
    hi_off = hi_g - open_rth[:, None]; lo_off = lo_g - open_rth[:, None]
    cl_off = cl_g - open_rth[:, None]
    F = np.full((N, NSLOT), np.nan)                       # fwd 15-min bps at slot u
    valid_u = np.arange(NSLOT - FWD_MIN)
    with np.errstate(invalid="ignore", divide="ignore"):
        F[:, :NSLOT - FWD_MIN] = (cl_g[:, FWD_MIN:] / cl_g[:, :NSLOT - FWD_MIN] - 1.0) * 1e4
    ctrl_ok = (np.isfinite(F) & np.isfinite(lo_g) & np.isfinite(hi_g))
    ctrl_ok[:, :S_1001] = False; ctrl_ok[:, S_1545 + 1:] = False
    with np.errstate(invalid="ignore"):
        sess_ctrl_mean = np.where(ctrl_ok.any(1),
                                  np.nansum(np.where(ctrl_ok, F, 0.0), 1) / ctrl_ok.sum(1), np.nan)

    close_dir = np.sign(close_rth - open_rth)
    vwap59_ok = np.isfinite(dVW[:, S_0959])

    return dict(N=N, sess=sess_rth, open_rth=open_rth, close_rth=close_rth, mh=mh, ml=ml,
                mh_off=mh_off, ml_off=ml_off, hi_off=hi_off, lo_off=lo_off, cl_off=cl_off,
                has_on=has_on, dONH=dONH, dONL=dONL, on_hi=on_hi, on_lo=on_lo,
                has_ib=has_ib, has_post=has_post, dIBH=dIBH, dIBL=dIBL, ib_hi=ib_hi, ib_lo=ib_lo,
                va_ok=va_ok, dVAH=dVAH, dVAL=dVAL, vah=vah, val=val, poc=poc,
                pd_ok=pd_ok, dPDH=dPDH, dPDL=dPDL,
                dVW=dVW, vwap59_ok=vwap59_ok, trend=trend, close_dir=close_dir,
                F=F, ctrl_ok=ctrl_ok, sess_ctrl_mean=sess_ctrl_mean, cl_g=cl_g)


# ---------------------------------------------------------------------------- claim statistics
def crosses_zero(cl_off_slice, lvl_slice):
    d = cl_off_slice - lvl_slice
    s = np.where(np.isfinite(d) & (d != 0), np.sign(d), 0.0)
    n_valid = (s != 0).sum(1)
    pos = np.where(s != 0, np.arange(s.shape[1])[None, :], -1)
    last = np.maximum.accumulate(pos, 1)
    filled = np.where(last >= 0, np.take_along_axis(s, np.maximum(last, 0), 1), 0.0)
    ncross = ((filled[:, 1:] * filled[:, :-1]) == -1).sum(1)
    return ncross, n_valid


def all_stats(B, J, detail=False):
    """The seven frozen claim statistics for pairing J (J[i] = level-source session for path i)."""
    N = B["N"]
    out = {}
    D = {}

    # CL1
    e1 = B["has_on"][J]
    t1 = (B["mh_off"] >= B["dONH"][J]) | (B["ml_off"] <= B["dONL"][J])
    out["CL1_ON_touch"] = (float(t1[e1].mean()), int(e1.sum()), t1[e1])

    # CL2
    e2 = B["va_ok"][J]
    above = B["dVAH"][J] < 0
    below = B["dVAL"][J] > 0
    ent = np.where(above, B["ml_off"] <= B["dVAH"][J],
                   np.where(below, B["mh_off"] >= B["dVAL"][J], False))
    trv = np.where(above, B["ml_off"] <= B["dVAL"][J],
                   np.where(below, B["mh_off"] >= B["dVAH"][J], False))
    den2 = e2 & (above | below) & ent
    out["CL2_VA80_traversal"] = (float(trv[den2].mean()) if den2.any() else np.nan,
                                 int(den2.sum()), trv[den2])
    if detail:
        D["cl2"] = dict(open_out=(above | below) & e2, entered=den2, traversed=den2 & trv)

    # CL3
    e3 = B["has_ib"][J] & B["has_post"]
    up = B["hi_off"][:, S_1031:] > B["dIBH"][J][:, None]
    dn = B["lo_off"][:, S_1031:] < B["dIBL"][J][:, None]
    any_up = up.any(1); any_dn = dn.any(1)
    BIG = 10 ** 6
    t_up = np.where(any_up, np.argmax(up, 1), BIG)
    t_dn = np.where(any_dn, np.argmax(dn, 1), BIG)
    ext = any_up | any_dn
    out["CL3a_IB_extension"] = (float(ext[e3].mean()), int(e3.sum()), ext[e3])
    den3b = e3 & ext & (t_up != t_dn) & (B["close_dir"] != 0)
    brk = np.where(t_up < t_dn, 1.0, -1.0)
    agr = brk == B["close_dir"]
    out["CL3b_IBbreak_close_dir"] = (float(agr[den3b].mean()) if den3b.any() else np.nan,
                                     int(den3b.sum()), agr[den3b])
    if detail:
        D["cl3"] = dict(elig=e3, ext=ext, den3b=den3b, brk=brk, ambiguous=e3 & ext & (t_up == t_dn),
                        zero_close=e3 & ext & (t_up != t_dn) & (B["close_dir"] == 0))

    # CL4
    e4 = B["pd_ok"][J]
    t4 = (B["mh_off"] >= B["dPDH"][J]) | (B["ml_off"] <= B["dPDL"][J])
    out["CL4_PDHL_touch"] = (float(t4[e4].mean()), int(e4.sum()), t4[e4])

    # CL5
    lvl5 = B["dVW"][J][:, S_1100:]
    nc, nv = crosses_zero(B["cl_off"][:, S_1100:], lvl5)
    e5 = (nv >= 2)
    zc = nc == 0
    m5 = e5 & B["trend"]
    out["CL5_trend_zeroVWAPcross"] = (float(zc[m5].mean()) if m5.any() else np.nan,
                                      int(m5.sum()), zc[m5])
    out["CL5_uncond"] = (float(zc[e5].mean()), int(e5.sum()), zc[e5])
    if detail:
        D["cl5"] = dict(elig=e5, ncross=nc, zc=zc, trend=B["trend"])

    # CL6
    dist = B["cl_off"][:, S_0959] - B["dVW"][J][:, S_0959]
    cond = np.isfinite(dist) & (np.abs(dist) >= VWAP_DIST) & B["vwap59_ok"][J]
    side = np.sign(dist)
    lvl6 = B["dVW"][J][:, S_1000:S_1600]                # level at slot t uses vwap through t-1
    touch = (B["lo_off"][:, S_1001:] <= lvl6) & (B["hi_off"][:, S_1001:] >= lvl6)
    anyt = touch.any(1) & cond
    tslot = np.where(anyt, np.argmax(touch, 1) + S_1001, -1)
    scor = anyt & (tslot <= S_1545)
    ii = np.flatnonzero(scor)
    fwd = B["F"][ii, tslot[ii]]
    okf = np.isfinite(fwd)
    ii = ii[okf]; fwd = fwd[okf]
    sgn = side[ii] * fwd
    ctrl = side[ii] * B["sess_ctrl_mean"][ii]
    okc = np.isfinite(ctrl)
    stat6 = (float(sgn.mean() - ctrl[okc].mean()) if len(ii) and okc.any() else np.nan)
    out["CL6_VWAP_first_touch"] = (stat6, int(len(ii)), sgn)
    if detail:
        D["cl6"] = dict(cond=cond, anyt=anyt, tslot=tslot, ev_idx=ii, signed=sgn, raw=fwd,
                        side=side, dist=dist, ctrl_expect=float(ctrl[okc].mean()) if okc.any() else np.nan)
    return (out, D) if detail else out


# ---------------------------------------------------------------------------- main
def main():
    t0 = _time.time()
    P(f"python {sys.version.split()[0]}  numpy {np.__version__}  pandas {pd.__version__}")
    df = load()
    B = build(df)
    N = B["N"]
    del df

    # ---------------- observed (k=0, identity pairing)
    J0 = np.arange(N)
    obs, D0 = all_stats(B, J0, detail=True)

    # ---------------- null sensitivity FIRST (null_guard doctrine: a toothless null stops the run)
    P("")
    P("=" * 110)
    P(f"=== NULL SENSITIVITY (probe shifts {PROBES}) — verified BEFORE any percentile is quoted")
    P("=" * 110)
    probe_stats = {r: [obs[r][0]] for r in ROWS}
    for k in PROBES:
        st = all_stats(B, (J0 + k) % N)
        for r in ROWS:
            probe_stats[r].append(st[r][0])
    for r in ROWS:
        arr = np.array(probe_stats[r], float)
        spread = float(np.nanmax(arr) - np.nanmin(arr))
        P(f"    {r:<26} real {arr[0]:+.5f}  probes {[f'{v:+.5f}' for v in arr[1:]]}  spread {spread:.5f}")
        if not np.isfinite(spread) or spread <= 1e-12:
            raise SystemExit(f"DEFECT: null has no teeth for {r} — statistic invariant across probe shifts")
    P("    all 7 statistics move under level-set shifts — the pairing null has teeth")

    # ---------------- pairing null: 300 shared shifts
    P("")
    P("=" * 110)
    P(f"=== PAIRING NULL — {N_SHIFTS} distinct whole-session circular shifts of the LEVEL set, "
      f"seed {SEED_SHIFTS}; ONE shared shift per replication across all claims")
    P("=" * 110)
    rng = np.random.default_rng(SEED_SHIFTS)
    shifts = np.sort(rng.choice(np.arange(1, N), size=N_SHIFTS, replace=False))
    nullm = np.full((N_SHIFTS, len(ROWS)), np.nan)
    null_unc5 = np.full(N_SHIFTS, np.nan)
    for a, k in enumerate(shifts):
        st = all_stats(B, (J0 + int(k)) % N)
        for j, r in enumerate(ROWS):
            nullm[a, j] = st[r][0]
        null_unc5[a] = st["CL5_uncond"][0]
        if (a + 1) % 50 == 0:
            P(f"    replication {a + 1}/{N_SHIFTS}  [{_time.time() - t0:.0f}s]")
    n_nan = int(np.isnan(nullm).sum())
    P(f"    done: {N_SHIFTS} replications, {n_nan} NaN cell(s) across {N_SHIFTS * len(ROWS)}")

    med = np.nanmedian(nullm, 0)
    sd = np.nanstd(nullm, 0, ddof=1)
    if (sd <= 0).any():
        raise SystemExit("DEFECT: a claim's null distribution has zero spread — toothless")
    p025 = np.nanpercentile(nullm, 2.5, 0)
    p975 = np.nanpercentile(nullm, 97.5, 0)
    p50 = np.nanmedian(nullm, 0)
    zmat = (nullm - med[None, :]) / sd[None, :]
    fam = np.nanmax(np.abs(zmat), 1)                    # one shared shift per replication
    fam_p95 = float(np.percentile(fam[np.isfinite(fam)], 95))
    obs_v = np.array([obs[r][0] for r in ROWS])
    z = (obs_v - med) / sd

    # ---------------- observed CIs (session-clustered = across-session; one datum/session)
    ci = {}
    for r in ROWS:
        v, n, samp = obs[r]
        samp = np.asarray(samp, float)
        se = float(np.std(samp, ddof=1) / math.sqrt(len(samp))) if len(samp) > 1 else np.nan
        ci[r] = (v - Z95 * se, v + Z95 * se, se, n)

    # ---------------- CL6 W111b full control draws (observed alignment)
    ii = D0["cl6"]["ev_idx"]; side = D0["cl6"]["side"]
    rngc = np.random.default_rng(SEED_CTRL)
    draw_tot = np.zeros(N_CTRL_DRAWS)
    for i in ii:
        u = np.flatnonzero(B["ctrl_ok"][i])
        picks = u[rngc.integers(len(u), size=N_CTRL_DRAWS)]
        draw_tot += side[i] * B["F"][i, picks]
    draw_means = draw_tot / len(ii)
    c_p50, c_p95 = float(np.percentile(draw_means, 50)), float(np.percentile(draw_means, 95))
    ctrl_expect = D0["cl6"]["ctrl_expect"]
    ev_mean_signed = float(D0["cl6"]["signed"].mean())
    ev_mean_raw = float(D0["cl6"]["raw"].mean())

    # ---------------- classification
    classi = {}
    for j, r in enumerate(ROWS):
        v = obs_v[j]
        outside_hi = v > p975[j]
        outside_lo = v < p025[j]
        fam_ok = abs(z[j]) > fam_p95
        d = CLAIM_DIR[r]
        if (outside_hi if d > 0 else outside_lo) and fam_ok:
            classi[r] = "SUPPORTED-BEYOND-GEOMETRY"
        elif (outside_lo if d > 0 else outside_hi) and fam_ok:
            classi[r] = "REFUTED"
        elif outside_hi or outside_lo:
            classi[r] = "GEOMETRY-EXPLAINED (band-outside but inside family bar; direction "
            classi[r] += "claim-side)" if (outside_hi if d > 0 else outside_lo) else "opposite)"
        else:
            classi[r] = "GEOMETRY-EXPLAINED"

    # ---------------- gate table
    G_lines = []
    A = G_lines.append
    A("G2_F2_CLAIMS01_20260829 — CLAIM REGISTER GATE TABLE (printed by program; trial G00021)")
    A(f"population: {N:,} NQ sessions 2022-01-01..2026-07-31 (session unit 18:00->17:00 ET; RTH bars "
      f"stamped 09:31..16:00); pairing null = {N_SHIFTS} whole-session circular shifts of the LEVEL "
      f"set vs unshifted paths, one shared shift/replication; family bar = p95 of max |z| over 7 rows")
    A("evidence status: DISCOVERY_CONSUMED (window includes burned 2026-05-31..07-31; no sealed reads)")
    A("no strategy, no P&L, no threshold search — descriptive claim register only")
    A("")
    A(f"    null sensitivity: VERIFIED FIRST — all 7 statistics moved across probe shifts {PROBES}")
    A(f"    family max-|z| p95 over {N_SHIFTS} replications = {fam_p95:.3f} "
      f"(a claim is SUPPORTED or REFUTED only if its |z| exceeds this)")
    A("")
    A("MDEs (printed BEFORE verdicts; 2.80*SE, ~80% power two-sided 5%; units of each stat):")
    for j, r in enumerate(ROWS):
        lo_, hi_, se, n = ci[r]
        A(f"    {r:<26} n={n:>5,}  SE={se:.5f}  MDE={MDE_K * se:.5f}")
    A("")
    hdr = f"{'CLAIM':<26}{'OBSERVED [95% CI]':<34}{'NULL p50 [p2.5,p97.5]':<32}{'z':>8}  CLASSIFICATION"
    A(hdr)
    A("-" * len(hdr))
    for j, r in enumerate(ROWS):
        v = obs_v[j]; lo_, hi_, se, n = ci[r]
        A(f"{r:<26}{f'{v:+.4f} [{lo_:+.4f},{hi_:+.4f}] n={n:,}':<34}"
          f"{f'{p50[j]:+.4f} [{p025[j]:+.4f},{p975[j]:+.4f}]':<32}{z[j]:>+8.2f}  {classi[r]}")
    A("")
    A("controls / diagnostics (same wave, matched):")
    u5o, u5n, _ = obs["CL5_uncond"]
    A(f"    CL5 UNCONDITIONAL P(zero crosses) = {u5o:+.4f} (n={u5n:,})  null p50 "
      f"{float(np.nanmedian(null_unc5)):+.4f} [{float(np.nanpercentile(null_unc5, 2.5)):+.4f},"
      f"{float(np.nanpercentile(null_unc5, 97.5)):+.4f}]   <- matched unconditional control for CL5")
    A(f"    CL6 event mean (signed) {ev_mean_signed:+.3f} bps; raw unsigned mean {ev_mean_raw:+.3f} bps; "
      f"analytic same-session count-matched control expectation {ctrl_expect:+.3f} bps")
    A(f"    CL6 W111b control draws ({N_CTRL_DRAWS}, seed {SEED_CTRL}): p50 {c_p50:+.3f}, p95 {c_p95:+.3f} bps; "
      f"claim stat = event mean - control expectation = {obs_v[6]:+.3f} bps")
    A(f"    CL3b exclusions: ambiguous same-slot double-breach {int(D0['cl3']['ambiguous'].sum())}, "
      f"zero close-dir {int(D0['cl3']['zero_close'].sum())}")
    A(f"    CL6 population: cond(|09:59 dist|>=20pt) {int(D0['cl6']['cond'].sum())} sessions; "
      f"first touch found {int(D0['cl6']['anyt'].sum())}; scored (<=15:45, fwd computable) {len(ii)}")
    A("")
    n_sup = sum(1 for r in ROWS if classi[r].startswith("SUPPORTED"))
    n_ref = sum(1 for r in ROWS if classi[r] == "REFUTED")
    n_geo = len(ROWS) - n_sup - n_ref
    A(f"VERDICT: {n_sup} SUPPORTED-BEYOND-GEOMETRY / {n_geo} GEOMETRY-EXPLAINED / {n_ref} REFUTED "
      f"(7 rows, 6 claims; family-corrected)")
    table = "\n".join(G_lines)
    P("")
    P(table)
    with open(os.path.join(OUT, "gate_table.txt"), "wb") as f:
        f.write(table.encode("utf-8"))

    # ---------------- claim_details
    sess_iso = pd.Series([s.isoformat() for s in B["sess"]])
    pd.DataFrame({"session": sess_iso, "on_high": B["on_hi"], "on_low": B["on_lo"],
                  "rth_open": B["open_rth"], "eligible": B["has_on"],
                  "touched": (B["mh_off"] >= B["dONH"]) | (B["ml_off"] <= B["dONL"])
                  }).to_csv(os.path.join(DET, "cl1_sessions.csv"), index=False)
    pd.DataFrame({"session": sess_iso, "prior_vah": B["dVAH"] + B["open_rth"],
                  "prior_val": B["dVAL"] + B["open_rth"], "rth_open": B["open_rth"],
                  "open_outside": D0["cl2"]["open_out"], "entered": D0["cl2"]["entered"],
                  "traversed": D0["cl2"]["traversed"]
                  }).to_csv(os.path.join(DET, "cl2_sessions.csv"), index=False)
    pd.DataFrame({"session": sess_iso, "ib_high": B["ib_hi"], "ib_low": B["ib_lo"],
                  "eligible": D0["cl3"]["elig"], "extended": D0["cl3"]["ext"],
                  "in_3b": D0["cl3"]["den3b"], "first_break_up": D0["cl3"]["brk"] > 0,
                  "close_dir": B["close_dir"]
                  }).to_csv(os.path.join(DET, "cl3_sessions.csv"), index=False)
    pd.DataFrame({"session": sess_iso, "pdh": B["dPDH"] + B["open_rth"],
                  "pdl": B["dPDL"] + B["open_rth"], "eligible": B["pd_ok"],
                  "touched": (B["mh_off"] >= B["dPDH"]) | (B["ml_off"] <= B["dPDL"])
                  }).to_csv(os.path.join(DET, "cl4_sessions.csv"), index=False)
    pd.DataFrame({"session": sess_iso, "trend_day": B["trend"], "eligible": D0["cl5"]["elig"],
                  "n_crosses_after_1100": D0["cl5"]["ncross"], "zero_crosses": D0["cl5"]["zc"]
                  }).to_csv(os.path.join(DET, "cl5_sessions.csv"), index=False)
    ev = pd.DataFrame({"session": sess_iso.iloc[ii].to_numpy(),
                       "side": side[ii].astype(int),
                       "dist_0959_pts": D0["cl6"]["dist"][ii],
                       "touch_slot": D0["cl6"]["tslot"][ii],
                       "fwd15_bps_raw": D0["cl6"]["raw"],
                       "fwd15_bps_signed": D0["cl6"]["signed"]})
    ev.to_csv(os.path.join(DET, "cl6_events.csv"), index=False)
    nd = pd.DataFrame(nullm, columns=ROWS)
    nd.insert(0, "shift_k", shifts)
    nd["CL5_uncond"] = null_unc5
    nd.to_csv(os.path.join(DET, "null_distributions.csv"), index=False)
    pd.DataFrame({"row": ROWS, "observed": obs_v,
                  "ci_lo": [ci[r][0] for r in ROWS], "ci_hi": [ci[r][1] for r in ROWS],
                  "n": [ci[r][3] for r in ROWS], "se": [ci[r][2] for r in ROWS],
                  "mde": [MDE_K * ci[r][2] for r in ROWS],
                  "null_p50": p50, "null_p025": p025, "null_p975": p975, "null_sd": sd,
                  "z": z, "family_p95": fam_p95,
                  "classification": [classi[r] for r in ROWS]
                  }).to_csv(os.path.join(DET, "summary.csv"), index=False)

    # ---------------- ledger result (pending — ledger itself NOT appended)
    ledger = {
        "trial_id": "G00021",
        "metrics": {
            "window": "2022-01-01..2026-07-31 sessions",
            "n_sessions": int(N),
            "n_null_replications": int(N_SHIFTS),
            "family_maxz_p95": round(fam_p95, 3),
            "evidence_status": "DISCOVERY_CONSUMED",
            "rows": {r: {"observed": round(float(obs_v[j]), 5),
                         "n": int(ci[r][3]),
                         "se": round(float(ci[r][2]), 5),
                         "mde": round(float(MDE_K * ci[r][2]), 5),
                         "null_p50": round(float(p50[j]), 5),
                         "null_band_p025_p975": [round(float(p025[j]), 5), round(float(p975[j]), 5)],
                         "z": round(float(z[j]), 3),
                         "classification": classi[r]} for j, r in enumerate(ROWS)},
            "cl5_uncond_control": {"observed": round(float(u5o), 5),
                                   "null_p50": round(float(np.nanmedian(null_unc5)), 5)},
            "cl6_detail": {"event_mean_signed_bps": round(ev_mean_signed, 4),
                           "event_mean_raw_bps": round(ev_mean_raw, 4),
                           "ctrl_expect_bps": round(ctrl_expect, 4),
                           "w111b_draws_p50_bps": round(c_p50, 4),
                           "w111b_draws_p95_bps": round(c_p95, 4),
                           "n_events_scored": int(len(ii))},
        },
        "result": f"REGISTER-COMPLETE: {n_sup} SUPPORTED-BEYOND-GEOMETRY / {n_geo} GEOMETRY-EXPLAINED / "
                  f"{n_ref} REFUTED (7 rows, family max-|z| corrected)",
        "note": ("Directive §45 descriptive claim register — 6 auction/level practitioner claims vs a "
                 "dependence-preserving pairing null (circular shift of per-session level-offset "
                 "objects vs unshifted paths, one shared shift/replication; sensitivity verified "
                 "first). CL6 signed by 09:59 side with W111b count-matched same-session control. "
                 "No strategy, no P&L; substrate hash matches provenance; all loads seal-guarded. "
                 "Resolutions in out/spec_resolutions.txt."),
    }
    with open(os.path.join(OUT, "ledger_result_pending.json"), "wb") as f:
        f.write(json.dumps(ledger, indent=2).encode("utf-8"))

    try:
        import psutil
        peak = psutil.Process().memory_info().peak_wset / 1e9
        P(f"\npeak_gb {peak:.3f}")
    except Exception:
        P("\npeak_gb not measured (psutil unavailable)")
    P(f"wall_s {int(_time.time() - t0)}")
    P("outputs: gate_table.txt, claim_details/ (7 csv), ledger_result_pending.json")
    _log.close()


if __name__ == "__main__":
    main()
