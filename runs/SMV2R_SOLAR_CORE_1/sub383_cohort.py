"""SMV2R sub_383 — cohort ablation (seq 383). FAST=vm{6,8,10,12}, MID=vm{14..22},
SLOW=vm{24..30}. Arms: ALL (incumbent 13), no-FAST (9), no-SLOW (9), MID-only (5).
Target = round(10 * mean pending over arm members), clamp +-10, same E10 executor.
REMOVABLE-CANDIDATE rule (frozen): removal improves Sharpe AND CDaR AND retains
>=95% of top-10-day sum.
"""
import sys, os, json, datetime as dt
import numpy as np, pandas as pd

RUN = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\runs\SMV2R_SOLAR_CORE_1"
sys.path.insert(0, RUN)
from common_exec import sm, e10_exec, metric_row, ROOT

OUT = os.path.join(RUN, "out")
DEV_END = dt.date(2026, 5, 31)

bars = sm.load_bars_3m(os.path.join(ROOT, "runs", "AUDIT03_BARS", "nq_3m_2022_2026.csv"))
bars = bars[bars["sess_date"] <= DEV_END].reset_index(drop=True)

cache = np.load(os.path.join(OUT, "cache_incumbent.npz"))
pend = cache["pend"]  # (n_bars, 13) verified == substrate p6..p30 100%
VMS = np.array(sm.VMS)

ARMS = {
    "ALL": VMS.tolist(),
    "no-FAST": [v for v in VMS if v >= 14],
    "no-SLOW": [v for v in VMS if v <= 22],
    "MID-only": [v for v in VMS if 14 <= v <= 22],
}

rows = []; dailies = {}
for arm, vms in ARMS.items():
    idx = [sm.VMS.index(v) for v in vms]
    tgt = sm.e10_target(pend[:, idx])
    daily, bar_pos, bar_pnl = e10_exec(bars, tgt)
    dailies[arm] = daily
    r = metric_row(arm, daily)
    r["members"] = "/".join(map(str, vms))
    r["n_members"] = len(vms)
    r["tgt_change_bars_pct"] = float((np.diff(tgt) != 0).mean() * 100)
    rows.append(r)
    print(arm, f"net={r['net']:.0f} sharpe={r['sharpe']:.3f} CDaR5={r['CDaR5']:.0f}", flush=True)

df = pd.DataFrame(rows)

# right-tail retention measured on the SAME calendar days: PnL of arm on the
# incumbent's top-10 days / incumbent top-10 sum, plus own-top-10 ratio
base = dailies["ALL"].set_index("sess")["net"]
top10_days = base.nlargest(10)
ret = {}
for arm in ARMS:
    d = dailies[arm].set_index("sess")["net"]
    on_base_days = float(d.reindex(top10_days.index).fillna(0).sum())
    ret[arm] = on_base_days
df["pnl_on_ALL_top10_days"] = df["arm"].map(ret)
df["retention_ALL_top10"] = df["pnl_on_ALL_top10_days"] / ret["ALL"]

# per-cohort marginal stats (ALL minus arm-without-cohort)
allr = df[df.arm == "ALL"].iloc[0]
marg = []
for cohort, arm in (("FAST", "no-FAST"), ("SLOW", "no-SLOW")):
    a = df[df.arm == arm].iloc[0]
    marg.append({
        "cohort": cohort, "removal_arm": arm,
        "d_net": float(a.net - allr.net),
        "d_sharpe": float(a.sharpe - allr.sharpe),
        "d_CDaR5": float(a.CDaR5 - allr.CDaR5),
        "d_maxDD": float(a.max_dd - allr.max_dd),
        "d_es5": float(a.es5_daily - allr.es5_daily),
        "d_contracts_per_day": float(a.avg_contracts_per_day - allr.avg_contracts_per_day),
        "retention_ALL_top10": float(a.retention_ALL_top10),
        "removable_candidate": bool(
            (a.sharpe > allr.sharpe) and (a.CDaR5 < allr.CDaR5)
            and (a.retention_ALL_top10 >= 0.95)),
    })
mdf = pd.DataFrame(marg)

df.to_csv(os.path.join(OUT, "cohort_ablation.csv"), index=False)
mdf.to_csv(os.path.join(OUT, "cohort_marginal.csv"), index=False)
for arm, d in dailies.items():
    d.to_csv(os.path.join(OUT, f"daily_cohort_{arm.replace('-','_')}.csv"), index=False)
print(df[["arm","net","sharpe","max_dd","CDaR5","es5_daily","top10_day_sum",
          "retention_ALL_top10","avg_contracts_per_day"]].to_string(index=False))
print(mdf.to_string(index=False))
