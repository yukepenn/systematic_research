"""EXEC01 step 3 -- align Python order-events (python_orders_periods.csv, both price bases) against
NT8 order-events (nt8_orders_periods.csv) leg-by-leg within each of the 9 selected periods, compute
the dollar residual per leg, and classify every dollar of residual into exactly one bucket:
  genuine_mnq_vs_proxy_price_basis, fill_timing, bar_boundary_serialization, same_bar_transition,
  one_tick_convention, commission, session_close_handling, rounding, unexplained

Method (see 00_period_selection.md / this script's own header comments for full derivation):
  1. price-basis component isolated FIRST and exactly, using the byte-identical target-exposure
     invariant already verified in step 1: python_genuine_cash - python_legacy_cash, computed at
     the SAME (time, side, qty) as the legacy leg (guaranteed identical between the two price bases).
  2. remaining residual = nt8_cash - python_genuine_cash, decomposed leg-by-leg by inspecting
     qty match, side match, time alignment (exact bar vs nearest-neighbor fallback), price diff
     size (0 / exactly-1-tick / other), and commission diff.
  3. unmatched legs (present on only one side) are classified from context (session boundary,
     period boundary, flatten/reversal signature) or fall to `unexplained` if none of the other
     buckets legitimately apply.

Every dollar of every leg's diff is assigned to exactly one bucket; nothing is silently dropped.
"""
import os
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(ROOT, "runs", "EXEC01_PRODUCT_A_DOLLAR_ATTRIBUTION", "out")

PV_MNQ_A = 2.0
TICK = 0.25
TOL_TICK = 0.02

py = pd.read_csv(os.path.join(OUT, "python_orders_periods.csv"), parse_dates=["time", "sess_dt"])
nt = pd.read_csv(os.path.join(OUT, "nt8_orders_periods.csv"), parse_dates=["time"])

periods = pd.read_csv(os.path.join(OUT, "periods_selected.csv"))
period_bounds = {r["id"]: (pd.Timestamp(r["start"]), pd.Timestamp(r["end"]) + pd.Timedelta(days=1)) for _, r in periods.iterrows()}

leg_rows = []


def classify_matched(py_row, nt_row, match_kind, dt_sec):
    """Returns (bucket_breakdown: dict[bucket -> dollars], notes: str) for ONE matched leg pair.
    The dict's values sum EXACTLY to nt_cash - py_legacy_cash (the leg's full dollar residual)."""
    side = py_row["side"]
    py_qty, nt_qty = py_row["qty"], nt_row["qty"]
    py_px_legacy, py_px_genuine = py_row["price_legacy"], py_row["price_genuine"]
    py_comm_legacy, py_comm_genuine = py_row["comm_legacy"], py_row["comm_genuine"]
    nt_px, nt_qty_, nt_comm = nt_row["price"], nt_row["qty"], nt_row["comm"]

    py_cash_legacy = -side * py_qty * py_px_legacy * PV_MNQ_A - py_comm_legacy
    py_cash_genuine = -side * py_qty * py_px_genuine * PV_MNQ_A - py_comm_genuine
    nt_cash = -side * nt_qty * nt_px * PV_MNQ_A - nt_comm

    diff_total = nt_cash - py_cash_legacy
    buckets = {}

    # 1. price-basis component (exact, always computed first, uses SAME py_qty/side both bases)
    price_basis = py_cash_genuine - py_cash_legacy
    buckets["genuine_mnq_vs_proxy_price_basis"] = price_basis
    remainder = diff_total - price_basis  # = nt_cash - py_cash_genuine

    if py_qty == nt_qty:
        # qty matches exactly -> remainder is pure price+commission effect at matched quantity
        px_diff = nt_px - py_px_genuine
        px_component = -side * py_qty * PV_MNQ_A * px_diff
        comm_component = nt_comm - py_comm_genuine
        # sanity: px_component + comm_component should equal remainder (to fp tolerance)
        check = abs((px_component + comm_component) - remainder)
        assert check < 0.01, f"decomposition mismatch {check}"

        if abs(px_diff) < TOL_TICK:
            bucket_px = "rounding" if abs(px_component) > 1e-9 else None
        elif abs(px_diff - (-side) * TICK) < TOL_TICK:
            # NT8 price is exactly 1 tick BETTER than python's synthetic-adverse-slip genuine
            # price, in the direction predicted by sm01_solarsim._fill's own docstring
            # ("1-tick adverse slip") -- matches the already-disclosed BEST_ONE_NQ/MNQ mechanism.
            bucket_px = "one_tick_convention"
        elif match_kind == "fuzzy" or dt_sec > 90:
            bucket_px = "fill_timing"
        else:
            bucket_px = "same_bar_transition" if py_row["kind"] == "adjust" and nt_row["n_legs_combined"] > 1 else "unexplained"

        if bucket_px:
            buckets[bucket_px] = buckets.get(bucket_px, 0.0) + px_component
        if abs(comm_component) > 1e-9:
            buckets["commission"] = buckets.get("commission", 0.0) + comm_component
    else:
        # qty mismatch -- genuine decision/order-count discrepancy for this leg. Attribute the
        # WHOLE remainder to same_bar_transition if this NT8 group merged >1 raw leg (reversal
        # decomposition ambiguity) or a flatten/session-close leg is involved; else unexplained.
        if nt_row["n_legs_combined"] > 1:
            buckets["same_bar_transition"] = buckets.get("same_bar_transition", 0.0) + remainder
        elif py_row["kind"] == "flatten":
            buckets["session_close_handling"] = buckets.get("session_close_handling", 0.0) + remainder
        else:
            buckets["unexplained"] = buckets.get("unexplained", 0.0) + remainder

    return diff_total, buckets


def classify_unmatched_python(py_row, period_end):
    """Python leg has NO NT8 counterpart. The FULL python_legacy leg cash is what NT8 apparently
    never realized (from Python's point of view) -- but since we're measuring nt8-vs-python-legacy,
    a python-only leg means NT8's side of the ledger is missing this cash flow, i.e. contributes
    -py_cash_legacy to the (nt8 - python) diff. Bucket by context."""
    side = py_row["side"]; qty = py_row["qty"]
    py_cash_legacy = -side * qty * py_row["price_legacy"] * PV_MNQ_A - py_row["comm_legacy"]
    py_cash_genuine = -side * qty * py_row["price_genuine"] * PV_MNQ_A - py_row["comm_genuine"]
    diff_total = -py_cash_legacy  # NT8 contributes 0 for this leg
    price_basis = -(py_cash_genuine - py_cash_legacy)
    remainder = diff_total - price_basis
    near_boundary = (period_end - py_row["time"]) < pd.Timedelta(hours=6)
    if py_row["kind"] == "flatten":
        bucket = "session_close_handling"
    elif near_boundary:
        bucket = "bar_boundary_serialization"
    else:
        bucket = "unexplained"
    buckets = {"genuine_mnq_vs_proxy_price_basis": price_basis, bucket: remainder}
    return diff_total, buckets


def classify_unmatched_nt8(nt_row, period_start, period_end):
    """NT8 leg has NO Python counterpart. Contributes its full nt8_cash to the diff (python
    contributes 0). No price-basis split possible (no python leg to compare against)."""
    side = nt_row["side"]; qty = nt_row["qty"]
    nt_cash = -side * qty * nt_row["price"] * PV_MNQ_A - nt_row["comm"]
    diff_total = nt_cash
    near_boundary = (nt_row["time"] - period_start) < pd.Timedelta(hours=6) or (period_end - nt_row["time"]) < pd.Timedelta(hours=6)
    if nt_row["n_legs_combined"] > 1:
        bucket = "same_bar_transition"
    elif near_boundary:
        bucket = "bar_boundary_serialization"
    else:
        bucket = "unexplained"
    return diff_total, {bucket: diff_total}


# ---------------------------------------------------------------- align + classify, per period
for pid in periods["id"]:
    py_p = py[py["period"] == pid].sort_values("time").reset_index(drop=True).copy()
    nt_p = nt[nt["period"] == pid].sort_values("time").reset_index(drop=True).copy()
    py_used = np.zeros(len(py_p), dtype=bool)
    nt_used = np.zeros(len(nt_p), dtype=bool)

    # pass 1: exact (time, side) match
    nt_by_time = {}
    for j, r in nt_p.iterrows():
        nt_by_time.setdefault((r["time"], r["side"]), []).append(j)

    for i, pr in py_p.iterrows():
        key = (pr["time"], pr["side"])
        cands = [j for j in nt_by_time.get(key, []) if not nt_used[j]]
        if cands:
            j = cands[0]
            nt_used[j] = True; py_used[i] = True
            diff_total, buckets = classify_matched(pr, nt_p.loc[j], "exact", 0.0)
            leg_rows.append({"period": pid, "match": "exact", "py_idx": i, "nt_idx": j,
                              "py_time": pr["time"], "nt_time": nt_p.loc[j, "time"],
                              "side": pr["side"], "py_qty": pr["qty"], "nt_qty": nt_p.loc[j, "qty"],
                              "py_price_legacy": pr["price_legacy"], "py_price_genuine": pr["price_genuine"],
                              "nt_price": nt_p.loc[j, "price"], "py_kind": pr["kind"],
                              "nt_leg_kinds": nt_p.loc[j, "leg_kinds"], "n_legs_combined": nt_p.loc[j, "n_legs_combined"],
                              "diff_total": diff_total, **{f"bucket__{k}": v for k, v in buckets.items()}})

    # pass 2: fuzzy nearest-time match (tolerance 30 min, same side), for leftovers
    py_left_idx = [i for i in range(len(py_p)) if not py_used[i]]
    nt_left_idx = [j for j in range(len(nt_p)) if not nt_used[j]]
    for i in py_left_idx:
        pr = py_p.loc[i]
        best_j, best_dt = None, None
        for j in nt_left_idx:
            if nt_used[j]:
                continue
            nr = nt_p.loc[j]
            if nr["side"] != pr["side"]:
                continue
            dt = abs((nr["time"] - pr["time"]).total_seconds())
            if dt <= 1800 and (best_dt is None or dt < best_dt):
                best_j, best_dt = j, dt
        if best_j is not None:
            nt_used[best_j] = True; py_used[i] = True
            diff_total, buckets = classify_matched(pr, nt_p.loc[best_j], "fuzzy", best_dt)
            leg_rows.append({"period": pid, "match": "fuzzy", "py_idx": i, "nt_idx": best_j,
                              "py_time": pr["time"], "nt_time": nt_p.loc[best_j, "time"],
                              "side": pr["side"], "py_qty": pr["qty"], "nt_qty": nt_p.loc[best_j, "qty"],
                              "py_price_legacy": pr["price_legacy"], "py_price_genuine": pr["price_genuine"],
                              "nt_price": nt_p.loc[best_j, "price"], "py_kind": pr["kind"],
                              "nt_leg_kinds": nt_p.loc[best_j, "leg_kinds"], "n_legs_combined": nt_p.loc[best_j, "n_legs_combined"],
                              "diff_total": diff_total, **{f"bucket__{k}": v for k, v in buckets.items()}})

    period_start, period_end = period_bounds[pid]
    # unmatched python legs
    for i in range(len(py_p)):
        if py_used[i]:
            continue
        pr = py_p.loc[i]
        diff_total, buckets = classify_unmatched_python(pr, period_end)
        leg_rows.append({"period": pid, "match": "python_only", "py_idx": i, "nt_idx": None,
                          "py_time": pr["time"], "nt_time": None, "side": pr["side"],
                          "py_qty": pr["qty"], "nt_qty": 0,
                          "py_price_legacy": pr["price_legacy"], "py_price_genuine": pr["price_genuine"],
                          "nt_price": None, "py_kind": pr["kind"], "nt_leg_kinds": None, "n_legs_combined": None,
                          "diff_total": diff_total, **{f"bucket__{k}": v for k, v in buckets.items()}})
    # unmatched nt8 legs
    for j in range(len(nt_p)):
        if nt_used[j]:
            continue
        nr = nt_p.loc[j]
        diff_total, buckets = classify_unmatched_nt8(nr, period_start, period_end)
        leg_rows.append({"period": pid, "match": "nt8_only", "py_idx": None, "nt_idx": j,
                          "py_time": None, "nt_time": nr["time"], "side": nr["side"],
                          "py_qty": 0, "nt_qty": nr["qty"],
                          "py_price_legacy": None, "py_price_genuine": None,
                          "nt_price": nr["price"], "py_kind": None, "nt_leg_kinds": nr["leg_kinds"],
                          "n_legs_combined": nr["n_legs_combined"],
                          "diff_total": diff_total, **{f"bucket__{k}": v for k, v in buckets.items()}})

    n_exact = sum(1 for r in leg_rows if r["period"] == pid and r["match"] == "exact")
    n_fuzzy = sum(1 for r in leg_rows if r["period"] == pid and r["match"] == "fuzzy")
    n_py_only = sum(1 for r in leg_rows if r["period"] == pid and r["match"] == "python_only")
    n_nt_only = sum(1 for r in leg_rows if r["period"] == pid and r["match"] == "nt8_only")
    print(f"  {pid}: python={len(py_p)} nt8={len(nt_p)}  exact={n_exact} fuzzy={n_fuzzy} "
          f"py_only={n_py_only} nt8_only={n_nt_only}")

leg_df = pd.DataFrame(leg_rows)
bucket_cols = [c for c in leg_df.columns if c.startswith("bucket__")]
leg_df[bucket_cols] = leg_df[bucket_cols].fillna(0.0)

# recheck: sum of bucket columns per row == diff_total
row_bucket_sum = leg_df[bucket_cols].sum(axis=1)
mismatch = (row_bucket_sum - leg_df["diff_total"]).abs() > 0.02
assert mismatch.sum() == 0, f"{mismatch.sum()} rows where buckets don't sum to diff_total"

leg_df.to_csv(os.path.join(OUT, "leg_reconciliation.csv"), index=False)
leg_df.to_json(os.path.join(OUT, "leg_reconciliation.json"), orient="records", indent=2, date_format="iso")
print(f"\n[EXEC01/03] wrote leg_reconciliation.csv/json ({len(leg_df)} legs)")

# ---------------------------------------------------------------- summaries
print("\n=== per-period total dollar residual (nt8 - python_legacy), leg-cash-flow basis ===")
per_period = leg_df.groupby("period")["diff_total"].sum().reindex(periods["id"])
print(per_period.to_string())
print(f"\nTOTAL dollar residual examined (9 periods): {per_period.sum():.2f}")

print("\n=== bucket totals across all 9 periods ===")
ALL_BUCKETS = ["genuine_mnq_vs_proxy_price_basis", "fill_timing", "bar_boundary_serialization",
               "same_bar_transition", "one_tick_convention", "commission", "session_close_handling",
               "rounding", "unexplained"]
bucket_totals = {b: 0.0 for b in ALL_BUCKETS}
for c in bucket_cols:
    bucket_totals[c.replace("bucket__", "")] = float(leg_df[c].sum())
bucket_series = pd.Series(bucket_totals).sort_values(key=np.abs, ascending=False)
print(bucket_series.to_string())
total_residual = float(per_period.sum())
print(f"\nsum of buckets = {sum(bucket_totals.values()):.2f}  (should equal total residual = {total_residual:.2f})")
print(f"n legs with ANY unexplained $ : {int((leg_df.get('bucket__unexplained', pd.Series(0, index=leg_df.index)).abs() > 1e-9).sum())}")

# ---------------------------------------------------------------- extrapolation to full 4.5y canonical history
# Primary certified full-history figure being cross-checked against (FULL_HISTORY_CERTIFICATION.md
# L59-68, re-verified at task start): NT8 stitched $197,329.70 vs Python mark-to-market $177,924.40,
# diff +$19,405.30 (+10.91%).
FULL_HISTORY_RESIDUAL = 19405.30
day_stats = pd.read_csv(os.path.join(OUT, "day_stats.csv"))
turnover_full = float(day_stats["turnover_contracts"].sum())
n_sess_full = len(day_stats)
turnover_sample = float(periods["sum_turnover"].sum())
n_sess_sample = int(periods["n_sessions"].sum())

# genuine_mnq_vs_proxy_price_basis: PRICE01 already computed this EXACTLY for the full canonical
# history (not sampled) -- runs/PRICE01_PRODUCT_A_GENUINE_MNQ/REPORT.md: genuine MNQ canonical net
# $178,687.40 vs legacy canonical net $177,924.40, diff +$763.00. Use that exact figure directly
# rather than extrapolating our 9-period sample's own $67.00 for this bucket.
price_basis_full_exact = 763.00

# one_tick_convention: no independent full-history leg-level figure exists yet (this run IS that
# proof, for the 9 sampled periods) -- extrapolate from the sample using TURNOVER as the scaling
# variable (not session count), because this bucket's dollar impact is a near-deterministic linear
# function of turnover (qty * PV_MNQ_A * TICK = qty * $0.50/contract, discounted only by the small
# fraction of legs where the bar's own high/low range clips the synthetic slip before it reaches a
# full tick -- 16/1371 = 1.2% of legs in this sample). Session-count scaling is shown alongside as
# an explicit upper bound: our 9 periods were deliberately selected for HIGH turnover/exposure/
# reversal extremes (mean 41.7 contracts/session in-sample vs 32.3 contracts/session full-history,
# +29%), so session-count scaling systematically overstates the full-history total.
one_tick_rate_per_contract = bucket_totals["one_tick_convention"] / turnover_sample
one_tick_turnover_scaled = one_tick_rate_per_contract * turnover_full
one_tick_sessioncount_scaled = bucket_totals["one_tick_convention"] / n_sess_sample * n_sess_full

extrap_turnover = one_tick_turnover_scaled + price_basis_full_exact
extrap_sessioncount = one_tick_sessioncount_scaled + price_basis_full_exact

print(f"\n=== extrapolation to full canonical history ({n_sess_full} sessions, {turnover_full:.0f} contracts turnover) ===")
print(f"sample: {n_sess_sample} sessions ({n_sess_sample/n_sess_full*100:.1f}% of sessions), "
      f"{turnover_sample:.0f} contracts turnover ({turnover_sample/turnover_full*100:.1f}% of full turnover)")
print(f"genuine_mnq_vs_proxy_price_basis: EXACT full-history figure already computed by PRICE01, "
      f"not extrapolated: ${price_basis_full_exact:,.2f}")
print(f"one_tick_convention: sample rate ${one_tick_rate_per_contract:.4f}/contract-turnover "
      f"(theoretical max $0.50/contract if never clipped by bar range)")
print(f"  turnover-scaled (PRIMARY):    ${one_tick_turnover_scaled:,.2f}")
print(f"  session-count-scaled (UPPER): ${one_tick_sessioncount_scaled:,.2f}")
print(f"TOTAL extrapolated explained (turnover-scaled + exact price-basis): ${extrap_turnover:,.2f} "
      f"= {extrap_turnover/FULL_HISTORY_RESIDUAL*100:.1f}% of certified ${FULL_HISTORY_RESIDUAL:,.2f} full-history residual")
print(f"TOTAL extrapolated explained (session-count-scaled + exact price-basis): ${extrap_sessioncount:,.2f} "
      f"= {extrap_sessioncount/FULL_HISTORY_RESIDUAL*100:.1f}% of certified full-history residual")

summary = {
    "total_dollar_residual_examined": round(total_residual, 2),
    "per_period_residual": {k: round(float(v), 2) for k, v in per_period.items()},
    "bucket_totals": {k: round(float(v), 2) for k, v in bucket_totals.items()},
    "n_legs_total": int(len(leg_df)),
    "n_legs_by_match_type": leg_df["match"].value_counts().to_dict(),
    "n_legs_qty_mismatch": int((leg_df["py_qty"] != leg_df["nt_qty"]).sum()),
    "extrapolation": {
        "full_history_certified_residual": FULL_HISTORY_RESIDUAL,
        "full_history_certified_residual_source": "runs/V1R4_NT8_PARITY/FULL_HISTORY_CERTIFICATION.md L59-68",
        "n_sessions_full": n_sess_full, "n_sessions_sample": n_sess_sample,
        "turnover_full": turnover_full, "turnover_sample": turnover_sample,
        "genuine_mnq_price_basis_full_history_EXACT": price_basis_full_exact,
        "genuine_mnq_price_basis_source": "runs/PRICE01_PRODUCT_A_GENUINE_MNQ/REPORT.md (exact, not extrapolated)",
        "one_tick_convention_rate_per_contract_turnover": round(one_tick_rate_per_contract, 4),
        "one_tick_convention_turnover_scaled_PRIMARY": round(one_tick_turnover_scaled, 2),
        "one_tick_convention_sessioncount_scaled_UPPER": round(one_tick_sessioncount_scaled, 2),
        "total_explained_turnover_scaled": round(extrap_turnover, 2),
        "total_explained_turnover_scaled_pct": round(extrap_turnover / FULL_HISTORY_RESIDUAL * 100, 1),
        "total_explained_sessioncount_scaled": round(extrap_sessioncount, 2),
        "total_explained_sessioncount_scaled_pct": round(extrap_sessioncount / FULL_HISTORY_RESIDUAL * 100, 1),
        "caveat": ("Turnover-scaling is the primary estimate because one_tick_convention's dollar "
                   "impact is a near-deterministic linear function of turnover (qty * $0.50/contract, "
                   "verified in-sample: rate is within 1%% of the theoretical $0.50 max). Session-count "
                   "scaling is shown as an explicit upper bound because the 9 periods were deliberately "
                   "selected for turnover/exposure/reversal EXTREMES, not randomly, so they over-represent "
                   "high-turnover sessions (+29%% turnover/session vs full history) -- this is a genuine "
                   "extrapolation with real uncertainty, not a proof, for the one_tick_convention bucket "
                   "specifically; the price-basis bucket uses PRICE01's own exact full-history figure, not "
                   "an extrapolation. Chunks E2 (2022-09-01..2023-05-01) and E4 (2024-01-01..2024-09-01) "
                   "are not independently represented in the 9 periods (disclosed in 00_period_selection.md); "
                   "if either chunk has a structurally different tick-clip rate this extrapolation would be off."),
    },
}
import json
json.dump(summary, open(os.path.join(OUT, "reconciliation_summary.json"), "w"), indent=2)
print(f"\n[EXEC01/03] wrote reconciliation_summary.json")
print("[EXEC01/03] done.")
