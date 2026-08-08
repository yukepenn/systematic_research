"""SMV2AB_ENGINE3_S4 -- R1 FAMILY TEST, seq 410-412 (Engine #3 slate 4, first cross-market
candidates). See spec.yaml (frozen, committed 0da78b6) for full text.

e410  cap-tier dispersion catch-up   ES+NQ 15-min consensus move, RTY laggard confirms.
e411  duration-spread shock reaction NQ 30-min shock w/o proportional YM move -> continuation.
e412  quarterly roll basis convergence  ES-vs-(RTY+YM)/2 spread drift into roll week -> NQ.

All economics NET of $4.36/RT + 1 tick/side slippage (NQ, $20/pt, tick 0.25). Dev window:
sessions <= 2026-05-31. No data >= 2026-08-01 is ever used (VIRGIN). NQ/MNQ are the ONLY
traded instruments; ES/RTY/YM are signal-only.

Frozen bar/fill conventions (same substrate and idiom as SMV2K/P/X, disclosed here again):
  - NQ bars: END-stamped 3m via sm01_solarsim.load_bars_3m (same substrate as every SMV2 run).
  - ES/RTY/YM: 1-minute OHLCV substrates (SM1M_{ES,RTY,YM}_SUBSTRATE), aggregated to 3m bars
    session-tagged against NQ's OWN 3m session calendar (searchsorted on NQ session-end times,
    exactly the SMV2U step0_substrate.py method -- NOT a naive intraday-gap heuristic), then
    bucketed by ceil('3min') within each assigned session (18:00-anchored, same as
    sm01_solarsim.resample_3m's own ceil('3min') bucketing). Verified against the NQ 3m dev
    session-date set BEFORE use (out/session_calendar_check.csv).
  - "session close" = the true last 3m bar of the (18:00->17:00 ET) session, matching the
    campaign's universal exit-on-session-close convention -- NOT the RTH (16:00) close, since
    e410 explicitly trades all session hours.
  - Entry/exit fills: sm01_solarsim._fill (1-tick adverse slip capped by the fill bar's range).
    Time-capped mid-session exits fill at the CLOSE of the deadline bar (matches SMV2K's
    sim_e368 "time"/"rth_end" convention); true session-close exits fill at the session's last
    bar's close, same function, at_close= kwarg.
  - NW t-stat: mean per-event net, SE clustered by session, Bartlett/Newey-West lag 5 (house
    convention, matches SMV2K/P/X). House bootstrap (moving block=5, B=10000, seed=20260808)
    reported alongside as P(mean>0), supplementary to the frozen t_NW>=2 gate.

Engine-specific mechanical choices not fully pinned by the frozen spec text, disclosed here
(each a reasonable, literal-consistent INFERENCE, not an improvised gate/grid/data choice --
see the structured-output "caveats" for the labeled rationale of each):
  - e410/e411 "z" (trailing 20-session vol of an intraday N-min return series): NOT a
    time-of-day-specific z. Per session s, pool ALL within-session N-min rolling-return (or
    N-min rolling-volume) observations from the trailing 20 COMPLETE sessions [s-20..s-1]
    (session-causal, >=20-session burn-in before any event can fire), take that pool's mean
    and (population) std, and standardize the CURRENT session's bar-level N-min return/volume
    against it. Implemented via per-session (sum, sumsq, n) aggregates + a 20-session rolling
    sum of those aggregates (shifted by 1 session), not a bar-level rolling pool (equivalent,
    O(sessions) not O(bars)).
  - e410/e411 N-min return: log(close_t / close_{t-k}) computed ONLY within the same session
    (k=5 bars for 15-min, k=10 bars for 30-min; bar_idx_in_session >= k required) -- no window
    ever crosses a session boundary, consistent with every prior SMV2 engine.
  - e410/e411 event de-duplication: chronological non-overlapping scan (single global "busy
    until" bar pointer) -- a new event cannot open while a prior event's trade is still open.
    This is a disclosed INFERENCE (spec is silent on de-dup); the alternative (report ALL
    qualifying bars, including serially-correlated near-duplicates from the same underlying
    move) is also computed and reported as a secondary "all-qualifying-bars" count for
    transparency, but the non-overlapping series is used for every gate.
  - e410 exit: min(entry_idx+19 [60min], session_last_idx); "60min" reason exits at the CLOSE
    of the entry_idx+19 bar (matches SMV2K sim_e368's time-stop convention); "session_close"
    reason exits at the session's true last bar close.
  - e411 exit: identical mechanic, deadline = entry_idx+19 (60min) or entry_idx+39 (120min),
    capped by session_last_idx; ONE event list, per-hold net columns computed off the SAME
    entry (busy-until pointer uses the LONGER 120min hold so both hold columns never overlap
    a later event's entry).
  - e412 "direction of the ES-vs-(RTY+YM)/2 spread's roll-week drift" (INFERENCE, most material
    interpretive call in this run, HYPOTHESIS-labeled in the report): the frozen text names the
    roll week's OWN drift as the direction signal, but the entry is priced at that same week's
    Monday open -- using the week's own realized drift as both signal and entry point is
    look-ahead and was not implemented. Instead: direction = sign of the ES-vs-(RTY+YM)/2
    log-return spread measured over the 3 trading sessions immediately BEFORE the roll week's
    first session (close-to-close, causal, known before Monday's open) -- i.e. "does ES already
    look like it's pulling away from RTY/YM heading INTO the roll week", continued into NQ for
    the roll week italic. This preserves the spec's underlying liquidity-migration mechanism
    (ES/NQ react first) without using in-week information to pick the in-week trade's direction.
  - e412 exit: "actual NQ contract roll session" data is not available anywhere in this repo
    (no vendor roll-date calendar was in the CODE MAP or discoverable); the spec's own text
    permits a fallback ("... or Friday close if earlier"), so this run uses that fallback
    UNIFORMLY: exit = T's (the 3rd-Friday quarterly expiration session) true session close.
  - e412 roll week = the ISO week containing T (Mar/Jun/Sep/Dec 3rd Friday); entry session =
    the EARLIEST dev trading session in that ISO week (usually Monday; if Monday is a holiday,
    the next available session that week, mirroring how e398 let T itself float off a strict
    calendar day when the naive candidate wasn't a trading session).
"""
import sys, os, json
import numpy as np
import pandas as pd

REPO = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
os.chdir(REPO)
sys.path.insert(0, "src/analytics")
from sm01_solarsim import load_bars_3m, _fill, TICK
from smv2_common import boot_ci_mean

RUN = "runs/SMV2AB_ENGINE3_S4"
OUT = f"{RUN}/out"
os.makedirs(OUT, exist_ok=True)

PV = 20.0             # NQ point value ($/pt)
COMM_RT = 4.36         # $/round trip (NQ Lifetime, $2.18/side, matches CLAUDE.md frozen truth)
DEV_END = pd.Timestamp("2026-05-31")
NW_LAG = 5
SPLIT = pd.Timestamp("2024-12-31")     # 2022-24 vs 2025-26 (house convention)
BOOT_BLOCK, BOOT_B, BOOT_SEED = 5, 10000, 20260808
BURNIN_SESSIONS = 20

print("=" * 90, flush=True)
print("STEP 0: substrate + session calendar", flush=True)
print("=" * 90, flush=True)

# ----------------------------------------------------------------- NQ 3m (authoritative calendar)
nq_full = load_bars_3m()
nq_full["sd"] = pd.to_datetime(nq_full["sess_date"])
assert nq_full["sd"].max() < pd.Timestamp("2026-08-01"), "VIRGIN data in NQ 3m file?!"
g3 = nq_full.groupby("sess_id")
edges = g3["time"].max().to_numpy()          # session end times, sorted ascending by construction
sess_date_by_id = g3["sd"].first()
n3_by_id = g3.size()
assert np.all(np.diff(edges) > np.timedelta64(0, "ns")), "NQ 3m session end times not strictly increasing"

nq_dev = nq_full[nq_full["sd"] <= DEV_END].reset_index(drop=True)
nq_dev_dates = set(pd.to_datetime(nq_dev["sd"]).unique())
print(f"NQ 3m: {len(edges)} sessions total (thru {sess_date_by_id.iloc[-1].date()}); "
      f"dev (<=2026-05-31): {nq_dev['sess_id'].nunique()} sessions, {len(nq_dev)} bars", flush=True)


def build_3m_from_1m(path, tag):
    """1m OHLCV -> session-tagged 3m OHLCV, session ids/dates assigned via searchsorted against
    NQ's own session-end times (SMV2U step0_substrate.py method), then ceil('3min') bucketed
    within each assigned session."""
    df1 = pd.read_parquet(path)
    df1 = df1.sort_values("time").reset_index(drop=True)
    assert df1["time"].is_monotonic_increasing, f"{tag}: 1m timestamps not monotone"
    t1 = df1["time"].to_numpy()
    idx = np.searchsorted(edges, t1, side="left")
    n_oob = int((idx >= len(edges)).sum())
    idx_c = np.clip(idx, 0, len(edges) - 1)
    sess_ids = idx_c + 1
    df1["sess_id"] = sess_ids
    df1["sd"] = sess_date_by_id.reindex(sess_ids).to_numpy()
    df1["oob"] = idx >= len(edges)
    n1_by_id = df1.loc[~df1["oob"]].groupby("sess_id").size()

    d = df1.loc[~df1["oob"]].copy()
    d["b3"] = d["time"].dt.ceil("3min")
    g = d.groupby(["sess_id", "b3"], sort=True)
    bars3 = pd.DataFrame({
        "open": g["open"].first(), "high": g["high"].max(), "low": g["low"].min(),
        "close": g["close"].last(), "volume": g["volume"].sum(), "sd": g["sd"].first(),
    }).reset_index().rename(columns={"b3": "time"})
    bars3 = bars3.sort_values(["sess_id", "time"]).reset_index(drop=True)
    bars3 = bars3[bars3["sd"] <= DEV_END].reset_index(drop=True)
    n3_by_id_out = bars3.groupby("sess_id").size()
    print(f"{tag}: {len(df1)} 1m bars ({n_oob} out-of-NQ-calendar-bounds, dropped); "
          f"dev 3m: {bars3['sess_id'].nunique()} sessions, {len(bars3)} bars", flush=True)
    return bars3, n1_by_id, n3_by_id_out


es3, es_n1, es_n3 = build_3m_from_1m("runs/SM1M_ES_SUBSTRATE/out/es_1m_2022_2026.parquet", "ES")
rty3, rty_n1, rty_n3 = build_3m_from_1m("runs/SM1M_RTY_SUBSTRATE/out/rty_1m_2022_2026.parquet", "RTY")
ym3, ym_n1, ym_n3 = build_3m_from_1m("runs/SM1M_YM_SUBSTRATE/out/ym_1m_2022_2026.parquet", "YM")

# ----------------------------------------------------------------- session_calendar_check.csv
rows = []
for tag, b3, n3 in (("ES", es3, es_n3), ("RTY", rty3, rty_n3), ("YM", ym3, ym_n3)):
    dates = set(pd.to_datetime(b3["sd"]).unique())
    match = dates == nq_dev_dates
    only_other = sorted(dates - nq_dev_dates)
    only_nq = sorted(nq_dev_dates - dates)
    ratio = (n3.reindex(nq_dev.groupby("sess_id").size().index, fill_value=0) /
             nq_dev.groupby("sess_id").size()).replace([np.inf, -np.inf], np.nan)
    flagged = ratio[(ratio < 0.9) | (ratio > 1.1)]
    rows.append({
        "instrument": tag, "n_dev_sessions": b3["sd"].nunique(), "n_dev_bars": len(b3),
        "nq_n_dev_sessions": nq_dev["sess_id"].nunique(), "nq_n_dev_bars": len(nq_dev),
        "session_date_set_match_vs_nq_dev": bool(match),
        "n_dates_only_in_instrument": len(only_other), "dates_only_in_instrument": str(only_other),
        "n_dates_only_in_nq": len(only_nq), "dates_only_in_nq": str(only_nq),
        "n_sessions_bar_count_ratio_outside_0.9_1.1": int(len(flagged)),
    })
calcheck = pd.DataFrame(rows)
calcheck.to_csv(f"{OUT}/session_calendar_check.csv", index=False)
print(calcheck.to_string(), flush=True)
# FACT: ES matches the NQ dev session-date set exactly. RTY/YM are each missing the SAME 7
# sessions (2023-04-06..2023-04-14), a genuine gap in the SM1M_{RTY,YM}_SUBSTRATE source files
# (an 11-day timestamp gap confirmed directly in the raw 1m parquet, not an artifact of this
# script's aggregation/session-tagging) -- consistent with the campaign's known 2023-04-05/06
# boundary irregularity (see SMV2Z spec's own "2023-04-05/06 boundary pair" note). This is a
# disclosed, pre-existing substrate limitation, not something this run fabricates or patches;
# per CLAUDE.md ("never delete raw research evidence ... never rewrite historical results") and
# the CODE MAP's "verify columns before use, do not rewrite", the correct handling is to drop
# those 7 sessions from any RTY/YM-dependent analysis (the inner-join merged table below does
# this automatically) and disclose it here, not to interpolate or refuse to run.
for _, r in calcheck.iterrows():
    ok = r["session_date_set_match_vs_nq_dev"] or (r["n_dates_only_in_nq"] <= 10 and r["n_dates_only_in_instrument"] == 0)
    assert ok, f"{r['instrument']}: session date set mismatch vs NQ dev exceeds the disclosed small-gap tolerance!"
    tag = "EXACT MATCH" if r["session_date_set_match_vs_nq_dev"] else \
        f"MATCH except {r['n_dates_only_in_nq']} NQ sessions absent from {r['instrument']} (disclosed gap, see above)"
    print(f"  {r['instrument']}: {tag}", flush=True)
print("session calendar check: ES exact match; RTY/YM match except the disclosed 2023-04 gap.", flush=True)

# ----------------------------------------------------------------- merged aligned bar table
def prep(df, pfx):
    d = df[["time", "sess_id", "sd", "open", "high", "low", "close", "volume"]].copy()
    return d.rename(columns={c: f"{pfx}_{c}" for c in ("open", "high", "low", "close", "volume")})

nq_p = nq_dev[["time", "sess_id", "sd", "open", "high", "low", "close", "volume", "is_last_of_sess"]].rename(
    columns={c: f"nq_{c}" for c in ("open", "high", "low", "close", "volume")})
es_p = prep(es3, "es")
rty_p = prep(rty3, "rty")
ym_p = prep(ym3, "ym")

M = nq_p.merge(es_p[["time", "es_open", "es_high", "es_low", "es_close", "es_volume"]], on="time", how="inner") \
        .merge(rty_p[["time", "rty_open", "rty_high", "rty_low", "rty_close", "rty_volume"]], on="time", how="inner") \
        .merge(ym_p[["time", "ym_open", "ym_high", "ym_low", "ym_close", "ym_volume"]], on="time", how="inner")
M = M.sort_values("time").reset_index(drop=True)
print(f"\nmerged aligned 3m table (inner join NQ/ES/RTY/YM on time): {len(M)} bars "
      f"(NQ dev had {len(nq_dev)}; dropped {len(nq_dev) - len(M)} bars lacking a concurrent "
      f"ES+RTY+YM 3m bar)", flush=True)

M["bar_idx_in_sess"] = M.groupby("sess_id").cumcount()
sess_size = M.groupby("sess_id")["time"].transform("size")
M["last_idx_in_sess"] = sess_size - 1
M["is_last_of_sess"] = M["bar_idx_in_sess"] == M["last_idx_in_sess"]
M.to_parquet(f"{OUT}/merged_3m_dev.parquet")

print("\nstep 0 done.\n", flush=True)

# ============================================================================ shared helpers
SESSION_ORDER = np.sort(M["sess_id"].unique())
SESS_RANK = pd.Series(np.arange(len(SESSION_ORDER)), index=SESSION_ORDER)
M["sess_rank"] = M["sess_id"].map(SESS_RANK).to_numpy()
M["sd"] = pd.to_datetime(M["sd"])

# global-row-index of each row's own session's LAST bar (contiguous blocks since M is time-sorted)
_row_pos = np.arange(len(M))
M["sess_last_gidx"] = _row_pos - M["bar_idx_in_sess"].to_numpy() + M["last_idx_in_sess"].to_numpy()

nq_o = M["nq_open"].to_numpy(); nq_h = M["nq_high"].to_numpy()
nq_l = M["nq_low"].to_numpy(); nq_c = M["nq_close"].to_numpy()
sess_last_gidx = M["sess_last_gidx"].to_numpy()
bar_idx_in_sess = M["bar_idx_in_sess"].to_numpy()
last_idx_in_sess = M["last_idx_in_sess"].to_numpy()
sd_arr = M["sd"].to_numpy()
sess_rank_arr = M["sess_rank"].to_numpy()


def add_kbar_ret_vol(df, close_col, vol_col, k, out_prefix):
    df[f"{out_prefix}_ret{k}"] = np.log(df[close_col] / df.groupby("sess_id")[close_col].shift(k))
    df[f"{out_prefix}_vol{k}"] = df.groupby("sess_id")[vol_col].rolling(k, min_periods=k).sum() \
        .reset_index(level=0, drop=True)
    return df


def trailing_session_stats(df, col, n_sessions=BURNIN_SESSIONS):
    """Session-causal trailing n_sessions pooled mean/std of `col` (bar-level obs), EXCLUDING
    the current session (shift(1) at the session-aggregate level). Returns two bar-aligned
    np arrays (mean_trail, std_trail), NaN wherever fewer than n_sessions prior sessions exist
    in this table (burn-in) or the trailing pool has <2 observations."""
    x = df[col]
    valid = x.notna()
    s = pd.DataFrame({"sess_id": df["sess_id"], "x": x.where(valid, 0.0), "v": valid.astype(float)})
    agg = s.groupby("sess_id").agg(sumx=("x", "sum"), sumx2=("x", lambda z: float((z ** 2).sum())),
                                    n=("v", "sum"))
    agg = agg.reindex(SESSION_ORDER).fillna(0.0)
    tr_sumx = agg["sumx"].rolling(n_sessions).sum().shift(1)
    tr_sumx2 = agg["sumx2"].rolling(n_sessions).sum().shift(1)
    tr_n = agg["n"].rolling(n_sessions).sum().shift(1)
    mean_tr = tr_sumx / tr_n
    var_tr = (tr_sumx2 / tr_n) - mean_tr ** 2
    var_tr = var_tr.clip(lower=0.0)
    std_tr = np.sqrt(var_tr)
    std_tr = std_tr.where(tr_n >= 2)
    mean_map = mean_tr.reindex(df["sess_id"]).to_numpy()
    std_map = std_tr.reindex(df["sess_id"]).to_numpy()
    return mean_map, std_map


def zscore(df, col, n_sessions=BURNIN_SESSIONS):
    mean_map, std_map = trailing_session_stats(df, col, n_sessions)
    with np.errstate(invalid="ignore", divide="ignore"):
        z = (df[col].to_numpy() - mean_map) / std_map
    return z


def nw_stats(x, sess_dates, lag=NW_LAG):
    x = np.asarray(x, dtype=float); n = len(x)
    out = {"n": n, "mean": np.nan, "total": np.nan, "t_nw": np.nan, "n_sessions": 0}
    if n == 0:
        return out
    xbar = x.mean()
    out["mean"] = xbar; out["total"] = x.sum()
    if n < 3:
        return out
    dfz = pd.DataFrame({"x": x - xbar, "s": pd.to_datetime(list(sess_dates))})
    z = dfz.groupby("s", sort=True)["x"].sum().to_numpy()
    out["n_sessions"] = len(z)
    Snw = float((z ** 2).sum())
    L = min(lag, len(z) - 1)
    for l in range(1, L + 1):
        w = 1.0 - l / (lag + 1.0)
        Snw += 2.0 * w * float((z[l:] * z[:-l]).sum())
    if Snw > 0:
        out["t_nw"] = xbar / (np.sqrt(Snw) / n)
    return out


def split_stats(sd, net):
    sd = pd.to_datetime(pd.Series(sd)); net = pd.Series(net).reset_index(drop=True)
    sd = sd.reset_index(drop=True)
    h1 = net[sd.values <= SPLIT]; h2 = net[sd.values > SPLIT]
    a = nw_stats(h1, sd[sd.values <= SPLIT]); b = nw_stats(h2, sd[sd.values > SPLIT])
    return a, b


def boot_p(net):
    if len(net) < 5:
        return np.nan
    _, _, p = boot_ci_mean(np.asarray(net, dtype=float), block=BOOT_BLOCK, n_boot=BOOT_B, seed=BOOT_SEED)
    return p


def sgn(v):
    return int(np.sign(v)) if np.isfinite(v) else 0


def fill_open(i, side):
    return _fill(nq_o[i], nq_h[i], nq_l[i], side)


def fill_close_at(i, side):
    return _fill(nq_o[i], nq_h[i], nq_l[i], side, at_close=nq_c[i])


def event_scan(mask, direction_arr, hold_bars_list):
    """Chronological non-overlapping scan over the merged bar array. mask[i]=True is a
    'trigger' bar; entry fills at open of bar i+1 (must be same session, i.e. i is not the
    session's last bar), direction = direction_arr[i]; for each hold in hold_bars_list, the
    exit deadline is min(entry_idx + hold - 1, session_last_gidx of the entry bar). The event's
    busy-until pointer uses the LONGEST hold so no later trigger can fire while ANY reported
    hold's trade could still be open. Returns (events_df, n_raw_qualifying_bars)."""
    n = len(mask)
    n_raw = int(mask.sum())
    events = []
    i = 0
    max_hold = max(hold_bars_list)
    while i < n:
        if mask[i] and bar_idx_in_sess[i] < last_idx_in_sess[i] and direction_arr[i] != 0:
            entry_idx = i + 1
            row = {"trigger_gidx": i, "entry_gidx": entry_idx, "sd": sd_arr[entry_idx],
                   "dir": int(direction_arr[i])}
            for hold in hold_bars_list:
                deadline = min(entry_idx + hold - 1, sess_last_gidx[entry_idx])
                row[f"deadline_gidx_h{hold}"] = deadline
            deadline_max = row[f"deadline_gidx_h{max_hold}"]
            row["deadline_gidx"] = deadline_max
            events.append(row)
            i = deadline_max + 1
        else:
            i += 1
    ev = pd.DataFrame(events)
    return ev, n_raw


def price_hold(ev, hold, entry_col="entry_gidx"):
    """Given events_df with entry_gidx/dir and a hold (bar count), compute entry_px, exit_px,
    exit_reason, net for that hold using the frozen fill convention (open entry; deadline bar
    CLOSE if time-capped, true session-close CLOSE if session ends first -- same formula either
    way since the deadline row IS the session's last bar in the session_close case)."""
    entry_idx = ev[entry_col].to_numpy()
    d = ev["dir"].to_numpy()
    deadline = ev[f"deadline_gidx_h{hold}"].to_numpy()
    entry_px = np.array([_fill(nq_o[e], nq_h[e], nq_l[e], dd) for e, dd in zip(entry_idx, d)])
    exit_px = np.array([_fill(nq_o[x], nq_h[x], nq_l[x], -dd, at_close=nq_c[x])
                         for x, dd in zip(deadline, d)])
    is_sess_close = deadline == sess_last_gidx[entry_idx]
    reason = np.where(is_sess_close, "session_close", f"{hold * 3}min")
    net = d * (exit_px - entry_px) * PV - COMM_RT
    return entry_px, exit_px, reason, net


# ============================================================================ ENGINE 410
print("=" * 90, flush=True)
print("ENGINE 410: cap-tier dispersion catch-up (ES+NQ 15-min consensus, RTY laggard)", flush=True)
print("=" * 90, flush=True)

M = add_kbar_ret_vol(M, "nq_close", "nq_volume", 5, "nq")
M = add_kbar_ret_vol(M, "es_close", "es_volume", 5, "es")
M = add_kbar_ret_vol(M, "rty_close", "rty_volume", 5, "rty")

z_nq_ret5 = zscore(M, "nq_ret5")
z_es_ret5 = zscore(M, "es_ret5")
z_rty_ret5 = zscore(M, "rty_ret5")
z_nq_vol5 = zscore(M, "nq_vol5")
z_es_vol5 = zscore(M, "es_vol5")

nq_ret5 = M["nq_ret5"].to_numpy(); es_ret5 = M["es_ret5"].to_numpy(); rty_ret5 = M["rty_ret5"].to_numpy()
consensus_sign = np.where(np.sign(nq_ret5) == np.sign(es_ret5), np.sign(nq_ret5), 0.0)
burnin_ok = sess_rank_arr >= BURNIN_SESSIONS
base410_ok = (burnin_ok & np.isfinite(z_nq_ret5) & np.isfinite(z_es_ret5) & np.isfinite(z_rty_ret5)
              & np.isfinite(z_nq_vol5) & np.isfinite(z_es_vol5) & (consensus_sign != 0))


def e410_mask(Z, volz=1.0, rtyz=0.5):
    m = base410_ok.copy()
    m &= (np.abs(z_nq_ret5) > Z) & (np.abs(z_es_ret5) > Z)
    m &= (z_nq_vol5 > volz) & (z_es_vol5 > volz)
    rty_confirmed_catchup = (np.sign(rty_ret5) == consensus_sign) & (np.abs(z_rty_ret5) > rtyz)
    m &= ~rty_confirmed_catchup
    return m


e410_grid_rows = []
e410_events_center = None
for Z in (1.25, 1.5, 1.75):
    mask = e410_mask(Z)
    ev, n_raw = event_scan(mask, consensus_sign, [20])   # 20 bars = 60min
    if len(ev):
        entry_px, exit_px, reason, net = price_hold(ev, 20)
        ev["entry_px"] = entry_px; ev["exit_px"] = exit_px; ev["exit_reason"] = reason; ev["net"] = net
    else:
        ev["entry_px"] = ev["exit_px"] = ev["exit_reason"] = ev["net"] = pd.Series(dtype=float)
    st = nw_stats(ev["net"], ev["sd"]) if len(ev) else nw_stats([], [])
    st.update({"z_threshold": Z, "n_raw_qualifying_bars": n_raw,
               "p_boot": boot_p(ev["net"].to_numpy()) if len(ev) else np.nan})
    if len(ev):
        h1, h2 = split_stats(ev["sd"], ev["net"])
        st["wf_2022_24_mean"] = h1["mean"]; st["wf_2022_24_t"] = h1["t_nw"]; st["wf_2022_24_n"] = h1["n"]
        st["wf_2025_26_mean"] = h2["mean"]; st["wf_2025_26_t"] = h2["t_nw"]; st["wf_2025_26_n"] = h2["n"]
    e410_grid_rows.append(st)
    if Z == 1.5:
        e410_events_center = ev.copy()
    print(f"e410 Z={Z:.2f}  N={st['n']:4d} (raw qualifying bars {n_raw:5d})  "
          f"mean={st['mean']:8.2f}  t_nw={st['t_nw']:6.2f}", flush=True)

e410_events_center.to_csv(f"{OUT}/e410_events.csv", index=False)
e410_summary = pd.DataFrame(e410_grid_rows)
e410_summary.to_csv(f"{OUT}/e410_summary.csv", index=False)
print(e410_summary[["z_threshold", "n", "mean", "total", "t_nw", "p_boot",
                     "wf_2022_24_mean", "wf_2025_26_mean"]].round(3).to_string(), flush=True)

g410_center = e410_summary[e410_summary["z_threshold"] == 1.5].iloc[0]
plateau410_signs = set(sgn(v) for v in e410_summary["mean"])
gate410 = pd.DataFrame([
    {"engine": "e410", "gate": "N>=60", "value": g410_center["n"], "pass": bool(g410_center["n"] >= 60)},
    {"engine": "e410", "gate": "t_nw>=2", "value": g410_center["t_nw"], "pass": bool(g410_center["t_nw"] >= 2)},
    {"engine": "e410", "gate": "WF_same_sign",
     "value": f"{g410_center['wf_2022_24_mean']:.2f}|{g410_center['wf_2025_26_mean']:.2f}",
     "pass": bool(sgn(g410_center["wf_2022_24_mean"]) == sgn(g410_center["wf_2025_26_mean"]) != 0)},
    {"engine": "e410", "gate": "plateau_z1.25_1.5_1.75_same_sign", "value": str(sorted(plateau410_signs)),
     "pass": bool(len(plateau410_signs) == 1)},
])
print(gate410.to_string(), flush=True)
verdict_410 = "PASS" if bool(gate410["pass"].all()) else "FAIL"
print(f"E410 VERDICT: {verdict_410}\n", flush=True)

# ============================================================================ ENGINE 411
print("=" * 90, flush=True)
print("ENGINE 411: duration-spread shock reaction (NQ 30-min shock w/o proportional YM move)", flush=True)
print("=" * 90, flush=True)

M = add_kbar_ret_vol(M, "nq_close", "nq_volume", 10, "nq")
M = add_kbar_ret_vol(M, "ym_close", "ym_volume", 10, "ym")

z_nq_ret10 = zscore(M, "nq_ret10")
z_ym_ret10 = zscore(M, "ym_ret10")
nq_ret10 = M["nq_ret10"].to_numpy()
nq_dir10 = np.sign(nq_ret10)
base411_ok = burnin_ok & np.isfinite(z_nq_ret10) & np.isfinite(z_ym_ret10) & (nq_dir10 != 0)


def e411_mask(ymz, shockz=2.0):
    m = base411_ok.copy()
    m &= (np.abs(z_nq_ret10) >= shockz)
    m &= (np.abs(z_ym_ret10) < ymz)
    return m


e411_grid_rows = []
e411_events_center = None
for ymz in (0.5, 0.75, 1.0):
    mask = e411_mask(ymz)
    ev, n_raw = event_scan(mask, nq_dir10, [20, 40])   # 60min, 120min
    if len(ev):
        for hold, tag in ((20, "h60"), (40, "h120")):
            entry_px, exit_px, reason, net = price_hold(ev, hold)
            ev[f"entry_px_{tag}"] = entry_px; ev[f"exit_px_{tag}"] = exit_px
            ev[f"exit_reason_{tag}"] = reason; ev[f"net_{tag}"] = net
    st = nw_stats(ev["net_h60"], ev["sd"]) if len(ev) else nw_stats([], [])
    st.update({"ym_quiet_threshold": ymz, "n_raw_qualifying_bars": n_raw,
               "p_boot": boot_p(ev["net_h60"].to_numpy()) if len(ev) else np.nan})
    if len(ev):
        h1, h2 = split_stats(ev["sd"], ev["net_h60"])
        st["wf_2022_24_mean"] = h1["mean"]; st["wf_2022_24_t"] = h1["t_nw"]; st["wf_2022_24_n"] = h1["n"]
        st["wf_2025_26_mean"] = h2["mean"]; st["wf_2025_26_t"] = h2["t_nw"]; st["wf_2025_26_n"] = h2["n"]
        st["mean_h120"] = ev["net_h120"].mean(); st["t_nw_h120"] = nw_stats(ev["net_h120"], ev["sd"])["t_nw"]
    e411_grid_rows.append(st)
    if ymz == 0.75:
        e411_events_center = ev.copy()
    print(f"e411 YMquiet<{ymz:.2f}  N={st['n']:4d} (raw qualifying bars {n_raw:5d})  "
          f"mean_h60={st['mean']:8.2f}  t_nw_h60={st['t_nw']:6.2f}", flush=True)

e411_events_center.to_csv(f"{OUT}/e411_events.csv", index=False)
e411_summary = pd.DataFrame(e411_grid_rows)
e411_summary.to_csv(f"{OUT}/e411_summary.csv", index=False)
print(e411_summary[["ym_quiet_threshold", "n", "mean", "total", "t_nw", "p_boot",
                     "wf_2022_24_mean", "wf_2025_26_mean", "mean_h120"]].round(3).to_string(), flush=True)

g411_center = e411_summary[e411_summary["ym_quiet_threshold"] == 0.75].iloc[0]
plateau411_signs = set(sgn(v) for v in e411_summary["mean"])
hold_signs_411 = set(sgn(v) for v in (g411_center["mean"], g411_center["mean_h120"]))
gate411 = pd.DataFrame([
    {"engine": "e411", "gate": "N>=40", "value": g411_center["n"], "pass": bool(g411_center["n"] >= 40)},
    {"engine": "e411", "gate": "t_nw>=2 (h60)", "value": g411_center["t_nw"], "pass": bool(g411_center["t_nw"] >= 2)},
    {"engine": "e411", "gate": "WF_same_sign (h60)",
     "value": f"{g411_center['wf_2022_24_mean']:.2f}|{g411_center['wf_2025_26_mean']:.2f}",
     "pass": bool(sgn(g411_center["wf_2022_24_mean"]) == sgn(g411_center["wf_2025_26_mean"]) != 0)},
    {"engine": "e411", "gate": "plateau_ymquiet_0.5_0.75_1.0_same_sign", "value": str(sorted(plateau411_signs)),
     "pass": bool(len(plateau411_signs) == 1)},
    {"engine": "e411", "gate": "DISCLOSED_EXTRA_hold60_hold120_same_sign (not in frozen spec's pass: list)",
     "value": str(sorted(hold_signs_411)), "pass": bool(len(hold_signs_411) == 1)},
])
print(gate411.to_string(), flush=True)
verdict_411 = "PASS" if bool(gate411[gate411["gate"] != "DISCLOSED_EXTRA_hold60_hold120_same_sign (not in frozen spec's pass: list)"]["pass"].all()) else "FAIL"
print(f"E411 VERDICT: {verdict_411}\n", flush=True)

# ============================================================================ ENGINE 412
print("=" * 90, flush=True)
print("ENGINE 412: quarterly roll basis convergence (ES-vs-(RTY+YM)/2 pre-week spread -> NQ)", flush=True)
print("=" * 90, flush=True)

sess_first = M.groupby("sess_id").first()
sess_last = M.groupby("sess_id").last()
SESS = pd.DataFrame({
    "sess_id": SESSION_ORDER,
    "sd": sess_first.loc[SESSION_ORDER, "sd"].to_numpy(),
    "nq_o0": sess_first.loc[SESSION_ORDER, "nq_open"].to_numpy(),
    "nq_h0": sess_first.loc[SESSION_ORDER, "nq_high"].to_numpy(),
    "nq_l0": sess_first.loc[SESSION_ORDER, "nq_low"].to_numpy(),
    "nq_o_last": sess_last.loc[SESSION_ORDER, "nq_open"].to_numpy(),
    "nq_h_last": sess_last.loc[SESSION_ORDER, "nq_high"].to_numpy(),
    "nq_l_last": sess_last.loc[SESSION_ORDER, "nq_low"].to_numpy(),
    "nq_c_last": sess_last.loc[SESSION_ORDER, "nq_close"].to_numpy(),
    "es_c_last": sess_last.loc[SESSION_ORDER, "es_close"].to_numpy(),
    "rty_c_last": sess_last.loc[SESSION_ORDER, "rty_close"].to_numpy(),
    "ym_c_last": sess_last.loc[SESSION_ORDER, "ym_close"].to_numpy(),
}).reset_index(drop=True)
SESS["rank"] = np.arange(len(SESS))


def wkey(idx):    # ISO week of session date -- matches SMV2Q/SMV2X/SMV2Z convention exactly
    iso = pd.DatetimeIndex(idx).isocalendar()
    return (iso["year"].astype(int) * 100 + iso["week"].astype(int)).to_numpy()


SESS["week_key"] = wkey(SESS["sd"])
SD_SET = set(pd.to_datetime(SESS["sd"]))
SD_TO_RANK = dict(zip(pd.to_datetime(SESS["sd"]), SESS["rank"]))
WK_TO_RANKS = {}
for rk, wk in zip(SESS["rank"], SESS["week_key"]):
    WK_TO_RANKS.setdefault(int(wk), []).append(rk)

FIRST_SD_412 = SESS["sd"].iloc[0]
q_all = pd.date_range(f"{FIRST_SD_412.year}-01-01", DEV_END, freq="WOM-3FRI")
q_dates = [pd.Timestamp(t.date()) for t in q_all if t.month in (3, 6, 9, 12)]

calendar_rows = []
e412_rows = []
for T in q_dates:
    in_cal = T in SD_SET
    row = {"T": T, "in_session_calendar": in_cal}
    if not in_cal:
        row["excluded_reason"] = "T is not a trading session (holiday, e.g. Good Friday)"
        calendar_rows.append(row)
        continue
    T_rank = SD_TO_RANK[T]
    wk = int(SESS.loc[T_rank, "week_key"])
    week_ranks = sorted(WK_TO_RANKS.get(wk, []))
    entry_rank = week_ranks[0]
    row["week_key"] = wk
    row["entry_sd"] = SESS.loc[entry_rank, "sd"]
    if entry_rank == T_rank:
        row["excluded_reason"] = "roll week has only 1 trading session (T itself) -- no separate entry point"
        calendar_rows.append(row)
        continue
    if entry_rank < 4:
        row["excluded_reason"] = "insufficient dev history for the 3-session pre-window signal"
        calendar_rows.append(row)
        continue
    row["excluded_reason"] = None
    calendar_rows.append(row)

    def sret(col, a, b):
        return np.log(SESS.loc[b, col] / SESS.loc[a, col])

    ret_es_pre = sret("es_c_last", entry_rank - 4, entry_rank - 1)
    ret_rty_pre = sret("rty_c_last", entry_rank - 4, entry_rank - 1)
    ret_ym_pre = sret("ym_c_last", entry_rank - 4, entry_rank - 1)
    spread_pre = ret_es_pre - (ret_rty_pre + ret_ym_pre) / 2.0
    direction = int(np.sign(spread_pre))
    if direction == 0:
        continue
    entry_px = _fill(SESS.loc[entry_rank, "nq_o0"], SESS.loc[entry_rank, "nq_h0"],
                      SESS.loc[entry_rank, "nq_l0"], direction)
    exit_px = _fill(SESS.loc[T_rank, "nq_o_last"], SESS.loc[T_rank, "nq_h_last"],
                     SESS.loc[T_rank, "nq_l_last"], -direction, at_close=SESS.loc[T_rank, "nq_c_last"])
    net = direction * (exit_px - entry_px) * PV - COMM_RT
    e412_rows.append({
        "T": T, "week_key": wk, "entry_sd": SESS.loc[entry_rank, "sd"], "exit_sd": T,
        "hold_sessions": T_rank - entry_rank + 1, "ret_es_pre": ret_es_pre, "ret_rty_pre": ret_rty_pre,
        "ret_ym_pre": ret_ym_pre, "spread_pre": spread_pre, "dir": direction,
        "entry_px": entry_px, "exit_px": exit_px, "net": net,
    })

e412 = pd.DataFrame(e412_rows)
e412.to_csv(f"{OUT}/e412_events.csv", index=False)
e412_calendar = pd.DataFrame(calendar_rows)
e412_calendar.to_csv(f"{OUT}/e412_expiry_calendar.csv", index=False)
n_excluded = int(e412_calendar["excluded_reason"].notna().sum())
print(f"e412: {len(q_dates)} quarterly 3rd-Friday candidates; {n_excluded} excluded (see "
      f"e412_expiry_calendar.csv); {len(e412)} tradeable cycles (spread_pre != 0 required)", flush=True)

st412 = nw_stats(e412["net"], e412["entry_sd"]) if len(e412) else nw_stats([], [])
st412["p_boot"] = boot_p(e412["net"].to_numpy()) if len(e412) else np.nan
if len(e412):
    h1, h2 = split_stats(e412["entry_sd"], e412["net"])
    st412["wf_2022_24_mean"] = h1["mean"]; st412["wf_2022_24_t"] = h1["t_nw"]; st412["wf_2022_24_n"] = h1["n"]
    st412["wf_2025_26_mean"] = h2["mean"]; st412["wf_2025_26_t"] = h2["t_nw"]; st412["wf_2025_26_n"] = h2["n"]
e412_summary = pd.DataFrame([st412])
e412_summary.to_csv(f"{OUT}/e412_summary.csv", index=False)
print(e412_summary.round(3).to_string(), flush=True)

gate412 = pd.DataFrame([
    {"engine": "e412", "gate": "N>=12 (disclosed power floor)", "value": st412["n"], "pass": bool(st412["n"] >= 12)},
    {"engine": "e412", "gate": "t_nw>=2", "value": st412["t_nw"], "pass": bool(np.isfinite(st412["t_nw"]) and st412["t_nw"] >= 2)},
    {"engine": "e412", "gate": "WF_same_sign",
     "value": f"{st412.get('wf_2022_24_mean', np.nan):.2f}|{st412.get('wf_2025_26_mean', np.nan):.2f}" if len(e412) else "n/a",
     "pass": bool(len(e412) and sgn(st412["wf_2022_24_mean"]) == sgn(st412["wf_2025_26_mean"]) != 0)},
])
print(gate412.to_string(), flush=True)
verdict_412 = "PASS" if bool(gate412["pass"].all()) else "FAIL"
print(f"E412 VERDICT: {verdict_412}\n", flush=True)

# ============================================================================ (joint whipsaw)
print("=" * 90, flush=True)
print("JOINT_WHIPSAW_TARGETING complementarity (V4.1 s14 primary read -- all 3 engines,", flush=True)
print("regardless of pass/fail) vs SMV2Z's 23 sigma460+ER150-flagged weeks", flush=True)
print("=" * 90, flush=True)

ALL_SD = pd.DatetimeIndex(SESS["sd"])
WK = pd.Series(wkey(ALL_SD), index=ALL_SD)

pol = pd.read_csv("runs/SMV2Z_VIABILITY_POLICY/out/policy_daily.csv")
jl_weeks = set(pol.loc[pol["scaled"] == True, "week_key"].astype(int).unique())
assert len(jl_weeks) == 23, f"expected 23 SMV2Z-flagged weeks, got {len(jl_weeks)} (spec says reuse verbatim)"
print(f"SMV2Z flagged weeks reused verbatim: {len(jl_weeks)} -> {sorted(jl_weeks)}", flush=True)

jl_mask_by_sd = WK.isin(jl_weeks)
n_dev_weeks_412 = WK.nunique()
n_flagged_present = int(jl_mask_by_sd.groupby(WK).first().sum())
print(f"dev sessions (this run's merged calendar) map to {n_dev_weeks_412} distinct ISO weeks; "
      f"{n_flagged_present} of those are SMV2Z-flagged weeks (all 23 expected present given the "
      f"flagged set's own date range sits inside 2024-2026, clear of the disclosed 2023-04 RTY/YM "
      f"gap)", flush=True)
assert n_flagged_present == 23, "not all 23 SMV2Z-flagged weeks are represented in this run's dev calendar!"

rc = pd.read_csv("runs/SMV2H_ONECONTRACT/out/rerank_curves.csv", parse_dates=["sess"])
rc = rc[rc["sess"] <= DEV_END].set_index("sess")
champ = rc["60_40"].reindex(ALL_SD, fill_value=0.0)


def mtm_decompose_412(entry_rank, exit_rank, entry_px, exit_px, direction, comm_rt=COMM_RT):
    out = {}
    for rk in range(entry_rank, exit_rank + 1):
        sd_i = SESS.loc[rk, "sd"]
        ref_prev = entry_px if rk == entry_rank else SESS.loc[rk - 1, "nq_c_last"]
        ref_now = exit_px if rk == exit_rank else SESS.loc[rk, "nq_c_last"]
        pnl = direction * (ref_now - ref_prev) * PV
        if rk == exit_rank:
            pnl -= comm_rt
        out[sd_i] = out.get(sd_i, 0.0) + pnl
    return out


e410_daily = e410_events_center.groupby("sd")["net"].sum().reindex(ALL_SD, fill_value=0.0)
e411_daily = e411_events_center.groupby("sd")["net_h60"].sum().reindex(ALL_SD, fill_value=0.0)
if len(e412):
    e412_rank_map = dict(zip(SESS["sd"], SESS["rank"]))
    mtm_list = [mtm_decompose_412(e412_rank_map[r.entry_sd], e412_rank_map[r.exit_sd],
                                   r.entry_px, r.exit_px, r.dir) for r in e412.itertuples()]
    tot = {}
    for d in mtm_list:
        for k, v in d.items():
            tot[k] = tot.get(k, 0.0) + v
    e412_daily = pd.Series(tot).reindex(ALL_SD, fill_value=0.0)
    assert abs(e412_daily.sum() - e412["net"].sum()) < 1e-6, "e412 MTM decomposition mismatch"
else:
    e412_daily = pd.Series(0.0, index=ALL_SD)

ENGINE_DAILY = {"e410_dispersion_catchup": e410_daily, "e411_shock_reaction_h60": e411_daily,
                "e412_roll_basis_convergence_mtm": e412_daily}

comp_rows = []
for name, ed in ENGINE_DAILY.items():
    ed = ed.reindex(ALL_SD, fill_value=0.0)
    ew = ed.groupby(WK).sum()
    cw = champ.groupby(WK).sum()
    corr_daily = float(ed.corr(champ))
    corr_weekly = float(ew.corr(cw))
    ew_jl = ew[ew.index.isin(jl_weeks)]
    ew_other = ew[~ew.index.isin(jl_weeks)]
    cw_jl = cw[cw.index.isin(jl_weeks)]
    cw_other = cw[~cw.index.isin(jl_weeks)]
    comp_rows.append({
        "engine": name, "n_days_dev": len(ed), "n_event_days": int((ed != 0).sum()),
        "corr_daily_vs_champ": corr_daily, "corr_weekly_vs_champ": corr_weekly,
        "n_weeks_dev": len(ew), "n_jointwhipsaw_weeks": len(ew_jl),
        "engine_total_all_weeks": float(ew.sum()), "engine_mean_week_all": float(ew.mean()),
        "engine_mean_week_jointwhipsaw": float(ew_jl.mean()) if len(ew_jl) else np.nan,
        "engine_total_jointwhipsaw": float(ew_jl.sum()) if len(ew_jl) else 0.0,
        "engine_mean_week_other": float(ew_other.mean()) if len(ew_other) else np.nan,
        "engine_n_jw_weeks_with_events": int((ew_jl != 0).sum()) if len(ew_jl) else 0,
        "champ_mean_week_all": float(cw.mean()), "champ_mean_week_jointwhipsaw": float(cw_jl.mean()) if len(cw_jl) else np.nan,
        "champ_mean_week_other": float(cw_other.mean()) if len(cw_other) else np.nan,
    })
jw_comp = pd.DataFrame(comp_rows)
jw_comp.to_csv(f"{OUT}/jointwhipsaw_complementarity.csv", index=False)
print(jw_comp.round(3).to_string(), flush=True)

verdicts_all = {"e410": verdict_410, "e411": verdict_411, "e412": verdict_412}
with open(f"{OUT}/verdicts.json", "w") as f:
    json.dump(verdicts_all, f, indent=2)
gates_all = pd.concat([gate410, gate411, gate412], ignore_index=True)
gates_all.to_csv(f"{OUT}/gates.csv", index=False)

print("\nVERDICTS:", verdicts_all, flush=True)
print("\ndone.", flush=True)


