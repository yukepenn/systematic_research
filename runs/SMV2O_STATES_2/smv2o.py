"""SMV2O_STATES_2 — JOB1 information test ONLY (seq 375 = Kalman whiteness, seq 376 = BOCPD age).

Frozen spec: runs/SMV2O_STATES_2/spec.yaml. DIAGNOSTIC class — no policy, no exposure rule.
Harness = EXACTLY the SMV2J frozen harness (runs/SMV2J_STATE_HARNESS/smv2j.py), reused verbatim:
  test_1 monotonicity   : expanding-rank quintile means of next-session PnL, <=1 adjacent inversion
  test_2 incremental    : OLS PnL_{t+1} ~ z(state_t)+z(sigma460_t)+HTF_t, Newey-West lag 5, |t|>2;
                          moving-block bootstrap (block=5, B=10000, seed=20260808) confirmation
  test_3 plateau        : |t| and Q5-Q1 spread rel. range < 30% across the family's own grid
  test_4 old-regime     : same-sign Q5-Q1 spread on 2006-2021 (E10 outcome); SIGN REVERSAL = kill
  cluster_rule          : |corr(best KAL cell, best BOC cell)| > 0.7 daily -> keep better-plateaued
EXTRA KILL (this spec only): |corr(state, sigma460)| > 0.7 daily -> cell killed as vol-transition
  in disguise (checked FIRST; BOCPD explicitly at risk per DR pass B).

State definitions (frozen; 12 cells, no extras):
  KAL_qr{q/r}_M{M} (seq 375): simple 2-state local level+trend Kalman on log(close), 3m bars.
      F=[[1,1],[0,1]], H=[1,0], R=1, Q=(q/r)*I2 with q/r in {1e-4,1e-3,1e-2} (engineering
      constants, not fitted; standardized innovations depend only on the ratio). Diffuse-ish init:
      level=logc[0], trend=0, P0=1e7*I2. State at session close t = Ljung-Box Q statistic at lag
      10 (statsmodels acorr_ljungbox) over the last M standardized one-step innovations ending at
      the last 3m bar of session t, M in {50,100,200}. 9 cells.
  BOC_lam{L} (seq 376): Adams-MacKay BOCPD on 30-min block returns (10 x 3m bars), Student-t
      predictive from normal-inverse-gamma conjugate updates, fixed weak prior kappa0=1, alpha0=2,
      mu0=0, beta0 = variance of block returns over the first 12mo of the series (per dataset;
      known by quintile burn-in end, so every state used by the harness is causal at t).
      Constant hazard H=1/lambda, lambda in {100,250,500} blocks. Run-length distribution
      truncated at 2000 (cap bin = "run length >= 2000", mass-weighted merge of mu/beta).
      State at session close t = E[run length] after the last completed block of session t.
      3 cells.
Block construction: within each session, consecutive non-overlapping 10-bar groups anchored at
the session's first bar; block return = logc[last bar of group] - logc[anchor], anchor = previous
session's last bar for the first group (overnight gap included there; very first session anchors
at its own first bar), else the previous group's last bar. Trailing <10-bar remainders are
dropped (dev: 25/1139 sessions non-multiple-of-10; hist: most sessions, so the last block ends
up to 9 bars before the close — still causal at session close).

Alignment identical to SMV2J: state at session t close predicts session t+1 PnL; expanding-rank
quintiles (>=12mo burn-in, no full-sample scaling anywhere).
"""
import os, sys, json, math, bisect
import numpy as np
import pandas as pd
from scipy import stats
from scipy.special import gammaln
import statsmodels.api as sm
from statsmodels.stats.diagnostic import acorr_ljungbox

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "runs", "SMV2O_STATES_2")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
SEED = 20260808
DEV_END = pd.Timestamp("2026-05-31")
B_BOOT = 10000
BLOCK = 5

KAL_QRS = ("1e-4", "1e-3", "1e-2")          # q/r ratio grid (frozen)
KAL_MS = (50, 100, 200)                     # LB window grid (frozen)
BOC_LAMS = (100, 250, 500)                  # hazard 1/lambda grid (frozen)
LB_LAG = 10
RMAX = 2000                                  # run-length truncation (frozen)
KAPPA0, ALPHA0, MU0 = 1.0, 2.0, 0.0
KAL_CELLS = [f"KAL_qr{qr}_M{M}" for qr in KAL_QRS for M in KAL_MS]
BOC_CELLS = [f"BOC_lam{L}" for L in BOC_LAMS]
ALL_CELLS = KAL_CELLS + BOC_CELLS
FAMS = [("KAL", KAL_CELLS), ("BOC", BOC_CELLS)]

meta = {"seed": SEED, "B_boot": B_BOOT, "block": BLOCK, "dev_end": str(DEV_END.date()),
        "kalman": {"qr_grid": list(KAL_QRS), "M_grid": list(KAL_MS), "lb_lag": LB_LAG,
                   "R": 1.0, "Q": "(q/r)*I2", "P0": "1e7*I2", "init": "level=logc[0], trend=0"},
        "bocpd": {"lambda_grid": list(BOC_LAMS), "rmax": RMAX,
                  "prior": {"kappa0": KAPPA0, "alpha0": ALPHA0, "mu0": MU0,
                            "beta0": "var(block returns, first 12mo of each series)"},
                  "blocks": "10x3m within-session, gap in first block, <10-bar remainder dropped"}}


# ------------------------------------------------------------------ state math
def kalman_innovations(logc, qr):
    """2-state local level+trend KF on logc; returns standardized one-step innovations.
    e[j] is the innovation of bar j+1 (filter starts from bar 1; a0=[logc[0],0])."""
    q = float(qr)
    r = 1.0
    K = len(logc)
    e = np.empty(K - 1)
    a1, a2 = logc[0], 0.0
    p11, p12, p22 = 1e7, 0.0, 1e7
    for t in range(1, K):
        a1p = a1 + a2
        p11p = p11 + 2.0 * p12 + p22 + q
        p12p = p12 + p22
        p22p = p22 + q
        v = logc[t] - a1p
        S = p11p + r
        e[t - 1] = v / math.sqrt(S)
        k1 = p11p / S
        k2 = p12p / S
        a1 = a1p + k1 * v
        a2 = a2 + k2 * v
        p11 = (1.0 - k1) * p11p
        p12 = (1.0 - k1) * p12p
        p22 = p22p - k2 * p12p
    return e


def lb_stat(x):
    """Ljung-Box Q statistic at lag LB_LAG via statsmodels acorr_ljungbox (spec-mandated)."""
    res = acorr_ljungbox(x, lags=[LB_LAG], return_df=True)
    return float(res["lb_stat"].iloc[0])


def make_blocks(logc, last_idx):
    """30-min block returns per the frozen construction. Returns (x_blocks, sess_last_block):
    x_blocks[j] = j-th block return in time order; sess_last_block[i] = index into x_blocks of
    the last completed block of session i (sessions ordered as last_idx)."""
    xs = []
    sess_last = np.full(len(last_idx), -1, dtype=int)
    start = 0
    for i, k in enumerate(last_idx):
        nbar = k - start + 1
        G = nbar // 10
        assert G >= 1, f"session {i} has {nbar} bars (<10)"
        for g in range(G):
            end = start + 10 * g + 9
            anchor = start + 10 * g - 1          # prev session close for g=0 (gap included)
            if anchor < 0:
                anchor = 0                       # very first session: 9 returns
            xs.append(logc[end] - logc[anchor])
        sess_last[i] = len(xs) - 1
        start = k + 1
    return np.asarray(xs), sess_last


def bocpd_expected_runlength(x, lam, beta0):
    """Adams-MacKay BOCPD, Student-t (NIG) predictive, constant hazard 1/lam, truncation RMAX.
    Returns E[run length] after each observation (in blocks)."""
    H = 1.0 / lam
    n = len(x)
    # deterministic per-run-length constants (run length r has seen exactly r observations)
    r_idx = np.arange(RMAX + 1, dtype=float)
    kap_all = KAPPA0 + r_idx
    alp_all = ALPHA0 + r_idx / 2.0
    lconst_all = gammaln(alp_all + 0.5) - gammaln(alp_all) - 0.5 * np.log(2.0 * alp_all * np.pi)
    er = np.empty(n)
    P = np.array([1.0])
    mu = np.array([MU0])
    beta = np.array([beta0])
    for t in range(n):
        L = len(P)
        kap = kap_all[:L]
        alp = alp_all[:L]
        s2 = beta * (kap + 1.0) / (alp * kap)
        z2 = (x[t] - mu) ** 2 / (2.0 * alp * s2)
        logpred = lconst_all[:L] - 0.5 * np.log(s2) - (alp + 0.5) * np.log1p(z2)
        w = P * np.exp(logpred)
        ws = w.sum()
        if ws <= 0.0:                            # numerical guard (never expected to trigger)
            w = P.copy()
            ws = w.sum()
        cp = H * ws
        growth = (1.0 - H) * w
        mu_new = (kap * mu + x[t]) / (kap + 1.0)
        beta_new = beta + kap * (x[t] - mu) ** 2 / (2.0 * (kap + 1.0))
        if L <= RMAX:                            # grow by one
            P = np.concatenate(([cp], growth))
            mu = np.concatenate(([MU0], mu_new))
            beta = np.concatenate(([beta0], beta_new))
        else:                                    # at cap: fold r=RMAX growth into cap bin
            wa, wb = growth[RMAX - 1], growth[RMAX]
            tot = wa + wb
            P = np.concatenate(([cp], growth[:RMAX - 1], [tot]))
            if tot > 0:
                fa = wa / tot                    # normalize FIRST: wa*beta can underflow to 0
                mu_cap = fa * mu_new[RMAX - 1] + (1.0 - fa) * mu_new[RMAX]
                beta_cap = fa * beta_new[RMAX - 1] + (1.0 - fa) * beta_new[RMAX]
            else:
                mu_cap, beta_cap = mu_new[RMAX], beta_new[RMAX]
            mu = np.concatenate(([MU0], mu_new[:RMAX - 1], [mu_cap]))
            beta = np.concatenate(([beta0], beta_new[:RMAX - 1], [beta_cap]))
        P /= P.sum()
        er[t] = float(np.dot(np.arange(len(P), dtype=float), P))
    return er


def compute_states(bars, label):
    """bars: time-ordered frame w/ close, sess_date (datetime), sigma460 optional.
    Session unit = sess_date; state computed at the LAST 3m bar of each sess_date
    (same session keying as SMV2J)."""
    assert bars["time"].is_monotonic_increasing, f"{label}: bars not time-ordered"
    c = bars["close"].to_numpy(float)
    assert not np.isnan(c).any(), f"{label}: NaN closes"
    logc = np.log(c)
    sd = bars["sess_date"].to_numpy()
    last_idx = np.flatnonzero(np.r_[sd[1:] != sd[:-1], True])
    sess_dates = pd.DatetimeIndex(sd[last_idx])
    assert sess_dates.is_monotonic_increasing and sess_dates.is_unique, f"{label}: session order"
    ns = len(last_idx)
    cols = {}
    # ---- seq 375: Kalman innovation whiteness (LB Q at lag 10 over last M std innovations)
    for qr in KAL_QRS:
        print(f"  {label}: Kalman filter qr={qr} ...", flush=True)
        e = kalman_innovations(logc, qr)         # e[j] = innovation of bar j+1
        for M in KAL_MS:
            out = np.full(ns, np.nan)
            for i, k in enumerate(last_idx):
                if k >= M:                       # last M innovations ending at bar k: e[k-M:k]
                    out[i] = lb_stat(e[k - M:k])
            cols[f"KAL_qr{qr}_M{M}"] = out
    # ---- seq 376: BOCPD expected run length on 30-min block returns
    xs, sess_last = make_blocks(logc, last_idx)
    first_sess = sess_dates[0]
    cut12 = first_sess + pd.DateOffset(years=1)
    sess_of_block = np.empty(len(xs), dtype=int)
    prev = -1
    for i, j in enumerate(sess_last):
        sess_of_block[prev + 1:j + 1] = i
        prev = j
    in12 = sess_dates[sess_of_block] < cut12
    beta0 = float(np.var(xs[in12], ddof=1))
    meta[f"bocpd_beta0_{label}"] = beta0
    meta[f"bocpd_nblocks_{label}"] = int(len(xs))
    for lam in BOC_LAMS:
        print(f"  {label}: BOCPD lambda={lam} ...", flush=True)
        er = bocpd_expected_runlength(xs, lam, beta0)
        cols[f"BOC_lam{lam}"] = er[sess_last]
    df = pd.DataFrame(cols, index=sess_dates)
    df["sess_close"] = c[last_idx]
    if "sigma460" in bars.columns:
        df["sigma460"] = bars["sigma460"].to_numpy(float)[last_idx]
    # LEAKAGE CHECK (FACT): Kalman is a forward filter (innovation at bar t uses bars <= t);
    # LB windows end at the last bar of session t. BOCPD is a forward filter over blocks; the
    # state is read after the last completed block of session t; beta0 uses only the first 12mo,
    # fully known before the >=12mo quintile burn-in ends.
    return df


def expanding_quintile(dates, vals, burn_end):
    """Rank of state_t within its own trailing history (inclusive); quintile=ceil(5*rank_pct)."""
    n = len(vals)
    out = np.full(n, np.nan)
    hist = []
    for i in range(n):
        x = vals[i]
        if np.isnan(x):
            continue
        bisect.insort(hist, x)
        if dates[i] >= burn_end:
            rp = bisect.bisect_right(hist, x) / len(hist)
            out[i] = math.ceil(5.0 * rp)
    return out


# ------------------------------------------------------------------ load dev
print("loading dev substrate ...", flush=True)
v = pd.read_parquet(os.path.join(ROOT, "runs/SM01_SUBSTRATE/out/vote_state_3m.parquet"),
                    columns=["time", "sess_date", "close", "sigma460"])
v["sess_date"] = pd.to_datetime(v["sess_date"])
v = v[v["sess_date"] <= DEV_END].reset_index(drop=True)   # HARD dev filter before anything else
meta["dev_bars"] = int(len(v))

pnl = pd.read_csv(os.path.join(ROOT, "runs/SMV2H_ONECONTRACT/out/solar_dual_htf_daily.csv"))
pnl.columns = ["date", "pnl_dual"]
pnl["date"] = pd.to_datetime(pnl["date"])
pnl = pnl.sort_values("date").reset_index(drop=True)
assert pnl["date"].max() <= DEV_END, "primary outcome extends past dev end"

e10 = pd.read_csv(os.path.join(ROOT, "runs/SM01_SUBSTRATE/out/e10_daily_py.csv"))
e10["sess"] = pd.to_datetime(e10["sess"])
e10 = e10[e10["sess"] <= DEV_END].sort_values("sess").reset_index(drop=True)

print("computing dev states (12 cells) ...", flush=True)
Sdev = compute_states(v, "dev")
assert set(Sdev.index) == set(pnl["date"]), "substrate sessions != primary PnL sessions"
assert set(Sdev.index) == set(e10["sess"]), "substrate sessions != e10 PnL sessions"

# controls: HTF sign at session t close (sign(close_t - SMA50 of session closes up to t)).
sclose = Sdev["sess_close"]
Sdev["htf"] = np.sign(sclose - sclose.rolling(50).mean())

# outcome alignment on the PnL files' own session sequence: next-session PnL
frame = pnl.set_index("date").join(e10.set_index("sess"))
frame = frame.join(Sdev)
frame["next_pnl_dual"] = frame["pnl_dual"].shift(-1)
frame["next_pnl_e10"] = frame["net"].shift(-1)

first_sess = frame.index.min()
burn_end_dev = first_sess + pd.DateOffset(years=1)
meta["dev_first_sess"] = str(first_sess.date())
meta["dev_burn_end"] = str(burn_end_dev.date())

dates_np = frame.index.to_numpy()
for cell in ALL_CELLS:
    frame[f"Q_{cell}"] = expanding_quintile(dates_np, frame[cell].to_numpy(float),
                                            np.datetime64(burn_end_dev))

# common regression sample (identical for all 12 cells by construction)
need = (ALL_CELLS + [f"Q_{c}" for c in ALL_CELLS]
        + ["sigma460", "htf", "next_pnl_dual", "next_pnl_e10"])
samp = frame[frame.index >= burn_end_dev].dropna(subset=need).copy()
n = len(samp)
meta["n_regression_sample"] = int(n)
meta["sample_first"] = str(samp.index.min().date())
meta["sample_last"] = str(samp.index.max().date())
print(f"regression sample: {n} sessions {samp.index.min().date()} .. {samp.index.max().date()}")
# reproduction check vs SMV2J (same data, same filters -> same sample)
assert n == 880 and str(samp.index.min().date()) == "2023-01-03" \
    and str(samp.index.max().date()) == "2026-05-28", \
    "regression sample does not reproduce SMV2J's (880, 2023-01-03..2026-05-28)"

# ------------------------------------------------------------------ load hist (old regime)
print("loading hist substrate ...", flush=True)
h = pd.read_parquet(os.path.join(ROOT, "runs/SM06_SOLAR_HISTORY/out/vote_state_3m_hist.parquet"),
                    columns=["time", "sess_date", "close", "sigma460"])
h["sess_date"] = pd.to_datetime(h["sess_date"])
print("computing hist states (12 cells) ...", flush=True)
Shist = compute_states(h, "hist")
eh = pd.read_csv(os.path.join(ROOT, "runs/SM06_SOLAR_HISTORY/out/e10_daily_hist.csv"))
eh["sess"] = pd.to_datetime(eh["sess"])
eh = eh.sort_values("sess").reset_index(drop=True)
assert set(Shist.index) == set(eh["sess"]), "hist sessions != hist e10 sessions"

hframe = eh.set_index("sess").join(Shist)
hframe["next_pnl_e10"] = hframe["net"].shift(-1)
burn_end_hist = hframe.index.min() + pd.DateOffset(years=1)
meta["hist_burn_end"] = str(burn_end_hist.date())
hd_np = hframe.index.to_numpy()
for cell in ALL_CELLS:
    hframe[f"Q_{cell}"] = expanding_quintile(hd_np, hframe[cell].to_numpy(float),
                                             np.datetime64(burn_end_hist))
hsamp = hframe[hframe.index >= burn_end_hist].dropna(
    subset=ALL_CELLS + [f"Q_{c}" for c in ALL_CELLS] + ["next_pnl_e10"]).copy()
meta["n_hist_sample"] = int(len(hsamp))
print(f"hist sample: {len(hsamp)} sessions {hsamp.index.min().date()} .. {hsamp.index.max().date()}")

# ------------------------------------------------------------------ bootstrap indices (shared)
nb = math.ceil(n / BLOCK)
rng = np.random.default_rng(SEED)
starts = rng.integers(0, n - BLOCK + 1, size=(B_BOOT, nb))
bidx = (starts[:, :, None] + np.arange(BLOCK)[None, None, :]).reshape(B_BOOT, -1)[:, :n]
meta["bootstrap"] = "moving-block, joint (y,X) rows, same index draws reused for all 12 cells"


def boot_beta_state(X, y, chunk=1000):
    """OLS beta of column 1 (state) under moving-block resampling of (y,X) rows."""
    betas = np.empty(B_BOOT)
    for s0 in range(0, B_BOOT, chunk):
        ix = bidx[s0:s0 + chunk]
        Xb = X[ix]                                    # (b, n, k)
        yb = y[ix]                                    # (b, n)
        XtX = np.einsum("bni,bnj->bij", Xb, Xb)
        Xty = np.einsum("bni,bn->bi", Xb, yb)
        betas[s0:s0 + chunk] = np.linalg.solve(XtX, Xty)[:, 1]
    return betas


def zsc(x):
    return (x - x.mean()) / x.std(ddof=1)


def quintile_stats(qcol, ycol, df):
    m = df.groupby(df[qcol].astype(int))[ycol].mean().reindex([1, 2, 3, 4, 5])
    cnt = df.groupby(df[qcol].astype(int))[ycol].size().reindex([1, 2, 3, 4, 5]).fillna(0)
    return m.to_numpy(), cnt.to_numpy().astype(int)


def welch_t(a, b):
    if len(a) < 2 or len(b) < 2:
        return np.nan, np.nan
    t, p = stats.ttest_ind(a, b, equal_var=False)
    return float(t), float(p)


# ------------------------------------------------------------------ correlations + EXTRA KILL
corr_cols = ALL_CELLS + ["sigma460", "htf"]
C = samp[corr_cols].corr()
C.to_csv(os.path.join(OUT, "state_correlations.csv"))
sig_corr = {cell: float(C.loc[cell, "sigma460"]) for cell in ALL_CELLS}
extra_kill = {cell: bool(abs(sig_corr[cell]) > 0.7) for cell in ALL_CELLS}
meta["extra_kill_rule"] = "|corr(state, sigma460)| > 0.7 daily (regression sample) -> cell killed"

# ------------------------------------------------------------------ harness (one pass, 12 cells)
print("running preregistered harness ...", flush=True)
y1 = samp["next_pnl_dual"].to_numpy(float)          # PRIMARY outcome
y2 = samp["next_pnl_e10"].to_numpy(float)           # secondary (report-only)
sig_z = zsc(samp["sigma460"].to_numpy(float))
htf = samp["htf"].to_numpy(float)

rows = []
for cell in ALL_CELLS:
    seq = 375 if cell.startswith("KAL") else 376
    st = samp[cell].to_numpy(float)
    st_z = zsc(st)
    X = np.column_stack([np.ones(n), st_z, sig_z, htf])

    # ---- test 1: monotonicity of quintile means (primary outcome)
    qm, qcnt = quintile_stats(f"Q_{cell}", "next_pnl_dual", samp)
    direction = np.sign(qm[4] - qm[0])
    adj = np.diff(qm)
    inversions = int((np.sign(adj) == -direction).sum()) if direction != 0 else 4
    t1_pass = bool(direction != 0 and inversions <= 1)

    # ---- test 2: incremental NW regression + moving-block bootstrap
    res1 = sm.OLS(y1, X).fit(cov_type="HAC", cov_kwds={"maxlags": 5})
    beta_state, t_state = float(res1.params[1]), float(res1.tvalues[1])
    res2 = sm.OLS(y2, X).fit(cov_type="HAC", cov_kwds={"maxlags": 5})
    t_state_e10 = float(res2.tvalues[1])
    betas = boot_beta_state(X, y1)
    boot_P_pos = float((betas > 0).mean())
    boot_same_sign = float((np.sign(betas) == np.sign(beta_state)).mean()) if beta_state != 0 else np.nan
    t2_t_pass = bool(abs(t_state) > 2.0)
    t2_boot_confirm = bool(boot_same_sign >= 0.975)

    # ---- spreads (dev)
    g5 = samp.loc[samp[f"Q_{cell}"] == 5, "next_pnl_dual"].to_numpy(float)
    g1 = samp.loc[samp[f"Q_{cell}"] == 1, "next_pnl_dual"].to_numpy(float)
    spread_p = float(g5.mean() - g1.mean())
    t_spread_p, _ = welch_t(g5, g1)
    g5e = samp.loc[samp[f"Q_{cell}"] == 5, "next_pnl_e10"].to_numpy(float)
    g1e = samp.loc[samp[f"Q_{cell}"] == 1, "next_pnl_e10"].to_numpy(float)
    spread_s = float(g5e.mean() - g1e.mean())

    # ---- test 4: old regime (E10 outcome, 2006-2021)
    h5 = hsamp.loc[hsamp[f"Q_{cell}"] == 5, "next_pnl_e10"].to_numpy(float)
    h1 = hsamp.loc[hsamp[f"Q_{cell}"] == 1, "next_pnl_e10"].to_numpy(float)
    spread_h = float(h5.mean() - h1.mean())
    t_spread_h, p_spread_h = welch_t(h5, h1)
    dev_sign = np.sign(spread_p)
    if abs(t_spread_h) < 1.0:
        t4_class = "FLAT"
    elif np.sign(spread_h) == dev_sign:
        t4_class = "SAME_SIGN"
    else:
        t4_class = "REVERSAL"
    t4_kill = bool(t4_class == "REVERSAL")

    rows.append({
        "seq": seq, "family": cell.split("_")[0], "cell": cell, "n_obs": n,
        "corr_sigma460": sig_corr[cell], "extra_kill_sigma460": extra_kill[cell],
        "q1_mean": qm[0], "q2_mean": qm[1], "q3_mean": qm[2], "q4_mean": qm[3], "q5_mean": qm[4],
        "q1_n": qcnt[0], "q5_n": qcnt[4],
        "mono_direction": int(direction), "inversions": inversions, "test1_pass": t1_pass,
        "beta_state": beta_state, "t_state_NW": t_state, "test2_t_pass": t2_t_pass,
        "boot_P_pos": boot_P_pos, "boot_same_sign_frac": boot_same_sign,
        "test2_boot_confirm": t2_boot_confirm,
        "t_state_NW_e10": t_state_e10,
        "spread_q5q1_primary": spread_p, "t_spread_primary": t_spread_p,
        "spread_q5q1_e10dev": spread_s,
        "spread_q5q1_hist": spread_h, "t_spread_hist": t_spread_h,
        "test4_class": t4_class, "test4_kill": t4_kill,
    })
    print(f"{cell:16s} sigC {sig_corr[cell]:+5.2f}{'K' if extra_kill[cell] else ' '} "
          f"t_NW {t_state:+6.2f} bootP+ {boot_P_pos:.3f} sprd {spread_p:+7.1f} "
          f"inv {inversions} | hist sprd {spread_h:+7.1f} t {t_spread_h:+5.2f} {t4_class}")

H = pd.DataFrame(rows)

# ---- test 3: plateau per family (rel. range = (max-min)/|mean| over the family's own grid)
for fam, cells in FAMS:
    sub = H[H["cell"].isin(cells)]
    tvals = sub["t_state_NW"].to_numpy()
    svals = sub["spread_q5q1_primary"].to_numpy()
    t_rr = float((tvals.max() - tvals.min()) / abs(tvals.mean())) if tvals.mean() != 0 else np.inf
    s_rr = float((svals.max() - svals.min()) / abs(svals.mean())) if svals.mean() != 0 else np.inf
    H.loc[H["cell"].isin(cells), "family_t_relrange"] = t_rr
    H.loc[H["cell"].isin(cells), "family_spread_relrange"] = s_rr
    H.loc[H["cell"].isin(cells), "test3_pass"] = bool(t_rr < 0.30 and s_rr < 0.30)

# ------------------------------------------------------------------ family verdicts
# best cell = max |t_NW| among cells NOT killed by the sigma460 rule; if every cell in the
# family is sigma460-killed, the family is KILLED-SIGMA460 (vol-transition in disguise).
best = {}
verdicts = {}
for fam, cells in FAMS:
    sub = H[H["cell"].isin(cells)]
    alive = sub[~sub["extra_kill_sigma460"]]
    if len(alive) == 0:
        best[fam] = sub.loc[sub["t_state_NW"].abs().idxmax(), "cell"]   # report-only
        verdicts[fam] = {
            "best_cell": best[fam], "verdict": "KILLED-SIGMA460",
            "n_cells_sigma_killed": int(sub["extra_kill_sigma460"].sum()),
        }
        continue
    best[fam] = alive.loc[alive["t_state_NW"].abs().idxmax(), "cell"]
    b = H[H["cell"] == best[fam]].iloc[0]
    fam_pass = bool(b["test1_pass"] and b["test2_t_pass"] and b["test2_boot_confirm"]
                    and b["test3_pass"] and not b["test4_kill"])
    verdicts[fam] = {
        "best_cell": best[fam],
        "corr_sigma460_best": float(b["corr_sigma460"]),
        "test1_pass_best": bool(b["test1_pass"]),
        "test2_t_pass_best": bool(b["test2_t_pass"]),
        "test2_boot_confirm_best": bool(b["test2_boot_confirm"]),
        "test3_pass": bool(b["test3_pass"]),
        "test4_class_best": b["test4_class"],
        "n_cells_sigma_killed": int(sub["extra_kill_sigma460"].sum()),
        "n_cells_test2_pass": int(sub["test2_t_pass"].sum()),
        "n_cells_test1_pass": int(sub["test1_pass"].sum()),
        "n_cells_test4_reversal": int(sub["test4_kill"].sum()),
        "verdict": "KEEP" if fam_pass else "KILL",
    }

cross_corr = float(C.loc[best["KAL"], best["BOC"]])
meta["best_KAL_cell"] = best["KAL"]
meta["best_BOC_cell"] = best["BOC"]
meta["best_cross_corr"] = cross_corr

cluster_applied = False
if verdicts["KAL"]["verdict"] == "KEEP" and verdicts["BOC"]["verdict"] == "KEEP" \
        and abs(cross_corr) > 0.7:
    cluster_applied = True
    ka_pl = H[H["cell"] == best["KAL"]]["family_t_relrange"].iloc[0]
    bo_pl = H[H["cell"] == best["BOC"]]["family_t_relrange"].iloc[0]
    loser = "BOC" if ka_pl <= bo_pl else "KAL"
    verdicts[loser]["verdict"] = "KILLED-REDUNDANT"
meta["cluster_rule_applied"] = cluster_applied

H["family_verdict"] = H["family"].map({f: verdicts[f]["verdict"] for f in verdicts})
H.to_csv(os.path.join(OUT, "harness_results.csv"), index=False)

# ------------------------------------------------------------------ evidence dumps
frame.reset_index().rename(columns={"index": "sess"}).to_csv(
    os.path.join(OUT, "states_dev.csv"), index=False)
hframe.reset_index().rename(columns={"index": "sess"}).to_csv(
    os.path.join(OUT, "states_hist.csv"), index=False)
with open(os.path.join(OUT, "meta.json"), "w") as f:
    json.dump({"meta": meta, "verdicts": verdicts}, f, indent=2, default=str)

print(json.dumps(verdicts, indent=2, default=str))
print("best cross-corr", round(cross_corr, 3), "cluster applied:", cluster_applied)
print("done")
