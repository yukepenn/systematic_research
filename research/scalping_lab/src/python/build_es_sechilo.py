"""Layer-1 supplement for ES: per-second mid_last/mid_high/mid_low from the UNION
Bid+Ask event stream (same construction as build_sechilo.py; W6/FSS-10 prerequisite).
ES ticks = 0.25 pt; mid stored in ES ticks."""
import glob, os
import pandas as pd, numpy as np

RAW = "research/scalping_lab/substrate/raw/ES"
OUT = "research/scalping_lab/substrate/sechilo/ES"
os.makedirs(OUT, exist_ok=True)

for pq in sorted(glob.glob(os.path.join(RAW, "es_s*.parquet"))):
    tag = os.path.basename(pq)[:-8]
    dst = os.path.join(OUT, tag + ".parquet")
    if os.path.exists(dst): continue
    df = pd.read_parquet(pq)
    df = df[df.bip.isin([1, 2])]
    if not len(df):
        print(tag, "L1-only, skipped", flush=True); continue
    df["time"] = pd.to_datetime(df["time"])
    df = df.drop_duplicates(subset=["bip", "time", "price", "volume"]).sort_values(
        "time", kind="mergesort").reset_index(drop=True)
    bid = df["price"].where(df.bip == 1).ffill()
    ask = df["price"].where(df.bip == 2).ffill()
    mid = ((bid + ask) / 2.0 / 0.25).astype(np.float64)
    ok = bid.notna() & ask.notna()
    t = df["time"][ok]; m = mid[ok]
    g = m.groupby(t.dt.floor("1s").values).agg(["last", "max", "min", "size"])
    g.columns = ["mid_last", "mid_high", "mid_low", "n_ev"]
    g.index.name = "time"
    g.reset_index().to_parquet(dst, compression="zstd", index=False)
    print(tag, len(g), "ok", flush=True)
print("ES SECHILO DONE")
