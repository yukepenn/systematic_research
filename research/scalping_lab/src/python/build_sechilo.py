"""Layer-1 supplement: per-second mid_last/mid_high/mid_low from the UNION Bid+Ask
event stream (W2-1 spec). Build-once, reusable. Excludes L1-only sessions (no quotes)."""
import glob, os
import pandas as pd, numpy as np

RAW = "research/scalping_lab/substrate/raw/NQ"
OUT = "research/scalping_lab/substrate/sechilo/NQ"
os.makedirs(OUT, exist_ok=True)

base = sorted(p for p in glob.glob(os.path.join(RAW, "s*.parquet")) if "_rth" not in p)
for pq in base:
    tag = os.path.basename(pq)[:-8]
    dst = os.path.join(OUT, tag + ".parquet")
    if os.path.exists(dst): continue
    parts = [pd.read_parquet(pq)]
    r = os.path.join(RAW, tag + "_rth.parquet")
    if os.path.exists(r): parts.append(pd.read_parquet(r))
    df = pd.concat(parts, ignore_index=True)
    df = df[df.bip.isin([1, 2])]
    if not len(df):
        print(tag, "L1-only, skipped", flush=True); continue
    df["time"] = pd.to_datetime(df["time"])
    df = df.drop_duplicates(subset=["bip", "time", "price", "volume"]).sort_values(
        "time", kind="mergesort").reset_index(drop=True)
    bid = df["price"].where(df.bip == 1).ffill()
    ask = df["price"].where(df.bip == 2).ffill()
    mid = ((bid + ask) / 2.0 / 0.25).astype(np.float64)  # ticks
    ok = bid.notna() & ask.notna()
    t = df["time"][ok]; m = mid[ok]
    sec = t.dt.floor("1s")
    g = m.groupby(sec.values).agg(["last", "max", "min", "size"])
    g.columns = ["mid_last", "mid_high", "mid_low", "n_ev"]
    g.index.name = "time"
    g = g.reset_index()
    g.to_parquet(dst, compression="zstd", index=False)
    print(tag, len(g), "ok", flush=True)
print("SECHILO DONE")
