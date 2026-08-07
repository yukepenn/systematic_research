"""AUDIT-02: fill-by-fill reproduction diff between committed campaign ledgers
and the audit re-run ledgers (AUDIT02_V3_SWEEP / AUDIT02_V4_SWEEP).

Comparison key per fill row: (time, order_action, price, commission, qty).
The `n` and `bar` columns are ordinal/engine-internal and compared only as
counts; `wave`/`signal` are attribution metadata, compared but reported
separately (a wave/signal mismatch with identical fills is a metadata note,
not a reproduction failure).

Usage:  python src/analytics/audit02_compare.py  (CWD = repo root)
Writes: research/audit/v3_reproduction_diff.csv, v4_reproduction_diff.csv
        and prints a verdict table.
"""
import glob
import os
import re
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PAIRS = [
    dict(
        name="V3",
        committed=os.path.join(ROOT, "research", "05_open_axes", "h006",
                               "h006__tf3_sm179_am0_th1_vp460_vm{vm}_xm0_sc_slip1.csv"),
        rerun=os.path.join(ROOT, "runs", "AUDIT02_V3_SWEEP_B", "ledgers",
                           "b2v3__tf3_sm179_am0_th1_vp460_vm{vm}_xm0_sc_slip1.csv"),
        out=os.path.join(ROOT, "research", "audit", "v3_reproduction_diff.csv"),
    ),
    dict(
        name="V4",
        committed=os.path.join(ROOT, "research", "10_v3v4_equivalence",
                               "v4verify__NQ_tf3_sm179_am0_th1_vp460_vm{vm}_bp20_xm0_sc_slip1.csv"),
        rerun=os.path.join(ROOT, "runs", "AUDIT02_V4_SWEEP_B", "ledgers",
                           "b2v4__NQ_tf3_sm179_am0_th1_vp460_vm{vm}_bp20_xm0_sc_slip1.csv"),
        out=os.path.join(ROOT, "research", "audit", "v4_reproduction_diff.csv"),
    ),
]

VMS = [6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]

FILL_COLS = ["time", "order_action", "price", "commission", "qty"]
META_COLS = ["wave", "signal"]


def load(path):
    df = pd.read_csv(path, comment="#")
    df["time"] = pd.to_datetime(df["time"])
    return df.reset_index(drop=True)


def find(path_tpl, vm):
    """Resolve the ledger path for a cell, tolerating int-vs-float vm in filenames."""
    for token in (str(vm), f"{vm}.0"):
        p = path_tpl.format(vm=token)
        if os.path.exists(p):
            return p
    hits = glob.glob(re.sub(r"vm\{vm\}", f"vm{vm}*", path_tpl.replace("{vm}", str(vm))))
    return hits[0] if hits else None


def compare_cell(pc, pr):
    a, b = load(pc), load(pr)
    row = dict(committed_fills=len(a), rerun_fills=len(b))
    if len(a) != len(b):
        row["verdict"] = "COUNT_MISMATCH"
        # locate first divergence by merge on time+action
        k = min(len(a), len(b))
        neq = (a.loc[:k - 1, FILL_COLS].reset_index(drop=True)
               != b.loc[:k - 1, FILL_COLS].reset_index(drop=True)).any(axis=1)
        row["first_diff_row"] = int(neq.idxmax()) if neq.any() else k
        return row
    neq = (a[FILL_COLS].reset_index(drop=True) != b[FILL_COLS].reset_index(drop=True)).any(axis=1)
    n_fill_diff = int(neq.sum())
    meta_neq = (a[META_COLS].reset_index(drop=True) != b[META_COLS].reset_index(drop=True)).any(axis=1)
    row["fill_mismatch_rows"] = n_fill_diff
    row["meta_mismatch_rows"] = int(meta_neq.sum())
    row["first_diff_row"] = int(neq.idxmax()) if neq.any() else -1
    row["verdict"] = "EXACT" if n_fill_diff == 0 else "FILL_MISMATCH"
    return row


def main():
    for pair in PAIRS:
        rows = []
        print(f"\n=== {pair['name']} ===")
        for vm in VMS:
            pc, pr = find(pair["committed"], vm), find(pair["rerun"], vm)
            if pc is None or pr is None:
                rows.append(dict(vm=vm, verdict="MISSING",
                                 committed=bool(pc), rerun=bool(pr)))
                print(f"vm{vm:>2}: MISSING committed={bool(pc)} rerun={bool(pr)}")
                continue
            r = compare_cell(pc, pr)
            r["vm"] = vm
            rows.append(r)
            print(f"vm{vm:>2}: {r['verdict']}  fills {r['committed_fills']}=={r['rerun_fills']}"
                  + (f"  fill_diff={r.get('fill_mismatch_rows')}" if "fill_mismatch_rows" in r else "")
                  + (f"  meta_diff={r.get('meta_mismatch_rows')}" if "meta_mismatch_rows" in r else ""))
        out = pd.DataFrame(rows).set_index("vm")
        os.makedirs(os.path.dirname(pair["out"]), exist_ok=True)
        out.to_csv(pair["out"])
        exact = (out["verdict"] == "EXACT").sum()
        print(f"{pair['name']}: {exact}/{len(VMS)} cells EXACT -> {pair['out']}")


if __name__ == "__main__":
    sys.exit(main())
