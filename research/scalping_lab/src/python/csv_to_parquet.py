import sys, os, glob
import pandas as pd
B = r"research/scalping_lab/runs/EXPORT01/out"
R = r"research/scalping_lab/substrate/raw/NQ"
os.makedirs(R, exist_ok=True)
man = r"research/scalping_lab/substrate/MANIFEST.csv"
if not os.path.exists(man):
    with open(man, "w") as f: f.write("session,rows,trades,bid_ev,ask_ev,t_min,t_max,capped,src\n")
for csv in sorted(glob.glob(os.path.join(B, "s*_ticks.csv"))):
    tag = os.path.basename(csv).replace("_ticks.csv","")
    out = os.path.join(R, tag + ".parquet")
    if os.path.exists(out): continue
    df = pd.read_csv(csv, dtype={"bip":"int8","price":"float64","volume":"int32"}, parse_dates=["time"])
    n = len(df)
    df.to_parquet(out, compression="zstd", index=False)
    chk = pd.read_parquet(out, columns=["bip"])
    assert len(chk) == n, tag
    c = df["bip"].value_counts()
    with open(man, "a") as f:
        f.write(f"{tag},{n},{c.get(0,0)},{c.get(1,0)},{c.get(2,0)},{df['time'].min()},{df['time'].max()},{int(n>=12000000)},SWScalpTickExport_v1\n")
    os.remove(csv)
    print(tag, n, "ok")
print("BATCH DONE")
