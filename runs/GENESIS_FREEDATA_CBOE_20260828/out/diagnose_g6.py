"""Post-gate diagnostic for G6 (%Tuesday sub-clause) — as executed 2026-08-28.

Appends a labeled DIAGNOSTIC section to out/gate_table.txt. Does NOT alter any
verdict: G6 remains FAIL as coded in certify.py. All values printed are certified
pre-seal (< 2026-08-01) rows read back from certified/, never from raw/.
"""
import pandas as pd
from pathlib import Path

RUN = Path(r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\runs\GENESIS_FREEDATA_CBOE_20260828")
cot = pd.read_parquet(RUN / "certified" / "cot_tff_futures_only.parquet")
L = []


def log(s):
    print(s)
    L.append(s)


log("")
log("=" * 100)
log("POST-GATE DIAGNOSTIC (printed by diagnose_g6.py; does NOT alter any verdict above — G6 remains FAIL as coded)")
log("=" * 100)
d = cot[["report_date"]].drop_duplicates()
d["wd"] = d["report_date"].dt.day_name()
log(f"distinct certified report dates: {len(d)}; weekday counts: {d['wd'].value_counts().to_dict()}")
nt = sorted(d.loc[d["wd"] != "Tuesday", "report_date"].dt.strftime("%Y-%m-%d (%a)"))
log(f"non-Tuesday as-of dates (ALL, certified pre-seal): {nt}")
rows = cot.copy()
rows["wd"] = rows["report_date"].dt.day_name()
log(f"row-level weekday shares: {(100 * rows['wd'].value_counts(normalize=True)).round(2).to_dict()}")
vix = cot[cot["Market_and_Exchange_Names"].str.upper().str.contains("VIX")]
tus = pd.date_range(vix["report_date"].min(), vix["report_date"].max(), freq="W-TUE")
miss = tus.difference(pd.DatetimeIndex(vix["report_date"].unique()))
by_year = pd.Series(miss.year).value_counts().sort_index().to_dict()
log(f"VIX-report missing Tuesdays by year (n={len(miss)}): {by_year}")
mon_cover = sum((t - pd.Timedelta(days=1)) in set(vix["report_date"]) for t in miss)
log(f"of those, {mon_cover} have a Monday as-of report in the same week (holiday-shift), {len(miss) - mon_cover} truly absent weeks")
with open(RUN / "out" / "gate_table.txt", "a", encoding="utf-8") as f:
    f.write("\n".join(L) + "\n")
