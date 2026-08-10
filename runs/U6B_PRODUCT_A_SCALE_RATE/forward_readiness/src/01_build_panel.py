"""U6B forward-readiness panel (Master Directive v4 sec8, Wave 5).

Builds an UNCERTAINTY-AWARE forward-readiness panel for CONTROL/F0.5/F0.7 under GENUINE MNQ
pricing. Every forward-looking statistic carries a session-block-bootstrap 95% CI (or is
explicitly flagged as too thin/unbootstrapped where honest). No new backtest engine: this
script only reads the already-certified daily P&L CSVs
(runs/U6B_PRODUCT_A_SCALE_RATE/out/{CONTROL,F0.5,F0.7}_daily_GENUINE_MNQ.csv) and the
already-computed year-by-year / repricing-recon / right-tail artifacts, and recomputes only the
NEW cuts this panel asks for (quarter-by-quarter, LOYO-by-dropped-year, rolling-window
distributions, per-year bootstrap CIs).

ABSOLUTE RULE: never touch data dated >= 2026-08-01 (research/operational/LOCKED_FORWARD.md).
The source CSVs already stop at 2026-07-31; this script adds an explicit assertion as a second
gate.

Canonical cutoff: sess_date <= 2026-05-29 (verified directly against the daily CSVs: the row
immediately after 2026-05-29 is 2026-06-01, confirming no ambiguity). Health-only extension:
2026-06-01 .. 2026-07-31 (matches health_substrate.py's own HEALTH_END and every other U6B
artifact this wave).

Session-block bootstrap convention: reused verbatim from this campaign's standing pattern
(runs/AUCTION01_VALUE_STATE/src/03_diagnostics.py, runs/FLOW01_AGGRESSIVE_PARTICIPATION/src/
02_analysis.py) -- resample sessions WITH REPLACEMENT (n_boot=1000), recompute the statistic on
each resample, report the 2.5/97.5 percentiles as the 95% CI. Because this panel's granularity
IS already one row per session (no finer intra-session decomposition is being resampled here),
a "session block" is exactly one daily P&L observation -- consistent with AUCTION01/FLOW01's own
definition of a block at whatever granularity one full session collapses to.

Run: python "01_build_panel.py" (from this directory, or via the ROOT-relative paths below --
no CLI args). Deterministic given SEED.
"""
import os, sys, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
from smv2_common import dd_battery
import primary_objective_v2 as PO2

U6B = os.path.join(ROOT, "runs", "U6B_PRODUCT_A_SCALE_RATE")
OUT_IN = os.path.join(U6B, "out")
FR = os.path.join(U6B, "forward_readiness")
OUT = os.path.join(FR, "out")
os.makedirs(OUT, exist_ok=True)

SEED = 20260809
N_BOOT = 1000
RNG_GLOBAL = np.random.default_rng(SEED)

CANONICAL_END = pd.Timestamp("2026-05-29")
EXT_START = pd.Timestamp("2026-06-01")
HEALTH_END = pd.Timestamp("2026-07-31")
LOCKED_FORWARD_START = pd.Timestamp("2026-08-01")

CANDIDATES = ["CONTROL", "F0.5", "F0.7"]
WINDOWS = [20, 60, 120, 252]

# ============================================================================================
# 0. LOAD + ABSOLUTE-RULE GATE
# ============================================================================================
daily = {}
for c in CANDIDATES:
    p = os.path.join(OUT_IN, f"{c}_daily_GENUINE_MNQ.csv")
    df = pd.read_csv(p)
    df["sess"] = pd.to_datetime(df["sess"])
    df = df.sort_values("sess").reset_index(drop=True)
    assert df["sess"].max() < LOCKED_FORWARD_START, (
        f"ABSOLUTE RULE VIOLATION: {c} daily series reaches {df['sess'].max()} "
        f">= {LOCKED_FORWARD_START} (sealed/virgin data)")
    daily[c] = df
    print(f"[load] {c}: n={len(df)} range=[{df['sess'].min().date()}, {df['sess'].max().date()}] "
          f"net=${df['net'].sum():,.2f}", flush=True)

print(f"[gate] all series confirmed < {LOCKED_FORWARD_START.date()}. Canonical cutoff "
      f"<= {CANONICAL_END.date()}, health-only extension {EXT_START.date()}..{HEALTH_END.date()}.",
      flush=True)


# ============================================================================================
# helpers
# ============================================================================================
def sharpe_stat(x):
    x = np.asarray(x, dtype=float)
    sd = x.std(ddof=1)
    return float(x.mean() / sd * np.sqrt(252)) if sd > 0 and len(x) > 1 else np.nan


def sortino_stat(x):
    x = np.asarray(x, dtype=float)
    dn = x[x < 0]
    if len(dn) > 1 and dn.std(ddof=1) > 0:
        return float(x.mean() / dn.std(ddof=1) * np.sqrt(252))
    return np.nan


def net_stat(x):
    return float(np.sum(x))


def session_block_bootstrap(x, stat_fn, n_boot=N_BOOT, seed=SEED, q=(2.5, 97.5)):
    """Resample sessions (rows) with replacement, n_boot reps, recompute stat_fn on each
    resample. Standing campaign convention (AUCTION01/FLOW01), applied here at the daily-P&L
    granularity (1 row == 1 session == 1 block)."""
    rng = np.random.default_rng(seed)
    x = np.asarray(x, dtype=float)
    n = len(x)
    if n < 10:
        return {"point": stat_fn(x), "ci_lo": np.nan, "ci_hi": np.nan, "n_boot": 0,
                "n_sessions": n, "TOO_THIN": True}
    boots = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, n, size=n)
        boots[i] = stat_fn(x[idx])
    lo, hi = np.nanpercentile(boots, q)
    return {"point": stat_fn(x), "boot_mean": float(np.nanmean(boots)),
            "ci_lo": float(lo), "ci_hi": float(hi), "n_boot": n_boot, "n_sessions": n,
            "TOO_THIN": False}


def battery_with_ci(sub_df, label):
    """Full dd_battery (campaign-standard) + session-block bootstrap 95% CI on Sharpe."""
    net = sub_df["net"].to_numpy(float)
    dates = sub_df["sess"]
    b = dd_battery(dates, net, label=label)
    ci = session_block_bootstrap(net, sharpe_stat)
    b["sharpe_ci_lo"] = ci["ci_lo"]
    b["sharpe_ci_hi"] = ci["ci_hi"]
    b["sharpe_boot_mean"] = ci.get("boot_mean", np.nan)
    b["sharpe_ci_n_boot"] = ci["n_boot"]
    b["sharpe_ci_too_thin"] = ci["TOO_THIN"]
    # rename CDaR5 (worst-5%-mean-drawdown, dd_battery's own field name) to CDaR95 to match
    # the panel's requested nomenclature -- SAME number, alpha=0.95 convention (worst 5% tail)
    b["CDaR95"] = b.pop("CDaR5")
    b["n_sessions"] = len(sub_df)
    b["date_min"] = str(dates.min().date())
    b["date_max"] = str(dates.max().date())
    return b


def slice_df(df, lo=None, hi=None):
    d = df
    if lo is not None:
        d = d[d["sess"] >= lo]
    if hi is not None:
        d = d[d["sess"] <= hi]
    return d


print("\n" + "=" * 100)
print("SECTION 1: FULL HISTORY (canonical, 2022-01-03 .. 2026-05-29), with Sharpe bootstrap CI")
print("=" * 100)
sec1_rows = []
for c in CANDIDATES:
    sub = slice_df(daily[c], hi=CANONICAL_END)
    b = battery_with_ci(sub, f"{c}_full_history_canonical")
    b["candidate"] = c
    sec1_rows.append(b)
    print(f"[sec1] {c}: n={b['n_sessions']} net=${b['net']:,.2f} sharpe={b['sharpe']:.4f} "
          f"CI95=[{b['sharpe_ci_lo']:.4f},{b['sharpe_ci_hi']:.4f}] sortino={b['sortino']:.4f} "
          f"calmar={b['calmar']:.4f} maxDD_eod=${b['maxDD_eod']:,.2f} CDaR95=${b['CDaR95']:,.2f}",
          flush=True)
sec1 = pd.DataFrame(sec1_rows)
sec1.to_csv(os.path.join(OUT, "01_full_history_canonical.csv"), index=False)


print("\n" + "=" * 100)
print("SECTION 2: 2022-2025-ONLY (LOYO/wash-test slice)")
print("=" * 100)
sec2_rows = []
for c in CANDIDATES:
    sub = slice_df(daily[c], hi=pd.Timestamp("2025-12-31"))
    b = battery_with_ci(sub, f"{c}_2022_2025")
    b["candidate"] = c
    sec2_rows.append(b)
    print(f"[sec2] {c}: n={b['n_sessions']} net=${b['net']:,.2f} sharpe={b['sharpe']:.4f} "
          f"CI95=[{b['sharpe_ci_lo']:.4f},{b['sharpe_ci_hi']:.4f}]", flush=True)
sec2 = pd.DataFrame(sec2_rows)
sec2.to_csv(os.path.join(OUT, "02_2022_2025_only.csv"), index=False)
ctrl_net_2225 = sec2.loc[sec2.candidate == "CONTROL", "net"].iloc[0]
for c in ["F0.5", "F0.7"]:
    d = sec2.loc[sec2.candidate == c, "net"].iloc[0] - ctrl_net_2225
    print(f"[sec2] {c} delta vs CONTROL (2022-2025, genuine MNQ) = ${d:,.2f} "
          f"({d/ctrl_net_2225*100:.4f}%)", flush=True)


print("\n" + "=" * 100)
print("SECTION 3: 2026 RESEARCH-CONSUMED (Jan-May canonical + Jun-Jul health-only extension)")
print("=" * 100)
sec3_rows = []
for c in CANDIDATES:
    sub_canon = slice_df(daily[c], lo=pd.Timestamp("2026-01-01"), hi=CANONICAL_END)
    sub_ext = slice_df(daily[c], lo=EXT_START, hi=HEALTH_END)
    sub_combined = slice_df(daily[c], lo=pd.Timestamp("2026-01-01"), hi=HEALTH_END)
    for label, sub in [("2026_canonical_JanMay", sub_canon),
                        ("2026_health_only_ext_JunJul", sub_ext),
                        ("2026_combined_research_consumed", sub_combined)]:
        b = battery_with_ci(sub, f"{c}_{label}")
        b["candidate"] = c
        b["segment"] = label
        sec3_rows.append(b)
        print(f"[sec3] {c} {label}: n={b['n_sessions']} net=${b['net']:,.2f} "
              f"sharpe={b['sharpe']:.4f} CI95=[{b['sharpe_ci_lo']:.4f},{b['sharpe_ci_hi']:.4f}] "
              f"too_thin={b['sharpe_ci_too_thin']}", flush=True)
sec3 = pd.DataFrame(sec3_rows)
sec3.to_csv(os.path.join(OUT, "03_2026_consumed.csv"), index=False)


print("\n" + "=" * 100)
print("SECTION 4: YEAR-BY-YEAR (reuse u6b_mnq_year_by_year.csv, ADD bootstrap CI per year)")
print("=" * 100)
yby = pd.read_csv(os.path.join(OUT_IN, "u6b_mnq_year_by_year.csv"))
print(f"[sec4] loaded existing {os.path.join(OUT_IN, 'u6b_mnq_year_by_year.csv')}: "
      f"{len(yby)} rows (reused verbatim, not recomputed)", flush=True)
sec4_ci = []
for c in CANDIDATES:
    for y in [2022, 2023, 2024, 2025, 2026]:
        if y == 2026:
            sub = slice_df(daily[c], lo=pd.Timestamp("2026-01-01"), hi=CANONICAL_END)
        else:
            sub = slice_df(daily[c], lo=pd.Timestamp(f"{y}-01-01"), hi=pd.Timestamp(f"{y}-12-31"))
        net = sub["net"].to_numpy(float)
        ci = session_block_bootstrap(net, sharpe_stat)
        row = {"candidate": c, "year": y, "n_sessions": len(sub),
               "sharpe_point_recomputed": ci["point"], "sharpe_ci_lo": ci["ci_lo"],
               "sharpe_ci_hi": ci["ci_hi"], "n_boot": ci["n_boot"],
               "too_thin_for_meaningful_ci": (len(sub) < 130),  # ~half a normal year of sessions
               "note": ("2026 is a PARTIAL year (Jan-May canonical only, ~106 sessions vs "
                        "~258 for a full year) -- CI is real but visibly wider/noisier than "
                        "the four full years; treat as lower-precision, not invalid."
                        if y == 2026 else "")}
        sec4_ci.append(row)
        print(f"[sec4] {c} {y}: n={len(sub)} sharpe={ci['point']:.4f} "
              f"CI95=[{ci['ci_lo']:.4f},{ci['ci_hi']:.4f}]", flush=True)
sec4_ci_df = pd.DataFrame(sec4_ci)
sec4_ci_df.to_csv(os.path.join(OUT, "04_year_by_year_bootstrap_ci.csv"), index=False)
yby.to_csv(os.path.join(OUT, "04_year_by_year_reused.csv"), index=False)


print("\n" + "=" * 100)
print("SECTION 5: QUARTER-BY-QUARTER (canonical window, NEW cut, computed directly)")
print("=" * 100)
sec5_rows = []
for c in CANDIDATES:
    sub = slice_df(daily[c], hi=CANONICAL_END).copy()
    sub["q"] = sub["sess"].dt.to_period("Q")
    for q, g in sub.groupby("q"):
        net = g["net"].to_numpy(float)
        sharpe = sharpe_stat(net)
        ci = session_block_bootstrap(net, sharpe_stat) if len(g) >= 30 else None
        # "partial" = genuinely truncated relative to a normal ~60-66-session quarter (i.e. the
        # canonical cutoff lands mid-quarter). NOT flagged merely because the calendar quarter's
        # first/last calendar day is a weekend/holiday (every quarter has that, it is not a
        # data gap) -- only true count-shortfall counts.
        is_partial = len(g) < 55
        row = {"candidate": c, "quarter": str(q), "n_sessions": len(g),
               "net": float(net.sum()), "sharpe": sharpe,
               "sharpe_ci_lo": ci["ci_lo"] if ci else np.nan,
               "sharpe_ci_hi": ci["ci_hi"] if ci else np.nan,
               "date_min": str(g["sess"].min().date()), "date_max": str(g["sess"].max().date()),
               "possibly_partial_quarter": bool(is_partial)}
        sec5_rows.append(row)
sec5 = pd.DataFrame(sec5_rows).sort_values(["candidate", "quarter"]).reset_index(drop=True)
sec5.to_csv(os.path.join(OUT, "05_quarter_by_quarter.csv"), index=False)
print(f"[sec5] {len(sec5)} candidate-quarter rows written "
      f"({sec5['quarter'].nunique()} distinct quarters x {len(CANDIDATES)} candidates)", flush=True)
print(sec5[sec5.candidate == "CONTROL"][["quarter", "n_sessions", "net", "sharpe",
                                          "possibly_partial_quarter"]].to_string(index=False))


print("\n" + "=" * 100)
print("SECTION 6: LOYO (leave-one-year-out, 2022-2025)")
print("=" * 100)
# 6a: reuse the existing full-4-year genuine-MNQ delta as a cross-check
recon = json.load(open(os.path.join(OUT_IN, "u6b_mnq_repricing_recon.json")))
recon_delta = {d["candidate"]: d for d in recon["delta_2022_2025_vs_control"]}
print("[sec6] cross-check against u6b_mnq_repricing_recon.json's own full-2022-2025 "
      "genuine-MNQ delta (reused, not recomputed):")
for c in ["F0.5", "F0.7"]:
    print(f"       {c}: genuine_delta_2022_2025 = ${recon_delta[c]['genuine_delta_2022_2025']:,.2f} "
          f"({recon_delta[c]['genuine_delta_pct']:.4f}%)")

full_2225 = {c: slice_df(daily[c], hi=pd.Timestamp("2025-12-31"))["net"].sum() for c in CANDIDATES}
print(f"[sec6] own recomputation of the same full-4-year net (sanity match): "
      f"CONTROL=${full_2225['CONTROL']:,.2f} F0.5=${full_2225['F0.5']:,.2f} "
      f"F0.7=${full_2225['F0.7']:,.2f}")
for c in ["F0.5", "F0.7"]:
    own_delta = full_2225[c] - full_2225["CONTROL"]
    match = abs(own_delta - recon_delta[c]["genuine_delta_2022_2025"]) < 1.0
    print(f"       {c}: own_delta=${own_delta:,.2f} vs recon=${recon_delta[c]['genuine_delta_2022_2025']:,.2f} "
          f"[{'MATCH' if match else 'MISMATCH'}]")
    assert match, f"LOYO cross-check mismatch for {c}"

# 6b: NEW -- drop each year individually, recompute delta on the remaining 3 years
sec6_rows = []
sec6_rows.append({"dropped_year": "NONE (full 4yr, cross-check)", "candidate": "F0.5",
                   "net_control": full_2225["CONTROL"], "net_candidate": full_2225["F0.5"],
                   "delta": full_2225["F0.5"] - full_2225["CONTROL"],
                   "delta_pct": (full_2225["F0.5"] - full_2225["CONTROL"]) / full_2225["CONTROL"] * 100,
                   "n_sessions": len(slice_df(daily["CONTROL"], hi=pd.Timestamp("2025-12-31")))})
sec6_rows.append({"dropped_year": "NONE (full 4yr, cross-check)", "candidate": "F0.7",
                   "net_control": full_2225["CONTROL"], "net_candidate": full_2225["F0.7"],
                   "delta": full_2225["F0.7"] - full_2225["CONTROL"],
                   "delta_pct": (full_2225["F0.7"] - full_2225["CONTROL"]) / full_2225["CONTROL"] * 100,
                   "n_sessions": len(slice_df(daily["CONTROL"], hi=pd.Timestamp("2025-12-31")))})

years_2225 = [2022, 2023, 2024, 2025]
for dropped in years_2225:
    keep_years = [y for y in years_2225 if y != dropped]
    masks = {}
    for c in CANDIDATES:
        d = daily[c]
        keep = slice_df(d, hi=pd.Timestamp("2025-12-31"))
        keep = keep[keep["sess"].dt.year.isin(keep_years)]
        masks[c] = keep
    net_ctrl = masks["CONTROL"]["net"].sum()
    n_sess = len(masks["CONTROL"])
    for c in ["F0.5", "F0.7"]:
        net_cand = masks[c]["net"].sum()
        delta = net_cand - net_ctrl
        sec6_rows.append({"dropped_year": dropped, "candidate": c, "net_control": net_ctrl,
                           "net_candidate": net_cand, "delta": delta,
                           "delta_pct": delta / net_ctrl * 100, "n_sessions": n_sess})
        print(f"[sec6] LOYO drop {dropped}: {c} delta vs CONTROL (remaining 3yr, n={n_sess}) = "
              f"${delta:,.2f} ({delta/net_ctrl*100:.4f}%)", flush=True)
sec6 = pd.DataFrame(sec6_rows)
sec6.to_csv(os.path.join(OUT, "06_loyo_delta_vs_control.csv"), index=False)
n_pos = int((sec6[sec6.dropped_year != "NONE (full 4yr, cross-check)"]["delta"] > 0).sum())
n_tot = len(sec6[sec6.dropped_year != "NONE (full 4yr, cross-check)"])
print(f"[sec6] LOYO direction consistency: {n_pos}/{n_tot} drop-one-year cells positive "
      f"(F0.5+F0.7 x 4 dropped years = 8 cells)", flush=True)


print("\n" + "=" * 100)
print("SECTION 7+8: ROLLING 20/60/120/252-SESSION WINDOWS -- distribution + worst observed")
print("=" * 100)
# Computed on the FULL available series (canonical + health-only extension, 2022-01-03 ..
# 2026-07-31) -- explicitly disclosed choice: this captures the most recent evidence (the
# extension) inside the realized-variability picture that answers "how much does a
# same-length future window plausibly vary", consistent with sec32's "high interpretive
# weight on recent evidence". Windows that overlap the extension are flagged separately.
rolling_dist_rows = []
worst_rows = []
per_series_rolling = {}
for c in CANDIDATES:
    d = daily[c].copy()
    s = pd.Series(d["net"].to_numpy(float), index=d["sess"])
    for w in WINDOWS:
        roll_net = s.rolling(w).sum()
        roll_sharpe = s.rolling(w).apply(
            lambda a: (a.mean() / a.std(ddof=1) * np.sqrt(252)) if a.std(ddof=1) > 0 else np.nan,
            raw=True)
        roll_net_v = roll_net.dropna()
        roll_sharpe_v = roll_sharpe.dropna()
        per_series_rolling[(c, w, "net")] = roll_net_v
        per_series_rolling[(c, w, "sharpe")] = roll_sharpe_v

        for metric_name, series in [("net", roll_net_v), ("sharpe", roll_sharpe_v)]:
            overlaps_ext = (series.index > CANONICAL_END)
            pctiles = np.percentile(series.to_numpy(), [0, 25, 50, 75, 100])
            rolling_dist_rows.append({
                "candidate": c, "window": w, "metric": metric_name,
                "n_windows": len(series),
                "n_windows_overlapping_extension": int(overlaps_ext.sum()),
                "min": pctiles[0], "p25": pctiles[1], "median": pctiles[2],
                "p75": pctiles[3], "max": pctiles[4],
            })
            worst_idx = series.idxmin()
            worst_val = series.loc[worst_idx]
            window_start = worst_idx - pd.tseries.offsets.BDay(w - 1)
            # find actual start date (w-1 sessions back) from the series index directly
            pos = series.index.get_loc(worst_idx) if worst_idx in series.index else None
            full_idx = s.index
            end_pos = full_idx.get_loc(worst_idx)
            start_pos = end_pos - w + 1
            start_date = full_idx[start_pos]
            worst_rows.append({
                "candidate": c, "window": w, "metric": metric_name,
                "worst_value": float(worst_val),
                "window_start": str(start_date.date()), "window_end": str(worst_idx.date()),
                "overlaps_extension": bool(worst_idx > CANONICAL_END),
            })
        print(f"[sec7] {c} w={w}: net dist min/p25/med/p75/max = "
              f"{np.percentile(roll_net_v,[0,25,50,75,100]).round(0)}  "
              f"sharpe dist = {np.percentile(roll_sharpe_v,[0,25,50,75,100]).round(3)}", flush=True)

rolling_dist = pd.DataFrame(rolling_dist_rows)
rolling_dist.to_csv(os.path.join(OUT, "07_rolling_window_distributions.csv"), index=False)
worst_df = pd.DataFrame(worst_rows)
worst_df.to_csv(os.path.join(OUT, "08_worst_rolling_windows.csv"), index=False)
print("[sec8] worst rolling windows (Sharpe metric):")
print(worst_df[worst_df.metric == "sharpe"].to_string(index=False))

# save full rolling series for the two most commonly-cited windows (60, 252) for auditability
for w in [60, 252]:
    cols = {}
    for c in CANDIDATES:
        cols[f"{c}_net"] = per_series_rolling[(c, w, "net")]
        cols[f"{c}_sharpe"] = per_series_rolling[(c, w, "sharpe")]
    rw_df = pd.DataFrame(cols)
    rw_df.index.name = "window_end_date"
    rw_df.to_csv(os.path.join(OUT, f"07b_rolling_series_w{w}.csv"))


print("\n" + "=" * 100)
print("SECTION 9+10: TAIL CONCENTRATION + WINNER RETENTION (reuse LEGACY-priced right-tail files)")
print("=" * 100)
top20 = pd.read_csv(os.path.join(OUT_IN, "u6b_righttail_top20_winners.csv"))
bot20 = pd.read_csv(os.path.join(OUT_IN, "u6b_righttail_bottom20_losers.csv"))
print(f"[sec9] LOADED (reused, not recomputed) LEGACY-priced right-tail block files: "
      f"top20 n={len(top20)}, bottom20 n={len(bot20)}. "
      f"KNOWN LIMITATION (disclosed): these two files are LEGACY NQ-proxy pricing, NOT "
      f"genuine-MNQ-repriced -- u6b_mnq_repricing_recon.json's own exposure-path-identity "
      f"finding (price affects fills only, never the scale-up/quality decision) means the "
      f"BLOCK IDENTITIES and bar-count/quality-fraction columns are pricing-invariant and "
      f"trustworthy as-is, but the $ delta columns (F0.5_window_delta/F0.7_window_delta) carry "
      f"legacy fill economics, not genuine-MNQ fill economics. Treated as a minor known "
      f"limitation of this specific reused table, not silently presented as genuine-MNQ truth.")

tail_summary = []
for name, tbl in [("top20_winners", top20), ("bottom20_losers", bot20)]:
    row = {"block_set": name, "n_blocks": len(tbl),
           "total_control_window_pnl": float(tbl["net_pnl_control_block"].sum())}
    for c in ["F0.5", "F0.7"]:
        dcol = f"{c}_window_delta"
        row[f"{c}_total_window_delta"] = float(tbl[dcol].sum())
        row[f"{c}_n_blocks_improved_gt1usd"] = int((tbl[dcol] > 1.0).sum())
        row[f"{c}_n_blocks_damaged_lt_neg1usd"] = int((tbl[dcol] < -1.0).sum())
        row[f"{c}_n_blocks_unchanged"] = int((tbl[dcol].abs() <= 1.0).sum())
        row[f"{c}_mean_frac_quality_low_in_block"] = float(tbl["frac_quality_low_in_block"].mean())
    tail_summary.append(row)
    print(f"[sec9/10] {name}: n_blocks={row['n_blocks']} total_control_pnl="
          f"${row['total_control_window_pnl']:,.2f} | F0.5_delta=${row['F0.5_total_window_delta']:.2f} "
          f"(improved={row['F0.5_n_blocks_improved_gt1usd']}, damaged="
          f"{row['F0.5_n_blocks_damaged_lt_neg1usd']}, unchanged={row['F0.5_n_blocks_unchanged']}) | "
          f"F0.7_delta=${row['F0.7_total_window_delta']:.2f} "
          f"(improved={row['F0.7_n_blocks_improved_gt1usd']}, damaged="
          f"{row['F0.7_n_blocks_damaged_lt_neg1usd']}, unchanged={row['F0.7_n_blocks_unchanged']})",
          flush=True)
tail_df = pd.DataFrame(tail_summary)
tail_df.to_csv(os.path.join(OUT, "09_10_tail_concentration_winner_retention.csv"), index=False)


print("\n" + "=" * 100)
print("SECTION 11: CURRENT-REGIME BEHAVIOR (2026 evidence vs full-history pattern)")
print("=" * 100)
regime_rows = []
for c in ["F0.5", "F0.7"]:
    # full-history-canonical delta vs control
    fh_ctrl = sec1.loc[sec1.candidate == "CONTROL", "net"].iloc[0]
    fh_cand = sec1.loc[sec1.candidate == c, "net"].iloc[0]
    fh_delta = fh_cand - fh_ctrl
    # 2022-2025-only delta vs control (already have as sec2)
    a2225_ctrl = sec2.loc[sec2.candidate == "CONTROL", "net"].iloc[0]
    a2225_cand = sec2.loc[sec2.candidate == c, "net"].iloc[0]
    a2225_delta = a2225_cand - a2225_ctrl
    # 2026 canonical Jan-May delta vs control
    j2026_ctrl = sec3.loc[(sec3.candidate == "CONTROL") & (sec3.segment == "2026_canonical_JanMay"), "net"].iloc[0]
    j2026_cand = sec3.loc[(sec3.candidate == c) & (sec3.segment == "2026_canonical_JanMay"), "net"].iloc[0]
    j2026_delta = j2026_cand - j2026_ctrl
    # extension delta vs control
    ext_ctrl = sec3.loc[(sec3.candidate == "CONTROL") & (sec3.segment == "2026_health_only_ext_JunJul"), "net"].iloc[0]
    ext_cand = sec3.loc[(sec3.candidate == c) & (sec3.segment == "2026_health_only_ext_JunJul"), "net"].iloc[0]
    ext_delta = ext_cand - ext_ctrl
    row = {"candidate": c,
           "full_history_canonical_delta": fh_delta,
           "y2022_2025_delta": a2225_delta,
           "y2026_janmay_canonical_delta": j2026_delta,
           "y2026_health_ext_junjul_delta": ext_delta,
           "sign_2022_2025": "pos" if a2225_delta > 0 else "neg",
           "sign_2026_janmay": "pos" if j2026_delta > 0 else "neg",
           "sign_2026_ext": "pos" if ext_delta > 0 else "neg",
           "consistent_with_2022_2025_sign": (
               (a2225_delta > 0) == (j2026_delta > 0) == (ext_delta > 0))}
    regime_rows.append(row)
    print(f"[sec11] {c}: 2022-2025 delta=${a2225_delta:,.2f} | 2026 Jan-May delta=${j2026_delta:,.2f} "
          f"| 2026 Jun-Jul(ext) delta=${ext_delta:,.2f} | "
          f"consistent_sign={row['consistent_with_2022_2025_sign']}", flush=True)
regime_df = pd.DataFrame(regime_rows)
regime_df.to_csv(os.path.join(OUT, "11_current_regime_comparison.csv"), index=False)


print("\n" + "=" * 100)
print("BONUS SECTION: PO2 owner-utility (J/CE_g/P_ruin) + leverage_curve sweep, canonical window")
print("=" * 100)
# Existing owner-utility infra (reuse, per shared context): primary_objective_v2 (PO2),
# calling convention identical to runs/O2_OWNER_UTILITY_READJUDICATION/src/01_dry_run_and_score.py.
# PO2's own load_daily_pnl enforces dev_window truncation at DEV_END=2026-05-29 (== our canonical
# cutoff) and raises on any date >= LOCKED_FORWARD_START=2026-08-01 -- a SECOND, independent
# absolute-rule gate on top of this script's own assertion above.
po2_rows = []
po2_full_results = {}
for c in CANDIDATES:
    sub = slice_df(daily[c], hi=CANONICAL_END)
    s = pd.Series(sub["net"].to_numpy(float), index=sub["sess"])
    res = PO2.primary_objective(s, capital=100_000.0, leverage=1.0,
                                 leverage_mode="fixed_fraction", label=f"U6B_{c}_genuineMNQ_canonical")
    prim = res["primary"]
    po2_full_results[c] = res
    row = {"candidate": c, "capital": 100_000.0, "leverage": 1.0,
           "J_mixture": prim["objective_J"], "J_gamma_minimax": prim["J_worst_over_methods"],
           "CE_g_mixture_ann": prim["ce_log_growth_ann"], "P_ruin_mixture": prim["p_ruin"],
           "model_determined_sign": prim["model_determined_sign"],
           "lambda_ruin_per_yr": prim["lambda_ruin_per_yr"]}
    po2_rows.append(row)
    verdict = "INCONCLUSIVE(model-determined sign)" if prim["model_determined_sign"] else (
        "POSITIVE" if prim["objective_J"] > 0 else "NEGATIVE")
    print(f"[po2] {c}: J_mixture={prim['objective_J']:.4f} J_worst={prim['J_worst_over_methods']:.4f} "
          f"CE_g={prim['ce_log_growth_ann']:.4f}/yr P_ruin={prim['p_ruin']:.4f} "
          f"verdict={verdict}", flush=True)
    with open(os.path.join(OUT, f"po2_{c}_full_result.json"), "w") as f:
        json.dump(res, f, indent=2, default=str)
po2_df = pd.DataFrame(po2_rows)
po2_df.to_csv(os.path.join(OUT, "12_po2_owner_utility.csv"), index=False)

print("\n[po2] leverage_curve sweep (J/CE_g/P_ruin shape over L in default grid), per candidate:")
lev_rows = []
for c in CANDIDATES:
    sub = slice_df(daily[c], hi=CANONICAL_END)
    s = pd.Series(sub["net"].to_numpy(float), index=sub["sess"])
    lc = PO2.leverage_curve(s, capital=100_000.0)
    lc["candidate"] = c
    lev_rows.append(lc)
    print(f"[po2-lev] {c}:")
    print(lc[["leverage", "J", "ce_log_growth_ann", "p_ruin_daily_close"]].to_string(index=False))
lev_df = pd.concat(lev_rows, ignore_index=True)
lev_df.to_csv(os.path.join(OUT, "12b_po2_leverage_curve.csv"), index=False)


# ============================================================================================
# consolidated JSON for report authoring
# ============================================================================================
consolidated = {
    "generated_by": "runs/U6B_PRODUCT_A_SCALE_RATE/forward_readiness/src/01_build_panel.py",
    "seed": SEED, "n_boot": N_BOOT,
    "canonical_end": str(CANONICAL_END.date()), "ext_start": str(EXT_START.date()),
    "health_end": str(HEALTH_END.date()), "locked_forward_start": str(LOCKED_FORWARD_START.date()),
    "sec1_full_history": sec1.to_dict(orient="records"),
    "sec2_2022_2025": sec2.to_dict(orient="records"),
    "sec3_2026_consumed": sec3.to_dict(orient="records"),
    "sec6_loyo": sec6.to_dict(orient="records"),
    "sec9_10_tail": tail_df.to_dict(orient="records"),
    "sec11_regime": regime_df.to_dict(orient="records"),
    "po2_owner_utility": po2_df.to_dict(orient="records"),
}
with open(os.path.join(OUT, "00_consolidated_panel.json"), "w") as f:
    json.dump(consolidated, f, indent=2, default=str)

print("\n\nDONE. All outputs written to", OUT)
