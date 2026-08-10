"""W5_PROTECTED_CONFIRMATION -- build the sechilo (per-second mid_last/mid_high/mid_low) cache
for EXACTLY the 8 frozen confirmation-pool session dates. Logic is byte-identical to
research/scalping_lab/src/python/build_sechilo.py (Layer-1 supplement, union Bid+Ask event
stream -> per-second mid_last/mid_high/mid_low) -- the only change is an explicit whitelist of
session tags instead of a directory glob, so that running this script cannot touch any session
outside the 8 authorized by runs/W5_PROTECTED_CONFIRMATION/MASTER_PREREGISTRATION.md.

GOVERNANCE: only the 8 dates below are read. No other file under
research/scalping_lab/substrate/{raw,grid1s,sechilo}/NQ is opened by this script.
"""
import os
import pandas as pd, numpy as np

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RAW = os.path.join(ROOT, "research", "scalping_lab", "substrate", "raw", "NQ")
OUT = os.path.join(ROOT, "research", "scalping_lab", "substrate", "sechilo", "NQ")
os.makedirs(OUT, exist_ok=True)

CONFIRMATION_DATES = ["20250819", "20250912", "20251028", "20251125",
                       "20260217", "20260302", "20260422", "20260512"]
assert len(CONFIRMATION_DATES) == 8
for d in CONFIRMATION_DATES:
    assert d < "20260801", f"date-firewall violation: {d} >= 2026-08-01"

for tag in CONFIRMATION_DATES:
    dst = os.path.join(OUT, f"s{tag}.parquet")
    if os.path.exists(dst):
        print(f"[sechilo] {tag}: already exists, skipping (not overwritten)", flush=True)
        continue
    pq = os.path.join(RAW, f"s{tag}.parquet")
    assert os.path.exists(pq), f"missing required raw file for confirmation session {tag}"
    parts = [pd.read_parquet(pq)]
    r = os.path.join(RAW, f"s{tag}_rth.parquet")
    if os.path.exists(r):
        parts.append(pd.read_parquet(r))
    df = pd.concat(parts, ignore_index=True)
    df = df[df.bip.isin([1, 2])]
    if not len(df):
        print(tag, "L1-only, skipped", flush=True)
        continue
    df["time"] = pd.to_datetime(df["time"])
    df = df.drop_duplicates(subset=["bip", "time", "price", "volume"]).sort_values(
        "time", kind="mergesort").reset_index(drop=True)
    bid = df["price"].where(df.bip == 1).ffill()
    ask = df["price"].where(df.bip == 2).ffill()
    mid = ((bid + ask) / 2.0 / 0.25).astype(np.float64)  # ticks (matches build_sechilo.py's own
    # pre-tick-denominated convention -- AUCTION01/REPORT.md's own documented units bug note)
    ok = bid.notna() & ask.notna()
    t = df["time"][ok]; m = mid[ok]
    sec = t.dt.floor("1s")
    g = m.groupby(sec.values).agg(["last", "max", "min", "size"])
    g.columns = ["mid_last", "mid_high", "mid_low", "n_ev"]
    g.index.name = "time"
    g = g.reset_index()
    g.to_parquet(dst, compression="zstd", index=False)
    print(tag, len(g), "ok", flush=True)

print("SECHILO_CONFIRMATION DONE")
