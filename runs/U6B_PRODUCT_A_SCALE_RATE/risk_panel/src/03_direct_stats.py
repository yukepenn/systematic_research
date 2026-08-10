"""U6B risk_panel Part 3 (sec7) -- DIRECT (single historical-path, non-bootstrapped) intraday /
EOD drawdown statistics on the genuine-MNQ canonical series (<=2026-05-29). No resampling here --
every number is a FACT about the one realized path (labelled as such throughout REPORT.md).

Honesty on resolution (stated once, applies to every 'intraday' figure below): this campaign's
execution granularity is 3-minute bars, not tick-level. 'Intraday' means bar-level (3-min)
within-session excursion, not true tick-by-tick equity. The continuous equity path used for
bar-level maxDD/CDaR is cumsum(bar_pnl) over ALL canonical bars in time order (positions are
forced flat at every session close per the campaign's own convention, so no additional overnight
excursion risk is hidden by this construction -- see spec.yaml / CLAUDE.md session-close rule).
"""
import os, sys, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "runs", "U6B_PRODUCT_A_SCALE_RATE")
OUT = os.path.join(RUN, "risk_panel", "out")
os.makedirs(OUT, exist_ok=True)

CAPITAL_GRID = [50_000.0, 75_000.0, 100_000.0, 150_000.0, 200_000.0, 300_000.0, 500_000.0]
CANDIDATES = ["CONTROL", "F0.5", "F0.7"]
CDAR_ALPHA = 0.95

CERTIFIED_WORST_DAY = -7405.599999999977   # u6b_mnq_grid_battery.csv, all 3 candidates, canonical


def drawdown_episodes(dates, eq):
    """Peak -> trough -> recovery episodes on an EOD equity series (dollars). Returns a list of
    dicts. The final episode is marked censored=True if the series ends still underwater
    (no new high reached by the last observation)."""
    peak = np.maximum.accumulate(eq)
    is_new_high = eq >= peak
    n = len(eq)
    episodes = []
    i = 0
    while i < n:
        if is_new_high[i]:
            i += 1
            continue
        # start of an underwater run: peak level is peak[i-1] (== peak[i], carried forward)
        run_start = i
        while i < n and not is_new_high[i]:
            i += 1
        run_end = i - 1   # inclusive, last underwater session in this run
        censored = (i == n)   # ran off the end of the sample without a new high
        seg = eq[run_start:run_end + 1]
        peak_level = peak[run_start] if run_start == 0 else peak[run_start - 1]
        trough_off = int(np.argmin(seg))
        trough_idx = run_start + trough_off
        episodes.append({
            "peak_date": str(dates[run_start - 1]) if run_start > 0 else str(dates[0]),
            "peak_level": float(peak_level),
            "trough_date": str(dates[trough_idx]),
            "trough_level": float(eq[trough_idx]),
            "depth_dollars": float(peak_level - eq[trough_idx]),
            "recovery_date": (str(dates[i]) if not censored else None),
            "drawdown_duration_sessions": int(trough_idx - (run_start - 1)) if run_start > 0 else int(trough_idx + 1),
            "recovery_duration_sessions": (int(i - trough_idx) if not censored else None),
            "total_underwater_sessions": int(run_end - run_start + 1),
            "censored_still_underwater_at_series_end": bool(censored),
        })
    return episodes


def summarize(vals):
    vals = np.asarray([v for v in vals if v is not None], dtype=float)
    if len(vals) == 0:
        return {"n": 0}
    return {"n": int(len(vals)), "mean": float(vals.mean()), "median": float(np.median(vals)),
            "p90": float(np.quantile(vals, 0.90)), "max": float(vals.max()), "min": float(vals.min())}


all_rows = []
episode_summaries = {}
for name in CANDIDATES:
    daily = pd.read_csv(os.path.join(RUN, "out", f"{name}_daily_GENUINE_MNQ.csv"))
    daily["sess"] = pd.to_datetime(daily["sess"])
    daily = daily[daily["sess"] <= pd.Timestamp("2026-05-29")].sort_values("sess").reset_index(drop=True)
    net = daily["net"].to_numpy(float)
    dates = daily["sess"].dt.strftime("%Y-%m-%d").to_numpy()
    n_days = len(net)

    # ---- EOD ----
    eq_eod = np.cumsum(net)
    peak_eod = np.maximum.accumulate(np.maximum(eq_eod, 0.0))
    dd_eod = peak_eod - eq_eod
    maxdd_eod = float(dd_eod.max())
    k = max(1, int((1 - CDAR_ALPHA) * n_days))
    cdar_eod = float(-np.partition(-dd_eod, k - 1)[:k].mean())
    worst_day = float(net.min())

    # ---- bar-level (canonical only, continuous single path) ----
    bl = pd.read_parquet(os.path.join(RUN, "risk_panel", "out", f"{name}_barlevel_GENUINE_MNQ_canonical.parquet"))
    bl = bl.sort_values("time").reset_index(drop=True)
    bar_pnl = bl["bar_pnl"].to_numpy(float)
    eq_bar = np.cumsum(bar_pnl)
    peak_bar = np.maximum.accumulate(np.maximum(eq_bar, 0.0))
    dd_bar = peak_bar - eq_bar
    maxdd_bar = float(dd_bar.max())
    maxdd_bar_time = str(bl["time"].to_numpy()[int(np.argmax(dd_bar))])
    n_bars = len(bar_pnl)
    kb = max(1, int((1 - CDAR_ALPHA) * n_bars))
    cdar_bar_naive = float(-np.partition(-dd_bar, kb - 1)[:kb].mean())
    # frequency-matched: one observation per session = that session's own worst bar-level dd
    bl2 = bl.copy(); bl2["dd_bar"] = dd_bar
    sess_worst_dd = bl2.groupby("sess_date")["dd_bar"].max().to_numpy()
    kd = max(1, int((1 - CDAR_ALPHA) * len(sess_worst_dd)))
    cdar_bar_matched = float(-np.partition(-sess_worst_dd, kd - 1)[:kd].mean())
    worst_intraday_excursion = maxdd_bar   # largest bar-level peak-to-trough $ drawdown, realized path

    # sanity: bar-level series' session-end values must reconcile to the EOD series (to the cent)
    last_rows = bl2[bl2["is_last_of_sess"]].sort_values("sess_date")
    eq_bar_sessend = last_rows["dd_bar"].to_numpy()  # not used directly; reconciliation done in 01_ script already

    # ---- drawdown-episode (time-under-water / recovery) distribution, on EOD equity ----
    episodes = drawdown_episodes(dates, eq_eod)
    tuw = [e["total_underwater_sessions"] for e in episodes]
    rec = [e["recovery_duration_sessions"] for e in episodes if not e["censored_still_underwater_at_series_end"]]
    n_censored = sum(1 for e in episodes if e["censored_still_underwater_at_series_end"])
    episode_summaries[name] = {
        "n_episodes": len(episodes), "n_censored_at_series_end": n_censored,
        "time_under_water_sessions": summarize(tuw),
        "recovery_time_sessions_uncensored_only": summarize(rec),
        "episodes_detail": episodes,
    }

    row = {
        "candidate": name, "n_sessions": n_days, "n_bars": n_bars,
        "maxDD_eod_dollars": maxdd_eod, "maxDD_eod_certified_battery": None,
        "CDaR95_eod_dollars": cdar_eod,
        "worst_session_dollars": worst_day,
        "worst_session_matches_certified_7405.60": bool(abs(worst_day - CERTIFIED_WORST_DAY) < 1e-6),
        "maxDD_barlevel_dollars": maxdd_bar, "maxDD_barlevel_time": maxdd_bar_time,
        "maxDD_barlevel_vs_eod_ratio": maxdd_bar / maxdd_eod if maxdd_eod else None,
        "CDaR95_barlevel_naive_dollars": cdar_bar_naive,
        "CDaR95_barlevel_freqmatched_dollars": cdar_bar_matched,
        "CDaR95_barlevel_matched_vs_eod_ratio": cdar_bar_matched / cdar_eod if cdar_eod else None,
        "worst_intraday_excursion_dollars": worst_intraday_excursion,
        "n_drawdown_episodes": len(episodes), "n_episodes_censored_at_series_end": n_censored,
        "time_under_water_mean_sessions": episode_summaries[name]["time_under_water_sessions"].get("mean"),
        "time_under_water_median_sessions": episode_summaries[name]["time_under_water_sessions"].get("median"),
        "time_under_water_p90_sessions": episode_summaries[name]["time_under_water_sessions"].get("p90"),
        "time_under_water_max_sessions": episode_summaries[name]["time_under_water_sessions"].get("max"),
        "recovery_time_mean_sessions": episode_summaries[name]["recovery_time_sessions_uncensored_only"].get("mean"),
        "recovery_time_median_sessions": episode_summaries[name]["recovery_time_sessions_uncensored_only"].get("median"),
        "recovery_time_p90_sessions": episode_summaries[name]["recovery_time_sessions_uncensored_only"].get("p90"),
        "recovery_time_max_sessions": episode_summaries[name]["recovery_time_sessions_uncensored_only"].get("max"),
    }
    all_rows.append(row)

    # ---- empirical margin-to-ruin distance at the preregistered capital grid (FACT, no bootstrap) ----
    for c in CAPITAL_GRID:
        all_rows[-1].setdefault("_margin_to_ruin", {})
    margin_rows = []
    for c in CAPITAL_GRID:
        margin_rows.append({
            "candidate": name, "capital": c,
            "eod_maxdd_consumed_fraction": maxdd_eod / c,
            "eod_maxdd_headroom_dollars": c - maxdd_eod,
            "barlevel_maxdd_consumed_fraction": maxdd_bar / c,
            "barlevel_maxdd_headroom_dollars": c - maxdd_bar,
        })
    pd.DataFrame(margin_rows).to_csv(
        os.path.join(OUT, f"part3_margin_to_ruin_{name}.csv"), index=False)

summary_df = pd.DataFrame(all_rows).drop(columns=["_margin_to_ruin"], errors="ignore")
summary_df.to_csv(os.path.join(OUT, "part3_direct_stats_summary.csv"), index=False)
with open(os.path.join(OUT, "part3_drawdown_episodes.json"), "w") as f:
    json.dump(episode_summaries, f, indent=2, default=str)

print(summary_df.drop(columns=[c for c in summary_df.columns if c.startswith("time_under_water") or
                                c.startswith("recovery_time")]).to_string(index=False))
print()
for name in CANDIDATES:
    es = episode_summaries[name]
    print(f"{name}: n_episodes={es['n_episodes']}  n_censored={es['n_censored_at_series_end']}  "
          f"TUW(sessions) mean/median/p90/max = "
          f"{es['time_under_water_sessions'].get('mean'):.1f}/"
          f"{es['time_under_water_sessions'].get('median'):.1f}/"
          f"{es['time_under_water_sessions'].get('p90'):.1f}/"
          f"{es['time_under_water_sessions'].get('max'):.0f}   "
          f"RECOVERY(sessions, uncensored) mean/median/p90/max = "
          f"{es['recovery_time_sessions_uncensored_only'].get('mean'):.1f}/"
          f"{es['recovery_time_sessions_uncensored_only'].get('median'):.1f}/"
          f"{es['recovery_time_sessions_uncensored_only'].get('p90'):.1f}/"
          f"{es['recovery_time_sessions_uncensored_only'].get('max'):.0f}")

print("\n[risk_panel] Part 3 direct stats complete.")
