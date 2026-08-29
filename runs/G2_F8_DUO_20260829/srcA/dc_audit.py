"""G2_F8_DUO sub-run A — MC-43 DC intrinsic-time audit (trial G00037).

Executable spec = outA/spec_resolutions.txt (frozen BEFORE this file ran on real data).
Three legs: (a) mean(omega)/delta per era, PASS=[0.8,1.2] all cells;
(b) var(omega)/delta^2 vs session-vol-matched Brownian SIMULATION (stated: simulation)
    + analytic continuous-limit reference (1.0) + circular-shift empirical null;
(c) DC-share vs 0.632 with block-bootstrap CI + ONE preregistered conditional
    (top/bottom-decile |d(t)| sessions vs era+vol MATCHED control, hazard-slope beta).
Gate tables printed BY PROGRAM. MDEs before verdicts. seal_guard on load. $0. No trades.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time as _time
from datetime import date

import numpy as np
import pandas as pd
from numba import njit

sys.path.insert(0, r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research")
from research_sdk.seal_guard import assert_presealed  # noqa: E402

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
PARQ = os.path.join(ROOT, r"research\scalping_lab\substrate\minute\NQ\nq1m_2005_202605.parquet")
OUTA = os.path.join(ROOT, r"runs\G2_F8_DUO_20260829\outA")

DELTAS = np.array([0.001, 0.002, 0.004, 0.008, 0.016])  # log units (0.1..1.6%)
DELTA_COND = 0.002
ANALYTIC_SHARE = 1.0 - 1.0 / np.e  # 0.63212
ERA_EDGES = [(date(2006, 1, 1), date(2015, 12, 31)), (date(2016, 1, 1), date(2022, 12, 31)),
             (date(2023, 1, 1), date(2026, 5, 31))]
ERA_NAMES = ["2006-15", "2016-22", "2023-26"]
K_SIM = 20
K_SHIFT = 20
K_LABEL = 500
B_BOOT = 1000
L_MEAN = 100
L_SHARE = 250
ROLL_W = 250
SEED = 20260829


# ------------------------------------------------------------------ DC kernel
@njit(cache=True)
def dc_pass(logp, delta):
    """Glattfelder-Dupuis-Olsen dissection on closes. Returns segment + event arrays.

    seg_conf[i]: bar index of the DC confirmation that STARTED segment i
    seg_omega[i]: overshoot (log units) of segment i; seg_nos[i]=floor(omega/delta)
    ev_idx / ev_isdc: chronological intrinsic event stream (DC + OS events)
    """
    n = logp.size
    sumabs = 0.0
    for i in range(1, n):
        d = logp[i] - logp[i - 1]
        sumabs += d if d > 0 else -d
    cap_seg = int(sumabs / delta) + 16
    cap_ev = int(2.0 * sumabs / delta) + 32
    seg_conf = np.empty(cap_seg, np.int64)
    seg_omega = np.empty(cap_seg, np.float64)
    seg_nos = np.empty(cap_seg, np.int64)
    ev_idx = np.empty(cap_ev, np.int64)
    ev_isdc = np.empty(cap_ev, np.uint8)
    ns = 0
    ne = 0
    mode = 1  # start scanning as uptrend (first segment has no pc -> discarded)
    ext = logp[0]
    have_pc = False
    pc = 0.0
    pc_i = -1
    osc = 0
    for i in range(1, n):
        p = logp[i]
        if mode == 1:
            if p > ext:
                ext = p
                if have_pc:
                    while p >= pc + (osc + 1) * delta:
                        osc += 1
                        ev_idx[ne] = i
                        ev_isdc[ne] = 0
                        ne += 1
            if p <= ext - delta:
                if have_pc:
                    seg_conf[ns] = pc_i
                    seg_omega[ns] = ext - pc
                    seg_nos[ns] = osc
                    ns += 1
                pc = p
                pc_i = i
                have_pc = True
                osc = 0
                ev_idx[ne] = i
                ev_isdc[ne] = 1
                ne += 1
                mode = -1
                ext = p
        else:
            if p < ext:
                ext = p
                while p <= pc - (osc + 1) * delta:
                    osc += 1
                    ev_idx[ne] = i
                    ev_isdc[ne] = 0
                    ne += 1
            if p >= ext + delta:
                seg_conf[ns] = pc_i
                seg_omega[ns] = pc - ext
                seg_nos[ns] = osc
                ns += 1
                pc = p
                pc_i = i
                have_pc = True
                osc = 0
                ev_idx[ne] = i
                ev_isdc[ne] = 1
                ne += 1
                mode = 1
                ext = p
    return (seg_conf[:ns].copy(), seg_omega[:ns].copy(), seg_nos[:ns].copy(),
            ev_idx[:ne].copy(), ev_isdc[:ne].copy())


# ------------------------------------------------------- vectorized bootstraps
def block_boot_mean_ci(x, L, B, rng):
    """Circular block bootstrap percentile 95% CI for the mean of x."""
    n = x.size
    if n < 3:
        return np.nan, np.nan, np.nan
    Le = min(L, n)
    m = int(np.ceil(n / Le))
    xw = np.concatenate([x, x[:Le]])
    pref = np.concatenate([[0.0], np.cumsum(xw)])
    starts = rng.integers(0, n, size=(B, m))
    bsums = pref[starts + Le] - pref[starts]
    means = bsums.sum(axis=1) / (m * Le)
    lo, hi = np.percentile(means, [2.5, 97.5])
    return float(lo), float(hi), float(means.std())


def wls_hazard_beta(D, R):
    """Weighted-LS slope of h(k)=D_k/R_k on k (k=0..4), weights R_k."""
    ks, hs, ws = [], [], []
    for k in range(5):
        if R[k] > 0:
            ks.append(float(k))
            hs.append(D[k] / R[k])
            ws.append(float(R[k]))
    if len(ks) < 2:
        return np.nan
    k = np.array(ks)
    h = np.array(hs)
    w = np.array(ws)
    kb = (w * k).sum() / w.sum()
    hb = (w * h).sum() / w.sum()
    den = (w * (k - kb) ** 2).sum()
    return float((w * (k - kb) * (h - hb)).sum() / den) if den > 0 else np.nan


def hist_to_DR(hist):
    """hist: [...,6] counts of N=0..4 exact + total. Return D_k,R_k arrays k=0..4."""
    tot = hist[..., 5]
    D = hist[..., 0:5]
    cum = np.cumsum(D, axis=-1)
    R = np.empty_like(D)
    R[..., 0] = tot
    R[..., 1:] = tot[..., None] - cum[..., :-1]
    return D, R


def nn_match(class_idx, pool_idx, vol, era):
    """Era-constrained nearest-neighbor (log trailing vol) match without replacement.

    Nearest unused neighbor = nearer of (closest unused left, closest unused right)
    in the era's vol-sorted pool. Class processed in given (chronological) order.
    """
    matched = np.full(class_idx.size, -1, dtype=np.int64)
    for e in np.unique(era[class_idx]):
        cls_pos = np.where(era[class_idx] == e)[0]
        pool = pool_idx[era[pool_idx] == e]
        if pool.size == 0:
            continue
        pv = np.log(vol[pool])
        order = np.argsort(pv, kind="stable")
        pool_s = pool[order]
        pv_s = pv[order]
        used = np.zeros(pool_s.size, dtype=bool)
        for j in cls_pos:
            t = np.log(vol[class_idx[j]])
            pos = np.searchsorted(pv_s, t)
            left = pos - 1
            while left >= 0 and used[left]:
                left -= 1
            right = pos
            while right < pool_s.size and used[right]:
                right += 1
            dl = t - pv_s[left] if left >= 0 else np.inf
            dr = pv_s[right] - t if right < pool_s.size else np.inf
            if not np.isfinite(dl) and not np.isfinite(dr):
                continue
            best = left if dl <= dr else right
            used[best] = True
            matched[j] = pool_s[best]
    return matched


# ------------------------------------------------------------------ pipeline
def load_real():
    df = pd.read_parquet(PARQ)
    df["time"] = pd.to_datetime(df["time"])
    assert_presealed(df, "time", "G2_F8_DUO_A load nq1m substrate")
    df = df.sort_values("time").drop_duplicates("time", keep="first")
    df = df[np.isfinite(df["close"]) & (df["close"] > 0)].reset_index(drop=True)
    ts = df["time"]
    sess_date = ts.dt.date.where(ts.dt.hour <= 17, (ts + pd.Timedelta(days=1)).dt.date)
    # END-stamped: bar stamped exactly 18:00 belongs to next session per >17:00 rule
    codes, uniq = pd.factorize(sess_date, sort=True)
    logp = np.log(df["close"].to_numpy())
    return logp, codes.astype(np.int64), np.array(uniq), ts


def session_arrays(logp, sess_id, sess_dates):
    n_sess = sess_dates.size
    r = np.diff(logp, prepend=logp[0])
    r[0] = 0.0
    first = np.zeros(logp.size, dtype=bool)
    first[0] = True
    first[1:] = sess_id[1:] != sess_id[:-1]
    gap = first.copy()  # first return of a session is the gap return
    rv = np.zeros(n_sess)
    sig = np.zeros(n_sess)
    nb = np.bincount(sess_id, minlength=n_sess)
    r2 = r * r
    intr = ~gap
    rv_all = np.bincount(sess_id, weights=r2, minlength=n_sess)
    rv = np.sqrt(rv_all)  # realized vol incl gap (matching variable)
    s1 = np.bincount(sess_id[intr], weights=r[intr], minlength=n_sess)
    s2 = np.bincount(sess_id[intr], weights=r2[intr], minlength=n_sess)
    cnt = np.bincount(sess_id[intr], minlength=n_sess)
    with np.errstate(invalid="ignore", divide="ignore"):
        mu = np.where(cnt > 0, s1 / np.maximum(cnt, 1), 0.0)
        var = np.where(cnt > 1, s2 / np.maximum(cnt, 1) - mu ** 2, 0.0)
    sig = np.sqrt(np.maximum(var, 0.0))
    era = np.full(n_sess, -1, dtype=np.int64)
    for k, (a, b) in enumerate(ERA_EDGES):
        m = (sess_dates >= a) & (sess_dates <= b)
        era[m] = k
    trail20 = np.full(n_sess, np.nan)
    c = pd.Series(rv).rolling(20).mean().shift(1).to_numpy()
    trail20 = c
    return r, gap, rv, sig, era, trail20, nb


def rebuild(logp0, r):
    return logp0 + np.cumsum(np.concatenate([[0.0], r[1:]]))


def stats_one_pass(logp, sess_id, era_sess, deltas):
    """Per delta: n_seg, mean w/d, var w/d2, share, plus per-era versions."""
    out = {}
    for d in deltas:
        sc, om, nos, ei, ed = dc_pass(logp, d)
        wd = om / d
        e_seg = era_sess[sess_id[sc]]
        e_ev = era_sess[sess_id[ei]]
        row = {"n_seg": int(sc.size), "mean": float(wd.mean()) if sc.size else np.nan,
               "var": float(wd.var()) if sc.size else np.nan,
               "share": float(ed.mean()) if ei.size else np.nan, "era": {}}
        for k in range(3):
            m = e_seg == k
            me = e_ev == k
            row["era"][k] = {"n": int(m.sum()),
                             "mean": float(wd[m].mean()) if m.any() else np.nan,
                             "var": float(wd[m].var()) if m.any() else np.nan,
                             "share": float(ed[me].mean()) if me.any() else np.nan}
        out[d] = row
    return out


def main(selftest=False):
    t0 = _time.time()
    rng = np.random.default_rng(SEED)
    if selftest:
        # synthetic GBM: validate engine against analytic values (no real data touched)
        n = 2_000_000
        lp = np.cumsum(rng.normal(0, 3e-4, n))
        for d in [0.002, 0.004]:
            sc, om, nos, ei, ed = dc_pass(lp, d)
            print(f"SELFTEST delta={d}: n_seg={sc.size} mean(w)/d={om.mean()/d:.4f} "
                  f"var(w)/d2={om.var()/d**2:.4f} share={ed.mean():.4f} "
                  f"(analytic 1.0 / 1.0 / {ANALYTIC_SHARE:.4f})")
        # hazard flatness on GBM
        cnt = np.bincount(np.minimum(nos, 5), minlength=6)
        h = [cnt[k] / cnt[k:].sum() for k in range(5)]
        print("SELFTEST hazard h(0..4):", np.round(h, 4), " (analytic const 0.6321)")
        return

    logp, sess_id, sess_dates, ts = load_real()
    n_bars = logp.size
    r, gap, rv, sig, era_s, trail20, nb = session_arrays(logp, sess_id, sess_dates)
    n_sess = sess_dates.size
    print(f"bars={n_bars} sessions={n_sess} span={sess_dates[0]}..{sess_dates[-1]}")
    with open(os.path.join(OUTA, "run_provenance.txt"), "w") as f:
        h = hashlib.sha256(open(PARQ, "rb").read()).hexdigest()
        f.write("G2_F8_DUO_20260829 sub-run A input provenance (printed by program)\n")
        f.write(f"python {sys.version.split()[0]} numpy {np.__version__} pandas {pd.__version__}\n")
        f.write(f"  {h}  {os.path.getsize(PARQ)} B  {PARQ}\n")
        f.write(f"  bars={n_bars} sessions={n_sess} span={sess_dates[0]}..{sess_dates[-1]}\n")

    # ---- REAL pass, all deltas (keep delta_cond details for conditional leg)
    real = {}
    keep = {}
    for d in DELTAS:
        sc, om, nos, ei, ed = dc_pass(logp, d)
        real[d] = (sc, om, nos, ei, ed)
        if abs(d - DELTA_COND) < 1e-12:
            keep = {"sc": sc, "om": om, "nos": nos, "ei": ei, "ed": ed}
    real_stats = {d: None for d in DELTAS}
    for d in DELTAS:
        sc, om, nos, ei, ed = real[d]
        wd = om / d
        e_seg = era_s[sess_id[sc]]
        e_ev = era_s[sess_id[ei]]
        real_stats[d] = {"n_seg": int(sc.size), "mean": float(wd.mean()),
                         "var": float(wd.var()), "share": float(ed.mean()),
                         "n_ev": int(ei.size), "era": {}}
        for k in range(3):
            m = e_seg == k
            me = e_ev == k
            real_stats[d]["era"][k] = {"n": int(m.sum()), "mean": float(wd[m].mean()),
                                       "var": float(wd[m].var()), "share": float(ed[me].mean())}
    print(f"real DC pass done {_time.time()-t0:.0f}s")

    # ---- leg (a) bootstrap CIs per era per delta; leg (c) share CIs
    rngA = np.random.default_rng(rng.integers(2**63))
    ciA, ciC = {}, {}
    for d in DELTAS:
        sc, om, nos, ei, ed = real[d]
        wd = om / d
        e_seg = era_s[sess_id[sc]]
        e_ev = era_s[sess_id[ei]]
        ciA[d] = {}
        for k in range(3):
            ciA[d][k] = block_boot_mean_ci(wd[e_seg == k], L_MEAN, B_BOOT, rngA)
        lo, hi, sd = block_boot_mean_ci(ed[:].astype(float), L_SHARE, B_BOOT, rngA)
        ciC[d] = {"full": (lo, hi, sd), "era": {}}
        for k in range(3):
            ciC[d]["era"][k] = block_boot_mean_ci(ed[e_ev == k].astype(float), L_SHARE, B_BOOT, rngA)

    # ---- Brownian null by SIMULATION (session-vol matched, real gaps kept), K_SIM reps
    rngS = np.random.default_rng(rng.integers(2**63))
    sim_rows = []
    sig_bar = sig[sess_id]  # per-bar sigma of its session
    for rep in range(K_SIM):
        rs = np.where(gap, r, rngS.normal(0.0, 1.0, n_bars) * sig_bar)
        lp = rebuild(logp[0], rs)
        sim_rows.append(stats_one_pass(lp, sess_id, era_s, DELTAS))
    print(f"sim null done {_time.time()-t0:.0f}s")

    # ---- circular-shift empirical null (within-session rotation, shared offset/session)
    rngC = np.random.default_rng(rng.integers(2**63))
    shift_rows = []
    sess_starts = np.searchsorted(sess_id, np.arange(n_sess))
    sess_ends = np.append(sess_starts[1:], n_bars)
    for rep in range(K_SHIFT):
        rs = r.copy()
        offs = rngC.integers(1, 10**9, size=n_sess)
        for s in range(n_sess):
            a, b = sess_starts[s], sess_ends[s]
            if b - a > 2:
                seg = rs[a + 1:b]  # non-gap returns
                rs[a + 1:b] = np.roll(seg, int(offs[s] % seg.size))
        lp = rebuild(logp[0], rs)
        shift_rows.append(stats_one_pass(lp, sess_id, era_s, DELTAS))
    print(f"circular-shift null done {_time.time()-t0:.0f}s")

    def agg(rows, d, key, erak=None):
        if erak is None:
            v = np.array([rw[d][key] for rw in rows])
        else:
            v = np.array([rw[d]["era"][erak][key] for rw in rows])
        return float(np.nanmean(v)), float(np.nanstd(v))

    # ---- scaling-law slope logN(delta) vs log(delta)
    logN = np.log10([real_stats[d]["n_seg"] for d in DELTAS])
    slope_real = float(np.polyfit(np.log10(DELTAS), logN, 1)[0])
    slopes_sim = [float(np.polyfit(np.log10(DELTAS),
                  np.log10([rw[d]["n_seg"] for d in DELTAS]), 1)[0]) for rw in sim_rows]

    # ---- CONDITIONAL LEG at delta_cond -------------------------------------
    sc, om, nos, ei, ed = keep["sc"], keep["om"], keep["nos"], keep["ei"], keep["ed"]
    ev_sess = sess_id[ei]
    roll = pd.Series(ed.astype(float)).rolling(ROLL_W).mean().to_numpy()
    # last event strictly before each session's open == last event in a session < s
    last_before = np.searchsorted(ev_sess, np.arange(n_sess), side="left") - 1
    d_sess = np.full(n_sess, np.nan)
    ok = last_before >= ROLL_W - 1
    d_sess[ok] = roll[last_before[ok]] - ANALYTIC_SHARE
    elig = np.where(np.isfinite(d_sess) & np.isfinite(trail20) & (trail20 > 0) & (era_s >= 0))[0]
    absd = np.abs(d_sess[elig])
    q_hi, q_lo = np.quantile(absd, 0.9), np.quantile(absd, 0.1)
    dev_idx = elig[absd >= q_hi]
    conf_idx = elig[absd <= q_lo]
    # per-session segment-N histograms (N=0..4 exact + total), keyed by conf-bar session
    seg_sess = sess_id[sc]
    hist = np.zeros((n_sess, 6))
    np.add.at(hist, (seg_sess, np.minimum(nos, 5)), 1.0)  # cols 0..4 exact N, col5 = N>=5
    tot = hist.sum(axis=1)
    hist[:, 5] = tot  # col5 := TOTAL segments (hist_to_DR needs D_0..4 exact + total)
    H = hist

    def beta_of(sessions):
        D, R = hist_to_DR(H[sessions].sum(axis=0))
        return wls_hazard_beta(D, R), D, R

    pool_dev = elig[~np.isin(elig, dev_idx)]
    pool_conf = elig[~np.isin(elig, conf_idx)]
    m_dev = nn_match(dev_idx, pool_dev, trail20, era_s)
    m_conf = nn_match(conf_idx, pool_conf, trail20, era_s)
    ok_d = m_dev >= 0
    ok_c = m_conf >= 0
    dev_u, ctl_d = dev_idx[ok_d], m_dev[ok_d]
    conf_u, ctl_c = conf_idx[ok_c], m_conf[ok_c]
    b_dev, D_dev, R_dev = beta_of(dev_u)
    b_ctld, _, _ = beta_of(ctl_d)
    b_conf, _, _ = beta_of(conf_u)
    b_ctlc, _, _ = beta_of(ctl_c)
    b_unc, D_unc, R_unc = beta_of(elig)
    delta_dev = abs(b_dev) - abs(b_ctld)
    delta_conf = abs(b_conf) - abs(b_ctlc)

    # pair bootstrap for Delta (B=1000)
    rngB = np.random.default_rng(rng.integers(2**63))
    def pair_boot(cls, ctl):
        n = cls.size
        out = np.empty(B_BOOT)
        for b in range(B_BOOT):
            pick = rngB.integers(0, n, n)
            bd, _, _ = beta_of(cls[pick])
            bc, _, _ = beta_of(ctl[pick])
            out[b] = abs(bd) - abs(bc)
        return out
    boot_dev = pair_boot(dev_u, ctl_d)
    boot_conf = pair_boot(conf_u, ctl_c)

    # label-shift null (K_LABEL circular shifts of class labels over ordered elig sessions)
    rngL = np.random.default_rng(rng.integers(2**63))
    n_el = elig.size
    is_dev = np.isin(elig, dev_idx)
    null_beta, null_delta = [], []
    offsets = rngL.choice(np.arange(1, n_el), size=K_LABEL, replace=False) \
        if n_el - 1 >= K_LABEL else rngL.integers(1, n_el, K_LABEL)
    for off in offsets:
        lab = np.roll(is_dev, int(off))
        cls = elig[lab]
        pool = elig[~lab]
        mm = nn_match(cls, pool, trail20, era_s)
        okm = mm >= 0
        bD, _, _ = beta_of(cls[okm])
        bC, _, _ = beta_of(mm[okm])
        null_beta.append(bD)
        null_delta.append(abs(bD) - abs(bC))
    null_beta = np.array(null_beta)
    null_delta = np.array(null_delta)
    nb_lo, nb_hi = np.percentile(null_beta, [2.5, 97.5])
    nd95 = np.percentile(null_delta, 95)
    print(f"conditional leg done {_time.time()-t0:.0f}s")

    # =================================================================== PRINT
    lines = []
    P = lines.append
    P("=" * 100)
    P("G2_F8_DUO_20260829 / SUB-RUN A — MC-43 DC INTRINSIC-TIME AUDIT (trial G00037)")
    P("NQ 1-min closes, sessions %s..%s, %d bars, %d sessions. POINTS/normalized units. No trades."
      % (sess_dates[0], sess_dates[-1], n_bars, n_sess))
    P("Back-adjusted-substrate caveat: %%-delta on adjusted prices differs from %%-of-spot in early eras;")
    P("audited quantities are ratio laws (omega/delta, share) — locally offset-invariant; era cells stand on their own.")
    P("Brownian null: BY SIMULATION, zero-drift Gaussian, per-session vol matched, real gaps kept, K=%d." % K_SIM)
    P("Analytic continuous-limit references: E[w]/d=1.0, Var(w)/d^2=1.0, share=%.4f." % ANALYTIC_SHARE)
    P("Circular-shift empirical null: within-session rotation, one shared offset/session, K=%d." % K_SHIFT)
    P("")
    P("---- MDE TABLE (printed BEFORE verdicts) " + "-" * 55)
    P("leg (a) mean(w)/d bootstrap-CI half-widths (per era, per delta):")
    for d in DELTAS:
        hw = ["%.4f" % ((ciA[d][k][1] - ciA[d][k][0]) / 2) for k in range(3)]
        P("  delta=%.1f%%  CI half-widths: %s" % (d * 100, " ".join(hw)))
    P("leg (b) Var(w)/d^2 sim-band half-width (1.96*SD over %d reps), full sample:" % K_SIM)
    for d in DELTAS:
        mu, sd = agg(sim_rows, d, "var")
        P("  delta=%.1f%%  band half-width: %.4f  (sim mean %.4f)" % (d * 100, 1.96 * sd, mu))
    P("leg (c) share CI half-widths (full): " + " ".join(
        "%.5f" % ((ciC[d]["full"][1] - ciC[d]["full"][0]) / 2) for d in DELTAS))
    P("conditional MDE: beta label-null SD=%.5f -> MDE(|beta|)=%.5f ; Delta null SD=%.5f -> MDE(Delta)=%.5f"
      % (null_beta.std(), 1.96 * null_beta.std(), null_delta.std(), 1.96 * null_delta.std()))
    P("")
    P("---- LEG (a): mean(omega)/delta per era  [SPEC PASS = in [0.8,1.2] ALL cells] " + "-" * 20)
    P("delta      era        n_seg     mean(w)/d   boot95CI            simGBM(mean+-sd)  shiftnull   in-band")
    legA_cells = []
    for d in DELTAS:
        for k in range(3):
            st = real_stats[d]["era"][k]
            lo, hi, _ = ciA[d][k]
            smu, ssd = agg(sim_rows, d, "mean", k)
            cmu, _ = agg(shift_rows, d, "mean", k)
            inb = 0.8 <= st["mean"] <= 1.2
            legA_cells.append(inb)
            P("  %.1f%%   %s  %8d   %8.4f   [%.4f,%.4f]   %.3f+-%.3f      %.3f      %s"
              % (d * 100, ERA_NAMES[k], st["n"], st["mean"], lo, hi, smu, ssd, cmu,
                 "YES" if inb else "NO"))
    legA_pass = all(legA_cells)
    P("")
    P("---- LEG (b): Var(omega)/delta^2 vs vol-matched Brownian sim (characterization) " + "-" * 16)
    P("delta      obs_var    sim(mean+-sd)     analytic   shiftnull   class")
    legB = {}
    for d in DELTAS:
        v = real_stats[d]["var"]
        mu, sd = agg(sim_rows, d, "var")
        cmu, _ = agg(shift_rows, d, "var")
        band = 1.96 * sd
        cls = "CONSISTENT" if abs(v - mu) <= band else ("ELEVATED" if v > mu else "SUPPRESSED")
        legB[d] = cls
        P("  %.1f%%   %8.4f   %.4f+-%.4f     1.0000     %.4f     %s" % (d * 100, v, mu, sd, cmu, cls))
    P("  per-era obs Var(w)/d^2:")
    for d in DELTAS:
        P("    %.1f%%  " % (d * 100) + "  ".join(
            "%s=%.3f" % (ERA_NAMES[k], real_stats[d]["era"][k]["var"]) for k in range(3)))
    P("")
    P("---- LEG (c) LAW: DC-share vs 0.632 " + "-" * 60)
    P("delta      obs_share   boot95CI              sim_share(mean+-sd)   contains_sim  dist_from_0.6321")
    legC_law = []
    for d in DELTAS:
        s = real_stats[d]["share"]
        lo, hi, _ = ciC[d]["full"]
        smu, ssd = agg(sim_rows, d, "share")
        cont = lo <= smu <= hi
        legC_law.append(cont)
        P("  %.1f%%   %.5f    [%.5f,%.5f]   %.5f+-%.5f      %s        %+.5f"
          % (d * 100, s, lo, hi, smu, ssd, "YES" if cont else "NO", s - ANALYTIC_SHARE))
    P("  per-era obs share:")
    for d in DELTAS:
        P("    %.1f%%  " % (d * 100) + "  ".join(
            "%s=%.4f" % (ERA_NAMES[k], real_stats[d]["era"][k]["share"]) for k in range(3)))
    P("")
    P("---- scaling law (observable, no gate): logN(delta) slope real=%.3f  sim=%.3f+-%.3f"
      % (slope_real, np.mean(slopes_sim), np.std(slopes_sim)))
    P("")
    P("---- LEG (c) CONDITIONAL at delta=0.2%% (THE preregistered conditional) " + "-" * 25)
    P("eligible sessions=%d  DEVIANT(top-decile |d|)=%d matched=%d  CONFORMING(bottom-decile)=%d matched=%d"
      % (elig.size, dev_idx.size, dev_u.size, conf_idx.size, conf_u.size))
    P("|d| decile cuts: hi=%.5f lo=%.5f ; class beta = WLS hazard slope h(k) on k=0..4 (memoryless: 0)"
      % (q_hi, q_lo))
    P("  UNCONDITIONAL (all eligible): beta=%+.5f  hazard h(0..4)=%s"
      % (b_unc, np.array2string(D_unc / np.maximum(R_unc, 1), precision=4)))
    P("  DEVIANT:    beta=%+.5f   matched-control beta=%+.5f   Delta=|b_dev|-|b_ctl|=%+.5f" % (b_dev, b_ctld, delta_dev))
    P("  CONFORMING: beta=%+.5f   matched-control beta=%+.5f   Delta=%+.5f" % (b_conf, b_ctlc, delta_conf))
    P("  label-shift null (K=%d): beta central95=[%+.5f,%+.5f]; Delta 95th pct=%+.5f"
      % (K_LABEL, nb_lo, nb_hi, nd95))
    dlo, dhi = np.percentile(boot_dev, [2.5, 97.5])
    clo, chi = np.percentile(boot_conf, [2.5, 97.5])
    P("  pair-bootstrap Delta 95%%CI: DEVIANT=[%+.5f,%+.5f]  CONFORMING=[%+.5f,%+.5f]" % (dlo, dhi, clo, chi))
    L1 = (b_dev < nb_lo) or (b_dev > nb_hi)
    L2 = (delta_dev > 0) and (dlo > 0)
    lift = L1 and L2
    P("")
    P("=" * 100)
    P("GATE TABLE (printed by program)")
    P("GATE | SPEC | OBSERVED | PASS-FAIL")
    P("A_overshoot_law | mean(w)/d in [0.8,1.2] all 15 era-cells | %d/15 in-band | %s"
      % (sum(legA_cells), "PASS" if legA_pass else "FAIL"))
    P("B_variability   | characterization vs sim band (no family gate) | %s | n/a"
      % ",".join("%.1f%%:%s" % (d * 100, legB[d]) for d in DELTAS))
    P("C_632_law       | share 95%%CI contains vol-matched sim share, all deltas | %d/5 | %s"
      % (sum(legC_law), "PASS" if all(legC_law) else "FAIL"))
    P("C_conditional_L1| beta_dev outside label-null central95 | beta=%+.5f vs [%+.5f,%+.5f] | %s"
      % (b_dev, nb_lo, nb_hi, "PASS" if L1 else "FAIL"))
    P("C_conditional_L2| Delta>0 with pair-boot 95%%CI excluding 0 | Delta=%+.5f CI=[%+.5f,%+.5f] | %s"
      % (delta_dev, dlo, dhi, "PASS" if L2 else "FAIL"))
    P("LIFT (L1 AND L2)| family opens iff lift above control+null | - | %s"
      % ("LIFT" if lift else "NO-LIFT"))
    P("=" * 100)
    verdict = "FAMILY-OPENS" if lift else "EVENTTIME-CLOSED (laws%s, no conditional lift)" % (
        "-hold" if legA_pass else "-deviate")
    P("VERDICT: %s" % verdict)
    P("wall_s %.0f" % (_time.time() - t0))
    txt = "\n".join(lines)
    print(txt)
    data = txt.encode("utf-8")
    with open(os.path.join(OUTA, "gate_table.txt"), "wb") as f:
        f.write(data)
    assert os.path.getsize(os.path.join(OUTA, "gate_table.txt")) > 0

    res = {
        "trial": "G00037", "run": "G2_F8_DUO_20260829/A", "verdict": verdict,
        "legA_pass": bool(legA_pass), "legC_law_pass": bool(all(legC_law)),
        "legB_class": {("%.1f%%" % (d * 100)): legB[d] for d in DELTAS},
        "lift": bool(lift), "L1": bool(L1), "L2": bool(L2),
        "beta_dev": b_dev, "beta_ctl": b_ctld, "beta_conf": b_conf, "beta_unc": b_unc,
        "delta_dev": delta_dev, "delta_dev_ci": [float(dlo), float(dhi)],
        "null_beta_ci": [float(nb_lo), float(nb_hi)],
        "real_stats": {("%.1f%%" % (d * 100)): real_stats[d] for d in DELTAS},
        "slope_logN": slope_real,
    }
    with open(os.path.join(OUTA, "dc_audit_results.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)


if __name__ == "__main__":
    main(selftest="--selftest" in sys.argv)
