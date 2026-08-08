"""SMV2Q_DIAGNOSTICS — pure measurement per frozen spec.yaml (seq 380).

Curves (dev <= 2026-05-31 primary; June-July 2026 only for master_exec, labeled CONSUMED):
  SOLAR_E10       runs/SM01_SUBSTRATE/out/e10_daily_py.csv                  (MNQ $, up to 10 MNQ)
  SOLAR_DUAL      runs/SMV2H_ONECONTRACT/out/solar_dual_htf_daily.csv       (MNQ $, up to 13 MNQ)
  BMOM_E2         ledger_E2_next_open.parquet net_c1_ticks x $5              (1-NQ $)
  MASTER_EXEC_NT  parity_daily_aligned.csv col nt, 2023-04-05/06 pair merged (MNQ $)
  MASTER_TWIN     parity_daily_aligned.csv col tw                            (MNQ $)
  SM14_MNQ        regen_daily_curves.csv col 355_SM14_ref_oldM(3,1)_MNQ      (1-MNQ $)

No gates, no selection. Deterministic (no RNG used).
"""
import sys, os
import numpy as np
import pandas as pd
from scipy import stats

REPO = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
os.chdir(REPO)
sys.path.insert(0, "src/analytics")
from sm01_solarsim import load_bars_3m

RUN = "runs/SMV2Q_DIAGNOSTICS"
OUT = f"{RUN}/out"
os.makedirs(OUT, exist_ok=True)

DEV_END = pd.Timestamp("2026-05-31")
K_SOLAR, K_BMOM = 0.728654, 2.934159      # frozen (SMV2M spec / task brief)
MNQ_PV = 2.0
NQ_FRICTION_PTS = 2 * 0.25 + 2 * 2.18 / 20.0   # 1-tick slip/side + Lifetime comm, 1-lot NQ RT = 0.718 pt

# ================================================================ load curves
e10 = pd.read_csv("runs/SM01_SUBSTRATE/out/e10_daily_py.csv", parse_dates=["sess"]).set_index("sess")["net"]
dual = pd.read_csv("runs/SMV2H_ONECONTRACT/out/solar_dual_htf_daily.csv", index_col=0, parse_dates=True).iloc[:, 0]
al = pd.read_csv("runs/SMV2M_MASTER_BUILD/out/parity_daily_aligned.csv", index_col=0, parse_dates=True)
reg = pd.read_csv("runs/SMV2H2_ONELOT_CONFIRM/out/regen_daily_curves.csv", index_col=0, parse_dates=True)
sm14 = reg["355_SM14_ref_oldM(3,1)_MNQ"]
bmledger = pd.read_parquet("runs/SMV2B_BMOM_EXEC_AUDIT/out/ledger_E2_next_open.parquet")
BM_raw = bmledger.groupby("sess")["net_c1_ticks"].sum() * 5.0
BM_raw.index = pd.to_datetime(BM_raw.index)

CAL_DEV = dual.index                                     # 1139 sessions == e10 dev == al dev
assert list(CAL_DEV) == list(e10.index[e10.index <= DEV_END])
assert list(CAL_DEV) == list(al.index[al.index <= DEV_END])
assert list(CAL_DEV) == list(sm14.index)

BM = BM_raw.reindex(CAL_DEV).fillna(0.0)                 # master session calendar, 0 on no-trade days

# master_exec: merge the 2023-04-05/06 data-gap boundary pair (as in SMV2M parity recompute)
nt_dev = al.loc[al.index <= DEV_END, "nt"].copy()
PAIR = (pd.Timestamp("2023-04-05"), pd.Timestamp("2023-04-06"))
merged_val = nt_dev.loc[PAIR[0]] + nt_dev.loc[PAIR[1]]
nt_merged = nt_dev.drop(index=PAIR[1])
nt_merged.loc[PAIR[0]] = merged_val
nt_merged = nt_merged.sort_index()
tw_dev = al.loc[al.index <= DEV_END, "tw"]

CURVES = {
    "SOLAR_E10": e10.loc[e10.index <= DEV_END],
    "SOLAR_DUAL": dual,
    "BMOM_E2": BM,
    "MASTER_EXEC_NT": nt_merged,
    "MASTER_TWIN": tw_dev,
    "SM14_MNQ": sm14,
}

# ---- reproduction crosschecks (written to out/, cited in REPORT) ----
rc = pd.read_csv("runs/SMV2H_ONECONTRACT/out/rerank_curves.csv", parse_dates=["sess"])
dc = pd.read_csv("runs/SMV2H_ONECONTRACT/out/daily_curves.csv", index_col=0, parse_dates=True)
twd = pd.read_csv("runs/SMV2M_MASTER_BUILD/out/twin_daily.csv", index_col=0, parse_dates=True).iloc[:, 0]
crosschecks = pd.DataFrame([
    {"check": "BM_E2_daily_sum_vs_rerank_BM_E2", "a": BM_raw.sum(), "b": rc["BM_E2"].sum(),
     "pass": bool(np.isclose(BM_raw.sum(), rc["BM_E2"].sum()))},
    {"check": "SM14_regen_vs_SMV2H_daily_curves_maxabsdiff",
     "a": float(np.abs(sm14.values - dc["355_SM14_ref_oldM(3,1)"].values).max()), "b": 0.0,
     "pass": bool(np.abs(sm14.values - dc["355_SM14_ref_oldM(3,1)"].values).max() < 1e-9)},
    {"check": "parity_tw_vs_twin_daily_allclose", "a": float(np.abs(al["tw"].reindex(twd.index).fillna(0) - twd).max()),
     "b": 0.0, "pass": bool(np.allclose(al["tw"].reindex(twd.index).fillna(0), twd))},
    {"check": "nt_boundary_pair_merged_value_2023-04-05+06", "a": float(merged_val), "b": np.nan, "pass": True},
    {"check": "dual_net_dev", "a": float(dual.sum()), "b": float(rc["DUAL"].sum()),
     "pass": bool(np.isclose(dual.sum(), rc["DUAL"].sum()))},
])

# ================================================================ period keys
def wkey(idx):   # ISO week of session date
    iso = idx.isocalendar()
    return (iso["year"].astype(int) * 100 + iso["week"].astype(int)).values

def mkey(idx):
    return idx.to_period("M")

def qkey(idx):
    return idx.to_period("Q")

def losing_streak(vals):
    b = c = 0
    for v in vals:
        c = c + 1 if v < 0 else 0
        b = max(b, c)
    return b

# ================================================================ A. smoothness battery
def smoothness(label, s):
    net = s.values.astype(float)
    idx = s.index
    wk = pd.Series(net, index=idx).groupby(wkey(idx)).sum()
    mo = pd.Series(net, index=idx).groupby(mkey(idx)).sum()
    qt = pd.Series(net, index=idx).groupby(qkey(idx)).sum()
    eq = np.cumsum(net); peak = np.maximum.accumulate(eq); dd = peak - eq
    uw = dd > 1e-9
    tuw = cur = 0; rec = []; ep = None
    for i, u in enumerate(uw):
        if u:
            cur += 1; tuw = max(tuw, cur)
            if ep is None: ep = i
        else:
            if ep is not None: rec.append(i - ep); ep = None
            cur = 0
    open_ep = ep is not None
    sd = net.std(ddof=1)
    r = {"label": label, "n_days": len(net), "n_zero_days": int((net == 0).sum()),
         "net": net.sum(), "sharpe": net.mean() / sd * np.sqrt(252) if sd > 0 else np.nan,
         "maxDD_eod": dd.max(),
         "pos_day_pct": (net > 0).mean(), "pos_week_pct": (wk > 0).mean(),
         "pos_month_pct": (mo > 0).mean(), "pos_quarter_pct": (qt > 0).mean(),
         "losing_day_streak": losing_streak(net), "losing_week_streak": losing_streak(wk.values),
         "losing_month_streak": losing_streak(mo.values),
         "worst_week": wk.min(), "worst_month": mo.min(), "worst_quarter": qt.min(),
         "roll20_min": pd.Series(net).rolling(20).sum().min(),
         "roll60_min": pd.Series(net).rolling(60).sum().min(),
         "roll120_min": pd.Series(net).rolling(120).sum().min(),
         "longest_TUW_days": tuw, "uw_day_share": uw.mean(),
         "median_recovery_days": float(np.median(rec)) if rec else np.nan,
         "p95_recovery_days": float(np.percentile(rec, 95)) if rec else np.nan,
         "n_recovered_episodes": len(rec), "open_episode_at_dev_end": open_ep,
         "n_weeks": len(wk), "n_months": len(mo), "n_quarters": len(qt)}
    return r

bat = pd.DataFrame([smoothness(k, v) for k, v in CURVES.items()]).set_index("label")
bat.to_csv(f"{OUT}/smoothness_battery.csv")
print("smoothness battery written")
print(bat[["pos_day_pct", "pos_week_pct", "pos_month_pct", "pos_quarter_pct",
           "worst_month", "longest_TUW_days"]].round(3).to_string())

# ================================================================ substrate features (dev sessions)
bars = load_bars_3m()
vs = pd.read_parquet("runs/SM01_SUBSTRATE/out/vote_state_3m.parquet")
tw_led = pd.read_parquet("runs/SMV2M_MASTER_BUILD/out/twin_bar_ledger.parquet")
assert (tw_led["time"].values == bars["time"].values).all()
assert (vs["time"].values == bars["time"].values).all()

sessdt = pd.to_datetime(bars["sess_date"].astype(str))
devbar = (sessdt <= DEV_END).to_numpy()
sess_str = bars["sess_date"].astype(str).to_numpy()

c = bars["close"].to_numpy(); o = bars["open"].to_numpy()
h = bars["high"].to_numpy(); l = bars["low"].to_numpy()
hm = (bars["time"].dt.hour * 100 + bars["time"].dt.minute).to_numpy()
first_of_sess = bars["first_bar_of_session"].to_numpy().astype(bool)

# session-level: range, close
g = pd.DataFrame({"sess": sess_str, "h": h, "l": l})
sess_rng = g.groupby("sess")["h"].max() - g.groupby("sess")["l"].min()
sclose = bars.loc[bars["is_last_of_sess"], ["sess_date", "close"]].set_index("sess_date")["close"]
sclose.index = pd.to_datetime(sclose.index.astype(str))
ret = sclose.pct_change()
rv20 = ret.rolling(20).std()
htf_sess = np.sign(sclose - sclose.rolling(50).mean()).shift(1)      # +1/-1/NaN, exact smv2h.py def

# bar-level features
dcl = np.diff(c, prepend=c[0]); dcl[first_of_sess] = (c - o)[first_of_sess]
absd = pd.Series(np.abs(np.diff(c, prepend=c[0])))
er150 = (pd.Series(c).diff(150).abs() / absd.rolling(150).sum().replace(0, np.nan)).to_numpy()
sgn_vote = np.sign(vs["vote_pos"].to_numpy())
flip_bar = np.zeros(len(bars))
flip_bar[1:] = (sgn_vote[1:] != sgn_vote[:-1]).astype(float)
flip_bar[first_of_sess] = 0.0

B_led = tw_led["B"].to_numpy(); Tpp_led = tw_led["Tpp"].to_numpy()
pos_led = tw_led["pos"].to_numpy(); tgt_led = tw_led["tgt_ops"].to_numpy()
rth_mask = (hm >= 933) & (hm <= 1557)

# --------- component attribution bar math (full series; outputs restricted to dev) ---------
denom = K_SOLAR * Tpp_led + K_BMOM * B_led
share_raw = np.where(np.abs(denom) > 1e-9, K_SOLAR * Tpp_led / np.where(np.abs(denom) > 1e-9, denom, 1.0), np.nan)
share_sig = pd.Series(share_raw).ffill().fillna(0.5)          # state carry-forward on flat-signal bars
# pos[t] == tgt_ops[t-1] at 99.99% of bars (next-open fill): the position at bar t embodies the
# signal state of bar t-1, so the specced ratio is evaluated on that signal bar.
share = share_sig.shift(1).fillna(0.5).to_numpy()
share_sig = share_sig.to_numpy()
mtm = pos_led * dcl * MNQ_PV
mtm_S = share * mtm; mtm_B = mtm - mtm_S
leg_tgt_S = share_sig * tgt_led; leg_tgt_B = tgt_led - leg_tgt_S

dS = np.diff(leg_tgt_S, prepend=0.0); dS[first_of_sess] = leg_tgt_S[first_of_sess]
dB = np.diff(leg_tgt_B, prepend=0.0); dB[first_of_sess] = leg_tgt_B[first_of_sess]

barf = pd.DataFrame({"sess": sess_str, "mtm": mtm, "mtm_S": mtm_S, "mtm_B": mtm_B,
                     "adS": np.abs(dS), "adB": np.abs(dB),
                     "mtm_long": np.where(pos_led > 0, mtm, 0.0),
                     "mtm_short": np.where(pos_led < 0, mtm, 0.0)})
sessagg = barf.groupby("sess").sum()
sessagg.index = pd.to_datetime(sessagg.index)
twin_all = al["tw"].reindex(sessagg.index).fillna(0.0)
fric = sessagg["mtm"] - twin_all                                   # session friction (slip+comm+fill-gap)
wS = sessagg["adS"]; wB = sessagg["adB"]; wT = (wS + wB).replace(0, np.nan)
alloc_S = (fric * (wS / wT)).fillna(fric * 0.5)
alloc_B = fric - alloc_S
legS_d = sessagg["mtm_S"] - alloc_S
legB_d = sessagg["mtm_B"] - alloc_B
recon_err = float(np.abs(legS_d + legB_d - twin_all).max())

legS_dev = legS_d.reindex(CAL_DEV).fillna(0.0)
legB_dev = legB_d.reindex(CAL_DEV).fillna(0.0)
pd.DataFrame({"leg_solar": legS_dev, "leg_bmom": legB_dev, "twin": tw_dev,
              "mtm_long": sessagg["mtm_long"].reindex(CAL_DEV).fillna(0.0),
              "mtm_short": sessagg["mtm_short"].reindex(CAL_DEV).fillna(0.0)}).to_csv(f"{OUT}/leg_daily.csv")

# ---------------- session feature table (dev) ----------------
sig_sess = pd.DataFrame({"sess": sess_str, "sig": vs["sigma460"].to_numpy()}).groupby("sess")["sig"].mean()
er_sess = pd.DataFrame({"sess": sess_str, "er": er150}).groupby("sess")["er"].mean()
flip_sess = pd.DataFrame({"sess": sess_str, "f": flip_bar}).groupby("sess")["f"].sum()
bact_sess = pd.DataFrame({"sess": sess_str[rth_mask], "b": (B_led[rth_mask] != 0).astype(float)}).groupby("sess")["b"].mean()
for s_ in (sig_sess, er_sess, flip_sess, bact_sess, sess_rng):
    s_.index = pd.to_datetime(s_.index)

F = pd.DataFrame(index=CAL_DEV)
F["sigma460"] = sig_sess.reindex(CAL_DEV)
F["rv20_pct"] = rv20.reindex(CAL_DEV).rank(pct=True)
F["range_friction"] = sess_rng.reindex(CAL_DEV) / NQ_FRICTION_PTS
F["er150"] = er_sess.reindex(CAL_DEV)
F["flip_rate"] = flip_sess.reindex(CAL_DEV)
F["htf_up"] = (htf_sess.reindex(CAL_DEV) > 0).astype(float).where(htf_sess.reindex(CAL_DEV).notna())
F["bmom_active"] = bact_sess.reindex(CAL_DEV).fillna(0.0)
F["mtm_long"] = sessagg["mtm_long"].reindex(CAL_DEV).fillna(0.0)
F["mtm_short"] = sessagg["mtm_short"].reindex(CAL_DEV).fillna(0.0)
FEATS = list(F.columns)

# ================================================================ B. joint-loss profile
def period_table(freq):
    key = wkey(CAL_DEV) if freq == "weekly" else mkey(CAL_DEV)
    P = pd.DataFrame({"solar": dual.groupby(key).sum(), "bmom": BM.groupby(key).sum()})
    fmean = F.groupby(key).mean()
    fsum = F[["mtm_long", "mtm_short"]].groupby(key).sum()
    fmean["mtm_long"] = fsum["mtm_long"]; fmean["mtm_short"] = fsum["mtm_short"]
    P = P.join(fmean)
    return P

profile_rows, cell_rows, jl_period_rows = [], [], []
for freq in ("weekly", "monthly"):
    P = period_table(freq)
    s, b = P["solar"], P["bmom"]
    cells = {"S+B+": (s > 0) & (b > 0), "S+B-": (s > 0) & (b < 0),
             "S-B+": (s <= 0) & (b > 0), "S-B-": (s <= 0) & (b < 0),
             "S+B0": (s > 0) & (b == 0), "S-B0": (s <= 0) & (b == 0)}
    for cname, msk in cells.items():
        cell_rows.append({"freq": freq, "cell": cname, "n": int(msk.sum()),
                          "share": float(msk.mean()),
                          "solar_sum": float(s[msk].sum()), "bmom_sum": float(b[msk].sum())})
    jl = (s < 0) & (b < 0)                                  # strict joint loss
    for pk in P.index[jl]:
        jl_period_rows.append({"freq": freq, "period": str(pk),
                               "solar": float(s[pk]), "bmom": float(b[pk])})
    prior = P[FEATS].shift(1)
    for when, X in (("concurrent", P[FEATS]), ("prior", prior)):
        for f_ in FEATS:
            a = X.loc[jl, f_].dropna(); allv = X[f_].dropna(); rest = X.loc[~jl, f_].dropna()
            if len(a) < 2:
                continue
            t_all, p_all = stats.ttest_ind(a, allv, equal_var=False)
            t_rest, p_rest = stats.ttest_ind(a, rest, equal_var=False)
            profile_rows.append({"freq": freq, "when": when, "feature": f_,
                                 "mean_jointloss": a.mean(), "sd_jointloss": a.std(ddof=1), "n_jointloss": len(a),
                                 "mean_all": allv.mean(), "sd_all": allv.std(ddof=1), "n_all": len(allv),
                                 "mean_rest": rest.mean(),
                                 "welch_t_vs_all": t_all, "p_vs_all": p_all,
                                 "welch_t_vs_rest": t_rest, "p_vs_rest": p_rest})

prof = pd.DataFrame(profile_rows)
cellsdf = pd.DataFrame(cell_rows)
out_jl = pd.concat([cellsdf.assign(section="cell_counts"),
                    prof.assign(section="feature_welch")], ignore_index=True, sort=False)
out_jl.to_csv(f"{OUT}/joint_loss_profile.csv", index=False)
pd.DataFrame(jl_period_rows).to_csv(f"{OUT}/joint_loss_periods.csv", index=False)
print("joint-loss profile written;",
      cellsdf[cellsdf.cell == "S-B-"][["freq", "n", "share"]].to_string(index=False))

# ================================================================ C. winner drought
thr = float(np.quantile(dual.values, 0.90))
top_idx = np.where(dual.values >= thr)[0]
waits = np.diff(top_idx)

def dd_series(sr):
    eq = sr.cumsum(); return eq.cummax() - eq

dd_champ = dd_series(nt_merged)       # champion = executable DAYONLY master (NT)
dd_dual = dd_series(dual)
dr = []
for k in range(len(top_idx) - 1):
    i0, i1 = top_idx[k], top_idx[k + 1]
    d0, d1 = dual.index[i0], dual.index[i1]
    win_ch = dd_champ[(dd_champ.index > d0) & (dd_champ.index <= d1)]
    win_du = dd_dual[(dd_dual.index > d0) & (dd_dual.index <= d1)]
    dr.append({"section": "drought", "start_top_day": d0.date(), "end_top_day": d1.date(),
               "wait_sessions": int(i1 - i0),
               "champ_max_uw_depth": float(win_ch.max()) if len(win_ch) else np.nan,
               "champ_uw_days": int((win_ch > 1e-9).sum()),
               "dual_max_uw_depth": float(win_du.max()) if len(win_du) else np.nan,
               "dual_uw_days": int((win_du > 1e-9).sum())})
drdf = pd.DataFrame(dr)
qlab = pd.qcut(drdf["wait_sessions"], 4, labels=["Q1_short", "Q2", "Q3", "Q4_long"])
qsum = drdf.groupby(qlab, observed=True).agg(
    n=("wait_sessions", "size"), wait_min=("wait_sessions", "min"), wait_max=("wait_sessions", "max"),
    champ_uw_depth_mean=("champ_max_uw_depth", "mean"), champ_uw_depth_max=("champ_max_uw_depth", "max"),
    champ_uw_days_mean=("champ_uw_days", "mean"), champ_uw_days_max=("champ_uw_days", "max"),
    dual_uw_depth_mean=("dual_max_uw_depth", "mean"), dual_uw_days_mean=("dual_uw_days", "mean")).reset_index()
qsum.insert(0, "section", "quartile_summary")
wstats = pd.DataFrame([{"section": "wait_distribution", "n_top_days": len(top_idx),
                        "top_decile_threshold": thr, "wait_mean": waits.mean(),
                        "wait_median": float(np.median(waits)), "wait_p75": float(np.percentile(waits, 75)),
                        "wait_p90": float(np.percentile(waits, 90)), "wait_p95": float(np.percentile(waits, 95)),
                        "wait_max": int(waits.max())}])
pd.concat([wstats, qsum, drdf], ignore_index=True, sort=False).to_csv(f"{OUT}/winner_drought.csv", index=False)
print("winner drought written: n_top", len(top_idx), "max wait", int(waits.max()))

# ================================================================ D. component attribution outputs
devm = devbar
both_active = (Tpp_led != 0) & (B_led != 0) & (pos_led != 0) & devm
conflict = both_active & (np.sign(Tpp_led) * np.sign(B_led) < 0)
jl_bar_frac = float(((mtm_S < 0) & (mtm_B < 0))[both_active].mean())
neg_bar_frac = float((mtm < 0)[both_active].mean())

def leg_stats(x):
    sd = x.std(ddof=1)
    return {"net": x.sum(), "daily_vol": sd, "sharpe": x.mean() / sd * np.sqrt(252) if sd > 0 else np.nan,
            "maxDD_eod": float((x.cumsum().cummax() - x.cumsum()).max())}

rows = []
for nm, x in (("LEG_SOLAR", legS_dev), ("LEG_BMOM", legB_dev), ("TWIN_TOTAL", tw_dev)):
    st = leg_stats(x)
    st.update({"leg": nm, "net_share_of_twin": x.sum() / tw_dev.sum()})
    for y in (2022, 2023, 2024, 2025, 2026):
        st[f"net_{y}"] = float(x[x.index.year == y].sum())
    rows.append(st)
att = pd.DataFrame(rows).set_index("leg")
att["jointloss_bar_frac_both_active"] = jl_bar_frac
att["neg_mtm_bar_frac_both_active"] = neg_bar_frac
att["conflict_bar_share_of_both_active"] = float(conflict.sum() / max(both_active.sum(), 1))
att["conflict_bar_mtm_sum"] = float(mtm[conflict].sum())
att["both_active_bar_share_dev"] = float(both_active.sum() / devm.sum())
att["leg_recon_max_abs_err"] = recon_err
att["friction_total_dev"] = float(fric.reindex(CAL_DEV).fillna(0).sum())
att.to_csv(f"{OUT}/component_attribution.csv")
print("attribution: legS", round(legS_dev.sum()), "legB", round(legB_dev.sum()),
      "twin", round(tw_dev.sum()), "recon_err", recon_err)

# top-10 executable DD episodes + leg ownership
ddx = dd_champ
episodes = []
in_ep = False
for i in range(len(ddx)):
    v = ddx.iloc[i]
    if v > 1e-9 and not in_ep:
        in_ep = True; s0 = i; tr = i
    elif in_ep:
        if v > ddx.iloc[tr]: tr = i
        if v <= 1e-9:
            episodes.append((s0, tr, i, ddx.iloc[tr])); in_ep = False
if in_ep:
    episodes.append((s0, tr, len(ddx) - 1, ddx.iloc[tr]))
episodes.sort(key=lambda e: -e[3])
own = []
for s0, tr, e0, depth in episodes[:10]:
    dstart, dtrough, dend = ddx.index[s0], ddx.index[tr], ddx.index[e0]
    m_ = (CAL_DEV >= dstart) & (CAL_DEV <= dtrough)
    ls, lb, tws = legS_dev[m_].sum(), legB_dev[m_].sum(), tw_dev[m_].sum()
    tot = ls + lb
    own.append({"peak_to_start": dstart.date(), "trough": dtrough.date(), "recovered_by": dend.date(),
                "nt_depth": float(depth), "days_to_trough": int(tr - s0 + 1),
                "twin_window_net": float(tws), "leg_solar_net": float(ls), "leg_bmom_net": float(lb),
                "solar_share_of_window_loss": float(ls / tot) if tot < 0 else np.nan,
                "bmom_share_of_window_loss": float(lb / tot) if tot < 0 else np.nan})
pd.DataFrame(own).to_csv(f"{OUT}/dd_ownership.csv", index=False)
print("dd ownership written (top-10 executable episodes)")

# conditioning matrix: side x HTF x time-of-day (dev, position bars only)
htf_bar = htf_sess.reindex(pd.to_datetime(pd.Series(sess_str))).to_numpy()
tod = np.select([hm >= 1800, hm < 933, (hm >= 933) & (hm < 1200),
                 (hm >= 1200) & (hm < 1430), (hm >= 1430) & (hm < 1600)],
                ["ON_1800_2400", "ON_0000_0933", "RTH_0933_1200", "RTH_1200_1430", "RTH_1430_1600"],
                default="POST_1600_1700")
mm = devm & (pos_led != 0)
cm = pd.DataFrame({"side": np.where(pos_led[mm] > 0, "LONG", "SHORT"),
                   "htf": np.where(np.isnan(htf_bar[mm]), "NA",
                                   np.where(htf_bar[mm] > 0, "HTF_UP", "HTF_DOWN")),
                   "tod": tod[mm], "mtm": mtm[mm],
                   "loss": np.minimum(mtm[mm], 0.0),
                   "mtm_S_loss": np.minimum(mtm_S[mm], 0.0),
                   "mtm_B_loss": np.minimum(mtm_B[mm], 0.0)})
agg = cm.groupby(["side", "htf", "tod"]).agg(n_bars=("mtm", "size"), mtm_sum=("mtm", "sum"),
                                             loss_sum=("loss", "sum"),
                                             solar_loss_sum=("mtm_S_loss", "sum"),
                                             bmom_loss_sum=("mtm_B_loss", "sum")).reset_index()
agg["loss_share_of_total"] = agg["loss_sum"] / agg["loss_sum"].sum()
agg.sort_values("loss_sum", inplace=True)
agg.to_csv(f"{OUT}/conditioning_matrix.csv", index=False)
print("conditioning matrix written")

# ================================================================ E. recency_2026
rec_rows = []
def r120(s):
    m = s.rolling(120).mean(); sd = s.rolling(120).std(ddof=1)
    return (m / sd * np.sqrt(252)).dropna()

for nm, s in CURVES.items():
    r = r120(s)
    fin = r.iloc[-1]
    pct = float((r <= fin).mean())
    rec_rows += [
        {"curve": nm, "metric": "r120_sharpe_final_devend", "value": float(fin), "label": "DEV"},
        {"curve": nm, "metric": "r120_sharpe_pctile_final_vs_own_history", "value": pct, "label": "DEV"},
        {"curve": nm, "metric": "r120_sharpe_hist_median", "value": float(r.median()), "label": "DEV"},
        {"curve": nm, "metric": "r120_sharpe_hist_min", "value": float(r.min()), "label": "DEV"},
        {"curve": nm, "metric": "r120_sharpe_hist_share_below_zero", "value": float((r < 0).mean()), "label": "DEV"},
        {"curve": nm, "metric": "r120_n_windows", "value": len(r), "label": "DEV"},
    ]
    for y in (2022, 2023, 2024, 2025, 2026):
        xy = s[s.index.year == y]
        sd = xy.std(ddof=1)
        tag = "net_2026YTD_thru_May" if y == 2026 else f"net_{y}"
        rec_rows.append({"curve": nm, "metric": tag, "value": float(xy.sum()), "label": "DEV"})
        rec_rows.append({"curve": nm, "metric": tag.replace("net", "sharpe"),
                         "value": float(xy.mean() / sd * np.sqrt(252)) if sd > 0 else np.nan, "label": "DEV"})
    # monthly rolling-120 snapshots 2024-01 .. dev end
    msnap = r.groupby(r.index.to_period("M")).last()
    hist_sorted = np.sort(r.values)
    for pk, v in msnap.items():
        if pk >= pd.Period("2024-01", "M"):
            rec_rows.append({"curve": nm, "metric": f"r120_sharpe_eom_{pk}", "value": float(v), "label": "DEV"})
            rec_rows.append({"curve": nm, "metric": f"r120_pctile_eom_{pk}",
                             "value": float(np.searchsorted(hist_sorted, v, side="right") / len(hist_sorted)),
                             "label": "DEV"})

# CONSUMED June-July 2026 — executable master only (committed artifact values, < 2026-08-01)
nt_full = al["nt"].copy()
nt_full.loc[PAIR[0]] += nt_full.loc[PAIR[1]]; nt_full = nt_full.drop(index=PAIR[1]).sort_index()
jun = nt_full[(nt_full.index >= "2026-06-01") & (nt_full.index <= "2026-06-30")]
jul = nt_full[(nt_full.index >= "2026-07-01") & (nt_full.index <= "2026-07-31")]
jul_ex = jul[~jul.index.isin([pd.Timestamp("2026-07-30"), pd.Timestamp("2026-07-31")])]
jj = pd.concat([jun, jul])
r_all = r120(nt_full)
fin_c = r_all.iloc[-1]
hist_dev = r120(nt_merged)
rec_rows += [
    {"curve": "MASTER_EXEC_NT", "metric": "net_2026_06", "value": float(jun.sum()), "label": "CONSUMED"},
    {"curve": "MASTER_EXEC_NT", "metric": "net_2026_07", "value": float(jul.sum()), "label": "CONSUMED"},
    {"curve": "MASTER_EXEC_NT", "metric": "net_2026_07_ex_edge_days_0730_0731", "value": float(jul_ex.sum()),
     "label": "CONSUMED"},
    {"curve": "MASTER_EXEC_NT", "metric": "n_days_2026_06_07", "value": len(jj), "label": "CONSUMED"},
    {"curve": "MASTER_EXEC_NT", "metric": "pos_day_pct_2026_06_07", "value": float((jj > 0).mean()),
     "label": "CONSUMED"},
    {"curve": "MASTER_EXEC_NT", "metric": "r120_sharpe_at_2026_07_31", "value": float(fin_c), "label": "CONSUMED"},
    {"curve": "MASTER_EXEC_NT", "metric": "r120_pctile_at_2026_07_31_vs_dev_history",
     "value": float((hist_dev <= fin_c).mean()), "label": "CONSUMED"},
]
pd.DataFrame(rec_rows).to_csv(f"{OUT}/recency_2026.csv", index=False)
crosschecks.to_csv(f"{OUT}/crosschecks.csv", index=False)
print("recency written; crosschecks written")
print("DONE")
