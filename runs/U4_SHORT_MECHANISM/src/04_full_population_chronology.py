"""
U4 step 4 -- full-population (not just top/bottom-20) checkpoint trace + year-by-year
chronology (directive point 4), for the strongest checkpoint candidates identified in step 2/3
(giveback_ratio at plus15 / plus30 / first_mdecay). Gives a population-level Spearman
correlation (same convention as P0/R4/R5), not just an extreme-decile comparison, and reports
each year (2022/2023/2024/2025/2026-canonical-Jan-May) SEPARATELY plus the 2026 Jun-Jul
health-only extension as its own observational row -- never blended into the chronology
verdict, per directive/standing rigor.
"""
import json
import numpy as np
import pandas as pd
from scipy import stats as sps

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = ROOT + r"\runs\U4_SHORT_MECHANISM\out"

bars = pd.read_parquet(OUT + r"\u4_bars_with_features.parquet").set_index("t_idx", drop=False)
blocks_B = pd.read_parquet(OUT + r"\blocks_B_short.parquet")
blocks_A = pd.read_parquet(OUT + r"\blocks_A_short.parquet")


def checkpoint_giveback(bars, entry_t_idx, n_bars, position_sign, giveback_col, offset):
    target = entry_t_idx + offset
    last = entry_t_idx + n_bars - 1
    if target > last:
        return np.nan
    return float(bars.at[target, giveback_col])


def checkpoint_giveback_first_mdecay(bars, entry_t_idx, n_bars, position_sign, giveback_col):
    last = entry_t_idx + n_bars - 1
    for t in range(entry_t_idx + 1, last + 1):
        if bars.at[t, "M_change"] * position_sign < 0:
            return float(bars.at[t, giveback_col]), int(t - entry_t_idx + 1)
    return np.nan, np.nan


def build_full_trace(blocks_df, giveback_col):
    gb15, gb30, gb_mdecay, age_mdecay = [], [], [], []
    for _, b in blocks_df.iterrows():
        et, nb = int(b["entry_t_idx"]), int(b["n_bars"])
        gb15.append(checkpoint_giveback(bars, et, nb, -1, giveback_col, 5))
        gb30.append(checkpoint_giveback(bars, et, nb, -1, giveback_col, 10))
        g, a = checkpoint_giveback_first_mdecay(bars, et, nb, -1, giveback_col)
        gb_mdecay.append(g)
        age_mdecay.append(a)
    out = blocks_df.copy()
    out["giveback_at_plus15"] = gb15
    out["giveback_at_plus30"] = gb30
    out["giveback_at_first_mdecay"] = gb_mdecay
    out["age_at_first_mdecay"] = age_mdecay
    return out


print("Building full-population checkpoint trace, Product B shorts (n=%d)..." % len(blocks_B))
full_B = build_full_trace(blocks_B, "giveback_ratio_B")
print("Building full-population checkpoint trace, Product A shorts (n=%d)..." % len(blocks_A))
full_A = build_full_trace(blocks_A, "giveback_ratio_A")

full_B.to_parquet(OUT + r"\full_trace_B_short.parquet")
full_A.to_parquet(OUT + r"\full_trace_A_short.parquet")


def year_chronology(full_df, label):
    rows = []
    # canonical years 2022-2025 + 2026 canonical (Jan-May) individually, then 2026 health-only separately
    full_df = full_df.copy()
    full_df["chrono_bucket"] = full_df["year"].astype(str)
    full_df.loc[full_df["is_health_only_bar"], "chrono_bucket"] = "2026_JunJul_HEALTHONLY"
    for bucket in ["2022", "2023", "2024", "2025", "2026", "2026_JunJul_HEALTHONLY"]:
        sub = full_df[full_df["chrono_bucket"] == bucket]
        if len(sub) < 5:
            continue
        row = {"product": label, "bucket": bucket, "n": len(sub)}
        for cp_col in ["giveback_at_plus15", "giveback_at_plus30", "giveback_at_first_mdecay"]:
            valid = sub.dropna(subset=[cp_col, "net_pnl"])
            if len(valid) >= 5:
                rho, p = sps.spearmanr(valid[cp_col], valid["net_pnl"])
                row[f"{cp_col}_spearman"] = round(float(rho), 3)
                row[f"{cp_col}_p"] = round(float(p), 4)
                row[f"{cp_col}_n"] = len(valid)
            else:
                row[f"{cp_col}_spearman"] = None
        rows.append(row)
    return pd.DataFrame(rows)


chrono_B = year_chronology(full_B, "B")
chrono_A = year_chronology(full_A, "A")
chrono_B.to_csv(OUT + r"\chronology_B.csv", index=False)
chrono_A.to_csv(OUT + r"\chronology_A.csv", index=False)

print("\n=== Product B short blocks: Spearman(giveback_at_checkpoint, net_pnl) by year ===")
print(chrono_B[["bucket", "n", "giveback_at_plus15_spearman", "giveback_at_plus30_spearman",
                 "giveback_at_first_mdecay_spearman"]].to_string(index=False))

print("\n=== Product A short blocks: Spearman(giveback_at_checkpoint, net_pnl) by year ===")
print(chrono_A[["bucket", "n", "giveback_at_plus15_spearman", "giveback_at_plus30_spearman",
                 "giveback_at_first_mdecay_spearman"]].to_string(index=False))

# pooled canonical-only (2022-2025 + 2026 canonical Jan-May) overall Spearman, for headline number
canon_B = full_B[~full_B["is_health_only_bar"]]
canon_A = full_A[~full_A["is_health_only_bar"]]
summary = {}
for label, df_ in [("B", canon_B), ("A", canon_A)]:
    for cp_col in ["giveback_at_plus15", "giveback_at_plus30", "giveback_at_first_mdecay"]:
        valid = df_.dropna(subset=[cp_col, "net_pnl"])
        rho, p = sps.spearmanr(valid[cp_col], valid["net_pnl"])
        summary[f"{label}_{cp_col}_pooled_canonical_spearman"] = round(float(rho), 4)
        summary[f"{label}_{cp_col}_pooled_canonical_p"] = float(p)
        summary[f"{label}_{cp_col}_pooled_canonical_n"] = int(len(valid))

print("\n=== Pooled canonical-window headline Spearman correlations ===")
print(json.dumps(summary, indent=2))

with open(OUT + r"\chronology_summary.json", "w") as f:
    json.dump(summary, f, indent=2)
