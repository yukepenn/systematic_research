"""Resyncing leg-by-leg aligner for BEST_ONE_NQ Python-vs-NT8 event logs. Unlike a blind
positional pairing (which derails permanently after the first count-changing divergence), this
walks both time-sorted leg lists with two pointers and, on a mismatch, searches a bounded lookahead
window in each list for the next matching leg to resynchronize -- so it can report EVERY divergent
episode across the whole window, not just the first one detected before indices permanently shift.
"""
import pandas as pd
import numpy as np

OUT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\runs\V1R4_NT8_PARITY\out\one_nq_events"

py = pd.read_csv(f"{OUT}/python_events_2024apr_2025mar.csv", parse_dates=["time"])
nt = pd.read_csv(f"{OUT}/nt8_events_2024apr_2025mar.csv", parse_dates=["time"])
CUT = pd.Timestamp("2025-01-01")
py = py[py["time"] >= CUT].sort_values("time").reset_index(drop=True)
nt = nt[nt["time"] >= CUT].sort_values("time").reset_index(drop=True)


def matches(pr, nr):
    dt = abs((pr["time"] - nr["time"]).total_seconds())
    return dt <= 60 and pr["side"] == nr["side"]


LOOKAHEAD = 6
i = j = 0
matched = []
episodes = []  # each: {py_skipped: [...], nt_skipped: [...]}
while i < len(py) and j < len(nt):
    if matches(py.iloc[i], nt.iloc[j]):
        matched.append((i, j, abs(py.iloc[i]["price"] - nt.iloc[j]["price"])))
        i += 1; j += 1
        continue
    # mismatch -- search bounded lookahead for a resync point
    found = None
    for da in range(0, LOOKAHEAD + 1):
        for db in range(0, LOOKAHEAD + 1):
            if da == 0 and db == 0:
                continue
            ii, jj = i + da, j + db
            if ii < len(py) and jj < len(nt) and matches(py.iloc[ii], nt.iloc[jj]):
                found = (ii, jj)
                break
        if found:
            break
    if found is None:
        # no resync within window -- treat rest as one final episode and stop
        episodes.append({"py_rows": list(range(i, len(py))), "nt_rows": list(range(j, len(nt)))})
        i, j = len(py), len(nt)
        break
    ii, jj = found
    episodes.append({"py_rows": list(range(i, ii)), "nt_rows": list(range(j, jj))})
    i, j = ii, jj

print(f"matched legs: {len(matched)}   divergent episodes: {len(episodes)}")
tick_diffs = [d for _, _, d in matched]
print(f"matched-leg price diffs: min={min(tick_diffs):.2f} max={max(tick_diffs):.2f} "
      f"mean={np.mean(tick_diffs):.4f}  (0.25 = exactly 1 NQ tick)")
n_exact_tick = sum(1 for d in tick_diffs if abs(d - 0.25) < 1e-6)
n_zero = sum(1 for d in tick_diffs if d < 1e-6)
print(f"  exactly 0.25 (1 tick): {n_exact_tick}/{len(tick_diffs)}   exactly 0.00: {n_zero}/{len(tick_diffs)}")

print(f"\n{'='*90}\nDIVERGENT EPISODES (Python leg(s) NT8 doesn't have / vice versa)\n{'='*90}")
for k, ep in enumerate(episodes):
    py_rows = py.iloc[ep["py_rows"]] if ep["py_rows"] else None
    nt_rows = nt.iloc[ep["nt_rows"]] if ep["nt_rows"] else None
    print(f"\n--- episode {k+1} ---")
    if py_rows is not None and len(py_rows):
        print("  PYTHON-only legs:")
        print(py_rows[["time", "kind", "side", "price"]].to_string(index=False))
    if nt_rows is not None and len(nt_rows):
        print("  NT8-only legs:")
        print(nt_rows[["time", "kind", "side", "price", "order_action"]].to_string(index=False))

# net dollar impact of each NT8-only / python-only episode (approx, using $20/pt NQ)
print(f"\n{'='*90}\nSUMMARY\n{'='*90}")
n_py_only = sum(len(ep["py_rows"]) for ep in episodes)
n_nt_only = sum(len(ep["nt_rows"]) for ep in episodes)
print(f"total python-only legs: {n_py_only}   total nt8-only legs: {n_nt_only}")
