"""SMV2Q addendum — worst-period labels + master-week overlap with the Solar/B-MOM 2x2 cells.
Pure measurement; same inputs and conventions as smv2q.py."""
import os
import numpy as np
import pandas as pd

REPO = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
os.chdir(REPO)
OUT = "runs/SMV2Q_DIAGNOSTICS/out"
DEV_END = pd.Timestamp("2026-05-31")

e10 = pd.read_csv("runs/SM01_SUBSTRATE/out/e10_daily_py.csv", parse_dates=["sess"]).set_index("sess")["net"]
dual = pd.read_csv("runs/SMV2H_ONECONTRACT/out/solar_dual_htf_daily.csv", index_col=0, parse_dates=True).iloc[:, 0]
al = pd.read_csv("runs/SMV2M_MASTER_BUILD/out/parity_daily_aligned.csv", index_col=0, parse_dates=True)
reg = pd.read_csv("runs/SMV2H2_ONELOT_CONFIRM/out/regen_daily_curves.csv", index_col=0, parse_dates=True)
sm14 = reg["355_SM14_ref_oldM(3,1)_MNQ"]
bml = pd.read_parquet("runs/SMV2B_BMOM_EXEC_AUDIT/out/ledger_E2_next_open.parquet")
BM = bml.groupby("sess")["net_c1_ticks"].sum() * 5.0
BM.index = pd.to_datetime(BM.index)
CAL = dual.index
BM = BM.reindex(CAL).fillna(0.0)
nt = al.loc[al.index <= DEV_END, "nt"].copy()
nt.loc[pd.Timestamp("2023-04-05")] += nt.loc[pd.Timestamp("2023-04-06")]
nt = nt.drop(index=pd.Timestamp("2023-04-06")).sort_index()
tw = al.loc[al.index <= DEV_END, "tw"]

CURVES = {"SOLAR_E10": e10[e10.index <= DEV_END], "SOLAR_DUAL": dual, "BMOM_E2": BM,
          "MASTER_EXEC_NT": nt, "MASTER_TWIN": tw, "SM14_MNQ": sm14}

def wk(idx):
    iso = idx.isocalendar()
    return (iso["year"].astype(int) * 100 + iso["week"].astype(int)).values

rows = []
for nm, s in CURVES.items():
    w = s.groupby(wk(s.index)).sum()
    m = s.groupby(s.index.to_period("M")).sum()
    q = s.groupby(s.index.to_period("Q")).sum()
    rows.append({"curve": nm,
                 "worst_week": str(w.idxmin()), "worst_week_val": float(w.min()),
                 "worst_month": str(m.idxmin()), "worst_month_val": float(m.min()),
                 "worst_quarter": str(q.idxmin()), "worst_quarter_val": float(q.min()),
                 "n_neg_weeks": int((w < 0).sum()), "n_neg_months": int((m < 0).sum()),
                 **{f"net_2026-{mm:02d}": float(m.get(pd.Period(f"2026-{mm:02d}", "M"), np.nan))
                    for mm in range(1, 6)}})
pd.DataFrame(rows).to_csv(f"{OUT}/worst_periods.csv", index=False)

# master weekly sign vs Solar/B-MOM 2x2 cells
mw = nt.groupby(wk(nt.index)).sum()
sw = dual.groupby(wk(CAL)).sum()
bw = BM.groupby(wk(CAL)).sum()
cell = np.select([(sw > 0) & (bw > 0), (sw > 0) & (bw < 0), (sw <= 0) & (bw > 0),
                  (sw < 0) & (bw < 0), (sw > 0) & (bw == 0)],
                 ["S+B+", "S+B-", "S-B+", "S-B-", "S+B0"], default="S-B0")
df = pd.DataFrame({"master": mw.reindex(sw.index), "cell": cell})
ov = df.groupby("cell").agg(n_weeks=("master", "size"),
                            n_master_neg=("master", lambda x: int((x < 0).sum())),
                            master_mean=("master", "mean"), master_sum=("master", "sum"))
ov["share_of_master_neg_weeks"] = ov["n_master_neg"] / int((df["master"] < 0).sum())
ov.to_csv(f"{OUT}/master_week_cell_overlap.csv")
print(pd.DataFrame(rows)[["curve", "worst_week", "worst_month", "worst_quarter"]].to_string(index=False))
print(ov.round(3).to_string())
print("master neg weeks total:", int((df['master'] < 0).sum()), "of", len(df))
