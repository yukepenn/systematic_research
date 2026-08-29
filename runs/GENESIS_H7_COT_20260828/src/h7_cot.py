"""GENESIS_H7_COT_20260828 - TEAM H7 driver (trial G00014).

Executes runs/GENESIS_H7_COT_20260828/spec.yaml EXACTLY. Every ambiguity resolution
was recorded in out/spec_resolutions.txt (R1-R14) BEFORE this program produced any
state-return number. LOW prior stated in advance; one shot; a FAIL is a FAIL.

STATE (frozen): CROWD(w) = Leveraged Funds net (long - short) / market OI on the
e-mini NASDAQ-100 TFF rows (CFTC code 209742, name-stripped, R1), trailing
156-report causal percentile (window includes current report, R5), fixed terciles
at 1/3 and 2/3 (R6).

CAUSALITY (frozen): as-of Tuesday -> published Friday 15:30 ET (Friday of the as-of
ISO week, R7) -> conditions the ISO week immediately FOLLOWING the publication week
(R8). Target = 100*(cond-week last session close / publication-week last session
close - 1), weekly closes from session closes (END-stamped bars, session label
rolls forward at 18:00 ET), deep+modern substrates, splice return dropped (R9).

GATES (all coded, printed as GATE/SPEC/OBSERVED/PASS-FAIL):
  C1  T3-T1 < 0 AND weekly (Welch two-sample) t <= -2.0          (R11)
  C2  real |T3-T1| > q95 of ALL m-1 circular shifts (>=300) of the state series
      against weekly returns, null_guard sensitivity FIRST        (R12)
  C3  T3-T1 < 0 in BOTH halves (<=2016-12-31 / >=2017-01-01)      (R13)
Dealer / Asset-Manager identical contrasts are NON-GATE diagnostics (R14).

SEAL: every data load passes research_sdk.seal_guard (truncate with printed count
inside the substrate chunk loop; assert everywhere else); no value >= 2026-08-01 is
read, printed or persisted. No parameter search exists in this file.
"""
from __future__ import annotations

import io
import json
import os
import sys

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
OUT = os.path.join(RUN, "out")
ROOT = os.path.abspath(os.path.join(RUN, "..", ".."))
sys.path.insert(0, ROOT)
os.makedirs(OUT, exist_ok=True)

from research_sdk import seal_guard as sg      # noqa: E402
from research_sdk import null_guard            # noqa: E402

COT = os.path.join(ROOT, "runs", "GENESIS_FREEDATA_CBOE_20260828", "certified",
                   "cot_tff_futures_only.parquet")
DEEP = os.path.join(ROOT, "research", "scalping_lab", "substrate", "minute", "NQ",
                    "nq1m_2005_202605.parquet")
MODERN = os.path.join(ROOT, "runs", "SM1M_SUBSTRATE", "out", "nq_1m_2022_2026.parquet")

# ---- FROZEN BY SPEC + RESOLUTIONS (no grid, no search) ----------------------------
WIN_LO = pd.Timestamp("2006-08-01")     # spec window (R2)
WIN_HI = pd.Timestamp("2026-07-31")
MKT_CODE = "209742"                     # e-mini NASDAQ-100 row set (R1)
PCTL_WIN = 156                          # trailing reports, incl current (R5)
T1_CUT, T3_CUT = 1.0 / 3.0, 2.0 / 3.0   # fixed tercile cuts (R6)
HALF_SPLIT = pd.Timestamp("2016-12-31")  # C3: cond-week end <= this = half 1 (R13)
SENS_SHIFTS = [1, 7, 101]               # sensitivity first (R12)
NULL_MIN = 300
NULL_SEED = 20260828
GRID_LO, GRID_HI = pd.Timestamp("2006-01-01"), WIN_HI
DEEP_HI, MODERN_LO = pd.Timestamp("2021-12-31"), pd.Timestamp("2022-01-01")

TEE_GATE = io.StringIO()
TEE_DIAG = io.StringIO()


def p(*a):
    line = " ".join(str(x) for x in a)
    print(line, flush=True)
    TEE_GATE.write(line + "\n")


def pd_(*a):
    line = " ".join(str(x) for x in a)
    print(line, flush=True)
    TEE_DIAG.write(line + "\n")


def num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s.astype(str).str.strip(), errors="raise")   # R3


# ------------------------------------------------------------------ session closes
def session_label(ts: pd.Series) -> pd.Series:
    """END-stamped bar -> session label date (hour >= 18 rolls to next calendar day)."""
    lab = ts.dt.normalize()
    return lab.where(ts.dt.hour < 18, lab + pd.Timedelta(days=1))


def load_session_closes(path, lab_lo, lab_hi, time_is_str, name) -> pd.DataFrame:
    """Chunked load -> one row per session: label, close of last END-stamped bar (R9)."""
    pf = pq.ParquetFile(path)
    parts, total_rows = [], 0
    for i in range(pf.metadata.num_row_groups):
        df = pf.read_row_group(i, columns=["time", "close"]).to_pandas()
        total_rows += len(df)
        ts = pd.to_datetime(df["time"], format="%Y-%m-%d %H:%M:%S") if time_is_str \
            else pd.to_datetime(df["time"])
        chunk = pd.DataFrame({"ts": ts.values, "close": df["close"].values})
        chunk, _nd = sg.truncate_presealed(chunk, "ts", f"{name} rg{i}")
        if len(chunk) == 0:
            continue
        lab = session_label(chunk["ts"])
        keep = (lab >= lab_lo) & (lab <= lab_hi)
        chunk, lab = chunk.loc[keep], lab.loc[keep]
        if len(chunk) == 0:
            continue
        chunk = chunk.assign(label=lab.values)
        idx = chunk.groupby("label")["ts"].idxmax()
        parts.append(chunk.loc[idx, ["label", "ts", "close"]])
    if not parts:
        raise RuntimeError(f"{name}: no rows in window")
    allp = pd.concat(parts, ignore_index=True)
    idx = allp.groupby("label")["ts"].idxmax()          # sessions straddling row groups
    ses = allp.loc[idx].sort_values("label").reset_index(drop=True)
    wd = ses["label"].dt.weekday
    n_wk = int((wd >= 5).sum())
    if n_wk:
        p(f"    {name}: dropped {n_wk} Saturday/Sunday-labeled artifact session(s)")
    ses = ses.loc[wd < 5].reset_index(drop=True)
    sg.assert_presealed(ses, "label", f"{name} session labels")
    sg.assert_presealed(ses, "ts", f"{name} session close timestamps")
    p(f"    {name}: {total_rows:,} bars -> {len(ses):,} sessions "
      f"[{ses['label'].iloc[0].date()} .. {ses['label'].iloc[-1].date()}]")
    return ses[["label", "close"]]


def iso_key_of_dates(d: pd.Series) -> pd.Series:
    iso = d.dt.isocalendar()
    return (iso["year"].astype(int) * 100 + iso["week"].astype(int)).astype(int)


def build_weekly_grid() -> pd.DataFrame:
    """Weekly closes: last session close per ISO week, per substrate; splice at 2022 (R9)."""
    deep = load_session_closes(DEEP, GRID_LO, DEEP_HI, True, "deep")
    modern = load_session_closes(MODERN, MODERN_LO, GRID_HI, False, "modern")
    deep["substrate"], modern["substrate"] = "deep", "modern"
    ses = pd.concat([deep, modern], ignore_index=True).sort_values("label").reset_index(drop=True)
    assert ses["label"].is_unique, "duplicate session labels across substrates"
    ses["iso_key"] = iso_key_of_dates(ses["label"])
    gb = ses.groupby("iso_key", sort=True)
    wk = pd.DataFrame({
        "iso_key": gb.size().index,
        "week_start_label": gb["label"].min().values,
        "week_end_label": gb["label"].max().values,
        "close": gb.apply(lambda g: g.loc[g["label"].idxmax(), "close"]).values,
        "substrate": gb.apply(lambda g: g.loc[g["label"].idxmax(), "substrate"]).values,
        "n_sessions": gb.size().values,
    }).sort_values("week_end_label").reset_index(drop=True)
    assert wk["iso_key"].is_unique and wk["week_end_label"].is_monotonic_increasing
    assert (wk["iso_key"].values == np.sort(wk["iso_key"].values)).all(), \
        "iso_key order != week_end order"
    sg.assert_presealed(wk, "week_end_label", "weekly grid ends")
    p(f"    weekly grid: {len(wk)} ISO weeks "
      f"[{wk['week_end_label'].iloc[0].date()} .. {wk['week_end_label'].iloc[-1].date()}]"
      f"  (splice: last deep week {deep['label'].max().date()}, "
      f"first modern week-end {modern['label'].min().date()}-anchored)")
    return wk


# ------------------------------------------------------------------ COT state
def load_cot() -> pd.DataFrame:
    df = pd.read_parquet(COT)
    sg.assert_presealed(df, "report_date", "certified COT TFF full frame")
    code = df["CFTC_Contract_Market_Code"].str.strip()
    g = df[code == MKT_CODE].copy()                                   # R1
    g["mkt"] = g["Market_and_Exchange_Names"].str.strip()             # trailing-space fix
    g = g.sort_values("report_date").reset_index(drop=True)
    assert g["report_date"].is_unique, "duplicate report dates in chosen row set"
    n_full = len(g)
    g = g[(g["report_date"] >= WIN_LO) & (g["report_date"] <= WIN_HI)].reset_index(drop=True)  # R2
    sg.assert_presealed(g, "report_date", "COT chosen rows in window")
    names = sorted(g["mkt"].unique())
    p(f"    COT rows: code {MKT_CODE} full set {n_full}, in window {len(g)} "
      f"[{g['report_date'].iloc[0].date()} .. {g['report_date'].iloc[-1].date()}]")
    p(f"    vendor names in set (stripped): {names}")
    for cat, L, S in [("lev", "Lev_Money_Positions_Long_All", "Lev_Money_Positions_Short_All"),
                      ("dealer", "Dealer_Positions_Long_All", "Dealer_Positions_Short_All"),
                      ("am", "Asset_Mgr_Positions_Long_All", "Asset_Mgr_Positions_Short_All")]:
        g[f"{cat}_long"], g[f"{cat}_short"] = num(g[L]), num(g[S])
    g["oi"] = num(g["Open_Interest_All"])
    assert (g["oi"] > 0).all(), "nonpositive OI in chosen row set"
    return g[["report_date", "mkt", "oi", "lev_long", "lev_short",
              "dealer_long", "dealer_short", "am_long", "am_short"]]


def trailing_pct(v: np.ndarray) -> np.ndarray:
    """pct(i) = #{v[i-155..i] <= v[i]} / 156, NaN for warmup (R5)."""
    n = len(v)
    out = np.full(n, np.nan)
    for i in range(PCTL_WIN - 1, n):
        w = v[i - PCTL_WIN + 1: i + 1]
        out[i] = np.sum(w <= v[i]) / PCTL_WIN
    return out


def terciles(pct: np.ndarray) -> np.ndarray:
    """1/2/3 by fixed cuts; 0 = undefined (warmup) (R6)."""
    t = np.zeros(len(pct), dtype=int)
    ok = np.isfinite(pct)
    t[ok & (pct <= T1_CUT)] = 1
    t[ok & (pct > T1_CUT) & (pct <= T3_CUT)] = 2
    t[ok & (pct > T3_CUT)] = 3
    return t


def welch(a: np.ndarray, b: np.ndarray):
    """diff = mean(a)-mean(b), Welch t. Each element = one week = one cluster (R11)."""
    n1, n0 = len(a), len(b)
    d = a.mean() - b.mean()
    se = np.sqrt(a.var(ddof=1) / n1 + b.var(ddof=1) / n0)
    return d, se, d / se, n1, n0


def contrast(frame: pd.DataFrame, tcol: str):
    a = frame.loc[frame[tcol] == 3, "ret"].to_numpy(float)
    b = frame.loc[frame[tcol] == 1, "ret"].to_numpy(float)
    return welch(a, b)


# ------------------------------------------------------------------ main
def main():
    p("=" * 100)
    p("GENESIS_H7_COT_20260828 - COT TFF positioning crowding vs next-week NQ (trial G00014)")
    p("spec frozen; resolutions R1-R14 recorded in out/spec_resolutions.txt BEFORE any number below")
    p("=" * 100)

    p("\n--- 1. NQ weekly grid (session closes; deep+modern; splice return dropped) ---")
    wk = build_weekly_grid()
    wk_idx = {k: i for i, k in enumerate(wk["iso_key"].tolist())}

    p("\n--- 2. COT state (e-mini NASDAQ-100, Leveraged Funds net / OI) ---")
    cot = load_cot()
    n_reports = len(cot)
    wd = cot["report_date"].dt.weekday
    n_shifted = int((wd != 1).sum())
    p(f"    as-of weekdays: Tue {int((wd == 1).sum())}, holiday-shifted (Mon/Wed) {n_shifted}")

    crowd = (cot["lev_long"] - cot["lev_short"]).to_numpy(float) / cot["oi"].to_numpy(float)  # R4
    cot["crowd_raw"] = crowd
    cot["pct156"] = trailing_pct(crowd)
    cot["tercile"] = terciles(cot["pct156"].to_numpy())
    n_warmup = int((cot["tercile"] == 0).sum())
    p(f"    trailing {PCTL_WIN}-report percentile: warmup reports (no state): {n_warmup}; "
      f"states defined: {n_reports - n_warmup}")

    # diagnostics categories (R14) - same pipeline, NON-GATE
    for cat in ["dealer", "am"]:
        cot[f"{cat}_pct"] = trailing_pct(
            (cot[f"{cat}_long"] - cot[f"{cat}_short"]).to_numpy(float) / cot["oi"].to_numpy(float))
        cot[f"{cat}_terc"] = terciles(cot[f"{cat}_pct"].to_numpy())

    # ---- causal alignment (R7, R8) ----------------------------------------------
    cot["publication_date"] = cot["report_date"] + pd.to_timedelta(
        4 - cot["report_date"].dt.weekday, unit="D")
    assert (cot["publication_date"].dt.weekday == 4).all(), "publication not a Friday"
    pub_key = iso_key_of_dates(cot["publication_date"])
    cond_key = iso_key_of_dates(cot["publication_date"] + pd.Timedelta(days=7))

    rows = []
    excl = {"warmup": 0, "pub_week_missing": 0, "cond_week_beyond_grid": 0,
            "not_consecutive": 0, "splice_or_nan_ret": 0}
    for i in range(n_reports):
        rec = dict(report_date=cot["report_date"].iloc[i],
                   as_of_weekday=int(wd.iloc[i]),
                   publication_date=cot["publication_date"].iloc[i],
                   lev_long=cot["lev_long"].iloc[i], lev_short=cot["lev_short"].iloc[i],
                   oi=cot["oi"].iloc[i], crowd_raw=cot["crowd_raw"].iloc[i],
                   pct156=cot["pct156"].iloc[i], tercile=int(cot["tercile"].iloc[i]),
                   dealer_terc=int(cot["dealer_terc"].iloc[i]),
                   am_terc=int(cot["am_terc"].iloc[i]),
                   cond_week_key="", cond_week_start="", cond_week_end="",
                   entry_close_label="", ret="", excluded_reason="")
        pk, ck = int(pub_key.iloc[i]), int(cond_key.iloc[i])
        if rec["tercile"] == 0:
            rec["excluded_reason"] = "warmup"
        elif pk not in wk_idx:
            rec["excluded_reason"] = "pub_week_missing"
        elif ck not in wk_idx:
            rec["excluded_reason"] = "cond_week_beyond_grid"
        elif wk_idx[ck] != wk_idx[pk] + 1:
            rec["excluded_reason"] = "not_consecutive"
        else:
            rp, rc = wk.iloc[wk_idx[pk]], wk.iloc[wk_idx[ck]]
            rec["cond_week_key"] = ck
            rec["cond_week_start"] = rc["week_start_label"].date().isoformat()
            rec["cond_week_end"] = rc["week_end_label"].date().isoformat()
            rec["entry_close_label"] = rp["week_end_label"].date().isoformat()
            if rp["substrate"] != rc["substrate"]:
                rec["excluded_reason"] = "splice_or_nan_ret"      # R9/R10c
            else:
                r = 100.0 * (float(rc["close"]) / float(rp["close"]) - 1.0)
                if np.isfinite(r):
                    rec["ret"] = r
                else:
                    rec["excluded_reason"] = "splice_or_nan_ret"
        if rec["excluded_reason"]:
            excl[rec["excluded_reason"]] += 1
        rows.append(rec)
    state = pd.DataFrame(rows)
    usable = state[state["excluded_reason"] == ""].copy()
    usable["ret"] = usable["ret"].astype(float)
    usable["cond_end_ts"] = pd.to_datetime(usable["cond_week_end"])
    assert usable["cond_week_key"].is_unique, "two reports condition the same week"
    m = len(usable)
    p(f"    exclusions (R10): {excl}")
    p(f"    usable conditioned weeks: {m} "
      f"[{usable['cond_week_end'].iloc[0]} .. {usable['cond_week_end'].iloc[-1]}]")
    tc = usable["tercile"].value_counts().sort_index()
    p(f"    tercile counts (usable): T1={int(tc.get(1, 0))} T2={int(tc.get(2, 0))} "
      f"T3={int(tc.get(3, 0))}")
    p(f"    mean next-week ret by tercile (%): "
      f"T1 {usable.loc[usable['tercile'] == 1, 'ret'].mean():+.4f}  "
      f"T2 {usable.loc[usable['tercile'] == 2, 'ret'].mean():+.4f}  "
      f"T3 {usable.loc[usable['tercile'] == 3, 'ret'].mean():+.4f}  "
      f"ALL {usable['ret'].mean():+.4f}")

    # ---- C1 ----------------------------------------------------------------------
    d, se, t, n3, n1 = contrast(usable, "tercile")
    p(f"\n--- 3. C1 tercile contrast: T3-T1 = {d:+.4f}%/wk  SE {se:.4f}  "
      f"Welch t {t:+.3f}  (n3={n3}, n1={n1})")

    # ---- C2 (sensitivity FIRST, then full circular null) -------------------------
    p("\n--- 4. C2 dependence-preserving null (research_sdk.null_guard, unit=week) ---")
    frame = usable[["tercile", "ret"]].reset_index(drop=True)
    frame["week_id"] = np.arange(len(frame))
    loader = lambda: frame.copy()                                     # noqa: E731
    decision_fn = lambda f: f["tercile"].to_numpy(int)                # noqa: E731

    def statistic_fn(dec: np.ndarray, base: pd.DataFrame) -> float:
        r = base["ret"].to_numpy(float)
        return abs(float(r[dec == 3].mean()) - float(r[dec == 1].mean()))

    sens = null_guard.verify_null_sensitivity(loader, decision_fn, statistic_fn,
                                              shifts=SENS_SHIFTS, unit="week_id")
    p(f"    sensitivity: real |T3-T1| {sens['real_stat']:.4f}  spread {sens['spread']:.4f} "
      f"across shifts {SENS_SHIFTS} -> null HAS teeth")
    assert m - 1 >= NULL_MIN, f"only {m-1} possible shifts < {NULL_MIN}"
    res = null_guard.run_circular_null(loader, decision_fn, statistic_fn,
                                       n_shifts=m - 1, unit="week_id", seed=NULL_SEED)
    nulls = np.asarray(res["null_stats"], dtype=float)
    q95 = float(np.quantile(nulls, 0.95, method="higher"))            # R12 conservative
    real_abs = float(res["real_stat"])
    assert abs(real_abs - abs(d)) < 1e-12, "engine/null parity violation"
    p(f"    {len(nulls)} circular shifts (ALL distinct shifts; >= {NULL_MIN} required)   "
      f"real |T3-T1| {real_abs:.4f}   null q95 {q95:.4f}   null med {np.median(nulls):.4f}   "
      f"percentile {100*res['percentile']:.1f}%   p_ge {res['p_ge']:.4f}")

    # ---- C3 ----------------------------------------------------------------------
    h1 = usable[usable["cond_end_ts"] <= HALF_SPLIT]
    h2 = usable[usable["cond_end_ts"] > HALF_SPLIT]
    d1 = contrast(h1, "tercile")
    d2 = contrast(h2, "tercile")
    p(f"\n--- 5. C3 halves (split on conditioned-week end, R13):")
    p(f"    half1 (<=2016-12-31): T3-T1 {d1[0]:+.4f}%  t {d1[2]:+.3f}  "
      f"(n3={d1[3]}, n1={d1[4]}, weeks={len(h1)})")
    p(f"    half2 (>=2017-01-01): T3-T1 {d2[0]:+.4f}%  t {d2[2]:+.3f}  "
      f"(n3={d2[3]}, n1={d2[4]}, weeks={len(h2)})")

    # ---- GATE TABLE (printed by program) -----------------------------------------
    c1a, c1b = d < 0, t <= -2.0
    c1 = c1a and c1b
    c2 = real_abs > q95
    c3a, c3b = d1[0] < 0, d2[0] < 0
    c3 = c3a and c3b
    allpass = c1 and c2 and c3
    p("")
    p("=" * 100)
    p("PREREGISTERED GATES (spec.yaml, frozen before results existed)")
    p("=" * 100)
    p(f"    {'GATE':<30} {'SPEC':>22} {'OBSERVED':>26}   PASS-FAIL")
    p("    " + "-" * 92)
    for nm, spc, obs, ok in [
        ("C1a contrarian sign T3-T1", "< 0", f"{d:+.4f}%/wk", c1a),
        ("C1b weekly clustered t", "<= -2.0", f"{t:+.3f}", c1b),
        ("C2  real |T3-T1| vs null q95", f"> {q95:.4f}", f"{real_abs:.4f}", c2),
        ("C3a half1 06-16 T3-T1", "< 0", f"{d1[0]:+.4f}%", c3a),
        ("C3b half2 17-26/07 T3-T1", "< 0", f"{d2[0]:+.4f}%", c3b),
    ]:
        p(f"    {nm:<30} {spc:>22} {obs:>26}   {'PASS' if ok else '*** FAIL ***'}")
    p("")
    p(f"    C1 {'PASS' if c1 else 'FAIL'}   C2 {'PASS' if c2 else 'FAIL'}   "
      f"C3 {'PASS' if c3 else 'FAIL'}")
    p("=" * 100)
    verdict = "PASS" if allpass else "NULL"
    p(f"VERDICT: {verdict} - " + (
        "all C1+C2+C3 pass." if allpass else
        "gate failure -> NULL, family closed at this formulation "
        "(ballast warning pre-applied: uncorrelated + unprofitable = ballast)."))
    p("=" * 100)

    # ---- diagnostics.txt ---------------------------------------------------------
    pd_("GENESIS_H7_COT_20260828 diagnostics (trial G00014) - printed by program")
    pd_("=" * 100)
    pd_("\n--- causal_availability_binding verification: example alignment rows ---")
    pd_("(report as-of -> publication Friday 15:30 ET -> conditioned NQ week; entry = "
        "publication-week last session close; NO earlier alignment exists in this run)")
    ex_idx = []
    if m:
        ex_idx.append(usable.index[0])
        shifted = usable[usable["as_of_weekday"] != 1]
        if len(shifted):
            ex_idx.append(shifted.index[0])
        ex_idx.append(usable.index[-1])
    for j in ex_idx:
        r_ = usable.loc[j]
        wd_name = ["Mon", "Tue", "Wed", "Thu", "Fri"][int(r_["as_of_weekday"])]
        cs = pd.Timestamp(r_["cond_week_start"])
        pd_(f"    report(as-of) {r_['report_date'].date()} ({wd_name}) -> published "
            f"{r_['publication_date'].date()} (Fri) 15:30 ET -> conditions ISO week "
            f"{r_['cond_week_key']}: start session {r_['cond_week_start']} "
            f"({['Mon','Tue','Wed','Thu','Fri'][cs.weekday()]}; opens "
            f"{(cs - pd.Timedelta(days=1)).date()} 18:00 ET) .. end session "
            f"{r_['cond_week_end']}; entry close = {r_['entry_close_label']} close; "
            f"ret {float(r_['ret']):+.4f}%  tercile T{int(r_['tercile'])}")
    pd_(f"\n    holiday-shifted as-of reports in window: {n_shifted} "
        f"(publication rule identical per R7)")

    pd_("\n--- NON-GATE diagnostic contrasts (R14): same pipeline, other TFF categories ---")
    for cat, label in [("dealer_terc", "Dealer net/OI"), ("am_terc", "Asset Manager net/OI")]:
        u = usable[usable[cat] > 0]
        dd = contrast(u, cat)
        cc = u[cat].value_counts().sort_index()
        pd_(f"    {label:<22} T3-T1 {dd[0]:+.4f}%/wk  Welch t {dd[2]:+.3f}  "
            f"(T1={int(cc.get(1, 0))}, T2={int(cc.get(2, 0))}, T3={int(cc.get(3, 0))})")
    pd_("    (Leveraged Funds gate contrast, for scale: "
        f"T3-T1 {d:+.4f}%/wk  t {t:+.3f})")

    pd_("\n--- NON-GATE robustness: publication-delay caveat (R7) ---")
    u_tue = usable[usable["as_of_weekday"] == 1]
    dt_ = contrast(u_tue, "tercile")
    pd_(f"    Tuesday-as-of only ({len(u_tue)} weeks): T3-T1 {dt_[0]:+.4f}%/wk  "
        f"t {dt_[2]:+.3f}  (excludes {m - len(u_tue)} holiday-shifted weeks)")

    pd_("\n--- accounting ---")
    pd_(f"    reports in window: {n_reports}; warmup {excl['warmup']}; "
        f"cond beyond grid {excl['cond_week_beyond_grid']}; "
        f"splice/nan {excl['splice_or_nan_ret']}; pub missing {excl['pub_week_missing']}; "
        f"not consecutive {excl['not_consecutive']}; usable {m}")
    pd_(f"    crowd_raw (usable): min {usable['crowd_raw'].min():+.4f} "
        f"med {usable['crowd_raw'].median():+.4f} max {usable['crowd_raw'].max():+.4f}")
    pd_(f"    weekly ret (usable): mean {usable['ret'].mean():+.4f}% "
        f"sd {usable['ret'].std(ddof=1):.4f}%")
    mde = 2.0 * se
    pd_(f"    POWER: MDE for |t|=2 at observed SE = {mde:.4f}%/wk on the T3-T1 contrast")

    # ---- state_series.csv (pre-seal asserted) ------------------------------------
    out_state = state.copy()
    sg.assert_presealed(out_state, "report_date", "state_series report_date")
    sg.assert_presealed(out_state, "publication_date", "state_series publication_date")
    nonempty = out_state[out_state["cond_week_end"] != ""].copy()
    nonempty["cond_week_end_ts"] = pd.to_datetime(nonempty["cond_week_end"])
    sg.assert_presealed(nonempty, "cond_week_end_ts", "state_series cond week ends")
    out_state["report_date"] = out_state["report_date"].dt.date
    out_state["publication_date"] = out_state["publication_date"].dt.date
    out_state.to_csv(os.path.join(OUT, "state_series.csv"), index=False)

    # ---- ledger + files ----------------------------------------------------------
    metrics = {
        "market_row_set": "e-mini NASDAQ-100 (CFTC code 209742, name-stripped union)",
        "reports_in_window": int(n_reports), "warmup": int(excl["warmup"]),
        "usable_weeks": int(m),
        "tercile_counts": {"T1": int(tc.get(1, 0)), "T2": int(tc.get(2, 0)),
                           "T3": int(tc.get(3, 0))},
        "t3_minus_t1_pct_per_wk": round(float(d), 4),
        "welch_t": round(float(t), 3),
        "null_shifts": int(len(nulls)), "null_q95_abs": round(q95, 4),
        "real_abs_diff": round(real_abs, 4),
        "null_percentile": round(float(res["percentile"]), 4),
        "null_p_ge": round(float(res["p_ge"]), 4),
        "half1_diff_pct": round(float(d1[0]), 4), "half1_t": round(float(d1[2]), 3),
        "half2_diff_pct": round(float(d2[0]), 4), "half2_t": round(float(d2[2]), 3),
        "diag_dealer_diff_pct": None, "diag_am_diff_pct": None,
        "mde_t2_pct_per_wk": round(float(mde), 4),
        "gates": {"C1": bool(c1), "C2": bool(c2), "C3": bool(c3)},
        "evidence_status": "DISCOVERY_CONSUMED",
    }
    for cat, key in [("dealer_terc", "diag_dealer_diff_pct"), ("am_terc", "diag_am_diff_pct")]:
        u = usable[usable[cat] > 0]
        metrics[key] = round(float(contrast(u, cat)[0]), 4)
    note = (f"COT TFF Leveraged-Funds net/OI crowding on e-mini NASDAQ-100 (209742), "
            f"trailing-156 percentile terciles, Friday-15:30 publication conditioning the "
            f"following ISO week (Fri-close->Fri-close); {m} usable weeks; T3-T1 "
            f"{d:+.4f}%/wk (t {t:+.3f}); null q95 {q95:.4f} on {len(nulls)} shifts; halves "
            f"{d1[0]:+.4f}/{d2[0]:+.4f}; gates C1 {'P' if c1 else 'F'} C2 "
            f"{'P' if c2 else 'F'} C3 {'P' if c3 else 'F'} -> {verdict}. Resolutions "
            f"R1-R14 recorded pre-computation; splice return dropped; seal asserted at "
            f"every load; LOW prior honored - "
            + ("family closed at this formulation." if verdict == "NULL"
               else "diagnostic conditioner only, no policy/P&L."))
    with open(os.path.join(OUT, "ledger_result_pending.json"), "w", encoding="utf-8") as f:
        json.dump({"trial_id": "G00014", "metrics": metrics, "result": verdict,
                   "note": note}, f, indent=2)
    with open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8") as f:
        f.write(TEE_GATE.getvalue())
    with open(os.path.join(OUT, "diagnostics.txt"), "w", encoding="utf-8") as f:
        f.write(TEE_DIAG.getvalue())
    print("outputs written: gate_table.txt, state_series.csv, diagnostics.txt, "
          f"ledger_result_pending.json  (result: {verdict})")
    return verdict


if __name__ == "__main__":
    main()
