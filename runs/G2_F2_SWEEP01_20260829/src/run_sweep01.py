"""G2_F2_SWEEP01_20260829 — sweep-and-reclaim vs its mirror (sweep-and-continue) on NQ.

Preregistered spec: runs/G2_F2_SWEEP01_20260829/spec.yaml (FROZEN; card MC-08).
Ambiguity resolutions: out/spec_resolutions.txt (written before any affected number).
Ledger trial G00022. Gate table PRINTED BY THIS PROGRAM (GATE/SPEC/OBSERVED/PASS-FAIL);
MDEs printed before verdicts. No P&L, no costs — signed forward 60-min NQ point returns.

No parameter search occurs in this file: breach depth (5.0 pts), reclaim window (30 min),
horizon (60 min), scan window (09:30-15:30) and RTH (09:30-16:00) are spec constants.
"""
from __future__ import annotations

import json
import math
import os
import sys
from datetime import date

import numpy as np
import pandas as pd

REPO = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, REPO)

from research_sdk.seal_guard import assert_presealed, truncate_presealed
from research_sdk.session_boundary import assert_not_locked_forward
from research_sdk.null_guard import run_circular_null, verify_null_sensitivity

RUN_DIR = os.path.join(REPO, "runs", "G2_F2_SWEEP01_20260829")
OUT = os.path.join(RUN_DIR, "out")

MODERN_PARQUET = os.path.join(REPO, r"runs\SM1M_SUBSTRATE\out\nq_1m_2022_2026.parquet")
DEEP_PARQUET = os.path.join(REPO, r"research\scalping_lab\substrate\minute\NQ\nq1m_2005_202605.parquet")

# Frozen spec constants (R1, R3-R6)
BREACH_PTS = 5.0
RECLAIM_MIN = 30
HORIZON_MIN = 60
GRID_LO, GRID_HI = 9 * 60 + 31, 16 * 60          # RTH end-stamps 09:31..16:00 -> slots 571..960
NGRID = GRID_HI - GRID_LO + 1                    # 390 cols
SCAN_HI_COL = (15 * 60 + 30) - GRID_LO           # 359: last breach col (15:30 stamp)
LATE_TE_COL = (15 * 60) - GRID_LO                # 329: last allowed event col (15:00 stamp)

GATE_FIRST, GATE_LAST = date(2022, 1, 1), date(2026, 7, 31)
DEEP_FIRST, DEEP_LAST = date(2006, 1, 1), date(2021, 12, 31)

N_CONTROL_DRAWS = 300
N_NULL_SHIFTS = 300
SENS_SHIFTS = [1, 7, 61]


# ----------------------------------------------------------------------------------
def load_window(path: str, first: date, last: date, ctx: str, parse_str: bool) -> pd.DataFrame:
    """Load a substrate, pass it through seal_guard, cut to the session window, keep RTH."""
    df = pd.read_parquet(path, columns=["time", "open", "high", "low", "close"])
    if parse_str:
        df["time"] = pd.to_datetime(df["time"], format="%Y-%m-%d %H:%M:%S")
    df, n_dropped = truncate_presealed(df, "time", ctx)
    assert_presealed(df, "time", ctx + ":post-truncate")
    print(f"seal_guard PASS [{ctx}]: {n_dropped} sealed row(s) mechanically dropped, frame certified pre-seal")
    assert_not_locked_forward(last)
    t = df["time"]
    sess = t.dt.date.where(t.dt.hour < 18, (t + pd.Timedelta(days=1)).dt.date)
    df["session"] = sess
    df = df[(df["session"] >= first) & (df["session"] <= last)]
    mod = t.dt.hour * 60 + t.dt.minute
    df = df[(mod >= GRID_LO) & (mod <= GRID_HI)]  # RTH slice only (09:31..16:00 stamps)
    df = df[["time", "high", "low", "close", "session"]].sort_values("time", kind="stable").reset_index(drop=True)
    print(f"loaded [{ctx}]: {len(df):,} RTH bars, {df['session'].nunique():,} sessions "
          f"({df['session'].min()} .. {df['session'].max()})")
    return df


def build_grids(frame: pd.DataFrame) -> dict:
    """Per-session-block minute grids (block order = order of first appearance)."""
    codes, uniques = pd.factorize(frame["session"], sort=False)
    n = len(uniques)
    mod = (frame["time"].dt.hour * 60 + frame["time"].dt.minute).to_numpy()
    col = mod - GRID_LO
    gh = np.full((n, NGRID), np.nan)
    gl = np.full((n, NGRID), np.nan)
    gc = np.full((n, NGRID), np.nan)
    gh[codes, col] = frame["high"].to_numpy()
    gl[codes, col] = frame["low"].to_numpy()
    gc[codes, col] = frame["close"].to_numpy()
    real = ~np.isnan(gc)
    first_real = np.argmax(real, axis=1)
    last_real = NGRID - 1 - np.argmax(real[:, ::-1], axis=1)
    fc = pd.DataFrame(gc).ffill(axis=1).bfill(axis=1).to_numpy()
    return dict(uniques=uniques, gh=gh, gl=gl, gc=gc, fc=fc, real=real,
                first_real=first_real, last_real=last_real,
                sess_high=np.nanmax(gh, axis=1), sess_low=np.nanmin(gl, axis=1))


# ----------------------------------------------------------------------------------
def sweep_decisions(frame: pd.DataFrame) -> pd.DataFrame:
    """The FROZEN event machinery, computed ONLY from `frame` (black box for the null).

    Levels for block j = block j-1's RTH extremes (R2); on a circularly shifted frame this
    is exactly 'the LEVEL series shifted across sessions against real paths' (R10).
    Returns one row per surviving event:
      session, level_kind, level, cb_col, breach_extreme, family, sign, te_col.
    """
    g = build_grids(frame)
    n = len(g["uniques"])
    L = np.full(n, np.nan)  # prior RTH low
    H = np.full(n, np.nan)  # prior RTH high
    L[1:] = g["sess_low"][:-1]
    H[1:] = g["sess_high"][:-1]

    scan_l = g["gl"][:, :SCAN_HI_COL + 1]
    scan_h = g["gh"][:, :SCAN_HI_COL + 1]
    m_low = scan_l <= (L - BREACH_PTS)[:, None]   # NaN compares -> False
    m_high = scan_h >= (H + BREACH_PTS)[:, None]

    rows = []
    for kind, mask, lvl, sgn_reclaim in (("prior_rth_low", m_low, L, +1),
                                         ("prior_rth_high", m_high, H, -1)):
        has = mask.any(axis=1)
        cb = np.argmax(mask, axis=1)
        for j in np.flatnonzero(has):
            cbj = int(cb[j])
            level = float(lvl[j])
            w0, w1 = cbj, cbj + RECLAIM_MIN                       # window cols [tb, tb+30]
            closes = g["gc"][j, w0:w1 + 1]                        # raw closes: reclaim needs a REAL bar
            if kind == "prior_rth_low":
                cross = closes > level                            # strict (R4)
                extreme = float(g["gl"][j, cbj])
            else:
                cross = closes < level
                extreme = float(g["gh"][j, cbj])
            cross = cross & g["real"][j, w0:w1 + 1]
            if cross.any():
                te = w0 + int(np.argmax(cross))
                family, sign = "primary", sgn_reclaim
            else:
                te = w1
                family, sign = "mirror", -sgn_reclaim
            if te > LATE_TE_COL or g["last_real"][j] < te + HORIZON_MIN:
                continue                                          # late event dropped (R6)
            rows.append((g["uniques"][j], kind, level, cbj, extreme, family, sign, te))
    dec = pd.DataFrame(rows, columns=["session", "level_kind", "level", "cb_col",
                                      "breach_extreme", "family", "sign", "te_col"])
    return dec


def scored_events(dec: pd.DataFrame, g: dict) -> pd.DataFrame:
    """Attach responses measured on the grids `g` (base grids for the real run)."""
    rowmap = {u: i for i, u in enumerate(g["uniques"])}
    r = dec["session"].map(rowmap).to_numpy(dtype=np.int64)
    te = dec["te_col"].to_numpy(dtype=np.int64)
    ec = g["fc"][r, te]
    fw = g["fc"][r, te + HORIZON_MIN]
    out = dec.copy()
    out["event_close"] = ec
    out["fwd60_close"] = fw
    out["fwd_ret_pts"] = fw - ec
    out["signed_ret_pts"] = out["sign"].to_numpy() * out["fwd_ret_pts"].to_numpy()
    return out


def clustered_t(x: np.ndarray, clusters: np.ndarray) -> tuple[float, float, int, int]:
    """(t, se, N, G): Liang-Zeger cluster-robust t of the mean, G/(G-1) correction (R8)."""
    n = len(x)
    m = float(np.mean(x))
    resid = pd.Series(x - m)
    ug = resid.groupby(pd.Series(clusters)).sum().to_numpy()
    G = len(ug)
    var = (G / max(G - 1, 1)) * float(np.sum(ug ** 2)) / (n ** 2)
    se = math.sqrt(var)
    t = m / se if se > 0 else float("inf") * np.sign(m or 1)
    return t, se, n, G


# ----------------------------------------------------------------------------------
def control_p95(ev: pd.DataFrame, g: dict, seed: int) -> tuple[float, np.ndarray]:
    """S2: count-matched same-session random-minute control (R9). Returns (p95, draw_means)."""
    rowmap = {u: i for i, u in enumerate(g["uniques"])}
    r = ev["session"].map(rowmap).to_numpy(dtype=np.int64)
    sign = ev["sign"].to_numpy(dtype=np.float64)
    lo = np.maximum(0, g["first_real"][r])
    hi = np.minimum(LATE_TE_COL, g["last_real"][r] - HORIZON_MIN)
    assert (hi >= lo).all(), "control slot range empty for some event (should be impossible)"
    rng = np.random.default_rng(seed)
    draws = rng.integers(lo, hi + 1, size=(N_CONTROL_DRAWS, len(ev)))     # per-event bounds
    fc = g["fc"]
    fwd = fc[r[None, :], draws + HORIZON_MIN] - fc[r[None, :], draws]
    means = (sign[None, :] * fwd).mean(axis=1)
    return float(np.percentile(means, 95)), means


def make_statistic(family: str, g: dict):
    """null_guard statistic_fn: score (shifted-frame) decisions against ORIGINAL grids."""
    rowmap = {u: i for i, u in enumerate(g["uniques"])}
    fc = g["fc"]

    def statistic_fn(dec: pd.DataFrame, base: pd.DataFrame) -> float:
        sel = dec[dec["family"] == family]
        if len(sel) == 0:
            return 0.0
        r = sel["session"].map(rowmap).to_numpy(dtype=np.int64)
        te = sel["te_col"].to_numpy(dtype=np.int64)
        fwd = fc[r, te + HORIZON_MIN] - fc[r, te]
        return float(np.mean(sel["sign"].to_numpy() * fwd))

    return statistic_fn


# ----------------------------------------------------------------------------------
def era_stats(ev: pd.DataFrame, family: str) -> dict:
    sel = ev[ev["family"] == family]
    if len(sel) == 0:
        return dict(n=0, mean=float("nan"), t=float("nan"), se=float("nan"), G=0,
                    n_low=0, n_high=0)
    t, se, n, G = clustered_t(sel["signed_ret_pts"].to_numpy(),
                              sel["session"].astype(str).to_numpy())
    return dict(n=n, mean=float(sel["signed_ret_pts"].mean()), t=t, se=se, G=G,
                n_low=int((sel["level_kind"] == "prior_rth_low").sum()),
                n_high=int((sel["level_kind"] == "prior_rth_high").sum()))


def event_csv_rows(ev: pd.DataFrame, era: str) -> pd.DataFrame:
    out = pd.DataFrame({
        "era": era,
        "session_id": ev["session"].astype(str),
        "level_kind": ev["level_kind"],
        "level_px": ev["level"],
        "breach_ts": [f"{s} {(GRID_LO + c) // 60:02d}:{(GRID_LO + c) % 60:02d}:00"
                      for s, c in zip(ev["session"].astype(str), ev["cb_col"])],
        "breach_extreme_px": ev["breach_extreme"],
        "event_type": np.where(ev["family"] == "primary", "reclaim", "continuation"),
        "event_ts": [f"{s} {(GRID_LO + c) // 60:02d}:{(GRID_LO + c) % 60:02d}:00"
                     for s, c in zip(ev["session"].astype(str), ev["te_col"])],
        "event_close": ev["event_close"],
        "fwd60_close": ev["fwd60_close"],
        "fwd_ret_pts": ev["fwd_ret_pts"].round(4),
        "signed_ret_pts": ev["signed_ret_pts"].round(4),
    })
    return out


# ----------------------------------------------------------------------------------
def main() -> None:
    modern = load_window(MODERN_PARQUET, GATE_FIRST, GATE_LAST, "SWEEP01:modern-gate", parse_str=False)
    deep = load_window(DEEP_PARQUET, DEEP_FIRST, DEEP_LAST, "SWEEP01:deep-diagnostic", parse_str=True)

    # ---------------- real events (modern gate window) ----------------
    g_mod = build_grids(modern)
    dec_mod = sweep_decisions(modern)
    ev_mod = scored_events(dec_mod, g_mod)
    prim = era_stats(ev_mod, "primary")
    mirr = era_stats(ev_mod, "mirror")
    n_sess = len(g_mod["uniques"])

    # ---------------- S2 controls (seed 1, fresh rng per family — shared construction) ----
    ev_p = ev_mod[ev_mod["family"] == "primary"]
    ev_m = ev_mod[ev_mod["family"] == "mirror"]
    s2_p95_p, s2_means_p = control_p95(ev_p, g_mod, seed=1)
    s2_p95_m, s2_means_m = control_p95(ev_m, g_mod, seed=1)

    # ---------------- S3 null (sensitivity FIRST, then 300 shifts, seed 0) ----------------
    frame = modern.copy()
    loader = lambda: frame
    stat_p = make_statistic("primary", g_mod)
    stat_m = make_statistic("mirror", g_mod)
    sens_p = verify_null_sensitivity(loader, sweep_decisions, stat_p, shifts=SENS_SHIFTS, unit="session")
    print(f"null sensitivity VERIFIED (primary): real={sens_p['real_stat']:.5f} pts "
          f"spread={sens_p['spread']:.5f} across probe shifts {SENS_SHIFTS} — the null can move")
    sens_m = verify_null_sensitivity(loader, sweep_decisions, stat_m, shifts=SENS_SHIFTS, unit="session")
    print(f"null sensitivity VERIFIED (mirror):  real={sens_m['real_stat']:.5f} pts "
          f"spread={sens_m['spread']:.5f} across probe shifts {SENS_SHIFTS} — the null can move")
    null_p = run_circular_null(loader, sweep_decisions, stat_p, n_shifts=N_NULL_SHIFTS, unit="session", seed=0)
    null_m = run_circular_null(loader, sweep_decisions, stat_m, n_shifts=N_NULL_SHIFTS, unit="session", seed=0)
    assert null_p["shifts"] == null_m["shifts"], "family shift sets differ — shared-draw discipline broken"
    print(f"S3 shift set SHARED across family: {len(null_p['shifts'])} shifts, identical for primary and mirror")
    s3_p95_p = float(np.percentile(np.asarray(null_p["null_stats"]), 95))
    s3_p95_m = float(np.percentile(np.asarray(null_m["null_stats"]), 95))
    assert abs(null_p["real_stat"] - (prim["mean"] if prim["n"] else 0.0)) < 1e-9, "real stat mismatch (primary)"
    assert abs(null_m["real_stat"] - (mirr["mean"] if mirr["n"] else 0.0)) < 1e-9, "real stat mismatch (mirror)"

    # ---------------- deep era cut (non-gate, own substrate, no splice) ----------------
    g_deep = build_grids(deep)
    ev_deep = scored_events(sweep_decisions(deep), g_deep)
    prim_d = era_stats(ev_deep, "primary")
    mirr_d = era_stats(ev_deep, "mirror")

    # ---------------- gates ----------------
    s1_pass = (prim["n"] > 0) and (prim["mean"] > 0) and (prim["t"] >= 2.0)
    s2_pass = (prim["n"] > 0) and (prim["mean"] > s2_p95_p)
    s3_pass = (prim["n"] > 0) and (prim["mean"] > s3_p95_p)
    m1_pass = (mirr["n"] > 0) and (mirr["mean"] > 0) and (mirr["t"] >= 2.0)
    m2_pass = (mirr["n"] > 0) and (mirr["mean"] > s2_p95_m)
    m3_pass = (mirr["n"] > 0) and (mirr["mean"] > s3_p95_m)
    survived = s1_pass and s2_pass and s3_pass
    mirror_all = m1_pass and m2_pass and m3_pass
    momentum_tell = mirror_all and not survived
    verdict = "INFORMATION-SUPPORTED" if survived else "NULL"

    mde_p = 2.0 * prim["se"] if prim["n"] else float("nan")
    mde_m = 2.0 * mirr["se"] if mirr["n"] else float("nan")

    # per-year diagnostic (non-gate)
    yr = ev_mod.copy(); yr["year"] = yr["session"].astype(str).str[:4]
    per_year = yr.groupby(["year", "family"])["signed_ret_pts"].agg(["size", "mean"]).round(3).unstack("family")

    # ---------------- gate table (printed by program) ----------------
    L = []
    A = L.append
    A("G2_F2_SWEEP01_20260829 — GATE TABLE (printed by program; ledger trial G00022)")
    A("primary: prior-RTH-extreme sweep (>=5.0 pts, first per level per session) reclaimed within 30 min;")
    A("target = signed forward 60-min NQ close-to-close return in points (no P&L, no costs).")
    A(f"gate window sessions {GATE_FIRST} .. {GATE_LAST} | sessions with RTH bars {n_sess}")
    A("evidence status: DISCOVERY_CONSUMED (gate window includes the burned 2026-05-31..07-31 span; no sealed reads)")
    A("")
    obs_s1a = "mean {:+.4f} pts (N={}, low {} / high {})".format(prim["mean"], prim["n"], prim["n_low"], prim["n_high"])
    obs_s1b = "t = {:.3f} (G={} session clusters, SE {:.4f})".format(prim["t"], prim["G"], prim["se"])
    obs_s2 = "mean {:+.4f} vs ctrl p95 {:+.4f} ({} draws)".format(prim["mean"], s2_p95_p, N_CONTROL_DRAWS)
    obs_s3 = "mean {:+.4f} vs null p95 {:+.4f} ({} shifts, pct {:.1f}%, p_ge {:.4f})".format(
        prim["mean"], s3_p95_p, N_NULL_SHIFTS, null_p["percentile"] * 100, null_p["p_ge"])
    obs_m1 = "mean {:+.4f} pts (N={}, low {} / high {}), t = {:.3f} (G={})".format(
        mirr["mean"], mirr["n"], mirr["n_low"], mirr["n_high"], mirr["t"], mirr["G"])
    obs_m2 = "mean {:+.4f} vs ctrl p95 {:+.4f} ({} draws)".format(mirr["mean"], s2_p95_m, N_CONTROL_DRAWS)
    obs_m3 = "mean {:+.4f} vs null p95 {:+.4f} ({} shifts, pct {:.1f}%, p_ge {:.4f})".format(
        mirr["mean"], s3_p95_m, N_NULL_SHIFTS, null_m["percentile"] * 100, null_m["p_ge"])
    A(f"{'GATE':<6}{'SPEC':<62}{'OBSERVED':<70}{'PASS-FAIL'}")
    A(f"{'S1a':<6}{'reclaim-event signed mean > 0 pts':<62}{obs_s1a:<70}"
      f"{'PASS' if prim['n'] and prim['mean'] > 0 else 'FAIL'}")
    A(f"{'S1b':<6}{'session-clustered t >= 2.0':<62}{obs_s1b:<70}"
      f"{'PASS' if prim['n'] and prim['t'] >= 2.0 else 'FAIL'}")
    A(f"{'S2':<6}{'mean > p95 of count-matched same-session random-minute ctrl':<62}{obs_s2:<70}"
      f"{'PASS' if s2_pass else 'FAIL'}")
    A(f"{'S3':<6}{'level-series circular-shift null; real above p95':<62}{obs_s3:<70}"
      f"{'PASS' if s3_pass else 'FAIL'}")
    A("")
    A("MIRROR READOUT (continuation = momentum; NON-GATE by spec, same three statistics):")
    A(f"{'M1':<6}{'continuation signed mean > 0 pts and clustered t >= 2.0':<62}{obs_m1:<70}"
      f"{'CLEAR' if m1_pass else 'not clear'}")
    A(f"{'M2':<6}{'mean > p95 of count-matched same-session random-minute ctrl':<62}{obs_m2:<70}"
      f"{'CLEAR' if m2_pass else 'not clear'}")
    A(f"{'M3':<6}{'level-series circular-shift null; real above p95':<62}{obs_m3:<70}"
      f"{'CLEAR' if m3_pass else 'not clear'}")
    A("")
    A("null sensitivity: VERIFIED FIRST — primary spread {:.5f} pts, mirror spread {:.5f} pts over probe "
      "shifts {}; S3 shift set identical across the family (shared draw).".format(
          sens_p["spread"], sens_m["spread"], SENS_SHIFTS))
    A(f"deep era cut 2006-2021 (NON-GATE, own substrate, no splice): "
      f"primary mean {prim_d['mean']:+.4f} pts (N={prim_d['n']}, t={prim_d['t']:.2f})"
      + (" [SIGN FLIP vs modern]" if prim["n"] and prim_d["n"] and np.sign(prim_d["mean"]) != np.sign(prim["mean"]) else "")
      + f"; mirror mean {mirr_d['mean']:+.4f} pts (N={mirr_d['n']}, t={mirr_d['t']:.2f})"
      + (" [SIGN FLIP vs modern]" if mirr["n"] and mirr_d["n"] and np.sign(mirr_d["mean"]) != np.sign(mirr["mean"]) else ""))
    A("")
    A("per-year (modern, signed mean pts / N — diagnostic, non-gate):")
    A(per_year.to_string())
    A("")
    A(f"MDE (printed before verdicts): signed mean required for t=2.0 at observed clustered SE/N — "
      f"primary {mde_p:.4f} pts/event (observed {prim['mean']:+.4f}); "
      f"mirror {mde_m:.4f} pts/event (observed {mirr['mean']:+.4f}). "
      f"Distributional bars: S2 p95 {s2_p95_p:+.4f} / M2 p95 {s2_p95_m:+.4f}; "
      f"S3 p95 {s3_p95_p:+.4f} / M3 p95 {s3_p95_m:+.4f} pts.")
    A(f"VERDICT (primary): {verdict}" + ("" if survived else " at formulation — S1+S2+S3 not jointly met"))
    if momentum_tell:
        A("MIRROR FINDING: MOMENTUM-TELL — the mirror (sweep-and-continue) clears all three bars while the "
          "primary fails; recorded as a genuine result, routed to the family tree, not promoted here.")
    else:
        A(f"MIRROR FINDING: mirror clears {int(m1_pass) + int(m2_pass) + int(m3_pass)}/3 bars "
          f"(M1 {'CLEAR' if m1_pass else 'no'}, M2 {'CLEAR' if m2_pass else 'no'}, M3 {'CLEAR' if m3_pass else 'no'}) — "
          "recorded; no MOMENTUM-TELL condition met." if not (mirror_all and survived) else
          "MIRROR FINDING: mirror clears all three bars AND the primary passed — both recorded.")
    table = "\n".join(L)
    print(table)
    with open(os.path.join(OUT, "gate_table.txt"), "wb") as f:
        f.write(table.encode("utf-8"))

    # ---------------- outputs ----------------
    ev_csv = pd.concat([event_csv_rows(ev_mod, "modern"), event_csv_rows(ev_deep, "deep")],
                       ignore_index=True)
    ev_csv.to_csv(os.path.join(OUT, "events.csv"), index=False)

    ledger = {
        "trial_id": "G00022",
        "metrics": {
            "window": "2022-01-01..2026-07-31 sessions (modern gate)",
            "n_sessions_rth": n_sess,
            "primary_reclaim": {"n": prim["n"], "n_low_sweep": prim["n_low"], "n_high_sweep": prim["n_high"],
                                "signed_mean_pts": round(prim["mean"], 4), "t_session_clustered": round(prim["t"], 4),
                                "clustered_se_pts": round(prim["se"], 4), "n_session_clusters": prim["G"],
                                "mde_pts_t2": round(mde_p, 4),
                                "s2_ctrl_p95_pts": round(s2_p95_p, 4), "s2_n_draws": N_CONTROL_DRAWS,
                                "s3_null_p95_pts": round(s3_p95_p, 4), "s3_n_shifts": N_NULL_SHIFTS,
                                "s3_percentile": round(float(null_p["percentile"]), 4),
                                "s3_p_ge": round(float(null_p["p_ge"]), 4)},
            "mirror_continuation": {"n": mirr["n"], "n_low_sweep": mirr["n_low"], "n_high_sweep": mirr["n_high"],
                                    "signed_mean_pts": round(mirr["mean"], 4), "t_session_clustered": round(mirr["t"], 4),
                                    "clustered_se_pts": round(mirr["se"], 4), "n_session_clusters": mirr["G"],
                                    "mde_pts_t2": round(mde_m, 4),
                                    "m2_ctrl_p95_pts": round(s2_p95_m, 4),
                                    "m3_null_p95_pts": round(s3_p95_m, 4),
                                    "m3_percentile": round(float(null_m["percentile"]), 4),
                                    "m3_p_ge": round(float(null_m["p_ge"]), 4)},
            "deep_2006_2021": {"primary_n": prim_d["n"], "primary_signed_mean_pts": round(prim_d["mean"], 4),
                               "primary_t": round(prim_d["t"], 4),
                               "mirror_n": mirr_d["n"], "mirror_signed_mean_pts": round(mirr_d["mean"], 4),
                               "mirror_t": round(mirr_d["t"], 4)},
            "gates": {"S1": bool(s1_pass), "S2": bool(s2_pass), "S3": bool(s3_pass)},
            "mirror_bars": {"M1": bool(m1_pass), "M2": bool(m2_pass), "M3": bool(m3_pass)},
            "momentum_tell": bool(momentum_tell),
            "evidence_status": "DISCOVERY_CONSUMED",
        },
        "result": verdict,
        "note": ("Sweep-and-reclaim vs mirror, card MC-08; no P&L; frozen 5.0pt/30min/60min. "
                 + ("MOMENTUM-TELL recorded: mirror clears all three bars while primary fails; "
                    "routed to family tree, not promoted. " if momentum_tell else "")
                 + "Resolutions in out/spec_resolutions.txt."),
    }
    with open(os.path.join(OUT, "ledger_result_pending.json"), "wb") as f:
        f.write(json.dumps(ledger, indent=2).encode("utf-8"))
    print("\noutputs written: gate_table.txt, events.csv, ledger_result_pending.json")


if __name__ == "__main__":
    main()
