"""U7 step1 -- bar-level and entry-block-level distributional comparison of state variables
between P0 (2022-2025), P1 (106-session 2026 canonical stub, 2026-01-02..2026-05-29) and P2
(is_health_only_bar==True, 2026-06-01..2026-07-31). Diagnostic only, no construction.
"""
import os, json
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(ROOT, "runs", "U7_2026_TIMING_REGIME", "out")
os.makedirs(OUT, exist_ok=True)

df = pd.read_parquet(os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet"))
print(f"[U7] loaded U0 state table: {df.shape}")

P0 = (~df["is_health_only_bar"]) & (df["year"] < 2026)
P1 = (~df["is_health_only_bar"]) & (df["year"] == 2026)
P2 = df["is_health_only_bar"]
P1P2 = df["year"] == 2026

assert P0.sum() + P1.sum() + P2.sum() == len(df)
n_sess = lambda m: df.loc[m, "sess_date"].nunique()
print(f"[U7] P0 (2022-2025): {P0.sum()} bars, {n_sess(P0)} sessions")
print(f"[U7] P1 (2026 canonical stub): {P1.sum()} bars, {n_sess(P1)} sessions")
print(f"[U7] P2 (health-only Jun-Jul 2026): {P2.sum()} bars, {n_sess(P2)} sessions")
print(f"[U7] P1+P2 (all of year==2026): {P1P2.sum()} bars, {n_sess(P1P2)} sessions")


def eff_size(base, cmp):
    """Pooled-std standardized mean difference (Cohen's d, cmp - base) + percentile rank of
    cmp's median within base's empirical distribution."""
    base = base[~np.isnan(base)]
    cmp = cmp[~np.isnan(cmp)]
    if len(base) < 5 or len(cmp) < 5:
        return dict(n_base=len(base), n_cmp=len(cmp), cohens_d=np.nan, pct_rank=np.nan)
    pooled_std = np.sqrt((base.std(ddof=1) ** 2 + cmp.std(ddof=1) ** 2) / 2)
    d = (cmp.mean() - base.mean()) / pooled_std if pooled_std > 0 else np.nan
    pct_rank = (base < np.median(cmp)).mean() * 100.0
    return dict(
        n_base=len(base), n_cmp=len(cmp),
        mean_base=float(base.mean()), mean_cmp=float(cmp.mean()),
        median_base=float(np.median(base)), median_cmp=float(np.median(cmp)),
        std_base=float(base.std(ddof=1)), std_cmp=float(cmp.std(ddof=1)),
        cohens_d=float(d) if pooled_std > 0 else np.nan,
        pct_rank_of_cmp_median_in_base=float(pct_rank),
    )


# ============================================================= BAR-LEVEL variables
bar_vars = [
    "sigma460_atr_proxy_pts", "trend_efficiency_20", "range_efficiency_20",
    "clv_signed", "vwap_disp_atr", "M_slope_20", "M_change", "vote_dispersion",
    "vol_surprise", "range_over_atr", "short_term_vol_ratio", "vol_compression_ratio",
]

bar_rows = []
for v in bar_vars:
    base = df.loc[P0, v].to_numpy(dtype=float)
    for label, mask in [("P1_vs_P0", P1), ("P2_vs_P0", P2), ("P1P2_vs_P0", P1P2)]:
        cmp = df.loc[mask, v].to_numpy(dtype=float)
        r = eff_size(base, cmp)
        r.update(variable=v, comparison=label, level="bar")
        bar_rows.append(r)

bar_df = pd.DataFrame(bar_rows)
bar_df.to_csv(os.path.join(OUT, "step1_bar_level_shift.csv"), index=False)
print("\n[U7] BAR-LEVEL effect sizes (P1_vs_P0 rows):")
print(bar_df[bar_df.comparison == "P1_vs_P0"][
    ["variable", "mean_base", "mean_cmp", "cohens_d", "pct_rank_of_cmp_median_in_base"]
].to_string(index=False))

# ============================================================= ENTRY-BLOCK-LEVEL variables
entries = df[df["action_B"] == "ENTRY"].copy()
print(f"\n[U7] total ENTRY rows: {len(entries)}")
entries["period"] = np.select(
    [(~entries["is_health_only_bar"]) & (entries["year"] < 2026),
     (~entries["is_health_only_bar"]) & (entries["year"] == 2026),
     entries["is_health_only_bar"]],
    ["P0", "P1", "P2"], default="?"
)
print(entries["period"].value_counts())

entry_vars = ["clv_signed", "vwap_disp_atr", "M_slope_20", "M_change", "vote_dispersion",
              "vol_surprise", "sigma460_atr_proxy_pts", "trend_efficiency_20",
              "range_efficiency_20"]

eP0 = entries[entries.period == "P0"]
eP1 = entries[entries.period == "P1"]
eP2 = entries[entries.period == "P2"]
eP1P2 = entries[entries.period.isin(["P1", "P2"])]

entry_rows = []
for v in entry_vars:
    base = eP0[v].to_numpy(dtype=float)
    for label, sub in [("P1_vs_P0", eP1), ("P2_vs_P0", eP2), ("P1P2_vs_P0", eP1P2)]:
        cmp = sub[v].to_numpy(dtype=float)
        r = eff_size(base, cmp)
        r.update(variable=v, comparison=label, level="entry_block")
        entry_rows.append(r)

entry_df = pd.DataFrame(entry_rows)
entry_df.to_csv(os.path.join(OUT, "step1_entry_level_shift.csv"), index=False)
print("\n[U7] ENTRY-LEVEL effect sizes (P1_vs_P0 rows):")
print(entry_df[entry_df.comparison == "P1_vs_P0"][
    ["variable", "mean_base", "mean_cmp", "cohens_d", "pct_rank_of_cmp_median_in_base"]
].to_string(index=False))

# ============================================================= session_phase distribution of entries
phase_counts_raw = entries.groupby(["period", "session_phase"]).size().unstack(level=1).fillna(0)
phase_dist = phase_counts_raw.div(phase_counts_raw.sum(axis=1), axis=0)
phase_dist = phase_dist.reindex(["P0", "P1", "P2"])
phase_dist.to_csv(os.path.join(OUT, "step1_session_phase_entry_dist.csv"))
print("\n[U7] entry session_phase distribution (share of entries):")
print(phase_dist.round(4).to_string())

# raw counts too
phase_counts = entries.groupby(["period", "session_phase"]).size().unstack(level=1).fillna(0).astype(int)
phase_counts = phase_counts.reindex(["P0", "P1", "P2"])
phase_counts.to_csv(os.path.join(OUT, "step1_session_phase_entry_counts.csv"))

# ============================================================= reversal-frequency proxy: sign(M) flips / session
M = df["M"].to_numpy()
sess = df["sess_date"].to_numpy()
sign_M = np.sign(M)
# causal: flip relative to previous bar within the SAME session only
same_sess = np.r_[False, sess[1:] == sess[:-1]]
flip = same_sess & (sign_M != np.r_[np.nan, sign_M[:-1]]) & (sign_M != 0) & (np.r_[np.nan, sign_M[:-1]] != 0)
df["_M_sign_flip"] = flip

flips_per_sess = df.groupby(["sess_date"])["_M_sign_flip"].sum()
sess_meta = df.drop_duplicates("sess_date")[["sess_date", "year", "is_health_only_bar"]].set_index("sess_date")
flips_per_sess = flips_per_sess.to_frame("n_sign_flips").join(sess_meta)
flips_per_sess["period"] = np.select(
    [(~flips_per_sess["is_health_only_bar"]) & (flips_per_sess["year"] < 2026),
     (~flips_per_sess["is_health_only_bar"]) & (flips_per_sess["year"] == 2026),
     flips_per_sess["is_health_only_bar"]],
    ["P0", "P1", "P2"], default="?"
)
flips_per_sess.to_csv(os.path.join(OUT, "step1_M_sign_flips_per_session.csv"))
flip_summary = flips_per_sess.groupby("period")["n_sign_flips"].agg(["mean", "median", "std", "count"])
flip_summary = flip_summary.reindex(["P0", "P1", "P2"])
print("\n[U7] sign(M) flips per session:")
print(flip_summary.to_string())

# action_B == REVERSAL count per session
rev = df[df["action_B"] == "REVERSAL"]
rev_per_sess = rev.groupby("sess_date").size()
rev_per_sess = rev_per_sess.reindex(sess_meta.index, fill_value=0).to_frame("n_reversals").join(sess_meta)
rev_per_sess["period"] = np.select(
    [(~rev_per_sess["is_health_only_bar"]) & (rev_per_sess["year"] < 2026),
     (~rev_per_sess["is_health_only_bar"]) & (rev_per_sess["year"] == 2026),
     rev_per_sess["is_health_only_bar"]],
    ["P0", "P1", "P2"], default="?"
)
rev_per_sess.to_csv(os.path.join(OUT, "step1_reversal_actions_per_session.csv"))
rev_summary = rev_per_sess.groupby("period")["n_reversals"].agg(["mean", "median", "std", "count", "sum"])
rev_summary = rev_summary.reindex(["P0", "P1", "P2"])
print("\n[U7] action_B=='REVERSAL' events per session:")
print(rev_summary.to_string())

# ============================================================= gap behavior: first-bar-of-session |open - prior close|
first_bar = df.loc[df.groupby("sess_date")["t_idx"].idxmin()].sort_values("sess_date").reset_index(drop=True)
last_bar = df.loc[df.groupby("sess_date")["t_idx"].idxmax()].sort_values("sess_date").reset_index(drop=True)
prior_close = last_bar["close"].shift(1).to_numpy()  # prior session's LAST close, causal (only uses past sessions)
gap_pts = np.abs(first_bar["open"].to_numpy() - prior_close)
gap_df = pd.DataFrame({
    "sess_date": first_bar["sess_date"], "year": first_bar["year"],
    "is_health_only_bar": first_bar["is_health_only_bar"],
    "gap_pts": gap_pts, "sigma460_first_bar": first_bar["sigma460_atr_proxy_pts"].to_numpy(),
})
gap_df["gap_atr"] = np.where(gap_df["sigma460_first_bar"] > 0,
                              gap_df["gap_pts"] / gap_df["sigma460_first_bar"], np.nan)
gap_df["period"] = np.select(
    [(~gap_df["is_health_only_bar"]) & (gap_df["year"] < 2026),
     (~gap_df["is_health_only_bar"]) & (gap_df["year"] == 2026),
     gap_df["is_health_only_bar"]],
    ["P0", "P1", "P2"], default="?"
)
gap_df = gap_df.iloc[1:].reset_index(drop=True)  # drop first session (no prior close)
gap_df.to_csv(os.path.join(OUT, "step1_session_open_gap.csv"), index=False)
gap_summary = gap_df.groupby("period")[["gap_pts", "gap_atr"]].agg(["mean", "median", "std", "count"])
gap_summary = gap_summary.reindex(["P0", "P1", "P2"])
print("\n[U7] session-open gap (points and ATR units):")
print(gap_summary.to_string())

# ============================================================= assemble a compact JSON summary
summary = {
    "n_bars": {"P0": int(P0.sum()), "P1": int(P1.sum()), "P2": int(P2.sum())},
    "n_sessions": {"P0": n_sess(P0), "P1": n_sess(P1), "P2": n_sess(P2)},
    "n_entries": {"P0": int((entries.period == "P0").sum()), "P1": int((entries.period == "P1").sum()),
                  "P2": int((entries.period == "P2").sum())},
    "M_sign_flips_per_session": flip_summary.to_dict(orient="index"),
    "reversal_actions_per_session": rev_summary.to_dict(orient="index"),
    "session_open_gap_atr": gap_summary["gap_atr"].to_dict(orient="index") if hasattr(gap_summary["gap_atr"], "to_dict") else None,
}
with open(os.path.join(OUT, "step1_summary.json"), "w") as f:
    json.dump(summary, f, indent=2, default=str)

print("\n[U7] step1 complete. Outputs written to", OUT)
