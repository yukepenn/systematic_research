"""Layer-1: 1-second causal state grid per session. Merges base + _rth files (dedupe)."""
import glob, os
import pandas as pd, numpy as np

RAW = "research/scalping_lab/substrate/raw/NQ"
OUT = "research/scalping_lab/substrate/grid1s/NQ"
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
    df["time"] = pd.to_datetime(df["time"])
    df = df.drop_duplicates(subset=["bip", "time", "price", "volume"]).sort_values("time")
    L = df[df.bip == 0]; B = df[df.bip == 1]; A = df[df.bip == 2]
    sec = df["time"].dt.floor("1s")
    idx = pd.date_range(sec.min(), sec.max(), freq="1s")
    g = pd.DataFrame(index=idx)
    ls = L.set_index(L["time"].dt.floor("1s"))
    g["last"] = ls.groupby(level=0)["price"].last().reindex(idx).ffill()
    g["trades"] = ls.groupby(level=0)["price"].size().reindex(idx, fill_value=0)
    g["vol"] = ls.groupby(level=0)["volume"].sum().reindex(idx, fill_value=0)
    # tick-rule signed flow
    tsign = np.sign(L["price"].diff()).replace(0, np.nan).ffill().fillna(0)
    sf = (tsign * L["volume"].values)
    g["sflow"] = sf.groupby(L["time"].dt.floor("1s").values).sum().reindex(idx, fill_value=0)
    for nm, S in (("bid", B), ("ask", A)):
        ss = S.set_index(S["time"].dt.floor("1s"))
        g[nm] = ss.groupby(level=0)["price"].last().reindex(idx).ffill()
        g[nm + "_upd"] = ss.groupby(level=0)["price"].size().reindex(idx, fill_value=0)
    g["mid"] = (g["bid"] + g["ask"]) / 2
    g["spread_t"] = (g["ask"] - g["bid"]) / 0.25
    g["ret1s_t"] = g["mid"].diff() / 0.25
    g = g.reset_index().rename(columns={"index": "time"})
    g.to_parquet(dst, compression="zstd", index=False)
    print(tag, len(g), "ok", flush=True)
print("GRID1S DONE")
