"""GENESIS_H2_CALENDAR_20260828 — TEAM H2 driver (trial G00011).

Executes the frozen spec: one session-level frame of NQ close-to-close returns
2006 -> 2026-07-31; eleven preregistered day-type dummies (TOM, FOMC_CYCLE, FOMC_DAY,
CPI_DAY, NFP_DAY, OPEX_WEEK, DOW_Mon..Fri); statistic per type = mean(in) - mean(out)
with session-clustered (= Welch two-sample) t; G1 family-wise max-|t| circular-shift
null (500 shared draws); G2 era-stability; G3 DOW expected-NULL check.
All ambiguity resolutions frozen in out/spec_resolutions.txt BEFORE this ran.
No policy, no P&L, no parameter search. Prints the gate table to stdout AND
out/gate_table.txt.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import sys
from datetime import date, timedelta

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
OUT = os.path.join(RUN, "out")
ART = os.path.join(OUT, "calendar_artifacts")
ROOT = os.path.abspath(os.path.join(RUN, "..", ".."))
sys.path.insert(0, ROOT)

from research_sdk import seal_guard as sg  # noqa: E402

DEEP = os.path.join(ROOT, "research", "scalping_lab", "substrate", "minute", "NQ",
                    "nq1m_2005_202605.parquet")
MODERN = os.path.join(ROOT, "runs", "SM1M_SUBSTRATE", "out", "nq_1m_2022_2026.parquet")
C01 = os.path.join(ROOT, "research", "04_complementary_family",
                   "c01_announcement_calendar.csv")
HIST = os.path.join(ROOT, "research", "scalping_lab", "data",
                    "hist_calendar_2005_2021.csv")
FOMC_CSV = os.path.join(ART, "fomc_meetings_2006_2026.csv")

FRAME_LO = pd.Timestamp("2006-01-01")
FRAME_HI = pd.Timestamp("2026-07-31")
ERA_SPLIT = pd.Timestamp("2016-01-01")   # era1 <= 2015-12-31 < era2
N_NULL = 500
SEED = 0

TEE = io.StringIO()


def p(*a):
    line = " ".join(str(x) for x in a)
    print(line)
    TEE.write(line + "\n")


# ------------------------------------------------------------------ session closes
def session_label(ts: pd.Series) -> pd.Series:
    """END-stamped bar -> session label date (hour >= 18 rolls to next calendar day)."""
    lab = ts.dt.normalize()
    return lab.where(ts.dt.hour < 18, lab + pd.Timedelta(days=1))


def load_session_closes(path: str, lab_lo: pd.Timestamp, lab_hi: pd.Timestamp,
                        time_is_str: bool, name: str) -> pd.DataFrame:
    """Chunked (row-group) load -> one row per session: label, close (last bar <= label 17:59)."""
    pf = pq.ParquetFile(path)
    parts = []
    total_rows = 0
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
        chunk = chunk.loc[keep]
        lab = lab.loc[keep]
        if len(chunk) == 0:
            continue
        chunk = chunk.assign(label=lab.values)
        # last bar per session within this chunk
        idx = chunk.groupby("label")["ts"].idxmax()
        parts.append(chunk.loc[idx, ["label", "ts", "close"]])
    if not parts:
        raise RuntimeError(f"{name}: no rows in window")
    allp = pd.concat(parts, ignore_index=True)
    # sessions can straddle row-group boundaries: keep the max-ts row per session
    idx = allp.groupby("label")["ts"].idxmax()
    ses = allp.loc[idx].sort_values("label").reset_index(drop=True)
    # R17: Sat/Sun labels are artifacts
    wd = ses["label"].dt.weekday
    n_wk = int((wd >= 5).sum())
    if n_wk:
        p(f"{name}: dropped {n_wk} Saturday/Sunday-labeled artifact session(s)")
    ses = ses.loc[wd < 5].reset_index(drop=True)
    sg.assert_presealed(ses, "label", f"{name} session labels")
    sg.assert_presealed(ses, "ts", f"{name} session close timestamps")
    p(f"{name}: {total_rows} bars -> {len(ses)} sessions "
      f"[{ses['label'].iloc[0].date()} .. {ses['label'].iloc[-1].date()}]")
    return ses[["label", "close"]]


def welch_t(r: np.ndarray, mask_in: np.ndarray, valid: np.ndarray):
    """mean(in)-mean(out) Welch t on valid rows. Returns (diff, se, t, n_in, n_out)."""
    rin = r[valid & mask_in]
    rout = r[valid & ~mask_in]
    n1, n0 = len(rin), len(rout)
    if n1 < 2 or n0 < 2:
        return np.nan, np.nan, np.nan, n1, n0
    d = rin.mean() - rout.mean()
    se = np.sqrt(rin.var(ddof=1) / n1 + rout.var(ddof=1) / n0)
    return d, se, d / se, n1, n0


def main():
    p("=" * 78)
    p("GENESIS_H2_CALENDAR_20260828 driver — trial G00011 — run", pd.Timestamp.now())
    p("=" * 78)

    # ---------------- 1. session frame -------------------------------------------
    deep = load_session_closes(DEEP, FRAME_LO, pd.Timestamp("2021-12-31"), True, "deep")
    modern = load_session_closes(MODERN, pd.Timestamp("2022-01-01"), FRAME_HI, False, "modern")

    deep["ret"] = 100.0 * deep["close"].pct_change()
    modern["ret"] = 100.0 * modern["close"].pct_change()   # first row NaN = dropped splice return
    cal = pd.concat([deep, modern], ignore_index=True).sort_values("label").reset_index(drop=True)
    assert cal["label"].is_unique, "duplicate session labels across substrates"
    sg.assert_presealed(cal, "label", "final session frame")
    n_all = len(cal)
    p(f"session calendar: {n_all} sessions; returns available: {int(cal['ret'].notna().sum())} "
      f"(dropped: first deep session + splice return at 2022 boundary)")

    labels = cal["label"]
    lab_date = labels.dt.date.to_numpy()

    # ---------------- 2. dummies on the full session calendar --------------------
    dummies: dict[str, np.ndarray] = {}
    valid: dict[str, np.ndarray] = {}
    ones = np.ones(n_all, dtype=bool)

    # DOW
    wd = labels.dt.weekday.to_numpy()
    for i, nm in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri"]):
        dummies[f"DOW_{nm}"] = wd == i
        valid[f"DOW_{nm}"] = ones

    # TOM: last session of month + first 3 of next month
    ym = labels.dt.year * 100 + labels.dt.month
    pos_in_month = ym.groupby(ym).cumcount().to_numpy()
    is_last_of_month = np.zeros(n_all, dtype=bool)
    last_idx = pd.Series(np.arange(n_all)).groupby(ym.values).max().to_numpy()
    is_last_of_month[last_idx] = True
    tom = is_last_of_month | (pos_in_month <= 2)
    # frame edge: first 3 sessions of Jan-2006 qualify (pos_in_month covers it);
    # NOTE the very first month's "first 3" belong to the Dec-2005/Jan-2006 turn —
    # window membership needs only the month itself, so it is well-defined.
    dummies["TOM"] = tom
    valid["TOM"] = ones

    # OPEX_WEEK: Mon..third-Friday window per month
    opex = np.zeros(n_all, dtype=bool)
    months = pd.period_range(FRAME_LO, FRAME_HI, freq="M")
    for per in months:
        first = date(per.year, per.month, 1)
        # third Friday
        off = (4 - first.weekday()) % 7
        f3 = first + timedelta(days=off + 14)
        mon = f3 - timedelta(days=4)
        opex |= (lab_date >= mon) & (lab_date <= f3)
    dummies["OPEX_WEEK"] = opex
    valid["OPEX_WEEK"] = ones

    # CPI / NFP
    c01 = pd.read_csv(C01, parse_dates=["date"])
    sg.assert_presealed(c01, "date", "c01 announcement calendar")
    hist = pd.read_csv(HIST, parse_dates=["date"])
    sg.assert_presealed(hist, "date", "BLS 2005-2021 calendar")
    ann = pd.concat([c01, hist], ignore_index=True)
    lab_set = set(lab_date)
    for ev in ["CPI", "NFP"]:
        days = sorted({d.date() for d in ann.loc[ann["event"] == ev, "date"]})
        days_in_frame = [d for d in days if FRAME_LO.date() <= d <= FRAME_HI.date()]
        hit = [d for d in days_in_frame if d in lab_set]
        p(f"{ev}: {len(days)} calendar dates total, {len(days_in_frame)} in frame window, "
          f"{len(hit)} matched sessions, {len(days_in_frame) - len(hit)} dropped (no session)")
        dummies[f"{ev}_DAY"] = np.isin(lab_date, np.array(hit))
        valid[f"{ev}_DAY"] = ones

    # FOMC meetings
    fomc = pd.read_csv(FOMC_CSV, parse_dates=["start_date", "decision_date"])
    fomc, nd = sg.truncate_presealed(fomc, "decision_date", "FOMC meeting list (analysis)")
    sg.assert_presealed(fomc, "start_date", "FOMC meeting starts (analysis)")
    fomc = fomc.sort_values("start_date").reset_index(drop=True)
    p(f"FOMC meetings in analysis: {len(fomc)} (post-seal meetings dropped: {nd})")

    dec_days = [d.date() for d in fomc["decision_date"]]
    hit_dec = [d for d in dec_days if d in lab_set]
    p(f"FOMC_DAY: {len(dec_days)} decision days, {len(hit_dec)} matched sessions, "
      f"{len(dec_days) - len(hit_dec)} dropped (no session)")
    dummies["FOMC_DAY"] = np.isin(lab_date, np.array(hit_dec))
    valid["FOMC_DAY"] = ones

    # FOMC_CYCLE (R07)
    anchor_idx = []
    mismatch = 0
    for sd in fomc["start_date"]:
        pos = int(np.searchsorted(lab_date, sd.date(), side="left"))
        if pos >= n_all:
            continue
        if lab_date[pos] != sd.date():
            mismatch += 1
        anchor_idx.append(pos)
    anchor_idx = sorted(set(anchor_idx))
    p(f"FOMC_CYCLE anchors: {len(anchor_idx)} (start date not itself a session: {mismatch})")
    t_cycle = np.full(n_all, np.nan)
    for j, a in enumerate(anchor_idx):
        end = anchor_idx[j + 1] if j + 1 < len(anchor_idx) else n_all
        idx = np.arange(a, end)
        t_cycle[idx] = idx - a
    for a in anchor_idx:           # day -1 (upcoming-meeting assignment wins)
        if a - 1 >= 0:
            t_cycle[a - 1] = -1
    even_days = set()
    for w in (0, 2, 4, 6):
        even_days.update(range(5 * w - 1, 5 * w + 4))
    cyc_valid = ~np.isnan(t_cycle)
    dummies["FOMC_CYCLE"] = np.isin(t_cycle, list(even_days)) & cyc_valid
    valid["FOMC_CYCLE"] = cyc_valid
    p(f"FOMC_CYCLE: defined for {int(cyc_valid.sum())} sessions "
      f"(undefined head before first 2006 meeting: {int((~cyc_valid).sum())}); "
      f"in-window {int(dummies['FOMC_CYCLE'].sum())}")

    FAMILY = ["TOM", "FOMC_CYCLE", "FOMC_DAY", "CPI_DAY", "NFP_DAY", "OPEX_WEEK",
              "DOW_Mon", "DOW_Tue", "DOW_Wed", "DOW_Thu", "DOW_Fri"]
    EXPECT = {"TOM": "+", "FOMC_CYCLE": "+", "FOMC_DAY": "+", "CPI_DAY": "+",
              "NFP_DAY": "+", "OPEX_WEEK": "+",
              **{f"DOW_{d}": "NULL" for d in ["Mon", "Tue", "Wed", "Thu", "Fri"]}}

    # ---------------- 3. stat frame (sessions with returns) ----------------------
    has_ret = cal["ret"].notna().to_numpy()
    r = cal["ret"].to_numpy()[has_ret]
    N = len(r)
    masks = {k: v[has_ret] for k, v in dummies.items()}
    valids = {k: v[has_ret] for k, v in valid.items()}
    era1 = (labels < ERA_SPLIT).to_numpy()[has_ret]
    p(f"stat frame: N = {N} session returns; era1(2006-2015) = {int(era1.sum())}, "
      f"era2(2016-2026/07) = {int((~era1).sum())}")

    # per-type session-date lists -> calendar_artifacts (+ sha256)
    sha_lines = []
    frame_dates = lab_date[has_ret]
    for k in FAMILY:
        fn = os.path.join(ART, f"daytype_sessions_{k}.csv")
        dd = pd.DataFrame({"session_date": [d.isoformat() for d in frame_dates[masks[k]]]})
        dd.to_csv(fn, index=False)
        sha_lines.append(f"{hashlib.sha256(open(fn, 'rb').read()).hexdigest()}  daytype_sessions_{k}.csv")
    with open(os.path.join(ART, "daytype_sha256.txt"), "w") as f:
        f.write("\n".join(sha_lines) + "\n")

    # ---------------- 4. real statistics -----------------------------------------
    real = {}
    for k in FAMILY:
        d_, se_, t_, n1, n0 = welch_t(r, masks[k], valids[k])
        real[k] = dict(diff=d_, se=se_, t=t_, n_in=n1, n_out=n0)

    # ---------------- 5. family-wise circular-shift null --------------------------
    def all_t(rvec: np.ndarray) -> dict[str, float]:
        return {k: welch_t(rvec, masks[k], valids[k])[2] for k in FAMILY}

    # sensitivity check (null_guard doctrine): the max-|t| statistic must move
    probe = [1, 7, 250]
    probe_stats = [max(abs(v) for v in all_t(np.roll(r, k)).values()) for k in probe]
    real_max = max(abs(real[k]["t"]) for k in FAMILY)
    spread = max([real_max] + probe_stats) - min([real_max] + probe_stats)
    p(f"null sensitivity: real max|t| = {real_max:.3f}, probe stats = "
      f"{[round(x, 3) for x in probe_stats]}, spread = {spread:.4f}")
    if not np.isfinite(spread) or spread <= 1e-9:
        raise RuntimeError("null has no teeth — construction defect, stopping")

    rng = np.random.default_rng(SEED)
    shifts = rng.choice(np.arange(1, N), size=N_NULL, replace=False)
    rows = []
    for rep, k_ in enumerate(shifts):
        ts_ = all_t(np.roll(r, int(k_)))
        rows.append({"rep": rep, "shift": int(k_),
                     **{f"t_{k}": ts_[k] for k in FAMILY},
                     "max_abs_t": max(abs(v) for v in ts_.values())})
    null_df = pd.DataFrame(rows)
    null_df.to_csv(os.path.join(OUT, "family_null_distribution.csv"), index=False)
    maxabs = null_df["max_abs_t"].to_numpy()
    q95 = float(np.quantile(maxabs, 0.95, method="higher"))   # R18 conservative
    p(f"family null: {N_NULL} shared-shift replications; max-|t| q95 = {q95:.3f} "
      f"(min {maxabs.min():.3f}, med {np.median(maxabs):.3f}, max {maxabs.max():.3f})")

    # ---------------- 6. MDE per type (printed BEFORE verdict) --------------------
    p("")
    p("--- per-type MDE at the family-wise bar (printed BEFORE verdict; %/session) ---")
    p(f"{'type':<12}{'n_in':>6}{'n_out':>7}{'SE':>9}{'MDE=q95*SE':>12}")
    for k in FAMILY:
        p(f"{k:<12}{real[k]['n_in']:>6}{real[k]['n_out']:>7}{real[k]['se']:>9.4f}"
          f"{q95 * real[k]['se']:>12.4f}")

    # ---------------- 7. gates ----------------------------------------------------
    g1_pass = {k: abs(real[k]["t"]) > q95 for k in FAMILY}
    era_stats = {}
    for k in FAMILY:
        d1, _, _, _, _ = welch_t(r[era1], masks[k][era1], valids[k][era1])
        d2, _, _, _, _ = welch_t(r[~era1], masks[k][~era1], valids[k][~era1])
        era_stats[k] = (d1, d2)
    g2_pass = {k: g1_pass[k] and np.sign(era_stats[k][0]) == np.sign(era_stats[k][1])
               and era_stats[k][0] != 0 for k in FAMILY}

    survivors = [k for k in FAMILY if g1_pass[k] and g2_pass[k]]
    dow_g1 = [k for k in FAMILY if k.startswith("DOW_") and g1_pass[k]]

    p("")
    p("=" * 98)
    p("GATE TABLE (printed by program)")
    p("=" * 98)
    hdr = (f"{'GATE':<22}{'SPEC':<34}{'OBSERVED':<32}{'PASS-FAIL':<10}")
    p(hdr)
    p("-" * 98)
    for k in FAMILY:
        spec_txt = f"|t| > family q95 = {q95:.3f}"
        sign_flag = ""
        if EXPECT[k] == "+" and real[k]["diff"] < 0 and g1_pass[k]:
            sign_flag = " SIGN_CONTRA"
        obs = (f"diff={real[k]['diff']:+.4f}% t={real[k]['t']:+.3f}"
               f" (exp {EXPECT[k]})")
        p(f"{'G1_' + k:<22}{spec_txt:<34}{obs:<32}"
          f"{('PASS' if g1_pass[k] else 'FAIL') + sign_flag:<10}")
    for k in FAMILY:
        if not g1_pass[k]:
            continue
        d1, d2 = era_stats[k]
        p(f"{'G2_' + k:<22}{'same sign 06-15 & 16-26/07':<34}"
          f"{f'era1={d1:+.4f}% era2={d2:+.4f}%':<32}"
          f"{'PASS' if g2_pass[k] else 'FAIL':<10}")
    if not any(g1_pass.values()):
        p(f"{'G2_era_stability':<22}{'same sign in both eras':<34}"
          f"{'no G1 survivor to test':<32}{'N/A':<10}")
    g3_obs = f"{len(dow_g1)} DOW type(s) passed G1"
    g3_verdict = "PASS(expected NULL)" if not dow_g1 else "FLAG SURPRISE_REVIEW"
    p(f"{'G3_dow_verdict':<22}{'preregistered expectation NULL':<34}{g3_obs:<32}{g3_verdict:<10}")
    p("-" * 98)

    result = "PASS" if survivors else "NULL"
    p(f"SURVIVORS (G1+G2): {survivors if survivors else 'NONE'}")
    p(f"VERDICT: {result} — " + (
        "survivors are candidate CONDITIONERS only (no policy, no P&L)." if survivors
        else "family closed at this formulation; per-type MDEs above state what was detectable."))

    # ---------------- 8. artifacts ------------------------------------------------
    metrics = {
        "n_sessions": int(N),
        "family_q95_max_abs_t": round(q95, 4),
        "per_type": {k: {"n_in": int(real[k]["n_in"]),
                         "diff_pct": round(float(real[k]["diff"]), 5),
                         "t": round(float(real[k]["t"]), 3),
                         "mde_pct": round(float(q95 * real[k]["se"]), 5),
                         "g1": bool(g1_pass[k]), "g2": bool(g2_pass[k]),
                         "era1_diff_pct": round(float(era_stats[k][0]), 5),
                         "era2_diff_pct": round(float(era_stats[k][1]), 5)}
                     for k in FAMILY},
        "n_null": int(N_NULL),
        "survivors": survivors,
        "dow_g1_passes": dow_g1,
    }
    note = (
        f"All 11 preregistered day-types tested in ONE frame ({N} sessions 2006-01->2026-07, "
        f"deep+modern splice, splice return dropped); family-wise max-|t| bar {q95:.3f} from "
        f"{N_NULL} shared circular shifts; "
        + (f"survivors {survivors} (conditioners only). " if survivors
           else "zero survivors -> family closed at this formulation. ")
        + f"G3: DOW expected NULL, {g3_verdict}. FOMC dates fetched from federalreserve.gov "
          f"(sha256 recorded), c01 cross-check 37/37 exact. Evidence status: "
          f"DISCOVERY_CONSUMED (all data pre-seal, consumed history)."
    )
    with open(os.path.join(OUT, "ledger_result_pending.json"), "w") as f:
        json.dump({"trial_id": "G00011", "metrics": metrics, "result": result,
                   "note": note}, f, indent=2)

    with open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8") as f:
        f.write(TEE.getvalue())
    p("artifacts written: gate_table.txt, family_null_distribution.csv, "
      "ledger_result_pending.json, calendar_artifacts/")
    # re-write gate_table to capture the final line
    with open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8") as f:
        f.write(TEE.getvalue())
    return 0


if __name__ == "__main__":
    sys.exit(main())
