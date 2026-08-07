"""E10MASTER_V2 vs V1 comparison per runs/E10MASTER_V2/spec.yaml gates G1-G4.

Both fill ledgers aggregated identically: session label = (fill_time + 6:59:59).date
(18:00->17:00 ET sessions; both versions are flat at every session close, so realized
session P&L = session MTM). MNQ multiplier $2/point. Net = 2*sum(signed px*qty) - commission.
Run from repo root: python runs/E10MASTER_V2/compare.py
"""
import pandas as pd, numpy as np

def daily(path):
    df = pd.read_csv(path, comment="#")
    t = pd.to_datetime(df["time"])
    df["sess"] = (t + pd.Timedelta(hours=6, minutes=59, seconds=59)).dt.date
    sign = df["order_action"].map(lambda a: 1.0 if "Sell" in str(a) else -1.0)
    df["cash"] = sign * df["price"] * df["qty"] * 2.0
    g = df.groupby("sess").agg(cash=("cash", "sum"), comm=("commission", "sum"),
                               qty=("qty", "sum"), n=("cash", "size"))
    g["net"] = g["cash"] - g["comm"]
    return df, g

def stats(g, label):
    eq = g["net"].cumsum()
    dd = (eq - eq.cummax()).min()
    sharpe = g["net"].mean() / g["net"].std() * np.sqrt(252)
    print(f"{label}: net ${g['net'].sum():,.2f} | execs {int(g['n'].sum()):,} | qty {int(g['qty'].sum()):,} "
          f"| comm ${g['comm'].sum():,.2f} | maxDD ${dd:,.2f} | daily Sharpe {sharpe:.3f} "
          f"| worst day ${g['net'].min():,.2f} | days {len(g)}")
    return eq, dd, sharpe

f1, g1 = daily("runs/E10MASTER_V1/out/e10m_v1_fills.csv")
f2, g2 = daily("runs/E10MASTER_V2/out/e10m_v2_fills.csv")
_, dd1, sh1 = stats(g1, "v1")
_, dd2, sh2 = stats(g2, "v2")

j = g1[["net"]].join(g2[["net"]], how="outer", lsuffix="_v1", rsuffix="_v2").fillna(0.0)
corr = j["net_v1"].corr(j["net_v2"])
delta = g2["net"].sum() - g1["net"].sum()
pct = 100.0 * delta / g1["net"].sum()
print(f"\nG1 daily corr: {corr:.6f}")
print(f"G2 net delta: ${delta:,.2f} ({pct:+.2f}% of v1) — gate [-8%, 0%]")
print(f"G3 maxDD v1 ${dd1:,.0f} vs v2 ${dd2:,.0f} ({100*(dd2-dd1)/abs(dd1):+.2f}%); "
      f"worst day v1 ${g1['net'].min():,.0f} vs v2 ${g2['net'].min():,.0f}")
top10 = g1["net"].nlargest(10)
ret = j.loc[j.index.isin(top10.index), "net_v2"].sum() / top10.sum()
print(f"G4 top-10 v1 days retention: {100*ret:.2f}% — gate >= 90%")

# late-session fills sanity: v2 must have no entries with position after 16:45 ET
t2 = pd.to_datetime(f2["time"]); hm = t2.dt.hour*100 + t2.dt.minute
late_fills = f2[(hm > 1645) & (hm <= 1700)]
print(f"\nv2 fills with 16:45<t<=17:00: {len(late_fills)} (expect 0)")
w = f2[(hm > 1636) & (hm <= 1645)]
print(f"v2 flatten-window fills 16:36<t<=16:45: {len(w)} (exits at ~16:42 open expected)")
j.to_csv("runs/E10MASTER_V2/out/daily_v1_v2.csv")
