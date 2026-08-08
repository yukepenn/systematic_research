"""SMV2U step1 -- seq 390 (1m clock arms) + seq 391 (5m clock arms).

13-member V3 ensemble VERBATIM (sm01_solarsim.member_states/member_trades/e10_target, reused
unmodified from runs/SMV2R_SOLAR_CORE_1's verified simulator) run on the 1m and 5m dev substrates
built in step0. Two frozen memory conventions per clock:
  bar-matched:  VolPeriod=460 bars (mechanism-neighbor: same bar-count memory as the incumbent)
  time-matched: VolPeriod=1380 bars (1m) / 276 bars (5m)  (~23h of clock time == incumbent's
                460*3min=1380min memory, matched in WALL-CLOCK duration instead of bar count)
E10 executor per clock: tgt = clip(rha(10*mean pending),+-10), fills next bar open +-1 tick on the
SAME clock, MNQ costs, session flatten (sm01_solarsim.e10_target + SMV2R common_exec.e10_exec,
verbatim). 4 challenger arms total + the 3m incumbent reference (reused from the already-verified,
already-committed runs/SMV2R_SOLAR_CORE_1/out/cache_incumbent.npz -- NOT recomputed).

Reads per arm: dd_battery + smoothness columns + turnover + friction share + top-10-day sum +
right-tail overlap with incumbent + portfolio contribution (vm-blend with frozen BMOM E2 daily at
60/40, equal-vol basis, SAME rerank construction as runs/SMV2H_ONECONTRACT/rerank.py) + LOYO table.

verdict_rule (frozen, no adoption language): an arm earns an R2 spec only if it beats the 3m
incumbent on Sharpe AND CDaR5 at BOTH the standalone level AND the portfolio level simultaneously.
"""
import os, sys, json
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "runs", "SMV2U_CLOCK_CHALLENGE")
OUT = os.path.join(RUN, "out")
sys.path.insert(0, os.path.join(ROOT, "runs", "SMV2R_SOLAR_CORE_1"))
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
from common_exec import sm, e10_exec, metric_row  # noqa: E402  (verbatim SMV2R executor)
from smv2_common import dd_battery  # noqa: E402

TICK = sm.TICK
MNQ_PV = sm.MNQ_POINT_VALUE
MNQ_COMM = sm.MNQ_COMM_SIDE
FRICTION_PER_CONTRACT_SIDE = TICK * MNQ_PV + MNQ_COMM   # 1-tick adverse slip $ + commission, per side

DEV_END = pd.Timestamp("2026-05-31")

# ------------------------------------------------------------------ smoothness (verbatim SMV2Q form)
def wkey(idx):
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
    return {"label": label, "n_days": len(net), "n_zero_days": int((net == 0).sum()),
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

# ------------------------------------------------------------------ rerank vm construction (verbatim
# SMV2H_ONECONTRACT/rerank.py method; leg = each arm's own plain-E10 daily curve, BM = frozen)
def vm_series(x, sig):
    return x * (sig / x.std(ddof=1))

def portfolio_blend(leg_daily, bm_daily, cal, ws=0.6, wb=0.4):
    leg = leg_daily.reindex(cal).fillna(0.0)
    bm = bm_daily.reindex(cal).fillna(0.0)
    sig = leg.std(ddof=1)
    p = vm_series(ws * leg + wb * vm_series(bm, sig), sig)
    return p

# ------------------------------------------------------------------ 0. load substrates + incumbent
print("loading substrates ...", flush=True)
bars1 = pd.read_parquet(os.path.join(OUT, "bars_1m_dev.parquet"))
bars5 = pd.read_parquet(os.path.join(OUT, "bars_5m_dev.parquet"))
for b in (bars1, bars5):
    assert (b["sess_date"] <= DEV_END.date()).all()

inc_cache = np.load(os.path.join(ROOT, "runs", "SMV2R_SOLAR_CORE_1", "out", "cache_incumbent.npz"))
inc_daily = pd.read_csv(os.path.join(ROOT, "runs", "SMV2R_SOLAR_CORE_1", "out",
                                     "e10_daily_dev_incumbent.csv"), parse_dates=["sess"])
CAL = inc_daily["sess"]                       # canonical 1139-session dev calendar
inc_series = inc_daily.set_index("sess")["net"]

bm_ledger = pd.read_parquet(os.path.join(ROOT, "runs", "SMV2B_BMOM_EXEC_AUDIT", "out",
                                         "ledger_E2_next_open.parquet"))
BM_raw = (bm_ledger.groupby("sess")["net_c1_ticks"].sum() * 5.0)
BM_raw.index = pd.to_datetime(BM_raw.index)

inc_metric = metric_row("3m_incumbent", inc_daily)
inc_smooth = smoothness("3m_incumbent", inc_series)
inc_port = portfolio_blend(inc_series, BM_raw, CAL)
inc_port_b = dd_battery(CAL, inc_port.values, label="3m_incumbent_portfolio")

# right-tail reference set: incumbent's own top decile days
n_cal = len(CAL)
k_dec = int(np.ceil(0.10 * n_cal))
inc_top_idx = inc_series.sort_values(ascending=False).index[:k_dec]
inc_top_sum = float(inc_series.loc[inc_top_idx].sum())

# incumbent per-year sessions/net (for LOYO)
years = CAL.dt.year.to_numpy()
YR_LIST = [2022, 2023, 2024, 2025, 2026]

def sharpe_of(x):
    x = np.asarray(x, dtype=float)
    sd = x.std(ddof=1)
    return float(x.mean() / sd * np.sqrt(252)) if sd > 0 else np.nan

# ------------------------------------------------------------------ 1. build each clock arm
CONFIGS = [
    ("1m", bars1, "bar_matched", 460),
    ("1m", bars1, "time_matched", 1380),
    ("5m", bars5, "bar_matched", 460),
    ("5m", bars5, "time_matched", 276),
]

VMS = sm.VMS
arm_rows = []; smooth_rows = []; loyo_rows = []; overlap_rows = []; portfolio_rows = []
daily_curves = {"3m_incumbent": inc_series}
pos_cache = {}   # (clock, conv) -> (n_bars,13) member pos matrix, for step2 MTF reads

for clock, bars_df, conv, N in CONFIGS:
    label = f"{clock}_{conv}"
    print(f"=== {label} (VolPeriod={N} {clock} bars) ===", flush=True)
    close = bars_df["close"].to_numpy()
    sig = sm.sigma_series(close, vol_period=N)
    PEND = []; POS = []
    for vm in VMS:
        is_up, flip, s_eff, anchor = sm.member_states(close, sig, float(vm))
        fills, pos, pend = sm.member_trades(bars_df, is_up, flip, s_eff, anchor)
        PEND.append(pend); POS.append(pos)
    pend = np.column_stack(PEND); pos_mat = np.column_stack(POS)
    pos_cache[(clock, conv)] = pos_mat
    tgt = sm.e10_target(pend)
    daily, bar_pos, bar_pnl = e10_exec(bars_df, tgt)
    daily["sess"] = pd.to_datetime(daily["sess"])   # align dtype with CAL/incumbent (Timestamp, not date)
    daily_curves[label] = daily.set_index("sess")["net"]

    assert len(daily) == n_cal, f"{label}: session count {len(daily)} != incumbent {n_cal}"
    assert list(pd.to_datetime(daily["sess"])) == list(CAL), f"{label}: calendar mismatch vs incumbent"

    m = metric_row(label, daily)
    sm_row = smoothness(label, daily.set_index("sess")["net"])

    # ---- turnover + friction share
    n_tgt_changes = int((np.diff(tgt) != 0).sum())
    total_contracts = float(daily["contracts"].sum())
    total_friction = total_contracts * FRICTION_PER_CONTRACT_SIDE
    gross = m["net"] + total_friction
    friction_share = total_friction / gross if gross != 0 else np.nan
    m.update({
        "clock": clock, "convention": conv, "vol_period_bars": N,
        "n_bars": len(bars_df), "n_tgt_changes": n_tgt_changes,
        "tgt_changes_per_day": n_tgt_changes / n_cal,
        "total_contracts_traded": total_contracts,
        "friction_per_contract_side_$": FRICTION_PER_CONTRACT_SIDE,
        "total_friction_$": total_friction, "gross_$": gross,
        "friction_share": friction_share,
    })

    # ---- right-tail overlap vs incumbent (RTC on incumbent's top-decile days + own top-decile set)
    arm_series = daily.set_index("sess")["net"]
    rtc = float(arm_series.reindex(inc_top_idx).fillna(0.0).sum() / inc_top_sum) if inc_top_sum else np.nan
    arm_top_idx = arm_series.sort_values(ascending=False).index[:k_dec]
    jaccard_n = len(set(arm_top_idx) & set(inc_top_idx))
    m.update({"RTC_incumbent_top_decile": rtc, "top_decile_day_overlap_n": jaccard_n,
             "top_decile_day_overlap_frac": jaccard_n / k_dec, "top_decile_k": k_dec})

    # ---- portfolio contribution (rerank vm construction, 60/40 vs frozen BMOM E2)
    port = portfolio_blend(arm_series, BM_raw, CAL)
    pb = dd_battery(CAL, port.values, label=f"{label}_portfolio")
    pb["clock"] = clock; pb["convention"] = conv
    portfolio_rows.append(pb)

    # ---- verdict: beats incumbent on Sharpe AND CDaR5, standalone AND portfolio
    standalone_beats = bool((m["sharpe"] > inc_metric["sharpe"]) and (m["CDaR5"] < inc_metric["CDaR5"]))
    portfolio_beats = bool((pb["sharpe"] > inc_port_b["sharpe"]) and (pb["CDaR5"] < inc_port_b["CDaR5"]))
    m["standalone_beats_incumbent"] = standalone_beats
    m["portfolio_beats_incumbent"] = portfolio_beats
    m["earns_R2_spec"] = bool(standalone_beats and portfolio_beats)

    arm_rows.append(m)
    smooth_rows.append(sm_row)

    # ---- LOYO table (per-year Sharpe, arm vs incumbent, full + leave-one-year-out)
    dsh_full = m["sharpe"] - inc_metric["sharpe"]
    sign_full = 0 if dsh_full == 0 else (1 if dsh_full > 0 else -1)
    agree = 0
    for y in YR_LIST:
        msk = years != y
        sh_arm_y = sharpe_of(arm_series.to_numpy()[msk])
        sh_inc_y = sharpe_of(inc_series.to_numpy()[msk])
        dsh = sh_arm_y - sh_inc_y
        sgn = 0 if dsh == 0 else (1 if dsh > 0 else -1)
        agree += int(sgn == sign_full)
        loyo_rows.append({"arm": label, "scope": f"loyo_{y}", "sharpe_arm": sh_arm_y,
                          "sharpe_incumbent": sh_inc_y, "dsharpe": dsh, "sign": sgn,
                          "sign_matches_full": bool(sgn == sign_full), "n_days": int(msk.sum())})
    for y in YR_LIST:
        msk = years == y
        sh_arm_y = sharpe_of(arm_series.to_numpy()[msk])
        sh_inc_y = sharpe_of(inc_series.to_numpy()[msk])
        loyo_rows.append({"arm": label, "scope": f"year_{y}", "sharpe_arm": sh_arm_y,
                          "sharpe_incumbent": sh_inc_y, "dsharpe": sh_arm_y - sh_inc_y,
                          "sign": np.nan, "sign_matches_full": np.nan, "n_days": int(msk.sum())})
    loyo_rows.append({"arm": label, "scope": "full", "sharpe_arm": m["sharpe"],
                      "sharpe_incumbent": inc_metric["sharpe"], "dsharpe": dsh_full,
                      "sign": sign_full, "sign_matches_full": True, "n_days": n_cal})

    print(f"  net={m['net']:.0f} sharpe={m['sharpe']:.3f} CDaR5={m['CDaR5']:.0f} "
          f"friction_share={friction_share:.3f} RTC={rtc:.3f} "
          f"standalone_beats={standalone_beats} portfolio_beats={portfolio_beats} "
          f"earns_R2={m['earns_R2_spec']}", flush=True)

# ------------------------------------------------------------------ 2. incumbent row + writeout
inc_metric.update({
    "clock": "3m", "convention": "bar_matched_incumbent", "vol_period_bars": 460,
    "n_bars": int(len(inc_cache["sigma460"])), "n_tgt_changes": int((np.diff(inc_cache["tgt"]) != 0).sum()),
    "tgt_changes_per_day": float((np.diff(inc_cache["tgt"]) != 0).sum()) / n_cal,
    "total_contracts_traded": float(inc_daily["contracts"].sum()),
    "friction_per_contract_side_$": FRICTION_PER_CONTRACT_SIDE,
    "total_friction_$": float(inc_daily["contracts"].sum()) * FRICTION_PER_CONTRACT_SIDE,
    "gross_$": inc_metric["net"] + float(inc_daily["contracts"].sum()) * FRICTION_PER_CONTRACT_SIDE,
    "friction_share": (float(inc_daily["contracts"].sum()) * FRICTION_PER_CONTRACT_SIDE) /
                      (inc_metric["net"] + float(inc_daily["contracts"].sum()) * FRICTION_PER_CONTRACT_SIDE),
    "RTC_incumbent_top_decile": 1.0, "top_decile_day_overlap_n": k_dec,
    "top_decile_day_overlap_frac": 1.0, "top_decile_k": k_dec,
    "standalone_beats_incumbent": None, "portfolio_beats_incumbent": None, "earns_R2_spec": None,
})
inc_port_b["clock"] = "3m"; inc_port_b["convention"] = "bar_matched_incumbent"
portfolio_rows.insert(0, inc_port_b)
arm_rows.insert(0, inc_metric)
smooth_rows.insert(0, inc_smooth)

clock_arms = pd.DataFrame(arm_rows)
clock_arms.to_csv(os.path.join(OUT, "clock_arms.csv"), index=False)
pd.DataFrame(portfolio_rows).to_csv(os.path.join(OUT, "portfolio_contrib.csv"), index=False)
pd.DataFrame(smooth_rows).to_csv(os.path.join(OUT, "smoothness_battery.csv"), index=False)
pd.DataFrame(loyo_rows).to_csv(os.path.join(OUT, "loyo_tables.csv"), index=False)

daily_curves_df = pd.DataFrame({k: v.reindex(CAL.values) for k, v in daily_curves.items()})
daily_curves_df.insert(0, "sess", CAL.values)
daily_curves_df.to_csv(os.path.join(OUT, "daily_curves.csv"), index=False)

# cache member pos matrices for step2 (avoid recompute); 1m bar-matched + time-matched only needed
np.savez_compressed(os.path.join(OUT, "cache_1m_pos.npz"),
                    bar_matched=pos_cache[("1m", "bar_matched")],
                    time_matched=pos_cache[("1m", "time_matched")])

print("\n=== SUMMARY ===")
print(clock_arms[["arm", "clock", "convention", "net", "sharpe", "CDaR5", "friction_share",
                  "RTC_incumbent_top_decile", "standalone_beats_incumbent",
                  "portfolio_beats_incumbent", "earns_R2_spec"]].to_string(index=False))
print("done")
