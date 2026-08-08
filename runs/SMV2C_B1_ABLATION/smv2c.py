"""SMV2C — B1 ablation P0-P3 at equal vol (seq 324-327). BMOM basis = E2 (SMV2B verdict)."""
import sys, os
import numpy as np, pandas as pd
sys.path.insert(0, "src/analytics")
from smv2_common import dd_battery, boot_ci_mean

OUT = "runs/SMV2C_B1_ABLATION/out"; os.makedirs(OUT, exist_ok=True)
cur = pd.read_csv("runs/SMV2A_DD_RECONCILE/out/daily_curves.csv", parse_dates=["sess"])
cal = pd.DatetimeIndex(cur["sess"])
T = cur["B"].to_numpy()          # tilt-Solar daily (stored canonical)
B1 = cur["B1"].to_numpy()        # B1 nightly (exit-session attribution)
bm2 = pd.read_parquet("runs/SMV2B_BMOM_EXEC_AUDIT/out/ledger_E2_next_open.parquet")
BM = (bm2.groupby("sess")["net_c1_ticks"].sum() * 5.0)
BM.index = pd.to_datetime(BM.index)
BM = BM.reindex(cal).fillna(0.0).to_numpy()

SIG = np.std(T, ddof=1)  # common risk target: tilt-Solar dev daily sigma
def vm(x):
    return x * (SIG / np.std(x, ddof=1))

ports = {
    "P0_tilt_solar": T.copy(),
    "P1_tilt+bmom_625_375": 0.625 * T + 0.375 * vm(BM),
    "P2_tilt+b1_80_20": 0.8 * T + 0.2 * vm(B1),
    "P3_tilt+bmom+b1_532": 0.5 * T + 0.3 * vm(BM) + 0.2 * vm(B1),
}
rows = []
for k, x in ports.items():
    x = vm(x)  # rescale portfolio to common sigma (equal-vol basis)
    rows.append(dd_battery(cal, x, label=k))
    ports[k] = x
df = pd.DataFrame(rows).set_index("label")
keep = ["net", "sharpe", "sortino", "calmar", "maxDD_eod", "CDaR5", "worst_month",
        "rolling60_min", "longest_TUW_days", "pos_month_pct", "ulcer"]
df[keep].to_csv(f"{OUT}/results.csv")
print(df[keep].round(2).to_string())

# P3 vs P1 gate: block bootstrap on daily difference
d31 = ports["P3_tilt+bmom+b1_532"] - ports["P1_tilt+bmom_625_375"]
lo, hi, p = boot_ci_mean(d31)
print(f"P3-P1 daily mean {d31.mean():.1f}  CI[{lo:.1f},{hi:.1f}]  P(>0)={p:.3f}")
crit = {"sharpe": 1, "calmar": 1, "maxDD_eod": -1, "worst_month": 1, "longest_TUW_days": -1}
wins = 0
for c, sgn in crit.items():
    b = (df.loc["P3_tilt+bmom+b1_532", c] - df.loc["P1_tilt+bmom_625_375", c]) * sgn
    wins += b > 0
    print(f"  {c}: P3-P1 {'WIN' if b>0 else 'lose'} ({b:+.2f})")
print("wins:", wins, "/5  | gate: >=3 wins AND P>=0.9")
pd.DataFrame({"sess": cal, **{k: v for k, v in ports.items()}}).to_csv(f"{OUT}/curves.csv", index=False)
