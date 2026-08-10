"""ICT01 -- first-pass sweep/MSS test. Directive: CONTINUOUS_EVOLUTION addendum ICT01+ICT02.

Swing point: a local extreme confirmed causally-knowable only K bars after it forms (strictly
greater/less than the K bars on both sides; "known" starting the bar AFTER the K-th confirming
bar closes -- never back-dated). SWEEP = price trading (intrabar high/low) beyond the most
recent causally-known opposite swing point. MSS/BOS = price CLOSING beyond that same swing point
(a strict superset relationship: every MSS bar is also a SWEEP bar, since close <= high). This
lets "SWEEP-ONLY vs SWEEP+MSS" be tested with ZERO predictor/outcome overlap: MSS is same-bar
information (the event bar's own completed close), so the forward-20-bar outcome window starts
cleanly at t+1, identical to EXP01/ICT02's convention.

Preregistered, single value, no sweep: K=5 bars (15 min on this 3-min bar table).
"""
import os, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
os.makedirs(OUT, exist_ok=True)
K = 5  # preregistered swing confirmation lookback, bars each side

cols = ["t_idx", "high", "low", "close", "M", "position_B", "sigma460_atr_proxy_pts",
        "bar_pnl_B_nq_dollars", "year", "is_health_only_bar"]
u0 = pd.read_parquet(os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet"),
                      columns=cols).sort_values("t_idx").reset_index(drop=True)
n = len(u0)
print(f"[ICT01] loaded {n} bars, K={K}", flush=True)

canon_net = u0.loc[~u0["is_health_only_bar"], "bar_pnl_B_nq_dollars"].sum()
print(f"[ICT01] correctness gate: canonical B-NQ net = {canon_net:.2f} (must be 301915.92)", flush=True)
assert abs(canon_net - 301915.92) < 0.01, "CORRECTNESS GATE FAILED -- do not proceed"

high = u0["high"].to_numpy(); low = u0["low"].to_numpy(); close = u0["close"].to_numpy()


def backward_max(x, k):
    s = pd.Series(x).shift(1).rolling(k, min_periods=k).max()
    return s.to_numpy()


def forward_max(x, k):
    rev = pd.Series(x[::-1]).shift(1).rolling(k, min_periods=k).max()
    return rev.to_numpy()[::-1]


def backward_min(x, k):
    s = pd.Series(x).shift(1).rolling(k, min_periods=k).min()
    return s.to_numpy()


def forward_min(x, k):
    rev = pd.Series(x[::-1]).shift(1).rolling(k, min_periods=k).min()
    return rev.to_numpy()[::-1]


left_max, right_max = backward_max(high, K), forward_max(high, K)
left_min, right_min = backward_min(low, K), forward_min(low, K)

cand_high = (high > left_max) & (high >= right_max)
cand_low = (low < left_min) & (low <= right_min)
print(f"[ICT01] swing-high candidates: {cand_high.sum()}, swing-low candidates: {cand_low.sum()}", flush=True)

# usable_from = i + K + 1 (strictly AFTER the K-bar right-side confirmation resolves at i+K)
usable_from_high = np.where(cand_high, np.arange(n) + K + 1, -1)
usable_from_low = np.where(cand_low, np.arange(n) + K + 1, -1)

slot_high = np.full(n + 1, np.nan)
slot_low = np.full(n + 1, np.nan)
for i in np.where(cand_high)[0]:
    uf = usable_from_high[i]
    if uf < n:
        slot_high[uf] = high[i]
for i in np.where(cand_low)[0]:
    uf = usable_from_low[i]
    if uf < n:
        slot_low[uf] = low[i]

known_swing_high = pd.Series(slot_high[:n]).ffill().to_numpy()
known_swing_low = pd.Series(slot_low[:n]).ffill().to_numpy()
print(f"[ICT01] bars with a known swing high: {(~np.isnan(known_swing_high)).sum()}, "
      f"known swing low: {(~np.isnan(known_swing_low)).sum()}", flush=True)

# ---------------------------------------------------------------- SWEEP (intrabar breach) + MSS (close-confirmed breach)
breach_up = high > known_swing_high
breach_dn = low < known_swing_low
ref_changed_up = np.r_[True, known_swing_high[1:] != known_swing_high[:-1]]
ref_changed_dn = np.r_[True, known_swing_low[1:] != known_swing_low[:-1]]
prev_breach_up = np.r_[False, breach_up[:-1]]
prev_breach_dn = np.r_[False, breach_dn[:-1]]
sweep_up_event = breach_up & (~prev_breach_up | ref_changed_up)
sweep_dn_event = breach_dn & (~prev_breach_dn | ref_changed_dn)
mss_up = close > known_swing_high   # close-confirmed
mss_dn = close < known_swing_low

u0["sweep_up_event"] = sweep_up_event
u0["sweep_dn_event"] = sweep_dn_event
u0["mss_confirmed_up"] = sweep_up_event & mss_up
u0["mss_confirmed_dn"] = sweep_dn_event & mss_dn
print(f"[ICT01] sweep_up_event bars: {sweep_up_event.sum()}, sweep_dn_event bars: {sweep_dn_event.sum()}")
print(f"[ICT01] of which MSS-confirmed (close beyond, same bar): "
      f"up {u0['mss_confirmed_up'].sum()}, dn {u0['mss_confirmed_dn'].sum()}")

# ---------------------------------------------------------------- forward-20-bar P&L, vectorized cumsum (same as ICT02)
bpnl = u0["bar_pnl_B_nq_dollars"].to_numpy()
cs = np.concatenate([[0.0], np.cumsum(bpnl)])
t_idx_all = u0["t_idx"].to_numpy()
max_t = t_idx_all.max()


def fwd20(t_arr):
    t_arr = np.asarray(t_arr)
    out = np.full(len(t_arr), np.nan)
    valid = t_arr + 20 <= max_t
    out[valid] = cs[t_arr[valid] + 21] - cs[t_arr[valid] + 1]
    return out


# ---------------------------------------------------------------- build event table: sweep events while position_B != 0, canonical window
events = []
for dirn, ev_col, mss_col in [(+1, "sweep_up_event", "mss_confirmed_up"), (-1, "sweep_dn_event", "mss_confirmed_dn")]:
    ev = u0[u0[ev_col] & (u0["position_B"] != 0) & (~u0["is_health_only_bar"])].copy()
    ev["sweep_dir"] = dirn
    ev["confirmed_mss"] = ev[mss_col].astype(int)
    events.append(ev[["t_idx", "position_B", "M", "sigma460_atr_proxy_pts", "year", "sweep_dir", "confirmed_mss"]])
ev_all = pd.concat(events, ignore_index=True)
ev_all["side"] = ev_all["position_B"].astype(int)
ev_all["sweep_with_position"] = (np.sign(ev_all["sweep_dir"]) == np.sign(ev_all["side"])).astype(int)
ev_all["fwd20_pnl"] = fwd20(ev_all["t_idx"].to_numpy())
ev_all = ev_all.dropna(subset=["fwd20_pnl"])
ev_all["M_abs"] = ev_all["M"].abs()
print(f"\n[ICT01] {len(ev_all)} sweep events on position_B!=0 canonical bars with a complete fwd20 window", flush=True)
print(f"[ICT01] sweep_with_position=1 (continuation-type): {ev_all['sweep_with_position'].sum()}, "
      f"=0 (adverse-type): {(1 - ev_all['sweep_with_position']).sum()}")
print(f"[ICT01] MSS-confirmed events: {ev_all['confirmed_mss'].sum()} of {len(ev_all)} "
      f"({ev_all['confirmed_mss'].mean():.1%})")

ev_all["vol_tercile"] = pd.qcut(ev_all["sigma460_atr_proxy_pts"], 3, labels=["low", "mid", "high"], duplicates="drop")
ev_all["vol_z"] = ev_all["vol_tercile"].cat.codes
ev_all["bucket"] = pd.qcut(ev_all["M_abs"], 3, labels=["weak", "mid", "strong"], duplicates="drop").astype(str) + "_" + ev_all["vol_tercile"].astype(str)
ev_all["bucket_mean"] = ev_all.groupby("bucket", observed=True)["fwd20_pnl"].transform("mean")
ev_all["resid_pnl"] = ev_all["fwd20_pnl"] - ev_all["bucket_mean"]
ev_all.to_csv(os.path.join(OUT, "ict01_events.csv"), index=False)


def ols_r2(df_, X_cols, y_col):
    d = df_.dropna(subset=X_cols + [y_col])
    X = d[X_cols].to_numpy(dtype=float)
    X = np.column_stack([np.ones(len(X)), X])
    y = d[y_col].to_numpy(dtype=float)
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    yhat = X @ coef
    ss_res = np.sum((y - yhat) ** 2); ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan
    return r2, coef, len(d)


baseline_cols = ["M_abs", "vol_z"]
r2_base, coef_base, n_base = ols_r2(ev_all, baseline_cols, "fwd20_pnl")
print(f"\n[ICT01] baseline R^2 (fwd20_pnl ~ M_abs + vol_z), on the sweep-event subset: {r2_base:.5f} (n={n_base})")

print("\n" + "=" * 90 + "\nRAW / RESIDUALIZED CORRELATION -- SWEEP-ONLY (sweep_with_position)\n" + "=" * 90)
d = ev_all.dropna(subset=["sweep_with_position", "fwd20_pnl", "resid_pnl"])
rho_raw = float(d["sweep_with_position"].corr(d["fwd20_pnl"], method="spearman"))
rho_res = float(d["sweep_with_position"].corr(d["resid_pnl"], method="spearman"))
print(f"  Spearman(sweep_with_position, fwd20_pnl) raw={rho_raw:+.4f}  residualized={rho_res:+.4f}  (n={len(d)})")

r2_sweep, coef_sweep, n_sweep = ols_r2(ev_all, baseline_cols + ["sweep_with_position"], "fwd20_pnl")
print(f"  SWEEP-ONLY model R^2={r2_sweep:.5f} (dR2 vs baseline = {r2_sweep - r2_base:+.5f}, n={n_sweep}, "
      f"coef_sign={'+' if coef_sweep[-1] > 0 else '-'})")

print("\n" + "=" * 90 + "\nSWEEP+MSS: does close-confirmation add information beyond sweep direction alone?\n" + "=" * 90)
r2_mss, coef_mss, n_mss = ols_r2(ev_all, baseline_cols + ["sweep_with_position", "confirmed_mss"], "fwd20_pnl")
print(f"  SWEEP+MSS model R^2={r2_mss:.5f} (dR2 vs SWEEP-ONLY = {r2_mss - r2_sweep:+.5f}, n={n_mss}, "
      f"confirmed_mss coef_sign={'+' if coef_mss[-1] > 0 else '-'})")

ev_all["interact"] = ev_all["sweep_with_position"] * ev_all["confirmed_mss"]
r2_mss2, coef_mss2, n_mss2 = ols_r2(ev_all, baseline_cols + ["sweep_with_position", "confirmed_mss", "interact"], "fwd20_pnl")
print(f"  SWEEP+MSS+interaction model R^2={r2_mss2:.5f} (dR2 vs SWEEP-ONLY = {r2_mss2 - r2_sweep:+.5f}, n={n_mss2})")

# residualized Spearman of confirmed_mss (within sweep-event subset, controlling for sweep direction via bucket)
d2 = ev_all.copy()
d2["bucket2"] = d2["bucket"].astype(str) + "_" + d2["sweep_with_position"].astype(str)
d2["bucket2_mean"] = d2.groupby("bucket2", observed=True)["fwd20_pnl"].transform("mean")
d2["resid_pnl2"] = d2["fwd20_pnl"] - d2["bucket2_mean"]
rho_mss_res = float(d2["confirmed_mss"].corr(d2["resid_pnl2"], method="spearman"))
print(f"  Spearman(confirmed_mss, resid_pnl | M-tercile x vol-tercile x sweep-direction bucket) = {rho_mss_res:+.4f}")

# ---------------------------------------------------------------- year-by-year stability
print("\n" + "=" * 90 + "\nYEAR-BY-YEAR STABILITY -- sweep_with_position residualized Spearman\n" + "=" * 90)
yby = []
for yr, g in ev_all.dropna(subset=["sweep_with_position", "resid_pnl"]).groupby("year"):
    if len(g) < 50:
        continue
    rho_yr = float(g["sweep_with_position"].corr(g["resid_pnl"], method="spearman"))
    yby.append({"year": int(yr), "n": len(g), "spearman_resid": rho_yr})
yby_df = pd.DataFrame(yby)
print(yby_df.round(4).to_string(index=False))

# 2022-2025-only chronology
sub_2225 = ev_all[ev_all["year"].between(2022, 2025)]
print(f"\n[ICT01] 2022-2025 sweep-event count: {len(sub_2225)}, sum fwd20_pnl (observational, no policy change): "
      f"${sub_2225['fwd20_pnl'].sum():,.2f}")

# ---------------------------------------------------------------- right-tail audit: sweep/MSS incidence in top/bottom-20 blocks' lifetime
print("\n" + "=" * 90 + "\nRIGHT-TAIL AUDIT: sweep-event incidence within top-20 / bottom-20 all-time Product-B blocks\n" + "=" * 90)
u0b = pd.read_parquet(os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet"),
                       columns=["t_idx", "block_id_B", "run_pnl_B_dollars", "is_health_only_bar"])
canon_b = u0b[~u0b["is_health_only_bar"]]
block_net = canon_b.groupby("block_id_B")["run_pnl_B_dollars"].last()
top20 = set(block_net.nlargest(20).index)
bot20 = set(block_net.nsmallest(20).index)
bid_map = canon_b.set_index("t_idx")["block_id_B"]
ev_all["block_id_B"] = ev_all["t_idx"].map(bid_map)
top_events = ev_all[ev_all["block_id_B"].isin(top20)]
bot_events = ev_all[ev_all["block_id_B"].isin(bot20)]
print(f"top-20 blocks: {len(top_events)} sweep-events total, "
      f"{top_events['sweep_with_position'].mean() if len(top_events) else float('nan'):.2%} sweep_with_position, "
      f"{top_events['confirmed_mss'].mean() if len(top_events) else float('nan'):.2%} MSS-confirmed")
print(f"bottom-20 blocks: {len(bot_events)} sweep-events total, "
      f"{bot_events['sweep_with_position'].mean() if len(bot_events) else float('nan'):.2%} sweep_with_position, "
      f"{bot_events['confirmed_mss'].mean() if len(bot_events) else float('nan'):.2%} MSS-confirmed")

summary = {
    "K": K, "n_sweep_events": int(len(ev_all)),
    "baseline_r2": float(r2_base), "sweep_only_r2": float(r2_sweep), "sweep_only_dr2": float(r2_sweep - r2_base),
    "sweep_mss_r2": float(r2_mss), "sweep_mss_dr2_vs_sweep_only": float(r2_mss - r2_sweep),
    "rho_sweep_with_position_raw": rho_raw, "rho_sweep_with_position_resid": rho_res,
    "rho_confirmed_mss_resid": rho_mss_res,
    "year_by_year": yby_df.to_dict("records"),
    "n_2225": int(len(sub_2225)), "sum_2225_fwd20": float(sub_2225["fwd20_pnl"].sum()),
    "top20_n_events": int(len(top_events)), "bot20_n_events": int(len(bot_events)),
}
json.dump(summary, open(os.path.join(OUT, "ict01_summary.json"), "w"), indent=2, default=str)
print("\nICT01 first-pass analysis complete.")
