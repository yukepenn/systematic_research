"""GENESIS_H4B_LASTHALFHOUR_20260828 — executes spec.yaml EXACTLY (ledger trial G00013).

Signal diagnostic only: does r_open30 predict r_last30 on modern NQ?
No policy, no thresholds, no P&L, no parameter search. Gates L1-L3 on the modern
window only; deep era and conditioning splits are REPORTED diagnostics, never gates.

All numbers in gate_table.txt / diagnostics.txt are printed by this program.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import date, timedelta

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import pyarrow.compute as pc

REPO = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, REPO)

from research_sdk import seal_guard
from research_sdk.null_guard import run_circular_null, verify_null_sensitivity

RUN = os.path.join(REPO, "runs", "GENESIS_H4B_LASTHALFHOUR_20260828")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)

MODERN_PARQUET = os.path.join(REPO, r"runs\SM1M_SUBSTRATE\out\nq_1m_2022_2026.parquet")
DEEP_PARQUET = os.path.join(REPO, r"research\scalping_lab\substrate\minute\NQ\nq1m_2005_202605.parquet")
CAL_DIR = os.path.join(REPO, r"runs\GENESIS_H2_CALENDAR_20260828\out\calendar_artifacts")

TRIAL_ID = "G00013"

# ------------------------------------------------------------------ resolutions FIRST
RESOLUTIONS = """\
GENESIS_H4B_LASTHALFHOUR_20260828 — spec_resolutions.txt
Written by the program BEFORE any affected number is computed. The spec is frozen;
each item below resolves an ambiguity CONSERVATIVELY without altering any frozen clause.

R1  "prior session's 16:00-stamped bar": the immediately preceding session PRESENT in the
    loaded window's data. If that session lacks a 16:00 bar (early close) or does not exist
    (first session of the window), the current session is DROPPED and counted. No skipping
    back to earlier sessions; no reaching before the loaded window.
R2  "session-clustered t": with exactly one observation pair per session, session-clustered
    SEs degenerate to heteroskedasticity-robust SEs. L1 uses HC1 (identical to CR1 with
    singleton clusters); L2 uses the plain sample-SE t of the per-session agreement
    indicator vs 0.5 (identical to singleton-cluster CR1).
R3  sign(): np.sign verbatim. Agreement iff sign(r_open30) == sign(r_last30) exactly; an
    exact-zero return agrees only with an exact-zero return. Zero counts reported.
R4  L3 "above the 95th percentile": STRICT > of np.percentile(null, 95, method='higher')
    (conservative on both choices). n_shifts = 300 distinct nonzero whole-session shifts,
    seed 0, via null_guard.run_circular_null; verify_null_sensitivity runs FIRST with
    shifts [1, 2, 5, 17, 101].
R5  MDE (power_note) = effect size giving t = 2.0 at the observed robust SE:
    slope MDE = 2.0 * SE_HC1(slope); sign-rate MDE = 0.5 + 2.0 * SE(mean indicator).
R6  trailing-21-session RV = mean over the 21 immediately preceding data sessions of the
    per-session realized vol RV_s = sqrt(sum of squared 1-min log close returns over bars
    stamped 09:31:00..16:00:00 within session s). Sessions with < 21 qualifying prior
    sessions (a session qualifies with >= 2 such RTH bars) are excluded from this split
    only, with the exclusion count printed. No lookahead: session s's own RV is excluded.
R7  "announcement days" = sessions in the UNION of H2 certified FOMC_DAY, CPI_DAY, NFP_DAY
    calendars (read-only). Calendar loads pass seal_guard via truncate_presealed (future
    scheduled dates >= 2026-08-01 are dropped with a printed count, never read into use).
R8  Conditioning splits are computed on the MODERN window only (the gate window); era
    comparison = deep 2006-2021 overall plus 4-year blocks. Every conditional row is
    printed next to its same-wave unconditional (ALL) control. All diagnostics REPORTED
    only — no gate reads them.
R9  Terciles: top tercile = conditioning value >= np.percentile(values, 200/3) (linear),
    computed across valid modern pairs.
R10 pairs_series.csv holds BOTH windows with a 'window' column (modern|deep); one row per
    valid pair; sessions as ISO dates.
R11 Window isolation AT LOAD: modern parquet scanned with filter
    2021-12-31 18:00:00 < time <= 2026-07-31 17:00:00 (session labels 2022-01-01..
    2026-07-31; END-stamped close of session 2026-07-31 is 17:00:00); deep parquet scanned
    with lexicographic ISO-string filter '2005-12-31 18:00:00' < time <= '2021-12-31
    17:00:00'. seal_guard.assert_presealed is applied to every loaded market frame after
    the read; calendar CSVs use truncate_presealed with printed counts.
R12 Duplicate bar timestamps inside a loaded window are a DEFECT (assertion fires; nothing
    substituted). Non-positive close prices at any used bar are likewise a DEFECT.
R13 Session label for a bar: END-stamped, exchange-session ET; hour >= 18 rolls to the
    next calendar day's session (runlib/session_boundary convention). Only RTH-stamped
    bars (hour < 18) enter any computed quantity here.
"""
with open(os.path.join(OUT, "spec_resolutions.txt"), "w", encoding="utf-8") as f:
    f.write(RESOLUTIONS)
print("spec_resolutions.txt written (before any affected number was computed)")

LOG = []  # mirrored into diagnostics.txt


def log(msg=""):
    print(msg)
    LOG.append(str(msg))


# ------------------------------------------------------------------ loading
def load_modern() -> pd.DataFrame:
    lo = pd.Timestamp("2021-12-31 18:00:00")
    hi = pd.Timestamp("2026-07-31 17:00:00")  # END-stamped close of session 2026-07-31
    t = pq.read_table(MODERN_PARQUET, columns=["time", "close"],
                      filters=[("time", ">", lo), ("time", "<=", hi)])
    df = t.to_pandas()
    seal_guard.assert_presealed(df, "time", "H4B modern load (window-isolated at scan)")
    log(f"modern load: {len(df):,} bars, window-isolated at parquet scan (> {lo}, <= {hi}); seal ASSERTED clean")
    return df


def load_deep() -> pd.DataFrame:
    t = pq.read_table(DEEP_PARQUET, columns=["time", "close"],
                      filters=[("time", ">", "2005-12-31 18:00:00"),
                               ("time", "<=", "2021-12-31 17:00:00")])
    df = t.to_pandas()
    df["time"] = pd.to_datetime(df["time"], format="%Y-%m-%d %H:%M:%S")
    seal_guard.assert_presealed(df, "time", "H4B deep load (window-isolated at scan)")
    log(f"deep load: {len(df):,} bars, window-isolated at parquet scan (ISO-string filter 2006->2021); seal ASSERTED clean")
    return df


def session_ids(ts: pd.Series) -> pd.Series:
    d = ts.dt.normalize()
    return (d + pd.to_timedelta((ts.dt.hour >= 18).astype(int), unit="D")).dt.date


# ------------------------------------------------------------------ pair construction
def build_pairs(df: pd.DataFrame, label: str):
    assert not df["time"].duplicated().any(), f"DEFECT: duplicate bar timestamps in {label} window"
    df = df.sort_values("time").reset_index(drop=True)
    df["session"] = session_ids(df["time"])
    tod = df["time"].dt.time
    import datetime as _dt
    t1000, t1530, t1600 = _dt.time(10, 0), _dt.time(15, 30), _dt.time(16, 0)

    def grab(t):
        sub = df.loc[tod == t, ["session", "close"]]
        assert not sub["session"].duplicated().any(), f"DEFECT: duplicate {t} bar within a session ({label})"
        return sub.set_index("session")["close"]

    c1000, c1530, c1600 = grab(t1000), grab(t1530), grab(t1600)
    sessions = pd.Index(sorted(df["session"].unique()))
    n_total = len(sessions)
    have = pd.DataFrame(index=sessions)
    have["c1000"], have["c1530"], have["c1600"] = c1000, c1530, c1600
    have["prior_c1600"] = have["c1600"].shift(1)  # immediately preceding data session (R1)

    miss_1000 = int(have["c1000"].isna().sum())
    miss_1530 = int(have["c1530"].isna().sum())
    miss_1600 = int(have["c1600"].isna().sum())
    valid_own = have[["c1000", "c1530", "c1600"]].notna().all(axis=1)
    miss_prior = int((valid_own & have["prior_c1600"].isna()).sum())
    pairs = have.loc[valid_own & have["prior_c1600"].notna()].copy()
    assert (pairs[["c1000", "c1530", "c1600", "prior_c1600"]] > 0).all().all(), \
        f"DEFECT: non-positive close at a used bar ({label})"
    pairs["r_open30"] = pairs["c1000"] / pairs["prior_c1600"] - 1.0
    pairs["r_last30"] = pairs["c1600"] / pairs["c1530"] - 1.0
    pairs = pairs.reset_index().rename(columns={"index": "session"})
    log(f"[{label}] sessions in window: {n_total}; dropped missing 10:00 bar: {miss_1000}, "
        f"missing 15:30 bar: {miss_1530}, missing 16:00 bar: {miss_1600}, "
        f"no usable prior-session 16:00 close: {miss_prior}; valid pairs: {len(pairs)}")
    drops = {"sessions_in_window": n_total, "miss_1000": miss_1000, "miss_1530": miss_1530,
             "miss_1600": miss_1600, "miss_prior_close": miss_prior, "valid_pairs": len(pairs)}
    return pairs[["session", "r_open30", "r_last30"]], drops, df


# ------------------------------------------------------------------ statistics
def ols_hc1(x: np.ndarray, y: np.ndarray):
    n = len(x)
    xc = x - x.mean()
    sxx = float((xc ** 2).sum())
    b = float((xc * y).sum() / sxx)
    a = float(y.mean() - b * x.mean())
    e = y - a - b * x
    se = float(np.sqrt((n / (n - 2)) * float(((xc ** 2) * (e ** 2)).sum()) / sxx ** 2))
    return b, se, b / se


def sign_agree(x: np.ndarray, y: np.ndarray):
    ind = (np.sign(x) == np.sign(y)).astype(float)
    n = len(ind)
    p = float(ind.mean())
    se = float(ind.std(ddof=1) / np.sqrt(n))
    return p, se, (p - 0.5) / se


def row_stats(pairs: pd.DataFrame, name: str) -> str:
    n = len(pairs)
    if n < 3:
        return f"  {name:<38s} N={n:>5d}  (too few for statistics)"
    x, y = pairs["r_open30"].to_numpy(), pairs["r_last30"].to_numpy()
    b, se, t = ols_hc1(x, y)
    p, pse, pt = sign_agree(x, y)
    return (f"  {name:<38s} N={n:>5d}  slope={b:+.5f} (HC1 t={t:+.2f})  "
            f"sign-agree={100*p:.2f}% (t={pt:+.2f})")


# ------------------------------------------------------------------ main
log("=" * 100)
log("GENESIS_H4B_LASTHALFHOUR_20260828 — r_open30 -> r_last30 (Gao/Han/Li/Zhou geometry), trial G00013")
log("=" * 100)

modern_bars = load_modern()
pairs_m, drops_m, modern_bars = build_pairs(modern_bars, "modern 2022-01..2026-07-31")

deep_bars = load_deep()
pairs_d, drops_d, deep_bars = build_pairs(deep_bars, "deep 2006..2021")

x = pairs_m["r_open30"].to_numpy()
y = pairs_m["r_last30"].to_numpy()
n = len(pairs_m)
zeros = int((np.sign(x) == 0).sum() + (np.sign(y) == 0).sum())
log(f"[modern] exact-zero returns among pairs (R3): {zeros} (r_open30: {int((np.sign(x)==0).sum())}, r_last30: {int((np.sign(y)==0).sum())})")

# L1
b, se_b, t_b = ols_hc1(x, y)
l1_pass = (b > 0) and (t_b >= 2.0)
# L2
p_agree, se_p, t_p = sign_agree(x, y)
l2_pass = (p_agree > 0.5) and (t_p >= 2.0)
# MDE (R5)
mde_slope = 2.0 * se_b
mde_rate = 0.5 + 2.0 * se_p
log(f"[modern] power (R5): N={n}; slope MDE @ t=2.0 = {mde_slope:.5f}; sign-rate MDE @ t=2.0 = {100*mde_rate:.2f}%")

# L3 — null_guard, sensitivity FIRST (R4)
frame = pairs_m.copy()
loader = lambda: frame.copy()
decision_fn = lambda f: f["r_open30"].to_numpy()
stat_fn = lambda d, base: ols_hc1(np.asarray(d, dtype=float), base["r_last30"].to_numpy())[0]
sens = verify_null_sensitivity(loader, decision_fn, stat_fn, shifts=[1, 2, 5, 17, 101], unit="session")
log(f"[L3] sensitivity verified: real={sens['real_stat']:+.6f}, spread across probe shifts={sens['spread']:.6f} (null CAN move)")
null = run_circular_null(loader, decision_fn, stat_fn, n_shifts=300, unit="session", seed=0)
null_arr = np.asarray(null["null_stats"], dtype=float)
p95 = float(np.percentile(null_arr, 95, method="higher"))
real_slope = null["real_stat"]
assert abs(real_slope - b) < 1e-12, "DEFECT: null real_stat disagrees with L1 slope"
l3_pass = real_slope > p95
log(f"[L3] {len(null_arr)} whole-session circular shifts (seed 0, {null['n_units']} units); "
    f"null slope p95(method=higher)={p95:+.6f}; real={real_slope:+.6f}; "
    f"real percentile-in-null={100*null['percentile']:.1f}%; p_ge(add-one)={null['p_ge']:.4f}")

verdict = "PASS" if (l1_pass and l2_pass and l3_pass) else "NULL"

# ------------------------------------------------------------------ gate table
W = 118
gt = []
gt.append("GENESIS_H4B_LASTHALFHOUR_20260828 — GATE TABLE (printed by program src/run_h4b.py; nothing hand-assembled)")
gt.append(f"trial {TRIAL_ID} | modern gate window sessions 2022-01-03..2026-07-31 | valid pairs N={n} "
          f"(drops: {drops_m['miss_1000']}/{drops_m['miss_1530']}/{drops_m['miss_1600']} missing 10:00/15:30/16:00 bar, "
          f"{drops_m['miss_prior_close']} no prior 16:00 close, of {drops_m['sessions_in_window']} sessions)")
gt.append("evidence status: DISCOVERY (modern window is research-consumed pre-seal data; no sealed rows read)")
gt.append("-" * W)
gt.append(f"{'GATE':<6}| {'SPEC':<52}| {'OBSERVED':<42}| PASS-FAIL")
gt.append("-" * W)
gt.append(f"{'L1':<6}| {'OLS slope r_last30~r_open30 > 0, clustered t>=2.0':<52}| "
          f"{f'slope={b:+.5f}, HC1 t={t_b:+.2f}':<42}| {'PASS' if l1_pass else 'FAIL'}")
gt.append(f"{'L2':<6}| {'sign-agreement > 50%, clustered t>=2.0':<52}| "
          f"{f'rate={100*p_agree:.2f}%, t={t_p:+.2f}':<42}| {'PASS' if l2_pass else 'FAIL'}")
gt.append(f"{'L3':<6}| {'real slope > p95 of >=300 whole-session circ shifts':<52}| "
          f"{f'real={real_slope:+.5f} vs p95={p95:+.5f} (300 shifts)':<42}| {'PASS' if l3_pass else 'FAIL'}")
gt.append("-" * W)
gt.append(f"VERDICT: {verdict}  (spec: ALL of L1-L3 pass -> PASS; any fail -> NULL at this geometry)")
gt.append(f"power: N={n}; MDE@t=2.0: slope {mde_slope:.5f}, sign-rate {100*mde_rate:.2f}% (R5)")
gate_text = "\n".join(gt)
print()
print(gate_text)
with open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8") as f:
    f.write(gate_text + "\n")

# ------------------------------------------------------------------ diagnostics (REPORTED ONLY)
log("")
log("DIAGNOSTICS — reported only; NO gate reads these; no iteration performed on them")
log("-" * 100)

# conditioning splits, modern window only (R8), each with its same-wave unconditional control
log("[modern conditioning splits]")
log(row_stats(pairs_m, "ALL modern (unconditional control)"))

absx = pairs_m["r_open30"].abs()
cut_abs = float(np.percentile(absx.to_numpy(), 200.0 / 3.0))
top_abs = pairs_m[absx >= cut_abs]
rest_abs = pairs_m[absx < cut_abs]
log(row_stats(top_abs, f"top-tercile |r_open30| (cut={cut_abs:.5f})"))
log(row_stats(rest_abs, "bottom two terciles |r_open30|"))

# trailing-21-session RV (R6) — computed from modern RTH minute bars
import datetime as _dt
rth = modern_bars.loc[(modern_bars["time"].dt.time >= _dt.time(9, 31)) &
                      (modern_bars["time"].dt.time <= _dt.time(16, 0))].copy()
def _rv(g):
    c = g["close"].to_numpy()
    if len(c) < 2:
        return np.nan
    r = np.diff(np.log(c))
    return float(np.sqrt((r ** 2).sum()))
rv = rth.groupby("session", sort=True).apply(_rv, include_groups=False).dropna()
trail = rv.rolling(21).mean().shift(1)  # mean RV of the 21 preceding qualifying sessions, no lookahead
pairs_rv = pairs_m.merge(trail.rename("trail_rv"), left_on="session", right_index=True, how="left")
excl = int(pairs_rv["trail_rv"].isna().sum())
pairs_rv = pairs_rv.dropna(subset=["trail_rv"])
cut_rv = float(np.percentile(pairs_rv["trail_rv"].to_numpy(), 200.0 / 3.0))
log(f"[modern] trailing-21-RV split: {excl} pairs excluded (insufficient trailing history), {len(pairs_rv)} usable")
log(row_stats(pairs_rv, "ALL with trailing-RV defined (control)"))
log(row_stats(pairs_rv[pairs_rv["trail_rv"] >= cut_rv], f"top-tercile trailing-21s RV (cut={cut_rv:.4f})"))
log(row_stats(pairs_rv[pairs_rv["trail_rv"] < cut_rv], "bottom two terciles trailing-21s RV"))

# announcement days (R7) — H2 certified calendars, truncated at seal with printed counts
ann_dates = set()
for nm in ["FOMC_DAY", "CPI_DAY", "NFP_DAY"]:
    cal = pd.read_csv(os.path.join(CAL_DIR, f"daytype_sessions_{nm}.csv"))
    cal["session_date"] = pd.to_datetime(cal["session_date"]).dt.date
    cal, n_dropped = seal_guard.truncate_presealed(cal, "session_date", f"H4B calendar {nm}")
    LOG.append(f"  (calendar {nm}: {len(cal)} sessions kept, {n_dropped} post-seal dropped)")
    ann_dates |= set(cal["session_date"])
is_ann = pairs_m["session"].isin(ann_dates)
log(f"[modern] announcement sessions (FOMC_DAY ∪ CPI_DAY ∪ NFP_DAY) among pairs: {int(is_ann.sum())}")
log(row_stats(pairs_m, "ALL modern (control, repeated)"))
log(row_stats(pairs_m[is_ann], "announcement days"))
log(row_stats(pairs_m[~is_ann], "non-announcement days"))

# era comparison (R8)
log("")
log("[era comparison — deep parquet, diagnostic only, NOT a gate]")
log(row_stats(pairs_d, "deep 2006-2021 (all)"))
sy = pd.Series([s.year for s in pairs_d["session"]])
for lo_y, hi_y in [(2006, 2009), (2010, 2013), (2014, 2017), (2018, 2021)]:
    log(row_stats(pairs_d[(sy >= lo_y).to_numpy() & (sy <= hi_y).to_numpy()], f"deep {lo_y}-{hi_y}"))
log(row_stats(pairs_m, "modern 2022-2026H1 (gate window)"))

with open(os.path.join(OUT, "diagnostics.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(LOG) + "\n")

# ------------------------------------------------------------------ pairs_series.csv (R10)
out_pairs = pd.concat([pairs_m.assign(window="modern"), pairs_d.assign(window="deep")],
                      ignore_index=True)[["window", "session", "r_open30", "r_last30"]]
seal_guard.assert_presealed(out_pairs, "session", "H4B pairs_series.csv pre-write check")
out_pairs.to_csv(os.path.join(OUT, "pairs_series.csv"), index=False)
print(f"pairs_series.csv written: {len(out_pairs)} rows (modern {len(pairs_m)}, deep {len(pairs_d)}); seal-checked")

# ------------------------------------------------------------------ ledger result (pending)
result = {
    "trial_id": TRIAL_ID,
    "metrics": {
        "n_pairs_modern": n,
        "l1_slope": round(b, 6), "l1_t_hc1": round(t_b, 3), "l1_pass": bool(l1_pass),
        "l2_sign_agree_rate": round(p_agree, 5), "l2_t": round(t_p, 3), "l2_pass": bool(l2_pass),
        "l3_real_slope": round(real_slope, 6), "l3_null_p95": round(p95, 6),
        "l3_n_shifts": int(len(null_arr)), "l3_pass": bool(l3_pass),
        "l3_percentile_in_null": round(null["percentile"], 4), "l3_p_ge_addone": round(null["p_ge"], 4),
        "mde_slope_t2": round(mde_slope, 6), "mde_sign_rate_t2": round(mde_rate, 5),
        "n_pairs_deep": len(pairs_d),
        "drops_modern": drops_m, "drops_deep": drops_d,
    },
    "result": verdict,
    "note": ("H4B last-half-hour geometry (r_open30 -> r_last30), modern gate window "
             "2022-01..2026-07-31. Gates L1-L3 coded per frozen spec; deep era and "
             "conditioning splits reported as diagnostics only. Seal asserted clean on "
             "every load; window isolation applied at parquet scan. Spec resolutions "
             "R1-R13 recorded before computation."),
}
with open(os.path.join(OUT, "ledger_result_pending.json"), "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)
print(f"ledger_result_pending.json written — result: {verdict}")
