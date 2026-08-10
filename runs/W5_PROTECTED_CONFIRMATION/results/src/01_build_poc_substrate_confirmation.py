"""W5_PROTECTED_CONFIRMATION Family 1 -- build: byte-identical reuse of
runs/AUCTION01_VALUE_STATE/src/02_build_poc_substrate.py's causal_running_poc() function and its
entire downstream merge/decision-point pipeline, unaltered, pointed at ONLY the 8 frozen
confirmation-pool session tags instead of the 37 discovery sessions. Per the master
preregistration: "reuses the existing causal-POC-building function/logic verbatim -- do not alter
the formula, only change which session files are read." The function body below is copied
character-for-character from 02_build_poc_substrate.py (verified by hash comparison of the
function source in the confirmation report); only the session-list source and output paths differ.
"""
import os, glob
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RAW = os.path.join(ROOT, "research", "scalping_lab", "substrate", "raw", "NQ")
GRID = os.path.join(ROOT, "research", "scalping_lab", "substrate", "grid1s", "NQ")
SECHILO = os.path.join(ROOT, "research", "scalping_lab", "substrate", "sechilo", "NQ")
OUT = os.path.join(ROOT, "runs", "W5_PROTECTED_CONFIRMATION", "results", "out")
os.makedirs(OUT, exist_ok=True)

TICK = 0.25

# ---- ONLY session-list change vs the frozen discovery script: 8 confirmation-pool dates ----
CONFIRMATION_DATES = ["20250819", "20250912", "20251028", "20251125",
                       "20260217", "20260302", "20260422", "20260512"]
assert len(CONFIRMATION_DATES) == 8
for d in CONFIRMATION_DATES:
    assert d < "20260801", f"date-firewall violation: {d} >= 2026-08-01"
sessions = sorted(CONFIRMATION_DATES)
print(f"[build-confirm] {len(sessions)} protected-pool confirmation sessions: {sessions}", flush=True)

u0 = pd.read_parquet(
    os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet"),
    columns=["time", "sess_date", "M", "position_B", "action_B"],
)
u0["sess_date"] = pd.to_datetime(u0["sess_date"]).dt.date
u0 = u0.sort_values("time")


def causal_running_poc(last):
    """VERBATIM copy of AUCTION01_VALUE_STATE/src/02_build_poc_substrate.py's function.
    last: DataFrame of bip==0 rows (time, price, volume), any order.
    Returns last sorted by time with poc_price, poc_share, vwap columns
    (all causal: use only rows up to and including the current one)."""
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


rows_all = []
for tag in sessions:
    raw_f = os.path.join(RAW, f"s{tag}.parquet")
    rth_f = os.path.join(RAW, f"s{tag}_rth.parquet")
    parts = [pd.read_parquet(raw_f)]
    if os.path.exists(rth_f):
        parts.append(pd.read_parquet(rth_f))
    df = pd.concat(parts, ignore_index=True)
    df["time"] = pd.to_datetime(df["time"])
    df = df.drop_duplicates(subset=["bip", "time", "price", "volume"])
    last = df[df.bip == 0][["time", "price", "volume"]].copy()
    poc = causal_running_poc(last)

    sec = poc["time"].dt.floor("1s")
    idx_start, idx_end = sec.min(), sec.max()
    idx = pd.date_range(idx_start, idx_end, freq="1s")
    ps = poc.set_index(sec)
    g = pd.DataFrame(index=idx)
    g["poc_price"] = ps.groupby(level=0)["poc_price"].last().reindex(idx).ffill()
    g["poc_share"] = ps.groupby(level=0)["poc_share"].last().reindex(idx).ffill()
    g["vwap"] = ps.groupby(level=0)["vwap"].last().reindex(idx).ffill()
    g = g.reset_index().rename(columns={"index": "time"})

    grid = pd.read_parquet(os.path.join(GRID, f"s{tag}.parquet"))
    grid["time"] = pd.to_datetime(grid["time"])
    sech = pd.read_parquet(os.path.join(SECHILO, f"s{tag}.parquet"))
    sech["time"] = pd.to_datetime(sech["time"])

    m = g.merge(grid[["time", "last", "mid", "sflow", "bid_upd", "ask_upd"]], on="time", how="left")
    m = m.merge(sech, on="time", how="left")
    m["mid_last"] = m["mid_last"].ffill()
    m["mid_high"] = m["mid_high"].fillna(m["mid_last"])
    m["mid_low"] = m["mid_low"].fillna(m["mid_last"])
    m = m.dropna(subset=["poc_price", "mid_last"]).reset_index(drop=True)

    sd = pd.Timestamp(f"{tag[:4]}-{tag[4:6]}-{tag[6:8]}").date()
    u0_sess = u0[u0["sess_date"] == sd]
    if len(u0_sess) == 0:
        print(f"[build-confirm] {tag}: no U0 rows for sess_date {sd}, skipping session", flush=True)
        continue
    m = pd.merge_asof(m.sort_values("time"), u0_sess[["time", "M", "position_B", "action_B"]],
                       on="time", direction="backward")

    m["value_dist_ticks"] = (m["last"] - m["poc_price"]) / TICK
    m["poc_migration_60s_ticks"] = (m["poc_price"] - m["poc_price"].shift(60)) / TICK

    m["sess_tag"] = tag
    rows_all.append(m)
    print(f"[build-confirm] {tag}: {len(m)} 1s rows, poc range [{m['poc_price'].min():.2f},{m['poc_price'].max():.2f}], "
          f"U0 match rate {(m['M'].notna().mean()):.3f}", flush=True)

full = pd.concat(rows_all, ignore_index=True)
full.to_parquet(os.path.join(OUT, "poc_1s_full_CONFIRM.parquet"), compression="zstd", index=False)
print(f"[build-confirm] full 1s table: {len(full)} rows across {full['sess_tag'].nunique()} sessions", flush=True)

# ---------------------------------------------------------------- decision points (verbatim)
full["hm"] = full["time"].dt.hour * 100 + full["time"].dt.minute
rth = (full["hm"] >= 930) & (full["hm"] < 1600)
full["liq60"] = (full["bid_upd"].fillna(0) + full["ask_upd"].fillna(0)).rolling(60, min_periods=1).sum()
liquid = full["liq60"] > 0
dec = full[rth & liquid].copy()
dec["sec_in_day"] = dec["hm"]
dec = dec.groupby("sess_tag", group_keys=False).apply(
    lambda d: d.iloc[::30]
)
dec = dec.reset_index(drop=True)
dec.to_parquet(os.path.join(OUT, "decision_points_30s_CONFIRM.parquet"), compression="zstd", index=False)
print(f"[build-confirm] decision points (RTH, liquid, 30s-sampled): {len(dec)} rows, "
      f"{dec['sess_tag'].nunique()} sessions", flush=True)
print("BUILD_CONFIRM DONE")
