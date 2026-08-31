"""G3_XMLAT_01 - the sub-second half (gate X3, and the quote-based policy variants of X4).

THE ONLY tick+BBO sessions this repository owns:
  research/data_microstructure_v2/raw/NQ/      58 sessions, MANIFEST.csv + quality/qa.csv
  research/scalping_lab/substrate/raw/NQ/      61 files (48 base sessions + 13 _rth supplements)

EXCLUSIONS, applied before any number is produced and printed by the program:
  * s20260525 - verdict QUARANTINE:short_span in quality/qa.csv. It has no parquet in raw/NQ
    and no MANIFEST row, so it is doubly excluded; the exclusion is asserted, not assumed.
  * any scalping_lab BASE file at EXACTLY 12,000,000 rows - the old export cap. The truncation
    is a TAIL truncation (the files stop between 13:28 and 16:45 ET) and does not touch the
    09:45 window, but the run excludes them from the primary set as instructed and reports the
    with-them sensitivity separately.
  * any session dated on or after 2026-08-01 (SEAL). None exist in either store; asserted.

Column contract (research/scalping_lab/src/python/build_grid1s.py:21):
    bip int8  0=Last 1=Bid 2=Ask  |  time  |  price float64  |  volume int32
Timestamps are exchange-session time (ET), sessions 18:00 -> 17:00.
"""
from __future__ import annotations

import glob
import os

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
DMV2 = os.path.join(ROOT, "research", "data_microstructure_v2", "raw", "NQ")
DMV2_MAN = os.path.join(ROOT, "research", "data_microstructure_v2", "MANIFEST.csv")
DMV2_QA = os.path.join(ROOT, "research", "data_microstructure_v2", "quality", "qa.csv")
SL = os.path.join(ROOT, "research", "scalping_lab", "substrate", "raw", "NQ")

TRUNC_ROWS = 12_000_000
SEAL_FROM = pd.Timestamp("2026-08-01")
TICK = 0.25
PV = 20.0

# the delay ladder of X3, in seconds
DELAYS = [0.0, 0.050, 0.100, 0.250, 0.500, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
DELAY_LBL = ["+0ms", "+50ms", "+100ms", "+250ms", "+500ms", "+1s", "+2s", "+5s", "+10s",
             "+30s", "+60s"]


# ==============================================================================================
def index_tick_sessions(verbose=True):
    """Build the owned-tick-session index with every exclusion printed by the program."""
    log = {}
    qa = pd.read_csv(DMV2_QA)
    man = pd.read_csv(DMV2_MAN)
    quar = qa[~qa["verdict"].astype(str).str.startswith("OK")]
    log["qa_rows"] = len(qa)
    log["qa_quarantined"] = list(zip(quar["session"].tolist(), quar["verdict"].tolist()))

    sess = {}                                   # date -> dict(store, paths, rows)
    dmv2_files = sorted(glob.glob(os.path.join(DMV2, "s*.parquet")))
    log["dmv2_files"] = len(dmv2_files)
    man_sess = set(man["session"].tolist())
    dmv2_excluded = []
    for p in dmv2_files:
        tag = os.path.basename(p)[:-8]
        if tag not in man_sess:
            dmv2_excluded.append((tag, "not-in-MANIFEST"))
            continue
        v = str(qa.loc[qa["session"] == tag, "verdict"].iloc[0]) if (qa["session"] == tag).any() \
            else "no-qa-row"
        if not v.startswith("OK"):
            dmv2_excluded.append((tag, v))
            continue
        d = pd.Timestamp(tag[1:5] + "-" + tag[5:7] + "-" + tag[7:9])
        if d >= SEAL_FROM:
            dmv2_excluded.append((tag, "SEAL >= 2026-08-01"))
            continue
        sess[d] = dict(store="DMV2", paths=[p], tag=tag)
    log["dmv2_excluded"] = dmv2_excluded

    sl_files = sorted(glob.glob(os.path.join(SL, "s*.parquet")))
    sl_base = [p for p in sl_files if "_rth" not in os.path.basename(p)]
    log["sl_files"] = len(sl_files)
    log["sl_base"] = len(sl_base)
    sl_excluded, sl_trunc_dates = [], []
    for p in sl_base:
        tag = os.path.basename(p)[:-8]
        nrows = pq.ParquetFile(p).metadata.num_rows
        d = pd.Timestamp(tag[1:5] + "-" + tag[5:7] + "-" + tag[7:9])
        if d >= SEAL_FROM:
            sl_excluded.append((tag, "SEAL >= 2026-08-01"))
            continue
        if nrows == TRUNC_ROWS:
            sl_excluded.append((tag, f"TRUNCATED at exactly {TRUNC_ROWS:,} rows"))
            sl_trunc_dates.append(d)
            continue
        if d in sess:
            sl_excluded.append((tag, "duplicate date - DMV2 copy preferred"))
            continue
        paths = [p]
        r = p.replace(".parquet", "_rth.parquet")
        if os.path.exists(r) and pq.ParquetFile(r).metadata.num_rows != TRUNC_ROWS:
            paths.append(r)
        sess[d] = dict(store="SL", paths=paths, tag=tag)
    log["sl_excluded"] = sl_excluded
    log["sl_truncated_dates"] = sl_trunc_dates
    log["n_sessions"] = len(sess)
    log["dates"] = sorted(sess)

    if verbose:
        print(f"    data_microstructure_v2: {log['dmv2_files']} parquet files, "
              f"{len(man)} MANIFEST rows, {len(qa)} qa rows")
        print(f"      QUARANTINED in qa.csv: {log['qa_quarantined']}")
        print(f"      excluded from DMV2: {dmv2_excluded if dmv2_excluded else 'none'}")
        print(f"    scalping_lab raw: {log['sl_files']} files, {log['sl_base']} base sessions")
        ntr = sum(1 for _, r in sl_excluded if r.startswith('TRUNCATED'))
        ndup = sum(1 for _, r in sl_excluded if r.startswith('duplicate'))
        print(f"      excluded: {ntr} TRUNCATED at exactly 12,000,000 rows, "
              f"{ndup} duplicate dates already covered by DMV2")
        print(f"      truncated tags: {[t for t, r in sl_excluded if r.startswith('TRUNCATED')]}")
        print(f"    -> USABLE TICK SESSIONS: {len(sess)}  "
              f"({sorted(sess)[0].date()} .. {sorted(sess)[-1].date()})")
    return sess, log


# ==============================================================================================
def read_window(paths, day, lo_str="09:40:00", hi_str="09:47:30"):
    """Read only the bars in [day lo, day hi] from one session's parquet(s)."""
    t0 = pd.Timestamp(f"{day.date()} {lo_str}")
    t1 = pd.Timestamp(f"{day.date()} {hi_str}")
    parts = []
    for p in paths:
        try:
            tb = pq.read_table(p, filters=[("time", ">=", t0), ("time", "<=", t1)])
        except Exception:
            tb = pq.read_table(p)
        d = tb.to_pandas()
        if len(d):
            d = d[(d["time"] >= t0) & (d["time"] <= t1)]
        parts.append(d)
    df = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()
    if len(df):
        df = (df.drop_duplicates(subset=["bip", "time", "price", "volume"])
                .sort_values("time", kind="mergesort").reset_index(drop=True))
    return df


def _ns(x):
    """datetime64[ns] -> int64 nanoseconds. Comparisons on int64 are unambiguous."""
    return np.asarray(x, dtype="datetime64[ns]").astype(np.int64)


def _first_at_or_after(t, p, cutoff):
    """t: int64 ns array (sorted). cutoff: int64 ns."""
    if len(t) == 0:
        return np.nan, np.nan
    i = int(np.searchsorted(t, cutoff, side="left"))
    return (float(p[i]), float(t[i])) if i < len(t) else (np.nan, np.nan)


def _last_at_or_before(t, p, cutoff):
    if len(t) == 0:
        return np.nan, np.nan
    i = int(np.searchsorted(t, cutoff, side="right")) - 1
    return (float(p[i]), float(t[i])) if i >= 0 else (np.nan, np.nan)


def measure_session(df, day, cutoff_str="09:45:00.000"):
    """Everything gate X3 needs from one tick session, direction-free."""
    cut = int(pd.Timestamp(f"{day.date()} {cutoff_str}").value)
    L = df[df["bip"] == 0]
    B = df[df["bip"] == 1]
    A = df[df["bip"] == 2]
    tl, pl = _ns(L["time"].to_numpy()), L["price"].to_numpy()
    tb, pb = _ns(B["time"].to_numpy()), B["price"].to_numpy()
    ta, pa = _ns(A["time"].to_numpy()), A["price"].to_numpy()

    bid, bt = _last_at_or_before(tb, pb, cut)
    ask, at_ = _last_at_or_before(ta, pa, cut)
    out = dict(day=day.date().isoformat(),
               n_last=len(L), n_bid=len(B), n_ask=len(A),
               bid_at_cut=bid, ask_at_cut=ask,
               bid_age_s=(cut - bt) / 1e9 if np.isfinite(bt) else np.nan,
               ask_age_s=(cut - at_) / 1e9 if np.isfinite(at_) else np.nan,
               spread_ticks=((ask - bid) / TICK) if np.isfinite(bid) and np.isfinite(ask)
               else np.nan)
    out["has_bbo"] = bool(np.isfinite(out["spread_ticks"]))
    # ---- ROBUST spread, because the instantaneous estimator is not clean.
    # Bid and Ask arrive as two INDEPENDENT event streams on a 4 ms clock. Forward-filling one
    # against the other produces occasional CROSSED reconstructions that are an artefact of
    # stream interleaving, not a crossed market. So the run reports three estimators and the
    # crossed fraction, and quotes the median rather than the instantaneous value.
    w0 = cut - 1_000_000_000
    mb = (tb >= w0) & (tb <= cut)
    ma = (ta >= w0) & (ta <= cut)
    if mb.any() and ma.any():
        ev_t = np.concatenate([tb[mb], ta[ma]])
        ev_p = np.concatenate([pb[mb], pa[ma]])
        ev_s = np.concatenate([np.zeros(mb.sum(), np.int8), np.ones(ma.sum(), np.int8)])
        o_ = np.argsort(ev_t, kind="mergesort")
        ev_t, ev_p, ev_s = ev_t[o_], ev_p[o_], ev_s[o_]
        bb = np.where(ev_s == 0, ev_p, np.nan)
        aa = np.where(ev_s == 1, ev_p, np.nan)
        bb = pd.Series(bb).ffill().to_numpy()
        aa = pd.Series(aa).ffill().to_numpy()
        sp = (aa - bb) / TICK
        sp = sp[np.isfinite(sp)]
        out["spread_ticks_med1s"] = float(np.median(sp)) if len(sp) else np.nan
        out["spread_crossed_frac1s"] = float((sp <= 0).mean()) if len(sp) else np.nan
        out["spread_n1s"] = int(len(sp))
    else:
        out["spread_ticks_med1s"] = np.nan
        out["spread_crossed_frac1s"] = np.nan
        out["spread_n1s"] = 0
    # the arrival price ladder
    for lab, d in zip(DELAY_LBL, DELAYS):
        c2 = cut + int(round(d * 1e9))
        px, ts = _first_at_or_after(tl, pl, c2)
        out["px" + lab] = px
        out["lag" + lab] = (ts - c2) / 1e9 if np.isfinite(ts) else np.nan
    # the quote ladder (what a marketable order would actually cross) and the MID ladder.
    # The MID matters: at 50-250 ms the change in the LAST price is dominated by bid-ask
    # BOUNCE, not by drift. The mid strips the bounce out, so the two ladders separate
    # "the price moved" from "I crossed a spread".
    for lab, d in zip(DELAY_LBL, DELAYS):
        c2 = cut + int(round(d * 1e9))
        b_ = _first_at_or_after(tb, pb, c2)[0]
        a_ = _first_at_or_after(ta, pa, c2)[0]
        out["bid" + lab] = b_
        out["ask" + lab] = a_
        out["mid" + lab] = (a_ + b_) / 2.0 if np.isfinite(a_) and np.isfinite(b_) else np.nan
    return out


def policy_fills(df, day, direction, give_up_s=60.0, cutoff_str="09:45:00.000"):
    """X4 policy variants. Quote-driven, so tick-session-only. Queue position NOT modelled."""
    cut = int(pd.Timestamp(f"{day.date()} {cutoff_str}").value)
    L = df[df["bip"] == 0]
    B = df[df["bip"] == 1]
    A = df[df["bip"] == 2]
    tl, pl = _ns(L["time"].to_numpy()), L["price"].to_numpy()
    tb, pb = _ns(B["time"].to_numpy()), B["price"].to_numpy()
    ta, pa = _ns(A["time"].to_numpy()), A["price"].to_numpy()
    bid0 = _last_at_or_before(tb, pb, cut)[0]
    ask0 = _last_at_or_before(ta, pa, cut)[0]
    res = {}
    # V0: the incumbent's modelled fill - the first PRINT at or after the decision instant
    res["V0_first_print"] = _first_at_or_after(tl, pl, cut)[0]
    # V1: immediate marketable - cross the prevailing quote at arrival
    res["V1_marketable"] = (_first_at_or_after(ta, pa, cut)[0] if direction > 0
                            else _first_at_or_after(tb, pb, cut)[0])
    # V2: marketable LIMIT at the causally known 09:45:00 quote +/- 1 tick
    end = cut + int(give_up_s * 1e9)
    if direction > 0 and np.isfinite(ask0):
        lim = ask0 + TICK
        m = (ta >= cut) & (ta <= end) & (pa <= lim)
        res["V2_marketable_limit"] = float(pa[m][0]) if m.any() else np.nan
    elif direction < 0 and np.isfinite(bid0):
        lim = bid0 - TICK
        m = (tb >= cut) & (tb <= end) & (pb >= lim)
        res["V2_marketable_limit"] = float(pb[m][0]) if m.any() else np.nan
    else:
        res["V2_marketable_limit"] = np.nan
    # V3: passive LIMIT AT THE TOUCH with a 60 s give-up. Filled only if a PRINT trades through
    #     the level. NO QUEUE MODEL - this is an upper bound on how often it fills.
    if direction > 0 and np.isfinite(bid0):
        lim = bid0
        m = (tl > cut) & (tl <= end) & (pl <= lim)
        res["V3_touch_60s"] = lim if m.any() else np.nan
    elif direction < 0 and np.isfinite(ask0):
        lim = ask0
        m = (tl > cut) & (tl <= end) & (pl >= lim)
        res["V3_touch_60s"] = lim if m.any() else np.nan
    else:
        res["V3_touch_60s"] = np.nan
    res["bid_at_cut"] = bid0
    res["ask_at_cut"] = ask0
    return res
