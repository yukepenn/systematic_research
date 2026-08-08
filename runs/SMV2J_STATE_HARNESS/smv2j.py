"""SMV2J_STATE_HARNESS — JOB1 information test ONLY (seq 366 = B-H1 VR, seq 367 = B-H3 ER).

Frozen spec: runs/SMV2J_STATE_HARNESS/spec.yaml. DIAGNOSTIC class — no policy, no exposure rule.

12 state cells (9 VR + 3 ER), ONE preregistered harness applied identically to all cells:
  test_1 monotonicity   : expanding-rank quintile means of next-session PnL, <=1 adjacent inversion
  test_2 incremental    : OLS PnL_{t+1} ~ z(state_t)+z(sigma460_t)+HTF_t, Newey-West lag 5, |t|>2;
                          moving-block bootstrap (block=5, B=10000, seed=20260808) confirmation
  test_3 plateau        : |t| and Q5-Q1 spread rel. range < 30% across the family's own grid
  test_4 old-regime     : same-sign Q5-Q1 spread on 2006-2021 (E10 outcome); SIGN REVERSAL = kill
cluster_rule: |corr(best VR cell, best ER cell)| > 0.7 daily -> keep only better-plateaued family.

State definitions (frozen):
  VR_t(q,N): Lo-MacKinlay variance ratio on trailing N 1-bar (3m) log returns ending at the
             session-t close bar, overlapping q-bar returns, bias-corrected (m = q(T-q+1)(1-q/T)),
             heteroskedasticity-consistent centering: state = psi*(q) = sqrt(T)(VR-1)/sqrt(theta*),
             theta* = sum_j [2(q-j)/q]^2 * delta_j (CLM 1997 eq. 2.4.43-44).
  ER_t(n):   |close_t - close_{t-n}| / sum_i |close_i - close_{i-1}| over trailing n 3m bars.

Alignment: state at session t close (uses ONLY bars with sess_date <= t, trailing windows end at
the last 3m bar of sess_date t) predicts session t+1 PnL; session sequence taken from the daily
PnL files. Expanding-rank quintiles: rank of state_t within its own trailing history (inclusive),
quintile = ceil(5*rank_pct), >=12mo burn-in, no full-sample scaling anywhere.
"""
import os, sys, json, math, bisect
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "runs", "SMV2J_STATE_HARNESS")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
SEED = 20260808
DEV_END = pd.Timestamp("2026-05-31")
B_BOOT = 10000
BLOCK = 5

VR_QS = (6, 12, 26)
VR_NS = (390, 780, 1950)
ER_NS = (60, 150, 460)
VR_CELLS = [f"VR_q{q}_N{N}" for q in VR_QS for N in VR_NS]
ER_CELLS = [f"ER_n{n}" for n in ER_NS]
ALL_CELLS = VR_CELLS + ER_CELLS

meta = {"seed": SEED, "B_boot": B_BOOT, "block": BLOCK, "dev_end": str(DEV_END.date())}

# ------------------------------------------------------------------ state math
def lm_vr_state(r_win, q):
    """Lo-MacKinlay VR + heteroskedasticity-consistent statistic psi* on window of T returns."""
    T = len(r_win)
    mu = r_win.mean()
    dev = r_win - mu
    d2 = dev * dev
    ssd = d2.sum()
    siga2 = ssd / (T - 1)
    S = np.concatenate(([0.0], np.cumsum(r_win)))
    rq = S[q:] - S[:-q]                     # overlapping q-bar returns (T-q+1)
    b = rq - q * mu
    m = q * (T - q + 1) * (1.0 - q / T)     # LM bias correction
    sigc2 = (b * b).sum() / m
    VR = sigc2 / siga2
    theta = 0.0
    for j in range(1, q):
        dj = T * (d2[j:] * d2[:-j]).sum() / (ssd * ssd)
        theta += (2.0 * (q - j) / q) ** 2 * dj
    z = math.sqrt(T) * (VR - 1.0) / math.sqrt(theta)
    return VR, z


def compute_states(bars, label):
    """bars: time-ordered frame w/ close, sess_date (datetime), sigma460 optional.
    Session unit = sess_date; state computed at the LAST 3m bar of each sess_date
    (== is_last_of_sess on dev where the mapping is 1:1; hist pre-2012 has 128 dates
    holding two NT sessions -> last bar per sess_date matches the daily-PnL keying)."""
    assert bars["time"].is_monotonic_increasing, f"{label}: bars not time-ordered"
    c = bars["close"].to_numpy(float)
    assert not np.isnan(c).any(), f"{label}: NaN closes"
    logc = np.log(c)
    r = np.diff(logc)                       # r[k-1] = log return into bar k
    absd = np.abs(np.diff(c))               # absd[k-1] = |c[k]-c[k-1]|
    sd = bars["sess_date"].to_numpy()
    # last bar position per sess_date (bars time-ordered, sess_date monotone by construction)
    last_idx = np.flatnonzero(np.r_[sd[1:] != sd[:-1], True])
    sess_dates = pd.DatetimeIndex(sd[last_idx])
    assert sess_dates.is_monotonic_increasing and sess_dates.is_unique, f"{label}: session order"
    ns = len(last_idx)
    cols = {}
    for q in VR_QS:
        for N in VR_NS:
            zc = np.full(ns, np.nan)
            vc = np.full(ns, np.nan)
            for i, k in enumerate(last_idx):
                if k >= N:                  # window r[k-N:k] ends at bar k (session close)
                    vc[i], zc[i] = lm_vr_state(r[k - N:k], q)
            cols[f"VR_q{q}_N{N}"] = zc
            cols[f"VRraw_q{q}_N{N}"] = vc
    for n in ER_NS:
        e = np.full(ns, np.nan)
        for i, k in enumerate(last_idx):
            if k >= n:
                den = absd[k - n:k].sum()   # |c-c| over trailing n bars ending at k
                e[i] = abs(c[k] - c[k - n]) / den if den > 0 else np.nan
        cols[f"ER_n{n}"] = e
    df = pd.DataFrame(cols, index=sess_dates)
    df["sess_close"] = c[last_idx]
    if "sigma460" in bars.columns:
        df["sigma460"] = bars["sigma460"].to_numpy(float)[last_idx]
    # LEAKAGE CHECK (FACT): every trailing window ends exactly at the last bar of session t;
    # window indices are <= that bar by construction (r[k-N:k], absd[k-n:k] end at bar k).
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
print("loading dev substrate ...")
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

print("computing dev states (12 cells) ...")
Sdev = compute_states(v, "dev")
assert set(Sdev.index) == set(pnl["date"]), "substrate sessions != primary PnL sessions"
assert set(Sdev.index) == set(e10["sess"]), "substrate sessions != e10 PnL sessions"

# controls: HTF sign at session t close (sign(close_t - SMA50 of session closes up to t)).
# This is exactly the value the deployed DUAL_HTF strategy uses DURING session t+1
# (smv2h.py applies shift(1): bars of session d use the sign from session d-1).
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

# ------------------------------------------------------------------ load hist (old regime)
print("loading hist substrate ...")
h = pd.read_parquet(os.path.join(ROOT, "runs/SM06_SOLAR_HISTORY/out/vote_state_3m_hist.parquet"),
                    columns=["time", "sess_date", "close", "sigma460"])
h["sess_date"] = pd.to_datetime(h["sess_date"])
print("computing hist states (12 cells) ...")
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


# ------------------------------------------------------------------ harness (one pass, 12 cells)
print("running preregistered harness ...")
y1 = samp["next_pnl_dual"].to_numpy(float)          # PRIMARY outcome
y2 = samp["next_pnl_e10"].to_numpy(float)           # secondary (report-only)
sig_z = zsc(samp["sigma460"].to_numpy(float))
htf = samp["htf"].to_numpy(float)

rows = []
for cell in ALL_CELLS:
    seq = 366 if cell.startswith("VR") else 367
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
    print(f"{cell:12s} t_NW {t_state:+6.2f} bootP+ {boot_P_pos:.3f} sprd {spread_p:+7.1f} "
          f"inv {inversions} | hist sprd {spread_h:+7.1f} t {t_spread_h:+5.2f} {t4_class}")

H = pd.DataFrame(rows)

# ---- test 3: plateau per family (rel. range = (max-min)/|mean| over the family's own grid)
for fam, cells in [("VR", VR_CELLS), ("ER", ER_CELLS)]:
    sub = H[H["cell"].isin(cells)]
    tvals = sub["t_state_NW"].to_numpy()
    svals = sub["spread_q5q1_primary"].to_numpy()
    t_rr = float((tvals.max() - tvals.min()) / abs(tvals.mean())) if tvals.mean() != 0 else np.inf
    s_rr = float((svals.max() - svals.min()) / abs(svals.mean())) if svals.mean() != 0 else np.inf
    H.loc[H["cell"].isin(cells), "family_t_relrange"] = t_rr
    H.loc[H["cell"].isin(cells), "family_spread_relrange"] = s_rr
    H.loc[H["cell"].isin(cells), "test3_pass"] = bool(t_rr < 0.30 and s_rr < 0.30)

# ------------------------------------------------------------------ correlations + cluster rule
corr_cols = ALL_CELLS + ["sigma460", "htf"]
C = samp[corr_cols].corr()
C.to_csv(os.path.join(OUT, "state_correlations.csv"))

best = {}
for fam, cells in [("VR", VR_CELLS), ("ER", ER_CELLS)]:
    sub = H[H["cell"].isin(cells)]
    best[fam] = sub.loc[sub["t_state_NW"].abs().idxmax(), "cell"]
cross_corr = float(C.loc[best["VR"], best["ER"]])
meta["best_VR_cell"] = best["VR"]
meta["best_ER_cell"] = best["ER"]
meta["best_cross_corr"] = cross_corr

# ------------------------------------------------------------------ family verdicts
verdicts = {}
for fam, cells in [("VR", VR_CELLS), ("ER", ER_CELLS)]:
    b = H[H["cell"] == best[fam]].iloc[0]
    fam_pass = bool(b["test1_pass"] and b["test2_t_pass"] and b["test2_boot_confirm"]
                    and b["test3_pass"] and not b["test4_kill"])
    verdicts[fam] = {
        "best_cell": best[fam],
        "test1_pass_best": bool(b["test1_pass"]),
        "test2_t_pass_best": bool(b["test2_t_pass"]),
        "test2_boot_confirm_best": bool(b["test2_boot_confirm"]),
        "test3_pass": bool(b["test3_pass"]),
        "test4_class_best": b["test4_class"],
        "n_cells_test2_pass": int(H[H["cell"].isin(cells)]["test2_t_pass"].sum()),
        "n_cells_test1_pass": int(H[H["cell"].isin(cells)]["test1_pass"].sum()),
        "n_cells_test4_reversal": int(H[H["cell"].isin(cells)]["test4_kill"].sum()),
        "verdict": "KEEP" if fam_pass else "KILL",
    }

cluster_applied = False
if verdicts["VR"]["verdict"] == "KEEP" and verdicts["ER"]["verdict"] == "KEEP" \
        and abs(cross_corr) > 0.7:
    cluster_applied = True
    vr_pl = H[H["cell"] == best["VR"]]["family_t_relrange"].iloc[0]
    er_pl = H[H["cell"] == best["ER"]]["family_t_relrange"].iloc[0]
    loser = "ER" if vr_pl <= er_pl else "VR"
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
