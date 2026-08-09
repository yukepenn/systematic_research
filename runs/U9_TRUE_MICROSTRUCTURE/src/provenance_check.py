"""
U9_TRUE_MICROSTRUCTURE -- provenance verification script.

Infrastructure/provenance only (Track C). Re-derives every on-disk fact cited in
../spec.yaml's provenance_gate section directly from research/scalping_lab/substrate/,
so the claims in spec.yaml are reproducible rather than asserted. Computes NO
feature-outcome relationship, NO P&L, NO candidate statistic -- schema/coverage/
timestamp/duplicate/gap inspection only, per this family's explicit no-alpha charter.

Run from repo root:
    python runs/U9_TRUE_MICROSTRUCTURE/src/provenance_check.py

Writes:
    runs/U9_TRUE_MICROSTRUCTURE/out/session_manifest_check.csv
    runs/U9_TRUE_MICROSTRUCTURE/out/block_table.csv
"""
import os
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
SL = os.path.join(ROOT, "research", "scalping_lab")
SUB = os.path.join(SL, "substrate")
OUT = os.path.join(ROOT, "runs", "U9_TRUE_MICROSTRUCTURE", "out")


def check_raw_sessions():
    """Per-session facts from substrate/raw/NQ: coverage, bip semantics, duplicates."""
    raw_dir = os.path.join(SUB, "raw", "NQ")
    files = sorted(f for f in os.listdir(raw_dir) if f.endswith(".parquet"))
    rows = []
    for f in files:
        df = pd.read_parquet(os.path.join(raw_dir, f))
        bipc = df["bip"].value_counts().to_dict()
        rows.append({
            "file": f,
            "n_rows": len(df),
            "t_min": df["time"].min(),
            "t_max": df["time"].max(),
            "price_min": df["price"].min(),
            "price_max": df["price"].max(),
            "n_last": bipc.get(0, 0),
            "n_bid": bipc.get(1, 0),
            "n_ask": bipc.get(2, 0),
            "exact_dup_row_frac": df.duplicated().mean(),
            "dup_timestamp_frac": df["time"].duplicated().mean(),
            "monotonic_time_frac": (df["time"].diff().dropna() >= pd.Timedelta(0)).mean(),
        })
    return pd.DataFrame(rows)


def check_grid1s_coverage():
    """Per-session close-coverage check on the merged (main+_rth) causal 1s grid."""
    grid_dir = os.path.join(SUB, "grid1s", "NQ")
    files = sorted(f for f in os.listdir(grid_dir) if f.endswith(".parquet"))
    rows = []
    for f in files:
        df = pd.read_parquet(os.path.join(grid_dir, f), columns=["time"])
        tmax = df["time"].max()
        rows.append({
            "session_file": f,
            "n_rows": len(df),
            "t_min": df["time"].min(),
            "t_max": tmax,
            "reaches_1659_59_close": tmax.strftime("%H:%M:%S") == "16:59:59",
        })
    return pd.DataFrame(rows)


def check_sechilo_scale(session="s20250905"):
    """Confirms sechilo price fields = grid1s mid * 4 (NQ 0.25pt tick -> integer tick units)."""
    g1 = pd.read_parquet(os.path.join(SUB, "grid1s", "NQ", f"{session}.parquet"),
                          columns=["time", "mid"])
    sec = pd.read_parquet(os.path.join(SUB, "sechilo", "NQ", f"{session}.parquet"),
                           columns=["time", "mid_last"])
    m = sec.merge(g1, on="time", how="inner")
    m["sec_div4"] = m["mid_last"] / 4.0
    return {
        "session": session,
        "corr": m["sec_div4"].corr(m["mid"]),
        "max_abs_diff": (m["sec_div4"] - m["mid"]).abs().max(),
    }


def build_frozen_block_table():
    """Reproduces the exact 40-session -> 9-block (floor-3 merge) table frozen in spec.yaml."""
    raw_dir = os.path.join(SUB, "raw", "NQ")
    base_sessions = sorted(set(
        f.replace(".parquet", "").replace("_rth", "")
        for f in os.listdir(raw_dir) if f.endswith(".parquet")
    ))
    dates = pd.to_datetime([s[1:] for s in base_sessions], format="%Y%m%d")
    df = pd.DataFrame({"session": base_sessions, "date": dates}).sort_values("date")
    df["ym"] = df["date"].dt.to_period("M")
    monthly = df.groupby("ym").size()

    # floor-3 forward-merge rule, applied mechanically
    blocks = []
    pending_label, pending_n, pending_months = None, 0, []
    for ym, n in monthly.items():
        if pending_label is None:
            pending_label, pending_n, pending_months = str(ym), n, [ym]
        else:
            pending_n += n
            pending_months.append(ym)
            pending_label = "+".join(str(m) for m in pending_months)
        if pending_n >= 3:
            blocks.append({"calendar": pending_label, "sessions": pending_n})
            pending_label, pending_n, pending_months = None, 0, []
    if pending_n > 0:  # trailing thin remainder folds into the last block
        blocks[-1]["calendar"] += "+" + "+".join(str(m) for m in pending_months)
        blocks[-1]["sessions"] += pending_n

    bt = pd.DataFrame(blocks)
    bt["block"] = range(1, len(bt) + 1)
    bt["role"] = ["seed"] + ["scored"] * (len(bt) - 1)
    return bt[["block", "calendar", "sessions", "role"]]


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)

    raw_check = check_raw_sessions()
    grid_check = check_grid1s_coverage()
    merged = grid_check.merge(
        raw_check.rename(columns={"file": "session_file_raw"}),
        left_on="session_file", right_on="session_file_raw", how="left",
    )
    merged.to_csv(os.path.join(OUT, "session_manifest_check.csv"), index=False)

    block_table = build_frozen_block_table()
    block_table.to_csv(os.path.join(OUT, "block_table.csv"), index=False)

    scale = check_sechilo_scale()

    print("=== Session close-coverage: sessions NOT reaching 16:59:59 ===")
    print(grid_check[~grid_check["reaches_1659_59_close"]][["session_file", "n_rows", "t_max"]])
    print("\n=== Frozen block table (floor-3 merge) ===")
    print(block_table)
    print(f"\n=== sechilo scale check ({scale['session']}) ===")
    print(f"corr(sechilo.mid_last/4, grid1s.mid) = {scale['corr']:.7f}, "
          f"max abs diff = {scale['max_abs_diff']:.3f}")
    print(f"\nWrote {OUT}\\session_manifest_check.csv and block_table.csv")
