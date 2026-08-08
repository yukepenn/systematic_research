"""SMV2U step0 — build verified 1m and 5m dev substrates from SM1M_SUBSTRATE, session-tagged
against the 3m substrate's own NT8-authoritative session calendar (runs/AUDIT03_BARS), NOT a
naive intraday-gap heuristic (that heuristic mis-splits at least one genuine intra-session data
gap into a false extra session -- see substrate_verify.json "false_split_dates").

Session assignment method: for each 1m bar with timestamp t, assign it to the 3m session s such
that session(s-1).last_bar_time < t <= session(s).last_bar_time (searchsorted on the sorted array
of 3m session end times). This inherits the NT8-native session boundaries used to build the 3m
file (AuditBarExport1, native session template) directly, so DST changeovers and thin-liquidity
intra-session gaps in the raw 1-minute feed cannot fracture a session.

5m bars: aggregated from the SAME session-tagged 1m dev bars via ceil('5min') within each session
id (18:00 ET open is a 5-minute-boundary time, so this bucketing is 18:00-anchored automatically,
exactly as sm01_solarsim.resample_3m's ceil('3min') is 18:00-anchored for the incumbent).

Dev filter (sess_date <= 2026-05-31) is applied immediately after tagging; June-July 2026 rows in
the source parquet are read only to compute correct session boundaries near the file's tail and
are never used in any economic computation (spec restricts this run to dev only).
"""
import os, sys, json
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
import sm01_solarsim as sm

RUN = os.path.join(ROOT, "runs", "SMV2U_CLOCK_CHALLENGE")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
DEV_END = pd.Timestamp("2026-05-31")

# ---------------------------------------------------------------- load 3m calendar (authoritative)
bars3_full = sm.load_bars_3m(os.path.join(ROOT, "runs", "AUDIT03_BARS", "nq_3m_2022_2026.csv"))
# session end (last-bar) times, in session order (1-indexed sess_id from load_bars_3m)
g3 = bars3_full.groupby("sess_id")
edges = g3["time"].max().to_numpy()               # sorted ascending by construction
sess_date3_by_id = g3["sess_date"].first()
n3_by_id = g3.size()   # Series indexed by sess_id (1-indexed)
assert np.all(np.diff(edges) > np.timedelta64(0, "ns")), "3m session end times not strictly increasing"

bars3_dev = bars3_full[bars3_full["sess_date"] <= DEV_END.date()]
n3_dev_sessions = bars3_dev["sess_id"].nunique()
n3_dev_bars = len(bars3_dev)
print(f"3m calendar: {len(edges)} sessions total (thru {sess_date3_by_id.iloc[-1]}); "
      f"dev (<=2026-05-31): {n3_dev_sessions} sessions, {n3_dev_bars} bars", flush=True)

# ---------------------------------------------------------------- load 1m bars, tag sessions
df1 = pd.read_parquet(os.path.join(ROOT, "runs", "SM1M_SUBSTRATE", "out", "nq_1m_2022_2026.parquet"))
df1 = df1.sort_values("time").reset_index(drop=True)
assert df1["time"].is_monotonic_increasing
t1 = df1["time"].to_numpy()

idx = np.searchsorted(edges, t1, side="left")      # 0-indexed session slot per 1m bar
n_oob = int((idx >= len(edges)).sum())
idx_c = np.clip(idx, 0, len(edges) - 1)
sess_ids = idx_c + 1                                # align to 1-indexed sess_id used by 3m frame
df1["sess_id"] = sess_ids
df1["sess_date"] = sess_date3_by_id.reindex(sess_ids).to_numpy()
df1["oob"] = idx >= len(edges)

# also compute the NAIVE gap>1hr session split (what a from-scratch build would do) purely to
# document the mis-split this method avoids
gap = pd.Series(t1).diff() > pd.Timedelta(hours=1)
naive_fb = (gap | (df1.index == 0)).to_numpy()
naive_sid = np.cumsum(naive_fb)
naive_sess_date = pd.Series(t1).groupby(naive_sid).transform("max")
naive_sess_date = pd.to_datetime(naive_sess_date).dt.date
false_splits = sorted(set(pd.to_datetime(pd.Series(naive_sess_date)).dt.date) -
                       set(pd.to_datetime(sess_date3_by_id).dt.date))

# first/last bar flags from the assigned (authoritative) session id
first_flag = np.r_[True, sess_ids[1:] != sess_ids[:-1]]
last_flag = np.r_[sess_ids[:-1] != sess_ids[1:], True]
df1["first_bar_of_session"] = first_flag
df1["is_last_of_sess"] = last_flag

n1_by_id = df1.groupby("sess_id").size()
ratio = (n1_by_id / n3_by_id.reindex(n1_by_id.index, fill_value=np.nan))
# flag sessions whose 1m/3m bar-count ratio deviates far from the ~3x expectation (missing data,
# beyond the ordinary shrinkage that early-close/holiday sessions already show equally in both files)
flagged = ratio[(ratio < 2.5) | (ratio > 3.05)]

df1_dev = df1[df1["sess_date"] <= DEV_END.date()].reset_index(drop=True)
n1_dev_sessions = df1_dev["sess_id"].nunique()
n1_dev_bars = len(df1_dev)
sess_date_match = set(pd.to_datetime(df1_dev["sess_date"]).unique()) == \
                  set(pd.to_datetime(bars3_dev["sess_date"]).unique())

print(f"1m dev: {n1_dev_sessions} sessions, {n1_dev_bars} bars; "
      f"session-date-set match vs 3m dev: {sess_date_match}", flush=True)
print(f"naive gap>1hr heuristic would have produced a false extra session split at: "
      f"{false_splits}", flush=True)
print(f"sessions with 1m/3m bar-count ratio outside [2.5,3.05]: {len(flagged)}", flush=True)

df1_dev.to_parquet(os.path.join(OUT, "bars_1m_dev.parquet"))

# ---------------------------------------------------------------- build 5m bars (session-aware ceil)
d5 = df1_dev.copy()
d5["b5"] = d5["time"].dt.ceil("5min")
g5 = d5.groupby(["sess_id", "b5"], sort=True)
bars5 = pd.DataFrame({
    "open": g5["open"].first(), "high": g5["high"].max(), "low": g5["low"].min(),
    "close": g5["close"].last(), "volume": g5["volume"].sum(),
    "sess_date": g5["sess_date"].first(),
}).reset_index().rename(columns={"b5": "time"})
bars5 = bars5.sort_values(["sess_id", "time"]).reset_index(drop=True)
first5 = np.r_[True, bars5["sess_id"].to_numpy()[1:] != bars5["sess_id"].to_numpy()[:-1]]
last5 = np.r_[bars5["sess_id"].to_numpy()[:-1] != bars5["sess_id"].to_numpy()[1:], True]
bars5["first_bar_of_session"] = first5
bars5["is_last_of_sess"] = last5
assert bars5["time"].is_monotonic_increasing, "5m bar timestamps not monotone after groupby-sort"

n5_dev_sessions = bars5["sess_id"].nunique()
n5_dev_bars = len(bars5)
sess_date_match5 = set(pd.to_datetime(bars5["sess_date"]).unique()) == \
                   set(pd.to_datetime(bars3_dev["sess_date"]).unique())
print(f"5m dev: {n5_dev_sessions} sessions, {n5_dev_bars} bars; "
      f"session-date-set match vs 3m dev: {sess_date_match5}", flush=True)

bars5.to_parquet(os.path.join(OUT, "bars_5m_dev.parquet"))

# ---------------------------------------------------------------- verification artifact
verify = {
    "n3_sessions_total_file": int(len(edges)),
    "n3_dev_sessions": int(n3_dev_sessions),
    "n3_dev_bars": int(n3_dev_bars),
    "n1_dev_sessions": int(n1_dev_sessions),
    "n1_dev_bars": int(n1_dev_bars),
    "n5_dev_sessions": int(n5_dev_sessions),
    "n5_dev_bars": int(n5_dev_bars),
    "session_date_set_match_1m_vs_3m_dev": bool(sess_date_match),
    "session_date_set_match_5m_vs_3m_dev": bool(sess_date_match5),
    "n_sessions_match_1m": bool(n1_dev_sessions == n3_dev_sessions),
    "n_sessions_match_5m": bool(n5_dev_sessions == n3_dev_sessions),
    "n_1m_bars_out_of_3m_calendar_bounds": int(n_oob),
    "naive_gap_gt_1hr_heuristic_false_extra_session_dates": [str(d) for d in false_splits],
    "n_sessions_flagged_bar_count_ratio_outside_2.5_3.05": int(len(flagged)),
    "flagged_sessions_ratio": {str(sess_date3_by_id.loc[i]): float(r) for i, r in flagged.items()},
    "dev_end": str(DEV_END.date()),
}
with open(os.path.join(OUT, "substrate_verify.json"), "w") as f:
    json.dump(verify, f, indent=2)
print(json.dumps(verify, indent=2))

flagged_rows = []
for sid, r in flagged.items():
    flagged_rows.append({
        "sess_id": int(sid), "sess_date": str(sess_date3_by_id.loc[sid]),
        "n_1m_bars": int(n1_by_id.loc[sid]) if sid in n1_by_id.index else 0,
        "n_3m_bars": int(n3_by_id.loc[sid]), "ratio_1m_per_3m": float(r),
    })
fr_df = pd.DataFrame(flagged_rows, columns=["sess_id", "sess_date", "n_1m_bars", "n_3m_bars", "ratio_1m_per_3m"])
if len(fr_df):
    fr_df = fr_df.sort_values("sess_date")
fr_df.to_csv(os.path.join(OUT, "substrate_flagged_sessions.csv"), index=False)
print("done")
