"""AUCTION03 -- adversarial stress test of the surviving M2M3 finding:

  "far-tercile reversion toward running POC (magnitude/tail effect, not hit-rate edge)"
  = position_direction_corrected variant, Q_reversion, far |value_dist_ticks| tercile, H=60.
  Discovery: far_mean=+7.829t, session_CI=[1.150,16.230], trade_CI=[0.444,16.591], dual-sig=True.
  Confirmation: far_mean=+1.998t, session_CI=[-7.155,133.484], trade_CI=[-6.147,133.484], dual-sig=False.
  H=60 is the ONLY horizon (of 15/60/300) where discovery and confirmation agree in sign.

This script re-derives the exact H=60 / position_direction_corrected / Q_reversion / far-tercile
cell from the two source parquets (same construction as
runs/AUCTION03_MECHANISM_DECOMPOSITION/src/01_m2m3_signed_decomposition.py, verified to reproduce
its reported numbers exactly -- see `[check] baseline reproduction` in the log) and then runs a
battery of attacks against it:

  A1  remove the single most-influential discovery session (the one whose removal drops the pooled
      far-tercile mean the most), recompute mean + dual-clustered CI.
  A2  remove the top-3 most-influential discovery sessions, recompute.
  A3  leave-one-session-out (all 28 discovery sessions that contribute >=1 far-tercile row; also
      all 3 confirmation far-contributing sessions), report the full distribution of the recomputed
      pooled mean and whether sign / dual-significance survive each removal.
  A4  median split of discovery sessions by a realized-session-range volatility proxy (built from
      mid_last_t already present in decision_outcomes.parquet -- sigma460 is not a column in this
      file, only in the M5 action_substrate; range is the closest available in-file proxy and is
      disclosed as such), recompute far-tercile mean + CI in each half.
  A5  split discovery sessions by an approximate NQ contract-quarter bucket (calendar-quarter proxy
      keyed to standard CME quarterly roll windows -- decision_outcomes.parquet carries no literal
      contract-month field, so this is a disclosed calendar approximation, not an exact roll-date
      match), recompute far-tercile mean + CI per bucket.
  A6  confound check: is the |value_dist_ticks| far tercile just relabeling |M| (the SolarWave wave
      value already present in this same file, a known predictor elsewhere in this campaign)?
      Report corr(|D_t|, |M|) and mean |M| by D_t tercile.
  A7  independent no-lookahead spot check: for 5 discovery far-tercile H=60 rows, recompute
      (mid_last(t+60) - mid_last(t))/tick directly from runs/AUCTION01_VALUE_STATE/out/
      poc_1s_full.parquet (the raw 1s mid-price series that decision_outcomes.parquet was itself
      built from) using strictly t-and-later timestamps, and confirm it matches the
      position_direction_corrected raw markout used above.

Governance: reads only the same two already-built parquets 01_m2m3_signed_decomposition.py reads,
plus (read-only, A7 only) runs/AUCTION01_VALUE_STATE/out/poc_1s_full.parquet (an already-built
AUCTION01 output, not new raw/grid1s/sechilo touch). No session outside the task's DISCOVERY/
CONFIRMATION lists. Writes only under runs/AUCTION03_MECHANISM_DECOMPOSITION/out/.
"""
import os
import json
import calendar
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
DISCOVERY_PATH = os.path.join(ROOT, "runs", "AUCTION01_VALUE_STATE", "out", "decision_outcomes.parquet")
CONFIRM_PATH = os.path.join(ROOT, "runs", "W5_PROTECTED_CONFIRMATION", "results", "out",
                             "decision_outcomes_CONFIRM.parquet")
POC_1S_PATH = os.path.join(ROOT, "runs", "AUCTION01_VALUE_STATE", "out", "poc_1s_full.parquet")
OUT_DIR = os.path.join(ROOT, "runs", "AUCTION03_MECHANISM_DECOMPOSITION", "out")
os.makedirs(OUT_DIR, exist_ok=True)

H_TARGET = 60          # the ONLY horizon where discovery/confirmation sign-agree -- the cell under attack
NBOOT = 1000
RNG_SEED = 20260810     # identical seed to 01_m2m3_signed_decomposition.py, for exact baseline reproduction
C1_COST_HURDLE_TICKS = 2.872
TICK = 0.25

DISCOVERY_DATES = sorted("""20250814 20250820 20250901 20250902 20250905 20250910
20250911 20250922 20251002 20251009 20251027 20251029 20251110 20251117 20251124 20251128
20251209 20251222 20260123 20260206 20260211 20260218 20260220 20260223 20260303 20260312
20260317 20260320 20260406 20260409 20260417 20260423 20260428 20260506 20260511 20260519
20260520""".split())
CONFIRMATION_DATES = sorted("""20250819 20250912 20251028 20251125 20260217
20260302 20260422 20260512""".split())
assert len(DISCOVERY_DATES) == 37 and len(CONFIRMATION_DATES) == 8
assert max(DISCOVERY_DATES) < "20260601" and max(CONFIRMATION_DATES) < "20260601"

log_lines = []
def log(msg):
    print(msg, flush=True)
    log_lines.append(str(msg))


# ============================================================= load + tercile + Qrev (identical to 01_*)
def load_and_filter(path, allowed_dates):
    raw = pd.read_parquet(path)
    df = raw[raw["sess_tag"].isin(allowed_dates)].copy()
    return df.sort_values(["sess_tag", "time"]).reset_index(drop=True)


def assign_trade_block(df):
    d = df.copy()
    sgn = np.sign(d["position_B"].to_numpy())
    sess = d["sess_tag"].to_numpy()
    change = np.ones(len(d), dtype=bool)
    change[1:] = (sgn[1:] != sgn[:-1]) | (sess[1:] != sess[:-1])
    d["trade_block_id"] = np.cumsum(change)
    return d


def assign_terciles(df):
    d = df.copy()
    d["D_t"] = d["value_dist_ticks"]
    n_zero = int((d["D_t"] == 0).sum())
    d = d[d["D_t"] != 0].copy()
    d["sign_D"] = np.sign(d["D_t"])
    abs_d = d["D_t"].abs().to_numpy()
    edges = np.unique(np.quantile(abs_d, [0.0, 1 / 3, 2 / 3, 1.0]))
    d["tercile"] = pd.cut(d["D_t"].abs(), bins=edges, labels=["near", "mid", "far"], include_lowest=True)
    return d, n_zero, [float(x) for x in edges]


def build_Qrev_H(d_t, H):
    """Return the sub-dataframe restricted to rows with a defined signed_markout_H, with the
    position_direction_corrected Q_reversion column attached, exactly matching
    01_m2m3_signed_decomposition.py's analyze_sample() body for this one (variant, quantity, H)."""
    col = f"signed_markout_{H}"
    sub = d_t[d_t[col].notna()].copy()
    side = np.sign(sub["position_B"].to_numpy())
    assert (side != 0).all()
    corrected = sub[col].to_numpy(dtype=float) * side           # raw signed price change (ticks)
    sub["raw_markout"] = corrected
    sub["Qrev"] = -sub["sign_D"].to_numpy() * corrected
    return sub


def _group_index(keys_arr):
    codes, uniques = pd.factorize(keys_arr)
    return len(uniques), [np.where(codes == g)[0] for g in range(len(uniques))]


def dual_clustered_bootstrap_mean(values, sess_keys, trade_keys, nboot=NBOOT, seed=RNG_SEED):
    values = np.asarray(values, dtype=float)
    obs_mean = float(values.mean()) if len(values) else float("nan")
    out = {"n": int(len(values)), "mean": obs_mean}
    for label, keys in [("session_block_ci", sess_keys), ("trade_block_ci", trade_keys)]:
        rng = np.random.default_rng(seed)
        n_groups, idx_by_group = _group_index(np.asarray(keys))
        boots = np.full(nboot, np.nan)
        for b in range(nboot):
            picks = rng.integers(0, n_groups, size=n_groups)
            idx = np.concatenate([idx_by_group[g] for g in picks]) if n_groups else np.array([], dtype=int)
            if len(idx) < 2:
                continue
            boots[b] = values[idx].mean()
        boots = boots[~np.isnan(boots)]
        lo, hi = (np.percentile(boots, [2.5, 97.5]) if len(boots) else (np.nan, np.nan))
        out[label] = [float(lo), float(hi)]
        out[f"{label}_n_clusters"] = int(n_groups)
    return out


def dual_significant(ci_session, ci_trade):
    def excl0(ci):
        lo, hi = ci
        return (not np.isnan(lo)) and (not np.isnan(hi)) and (lo > 0 or hi < 0)
    return bool(excl0(ci_session) and excl0(ci_trade))


def far_stats(far_df):
    boot = dual_clustered_bootstrap_mean(far_df["Qrev"].to_numpy(), far_df["sess_tag"].to_numpy(),
                                          far_df["trade_block_id"].to_numpy())
    sig = dual_significant(boot["session_block_ci"], boot["trade_block_ci"])
    return {
        "mean": boot["mean"], "n": boot["n"],
        "session_ci": boot["session_block_ci"], "session_n_clusters": boot["session_block_ci_n_clusters"],
        "trade_ci": boot["trade_block_ci"], "trade_n_clusters": boot["trade_block_ci_n_clusters"],
        "dual_significant": sig,
        "sign": "+" if boot["mean"] > 0 else ("-" if boot["mean"] < 0 else "0"),
        "econ_relevant_vs_C1": bool(abs(boot["mean"]) >= C1_COST_HURDLE_TICKS) if boot["n"] else None,
    }


# ============================================================= load
disc_df = load_and_filter(DISCOVERY_PATH, DISCOVERY_DATES)
conf_df = load_and_filter(CONFIRM_PATH, CONFIRMATION_DATES)
disc_df = assign_trade_block(disc_df)
conf_df = assign_trade_block(conf_df)
disc_t, disc_nzero, disc_edges = assign_terciles(disc_df)
conf_t, conf_nzero, conf_edges = assign_terciles(conf_df)

disc_sub = build_Qrev_H(disc_t, H_TARGET)
conf_sub = build_Qrev_H(conf_t, H_TARGET)
disc_far = disc_sub[disc_sub["tercile"] == "far"].copy()
conf_far = conf_sub[conf_sub["tercile"] == "far"].copy()

baseline_disc = far_stats(disc_far)
baseline_conf = far_stats(conf_far)
log("=" * 100)
log(f"[check] baseline reproduction, discovery H={H_TARGET} far: mean={baseline_disc['mean']:.4f}t "
    f"(target 7.8292) session_CI={baseline_disc['session_ci']} (target [1.1502,16.2299]) "
    f"trade_CI={baseline_disc['trade_ci']} (target [0.4435,16.5910]) n={baseline_disc['n']} (target 5902) "
    f"n_sess_clusters={baseline_disc['session_n_clusters']} (target 28)")
log(f"[check] baseline reproduction, confirmation H={H_TARGET} far: mean={baseline_conf['mean']:.4f}t "
    f"(target 1.9980) session_CI={baseline_conf['session_ci']} (target [-7.1553,133.4839]) "
    f"trade_CI={baseline_conf['trade_ci']} (target [-6.1466,133.4839]) n={baseline_conf['n']} (target 1010) "
    f"n_sess_clusters={baseline_conf['session_n_clusters']} (target 3)")
assert abs(baseline_disc["mean"] - 7.8292104371399525) < 1e-6, "discovery baseline mismatch"
assert abs(baseline_conf["mean"] - 1.998019801980198) < 1e-6, "confirmation baseline mismatch"
assert baseline_disc["session_n_clusters"] == 28 and baseline_conf["session_n_clusters"] == 3
log("[check] EXACT match to m2m3_signed_decomposition.json reported numbers -- proceeding with attacks.")
log("=" * 100)

results = {"h_target": H_TARGET, "rng_seed": RNG_SEED, "nboot": NBOOT,
           "c1_cost_hurdle_ticks": C1_COST_HURDLE_TICKS,
           "baseline": {"discovery": baseline_disc, "confirmation": baseline_conf}}


# ============================================================= A1/A2: drop most-influential session(s)
def session_influence_table(far_df):
    total_sum = far_df["Qrev"].sum()
    total_n = len(far_df)
    g = far_df.groupby("sess_tag")["Qrev"].agg(["sum", "count", "mean"])
    g["new_mean_if_removed"] = (total_sum - g["sum"]) / (total_n - g["count"])
    g["baseline_mean"] = total_sum / total_n
    g["drop_in_mean"] = g["baseline_mean"] - g["new_mean_if_removed"]
    return g.sort_values("drop_in_mean", ascending=False)


disc_infl = session_influence_table(disc_far)
conf_infl = session_influence_table(conf_far)
log("[A1/A2] discovery session influence ranking (most mean-reduction-if-removed first):")
log(disc_infl.to_string())
log("[A1/A2] confirmation session influence ranking:")
log(conf_infl.to_string())

top1_disc = [disc_infl.index[0]]
top3_disc = list(disc_infl.index[:3])
top1_conf = [conf_infl.index[0]]

a1_disc = far_stats(disc_far[~disc_far["sess_tag"].isin(top1_disc)])
a2_disc = far_stats(disc_far[~disc_far["sess_tag"].isin(top3_disc)])
a1_conf = far_stats(conf_far[~conf_far["sess_tag"].isin(top1_conf)])

results["A1_drop_single_most_influential_session"] = {
    "discovery": {"dropped_session": top1_disc, **a1_disc},
    "confirmation": {"dropped_session": top1_conf, **a1_conf},
}
results["A2_drop_top3_most_influential_sessions"] = {
    "discovery": {"dropped_sessions": top3_disc, **a2_disc},
}
log(f"[A1] discovery, drop {top1_disc}: mean {baseline_disc['mean']:.3f}t -> {a1_disc['mean']:.3f}t, "
    f"dual_sig={a1_disc['dual_significant']}, sign={a1_disc['sign']}")
log(f"[A2] discovery, drop {top3_disc}: mean {baseline_disc['mean']:.3f}t -> {a2_disc['mean']:.3f}t, "
    f"dual_sig={a2_disc['dual_significant']}, sign={a2_disc['sign']}")
log(f"[A1] confirmation, drop {top1_conf}: mean {baseline_conf['mean']:.3f}t -> {a1_conf['mean']:.3f}t, "
    f"dual_sig={a1_conf['dual_significant']}, sign={a1_conf['sign']}")


# ============================================================= A3: leave-one-session-out
def loso(far_df, all_sessions_label):
    out = []
    for s in sorted(far_df["sess_tag"].unique()):
        sub = far_df[far_df["sess_tag"] != s]
        st = far_stats(sub)
        out.append({"held_out_session": s, "n_removed": int((far_df["sess_tag"] == s).sum()),
                    "mean": st["mean"], "sign": st["sign"], "dual_significant": st["dual_significant"],
                    "session_ci": st["session_ci"], "trade_ci": st["trade_ci"]})
    return out


loso_disc = loso(disc_far, "discovery")
loso_conf = loso(conf_far, "confirmation")
disc_means = np.array([r["mean"] for r in loso_disc])
conf_means = np.array([r["mean"] for r in loso_conf])
results["A3_leave_one_session_out"] = {
    "discovery": {
        "n_sessions_iterated": len(loso_disc),
        "recomputed_mean_min": float(disc_means.min()), "recomputed_mean_max": float(disc_means.max()),
        "recomputed_mean_median": float(np.median(disc_means)),
        "n_sign_flips_to_negative": int((disc_means < 0).sum()),
        "n_still_dual_significant": int(sum(r["dual_significant"] for r in loso_disc)),
        "per_session": loso_disc,
    },
    "confirmation": {
        "n_sessions_iterated": len(loso_conf),
        "recomputed_mean_min": float(conf_means.min()), "recomputed_mean_max": float(conf_means.max()),
        "recomputed_mean_median": float(np.median(conf_means)),
        "n_sign_flips_to_negative": int((conf_means < 0).sum()),
        "n_still_dual_significant": int(sum(r["dual_significant"] for r in loso_conf)),
        "per_session": loso_conf,
    },
}
log(f"[A3] discovery LOSO over {len(loso_disc)} sessions: recomputed mean range "
    f"[{disc_means.min():.3f}, {disc_means.max():.3f}]t, median={np.median(disc_means):.3f}t, "
    f"sign flips to negative in {int((disc_means < 0).sum())}/{len(loso_disc)} removals, "
    f"still dual-significant in {sum(r['dual_significant'] for r in loso_disc)}/{len(loso_disc)} removals")
log(f"[A3] confirmation LOSO over {len(loso_conf)} sessions (of only 3 total contributing far rows): "
    f"recomputed mean range [{conf_means.min():.3f}, {conf_means.max():.3f}]t, "
    f"sign flips to negative in {int((conf_means < 0).sum())}/{len(loso_conf)} removals")


# ============================================================= A4: median split by session-range vol proxy
def session_range_proxy(df, sessions):
    """Realized session range in ticks from mid_last_t, computed over ALL rows for that session in
    the file (not restricted to far tercile or nonzero position) -- an in-file, no-new-data proxy
    for 'session volatility' since sigma460 is not a column of decision_outcomes.parquet (only of
    the separate M5 action_substrate)."""
    out = {}
    for s in sessions:
        sub = df[df["sess_tag"] == s]
        out[s] = float((sub["mid_last_t"].max() - sub["mid_last_t"].min()) / TICK)
    return out


disc_sessions_far = sorted(disc_far["sess_tag"].unique())
vol_proxy = session_range_proxy(disc_df, sorted(disc_df["sess_tag"].unique()))
vol_series = pd.Series(vol_proxy)
med = vol_series.median()
hi_vol_sessions = set(vol_series[vol_series >= med].index)
lo_vol_sessions = set(vol_series[vol_series < med].index)
log(f"[A4] discovery session-range vol proxy (ticks): median={med:.1f}, "
    f"hi-vol sessions={len(hi_vol_sessions)}, lo-vol sessions={len(lo_vol_sessions)}")

a4_hi = far_stats(disc_far[disc_far["sess_tag"].isin(hi_vol_sessions)])
a4_lo = far_stats(disc_far[disc_far["sess_tag"].isin(lo_vol_sessions)])
results["A4_median_split_session_range_vol_proxy"] = {
    "vol_proxy_definition": "session realized range (max(mid_last_t)-min(mid_last_t)) in ticks, "
                              "all rows of that session in decision_outcomes.parquet; sigma460 not "
                              "present in this file (only in M5's action_substrate) -- disclosed proxy",
    "median_ticks": float(med),
    "n_sessions_hi": len(hi_vol_sessions), "n_sessions_lo": len(lo_vol_sessions),
    "hi_vol": a4_hi, "lo_vol": a4_lo,
}
log(f"[A4] hi-vol half: mean={a4_hi['mean']:.3f}t n={a4_hi['n']} sess_CI={a4_hi['session_ci']} "
    f"trade_CI={a4_hi['trade_ci']} dual_sig={a4_hi['dual_significant']}")
log(f"[A4] lo-vol half: mean={a4_lo['mean']:.3f}t n={a4_lo['n']} sess_CI={a4_lo['session_ci']} "
    f"trade_CI={a4_lo['trade_ci']} dual_sig={a4_lo['dual_significant']}")


# ============================================================= A5: approximate contract-quarter split
def third_friday(year, month):
    cal = calendar.monthcalendar(year, month)
    fridays = [w[calendar.FRIDAY] for w in cal if w[calendar.FRIDAY] != 0]
    return pd.Timestamp(year, month, fridays[2])


# Standard CME quarterly-index-futures roll convention: front month rolls ~8 calendar days before
# the 3rd Friday of the CURRENT (expiring) contract month. This substrate has no literal contract
# field (per-session decision_outcomes.parquet is a back-adjusted continuous merge per CLAUDE.md),
# so this is a disclosed calendar-quarter APPROXIMATION of which quarterly contract was front-month
# on each date, not an exact vendor roll-date match.
roll_sep25 = third_friday(2025, 9) - pd.Timedelta(days=8)    # ~2025-09-11 -> U5/Z5 boundary
roll_dec25 = third_friday(2025, 12) - pd.Timedelta(days=8)   # ~2025-12-11 -> Z5/H6 boundary
roll_mar26 = third_friday(2026, 3) - pd.Timedelta(days=8)    # ~2026-03-12 -> H6/M6 boundary


def contract_bucket(sess_tag):
    d = pd.Timestamp(sess_tag[:4] + "-" + sess_tag[4:6] + "-" + sess_tag[6:8])
    if d < roll_sep25:
        return "U5(Sep25)"
    elif d < roll_dec25:
        return "Z5(Dec25)"
    elif d < roll_mar26:
        return "H6(Mar26)"
    else:
        return "M6(Jun26)"


disc_far = disc_far.copy()
disc_far["contract_bucket"] = disc_far["sess_tag"].map(contract_bucket)
bucket_counts = disc_far.groupby("contract_bucket")["sess_tag"].nunique().to_dict()
log(f"[A5] approx contract-quarter buckets (roll cutoffs: {roll_sep25.date()}, {roll_dec25.date()}, "
    f"{roll_mar26.date()}), sessions contributing far rows per bucket: {bucket_counts}")

a5 = {}
for b in sorted(disc_far["contract_bucket"].unique()):
    sub = disc_far[disc_far["contract_bucket"] == b]
    st = far_stats(sub)
    a5[b] = {"n_sessions": int(sub["sess_tag"].nunique()), **st}
    log(f"[A5] {b}: mean={st['mean']:.3f}t n={st['n']} n_sessions={sub['sess_tag'].nunique()} "
        f"sess_CI={st['session_ci']} trade_CI={st['trade_ci']} dual_sig={st['dual_significant']}")
results["A5_approx_contract_quarter_split"] = {
    "roll_cutoffs_used": {"U5_Z5": str(roll_sep25.date()), "Z5_H6": str(roll_dec25.date()),
                            "H6_M6": str(roll_mar26.date())},
    "caveat": "decision_outcomes.parquet has no literal contract-month field; buckets are a "
              "disclosed calendar-quarter approximation to standard CME roll timing, not exact.",
    "by_bucket": a5,
}


# ============================================================= A6: confound check vs |M|
def confound_check(sub_df, label):
    absD = sub_df["D_t"].abs().to_numpy()
    absM = sub_df["M"].abs().to_numpy()
    corr = float(np.corrcoef(absD, absM)[0, 1])
    by_tercile = sub_df.groupby("tercile", observed=True)["M"].apply(lambda x: float(x.abs().mean())).to_dict()
    return {"corr_absD_absM": corr, "mean_absM_by_tercile": by_tercile}


a6_disc = confound_check(disc_sub, "discovery")
a6_conf = confound_check(conf_sub, "confirmation")
results["A6_confound_check_vs_M"] = {"discovery": a6_disc, "confirmation": a6_conf}
log(f"[A6] discovery: corr(|D_t|,|M|)={a6_disc['corr_absD_absM']:.4f}, "
    f"mean|M| by tercile={a6_disc['mean_absM_by_tercile']}")
log(f"[A6] confirmation: corr(|D_t|,|M|)={a6_conf['corr_absD_absM']:.4f}, "
    f"mean|M| by tercile={a6_conf['mean_absM_by_tercile']}")

# also: does controlling for |M| linearly kill the far-tercile reversion effect? Simple OLS check
# (Qrev ~ far_dummy + |M|) restricted to near+far rows, discovery only, H=60, session-clustered SE
# via the same session-block bootstrap machinery applied to the OLS coefficient.
near_far = disc_sub[disc_sub["tercile"].isin(["near", "far"])].copy()
near_far["far_dummy"] = (near_far["tercile"] == "far").astype(float)
X = np.column_stack([np.ones(len(near_far)), near_far["far_dummy"].to_numpy(), near_far["M"].abs().to_numpy()])
y = near_far["Qrev"].to_numpy()
beta, *_ = np.linalg.lstsq(X, y, rcond=None)
raw_far_minus_near = float(near_far.loc[near_far["far_dummy"] == 1, "Qrev"].mean() -
                            near_far.loc[near_far["far_dummy"] == 0, "Qrev"].mean())
results["A6_ols_far_dummy_controlling_for_absM"] = {
    "raw_far_minus_near_diff_ticks": raw_far_minus_near,
    "ols_far_dummy_coef_ticks_controlling_for_absM": float(beta[1]),
    "ols_absM_coef": float(beta[2]),
    "note": "near vs far Q_reversion difference, with and without controlling for |M| (SolarWave "
            "wave-value magnitude, already present in decision_outcomes.parquet) -- if the far-dummy "
            "coefficient survives near-unchanged, the tercile effect is not simply relabeling |M|.",
}
log(f"[A6] OLS check: raw far-near diff={raw_far_minus_near:.3f}t, "
    f"far-dummy coef controlling for |M|={beta[1]:.3f}t (|M| coef={beta[2]:.3f})")


# ============================================================= A7: independent no-lookahead spot check
poc = pd.read_parquet(POC_1S_PATH, columns=["time", "sess_tag", "mid_last"])
poc = poc.sort_values(["sess_tag", "time"]).reset_index(drop=True)
rng_spot = np.random.default_rng(20260810)
spot_idx = rng_spot.choice(len(disc_far), size=5, replace=False)
spot_rows = disc_far.iloc[spot_idx]

spot_results = []
for _, row in spot_rows.iterrows():
    sess = row["sess_tag"]
    t0 = row["time"]
    t1 = t0 + pd.Timedelta(seconds=H_TARGET)
    ref = poc[poc["sess_tag"] == sess].set_index("time")["mid_last"]
    # strictly t-or-earlier for the anchor, t+H (first available tick at/after t+H, matching
    # 03_diagnostics.py's own searchsorted-forward convention) for the outcome -- no data beyond
    # t+H is used to construct the t+H outcome, and no data beyond t is used for the anchor
    idx = ref.index
    p0 = idx.searchsorted(t0)
    p1 = idx.searchsorted(t1)
    assert idx[p0] == t0, f"anchor timestamp {t0} not found exactly in poc_1s_full for {sess}"
    mid0 = float(ref.iloc[p0])
    mid1 = float(ref.iloc[p1]) if p1 < len(idx) and (idx[p1] - t1) <= pd.Timedelta(seconds=2) else None
    recompute_raw = ((mid1 - mid0) / TICK) if mid1 is not None else None
    stored_raw = float(row["raw_markout"])
    match = (recompute_raw is not None) and (abs(recompute_raw - stored_raw) < 1e-6)
    spot_results.append({
        "sess_tag": sess, "t0": str(t0), "t1_target": str(t1),
        "mid_last_t0_independent": mid0, "mid_last_t1_independent": mid1,
        "recomputed_raw_markout_ticks": recompute_raw,
        "stored_raw_markout_ticks_from_decision_outcomes": stored_raw,
        "match_within_1e-6": bool(match),
    })
    log(f"[A7] {sess} t0={t0} : independent recompute raw_markout={recompute_raw}, "
        f"stored={stored_raw}, match={match}")

results["A7_independent_lookahead_spot_check"] = {
    "n_spot_checked": len(spot_results),
    "n_matched": int(sum(r["match_within_1e-6"] for r in spot_results)),
    "rows": spot_results,
    "note": "recomputes (mid_last(t+H)-mid_last(t))/tick from the independent 1s poc_1s_full.parquet "
            "series (which decision_outcomes.parquet was itself built from), anchor row required to "
            "match t0 exactly (strictly t-or-earlier data used for the anchor) and the outcome row is "
            "the first available tick at/after t+H (strictly forward data, matching the original "
            "construction's own searchsorted-forward convention in 03_diagnostics.py) -- no reuse of "
            "any precomputed decision_outcomes.parquet column in the recomputation itself.",
}


# ============================================================= write outputs
json_path = os.path.join(OUT_DIR, "05_stress_M2M3_far_tercile_reversion.json")
with open(json_path, "w") as f:
    json.dump(results, f, indent=2, default=lambda o: None if isinstance(o, float) and np.isnan(o) else o)
log(f"[write] {json_path}")

txt_path = os.path.join(OUT_DIR, "05_stress_M2M3_far_tercile_reversion_log.txt")
with open(txt_path, "w") as f:
    f.write("\n".join(log_lines))
log(f"[write] {txt_path}")
