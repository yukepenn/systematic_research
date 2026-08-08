"""ARCHIVE_ONLY converter: runs/EXPORT01/out/es_*_ticks.csv -> substrate/raw/ES/*.parquet
(zstd) + MANIFEST append. Header-aware (exporter writes a header line; appended runs may
repeat it). No feature computation, no analysis — archival per Amendment 4 par.20."""
import glob, os
import pandas as pd

OUT = "research/scalping_lab/substrate/raw/ES"
MAN = os.path.join(OUT, "MANIFEST.csv")
os.makedirs(OUT, exist_ok=True)
seen = set()
if os.path.exists(MAN):
    seen = set(pd.read_csv(MAN)["session"])
rows = []
for src in sorted(glob.glob("research/scalping_lab/runs/EXPORT01/out/es_*_ticks.csv")):
    tag = os.path.basename(src)[:-10]
    if tag in seen:
        continue
    df = pd.read_csv(src, dtype=str)
    df = df[df["bip"] != "bip"]
    df = df.astype({"bip": "int8", "price": "float64", "volume": "float64"})
    df.to_parquet(os.path.join(OUT, tag + ".parquet"), compression="zstd", index=False)
    rows.append(dict(session=tag, rows=len(df),
        trades=int((df.bip == 0).sum()), bid_ev=int((df.bip == 1).sum()),
        ask_ev=int((df.bip == 2).sum()), t_min=df.time.min(), t_max=df.time.max(),
        capped="Y" if len(df) >= 12_000_000 else "N", src=os.path.basename(src)))
    os.remove(src)
    print(tag, len(df), "ok", flush=True)
if rows:
    m = pd.concat([pd.read_csv(MAN), pd.DataFrame(rows)]) if os.path.exists(MAN) else pd.DataFrame(rows)
    m.to_csv(MAN, index=False)
print("ES CONVERT DONE", len(rows), "new")
