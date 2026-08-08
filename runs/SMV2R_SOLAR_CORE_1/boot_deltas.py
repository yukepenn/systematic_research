"""SMV2R — house paired block bootstrap (block=5, B=10000, seed=20260808) on daily
net deltas for the 382/383 headline comparisons (supporting evidence only; the frozen
verdict rules are deterministic)."""
import sys, os
import numpy as np, pandas as pd

RUN = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\runs\SMV2R_SOLAR_CORE_1"
sys.path.insert(0, RUN)
from common_exec import ROOT
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
from sm_metrics import block_bootstrap_delta

OUT = os.path.join(RUN, "out")

def load(f):
    d = pd.read_csv(os.path.join(OUT, f))
    d["sess"] = pd.to_datetime(d["sess"])
    return d.set_index("sess")["net"]

base = load("daily_volmem_N460.csv")
pairs = {
    "N230_minus_N460": load("daily_volmem_N230.csv"),
    "N920_minus_N460": load("daily_volmem_N920.csv"),
    "noFAST_minus_ALL": load("daily_cohort_no_FAST.csv"),
    "noSLOW_minus_ALL": load("daily_cohort_no_SLOW.csv"),
    "MIDonly_minus_ALL": load("daily_cohort_MID_only.csv"),
}
rows = []
for name, s in pairs.items():
    assert len(s) == len(base) and (s.index == base.index).all()
    r = block_bootstrap_delta(s.to_numpy(), base.to_numpy(), block=5,
                              n_boot=10_000, seed=20260808)
    r["comparison"] = name
    rows.append(r)
df = pd.DataFrame(rows)[["comparison", "delta", "p_leq_0", "ci_lo", "ci_hi"]]
df.to_csv(os.path.join(OUT, "boot_deltas.csv"), index=False)
print(df.to_string(index=False))
