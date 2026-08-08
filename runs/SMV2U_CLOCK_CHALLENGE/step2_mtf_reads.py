"""SMV2U step2 -- seq 392, mtf_info_reads_392. Three preregistered information-only reads
(no policy, no exposure rule -- DIAGNOSTIC, matches SMV2J_STATE_HARNESS "JOB1" methodology and
gate convention exactly: OLS with Newey-West HAC (maxlags=5), |t_NW|>2 bar, moving-block bootstrap
confirmation (block=5, B=10000, seed=20260808 -- house convention)).

1m-clock member votes are resampled onto the 3m decision-bar spine via a BACKWARD asof-join on
timestamp (no lookahead: uses the 1m state at or before the 3m bar's close only). 225 of 519,714
3m decision bars (0.043%) have no EXACT-timestamp 1m bar (isolated missing-minute prints in the
raw 1m feed, scattered over years, confirmed not a systematic gap -- see REPORT.md); the asof join
carries forward the most recent available 1m state for those bars, which is still causal.

Both frozen 1m memory conventions (bar-matched N=460, time-matched N=1380) are read and reported;
bar-matched is treated as PRIMARY (mechanism-neighbor: matches the incumbent's bar-count memory,
reacts fastest -- the natural candidate for "does the fast clock lead the slow one" questions);
time-matched is a secondary robustness cross-check. This choice is not specified verbatim in the
frozen spec and is flagged INFERENCE in REPORT.md.
"""
import os, sys, json, math
import numpy as np
import pandas as pd
import statsmodels.api as sm_api

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "runs", "SMV2U_CLOCK_CHALLENGE")
OUT = os.path.join(RUN, "out")
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
import sm01_solarsim as sm  # noqa: E402

SEED = 20260808
B_BOOT = 10000
BLOCK = 5
DEV_END = pd.Timestamp("2026-05-31")

# ------------------------------------------------------------------ 0. load substrates
print("loading ...", flush=True)
bars1 = pd.read_parquet(os.path.join(OUT, "bars_1m_dev.parquet"))
posc = np.load(os.path.join(OUT, "cache_1m_pos.npz"))
vote1m = {
    "bar_matched": posc["bar_matched"].sum(axis=1).astype(float),
    "time_matched": posc["time_matched"].sum(axis=1).astype(float),
}
t1 = bars1["time"].to_numpy()
assert pd.Series(t1).is_monotonic_increasing

v3 = pd.read_parquet(os.path.join(ROOT, "runs", "SM01_SUBSTRATE", "out", "vote_state_3m.parquet"))
v3["sess_date"] = pd.to_datetime(v3["sess_date"])
v3 = v3[v3["sess_date"] <= DEV_END].reset_index(drop=True)
n3 = len(v3)
assert n3 == 519714

inc_cache = np.load(os.path.join(ROOT, "runs", "SMV2R_SOLAR_CORE_1", "out", "cache_incumbent.npz"))
bar_pos = inc_cache["bar_pos"]; bar_pnl = inc_cache["bar_pnl"]
assert len(bar_pos) == n3 == len(bar_pnl)

# is_last_of_sess for the dev 3m bars (used to exclude cross-session "next bar" in R1)
bars3 = sm.load_bars_3m(os.path.join(ROOT, "runs", "AUDIT03_BARS", "nq_3m_2022_2026.csv"))
bars3 = bars3[bars3["sess_date"] <= DEV_END.date()].reset_index(drop=True)
assert len(bars3) == n3 and (bars3["time"].to_numpy() == v3["time"].to_numpy()).all()
is_last3 = bars3["is_last_of_sess"].to_numpy()

# ------------------------------------------------------------------ backward asof join: 1m vote -> 3m spine
n_exact = int(np.isin(v3["time"].to_numpy(), t1).sum())
print(f"3m decision bars with an EXACT-timestamp 1m bar: {n_exact}/{n3} "
      f"({100*n_exact/n3:.3f}%); remainder resolved by backward asof (causal).", flush=True)

def asof_vote(conv):
    src = pd.DataFrame({"time": t1, "vote": vote1m[conv]})
    tgt = pd.DataFrame({"time": v3["time"].to_numpy()})
    merged = pd.merge_asof(tgt, src, on="time", direction="backward")
    assert merged["vote"].notna().all(), f"{conv}: asof join produced NaN (bar before first 1m bar?)"
    return merged["vote"].to_numpy()

VOTE1M = {c: asof_vote(c) for c in ("bar_matched", "time_matched")}
VOTE3M = v3["vote_pos"].to_numpy().astype(float)
CLOSE3M = v3["close"].to_numpy()

# ------------------------------------------------------------------ shared regression helpers
def nw_ols(X, y, maxlags=5):
    res = sm_api.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": maxlags})
    return res

def moving_block_bootstrap_beta(X, y, coef_idx=1, block=BLOCK, B=B_BOOT, seed=SEED,
                                mem_budget_bytes=2e8):
    n = len(y)
    k = X.shape[1]
    nb = math.ceil(n / block)
    # adaptive chunk: cap (chunk * n * (k+1) * 8 bytes) for the gathered Xb/yb arrays; the (chunk,
    # nb) starts/idx arrays are the same order of magnitude and are built PER CHUNK, never for
    # all B draws at once (an all-at-once (B, n) idx array is B/chunk times too big to hold).
    chunk = max(1, min(B, int(mem_budget_bytes / (n * (k + 1) * 8))))
    rng = np.random.default_rng(seed)
    betas = np.empty(B)
    for s0 in range(0, B, chunk):
        b = min(chunk, B - s0)
        starts = rng.integers(0, max(n - block + 1, 1), size=(b, nb))
        idx = (starts[:, :, None] + np.arange(block)[None, None, :]).reshape(b, -1)[:, :n]
        Xb = X[idx]; yb = y[idx]
        XtX = np.einsum("bni,bnj->bij", Xb, Xb)
        Xty = np.einsum("bni,bn->bi", Xb, yb)
        try:
            betas[s0:s0 + b] = np.linalg.solve(XtX, Xty)[:, coef_idx]
        except np.linalg.LinAlgError:
            betas[s0:s0 + b] = np.array(
                [np.linalg.lstsq(Xb[j], yb[j], rcond=None)[0][coef_idx] for j in range(Xb.shape[0])])
        del starts, idx, Xb, yb, XtX, Xty
    return betas

def welch_t(a, b):
    from scipy import stats
    if len(a) < 2 or len(b) < 2:
        return np.nan, np.nan
    t, p = stats.ttest_ind(a, b, equal_var=False)
    return float(t), float(p)

def classify(t_nw, boot_same_sign):
    t_pass = bool(abs(t_nw) > 2.0)
    boot_pass = bool(boot_same_sign >= 0.975)
    if t_pass and boot_pass:
        return "INFORMATIVE"
    if t_pass and not boot_pass:
        return "T_PASS_BOOT_FAILS"
    return "NOT_INFORMATIVE"

reads = []

# ================================================================== R1: failed-start detection
# disagreement_t (3m core positioned, vote3m!=0) vs next-3m-bar adverse move for the positioned
# side; excludes bars where "next bar" would cross a session boundary (overnight jump, not a
# same-session continuation question).
print("\n--- R1: 1m disagreement -> next-3m-bar adverse move ---", flush=True)
for conv in ("bar_matched", "time_matched"):
    vote1 = VOTE1M[conv]
    positioned = (VOTE3M != 0) & (~is_last3) & (np.arange(n3) < n3 - 1)
    idx = np.where(positioned)[0]
    side = np.sign(VOTE3M[idx])
    disagree = (np.sign(vote1[idx]) != side).astype(float)
    adverse = -side * (CLOSE3M[idx + 1] - CLOSE3M[idx])   # points; + = adverse to the positioned side

    X = np.column_stack([np.ones(len(idx)), disagree])
    res = nw_ols(X, adverse)
    t_nw = float(res.tvalues[1]); beta = float(res.params[1])
    betas = moving_block_bootstrap_beta(X, adverse)
    boot_same = float((np.sign(betas) == np.sign(beta)).mean()) if beta != 0 else np.nan

    g1 = adverse[disagree == 1]; g0 = adverse[disagree == 0]
    t_w, p_w = welch_t(g1, g0)
    cls = classify(t_nw, boot_same)
    row = {"read": "R1_failed_start", "convention": conv, "n_obs": len(idx),
          "n_disagree": int(disagree.sum()), "n_agree": int((disagree == 0).sum()),
          "mean_adverse_disagree": float(g1.mean()), "mean_adverse_agree": float(g0.mean()),
          "spread": float(g1.mean() - g0.mean()), "welch_t": t_w, "welch_p": p_w,
          "beta_disagree_pts": beta, "t_NW": t_nw, "boot_same_sign_frac": boot_same,
          "t_pass": bool(abs(t_nw) > 2.0), "boot_confirm": bool(boot_same >= 0.975),
          "classification": cls}
    reads.append(row)
    print(f"  [{conv}] n={len(idx)} disagree={int(disagree.sum())} spread={row['spread']:+.3f}pt "
          f"t_NW={t_nw:+.2f} bootP+={boot_same:.3f} -> {cls}", flush=True)

# ================================================================== R2: entry-timing value
# episodes = contiguous nonzero runs of the incumbent's bar_pos (3m E10 executor); disagreement at
# the entry bar (1m vote sign vs the episode's side) vs the episode's total realized PnL (bar_pnl
# summed over the run).
print("\n--- R2: 1m disagreement at entry -> episode final PnL ---", flush=True)
nz = bar_pos != 0
starts = np.where(nz & np.r_[True, ~nz[:-1]])[0]
ends = np.where(nz & np.r_[~nz[1:], True])[0]
assert len(starts) == len(ends) and (ends >= starts).all()
ep_pnl = np.array([bar_pnl[s:e + 1].sum() for s, e in zip(starts, ends)])
ep_side = np.sign(bar_pos[starts]).astype(float)
print(f"  n_episodes={len(starts)}", flush=True)

for conv in ("bar_matched", "time_matched"):
    vote1 = VOTE1M[conv]
    disagree = (np.sign(vote1[starts]) != ep_side).astype(float)
    y = ep_pnl.astype(float)
    X = np.column_stack([np.ones(len(starts)), disagree])
    res = nw_ols(X, y)
    t_nw = float(res.tvalues[1]); beta = float(res.params[1])
    betas = moving_block_bootstrap_beta(X, y)
    boot_same = float((np.sign(betas) == np.sign(beta)).mean()) if beta != 0 else np.nan
    g1 = y[disagree == 1]; g0 = y[disagree == 0]
    t_w, p_w = welch_t(g1, g0)
    cls = classify(t_nw, boot_same)
    row = {"read": "R2_entry_timing", "convention": conv, "n_obs": len(starts),
          "n_disagree": int(disagree.sum()), "n_agree": int((disagree == 0).sum()),
          "mean_pnl_disagree": float(g1.mean()), "mean_pnl_agree": float(g0.mean()),
          "spread": float(g1.mean() - g0.mean()), "welch_t": t_w, "welch_p": p_w,
          "beta_disagree_$": beta, "t_NW": t_nw, "boot_same_sign_frac": boot_same,
          "t_pass": bool(abs(t_nw) > 2.0), "boot_confirm": bool(boot_same >= 0.975),
          "classification": cls}
    reads.append(row)
    print(f"  [{conv}] n={len(starts)} disagree={int(disagree.sum())} spread=${row['spread']:+.1f} "
          f"t_NW={t_nw:+.2f} bootP+={boot_same:.3f} -> {cls}", flush=True)

# ================================================================== R3: 1m agreement acceleration
# state_t (session close) = accel of the 1m vote sum over the last 15 minutes = roll15_t - roll15_{t-15}
# (roll15 = mean of the 1m vote over the trailing 15 1m bars, inclusive); predicts next-session
# SOLAR_DUAL_HTF PnL beyond sigma460 + HTF (identical control set / burn-in / NW+bootstrap
# machinery as SMV2J_STATE_HARNESS test_2).
print("\n--- R3: 1m agreement acceleration -> next-session DUAL PnL (SMV2J controls) ---", flush=True)
last1_idx = np.where(bars1["is_last_of_sess"].to_numpy())[0]
sess_dates_1m = pd.to_datetime(bars1["sess_date"].to_numpy()[last1_idx])
assert sess_dates_1m.is_monotonic_increasing and sess_dates_1m.is_unique
ns = len(last1_idx)

dual = pd.read_csv(os.path.join(ROOT, "runs", "SMV2H_ONECONTRACT", "out", "solar_dual_htf_daily.csv"))
dual.columns = ["date", "pnl_dual"]
dual["date"] = pd.to_datetime(dual["date"])
dual = dual.sort_values("date").reset_index(drop=True)
assert dual["date"].max() <= DEV_END

sclose = v3.loc[v3["is_last_of_sess"], ["sess_date", "close"]].set_index("sess_date")["close"]
htf_map = np.sign(sclose - sclose.rolling(50).mean()).shift(1)
sig_map = v3.loc[v3["is_last_of_sess"], ["sess_date", "sigma460"]].set_index("sess_date")["sigma460"]

frame = pd.DataFrame({"sess": sess_dates_1m}).set_index("sess")
frame["htf"] = htf_map.reindex(frame.index)
frame["sigma460"] = sig_map.reindex(frame.index)
frame = frame.join(dual.set_index("date")["pnl_dual"])
frame["next_pnl_dual"] = frame["pnl_dual"].shift(-1)

first_sess = frame.index.min()
burn_end = first_sess + pd.DateOffset(years=1)

for conv in ("bar_matched", "time_matched"):
    vote1 = vote1m[conv]
    roll15 = pd.Series(vote1).rolling(15, min_periods=15).mean().to_numpy()
    accel_full = np.full(len(vote1), np.nan)
    accel_full[15:] = roll15[15:] - roll15[:-15]
    accel_at_close = accel_full[last1_idx]
    frame[f"accel_{conv}"] = accel_at_close

    need = ["accel_" + conv, "sigma460", "htf", "next_pnl_dual"]
    samp = frame[frame.index >= burn_end].dropna(subset=need).copy()
    n = len(samp)

    def zsc(x):
        return (x - x.mean()) / x.std(ddof=1)

    st_z = zsc(samp["accel_" + conv].to_numpy(float))
    sig_z = zsc(samp["sigma460"].to_numpy(float))
    htf = samp["htf"].to_numpy(float)
    y = samp["next_pnl_dual"].to_numpy(float)
    X = np.column_stack([np.ones(n), st_z, sig_z, htf])
    res = nw_ols(X, y)
    beta = float(res.params[1]); t_nw = float(res.tvalues[1])
    betas = moving_block_bootstrap_beta(X, y, coef_idx=1)
    boot_same = float((np.sign(betas) == np.sign(beta)).mean()) if beta != 0 else np.nan

    med = np.median(samp["accel_" + conv])
    hi = samp.loc[samp["accel_" + conv] > med, "next_pnl_dual"]
    lo = samp.loc[samp["accel_" + conv] <= med, "next_pnl_dual"]
    t_w, p_w = welch_t(hi.to_numpy(), lo.to_numpy())
    cls = classify(t_nw, boot_same)
    row = {"read": "R3_agreement_accel", "convention": conv, "n_obs": n,
          "sample_first": str(samp.index.min().date()), "sample_last": str(samp.index.max().date()),
          "beta_accel_z": beta, "t_NW": t_nw, "boot_same_sign_frac": boot_same,
          "t_pass": bool(abs(t_nw) > 2.0), "boot_confirm": bool(boot_same >= 0.975),
          "median_split_t": t_w, "median_split_p": p_w, "classification": cls}
    reads.append(row)
    print(f"  [{conv}] n={n} beta_z={beta:+.2f} t_NW={t_nw:+.2f} bootP+={boot_same:.3f} -> {cls}",
          flush=True)

# ------------------------------------------------------------------ outputs
R = pd.DataFrame(reads)
R.to_csv(os.path.join(OUT, "mtf_reads.csv"), index=False)
meta = {"seed": SEED, "B_boot": B_BOOT, "block": BLOCK, "dev_end": str(DEV_END.date()),
       "n_3m_decision_bars": int(n3), "n_exact_time_matches_1m_to_3m": int(n_exact),
       "n_asof_backfilled": int(n3 - n_exact), "n_episodes_R2": int(len(starts))}
with open(os.path.join(OUT, "mtf_reads_meta.json"), "w") as f:
    json.dump(meta, f, indent=2)
print("\n" + R.to_string(index=False))
print("\ndone")
