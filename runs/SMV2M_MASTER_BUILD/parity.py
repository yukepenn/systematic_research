"""SMV2M parity reconcile: NT8 Analyzer export ledgers (v2) vs Python twin (gates per spec.yaml)."""
import sys
import numpy as np, pandas as pd

OUT = "runs/SMV2M_MASTER_BUILD/out"
TAG = "smm_v2"

# ---------- NT8 per-bar decision ledger ----------
nt = pd.read_csv(f"{OUT}/nt8/{TAG}_bars.csv", comment="#")
nt["time"] = pd.to_datetime(nt["time"])
tw = pd.read_parquet(f"{OUT}/twin_bar_ledger.parquet")
tw["time"] = pd.to_datetime(tw["time"])

m = nt.merge(tw, on="time", how="inner", suffixes=("_nt", "_tw"))
print(f"bars: nt={len(nt)} twin={len(tw)} matched={len(m)} "
      f"(nt-only {len(nt)-len(m)}, twin-only {len(tw)-len(m)})")

tpp_match = (m["Tpp_nt"] == m["Tpp_tw"]).mean()
b_match = (m["B_nt"] == m["B_tw"]).mean()
tgt_match = (m["tgt_ops_nt"] == m["tgt_ops_tw"]).mean()
print(f"Tpp match: {tpp_match:.6f}  B match: {b_match:.6f}  tgt_ops match: {tgt_match:.6f}")

mis = m[m["tgt_ops_nt"] != m["tgt_ops_tw"]]
if len(mis):
    mis[["time", "T", "Tpp_nt", "Tpp_tw", "B_nt", "B_tw", "tgt_raw", "tgt_ops_nt", "tgt_ops_tw",
         "tilt_state"]].to_csv(f"{OUT}/parity_target_mismatches.csv", index=False)
    bad_days = mis["time"].dt.date.value_counts()
    print(f"target mismatches: {len(mis)} bars across {len(bad_days)} days -> parity_target_mismatches.csv")
    print(bad_days.head(12).to_string())
    # decision-path match EXCLUDING whole-divergent (holiday-template) days
    whole_bad = set(bad_days[bad_days > 50].index)
    ok = ~m["time"].dt.date.isin(whole_bad)
    print(f"match excluding {len(whole_bad)} holiday-template days: "
          f"{(m.loc[ok, 'tgt_ops_nt'] == m.loc[ok, 'tgt_ops_tw']).mean():.6f}")

# ---------- NT8 fills -> daily PnL bucketed by twin session boundaries ----------
f = pd.read_csv(f"{OUT}/nt8/{TAG}_fills.csv", comment="#")
f["time"] = pd.to_datetime(f["time"])
buy = f["order_action"].str.contains("Buy", case=False)
signed = np.where(buy, f["qty"], -f["qty"]).astype(float)
cash = pd.Series(-(signed * f["price"].to_numpy() * 2.0) - f["commission"].to_numpy(), index=f.index)

sess_ends = tw.loc[tw["time"].dt.hour.isin([13, 17]) | (tw["time"].shift(-1).isna()), :]
# robust: use per-session last bar times from the ledger's sess_date groups
last_bar = tw.groupby("sess_date")["time"].max().sort_values()
bounds = last_bar.to_numpy()
sess_of = last_bar.index.to_numpy()
idx = np.searchsorted(bounds, f["time"].to_numpy(), side="left")
idx = np.clip(idx, 0, len(sess_of) - 1)
fs = pd.Series(cash.to_numpy()).groupby(pd.Index(sess_of[idx])).sum()
fs.index = pd.to_datetime(fs.index)
fs.index.name = "sess"

twd = pd.read_csv(f"{OUT}/twin_daily.csv", index_col=0, parse_dates=True).iloc[:, 0]
al = pd.DataFrame({"nt": fs, "tw": twd}).fillna(0.0)
al = al[(al["nt"] != 0) | (al["tw"] != 0)]
print(f"daily rows compared: {len(al)}")
corr = al["nt"].corr(al["tw"])
net_nt, net_tw = al["nt"].sum(), al["tw"].sum()
print(f"daily corr {corr:.6f} | net NT {net_nt:,.0f} vs twin {net_tw:,.0f} "
      f"| diff {net_nt-net_tw:+,.0f} ({(net_nt-net_tw)/abs(net_tw)*100:+.3f}%)")
worst = (al["nt"] - al["tw"]).abs().sort_values(ascending=False).head(10)
print("worst daily gaps:\n", worst.to_string())

# dev-only battery on the NT executable curve
nt_dev = al.loc[al.index <= "2026-05-31", "nt"]
sys.path.insert(0, "src/analytics")
from smv2_common import dd_battery
bat = dd_battery(nt_dev.index, nt_dev.values, label="NT8_EXECUTABLE_dev")
pd.DataFrame([bat]).set_index("label").to_csv(f"{OUT}/nt8_dev_battery.csv")
keep = {k: v for k, v in bat.items() if k in
        ("net", "sharpe", "maxDD_eod", "CDaR5", "worst_month", "longest_TUW_days")}
print("NT8 executable dev battery:", keep)

res = {"bars_matched": len(m), "tpp_match": tpp_match, "b_match": b_match,
       "tgt_match": tgt_match, "n_mismatch": len(mis), "daily_corr": corr,
       "net_nt": net_nt, "net_twin": net_tw, "net_diff_pct": (net_nt-net_tw)/abs(net_tw)*100,
       "gate_decision_path": tgt_match >= 0.995, "gate_corr": corr >= 0.999,
       "gate_net": abs((net_nt-net_tw)/net_tw) <= 0.005}
pd.Series(res).to_csv(f"{OUT}/parity_summary.csv")
print(pd.Series(res).to_string())
