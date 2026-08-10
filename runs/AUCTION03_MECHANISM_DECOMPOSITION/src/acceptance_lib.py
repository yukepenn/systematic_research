"""AUCTION03 mechanism decomposition, part 3 -- shared library for the
"new-value acceptance" feature family.

Conventions reused verbatim from runs/AUCTION01_VALUE_STATE/src/02_build_poc_substrate.py
(read, not modified): tick_size=0.25, per-session sort by time, bip==0 (Last
trade prints only) from research/scalping_lab/substrate/raw/NQ/s<date>.parquet
(+ _rth companion file when present, same dedupe key), causal running-POC
definition (`causal_running_poc`, copied verbatim), and 1-second-grid
downsampling via last-observation-per-second + ffill (matching
research/scalping_lab/src/python/build_grid1s.py's own convention).

DATA SCOPE: this module hardcodes the exact 37 discovery + 8 confirmation
session tags it is permitted to touch. No glob of raw/NQ, grid1s/NQ, or
sechilo/NQ ever occurs here -- every file path is built from one of the two
constants below. Do not add sessions to these lists.
"""
import os
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RAW = os.path.join(ROOT, "research", "scalping_lab", "substrate", "raw", "NQ")
GRID1S = os.path.join(ROOT, "research", "scalping_lab", "substrate", "grid1s", "NQ")

TICK = 0.25
WINDOW_S = 60  # trailing window, seconds -- chosen for consistency with the
# existing codebase's own 60s constants (poc_migration_60s_ticks in
# AUCTION01, liq60 in AUCTION01's decision-point liquidity gate). No new time
# constant is introduced.

DISCOVERY = (
    "20250814 20250820 20250901 20250902 20250905 20250910 20250911 20250922 "
    "20251002 20251009 20251027 20251029 20251110 20251117 20251124 20251128 "
    "20251209 20251222 20260123 20260206 20260211 20260218 20260220 20260223 "
    "20260303 20260312 20260317 20260320 20260406 20260409 20260417 20260423 "
    "20260428 20260506 20260511 20260519 20260520"
).split()

CONFIRMATION = (
    "20250819 20250912 20251028 20251125 20260217 20260302 20260422 20260512"
).split()

assert len(DISCOVERY) == 37, len(DISCOVERY)
assert len(CONFIRMATION) == 8, len(CONFIRMATION)
assert set(DISCOVERY).isdisjoint(CONFIRMATION)

# Step A candidate screen subset: 7 discovery sessions spread across the full
# date range, disclosed BEFORE any candidate computation or outcome look.
SCREEN_SUBSET = ["20250814", "20250910", "20251009", "20251117", "20260123", "20260317", "20260520"]
assert set(SCREEN_SUBSET).issubset(DISCOVERY)


def load_last_prints(tag: str) -> pd.DataFrame:
    """bip==0 (Last) trade prints for one session tag, sorted by time.
    Only reads s<tag>.parquet (+ s<tag>_rth.parquet if present) -- both
    already-permitted files for the given tag, exactly the AUCTION01 pattern."""
    raw_f = os.path.join(RAW, f"s{tag}.parquet")
    rth_f = os.path.join(RAW, f"s{tag}_rth.parquet")
    parts = [pd.read_parquet(raw_f)]
    if os.path.exists(rth_f):
        parts.append(pd.read_parquet(rth_f))
    df = pd.concat(parts, ignore_index=True)
    df["time"] = pd.to_datetime(df["time"])
    df = df.drop_duplicates(subset=["bip", "time", "price", "volume"])
    last = df[df.bip == 0][["time", "price", "volume"]].copy()
    last = last.sort_values("time").reset_index(drop=True)
    return last


def causal_running_poc(last: pd.DataFrame) -> pd.DataFrame:
    """Verbatim port of AUCTION01's causal_running_poc (02_build_poc_substrate.py).
    last: DataFrame of bip==0 rows (time, price, volume), any order.
    Returns last sorted by time with tick_id, poc_price, poc_share, vwap
    columns (all causal: use only rows up to and including the current one)."""
    last = last.sort_values("time").reset_index(drop=True)
    tick_id = np.round(last["price"].values / TICK).astype(np.int64)
    last["tick_id"] = tick_id
    last["cum_vol_at_price"] = last.groupby("tick_id")["volume"].cumsum()
    running_max = last["cum_vol_at_price"].cummax()
    is_record = last["cum_vol_at_price"].values >= running_max.values
    poc_tick = np.where(is_record, tick_id, np.nan)
    poc_tick = pd.Series(poc_tick).ffill().values
    last["poc_price"] = poc_tick * TICK
    cum_total_vol = last["volume"].cumsum()
    last["poc_share"] = running_max.values / cum_total_vol.values
    cum_pv = (last["price"] * last["volume"]).cumsum()
    last["vwap"] = cum_pv.values / cum_total_vol.values
    return last


def session_grid(last_poc: pd.DataFrame):
    """1-second DatetimeIndex spanning the session's own Last-print range,
    same construction as AUCTION01 (idx_start/idx_end from the trade data,
    not a fixed exchange-session boundary)."""
    sec = last_poc["time"].dt.floor("1s")
    idx = pd.date_range(sec.min(), sec.max(), freq="1s")
    return idx, sec


def downsample_last_per_second(last_poc: pd.DataFrame, idx, sec, cols):
    """Last-observation-per-second + ffill, identical convention to
    AUCTION01's own 1s downsample of poc_price/poc_share/vwap and to
    build_grid1s.py's downsample of `last`."""
    ps = last_poc.set_index(sec)
    g = pd.DataFrame(index=idx)
    for c in cols:
        g[c] = ps.groupby(level=0)[c].last().reindex(idx).ffill()
    return g


def per_second_sum(last: pd.DataFrame, idx, sec, value_col, fill_value=0.0):
    """Per-second SUM (not last-obs) of a column over bip==0 rows, reindexed
    onto the full 1s grid with 0 for empty seconds -- same convention as
    build_grid1s.py's `vol`/`trades` columns (groupby(level=0).sum(), fill_value=0)."""
    s = last.set_index(sec)
    out = s.groupby(level=0)[value_col].sum().reindex(idx, fill_value=fill_value)
    return out.values.astype(np.float64)


def trailing_band_cumvol(last: pd.DataFrame, idx, sec, ref_tick_1s: np.ndarray,
                          offsets=(-2, -1, 0, 1, 2)) -> np.ndarray:
    """Causal trailing-WINDOW_S volume traded within `offsets` ticks of a
    (possibly time-varying) reference tick series `ref_tick_1s`, on the 1s
    grid. `ref_tick_1s` must already be a fully-causal (no lookahead) series
    aligned to `idx` (e.g. the current price tick or the running POC tick).

    Method: build a sparse per-(second, tick_id) volume table from the raw
    trade prints, cumulative-sum it within each tick_id group (this gives,
    for each traded tick, its running total volume as of each second it
    actually traded), then for each of the 5 band offsets do TWO
    merge_asof(direction='backward', by='tick_id') queries per grid second t:
    one at t (cumulative volume of tick ref_tick_1s[t]+o as of t) and one at
    t-WINDOW_S (cumulative volume of the SAME tick ref_tick_1s[t]+o as of
    t-WINDOW_S). Subtracting gives that tick's volume traded in
    (t-WINDOW_S, t]; summing over the 5 offsets gives the trailing band sum.

    IMPORTANT: because `ref_tick_1s` is itself a time-varying (moving)
    reference, the two queries for a given row t MUST use the same tick IDs
    (ref_tick_1s[t]+o) at both the t and t-WINDOW_S timestamps -- a single
    cumulative series shifted by WINDOW_S positions (the pattern used
    elsewhere in this codebase for a FIXED quantity, e.g. AUCTION01's
    poc_migration_60s_ticks = poc_price - poc_price.shift(60)) is NOT valid
    here, because that would difference the cumulative volume of *different*
    tick bands (today's band vs. WINDOW_S-seconds-ago's band) whenever the
    reference has moved in between -- silently producing negative/unbounded
    "trailing volume" (caught in Step A screening: initial draft produced a
    share statistic ranging [-124, 246] instead of the required [0,1]).
    No information from t' > t is used at any step.
    """
    tmp = last.copy()
    tmp["sec"] = sec.values
    g2 = tmp.groupby(["tick_id", "sec"], as_index=False)["volume"].sum()
    g2 = g2.sort_values(["tick_id", "sec"])
    g2["cum_vol"] = g2.groupby("tick_id")["volume"].cumsum()
    g2 = g2[["sec", "tick_id", "cum_vol"]].sort_values("sec").reset_index(drop=True)
    g2["tick_id"] = g2["tick_id"].astype(np.int64)

    n = len(idx)
    band_now = np.zeros(n, dtype=np.float64)
    band_lag = np.zeros(n, dtype=np.float64)
    q_sec_now = pd.Series(idx)
    q_sec_lag = pd.Series(idx - pd.Timedelta(seconds=WINDOW_S))
    ref = ref_tick_1s.astype(np.int64)
    for o in offsets:
        tick_ids = ref + o
        q_now = pd.DataFrame({"sec": q_sec_now, "tick_id": tick_ids})
        merged_now = pd.merge_asof(q_now, g2, on="sec", by="tick_id", direction="backward")
        band_now += merged_now["cum_vol"].fillna(0.0).values

        q_lag = pd.DataFrame({"sec": q_sec_lag, "tick_id": tick_ids})
        merged_lag = pd.merge_asof(q_lag, g2, on="sec", by="tick_id", direction="backward")
        band_lag += merged_lag["cum_vol"].fillna(0.0).values

    trailing = band_now - band_lag
    return trailing


def build_base_session(tag: str):
    """Shared causal groundwork for one session: tick-level running POC,
    1s-grid poc_price / last / value_dist_ticks (cross-checkable against
    AUCTION01's poc_1s_full.parquet), and per-second volume/side aggregates.
    Returns a dict of aligned 1-second-grid numpy arrays + the idx DatetimeIndex.

    NOTE on the current-price reference series: the "last traded price in
    second s" is only well-defined up to a tie-break when >1 trade shares the
    same millisecond timestamp (common: ~50% of bip==0 rows in this data have
    a timestamp shared with another row). `pandas.sort_values` defaults to
    quicksort (NOT stable), so re-deriving "last-in-second" here from a
    locally-resorted bip==0-only frame picks a *different* (equally valid,
    but different) trade among exact ties than build_grid1s.py's own
    already-published `last` column does (verified: ties account for ~10% of
    1s rows in a spot check, tick-level poc_price itself matches AUCTION01
    100% since cumulative-volume tick assignment is not order-sensitive).
    To keep this feature's D_t/side classification IDENTICAL to the D_t
    already published in poc_1s_full.parquet / decision_outcomes.parquet
    (the tables this feature is meant to time-join onto), the current-price
    reference is read directly from grid1s/NQ's own canonical `last` column
    instead of being re-derived. All volume/count SUMS below (order-
    independent, verified exact match) are still computed from raw bip==0
    prints directly, per this run's own data-scope rule of not depending on
    grid1s for anything beyond this one already-built, already-canonical
    column."""
    last = load_last_prints(tag)
    poc = causal_running_poc(last)  # tick-level, sorted by time
    idx, sec = session_grid(poc)

    g_poc = downsample_last_per_second(poc, idx, sec, ["poc_price"])
    poc_price_1s = g_poc["poc_price"].values

    grid_f = os.path.join(GRID1S, f"s{tag}.parquet")
    grid_last = pd.read_parquet(grid_f, columns=["time", "last"])
    grid_last["time"] = pd.to_datetime(grid_last["time"])
    g_cur = pd.DataFrame(index=idx)
    g_cur = g_cur.join(grid_last.set_index("time"), how="left")
    g_cur["last"] = g_cur["last"].ffill().bfill()
    last_1s = g_cur["last"].values
    value_dist_ticks_1s = (last_1s - poc_price_1s) / TICK

    cur_tick_1s = np.round(last_1s / TICK).astype(np.int64)
    poc_tick_1s = np.round(poc_price_1s / TICK).astype(np.int64)

    vol_1s = per_second_sum(poc, idx, sec, "volume", fill_value=0.0)
    pv_1s = per_second_sum(
        poc.assign(pv=poc["price"] * poc["volume"]), idx, sec, "pv", fill_value=0.0
    )

    side_tick = np.sign(poc["price"].values - poc["poc_price"].values)
    pos_vol_1s = per_second_sum(poc.assign(pv_pos=np.where(side_tick > 0, poc["volume"], 0.0)),
                                 idx, sec, "pv_pos", fill_value=0.0)
    neg_vol_1s = per_second_sum(poc.assign(pv_neg=np.where(side_tick < 0, poc["volume"], 0.0)),
                                 idx, sec, "pv_neg", fill_value=0.0)

    return dict(
        tag=tag, idx=idx, sec=sec, last=poc, n=len(idx),
        last_1s=last_1s, poc_price_1s=poc_price_1s,
        value_dist_ticks_1s=value_dist_ticks_1s,
        cur_tick_1s=cur_tick_1s, poc_tick_1s=poc_tick_1s,
        vol_1s=vol_1s, pv_1s=pv_1s,
        pos_vol_1s=pos_vol_1s, neg_vol_1s=neg_vol_1s,
    )


def rolling_trailing_sum(arr: np.ndarray, window=WINDOW_S) -> np.ndarray:
    s = pd.Series(arr)
    return s.rolling(window, min_periods=1).sum().values


# ---------------------------------------------------------------- candidates
def candidate_a_excursion_side_share(base: dict) -> np.ndarray:
    """(a) excursion-side recent volume share: fraction of trailing WINDOW_S
    volume traded on the same side of the running POC as the CURRENT
    excursion sign(D_t). D_t == 0 (price sitting exactly at POC) -> NaN
    (no excursion side to agree with)."""
    pos60 = rolling_trailing_sum(base["pos_vol_1s"])
    neg60 = rolling_trailing_sum(base["neg_vol_1s"])
    tot60 = rolling_trailing_sum(base["vol_1s"])
    side_now = np.sign(base["value_dist_ticks_1s"])
    with np.errstate(invalid="ignore", divide="ignore"):
        frac = np.where(side_now > 0, pos60 / tot60,
                         np.where(side_now < 0, neg60 / tot60, np.nan))
    frac = np.where(tot60 <= 0, np.nan, frac)
    return frac


def candidate_b_near_price_acceptance(base: dict) -> np.ndarray:
    """(b) near-current-price volume acceptance: bounded share
    vol_near_current / (vol_near_current + vol_near_poc), each a trailing
    WINDOW_S sum of volume within +/-2 ticks of the respective reference
    price. A bounded SHARE (not the raw ratio literally described in the
    task) is used deliberately: the raw ratio vol_near_current/vol_near_poc
    is unbounded and blows up to +inf whenever recent POC-adjacent volume is
    (correctly, informatively) near zero during a sustained excursion --
    exactly the "accepted repricing" case the feature is meant to flag
    cleanly, not represent as inf/NaN. The bounded share preserves the same
    ordering and economic meaning (>0.5 = more recent transacting near the
    new price than the old value area) while staying well-behaved."""
    vol_near_cur = trailing_band_cumvol(base["last"], base["idx"], base["sec"], base["cur_tick_1s"])
    vol_near_poc = trailing_band_cumvol(base["last"], base["idx"], base["sec"], base["poc_tick_1s"])
    denom = vol_near_cur + vol_near_poc
    with np.errstate(invalid="ignore", divide="ignore"):
        share = np.where(denom > 0, vol_near_cur / denom, np.nan)
    return share, vol_near_cur, vol_near_poc


def candidate_d_local_value_divergence(base: dict) -> np.ndarray:
    """(d) short trailing local value center vs full-session running POC,
    sign-matched to excursion direction. Operationalization: trailing-WINDOW_S
    VWAP (not a second sliding-window mode/POC) as the local value center --
    disclosed deliberate substitution for tractability (an exact sliding-
    window *mode* running-POC requires re-scanning the full trailing volume-
    by-price histogram at every second; VWAP is the standard alternate local
    value-center estimator, is exactly causal, and is computable with a plain
    rolling sum). accept_d = sign(D_t) * (trailing_vwap_60s - poc_price_full) / TICK:
    positive means the recent local value center has moved WITH the excursion
    (recent trading has re-centered toward the new price -- acceptance);
    non-positive means it hasn't (rejection-like)."""
    pv60 = rolling_trailing_sum(base["pv_1s"])
    vol60 = rolling_trailing_sum(base["vol_1s"])
    with np.errstate(invalid="ignore", divide="ignore"):
        vwap60 = np.where(vol60 > 0, pv60 / vol60, np.nan)
    side_now = np.sign(base["value_dist_ticks_1s"])
    divergence_ticks = (vwap60 - base["poc_price_1s"]) / TICK
    accept_d = side_now * divergence_ticks
    return accept_d, vwap60
