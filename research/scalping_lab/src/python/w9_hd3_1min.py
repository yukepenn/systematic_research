"""W9-2 — H-D3 @1min: the ONE reserved reconstruction (LAST permitted H-D3 test).

Frozen spec: research/scalping_lab/specs/W9_nq_minute_resolutions.md (frozen at
d7dfdad before readout; the decay amendment leaves W9-2 unchanged). Original
terms: specs/W1-4_HD3_cashclose_window.md + artifacts/hd3/hd3_report.md.

Frozen construction (exact, DoF already charged at W1-4):
- predictor = 15:50->15:55 return: the 15:55-stamped 1-min close minus the
  15:50-stamped 1-min close (bars END-stamped, exchange ET);
- target = 15:55->16:00: the 16:00-stamped close minus the 15:55-stamped close;
- trade sign(predictor) at the 15:55 close, exit at the 16:00 close;
- friction C1 = 2.872 ticks/RT (BBO_EXEC unavailable on minute data — C1 stands
  per Amendment 3). NQ tick = 0.25 pt = $5.
- PRIMARY window 2022-01 -> 2026-05 (comparability with the 3-min readout);
  SECONDARY full 2006 -> 2026-05 (context + trend; NT8 cache starts 2006-01-05).
- Frozen verdict (PRIMARY window only): significant iff OLS slope (HC1) t >= 2
  AND net C1 > 0 with day-clustered bootstrap CI_lo > 0.
  Whatever the outcome, H-D3 is FINAL after this test.

Contamination rule: dev window ends 2026-05-31 — rows stamped >= 2026-06-01 are
dropped at load before any analysis (holdout June/July 2026 was never exported).

Roll caution (per W5-B1 convention): the substrate is a back-adjusted merge.
The 15:50->16:00 window never spans a session boundary, so no roll adjustment
can land inside it, but days with |pred| or |target| > 8 sigma (full-sample) are
flagged and headline stats are reported with AND without them. Verdict is on ALL
days (the frozen rule names no exclusion).

Seed 20260808; 1000 bootstrap reps; day-clustered (one day = one cluster).
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import binomtest

ROOT = Path(__file__).resolve().parents[4]  # systematic_research/
BARS_PARQUET = ROOT / "research" / "scalping_lab" / "substrate" / "minute" / "NQ" / "nq1m_2005_202605.parquet"
SOLAR_CSV = ROOT / "runs" / "E10MASTER_V2" / "out" / "daily_v1_v2.csv"
ART = ROOT / "research" / "scalping_lab" / "artifacts" / "w9_hd3"

DEV_CUTOFF = pd.Timestamp("2026-06-01 00:00:00")  # exchange ET, exclusive
PRIMARY_START = pd.Timestamp("2022-01-01")
SEED = 20260808
N_BOOT = 1_000
C1_T = 2.872          # ticks per round trip
TICKS_PER_PT = 4.0
USD_PER_TICK = 5.0
OUTLIER_SIGMA = 8.0

STAMPS = {"15:50": "p1550", "15:55": "p1555", "16:00": "p1600"}


class Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, s):
        for st in self.streams:
            st.write(s)

    def flush(self):
        for st in self.streams:
            st.flush()


def boot_ci(x: np.ndarray, rng: np.random.Generator, n_boot: int = N_BOOT):
    """Day-clustered 95% percentile CI on the mean: each day is one cluster;
    resample days with replacement."""
    x = np.asarray(x, dtype=float)
    n = len(x)
    if n == 0:
        return np.nan, np.nan, np.nan
    if n == 1:
        return float(x[0]), np.nan, np.nan
    idx = rng.integers(0, n, size=(n_boot, n))
    means = x[idx].mean(axis=1)
    return float(x.mean()), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def ols_hc1(y: np.ndarray, x: np.ndarray):
    """OLS y = a + b*x with HC1 (day-robust; one obs per day) slope t-stat."""
    if len(y) < 3:
        return np.nan, np.nan
    X = sm.add_constant(np.asarray(x, dtype=float))
    res = sm.OLS(np.asarray(y, dtype=float), X).fit(cov_type="HC1")
    return float(res.params[1]), float(res.tvalues[1])


def sign_agreement(pred: np.ndarray, tgt: np.ndarray):
    """Share of days with sign(tgt) == sign(pred) among days where both are
    nonzero; two-sided binomial p vs 0.5."""
    m = (pred != 0) & (tgt != 0)
    n = int(m.sum())
    if n == 0:
        return np.nan, np.nan, 0
    k = int((np.sign(pred[m]) == np.sign(tgt[m])).sum())
    p = binomtest(k, n, 0.5, alternative="two-sided").pvalue
    return k / n, float(p), n


def group_stats(name, sub: pd.DataFrame, rng: np.random.Generator):
    net = sub["net_t"].values
    gross = sub["gross_t"].values
    mean_net, lo, hi = boot_ci(net, rng)
    slope, t = ols_hc1(sub["tgt_t"].values, sub["pred_t"].values)
    agree, p_agree, n_agree = sign_agreement(sub["pred_t"].values, sub["tgt_t"].values)
    traded = sub["pred_t"].values != 0
    return {
        "group": name,
        "n_days": len(sub),
        "n_traded": int(traded.sum()),
        "slope": slope,
        "t_HC1": t,
        "sign_agree": agree,
        "p_sign": p_agree,
        "gross_mean_t": float(np.mean(gross)) if len(gross) else np.nan,
        "net_mean_t": mean_net,
        "net_ci_lo": lo,
        "net_ci_hi": hi,
        "hit_rate_traded": float(np.mean(net[traded] > 0)) if traded.any() else np.nan,
        "std_gross_t": float(np.std(gross, ddof=1)) if len(gross) > 1 else np.nan,
    }


def print_table(title, rows):
    df = pd.DataFrame(rows)
    print(f"\n--- {title} ---")
    print(df.to_string(index=False,
                       float_format=lambda v: f"{v:.4f}" if pd.notna(v) else "nan"))
    return df


def main():
    ART.mkdir(parents=True, exist_ok=True)

    print("=" * 78)
    print("W9-2  H-D3 @ 1-min — the ONE reserved reconstruction (FINAL H-D3 test)")
    print("Spec: specs/W9_nq_minute_resolutions.md frozen at d7dfdad (amendment: W9-2 unchanged)")
    print("=" * 78)

    # ---- Load 1-min bars; enforce contamination rule immediately at load ----
    df = pd.read_parquet(BARS_PARQUET, columns=["time", "close"])
    n_raw = len(df)
    # time is stored as string; keep only the three stamps we need BEFORE parsing
    hhmm = df["time"].str.slice(11, 16)
    df = df[hhmm.isin(STAMPS.keys())].copy()
    df["stamp"] = hhmm[hhmm.isin(STAMPS.keys())]
    df["time"] = pd.to_datetime(df["time"], format="%Y-%m-%d %H:%M:%S")
    n_pre_cut = len(df)
    df = df[df["time"] < DEV_CUTOFF].reset_index(drop=True)
    print(f"Bars: {n_raw} raw rows; {n_pre_cut} rows carry a 15:50/15:55/16:00 stamp; "
          f"{n_pre_cut - len(df)} dropped at dev cutoff {DEV_CUTOFF} (exclusive); {len(df)} kept.")
    print(f"Kept stamp range: {df['time'].min()} -> {df['time'].max()} (exchange ET, END-stamped)")

    df["date"] = df["time"].dt.normalize()
    dup = df.duplicated(subset=["date", "stamp"]).sum()
    if dup:
        print(f"WARNING: {dup} duplicated (date,stamp) rows — keeping the last of each.")
        df = df.drop_duplicates(subset=["date", "stamp"], keep="last")

    wide = df.pivot(index="date", columns="stamp", values="close").rename(columns=STAMPS)
    n_any = len(wide)
    days = wide.dropna(subset=["p1550", "p1555", "p1600"]).copy()
    print(f"Days with any of the three stamps: {n_any}; with ALL three: {len(days)} "
          f"({n_any - len(days)} dropped: early closes / missing minutes).")

    # ---- Frozen construction ----
    days["pred_t"] = (days["p1555"] - days["p1550"]) * TICKS_PER_PT
    days["tgt_t"] = (days["p1600"] - days["p1555"]) * TICKS_PER_PT
    days["sign"] = np.sign(days["pred_t"])
    days["gross_t"] = days["sign"] * days["tgt_t"]
    days["net_t"] = np.where(days["sign"] != 0, days["gross_t"] - C1_T, 0.0)
    days["net_usd"] = days["net_t"] * USD_PER_TICK
    days = days.reset_index()
    days["year"] = days["date"].dt.year

    n_zero = int((days["sign"] == 0).sum())
    print(f"\nDays formed: {len(days)}  ({days['date'].min().date()} -> {days['date'].max().date()})")
    print(f"Zero-predictor days (15:55 close == 15:50 close -> NO trade, no friction): "
          f"{n_zero} ({n_zero / len(days):.2%})")

    # ---- Roll/outlier detector (W5-B1 convention; diagnostics only) ----
    sig_p = days["pred_t"].std(ddof=1)
    sig_t = days["tgt_t"].std(ddof=1)
    days["outlier_8sig"] = (days["pred_t"].abs() > OUTLIER_SIGMA * sig_p) | \
                           (days["tgt_t"].abs() > OUTLIER_SIGMA * sig_t)
    out_rows = days[days["outlier_8sig"]]
    print(f"\nFull-sample sigma: pred {sig_p:.2f} t, target {sig_t:.2f} t; "
          f"8-sigma thresholds {OUTLIER_SIGMA * sig_p:.0f} t / {OUTLIER_SIGMA * sig_t:.0f} t")
    print(f"Outlier days flagged (|pred| or |tgt| > 8 sigma): {len(out_rows)} "
          f"(the 15:50->16:00 window never spans a session boundary, so these are "
          f"prints, not roll gaps — flagged for robustness only)")
    for _, r in out_rows.iterrows():
        print(f"    {r['date'].date()}: pred {r['pred_t']:+.0f} t, tgt {r['tgt_t']:+.0f} t, "
              f"net {r['net_t']:+.0f} t")

    prim = days[days["date"] >= PRIMARY_START]
    sec = days  # full 2006+ window

    rng = np.random.default_rng(SEED)  # ONE rng, fixed evaluation order

    # =================== PRIMARY window: 2022-01 -> 2026-05 ===================
    rows_p = [group_stats("PRIMARY 2022-01->2026-05 (ALL days)", prim, rng),
              group_stats("PRIMARY excl. 8-sigma outliers", prim[~prim["outlier_8sig"]], rng)]
    for y in sorted(prim["year"].unique()):
        rows_p.append(group_stats(f"year {y}", prim[prim["year"] == y], rng))
    rows_p.append(group_stats("era 2022-23", prim[prim["year"] <= 2023], rng))
    rows_p.append(group_stats("era 2024-26", prim[prim["year"] >= 2024], rng))
    df_p = print_table(f"PRIMARY window — per-day stats (ticks), day-clustered 95% bootstrap CI, "
                       f"{N_BOOT} reps, seed {SEED}", rows_p)

    # =================== SECONDARY window: 2006+ -> 2026-05 ===================
    rows_s = [group_stats("SECONDARY 2006+->2026-05 (ALL days)", sec, rng),
              group_stats("SECONDARY excl. 8-sigma outliers", sec[~sec["outlier_8sig"]], rng)]
    for y in sorted(sec["year"].unique()):
        rows_s.append(group_stats(f"year {y}", sec[sec["year"] == y], rng))
    blocks = [(2006, 2009), (2010, 2013), (2014, 2017), (2018, 2021), (2022, 2026)]
    for a, b in blocks:
        rows_s.append(group_stats(f"block {a}-{b}",
                                  sec[(sec["year"] >= a) & (sec["year"] <= b)], rng))
    df_s = print_table("SECONDARY window (2006+) — same table", rows_s)

    # Trend context (amendment spirit; NOT part of the W9-2 verdict): daily net
    # regressed on time (years since start), HC1.
    tyears = (sec["date"] - sec["date"].min()).dt.days / 365.25
    tr_slope, tr_t = ols_hc1(sec["net_t"].values, tyears.values)
    print(f"\nTrend context (secondary, NOT in verdict): daily net_t on years-since-2006 "
          f"slope {tr_slope:+.4f} t/yr (HC1 t = {tr_t:.2f})")

    # ---- Solar overlap correlation (diagnostic context only; NOT in the frozen
    # W9-2 verdict — recorded because any Program-B candidacy would need rho) ----
    solar = pd.read_csv(SOLAR_CSV, parse_dates=["sess"])
    solar = solar[solar["sess"] < DEV_CUTOFF]
    j = prim.merge(solar[["sess", "net_v1"]], left_on="date", right_on="sess", how="inner")
    if len(j) >= 3:
        rho = float(np.corrcoef(j["net_usd"], j["net_v1"])[0, 1])
        print(f"\nSolar correlation context (E10MASTER net_v1, {len(j)} overlapping days, "
              f"2022+): pearson rho = {rho:+.4f} (diagnostic only)")
    else:
        rho = np.nan
        print("\nSolar correlation context: insufficient overlap.")

    # =========================== FROZEN VERDICT ===============================
    head = df_p.iloc[0]  # PRIMARY, ALL days
    c_t = head["t_HC1"] >= 2.0
    c_net = head["net_mean_t"] > 0.0
    c_ci = head["net_ci_lo"] > 0.0
    verdict = "SIGNIFICANT" if (c_t and c_net and c_ci) else "NOT SIGNIFICANT"
    print("\n" + "=" * 78)
    print("FROZEN VERDICT RULE (PRIMARY window, ALL days — unchanged from W1-4):")
    print(f"  OLS slope = {head['slope']:+.4f}, HC1 t = {head['t_HC1']:.2f} "
          f"(need >= 2): {'PASS' if c_t else 'FAIL'}")
    print(f"  net C1 mean = {head['net_mean_t']:+.3f} t/day (need > 0): "
          f"{'PASS' if c_net else 'FAIL'}")
    print(f"  day-clustered CI_lo = {head['net_ci_lo']:+.3f} t (need > 0): "
          f"{'PASS' if c_ci else 'FAIL'}")
    print(f"VERDICT: {verdict} — H-D3 is FINAL after this test at ANY resolution.")
    print("=" * 78)

    # ---- Persist artifacts ----
    keep = ["date", "year", "p1550", "p1555", "p1600", "pred_t", "tgt_t", "sign",
            "gross_t", "net_t", "net_usd", "outlier_8sig"]
    daily = days[keep].copy()
    daily["in_primary"] = daily["date"] >= PRIMARY_START
    daily.to_csv(ART / "w9hd3_daily.csv", index=False)
    df_p.to_csv(ART / "w9hd3_summary_primary.csv", index=False)
    df_s.to_csv(ART / "w9hd3_summary_secondary.csv", index=False)
    print(f"\nArtifacts written to {ART.relative_to(ROOT)}: w9hd3_daily.csv, "
          f"w9hd3_summary_primary.csv, w9hd3_summary_secondary.csv, w9hd3_stdout.txt")
    return df_p, df_s, verdict


if __name__ == "__main__":
    ART.mkdir(parents=True, exist_ok=True)
    with open(ART / "w9hd3_stdout.txt", "w", encoding="utf-8") as f:
        sys.stdout = Tee(sys.__stdout__, f)
        try:
            main()
        finally:
            sys.stdout = sys.__stdout__
